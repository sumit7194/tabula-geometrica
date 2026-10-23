# §199 — Separatrix splitting at the TS δ=2 saddle-centre (pre-registration, 2026-10-23)

Requested by The Bridge (user-approved), building on §198. Attended run, ≤ 4 cores, ~4 h. Written and committed
before the code exists.

## Question
§198 saw no chaotic layer at Δx ≈ 3e-3. Non-integrability implies transversal homoclinic intersections
somewhere. How large is the splitting of the stable and unstable manifolds at the equatorial saddle-centre, and
hence how thin is the layer there?

## Correction to the brief and to §198's rationale (found before designing)
At §198's S1/S2 levels (L = −l_sep·(1+0.003 / 0.01)) the shell H = −1/2 lies BELOW the barrier top (V_b −0.482 …
−0.495, measured 2026-10-23). The pocket is closed, so there is NO Lyapunov orbit and no saddle separatrix on that
energy surface. §198's prereg called those levels "hugging the unstable circular orbit's separatrix, where a layer
is generically widest". That was WRONG: there they probe long-period near-saddle tori, not a separatrix. **§198's
verdict is unaffected; its rationale for S1/S2 is withdrawn.** The Lyapunov orbit exists only for ε < 0 (shell above
the saddle, open pocket, V_b < −1/2). So §199 runs at **ε ∈ {−0.003, −0.01, −0.03}** (L = −l_sep·(1+ε), prograde,
E = 0.94). These are §196's open-level family. h = −1/2 − V_b > 0 is the energy above the saddle.

## Objects
TS δ=2 at p = 4/5 (t1o3) and 3/5 (t1o2); control Kerr at the same mass and spin, at the same ε relative to ITS OWN
l_sep. One code path (194/196 model classes).

## Method
- **Integration:** scipy DOP853 on `mdl.rhs`, rtol = atol = 1e-13 (variant 1e-12 for the stability check). The
  section is y = 0 crossed upward (p_y > 0), event-located; section coordinates are (x, p_x), canonical on the
  section.
- **Lyapunov orbit:** the hyperbolic fixed point z* of the section map P near (x_b, 0), found by Newton with a
  finite-difference DP. It must be hyperbolic (|tr DP| > 2) and closed to |P(z*) − z*| < 1e-10.
- **Reversor gate (R0, BEFORE any splitting is read):** S(x, p_x) = (x, −p_x) is time reversal composed with the
  equatorial reflection y → −y, so W^s = S(W^u). Check S∘P∘S∘P(z) = z to < 1e-9 on 5 test points per system/level.
  If it fails, the level is UNREADABLE (W^s is then computed independently, or the level is dropped; a fix round).
- **Unstable manifold, pocket branch** (x > x*): seed z* + s·v_u for s in one fundamental domain [s0, λ·s0],
  s0 = 1e-7. Iterate P up to N = 40. Locate the FIRST crossing of the symmetry line p_x = 0 at x > x* (the primary
  symmetric homoclinic point z_h); refine s by bisection to |p_x| < 1e-12.
- **Splitting angle:** θ = the angle between t = (a, b), the W^u tangent at z_h, and S·t = (a, −b), in (x, p_x).
  θ = 2·atan(|a|/|b|), with b the p_x component of the tangent (an integrable separatrix crosses p_x = 0 vertically,
  so θ = 0). The tangent comes from central differences in s at relative step δ ∈ {1e-4, 1e-5}. Coordinate
  dependence is noted: the angle is in canonical section coordinates and is reported in those units.
- **Kerr floor:** in an integrable system W^u = W^s and θ = 0 exactly. Kerr's θ, together with the spread of TS
  θ across (δ, rtol) variants, is the floor F = max(θ_Kerr, |Δθ_TS| across variants).
- **Registered floor estimate (before running):** with rtol 1e-13 and the section map amplifying errors by λ per
  return over n returns, the position error at z_h is ~ 1e-13·λ^n relative. I expect θ_floor ~ 1e-8 … 1e-6.

## Verdict (per p, per ε)
- **"transversal splitting measured, θ ± err ≫ Kerr floor"** iff R0 passes, θ_TS > 10·F, and θ_TS varies by < 20%
  across the (δ, rtol) variants. err = the variant spread.
- otherwise **"splitting below floor F at this precision"**. Never "integrable".
- **Descriptive:**
  - θ against h for the 3 ε, with log θ fitted both against 1/√h (exponentially small, the saddle-centre
    expectation; Lerman 1991 / Gelfreich–Lerman) and against log h (power law). With 3 points this is suggestive
    only.
  - An order-of-magnitude layer width, reported as the p_x gap between W^u and W^s one step off z_h, compared with
    §198's/§196's resolutions. The comparison is LOOSE: §198 never sampled these open levels.

## Prediction (stated now)
TS2 splitting measurable (≫ Kerr floor) at ε = −0.03, smaller at −0.003, decreasing with h. Kerr at the floor.
Confidence moderate. If TS2 is at the floor everywhere, that is "below floor F", the expected look of an
exponentially small splitting at double precision.

