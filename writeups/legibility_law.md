# The Legibility Law

*When is a neural network's internal code for a per-object property **human-readable**
— a clean number you can linearly decode — versus a scrambled tangle that holds the
same information illegibly? This note states a three-part answer, each leg backed by a
controlled experiment, and shows it is the hidden through-line under the whole
`curvature/` project. Written plainly; the raw log is `curvature/notes/lab_notebook.md`.*

---

## The claim, in one paragraph

A network that must represent a per-object property (a particle's charge, say) can store
it two ways: as **free parameters** (one learned vector per object, looked up by identity)
or as an **amortized code** (inferred on the fly by a shared encoder from the object's
data). These are information-equivalent — both let the network use the property — but they
are **not legibility-equivalent**:

> **The Legibility Law.**
> 1. **Amortize → legible.** A code *inferred by a shared encoder* is linearly decodable
>    (legible). The same property *stored as free per-object parameters* is scrambled —
>    linearly unreadable, recoverable only nonlinearly.
> 2. **Generic evolution → re-scrambled.** Evolving an (even amortized, clean) code through
>    a generic learned update destroys its legibility *and* breaks its conserved quantities.
> 3. **Invariant-preserving structure → restored.** Constraining the update to respect the
>    property's symmetry (e.g. an orthogonal update for a rotating, length-conserved
>    quantity) restores the invariant exactly and recovers the legibility to the static
>    ceiling — given an update expressive enough to match the true symmetry transformation.

One line: *a learned per-object code is legible when it is **inferred, not stored**;
evolving it through a generic update destroys that; matching the update to the quantity's
symmetry buys back the invariant and the legibility.*

## Why this matters

Mechanistic interpretability keeps hitting the same wall: networks provably *use* a
quantity that no linear probe can read (it's "there" but illegible). The usual response is
better probes. The Legibility Law says the illegibility is often **not intrinsic to the
quantity — it's a property of how the code was produced**, and it can be designed away.
That turns "is this feature legible?" from a fact about the trained network into a
**design choice** about the architecture that produced it.

## What "legible" means here (the probe ladder)

For each experiment we hold a network that represents a known scalar/vector property and
ask two things of its internal code `c` versus the true property `q`:
- **linear decode r** (ridge, cross-validated) — *legibility*. High = you can read it off.
- **nonlinear decode r** (kNN) — *information presence*. High = it's in there somewhere.

The diagnostic signatures: **legible** = linear high; **scrambled** = linear low *but
nonlinear high* (information present, illegibly stored). This ladder is the whole method.

---

## Leg 1 — Amortize → legible (the decisive experiment)

**Specimen (Phase C).** A network learns many bodies' gravitational + electromagnetic
motion, storing each body's charge `q/m` in a free per-body embedding. It demonstrably
uses the charge (swapping embeddings is catastrophic), yet: **PCA r = −0.12, linear probe
r = 0.02, behavioral decode r = 0.9999.** A perfect specimen of an illegibly-stored
number — information fully present, linearly invisible.

**Controlled test (Phase I, `29_consensus_legibility.py`).** A shared encoder infers a
per-body charge from trajectory snippets; we vary one thing at a time (3 seeds):

| arm | linear decode r |
|---|---|
| amortized, recurring-discrete charges | 0.96 |
| amortized, unique-discrete charges | 0.97 |
| amortized, unique-continuous charges | 0.97 |
| **free embedding** (Phase C regime) | **0.50** (nonlinear 0.86) |

Effects: recurrence (A−B) = −0.004, discreteness (B−C) = −0.005, **amortization
(C − free) = +0.466.** Recurrence and discreteness do *nothing*; amortization is the whole
effect. (This was pre-registered against a *competing* hypothesis — that *agreement /
value recurrence* selects legibility — which it cleanly falsified.) **An inferred code is
legible for free; a stored one scrambles.** The Phase C "illegible charge" was a
free-parameter artifact, not a property of charge.

### Refinement — *what* makes a free code scramble: latent dimensionality (scripts 45–48)

"Free → scramble" turned out to be *conditional*, and chasing the condition sharpened the law.
A new field (a scalar charge, script 45) gave a free code that was **linearly legible** (r=0.98),
contradicting a naïve "free always scrambles." A 2×2 factorial (script 46) then ruled out the
obvious suspects: **sign** (one-signed vs ±) and **coupling type** (position/potential vs
velocity/magnetic) make *no* difference — all four cells legible (0.99–1.00). The real driver,
isolated cleanly (script 48: a charge in `R^D` driving `D` independent wells, fixed tight free code):

| latent dim `D` | linear (legibility) | nonlinear (info present) |
|---|---|---|
| 1 | 0.86 (legible) | 0.95 |
| 2 | **0.26** (scrambled) | 0.91 |
| 3 | **0.34** (scrambled) | 0.88 |

A ~0.6 collapse in linear decodability from `D=1` to `D=2`, with the information fully preserved
nonlinearly — the scramble signature, reproducing Phase I's 2-D result. **Mechanism:** a free code
has no pressure to align a *multi-dimensional* latent with linear axes, so it scatters it across the
embedding manifold; a *1-D* latent has only a monotone curve to occupy and stays linearly readable.
So leg 1 sharpens to: **free + multi-dimensional latent → scramble; a 1-D free code is legible for
free.** (Amortization restores legibility at any `D` by biasing toward smooth inference. Embedding
capacity modulates the level — a roomier code softens the collapse, a tight one sharpens it.)

**Refinement of the refinement (AlphaLudo cross-session, credited).** The "1-D free code is legible for free"
clause is **task-dependent**, not universal. The AlphaLudo session (a trained Ludo RL agent) reimplemented our
harness — reproducing our scramble as a positive control (free `D=2` linear **0.216**, matching our 0.22) — and
found that under a *generic (random-MLP)* property→output map, even a **1-D** free code **scrambles** (their abstract
task: linear 0.36), whereas a *linear-in-property* world flipped `D=1` back to **legible** (0.61).

**We then ran the definitive re-test in our own validated harness** (`104_task_structure_validated.py` — script 35's
World, which provably scrambles, with a linear-coupling variant; plus a capacity sweep `105_capacity_check.py`),
3 seeds each. Two honest outcomes:
- **Confirmed (robust):** under *generic* coupling the free code scrambles **even at `D=1`** (linear 0.24, info
  present in kNN 0.59) — reproducing AlphaLudo's main point in our harness, and what the easy toy `103` (which
  failed to scramble at all, 0.93–1.0) could **not** show.
