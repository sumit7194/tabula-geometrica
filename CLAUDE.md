# SpaceTime — project memory

> **Repo split (2026-06-13):** SpaceTime is now the **neural-network / curvature**
> project only. The three LIGO-data black-hole projects — `echoes/`,
> `ringdown_spectroscopy/`, `primordial_blackhole_search/` — moved to
> `../BlackHole/` (its own CLAUDE.md + verify.sh there). `conjecture_machine/`
> remains a separate standalone repo at the Github root (untouched). The three
> straddling concept docs (`dimensional_ladder.md`, `emergent_dimension.md`,
> `3plus1_vs_2plus1.md`) live in BOTH repos (relevant to each). User will
> `git init` SpaceTime and BlackHole separately.

## What this project is
A collaborative, step-by-step exploration of how spacetime concepts change with the
number of dimensions — climbing a "dimensional ladder" (1+1 → 2+1 → 3+1 → 4+1) toward a
real goal: **understanding how gravity curves spacetime, and whether that curvature
"is" an extra dimension** — then making that ambition *executable* as the `curvature/`
neural-network experiments (can a net DISCOVER geometry from raw observations?). The
conceptual docs are the intellectual on-ramp; `curvature/` is the live build.

## Who I'm working with
The user is **not a physicist** and is explicitly relying on me to carry the technical
correctness. Treat that as a responsibility, not a license to simplify into vagueness.

## Standing directive (the user asked me to "keep this in memory")
**Do real research every time. Verify load-bearing claims with web search before
asserting them — never recite physics from memory and hope.** Especially numbers,
formulas, and dimension-dependent facts. Cite sources in the docs. If something can't be
verified, say so plainly rather than bluffing.

## Working style that's landing well
- Explain intuitively first, then give the precise statement.
- Use a **verdict tag** when comparing worlds: ✅ clean parity (just fewer numbers) ·
  ⚠️ degenerate/vanishes · 🔀 qualitatively different.
- End sections with **open threads** so the user can pick the next direction.
- Keep the docs as **living documents** — extend them, don't rewrite from scratch.
- Go **step by step**; don't jump to the finale before the rungs are built.

## Docs in this repo
- `README.md` — index + roadmap toward the gravity finale.
- `discovering_curvature_with_nn.md` — the user's real ambition (the charter for
  `curvature/`): can an NN DISCOVER curvature unsupervised from adjacent observables
  (never told the law)? Paradigm = SciNet bottleneck. Precedent = Wetzel net discovered
  the Minkowski interval. Verdict: pure dream provably impossible (Locatello), but a
  minimal-bias variant is buildable. The crux is the equivalence principle (many bodies
  fall alike → geometry beats force on description length); judge by curvature INVARIANTS
  not metric numbers (gauge freedom). Novel angle: let the minus sign EMERGE; make
  geometry-vs-force compete. Concrete 2+1 experiment inside.
- `nn_and_spacetime.md` — side-exploration connecting neural networks to spacetime
  physics. Honest map: the metric tensor is the shared object (Fisher/natural gradient =
  GR's g); hyperbolic/Lorentz-model embeddings use the real SO(n,1); PINNs; Hashimoto's
  depth-as-emergent-dimension (holography in ML); five category errors corrected; six
  buildable toys (the Huygens-tail PINN validates dimensional_ladder §5). Confidence-tagged.
- `dimensional_ladder.md` *(also in ../BlackHole — shared)* — 1+1 rung, scaling laws
  across dimensions, shapes & measures staircase, black-hole horizons across the ladder,
  4+1 extrapolation + invented vocabulary, the bridge to curvature/gravity.
- `emergent_dimension.md` *(also in ../BlackHole — shared)* — "is the extra dimension
  real?" CS-first intuition ladder (mipmap→RG→AdS/CFT→entanglement→Hashimoto), the
  three-way contrast (holographic-emergent · Kaluza–Klein → EM · GR curvature, Theorema
  Egregium). Frames both finales. Ties S=A/4 back to the black-hole chat.
- `3plus1_vs_2plus1.md` *(also in ../BlackHole — shared)* — detailed comparison of our
  world vs Flatland.
- `writeups/emergent_geometry.md` — the polished four-phase curvature story (shareable).
- `writeups/curvature_field_guide.md` — workshop-version history of all curvature phases.
- `writeups/legibility_law.md` — the crystallized standalone result: the 3-part legibility
  law (amortize→legible · generic evolution→scrambles · structure→restores), the project's
  most novel finding and its self-explanation.
- `writeups/representability_frontier.md` — ② the theory of the discoverable: the 5-cell
  taxonomy of why discovery succeeds/fails (EMIT · CERTIFY-NO-CODE/chaos · CERTIFY-GAUGE ·
  CERTIFY-CONTEXTUAL · PARTIAL-LEGIBLE), made into ONE diagnostic (script 143) that routes by
  data type and emits all five verdicts. Unifies the impossibility certificates + the gauge/
  no-fixed-reference walls + the legibility law into one predictive instrument.

## Accessibility note (important)
The user flagged that some responses got "very very technical." Lead with plain-language
CS framings and concrete analogies; put precise/math content second and clearly optional.
He is driving the ideas — reflect his idea back accurately before extending it.

## Context the user brought in
The user arrived here from a deep black-hole chat (notes from a Brian Cox talk): the
information paradox, complementarity, holographic principle, Bekenstein–Hawking entropy
S = A/4, the M² entropy law, Planck-area tiles, and spaghettification geometry
(stretch-one / squeeze-two, traceless; singularity is a *time* not a *place* inside).
He's a **computer engineer** — CS framings (bits, encoding, hashing) land well. The
horizon-measure section of `dimensional_ladder.md` deliberately generalizes that
black-hole material across dimensions.

## Sibling repo: `../BlackHole/` (the LIGO-data projects, moved out 2026-06-13)
The black-hole data-analysis projects now live in `../BlackHole/` with their own
CLAUDE.md, verify.sh, and the shared concept docs: **`echoes/`** (post-merger GW
echo search, v5 complete — production-path ML edge ≈1.2×), **`ringdown_spectroscopy/`**
(no-hair test via amortized SBI, v3 complete — calibration-certified), and
**`primordial_blackhole_search/`** (subsolar-mass merger ML search, v1 complete —
41–45% of ideal-MF sensitive distance). All are PARKED complete arcs (green gates,
shelf lists in their lab notebooks). The `ai-coding-standards` skill is copied there
too. Revisit only when curvature is mined out (FOCUS DIRECTIVE below).

## Sub-project: `curvature/` (active build — THE main thread, the whole repo now)
The user's core ambition made executable (see `discovering_curvature_with_nn.md`):
networks trained only on adjacent observable tasks, tested for whether geometry
emerges. **Phase A COMPLETE (2026-06-11), all gates passed first attempt:** a tiny
Siamese MLP (2→64→64→K, tanh, strict distance head, BCE) trained only on "same
event seen by two boosted observers?" with raw (t,x) inputs INVENTED the Minkowski
interval: K=1 saturates (99.91%), G1 isotonic R²=1.0000, G2 gradient alignment
|cos|=1.0000 with the (+,−) sign pattern (minus sign EARNED), G3 Euclidean control
0.43, G4 level sets = hyperbolas. Bonus: K=2/4 nets left extra latents empty
(PCA evr [1,0,0,0]) — emergent minimality from the strict head. G0 honesty checks
(oracle 0.99 / linear 0.52 / leak 0.49) ran BEFORE training. Replicates Wetzel
PRR 2, 033499 with stronger gates. Decisions table in `curvature/README.md`;
results in `curvature/notes/lab_notebook.md`.
- Environment: `curvature/.venv` (python3.12, torch 2.12 CPU, sklearn 1.9).
- **v0.1 COMPLETE (2026-06-11):** all four causal sectors; K=1 still saturates
  (0.993 — counting measures continuous dims, not bits; my "knee→2" prediction
  was corrected BEFORE running, recorded); per-sector R²≥0.9997; net chose
  disjoint branch ranges — **the light cone emerges as the discontinuities of
  the latent** (results/04_gates_mixed_k1.png).
- **Phase B COMPLETE (2026-06-11), all pre-registered gates passed:** static
  weak well ds²=(1+2φ)dt²−(1−2φ)dx² (convention verified), observations =
  (anchor x, COORDINATE components), pairs share anchor. Results: position-blind
  control 0.9054 vs position-aware 0.9983 (the well is behaviorally real);
  ratio readout −(∂f/∂Δt/∂f/∂Δx)(Δx/Δt)=A/B (per-position reshaping h_x
  CANCELS) traces the well at r=0.9995, depth ~2% (05_gates_well_k1.png);
  per-bin isotonic R²≥0.975. **"The interval bends" — demonstrated.** Caveats:
  toy 1+1 data-generator metric (not Einstein dynamics); only A/B recoverable
  per position by construction — separating A,B needs cross-position data =
  Phase C (geometry-vs-force economy race, trajectories of many bodies).
- **Phase C COMPLETE (2026-06-11), the economy race:** geometry model (identity-
  blind MLP) vs force model (per-body embedding), identical data/budget, slow-
  motion trajectories (generator = exact Newtonian gravity; G0 gap 0.182 vs full
  geodesics INVESTIGATED via scaling probe → real PN physics, not a bug —
  shrinks to 0.0006 at depth 0.01/v 0.05). Neutral mix: tie (4.7e-6 vs 6.2e-6),
  swap test harmless, zero-shot works — identity buys nothing under gravity.
  Charged mix: geometry fails 88× on charged bodies only (0.0853 vs 0.00097),
  swap test catastrophic (1700×), and the embeddings encode EXACTLY one number
  per body — q/m — via behavioral decode r=0.9999 after PCA (r=−0.12) and
  linear probes (r=0.02) both failed (probe-ladder lesson: variance ✗ →
  linear ✗ → behavioral ✓; info present+used but stored non-linearly).
  **Headline: gravity costs 0 numbers/body, EM exactly 1 — why geometry absorbs
  gravity and not EM, replayed in a trainable system.** Pre-registration
  corrections recorded openly (C3 "collapse"→swap-test; C8 PCA→behavioral).
- **3+1 replication COMPLETE (2026-06-11):** R1-R5 all pass — K=1 saturates
  (0.9970), isotonic R²=0.9997, alignment 1.0000 with (+,−,−,−) sign pattern
  (three minus signs earned), Euclidean control 0.42, slice level sets on the
  hyperbolas. Phase A is dimension-robust.
- **Write-up COMPLETE:** `writeups/emergent_geometry.md` — the four-phase story,
  shareable. Update it when new phases land.
- **SAE/steering side quest COMPLETE (2026-06-11):** S1 ✓✓ linearization-with-
  depth (q/m decode: embedding 0.02 → hidden layers 0.98, held-out bodies);
  S2 ✗ honest negative (tuned SAE: best feature |r|=0.72 vs qm, 0.78 vs qm·E —
  distributed, not monosemantic; hint it stores the used PRODUCT); S3 ✓ causal
  steering at layer-1 sweeps a neutral body's effective charge across the full
  physical range (corr 0.9987, on-manifold residual 3× better than random);
  S4 ⚠ lesson: in small smooth nets random directions also steer monotonically
  — specificity claims need equal-norm controls on span AND on-manifold-ness.
  Scripts: 09_sae_steering.py.
- **MDL race COMPLETE (2026-06-11):** charged mix → MDL minimum at EXACTLY
  d=1 per-body code (5,320 bits vs 14,696 geometry-only / 6,028 d=4).
  Quantitative punchline via the quantization probe: **identity is worth 0.44
  bits/body under gravity, 9.86 bits/body with EM.** Honest corrections: (M1)
  neutral-mix MDL minimum unresolvable at this convergence (data-term variance
  swamps param term; multi-seed averaging queued); (M3) the 1-d code is
  sufficient but NOT monotone (spearman 0.30) — "bottleneck ⇒ interpretable" is
  false; legibility must be selected for. Reproducibility bug found & fixed:
  torch inits were unseeded (models constructed before train() seeds) — 06/10
  now seed before construction. Scripts: 10_mdl.py.
- **Metric-component experiment COMPLETE (2026-06-11):** 2+1 ANISOTROPIC well
  (A,B,C,D from 3 independent fields). N3 ✓✓ headline: the FULL anisotropic
  local metric (incl. shear D) read out anchor-by-anchor from gradients at
  median |cos|=1.0000 (every anchor >0.9997) — the entire 4-component metric
  field reconstructed. N2 ✓ (R²=1.0000), N4 ✓ (d=0 worst, 0.92). N1 ✗ for a
  DEEP reason: knee at d=2 not 3 — position is itself a 2-d sufficient code;
  **you cannot count field components by bottlenecking the ADDRESS** (it
  measures min(base-dim, form-dof)). Corrected design queued: set-encoder /
  in-context — random forms per episode, bottleneck must carry the FORM;
  knee should land at form dof (3 in 2+1, 5 in 3+1 up to scale).
- **Form-counting arc (2026-06-12, in progress):** 12 (raw set encoder) FLAT
  at 0.904 all d → 12b diagnosis: oracle 0.992, k-sweep crawls (0.929 @k=128)
  ⇒ mean-pool encoder can't invert quadratic constraints → 12c (quad item
  features) better (0.95 @d=4) but G1 ✗; step-up at d=4 not 3 = the projective
  smear predicted by the SECOND-OPINION SESSION (user relays peer review from a
  parallel Claude session — incorporate such input, credit it). 12d running:
  pool the exact sufficient statistic Σuuᵀ (peer-suggested decisive test);
  stopping rule pre-registered — if d≥4 < 0.97, park counting with honest
  verdict and advance to Phase D.
