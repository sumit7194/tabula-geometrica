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

### C5 refinement 1 — the positive must match the certify in DEGREE

§174's C5 test withheld Carter, which is **degree 2**, while certifying at **degree 4**. It failed anyway, so
that verdict is unaffected. But a script that *passes* C5 using a low-degree positive while certifying at high
degree has a **weak pass**: nothing was shown about the instrument at the degree that matters.

> **C5 is only as strong as the degree and complexity of the positive used to demonstrate it.** Record the
> positive's degree alongside the certify's degree; a gap between them is a caveat, not a pass.

### C5 refinement 2 — "same system, different parameter" is not automatically the same substrate

ansatz's caution, and it kills the assumption that the emit-at-one-parameter / certify-at-another family passes
by construction: **the parameter change may itself alter what is representable.** On their metric ε=0 collapses a
degree-11 denominator to degree 4, so their ε=0 control validated a materially different basis from the one
issuing the ε=2 null — regime match wearing a different coat, and they retracted the claim on that basis.

**Checkable, not arguable.** Measured on §168, whose library *is* ε-dependent (it carries the inverse-metric
components), with a fixed analytic target evaluated on each substrate's own ensemble:

    eps      p_kept   Carter repr    L repr    L^2 repr
    0          179      3.52e-07    1.13e-08   1.18e-08
    2          180      1.56e-06    1.08e-08   1.26e-08
    5          179      2.44e-06    1.05e-08   1.26e-08
    10         181      2.92e-06    1.34e-08   1.75e-08

Flat: Carter degrades 8× and stays the same order, L and L² are unchanged, retained dimension stable. **§168's
ε-dependent basis does NOT materially alter representability, so its ε=0 control transfers.** Their failure mode
was specific to a denominator-degree collapse and has no analogue here — but that is now measured rather than
assumed, which was the point.

*(Noted in passing: §168's absolute representability is only ~1e-7/1e-8, limited by the conditioning truncation
at tol 1e-9 — the same limit §174 diagnosed and fixed with tol 1e-13. It does not affect the degree-2 verdict,
whose on-substrate positive is the reducible set, but it is the ceiling on anything asked of that library.)*

## THE C5 AUDIT — status of every certify-bearing result in this repo

17 results carry a CERTIFY verdict; 13 are gated in verify.sh. Audited so far:

| result | certify degree | on-substrate positive | degree of positive | C5 |
|---|---|---|---|---|
| §161 Candidate B (**filed with the bridge**) | ≤6 | H2 recovered at 1.75e-26 with the shell varying (§175) | 2 | **PASS** (weak on degree) |
| §168 degree 2 | 2 | the 6 reducibles recovered on the deformed substrate | ≤2 | **PASS** (degree matched) |
| §174 degree 4 | 4 | Carter withheld at ε=0 stays invisible (sep 1.277 vs 1.077) | 2 | **FAIL → REFUSED** |
| §167 | 2 | K0 rediscovers Carter at ε=0; basis is ε-**independent** (`library(T, deg, rational)`) | 2 | **PASS** |
| §162 (4 bases, **filed with the bridge**) | ≤6 | H2 recovered in *each* basis: 1.4e-26 / 5.3e-26 / 8.5e-25 / 3.0e-23 | 2 | **PASS** (weak on degree) |

Out of scope (measurement-based, not search-based): §141, §142, §143, §145, §147, §150, §151.
§171 carries a CERTIFY string but *is* a positive control (it finds tr L⁴ at Q2) — no separate audit needed.
| §93 | 2 | engine at the integration floor at certifying λ (0.4, 0.5) | 2 | **PASS** |
| §94 | ≤4 | engine below the floor at certifying α (9.0e-10 vs 4.8e-07) | 2 | **PASS** |

Still to audit: **§95, §160, §166**. All five of §93/94/95/160/166 were checked structurally for refinement 2 —
each builds features from state alone (`library(X,Y,PX,PY)`, `lib(...)`, `poly_features(T)`), with no system
parameter passed in and no module-level parameter read inside — so the basis **cannot** vary with the parameter
and ansatz's ε=0 failure mode is excluded by construction rather than by argument.

### C5 scope — the clause applies to SEARCH-BASED nulls, not to measurement-based verdicts

Sorting the 17 certify-bearing results showed they are two different kinds of object and C5 only bites one:

- **Search-based nulls** — "we looked in a named family and found nothing". The verdict is the *absence of a
  find*, so it is worthless unless the instrument was shown able to find. **C5 applies.**
  (§93, §94, §95, §160, §161, §162, §167, §168, §174)
