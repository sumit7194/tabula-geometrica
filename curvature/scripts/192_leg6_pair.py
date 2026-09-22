#!/usr/bin/env python3
"""§192 -- 1a: a WELL-SEPARATED Carter pair, built in-house. Pre-registration: notes/leg6_pair.md.

KEEP is purely angular (Carter becomes Q + eps*dTheta EXACTLY, dTheta known in closed form); BREAK is purely
mixed with f(r) = r - 7 (zero-mean on the orbit region), so it is nearly orthogonal to KEEP. Two pairs: the
keeper's invariant IN the screen's basis (cos^2) and OUT of it (cos^4). Uses §191b's validated split machinery.
Every arm: chi, seed 1/51, NTRAJ/NSTEP 40/3000, readout = min over ALL conserved directions, own eps=0 floor.
"""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np, sympy as sp
sys.path.insert(0, str(Path(__file__).resolve().parent))
from importlib import import_module
import importlib.util

m = import_module("190_leg6_triple")
_spec = importlib.util.spec_from_file_location("c191b", Path(__file__).resolve().parent / "191b_c_mechanism.py")
c = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(c)
ROOT = Path(__file__).resolve().parents[1]
r, th, a, eps, SIG = c.r, c.th, c.a, c.eps, c.SIG
CHI, NTRAJ, NSTEP = 0.075, 40, 3000
c.CHI = CHI
EPS_GRID = [0.0, 0.05, 0.10, 0.20]
G = {1: sp.Rational(49, 20) * sp.cos(th) ** 2, 2: sp.Rational(49, 20) * sp.cos(th) ** 4}
F = r - 7


def _obj(kind, pair):
    g00, g03, g11, g22, g33 = c._kerr
    extra = G[pair] if kind == "KEEP" else F * G[pair]
    return (g00, g03, g11, 1 / (c._IK["ith"] + eps * extra / SIG), g33)


for pr in (1, 2):
    for kd in ("KEEP", "BREAK"):
        m.OBJECTS[f"{kd}{pr}"] = (lambda kd=kd, pr=pr: _obj(kd, pr))
        c.m.OBJECTS[f"{kd}{pr}"] = m.OBJECTS[f"{kd}{pr}"]

_G = {k: sp.lambdify(th, v, "numpy") for k, v in G.items()}


def traj(obj, ep, seed):
    m.A_SPIN = CHI
    M = m.build(obj)
    y0, E, L = m.launch(M, ep, seed, NTRAJ)
    return m.rk4(M, y0, E, L, ep, m.DT, NSTEP), E, L


def Qof(T, E, L):
    TH, PT = T[:, 1, :], T[:, 3, :]
    return PT ** 2 + np.cos(TH) ** 2 * (CHI ** 2 * (1 - E ** 2) + L ** 2 / np.sin(TH) ** 2)


def held(X):
    z = (X - X.mean()) / X.std()
    return float(np.mean([z[:, i].var() for i in range(z.shape[1])]) / z.var())


def screen(obj, ep, pair, add):
    Ttr, E, L = traj(obj, ep, 1)
    Tte, _, _ = traj(obj, ep, 51)
    def feats(T):
        f, _ = m.features(T, 2, True)
        if not add:
            return f
        TH, PT = T[:, 1, :].T, T[:, 3, :].T
        return np.concatenate([f, (_G[pair](TH) * PT ** 2)[..., None]], -1)
    ev, C, mu, sd = m.conserved(feats(Ttr))
    minsel = float(min(m.s99.heldout(feats(Tte), C[:, k], mu, sd) for k in range(C.shape[1])))
    dth = _G[pair](Tte[:, 1, :]) * Tte[:, 3, :] ** 2
    scored = held(Qof(Tte, E, L) + ep * dth)                  # the KNOWN direction Q + eps*dTheta_KEEP
    return minsel, scored


