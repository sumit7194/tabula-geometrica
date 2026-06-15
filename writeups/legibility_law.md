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
>    quantity) restores the invariant exactly and recovers most of the legibility.

One line: *a learned per-object code is legible when it is **inferred, not stored**;
evolving it through a generic update destroys that; matching the update to the quantity's
symmetry buys the invariant back and most of the legibility.*

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

## Leg 3 — Invariant-preserving structure → restored (partial)

Same precessing charge, same amortized start, same task — change *only* the update rule.
Replace the generic update of the code with an **orthogonal** one,
`w ← exp(skew(MLP(state))) · w` (a learned rotation in SO(3)), which conserves `|w|` *by
construction*. (`33_legibility_structure.py`, 25k steps, one variable changed.)

| dynamic cell | legibility (mean) | \|w\| drift | fit (W1) |
|---|---|---|---|
| static + generic (ceiling) | 0.61 | 0.39 | 1.3e-2 |
| generic update | 0.38 | 0.62 | 1.5e-2 |
| **orthogonal update** | **0.49** | **3e-7** | 2.0e-2 |

- **Conservation fully restored:** `|w|` drift 3e-7 vs 0.62 — the invariant is now exact.
- **Legibility substantially recovered:** 0.49 vs generic 0.38 (+0.11), reaching ~80% of the
  static ceiling (0.61), at a small fit cost (an orthogonal update can only rotate, so it
  pays ~0.5e-2 in trajectory fit).

Honest grade: **partial** — conservation is a clean pass, legibility a strong-but-incomplete
recovery (it doesn't fully reach the static ceiling, because the learned rotation is
optimized for trajectory fit, not for tracking `Q`, so it only approximately matches the
true precession). The *direction* of the law is unambiguous: structure beats a generic
update on both legibility and conservation.

---

## The unified law — and the through-line

Putting the legs together (linear-decode legibility, same harness where comparable):

```
                          legible?        invariant kept?
  amortized, static        YES (0.6–1.0)      n/a
  generic, evolving        NO  (0.38)         no  (drift 0.62)
  structured, evolving     MOSTLY (0.49)      YES (drift 3e-7)
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

## Honest limits / scope

- "Legibility" here = linear decodability of a known scalar/vector. A stronger notion
  (monosemantic features, full disentanglement) is not claimed.
- Leg 3 is partial: structure restores the invariant cleanly but only ~80% of legibility,
  with a small fit cost. Fully closing the gap (a rotation trained to track the quantity, or
  a Hamiltonian parameterization) is open.
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
`33_legibility_structure.py` (legs 2+3 in one harness); results `29_consensus.json`,
`31_wong_amortized.json`, `33_legibility.json` (+ `.png`s); full pre-registrations and
numbers in `curvature/notes/lab_notebook.md`. The broader curvature saga this emerged from
is `curvature_field_guide.md`.
