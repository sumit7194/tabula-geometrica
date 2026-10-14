# Third chaos method after §195: measurement plan for an established indicator (DRAFT for The Bridge)

**Status:** a measurement plan only. Nothing here is a design, a threshold or a gate. It answers one question:
*can an established indicator separate regular from chaotic orbits in the cycle-poor near-separatrix regime,
without firing on integrable Kerr?* A design is proposed only after these distributions exist, and it is then
validated on unseen levels.

## Research (2026-10-11)
- **MEGNO** (Cincotta & Simó 2000): ⟨Y⟩ → 2 on quasi-periodic orbits, → 0 on stable periodic orbits, and grows like
  λt/2 for chaos. Its time weighting damps transients.
- **FLI** is analytically related to MEGNO (Mestre, Cincotta & Giordano). It comes from the same tangent
  integration.
- **SALI** (= GALI₂ for 2 DOF; Skokos): from two deviation vectors. It tends to a non-zero constant on tori and decays
  exponentially for chaos. It is often faster than MEGNO in few cycles. Commonly quoted threshold: 1e-8.
- **Known pitfalls:**
  - (a) Variational indicators show SPURIOUS structures when the initial deviation vector aligns with special
    directions (Breiter et al.). Mitigation: random initial vectors, and reporting dependence on them.
  - (b) Sticky orbits are misclassified by EVERY indicator if the run is too short. Practical remedy: classify as a
    function of T and accept only verdicts that are stable in T.
  - (c) No published benchmark on Kerr zoom-whirl orbits was found. The Bridge's V11: a finite-time Lyapunov-type
    statistic (S_ex) FIRED ON INTEGRABLE KERR near the separatrix (hyperbolic passage + shear). So this must be
    measured, not assumed.
- **Structural difference from §195:** these indicators need the FLOW's tangent map, so they cannot be applied to
  surrogate time series. Their false-positive controls are INTEGRABLE DYNAMICS instead: Kerr (Carter),
  Schwarzschild, and ZV δ=1 (Schwarzschild in Weyl form). The surrogate nulls are not used.

## Implementation (to be validated before use)
- One integration carries the orbit plus 2 deviation vectors with random unit initial directions (pitfall a).
  Tangent dynamics come from a central directional difference of the reduced RHS, J·w ≈ [f(z+εw) − f(z−εw)]/2ε,
  ε = 1e-7·|z|.
  - **Validation:** on Hénon–Heiles, compare with the exact analytic Jacobian (agreement of ⟨Y⟩ and SALI over T).
- Renormalise each deviation vector every step (SALI uses the normalised pair).
- ⟨Y⟩ is accumulated per Cincotta–Simó, and FLI = max log|w|. The 0-1 test is report-only, from x(t).
- Per-system dt by the drift target (Kerr 0.05, HH 0.0025, ZV measured), sampling every 0.5 τ for checkpoints.

## Controls (fresh seeds; none reused later as validation)
| group | role |
|---|---|
| Kerr real, near-separatrix level (pro, ε = −0.01, E 0.97), 40 orbits | false-positive control in the hard regime (zoom-whirl) |
| Kerr real, a generic (far-from-separatrix) level, 20 orbits | does Kerr settle to ⟨Y⟩ = 2 there? |
| Schwarzschild / ZV δ=1, 20 orbits | integrable static control |
| HH E = 1/12 regular-truth, E = 0.1657 chaotic-truth (FTLE + section-gap labels) | separation where truth is known |
| ZV δ=2: the V11 regular orbit, deep x0 ∈ [7.8, 9.5], the two V11 layer orbits | the target-like regime |

## Readouts (distributions, not verdicts)
- ⟨Y⟩(t), SALI(t), FLI(t) at log-spaced checkpoints up to T = 3e4, and to 1.5e5 for Kerr and ZV.
- For integrable Kerr: the SETTLING time (first t after which |⟨Y⟩ − 2| < 0.1 stays true), its relation to cycles
  completed, and to periapsis proximity to the unstable circular orbit (the zoom-whirl transient). Also the minimum
  SALI over the run and when it occurs.
- Per group and checkpoint: the separation between the integrable and chaotic-truth distributions (min/median/max,
  overlap counts), and dependence on the initial deviation vector (two random draws per orbit).
- Cost and memory, to size any later design.

## What would make the indicator usable (to be proposed AFTER measurement, not frozen here)
Integrable Kerr settles (⟨Y⟩ → 2, SALI bounded away from 0) within a feasible T at the near-separatrix levels, AND
chaotic-truth orbits separate from it by a pre-agreed margin at that T. If Kerr does not settle in feasible T, that
is reported as the indicator's limit in this regime, just as §195's was.

## MEASUREMENT 1 RESULTS (2026-10-12 03:44; results/196_measure/*.json; code 89ae240)
Environment: py314_openblas, BLAS threads 1. Barrier separatrix (Kerr gated vs BPT), per-level cut, per-system dt
(drift pilot <= 1e-10: Kerr 0.05, p 3/5 pro and the long job 0.025, ZV 0.0125, HH 0.0016).

**Integrable controls** (max ⟨Y⟩ over survivors, both vector pairs):
| group | t <= 1e3 | t >= 3e3 (all later checkpoints) | min SALI (at T) |
|---|---|---|---|
| Kerr p4/5 pro near-sep (39/40 survive) | up to 2.33 (transient) | <= 1.97 | 4e-4 |
| Kerr p4/5 retro near-sep (19/20) | <= 1.93 | <= 1.90 | 3e-4 |
| Kerr p3/5 pro near-sep (19/20) | <= 2.09 | <= 2.03 | 1e-4 |
| Kerr generic (20/20) | <= 1.94 | <= 2.02 | 8e-4 |
| Kerr p4/5 pro near-sep LONG to 1.5e5 (20/20) | up to 2.19 | <= 2.08 (at 1.5e5) | 2e-4 |
| Schwarzschild near-sep (19/20) | up to 2.14 | <= 1.95 | 3e-5 |
- **No false alarms after settling.** From t = 3e3 on, every integrable orbit stays at ⟨Y⟩ <= 2.08. Early
  transients reach 2.33, so any rule must use t >= 3e3. The Bridge's zoom-whirl worry (V11 S_ex) does NOT show
  in time-weighted MEGNO.
- SALI decays slowly on integrable orbits (3e-5 to 8e-4 by T, still decreasing): far above the 1e-8 folklore
  threshold, but not constant. It is a weaker discriminator here.

**Truth-labelled HH:** E = 1/12 tori: ⟨Y⟩ <= 2.36 at 1e4 and <= 2.15 at 3e4 (1/80 over 2.1), with an early transient
up to 4.32 at 1e3. KAM tori in a NON-integrable system wobble above 2, so a 2.1 cut is too tight for them.
E = 0.1657 chaos: ⟨Y⟩ >= 10 by t = 100, >= 504 at 3e4. SALI 0.

**ZV δ=2** (new cut x < 1.5): the V11 regular orbit (x0 7.62) and 7 deep seeds survive with ⟨Y⟩(3e4) 1.64-2.13
(pair A; the 2.13 is x0 8.2, whose pair B gives 1.85). **The two V11 layer orbits PLUNGE before T** (9380, 24404 tau),
with ⟨Y⟩ rising to only 2.8 / 4.4 before plunging.

