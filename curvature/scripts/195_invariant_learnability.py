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
import json
import sys
import zlib
from importlib import import_module
from itertools import combinations_with_replacement
from multiprocessing import get_context
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np

from curvlib import RESULTS

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
        """r_train, r_test (variance relative to R's), for the direction fitted on Ztrain."""
        Ft = self.scaled(Ztrain)
        Rw = _stream_qr(_chunks(Ft - Ft.mean(0)))
        nt = len(Ft)
        del Ft
        _, S2, V2t = np.linalg.svd(Rw @ self.W, full_matrices=False)
        c = self.W @ V2t[-1]
        r_train = (S2[-1] ** 2 / nt) * self.NR
        v = np.concatenate([self.scaled(Zc) @ c for Zc in _chunks(Ztest)])
        r_test = float(np.var(v)) * self.NR
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
    v, r, g = sc["v"], sc["r_star"], sc["g_star"]
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

def accepted_mask(res, T):
    life = np.minimum(res["t_plunge"], T)
    return (life >= T / 4) & (res["hdrift"] <= m94.H_DRIFT_DROP)


def valid(res, g):
    Z = res["samples"][:, :, g].T
    return Z[np.isfinite(Z).all(1)]


def reference_cloud(res, acc, rng):
    pts = np.concatenate([valid(res, g) for g in np.where(acc)[0]])
    take = rng.choice(len(pts), size=min(R_POINTS, len(pts)), replace=False)
    return pts[np.sort(take)]


def build_refs(Rpts, geo):
    return {d: Reference(Rpts, d, geo) for d in DEGREES}


def score_batch(res, acc, refs, T, r0, stage):
    rows = []
    for g in range(res["samples"].shape[2]):
        row = {"r0": float(r0[g]), "stage": stage, "t_plunge": float(res["t_plunge"][g]),
               "hdrift": float(res["hdrift"][g]), "accepted": bool(acc[g])}
        if res.get("ftle") is not None:
            row["ftle"] = float(res["ftle"][g])
        if acc[g]:
            row["fate"] = "SURVIVED" if not np.isfinite(res["t_plunge"][g]) else "STICKY-then-PLUNGED"
            row["scores"] = orbit_scores(valid(res, g), refs, T)
        rows.append(row)
    return rows


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
    reg = m94.seed_region(st, job["E"], job["L"])
    out = {k: v for k, v in job.items() if k != "extra_r0"} | {"region_r": reg}
    if reg is None:
        out["status"] = "NO-REGION"
        return out
    T, twin = job["T"], job.get("twin", False)
    r_seeds = np.concatenate([np.linspace(reg[0], reg[1], m94.N_STAGE1), np.asarray(job.get("extra_r0", []))])
    z1, r1 = m94.seeds(mdl, r_seeds)
    res1 = m94.integrate(mdl, z1, T, DT, STRIDE, twin=twin)
    acc1 = accepted_mask(res1, T)
    if acc1.sum() < 5:
        out["status"] = "TOO-FEW-ACCEPTED"
        return out
    refs = build_refs(reference_cloud(res1, acc1, rng), geo=True)
    out["reference"] = {str(d): {"p": r.p, "pruned": r.pruned, "N_R": r.NR} for d, r in refs.items()}
    rows = score_batch(res1, acc1, refs, T, r1, "stage1")
    n1 = m94.N_STAGE1
    fate = np.isfinite(res1["t_plunge"][:n1])
    trans = [(r1[i], r1[i + 1]) for i in range(min(n1, len(r1)) - 1) if fate[i] != fate[i + 1]][:m94.N_TRANS]
    for a, b in trans:
        z2, r2 = m94.seeds(mdl, np.linspace(a, b, m94.N_STAGE2))
        if z2.shape[1]:
            res2 = m94.integrate(mdl, z2, T, DT, STRIDE, twin=twin)
            rows += score_batch(res2, accepted_mask(res2, T), refs, T, r2, "stage2")
    if job.get("keep_for_nulls"):
        keep = [g for g in np.where(acc1)[0] if not np.isfinite(res1["t_plunge"][g])][:40]
        out["_null_samples"] = [valid(res1, g) for g in keep]
        out["_refs"] = refs
    if job.get("f1"):
        out["f1"] = f1_level(mdl, res1, acc1, reg)
    if job.get("coverage"):
        for g, row in enumerate(rows[:res1["samples"].shape[2]]):
            if row["accepted"]:
                row["section_gap"] = m94b.section_coverage(valid(res1, g))[1]
    out.update({"status": "DONE", "transitions": [list(t) for t in trans], "rows": rows,
                "spin": spin})
    return out


def f1_level(mdl, res, acc, reg):
    """Report-only F1: the §193 engine across orbits (train/test alternate survivors), time subsampled every 20th."""
    surv = [g for g in np.where(acc)[0] if not np.isfinite(res["t_plunge"][g])]
    if len(surv) < 20:
        return {"status": "too few survivors"}
    S = res["samples"][:, ::20, :]
    tr, te = S[:, :, surv[0::2]], S[:, :, surv[1::2]]
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


