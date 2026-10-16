"""Step 197 -- K20: tabula's independent screen of the Manko-Novikov chaotic sea (pre-registration
notes/k20_mn_screen_prereg.md, 9aca9a4 + amendment A1 3880145).

This file is built in stages, each gated before the next:
  --gq        gate G-q (geometry only, no orbits): our allowed-region code reproduces the published P0 thresholds
              (CLA 2011 / GLM 2008). A flipped or misscaled beta fails it.
  --geometry  per point: the domain-D margins (quantum's rules, A1.3) and the level classification (prereg §2).

Metric: the Gair-Li-Mandel MN subclass, transcribed independently as in script 144 (validated there: asymptotic
flatness, Kerr limit). Reduced Hamiltonian (quantum §3.2), with p_t = -E and p_phi = Lz:
  H = (1/2) pref [(x^2-1) px^2 + (1-y^2) py^2] + (1/2)[f (Lz - w E)^2 / rho^2 - E^2 / f] = -1/2,
  pref = (1-alpha^2)^2 e^{2psi} / (k^2 B G),  rho^2 = k^2 (x^2-1)(1-y^2).
A point is ALLOWED iff the kinetic part K = -1/2 - V >= 0. This is valid in the ergoregion too, since pref > 0 always,
unlike the LGAC V_eff <= 0 form, which flips sign where f < 0.

    .venv314ob/bin/python scripts/197_k20_mn_screen.py --gq
"""

import argparse
import json
from fractions import Fraction as Fr
from pathlib import Path

import numpy as np

RESULTS = Path(__file__).resolve().parent.parent / "results"
np.seterr(all="ignore")

# The points (prereg §0 + A1.1), scale-free: M = 1, a = chi. Exact rationals kept for the record.
POINTS = {
    "p1":   {"M": 5,  "a": 3,  "beta": Fr(1, 5)},
    "p2":   {"M": 13, "a": 5,  "beta": Fr(-1, 3)},
    "F5R":  {"M": 89, "a": 80, "q": Fr(19, 20)},
    "P0":   {"chi": 0.9, "q": 0.95},                    # the published point: instrument control only
}


def point_params(name, kerr=False):
    """(chi, alpha, k, beta) at M = 1. kerr=True gives q = 0 at the same chi (the matched null)."""
    p = POINTS[name]
    if "chi" in p:
        chi, q = p["chi"], p["q"]
    else:
        chi = p["a"] / p["M"]
        kk = np.sqrt(1 - chi ** 2)
        q = float(p["q"]) if "q" in p else float(p["beta"]) * kk ** 3   # beta = q M^3/k^3, M = 1
    alpha = (-1 + np.sqrt(1 - chi ** 2)) / chi
    k = (1 - alpha ** 2) / (1 + alpha ** 2)
    beta = 0.0 if kerr else q / k ** 3
    return chi, alpha, k, beta


def _legendre(mu):
    return np.ones_like(mu), mu, 0.5 * (3 * mu ** 2 - 1), 0.5 * (5 * mu ** 3 - 3 * mu)


def metric_parts(x, y, alpha, k, beta):
    """f, w, B, A, G (gamma deformation), e^{2psi}, R^2 -- numpy, vectorised (script 144's formulas)."""
    R2 = x ** 2 + y ** 2 - 1
    R = np.sqrt(R2)
    mu = x * y / R
    P0, P1, P2, P3 = _legendre(mu)
    Pl, Rm = (P0, P1, P2), (1 / R, 1 / R ** 2, 1 / R ** 3)
    psi = beta * P2 / R ** 3
    S_a = sum((x - y) * Pl[l] * Rm[l] for l in range(3))
    S_b = sum(((-1) ** (3 - l)) * (x + y) * Pl[l] * Rm[l] for l in range(3))
    a = -alpha * np.exp(-2 * beta * (-1 + S_a))
    b = alpha * np.exp(2 * beta * (1 + S_b))
    S_g = sum((x - y + ((-1) ** (2 - l)) * (x + y)) * Pl[l] * Rm[l] for l in range(3))
    G = np.exp(3 * beta ** 2 * R ** (-6) * (P3 ** 2 - P2 ** 2) + 2 * beta * (S_g - 2))
    ab = a * b
    A = (x ** 2 - 1) * (1 + ab) ** 2 - (1 - y ** 2) * (b - a) ** 2
    B = (x + 1 + (x - 1) * ab) ** 2 + ((1 + y) * a + (1 - y) * b) ** 2
    C = (x ** 2 - 1) * (1 + ab) * (b - a - y * (a + b)) + (1 - y ** 2) * (b - a) * (1 + ab + x * (1 - ab))
    e2psi = np.exp(2 * psi)
    f = e2psi * A / B
    w = 2 * k * np.exp(-2 * psi) * C / A - 4 * k * alpha / (1 - alpha ** 2)
    return {"f": f, "w": w, "A": A, "B": B, "G": G, "e2psi": e2psi, "R2": R2}


def kinetic(x, y, E, Lz, alpha, k, beta):
    """K = -1/2 - V(x, y); allowed iff K >= 0."""
    m = metric_parts(x, y, alpha, k, beta)
    rho2 = k ** 2 * (x ** 2 - 1) * (1 - y ** 2)
    V = 0.5 * (m["f"] * (Lz - m["w"] * E) ** 2 / rho2 - E ** 2 / m["f"])
    return -0.5 - V


def gphiphi(x, y, alpha, k, beta):
    m = metric_parts(x, y, alpha, k, beta)
    rho2 = k ** 2 * (x ** 2 - 1) * (1 - y ** 2)
    return -m["f"] * m["w"] ** 2 + rho2 / m["f"]


def rho_of_x(x, k):
    return k * np.sqrt(x ** 2 - 1)                   # Weyl rho on the equator y = 0