**Reading:** MEGNO is a clean NO-FALSE-ALARM instrument here (integrable Kerr/Schwarzschild settle by 3e3, ≤ 2.08
to 1.5e5), and strong chaos separates by > 200x. The open question is WEAK, SHORT-LIVED separatrix-layer chaos:
⟨Y⟩ of 2.8-4.4 before plunge against torus wobble up to ~2.4 is a thin margin, from n = 2.
**Next measurement (proposed):** a ZV δ=2 near-separatrix population large enough to matter (several eps levels,
dozens of seeds, FTLE truth against the Schwarzschild reference), recording ⟨Y⟩(t) up to the plunge, and testing
whether a GROWTH statistic (the slope of ⟨Y⟩ ~ λt/2 over the surviving window) separates weak layer chaos from
torus wobble better than a final value does.

## MEASUREMENT 2: analysis plan FIXED BEFORE ANY RESULT (2026-10-12, launched 04:20; scope agreed with The Bridge)
Context: ansatz's high-precision probe found TS's near-separatrix chaos TRANSIENT (a chaotic saddle with escape;
most chaotic window orbits plunge within ~300 crossings). So the target is weak, short-lived chaos.
Anchor: open Henon-Heiles (E 0.18, 0.21, 0.25 > 1/6; chaotic scattering, escape through saddles; Aguirre, Vallejo &
Sanjuán, PRE 64, 066208 (2001), verified). Escape = |q| > 2.

Populations:
- CHAOTIC-TRANSIENT: (i) open-HH orbits that escape after >= 25 tau (direct escapes have no time to develop chaos;
  lifetime is the label, FTLE is reported as a covariate); (ii) ZV δ=2 layer-grid orbits with FTLE > 3x the max
  Schwarzschild-reference FTLE (the pre-registered truth rule); (iii) HH E = 0.125 chaotic-truth orbits.
- REGULAR (null): Kerr p4/5 pro/retro and p3/5 pro at the barrier separatrix (eps -0.01); Schwarzschild; HH E = 1/12
  regular-truth; HH E = 0.125 regular-truth; ZV layer-grid orbits that survive T with FTLE <= 1.5x the Schwarzschild
  median.

Statistics, DURATION-MATCHED (The Bridge): each chaotic orbit has lifetime tau (escape, plunge or T). At duration tau:
- S1 = ⟨Y⟩(tau), the last series point <= tau;
- S2 = OLS slope of ⟨Y⟩(t) over [tau/2, tau] (≈ λ/2 for chaos, → 0 on tori);
- the null at tau is EVERY regular orbit's series truncated at the same tau.

Reported per duration bin (tau in [25, 100), [100, 300), [300, 1e3), [1e3, 3e3), [3e3, 3e4]):
- the ROC AUC of S1 and S2 (chaotic vs duration-matched null);
- the null's 99th percentile vs the chaotic median;
- the fraction of chaotic orbits above the null's 99th percentile ("detection rate at 1% false alarm").
- Covariate: tau x λ_FTLE (Lyapunov times lived). Expected: MEGNO needs several Lyapunov times, so detection should
  track it.
- The DETECTION HORIZON is the shortest bin where the detection rate at 1% false alarm is >= 50%.

No usability rule is drawn from this alone; it is proposed to The Bridge afterwards, with thresholds validated on
unseen levels.

## MEASUREMENT 2 RESULTS (2026-10-12 06:17; results/196_measure2/*.json, results/196_measure2_analysis.json)
**Per the fixed plan** (duration-matched, regular null n = 117: Kerr p4/5 pro/retro + p3/5 pro + Schwarzschild survivors,
HH E=1/12 and E=0.125 regular-truth; chaotic n = 171):

| lifetime bin | n analysed | Lyap. times (median) | S1 = ⟨Y⟩(τ) AUC | S1 detect @1% FA | S2 slope AUC | S2 detect @1% FA |
|---|---|---|---|---|---|---|
| 25-100 | 45 (of 56; see flaw 1) | 12 | 0.9996 | 1.00 | 0.9996 | 0.98 |
| 100-300 | 22 | 30 | 1.000 | 1.00 | 1.000 | 1.00 |
| 300-1e3 | 13 | 73 | 0.987 | 0.85 | 0.846 | 0.85 |
| 1e3-3e3 | 1 | 24 | - | 0/1 | - | 1/1 |
| 3e3-3e4 | 79 | 97 | 0.787 | 0.61 | 0.733 | 0.53 |

Duration-matched null 99th percentile of ⟨Y⟩: 2.02 (25-100), 2.33 (100-300), 2.58 (300-1e3), 2.45 (1e3-3e3), 2.08 (3e3-3e4).

**Post-hoc diagnostics (NOT in the fixed plan; labelled as such):**
- HH E = 0.125 chaotic-truth (37): ⟨Y⟩(T) 255-854, so **100% detected**. The long bin's 61% comes ENTIRELY from ZV.
- **Flaw 1 (mine; silent-drop class):** S1/S2 need >= 3 series points <= τ, and ZV/Kerr series were recorded every 25 τ.
  So 11 ZV layer orbits with lifetimes 57-75 were dropped from the 25-100 bin without a flag (56 in the bin, 45
  analysed). By eye their ⟨Y⟩ is 1.6-4.8, mostly but not all above the null. The 25-100 "100%" is really open HH plus
  the longer ZV transients.
- **Flaw 2 (the truth rule, pre-registered in §195 and inherited here):** "ZV chaotic iff FTLE > 3x the max of the
  Schwarzschild reference" labels ALL 62 ZV grid orbits chaotic, because Schwarzschild's finite-time FTLE (max
  1.2e-4) is 3-10x below that of ZV's own clearly regular orbits (x0 >= 7.60: survive T, ⟨Y⟩ 1.4-2.1, FTLE 4-13e-4).
  Schwarzschild is not a valid FTLE reference for ZV δ=2 near its layer. Consequence: no ZV regular null, and the
  long bin's ZV "chaotic" set is mostly regular orbits.
- ZV structure as MEGNO sees it: x0 <= 7.53 are fast transients (life 57-120, FTLE 0.12-0.18, ⟨Y⟩ 1.6-4.8 at
  25-50 tau resolution). x0 7.54-7.59 is the layer edge (lives 450-30000, several with ⟨Y⟩ 5-13). x0 >= 7.60 is
  regular-looking (⟨Y⟩ ~2).

**Reading:** MEGNO detects short-lived transient chaos (open HH) at ~100% against a duration-matched 1% false-alarm
bar from 25 tau on (12+ Lyapunov times), and bounded chaos (HH 0.125) at 100%, with no false alarms on integrable
Kerr/Schwarzschild. Before any usability rule: (a) the ZV truth rule must be replaced; (b) series resolution must
scale with lifetime (5 tau, as open HH had).

