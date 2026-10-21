"""§198 -- Tomimatsu-Sato delta=2 thin-chaotic-layer scan, unattended (pre-registration notes/ts_layer_scan_prereg.md,
04ee519 + amendment 1 bb47f7a, both committed before this file existed).

Closed pockets only (D = Dubeibe's level, S1/S2 = just above the barrier separatrix), TS2 vs Kerr through one code
path. Stages: survey -> resonance/separatrix zoom -> long -> dt/2 confirm -> verdict. The instrument is §196's
validated MEGNO (indicators + verdict_megno + the frozen threshold table); sections/rotation numbers via its
sections=True option (MEGNO output verified bit-identical).

  --run [--workers 3]     the whole scan, resumable (finished jobs with identical settings are skipped)
  --smoke                 the same pipeline at toy size into results/198_smoke (for testing only)
  --analyze               re-derive the verdict from the job files on disk
"""
import argparse
import json
import os
import sys
import time
import traceback
from fractions import Fraction
from importlib import import_module
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
c = import_module("196_chaos_indicators")                 # BLAS threads = 1; 193's OpenBLAS tripwire
m94 = c.m94
import numpy as np                                        # noqa: E402

RESULTS = Path(__file__).resolve().parent.parent / "results"
E0, SENSE = 0.94, -1                                      # Dubeibe's energy; prograde (their sign, §150)
LEVELS = [(tag, lvl) for tag in ("t1o3", "t1o2") for lvl in ("D", "S1", "S2")]
EPS = {"S1": 0.003, "S2": 0.01}
PNAME = {"t1o3": "p4/5", "t1o2": "p3/5"}
SYSTEMS = ("TS2", "Kerr")
QMAX, NWIN = 8, 3
KERR_P0, KERR_ALPHA, UNREAD = 0.03, 0.05, 0.25            # amendment 1: deep-v2's gate
ACCEPT = 1e-9

FULL = {"out": RESULTS / "198_ts_layer", "n1": 200, "T1": 3e4, "n2": 60, "T2": 3e4, "T3": 1e5, "batch": 40,
        "levels": LEVELS, "confirm_cap": 40, "kerr3_min": 200}
SMOKE = {"out": RESULTS / "198_smoke", "n1": 12, "T1": 300.0, "n2": 6, "T2": 300.0, "T3": 1000.0, "batch": 6,
         "levels": [("t1o3", "D"), ("t1o3", "S1")], "confirm_cap": 3, "kerr3_min": 2}


# ---------------------------------------------------------------- level geometry (one code path for TS2 and Kerr)

_LEVELS = {}


def level(system, tag, lvl):
    """Cached per process: building a spacetime re-parses the sealed metric (~80 MB each, never freed), so an uncached
    worker grows with every job (measured 2026-10-21). The plunge cut is a module global and is re-set on every call."""
    key = (system, tag, lvl)
    if key not in _LEVELS:
        _LEVELS[key] = _level(*key)
    m94.R_PLUNGE = _LEVELS[key][1]["r_cut"]
    return _LEVELS[key]


_ST = {}


def _level(system, tag, lvl):
    if tag not in _ST:
        _ST[tag] = m94.spacetimes(tag)[0]
    st = _ST[tag][system]
    m94.R_PLUNGE = 3.0                                    # §196 level_model order: separatrix first, then the cut
    ls = c.l_sep_barrier(st, E0, SENSE)
    L = -3.12 if lvl == "D" else SENSE * ls * (1 + EPS[lvl])
    mdl = st.at(E0, L)
    m94.R_PLUNGE = c.r_cut_for(mdl)
    closed, _ = m94.has_pocket(st, E0, L)
    reg = m94.seed_region(st, E0, L)
    return mdl, {"L": float(L), "l_sep": ls, "r_cut": m94.R_PLUNGE, "closed": bool(closed),
                 "region_r": list(reg) if reg else None}


def line(mdl, xa, xb, n):
    step = (xb - xa) / (n - 1)
    xs = np.linspace(xa + step / 5, xb - step / 5, n)
    py2 = mdl.py2_on_shell(xs, np.zeros_like(xs), np.zeros_like(xs))
    ok = py2 > 0
    return xs[ok], np.array([xs[ok], np.zeros(ok.sum()), np.zeros(ok.sum()), np.sqrt(py2[ok])])


