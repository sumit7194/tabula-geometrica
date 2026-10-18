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

## AMENDMENT A7 (2026-10-16, post-pilot, BEFORE any verdict or gate is graded; The Bridge's ruling, adopted)
**Why:** the C0-level inner orbits pass within ~1e-3 of the B = A = 0 ring, where H = T + V = −½ cancels across
|V| ~ 1e4–1e5. The 1e-9 drift standard is out of reach there in double precision. LGAC themselves report ≤ 1e-8 in
the inner region. The gate must test the instrument in the PUBLISHED setting; mixing in the physics question (is the
published chaos ring scattering?) would make a failure uninterpretable.

**GATE (instrument):**
- C0, C3 and C4 at (χ 0.9, q 0.95, E 0.95, Lz 3) are graded on the BASE domain (g_φφ > 0, finite, det g < 0; no
  margins, as in A2.3), with per-orbit acceptance |dH/H| ≤ 1e-8 (LGAC's reported inner-region accuracy) up to the
  reading time.
- The pilot target at the C0 level is 1e-9 (10× under acceptance, the same ratio as elsewhere).
- Pass criteria are unchanged: inner ≥ 50% CHAOTIC; outer ≤ 10%; inner region at ρ 0.72–2.1 ± 0.05; C3 NOT CHAOTIC
  on both arms; C4 D₂ < 1.3. The 25% UNREADABLE rule still applies.
- The C3/C4 island orbits are expected to meet 1e-9 as well. Their drift is reported, but they are graded at the
  gate's 1e-8.

**FINDING (physics, not a gate), pre-stated:** the SAME C0 orbits are also read under D_B9, each at
min(N_ret-th return, its B9 exit), with 1e-9 accuracy up to that reading. Reported:
1. the fraction of C0 inner and outer orbits that exit D_B9 before N_ret (with CP intervals);
2. the distribution of the number of returns before the B9 exit;
3. among base-domain CHAOTIC inner orbits, the fraction that (i) never leave D_B9, (ii) leave after ≥ 500 returns
   and are still CHAOTIC at their secondary reading, or (iii) leave before 500 returns (ESCAPE under B9);
4. f_D for C0's inner candidate region;
5. the same under B6 and P, for information.
- **Prediction, written now:** at least 50% of base-domain CHAOTIC inner orbits leave D_B9 before 500 returns. That
  would make the published inner chaos predominantly a ring-proximity phenomenon at this level. Low-to-moderate
  confidence.

**Counted screens** (p1, p2, F5-R, own and shared levels) are unchanged: 1e-9, read at the B9 exit (A3, A4.2), with
the pilot target 1e-10.

**Kernel support:** drift at each rule's exit is recorded (orb[9..11]), so B9 readings are accuracy-gated up to the
exit itself, not only up to the last crossing before it.

**Also commissioned (The Bridge):**
- the Kretschmann scalar near x_s, along y = 0 and two off-equator rays, at 50 digits, with its growth rate in the
  distance to the ring point;
- the same exactness check for p1's B near-zero at x ≈ 1.076;
- a literature check of whether this ring is identified anywhere.

## Kretschmann near the ring (scripts/197c_kretschmann.py; results/197c_kretschmann.json)
- **Method:** mpmath at 60 digits, metric derivatives by mp.diff, generic Christoffel → Riemann → K = R_abcd R^abcd.
- **Validated on Kerr (β = 0)** against the closed form: relative error 3e-17 to 2e-16 at three points.
- **P0 and F5-R: K diverges as d⁻⁶** along every ray from the ring point (y = 0 from both sides, 45°, axis-ward 90°):
  - P0, y = 0, x > x_s: K = 1.19e20, 1.10e26 and 1.09e32 at d = 1e-3, 1e-4 and 1e-5. The local exponent is −5.97,
    then −6.00.
  - The other rays give the same 10⁶ per decade, with ray-dependent prefactors and signs (the axis-ward ray is
    negative). B ∝ d² along each ray.
- **Conclusion:** a genuine curvature singularity, with the same d⁻⁶ law as Schwarzschild's r = 0, located OUTSIDE
  the horizon at R ≈ 1.65 (ρ = 0.7194 at P0).
- **p1:** B = 9.1e-88 and A = −1.7e-42 at x = 1.0759622 (y = 0), so it too has an EXACT B = A = 0 point on the
  equator. The singular ring is generic to these MN points. At p1 it sits at R = 0.396, inside D's excluded R < 0.5.
  Not computed: Kretschmann at p1, and p2's B zero (p2's grid minimum is near x → 1, |y| ≈ 0.49).
- **Independent confirmation (The Bridge, V13 FINDINGS).** Their own V9 metric transcription, EXACT sympy first and
  second derivatives lambdified to mpmath at 60 digits, and their own Christoffel → Riemann → K code.
  - Kerr closed form reproduced to ≤ 6e-59.
  - At C0, on the equator (x > x_s): K = 1.191e20, 1.100e26 and 1.091e32 at d = 1e-3, 1e-4 and 1e-5, which are our
    values to 3 digits. d⁻⁶ on both sides. F5-R matches after M⁴ scaling.
  - The two routes share no code and use different derivative methods (numerical mp.diff vs exact symbolic).
- **Shared-source caveat (applies to both of us):** our MN formulas share one source chain. The metric is as given in
  GLM 2008 / Brink 2008 App. C (same B), and quantum's MN_METRIC.md derives from it. Nobody has read Manko & Novikov
  1992 itself. Any write-up must say "the MN subclass as given in GLM 2008 / Brink 2008 App. C".

## AMENDMENT A8 (2026-10-16, before ANY verdict; The Bridge's ruling): the matched-proximity null is infeasible in Kerr
**Found while building the C-gates, not from any MN result.** The first Kerr whirl level (χ 0.9, Lz 3, E = E_b − 1e-4,
E_b = 0.969002) had one period-1 orbit, which is STABLE, and no hyperbolic ones. That is forced by separability:
- Below E_b every bound Kerr orbit lies on a torus, and the unstable spherical orbit sits on the barrier top,
  outside the bound region.
- At or above E_b the radial motion has no inner turning point, so every orbit plunges within about one radial
  period.
- So NO long-lived Kerr orbit can lie near a hyperbolic UPO. The registered per-d_min-bin thresholds (§5) would leave
  bins 0–2 permanently empty, and every MN orbit near a hyperbolic UPO, exactly where chaos lives, would read
  CANNOT-DISCRIMINATE. That is a silent null built into the design. (The Bridge: "my requirement's fault"; V13 has
  the same flaw and mirrors A8.)

**Replacement:**
1. **Thresholds** are pooled over all Kerr null orbits at that χ: the class-wise max over the levels. The whirl
   levels (E_b − 1e-4, 1e-3, 1e-2) are near-separatrix tori, with log-divergent periods and large transient stretching:
   the hardest integrable cases available for long orbits. The generic levels are added.
   - TRAINING orbits (even index) set the thresholds. C1 is a binomial test on the pooled HELD-OUT orbits (odd index)
     against 1% (A4.1).
   - MN verdicts are still tabulated by d_min bin, as information only.
2. **d_sep is reported for the Kerr null:** the normalised section distance from each orbit's points to its bound
   region's section boundary (the p_y² = 0 curve). It shows how close to separatrix structure the null actually
   goes.
3. **Transient hyperbolic stretching** is guarded by I1's plateau ratio ρλ and by I2 being non-variational.
   Short-lived near-hyperbolic Kerr transits (E ≥ E_b plungers) cannot reach 500 returns, so they produce no reading.
