# K20 (§197) build log: gates and geometry before any orbit

## Gate G-q (geometry only; results/197_gate_gq.json): PASS after fix round 1
- **Run 1: thresholds PASS, extents FAIL.**
  - At P0 (E 0.95, Lz 3), all four published thresholds reproduce:
    - join Lz 2.9976191477 vs CLA 2.99761912 (dev 3e-8);
    - regions separate up to E 0.9503754 vs 0.95038;
    - outer region vanishes at Lz 3.4093666 vs 3.40935, and at E 0.9321010 vs 0.93210.
  - Both published regions match within 0.05: inner ρ 0.7194–2.1246 (GLM 0.72–2.12), outer 2.3865–13.6385
    (2.39–13.6).
  - **But the code demanded exactly two bound equatorial intervals and found three.** The third is ρ 0.1687–0.5671.
- **Diagnosis (2D connected components on an (x, y) grid):**
  - The third interval is a genuinely separate, closed bound region: x ∈ [1.037, 1.640], |y| ≤ 0.16, not touching
    x → 1. It is NOT a slice of the plunging region.
  - It sits between the singular ring and the equatorial CTC band (CTC on the equator at ρ 0.561–0.716).
  - About 30% of its cells have R² < 0.25 and 0.5% have g_φφ < 0. It lies outside D under any of the rules
    considered.
  - GLM's text does not list it. Either it is part of what they call the plunging region, or they did not resolve
    it. This is recorded as a discrepancy with the paper's description, not with its numbers.
- **Fix round 1:** the registered criterion is "the published extents within 0.05". The code now matches each
  published region to its nearest bound interval, and reports unmatched intervals rather than failing on them.
  - The run-1 shortcut was COARSER than prereg §2, which defines topology by 2D components (silent_nulls 42).
  - Known-fail diagnostic: with β's sign flipped, the result is a single region at ρ 3.98–13.47, which would fail.
- The Bridge's independent G-q also passed, with the same four thresholds to ≤ 1.7e-5 and inner ρ 0.719–2.125. That
  result was received before my fix round. My fix does not use their numbers; it implements the registered
  criterion.

## Domain D geometry at the four points (geometry only)
Grid: x ∈ 1 + logspace(−6, log10 9) with 2400 points, |y| ≤ 0.99999 with 2001 points.

| point | χ | β | x_CTC (global, any y) | δ_x by quantum's rule | equatorial CTC x range | R_s (whole grid / within x−1 ≥ δ_x) |
|---|---|---|---|---|---|---|
| p1 | 0.6 | 0.2 | 1.07563 | **0.15 (quantum states 0.10)** | 1.0432–1.0756 | 0.304 / 0 |
| p2 | 5/13 | −1/3 | 1.12311 | 0.15 (= quantum) | 1.0030–1.1231 | 0.395 / 0 |
| F5-R | 80/89 | 11.290 | 2.41668 | 1.45 | 1.6233–1.9180 | 1.184 / 0 |
| P0 | 0.9 | 11.471 | 2.43572 | 1.50 | 1.6317–1.9242 | 1.190 / 0 |

- **p1 is a knife edge.** The rule needs x_CTC ≤ 1.0750 to give 0.10. I measure 1.07563 and the Bridge measures
  1.07592, so both give 0.15. This is for quantum to resolve.
- **R_s is ambiguous.** Over the whole grid, the "bad" set includes the x → 1 horizon segment, which gives R ~ 0.3–1.2.
  Restricted to the region D keeps (x − 1 ≥ δ_x), it is empty, so R_min = max(0.5, 0) = 0.5 everywhere. I use the
  restricted reading; both are recorded.