- **Not cleanly reproduced (fragile):** "linear coupling rescues `D=1`" did **not** hold in our *abstract-scalar*
  harness — the linear-world free `D=1` stayed scrambled across capacities (0.19–0.30 at cdim 2–16; a noisy 0.61
  only at cdim 32, where kNN also drops). Yet our *physics-trajectory* harness (script 48) shows linear `D=1`
  clearly **legible** (0.86). Same coupling-linearity, opposite outcome → the rescue depends on the **task / output
  structure** (trajectory vs scalar), not coupling or capacity alone (the capacity hypothesis was **refuted**, 105).

So the honest, scoped conclusion: the **`D=1` boundary is genuinely fragile and task-specific** — *neither* our old
"1-D free is legible" *nor* AlphaLudo's "linear coupling rescues `D=1`" is a clean universal. What is **robust across
all three domains** is the core: *amortized → legible; free + multi-D → scramble; free + generic-coupling → scrambles
even at `D=1`*. The earlier inconclusive toy `103` is superseded by `104`/`105`. Credit: AlphaLudo + Phronesis sessions.

**The 1-D mystery, cracked — and a real bound on the law (`107`–`109`).** Chasing *why* the same linear coupling
gives free `D=1` legible in physics-trajectory (`48`, 0.86) but scrambled in abstract-scalar (`104`, 0.23), we ran a
process of elimination and the answer is **none of the obvious suspects**: output richness (`107`, legible at every
output dim 0.93→1.0), capacity (`105`, non-monotonic), and batching regime (`108`, per-object 0.89 vs per-query 0.93)
are all **refuted**. The driver, isolated decisively (`109`): the **target function itself**. At identical
learner/capacity/batching/output, swapping *only* the world flips it — a default-init MLP world (s35's) **scrambles**
the free code (0.247, reproducing the s35 scramble through a fresh learner), while a large-weight world stays
**legible** (0.78). Plausible mechanism: the property's *signal-strength* in the observations (a strong, distinct
effect → legible; weak/diffuse → scramble). **Honest consequence:** *free → scramble is NOT universal* — it is
conditional on the target/observation structure (`109`) and, within a fixed world, on latent dimensionality (`48`).
Three fresh harnesses (`103`/`107`/`108`) never scrambled because they used "easy" targets; the cross-domain
reproductions (Phronesis 0.22, AlphaLudo 0.216) matched s35's number because they copied the s35 *target*. So the
**robust, theorem-backed** direction is *amortize → legible* (Roeder); *free → scramble* is real but
**target-conditional**, and the "1-D boundary" fragility is a symptom of that target-dependence, not a property of
`D=1` itself.

