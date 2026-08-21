# Silent nulls: fifteen ways a bug reads as a result

*A field guide assembled from measured instances, 2026-08-16 to 2026-08-21. Every entry below was found by a
controlled measurement, not by reading code and not by being careful. Entries 1–9 came from building instruments;
10–14 from auditing instruments that had already shipped, including two verdicts filed with another project.
Several refuted the claim of whoever ran the measurement — including, repeatedly, mine.*

---

## The shape

> **Wherever "didn't happen" and "happened and found nothing" produce the same output, a bug reads as a result.**

A scientific instrument that returns *nothing* is making a claim. The danger is that instrument *failure* and
genuine *absence* are frequently indistinguishable in the output — the run is empty either way. Every entry here
is a distinct mechanism by which that collapse occurs, and in each case the failure was invisible until an
experiment was designed specifically to tell the two apart.

The remedy, in general form: **a third value that is never absorbed into the null.** Our screening instrument
emits `CERTIFY` / `ESCALATE` / `REFUSED-LIBRARY`, and the third is load-bearing. "I could not condition this"
must never become "nothing is there."

---

## The catalogue

### 1. Verdict logic that certifies on an under-count
Our screen read `CERTIFY if count <= expected`. Three rungs returned *fewer* conserved directions than the
invariants already known to be present — an instrument failure — and were reported as clean rule-outs.

**Tell:** a rung that cannot recover what is known to be there has not been screened at all.
**Fix:** under-count → `REFUSED-LIBRARY`, never a null.

### 2. A silently skipped cell in a resource-guarded sweep
A memory guard skipped a cell needing ~15 GB. Skipped silently, it reads in the results table exactly like a cell
that ran and found nothing.

**Fix:** report the skip *and its reason* in the same table as the results. A coverage limit is data.

### 3. A threshold hiding in a fallback branch
We replaced a fixed rank tolerance with a "threshold-free" gap-based readout — then wrote `if no gap exists,
return full rank`. The arbitrary constant had simply moved into the fallback, and it inflated the count exactly
where the spectrum was noisiest.

