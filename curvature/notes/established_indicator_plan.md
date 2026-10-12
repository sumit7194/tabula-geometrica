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
