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

## Pilot result (six deterministic ACC runs, pinned label; excluded from the A/B test)
- 2/6 crashed (runs 3 and 6). Every run printed identical output, and both crashes came after the last print.
- **Both crashes are at the SAME site:** SIGSEGV in `func_traverse` during the final GC in `Py_Finalize`. The GC
  dereferences a corrupted *function object*.
- This refines the correction above. One matching site proves nothing (ASLR), but 2/2 at the same object type on
  identical input points to a repeatable overwrite of one kind of object, not ambient noise.
- Candidate: function objects created in bulk by this code path, e.g. sympy `lambdify` products in `load_ts`/
  `spacetimes`, built twice (run_level and `_model_for`). Not tested yet.

## A/B result (15+15 interleaved, 07:11-11:44): ACC 0/15, OB 0/15 -> UNRESOLVED per the pre-registered rule
- Neither arm crashed. Fisher p = 1. By the pre-registered reading this does not implicate Accelerate, and with OB
  clean it is also not evidence against Accelerate. What it does show is that the ACC crash rate itself collapsed:
  P(0/15 | p = 1/3) = 0.0023.
- ProbGuard on ACC: 5 runs clean (the 6th is still running). Uninformative by its own limits.
- OB output differs from ACC in the last printed digit (e.g. r* 1.0e-29 vs 9.8e-30), which is LAPACK round-off at
  the 1e-29 floor. Every verdict is identical.
- **The last crash report is 07:10:52**, the end of the pilot; the reports at 06:55 are my own deliberate uaf.py
  tests. Before 07:10, about a third of runs crashed (3.12 and 3.14, many configurations). After it, about 35 runs had
  zero crashes.
- What changed at ~07:10, two candidates:
  (a) **The invocation:** the pilot used a relative script path; the A/B and ProbGuard runs used an absolute one. That
      changes allocation layout, which can move a deterministic overwrite between a function object and harmless
      memory.
  (b) **The machine:** conditions between ~04:30 and 07:10 (load, memory pressure, other jobs) that have since ended.

## Pre-registered discriminator (written before launch)
- Re-run the pilot's EXACT script (relative path, pinned label, ACC), 6 runs, logs 195_rep_i.
- If 1 or more of 6 crash, (a) is favoured: the crash is layout-sensitive and our process is the culprit. Under the
  pilot rate p = 1/3, P(at least 1) = 0.91.
- If 0 of 6 crash, (a) becomes unlikely (P = 0.088 under p = 1/3) and (b), a time window, is favoured. Then ask what
  ran in that window.

## Discriminator result: (a) INVOCATION/LAYOUT favoured (as pre-registered)
- Re-run of the pilot's exact script (relative path), 12:00-12:28: 1/6 crashed (run 6), again SIGSEGV in
  func_traverse in the final GC. Output was identical to every clean run.
- Pilot-style launch: 3/12 crash, ALL at func_traverse at exit. Absolute-path ACC launches (A/B ACC arm + ProbGuard):
  0/21. Fisher one-sided p = C(12,3)/C(33,3) = 0.040. This is a POST-HOC pooled comparison; the pre-registered test
  was the 6-run rerun alone, which met its ">= 1 crash" criterion.
- Reading: a deterministic-in-kind overwrite inside our own process, whose victim depends on allocation layout. Under
  the pilot layout the victim is a function object that the final GC traverses. It is not machine conditions: the
  kernel log shows no pressure events, kills or memory errors in the crash window.
- Science impact so far: every crashed run printed results identical to the clean runs, and OpenBLAS agrees to
  round-off (1e-29), so no computed number has been seen to change. That is evidence, not proof, that results are
  unaffected.
- Prior-art lead (unconfirmed, may not match): CPython PR #142152 / issue #91636 reverted a 3.14 GC change about
  function objects reached after tp_clear. Our crash is in traverse, not repr, and 3.12 also crashed (at other sites).

