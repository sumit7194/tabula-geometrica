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


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--gq", action="store_true")
    a = ap.parse_args()
    if a.gq:
        gate_gq()
