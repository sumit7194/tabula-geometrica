"""Step 195 — per-orbit invariant learnability (F2), an independent regular/chaotic classifier for TS delta=2.

Pre-registration: notes/invariant_learnability_prereg.md, committed before any run. Runs after The Bridge's V11
rerun, in the order G0 -> G1 -> G2, stopping at any failed gate.

F2, per orbit and per degree d in {2, 4, 6}:
  1. Fit the direction c in a feature library whose variance along the orbit's FIRST HALF is smallest relative to
     its variance over the level's reference cloud R (the §193 square-root engine, pruning 1e-12).
  2. Test the same c on the SECOND HALF.
  3. A regular orbit's invariant generalizes in time (g = r_test / r_train ~ 1) and improves with degree. A chaotic
     orbit's does neither.
Raw scores are saved. Verdicts come from the frozen rule (verdict()), applied after the matched Kerr floors are
known.

MODES
  --g0      Kerr p=4/5, E=0.97, both senses, eps in {-0.01, +0.005}, plus near-resonant seeds and both nulls.
  --g1      controls with our own long-window twin-FTLE truth (TS Dubeibe, Henon-Heiles, ZV near-boundary).
  --g2      TS + Kerr at both p, all levels (parallel over levels), plus the F1 report-only readout.
  --verdict re-apply the frozen rule to saved levels and print the gate and prediction table.
"""

import argparse
import gc
import json
import os
import sys
import zlib
from importlib import import_module
from itertools import combinations_with_replacement
from multiprocessing import get_context
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np

RESULTS = Path(__file__).resolve().parent.parent / "results"   # not curvlib: it imports torch, implicated in segfaults (§195, 2026-10-11)

m94 = import_module("194_orbit_dimension")
m94b = import_module("194b_diagnose_g0")
s193 = m94.s193

DT, STRIDE = 0.05, 10                    # samples every 0.5 tau
T_PRIMARY, T_SHORT, T_TRUTH = 3.0e4, 1.0e4, 1.0e5
DEGREES = (2, 4, 6)
N_OVER_P = 40                      # final train-half fit
N_INNER = 20                       # inner-validation fit on Q1 (amendment 1)
R_POINTS = 200_000
PRUNE = 1e-12
G_REG, G_CHA, D_REG, D_CHA, R_PIN = 10.0, 100.0, 10.0, 3.0, 1e-4
EXACT_X, NOISE_X, NOISE_ABS = 10.0, 100.0, 1e-22     # amendment 1
OUT = RESULTS / "195_levels"


# ---------------------------------------------------------------- features

def _exponents(d):
    exps = [(0, 0, 0, 0)]
    for k in range(1, d + 1):
        for combo in combinations_with_replacement(range(4), k):
            e = [0, 0, 0, 0]
            for i in combo:
                e[i] += 1
            exps.append(tuple(e))
    return exps


EXPS = {d: _exponents(d) for d in DEGREES}


def feats(Z, d, geo, mu, sd):
    """Monomials of u = (Z - mu)/sd up to degree d, times {1, 1/(1-y^2), 1/(x^2-1)} for geodesics; constant dropped."""
    u = (Z - mu) / sd
    pw = [np.ones((len(Z), 4))]
    for k in range(1, d + 1):
        pw.append(pw[-1] * u)
    mons = np.stack([pw[e[0]][:, 0] * pw[e[1]][:, 1] * pw[e[2]][:, 2] * pw[e[3]][:, 3] for e in EXPS[d]], 1)
    fam = [np.ones(len(Z))]
    if geo:
        fam += [1.0 / (1.0 - Z[:, 1] ** 2), 1.0 / (Z[:, 0] ** 2 - 1.0)]
    F = np.concatenate([mons * f[:, None] for f in fam], 1)
    return F[:, 1:]                                       # column 0 = constant x 1


def _stream_qr(Z_iter):
    Rm = None
    for Zc in Z_iter:
        Rm = np.linalg.qr(Zc if Rm is None else np.vstack([Rm, Zc]), mode="r")
    return Rm


def _chunks(Z, n=8000):
    for i in range(0, len(Z), n):
        yield Z[i:i + n]