- **Measurement-based verdicts** — the certificate is a *positive measurement* that crosses a theorem's
  threshold: §142's CERTIFY-CONTEXTUAL is a measured CHSH of 2.83 > 2, not a failed search. Nothing was looked
  for and not found. **C5 does not apply**; what those need is instrument calibration, which they already carry.
  (§141, §142, §143, §145, §147, §150, §151)

The distinction matters because applying C5 to the second group would demand a control that makes no sense there,
and skipping it for the first group is how §174 happened.

### §162 audited — four bases, all PASS

§162 certifies Candidate B across **four** bases, and §175's demonstration was in the polynomial basis only. Per
refinement 2 a different basis is closer to a different substrate than it looks, so each arm needs its own C5.
Run on §175's varying-shell ensemble (H2 spread 0.298, H drift 4.3e-14):

    arm                p    H2 representable   best held-out   finds a positive
    1 polynomial      23        3.32e-14          1.37e-26           YES
    2 rational        32        3.16e-14          5.32e-26           YES
    3 log-coordinate  44        3.41e-14          8.48e-25           YES
    4 transcendental  38        3.24e-14          2.95e-23           YES

Arm 4 was the one at risk — its `exp(a·px² + b·py² + g·px·py)` features could have displaced the polynomial
monomials H2 needs — and it does not: the polynomial block survives alongside them, H2 stays representable at
3.24e-14, and the readout recovers it at 2.95e-23. **All four §162 certifies carry an on-substrate demonstration.**

**Degree caveat, per refinement 1.** These demonstrate the instrument at **degree 2** while §161/§162 certify out
to **degree 6**. That is a real pass and a *weak* one. Closing it properly would need a degree-6 positive on
Candidate B, which does not exist to plant — so the caveat is recorded rather than quietly upgraded.

### §93 and §94 audited — both PASS, and the two-run pattern is the general recipe

Both scripts pin the energy shell, so H is whitened out of the eigenproblem and there is nothing on-substrate to
demonstrate with — §161's situation, and the reason a naive C5 test on them returns a meaningless null.

**§93 (Pullen–Edmonds).** Its library has no `x²y²` term, so at the certifying λ the one conserved quantity that
certainly exists is **not even representable**: H residual 4.6e-11 at λ=0 but **0.79 / 0.85** at λ = 0.25 / 0.50.
With the shell varied *and* the basis augmented so H is representable (8.5e-15), the engine reaches the
integration floor:

    lambda   H rel drift   floor (var-ratio)   engine best   engine/floor
     0.25      7.98e-05        3.62e-07         1.36e-07         0.4
     0.50      1.29e-04        9.19e-07         4.52e-07         0.5

At/below the floor ⇒ **resolving, integration-limited, not blind**. §93's certify value is 0.62 — six orders
above that floor — so the verdict is safe by a wide margin. **PASS.**