## FROZEN MEGNO RULE + THRESHOLD TABLE (2026-10-12 07:59; results/196_threshold_table.json) — sent to The Bridge before validation
Calibration (scripts/196 --calibrate, results/196_calibrate/): 5-tau ⟨Y⟩ series. Null set (audited; no silent drops):
- integrable survivors: Kerr p4/5 pro 20/20, p4/5 retro 19/20, p3/5 pro 19/20, Schwarzschild 18/20;
- tori: HH E 1/12 60/60, HH E 0.125 26/60. Tori are labelled NON-variationally by the 0-1 test (whole window AND both
  halves < 0.2; "chaos" = all three > 0.8).
**Correction before freezing:** the first table used a 0-1 label on the FIRST 3000 tau only, while MEGNO saw 3e4. A
sticky-then-chaotic HH orbit (FTLE 0.04, ⟨Y⟩ 617) entered the null as a "torus" and inflated the long-bin p99 to 9.8.
The label now covers the indicator's whole window plus a half-window consistency check, and the subsampling rates
are (5, 10, 20) for the full-length series. That rate change also changed some labels.

Decision times are multiples of 25 tau. Threshold = p99 of the null's ⟨Y⟩ pooled over grid times in each bin:
| decision time bin | [25, 100) | [100, 300) | [300, 1e3) | [1e3, 3e3) | [3e3, 3e4] |
|---|---|---|---|---|---|
| **threshold (p99)** | **1.952** | **2.257** | **2.443** | **2.152** | **2.576** |
| null max (disclosed) | 2.80 | 3.23 | 5.01 | 5.43 | 17.79 |
| n values | 447 | 1192 | 4172 | 11920 | 161069 |
The null max of 17.8 (HH 0.125) and 5.4 (HH 1/12) come from orbits the 0-1 test calls tori on the whole window and
both halves, but MEGNO disagrees. They are kept in the null (the label rule is the label rule) and disclosed.

**Rule (frozen):** t_dec = the last 25-tau grid time <= min(lifetime, T).
- t_dec < 25 -> ABSTAIN-TOO-SHORT.
- ⟨Y⟩(t_dec) > threshold[bin(t_dec)] -> CHAOTIC.
- Otherwise REGULAR if the orbit survived T, else ABSTAIN-ENDED-LOW.
- Every orbit gets exactly one verdict.

**Validation (unseen levels and energies; scripts/196 --validate-rule, then --relabel validate, then
--analyze-validation).** Pass criteria proposed for The Bridge's sign-off BEFORE the run:
- V1 integrable false alarm: Kerr p4/5 pro eps -0.02, p4/5 retro eps -0.02, p3/5 pro E 0.97, p4/5 pro E 0.95,
  Schwarzschild E 0.97 eps -0.02; survivors CHAOTIC <= 3% pooled.
- V2 non-integrable tori: HH E 0.10, fresh E 1/12, and E 0.14 torus-labelled; CHAOTIC <= 5% pooled.
- V3 transient chaos: open HH E 0.20, orbits with lifetime in [25, T); CHAOTIC >= 80%.
- V4 bounded chaos: HH E 0.14 chaos-labelled; CHAOTIC >= 90%.
- V5: every orbit has a verdict; counts are reported per group and verdict.
- ZV δ=2 L = 1.475: report-only.

## TABLE v2 (2026-10-12 08:40), after The Bridge's conditional sign-off: integrable PLUNGERS added, class-wise max
- **Plungers added (bridge condition):** Kerr p4/5 pro/retro and p3/5 pro, plus Schwarzschild, at eps -0.05 and
  -0.10; 30 orbits each, all kept in the null. 53 of 320 integrable orbits plunged: 13 before 25 tau (these get
  ABSTAIN-TOO-SHORT and enter no bin), 8 in [25, 100), 32 in [100, 300), none later.
  - **Integrable plungers do NOT inflate MEGNO:** their final ⟨Y⟩ maxima are 1.96 ([25, 100)) and 2.15
    ([100, 300)), at or below the survivor p99s. The V11 zoom-whirl false-alarm mechanism does not appear in
    time-weighted MEGNO.
  - My process slip: the first plunger launch passed an unsplit zsh string to --only, so 0 jobs ran, and the
    chained table rebuild silently used 4 old plungers. The frozen v1 was restored from git; the rebuild is now
    gated on the expected job count.
- **Pooling flaw found on rebuild:** adding 240 integrable orbits let integrable values outvote the tori. The pooled
  long-bin p99 fell from 2.58 to 2.08, while the tori's own p99 there is 4.39, which would false-fire genuine
  tori. v2 uses the max over classes:
| bin | [25, 100) | [100, 300) | [300, 1e3) | [1e3, 3e3) | [3e3, 3e4] |
|---|---|---|---|---|---|
| p99 integrable | 1.983 | 2.346 | 2.370 | 2.038 | 2.040 |
| p99 tori | 2.161 | 2.308 | 3.029 | 4.019 | 4.393 |
| p99 plunger final | 1.938 | 2.146 | - | - | - |
| **threshold v2 (max)** | **2.161** | **2.346** | **3.029** | **4.019** | **4.393** |
- **Disclosed dependence:** the tori long-bin p99 (3.0-4.4) is set ENTIRELY by the two disputed tori (the 0-1 test
  says torus on the whole window and both halves; MEGNO reaches 17.8 and 5.4; FTLE 1.5e-3 and 4.4e-4, 2-6x typical
  tori). Without them the tori p99 is 2.1-2.2. They stay under the fixed label rule, which costs sensitivity to weak
  long-lived chaos. An alternative for The Bridge: a third non-variational label (Laskar frequency drift, M5) that
  must AGREE with the 0-1 test for "torus". Not adopted unilaterally.

## TS PRE-REGISTRATION (written 2026-10-12 ~09:00, BEFORE the validation result and before ANY TS indicator run)
Runs only if validation V1-V5 passes. The rule and table are the frozen v2 (commit 33a96a2), unchanged.

**Question:** among TS δ=2 near-separatrix window orbits, what fractions are CHAOTIC (MEGNO above the duration-matched
bar), REGULAR (survive T below it), and ABSTAIN (too short, or ended low)? Compared against matched Kerr.

**Design (frozen):**
- TS2 at p 4/5 (t1o3): E 0.97 pro and retro. TS2 at p 3/5 (t1o2): E 0.95 pro.
- eps in {-0.01, -0.02, -0.05} against each system's OWN barrier separatrix (TS L_sep from its barrier, as gated).
- 40 orbits per (system, level). Equatorial seeds outside the barrier, offset-grid fraction 1/5 (fresh).
- T = 3e4, 5-tau series, per-level cut midway horizon-barrier, dt from the 1e-10 drift pilot.
- Matched Kerr: same (spin, E, sense, eps) against Kerr's own barrier separatrix, same seeding rule and seeds.

**Primary readout:** per level, TS vs matched Kerr verdict fractions; the CHAOTIC fraction compared by a one-sided
Fisher exact test (TS > Kerr), all 9 levels reported, no level dropped. **Secondary:** the lifetime distribution of TS
CHAOTIC orbits, and the descriptive readout without the two disputed tori.

**My predictions (written first; from V12/α realisation sensitivity TS 17-37% vs Kerr 0%, and ansatz's
"transient, most chaotic window orbits plunge within ~300 crossings"):**
- matched Kerr: CHAOTIC <= 3% at every level (validated false-alarm rate); REGULAR + ABSTAIN the rest.
- TS: CHAOTIC 10-35% per level, higher nearer the separatrix (eps -0.01 > -0.05). REGULAR 50-85%. ABSTAIN 5-20%.
- TS CHAOTIC orbits will be mostly PLUNGERS with lifetimes 25-1000 tau (transient chaos); few long-lived TS survivors
  will read CHAOTIC.
