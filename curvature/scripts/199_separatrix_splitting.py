"""§199 -- separatrix splitting at the TS delta=2 equatorial saddle-centre (pre-registration
notes/separatrix_splitting_prereg.md, 8feff19 + amendment 1 27a7be6, both before this file).

Per (system, p, eps, rtol): the Lyapunov orbit = hyperbolic fixed point z* of the y = 0 (p_y > 0) section map P;
reversor gate R0 (S(x, px) = (x, -px), W^s = S W^u); the pocket branch of W^u to its first crossing of px = 0
(the primary symmetric homoclinic point z_h); splitting angle theta = angle(t, S t) of the W^u tangent t at z_h.
Kerr (integrable: W^u = W^s, theta = 0) gives the numerical floor.

  --run [--workers 4]   all levels -> results/199_splitting.json + 199_REPORT.md
  --one SYS TAG EPS     a single level (test)
"""
import argparse
import json
import sys
import time
from importlib import import_module
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
c = import_module("196_chaos_indicators")
m94 = c.m94
import numpy as np                                        # noqa: E402
from scipy.integrate import solve_ivp                    # noqa: E402

RESULTS = Path(__file__).resolve().parent.parent / "results"
E0, SENSE = 0.94, -1
EPSS = (-0.003, -0.01, -0.03, -0.1)
TAGS = {"t1o3": "p4/5", "t1o2": "p3/5"}
TMAX, S0, NMAX, K = 5000.0, 1e-7, 40, 60
DELTAS = (1e-4, 1e-5)


def setup(system, tag, eps):
    st = m94.spacetimes(tag)[0][system]
    m94.R_PLUNGE = 3.0
    ls = c.l_sep_barrier(st, E0, SENSE)
    mdl = st.at(E0, SENSE * ls * (1 + eps))
    rb, Vb = c.barrier(mdl)
    return mdl, {"l_sep": ls, "L": mdl.L, "r_b": rb, "V_b": Vb, "h": (-0.5 - Vb) if Vb is not None else None}


class Map:
    def __init__(self, mdl, rtol):
        self.mdl, self.rtol = mdl, rtol
        self.rcut = c.r_cut_for(mdl)       # §196/198's barrier-based plunge cut (x = 1.0005 let TS2 plungers grind
                                            # in the near-singular region at tiny steps: 4 GB watchdog kill, run 1)

    def _f(self, t, z):
        return self.mdl.rhs(z)

    def _leg(self, z, direction):
        ev = lambda t, zz: zz[1]
        ev.terminal, ev.direction = True, direction
        dead = lambda t, zz: (1 + self.mdl.sig * zz[0]) - self.rcut
        dead.terminal = True
        r = solve_ivp(self._f, (0, TMAX), z, method="DOP853", rtol=self.rtol, atol=self.rtol, events=(ev, dead),
                      t_eval=[])                       # store no steps: only the event state is used
        if len(r.t_events[0]) == 0:
            return None
        return r.y_events[0][0]

    def P(self, q):
        """(x, px) on y = 0, p_y > 0 -> next such crossing; None if off-shell, plunging or no return by TMAX."""
        x, px = q
        py2 = self.mdl.py2_on_shell(np.array(x), np.array(0.0), np.array(px))
        if not np.isfinite(py2) or py2 <= 0:
            return None
        z = np.array([x, 0.0, px, np.sqrt(py2)])
        a = self._leg(z, -1)                                 # phase 1: the downward crossing (start can't count)
        if a is None:
            return None
        b = self._leg(a, +1)                                 # phase 2: the next upward crossing
        return None if b is None else np.array([b[0], b[2]])

    def Pn(self, q, n):
        for _ in range(n):
            q = self.P(q)
            if q is None:
                return None
        return q


def jac(M, q, h=1e-7):
    J = np.zeros((2, 2))
    for j in range(2):
        e = np.zeros(2); e[j] = h
        a, b = M.P(q + e), M.P(q - e)
        if a is None or b is None:
            return None
        J[:, j] = (a - b) / (2 * h)
    return J