4. **A second integrable null that DOES populate small d_min (built, not left as a limitation):** a separable double
   well,
   H = ½p₁² + ¼q₁⁴ − ½q₁² + ½p₂² + ½q₂², at total energy h = 0.5.
   - Its periodic orbit q₁ = p₁ = 0 (q₂ oscillating) is a genuine HYPERBOLIC fixed point of the section map on
     Σ = {q₂ = 0, p₂ > 0} in (q₁, p₁), known exactly. Near-separatrix orbits (E₁ = ½p₁² + V₁ ≈ 0) live forever.
   - It runs through the SAME C kernel (integ.c with this vector field compiled in, domain checks disabled), the same
     Hénon crossings, the same pilot and acceptance, and the same N_ret = 2000 and windows.
   - 200 orbits: 150 with |E₁| ≤ 1e-2 (near separatrix) and 50 generic; fixed seeds.
   - **Test:** the dimensionless statistics, ρλ and D₂(A), D₂(B), are compared with the Kerr-pooled p99 thresholds.
     λ₂ has units of 1/time and is NOT comparable across systems, so it is reported but not used.
   - **PASS iff, in d_min bins 0–2, the AND rule would not fire:** for every accepted orbit, NOT (ρλ > p99 AND
     D₂A > p99 AND D₂B > p99). Equivalently, the guard in (3) is demonstrated rather than argued.
   - The per-arm rates (ρλ above p99; D₂ above p99) are also reported.
- **A8.1 (before any real threshold; a code-path smoke with placeholder thresholds):** uniform |E₁| ≤ 1e-2 put every
  near-separatrix double-well orbit in d_min bin 2 (distance to the saddle scales like √|E₁|). The near set is now
  log-uniform, |E₁| ∈ [1e-8, 1e-2], both signs, to populate bins 0–2. Smoke statistics (not results): ρλ 0.28–0.41,
  D₂ ≈ 1. The DW pilot is tolerance-limited (drift 9.4e-10 at the 1e-13 floor, floor_hit, under the 1e-9 acceptance).

## C-GATES RESULT (2026-10-16; results/197_cgates.json; prereg 9aca9a4 + A1..A8)
**All instrument gates PASS.**

| gate | result | criterion |
|---|---|---|
| G-q (geometry) | PASS (earlier; fix round 1 recorded) | published thresholds within 1e-3, extents within 0.05 |
| C2 pilot self-test | PASS 5/5 (earlier) | known-fail cases fail |
| C1 Kerr null, χ 0.9, pooled held-out | **0/200 CHAOTIC** (CP95 upper 1.49%, p = 1.0 vs 1%) | binomial test vs 1% |
| A8 double-well null, d_min bins 0/1/2 (n 74/46/34) | **AND rule fires 0 times**; ρλ alone is above p99 in 6/74 (bin 0) and 1/46 (bin 1); D₂ above p99 in 0 | no joint flag in bins 0–2 |
| C0 inner (base domain, 1e-8) | **75/80 CHAOTIC = 93.8%** (5 INDETERMINATE); 20/100 excluded on accuracy (< 25%) | ≥ 50% |
| C0 outer (base domain, 1e-8) | **0/100 CHAOTIC** (51 REGULAR, 49 INDETERMINATE) | ≤ 10% |
| C0 inner extent | 0.7194–2.1246 (G-q) | 0.72–2.1 ± 0.05 |
| C3 islands, outer (centre ρ 8.350) / inner (centre ρ 0.886) | NOT CHAOTIC on both arms, 10/10 each | both arms not high |
| C4 D₂ on the island orbits | < 1.3 in both windows | < 1.3 |

- **Pooled thresholds** (class-wise max over 4 Kerr levels, 200 training orbits): λ₂ p99 4.18e-5, ρλ p99 0.377,
  D₂A p99 1.126, D₂B p99 1.180.
- **The Kerr null's d_sep:** min 1.1e-4, p5 6.0e-3, median 0.061. The whirl levels reach close to the separatrix
  boundary.
- **The island centres** found by our own Newton step reproduce the published values: u₀ at ρ 8.350 (CLA: 8.35) and
  u₀′ at ρ 0.886 (CLA: 0.886).
- **The double well shows why the AND rule is needed.** The variational arm alone (ρλ) false-alarms on 8% of the
  orbits nearest the hyperbolic point (the MEGNO mechanism, near-hyperbolic transit), and the non-variational D₂ arm
  never does.
- **Accuracy notes:**
  - C0 inner pilot: floor_hit (drift 1e-6 at tol 1e-13 vs target 1e-9). Per-orbit acceptance at 1e-8 decides
    instead; the 20 excluded orbits would all have been CHAOTIC (unscored, drift 1.0e-8 to 1.0e-6). Exclusion can only
    lower the chaotic fraction.
  - C0 outer pilot PASS at tol 1e-12.
  - DW pilot floor_hit (8.9e-10 at 1e-13), with all 200 accepted at 1e-9.
  - C3 drift ≤ 3.5e-10.

**Pre-stated A7 FINDING (C0 level, read under D_B9 at 1e-9):**
- 95 of 100 inner orbits leave D_B9 before N_ret: median 16 returns, p90 46, max 126.
- **Of the 75 base-domain CHAOTIC inner orbits, 75 (100%) leave D_B9 before 500 returns.** None stays in D_B9, and
  none leaves after 500 returns still CHAOTIC.
- The 5 inner orbits that never leave D_B9 read INDETERMINATE (2) or are excluded on accuracy (3); none reads
  CHAOTIC.
- Outer: 0 exits.
- **Prediction (≥ 50% leave before 500): HELD**, at 100%.
- **Reading:** at the C0 level, the published inner chaos lives entirely in orbits that come within the B9 exclusion
  of the ring singularity (about 0.025) within tens of returns. Inside D_B9 this level yields no chaotic reading.
  This concerns ONE level of the published point and says nothing yet about F5-R's own levels, which are the
  counted screen.

**SEALING (C0 is a shared comparison level):** these numbers are sealed by this commit and the sha256 of
results/197_cgates.json. Only pass/fail status goes to The Bridge until V13's C0 is sealed.
- sha256(results/197_cgates.json) = dd6c102c7134d7430fb2bb04f0566a44c27b2969e5f7147e4a4435378d621c07

## §2 OWN LEVELS (geometry only; results/197_own_levels.json)
- **Grid:** E 0.900–0.995 (step 0.005) × Lz 1.00–4.50 (step 0.05), 1420 levels per point. Components are labelled
  inside D_B9 (A3), and any component touching D's boundary is PLUNGE (orbits that leave D count as plunging).
- **Counts:**
  - p1: T1 109, T2 0, T3 0;
  - p2: T1 119, T2 0, T3 0;
  - F5-R: T1 53, T2 0, T3 0.
  **No T2 or T3 level exists inside D_B9 at any point** (a registered result under §2.4).
- **At F5-R (and at P0, checked at (0.95, 3)), the MN-type inner region classifies as PLUNGE:** it abuts the
  ring's B9 exclusion. Only the outer region is bound inside D.
- **Selected own levels, by rules (c) and (d) only (no T2 or T3 exists for (a) and (b)):**
  - p1: (0.975, 3.7) [c], (0.95, 3.3) [d];
  - p2: (0.975, 3.75) [c], (0.95, 3.3) [d];
  - F5-R: (0.96, 3.4) [c], (0.945, 3.15) [d].
- **Shared levels (V13, The Bridge):** p1 (37/40, 29/10); p2 (9/10, 13/10) (V13 A5, replacing the Lz = 0 level,
  which was D-incompatible); F5-R (19/20, 3); plus C0.
