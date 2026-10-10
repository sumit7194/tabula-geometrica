"""Step 194 — orbit-manifold dimension as an independent regular/chaotic classifier for Tomimatsu-Sato delta=2.

Pre-registration: notes/orbit_dimension_prereg.md. PREPARED, NOT RUN: execution waits for The Bridge to report free
Mac cores, and the Kerr pilot (--pilot, gate G0) runs first.

An "AI Poincare"-style count (Liu & Tegmark, arXiv:2011.04698), done per orbit. Each orbit is a point cloud in the
reduced phase space (x, y, p_x, p_y) at fixed (E, L). If its closure is 2-D it lies on a torus: count 2, REGULAR. If
it is 3-D it fills part of the energy shell: count 1, CHAOTIC. This is NOT an integrability test, because KAM tori of
a non-integrable system read 2 as well. It is an independent-method replication of ansatz section 150 (thin sticky
chaotic layers at the survive/plunge boundary).

The dimension readout is curvature scaling of local PCA:
- On a 2-torus, the third local eigenvalue comes only from curvature, so lambda_3 ~ r^4 (slope s3 ~ 4).
- In a 3-D fill, lambda_3 ~ r^2 (s3 ~ 2).
- The fourth eigenvalue is an internal control. The energy shell is 3-D, so s4 ~ 4 for every orbit.
- Temporal neighbours are excluded (Theiler window); otherwise every orbit reads 1-D along its own track.

MODES
  --unit        synthetic torus vs 3-D fill: tests the estimator only, no physics, seconds.
  --pilot       G0: the Kerr pilot. It is the first gate, and nothing else runs until it passes.
  --controls    G1: the Henon-Heiles calibration against a twin-trajectory Lyapunov, plus the ZV thin-layer
                positive control.
  --production  G2: all TS + Kerr levels, parallel over levels (--workers).
"""

import argparse
import json
import sys
import time
import zlib
from importlib import import_module
from multiprocessing import get_context
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
import sympy as sp
from scipy.spatial import cKDTree

from curvlib import RESULTS

s193 = import_module("193_ts2_screen")          # Spacetime, Reduced, loaders, equatorial_intervals, carter_shell

R_PLUNGE = 3.0                    # r_like < 3m = PLUNGED (also keeps orbits off the ring singularity, as in §193)
R_SEED_MIN = 3.5
H_DRIFT_DROP = 1e-9
T_WINDOW, DT, STRIDE = 1.0e4, 0.05, 10
N_STAGE1, N_STAGE2, N_TRANS = 200, 100, 3
EPS_BINS = (-0.02, -0.01, -0.005, 0.005, 0.02)
ENERGIES = (0.95, 0.97)
KS, THEILER, N_ANCHOR = (20, 40, 80, 160), 200, 100
S3_REG, S3_CHAOS, S4_MIN = 3.4, 2.6, 3.0
TWIN_D0, TWIN_EVERY = 1e-8, 200   # renormalize every 200 steps = 10 tau at dt 0.05


# ---------------------------------------------------------------- the estimator

def local_slopes(Z, rng, ks=KS, theiler=THEILER, n_anchor=N_ANCHOR):
    """Median curvature-scaling slopes (s3, s4) of an orbit's point cloud Z (P, 4), temporal neighbours excluded."""
    Z = (Z - Z.mean(0)) / (Z.std(0) + 1e-300)
    P = len(Z)
    if P < 4 * (max(ks) + 2 * theiler):
        return np.nan, np.nan
    tree = cKDTree(Z)
    anchors = rng.choice(P, size=min(n_anchor, P), replace=False)
    kq = max(ks) + 2 * theiler + 1
    dist, idx = tree.query(Z[anchors], k=kq)
    s3s, s4s = [], []
    for a, d_row, i_row in zip(anchors, dist, idx):
        keep = np.abs(i_row - a) > theiler
        d_row, i_row = d_row[keep], i_row[keep]
        if len(i_row) < max(ks):
            continue
        lr, l3, l4 = [], [], []
        for k in ks:
            nb = Z[i_row[:k]]
            ev = np.sort(np.linalg.eigvalsh(np.cov(nb.T)))[::-1]
            lr.append(np.log(d_row[:k].mean()))
            l3.append(np.log(max(ev[2], 1e-300)))
            l4.append(np.log(max(ev[3], 1e-300)))
        s3s.append(np.polyfit(lr, l3, 1)[0])
        s4s.append(np.polyfit(lr, l4, 1)[0])
    if not s3s:
        return np.nan, np.nan
    return float(np.median(s3s)), float(np.median(s4s))


