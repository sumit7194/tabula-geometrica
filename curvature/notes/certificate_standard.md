# The certificate standard — pre-registration (frozen 2026-08-16, before any code)

**Authorized by the user 2026-08-16**, following the PROGRAM_II round. Our slice: not a new certificate,
but the **standard form a certified null must take before it counts**.

## Why this and not P4

The family's collective read on PROGRAM_II converged, from three repos with no coordination, on the
same shape: ansatz's surviving P1(a′) is a *certified classification to stated order*, P3 is *certify
non-existence to stated order*, and our §160–§165 basis ladder is *certified basis-relative
non-existence*. The distinctive product of this program is **the certified null**.

Which is exactly why the certification has to be airtight — and we have now hit **four** separate ways
it silently isn't. Three we found and patched piecemeal; the fourth we identified only in the P4 read
and have never tested:

| # | failure mode | where we hit it | status |
|---|---|---|---|
| 1 | **basis-relativity** — "no invariant" always means "not in my library" | §162 (Candidate B illegible in every analytic-in-p basis), §164 (the un-blind: naming the basis moved the boundary instantly) | patched, never asserted as a required clause |
| 2 | **library conditioning** — collinear columns manufacture null directions | §165 (deg 8: 8 exact zeros out of p=147, cutoff reported 9 "invariants") | patched, fix is `null(W) − deficiency(F)` |
| 3 | **in-sample approximation** — a polynomial crosses an emit threshold by approximating, not representing | §164 U3 / bridge O4 (in-sample 9.9e-7 crossed the 1e-6 line; held-out 5.6e-6 did not) | patched, held-out orbits |
| 4 | **confounding** — a per-realization nuisance constant is constant-within and varying-across, so the engine finds it **and it passes out-of-sample validation perfectly** | identified in the P4 read (2026-08-16); the bridge confirmed they had been treating R7's out-of-sample rule as covering it | **NOT patched, NOT tested — the new work** |

Failure 4 is the one that matters most, because it is invisible to every defence we have. Held-out
validation catches **overfitting**, not **confounding**: a calibration offset, a subject identity, a
per-run instrument constant generalizes to held-out data flawlessly, because it is genuinely constant.

## The proposed standard

A certificate is admissible only if it carries all four clauses. Any one missing → the claim is not a
certificate, it is a curiosity.

- **C1 BASIS NAMED.** The verdict states the family `F` and order `N`. The instrument must be
  structurally incapable of emitting an unqualified "no invariant exists" — every null is scoped.
- **C2 CONDITIONING GATED.** `rank(F)` reported; the invariant count is `null(W) − deficiency(F)`,
  never raw `null(W)`. (§165. Note the trap inside the fix: measuring deficiency on `W` deletes the
  finding, since a true invariant *is* a rank deficiency of `W`.)
- **C3 OUT-OF-SAMPLE.** The conservation statistic is evaluated on **held-out realizations**, never
  in-sample. (§164 / R7.)
- **C4 STATE-FUNCTIONALITY** *(new)*. A candidate invariant must be **a function of the dynamical
  state alone**, verified by predicting it on **held-out realizations** from their states. A genuine
  invariant `I(z)` is determined by the state, so a regressor `z → Î` generalizes across realizations.
  A nuisance constant is not a function of the state, so it cannot. The certificate must declare which
  channels are dynamical state and which are auxiliary/metadata.

## Pre-registered gates (frozen before writing the script)

Menu of four cases, every one with a known answer, so the standard itself is what is under test:

- **S1 GENUINE INVARIANT PASSES.** Kepler ensemble (many bodies, one law, different invariant values —
  §156's structure). The engine emits a conserved direction; all four clauses pass; C4's
  cross-realization R² > 0.9.
- **S2 THE CONFOUND GAP, DEMONSTRATED AND CLOSED** *(the headline; both halves required)*. Same
  ensemble plus a **planted per-realization nuisance channel** (a calibration-offset-style constant,
  no dynamical meaning). Then:
  (a) the engine **finds** it — it is at least as conserved as the true invariant;
  (b) it **passes C3** — held-out variance ratio comparable to the genuine case, i.e. our existing
      defence does not catch it;
  (c) it is **rejected by C4** — cross-realization R² < 0.3, versus > 0.9 for the genuine invariant.
  If (b) fails, the gap was never real and this whole clause is unnecessary — that would be a valid
  and cheap null, and it is reported as such.
- **S3 A TRUE NULL CERTIFIES, SCOPED.** Hénon–Heiles in its chaotic regime (H conserved, no second
  invariant): the instrument returns CERTIFY **with `F` and `N` attached**, never an unqualified
  non-existence claim.
- **S4 CONDITIONING CLAUSE FIRES.** A deliberately over-rich library on the S1 data: raw `null(W)`
  inflates, `null(W) − deficiency(F)` does not. (Replicates §165 inside the protocol.)

**Honest limitations to be stated in the output, not discovered later:**
- C4 requires the auxiliary/state split to be declared. If a confound contaminates a *state* channel
  (e.g. multiplicative per-run gain on an observable), C4 as specified will not catch it. Scope stated.
- C4's power depends on the ensemble spanning enough state space for `z → Î` to be learnable at all;
  a degenerate ensemble makes it uninformative rather than negative. Report, don't assert.
- §165's conditioning fix carries a measured rank-estimate sensitivity (exact at full sampling, ±1 at
  coarse). Inherited here.

