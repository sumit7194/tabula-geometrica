# Pre-registration — §195: per-orbit invariant learnability, an independent regular/chaotic classifier for TS δ=2

*Written 2026-10-11, after the §194 G0 failure and its root-cause trace (§194b). Approved by The Bridge, and by the
user through The Bridge. **Committed before any run.** Runs after The Bridge's V11 rerun, in the order
G0 → G1 → G2, stopping at any failed gate.*

## Why a new instrument (first principles)

A conserved quantity is a smooth function that stays constant along every orbit in a region. There are two ways to
detect one:
- **Geometric:** look at the orbit's closure, a 2-D torus (count 2) or a 3-D region (count 1). §194 tried this.
  It needs dense coverage of the torus, and §194b showed what breaks it:
  - a 10⁴ τ window is only 23 radial periods, and every orbit is still in the strand regime;
  - **near-resonant tori** (rotation number within 0.002 of 6/5) still leave 10–17% coverage gaps at 10⁵ τ.
  - Resonances are where island chains and thin chaotic layers live, so the geometric readout is weakest exactly
    where the physics is.
- **Functional:** learn the function itself and test it on data it has not seen. A smooth fit interpolates between
  strands, so dense coverage is not needed. This is our emit-or-certify engine (validated in §193, where Kerr's
  counts came out exact), applied one orbit at a time.

**What separates regular from chaotic, from first principles.** A regular orbit's future stays on the torus its
past traced, so an invariant learned on the past **generalizes in time**. A chaotic orbit keeps exploring, so a
function fitted to its past fails on its future. A regular orbit also has a genuine smooth invariant, so the fit
**improves with resolution** (polynomial degree). A chaotic orbit has none, so the fit plateaus.

## ONE primary verdict instrument (The Bridge's note 3)

**F2, per-orbit invariant learnability, issues every verdict.** The other three readouts are reported only and can
never add or remove a CHAOTIC verdict:
- F1, the level-wise defect δ(ε);
- the geometric arm (coverage-gated);
- survival statistics.

So the four readouts cannot become four chances to find chaos.

## F2: the procedure, fixed now

For each orbit with samples z(t), t ∈ [0, T] (stride 0.5 τ), and for each degree d ∈ {2, 4, 6}:

1. **Features.** φ_d(z) is the set of monomials in the standardized coordinates u = (z − μ_R)/σ_R, of total degree
   1..d.
   - For geodesic systems, φ_d is multiplied by the coordinate family {1, (1 − y²)⁻¹, (x² − 1)⁻¹}. This is the
     chart-rational family of §193, in which Kerr's Carter constant is exact.
   - Hénon–Heiles uses the polynomial set only.
   - Basis sizes, constant excluded: geodesics 15 × 3 − 1 = 44, 70 × 3 − 1 = 209 and 210 × 3 − 1 = 629;
     Hénon–Heiles 14, 69 and 209.
   - Hénon–Heiles has no exact polynomial invariant, so EXACT-REGULAR does not apply to it.
2. **Reference cloud R.** All accepted orbits of the level, subsampled to 2×10⁵ points with a fixed seed. Its
   scatter is the denominator. Functions constant on the whole shell, such as H, have no spread on R; they fall
   below the pruning tolerance and are removed.
3. **Fit on the train half.** Fit on [0, T/2] with the §193 square-root engine: streamed QR, SVD pruning at 1e-12
   relative on R. c_d is the direction with the smallest train within-variance relative to R's variance:
   r_train,d = var_train(c·φ) / var_R(c·φ).
4. **Test on the second half.** r_test,d = var_test(c·φ) / var_R(c·φ) on [T/2, T], with the same c_d.
5. **Generalization gap.** g_d = r_test,d / r_train,d.