class Reference:
    """The level's reference cloud R for one degree: column scaling, and the whitening W of R's total scatter."""

    def __init__(self, Rpts, d, geo):
        self.d, self.geo = d, geo
        self.mu, self.sd = Rpts.mean(0), Rpts.std(0) + 1e-300
        n, mean, M2 = 0, None, None                       # chunked Chan moments: R's features never held whole
        for Zc in _chunks(Rpts):
            F = feats(Zc, d, geo, self.mu, self.sd)
            nb, mb = len(F), F.mean(0)
            M2b = ((F - mb) ** 2).sum(0)
            if mean is None:
                n, mean, M2 = nb, mb, M2b
                continue
            delta = mb - mean
            tot = n + nb
            mean, M2, n = mean + delta * nb / tot, M2 + M2b + delta ** 2 * n * nb / tot, tot
        self.cmean, self.csd = mean, np.sqrt(M2 / n) + 1e-300
        self.p = len(mean)
        Rt = _stream_qr(((feats(Zc, d, geo, self.mu, self.sd) - self.cmean) / self.csd for Zc in _chunks(Rpts)))
        _, S, Vt = np.linalg.svd(Rt, full_matrices=False)
        keep = S > PRUNE * S[0]
        self.W = Vt[keep].T / S[keep]                     # ||Rt W v|| = ||v||
        self.NR = len(Rpts)
        self.pruned = int((~keep).sum())

    def scaled(self, Z):
        return feats(Z, self.d, self.geo, self.mu, self.sd) / self.csd

    def score(self, Ztrain, Ztest):
        """r_train, r_test (variance relative to R's), for the direction fitted on Ztrain. Streamed in 4000-row
        chunks so an orbit's feature matrix is never held whole (the first G0 launch died at a 9.9 GB tree)."""
        tot, n = 0.0, 0
        for Zc in _chunks(Ztrain, 4000):
            F = self.scaled(Zc)
            tot = tot + F.sum(0)
            n += len(F)
        m = tot / n
        Rw = _stream_qr(self.scaled(Zc) - m for Zc in _chunks(Ztrain, 4000))
        _, S2, V2t = np.linalg.svd(Rw @ self.W, full_matrices=False)
        c = self.W @ V2t[-1]
        r_train = (S2[-1] ** 2 / n) * self.NR
        v = np.concatenate([self.scaled(Zc) @ c for Zc in _chunks(Ztest, 4000)])
        # Amendment 2: "does the invariant KEEP ITS VALUE" -- test deviation about the TRAIN mean. The self-centred
        # variance (kept for report) let a GLOBAL invariant pass on the wrong orbit (G0 run 1, splice null).
        r_test = float(np.mean((v - float(m @ c)) ** 2)) * self.NR
        self.last_self = float(np.var(v)) * self.NR
        return float(r_train), r_test


def orbit_scores(Z, refs, T, dt_s=DT * STRIDE):
    """F2 scores for one orbit (amendment 1). Per window: the train half splits into Q1 | Q2.
    - Inner validation: fit on Q1, validate on Q2 -> v_d for every rung with |Q1| >= N_INNER * p.
    - d* = argmin v_d. Final fit on the whole train half at d*, tested on the untouched test half: r*, g*.
    - r_test is also kept for every rung (report only)."""
    out = {}
    for name, win in (("primary", T), ("short", T_SHORT)):
        n = min(len(Z), int(round(win / dt_s)))
        half, q = n // 2, n // 4
        v, rt = {}, {}
        for d, ref in refs.items():
            if q < N_INNER * ref.p:
                continue
            v[str(d)] = ref.score(Z[:q], Z[q:2 * q])[1]
            if half >= N_OVER_P * ref.p:
                rt[str(d)] = ref.score(Z[:half], Z[half:2 * half])
        if not v:
            out[name] = {}
            continue
        dstar = min(v, key=lambda k: v[k])
        rtr, rte = rt[dstar] if dstar in rt else refs[int(dstar)].score(Z[:half], Z[half:2 * half])
        out[name] = {"v": v, "dstar": dstar, "r_train": rtr, "r_star": rte, "g_star": rte / max(rtr, 1e-300),
                     "r_test_all": {k: x[1] for k, x in rt.items()}}
    return out


# ---------------------------------------------------------------- the frozen decision rule

