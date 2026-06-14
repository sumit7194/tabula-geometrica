# The Curvature Project — Complete Field Guide

*Everything we did, Phases A→E through the generalist arc (F-closed, G, the
legibility law I, and the H geometrization survey) and all side quests: what each
experiment was, how it actually worked, what it found, what surprised us, and —
most importantly — the threads we noticed but never pulled. Written plainly, for
thinking with. (The polished narrative is `emergent_geometry.md`; this is the
workshop version.)*

---

## 0. The one idea underneath everything

Every experiment has the same skeleton:

1. **Build a toy world** with known physics (we always know the right answer —
   that's what makes claims checkable).
2. **Show a network only "adjacent observables"** — raw coordinates, trajectories,
   clock readings. Never the metric, never the law, never the concept.
3. **Starve the network's internal representation** (tiny bottleneck) so the
   *cheapest sufficient code* is forced to appear.
4. **Probe what appeared** with gates designed in advance — and designed to be
   immune to the net's freedom to relabel its internal numbers.

The recurring discovery: when the data is arranged so that a geometric concept is
the most economical explanation, the network invents it. The recurring villain:
**gauge freedom** — there are always many internal codes that work equally well,
and the gates must only ever test what survives relabeling.

---

## 1. Phase A — the network invents the spacetime interval

**Question.** Special relativity says all observers, however fast they move, agree
on one number between two events: `s² = t² − x²` (note the minus sign — that minus
sign IS spacetime). If a net is only asked "are these two observations the same
event?", must it invent `s²`?

**The world.** Flat 1+1 spacetime. An "event" = a displacement `(t, x)` from a
shared origin, restricted to the future timelike region (`t > |x|`) — chosen
because there the boost-orbits are labeled by *exactly one* number (proper time τ).
Sharp prediction: one latent should suffice.

**The data.** A "positive pair" = the SAME event as recorded by two observers
moving at different velocities (random boosts, rapidity up to 1.5 ≈ 0.9c). A
negative pair = two genuinely different events (τ differing by a margin — closer
than measurement noise isn't "different" in any learnable sense). 1% noise on all
coordinates. Crucially: **raw `(t,x)` inputs only** — feeding `t²` or `x²` would
hand over the answer.

**The model.** A Siamese twin: one tiny MLP `2→64→64→K` (tanh) applied to both
observations; the head says "same" iff the K-number outputs are close
(`logit = α − softplus(β)·‖z_a − z_b‖`). This *strict head* is the key design: the
only way to win is for the encoder itself to output a number all observers agree
on — an invariant. The symmetry lives ONLY in the data; the architecture knows
nothing about physics.

**Honesty checks BEFORE training (G0).** An oracle comparing true intervals gets
0.99 (task solvable); a linear classifier on raw coordinates gets 0.52 (no cheap
shortcut); a single observation predicts nothing (0.49, no label leak). Without
these, high accuracy would be meaningless.

**Results.** K=1 saturates at **99.91%** (K=2, K=4 add nothing — and the wider
nets left their extra latents EMPTY: PCA variance [1,0,0,0]). The learned scalar
is a monotone function of `t² − x²` (isotonic R² = 1.0000). Its gradient aligns
with `(2t, −2x)` everywhere — |cos| = 1.0000 — and that opposite sign on the space
part **is the minus sign, earned from raw data**. Euclidean control (is it just
distance from origin?) rejected at 0.43. Level sets of the latent lie exactly on
the hyperbolas.

**3+1 replication:** identical results in full `(t,x,y,z)` — three minus signs
earned, rotations add symmetry but no new invariants.

**Loose ends never pulled:**
- *Emergent minimality:* nobody forced K=2/4 nets to use one dimension — the
  strict head implicitly prunes unused latents. We noted it, never studied it.
- *How is the invariant assembled layer by layer?* (Your SAE/hooks idea — we did
  a version on Phase C's net, never on this one.)

---

## 2. v0.1 — the light cone appears as the latent's tears

**Question.** Open the sampling to ALL of spacetime — future, past, and the two
spacelike wedges (events too far away to influence). Now the orbit space is four
disjoint pieces. What does one scalar latent do?

**Result.** K=1 still suffices (99.3% — counting measures continuous dimensions,
not discrete labels; my pre-registered "knee moves to 2" was WRONG and corrected
before running — recorded). The portrait plot is the keeper: the net mapped the
four causal sectors to **four separated monotone branches**, and the gaps between
the branches sit exactly at the light cone. **Causality emerged as the
discontinuity structure of a learned representation.** Nobody mentioned cause and
effect to the network.

**Loose ends:**
- We never probed behavior *near* the cone (where the branches approach each
  other). What happens to nearly-null events? Is there structure in how the net
  handles the boundary?
- The net *chose* disjoint ranges over interleaving — why? Is that an optimization
  preference or a necessity? Never investigated.

---

## 3. Phase B — the interval bends (a static gravity well)

**Question.** In curved spacetime there's no global interval — there's a *local*
one at each point, with coefficients that vary from place to place (that variation
IS the gravitational field). Can the net discover position-dependence?

**The world.** 1+1 with metric `ds² = A(x)dt² − B(x)dx²`, `A = 1+2φ`, `B = 1−2φ`,
φ a Gaussian well (depth 0.15) — the standard weak-field form (verified against
the literature before building). Gravitational time dilation lives in `A`.

**The data.** Same-event pairs, but both observations are made at a SHARED anchor
position `x` (so position is context, never a label giveaway), and observers
report **map coordinates** of small displacements. That choice is forced by
physics: in your own free-falling frame spacetime always looks flat (equivalence
principle) — local-ruler data would contain NO gravity at all. Gravity is only
visible when comparing *here* against *there* on a shared chart.

**The model.** Same Siamese, input now `(x, Δt, Δx)` — position concatenated.
Plus the control that must fail: an identical net WITHOUT the position input.

**Results.** Position-blind control plateaus at **90.5%**; position-aware reaches
**99.8%** — those nine points are the well, detected behaviorally. The readout
that can't lie: the net may relabel its latent differently at every position
(per-anchor monotone freedom `h_x`), but in the gradient ratio
`−(∂f/∂Δt / ∂f/∂Δx)·(Δx/Δt)` that freedom cancels algebraically, leaving exactly
`A(x)/B(x)`. Plotted across position: **r = 0.9995 against the true well, depth
recovered to ~2%.**

**The built-in limitation (which later became Phase E's purpose):** from
single-anchor data, only the RATIO A/B is recoverable per position — provably.
Separating A from B needs data that *connects* positions.

**Loose ends:**
- Only static wells. **Time-dependent geometry was never tried** (a moving or
  breathing well; gravitational waves are exactly this).
- The well was hand-chosen, not a solution of any field equation.

---

## 4. Phase C — the economy race (why gravity geometrizes)

**Question.** For ONE falling body, "curved geometry" and "flat space + force" are
indistinguishable — that's why Newton worked for 200 years. The only tiebreaker is
the equivalence principle: *everything falls identically*. Can we make a trainable
system re-enact Einstein's choice?

**The world.** Bodies on trajectories through the well (slow-motion regime — the
historically honest one; our Newtonian generator was validated against full
relativistic geodesics via a scaling probe: the 0.18 gap at depth 0.15 shrinks
quadratically as the well weakens, so both integrators are right and the gap is
real post-Newtonian physics). Two versions: all-neutral (gravity only), and a
charged mix (half the bodies feel an off-center electric field ∝ q/m).

**The two rival models, identical data and budget:**
- *Geometry:* `MLP(x₀, v₀) → trajectory` — body identity architecturally
  impossible to use. "Motion is a property of the arena."
- *Force:* `MLP(x₀, v₀, embedding[body]) → trajectory` — a learned 4-number
  embedding per body. "Motion depends on what the body is."

**Results, neutral world:** dead tie (4.7e-6 vs 6.2e-6). The **swap test**
(permute all bodies' embeddings) changes nothing — identity is behaviorally
irrelevant. Geometry model works zero-shot on bodies it never saw. That IS the
equivalence principle, measured.

**Results, charged world:** geometry model fails **88×, on exactly the charged
bodies**; the swap test becomes catastrophic (1700×). And the force model's
embeddings? Each encodes exactly ONE physical number — the body's q/m — but
**non-linearly**: PCA on the embeddings is blind (r = −0.12), a linear decode is
blind (r = +0.02), yet inverting the net's own simulated trajectories recovers
q/m at **r = 0.9999**. The probe ladder (variance ✗ → linear ✗ → behavioral ✓)
became a standing lesson.

**The MDL sequel (formal bits):** sweeping per-body code size d ∈ {0,1,2,4} with a
real two-part description length: charged world's minimum at **exactly d=1**
(5,320 bits vs 14,696 for geometry-only); the quantization probe prices identity
directly — **0.44 bits/body under gravity, 9.86 bits/body with EM.** Honest
extras: the winning 1-d code fits perfectly yet is a *lookup table, not a scale*
(rank corr 0.30) — capacity pressure forces sufficiency, never legibility; and we
caught a real reproducibility bug (unseeded torch inits) because two scripts
disagreed.

**The SAE/steering side quest (your toolkit, pointed at this net):**
- *Linearization with depth:* q/m decode goes 0.02 (embedding) → **0.98 (hidden
  layers)**, held-out bodies — the net untangles its own nonlinear code where it
  needs to compute with it.
- *Honest SAE negative:* no monosemantic q/m feature (best |r| = 0.72; hint that
  the stored thing is the *used product* q/m·E(x), 0.78).
- *Steering works:* adding the probe direction to layer-1 activations sweeps a
  neutral body's effective charge across the full physical range (corr 0.999),
  staying on the physics manifold. Layer-2 steering barely works — steer
  *upstream* of where information is consumed.
- *Methodology lesson:* in small smooth nets, random directions also steer
  monotonically — specificity claims need equal-norm controls on span AND
  on-manifold-ness.

**Loose ends:**
- "Legibility must be selected for" — we never asked *what pressure* would make
  the learned codes interpretable. (A regularizer? A communication game between
  two nets? Open and interesting.)
- The probe ladder generalizes to LLM interpretability claims — never written up
  as its own note.

---

## 5. Phase D — the Kaluza move (charge becomes geometry)

**Question.** Phase C left EM as the holdout: 1 number per body that geometry
can't absorb. Kaluza's 1921 answer: it CAN, if you buy one extra dimension —
charged motion in d dims is *free* motion in d+1, with q/m as momentum around the
hidden circle. Offered an internal dimension, does a network spontaneously make
that move? (Proposed by your second-opinion session — peer review entering the
loop.)

**D-v1 (electric).** A single shared, identity-blind one-step dynamics on an
EXTENDED state `(x, v, w)`, rolled out recurrently; bodies differ ONLY in a
learned initial `w₀` — one number entering as *state*, not as a consumed
embedding. Results: fits charged motion (D1 ✓); **each body's w₀ behaviorally
decodes to its true q/m at r = +0.9998** (D2 ✓✓ — identity migrated from model
parameters into state, i.e., into geometry's ledger); w approximately conserved
along rollouts (13% drift — a rough isometry, honest partial); a NEW body's
charge is fit from ONE observed point with zero weight updates (D4 ✓ — identity
became *inferable from motion*, like a coordinate, unlike an embedding).

**D-v2 (the structural test — honest negative, deep lesson).** Tried to upgrade
to a learned *Lagrangian* where "charge = conserved momentum ∂L/∂ẇ" is literally
checkable by autodiff. Run 1: a generic extended Lagrangian FITS (3.15e-5) but
uses w as a label channel — cyclicity 0.94, corr(p_w, q/m) = −0.26. **Economy
does not select gauge:** the Kaluza form is one choice in a large equivalence
class of Lagrangians producing identical visible motion, and nothing in the loss
prefers it. Run 2 (symmetry imposed as architecture — the one allowed fix):
Euler–Lagrange rollout numerics blew up (loss 0.07→50→3.6). Verdict: KK structure
*unverified-not-refuted*; Phase D stands on v1's gauge-robust behavioral result.

**D-3 (magnetic).** The genuinely new face: velocity-dependent forces
(q/m · v×B) in 2-d. Same recurrent machinery, state `(x,y,vx,vy,w)`. Result:
**r = +0.9974** — the internal coordinate carries charge in a velocity-coupled
world too; the w-less control fails 23×. In real KK theory the magnetic force IS
the Coriolis effect of the hidden dimension — the toy now shows both faces.

**Loose ends:**
- The 13% conservation drift — never explained. Is it integrator error,
  optimization slack, or something meaningful?
- D-v2's failure is *numerics*, not physics — a stabilized Lagrangian/Hamiltonian
  parameterization remains on the shelf.
- Is there a *physically motivated* pressure (minimal coupling? action
  simplicity?) that WOULD select the Kaluza gauge? That's a real research-y
  question about why nature's description is the elegant one.

---

## 6. Phase E — the whole metric field from watching things move

**Question.** Phase B could only see one ratio per point. Trajectories cross
positions — can ALL the geometry be pinned at once?

**The world.** 2+1 anisotropic: `ds² = A dt² − (B dx² + 2D dxdy + C dy²)` with
four fields from three independent bumps — including the shear D, the component
Phase B provably couldn't see.

**The model — bias declared, trap avoided.** "Motion = mass-matrix mechanics"
(L = ½q̇ᵀS(q)q̇ − φ(q)) with the FIELDS S_θ (SPD via Cholesky — always invertible,
no D-v2-style implicit solves) and φ_θ as free networks; closed-form equations of
motion; differentiable rollout; loss = positions at three times. Identifiability
note: trajectories pin (S, φ) up to ONE global scale + a constant on φ — gates
fit that freedom once, never per-point.

**Results — all four gates:** held-out trajectory MSE 5e-6; field recovery
**cos = 1.0000** after the single global scale; φ correlation 0.9997; **the shear
D̂ at r = 0.9989** (Phase B's caveat resolved by measurement); constant-field
control fails by 1700×.

**The closing readout — curvature itself.** Differentiate the trained field nets
*twice* (Brioschi formula; the calculator first validated exactly on a 2-sphere)
→ the **Gaussian curvature of the learned geometry matches the true world's at
corr = 0.9903**. This is Theorema Egregium currency — the number no coordinate
relabeling can fake. The project's title question, closed.

**Loose ends:**
- The global scale (units) is the one number trajectories can never pin — is
  there an observable that would?
- Everything is still STATIC and 2-d and slow-motion. Dynamical geometry,
  relativistic speeds, 3+1 — none attempted.
- We read out curvature post-hoc. We never made curvature *itself* the latent of
  a bottleneck task.

---

## 7. The side quests that didn't headline

- **Metric-component counting (step 11):** the full anisotropic local metric was
  read out anchor-by-anchor at |cos| = 1.0000 (a spectacular pass), but the
  *counting* gate failed for a deep reason: **you cannot count a field's
  components by bottlenecking position — the address is always a sufficient
  code** (a width-2 code matched a 3-component geometry because the world is
  2-dimensional).
- **In-context counting (steps 12–12d):** the corrected design (random geometries
  per episode, infer the form from k example events through a bottleneck) is
  information-feasible (oracle 0.992) but our readout chains lose ~5% before code
  width binds — **knee-counting needs near-oracle inference**. Parked with that
  honest verdict. (The projective smear — "the code carries a direction, not a
  vector" — was predicted by your second-opinion session and visible in our data.)
- **Phase F (the law itself) — CLOSED, honest null.** matter configs → geometry,
  trajectories only. The one gate that PASSED is provocative: field *direction*
  superposes on never-seen 3-mass worlds (cos 0.965) while magnitude fails.
  Diagnostics proved the wall is the CNN's local receptive field vs the long-range
  1/r kernel (can't even overfit one batch; capacity and data don't help); the RF
  sweep confirmed F2 climbs 0.85→0.99 with reach. This corner overlaps the
  established neural-operator field (FNO etc.) — fix is known science, novelty
  modest — so F-v3 was deliberately skipped for the generalist arc below.

---

## 7½. The generalist arc — Phases G, I, H (the 2026-06-15 stretch)

After Phase F, the project pivoted (user's redirect) from *one net per world* to
**one generalist across all world families**, and from accuracy to a deeper
question: **what makes a learned representation legible?**

**Phase G — the generalist + its world-summary space.** A 2M-param transformer
reads a handful of observations from *some* world (same-event pairs, trajectory
snippets, matter blobs — family never given), pools a 64-number summary `w`, and
answers queries. Data scaling (24k→60k→120k episodes) helps monotonically but the
charge-gated families sit ~300× above the per-family specialist floor — the wall
is the single global **mean-pool**, not data. The prize was never accuracy though:
it's `w`. Probing it (G3): the families **cluster into a physics taxonomy** (ARI
0.82 — flat spacetimes apart, pure-geometry wells isolated, the three
EM-coupled worlds in one neighborhood), and **electromagnetism is its own region**
— chargedE and magneticB sit 2× closer to each other than to gravity (z=27 vs a
shuffled null). The net drew a map of *laws*, unprompted. (Ties straight to the
It-from-Qubit "is there a geometry to the space of laws?" thread.)

**The dilemma, and how a symmetry dissolved it (Phase G-sym).** The mean-pool is
**permutation-invariant over bodies** — which is the *equivalence principle in
disguise*: an invariant code can only keep what survives relabeling bodies
(geometry), and is structurally forbidden from keeping the tag→charge binding. So
the stage/actor split isn't a design choice, it's the **invariant/equivariant
decomposition under body-relabeling symmetry** — and imposing that symmetry is the
same fair move as Phase A's boost-invariant head. (Frame contributed by a parallel
Claude session; credited.) The fix: keep the invariant pool as the legible
world-map *and* add an **equivariant per-body channel** (each query cross-attends
to the context). It restored accuracy (chargedE 14×, twocharge 11.5×) and the
per-body charge now decodes from the equivariant channel (0.91) — **but at a real
cost: the world-map's clustering dropped (0.82→0.69) as per-body info migrated out
of it.** Accuracy and legibility *trade off*; they are not free together.

**Phase I — the legibility law (the stretch's headline).** *What selects
legibility?* A clean factorial experiment (recurrence × discreteness, with a
free-embedding reference) gave a sharp answer: recurrence and discreteness do
**nothing**; the entire effect is **amortization**. A per-object code that a shared
encoder must *infer from data* is **linearly legible for free** (r≈0.97); the same
code stored as **free per-body parameters scrambles** (linear 0.50, info hiding in
nonlinear 0.86 — the exact Phase C signature). So:

> **Legibility is selected by amortization, not by agreement or discreteness.**
> The famous Phase C "illegible charge code" was a *free-parameter artifact*, not a
> property of charge. Want a legible per-object code? Don't store it — *infer* it.

(This also overturned a tempting "consensus → legibility" bet from the parallel
session — the question was right, the mechanism wasn't.)

**Phase H — the geometrization survey.** *Which particle-like labels become hidden
lanes?*
- **Row 1, two independent charges:** the practical lane-count knee lands at
  **exactly 2** (behavioral counting, where bottleneck-counting failed in steps
  11–12); both charges decode behaviorally at r≈0.9997; a never-seen body is
  pinned from ~4 observed trajectories.
- **Row 2, Wong color charge (the crown, and a boundary):** a classical SU(2)
  charge that *parallel-transports* — it rotates as the body moves, with |Q|
  conserved (Wong 1970, verified). Result: amortization **legibly encodes the
  static charge** Q₀ (linear 0.79–0.92, Phase I confirmed in a new setting), **but
  the rotating Q(t) is tracked only nonlinearly** (linear 0.29–0.46 / nonlinear
  0.66–0.76) and |Q| isn't conserved. **The refinement: amortization buys
  legibility for *static* codes, but a generic recurrent update re-scrambles a
  *dynamic* conserved quantity as it evolves.** Static labels geometrize (electric
  charge, color Q₀); the dynamic SU(2) rotation does not — a sharp survey boundary.

**The synthesis of the stretch (one sentence):** *amortize and you get legibility
for free — but only for static codes; representing a dynamic conserved quantity
legibly needs structure that preserves its invariant, which a plain learned update
does not provide.*

---

## 8. The recurring patterns (the real harvest, maybe)

1. **Gauge freedom is everywhere** — and we finally got a partial answer to the
   deep question. Phase B's per-anchor relabeling, C's illegible embeddings, MDL's
   lookup-table code, D-v2's Lagrangian equivalence class, E's global scale: every
   honest gate works by finding the quantity that *survives* the freedom. The
   question we'd never asked head-on — *what selects the human-legible gauge?* —
   **Phase I answered for per-object codes: amortization.** A code inferred by a
   shared encoder lands in the legible (linear) gauge for free; a free per-object
   parameter scrambles. (Refinement from Wong row 2: this holds for *static* codes
   only — a generic recurrent update re-scrambles a dynamic one. Selecting the
   legible gauge for *dynamics* needs invariant-preserving structure — open.)
5. **The stage/actor split is a symmetry, not a choice** (Phase G-sym). What's
   shared by all bodies (geometry) vs what distinguishes them (charge) is exactly
   the invariant/equivariant decomposition under body-relabeling — the equivalence
   principle, re-derived as representation theory. It re-derives Phase C's
   0-vs-1-number-per-body count from symmetry alone.
2. **Behavioral probes beat structural probes.** Every time we tested *what the
   net does* (swap tests, trajectory inversion, zero-shot fitting), we got clean
   answers; every time we tested *what the net looks like inside* (PCA, linear
   probes, SAE features, Lagrangian structure), we hit illegibility. That's a
   finding about networks, not about physics.
3. **Universality is the geometrizer.** The single conceptual through-line:
   what's identical for all bodies gets absorbed into the arena (0.44 bits/body);
   what varies per body stays a label (9.86 bits/body) — unless you add a
   dimension, and then it becomes position again.
4. **Direction is local, magnitude is global** (Phase F's split). Possibly a
   general decomposition of field-learning. Unexplored.

---

## 9. Things explicitly never tried (raw list for your thinking)

- **The orthogonal/Hamiltonian update (the live open thread from Wong row 2):** an
  update F that conserves |w| by construction (ẇ = Ω(state)·w, Ω antisymmetric →
  a learned rotation). Does *structure* recover the legible, conserved dynamic
  charge that amortization alone couldn't? The cleanest next experiment.
- **"Geometry from entanglement" (Phase J candidate — the It-from-Qubit bridge):**
  train only on the mutual-information table of a quantum lattice's ground state,
  test whether the net builds the right spatial geometry; replicate Van Raamsdonk's
  pinch-off as a behavioral gate; look for hyperbolic curvature at criticality
  (You–Qi 2018). Free-fermion states are classically computable → Mac-buildable.
  This is the one that closes the loop back to the original black-hole chat.
- Time-dependent geometry (moving/oscillating wells; the road to gravitational
  *waves* in a toy).
- Relativistic-regime learning (we measured the post-Newtonian gap in Phase C's
  G0 and then always stayed slow).
- An **embodied agent** (your original idea #4!): an RL agent living IN the
  curved world, navigating — does its world-model contain the geometry? Never
  built, and it's the one that used your AlphaLudo muscle.
- Observers with realistic limitations (noisy clocks, finite light-speed
  signaling between observers — *operational* relativity rather than given
  coordinates).
- Discrete/graph worlds (does geometry emerge without a continuum?).
- Making curvature the *bottleneck* rather than the readout.
- A communication game: two nets must AGREE on a description of the same world —
  does the shared protocol converge to the legible gauge? (Note: Phase I tested
  the related "recurrence → legibility" and it was the AMORTIZATION axis that
  mattered, not agreement — so reframe this if revisited.)
- The thermodynamic corner: your original black-hole interests (horizons,
  entropy, S = A/4) never met the learning experiments at all. There is no
  horizon anywhere in our toys.

---

*Everything above is backed by artifacts: `curvature/notes/lab_notebook.md` (raw
log, pre-registrations, all numbers), `curvature/results/` (plots, JSONs, saved
models), and the per-script docstrings. The polished narrative for outsiders is
`emergent_geometry.md`. This document is the one to argue with.*
