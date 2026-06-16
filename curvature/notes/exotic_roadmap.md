# Exotic-physics roadmap — discovery problems beyond black holes

**Vision (user, 2026-06-17):** stop orbiting black holes. Our method — *a net discovers hidden
structure / law / geometry from raw observation, and the cheapest (most shareable) explanation wins* —
is domain-general. Point it at the whole zoo of exotic physics, one by one. Recurring image: **sharing
is the compression principle behind geometry, gravity, and representations; entanglement sews emergent
space together.** Writeups are for weekends; weeknights are for connecting dots.

**Rigor (unchanged):** web-verify load-bearing physics BEFORE building; pre-register gates BEFORE
running; ONE fix round each; honest nulls are results; document (lab notebook + JOURNAL) + commit every
iteration. Each entry below is meant to be buildable cold.

## The framing result (done)
- **55 — Unification: geometry = amortized physics.** Universality (physics) and amortization (ML) are
  the SAME lever; one knob drives both the geometrize transition and the legibility split. The economy-
  race geometry model IS the amortized model; force IS the free code. This is the lens for everything
  below — every row is a *shared-vs-per-instance* question.

## Queue (one by one)

### DONE
- **56 — Dark matter vs MOND ✅** (shareability verdict). MOND = shared universal law; DM = per-galaxy
  halo. Universal anomaly → shared law fits AND zero-shot-predicts new galaxies (R²=1.000), DM can't →
  Occam+predictivity favor MOND. Per-system anomaly → DM needed. The zero-shot predictivity asymmetry
  IS the real epistemic argument. (Honest: MOND-generated data → shows the model-selection LOGIC.)
- **57 — Wormhole / ER=EPR ✅** (inverse of Phase J pinch-off). Adding entanglement between two far
  chain regions collapses emergent distance 4.44→0.37 (closer than neighbors) — a traversable shortcut,
  dose-responsive. ER=EPR demonstrated in our MI-geometry. Pure linear algebra.

### 58 Antimatter / CPT — DONE ✅ (3/3)
Net discovers charge conjugation: in a C-symmetric (odd-in-q) world, negating the inferred signed
charge code FLIPS the predicted force = the antiparticle (C-equivariance cos +0.95); in a C-violating
(even-in-q) world the cos slams to −0.97 (violation detected). Antimatter = a sign in an internal
coordinate. Original design below.
**Question:** does a net discover charge-conjugation (C) as a structure-preserving symmetry — the law
is invariant under flipping the charge, so matter and antimatter obey the same dynamics?
**Design:** charged bodies (charges q∈[−1,1], both signs = matter+antimatter) in a magnetic field
(a = (q/m) v×B, odd in q). Amortized net infers a signed charge code, predicts dynamics. C operation =
negate the code. Contrast a **C-symmetric** world (odd-in-q, magnetic) vs a **C-violating** world (add
an even-in-q term ε·q²·field). 
**Gates:** A1 inferred code is signed & decodes to q (legible). A2 (C as involution): in the symmetric
world, NEGATING a body's code reproduces its antiparticle's (−q) dynamics (match R²>0.9); equivalently
the learned model is C-equivariant: f(x,v,−code) ≈ −f(x,v,code). A3 (discovery of when C holds): the
C-equivariance error is ~0 for the symmetric world but LARGE for the C-violating world — the net
discovers C exactly when it is present. (Web-verify: EM is C-symmetric; Lorentz force odd in q; CPT.)

### 59 Fundamental particles / symmetry groups (Noether from data) — DONE ✅ (3/3, 1 fix round)
Net rediscovers conserved quantum numbers from allowed/forbidden reactions alone: learned functionals
span the true Q exactly (R²=1.000); the recovery-span knee COUNTS the symmetries (1-number recovers at
K=1; 2-number needs K=2, span 0.435→1.000). Fix round = N3 metric (span-recovery, not accuracy, which
saturates early). Noether, backwards. Original design below.
**Question:** from ALLOWED-vs-FORBIDDEN reactions alone, can a net recover the conserved quantum number
/ selection rule — i.e. discover the symmetry from observation?
**Design:** invent particles each carrying hidden quantum number(s) (e.g. a U(1) charge, or two numbers
like charge+baryon). Generate reactions (multisets in → multisets out); label ALLOWED iff the conserved
quantity balances (Σq_in = Σq_out), else FORBIDDEN (plus kinematic noise). Net sees only particle
identities + allowed/forbidden label. 
**Gates:** N1 net classifies allowed/forbidden > 0.95. N2 (the discovery): the net's learned per-particle
embedding recovers the conserved quantum number(s) — linear-decodes q (R²>0.95), and the decision rule
is "Σ over reaction ≈ 0". N3 knee: #conserved-numbers recovered = #imposed (1 vs 2). N4 generalize to
unseen reactions / particle counts. (Noether/representation-theory from data.)