- **PHASE D COMPLETE (2026-06-12) — THE KALUZA MOVE REDISCOVERED, all gates:**
  shared identity-blind one-step dynamics on extended state (x, v, w); bodies
  differ only in learned initial w₀. D1 fit 4.64e-5 ✓; **D2 behavioral decode
  of w₀ vs q/m r = +0.9998** ✓✓ (charge became an internal coordinate of a
  shared geometry — identity migrated from model parameters to STATE); D3
  approximate conservation (drift 13% of spread — rough isometry, partial);
  D4 zero-shot: new body's charge fit from ONE point, no weight updates ✓.
  Counting question PARKED (12d: even exact sufficient statistic leaves ~5%
  readout gap — knee-counting needs near-oracle inference; honest verdict in
  notebook). Multi-seed MDL (13): charged min at d=1 decisive (+8,870±15 bits
  for d=0); neutral ordering restored (d=0 min) at marginal significance.
  D-v2 queued: extended-Lagrangian form, ∂L/∂ẇ conserved-momentum test.
- **Dashboard (2026-06-12):** repo-root dashboard.html + curvlib.progress()
  heartbeats (wired into 02/06/14 train loops; call in any new long loop).
  Serve: `./start_dashboard.sh` (kills any stale server, always roots at the
  repo — added after a wrong-cwd restart served 404s) →
  http://localhost:8788/dashboard.html.
- Writeup v2 DONE (five acts incl. Kaluza ending; user will polish weekends).
- **D-v2 (2026-06-12): first run = honest negative with a deep lesson —
  ECONOMY DOES NOT SELECT GAUGE.** Generic extended Lagrangian fits (3.15e-5 ✓)
  but uses w as a label channel (cyclicity 0.94 ✗, corr(p_w, q/m) −0.26 ✗):
  the KK form is one gauge choice in a large equivalence class; nothing in the
  loss prefers it (v1's behavioral gates were gauge-robust, v2's structural
  gates gauge-fixed — both correct). Fix round (--cyclic) FAILED on numerics
  (EL rollout stiffness; loss 0.07→50→3.6 oscillation; test MSE 79).
  **D-v2 CLOSED per one-fix-round rule: KK structure unverified-not-refuted;
  Phase D stands on v1's behavioral r=0.9998.** Future shelf: stabilized LNN /
  Hamiltonian parameterization. Same villain as Phase B reshaping + MDL
  lookup codes: gauge freedom is the project's recurring lesson.
- **User-approved sequence: D-v2 → echoes v2 → ringdown v2 → frontier — all
  reached.** Echoes v2+v3 done (see echoes block); ringdown v2 done + fix round
  running (see ringdown block).
- **D-3 MAGNETIC KALUZA (2026-06-13): M2 ✓✓ r = +0.9974** — v×B forces
  geometrize into the internal coordinate; control fails 23× on charged.
  KK suite complete (electric D-v1 + magnetic D-3). M1 marginal (1.07e-4 vs
  1e-4 guess-gate, recorded; no fix round spent). Script: 18_magnetic_kaluza.py.
- **PHASE E (2026-06-12, overnight, the frontier pick): the metric FIELD from
  trajectories — E1/E2/E4 ✓✓.** Held-out MSE 5e-6; field recovery cos = 1.0000
  after ONE global scale; φ corr 0.9997; **shear D̂ r = 0.9989 — the component
  Phase B provably could not see, now measured from cross-position dynamics
  (Phase B caveat RESOLVED).** Model: declared-bias mass-matrix mechanics
  (L = ½q̇ᵀS(q)q̇ − φ), Cholesky-SPD field nets, closed-form EOM — the D-v2
  numerical trap avoided by construction; training stable. **E3 ✓ (control
  1700× worse: 8.74e-3 vs 5e-6) — ALL FOUR GATES PASSED, PHASE E COMPLETE.**
  Script: 16_field_from_trajectories.py (allow_unused autograd fix recorded).
- **CURVATURE INVARIANT (2026-06-13) — ALL GATES, the closing readout:**
  Gaussian curvature of the learned Phase E geometry via double-autodiff
  (Brioschi; calculator validated exactly on a 2-sphere): **corr(K̂, K_true)
  = 0.9903**, magnitude 0.157, far-field exact match. Script:
  17_curvature_invariant.py. 16 now saves weights (16_field_model.pt).
  The project's title question closed in coordinate-free currency.
- **PHASE F (2026-06-12) — THE LAW ITSELF, honest NULL (1/4 gates):** learn the
  MAPPING matter→acceleration-field (random 1–2 blob worlds → CNN field →
  differentiable rollout, trajectories-only). Results (19_law.json): F1 traj MSE
  0.058 (gate ≤1e-3, FAIL 58×); F2 field cos 0.937 (>0.98, FAIL); F3 superposition
  cos 0.965 (>0.96, **PASS** — direction-linearity DID emerge on unseen 3-blob
  worlds) but F3 MSE 2.65× F1 (FAIL); F4 blind 6.4× F1 (≥10×, FAIL). The predicted
  local-CNN-vs-1/r-long-range miss. A parallel Gemini session mis-reported this as
  "flying colors" (cherry-picked F3 cos) — corrected. Stale results/19_ckpt.pt
  renamed → 19_ckpt_v1_failed.pt (silent-resume trap defused). **F-v2 pre-reg owed:
  oracle discretization floor FIRST, 3-pt LR sweep, diagnostic trio, THEN
  receptive-field fix** (ai-coding-standards SKILL "ML experiment methodology",
  adopted after this). NOT in verify.sh (a null, no saved-gate to assert).
  **Next-steps decision tree: `curvature/notes/fv2_roadmap.md`** (executable cold
  without chat context). Autonomous diagnostics: `scripts/22_fv2_diagnostics.py`
  (oracle floor 1.2e-4 already banked ⇒ Phase F gate WAS feasible; arms run to
  results/22_fv2_diag.json, dashboard 22_*, no Claude in the loop).
- **PHASE F CLOSED (2026-06-14):** diagnostics → overfit-one-batch FAILS at
  0.047 (representational wall); RF sweep (one knob, MPS, clean) → F2 climbs
  0.852→0.985 over reach 17→53px (locality confirmed) then d=8 collapses
  (extreme-dilation gridding, recorded); RF1 fails-as-pre-registered, RF2
  fails (magnitude needs global operators = known FNO-class result).
  **F-v3 deliberately skipped** — superseded by the user's redirect.
- **INFRA (2026-06-14):** bit-exact checkpoints (curvlib save_ckpt/load_ckpt:
  RNG state + atomic writes; proven bitwise); detached launches for long runs
  (session restarts were killing harness children — 5 deaths diagnosed);
  curvlib.bilerp (MPS twin of trilerp, verified exact) → **MPS 12.4×**;
  ./start_dashboard.sh.
- **NEXT ARC (user redirect 2026-06-14): PHASE G (generalist — one net, all
  world families; the PRIZE = structure of its internal world-summary space)
  then PHASE H (geometrization survey — which particle-like labels become
  hidden lanes: two-charge → lane counting; Wong color charge → rotating
  label, the crown; friction → predicted failure boundary; equivalence-
  breaking gravity → open). Design doc AWAITING JOINT REVIEW:
  `curvature/notes/phase_g_design.md`. L4 GPU arrives ~1-2 days, sized for G.
  Do NOT start the big G build before the user reviews the design.