**What would falsify the whole standard:** if the planted confound fails to pass C3 (i.e. held-out
validation already catches it), then failure mode 4 is not real and C4 is ceremony. That is the
cheapest possible outcome and it is a genuine result.


## Post-run record (2026-08-16) — all four gates green, with two corrections

**Result.** S1 EMIT (relative 1.03) · **S2 the confound gap demonstrated AND closed** · S3 true null certifies
SCOPED as `CERTIFY-NO-INVARIANT-IN[poly(state),order2]` · S4 raw null 3 → corrected 1. Full run 8s, `--fast` 7s.

**The headline, S2.** The planted per-realization nuisance channel is found by the engine at held-out ratio
**4.2e-17 — *more* conserved than the genuine invariant's 1.2e-16** — and **passes C3 completely**. Only C4 rejects it
(state-R² −0.688 vs genuine +0.61; relative −1.17 vs 1.03). Failure mode 4 was real and invisible to every defence we
had. The falsification condition stated above (if the confound had failed C3, C4 would be ceremony) did not trigger.

**Correction 1 — the C4 gate was unreachable by construction.** S1's threshold was frozen at absolute R² > 0.9.
Feeding C4 the *true energy* — definitionally a function of the state — scores only **0.658 / 0.750** in this harness;
the engine's candidate scores 0.61–0.70, the same band; more trajectories moved it 0.606 → 0.698 then plateaued. That
is a held-out-**realization** extrapolation ceiling, not a defect of the candidate. Third instance in this family of
testing the convenient quantity rather than the commensurable one (bridge's S3, our §164 proxy, now this — ours again).
**Fixed with a positive control, not a lowered bar:** C4's statistic is the candidate's state-functionality *relative to
a manifest invariant measured in the identical harness*. Self-calibrating — any implementation must ship its own
control. Where no manifest invariant exists, C4 can only REJECT, never confirm.

**Correction 2 — `--fast` was cutting the wrong resource.** Reducing trajectory count (40 → 24) dropped the control
R² to 0.448 and S1 failed. That is the pre-registered coverage limitation firing exactly as written: C4's *confirm*
direction needs ensemble coverage (its *reject* direction still worked, S2 passed at −0.52). `--fast` now trims **time
samples**, never trajectory count.

**Standing note for any future use:** C4 has an asymmetry worth carrying forward — **rejecting** a confound is cheap and
robust, **confirming** a genuine invariant is coverage-limited. For screening work that asymmetry is the right way
round.

---

## C5 — ON-SUBSTRATE DETECTABILITY (added 2026-08-21, after §174)

The four clauses above are necessary and **not sufficient**. §174 produced a CERTIFY that passed C1–C4 and was
worthless.

> **C5. The readout must be demonstrated to detect a genuine positive ON THE SUBSTRATE WHERE THE NULL IS ISSUED.**
> Not on a related system, not in a matching regime — there.

**Why it is a separate clause.** §174 screened bumped Kerr at momentum degree 4 and found no surviving direction:
known invariants representable to ~3e-12, known-fail correctly excluded, conditioning gated, out-of-sample. Clean
by every existing standard. The on-substrate control then showed that withholding Carter at ε=0 — where it is
genuinely conserved — left it **invisible** (separation 1.277 vs 1.077 with it included). The readout could not
see a standout on that spacetime even when one was certainly present, so "no survivor" was the instrument
finding nothing.

**The failure it closes has a name: validation by REGIME MATCH.** §173 had validated the readout at two Killing
vectors *on the Cariglia–Galajinsky substrate*, and bumped Kerr has two Killing vectors with a comparable
reducible list. The inference did not transfer. **Readout capability is substrate-specific and must be measured
where it is used, not inferred from where it was validated.**

**How to satisfy it.** Withhold a known invariant from the reducible set (or let a pinned constant vary) and
require the readout to recover it — *and to recover specifically it*, not merely "something conserved". A design
that whitens every known invariant away has, by construction, nothing left to demonstrate with.

### First audit under C5: §161 Candidate B — PASSES, and the gap was real

§161 filed a CERTIFY on the bridge's Candidate B. Candidate A emitted an exact quadratic invariant (2.2e-19),
which demonstrates the readout **on A**; A and B are different metrics. Worse, B's ensemble pins the energy shell
(H2 = 0.10 for every trajectory) precisely so the manifest constants whiten out — sound against false positives,
and it removes the only quantity that could have served as an on-substrate positive. **By construction there was
nothing on B the readout could be shown to find.**

Tested (§175) by rebuilding B's ensemble with the shell **varying**, making H2 a genuine conserved quantity with
across-ensemble spread 0.285 (against exactly 0 in §161):

    deg2 poly   best held-out ratio  1.75e-26        H2 representable   1.13e-14
    deg2 rat    best held-out ratio  8.57e-26        known-fail repr.   3.33e-02
    deg4 poly   best held-out ratio  2.74e-24

**The readout does detect a genuine invariant on B's substrate.** §161's CERTIFY stands, with C5 now satisfied
retroactively, and the verdict filed with the bridge is unchanged.

**The instructive asymmetry.** §174 and §161 had the *same* structural weakness — a null issued without an
on-substrate demonstration. In §174 the gap was **real** (the instrument genuinely could not answer there); in
§161 it was **only a gap in the demonstration** (the instrument could answer, nobody had shown it). Same shape,
opposite resolutions, and no way to tell which from the outside. That is precisely why C5 has to be *measured*
per substrate rather than argued.