- **Predictions vs topology:**
  - p1 "no T2/T3": HELD.
  - p2 "T1": HELD.
  - F5-R's prediction ("chaos concentrated in the inner region and at the neck, with a candidate region inside D on
    ≥ 1 level"): its STRUCTURAL premise has already failed, since under D_B9 there is no inner region or neck.
    Whether any chaos exists in F5-R's outer region is what the screen measures.

## Counted-screen driver (screen_point), smoke-tested in scratch before any counted orbit
- **Smoke** (p1, n = 6, N_ret 60, in scratch; numbers meaningless): every path executed and the seal was written.
- **CAUGHT: an empty-threshold pass.** With too few null orbits (fewer than 20 training orbits per level),
  thresholds are None and every verdict is CANNOT-DISCRIMINATE, as it should be. But C1 printed "pass: True",
  because 0 CHAOTIC out of an empty set reads as "no false alarms" (the shape of silent_nulls 73). It is fixed in
  both screen_point and cgates: no thresholds means C1 = NO-THRESHOLDS, not passed. The sealed C-gate run is
  unaffected; it had thresholds (4 levels, 200 training orbits).
- candidate_regions was exercised on real data (the C0 inner base-domain CHAOTIC orbits; a code test only): one
  region, with the 200×200 grid occupancy, UPOs inside and return-time percentiles produced.
- The screen refuses to start unless the sealed C-gates passed (C1, DW, C0 inner/outer, C3/C4).

## C0 EXCHANGE with V13 (2026-10-17; both sealed before exchange: tabula a1c5051 / dd6c102c…, V13 d24e034 / 6a705e2b…)
V13 (The Bridge): its own code, indicators (NAFF log10|Δν| over two halves AND the 0-1 test K) and χ 0.9 Kerr null
(C1 held-out 0/136); 60 orbits per region; acceptance 1e-8.