def verdict(sc, noise):
    """Frozen rule (pre-reg + amendment 1). sc = orbit_scores(...)[window].
    noise = the numerical noise ceiling: the 99th percentile of r* over the integrable reference (Kerr, or
    Schwarzschild for ZV), where the invariant is exact in the basis, so r* is pure round-off. It comes from the
    matched reference level; for G0, from the OTHER G0 levels. None -> no reference (Henon-Heiles): NOISE_ABS."""
    if not sc:
        return "ABSTAIN"
    noise = NOISE_ABS if noise is None else noise
    v, r = sc["v"], sc["r_star"]
    g = r / (sc["r_train"] + noise)                      # amendment 2: scaled by train spread + integration floor
    if r <= EXACT_X * noise:
        return "EXACT-REGULAR"
    ds = sorted(v, key=int)
    lo, best = v[ds[0]], min(v.values())
    descending = len(ds) > 1 and best <= lo / D_REG
    flat = len(ds) > 1 and best >= lo / D_CHA
    if g <= G_REG and descending and r <= R_PIN:
        return "REGULAR"
    if r > NOISE_X * noise and (g >= G_CHA or (flat and r > R_PIN)):
        return "CHAOTIC"
    return "ABSTAIN"


def noise99(rows, window="primary"):
    vals = [r["scores"][window]["r_star"] for r in rows if r.get("scores") and r["scores"].get(window)]
    return float(np.percentile(vals, 99)) if vals else None


# ---------------------------------------------------------------- integration helpers

CHUNK = 40                         # orbits integrated per batch; samples spill to disk (memory fix, 2026-10-11)


def accepted_mask(res, T):
    life = np.minimum(res["t_plunge"], T)
    return (life >= T / 4) & (res["hdrift"] <= m94.H_DRIFT_DROP)


def _valid(S, g):
    Z = np.array(S[:, :, g]).T
    return Z[np.isfinite(Z).all(1)]


def valid(res, g):
    return _valid(res["samples"], g)


class Spill:
    """Integrate seeds in CHUNK-orbit batches; keep per-orbit fate arrays in memory, samples memory-mapped on disk."""

    def __init__(self, mdl, z, T, twin, tmpdir, tag):
        self.files, self.idx = [], []
        tp, hd, ft = [], [], []
        for k, i0 in enumerate(range(0, z.shape[1], CHUNK)):
            res = m94.integrate(mdl, z[:, i0:i0 + CHUNK], T, DT, STRIDE, twin=twin)
            f = tmpdir / f"{tag}_{k}.npy"
            np.save(f, res["samples"])
            self.files.append(f)
            self.idx += [(k, g) for g in range(res["samples"].shape[2])]
            tp.append(res["t_plunge"]); hd.append(res["hdrift"])
            ft.append(res["ftle"] if res.get("ftle") is not None else np.full(res["samples"].shape[2], np.nan))
            del res
        self.t_plunge, self.hdrift, self.ftle = np.concatenate(tp), np.concatenate(hd), np.concatenate(ft)
        self.acc = accepted_mask({"t_plunge": self.t_plunge, "hdrift": self.hdrift}, T)
        self._mm = {}

    def orbit(self, i):
        """No memory-mapping (2026-10-11): 2 of 4 runs of the mmap version died of heap corruption (macOS malloc
        trap inside numpy). A chunk is read fully, one chunk cached at a time, and every orbit returned is a copy."""
        k, g = self.idx[i]
        if k not in self._mm:
            self._mm = {k: np.load(self.files[k])}
        return _valid(self._mm[k], g)

    def n(self):
        return len(self.idx)

    def cleanup(self):
        self._mm = {}
        for f in self.files:
            f.unlink(missing_ok=True)


def reference_cloud(sp, rng):
    """Stratified per accepted orbit (each contributes ~R_POINTS / n_accepted points), so the full cloud never has to
    be concatenated in memory. Same distribution as a uniform subsample of all accepted points."""
    acc = np.where(sp.acc)[0]
    k = int(np.ceil(R_POINTS / max(len(acc), 1)))
    pts = []
    for i in acc:
        Z = sp.orbit(i)
        pts.append(Z[np.sort(rng.choice(len(Z), size=min(k, len(Z)), replace=False))])
    return np.concatenate(pts)


def build_refs(Rpts, geo):
    return {d: Reference(Rpts, d, geo) for d in DEGREES}


def score_spill(sp, refs, T, r0, stage, coverage=False):
    rows = []
    for i in range(sp.n()):
        row = {"r0": float(r0[i]), "stage": stage, "t_plunge": float(sp.t_plunge[i]),
               "hdrift": float(sp.hdrift[i]), "accepted": bool(sp.acc[i])}
        if np.isfinite(sp.ftle[i]):
            row["ftle"] = float(sp.ftle[i])
        if sp.acc[i]:
            Z = sp.orbit(i)
            row["fate"] = "SURVIVED" if not np.isfinite(sp.t_plunge[i]) else "STICKY-then-PLUNGED"
            row["scores"] = orbit_scores(Z, refs, T)
            if coverage:
                row["section_gap"] = m94b.section_coverage(Z)[1]
        rows.append(row)
    return rows


