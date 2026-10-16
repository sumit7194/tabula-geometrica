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

## Integrator check (pure Kerr; not a screen output)
- **Setup:** Kerr at χ = 0.6, E = 0.95, Lz = 3.0 + the first 0.1 step with a bound region (Lz 3.7, outer bound ρ
  2.90–13.17), launched at mid-interval with p_x = 0, 200 returns.
- **Max |dH/H|:** 1.1e-12, 3.7e-14 and 3.9e-15 at dt 0.1, 0.05 and 0.025.
- **Kerr's Carter constant** (prolate form, as in 144/132) changes by 3.7e-11, 1.2e-12 and 1.9e-14: conserved and
  convergent. The integrable dynamics, Hénon crossings and t-integration work.
- **Cost:** about 1.5 µs per RK4 step with one exact tangent. The mean return time there is about 153 τ, so a
  2000-return orbit costs about 10 s at dt 0.05.
- **Kernel verification (before this):** H agrees with the independent numpy code to ≤ 3e-14, the vector field with
  numpy finite differences to ≤ 1.4e-8, and the analytic Jacobian with finite differences of the kernel to ≤ 2.6e-8.
  This was checked at all four points and their Kerr limits, at random points.

## AMENDMENT A4 (2026-10-16, before any gate or screen orbit): operational numbers the prereg left open
- **Orbits per screened level (own and shared):** n = 200 launch points, drawn uniformly by rejection over the
  allowed section set {(x, p_x): p_y² > 0} of the screened bound component, using the component's equatorial
  x-interval (fixed seed per level).
- **C0:** 100 orbits in the inner region and 100 in the outer region, graded separately.
- **C3:** 10 orbits per island, launched within 1e-3 (normalised) of the island centre, where the centre is the
  STABLE period-1 fixed point found by our Newton step (the outer one is u₀; the inner one is the period-1 island
  centre).
- **Pilot:** 12 of the level's launch points, evenly spaced in sorted x. No tangent. Drift is the running max up to
  the last crossing, i.e. the reading time. The pilot runs the full N_ret.
- **UPOs:** Newton on Pⁿ − id for n = 1, 2, 3, from a 20×20 seed grid over the level's section box.
  - DPⁿ comes from two exact tangents started on the section (δp_y from the energy constraint), projected onto the
    section at every crossing.
  - Converged when |Pⁿ(z) − z| < 1e-10 (normalised). Duplicates are merged within 1e-6. Orbits are classified by
    |trace| (> 2 hyperbolic).
  - The dt is the level's pilot dt.