# ---------------------------------------------------------------- one job (runs in a spawned worker)

def job_run(job):
    try:
        mdl, info = level(job["system"], job["tag"], job["lvl"])
        x0 = np.array(job["x0"])
        py2 = mdl.py2_on_shell(x0, np.zeros_like(x0), np.zeros_like(x0))
        z = np.array([x0, np.zeros_like(x0), np.zeros_like(x0), np.sqrt(np.clip(py2, 0, None))])
        T = job["T"]
        if job["kind"] == "pilot":
            try:
                dt, drift, pinfo = c.pilot_dt_v2(mdl, z, T)
                res = {"dt": dt, "pilot_drift": drift, "pilot_v2": pinfo}
            except c.PilotRefused as e:
                res = {"refused": str(e)}
        else:
            t0 = time.time()
            r = c.indicators(mdl, z, T, job["dt"], job["seed"], series_dt=5.0, sections=True)
            fv = os.environ.get("TABULA198_SMOKE_FORCE", "")
            force = bool(fv) and (job["system"] == "TS2" or fv == "all")
            if force and Path(job["out"]).name != "198_smoke":
                raise RuntimeError("TABULA198_SMOKE_FORCE is a smoke-test switch; refused outside results/198_smoke")
            res = {"orbits": orbit_rows(r, x0, T, force), "wall_s": time.time() - t0}
        res.update(job=job, level=info)
        _write(Path(job["out"]) / f"{job['name']}.json", res)
        return job["name"], None
    except Exception:
        return job["name"], traceback.format_exc()


def orbit_rows(r, x0, T, force=False):
    table = json.load(open(c.TABLE_FILE))
    if force:                                             # TEST ONLY (smoke): exercises the CHAOTIC/confirm path
        table["threshold_p99"] = [-1e9] * len(table["threshold_p99"])
    t = np.array(r["series"]["t"])
    YA = np.array(r["series"]["YA"], float)
    hd = np.array(r["series"]["hd"], float)
    rows = []
    for g in range(len(x0)):
        tp = r["t_plunge"][g]
        life = float(tp) if np.isfinite(tp) else float(T)
        v, val = c.verdict_megno(t, YA[:, g], life, T, table)
        tdec = np.floor(min(life, T) / c.GRID) * c.GRID
        i = np.where(t <= tdec + 1e-6)[0]
        drift = float(hd[i[-1], g]) if len(i) else None
        ck = {str(int(k)): v["megno"][0][g] for k, v in r["checkpoints"].items()}
        nx, ny = r["n_xmax"][g], r["n_ycross"][g]
        rows.append({"x0": float(x0[g]), "life": life, "bound": life >= T, "verdict_table": v, "megno_tdec": val,
                     "drift": drift, "accepted": drift is not None and drift <= ACCEPT, "Y": ck,
                     "fli_T": (r["checkpoints"][max(r["checkpoints"])]["fli"][0][g] if r["checkpoints"] else None),
                     "n_xmax": nx, "n_ycross": ny, "nu": (ny / nx if nx else None),
                     "section": [[round(a, 3), round(b, 9), round(p, 9)] for a, b, p in r["sections"][g]]})
    return rows


def _write(path, obj):
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(obj, default=float))
    os.replace(tmp, path)


def _done(job):
    f = Path(job["out"]) / f"{job['name']}.json"
    if not f.exists():
        return False
    try:
        return json.load(open(f)).get("job") == job
    except Exception:
        return False


# ---------------------------------------------------------------- driver: phases, pool, status

class Status:
    def __init__(self, cfg):
        self.f = cfg["out"] / "198_status.json" if cfg is SMOKE else RESULTS / "198_status.json"
        self.s = {"run": "§198 TS2 thin-layer scan", "pid": os.getpid(), "started": _now(), "phases_done": [],
                  "phase": None, "errors": [], "verdict": None}

    def put(self, **kw):
        self.s.update(kw, updated=_now())                 # 'updated' moves only with content (keepalive lesson)
        _write(self.f, self.s)


def _now():
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")