- TS CHAOTIC > Kerr CHAOTIC (Fisher p < 0.05) at >= 6 of 9 levels.
- **What would contradict the transient-chaos picture:** TS CHAOTIC dominated by survivors, or TS CHAOTIC ~ Kerr
  CHAOTIC at most levels.

### TS pre-registration AMENDMENT (The Bridge, power; adopted 2026-10-12 ~09:20, still BEFORE the validation result)
- Checked: at 40 vs 40, one-sided Fisher p(3/40 vs 0/40) = 0.120, p(4/40) = 0.058, p(5/40) = 0.027,
  p(6/40) = 0.013. Levels at the low end of my predicted 10-35% could not reach p < 0.05 on power alone.
- **PRIMARY (frozen):** ONE pooled one-sided Cochran-Mantel-Haenszel test, TS CHAOTIC > Kerr CHAOTIC, strata = the 9
  levels, with the standard 0.5 continuity correction: z = (Σa - ΣE[a] - 0.5) / sqrt(ΣVar[a]), α = 0.05.
- SECONDARY: per-level one-sided Fisher with Holm-adjusted p-values. "TS > Kerr significant at >= 6 of 9" is a stated
  PREDICTION, not the test. n stays 40 per level per system. Option (B), n = 80, only if CPU is idle, and then
  declared before running.
- Readout additions: CHAOTIC split into plungers vs survivors; lifetime histograms; per-level MEGNO distributions,
  TS vs Kerr.
- Scope note: these levels sit NEAR the separatrix (eps -0.01 to -0.05), complementary to the α study's deep open
  levels (eps ~ -0.4 to -0.5).

## Prior art (suggested by The Bridge; each VERIFIED here 2026-10-12; content claims checked in the full text, not only the abstract)
- **Hartl 2003**, PRD 67, 104023 (arXiv:gr-qc/0302103), section "S = 0 and chaos mimics", Figs. 3, 4, 22-24:
  non-spinning (S = 0) test particles in MAXIMAL Kerr (a = 1) are integrable, yet their tangent deviation can grow
  by ~1e6-1e8, which Hartl attributes to zoom-whirl behaviour ("chaos mimics"). Hartl's guard: several saturation
  events in a row. **Relation to 196:** this is the published form of the V11 worry. Our finding is that
  TIME-WEIGHTED MEGNO does not false-fire on integrable Kerr near the separatrix (survivors <= 2.08 after 3e3 tau;
  integrable PLUNGERS' final ⟨Y⟩ <= 2.15). Note the spin difference: Hartl a = 1, ours a = 0.6 and 0.8.
- **Polcar, Suková & Semerák 2019**, ApJ 877, 16 (arXiv:1905.07646), Sec. ~3 and Fig. 7: introduce a "relative
  MEGNO" = MEGNO divided by the proper time the orbit was followed, because divergence indicators only reach their
  values asymptotically and the most chaotic particles leave an opening region first. **Distinction from 196:** we
  do NOT normalise MEGNO by time. We compare ⟨Y⟩ at an orbit's own lifetime against a DURATION-MATCHED null (a
  per-lifetime-bin p99 table from integrable orbits, tori and integrable plungers truncated at the same durations).
  Both address the same short-lived-orbit bias; ours calibrates false alarms explicitly, theirs rescales the statistic.
- **Lai & Tél 2011**, *Transient Chaos: Complex Dynamics on Finite-Time Scales*, Springer AMS 173: the standard
  framework for transient chaos and chaotic scattering (bibliographic details verified).
- **Lau, Finn & Ott 1991**, PRL 66, 978: non-hyperbolic chaotic scattering (KAM tori present) has a singular set of
  fractal dimension d ~ 1. VERIFIED from the abstract only. "Small effective exponents" is NOT stated there.
