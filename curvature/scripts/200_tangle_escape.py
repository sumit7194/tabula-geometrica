"""§200 -- does the measured tangle produce chaos? (pre-registration notes/tangle_escape_prereg.md, 69d85d8 + amendments)

PRIMARY: uncertainty exponent of the escape-count function n(x0) on a section segment through §199's primary
homoclinic point (p_x = 0, centred on x_h, half-width 2% of x_h). n = upward section crossings before the orbit
plunges (r < §196's r_cut), capped at NCAP (the cap is an outcome value: orbits outside the separatrix loop are
trapped). f(delta) = fraction of base points with n(x0) != n(x0 + delta*L); alpha = slope of log f vs log delta.
Kerr (integrable) -> alpha ~ 1; a chaotic saddle -> alpha < 1.

  --time SYS TAG EPS N   timing probe (N orbits)
  --run [--workers 2]    all jobs (resumable: per-job JSON skip-if-done) -> results/200_tangle/
  --analyze              verdicts -> results/200_summary.json + 200_REPORT.md
"""
import argparse
import json
import os
import sys
import time
from importlib import import_module
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
s199 = import_module("199_separatrix_splitting")
c, m94 = s199.c, s199.m94
import numpy as np                                        # noqa: E402

RESULTS = Path(__file__).resolve().parent.parent / "results"
OUT = RESULTS / "200_tangle"
DT = 0.025
CFG = {"n_base": 500, "deltas": [1e-2, 3e-3, 1e-3, 3e-4, 1e-4, 3e-5, 1e-5, 3e-6, 1e-6], "ncap": 60}
LEVELS = [(s, t, e) for t in ("t1o2", "t1o3") for e in (-0.003, -0.01, -0.03) for s in ("TS2", "Kerr")]


def level(system, tag, eps):
    mdl, info = s199.setup(system, tag, eps)
    m94.R_PLUNGE = c.r_cut_for(mdl)
    row = next(r for r in json.load(open(RESULTS / "199_splitting.json"))["rows"]
               if r.get("system") == system and r.get("tag") == tag and r.get("eps") == eps and r.get("rtol") == 1e-13)
    return mdl, dict(info, x_h=row["z_h"][0], r_cut=m94.R_PLUNGE)


def escape_counts(mdl, x0, ncap, dt=DT, tmax=None):
    """Vectorised RK4 from (x0, y=0, px=0, py>0 on shell). Returns n (crossings before plunge; ncap if capped;
    -1 if off-shell) and the plunge flag. Only live orbits are stepped (arrays compressed)."""
    x0 = np.asarray(x0, float)
    py2 = mdl.py2_on_shell(x0, np.zeros_like(x0), np.zeros_like(x0))
    n = np.full(len(x0), -1, int)
    ok = np.isfinite(py2) & (py2 > 0)
    idx = np.flatnonzero(ok)
    z = np.array([x0[ok], np.zeros(ok.sum()), np.zeros(ok.sum()), np.sqrt(py2[ok])])
    cnt = np.zeros(len(idx), int)
    plunged = np.zeros(len(x0), bool)
    tmax = tmax or ncap * 400.0
    t = 0.0
    while len(idx) and t < tmax:
        k1 = mdl.rhs(z); k2 = mdl.rhs(z + 0.5 * dt * k1); k3 = mdl.rhs(z + 0.5 * dt * k2); k4 = mdl.rhs(z + dt * k3)
        zn = z + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        t += dt
        cnt += (z[1] < 0) & (zn[1] >= 0) & (zn[3] > 0)
        dead = ~np.isfinite(zn).all(0) | ((1 + mdl.sig * np.where(np.isfinite(zn[0]), zn[0], 0)) < m94.R_PLUNGE)
        capped = cnt >= ncap
        done = dead | capped
        if done.any():
            n[idx[done]] = np.where(dead[done], cnt[done], ncap)
            plunged[idx[done]] = dead[done]
            keep = ~done
            idx, z, cnt = idx[keep], zn[:, keep], cnt[keep]
        else:
            z = zn
    n[idx] = ncap                                          # time cap reached: trapped
    return n, plunged


def seeds(info, cfg, seed):
    rng = np.random.default_rng(seed)
    xh, hw = info["x_h"], 0.02 * info["x_h"]
    L = 2 * hw
    base = rng.uniform(xh - hw, xh + hw - max(cfg["deltas"]) * L, cfg["n_base"])
    return base, L


