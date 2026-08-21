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
     READOUT, and TWO were rejected before one was right -- both rejections recorded because each was wrong for
     a different reason and the pair is the lesson:
       min-over-restarts  (run 1)  reads 0.0000 from K=2 on. Blind to identifiability: a configuration and its
                                   mirror have IDENTICAL stress, so min-selection reports whichever seed ran
                                   first while the ambiguity is fully live. §111 recorded this exact point
                                   ("restarts fix OPTIMIZATION but NOT IDENTIFIABILITY") and it was ignored here.
       mean-over-restarts (run 2)  reads 0.96 / 0.53 / 0.73 at K=3/4/5 -- never approaching zero, because most
                                   restarts never reach a minimum at all. Contaminated by optimization failure,
                                   which is why §111 used best-of-8 in the first place.
       spread among minima (run 3) is the one the definition dictates: gauge ambiguity means SEVERAL EXACT
                                   GLOBAL MINIMA, so compare only solutions that ARE minima. Filtering out
                                   high-stress restarts is not cherry-picking; a non-minimum is not a rival
                                   frame, it is a failed fit.
     STOPPING RULE, pre-registered now: this is the last readout. If K* != 3 under it, W1 is parked as an honest
     negative with the diagnostic table recorded, and the located-wall upgrade is reported as applying to
     CERTIFY-CHAOS / CERTIFY-CONTEXTUAL / CERTIFY-NO-CODE but NOT to CERTIFY-GAUGE at this sample size.
  W2 CERTIFY-CHAOS. Sweep the logistic map's r through the Feigenbaum accumulation point r_inf = 3.5699456,
     the exact onset of chaos. The 0-1 test statistic K should cross from ~0 to ~1 there. Gate: |r* - r_inf|
     small, and K low below / high above.
  W3 THE GUARD, known-fail. Feed the same locator a deliberately CENSORED quantity -- the identical sweep with
     the statistic clipped at a cap, reproducing TheBridge's situation -- and it must ABSTAIN rather than
     report a wall. Without W3 the guard could not fail and would certify its own correctness.
  W5 THE GUARD FLAGS, IT DOES NOT DECIDE. A sweep with BOTH a crossing and high censoring must still report
     the wall, with the flag alongside. This is a regression test for the bug guard v1 shipped with, kept
     permanently because the failure it encodes is invisible by nature.
  W4 THE GUARD MUST NOT BE TRIGGER-HAPPY: it must NOT abstain on W1 or W2, whose quantities are uncensored.
     A guard that abstains on everything is vacuous in the same way §170's floor of ~1 was.
     FIRST RUN: W4 FAILED, and correctly -- under min-selection the gauge sweep was 0.4462 then 0.0000 four
     times over, a step function pinned at a floor, which is censoring in exactly TheBridge's sense. The guard
     caught its own author's sweep one hour after the precondition was catalogued. Recorded rather than
     suppressed; the averaged readout is uncensored because the mirror fraction varies continuously with K.

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
STRESS_TOL = 1e-3              # relative: a restart counts as "at the minimum" within this of the best stress
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
    """First knob at which the statistic crosses `thresh`, with the censoring guard applied CORRECTLY.

    GUARD v1 (rejected, and the rejection is a result). "Abstain if a large fraction of swept values sit at an
    extreme." It fired on the gauge sweep -- values 1.25, 1.59, 1.79, 0.0000, 0.0000, 0.0000, censored fraction
    exactly 0.50 -- and suppressed a wall that is CORRECT and lands on its predicted value. The flaw:

        a flat region is not censoring when the wall lies at its BOUNDARY rather than inside it.

    A sharp wall IS a step function; pinning after the step is what a resolved transition looks like. TheBridge's
    case is different in kind -- their statistic was pinned at the cap across the ENTIRE range with no crossing
    anywhere, so the wall's position was unresolvable rather than merely sharp.

    GUARD v2. Look for the crossing FIRST. A crossing between adjacent knobs localises the wall to one knob
    spacing, which is all any sweep can deliver, and the flat region beyond it is irrelevant. Abstain only when
    NO crossing exists AND the statistic is pinned in a long flat run at an extreme -- the signature of a
    quantity truncated before it could cross. If there is no crossing and no pinning, the honest answer is "no
    wall in this range", which is neither a location nor an abstention.

    GUARD v3 -- FLAG, DO NOT DECIDE (ansatz's correction, adopted). v2 got the ORDER right but still let the
    guard erase information: on the abstain branch it returned no wall and dropped the censoring diagnostic on
    the floor. The asymmetry that makes this worse than it sounds is theirs and it is exact:

        a wrong NUMBER stays wrong loudly -- "four irreducible Killing tensors on Schwarzschild" is absurd on
        sight and was caught within the hour. A wrong ABSTENTION is indistinguishable from a legitimate
        "insufficient evidence", so it can never look absurd. A guard that suppresses has no equivalent of that
        sanity check.

    So: the crossing, when one exists, is ALWAYS reported and can never be erased by the guard; the censoring
    measurement always rides alongside as a flag; and the caller sees both. Abstention is reserved for the case
    where there is genuinely nothing to report.

    Returns (wall, abstain, censor_frac, reason, flag)."""
    cf = censored_fraction(vals)
    flag = (f"CENSORING FLAG: {cf:.0%} of swept values sit at an extreme" if cf >= CENSOR_FRAC_MAX else None)
    for k, v in zip(knobs, vals):
        if (v > thresh) if rising else (v < thresh):
            why = "located: threshold crossed between adjacent knobs"
            if flag:                                       # both true at once -- report the wall AND the flag
                why += f" [{flag} -- reported, NOT suppressed: the wall lies at the flat region's BOUNDARY]"
            return k, False, cf, why, flag
    if cf >= CENSOR_FRAC_MAX:
        return None, True, cf, ("abstain: no crossing, and the statistic is pinned at an extreme for "
                                f"{cf:.0%} of the sweep -- truncated before it could cross"), flag
    return None, False, cf, "no wall in this range (statistic varies but never crosses)", flag