### 60 Exotic / negative-energy matter (wormhole traversability)
**Question:** what kind of SOURCE does a stable, traversable shortcut require — does the economy push
toward sign-violating (negative-energy) matter? Ties to 57.
**Design (loose):** in a metric-from-trajectories or emergent-geometry setup, require a persistent
"throat" (a region of short emergent distance between far points) and ask what source/coupling sign
sustains it. Or: in 57's bridge, sweep toward a regime where holding the shortcut open needs the bridge
coupling to violate a positivity bound. 
**Gates (sketch):** E1 a stable throat requires the source's effective energy to go negative (sign flip)
in the maintained-shortcut regime; E2 positive-only sources cannot hold the throat (control fails).
*(Most speculative — design properly when reached; may become an honest null.)*

### 61 Entropic / emergent gravity (user-queued earlier)
**Question:** can a net discover an attractive FORCE arising from a purely statistical/entropic
substrate (Verlinde-style) — gravity as bookkeeping, not a field?
**Design (sketch):** a substrate with many microstates; an "entropy gradient" w.r.t. a probe's position;
test whether the net discovers an effective attractive force ∝ the entropy gradient (F = T ∂S/∂x), and
whether it geometrizes (universal) per the unification. Connects to It-from-Qubit (Phase J).

### PHASE BH — black-hole interior, mech-interp of the mind-benders (user's capstone pivot)
The return to black holes with the full toolkit: simulate the Penrose-diagram interior in a NN, then
probe what the space-time switch / singularity MEAN in the net. Each mind-bender -> a probeable quantity.
- **BH-1 — space↔time flip ✅ DONE (3/3, script 60).** A net learns the EF interval across the horizon
  (never told its location); learned g_vv crosses zero at r*=2.02 (located the horizon as the
  signature-flip locus); v-direction goes timelike (out, g_vv −0.59) → spacelike (in, +0.99). The
  space↔time swap = the learned metric's signature flip.
- **BH-2 — the singularity ✅ DONE (3/3, script 63).** From the net's learned g_vv(r), curvature
  R=-g_vv''=-4M/r^3 read via autodiff: FINITE at the horizon (R_hat(2M)=-0.50, corr 1.000 → smooth
  coordinate flip, not a singularity) but DIVERGES ~1/r^3 toward r→0 (124× blowup → real singularity);
  causal structure SPACELIKE — outgoing-null escape flips +0.25 outside → -0.49 inside (trapped) → r=0
  is an unavoidable future = "a time, the end of time." Original design below.
- **BH-3 — charge (Reissner-Nordström) ✅ DONE (3/3, script 64).** A net learns g_vv(r,Q); from its
  learned metric: TWO horizons for Q=0.8 (learned [0.40, 1.63] vs true [0.4, 1.6] — outer + inner/Cauchy);
  charge makes the singularity TIMELIKE — g_vv(0.2)=−7.0 for Q=0.8 (r spacelike near 0 = avoidable) vs
  +9.0 for Q=0 (spacelike/unavoidable). Charge → a second horizon + the singularity flips spacelike (end
  of time) → timelike (avoidable). C2 = the Q→timelike relation the sister glass-box analyzer offered to
  verify. **PHASE BH interior-physics trilogy COMPLETE (flip + singularity + charge).** Original design below.
- **BH-4 — scale up + hooks (deep mech-interp).** A larger net; install hidden-layer probes — find the
  internal "inside/outside-horizon" feature, the rotating timelike direction; steer it (does forcing
  the feature flip the predicted causal structure?). The proper mech-interp the proof-of-concept enables.

### FUTURE / PARKED — the QFT / Standard-Model lens (user idea, 2026-06-17, after a Feynman QFT lecture)
The dream: a general model spanning the Standard Model's field zoo (quarks/leptons = massive matter
fields; photon/gluon = massless force carriers; W/Z = massive; Higgs = scalar; gravity = the open one,
massless graviton, couples universally) — and from it, insight into gravity and its quantum connection.
**Honest hard limit (banked so we don't chase a mirage):** a net CANNOT learn quantum gravity — there is
zero data in its regime (Planck scale) and no agreed theory to generate training data; reproducing the
known SM+GR is not discovering what isn't in the data. **Two REACHABLE, on-mission versions instead:**
1. WHY gravity is the odd one out (structural): the graviton couples UNIVERSALLY to all energy-momentum
   (equivalence principle) -> it becomes the geometry/arena; EM/strong couple to SPECIFIC charges -> stay
   forces. That IS our shareability result (universal->geometrize, scripts 45/55). A generalist with
   gravity + SM field-types -> study, in its law-space, why gravity sits in the geometry basin. Build a
   toy "field zoo": massless/massive (= range/c, Proca knob 53) x universal/charge-coupled (= geometrize/
   force, economy race) x scalar/vector/tensor; read where gravity is isolated and what couples like it.
2. The actual quantum connection being pursued = emergent gravity from ENTANGLEMENT (It-from-Qubit /
   holography / ER=EPR), NOT quantizing the graviton. We've toy-demonstrated it: geometry-from-
   entanglement (Phase J), wormhole-from-entanglement (57), AdS-at-criticality (J4). Keep mining this.

### 62+ Wider non-physics area (stretch)
Point the whole machinery at non-physics relational data — chemistry (reaction space), networks, language
embeddings: does a meaningful geometry/invariant/symmetry emerge? The shareability principle as a general
theory of emergent structure. (Pick a concrete domain when reached.)