def fixed_point(M, xb):
    """Symmetric periodic orbit by 1-D shooting (Newton from the barrier diverges: the map expands strongly).
    Start on the reversor's fixed set (y = 0, px = 0, py > 0); f(x0) = px at the next DOWNWARD crossing; the
    Lyapunov orbit is the root nearest the barrier. Plunging starts count as px < 0 (they fall inward)."""
    def f(x0):
        py2 = M.mdl.py2_on_shell(np.array(x0), np.array(0.0), np.array(0.0))
        if not np.isfinite(py2) or py2 <= 0:
            return np.nan
        a = M._leg(np.array([x0, 0.0, 0.0, np.sqrt(py2)]), -1)
        return -1.0 if a is None else float(a[2])
    xs = xb + np.linspace(-2.0, 2.0, 201)                # fix round 1: +-0.6 missed TS2's orbit at eps = -0.03
    fs = [f(x) for x in xs]
    br = [(xs[i], xs[i + 1]) for i in range(200) if np.isfinite(fs[i]) and np.isfinite(fs[i + 1])
          and np.sign(fs[i]) != np.sign(fs[i + 1])]
    if not br:
        return None, None
    lo, hi = min(br, key=lambda b: abs(0.5 * (b[0] + b[1]) - xb))
    flo = f(lo)
    for _ in range(100):
        mid = 0.5 * (lo + hi)
        fm = f(mid)
        if np.sign(fm) == np.sign(flo):
            lo, flo = mid, fm
        else:
            hi = mid
        if hi - lo < 1e-15 * abs(mid):
            break
    q = np.array([0.5 * (lo + hi), 0.0])
    p = M.P(q)
    return q, (None if p is None else float(np.linalg.norm(p - q)))


S = lambda q: np.array([q[0], -q[1]])


def level(system, tag, eps, rtol):
    t0 = time.time()
    mdl, info = setup(system, tag, eps)
    out = dict(system=system, p=TAGS[tag], tag=tag, eps=eps, rtol=rtol, **info)
    if info["h"] is None or info["h"] <= 0:
        return dict(out, status="NO-SADDLE-ON-SHELL")
    M = Map(mdl, rtol)
    xb = (info["r_b"] - 1) / mdl.sig
    zs, closure = fixed_point(M, xb)
    if zs is None:
        return dict(out, status="NO-FIXED-POINT")
    J = jac(M, zs)
    ev, V = np.linalg.eig(J)
    k = int(np.argmax(np.abs(ev)))
    lam, vu = float(np.real(ev[k])), np.real(V[:, k])
    out.update(z_star=zs.tolist(), closure=closure, trace=float(np.trace(J)), lam=lam)
    if abs(np.trace(J)) <= 2 or closure is None or closure > 1e-10:
        return dict(out, status="LYAPUNOV-ORBIT-NOT-HYPERBOLIC-OR-NOT-CLOSED")
    # R0 reversor gate: S P S P q = q on 5 points near z*
    r0 = []
    for ang in np.linspace(0, 2 * np.pi, 5, endpoint=False):
        q = zs + 1e-3 * np.array([np.cos(ang), np.sin(ang)])
        w = M.P(q)
        w2 = None if w is None else M.P(S(w))
        r0.append(None if w2 is None else float(np.linalg.norm(S(w2) - q)))
    good = [v for v in r0 if v is not None]
    out["R0"] = {"errors": r0, "pass": bool(good) and max(good) < 1e-9}
    if not out["R0"]["pass"]:
        return dict(out, status="UNREADABLE-R0")
    hits = {}
    for sgn in (+1, -1):                                   # pocket branch = the one reaching x > x* + 0.01
        v = sgn * vu
        s = S0 * np.abs(lam) ** (np.arange(K + 1) / K)
        pts = [zs + si * v for si in s]
        for n in range(1, NMAX + 1):
            pts = [None if q is None else M.P(q) for q in pts]
            for a in range(K):
                qa, qb = pts[a], pts[a + 1]
                if qa is None or qb is None or min(qa[0], qb[0]) < zs[0] + 0.01:
                    continue
                if np.sign(qa[1]) != np.sign(qb[1]):
                    hits[sgn] = (n, s[a], s[a + 1], v)
                    break
            if sgn in hits:
                break
    pocket = [h for sg, h in hits.items()]
    if not pocket:
        return dict(out, status="NO-HOMOCLINIC-CROSSING-FOUND", n_searched=NMAX)
    n, lo, hi, v = min(pocket, key=lambda h: h[0])
    g = lambda s: M.Pn(zs + s * v, n)
    glo = g(lo)[1]
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        qm = g(mid)
        if np.sign(qm[1]) == np.sign(glo):
            lo, glo = mid, qm[1]
        else:
            hi = mid
        if abs(qm[1]) < 1e-12 or (hi - lo) < 1e-16 * mid:
            break
    sh, zh = mid, g(mid)
    th = {}
    for d in DELTAS:
        a, b = g(sh * (1 + d)), g(sh * (1 - d))
        t = (a - b) / (2 * d * sh)
        ang = 2 * np.arctan2(abs(t[0]), abs(t[1]))
        th[str(d)] = float(min(ang, np.pi - ang))
    return dict(out, status="OK", n_iter=n, s_h=sh, z_h=zh.tolist(), px_at_zh=float(zh[1]), theta=th,
                wall_s=time.time() - t0)