def checks():
    out = {}
    T, E, L = traj("A", 0.0, 1)                                # Kerr orbits (every object = Kerr at eps=0)
    R, TH, PT = T[:, 0, :], T[:, 1, :], T[:, 3, :]
    for pr in (1, 2):
        k = (_G[pr](TH) * PT ** 2).ravel(); b = ((R - 7) * _G[pr](TH) * PT ** 2).ravel()
        out[f"cos_pair{pr}"] = float(abs(k @ b) / (np.linalg.norm(k) * np.linalg.norm(b)))
    u = np.cos(TH).ravel() ** 2
    Bm = np.stack([np.ones_like(u), u, 1 / (1 - u)], 1)
    coef, *_ = np.linalg.lstsq(Bm, u ** 2, rcond=None)
    out["cos4_span_residual"] = float(np.linalg.norm(Bm @ coef - u ** 2) / np.linalg.norm(u ** 2))
    for pr in (1, 2):
        for kd in ("KEEP", "BREAK"):
            P = c.split(f"{kd}{pr}"); Tk, Ek, Lk = traj(f"{kd}{pr}", 0.1, 1)
            Rk, THk, PRk, PTk = Tk[:, 0, :], Tk[:, 1, :], Tk[:, 2, :], Tk[:, 3, :]
            mom = {"E2": Ek ** 2, "m2EL": -2 * Ek * Lk, "L2": Lk ** 2, "pr2": PRk ** 2, "pth2": PTk ** 2}
            ang = mix = 0.0
            for kk, fn in P.items():
                _, f_, g_, c_, n_ = c.parts_at(fn, Rk, THk); mm = mom[c.MOM[kk]]
                if kk == "irr":   mix = mix + (g_ + n_) * mm
                elif kk == "ith": ang, mix = ang + (g_ + c_) * mm, mix + (f_ + n_) * mm
                else:             ang, mix = ang + g_ * mm, mix + n_ * mm
            out[f"{kd}{pr}_rms_angular"] = float(np.sqrt(np.nanmean(np.asarray(ang) ** 2)))
            out[f"{kd}{pr}_rms_mixed"] = float(np.sqrt(np.nanmean(np.asarray(mix) ** 2)))
    return out


def main():
    res = {"config": {"chi": CHI, "ntraj": NTRAJ, "nstep": NSTEP, "seeds": [1, 51], "readout": "all",
                      "eps_grid": EPS_GRID}}
    ck = checks(); res["checks"] = ck
    print("  CONSTRUCTION CHECKS (must hold before any screen result is read)")
    for pr in (1, 2):
        print(f"    pair {pr}: cos(KEEP, BREAK) on Kerr orbits = {ck[f'cos_pair{pr}']:.4f}   (need < 0.3)")
        for kd in ("KEEP", "BREAK"):
            print(f"      {kd}{pr}: rms angular {ck[f'{kd}{pr}_rms_angular']:.3e}   rms mixed {ck[f'{kd}{pr}_rms_mixed']:.3e}")
    print(f"    cos^4 relative residual in span{{1, cos^2, 1/sin^2}} over orbit samples: {ck['cos4_span_residual']:.3e}\n",
          flush=True)
    arms = [("KEEP1", 1, False), ("BREAK1", 1, False),
            ("KEEP2", 2, False), ("BREAK2", 2, False), ("KEEP2", 2, True), ("BREAK2", 2, True)]
    print(f"  {'arm':>16} " + " ".join(f"{e:>10}" for e in EPS_GRID) + "   <- min-over-basis margin")
    for obj, pr, add in arms:
        lab = f"{obj}{' +dTheta' if add else ''}"
        rows = [screen(obj, e, pr, add) for e in EPS_GRID]
        res[lab] = {"min_over_basis": [x[0] for x in rows], "scored_known_direction": [x[1] for x in rows]}
        print(f"  {lab:>16} " + " ".join(f"{x[0]:>10.3e}" for x in rows), flush=True)
        print(f"  {'scored Q+eps*dTh':>16} " + " ".join(f"{x[1]:>10.3e}" for x in rows), flush=True)
    (ROOT / "results").mkdir(exist_ok=True)
    json.dump(res, open(ROOT / "results" / "192_leg6_pair.json", "w"), indent=2)


if __name__ == "__main__":
    main()