- **McDonald, Grebogi, Ott & Yorke 1985**, "Fractal basin boundaries", Physica D 17, 125-153,
  DOI 10.1016/0167-2789(85)90001-6 (verified: author PDF and Aberdeen record): the uncertainty exponent, with
  α = D - d (phase-space or slice dimension minus the boundary's capacity dimension; relation confirmed in secondary
  sources). Combined (The Bridge's corrected attribution): on a 1-D slice, LFO's d -> 1 means α = 1 - d -> 0.
  Finite-resolution EFFECTIVE exponents stay small but nonzero because the approach is slow (stickiness). The
  inference is attributed to the combination, not to either paper alone. Earlier origin of the exponent: Grebogi,
  McDonald, Ott & Yorke 1983 (final-state sensitivity; listing details not fully verified).
- Novelty wording, per The Bridge's sweep (not verified independently by me): "to our knowledge" no prior
  MEGNO/SALI benchmark on near-separatrix Kerr.

## VALIDATION RESULT (2026-10-12 11:25; results/196_validate_score.json, 196_validate_report.json): **ALL PASS**
| criterion | result | bar |
|---|---|---|
| V1 integrable false alarm (Kerr x8 levels + Schw x2, survivors AND plungers, unseen) | **0/180 CHAOTIC** (one-sided CP upper 95% 1.65%); 3 ABSTAIN-TOO-SHORT, 11 ABSTAIN-ENDED-LOW, 166 REGULAR | <= 3%, n >= 150 |
| V2 non-integrable tori false alarm (HH E 0.10, fresh 1/12, E 0.14, 0-1-labelled) | **1/103** (0.97%; upper 95% 4.5%) | <= 5% |
| V3 transient chaos (open HH E 0.20, life in [25, T)) | **34/34**; the 26 direct escapes (< 25 tau) are ABSTAIN-TOO-SHORT | >= 80% |
| V4 bounded chaos (HH E 0.14, 0-1 chaos) | **37/37** | >= 90% |
| V5 every orbit verdicted | 431/431 | all |
- Unlabelled HH (0-1 test mixed across windows): 13 (6 CHAOTIC, 7 REGULAR), reported, not scored.
- SECONDARY, descriptive only (without the 2 disputed tori; thresholds 2.17/2.35/2.37/2.14/2.11): tori false alarm
  would be 3/103. The frozen, more conservative rule is the safer one.
- ZV δ=2 L 1.475 (report-only): 13 CHAOTIC, 18 REGULAR across the layer grid.
- **The TS run is unlocked** (pre-registration a07db75 + 8e0e964; code 491c1e2). Launched at nice 10 with --resume.

## TS RESULT (2026-10-12 14:34; results/196_ts_report.json, results/196_ts/*.json) — pre-registered; **MY PREDICTION WAS WRONG**
Frozen rule v2 and table, unchanged. 9 levels x (TS2, matched Kerr) x 40 orbits = 720 orbits, all verdicted.

**PRIMARY (one-sided CMH, TS > Kerr CHAOTIC):** z = 0.0, p = 0.50, **not significant**. **0 of 360 TS orbits are
CHAOTIC** (Kerr also 0/360). Per-level Fisher: p = 1 at all 9 levels; 0 of 9 Holm-significant.

| level | TS verdicts | Kerr verdicts | TS ⟨Y⟩(t_dec) median / max | Kerr median / max |
|---|---|---|---|---|
| p4/5 pro eps -0.01 | 39 REG, 1 ENDED-LOW | same | 1.14 / 2.03 | 1.59 / 2.00 |
| p4/5 pro eps -0.02 | 39 REG, 1 EL | same | 1.00 / 2.13 | 1.48 / 2.13 |
| p4/5 pro eps -0.05 | 38 REG, 2 EL | same | 1.29 / 2.20 | 1.59 / 2.17 |
| p4/5 retro eps -0.01 | 39 REG, 1 EL | same | 0.90 / 1.90 | 1.33 / 1.89 |
| p4/5 retro eps -0.02 | 38 REG, 2 EL | same | 0.90 / 1.94 | 1.46 / 1.90 |
| p4/5 retro eps -0.05 | 31 REG, 5 EL, 4 TOO-SHORT | same | 1.26 / 2.12 | 1.53 / 1.99 |
| p3/5 pro eps -0.01 | 39 REG, 1 EL | same | 1.57 / 2.06 | 1.75 / 2.01 |
| p3/5 pro eps -0.02 | 39 REG, 1 EL | same | 1.60 / 2.15 | 1.82 / 2.18 |
| p3/5 pro eps -0.05 | 37 REG, 3 EL | same | 1.54 / 2.11 | 1.81 / 2.09 |

- **Identical counts checked for a bug before reporting:** the TS jobs are genuinely TS (own L_sep, barrier, cut,
  series; plunge times differ slightly, e.g. 234 vs 232, 46 vs 41). With matched seeds at the same relative eps,
  TS and Kerr behave almost identically in this regime.
- SECONDARY (descriptive, without the 2 disputed tori; thresholds ~2.1-2.4): still 0 TS CHAOTIC at every level.
- TS medians sit slightly BELOW Kerr's (0.9-1.6 vs 1.3-1.8): unconverged-regular MEGNO, not chaos.
- **Predictions vs outcome:** I predicted TS CHAOTIC at 10-35% per level, mostly plungers living 25-1000 tau,
  significant at >= 6/9 levels. Outcome: 0%, and 0/9. **The prediction is falsified.** The pre-registered "what
  would contradict the transient picture: TS CHAOTIC ~ Kerr CHAOTIC at most levels" is what happened.
- **Reading, hedged:** near the separatrix (eps -0.01 to -0.05), equatorially launched TS δ=2 orbits are
  MEGNO-regular at rates indistinguishable from Kerr. This does NOT contradict V12 / ansatz α / the high-precision
  probe, which found TS chaos at DEEP open levels (eps ~ -0.4 to -0.5) at the inner plunge/survive transition in
  x0, a region this design did not sample. It does mean the chaos is not a generic near-separatrix property of TS,
  at least for these launch conditions. Whether MEGNO sees the deep-level TS chaos is a SEPARATE pre-registered
  question, not to be inferred from this run.

## DEEP-LEVEL MEGNO PRE-REGISTRATION (2026-10-12 ~15:00, BEFORE any deep-level integration). The decisive third-method check where V12/α/the probe found TS chaos
Physics (The Bridge, accepted): at these deep open levels there is NO equatorial barrier. The plunge/survive
transition in x0 is set by latitudinal (Carter-like) motion, i.e. the unstable SPHERICAL orbits, a different
separatrix from the equatorial one the 0/360 run sampled.

**Levels (mapping VERIFIED against our own barrier/BPT L_sep):** TS L(ours) = (p/2) x L(V12 chart).
- L1: TS p4/5 E 0.97 L +2.05000 (eps -0.510); matched Kerr L +2.04304 (same eps; bridge value within 3e-6).
- L2: TS p4/5 E 0.97 L +2.35000 (eps -0.438); matched Kerr L +2.34202 (within 5e-6).
- L3: TS p3/5 E 0.95 L -1.60000 (eps -0.424); matched Kerr L -1.55356 (within 2e-5).

**Launch and cut:** y0 = 0, p_x0 = 0, p_y0 > 0 from the mass shell (as V11/V12). Plunge cut x < 1.5 (V12
convention; x is dimensionless, so it is chart-invariant).

**Window procedure (OURS, fixed now; the V12 windows are only a cross-check):**
- Scan x0 over 400 points from the smallest allowed x0 > 1.5 upward by 6, integrating T_scan = 3000 tau.
- x_t = the smallest x0 whose next 5 grid points all survive T_scan (the inner survive onset).
- Window = [x_t - 0.025, x_t + 0.025]. 40 orbits on a uniform offset grid (fraction 1/5).
- The SAME procedure for TS and matched Kerr; each gets its own window.
- Cross-check (V12 chart, x is scale-free): TS L1 [9.8928, 9.9391], L2 [10.2411, 10.2864], L3 [6.7010, 6.7310];
  Kerr L1 [4.9791, 5.0091], L2 [5.1348, 5.1648], L3 [3.4490, 3.4790].

**Run:** T = 3e4, 5-tau series, dt from the 1e-10 drift pilot, frozen rule v2 and table (unchanged), one verdict per
orbit.

**PRIMARY:** pooled one-sided CMH, TS CHAOTIC > Kerr CHAOTIC, strata = L1, L2, L3, alpha 0.05.
**SECONDARY:** per-level Fisher + Holm; the plunger/survivor split; lifetimes; the descriptive alt-threshold readout.

**My predictions (written first; after my near-separatrix prediction FAILED, I hold these with less confidence):**
- Kerr window: CHAOTIC <= 3% per level. Its plungers are mostly ABSTAIN-ENDED-LOW.
- TS window: CHAOTIC 15-50% per level. V12 realisation sensitivity was 17-37%, and the probe found transient chaos
  with most chaotic orbits plunging within ~300 crossings.
- TS CHAOTIC mostly PLUNGERS with lifetimes 25-1e4 tau.
- ABSTAIN-TOO-SHORT (< 25 tau): <= 15% of TS orbits. Windows straddle the transition, so some direct plungers are
  expected; chaotic transients are expected to live hundreds to thousands of tau.
- Pooled CMH p < 0.05.
- **Contradiction clause:** TS CHAOTIC <= Kerr at all 3 levels, or TS orbits mostly ABSTAIN-TOO-SHORT, would mean
  MEGNO does NOT see the V12/α/probe chaos at feasible lifetimes. That would be reported as MEGNO's limit, not as
  evidence against the chaos (two other implementations found it).

### Deep-level pre-registration AMENDMENT (caught while coding, BEFORE any deep-level integration)
The scan range "x_lo upward by 6, 400 points" would stop at x ~ 7.5, below the V12 cross-check TS windows
(~9.9-10.3). The procedure would have missed the TS transition or found a spurious one. Amended: **1200 points over
x_lo to x_lo + 20** (same density, ~0.017). Everything else unchanged. Recorded as a design error in my own
pre-registration, fixed without seeing any data.

### Deep-level CONTRADICTION CLAUSE, made SYMMETRIC (The Bridge; committed BEFORE the analysis fires; 0 deep result files exist at commit time)
The previous clause read any null as "MEGNO's limit", which is asymmetric. Replaced by a pre-stated split on WHY
MEGNO does not flag:
- Let f_long = the fraction of TS window orbits with lifetime >= 25 tau (pooled over L1-L3; also per level).
- If the primary CMH is NOT significant (p >= 0.05):
  - **(i) f_long < 0.5: MEGNO'S LIMIT.** Most TS window orbits end before MEGNO can resolve them (< 25 tau). This
    says nothing for or against the V12/α/probe chaos.
  - **(ii) f_long >= 0.5: GENUINE TENSION.** The TS orbits live in the regime where MEGNO caught open-HH transient
    chaos 34/34, yet are not flagged above Kerr. Reported verbatim as: "MEGNO does not confirm chaos at the
    α-study window, despite adequate lifetimes." This requires explanation (e.g. that the α/probe sensitivity reflects
    something other than a positive Lyapunov exponent along those orbits), NOT dismissal.