- **3+1 LAW (2026-06-12, script 21, run 21_law_3p1):** Gemini scaled Phase F to
  24³ voxels (nn.Conv3d, 3D rollout), batch 192→48 for 15× CPU speedup. Doubles as
  a locality probe (larger relative receptive field). MPS enabled via trilerp()
  rewrite + --device flag (3D grid_sample backward unimplemented on MPS,
  pytorch#141287; CPU path verified byte-identical, resume-safe). **Gates were ALREADY
  documented 2026-06-12 (lab_notebook "3+1 LAW RESULTS: failed all gates, CONFOUNDED"):
  F1 0.041, F2 0.417, F3 0.685/0.112, F4 0.141 — failed all gates. CRUCIAL CAVEAT (from
  that entry): the run is CONFOUNDED vs 2+1 — it changed three things at once (kernels
  5²→3³, channels 16/32→8/16, 6× fewer training samples), so the F2 0.417≪0.937 gap is
  NOT a clean "locality worse in 3D" claim. (2026-06-26: only the stale "Gates pending"
  status line above was corrected; the result itself was not new.)**
- **FNO GRID SWEEP — pre-registered pending result FILLED IN (2026-06-26).** The FNO
  grid-resolution sweep was launched + PRE-REGISTERED 2026-06-20 (lab_notebook: "results
  to be documented when the 6 arms finish"; pre-reg conclusion: "if F1 still ~0.015 at
  grid 96, the gap is not resolution → honest null, bank the FNO architecture win"). The
  6 arms finished Jun 19 but the numbers were never pulled back — now filled in: grids
  64/96 (3 seeds each) F1 = 0.0141–0.0169, ~0.015 same as the 48-grid modes sweep, F2_cos
  ~0.995. So the pre-registered honest-null holds: F1 is NOT resolution-limited; the FNO
  resolves Phase-F locality/F2 (F2 0.995 vs CNN 0.937; P0 3.7e-6 on Mac) but the absolute
  F1 trajectory gate (1e-3) is bounded ~0.015 by a non-resolution factor. Results
  results/100_fno_law_{g64,g96}_s*. Not in verify.sh (GPU-only).
- **REGRESSION GATE (2026-06-13): `./verify.sh` at SpaceTime root — curvature
  only now.** Re-runs all six curvature probe batteries against saved models
  (Phase A, v0.1, B, C, 3+1, E+curvature; thresholds = the pre-registered
  gates; curvature/verify.sh + scripts/verify_gates.py) plus the 17/18
  invariant+magnetic artifacts. (echoes+ringdown asserts moved to
  `../BlackHole/verify.sh`.) **Run it after any curvature change; a result
  isn't real until the gate is green.**
- **PHASE H ROW 1 — two-charge lanes (24/24b/24c) CLOSED:** knee exactly at L=2;
  H3 behavioral decode r=0.9996/0.9998 both charges; H4 zero-shot from ~4
  trajectories (k=1 fails by identifiability — recorded).
- **PHASE G — the generalist (scripts 25 worldgen / 26 transformer, 2.01M):**
  data-scaling curve (24k/60k/120k episodes) SCALES monotonically (no plateau),
  but the charge-gated traj families sit ~300× above the two-charge specialist
  floor (1.2e-4) → the wall is ARCHITECTURE (the single global mean-pool), not
  data. **G2 zero-shot PASS** (+25% wider worlds, traj ratio 1.0). **G3 prize —
  the world-summary space (script 27):** G3a families cluster (ARI 0.82, the PCA
  map reads as a physics taxonomy); **G3c EM-kinship** chargedE↔magneticB sit 2×
  closer to each other than to gravity (z=27) — the net carved "force gated by a
  per-body charge" as its own region of law-space (ties to It-from-Qubit).
- **PHASE G-sym — symmetry-respecting generalist (script 28, frame from a
  parallel Claude session, credited):** the mean-pool is body-relabeling
  INVARIANCE (equivalence principle in disguise) — keeps body-symmetric info
  (geometry), drops the tag→charge binding. Fix = invariant stage pool +
  EQUIVARIANT per-body cross-attention channel. After catching a degenerate-tag
  confound + a STALE-DATA trap (merged old shards — "file exists ≠ fresh"; both
  logged), clean run: **A1 accuracy restored** (chargedE 14×, twocharge 11.5×),
  per-body charge decodes from the equivariant channel (chargedE 0.91), **but a
  real ACCURACY↔LEGIBILITY tension** — stage clustering drops 0.82→0.69 as
  per-body info migrates out. magneticB a consistent special case (v×B
  velocity-gated).
- **PHASE I — consensus→legibility (script 29), THE session's law:** tested
  "agreement/recurrence selects legibility" with a discreteness control (3
  seeds). Recurrence (−0.004) and discreteness (−0.005) do NOTHING; **amortize-
  vs-free-embedding (+0.466) is the whole effect. Legibility is selected by
  AMORTIZATION, not agreement:** a code a shared encoder INFERS is linearly
  legible for free (r~0.97); a free per-body parameter scrambles (linear 0.50,
  info in nonlinear 0.86). The Phase C illegible q/m code was a FREE-PARAMETER
  artifact. Consensus bet (parallel session) falsified; their question was right.
- **LEGIBILITY LAW → SAE MONOSEMANTICITY (script 139, 2026-06-27) — the bridge to mech-interp, direction ①.**
  Connects the crown jewel to sparse autoencoders (the tool that finds monosemantic features by resolving
  superposition). Script 09 did the FREE half (force-model q/m → SAE best feature |r|=0.72, distributed); 139 completes
  it in one controlled harness: a scalar property stored AMORTIZED (encoder infers) vs FREE (per-item embedding), then an
  L1-SAE on the code. 4/4 (after honest iteration): amortized linear-legible (0.99) + MONOSEMANTIC (p from ~2 SAE
  features, mono-ratio top2/full 0.96); free SCRAMBLED (linear 0.46 / nonlinear 0.78) + SUPERPOSED (top-2 0.29 ≪ full
  0.71, mono-ratio 0.41). The mono-ratio GAP 0.55 (decisive metric) tracks legibility. **NOVEL: amortization-vs-free
  storage is a CONTROLLABLE cause of superposition** (standard story = underparameterization+sparsity; web-verified
  Cunningham 2309.08600 + Anthropic Scaling Monosemanticity) — links the amortization-gap/identifiability literature
  (Roeder, O'Neill) to SAE/superposition. Iteration (honest): no base term + FRESH queries (free can't memorize) +
  strong coupling + top-2-decode metric (robust to ReLU ±-split of signed p). Caveat: free is a moderately-lossy
  nonlinear store (0.78/0.71) → "info present" bar 0.8→0.7; the robust finding is the mono-ratio gap. In verify.sh.
  ① done (139+140). **② REPRESENTABILITY FRONTIER STARTED (notes/representability_frontier.md + script 141, 2026-06-27):**
  a theory of the discoverable — the project's scattered limits-of-discovery as a 5-cell taxonomy (EMIT / CERTIFY-CHAOS /
  CERTIFY-GAUGE / CERTIFY-CONTEXTUAL / PARTIAL-LEGIBLE) under one lens ("the cheapest legible code" fails to exist/be
  unique/be consistent/be linear), toward a predictive DISCOVERABILITY DIAGNOSTIC. **EXP-1 (141, 4/4):** ONE diagnostic
  on a distance-geometry menu (reuses dS-anchor 111) names THREE verdicts — EMIT (2D config + anchor: stress 0, raw 0,
  unique) / CERTIFY-GAUGE (relational: shape recovers, raw frame 1.42 = gauge) / CERTIFY-NO-CODE (6D config: stress 1.29,
  no cheap 2D code). Read STRESS (cheap code exists?) then RAW frame error (unique or gauge?). In verify.sh. Roadmap:
  **EXP-2 (142, 3/3):** CERTIFY-CONTEXTUAL on correlation-table data — fit the cheapest local-hidden-variable code
  (simplex over the 16 deterministic strategies = local polytope) + read CHSH; classical→EMIT-CLASSICAL, singlet→
  CERTIFY-CONTEXTUAL (CHSH 2.83>2 = Bell), and a Werner sweep LOCATES the wall at v=0.725~1/√2. 4/5 verdicts done.
  **EXP-3 (143 + writeup, complete):** PARTIAL-LEGIBLE (the 5th verdict, free code linear 0.45 / nonlinear 0.75) +
  the UNIFIED diagnostic -- one instrument routes by data type and emits all 5 verdicts on a 7-case menu. ② FIRST ARC
  COMPLETE (framework + EXP-1/2/3 + writeups/representability_frontier.md). 143 not in verify.sh (redundant train; the 5
  verdicts gated by 139/141/142). **EXP-4 (145, 2026-07-02, 9/9): the REGIME DETECTOR — the honest-scope gap closed.**
  Label-free + truth-free: infers the data type from structural signatures (triangle-inequality→distances; discrete ±1
  records→correlations; temporal smoothness→trajectories; exchangeable tabular→code), then decides the regime truth-free
  (gauge = two rigid-motion configs explain the data equally unless anchor DATA breaks it; contextual = samples' own
  CHSH; legible = decode own target). NEW trajectory branch folds CHAOS-proper into the router: web-verified
  Gottwald-Melbourne 0-1 test + §99 engine — Kepler EMIT (K=-0.06, invariant 7e-18 machine-exact), Lorenz CERTIFY-CHAOS
  (K=0.997). Gotcha (smoke-caught): oversampled chaos reads K~0 → K = max over subsample rates. Truth only in gates.
  In verify.sh (45s). The table is now a DETECTOR. **EXP-5 (146, 2026-07-02): the sixth-wall hunt -- no 6th cell, but the table is ONE FACE of a 3-axis space.** Threw 3 adversarial non-taxonomy systems at the detector: partial observability is ABSORBED (Takens; scalar-only 0-1 test gives right verdict, Kepler K=-0.06/Lorenz K=0.998); computational irreducibility is a GENUINE MISFIT on an orthogonal PREDICTABILITY axis (Rules 30/90/250 all EMIT the one-step law yet split on compressibility -- Rule30 incompressible, Rule250 compressible; Rule90 nuance: algebraically reducible yet zlib-incompressible = statistical vs algorithmic predictability); finite-sample is an orthogonal UNDERDETERMINATION axis that bites NEAR a wall (near-boundary Werner 65% correct at N=16 vs 100% at N=200k -> needs ABSTAIN). So the frontier = DISCOVERABILITY (the 5-cell table) x PREDICTABILITY x SAMPLING. In verify.sh. **EXP-6 (147): ABSTAIN-aware detector** (bootstrap CI per branch → abstains when the CI straddles the threshold / below a sample floor; A1 confident-correct, A2 zero-wrong-verdicts on underdetermined inputs, A3 resolves with data). **EXP-7 (148): LAW-learnability vs TRAJECTORY-predictability DISSOCIATE** — all structured systems have a learnable one-step law (Kepler/Lorenz R²=1, Rule 30/250 acc=1) but predictability splits (Lorenz/Rule 30 = learnable rule, unpredictable trajectory); the 5-cell frontier measures trajectory-level structure, not the local rule. Both in verify.sh. **EXP-8 (149): mixed-regime robustness** — a KAM phase space (Hénon-Heiles) needs a FRACTION readout, not one label (λ-bimodal at E=1/8, fraction tracks KAM); the 0-1 test's quasiperiodic false-positives are an under-sampling artifact (ties EXP-6). **EXP-9 (150): the unified ROBUST detector** — folds detector+abstain+mixture into ONE data-driven instrument (verdict | ABSTAIN | MIXTURE-fraction), 9/9, zero wrong confident verdicts. Autonomous arc EXP-4..9 (scripts 145-150) all in verify.sh.
- **LEGIBILITY LAW — CROSS-SESSION VALIDATION (2026-06-22/23, writeups/legibility_law.md):**
  three parallel projects pressure-tested the law and each corrected the others
  (adversarial peer review, not echo). **Phronesis (real 4B LLM):** refuted our
  "redundancy explains weak steering" cross-claim → the LLM mechanism is
  read-direction≠write-direction (cos 0.34); calibrated two of our overshoots
  (cosine must stay qualitative; up/down asymmetry was a baseline confound,
  withdrawn). Our reciprocal toy test (102) reproduced read≠write functionally;
  settled joint statement recorded. **AlphaLudo (game-RL):** third domain;
  positive control reproduced our 0.22; identity-only free code stays legible
  (boundary: scramble needs free-STORAGE of a multi-D property). **Owed re-test
  (104/105):** generic coupling scrambles free D=1 (confirmed in the validated
  harness; toy 103 was too easy and failed), but "linear coupling rescues D=1" is
  FRAGILE/task-specific (legible in physics-trajectory harness 48, scrambled in
  abstract-scalar 104; capacity hypothesis refuted by 105). **Robust core (all 3
  domains): amortized→legible; free+multi-D→scramble; free+generic→scrambles even
  at D=1. The D=1-legible boundary is fragile, not universal.** Cited O'Neill
  amortisation-gap (arXiv:2411.13117). verify.sh ALL GREEN incl. J5+CertV.
- **1-D MYSTERY CRACKED — free→scramble driver = the TARGET FUNCTION (scripts
  107-109, 2026-06-23).** Process of elimination on "why same linear coupling →
  D=1 legible in physics-traj (48, 0.86) but scrambled in abstract-scalar (104,
  0.23)": output richness REFUTED (107, legible at every OUT), capacity REFUTED
  (105), batching regime REFUTED (108). DECISIVE (109): swap ONLY the world at
  identical learner → s35's default-init MLP world SCRAMBLES the free code
  (0.247) while a large-weight world stays LEGIBLE (0.78). So free→scramble is
  driven by the TARGET / observation structure (plausibly the property's
  signal-strength), NOT output/capacity/batching. **Honest bound: free→scramble
  is target-conditional, not universal** (my fresh harnesses 103/107/108 never
  scrambled = "easy" targets; Phronesis/AlphaLudo matched s35 because they copied
  its TARGET). Robust theorem-backed direction stays amortize→legible (Roeder).
  **MECHANISM CONFIRMED (110): the knob is the property's SIGNAL STRENGTH in the
  observations** — scaling ONLY p's effect (y=base(x)+α·p·coup(x), base frozen)
  makes free D=1 legibility climb monotonically 0.21→0.58→0.87→0.89 as α goes
  0.05→0.15→0.4→1.0 (saturates ~0.4). Weak signal → scramble; strong → legible.
  **4TH-DOMAIN EASY-TARGET CONFIRMATION (133, 2026-06-26, communication-game-for-
  gauge):** the amortized-protocol reframe — a 2-agent Lewis referential game (speaker
  sees D=3 props → message; listener picks target among distractors). Amortized protocol
  legible (linear R² 0.998, robust half transfers to emergent comms), but free→scramble
  did NOT reproduce (free legible 0.986). Fix round added an ungrounded reconstruction
  contrast to test "grounding legibilizes" → REFUTED (recon-free legible 0.994 too). So
  this comms task is a 4th easy target (after 103/107/108): free storage of a multi-D
  property is NECESSARY but NOT SUFFICIENT to scramble (sharpens AlphaLudo's boundary).
  Honest null, NOT in verify.sh (the pre-registered scramble failed). Robust amortize→
  legible stands.
- **PHASE H ROW 2 — Wong color charge (scripts 30/30b/31), CLOSED, honest
  boundary:** classical SU(2) charge that parallel-transports (rotates, |Q|
  conserved; web-verified Wong 1970). v1 negative (confounded: 12° precession +
  free embedding + n=32). v2 (amortized code + ×6 field → 90° + n=200) + fix:
  **W3b ✓✓ amortization legibilizes the STATIC charge** Q0 (linear 0.79–0.92 vs
  v1 ~0 — Phase I cross-validated), **but the ROTATING Q(t) is tracked only
  NONLINEARLY** (linear 0.29–0.46 / nonlinear 0.66–0.76) and **|Q| not conserved**
  (drift 0.47). **Refinement of Phase I: amortization buys legibility for STATIC
  codes; a DYNAMIC conserved quantity needs an invariant-preserving update — a
  generic recurrent F re-scrambles the clean w0 as it evolves.** Survey boundary:
  static labels geometrize (electric, color Q0); the dynamic rotation does not.
- **PHASE J — geometry from entanglement (script 32), the big swing, loop closed:**
  free-fermion ground states (Peschel method, web-verified) -> learn geometry from the
  mutual-information table alone. J0 floor ✓ (c=0.97 vs CFT c=1). **J1 chain ✓ isotonic
  0.971** — block-MI embedding recovers the 1D order, positions never given (geometry FROM
  entanglement). **J3 Van Raamsdonk pinch-off ✓** — decoupling two halves (cross-MI->0)
  flings them 6.4x apart in the emergent geometry. Gotcha: half-filled single-site MI is
  parity-pathological (even-sep correlations vanish) -> use region/block MI (why RT uses
  regions). Honest gaps: J2 dimension (curved-manifold PCA overcounts) + 2D grid (needs
  spectral embedding). Premise demonstrated; J4 hyperbolic-curvature + spectral 2D open.
- **J4 HYPERBOLIC / AdS payoff DONE (2026-06-16, script 41):** is the emergent radial/scale
  dimension negatively curved (AdS), and only at criticality? Web-verified Calabrese-Cardy +
  Ryu-Takayanagi: critical S(l)=(c/3)ln[(n/π)sin(πl/n)] IS a boundary-anchored geodesic length in
  a negatively-curved AdS2 bulk (flat bulk -> S~l linear). **J4a ✓✓ c_fit=1.001, R²_log=1.0000**
  (the RT log-law exactly); **J4b ✓✓** gapped (staggered mass) saturates, large-l slope 0.000 vs
  critical 0.333 — the hyperbolic dimension exists ONLY at criticality. J4c FAIL = a weak instrument
  (log-vs-linear R²-margin 0.239<0.3 because a line approximates a gentle log over a monotone range;
  R²_log=1.0000 already proves the form; one fix round spent, gate not moved). **Verdict: hyperbolic/
  AdS emergent dimension CONFIRMED on J4a+J4b** — holography's extra dimension is real, emergent from
  entanglement, negatively curved (ties It-from-Qubit to emergent_dimension.md).
- **J5 CURVATURE FROM ENTANGLEMENT DONE (2026-06-22, script 42) — the deferred Brioschi K-map, all
  3 gates.** The emergence arc's coordinate-free close: build a 2D curved geometry from a chain's
  entanglement ALONE and MEASURE its Gaussian curvature with the script-17 Brioschi calculator.
  Research-first cracked the "fragile, deferred" flag: the naive MI-embedding fails for free fermions
  (exponentially small far-region MI, arXiv:1508.00766) — use kinematic space from SINGLE-INTERVAL S
  instead (Czech-Lamprou-McCandlish-Sully 2015, arXiv:1505.05515): metric ds²=(∂²S/∂u∂v)du dv, nothing
  geometric assumed. **E0 ✓** calculator self-calibrates on analytic c=1 (Brioschi K=12 constant). **E1
  ✓✓** critical chain → CONSTANT curvature (R-CoV 0.001), central charge read OFF the curvature
  c=1.000 (robust across N=256/384/512 and 4 bands; cross-checks J4 via a different route); Brioschi
  K=12.0 constant. **E2 ✓** gapped → metric degenerates (collapses 4000×), constant curvature only at
  criticality. Honest scope: the full 4th-derivative Brioschi on raw free-fermion S is noise-swamped
  (CoV 1.4, the predicted "quantum bulk") → curvature measured via the robust 2nd-derivative metric,
  Brioschi on the clean measured metric for the invariant value. The constancy is tightly linked to
  J4's log-law (it follows from it); the NEW content = the explicit 2D kinematic geometry (dS₂,
  constant POSITIVE curvature — the integral-geometry dual of the AdS bulk, NOT literally the AdS
  bulk) + measured Brioschi invariant + c-from-curvature + the gapped degeneration. One fix round
  (4th-deriv noise → 2nd-deriv metric). **Emergence arc: entanglement → metric → curvature, no
  geometry put in by hand.**
- **THE SESSION SYNTHESIS (the legibility law):** amortize → legible (static);
  evolve through a generic net → re-scrambled (dynamic). **Open thread RESOLVED
  (Wong v3, script 106, 2026-06-23) — honest PARTIAL:** an orthogonal SO(3)
  update in the REAL Wong physics conserves |Q| EXACTLY (drift 2.7e-7 vs generic
  0.47) and roughly doubles legibility of the rotating charge (linear 0.29 →
  0.56-0.64, nonlinear 0.71) BUT does not reach the static ceiling (0.89) / the
  0.70 gate; one fix round (richer rotation generator, leg-3's lever) did NOT
  help → it's a PARTIAL-OBSERVABILITY ceiling (trajectory-only supervision sees
  the charge only via Q·E along the path). Refined lesson: structure-preserving
  updates conserve the invariant and substantially help, but FULL dynamic
  legibility ALSO needs the quantity to be OBSERVABLE — structure necessary, not
  sufficient (leg 3 hit the ceiling only because there the rotation was fully
  observable). **v4 REFUTES the partial-observability hypothesis (script 135,
  2026-06-26): observability does NOT resolve the ceiling — CLEAN negative.** K=1
  (single field) vs K=4 (four diverse color-electric probe fields, shared SO(3)
  transport). First run (matched 12000 steps): K=4 0.295 < K=1 0.376 but CONFOUNDED
  (K=4 fits 4× data at same steps, under-converged). Fix round — STEP-MATCHED per-field
  (K=4 at 4×=48000 steps): K=4 now well-converged (nonlinear decode 0.958 > K=1's 0.904,
  tracks Q(t) BETTER) YET linear decode 0.373 ≈ K=1's 0.376, nowhere near 0.70. So
  fuller observability does NOT improve LINEAR legibility — the partial-observability
  hypothesis is REFUTED, and the dynamic-legibility ceiling is a genuine REPRESENTATIONAL
  limit (the rotating charge is tracked nonlinearly, not linearly, independent of
  observability). Structure (SO(3)) conserves |Q| (1.4e-7); neither structure nor
  observability makes the dynamic rotating charge linearly legible. NOT in verify.sh
  (negative). **Survey-row status corrected
  (2026-06-23): friction is DONE (script 70 — universal but dissipative does NOT
  geometrize, geom/dissip MSE ratio 606,265× vs 0.085 for a conservative force;
  reversibility explains it), and equivalence-breaking gravity is already covered
  by the field zoo (68) + EM (Phase C): non-universal coupling → no geometry. So
  the geometrization survey is ESSENTIALLY COMPLETE: a force geometrizes ⟺
  UNIVERSAL ∧ CONSERVATIVE. Genuinely-open directions are now the frontier pokes
  (de Sitter learnability) + consolidation, not more survey rows.**
- **SCALAR FIELD = the equivalence-principle knob (2026-06-16, script 45) — 4/4
  first attempt.** New-field direction (user: extend methods, "what can we
  learn"). Scalar (spin-0) force is attractive-only (web-verified), what matters
  is ρ=s/m. 2D gravity well + scalar well scaled by per-body ρ; economy race
  (Geometry identity-blind vs Force per-body code); sweep the SPREAD of ρ
  (universality), attraction fixed. geometry/force MSE ratio = **[1.23, 4.16,
  8.88, 25.21]** across spread {0,0.4,0.8,1.6}: universal ρ GEOMETRIZES (1.23,
  cost 0), species ρ COSTS (25×, cost 1). **Universality IS the cause of
  geometrization — shown as a continuous knob; the project's thesis on trial,
  confirmed.** Code recovers ρ one-signed (decode 0.98); bonus refinement of the
  legibility law: ρ is LINEARLY legible (0.98) unlike EM's q/m (scrambled,
  Phase C) — a free code's legibility depends on how the charge couples
  (one-signed/linear stays legible; signed/nonlinear scrambles; open thread).
- **Field menu (parked, user-supplied, to extend the survey "when we hit a
  wall"):** scalar ✓done; dilaton/secondary-hair ✓done (partial: softens, no clean
  knee=1, capacity-confounded); Proca ✓done (Run 3); Yang-Mills =
  Wong dynamic (orthogonal-F v3, OPEN); Dirac/spinor (OPEN — can a net discover a
  double-cover state space? edge-of-representability).
- **OVERNIGHT EXOTIC-PHYSICS QUEUE (2026-06-16, autonomous, 4/4 done):** pointed
  "discover geometry from observation" at quantum/particle physics.
  • **Run 1 Bloch sphere (script 51) ✅** — a net INVENTS the Bloch sphere + Born
    rule from qubit measurements (sphere decode R²=1.000, |r|=1.000±0.011; Born
    gradient cos=0.998). Knee at K=3 not 2 (pre-reg corrected): the net finds the
    3-D Cartesian Bloch VECTOR (linearizes Born), not the 2-D chart — Phase-A
    minimal-linearizing-code lesson in quantum state space. The quantum Phase A.
  • **Run 2 confinement (52) ✅ 3/3** — a confining force V~|x| geometrizes when
    universal (ratio 1.06→26.78); geometrization is SHAPE-INDEPENDENT (universality
    is the whole story), generalizing the equivalence-principle knob (45).
  • **Run 3 Proca (53) ✅** (1 fix round) — locality IS the learnability knob: the
    1/r long-range TAIL needs a global RF (small-RF far-field R²=0.17 vs large-RF
    0.94 at μ=0); global R² masked it. Phase F wall isolated (FNO-class).
  • **Run 4 Berry holonomy (54) ✅ 3/3** — a net discovers the geometric phase is a
    HOLONOMY (area, path-independent): whisker-invariance Δ0.9% vs the dynamical
    length-net's 72%. Web-verified Berry = -½ solid angle. Ties quantum geometric
    phase to curvature.
  Two pre-reg deviations recorded openly (Bloch knee 2→3; Proca near→far metric).
- **GENERALIST v2 + PHASE BH + EMERGENT/EXOTIC QUEUE (2026-06-16/17):** the
  strategic pivot to ONE in-context model (script 61, ~12.7M, MPS, full physics
  span: 6 families gravity/charged/scalar/Schwarzschild/Reissner-Nordström/Bloch).
  Physics-eval harness (62) caught metric families faking low MSE (M only 2% of
  ds² var) → fixed worldgen to predict g_vv directly → decode R²→1.000. Phase BH
  (the black-hole capstone) COMPLETE 3/3 ×4: space↔time flip (60), singularity
  R~1/r³ (63), charge two-horizons + timelike singularity (64), mech-interp =
  the spacetime switch is a STEERABLE linear direction (65). Law-space (66).
  **Overnight emergent/exotic queue, autonomous, 4/4 (scripts 67-70):** entropic
  gravity (force ∝ T, vanishes at T→0 — gravity as bookkeeping); the FIELD ZOO
  (why gravity is special — geometrize is bought by UNIVERSAL coupling not
  masslessness; coupling axis decides by 2-3 orders, mass axis never flips it);
  exotic matter (wormhole throat learned from rulers needs NEGATIVE energy / NEC
  violation); the FRICTION BOUNDARY (universal yet not geometry — breaks time-
  reversal). **Crystallized: a force geometrizes ⟺ UNIVERSAL ∧ CONSERVATIVE**
  (zoo gives condition 1, friction isolates condition 2; sits atop unification 55).
- **IMPOSSIBILITY-CERTIFICATE QUINTET (2026-06-17/22, scripts 84-87, 101):** a new KIND
  of result — a net's FAILURE to find a cheap explanation, gated against a theorem,
  as a positive certificate. Bell/no-local-code (84, wall at 1/√2), chaos/no-invariant
  (85, Lorenz constancy 0.45 vs Kepler 0.00), gauge/no-unique-law (86, equivalence
  class + 1508× gauge split), KCBS/contextuality (87, wall at 2/√5). The negative
  space of the legibility law. Writeup: writeups/impossibility_certificates.md.
- **CERTIFICATE V — NO OBSERVER-INDEPENDENT TIME (2026-06-22, script 101):** the
  deepest face of the "no fixed reference" wall (the map's recurring villain under 4
  masks: problem of time / background independence / complementarity / dS observables),
  for the case of TIME. Page-Wootters universe (web-verified Page-Wootters 1983 +
  Trinity arXiv:1912.00033): history state |Ψ⟩=(1/√T)Σ_t|t⟩U_S^t|ψ0⟩, an exact
  constraint fixed point. **C1 ✓** no global time (||G|Ψ⟩-|Ψ⟩||=3e-15 timeless; system
  marginal frozen [ρ_S,H_S]=1e-16 — no clock ⇒ no dynamics); **C2 ✓** relational time
  exists (condition on the clock → learner recovers the propagator, overlap 1.0000);
  **C3 ✓** time is GAUGE (a non-uniform second clock reads the same frozen state →
  identical history, different inferred law: var A 3e-32 autonomous vs B 0.24
  non-autonomous; no preferred clock, the clock-ambiguity theorem). 5/5 seeds. Honest:
  exact-by-construction structural certificate (like the 84/87 theorem walls), not an
  empirical fit; non-relativistic regime; Kuchař relativistic subtleties out of scope.
  Also the honest answer to "is time a field/emergent" (= Page-Wootters relational
  time). Came out of the emergent-spacetime physics-discussion arc (the map's central
  wall, made a positive result).
- **DE SITTER ANCHOR — AdS-easy/dS-hard as LEARNABILITY (2026-06-23, script 111),
  3/3.** The frame-gauge companion to Cert V (which did the TIME-gauge): the map's
  "no fixed reference" wall, for SPACE/frame. A learner discovers a 2D geometry
  from relational (rigid-motion-invariant) pairwise distances, with vs without a
  boundary ANCHOR (K=4 points clamped to truth = the AdS boundary). Web-verified:
  distance-geometry is unique only up to rigid motions (arXiv:1804.04310) = the
  clean analog of "no fixed frame". Best-of-8-restarts. G1 ✓ relational SHAPE
  recovers in both (aligned err 0.00); G2 ✓ absolute FRAME recovers only WITH the
  anchor (raw err 0.000 vs 1.46); G3 ✓ no-anchor recovers shape but not frame
  (raw 1.46, varies across restarts) → data fixes geometry only up to the
  rigid-motion gauge = no observer-independent global frame (dS); the anchor (AdS)
  restores it. Restarts fix OPTIMIZATION (anchor converges) but NOT IDENTIFIABILITY
  (no-anchor stays gauge). Honest scope: toy of the ANCHOR MECHANISM, not literal
  dS holography. In verify.sh. Cert V (time, 101) + this (frame, 111) = the
  no-fixed-reference wall mapped for both axes.
- **PAGE CURVE + INFORMATION RETURN (2026-06-23, script 112), 3/3 — the map's
  LAST poke; emergent-spacetime arc COMPLETE.** The info paradox as an exact qubit
  toy (web-verified Page 1993 + Hayden-Preskill 2007) in recoverability/cheapest-
  code language. P1 ✓ Page curve: S(radiation) of a Haar pure state (N=12) rises
  then FALLS, peak at k=6=N/2, purifies to S=-0.000 (vs thermal monotone). P2 ✓
  information return: I(Ref:radiation) 0.18→1.386=2ln2 across the Page time
  (N=10 Haar-scrambled; the info comes back, fully recoverable -- Hayden-Preskill
  mirror). P3 ✓ unitary returns I=1.39 vs thermal 0 → unitarity = the
  information-RECOVERABLE description; the Page time = the recoverability
  transition (a decoder exists iff I>0). Honest: a demonstration, not new physics.
  In verify.sh. **EMERGENT-SPACETIME MAP COMPLETE: J5 (entanglement→geometry→
  curvature) · Cert V (no observer-independent TIME, 101) · dS anchor (no
  observer-independent FRAME, 111) · Page curve (information RETURNS, 112).**
- **AHARONOV-BOHM HOLONOMY (2026-06-24, script 113), 3/3.** A net discovers a phase
  from ZERO local field: closed loops (winding n∈-2..2, randomized shape) around a
  confined flux Φ (B=0 off-origin), true phase=Φ·n; three DeepSets (mask-summed
  over edges), each a different per-edge view. AB1 ✓ holonomy net (per-edge A·dl)
  learns phase=Φ·winding R²=1.000; AB2 ✓ whisker/shape-invariant (Δ0.033 →
  topological, winding-only); AB3 ✓ certificate: NEITHER local-field (B=0,
  R²=-0.002) NOR geometric perimeter (R²=-0.004) predicts it, only the loop
  integral → no local-field AND no shape code; the observable is the non-local
  topological enclosed flux. Web-verified AB. Ties Berry (54, geometric/area) →
  AB (topological/winding) + the gauge theme + the certificate-quintet 'no local
  code'. In verify.sh.
- **SPINOR DOUBLE COVER, DISCOVERY PARADIGM (2026-06-24, script 114), 3/3.**
  Companion to 98 (symbolic-library: half-angle features + sign-unobservable
  certificate); 114 adds what 98 lacked — a NET learns the double cover, shown as
  TWO SHEETS over the same lab-frame point, framed as a continuous-rotation
  HOLONOMY (spinor-sign cousin of AB/Berry). SU(2)→SO(3) double cover (web-verified):
  360° gives -1 on the STATE, 720° returns; interference cos(α/2) is 720-periodic
  (Rauch-Werner), the Bloch vector only 360. S1 ✓ spinor-net (input=continuous α)
  learns cos(α/2) R²=1.000; S2 ✓ certificate: bloch-net (lab-frame cos α,sin α)
  CANNOT (R²=-0.001) — no 2π input yields a 4π output, double cover invisible to
  single-time measurements; S3 ✓ two sheets: at the same lab orientation (α vs
  α+2π) spinor gives OPPOSITE preds (diff 1.27, bloch forced 0.00), pred(360°)=-1.00,
  pred(720°)=+1.01. Ties 98 + 51 (Bloch discovery) + holonomy cluster (AB 113,
  Berry 54). In verify.sh.
- **GRID-CELL TORUS — topology of a navigation code (2026-06-24, scripts
  115/115b).** Curvature-atlas neuroscience row (after ring 90). Web-verified
  Gardner 2022: a grid MODULE's population = a TORUS (b0=1,b1=2,b2=1; Ripser
  Z_p). Built a Betti reader (ratio-gap + RMS norm), de-risked in stages. **T0 ✓
  (gated):** reader validated on synthetic torus/sphere/plane/circle 4/4. **T1 ✓
  (gated):** ideal hexagonal grid module → [1,2,1] (torus); ideal place code →
  b1=0 (not a torus) — the instrument distinguishes the codes by topology
  (Gardner result reproduced on ideal codes). **T2 EMERGENCE = HONEST PARTIAL
  (115b, not gated):** a trained path-integrator (Sorscher softmax-PC + CE + ReLU
  + conformal-isometry regularizer) LEARNS path integration (CE 6.24→3.51),
  isometry nudges gridness (max −0.02→0.12), but NO clean grids (0%) → place-like
  code → learned manifold [1,0,0] (plane, not torus). PI + nonnegativity necessary
  but NOT sufficient; toroidal grids need the conformal-NORMALIZATION architecture
  (Xu/Wu/Gao 2023, arXiv:2310.19192), beyond this budget (3 trainer rounds,
  disciplined stop). Added ripser+persim to venv. 115 in verify.sh.
