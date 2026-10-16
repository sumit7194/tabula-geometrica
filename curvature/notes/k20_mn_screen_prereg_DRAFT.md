# §197 K20 — tabula's independent screen of Manko–Novikov's chaotic sea at p1, p2 (pre-registration DRAFT)

*Draft 1, 2026-10-16. Nothing has been integrated. No orbit of MN at p1/p2 has been run, and no CZV or level
geometry at p1/p2 has been computed. The Bridge's V13 numbers have not been seen and will not be seen until both
screens are sealed (commit hashes exchanged). The project is quantum's computer-assisted horseshoe proof; K20 is
step 3: locate the chaotic sea and give candidate regions and return times. The Bridge runs V13 and tabula is the
independent screen.*

## 0. Targets and the code base
- **Metric:** the Gair–Li–Mandel subclass of MN (arXiv:0708.0628, Eqs. 2-7), as already transcribed independently
  in tabula script 144:
  - validated there: V0 asymptotic flatness, and V1 the Kerr limit EMITS Carter;
  - γ′ uses a single −2β, the asymptotically flat form adopted by LGAC 2010 (Eq. 5h);
  - parameters α = (−1+√(1−χ²))/χ, k = √(M²−a²), β = qM³/k³.
- **The two certified points (V9 rows), converted to (χ, q) and set to M = 1, since the problem is scale-free:**
  - **p1:** (M, a, β) = (5, 3, 1/5), so **χ = 0.6, q = +0.1024** (oblate).
  - **p2:** (13, 5, −1/3), so **χ = 5/13 = 0.38462, q = −0.26217** (prolate; prolate MN is not studied in any of the three
    papers).
  - Results are reported in M = 1 units; to convert to the V9 normalisation, multiply times and lengths by M.
- **Dynamics:** geodesics with H = ½ g^{μν}p_μp_ν = −½ (proper time τ), and E, Lz fixed, in prolate-spheroidal
  (x, y). Sections and maps are reported in Weyl–Papapetrou (ρ, z) = (k√((x²−1)(1−y²)), kxy) to match the
  literature.
- **Integrator:** fixed-step RK4 in float64, with dt from the pilot (§3). The tangent map is EXACT, by forward-mode AD
  (torch.func.jvp of the Hamiltonian vector field), not finite-difference twins.

## 1. What the literature says (full-text read; numbers in notes/k20_literature.md)
- LGAC 2010, CLA 2011 and CHL 2012 all study χ = 0.9, q = +0.95 (oblate, strong); E around 0.95, Lz around 3. Sections
  are (ρ, ρ̇) at z = 0 with ż > 0.
- At that point the allowed set has an outer bound region (ρ ≈ 2.4–13.6) that is mostly KAM, plus an inner bound
  region (ρ ≈ 0.72–2.1) where "most orbits are chaotic" (about 20% of the section area at Lz = 3, rising above 80% at
  Lz ≤ 1.6).
  - The chaos is tied to a deep hole in V_eff near the inner edge, close to the CTC edge, and to the instability of
    the inner z = 0 orbit.
  - Above the joining threshold (a saddle, then a neck) there is heteroclinic chaos between the two regions.
  - Stickiness appears near the main islands.
- Island width falls to near zero for q ≲ 0.4 at χ = 0.9 (LGAC Fig. 6). **No paper reports MN chaos at q ≈ 0.1, or
  at any q < 0.**
- The only chaos indicators used there are rotation numbers and section morphology. No Lyapunov exponents are
  published for MN, so the literature gives no threshold to borrow.

## 2. Level selection (mechanical, from metric geometry only, before any orbit is integrated)
For each point and for the matched Kerr (q = 0, same χ):
1. On the grid E ∈ [0.90, 0.995] in steps of 0.005 and Lz ∈ [1.0, 4.5] in steps of 0.05, compute the CZV,
   V_eff ≤ 0 (LGAC Eq. 14), on a (ρ, z) grid. Label each connected allowed component as **PLUNGE** (touches
   ρ = 0, |z| ≤ k, or the line singularity), **ESCAPE** (unbounded), or **BOUND**.
2. Classify each (E, Lz) level by its BOUND topology:
   - **T1**: a single bound region;
   - **T2**: two disjoint bound regions (an MN-type inner and outer);
   - **T3**: two regions joined through a neck, i.e. a saddle of V_eff in z = 0 exists inside the bound set.