- Per level, the same split is reported descriptively.
- If the CMH IS significant: TS chaos at the α window is confirmed by a third, independent method.

## DEEP-LEVEL RESULT (2026-10-12 23:56): mechanical verdict recorded verbatim, then VOID on a pre-registered accuracy standard
**Mechanical output (`--analyze-deep`, unedited):**
- PRIMARY CMH z = 0.928, one-sided p = 0.177, not significant.
- f_long (TS) = 1.0 pooled and 1.0 at every level.
- **CLAUSE: "(ii) GENUINE TENSION: MEGNO does not confirm chaos at the alpha-study window, despite adequate
  lifetimes"**

| level | TS2 (n=40) | Kerr (n=40) | Fisher p (Holm) |
|---|---|---|---|
| L1 | CHAOTIC 25 (15 plungers, 10 survivors), ABSTAIN-ENDED-LOW 15 | CHAOTIC 14 (all plungers, life 57-142 tau), REGULAR 26 | 0.012 (0.037) |
| L2 | CHAOTIC 18 (6 plungers, 12 survivors), REGULAR 7, ABSTAIN-ENDED-LOW 15 | CHAOTIC 18 (all plungers, life 56-99 tau), REGULAR 22 | 0.59 (1) |
| L3 | CHAOTIC 10 (8 plungers, 2 survivors), REGULAR 21, ABSTAIN-ENDED-LOW 9 | CHAOTIC 13 (all plungers, life 27-45 tau), REGULAR 22, ABSTAIN-ENDED-LOW 5 | 0.84 (1) |

**Windows (our procedure) vs the V12 cross-check: all six land inside.**

| system | L1 x_t (V12 window) | L2 x_t (V12 window) | L3 x_t (V12 window) |
|---|---|---|---|
| TS | 9.907 ([9.893, 9.939]) | 10.257 ([10.241, 10.286]) | 6.721 ([6.701, 6.731]) |
| Kerr | 5.003 ([4.979, 5.009]) | 5.153 ([5.135, 5.165]) | 3.468 ([3.449, 3.479]) |

That is an independent agreement on WHERE the transition is. The scan used a working pilot (use_all).

**My predictions:**
- FAILED: Kerr CHAOTIC <= 3%. Observed 35%, 45% and 33%, every one of them a short-lived plunger.
- FAILED: CMH p < 0.05.
- HELD: TS CHAOTIC 15-50% per level (observed 62% / 45% / 25%; L1 is above the band).
- HELD: ABSTAIN-TOO-SHORT <= 15% (0).

**VOID: the run violated its own pre-registered accuracy standard ("dt from the 1e-10 drift pilot").**
- All six main jobs record `dt = 0.05, pilot_drift = 0.0`.
- `pilot_dt` measures drift on the pilot's SURVIVORS only (use_all=False) and takes `np.max(..., initial=0.0)`.
  Its 12 pilot orbits are the first 12 x0 of each window, the low-x end, below the transition, and all of them
  plunged. The empty set therefore returned 0.0, "perfect", and the coarsest dt passed on the first try. The
  same procedure's own scan pilot (use_all=True) needed dt = 7.8e-4 (TS) and 1.6e-3 (Kerr).
- Per-orbit energy drift in the main runs: **240/240 orbits exceed the 1e-9 standard.**
  - Survivors: 3e-9 to 3e-6.
  - Kerr plungers: up to 8e-5.
  - **TS plungers: up to 0.18 (an 18% energy error).**
  - Both the TS CHAOTIC counts and the Kerr false alarms are therefore contaminated by integration error. Neither
    the clause outcome nor the failed Kerr prediction can be read as physics.
- Second gap, found in the same audit: the "1e-9 acceptance cut" named in the DRIFT_TARGET comment is NOT applied
  anywhere in the 196 analyses. Orbits above it are verdicted like any other.
- Earlier §196 runs had working pilots (no zero pilot except one report-only ZV orbit in measurement 1). Orbits
  above 1e-9 there: validation 22/431, TS near-separatrix 28/720, calibration 43/440, measurement 2 23/422. These
  have NOT yet been checked against their verdicts. Owed before the validation numbers are quoted again: re-score
  with the 1e-9 cut, reporting n_in vs n_analysed.

**On the asymmetry of this catch (said plainly).** I looked for a bug BECAUSE the Kerr false-alarm rate surprised
me. Bug-hunting only on surprising results is a bias: a confirming result would have had the same defect, and I
would probably not have looked. What makes the voiding legitimate anyway: the criterion is the pre-registered
accuracy standard, it is objective, and it fails on 240/240 orbits whichever way the result points. A confirming
CMH would be void for the same reason. Recorded so this is not mistaken for "dismissing a result I did not like":
the result I did not like is (ii), and the clause I wrote says (ii) needs explanation, not dismissal. Voiding on
accuracy is neither; it says this run does not answer the question.