**§94 (coupled quartic).** The cleanest structure in the repo: its integrable islands at α ∈ {0, 1, 3} sit
*inside the same parameter sweep* as the certifying α ∈ {2, 4}, identical basis, only α differing. Two runs:

    pinned shell (§94's real config)   engine: 1.1e-10 / 4.9e-19 / 2.3e-10 at islands,
                                               1.9e-04 / 1.8e-03 at CERTIFY  -> correct null
    varying shell (the C5 test)        floor 4.8e-07 / 1.0e-06 at CERTIFY,
                                               engine 9.0e-10 / 3.1e-09     -> BELOW the floor

**The pair is the demonstration.** With H varying the engine resolves it below the integration floor *at the
certifying α*; with H pinned it correctly finds nothing, because no second invariant exists there. So the null is
about the physics, not the readout. **PASS.**

> **The recipe, generalised:** when a design pins a constant to whiten it out (correct, against false positives),
> run the C5 test on a *second* ensemble with that constant varied. The pinned run gives the verdict; the varied
> run gives the demonstration. Neither alone is sufficient and the two together cost one extra ensemble.

**Four wrong turns inside this audit, every one producing a plausible number**, recorded because the ratio matters
more than the result: (i) the pinned shell whitening the target away, so a null meant nothing; (ii) the target not
representable in the certifying basis; (iii) a within/total variance ratio computed on an ensemble with **no
across-ensemble variance**, which returns ~1 for a perfectly conserved quantity; (iv) comparing a *relative drift*
against a *variance ratio* — a units error. The third nearly landed: it read as "the engine cannot resolve at
λ>0", which would have downgraded a shipped verdict, and it was wrong on two counts at once.

### §95, §160, §166 audited — the C5 audit is COMPLETE (17/17)

**§95 (anisotropic quartic).** Two-run recipe. Engine resolves H below the integration floor at every certifying
point, including the κ=2 open family where §95's most interesting claim lives:

    (alpha,kappa)   H repr     floor      engine best     kind
    (0, 1)         6.4e-15   1.62e-06     1.84e-10       island
    (2, 1)         5.0e-15   2.50e-06     4.79e-09       certify
    (1, 2)         9.2e-15   1.58e-06     3.33e-09       certify (open family)
    (3, 2)         3.9e-15   2.51e-06     5.71e-09       certify (open family)

**PASS.**

**§160 (basis ladder) — a SECOND satisfaction structure, and the cleaner one.** Its Hamiltonian is deliberately
transcendental in the momenta, so H is genuinely unrepresentable in the poly/rational rungs where it certifies
(9.97e-04, 3.22e-04) — and the **transcendental rung emits at 1.66e-22 on the same ensemble**. The engine's
1.09e-06 / 1.23e-07 in the lower rungs is a polynomial best-approximation, the §97 signature, not an exact
invariant.

> **THE LADDER CONTRAST SATISFIES C5 BY CONSTRUCTION.** If a design certifies in basis A and emits in basis B on
> *one ensemble with one engine*, the demonstration is internal: only the basis changed. No second ensemble is
> needed. This is strictly better than the two-run recipe where it is available, because nothing about the
> substrate varies between the demonstration and the verdict.

**PASS.** (ansatz has since taken this further: their *denominator* ladder gives rank-4 solution space 8 at den¹
against a reducible span of 9, the single difference being H² which requires den² — self-validating *and* it
names its own scope limitation as an object rather than as "we truncated".)

**§166's own S3 (chaotic Hénon–Heiles) — and it produced a FALSE PASS first, which is the entry worth keeping.**

    first attempt   H spread 0.0000   floor 9.1e-01   H repr 9.96e-01   -> criterion "passed"
    corrected       H spread 0.1501   floor 4.50e-11  H repr 4.31e-15   engine 4.44e-11 (ratio 0.98)

§166 pins E = 0.15, so H had **no across-ensemble variance**, the floor degenerated to ~1, and the criterion
`best ≤ floor × 10` became **unfailable**. It reported PASS by arithmetic. Two fixes were needed together —
vary the energy (H findable) *and* augment the basis with the cubic terms x²y, y³ (H representable, since
Hénon–Heiles is cubic and the degree-2 library cannot hold it). Corrected, the engine sits exactly at the
integration floor. **PASS**, and this time the criterion could have failed.

**Fifth appearance of the degenerate-denominator trap, third against us specifically.** ansatz's formulation is
the one to keep: *a statistic inverts its meaning when its denominator degenerates, and the degenerate case is
exactly where a null lives.* Same family as their scale-free σ_min/σ_max — the normalisation that makes a
quantity comparable is the one that makes it meaningless in the degenerate case.

## FINAL C5 AUDIT — 17/17

    PASS  §93  §94  §95  §160  §161-B  §162(4 bases)  §166  §167  §168-deg2
    FAIL  §174 deg-4  -> REFUSED (retracted 2026-08-21)
    N/A   §141 §142 §143 §145 §147 §150 §151  -- measurement-based, not search-based

Both verdicts filed externally with TheBridge (§161, §162) came back clean. The one genuine failure, §174, was
caught and retracted before it propagated. **Two satisfaction structures exist:** the ladder contrast (internal,
preferred) and the pinned/varied two-run recipe (for designs that whiten a constant out).

### C5 refinement 3 — a cross-parameter claim must be gated on GAIN STABILITY, not on the floor

TheBridge's correction, accepted. Three of the C5 passes above are **cross-parameter claims**: §93 (emit at λ=0,
certify at λ = 0.25/0.5), §94 (emit at the islands α ∈ {0,1,3}, certify at α ∈ {2,4}), §95 (emit at (0,1),
certify at (2,1) and the κ=2 family). All three were validated against the **integration floor**.

> **Floor is the wrong property for a claim that spans a comparison axis.** Floor is statistical error and
> averages down as 1/√N; **gain variation along the axis is systematic and never averages down at any N**. If the
> readout's sensitivity drifts with the parameter, an "emits here, silent there" contrast can be a sensitivity
> gradient wearing the costume of physics, and a floor check cannot distinguish the two.

Their sharper form of the same family: gating on noise alone selects for **deafness** (an instrument returning
zero has a perfect floor), and gating on SNR selects the **distorting** instrument. The right property is
determined by the claim's shape — single-setting claims need SNR, cross-parameter claims need gain stability.

