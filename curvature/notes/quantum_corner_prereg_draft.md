# Pre-registration DRAFT — blind independent check of corner coefficients (for quantum/vestigium)

**Status: DRAFT, not yet frozen, no physics run.** Sequenced behind current repo work by user decision.
Nothing in this file may be edited after the hash is sent.

## Isolation (binding, agreed 2026-08-22)
No reading of the vestigium repo, its commits, or its status file until my numbers exist. Their commits contain
the values and one glance spends the channel. Questions about the SYSTEM go to them directly, and they answer
without numbers — a cleaner channel than inference from their code.

## CONTAMINATION EVENT (2026-08-22) — and the ruling that followed

**Before any entropy was computed**, TheBridge sent me their square-lattice results unprompted: corner spreads
1.69 / 0.25 / 0.12 / 0.0676% falling ~s^-2, area spreads ~36.2% flat, clip band 2254x below the corner spread.

**"Different geometry" does not save it.** The contaminating content is not the geometry — it is the
**magnitudes and their ratio**: corner sub-1%, area ~36%, ~500x separation. That is quantum's C2 supplied
quantitatively, and by quantum's own analysis the magnitudes are precisely what the literature does *not*
contain, i.e. precisely what a clean channel was worth having for. It also supplied the clip-band answer they had
asked me to add, before I ran it. **A geometry difference protects the ANGLE, not the SCALE** — and the claim
under test is about scale. Logged in `.claude-coordination/DISCLOSURES.md`; I struck the CLEAN line that named me.

### The ruling (quantum's, and it identifies an asymmetry I had not weighted)

> **Contamination biases toward AGREEMENT. It therefore degrades confirmation and leaves falsification intact.**

A pass is now weak — I knew the range, and neither of us could separate my implementation from my expectation.
But a **disagreement is not weakened; it is strengthened**, because it survived a pull toward agreement. The
instrument is smaller, not dead. **Pre-committed by quantum before my numbers exist: a pass will be recorded as
WEAK, a fail as DECISIVE, and they will not later argue the pass was stronger.**

### What the leak did NOT touch — and it is now the primary value

**The fit model.** TheBridge adopted quantum's model, so their "two-model robustness check" tested nothing; and
quantum has only ever used their own. **Model choice is the one degree of freedom in this entire result that has
never been independently exercised** — and knowing the answer is sub-percent does not tell you which model to
pick. It could only steer me if I chose a model *after* seeing my own numbers, which is exactly what freezing
the extraction prevents.

So the question my run answers is no longer *"do the magnitudes replicate"* but:

> **does this result survive someone else's choice of extraction?**

They sent me results, not a method. That question is untouched.

### Final scope (quantum's ruling, accepted)

1. **triangle-vs-hexagon area agreement — FIRST.** Physics-independent, magnitude-independent, untouched by the
   leak, and it can kill the study on my side before any corner number exists.
2. **a(60) and a(120)** on the triangular lattice with my frozen extraction, all four regulator families,
   plus across-regulator spreads and the clip band.
3. **DROPPED: Q2, the square-lattice a(90)** — most compromised, and it carried C3, which was itself a recall
   check (the literature says a(θ) is universal, so "the square point lies between the triangular ones" is
   absorbed rather than predicted).

Report regardless of outcome: the model, the priors as written, the controls **and why they were chosen**, and
the clip band. Control *design* is untouched by the leak and remains as informative as the numbers.

## The two exposures, stated rather than denied
1. **Their channel: clean.** Verified by grep across my tree — one hit, a README link to their public repo, no
   numbers. All my entanglement work is free-*fermion* Peschel; never bosonic, never a corner term.
2. **The literature: NOT clean.** Corner coefficients for 2+1D free scalars are published. I carry priors about
   the *shape* of a(θ). Their decision, with reasoning I accept: proceed, because the prior supplies the shape
   and not the magnitudes; the freeze removes the choices a prior could act through; and *the alternative is not
   a cleaner checker, it is no checker* — every sibling has the same exposure, so disqualifying on that basis
   sets the correct number of checks to zero.

   **Agreed weighting when I report: strong evidence on the quantitative claims, weak on the ordering.** If the
   ordering holds that is not news to either of us — it is a recall check. The spreads are the finding.

## To freeze before any entropy is computed
- four regulator families, built independently, **with the small-k convergence check run and reported as a gate**
- region size ranges (triangle / hexagon / square) with `region << correlation length`, `region << N` numerically
- fit model and basis
- **the length scale inside the logarithm** — the choice I expect to matter most
- convergence criterion and rejection rules for a bad fit
- **my stated priors**, written out, so a reader can see what I expected before seeing anything
- **an explicit known-fail per claim** — a pre-registration enumerating how a result could be *ambiguous* is not
  one stating how it could be *wrong* (silent_nulls 33)

## Gate order — physics-independent FIRST
1. **triangle-vs-hexagon area agreement.** Same cut, same lattice: disagreement means my extraction is broken
   regardless of how good the corner spreads look, and it does not depend on either of us being right about the
   physics. **If this fails the study is dead on my side and I send no corner numbers at all.**
2. regulator small-k convergence
3. only then the corner/area extraction

## Required reporting — the clip band (their addition, adopted)
**Sweep the floor imposed on the symplectic eigenvalues across several decades and quote how much every result
moves.** Rationale, which is why this is not optional: *the corner coefficient is a small residual on a large
area term*, and a numerical floor silently caps small residuals. They measured this on their own machinery with
two independent probes and the probes **disagreed about which limit binds** — the algorithmic route was fine at
6e-14 relative while clip sensitivity grew with region size, reaching within ~1.5× of mattering at the largest
sizes.

> **If my clip band is comparable to my corner spread, then my spread IS my floor and neither of us learns
> anything about universality.** Reporting that is still a result; reporting the spread without the band would
> be an artifact presented as a measurement.

This is the same shape as silent_nulls 18 (a budget-truncated statistic carries less than the boolean) and 29
(a cost that scales with the swept variable is invisible where the sweep worked): the sensitivity **grows with
region size**, so every small region is a passing test that reports nothing about the trajectory.

## Controls I will build (design to be stated with the numbers)
Their free positive control is adopted: **the area coefficient must FAIL to be universal.** Their framing of why
it is strong, which is better than mine — *the strongest controls are the ones whose pass condition is a failure
of the thing you want*; not a known-fail alongside a known-pass, but one test whose only pass IS a failure.
