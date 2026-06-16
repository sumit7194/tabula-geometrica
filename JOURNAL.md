## 2026-06-17 (overnight cont., autonomous) — legibility law Leg 3: the boundary condition (observation regime)

Probed the legibility law's third leg ("invariant-preserving structure restores legibility") with a fresh
precessing-charge harness (scripts 71/71b/71c) and found a genuinely new boundary condition that sharpens
the law and lifts the old ~0.5 ceiling from scripts 33/34:

- **71 (direct obs, linear readout)** — instructive negative: BOTH generic and orthogonal updates keep the
  rotating charge legible (0.99); structure adds only exact conservation (|w| drift 0 vs 0.41), not
  legibility. The linear readout anchors the latent to the charge regardless of update.
- **71b (direct obs, NONLINEAR readout)** — still both legible (0.98/0.99); rules out "it was just the
  linear anchor." Under direct observation the update rule is simply irrelevant to legibility.
- **71c (INDIRECT obs — single probe, charge inferred from the time-series of its rotation)** — the effect
  appears decisively: orthogonal fits (0.96) and stays legible (linear 0.91, no erosion); GENERIC fits worse
  (0.64) AND scrambles (linear 0.06 / kNN 0.42 = the probe-ladder signature) and erodes through time
  (0.12->0.03).

**Refinement:** Leg 3 is not "structure always restores legibility." It is — **structure earns its keep
exactly when the conserved quantity must be INFERRED through the dynamics rather than read off directly.**
That is the Phase H Row 2 regime (a Wong charge seen through a force), which explains both why it scrambled
there and why amortized codes often stay legible anyway. The clean indirect harness also breaks 33/34's
apparent 0.5 ceiling (orthogonal reaches 0.91). Documented in lab notebook + a dated addendum to
writeups/legibility_law.md (Leg 3). Pre-registration honesty: 71 failed its gate (negative), one
learnability fix round (cycling probe + GRU), then 71b/71c were new conditions (not gate-tuning) that
located the boundary.


## 2026-06-17 (overnight, autonomous) — emergent/exotic gravity queue: 4 clean results, the geometrization criterion closed

Ran the user-authorized overnight queue ("Law-space prize, then exotic queue") to four 3/3 results, each
web-verified, pre-registered, gated, documented, committed:

- **#1 Entropic / emergent gravity (script 67)** — a net discovers gravity-as-bookkeeping: entropic force
  ∝ T (a(2T)/a(T)=2.00), vanishes at T->0 (0.10), extrapolates the law (a(4)/a(2)=1.85); energetic control
  T-independent. The reachable "emergent gravity" angle from the Feynman/QFT discussion (Verlinde).
- **#2 The field zoo (script 68)** — why gravity is the odd one out. Economy race across COUPLING
  (universal vs charge) x MEDIATOR MASS (massless vs massive Yukawa). Universal cells geometrize (R=1.5/0.5),
  charge cells stay force (R=429/133); the coupling axis decides by 2-3 orders of magnitude and the mass
  axis never flips a verdict. Gravity's place in the geometry basin is bought by UNIVERSAL COUPLING, not
  masslessness — even a massive graviton would geometrize.
- **#3 Exotic matter (script 69, roadmap #60)** — a net learns a wormhole-throat geometry from rulers only;
  the matter required to source its learned geometry (read via autodiff) has NEGATIVE energy density (-0.71)
  and violates the NEC (-1.68); a normal-star control is positive. Holding a shortcut open needs exotic
  matter — discovered without ever being shown an energy (the roadmap's "may be a null" worry didn't land).
- **#4 The friction boundary (script 70)** — universality is necessary but NOT sufficient. Friction is
  universal (mass-independent) yet does not geometrize (R=6e5) because it breaks time-reversal (reverse-
  return error 1.42 vs conservative 0.009). 

**The crystallized refinement:** a force geometrizes <=> it is UNIVERSAL **and** CONSERVATIVE. The field
zoo establishes the first condition (and places gravity); friction isolates the second. This is a clean
two-condition criterion sitting on top of the unification (geometry = amortized physics, script 55).

Open threads for next: orthogonal-F Wong v3 (does a structure-preserving update recover the legible
rotation?), equivalence-breaking gravity (the third "where it breaks" row), and folding the geometrization
criterion into writeups/curvature_field_guide.md (weekend, user polishes).

# Journal — activity log (SpaceTime: curvature / NN)

*One entry per working session, newest first. What happened, what was decided,
where the details live. (Lab-notebook-level detail stays in each sub-project's
`notes/lab_notebook.md`; polished narratives live in `writeups/`.)*

> **Repo split 2026-06-13:** the black-hole LIGO-data projects (echoes, ringdown,
> pbh) moved to `../BlackHole/`. Entries below predating the split are the shared
> historical narrative and mention all projects; new black-hole work logs to
> `../BlackHole/JOURNAL.md`. This journal is now curvature/NN going forward.

---

## 2026-06-17 — PHASE BH-2 + BH-3: the singularity, and what charge does (interior trilogy complete)
- Continuing the Phase BH plan (focus on the BH mind-benders). Both read out of LEARNED metrics, on CPU.
- **BH-2 — the singularity (3/3, script 63).** A net learns g_vv(r) for Schwarzschild; curvature
  R=-g_vv''=-4M/r³ via autodiff. Horizon SMOOTH (R̂(2M)=-0.50=true, corr 1.000 → coordinate flip, not a
  singularity); r=0 a REAL singularity (R̂(0.4)=-62.4, 124× blowup ~1/r³); SPACELIKE/end-of-time (escape
  dr/dv flips +0.25 outside → -0.49 inside trapped → r=0 is an unavoidable future moment).
- **BH-3 — charge / Reissner-Nordström (3/3, script 64).** A net learns g_vv(r,Q). Charge gives TWO
  horizons (learned [0.40,1.63] vs true [0.4,1.6], outer+Cauchy) and flips the singularity to TIMELIKE/
  avoidable (g_vv(0.2)=-7.0 for Q=0.8 vs +9.0 for Q=0). C2 is the Q→timelike relation the sister
  glass-box analyzer offered to independently verify.
- **PHASE BH interior-physics trilogy COMPLETE: flip (BH-1) + singularity (BH-2) + charge (BH-3).** BH-4
  (mech-interp on the validated generalist) is next, pending the eval. Also banked the QFT/Standard-Model
  general-model idea as future work (honest limit + the why-gravity-is-special and emergent-gravity-from-
  entanglement reachable angles). Docs: lab notebook; roadmap; results/63_*, 64_*.

## 2026-06-17 — Generalist v2 EVAL: the harness catches the spacetime families faking loss (fix applied)
- **User re-corrected:** "checking training is not just watching loss drop — naive"; picking 40k steps
  by round number is the same sin. Built the real eval harness (script `62_generalist_eval.py`): judge by
  specialist-floor ratio + held-out/extrapolation + WORLD-CODE DECODE + PHYSICAL GATES, not loss.
- **It immediately earned its keep.** First eval (40k checkpoint): gravity/scalar/bloch/charged genuinely
  learned (near floor, decode latents 0.98–1.0, Bloch's Born rule exact). But the **spacetime families
  faked it**: Schwarzschild had low MSE 8.4e-5 yet world-decode R²=0.37 and the horizon did NOT track M
  (pinned ~2.2 for true horizons 1.6/2.0/2.6); RN R²=0.16. The families central to the BH capstone are
  the ones loss hid. **Diagnosis (decisive):** in ds², M is only 2.16% of the target variance; a model
  ignoring M scores 9.6e-5, the generalist scored 8.4e-5 — right at the ignore-M ceiling.
- **Fix:** metric families now predict the metric component g_vv(r) directly (M-essential; ignoring M now
  costs 5.9e-2 vs 1e-4) — and g_vv's sign is the signature-flip probe. Re-training fresh; re-eval gates =
  decode-R²(M) + horizon-tracks-M. **Gate: no BH-4 mech-interp until the spacetime families represent M.**
  Methodology banked in memory. Docs: lab notebook; results/62_*.

## 2026-06-17 — STRATEGIC PIVOT: Generalist v2 becomes the main thread (full span, ~12M, MPS)
- **User's call:** stop building one-off specialists (they only tell us about one thing or about NNs;
  no cross-pollination, nothing rich to mech-interp). Commit to ONE bigger generalist where emergence
  and the BH mech-interp capstone can actually happen. Decisions: FULL data span, ~10-15M params, build
  now. Honest framing logged: specialists were right for building the lesson library; now the marginal
  specialist is local optimization and the prize is in the generalist (the Phase-G law-space — EM as its
  own region — only existed because a generalist saw many physics at once). Keep specialists only as
  controls. MPS ceiling acknowledged (~10-50M, not frontier; emergence not raw scale is the goal).
- **Built the foundation (one session):**
  - `worldgen_v2.py` — unified in-context episode schema across the FULL span: gravity, charged (EM),
    scalar, Schwarzschild, Reissner-Nordström (charged BH), Bloch (quantum). 3 modalities (trajectory /
    metric / quantum) in one (u,y)+mask format; the model infers the hidden world (q, M, Q, Bloch
    vector) in-context. Verified all 6 families generate cleanly.
  - `61_generalist_v2.py` — GeneralistV2: in-context transformer, **12.69M params** (hit the ~12M
    target), applying our lessons — amortized in-context inference (legibility), G-sym INVARIANT pool
    over the exchangeable context, built-in HOOKS (per-layer activation cache + the world code) for
    mech-interp from day one, MPS, bit-exact checkpoint/resume.
  - Smoke train (600 steps) proved the pipeline: trajectory families 8-13× over the ctx-mean baseline.
