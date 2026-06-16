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

### NEXT — 58 Antimatter / CPT
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

### 59 Fundamental particles / symmetry groups (Noether from data)
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

### 62+ Wider non-physics area (stretch)
Point the whole machinery at non-physics relational data — chemistry (reaction space), networks, language
embeddings: does a meaningful geometry/invariant/symmetry emerge? The shareability principle as a general
theory of emergent structure. (Pick a concrete domain when reached.)
