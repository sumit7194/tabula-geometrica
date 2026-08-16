"""Step 168b — COSTING the rank 3-4 screen before running it: how much coverage does the CONTROL need?

§168 screened degree 2 on ansatz's bumped Kerr and REFUSED degrees 3-4: three of four controls could not recover
Carter at all, and the fourth produced an unstable count. The stated binding constraint was ensemble coverage
relative to library size. That was a diagnosis, not a measurement -- this script measures it.

WHY THE CONTROL AND NOT THE SCREEN. Four of the five bugs found while building §168 would have produced a
CONFIDENT WRONG ANSWER rather than an error, and every one was caught by a run whose answer was known in advance.
So the increment goes to controls first: if the eps=0 control cannot recover Carter at a given (degree, coverage),
no verdict at that rung is worth anything, and running the deformed arms would only manufacture numbers.

WHAT IT REPORTS, per (degree, family, ntraj): whether the control recovers Carter (irreducible dimension exactly
1, and Carter inside the conserved span), plus the wall time. That turns "we need more coverage" into a cost
curve -- and if the curve does not turn over, that is itself the answer: the instrument's reach ends here, which
is a fact about the instrument and gets reported as one rather than as a disappointment.

NOT A SCREEN. No deformed arm runs here and no verdict about the spacetime is issued.
"""

import json
import sys
import time
from importlib import import_module
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from curvlib import RESULTS

m168 = import_module("168_bumped_kerr_screen")

FAST = "--fast" in sys.argv[1:]
LADDER = [110, 250, 500] if FAST else [110, 250, 500, 1000, 2000]
RUNGS = [(2, True), (3, False), (3, True), (4, True)]
MEM_BUDGET_GB = 3.0        # feature matrix is G x P x p float64; the first attempt at this probe was OOM-killed


def cell_gb(n, p_est):
    """Feature-matrix footprint for one cell, in GB. Two copies (train + test) plus the SVD workspace."""
    P = max(1, m168.NSTEP // m168.STRIDE)
    return 3.0 * n * P * p_est * 8 / 1e9


def p_estimate(deg, wm):
    """Column count without building the library -- cheap enough to guard on."""
    T = m168.geodesics(0.0, seed=7, n=6)
    return m168.library(T, deg, wm, 0.0)[0].shape[-1]


def _flush(out):
    """Write results after EVERY cell. The first attempt at this probe was OOM-killed 20 minutes in with buffered
    output and no incremental write, so every completed cell was lost. A long detached run that only writes at the
    end has no partial results by construction -- it has an all-or-nothing bet."""
    (RESULTS / "168b_coverage_probe.json").write_text(json.dumps(out, indent=1))


def main():
    out = {"purpose": "cost the rank 3-4 screen by measuring what coverage the eps=0 CONTROL needs",
           "not_a_screen": "no deformed arm is run here; no verdict about the spacetime is issued",
           "spin": m168.SPIN, "rows": []}
    print(f"control-coverage probe on ansatz's metric (a={m168.SPIN}), eps=0 only")
    print(f"{'deg':>4} {'family':>12} {'ntraj':>6} {'p':>5} {'cons':>5} {'red':>4} {'irr':>4} "
          f"{'carter_resid':>13} {'control':>8} {'sec':>7}")
    for deg, wm in RUNGS:
        p_est = p_estimate(deg, wm)
        for n in LADDER:
            need = cell_gb(n, p_est)
            if need > MEM_BUDGET_GB:
                # Reported, never silent: a skipped cell is a coverage limit and must not read as a passing rung.
                print(f"{deg:>4} {'rat+metric' if wm else 'rational':>12} {n:>6}  SKIPPED: needs ~{need:.1f} GB "
                      f"> {MEM_BUDGET_GB} GB budget")
                out["rows"].append({"deg": deg, "with_metric": wm, "ntraj": n, "skipped_gb": need})
                _flush(out)
                continue
            m168.NTRAJ = n
            t0 = time.time()
            try:
                Ttr = m168.geodesics(0.0, seed=1, n=n)
                Tte = m168.geodesics(0.0, seed=51, n=n)
                r = m168.screen(Ttr, Tte, deg, wm, carter_alive=True, eps=0.0, deflate_carter=False)
            except Exception as e:                                  # a failed rung is data, not a crash
                print(f"{deg:>4} {'rat+metric' if wm else 'rational':>12} {n:>6}  FAILED: {type(e).__name__}: {e}")
                out["rows"].append({"deg": deg, "with_metric": wm, "ntraj": n, "error": str(e)})
                _flush(out)
                continue
            dt = time.time() - t0
            ok = bool(r["count"] == 1 and r["carter_residual_in_span"] < 1e-3)
            print(f"{deg:>4} {'rat+metric' if wm else 'rational':>12} {n:>6} {r['p']:>5} {r['n_conserved']:>5} "
                  f"{r['reducible_rank']:>4} {r['count']:>4} {r['carter_residual_in_span']:>13.2e} "
                  f"{'OK' if ok else 'FAIL':>8} {dt:>7.1f}")
            out["rows"].append({"deg": deg, "with_metric": wm, "ntraj": n, "p": r["p"],
                                "n_conserved": r["n_conserved"], "reducible_rank": r["reducible_rank"],
                                "irreducible": r["count"], "carter_residual": r["carter_residual_in_span"],
                                "control_ok": ok, "seconds": dt})
            _flush(out)

    good = [r for r in out["rows"] if r.get("control_ok")]
    by_deg = {}
    for r in good:
        key = f"deg{r['deg']}{'+m' if r['with_metric'] else ''}"
        by_deg[key] = min(by_deg.get(key, 10 ** 9), r["ntraj"])
    out["min_coverage_for_control"] = by_deg
    reach = {f"deg{d}{'+m' if w else ''}": any(r["deg"] == d and r["with_metric"] == w and r.get("control_ok")
                                               for r in out["rows"]) for d, w in RUNGS}
    out["control_reached"] = reach
    out["verdict"] = ("Coverage needed for the eps=0 control to recover Carter, per rung: "
                      + (", ".join(f"{k} at ntraj>={v}" for k, v in by_deg.items()) if by_deg else "NONE reached")
                      + ". Rungs whose control never passes at this ladder are beyond the instrument's reach at "
                        "this configuration -- a fact about the instrument, reported as one. No deformed arm was "
                        "run and no claim about the spacetime is made here.")
    print("\n" + out["verdict"])
    (RESULTS / "168b_coverage_probe.json").write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(figsize=(9, 5))
    for deg, wm in RUNGS:
        rows = [r for r in out["rows"] if r["deg"] == deg and r["with_metric"] == wm and "carter_residual" in r]
        if not rows:
            continue
        ax.loglog([r["ntraj"] for r in rows], [max(r["carter_residual"], 1e-12) for r in rows], "o-",
                  label=f"deg{deg} {'rat+metric' if wm else 'rational'} (p≈{rows[-1]['p']})")
    ax.axhline(1e-3, color="crimson", ls="--", lw=1, label="control passes below this")
    ax.set_xlabel("ensemble size (trajectories)")
    ax.set_ylabel("Carter residual in the conserved span")
    ax.legend(fontsize=8)
    ax.set_title("Costing the rank 3-4 screen: can the ε=0 CONTROL recover Carter?\n"
                 "controls first, rungs second — four of five bugs gave confident wrong answers, not errors")
    fig.tight_layout()
    fig.savefig(RESULTS / "168b_coverage_probe.png", dpi=140)
    print("saved results/168b_coverage_probe.json + .png")


if __name__ == "__main__":
    main()
