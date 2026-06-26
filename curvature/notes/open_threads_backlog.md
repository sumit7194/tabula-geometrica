# Open threads & backlog — consolidated (2026-06-25)

A full sweep of every doc (CLAUDE.md, JOURNAL.md, README, notes/*, writeups/*, the 5 concept docs) for things NOTED to
try later but not done, cross-checked against scripts/ (latest 119) so nothing already-built is listed. Two halves:
**(I) on our current trajectory** (extends what we've built) and **(II) separate angles** (different lenses/paradigms).
Tiered by effort/readiness. Honest-negative "walls" that are RESULTS (don't re-grind) are listed last so we don't
mistake them for todo.

Done-since-noted (NOT listed below): J-thread hyperbolic/AdS + curvature (J4 41, J5 42); Dirac/spinor double cover
(98, 114); grid-cell torus (115/116); topological band SSH (117); emergent dimension RG (118); arrow of time (119);
black-hole GEOMETRY (Phase BH 60/63/64/65); info-return/Page curve (112).

---

## I. ON THE CURRENT TRAJECTORY

### A — quick, buildable now (analytic or <1h compute, no new infra)
- **2D Chern number** — finish topological band theory (117 did 1D SSH winding). A net discovers the Chern number =
  (1/2π)∫_BZ Berry curvature = integer, for a 2D Qi-Wu-Zhang/Haldane band; quantized, robust, bulk-boundary (chiral
  edge modes). Caps the topology/holonomy cluster fully. [CLAUDE: "2D Chern left as future"]
- **J2 dimension + 2D spectral grid** — the last loose ends of geometry-from-entanglement: PCA overcounts curved
  manifolds → swap to a spectral / persistent-homology dimension estimator; recover a 2D entanglement grid via
  spectral embedding. Cheap method-swap, not a new net. [scaling_backlog B-METH; field_guide §9]
- **Hierarchy H2 (Riemannian optimizer)** — script 89 hyperbolic distortion stalled at 0.61 (gate <0.5) on vanilla
  Poincaré SGD; retry with RiemannianAdam + burn-in LR. ~30 min, likely 2/3→3/3. [scaling_backlog A]
- **MDL M1 multi-seed** — neutral-mix MDL minimum unresolved (data-term variance); multi-seed average to resolve the
  d=0 minimum at significance. [scaling_backlog A]
- **Curvature-atlas open rows** — graph **Ollivier-Ricci** curvature (Ricci flow detects communities; negative on
  bridges) and **Turing-pattern** topology. Cross-domain "curvature beyond gravity" rows still open. [CLAUDE 88-90]

### B — architecture / compute bets (need L4 or a method change)
- **Phase F law via FNO / global operator** — THE biggest known wall: matter→acceleration-field; local CNN provably
  can't represent the 1/r long-range tail (overfit-one-batch failed at 0.047; Proca 53 isolated locality as the knob).
  A Fourier Neural Operator (global) is the literature fix. Oracle floor 1.2e-4 banked → feasible. [scaling_backlog B;
  fv2_roadmap]
- **Wong color-charge v3, fuller observability** — 106 (orthogonal SO(3) update) conserves |Q| exactly but dynamic
  legibility hit a PARTIAL-OBSERVABILITY ceiling (0.56-0.64 vs 0.89 static; trajectory-only sees Q·E along the path).
  Untried lever: give the learner richer observations (multiple field probes) so Q(t) is observable, then re-test.
  [CLAUDE Wong block; scaling_backlog B]
- **3+1 Kaluza with a vector potential** — extend the KK arc (Phase D electric + D-3 magnetic, both 2+1) to 3+1 with a
  genuine A_μ. [CLAUDE remaining-queue]
- **Larger G-sym generalist + explicit legibility regularizer** — the accuracy↔legibility tension (stage clustering
  0.82→0.69 as per-body info migrates out); needs scale + a legibility loss term. [scaling_backlog B]
- **hail-mary global PINN (Choptuik)** — the one untried lever the literature validates (arXiv:2511.15247): a GLOBAL
  PINN solve (physics-in-loss, no autoregressive rollout) sidesteps the rollout wall we proved (exp12). Different
  paradigm; re-confirms the structure-by-construction thesis. [hail_mary.md]

---

## II. SEPARATE ANGLES (different lenses / paradigms — not just more of the same)

### C — toward GR dynamics (the project's stated finale axis)
- **Time-dependent geometry → gravitational-wave toy** ⭐ — every learned geometry so far is STATIC. A moving/breathing
  well is the toy road to gravitational *waves*. Natural next on the curvature axis; novel for us. [field_guide §3,§9]
- **Horizon thermodynamics / S = A/4** ⭐ — Phase BH did horizon GEOMETRY (space↔time flip, singularity scaling), and
  112 did info-return, but the **entropy ∝ horizon-area** law — the user's *original* black-hole interest (Brian Cox /
  Bekenstein-Hawking) — was never built. Does a net discover S∝A from a horizon toy? Closes the loop to where the whole
  project started. [field_guide §9 "thermodynamic corner"; verify it's unbuilt before starting]
- **Relativistic-regime learning** — always stayed slow-motion (the PN gap was measured in Phase C, never crossed).
  Train discovery at relativistic speeds. [field_guide §9]
- **3+1 dynamical geometry** — combine 3+1 (done for Phase A) with dynamics (never combined). [field_guide §5]

### D — different discovery paradigms (not "given coordinates → readout")
- **Embodied RL agent in a curved world** ⭐ — does an agent that must NAVIGATE a curved world build the geometry into
  its world-model? Discovery via behavior, not given coords. A genuinely different paradigm. [field_guide §9]
- **Operational observers** — discover relativity from REALISTIC measurements (noisy clocks, finite-speed signaling
  between observers) instead of given (t,x). Deepens the "no fixed reference" theme (Cert V / 111). [field_guide §9]
- **Discrete / graph worlds** — does geometry emerge WITHOUT a continuum assumption? Ties to Ollivier-Ricci. [field_guide §9]
- **Curvature as the bottleneck itself** — make curvature the latent of a bottleneck task, not a post-hoc readout (as
  Phase E/17 did). [field_guide §9]
- **Communication game for gauge** — two nets must agree on a description of the same world; does the shared protocol
  converge to the legible gauge? (Reframe post-Phase-I: amortization, not agreement, was the driver — so test whether a
  shared *amortized* protocol selects legibility.) [field_guide §9]

### E — the nn_and_spacetime "six buildable toys" (sandbox; validate cross-doc claims)
- **Fisher / natural-gradient = GR metric** ⭐ — Riemannian SGD on a 2-param Gaussian; natural GD is reparameterization-
  invariant (the ML face of general covariance; Fisher metric = GR's g). The cleanest ML↔GR bridge, executable. [§5]
- **Huygens-tail PINN** — two tiny wave-equation PINNs (2+1 vs 3+1) showing a sharp signal develops a fading tail in 2D
  but stays sharp in 3D; validates dimensional_ladder §5. [§5]
- **Hashimoto depth = bulk dimension** — reimplement the AdS/CFT net recovering AdS-Schwarzschild from boundary data;
  depth becomes a spacetime dimension, weights become the metric. (Conceptual cousin of 118.) [§5]
- **Schwarzschild geodesic integrator**; **extrapolation-failure probe** (net trained on n=2,3 fails the discontinuous
  Weyl count at n=4 while the algebra succeeds) — smaller demos. [§5]

### F — concept-doc finales & write-ups (the weekend/consolidation track)
- **Consolidation synthesis** ⭐ — pull J5 + Cert V + 111 + 112 + the bounded legibility law + the certificate quintet +
  the holonomy cluster (AB/Berry/grid-torus/SSH) into ONE shareable narrative. The pile has outgrown its write-ups.
- **Roadmap Finale 2 / Finale 3 write-ups** — gravity-as-curvature (Theorema Egregium) and Kaluza-Klein, as polished
  docs (the original README roadmap). [README]
- **dimensional_ladder open threads** — 1+1 rung table, 4D chirality/lift section, visual companion diagrams. [3plus1_vs_2plus1 §10]

---

## III. WALLS THAT ARE RESULTS (do NOT re-grind — they're the science)
- D-v2 KK gauge: economy does NOT select the gauge (gauge-invariant loss) — a result, not a bug.
- Choptuik learned-emulator: the autoregressive rollout is the wall (exp12 global 0.99 vs rollout 0.50) — a result;
  the PINN global-solve (II-B) is the legitimate different paradigm.
- Form-counting ceiling: knee-counting needs near-oracle inference — documented ceiling.
- Impossibility certificates (84-87/101): Bell/chaos/gauge/contextuality/time — these ARE the results.
- Accuracy↔legibility tension (G-sym): a genuine tradeoff, not a capacity limit.
- "bigger is often worse for a discovery project (minimality IS the result)" — the meta-principle.

---

## Top picks (my recommendation, if asked)
1. **Horizon thermodynamics / S=A/4** (II-C) — biggest thematic payoff: closes the loop to the project's origin.
2. **Time-dependent geometry → gravitational waves** (II-C) — the natural GR-dynamics next step.
3. **Fisher/natural-gradient = GR metric** (II-E) — cleanest, cheapest ML↔GR bridge; high insight/effort ratio.
4. **2D Chern** (I-A) — quick, caps the topology cluster.
5. **Consolidation writeup** (II-F) — overdue; turns the pile into something shareable.

---

## ★ BIG-SWING DIRECTION (user-approved 2026-06-27, queued for LATER — after the SAE-legibility probe): THE REPRESENTABILITY FRONTIER

A future arc to unify the project's scattered LIMITS-of-discovery into one coherent theory of "what a net can / cannot
extract from observation, and why." The negative-space results are currently spread across ~15 scripts:
- Impossibility certificates: Bell / no-local-code (84), chaos / no-invariant (85), gauge / no-unique-law (86),
  KCBS / contextuality (87), Page-Wootters / no-observer-independent-time (101).
- The dynamic-legibility ceiling: Wong rotating charge tracked nonlinearly, not linearly (106/135 — clean negative).
- The no-fixed-reference walls: time (Cert V 101), frame (dS anchor 111).
- The spinor double-cover / sign-unobservable certificate (98 symbolic + 114 net).
- The legibility law itself (amortize→legible; free→scramble) is the POSITIVE side of the same coin.

GOAL: a single "DISCOVERY DIAGNOSTIC" that, given a system, PREDICTS whether a net can extract its law (integrable /
legible / emit) or provably cannot (chaotic / gauge / contextual / certify) — a theory of the discoverable that turns
the scattered negatives + the legibility law into one framework. The emit-or-certify engine (93/127) is the seed of the
predictor. Likely the project's most reframing single result. Tackle after the SAE-legibility probe lands.
