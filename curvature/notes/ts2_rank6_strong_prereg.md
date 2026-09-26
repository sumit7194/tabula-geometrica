# Pre-registration — §193c: strong-field rank-6 d=6, the decisive follow-up to §193b's post-hoc TS direction

*Frozen before any strong-field d = 6 TS statistic. The Bridge gave the go on 2026-09-26. Local, unpushed.*

## Why

In §193b (q = 3/5, shared arm, even r6 d4), TS showed exactly one direction at Kerr's exact-conservation level:
2.0e-23, 1.6e-24 and 7.6e-26, against Kerr's Carter at 1.9e-25, 6.9e-25 and 3.4e-26. This was **post-hoc, not a
verdict**, because Kerr was UNRESOLVED there. Two readings fit: a far-field formal-series approximant, or a
genuine rank-≤6 invariant.

**The discriminator:** near the source an approximant should degrade, while an exact invariant should not. At
d = 6, K³ is representable, so the Kerr control can resolve.

## Scope

- The strong-field arm only, with **§193's strong shells unchanged**:
  - q = 3/5: (0.935, −2.9), (0.94, −3.0), (0.945, −3.1);
  - q = 4/5: (0.94, −3.05), (0.935, −3.05), (0.94, −3.15).
- Both (p, q).
- One cell: **CR even r = 6, d = 6 (s = 3)**.
- The same seeds and ensembles (60 + 60 orbits, 20000 steps at dt = 0.1, stride 20), the same engine
  (square-root form), and the same band (10³).

## Controls first. TS is not integrated for a q unless all of these pass on every shell.

- **Kerr count = 3** (K, K², K³), with Carter span residual < 1e-3.
- **R1:** Kerr's 4th ratio / 3rd ratio ≥ 1e5.
- Any failure on any shell at that q → **REFUSED** for that q.

## The frozen reading rule, per q, over the three strong shells

The quantities:
- **TS_best** = TS's best held-out ratio in the cell;
- **floor** = Kerr's 3rd ratio (K³, the last expected direction);
- **K_ratio** = Kerr's 1st ratio (Carter), on the same shell;
- **far-field level** (q = 3/5 only) = the largest of §193b's shared-arm TS_best values, **2.0e-23**. q = 4/5 has
  no far-field reference, because §193b did not read TS there.

The readings:
- **EXACT-LIKE:** on every shell, TS_best ≤ 10³ × floor **and** TS_best ≤ 10³ × K_ratio.
- **APPROXIMANT-LIKE:** on every shell, TS_best > 10³ × floor (it leaves the band), **or**, for q = 3/5,
  TS_best > 10³ × 2.0e-23 = 2.0e-20 (a degradation of more than 10³ from the far-field level).
- **INCONCLUSIVE:** anything else, including any mix across shells.

Neither EXACT-LIKE nor APPROXIMANT-LIKE is a claim. Both go to The Bridge only.

## Resources (The Bridge's rule, replacing the swap trigger)

- Detached, logging to the repo.
- The whole-process-tree cap is 5 GB (MEM + CMPRS).
- Kill if free disk < 8 GB, or if `memory_pressure` reports system-wide free below 10%.
- No swap trigger. On this Mac, swap is dynamic.

## Export (separate, before the run)

The §193b far-field direction (q = 3/5, shared shells, even r6 d4) is recomputed with the same seeds, and its
coefficient vector is written to `results/193c_farfield_direction.json`:
- the raw-feature basis names;
- the shell's (E, L);
- x_ref;
- the feature scales, and a unit normalisation in raw-feature space.

Its path goes to The Bridge only.