def job(spec):
    system, tag, eps, dt = spec
    name = f"{system}_{tag}_{eps}_dt{dt}"
    f = OUT / f"{name}.json"
    if f.exists():
        return name, "skip"
    t0 = time.time()
    mdl, info = level(system, tag, eps)
    base, L = seeds(info, CFG, seed=200)
    xs = np.concatenate([base] + [base + d * L for d in CFG["deltas"]])
    n, pl = escape_counts(mdl, xs, CFG["ncap"], dt=dt)
    nb = len(base)
    res = {"spec": spec, "info": info, "cfg": CFG, "n_base": n[:nb].tolist(),
           "n_shift": {str(d): n[nb * (i + 1): nb * (i + 2)].tolist() for i, d in enumerate(CFG["deltas"])},
           "plunged_frac": float(pl.mean()), "capped_frac": float((n == CFG["ncap"]).mean()),
           "offshell": int((n < 0).sum()), "wall_s": time.time() - t0, "platform": "macOS 27.2"}
    tmp = f.with_suffix(".tmp"); tmp.write_text(json.dumps(res, default=float)); os.replace(tmp, f)
    return name, f"{res['wall_s']:.0f}s"


# ---------------------------------------------------------------- amendment 1: zoom design (b710291)
ZOOM = {"windows": [1e-2, 1e-3, 1e-4, 1e-5, 1e-6], "npts": 801, "cap": 12, "rtols": [1e-13, 1e-12]}
ZOOM_ORDER = [("t1o2", -0.03), ("t1o2", -0.01), ("t1o2", -0.003), ("t1o3", -0.03), ("t1o3", -0.01), ("t1o3", -0.003)]


def n_hp(M, x0, cap):
    """Section returns before plunge with §199's DOP853 map; -1 off-shell, cap if trapped."""
    py2 = M.mdl.py2_on_shell(np.array(x0), np.array(0.0), np.array(0.0))
    if not np.isfinite(py2) or py2 <= 0:
        return -1
    q = np.array([x0, 0.0])
    for k in range(cap):
        q = M.P(q)
        if q is None:
            return k
    return cap


def zoom_job(spec):
    system, tag, eps, rtol, w = spec
    name = f"zoom_{system}_{tag}_{eps}_r{rtol:.0e}_w{w:.0e}"
    f = OUT / f"{name}.json"
    if f.exists():
        return name, "skip"
    t0 = time.time()
    mdl, info = s199.setup(system, tag, eps)
    row = next(r for r in json.load(open(RESULTS / "199_splitting.json"))["rows"]
               if r.get("system") == system and r.get("tag") == tag and r.get("eps") == eps and r.get("rtol") == 1e-13)
    xh = row["z_h"][0]
    M = s199.Map(mdl, rtol)
    xs = np.linspace(xh * (1 - w), xh * (1 + w), ZOOM["npts"])
    n = [n_hp(M, float(x), ZOOM["cap"]) for x in xs]
    res = {"spec": list(spec), "x_h": xh, "x": xs.tolist(), "n": n, "wall_s": time.time() - t0,
           "platform": "macOS 27.2", "prereg": "notes/tangle_escape_prereg.md 69d85d8 + amendment 1 b710291"}
    tmp = f.with_suffix(".tmp"); tmp.write_text(json.dumps(res, default=float)); os.replace(tmp, f)
    return name, f"{res['wall_s']:.0f}s"


def zoom_run(workers):
    from multiprocessing import get_context
    OUT.mkdir(parents=True, exist_ok=True)
    specs = [(s, t, e, r, w) for t, e in ZOOM_ORDER for s in ("TS2", "Kerr") for w in ZOOM["windows"] for r in ZOOM["rtols"]]
    st = RESULTS / "200_status.json"
    done = 0
    with get_context("spawn").Pool(workers, maxtasksperchild=1) as pool:
        for name, msg in pool.imap(zoom_job, specs):     # in registered order: levels finish one at a time
            done += 1
            st.write_text(json.dumps({"done": done, "total": len(specs), "last": name, "msg": msg,
                                      "updated": time.strftime("%Y-%m-%dT%H:%M:%S%z")}))
            print(f"[{done}/{len(specs)}] {name} {msg}", flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--time", nargs=4)
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--zoom", action="store_true")
    ap.add_argument("--smoke-zoom", action="store_true")
    a = ap.parse_args()
    if a.smoke_zoom:
        ZOOM["npts"] = 9; OUT = RESULTS / "200_smoke"; OUT.mkdir(parents=True, exist_ok=True)
        for spec in [("TS2", "t1o2", -0.03, 1e-13, 1e-4), ("Kerr", "t1o2", -0.03, 1e-13, 1e-4)]:
            print(zoom_job(spec))
        sys.exit(0)
    if a.zoom:
        zoom_run(a.workers); sys.exit(0)
    if a.time:
        mdl, info = level(a.time[0], a.time[1], float(a.time[2]))
        N = int(a.time[3]); xs = np.linspace(info["x_h"] * 0.98, info["x_h"] * 1.02, N)
        t0 = time.time(); n, pl = escape_counts(mdl, xs, CFG["ncap"])
        print(json.dumps({"N": N, "wall_s": round(time.time() - t0, 1), "capped_frac": float((n == CFG["ncap"]).mean()),
                          "plunged_frac": float(pl.mean()), "offshell": int((n < 0).sum()),
                          "n_median_escaped": float(np.median(n[pl])) if pl.any() else None}))