# ---------------------------------------------------------------- gate G-q (geometry only)

XG = 1 + np.logspace(-6, np.log10(60.0), 400000)     # equatorial line, dense near x = 1


def equatorial_intervals(E, Lz, pp):
    """Allowed intervals on y = 0, in rho, together with K on the line."""
    _, alpha, k, beta = pp
    K = kinetic(XG, 0 * XG, E, Lz, alpha, k, beta)
    ok = np.isfinite(K) & (K >= 0)
    edges = np.flatnonzero(np.diff(ok.astype(int)))
    iv, start = [], (0 if ok[0] else None)
    for e in edges:
        if ok[e + 1]:
            start = e + 1
        else:
            iv.append((start, e)); start = None
    if start is not None:
        iv.append((start, len(XG) - 1))
    return [(float(rho_of_x(XG[i], k)), float(rho_of_x(XG[j], k)), int(i), int(j)) for i, j in iv], K


def bound_pair(E, Lz, pp):
    """(inner, outer) bound intervals, excluding one that touches the line's inner end (plunge) or outer end (escape)."""
    iv, K = equatorial_intervals(E, Lz, pp)
    bound = [v for v in iv if v[2] > 0 and v[3] < len(XG) - 1]
    return bound, K


def _bisect(fn, lo, hi, n=60):
    flo = fn(lo)
    for _ in range(n):
        mid = 0.5 * (lo + hi)
        if (fn(mid) > 0) == (flo > 0):
            lo, flo = mid, fn(mid)
        else:
            hi = mid
    return 0.5 * (lo + hi)


