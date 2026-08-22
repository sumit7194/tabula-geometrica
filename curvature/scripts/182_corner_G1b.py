"""Step 182 / G1b — THE ZERO-TEST: does my extraction manufacture a logarithm out of a shape change?

FROZEN PRE-REG @ e283d21, Amendment 1 (the gate), Amendment 2 (two-sided), Amendment 3 (absolute floor).

THE IDEA, which is quantum's and is the fix for a limitation I flagged in the frozen file. My original G1
compared the area coefficient between a triangle (3 corners) and a hexagon (6 corners) -- different corner
COUNTS, so a systematic in the corner extraction shifts both alphas together and slips through.

Instead compare two shapes with IDENTICAL corner content, so the corner term cancels EXACTLY rather than
approximately. H(p,q,r) has six exact 120-degree corners for every |p-q| < r < p+q (Amendment 2, verified
exhaustively here: 3146 cases, zero mismatches). So H(R,R,R+2) and H(R,R,R) both have six 120-degree corners,
and their DIFFERENCE has none.

    S_elongated(R) - S_regular(R)   contains NO corner content by construction
    => fitting the SAME frozen model to it must return beta ~ 0

KNOWN-FAIL: a non-zero beta means the extraction is manufacturing a logarithm out of the shape change alone,
every corner coefficient it produces is contaminated, and PER THE FROZEN FILE THE STUDY IS DEAD ON MY SIDE --
no corner numbers are sent.

TWO-SIDED (Amendment 2): H(R,R,R-2) sits on the other side of the reference shape. An extraction that
manufactures a logarithm from elongation would have to manufacture it with the SAME SIGN in both directions to
escape a two-sided test. One-sided, a systematic slips through.

ABSOLUTE FLOOR (Amendment 3, the anti-guard mitigation): beta ~ 0 is satisfied TRIVIALLY by an extraction that
returns beta ~ 0 for EVERYTHING -- including shapes that genuinely have corners. So the single-shape fit must
first demonstrate a beta that is clearly non-zero. A ZERO-TEST IS WORTHLESS WITHOUT A DEMONSTRATED NON-ZERO.
"""

import json
import sys
from importlib import import_module
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from curvlib import RESULTS

cl = import_module("181_corner_lib")

RS = (6, 8, 10, 12, 14, 16)          # side lengths, frozen
REG = "nn"                            # G1b tests MY EXTRACTION, not universality -- one regulator suffices


