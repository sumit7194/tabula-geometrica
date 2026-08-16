# P3 (with P4 folded in) — tabula's half: PRE-REGISTRATION, frozen 2026-08-16 before any code

**Authorized by the user in this session** (standing authorization, 2026-08-16). Joint item with ansatz,
who own the symbolic half. This document freezes **our** half only, and is written to be handed to them
before we start so the division of labour is agreed rather than assumed.

## The question P3 asks

Leg J left this genuinely open, not merely unfinished: deformed Kerr is *"formally non-integrable,
dynamically regular"* — no Killing–Yano tensor to degree 4, thin-layer chaos only at ε≈0.98, Carter drift
bounded 7→18% — but **whether any higher-rank Killing tensor survives is undetermined.**

**The translation into our currency.** A rank-`r` Killing tensor corresponds to an invariant that is a
degree-`r` homogeneous polynomial in the momenta. So P3's "rank 3–4" is **momentum degree 3 and 4** on the
ladder — and it sits at the *top of the first rung of the momentum axis*, not off it, because the whole
analytic-in-p axis is decidable and finite by the grading theorem. Note degree 3 is **odd**, and every
library we have ever built used even total degree only (these metrics' known invariants are even under
t→−t, φ→−φ). Odd degree is therefore a genuine extension, and one we should not assume is empty.

## What our half produces (and, explicitly, what it does not)

We produce a **cheap numerical screen** that tells the symbolic prover where to spend expensive exhaustive
effort. Each rung of the ladder returns one of three things:

- **CERTIFY-NO-INVARIANT-IN[F, order N]** — cheap rule-out, all four clauses passed.
- **ESCALATE** — something survives screening and deserves symbolic certification.
- **REFUSED-LIBRARY** — the conditioning gate rejected the library. **This is not a null** and must never be
  absorbed into one; "I could not condition this" ≠ "nothing is there".

**What we never claim:** non-existence outside a named family. *The union over screened families is a map of
where we looked, not a theorem — therefore the escalation list is the deliverable, not a leftover.*
Only symbolic certification converts a rung into a theorem. The handoff is one-directional by design: we can
save ansatz work; we cannot do their half.

## Method: the invariant COUNT, as a function of deformation and rung

A design decision worth stating, because it differs from §161. There we fixed the manifest constants
globally so they were whitened out and any hit was necessarily new. Here we do the opposite — we let the
manifest constants **vary across realizations**, so that:

1. the engine must first recover the *known* invariants (a sanity check the chain works at all), and
2. C4's positive control (a manifest invariant, measured in the identical harness) is available in-band,
   which the §166 correction showed is required for the clause to be self-calibrating.

The screening statistic is then the **conserved-subspace dimension**, `null(W) − deficiency(F)` (C2),
compared against the number of *known* invariants spanned by that library. **Excess ⇒ ESCALATE. Equal ⇒
CERTIFY.** The whole P3 question becomes: *does the count drop by exactly one when the deformation kills
Carter, or does something replace it?*

Every rung carries the §166 four-clause certificate: **C1** basis named · **C2** conditioning gated ·
**C3** out-of-sample realizations · **C4** state-functionality vs positive control.

## Pre-registered gates (frozen before the script exists)

- **K0 — INTEGRABLE CONTROL LIMIT (the single most valuable item, per §144's lesson).** At ε=0 (undeformed
  Kerr-like), the ladder EMITS the Carter constant at momentum degree 2: conserved-count = known-count
  *including* Carter, held-out ratio at machine precision, and all four clauses pass. This validates metric
  transcription, integrator, library, engine and certificate **independently of the adversarial question**.
  Without it a CERTIFY at ε≠0 cannot be distinguished from a transcription bug.
- **K1 — CARTER DIES UNDER DEFORMATION, MEASURED.** At the deformed parameter the degree-2 conserved count
  drops by exactly one relative to K0, with the drift/held-out separation reported in the §132
  relative-exactness form (>1e6× the integrable floor), never as an absolute threshold.
- **K2 — THE RANK 3–4 SCREEN (the open question).** Momentum degrees 3 and 4 × coordinate classes
  {polynomial, rational}, deformed. For each rung report the full certificate and one of the three verdicts.
  **Both outcomes are results and both are pre-registered:** an ESCALATE at any rung is a lead for ansatz's
  prover; a clean CERTIFY across all rungs converts leg J's diagnosis into *"no invariant representable in
  {poly, rational} × momentum-degree ≤ 4, conditioning-gated, out-of-sample validated"* — which is a real
  statement about where the invariant isn't, and exactly the certified-null genre.