| quantity | tabula | V13 | §7 / A1 rule | result |
|---|---|---|---|---|
| inner CHAOTIC | 75/80 = 0.9375, CP95 [0.860, 0.979] | 49/50 = 0.98, CP95 [0.894, 0.999] | 95% CIs overlap | AGREE |
| outer CHAOTIC | 0/100, CP95 [0, 0.036] | 0/60, CP95 [0, 0.060] | CIs overlap | AGREE |
| B9: inner orbits leaving before N_ret | 95/100 (median 16 returns, max 126) | 59/60 (median 15, max 116) | — (A7 finding) | AGREE |
| B9: base-CHAOTIC orbits leaving before 500 returns | 75/75 | 49/49 | — | AGREE |
| region overlap (Jaccard ≥ 0.5, 200×200) | sea spans ρ 0.7201–2.1237 (section points, computed after the seal from the sealed run's orbits) | section points not stored | Jaccard | **NOT EVALUABLE** (V13 limitation, stated) |
| accuracy exclusions | 20/100 (would-be CHAOTIC, unscored) | 10/60 (unscored) | — | — |

- **Joint reading:** two independent screens, with different indicators, code and Kerr nulls, agree that the
  published C0 inner chaos is real (≥ 86% of readable inner orbits), that the outer region is not chaotic, and that
  NO base-chaotic orbit stays inside D_B9 for 500 returns.
- **Precision:** this does NOT mean the sea "lives inside" the excluded neighbourhood. Our section points show the
  chaotic orbits roam the whole inner region (ρ 0.72–2.12). What is established is that every one of them reaches
  the singular-ring / CTC exclusion (within ~0.025 of the ring) within ≤ 126 returns.

## AMENDMENT A9 (2026-10-17, BEFORE any counted-screen result exists): exact section boxes
- **Noticed:** for the p1 shared level my classifier gives the bound region's equatorial x-interval as
  [3.2728, 7.6992], and V13 gives [3.271, 7.756].
- **Cause:** my §2 classifier uses a log grid (500 points over x − 1 ∈ [0.05, 39]) whose spacing near x ≈ 7.7 is
  about 0.09. Its interval endpoints are grid-limited, and that interval also defined the analysis box (§10), which
  sets every normalised statistic (I2 windows, d_min, d_sep) and the shared 200×200 Jaccard grid.
- **Fix:**
  - The OFFICIAL counted-screen analysis uses section boxes whose x-edges are refined by bisection on
    K(x, y = 0) = 0 (the CZV), to 1e-12, starting from the classifier's bracket. p_x max is taken from that exact
    interval.
  - The analysis that screen_point performs at the end of each point used the grid-limited boxes. It is SUPERSEDED,
    and its sealed JSON is kept as a record but not used for comparison.
  - The orbits are unchanged.
- **Coverage limitation, stated:** launch points were sampled inside the grid-limited interval, so a strip of width
  ≤ ~0.09 in x at each edge of each screened region was not launched into. Orbits launched inside do visit that
  strip, and the section clouds use all crossings.

## AMENDMENT A10 (2026-10-17, before any counted result; quantum's point via The Bridge, V13 A7 mirrors it): saddle-in-D, not f_D
- **Why:** fast escape of SAMPLED orbits does not exclude a measure-zero chaotic saddle INSIDE D, and a horseshoe
  needs only that. So the per-point K20 verdict is **"saddle-in-D candidates found / none found within the search"**,
  where the search is the UPOs of period ≤ 3 from the Newton seed grid (A4) plus connections within 30 + 30 iterates.
  f_D is reported but does not decide it.
- **Per hyperbolic UPO:**
  - integrate one full period (n returns, from its section point) at the level's tolerance;
  - report whether the WHOLE orbit stays in D_B9 (no B9 exit) and is complete (n returns, base domain);
  - report its minimum D-margins along the orbit: x − 1, g_φφ, R², 1 − y² (running minima at the n-th crossing);
  - plus the earlier A1.4(b) items: eigenvalues, eigenvectors, period-n points.
- **Transition graph (A1.4(c)):** each numerical homoclinic or heteroclinic connection is marked "in D" iff every
  point of the connecting manifold segments, sampled at each integration step from the UPO through the
  intersection, stays in D_B9. Both UPO orbits must be in D.
- **Search extension (closes a gap in my own level rule):** at C0 and F5-R the MN-type inner region classifies as
  PLUNGE under B9, so §2 never screened it, and so never searched it for UPOs. Under A10 the UPO search (periods
  1–3, A4 grid) also covers every BASE-domain bound component at:
  - the C0 level (0.95, 3), whose inner-region UPOs already exist from the C-gate run (13 located, 11 hyperbolic);
  - the F5-R shared level (19/20, 3);
  - F5-R's own levels.
  Each hyperbolic UPO found there is tested for whole-orbit D_B9 containment.
- **Provenance note (2026-10-17):** libk20.dylib was rebuilt (adding the mode bit for downward crossings, used by the
  inverse section map) WHILE the counted screen was running.
  - The running workers survived (no crash; macOS replaced the file rather than rewriting the mapped pages).
  - Workers spawned later load the new binary. Its semantics for the modes the screen uses (0 = FTLE, 1 = section
    map) are unchanged: crossing direction defaults to upward and projection is still mode & 1.
  - Rule from here: development kernels are built under a separate filename; a binary that a run is using is never
    rebuilt.

## Shared-level geometry checks (2026-10-17; geometry only)
- **Bisection-refined box edges (A9),** sent to The Bridge for comparison with V13's brentq roots before any Jaccard:
  - p1 shared (37/40, 29/10): x [3.270714456306, 7.755572149181], p_x max 0.106266926039 (the grid gave
    [3.2728, 7.6992]; V13's quoted [3.271, 7.756]);
  - F5-R shared (19/20, 3): x [5.454197086440, 31.141918436652], p_x max 0.116565707598.
- **The p2 shared level (9/10, 13/10) is NOT a bound region.**
  - Its equatorial allowed interval is [1.1519, 9.4001] (matching V13), and that slice is inside D.
  - The 2D allowed component, however, connects to the horizon: cells down to x − 1 = 5e-4 at |y| 0.05–0.999, and it
    touches x → 1. 444k of its 1.23M cells lie outside D_B9.
  - Under §2 it is PLUNGE, so the in-run screen_point would have skipped it silently. That is a skip with no record,
    so it is now recorded here.
  - Proposed to The Bridge: (a) screen it anyway from the equatorial interval for comparability, reporting
    plunge/ESCAPE fractions; or (b) fallback with a 2D bound-in-D criterion. Until they decide, tabula screens it as
    in (a), in a separate run, and reports its topology as plunge-connected.
- The inverse section map (A10 stable manifolds: flip momenta, integrate to the next downward crossing, flip back)
  is verified: P⁻¹(P(z)) = z to 6e-12–7e-11 at p1 and P0.
- **A10.1 (definition, before any result):** a lone hyperbolic periodic orbit is not evidence of chaos, since
  integrable systems have them too (the double well's saddle).
  - **Tier 1:** a hyperbolic UPO (period ≤ 3) whose whole orbit is complete and stays in D_B9.
  - **Tier 2, a "saddle-in-D CANDIDATE":** a tier-1 UPO with a TRANSVERSAL homoclinic connection, or a transversal
    heteroclinic connection to another tier-1 UPO.
    - Found by intersecting W^u (P^n, forward) with W^s (P^-n, by momentum reversal), each grown from a fundamental
      segment at ε = 1e-6 for at most 30 iterates.
    - Manifold points whose map step leaves D_B9 are dropped, so every reported intersection lies on in-D manifold
      pieces.
    - Transversal means a crossing angle > 1e-3 rad that persists, within 50%, between ε = 1e-6 and 1e-7.
  - **Per-point K20 verdict:** "saddle-in-D candidates FOUND (tier 2)", or "tier-1 UPOs in D but no transversal
    connection in D found within the search", or "no tier-1 UPO in D within the search". Always "within the
    search": a null is a map of where we looked, not a theorem.
- **The Bridge confirmed the p2 finding independently** (v13_geom2d: flood fill on a 500×400 grid plus D_B9 per cell).
  The component touches x → 1 and |y| = 0.999, with 43% of its cells outside D_B9. Their shared-level rule had
  looked only at the equatorial interval.
  - They chose option (b): V13 A8 re-applies the fallback with a 2D bound-inside-D criterion. A new p2 shared level
    is pending; tabula keeps option (a) for p2 only until it lands.
  - p1 and F5-R pass their 2D test (p1 reaches |y| ≤ 0.18, F5-R |y| ≤ 0.47, 0% outside D).
- **Box edges agree to < 1e-11:** V13 p1 [3.2707144563061483, 7.755572149181034], F5-R
  [5.454197086440008, 31.14191843665211]. p_x max is still to be compared before Jaccard.
- **New p2 shared level (V13 A8, TheBridge 326d21f): (37/40, 3).** My 2D classifier gives T1, fully inside D_B9, at
  500×241 and 800×401. My bisection-refined edges are [3.388571137065809, 5.741146012209716] vs V13's
  [3.3885711370657745, 5.741146012209553]: agreement to 1.6e-13. SHARED["p2"] is switched.
  - The running screen loaded the old SHARED. At the old p2 level it finds no bound component and skips it (now on
    record).
  - The new level is screened by a resumed screen_point run, which re-uses every saved level and integrates only the
    new one.

## C3 EXCHANGE with V13 (2026-10-17; sealed both sides: tabula a1c5051 / dd6c102c…, V13 c9659af / a9264f32…), plus a flaw in my own C3/C4
- **Island centres agree:**
  - outer: tabula x 19.182949 (ρ 8.3503) vs V13 19.18295 (ρ 8.3503);
  - inner: tabula x 2.265080 (ρ 0.8859) vs V13 2.26508 (ρ 0.8859).
- **Verdicts:** tabula 20/20 accepted, I1 high 0, I2 high 0, so C3 PASS. V13 20/20 READ, 0 CHAOTIC, so PASS.
  AGREE.
- **FLAW FOUND IN MY OWN C3/C4 (found reading the sealed numbers; the gate verdicts are not changed, but their
  meaning is):**
  - D₂ = −9e-16 (window A) and −1e-16 (window B) on every island orbit.
  - A4 registered launches within 1e-3 (normalised) of the island centre, so each orbit traces a tiny invariant
    curve, and its whole section cloud (~1e-3 across) is SMALLER than the fixed D₂ scaling windows
    (r ∈ [0.01, 0.05] and [0.02, 0.10]). Every pair falls below every r, C(r) is flat, and the slope is 0.
  - So **C4 (D₂ < 1.3) and the I2 half of C3 passed VACUOUSLY**: they measured nothing. C3 is a real pass only
    through I1 (ρλ and λ₂ below threshold).
  - Silent-null shape: a statistic whose window does not reach the object reports a "pass". The < 200-pairs guard
    did not fire, because all ~2M pairs sit below the window's FLOOR rather than above its ceiling. A guard that
    checks only the low-count side misses the saturated side.
- **What still shows I2 on genuine regular orbits:** the Kerr null tori (D₂ p99 1.13 / 1.18, from the training set)
  and the A8 double-well near-separatrix curves (D₂ ≈ 1 in the smoke run). There, the clouds span the windows.
- **Proposed supplement (post-hoc, labelled; it does not replace the registered gate):** re-run C3/C4 with V13's
  launch geometry (x offsets ±0.2–4% of x_c, p_x = 0), so the curves span the D₂ windows. Also add a saturation
  guard: I2 = "mixed" when C(r_max) equals the total pair count or C(r_min) is within 1% of it, i.e. the window
  sits outside the cloud's scale.

## AMENDMENT A11 (2026-10-17, BEFORE any counted-screen verdict has been read; The Bridge agreed): an I2 window-scale guard
- **Rule, per D₂ window (A and B)**, with n_pairs the total number of pairs:
  - **"saturated":** C(r_min) ≥ 99% of n_pairs. The window lies ABOVE the cloud.
  - **"below-scale":** C(r_max) ≤ 1% of n_pairs. The window lies BELOW the cloud's scale.
  - The existing "low-count" guard (C(r_min) < 200) stays.
  In all three cases D₂ for that window is None, so I2 = "mixed" (neither high nor low).
- **Effect under the AND rule:** it can only turn a vacuous I2 into "mixed", so CHAOTIC → INDETERMINATE or REGULAR →
  INDETERMINATE. It can never create CHAOTIC.
- **Reported per cell:** how many accepted orbits each guard fired on, and how many readings it reclassified. Raw
  slopes are kept as D2_raw.
- **Applies to:** the official counted analysis (analyze_point) and the supplementary C3/C4. It does NOT re-grade the
  sealed C-gates; C3 stands through I1, and C4 is recorded as vacuous.
- **Status at commit:** the counted screen is still running. The only verdict lines it writes are its in-run
  analysis, which A9 has already superseded, and none has been read. From here only progress lines are inspected.

## AMENDMENT A12 (2026-10-17, BEFORE the official analysis has run): confirming tier-2 crossings
- **Why:** first hits between W^u and W^s polylines are unrefined. Two long, sparsely sampled segments can "cross"
  spuriously, and A10.1's ε-persistence and angle test does not rule that out. (The Bridge raised this for V13,
  whose A9 uses Newton refinement in (s, s′). Mine is kept independent: seed resampling.)
- **Procedure:**
  - Each manifold point carries its fundamental-segment seed parameter t ∈ [0, 1].
  - For the first hit at each ε, the two seeds generating the hit segment on W^u, and likewise on W^s, are resampled
    at 20 points and mapped the same number of iterates through D (any step leaving D_B9 drops the point). The
    intersection is recomputed on the refined polylines.
  - **CONFIRMED** iff the refined chords on both manifolds are < 1e-2 (normalised), the refined point moves by less
    than the original chord, and the refined angle is within 50% of the unrefined one.
  - A segment that straddles two iterates is "not refinable", so unconfirmed.
- **Tier 2** now requires A10.1 (angle > 1e-3, persistence between ε 1e-6 and 1e-7, in-D manifolds) AND A12
  confirmation at both ε.
- **Reported per edge (The Bridge's request, for edge-by-edge matching with V13):** the UPO pair (period-n section
  points), the refined crossing point (x, p_x), the angle, the iterates, the chords, and confirmed or not.
  Unconfirmed hits are reported and do not count.
- **Protocol deviation, recorded (2026-10-17):** while agreeing to add C0 structure (informational) to the sealed
  analysis, The Bridge's message disclosed summary COUNTS from V13's C0 structure stage before tabula's C0 structure
  stage had run.
  - Mitigation: tabula's C0 UPO search had already run (C-gate run, a1c5051), and every rule for the in-D test,
    manifolds and edge confirmation (A10, A10.1, A12; last commit 5a7d93d) was committed before the message. No
    procedure can be tuned toward their counts.
  - The counts are not restated here (silent_nulls 50: disclose the class, not the content).
- **C0 add-on spec (agreed):** level (19/20, 3) at χ 0.9, q 0.95; Σ = {y = 0, p_y > 0} in (x, p_x); tier 1 = the
  whole orbit in D_B9; edges only through in-D manifold segments; base-domain-only hyperbolic UPOs FLAGGED, not
  dropped; matching by UPO section points (1e-6) and refined crossing points.
- **Disk-full stop and resume (2026-10-17).** The screen's watchdog killed the run during F5-R's Kerr null (free disk
  4 GB, below its 5 GB floor; tree 526 MB, sysfree 35%). The data volume was 99% full machine-wide. tabula's share:
  results 1.8 GB, scratch 0.2 GB. Nothing was deleted, since that is the user's call.
  - User decision: resume now with MINDISK = 2 GB. The resumed run re-uses every saved level, integrates the rest of
    F5-R's null, and screens p2's new shared level (37/40, 3). Remaining output ≲ 0.2 GB.
- **The resume was killed immediately:** free disk had fallen to ~1.9 GB (df -g / showed 0), below the user's 2 GB
  floor. Tree 21 MB, so tabula was not the cause; swap stood at 7 GB of swapfiles, which The Bridge traced to its own
  memory-heavy control run. The screen stays stopped until space is freed. All completed levels are saved and
  resume without loss.
- **PAUSED by the user (2026-10-17 07:49).** The auto-resume watcher is stopped and no screen process is running. Resume on the user's word: `--screen p1 p2 F5R` re-uses every saved level.
- **RESUMED by the user (2026-10-17 19:33):** the overnight chain scripts/k20_chain.sh runs the screen (resume), then the C3 supplement, then the official analysis (p1, p2, F5-R), then the C0 add-on. Each stage runs under the watchdog (≤ 4 workers, MAXMB 2048, MINDISK 5) and must end with exit=0, or the chain stops. The user is away; coordination is with The Bridge, with routine calls logged here.
- Chain: stage 1 (counted screen resume: F5-R Kerr null and p2's new shared level) ended exit=0 at 2026-10-17 21:29; the C3 supplement started.

## SUPPLEMENTARY C3/C4 (post-hoc, labelled; results/197_c3_supplement.json, sha256 e3b3f895…54e2)
Launch geometry from V13: x offsets ±0.2–4% of x_c, p_x = 0. Base domain, 1e-8. A11 guard on.
- **C3: 20/20 accepted, I1 high 0, I2 high 0 → PASS** (both islands).
- **C4, inner island: a GENUINE pass.** All 10 curves span the windows: D₂A 0.62–1.10, D₂B 0.17–1.08, all < 1.3.
  This replaces the registered vacuous pass with a real one.
- **C4, outer island: 7/10 NOT EVALUABLE** (A11 "saturated" in both windows). The outer box is 25.7 wide in x, so a
  4% offset at x_c ≈ 19 still gives curves only ≲ 0.03 across in normalised units. The 3 evaluable curves read D₂A
  1.07–1.20 and D₂B 0.40–0.96, all < 1.3. The JSON's C4_pass = False for the outer island is the conservative
  reading (unevaluable counts as not-pass). No curve read D₂ ≥ 1.3.
- **The guard bit 7/10 times on the outer island and 0/10 on the inner.** This confirms the registered C3's
  vacuity was real and is now caught.
- **Observation (no rule change):** island orbits mostly read INDETERMINATE, not REGULAR. "REGULAR" needs BOTH arms
  below the Kerr p95, and island D₂ ≈ 1.07–1.10 sits at the D₂A p95 (1.084). So CHAOTIC is the operative verdict;
  REGULAR counts understate regularity and should not be read as "fraction regular".

## OFFICIAL COUNTED ANALYSIS (sealed 2026-10-18; prereg 9aca9a4 + A1..A12; results/197_analysis_{p1,p2,F5R}.json)
sha256: p1 5623aa8b45f4bbe601e5741f0c7bde377ebc5d63000eb45e233fd01245dbd553 · p2
928f0ce5ff54281ce896f6288a438a29346015d818029078f57cef332f1dbe0f · F5-R
e6a21746557ec961a63397c782eb931e9033907c4242138c96e9908de4cfd7e5.

**Sampled-orbit screen (B9 reading, 1e-9, A9 exact boxes, A11 guard):**
- CHAOTIC is 0/200 at EVERY screened level of every point, CP95 upper 1.8%.
  - p1: own (0.975, 3.7), own (0.95, 3.3), shared (37/40, 29/10).
  - p2: own (0.975, 3.75), own (0.95, 3.3), shared (37/40, 3).
  - F5-R: own (0.96, 3.4), own (0.945, 3.15), shared (19/20, 3).
- n_analysed is 200/200 everywhere, with no accuracy exclusions and no pilot floor_hit. No candidate region exists.
- The A11 guard fired on 1 orbit at p1 (0.95, 3.3) and 1 at F5-R (0.945, 3.15); it reclassified 1 each.
- C1 (pooled held-out Kerr) passes: p1 0/550, p2 0/400, F5-R 0/600.
- **Predictions:** p1 CHAOTIC ≤ 5%: HELD (0%). p2 ≤ 10%: HELD (0%). F5-R "candidate region inside D": NOT
  supported by sampled orbits (0%), as its structural premise had already failed (§2 log).

**Saddle-in-D (A10/A10.1/A12):**
- **p1:** 42 hyperbolic UPOs.
  - Most come from the A10 extension into near-horizon components (x 1.005–2.77), and those leave D_B9 or sit at
    R² ≈ 0.14 < 0.25.
  - Tier 1: 2 period-2 UPOs at the shared level, with trace = 2.000 (marginal, resonance saddles).
  - No confirmed connection.
  - VERDICT (registered wording): "tier-1 UPOs in D but no transversal connection in D found within the search".
- **p2:** 1 hyperbolic UPO (period 3, trace 2.0005, marginal), in D; no connection. Same verdict wording.
- **F5-R:** 29 hyperbolic UPOs, 16 in D_B9.
  - Most tier-1 orbits are INNER-region UPOs found only by the A10 extension: x ≥ ~1.94, min x − 1 ≈ 0.94–1.15,
    R² ≥ 2.78.
  - 134 graph rows; 58 hits at ε = 1e-6; 5 A12-confirmed at ε = 1e-6; **1 transversal and confirmed at BOTH ε → TIER
    2.** VERDICT: "saddle-in-D candidates FOUND (tier 2)".
  - **The edge:** level (19/20, 3), heteroclinic, from period-1 A (3.602745, 0) (trace 8.11, closure 5e-13) to
    period-3 B (3.348209, 0) (trace 32.6, closure 2.4e-11).
    - Refined crossing (x, p_x) = (3.4393518, −0.0895437), stable to ~5e-9 between ε = 1e-6 and 1e-7.
    - Angle 1.24 rad; iterates (n_u, n_s) = (5, 3) at 1e-6 and (6, 4) at 1e-7.
    - Refined chords 3.9e-5 and 5.7e-5.
  - **CAVEAT, reported with the verdict:**
    - The CONFIRMED graph has NO CYCLE (no B → A edge and no confirmed homoclinic). A single one-way heteroclinic
      edge is not by itself a horseshoe; symbolic dynamics needs a cycle. The registered tier-2 definition (A10.1)
      is weaker than that.
    - Near misses: the period-1 pair D±(3.641936, ±0.067821) (trace −18.05) has mutual edges D+ → D− and D− → D+
      confirmed at ε = 1e-6 but NOT at 1e-7. Such a 2-cycle would be a horseshoe candidate. The registered rule
      rejects it, and it is listed for quantum and V13 as the first thing to check.
    - A homoclinic hit on the period-1 orbit (3.290238, 0) at (0.945, 3.15) is rejected: the angle changes from
      0.52 to 0.04 between ε, so the two runs found different crossings.
- **Reading:**
  - The sampled-orbit screen finds NO chaotic sea inside D at any of the three points.
  - F5-R's inner region, which every sampled chaotic orbit leaves (C0/A7), nevertheless contains hyperbolic periodic
    orbits whose whole orbits stay in D_B9, with one confirmed transversal heteroclinic connection inside D.
  - That is the measure-zero-saddle scenario quantum anticipated: evidence of a chaotic invariant set inside D, but
    not yet a closed cycle.

## COUNTED-SCREEN EXCHANGE with V13 (2026-10-18; both sealed: tabula 41d57be, V13 c365279)
Shared levels. V13 has 60 orbits per level; tabula has 200. Both use Clopper–Pearson 95% (two-sided). Times are in
each point's own M units (tabula's M = 1 values × M).

| point (shared level) | tabula CHAOTIC | V13 CHAOTIC | CIs | return-time median: tabula / V13 | chaotic-cell Jaccard |
|---|---|---|---|---|---|
| p1 (37/40, 29/10) | 0/200 [0, 0.018] | 1/60 [0.0004, 0.089] | overlap → AGREE | 315.0 / 319.5 → AGREE (×1.01) | 0 (V13 331 cells, tabula 0) → **FAILS** the ≥ 0.5 criterion |
| p2 (37/40, 3) | 0/200 [0, 0.018] | 0/60 [0, 0.060] | AGREE | 752.5 / 753.6 → AGREE | both empty → AGREE |
| F5-R (19/20, 3) | 0/200 [0, 0.018] | 0/60 [0, 0.060] | AGREE | 13676 / 14006 → AGREE (×1.02) | both empty → AGREE |

- **Boxes and grids are identical** after the M scaling: x edges to < 1e-11, and p_x half-width ×M = 0.53133, 0.96890
  and 10.37435 on both sides.
- **All-read coverage:** tabula 28228 / 27973 / 24580 cells (200 orbits per level); V13 12855 / 13095 / 11898 (60
  orbits). V13 published only the count of read cells, so all-read overlap is NOT computable, only compared by count.
- **The p1 disagreement, diagnosed (post-seal, from sealed data; nothing re-run):**
  - V13's single CHAOTIC orbit (i = 55, x0 = 6.8700; A1 −6.41 vs threshold −7.21; A2 K = 0.0275 vs threshold
    −0.0025) occupies 331 cells.
  - One tabula orbit (x0 = 5.2558) covers 97% of those cells, i.e. the same region. It reads **REGULAR** with margin:
    λ₂ 5.5e-5 vs p99 9.6e-5; ρλ 0.27 vs 0.46; D₂ 1.02 / 1.01 (a curve).
  - V13's call rests on a 0-1 test K of 0.0275 against a NEGATIVE threshold. Regular orbits' K fluctuates by a few
    hundredths around 0, so the threshold plausibly lies inside regular-orbit noise. Reported to The Bridge as theirs
    to adjudicate. tabula's rules are unchanged.
- **Own levels (tabula only):** 0/200 at all 6. V13 has no counterpart.

## F5-R EDGE EXCHANGE with V13 (2026-10-18; both sealed: tabula 41d57be, V13 A10 085ac13)
**UPO lists** at (19/20, 3) (V13 p_x is in M = 89 units, so tabula × 89):
- 8 of V13's 11 in-D hyperbolic UPOs match tabula's to 1e-5: UPO0, 2, 3, 4, 6, 7, 8, 10.
- V13 UPO1 and UPO5 (period 3) were NOT found by tabula's 20×20 Newton grid.
- **V13 UPO9 (period 2): tabula finds this orbit but its D-test says it LEAVES D_B9.** A D-test disagreement, flagged
  to The Bridge. tabula's dilated mask is on the strict side by ≤ h = 5e-4.
- tabula also lists the outer (6.15212, 0) period 2, which is marginal (trace 2.005).

**Edges:** V13 confirms 35/42 (multiple shooting), giving an SCC {2..8} with self-loops at 2–7, i.e. cycles: a
horseshoe-candidate structure. tabula confirms 1 (UPO8 → UPO7, crossing (3.43934, −7.970) in M units). V13 has no
8 → 7.

**Why tabula's graph is so sparse: a DEFECT IN TABULA'S METHOD, found in this comparison (post-seal):**
- **(1) A bridging-segment bug.** manifold() concatenates successive iterates into ONE polyline per branch, so the
  segment joining the last point of iterate k to the first of iterate k+1 is spurious.
- **(2) First-hit only.** The tier-2 test examines only the FIRST hit per pair per ε. A spurious bridging-segment hit
  can therefore mask every real crossing behind it.
- A12 correctly refused such hits ("not refinable": the segment straddles iterates). Many first hits in tabula's
  F5-R rows are exactly that. But no later hit was then examined.
- **Consequence:** tabula's "no confirmed cycle" is a SENSITIVITY LIMITATION of its search, NOT evidence against
  V13's SCC. Also: refinement at only 20 resampled seeds can miss a crossing on a strongly folded segment ("no
  crossing after refinement").
- The registered verdict ("tier 2 FOUND at F5-R; none at p1/p2") stands and AGREES with V13 on existence. V13 has no
  in-D hyperbolic UPOs at p1/p2; tabula has only marginal trace ≈ 2 ones and no edges.

**Proposed A13 (post-hoc and labelled as such; it does not replace the sealed analysis):**
- Split the manifold polylines per iterate, so no bridging segments exist.
- Examine EVERY hit, not just the first, and A12-confirm each at both ε.
- Report the confirmed graph and its strongly connected components.
- This independently tests V13's SCC with tabula's own manifold code.

**Ring-proximity caution (V13's point; agreed and sharpened):**
- tabula's tier-1 UPOs keep x ≥ 1.942, i.e. ≥ 0.02 from x_s = 1.92192.
- V13 reports its connecting orbits reaching min x − 1 = 0.939 (x = 1.939, 0.017 from the ring). If that point is
  near y ≈ 0, a ±0.025 box around it reaches x < x_s, where the CTC region starts, and the orbit would violate B9.
  V13 is asked to check that its connecting-orbit D test is the BOX test, not a point test.
- **In any write-up:** "inside D" here means within a few hundredths of a naked curvature singularity.

## A13 (POST-HOC, labelled; registered before it runs, AFTER both sides' edge results were seen and exchanged)
- **Scope:** F5-R (19/20, 3) and C0, on the tier-1 UPOs of the sealed analyses, grouped by base-domain equatorial
  component. Each component uses its own pilot tolerance.
- **Method:**
  - Skip any segment that joins two iterates (fixes the bridging bug).
  - For each ordered UPO pair, A12-confirm up to the first 10 non-bridging hits (ordered by n_u + n_s) at each ε.
  - An EDGE is confirmed iff the SAME refined crossing (within 1e-6, normalised) is confirmed at both ε, with angle
    > 1e-3 and stable within 50%.
  - Report the confirmed graph and its strongly connected components (self-loops count).
- **Purpose:** an independent test of V13's SCC {2..8} with different manifold code and a different confirmation
  method. It does not change the sealed verdicts.
- **Note:** the C0 add-on (running) uses the same structure_stage, so it carries the same sensitivity defect. Its edge
  graph is to be read through A13 as well.
- **V13's B9 implementation (from The Bridge):** a 9-sample box test (centre, 4 corners, 4 edge midpoints), not a
  full box. That plausibly explains the UPO9 D-test disagreement. V13 is re-testing every edge and UPO with a strict
  box (21×21 grid plus local minimisation of g_φφ). tabula's dilated-mask test covers the full box (strict by ≤ h).
- **p1 disagreement ADJUDICATED by V13 (post-hoc, labelled; the registered verdicts are unchanged on both sides).**
  V13's orbit 55 is LIKELY REGULAR:
  - λ_max decays like ln t / t (4.9e-5 at 200k returns, like a regular control);
  - its section is one smooth curve (D₂ 1.002), ν = 0.49849, near the 1/2 resonance;
  - its windowed 0-1 K swings from −0.041 to +0.028, and V13's AND rule fires on 46/100 windows of this regular orbit;
  - V13's Kerr-null A2 threshold (sd 0.0020) is 8× narrower than the regular-orbit K scatter at p1 (sd 0.0168).
  The p1 region-criterion FAIL stands as registered, with this explanation attached. tabula's 0/200 is the correct
  reading at p1, and the earlier diagnosis (a region tabula reads REGULAR with margin; a negative A2 threshold) is
  confirmed.
- **V13 strict-box recheck (post-hoc, labelled):** a full ±0.025 box (21×21 plus local minimisation along densely
  sampled orbits), controls passing.
  - All F5-R edges and in-D UPOs survive; the SCC is unchanged.
  - **The F5-R SCC's margin to the CTC is ≥ 7.2e-4,** only just above tabula's mask resolution (strict by
    ≤ 5e-4). Registered expectation for A13, stated before it runs: tabula's stricter-by-≤h mask may drop some
    F5-R connections on RESOLUTION grounds. Any such drop is to be reported as resolution-limited, not as a
    disagreement.
  - UPO9 is strictly inside by 5.1e-5, below tabula's resolution. So tabula's "leaves" is within resolution, not a
    contradiction.
  - Ring distance corrected by V13: min x (1.9392 at F5-R) occurs at y ≈ ±0.095, so the distance to the ring point is
    ~0.096 (0.017 was an x-difference only).
- **Second blinding deviation (by class; content not restated):** V13's recheck message included C0 edge and SCC
  information while tabula's C0 add-on was still running and unsealed. Mitigation as before: tabula's C0 procedure
  (structure_stage, 87ed331; A13, e7f38be) was committed before the message.
- **Blinding guard (fleet practice 3, relayed 2026-10-18).**
  - tabula has its own copy in SpaceTime/tools/: EMBARGOES.json, blind_check.py and blind_hook.sh, adapted from
    TheBridge/tools.
  - Active embargo: "tabula-C0-addon-to-bridge", recipient "*" (so it also catches socket-path addresses), until the
    C0 add-on is sealed.
  - Tested: an embargoed message is blocked (checker exit 1, hook exit 2); a clean one passes; a uds-addressed one is
    blocked.
  - **NOT wired** into .claude/settings.json: that is a config change, and tabula does not change its settings on a
    relayed request. It waits for the user's direct OK. Until then the checker is run by hand before any C0-adjacent
    message.

## C0 ADD-ON SEALED; HOLD for restart (2026-10-18 13:12)
- results/197_analysis_C0.json, sha256 1eb357f8583f8bd8727a21354125f19ed640a93f43384faa09ecb2e331f6d1c4.
  - INFO verdict: "tier-1 UPOs in D, no confirmed connection" (13 hyperbolic, 10 tier 1).
  - It uses the same structure_stage, so it carries the same sensitivity defect (bridging segments plus first-hit
    only). A13 will re-test it.
- The C0 embargo in tools/EMBARGOES.json is lifted (both sides sealed).
- HOLD (relayed by the user): no new runs until after the Mac restart. A13 is held.

## A13 RESULT, SEALED (2026-10-18, after the restart)
- results/197_a13.json, sha256 c2343e2456f1fed7aca62fe873ad2b91ee61145d37f41e494e06f6c09e4640c9. Serial run, exit 0,
  peak footprint 623 MB. Post-hoc, labelled (A13 rules: no bridging segments, ≤10 hits per pair, the same refined
  crossing at both ε, SCC of the confirmed graph).
- **F5-R inner component** (x ∈ [1.922, 5.030]): 7 tier-1 UPOs, **22 confirmed edges, one SCC = all 7 UPOs.**
  Transversality angles 0.33–1.24 rad (≫ the 1e-3 floor).
- **C0 inner component** (x ∈ [1.930, 4.976]): 8 tier-1 UPOs, **27 confirmed edges, one SCC of 7 UPOs** {0,1,2,3,5,6,7}.
  UPO 4 (section point x 3.3631, p_x 0) has out-edges (→2, →6) but no confirmed in-edge, so it is outside the SCC.
  This **supersedes the C0 add-on's "no confirmed connection"**: that INFO verdict was the sensitivity defect A13 was
  built to remove, as pre-stated.
- **Outer components** (F5-R x > 5.45, C0 x > 5.57): 0 confirmed edges, no SCC, at both points.
- **Defect found on reading (not fixed, not affecting the inner results):** the F5-R outer component lists 4 UPOs that
  are 2 distinct orbits each listed twice (section points 6.15212/0 and 11.056215/0.066995). UPO de-duplication in
  that component did not merge them. It has 0 edges either way, so the SCC result is unchanged.
- Not yet compared with V13. Exchange next: commit + sha first, then edges/SCCs mapped to V13 indices through section
  points. Registered caveat stands: any F5-R edge tabula lacks is to be read as resolution-limited first (margin
  ≥ 7.2e-4 vs mask h 5e-4).

## A13 ↔ V13 F5-R EDGE COMPARISON (2026-10-18; both sealed: tabula 771a5af, V13 085ac13 / c4daaa7)
- **Index map:** tabula UPO 0..6 → V13 8, 2, 4, 0, 3, 6, 7. V13 UPOs 1, 5 and 10 are not in tabula's tier-1 set.
- **Edges:**
  - Agree: 9 (2→2, 2→4, 3→3, 4→2, 4→4, 4→8, 6→3, 6→6, 8→2). The 2→2 and 4→4 crossings match to ≤1e-6.
  - V13 only: 13. Read first as tabula sensitivity/resolution (registered).
  - tabula only: 11, all on pairs V13 never tested.
  - tabula Y / V13 N: 2 (2→6, 3→4). These are at DIFFERENT crossings, a p_x-mirror pair at (2.81133, ∓37.398 in M
    units), offered to V13 for multiple-shooting checks.
- **SCCs:** both contain the core {2, 3, 4, 6, 7, 8}. V13 adds 5 (not found by tabula); tabula adds 0 (untested by
  V13). **The cycle structure is confirmed by two independent manifold codes.** C0 edges sent in tabula indices; V13's
  C0 list is pending.

## A13 ↔ V13 C0 EDGE COMPARISON (2026-10-18; V13 A10 085ac13, file v13_s7_C0_edges_bridge.txt)
- **Map** (re-derived independently, agreeing with V13's): tabula → V13 0→2, 1→4, 3→0, 5→3, 6→1. tabula 2, 4 and 7
  have no V13 match. V13 5–10 are not in tabula's tier-1 set.
- **Edges on mapped pairs:**
  - agree 5 (1→1, 3→3, 2→4, 3→4, 4→1); tabula-only 7, all on pairs V13 did not test; V13-only 11;
  - **0 Y-vs-N contradictions.**
  - Shared SCC core {1, 3, 4} (V13 indices).
- **Same orbit or not** (scripts/197d_crossing_orbit_match.py: tabula's crossing iterated ≤12 steps either way, closest
  approach to V13's):
  - 2→4: SAME heteroclinic orbit (P³ lands on V13's to 2.8e-6, i.e. their rounding);
  - 3→4 and 4→1: 4.2e-3 at P^±1, inconclusive;
  - 1→1 and 3→3: 0.37, DIFFERENT homoclinic orbits.
  So C0 agreement is in edge existence, with one crossing confirmed identical.
- **Combined (both points):** two independent codes find a strongly connected core of in-D hyperbolic UPOs with
  transversal connections at F5-R and at C0. Wording for V13 FINDINGS was proposed, with the ring-proximity caveat.

## QUEUED (not registered; for when the user is back)
- Targeted A12 check: seed tabula's confirmation at V13's 13 F5-R-only and 11 C0-only crossings, with mask h = 5e-4 and
  1e-4 side by side. This separates search-cap misses from mask-resolution drops. It must be pre-registered before any
  run.
- No overnight launch (2026-10-18): nothing registered was ready, and the Bridge's premise of a pre-stated
  h = 1e-4 rerun was corrected; the Bridge accepted.

## A14 PRE-REGISTRATION (2026-10-18, user present; written and committed BEFORE any code runs)
**Question.** Why does tabula lack 13 of V13's confirmed F5-R edges and 11 of its C0 edges? Is each a search-cap miss
(the connection is real and inside tabula's D_B9), a resolution/box-margin drop (real, but outside tabula's strict
mask while inside the base domain), a domain disagreement (outside even the base domain in tabula's kernel), or not
reproducible in tabula's kernel at all?
**Inputs (read-only, hashes verified against V13's seals):**
- v13_a10_F5R.json 3e098030… and v13_a10_C0.json a4602110…, both @085ac13. Every edge with CONFIRMED_MS = true is
  used: 35 F5-R and 16 C0. The crossing point is ms_13.point.
- V13 UPO section points from v13_upo_F5R_19o20_3.json and v13_upo_C0_19o20_3.json.
- Units: F5-R p_x(V13) = 89 × p_x(tabula) (M = 89); C0 p_x is 1:1; x is 1:1.
**Method (tabula kernel, level (19/20, 3), each point's inner-component pilot tolerance as in A13):**
- For a V13 edge i→j with crossing q, apply the section map P forward n = 1..15 times. d_f is the minimum over n of
  the normalised distance (x/(xb−xa), p_x/(2 pm), refined inner box) to the section points of V13's UPO j. Apply
  P⁻¹ the same way to UPO i, giving d_b. The statistic is s = max(d_f, d_b).
- Domain, along the iterates up to each side's argmin n: did any step leave D_B9 (orb[3] ≥ 0)? Did any step fail the
  base domain (map returns None)?
**Controls (computed before V13's points are read by this code; the threshold is fixed by them):**
- POS: tabula's own A13 confirmed crossings (22 F5-R + 27 C0), each tested against its own target UPOs.
- NEG: the same points displaced by 1e-2 (normalised) in a random direction (seed 0).
- Threshold: thr = sqrt(p95(POS) · p5(NEG)). The test is VALID only if p95(POS) < p5(NEG)/10; otherwise every V13
  edge is reported ABSTAIN.
**Classification of each V13 edge:**
- REAL-IN-D: s < thr and every iterate inside D_B9.
- REAL-BAND: s < thr, leaves D_B9 but stays in the base domain.
- REAL-OUT: s < thr, fails the base domain.
- NOT-REPRODUCED: s ≥ thr. To be examined, not a refutation.
**Predictions (stated now):**
- The 9 F5-R and 5 C0 edges that both sides confirm are REAL-IN-D (a second positive control). If any is not, the
  method is suspect and is reported as such.
- For the V13-only edges, predicted mostly REAL-IN-D, i.e. a tabula search-cap miss: A13 caps at 10 hits/pair and
  30+30 iterates.
- V13's densebox found the F5-R SCC margin ≥ 7.2e-4 (above the mask h 5e-4), so REAL-BAND is predicted to be rare.
**Not tested:** transversality (V13's angles are quoted only) and V13 UPOs outside tabula's tier-1 set (their edges
are still tested, against V13's UPO points). One process, 1 core, post-hoc and labelled; registered verdicts are
unchanged.

## A14 RUN 1 = ABSTAIN (validity gate failed), plus FIX ROUND 1 (registered after seeing run 1, before running it)
- Run 1 (results/197_a14_run1_ABSTAIN.json, sha256 96475178…ad0ab as sealed at write, file renamed): p95(POS) 2.05e-3
  vs p5(NEG) 1.89e-2. The gate needs p95 < p5/10 = 1.89e-3, which FAILED by 8%, so every V13 edge is ABSTAIN as
  registered. The threshold was not moved.
- **Diagnosis: CENSORING at NMAX = 15.** 19/51 V13 points, and the worst POS controls, reach their closest approach
  AT the cap, so the approach is cut off before the orbit has settled onto the UPO. This is silent_nulls 18 (check the
  fraction at the cap first), and the pre-registration omitted that check. Information only, not classified: every
  V13 point has s ≤ 1.13e-3 (below p5(NEG)); 5 leave D_B9 before the argmin; 0 fail the base domain.
- **Fix round 1 (the only one):**
  - NMAX 15 → 30, which is A13's own manifold depth: a value fixed by the existing method, not by this data.
  - A censoring guard: if > 25% of POS argmins sit at the cap, ABSTAIN.
  Everything else is unchanged (controls, seed, threshold rule, classes). If run 2 also fails, A14 closes as ABSTAIN.
