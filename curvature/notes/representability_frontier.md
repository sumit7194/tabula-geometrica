# ② The Representability Frontier — a theory of the discoverable

**Started 2026-06-27** (after the SAE-legibility bridge ①). The big-swing arc: unify the project's scattered
LIMITS-of-discovery into ONE coherent account of *what a net can / cannot extract from observation, and why* — and make
that account a **predictive diagnostic**. Executable cold (this doc + the cited scripts).

## The thesis (one sentence)

Every "discovery" the project has done is a search for the **cheapest legible code** for the observations; every WALL
it has hit is a distinct *way that cheapest legible code fails to exist or fails to be unique*. The frontier is the
boundary of that search, and it has a small number of named failure modes.

## The taxonomy (the regimes a discovery-net lands in)

| verdict | what it means | the instrument (existing) | example scripts |
|---|---|---|---|
| **EMIT** | a UNIQUE cheap conserved code exists → the net extracts the law | emit-or-certify engine (generalized-eigenproblem invariant finder), held-out exact | 91–97, 127 (Kepler E/L, Kerr Carter, LRL) |
| **CERTIFY-CHAOS** | NO cheap invariant exists → the net provably can't find one | same engine: held-out var-ratio stays high; no low-degree polynomial invariant | 85, 93–95, 132 (Lorenz, chaotic quartic, ZV δ=2) |
| **CERTIFY-GAUGE** | a cheap code exists but only UP TO a gauge (frame / relabeling redundancy) → recovered law is non-unique | relational-vs-anchored: shape recovers, the absolute frame does not | 86, 111 (dS anchor), 101 (time gauge) |
| **CERTIFY-CONTEXTUAL** | NO consistent GLOBAL code → local descriptions can't be glued | a classical-bound test: the cheapest local-code score exceeds the bound | 84 (Bell, 1/√2), 87 (KCBS, 2/√5) |
| **PARTIAL-LEGIBLE** | the code EXISTS and is used, but is not LINEARLY legible (stored nonlinearly) | the legibility law: linear vs nonlinear decode gap; amortize→legible | 29, 106/135 (Wong dynamic ceiling), 139/140 |

**The unifying lens:** EMIT = the cheapest code is unique + legible. The four CERTIFY/PARTIAL rows are the four ways
that breaks: it doesn't exist (chaos), it isn't unique (gauge), it isn't globally consistent (contextual), or it isn't
linear (partial-legible). The frontier IS this 5-cell classification.

## The deliverable: a DISCOVERABILITY DIAGNOSTIC

One instrument that, given a system's observations, runs the appropriate sub-tests and returns the verdict + the
evidence (the conserved code if EMIT; the certificate if CERTIFY). The emit-or-certify engine (93/127) is the seed; the
arc extends it to the other failure modes and proves the whole table on a controlled MENU where each regime is dialed in
on demand.

## Experiment roadmap

- **EXP-1 (DONE 2026-06-27, script 141, 4/4): the discoverability trichotomy — EMIT / CERTIFY-GAUGE / CERTIFY-NO-CODE.**
  Built on the cleanest common substrate: PAIRWISE DISTANCES of a point configuration (reuses dS-anchor 111's
  reconstruct/errors/pdist). One diagnostic reads the residual 2D STRESS (does a cheap low-D code exist?) then the RAW
  frame error (unique, or a gauge?) and emits the verdict. EMIT = 2D config + anchor (stress 0, raw 0, unique);
  CERTIFY-GAUGE = same config relational (stress 0, shape aligned, raw 1.42 = frame is a gauge); CERTIFY-NO-CODE = a 6D
  config that does not embed in 2D (stress 1.29 = no cheap low-D code, the geometric analog of "no conserved invariant"
  / chaos). So beyond integrable-vs-chaotic, one instrument names the GAUGE failure. (The trajectory/emit-or-certify
  version of CHAOS proper — Lorenz held-out drift — folds into the same diagnostic in the synthesis; NO-CODE is its
  distance-geometry analog here.)
