# Leg 3 (TheBridge METRIC_A) — INFORMATION RECEIVED BEFORE RUNNING

**Written before the screen is run. Status: INFORMED — not blind, not partially blind.**

The leg was set up as blind: a 4D Lorentzian metric with no provenance, no rank, no claim of integrability,
two code-disjoint instruments reporting independently. It is no longer blind for me, and this file records
exactly what I was told and when, so the verdict can be discounted correctly by anyone reading it.

## What I received, in order, all before any computation

1. **From the leg announcement:** the object is *"neither of your two catalogued cases — the intermediate one,
   and it discriminates."* → tells me the answer is not my clean EMIT and not my clean CERTIFY.
2. **From the operator's retraction of (1)**, which quoted verbatim a sentence sent to the *other* participant
   and not previously to me: *"this object's invariant is polynomial in the momenta with non-polynomial
   coefficients in position."* → tells me **an invariant exists**, that it is **polynomial in the momenta**,
   and that its **position dependence is not polynomial**.

Item 2 is close to the answer itself. My instrument's job (§178) is to separate *no invariant* — a **flat**
degree ladder — from *an invariant the basis cannot represent* — a ladder that **descends monotonically
without reaching the integration floor** (§97/§160/§161, CERTIFY-RELATIVE-TO-BASIS). Being told the invariant
is polynomial in momenta with non-polynomial position coefficients **states which of those two shapes the
readout should print.**

## Consequence for what this run can and cannot establish

- **It is NOT a discovery, and will not be reported as one.** A verdict that matches a structure I was handed
  is not evidence about the object.
- **It IS a legitimate instrument calibration**, and a pre-registerable one: given item 2, the predicted
  signature is a **descending, non-converging degree ladder** in a position-polynomial basis, with the
  momentum-degree axis able to represent the invariant and the position axis unable to. If my engine prints
  something else — flat, or converging to the integration floor — then either the received description is
  wrong or my readout does not behave as §178 claims. **That is worth running.**
- **If the other instrument is genuinely uninformed on item 2, their number carries the weight and mine is the
  control.** This asymmetry should be stated in the leg's writeup.

## Pre-registration (frozen before running)

- **Expected:** best held-out within/total variance ratio **descends** monotonically across momentum degree
  {2, 4, 6} in a polynomial-in-position basis, and does **not** reach the ~1e-19..1e-28 floor this engine hits
  when an invariant is exactly representable (§161 A: 2.2e-19; §167 K0: 3.1e-26).
- **Would surprise me:** a flat ladder (would contradict item 2, i.e. the operator's own statement), or exact
  convergence to the floor (would mean the position coefficients *are* representable in my basis after all).
- **Reported statistic:** the ladder itself plus the §178 monotonicity test — never a bare verdict label.

Related: `writeups/silent_nulls.md` §50 (the disclosure of a leak can be a larger leak than the leak), and
`../../DISCLOSURES.md` in the coordination directory, which already carries the reverse contamination between
these repos (square-lattice magnitudes reaching me before the corner study computed).