def _probe(tag):
    """Heap-corruption hunt (2026-10-11): with TABULA_GC_PROBE=1, a full GC at each phase boundary traverses every
    tracked object, so a corrupted one crashes HERE (faulthandler names the phase) instead of at interpreter exit."""
    if os.environ.get("TABULA_GC_PROBE"):
        print(f"[probe] {tag}", flush=True)
        gc.collect()


def run_level(job):
    """Measure F2 raw scores for one level (two-stage seeding). job: system, tag, E, L, label, T, (twin, extra_r0)."""
    rng = np.random.default_rng(zlib.crc32(job["label"].encode()))
    if job["system"] == "ZV2":
        st, spin = s193.Spacetime(*s193.zv2_components(), "ZV2"), None
    elif job["system"] == "SCHW":
        st, spin = s193.Spacetime(s193.kerr_components(0, 1), 1, "SCHW"), 0.0
    else:
        sts, spin = m94.spacetimes(job["tag"])
        st = sts[job["system"]]
    mdl = st.at(job["E"], job["L"])
    _probe("spacetimes+model")
    reg = m94.seed_region(st, job["E"], job["L"])
    out = {k: v for k, v in job.items() if k != "extra_r0"} | {"region_r": reg}
    if reg is None:
        out["status"] = "NO-REGION"
        return out
    tmp = OUT / "tmp"
    tmp.mkdir(parents=True, exist_ok=True)
    T, twin = job["T"], job.get("twin", False)
    r_seeds = np.concatenate([np.linspace(reg[0], reg[1], m94.N_STAGE1), np.asarray(job.get("extra_r0", []))])
    z1, r1 = m94.seeds(mdl, r_seeds)
    sp1 = Spill(mdl, z1, T, twin, tmp, job["label"] + "_s1")
    _probe("stage1 integrated")
    try:
        if sp1.acc.sum() < 5:
            out["status"] = "TOO-FEW-ACCEPTED"
            return out
        Rpts = reference_cloud(sp1, rng)
        np.save(OUT / f"R_{job['label']}.npy", Rpts)          # lets the confirmation step rebuild refs exactly
        refs = build_refs(Rpts, geo=job.get("geo", True))
        _probe("refs built")
        out["reference"] = {str(d): {"p": r.p, "pruned": r.pruned, "N_R": r.NR} for d, r in refs.items()}
        rows = score_spill(sp1, refs, T, r1, "stage1", coverage=job.get("coverage", False))
        _probe("stage1 scored")
        n1 = min(m94.N_STAGE1, len(r1))
        fate = np.isfinite(sp1.t_plunge[:n1])
        trans = [(r1[i], r1[i + 1]) for i in range(n1 - 1) if fate[i] != fate[i + 1]][:m94.N_TRANS]
        for j, (a, b) in enumerate(trans):
            z2, r2 = m94.seeds(mdl, np.linspace(a, b, m94.N_STAGE2))
            if z2.shape[1]:
                sp2 = Spill(mdl, z2, T, twin, tmp, job["label"] + f"_s2_{j}")
                rows += score_spill(sp2, refs, T, r2, "stage2", coverage=job.get("coverage", False))
                sp2.cleanup()
        _probe("stage2 done")
        if job.get("keep_for_nulls"):
            keep = [i for i in np.where(sp1.acc)[0] if not np.isfinite(sp1.t_plunge[i])][:40]
            out["nulls_raw"] = nulls([sp1.orbit(i) for i in keep], refs, rng)
        _probe("nulls scored")
        if job.get("f1"):
            out["f1"] = f1_level(mdl, sp1, reg)
        out.update({"status": "DONE", "transitions": [list(t) for t in trans], "rows": rows, "spin": spin})
        return out
    finally:
        sp1.cleanup()


def f1_level(mdl, sp, reg):
    """Report-only F1: the §193 engine across orbits (train/test alternate survivors), time subsampled every 20th."""
    surv = [i for i in np.where(sp.acc)[0] if not np.isfinite(sp.t_plunge[i])]
    if len(surv) < 20:
        return {"status": "too few survivors"}
    S = np.stack([sp.orbit(i)[::20] for i in surv], 2).transpose(1, 0, 2)          # (4, P, G)
    tr, te = S[:, :, 0::2], S[:, :, 1::2]
    xref = 0.5 * ((reg[0] - 1) + (reg[1] - 1)) / mdl.sig
    out = {}
    for c in (("CR", "even", 2, 4), ("CR", "even", 4, 4)):
        r = s193.engine(tr, te, c + (xref,), mdl)
        out["/".join(map(str, c))] = [float(v) for v in r["ratios"][:4]]
    return out


