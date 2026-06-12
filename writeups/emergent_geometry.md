# Teaching a neural network to invent spacetime

*How a 10k-parameter network rediscovered the spacetime interval, found the light
cone, traced a gravity well it was never told about, demonstrated why Einstein
geometrized gravity and not electromagnetism — and then rediscovered Kaluza's
century-old answer for electromagnetism too.*

*(Figures referenced live in `../curvature/results/`; full numbers and the raw
decision log in `../curvature/notes/lab_notebook.md`. All experiments run on a
laptop CPU in minutes.)*

---

## 1. The question

Gravity, in Einstein's picture, is not a force — it's geometry. Mass curves
spacetime, and "falling" is just travelling straight through a curved arena. The
question behind this project:

> Could a neural network, shown only raw observations and **never told that
> geometry exists**, be forced to *invent* it — the way Einstein was?

Not "train a net to output curvature" (that's supervised regression, and teaches
nothing). The real question is about **emergence**: arrange the data so that a
geometric concept is the *cheapest possible explanation*, starve the network's
internal representation, and check — with probes designed in advance — whether
geometry is what appears.

One known impossibility shapes everything: a representation can't emerge from
*nothing* (Locatello et al. 2019 — for any clean latent there are infinitely many
scrambled ones fitting identical data). Emergence needs a minimal, carefully
chosen bias, and ours is a single assumption baked into a Siamese architecture:
*"there exists some shared quantity that observers agree on."* Which quantity,
how many of them, its sign structure, and how it varies in space are all left for
the network to discover.

## 2. The method (same skeleton in every phase)

- **Task:** two observers each report raw coordinates of an event; a twin network
  (shared weights, tiny bottleneck of width K) answers *"same event or not?"*
  The only way to win is to compute something observer-independent internally.
- **Honesty checks before training (G0):** an oracle proves the task is solvable;
  a linear probe and a single-observation probe prove there's no shortcut and no
  label leak. Without G0, high accuracy would mean nothing.
- **Pre-registered gates:** every prediction written down before running. Where a
  prediction or probe turned out wrong, the correction is recorded openly (it
  happened twice — §6).
- **Reshaping-proof readouts:** the net is only pinned down up to a monotone
  relabeling of any invariant it finds, so gates use monotone fits, gradient
  *directions*, and behavioral tests — never raw value comparisons.

## 3. Phase A — the network invents the spacetime interval

Flat spacetime, future-timelike events, observers related by Lorentz boosts.
Raw `(t, x)` in; no engineered features (the minus sign must be *earned*).

**Results:** accuracy saturates at bottleneck width **K = 1** (99.91%) — this
world has exactly one invariant, and the net knows it. Nets *given* K = 2 or 4
leave the extra dimensions empty. The learned scalar is a monotone function of
`t² − x²` (isotonic R² = 1.0000); its gradient aligns with `(2t, −2x)`
everywhere (|cos| = 1.0000) — that sign pattern **is** the Lorentzian signature,
read out of trained weights; and its level sets lie exactly on the hyperbolas
`t² − x² = const` (`03_gates_k1.png`). A Euclidean control (alignment with
`2t, +2x`) fails at 0.43, refuting "it just learned distance."

This replicates Wetzel et al. (PRR 2, 033499, 2020) with stricter verification
than the original. A 3+1 replication (events in full `(t, x, y, z)`, rotations
joining the symmetry group) is in the lab notebook.

## 4. Interlude — the light cone appears on its own

Open the sampling to all four causal sectors (future, past, and the two
spacelike wedges) and the orbit space becomes four disjoint half-lines — still
one continuous dimension. K = 1 still suffices (99.3%), and the four-branch
portrait (`04_gates_mixed_k1.png`) shows *how*: the net assigned the four
sectors four separated monotone branches, and **the light cone shows up as the
gaps — the discontinuities of the learned latent.** Nobody mentioned causality;
the boundary between "can influence" and "cannot" emerged as the geometry of the
network's own representation.

## 5. Phase B — the interval bends

Now a weak gravity well: `ds² = A(x)dt² − B(x)dx²` with the standard weak-field
form `A = 1+2φ, B = 1−2φ`. Observers at a shared anchor report **map
coordinates** of displacements — a deliberate choice forced by physics: in your
own local free-falling frame spacetime is always flat (the equivalence
principle), so local-ruler data would contain no gravity at all.

**The control that must fail, fails:** a position-blind twin plateaus at
**90.5%** while the position-aware model reaches **99.8%** — those nine points
*are* the well, detected behaviorally.

**The readout that can't lie:** the net may relabel its number differently at
every position, so we read out a *ratio of its gradients* in which that freedom
cancels algebraically: `−(∂f/∂Δt / ∂f/∂Δx)·(Δx/Δt) = A(x)/B(x)`. Plotted across
position (`05_gates_well_k1.png`), the points read out of the trained network
trace the true well at **r = 0.9995**, recovering its depth to ~2% — a gravity
well the network was never told existed, drawn from its weights.

## 6. Phase C — why gravity geometrizes and electromagnetism doesn't