- **Kerr null (per χ):**
  - **(i) Whirl levels.** For Lz ∈ {screened levels' Lz values}, find E_b(Lz), the energy at which Kerr's bound
    region merges with the plunge (bisection on the equatorial gap). Then take levels E_b − δ for
    δ ∈ {1e-4, 1e-3, 1e-2}, where a bound region exists.
  - **(ii) Generic levels.** Kerr at the screened MN levels' own (E, Lz), where bound.
  - 100 orbits per null level. Even-indexed orbits are TRAINING (thresholds) and odd-indexed are HELD-OUT (the
    gate, never used for thresholds).
  - d_min is measured to Kerr's own located UPOs, by the same Newton procedure.
- **Verdict reading:** I1 and I2 at N_ret = 2000 (primary) and 500 (secondary), with N_ret/4 for T₁. The I2 windows
  are as registered.
- **Workers:** 4 processes, at nice 10, launched by absolute path, BLAS threads = 1.
- **A4.1 Reading of the null gate (C1 and §5), fixed before any data.** "Held-out Kerr CHAOTIC ≤ 1% (CP95)" cannot mean
  "the CP95 UPPER bound ≤ 1%": that needs n ≥ 299 held-out orbits with zero events, so the gate would fail by
  construction at n = 200. The registered meaning, consistent with §5's "exceeds the 1% one-sided CP95 bound" and
  with §196's Kerr gate: a bin FAILS iff P(X ≥ k | n_heldout, 0.01) < 0.05, i.e. the observed CHAOTIC count is
  significantly above 1%. The CP95 upper bound is reported alongside.
- **A4.2 (pilot drift window; caught by a code-debug run before any gate result).**
  - A4 said the pilot reads drift "up to the last crossing". An orbit that blows up numerically before its first
    crossing then contributes NaN. A dt coarse enough to kill EVERY pilot orbit would read REFUSE instead of FAIL,
    which is the §196 empty-set bug in a new form.
  - Prereg §3's own wording ("over each orbit's life up to its reading time") already fixes it: an orbit that ends
    early is read by its FATE (ESCAPE, with life and return count), so its accuracy window runs to its end.
  - Pilot drift and per-orbit acceptance therefore use the running max |dH/H| over the whole life up to the reading:
    the N_ret-th crossing, or the end for an orbit that ends early. Not a change of rule; it closes A4's parenthetical.
  - Debug evidence (a code-diagnosis run at the self-test's REAL case, whose expected outcome is FAIL): at P0's
    inner region with dt = 0.05, 4 of 5 probe orbits blow up within 0.1–14 τ (drift 0.5 to 250).
  - **Kernel:** a stall guard was added (end code 5: no section crossing for 2e4 τ). The first self-test attempt
    spun on a non-crossing orbit toward the 1e9-step cap and was stopped (own PID).
  - **Process:** that run was launched by RELATIVE path and was invisible to a path-based pgrep (silent_nulls 46,
    again). All runs from here are launched by absolute path.

## AMENDMENT A5 (2026-10-16, before any verdict): an adaptive integrator (Dormand–Prince 5(4)), with the pilot choosing a TOLERANCE
- **Why (an instrument finding, from the pilot):**
  - Fixed-step RK4 cannot hold the accuracy standard in the C0 inner region. The pilot at (0.95, 3), inner region,
    failed at every dt from 0.05 down to the 7.8e-4 floor, with drift O(1e1–1e3); floor_hit.
  - The inner region's equatorial boundary is the CTC edge, where V diverges (The Bridge's observation, confirmed).
    Accelerations there are huge, and LGAC 2010 also needed adaptive steps of 1e-4 to 1e-8 there.
  - The outer region passed at dt 0.05 (drift 9.3e-11).
  - Without this change, C0 would be UNREADABLE and the instrument unfit by construction. The change is made before
    any verdict exists. The pilot only sets accuracy, so this is the accuracy machinery doing its job.
- **What:**
  - Embedded DP5(4) with error control on z = (x, y, p_x, p_y): scale tol·(1 + |z_i|), factor clamp [0.2, 5], safety
    0.9.
  - h_max = 0.5, to keep the per-step domain sampling and crossing detection dense (returns are ≥ ~4 τ). h_min = 1e-13
    gives end code 6, step underflow.
  - The tangent is carried through the same stages but not error-controlled. The section crossing is still one Hénon
    RK4 step from the accepted point.
- **Pilot:** tol ladder 1e-9, 1e-10, …, with a floor at 1e-13 (floor_hit if it still fails). The same drift target
  (1e-10) and the same whole-life window (A4.2).
- **Pilot self-test real case:** the coarsest tolerances (1e-5, 1e-4, 1e-3, 1e-2) on P0's inner region, until one
  FAILS end to end. That is the A5 analogue of "dt 0.05, or a coarser one".
- **Kerr re-check (adaptive):**
  - At tol 1e-12: drift 1.1e-11, Carter conserved to 3.9e-10, 200 returns, about 15 µs per τ.
  - At tol ≥ 1e-10 the h_max cap binds (drift 1.2e-10, not yet at target), so the ladder would continue.
- Nothing else changes: verdict rules, thresholds, windows, levels, controls and gates are as registered.

## AMENDMENT A6 (2026-10-16, before any verdict): the Hamiltonian is regularised at the ergosurface A = 0
- **Finding.** After A5 the C0 inner pilot still failed: drift fell only about 3× per decade of tolerance, to 7e-7 at
  the 1e-13 floor (the outer region passed at 1e-13). That is the signature of a precision loss, not a step-size
  problem.
- **Cause.** 94% of the C0 inner region is ergoregion (f < 0), so orbits cross the ergosurface f = 0, i.e. A = 0. In
  V = ½[f(L − ωE)²/ρ² − E²/f], with f = e^{2ψ}A/B and ω = 2k e^{−2ψ}C/A − ω₀, the terms 4k²C²E²e^{−2ψ}/(ABρ²) and
  E²Be^{−2ψ}/A each diverge like 1/A. Their finite difference is catastrophic cancellation, and g_φφ = −fω² + ρ²/f has
  the same problem. LGAC 2010 hit this and "removed the zeros of A analytically".
- **Exact identity** (sympy polynomial division, with a, b as symbols, ZERO remainder):
  ρ²B² − 4k²C² = k²·A·Q, where Q is the polynomial quotient (in codegen.py; 46 monomials in x, y, a, b — first written as "45", an uncounted estimate; counted after The Bridge reported 46, and they are right). Hence:
  - V = ½[e^{2ψ}A L′² − 4kCEL′ − e^{−2ψ}k²E²Q]/(ρ²B), with L′ = L + ω₀E;
  - g_φφ = [e^{−2ψ}k²Q + 4kω₀C − e^{2ψ}ω₀²A]/B;
  - dt/dτ = −∂V/∂E.
  None of these divides by A.
- **Verification:**
  - Away from A = 0 the regularised kernel matches the original numpy H to ≤ 1.6e-14, at all 4 points and their Kerr
    limits.
  - At the equatorial ergosurface of C0 (x₀ = 3.0278830543…), the regularised g_φφ is exact to ≤ 3e-15 at
    A = 3.7e-3 … 3.7e-12. The unregularised form degrades like 1/A (6e-5 at A = 3.7e-12).
  - The regularised V is smooth through A = 0 (−0.8526711 at both ±1e-9 and +1e-12) and equals an 80-digit evaluation.
- **Lesson on a reference that lied.** My first "truth" (the unregularised V in mpmath at 50-240 digits) disagreed
  with the kernel by exactly 3.9e-16/A, stable in precision. Cause: E**2 was squared in Python DOUBLE before
  entering mpmath, and the 1/A pole amplified that 1e-16 rounding. With exact inputs, the two forms agree. A
  high-precision reference is only as good as its least precise input, and near a pole that is the whole error.
- **For The Bridge and quantum:** any evaluation of f and ω through A (V13 in float; quantum's interval enclosures)
  carries these 1/A poles. Near the ergosurface, values lose about log10(1/A) digits and interval enclosures widen
  without bound. The inner region of C0/F5-R is mostly ergoregion, so its orbits cross A = 0.

## FINDING (geometry + pilot accuracy, before any verdict): an equatorial singular ring B = A = 0 at P0 and F5-R
- **After A6, the C0 inner pilot still fails:** all 12 orbits complete 2000 returns, but drift is about 5e-8 (one
  at 1.8e-6), building in sporadic jumps. The orbits reach x − 1 = 0.930.
- **B = A = 0 exactly on the equator** (mpmath at 50 digits, minimising B):
  - **P0:** B = 4e-98 at x_s = 1.929828259;
  - **F5-R:** B = 1e-97 at x_s = 1.921922588.
  - At both, A = 0, a = −b, and a² = (x+1)/(x−1) to 1e-49.
  - P0's x_s is ρ = 0.7194, the literature's "inner edge ρ ≈ 0.72". The ring lies at R ≈ 1.65, outside the horizon.
- **Behaviour there:** g_φφ and V have POLES at x_s.
  - The equatorial "CTC edge" (1.9298 / 1.9219, measured by both screens) is the g_φφ POLE, not a zero:
    g_φφ = −1.9e5 at 1.9298 and +4.7e3 at 1.931. The CTC region lies on the x < x_s side.
  - V ~ −c/B: V_min on the inner region is −1.4e4 (P0) and −3.1e4 (F5-R) at the inner edge. This is LGAC's "deep
    hole … stochastic scatterer".
- **Not yet checked:** whether this is a curvature singularity (Kretschmann). Until then it is described as "a
  singular ring of the metric functions".
- **p1/p2:** inside D's R ≥ 0.5, min B is 3.8 (p1) and 0.35 (p2), so there is no ring there. p1 has a B near-zero
  (2.9e-3 on the grid) at x ≈ 1.076, y = 0, coinciding with its "CTC edge" 1.0756. It sits inside R < 0.5 and is
  already excluded; exactness not checked.
- **Accuracy:** near V ~ −1e4..−1e5, H = T + V = −½ is a cancellation that amplifies relative errors by about
  |V|/½. That is consistent with the drift floor of ~5e-8 for orbits passing within ~1e-3 of x_s. LGAC themselves
  report inner-region errors of ≤ 1e-8.
- **Kernel:** now records the running max drift at each domain rule's exit (orb[9..11]), so each rule's verdicts can
  be accuracy-gated up to their own reading time.
- **Open, referred to The Bridge before any C-gate is graded:** how C0 is graded. Options:
  - (a) on B9-truncated orbits;
  - (b) on the base domain at LGAC's own 1e-8.
  Also: whether to compute the Kretschmann scalar.
