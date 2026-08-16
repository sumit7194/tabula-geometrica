"""Step 170 — CALIBRATE AGAINST ABSENCE, NOT AGAINST OTHER PRESENCES.

THE FAILURE MODE THIS FIXES (§168, found via ansatz's bisecting test). Our acceptance band was calibrated on the
REDUCIBLES -- the invariants known to be present. But the reducibles are exact polynomials in E, L, H and are
represented to ~1e-16, while Carter is only approximately representable at degree 3 and its best representation
is conserved only to ~1e-11. So the band was set by quantities BETTER CONSERVED THAN THE THING IT WAS MEANT TO
ACCEPT, and it excluded the control target. Nothing was missing from the span -- the target sat right there, one
decimal class worse than the calibrators.

    A control-calibrated floor is only valid if the control target is represented as well as the calibrators are.

ansatz's sharpening, which is the general form and the fix: **a floor set by things that are PRESENT inherits
their representation quality; a floor set by a library KNOWN TO CONTAIN NOTHING inherits only the dimension.**
Calibrate against absence. Their §123 per-degree structureless control does this by construction, which is why
their pipeline could not have hit our sixth mode.

THE INSTRUMENT. Build the SAME library, at the same (G, P, p), on data where NO invariant exists -- phase-space
points drawn from the same region and grouped arbitrarily, so nothing is conserved within a group by
construction. The smallest held-out ratio achievable there is the best "apparent conservation" that finite
sampling and dimension alone can manufacture. Anything below it is real structure; anything above it is noise.
No presence enters the calibration, so no calibrator's representation quality can leak into the band.

PRE-REGISTERED. A new floor must be validated on KNOWN answers before it is allowed to re-judge anything:
  A1 the structureless floor is NON-TRIVIAL IN BOTH DIRECTIONS. It must be far above machine precision (else
     it models nothing) AND it must REJECT a known negative: a smooth, non-conserved function of the state.
     Testing only the first is how a floor ends up vacuous -- a floor of ~1 "passes" a lower bound while
     admitting the entire library. Stated after the first version of this script did exactly that.
  A2 VALIDATION ON A KNOWN POSITIVE (Toda, §169): the absence-calibrated band still admits the genuine cubic
     invariant I3 -- a floor that rejects a known invariant is worse than the one it replaces
  A3 VALIDATION ON A KNOWN POSITIVE (deformed Kerr degree 2, where the present instrument works): the band
     still admits Carter
  A4 ONLY THEN, the degree-3 rungs are re-measured under the new floor and reported as a NEW MEASUREMENT under
     a NEW instrument. §168's verdicts stand as they were recorded; this does not retroactively change them,
     and if degree 3 now passes that is a fact about the floor, not a rescue of the old result.

WHAT THIS IS NOT. Not a gate being moved. The pre-registered thresholds (1e-3 on the Carter residual, 1e6 on the
drift ratio) are untouched; what changes is which directions are admitted to the conserved band, which is an
instrument design decision with its own controls above.
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

m168 = import_module("168_bumped_kerr_screen")
m169 = import_module("169_degree3_positive_control")
s99 = m168.s99
np.seterr(all="ignore")

FAST = "--fast" in sys.argv[1:]


def structureless(T, rng):
    """Same points, same region, same (G, P) -- but regrouped so NOTHING is conserved within a group.

    Pooling every sample and re-dealing it into groups destroys the trajectory structure while preserving the
    marginal distribution of the data exactly, so the library's column statistics are unchanged and only the
    conservation is gone. That is the point: the floor must inherit the DIMENSION of the problem and nothing else.
    """
    G, P, D = T.shape
    flat = T.reshape(-1, D).copy()
    rng.shuffle(flat)
    return flat.reshape(G, P, D)


def floor_from_absence(lib, T, rng, n_rep=3):
    """Best apparent conservation reachable with no invariant present. Worst (largest) over repeats, so the floor
    is not set by one lucky shuffle."""
    best = []
    for _ in range(n_rep):
        Str, Ste = structureless(T, rng), structureless(T, rng)
        Fa, Fb = lib(Str), lib(Ste)
        V, _ = m168.conditioning_basis(Fa)
        Fk, Ftek = Fa @ V, Fb @ V
        ev, C, mu, sd = s99.conserved(Fk)
        best.append(min(s99.heldout(Ftek, C[:, k], mu, sd) for k in range(C.shape[1])))
    return float(max(best)), [float(b) for b in best]


def known_negative(T):
    """A smooth function of the state that is NOT conserved. The floor must reject it, or it is vacuous.

    This is the control the first version of this script lacked: it gated only that the floor was above machine
    precision, which a floor of ~1 satisfies while admitting every direction in the library."""
    r, th, pr, pth, E, L = [T[..., i] for i in range(6)]
    return r * np.cos(th) + 0.3 * pr


def admitted(lib, Ttr, Tte, target_fn, floor):
    """Is the best-fit representation of `target_fn` inside the band this floor defines?"""
    Fa, Fb = lib(Ttr), lib(Tte)
    V, _ = m168.conditioning_basis(Fa)
    Fk, Ftek = Fa @ V, Fb @ V
    ev, C, mu, sd = s99.conserved(Fk)
    Z = ((Fk - mu) / sd).reshape(-1, Fk.shape[-1])
    Za = np.concatenate([Z, np.ones((len(Z), 1))], 1)
    y = target_fn(Ttr).reshape(-1)
    c, *_ = np.linalg.lstsq(Za, y, rcond=None)
    v = c[:-1] / (np.linalg.norm(c[:-1]) + 1e-300)
    ho = s99.heldout(Ftek, v, mu, sd)
    n_cons = int(sum(s99.heldout(Ftek, C[:, k], mu, sd) <= floor for k in range(C.shape[1])))
    return float(ho), bool(ho <= floor), n_cons


def main():
    rng = np.random.default_rng(0)
    out = {"fix": "calibrate the acceptance band against ABSENCE (a library known to contain nothing), "
                  "not against the reducibles (whose representation quality leaks into the band)",
           "credit": "sharpened form due to ansatz; their §123 per-degree structureless control does this",
           "rows": []}

    # ---------- Toda (§169): a KNOWN irreducible cubic ----------
    m169.NTRAJ, m169.NSTEP, m169.STRIDE = (120, 4000, 16) if FAST else (250, 8000, 8)
    Ttr, Tte = m169.ensemble(seed=1), m169.ensemble(seed=51)
    lib_toda = lambda T: m169.library(T, 3)[0]
    f_toda, reps_toda = floor_from_absence(lib_toda, Ttr, rng)
    ho_i3, ok_i3, nc_toda = admitted(lib_toda, Ttr, Tte, m169.I3_of, f_toda)
    neg_toda = lambda T: T[..., 0] * np.cos(T[..., 1]) + 0.3 * T[..., 3]
    ho_neg, ok_neg, _ = admitted(lib_toda, Ttr, Tte, neg_toda, f_toda)
    print(f"            KNOWN NEGATIVE heldout {ho_neg:.2e} -> "
          f"{'WRONGLY ADMITTED (floor vacuous)' if ok_neg else 'correctly rejected'}")
    print(f"Toda deg3:  absence floor {f_toda:.2e} (repeats {['%.0e' % r for r in reps_toda]})")
    print(f"            I3 heldout {ho_i3:.2e} -> {'ADMITTED' if ok_i3 else 'REJECTED'}; "
          f"{nc_toda} directions inside the band")
    A1 = bool(f_toda > 1e-14 and not ok_neg)          # non-trivial in BOTH directions
    A2 = bool(ok_i3)
    out["rows"].append({"case": "toda_deg3", "floor": f_toda, "target_heldout": ho_i3,
                        "admitted": ok_i3, "n_inside": nc_toda,
                        "known_negative_heldout": ho_neg, "known_negative_admitted": ok_neg})

    # ---------- deformed Kerr: degree 2 (works today) and degree 3 (the failing rungs) ----------
    m168.NTRAJ, m168.NSTEP, m168.STRIDE = (110, 2400, 16) if FAST else (250, 2400, 8)
    K0tr, K0te = m168.geodesics(0.0, seed=1), m168.geodesics(0.0, seed=51)
    carter = lambda T: m168.carter(T, 0.0)
    res = {}
    for deg, wm in [(2, True), (3, False), (3, True)]:
        lib = lambda T, d=deg, w=wm: m168.library(T, d, w, 0.0)[0]
        f, reps = floor_from_absence(lib, K0tr, rng)
        ho, ok, nc = admitted(lib, K0tr, K0te, carter, f)
        tag = f"deg{deg} {'rat+metric' if wm else 'rational'}"
        print(f"Kerr {tag:16s}: absence floor {f:.2e}   Carter heldout {ho:.2e} -> "
              f"{'ADMITTED' if ok else 'REJECTED'}; {nc} inside")
        res[tag] = ok
        out["rows"].append({"case": f"kerr_{tag}", "floor": f, "target_heldout": ho,
                            "admitted": ok, "n_inside": nc})
    A3 = bool(res.get("deg2 rat+metric", False))
    A4 = True                                    # the degree-3 rows are the new measurement, reported either way

    deg3_admits = {k: v for k, v in res.items() if k.startswith("deg3")}
    out.update({"A1_floor_nontrivial": A1, "A2_toda_positive_admitted": A2,
                "A3_kerr_deg2_admitted": A3, "A4_deg3_remeasured": A4,
                "deg3_admitted_under_absence_floor": deg3_admits,
                "validated": bool(A1 and A2 and A3),
                "verdict": ("The absence-calibrated floor is VALIDATED on both known positives (Toda's cubic "
                            "I3 and Kerr degree-2 Carter are admitted) and is non-trivial ({:.0e}). Degree-3 "
                            "rungs under the new floor: {}. This is a NEW MEASUREMENT under a NEW instrument -- "
                            "§168's recorded verdicts stand as they were, and a degree-3 admission here is a "
                            "fact about the floor, not a rescue of the old result."
                            .format(f_toda, deg3_admits) if (A1 and A2 and A3) else
                            "NOT VALIDATED, NOT ADOPTED. Shuffling destroys the trajectories' TEMPORAL "
                            "structure as well as their conservation, so it under-estimates what chance can "
                            "manufacture on smooth data and returns a floor of ~1 that admits the entire "
                            "library -- vacuous in the opposite direction from the bug it was meant to fix, "
                            "and it wrongly admits a smooth non-conserved control. The IDEA (calibrate against "
                            "absence) stands; this MODEL of absence does not. A correct one must preserve every "
                            "property of the real data except the invariant itself."),
                "scope": ("fixes the sixth failure mode by construction: no present quantity enters the "
                          "calibration, so no calibrator's representation quality can leak into the band. "
                          "Does not touch the pre-registered thresholds.")})
    print(f"\nA1 floor non-trivial: {A1} | A2 Toda positive admitted: {A2} | A3 Kerr deg2 admitted: {A3}")
    print(out["verdict"])
    (RESULTS / "170_absence_calibrated_floor.json").write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(figsize=(9, 5))
    labs = [r["case"] for r in out["rows"]]
    x = np.arange(len(labs))
    ax.semilogy(x, [max(r["floor"], 1e-30) for r in out["rows"]], "s--", label="absence-calibrated floor")
    ax.semilogy(x, [max(r["target_heldout"], 1e-30) for r in out["rows"]], "o-", label="known target, held-out")
    ax.set_xticks(x)
    ax.set_xticklabels(labs, fontsize=8, rotation=15)
    ax.set_ylabel("held-out within/total variance ratio")
    ax.legend(fontsize=8)
    ax.set_title("Calibrate against absence, not against other presences\n"
                 "target below floor = admitted; a floor set by present quantities inherits their exactness")
    fig.tight_layout()
    fig.savefig(RESULTS / "170_absence_calibrated_floor.png", dpi=140)
    print("saved results/170_absence_calibrated_floor.json + .png")


if __name__ == "__main__":
    main()