# ---------------------------------------------------------------- nulls (G0)

def phase_randomize(Z, rng):
    F = np.fft.rfft(Z - Z.mean(0), axis=0)
    th = rng.uniform(0, 2 * np.pi, len(F))
    th[0] = 0.0
    return np.fft.irfft(F * np.exp(1j * th)[:, None], n=len(Z), axis=0) + Z.mean(0)


def nulls(samples, refs, rng):
    """Raw null scores (verdicts are applied later with the level's noise ceiling)."""
    pr = [orbit_scores(phase_randomize(Z, rng), refs, T_PRIMARY)["primary"] for Z in samples[:20]]
    spl = []
    for i in range(min(20, len(samples) - 10)):
        A, B = samples[i], samples[i + 10]
        n = min(len(A), len(B))
        spl.append(orbit_scores(np.concatenate([A[:n // 2], B[n // 2:n]]), refs, T_PRIMARY)["primary"])
    return {"phase_random": pr, "splice": spl}


def null_verdicts(raw, noise):
    frac = lambda v: sum(x not in ("REGULAR", "EXACT-REGULAR") for x in v) / max(len(v), 1)
    pr = [verdict(sc, noise) for sc in raw["phase_random"]]
    spl = [verdict(sc, noise) for sc in raw["splice"]]
    return {"phase_random": pr, "phase_random_notregular": frac(pr), "splice": spl, "splice_notregular": frac(spl)}


# ---------------------------------------------------------------- modes

def _save(out, name):
    OUT.mkdir(exist_ok=True)
    clean = {k: v for k, v in out.items() if not k.startswith("_")}
    (OUT / f"{name}.json").write_text(json.dumps(clean, default=float))


def resonant_seeds(st, E, L, reg, n=50):
    """Locate the 6/5 and 5/4 bands by a short rotation-number scan; return n seeds inside them."""
    mdl = st.at(E, L)
    z, r0 = m94.seeds(mdl, np.linspace(reg[0], reg[1], 400))
    res = m94.integrate(mdl, z, 3000.0, DT, STRIDE, twin=False)
    good = []
    for g in range(z.shape[1]):
        Z = valid(res, g)
        if len(Z) < 4000 or np.isfinite(res["t_plunge"][g]):
            continue
        w = m94b.freqs(Z[:, 1], DT * STRIDE) / m94b.freqs(1 + mdl.sig * Z[:, 0], DT * STRIDE)
        if min(abs(w - 1.2), abs(w - 1.25)) < 0.002:
            good.append(r0[g])
    if not good:
        return []
    return list(np.quantile(good, np.linspace(0, 1, min(n, len(good)))))


def _model_for(job):
    if job["system"] == "ZV2":
        st = s193.Spacetime(*s193.zv2_components(), "ZV2")
    elif job["system"] == "SCHW":
        st = s193.Spacetime(s193.kerr_components(0, 1), 1, "SCHW")
    else:
        st = m94.spacetimes(job["tag"])[0][job["system"]]
    return st.at(job["E"], job["L"])


def dop853_fixed(mdl, z0, T, dt=DT, stride=STRIDE):
    """Independent integrator for confirmation: the 8th-order DOP853 Butcher tableau (Dormand-Prince), run with a
    FIXED step, vectorized like the RK4 path. It is a different scheme (order 8 against order 4), not RK4 checking
    itself. The adaptive scalar solve_ivp version at rtol 1e-13 took over 40 min per Kerr orbit, so it was unusable
    for every-candidate confirmation. Plunge and NaN handling match m94.integrate."""
    from scipy.integrate._ivp import dop853_coefficients as cf
    A, B, ns = cf.A[:cf.N_STAGES, :cf.N_STAGES], cf.B, cf.N_STAGES
    z = np.array(z0, dtype=float).reshape(4, -1)
    alive = np.ones(z.shape[1], bool)
    t_plunge = np.full(z.shape[1], np.inf)
    nstep = int(round(T / dt))
    rec = []
    for i in range(nstep):
        K = []
        for st_ in range(ns):
            zi = z + dt * sum(A[st_, j] * K[j] for j in range(st_)) if st_ else z
            K.append(mdl.rhs(zi))
        znew = z + dt * sum(B[j] * K[j] for j in range(ns))
        z = np.where(alive, znew, z)
        fin = np.isfinite(z).all(0)
        if mdl.sig is not None:
            fin &= (1 + mdl.sig * np.where(fin, z[0], 0.0)) >= m94.R_PLUNGE
        t_plunge[alive & ~fin] = (i + 1) * dt
        alive &= fin
        if i % stride == 0:
            snap = z.copy()
            snap[:, ~alive] = np.nan
            rec.append(snap)
    return {"samples": np.stack(rec, 1), "t_plunge": t_plunge}


def confirm_candidate(args):
    """Amendment 2: every CHAOTIC candidate, in every system, is re-integrated (a) by RK4 at dt/2 and (b) by an
    independent fixed-step DOP853 (8th order), then re-scored with the level's own reference cloud. Three-way:
      TRUNCATION  -> the dt/2 r* collapses by >= 16x (RK4 truncation; variance would be ~256x if pure);
      PRECISION   -> the dt/2 r* sits at <= 10 x noise (the precision floor);
      PHYSICAL    -> CHAOTIC stands only if BOTH re-integrations still read CHAOTIC and r* moved by < 4x.
    Anything else -> ABSTAIN (unresolved). ONE-SIDED: it can only remove CHAOTIC verdicts, never add them, so it
    biases every system, TS included, toward reading LESS chaotic."""
    job, row, noise, T = args
    mdl = _model_for(job)
    refs = build_refs(np.load(OUT / f"R_{job['label']}.npy"), geo=job.get("geo", True))
    z, _ = m94.seeds(mdl, np.array([row["r0"]]))
    out = {"label": job["label"], "r0": row["r0"], "r_star_dt": row["scores"]["primary"]["r_star"]}
    res = m94.integrate(mdl, z, T, DT / 2, 2 * STRIDE, twin=False)
    sc2 = orbit_scores(valid(res, 0), refs, T)["primary"]
    out.update({"r_star_dt2": sc2.get("r_star"), "verdict_dt2": verdict(sc2, noise)})
    resd = dop853_fixed(mdl, z, T)
    scd = orbit_scores(valid(resd, 0), refs, T)["primary"]
    out.update({"r_star_dop853": scd.get("r_star"), "verdict_dop853": verdict(scd, noise)})
    q = out["r_star_dt"] / max(out["r_star_dt2"] or 1e-300, 1e-300)
    out["collapse_q"] = q
    if out["verdict_dt2"] == "CHAOTIC" and out["verdict_dop853"] == "CHAOTIC" and q < 4:
        # The Bridge: a fixed step gives up error control, so convergence must be SHOWN. For chaos, pointwise
        # long-window convergence is impossible by construction (Lyapunov amplification), so the step regime is
        # checked pointwise over a SHORT horizon (h -> h/2 -> h/4 over 1000 tau; ratio ~2^8 expected for order 8,
        # or both diffs at round-off), and the STATISTIC over the full window (DOP853 at h/2: r* within 4x, same
        # verdict).
        hz = {f: dop853_fixed(mdl, z, 1000.0, DT / f, STRIDE * f)["samples"][:, :, 0] for f in (1, 2, 4)}
        d1, d2 = (float(np.nanmax(np.abs(hz[1] - hz[2]))), float(np.nanmax(np.abs(hz[2] - hz[4]))))
        res_h2 = dop853_fixed(mdl, z, T, DT / 2, 2 * STRIDE)
        sch2 = orbit_scores(valid(res_h2, 0), refs, T)["primary"]
        stat_ok = sch2.get("r_star") and verdict(sch2, noise) == "CHAOTIC" and \
            0.25 <= scd["r_star"] / sch2["r_star"] <= 4
        step_ok = (d2 > 0 and d1 / d2 >= 64) or max(d1, d2) <= 1e-11
        out.update({"conv_short_d1": d1, "conv_short_d2": d2, "conv_short_ratio": d1 / d2 if d2 else None,
                    "r_star_dop853_h2": sch2.get("r_star"), "step_converged": bool(step_ok),
                    "statistic_stable": bool(stat_ok)})
        if step_ok and stat_ok:
            out["class"], out["final"] = "PHYSICAL", "CHAOTIC"
        else:
            out["class"], out["final"] = "UNCONVERGED", "ABSTAIN"
    elif q >= 16:
        out["class"], out["final"] = "TRUNCATION", out["verdict_dt2"] if out["verdict_dt2"] != "CHAOTIC" else "ABSTAIN"
    elif (out["r_star_dt2"] or 0) <= EXACT_X * noise:
        out["class"], out["final"] = "PRECISION", "EXACT-REGULAR"
    else:
        out["class"], out["final"] = "UNRESOLVED", "ABSTAIN"
    return out


def confirm_all(cands, workers):
    if not cands:
        return []
    with get_context("spawn").Pool(min(workers, len(cands))) as pool:
        return pool.map(confirm_candidate, cands)


def _g0_measure(job):
    sts, _ = m94.spacetimes(job["tag"])
    st = sts["Kerr"]
    reg = m94.seed_region(st, job["E"], job["L"])
    job["extra_r0"] = resonant_seeds(st, job["E"], job["L"], reg) if reg else []
    out = run_level(job)
    out["extra_r0"] = job["extra_r0"]
    return out


def g0(args):
    sts, spin = m94.spacetimes("t1o3")
    st = sts["Kerr"]
    rng = np.random.default_rng(5)
    jobs = []
    for sense in (-1, 1):
        ls = m94.l_sep(st, 0.97, sense)
        for eps in (-0.01, 0.005):
            L = sense * ls * (1 + eps)
            jobs.append({"system": "Kerr", "tag": "t1o3", "E": 0.97, "L": L, "eps": eps, "T": T_PRIMARY,
                         "label": f"G0_Kerr_t1o3_E0.97_{'pro' if sense < 0 else 'retro'}_eps{eps:+}",
                         "keep_for_nulls": True, "set": "original"})
    # amendment 2, condition 4: HELD-OUT Kerr levels never used in any diagnosis (other spin, other energy, other eps)
    st2 = m94.spacetimes("t1o2")[0]["Kerr"]
    ls2 = m94.l_sep(st2, 0.95, -1)
    for eps in (-0.005, 0.02):
        jobs.append({"system": "Kerr", "tag": "t1o2", "E": 0.95, "L": -ls2 * (1 + eps), "eps": eps, "T": T_PRIMARY,
                     "label": f"G0H_Kerr_t1o2_E0.95_pro_eps{eps:+}", "keep_for_nulls": True, "set": "heldout"})
    with get_context("spawn").Pool(min(args.workers, len(jobs))) as pool:
        measured = pool.map(_g0_measure, jobs)
    for out in measured:
        print(out["label"], out["status"], "resonant seeds", len(out["extra_r0"]), flush=True)
    noise_of = {}
    cands = []
    for i, out in enumerate(measured):
        others = [r for j, o in enumerate(measured) if j != i for r in o.get("rows", []) if r.get("fate") == "SURVIVED"]
        noise_of[i] = noise99(others)                     # leave-one-level-out: Kerr cannot pass trivially
        for r in out.get("rows", []):
            if r.get("fate") == "SURVIVED":
                r["verdict_raw"] = verdict(r["scores"]["primary"], noise_of[i])
                r["verdict_short"] = verdict(r["scores"]["short"], noise_of[i])
                if r["verdict_raw"] == "CHAOTIC":
                    cands.append(({k: v for k, v in out.items() if k in ("system", "tag", "E", "L", "label")},
                                  r, noise_of[i], T_PRIMARY))
    print(f"{len(cands)} CHAOTIC candidates -> dt/2 + DOP853 confirmation", flush=True)
    confirmed = {(c["label"], c["r0"]): c for c in confirm_all(cands, args.workers)}
    summary = {"gate": "G0", "levels": [], "confirmations": list(confirmed.values())}
    by_set = {"original": [], "heldout": []}
    resv = []
    for i, out in enumerate(measured):
        noise = noise_of[i]
        rows = [r for r in out.get("rows", []) if r.get("fate") == "SURVIVED"]
        for r in rows:
            r["verdict"] = confirmed[(out["label"], r["r0"])]["final"] if r["verdict_raw"] == "CHAOTIC" else r["verdict_raw"]
        ex = np.asarray(out["extra_r0"]) if out["extra_r0"] else np.array([np.inf])
        res_rows = [r for r in rows if r["stage"] == "stage1" and np.min(np.abs(ex - r["r0"])) < 1e-9]
        nl = null_verdicts(out["nulls_raw"], noise)
        by_set[out["set"]] += [r["verdict"] for r in rows]
        resv += [r["verdict"] for r in res_rows]
        out.update({"noise99_loo": noise, "nulls": nl, "resonant_n": len(res_rows)})
        _save(out, out["label"])
        cnt = lambda rr, key="verdict": {k: [r[key] for r in rr].count(k) for k in
                                         ("EXACT-REGULAR", "REGULAR", "CHAOTIC", "ABSTAIN")}
        summary["levels"].append({"label": out["label"], "set": out["set"], "noise99_loo": noise,
                                  "n_survivors": len(rows), "counts": cnt(rows), "counts_raw": cnt(rows, "verdict_raw"),
                                  "resonant_counts": cnt(res_rows),
                                  "nulls": {k: v for k, v in nl.items() if k.endswith("notregular")}})
        print(summary["levels"][-1], flush=True)

    def ok(v):
        n = len(v)
        reg = sum(x in ("REGULAR", "EXACT-REGULAR") for x in v)
        return bool(n > 0 and reg >= 0.98 * n and v.count("CHAOTIC") == 0 and v.count("ABSTAIN") <= 0.02 * n)
    nulls_ok = all(lv["nulls"]["phase_random_notregular"] >= 0.95 and lv["nulls"]["splice_notregular"] >= 0.95
                   for lv in summary["levels"])
    summary["G0"] = {"original_ok": ok(by_set["original"]), "heldout_ok": ok(by_set["heldout"]),
                     "resonant_ok": ok(resv), "resonant_n": len(resv), "nulls_ok": nulls_ok,
                     "n_candidates": len(cands),
                     "candidate_classes": {k: sum(c["class"] == k for c in confirmed.values())
                                           for k in ("TRUNCATION", "PRECISION", "PHYSICAL", "UNRESOLVED")}}
    summary["G0"]["pass"] = all(summary["G0"][k] for k in ("original_ok", "heldout_ok", "resonant_ok", "nulls_ok"))
    (RESULTS / "195_G0.json").write_text(json.dumps(summary, indent=1, default=float))
    print("G0:", summary["G0"])


def _gate(name):
    f = RESULTS / f"195_{name}.json"
    return f.exists() and json.loads(f.read_text()).get(name, {}).get("pass", False)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    for m in ("g0", "g1", "g2", "verdict"):
        ap.add_argument(f"--{m}", action="store_true")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--smoke", action="store_true", help="code-path check only: tiny T, guard relaxed, nothing saved")
    a = ap.parse_args()
    if a.smoke:
        sts, _ = m94.spacetimes("t1o3")
        ls = m94.l_sep(sts["Kerr"], 0.97, -1)
        m94.N_STAGE1 = 12
        T_SHORT = 4000.0
        lab = os.environ.get("SMOKE_LABEL") or f"smoke_{os.getpid()}"   # unique unless pinned (deterministic repeats)
        o = run_level({"system": "Kerr", "tag": "t1o3", "E": 0.97, "L": -ls * 1.005, "T": 12000.0,
                       "label": lab, "keep_for_nulls": True, "f1": False})
        _probe("run_level returned")
        rows = [r for r in o["rows"] if r.get("fate")]
        fl = noise99(rows)
        for r in rows[:8]:
            sc = r["scores"]["primary"]
            print({k: f"{x:.1e}" for k, x in sc["v"].items()}, "d*", sc["dstar"], f"r*={sc['r_star']:.1e} g*={sc['g_star']:.1e}",
                  verdict(sc, fl))
        T_PRIMARY = 12000.0
        c = confirm_candidate(({"system": "Kerr", "tag": "t1o3", "E": 0.97, "L": -ls * 1.005, "label": lab},
                               rows[0], fl, 12000.0))
        _probe("confirm done")
        print("confirm path:", {k: (f"{v:.2e}" if isinstance(v, float) else v) for k, v in c.items()})
        print("nulls", {k: v for k, v in null_verdicts(o["nulls_raw"], fl).items() if k.endswith("notregular")})
        print("torch loaded:", "torch" in sys.modules)
        _probe("end of smoke")
        raise SystemExit(0)
    if a.g0:
        g0(a)
    elif a.g1:
        if not _gate("G0"):
            raise SystemExit("G0 has not passed: G1 refused (pre-registered order)")
        raise SystemExit("G1 driver is written after G0 passes; its design is frozen in the pre-registration")
    elif a.g2:
        if not (_gate("G0") and _gate("G1")):
            raise SystemExit("G0 and G1 must pass first: G2 refused (pre-registered order)")
        raise SystemExit("G2 driver is written after G1 passes; its design is frozen in the pre-registration")
