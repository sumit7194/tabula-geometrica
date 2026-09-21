# PRE-REGISTRATION — locating J5's criticality wall (ξ\*)

**Frozen before the sweep script exists and before any number is produced.** Committed first, deliberately, so
its git timestamp precedes the result. TheBridge states that `../quantum` filed a sealed prediction for this
sweep in their own repo on 2026-09-05, before my instrument ran, and did not send it. **I have not read it and
will not look.** I have read access to that repository; not using it is the whole point. Leg 3 died because the
party administering the blinding spent it in the sentence announcing it (`silent_nulls` 50) — the failure mode
here would be mine alone and entirely avoidable.

## What is wrong with the gate today

§42's E2 reads: gapped chain → `R_CoV = 5.56` vs critical `0.0013`, pass. **That is a boolean** — *constancy
holds at criticality and fails when gapped* — in a project where every other certify verdict now reports a
location: `d* = 6` (§176), `K* = 3` and `r* = 3.6` (§177), *no invariant below degree 5* (§178).

> **A gate that can fail, and passes, has still not been characterised.** E2 says *that* constancy fails and
> never *where*.

I missed it for three months because E2 **passes**, and I had been auditing verdicts that certify rather than
controls that pass.

## The system, unchanged from §42 on purpose

`N = 512`, band `l ∈ [16, 176]` even, staggered mass `±m` (gap `2m`), `R(l) = Ω(l)·(N/π)²·sin²(πl/N)`,
statistic `R_CoV = std(R)/|mean(R)|` — the *same* `omega`, `R_const` and `cov` functions §42 already uses.
**Nothing about the instrument is re-tuned.** Changing N or the band would confound the location with a
re-tuning, and the object of this run is to locate the wall of *the gate that already exists*.

## Frozen choices

1. **Mass grid.** `m = 0` (critical baseline) plus 24 log-spaced points `m ∈ [1e-4, 0.5]`. The upper end
   reproduces §42's existing gapped point; the lower end pushes ξ past the box.
2. **ξ is MEASURED, never assumed.** The textbook relation is `ξ ~ 1/gap = 1/(2m)`, and I am not using it as
   the x-axis. ξ is fitted from the exponential decay of the correlation envelope `|C(r)|` on the same chain
   whose entropy is being read. **Both the measured ξ and `1/(2m)` are reported**, so any divergence between
   them is visible rather than absorbed. *Touch the state; do not reason about it.*
3. **The wall.** `ξ* = ξ at which R_CoV first crosses 3× the critical baseline`, interpolated on the log-ξ
   axis. The factor 3 is **not chosen now** — it is E2's own existing threshold (`cov_Rg > 3 * cov_Rc`, §42
   line 157). This run locates the boundary of the gate as written; inventing a new threshold would make the
   location an artifact of this run's taste.
4. **THE RATIO IS NOT COLLAPSED.** ξ\* is reported as `ξ*/N`, `ξ*/l_min` and `ξ*/l_max` **separately, never as
   one number.** The regime condition is `l ≪ ξ ≪ N` — *two* conditions on *different* lengths, which fail
   independently. Quantum's own withdrawal of their ξ/L threshold is the reason this clause exists: their
   chain had one length besides ξ, so a single ratio conflated "region ≪ ξ" with "ξ ≪ box". Mine has both, so
   there is no excuse for reporting one number.

## Known-fail control (L1) — binding

The sweep must reproduce **both** §42 endpoints on the same code path: critical `R_CoV ≈ 0.0013` and `m = 0.5`
→ `R_CoV ≈ 5.56`, each within 20%. **If either endpoint is missed, the instrument is broken, no ξ\* is issued,
and that is the reported result.** A sweep that cannot recover the two points it is interpolating between has
not earned the right to interpolate.

## Censoring guard (entry 19 / §177 W3)

If the crossing lies at the **boundary** of the swept range rather than inside it, the statistic is censored:
**ABSTAIN, report a bound, and widen the grid** — do not report an edge value as a location. Fraction of grid
points pinned at an extreme is checked first.

## What would make me re-examine the INSTRUMENT rather than the physics

Stated now, so it cannot be decided after seeing the number:

- **Either endpoint not reproduced** (above) → instrument, no verdict.
- **`R_CoV` non-monotone in ξ** → instrument *first*. It becomes a physics claim only if the non-monotonicity
  tracks `ξ/N` crossing 1, which is the box condition biting independently of the region condition — and that
  must be shown, not asserted.
- **Crossing at the edge of the grid** → censored, abstain, widen.
- **Measured ξ disagreeing with `1/(2m)` by more than 3× in the regime where they should agree (`ξ ≪ N`)** →
  the ξ fit is broken, not the physics.

## What this run cannot establish

`R_CoV` rising is the *geometry* degenerating, which is what E2 already asserts. Locating it does **not** show
that a central charge read off that geometry inherits a universality condition — that is a further claim and
this sweep does not test it. The c-from-curvature number in §42 is read at exact criticality using the
finite-size chord form, and nothing here changes its status.

**Frozen. Next commit in this file's history that touches the result is the result.**