def run_jobs(jobs, workers, status, phase):
    from multiprocessing import get_context
    todo = [j for j in jobs if not _done(j)]
    status.put(phase=phase, jobs_total=len(jobs), jobs_done=len(jobs) - len(todo), eta_h=None)
    if not todo:
        return
    t0, done = time.time(), 0
    with get_context("spawn").Pool(min(workers, len(todo)), maxtasksperchild=1) as pool:   # memory: one job each
        for name, err in pool.imap_unordered(job_run, sorted(todo, key=lambda j: -j["T"] * len(j["x0"]))):
            done += 1
            if err:
                status.s["errors"].append({"job": name, "trace": err[-1500:], "at": _now()})
            rate = (time.time() - t0) / done
            status.put(jobs_done=len(jobs) - len(todo) + done, last_job=name,
                       eta_h=round(rate * (len(todo) - done) / 3600, 2))
            print(f"[{phase}] done {name}{' ERROR' if err else ''}", flush=True)


def _load(cfg, name):
    f = cfg["out"] / f"{name}.json"
    return json.load(open(f)) if f.exists() else None


def batches(cfg, stage, system, tag, lvl, xs, T, dt, seed0):
    b = cfg["batch"]
    return [{"name": f"{stage}_{system}_{tag}_{lvl}_b{k}", "kind": "run", "stage": stage, "system": system, "tag": tag,
             "lvl": lvl, "x0": [float(x) for x in xs[i:i + b]], "T": T, "dt": dt, "seed": seed0 + k,
             "out": str(cfg["out"])} for k, i in enumerate(range(0, len(xs), b))]


def pilot_job(cfg, stage, system, tag, lvl, xs, T):
    return {"name": f"pilot{stage}_{system}_{tag}_{lvl}", "kind": "pilot", "stage": stage, "system": system,
            "tag": tag, "lvl": lvl, "x0": [float(x) for x in xs], "T": T, "out": str(cfg["out"])}


def rows_of(cfg, stage, system, tag, lvl):
    out = []
    k = 0
    while (d := _load(cfg, f"{stage}_{system}_{tag}_{lvl}_b{k}")) is not None:
        out += d.get("orbits", [])
        k += 1
    return sorted(out, key=lambda r: r["x0"])


def windows(rows, x_lo, x_hi, separatrix):
    """Pre-registered: rationals p/q (q <= 8) crossed by nu between adjacent accepted bound seeds; 3 lowest q
    (ties: smaller p/q); window = bracket widened one step each side. S levels add the 3 innermost steps."""
    ok = [r for r in rows if r["accepted"] and r["bound"] and r["nu"]]
    xs = [r["x0"] for r in ok]
    cand = {}
    for k in range(len(ok) - 1):
        a, b = sorted((ok[k]["nu"], ok[k + 1]["nu"]))
        for q in range(1, QMAX + 1):
            for p in range(int(np.floor(a * q)), int(np.ceil(b * q)) + 1):
                fr = Fraction(p, q)
                if a < fr < b and fr not in cand:
                    cand[fr] = (max(x_lo, xs[max(k - 1, 0)]), min(x_hi, xs[min(k + 2, len(xs) - 1)]))
    w = []
    for f in sorted(cand, key=lambda f: (f.denominator, f)):         # a rational sharing an already-picked
        if len(w) < NWIN and all(list(cand[f]) != x["x"] for x in w):  # bracket is skipped (amendment 2)
            w.append({"tag": f"nu={f}", "q": f.denominator, "x": list(cand[f])})
    if separatrix and len(xs) >= 4:
        w.append({"tag": "separatrix", "q": None, "x": [x_lo, xs[3]]})
    return w


def _geometry(levels, n1):
    """Child-process task: the closed-pocket seed range and stage-1 line of every (system, tag, level)."""
    geo, lines = {}, {}
    for tag, lvl in levels:
        for system in SYSTEMS:
            mdl, info = level(system, tag, lvl)
            if info["closed"] and info["region_r"]:
                xa, xb = [(r - 1) / mdl.sig for r in info["region_r"]]
                geo[(system, tag, lvl)] = (xa, xb, info)
                lines[(system, tag, lvl)] = line(mdl, xa, xb, n1)[0].tolist()
            else:
                geo[(system, tag, lvl)] = (None, None, info)
    return geo, lines


def _window_lines(reqs):
    """Child-process task: stage-2 seed lines, reqs = [(key, xa, xb, n)]."""
    return [line(level(*k)[0], xa, xb, n)[0].tolist() for k, xa, xb, n in reqs]