- **At F5-R and P0 the global δ_x rule cuts the inner region.**
  - At (E 0.95, Lz 3), D keeps 65% (F5-R) and 62% (P0) of the inner region's grid cells.
  - On the equator it keeps only ρ ≥ 0.98 (F5-R) and ρ ≥ 1.00 (P0), out of 0.72–2.15.
  - The removed part contains the published period-1 island (ρ 0.8–1.05) and the inner edge where LGAC place the
    chaos-generating V_eff hole.
  - Yet the inner region itself is CTC-free (g_φφ > 0 in every cell) and far from the singularity (R² ≥ 2.7). The
    global rule is conservative because the CTC region reaches x ≈ 2.42 only at high latitude (|y| ≈ 0.65–0.9),
    where the bound region does not go.
  - The Bridge found the same, independently, and has asked quantum to decide (before any orbit) whether to use a
    pointwise margin x − x_CTC(y) ≥ 0.025.

## AMENDMENT A2 (2026-10-16, before any orbit)
1. **f_D is reported under BOTH domain rules:**
   - (G) quantum's global rule: x − 1 ≥ δ_x, with δ_x from the global x_CTC;
   - (P) the pointwise rule: x − x_CTC(y) ≥ 0.025.
   The other D conditions (g_φφ > 0, R ≥ 0.5, 1 − y² > 0, finite metric, det g < 0) apply under both. Which rule
   counts is quantum's decision. Until it is made, ESCAPE-by-leaving-D is recorded separately under each rule, and
   verdicts are given under both.
2. **Implementation of the exact tangent:** a sympy-generated analytic Hessian, compiled to C (system compiler, no
   new dependency), instead of torch.func forward-mode AD. Both are exact; this is not a change of method. Reason:
   torch exists only in the Accelerate venv, and the OpenBLAS venv is the project standard since the vendor-bug
   remedy. The C kernel also does the per-step D checks and the Hénon section crossings.
3. **The C0/C3 instrument gates are graded on orbits classified without the D-margin rules** (only g_φφ > 0 and a
   finite metric). The literature they test applies no margin, and C0 tests the instrument against the
   literature, not the proof domain. D-status is still reported for those orbits.

## AMENDMENT A3 (2026-10-16, before any orbit): quantum's B9 (45c1168) is the COUNTED domain rule
- **D_B9:**
  - (a) g_φφ > 0 on the box [x ± 0.025] × [y ± 0.025] around every orbit point;
  - (a′) x − 1 ≥ 0.05;
  - (c) R ≥ 0.5;
  - every metric function finite and det g < 0.
  The global δ_x rule (B6) and the R_s rule are withdrawn as counted rules.
- **Also reported, not counted:** f_D under B6 (the global δ_x) and under (P) (pointwise x − x_CTC(y) ≥ 0.025).
- **How (a) is implemented, and its sampling note:**
  - A CTC mask, g_φφ < 0 or non-finite, is computed on a uniform grid with h = 5e-4 over x ∈ [1, 3], |y| ≤ 1. That
    covers the CTC region's full extent (global x_CTC ≤ 2.436 at every point; outside x > 3, g_φφ > 0 is checked
    pointwise).
  - The mask is dilated by a square of half-width 0.025 + h (one extra cell, so a CTC cell just outside the box can
    only make the test STRICTER, never laxer).
  - Each integration step looks up the orbit point in the dilated mask, and g_φφ > 0 is also checked exactly at the
    point itself.
  - This covers the box's interior as well as its edges and corners (edges and corners alone can miss a CTC blob
    strictly inside the box). Its error is bounded by the grid: at most h = 5e-4, always on the strict side.
  - Limitation: the CTC boundary is resolved only to h. Points within h of the dilated boundary may be judged
    strictly. This is reported, since it can only lower f_D_B9.
- **The equatorial CTC edge is refined by bisection.** My grid values 1.9180 (F5-R) and 1.9242 (P0) were the last
  grid points inside, on a log grid spaced ~0.006 there. The Bridge's 20k-point grid plus bisection gives 1.92192 and
  1.92983, and the latter equals the inner allowed region's lower edge to all digits (g_φφ → 0 makes V diverge, so
  the inner region's equatorial boundary IS the CTC edge). The (P) rule's x_CTC(y) table is bisection-refined to
  1e-10.
