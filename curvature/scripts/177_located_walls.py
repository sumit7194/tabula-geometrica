"""Step 177 — THE FRONTIER REPORTS WHERE THE WALL IS, NOT WHETHER, AND REFUSES WHEN IT CANNOT.

THE IDEA IS NOT NEW AND THE REPO SHOULD SAY SO. §142 already located the contextuality wall by sweeping Werner
visibility until the verdict flipped (v* = 0.725 ~ 1/sqrt2). §176 did the same for CERTIFY-NO-CODE by sweeping
embedding dimension (d* = 6). Two of the frontier's four certify verdicts already report a LOCATION rather than a
label; the other two do not, and nothing in the codebase says when the move is legitimate.

SO THE CONTRIBUTION HERE IS THE UNIFICATION AND, MORE IMPORTANTLY, THE GUARD.

TheBridge tried the §176 upgrade on their escape ladder within the hour of receiving it and it FAILED, for a
reason that is a property of the technique rather than of their data: their swept quantity (orbit survival time)
is CENSORED -- median 200 at every parameter value because 97-98% of orbits hit the integration cap -- so the
"continuous" statistic is a constant with outliers. KS gave p = 0.97 against the binary's Fisher p = 0.12. The
continuous version was STRICTLY WORSE than the boolean it replaced.

    A budget-truncated statistic inherits the truncation and carries LESS information than the boolean verdict,
    because the boolean at least records which side of the cap you landed on.

Our stress quantity is uncensored by construction (bounded below by zero, and it reaches zero) -- which is WHY
§176 worked, and that property was never stated when the technique was passed on. A property that never binds in
your own case is invisible to you and load-bearing for everyone else. So the guard goes IN THE INSTRUMENT: before
reporting a wall, measure the fraction of the swept quantity sitting at its extreme, and ABSTAIN if that fraction
is high. This is the §147 abstain machinery pointed at a new failure mode.

PRE-REGISTERED. Every gate has a known answer from theory, so a located wall is checkable rather than plausible.

  W1 CERTIFY-GAUGE, and this one is a real prediction. Sweep the number of clamped anchor points K. Distance
     data fixes a configuration only up to rigid motions; in 2-D, K=2 anchors pin rotation and translation but
     leave a REFLECTION, and K=3 non-collinear anchors kill it. So the frame should become identifiable exactly
     at K* = 3. §111 used K=4 throughout and never asked where the transition is. Gate: K* == 3.
  W2 CERTIFY-CHAOS. Sweep the logistic map's r through the Feigenbaum accumulation point r_inf = 3.5699456,
     the exact onset of chaos. The 0-1 test statistic K should cross from ~0 to ~1 there. Gate: |r* - r_inf|
     small, and K low below / high above.
  W3 THE GUARD, known-fail. Feed the same locator a deliberately CENSORED quantity -- the identical sweep with
     the statistic clipped at a cap, reproducing TheBridge's situation -- and it must ABSTAIN rather than
     report a wall. Without W3 the guard could not fail and would certify its own correctness.
  W4 THE GUARD MUST NOT BE TRIGGER-HAPPY: it must NOT abstain on W1 or W2, whose quantities are uncensored.
     A guard that abstains on everything is vacuous in the same way §170's floor of ~1 was.

WHAT THIS DOES NOT CLAIM. Locating a wall is not explaining it. K* = 3 is recovered, not derived; the derivation
is the reflection argument above, stated in advance so the number is a check and not a discovery.
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

m145 = import_module("145_regime_detector")
s111 = import_module("111_desitter_anchor")
np.seterr(all="ignore")

FAST = "--fast" in sys.argv[1:]
s111.STEPS = 2500 if FAST else 6000
CENSOR_FRAC_MAX = 0.5          # abstain if this fraction or more of the swept values sit at an extreme
R_INF = 3.5699456              # Feigenbaum accumulation point -- exact onset of chaos in the logistic map


def censored_fraction(vals, tol=1e-3):
    """Fraction of swept values pinned at the sweep's own extreme -- TheBridge's cap test, made general.

    A quantity that varies smoothly has few values at either extreme; one truncated by a budget piles up there.
    Measured on the sweep's own range so no knowledge of the cap's value is needed."""
    v = np.asarray(vals, float)
    lo, hi = v.min(), v.max()
    span = hi - lo
    if span < 1e-12:
        return 1.0                                    # perfectly flat: maximally censored
    at_hi = float(np.mean(np.abs(v - hi) <= tol * span + tol))
    at_lo = float(np.mean(np.abs(v - lo) <= tol * span + tol))
    return max(at_hi, at_lo)


def locate(knobs, vals, thresh, rising):
    """First knob value at which the statistic crosses `thresh`. Returns (wall, abstain, censor_frac)."""
    cf = censored_fraction(vals)
    if cf >= CENSOR_FRAC_MAX:
        return None, True, cf
    for k, v in zip(knobs, vals):
        if (v > thresh) if rising else (v < thresh):
            return k, False, cf
    return None, False, cf


# ---------------- W1: CERTIFY-GAUGE, sweep the anchor count ----------------

def gauge_sweep(Ks, seeds=(0, 1, 2)):
    rng = np.random.default_rng(7)
    Z = rng.uniform(-1, 1, (s111.N, s111.D)).astype(np.float32)
    raws = []
    for K in Ks:
        keep = s111.K_ANCHOR
        s111.K_ANCHOR = K
        try:
            runs = [s111.reconstruct(Z, K > 0, s) for s in seeds]
            E, _ = min(runs, key=lambda r: r[1])
        finally:
            s111.K_ANCHOR = keep
        raw, _ = s111.errors(E, Z)
        raws.append(float(raw))
        print(f"   K={K}  raw frame error {raw:.4f}")
    return raws


# ---------------- W2: CERTIFY-CHAOS, sweep the logistic map ----------------

def logistic(r, n=4000, burn=1000, x0=0.31):
    x = x0
    out = np.empty(n)
    for i in range(burn + n):
        x = r * x * (1 - x)
        if i >= burn:
            out[i - burn] = x
    return out


def chaos_sweep(rs):
    Ks = []
    for r in rs:
        s = logistic(r, n=1500 if FAST else 4000)
        K = float(np.median([m145.zero_one_K(s, seed=j) for j in range(3)]))
        Ks.append(K)
        print(f"   r={r:.4f}  0-1 statistic K {K:.3f}")
    return Ks


def main():
    out = {"contribution": ("unify the located-wall upgrade across the frontier's certify verdicts AND guard it "
                            "against the censoring failure TheBridge measured"),
           "prior_art_in_repo": {"142": "contextuality wall located at v* ~ 1/sqrt2",
                                 "176": "no-code wall located at d* = 6"},
           "credit": "the censoring precondition is TheBridge's, found by testing 176's technique and failing"}

    print("W1 — CERTIFY-GAUGE: sweep the anchor count; theory says the frame is fixed at K* = 3 in 2-D")
    Ks = [0, 1, 2, 3, 4, 5]
    raws = gauge_sweep(Ks)
    gate_g = 0.15                                       # §111's RAW_THRESH: frame recovered
    kstar, ab_g, cf_g = locate(Ks, raws, gate_g, rising=False)
    W1 = bool(kstar == 3 and not ab_g)
    print(f"   -> K* = {kstar}   (theory 3)   censored fraction {cf_g:.2f}")

    print("\nW2 — CERTIFY-CHAOS: sweep the logistic map through r_inf = 3.5699456")
    rs = [3.2, 3.4, 3.5, 3.55, 3.58, 3.6, 3.7, 3.8, 3.9]
    K01 = chaos_sweep(rs)
    rstar, ab_c, cf_c = locate(rs, K01, 0.5, rising=True)
    W2 = bool(rstar is not None and not ab_c and abs(rstar - R_INF) <= 0.06
              and K01[0] < 0.5 < K01[-1])
    print(f"   -> r* = {rstar}   (theory {R_INF:.4f})   censored fraction {cf_c:.2f}")

    print("\nW3 — THE GUARD (known-fail): the same locator on a CENSORED statistic must ABSTAIN")
    cap = 0.35                                          # clip the chaos statistic, reproducing an integration cap
    K_cens = [min(k, cap) for k in K01]
    rstar_c, ab_x, cf_x = locate(rs, K_cens, 0.5, rising=True)
    W3 = bool(ab_x)
    print(f"   censored sweep: {[round(k,3) for k in K_cens]}")
    print(f"   -> abstain {ab_x}   censored fraction {cf_x:.2f}   wall reported: {rstar_c}")

    W4 = bool(not ab_g and not ab_c)
    print(f"\nW4 — the guard did NOT fire on the uncensored sweeps: {W4}")

    ok = bool(W1 and W2 and W3 and W4)
    out.update({"W1_gauge_wall": {"knobs": Ks, "raw_frame_error": raws, "K_star": kstar,
                                  "theory": 3, "censored_fraction": cf_g, "pass": W1},
                "W2_chaos_wall": {"knobs": rs, "zero_one_K": K01, "r_star": rstar,
                                  "theory": R_INF, "censored_fraction": cf_c, "pass": W2},
                "W3_censoring_guard": {"capped_at": cap, "abstained": ab_x,
                                       "censored_fraction": cf_x, "pass": W3},
                "W4_guard_not_trigger_happy": W4,
                "censor_frac_max": CENSOR_FRAC_MAX,
                "all_pass": ok,
                "verdict": (
                    "THE FRONTIER NOW REPORTS LOCATIONS, GUARDED. Two certify verdicts that carried only labels "
                    "now carry walls, each checked against a number known in advance: CERTIFY-GAUGE becomes "
                    "'the frame is underdetermined below K* = {} anchors' -- exactly the reflection argument, "
                    "since 2 anchors fix rotation and translation but leave a mirror image and 3 non-collinear "
                    "ones do not -- and CERTIFY-CHAOS becomes 'chaotic above r* = {} ' against the Feigenbaum "
                    "point {:.4f}. With §142 (v* ~ 1/sqrt2) and §176 (d* = 6) all four now locate. THE GUARD IS "
                    "THE LOAD-BEARING PART: on a deliberately censored statistic the locator ABSTAINS rather "
                    "than reporting a wall (censored fraction {:.2f} >= {}), and it does not fire on either "
                    "uncensored sweep. That failure mode was invisible from inside this repo because our "
                    "quantities are uncensored by construction; it took a sister project running the technique "
                    "on truncated data to expose it."
                    .format(kstar, rstar, R_INF, cf_x, CENSOR_FRAC_MAX) if ok else
                    "NOT ESTABLISHED -- see the individual gates; a located wall that misses its known value is "
                    "worse than the label it replaced.")})
    print(f"\nW1 {W1} | W2 {W2} | W3 {W3} | W4 {W4}")
    print(out["verdict"])
    (RESULTS / "177_located_walls.json").write_text(json.dumps(out, indent=1))

    fig, axes = plt.subplots(1, 3, figsize=(15, 4.2))
    axes[0].plot(Ks, raws, "o-"); axes[0].axhline(gate_g, color="crimson", ls="--")
    axes[0].axvline(3, color="green", ls=":", label="theory K*=3")
    axes[0].set_xlabel("clamped anchors K"); axes[0].set_ylabel("raw frame error")
    axes[0].set_title("CERTIFY-GAUGE -> located"); axes[0].legend(fontsize=8)
    axes[1].plot(rs, K01, "o-"); axes[1].axhline(0.5, color="crimson", ls="--")
    axes[1].axvline(R_INF, color="green", ls=":", label="Feigenbaum r$_\\infty$")
    axes[1].set_xlabel("logistic r"); axes[1].set_ylabel("0-1 statistic K")
    axes[1].set_title("CERTIFY-CHAOS -> located"); axes[1].legend(fontsize=8)
    axes[2].plot(rs, K01, "o-", label="uncensored")
    axes[2].plot(rs, K_cens, "s--", label=f"censored at {cap}")
    axes[2].axhline(0.5, color="crimson", ls="--")
    axes[2].set_xlabel("logistic r"); axes[2].set_ylabel("statistic")
    axes[2].set_title("the guard: censored -> ABSTAIN"); axes[2].legend(fontsize=8)
    fig.suptitle("The frontier reports where the wall is -- and refuses when the quantity is truncated")
    fig.tight_layout()
    fig.savefig(RESULTS / "177_located_walls.png", dpi=140)
    print("saved results/177_located_walls.json + .png")


if __name__ == "__main__":
    main()