- **FULL EMERGENT GRID TORUS (2026-06-24, script 116) — chased down, both gates.**
  User: "chase the full emergent torus." Faithful PyTorch port of the Gao-Wu
  representational model (ruiqigao/grid-cell-path, NeurIPS 2021; cloned + read the
  repo): code v[40,40,192]=16 blocks×12, decode u≥0, antisym Lie generators Bx/By,
  motion M=I+A+A²/2; losses = kernel ⟨v(x),u(x')⟩=Gaussian + transformation (PI) +
  **ISOMETRY** ‖B(θ1)v‖=‖B(θ2)v‖ (the hexagon driver) + reg_u; block-normalize v +
  clip u≥0 each step. Why 115b only nudged: the isometry must be INTRINSIC to the
  transport, not a soft add-on. **H1 ✓** genuine hexagons emerge (peak gridness
  0.84 vs 115b's 0.12); **H2 ✓ (controlled)** 11/16 block-modules' population
  manifolds read as TORI [1,2,1] via the 115 instrument vs **0/16 for an untrained
  control** (all planes) and [1,0,0] for the 115b place code → emergent toroidal
  topology from training, NOT a reader artifact. Nuance: module=torus iff the code
  is 2D-PERIODIC (weaker than strict hexagonal gridness) → topology robust (11/16)
  even at modest per-cell frac>0.3 (0.03). Honest scope: training transiently
  forms then degrades grids (cosine lr + best-checkpoint used); full STABLE
  per-cell convergence needs the reference's full scale (90k-batch × 8000 epochs).
  Model saved (116_grid_model.pt); fast --probe-only gate in verify.sh. The
  curvature-atlas grid-cell-torus row is now a FULL emergent result.
- **ARROW OF TIME — entropy production / fluctuation theorem (2026-06-24, script
  119), 3/3.** Poke 3 of 3 (the arc COMPLETE). Extends the friction boundary (70).
  From trajectories ALONE a net discovers the second law. Web-verified Crooks:
  P_F/P_R=e^σ → the optimal forward-vs-reverse discriminator's log-odds IS the
  entropy production. Overdamped Langevin in a dragged harmonic trap (ΔF=0 → σ=W).
  A1 ✓ a DeepSets net trained ONLY to classify forward vs time-reversed
  trajectories has a logit matching analytic W, corr=0.995 (cheapest forward-vs-
  reverse code = the second law); A2 ✓ Crooks log-ratio slope 1.01 + Jarzynski
  ⟨e⁻ᵂ⟩=0.87 (~1, finite-sample low bias); A3 ✓ certificate: quasistatic→σ≈0→
  forward/reverse INDISTINGUISHABLE (AUC 0.55), fast→σ=3.28→readable (AUC 0.96) —
  time's arrow legible iff entropy produced (ties friction 70). In verify.sh.
- **EMERGENT DIMENSION FROM RG — real-space coarse-graining (2026-06-24, script
  118), honest 2/3.** Poke 2 of 3. Makes emergent_dimension.md executable via
  real-space block-RG on 1D classical Gaussian fields (distinct from J4/J5's
  entanglement route). Web-verified MERA=discrete AdS (Swingle): emergent extra
  dimension = RG length scale. Massive free field P(k)=1/(k²+m²), ξ=1/m. **R1 ✓**
  emergent depth = log₂ξ (active RG-tower depth where neighbor-corr drops, fit
  R²=1.000, slope~1; criticality→maximal depth) — coarse-graining GENERATES the
  scale dimension, extent=log ξ; **R2 ✓** radial homogeneity only at criticality
  (ρ_s flat, slope 0.008 = scale-invariant = AdS radial isometry; gapped flows
  0.131, >16×). **R3 hyperbolic geometry = honest WEAK INSTRUMENT** (not claimed):
  d_geo and C(r) don't cleanly separate hyperbolic from flat in 1D classical
  (crit corr ~1 → tiny noisy geodesic; 1/k² critical limit is rough) — the
  hyperbolic/AdS geometry is established cleanly in J4 (entanglement, exact
  log-law). One fix round (N→16384) confirmed R2 not R3. Gate R1+R2 in verify.sh.
- **CURVATURE AS THE BOTTLENECK (2026-06-25, script 129), 3/3.** Phase 1b probe #2
  (field_guide §9 loose end). Phase E read curvature post-hoc; here curvature is the
  BOTTLENECK. Jacobi geodesic deviation s″=−K s on constant-curvature surfaces; a
  SciNet encoder(probe curve)→latent z→decoder(z, new IC, query t). CB1 ✓ 1-D
  bottleneck suffices (held-out R²=1.000); CB2 ✓ the latent IS curvature (decodes K
  at r=0.999, coordinate-free); CB3 ✓ minimality (extra dims +0.000 — 1-number code)
  + necessity (bottleneck lifts a curvature-blind control 0.60→1.000; the flat
  s0+v0t part is K-independent, curvature is the geometry-dependent correction).
  Curvature emerges as the minimal sufficient code for geodesic behavior. In verify.sh.
- **OPERATIONAL OBSERVERS (2026-06-25, script 130), 3/3.** Phase 1b probe #3 — the
  interval from RADAR light-timings, not given coordinates. Phase A used given (t,x);
  here observers are operational (Bondi k-calculus): radar T_send=t−x, T_recv=t+x ⇒
  s²=T_send·T_recv; a boost Doppler-scales the timings (×e^∓φ, Bondi k) but the PRODUCT
  is invariant → a strict-distance Siamese on raw timings is forced to discover it.
  O1 ✓ K=1 saturates (acc 0.95) + 1-D latent decodes s²=T_s·T_r isotonic R²=0.999;
  O2 ✓ clock-noise robust (5% mult. noise → acc 0.91, R² 0.994); O3 ✓ the invariant
  is the PRODUCT (latent |r|=0.999), Doppler-INVARIANT across observers (CoV 0.000) vs
  euclidean T_s²+T_r² (CoV 0.95). Fix round: isotonic increasing="auto"; O3 muddy
  correlation → Doppler-invariance CoV test. Deepens "no fixed reference" (Cert V 101
  / dS anchor 111): the interval is operationally real (survives given-coords → noisy
  light-signals). In verify.sh.
- **RELATIVISTIC RAPIDITY (2026-06-25, script 131), 3/3 (clean).** Phase 1b probe #4 —
  the gravity phases ran slow-motion; here we go relativistic. Velocities compose as
  w=(v1+v2)/(1+v1v2), but the 1+1 Lorentz group is the real line under ADDITION in
  RAPIDITY φ=atanh(v) (φ=φ1+φ2). Toy = an additive-bottleneck net ψ(v1)+ψ(v2)→decode w;
  only bias = "boosts compose additively in some learned coordinate", the net must
  discover which. R1 ✓ held-out R²=1.000 on Einstein composition; R2 ✓ learned ψ
  recovers atanh(v) at |r|=1.000 (vs 0.985 for velocity) — discovers rapidity; R3 ✓
  relativistic not Galilean (w=v1+v2 goes superluminal |w|>1 on 36% of high-speed
  pairs, MSE 732× worse, ψ nonlinear = v only near 0). The additive parameter of the
  1+1 Lorentz group is unique up to scale → the net is forced to find rapidity.
  Relativity from the composition law alone. Ties Phase A (interval) + 130 (k-calculus).
  In verify.sh.
- **EXTRAPOLATION IS A CONFOUNDED TEST OF DISCOVERY (2026-06-26, script 134), honest
  3/3 reframe.** Phase 1b probe #6. Acid-test intuition: a net that DISCOVERED a law
  should extrapolate beyond training. Tested on velocity composition (bounded, coord
  atanh) vs Doppler k=k1·k2 (unbounded, coord log), structured additive-bottleneck vs
  generic MLP, trained on moderate compositions only. Original "structured extrapolates,
  generic fails" REFUTED → deeper finding (median-rel-err, R² unstable on narrow bands):
  G1 benign → BOTH extrapolate (velocity 3%/5%); G2 growing → BOTH fail (Doppler 48%/24%
  — even the structured exp-decoder faces OOD growth); G3 structure found (ψ=atanh/log
  |r|=1.000). Extrapolation is confounded (fails both ways) despite real discovery →
  validate discovery by DIRECT structure-verification (the invariant-decode gates the
  project already uses), not extrapolation. Honest scoping of our own methodology;
  no-free-lunch in extrapolation (some component always extrapolates the OOD output).
  NOT in verify.sh (methodological + trains 4 nets/run). Probe #5 (133 comms-game) was
  an honest easy-target null; #6 here a methodological scoping. Phase 1b's clean physics
  wins are 128-131 (+ 132 bridge).
- **HUYGENS' PRINCIPLE BY DIMENSION (2026-06-25, script 128), 3/3.** Phase 1b
  probe #1; validates dimensional_ladder §5. Web-verified (Hadamard; Ehrenfest):
  the wave eq satisfies Huygens in ODD spatial dim (3D sharp, field→0 after the
  front) and violates it in EVEN (2D: a ~1/√(t²−r²) cylindrical tail). Source-driven
  radial FDTD u_tt=u_rr+((d-1)/r)u_r, only d differs. H1 ✓ 3D tail/peak 0.0000 vs 2D
  0.226; H2 ✓ same wavefront speed (arrival 5.18 vs 5.09 — the WAKE differs, not c);
  H3 ✓ 2D tail matches the cylindrical Green form, corr 1.00. A clean 'now' exists
  only in odd spatial dim (a reason our world is 3+1). Reliable solver (PINN noted
  but finicky for long-time waves). In verify.sh.
- **A10 FOR THEBRIDGE — legibility ⟺ integrability (2026-06-25, script 127), 3/3.**
  Sister-project help (TheBridge SISTER_REQUESTS A10, the tabula-addressed ask). Does
  a learned geometry become LEGIBLE iff the metric is INTEGRABLE (admits a Killing
  tensor)? Unified our piecewise results (92 Kerr / 97 KdS / 99 KN+bumpy / 85 chaos)
  into one emit-or-certify catalog survey + added Taub-NUT (web-verified integrable;
  NUT shift L→L−2n cosθ). Staeckel Kerr-like geodesic toy, params Q/Lam/nut/eps. G1 ✓
  integrable {Kerr, Kerr-Newman, Kerr-de Sitter, Taub-NUT} EMIT the Carter constant
  (held-out ~1e-28); G2 ✓ non-integrable {bumpy×2} CERTIFY (held-out ~1e-2, Carter
  drift ~0.25); G3 ✓ legible⟺integrable perfect across the catalog (~26 orders of mag
  separation). Deliverable: results/127 JSON + notes/A10_for_bridge.md (bridge reads
  read-only; repos independent). Strengthens our distillation arc (91-99) into a clean
  integrability↔legibility correlation. In verify.sh.
- **ZV GAMMA-METRIC — A10 extension for TheBridge (2026-06-25, script 132), 3/3.**
  Bridge follow-up: leg Q had only ONE non-integrable test (the 127 bump); added a
  literature-standard 2nd in a DIFFERENT deformation + coordinates — the Zipoy-Voorhees
  γ-metric (static axisym VACUUM Weyl; δ=1≡Schwarzschild integrable, δ=2 proven non-
  integrable: no Killing tensor up to valence 11, no poly integral deg≤6; web-verified
  Lukes-Gerakopoulos 1206.0660 + Kruglikov-Matveev 1111.4690). Built the ZV geodesic
  Hamiltonian in prolate-spheroidal (x,y) (autograd RK4, bound geodesics), reused the 99
  emit-or-certify engine. DERIVED the target: HJ cross-term (x²−y²)^(1−δ²) is y-indep iff
  δ=1 → separation constant C=(1−y²)p_y²+L²/(1−y²) (=L_total²). Z1 ✓ δ=1 EMITS (held-out
  6.9e-24, cosine to C 1.000); Z2 ✓ δ=2 CERTIFIES (same C drifts 7e17× the integrable
  floor at matched E,L; 3e-4 macroscopic nearer ISCO — Killing-tensor invariant
  destroyed); Z3 ✓ legible⟺integrable. Fix round: absolute threshold mislabeled δ=2's
  KAM remnant → switched to the 99 RELATIVE-EXACTNESS test (conserved to integration
  precision or not). Deliverable: results/132 JSON + 2 rows in notes/A10_for_bridge.md
  (6th metric, 2nd independent non-integrable case). In verify.sh.
- **GEOMETRY FROM ENTANGLEMENT — dimension + 2D grid, closing J2 (2026-06-25,
  script 125), 3/3.** Build-queue item 6. Phase J (32) recovered a chain's 1D order
  + Van Raamsdonk pinch-off but left J2 open (PCA overcounted dimension; 2D grid
  needed spectral embedding). Free-fermion gapped states (staggered → smooth
  correlations, no parity pathology), chain N=48 + grid 9×9; MI from Peschel,
  positions never given. J2a ✓ geodesic correlation-dimension recovers chain 1.11
  (=1)/grid 1.83 (=2) while PCA/MDS overcounts the curved chain (2-D) — the J2
  failure fixed by a manifold-aware (neighbor-rank) estimator; J2b ✓ Isomap+MDS
  recovers the 2D grid layout (Procrustes corr 0.99); J2c ✓ recovered geodesic
  matches true distance (Spearman 1.00/0.95). One fix round (ball-growth/raw-MI →
  geodesic correlation-dim + geodesic monotonicity). Ties J1 (32) + J5 (42). In
  verify.sh.
- **GRAPH OLLIVIER-RICCI CURVATURE (2026-06-25, script 124), 3/3.** Build-queue
  item 5; a curvature-atlas row (after finance 88 / hierarchy 89 / neuroscience 90)
  — curvature as the geometric signature of network structure, beyond gravity.
  Web-verified (Ollivier; Sia/Ni et al. 2019): ORC κ(x,y)=1−W₁(m_x,m_y)/d(x,y);
  community graphs → BIMODAL curvature (intra-community positive, inter-community
  bridges negative). SBM toy; W₁ via a scipy.linprog optimal-transport LP; networkx.
  O1 ✓ bimodal (intra +0.12 > 0 > inter −0.21, bridge AUC 1.00); O2 ✓ Ricci surgery
  (cut negative-curvature edges) recovers communities ARI=1.00; O3 ✓ control: random
  cut ARI 0.00, SBM gap 5× the ER-graph spread — curvature carries the signal. Clean
  first attempt. networkx added to requirements. In verify.sh.
- **GRAVITATIONAL WAVES — radiation is quadrupolar (2026-06-25, script 123), 3/3.**
  Build-queue item 4 — the GR-DYNAMICS step (first non-static learned geometry).
  Web-verified Einstein 1918 quadrupole formula: h∝Q̈(t-r/c); NO monopole (mass-
  energy conservation) or dipole (momentum conservation) radiation. Toy (G=c=1):
  binary (quadrupole) / octahedral breathing (monopole) / rigid translation
  (dipole), multipoles about COM. W1 ✓ a net predicts radiated power from the
  quadrupole Q_ij(t) (R²=0.993) but not from monopole+dipole (R²=0.053); W2 ✓
  certificate: breathing & translating sources radiate ~0 vs binary (~10²⁷×) — no
  monopole/dipole GW; W3 ✓ outgoing wave at speed c (1.026), 1/r far-field falloff.
  Smoke-test caught 2 physics bugs (breathing needs octahedral dirs for Q=0; Q
  about the COM). Honest scope: linearized GW (Newtonian sources + quadrupole
  formula), not full GR. In verify.sh.
- **HORIZON THERMODYNAMICS — Bekenstein-Hawking S = A/4 (2026-06-25, script 122),
  3/3.** Build-queue item 3 — closes the loop to the project's ORIGIN (the Brian-Cox
  black-hole chat: holography, S=A/4, the M² law). Web-verified Schwarzschild:
  T=1/(8πM), A=16πM², S=A/4=4πM², first law T⁻¹=dS/dM. A net learns S(M) from
  observable (mass + Hawking T) via the first law (autodiff dS/dM=1/T) + S→0 anchor.
  H1 ✓ S vs horizon area linear, slope 0.250, R²=1.000 (=A/4); H2 ✓ holographic —
  S∝M² (area, R²=1.000) >> S∝M³ (volume 0.976), T∝1/M — ~1 bit per Planck area, not
  volume; H3 ✓ negative specific heat (bigger holes are COLDER) + first law holds
  (residual 0.020). Two principled instrument fixes (H1 clean first run): S-vs-M²
  linear fit (offset-robust) + train wider than eval; lower obs noise + more steps
  for H3's residual. Ties 112 (info return) + Phase BH (geometry). In verify.sh.
- **FISHER = GR METRIC / natural gradient (2026-06-25, script 121), 3/3.**
  Build-queue item 2 (nn_and_spacetime §5). The ML↔GR bridge made executable: the
  shared object is the METRIC. Fisher info = GR's g; natural gradient (Amari)
  g⁻¹∇L = the covariant, reparameterization-invariant update. Self-verifying toy
  (1D Gaussian, 3 scale coords σ/log σ/σ³). F1 ✓ autodiff Fisher (Hessian of mean
  NLL) = analytic diag(1/σ²,2/σ²) rel err 0.005; F2 ✓ general covariance — natural-
  GD distribution-space path coord-free (div 0.0046 vs ordinary 0.470, 103×); F3 ✓
  (fixed finite budget) natural converges in all coords (max KL 1.4e-5) vs ordinary
  lags in σ³ (0.27, >50×). One fix round (finite budget; F2 is the budget-free
  result). In verify.sh.
- **2D CHERN NUMBER (2026-06-25, script 120), 3/3.** Build-queue item 1
  (notes/build_queue.md + open_threads_backlog.md = the backlog knock-out). 2D
  cousin of 117 — caps the topology cluster. Web-verified Qi-Wu-Zhang:
  d(k)=(sin kx, sin ky, u+cos kx+cos ky); Chern = degree of the Gauss map
  T²→S² = +1(0<u<2)/−1(−2<u<0)/0(|u|>2). C1 ✓ DeepSets net over BZ plaquettes
  (summing solid angles = Berry flux) learns C=integer R²=0.992 round-acc 100%
  (excluding the gapless window where C is ill-defined — physics, not tuning);
  C2 ✓ robust to gap-preserving deformations (Δ0.007), u-sweep flips 0/−1/+1/0
  only at gap closings u=−2,0,2; C3 ✓ bulk-boundary, strip chiral edge states iff
  C≠0. One fix round (exclude gapless u). In verify.sh.
- **TOPOLOGICAL BAND THEORY — SSH winding + bulk-boundary (2026-06-24, script 117),
  3/3.** Poke 1 of 3 (notes/topology_rg_arrow_plan.md). Caps the topology/holonomy
  cluster (AB 113 → Berry 54 → grid torus → band topology). Web-verified SSH (BDI):
  d(k)=(v+w cos k, w sin k); winding of d over the BZ = invariant (0 trivial v>w /
  1 topological w>v), a HOLONOMY; bulk-boundary #edge modes = 2·winding. B1 ✓ a
  DeepSets net over BZ segments (unit d-vectors → angles) learns the winding,
  R²=0.999, integer-round-acc 100%; B2 ✓ quantized/robust — gap-preserving
  deformations leave it unchanged (Δ0.029), a v-sweep flips 0↔1 only at the gap
  closing v=w; B3 ✓ bulk-boundary — 2·round(net winding) == open-chain edge-mode
  count for 97% (misses near v=w finite-size). Ties AB (winding) + Berry (curvature)
  + certificate quantization. In verify.sh. (2D Chern left as future.)
- **CURVATURE ATLAS (2026-06-19, scripts 88-90):** curvature/holonomy/topology as the
  universal signature of "the cheapest shared description," beyond gravity. Finance
  (88, no-arbitrage = flat connection, arbitrage = holonomy, numéraire = gauge, 3/3);
  hierarchy (89, trees intrinsically hyperbolic, Gromov δ 0 vs grid 6, 2/3 core-clean);
  neuroscience (90, population activity = ring S¹, Betti b1=1, 3/3). Open rows: graph
  Ollivier-Ricci, Turing patterns, grid-cell torus.
- **SYMBOLIC DISTILLATION HEAD (2026-06-20, scripts 91-92) — tabula is now a PROPOSAL
  engine, not just a reading instrument.** It EMITS verified closed-form invariants
  (not scalars/counts/embeddings) as the CHEAPEST CONSERVED CODE: a sparse combination
  over a physics feature library, found by a generalized eigenproblem (within-traj /
  total variance; near-zero eigenvalues = conserved directions; sparse rotation =
  formulas). 91: calibrated on Kepler — emits E and L exactly, self-verified, and
  REFUSES to hallucinate on chaotic Lorenz (no-hallucination guard, inherits cert II).
  92: hard calibration — emits Kerr's CARTER CONSTANT (a hidden Killing-TENSOR
  invariant, quadratic in momenta, not readable off the metric) at cosine 1.0000, exact
  coefficients, verified 1e-28. Proven from easy (Killing vectors E,L) to hard (Killing
  tensor). Built OUR way (linear algebra + sparsity + MDL; no imported symbolic
  regression). 93 EMIT-OR-CERTIFY (DONE): distillation head × impossibility certificate
  FUSED into one instrument — proposes a verified invariant when integrable, certifies
  chaos (no hidden invariant) when a deformation destroys integrability. Pullen-Edmonds
  (bounded, exact quadratic at λ=0); HELD-OUT verification as the honest decision; 3/3
  (held-out var-ratio 1.3e-29 emit → 0.62 certify). The inductive-discovery payoff
  (propose-or-prove-impossible), all in our repo. (Deformed-Kerr angular sector tried
  first but hit a 1/sin²θ pole + θ-clip artifact — diagnosed, pivoted to Pullen-Edmonds.)