def in_child(fn, *args):
    """Run fn in a fresh spawned process: building a spacetime costs ~0.5 GB that Python never returns, and the
    parent lives for days, so the parent never builds one itself (measured 2026-10-21)."""
    from multiprocessing import get_context
    with get_context("spawn").Pool(1) as pool:
        return pool.apply(fn, args)


def scan(cfg, workers):
    cfg["out"].mkdir(parents=True, exist_ok=True)
    status = Status(cfg)
    status.put(phase="setup", config={k: (str(v) if isinstance(v, Path) else v) for k, v in cfg.items()})
    geo, lines = in_child(_geometry, cfg["levels"], cfg["n1"])
    for k, (xa, _, info) in list(geo.items()):
        if xa is None:
            status.s["errors"].append({"job": f"level {' '.join(k)}", "trace": f"not closed: {info}"})
            del geo[k]
    _write(cfg["out"] / "geometry.json", {" ".join(k): v for k, v in geo.items()})
    lines = {k: np.array(v) for k, v in lines.items()}

    # stage 1: pilots then the survey line
    run_jobs([pilot_job(cfg, 1, *k, xs, cfg["T1"]) for k, xs in lines.items()], workers, status, "pilot1")
    dt1 = {k: (_load(cfg, f"pilot1_{k[0]}_{k[1]}_{k[2]}") or {}).get("dt") for k in lines}
    jobs = []
    for i, (k, xs) in enumerate(lines.items()):
        if dt1[k]:
            jobs += batches(cfg, "s1", *k, xs, cfg["T1"], dt1[k], 1000 + 50 * i)
    run_jobs(jobs, workers, status, "stage1")
    status.s["phases_done"].append("stage1")

    # stage 2: windows from each system's own nu(x0)
    win, reqs = {}, []
    for k in lines:
        if dt1[k]:
            xa, xb, _ = geo[k]
            win[k] = windows(rows_of(cfg, "s1", *k), xa, xb, separatrix=(k[2] != "D"))
            reqs += [(k, w["x"][0], w["x"][1], cfg["n2"]) for w in win[k]]
    got = iter(in_child(_window_lines, reqs) if reqs else [])
    jobs = []
    for i, k in enumerate(lines):
        for j, w in enumerate(win.get(k, [])):
            w["x0"] = next(got)
            jobs += batches(cfg, f"s2w{j}", *k, np.array(w["x0"]), cfg["T2"], dt1[k], 3000 + 50 * i + 7 * j)
    _write(cfg["out"] / "windows.json", {" ".join(k): v for k, v in win.items()})
    run_jobs(jobs, workers, status, "stage2")
    status.s["phases_done"].append("stage2")

    # stage 3: the lowest-q window (D) or the separatrix window (S), long, own pilot at T3
    sel = {}
    for k, ws in win.items():
        cands = [w for w in ws if (w["tag"] == "separatrix") == (k[2] != "D")]
        if cands:
            sel[k] = min(cands, key=lambda w: (w["q"] or 0))
    run_jobs([pilot_job(cfg, 3, *k, np.array(w["x0"]), cfg["T3"]) for k, w in sel.items()], workers, status, "pilot3")
    jobs = []
    for i, (k, w) in enumerate(sel.items()):
        dt3 = (_load(cfg, f"pilot3_{k[0]}_{k[1]}_{k[2]}") or {}).get("dt")
        if dt3:
            jobs += batches(cfg, "s3", *k, np.array(w["x0"]), cfg["T3"], dt3, 5000 + 50 * i)
    run_jobs(jobs, workers, status, "stage3")
    status.s["phases_done"].append("stage3")

    # stage 4: dt/2 confirmation of every TS2 CHAOTIC orbit (cap per level, seed order)
    v = verdict(cfg, confirm=False)
    jobs = []
    for i, (tag, lvl) in enumerate(cfg["levels"]):
        allc = sorted(v["levels"].get(f"{tag} {lvl}", {}).get("ts_chaotic", []), key=lambda r: r["x0"])
        keep = allc[:cfg["confirm_cap"]]                  # cap per LEVEL, seed order (prereg stage 4)
        for stage, T, dtsrc in (("s1", cfg["T1"], "pilot1"), ("s2", cfg["T2"], "pilot1"), ("s3", cfg["T3"], "pilot3")):
            xs = [r["x0"] for r in keep if r["stage"] == stage]
            dt = (_load(cfg, f"{dtsrc}_TS2_{tag}_{lvl}") or {}).get("dt")
            if xs and dt:
                jobs += batches(cfg, f"c{stage}", "TS2", tag, lvl, np.array(xs), T, dt / 2, 7000 + 50 * i)
    run_jobs(jobs, workers, status, "confirm")
    status.s["phases_done"].append("confirm")
    v = verdict(cfg, confirm=True)
    _write(cfg["out"] / "198_summary.json" if cfg is SMOKE else RESULTS / "198_summary.json", v)
    report(cfg, v)
    status.put(phase="DONE", verdict=v["overall"])