**Status:** handed to TheBridge as an **independent** measurement — plant a synthetic conserved quantity of known
amplitude at each α on §94's system and measure recovered/planted gain across the axis. Flat gain ⇒ the contrast
is physics; gain degrading at α = 2, 4 ⇒ §94's pass measures sensitivity and needs re-scoping. They did not build
any of this instrument, which is the property we cannot manufacture for ourselves.

### C5 refinement 4 — non-degeneracy is not discrimination

Also TheBridge's, from a live instance in their own work: a gate conjunct passed a **non-degeneracy** check (50
distinct values across 50 orbits — genuinely varying, well-conditioned) while simultaneously clearing its own
firing threshold by 993× on a *provably integrable* metric. Alive and uninformative at the same time.

> **Aliveness is a one-sample question ("does this vary?"). Discrimination is a two-sample question ("does its
> distribution on the control differ from its distribution on the signal?").** A check of the first form does not
> do what it appears to.

**Audited against it.** §93/§94/§95 carry a genuine two-sample contrast: the engine's best differs by 6–15 orders
between emit and certify parameters. **§166's S3 is the weak one** — a single chaotic Hénon–Heiles case whose
evidence is "the engine sits at the integration floor", one sample with no in-family contrast. Its contrast
exists only across §166's *other* gates (S1 Kepler, where a genuine second invariant is found), which is weaker
than an in-family contrast. Recorded, not smoothed.

### C5 refinement 5 — A THRESHOLD MUST BE REACHABLE BY THE INSTRUMENT AT EACH OPERATING POINT

The sharpest entry the audit produced, and it has an independent precedent in a sibling repo.

**What happened.** §161/§162 certify across a ladder of momentum degrees {2, 4, 6}, with an EMIT criterion of
**< 1e-10** applied uniformly. Testing with H2 — known conserved, and representable at *every* rung (3.8e-14 to
1.3e-13) — the engine's best achievable was:

    deg 2  poly/rational   1.18e-26 / 4.29e-26    CAN emit
    deg 4  poly/rational   5.27e-25 / 3.07e-12    CAN emit
    deg 6  poly/rational   9.85e-10 / 2.96e-09    CANNOT emit

**At degree 6 the instrument could not reach its own emit threshold**, so that rung could not have emitted
regardless of the physics. Its certify was correct-but-undemonstrated: the instrument could not have said
anything else. Not a bad basis, not a degenerate denominator — **a threshold set beyond the instrument's reach at
that operating point.**

> **Check that your threshold is reachable by your instrument at each operating point before gating on it.**
> It hides specifically in **LADDERS**: a threshold validated at one rung is silently inherited by rungs with
> different resolution, and the unreachable rung is usually the one that looks most decisive.

**Repairable, and repaired.** The cause was a missing conditioning step — §161 feeds raw features of wildly
different dynamic range straight into the eigenproblem. Applying §174's SVD-conditioning basis at tol = 1e-11:
degree-6 poly **9.85e-10 → 4.30e-26**, rational **2.96e-09 → 3.95e-25**, with the retained dimension *unchanged*
(96, 141). It is the rescaling, not truncation.

**The negative control, which TheBridge insisted on before the verdict and was right to.** A rescaling worth
sixteen orders could plausibly manufacture emissions. It does not: on §161's **own pinned ensemble** — a genuine
null substrate, since the manifest constants are whitened out by design — the conditioned degree-6 rung returns
**2.29e-05**, a 12% change from unconditioned. Sixteen orders where a real signal exists, 12% where none does.
**The rescaling amplifies signal, not noise.**

**The resulting threshold geometry** (their question: is 1e-10 comfortably above the new floor, or merely on the
right side of it?):

    null-substrate floor, conditioned, deg 6    ~1e-5      what "nothing there" reads
    emit threshold                               1e-10     5 orders BELOW the floor
    genuine signal (H2), conditioned, deg 6      4.3e-26   16 orders below the threshold

Conservative, not marginal. Unmeasurable before the repair, because the unconditioned instrument's floor and its
resolution were the same number.

**Verdict status:** B still CERTIFIES at every rung (7.5e-04 down to 1.4e-05, all far above 1e-10). §161/§162's
results were always right; what was missing was the demonstration at the top rung, which now exists.

**Independent precedent — same species, nine days apart, no contact.** TheBridge's G3 run 1 (2026-07-26) returned
UNDECIDED(search) because their frequency-drift measure's smallest readable value was 2/N = 0.0333 while the
target sat at 0.027 — **the signal was beneath the instrument's floor**, and every δ returned an identical
6.67e-02 *including integrable Schwarzschild*. Both repairs recover resolution without discarding data (their
parabolic sub-bin FFT interpolation, our SVD rescaling). Both gates returned a clean-looking verdict rather than
an error. Their sting is worth carrying: **a better floor is still a floor** — after repairing, re-measure where
the new floor sits rather than assuming the old threshold still clears it.

### A note on over-generalising a rule one has just been burned by

I warned TheBridge that a pinned shell makes the within/total ratio unfailable and told them to vary E0. They
kept it pinned and pre-registered why: their plant was *synthetic* and carried its own across-ensemble variance,
and the pinned shell is the configuration §94's certificate actually runs in. They were right. Their diagnosis of
my error is better than mine: **a true rule applied one case too wide.** The rule governs natural quantities,
whose across-ensemble variance the design controls; it does not govern synthetic plants that supply their own.
Having just been burned by the degenerate-denominator trap three times, I generalised the fix past its domain —
which is its own failure mode.

### C5 refinement 5, closed — the conditioning repair is validated, and a directional argument is retired

**TheBridge's structural result, which is stronger than any control we ran.** The generalised eigenproblem
`Cw v = λ Ct v` is **invariant under invertible linear reparametrisation of the feature basis**: `F → FD` sends
`Cw → DᵀCwD` and `Ct → DᵀCtD`, leaving the eigenvalues unchanged. SVD rescaling at unchanged dimension is such a
map. **So in exact arithmetic the conditioning is a no-op** — it cannot change what the criterion *says*, only
what a finite-precision solver can *resolve*. Therefore the sixteen-order recovery is necessarily numerical, and
**a reparametrisation cannot manufacture a signal that is not in the data.**

**Their discriminating test — a plateau under tightening precision.** A genuine resolution recovery converges;
solver noise wanders. Measured:

    deg 6 poly       none 9.849e-10 | 1e-9 4.300e-26 | 1e-11 4.300e-26 | 1e-13 4.300e-26 | 1e-15 4.300e-26
    deg 6 rational   none 2.961e-09 | 1e-9 3.948e-25 | 1e-11 3.948e-25 | 1e-13 3.948e-25 | 1e-15 3.948e-25

Identical across **four decades**, kept dimension fixed. The repair is validated. Their earlier recommendation —
run a negative control — they retracted themselves as the *wrong* test: given the invariance, a reparametrisation
could never have manufactured signal, so the null was always going to pass and discriminated nothing.

**A DIRECTIONAL ARGUMENT, RETIRED.** They proposed that ill-conditioning drives the ratio spuriously *small*
(toward false EMISSION), so an all-CERTIFY ladder would be robust by direction without any control. **Measured
here, the sign is opposite.** Against H2's own within/total ratio computed directly on the data:

    ground truth                  2.015e-28
    unconditioned      9.849e-10   INFLATED by 18 orders
    conditioned 1e-11  4.300e-26   inflated by 2 orders

Ill-conditioning **inflates** in this setup — toward false CERTIFY, precisely the direction every verdict in the
ladder sits in. So the unconditioned certifies were structurally at risk, and re-running them was the check that
mattered rather than bookkeeping.

> **Two constructions, two opposite signs. The direction of a conditioning bias is a property of the particular
> basis and spectrum, not of ill-conditioning as such. Neither side should use a directional argument to skip the
> measurement.** This outranks either specific result.

**Residual honesty:** even conditioned, the engine's best sits ~2 orders above the data's own floor (4.3e-26 vs
2.0e-28). Irrelevant to this verdict — the threshold is 16 orders away — but 4.3e-26 should not be read as exact.

**Final status of the filed verdicts:** §161/§162 certify Candidate B illegible relative to {polynomial,
rational} at momentum degrees **2, 4 and 6**. The degree-6 rung required a conditioning step §161 as-run did not
apply; without it that rung could not reach its own emit threshold. Conditioned, the recovery plateaus and the
verdict is unchanged. B still certifies at 1.44e-05 at degree 6 — five orders above threshold.

### New catalogue entry — agreement between two noise figures reads as corroboration

TheBridge withdrew their own corroboration of our 12% figure on noticing that their normalised and raw baselines
agreed to four digits (8.596e-13 vs 8.597e-13). They had read that as "the ill-conditioned variant behaved well".
It actually means **the reparametrisation did nothing** — it *is* the invariance. Two noise figures coinciding
presented as an independent measurement agreeing with ours.

> **Before treating agreement as corroboration, check that both quantities were free to disagree.** Two
> measurements of nothing agree perfectly.