- **K3 — CONDITIONING HONESTY.** Any rung with `rank(F) < p` is reported REFUSED-LIBRARY and excluded from
  the certify count. Gate: the report distinguishes refused from certified rungs; no rung is silently
  absorbed.
- **K4 — THE ESCALATION LIST IS THE DELIVERABLE.** The output is an explicit, ordered list of what survived
  cheap screening and therefore merits symbolic effort, with the reason per item.

## Honest limitations, stated up front

- Odd-degree (rank 3) invariants may be structurally forbidden here by the metric's discrete symmetries. If
  so the rung is *trivially* empty and must be reported as such, not counted as an informative certify.
- C4 confirms only with ensemble coverage (measured in §166); it **rejects** cheaply and robustly. On rungs
  where coverage is thin, C4 is reported as uninformative rather than passing.
- C2's correction inherits §165's rank-estimate sensitivity (exact at full sampling, ±1 at coarse).
- Our numerical certify is evidence of absence **only relative to F**; our emit is a **pointer, never a proof**.

---

## Post-run record (2026-08-16) — all five gates green, after THREE corrections (two of them to this document)

**Result.** K0 ✓ K1 ✓ K2 ✓ K3 ✓ K4 ✓. Full run 5m35s. `results/167_p3_killing_tensor_screen.json`.

**Headline.** At ε=0, with only the reducible L-powers deflated, the engine **rediscovers the Carter constant
unaided** in the 57-dim complement (cos to the known Carter vector 0.975, held-out 3.1e-26, Carter drift 9.5e-29).
At ε=0.35 the bump destroys Carter (drift 6.6e-2 = **7.0e26×** the integrable floor) and *the identical search
finds nothing in its place*. Across momentum degrees 3 and 4 × {polynomial, rational}, with all reducibles
deflated so any survivor is irreducible by construction, **nothing survived at any rung** — an empty escalation
list, which is a real result and was pre-registered as one.

### Correction 1 — the K0 control FAILED first, and the cause was ensemble coverage, not numerics

K0 initially returned count 2 against a reference of 3, at ε=0 where Carter is conserved to 2.0e-15. Diagnosis by
elimination: all three known invariants {L, L², K} were *exactly* representable (projection residual ~1e-14) and
their explicit fits scored held-out 4.6e-29 / 1.8e-29 / 2.5e-18 — so the conserved subspace really was
3-dimensional and the engine was under-counting. Not conditioning (the count was invariant across four decades of
pruning tolerance). The cause was `L_LO, L_HI = 0.85, 1.15`: over a ±15% band **corr(L, L²) = 0.99923**, so two of
the three conserved directions are numerically near-parallel and the solver resolves only two. Widening to ±50%
(corr 0.9917) resolves all three at machine precision with a ~20-decade gap.

**The ensemble must SPAN enough for the invariants to be independently resolvable.** This is §166's C4 coverage
limitation reappearing on the counting side, and it is the second time in two scripts that coverage — not
algorithm — was the binding constraint. K0 existed precisely to catch this class of thing before a production
claim, and it did.

### Correction 2 — the verdict logic silently certified on UNDER-count

The first working version read `CERTIFY if count <= expected`. Three rungs returned count < expected and were
reported as clean rule-outs. A rung that cannot recover the invariants *already known to be there* has not been
screened at all; certifying from it is precisely the failure the certificate standard exists to prevent. Now an
under-count is **REFUSED-LIBRARY**, never absorbed into a null (K3).

### Correction 3 — the statistic is the IRREDUCIBLE QUOTIENT (ansatz's correction, adopted)

ansatz pointed out that every rung is populated by reducible products of the known invariants, so the raw count
must be compared against the reducible baseline, not against one. Adopted, and taken one step further for a
numerical reason: rather than *compare against* the baseline we **deflate it out of the feature space before the
eigenproblem**. The reducible directions are near-parallel powers of a single scalar — the nastiest directions in
the problem, and the ones that refused three rungs. In the deflated complement the null expectation is exactly
zero and any survivor is irreducible by construction. This also buys the stronger control above: leave Carter
undeflated at ε=0 and the engine must *rediscover* it, which checks **what** was found and not merely how many.

### Two claims in this pre-registration are WITHDRAWN

- **"Odd degree may be structurally forbidden by the metric's discrete symmetries."** Withdrawn. ansatz's
  counterexample is decisive: p_t and p_φ are themselves degree-1 (odd) invariants, so odd-degree conserved
  quantities manifestly exist for this metric class. The involution t→−t, φ→−φ **grades** odd invariants into its
  odd eigenspace; it does not exclude them. Our libraries already included odd degrees, so no code changed — but
  the prose was wrong and the rung must never be reported as trivially empty.
