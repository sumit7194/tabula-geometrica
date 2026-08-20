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

## WITHDRAWAL + the degree-3 positive control (script 169, 2026-08-16), 4/4

**Withdrawn: §168's "third answer".** We reported that at momentum degree ≥3 on deformed Kerr "there is no
separated structure to count", and called it a third answer distinct from coverage and from a miscount. ansatz
showed it was never established, and they are right. At degree 3 the deflation removes p_t·K and p_φ·K — every
place Carter appears at that degree — so the ε=0 control was asking the engine to find something that, as far as
anyone knows, **isn't there**. An empty complement is then consistent with *both* readings and discriminates
neither: "correctly nothing, instrument fine" and "instrument blind" produce the same output.

**A null at a rung with no positive control is not a null.** This is our own REFUSED-LIBRARY principle one level
up, and the **fourth** instance of the silent-null class we had just named. We shipped it in the same session in
which we named it. Also recorded from ansatz: they searched for a theorem that Kerr admits no irreducible rank-3
or rank-4 Killing tensor and **could not find one**, so "correctly nothing" is an expectation, not a fact.

**The control.** ansatz proposed Cariglia & Galajinsky, *Ricci-flat spacetimes admitting higher rank Killing
tensors* (arXiv:1503.02162) — Ricci-flat signature-(2,q) spacetimes with irreducible rank-3/4 Killing tensors,
built by Eisenhart-lifting Drach's 2D integrable systems. Web-verified to exist and to say that. We used the
simpler member of the same family, since a positive control needs a *known* answer rather than an exotic one:
the **3-particle open Toda chain**, whose third integral is cubic in the momenta. The formula was **not** trusted
from memory — T0 verifies conservation numerically and T1 verifies irreducibility numerically before it is used.

**Result, 4/4 (250 train / 250 test trajectories).** T0 I3 conserved, drift 2.8e-11 (H 1.8e-12, P 1.2e-13).
T1 irreducible: R² = 0.876 regressed on {P, P², P³, H, P·H}. **T2 the readout FINDS it** — 6 conserved
directions = 5 reducibles + 1, I3 inside the conserved span at residual **6.3e-12**. T3 the residual spectrum
separates by **4.8e10**, against 1.7 on deformed Kerr at the same degree.

**What this licenses, precisely.** It removes *"the instrument cannot resolve degree 3"* as a general
explanation. It does **not** retroactively validate §168's degree-3 rungs — those failed their own ε=0 controls
and remain REFUSED on their own terms. And it says nothing about **degree 4**, which still has no positive
control. The open question is now specific and answerable: *why did the deformed-Kerr degree-3 control fail when
the readout demonstrably works at that degree?*

**The same bug, twice, in two scripts.** T2 first failed at 5 conserved vs 5 reducibles. Diagnosis before any
change: P, P², P³, P·H and I3 were all inside the found span at ~1e-13, but **H was not** (residual 0.957) —
because the library required momentum degree ≥1 and H's potential term `a+b` carries no momentum factor. §167
hit the identical bug on Carter's `−A²cos²θ·H0` term. **Recurring form: a known invariant with a pure-coordinate
piece is invisible to a library that insists on a momentum factor.** The fix changed the *library*, not the
gate; thresholds are untouched; and the diagnosis identified which invariant was missing and why before the fix
was made.

**Also fixed:** the full-length run silently emptied because open Toda *scatters* — positions grow without
bound, and a `|position| < 60` filter rejects every trajectory at longer integration times. Filter on momenta
and the exponentials, which are what must stay bounded.

## Why the deformed-Kerr degree-3 control failed — measured, and it is NOT what either side guessed