## Leg 2 — Generic evolution → re-scrambled

What if the property is not static but **evolves**? We use a classical SU(2) "color charge"
that *precesses* along a body's path (Wong 1970): it rotates, with its length `|Q|`
conserved. The code is amortized at `t=0` (so leg 1 says it *starts* legible) and then
evolved through a generic learned recurrent update while the body moves.

Result (`31`, `33`): the amortized initial code is legible (`w0 → Q0` linear **0.79–0.92**),
but decoding the *evolving* code against the true `Q(t)`:

| | linear | nonlinear | \|Q\| drift |
|---|---|---|---|
| dynamic, generic update | **0.38** | 0.68 | **0.62** |

Linear legibility collapses (0.38) while information survives nonlinearly (0.68) — the
scramble signature — and the conserved length drifts badly. **A generic update re-scrambles
a clean code as it evolves, and forgets the invariant.**

## Leg 3 — Invariant-preserving structure → restored

Same precessing charge, same amortized start, same task — change *only* the update rule.
Replace the generic update of the code with an **orthogonal** one,
`w ← exp(skew(MLP(state))) · w` (a learned rotation in SO(3)), which conserves `|w|` *by
construction*. (`33_legibility_structure.py`, `34_legibility_close.py`; one variable changed.)

| dynamic cell | legibility (mean) | \|w\| drift |
|---|---|---|
| generic update | 0.38 | 0.62 |
| orthogonal, shallow generator | 0.49 (80% of ceiling) | 3e-7 |
| **orthogonal, richer generator** | **0.51 (101% of ceiling)** | **3e-7** |

- **Conservation fully restored:** `|w|` drift 3e-7 vs the generic update's 0.62 — exact.
- **Legibility recovered to the ceiling:** a *shallow* rotation generator reached only ~80%
  of the static-code ceiling, but a generator expressive enough to track the precession
  reaches **101%** (`34`: 0.506 vs its 0.500 ceiling) — i.e. the evolving code becomes *as
  legible as a static one*.

Refined lesson: invariant-preserving structure recovers legible dynamics **provided the
structured update has the capacity to match the true symmetry transformation**. (Absolute
legibility here is ~0.5 because decoding a rotating 3-vector from the evolved state over a
whole rollout is intrinsically hard — "reaches ceiling" means *as legible as the best
achievable in this harness*, not linear r → 0.9.)