def nulls(level_out, rng):
    samples, refs = level_out["_null_samples"], level_out["_refs"]
    pr, sp = [], []
    for Z in samples[:20]:
        pr.append(verdict(orbit_scores(phase_randomize(Z, rng), refs, T_PRIMARY)["primary"], None))
    for i in range(min(20, len(samples) - 10)):
        A, B = samples[i], samples[i + 10]
        n = min(len(A), len(B))
        sp.append(verdict(orbit_scores(np.concatenate([A[:n // 2], B[n // 2:n]]), refs, T_PRIMARY)["primary"], None))
    frac = lambda v: sum(x not in ("REGULAR", "EXACT-REGULAR") for x in v) / max(len(v), 1)
    return {"phase_random": pr, "phase_random_notregular": frac(pr), "splice": sp, "splice_notregular": frac(sp)}


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


def g0(args):
    sts, spin = m94.spacetimes("t1o3")
    st = sts["Kerr"]
    rng = np.random.default_rng(5)
    measured = []
    for sense in (-1, 1):
        ls = m94.l_sep(st, 0.97, sense)
        for eps in (-0.01, 0.005):
            L = sense * ls * (1 + eps)
            reg = m94.seed_region(st, 0.97, L)
            extra = resonant_seeds(st, 0.97, L, reg) if reg else []
            job = {"system": "Kerr", "tag": "t1o3", "E": 0.97, "L": L, "eps": eps, "T": T_PRIMARY,
                   "label": f"G0_Kerr_t1o3_E0.97_{'pro' if sense < 0 else 'retro'}_eps{eps:+}",
                   "extra_r0": extra, "keep_for_nulls": True}
            out = run_level(job)
            out["extra_r0"] = extra
            measured.append(out)
            print(job["label"], out["status"], "resonant seeds", len(extra), flush=True)
    summary = {"gate": "G0", "levels": []}
    allv, resv = [], []
    for i, out in enumerate(measured):
        rows = [r for r in out.get("rows", []) if r.get("fate") == "SURVIVED"]
        others = [r for j, o in enumerate(measured) if j != i for r in o.get("rows", []) if r.get("fate") == "SURVIVED"]
        noise = noise99(others)                            # leave-one-level-out: Kerr cannot pass trivially
        for r in rows:
            r["verdict"] = verdict(r["scores"]["primary"], noise)
            r["verdict_short"] = verdict(r["scores"]["short"], noise)
        ex = np.asarray(out["extra_r0"]) if out["extra_r0"] else np.array([np.inf])
        res_rows = [r for r in rows if r["stage"] == "stage1" and np.min(np.abs(ex - r["r0"])) < 1e-9]
        nl = nulls(out, rng)
        allv += [r["verdict"] for r in rows]
        resv += [r["verdict"] for r in res_rows]
        out.update({"noise99_loo": noise, "nulls": nl, "resonant_n": len(res_rows)})
        _save(out, out["label"])
        cnt = lambda rr: {k: [r["verdict"] for r in rr].count(k) for k in ("EXACT-REGULAR", "REGULAR", "CHAOTIC", "ABSTAIN")}
        summary["levels"].append({"label": out["label"], "noise99_loo": noise, "n_survivors": len(rows),
                                  "counts": cnt(rows), "resonant_counts": cnt(res_rows),
                                  "nulls": {k: v for k, v in nl.items() if k.endswith("notregular")}})
        print(summary["levels"][-1], flush=True)

    def ok(v):
        n = len(v)
        reg = sum(x in ("REGULAR", "EXACT-REGULAR") for x in v)
        return bool(n > 0 and reg >= 0.98 * n and v.count("CHAOTIC") == 0 and v.count("ABSTAIN") <= 0.02 * n)
    nulls_ok = all(lv["nulls"]["phase_random_notregular"] >= 0.95 and lv["nulls"]["splice_notregular"] >= 0.95
                   for lv in summary["levels"])
    summary["G0"] = {"survivors_ok": ok(allv), "resonant_ok": ok(resv), "resonant_n": len(resv), "nulls_ok": nulls_ok}
    summary["G0"]["pass"] = all(summary["G0"][k] for k in ("survivors_ok", "resonant_ok", "nulls_ok"))
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
        o = run_level({"system": "Kerr", "tag": "t1o3", "E": 0.97, "L": -ls * 1.005, "T": 12000.0,
                       "label": "smoke", "keep_for_nulls": True, "f1": False})
        rows = [r for r in o["rows"] if r.get("fate")]
        fl = noise99(rows)
        for r in rows[:8]:
            sc = r["scores"]["primary"]
            print({k: f"{x:.1e}" for k, x in sc["v"].items()}, "d*", sc["dstar"], f"r*={sc['r_star']:.1e} g*={sc['g_star']:.1e}",
                  verdict(sc, fl))
        T_PRIMARY = 12000.0
        print("nulls", {k: v for k, v in nulls(o, np.random.default_rng(0)).items() if k.endswith("notregular")})
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