- **94 UNKNOWN-REGIME DISCOVERY (DONE) — the payoff.** Aimed emit-or-certify at the
  coupled quartic oscillator (bounded; integrable ONLY at α=0,1,3, chaotic otherwise —
  invisible in the Hamiltonian) and DISCOVERED the integrable islands {0,1,3} EXACTLY
  from trajectory data alone (held-out ~1e-10 at islands vs ~0.8 chaos, 10-order
  separation; U1/U2/U3 all pass). Test = a SECOND H-independent invariant (integrability
  of a 2-DOF system); complete degree-2+4 monomial library; held-out verification.
  The instrument reconstructs the integrability structure of parameter space with no
  analytic input — the capability transfers to families where the islands are NOT known.
  DISTILLATION ARC (91/92/93/94): tabula reads, writes, AND discovers.
- **95 OPEN FAMILY + 96 RICHER INVARIANTS.** 95: aimed emit-or-certify OFF the
  classified line (anisotropic quartic V=1/4(x^4+kappa y^4)+(alpha/2)x^2y^2),
  cross-validated against an INDEPENDENT chaos diagnostic (SALI chaotic-fraction).
  3/3 honest gates: recovers the kappa=1 anchor {0,1,3}; agrees with SALI on every
  unambiguous point; open finding -- at kappa=2 only alpha=0 keeps an exact low-degree
  invariant (anisotropy destroys the alpha=1,3 islands). The informative disagreements
  (regular dynamics but NO low-degree polynomial invariant) flag RICHER-invariant
  candidates + the honest caveat (certify = no low-degree invariant, not provably
  chaotic). 96: extend the library to RATIONAL features and catch the Kepler LRL vector
  (the hidden SO(3) invariant, Kepler's analog of Kerr's Carter constant) -- RATIONAL
  (x/r term), so a polynomial library MISSES it (finds E,L), a rational library CATCHES
  it (finds E,L,A_x,A_y, held-out 6e-6). The capability for Carter-analogs in deformed
  black holes.