def verdict(s3, s4):
    if not np.isfinite(s3) or not np.isfinite(s4) or s4 < S4_MIN:
        return "ABSTAIN"
    if s3 >= S3_REG:
        return "REGULAR"
    if s3 <= S3_CHAOS:
        return "CHAOTIC"
    return "ABSTAIN"


# ---------------------------------------------------------------- Henon-Heiles (G1 calibration)

class HenonHeiles:
    label, sig = "HH", None

    def __init__(self, energy):
        self.E0 = energy

    def H(self, z):
        x, y, px, py = z
        return 0.5 * (px ** 2 + py ** 2) + 0.5 * (x ** 2 + y ** 2) + x ** 2 * y - y ** 3 / 3

    def rhs(self, z):
        x, y, px, py = z
        return np.stack([px, py, -(x + 2 * x * y), -(y + x ** 2 - y ** 2)])

    def launch(self, n, rng):
        pts = []
        while len(pts) < n:
            x, y = rng.uniform(-0.5, 0.5), rng.uniform(-0.5, 0.7)
            ke = self.E0 - (0.5 * (x * x + y * y) + x * x * y - y ** 3 / 3)
            if ke <= 1e-3:
                continue
            th = rng.uniform(0, 2 * np.pi)
            v = np.sqrt(2 * ke)
            pts.append((x, y, v * np.cos(th), v * np.sin(th)))
        return np.array(pts).T


# ---------------------------------------------------------------- integration with plunge + twin Lyapunov

def integrate(model, z0, T, dt, stride, twin=True, spin=None):
    """Vectorized RK4. Returns samples (4, P, G) with NaN after plunge, t_plunge (inf if survived), H drift, and the
    twin FTLE (if twin). spin is not None -> also the Kerr Carter drift (G0's integrator gate)."""
    nstep = int(round(T / dt))
    G = z0.shape[1]

    def step(z):
        k1 = model.rhs(z)
        k2 = model.rhs(z + 0.5 * dt * k1)
        k3 = model.rhs(z + 0.5 * dt * k2)
        k4 = model.rhs(z + dt * k3)
        return z + (dt / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)

    z = z0.copy()
    H0 = model.H(z)
    alive = np.ones(G, bool)
    t_plunge = np.full(G, np.inf)
    hdrift = np.zeros(G)
    zt, lsum = None, np.zeros(G)
    if twin:
        zt = z.copy()
        zt[2] += TWIN_D0
    K0 = s193.carter_shell(z, spin, model.E, model.L) if spin is not None else None
    kdrift = np.zeros(G)
    rec = []
    for i in range(nstep):
        z = np.where(alive, step(z), z)
        if twin:
            zt = np.where(alive, step(zt), zt)
        fin = np.isfinite(z).all(0)
        if model.sig is not None:
            fin &= (1 + model.sig * np.where(fin, z[0], 0.0)) >= R_PLUNGE
        newly = alive & ~fin
        t_plunge[newly] = (i + 1) * dt
        alive &= fin
        if i % stride == 0:
            hdrift = np.where(alive, np.maximum(hdrift, np.abs(model.H(z) - H0) / np.abs(H0)), hdrift)
            if spin is not None:
                K = s193.carter_shell(z, spin, model.E, model.L)
                kdrift = np.where(alive, np.maximum(kdrift, np.abs(K - K0) / np.abs(K0)), kdrift)
            snap = z.copy()
            snap[:, ~alive] = np.nan
            rec.append(snap)
        if twin and (i + 1) % TWIN_EVERY == 0:
            d = np.linalg.norm(zt - z, axis=0)
            ok = alive & (d > 0) & np.isfinite(d)
            lsum = np.where(ok, lsum + np.log(np.where(ok, d, 1.0) / TWIN_D0), lsum)
            zt = np.where(ok, z + (zt - z) * (TWIN_D0 / np.where(ok, d, 1.0)), zt)
    life = np.minimum(t_plunge, T)
    out = {"samples": np.stack(rec, 1), "t_plunge": t_plunge, "hdrift": hdrift,
           "ftle": lsum / np.maximum(life, 1e-300) if twin else None}
    if spin is not None:
        out["carter_drift"] = kdrift
    return out


