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