> **Addendum (2026-06-17) — the boundary condition: Leg 3 only bites under *indirect*
> observation** (`71/71b/71c`). Re-running the precessing-charge test while varying *how the
> charge is observed* sharpened Leg 3 and lifted the ~0.5 ceiling:
> - **Direct observation** (the charge's components are read off ~each step): the update rule
>   is *irrelevant* — generic and orthogonal both stay legible at **0.98–0.99**, with or
>   without a nonlinear readout (`71`, `71b`). Structure adds only exact conservation, not
>   legibility.
> - **Indirect observation** (a single projection per step; the charge must be reconstructed
>   from the *time-series* of its rotation, `71c`): the effect appears decisively — orthogonal
>   stays legible at **0.91** (no erosion), while the generic update **scrambles** it to linear
>   **0.06** (kNN 0.42 — info present, illegible) and *erodes through time*.
>
> So Leg 3 is not "structure always restores legibility" — it is: **structure earns its keep
> exactly when the conserved quantity must be *inferred through the dynamics* rather than read
> off directly.** This is the Phase H Row 2 regime (a Wong charge seen through a force) and
> explains both *why* it scrambled there and why everyday amortized codes often stay legible
> anyway. With a clean indirect-but-identifiable harness the structured update reaches 0.91
> (not the 0.5 of `33/34`), and the generic–orthogonal gap is far cleaner.

---

## The unified law — and the through-line

Putting the legs together (linear-decode legibility, same harness where comparable):

```
                          legible?              invariant kept?
  amortized, static        YES (ceiling)          n/a
  generic, evolving        NO  (0.38)             no  (drift 0.62)
  structured, evolving     YES (reaches ceiling)  YES (drift 3e-7)
```

This is not a side result — **it is the curvature project's explanation of itself.** It
retro-explains every legibility outcome we hit along the way:
- Phase C's charge was illegible **because** it was a free embedding (leg 1).
- The Phase G-sym generalist's equivariant channel decoded charge at 0.91 **because** it was
  amortized (leg 1).
- Wong's static color charge read out but its rotation didn't **because** the rotation was
  evolved generically (leg 2), and an orthogonal update partly fixes it (leg 3).

The project's recurring villain was *gauge freedom* — many internal codes work equally well,
and only what survives relabeling is real. The Legibility Law is the first lever we found
that **selects** among those gauges: it says which architectural choices land the network in
the human-legible one.

## Cross-test on real LLMs (Phronesis session, credited)

A parallel project (Phronesis — activation steering in small LLMs) ran the cheap "does the law
describe real models?" test on Qwen3-4B, pre-registered. The headline: the *stored → scrambled*
prediction does **not** transfer — and the reason sharpens the law rather than breaking it.

- **No scramble found.** A scalar recalled from weights (atomic number) is just as linearly
  legible as the same value supplied in context (parametric r=0.92 vs in-context 0.96, Δ=+0.04;
  they'd pre-registered Δ≥0.15 for "route matters"). Replicated on birth-year and population;
  nonlinear never beats linear → no scramble signature anywhere.
- **Why — the precondition isn't instantiated.** A pretrained transformer has **no
  free-embedding regime**: its parametric knowledge is reconstructed through massively shared
  weights — i.e. it is *amortized by default*. So everything lands in the law's "amortized →
  legible" regime; the free-parameter regime that scrambles in our toy simply does not occur.
  (Consistent with ROME's rank-one fact editability and the Linear Representation Hypothesis.)
- **The reframe (stronger, positive claim).** Rather than "the law predicts which LLM concepts
  are scrambled" (answer: ≈ none of the ones tested), the defensible claim is that **the law may
  explain *why* the Linear Representation Hypothesis holds at all** — concepts are linearly
  readable in LLMs *because* shared-weight training is amortized inference. That turns a
  case-by-case empirical puzzle (which concepts are linear?) into a mechanism. (Othello-GPT is
  *consistent* with the law but is not a controlled test — it has no free-embedding arm — so cite
  it as illustration, not confirmation.)
- **A new observable.** Route doesn't change *whether* a scalar is legible, it changes *where*:
  in-context-supplied values read out at a shallow layer (L4); recalled-from-weights ones only
  assemble by the deep layers (L4 r=0.40 → L36 r=0.92). **Depth-of-emergence, not peak
  legibility, is the "inferred vs recalled" fingerprint in a deep transformer.**

**Toy confirmation of the mechanism (script 38, sharing-interpolation).** Interpolating the
per-object code `c = (1−λ)·free_embedding + λ·shared_encoder` from λ=0 to λ=1, on the abstract
non-physics task:

| λ | 0.0 | 0.25 | 0.5 | 0.75 | 1.0 |
|---|---|---|---|---|---|
| linear decode (legibility) | 0.24 | 0.36 | **0.78** | 0.97 | 0.78 |
| nonlinear (info present) | 0.59 | 0.66 | 0.84 | 0.91 | 0.76 |

Legibility **flips around λ≈0.5** — even *partial* sharing converts the scrambled free code to a
legible one, which is precisely why an all-shared-weight LLM is legible by default. And the
free-embedding scramble **persists with a transformer set-encoder** (free: linear 0.20 /
nonlinear 0.56 = scramble; amortized: linear 0.70 = legible) — so the scramble is not an
MLP artifact, and the LLM null is purely "pretraining has no free regime," exactly as the
reframe predicts.

## Third domain — a trained game-RL agent (AlphaLudo, credited)

A second parallel project (AlphaLudo — a trained 2-player Ludo RL agent, whose 4 own tokens are natural per-object
slots) gave the law a **third independent domain** (physics → LLM → game-RL), with our harness reproduced as a
control.

- **Positive control reproduces.** They reimplemented our abstract task with our exact metric and recovered the
  scramble: free `D=2` linear **0.216** (our 0.22), kNN 0.63, amortized 0.84 — so their probe provably detects a
  scramble when one exists.
- **The game-RL boundary test (6 seeds).** Identical Ludo model, one arm adding a free per-token-ID embedding
  (`nn.Embedding(4, 96)`), the other not; same data + seed; probed on a shared state set with our Pearson-r metric.
  The free arm is **exactly as legible as amortized**: Δ(free − amortized) linear r = **−0.001 ± 0.007** (token
  position), **−0.004 ± 0.020** (capture-danger). The free code is **genuinely used** (per-slot embedding norms
  1.2–2.9), and the *same* probe shows Δ ≈ **−0.6** when a scramble is forced — so this is a **true zero**, not a
  blind instrument.
- **Why — and the boundary it maps.** In a real agent the per-object properties (position, danger) are computed by
  the **amortized backbone from the board**; the free per-ID code carries only **identity**, not the property — so
  there is **nothing to scramble**. That is exactly the boundary the law implies: *a free code scrambles only when
  it STORES the multi-D property; an identity-only free code stays legible even when actively used.*
- **Honest scope.** This does **not** test the core free-*storage* scramble inside Ludo — only 4 tokens (too few for
  a manifold scramble) and the per-token properties are dynamic/board-computed (cannot live in a static per-ID
  embedding). So AlphaLudo's contribution is **confirmation + boundary-mapping of the *refined* law** (an
  identity-only free code stays legible; the scramble needs free-*storage* of a multi-D property), plus the
  task-structure refinement above — **not** a re-run of the toy storage claim. (An earlier cross-session suggestion
  that AlphaLudo would be "the cleaner test" was wrong — it has no native free-storage arm and its properties are
  dynamic; this is the honest version.)

## Prior work, and what is actually ours (positioning)

"Why are representations linear?" is a **crowded** question, and honesty about the lineage makes the
real contribution sharper, not smaller:

- **Roeder, Metz & Kingma** ([ICML 2021](https://arxiv.org/abs/2007.00810)) prove discriminatively-
  trained representations are identifiable in function space *up to a linear transformation*. That is
  the theoretical statement of our **"amortized → legible"** leg, for encoder-type models — we
  re-demonstrate it, we don't discover it.
- **"Free → scrambled"** is, qualitatively, **auto-decoder / GLO folklore**: free per-object latent
  codes are known to be unstructured (un-samplable, no smooth interpolation), which is why that
  community bolts on variational regularizers. Our **dimensionality refinement** (1-D free legible,
  ≥2-D scrambles) rhymes with the disentanglement result that factors are identifiable only up to
  rotation absent an alignment pressure.
- **"LRH holds because amortization"** has company: **Jiang, Veitch et al.**
  ([ICML 2024](https://arxiv.org/abs/2403.03867)) derive linearity from the *next-token softmax-CE
  loss* + implicit bias of GD; Ravfogel et al. derive it from concept co-occurrence. So we are *not*
  first to "why linear."
- **"Amortization is not a neutral approximation step"** is published in the SAE/interpretability
  setting: **O'Neill et al.** ([arXiv:2411.13117](https://arxiv.org/pdf/2411.13117)) prove an
  *amortisation gap* — a shared linear-nonlinear SAE encoder cannot implement optimal sparse inference
  even when the dictionary is fully recoverable, and more expressive inference improves sparse-code
  recovery in LLM activations. That is the closest published "amortization shapes
  identifiability/legibility" result. It is *adjacent, not identical*: O'Neill is about amortized
  inference being **sub-optimal** (a gap vs exact sparse coding); ours is the orthogonal axis —
  amortized-vs-**free-parameter** *legibility flip* (a free per-object code scrambles; a shared
  encoder's inferred code is linearly legible). We cite it as same-family prior art; the one-variable
  free-vs-amortized isolation below is still ours. *(Found by a parallel prior-art audit — flagged here
  because a referee would expect it.)*

**What is genuinely ours** is the controlled, one-variable isolation none of them ran: hold the
objective and data fixed and vary **only amortization** (free embedding vs shared encoder), and show
the *same information* flips scrambled → legible — quantified with the linear-vs-nonlinear probe
ladder, the λ-interpolation snapping on at λ≈0.5, and latent dimensionality isolated as the driver.
The sharpest card: **our harness uses no softmax-CE at all** (it is regression/contrastive), so if
amortization buys legibility here, the lever is *separable from the language-modeling objective* the
LLM theories depend on.

The decisive test (`50_objective_x_storage.py`) — objective {regression, softmax-CE} × storage
{free, amortized}, **mean ± std over 3 seeds**:

| | regression (MSE) | softmax-CE (LM-style) |
|---|---|---|
| **amortized** | 0.84 ± 0.06 | 0.86 ± 0.06 |
| **free** | 0.22 ± 0.02 | 0.72 ± 0.06 |

Amortization effect **+0.38**; objective effect *within* amortized **0.02**. So **amortization is a
sufficient, objective-independent lever** — it makes the code legible (~0.85) with *no* LM objective,
which separates it from Jiang–Veitch. And honestly: softmax-CE is *also* a lever — it legibilizes
even a free code (0.22 → 0.72), confirming Jiang–Veitch's mechanism in our own harness.
**So the levers are complementary, not competing.** The defensible claim is therefore the modest,
true one: *amortization/sharing is an additional, isolable, objective-independent architectural lever
for linear legibility* — a mechanistic complement to the data-and-objective theories, and a bridge
from the auto-decoder community's "free latents are unstructured" to interpretability's LRH. (The
geometry arc — interval → well → Kaluza r=0.9998 → curvature — is the elegant *vehicle* that birthed
this, with known Wetzel/SciNet lineage; the legibility law is the *cargo*.)

## The second law — legibility ≠ steerability (confirmed), and a three-way distinction

The first law is about *reading* a code. A second, independent law is about *writing* to it:
**a direction can be legible (linearly readable) without being a control lever.** Demonstrated
cleanly (`39_read_vs_control.py`): encode a property redundantly across two channels
(channel-dropout in training), then —
- **read** the property from channel 1 alone: r = **0.89** (legible from a part);
- **steer** channel 1's direction: the output moves only **40%** of the counterfactual — the
  other channel still encodes the old value and partly overrides it (readable, weak lever);
- **steer both channels**: the output moves **100%** (full control).

So reading is easy from any copy, but *controlling* requires writing all the redundant copies —
**legibility ≠ steerability**, decoupled by redundancy. (Contrast: edge (a)'s world-summary was a
single causal bottleneck, so there read *did* equal control, 3.8× over random — read=control holds
when the legible code *is* the bottleneck, breaks when the property is distributed.)

**Cross-project test on a real LLM (Phronesis, pre-registered) — and a correction.** The earlier version of
this section claimed the toy's *redundancy* mechanism explained the LLM observation ("a distributed feature is
readable but single-direction steering is weak"). A direct, pre-registered test on Qwen3-4B (TruthfulQA, layer 20,
matched injection norm, directions fit on a disjoint split) **refutes that mechanism**: writing the full-rank
optimal *readout* (the "all redundant copies" direction) is **inert as a steering vector** (≈ a random direction),
not a strong lever. The only clean causal lever is the diff-of-means (correct − incorrect) direction (~8× stronger,
sign-dependent), and even that is modest and inseparable from fluency degradation. The LLM mechanism is therefore
**not redundancy but read-direction ≠ write-direction**: the discrimination-optimal *read* probe and the *write*-
optimal direction are nearly orthogonal (cos ≈ 0.34).

So the cross-project claim, now tested **both ways** and **calibrated**: **legibility ≠ steerability holds in both
settings, and read-direction ≠ write-direction is a shared *qualitative* phenomenon.** A reciprocal test back in our
own toy (`102_read_vs_write_direction.py`, 3 seeds) reproduces the functional dissociation: the read-optimal probe
direction is **legible** (r ≈ 0.89) but a **markedly weaker control lever** (matched-norm reach ≈ 0.4) than
diff-of-means (≈ 1.0), and it points in a partially-different direction (cos(read, diff-of-means) ≈ 0.55). Two
calibrations (credit: Phronesis) keep this honest:
- **the geometric direction-mismatch is strong on the LLM, only marginal in the toy.** cos(read, diff-of-means) =
  0.34 on the LLM is ~17σ from random in 2560-d; our 0.55 sits right at our 16-d random p95 (≈ 0.48, mean 0.20) —
  barely above chance. So the *directions-literally-differ* claim is carried mainly by the LLM; in the toy it is
  only suggestive. (The **functional** dissociation below is the part that is strong in *both*.)
- **the up/down asymmetry was a baseline-position confound — withdrawn.** Re-run from a *centered* baseline (mid
  tercile), the control lever (diff-of-means) is **symmetric** (|Δup|/|Δdown| ≈ 1.0); the strong asymmetry first
  seen came from steering out of the *low* group (the analog of the LLM's −12.66 starting point). So we do **not**
  claim intrinsic asymmetry — this *confirms* Phronesis's caution. (Their −side behaviour was independently
  diagnosed as fluency degeneration, so the asymmetry was a starting-point artifact on **both** sides.)

The strongly-shared result is the **functional** dissociation — the read-optimal direction is *legible but a weak
lever* in **both** systems; the **geometric** direction-mismatch is strong on the LLM and marginal in the toy. The
toy *additionally* has the engineered redundancy of script 39 (a real but toy-specific second cause that does **not**
transfer to the LLM). Both the earlier "redundancy explains the LLM" claim and the "intrinsic asymmetry" bonus are
**withdrawn**.

**Settled joint statement (both projects carry this, referee-proof):** (1) legibility ≠ steerability in both the toy
and a real 4B LLM; (2) read-direction ≠ write-direction is the shared mechanism — *functionally* strong in both
(reads-but-weak-lever), *geometrically* strong on the LLM (cos 0.34, ~17σ) and marginal in the 16-d toy (cos 0.55 ≈
random p95); (3) redundancy is a real but toy-specific extra cause; (4) the up/down asymmetry was a baseline confound
on both sides — withdrawn as intrinsic; the LLM −behaviour attribution stays open pending Phronesis's near-boundary
test. Reciprocal credit: Phronesis session — they tested our toy-derived claim on a real model, we tested their
model-derived mechanism in a controlled toy, and each corrected the other (cross-validation working as designed).

Phronesis also sharpened the reading into a **three-way distinction** — on Qwen3-4B, the *monosemantic SAE feature*
that semantically reads as the concept ("I don't know") was **not** the direction carrying the model's calibration
signal (AUC 0.53 vs a 0.64 supervised probe), and (above) the *read*-optimal probe is not the *write*-optimal
lever. So **legibility (linearly readable), monosemanticity (a clean single feature), and task-causality (actually
drives behavior) are three different things** — a representation can have any subset. The legibility law governs the
first; the second law and the SAE caution say the other two do not come for free. (Credit + the corrected numbers:
Phronesis session.)

## Honest limits / scope

- "Legibility" here = linear decodability of a known scalar/vector. A stronger notion
  (monosemantic features, full disentanglement) is not claimed.
- Leg 3 closed (edge 1): a *shallow* rotation generator reached only ~80% of the ceiling, but a
  generator expressive enough to match the precession reaches it (101%), with the invariant
  conserved to 3e-7. So the recovery is real but contingent on the structured update having the
  capacity to match the true symmetry transformation.
- **Generality + scale (tested, edge 3):** the core leg holds in a deliberately NON-physics
  abstract task (objects with a hidden property under a frozen random world function) and the
  amortize>>free gap PERSISTS and WIDENS across width/object-count (free linear decode
  0.33→0.13 as size grows; amortized stays ~0.8) — the scramble fingerprint (linear 0.13 /
  nonlinear 0.57) reproduces out of physics. So the law is a general representation property,
  not a toy artifact. Caveat: 'scale' here is ≤~1M params, not LLM-scale; the widening trend
  is encouraging but extrapolation to large models remains untested.
- Process note: the leg-3 pre-registration used a +0.2-on-min gate mis-calibrated to a ~0.9
  ceiling that doesn't exist in this hard decode (real ceiling ~0.6 mean); the honest
  comparisons are orthogonal-vs-generic and orthogonal-vs-static.

## Artifacts

`curvature/scripts/29_consensus_legibility.py` (leg 1), `31_wong_amortized.py` (leg 2),
`33_legibility_structure.py` (legs 2+3), `34_legibility_close.py` (leg-3 closure),
`35_legibility_scale.py` (generality+scale), `38_sharing_interpolation.py` (the Phronesis
cross-test: sharing flips legibility, in MLP and transformer); results `29_/33_/34_/35_/38_*.json`
(+ `.png`s); full pre-registrations and numbers in `curvature/notes/lab_notebook.md`. The
real-LLM cross-test lives in the sibling Phronesis project. The broader curvature saga this
emerged from is `curvature_field_guide.md`.