- **"The whole analytic-in-p axis is decidable and finite by the grading theorem."** Withdrawn. ansatz verified the
  grading half symbolically (for *geodesic* flow the bracket raises momentum degree by exactly one, k→k+1 for
  k=0..5, so the rungs are independent and cannot cancel each other) and separately showed the finiteness half does
  not follow: each fixed degree is a finite-dimensional decidable problem, but **nothing bounds the degree**. Also
  worth carrying: with a potential added the bracket lands in *two* slots (k±1) and only parity decouples, so the
  grading result is specific to geodesic flow and must not be restated as a general Hamiltonian fact.
  Consequence: the certificate reads **"screened to degree 4"**, and the degree axis now carries the same sentence
  the family axis always did — *a map of where we looked, not a theorem*.

### Metric identity — checked, and the sharpest version of ansatz's worry does not apply

ansatz flagged that if our object were Stäckel-separable at ε≠0 it would be integrable *by construction* and the
two halves would be answering different questions under one word. Checked: our deformation enters as
`ε·(r−R)²·cos²θ`, a **product** of an r-function and a θ-function, which breaks the additive Stäckel form
`N = N_r(r) + N_θ(θ)` — separability is exactly what it destroys, as in theirs. So the screen is not trivially
integrable. **But the objects are still not the same:** ours is a Kerr-*like* Stäckel-form toy with a harmonic trap,
theirs is Kerr in Boyer–Lindquist with `g_tt × (1 + ε(3cos²θ − 1)/r³)`. Their request to share a metric exactly is
correct and is the next build; this run validates the instrument, not the specific spacetime. Also recorded from
them: the bumped metric is **not a vacuum solution** (R_ab ≠ 0), legitimate as a geodesic testbed but it must be
described that way, and their leg-Q "bumpy" metric (`1 + 6εcos²θ/r`) is a **third, inequivalent** object — the word
"bumpy" must not merge them.

### Honest scope of the result

- CERTIFY here means: **no irreducible invariant representable in {polynomial, rational}(coord) × momentum-degree
  ≤ 4**, conditioning-gated and out-of-sample validated, **on our Kerr-like toy** — not on ansatz's bumped Kerr,
  and not beyond degree 4.
- C4 (state-functionality) is **vacuous** in this setting: the library is built purely from state with no auxiliary
  channels, so nothing can fail it. Run and reported for completeness; C1–C3 do the work. C4 earns its place in
  real-data screening, which is where §166 built it.
- ansatz's cheaper **informativeness pre-filter** (does the emitted quantity separate orbits? planted constant
  scores 0.0, a real invariant 3.1e-1) is a strictly cheaper first pass than C4's coverage-hungry confirm step, and
  should sit ahead of it in any future screen.

---

## Transcription to ansatz's metric (script 168, 2026-08-16) — HONEST PARTIAL: degree 2 certified, degrees 3–4 NOT screened

