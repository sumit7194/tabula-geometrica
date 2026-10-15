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

## Amendment 2 (2026-10-15, ~15:25 IST). A protocol slip by The Bridge: the probe's orbit count
- This pre-registration said "default arguments, as the originals". That holds for production, rank6, rank6-strong,
  export-farfield, 194 and 194b. The stored files confirm n_per_ensemble 60, nstep 20000 and dt 0.1. It does NOT hold
  for `--probe`: the stored 193_ts2_probe.json has n = 32 per system, while the default is 16.
- The interim comparison flagged this as 12 "count shifts" (n and kept, 32 -> 16; every orbit kept in both runs).
  It is a sample-size difference, not a numerical one.
- **Fix:** the probe is rerun with `--n 32`. The n = 16 output is kept in `repro_logs/attempt1_probe_n16/` as a record
  and is not read. Reading rules unchanged.
- Interim (not final, recorded as seen): 194_pilot.json REPRODUCED and 194b_diagnose_g0.json REPRODUCED (0
  categorical, 0 count, 0 structural differences).

## OUTCOME (2026-10-15 18:48 IST; The Bridge). Recorded as the rule reads it, then investigated
All steps exited 0 with no watchdog trips, at commit 937e5c0 (probe `--n 32`, per amendment 2). Outputs, logs and
the comparison are in `results/repro_openblas_2026-10-15/`.

**Mechanical output (`repro_openblas_compare.py`, baseline cd3b89d), verbatim:**

| file | reading | categorical | structural | counts | floats: max / median dist |
|---|---|---|---|---|---|
| 193_ts2_probe | REPRODUCED | 0 | 0 | 0 | 0 / 0 (bit-identical) |
| 193_ts2_screen | REPRODUCED | 0 | 0 | 0 | 0.12 / 2.0e-6 |
| 193b_rank6 | **NOT REPRODUCED** | 4 | 22 | 0 | 0.0020 / 4.6e-5 |
| 193c_strong | REPRODUCED WITH COUNT SHIFTS | 0 | 0 | 1 | 0.0067 / 4.1e-6 |
| 193c_farfield_direction | REPRODUCED | 0 | 0 | 0 | 1.9 / 0 |
| 194_pilot | REPRODUCED | 0 | 0 | 0 | 0.16 / 1.3e-13 |
| 194b_diagnose_g0 | REPRODUCED | 0 | 0 | 0 | 0.028 / 0 |
| **OVERALL** | **NOT REPRODUCED** (set by 193b) | | | | |

**Under the registered rules, 193b stays NOT REPRODUCED**, because of the 4 categorical (boolean) differences below.
The investigation says why. It does not change the reading.
1. **The 4 categorical differences sit at a threshold.** t1o3, shared arm, shell 0: the Kerr and ZV2 cells CR/even/6/4
   and CR/odd/5/4 flipped `resolved` False -> True. The shell's resolution is 99,943.65 originally and 100,095.96 now
   (+0.15%), against the resolve threshold of 1e5. Every cell's `count`, `expected` and `pass` is identical, and so
   is every arm verdict in 193b. t1o3 shared is REFUSED in both runs, because the shell-2 Kerr control count fails in
   both. The flag moves no verdict.
2. **The 22 structural differences are the d = 6 resource-guard cells** (`CR/even/6/6`). The original dropped them
   (free swap < 1 GB) and this run did not. The pre-registration calls such cells "not comparable" and says they are
   never counted as a difference. **The script did not implement that exemption**, which is a shortfall of the
   bridge's script. Excluding them would not change the 193b reading, which (1) already sets.
3. **193c count shift:** t1o2 shell 1 Kerr CR/even/6/6 `pruned` 2148 -> 2147 (one basis term). Count and pass are
   identical, and both 193c readings (INCONCLUSIVE, INCONCLUSIVE) are identical.
4. **193c_farfield max dist 1.9:** noise-floor coefficients (floats only, descriptive). All categorical fields are
   identical.