# ---------------------------------------------------------------- verdict (pre-registered rules)

def verdict(cfg, confirm):
    from scipy.stats import binom
    stages12 = lambda s, k: rows_of(cfg, "s1", s, *k) + [r for j in range(NWIN + 1)
                                                         for r in rows_of(cfg, f"s2w{j}", s, *k)]
    k1, k3 = str(int(cfg["T1"])), str(int(cfg["T3"]))
    kerr3 = [r for (tag, lvl) in cfg["levels"] for r in rows_of(cfg, "s3", "Kerr", tag, lvl)
             if r["accepted"] and r["bound"] and r["Y"].get(k3) is not None]
    thr3 = max(r["Y"][k3] for r in kerr3) if len(kerr3) >= cfg["kerr3_min"] else None
    out = {"thr3_kerr_max": thr3, "n_kerr3": len(kerr3), "stage3_readable": thr3 is not None, "levels": {}}

    def chaotic3(r):
        y1, y0 = r["Y"].get(k3), r["Y"].get(k1)
        return thr3 is not None and y1 is not None and y0 is not None and y1 > thr3 and y1 > y0 + 1

    try:
        win = json.load(open(cfg["out"] / "windows.json"))
    except Exception:
        win = {}
    for tag, lvl in cfg["levels"]:
        k = (tag, lvl)
        rec = {"p": PNAME[tag], "level": lvl}
        ts12, kr12 = stages12("TS2", k), stages12("Kerr", k)
        ts3, kr3 = rows_of(cfg, "s3", "TS2", *k), rows_of(cfg, "s3", "Kerr", *k)
        acc = lambda rs: [r for r in rs if r["accepted"]]
        nK = len(acc(kr12))
        kK = sum(r["verdict_table"] == "CHAOTIC" for r in acc(kr12))
        kerr_any = kK + sum(chaotic3(r) for r in acc(kr3) if r["bound"])
        rec.update(n_ts12=len(ts12), n_ts12_accepted=len(acc(ts12)), n_kerr12_accepted=nK, kerr12_chaotic=kK,
                   kerr_chaotic_all_stages=int(kerr_any))
        rec["unreadable"] = (nK == 0 or not ts12 or (len(ts12) - len(acc(ts12))) > UNREAD * len(ts12))
        rec["kerr_gate_p"] = float(binom.sf(kK - 1, nK, KERR_P0)) if nK else None
        rec["kerr_gate_pass"] = (not rec["unreadable"]) and rec["kerr_gate_p"] >= KERR_ALPHA
        chaos = [dict(r, stage="s1") for r in acc(rows_of(cfg, "s1", "TS2", *k))
                 if r["bound"] and r["verdict_table"] == "CHAOTIC"]
        chaos += [dict(r, stage="s2") for j in range(NWIN + 1) for r in acc(rows_of(cfg, f"s2w{j}", "TS2", *k))
                  if r["bound"] and r["verdict_table"] == "CHAOTIC"]
        chaos += [dict(r, stage="s3") for r in acc(ts3) if r["bound"] and chaotic3(r)]
        if confirm:
            for r in chaos:
                cr = [x for x in rows_of(cfg, f"c{r['stage']}", "TS2", *k) if abs(x["x0"] - r["x0"]) < 1e-12]
                r["confirmed"] = bool(cr) and cr[0]["accepted"] and cr[0]["bound"] and (
                    chaotic3(cr[0]) if r["stage"] == "s3" else cr[0]["verdict_table"] == "CHAOTIC")
        rec["ts_chaotic"] = [{k_: r[k_] for k_ in ("x0", "stage", "nu", "megno_tdec", "Y") if k_ in r}
                             | {"confirmed": r.get("confirmed")} for r in chaos]
        good = [r for r in chaos if r.get("confirmed")]
        cluster = None
        for w in win.get(f"TS2 {tag} {lvl}", []):
            inw = [r for r in good if w["x"][0] <= r["x0"] <= w["x"][1]]      # any stage (prereg: seeds in window)
            if len(inw) >= 3:
                cluster = {"window": w["tag"], "x": w["x"], "n": len(inw),
                           "nu": [min(r["nu"] for r in inw), max(r["nu"] for r in inw)]}
                break
        s1x = [r["x0"] for r in rows_of(cfg, "s1", "TS2", *k)]
        if cluster is None and len(good) >= 3:
            idx = sorted(s1x.index(r["x0"]) for r in good if r["stage"] == "s1" and r["x0"] in s1x)
            for a in range(len(idx) - 2):
                if idx[a + 2] - idx[a] <= 2:
                    cluster = {"window": "stage1-adjacent", "seed_index": idx[a:a + 3]}
                    break
        rec["layer"] = bool(confirm and rec["kerr_gate_pass"] and cluster is not None and kerr_any == 0)
        rec["cluster"] = cluster
        xs = sorted(s1x)
        rec["resolution"] = {"stage1_dx": (xs[1] - xs[0]) if len(xs) > 1 else None,
                             "stage2_dx_min": min((w["x"][1] - w["x"][0]) / (cfg["n2"] - 1)
                                                  for w in win.get(f"TS2 {tag} {lvl}", [{"x": [0, 1e9]}])),
                             "T": [cfg["T1"], cfg["T3"]],
                             "nu_resolution": 1 / max((r["n_xmax"] for r in ts12 if r["n_xmax"]), default=1)}
        out["levels"][f"{tag} {lvl}"] = rec
    lv = out["levels"].values()
    if any(r["layer"] for r in lv):
        out["overall"] = "LAYER-FOUND: " + ", ".join(f"{r['p']} {r['level']}" for r in lv if r["layer"])
    elif all(r["unreadable"] or not r["kerr_gate_pass"] for r in lv):
        out["overall"] = "UNREADABLE"
    else:
        out["overall"] = "NO-LAYER-RESOLVED (not seen at this resolution; not a statement of integrability)"
    return out


