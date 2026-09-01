"""Step 186 — ADDITIVE mutation test of the whole gate set (Amendment 3, owed before any number is filed).

WHY ADDITIVE. quantum's detail, and the part that would have been got wrong: a common MULTIPLICATIVE rescaling
leaves every ratio EXACTLY invariant. Every gate here is a ratio -- relative area agreement, fractional corner
spread, clip band as a fraction. Scale all the entropies by 1.5 and not one number moves. The obvious corruption
test therefore shows nothing and the conclusion is "clean". Corrupt ADDITIVELY instead.

WHAT THIS IS FOR. Amendment 3 found two ANTI-GUARDS among the frozen gates -- statistics whose measured
denominator means corrupting the data can make them EASIER to satisfy. G2's corner spread is one, and it is the
universality headline. A gate that gets greener as the data gets worse is not weak, it is pointing the wrong
way. This measures which gates actually notice damage.
"""

import json
import sys
from importlib import import_module
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np

from curvlib import RESULTS

cl = import_module("181_corner_lib")
RS = [5, 6, 7, 8, 10, 11, 13, 16, 18, 22, 25, 30]


def gates_from(S_by):
    """Recompute G1/G2/G3 from a dict {(reg, shape): (S, P)}."""
    a60, a120, alph, atri = {}, {}, {}, {}
    for reg in cl.REGULATORS:
        for shape, n in (("hex", 6), ("tri", 3)):
            S, P = S_by[(reg, shape)]
            a, b, g, r2, _ = cl.fit_area_log(RS, P, S)
            (a120 if shape == "hex" else a60)[reg] = -b / n
            (alph if shape == "hex" else atri)[reg] = a
    sp = lambda d: (max(d.values()) - min(d.values())) / abs(np.mean(list(d.values())))
    g1 = max(abs(atri[r] - alph[r]) / abs((atri[r] + alph[r]) / 2) for r in cl.REGULATORS)
    return {"G1_worst_rel": g1, "G1_pass": bool(g1 < 0.05),
            "spread_a60": sp(a60), "spread_a120": sp(a120), "area_spread": sp(alph),
            "G3_pass": bool(sp(alph) > 10 * max(sp(a60), sp(a120)))}


def main():
    print("baseline...")
    base = {}
    for reg in cl.REGULATORS:
        X, P = cl.correlators(reg)
        for shape in ("hex", "tri"):
            S, PR = [], []
            for R in RS:
                sites = cl.hexagon(R, R, R) if shape == "hex" else cl.triangle(R)
                s, _ = cl.entropy(sites, X, P)
                S.append(s); PR.append(cl.perimeter(sites))
            base[(reg, shape)] = (np.array(S), np.array(PR, float))
    g0 = gates_from(base)
    print(f"  G1 {g0['G1_worst_rel']:.4%} pass={g0['G1_pass']} | a120 spread {g0['spread_a120']:.3%} | "
          f"area {g0['area_spread']:.2%} | G3 pass={g0['G3_pass']}")

    rows = {"baseline": g0}

    # --- CONTROL: multiplicative rescale. Every ratio MUST be invariant -- if a gate moves, it is not a ratio. ---
    mult = {k: (S * 1.5, P) for k, (S, P) in base.items()}
    rows["multiplicative_x1p5"] = gates_from(mult)
    print(f"\nMULTIPLICATIVE x1.5 (the test that shows nothing, by construction):")
    m = rows["multiplicative_x1p5"]
    print(f"  G1 {m['G1_worst_rel']:.4%} | a120 spread {m['spread_a120']:.3%} | area {m['area_spread']:.2%}"
          f"   -> {'INVARIANT, as predicted' if abs(m['spread_a120']-g0['spread_a120'])<1e-9 else 'moved'}")

    # --- ADDITIVE mutations of increasing severity, applied to ONE regulator ---
    print("\nADDITIVE corruption of one regulator's hexagon entropies (does any gate notice?):")
    for amp in (1e-4, 1e-3, 1e-2, 1e-1):
        mut = dict(base)
        S, P = base[("quartic", "hex")]
        rng = np.random.default_rng(0)
        mut[("quartic", "hex")] = (S + rng.normal(0, amp, len(S)), P)
        r = gates_from(mut)
        rows[f"additive_{amp:g}"] = r
        caught = [n for n, ok in (("G1", r["G1_pass"]), ("G3", r["G3_pass"])) if not ok]
        print(f"  amp {amp:.0e}: G1 {r['G1_worst_rel']:.3%} | a120 spread {r['spread_a120']:.2%} "
              f"(was {g0['spread_a120']:.3%}) | caught by: {caught or 'NOTHING'}")

    # --- the anti-guard demonstration: does damage make the HEADLINE easier? ---
    print("\nANTI-GUARD CHECK -- does corrupting the data make the corner spread SMALLER (easier to claim)?")
    mut = dict(base)
    for reg in cl.REGULATORS:                       # inflate every a(120) equally -> spread shrinks
        S, P = base[(reg, "hex")]
        mut[(reg, "hex")] = (S - 0.02 * np.log(RS), P)
    r = gates_from(mut)
    rows["antiguard_inflate_all"] = r
    print(f"  adding a COMMON spurious log to every regulator: a120 spread "
          f"{g0['spread_a120']:.3%} -> {r['spread_a120']:.3%}   "
          f"{'SPREAD SHRANK -- the headline got EASIER on corrupted data' if r['spread_a120'] < g0['spread_a120'] else 'spread grew'}")

    out = {"why_additive": ("a common multiplicative rescale leaves every ratio exactly invariant, so the "
                            "obvious corruption test shows nothing and the conclusion is 'clean'"),
           "rows": rows,
           "antiguard_confirmed": bool(rows["antiguard_inflate_all"]["spread_a120"] < g0["spread_a120"])}
    (RESULTS / "186_corner_mutation.json").write_text(json.dumps(out, indent=1))
    print("\nsaved results/186_corner_mutation.json")


if __name__ == "__main__":
    main()