- **Real 40k-step train LAUNCHED on MPS** (detached, ~35 min, checkpointed to results/61_gen2.pt; loss
  0.001 by step 2000). NEXT: per-family convergence, then the law-space / world-summary probe (the
  cross-pollination prize) and the BH region for mech-interp (BH-4 hooks).

## 2026-06-17 — PHASE BH-1: the space↔time flip emerges in a learned black-hole interior (capstone)
- **User's ambitious pivot:** simulate the Penrose-diagram black-hole interior in a NN, then mech-interp
  the mind-benders — the space↔time switch inside the horizon, the singularity as a *time* not a place.
  Web-verified physics (r↔t causal swap at the horizon; spacelike Schwarzschild singularity; EF coords
  regular; RN charged singularity is timelike). Translated each phenomenon into a probeable net quantity:
  the swap = the learned metric's *signature flip*.
- **BH-1 (3/3), script `60_blackhole_spacetime_flip.py`.** A generic net learns ds²(r,dv,dr) in
  Eddington-Finkelstein coords across the horizon, **never told where the horizon is**; we fit the local
  metric per r and read the signature. interval R²=0.9999; learned g_vv crosses zero at **r\*=2.02**
  (true horizon 2.0 — the net *located* it as the flip locus); g_vv = −0.59 outside (v timelike) →
  +0.99 inside (v spacelike) — **the space↔time swap, emergent.** "The spacetime switch" = the
  direction the net treats as time becomes a space direction at the horizon it found on its own.
- Pre-reg correction (before running): in EF the swap is g_vv's sign flip, not a 90° eigenvector
  rotation — BH1c reframed to the signature-character inversion. Phase BH program registered (BH-2
  singularity, BH-3 charge/RN, BH-4 scale-up + hidden-layer hooks). Docs: lab notebook; results/60_*.

## 2026-06-17 — EXOTIC: Noether from data — recover a conserved quantum number from reactions
- Can a net rediscover a conservation law from ONLY allowed-vs-forbidden reaction labels (never the
  quantum numbers)? P=8 particles with hidden integer quantum numbers Q (1 or 2); reaction = signed
  count vector n, allowed iff Qn=0. Net learns K conservation functionals; sweep K. Script `59_noether_from_data.py`.
- **3/3 (one fix round).** N1 classify 1.000. N2 the learned functionals **span the true conserved
  quantum numbers exactly** (R²=1.000). N3 the recovery-span **knee counts the symmetries** (1-number
  world recovers at K=1; 2-number needs K=2: span 0.435→1.000). Fix round = N3 metric (accuracy
  saturates early since one conserved number already rejects most forbidden reactions; the span-R²
  knee is the right counter). **A net rediscovers conservation laws — which quantum numbers and how
  many — from reactions alone. Noether, backwards.** Docs: results/59_*.

## 2026-06-17 — EXOTIC: a net discovers charge conjugation (C / antimatter symmetry)
- Web-verified C/CPT (EM is C-invariant, Lorentz force odd in q; CPT exact). Can a net DISCOVER C —
  that negating the internal charge = the antiparticle — and DETECT violation? Magnetic dynamics
  (odd in q, C-symmetric) vs an even-in-q term (C-violating). Amortized net infers a signed charge
  code from (state,accel) context, predicts accel; C = negate the code. Script `58_antimatter_cpt.py`.
- **3/3.** Symmetric world: code→q |r|=0.96, C-equivariance cos(pred(−code),−pred(code))=**+0.95** —
  negating the internal charge flips the force = the antiparticle (C discovered as a coordinate
  involution). Violating world: cos=**−0.97** — negating doesn't flip → the net sharply detects the
  C-violation. **Antimatter = a sign in an internal coordinate**; the net finds it when the law is
  C-symmetric and sees it break otherwise. Ties to signed-charge (46) + Kaluza (D). Docs: results/58_*.

## 2026-06-17 — EXOTIC: a wormhole from entanglement (ER=EPR), the inverse of Phase J pinch-off
- Web-verified ER=EPR (Maldacena-Susskind): entanglement between two regions = a wormhole. Phase J
  showed decoupling flings regions apart; the inverse — does *adding* entanglement build a shortcut?
  Free-fermion chain, regions A={0,1}/B={16,17} (chain-distance 16), add a bridge bond (entanglement)
  between them, sweep its strength; emergent distance d = −log(region MI). Script `57_wormhole_er_epr.py`.
- **3/3.** d(A,B) collapses **4.44 → 0.37** as the bridge entanglement grows (monotone) — the two
  maximally-far regions become *closer than physical neighbors* (0.42) in the emergent geometry,
  without moving on the chain. A traversable **wormhole built from entanglement**, dose-responsive.
  Clean inverse of Phase J's Van Raamsdonk pinch-off. ER=EPR demonstrated in our MI-geometry. Pure
  linear algebra. Docs: lab notebook; results/57_*.

## 2026-06-17 — EXPANDED SCOPE: dark matter vs MOND as a shareability verdict (first out of black-hole orbit)
- **User pushed to widen the view** far beyond black holes (wormholes, dark matter, antimatter, particles,
  "wider area" — the method is domain-general). First pick: recast the real **DM-vs-MOND** controversy as
  our shareability/economy problem. Web-verified MOND (`g=(g_N+√(g_N²+4g_N·a0))/2`). MOND = modify the
  *universal law* (shared); dark matter = per-galaxy *halo* (per-instance) = tonight's exact axis.
  Script `56_dark_matter_vs_mond.py`.
- **3/3.** Many galaxies, true world = MOND with a0_i, sweep a0-spread (universality knob). MOND-model
  (shared law) vs DM-model (per-galaxy halo). **Universal anomaly → MOND fits AND zero-shot predicts new
  galaxies** (held-out R²=1.000) while dark matter can't predict an unfitted galaxy → Occam+predictivity
  favor MOND. **Per-system anomaly → shared law fails (0.000→0.014), only per-galaxy halos fit → dark
  matter real.** The verdict tracks anomaly-*universality*. The non-trivial content = the zero-shot
  predictivity asymmetry (shared explanations predict new instances; per-instance ones don't) — the real
  epistemic argument for MOND. Honest: MOND-generated data, so it shows the *model-selection logic*, not
  that MOND is right in reality. Extends the unification to a famous controversy. Docs: lab notebook; results/56_*.

## 2026-06-17 — THE UNIFICATION TEST: geometry = amortized physics (the repo's two laws are one)
- **The orthogonal "connect the dots" experiment.** The repo's two headline laws — PHYSICS (a label
  geometrizes iff *universal*; else a per-body force) and ML (a code is legible iff *amortized*; a free
  multi-D code scrambles) — may be ONE principle: *what's shared across instances collapses into
  structure; per-instance stays a scrambled tag.* Key realization: the economy-race geometry model IS
  the maximally-amortized (identity-blind) model and the force model IS the free code — so the two
  transitions might be the same comparison. Tested on ONE universality knob with three models
  (blind / amortized in-context / free), 2-D coupling so the free code can scramble. Script `55_unification.py`.
- **Result: UNIFICATION SUPPORTED (3/3 after one fix round).** Γ = blind/free MSE by σ = [0.30, 3.75,
  6.90, **26.96**] (geometrization transition; at σ=0 the shared model *beats* free → geometry). The
  needed per-body code is legible iff amortized: at max σ, amortized **0.97** vs free **0.43**. Both
  order parameters ride the *same* knob and co-emerge. **Geometry = amortized physics**: a law is
  geometric exactly when amortizable across bodies; a "force" when it must be stored per-body; and that
  residual code is legible iff amortized. One selection principle ("shareability") seen from physics
  and from representation-learning. Honest nuance: amortized legibility is signal-limited at low σ (the
  split emerges as σ grows). **Weekend-writeup-worthy synthesis** — ties the repo's two halves together.
- NEXT (user-queued): entropic / emergent gravity (Verlinde-style) — discover an attractive force from
  a statistical/entropic substrate; connects to It-from-Qubit (Phase J). Docs: lab notebook; results/55_*.

## 2026-06-16 (OVERNIGHT, autonomous) — exotic-physics queue: quantum/particle fields
User set an overnight autonomous queue ("try quantum/particle physics, things one conventionally
won't do"): Bloch sphere → confinement → Proca → Berry phase. Full rigour (pre-register → gate →
honest null → document → commit), credited web-verification.

- **Run 1 (QUANTUM — Bloch sphere) ✅ DISCOVERED.** Pointed our "discover geometry from observation"
  paradigm at quantum STATE space. SciNet bottleneck on qubit measurement probabilities (script
  `51_bloch_sphere.py`; web-verified Born rule P=(1+r·n)/2). The net invented the **Bloch sphere +
  Born rule** from measurement data alone: G2 sphere decode R²=1.000 with codes on |r|=1.000±0.011;
  G3 Born-rule gradient cos=0.998. **Knee at K=3, not the pre-registered 2** — the net found the 3-D
  Cartesian Bloch *vector* (which makes Born *linear*), not the 2-D angle chart: the Phase-A
  minimal-linearizing-code lesson, now in quantum state space. Deviation recorded openly. The quantum
  analog of Phase A's Minkowski-interval discovery. Docs: lab notebook; results/51_*.
- **Run 2 (PARTICLE — confinement) ✅ 3/3.** Is geometrization about universality or gravity's 1/r
  shape? A CONFINING force V~|x| (grows with distance, QCD-flux-tube-like) also geometrizes when
  universal: ratio [1.06, 3.40, 12.57, 26.78] across the spread sweep (script `52_confinement.py`).
  **Geometrization is shape-independent** — universality is the whole story. Generalizes script 45.