- **97 THE DEFORMED-KERR TARGET, DONE RIGHT — Kerr-de Sitter's rational Carter
  constant.** Web-verified Kerr-de Sitter separation: the cosmological constant adds
  Delta_theta = 1+(Lambda a^2/3)cos^2(theta), making Carter's constant RATIONAL. 3/3
  (revised honest gates): D1 both libraries exact at Lambda=0; D2 the Lambda-aware
  (Delta_theta-weighted, rational) library represents the deformed Carter EXACTLY
  (held-out 3e-29, cosine to textbook K_Lambda 1.0000) while the Kerr-tuned polynomial
  library only APPROXIMATES it, error growing monotonically with Lambda (4e-31->2e-4);
  D3 reduces to Kerr's Carter at Lambda->0. Honest deviation: the polynomial doesn't
  MISS the invariant (it approximates a rational function well over the accessible band)
  -- the sharper finding is EXACT vs growing-approximation, which is WHY Carter needed
  the rational ansatz. **The distillation arc (91-97) is complete: reads probes (91),
  writes Kerr's Carter (92), emit-or-certify (93), discovers islands (94), maps off the
  textbook line cross-validated (95), catches rational invariants (96 LRL), represents a
  real deformed BH's rational Carter exactly (97).**
- **98 SPINOR DOUBLE COVER — the function-class rung + an SO(3)-invisibility certificate.**
  The genuinely-open field-menu item (Dirac/spinor), as the rung past rational. Web-
  verified SU(2)->SO(3) double cover + Rauch-Werner 720deg neutron interferometry. 3/3:
  G1 an integer-angle library (the class of every SO(3) observable) gives held-out
  R2=-0.01 on the spinor interference cos(alpha/2) while a HALF-ANGLE library gives
  1.0000 -- a required new feature class; G2 the spinor sign is unobservable from the
  Bloch vector (Bloch identical at alpha and alpha+2pi to 2e-15, interference exactly
  opposite) -- a 2pi input cannot make a 4pi output, an impossibility certificate; G3
  -1 at 360deg (destructive), +1 at 720deg (constructive). UNIFIES the function-class
  arc (91-97) with the impossibility-certificate arc (84-87).