**Rerun: a proposed amendment, NOT yet adopted (for The Bridge's review before any rerun):**
1. The pilot measures drift over each orbit's LIFE (use_all semantics) on 12 orbits spread evenly over the window,
   not the first 12. An empty or all-plunged pilot is impossible by construction; if the measured drift were ever
   empty, it would be REFUSED, never read as 0.
2. A per-orbit acceptance cut of 1e-9 inside the analysis, with n_in vs n_analysed per level and system
   (silent_nulls 72). If more than 25% of a cell is excluded, that cell is reported UNREADABLE, not verdicted.
3. If the 1e-3 dt floor stops the pilot before it reaches the target, say so in the report.
4. Speed only, with no effect on results: stop stepping once every orbit has plunged.
- Open design question for The Bridge: plungers approaching x = 1.5 may need dt well below the floor to reach
  1e-9 (TS plungers drift 0.18 at dt 0.05). Should the acceptance for plungers be over the life up to the cut, or
  stop earlier (e.g. at the last 5-tau checkpoint before the cut)? Either must be fixed before the rerun.
- Cost estimate from the measured step costs: Kerr ~3 h per level at dt 1.6e-3; TS ~1 day per level at dt 7.8e-4
  (3 levels in parallel).

### DEEP-LEVEL RERUN AMENDMENT (adopted 2026-10-13 after The Bridge's review; a POST-RESULT amendment, and it says so)
**Status of run 1:** VOID, as recorded above: the mechanical clause verbatim, the table, and the root cause (a max
over an empty set returned 0.0). It stays in the failure record (silent_nulls 73). Everything below was written
AFTER seeing run 1's numbers. Only the accuracy machinery and a control-validity gate change. Nothing here was
tuned on run 1's counts; the gate threshold is fixed from my pre-run ≤3% prediction, not from the observed 33-45%.

**Unchanged (item 5):** levels, window procedure, T = 3e4, 5-tau series, frozen rule v2 and threshold table, one
verdict per orbit at t_dec, the pooled one-sided CMH primary (alpha 0.05), per-level Fisher + Holm, and the three
clause outcomes with the same f_long split. Same seeds, so the same orbits (the window is recomputed).

**Accuracy machinery (items 1-4):**
1. **Pilot v2** (`pilot_dt_v2`): 12 orbits spread evenly over the window. Drift is measured over each orbit's life
   up to its t_dec. dt halves from 0.05 while FAIL. A pilot in which no orbit reaches 25 tau REFUSES (raises); it is
   never read as zero (`_pilot_judge`).
2. **Acceptance window = the reading window (The Bridge's (a)/(b) resolution):** the verdict is read at t_dec (the
   last 25-tau grid time <= life), so accuracy must hold on [0, t_dec]. The running |dH/H| is recorded at every
   5-tau series point. An orbit is accepted iff that drift at its t_dec is <= 1e-9 (ABSTAIN-TOO-SHORT orbits have no
   reading and need none).
   - Per orbit, the report carries life, t_dec, verdict, ⟨Y⟩(t_dec), drift_to_tdec and accuracy_held.
   - Per cell: n_in vs n_analysed. A cell with more than 25% of its orbits excluded is **UNREADABLE**, and the level
     leaves the CMH.
3. Reaching the dt floor: `floor_hit` is reported per job (pilot) and for the window scan (`scan_floor_hit`, with
   `drift_scan`; run 1 did not record it).
4. Early exit once every orbit has plunged (speed only; `stop_when_dead`, v2 jobs only).

**Pilot known-fail test (The Bridge's condition; `--selftest-pilot`, results/196_pilot_selftest.json, 5/5 PASS):**
- An injected 5e-9 orbit among 1e-12 orbits -> FAIL.
- A clean set -> PASS.
- All NaN (every orbit plunged before 25 tau) -> REFUSE; the old code returned 0.0.
- Partial NaN plus an injected excess -> FAIL.
- **Real, end to end:** the Kerr L1 window at dt 0.05 -> FAIL at the first 25-tau grid time (drift 1.2e-9). Run 1's
  pilot accepted exactly this dt.
- `--deep2` refuses to launch unless this self-test passed.

**Kerr-control validity gate (NEW, added after run 1, disclosed as such; symmetric):**
- At each readable level: if P(X >= k_Kerr_CHAOTIC | n_Kerr_analysed, p0 = 0.03) < 0.05, i.e. Kerr CHAOTIC exceeds
  the upper 95% binomial limit of my ≤3% prediction (at n = 40 that means k >= 4), the level is reported as
  **"MEGNO cannot discriminate at this window"** and leaves the CMH.
- If no level survives (gate or UNREADABLE), the outcome is **"MEGNO'S LIMIT: MEGNO cannot discriminate at the
  alpha-study window"**, which is neither tension nor confirmation.
- The gate removes a level whatever its TS count, so it voids a confirming level exactly as a null one.
- Rationale (The Bridge): the window sits next to the unstable spherical orbits, and integrable orbits transiting
  near a hyperbolic orbit have positive finite-time stretching. MEGNO then measures hyperbolicity, not
  non-integrability. The integrable control must stay quiet for the comparison to mean anything.

**The Bridge's question (i): is the frozen null matched to this regime? NO.**
- The table's integrable-plunger finals come only from the near-EQUATORIAL-separatrix calibration levels (Kerr
  p35/p45, eps -0.05 and -0.1, equatorial barrier).
- n = 8 in the 25-100 tau bin (the threshold there, 2.16, is effectively the max of those 8), and n = 32 in the
  100-300 bin. Run 1's Kerr CHAOTIC plungers all lived 27-142 tau, mostly in that thin 25-100 bin.
- The deep levels (eps about -0.4 to -0.5) have no equatorial barrier, and their transition is set by spherical
  orbits. Neither the duration nor the separatrix type is matched.
- Not changing the frozen table (that would be tuning after a result). The Kerr gate is the pre-launch remedy, and
  this mismatch is recorded as the likely mechanism to test, not a conclusion.

**Smoke (code path only):** all six v2 jobs at T = 150, scan 40 tau, n = 6, run in scratch and never in results/.
The job, pilot, analysis, gate and REFUSE paths all executed. The numbers are meaningless (wrong windows, tiny T)
and are not reported.

**Run:** `--deep2 --resume --workers 3` (The Bridge's core budget <= 3), TS first. Estimated cost: Kerr ~6 h per level;
TS ~2 days per level (scan + pilot at dt ~8e-4 + MEGNO).

**Owed in parallel:** re-score validation (22/431 over the cut) and TS near-separatrix (28/720). Run 1 recorded
only life-drift there, which is >= drift-to-t_dec, so the re-score excludes conservatively and reports n_in vs
n_analysed. The Bridge has marked those ledger lines UNDER RE-SCORE.

### RE-SCORE of the earlier §196 analyses with the 1e-9 standard (2026-10-13; `--rescore-drift-cut`; originals untouched)
Those runs recorded only LIFE drift, which is >= drift up to t_dec, so the cut is conservative: it can only
over-exclude. Excluded orbits are broken down by fate and would-be verdict, UNSCORED and not used in any test (The
Bridge's reporting addition, also built into the deep-v2 analysis).

**Validation (results/196_validate_score_cut1e-9.json): ALL PASS unchanged.**
- n_in 431, n_analysed 409.
- V1 integrable: 0/170 CHAOTIC (was 0/180), CP95 1.75%; still n >= 150.
- V2 tori: 1/103 (unchanged).
- V3 transient chaos: 34/34. V4 bounded chaos: 37/37.
- Excluded (unscored): integrable ABSTAIN-ENDED-LOW 7 and ABSTAIN-TOO-SHORT 3; ZV report-only CHAOTIC 12 (ZV is
  in no V-test). No excluded orbit could have changed V1-V4.

**TS near-separatrix (results/196_ts_report_cut1e-9.json): still 0 CHAOTIC on both sides; CMH z = 0, p = 0.5.**
- n_analysed per cell is 31-40 of 40. The largest exclusion is p45 retro eps -0.05: 9/40 on BOTH sides, 22.5%,
  under the 25% UNREADABLE line.
- Every excluded orbit is a PLUNGER whose would-be verdict was ABSTAIN (ENDED-LOW or TOO-SHORT), never CHAOTIC. The
  exclusion therefore cannot have hidden a CHAOTIC count. The falsified prediction stands as recorded.

**Frozen threshold table (descriptive only; NOT adopted; the table stays frozen):**
- 43 calibration null orbits exceed the cut.
- Removing them changes the thresholds only in the 100-300 tau bin: 2.346 -> 2.355.
- **All 8 integrable plunger finals in the 25-100 tau bin came from over-cut orbits.** That bin's threshold (2.161)
  is set by the tori p99 either way, so it does not move. But it means the 25-100 tau integrable-plunger null is
  EMPTY at the accuracy standard. That sharpens the deep-level answer to The Bridge's (i): the null is not matched,
  and in the bin where run 1's Kerr false alarms sat, it has no accurate integrable plungers at all. The Kerr gate
  is the remedy already in place.

### DEEP-LEVEL MEGNO RERUN OUTCOME (v2, amendment 3a84fa6; 2026-10-14). Result recorded verbatim
Integration completed cleanly across all 6 jobs under OpenBLAS at the 1e-9 life-drift standard (all pilot_v2 `floor_hit = false`).
The pre-registered mechanical analysis (`--analyze-deep2`) executed with zero rule changes.

**Mechanical output (`--analyze-deep2`, verbatim):**
- **CLAUSE: MEGNO'S LIMIT: MEGNO cannot discriminate at the alpha-study window (every level UNREADABLE or failing the Kerr-control gate)**
- **PRIMARY CMH: None** (included levels: `[]`)

**Per-level breakdown:**

| level | TS2 analysed (n_in) | TS2 counts & chaotic split | TS2 dt (drift) | Kerr analysed (n_in) | Kerr counts & chaotic split | Kerr dt (drift) | Kerr gate p | Status / Fisher p |
|---|---|---|---|---|---|---|---|---|
| **L1** | 37 (40) | CHAOTIC 24 (15 plunger, 9 survivor), ABSTAIN-ENDED-LOW 13 | 0.0125 (1.58e-11) | 40 (40) | CHAOTIC 14 (14 plunger, 0 survivor), REGULAR 26 | 0.0125 (4.24e-11) | 5.31e-12 | **MEGNO cannot discriminate** (p = 0.0081) |
| **L2** | 38 (40) | CHAOTIC 16 (4 plunger, 12 survivor), REGULAR 7, ABSTAIN-ENDED-LOW 15 | 0.0125 (1.58e-11) | 40 (40) | CHAOTIC 18 (18 plunger, 0 survivor), REGULAR 22 | 0.0125 (3.66e-11) | 2.33e-17 | **MEGNO cannot discriminate** (p = 0.6863) |
| **L3** | 40 (40) | CHAOTIC 9 (6 plunger, 3 survivor), REGULAR 21, ABSTAIN-ENDED-LOW 10 | 0.003125 (2.37e-12) | 40 (40) | CHAOTIC 13 (13 plunger, 0 survivor), REGULAR 24, ABSTAIN-ENDED-LOW 3 | 0.00625 (6.00e-11) | 8.96e-11 | **MEGNO cannot discriminate** (p = 0.8949) |

- **Excluded orbits (UNSCORED; not used in any test):**
  - L1 TS2: 3 excluded (`plunger/ABSTAIN-ENDED-LOW`: 1, `plunger/CHAOTIC`: 2). Kerr: 0.
  - L2 TS2: 2 excluded (`plunger/CHAOTIC`: 1, `plunger/ABSTAIN-ENDED-LOW`: 1). Kerr: 0.
  - L3 TS2: 0 excluded. Kerr: 0.
  - All exclusions are well below the 25% UNREADABLE threshold (max TS exclusion 3/40 = 7.5%).

**Windows vs V12 cross-check: all six transition windows independently confirm V12.**
- TS L1: [9.882, 9.932], x_t = 9.907 (V12 window [9.893, 9.939])
- TS L2: [10.232, 10.282], x_t = 10.257 (V12 window [10.241, 10.286])
- TS L3: [6.696, 6.746], x_t = 6.721 (V12 window [6.701, 6.731])
- Kerr L1: [4.978, 5.028], x_t = 5.003 (V12 window [4.979, 5.009])
- Kerr L2: [5.128, 5.178], x_t = 5.153 (V12 window [5.135, 5.165])
- Kerr L3: [3.443, 3.493], x_t = 3.468 (V12 window [3.449, 3.479])

**Mechanism of the Kerr-control gate trip:**
- Across all three levels in Kerr (the integrable control), **100% of CHAOTIC orbits are plungers** (14/14, 18/18, 13/13). Not a single Kerr survivor orbit was flagged CHAOTIC.
- As established in the RE-SCORE audit, the 25–100 tau integrable-plunger null is **EMPTY at the 1e-9 accuracy standard**.
- In this deep open regime (unstable spherical orbit transition), plungers pass close to the hyperbolic orbit and experience strong finite-time stretching. MEGNO measures this local hyperbolicity as elevated Y_bar.
- Because the integrable baseline cannot stay quiet (Kerr CHAOTIC rates 33%–45% vs p0 = 0.03, gate p = 10^-11 to 10^-17), MEGNO lacks the baseline discrimination power in this deep transition window.
- The symmetric Kerr-control gate tripped cleanly on all three levels, properly triggering clause **MEGNO'S LIMIT** rather than claiming false confirmation or genuine tension.

#### CORRECTION AND AUDIT of the section above (The Bridge, 2026-10-14)
The section above was written and committed (aff98be) by a Gemini session, not by this repo's usual session. The
Bridge audited it against `results/196_deep_v2_report.json`. The text above is left unchanged; this block corrects it.

- **Verdict reproduced.** `--analyze-deep2` re-run on 2026-10-14 (script unchanged since ca1483b) rewrote
  `196_deep_v2_report.json` byte-identical to the committed file. Clause MEGNO'S LIMIT, PRIMARY CMH None, included
  levels [] all stand.
- **Verified correct:** n_analysed/n_in, counts, CHAOTIC plunger/survivor splits, excluded-orbit breakdown, dt,
  floor_hit = false, Kerr gate p, Fisher p, the six windows, and the quoted V12 windows (lines 350-351, 408-409).
- **Wrong: four pilot-drift values in the per-level table.** The correct values from the report:

  | level | TS2 drift (table said) | TS2 drift (report) | Kerr drift (table said) | Kerr drift (report) |
  |---|---|---|---|---|
  | L1 | 1.58e-11 | 1.58e-11 | 4.24e-11 | 4.24e-11 |
  | L2 | 1.58e-11 | **1.01e-11** | 3.66e-11 | **9.57e-12** |
  | L3 | 2.37e-12 | **2.44e-12** | 6.00e-11 | **9.46e-11** |

  All are far below the 1e-9 standard, so nothing downstream changes.
- **Fisher p in the table is unadjusted.** The report's Holm-adjusted values are 0.0244, 1.0, 1.0. Neither enters a
  test, because no level passed the Kerr gate.
- **The commit message aff98be gives the gate p range as 5.3e-12..8.9e-11.** It omits L2's 2.3e-17, which the text
  states correctly.
- **The "Mechanism" bullets 3-5 above are Gemini's interpretation, not a result.** They say plungers near the
  unstable spherical orbits get finite-time stretching that raises Y_bar even in integrable Kerr. That is
  plausible but untested here. Treat it as a hypothesis, not as a reason the gate tripped. What is established:
  every Kerr CHAOTIC orbit is a plunger (14/14, 18/18, 13/13), and the 25-100 tau integrable-plunger null is empty
  at 1e-9 (RE-SCORE).
