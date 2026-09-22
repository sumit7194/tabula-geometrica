#!/usr/bin/env python3
"""§191 -- the C anomaly, M1: re-measure at ONE configuration.

Leg 6 reported C's bare Carter Q conserved far better than A's, "confirmed by two instruments agreeing to
2.24x". Opening this arc found the two instruments differed on THREE axes, not zero: chi (0.6 vs 0.075),
trajectory set (seed 1 vs seed 51), and statistic (global max amplitude vs within/total variance). This
script computes BOTH statistics on BOTH trajectory sets at BOTH chi, so every reported ratio is
like-for-like. The drift statistic is the original, verbatim (recovered from the session transcript).

    drift    = max over all trajectories and times of |Q - Q0| / |Q0|        (an AMPLITUDE)
    heldout  = mean over trajectories of var_within(Q) / var_total(Q)        (a VARIANCE ratio)
"""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from importlib import import_module

m = import_module("190_leg6_triple")
ROOT = Path(__file__).resolve().parents[1]
NTRAJ, NSTEP, EPS = 40, 3000, 0.05


def trajectories(obj, chi, ep, seed):
    m.A_SPIN = chi
    M = m.build(obj)
    y0, E, L = m.launch(M, ep, seed, NTRAJ)
    T = m.rk4(M, y0, E, L, ep, m.DT, NSTEP)
    TH, PT = T[:, 1, :], T[:, 3, :]
    Q = PT ** 2 + np.cos(TH) ** 2 * (chi ** 2 * (1 - E ** 2) + L ** 2 / np.sin(TH) ** 2)
    return Q                                     # (time, traj)


def drift(Q):
    return float(np.nanmax(np.abs(Q - Q[0]) / (np.abs(Q[0]) + 1e-30)))


def heldout(Q):
    z = (Q - Q.mean()) / Q.std()
    return float(np.mean([z[:, i].var() for i in range(z.shape[1])]) / z.var())


def main():
    out = {}
    print(f"  {'chi':>6} {'seed':>4} {'obj':>3} {'drift(eps=0)':>13} {'drift':>11} {'heldout':>11}")
    for chi in (0.6, 0.075):
        for seed in (1, 51):
            for obj in ("A", "B", "C"):
                q0 = trajectories(obj, chi, 0.0, seed)
                q = trajectories(obj, chi, EPS, seed)
                row = {"floor": drift(q0), "drift": drift(q), "heldout": heldout(q)}
                out[f"chi{chi}_s{seed}_{obj}"] = row
                print(f"  {chi:>6} {seed:>4} {obj:>3} {row['floor']:>13.3e} {row['drift']:>11.4e} "
                      f"{row['heldout']:>11.4e}", flush=True)
    print("\n  A/C ratios, matched power (drift^2 vs heldout):")
    print(f"  {'chi':>6} {'seed':>4} {'drift A/C':>10} {'(drift A/C)^2':>14} {'heldout A/C':>12} {'agreement':>10}")
    for chi in (0.6, 0.075):
        for seed in (1, 51):
            a, c = out[f"chi{chi}_s{seed}_A"], out[f"chi{chi}_s{seed}_C"]
            dr = a["drift"] / c["drift"]; hr = a["heldout"] / c["heldout"]
            print(f"  {chi:>6} {seed:>4} {dr:>10.2f} {dr**2:>14.1f} {hr:>12.1f} {max(dr**2,hr)/min(dr**2,hr):>9.2f}x")
    (ROOT / "results").mkdir(exist_ok=True)
    json.dump(out, open(ROOT / "results" / "191_c_anomaly_m1.json", "w"), indent=2)


if __name__ == "__main__":
    main()