**Overfitting guard (The Bridge's note 2).**
- N/p ≥ 40 at every rung. One half of the primary window has 3×10⁴ samples, so N/p ≥ 47 at p = 629.
- If an orbit's lived half has fewer samples than 40·p at the top rung, that rung is skipped and the verdict uses
  the rungs that remain.
- The pruning tolerance is the only regularization, and it is fixed.

**Decision rule, fixed from first principles before G0. G0 and G1 validate it; they do not tune it.**

Let d* = argmin_d r_test,d. The floor is Kerr's median r_test,2 at the same ε, measured in G0 and G2.

| verdict | rule |
|---|---|
| **EXACT-REGULAR** | r_test,d* ≤ 10³ × floor |
| **REGULAR** | g_d* ≤ 10 **and** r_test,6 ≤ r_test,2 / 10 (the fit generalizes in time and improves with resolution) |
| **CHAOTIC** | g_d* ≥ 100, **or** (r_test,6 ≥ r_test,2 / 3 **and** r_test,6 > 10⁻⁴) (the fit fails in time, or plateaus) |
| **ABSTAIN** | anything else |

**Rationale for the numbers:**
- They separate orders of magnitude, not fine margins.
- A factor of 10 in variance is about a factor of 3 in spread.
- r = 10⁻⁴ means the orbit's spread is 1% of the level's spread. Above that, a "pinned" function is no invariant
  at all.
- Regular and chaotic orbits are expected to differ by many decades: Kerr floors were 10⁻²⁰ in §193, and chaotic
  seas sit near 10⁻² to 1.

**Stickiness (The Bridge's note 4).** Each orbit is classified at T = 10⁴ τ and at T = 3×10⁴ τ, the **primary**
window, with each window split into its own halves. The verdict pair (10⁴ → 3×10⁴) is reported per orbit. A sticky
chaotic orbit that reads REGULAR at 10⁴ and CHAOTIC at 3×10⁴ is shown as such. Reading a sticky orbit as REGULAR is
the conservative direction, and it is accepted.

Plunged orbits are classified on their lived segment, if it lasted ≥ T/4. They are reported as
STICKY-then-PLUNGED with their verdict.

## Nulls (The Bridge's note 2), run inside G0

- **Phase-randomized surrogates.** 20 Kerr orbits; one random phase per frequency, shared across the four
  coordinates, which keeps every power spectrum and cross-spectrum. Such a series has no invariant level set, so
  **≥ 95% must read not-REGULAR.**
- **Spliced surrogates.** The first half from orbit A and the second half from orbit B, two regular Kerr orbits on
  different tori at the same level (20 pairs). An invariant learned on A must fail on B, so **≥ 95% must read
  not-REGULAR.**
- **Why there is no shuffled-time surrogate:** shuffling time keeps the orbit's point set. A torus stays a torus,
  so the method *should* still find its invariant. It would not be a valid null.

## Systems, levels, seeding, integration

Identical to §194 except for the window. Systems:
- **TS δ=2** at p = 3/5 and 4/5;
- **Kerr** at matched spin;
- **ZV δ=2**;
- **Hénon–Heiles** at E = 1/12 and 0.1657.

Levels:
- E ∈ {0.95, 0.97}, both senses, ε ∈ {−0.02, −0.01, −0.005, +0.005, +0.02} against each system's own L_sep;
- the far levels: Dubeibe (sign self-checked) and the §193 shell.

Two-stage seeding: 200 uniform seeds, then 100 per survive/plunge transition, for up to 3 transitions.

Integration: RK4 at dt 0.05, plunge below r < 3m, drop at H drift > 1e-9. **Primary T = 3×10⁴ τ.**

## Ground truth for the controls (The Bridge's note 1: per-orbit, our own, never taken from §150 or Dubeibe)

Each control orbit is labelled with a **long-window (10⁵ τ) twin-trajectory FTLE λ** and its section coverage.
- **Chaotic truth:** λ > 3 × the maximum λ over the integrable reference orbits at the same ε. The
  reference is Kerr at matched spin for TS, and Schwarzschild (Kerr with a = 0) for the static ZV. That makes the threshold
  self-calibrated against integrable finite-time stretching, including §150's zoom-whirl artifact.
  - For Hénon–Heiles: 3 × the maximum over the E = 1/12 orbits whose section coverage gap is ≤ 0.05.
- **Regular truth:** λ ≤ 1.5 × the Kerr median at the same ε, **and** section coverage gap ≤ 0.05 at 10⁵ τ.
- **Everything else is unlabelled** and excluded from the control scores.

## Gates, in order. A failure stops the run, and TS stays unread.

- **G0, Kerr in the same sampling regime.** Kerr p = 4/5, E = 0.97, both senses, ε ∈ {−0.01, +0.005}. It is
  **enriched with near-resonant seeds**: a fine r₀ scan locates the 6/5 and 5/4 bands, and 50 seeds are placed
  inside them.
  1. ≥ 98% EXACT-REGULAR or REGULAR, **0 CHAOTIC**, ABSTAIN ≤ 2% (survivors, primary window).
  2. The same holds separately on the near-resonant subset.
  3. Both nulls pass at ≥ 95%.
- **G1, controls with our own per-orbit truth.**
  1. *Regular truth* (TS at the Dubeibe level, Hénon–Heiles at E = 1/12, and the regular-truth orbits of ZV's
     near-boundary levels): **≥ 98% not-CHAOTIC.**
  2. *Chaotic truth* (Hénon–Heiles at E = 0.1657, and ZV's chaotic-truth orbits): **≥ 70% CHAOTIC** at the primary
     window. The conservative misses are expected to be sticky; their window-dependence is reported.
  3. *ZV thin layer:* ≥ 1 F2-CHAOTIC orbit at ≥ 2 of the 5 ε levels. If this fails, TS **absence** claims are
     forbidden, but presence can still be reported.
- **G2, TS and Kerr at both p, all levels.**

## Pre-registered predictions for G2. Each is checked; none is assumed.

- **P1:** Kerr has 0 CHAOTIC at every level.
- **P2:** TS at the far levels is ≤ 1% CHAOTIC.
- **P3:** TS near the boundary has ≥ 1 CHAOTIC orbit (including STICKY-then-PLUNGED) in ≥ half the ε bins at
  both p, with Kerr at 0.
- **P4, reported:** the TS chaotic fraction against |ε| (Spearman), and the window-dependence (10⁴ → 3×10⁴).

## Report-only readouts (no gates; they cannot change any verdict)

- **F1, the level-wise defect δ(ε).** The §193 engine (CR family, even r = 2 and 4) is fitted on half the level's
  orbits and tested on the other half, with time subsampled to every 20th sample. δ = TS's best held-out ratio over Kerr's Carter floor at the same ε.
- **The geometric arm**, at T = 10⁵ τ: §194's estimator, **coverage-gated**. A section gap > 0.05 →
  ABSTAIN-coverage. It runs after G2, if time allows.
- **Survival statistics:** the plunge-time distributions per level. These overlap The Bridge's V11.

## Kerr-limited bins (carried over from §194 amendment 1)

TS verdicts in any ε bin where Kerr's ABSTAIN rate exceeds 10% are graded "Kerr-limited", and no TS conclusion is
drawn there. Thresholds are never changed after data.

## Scope

- Numerical, on the listed levels.
- Equatorial seeds with p_x = 0, and the stated windows.
- A REGULAR verdict means "a learnable local invariant over the window", not "integrable".
- Vacuum is inherited from ansatz's Schwartz–Zippel check.
- Orbits are held at r ≥ 3m.

## Resources

- Primary F2 at 3×10⁴ τ, about 20k orbits plus controls: roughly 8–12 h on 4 workers (QR per orbit at p ≤ 624).
- The geometric arm adds ~18 h on 4 workers, and is optional.
- Everything is checkpointed per level.
- BLAS is pinned to 1 thread per worker, the runs are detached, and the watchdog uses The Bridge's rule.

## Implementation notes (fixed now)

- **Measurement and verdict are separate.** Per orbit, the raw r_train,d, r_test,d and g_d are saved. Verdicts
  are computed afterwards by the frozen rule, because the TS floor needs Kerr's matched level first.
- **The reference cloud R** comes from the level's stage-1 accepted orbits (2×10⁵ points, fixed seed). It is
  built once per level and degree. Features are scaled by R's column standard deviations before the QR.

## Amendment 1 — 2026-10-11, from a code-path smoke test, before any gate run

The smoke test was a code-path check only: 12 Kerr orbits on a short window, guard relaxed, nothing saved, no gate
evaluated. It exposed two design defects, fixed here from first principles. **The decision rule below supersedes
the table above.**

1. **The EXACT floor was set at the wrong rung.**
   - In this basis, Kerr's Carter constant needs degree-4 monomials (y²p_y², or x²p_x² in the radial form), so it
     is *not* exact at d = 2. A floor taken from Kerr's r_test,2 sits near 10⁻¹² rather than at the numerical
     floor, and could have let a thin chaotic layer read as EXACT.
   - **New rule: the noise ceiling** is the 99th percentile of Kerr's best held-out ratio r* over the matched
     reference level, where Carter is exact in the basis, so r* is pure round-off. ZV uses Schwarzschild.
   - For G0 it is taken **leave-one-level-out**, from the other G0 levels, so Kerr cannot pass by construction.
   - Hénon–Heiles has no reference, so it uses a fixed NOISE_ABS = 10⁻²².
2. **High rungs overfit when the data are thin.**
   - With the guard relaxed, d = 4 and 6 drove r_train to about 10⁻³³ and blew up r_test. The orbit's strands give
     far fewer independent constraints than the raw sample count, so N/p alone cannot guard against this.
   - **New: rung selection by inner validation.** The train half is split into Q1 | Q2. The fit is made on Q1 and
     validated on Q2, giving v_d for every rung with |Q1| ≥ 20p. Then d* = argmin v_d.
   - The final fit is made on the whole train half at d*, and tested on the **untouched** test half, giving r* and
     g* = r*/r_train.
   - The test half is never used to choose anything.
3. **g at the numerical floor is meaningless** (a ratio of two round-off numbers). The smoke test showed g up to 10³
   for exactly-conserved Kerr orbits. So the g-test only counts above 100 × the noise ceiling.

**Frozen decision rule (supersedes the earlier table):**

| verdict | rule |
|---|---|
| EXACT-REGULAR | r* ≤ 10 × noise |
| REGULAR | g* ≤ 10 **and** min_d v_d ≤ v_lowest / 10 (descending) **and** r* ≤ 10⁻⁴ |
| CHAOTIC | r* > 100 × noise **and** (g* ≥ 100 **or** (min_d v_d ≥ v_lowest / 3 (flat) **and** r* > 10⁻⁴)) |
| ABSTAIN | anything else |

- "r* ≤ 10⁻⁴" is new in REGULAR. Otherwise a well-mixed chaotic orbit lying away from the rest of R could fake a
  slow "descent" (a polynomial approximating a function that is constant on a 3-D region).
- In the smoke test, Kerr picked d* = 4 with r* between 10⁻²⁵ and 10⁻³⁰, so every orbit read EXACT-REGULAR. Both
  nulls read 100% not-REGULAR.
- **This is a code-path check, not gate evidence.** G0 runs at T = 3×10⁴ τ, with the full seeding and the
  near-resonant enrichment.

## Implementation note — 2026-10-11, the first G0 launch was killed by the watchdog (not a gate result)

- The watchdog killed the first G0 launch at a 9.9 GB process tree, over the 8 GB cap. Nothing was saved, and no
  verdict was issued.
- The cause: each worker held whole float64 trajectory arrays and whole per-orbit feature matrices.
- The fix, in implementation only (design, gates and rule unchanged):
  - trajectories are integrated in 40-orbit chunks that spill to disk and are memory-mapped back;
  - features are streamed in 4000-row chunks;
  - nulls are scored inside the worker;
  - the reference cloud R is subsampled **stratified per accepted orbit**, about R_POINTS / n_accepted points
    each, which is the same distribution as a uniform subsample.
- A smoke test peaked at 0.58 GB, with the same Kerr verdicts and nulls as before.
