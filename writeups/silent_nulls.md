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
to be roughly right — which is most of the time.

**And the located form is systematically under-written, for a structural reason rather than a careless one.**
Compare a real headline in both forms:

    binary:   no irreducible Killing tensor
    located:  irreducible = 0 at ranks 1-6, den¹, 13 of 30 products named as excluded

The second is the result; the first is the second with its scope removed. But the scope clause **looks like an
apology for the finding**, so it gets written at the bottom in smaller words — and (ansatz's addition, which is
the compounding half) **it is written by the person most motivated to treat it as a caveat**, the author of the
result it appears to qualify. *Nobody else is in a position to write it.* So the one item that locates a verdict
is drafted, every time, by the party with an interest in its being small.

> **An exclusion list is not a caveat on the result. It is the part of the result that makes the number mean
> anything** — and the only defence against its being minimised is to write it before the headline, not after.

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

### 32. A write that succeeds and is silently reverted

Found in our own coordination file, minutes after declaring the night closed, while checking why a peer's status
would not parse.

A keepalive process refreshed our shared status file's timestamp every 30 s so that a stale status would
announce itself — the repair for an earlier failure in this same file. **It read the file once at startup and
rewrote that snapshot on every tick.** So every status update published during the session was reverted within
30 seconds, to a snapshot reading *"C5 audit complete, silent_nulls at 15 entries"* — while 28 commits and 16
further entries went by.

Three sessions were told to read that file.

    every write:  succeeded, returned no error, was correct at the moment it landed
    every read 30s later:  the startup snapshot
    never done:   re-read after writing

> **A successful write is not a persisted write.** Nothing in the writing process can detect this: the API
> returns success, the file is valid, the content is *plausible*, and the only evidence is a read that nobody
> performs because the write already succeeded.

**And the sharper statement is TheBridge's, about why this version is worse than the failure it replaced:**

> **A repair that fixes the symptom a reader uses to detect the fault converts a visible failure into an
> invisible one — and every observable says it worked.**

The first failure was detectable *because the timestamp froze*. The repair made the timestamp truthful and left
the content frozen, so **the only field a reader checks for freshness became the only field being maintained.**
Their independent instance from the same night: a tolerance sweep returning `kept = 70/80` identically at three
tolerances, meaning the knob being varied controlled nothing — and a flat result read as evidence. **Both are
instruments whose failure signature is indistinguishable from success through every channel actually
consulted.**

*(Their own keepalive persists, verified by read-back rather than assumed — and by their account the mechanism
was accidental: they edit only the `updated` field in place, so no snapshot is ever held. They chose it for
tidiness, not safety. Same accidental correctness as their per-orbit checkpoint turning out to be a liveness
signal.)*

**It is the catalogue's own thesis in the coordination layer** (entry 28): the file was honest about what it
contained and silent about the fact that it was not what anyone had put there. And it is entry 23 once more —
the keepalive was itself the *fix* for a stale-status failure, and the fix reintroduced the failure it was built
to prevent, in a form that looks like health: **a timestamp advancing every 30 seconds is exactly what a
correctly-maintained file looks like.**

**Validated the repair two-sample, per the closing rule below**, rather than assuming a re-read per tick fixed
it: wrote a new `detail`, waited past one tick, confirmed it survived. That check takes 35 seconds and would
have caught this at any point in the preceding ten hours.

**Adopted from a sister session in the same minute:** a machine-checkable `stale_after_s` field instead of a
prose warning that readers must notice and honour. *A staleness contract a reader can evaluate beats a sentence
asking them to be careful.*

**Two aggravating details, both found in the same five minutes.**

The original complaint this keepalive was built to answer was *"a file asserting a state nobody maintains is
worse than no file."* The repair made the **timestamp** truthful and left the **content** frozen — so the one
field a reader checks for freshness became the only field being maintained. **A detectable failure was converted
into an undetectable one and called a fix.**

And the peer-liveness checker used to survey the other sessions **reported one of them as `?`** because it
parsed only `...Z` timestamps while that session emitted `+00:00`. It could not read the file and reported the
peer's *state* as unknown rather than its own *parser* as failing — entry 28, in the tooling being used to audit
everyone else.

**The correction could not be fully delivered.** One of the sessions that had been told to read the status file
ended before this was found. The stale content propagated to them; the correction has nowhere to go. That is
entry 25 in its terminal form — **a recipient list is not guaranteed to still exist when you discover you owe it
a retraction**, which is an argument for correcting early and loudly rather than at the end of a session.

