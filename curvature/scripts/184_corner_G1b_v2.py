"""Step 184 / G1b-v2 — the re-powered zero-test. A NEW gate (Amendment 4), not a retry of the failed one.

WHAT CHANGED, and why the obvious repair was rejected before it was run. The failed G1b asked whether beta ~ 0
in a difference fit. Its post-mortem blamed corr(log R, 1/R) = -0.99 over R = 6..16, and the natural fix was to
widen the range -- but measured first, ratio 10 still leaves -0.955. log R and 1/R are intrinsically similar
over ANY bounded positive range, so a gate that needs beta ESTIMATED cannot be rescued by more range.

So the statistic changed instead: never estimate beta, ask whether the log column is NEEDED.

    model A:  [dP, 1, 1/R]           subleading structure, no log
    model B:  [dP, 1, 1/R, log R]    adds the log
    nested F-test.  1/R is in BOTH -- omit it and log R proxies for it and the test fires with no corner content.

MEASURED POWER (Amendment 4.3, pre-registered): the ORIGINAL gate had 12% power and a 9% false-positive rate --
it could not have detected a real violation and was measuring noise. This design has 95.8% power at alpha=0.01
against an effect of 10% of the single-shape logarithm.

Elongation now SCALES with R (delta = round(R/2)) so dP varies 8..60 rather than sitting constant at 8; the
design matrix is no longer rank-deficient (cond 6.0e16 -> 449.7).

KNOWN-FAIL: p < 0.01 on either side => log structure beyond the subleading term => extraction implicated =>
STUDY DEAD, no corner numbers.
ABSOLUTE FLOOR: the same F-test on the SINGLE shape must fire decisively, or the test cannot tell a working
extraction from one that never needs a log column at all.
DECLARED DEVIATION: R=30 puts L/xi at 0.30. Controlled by re-running at m = 0.005 (L/xi = 0.15); the verdict
must not change.
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
from scipy import stats

from curvlib import RESULTS, progress

cl = import_module("181_corner_lib")

RS = [5, 6, 7, 8, 10, 11, 13, 16, 18, 22, 25, 30]      # FROZEN, Amendment 4.4
ALPHA = 0.01
REG = "nn"


def f_pvalue(y, A, B):
    def rss(X):
        c, *_ = np.linalg.lstsq(X, y, rcond=None)
        r = y - X @ c
        return float(r @ r), c
    r0, _ = rss(A)
    r1, c1 = rss(B)
    n, p0, p1 = len(y), A.shape[1], B.shape[1]
    if n - p1 <= 0 or r1 <= 0:
        return 1.0, np.nan
    F = ((r0 - r1) / (p1 - p0)) / (r1 / (n - p1))
    return float(1 - stats.f.cdf(F, p1 - p0, n - p1)), float(c1[-1])


def run(mass):
    """Whole gate at a given mass. Returns the record."""
    cl.MASS = mass
    X, P = cl.correlators(REG)
    R = np.array(RS, float)
    rows = {}
    for nm in ("regular", "elong+", "elong-"):
        S, PR, NS = [], [], []
        for i, r in enumerate(RS):
            d = max(1, round(r / 2))
            sites = (cl.hexagon(r, r, r) if nm == "regular" else
                     cl.hexagon(r, r, r + d) if nm == "elong+" else cl.hexagon(r, r, r - d))
            s, _ = cl.entropy(sites, X, P)
            S.append(s); PR.append(cl.perimeter(sites)); NS.append(len(sites))
            progress(f"184_{mass}_{nm}", i + 1, len(RS))
        rows[nm] = {"S": S, "perimeter": PR, "n_sites": NS}
        print(f"    {nm:8s} sites {NS[0]}..{NS[-1]}  S {S[0]:.4f}..{S[-1]:.4f}", flush=True)

    # --- ABSOLUTE FLOOR: on the single shape the log column must be NEEDED ---
    y0 = np.array(rows["regular"]["S"])
    P0 = np.array(rows["regular"]["perimeter"], float)
    A0 = np.stack([P0, np.ones_like(R), 1 / R], 1)
    B0 = np.stack([P0, np.ones_like(R), 1 / R, np.log(R)], 1)
    p_single, beta_single = f_pvalue(y0, A0, B0)
    floor_ok = bool(p_single < 1e-4)
    print(f"    FLOOR  single shape: p = {p_single:.3e}  beta = {beta_single:+.6f}  "
          f"-> {'log column IS needed' if floor_ok else 'NO log needed: test would be vacuous'}")

    # --- THE ZERO TEST ---
    diffs = {}
    for nm in ("elong+", "elong-"):
        dS = np.array(rows[nm]["S"]) - y0
        dP = np.array(rows[nm]["perimeter"], float) - P0
        A = np.stack([dP, np.ones_like(R), 1 / R], 1)
        B = np.stack([dP, np.ones_like(R), 1 / R, np.log(R)], 1)
        p, beta = f_pvalue(dS, A, B)
        diffs[nm] = {"p": p, "beta": beta, "dS": dS.tolist(), "dP": dP.tolist(),
                     "cond": float(np.linalg.cond(B))}
        print(f"    ZERO   {nm}: p = {p:.4f}  beta = {beta:+.6f}  cond = {diffs[nm]['cond']:.0f}  "
              f"-> {'NO log structure (pass)' if p >= ALPHA else 'LOG STRUCTURE PRESENT (fail)'}")
    zero_ok = bool(min(d["p"] for d in diffs.values()) >= ALPHA)
    return {"mass": mass, "shapes": rows, "p_single": p_single, "beta_single": beta_single,
            "floor_ok": floor_ok, "diffs": diffs, "zero_ok": zero_ok,
            "pass": bool(floor_ok and zero_ok)}


def main():
    out = {"prereg": "e283d21 +A1 +A2 +A3 +A4", "gate": "G1b-v2", "R": RS, "alpha": ALPHA,
           "claim_scope": "tabula's OWN instrument check -- NOT an independent replication of quantum",
           "measured_power": {"this_design": 0.958, "original_G1b": 0.12,
                              "original_G1b_false_positive": 0.09}}

    print("PRIMARY (frozen m = 0.01, L/xi max = 0.30):")
    main_run = run(0.01)
    print("\nDECLARED-DEVIATION CONTROL (m = 0.005, L/xi max = 0.15) -- the verdict must not change:")
    ctrl_run = run(0.005)

    # THREE-WAY OUTCOME, as pre-registered. Run 1 of this script collapsed it to two and printed
    # "extraction implicated / STUDY DEAD" on a run whose ABSOLUTE FLOOR HAD FAILED -- which the frozen text
    # explicitly says means the test "cannot distinguish a working extraction from one that never needs a log
    # column", i.e. VACUOUS, not a conviction. The implementation dropped a distinction the pre-registration
    # made. That is silent_nulls 37 by OMISSION rather than addition: the freeze protects against the code
    # being stricter than the spec, and equally needs protecting against the code being COARSER than it.
    agree = bool(main_run["pass"] == ctrl_run["pass"])
    if not main_run["floor_ok"]:
        outcome = "VACUOUS"          # the instrument cannot see a log where one certainly exists
    elif not main_run["zero_ok"]:
        outcome = "IMPLICATED"       # floor fired, and the log appears where it must not
    elif not agree:
        outcome = "WITHDRAWN"        # the declared deviation is doing the work
    else:
        outcome = "PASSED"
    ok = bool(outcome == "PASSED")
    VERDICTS = {
        "VACUOUS": (
            "G1b-v2 VACUOUS -- NOT a conviction. The ABSOLUTE FLOOR FAILED at m=0.01: on a shape that genuinely "
            "has six 120-degree corners the log column is not needed (p = {p:.3f}), so the test cannot "
            "distinguish a working extraction from one that never needs a log. DIAGNOSED: the 1/R column "
            "ABSORBS the corner logarithm. Without 1/R the log is decisive (p = 2.9e-07, beta = -0.0172); with "
            "it, undetectable (p = 0.40). corr(log R, 1/R) = -0.9711 here and the data wants c_1/R = "
            "+0.12..+0.40, far larger than the -0.08 the power analysis assumed -- which is exactly why it "
            "predicted 95.8% power and delivered none. Amendment 4 put 1/R in both models to stop log R "
            "proxying for it; that requirement destroys the ability to see a real log. THE TWO FAILURE MODES "
            "ARE MIRRORS AND THIS FAMILY OF ZERO-TEST APPEARS UNCONSTRUCTIBLE ON THIS RANGE. No claim is made "
            "about the extraction in either direction."),
        "IMPLICATED": (
            "G1b-v2 FAILED with the floor firing: log structure is present in a difference that has no corner "
            "content by construction. The extraction is implicated. STUDY DEAD -- no corner numbers."),
        "WITHDRAWN": (
            "G1b-v2 WITHDRAWN: the m=0.005 control disagrees with the primary run, so the declared L/xi = 0.30 "
            "deviation is doing the work."),
        "PASSED": (
            "G1b-v2 PASSED. The log column is decisively needed on the single shape and buys nothing on either "
            "zero-corner-content difference, at 95.8% measured power. The m=0.005 control agrees. Proceeding."),
    }
    out.update({"primary": main_run, "mass_control": ctrl_run, "control_agrees": agree,
                "G1b_v2_pass": ok, "outcome": outcome,
                "verdict": VERDICTS[outcome].format(p=main_run["p_single"])})
    print(f"\nprimary {main_run['pass']} | control {ctrl_run['pass']} | agree {agree} -> G1b-v2 {ok}")
    print(out["verdict"])
    (RESULTS / "184_corner_G1b_v2.json").write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(1, 2, figsize=(13, 4.6))
    for nm in ("regular", "elong+", "elong-"):
        ax[0].plot(RS, main_run["shapes"][nm]["S"], "o-", label=nm)
    ax[0].set_xlabel("R"); ax[0].set_ylabel("S"); ax[0].legend(fontsize=8)
    ax[0].set_title("all three shapes have six 120° corners")
    for nm in ("elong+", "elong-"):
        ax[1].plot(RS, main_run["diffs"][nm]["dS"], "s-",
                   label=f"{nm} − regular  (p={main_run['diffs'][nm]['p']:.3f})")
    ax[1].set_xlabel("R"); ax[1].set_ylabel("ΔS"); ax[1].legend(fontsize=8)
    ax[1].set_title("G1b-v2 · does the log column buy anything? (95.8% power)")
    fig.tight_layout(); fig.savefig(RESULTS / "184_corner_G1b_v2.png", dpi=140)
    print("saved results/184_corner_G1b_v2.json + .png")


if __name__ == "__main__":
    main()
