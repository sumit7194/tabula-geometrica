"""Diagnostic (The Bridge, 2026-10-15): does §193's r_like < 3m guard (R_GUARD) ever drop an orbit?
Replays ensemble() exactly (same seeds, same draws, n 60, nstep 20000, dt 0.1, stride 20) for every production shell,
counting drops by reason over ALL launched orbits, plus the minimum r_like reached by any launched orbit."""
import json, sys
from importlib import import_module
from concurrent.futures import ProcessPoolExecutor
import numpy as np
sys.path.insert(0, "/Users/sumit/Github/SpaceTime/curvature/scripts")
m = import_module("193_ts2_screen")
N, NSTEP, DT, STRIDE = 60, 20000, 0.1, 20

def models(tag):
    comps, p, q, sig = m.load_ts(tag)
    sp_ = {"Kerr": m.Spacetime(m.kerr_components(-q, p), p, "Kerr"), "ZV2": m.Spacetime(*m.zv2_components(), "ZV2"),
           "TS2": m.Spacetime(comps, sig, "TS2")}
    sp_["TS2"].B = comps["B"]
    return sp_, float(-q)

def job(a):
    tag, arm, si, E, L, nm = a
    sp_, kerr_a = models(tag)
    mdl = sp_[nm].at(E, L)
    outer = m.outer_interval(mdl)
    xg = np.linspace((m.R_GUARD - 1) / mdl.sig, 80 / mdl.sig, 8000)
    ivs = [(1 + mdl.sig * a_, 1 + mdl.sig * b_) for a_, b_ in m.equatorial_intervals(mdl, xg)]
    xl, xh = ((outer[0] - 1) / mdl.sig, (outer[1] - 1) / mdl.sig)
    seed = 100 * si + {"Kerr": 1, "ZV2": 2, "TS2": 3}[nm]
    rec = {"tag": tag, "arm": arm, "shell": si, "E": E, "L": L, "space": nm, "outer": outer, "eq_intervals": ivs,
           "kerr_a": kerr_a, "ensembles": []}
    for s in (seed, seed + 50):
        rng = np.random.default_rng(s)
        tot = kept = 0; drops = {"r_guard": 0, "y_guard": 0, "nonfinite": 0, "drift": 0}; rmin_all = np.inf; draws = 0
        for _ in range(6):
            draws += 1
            z0 = m.launch(mdl, 2 * N, rng, xl, xh)
            traj = m.rk4(mdl, z0, NSTEP, DT, STRIDE)
            x, y = traj[0], traj[1]
            fin = np.isfinite(traj).all((0, 1))
            r = 1 + mdl.sig * np.where(np.isfinite(x), x, np.inf).min(0)
            rmin_all = min(rmin_all, float(np.nanmin(r)))
            k, drift = m.keep_mask(mdl, traj)
            tot += traj.shape[2]; kept += int(k.sum())
            drops["nonfinite"] += int((~fin).sum())
            drops["r_guard"] += int((fin & (r < m.R_GUARD)).sum())
            drops["y_guard"] += int((fin & (r >= m.R_GUARD) & (np.abs(y).max(0) > m.Y_GUARD)).sum())
            drops["drift"] += int((fin & (r >= m.R_GUARD) & (np.abs(y).max(0) <= m.Y_GUARD) & ~(drift < m.H_DRIFT_KEEP)).sum())
            if kept >= N: break
        rec["ensembles"].append({"seed": s, "draws": draws, "launched": tot, "kept": kept, "drops": drops,
                                 "min_r_like_all_launched": rmin_all})
    return rec

if __name__ == "__main__":
    jobs = []
    for tag in m.POINTS:
        for si, (E, L) in enumerate(m.SHELLS):
            for nm in ("Kerr", "ZV2", "TS2"): jobs.append((tag, "shared", si, E, L, nm))
        for si, (E, L) in enumerate(m.SHELLS_STRONG[tag]):
            for nm in ("Kerr", "TS2"): jobs.append((tag, "strong", si, E, L, nm))
    with ProcessPoolExecutor(8) as ex:
        out = list(ex.map(job, jobs))
    json.dump(out, open(sys.argv[1], "w"), indent=1, default=float)
    for r in out:
        e = r["ensembles"]
        print(f"{r['tag']} {r['arm']:6s} sh{r['shell']} {r['space']:4s} (E {r['E']}, L {r['L']}) outer r {r['outer'][0]:.2f}-{r['outer'][1]:.2f} "
              f"| eq intervals {[(round(a,2),round(b,2)) for a,b in r['eq_intervals']]} | "
              + " ; ".join(f"seed {x['seed']}: {x['kept']}/{x['launched']} kept, drops {x['drops']}, min r {x['min_r_like_all_launched']:.2f}" for x in e))