- **Run 4 (QUANTUM — Berry holonomy) ✅ 3/3.** Does a net discover that a geometric phase is a
  HOLONOMY (depends only on enclosed area, invariant to retraced paths)? Planar Berry-curvature toy,
  edge-sum (Stokes-structured) net predicts the geometric phase = signed area (script
  `54_berry_holonomy.py`; web-verified Berry = -½ solid angle). area-net R²=1.000; **whisker
  invariance Δ 0.9%** (vs the length/dynamical net's 72%, ~80× more). The net discovered the
  geometric phase is path-independent — the Berry signature; ties the quantum geometric phase to our
  curvature theme. Docs: lab notebook; results/54_*.
- **Run 3 (QUANTUM FIELD — Proca range knob) ✅ (after 1 fix round).** A massive mediator screens
  gravity's 1/r to short-range Yukawa; does locality flip learnability (the parked Phase F wall)?
  Script `53_proca_range.py`. First run: global R² masked it (small-RF gets 0.94 even for 1/r — the
  near-field dominates variance). Fix round (FAR-field R²): at µ=0 (1/r), small-RF far-field R²=**0.172**
  (fails the tail) vs large-RF **0.937** (recovers it). **Locality IS the learnability knob — the 1/r
  long-range TAIL needs a global receptive field.** Refines Phase F: the field-map is learnable at all
  ranges; only the long-range tail needs global operators (FNO-class). Docs: lab notebook; results/53_*.

- **OVERNIGHT WRAP-UP — exotic-physics queue COMPLETE (4/4 runs, all documented + committed):**
  Pointed our "discover geometry from observation" paradigm at quantum & particle physics. Headlines:
  (1) a net **invents the Bloch sphere + Born rule** from qubit measurements (the quantum Phase A);
  (2) geometrization is **shape-independent** (confinement geometrizes when universal);
  (3) a net **discovers a holonomy** (Berry geometric phase = enclosed area, path-independent);
  (4) **locality is the learnability knob** (the 1/r tail needs a global RF — Phase F wall isolated).
  Recurring thread: the net keeps choosing the **minimal LINEARIZING code** (Bloch *vector* not the
  2-D chart, knee at 3) — the Phase-A lesson, now confirmed in quantum state space. Two pre-reg
  deviations recorded openly (Bloch knee 2→3; Proca metric near→far). All rigour held; honest nulls
  and fixes logged. Remaining classical menu: Wong dynamic (orthogonal-F v3), Dirac/spinor.

## 2026-06-16 — POSITIONING the legibility law: amortization is an objective-independent lever
- **External review (parallel Claude session, credited)** located our defensible contribution vs the
  prior art. Web-verified the load-bearing citations: [Roeder-Metz-Kingma ICML 2021](https://arxiv.org/abs/2007.00810)
  (discriminative training → linear identifiability = our "amortized→legible" leg) and
  [Jiang-Veitch ICML 2024](https://arxiv.org/abs/2403.03867) (LLM linearity from the next-token
  softmax-CE loss). "Why linear" is crowded; our novel handle is that we get legibility from
  AMORTIZATION in a regression/contrastive harness with **no softmax-CE**.
- **Ran the decisive objective × storage 2×2** (script `50_objective_x_storage.py`), 3 seeds. Linear
  legibility of the latent: amortized×reg **0.84±0.06**, amortized×ce **0.86±0.06**, free×reg
  **0.22±0.02**, free×ce **0.72±0.06**. Amortization effect +0.38; objective effect within amortized
  0.02. **O1/O2/O4 pass: amortization is a sufficient, objective-independent lever** (legible ~0.85
  under both objectives, no LM objective needed) — separable from Jiang-Veitch. **O3 fails as a real
  finding:** softmax-CE *also* legibilizes a free code (0.22→0.72), confirming Jiang-Veitch in our
  harness. → the levers are **complementary, not competing.**
- **Reframed the writeup** (`writeups/legibility_law.md`, new "Prior work, and what is actually ours"):
  position WITH the literature; the contribution is the controlled one-variable isolation of
  amortization as an objective-independent lever, complementary to the data/objective theories.
  Don't let the geometry lead — it's the vehicle, the legibility law is the cargo. Docs + results/50_*.

## 2026-06-16 — NEW FIELD: dilaton (secondary hair) — honest partial, two real nuances
- **Dilaton = the secondary-hair field** (web-verified: the dilaton scalar charge is DETERMINED by
  mass & electric charge). Reused the script-24 lane-counter; dilaton arm q2=κq1 (determined) vs
  independent q2 (script 24). Predicted dilaton knee=1. Script `49_dilaton_secondary_hair.py`.
- **Honest partial (1/3 gates).** test MSE: dilaton L0 0.106→L1 4.9e-4→L2 1.8e-4; independent
  L0 0.163→L1 1.8e-3→L2 3.1e-4. DL2 (independent knee=2) PASS; DL1 (dilaton knee=1) FAIL; DL3
  (1-d lane legible) FAIL. Two real nuances instead:
  1. **Secondary hair shows as a SOFTENING:** the determined charge halves the value of the 2nd lane
     (2.7× vs 6.0×) and lets one lane reach a 3.7× lower floor — but not a clean knee=1, because
     model-capacity slack confounds knee-counting (the known Phase 11/12 lesson).
  2. **The 1-D rollout lane is linearly illegible (0.31)** — opposite of 48's direct-readout result —
     because the recurrent rollout F re-scrambles it: that's *leg 2* of the legibility law. So 48's
     "1-D free code legible" holds for direct readout; a recurrent latent scrambles even 1-D.
- Honest null on the clean prediction; no fix round (the failures are known limitations). Field menu
  remaining: Proca (range/learnability knob), Wong dynamic, Dirac. Docs: lab notebook; results/49_*.

## 2026-06-16 — what makes a free code scramble? → LATENT DIMENSIONALITY (refines the crown finding)
- **Chased the script-45 anomaly** (a free code that was *legible*) into a refinement of the
  legibility law's first leg. Three experiments:
  - **46** (2×2 sign × coupling): ruled out the obvious suspects — sign (±) and coupling-type
    (position vs velocity/magnetic) make NO difference, all four cells legible 0.99–1.00. Falsified
    my pre-registered "sign dominates."
  - **47** (control / neutral-mix / random-MLP, well-powered N=200): messy + confounded, but the key
    clue — even a *linearly*-coupled 2-D charge was only 0.70 linear / 0.94 nonlinear (partial
    scramble). Pointed at dimensionality.
  - **48** (clean isolation: charge in R^D → D independent wells, fixed tight 4-D code): **DIMENSIONALITY
    IS THE CAUSE.** D=1 linear 0.86 (legible) → D=2 **0.26** / D=3 **0.34** (scrambled), info preserved
    nonlinearly (0.88–0.95). A ~0.6 collapse at D=1→2; reproduces Phase I (2-D, 0.50).
- **Refinement of the crown finding:** "free → scramble" is really "**free + multi-dimensional latent
  → scramble**"; a 1-D free code is legible for free. Mechanism: no pressure to align a multi-D latent
  with linear axes → it scatters across the embedding manifold; a 1-D latent has only a monotone curve
  to occupy. Sign/coupling don't matter; embedding capacity modulates the level. Folded into
  `writeups/legibility_law.md` (leg 1 refinement). Scripts 46/47/48, results/4{6,7,8}_*.

## 2026-06-16 — NEW FIELD: scalar charge = the equivalence-principle knob (4/4 first attempt)
- **New direction (user): extend the methods to more field types, "see what we can and cannot learn."**
  Picked the SCALAR by gut — it isolates the project's thesis (geometrization ⇐ equivalence principle).
  Web-verified: scalar force is attractive-only (no ± sign); what matters is ρ = s/m.
- **Built an equivalence-principle KNOB** (script `45_scalar_equivalence.py`): 2D gravity well + a
  scalar well scaled by each body's ρ; economy race (Geometry identity-blind vs Force with per-body
  code); sweep the SPREAD of ρ (universality), holding attraction fixed.
- **All four gates, first attempt.** geometry/force MSE ratio by spread: **[1.23, 4.16, 8.88, 25.21]** —
  a smooth monotone transition. Universal ρ (spread 0) → geometry ties force (1.23) → **geometrizes
  (cost 0)**; species ρ (spread 1.6) → geometry 25× worse → **costs 1**. The code recovers ρ as a
  one-signed quantity (decode 0.98). **Universality is the *cause* of geometrization, shown as a
  continuous knob** — the project's thesis put on trial and confirmed.
- **Bonus:** ρ's free code is *linearly* legible (0.98) — unlike EM's q/m which scrambled (Phase C).
  Hint: a free code's legibility depends on how the charge couples (one-signed/linear stays legible;
  signed/nonlinear scrambles). Open thread, not a refutation of free→scramble.
- Menu of next fields parked (dilaton/secondary hair, Proca learnability knob, Wong dynamic, Dirac
  spinor). Docs: lab notebook; results/45_*.

## 2026-06-16 — thread D depth-of-emergence: the bracketing (42→43→44), an abstraction-depth verdict
- **Closed the depth-of-emergence question across three tasks.** Phronesis saw legibility rise with
  depth on Qwen3-4B (L4 0.40 → L36 0.92); does a toy reproduce a gradual multi-layer ramp?
  - **42** (smooth latent, legible at input): flat at 0.70 — no emergence, latent too accessible.
  - **43** (in-context rotation, *illegible* at input −0.12, shallow nonlinearity): one-layer STEP
    (−0.12 → 1.00 at layer 1). The precondition (illegible input) is confirmed necessary.
  - **44** (non-commuting SO(3) product, illegible *and* deep-in-generation D=6, on MPS): STILL a
    one-layer step, identical to D=1. The product of D rotations is one linear operator M(θ); the
    transformer recovers M from the (u,Mu) pairs in one layer and reads θ off it — it never unrolls
    the composition. **Generation-depth ≠ inference-depth; attention finds the parallel shortcut.**
