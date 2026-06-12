# Can a neural network *discover* that spacetime is curved?

*The ambition: not a net that computes curvature from a formula, but a net that — trained
only on adjacent observable facts, never shown curvature, never given Einstein's equation —
**invents "spacetime is curved" on its own**, because a hidden geometry turns out to be the
cheapest way to explain everything at once. This doc is the honest feasibility study + a
concrete experiment design. Researched against primary sources; citations at the bottom.*

> **Confidence tags:** 🟢 established result · 🔵 credible but narrow · 🟡 preliminary/open ·
> ⚪ provably impossible-as-stated.

---

## 1. Your idea has a name — and a track record

What you're describing is a real research paradigm: **unsupervised concept discovery
through an information bottleneck.** You build an *encoder → tiny bottleneck → decoder*,
train it *only* to predict adjacent observations, and **starve the bottleneck** (very few
numbers + a penalty for using them). The physical concept is **never in the loss** — it
appears because it's the cheapest sufficient code, and you *read it off afterward* by
checking what each bottleneck number correlates with.

This isn't hypothetical. It has already produced exactly the kind of "it discovered the
concept" result you're after:

- **SciNet (Renner group, 2020)** 🟢 — fed only Earth's-eye-view angles of Mars and the
  Sun, two bottleneck neurons spontaneously stored the **heliocentric (Sun-centered)
  angles**. It re-derived the Copernican switch with *zero* supervision of the frame.
- **The special-relativity version of your exact dream is *already done*** 🟢 — Wetzel et
  al. (2020) trained a network *only* on the question *"are these two snapshots the same
  event seen by two observers moving relative to each other?"* and the network **invented
  the Minkowski spacetime interval** `s² = −t² + x² + y² + z²` — the flat-spacetime
  "distance," **minus sign and all** — as its internal invariant. *A net discovering
  spacetime geometry unsupervised is published fact.*
- **A physical *vector* can emerge in a bottleneck** 🔵 — Cranmer et al. (2020) trained a
  graph net only to predict accelerations, squeezed the internal "messages," and the
  message channels became the **true force vector** (then symbolic regression read off
  `1/r²`). The same pipeline even found a **new dark-matter formula** that beat the
  hand-built one.

So: flat spacetime geometry — done. A physical vector emerging — done. **Curvature
(gravity) is the next rung, and it is genuinely open.**

---

## 2. The honest verdict: the *purest* dream is impossible — but a real variant isn't

⚪ **The literal version — feed raw data, impose *nothing*, let a curved spacetime metric
self-assemble from a plain bottleneck — is provably impossible.** This is a theorem
(Locatello et al., 2019), not a lack of effort: for any clean hidden representation there
are *infinitely many scrambled ones* that fit identical data, so a plain bottleneck has **no
signal** to prefer "curvature" over coordinate junk. **Emergence always needs a little
built-in bias — and it goes into the *data design* and the *encoding*.** That is *exactly*
the lever you kept pointing at. Your instinct "the encoding is what lets it emerge or buries
it" is *literally the content of the theorem.*

So the honest framing isn't "no bias." It's **minimal, geometry-shaped bias.** We assume as
little as possible (e.g. "motion follows *some* economical rule") and let the geometry
itself — including the curvature and even the minus sign — be *earned* from data.

---

## 3. The one obstacle that is the whole game: geometry vs. force

This is the crux, and it's *physics*, not machine learning.

**For a single falling object, "curved spacetime" and "flat space + a force" fit equally
well.** That's not a flaw in the net — it's literally why Newton's force-gravity worked
perfectly for 200 years. One trajectory cannot tell the two stories apart.

**The only thing that breaks the tie is the equivalence principle:** *every* object falls
the same way, regardless of its mass or what it's made of — a feather and a cannonball trace
the same arc in vacuum. Think about what that costs each explanation:

- A **force** has to be *re-tuned for every object* (pay a description cost *per object*).
- A **geometry** is *one shared thing for all objects* (pay *once*).

So if you feed the net the free-fall of **many different test bodies** and **forbid the
object's identity from entering the geometry part of the net**, then *the cheapest possible
code is a single shared geometry.* **Curvature wins on economy** — and only then. *This is
the equivalence principle turned into an architecture,* and it's the same reason Einstein
himself abandoned force for geometry.

> **Takeaway that decides everything:** without many *different* objects sharing the same
> trajectories in your training data, curvature can *never* beat a force on economy, and the
> experiment is unwinnable in principle. With it, curvature can emerge. The data design *is*
> the experiment.

---

## 4. What "success" even means (the gauge problem)

You can **never** verify success by comparing the net's learned metric numbers to a
textbook metric — because **the metric isn't unique.** You can always relabel coordinates
and get different numbers for the same physical spacetime (this is rigorous: "boundary
rigidity," Stefanov–Uhlmann–Vasy, *Annals of Math* 2021 — recoverable only up to coordinate
change and overall scale).

So you judge it the **Theorema Egregium** way — by things that *don't* depend on
coordinates:

1. **Curvature invariants** — compute a coordinate-free curvature number (the kind you
   already understand as the **round-trip / parallel-transport mismatch**) and check it
   matches the truth *in any coordinates*.
2. **The description-length horse race** — does the *one-shared-curved-geometry* model
   actually beat a *flat-space-plus-per-object-force* model at explaining held-out data?
   Curvature "wins by emerging" **if and only if** it's the more compressive story — and the
   win should *grow* as you add more kinds of objects (proof that it's the equivalence
   principle doing the work, not overfitting).

---

## 5. The concrete experiment (the most promising buildable variant)

Build it on the **2+1 rung** of our dimensional ladder — the simplest real curved
spacetime (no gravitational waves, very few metric numbers), so curvature can emerge with
little data.

**One-line idea:** *a bottleneck whose hidden representation is forced to be a single
shared per-point geometry that must explain the free-fall of many different bodies at once —
so "spacetime is curved" emerges as the cheapest object-independent code, verified by
coordinate-free curvature and a description-length win over a force model.*

| Piece | What you do |
|---|---|
| **Data ("adjacent things")** | Generate from a fixed, *withheld* weakly-curved 2+1 spacetime, but feed the net only observables: (1) free-fall trajectory segments for **many distinct test bodies** (the equivalence-principle seed — non-negotiable); (2) **light-ray** bending (the massless extreme — forces the light-cone structure); (3) **clock-rate vs. position** (gravitational redshift — forces the *time* part and the minus sign); (4) **closed-loop mismatches** — send two clocks/gyros around different paths between the same endpoints and record the disagreement (this round-trip mismatch is the only honest fingerprint of *intrinsic* curvature). |
| **Encoding (your crux)** | **Do not** feed raw global coordinates (the net would just absorb arbitrary coordinate changes = the gauge villain). Encode **relative, coordinate-free** quantities (proper times, relative angles, loop mismatches) and show the same region from **multiple observer frames** (the Wetzel trick). Encode each point with **Fourier features** so a smoothly-varying field is learnable. The geometry latent is **one shared symmetric field over points**, and **object identity is structurally barred from it** — that bar *is* the equivalence principle. |
| **Architecture** | A **Lorentzian Neural Geodesic Flow**: coordinate → small net → a per-point metric field; latent states evolve along **geodesics** of that metric; decoder predicts the next observable. The metric is the only free function; "motion is economical/geodesic" is the single minimal assumption. Run a **rival head**: flat space + a learned *per-object* force. |
| **Training** | Loss = prediction error on the observables **only**, + a squeeze on the bottleneck, + an L1 penalty on any per-object channel (so the *shared* geometry must do the work). **Not supervised:** the metric, the curvature, the signature (minus sign), the number of components, or whether geometry-beats-force. All of those must be *outputs of economy*, never targets. |
| **How curvature emerges** | Two pressures conspire: (a) many bodies fall identically → a shared metric is cheaper than per-object forces → geometry wins the horse race; (b) a flat metric predicts *zero* loop mismatch, so any non-zero round-trip disagreement **can only** be explained by curving the metric — curvature is forced to be non-zero exactly where "gravity" is, having never been shown to the net. |
| **Recognizing success (4 gates)** | (1) **Counting:** sweep the bottleneck width; the data needs *exactly* the geometric number of components. (2) **Invariant:** the learned curvature *scalar* matches the true one in any coordinates. (3) **Holonomy:** the learned round-trip mismatch is non-zero exactly where the true curvature is. (4) **Economy:** the curved-geometry model beats the force model on held-out description length, and the gap *grows* with more object types. |

---

## 6. Where no one has looked yet (the genuinely novel angle)

The synthesis flagged two specific openings nobody has cleanly done:

1. **Let the *minus sign* emerge.** Every existing "discover the metric" result lives in
   *positive-definite* (Riemannian) space — no time, no light cones, no causality. The one
   gravity-specific attempt (Jan 2026) **hard-codes** the Lorentzian signature. **Nobody has
   let the causal structure — the minus sign itself — be *earned* from clock-difference and
   light-bending data.** That's your spacetime-specific frontier.
2. **Make geometry *compete* with force, not just discover which geometry.** Every current
   method *assumes* "motion = geodesics of some metric" and only finds *which* one. **The
   experiment nobody has run** puts a flat-space-force model and a curved-geometry model in
   the *same* bottleneck and shows **geometry wins on description length precisely because
   the equivalence principle is in the data.**

That reframes your ambition into something **falsifiable and new**: not "AI discovers
Einstein," but **"curvature is the most compressive explanation of object-independent
free-fall — and we can measure the exact point where it beats a force."** That is the
*computational re-enactment of why Einstein chose geometry over a force* — and per all the
research threads, it has never been cleanly demonstrated.

---

## 7. Honest caveats (hold this at the right confidence)

- ⚪ The **no-bias** dream is impossible (Locatello). Pitch is *minimal* bias, in the data +
  encoding.
- 🟢 Even SciNet's famous result carried a hard-coded prior — "discovery enabled by a chosen
  bias + bottleneck," not pure free emergence.