def classify_orbits(res, T, rng, slices=(1.0,)):
    """Per orbit: verdicts on the first fraction f of its life for each f in slices, if the orbit lived >= T/4."""
    S = res["samples"]
    G = S.shape[2]
    rows = []
    for g in range(G):
        Z = S[:, :, g].T
        Z = Z[np.isfinite(Z).all(1)]
        life = min(res["t_plunge"][g], T)
        row = {"t_plunge": float(res["t_plunge"][g]), "hdrift": float(res["hdrift"][g]),
               "ftle": None if res["ftle"] is None else float(res["ftle"][g])}
        if "carter_drift" in res:
            row["carter_drift"] = float(res["carter_drift"][g])
        if life < T / 4 or row["hdrift"] > H_DRIFT_DROP:
            row["verdict"] = "DROPPED" if row["hdrift"] > H_DRIFT_DROP else "SHORT-PLUNGE"
            rows.append(row)
            continue
        for f in slices:
            n = int(len(Z) * f)
            s3, s4 = local_slopes(Z[:n], rng)
            row[f"s3@{f}"], row[f"s4@{f}"], row[f"verdict@{f}"] = s3, s4, verdict(s3, s4)
        row["verdict"] = row[f"verdict@{slices[-1]}"]
        row["fate"] = "SURVIVED" if not np.isfinite(res["t_plunge"][g]) else "STICKY-then-PLUNGED"
        rows.append(row)
    return rows


# ---------------------------------------------------------------- levels

def spacetimes(tag):
    comps, p, q, sig = s193.load_ts(tag)
    return {"TS2": s193.Spacetime(comps, sig, "TS2"), "Kerr": s193.Spacetime(s193.kerr_components(-q, p), p, "Kerr")}, \
        float(-q)


def has_pocket(st, E, L):
    mdl = st.at(E, L)
    xg = np.linspace((R_PLUNGE - 1) / mdl.sig, 80 / mdl.sig, 8000)
    iv = [(1 + mdl.sig * a, 1 + mdl.sig * b) for a, b in s193.equatorial_intervals(mdl, xg)]
    return any(lo > R_PLUNGE + 0.3 and hi < 60 for lo, hi in iv), iv


def l_sep(st, E, sense):
    """Smallest |L| at which the equatorial outer pocket separates from the inner plunge region (bisection)."""
    grid = np.arange(1.5, 6.0, 0.02)
    flags = [has_pocket(st, E, sense * L)[0] for L in grid]
    j = next((k for k, f in enumerate(flags) if f), None)
    if j is None or j == 0:
        return None
    lo, hi = grid[j - 1], grid[j]
    for _ in range(30):
        mid = 0.5 * (lo + hi)
        lo, hi = (lo, mid) if has_pocket(st, E, sense * mid)[0] else (mid, hi)
    return float(hi)


def seed_region(st, E, L):
    """Equatorial r-range to seed: the bounded component reaching the largest r (< 60), from r >= R_SEED_MIN."""
    _, iv = has_pocket(st, E, L)
    cand = [(lo, hi) for lo, hi in iv if hi < 60]
    if not cand:
        return None
    lo, hi = max(cand, key=lambda v: v[1])
    return max(lo, R_SEED_MIN), hi


def seeds(mdl, r_vals):
    x = (np.asarray(r_vals) - 1) / mdl.sig
    y = np.zeros_like(x)
    px = np.zeros_like(x)
    py2 = mdl.py2_on_shell(x, y, px)
    ok = py2 > 0
    return np.array([x[ok], y[ok], px[ok], np.sqrt(py2[ok])]), np.asarray(r_vals)[ok]