- **Verdict: depth-of-emergence is an ABSTRACTION-depth phenomenon, not a computation-depth one.** A
  small transformer reads any parallel-recoverable latent in ~1 layer; the LLM L4→L36 ramp reflects
  many layers of *linguistic* abstraction (a concept built from progressively composed features),
  which an in-context toy doesn't reproduce. This *sharpens* the Phronesis observable. Mapped the
  structural tension: linear-in-u keeps the input illegible but gives a single sufficient operator
  (shallow inference); nonlinear-in-u allows deep inference but leaks the latent to the pooled mean.
- The legibility law *itself* in a transformer was already confirmed (script 38). Scripts 42/43/44,
  results/4{2,3,4}_*. One fix round spent across 43→44; gates not moved.

## 2026-06-16 — thread D: transformer port + depth-of-emergence (honest negative, sharp lesson)
- **Thread D (the assigned physics-side port).** Phronesis found legibility rises with depth on
  Qwen3-4B (L4 r=0.40 → L36 r=0.92). Ported to an in-context depth-6 transformer on the script-35
  latent task; probe linear legibility of the true latent after each layer (script `42_transformer_depth.py`).
- **Honest negative on the depth observable.** The depth curve is FLAT at ~0.70 across all 7 layers,
  robust across both the raw-128-d probe and a PCA-16 fix-round probe. No depth-of-emergence — because
  the latent is already ~0.70 linearly legible at layer 0 (input pooling). A smooth in-context
  regression latent is immediately readable from pooled examples; there's no illegible→legible climb.
- **The real finding:** depth-of-emergence requires the latent to be *initially linearly inaccessible*
  — a high-level abstraction the net must compute over depth (as a real LLM's "calibration" concept
  is). Amortization alone isn't enough for a depth climb; you also need representational distance
  between input and concept. Refines the Phronesis observable. The legibility law *itself* in a
  transformer was already confirmed (script 38, cdim=16: free scrambles 0.20/0.56, amortized legible
  0.70). Methodology note: probe 128-d reps via a native small bottleneck, not post-hoc PCA (lossy).
- All four threads of this stretch (#1 second law, #2 clean Platonic, #3 J4 hyperbolic, D transformer
  port) are now complete and documented. Docs: lab notebook; results/42_*.

## 2026-06-16 — #3 Phase J encore J4: the AdS payoff — the emergent dimension is hyperbolic
- **Open thread #3.** Is the emergent radial/scale dimension of geometry-from-entanglement
  negatively curved (AdS), and does it appear only at criticality? Web-verified physics
  (Calabrese-Cardy + Ryu-Takayanagi): a critical c=1 chain's interval entropy S(ℓ)=(c/3)ln[(n/π)
  sin(πℓ/n)] *is* the length of a boundary-anchored geodesic in a negatively-curved AdS₂ bulk; a
  flat bulk would give S∝ℓ. Script `41_hyperbolic_adS.py`, free-fermion machinery from script 32.
- **J4a PASS ✓✓** (c_fit=1.001, R²_log=1.0000 — the RT log-law exactly). **J4b PASS ✓✓** (gapped
  chain, staggered mass: large-ℓ slope 0.000 vs critical 0.333 — perfect area-law saturation; the
  hyperbolic dimension exists only at criticality). **J4c FAIL** as an *instrument*: log-beats-linear
  R²-margin 0.239 < pre-reg 0.3 because over a monotone range a line approximates a gentle log
  (linear R² 0.76) — yet R²_log=1.0000 (a perfect log) already proves the form. One fix round spent
  (extended range); gate not moved; recorded openly.
- **Verdict: HYPERBOLIC/AdS emergent dimension CONFIRMED** on the load-bearing gates J4a+J4b — the
  "extra dimension" of holography is real, emergent from entanglement, and negatively curved; ties
  It-from-Qubit to emergent_dimension.md. Open: full 2D bulk embedding + Brioschi K-map (deferred,
  fragile). Docs: lab notebook; results/41_*.