## Amendment 1 (2026-10-23, The Bridge's review, before any code ran)
- **A fourth level ε = −0.1** joins the set, so ε ∈ {−0.003, −0.01, −0.03, −0.1}. If the splitting is exponentially
  small in √h, the near-saddle levels may all sit below the floor; −0.1 is the level most likely to be resolvable,
  so the trend gets at least one or two measured points. If its Lyapunov orbit is not hyperbolic or not found, the
  level is reported as such.
- **Pre-stated high-precision follow-up** (NOT run now) for any level that comes out "below floor F": re-run that one
  level with arbitrary-precision integration (mpmath odefun, or a Taylor integrator in ≥ 30 digits), same
  method, same verdict rule, with F re-estimated from Kerr at the same precision. "Below floor" can then be tightened
  without a new design.
- **Two implementation details fixed now:** a section return is found in two event-located phases (first the
  downward y = 0 crossing, then the upward one), so the start point can never register as a crossing. Seeds that
  plunge (event not reached by t = 5000) are marked missing, never dropped silently.

## Run 1 KILLED by the watchdog + implementation fix (2026-10-23)
- Run 1 reached the 4,000 MB cap after only 2 jobs (Kerr p = 4/5, ε = −0.003; the only results seen, both Kerr).
  Cause: the plunge cut at x = 1.0005 lay inside TS2's near-singular region. Plunging seeds ground there at tiny
  steps toward the 5,000 τ cap, and solve_ivp stored every step.
- Fix (implementation only, no rule changes): the plunge cut is now §196/§198's `r_cut_for` (halfway between the
  horizon and the barrier); steps are not stored (`t_eval=[]`, events only). A TS2 near-saddle level now takes 47 s.
  Run 1's results are discarded; run 2 starts clean.

## Fix round 1 (the only one) + RESULT (2026-10-23)
- **Fix round 1:** TS2 at ε = −0.03 returned NO-FIXED-POINT at both p. Its Lyapunov orbit lies outside the ±0.6
  shooting window around the barrier (Kerr found its own). The window was widened to ±2.0 and only those 4 jobs were
  re-run. The search range cannot change a computed angle. Run 2 otherwise clean: peak 2.1 GB; all R0 ≤ 4e-11;
  closures ≤ 5e-12.
- **ε = −0.1 does not exist** at either p, in TS2 or Kerr: at L = 0.9·l_sep the barrier is gone (no saddle on the
  shell). Amendment 1's added level is reported as absent.

| p | ε | h | θ_TS | spread | Kerr θ | verdict |
|---|---|---|---|---|---|---|
| 3/5 | −0.003 | 5.0e-3 | 7.87e-4 | 2.9e-5 | 2.6e-6 | **transversal splitting measured** |
| 3/5 | −0.01 | 1.6e-2 | 2.50e-3 | 3.4e-5 | 1.7e-6 | **transversal splitting measured** |
| 3/5 | −0.03 | 4.5e-2 | 6.85e-3 | 7.2e-4 | 2.2e-6 | below floor F = 7.2e-4 (θ = 9.5 F; 10 F needed; spread 10.5%) |
| 4/5 | −0.003 | 3.0e-3 | 5.5e-5 | 7.7e-5 | 4.2e-6 | below floor F = 7.7e-5 |
| 4/5 | −0.01 | 9.7e-3 | 4.7e-5 | 1.1e-4 | 4.0e-6 | below floor F = 1.1e-4 |
| 4/5 | −0.03 | 2.6e-2 | 2.0e-4 | 5.8e-5 | 2.7e-6 | below floor F = 5.8e-5 |

- **Headline:** at p = 3/5 the stable and unstable manifolds of the saddle's Lyapunov orbit cross TRANSVERSALLY,
  with an angle 300–1,000× Kerr's numerical floor, stable across step sizes and tolerances. This is a direct
  numerical certificate of a homoclinic tangle, the mechanism of chaos, in TS δ=2.
- **p = 4/5:** TS values are consistently 20–50× above Kerr, but unstable across variants, so they are below floor.
  The pre-stated high-precision follow-up applies.
- **Descriptive (3 points at p = 3/5, the third below floor by the rule):** θ ∝ h^0.98 and h^0.99 between
  consecutive pairs, a linear growth. The exp(−c/√h) form gives inconsistent constants (−0.18, −0.32). The splitting
  is NOT exponentially small here. Caveat: θ is an angle in the section's canonical coordinates, not an invariant.
  The lobe area (invariant) was not computed.
- **Layer width vs §198 (loose, as registered):** an O(1e-3) splitting is far from "invisible". So the tangle is
  real and not tiny at these OPEN levels, but those orbits can leave through the bottleneck (transient chaos).
  §198's closed levels contain no saddle separatrix (see the correction above). The two results are therefore
  compatible: near the saddle the chaos lives on the open side, as a transient.
- **Open thread:** §196 saw 0/360 MEGNO-chaotic at open levels ε = −0.01…−0.05 at T = 3e4. With θ ~ 1e-3 the
  tangle's orbits are presumably a thin, short-lived subset (most seeds miss it, or plunge before MEGNO grows).
  Untested; a seed-on-the-manifold MEGNO check would settle it.