def main():
    out = {"prereg": "e283d21 +A1 +A2 +A3", "regulator": REG, "R": list(RS)}
    X, P = cl.correlators(REG)

    shapes = {"regular": lambda R: cl.hexagon(R, R, R),
              "elong+2": lambda R: cl.hexagon(R, R, R + 2),
              "elong-2": lambda R: cl.hexagon(R, R, R - 2)}

    S, PER, NS = {}, {}, {}
    for nm, fn in shapes.items():
        S[nm], PER[nm], NS[nm] = [], [], []
        for R in RS:
            sites = fn(R)
            s, nu = cl.entropy(sites, X, P)
            S[nm].append(s); PER[nm].append(cl.perimeter(sites)); NS[nm].append(len(sites))
        print(f"  {nm:8s} sites {NS[nm]}")
        print(f"  {'':8s} S     " + " ".join(f"{v:8.4f}" for v in S[nm]))

    # ---- ABSOLUTE FLOOR FIRST (Amendment 3): the single-shape fit must show a real logarithm ----
    a1, b1, g1, r2_1, cond1 = cl.fit_area_log(RS, PER["regular"], S["regular"])
    a_120_single = -b1 / 6.0
    print(f"\nABSOLUTE FLOOR (single shape, H(R,R,R)):")
    print(f"  alpha={a1:.6f}  beta={b1:.6f}  R2={r2_1:.8f}  cond={cond1:.0f}")
    print(f"  implied a(120) = -beta/6 = {a_120_single:.6f}")
    FLOOR = 0.01
    floor_ok = bool(abs(b1) > FLOOR)
    print(f"  |beta| = {abs(b1):.4f} vs floor {FLOOR}  -> "
          f"{'a real logarithm is present, so a zero-test is meaningful' if floor_ok else 'NO demonstrated non-zero: the zero-test would be vacuous'}")

    # ---- THE TWO-SIDED ZERO TEST ----
    print(f"\nG1b — fitting the SAME model to differences with ZERO corner content:")
    res = {}
    for nm in ("elong+2", "elong-2"):
        dS = np.array(S[nm]) - np.array(S["regular"])
        dP = np.array(PER[nm]) - np.array(PER["regular"])
        a, b, g, r2, cond = cl.fit_area_log(RS, dP, dS)
        ratio = abs(b) / abs(b1)
        res[nm] = {"alpha": a, "beta": b, "gamma": g, "R2": r2, "cond": cond,
                   "beta_over_single_beta": ratio, "dS": dS.tolist(), "dP": dP.tolist()}
        print(f"  {nm}:  beta = {b:+.6f}   |beta|/|beta_single| = {ratio:.4f}   R2={r2:.6f}")

    TOL = 0.10                       # the manufactured log must be <10% of the real one
    both = [res["elong+2"]["beta_over_single_beta"], res["elong-2"]["beta_over_single_beta"]]
    zero_ok = bool(max(both) < TOL)
    same_sign = bool(np.sign(res["elong+2"]["beta"]) == np.sign(res["elong-2"]["beta"]))

    G1b = bool(floor_ok and zero_ok)
    print(f"\n  two-sided: betas {res['elong+2']['beta']:+.6f} and {res['elong-2']['beta']:+.6f}"
          f"   same sign: {same_sign}")
    print(f"  max |beta|/|beta_single| = {max(both):.4f}  vs tolerance {TOL}")

    out.update({"S": S, "perimeter": PER, "n_sites": NS,
                "single_shape_fit": {"alpha": a1, "beta": b1, "R2": r2_1, "cond": cond1,
                                     "implied_a120": a_120_single},
                "absolute_floor": {"floor": FLOOR, "abs_beta": abs(b1), "pass": floor_ok,
                                   "why": "a zero-test is worthless without a demonstrated non-zero"},
                "differences": res, "tolerance": TOL,
                "two_sided_same_sign": same_sign,
                "G1b_pass": G1b,
                "verdict": ("G1b PASSED. The single-shape fit shows a real logarithm (|beta| = {:.3f}, implied "
                            "a(120) = {:.4f}), so the zero-test is meaningful rather than vacuous. Fitting the "
                            "SAME model to two differences with zero corner content by construction returns "
                            "beta = {:+.5f} and {:+.5f}, both under {:.0%} of the genuine logarithm. The "
                            "extraction is not manufacturing a logarithm out of the shape change, in either "
                            "direction. Proceeding to G1 and the corner coefficients."
                            .format(abs(b1), a_120_single, res['elong+2']['beta'], res['elong-2']['beta'], TOL)
                            if G1b else
                            ("G1b FAILED -- THE STUDY IS DEAD ON MY SIDE AND NO CORNER NUMBERS ARE SENT. " +
                             ("The extraction manufactures a logarithm from a shape change with no corner "
                              "content, so every corner coefficient it produces is contaminated."
                              if floor_ok else
                              "The single-shape fit shows no demonstrated non-zero logarithm, so the zero-test "
                              "cannot distinguish a working extraction from one that returns beta~0 for "
                              "everything.")))})
    print(f"\nfloor {floor_ok} | zero-test {zero_ok} -> G1b {G1b}")
    print(out["verdict"])
    (RESULTS / "182_corner_G1b.json").write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(1, 2, figsize=(13, 4.6))
    for nm in shapes:
        ax[0].plot(RS, S[nm], "o-", label=nm)
    ax[0].set_xlabel("R (side length)"); ax[0].set_ylabel("S"); ax[0].legend(fontsize=8)
    ax[0].set_title("entropies · all three shapes have six 120° corners")
    for nm in ("elong+2", "elong-2"):
        ax[1].plot(RS, res[nm]["dS"], "s-", label=f"{nm} − regular (β={res[nm]['beta']:+.4f})")
    ax[1].set_xlabel("R"); ax[1].set_ylabel("ΔS"); ax[1].legend(fontsize=8)
    ax[1].set_title("G1b · differences have ZERO corner content → β must vanish")
    fig.tight_layout(); fig.savefig(RESULTS / "182_corner_G1b.png", dpi=140)
    print("saved results/182_corner_G1b.json + .png")


if __name__ == "__main__":
    main()