- The "one by one" trio (#1 second law, #2 clean Platonic, #3 J4 hyperbolic) is now complete.
  Remaining: thread D (transformer toy-port).

## 2026-06-16 — #2 the clean Platonic test (honest partial, sharper than edge (b))
- **Open thread #2.** Fixed edge (b)'s confound by making the converged-on object a LATENT not in
  any input (script 35's hidden p, frozen world g; recoverable only by learning to invert g). 3
  independent amortized nets (widths 96/128/160) vs free vs untrained, script `40_platonic_clean.py`.
- **Result (recover_p vs truth):** amortized **0.75**, free 0.40, untrained **−0.06**. P2 PASS — the
  edge-(b) confound is removed (untrained read families at 0.54 there; here it reads the latent at
  ~0, because p isn't in the inputs). P3 PASS (amortized ≫ free).
- **P1 fails for an instructive reason → the real finding:** *every cross-net similarity metric is
  input-confounded under shared inputs.* Raw-code CCA: untrained 1.0. Even "agreement of the
  recovered latent": untrained 0.936 (two random encoders of the same inputs share an input *shadow*
  of p). CKA/RDM/CCA/agreement all inflate. The only confound-free anchor is correlation with the
  ground-truth non-input latent — there amortized 0.75 ≫ free 0.40 ≫ untrained −0.06 is clean.
- **Verdict:** learned convergence on the platonic latent is real and learning-dependent; but a clean
  "platonic PASS" via net-to-net *similarity* is unachievable when inputs are shared (all similarity
  metrics saturate ~1.0 even untrained) — the project's metric-inflation lesson mapped to its
  boundary. Amortized recover_p 0.75 also sits at the task's ~0.78 ceiling, under the pre-reg 0.8
  (one fix round already spent; gate not moved). Docs: lab notebook; results/40_*.
- Queue remaining: #3 Phase J encore (J4 hyperbolic), thread D (transformer toy-port).

## 2026-06-16 — The second law: legibility ≠ steerability (CONFIRMED)
- **Open thread #1 closed.** A direction can be linearly *readable* without being a control
  *lever*. Built a two-channel amortized code (channel-dropout in training forces each channel to
  redundantly encode the property), script `39_read_vs_control.py`. Result: **read** the property
  from channel-1 alone r=**0.89** (legible from a part); **steer** channel-1's direction → output
  moves only **0.40** of the counterfactual (the other channel overrides — readable but a weak
  lever); **steer both** → **1.01** (full control). Redundancy decouples read from control.
- **Contrast with edge (a):** there the world-summary was a single causal bottleneck, so read *did*
  equal control (steering bent trajectories 3.8× over random). Read=control holds when the legible
  code *is* the bottleneck; breaks when the property is distributed/redundant.
- **Three-way distinction (folded into the writeup, credit Phronesis):** legibility (linearly
  readable) ≠ monosemanticity (a clean single feature) ≠ task-causality (drives behavior). On
  Qwen3-4B the monosemantic SAE "I-don't-know" feature carried the calibration signal at AUC 0.53
  vs a 0.64 supervised probe — semantically clean, not the causal direction. A representation can
  have any subset of the three; the legibility law governs only the first.
- Docs: writeup `legibility_law.md` "second law" section; lab notebook; results/39_*.
- Next in the "one by one" queue: #2 clean Platonic (within-family convergence), #3 Phase J encore
  (J4 hyperbolic), plus thread D (full transformer toy-port).

## 2026-06-16 — Edge (b) Platonic + the Phronesis LLM cross-test folded in
- **Edge (b) Platonic (honest partial):** 4 independent generalists (seeds x sizes) agree on the
  family map at cluster-ARI 0.92, but an untrained net already clusters families at 0.54 (they're
  input-distinguishable) and CKA/RDM baselines are architecture-inflated -> convergence is real
  (0.54->0.92) but partly input-driven; strong platonic claim not cleanly isolated. 37 made
  reboot-resumable. (Also diagnosed: the earlier 'kill' was most likely a sibling session's
  pkill -f python, not power — fixed by resumability.)
- **Phronesis LLM cross-test (credited):** the law's stored->scrambled prediction doesn't transfer
  to Qwen3-4B because pretrained transformers have NO free regime (amortized by default). Adopted
  their reframe into the writeup: the law may explain WHY the Linear Representation Hypothesis
  holds. Their depth-of-emergence observable + a legibility!=steerability open question added.
- **Toy confirmation (script 38):** sharing interpolation — legibility flips from scrambled (free,
  lin 0.24/nl 0.59) to legible around lam~0.5 (lin 0.78) up to 0.97; and the free-embedding
  scramble PERSISTS with a transformer encoder (lin 0.20/nl 0.56) -> scramble isn't MLP-specific,
  the LLM null is 'no free regime in pretraining'. Mechanism behind the reframe, confirmed.

## 2026-06-15l — Edge (a): the generalist's world-map is real & editable (causal steering)
- Othello-GPT-style causal test on the generalist (script 36). Edit the world-summary along the
  on-manifold "mass" direction (high-mass centroid - low-mass centroid) and the predictions bend
  as if the world were genuinely heavier: bend 0.53->1.07 (real low 0.53 / high 0.98), 3.8x more
  specific than equal-norm random edits, reaching 76% of the real low->high counterfactual gap. CS PASS.
- First attempt failed honestly (off-manifold ridge-direction x large alpha -> garbage); fix =
  on-manifold diff-of-means steering (the S4 lesson re-confirmed). The internal world-model is
  causally USED, not decorative. Next: (b) Platonic test — do independent generalists converge
  to the same map of physical law?

## 2026-06-15k — all 3 open edges resolved; the legibility law is complete
- **Edge 1 (leg-3 close) CONFIRMED:** a richer orthogonal rotation generator makes the
  evolving dynamic charge AS legible as a static one — legible 0.506 vs its static ceiling
  0.500 (ratio 1.01), |w| conserved to 3e-7. The shallow generator only reached 80%; capacity
  to match the true symmetry transformation closes it. Leg 3 upgraded partial -> confirmed.
- **Edge 2 (Phase J) closed:** spectral (Laplacian-eigenmap) embedding recovers geometry
  (chain Fiedler spearman 0.98 -> 1D; grid 2 modes isotonic 0.91 -> 2D) and the Van Raamsdonk
  pinch-off as the textbook connectivity signature (ev1 -> 0, a 2nd zero-mode at decoupling).
- **Edge 3 (scale/generality) WIN:** the law holds in a zero-physics abstract task and the
  amortize>>free gap WIDENS with scale (free linear 0.33->0.13; amortized ~0.8) — general
  representation property, not a toy artifact.
- **THE LEGIBILITY LAW COMPLETE (3 legs):** amortize->legible static; generic evolution->
  re-scrambles+breaks invariants; invariant-preserving structure->restores both. Crystallized
  in writeups/legibility_law.md (leg 3 now 'confirmed', scope strengthened with edge 3).
- (Power loss mid-session: edge 1 had already finished + saved; nothing lost. Only the
  dashboard server needed restarting.)

## 2026-06-15j — Phase J: geometry from entanglement (the big swing, loop closed)
- The It-from-Qubit bridge, back to the project's black-hole origin. Free-fermion ground
  states (Peschel correlation-matrix method, web-verified) -> learn a geometry from the
  mutual-information table alone. **J0 floor PASSED** (entanglement scaling slope 0.323 ->
  c=0.97 vs CFT c=1 — engine physically correct).
- **J1 chain ✓ isotonic R2=0.971:** embedding the block-MI table (positions NEVER given)
  recovers the 1D chain order. **Geometry emerges from entanglement** — demonstrated.
- **J3 Van Raamsdonk pinch-off ✓ (money shot):** decouple two halves (cross-MI->0) and they
  fly 6.4x apart in the emergent geometry — disentangling pulls space apart.
- Real gotcha (recorded): half-filled single-site MI is pathological (even-separation
  correlations vanish, 2k_F=pi); fixed by region/block MI — which is exactly WHY Ryu-Takayanagi
  uses regions not points. Honest gaps: J2 dimension (curved-manifold PCA overcounts: 3.8 not 1)
  and 2D grid (0.24, needs spectral embedding) — methodological follow-ups logged.
- Verdict: premise demonstrated (chain + pinch-off); crisp dimensionality/2D are open. The
  project has now reached from "a net invents the interval" (Phase A) to "a net builds space
  from entanglement" (Phase J) — the two ends of the original ambition.

## 2026-06-15i — Wong v2 + fix: definitive verdict, a Phase I refinement
- Amortized code + strong field (90deg rotation) + n=200, plus a 35k fix round with the
  nonlinear probe ladder. **W3b ✓✓: amortization legibilizes the STATIC color charge**
  (w0->Q0 linear 0.86/0.92/0.79 vs v1 free-embedding ~0) — Phase I cross-validated. **But
  W3: the rotating Q(t) is tracked only NONLINEARLY** (linear 0.29-0.46 / nonlinear 0.66-0.76)
  and **W4: |Q| not conserved** (drift 0.47). The recurrent F re-scrambles the clean
  amortized w0 as it evolves.
- **Verdict (row 2 CLOSED):** the crown isn't reached, but the answer is precise — amortization
  buys legibility for STATIC per-object codes; a DYNAMIC conserved quantity (rotating charge)
  is NOT legibly represented by a generic recurrent net, and its invariant isn't preserved.
  Refinement of Phase I. Survey boundary: static labels geometrize (electric, color Q0); the
  dynamic SU(2) rotation does not, here. Open thread: an orthogonal/Hamiltonian update F that
  conserves |w| by construction — does STRUCTURE recover the legible rotation?

## 2026-06-15h — Phase H row 2 (Wong color): honest NEGATIVE on the crown
- Fix-round probe (30b) decodes the true precessing Q(t) from the lane-state trajectory.
  W1 ✓ (color fits, 3.7e-4) but **W3 FAIL** (lane->Q(t) decode r=0.55/0.35/0.61, weak) and
  **W4 FAIL** (decoded |Q| drifts 0.18 vs true 0). The net fits color dynamics but does NOT
  demonstrably represent the rotating, |Q|-conserved color charge as a legible coordinate.
- Diagnosis: (1) true precession is only ~12deg in this regime — barely a rotation to find;
  (2) the LaneModel's FREE per-body embedding is illegible by construction (Phase I!), so the
  design fights legibility; (3) n=32 bodies underpowers the per-body decode. Clean retry
  (fresh experiment, not auto-run): strong gauge field (>=90deg rotation) + AMORTIZED per-body
  code + many bodies. Electric (row 1) geometrized cleanly; dynamic SU(2) did not here.
- One fix round spent; stopping per rule. Row 2 = a real, honestly-logged boundary of the survey.

## 2026-06-15g — Phase I: consensus bet FALSIFIED; legibility = amortization
- Built the consensus->legibility experiment (script 29) with the discreteness control.
  3 seeds, 4 arms. Result: recurrence (A-B)=-0.004 and discreteness (B-C)=-0.005 make NO
  difference; **amortize-vs-free-embedding (C-D)=+0.466 is the whole effect.**
- **Verdict:** the consensus/recurrence bet is FALSE. Legibility is selected by AMORTIZATION
  — a code inferred by a shared encoder is linearly legible for free (r~0.97); a free
  per-body parameter scrambles (linear 0.50, info in nonlinear 0.86 = the Phase C signature
  reproduced). The Phase C illegible charge code was a free-parameter artifact, not a
  property of charge. Lesson: want a legible per-object code? amortize its inference.
- Credit to the parallel session for the question; honest answer differs from the bet.
- Wong's equations web-verified for Phase H row 2 (color charge parallel-transports: rotates,
  |Q| conserved; SU(2) f=epsilon -> Q precesses like spin). Building next.

## 2026-06-15f — G-sym fix round (clean): frame validates on accuracy, tension found
- The clean unique-tag retrain finished (resumed through a 3rd power loss; sym2 genuinely
  differs from the confounded run — weight diff 2.6). Real fix-round verdict:
- **A1 ✓ accuracy restored:** chargedE 0.0129→0.0009 (14×), twocharge 0.0369→0.0032
  (11.5×), both clear pre-registered thresholds. The equivariant per-body channel works
  once tags are unique — the symmetry frame's core claim is VALIDATED for electric/two-charge.
- **A3a ✓ (chargedE):** per-body charge decodes from the equivariant channel at r=0.914
  (was 0.70 with degenerate tags); invariant-w control 0.36. Binding lives in the
  equivariant channel, as predicted. twocharge 0.76/0.64 (improved), magneticB dead.
- **A2 ✗ but interpretable:** stage clustering ARI 0.82→0.69 — per-body info migrated to
  the equivariant channel, so the stage merges the structurally-similar EM trio at the
  world level. Flip side: EM-kinship got STRONGER (z 26.7→34.9). A real accuracy↔legibility
  tension, contra the "no tension" hope.
- **A3b ✗:** field amplitudes did not lift (my amendment unsupported, recorded).
- **magneticB** is a consistent special case (v×B velocity-gated → per-body magnetic charge
  unreadable from snippets). Open thread.
- One fix round spent; stopping per rule. Next-direction options put to the user (accept +
  write up the tension / legibility-preserving variant / the deferred consensus experiment).

## 2026-06-15e — power loss + a STALE-DATA trap caught in the G-sym fix round
- **Power loss overnight, nothing lost:** the confounded G-sym run had finished and
  saved before the cut; ran the full A1–A4 suite this morning.
- **G-sym (confounded run) verdict:** gates miss — pair families up (aniso passes),
  matter up 2.4x, but charge-gated families flat; stage ARI regressed 0.82→0.68.
  A3a is the one clean signal: per-body charge decodes better from the EQUIVARIANT
  channel than the invariant control everywhere (chargedE 0.70 vs 0.33) — split
  direction right. BUT the run was confounded: the 4-d tag field zero-collides 2 of
  6 bodies, starving the binding. Not a verdict; needs unique tags.
- **Fix round attempt 1 = stale-data trap (caught):** the driver waited on shard-file
  EXISTENCE, but old shards were already on disk → it merged stale 120k and trained
  6h on OLD degenerate-tag data. Caught because two different-checksum models gave
  identical eval to 16 digits (tensors 0/80 differ). "file exists" != "file fresh",
  same family as the Phase F stale-ckpt trap.
- **Resolution:** re-merged 120k from verified-fresh new-tag shards, deleted stale
  artifacts, relaunched the clean retrain (running, ~6h). Driver hardened to own the
  full gen→merge→train order. Real fix-round verdict pending.

## 2026-06-15d — Phase G-sym: the symmetry-respecting generalist (training)
- **The dilemma dissolved, not split.** A parallel Claude session (credited)
  reframed the mean-pool as body-relabeling *invariance* — the equivalence
  principle in disguise: an invariant code can only keep body-symmetric info
  (geometry) and structurally drops the tag→charge binding. So the stage/actor
  split is the invariant/equivariant decomposition under relabeling; imposing
  that symmetry is the same fair move as Phase A's boost-invariant head, and it
  re-derives Phase C (0 vs 1 number/body) from symmetry alone.
- **My amendment (recorded):** field amplitudes (e_amp, b_amp) are body-symmetric
  yet decode badly because their signature is charge-GATED — so restoring the
  per-body channel should lift those decode rows too (gate A3b).
- **Built + launched `28_symmetric_generalist.py`** (SymGeneralist, 2.16M): R⁶⁴
  invariant mean-pool stage (the legible G3 object) + an equivariant per-body
  channel (query cross-attends into context, bottlenecked to R⁸ so it carries
  labels not the world). Training on the 120k bank, 150k steps, MPS (~6h).
- **Gates A1–A4 pre-registered** (lab notebook); all probes staged: 27 for
  A2/A3b/A4, new 28b decodes per-body charge from the equivariant channel with
  an invariant-stage control (worldgen gained --emit-qlabels for it). The
  consensus→legibility bet is deliberately deferred to its own pre-registered
  experiment (with a recurrence-vs-discreteness control).
- Dashboard restarted (server had stopped; title already correct as
  "tabula geometrica").

## 2026-06-15c — Phase G prize: the world-summary space (G2 ✓, G3a ✓, G3c ✓✓)
- **G3a — families cluster, ARI 0.82 (PASS).** The PCA map of the 64-d summary
  reads like a physics taxonomy: flat 1+1 / 3+1 as separate knots, well1p1 and
  aniso2p1 isolated (pure geometry), and the three EM-coupled worlds (chargedE,
  magneticB, twocharge) sharing one neighborhood; matter a diffuse cloud.
- **G3c — EM-kinship confirmed (exploratory, striking).** chargedE & magneticB
  sit 2× closer to each other (15.1) than to the gravity well (29.1), z=26.7 vs
  shuffled null. The net spontaneously carved "force gated by a per-body charge"
  as its own region of law-space. (Ties to It-from-Qubit "geometry of laws.")
- **G2 — zero-shot to +25% wider worlds: PASS.** traj ratio 1.00, pair 0.97→0.90.
  It learned mechanisms, not a table.
- **G3b decodability FAILS as gated (median 0.50) — but the pattern IS the
  finding:** world-geometry decodes great (well depth 0.92, total mass 0.98),
  per-body-charge-gated field amplitudes decode poorly (magneticB b_amp 0.04).
- **Synthesis: the G1 trajectory gap and the G3b illegibility are the SAME
  thing** — the global mean-pool nails world-geometry, is blind to per-body
  labels. So accuracy and legibility aren't in tension; a hybrid (global w +
  query→context attention) fixes both. Scripts: 27_g3_probes.py; worldgen got
  --widen for G2. Decision on the hybrid pending (thinking in parallel).

