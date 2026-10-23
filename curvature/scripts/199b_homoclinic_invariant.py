"""§199b -- canonical splitting measures at the TS delta=2 saddle-centre (pre-registration
notes/homoclinic_invariant_prereg.md, d32968d). Reuses §199's map, Lyapunov-orbit shooting and homoclinic search
unchanged (199_separatrix_splitting.level), then computes
  Lazutkin's homoclinic invariant I = omega(xi_u, S xi_u), xi_u = W^u'(t_h) in the natural parametrisation, and
  the lobe area between h and the next W^u / W^s intersection (shoelace in canonical (x, px)).
BLIND: The Bridge replicates these; embargo tabula-199b-invariants-to-bridge is active until it seals.

  --run [--workers 4]   -> results/199b_invariants.json + 199b_REPORT.md
"""
import argparse
import json
import sys
import time
from importlib import import_module
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
m = import_module("199_separatrix_splitting")
import numpy as np                                        # noqa: E402

RESULTS = Path(__file__).resolve().parent.parent / "results"
EPSS = (-0.003, -0.01, -0.03)
NLOBE = 1600                                              # per fundamental domain; N = 800 = every other point


_SAVED = None


def _rebuild(system, tag, eps, rtol):
    """§199's SAVED level (same code and tolerances, deterministic; recomputing costs 5-10 min per level), then the
    oriented unit unstable vector v with P^n(z* + s_h v) = z_h, checked against the saved z_h."""
    global _SAVED
    if _SAVED is None:
        _SAVED = json.load(open(RESULTS / "199_splitting.json"))["rows"]
    r = next((x for x in _SAVED if x.get("system") == system and x.get("tag") == tag and x.get("eps") == eps
              and x.get("rtol") == rtol), {"status": "NOT-IN-199"})
    if r.get("status") != "OK":
        return r, None, None
    mdl, _ = m.setup(system, tag, eps)
    M = m.Map(mdl, rtol)
    zs = np.array(r["z_star"])
    ev, V = np.linalg.eig(m.jac(M, zs))
    vu = np.real(V[:, int(np.argmax(np.abs(ev)))])      # exactly as §199 (re-normalising perturbs v ~1e-16, which
                                                         # lam^n ~ 1e8 amplifies: run-1 reproduction misses ~1e-8)
    zh = np.array(r["z_h"])
    best = None
    for v in (vu, -vu):
        q = M.Pn(zs + r["s_h"] * v, r["n_iter"])
        if q is not None and (best is None or np.linalg.norm(q - zh) < best[0]):
            best = (np.linalg.norm(q - zh), v)
    if best[0] > 1e-9:                                   # the saved homoclinic point must reproduce exactly
        return dict(r, status=f"REPRODUCTION-FAILED ({best[0]:.1e})"), None, None
    return r, M, best[1]


def lazutkin(job):
    system, tag, eps, rtol = job
    t0 = time.time()
    r, M, v = _rebuild(system, tag, eps, rtol)
    out = dict(system=system, p=m.TAGS[tag], tag=tag, eps=eps, rtol=rtol, status=r.get("status"), h=r.get("h"))
    if v is None:
        return out
    zs, n, sh, lam = np.array(r["z_star"]), r["n_iter"], r["s_h"], r["lam"]
    cnorm = np.sqrt(abs(2 * v[0] * v[1]))                 # |omega(v, S v)| = |2 v_x v_p|  ->  e_u = v / cnorm
    I = {}
    for d in m.DELTAS:
        a, b = M.Pn(zs + sh * (1 + d) * v, n), M.Pn(zs + sh * (1 - d) * v, n)
        dzds = (a - b) / (2 * d * sh)
        xi = dzds / (cnorm * lam ** n)
        I[str(d)] = float(-2 * xi[0] * xi[1])
    return dict(out, I=I, lam=lam, n_iter=n, cnorm=float(cnorm), wall_s=time.time() - t0)


def _seg_x(p, q, a, b):
    d1, d2 = q - p, b - a
    den = d1[0] * d2[1] - d1[1] * d2[0]
    if abs(den) < 1e-300:
        return None
    t = ((a[0] - p[0]) * d2[1] - (a[1] - p[1]) * d2[0]) / den
    u = ((a[0] - p[0]) * d1[1] - (a[1] - p[1]) * d1[0]) / den
    return (t, u) if 0 < t < 1 and 0 < u < 1 else None


def lobe_area(U, N):
    """U: W^u points for t = t_h * lam^(j/N), j = -N..N (index N = h). Sigma = S U. h2 = first crossing of U (j > N)
    with Sigma away from h; lobe = U[N..j] + X + Sigma back to index N; shoelace area in (x, px)."""
    Sg = U * np.array([1.0, -1.0])
    for j in range(N + 2, len(U) - 1):
        for k in range(len(Sg) - 1):
            if abs(k - N) <= 2:
                continue
            hit = _seg_x(U[j], U[j + 1], Sg[k], Sg[k + 1])
            if hit:
                X = U[j] + hit[0] * (U[j + 1] - U[j])
                back = list(range(k, N - 1, -1)) if k >= N else list(range(k + 1, N + 1))
                poly = np.vstack([U[N:j + 1], X[None, :], Sg[back]])
                x, p = poly[:, 0], poly[:, 1]
                A = 0.5 * float(np.sum(x * np.roll(p, -1) - np.roll(x, -1) * p))
                return {"area": A, "j": j, "k": k, "h2": X.tolist(), "n_poly": len(poly)}
    return None


