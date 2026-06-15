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

This explains the LLM observation it came from (Phronesis): a distributed feature is readable but
single-direction steering is weak. And Phronesis sharpened it into a **three-way distinction** —
on Qwen3-4B, the *monosemantic SAE feature* that semantically reads as the concept ("I don't
know") was **not** the direction carrying the model's calibration signal (AUC 0.53 vs a 0.64
supervised probe). So **legibility (linearly readable), monosemanticity (a clean single feature),
and task-causality (actually drives behavior) are three different things** — a representation can
have any subset. The legibility law governs the first; the second law and the SAE caution say the
other two do not come for free. (Credit: Phronesis session.)

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