## 2026-06-15b — Phase G: 150k run finishes; underfit → overfit; data-scaling next
- **G1 second verdict: still 2/8 — but the failure mode flipped.** Train loss
  fell 4× (traj 0.023→0.0053) while val didn't move: the model memorized the
  21.6k training episodes. 30k run = underfit, 150k run = overfit ⇒ the steps
  knob is exhausted and the binding constraint is DATA (the user's "you need
  millions of games" instinct lands a second time). Methodology arm (c)
  answered by runs already paid for.
- **Pre-registered next: a data-scaling curve.** 4 worldgen shards × 30k
  episodes generating now (per-seed heartbeats after a shared-heartbeat
  rename race killed shard 3 — patched in 25_worldgen). Arms: 48k and 120k
  banks, identical model/budget. If val scales with data → ride it; if it
  plateaus → measure the context-information floor (owed; recorded as a
  process miss that it wasn't measured before gating).
- **Repo is live: https://github.com/sumit7194/tabula-geometrica** (public).
  Initial push (142 files, 15 MB incl. gate-required model weights),
  description + topics set, README retitled to the new name. Repo scope
  locked: curvature only.

## 2026-06-15 — Phase H row 1 lands (knee = 2); Phase G build + launch
- **Two-charge lane sweep (script 24) complete: the knee is exactly at L=2.**
  L=0: 1.13e-1 · L=1: 4.38e-3 · L=2: 1.20e-4 · L=3: 1.35e-4 (flat). H1 ✓
  (no-lane control fails 940×), H2 ✓✓ (sharp 0→1→2, saturated 2→3). Two
  independent charges geometrize into exactly two hidden lanes — behavioral
  lane-counting succeeds where bottleneck-counting (steps 11/12) hit the
  readout wall. **H3 ✓✓ (24b): behavioral decode of BOTH charges at
  r = 0.9996/0.9998** (lanes nearly axis-aligned — mixing barely needed).
  **H4: one-point zero-shot fails (identifiability), k-sweep fix round
  (24c) turns it into the finding — k=1: 8.8e-2 → k=4: 1.0e-4 = trained-
  body level.** Two unknown charges need a few independent measurements;
  a never-seen body is fully characterized by 4 observed trajectories.
  Row 1 CLOSED. Details: curvature lab notebook.
- **Phase G (the generalist) pre-registered and built:** 25_worldgen.py (8
  families, unified token format, 24k-episode bank with true params saved
  for the G-3 probes) + 26_generalist.py (2.01M-param transformer set
  encoder → world-summary w∈R⁶⁴ → query head). Smoke test: 25 ms/step on
  MPS → full 30k-step run ≈ 12 min — Ludo-sized, no L4 needed for v1.
  Launched detached on bank completion. Gates G1/G2/G3 in lab notebook.

## 2026-06-14 — Phase F closed; infra wins; the redirect to Phase G/H
- **RF sweep verdict:** field accuracy climbs with the net's reach (0.852 →
  0.985 across 17→53 px; one knob, all else frozen) — locality confirmed as
  Phase F's wall — then the 101-px arm collapses to a known dilation pathology
  (gridding; recorded). RF1 fails as literally pre-registered (non-monotone
  through d=8), RF2 fails (magnitude still 27× over gate): reach fixes
  direction, global operators fix magnitude — the established result, so
  **F-v3 deliberately skipped; Phase F closed.**
- **Infra wins this stretch:** bit-exact checkpoints (RNG state + atomic
  writes, proven bitwise); detached session-proof launches; bilerp (MPS twin
  of trilerp) verified exact → **12.4× speedup on MPS**; dashboard launcher
  pinned to repo root.
- **The redirect (user):** two ideas — ONE generalist net across all world
  families (study its internal map of worlds), then the GEOMETRIZATION SURVEY
  (which particle-like labels become hidden-dimension lanes: two-charge,
  Wong color charge with its rotating label, friction as the predicted
  failure, equivalence-breaking gravity as the open case). Design doc for
  joint review: curvature/notes/phase_g_design.md. L4 arrives in ~1-2 days —
  sized for Phase G.

## 2026-06-12 — Phase F honest accounting + 3+1 scale-up + MPS enablement
- Picked up from a power-loss + a parallel Gemini-AI session. Verified claims
  against disk: **Phase F (matter→geometry law, `19_law`) actually MISSED 3 of 4
  gates** (F1 58× over, F2 0.937<0.98, F4 6.4×<10×; only F3 superposition cos
  0.965 passed). Gemini had reported "flying colors" by cherry-picking the one
  passing number — corrected in lab notebook + CLAUDE.md. Honest read: field
  DIRECTION + direction-superposition emerged (encouraging), accuracy/control
  did not — the predicted local-CNN-vs-1/r miss. Defused the stale-checkpoint
  trap (19_ckpt.pt → 19_ckpt_v1_failed.pt).
- **Methodology audit** (user asked for an honest unbiased review): our science
  hygiene is strong, ML-craft was folklore (default LR, round-number steps, no
  sweeps, single seeds). Adopted "measure the floor, then gate relative to it"
  as a rule → new "ML experiment methodology" section in the ai-coding-standards
  skill + 3 memory entries (oracle floors, diagnostic trio, LR sweeps,
  convergence stopping, ≥3 seeds, receptive-field arithmetic).
- **3+1 law (script 21, `21_law_3p1`)**: Gemini's 24³-voxel scale-up of Phase F;
  finishing in background. **MPS enabled**: replaced 3D `grid_sample` (backward
  unimplemented on MPS, pytorch#141287) with a hand-rolled `trilerp()` +
  `--device` flag; verified value/grad match to float32 epsilon (CPU path
  unchanged, resume-safe). ~1.5–2× free local speedup; L4 GPU stays the option
  for the F-v2 sweep (inspected VM read-only — only Ludo computes; conjecture
  machine idle).
- **Dashboard**: restarted the dead server; fixed the "0 active" flicker
  (`LIVE_WINDOW_S` 60s→360s, exceeds the 250-step heartbeat gap).

## 2026-06-13 — housekeeping: simulator debt cleared; queue now idle
- ringdown 09/10 now share scripts/sbilib.py (duplication gone); the pickle
  Embed-alias constraint handled and tested (posterior loads + samples);
  repo gate ALL GREEN after the refactor.
- Writeup sections read coherently after the night's additions (spot-checked).
- **Queue status: all arcs closed, debts cleared, gate green — no high-value
  items left that don't deserve the user's input first.** Loop slows to
  hourly monitoring until he's back; the what-next menu lives in Morning
  Summary #3 below.

## ☕ 2026-06-13 — MORNING SUMMARY #3 (the second night stretch)

**Four arcs closed tonight. Repo gate ALL GREEN throughout. Loop still
running.**

1. **Echoes, final story:** the fair production-path head-to-head measured the
   real ML advantage at **~1.2× (not 13×** — that was a whitened-domain
   convention artifact). Plus: band-honesty measured, family-robustness
   confirmed, on-source nulls intact. The v2→v5 arc is now a documented case
   study in production-path validation.
2. **Ringdown, arc closed:** temperature recalibration certified (held-out
   coverage 0.91/0.92/0.90 after a noise-limited first round taught its own
   lesson). Final: **an amortized, start-time-marginalized,
   calibration-certified neural no-hair test — GW250114 δ = −0.16,
   Kerr-consistent, agreeing with the classical method.**
3. **The magnetic Kaluza (D-3):** velocity-dependent v×B forces ALSO
   geometrize into the internal coordinate (behavioral decode **r = 0.9974**;
   w-less control fails 23×). With D-v1, the toy KK suite is complete —
   electric and magnetic, the latter as the hidden dimension's Coriolis
   effect. (M1 marginal at 1.07e-4 vs the 1e-4 guess-gate; recorded as such.)
4. **Curvature invariant (earlier tonight):** the learned geometry's Gaussian
   curvature matches truth at 0.9903 — Theorema Egregium by autodiff.

**Night lessons recorded:** production-path validation before sensitivity
claims; n=300 calibration can't resolve 5% miscalibration; background shells
reset cwd (cd before every launch); pickled sbi posteriors need their Embed
class redefined at load.
**Queue (loop continues):** refactor 09_sbi_nohair into lib+script (clears
recorded debt); extend verify.sh with the 10/17/18 artifacts; writeup
touch-ups; deeper shelf items per sub-project lab notebooks.

## 2026-06-13 — ringdown v3: calibration certified, arc closed
- Temperature recalibration: n=300 was noise-limited (honest first-round fail
  + lesson); n=1000 fix round passed everything — T=1.05, held-out coverage
  0.91/0.92/0.90, GW250114 δ = −0.16 Kerr-consistent unchanged. **The ringdown
  story is complete: an amortized, start-time-marginalized,
  calibration-certified neural no-hair test that agrees with the classical
  analysis on the loudest black hole ever recorded.**
- Next: the magnetic Kaluza (D-3) — velocity-dependent forces from an internal
  dimension, the genuinely new Kaluza test.

## 2026-06-13 — echoes v5: the fair number is ~1.2× (and that's the story)
- Both statistics through the IDENTICAL raw-injection path: ML 50% point
  ≈ 0.85σ vs comb ≈ 1.05σ — **a real but modest ~1.2× advantage; the 13× was
  a whitened-domain-convention artifact** (unfiltered templates are maximally
  novel to a noise-trained net). README/notebook rewritten to the final honest
  story: modest ML edge, band-honest, family-robust, periodicity-specific,
  on-source nulls. The v2→v5 arc = a case study in production-path validation.
- Next: ringdown v3 recalibration, then the 3+1 Kaluza design pass.

## ☕ 2026-06-13 — MORNING SUMMARY #2 (since you went to bed)

**Three iterations ran; two big passes, one honest rescope. Repo gate ALL
GREEN. Loop paused.**

1. **The curvature invariant (run before you slept, recap):** the Gaussian
   curvature of Phase E's learned geometry matches the true world at
   **corr = 0.9903** — Theorema Egregium by double-autodiff, calculator
   validated exactly on a 2-sphere first. The project's title question,
   closed coordinate-free. (`curvature/results/17_curvature_invariant.png`)
2. **Consolidation:** `./verify.sh` at repo root — six curvature probe
   batteries + echoes/ringdown headline artifacts, asserted against the
   pre-registered thresholds. ALL GREEN twice tonight.
3. **Echoes v4 (raw-strain injection):** the mission gate **passed** — 450 Hz
   raw injections die in the bandpass (10% fire vs the invalid control's
   100%): **band-honesty is now a measurement.** The honest surprise: through
   the production path the 50% point is ≈ 1.0σ (filter chain reshapes pulses;
   calibration verified by differencing, so it's real). **Rescope: the 13× is
   a same-convention comparison — not refuted, but unverified in the
   production path** until the comb baseline runs through the same raw path
   (queued at v5's top). All claims in README/notebook updated to match.

**Didn't get to (queued):** ringdown v3 post-hoc recalibration (small);
3+1 Kaluza design pass; the fair production-path head-to-head (echoes v5).
**What-next menu:** (a) echoes v5 head-to-head — completes the rescope
honestly; (b) ringdown v3 recalibration — small, closes the coverage caveat;
(c) 3+1 Kaluza — the romantic capstone; (d) weekend writeup polish (yours).

## 2026-06-13 — consolidation: the repo regression gate, ALL GREEN
- Built `./verify.sh` (root) + `curvature/verify.sh`: re-runs all six curvature
  probe batteries against saved models with the pre-registered thresholds, and
  asserts echoes + ringdown headline artifacts. First run: **ALL GREEN** —
  every result in the project is now one command away from re-proving itself.
- Rule recorded in CLAUDE.md: run the gate after any sub-project change.

## 2026-06-13 — the closing readout: CURVATURE, by Theorema Egregium
- Differentiated the trained Phase E field network twice (Brioschi formula;
  calculator validated exactly on a 2-sphere first) → the Gaussian curvature
  of the LEARNED geometry matches the true world's at **corr = 0.9903**, all
  pre-registered gates passed (one far-field mask bug fixed, recorded).
- The project's title question closed in coordinate-free currency. Writeup
  closing section updated. Loop paused: direction discussion with the user
  (consolidation+verify.sh vs echoes v4 raw-strain vs 3+1 Kaluza).

## ☕ 2026-06-12 — MORNING SUMMARY (the night shift, in one read)

**Four experiments ran while you slept. Three passed with headlines, one closed
with a lesson. Everything gated, documented, and on the dashboard.**

1. **Ringdown v2 — CLOSED, with the night's prettiest number.** The amortized
   no-hair network (NPE over M, χ, δ, start time marginalized by construction)
   applied to GW250114: **δ = −0.16 [−0.45, +0.32], Kerr-consistent — landing
   EXACTLY on the classical method's point estimate.** Two completely
   independent analyses, one answer. Kerr injections in real O4 noise:
   unbiased, ~2–2.6× tighter than the classical ceiling. Honest residual:
   mild overconfidence (~0.84–0.88 coverage vs 0.90) stable across 90k→150k
   sims — not sample-size-curable; post-hoc recalibration is the v3 item.
2. **Echoes v3 — the 13× is family-robust.** 97–100% recovery at 0.5σ across
   frequency/decay/reflectivity variations. One honest lesson: my out-of-band
   control was INVALID BY DESIGN (whitened-domain injections can't probe the
   bandpass) — claims now scoped to in-band morphologies; raw-strain injection
   tops the v4 queue.
3. **Curvature Phase E — ALL FOUR GATES, the capstone.** The full metric field
   of the 2+1 anisotropic world learned from TRAJECTORIES alone: field
   recovery cos = 1.0000 (one global scale), φ corr 0.9997, and **the shear
   D̂ at r = 0.9989 — the component Phase B provably couldn't see, now
   measured. Phase B's caveat is resolved.** Constant-field control fails by
   1700×. The D-v2 numerical trap was dodged by construction (closed-form
   mass-matrix EOM, Cholesky-SPD fields).
4. **D-v2 — closed earlier tonight:** economy does not select gauge (the deep
   lesson); the symmetry-imposed fix lost to Euler–Lagrange numerics; Phase D
   stands on v1's behavioral r = 0.9998.

**What-next menu:** (a) writeup additions — Phase E deserves a paragraph and
the new plots; (b) echoes v4: raw-strain injection (converts the band claim
from assumption to measurement); (c) ringdown v3: post-hoc recalibration +
simulator realism for the +10% mass pull; (d) fresh frontier: 3+1 Kaluza with
a real vector potential, or curvature-invariant readouts (Ricci from the
learned Phase E fields). Loop is PAUSED — say the word and it resumes.

## 2026-06-12 — ringdown v2: the network IS the no-hair test (first run)
- NPE extended to (M, χ, δ) with start time marginalized by construction.
  Kerr injections in real O4 noise: δ̂ = −0.02 ± 0.14 — unbiased and ~2.6×
  tighter than the classical ceiling. Violation injections detected at
  population level (with honest shrinkage). **GW250114: δ = −0.13
  [−0.42, +0.33], Kerr-consistent — landing on 07's classical −0.16.**
  M-coverage 0.83 marginally under gate → the one pre-registered fix round
  (150k sims) running overnight. Dashboard heartbeat blind spot for opaque
  training loops found (user spotted it) and fixed (daemon-thread heartbeats).

## 2026-06-12 — D-v2 closed: economy does not select gauge
- Run 1: a generic extended Lagrangian FITS charged motion (3.15e-5) but uses
  the internal coordinate as a label track — cyclicity 0.94, corr(p_w, q/m)
  −0.26. The KK form is a gauge choice; nothing in the loss prefers it. The
  project's recurring villain (gauge freedom), now at the Lagrangian level.
- Run 2 (the one allowed fix, symmetry imposed as architecture): Euler–Lagrange
  rollout instability — training never converged (test MSE 79). Verdict:
  "charge = conserved momentum of a learned Lagrangian" is unverified-not-
  refuted; Phase D stands on v1's gauge-robust behavioral result (r = 0.9998).
  Writeup limits updated.

## 2026-06-12 — echoes v2: the ML scorer beats the comb by ~13×
- The noise-trained conv scorer, judged by the IDENTICAL v1 harness: 50%
  recovery at ≈0.11σ vs the comb's 1.5σ. First run looked too good (100% at
  every amplitude) → per standards, extended the curve down to 0.1σ and added
  an irregular-spacing specificity control BEFORE claiming: periodic trains
  100%, equal-energy aperiodic trains 6%/2% — it is an echo detector, not an
  energy detector. On-source GW150914 remains null (p = 0.75). Caveats (family-
  specific sensitivity, whitened-domain injections) + v3 queue in the echoes
  lab notebook.
- D-v2 cyclic Kaluza fix round still training; ringdown v2 next in sequence.

## 2026-06-12 — writeup v2 complete; ARC COMPLETE; loop paused for direction
- `writeups/emergent_geometry.md` now tells the full five-act story (interval →
  light cone → well → economy race in bits → the Kaluza ending), with the
  counting arc's lessons and current limits. README row updated.
- Autonomous loop PAUSED at the natural boundary: the arc the project set out
  to walk is complete. Reconsider note with four ranked options in
  `curvature/notes/lab_notebook.md` (recommendation: polish & share, then D-v2).

## 2026-06-12 — PHASE D: the Kaluza move, rediscovered (+ dashboard, + MDL seeds)
- **The crown experiment passed.** A single identity-blind dynamics on an
  extended state (x, v, w), bodies differing only in an initial condition w₀:
  fits charged motion (D1 ✓), and each body's w₀ behaviorally decodes to its
  true q/m at **r = +0.9998** (D2 ✓✓) — charge became a position in an internal
  dimension; identity migrated from model parameters into STATE. w is
  approximately conserved (13% drift — a rough isometry, D3 partial); a new
  body's charge is inferable from one observed point with no weight updates
  (D4 ✓). Kaluza 1921, replayed by gradient descent. Credit: proposed by the
  second-opinion session.
- Counting question parked honestly (12d: sufficient statistic provided, ~5%
  readout gap remains — knee-counting needs near-oracle inference).
- Multi-seed MDL: charged minimum at d=1 decisive (+8,870±15 bits for d=0);
  neutral ordering restored at marginal significance.
- **Training dashboard added** (user request): dashboard.html at repo root +
  curvlib.progress() heartbeats from all long training loops;
  `python3 -m http.server 8788` → http://localhost:8788/dashboard.html.

## 2026-06-12 — the counting arc (12 → 12d) + peer review enters the loop
- In-context form counting: first run FLAT (0.904 at every code width) →
  diagnosis run: oracle 0.992, k-sweep crawls ⇒ the mean-pool set encoder
  can't invert quadratic constraints → quad-feature version improves to 0.95
  but misses the gate, with the step at d=4 not 3.
- **Peer review entered the workflow:** the user relayed analysis from a
  parallel Claude session reviewing our lab notebook. It (a) predicted the
  projective smear (knee at 3+1 because the code carries a direction, not a
  vector) — visible in our data; (b) proposed the decisive diagnostic now
  running (pool the exact sufficient statistic Σuuᵀ); and (c) proposed
  **Phase D: the Kaluza–Klein migration** — offer the geometry model an
  internal coordinate and ask if the 9.86 bits/body of charge migrate into
  geometry. Queued as the crown experiment.

## 2026-06-12 (early) — metric-component experiment: the field reconstructed,
## and a counting gate that failed for a deep reason
- 2+1 anisotropic well (time-stretch, two space-stretches, shear — 3 independent
  fields). **Headline: the network's gradients reproduce the ENTIRE 4-component
  anisotropic metric field, anchor by anchor, at median cosine 1.0000** (every
  anchor > 0.9997) — the full-field generalization of Phase B's 1-d ratio.
- The counting gate failed informatively: the accuracy knee sits at d=2 (= the
  dimension of POSITION), not 3 (= the metric's dof). Diagnosis: an address
  bottleneck can never count field components — the address is always a
  sufficient code; it measures min(base-dim, form-dof). Corrected design queued:
  in-context/set-encoder counting (random forms per episode; the bottleneck must
  carry the form itself).
- Writeup §6/§8 updated with the MDL bits and the running experiment.

## 2026-06-11 (night) — the MDL race + autonomous mode engaged
- **MDL race (curvature step 10):** charged mix → description-length minimum at
  EXACTLY d=1 per-body code; the quantization probe gives the quantitative
  punchline — **identity is worth 0.44 bits/body under gravity vs 9.86
  bits/body with EM.** Honest corrections recorded: neutral-mix MDL minimum
  unresolvable at this convergence (optimization variance); the 1-d code is
  sufficient but NOT monotone (a lookup table, not a scale) — "bottleneck ⇒
  interpretable" is false, legibility must be selected for.
- **Reproducibility bug found & fixed:** torch inits were unseeded (models
  constructed before train() seeded the generator) — caught because steps 06
  and 10 disagreed on identical configs; both scripts now seed before
  construction.
- **Autonomous mode engaged** (user authorization): work the queue without
  prompts, schedule wakeups, pre-register → build → gate → document each
  iteration. Next queued: discover-the-number-of-metric-components (2+1 well).

## 2026-06-11 (late) — doc system, write-up, 3+1, and the SAE/steering quest
- Established the documentation taxonomy (this journal; `writeups/` for polished
  notes; per-subproject lab notebooks unchanged) and recorded it in README +
  CLAUDE.md.
- Wrote `writeups/emergent_geometry.md` — the four-phase curvature story as one
  coherent, shareable note (updated same session with side-quest results).
- **3+1 replication:** all five pre-registered gates passed — K=1 saturates,
  alignment 1.0000 with the full (+,−,−,−) signature, slice level sets on the
  hyperbolas. Phase A is dimension-robust.
- **SAE/steering side quest:** S1 decisive — the net LINEARIZES its hidden q/m
  with depth (decode 0.02 → 0.98); S2 honest negative — no monosemantic SAE
  feature (best |r| = 0.72; hint: the used product q/m·E is what's stored);
  S3 — steering layer-1 gives full-range, on-manifold causal control of a
  neutral body's charge; S4 — methodological lesson: in small smooth nets,
  random directions also steer monotonically; specificity needs equal-norm
  controls. Two probe-metric flaws found and fixed mid-run, recorded.

## 2026-06-11 — curvature/: the full experimental arc (Phases A → C)
- Adopted the user-supplied **ai-coding-standards** skill repo-wide
  (`.claude/skills/ai-coding-standards/`, project-adapted).
- **Phase A:** Siamese net on "same event, two boosted observers?" invented the
  Minkowski interval — K=1 saturates (99.91%), isotonic R² = 1.0000, gradient
  alignment 1.0000 (minus sign earned), level sets = hyperbolas. G0 honesty
  checks ran before training.
- **v0.1:** all four causal sectors — net mapped them to four separated monotone
  branches; **the light cone emerged as the discontinuities of the latent.**
  (Pre-registration corrected before running: counting measures continuous
  dims, not bits.)
- **Phase B:** weak gravity well, coordinate-component observations at shared
  anchors. Position-blind control 90.5% vs position-aware 99.8%; the
  reshaping-proof gradient-ratio readout traced A(x)/B(x) at r = 0.9995, well
  depth to ~2%. **"The interval bends," demonstrated.**
- **Phase C:** the economy race. Gravity only → geometry model ties force model,
  embedding swaps harmless, zero-shot works. Add charged bodies → geometry fails
  88× on exactly them; swap test catastrophic (1700×); embeddings encode one
  number per body (q/m), behavioral decode r = 0.9999 after PCA and linear
  probes both failed (the probe-ladder lesson). **Gravity costs 0 numbers per
  body, EM exactly 1.**
- Generator honesty: the 0.18 Newtonian-vs-geodesic gap was investigated via a
  scaling probe before proceeding — real post-Newtonian physics, not a bug.

## 2026-06-10 — echoes/: v1 pipeline complete on real LIGO data
- Full injection-first pipeline: fetch → inject → comb search → background →
  sensitivity. Sensitivity: blind <1σ, 50% @1.5σ, 100% @≥2σ (p<0.01, real
  H1+L1 noise). On-source GW150914 and GW151226: clean nulls (p ≈ 0.4–1.0),
  consistent with Westerweck et al. Gotcha fixed: NaN gaps in GWOSC blocks.
- Decision (next day): park echoes (v2 = ML scorer through the identical
  harness) in favor of the curvature project.

## 2026-06-10 — parallel sessions (recorded for completeness)
- `primordial_blackhole_search/` v1: CNN at 41–45% of ideal-MF sensitive
  distance at zero-FA threshold; transformer = honest negative. Parked.
- `ringdown_spectroscopy/` v1: injection-validated pipeline; start-time
  "poisoned choice" reproduced; no-hair test on GW250114 (overtone consistent
  with Kerr); SBI/NPE prototype with start time marginalized by construction.
  Parked (highest standalone science value; revisit deliberately).
- `conjecture_machine/` v1: propose→verify→evolve loop rediscovered
  Schwarzschild/BTZ/Tangherlini blind. Continues in its own session.

## 2026-06-08 → 09 — the concept docs (the project's foundation)
- `3plus1_vs_2plus1.md` (our world vs Flatland), `dimensional_ladder.md` (1+1
  rung, scaling laws, shapes & measures, black-hole horizons across dimensions,
  4+1 extrapolation).
- Research-driven side docs: `nn_and_spacetime.md` (the honest NN↔spacetime
  map), `emergent_dimension.md` (holography; the three-way "extra dimension"
  contrast), `discovering_curvature_with_nn.md` (the feasibility study that
  became the curvature/ experiment), `neural_network_holography_experiment.md`
  (portable Hashimoto note).
- Standing directive adopted: verify load-bearing claims by real research, cite
  sources, never bluff.