The historical puzzle: for a *single* falling body, "curved geometry" and "force
in flat space" are indistinguishable — Newton's force-gravity worked for 200
years. What broke the tie is **universality**: everything falls identically. A
force must be re-tuned per object; a geometry is one shared thing.

So: 40 bodies, trajectories through the well, and two rival models on identical
data and budget — a **geometry model** (shared rule; body identity
architecturally impossible to use) and a **force model** (a learned 4-d
embedding per body). Then a second world where half the bodies are charged and
an off-center electric field tugs them in proportion to q/m.

**Gravity only:** the models tie (MSE 4.7e-6 vs 6.2e-6). The **swap test** —
permute every body's embedding — changes nothing. The geometry model works
zero-shot on bodies it never saw. Identity is irrelevant: the equivalence
principle, measured.

**Add the charged bodies:** the geometry model fails **88×, on exactly the
charged bodies** (0.0853 vs 0.00097 on neutral); the swap test becomes
catastrophic (**1700×** degradation). And the force model's embeddings turn out
to encode **exactly one number per body — its q/m** — recovered at
**r = 0.9999** (`07_economy_charged.png`: every body on the diagonal).

> **The punchline of the whole project:** gravity costs **0 numbers per body**;
> electromagnetism costs **exactly 1**. Universality is the asymmetry that lets
> geometry absorb gravity — and only gravity. A trainable system, offered both
> explanations honestly, re-enacts Einstein's choice.

**Now in actual bits (the formal MDL race):** sweeping the per-body code size
d ∈ {0, 1, 2, 4} and computing a two-part description length, the charged world's
minimum lands at **exactly d = 1** (5,320 bits/body, vs 14,696 for geometry-only
and 6,028 for d = 4). And a quantization probe — how coarsely can you round each
body's code before predictions degrade — prices identity directly: **0.44
bits/body under gravity alone; 9.86 bits/body once electromagnetism enters.**
Two honest footnotes from that run: the neutral world's MDL minimum needed
seed-averaging to resolve (three seeds restore the expected ordering — minimum
at d = 0 with monotone growth — at marginal significance; the quantization
probe is the sharper instrument), and the winning 1-d code, despite fitting
perfectly, is a **lookup table, not a scale** (rank correlation with q/m only
0.30) — capacity pressure forces *sufficiency*, never *legibility*. It also
flushed out a real reproducibility bug (unseeded model inits), caught because
two scripts disagreed on identical configs.

**The probe-ladder lesson** (a finding in its own right, for the
interpretability-minded): the q/m information was *invisible to PCA*
(r = −0.12) and *invisible to a linear decode* (r = +0.02), yet provably used
(the swap test) and perfectly recoverable *behaviorally* (invert the net's own
simulated trajectories: r = 0.9999). Information can be present and load-bearing
while stored non-linearly — variance probes ✗, linear probes ✗, behavioral
probes ✓.

**Corrections recorded along the way:** the original v0.1 prediction ("the
bottleneck knee moves to 2") was wrong and corrected *before* running (counting
measures continuous dimensions, not bits); the original Phase C embedding probe
(PCA axis) was the wrong operationalization and was replaced by the behavioral
decode, with both failures kept in the record. A generator discrepancy (0.18 vs
full relativistic geodesics) was root-caused by a scaling probe before
proceeding: real post-Newtonian physics, not a bug — the dynamics generator is
exact Newtonian gravity, the historically exact arena for this contest.

## 7. The closing act: the Kaluza move, rediscovered

Phase C left electromagnetism standing outside geometry — one stubborn number
per body. That is exactly where physics stood in 1921, when Kaluza noticed the
number *is* geometrizable if you buy one extra dimension: charged motion in
ordinary spacetime is **free motion in a five-dimensional spacetime**, with
charge-to-mass ratio as the conserved momentum around the extra (curled-up)
direction. The obvious question for our toy — proposed, fittingly, by a
*second* AI session reviewing this project's lab notebook — was: offered an
internal dimension, does a network spontaneously make the same move?

**Phase D setup:** one shared, identity-blind, one-step dynamical rule on an
*extended* state `(x, v, w)`, rolled out recurrently. Bodies differ **only** in
a learned initial condition `w₀` — one number entering as *state*, not as an
embedding consumed by the network. Trained on the same charged-mix
trajectories; `w` never supervised.

**Results (all pre-registered gates):**
- It fits charged motion at force-model accuracy — where the plain geometry
  model had failed 88×.
- **The migration:** each body's learned internal coordinate behaviorally
  decodes to its true q/m at **r = +0.9998** (`14_kaluza.png`). Charge stopped
  being a label and became a *place*.
- The net *approximately* conserves `w` along trajectories (drift ≈ 13% of the
  population spread) — a rough, imperfect version of the symmetry that makes
  Kaluza's momentum conserved. Honest partial.
- **The state-vs-embedding test:** for a body never seen in training, fitting
  the single scalar `w₀` from *one observed point* — no weight updates —
  predicts the rest of its motion. Identity became *inferable from motion*,
  exactly like a coordinate and unlike a trained embedding.