- 🟡 The closest GR attempt (Hamzaogullari & Ozakin, Jan 2026) is materially weaker than
  "curvature emerges": the target metric was *known and supplied*, the signature was
  *hard-coded*, and the **Schwarzschild (real black-hole) case failed to train near the
  horizon.** Preliminary and essentially uncited.
- 🔵 Cranmer's "force vector emerges" is real but **finicky** — it worked for `1/r²` and
  springs, but *collapsed* for the electric-charge case under one of the penalties.
- 🟢 Across the *whole* field, NNs have overwhelmingly produced **controlled rediscovery of
  known toy laws**, not net-new physics. **Set the bar at "rediscovery with a twist"** —
  recover a *known* toy's curvature from *withheld* data, the way SciNet rediscovered
  heliocentrism. "AI discovers Einstein from scratch" is not the realistic deliverable.
- 🔵 Symbolic regression is the **readout**, not the discoverer — the viable pipeline is two
  stages: bottleneck makes the geometric latent emerge, *then* symbolic regression *names*
  it.

---

## 8. Open threads

- **Pick the first milestone.** The cleanest starting brick isn't the full thing — it's the
  *counting* probe: show that the free-fall data of many objects **needs a shared
  multi-component field** (a geometry) and that a single scalar force won't compress it.
  That alone, done honestly in 2+1, would be new.
- **Or start from the proven SR result and add gravity.** Re-run the Wetzel "same event,
  two observers" experiment (which discovered the *flat* interval), then introduce a weak
  gravitational field and see whether the learned invariant has to **vary from place to
  place** — i.e. watch the *flat* interval become a *curved* one. That's the most direct
  bridge from "already done" to "open."
- **Connect to the finales.** This experiment is the *empirical* sibling of Finale 2
  (gravity *is* curvature) — it tries to make a machine *re-derive* that geometry beats
  force. Worth doing Finale 2 (the physics) alongside, so we know exactly what the net would
  be rediscovering.

---

## Sources

- [Iten, Metger, Wilming, del Rio, Renner, "Discovering Physical Concepts with Neural Networks," PRL 124, 010508 (2020), arXiv:1807.10300](https://arxiv.org/abs/1807.10300) — SciNet, the bottleneck-emergence blueprint
- [Wetzel et al., "Discovering Symmetry Invariants… by Interpreting Siamese Neural Networks," PRR 2, 033499 (2020), arXiv:2003.04299](https://arxiv.org/abs/2003.04299) — **the Minkowski interval emerges (the SR version of the dream)**
- [Cranmer et al., "Discovering Symbolic Models from Deep Learning with Inductive Biases," NeurIPS 2020, arXiv:2006.11287](https://arxiv.org/abs/2006.11287) — a physical vector emerges in a bottleneck
- [Cranmer et al., "Lagrangian Neural Networks," arXiv:2003.04630](https://arxiv.org/abs/2003.04630) · [Greydanus et al., "Hamiltonian Neural Networks," arXiv:1906.01563](https://arxiv.org/abs/1906.01563) — geometry/conservation as emergent, coordinate-free
- [Locatello et al., "Challenging Common Assumptions in the Unsupervised Learning of Disentangled Representations," ICML 2019, arXiv:1811.12359](https://arxiv.org/abs/1811.12359) — **why emergence needs inductive bias (the impossibility theorem)**
- [Stefanov, Uhlmann, Vasy, "Boundary rigidity and the geodesic X-ray transform," Annals of Math 194(1) 2021, arXiv:1702.03638](https://arxiv.org/abs/1702.03638) — metric recoverable only up to gauge + scale
- [Hickok & Blumberg, "An Intrinsic Approach to Scalar-Curvature Estimation for Point Clouds," arXiv:2308.02615](https://arxiv.org/abs/2308.02615) — curvature from distances alone (computational Theorema Egregium)
- [Chen et al., "Automated discovery of fundamental variables hidden in experimental data," Nature Comp. Sci. 2, 433 (2022)](https://www.nature.com/articles/s43588-022-00281-6) — count hidden degrees of freedom from raw video
- [Hamzaogullari & Ozakin, "Learning Relativistic Geodesics… via Stabilized Lagrangian Neural Networks," arXiv:2601.12519 (2026)](https://arxiv.org/abs/2601.12519) — closest GR attempt (preliminary; supplied metric, hard-coded signature, Schwarzschild failed)
- Neural Geodesic Flows — Burge, O'Donnell, Moseley, EuroIPS 2025 workshop — closest architecture (Riemannian; geodesics imposed)
- [Liu & Tegmark, "AI Poincaré: ML Conservation Laws from Trajectories," PRL 126, 180604 (2021), arXiv:2011.04698](https://arxiv.org/abs/2011.04698) · [Tancik et al., "Fourier Features…," NeurIPS 2020, arXiv:2006.10739](https://arxiv.org/abs/2006.10739)

*Living document. §8 has the first concrete milestone — start there when you're ready.*
