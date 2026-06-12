# Neural Networks & Spacetime — what actually connects

*Your curiosity: can vector embeddings / neural-network training represent dimensions
(including time), run physics across the ladder, and model spacetime curvature? Here is
the honest map — researched and fact-checked, not freehanded.*

> **Confidence tags used below** (this doc's version of the verdict tags):
> 🟢 solid / textbook · 🔵 established research · 🟡 speculative / frontier · ⚪ loose analogy.
>
> **The one-sentence headline.** There are several *genuinely solid* bridges from neural
> networks to spacetime physics — but **every one of them runs through differential
> geometry (the metric tensor), not through a literal "embedding axis = physical
> dimension."** Your three core instincts each survive, but only in a corrected form.

---

## 1. Clearing the ground — five tempting ideas that are category errors

You said yourself most of the framing wouldn't apply literally. You were right to flag
that. Here are the specific traps, stated so we never trip on them later. (❌ = the
seductive version, ✅ = what's actually true.)

**① "An embedding with D dimensions is like a D-dimensional spacetime."**
❌ Tempting because both are "vectors with D slots." ✅ *Three different meanings of
"dimension" are being blurred.* (a) An embedding's **ambient** dimension is just array
length — an arbitrary design choice (512, 768…). (b) The **intrinsic** dimension of the
data inside is typically tiny (~16–60, even in a 512-wide embedding). (c) Physics' **manifold**
dimension is a hard integer welded to a metric. Every formula in our other docs —
rotation planes `n(n−1)/2`, force `1/r^(n−1)`, the Weyl counts `0/0/10/35` — keys off the
**manifold** dimension. You can crank ambient dimension to 10,000 and change *nothing*
physical; and you can't measure spacetime's dimension as "3.7."

**② "A net solves PDEs in 100,000 dimensions, so 4 spatial dimensions is trivial / done."**
❌ ✅ In that literature "dimension" = **number of input variables** of the equation (1000
asset prices, many particle coordinates). A 100,000-variable Schrödinger equation still
lives in ordinary 3D space. None of it grows a new geometric axis with new rotation
planes (`xw, yw, zw`) or a 50-component Riemann tensor. Different word, different thing —
and the method still needs the governing equation *handed to it*.

**③ "Train on 2D & 3D physics, the net extrapolates the laws to 4D."**
❌ ✅ Nets are reliable **interpolators** and notoriously bad **extrapolators**. Worse,
the jump 3+1 → 4+1 isn't a benign point outside the data cloud — it's a **structural
discontinuity**: the Weyl tensor is *identically zero below 3+1* and only switches on at
3+1; double rotations are *new* in 4D. No amount of 2D/3D data implies them. **What
extrapolates is the closed-form algebra (it's a function of `n`); a neural net does not
inherit that guarantee.** Use the algebra to climb the ladder; use a net only to solve a
fixed rung fast and *check* the algebra. 🔀

**④ "Training a network is a ball falling along geodesics — gradient descent ≈ gravity."**
❌ ✅ The curved-manifold part is real (next section). But "falling along geodesics"
breaks twice: (1) real optimizers take a straight Euler step and *re-measure* curvature —
they don't integrate the geodesic equation; (2) gradient flow is **dissipative descent**
(always pulled downhill by −∇loss), whereas a freely-falling planet is **force-free
inertial coasting** with conserved energy. A falling planet feels nothing; a training
run is explicitly forced.

**⑤ "A training step is a step of physical time."**
❌ This is the *most-abused* part of the mapping. ✅ Optimizer "time" has no metric
signature, no causal light-cone, no conserved energy, and is reparameterization-arbitrary
(steps vs epochs vs wall-clock all differ). Physical time carries the minus sign in the
metric, a causal cone, and a thermodynamic arrow — none of which optimizer time has. This
is the precise, rigorous form of this project's recurring theme that **time is genuinely
different**.

*(Two more worth knowing: "a hyperbolic embedding is curved spacetime" — no, it's a*
*chosen, constant, source-free Riemannian curvature, not a mass-sourced Lorentzian one;*
*and "a tensor network IS a slice of AdS spacetime" — the area-law part is exact, but the*
*clean "MERA = AdS slice" slogan did not survive scrutiny.)*

---

## 2. The bridges that are real — ranked by how solid they are

### 🟢 Tier A — solid / textbook

**A1. The metric tensor `g` is the one object both worlds literally share.** *This is the
deepest bridge — see §3.* On a curved space you can't just subtract gradients; you must
**raise** the gradient with the inverse metric: `step = g⁻¹·∇f`, then move along the
surface. That `g⁻¹` index-raising is *exactly* the algebra of general relativity.
Riemannian SGD and Amari's **natural gradient** do this every step. → *Same `g` you meet
in the gravity rung; different job (distance-between-models vs distance-between-events).*
[Amari 1998](https://doi.org/10.1162/089976698300017746) · [Bonnabel 2013, arXiv:1111.5280](https://arxiv.org/abs/1111.5280)

**A2. Hyperbolic / "Lorentz-model" embeddings use the *exact* Minkowski form and Lorentz
group of special relativity.** To embed hierarchies (trees, word taxonomies), ML places
points on the upper sheet of a two-sheeted hyperboloid `⟨x,x⟩ = −x₀² + x₁² + … = −1` — the
*same* `−t² + x² + …` bilinear form and the *same* isometry group `SO⁺(1,n)` from our
Lorentz-group tables. → *The most literal embedding↔spacetime link in the whole set.* The
**one honest divergence is signature**: physics keeps the indefinite metric *live* (light
cones, causality); ML "spends" the minus sign to carve the sheet, then lives on a
positive-definite slice (hierarchy, no time). Negative curvature buys *exponential room* —
the same "more room" intuition we use climbing the ladder, but bought with curvature
instead of a new axis. [Nickel & Kiela, ICML 2018, arXiv:1806.03417](https://arxiv.org/abs/1806.03417)

**A3. The Fisher information matrix *is* a Riemannian metric on the space of models.** For
a model `p(x|θ)`, `g_ij(θ) = E[∂_i log p · ∂_j log p]` is a genuine metric tensor (the
curvature of KL-divergence; unique by Chentsov's theorem). So "the space of trained models
is curved" is **precise, not metaphor** — and you can run the *same* machinery (metric →
Christoffel → Riemann → Ricci) on it that the gravity rung runs on spacetime. *Caveat:*
this manifold is the space of *distributions*, it's positive-definite (no time, no cone),
and its curvature comes from the model family, not mass-energy.
[Amari & Nagaoka, *Methods of Information Geometry*, 2000](https://bookstore.ams.org/mmono-191)

**A4. PINNs: a PDE in the loss is the literal "run a physics formula" machine.** A
Physics-Informed Neural Network is a net `u_θ(t,x)` whose *output* is the field; you reuse
the same autodiff that powers backprop to compute its derivatives, plug them into the PDE,
and minimize "how wrong is physics here" instead of "how wrong is my label." → *Hand it the
wave or Poisson equation in 2+1 vs 3+1 and only the input-coordinate count and the number
of derivative terms change.* **But:** it solves *one* instance per trained net (an
optimizer dressed as a net, not a generalizing model), and fights "spectral bias" on sharp
gradients. [Raissi, Perdikaris, Karniadakis, JCP 378 (2019)](https://doi.org/10.1016/j.jcp.2018.10.045)

**A5. The "3+1" in this project's name is mechanized as ADM/BSSN numerical relativity.**
Einstein's equations are evolved by slicing 4D spacetime into a stack of 3D "now"
snapshots — literally "n space + 1 time." That machinery simulated the black-hole mergers
LIGO heard, and the **graviton-DOF count `D(D−3)/2 = 2` in 3+1 is exactly the two waveform
polarizations** the ML surrogates reproduce. → *ML mostly **accelerates byproducts**
(waveform surrogates, ~20-second Bayesian parameter estimation), it does not replace the
core solver. "ML solved gravity" overclaims.* [Dax et al., PRL 127, 241103 (2021)](https://doi.org/10.1103/PhysRevLett.127.241103)

**A6. The Lorentz group is *non-compact* — so the boosts are the hard part.** You can boost
toward `c` forever; the group has infinite volume and **no finite-dimensional unitary
representations**. → *This sharpens our `SO(n,1)` entries: the `(n,1)` minus sign is
exactly what makes the group non-compact. The compact rotation part `SO(n)` (the
`n(n−1)/2` planes) is "easy"; the `n` boosts are "hard."* A CS engineer's intuition
"symmetry = rotate the image, easy" does **not** transfer to boosts; real nets dodge this
by contracting to invariant scalars or canonicalizing into a local frame.
[Representation theory of the Lorentz group](https://en.wikipedia.org/wiki/Representation_theory_of_the_Lorentz_group)

### 🔵 Tier B — established research

**B1. Lorentz-equivariant networks bake our 6-parameter Lorentz group into the wiring.**
LorentzNet / LGN combine particle 4-momenta *only* through the Minkowski dot product, so
they are physically incapable of telling which inertial frame measured the data. → *The
3+1 table cell "Lorentz dim = 6 = 3 boosts + 3 rotation planes" becomes an engineering
primitive; climb the ladder and the symmetry budget grows `1→3→6→10` in lockstep with
`n(n+1)/2`.* Scope: this is **flat** special relativity — no curvature, no gravity.
[Gong et al., JHEP 07 (2022) 030, arXiv:2201.08187](https://arxiv.org/abs/2201.08187) · [Bogatskiy et al. (LGN), arXiv:2006.04780](https://arxiv.org/abs/2006.04780)

**B2. Hashimoto's AdS/DL — network *depth* becomes an emergent spacetime dimension; the
*weights* become the bulk metric.** *This is your black-hole holography thread reappearing
in ML.* Discretize a field equation propagating from the AdS boundary into the bulk and it
takes exactly the form "next layer = weight matrix × state, then nonlinearity" — so each
layer is a radial step and the metric sits in a slot of each layer's weights. Trained on
boundary data, it reconstructs the AdS-Schwarzschild metric. → *The cleanest executable
version of "is the extra dimension real or bookkeeping?"* **Honest scope:** it's an
inverse-problem solver that *assumes* holography (the radial dimension is built in, not
discovered), the "weights" are a constrained metric slot (not a generic MLP), and there's
~30% discretization error near the horizon. [Hashimoto et al., PRD 98, 046019 (2018), arXiv:1802.08313](https://arxiv.org/abs/1802.08313)

**B3. ResNet / Neural-ODE depth = the bulk radial flow.** A ResNet `xₙ₊₁ = xₙ + f(xₙ)` is
the Euler step of `dx/dt = f(x)`; the continuous-depth limit makes "deeper network" and
"further into the bulk" the *same* limit, and "depth = RG/zoom scale" is the standard
holographic-RG statement (UV at the boundary, IR deep inside). *Caveat:* precise in
AdS/CFT, only loose intuition for an ordinary supervised net. [Chen et al., Neural ODEs, arXiv:1806.07366](https://arxiv.org/abs/1806.07366)

**B4. PINNs have recovered black-hole metrics by minimizing the Einstein residual.** A net
outputs the metric, autodiff gives the curvature, training drives `R_μν − ½g_μν R − κT_μν
→ 0`, and out come Schwarzschild / Reissner–Nordström. A separate "Einstein Fields" net
walks the metric → Christoffel → Riemann → Ricci chain by differentiating one network. →
*Theorema Egregium in code: the net sees only coordinates and metric values, never an
embedding 5th axis — curvature falls out of derivatives of the field itself.* **Demoted
per verification:** a spherically-symmetric *static* ansatz and weak-field boundary
conditions are hard-coded, so it learns two radial functions of *known* solutions; and
"Einstein Fields" *compresses* an already-computed metric — it does not solve from matter.
[Li, Li, Pang, arXiv:2309.07397](https://arxiv.org/abs/2309.07397) · [Cranganore et al., arXiv:2507.11589](https://arxiv.org/abs/2507.11589)

**B5. Tensor networks (MERA, HaPPY) — discrete holography you can count in bits.**
Entanglement entropy of a boundary region = the **minimum number of bonds you must cut** (a
discrete Ryu–Takayanagi min-cut), and HaPPY makes "the bulk is encoded on the boundary" a
literal **quantum error-correcting code**. → *Turns the holography rung's "info on a
boundary one dimension down, S = A/4" into a finite, countable bits-and-encoding object.*
**Honest caveat:** the clean "MERA = an AdS time-slice" slogan did *not* survive — its
intrinsic geometry is a light-cone, not a hyperbolic AdS slice; these are kinematic toys
with no Einstein equations. [Pastawski et al. (HaPPY), arXiv:1503.06237](https://arxiv.org/abs/1503.06237) · [Milsted & Vidal, arXiv:1812.00529](https://arxiv.org/abs/1812.00529)

**B6. Neural operators (FNO, DeepONet) — learn the solver once, NOT the dimension.** These
learn a map from PDE inputs to solution functions; FNO is **resolution-invariant** (train
coarse, evaluate fine). → *The honest home for the "embeddings + reuse physics fast"
instinct — DeepONet's branch×trunk really is a dot-product of learned embeddings.* But
**"super-resolution" = more grid points along the same axes, not a new axis.** A 2D-trained
FNO has 2D Fourier weights; you cannot query it at "4 spatial dimensions" — the tensor
shapes don't exist. [Li et al. (FNO), arXiv:2010.08895](https://arxiv.org/abs/2010.08895) · [Lu et al. (DeepONet), Nat. Mach. Intell. 3 (2021)](https://www.nature.com/articles/s42256-021-00302-5)

**B7. Curvature as a *trainable weight* (mixed-curvature / learned-K embeddings).** Embed
into a product of spherical + hyperbolic + flat factors and **learn each factor's
curvature** by gradient descent. → *The strongest literal "training can model curvature,"
and the perfect setup for the "mass → Ricci" step: it shows what's present (tunable
curvature) and what's missing (a source term — there's no `G_μν = 8πT_μν`).* Each factor's
curvature is *constant*, not a smoothly varying field. [Gu et al., ICLR 2019](https://openreview.net/forum?id=HJxeWnCcF7)

**B8. Two metrics, intrinsic vs extrinsic — an on-ramp to *Theorema Egregium*.** The Fisher
metric is an **intrinsic, reparameterization-invariant** object (like the Riemann tensor);
the loss **Hessian** ("sharp vs flat minima") is **not** — you can make a flat minimum look
arbitrarily sharp without changing the function. → *A clean ML illustration of exactly why
physicists insist curvature be coordinate-free* — which is the hinge of the gravity finale.
[Dinh et al., ICML 2017, arXiv:1703.04933](https://arxiv.org/abs/1703.04933)

---

## 3. The spine: the metric tensor is the same object in both worlds

If you remember one thing, remember this. The **metric tensor `g`** is the single
mathematical object that both fields are built on:

| | In general relativity | In machine learning |
|---|---|---|
| What `g` is | the shape of spacetime | the Fisher / Riemannian metric on model (or embedding) space |
| What sources it | mass-energy (`G_μν = 8πT_μν`) | the model family / a chosen curvature |
| What you do with it | particles follow its **geodesics** → "falling" | gradient steps are **raised by `g⁻¹`** → natural gradient |
| Signature | **Lorentzian** (`−+++`): a minus sign, light cones, causality | **Riemannian** (`++++`): positive-definite, no time, no cone |

So "gravity = curved geometry" and "training on a curved manifold" are the *same
mathematics with two different jobs*: **distance-between-events** vs
**distance-between-models**. And the intrinsic/extrinsic split shows up on both sides
(B8) — which is precisely the distinction that answers your headline question, *"is
curvature another dimension?"* It isn't; it's a field *on* the dimensions, measurable from
the inside, in physics **and** in ML.

---

## 4. The holography thread, reappearing in ML (why this excites me)

You arrived here from black-hole holography — and it comes back on its own:

- **Depth as the emergent dimension** (B2): the holographic *radial* direction you met via
  `S = A/4` literally becomes a neural network's **depth axis**, with curvature stored as
  trained weights.
- **Area law as bond-counting** (B5): the entropy `S = A/4` becomes a discrete min-cut
  through a tensor network, and "the interior is encoded on the boundary" becomes a real
  error-correcting code.

Both are genuine research, and both are *easy to over-hype* — so the doc flags the limits
in place (assumes holography; MERA isn't literally an AdS slice; no Einstein equations in
the toy networks). The grown-up statement: **the emergent extra direction in these systems
is a genuine *scale/RG* axis; whether it is *literally* the AdS spacetime radial dimension
is an open question, not settled fact.** 🟡

---

## 5. Toys actually worth building

Concrete, with an honest note on what each does and doesn't show.

| Toy | What you build | What it shows | Effort |
|---|---|---|---|
| **Huygens tail by dimension** ⭐ | Two tiny PINNs solving the wave equation, one in 2+1, one in 3+1 — differing only in input-coordinate count | The **"heyyyy" smear**: a clean trailing edge in 3D, a lingering tail in 2D — our `dimensional_ladder.md §5` claim, made runnable | weekend |
| **Hyperbolic tree** ⭐ | Embed a tree in 2D Euclidean vs 2D hyperbolic (Riemannian SGD on the Lorentz hyperboloid) | **Negative curvature = exponential room** — and you're optimizing on the *same Minkowski hyperboloid* a physicist calls a mass shell | weekend |
| **Schwarzschild geodesics** | Integrate the geodesic equation in the Schwarzschild metric (Christoffels via autodiff); optional: fit a net to the metric and re-derive | **"Falling" is force-free geodesic motion** — no force term, just `Γ` from derivatives of `g`. Sets up the finale | serious |
| **Fisher natural gradient** | 2-parameter Gaussian; plot ordinary GD vs natural GD; reparameterize and rerun | The **metric corrects the step** (`g⁻¹`), and natural GD is **reparameterization-invariant** = the ML face of general covariance | weekend |
| **Depth = bulk dimension** | Reimplement Hashimoto's toy; recover AdS-Schwarzschild from boundary data | **Depth becomes a spacetime dimension, weights become a metric** — the holography demo | serious |
| **Extrapolation failure** | Train an MLP on a dimension-dependent quantity for `n=2,3` only; query `n=4` | Honest negative result: the **algebra extrapolates, the net doesn't** — especially the discontinuous Weyl count `0,0,10,35` | weekend |

The starred two are the best first builds: they directly *validate claims already in our
docs* with ~100 lines of code each.

---

## 6. Verdict on your three core ideas

1. **"Embeddings for dimensions, including time."** → Category error as stated (ambient ≠
   manifold dimension), **but** the corrected version is real and elegant: ML already
   embeds data on the **Minkowski hyperboloid with the `SO(n,1)` group** of special
   relativity (A2). The catch is signature — ML keeps the positive-definite slice; physics
   keeps the live light cone.
2. **"Run physics for 2D/3D, extrapolate to 4D."** → The **closed-form algebra
   extrapolates; a neural net does not** (③). The qualitative jumps — Weyl switching on at
   3+1, double rotation in 4D — are exactly where nets fail. Net's honest role: solve a
   *fixed* rung fast (A4) and cross-check the algebra.
3. **"Use how nets are trained to model curvature."** → Real, via the **metric-tensor /
   Fisher bridge** (A1, A3, B7) — training genuinely moves on a curved manifold. But
   training is **dissipative, forced descent**, not the force-free geodesic free-fall of
   gravity (④).

**Overall:** your instincts weren't naive — they pointed at real bridges. They just land
one level of abstraction up from where you aimed them: not "embedding axis = space axis,"
but "**the metric tensor is the shared object, and the rest follows from differential
geometry.**"

---

## 7. Open threads

- **Build the starred Huygens-tail PINN** — it turns a claim in `dimensional_ladder.md`
  into a runnable artifact, and it's a genuinely instructive weekend project.
- **Proceed to the gravity finale** now armed with a CS anchor: "mass → Ricci curvature →
  geodesics that look like falling," with the metric tensor `g` as the object the engineer
  can already picture from natural gradient.
- **The Kaluza–Klein contrast** (the payoff): the *one* place an extra dimension is real
  physics — adding a literal 5th dimension produces electromagnetism. Worth setting beside
  "depth as an emergent dimension" in ML: one is a genuine new axis, the other is a useful
  re-description. The comparison sharpens the whole "is curvature a dimension?" question.

---

## Sources (the load-bearing ones)

- [Hashimoto, Sugishita, Tanaka, Tomiya, "Deep Learning and AdS/CFT," PRD 98, 046019 (2018), arXiv:1802.08313](https://arxiv.org/abs/1802.08313) — depth = emergent radial bulk dimension; weights = bulk metric
- [Nickel & Kiela, "Lorentz Model of Hyperbolic Geometry," ICML 2018, arXiv:1806.03417](https://arxiv.org/abs/1806.03417) — embeddings on the Minkowski hyperboloid, same `SO(n,1)` as SR
- [Amari, "Natural Gradient Works Efficiently in Learning," Neural Computation 1998](https://doi.org/10.1162/089976698300017746) — the Fisher matrix is a Riemannian metric
- [Raissi, Perdikaris, Karniadakis, "Physics-Informed Neural Networks," JCP 378 (2019)](https://doi.org/10.1016/j.jcp.2018.10.045) — PDE-in-the-loss
- [Li, Li, Pang, "Solving Einstein equations using deep learning," arXiv:2309.07397](https://arxiv.org/abs/2309.07397) · [Cranganore et al., "Einstein Fields," arXiv:2507.11589](https://arxiv.org/abs/2507.11589)
- [Gong et al., Lorentz-equivariant GNN, JHEP 07 (2022) 030, arXiv:2201.08187](https://arxiv.org/abs/2201.08187) · [Bogatskiy et al. (LGN), arXiv:2006.04780](https://arxiv.org/abs/2006.04780)
- [Pastawski, Yoshida, Harlow, Preskill (HaPPY), arXiv:1503.06237](https://arxiv.org/abs/1503.06237) · [Milsted & Vidal, arXiv:1812.00529](https://arxiv.org/abs/1812.00529) — holographic codes; the "MERA ≠ AdS slice" correction
- [Balestriero, Pesenti, LeCun, "Learning in High Dimension Always Amounts to Extrapolation," arXiv:2110.09485](https://arxiv.org/abs/2110.09485) — why "interpolate vs extrapolate" must be re-read for the ladder
- [Li et al. (FNO), arXiv:2010.08895](https://arxiv.org/abs/2010.08895) · [Lu et al. (DeepONet), Nat. Mach. Intell. 3 (2021)](https://www.nature.com/articles/s42256-021-00302-5)
- [Clough & Evans, "Embedding Graphs in Lorentzian Spacetime," arXiv:1602.03103](https://arxiv.org/abs/1602.03103) · [Cohen et al., "Edge of Stability," arXiv:2103.00065](https://arxiv.org/abs/2103.00065) — the disanalogy backbone

*Living document — `§7` has the next moves; pick one.*