And the magnetic sequel: repeating the experiment in a 2-d world with a
**v×B field** — where the force depends on *velocity* — the internal
coordinate again decodes to the body's charge (r = 0.997). In real
Kaluza–Klein theory the magnetic force is literally the Coriolis effect of
the hidden dimension; the toy now shows both faces, electric and magnetic.

In MDL terms: the ~10 bits per body that electromagnetism cost in Phase C
didn't vanish — they moved from **model parameters into state**, which is
precisely where geometry keeps its per-body information (position, velocity).
The arc-completing sentence: **what universality geometrizes, an extra
dimension can geometrize too** — and a network under economy pressure finds
both moves, a century after physics did.

## 8. What this is and isn't

**It is:** a controlled demonstration — behind pre-registered gates, honesty
checks, and reshaping-proof readouts — that the central concepts of special and
weak-field general relativity (the interval, the signature, the light cone, a
position-dependent metric, and the geometrizability of *specifically universal*
forces) emerge inside a small network when, and only when, the data makes them
the cheapest explanation. Every phase is a *rediscovery in a toy*: the answers
were known, withheld, and recovered — the same epistemics as SciNet's
heliocentrism and Wetzel's interval, extended to curvature and to the
geometry-vs-force contest, which had not been done.

**It isn't:** new physics, a solution of Einstein's field equations (the well is
a hand-chosen data-generator metric; nothing here is gravitational *dynamics*),
or evidence about our universe. The 1+1 setting and the slow-motion regime are
choices for clarity; Phase D's result is a *dynamical-systems* statement (a
shared one-step rule), not yet a geodesic/metric one. The structural version
was attempted and closed honestly: a generic learned extended Lagrangian fits
the motion but **economy does not select the Kaluza gauge** (it used the extra
coordinate as a label track — the same gauge-freedom villain that haunted every
phase), and the gauge-fixed (cyclic) Lagrangian defeated our training machinery
(Euler–Lagrange rollout instability). So "charge = conserved momentum of a
learned Lagrangian" remains unverified-not-refuted, on the future-work shelf.
Caveats live in the lab notebook next to each result.

## 9. Where it goes next

- **The SAE side quest (now run — three findings):** Phase C manufactured a
  perfect specimen — a network provably storing one physical number (q/m)
  non-linearly, invisible to linear probes. Results: (1) the network
  **linearizes it with depth** (decode r: 0.02 in the embedding → 0.98 in the
  hidden layers — it must, to compute with it); (2) honest negative: a tuned
  SAE finds **no monosemantic q/m feature** (best |r| = 0.72; the information
  stays distributed, with a hint that the *used product* q/m·E(x) is what's
  stored); (3) **steering works**: adding the probe direction to layer-1
  activations sweeps a neutral body's effective charge across the full physical
  range (corr 0.999), staying on the physics manifold — with the recorded
  caveat that in small smooth networks random directions also steer somewhat,
  so specificity claims need equal-norm controls.
- **Counting the metric components (run, and honestly parked):** two genuine
  lessons survived four iterations. First, *you cannot count a field's
  components by bottlenecking position* — the address is always a sufficient
  code (a width-2 code matched a 3-component geometry because the world is
  2-dimensional). Second, the in-context fix (infer the geometry from example
  events through a bottleneck) is information-feasible but **knee-counting
  requires near-oracle inference**: even handed the exact sufficient statistic,
  the readout chain loses ~5% accuracy before code width binds, smearing the
  knee. A consolation finding en route: the network's gradients reproduce the
  *entire* 4-component anisotropic metric field of a 2+1 well, anchor by
  anchor, at cosine 1.0000.
- **D-v2 (attempted, closed):** the extended-Lagrangian version taught the
  final gauge lesson (§8) and lost its fix round to numerics; the behavioral
  result stands.
- **Phase E (run — all gates):** the full metric *field* of a 2+1 anisotropic
  world learned from **trajectories alone** — one shared pair of field
  networks (an SPD mass-matrix/metric and a potential) explaining many bodies'
  motion. Field recovery cosine 1.0000 (up to the one allowed global scale),
  potential correlation 0.9997, and the **shear component at r = 0.9989** —
  the very component the single-anchor Phase B provably could not pin, now
  measured by cross-position dynamics. A constant-field control fails by
  1700×. The earlier caveat list shrinks by one, the honest way: with a
  *measurement*, not a promise.
- **The closing readout (run — all gates):** differentiate the trained Phase E
  field network *twice* and compute the **Gaussian curvature** of the geometry
  it learned — the coordinate-free invariant of Gauss's Theorema Egregium, the
  one number no relabeling can fake. It reproduces the true world's curvature
  map at **corr = 0.990** (`17_curvature_invariant.png`), with the calculator
  first validated exactly on a 2-sphere. The project's title question, answered
  in its own currency: *a network watched things move, built a geometry, and
  that geometry has the right curvature.*

---

*Repo: the `curvature/` sub-project. Methods: `curvature/README.md` (decisions
table). Raw log: `curvature/notes/lab_notebook.md`. Background and feasibility
study: `../discovering_curvature_with_nn.md`. Key prior art: Wetzel et al., PRR
2, 033499 (2020); Iten et al., PRL 124, 010508 (2020); Locatello et al., ICML
2019.*
