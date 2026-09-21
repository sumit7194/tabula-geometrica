# PRE-REGISTRATION — leg 6, the blind triple

**Frozen before the metrics are transcribed and before any number exists.** Three stationary axisymmetric
metrics (A, B, C) supplied by TheBridge, key sealed in ansatz's repo. **I have not read the key and will not.**

## What was supplied, and what was NOT

Supplied: the five non-zero components per object in `(t, r, θ, φ)`, plus `a` and `ε`. One scope line from the
operator — *"this does not test whether an invariant outside your basis is detectable"* — and nothing else: not
why the objects were chosen, not what is expected, not how they relate.

**Contrast with leg 3, deliberately.** There I was told the answer's structure before running and had to file the
verdict as INFORMED. Here I have been told **nothing that narrows the answer**, and the one scope line *removes*
a claim rather than adding one. So this verdict can be filed blind, and that is the difference between the two
legs.

## The instrument, unchanged

§99's `conserved`/`heldout` engine driven exactly as §161/§168 drive it. Nothing about the engine is re-tuned
for this leg; only `metric_inv` is generalised to accept a supplied metric instead of a hardcoded one.

**Manifest constants whitened GLOBALLY.** `E = −p_t` and `L = p_φ` are fixed to the same values across the whole
ensemble, so they carry zero across-ensemble variance and drop out of the generalized eigenproblem. Any
conserved direction returned is therefore a genuinely NEW invariant, not a repackaged Killing vector. The mass
shell `2H = −1` is fixed for the same reason.

## The ladder, frozen

Momentum degree **{2, 3, 4}** × coordinate basis **{polynomial, rational}**, held-out validated on disjoint
trajectories, 3 seeds. Reported per object as the full grid of held-out variance ratios — **the ladder, not a
label**, which is what was asked for.

## Verdicts, frozen

- **EMIT** := min held-out ratio over the grid **< 1e-10** — an invariant conserved to integration precision,
  as Kerr's Carter is (§92: 1e-28; §161-A: 2.2e-19).
- **CERTIFY-RELATIVE-TO-BASIS** := min held-out ratio **> 1e-8** across the whole grid, with a clean integrator.
- **In between: no label.** I report the number and say it is between the thresholds. Inventing a third verdict
  after seeing the data is how a screen becomes a story.

## KNOWN-FAIL CONTROL (L1) — binding, and it is per-object

At **ε = 0** every object should reduce to Kerr, where the Carter constant exists and **must** be recovered.
Run each object's own code path at ε = 0 and require EMIT.

> **If ε = 0 does not emit on an object, my instrument is blind on that object's substrate and NO VERDICT
> ISSUES for it.** Not a certify — no verdict. A screen that cannot find an invariant that is definitely there
> has not earned the right to report that one is absent.

This is §178's L1 discipline applied per-object rather than once for the leg, because the three objects have
different `g_rr` and a control that passes on A says nothing about C.

## Integrator gate (G0)

Relative drift in `H` along the flow **< 1e-7** for every object. A certify from a drifting integrator is an
artifact, and the floor must be set by the physics rather than by the step size.

## What I will NOT do

- **Not look at the sealed key**, before or after reporting.
- **Not tune per object.** Same degrees, same bases, same integrator settings, same seeds for all three. If one
  object needs different treatment, that is a finding to report, not a knob to turn.
- **Not report a rank ordering or a grouping.** I was given three objects with no stated relation; producing a
  "these two are alike" claim would be an inference dressed as a measurement.
- **Not explain a surprising result tonight.** Report the ladder; interpretation waits for the unblinding.
