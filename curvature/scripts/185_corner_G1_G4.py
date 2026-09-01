"""Step 185 — the remaining frozen gates: G1 (area agreement), G2 (corner coefficients + PAIRWISE matrix),
G3 (the area-must-fail-to-be-universal control), G4 (the clip band).

FROZEN PRE-REG @ e283d21 +A1 +A2 +A3 +A4.  EXTRACTION MODEL IS THE FROZEN ONE:  S = alpha*P + beta*ln(L) + gamma
with L the side length. The 1/R column used in 183/184 was a DIAGNOSTIC and never enters the extraction.

STANDING LIMITATION, stated here so it appears beside every number this produces: **the extraction carries ONE
validation gate, not two.** G1b was designed to test whether the extraction manufactures logarithms out of shape
changes, and it turned out to be UNCONSTRUCTIBLE on any range compatible with L << xi -- omit the subleading
column and the log proxies for it (false positives); include it and it absorbs the genuine log (no sensitivity).
Its verdict is VACUOUS, not passed and not failed. G1 below is the remaining check and it has a known weakness
of its own (different corner counts, so a systematic could shift both alphas together).

CLAIM SCOPE: tabula's OWN instrument check. NOT an independent replication -- that died with the contamination
and cannot be revived by finishing the work.

G3 IS THE STRONGEST GATE HERE and it is quantum's: the AREA coefficient must FAIL to be universal. Its only
pass is a failure of the thing one would naively want, so it cannot be satisfied by a broken extraction that
flatters everything.

G2 REPORTS THE FULL PAIRWISE MATRIX, not max-min (Amendment 3): a max-min spread does not move when an
accidentally-tight pair sits between the extrema, so it is structurally blind to the coincidence where one
regulator agrees with another for reasons unrelated to universality.
"""

import json
import sys
from importlib import import_module
from itertools import combinations
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from curvlib import RESULTS, progress

cl = import_module("181_corner_lib")

RS = [5, 6, 7, 8, 10, 11, 13, 16, 18, 22, 25, 30]
CLIPS = (1e-14, 1e-12, 1e-10, 1e-8)
REGS = cl.REGULATORS


def entropies(reg, shape, clip):
    X, P = cl.correlators(reg)
    S, PR = [], []
    for i, R in enumerate(RS):
        sites = cl.hexagon(R, R, R) if shape == "hex" else cl.triangle(R)
        s, _ = cl.entropy(sites, X, P, clip=clip)
        S.append(s); PR.append(cl.perimeter(sites))
        progress(f"185_{reg}_{shape}", i + 1, len(RS))
    return np.array(S), np.array(PR, float)


