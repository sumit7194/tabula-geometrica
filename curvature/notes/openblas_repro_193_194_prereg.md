# Pre-registration: OpenBLAS reproducibility rerun of §193, §193b, §193c, §194 and §194b

Written by The Bridge on 2026-10-15, at the user's request ("go ahead"), BEFORE any rerun output exists. Committed together with
the comparison script `scripts/repro_openblas_compare.py`. The script's self-test passed before this commit: the stored
results compared with themselves read REPRODUCED with 0 differences, and four planted changes were all caught
correctly (a verdict string, a control-pass flag, a count, a float).

## Why
These runs used Accelerate numpy (Python 3.12.13), which has the dgeqrf heap overrun (notes/heap_corruption_hunt.md).
The lab notebook marks them "ACCELERATE-EXPOSED; pending OpenBLAS rerun ... re-run before anyone cites them".
This is that rerun. It decides nothing new.

## What runs (code unchanged at cd3b89d, in a separate git worktree, so the stored results are untouched)
- Environment: `curvature/.venv314ob` (Python 3.14.5, OpenBLAS; ENVIRONMENT/py314_openblas.json),
  OPENBLAS_NUM_THREADS=1, OMP_NUM_THREADS=1. Normal priority. Each step runs under `scripts/watch_footprint.sh`
  (MAXMB 6144, MINFREEPCT 8, MINDISK 5).
- Chain A, sequential, in the original order and with default arguments, as the originals:
  `193_ts2_screen.py --probe`, `--production`, `--rank6`, `--export-farfield`, `--rank6-strong`.
- Chain B, concurrent with A: `194_orbit_dimension.py --pilot` (default 4 workers), then `194b_diagnose_g0.py`.
- Baseline: the committed files at cd3b89d (`git show`), never the working tree.

## Reading rule (mechanical, per file and overall; the worst file sets the overall reading)
- **REPRODUCED:** every boolean, every verdict string (with numbers masked) and every integer count is identical, and
  the structure is identical.
- **REPRODUCED WITH COUNT SHIFTS:** the booleans, verdict strings and structure are identical, but some integer counts
  differ. Each shift is listed.
- **NOT REPRODUCED:** any boolean or verdict string differs, or the structure differs. Each difference is listed and
  investigated before anything is said about its cause.
- **Floats are descriptive only.** Report the max and median |log10 ratio| and the 10 largest. Noise-floor quantities
  (1e-20 and below) are expected to move between BLAS libraries and are not read.
- Timing fields are ignored. The pre-registered d=6 resource guard (`d6_dropped`, free swap < 1 GB) is reported but
  never counted as a difference. A cell that ran in one run and was dropped in the other is "not comparable".

## Caveats stated in advance
- This changes BLAS AND Python version (3.12 -> 3.14), plus code changes since the originals (6aca281: the
  tokenizer-free srepr parser; torch removed from the import chain). A difference therefore means "investigate", not
  "Accelerate corrupted it". Agreement means the cited verdicts hold on the safe stack.
- This rerun does NOT address the separate PLUNGE-CUT EXPOSURE of the prograde levels (lab notebook, 2026-10-12).
  Prograde rows stay exposed whatever this reads. Only a redesigned rerun with the barrier separatrix can clear them.
- §194's own gate G0 FAILED originally (classifier_ok False). Reproducing a FAIL is the expected outcome, and it is
  not a result about TS.

## Amendment 1 (2026-10-15, ~15:15 IST). A launch failure; non-numerical code fix; no §193 output had been produced
- **What happened.** At cd3b89d, `193 --production`, `--rank6` and `--rank6-strong` crashed in under 3 s with
  `ModuleNotFoundError: torch`. Each mode lazily runs `from curvlib import progress`, and curvlib imports torch, which
  `.venv314ob` does not have. 6aca281 removed torch from 193's module-level imports but missed these three lines. So
  these modes could not start on the OpenBLAS venv that the tripwire requires. `--probe` and `--export-farfield`
  completed: they do not call progress.
- **Fix.** New `scripts/progress_heartbeat.py`, a verbatim copy of `curvlib.progress` (the function body was checked
  identical by script). The three lines now import from it. It writes the dashboard heartbeat JSON only and has no
  numerical effect. Nothing else changes.
- **Effect on this rerun.** Chain A is relaunched from scratch at the fix commit, probe included. Chain B (194, 194b)
  does not use curvlib and continues at cd3b89d. The baseline stays cd3b89d's committed results. Reading rules
  unchanged.