§167 validated the instrument on *our* Kerr-like toy. ansatz asked that both halves share the object exactly, and
sent their parameters verbatim: Kerr in Boyer–Lindquist with `g_tt × (1 + ε(3cos²θ−1)/r³)`, spin **a = 3/5**,
canonical sweep **ε = 2, 5, 10** (large, *not* perturbative — never to be quoted beside our toy's 0.35), RK4.
Recorded from them: **not a vacuum solution** (R_ab ≠ 0), and their leg-Q "bumpy" metric is a third, inequivalent
object. Here E, L **and** H all vary across realizations — which also closes the scope gap ansatz identified in
§167, where H was held fixed at a band of zero width.

**What is established (B0, B1).** At ε=0 the control recovers Carter *inside the conserved span* (residual
1.6e-06) and the conserved set is exactly the 6 reducibles + Carter. At ε = 2, 5, 10 the bump destroys Carter —
drift **2.1e-3 → 1.0e-2 → 3.8e-2, growing monotonically**, 1.3e24 → 2.4e25× the integrable floor — and the search
finds **exactly the 6 reducibles and nothing else**. This independently reproduces ansatz's §85 degree-2 result in
a different harness, integrator and basis.

**What is NOT established (B2).** The rank 3–4 question — the actual open part of P3 — **remains unscreened on
their metric**. Three of the four degree-3/4 controls fail outright (the ε=0 run does not cleanly recover Carter
at those library sizes), and the one whose control passed was **withdrawn for instability**: it reported 31, 15
and 12 irreducible directions at ε = 2, 5, 10. A genuine invariant does not change multiplicity with the
deformation, so that is the instrument's noise floor being crossed, not a discovery. §167's empty escalation list
at degrees 3–4 was obtained on *our toy* and does not transfer.

**Five instrument bugs found and fixed on the way, each caught by a control rather than by inspection.**
1. *Carter's mass term.* Drift sat at 2.1e-4 **independently of the timestep** — the tell that it was a
   transcription error, not integration error. K = p_θ² + cos²θ[a²(μ²−E²) + L²/sin²θ] carries μ² = −2H, and the
   ensemble deliberately varies H, so hard-coding μ=1 was wrong.
2. *Greedy column pruning destroyed the result.* It keeps early columns and drops later ones; the metric
   components sit last, so exactly the columns H needs were dropped, H stopped being representable, the deflation
   missed it, and the engine reported H and its products as ESCALATE. Replaced by **SVD truncation**, which
   preserves anything representable in the full library whatever the column order.
3. *Coefficient-space deflation is unsound in an over-complete library.* The coefficient vectors for E, L, H and
   Carter are not unique, so projecting out one damages the others — measured, Carter went from conserved at
   6e-28 to 2e-3 *after* deflation. Replaced by a **subspace readout**: irreducible dim = rank[reducible |
   conserved] − rank[reducible], plus "does Carter lie in the conserved span".
4. *Vector-wise Carter tests are meaningless on a degenerate subspace.* Every eigenvector sat at cos ≈ 0.53 to
   Carter while the subspace was exactly right — the eigenbasis is an arbitrary rotation within it. Both
   replacement statistics are rotation-invariant.
5. *A floor calibrated at one rung does not transfer to another.* Calibrated at degree 2 (163-dim) and applied at
   degree 4 (442-dim), it let a rung report 441 "conserved" directions out of p=410. **Every rung now ships its
   own ε=0 control**, and a rung whose control fails issues no verdict at all.

**The through-line.** Four of these five would have produced a *confident wrong answer* rather than an error, and
every one was caught by a control whose answer was known in advance. That is the §144/§166 lesson paying for
itself twice in two scripts.

**Scope.** Degree 2 is screened and certified on their object. Degrees 3–4 are REFUSED at this configuration; the
binding constraint is ensemble coverage relative to library size (p grows to 250–580 while the conserved-subspace
readout degrades). Not run at larger scale — stated as a resource limit, not as a null.

## Correction (168b, 2026-08-16): "the binding constraint is ensemble coverage" was WRONG

§168 refused degrees 3–4 and attributed it to ensemble coverage relative to library size. That was an inference
stated as a finding — the same error ansatz and I had just caught each other making about the drift offset — so
168b measured it instead. **The inference is refuted.**

    rung                  p     control   Carter residual, ntraj 110 -> 1000
    deg2 rat+metric     179       OK      1.56e-6 -> 1.10e-6   (flat)
    deg3 rational       264       FAIL    3.63e-4 -> 3.01e-4   (flat, 9x the data changes nothing)
    deg3 rat+metric     355       FAIL    4.28e-3 -> 1.13e-3
    deg4 rat+metric     581       OK      3.23e-5 -> 2.52e-5

**The decisive fact is non-monotonicity in degree: degree 4 passes its control and degree 3 fails.** A larger
library (p=581) works where a smaller one (p=264) does not, and nine times more coverage moves degree 3 not at
all. Whatever refuses degree 3 is structural, not statistical, and more orbits will not fix it.

**And the probe localises it to our own readout, not to the physics.** At degree 3 the two estimators disagree:
`n_conserved − reducible_rank` = 13 − 12 = **1**, which is exactly "Carter and nothing else", while the
rank-difference statistic `rank[R|C] − rank[R]` reports **4**. At degree 4 they agree (22 − 21 = 1, irr = 1). So
the degree-3 rungs are plausibly fine and the subspace readout is miscounting them. Leading hypothesis: `_rank`
reads a gap of ≥1.5 decades and returns full rank when no such gap exists; the degree-3 conserved directions are
noisier (residual ~3e-4 vs 1e-6 at degree 2, 2.5e-5 at degree 4), so the combined spectrum decays smoothly and
the fallback inflates the count. Odd momentum degree is the obvious suspect for the extra noise — monomials odd
in (p_r, p_θ) average toward zero over orbits symmetric in the momenta — but that is a hypothesis, not a result.

**Status of §168's headline, unchanged:** degree 2 is still screened and certified on their metric; degrees 3–4
still issue no verdict. What changes is *why*, and therefore what would fix it: not more compute, but a readout
that does not depend on finding a spectral gap. Recorded as the concrete next step rather than a scaling request.

**Operational bug worth keeping.** 168b's first attempt was OOM-killed ~20 minutes in (feature matrix is
G × P × p float64; the degree-4 cell at ntraj=2000 needs ~15 GB) **with buffered output and no incremental
write, so every completed cell was lost**. A long detached run that only writes at the end is an all-or-nothing
bet. Now: `python -u`, a per-cell memory guard that reports skipped cells rather than silently omitting them,
and a flush after every cell.