def report(cfg, v):
    L = ["# §198 TS δ=2 thin-chaotic-layer scan: result", "", f"**Overall: {v['overall']}**", "",
         f"Stage-3 Kerr null threshold (max ⟨Y⟩ at T3 = {cfg['T3']:g} over {v['n_kerr3']} Kerr orbits): {v['thr3_kerr_max']}", "",
         "| p | level | TS2 orbits (accepted) | TS2 CHAOTIC (confirmed) | Kerr CHAOTIC | Kerr gate p | layer |",
         "|---|---|---|---|---|---|---|"]
    for r in v["levels"].values():
        nc = len(r["ts_chaotic"]); ncc = sum(1 for x in r["ts_chaotic"] if x.get("confirmed"))
        L.append(f"| {r['p']} | {r['level']} | {r['n_ts12']} ({r['n_ts12_accepted']}) | {nc} ({ncc}) | "
                 f"{r['kerr_chaotic_all_stages']} | {r['kerr_gate_p']} | {'YES' if r['layer'] else 'no'} |")
    L += ["", "Rules: notes/ts_layer_scan_prereg.md (04ee519 + amendment 1 bb47f7a). A null means 'not seen at this "
          "resolution' (see the summary JSON's per-level resolution), never 'integrable'."]
    (cfg["out"] / "198_REPORT.md" if cfg is SMOKE else RESULTS / "198_REPORT.md").write_text("\n".join(L) + "\n")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--analyze", action="store_true")
    ap.add_argument("--workers", type=int, default=3)
    a = ap.parse_args()
    cfg = SMOKE if a.smoke else FULL
    if a.analyze:
        v = verdict(cfg, confirm=True)
        report(cfg, v)
        print(json.dumps({k: x for k, x in v.items() if k != "levels"}, indent=1))
    elif a.run or a.smoke:
        scan(cfg, a.workers)
