# §197 K20 — tabula's independent screen of Manko–Novikov's chaotic sea (PRE-REGISTRATION, final)

*Final, 2026-10-16. Draft 1 was 7db2304; The Bridge's review is folded in (changes listed at the end).*

*Status at commit time:*
- Nothing has been integrated: no MN or Kerr orbit at any point.
- No CZV, level or CTC geometry has been computed at p1, p2 or P0.
- The Bridge's V13 numbers have not been seen and will not be seen until both screens are sealed.

*Context: the project is quantum's computer-assisted horseshoe proof (PREREG_chaos_horseshoe_phase2.md), and K20
is its step 3: locate the chaotic sea and give candidate regions and return times. The Bridge runs V13; tabula is
the independent screen: its own code, its own indicator, and its own level rule plus agreed shared levels.*

## 0. Targets and the code base
- **Metric:** the Gair–Li–Mandel subclass of MN (arXiv:0708.0628), as independently transcribed in tabula script
  144. Validated there by V0 (asymptotic flatness) and V1 (Kerr limit EMITS Carter). γ′ uses a single −2β.
  Parameters: α = (−1+√(1−χ²))/χ, k = √(M²−a²), β = qM³/k³. The same α, k and β as the Bridge's V9 code.
- **Points, set to M = 1 (the problem is scale-free; to convert to the V9 normalisation, multiply times and lengths
  by M):**
  - **p1:** (M, a, β) = (5, 3, 1/5), so χ = 0.6, q = +0.1024 (oblate).
  - **p2:** (13, 5, −1/3), so χ = 5/13, q = −0.26217 (prolate; not studied in the literature).
  - **P0, the published point:** χ = 0.9, q = 0.95 (LGAC 2010, CLA 2011, CHL 2012). P0 serves two roles, kept
    apart (§8):
    - **C0:** the instrument gate, at the single level E = 0.95, Lz = 3.
    - A **FULL screen**, on its own level set that EXCLUDES the C0 level. If p1 and p2 come out thin, P0 is the
      horseshoe fallback (quantum's F5).
- **Dynamics:**
  - Geodesics with H = ½g^{μν}p_μp_ν = −½, proper time τ; p_t = −E and p_φ = Lz fixed.
  - The reduced 2-DOF system in prolate-spheroidal (x, y, p_x, p_y), as in quantum §3.2.
  - E and Lz are rational, because they lie on the grid.
- **Section (shared with quantum §3.3):** Σ = {y = 0, p_y > 0}, with coordinates (x, p_x). Weyl (ρ, ρ̇) is also
  reported for comparison with the literature.
- **Integrator:** fixed-step RK4 in float64, with dt from the pilot (§3).
  - The tangent map is EXACT: forward-mode AD of the Hamiltonian vector field (torch.func), not finite-difference
    twins.
  - Section crossings are located by Hénon's trick (one step in y as the independent variable), so the crossing
    lands exactly on y = 0.

## 1. Literature (full text; notes/k20_literature.md)
- All published MN chaos is at χ = 0.9, q = +0.95 (E ≈ 0.95, Lz ≈ 3), and lies in the inner bound region
  (ρ ≈ 0.72–2.1).
  - It is tied to a deep V_eff hole near the CTC edge, and to the unstable inner z = 0 orbit.
  - Above the join there is heteroclinic chaos.
- Island width is about 0 for q ≲ 0.4 at χ = 0.9.
- No published MN chaos at q ≈ 0.1, or at any q < 0.
- No Lyapunov thresholds are published: the papers use rotation numbers only.

## 2. Levels
- **Own levels (a mechanical rule from metric geometry only, before any orbit), per point and for the matched
  Kerr (q = 0, same χ):**
  1. On the grid E ∈ [0.90, 0.995] (step 0.005) × Lz ∈ [1.0, 4.5] (step 0.05), compute the allowed set V_eff ≤ 0
     (LGAC Eq. 14, evaluated in (x, y)) intersected with D (§7).
  2. Label each connected component:
     - **PLUNGE**: it reaches the boundary of D (orbits leaving D are treated as plunging, per quantum §3.4);
     - **ESCAPE**: unbounded;
     - **BOUND**: otherwise.
  3. Classify each level by its BOUND topology:
     - **T1:** one bound region;
     - **T2:** two disjoint regions, MN-type inner and outer;
     - **T3:** two regions joined through a neck (a saddle of V_eff in y = 0 inside the bound set).
  4. Screened levels, in order and capped at 12 per point:
     - (a) T2 levels within 3 E-steps of a T2→T3 transition;
     - (b) the first 3 T3 levels past each transition;
     - (c) the T1 level nearest in E to the plunge-merger threshold;
     - (d) one level at the median E among bound levels.
  5. For P0's full screen, the C0 level (0.95, 3) is excluded from its own list.
  6. **No T2 or T3 level at p1 or p2 is reported as a result**, and the screen then runs the (c) and (d) levels.
- **Shared levels (named by the Bridge in V13, by its mechanical rule, before any output from either side):**
  - one level per point;
  - plus the C0 level.
  - These are screened exactly like the own levels, and are the basis of the direct comparison (§10).

## 3. Accuracy (§196 machinery)
- **Pilot:** 12 orbits spread evenly over the level's section. Drift is measured over each orbit's life up to its
  reading time, and dt halves from 0.05 while the max drift exceeds 1e-10.
  - An empty measurement REFUSES, and is never read as 0.
  - Reaching the 1e-3 floor is reported as floor_hit.
- **Pilot self-test (must pass before any screen run):**
  - an injected 5e-9 orbit FAILS;
  - all-NaN REFUSES;
  - partial NaN plus an excess FAILS;
  - REAL: dt = 0.05 on P0's inner region FAILS end to end, or, if it happens to pass, the test is replaced by a dt
    shown to fail on that level. Either way the real case must exercise the FAIL path.
- **Per-orbit acceptance:** |dH/H| ≤ 1e-9 up to the reading time (N_ret returns, or the orbit's end).
  - n_in vs n_analysed per cell, with the excluded orbits broken down by fate and would-be verdict (UNSCORED).
  - A cell with more than 25% excluded is UNREADABLE.

## 4. Indicator (independent; not MEGNO; two arms, AND rule)
- **I1, variational: a two-window FTLE ratio.**
  - λ(T) = T⁻¹ ln(‖w(T)‖/‖w(0)‖), on the exact tangent, renormalised every 100 steps (log accumulated).
  - T₁ = the time at N_ret/4 returns and T₂ = the time at N_ret returns.
  - Statistics: λ₂ = λ(T₂) and ρλ = λ(T₂)/λ(T₁). Regular orbits give ρλ well below 1 (ln T/T decay); chaotic orbits
    give ρλ → 1, a plateau.
  - **I1 high** iff λ₂ > the null p99 for λ₂ AND ρλ > the null p99 for ρλ.
  - **I1 low** iff both are below their null p95.
  - Otherwise I1 is mixed.
- **I2, non-variational: the correlation dimension of the section cloud.**
  - Take the N_ret section points (x, p_x), each axis normalised by the level's section bounding box (§10).
  - Grassberger–Procaccia C(r) over all pairs. D₂ is the least-squares slope of log C vs log r over **two fixed
    scaling windows: W_A r ∈ [0.01, 0.05] and W_B r ∈ [0.02, 0.10]**.
  - **I2 high** iff D₂ exceeds the null p99 in BOTH windows; **I2 low** iff it is below the null p95 in both;
    otherwise I2 is mixed.
  - A window holding fewer than 200 pairs is mixed, never zero.
- **Verdicts:**
  - CHAOTIC iff I1 high AND I2 high;
  - REGULAR iff I1 low AND I2 low;
  - otherwise INDETERMINATE;
  - **ESCAPE** if the orbit leaves D, plunges or escapes before N_ret. Its life and return count are reported, and
    one with ≥ 500 returns is also verdicted at the secondary count.
  - N_ret = 2000 primary, 500 secondary.

## 5. Matched integrable null (Kerr, same χ, q = 0, the same code path)
- **Matched in time scale:** thresholds are calibrated at the same N_ret and on the same section.
- **Matched in proximity:**
  - For every screened orbit, d_min = the minimum distance (in normalised section coordinates) between its section
    points and the nearest located UPO of period ≤ 3 (§6).
  - The Kerr null comes from levels just below Kerr's unstable spherical-orbit barrier (whirling orbits that pass
    the hyperbolic point) plus generic tori, sampled to cover the screened orbits' d_min distribution in 4 log bins
    (d_min < 1e-3, 1e-3 to 1e-2, 1e-2 to 1e-1, ≥ 1e-1).
  - Thresholds are per bin. Where a bin holds fewer than 60 null orbits, the class-wise maximum over that bin and
    its neighbour is used.
- **Null validity gate (per bin):** on HELD-OUT Kerr orbits (a separate seed set, never used for thresholds), if
  the CHAOTIC rate exceeds the 1% one-sided CP95 bound, that bin reads "cannot discriminate" and issues no verdict.

## 6. Structure
- **Fixed points and UPOs of period ≤ 3:** Newton on the section map from a seed grid, with monodromy matrices,
  eigenvalues and stability.
- **Candidate regions:**
  - Connected components of the CHAOTIC section cloud, by single-linkage at 0.02 in normalised units.
  - Each is reported with its box in (x, p_x) and in (ρ, ρ̇), its area fraction with a CP interval, its host level,
    the UPOs inside it, and its D-status.
- **Return times:** per candidate region, the distribution of section returns in τ and in t (median, p5, p95, max),
  plus the recurrence time to the region itself.
- **Splitting angle at the best candidate UPO per point** (preferring a hyperbolic period-1 point inside a candidate
  region that lies in D):
  - Grow W^u and W^s from a fundamental segment at ε = 1e-6 and at 1e-7.
  - Find the primary homoclinic point: on the p_x = 0 line if reversibility puts it there, otherwise at the first
    transversal intersection.
  - Report the angle, and its change between the two ε as the stated error.
  - No transversal intersection within 30 iterations is reported as such.

## 7. Exterior: quantum's physical domain D decides (quantum §3.4)
- **D is:**
  - x − 1 ≥ δ_x;
  - g_φφ > 0;
  - R² = x² + y² − 1 ≥ 0.25;
  - 1 − y² > 0;
  - every metric function finite, with B > 0;
  - det g < 0.
  - The ergoregion is allowed.
- **Margins:** δ_x = 0.10 at p1 and 0.15 at p2, as quantum gives them.
- **P0's margin, by the SAME rule derived from those two:** measure the CTC region's largest x on the grid,
  x_CTC = max{x : g_φφ < 0 for some y}, then δ_x = ⌈x_CTC − 1 + 0.02⌉ to a multiple of 0.05.
  - This reproduces quantum's values: 1.075 gives 0.10, and 1.122 gives 0.15.
  - Also check that the singular neighbourhood stays inside R² < 0.25. If it does not, report it and use
    R² ≥ (R_sing + 0.03)².
  - The derivation is committed BEFORE any P0 orbit.
- Every point of every orbit is checked against D in float64, on samples every integration step (not interval
  arithmetic; that is quantum's job). Any orbit that leaves D is ESCAPE.
- Also reported, as extra information only: min(x−1), min g_φφ, min R², the time in the ergoregion, and min V_eff,
  plus the earlier E-strict (x ≥ 1.05 and g_φφ > 0) and E-weak tiers.

## 8. Controls (each must pass before p1, p2 or the full P0 screen is read)
- **C0, the instrument gate at P0's level (E 0.95, Lz 3), exactly as in draft 1, graded only on its own orbits:**
  - inner-region orbits ≥ 50% CHAOTIC;
  - outer-region orbits ≤ 10% CHAOTIC;
  - the inner bound region at ρ ≈ 0.72–2.1, a check on our CZV code (tolerance ±0.05).
- **C1, integrable null:** held-out Kerr CHAOTIC ≤ 1% (CP95) per d_min bin, at every χ used (0.6, 5/13, 0.9).
- **C2:** the pilot self-test (§3).
- **C3, negative control for the AND rule:** orbits launched on large published islands at the C0 level must be
  NOT CHAOTIC on BOTH arms (I1 not high AND I2 not high).
  - The islands: the outer main island around u₀ (ρ ≈ 8.35, CLA 2011) and the inner period-1 island (ρ ≈ 0.8–1.05,
    LGAC 2010).
  - 10 orbits each, near the island centres located by our own Newton step.
- **C4, I2 sanity:** on C3's island orbits, D₂ < 1.3 in both windows.
- If any control fails, the instrument is unfit. Nothing about p1, p2 or P0-full is reported beyond the failure.

## 9. Predictions (written first)
- **p1** (q = +0.10, weak oblate): no T2 or T3 level. CHAOTIC ≤ 5% on every screened level; any chaos only in thin
  layers near the plunge-adjacent hyperbolic orbit. Splitting angle ≤ 1e-2 rad, or none found.
- **p2** (q = −0.26, prolate): T1, CHAOTIC ≤ 10% (low confidence; no literature).
- **P0 full screen:** chaos concentrated in the inner region and at the neck, with a candidate region inside D on at
  least one level.
- **C0 to C4 pass.**

## 10. Output, sealing, comparison
- **Section bounding box per level** (shared with V13, computed from geometry only): x from the y = 0 CZV extent of
  the screened bound region, and p_x from ±√(max of the shell-allowed p_x²) over that x range. The comparison
  grid is a 200×200 grid on this box.
- **Per point and level:** topology, n_in/n_analysed, the CHAOTIC, REGULAR, INDETERMINATE and ESCAPE counts with
  95% CIs, candidate regions (boxes, area, UPOs, D-status), fixed points and UPOs to period 3 with monodromy,
  return-time distributions, and splitting angles.
- **Sealing:** a commit, plus the sha256 of the result JSON, sent to the Bridge before anything is exchanged.
- **Comparison (thresholds fixed now, The Bridge):**
  - region overlap: Jaccard ≥ 0.5 on the 200×200 grid;
  - chaotic fractions: 95% CIs overlap;
  - return-time medians within a factor of 2;
  - splitting angles within the combined stated errors.
  - Disagreements are reported, never tuned.

## 11. Budget
≤ 4 cores, BLAS threads = 1, and launch by absolute path. The cost estimate comes from a timing-only benchmark of the
vector field and tangent, which reads no orbit outcome.

## Changes from draft 1 (The Bridge's review, 2026-10-16)
1. P0 is screened FULLY on a separate level set; C0 remains the gate, graded only on its own level's orbits.
2. Exterior is quantum's domain D, with margins 0.10 and 0.15 and P0's margin by a stated rule. The ergoregion is
   allowed, and E-strict/E-weak become information only.
3. The section is quantum's {y = 0, p_y > 0} in (x, p_x), with Weyl reported alongside.
4. Fixed points and UPOs are reported to period 3 with monodromy.
5. Shared levels: one per point, named by the Bridge in V13 by rule before any output, plus the C0 level.
6. Comparison thresholds are fixed (Jaccard ≥ 0.5 on 200×200, CI overlap, ×2, combined errors).
7. I2: two fixed scaling windows; a verdict only if both agree.
8. New C3/C4: the AND rule's negative control on published islands.

## AMENDMENT A1 (2026-10-16, before ANY integration or geometry computation; The Bridge, relaying quantum 78e2d63/40ad82b)
Where A1 conflicts with the text above, A1 wins.

**A1.1 The fallback point that counts is F5-R, screened IN FULL; P0 is control only.**
- F5-R: (M, a, q) = (89, 80, 19/20).
  - χ = 80/89 ≈ 0.89888.
  - k = √(89² − 80²) = 39 exactly.
  - α = (−1 + 39/89)/(80/89) = −5/8.
  - β = qM³/k³ = 19·704969/(20·59319) = 13394411/1186380 ≈ 11.290. All are rational, as the Morales–Ramis machinery
    needs.
- F5-R gets everything p1/p2 get: the own level rule (§2), shared levels, the full outputs, and the matched Kerr
  null at χ = 80/89.
- The published point P0 (χ = 0.9, q = 0.95) is now ONLY the instrument control: C0 at (E 0.95, Lz 3), plus C3/C4
  at that level. "P0 full screen" in §0/§2/§9 is replaced by "F5-R full screen". Prediction for F5-R: the same as
  the old P0 prediction, i.e. chaos concentrated in the inner region and at the neck, with a candidate region
  inside D on at least one level.

**A1.2 The q convention is confirmed (text now; numerically as gate G-q before anything counts).**
- Text: β = qM³/k³ appears identically in GLM 2008 Eq. 5, LGAC 2010 Eq. 7 (β = q((1+α²)/(1−α²))³ = q(M/k)³),
  quantum's MN_METRIC.md line 26, and tabula script 144.
- γ: quantum's "−2 inside Σ_{l=0..2}, then +8β" equals tabula's single 2β(Σ − 2) exactly. Same metric.
- The sign of q: GLM q ≡ −(M₂ − M₂^Kerr)/M³ (q > 0 oblate), and LGAC/CLA/CHL use the same.
- **Gate G-q (geometry only, at P0, no orbits).** Our CZV code must reproduce the published thresholds:
  - CLA 2011: the regions join for Lz < 2.99761912 at E = 0.95; the outer region vanishes at Lz ≈ 3.40935; and at
    Lz = 3 the regions are separate for E ≤ 0.95038 and the outer region vanishes at E ≈ 0.93210. Each must hold to
    within 1e-3.
  - GLM's region extents at E 0.95, Lz 3 (inner ρ ≈ 0.72–2.12, outer 2.39–13.6) must hold to within 0.05.
  - A flipped or misscaled β fails these. If G-q fails, nothing counts.

**A1.3 Domain rules: quantum §3.4 exactly (replaces my §7 margin rule).**
- **CTC margin:** δ_x = (x_CTC − 1) + 0.025, rounded UP to a multiple of 0.05, where x_CTC is the outer x-extent of
  the g_φφ < 0 region over |y| < 1. This reproduces 0.10 at p1 and 0.15 at p2. It is derived the same way at F5-R and
  P0, and committed before any orbit there.
- **Singular rule:** R ≥ max(0.5, 2R_s), where R_s is the radius around R → 0 within which any metric function is
  non-finite or has magnitude above 1e12. (This replaces R² ≥ 0.25 unless that is the larger.)
- **Report, with no gate:** ergoregion extent and min |B|.

**A1.4 Additional outputs (quantum's list).**
- **(a)** Exact rational (E, Lz) per level, the section, and transversality: min |ẏ| over all recorded crossings,
  per level and per candidate region.
- **(b) Per UPO:**
  - its period-n points on Σ;
  - the eigenvalues AND eigenvectors of DPⁿ;
  - its minimum D-margins along the full periodic orbit (x−1−δ_x, R − R_min, g_φφ, 1−y²);
  - **in-sea test:** of 20 orbits launched uniformly in a normalised ball of radius 0.01 around the UPO, ≥ 50% are
    CHAOTIC, and their section clouds fall in the same single-linkage component as a candidate region. Otherwise it
    is labelled BOUNDARY-LAYER / ISLAND-CHAIN.
- **(c) Candidate transition graph (the priority output):**
  - For every ordered pair (i, j) of in-sea UPOs (i = j means homoclinic), grow W^u(i) from a fundamental segment
    at ε = 1e-6 for up to 30 forward iterates, and W^s(j) likewise backward.
  - Report the first iterate pair (n_u, n_s) at which they intersect transversally (a sign change of the signed
    distance between the polylines), plus the intersection point, the angle, and the result repeated at ε = 1e-7.
  - Pairs with no intersection within the budget are reported as "none found within 30 + 30", not as "no
    connection".
- **(d) Maximum one-return stretch:** max and median of the largest singular value of DP (one return) over
  section points of sea orbits within normalised radius 0.02 of each UPO.
- **(e) Plunge/escape fraction near each UPO:** of 50 orbits launched uniformly in a ball of radius 0.01 around it,
  the fraction that leaves D, plunges or escapes within N_ret returns, with a CP interval.
- **(f) Fraction of the candidate sea inside D:**
  - f_D = (CHAOTIC orbits of the region that stay in D for N_ret) / (those + the ESCAPE orbits whose pre-escape
    section points fall in the region's 200×200 grid cells).
  - Plus the fraction of the region's grid cells whose sampled orbits never left D.

**A1.5 Order.** The C-gates (C0-C4, G-q, the self-test) and the geometry (levels, margins at all four points) come
first, then the cost benchmark. Nothing beyond the C-gates is screened until the Bridge's shared levels arrive as
(E, Lz) rationals from the committed V13.