## Readout investigation (2026-08-16) — STOPPED and reverted, with what it found recorded

168b showed degree 3 failing while degree 4 passed, so I tried to rebuild the irreducible-dimension readout. Four
successive patches, each fixing one artifact and exposing the next, is the signal to stop rather than continue,
so this was reverted to the committed state. What it established is worth keeping; what it did not, is not shipped.

**Established.** Project the conserved per-trajectory values onto the orthogonal complement of the reducibles and
look at whether the residual spectrum SEPARATES:

    deg2 rat+metric   [1.0, 3.6e-6, 9.5e-7, ...]      separation 2.8e5   one clean direction (Carter)
    deg3 rational     [1.0, 0.60, 0.49, 0.30]         separation 1.7     nothing stands out
    deg3 rat+metric   [1.0, 0.86, 0.68, 2.2e-5]       separation 1.2     nothing stands out
    deg4 rat+metric   [1.0, 0.94, 0.86, 0.73]         separation 1.1     nothing stands out

**Degree 2 is the only rung on this metric with separated conserved structure.** This also exposes degree 4's
earlier "control OK" as a FALSE PASS: the rank-difference statistic returned 1 while nothing actually stands out.
So the earlier hypothesis — *"the readout is miscounting and the degree-3 physics is fine"* — is **not supported**
and is withdrawn. At degree ≥ 3 there is no separated structure to count, which is a third answer, distinct from
both "coverage" and "miscount".

**Two traps caught inside the investigation, both worth more than the fix attempt.**
- *A control that cannot fail is not a control.* Calibrating the cutoff as the geometric mean of the first two
  singular values makes the control return exactly 1 **by construction**. It looked like four rungs passing; it
  was arithmetic. The separation ratio above is the non-definitional replacement.
- *A scale-free statistic cannot answer "is anything here".* Normalizing the spectrum by its own largest value
  sets `spec[0] = 1` identically, so every deformed rung clears any cutoff and ESCALATES. The normalization that
  makes rungs comparable is the same one that destroys the absolute question.

**Recorded for whoever rebuilds this:** ansatz's advice, which is right — when no gap exists the readout should
return **REFUSED**, not a number. The fallback's error was not the value it picked but that it answered at all.
And their cheap test for the odd-degree hypothesis before rebuilding around it: compute per-column ensemble
variance at degree 3 and check whether the odd-momentum columns are systematically smaller.

## ε=10 is not perturbative for ansatz, and is for us (their scope error, our radial cutoff)

They asked whether our orbits reach the region where their ε=10 stops being a perturbation. Measured:

    eps      our r range        our max|bump-1|      theirs
     0       [4.08, 11.91]         0.0000            —
     2       [4.04, 11.50]         0.0299            0.0075
     5       [4.09, 11.95]         0.0728            0.0453
     10      [4.07, 11.26]         0.1336            1.2548   (their orbits reach r = 2.00)

Our radial cutoff holds every orbit outside r ≈ 4, so at ε=10 our deformation peaks at 0.134 while theirs reaches
1.25 — larger than the function it multiplies, sign-flipping g_tt. Same ε, different spacetime region. That
accounts for the 7.6× disagreement at ε=10 with neither side being wrong, and it closes the question exactly as
they predicted it would.

**With the statistics matched** (they computed *our* variance-ratio statistic on *their* trajectories, restricted
to the 10 orbits surviving at every ε): agreement **7% at ε=2 and 2.4% at ε=5**. Far stronger than the original
side-by-side comparison, and it isolates the disagreement to the one non-perturbative point. Their ε=0 floor on
our statistic is 2.87e-27 against our 1.48e-28 — same order, and both sweeps sit 1e23–1e26 above their floors, so
neither side is measuring noise at weak coupling. **The value agreement is now established for ε = 2 and 5, and
ε = 10 should be reported with its radial reach or dropped.**