def run_level(job):
    """One level: two-stage seeding, integration, classification. job = dict(system, tag, E, L, label)."""
    rng = np.random.default_rng(zlib.crc32(job["label"].encode()))      # deterministic across runs and processes
    sts, spin = spacetimes(job["tag"]) if job["system"] != "ZV2" else (
        {"ZV2": s193.Spacetime(*s193.zv2_components(), "ZV2")}, None)
    st = sts[job["system"]]
    mdl = st.at(job["E"], job["L"])
    reg = seed_region(st, job["E"], job["L"])
    out = {**job, "region_r": reg}
    if reg is None:
        out["status"] = "NO-REGION"
        return out
    z1, r1 = seeds(mdl, np.linspace(reg[0], reg[1], job.get("n1", N_STAGE1)))
    kerr_spin = spin if job["system"] == "Kerr" else None
    res1 = integrate(mdl, z1, job["T"], job["dt"], STRIDE, spin=kerr_spin)
    fate = np.isfinite(res1["t_plunge"])
    trans = [(r1[i], r1[i + 1]) for i in range(len(r1) - 1) if fate[i] != fate[i + 1]][:N_TRANS]
    rows = classify_orbits(res1, job["T"], rng, slices=(0.25, 0.5, 1.0))
    for a, b in trans:
        z2, _ = seeds(mdl, np.linspace(a, b, job.get("n2", N_STAGE2)))
        if z2.shape[1]:
            rows += classify_orbits(integrate(mdl, z2, job["T"], job["dt"], STRIDE, spin=kerr_spin), job["T"], rng,
                                    slices=(0.25, 0.5, 1.0))
    v = [r["verdict"] for r in rows]
    out.update({"status": "DONE", "n_orbits": len(rows), "transitions": [list(t) for t in trans],
                "counts": {k: v.count(k) for k in ("REGULAR", "CHAOTIC", "ABSTAIN", "DROPPED", "SHORT-PLUNGE")},
                "sticky_chaotic": sum(1 for r in rows if r.get("fate") == "STICKY-then-PLUNGED"
                                      and r["verdict"] == "CHAOTIC"),
                "rows": rows})
    if job["system"] == "Kerr":
        cd = [r["carter_drift"] for r in rows if r.get("fate") == "SURVIVED"]
        out["carter_drift_max"] = float(max(cd)) if cd else None
    return out


def level_jobs(systems, tags, T, dt, extra_far=True):
    jobs = []
    for tag in tags:
        sts, _ = spacetimes(tag)
        for sysname in systems:
            st = sts[sysname]
            for E in ENERGIES:
                for sense in (-1, +1):                      # -1 = prograde (J < 0 in BL convention, §193 A1)
                    ls = l_sep(st, E, sense)
                    for eps in EPS_BINS:
                        if ls is None:
                            continue
                        jobs.append({"system": sysname, "tag": tag, "E": E, "L": sense * ls * (1 + eps),
                                     "label": f"{sysname}/{tag}/E{E}/{'pro' if sense < 0 else 'retro'}/eps{eps:+}",
                                     "L_sep": ls, "eps": eps, "T": T, "dt": dt})
            if extra_far:
                jobs.append({"system": sysname, "tag": tag, "E": 0.97, "L": -3.8, "label": f"{sysname}/{tag}/far-193",
                             "eps": None, "T": T, "dt": dt})
                if tag == "t1o3":
                    jobs.append({"system": sysname, "tag": tag, "E": 0.94, "L": dubeibe_L(sts["TS2"]),
                                 "label": f"{sysname}/{tag}/far-dubeibe", "eps": None, "T": T, "dt": dt})
    return jobs


def dubeibe_L(st_ts):
    """Dubeibe 2007's Fig. 1 level is E = 0.94, |L| = 3.12; §150 reports its closed pocket at x in [9.96, 21.9] for
    p = 4/5. Our sign convention may differ from theirs, so pick the sign that reproduces that pocket, or refuse."""
    for L in (-3.12, 3.12):
        mdl = st_ts.at(0.94, L)
        xg = np.linspace(2, 60, 20000)
        for a, b in s193.equatorial_intervals(mdl, xg):
            if abs(a - 9.96) < 0.1 and abs(b - 21.9) < 0.2:
                return L
    raise RuntimeError("Dubeibe pocket x in [9.96, 21.9] not reproduced at either sign -- convention check FAILED")


# ---------------------------------------------------------------- modes