- **99 SECOND DEFORMED METRIC — separability-preserving vs integrability-breaking.** Can
  the engine tell a deformation that KEEPS the hidden symmetry from one that DESTROYS it?
  Faithful Staeckel-separable Kerr-like geodesic Hamiltonian; web-verified Kerr-Newman
  integrability (arXiv:1202.5228) + bumpy-BH Carter breaking (arXiv:2305.18522). 3/3:
  C1 Kerr emits the EXACT Carter (held-out 5e-28, cosine 1.000); C2 Kerr-Newman (charge
  in Delta_r, separability kept) STILL emits the EXACT Carter; C3 a quadrupole bump
  DESTROYS it (Carter drifts 0.23, engine's best is NOT the Carter at cosine 0.20, 4e25x
  less exact). Honest KAM caveat: a crude approximate invariant always lingers under
  bounded confinement, so the decisive test is whether the SPECIFIC Killing-tensor
  symmetry survives exactly. Build bug fixed (H*Sigma~H r^2 is anti-binding; put H0 r^2
  in V_r to cancel it in the radial EOM).
- **NN scaling backlog parked** (notes/scaling_backlog.md) for when the L4 VM frees up
  (Ludo training now): A=quick wins (Hierarchy H2 Riemannian optimizer, MDL M1 seeds),
  B=architecture bets (FNO for Phase F long-range, orthogonal-F Wong v3, larger G-sym),
  C=do-not-scale (the certificates/gauge/function-class walls are the result). Meta:
  bigger is often WORSE for a discovery project (minimality IS the result).
