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

---

## AMENDMENT 1 (appended, original text above left unchanged)

**My proposed asymmetry was backwards, and the leg is retired as evidence.**

I wrote above: *"If the other instrument is genuinely uninformed on item 2, their number carries the weight and
mine is the control."* That is wrong on its premise. Disclosed by the operator after the fact, and carrying no
information about the answer: **two hours before leg 3 opened, at the user's instruction, the entire scratch
workspace was copied into the other participant's repository** — the metric, the conserved tensor written out,
the claimed dimension counts, every script and result log. They are not the uninformed party; **they are the
most informed participant, and were before the leg was announced.** The operator's leaked sentence told them
nothing they could not read off their own filesystem.

So the leg's structure is: **one fully-informed instrument running a replication, and one informed instrument
(me) running a calibration. Neither is a test of the object, and there is no blind side to referee.** The
operator has retired the claim and will report that the leg failed as a leg. That is the correct outcome and I
am recording it here rather than letting my original, flattering asymmetry stand.

**What survives, and it survives on its own merit rather than as anyone's control:** the run below tests
whether my instrument behaves as **my own §178 theory** predicts on a case whose structure I was told. The
pre-registration above is unchanged and still binding — descending, non-converging ladder expected; flat or
floor-converging would be the informative surprise. **It is an instrument calibration. It is not evidence
about the metric, and no concurrence between the two instruments should be read as two-oracle agreement.**

**One observation worth carrying out of this, from the operator's own tally rather than mine:** across today,
*every mechanism they proposed was wrong and every measurement they made was right* — ps-truncation refuted by
measurement, the leg-3 framing, the over-broad retraction. My own tally has the same shape from the other side:
my measurements held, and what failed were my **applications of conclusions I had already reached** — a rule I
had just relayed, a wait-loop I had just catalogued, a heartbeat I had already written the entry for.

> **In both sessions the reliable part was the part that touched data, and the unreliable part was the part
> that reasoned about what the data meant for something else.** That is not a coincidence of one bad day; it is
> the difference between a claim that gets checked by the world and a claim that gets checked only by the
> person making it.

## AMENDMENT 2 — hint (iv), logged before the calibration runs

A fourth piece of information arrived from the operator: a published result (Kubizňák & Krtouš, PRD 78, 064022,
arXiv:0804.4705) stating that a **principal conformal Killing–Yano tensor alone** — Einstein equations not
imposed — yields Petrov type D, separability, and complete integrability of geodesic motion. The operator
flagged it themselves: it says something structural about 4D metrics with hidden symmetry, and METRIC_A is a 4D
metric handed to me for a legibility verdict. Their words: *"I do not think it identifies METRIC_A — the
principal-tensor class is large — but 'I do not think' is not 'it does not'."*

**Choice recorded: (b), treat it as a further leak and downgrade.** The cost is asymmetric. Were I to run the
screen and land on a verdict consistent with the class this result describes, I could no longer separate *my
instrument found this* from *I was told roughly this and my instrument agreed*. Leg 3 is already retired as
evidence, so strictness costs nothing here — **which is exactly why this is the right place to practise it. A
rule adopted only where breaking it would be costless is not a rule.**

**Received hints now number four**, which is enough that the honest label is *informed*, not *informed about one
thing*:

    (i)   intermediate case, discriminates
    (ii)  an invariant exists
    (iii) polynomial in the momenta, non-polynomial coefficients in position
    (iv)  the principal-CKY structural result above

The pre-registration in the original section is unchanged and still binding. The calibration proceeds at its
declared weight — an instrument check against §178's predicted signature, not evidence about the metric.

**Not taken as a lead:** the operator's further suggestion that legibility and integrability might both be
downstream of a principal tensor. They labelled it their own inference and noted they had just been corrected
for that species of inference in this exact material; the bridging step sits in what they graded unverified. If
it bears on §161 it will still bear on it after reading the paper's body directly. **What survives without
inference, and is worth having on its own: the field equations are not what generates the symmetry.**