def _job(args):
    try:
        return level(*args)
    except Exception as e:
        import traceback
        return {"job": list(args), "status": "ERROR", "trace": traceback.format_exc()[-1500:]}


def verdicts(rows):
    out = []
    for tag in TAGS:
        for eps in EPSS:
            pick = lambda s, r: next((x for x in rows if x.get("system") == s and x.get("tag") == tag
                                      and x.get("eps") == eps and x.get("rtol") == r), {})
            ts13, ts12, k13, k12 = pick("TS2", 1e-13), pick("TS2", 1e-12), pick("Kerr", 1e-13), pick("Kerr", 1e-12)
            rec = {"p": TAGS[tag], "eps": eps, "h_TS": ts13.get("h"), "h_Kerr": k13.get("h"),
                   "status": {k: v.get("status") for k, v in (("TS13", ts13), ("TS12", ts12), ("K13", k13),
                                                             ("K12", k12))}}
            if all(v.get("status") == "OK" for v in (ts13, ts12, k13, k12)):
                tv = [ts13["theta"][str(d)] for d in DELTAS] + [ts12["theta"][str(DELTAS[1])]]
                kv = [k13["theta"][str(d)] for d in DELTAS] + [k12["theta"][str(DELTAS[1])]]
                theta = ts13["theta"][str(DELTAS[1])]
                spread = max(tv) - min(tv)
                F = max(max(kv), spread)
                ok = theta > 10 * F and spread < 0.2 * theta
                rec.update(theta=theta, err=spread, kerr_theta=max(kv), floor=F,
                           verdict=(f"transversal splitting measured, theta = {theta:.3e} +- {spread:.1e} >> Kerr "
                                    f"floor {F:.1e}") if ok else f"splitting below floor F = {F:.1e} at this "
                                    "precision")
            else:
                rec["verdict"] = "UNREADABLE (see status)"
            out.append(rec)
    return out


def main(workers):
    from multiprocessing import get_context
    jobs = [(s, t, e, r) for t in TAGS for e in EPSS for s in ("TS2", "Kerr") for r in (1e-13, 1e-12)]
    with get_context("spawn").Pool(workers, maxtasksperchild=1) as pool:
        rows = []
        for row in pool.imap_unordered(_job, jobs):
            rows.append(row)
            print(json.dumps({k: row.get(k) for k in ("system", "p", "eps", "rtol", "status", "theta", "n_iter",
                                                        "lam", "h")}, default=float), flush=True)
    v = verdicts(rows)
    res = {"prereg": "notes/separatrix_splitting_prereg.md (8feff19 + 27a7be6)", "rows": rows, "verdicts": v}
    (RESULTS / "199_splitting.json").write_text(json.dumps(res, indent=1, default=float))
    L = ["# §199 separatrix splitting at the TS δ=2 saddle-centre", "",
         "| p | ε | h (TS) | θ_TS | err | Kerr θ | floor F | verdict |", "|---|---|---|---|---|---|---|---|"]
    for r in v:
        f = lambda k: ("%.2e" % r[k]) if isinstance(r.get(k), float) else "—"
        L.append(f"| {r['p']} | {r['eps']} | {f('h_TS')} | {f('theta')} | {f('err')} | {f('kerr_theta')} | "
                 f"{f('floor')} | {r['verdict']} |")
    (RESULTS / "199_REPORT.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--one", nargs=3)
    ap.add_argument("--redo", nargs="*", help="re-run only these 'SYS TAG EPS' jobs (both rtol) into the saved JSON")
    a = ap.parse_args()
    if a.one:
        r = level(a.one[0], a.one[1], float(a.one[2]), 1e-13)
        print(json.dumps(r, indent=1, default=float))
    elif a.redo:
        d = json.load(open(RESULTS / "199_splitting.json"))
        todo = [(a.redo[i], a.redo[i + 1], float(a.redo[i + 2]), r) for i in range(0, len(a.redo), 3) for r in (1e-13, 1e-12)]
        from multiprocessing import get_context
        with get_context("spawn").Pool(a.workers, maxtasksperchild=1) as pool:
            new = list(pool.imap_unordered(_job, todo))
        key = lambda r: (r.get("system"), r.get("tag"), r.get("eps"), r.get("rtol"))
        rows = [r for r in d["rows"] if key(r) not in {key(n) for n in new}] + new
        v = verdicts(rows)
        d.update(rows=rows, verdicts=v, fix_round_1="shooting range +-0.6 -> +-2.0 for the redone jobs")
        (RESULTS / "199_splitting.json").write_text(json.dumps(d, indent=1, default=float))
        for n in new:
            print(json.dumps({k: n.get(k) for k in ("system", "p", "eps", "rtol", "status", "theta", "closure", "lam")}, default=float))
    elif a.run:
        main(a.workers)
