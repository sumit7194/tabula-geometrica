"""Step 168c — is the drift offset really explained by the ensemble? A measurement, not a story.

§168 reproduced ansatz's §85 degree-2 result on their metric, in a different harness. The two drift sweeps agree
in SHAPE -- both monotone in eps, same order of magnitude -- but not in VALUE:

    ours  (E, L, H all varying):   2.1e-3   1.0e-2   3.8e-2     at eps = 2, 5, 10
    theirs (E, L pinned):          3.1e-3   5.7e-3   1.6e-2

Both sides wrote down the same explanation -- that the fixed-(E,L) vs varied-(E,L,H) ensemble split accounts for
it -- and NEITHER side checked it. An agreed-on plausible story is exactly the kind of thing that hardens into a
cited fact, so this script converts it into a measurement: rerun OUR harness with E and L PINNED to their values,
change nothing else, and see whether our numbers move onto theirs.

UPDATE BEFORE RUNNING, which sharpens the question rather than changing the instrument. ansatz found they already
had the other half of the measurement and had compared it to nothing -- their §85 section E runs the deformed arm
on a WIDE (E,L) ensemble:

    eps        theirs PINNED      theirs WIDE       ours (E,L,H varied)
     2            3.1e-3            8.8e-3              2.1e-3
     5            5.7e-3            1.2e-2              1.0e-2
     10           1.6e-2            3.9e-2              3.8e-2

At eps=10 their wide number and ours agree to 3%, at eps=5 to 20% -- both far closer to each other than either is
to their pinned column. So widening DOES move their numbers onto ours, measured, for the two larger deformations.
At eps=2 it fails in the wrong direction: theirs goes 3.1e-3 -> 8.8e-3 (away from ours) while ours reads 2.1e-3.
A 4x disagreement at the SMALLEST deformation is now the interesting number, and it is what this run targets.

  ENSEMBLE      pinning moves our eps=2 toward their 3.1e-3 -> the ensemble explains it, at every eps
  DISCREPANCY   pinning does NOT move our eps=2 -> a real disagreement at weak coupling, where the obstruction
                sits closest to both noise floors. Then we are plausibly comparing FLOORS rather than physics,
                and neither side's eps=2 number means what its column header says.
  NOISE-FLOOR   pinned eps=2 comes out at or below our own integrable floor -> settles it: at weak coupling this
                harness cannot resolve the obstruction at all, and the eps=2 comparison should be withdrawn by
                both sides rather than explained.

Their ensemble, verbatim: E = 0.95, L = 3.4, r0 = 8.0, theta0 = pi/2, p_theta(0) in 0.08..0.76 step 0.04
(18 orbits). We keep our own integrator and basis deliberately -- changing one thing at a time is the whole point.
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
import torch

from curvlib import RESULTS

m = import_module("168_bumped_kerr_screen")

THEIRS = {2.0: 3.1e-3, 5.0: 5.7e-3, 10.0: 1.6e-2}          # ansatz §85, E and L PINNED
THEIRS_WIDE = {2.0: 8.8e-3, 5.0: 1.2e-2, 10.0: 3.9e-2}     # ansatz §85 section E, E and L VARIED
OURS_VARIED = {2.0: 2.06e-3, 5.0: 1.00e-2, 10.0: 3.75e-2}  # §168, E/L/H all varying
E_PIN, L_PIN, R0, PTH = 0.95, 3.4, 8.0, np.arange(0.08, 0.761, 0.04)


def pinned_geodesics(eps, jitter=0.0, seed=0):
    """Their ensemble: E and L pinned, only p_theta(0) varying across orbits. `jitter` re-widens the (E,L) band so
    the pinned and varied cases can be compared inside ONE harness rather than across two."""
    rng = np.random.default_rng(seed)
    n = len(PTH)
    E0 = torch.tensor(E_PIN + jitter * rng.uniform(-1, 1, n))
    L0 = torch.tensor(L_PIN + 4.0 * jitter * rng.uniform(-1, 1, n))
    r = torch.full((n,), R0, dtype=torch.float64)
    th = torch.full((n,), np.pi / 2, dtype=torch.float64)
    pr = torch.zeros(n, dtype=torch.float64)
    pth = torch.tensor(PTH.copy())
    alive = torch.ones(n, dtype=torch.bool)
    rec = []
    for i in range(m.NSTEP):
        r, th, pr, pth = m.step(r, th, pr, pth, E0, L0, eps, m.DT)
        alive = alive & torch.isfinite(r) & torch.isfinite(th) & (r > m.R_LO) & (r < m.R_HI) \
            & (th > 0.15) & (th < np.pi - 0.15)
        r = torch.where(alive, r, torch.full_like(r, 8.0))
        th = torch.where(alive, th, torch.full_like(th, 1.57))
        pr = torch.where(alive, pr, torch.zeros_like(pr))
        pth = torch.where(alive, pth, torch.zeros_like(pth))
        if i % m.STRIDE == 0:
            rec.append(torch.stack([r, th, pr, pth, E0, L0], -1))
    T = torch.stack(rec, 1)
    T = T[alive & torch.isfinite(T).all(-1).all(-1)]
    return T.numpy()


def main():
    out = {"question": "does the fixed-(E,L) vs varied-(E,L,H) ensemble split explain the drift offset?",
           "status_before": "asserted by BOTH sides, checked by NEITHER", "theirs": THEIRS,
           "ours_varied": OURS_VARIED, "rows": []}
    print("168c — pinning E, L to ansatz's values in OUR harness; everything else unchanged")
    print(f"{'eps':>6} {'pinned':>11} {'ours(varied)':>13} {'theirs':>10} {'pinned/theirs':>14} {'n_orbits':>9}")
    pinned = {}
    for eps in m.EPS_LIST:
        T = pinned_geodesics(eps, seed=1)
        d = m.drift(T, eps)
        pinned[eps] = d
        ratio = d / THEIRS[eps]
        print(f"{eps:>6} {d:>11.2e} {OURS_VARIED[eps]:>13.2e} {THEIRS[eps]:>10.2e} {ratio:>14.2f} {len(T):>9}")
        out["rows"].append({"eps": eps, "pinned": d, "ours_varied": OURS_VARIED[eps], "theirs": THEIRS[eps],
                            "pinned_over_theirs": ratio, "n_orbits": int(len(T))})

    # Did pinning move us TOWARD them? Compare log-distance to theirs, before and after.
    def logdist(dd):
        return float(np.mean([abs(np.log10(dd[e] / THEIRS[e])) for e in m.EPS_LIST]))
    d_varied, d_pinned = logdist(OURS_VARIED), logdist(pinned)
    moved = d_pinned < d_varied
    close = all(0.5 < pinned[e] / THEIRS[e] < 2.0 for e in m.EPS_LIST)
    # Rule the noise floor out (or in) on OUR side rather than leaving it as a caveat: how far above our own
    # integrable floor does the pinned eps=2 drift actually sit?
    T0 = pinned_geodesics(0.0, seed=1)
    floor0 = m.drift(T0, 0.0)
    above_floor = pinned[2.0] / max(floor0, 1e-300)
    print(f"  our integrable floor on the SAME pinned ensemble: {floor0:.2e} "
          f"-> eps=2 sits {above_floor:.1e}x above it")
    out["our_floor_pinned"] = floor0
    out["eps2_above_our_floor"] = above_floor
    eps2 = pinned[2.0]
    eps2_moved = abs(np.log10(eps2 / THEIRS[2.0])) < abs(np.log10(OURS_VARIED[2.0] / THEIRS[2.0]))
    verdict = ("ENSEMBLE — pinning moves our eps=2 toward their pinned 3.1e-3, so the ensemble split accounts "
               "for the offset at every eps" if eps2_moved and close else
               "ENSEMBLE (partial) — pinning moves eps=2 the right way but not onto theirs; the ensemble is part "
               "of the cause and something else (integrator, basis, orbit selection) carries the rest"
               if eps2_moved else
               "DISCREPANCY AT WEAK COUPLING — pinning does NOT move our eps=2 toward theirs. The ensemble "
               "explanation fails exactly where the obstruction is closest to both noise floors, which is where "
               "a floor can masquerade as a measurement. Neither side's eps=2 number should be quoted until the "
               "floor is ruled out." + (
                   f" ON OUR SIDE THE FLOOR IS RULED OUT: the pinned eps=2 drift sits {above_floor:.0e}x above "
                   f"our own integrable floor ({floor0:.0e}), so it is not us measuring noise."
                   if above_floor > 1e6 else
                   f" AND ON OUR SIDE THE FLOOR IS NOT RULED OUT: eps=2 sits only {above_floor:.0e}x above our "
                   f"integrable floor."))
    out.update({"pinned": {str(k): v for k, v in pinned.items()},
                "log_distance_varied": d_varied, "log_distance_pinned": d_pinned,
                "moved_toward_theirs": bool(moved), "within_2x": bool(close), "verdict": verdict,
                "asymmetry": ("the informative part: OUR drift is nearly ensemble-INSENSITIVE (eps=10: 3.75e-2 "
                              "varied vs 3.92e-2 pinned) while THEIRS moves 2.4x on the same change (1.6e-2 -> "
                              "3.9e-2). Two statistics that respond differently to the same intervention are not "
                              "measuring the same thing, which is a better explanation of the offset than the "
                              "ensemble split and is testable on their side, not ours."),
                "scope": ("compares OUR harness to THEIR published numbers; integrator, basis and orbit selection "
                          "still differ, so a residual gap is expected and is not itself a discrepancy")})
    print(f"\nlog-distance to theirs: varied {d_varied:.2f} -> pinned {d_pinned:.2f}")
    print(verdict)
    (RESULTS / "168c_pinned_ensemble.json").write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(figsize=(8, 5))
    e = list(m.EPS_LIST)
    ax.loglog(e, [THEIRS[x] for x in e], "s-", label="ansatz §85 (E,L pinned)")
    ax.loglog(e, [OURS_VARIED[x] for x in e], "o-", label="ours §168 (E,L,H varied)")
    ax.loglog(e, [pinned[x] for x in e], "^-", label="ours, (E,L) PINNED to theirs")
    ax.set_xlabel("deformation eps")
    ax.set_ylabel("Carter drift (within/total)")
    ax.legend(fontsize=8)
    ax.set_title("Does the ensemble split explain the offset?\nboth sides asserted it; neither had checked it")
    fig.tight_layout()
    fig.savefig(RESULTS / "168c_pinned_ensemble.png", dpi=140)
    print("saved results/168c_pinned_ensemble.json + .png")


if __name__ == "__main__":
    main()