def unit(args):
    """The estimator on synthetic clouds: a 2-torus embedded in 4-D (quasi-periodic, time-ordered) vs a 3-D fill."""
    rng = np.random.default_rng(0)
    t = np.arange(20000) * 0.05
    u, v = 1.0 * t, np.sqrt(2) * t
    torus = np.stack([(2 + np.cos(v)) * np.cos(u), (2 + np.cos(v)) * np.sin(u), np.sin(v), 0.3 * np.cos(u + v)], 1)
    g = rng.normal(size=(20000, 4))
    g[:, 3] = 0.2 * (g[:, 0] ** 2 - g[:, 1] ** 2)                       # a curved 3-D sheet in 4-D
    out = {}
    for name, Z in (("torus", torus), ("fill3d", g)):
        s3, s4 = local_slopes(Z, rng)
        out[name] = {"s3": s3, "s4": s4, "verdict": verdict(s3, s4)}
        print(f"{name}: s3={s3:.2f} s4={s4:.2f} -> {out[name]['verdict']}")
    ok = out["torus"]["verdict"] == "REGULAR" and out["fill3d"]["verdict"] == "CHAOTIC"
    print("UNIT", "PASS" if ok else "FAIL")


def pilot(args):
    """G0, the first gate: Kerr p = 4/5, E = 0.97, prograde, eps in {-0.01, +0.005}."""
    sts, _ = spacetimes("t1o3")
    ls = l_sep(sts["Kerr"], 0.97, -1)
    out = {"gate": "G0", "L_sep": ls, "levels": []}
    for eps in (-0.01, 0.005):
        for dt in (args.dt, args.dt / 2):
            job = {"system": "Kerr", "tag": "t1o3", "E": 0.97, "L": -ls * (1 + eps), "eps": eps, "T": args.T,
                   "dt": dt, "label": f"Kerr/t1o3/pilot/eps{eps:+}/dt{dt}"}
            if dt != args.dt:
                job.update({"n1": 20, "n2": 0})
            r = run_level(job)
            out["levels"].append({k: v for k, v in r.items() if k != "rows"} | {"rows": r.get("rows", [])})
            print(r["label"], r.get("counts"), "carter_drift_max", r.get("carter_drift_max"), flush=True)
    surv = [row for lv in out["levels"] if lv["dt"] == args.dt for row in lv["rows"] if row.get("fate") == "SURVIVED"]
    n = len(surv)
    reg = sum(r["verdict"] == "REGULAR" for r in surv)
    cha = sum(r["verdict"] == "CHAOTIC" for r in surv)
    abst = sum(r["verdict"] == "ABSTAIN" for r in surv)
    cd = max((r["carter_drift"] for r in surv), default=np.inf)
    # robustness clause (iii): 20 orbits, verdicts under dt/2, Theiler x2, and the k-set shifted to {40..320}
    mdl = sts["Kerr"].at(0.97, -ls * 1.005)
    reg_r = seed_region(sts["Kerr"], 0.97, -ls * 1.005)
    z, _ = seeds(mdl, np.linspace(reg_r[0], reg_r[1], 20))
    rng = np.random.default_rng(7)
    a = integrate(mdl, z, args.T, args.dt, STRIDE, twin=False)
    b = integrate(mdl, z, args.T, args.dt / 2, 2 * STRIDE, twin=False)
    same, tot = 0, 0
    for g in range(z.shape[1]):
        if np.isfinite(a["t_plunge"][g]) or np.isfinite(b["t_plunge"][g]):
            continue
        Za, Zb = a["samples"][:, :, g].T, b["samples"][:, :, g].T
        base = verdict(*local_slopes(Za, rng))
        variants = [verdict(*local_slopes(Zb, rng)), verdict(*local_slopes(Za, rng, theiler=2 * THEILER)),
                    verdict(*local_slopes(Za, rng, ks=(40, 80, 160, 320)))]
        same += sum(v == base for v in variants)
        tot += len(variants)
    robust = same / tot if tot else 0.0
    out["G0"] = {"survivors": n, "regular": reg, "chaotic": cha, "abstain": abst, "carter_drift_max": cd,
                 "robust_unchanged_frac": robust,
                 "integrator_ok": bool(cd <= 1e-8),
                 "classifier_ok": bool(n > 0 and reg >= 0.98 * n and cha == 0 and abst <= 0.02 * n),
                 "robust_ok": bool(robust >= 0.95)}
    out["G0"]["pass"] = bool(out["G0"]["integrator_ok"] and out["G0"]["classifier_ok"] and out["G0"]["robust_ok"])
    (RESULTS / "194_pilot.json").write_text(json.dumps(out, indent=1, default=float))
    print("G0:", out["G0"])