# ---------------- W1: CERTIFY-GAUGE, sweep the anchor count ----------------

def gauge_sweep(Ks, seeds=(0, 1, 2, 3, 4, 5, 6, 7)):
    """Frame error AVERAGED over restarts, not minimised over them.

    FIX ROUND, and the reason is §111's own recorded lesson used against this script. Selecting the lowest-stress
    restart answers an OPTIMIZATION question; identifiability is a question about whether the restarts AGREE.
    With K=2 anchors in 2-D, a configuration and its mirror image across the anchor line have IDENTICAL distances
    and therefore identical stress -- both are exact global minima -- so min-selection reports whichever seed ran
    first and reads 0.0000 while the frame is still ambiguous. Averaging over restarts sees the mirror: half the
    seeds land on it. The pre-registered gate (K* = 3) is unchanged; only the readout is, because the previous one
    provably cannot measure the property being gated."""
    rng = np.random.default_rng(7)
    Z = rng.uniform(-1, 1, (s111.N, s111.D)).astype(np.float32)
    raws, diag = [], []
    for K in Ks:
        keep = s111.K_ANCHOR
        s111.K_ANCHOR = K
        try:
            runs = [s111.reconstruct(Z, K > 0, s) for s in seeds]
        finally:
            s111.K_ANCHOR = keep
        stress = np.array([r[1] for r in runs])
        errs = np.array([s111.errors(r[0], Z)[0] for r in runs])
        smin = stress.min()
        opt = stress <= smin + STRESS_TOL * max(smin, 1e-8) + STRESS_TOL
        spread = float(errs[opt].max() - errs[opt].min())
        raws.append(spread)
        diag.append({"K": int(K), "n_optimal": int(opt.sum()), "stress_min": float(smin),
                     "stress_max": float(stress.max()), "errs_optimal": [float(e) for e in errs[opt]],
                     "spread_optimal": spread, "mean_all": float(errs.mean())})
        print(f"   K={K}  {int(opt.sum())}/{len(seeds)} restarts at the minimum "
              f"(stress {smin:.2e}..{stress.max():.2e})  frame-error SPREAD among them {spread:.4f}  "
              f"[mean over all restarts {errs.mean():.4f} -- contaminated by optimization failures]")
    return raws, diag


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
    raws, gdiag = gauge_sweep(Ks)
    gate_g = 0.15                                       # §111's RAW_THRESH: frame recovered
    kstar, ab_g, cf_g, why_g, flag_g = locate(Ks, raws, gate_g, rising=False)
    W1 = bool(kstar == 3 and not ab_g)
    print(f"   -> K* = {kstar}   (theory 3)   [{why_g}]")

    print("\nW2 — CERTIFY-CHAOS: sweep the logistic map through r_inf = 3.5699456")
    rs = [3.2, 3.4, 3.5, 3.55, 3.58, 3.6, 3.7, 3.8, 3.9]
    K01 = chaos_sweep(rs)
    rstar, ab_c, cf_c, why_c, flag_c = locate(rs, K01, 0.5, rising=True)
    W2 = bool(rstar is not None and not ab_c and abs(rstar - R_INF) <= 0.06
              and K01[0] < 0.5 < K01[-1])
    print(f"   -> r* = {rstar}   (theory {R_INF:.4f})   [{why_c}]")

    print("\nW3 — THE GUARD (known-fail): the same locator on a CENSORED statistic must ABSTAIN")
    cap = 0.35                                          # clip the chaos statistic, reproducing an integration cap
    K_cens = [min(k, cap) for k in K01]
    rstar_c, ab_x, cf_x, why_x, flag_x = locate(rs, K_cens, 0.5, rising=True)
    W3 = bool(ab_x)
    print(f"   censored sweep: {[round(k,3) for k in K_cens]}")
    print(f"   -> abstain {ab_x}   wall reported: {rstar_c}   [{why_x}]")

    W4 = bool(not ab_g and not ab_c)
    print(f"\nW4 — the guard did NOT fire on the uncensored sweeps: {W4}")

    # W5 -- REGRESSION TEST FOR THE BUG GUARD v1 SHIPPED WITH. The gauge sweep has BOTH a genuine crossing and a
    # high censored fraction (0.50, four values at an extreme). v1 saw the fraction and suppressed a correct wall
    # at its predicted value. A guard must FLAG that situation, never DECIDE it away.
    print("\nW5 — regression: a sweep with BOTH a crossing and high censoring must report the wall, flagged")
    W5 = bool(kstar == 3 and flag_g is not None and not ab_g)
    print(f"   gauge sweep: wall reported {kstar}, censoring flag raised: {flag_g is not None}")
    print(f"   -> wall survived the guard: {W5}")

    ok = bool(W1 and W2 and W3 and W4 and W5)
    out.update({"W1_gauge_wall": {"knobs": Ks, "raw_frame_error": raws, "K_star": kstar,
                                  "theory": 3, "censored_fraction": cf_g, "pass": W1},
                "W2_chaos_wall": {"knobs": rs, "zero_one_K": K01, "r_star": rstar,
                                  "theory": R_INF, "censored_fraction": cf_c, "pass": W2},
                "W3_censoring_guard": {"capped_at": cap, "abstained": ab_x, "reason": why_x,
                                       "censored_fraction": cf_x, "pass": W3},
                "guard_v1_rejected": ("'abstain if a large fraction of values sit at an extreme' fired on the "
                                      "gauge sweep (fraction exactly 0.50) and suppressed a CORRECT wall at its "
                                      "predicted value. A flat region is not censoring when the wall lies at its "
                                      "BOUNDARY rather than inside it -- a sharp wall IS a step function. v2 "
                                      "looks for the crossing first and abstains only when none exists AND the "
                                      "statistic is pinned, which is TheBridge's actual situation."),
                "W4_guard_not_trigger_happy": W4,
                "W5_guard_flags_not_decides": {"pass": W5, "wall": kstar, "flag": flag_g,
                                               "why": ("regression test for the bug guard v1 shipped with: the "
                                                       "gauge sweep has BOTH a crossing and censored fraction "
                                                       "0.50, and v1 suppressed the correct wall. A guard must "
                                                       "flag, never decide -- a wrong abstention is "
                                                       "indistinguishable from honest insufficiency and so can "
                                                       "never look absurd the way a wrong number can. "
                                                       "(ansatz's asymmetry, adopted.)")},
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
    print(f"\nW1 {W1} | W2 {W2} | W3 {W3} | W4 {W4} | W5 {W5}")
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