## Next: localize with env-gated GC probes (TABULA_GC_PROBE=1)
- `_probe(tag)` prints a tag and runs gc.collect() at each phase boundary: spacetimes+model, stage1 integrated,
  refs built, stage1 scored, stage2 done, nulls scored, run_level returned, confirm done, end of smoke. A corrupted
  tracked object then crashes at the first probe after the damage, and the last printed tag brackets the culprit
  phase.
- Pilot-style launch (relative path), up to 12 runs, stop at first crash.
- Caveat, declared in advance: the edit itself, the env var and the extra collections all shift layout, so the crash
  may vanish. A clean probe series is INCONCLUSIVE, not a clearance.

## Probe result: damage bracketed (13:04)
- Probe run 6 crashed INSIDE the "refs built" probe's gc.collect (func_traverse); the previous probe ("stage1
  integrated") passed. Bracket = reference_cloud + np.save + build_refs (lines 327-329).
- The bracket in isolation (scratchpad repro_ref2.py, exact `Reference` code on that run's saved Rpts, gc after each
  degree, 100 reps = 300 builds): 0 crashes. Isolation does not reproduce; it needs the run's prior heap state.

## The faulting VALUE (decisive clue)
- Three crashes in separate processes (pilot 3, pilot 6, rep 6), each with its own ASLR layout, fault at the IDENTICAL
  "address" 0x3ee5a129056bde81. A real pointer cannot repeat across layouts. This is the float64 value
  **1.031376465963842e-05** written over a function object's pointer field.
- So a deterministic computation writes float64 data out of bounds. It is not a refcount bug and not random
  hardware corruption.
- Victims seen: function objects (func_traverse), dict internals, the libc locale (btowc_l in 3.12;
  mbstowcs NULL deref in the hunt run), marshal/import state. Many victims, one kind of culprit: a buffer overrun.
- Exact bit pattern searched for, NOT found in: the bracket's arrays (Rpts, mu, sd, every feature chunk, every
  stream-QR factor, Householder vectors + tau via mode="raw", S/U/Vt, W); nor any float64 array RETURNED by
  np.linalg.{qr,svd,lstsq,solve,eigh,norm}, np.fft.*, np.{concatenate,stack,vstack,load,where,quantile,sort},
  m94.integrate/seeds, or m.{feats,dop853_fixed,phase_randomize,orbit_scores,reference_cloud,valid}, Spill.orbit,
  during a full smoke (scratchpad hunt_value.py). That run crashed (mbstowcs) in confirm before reaching its end.
  -> The value is most likely transient (inside a library's workspace or a temporary) rather than a returned array.
- My mistake, caught: the first full-run hunt used label "hunt", but the RNG is seeded from the label (crc32,
  line 301), so it computed different numbers. Caught because its printed rows differed from the crashing runs.
  Rerun with label smoke_fixed: rows identical. The wrong-label log is kept as 195_hunt_value_wronglabel.log.
- Process slip: killed the first hunt with `pkill -f <scratchpad script name>`. The rule is an exact PID or the
  SpaceTime/curvature path only; exact PIDs since.

## Guard Malloc, now actually loaded and validated
- DYLD_INSERT_LIBRARIES set as a prefix directly on the python exec (not via nohup/env, which SIP strips) loads it:
  GuardMalloc banner printed.
- Known-fail (scratchpad oob.py: malloc(64), memset 32 bytes past the end): plain run -> "survived overrun", then
  SIGSEGV at exit (EXACTLY our symptom); Guard Malloc -> SIGSEGV with faulthandler at the overrun line. It catches
  the writer at the write.
- Layout-INDEPENDENT: any overrun off a malloc'd block faults, whatever the layout. Limits: 16-byte alignment slack
  (MALLOC_STRICT_SIZE not used yet), and pymalloc-arena objects are not guarded, so an overrun from a small
  pymalloc buffer would be missed.
- Running: full smoke under Guard Malloc, label smoke_fixed, absolute path (195_gmalloc.log).