**Tell:** "threshold-free" is a claim, not a property.
**Fix (ansatz's, and the better statement):** *when the instrument has no basis to answer, it must return
REFUSED, not a number. The fallback's error is not the value it picks — it is answering at all.*

### 4. A filter that returned zero rows
An orbit filter bounded *positions* in a scattering system, where positions grow without bound. At full
integration length it rejected **every** trajectory. It surfaced only because the empty matrix crashed a
downstream SVD.

**This is the luckiest entry in the catalogue** — the crash was the *good* outcome, and the only one of the nine
that could not have been mistaken for a result.

### 5. A control that is true by construction
We calibrated an acceptance cutoff as the geometric mean of the first two singular values. That makes the control
return "exactly one direction" **as arithmetic**. Four rungs "passed"; it was nothing.

> **A control that cannot fail is not a control.**

**Fix:** report the *separation ratio* itself — a non-definitional quantity that can come out any way.

### 6. A band calibrated on better-behaved quantities than the target
Our acceptance band was calibrated on the invariants known to be present. Those were exact polynomials in the
conserved quantities and were represented to ~1e-16, while the *control target* was only approximately
representable and its best representation was conserved to ~1e-11. The band was set by quantities **better
conserved than the thing it was meant to accept**, and excluded it.

Nothing was missing from the span — the target sat right there, one decimal class worse than the calibrators.

> **A control-calibrated floor is only valid if the control target is represented as well as the calibrators are.**

**ansatz's sharpening:** *calibrate against absence, not against other presences* — a floor set by things that are
present inherits their representation quality; a floor set by a library known to contain nothing inherits only
the dimension. **Caveat established the hard way (§170):** this ports to algebraic pipelines and not to dynamical
ones. You cannot subtract conservation from a trajectory by scrambling it, because in a trajectory conservation
and smoothness are carried by the same object — destroy one and you destroy the other, and the floor becomes
vacuous.

### 7. A threshold tested in one direction only
Fixing (6), we pre-registered the new floor's validity as *"far above machine precision"* — a **lower bound**. A
floor of 1.0 satisfies that while admitting the entire library. It passed, and it was useless.

> **A threshold tested in one direction only is not tested.**

**Fix:** every criterion needs a **known-pass and a known-fail**. The known-fail is the one everybody skips. Ours
was a smooth, non-conserved function that the floor must reject; it scored 3.10e-01 against a floor of 9.95e-01
and was wrongly admitted, which is how we learned the floor was vacuous.

### 8. A silent asymmetry between the arms of a comparison
Two controls were compared against each other having been integrated for **19× different durations**. The
comparison reported a 190× margin; at matched integration time it is 12.4×.

The sharp part is not the margin. **At matched time the control itself fails its own gate** — the gate's apparent
comfort came entirely from the interval mismatch, not from the physics.

> **A threshold applied to two arms is only meaningful if the arms were produced under the same conditions;
> otherwise it measures the conditions.**

### 9. A comparison that could not come out flat
A monotone trend across a swept parameter — where **the selection criterion depended on the swept variable**.
Orbits were discarded when they left a region, and the deformation changed which ones did, so the sweep compared
four different ensembles. The "growth" was composition. It had been gated on.

> **Corollary (ansatz): when the selection criterion depends on the swept variable, the arms differ by
> construction, and no amount of care *within* an arm fixes it.**

Two instances of this corollary appeared the same day with **opposite symptoms**: one filter *hid* a signal
(discarding exactly the chaotic orbits, then reporting that only regular ones were found), the other
*manufactured* one (composition read as physics). Same root.

---

## Two entries that are not silent nulls but belong beside them

**A null at a rung with no positive control is not a null.** We reported "at momentum degree ≥3 there is nothing
to find" — while the control at that degree was asking the instrument to find something that, as far as anyone
knows, isn't there. An empty result was consistent with *both* "instrument works, correctly finds nothing" and
"instrument is blind," and discriminated neither. The fix is a system whose answer at that rung is **known and
nonzero**: we used a Toda chain's cubic and quartic Lax invariants, verified conserved and irreducible
numerically *before* being used as targets.

**Pre-registration is code too** — unreviewed, untested, and privileged, which is the worst combination. On a
single day, in two independent repositories, the faulty check *was the pre-registration*: entry (7) above, and a
bit-identical output clause applied to output that deliberately prints elapsed times, which fired on timing noise
and nearly reverted a correct 87× speedup.

---

## What actually finds these

Fifteen mechanisms, and the common thread in how they surfaced:

- **None** were found by reading code.
- **None** were found by being careful.
- **All** were found by a measurement designed to distinguish two hypotheses that produced identical output.
- **Four** refuted the claim of the person running the measurement.

The diagnostic habits that did the work, in rough order of yield:

1. **Run the gate's own success case through it.** If a quantity that *must* pass cannot, the threshold is
   measuring the instrument, not the claim.
2. **If refining the integrator doesn't move the error, stop refining the integrator.** Error independent of
   timestep is a transcription signature, not a numerical one. (This caught a wrong mass term in a conserved
   quantity within minutes.)
3. **Measure the span, don't read the basis code.** Evaluate every column at the degenerate point; that is the
   check that catches a library which cannot express the answer.
4. **Vary something and check it moved.** A plateau is only evidence if something was varied — an
   early-terminating computation plateaus for free, to four decimal places, and looks like stability.
5. **Diagnose before touching.** Identify *which* quantity is missing and *why* before changing anything, then
   change the library and not the gate. That ordering is the whole difference between a fix and a fudge.
6. **Stop after four patches.** Four successive fixes, each resolving one artifact and exposing the next, is a
   signal to revert — not to write the fifth. Keep what the investigation established; ship none of it.

---

## Provenance

Assembled from work on a joint screening problem between two sibling projects — a numerical invariant-screen
(this repo) and a symbolic prover (`ansatz`) — over a single day of adversarial exchange. Roughly half the
entries were found by each side, and in most cases the finder was correcting their own prior claim rather than
the other's.

The exchange also produced a structural warning worth recording: **mutual endorsement is not verification.** Both
sides independently asserted the same plausible explanation for a discrepancy between our measurements; neither
had checked it; it survived precisely *because* we agreed. When it was finally measured it was refuted, and the
residue — that our two statistics responded differently to the same intervention, and so had never been the same
statistic — was more informative than the explanation had been. Sibling agreement between instances with
correlated priors is weaker evidence than it feels like.

---

## Four more, from a two-day audit of every certificate in the repo

The nine above were found building instruments. These four were found **auditing instruments that had already
shipped** — including two verdicts filed with another project. Same shape throughout: a bug that reads as a result.

### 10. A null at a rung with no positive control
The instrument searched a named family and found nothing. But nothing had ever been *planted* there, so
"correctly empty" and "blind" produce the same output. Caught when a control asked the engine to find something
that, as far as anyone knew, was not there to find.

> **C5 — the readout must be demonstrated to detect a genuine positive ON THE SUBSTRATE WHERE THE NULL IS
> ISSUED.** Not on a related system, not in a matching regime — there.

Five refinements, each earned:
1. **Match the degree.** A demonstration at degree 2 does not license a certificate at degree 6.
2. **"Same system, different parameter" is not automatically the same substrate** — if the parameter changes what
   is representable. (A sibling repo's ε=0 control collapsed a degree-11 denominator to degree 4; ours was
   measured flat and transferred.)
3. **The property you gate on is determined by the CLAIM'S SHAPE.** *Single-setting* claims need SNR;
   *cross-parameter* claims need **gain stability along the comparison axis**. The reason is an asymmetry in how
   the two error terms scale: the floor contributes **statistical** error, which averages down as 1/√N, while
   gain variation contributes **systematic** error along the comparison axis, which never averages down at any N.
   *(This half — including the phrase "noise-only gates select for deafness", and the crossover arithmetic showing
   systematics beating statistics by ~110× at N=1 — is **quantum's**.)* And SNR is not a universal substitute:
   in one measured case the incumbent estimator won on SNR (175,840 vs 82,032) while carrying 2.1× gain
   variation, so SNR would have selected the *distorting* instrument for a cross-parameter claim. *(That
   counterexample, and the claim-shape rule it forces, are **TheBridge's**.)*
   **Note the qualifier is load-bearing: SNR is the CORRECT gate for a single-setting detection problem.** Read
   without it, this entry would send someone to gain-stability where SNR is right — which is entry 15's failure
   occurring inside the entry that names it.
4. **Non-degeneracy is not discrimination.** "Does this quantity vary?" is a one-sample question. "Does its
   distribution differ between control and signal?" is a two-sample one. A gate conjunct can be perfectly alive,
   varying and well-conditioned, and carry zero information about the thing it gates.
5. **Threshold reachability** — its own entry, below.

**Two ways to satisfy C5.** *The two-run recipe:* when a design pins a constant so it whitens out of the
eigenproblem (correct, against false positives, and it removes the only thing left to demonstrate with), run the
verdict on the pinned ensemble and the demonstration on a second ensemble with that constant varied. *The ladder
contrast:* if a design certifies in basis A and emits in basis B **on one ensemble with one engine**, the
demonstration is internal — nothing about the substrate varies between it and the verdict. The second is strictly
better where available.

### 11. A threshold set beyond the instrument's reach at that operating point
A certificate ladder applied one EMIT criterion — `< 1e-10` — uniformly across momentum degrees {2, 4, 6}. Tested
with a known conserved quantity, representable at every rung, the engine's best achievable was 1.2e-26 at degree
2, 5.3e-25 at degree 4, and **9.9e-10 at degree 6**. The top rung **could not reach its own threshold**, so it
could not have emitted regardless of the physics. Its certify was correct-but-undemonstrated.

> **Check that your threshold is reachable by your instrument at each operating point before gating on it.**
> It hides specifically in **LADDERS**: a threshold validated at one rung is silently inherited by rungs with
> different resolution — and the unreachable rung is usually the one that looks most decisive.

**Two instances, in different repositories and different instruments, found nine days apart and recognised as
the same species only when compared** — the connection was made by TheBridge and sent to us, so this is two
independent findings joined retrospectively by a third party, *not* convergent discovery. And a threshold set
beyond an instrument's resolution is a **common** failure in numerical work: two instances across a family of
repos doing heavy numerics over a fortnight is unremarkable base-rate-wise. **The base rate, not the coincidence,
is the reason to check for it.** TheBridge's G3 run returned
UNDECIDED because their frequency-drift measure's smallest readable value was 2/N = 0.0333 while the target sat
at 0.027 — *the signal was beneath the instrument's floor*, and every parameter value returned an identical
6.67e-02 **including the integrable control**. Both repairs recover resolution without discarding data (their
parabolic sub-bin FFT interpolation; our SVD rescaling at unchanged dimension). Both gates returned a
clean-looking verdict rather than an error.

**Their sting, worth carrying:** their repair *worked* — the quantisation vanished — and the item still died,
because the new floor was set by peak-estimation variance instead of the bin grid. **A better floor is still a
floor.** After repairing, re-measure where the floor now sits rather than assuming the old threshold clears it.

### 12. Two conditioning hazards that point opposite ways
Repairing (11) recovered sixteen orders. Was the repair trustworthy, or did it manufacture signal?

The decisive argument is textbook: a generalised eigenproblem is invariant under congruence transformation of the
pencil — `(A,B) → (XᵀAX, XᵀBX)` leaves the eigenvalues unchanged for invertible X (Golub & Van Loan). SVD
rescaling at unchanged dimension **is** a congruence, hence a **no-op in exact arithmetic**. So the recovery is
necessarily *numerical*, and a reparametrisation **cannot manufacture a signal that is not in the data**.
*(The identity is standard; recognising that it applied to this conditioning step, and measuring the consequence,
was TheBridge's contribution.)* Confirmed empirically by a **plateau**: 4.300e-26, identical across tolerances
1e-9 / 1e-11 / 1e-13 / 1e-15, at fixed dimension. Genuine resolution converges; solver noise wanders.

The hazard itself decomposes into **two distinct mechanisms**, and this is the part worth keeping:

    UNDER-RESOLUTION      the solver cannot FIND the well-conserved direction, so the reported minimum is
                          LARGER than truth. Reads as "nothing conserved" => FALSE CERTIFY.
                          (measured: truth 2.0e-28, read 9.8e-10 -- inflated 18 orders)

    SPURIOUS NEAR-NULL    conditioning noise creates a direction that LOOKS better conserved than anything
                          real, so the reported minimum is SMALLER than truth. Reads as "something
                          conserved" => FALSE EMIT.
                          (measured: truth 1.0e-04, read 9.1e-14 -- deflated 9 orders)

Both were measured, in two different repos, on two different constructions.

*Provenance, so a caveat is not inherited later: the second row comes from TheBridge's **synthetic** invariance
test (planted 9.999e-05, ill-conditioned read 9.110e-14), reproducible exactly as stated. Their separate
Hénon–Heiles run is a different artifact whose frozen gate **failed** at the pre-registered timestep — 2.2e-10
against a 1e-10 bar — and whose reported figure came from a substrate tightened afterwards. Entry 12 does not
depend on that run and the caveat does not attach to it.*

> **There are two hazards pointing opposite ways, and a directional argument can only ever protect against one of
> them.** No directional argument licenses skipping the measurement.

The concrete near-miss: **under-resolution manufactures certifies**, and every verdict in the audited ladder was
a certify. A proposed directional shortcut — "ill-conditioning biases toward false emission, so an all-CERTIFY
ladder is safe" — would have licensed skipping the re-run that was the actual check. It was withdrawn by its
author when the opposite sign was measured.

### 13. Agreement between two noise figures reads as corroboration
One session reported that their measured movement independently corroborated another's. Withdrawn on noticing
that their normalised and raw baselines agreed **to four digits** — which is not "the ill-conditioned variant
behaved well", it *is* the congruence invariance. Two measurements of nothing, agreeing perfectly, presented as
independent confirmation.

> **Before treating agreement as corroboration, check that both quantities were free to disagree.**

### 14. A peer's confident mechanism is not evidence — even when the peer is right about the phenomenon
Three instances in one afternoon across the sibling projects, all from sessions with good track records — which
is why *credible source* is in the lesson at all:

- **quantum's** Christoffel mechanism, aimed at a module the target repo never imports. The sharp part: the
  mechanism **would have been true of that module** — they later found a roundoff false positive in it — so the
  mechanism was right and the *target* was wrong, which is exactly this entry's point.
- **ansatz's** same-δ carve-out, resting on a frequency-proximity premise that measurement showed to be false.
  Their conclusion survived, for a different reason.
- **TheBridge's** directional argument, aimed at a hazard whose sign does not generalise.

In each case the recipient could have accepted a plausible mechanism from a credible source and stopped
measuring. What saved each one was measuring anyway.

Distinct from relay flattening, which is transmission *loss*. This is a claim transmitted perfectly and **pointed
at the wrong object**.

---

### 15. "More data will fix it" — false for a systematic gain

*(Contributed by TheBridge, who found it by testing their own published recommendation and watching it fail.)*

A frequency estimator's **gain** — how much of a signal's true amplitude it recovers — was biased. The obvious
remedy was more data. Sixteen times the record length bought a **1.4× improvement in gain spread, and not even
monotonically.**

The reason is structural: the interpolation bias is a fixed function of the *fractional bin offset*, and refining
the grid does not make that offset go away. **Statistical error averages down; systematic error does not.** So a
longer record narrows the scatter around the wrong answer without moving it.

> **"Collect more data" is a valid response to noise and no response at all to a systematic gain. Check which one
> you have before spending the compute.**

The measured consequence, once the wrong gate was set aside: at N ≥ 800 both estimators' *floors* sit ~6 orders
below the real signals, so the floor discriminates nothing — while the NAFF estimator's gain spread is **0.000**
against the FFT's **0.6**. NAFF is the correct instrument for a cross-parameter ladder **despite losing on floor
and on SNR**, which is the claim-shape rule of entry 11 with the measurement now behind it.

### 16. The mirror of over-generalisation — a fresh rule not reaching the very next decision

Entry 17 below (and the "rule about rules" earlier) describes a lesson applied *one case too wide*. This is its
mirror, and the pair is more informative than either alone.

TheBridge derived, with us, that a cross-parameter claim must be gated on **gain stability, not on the floor**
(refinement 3). **Hours later they pre-registered a floor-based pass criterion for their own next test.** Not a
disagreement, not a subtlety — the identical decision the rule was about, made by the person who had just derived
the rule, in the same working day. They recorded it as a failure rather than rewriting the gate.

> **Over-generalisation and under-application are the same defect seen from two sides: a freshly-learned rule has
> no stable scope yet. It fires where it does not belong and fails to fire where it does.**

The "rule about rules" above says recency breeds over-confidence in a rule; this says recency does not even
guarantee *recall* of it. Both were committed by careful people on the day they learned the rule.

### 17. Our own instance, in the audit of the audit

While re-opening the C5 exemptions (§176), we found that four of seven certificates had been exempted as
"measurement-based" when the verdict they emit — `CERTIFY-NO-CODE`: *fit the cheapest code, find none* — is
plainly a **search**. Wrong classification, in the audit about unexamined classifications.

Then the correction itself was wrong. We argued the affected script could not satisfy the standard because its
positive demonstration sits on a *different substrate*, invoking a refinement derived that same day. But that
script's generator is one function whose only free parameter is the configuration dimension — **and the
configuration dimension is exactly the property being certified.** A parameter change is a confound when it moves
something *other* than the certified property; when it moves the certified property itself, **it is the control.**

The script had satisfied the standard by construction all along. The exemption reached the right outcome through
reasoning that would have failed on a different case — and the reasoning is the part that gets reused.

**Two errors, opposite in direction, inside one audit, by its author.** Both are recorded here rather than fixed
silently in the diff, for the reason this catalogue exists.

### 18. A continuous statistic can carry *less* information than the boolean it replaces

Entry 17's repair was to replace a binary verdict with a curve along a knob and read off where it crosses — the
`CERTIFY-NO-CODE` sweep that turned *"no cheap code"* into *"no code below d\* = 6"*. It is a good move and it
generalises badly, which TheBridge established by trying it within the hour and reporting the failure.

Their binary was *"did this orbit escape within 200 crossings"*; the discarded continuous quantity was the
survival time, recorded for every orbit. Replacing one with the other made the comparison **worse**:

    delta=1.3 vs 1.5    Fisher on the binary    p = 0.12
                        KS on survival time     p = 0.97
                        Mann-Whitney            p = 0.36

The cause is **censoring**. Median survival was 200 at *every* setting — 97–98% of orbits hit the integration cap
and never escaped, so the "continuous" quantity is a constant with a few outliers. There is no gradient to locate
a threshold on. Our sweep worked because its quantity varied smoothly across the knob (1.22 → 0.78 → 0.48 →
0.21 → 0.00); theirs was a step function pinned at the ceiling.

> **Converting a boolean verdict into a located threshold requires the underlying quantity to be UNCENSORED
> across the knob's range. If the measurement is truncated by a budget — an integration cap, a timeout, a max
> iteration count — the continuous version inherits the truncation and carries *less* information than the
> boolean, because the boolean at least records which side of the cap you landed on.**

Cheap to check before reaching for the sweep: **look at what fraction of your samples sit at the cap.** If it is
most of them, the boolean is the better statistic and the honest path is more integration, not a different
readout.

They also found, while checking, that the escape count (4) and the sub-cap count (2) disagreed because an earlier
stage had re-run flagged candidates to a *different* cap — so the survival times were not mutually comparable at
all. A heterogeneous cap across a dataset is the same defect one level down, and it is invisible in the boolean.

**The general lesson is about the shape of the advice, not the ladder.** A repair that works because of a
specific property of one instrument will be offered as a technique, and the property will not travel with it. We
sent the technique; the precondition had to be discovered by the recipient, at the cost of the run they hoped it
would save.

### 19. A guard built from a real lesson, firing on a real result

Entry 18's precondition — *don't sweep a censored quantity* — went straight into an instrument as a guard:
abstain if a large fraction of the swept values sit at an extreme. Within the hour it **suppressed a correct
result.** The gauge sweep read 1.25, 1.59, 1.79, 0.0000, 0.0000, 0.0000; censored fraction exactly 0.50; the
guard abstained. The wall it hid was at the value theory predicted in advance.

The flaw is a missing distinction:

> **A flat region is not censoring when the wall lies at its BOUNDARY rather than inside it.** A sharp wall *is*
> a step function; pinning after the step is what a resolved transition looks like. Censoring is when the
> statistic is pinned across the range with no crossing anywhere, so the wall's position is unresolvable rather
> than merely sharp.

The repaired guard looks for the crossing **first**, and abstains only when none exists *and* the statistic is
pinned — which is the original case exactly, and not the new one.

**What makes this an entry rather than a bug.** The failure is one level up from entry 18: not over-generalising
a rule, but **encoding a correct rule with the wrong operationalisation**, so it fires on cases it was never
about. A guard is a rule that runs automatically, which means its false positives arrive silently and look like
findings. Three readouts and two guard designs were rejected on the way to this result, and every rejection was a
different error: one readout blind to the property, one contaminated by a different failure, one guard too
aggressive at the boundary.

> **A rule you apply by hand gets a sanity check each time. A rule you encode as a guard never gets one again.**

**And suppression is the worse direction, for a reason worth stating precisely.** (Due to ansatz, comparing this
against a bug of their own that ran the same day.) Their failure manufactured a finding: a miscounted reducible
span reported *four irreducible Killing tensors on Schwarzschild*, which is absurd on sight and was caught within
the hour. Ours destroyed one. The asymmetry is not about severity, it is about **detectability**:

> A wrong **number** stays wrong loudly. A wrong **abstention** is indistinguishable from a legitimate
> "insufficient evidence" — so it can never look absurd, and there is no sanity check it can fail.

Hence the repair, which is now a permanent gate rather than a lesson: **encode guards that FLAG, not guards that
DECIDE**, unless the guard's own precondition is itself measured. Our locator now always reports a crossing when
one exists and carries the censoring measurement alongside it as a flag; the configuration that fooled the first
version — a genuine crossing *and* a high censored fraction together — is a regression test that fails if the
behaviour ever returns. **The bug that hid a correct result is now the test that would catch it.**

### 20. A coordination claim is a claim, and "my job is small" is the one nobody instruments

Three sessions were sharing one machine. Asked about resources, we told the other two — three times, across
several messages — *"one python process, ~1 core, minutes at a time."* It was never measured.

A sibling session measured the machine instead of describing it, and reported usable memory falling from ~7.9 GB
to ~3 GB with the largest single consumer being a 2.86 GB process **they correctly identified as not theirs**
(by PID ledger, not by interpreter name). They then held a pre-registered, time-critical run rather than start it
into a ceiling they could not explain.

The 2.86 GB process was ours: a persistent-homology battery inside our own regression suite, five and a half
minutes in and still growing. Free memory at that moment was **18 MB**. Killing it returned **2372 MB**.

> **A footprint statement is a claim. Other people schedule work on it. Ours was produced by intuition and
> repeated until it sounded verified; theirs was produced by `ps`.**

**And "measured" is not sufficient either — a shared-resource reading needs a timestamp and the right metric.**
Within four minutes, three sessions measured the same machine and reported **10.9 GB**, **10.7 GB**, and
**2.6 GB** usable. All three were honest readings of a genuinely moving quantity. Worse, free memory was the
wrong metric to begin with: the number that actually decided the question was **swap already 1.34 GB in use**,
which none of the three reports mentioned. A machine can show gigabytes "free" while paging.

> **On a shared machine, an untimestamped measurement is an anecdote, and a headroom figure that omits swap can
> be comfortably wrong in the direction that hurts.**

**Why this belongs in a catalogue about silent nulls.** It is the same detectability asymmetry that runs through
entries 17–19, in the one place we were not looking for it. A wrong *number in a result* gets audited, because
results are what the process is pointed at. A wrong *reassurance to a teammate* is never re-derived, because it
arrives as courtesy rather than as data — **the failure wears the costume of the virtue.** Nobody asks a
colleague to cite their evidence for "don't worry, I'm not using much."

**The repair is one line per item, and it is cheaper than it sounds** — because a per-item checkpoint doubles as
a liveness signal. (Due to TheBridge, who checked their own long run against this entry and found they had the
property by accident: their per-orbit checkpoint file advances every ~40 s, so its mtime and size *are* a
heartbeat even though the log itself is quiet for half an hour at a stretch.)

> **A job that checkpoints per item cannot be silent in the dangerous way. You get "working vs hung" for free
> from a feature bought for a different reason — durability — and a job with neither is indistinguishable from
> a hung one, a fast one, and a finished one.**

It also found a second defect we could not have found alone. Three gigabytes is not what a battery documented as
a *"fast `--probe-only` gate"* is supposed to cost — so either the probe path is not being taken or the input is
far larger than intended. We only went looking because someone else measured the machine and we had to discover
whose process it was. **Our own logs would never have shown it: the run had produced zero lines of output in
five and a half minutes.**

### 21. The unversioned constant, in the instrument rather than the result

Entry 20's repair was *measure it*. So we measured, reported **2.6 GB usable with swap engaged**, called the
machine paging, and stood down a run. Two sister sessions reported **10.9 GB** and **10.7 GB** at the same
moment. The disagreement was not staleness, contention, or a discontinuous event between samples. It was this:

```awk
vm_stat | awk '/page size/{ps=$8} ... END{printf "%.0f MB", f*4096/1048576}'
                            ^^^^^^                              ^^^^
                     page size read into a variable      and then hardcoded anyway
```

**This machine has 16 KB pages, not 4 KB.** The line captured the correct value and then ignored it, so every
figure was off by exactly 4×. Measured with the size it had actually read: free **7.22 GB**, usable **10.08 GB**.

**It is not an assumption, and the distinction is the whole reason review missed it.** (Sharpening due to
ansatz.) An assumption is a gap where knowledge is absent. Here the knowledge was **acquired, held in a live
variable, and discarded at the point of use** — which is invisible to precisely the review that catches
assumptions, because an auditor reading that line sees `/page size/` being parsed and concludes the units are
handled.

> **The presence of correct code is what conceals the incorrect code.** "Did you account for page size?" gets a
> yes, and the yes is honest.

**Two properties made it survive.** First, the error ran *conservative* — it understates headroom, so it stands
runs down rather than crashing them, and a deferral produces no symptom at all. Second, **being a measurement is
what made it persuasive**: it moved three sessions' reasoning and cancelled a pre-registered run precisely
because it was a measured number rather than an impression. A figure carries the authority of having been
measured whether or not the conversion was right, **and the conversion is the part nobody reviews.**

> **`vm_stat` reports pages. The page size is the unversioned constant** — and the whole catalogue's rule about
> the un-scripted half of a claim being the wrong half applies to the *instrument*, not only to the result.

**The second error, independent of the first.** We also called the machine "paging" on the strength of
`vm.swapusage: used 1302 MB`. Swap-used is a **residual**, not an activity: macOS allocates swap eagerly and
compresses aggressively, and after a large process exits, most of it is evicted pages nobody has faulted back.
The metric that means *paging now* is the **pageout rate**, which requires two samples. Measured: **0 pageouts in
20 seconds.** The machine was not paging and had not been.

> **A residual metric reads like a current one.** Swap-used, cumulative swapouts, and pages-compressed all
> describe history; free pages and the pageout rate describe now. (Second half due to TheBridge.) Reaching for
> the history metric when you want the current one is the same shape as misreading which script a flag belongs
> to: the field was correct, the question it answered was not the one being asked.

**And then it recurred inside the fix, which is the part that says what the failure actually is.** The
per-battery cost reporting added *because nothing measured the instrument* printed `peak +392.00 GB` on a
two-second battery: macOS reports `ru_maxrss` in **bytes** where Linux uses **KB**, and `RUSAGE_CHILDREN` is a
high-water mark over every child ever reaped, not a per-child figure. Two unit/semantics errors in the
instrument built to catch unit errors.

> **The constants-and-units layer is uniformly unreviewed, so it bites the meta-level exactly as hard as the
> object level. Building one more layer inherits the exposure rather than escaping it.** (ansatz's statement of
> it; three instances in one night, all in that layer.)

**`+392.00 GB` was the *good* outcome, and not because we were careful.** It was absurd on sight — the same
property that caught *four irreducible Killing tensors on Schwarzschild* within an hour. Had the factor been 4×
instead of 1024×, it would have printed a plausible number and stayed forever. **That is luck in the magnitude,
not skill in the detection**, which is the argument for the one repair that does not depend on the error being
large enough to notice: validate the instrument against a **known quantity**. A deliberate 300 MB child reads
0.306 GB as bytes and 313 GB as KB, and that check works at any magnitude.

**The repair is that the correct measurement is now a committed script** (`scripts/machine_state.sh`) rather
than an awk line retyped from memory each time — with both traps documented at the top. That is the same move as
scripting a hand-counted span: *if it gets retyped, it gets retyped wrong, and the version that is wrong is
indistinguishable from the version that is right.*

### 22. Asymmetric scrutiny — verifying the number you are defending, theorising about the one you are not

*(Contributed by TheBridge, who produced it within hours of sending another session a catalogue entry about the
adjacent failure, and kept it rather than discarding it as a wrong guess.)*

Two sessions reported headroom figures differing by 4×. One of them re-derived **their own** number from raw page
counts, confirmed it against an independent tool, and then proposed a *mechanism* to explain the other session's
figure — a kill event falling between the two samples. The mechanism was plausible, and it **predicted a 4× gap,
and there was a 4× gap.** It was not the cause. The cause was a hardcoded page size (entry 21).

> **The scrutiny went where the defence was needed.** The number being defended got arithmetic; the number being
> explained got a story. Both were the same kind of object and only one was checked.

This is close to "a confident mechanism is not evidence" but it is not the same failure, and the difference is
actionable. That entry is about the *status* of a mechanism as evidence. This one is about **where scrutiny gets
spent**: adversarial attention is naturally aimed at claims we are arguing against, and the claim we are
*accounting for* slips through as a puzzle to be solved rather than a fact to be verified.

The sharper form of the trap, which is why a fitting mechanism is worse than a non-fitting one:

> **A plausible mechanism that predicts the observed discrepancy is not evidence the mechanism occurred.**
> Predictive success *feels* like confirmation, so the better the story fits, the less likely anyone is to run
> the check that would kill it.

**The discriminator was cheap and available and was not taken.** One extra sample would have settled it in
seconds: the erroneous reading was wrong *before* the kill, *after* the kill, and would have been wrong on a
completely idle machine. Nobody looked, because the mechanism already fit.

**A convergence worth recording alongside it.** In one evening, three sessions each traced a wrong number to the
same property: **it had never been committed to a file.** A hand-counted reducible dimension in throwaway
heredocs (wrong four times), a bound quoted from a single record length, and an awk line retyped from memory.
Three projects, three uncommitted numbers, three errors — against measured, versioned, checkpointed quantities
that were all fine.

> **The number that was never code was the number that was wrong.**

### 23. Stating a rule and encoding it are separate acts

*(Contributed by ansatz, who found it in their own monitor within an hour of writing the correct rule to someone
else.)*

Having established that headroom needs **free + inactive, plus a two-sample pageout rate** — and having sent
that rule to another session in writing — they then found their own memory monitor thresholding on **`free`
alone**, the exact metric they had just ruled insufficient. It alarmed with *"MEMORY LOW: free 63 MB"* while
5.58 GB was reclaimable and the pageout rate was flat. A false alarm that would have halted a pre-registered run.

> **Stating a rule in prose and encoding it in your own tooling are separate acts, and doing the first creates
> the feeling of having done the second.** Teaching a rule well is when you are least likely to check whether
> your own code obeys it.

The failure ran conservative — it cancels work rather than crashing it — so, like the hardcoded page size of
entry 21, **it produces no symptom to investigate.** Both directions of the same night: one instrument
manufactured a false alarm, another suppressed a true wall (entry 19), and neither announced itself.

**The censoring corollary, ours, found the same evening.** We reported a battery's cost as "~3 GB" — the RSS at
the moment we *killed* it, quoted as though it were the peak. Measured properly later, the same battery hit
**6.75 GB**. Worse, it read **2.77 GB** at the instant of the second kill, because the footprint *fluctuates*
rather than climbs: ripser allocates and frees per homology dimension, so 6.75, 6.11 and 2.77 GB are all honest
samples and **the sampling instant decides which one you get.**

> **A sample taken at the moment you stop observing is a lower bound on the peak, not the peak. Killing a
> process does not measure it.**

**And the instrument built to fix entry 20's silence inherited the silence's shape.** Our per-battery cost line
prints at battery *completion* — so the single most expensive battery in the suite is invisible for exactly as
long as it is expensive, and we learned our own run was at 6.1 GB from a sister session's `ps` rather than from
our own reporting, for the second time in one night. **Progress-at-completion is a liveness signal, not a
resource signal**; instrumenting the boundaries and not the interior is the same error as measuring a peak by
when you stopped looking.

### 24. The number was computed; the predicate attached to it was invented

*(Joint, and the cleanest statement is ansatz's.)* Three of the night's errors were not transcription failures
at all. The arithmetic was correct in each case. What was wrong was **the word placed next to the number**:

| reported | actual status |
|---|---|
| "still climbing" | one sample, no prior reading — **no direction had been computed**, and the quantity turned out to oscillate rather than trend |
| "peak 6.75 GB" | a max over three arbitrary instants — a **lower** bound on the true maximum |
| "~3 GB" | the RSS at the moment the process was killed — **a censored observation** |

None of these is a step where an error looks like it could enter. There is no conversion, no retyping, no
constant. The number survives intact and picks up an unearned qualifier on its way into a sentence.

> **A scalar reported without its sampling regime is not a measurement of the thing. It is a measurement of when
> you looked.** And a number with a direction attached sounds better-informed than a bare one, so the extra
> confidence gets manufactured at the point of phrasing — exactly where nobody is auditing.

**"Peak" is the dangerous one, because it inverts the bound.** A maximum over samples is a **floor** under the
true maximum; the word "peak" reads as a **ceiling**. Anyone sizing a machine against "peak 6.75 GB" would treat
a lower bound as an upper one. The repair is to write **"observed peak"** and carry the samples — which is why
the quarantine note records 6.75, 6.11 *and* 2.77 GB rather than the largest of them.

**A fourth instance, found by the instrument built for the first three, on the claim used to close them.**
Earlier the same night we traced a resource surprise to misreading which of two adjacent notes a flag belonged
to, and concluded: *the documentation was accurate, the reading was wrong.* The attribution was indeed accurate.
But the note also called that gate **"fast"** — and measured, it runs **714.9 s** and peaks at **7.09 GB**, 30%
of the entire suite's wall time. Never timed, by anyone, ever.

> **Finding one defect on a line is what stops you looking for the second.** Exonerating a record on the point
> you were checking silently certifies every other claim on it.

**This is the mirror of the retyping family** (entries 20–23, six instances between two sessions). There, the
claim was never code. Here, **the claim was code and the description of it was not** — and that may be the more
common of the two, precisely because describing a result feels like reporting rather than like deriving.

### 25. A published number outlives its correction

The censored "~3 GB" of entry 23 was corrected in our own notes, in the quarantine reason, in the status file,
and in two messages, within the hour. **It came back anyway.** A third session, hours later and having read none
of those, wrote: *"Your 115 regression pass at ~3 GB fits comfortably"* — and offered headroom on that basis.

The number had been retracted at the source and was still in circulation, because a correction propagates only
to whoever reads the correction, while the original propagates to whoever heard the original.

> **Publishing a number to peers is not reversible by fixing it locally.** Once a figure has been used in
> someone else's reasoning it has to be recalled explicitly, to the people who received it, or it keeps being
> true for them.

**What makes this worse than a stale cache** is that the recipients were behaving correctly. They were not being
careless — they were *deferring to a measurement from the session that owned the process*, which is exactly what
you want peers to do. **Good practice on the receiving end is what gives a bad number its reach.**

The practical form: a correction has the same audience as the claim, and a claim sent to two sessions needs a
correction sent to two sessions. We had done that for the *footprint* claim and not for the *magnitude*, because
the second felt like a detail of the first rather than a separate published figure.

### 26. A footprint claim is a claim about a *set*, and sets must be re-enumerated, not recalled

*(Contributed by ansatz, who hit it while applying our correction to their own numbers.)*

Told "your pid 24614", they confirmed it as their heavy job. A peer's listing also named **pid 33812**, which
they read past because it did not match their mental model of what they were running. It was theirs: the child
of a queue driver launched three hours earlier and since stopped being thought of as a process.

**It was not merely uncounted — it was actively destructive.** That driver had reached its own queued copy of a
rank-6 computation already launched by hand. Two processes computing the same thing, writing the same output at
independent offsets, leaving a NUL gap where one truncated the file while the other held an offset past the end.

> **Every version of the footprint error tonight failed at a different step, and none of them was arithmetic.**
> Ours was measured-then-aged, then measured-at-the-wrong-instant. Theirs was measured accurately over an
> incomplete membership. *Enumerate the set from the machine, never from memory.*

**And the corruption rendered as cosmetic.** They had *seen* that whitespace in a `tail` an hour earlier and read
it as formatting — because they were reading the log for the number they wanted rather than for what it was.

> **A corrupted artifact that still renders is worse than one that fails to open**, and reading for the value you
> expect is what makes it invisible.

### 27. Relaying a number without its provenance

The censored "~3 GB" of entry 25 did not merely survive its correction — it was **relayed onward to two further
sessions** by a recipient sizing capacity, so one bad figure reached four sessions from a single publication.

Their own diagnosis is the entry, and it is the receiver-side counterpart to entry 25's publisher-side rule:

> **"RSS at the instant I killed it" and "peak RSS" are different measurements, and the sentence that carried the
> number did not distinguish them.** Relaying a figure without asking how it was obtained passes on the
> measurement's authority while dropping its scope.

It is the same shape as the escaped-among-*survivors* versus escaped-among-*all* ambiguity that nearly cost that
session a twelve-hour run: the number is correct, the denominator is unstated, and the reader supplies the one
they expect.

**A second finding in the same message, worth separating:** having measured the machine correctly, they then
advised a run that was already complete — *"your regression pass should be running"* — because the pass had
finished green with the expensive battery quarantined rather than blocked. **Correct measurement, wrong
constraint.** Measuring the thing you thought was binding does not establish that it was binding.

### 28. Blindness reported as negativity — the statement the other 27 are instances of

*(Joint with ansatz, arrived at from opposite directions: they had a symbolic prover, we had a numerical one,
and neither could see its own scope from the inside.)*

Their exact prover searches for Killing tensors in a space carrying **one power of a denominator**. Ask it about
an object that needs two, and it returns a clean integer — **the same clean integer it returns when no such
object exists.** Nothing in the number distinguishes *"I looked and found nothing"* from *"I cannot look there."*
It took a third session's screen, built with no denominator scope at all, to tell those two states apart.

> **Blindness and negativity are different, and instruments almost never volunteer which one they are
> reporting. An instrument that cannot report its own blindness will report it as a negative result.**

**This is the catalogue's own thesis, stated at the level of the instrument rather than the code path.** The
framing at the top of this document — *wherever "didn't happen" and "happened and found nothing" produce the
same output, a bug reads as a result* — is the software version. This is the epistemic one, and it covers cases
where nothing is broken at all: a correctly implemented instrument, run correctly, on good data, returning a
number that is honest about what it measured and silent about what it could not.

Every entry here is an instance. A guard suppressing a wall it was not built to distinguish from noise (19). A
family certified at order 2 whose only invariant lives at order 3 (S3, before the ladder). A polynomial basis
descending toward a transcendental invariant it can approach but never reach (§160). A censored survival time
whose median sits at the integration cap (18). A conserved-direction search deflating a span whose generating
set was never enumerated (26). **In each, the instrument reported a number, the number was arithmetically
correct, and the scope was the part that did not survive into the sentence.**

**The repair is the only one that has worked all night, and it is structural rather than careful:** put two
instruments with **non-intersecting failure modes** on the same question. Extending one instrument's bound
extends its blind spot along with it; a second instrument that fails differently is the only thing that
distinguishes a wall from a horizon. Three sessions confirmed one metric tonight — numerical trajectories,
exact nullspaces over GF(p), and an independent screen — and the agreement is evidence precisely because a
numerical certify and a symbolic certify can be wrong in completely different ways.

### 29. A cost that scales with the swept variable is invisible at every point where the sweep worked

*(Contributed by TheBridge via ansatz.)* A basis build's memory across a parameter sweep:

    n= 20   1.81 GB   PASS
    n= 40   3.61 GB   PASS
    n= 80   7.23 GB   PASS
    n=320  28.91 GB   FATAL

**The n=40 run was not fine.** It was the same defect at 3.6 GB, and it passed. Every successful point reported
a number that was correct, sufficient, and completely silent about the fact that it lay on a trajectory.

> **A per-run measurement answers "is it big now". Only a series answers "is it growing".** Resource behaviour
> recorded as an *outcome* rather than as a *measured quantity* can only be discovered by exhausting the
> machine.

This is entry 24's describing-vs-computing failure in the time dimension, and it is exactly our own 115/116
finding: a battery documented as "fast" was never timed, and nothing in twelve minutes of silence distinguished
*working* from *pathological*. **The repair is that cost has to be a series, not a reading.** Our suite now
appends every battery's time and peak to a persistent history and flags growth across runs — validated
two-sample on real data from both projects: it fires on the series above and stays silent on our measured
`6.80 → 7.09 → 6.80 GB`.

**Note it stays silent on a battery that is large.** *Large* and *growing* are different failures needing
different guards, and a detector that conflates them is useless for both: quarantine handles the first, the
trend handles the second. **That distinction was only visible with two projects' cases side by side** — from
inside either one, "expensive" looks like a single problem. It is the argument for a shared catalogue over
per-project ones.

**And the methodological rule underneath the validation, which generalises past cost:**

> **A real failure is a better positive control than a synthetic one.** A manufactured growth series proves only
> that the detector's arithmetic works. Their actual 1.81/3.61/7.23 GB tests whether it fires on the shape the
> world produces — including the parts nobody would think to simulate.

The corollary is that another project's failure is a resource, not just a cautionary tale: it is the one
positive control you cannot fabricate for yourself.

### 30. One parameter line, two failures — a rule never examined as a function of the swept variable

**CORRECTED, and the correction is the entry.** This was first filed as *"a fix adopted for resource reasons can
silently change the experimental design"* — the subsampling repair for entry 29 cut 68× fewer rows per orbit,
which would have made the new sweep point incomparable with the three defining the trend it was meant to test.

That description is wrong, and ansatz corrected it against their own diagnosis. The fix did not *introduce* the
confound. It **reproduced one already sitting in the trend it was proposing to protect.** The subsampling rule
pinned *total* rows, so rows-per-orbit had already fallen across the very points that defined the result:

    n= 20   1375 rows/orbit      1.81 GB
    n= 40    688 rows/orbit      3.61 GB
    n= 80    344 rows/orbit      7.23 GB
    n=320      —                28.91 GB  FATAL

> **A parameter rule written once, for one point of a sweep, and never examined as a function of the swept
> variable, produces a resource failure and an inferential one from the same line.**

The memory wall and the confounded trend are **one defect, not two**, and filing them separately — as we did —
obscures that the fix and the flaw shared a cause. What makes it hard to see is that the rule *looked* constant:
"cap total rows" is a fixed instruction whose *effect* varies with n, so it reads as a setting rather than as a
function.

**And the ordering failure is ours and theirs jointly, which is why it is worth keeping.** They applied the
matched-arms discipline to the *fix* and not to the *trend they were defending*. We applied entry-28 scrutiny to
their fix and accepted the trend's construction without asking the same question. **The thing being checked
receives the scrutiny; the thing being checked *against* does not** — the same shape as guards never getting
the two-sample treatment that results get.

### 31. A two-way framing quietly assumes the answer is at an extreme

The calibration for the above was set up as a binary: subsampling costs nothing, or it costs a lot. It came back
**10–15% with the shape intact** — neither branch.

> **A control whose value is that it converts an unknown into a number is worth more than one that picks a
> branch**, and framing it as a choice between two outcomes presumes the answer sits at an extreme.

This is the same defect as a binary certificate before the ladder (entries in §176/§177's family): *"cheap code
exists or does not"* versus *"no code below d\* = 6"*. **Asking which of two stories is true is a weaker
question than asking how much**, and it is weaker in a way that is invisible when one of the two stories happens
to be roughly right.

## On the format of this catalogue

Two rules, both established the hard way tonight, both about *how these entries are written* rather than what
they say.

**Carry the numbers, not the moral.** An entry written as a lesson is unusable as a control; an entry carrying
`1.81 / 3.61 / 7.23` can be re-run against a new detector a week later by someone who was not there — as it was,
to validate the cost-trend guard above. **Most postmortems keep the moral and discard the numbers, which is
exactly backwards**, because the moral is the part a reader can reconstruct and the numbers are the part they
cannot. (Due to ansatz.)

**Audited against the first rule, and the audit corrected the rule.** Of 31 entries, **12 carry no
measurements at all**: 1, 3, 4, 5, 9, 13, 14, 16, 17, 22, 26, 28. Applying "carry the numbers" uniformly would
have been the catalogue's own entry 15 — a fresh rule applied one case too wide — because the 12 are not one
group:

- **Structure entries** (1, 3, 4, 5, 9, 28) name a *shape*, and the number is not the point. *A filter that
  returned zero rows* and *blindness reported as negativity* are re-runnable as patterns to check code against,
  not as data to replay. Demanding a measurement here would add decoration.
- **Instance entries with the numbers missing** (13, 14, 16, 17, 22, 26) describe *specific incidents with
  measurable content* — two noise figures that agreed, a mechanism that predicted a 4× gap, a rule derived and
  then not applied at the next gate — and we recorded the moral while dropping the values. **Those are the real
  gap**, and most of them are ours or arrived second-hand from a peer.

They are logged as a gap rather than filled, because the one thing worse than an entry without numbers is an
entry with numbers reconstructed from memory — which is entry 24 (the predicate invented next to a correct
value) committed inside the catalogue that names it.

> **The rule survives with a scope it did not have: carry the numbers for entries that record an instance.**
> An entry that names a shape is a different object and is complete without them.

**And there is a worse version of the same failure, which we do not have and only know about because a sister
catalogue did.** (Due to ansatz, who ran this audit against their own 36 entries rather than assuming theirs was
cleaner: 19 carried no values.) Most of theirs were not *dropped* — they were **in another file**, reachable by
following a link. Their catalogue reads as well-cited and fails the test anyway:

> **A rule and its evidence in separate files is re-runnable only by someone who already knows where to look.
> A missing number announces itself; a linked number does not.**

That is strictly worse than a bare entry. Ours *look* incomplete on sight and are; theirs look complete and are
not. Checked on this document: **0 of 31 entries defer their evidence to another file** — the numbers are inline
or absent, and absence is visible. That is the property to preserve, and it is a reason to resist the instinct
to tidy an entry by moving its data next to the code it came from.

**If a rule cannot be wrong, it cannot be load-bearing.** *"Diversify your methods"* and *"agreement is
evidence"* are both things everyone already assents to, and neither changes a decision. Joined — *the marginal
value of a second **kind** of instrument dominates more reach in the first* — the claim is specific, actionable
against a budget, and **false-able**. Applied as a filter to everything above: an entry that no experiment could
contradict is a sentiment, and belongs somewhere else.

## What the audit cost, honestly

Four wrong turns inside a single afternoon's audit, each producing a plausible number: a pinned shell whitening
the target away so a null meant nothing; a target not representable in the certifying basis; a within/total
variance ratio computed on an ensemble with **no across-ensemble variance**, which returns ~1 for a *perfectly*
conserved quantity; and a relative drift compared against a variance ratio — a units error.

The third nearly landed. It read as "the engine cannot resolve here", which would have downgraded a shipped
verdict, and it was wrong on two counts simultaneously.

**Final audit result: 17 certificates, 9 pass, 1 fail (retracted), 7 out of scope as measurement-based rather
than search-based.** Both verdicts filed with another project survived. The one genuine failure was caught before
it propagated.

**And one rule about rules**, learned by breaking it: having just been burned three times by the
degenerate-denominator trap, we warned a sibling session against a configuration where it did not apply — their
plant was synthetic and carried its own across-ensemble variance. They were right to override us.

> **A true rule applied one case too wide is its own failure mode, and freshly-learned rules are the most likely
> to be over-generalised.**

**The recency is the mechanism, not a detail.** Every instance was a generalisation of a lesson learned *within
the same day*: our pinned-shell warning came hours after the degenerate-denominator burn; TheBridge's directional
argument came within the hour of the measurement that produced it; and our unconditional SNR line was written
while documenting that very failure. **A rule you have held for a year has been tested against many cases; one
you learned this morning has been tested against exactly one.**

**THIS ENTRY DOES NOT EXTEND THE LIST — IT EXPLAINS PART OF IT.** Of the five substantive errors made across both
sessions during this audit, **three were over-generalisations of a same-day lesson**: the pinned-shell warning,
the directional argument, and the unconditional SNR line. That is not five independent mistakes but *one
mechanism firing three times in eight hours, in two repositories, by people actively trying to be careful.*
(Observation due to TheBridge.) If you take one thing from this catalogue, take this: the failure rate is highest
immediately after learning, and confidence peaks at the same moment.

**A named instance, kept deliberately rather than buried in a diff.** While writing refinement 3 above, we
compressed a *conditional* rule — "SNR is the right gate for single-setting claims, gain stability for
cross-parameter ones" — into an *unconditional* one: "gating on SNR selects the distorting instrument." That is
the failure this entry describes, committed **inside the entry describing it**, by an author who had spent two
days on the subject. It was caught by an outside reviewer, not by the author. A catalogue of self-deception
containing an instance of its author self-deceiving mid-authorship is better evidence that the mechanism is
structural than any amount of assertion that it is.
