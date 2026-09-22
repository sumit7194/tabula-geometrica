#!/usr/bin/env python3
"""§191b -- the C anomaly, M2: WHY is bare Carter Q conserved better on C than on A?

Kerr separates in this code's own coordinates (verified: with Sigma = r^2 + a^2 cos^2 th, every coefficient
of 2*Sigma*H0 passes its separability test with residual exactly 0). So 2*Sigma*H = R(r,p_r) + Theta(th,p_th),
and K = Theta - 2H a^2 cos^2 th is Carter's constant. Split the O(eps) deformation 2*Sigma*dH into

    RADIAL     depends on (r, p_r) only                  -> bare Q stays EXACTLY conserved
    ANGULAR    depends on (th, p_th) only                -> separable, but Carter becomes Q + eps*dTheta,
                                                            so bare Q moves by exactly -eps*dTheta
    MIXED      everything else                           -> breaks separability

and PREDICT the bare-Q drift from the angular part alone, in the SAME statistic as the measured drift
(global max over trajectories and times of |Q - Q0|/|Q0|). Exact at O(eps) for separable deformations.

CONTROLS, which must behave as stated or no verdict issues:
    RAD  a radial-only deformation  -> measured drift at the integration floor, prediction 0
    ANG  an angular-only deformation -> measured drift matches the prediction
Their deformation norms are reported so RAD's zero cannot come from a deformation too small to matter.
"""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np, sympy as sp
sys.path.insert(0, str(Path(__file__).resolve().parent))
from importlib import import_module

m = import_module("190_leg6_triple")
ROOT = Path(__file__).resolve().parents[1]
r, th, a, eps = m.r, m.th, m.a, m.eps
SIG = r ** 2 + a ** 2 * sp.cos(th) ** 2
NTRAJ, NSTEP, EPS, CHI, SEED = 40, 3000, 0.05, 0.6, 1
R0, TH0 = sp.Integer(7), sp.pi / 2                       # reference point for the f/g/n split

_kerr = [sp.simplify(c.subs(eps, 0)) for c in m.OBJECTS["A"]()]


def _inv(g):
    g00, g03, g11, g22, g33 = g
    D = g00 * g33 - g03 ** 2
    return {"itt": g33 / D, "itp": -g03 / D, "ipp": g00 / D, "irr": 1 / g11, "ith": 1 / g22}


_IK = _inv(_kerr)


def _control(kind):
    g00, g03, g11, g22, g33 = _kerr
    if kind == "RAD":      # Sigma * d(irr) = r^2 / 20  -- a function of r ONLY, times p_r^2
        return (g00, g03, 1 / (_IK["irr"] + eps * (r ** 2 / 20) / SIG), g22, g33)
    if kind == "RAD2":     # Sigma * d(ipp) = 49/r^2 -- r ONLY, on the L^2 coefficient (L^2 ~ 6.8 here), so the
        #                  deformation is the same SIZE as ANG's. RAD's p_r^2 version was ~240x smaller than
        #                  ANG's on near-circular orbits, which left its zero open to "too small to matter".
        #                  Built by editing ONLY the inverse (t,phi) block's L^2 entry and inverting exactly.
        itt, itp, ipp = _IK["itt"], _IK["itp"], _IK["ipp"] + eps * (49 / r ** 2) / SIG
        Dinv = itt * ipp - itp ** 2
        return (ipp / Dinv, -itp / Dinv, g11, g22, itt / Dinv)
    if kind == "ANG":      # Sigma * d(ith) = cos^2 th * 49/20 -- a function of th ONLY, times p_th^2
        return (g00, g03, g11, 1 / (_IK["ith"] + eps * (sp.cos(th) ** 2 * sp.Rational(49, 20)) / SIG), g33)


m.OBJECTS["RAD"] = lambda: _control("RAD")
m.OBJECTS["ANG"] = lambda: _control("ANG")
m.OBJECTS["RAD2"] = lambda: _control("RAD2")

MOM = {"itt": "E2", "itp": "m2EL", "ipp": "L2", "irr": "pr2", "ith": "pth2"}