**What this means for citing.** Every verdict in §193 (TS NONE up to rank 4; all controls), §193b (all REFUSED arms),
§193c (both INCONCLUSIVE), §194 (G0 FAIL as before) and §194b is identical on the OpenBLAS stack. The one NOT
REPRODUCED file differs only in an intermediate resolution flag at a threshold. The Accelerate-exposure flag on
§193-194 can be read as resolved for the verdicts. The prograde plunge-cut exposure is untouched (out of scope).

**New, unpaired, NOT a reproduction item.** One d = 6 cell, absent from the original because of the guard, now
exists: §193b t1o2 shared arm CR/even/6/6 reads by the gate-R1 rule "EXACT (polynomial, rank <= 6) -- escalate as a
CANDIDATE, not a claim" (best/floor per shell 1.0e-2, 7.2e-6, 2.0e-3).
- It is a fixed-shell numerical approximant, so it is shell-restricted by construction. §193c already met the same
  kind of candidate in the strong arm and read it INCONCLUSIVE ("candidate SHELL-RESTRICTED integral, never a
  Killing tensor").
- It cannot be an exact Killing tensor: Vollmer 2017 and the bridge's V10 rule out valence <= 7 and <= 10 at p = 3/5,
  and quantum's Morales–Ramis certificates rule out any meromorphic integral. The reading most consistent with the
  record is the near-integrable (KAM-like) approximant seen in §193 ("TS far nearer to integrable than ZV").
- It is recorded for tabula to read under its own rules. Do not cite it as anything.

## Post-outcome diagnosis of the 193b flip (2026-10-15 ~20:30 IST; The Bridge). Diagnostic, not a gate
**Question:** is the 99,944 -> 100,096 move in t1o3 shared shell 0's Kerr resolution caused by the maths library, the
Python version, the code changes since September, or Accelerate heap corruption in the original?

**Method:** `diag_193b_flip/diag.py` recomputes only that cell: Kerr, CR/even/6/4, seed 1, n 60, nstep 20000, dt 0.1.
It prints the resolution and floor, plus SHA-256 fingerprints of the train and test trajectories. It ran in four
setups. Accelerate was used deliberately, through tabula's documented diagnostic override `TABULA_ALLOW_ACCELERATE=1`.

| setup | Python | LAPACK | code | trajectories | floor | resolution |
|---|---|---|---|---|---|---|
| A | 3.14.5 | OpenBLAS | 937e5c0 | 43b7b1d2 / 5f932627 | 4.4231164949e-23 | 100,095.9586 |
| B | 3.14.5 | Accelerate | 937e5c0 | identical | 4.4298367825e-23 | 99,943.6526 |
| C | 3.12.13 | Accelerate | 937e5c0 | identical | 4.4298367825e-23 | 99,943.6526 |
| D | 3.12.13 | Accelerate | f354abb (the original run's code) | identical | 4.4298367825e-23 | 99,943.6526 |

**Findings:**
- **The cause is the LAPACK library alone.** Trajectories are bit-identical in all four setups, so the orbit
  integration plays no part. With the same library, the Python version (B vs C) and the code changes (C vs D) change
  nothing at all. Switching library (A vs B) moves the floor, a relative singular value of ~4e-23, by 0.15%, and the
  resolution moves with it.
- **The original was not corrupted.** Accelerate reproduces the original 99,943.6526 to every printed digit in three
  independent setups, including the original code. A, in turn, reproduces the rerun's 100,095.9586 exactly, so each
  library is deterministic. Neither value is "more correct": both are within that quantity's rounding sensitivity.
- **Methodological caveat for gate R1 (for tabula).** The resolve threshold (1e5) is applied to a ratio of noise-floor
  singular values. Their cross-library spread is ~0.15% (0.01-0.15% across all 15 Kerr shells). This shell sits 0.06%
  from the threshold, so its R1 status is undecidable at numerical precision. No verdict depends on it: the arm is
  REFUSED by its shell-2 Carter-span control failure in every setup.
  - Note also that 193b's refusals rest on Carter-span residuals 4-9% above the 1e-3 limit (0.0010416 and 0.0010895).
    Those are stable across libraries to about 1e-4 relative, but they are close.
  - A full scan found 540 threshold decisions in 193/193b/193c. Exactly one value (this resolution, reused by 4
    cells) changed side.
