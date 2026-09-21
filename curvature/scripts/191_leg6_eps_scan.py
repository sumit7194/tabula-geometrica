"""Step 191 — leg 6 follow-up: the epsilon SCALING EXPONENT as the discriminator.

NOT BLIND. The key was unsealed before this ran: A keeps Carter at FIRST ORDER in eps, B destroys it, C keeps
it rationally. ansatz corrected their own scope -- a first-order invariant leaves an O(eps^2) residual at
finite eps, so at eps=0.05 the test could not separate A from B, and my CERTIFY on A is not a false positive.

The discriminator is the EXPONENT, not the magnitude (TheBridge). Corrected here: the reported margin is
heldout = mean_traj(var_within)/var_total, a VARIANCE, so it goes as the residual amplitude SQUARED --
    A residual O(eps^2) -> margin O(eps^4);  B residual O(eps^1) -> margin O(eps^2).
Predictions frozen in notes/leg6_prereg.md before running, including the outcome where BOTH fit the same
exponent, which would mean the margin measures something common to both metrics that nobody has named.
"""

import json
import sys
from importlib import import_module
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from curvlib import RESULTS

m = import_module("190_leg6_triple")

EPS = [0.05, 0.0158, 0.005, 0.00158, 0.0005]
FLOOR = 1e-16          # instrument floor: the eps=0 control emits at ~1e-17


def main():
    print("Step 191 — leg 6 eps-scan (NOT blind; key already unsealed)\n")
    out = {"prereg": "notes/leg6_prereg.md AMENDMENT (frozen before this ran)",
           "blind": False, "eps_grid": EPS, "floor": FLOOR,
           "predicted": {"A": 4, "B": 2, "note": "margin is a variance -> amplitude squared"},
           "objects": {}}
    for obj in ("A", "B", "C"):
        mins = []
        for ep in EPS:
            g = [m.screen(obj, ep, sd)[1] for sd in (1, 2)]
            med = {k: float(np.nanmedian([x[k] for x in g])) for k in g[0]}
            mins.append(float(np.nanmin(list(med.values()))))
            print(f"  {obj}  eps={ep:<8} min heldout {mins[-1]:.4e}")
        e = np.array(EPS); y = np.array(mins)
        ok = y > FLOOR                                     # censoring guard: drop points at the floor
        ncens = int((~ok).sum())
        if ok.sum() >= 3:
            slope, icpt = np.polyfit(np.log10(e[ok]), np.log10(y[ok]), 1)
            pred = icpt + slope * np.log10(e[ok])
            ss = 1 - np.sum((np.log10(y[ok]) - pred) ** 2) / max(np.var(np.log10(y[ok])) * ok.sum(), 1e-30)
        else:
            slope, ss = float("nan"), float("nan")
        out["objects"][obj] = {"eps": EPS, "min_heldout": mins, "n_censored_at_floor": ncens,
                               "fitted_exponent": float(slope), "fit_R2": float(ss)}
        print(f"     -> fitted exponent {slope:.3f}   (R2 {ss:.4f}, {ncens} point(s) censored at floor)\n")
    A, B = out["objects"]["A"]["fitted_exponent"], out["objects"]["B"]["fitted_exponent"]
    ratios = [out["objects"]["B"]["min_heldout"][i] / out["objects"]["A"]["min_heldout"][i]
              for i in range(len(EPS))]
    out["B_over_A"] = ratios
    print("  B/A across eps:", " ".join(f"{x:.2f}" for x in ratios))
    if abs(A - 4) < 1.0 and abs(B - 2) < 1.0:
        out["verdict"] = ("(i) FINITE-EPSILON CONFIRMED: A fits ~4 and B fits ~2 as predicted, so A's Carter "
                          "survives at first order and B's does not -- the screen DOES detect the property, "
                          "and eps=0.05 was simply too coarse to show it.")
    elif abs(A - B) < 0.7:
        out["verdict"] = (f"(iii) SAME EXPONENT (A {A:.2f}, B {B:.2f}): B/A stays flat across eps, so the "
                          f"margin is dominated by something COMMON to both metrics that neither party has "
                          f"named. This was pre-registered as a real outcome and is the informative one.")
    else:
        out["verdict"] = (f"(ii) NEITHER PREDICTION: A {A:.2f}, B {B:.2f}. The exponents split but not as "
                          f"predicted; reported as a number, not explained tonight.")
    (RESULTS / "191_leg6_eps_scan.json").write_text(json.dumps(out, indent=2))
    print("\n" + out["verdict"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