- **EXP-2 (DONE 2026-06-27, script 142, 3/3): CERTIFY-CONTEXTUAL.** On correlation-table data: fit the cheapest
  local hidden-variable code (simplex over the 16 deterministic strategies = the local polytope) + read CHSH. Classical
  table -> EMIT-CLASSICAL (fits, CHSH 0.70); singlet -> CERTIFY-CONTEXTUAL (can't fit, CHSH 2.83>2 = Bell certificate);
  and a Werner sweep LOCATES the wall (verdict flips at v=0.725 ~ 1/sqrt2). 4/5 verdicts now instrumented.
- **EXP-3 (DONE 2026-06-27, script 143 + writeup): PARTIAL-LEGIBLE + the unified diagnostic.** One instrument routes
  by data type (distances / correlations / code) and emits all FIVE verdicts correctly on a 7-case menu (U1+U2). The 5th
  verdict PARTIAL-LEGIBLE = a free code (linear 0.45, nonlinear 0.75 = info present, not linear). Synthesis:
  ../../writeups/representability_frontier.md. NOT in verify.sh (re-runs 139's train; the 5 verdicts gated by 139/141/142).
  Honest open scope: classifies KNOWN regimes routed by data type; inferring the regime of a fully-unknown system is the
  next swing.
- **EXP-4 (DONE 2026-07-02, script 145, 9/9 D1/D2/D3): the REGIME DETECTOR — fully-unknown systems.** Closes EXP-3's honest
  scope gap: 143 was TOLD the data type; 145 must infer it. Given a raw dataset with NO type label and NO ground truth,
  the detector (1) infers the DATA TYPE from structural signatures alone — square/symmetric/hollow/triangle-inequality
  → distances; discrete ±1 measurement records → correlations; 3D-array + temporal smoothness (lag-1 autocorr) →
  trajectories; exchangeable continuous tabular → code — then (2) runs the matching regime diagnostic, TRUTH-FREE:
  gauge is certified by exhibiting two distinct configs that explain the data equally (a rigid motion) with no anchor
  side-info to break the tie (anchor coordinates, when present, are DATA, not labels); legibility from decoding the
  dataset's own target column; contextuality from the samples' CHSH. NEW: the TRAJECTORY branch folds CHAOS-proper into
  the table — the web-verified 0–1 test for chaos (Gottwald–Melbourne; K→0 regular, K→1 chaotic) + the §99 emit-or-
  certify engine: Kepler → EMIT (K~0, exact invariant), Lorenz → CERTIFY-CHAOS (K~1, no invariant). Ground truth is used
  ONLY to gate. Pre-reg: D1 TYPE-INFERENCE all 9 menu systems typed correctly from structure alone; D2 TRAJECTORY branch
  correct (Kepler emit + its invariant held-out exact; Lorenz certify, K>0.8 vs K<0.2); D3 END-TO-END all 9 verdicts
  correct (type inferred + regime). Menu: 3 distance (anchored/relational/6D) + 2 measurement (LHV/singlet samples) +
  2 trajectory (Kepler/Lorenz) + 2 code (amortized/free). RESULT: all 9 typed AND verdicted correctly; Kepler
  invariant held-out 7e-18 (machine-exact), Lorenz K=0.997; gotcha caught in smoke (oversampled chaos reads K~0 → max
  over subsample rates). In verify.sh (45s). The table is now a DETECTOR, not just a classifier. Open: is the 5-cell set
  exhaustive (hunt a 6th wall)?
- **EXP-5 (DONE 2026-07-02, script 146, W1/W2/W3): the SIXTH-WALL / EXHAUSTIVENESS hunt.** RESULT: no 6th cell
  — the 5-cell table is EXHAUSTIVE for law-discoverability of well-sampled stationary systems, but it is ONE FACE of a
  3-axis space: DISCOVERABILITY (the table) × PREDICTABILITY (computational irreducibility, P-B) × SAMPLING
  (underdetermination near walls, P-C); partial observability is ABSORBED (Takens, P-A). Numbers below. Throw systems NOT built to fit
  the 5-cell taxonomy at the 145 detector; each must either land in an existing cell with correct evidence (evidence FOR
  exhaustiveness) or produce a documented misfit (seed of a new axis). Probes + predictions:
  - **P-A PARTIAL OBSERVABILITY → predict ABSORBED (not a new wall).** A single scalar observable from Kepler (regular)
    and Lorenz (chaotic). Web-verified Takens: delay embedding reconstructs the attractor from one observable, and the
    0–1 chaos test is *designed* for scalar series → the regular/chaotic verdict survives partial observation. Gate:
    K(Kepler-scalar) < 0.2 AND K(Lorenz-scalar) > 0.8 → partial obs reduces to existing cells.
  - **P-B COMPUTATIONAL IRREDUCIBILITY → predict GENUINE MISFIT (orthogonal axis).** An elementary cellular automaton
    (Rule 30/110), deterministic + short rule. Show (1) the one-step LAW is perfectly learnable (neighborhood→next-cell
    accuracy ≈ 1.0 = discoverable / EMIT-able) BUT (2) the trajectory is incompressible (a cell's column fails a
    compressibility/predictability proxy). Web-verified Wolfram: computational irreducibility is DISTINCT from chaos
    (deterministic, no shortcut). Gate: one-step accuracy > 0.99 AND incompressibility signature → documents a
    PREDICTABILITY axis the 5-cell (discoverability) table lacks.
  - **P-C FINITE-SAMPLE UNDERDETERMINATION → predict epistemic gap.** The 0–1 verdict on Lorenz degrades with a
    too-short series (unreliable K at small N) while stable at large N. Gate: short-N K is unreliable (crosses the
    regular threshold / high variance) while long-N K is stable > 0.8 → the detector needs an ABSTAIN output;
    underdetermination is an epistemic axis, not a world-cell.
  Honest conclusion structure: the 5-cell table is exhaustive for LAW-DISCOVERABILITY of well-sampled stationary systems;
  EXP-5 maps its boundaries — partial obs is ABSORBED (Takens), while computational irreducibility (a PREDICTABILITY
  axis) and finite-sample (an UNDERDETERMINATION axis) are ORTHOGONAL frontiers the table doesn't cover (not 6th cells in
  the same table — a "this table is one face of a larger space" annotation).
- **EXP-6 (DONE 2026-07-02, script 147, A1/A2/A3): the ABSTAIN-AWARE detector.** RESULT: A1 confident-correct on
  5 well-sampled systems (no spurious abstain); A2 honest-abstain on 3 underdetermined inputs (ZERO wrong verdicts);
  A3 near-boundary Werner resolves ABSTAIN(N≤256)→CONTEXTUAL(N≥1024) monotonically. Underdetermination is now an explicit
  output. In verify.sh.
- **EXP-7 (DONE 2026-07-02, script 148, G1/G2/G3): LAW-learnability vs TRAJECTORY-predictability DISSOCIATE.** Sharpens
  EXP-5's predictability axis with unambiguous metrics + clarifies two conflated "discoverability" notions: (1) the local
  RULE (one-step forecast R² / CA accuracy) vs (2) the TRAJECTORY (0-1 K / compressibility). RESULT: all 4 structured
  systems are law-learnable (Kepler/Lorenz R²=1.0, Rule 30/250 acc=1.0; iid-noise control fails R²=-0.001) but
  predictability SPLITS (Kepler/Rule 250 predictable; Lorenz/Rule 30 not). Lorenz & Rule 30 = law-learnable-yet-
  unpredictable → the levels are independent; the 5-cell frontier measures TRAJECTORY-level structure, not the local
  rule (which is almost always emit-able). In verify.sh. 
- **EXP-8 (DONE 2026-07-02, script 149, X1/X2/X3): MIXED-REGIME robustness test.** RESULT: the single-regime
  assumption IS a real limitation, and a fraction-chaotic readout fixes it (Hénon-Heiles KAM, cross-validated by Lyapunov):
  X1 λ bimodal at E=1/8 (modes coincide with pure ensembles); X2 true chaotic frac 0.55 intermediate (single label
  inadequate); X3 fraction-chaotic monotonic [0.0,0.12,0.55,0.78] matches KAM. BONUS (ties EXP-6): the 0-1 test
  false-positives on quasiperiodic orbits only at SHORT integration → an under-sampling artifact (abstain is the guard);
  λ is robust. In verify.sh.
- **EXP-9 (DONE 2026-07-02, script 150, U1/U2/U3/U4): the unified ROBUST detector.** Folds EXP-4 + EXP-6 + EXP-8 into ONE
  data-driven instrument: infer type, then return a confident VERDICT / ABSTAIN (under-sampled or near a wall) / MIXTURE
  (regimes coexist → report the fraction). 9/9 menu: U1 confident-correct on clean inputs; U2 Hénon-Heiles E=1/8 →
  MIXTURE (fraction 0.42); U3 ABSTAIN on 3 underdetermined inputs (short KAM, Werner N=16, 6-pt matrix) with ZERO wrong
  confident verdicts; U4 one instrument, all outcomes. The detector now degrades honestly. In verify.sh. The detector assumes ONE clean regime;
  this stress-tests that on a KAM MIXED PHASE SPACE (regular + chaotic orbits coexisting at one energy). Web-verified
  Hénon-Heiles: regular for E<1/12, MIXED for 1/12<E<1/6 (chaotic fraction grows with E), fully chaotic at E=1/6. Per
  orbit: 0-1 test K (chaos) + an independent finite-time max-Lyapunov λ (Benettin two-orbit method) for cross-validation.
  X1 MIXTURE-IS-REAL — at E=1/8 the per-orbit K's are BIMODAL (a fraction <0.3 regular AND a fraction >0.7 chaotic), and
  K agrees with λ (K-chaotic orbits have mean λ ≫ K-regular); unimodal at E_low/E_high. X2 SINGLE-VERDICT-LOSES-IT (the
  honest limitation) — at E=1/8 the true chaotic fraction is genuinely intermediate (in [0.2,0.8]), so a 145-style single
  aggregate verdict cannot represent the mixture. X3 MIXTURE-AWARE-RECOVERS-IT (the fix) — the fraction-chaotic readout is
  monotonic in E and matches KAM (≈0 at E_low, intermediate at E=1/8, ≈1 at E_high). Honest-negative-friendly.
## EXP-1 result (script 141, distance-geometry realization)

A distance-geometry menu, one diagnostic (read STRESS, then RAW frame error), correct verdict on each (all PASSED):
- F1 EMIT (2D config, anchored): low 2D stress (a cheap code exists, 0.000) AND low raw error (the frame is UNIQUE,
  0.000) → verdict EMIT.
- F2 CERTIFY-GAUGE (2D config, relational/no-anchor): low stress + low ALIGNED shape error (0.000) BUT high RAW frame
  error (1.42) → the absolute frame is a gauge → verdict CERTIFY-GAUGE.
- F3 CERTIFY-NO-CODE (6D config): HIGH 2D stress (1.29) — distances don't embed in 2D → verdict CERTIFY-NO-CODE (the
  geometric analog of "no conserved invariant" / chaos).
- F4 ONE DIAGNOSTIC, ALL THREE: the single verdict function classifies all three correctly.

**Honest scope (stated up front):** EXP-1 is the distance-geometry subset (NO-CODE stands in for trajectory CHAOS here);
the CONTEXTUAL (Bell/KCBS) + PARTIAL-LEGIBLE (legibility law) rows are EXP-2/3, and the trajectory emit-or-certify engine
(Lorenz drift = CHAOS proper) folds in at the synthesis. The point: ONE diagnostic already names three discovery
failure modes, not just integrable-vs-chaotic — the seed of the full frontier table.