ansatz proposed that our degree-3 library might be **homogeneous** in momentum degree 3, which would put Carter
(degree 2) outside its span and make the Carter-recovery control structurally unsatisfiable — a residual flat in
coverage forever, exactly what §168b measured. Tested by measuring the span directly (their own discipline:
evaluate the columns, don't read the code):

    rung                p_raw   Carter resid RAW   p_kept   after truncation
    deg2 rat+metric      224       4.69e-07         180        5.27e-07
    deg3 rational        314       7.07e-05         266        7.15e-05
    deg3 rat+metric      524       1.81e-07         363        2.65e-07
    deg4 rat+metric     1049       6.44e-08         611        1.53e-07

The degree-3 library carries momentum degrees **[0, 1, 2, 3]** — total-degree ≤ 3, **not homogeneous**. Carter is
in scope at every rung and the SVD truncation does not remove it. **Hypothesis refuted.**

**But it located a real limit one rung over.** `deg3 rational` represents Carter only to **7.07e-05**, ~100×
worse than every rung carrying the metric components, because Carter needs μ² = −2H and the plain rational
coordinate family cannot express the inverse-metric components. That rung is genuinely **basis-limited**, and its
§168 control residual of 9.2e-4 sits against a representability ceiling of 7e-5 — consistent.

**`deg3 rat+metric` is the one with nowhere left to hide:** Carter representable at 1.8e-07, control failed at
1.6e-3 — four orders between what the basis can express and what the engine recovered. Not sampling (flat in
coverage, §168b), not representability (measured here). An undiagnosed **readout/conditioning** failure.

**A tidy story rejected.** ansatz suggested a homogeneous degree-N library is the correct design given the
grading theorem, and that Toda passed because it finally got a degree-N control. The second half is true; the
first does not describe this instrument, which is total-degree *by design* — the degree-3 reducibles (P·H, p_t·K)
are inhomogeneous products and must be representable to be deflated. Toda's I3 is a genuine cubic **and** the
Toda library is total-degree ≤ 3, so that run does not discriminate the two designs. Recorded because the tidy
version would have left both sides more confident than the evidence supports.

**Reclassification.** The degree-3 rungs on their metric move from REFUSED to **"control failed for a diagnosed
reason; rung never actually screened"** — basis-limited for `rational`, undiagnosed readout failure for
`rat+metric`. Neither is a statement about the spacetime.

**Adopted rule** (ansatz's, neither of us had written it down): *diagnose which invariant is missing and why
before touching anything, then change the library and not the gate — that ordering is the difference between a
fix and a fudge.* And their generalized form of the momentum-floor bug: *a graded library and an invariant that
is not homogeneous in the grading will always mismatch, and it presents as an under-count of the reducibles
rather than as an error.* Three mechanisms now, one symptom — constant column, slice-specific coefficients,
grading mismatch — the engine reporting confidently on a span that cannot hold the answer.

## The degree-3 control failure, fully localised (ansatz's bisecting test + follow-up)

ansatz's test: I had measured "Carter is representable" by fitting the library to Carter's **analytic values**,
which is a different question from whether the fitted vector is **conserved along trajectories**. Pushing the
best-fit coefficient vector through the conservation statistic:

    rung              fit resid   heldout(fit vector)   engine best
    deg2 rat+metric    5.27e-07        2.69e-11           4.68e-16
    deg3 rational      7.15e-05        2.14e-07           1.93e-16
    deg3 rat+metric    2.65e-07        6.02e-11           1.26e-13
    deg4 rat+metric    1.53e-07        3.50e-10           2.82e-12

**The chain, named.** Carter is only *approximately* representable at these rungs, so its best representation is
conserved only to ~1e-11 — while the engine's own conserved directions reach ~1e-16. The reducibles are
polynomials in E, L, H and are represented *exactly*, so the control-calibrated floor is set by quantities far
better conserved than the control target. **A control-calibrated floor is only valid if the control target is
represented as well as the calibrators are.** That is a third distinct way a basis can be silently inadequate,
and it is not one either of us had listed.

**`deg3 rational`: explained.** Carter's conservation (2.14e-07) sits **5 orders outside** the band its own
reducibles define (3.40e-12). Basis-limited, exactly ansatz's §85 H2, one rung over from where they guessed.

**`deg3 rat+metric`: explained, and not by coverage.** Carter *is* inside the band here, so the floor is not the
cause. Sweeping the control against ensemble size:

    ntraj    150      300      500      800
    resid  4.58e-3  1.26e-3  1.18e-3  1.87e-3      gate 1e-3

It improves to ~1.2e-3 by n=300 and then **plateaus just above the pre-registered gate**. The conserved subspace
(13-dim, 12 reducibles + 1) captures Carter only to ~1.2e-3 even though the full kept library represents it to
2.65e-07 — because Carter's representation is conserved to 6e-11 while the subspace is defined by directions
conserved to 1e-13, so Carter sits partly outside the very band that defines the subspace. Same mechanism as
`rational`, milder, and it lands just the wrong side of the threshold. **The gate is not moved.** The rung is not
screenable at the pre-registered standard, and now for a named reason rather than an open shrug.

**Correction to our own earlier reading of §168b.** We described *both* degree-3 rungs as "flat in coverage".
Only `rational` was flat (3.63e-4 → 3.01e-4). `rat+metric` was **descending** (4.28e-3 → 4.36e-3 → 1.13e-3) and
we read it as flat because it sat next to one that was. It plateaus, but it does not start flat.

## The absence-calibrated floor (script 170) — HONEST NEGATIVE: right idea, wrong model of absence

ansatz's sharpening of our sixth failure mode is the general form and it is correct: *a floor set by things that
are PRESENT inherits their representation quality; a floor set by a library KNOWN TO CONTAIN NOTHING inherits
only the dimension.* **Calibrate against absence, not against other presences.** Their §123 per-degree
structureless control does this by construction, which is why their pipeline could not have hit our sixth mode.

**Our implementation of "absence" was wrong, and it failed in the mirror direction of the bug it was meant to
fix.** Modelling absence by pooling all samples and re-dealing them into groups destroys the trajectories'
**temporal structure** as well as their conservation. Chance conservation on structureless data is then
essentially nil, the floor comes out at **~1.0**, and the band admits the entire library — 73 directions at Toda
degree 3, 178 at Kerr degree 2, **354** at Kerr degree 3. A floor that accepts everything is exactly as useless
as one that rejects the target, and both were reached in the same session from opposite directions.

**The gate that let it through was our own, and it was mis-specified.** A1 was pre-registered as "the floor is
non-trivial: far above machine precision" — a *lower* bound only. A floor of 1.0 satisfies that while admitting
everything. **Testing a threshold in one direction only is how a vacuous control passes.** Fixed by adding the
missing half: a **known negative** — a smooth, non-conserved function of the state, which the floor must reject.
It scores 3.10e-01 against a floor of 9.95e-01 and is **wrongly admitted**, so A1 fails and the instrument is
**not adopted**. §168's recorded verdicts stand exactly as they were.

**What a correct absence model must do:** preserve *every* property of the real data except the invariant itself
— in particular the smoothness and limited phase-space exploration of a trajectory, which are what make ordinary
library directions look partly conserved. Shuffling removes the confound and the signal together. The natural
candidate is trajectories from a system in the same family with the extra invariant genuinely destroyed (the
deformed case), rather than synthetic noise — but that reintroduces a *presence* to calibrate against, so the
design tension is real and unresolved. Recorded as open.

**Running count of the shape.** This is the seventh instance today of a check that could only come out one way:
the first version gated the floor from below, the quantity it guarded sat at the top of its range, and nothing in
the pre-registration would have caught it. Same family as *a control that cannot fail is not a control* and
*measure the CEILING too* — and this time the mis-specified check was in a script written **to fix** a
mis-specified check.

## Chaotic-sea calibration: measured to be UNAVAILABLE in this family (closes the open tension)

ansatz identified why no shuffle can work, as a fixed point rather than a bug: *conservation is a property of the
temporal structure, so any operation that removes conservation by destroying temporal structure removes the thing
you are calibrating against.* Their way out — don't manufacture absence, **find** it: use real trajectories from
the **chaotic sea of the same family** (same metric, integrator, library, smoothness), where the extra invariant
genuinely does not exist, and certify that with an instrument that isn't ours (a positive Lyapunov exponent).

**We validated the certificate before using it, per the rule adopted this session.** A maximal-Lyapunov estimator
(two-trajectory divergence with renormalization; no library, no eigenproblem) first read **λ = +0.019 on ε=0,
i.e. on integrable Kerr**, which must read zero. Cause: finite-time bias goes as ln(T)/T ≈ 0.04 at T=120 — the
same order as the claimed signal. The fix is a better *discriminator*, not a better threshold: measure λ(T) at
growing T and ask whether it decays like ln(T)/T (regular) or plateaus at a positive constant (chaotic).

    T        ln(T)/T     eps=0            eps=5            eps=20
     60      0.0682     +0.0357 (24)     +0.0472 (8)      no surviving orbits
    120      0.0399     +0.0157 (22)     +0.0301 (1)      no surviving orbits
    240      0.0228     +0.0116 (22)     +0.0129 (1)      no surviving orbits
    480      0.0129     +0.0066 (22)     +0.0083 (1)      no surviving orbits

**Known-negative passes** (ε=0 decays with ln(T)/T, so the instrument is validated), and the result is that
**ε=5 decays the same way** — also regular. At ε=20 no orbit survives the radial band at all. So **there is no
accessible chaotic sea in this family within the band the screen operates in**, consistent with leg J's
"dynamically regular". Reaching chaos would require leaving that band, which violates ansatz's own
match-the-exploration-volume requirement and would calibrate the floor on a different region than it is applied to.

**Conclusion, and it is now measured rather than assumed:** the absence-calibrated floor cannot be built for this
family by either route — surrogates over-destroy (§170), and the chaotic sea does not exist here. Per ansatz's own
statement of the fallback, the honest position stands: **the band is uncalibrated, and the rungs depending on it
are REFUSED.** That is where §168 already had them; what changed is that the refusal now rests on a measurement
of why no calibrator exists, rather than on our having failed to find one.

**Reusable outcome:** the λ(T)-trend Lyapunov instrument is validated (known-pass and known-fail both exercised)
and is available for any future integrability question in this repo.

## SURVIVOR BIAS — our "no chaotic sea" claim was overreach; chaos exists, outside the band

ansatz sent back two rules from their own §79 correction, and both landed on our data:
*a plateau is only evidence if something was varied* (an early-terminating computation plateaus for free), and
*two controls compared against each other must be measured under the same conditions*.

**The flaw they exposed in ours.** Our λ(T) sweep filtered orbits to a radial band and reported only survivors.
But **chaotic orbits wander more, so they leave the band first** — the filter selects for regularity, then we
reported finding only regular orbits. Worse, the ε=5 row rested on **n = 1 surviving orbit**.

**Re-measured with each orbit's OWN survival time and its OWN finite-time bias**, comparing λ against ln(T)/T at
the T that orbit actually reached (never at the requested T):

    eps    n_full  n_short   median T   lambda    own bias   ratio
     0        22      38        42.0    +0.0805    0.0891     0.90x     <- integrable: known-negative
     2        12      48        40.6    +0.0899    0.0912     0.99x
     5         1      59        38.6    +0.0974    0.0947     1.03x
    10         0      60        31.3    +0.1241    0.1100     1.13x
    20         0      60        24.9    +0.4985    0.1291     3.86x     <- genuine chaos

**The ε=0 row is the built-in known-negative** and it passes: at integrable Kerr the *discarded* orbits sit at
0.90× their own bias, so escaping orbits are not falsely flagged as chaotic. That validates the ε=20 reading.

**What changes.** Across the entire canonical sweep {2, 5, 10} — in the band *and* among the escapers — nothing
is chaotic; the ratio stays at 1.0 within noise. So the operative conclusion survives. But **"no accessible
chaotic sea in this family" was overreach**: chaos is plainly there at ε=20, at 3.86× its own bias, and our
filter had been discarding exactly those orbits. Corrected.

**Why the calibration is still unavailable, now for a sharper reason.** The chaotic region fails *both* of
ansatz's matching requirements at once: it is not co-located with the screening band (those orbits leave it), and
it survives only T ≈ 25 against the band's T ≈ 240 — a **10× integration-time mismatch**, which is precisely the
defect they had just found in their own §79 (Kerr at T=400 vs di-hole at T=21, an order of magnitude apart,
compared directly and flattering the margin 190× → 12.4×). A floor calibrated on ε=20 escapers would inherit both
mismatches.

**Standing conclusion, unchanged in substance and better supported:** the band is uncalibrated and the dependent
rungs are REFUSED — because no calibrator exists that is matched in region *and* in integration time, which is a
measured statement about the family rather than a failure to search.

## Arm-matching check on our growth-with-ε gate (prompted by ansatz's §85 falsification) — SURVIVES

ansatz found that their own ε-sweep growth was an artifact: their surviving-orbit count varied with ε (10, 16,
18, 18), so the sweep compared four different ensembles, and on a common-survivor set the trend went **flat**.
They gated on that growth and removed the gate. They flagged that §168's B1 gates on the same shape.

**Checked on fixed arms.** 900 initial conditions rolled at every ε; drift measured on the 174 that survive at
*all* of them:

    eps     per-eps ensemble (as shipped)     COMMON-survivor ensemble
     0            1.794e-27 (control)               3.138e-28
     2            1.735e-03                         1.654e-03
     5            1.010e-02                         9.730e-03
    10            3.500e-02                         3.622e-02

    survivors per eps: 341, 311, 275, 188   ->   174 common

**Monotone on both.** The growth is physics here, not composition, and B1 stands. Why ours differs from theirs:
their arms were 10–18 orbits with a drift changing by ~5× across ε, where composition can dominate; ours are
174–341 orbits with a drift changing by **20×**, far more than the ensemble difference can manufacture. The
claim is now *measured* on fixed arms rather than assumed to be safe.

**The general rule this round produced** (ansatz's corollary to our arms formulation, adopted): *a threshold
applied to two arms is only meaningful if the arms were produced under the same conditions; and when the
selection criterion depends on the swept variable, the arms differ by construction — no amount of care within an
arm fixes it.* Both of today's instances are that corollary with opposite symptoms: our survivorship filter
**hid** a signal (chaos at ε=20), theirs **manufactured** one (growth that was composition).

## Degree-4 positive control (script 171), 5/5 — the last unvalidated rung

§169 closed degree 3; **degree 4 was left explicitly uncontrolled**, so §168's degree-4 rungs and the degree-4
half of every CERTIFY we have written rested on an instrument never shown to find a degree-4 invariant when one
exists. Closed now.

**System:** the 4-particle open Toda chain, extending §169's by one site. The quartic invariant is **tr L⁴ from
the Lax matrix, evaluated numerically at every sample** — no recalled polynomial, which is what nearly cost us
§169. ansatz's Cariglia–Galajinsky metrics (arXiv:1503.02162) remain the exotic route; this is the simple member
of the same family, chosen because a positive control needs a *known* answer, not an exotic one.

**Result (220 train / 220 test, 700 samples each), 5/5 first attempt:**
- **Q0** tr L⁴ conserved, drift 6.76e-12 (H 2.88e-12, P 2.89e-14); the **known-fail control drifts at 6.24e-01**
- **Q1** irreducible: R² = 0.973 regressed on all ten degree-≤4 reducibles {P, P², P³, P⁴, H, H², P·H, P²·H, I3, P·I3}
- **Q2** the readout **finds it**: 11 conserved = 10 reducibles + 1, tr L⁴ in the conserved span at **5.11e-11**
- **Q3** residual spectrum separates by **3.70e+09**
- **Q4** *(the known-fail half)* a smooth non-conserved degree-4 function is **correctly excluded**, residual 2.55e-01

**Every criterion carries a known-pass and a known-fail**, per the rule adopted this session after two
pre-registrations in one day turned out to be the faulty check. Q4 exists precisely because §170's floor passed a
one-directional test while admitting the entire library.

**What this licenses.** Degree 4 now has what degree 3 got in §169: a demonstration that the readout resolves a
genuine irreducible quartic invariant when one is present in a representing library. A degree-4 null elsewhere in
the ladder is therefore a statement about the *basis*, not about the instrument. It does **not** revalidate
§168's degree-4 rungs on bumped Kerr — those failed their own controls and remain REFUSED on their own terms.

**Scope:** natural Hamiltonian, not geodesic flow, so the grading argument does not apply and this is not a claim
about any spacetime. In verify.sh.

## §172 — the degree-4 positive control in GEODESIC FLOW: an honest negative with a named mechanism

§171 gave degree 4 a positive control in a *natural Hamiltonian* (Toda tr L⁴, 5/5). That tests the readout but
not the setting: P3 asks about Killing tensors of a **spacetime**, and geodesic flow is also the only setting
where the grading argument applies. ansatz identified the Cariglia–Galajinsky 5D Ricci-flat metric
(arXiv:1503.02162, Eq. 26) as the route and asked that it be built independently rather than taken from them.

**Substrate verified before use** (their Taub-NUT lesson — a metric that was neither Taub-NUT nor vacuum):
Ricci **exactly 0.00e+00** for additive U, and the **known-fail** reproduces the paper's own Eq. (4) prediction
to the digit — adding a non-additive 0.25·x·y term gives R_tt = 0.5000 against predicted 2c = 0.5000, with every
other component exactly zero. H conserved 1.1e-13, Killing momenta 1.4e-16, the rank-4 tensor **1.8e-13**, and a
smooth non-conserved control drifting 1.3e-01.

**A transcription trap, resolved.** Eq. (29) as extracted from the PDF gives a tensor that is *not* conserved
(drift 3.0e-01, either index convention, null or generic geodesics). Deriving instead from Eq. (24) — which does
transcribe correctly, verified conserved to 1.6e-14 — and uplifting via Eq. (28) gives a conserved quantity whose
term-by-term expansion matches every component of Eq. (29) except one index label: **K_ttxw**, not K_tttw.
ansatz then fetched the paper's **HTML** rendering: the published text reads K_ttxw. **The paper is correct; our
PDF-to-text path collapsed the `x` into a `t`.** So the derivation independently recovered what the authors
actually published, index placement included, from a corrupted source. The warning stands for anyone transcribing
from a PDF: a silently wrong target tensor makes a prover fail to find the known invariant, which reads as *"the
control failed"* or, worse, *"no rank-4 KT exists"*. **Verify the paper's invariant is conserved before using it
as a target** — the same rule as verifying a transcribed metric is Ricci-flat before calling it a spacetime.

**THE RESULT: G2 FAILS.** K is representable (2.9e-15), genuinely conserved (1.8e-13), verified irreducible
(R² = 0.397 against 45 *measured* reducibles) — and the readout still does not isolate it. Conserved count 0
against a floor calibrated on H and p_t; in the earlier, better-conditioned probe K's residual in the top-46 span
was 2.6e-02 against a non-conserved control at 1.8e-01, i.e. almost no discrimination. ~30 directions come out
well conserved where 45 reducibles plus K exist.

**The mechanism.** In geodesic flow the degree-4 reducible algebra is **45 elements generated by only four
quantities** (p_t, p_s, p_w, H), so its members are inherently near-collinear — §167's near-parallel powers at
scale. The extraction cannot isolate one irreducible direction inside a large, nearly degenerate reducible span.
§171 succeeds precisely because Toda's degree-4 reducible set is 10 elements and well separated.

**One fix round spent, failed informatively.** Widening the ensemble's momentum spread (the §167 remedy) makes it
**worse**: at spread 0.8 and 1.5 there are *zero* directions below 1e-9 and the known-fail residual falls to
5.5e-02 / 9.1e-02, converging on K's. Stopped per the one-fix-round rule rather than tuning until it passed.

**Two of our own catalogued failures, hit again inside this script.**
- *Mode 6* — the floor calibrated on H and p_t, which are exactly representable and conserved to ~1e-28, while K
  represents to 3e-15 and conserves to ~4e-07. We wrote that rule down and walked into it again.
- *Modes 5/7* — with `conserved = 0`, G3 reported `separation = inf` and G4 reported "correctly EXCLUDED": an
  empty spectrum cannot separate and an empty span excludes everything. **Two passes by construction, in the
  script written to enforce that they can't happen.** Caught in our own output before committing; both now
  report REFUSED when nothing was found.

**A new entry for the catalogue: an ensemble that does not EXPLORE cannot distinguish a conserved direction from
a slowly varying one.** At a 1.5-time-unit window the geodesics barely move (mean x-spread 0.22) and K's own best
fit conserves only to 4.1e-07 with a flat spectrum at ~2.5e-04; at 6 units (spread 0.90) the same fit reaches
7.6e-23. Over a short enough arc *everything* looks conserved. Mirror of the coverage failure: that one was too
few trajectories, this is too little motion along each.

**Basis note.** The coordinate family uses the metric's own potential U rather than {y, x·y}: y grows secularly
along geodesics, so y-bearing columns are non-stationary and wreck conditioning (engine best 3.9e-07 with them,
4.2e-12 with U), while U keeps H representable in one column. Both H and K represent to ~3e-15 either way.

**WHAT THIS LICENSES — and it is the most consequential result of the arc.** The instrument is demonstrated at
degree 4 for a natural Hamiltonian (§171) and **NOT** demonstrated at degree 4 for geodesic flow with several
Killing vectors — exactly the setting P3 lives in. So **§168's degree-4 refusals on bumped Kerr were correct**,
and any degree-4 numerical null on a spacetime is REFUSED rather than null, now for a measured reason with a
named mechanism. Had we only ever run §171 we would have believed the ladder validated at degree 4 and read those
refusals as fixable. **The control did its job by failing.**