def gate_gq():
    pp = point_params("P0")
    out = {"P0_params": dict(zip(("chi", "alpha", "k", "beta"), map(float, pp)))}
    bnd, _ = bound_pair(0.95, 3.0, pp)
    out["extents_E095_L3_rho"] = [(round(a, 4), round(b, 4)) for a, b, *_ in bnd]
    gapmax = lambda E, L: (lambda b, K: K[b[0][3] + 1:b[1][2]].max() if len(b) == 2 else 1.0)(*bound_pair(E, L, pp))
    outer_max = lambda E, L: (lambda b, K: K[b[-1][2]:b[-1][3] + 1].max() if len(b) == 2 else -1.0)(*bound_pair(E, L, pp))
    out["join_Lz_at_E095"] = _bisect(lambda L: gapmax(0.95, L), 2.9, 3.1)          # gap closes: K_gap_max = 0
    out["join_E_at_L3"] = _bisect(lambda E: gapmax(E, 3.0), 0.945, 0.96)
    out["outer_vanish_Lz_at_E095"] = _bisect(lambda L: outer_max(0.95, L), 3.2, 3.6)
    out["outer_vanish_E_at_L3"] = _bisect(lambda E: outer_max(E, 3.0), 0.925, 0.945)
    pub = {"join_Lz_at_E095": 2.99761912, "join_E_at_L3": 0.95038, "outer_vanish_Lz_at_E095": 3.40935,
           "outer_vanish_E_at_L3": 0.93210}
    out["published"] = pub
    out["dev"] = {kk: abs(out[kk] - v) for kk, v in pub.items()}
    ext_pub = [(0.72, 2.12), (2.39, 13.6)]
    # A1.2: +-0.05 on each published extent. Fix round 1: each published region is matched to its nearest bound
    # interval. Run 1 demanded exactly two intervals and failed on a third, CTC-adjacent one (reported, not hidden).
    near = [min(bnd, key=lambda v: abs(v[0] - pa) + abs(v[1] - pb)) for pa, pb in ext_pub] if bnd else []
    ext_ok = len(near) == 2 and all(abs(v[0] - pa) <= 0.05 and abs(v[1] - pb) <= 0.05
                                    for v, (pa, pb) in zip(near, ext_pub))
    out["unmatched_bound_intervals_rho"] = [(round(v[0], 4), round(v[1], 4)) for v in bnd if v not in near]
    out["extents_pass"] = bool(ext_ok)
    out["thresholds_pass"] = bool(all(d <= 1e-3 for d in out["dev"].values()))
    # diagnostic only: the same with beta's sign flipped must NOT pass (shows the gate can fail)
    chi, alpha, k, beta = pp
    flip = (chi, alpha, k, -beta)
    bf, _ = bound_pair(0.95, 3.0, flip)
    out["diag_flipped_beta_extents"] = [(round(a, 4), round(b, 4)) for a, b, *_ in bf]
    out["G_q_PASS"] = out["extents_pass"] and out["thresholds_pass"]
    (RESULTS / "197_gate_gq.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))
    return out


# ---------------------------------------------------------------- C kernel (k20_kernel/integ.c; amendments A2/A3)

import ctypes as ct

KDIR = Path(__file__).resolve().parent / "k20_kernel"
RCOLS = 14
_dp = ct.POINTER(ct.c_double)


class Dom(ct.Structure):
    _fields_ = [("mask", ct.POINTER(ct.c_ubyte)), ("nx", ct.c_int), ("ny", ct.c_int), ("x0", ct.c_double),
                ("y0", ct.c_double), ("h", ct.c_double), ("xctc", _dp), ("nyt", ct.c_int), ("yt0", ct.c_double),
                ("yth", ct.c_double), ("dx_global", ct.c_double), ("xesc", ct.c_double)]


def _lib():
    lib = ct.CDLL(str(KDIR / "libk20.dylib"))
    lib.trace.argtypes = [_dp, _dp, ct.c_int, ct.c_int, ct.c_double, ct.c_long, ct.c_int, ct.c_int,
                          ct.POINTER(Dom), _dp, _dp]
    lib.trace.restype = ct.c_int
    lib.mn_eval.argtypes = [_dp, _dp, _dp]
    return lib


MASK_H, MASK_X1, BOX = 5e-4, 3.0, 0.025


def build_domain(pp, xesc=500.0):
    """B9 dilated CTC mask (A3), P-rule x_CTC(y) table (bisection-refined) and the B6 global dx. Geometry only."""
    from scipy import ndimage
    _, alpha, k, beta = pp
    xs = 1.0 + MASK_H * (np.arange(int((MASK_X1 - 1) / MASK_H)) + 0.5)
    ys = -1.0 + MASK_H * (np.arange(int(2 / MASK_H)) + 0.5)
    bad = np.zeros((len(xs), len(ys)), bool)
    for i0 in range(0, len(xs), 200):
        X, Y = np.meshgrid(xs[i0:i0 + 200], ys, indexing="ij")
        g = gphiphi(X, Y, alpha, k, beta)
        bad[i0:i0 + 200] = ~np.isfinite(g) | (g <= 0)
    r = int(np.ceil(BOX / MASK_H)) + 1                   # +1 cell: the strict side (A3)
    dil = ndimage.maximum_filter(bad.astype(np.uint8), size=2 * r + 1, mode="constant", cval=0)
    # P rule: outer x-extent of the CTC region at each y, refined by bisection on g_phiphi = 0
    yt = np.linspace(-0.99999, 0.99999, 4001)
    xctc = np.full(len(yt), -1.0)
    has = bad.any(0)
    for jj, yv in enumerate(yt):
        j = min(int((yv + 1) / MASK_H), len(ys) - 1)
        if not has[j]:
            continue
        i = np.flatnonzero(bad[:, j]).max()
        lo, hi = xs[i], xs[i] + MASK_H
        gf = lambda xv: gphiphi(np.array(xv), np.array(yv), alpha, k, beta)
        if not (gf(hi) > 0):
            xctc[jj] = hi
            continue
        for _ in range(50):
            mid = 0.5 * (lo + hi)
            if gf(mid) > 0:
                hi = mid
            else:
                lo = mid
        xctc[jj] = hi
    xg = xctc.max()
    dxg = float(np.ceil(((xg - 1) + 0.025) / 0.05 - 1e-12) * 0.05) if xg > 0 else 0.05
    keep = {"mask": np.ascontiguousarray(dil, np.uint8), "xctc": np.ascontiguousarray(xctc), "xs": xs, "ys": ys,
            "x_ctc_global": float(xg), "dx_global_B6": dxg}
    d = Dom(keep["mask"].ctypes.data_as(ct.POINTER(ct.c_ubyte)), len(xs), len(ys), 1.0, -1.0, MASK_H,
            keep["xctc"].ctypes.data_as(_dp), len(yt), float(yt[0]), float(yt[1] - yt[0]), dxg, xesc)
    keep["dom"] = d                                     # the arrays must outlive the struct
    return keep


def eval_point(lib, par, z):
    out = np.zeros(26)
    p, zz = np.ascontiguousarray(par, float), np.ascontiguousarray(z, float)
    lib.mn_eval(p.ctypes.data_as(_dp), zz.ctypes.data_as(_dp), out.ctypes.data_as(_dp))
    return out


def launch(pp, E, Lz, x, px):
    """Section point (x, px) on y = 0 -> full state with p_y > 0 from H = -1/2; None if not allowed."""
    _, alpha, k, beta = pp
    m = metric_parts(np.array(x), np.array(0.0), alpha, k, beta)
    pref = (1 - alpha ** 2) ** 2 * m["e2psi"] / (k ** 2 * m["B"] * m["G"])
    K = kinetic(np.array(x), np.array(0.0), E, Lz, alpha, k, beta)
    rem = 2 * K - pref * (x ** 2 - 1) * px ** 2              # = pref (1 - 0) p_y^2
    if not (np.isfinite(rem) and rem > 0):
        return None
    return np.array([x, 0.0, px, float(np.sqrt(rem / pref))])


def trace(lib, dom, pp, E, Lz, z0, dt, n_ret, mode=0, nv=1, w0=None, max_steps=10 ** 9, renorm=100, seed=0):
    _, alpha, k, beta = pp
    par = np.array([alpha, k, beta, E, Lz], float)
    st = np.zeros(5 + 4 * nv)
    st[:4] = z0
    if nv:
        W = np.asarray(w0, float).reshape(nv, 4) if w0 is not None else np.random.default_rng(seed).standard_normal((nv, 4))
        if w0 is None:
            W /= np.linalg.norm(W, axis=1, keepdims=True)
        st[5:] = W.ravel()
    rec, orb = np.zeros(n_ret * RCOLS), np.zeros(12)
    nc = lib.trace(par.ctypes.data_as(_dp), st.ctypes.data_as(_dp), nv, mode, dt, max_steps, n_ret, renorm,
                   ct.byref(dom["dom"]), rec.ctypes.data_as(_dp), orb.ctypes.data_as(_dp))
    return rec.reshape(n_ret, RCOLS)[:nc], orb, st


# ---------------------------------------------------------------- levels, launches, pilot (prereg §3, A4)

N_RET, N_SEC = 2000, 500
DRIFT_TARGET, ACCEPT = 1e-10, 1e-9


def component_interval(pp, E, Lz, which):
    """Equatorial x-interval of a bound component: which = 'inner' | 'outer' | index into the bound list."""
    bnd, _ = bound_pair(E, Lz, pp)
    _, _, k, _ = pp
    if not bnd:
        return None
    if which == "outer":
        v = bnd[-1]
    elif which == "inner":
        v = bnd[-2] if len(bnd) >= 2 else None
        if v is None:
            return None
    else:
        v = bnd[which]
    return float(XG[v[2]]), float(XG[v[3]])


def section_box(pp, E, Lz, xa, xb):
    """Geometry-only box (prereg §10): x in [xa, xb], |p_x| <= sqrt(max over x of 2K / (pref (x^2 - 1)))."""
    _, alpha, k, beta = pp
    xx = np.linspace(xa, xb, 4001)
    m = metric_parts(xx, 0 * xx, alpha, k, beta)
    pref = (1 - alpha ** 2) ** 2 * m["e2psi"] / (k ** 2 * m["B"] * m["G"])
    K = kinetic(xx, 0 * xx, E, Lz, alpha, k, beta)
    pm = float(np.sqrt(np.nanmax(np.clip(2 * K / (pref * (xx ** 2 - 1)), 0, None))))
    return {"xa": xa, "xb": xb, "pm": pm}


def sample_launch(pp, E, Lz, box, n, seed):
    rng = np.random.default_rng(seed)
    out = []
    while len(out) < n:
        x = rng.uniform(box["xa"], box["xb"]); p = rng.uniform(-box["pm"], box["pm"])
        z = launch(pp, E, Lz, x, p)
        if z is not None:
            out.append(z)
    return np.array(out)


def norm_sec(box, x, px):
    return (np.asarray(x) - box["xa"]) / (box["xb"] - box["xa"]), (np.asarray(px) + box["pm"]) / (2 * box["pm"])


def pilot_judge(drifts, target=DRIFT_TARGET):
    d = np.asarray(drifts, float)
    if not np.isfinite(d).any():
        return "REFUSE"
    return "PASS" if float(np.nanmax(d)) <= target else "FAIL"


def pilot(lib, dom, pp, E, Lz, launches, n_ret=N_RET, log=print):
    idx = np.unique(np.round(np.linspace(0, len(launches) - 1, 12)).astype(int))
    order = np.argsort(launches[:, 0])
    sel = launches[order[idx]]
    tol, tried = 1e-9, []                                 # A5: Dormand-Prince tolerance ladder, not a dt ladder
    while True:
        dr = []
        for z in sel:
            rec, orb, _ = trace(lib, dom, pp, E, Lz, z, tol, n_ret, nv=0)
            dr.append(orb[6] if orb[1] > 0 else np.nan)   # A4.2: drift over the whole life up to the reading (fate)
        res = pilot_judge(dr)
        tried.append({"tol": tol, "result": res, "max_drift": float(np.nanmax(dr)) if np.isfinite(dr).any() else None})
        log(f"  pilot tol={tol:.0e}: {res} {tried[-1]['max_drift']}")
        if res == "REFUSE":
            raise RuntimeError(f"pilot REFUSED at tol={tol}: no pilot orbit measured")
        if res == "PASS" or tol < 1e-12:
            return tol, {"floor_hit": res != "PASS", "tried": tried}
        tol /= 10


# ---------------------------------------------------------------- section map, UPOs (A4)

def section_map(lib, dom, pp, E, Lz, x, px, n, dt):
    """P^n(x, px) and DP^n (2x2) via two exact tangents started on the section; None if the orbit dies."""
    z0 = launch(pp, E, Lz, x, px)
    if z0 is None:
        return None
    _, alpha, k, beta = pp
    o = eval_point(lib, [alpha, k, beta, E, Lz], z0)
    xd, yd, pxd = o[0], o[1], o[2]
    W = np.array([[1.0, 0.0, 0.0, pxd / yd], [0.0, 0.0, 1.0, -xd / yd]])
    rec, orb, st = trace(lib, dom, pp, E, Lz, z0, dt, n, mode=1, nv=2, w0=W, renorm=0)
    if int(orb[0]) < n:
        return None
    w = st[5:].reshape(2, 4)
    DP = np.array([[w[0, 0], w[1, 0]], [w[0, 2], w[1, 2]]])
    return np.array([st[0], st[2]]), DP, rec


def find_upos(lib, dom, pp, E, Lz, box, dt, periods=(1, 2, 3), grid=20, log=print):
    found = []
    sx, sp_ = box["xb"] - box["xa"], 2 * box["pm"]
    for n in periods:
        for xs_ in np.linspace(box["xa"], box["xb"], grid + 2)[1:-1]:
            for ps_ in np.linspace(-box["pm"], box["pm"], grid + 2)[1:-1]:
                z = np.array([xs_, ps_])
                ok = False
                for _ in range(30):
                    r = section_map(lib, dom, pp, E, Lz, z[0], z[1], n, dt)
                    if r is None:
                        break
                    Pz, DP, _ = r
                    F = Pz - z
                    if np.hypot(F[0] / sx, F[1] / sp_) < 1e-10:
                        ok = True
                        break
                    try:
                        z = z - np.linalg.solve(DP - np.eye(2), F)
                    except np.linalg.LinAlgError:
                        break
                    if not (box["xa"] <= z[0] <= box["xb"] and abs(z[1]) <= box["pm"]):
                        break
                if not ok:
                    continue
                if any(f["n"] == n and np.hypot((f["z"][0] - z[0]) / sx, (f["z"][1] - z[1]) / sp_) < 1e-6
                       for f in found):
                    continue
                ev, evec = np.linalg.eig(DP)
                # the orbit's period-n points on the section
                pts, zz = [z.copy()], z.copy()
                for _ in range(n - 1):
                    rr = section_map(lib, dom, pp, E, Lz, zz[0], zz[1], 1, dt)
                    zz = rr[0]; pts.append(zz.copy())
                minimal = all(np.hypot((p[0] - z[0]) / sx, (p[1] - z[1]) / sp_) > 1e-6 for p in pts[1:])
                if not minimal:
                    continue                              # a lower-period orbit counted again
                if any(f["n"] == n and min(np.hypot((q[0] - z[0]) / sx, (q[1] - z[1]) / sp_) for q in f["pts"]) < 1e-6
                       for f in found):
                    continue
                found.append({"n": n, "z": z.tolist(), "pts": [p.tolist() for p in pts], "trace": float(np.trace(DP)),
                              "det": float(np.linalg.det(DP)), "eig": [complex(e) for e in ev],
                              "evec": evec.tolist(), "hyperbolic": bool(abs(np.trace(DP)) > 2)})
        log(f"  period {n}: {sum(1 for f in found if f['n'] == n)} orbits "
            f"({sum(1 for f in found if f['n'] == n and f['hyperbolic'])} hyperbolic)")
    return found


# ---------------------------------------------------------------- indicators (prereg §4)

D2_WINDOWS = {"A": (0.01, 0.05), "B": (0.02, 0.10)}


def ftle_pair(rec, N):
    if len(rec) < N:
        return None
    n1 = N // 4
    l2 = rec[N - 1, 5] / rec[N - 1, 0]
    l1 = rec[n1 - 1, 5] / rec[n1 - 1, 0]
    return float(l2), float(l2 / l1) if l1 != 0 else float("nan")


def corr_dim(box, rec, N):
    from scipy.spatial.distance import pdist
    if len(rec) < N:
        return None
    u, v = norm_sec(box, rec[:N, 2], rec[:N, 3])
    d = pdist(np.column_stack([u, v]))
    out = {}
    for key, (lo, hi) in D2_WINDOWS.items():
        rs = np.logspace(np.log10(lo), np.log10(hi), 9)
        C = np.array([np.count_nonzero(d < r) for r in rs], float)
        if C[0] < 200:
            out[key] = None                               # a window with < 200 pairs is "mixed", never zero
            continue
        out[key] = float(np.polyfit(np.log(rs), np.log(C), 1)[0])
    return out


def d_min(box, rec, N, upos):
    hyp = [p for u in upos if u["hyperbolic"] for p in u["pts"]]
    if not hyp or len(rec) == 0:
        return float("inf")
    u, v = norm_sec(box, rec[:N, 2], rec[:N, 3])
    H = np.array([norm_sec(box, p[0], p[1]) for p in hyp])
    return float(np.min(np.hypot(u[:, None] - H[None, :, 0], v[:, None] - H[None, :, 1])))


DBINS = (0.0, 1e-3, 1e-2, 1e-1, np.inf)


def dbin(dm):
    for i in range(4):
        if DBINS[i] <= dm < DBINS[i + 1]:
            return i
    return 3


def stats_for(rec, box, N, upos):
    f = ftle_pair(rec, N)
    c = corr_dim(box, rec, N)
    return {"N": N, "lam2": f[0] if f else None, "rho": f[1] if f else None,
            "D2A": c["A"] if c else None, "D2B": c["B"] if c else None, "dmin": d_min(box, rec, N, upos)}


def verdict(st, thr):
    """CHAOTIC iff I1 high AND I2 high; REGULAR iff both low; else INDETERMINATE (prereg §4)."""
    if st["lam2"] is None:
        return "ESCAPE"
    t = thr[dbin(st["dmin"])]
    if t is None:
        return "CANNOT-DISCRIMINATE"
    i1h = st["lam2"] > t["lam2"][1] and st["rho"] > t["rho"][1]
    i1l = st["lam2"] < t["lam2"][0] and st["rho"] < t["rho"][0]
    if st["D2A"] is None or st["D2B"] is None:
        i2h = i2l = False
    else:
        i2h = st["D2A"] > t["D2A"][1] and st["D2B"] > t["D2B"][1]
        i2l = st["D2A"] < t["D2A"][0] and st["D2B"] < t["D2B"][0]
    if i1h and i2h:
        return "CHAOTIC"
    if i1l and i2l:
        return "REGULAR"
    return "INDETERMINATE"


def thresholds(train_stats):
    """Per d_min bin: (p95, p99) of each statistic over the TRAINING null; thin bins (< 60) merge with a neighbour."""
    by = {i: [s_ for s_ in train_stats if s_["lam2"] is not None and dbin(s_["dmin"]) == i] for i in range(4)}
    out = {}
    for i in range(4):
        pool = list(by[i])
        if len(pool) < 60:
            for j in (i - 1, i + 1):
                if 0 <= j < 4:
                    pool += by[j]
        if len(pool) < 60:
            out[i] = None
            continue
        q = lambda key: [float(np.percentile([s_[key] for s_ in pool if s_[key] is not None], p)) for p in (95, 99)]
        out[i] = {"n": len(pool), "lam2": q("lam2"), "rho": q("rho"), "D2A": q("D2A"), "D2B": q("D2B")}
    return out


# ---------------------------------------------------------------- worker pool

_W = {}


def _worker_init():
    import os
    for v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
        os.environ.setdefault(v, "1")


def _job(args):
    """args: (tag, point, kerr, E, Lz, z0, dt, n_ret, seed) -> (tag, rec, orb)."""
    tag, point, kerr, E, Lz, z0, dt, n_ret, seed = args
    key = (point, kerr)
    if key not in _W:
        pp = point_params(point, kerr=kerr)
        _W[key] = (_lib(), build_domain(pp), pp)
    lib, dom, pp = _W[key]
    rec, orb, _ = trace(lib, dom, pp, E, Lz, np.asarray(z0), dt, n_ret, nv=1, seed=seed)
    return tag, rec, orb


def run_pool(jobs, workers=4):
    from multiprocessing import get_context
    with get_context("spawn").Pool(workers, initializer=_worker_init) as pool:
        return list(pool.imap(_job, jobs, chunksize=1))


# ---------------------------------------------------------------- C2: the pilot self-test

def selftest_pilot():
    good = np.full(12, 1e-12)
    inj = good.copy(); inj[5] = 5e-9
    checks = [("injected 5e-9 orbit FAILS", pilot_judge(inj) == "FAIL"),
              ("clean set PASSES", pilot_judge(good) == "PASS"),
              ("all-NaN REFUSES (never read as 0)", pilot_judge(np.full(12, np.nan)) == "REFUSE"),
              ("partial NaN + excess FAILS", pilot_judge([np.nan, np.nan, 5e-9, 1e-12]) == "FAIL")]
    lib = _lib()
    pp = point_params("P0")
    dom = build_domain(pp)
    xa, xb = component_interval(pp, 0.95, 3.0, "inner")
    box = section_box(pp, 0.95, 3.0, xa, xb)
    L = sample_launch(pp, 0.95, 3.0, box, 200, seed=97001)       # a seed reserved for the self-test only
    idx = np.unique(np.round(np.linspace(0, len(L) - 1, 12)).astype(int))
    sel = L[np.argsort(L[:, 0])[idx]]
    real = {}
    for dt in (1e-5, 1e-4, 1e-3, 1e-2):                         # A5: the coarsest tolerances, until one FAILS
        dr = []
        for z in sel:
            rec, orb, _ = trace(lib, dom, pp, 0.95, 3.0, z, dt, N_RET, nv=0)
            dr.append(orb[6] if orb[1] > 0 else np.nan)
        real[dt] = (pilot_judge(dr), float(np.nanmax(dr)) if np.isfinite(dr).any() else None)
        print(f"  REAL P0 inner, tol {dt}: {real[dt]}", flush=True)
        if real[dt][0] == "FAIL":
            break
    checks.append((f"REAL: P0 inner region at tol {dt} FAILS end to end", real[dt][0] == "FAIL"))
    ok = all(c for _, c in checks)
    for n_, c in checks:
        print(("PASS  " if c else "FAIL  ") + n_, flush=True)
    out = {"checks": {n_: bool(c) for n_, c in checks}, "real": {str(k_): v for k_, v in real.items()}, "ALL_PASS": ok}
    (RESULTS / "197_pilot_selftest.json").write_text(json.dumps(out, indent=1))
    if not ok:
        raise SystemExit("C2 pilot self-test FAILED")
    return out


# ---------------------------------------------------------------- C-gates (prereg §8, A4, A7)

def e_barrier(pp, Lz, lo=0.80, hi=0.9999):
    """Kerr: the energy at which the equatorial bound interval merges with the plunge interval (bisection)."""
    def separate(E):
        iv, _ = equatorial_intervals(E, Lz, pp)
        plunge = [v for v in iv if v[2] == 0]
        bound = [v for v in iv if v[2] > 0 and v[3] < len(XG) - 1]
        return bool(bound) and bool(plunge)
    Es = np.linspace(lo, hi, 400)                     # bracket the LAST separate -> merged transition by scanning
    sep = [separate(E) for E in Es]
    idx = [i for i in range(len(Es) - 1) if sep[i] and not sep[i + 1]]
    if not idx:
        return None
    lo, hi = Es[idx[-1]], Es[idx[-1] + 1]
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if separate(mid):
            lo = mid
        else:
            hi = mid
    return lo


def run_level(lib, dom, point, kerr, E, Lz, region, n, seed, target, workers, log):
    """Launch n orbits in one bound component, pilot the tolerance, find UPOs, run the orbits. Returns a dict."""
    pp = point_params(point, kerr=kerr)
    iv = component_interval(pp, E, Lz, region)
    if iv is None:
        return None
    box = section_box(pp, E, Lz, *iv)
    L = sample_launch(pp, E, Lz, box, n, seed)
    tol, pinfo = pilot_target(lib, dom, pp, E, Lz, L, target, log)
    t0 = __import__("time").time()
    upos = find_upos(lib, dom, pp, E, Lz, box, tol, log=log)
    log(f"  UPOs {len(upos)} in {__import__('time').time() - t0:.0f}s")
    jobs = [((point, kerr, E, Lz, region, i), point, kerr, E, Lz, L[i].tolist(), tol, N_RET, seed * 1000 + i)
            for i in range(n)]
    res = run_pool(jobs, workers)
    recs = [r for _, r, _ in res]
    orbs = [o for _, _, o in res]
    return {"point": point, "kerr": kerr, "E": E, "Lz": Lz, "region": region, "box": box, "launch": L.tolist(),
            "tol": tol, "pilot": pinfo, "upos": upos, "recs": recs, "orbs": orbs}


def pilot_target(lib, dom, pp, E, Lz, launches, target, log):
    idx = np.unique(np.round(np.linspace(0, len(launches) - 1, 12)).astype(int))
    sel = launches[np.argsort(launches[:, 0])[idx]]
    tol, tried = 1e-9, []
    while True:
        dr = []
        for z in sel:
            rec, orb, _ = trace(lib, dom, pp, E, Lz, z, tol, N_RET, nv=0)
            dr.append(orb[6] if orb[1] > 0 else np.nan)
        res = pilot_judge(dr, target)
        tried.append({"tol": tol, "result": res, "max_drift": float(np.nanmax(dr)) if np.isfinite(dr).any() else None})
        log(f"  pilot tol={tol:.0e} target {target:.0e}: {res} {tried[-1]['max_drift']}")
        if res == "REFUSE":
            raise RuntimeError("pilot REFUSED")
        if res == "PASS" or tol < 1e-12:
            return tol, {"floor_hit": res != "PASS", "tried": tried, "target": target}
        tol /= 10


def orbit_stats(lev, i, rule, accept):
    """Statistics of orbit i read under a domain rule: 'base' (A2.3/A7 gate) or 'B9' (counted). Reading = the N_ret-th
    return, or, if the orbit ends or leaves the rule's domain first, its fate (ESCAPE), and if it has >= 500 returns
    before that, also read at 500."""
    rec, orb = np.asarray(lev["recs"][i]).reshape(-1, RCOLS), lev["orbs"][i]
    ex = orb[3] if rule == "B9" else -1.0
    n_all = len(rec)
    n_in = n_all if ex < 0 else int(np.sum(rec[:, 0] <= ex))
    ended_early = (orb[2] != 0) or (ex >= 0 and n_in < N_RET)
    N = N_RET if not ended_early else (N_SEC if n_in >= N_SEC else None)
    if N is None:
        drift = (orb[9] if (rule == "B9" and ex >= 0) else orb[6])
        return {"fate": "ESCAPE", "n_ret": n_in, "drift": float(drift), "accepted": bool(drift <= accept), "N": None}
    drift = float(rec[N - 1, 6])
    st = stats_for(rec, lev["box"], N, lev["upos"])
    st.update({"fate": "ESCAPE-READ-500" if ended_early else "FULL", "n_ret": n_in, "drift": drift,
               "accepted": bool(drift <= accept)})
    return st


def save_level(lev, name):
    d = RESULTS / "197_levels"
    d.mkdir(exist_ok=True)
    recs = lev.pop("recs")
    np.savez_compressed(d / f"{name}_recs.npz", *[np.asarray(r) for r in recs])
    (d / f"{name}.json").write_text(json.dumps(lev, default=lambda o: [o.real, o.imag] if isinstance(o, complex)
                                               else float(o)))
    lev["recs"] = recs


def null_levels(point, Lz_list, E_generic):
    """Kerr null levels at this chi (A4): whirl E_b - delta for each Lz, plus generic levels where bound."""
    pk = point_params(point, kerr=True)
    out = []
    for Lz in sorted(set(Lz_list)):
        Eb = e_barrier(pk, Lz)
        if Eb is not None:
            for dl in (1e-4, 1e-3, 1e-2):
                if component_interval(pk, Eb - dl, Lz, "outer") is not None:
                    out.append(("whirl", Eb - dl, Lz, dl))
    for E, Lz in E_generic:
        if component_interval(pk, E, Lz, "outer") is not None:
            out.append(("generic", E, Lz, None))
    return out


def cgates(workers=4):
    import time
    from scipy.stats import binom, beta as cp
    logf = open(RESULTS / "197_cgates.log", "a")

    def log(m):
        print(m, flush=True); logf.write(m + "\n"); logf.flush()
    out = {"amendments": "9aca9a4 + A1..A7 (25c2d39)"}
    lib = _lib()
    # ---- Kerr null at chi = 0.9 (C1; thresholds for C0/C3/C4)
    pk = point_params("P0", kerr=True)
    domk = build_domain(pk)
    nl = null_levels("P0", [3.0], [(0.95, 3.0)])
    log(f"Kerr null levels (chi 0.9): {nl}")
    null = []
    for j, (kind, E, Lz, dl) in enumerate(nl):
        t = time.time()
        lev = run_level(lib, domk, "P0", True, E, Lz, "outer", 100, 197300 + j, DRIFT_TARGET, workers, log)
        save_level(lev, f"null_chi0.9_{j}")
        null.append(lev)
        log(f"null {j} {kind} E {E:.6f} Lz {Lz}: tol {lev['tol']:.0e} UPOs {len(lev['upos'])} [{time.time() - t:.0f}s]")
    tr, ho = [], []
    for lev in null:
        for i in range(len(lev["orbs"])):
            st = orbit_stats(lev, i, "base", ACCEPT)
            if st["fate"] != "ESCAPE" and st["accepted"]:
                (tr if i % 2 == 0 else ho).append(st)
    thr = thresholds(tr)
    out["thresholds_chi0.9"] = thr
    c1 = {}
    for b in range(4):
        hb = [s_ for s_ in ho if dbin(s_["dmin"]) == b]
        if not hb or thr[b] is None:
            c1[b] = {"n": len(hb), "status": "no thresholds" if thr[b] is None else "no held-out orbits"}
            continue
        kk = sum(1 for s_ in hb if verdict(s_, thr) == "CHAOTIC")
        p = float(binom.sf(kk - 1, len(hb), 0.01)) if kk > 0 else 1.0
        c1[b] = {"n": len(hb), "chaotic": kk, "p_vs_1pct": p, "cp95_upper": float(cp.ppf(0.95, kk + 1, len(hb) - kk)),
                 "pass": p >= 0.05}
    out["C1_chi0.9"] = c1
    log(f"C1 (chi 0.9) per d_min bin: {c1}")
    # ---- C0 level (P0, E 0.95, Lz 3): inner + outer, gate on the base domain at 1e-8 (A7)
    dom0 = build_domain(point_params("P0"))
    c0 = {}
    for region, seed in (("inner", 197101), ("outer", 197102)):
        t = time.time()
        lev = run_level(lib, dom0, "P0", False, 0.95, 3.0, region, 100, seed, 1e-9, workers, log)
        save_level(lev, f"C0_{region}")
        sts = [orbit_stats(lev, i, "base", 1e-8) for i in range(100)]
        acc = [s_ for s_ in sts if s_["accepted"]]
        vs = [verdict(s_, thr) for s_ in acc]
        exc = [s_ for s_ in sts if not s_["accepted"]]
        c0[region] = {"n_in": 100, "n_analysed": len(acc), "unreadable": len(exc) > 25,
                      "counts": {v: vs.count(v) for v in sorted(set(vs))},
                      "chaotic_frac": vs.count("CHAOTIC") / max(len(acc), 1),
                      "excluded_UNSCORED": {f"{s_['fate']}": sum(1 for x in exc if x["fate"] == s_["fate"]) for s_ in exc},
                      "tol": lev["tol"], "pilot": lev["pilot"],
                      "upos": [{k_: u[k_] for k_ in ("n", "z", "trace", "hyperbolic")} for u in lev["upos"]]}
        # A7 FINDING: the same orbits read under D_B9 at 1e-9
        b9 = [orbit_stats(lev, i, "B9", ACCEPT) for i in range(100)]
        c0[region]["FINDING_B9"] = {
            "exit_before_Nret": sum(1 for i in range(100) if lev["orbs"][i][3] >= 0 and
                                    int(np.sum(np.asarray(lev["recs"][i]).reshape(-1, RCOLS)[:, 0] <= lev["orbs"][i][3])) < N_RET),
            "returns_before_exit": [b_["n_ret"] for b_ in b9 if b_["fate"] != "FULL"],
            "base_chaotic_breakdown": {
                "never_leave_B9": sum(1 for i, s_ in enumerate(sts) if s_["accepted"] and verdict(s_, thr) == "CHAOTIC"
                                      and lev["orbs"][i][3] < 0),
                "leave_after_500_still_chaotic": sum(1 for i, s_ in enumerate(sts) if s_["accepted"]
                                                     and verdict(s_, thr) == "CHAOTIC" and b9[i]["fate"] == "ESCAPE-READ-500"
                                                     and b9[i]["accepted"] and verdict(b9[i], thr) == "CHAOTIC"),
                "leave_before_500": sum(1 for i, s_ in enumerate(sts) if s_["accepted"] and verdict(s_, thr) == "CHAOTIC"
                                        and b9[i]["fate"] == "ESCAPE")},
            "B9_counts_at_1e-9": (lambda vv: {v: vv.count(v) for v in sorted(set(vv))})(
                [verdict(b_, thr) if b_["fate"] != "ESCAPE" and b_["accepted"] else
                 ("ESCAPE" if b_["fate"] == "ESCAPE" else "EXCLUDED-ACCURACY") for b_ in b9])}
        log(f"C0 {region}: {json.dumps({k_: v for k_, v in c0[region].items() if k_ not in ('upos', 'pilot')}, default=str)} [{time.time() - t:.0f}s]")
    out["C0"] = c0
    out["C0_pass"] = {"inner_ge_50pct": (not c0["inner"]["unreadable"]) and c0["inner"]["chaotic_frac"] >= 0.5,
                      "outer_le_10pct": (not c0["outer"]["unreadable"]) and c0["outer"]["chaotic_frac"] <= 0.10,
                      "inner_extent": "0.7194-2.1246 (G-q): within 0.05 of 0.72-2.1"}
    # ---- C3/C4: island orbits near stable period-1 centres (outer u0; inner period-1)
    c3 = {}
    for region, rho_ref, seed in (("outer", 8.35, 197201), ("inner", 0.92, 197202)):
        lev0 = json.load(open(RESULTS / "197_levels" / f"C0_{region}.json"))
        pp = point_params("P0")
        k = pp[2]
        stab = [u for u in lev0["upos"] if u["n"] == 1 and not u["hyperbolic"]]
        if not stab:
            c3[region] = {"status": "no stable period-1 orbit found"}
            continue
        cen = min(stab, key=lambda u: abs(rho_of_x(u["z"][0], k) - rho_ref))
        box = lev0["box"]
        rng = np.random.default_rng(seed)
        L = []
        while len(L) < 10:
            du, dv = rng.uniform(-1e-3, 1e-3, 2)
            z = launch(pp, 0.95, 3.0, cen["z"][0] + du * (box["xb"] - box["xa"]), cen["z"][1] + dv * 2 * box["pm"])
            if z is not None:
                L.append(z)
        jobs = [(("P0", False, "C3", region, i), "P0", False, 0.95, 3.0, L[i].tolist(), lev0["tol"], N_RET,
                 seed * 1000 + i) for i in range(10)]
        res = run_pool(jobs, workers)
        lev = {"box": box, "upos": lev0["upos"], "recs": [r for _, r, _ in res], "orbs": [o for _, _, o in res]}
        sts = [orbit_stats(lev, i, "base", 1e-8) for i in range(10)]
        rows = []
        for s_ in sts:
            t_ = thr[dbin(s_["dmin"])] if s_["lam2"] is not None else None
            i1h = t_ is not None and s_["lam2"] > t_["lam2"][1] and s_["rho"] > t_["rho"][1]
            i2h = t_ is not None and s_["D2A"] is not None and s_["D2B"] is not None and \
                s_["D2A"] > t_["D2A"][1] and s_["D2B"] > t_["D2B"][1]
            rows.append({"accepted": s_["accepted"], "fate": s_["fate"], "I1_high": bool(i1h), "I2_high": bool(i2h),
                         "D2A": s_.get("D2A"), "D2B": s_.get("D2B"), "drift": s_["drift"]})
        c3[region] = {"centre": cen["z"], "centre_rho": float(rho_of_x(cen["z"][0], k)), "rows": rows,
                      "C3_pass": all(r["accepted"] and not r["I1_high"] and not r["I2_high"] for r in rows),
                      "C4_pass": all(r["D2A"] is not None and r["D2B"] is not None and r["D2A"] < 1.3 and r["D2B"] < 1.3
                                     for r in rows)}
        log(f"C3/C4 {region}: centre rho {c3[region]['centre_rho']:.3f} C3 {c3[region]['C3_pass']} C4 {c3[region]['C4_pass']}")
    out["C3_C4"] = c3
    (RESULTS / "197_cgates.json").write_text(json.dumps(out, indent=1, default=str))
    log("saved results/197_cgates.json")
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--gq", action="store_true")
    ap.add_argument("--cgates", action="store_true")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--selftest-pilot", action="store_true")
    a = ap.parse_args()
    if a.gq:
        gate_gq()
    if a.selftest_pilot:
        selftest_pilot()
    if a.cgates:
        st_ = RESULTS / "197_pilot_selftest.json"
        gq_ = RESULTS / "197_gate_gq.json"
        if not (st_.exists() and json.load(open(st_)).get("ALL_PASS") and gq_.exists()
                and json.load(open(gq_)).get("G_q_PASS")):
            raise SystemExit("C-gates refused: C2 self-test and G-q must have passed first")
        cgates(a.workers)
