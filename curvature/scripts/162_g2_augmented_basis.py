"""Step 162 — R1: move the basis, see if the boundary moves (TheBridge round-9 falsification-v2).

Round 8 (§161) ran the §127/§132/§144 emit-or-certify legibility instrument BLIND on ansatz's two adversarial metrics:
Candidate A -> LEGIBLE (exact quadratic/Killing-tensor invariant, 2.2e-19); Candidate B -> ILLEGIBLE relative to
{polynomial, rational} up to momentum degree 6 (best 2.2e-5, a monotone-non-converging degree sequence = the §97/§160
signature of a polynomial APPROXIMATING a non-polynomial invariant). The corrected claim: legible <-> the invariant is
representable IN THE PROBE'S BASIS. Round 9 R1: rerun B's probe with an AUGMENTED basis and report the residual-vs-basis
curve, blind (the _SEALED files stay closed; B's Hamiltonian is reused verbatim from §161).

THE SHARPENING (pre-registered before running). Round 8's OWN diagnostic pins the transcendence in the MOMENTA (B's
polynomial-in-momenta degree ladder descends without converging). So the ask's requested "log coordinate terms" (R1a)
extend the wrong axis: they enrich the COORDINATE COEFFICIENTS while the momenta stay polynomial -- that cannot represent
a momentum-transcendental invariant. The axis that can is extending the MOMENTUM function class (§160's transcendental
rung). R1 therefore runs BOTH and separates them, which is the actual content of "which kind of representability matters."

Arms (same §99 engine, same B ensemble as §161, held-out variance ratio):
  1. POLYNOMIAL (control)          -- momentum monomials deg{2,4,6} x coordinate polynomials. Reproduces round 8 (illegible).
  2. RATIONAL                      -- + 1/x^2, 1/(1+x^2), 1/(1+y^2) coordinate coefficients (round-8 arm, reconfirmed).
  3. LOG-COORDINATE (R1a, requested)-- + log(2+(x+y)^2), log(1+y^2), log(1+x^2), log(1+(x+y)^2) coordinate coefficients,
                                       momenta still polynomial. Pre-registered sub-prediction: does NOT emit (wrong axis).
  4. TRANSCENDENTAL-MOMENTUM SCAN  -- the axis that CAN: features exp(a px^2 + b py^2 + g px py) x coordinate polys,
                                       scanned over a grid of (a,b,g), best member kept (§160's posit-a-family-then-fit).
                                       EMIT if some member is conserved to machine precision (< 1e-8).

Two clean outcomes, both pre-registered (a miss is a finding):
  - some augmented arm EMITS (< 1e-8, flat) -> "legible <-> representable-in-basis" CONFIRMED, and we have MEASURED which
    basis unlocks B (and on which axis -- coordinate vs momentum);
  - every arm stays illegible (>> 1e-8) -> the obstruction is deeper than the bases tried; report the residual-vs-basis
    curve as the evidence (transcendental invariants resist linear probing beyond the families searched).

Gates are METHODOLOGICAL (a falsification test; the outcome is reported, not gated):
  G0 INTEGRATOR: B's H2 conserved along the flow to < 1e-7 (else every "certify" is confounded by integration error).
  G1 CONTROL REPRODUCES ROUND 8: the polynomial arm is illegible (best held-out > 1e-6) with a monotone-non-converging
     degree sequence -- the run is commensurable with §161.
  G2 AUGMENTED CHARACTERIZED: every augmented arm's best held-out is reported, and the verdict is decided by the same
     RELATIVE-EXACTNESS rule as §160 (EMIT = machine-precision + flat; CERTIFY-RELATIVE-TO-BASIS otherwise), naming the
     families searched. The residual-vs-basis curve is the deliverable.
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

s161 = import_module("161_g2_blind_legibility")
s99 = import_module("99_deformed_metrics")

EMIT = 1e-8                                            # machine-precision emit (relative-exactness, §160)


def coord_families(x, y, rational=False, log=False):
    fam = [(np.ones_like(x), "1"), (x, "x"), (y, "y"), (x ** 2, "x2"), (x * y, "xy"), (y ** 2, "y2")]
    if rational:
        fam += [(1 / (1 + x ** 2), "1/(1+x2)"), (1 / (1 + y ** 2), "1/(1+y2)"),
                (1 / (2 + (x + y) ** 2), "1/(2+(x+y)2)")]
    if log:                                            # log of the metric/potential factors (R1a)
        fam += [(np.log(2 + (x + y) ** 2), "log(2+(x+y)2)"), (np.log(1 + y ** 2), "log(1+y2)"),
                (np.log(1 + x ** 2), "log(1+x2)"), (np.log(1 + (x + y) ** 2), "log(1+(x+y)2)")]
    return fam


def build(traj, deg, rational=False, log=False, expo=None):
    T = traj.numpy()
    x, y, px, py = T[:, 0, :].T, T[:, 1, :].T, T[:, 2, :].T, T[:, 3, :].T   # (ntraj, nstep)
    fam = coord_families(x, y, rational, log)
    feats, names = [], []
    # momentum monomials (even total degree) x coordinate families
    for a in range(deg + 1):
        for b in range(deg + 1 - a):
            if 1 <= a + b <= deg and (a + b) % 2 == 0:
                mv = (px ** a) * (py ** b)
                for cv, cn in fam:
                    feats.append(mv * cv); names.append(f"px{a}py{b}*{cn}")
    if expo is not None:                               # transcendental-momentum feature at family member expo=(a,b,g)
        a, b, g = expo
        e = np.exp(a * px ** 2 + b * py ** 2 + g * px * py)
        for cv, cn in fam[:6]:
            feats.append(e * cv); names.append(f"exp({a:.2f}px2+{b:.2f}py2+{g:.2f}pxpy)*{cn}")
    for cv, cn in [(x ** 2, "x2"), (y ** 2, "y2"), (x * y, "xy"), (x ** 4, "x4"), (y ** 4, "y4")]:
        feats.append(cv); names.append(cn)            # pure-coordinate terms
    return np.stack(feats, -1), names


def best(tr, te, **kw):
    Ftr, names = build(tr, **kw); Fte, _ = build(te, **kw)
    ev, C, mu, sd = s99.conserved(Ftr)
    bo = np.inf
    for k in range(min(6, C.shape[1])):
        ho = s99.heldout(Fte, C[:, k], mu, sd)
        bo = min(bo, ho)
    return float(bo)


def main():
    # B ensemble (same as §161: train seed s, test seed s+100), median over seeds
    print("integrating Candidate B (reused from 161)...")
    ens = {}
    drifts = []
    for s in s161.SEEDS:
        tr, dtr, ntr = s161.ensemble_B(s)
        te, dte, nte = s161.ensemble_B(s + 100)
        ens[s] = (tr, te); drifts += [dtr, dte]
    drift = float(max(drifts))
    G0 = bool(drift < 1e-7)
    print(f"G0 integrator: max H2 drift {drift:.1e} -> {G0}")

    def arm(**kw):
        return float(np.median([best(ens[s][0], ens[s][1], **kw) for s in s161.SEEDS]))

    curve = {}
    # 1 polynomial control, 2 rational, 3 log-coordinate -- momentum degree ladder
    for label, kw in [("polynomial", {}), ("rational", {"rational": True}), ("log_coordinate", {"log": True})]:
        curve[label] = {f"deg{d}": arm(deg=d, **kw) for d in (2, 4, 6)}
        seq = [curve[label][f"deg{d}"] for d in (2, 4, 6)]
        print(f"  {label:16s} deg 2/4/6: [{', '.join(f'{h:.2e}' for h in seq)}]")

    # 4 transcendental-momentum scan (posit exp(a px^2 + b py^2 + g px py), fit inside each member)
    fast = "--fast" in sys.argv                        # coarse scan for verify.sh (the gates are scan-independent)
    print(f"  transcendental-momentum scan{' (fast)' if fast else ''}...")
    grid = np.linspace(-1.2, 1.2, 3 if fast else 7)
    gg = (0.0,) if fast else (-0.6, 0.0, 0.6)
    scan_best, scan_arg = np.inf, None
    for a in grid:
        for b in grid:
            for g in gg:
                if a == 0 and b == 0 and g == 0:
                    continue
                h = arm(deg=2, expo=(a, b, g))
                if h < scan_best:
                    scan_best, scan_arg = h, (float(a), float(b), float(g))
    curve["transcendental_momentum_scan"] = {"best": scan_best, "argmin_abg": scan_arg}
    print(f"  transcendental-momentum scan: best {scan_best:.2e} at (a,b,g)={scan_arg}")

    poly_seq = [curve["polynomial"][f"deg{d}"] for d in (2, 4, 6)]
    G1 = bool(min(poly_seq) > 1e-6 and poly_seq[0] > poly_seq[1] > poly_seq[2])   # illegible + monotone-non-converging
    arms_best = {"polynomial": min(poly_seq),
                 "rational": min(curve["rational"].values()),
                 "log_coordinate": min(curve["log_coordinate"].values()),
                 "transcendental_momentum_scan": scan_best}
    emitters = [k for k, v in arms_best.items() if v < EMIT]
    log_helps = bool(arms_best["log_coordinate"] < EMIT)
    G2 = bool(all(np.isfinite(v) for v in arms_best.values()))

    if emitters:
        verdict_kind = f"EMIT via {emitters[0]}"
        headline = ("legible <-> representable-in-basis CONFIRMED for Candidate B: the {} basis emits an invariant "
                    "conserved to {:.1e} (machine precision) -- the boundary MOVED with the basis, and it is the {} axis "
                    "that unlocks it (the polynomial/rational/log-coordinate arms stay illegible, best {:.1e})."
                    .format(emitters[0], arms_best[emitters[0]],
                            "MOMENTUM" if "momentum" in emitters[0] else "COORDINATE",
                            min(v for k, v in arms_best.items() if k not in emitters)))
    else:
        verdict_kind = "CERTIFY-RELATIVE-TO-ALL-BASES-TRIED"
        headline = ("Candidate B stays ILLEGIBLE across every basis tried -- polynomial ({:.1e}), rational ({:.1e}), "
                    "log-coordinate ({:.1e}), and a transcendental-MOMENTUM scan exp(a px^2+b py^2+g px py) ({:.1e} at "
                    "{}). The requested log-COORDINATE augmentation does NOT move the boundary, exactly as pre-registered: "
                    "round 8's diagnostic put the transcendence in the MOMENTA, and coordinate-coefficient logs keep the "
                    "momenta polynomial. The momentum scan is the right axis but its finite exp(quadratic) family does not "
                    "contain B's invariant -> the obstruction is deeper than the families searched (a real finding: B's "
                    "transcendental invariant resists linear probing beyond a posited family; naming the exact family is "
                    "the un-blind step the bridge holds)."
                    .format(arms_best["polynomial"], arms_best["rational"], arms_best["log_coordinate"],
                            scan_best, scan_arg))

    out = {"candidate": "B", "blind": True, "engine": "99_deformed_metrics (leg-Q, unchanged)",
           "G0_integrator_drift": drift, "residual_vs_basis": curve, "arms_best": arms_best,
           "emitters": emitters, "log_coordinate_helps": log_helps, "verdict": verdict_kind,
           "G0_integrator": G0, "G1_control_reproduces_round8": G1, "G2_augmented_characterized": G2,
           "r1_done": bool(G0 and G1 and G2),
           "headline": headline,
           "for_bridge": ("R1 residual-vs-basis for Candidate B, blind. " + headline + " Sharpening (the actual content): "
                          "'representable-in-basis' has an AXIS -- extending the coordinate-coefficient class (rational, "
                          "log) is NOT the same as extending the momentum function class; round 8 localized B's "
                          "transcendence in the momenta, so only the latter axis can matter. Blind leg-Q implication "
                          "unchanged: if B is sealed-integrable via a transcendental-in-momenta invariant, my instrument "
                          "misses it in every polynomial/rational/log-coordinate basis and in a first exp(quadratic) "
                          "momentum family -- localizing the biconditional's break to 'invariants representable in the "
                          "probe's MOMENTUM basis', not integrability per se. The bridge unseals + scores.")}
    print(f"\nVERDICT: {verdict_kind}")
    print(f"G0 {G0} | G1 control-reproduces {G1} | G2 characterized {G2} -> R1 methodologically sound: {out['r1_done']}")
    (RESULTS / "162_g2_augmented_basis.json").write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(figsize=(9, 5.2))
    degs = [2, 4, 6]
    for label, col in [("polynomial", "gray"), ("rational", "steelblue"), ("log_coordinate", "orange")]:
        ax.plot(degs, [curve[label][f"deg{d}"] for d in degs], "o-", color=col, label=f"{label} (best {arms_best[label]:.1e})")
    ax.axhline(scan_best, ls="--", color="crimson", label=f"transc.-momentum scan best {scan_best:.1e}")
    ax.axhline(EMIT, ls=":", color="k", lw=0.8, label="emit floor (machine precision)")
    ax.set_yscale("log"); ax.set_xlabel("momentum degree"); ax.set_ylabel("best held-out variance ratio (log)")
    ax.set_xticks(degs); ax.legend(fontsize=8)
    ax.set_title("R1 — Candidate B: residual vs basis (blind)\nlog-COORDINATE ≠ transcendental-MOMENTUM: 'representable-in-basis' has an axis")
    fig.tight_layout(); fig.savefig(RESULTS / "162_g2_augmented_basis.png", dpi=140)
    print("saved results/162_g2_augmented_basis.json + .png")


if __name__ == "__main__":
    main()
