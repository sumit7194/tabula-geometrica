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