### 33. A pre-registration that plans for arms disagreeing, but not for both arms refuting

*(Contributed by TheBridge, whose night ended with two withdrawals.)*

They froze a commitment before their runs finished: a headline must hold under **matched-n and matched-spacing**,
and is withdrawn if the arms disagree. Both arms then agreed — **4 above, 4 below, exactly** — so the commitment
was satisfied in its letter. And they agreed the headline was **false**.

    original headline:  "eight of nine δ at or below the integrable control"
    the control:        measured at n=50, max/median inflated 2.4x by small-sample bias
    re-measured:        n=1254 and n=1238 across both arms -> only 4 of 8 sit below

> **A pre-registration that enumerates how a result could be *ambiguous* is not the same as one that states how
> it could be *wrong*.** Theirs anticipated arms disagreeing; it did not anticipate both arms refuting, so the
> outcome that actually occurred had no rule attached to it.

Their boundary run closed the same way: Fisher exact **p = 1.0000**, not supported, and the **direction
reversed** — a prior 4/100 vs 0/99 became 2/312 vs 3/317, with the previously-silent arm now the louder one.
The early interim they had pre-announced (0.061 at n=33 against a 0.040 baseline) regressed to nothing, which is
exactly why pre-announcing it cost them nothing to report.

**And the mechanism they name for their own failure is entry 31's, in a different costume:** they spent the
night establishing that an unmatched control invalidates a comparison, *while their own unmatched control sat
recorded as a caveat rather than fixed.* Two other sessions had flagged it hours before they measured it.

> **A caveat is where you put the thing you have decided not to act on.** Writing it down feels like handling
> it, and it is the same move as burying an exclusion list at the bottom in smaller words (entry 31) — the
> record is honest and the behaviour is unchanged.

**One practice worth stealing from the same message.** They owed a result to a session that had already ended
and filed a prediction on it, so they committed the numbers with the note that *the commit is the only delivery
available*. Against entry 25's terminal form — a recipient list that no longer exists — **the durable record is
the only channel that outlives the recipients.**

### 34. A pre-registration of standard knowledge is a recall check wearing a test's clothes

*(Contributed by quantum, who found it in their own published file and demoted the claim rather than quietly
fixing it — and it lands on us too.)*

They registered, before running, an ordering that is standard published knowledge, reported it **confirmed**, and
treated it as a prediction landing. It is not a prediction. **They could not have been surprised by it.** Their
own summary of the damage: *"three predictions, all confirmed" was one measurement and two recollections.*

> **Registering a known result in advance tests the instrument, not the hypothesis.** Both are worth doing and
> they are not the same act — and the pre-registration ritual makes the second look like the first, because the
> mechanics (write it down, freeze it, compare) are identical.

**The distinction that survives:** a known value registered in advance is a **positive control** — it asks *can
my readout find a wall that is definitely there.* That is legitimate and valuable. What is illegitimate is
reporting it as evidence *for* the claim, because a control that could not have failed carries no information
about the world, only about the code.

**AND IT LANDS ON OUR §177.** We registered `K* = 3` — two anchors fix rotation and translation but leave a
mirror; three non-collinear ones do not — and reported it as *"predicted before running, landed exactly."* The
reflection argument is standard distance geometry. It was an instrument check.

**The instructive part is where the qualifier went.** The script itself says it correctly:

    "K* = 3 is recovered, not derived; the derivation is the reflection argument above,
     stated in advance so the number is a check and not a discovery."

**That sentence is in the source and appears in none of the retellings.** Every summary — the status block, the
journal, two peer messages, the report to our own user — carried *"predicted before running"* and dropped the
clause that made it honest. Nobody removed it; it simply did not survive compression.

> **A qualifier that lives only in the primary record is one retelling away from gone.** If a claim needs a
> scope clause to be true, the clause has to be inside the claim's shortest form, or the shortest form is the
> version that travels.

Which is entry 31's mechanism arriving by a different route: there the scope clause is written small because it
reads as an apology; here it is written correctly and then lost, every time, to the summary.

### 35. A mechanism defeated by its own implementation — and the fix is to derive, not to detect

*(Found by TheBridge in their own keepalive; we then found the identical defect in ours, plus a second one.)*