def split(obj):
    """Lambdified 2*Sigma*dH coefficients. The radial/angular/mixed split is done NUMERICALLY at the
    evaluation points (mixed = s(r,th) - s(r,th0) - s(r0,th) + s(r0,th0)), so no symbolic simplify is needed.
    The first version simplified symbolically and died silently on object A with no traceback."""
    inv = _inv(m.OBJECTS[obj]())
    return {k: sp.lambdify((r, th, a), SIG * sp.diff(v, eps).subs(eps, 0), "numpy") for k, v in inv.items()}


def parts_at(fn, R, TH):
    r0, th0 = float(R0), float(TH0)
    ev = lambda x, y: np.broadcast_to(np.asarray(fn(x, y, CHI), float), np.broadcast(R, TH).shape)
    s_ = ev(R, TH); f_ = ev(R, np.full_like(TH, th0)); g_ = ev(np.full_like(R, r0), TH)
    c_ = ev(np.full_like(R, r0), np.full_like(TH, th0))
    return s_, f_ - c_, g_ - c_, c_, s_ - f_ - g_ + c_        # s, f, g, c, mixed


def evaluate(obj):
    m.A_SPIN = CHI
    M = m.build(obj)
    y0, E, L = m.launch(M, EPS, SEED, NTRAJ)
    T = m.rk4(M, y0, E, L, EPS, m.DT, NSTEP)
    R, TH, PR, PT = T[:, 0, :], T[:, 1, :], T[:, 2, :], T[:, 3, :]
    Q = PT ** 2 + np.cos(TH) ** 2 * (CHI ** 2 * (1 - E ** 2) + L ** 2 / np.sin(TH) ** 2)
    mom = {"E2": E ** 2, "m2EL": -2 * E * L, "L2": L ** 2, "pr2": PR ** 2, "pth2": PT ** 2}
    P = split(obj)
    rad = ang = mix = 0.0
    for k, fn in P.items():
        _, f_, g_, c_, n_ = parts_at(fn, R, TH)
        mm = mom[MOM[k]]
        if k == "irr":   rad, mix = rad + (f_ + c_) * mm, mix + (g_ + n_) * mm      # p_r^2 x th-fn mixes
        elif k == "ith": ang, mix = ang + (g_ + c_) * mm, mix + (f_ + n_) * mm      # p_th^2 x r-fn mixes
        else:            rad, ang, mix = rad + f_ * mm, ang + g_ * mm, mix + n_ * mm
    Q0 = np.abs(Q[0]) + 1e-30
    measured = float(np.nanmax(np.abs(Q - Q[0]) / Q0))
    predicted = float(np.nanmax(np.abs(EPS * (ang - ang[0])) / Q0))    # Q + eps*dTheta conserved
    return {"measured": measured, "predicted_from_angular": predicted,
            "rms_radial": float(np.sqrt(np.nanmean(rad ** 2))),
            "rms_angular": float(np.sqrt(np.nanmean(ang ** 2))),
            "rms_mixed": float(np.sqrt(np.nanmean(mix ** 2)))}


def main():
    out = {}
    print(f"  chi={CHI}, eps={EPS}, seed {SEED}, {NTRAJ}/{NSTEP}  (same config as the leg-6 analytic drift)\n")
    print(f"  {'obj':>4} {'measured':>11} {'pred(ang)':>11} {'meas/pred':>10} | {'rms radial':>11} {'rms angular':>12} {'rms mixed':>11}")
    for obj in ("RAD", "RAD2", "ANG", "A", "B", "C"):
        d = evaluate(obj); out[obj] = d
        ratio = d["measured"] / d["predicted_from_angular"] if d["predicted_from_angular"] > 0 else float("inf")
        print(f"  {obj:>4} {d['measured']:>11.3e} {d['predicted_from_angular']:>11.3e} {ratio:>10.3f} | "
              f"{d['rms_radial']:>11.3e} {d['rms_angular']:>12.3e} {d['rms_mixed']:>11.3e}", flush=True)
    (ROOT / "results").mkdir(exist_ok=True)
    json.dump(out, open(ROOT / "results" / "191b_c_mechanism.json", "w"), indent=2)


if __name__ == "__main__":
    main()