3. Screened levels per point (fixed rule):
   - (a) every T2 level within 3 grid steps in E of a T2→T3 transition;
   - (b) the first 3 T3 levels past each transition;
   - (c) the T1 level, if any, whose bound region lies closest in E to the plunge-merger threshold (the analogue of
     the Kerr separatrix);
   - (d) a T1 or T2 "deep" level at the grid's median E among bound levels.
   Capped at 12 levels per point, taken in this order.
4. **If p1 or p2 has no T2 or T3 level on the grid, that is reported as a result** ("no MN-type inner region at
   this point on this grid"), and the screen proceeds on the (c) and (d) levels.

## 3. Accuracy (the §196 lesson, carried over)
- **Pilot:** 12 orbits spread evenly over each level's section. Drift is measured over each orbit's life up to its
  reading time, and dt halves from 0.05 while the max drift exceeds 1e-10. If the pilot measures nothing, it
  REFUSES. Reaching the 1e-3 floor is reported as floor_hit.
- **Pilot self-test (must pass before any screen run):**
  - an injected 5e-9 orbit FAILS;
  - all-NaN REFUSES;
  - partial NaN plus an excess FAILS;
  - REAL: a coarse dt on a strong-deformation level FAILS end to end.
- **Per-orbit acceptance:** |dH/H| ≤ 1e-9 up to the reading time, and |ΔE|, |ΔLz| implied by the shell are checked.
  n_in vs n_analysed is reported per cell, with the excluded orbits broken down by fate and would-be verdict
  (unscored). A cell with more than 25% excluded is UNREADABLE.

## 4. The indicator (independent; not MEGNO; two arms, AND rule)
- **I1, variational: a two-window FTLE ratio.**
  - λ(T) = (1/T)·ln(‖w(T)‖/‖w(0)‖), with the exact tangent vector renormalised periodically.
  - The reading is at N_ret section returns, T₁ = time at N_ret/4 returns and T₂ at N_ret returns. The statistic
    is the pair (λ(T₂), ρλ = λ(T₂)/λ(T₁)).
  - Regular orbits have λ ∝ ln T/T, so ρλ ≈ (ln T₂/ln T₁)·(T₁/T₂) ≪ 1. Chaotic orbits plateau, ρλ → 1. A transit
    near a hyperbolic orbit inflates λ(T₁) but not the plateau. That is the mechanism that fooled MEGNO, and ρλ
    is designed against it.
- **I2, non-variational: the dimension of the section cloud.**
  - Take the N_ret section points (ρ, ρ̇), normalised by the section's extent, and compute a Grassberger–Procaccia
    correlation-dimension estimate D₂ over a fixed scaling range.
  - A regular orbit's points lie on an invariant curve (D₂ ≈ 1); a chaotic orbit fills area (D₂ → 2).
  - It uses no tangent dynamics, so it is blind to transient stretching.
- **Verdicts:**
  - CHAOTIC iff I1 AND I2 both exceed their matched-null p99 thresholds (§5);
  - REGULAR iff both are below their p95;
  - otherwise INDETERMINATE;
  - an orbit that plunges or escapes before N_ret returns is ESCAPE (life and return count reported, and those
    with ≥ 50 returns also verdicted at their own count).
  - N_ret = 2000 primary and 500 secondary.

## 5. The matched integrable null (the Bridge's requirement)
- Kerr at the same χ, using the same code path (q = 0), the same section, the same N_ret, and the same dt rule.
- **Matched in time scale:** the thresholds are calibrated at the same return count and the same proper-time window.
- **Matched in proximity to unstable orbits:**
  - For every screened MN orbit, d_min = the minimum distance (in normalised section coordinates) between its
    section points and the nearest located unstable fixed point or low-period orbit (§6).
  - The Kerr null is built from levels just below Kerr's own unstable spherical-orbit barrier, where bound orbits
    whirl past the hyperbolic fixed point, plus generic tori. It is sampled to cover the MN d_min distribution, bin
    by bin (4 log bins).
  - Thresholds are per d_min bin, taking the class-wise maximum over bins wherever a bin is thin.
- **Null validity gate:** if the Kerr null's own CHAOTIC rate under the frozen thresholds (measured on held-out
  Kerr orbits) exceeds the 95% upper limit for 1%, the screen reports "cannot discriminate" for that d_min bin. No
  verdicts are issued there.