def controls(args):
    """G1: Henon-Heiles calibration against twin-trajectory Lyapunov, then the ZV thin-layer positive control."""
    if not _gate_passed("194_pilot.json", "G0"):
        raise SystemExit("G0 has not passed: controls refused (pre-registered order)")
    rng = np.random.default_rng(11)
    hh = {}
    for E in (1 / 12, 0.1657):
        m = HenonHeiles(E)
        r = integrate(m, m.launch(200, np.random.default_rng(int(E * 1e4))), args.T, 0.01, 50)
        rows = classify_orbits(r, args.T, rng)
        hh[E] = rows
    lam_ref = np.median([r["ftle"] for r in hh[1 / 12] if r.get("verdict") in ("REGULAR", "CHAOTIC", "ABSTAIN")])
    agree, tot = 0, 0
    for E, rows in hh.items():
        for r in rows:
            if r.get("verdict") not in ("REGULAR", "CHAOTIC"):
                continue
            if r["ftle"] > 5 * lam_ref:
                tot += 1
                agree += r["verdict"] == "CHAOTIC"
            elif r["ftle"] < 0.2 * lam_ref:
                tot += 1
                agree += r["verdict"] == "REGULAR"
    zv = s193.Spacetime(*s193.zv2_components(), "ZV2")
    zv_levels = []
    for E in ENERGIES:
        ls = l_sep(zv, E, -1)
        for eps in EPS_BINS:
            if ls is None:
                continue
            job = {"system": "ZV2", "tag": "zv", "E": E, "L": -ls * (1 + eps), "eps": eps, "T": args.T, "dt": args.dt,
                   "label": f"ZV2/E{E}/eps{eps:+}"}
            rr = run_level(job)
            zv_levels.append({k: v for k, v in rr.items() if k != "rows"})
            print(rr["label"], rr.get("counts"), "sticky-chaotic", rr.get("sticky_chaotic"), flush=True)
    hits = sum(1 for lv in zv_levels if (lv.get("counts", {}).get("CHAOTIC", 0) + lv.get("sticky_chaotic", 0)) > 0)
    out = {"gate": "G1", "hh_lambda_ref": float(lam_ref), "hh_agreement": agree / tot if tot else 0.0,
           "hh_unambiguous": tot, "zv_levels": zv_levels, "zv_levels_with_chaos": hits}
    out["G1"] = {"hh_ok": bool(tot > 0 and agree / tot >= 0.90), "zv_ok": bool(hits >= 2),
                 "absence_statements_allowed": bool(hits >= 2)}
    out["G1"]["pass"] = out["G1"]["hh_ok"]          # zv_ok gates ABSENCE claims only (pre-reg G1.2)
    (RESULTS / "194_controls.json").write_text(json.dumps(out, indent=1, default=float))
    print("G1:", out["G1"])


def _gate_passed(fname, key):
    f = RESULTS / fname
    return f.exists() and json.loads(f.read_text()).get(key, {}).get("pass", False)


def production(args):
    if not (_gate_passed("194_pilot.json", "G0") and _gate_passed("194_controls.json", "G1")):
        raise SystemExit("G0 and G1 must both pass first: production refused (pre-registered order)")
    jobs = level_jobs(("TS2", "Kerr"), ("t1o2", "t1o3"), args.T, args.dt)
    done_dir = RESULTS / "194_levels"
    done_dir.mkdir(exist_ok=True)
    todo = [j for j in jobs if not (done_dir / (j["label"].replace("/", "_") + ".json")).exists()]
    print(f"{len(jobs)} levels, {len(todo)} to run, {args.workers} workers", flush=True)
    with get_context("spawn").Pool(args.workers) as pool:
        for r in pool.imap_unordered(run_level, todo):
            (done_dir / (r["label"].replace("/", "_") + ".json")).write_text(json.dumps(r, default=float))
            print(r["label"], r.get("counts"), "sticky-chaotic", r.get("sticky_chaotic"), flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    for m in ("unit", "pilot", "controls", "production"):
        ap.add_argument(f"--{m}", action="store_true")
    ap.add_argument("--T", type=float, default=T_WINDOW)
    ap.add_argument("--dt", type=float, default=DT)
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()
    if a.unit:
        unit(a)
    elif a.pilot:
        pilot(a)
    elif a.production:
        production(a)
    elif a.controls:
        controls(a)