Entry 32's remedy for a silently-frozen status file was a timestamped heartbeat plus a machine-checkable
`stale_after_s`. The cheapest correct-looking implementation of that remedy is one line:

```bash
sed -i "s/\"updated\": \".*\"/\"updated\": \"$(date -u ...)\"/" status
```

The clock advances every 30 s and **nothing else is ever touched**. So the file reported `state: running, heavy:
true, "resumed, peak ~5 GB"` for hours after that run had finished and been committed — with a timestamp always
seconds old. It cost a peer's scheduling: another session holds a 4.75 GB run and checks status before
launching, so a dead-man's switch was **blocking a real run on a completely idle machine.**

> **A frozen file is DETECTABLE — `updated` stops and the threshold fires. A file whose clock is driven
> independently of its content is undetectable by construction: it emits the exact signature the staleness
> check was built to certify as healthy.**

So the mechanism is defeated by *the implementation of the mechanism*. That is a nastier shape than entry 32:
there, a repair reintroduced the fault it was built to prevent; here, the cheapest faithful-looking
implementation of the repair **inverts the detector**.

**We had it too, and a second one underneath it.** Our heartbeat re-read the file (so entry 32 was genuinely
fixed) but bumped only `updated`, preserving whatever `state`/`detail` had last been typed — ours read *"now
writing the pre-registration"* two work-items after that finished. And our liveness probe, `pgrep -f
'SpaceTime/curvature'`, **matched the keepalive itself**: a monitor counting itself as evidence of activity, so
it could never report idle.

**THE FIX IS NOT A BETTER DETECTOR.** The tempting repair is a freshness token a lazy loop cannot forge — a
monotonic counter (a lazy loop increments it just as happily) or a jitter check (an idle box legitimately has
stable numbers). Both are heuristics for catching a liar. The real defect is upstream:

> **`state` was a DECLARATION.** A declared field is stale the instant work moves on, and **no heartbeat can
> refresh a declaration** — which is why bumping the clock beside it produces a confident lie. Derive the field
> from the machine instead and there is nothing left to fake: a value that requires having looked cannot be
> produced by not looking.

Ours now derives `state` from a self-excluding process scan and `heavy` from measured RSS, carries live
`free+inactive` (which jitters — 7.45 → 7.38 GB across two ticks), and keeps `detail` explicitly labelled
DECLARED with a `declared_age_s`. **The honest move is not to refresh the declaration but to stamp it**, so a
reader can see which fields are claims and which are measurements.

> **Never update `updated` on its own; that field is a claim about all the others.** (TheBridge's rule.)

### 36. Our review practice is textual; this week's failures were not

*(TheBridge's observation, from four independent cases across four sessions in three hours.)*

    quantum found two of another session's headline numbers had no artifact behind them
    we found their heartbeat was counterfeit -- correct code, bumping a clock beside frozen content
    a mutation test forced a run from a FRESH CLONE, catching a `.gitignore` `*.npz` rule that had
        swept up the SOLE INPUT to a gate committed twenty minutes earlier
    a fourth session hit the same gitignore class independently

> **Every one was invisible to reading the relevant file and obvious within seconds of executing something.**

The `sed -i` heartbeat is the cleanest specimen: it is *correct code*, it does exactly what it says, and there is
no bug to find by reading it. The defect lives entirely in the gap between what the file asserts and what the
loop actually checked — and that gap is invisible at every level a normal review operates on.

**THE PROBE VERSION OF THIS, which is the reusable half:**

> **A probe that never fires and a probe that always fires both look correct in the source.** The only way to
> tell them apart is to make the thing *transition* and watch it change.

Our own liveness probe matched its own keepalive — *a dead-man's switch alive because it is running* — and we
"verified" the fix by observing it report `idle` while nothing ran. That is the never-fires half only. Running
the full transition (nothing → real job → exit) is what actually establishes it, and it passed:
`idle/0 → running/1 → idle/0`.

**And the transition test failed twice before it passed, both times in the TEST.** `$!` returned the wrapper pid
rather than the python, so the kill missed; then a status read raced the 30-second tick and returned a value
written while the job was still alive. **The harness was wrong twice while the instrument under test was
right** — which is entry 21's constants-and-units lesson wearing a third costume, and an argument for making a
probe transition *more* than once before believing either the pass or the fail.

### 37. The freeze stops post-hoc relaxation; it does not stop implementation-time tightening

A pre-registration was frozen and hashed before any physics. Its first gate read, verbatim:

> `ω²/(m²+k²) − 1 → 0` as k→0, **at the expected order.**

The code that implemented it gated on:

```python
ok = abs(fitted_order - expected) < 0.35 and rel_err[-1] < 1e-3
```

**That second clause appears nowhere in the frozen file.** It was invented while typing the implementation. It
fired on one of four regulators — the deliberately-deformed one, whose larger magnitude is a design property,
not a defect — and produced a `G0 FAILED, the run STOPS` verdict that looked exactly like the pre-registered
known-fail doing its job.

> **Freezing protects against relaxing a criterion after seeing the data. It does nothing about *tightening*
> one before seeing the data** — and a criterion that was never registered is, by construction, one nobody
> agreed to and nobody will re-derive.

**The asymmetry that makes this dangerous.** A post-hoc relaxation is visible: the frozen text says X, the
report says Y, anyone comparing them sees it. An implementation-time tightening is invisible *unless it fires*.
Had the quartic regulator come in at 8e-4 instead of 1.5e-3, the two criteria would never have diverged, the
run would have passed, and the extra clause would have sat in the code indefinitely — silently making a future
run stricter than the thing anyone agreed to.

> **The only reason this was found is that it failed.** Every un-fired invented criterion is still there.

**The repair is not judgement, it is a diff.** Gate text and gate code have to be compared *mechanically*, and
the comparison has to happen before the first run rather than after the first surprising result. Ours was
caught by re-reading the frozen file when the gate fired — which works exactly once per gate, and only for
gates that fire.

**And note what it is NOT.** Removing the clause is restoring fidelity to the pre-registration, not relaxing a
gate — the opposite direction from entries where a threshold was moved to accommodate a result. The
distinction is checkable rather than a matter of self-report: the frozen text is committed at a hash, so
whether a criterion was registered is a fact about the repository, not about the author's intentions.

### 38. Freshness and liveness cover disjoint windows — and the dangerous one is not the one people build

A coordination file carried a timestamp and a `stale_after_s` contract (entry 32's remedy) and, later, a
published writer pid. At one moment it read:

    now      11:08:33Z
    updated  11:06:26Z     <- 127 s old, comfortably INSIDE a 300 s freshness window
    hb_pid   4384          <- pgrep: NONE. The writer was dead.

**The freshness check passed. Only the token caught it.** (TheBridge, on their own file, an hour after adding
the token at our suggestion.)

> **Staleness detection catches a writer that has been dead a WHILE. A liveness token catches one that died
> JUST NOW — which is the window in which a peer is most likely to still be acting on the file.**

The two mechanisms are complementary rather than redundant, and **the one everyone builds first covers the
less dangerous window.** A file whose writer died ten minutes ago is usually about to be noticed; a file whose
writer died ninety seconds ago looks perfectly healthy and is exactly what a peer schedules against. Their
tool found this on its own author in its first minute of use.

### 39. A captured stream that never emits looks instrumented and tells you nothing

TheBridge's keepalive died three times. Each restart, they moved on. It had been detached with stdout and
stderr to `/dev/null` — **so every death destroyed precisely the evidence needed to diagnose it**, three times,
during a day spent arguing that failures are found by running things rather than reading them.

> **"Run it, don't read it" does not help if you throw away what it prints.**

**Ours was the subtler variant, and arguably worse.** Both streams *were* captured to a file — no `/dev/null`
anywhere. But the script only printed on **normal completion**, so an abnormal exit produced an empty file. Our
keepalive died with exit 143 and 144 more than once and we learned nothing, while a correctly-plumbed log sat
there at zero bytes.

> **A channel that exists and carries nothing looks instrumented.** That is worse than obviously not being
> instrumented, because nobody goes looking for the missing pipe — the pipe is right there.

Repair in both cases is the same and takes one line: an `EXIT`/`TERM`/`INT`/`HUP` trap that records the exit
code. **Capture is not instrumentation; something has to actually be written on the path you care about.**

### 40. A disclaimer is composed as a frame for the number, not a replacement for it

Twice in one day, two different sessions, same shape. A message states plainly that **no values are being
sent** — and contains one.

Ours read: *"the study is dead on my side and I am sending no corner numbers"*, and four lines later,
*"implied a(120) = 0.003757"*. Both sentences were written in the same minute by the same author, and the
contradiction was invisible while writing.

> **The disclaimer does not suppress the number. It gets composed as a FRAME for it** — "here is why this
> doesn't count" reads, to the writer, as discharging the obligation, while leaving the value fully legible to
> the reader.

**Why the usual defence fails here.** A ledger consulted before sending (entry 27's remedy) catches a value you
*know* you are transmitting. It cannot catch one you believe you have already excluded — and a disclaimer
creates exactly that belief. The author is not evading the rule; **they have privately marked the number as
not-sent and then sent it.**

**What was and was not lost, because the distinction matters.** The value was computed *blind*, so the
recipient learning it afterwards cannot retroactively contaminate a completed computation — that comparison
stands (3.7% apart, genuinely independent). What is spent is every *future* comparison of that quantity, in
either direction. **A leak after the fact spoils the future, not the past**, which is worth knowing precisely
because it is the one case where the damage is bounded.

**The mechanical repair, since judgement demonstrably fails:** grep the outgoing message for numerals against
the quantities under embargo, *after* composing and *before* sending. Both instances today would have been
caught by a check that reads the message rather than trusting the sentence that says what the message contains.

### 41. A power analysis is only as good as its assumed nuisance amplitude

A gate had failed with 12% measured power. The replacement was designed carefully: a statistic immune to the
collinearity that broke the first one, and — for the first time — a **Monte Carlo power analysis run before
freezing**, reporting **95.8% power at a 0% false-positive rate**.

It delivered **none**. On the very shape where the effect certainly exists, the test returned **p = 0.40**.

The simulation injected the effect into synthetic data carrying a nuisance term with coefficient **−0.08**. The
real data wants **+0.12 to +0.40** — three to five times larger, and of the opposite sign. With the nuisance
that big and 97% collinear with the signal, the effect is unrecoverable.

> **A power analysis validates the test against the world you simulated.** Its headline number is a claim about
> that world, and it is silently conditional on every nuisance amplitude you guessed. Guessing one 4× too small
> converts "95.8% power" into a number with no bearing on the experiment.

**The repair is cheap and was skipped:** the nuisance amplitude was *measurable from a pilot fit on real data*
before the simulation was written. Nothing required it to be assumed. **Fit the nuisance first, simulate at the
fitted amplitude.**

**AND THE TWO FAILURE MODES WERE MIRRORS, which is the deeper finding.** The nuisance column had to be included
— omit it and the signal column proxies for it, firing when nothing is there. Include it and it absorbs the
genuine signal, firing never. There was no third option on this range:

    without the nuisance column:  false positives   (signal proxies for nuisance)
    with the nuisance column:     no sensitivity    (nuisance absorbs signal)

> **When a nuisance is nearly collinear with the effect, "control for it" and "don't control for it" are both
> wrong, and no amount of care chooses correctly between them.** The honest conclusion is that the test is not
> constructible on that range — which is a statement about the design space, not about the hypothesis.

### 42. An implementation can be COARSER than its pre-registration, not only stricter

Entry 37 recorded code that added a criterion the frozen file did not have. This is the mirror: **code that
dropped one it did.**

The pre-registration named a three-way outcome — pass, *implicated*, and **vacuous** (the floor fails, so the
test cannot distinguish a working instrument from a blind one). The implementation computed
`pass = floor_ok and zero_ok` and reported everything else as failure. So a run whose floor had failed printed
**"the extraction is implicated, STUDY DEAD"** — a conviction, from a test the frozen text says was
uninterpretable.

> **A freeze is only as good as the distinctions the code preserves.** Stricter-than-spec fires visibly and gets
> caught; **coarser-than-spec produces a confident verdict in the wrong category and looks exactly like a
> result.**

Both directions have the same repair and it is the one entry 37 already named: diff the gate text against the
gate code mechanically, before the first run — not because the author is careless, but because the two artifacts
are written hours apart in different languages and nothing checks that they still agree.

### 43. A survey row obtained by a different method is the least trustworthy row, not the most

Surveying six sessions on a shared machine, `pgrep -f "claude"` returned two processes for every repo except
our own, which returned one. We reported that anomaly to a peer as a **correction to their list**.

It was our instrument failing to see us. Each session is a pair — a helper plus the main process — and the
pattern matches every session's pair **except the caller's own**. The single row our scan returned for our repo
was an unrelated `/bin/zsh` that happened to match. The peer's count was right.

**AMENDED after the peer corrected the credit, against their own interest.** We first wrote that they "read the
asymmetry correctly from outside with less information." **They did not.** They had used a *different
enumerator* (sockets), and their process-level instrument has the identical hole — running our method, they
would have produced our number. **They were right because of which tool they happened to hold, not because of
how they reasoned.** Recording it the first way would have taught the wrong lesson to anyone reading later:
that careful outside judgement caught it, when what caught it was a second instrument.

**The mechanism is the inverse of the familiar self-match bug and it is nastier.** The known failure is a probe
that *counts itself* (a monitor alive because it is running, entry 35). This is a probe **blind to its
operator** — and the hole did not merely hide something, it **manufactured a confident correction to a third
party.** An absence in your own instrument became positive evidence about someone else's data.

> **When one row of a survey was obtained by a different method than the rest, that row is the least
> trustworthy in the table — not the most, however much effort went into it.**

We found our own row by an ancestor walk *because the primary method could not find it*, and that extra effort
felt like extra confidence. It was the opposite: the switch of instrument was itself the signal that the
primary method had a hole, and the hole was exactly where we were standing.

**The peer's statement of it is the keeper:** *the one row you measured differently is the one you concluded was
wrong in someone else's list.*

### 44. Naming a failure mode in a pre-registration is not the same as being able to detect it

A peer froze the clause: *"A == 0 with the controls also zero is instrument failure, not physics."* The sentence
is **correct**. It identifies precisely the right hazard.

It also cannot fire. Both controls in that design return zero **by construction**, so "the controls are also
zero" is unconditionally true and carries no information. The bucket named the failure and was itself an
instance of it.

> **A pre-registration can state a failure mode exactly and still have no path to observing it. Naming and
> detecting are separate acts, and freezing the first produces the feeling of having done the second.**

This is the same shape as two of our own: a G0 gate whose extra clause fired on nothing, and a cost label
(`exact.max`) asserting a property the measurement did not have. **A correct statement doing no work is
invisible precisely because it is correct** — review checks whether the sentence is true, not whether anything
could ever make it false.

### 45. Two instruments give you a contradiction; three give you an explanation

Entry 43's companion, and the harder half — the peer's, stated against their own credit:

> **When your survey and someone else's disagree and yours came from a second instrument, you have not checked
> them. You have swapped which blind spot you are exposed to.**

Two enumerators disagreeing tells you one is wrong and gives you **no way to assign it**. Adjudicating by "which
tool do I trust" or "which did I run more carefully" is choosing a blind spot, not resolving one — and the more
careful run is often the one that switched methods, which entry 43 says is the *least* trustworthy row.

**The resolution is a third instrument sharing a failure mode with neither.** Run on the same machine, same
minute:

    sockets    6   37066 38306 40134 40351 40540 40689
    pgrep     10   missing the caller's OWN pair -- blind to self
    ps -Ao    12   includes it -- not blind to self

**Sockets and `ps` agree exactly** — the socket names are precisely the main pid of each pair — and `pgrep` is
the outlier for a documented reason: it excludes the caller's own process ancestry. So the hole was never
"process enumeration is blind to the operator"; it was **one tool with a self-exclusion, which both parties
happened to reach for.**

> **A disagreement between two instruments localises nothing. A third both breaks the tie and explains the
> outlier** — and the explanation is what converts a mystery into a named scope limit you can carry forward.

The practical form: when two enumerators disagree, do not pick. **Add one whose failure mode resembles neither**
— and treat the deviation of the odd instrument as the finding rather than as noise to be voted down.

## The closing rule: distrust the fix, not only the result

Every entry above is about distrusting a **result** — a number, a verdict, a null, a green pass. This last one
is about distrusting a **fix**, and it is the one none of the three sessions had written down before the night
that produced it.

Look at what actually went wrong, in four projects, over twelve hours:

- a flag was withdrawn on a peer's say-so, which helped close the file on a line hiding a 7 GB battery;
- that line was exonerated on the point being checked, silently certifying an adjacent claim nobody had timed;
- a censored observation was quoted as a peak and reached **four sessions** from one publication;
- a hand-count nearly announced *four irreducible Killing tensors on Schwarzschild*;
- a rule was derived, written to a colleague, and then not applied to the author's own next gate;
- a guard built from a correct lesson suppressed a correct result within the hour.

> **Every one was a correction somebody accepted too easily — including from themselves.**

And the half that will slip, because it is counterintuitive: **the *liked* corrections are the hard ones.** A
fix that flatters your instincts, resolves a confusion you were already sitting with, or hands you a rule you
were half-holding already is the one adopted **without a known-fail**. Suspicion is cheap to apply to a claim
you dislike. The whole difficulty is applying it to a repair that feels like relief.

**Which yields the practical form of everything above:**

> **A fix is a claim. It needs a known-pass and a known-fail, on real data, before it ships** — the same two
> samples any result would need. A guard is a claim about a claim, and it has never once earned an exemption.

Tonight both new guards were validated that way, and both had already failed silently before they were: one
suppressed a true wall, the other shipped with two unit errors in the instrument built to catch unit errors.
Neither failure announced itself. **That is the entire argument for the rule, and it is the argument this
catalogue exists to make.**

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

### 46. A path-based identity check reads the launcher's string, not the process

Entry 45 ended by naming `pgrep`'s self-exclusion as the hole and `ps` as the fix. Restarting a keepalive the
next morning found the deeper version of the same hole, and `ps` has it too.

The loop was launched as `./curvature/scripts/keepalive.sh`. It ran correctly. But its argv now reads

    bash ./curvature/scripts/keepalive.sh 10

which does **not contain the string `SpaceTime/curvature`** — the pattern that every identification rule in this
project matches on: the kill-targeting rule ("never `pkill` by generic pattern; match only the full path"), the
script's own self-exclusion, and the heartbeat's derived job count. A `ps | grep <full path>` returned nothing
while the process sat there in the next line of output under a relative path.

So the same process is present or absent depending on **how it was invoked**, not on what it is. Both failure
directions are live: a job launched relatively is invisible to the heartbeat, which then publishes `n_procs: 0`
— a measured, jittering, entirely trustworthy-looking field asserting the machine is idle while it computes. And
a kill rule that matches on the full path silently spares the process it was written to target.

> **`pgrep` and `ps` both match against argv, which is a string the *launcher* chose. It is not an identifier
> of the process.** Two instruments sharing a failure mode is exactly what entry 45 warned about — and having
> written that warning, I switched from one of them to the other and called it fixed.

The identity that does not depend on the caller's typing is the kernel's: `/proc`-equivalent executable path, or
the pid recorded by the process itself at startup. This project already had the second one — the keepalive
writes `writer_pid` into its own status file — and it was the field I did not check first.

**Fix applied, not just noted:** relaunched by absolute path so argv and identity coincide, and verified by the
rule that would do the killing rather than by a friendlier grep. The cheap discipline is *always launch by
absolute path* — it costs nothing and makes argv-matching accidentally correct.

**A THIRD PARTY'S JOB, CHECKED THE SAME HOUR, MAKES THIS WORSE THAN OVER-MATCHING.** A sibling session
announced a 10-hour run and asked that it not be touched. Verified on this machine:

    pid 1655  scripts/_kt_double.py --rank 4 ...     cwd /Users/sumit/Github/conjecture_machine   THE JOB
    pid 1686  zsh -c '... cd /Users/sumit/Github/conjecture_machine; tail -f ... | grep -E "GUARD FAILED|..."'
                                                     cwd /Users/sumit/Github/conjecture_machine   ITS MONITOR

`ps | grep conjecture_machine` returns **1686 and not 1655.** The detached worker was launched with a relative
path, so the repo name is nowhere in its argv; the monitor was typed by a human with an absolute `cd`, so the
repo name is right there in its command line.

> **`pkill -f <repo>` would have killed the monitor and spared the job.** The output watch dies, the guard
> lines — `GUARD FAILED`, `MemoryError`, `Killed` — go unread, and the 1.2 GB job runs on believed stopped.

The bias has a mechanism and is not a coincidence of these two pids: **the strings a human types by hand carry
absolute, human-readable paths, and the strings a launcher generates for a long detached job often do not.**
Argv matching therefore selects, systematically, for *observers over workers* — it kills the instrument and
leaves the subject running. (Two pairs seen so far, this one and my own keepalive; recorded as an observed bias
with a mechanism, not a law.) The fleet rule that follows — *identify by PID plus provenance (cwd, venv), never
by argv match; `pkill -f` banned* — is now carrying a reason, not just a prohibition.

**Coda, same restart, same theme.** The first launch used `setsid`, which does not exist on macOS. It failed
instantly with `command not found` and the announcement "keepalive running" would have been false. It was caught
only because stderr went to a file rather than `/dev/null` — the same instrumentation that entry-era work added
for *deaths*, paying out on a **birth** instead. A launch that never starts and a loop that dies silently produce
identical evidence: no process, no message. **Instrument the launcher, not only the exit.**

### 47. A blow-up announces itself; a plateau recruits you

Relayed by TheBridge from a third workspace (3d CFT entanglement), from that workspace's own record — the
mechanism is what transfers, not the physics, and neither they nor I verified their numbers.

Three independent methods — polynomial fit, finite differences, Chebyshev — were used to extract series
coefficients from numerically computed data. **All three failed at the same orders, and each failure wore the
costume of its own method:** a wandering coefficient, a 10⁵ blow-up, and a degree-dependent plateau.

> **The plateau was the dangerous one, because it looked like convergence.** The blow-up cost minutes. The
> plateau survived hours and got written up.

Two of five extracted ratios were pure fit artifact — they swung by factors of **8 and 170** on a fit-degree
parameter with no physics in it — and an argument about an asymptotic limit had been built on them.
*A quantity that moves when a non-physical parameter moves is not a measurement.*

**WHY I CHECKED THIS AGAINST MY OWN WORK BEFORE FILING IT.** §178 reads a **flat** sequence across momentum
degree as the signature of a genuine absence. That is a plateau in a nuisance parameter being used as positive
evidence — the exact shape this entry calls seductive. So the item arrives as a potential refutation of one of
this project's located verdicts, and I went and looked:

    control (transcendental invariant)  1.04e-2 -> 1.49e-4 -> 1.16e-7   DESCENDING, 89,109x
    deformed Kerr                       1.96e-4 -> 5.91e-5 -> 9.11e-5   FLAT, span 3.32x, non-monotone

**§178 survives, and only because of L1.** The pre-registration made the control a *known-fail*: a system with
a provably transcendental invariant, where the same sweep on the same statistic **must** descend. It descends
by 89,109× while Kerr moves 3.32×. Had the readout been unable to see descent, no verdict would have issued.

> **A plateau is evidence only when the identical sweep has been shown to MOVE on a case where it must.**
> Without that, "it stopped changing" and "my instrument stopped responding" are the same picture.

Note honestly that Kerr's 3.32× is *not* zero — an absolute flatness threshold of 3.0 failed it in run 1, and
the recorded fix replaced the statistic rather than the number. It reads as flat *relative to* a control that
moves four orders further, against a located margin of 8.0e+19×. A 3.32× wobble cannot reach that verdict; on
a marginal one it would have to be taken seriously.

**The operational corollary, also theirs, and sharper than how I had it:**

> **Evaluating a candidate closed form at points is VERIFICATION. Inferring its coefficients from points is
> INFERENCE.** The same data yielded three real coefficients and two convincing fictions, and nothing in the
> output distinguished them.

(Their item ③ — *a pre-registration named a failure mode precisely and could not detect it, because both
controls were zero by construction* — is entry 44 arriving independently from another workspace. Recorded as
a second sighting, not a new entry.)

### 48. A correction that inherits the premise of what it corrects

Also relayed, and I am filing it because I have a first-hand instance from **this morning**, which is better
evidence than the relay.

> **A correction that keeps the unexamined assumption of the thing it corrects looks like independent scrutiny
> and is the same mistake at higher confidence.**

Their case: session A stated a term ratio as if it were an error. Session B corrected A's number and
generalised it — while silently keeping A's unexamined premise that the coefficients were O(1). **B's version
was more confident and less checked than A's.** Measurement settled it at 4.3%, not the 70% both had implied.

**MY INSTANCE, COMMITTED AN HOUR BEFORE THIS MESSAGE ARRIVED.** Entry 45 ended by identifying `pgrep`'s
self-exclusion as a blind spot and switching to `ps`. That was a correction. It inherited, unexamined, the
premise that **a process can be identified by matching a path against its command line** — and entry 46 is the
record of that premise failing the very next time it was used, because argv is a string the *launcher* chose.
The correction was narrower than the error it fixed and carried more confidence.

Worse: entry 45's own closing line was *"two instruments sharing a failure mode is exactly the hole."* I wrote
that, then swapped one argv-matcher for another argv-matcher and called the hole closed.

> **Check what the correction kept, not only what it changed.** The premise that survives a correction has
> never been tested — it was load-bearing in the original claim and is load-bearing in the fix, and the
> correction's confidence is borrowed from the scrutiny it applied elsewhere.
