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
