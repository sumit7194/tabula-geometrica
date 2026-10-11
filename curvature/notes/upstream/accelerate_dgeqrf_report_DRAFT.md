# DRAFT, NOT SENT: whether and where to file is the user's decision

Two targets:
- **(A)** Apple Feedback Assistant (Accelerate / LAPACK). Needs the user's Apple ID.
- **(B)** A short heads-up issue on numpy/numpy. numpy's macOS >= 14 arm64 wheels link Accelerate by default, so
  `np.linalg.qr` users are exposed.

---

## (A) Apple Feedback: Accelerate `dgeqrf` (NEWLAPACK) writes past an internal heap allocation

**Summary.** On macOS 26.5 (25F71), Apple M4 (Mac16,10), `dgeqrf` in Accelerate's new LAPACK interface writes
past the end of a heap block that it allocates itself. The trigger is near-square double-precision matrices with
about 550-629 columns. In normal runs the overrun usually lands in allocator slack. When it does not, it silently
corrupts neighbouring heap objects, and the process crashes later at an unrelated site.

**Reproduce.** Use numpy 2.4.6 from PyPI, wheel `cp314-cp314-macosx_14_0_arm64`, which is linked to Accelerate.
This reproduces on Python 3.14.5 and 3.12.13.
```python
import numpy as np
A = np.random.default_rng(0).standard_normal((629, 629))
R = np.linalg.qr(A, mode="r")      # numpy calls dgeqrf$NEWLAPACK$ILP64
```
Run it under Guard Malloc. Set the variable directly on the interpreter exec; launchers like `env` and `nohup` are
SIP-protected and strip it.
```
DYLD_INSERT_LIBRARIES=/usr/lib/libgmalloc.dylib VECLIB_MAXIMUM_THREADS=1 python repro.py
```
**Result:** `EXC_BAD_ACCESS (SIGSEGV)`, ESR "(Data Abort) byte write Translation fault", at the first byte past a
MALLOC_LARGE region (976 KB for 604x600; 752 KB inside our pipeline). The faulting frame is in `libLAPACK.dylib`,
under `dgeqrf$NEWLAPACK$ILP64`, called from numpy `qr_r_raw<double>`.

**Shape dependence** (m x n; FAIL = Guard Malloc write fault):
- FAIL: 554x550, 604x600, 620x629, 629x629, 633x629, 650x629, 700x629, 800x629
- OK: 64x64, 128x128, 44x44, 209x209, 300x300, 404x400, 504x500, 900x629, 950x629, 1000x629, 8000x629, 1004x1000

**Not a caller workspace error.** The same overrun occurs through SciPy's independent wrapper
(`scipy.linalg.lapack.dgeqrf`, SciPy 1.17.1 linked to Accelerate), both with the `lwork` that Accelerate's own
workspace query returns (19200 = 32n for 604x600) and with twice that. The overrun buffer's size matches neither the
matrix copy, `tau`, nor `work`. It appears to be allocated inside Accelerate.

**Control.** The identical numpy and SciPy versions built against OpenBLAS (PyPI `macosx_11_0` / `macosx_12_0`
wheels, scipy-openblas 0.3.31) run every shape above cleanly under Guard Malloc.

**Impact observed.** In a long numerical pipeline the corruption showed up as intermittent SIGSEGV/SIGTRAP at
unrelated sites: GC traversal of a function object, dict lookup, marshal during import, libc `mbstowcs`/`btowc_l`,
xzone malloc traps. The rate was about 1 in 4 runs and depended on memory layout (even the script's path changed
it). In three ASLR-distinct crashes the faulting address was the same float64 value (0x3ee5a129056bde81 =
1.0314e-05), i.e. numeric data written over a pointer field.

---

## (B) numpy heads-up issue (short)

**Title:** `np.linalg.qr` on macOS Accelerate wheels: heap overrun inside Accelerate `dgeqrf` for n ~550-629
(Guard Malloc repro)

**Body:** On macOS 26.5 / M4 with the numpy 2.4.6 `macosx_14_0_arm64` wheel (Accelerate),
`np.linalg.qr(rng.standard_normal((629, 629)), mode="r")` triggers a Guard Malloc byte-write fault inside
`libLAPACK.dylib` (`dgeqrf$NEWLAPACK$ILP64`). The identical code on the OpenBLAS wheel is clean.

The fault reproduces through `scipy.linalg.lapack.dgeqrf` even with twice the queried `lwork`, so we believe it is an
Accelerate bug, not numpy's workspace handling. It has been reported to Apple as FB<number>.

Filing so that users seeing intermittent, layout-dependent segfaults after QR at these sizes can find it. Workaround:
the OpenBLAS wheels. Full shape table and crash details: (link to the Apple report text above, or paste it).

---
Provenance: tabula-geometrica `curvature/notes/heap_corruption_hunt.md`, 2026-10-11.
Repro script: `notes/upstream/accelerate_dgeqrf_overrun_repro.py`.
