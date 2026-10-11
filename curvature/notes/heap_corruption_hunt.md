# Heap-corruption hunt (§195 smoke crashes), 2026-10-11

## Evidence so far
- Crashes are SIGSEGV/SIGTRAP at random sites: numpy allocation, the tokenizer (sympy parse), marshal during a lazy
  import, func_traverse in the final GC. Python 3.12.13 and 3.14.5 both crash, so the interpreter version is not it.
- Pinned-label deterministic smoke on 3.14 (`SMOKE_LABEL=smoke_fixed`, single-threaded BLAS): runs 1-2 clean, run 3
  crashed at the final GC after printing output identical to run 1 (all numbers, confirm path, nulls). The
  computation is deterministic; the corruption detonates later at a site that varies.
- **Correction to my own plan:** I had said "same crash site -> our code, random sites -> environment". That test
  cannot discriminate. ASLR and allocator state change the layout every launch, so a deterministic overwrite also
  detonates at random sites. Crash LOCATION is not evidence either way.
- The two crashes with Python frames both sit in `confirm_candidate` (amendment 2), at its start: `load_ts` and a
  lazy scipy import. The heap is already damaged by then; the confirm step is the next allocation-heavy phase.
  Pre-amendment-2 smokes ended before it, which may be why they never crashed.
- Ruled out earlier: mmap, torch, fork, own native code, Accelerate QR/SVD in isolation (300 calls on the real Rt).
- Prior art: Apple Developer Forums thread 772620. It reports intermittent numpy SIGSEGV with Accelerate,
  irreproducible in isolation, gone with an OpenBLAS build.

## Pre-registered A/B (written before any OpenBLAS run)
- Arm ACC: `.venv314` (numpy 2.4.6 / scipy 1.17.1, Accelerate). Baseline = the six deterministic runs.
- Arm OB: `.venv314ob` (same versions, PyPI macosx_11/12 wheels, scipy-openblas 0.3.31; ENVIRONMENT/py314_openblas.json).
- Same command, same pinned label, run sequentially: 10 OB runs.
- Reading: if ACC crashes >= 2/6 and OB 0/10, Accelerate is implicated (P(0/10 | p=1/3) = 1.7%). Remedy: run §195
  on OB, and cross-check that OB output matches ACC to the printed precision. If OB also crashes, Accelerate is
  cleared, and the next step is Guard Malloc launched directly (not via nohup/env, which SIP strips).
- Confound noted: the arms run at different times, not interleaved.

## Amendment 1 (The Bridge's review, before any OB run)
- **Interleaved:** 15 pairs, alternating which arm goes first (odd pairs ACC first, even pairs OB first). Order and
  timestamps go to results/195_ab_order.log. This removes the time/load confound instead of just declaring it. The
  box's load varies (sister runs, the bridge's V12 with 6 workers).
- **Balanced, decided by a test:** 15 vs 15. The six deterministic ACC runs are a PILOT and are excluded from the
  test. Decision: one-sided Fisher exact test on the 2x2 table, p < 0.05 implicates Accelerate. With OB = 0 crashes,
  ACC needs at least 4 of 15 (p = 0.0498). Power at a true rate of 1/3 is 0.79. With 10 vs 10 it would have been 0.44,
  which is why the arms are not 10 each.
- If Accelerate is implicated, the conditional OB-vs-ACC output cross-check still applies.
- A not-significant result with OB crashing is evidence AGAINST Accelerate. A not-significant result with OB clean and
  ACC under 4 is UNRESOLVED (underpowered); it is not read as a clearance.
- Context from the bridge (their claim, not verified here): V12 ran thousands of short workers today on 3.14 +
  Accelerate (numpy 2.4.6 / scipy 1.18.0) without a crash. Its workload is numba ODE integration with almost no
  LAPACK; §195 is heavy on QR/SVD. Consistent with an Accelerate-LAPACK-specific issue, not a test of it.

## Research pass (done late: the A/B was designed after ONE search. Logged as a lapse of the research-first habit.)
- **No published report matches our signature** (heap corruption in a single-threaded spawn-free numpy/scipy process
  on macOS 26 + Accelerate). Searched the numpy, scipy and CPython trackers and the Apple forums.
- Known Accelerate hazards that do NOT apply: fork-after-threads (FreeGSNKE #125, radvel docs; we never fork); the
  NEWLAPACK ILP64 symbol load failures (numpy #30230, rotki #13216; a load error, not corruption).
- Apple forum 772620: intermittent np.matmul SIGSEGV with Accelerate, gone with OpenBLAS. The closest prior case,
  still a single anecdote.
- xzm (macOS xzone malloc): Apple's forum guidance is that a crash inside xzm frames means a client memory bug (most
  often a write after free), detected later on reuse. That matches our delayed, randomly sited detonations.
- CPython #111049 (gc segfault in 3.12.0) was fixed long before 3.12.13. It is not ours, and 3.14 crashes too.

## Instrument: libmalloc ProbGuard (validated before use)
- Not in `man malloc`, but present in Apple's libmalloc source (tests/pgm_integration.c): `MallocProbGuard=1`,
  `MallocProbGuardSampleRate=1`, `MallocProbGuardAllocations=N`. Plain env vars, so SIP does not strip them, unlike
  DYLD_INSERT_LIBRARIES for Guard Malloc.
- Known-fail check (scratchpad uaf.py, a deliberate write after free through ctypes): plain run -> SIGTRAP (xzm
  catches it later, on reuse, exactly our crash style); ProbGuard -> SIGBUS, with faulthandler pointing at the WRITE
  line itself. So it stops at the culprit's write instead of at a later victim.
- Limits: sampling, allocation cap, and possibly a size ceiling, so a clean ProbGuard run proves nothing.
- Diagnostic only, NOT part of the A/B decision: up to 6 ProbGuard smoke runs on ACC (labels pg_i, stop at first
  crash), concurrent with the A/B, whose interleaving absorbs the extra load.