- **HAIL MARY (long-shot/hobby track, curvature/hailmary/ + notes/hail_mary.md):
  neural numerical relativity reframed as ML.** Phase 1 (Maxwell testbed): the
  modular recipe -- decompose + enforce the constraint/gauge BY CONSTRUCTION
  (Leray projection) + push-forward for stability -- is robust (charged, scale,
  8 seeds); the learned-dynamics half has bounded autoregressive error. Phase 2
  (verified Choptuik collapse solver, collapse.py): the constraint-respecting
  PHYSICS cracks criticality; the learned autoregressive emulator does NOT.
  **v3 rigorous re-examination (2026-06-21, user challenge "did we try
  everything?"):** the learned-half negative is now SCOPED + DIAGNOSED, not
  overstated. exp10 a spectral FNO collapses everything too (== CNN); exp11 even
  OVERFITTING one disperse trajectory fails (rollout -> 2m/r 0.999 via the stiff
  geometry readout) -- not arch/capacity/data; exp12 DECISIVE: a GLOBAL one-shot
  net scores 0.99 where the autoregressive emulator scores 0.50 (chance) on
  identical balanced data -- **the AUTOREGRESSIVE ROLLOUT is the wall**; exp4b
  the residual-stream (Plan B) diverges ~1/3 of seeds (6 seeds, either recipe),
  clean (Plan A) never. Literature (arXiv:2511.15247, w/ M. Choptuik): the
  published NN-Choptuik win is a PINN (global solve, physics-in-loss, no rollout)
  -- sidesteps this wall, wins by building physics in = OUR structure-by-
  construction thesis. Untried lever the literature validates = a global PINN
  solve (different paradigm; re-confirms the thesis). Pivot freely; nothing waits.
  **UNTRIED LEVER BUILT (script 136, 2026-06-26, VM GPU): the global PINN, honest
  PARTIAL.** Plain-MLP global PINN (first-order EMKG: outputs Phi,Pi,C,alpha;
  residuals = 2 field eqs + 2 metric constraints from collapse.py; IC + spatial-BC
  anchored to the FD reference). Pre-reg scope (stated up front, no overclaim): plain
  MLP, NOT the paper's ModPINN (QRes/RBF-embeddings/causality-weighting/adaptive-
  remeshing/SOAP/100k-epochs/A100) — demonstrate the PARADIGM, not near-critical
  accuracy. Result: **G2 DICHOTOMY ✓** — subcritical (A=0.02) max 2m/r 0.024 (DISPERSES,
  no spurious horizon — the exact regime the rollout drove to spurious collapse,
  exp11 D1); supercritical (A=0.40) max 2m/r 0.977 (COLLAPSES, FD 0.980). A global
  physics-in-loss solve with ZERO rollout steps reproduces the disperse/collapse
  criticality the rollout could not. **G1 ✗** — plain-MLP field accuracy poor (relL2
  Phi 0.62, C 0.70 vs gate 0.20); a plain MLP is not a quantitative solver (ModPINN
  territory, cited). So: the paradigm is demonstrated QUALITATIVELY (dichotomy + no
  spurious collapse, no rollout), not quantitatively — re-confirms structure-by-
  construction (physics-in-loss > learned rollout) honestly scoped. Not in verify.sh.
  **ACCURACY FOLLOW-UPS (137 ModPINN-lite, 138 full ModPINN, 2026-06-27, L4):** can
  better ARCHITECTURE close 136's field-accuracy gap? The PINN ACCURACY ARC: 136 plain
  MLP relL2_Phi **0.62** → 137 (+Fourier features +causality) **0.497** → 138 (full
  ModPINN: QRes blocks + 32 RBFs + residual-adaptive sampling + causality) **0.363** —
  a clear MONOTONIC improvement (each upgrade helps; 138 beats 137 by 0.134), dichotomy
  preserved throughout (sub C 0.024 / super 0.974). BUT all three miss the quantitative
  <0.20 gate: 138 plateaus ~0.36 at an L4-feasible budget (~22k steps; the paper's 100k
  on an A100 with SOAP would be ~9h here — the 2nd-order autograd runs ~3.6 step/s).
  Honest close of the hail-mary PINN arc: the global physics-in-loss paradigm (no
  rollout) is demonstrated AND better architecture monotonically improves accuracy —
  the remaining wall is COMPUTE, not the paradigm. 137/138 NOT in verify.sh (GPU-only,
  honest partials). Op-note (robust VM pattern, last night's idle-cost lesson fixed):
  4h watchdog self-stop works (gcloud active on the VM's service account); setsid-
  detached jobs survive Mac power-loss.
- Remaining curvature queue: the orthogonal-F Wong v3 (open thread above); other
  Phase H rows (equivalence-breaking gravity); a G-sym legibility-preserving
  variant; the deferred Phase J "geometry from entanglement" (It-from-Qubit
  bridge, in writeups/curvature_field_guide never-tried list); 3+1 Kaluza with
  vector potential; writeup polish (user, weekends).
- Wakeup policy (user 2026-06-11): SHORT delays (60-90s) between iterations;
  long delays only as fallback while harness-tracked jobs run.
- **FOCUS DIRECTIVE (user, 2026-06-13): curvature ONLY until mined out.**
  echoes (post-v5) and ringdown (post-v3) PARKED — complete arcs, green gates,
  shelf lists in their lab notebooks; revisit only when curvature is done.
- AUTONOMOUS MODE (user-authorized 2026-06-11; strengthened 2026-06-13):
  keep working the queue without waiting for prompts; schedule wakeups to
  continue; pre-register → build → gate → document every iteration; write
  reconsider notes at arc boundaries but DO NOT pause the loop until the user
  explicitly says they're back.
- User role: he watches/learns ML decisions here — explain choices simply, teach.

## Documentation taxonomy (adopted 2026-06-11 — MAINTAIN THIS)
Four doc types, each with one job:
- `JOURNAL.md` (root) — dated activity log, one entry per working session,
  newest first, all sub-projects. **Append an entry every session.**
- `writeups/` (root) — polished, self-contained, shareable narratives (e.g.
  `emergent_geometry.md` = the four-phase curvature story). Update when a
  project completes an arc; these are the artifacts to show people.
- `<sub>/notes/lab_notebook.md` — raw per-subproject record: pre-registrations,
  results, gotchas, corrections. Same-change updates (per coding standards).
- `README.md` (root) = index; `CLAUDE.md` = machine memory / status blocks;
  `<sub>/README.md` = methods + decisions (ADR equivalent).

## Engineering standards (adopted 2026-06-11)
`.claude/skills/ai-coding-standards/SKILL.md` governs ALL code work in this repo
(user-supplied skill, project-adapted). Key bits: search-before-write, smallest
diff, verify-before-done with fresh output shown, no narration comments, dependency
restraint, decisions recorded in sub-project README/lab notebook (ADR equivalent),
root CLAUDE.md status blocks updated when milestones land.

## Roadmap / where we are
1. ✅ 3+1 vs 2+1 concept map
2. ✅ 1+1 rung + scaling laws + 4+1 extrapolation & vocabulary
3. ✅ Side-explorations: NN↔spacetime (`nn_and_spacetime.md`) and the emergent-dimension /
   holography deep-dive (`emergent_dimension.md`). The latter produced the **three-way
   "extra dimension" contrast** that now frames both finales.
4. ⬜ **Next (Finale 2):** gravity *as* curvature — mass → Ricci curvature → geodesics that
   look like "falling." Intrinsic vs extrinsic curvature (Theorema Egregium). Column (c)
   of the emergent_dimension §4 table: curvature is NOT a dimension.
5. ⬜ **Finale 3 (the payoff):** **Kaluza–Klein** — literally adding a 5th dimension
   produces electromagnetism. Column (b) of the §4 table. Do *after* Finale 2.
