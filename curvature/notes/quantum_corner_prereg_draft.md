# Pre-registration DRAFT — blind independent check of corner coefficients (for quantum/vestigium)

**Status: DRAFT, not yet frozen, no physics run.** Sequenced behind current repo work by user decision.
Nothing in this file may be edited after the hash is sent.

## Isolation (binding, agreed 2026-08-22)
No reading of the vestigium repo, its commits, or its status file until my numbers exist. Their commits contain
the values and one glance spends the channel. Questions about the SYSTEM go to them directly, and they answer
without numbers — a cleaner channel than inference from their code.

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