def main():
    out = {"prereg": "e283d21 +A1 +A2 +A3 +A4", "R": RS,
           "claim_scope": "tabula's OWN instrument check, NOT an independent replication",
           "standing_limitation": ("the extraction carries ONE validation gate (G1), not two -- G1b proved "
                                   "UNCONSTRUCTIBLE and its verdict is VACUOUS, neither pass nor fail"),
           "extraction_model": "FROZEN: S = alpha*P + beta*ln(L) + gamma, L = side length"}

    # ---------- G1 + G2 + G3 at the reference clip ----------
    fits = {}
    print("computing entropies (4 regulators x 2 shapes x 12 sizes)...")
    for reg in REGS:
        fits[reg] = {}
        for shape, ncorn in (("hex", 6), ("tri", 3)):
            S, PR = entropies(reg, shape, 1e-12)
            a, b, g, r2, cond = cl.fit_area_log(RS, PR, S)
            fits[reg][shape] = {"alpha": a, "beta": b, "gamma": g, "R2": r2, "cond": cond,
                                "a_theta": -b / ncorn, "S": S.tolist(), "P": PR.tolist()}
            print(f"  {reg:9s} {shape}: alpha={a:+.6f}  a({120 if shape=='hex' else 60})={-b/ncorn:+.6f}  "
                  f"R2={r2:.8f}  cond={cond:.0f}", flush=True)

    # G1 -- area agreement between shapes, with Amendment 3's absolute bounds on the denominator
    g1 = {}
    for reg in REGS:
        at, ah = fits[reg]["tri"]["alpha"], fits[reg]["hex"]["alpha"]
        rel = abs(at - ah) / abs((at + ah) / 2)
        absolute_ok = bool(np.isfinite(at) and np.isfinite(ah) and at > 0 and ah > 0
                           and 0.001 < abs(at) < 1.0 and 0.001 < abs(ah) < 1.0)
        g1[reg] = {"alpha_tri": at, "alpha_hex": ah, "rel_diff": rel, "absolute_bounds_ok": absolute_ok,
                   "pass": bool(absolute_ok and rel < 0.05)}
    G1 = all(v["pass"] for v in g1.values())
    print(f"\nG1 area agreement (tri vs hex): " +
          "  ".join(f"{r}={g1[r]['rel_diff']:.2%}" for r in REGS) + f"   -> {G1}")

    # G2 -- corner coefficients, FULL PAIRWISE MATRIX (Amendment 3)
    a60 = {r: fits[r]["tri"]["a_theta"] for r in REGS}
    a120 = {r: fits[r]["hex"]["a_theta"] for r in REGS}
    def pairwise(d):
        m = {}
        for x, y in combinations(REGS, 2):
            m[f"{x}|{y}"] = abs(d[x] - d[y]) / abs((d[x] + d[y]) / 2)
        return m
    pw60, pw120 = pairwise(a60), pairwise(a120)
    sp60 = (max(a60.values()) - min(a60.values())) / abs(np.mean(list(a60.values())))
    sp120 = (max(a120.values()) - min(a120.values())) / abs(np.mean(list(a120.values())))
    print(f"\nG2 a(60):  " + "  ".join(f"{r}={a60[r]:+.5f}" for r in REGS))
    print(f"   a(120): " + "  ".join(f"{r}={a120[r]:+.5f}" for r in REGS))
    print(f"   max-min spread: a(60) {sp60:.2%}   a(120) {sp120:.2%}")
    print(f"   PAIRWISE a(120): " + "  ".join(f"{k}={v:.2%}" for k, v in pw120.items()))

    # G3 -- quantum's free positive control: the AREA coefficient must FAIL to be universal
    alph = {r: fits[r]["hex"]["alpha"] for r in REGS}
    sp_area = (max(alph.values()) - min(alph.values())) / abs(np.mean(list(alph.values())))
    G3 = bool(sp_area > 10 * max(sp60, sp120))
    print(f"\nG3 area spread {sp_area:.2%} vs corner spreads {max(sp60,sp120):.2%}  "
          f"-> area {'IS' if G3 else 'is NOT'} far less universal  ({G3})")

    # G4 -- clip band
    print("\nG4 clip band sweep...")
    band = {}
    for c in CLIPS:
        S, PR = entropies("nn", "hex", c)
        a, b, g, r2, _ = cl.fit_area_log(RS, PR, S)
        band[f"{c:g}"] = {"alpha": a, "a120": -b / 6}
        print(f"  clip {c:g}: alpha={a:+.8f}  a(120)={-b/6:+.8f}")
    a120s = [v["a120"] for v in band.values()]
    clip_band = (max(a120s) - min(a120s)) / abs(np.mean(a120s))
    G4 = bool(clip_band < 0.1 * max(sp60, sp120))
    print(f"  clip band on a(120): {clip_band:.3%}  vs corner spread {max(sp60,sp120):.2%}  -> {G4}")

    out.update({"fits": {r: {s: {k: v for k, v in fits[r][s].items() if k not in ("S", "P")}
                             for s in fits[r]} for r in REGS},
                "G1": g1, "G1_pass": G1,
                "G2": {"a60": a60, "a120": a120, "spread_a60": sp60, "spread_a120": sp120,
                       "pairwise_a60": pw60, "pairwise_a120": pw120},
                "G3": {"area_spread": sp_area, "corner_spread_max": max(sp60, sp120), "pass": G3},
                "G4": {"band": band, "clip_band_frac": clip_band, "pass": G4},
                "all_gates": bool(G1 and G3 and G4)})
    (RESULTS / "185_corner_G1_G4.json").write_text(json.dumps(out, indent=1))
    print(f"\nG1 {G1} | G3 {G3} | G4 {G4}")
    print("saved results/185_corner_G1_G4.json")


if __name__ == "__main__":
    main()