## 6. Structure: periodic orbits, candidate regions, return times, splitting angle
- **Fixed points:** Newton on the section map, from a seed grid, finding period 1-3 orbits with the monodromy
  eigenvalues; listed with stability.
- **Candidate regions:** connected components of the CHAOTIC section cloud, by single-linkage at a fixed scale. Each
  is reported with its bounding box in (ρ, ρ̇), area fraction (with a Clopper–Pearson interval), host level, and
  the UPOs inside it.
- **Return times:** for each candidate region, the distribution of section-to-section return times in τ and in
  coordinate t (median, p5, p95, max), plus the recurrence time to the region itself.
- **Splitting angle, at the best candidate UPO per point (ideally a period-1 hyperbolic fixed point inside a
  candidate region):**
  - Grow W^u and W^s from a fundamental segment at ε = 1e-6 and 1e-7.
  - Find the primary homoclinic point. The system is reversible, so look on the symmetry line ρ̇ = 0 if it falls
    there; otherwise use the first transversal intersection.
  - Report the angle between the manifolds and its change between the two ε values as the error estimate.
  - If no transversal intersection is found within 30 iterations, say so.

## 7. Exterior check (the sea must lie outside the source)
Along every orbit, record min (x − 1), min g_φφ (the CTC region is g_φφ < 0), the fraction of time spent in the
ergoregion, and min V_eff.
- **Tier E-strict:** g_φφ > 0 throughout, and the orbit never enters x < 1 + 0.05.
- **Tier E-weak:** g_φφ > 0 throughout.
- Each candidate region is tagged with the tier its orbits satisfy. Any region whose orbits touch the CTC region
  is reported but marked NOT EXTERIOR.

## 8. Controls (each must pass before the p1/p2 screen is read)
- **C0, positive control from the literature:** χ = 0.9, q = 0.95, E = 0.95, Lz = 3.
  - Inner-region orbits must come out ≥ 50% CHAOTIC (paper: "most").
  - Outer-region orbits must come out ≤ 10% CHAOTIC (paper: mostly KAM).
  - The inner region must lie at ρ ≈ 0.72–2.1, as published (a check on our CZV code).
- **C1, integrable null:** Kerr held-out CHAOTIC ≤ 1% (CP95 upper bound), per d_min bin.
- **C2, the pilot self-test** (§3).
- **C3, the I2 sanity check:** on C0's own published islands, D₂ < 1.3. (The ±1e-3 tolerances against the
  published values are checks, not tuning.)

## 9. Predictions (written first)
- **p1** (q = +0.10, weak oblate): no T2 or T3 level; MN-type inner region absent or tiny. CHAOTIC fraction ≤ 5% on
  every screened level, with chaos, if any, only in thin layers near the plunge-adjacent hyperbolic orbit. The
  candidate region for a horseshoe is thin; the splitting angle is small (≤ 1e-2 rad).
- **p2** (q = −0.26, prolate): no basis in the literature. I predict a T1 topology and CHAOTIC ≤ 10%, held with low
  confidence.
- **C0** passes. If it fails, the screen is unfit, and nothing about p1/p2 is reported beyond "instrument failed
  its positive control".

## 10. Output and sealing
- Per point and level: topology, n_in/n_analysed, the CHAOTIC/REGULAR/INDETERMINATE/ESCAPE counts with CIs,
  candidate regions (boxes, area, UPOs, exterior tier), return-time distributions, and splitting angle(s).
- Sealed as a commit with the result JSON's sha256 before anything is exchanged with V13.
- **Comparison protocol: to be agreed with the Bridge.** Proposed:
  - overlap of candidate regions on the shared section;
  - agreement of chaotic fractions within CIs;
  - return-time medians within a factor of 2;
  - splitting angles within the stated error.
  Disagreements are reported, not resolved by tuning.

## 11. Budget
≤ 4 cores, BLAS threads = 1. The cost estimate comes from a timing-only benchmark of the Hamiltonian vector field,
which reads no orbit outcome and is done after this draft is agreed.

## Open questions for the Bridge
1. "Exterior": are the E-strict and E-weak tiers what you mean, or is the "source" defined differently in V13 (e.g.
   a Weyl radius around the line singularity)?
2. Is N_ret = 2000 enough for the proof's needs, or does quantum need specific return-map orders?
3. Is it OK that level selection is rule-based on my side, independent of V13's choice of (E, Lz)? Or should we
   agree a shared level list, with only the indicator independent? I would propose the former for independence,
   plus one SHARED level per point for the direct comparison.