def lobe(job):
    system, tag, eps = job
    t0 = time.time()
    r, M, v = _rebuild(system, tag, eps, 1e-13)
    out = dict(system=system, p=m.TAGS[tag], tag=tag, eps=eps, status=r.get("status"), h=r.get("h"))
    if v is None:
        return out
    zs, n, sh, lam = np.array(r["z_star"]), r["n_iter"], r["s_h"], r["lam"]
    js = np.arange(-NLOBE, NLOBE + 1)
    U = [M.Pn(zs + sh * lam ** (j / NLOBE) * v, n) for j in js]
    miss = sum(u is None for u in U)
    if miss:
        return dict(out, status="LOBE-PLUNGE", n_missing=miss)
    U = np.array(U)
    res = {}
    for N in (NLOBE, NLOBE // 2):
        sub = U[::NLOBE // N]
        res[str(N)] = lobe_area(sub, N) or {"area": None, "why": "NO-SECOND-INTERSECTION"}
    return dict(out, lobe=res, wall_s=time.time() - t0)


def _job(spec):
    try:
        return lazutkin(spec[1]) if spec[0] == "I" else lobe(spec[1])
    except Exception:
        import traceback
        return {"job": list(spec), "status": "ERROR", "trace": traceback.format_exc()[-1500:]}


def verdict(ts_vals, kerr_vals):
    ts = [abs(x) for x in ts_vals if x is not None]
    kr = [abs(x) for x in kerr_vals if x is not None]
    if ts_vals[0] is None or not ts or not kr:            # no headline value -> UNREADABLE, never a crash
        return None, "UNREADABLE"
    val, spread = abs(ts_vals[0]), max(ts) - min(ts)
    F = max(max(kr), spread)
    ok = val > 10 * F and spread < 0.2 * val
    return {"value": ts_vals[0], "spread": spread, "kerr": max(kr), "floor": F}, (
        "canonical splitting measured" if ok else f"below floor F = {F:.1e} at this precision")


def main(workers):
    from multiprocessing import get_context
    specs = [("L", (s, "t1o2", e)) for e in EPSS for s in ("TS2", "Kerr")]          # longest first
    specs += [("I", (s, t, e, r)) for t in m.TAGS for e in EPSS for s in ("TS2", "Kerr") for r in (1e-13, 1e-12)]
    rows = []
    with get_context("spawn").Pool(workers, maxtasksperchild=1) as pool:
        for row in pool.imap_unordered(_job, specs):
            rows.append(row)
            print(json.dumps({k: row.get(k) for k in ("system", "p", "eps", "rtol", "status", "wall_s")}), flush=True)
    get = lambda s, t, e, r=None, kind="I": next((x for x in rows if x.get("system") == s and x.get("tag") == t
                                                  and x.get("eps") == e and (kind == "L" or x.get("rtol") == r)
                                                  and (("I" in x) if kind == "I" else ("lobe" in x or "I" not in x))),
                                                 {})
    table = []
    for t in m.TAGS:
        for e in EPSS:
            ts13, ts12, k13, k12 = (get(s, t, e, r) for s, r in (("TS2", 1e-13), ("TS2", 1e-12), ("Kerr", 1e-13),
                                                                  ("Kerr", 1e-12)))
            tsv = [ts13.get("I", {}).get(str(d)) for d in m.DELTAS] + [ts12.get("I", {}).get(str(m.DELTAS[1]))]
            tsv = [tsv[1], tsv[0], tsv[2]]                  # headline = rtol 1e-13, delta 1e-5 (as §199)
            kv = [k13.get("I", {}).get(str(d)) for d in m.DELTAS] + [k12.get("I", {}).get(str(m.DELTAS[1]))]
            rI, vI = verdict(tsv, kv)
            rec = {"p": m.TAGS[t], "eps": e, "h": ts13.get("h"), "I": rI, "I_verdict": vI}
            if t == "t1o2":
                lt, lk = get("TS2", t, e, kind="L"), get("Kerr", t, e, kind="L")
                av = [(lt.get("lobe") or {}).get(str(N), {}).get("area") for N in (NLOBE, NLOBE // 2)]
                ak = [(lk.get("lobe") or {}).get(str(N), {}).get("area") for N in (NLOBE, NLOBE // 2)]
                rA, vA = verdict(av, ak)
                rec.update(A=rA, A_verdict=vA, lobe_status=(lt.get("status"), lk.get("status")))
            table.append(rec)
    res = {"prereg": "notes/homoclinic_invariant_prereg.md (d32968d)", "rows": rows, "table": table}
    (RESULTS / "199b_invariants.json").write_text(json.dumps(res, indent=1, default=float))
    f = lambda d, k: ("%.3e" % d[k]) if d and isinstance(d.get(k), float) else "—"
    L = ["# §199b canonical splitting measures (BLIND to The Bridge until it seals)", "",
         "| p | ε | h | Lazutkin I | spread | Kerr | verdict | lobe area A | spread | Kerr | verdict |",
         "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in table:
        L.append(f"| {r['p']} | {r['eps']} | {f(r, 'h')} | {f(r['I'], 'value')} | {f(r['I'], 'spread')} | "
                 f"{f(r['I'], 'kerr')} | {r['I_verdict']} | {f(r.get('A'), 'value')} | {f(r.get('A'), 'spread')} | "
                 f"{f(r.get('A'), 'kerr')} | {r.get('A_verdict', '—')} |")
    (RESULTS / "199b_REPORT.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--test-lobe", nargs=3)
    a = ap.parse_args()
    if a.test_lobe:
        NLOBE = 100
        print(json.dumps(lobe((a.test_lobe[0], a.test_lobe[1], float(a.test_lobe[2]))), default=float)[:600])
    elif a.run:
        main(a.workers)
