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

**A SECOND INSTANCE, THE SAME MECHANISM ONE LEVEL UP, COMMITTED BY ME AGAINST A RULE I HAD JUST RELAYED.**
Within one hour I: relayed the fleet rule *"`pkill -f` is banned — it has already killed a sibling's gate"* to
two sessions; wrote entry 46 on why argv matching is unsafe; wrote entry 49 on how it under-reports to zero —
and then reached for `pkill -x -f "<full command>"` to restart my own keepalive. It happened to be precise and
harmed nothing (the neighbour's 1.2 GB job was verified untouched immediately after), which is luck, not care.

> **Producing the correct statement about a hazard produces the feeling of being protected from it.** Naming,
> relaying, and even *teaching* a rule are all acts of description; obeying it is not, and the first three feel
> like the fourth.

This is entry 44 at the level of behaviour rather than instrument design: a pre-registration that names a
failure mode it cannot detect, and an author who advocates a prohibition an hour before violating it, are the
same substitution of description for capability. Filed here rather than as entry 50, because it is that
mechanism a second time and **a catalogue that inflates its count stops being a catalogue.**

**A THIRD INSTANCE, AND IT PAIRS WITH A PEER'S IN MIRROR IMAGE.** Having told the fleet, in writing, *"sample
twice, ~30 s apart; throttle only if the rate is RISING; levels are not a scheduling input"*, I then shipped a
`paging` flag in my own heartbeat that fired on **a single tick**. Its first live firing:

    tick 1   pageouts/s 6.38   swap_delta -8.0 MB   paging TRUE
    tick 2   pageouts/s 1.16   swap_delta  0.0 MB   paging false
    tick 3   pageouts/s 0.00   swap_delta -8.0 MB   paging false
    direct vm_stat over 20 s: 0.25 pageouts/s

A one-tick spike, published as `paging: true` at the instant a peer might read it and throttle — **while
`swap_delta` was NEGATIVE, i.e. swap being reclaimed, which is the opposite of pressure.** The flag and one of
its own inputs disagreed and nothing noticed, because the OR had no veto term.

The pairing is the useful part. A sibling had confessed the same rule broken the other way round: *"I read a
LEVEL as a RATE — the same error in the general rule that I had avoided in the specific case."* They had told
a third party to sample **during** a measurement window (correct), then broadcast a levels gate to everyone
(wrong). **They got the instance right and the export wrong; I got the export right and the instance wrong.**
Same rule, opposite halves, two repos, one week.

> **Writing the rule down for others is not implementing it for yourself, and doing the first makes the second
> feel done.** Entry 44's mechanism has now fired on a pre-registration (naming a mode it cannot
detect), on a prohibition (relaying `pkill -f` is banned, then using it), and on an exported protocol —
description substituting for capability in three different formats.

**AND THE COROLLARY, WHICH IS THE PEER'S AND IS THE PART THAT CHANGES WHAT TO CHECK.** The two halves of that
failure are invisible through *different* channels:

    their half   the EXPORT was wrong        invisible because NOTHING RUNS AN EXPORT. A rule broadcast to
                                             four sessions is never executed, cannot fail, and therefore
                                             accumulates no evidence against itself. A reader caught it.

    my half      the IMPLEMENTATION was wrong invisible because THE CODE RAN AND MOSTLY BEHAVED. A single-tick
                                             trigger is correct most of the time; it took a live spike with a
                                             NEGATIVE swap delta -- the flag contradicting one of its own
                                             inputs -- to expose it. Telemetry caught it.

> **The same mechanism produced one error only a reader could find and one only a run could find.** So
> "instrument it and let it run" does not cover the exported half, and "have someone read it" does not cover
> the implemented half. Checking one is not evidence about the other, and the two feel like the same act of
> diligence.

This sharpens the catalogue's own favourite repair. *A gate corrects you for reasons it was not designed to
catch* (entry 51) is true of code and **false of a protocol you published**, because a protocol has no
runtime. The only referee an exported rule has is a reader who bothers to compare it against practice. Entry 44's mechanism has now fired on a pre-registration (naming a mode it cannot detect), on a
> prohibition (relaying `pkill -f` is banned, then using it), and on an exported protocol — description
> substituting for capability in three different formats.

Fixed by requiring the raw condition on **two consecutive ticks**, with swap being reclaimed as an explicit
veto. **Not by lowering the threshold** — the threshold was never the problem; the sampling discipline was, and
it was the exact discipline being advertised.

### 68c. Mutation-test the control, because "it passed" and "it can fail" are different facts

Entry 68b rebuilt a known-fail control so it actually executed the scanner it certified. That fixed
the hollow version. It did not establish that each arm fails **for its own reason** — and a peer
demonstrated the gap by mutating their scanner and watching arms pass that had no business passing.

So I mutated mine rather than reading it:

    mutation                 arm1  arm2  arm3 | live gate
    healthy                   OK    OK    OK  | PASS
    scan() dead               BAD   BAD   BAD | FAIL
    namespace scanner dead    OK    BAD   OK  | PASS
    path pattern dead         BAD   OK    OK  | PASS
    prefix RESOLUTION removed OK    OK    BAD | PASS   <-- only arm 3 sees it

**Re-run at a single code state, after a peer found their own matrix was a composite of two.** Mine
was too, and it changed a row: `scan() dead` reads `BAD BAD BAD`, not `BAD BAD OK` as first
published. I measured that row BEFORE fixing arm 3, fixed arm 3 *because of* that row, and never
re-ran it. **The stale row was the one that motivated the fix** — a table certifying the controls,
assembled from two code states, presenting them as one measurement.

**All four mutations produce distinct signatures**, so the matrix discriminates. And the `live gate`
column is the reason the control exists at all: **three of the four faults leave the gate green.**
Only the selftest sees them, which is what a gate that cannot detect its own blindness looks like
from outside — green, and wrong.

Arms 1 and 2 discriminate: each fails for its own cause and neither fires on the other's mutation.
**Arm 3 passed under every mutation including a completely dead scanner** — because it is a
*must-NOT-flag* assertion, and **a dead scanner flags nothing, which satisfies it perfectly.**

> **A negative assertion is satisfied by the absence of the machinery that would falsify it.** Any
> arm phrased as "X must not appear" is vacuous whenever the thing that produces X is broken — and
> that is precisely the failure the control exists to detect.

**Fixed rather than labelled**, by pairing the negative with a positive from the *same* sweep: the
local module must be absent AND a real sibling edge must be present. Now all three fail under
`scan() -> {}`.

**The bottom row is why the arm was worth having, and it was added before anyone knew what it would
catch.** Removing the *resolution* step — so the prefix matches without checking whether this repo
supplies the module — is invisible to every other arm, and the gate returns 0. A peer adopted this
arm and it failed on their first run: their namespace list was built empirically for the twelve
exact module names and **never resolved the prefix family at all**, so any local `_kt_*` module
would have counted as a sibling edge. Their count did not move — no such module exists there today —
which makes it *a right number from an unsound method, with nothing for a check to grip*, inside the
tooling built to catch exactly that.

**A refinement on "each arm must fail for its own cause":** arm 3 fails under two mutations, so it is
not cause-specific on its own. That is acceptable because **the matrix discriminates even where a
single arm does not** — under a dead scanner arms 1 and 2 fail too; under removed resolution *only*
arm 3 fails. The property worth requiring is that **every mutation produce a distinct signature**,
not that every arm map to exactly one fault.

**The general rule, which is not "write controls" but a strictly stronger thing:** *a control that
passed tells you nothing until you have seen it fail on purpose.* "It passed" is a fact about today's
code; "it can fail, and for its own reason" is a fact about the control. The second is the one worth
having, it costs three deliberate breakages, and it is the only way to distinguish a working arm from
one that is merely quiet.

**Sequence worth noting:** entry 68a was the gate catching its author, 68b was the control being
hollow, 68c is the control being untested. **Each fix exposed the next layer**, and none of the three
would have surfaced by inspection — 68b came from a peer mentioning a third party's fault, 68c from
a peer mutating their own.

### 68b. My known-fail control never called the function it was controlling

The gate from entry 68 shipped with a `--selftest` that I verified by hand, watched pass, and wired
into the suite. It built a **fake dictionary** and tested the set logic around the scanner. **It
never called the scanner.** Had `scan()` been completely broken — wrong regex, wrong root, returning
`{}` — the control would still have printed OK twice and the live gate would have been decoration
reporting zero edges as a clean bill of health.

A peer had hit exactly this the same week (their known-fail turned out to be dead code and certified
a live gate as ornamental), and I had *already written* the lesson about controls needing to fire.
Mine was written, passing, and hollow.

> **A control that does not execute the code path it certifies is not weak, it is inverted: it
> converts "the gate is silent" into "the gate is healthy", which is the one reading silence must
> never get.**

**Rebuilt to exercise `scan()` against planted files** in a temp directory — an absolute-path edge, a
path-less sibling import, and a **local module deliberately sharing the sibling prefix** that must
*not* be flagged. And on its first honest run it failed:

    BAD  selftest: absolute-path edge detected

Not a scanner bug — **my own wrong expectation.** A bare path constant classifies as `REF`, not
`IMPORT`, which is correct. The fake-dict control could never have surfaced that, because a fake
dict contains whatever I believed. *A real control disagrees with its author; a fake one cannot.*

**Also fixed in the same pass, from the same peer's empirical finding:** the namespace signal now
**resolves** rather than assumes. A hand-built prefix list flags any *local* module sharing the
prefix — their by-eye list would have declared four of their own modules sibling edges. A prefix is
now necessary and not sufficient: it counts only if nothing in this repo provides the module.

### 68a. The gate built from entry 68 found a third edge in its first run — and its own first version was wrong

Entry 68 said a scope claim needs a re-check trigger. So the claim *"their solver is not being
imported into any SpaceTime script"* was moved out of prose into
`curvature/scripts/audit_cross_repo.py`: every sibling-repo path reference must appear in a
`DECLARED` allowlist with a reason. **Undeclared edge → fail. Declared edge that vanishes → also
fail**, because a stale allowlist is a scope statement with the identical defect as the sentence it
replaced.

**Two things happened on first run, and both are the point.**

**(1) It found an edge I had not reported.** An independence audit had just asked me, in writing, to
enumerate cross-repo code dependencies. I answered from a `grep` and gave **two files**. The gate
found a **third**. My hand answer to a direct question about exactly this, given that same hour, was
incomplete — which is what a census is for and what recall is not.

**(2) The third one was a FALSE POSITIVE, and catching that mattered more.** The hit was
`ansatz/TheBridge's rule 33, adopted` — a slash inside English prose, matching a pattern meant for
filesystem paths. **A gate whose first act is to cry wolf gets switched off** (entry 55: the
false-alarm direction is the costly one). Fixed by anchoring on the absolute repo root that a real
cross-repo reference always carries, and the known-fail selftest still passes both ways.

> **A census answers a question recall cannot: "what is there now." A prose claim answers "what was
> there when I wrote this."** The audit question was of the first kind and I answered it in the
> second mode without noticing the substitution.

**And the argument for building it at all** came from a peer's observation about the previous entry:
every fault in that audit — four theirs, one mine — was caught by *a person*, and the only one caught
by a *mechanism* was a stale-reference error that a gate refused **inside the entry about stale
references**. *A lesson you must remember at the moment of decision is not a guardrail.* That is the
case for converting entries into gates rather than into more entries, and this entry is the first
test of it: the gate found something the entry's author had already been asked about directly and
gotten wrong.

### 68. Prose has no dependency graph — a scope statement keeps asserting whatever it asserted the day it was written

I wrote, in a pre-registration: *"their solver is not being imported into any SpaceTime script."* It
was true. The scripts that used the sibling repo's solver lived in a scratchpad. Later I **promoted
those scripts into the repo** — filing, not claiming — and the sentence three sections up went false
with nothing to notice it. It took an outside audit asking a question I had already answered in
writing.

> **Code has imports, and a build breaks when a dependency moves. A claim in prose has no
> dependencies and never recompiles: it keeps asserting its original content indefinitely, while the
> world it describes is edited by actions nobody thinks of as touching it.**

**The generalisation is stronger than the instance, and it explains a whole audit's worth of
findings.** Every claim that audit corrected — *"the repos are kept ignorant of each other"*, *"two
independent repos"*, *"four failure-mode-disjoint routes"* — **was true when written.** None was ever
a lie. All three went false through later action: a repo split, a promoted directory, a replication
that knew its target. And each was restated many times without re-derivation, because restating is
free and re-checking is not.

**The weapon, and it is the only one that has worked:** *a claim about the state of the world carries
a re-check trigger, or a scope narrow enough that staleness is visible.*

    "kept ignorant of each other"                  not re-checkable — survived years of restatement
    "SHARED INPUT WITH: none, checked <how>"       re-checkable, and its staleness is a diff away

**The asymmetry that makes this the default failure:** the moment of writing is when the claim is
verified, and the moment of falsification is a routine action somewhere else entirely. Nobody is
looking at the sentence when it dies.

### 69. I reported the length of a truncated list as a count

Auditing whether a migrated pipeline had left traces, I ran a search, piped it to `head -5`, and
told a peer the string appeared in **five files**. It appears in seven. **The truncation was mine,
one line earlier in my own command, and invisible in the output I then read as a result.**

`head` is a display limit. It leaves no marker, produces a well-formed list, and a well-formed list
of five things answers "how many?" with perfect confidence. **Nothing about the output says it was
cut** — which is entry 57's shape (a mechanism that did nothing looks exactly like one that ran and
found nothing) relocated into my own shell history.

> **If a number will be quoted, produce it with something that counts (`wc -l`, `len()`), not with
> something that displays. A limit applied for readability becomes a measurement the moment anyone
> reads the output as an answer — and the person most likely to do that is whoever applied the
> limit, because they have already forgotten it.**

The substantive claim survived — zero executable lines, verified separately — so the error cost a
wrong number in a message and not a wrong verdict. It was caught because the peer re-ran the search
instead of repeating my figure, which is the only reason any number in this exchange has ever been
right.

### 67. A reviewer's errors land inside their corrections, where they inherit the correction's authority

Across one long exchange, two workers made seven instances of the same species. Five were mine and a
peer caught them. Two were the peer's — **and both were committed in the act of handing me a better
check than the one I had.**

> **That is not incidental to the role, it is the hazard of it.** A correction arrives with momentum:
> it has just been *right* about something, the recipient is mid-update, and the natural response is
> to adopt rather than audit. **An error inside a correction inherits the authority of the
> correction.**

Both instances had that shape. One offered a consistency check for a ladder and built it by dividing
a baseline from one parameter value by a ratio from another — landing on `1.1×`, flush against a
boundary, which *reads as confirmation and stops the inquiry.* The other, correcting that, offered a
parameter-stability check whose numerator was **inferred rather than measured**, making it
algebraically identical to a fact already known. **Two attempts to supply a cross-check, one artefact
and one tautology**, and the real diagnosis was upstream of both: the object had no internal check in
it at all — its rungs telescope to the endpoints by construction.

**Why the recipient is badly placed to catch it:** I was reading a structure as its author presented
it. The miscount — treating four arithmetic rungs and one external comparison as five pieces of
evidence — **was theirs to make and mine to inherit.** Inheriting a frame is cheaper than building
one, which is most of why peer correction works and all of why it fails this way.

**And the symmetry is the useful part.** The same species appearing in both directions, on opposite
halves of one problem, says it is a property of ratio-heavy work rather than of either worker — which
is why the response was three mechanical rules (fingerprint the configuration, sample the null,
re-derive anything flush against a boundary) and a gate, rather than a resolution to be careful. *Not
one of the seven was caught by an intention to be careful.*

**The corollary for the reviewer's side:** the correction you are most confident in is the one to
state with its own caveat attached, because it is the one the recipient will audit least.

### 66. The argmin was the entire noise source — score a known direction, don't minimise over the basis

Every unstable number in a day of unstable numbers came from the same statistic in the same mode:
**a minimum over near-degenerate directions.** The one number that behaved was the one that did not
minimise, and the gap is nearly three orders of magnitude.

    heldout(FITTED)   min over the basis' conserved directions
                      same object, exact algebraic rescaling (δK vs −K₁/8)     1.326×  = 33%

    heldout(Q)        the SAME statistic evaluated at ONE FIXED known direction
                      same object, two ε, against ε² required by theory
                      0.052%   0.102%   0.154%

                      stability factor ≈ 650×

**Why:** an argmin over directions whose generalized eigenvalues straddle zero *reshuffles* under a
1-ULP perturbation — the mechanism behind the floor's 2.8× scatter and the 1.33× identity bound.
Scoring a direction you already know incurs none of it. **There is no minimiser to move.**

> **Wherever the candidate is known in advance, score it directly. The minimum answers *"what is the
> best-conserved thing in this basis"*; scoring answers *"how conserved is THIS thing."*** Most of
> the day's questions were the second kind and were being answered with the first instrument.

**And it corrects an attribution I had made.** I had explained the `sp.expand` exponent's survival
(1.5% under the same ULP that moved the floor 2.8×) as *the ratio cancelling common-mode noise*. Half
right: the exponent is a ratio that **partially cancels** argmin scatter, while `heldout(Q)` **never
incurs it**. *Cancelling a noise source and not having one are different things, and both are now
measured — 1.5% versus 0.05%.*

**The uncomfortable corollary:** every floor, every margin and every suppression ratio quoted that
day came from the minimising version. The verdicts survive — they rest on separations of 3 to 5
orders, far above 33% — but the *precision* implied by quoting them to four significant figures was
never there.

**How it was found, which is the part with a method in it:** one party produced the number (`3.998`
against a theoretical `4.000`), the other identified why a statistic with 33% scatter could produce
a ratio good to 0.05%. **Neither half is anything alone** — and the reason anyone looked at all was
that `0.05%` was *suspiciously tight*, which is entry 65's rule, written forty minutes earlier, being
applied. **The rule found the thing that produced the rule.**

### 65. A number flush against a boundary is usually two configurations, not a coincidence

Three times in one day a suspiciously clean number turned out to be an artefact of combining
quantities that did not share a configuration — and each time the artefact read as **more
conclusive** than the truth it displaced:

| the clean number | what it displaced |
|---|---|
| a dissolution at **13.5** against a measured **13.9** (3% agreement) | the quantity is **3.6× in the opposite direction** when measured in the right space |
| a **2.8×** two-instrument "agreement" | wrong power *and* wrong object; the real like-for-like is 193 vs 432 |
| an augmented fit landing **1.1×** above the floor, "every step accounted for" | an ε=0.05 baseline divided by an ε=0.20 ratio; the true value is **7.2×** |

> **The operational rule is sharper than "check the arithmetic": when a number lands flush against a
> boundary, or agrees to a few percent across a large change, that is the moment to re-derive it.
> Flush-against-a-boundary is what mixing two configurations produces, and what a real measurement
> rarely does.** (TheBridge's formulation.)

`1.1×` reads as *lands exactly on the floor* and stops further checking. The correct `7.2×` reads as
*comfortably above the floor* and invites the next question. **The false version was the one that
closed the inquiry.**

**And the fourth instance is the subtlest, because it survives arithmetic entirely — and its real
diagnosis is upstream of the instance.** A four-rung ladder (`Q` → best-basis fit → +column → floor)
was offered with "every step accounted for, nothing left over" as a consistency check. Two attempts
to extract a check from it produced, in order, an **artefact** (the mixed-ε 1.1×) and then a
**tautology**: "the corrector gain is ε-stable, 409× at ε=0.05 against 404× at ε=0.20", whose ε=0.20
numerator was *inferred* as 16× the ε=0.05 one, making it algebraically identical to *"the arm scales
as ε²"* — already measured at exponent 2.008, so it cannot fail unless something already known is
false.

**But both attempts failed for one reason, and it is a property of the object:**

    rung 1   Q / best-basis        =       408.7x
    rung 2   best-basis / (+col)   =    34,350.4x
    rung 3   (+col) / floor        =         7.2x
             product               = 1.0101e+08
             Q / floor directly    = 1.0101e+08     identical to 0.0000%

> **Every rung is a ratio of two adjacent measured quantities, so the product telescopes to the
> endpoints by construction. The ladder is a DECOMPOSITION, not a check. There is no internal
> cross-check in it to find** — which is why one attempt to find one produced an artefact and the
> next a tautology.

**A decomposition displays a result; it cannot test one.** The distinction is invisible from inside
because a decomposition that "accounts for every step" *feels* like a reconciliation, and arithmetic
that closes to 0.0000% feels like confirmation. It closes because it must.

**The one real cross-check in that structure was the single quantity produced by machinery sharing no
code with the rest** — an analytic Poisson-bracket drift, no basis, no eigenproblem, no conditioning,
agreeing with the engine's statistic to a factor of 2.24 at matched power and object. *The rungs are
arithmetic; the external comparison is evidence.*

**Symmetry worth recording:** this species appeared six times across two independent workers on
opposite halves of the same problem. That is not carelessness in either direction — **it is what
ratio-heavy work does by default**, which is why the response was a gate
(`curvature/scripts/comparable.py`) rather than a resolution to be careful.

### 64. Measure the null; do not reason about it

Asked whether a fitted direction was meaningfully aligned with a known invariant, I computed
`|cos| = 0.0336` and compared it to `1/√40 = 0.158` — the random-cosine baseline for an isotropic
40-dimensional space — and concluded the alignment was *below random*.

A peer caught that the basis is not isotropic (κ ~ 2.3e14), so the effective dimension
`d_eff = (Σλ)²/Σλ²` is far below 40 and the baseline should be **larger**. Measured: `d_eff = 4.34`,
giving 0.48. **That correction was right in principle, pointed the same way as my error, and pushed
harder** — at 0.48 both values sit even further below random.

Then I drew from the null instead: 20,000 random unit vectors in the same whitened space.

    median 0.0000    90th 0.0001    99th 0.0002    MAXIMUM 0.0009

**`0.0336` is at the 100th percentile. Both values are far ABOVE random, not below.** Two people
reasoned about a distribution, both got the *sign* of the answer wrong, and the correction made it
worse.

> **The mechanism is one no dimensional argument produces:** the fitted direction lives in whitened
> space and is converted to raw coefficients by dividing by `sd`, so a *random* direction is
> dominated by the tiny-`sd` features and lands nearly orthogonal to the target by construction. The
> null is not "isotropic in some effective dimension" — it is shaped by the transform between the two
> spaces, and nothing about dimension counting sees that.

**Drawing from it took thirty seconds.** Every ingredient was already in memory: the covariance, the
scaling vector, the target. There was no reason to reason.

**Attribution, because it matters for why the entry exists:** neither party originated this rule —
*the failure did.* One reasoned to `1/√40`, the other to `1/√d_eff`, **both got the sign wrong**, and
the lesson only became visible because two independent wrong answers arrived at the same wrong side.
**Had either of us happened to be right, there would be no entry** — there would be a correct
baseline, an unexamined method, and the same mistake waiting in the next problem.

**And the sequel mattered:** once the cosine was known to be a strong signal rather than a weak one,
the direct check (`corr(fit, Q) = 1.0000`) showed the fitted direction *is* the invariant, and the
like-for-like statistic then reproduced an independent analytic measurement to a factor of 2.2. **The
whole chain was unlocked by replacing one assumed baseline with a sampled one.**

> **A null distribution is a thing you can sample whenever you can generate the objects it is over.
> Analytic baselines are for when you cannot — and the moment you are correcting someone else's
> analytic baseline is the moment to notice you are both still guessing.**

### 63. I compared an amplitude to a variance twice in one night — the second time while celebrating an agreement

Two instruments sharing no machinery pointed the same way at the same effect, and I reported the
agreement as a factor of **1.75×**:

    analytic Q-drift    A/C = 13.9    an AMPLITUDE   max|Q−Q₀|/|Q₀|
    engine var_within   A/C = 24.3    a VARIANCE

    raw             13.9 vs 24.3        factor 1.75
    common power    13.9 vs √24.3=4.93  factor 2.82

**The raw comparison flatters the agreement by 1.6×.** Both numbers are dimensionless, both are "A
over C", both describe the same object — and one is an amplitude ratio of Carter's `Q` along a
trajectory while the other is a variance ratio of a *fitted direction that is not `Q`.* Different
objects **and** different powers.

**This is the same error as entry 53's neighbour, committed by the same author about nine hours
later.** Earlier that night I discounted my own gap by dividing a drift statistic (2.2e-03) by a
variance ratio (2.36e-04) and called it the night's founding species. Then I did it again — *in the
act of reporting that two instruments had agreed*, which is exactly the moment nobody re-checks the
arithmetic, because the conclusion is the pleasant one.

> **Quantities become comparable in the mind as soon as they are both dimensionless, both ratios of
> the same two things, and both pointing the same way. Dimensionlessness is not commensurability.
> Check the POWER before quoting an agreement, and check it hardest when the agreement is the
> result you wanted.**

**What survived is still the good part, at the converted number:** 2.8× agreement between an analytic
Poisson-bracket drift — no basis, no eigenproblem, no conditioning — and a whitened
generalized-eigenproblem statistic, about an effect nobody predicted. That is two instruments
agreeing rather than one correcting the other, which happened once all day. **It just has to be
quoted at 2.8×.**

**And the residual 2.8× is a question, not slop.** If the engine's candidate were exactly `Q` the two
would match after conversion. They don't, and the fitted direction is suppressed *less* than `Q`
itself — consistent with the fit landing adjacent to Carter rather than on it. Checkable with one
inner product.

### 62. Project your predicted signal against your measured floor *before* you run

I ran a three-point ε sweep to ask whether adding a column collapses a scaling exponent. Both treated
arms came back flat, I called the test void, and the peer who checked it found that **the predicted
signal was below the instrument's floor at two of the three points.**

       eps   predicted (eps² from the largest point)   ÷ its own floor
      0.05                            1.4286e-14             7.20
      0.0158                          1.4265e-15             0.72   ← below
      0.005                           1.4286e-16             0.07   ← below

The three-point fit was **one signal point and two floor readings.** The fitted exponent was
**−0.504** — the margin *growing* as the deformation shrank, which is not physics, it is floor
scatter fitted as a slope. **The sign alone should have stopped me and I quoted the number as a
collapse.**

> **A test whose predicted signal falls below its own noise floor over most of its range cannot
> return a positive. It is entry 45a with arithmetic attached — and unlike 45a, it is cheap to check
> in advance: take the predicted effect size, project it across the sweep, divide by the measured
> floor. Any point under 1 is a point that will report the floor no matter what is true.**

**The fix was the day's third instance of sweeping the wrong parameter in the wrong direction.** One
parameter here is *exact* (ε — it enters the metrics with no truncation) and one is *truncated* (χ).
Pushing the exact one **up** lifts every point clear of the floor at zero cost to fidelity. Same
asymmetry, third time, and each time the instinct was to sweep toward "smaller and cleaner" when
smaller means *closer to the noise*.

**And the control that made the eventual result readable was itself only readable because it was
uncensored.** A sham column — same momentum degree, same χ² scaling, same coordinate degrees, same
magnitude, coefficients permuted so it no longer solves the defining equation — sat **25,000× to
1,000,000× above its own floor** and showed an effect of **1.5×** where the real object showed
**2×10⁵**. On the original censored grid the sham would have read ~0 like everything else, and
"sham collapses both, so the effect is generic" would have been *exactly wrong*.

> **A negative control tells you whether a null is about your object or about your instrument — but
> only if the control itself is far from the instrument's floor. A censored control confirms whatever
> the censoring is doing.**

### 61. One ULP became 2.8×, and every verdict built on that denominator was never resolvable

A peer proposed a free consistency check: at `ε = 0` the deformation vanishes, so metrics A and B are
the same metric, and their `ε=0` floors are one computation run twice. I verified the premise
symbolically — `A(ε=0) == B(ε=0)`, exactly — and ran it expecting a formality.

    A-alone  8.2238e-15     B-alone  2.9502e-15     ratio 2.79   DISAGREE
    A+δK     1.9853e-15     B+δK     5.1712e-15     ratio 2.60   DISAGREE

**Cause measured rather than inferred.** `_A()` and `_B()` are different expression trees that are
mathematically equal at `ε=0`, so `lambdify` rounds one component differently:

    launch inputs, H, ith, dHdr, dHdth   bitwise identical
    irr                                  rel 2.86e-16    <- ONE ULP
    trajectories                         max|diff| 1.04e-17
    the floor                            2.8x

**A single ulp, amplified through 3000 RK4 steps and a generalized eigenproblem, moves the derived
quantity by a factor of nearly three.**

**The floor was never a property of `(metric, basis)`. It is a property of rounding.** And the
headline verdict the whole evening was built toward — does A's margin sit below the floor — had
**1.57× of headroom against a denominator carrying 2.8× of scatter.** Not wrong: *unresolvable*, and
unresolvable from the moment it was formulated. Every headroom figure produced that night (6.52×,
the corrected 1.57×, and the `f`-room figures 2.55× and 1.25×) was quoted to three significant
figures against a quantity that cannot support one.

> **A number that has never been measured twice has no known precision, and every verdict downstream
> of it silently inherits the precision you assumed it had.**

**The collateral damage is the more instructive part.** The peer had inferred, from a 4.14× drop in
the floor when one column was added, that the added column was capturing real structure — *"one extra
column in a ~39-column fit reduces residual variance by a fraction of a percent, not 4.1×."* Sound
reasoning. But 4.14× sits **1.5× above a 2.7× noise level nobody had measured yet**, so it is not a
signal and the inference is withdrawn — on the noise, not on the logic. I had supplied that 4.14×,
and the floor, and `f`, and **attached an uncertainty to none of them.** A recipient cannot discount a
number by an error bar it was never given.

**What survived is the quantity with no denominator.** In the same run, the unaugmented arm
reproduced its banked reference to all four digits — `4.9073e-10 / 5.1566e-11 / 5.5446e-12`, exponent
**1.947**. Exponents are within-arm *shape* comparisons: no cross-arm normalisation, no absolute
threshold, no floor. They reproduce exactly where floors scatter by 2.8×. Stated by the peer before
any of these rows existed: *everything that had gone wrong in three hours had gone wrong in a
denominator.*

**And the check was proposed as a cheap confirmation of an obvious premise.** It fired, and it
invalidated the readout it was checking. That is the most expensive outcome available and the entire
reason to spend four rows on something you expect to be a formality.

### 60. Five borrowed denominators in one evening, and the first thing that actually caught one

The same error, five times, on five axes, every instance invisible in a table that shows only ratios:

    1  A+dK margins / A-alone floor              axis BASIS          caught by a peer
    2  A+dK/floor_A vs B+dK/floor_B              axis ENSEMBLE       caught by a peer
    3  margins at 90/9000 / floor at 40/3000     axis RUN PARAMETERS caught by LUCK (wrong mode was slow)
    4  margins at seed 0 / floor at seed 1       axis SEED           caught by running the floors
    5  min over 4 directions / min over all      axis READOUT        caught by reading the reference

Instance 4 and 5 together moved a floor I had quoted in every message that night — `8.2238e-15` —
to `6.0405e-17`, a factor of **136**, purely from configuration. Had I compared against the quoted
value, the collapse prediction would have flipped from pass to fail on a number that measured
nothing but my own inconsistency.

**Four of five were caught by a second party reading the work.** Not by documents: two of the
relevant catalogue entries were written by me, hours earlier, describing the exact move. I wrote the
peer's generalisation into my own notes — *check what a quantity SHARES with what it is compared
against, not only what changed* — and produced a fourth instance **in the next launch.**

**Why prose cannot fix this: the axis list is open.** Basis, ensemble, run parameters, seed, readout,
and still ahead of us integrator settings, precision, code version, grid. An enumeration cannot close
an open list, *and an enumeration and a class behave identically on every instance already seen* —
which is the always-true-guard failure one level up in abstraction, and exactly why writing the class
down did not stop me producing instances of it.

**So this one got a gate, not an entry** (`curvature/scripts/comparable.py`, in `verify.sh`). A value
carries the configuration that produced it; a comparison declares which axis it varies along and
**asserts the fingerprints agree everywhere else.** All five instances collapse to one assertion
failure, raised at the moment of comparison, with the offending axis named — no one has to remember
the class. Its known-fail suite is the five real mismatches above; if it stops catching them it fails
loudly.

**Instance 5 is why a document could not have worked, and this is stronger than "prose does not
fire."** A convention can have **two authorities that disagree, each locally correct**: §190's
`screen()` minimises over `min(4, ·)` conserved directions, while the script that produced the banked
reference used all of them. Following the library made me inconsistent with the reference; following
the reference made me inconsistent with the library. **There was no source I could have obeyed to be
right.** A convention note saying "use `min(4,·)`" would be obeyed by one party and contradicted by a
file that predates it, and *both parties would believe they were compliant.*

> **The gate does not need to RESOLVE the ambiguity — only to make it VISIBLE. And visible is
> sufficient: you cannot be right by following one source, but you can be right by being told the
> sources differ.** (TheBridge)

So the night's recurring complaint — that documents fail to fire for their own authors — was not the
real problem. **Here no document could have been correct.**

**And the supply side of it, which is mine.** The peer computed headroom from `8.2238e-15` across
three messages without asking where it came from, and called that their failure. It was not: *I
supplied the number, repeatedly, without its configuration.* A reader cannot ask for a fingerprint
they have no reason to believe is missing, and treating a supplied number as a constant of the
apparatus is the correct default. **Which is precisely why the configuration has to be attached at
construction rather than requested at use.**

**The positive half, and it is why one result survived:** a ratio taken *within* a single
configuration is self-normalising — the parameters appear in numerator and denominator and cancel —
so it is transportable. `f = a·χ + b` was built from within-run drift ratios, which is why it
survived two relaunches that invalidated every absolute number it had been combined with. The gate
marks these `within=True`.

**And the honest note on instance 3:** it was detected only because the wrong mode was the *slow*
one. A flag that silently selected the *cheap* mode would have produced a fast, clean, wrong answer
with nothing to prompt a second look. Three times that night, what separated a caught fault from an
uncaught one was which direction the failure happened to point.

### 59. A mode flag set through the wrong channel is silently ignored — and it moves the baseline, not just the cost

I launched two runs with `env FAST=1`. The script reads `"--fast" in sys.argv`. **The environment
variable did nothing**, and both runs proceeded at the full-mode defaults while I believed they were
in fast mode.

Nothing errored. Nothing warned. An unrecognised environment variable is indistinguishable from one
that was honoured and had no visible effect — the same shape as entry 57's substitution dict that
matched none of its keys. It surfaced only because the runs were *slower than I expected*, which is
the weakest possible detector and works only when the wrong mode happens to be the expensive one. **A
flag that silently selected the *cheaper* mode would have produced a fast, clean, wrong answer.**

**But cost was not the damage.** The reference numbers this experiment compares against — a banked
exponent of 1.947 and an emit floor of 8.2238e-15 — were produced by a script that set
`NTRAJ, NSTEP = 40, 3000` *explicitly*. The defaults are `90, 9000`. So the run would have divided
margins computed at 90/9000 by a floor computed at 40/3000:

> **the borrowed-denominator error for the third time in one evening — first across BASIS, then
> across ENSEMBLE, now across RUN PARAMETERS — and every instance was invisible in a table that
> shows only ratios.**

The peer-supplied generalisation that finally covers all three: *every quantity in a comparison must
be checked for what it **shares** with the thing it is compared against, not only for what changed.*
I had been enumerating instances of that class while believing I had the class, **and an enumeration
and a class behave identically on every instance you have already seen** — the always-true-guard
failure, one level up in abstraction.

**What makes a mode flag worse than an ordinary wrong parameter:** it does not read as a parameter at
all. `--fast` sounds like it trades accuracy for time, so it gets treated as a cost knob and reviewed
as one — while it silently redefines the baseline that every downstream comparison is measured
against. Entry 55 says an artifact must record the mode it was produced in. **This says the mode is
not a property of the artifact's provenance, it is a property of its NUMBERS.**

### 58. Forecasting the accepted arm from the rejected one

Having run a control at two settings of a sign, `σ=+1` and `σ=−1`, I had one arm measured at both
values of a second parameter and the other measured at only one. So I extrapolated: the rejected arm
had improved by 1.61× between the two settings, therefore the accepted arm would land near 125×.

It landed at **623.7×**. The peer who refuted the estimate before the number existed gave the reason,
and the reason is structural rather than numerical:

> **The rejected arm was rejected because of a defect. That defect is exactly what governs how it
> responds to the parameter. So the rejected arm is the one measurement in the experiment
> *guaranteed* not to generalise to the accepted one.**

Concretely: the object is pure `χ²`, so flipping a component's sign leaves a residual proportional to
`χ²` — the *same* power as the quantity being cancelled — hence a **χ-independent** error fraction. A
wrong sign is a constant-offset error *by construction*, and a constant-offset error barely improves
when you lower `χ`. The rejected arm's 1.61× was not a weak version of the accepted arm's behaviour;
it was a measurement of the defect I had just removed.

**Why it was tempting:** it was the nearest available data, it was in the same table, it came from the
same code path, and it was about the same object. Every surface property said "comparable." The one
property that mattered — *why is this arm not the answer* — was the property that disqualified it.

**And a hedge is not a control.** I wrote the estimate with "a preview I am not going to over-read"
attached. I still wrote the number down, still sent it, and a hedged number is a number a reader can
carry forward without the hedge. The hedge protected my reasoning and not the claim.

**Compounding, on the same night:** this and entry 53's sharpening failure went out in consecutive
messages to the same peer, both stated more confidently than their caveats, both corrected by them
rather than by me. The instrument that caught both was a second party who was not grading my design.

### 57. `subs` cannot fail, so a substitution dict is a silent instrument

Building a convention bridge between two repos, I wrote a substitution keyed on `"P_x"`, `"P_y"`,
`"P_t"`, `"P_phi"`. The source momenta are named `p_r`, `p_u`, `p_t`, `p_phi`. **The dict matched no
momentum at all**, and `expr.subs(...)` reported nothing, because a substitution that finds none of
its keys is not an error — it is the identity.

The near-miss is the part worth keeping. One name, `p_r`, **exists in both namespaces** with
different assumptions (`real=True` theirs, `positive=True` mine) — so they are different symbols that
print identically. `lambdify` emits a function whose parameter is spelled `p_r`, and the body's
foreign `p_r` binds to it **by name**, correctly and by accident. So the bridge would have been right
about exactly one coordinate and silently absent on three, and the object it produced would have been
a number rather than a crash.

> **A translation layer whose failure mode is "does nothing" needs a completeness check, because
> nothing is exactly what a correct no-op looks like.**

That is the same species as 45a one level down: the wrong answer and the right answer have the same
shape, so the instrument cannot distinguish them and neither can you. Fixed with an assertion in both
directions — every source symbol must be consumed, and nothing unexpected may survive.

**And the reason it was worth reading the names rather than scanning past them:** their `y` is
`u = cos θ`, which fixes the conjugate momentum by calculus (`p_u = −p_θ/sin θ`) and turned an open
sign I had planned to *resolve by control* into a sign I could *predict*. The bug and the prediction
came from the same act of looking at what the symbols actually were.

### 56. The only exit that happens unattended is the one that misreports itself

My coordination heartbeat was dead for 2.5 hours overnight under a standing instruction to keep it
running, and the status file it left behind said it had not stopped deliberately.

It had. The loop carries a **10h TTL** so an abandoned heartbeat cannot run forever, and it exited
exactly on time, code 0, logged. But **the TTL path wrote nothing to the status file.** It left
`stopped_deliberately: false` and a `note_to_readers` still saying *"Writer is LIVE"*, and simply
stopped updating. To any reader that is the precise signature of a **crash** — and the flag that
exists for no other purpose than to tell those two apart was never set.

> **An explicit-stop path gets its flag set because you are standing there writing the stop. The
> timeout path is the one that fires while nobody is watching — which is exactly why it is the one
> that must announce itself, and exactly why it is the one nobody remembers to instrument.**

Worse than an uninstrumented exit, for the reason entry 2 of this heartbeat's own header comment
already gives about timestamp-only updates: the failure emits a signature the monitoring was built to
interpret, rather than no signature at all. The same script that documents that lesson in a banner
comment contained a second instance of it further down.

**Fixed, and verified by firing it** — a throwaway status file and `TTL=0`, because a repair to an
unattended path that is never actually triggered is a claim, not a fix. It now writes
`stopped_deliberately: true`, sets state idle, freezes `measured` with a note not to schedule against
it, and names the restart command.

**The companion error, mine, ten minutes earlier:** asked whether my own heartbeat was up, I ran
`ps | grep -i keepalive`, saw a 17-hour-old process, and reported *"keepalive up 17h21m as
instructed."* It was **another session's** heartbeat, for a different repo. I matched on the word
`keepalive`, not on ownership — entry 46's mistake (identity by string rather than by the thing) in
its most embarrassing form, since a monitor-liveness check that matches any monitor on the machine
reports success whenever *anyone* is monitoring. The real check is the one that actually found it:
read the status file my writer owns and compare `updated` against `stale_after_s`.

**Amendment, after TheBridge checked their own by PID and `lsof` cwd** — three heartbeats were
running, in three repos, answering to one string:

    pid 23920  17h  cwd=/Users/sumit/Github/BlackHole     <- the one I reported as mine
    pid 33618       cwd=/Users/sumit/Github/TheBridge
    pid 31412       cwd=/Users/sumit/Github/SpaceTime     <- actually mine

Their generalisation is worse than my instance, and is the version to keep: **a liveness check
scoped by name rather than by ownership returns SUCCESS more often the more crowded the machine
gets. It degrades in the direction that looks like health.**

And the correction I owe my own write-up above: I said the `updated`-vs-`stale_after_s` comparison
is "the real check", as though I had chosen it. I had not. **It saved me by accident** — that field
exists for staleness detection, and nobody put it there to prevent cross-session misattribution. A
near-miss that depends on a property nobody selected for that purpose is not a control, and writing
it up as one converts luck into a procedure that will not hold next time. *The check that caught this
was the right check; that I was running it was not design.*



### 45a. A test whose two outcomes are not distinguishable by the thing it measures

Filed as a companion to 44 rather than a new number, because it is that mechanism in experiment design.

This repo has built the shape **twice**. §180–186's G1b was *vacuous twice* — the difference-based zero-test
is unconstructible over any range with `L ≪ ξ`, so omitting the subleading column gives false positives and
including it absorbs the genuine log. And tonight, setting up the `δK` collapse test, I ran a premise check
with `ε ∈ {0, 0.05}` — the floor and one margin, **enough to see headroom and not enough to measure an
exponent at all.** I was one step from asking a peer for `δK`, adding it, and testing whether A's exponent
*collapsed from 2* — **without ever having checked there was a 2 to collapse.**

> **A gate whose only passing outcome is a failure, and a collapse test with nothing to collapse, are the same
> object: a measurement whose two possible results are not distinguishable by the thing being measured.**

**The reason it survives design review is the part worth keeping** (TheBridge's formulation):

> **It is invisible from inside the design, because from inside you are always asking "will this work" and
> never "could this have come out the other way."**

Both times it took someone outside the design to see it. That is the four-catches mechanism of this same
night — *the party who would benefit going and getting the answer that costs them* — pointed at experiment
design instead of at claims, and it has the same non-implementation: **you cannot write a gate that asks
whether your test could have failed, because the gate is built from the same understanding that could not see
it.** The only thing that has worked is a second party who is not grading the design.

**The cheap partial defence, since a full one does not exist:** before running, state the outcome that would
falsify the thing being tested, and check that the instrument as built can *produce* that outcome. Not "what
will this show" — **"what is the shape of the data that says no, and can this configuration emit it."**

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

**THE WORST CASE WAS MY OWN, AND I FOUND IT ONLY BY RUNNING THE FIXED SCAN IN PRODUCTION.** This repo's
central instrument is `./verify.sh` — 66 gates, ~30 minutes, the thing that decides whether a result is real.
Its entry point is:

    exec .venv/bin/python scripts/verify_gates.py

**Relative interpreter, relative script.** So while the suite was running, at 68.5% CPU:

    OLD scan  pgrep -f 'SpaceTime/curvature'   ->  0 hits
    NEW scan  by cwd                           ->  1 hit

**Every regression run this project has ever done was invisible to its own heartbeat.** The status file that
sister sessions read to decide whether the machine is free would have advertised `n_procs: 0` — *tabula idle* —
for the entire duration of the heaviest workload in the repo. Not a hypothetical near-miss on one relaunch: the
single most important process here was the one the monitor could never see, for the monitor's whole life.

And the failure is silent in both directions at once. The field was **derived**, it **jittered**, it was
**fresh** — it passed every check built to distinguish a real heartbeat from a bumping one (failure mode 2
above), because those checks confirm the *loop* is measuring, not that the *scan* can see. A liveness probe can
be provably alive and structurally blind.

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

**AND THE FIX ITSELF BROKE A CONSUMER, WHICH NOTHING DETECTED FOR NINE HOURS.** The cwd rewrite above is
correct and I shipped it with two known-fail controls. What neither control covered was a *downstream* field.
`state` was derived as `"running" if procs else "idle"` — correct while `procs` came from an argv match on this
repo's own scripts. Widening detection to cwd widened `procs` to include **an idle login shell whose working
directory happens to be the repo**, so the heartbeat published:

    state: running        n_procs: 3        n_active: 0

to every sister session using that file to decide whether the machine is free. **The label said busy; nothing
was computing.** I had added `n_active` that same morning for exactly this distinction and never pointed
`state` at it — the honest dual counts went in beside a collapsed label still reading the wrong one.

> **Fixing an input can corrupt a consumer that was correct under the old semantics.** The bug is not in either
> piece; it is in the fact that widening a definition is a silent interface change to everything downstream.

Nothing failed. The field was derived, fresh, and jittering the entire time — it passed every check built to
distinguish a real heartbeat from a bumping one, because those checks ask whether the loop is *measuring*, not
whether the measurement still *means* what its name says. Corrected to key on CPU rather than presence
(`heavy` likewise), and verified in both directions: idle → `idle`, a live 100%-CPU job → `running`, job
killed → `idle`.

**Three of this file's entries now describe the same morning's fix breaking something else** (46 the scan, 49
the wait-loop, this one the label). The repair rate is not the problem; **the invisibility is** — every one of
these published a plausible, well-formed, freshly-timestamped value.

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

### 49. The filter that removes your own footprint removes your neighbour's too

Entry 46 said an argv scan misses the *worker*. TheBridge, checking it independently on the same machine within
the hour, got something worse: **their scan returned neither pid** — not the worker and not the monitor —
`ps -eo pid=,command= | grep conjecture_machine | grep -v grep` → nothing, on a machine running a 1.2 GB job
with nine hours left and a live watcher on its output.

They proposed macOS `ps` truncation (the repo name sits at offset 306 of a 709-character argv) and — correctly —
**flagged it as inferred rather than isolated.** So I measured it:

    pid 1655 (job)      ps -p / -ww / -eo / -eww / -Ao   ->  193 chars, all five identical
    pid 1686 (monitor)  ps -p / -ww / -eo / -eww / -Ao   ->  708 chars, all five identical

**No truncation, in any form, at any width.** The hypothesis is refuted; the observation is exactly right. The
real mechanism is one line further down the pipe:

    ps -eo pid=,command= | grep conjecture_machine                 ->  1686 found
    ps -eo pid=,command= | grep conjecture_machine | grep -v grep  ->  nothing

**The monitor is `tail -f … | grep -E "GUARD FAILED|MemoryError|Killed|…"`. Its argv contains the word `grep`.**
So `grep -v grep` — the reflex everyone appends to remove the scan's own footprint — deletes it.

> **A hygiene filter defined by what your instrument looks like will also delete every neighbour that looks
> like your instrument.** And the processes that most resemble a scan are *other people's monitors*, because a
> monitor is a scan someone left running.

**The two failures compose, and neither alone produces the observed silence.** The worker is invisible because
its argv carries a relative path (entry 46). The monitor is invisible because your own hygiene filter eats it.
Net result: **a scan that returns absolutely nothing on a busy machine.** "Nothing is running" and "my scan
cannot see anything" are byte-identical outputs, and this is the default idiom, not an exotic mistake.

**The kill path and the observe path fail differently, and both are live.** `pgrep -f conjecture_machine`
carries no `grep -v grep`, so it returns **1686 and not 1655** — confirmed by direct check:

    is the JOB    (1655) in pgrep -f conjecture_machine?  -> no
    is the MONITOR(1686) in pgrep -f conjecture_machine?  -> yes

So the *kill* asymmetry of entry 46 stands unchanged — `pkill -f` kills the observer and spares the subject —
while the *observation* blindness is total. One idiom under-reports the machine to zero; the other aims the
signal at precisely the wrong process.

**AND IT MAKES ABSENCE UNOBSERVABLE, WHICH I FOUND BY HANGING ON IT TEN MINUTES AFTER WRITING THE ABOVE.**
Waiting for the old keepalive to exit before starting the new one:

    until ! ps -eo command= | grep -q "SpaceTime/curvature/scripts/keepalive.sh"; do sleep 2; done

This never terminates. The `grep` process carries the pattern in its own argv, so the scan matches itself, so
the condition "no such process" is **structurally unreachable** — the loop ran until the 2-minute tool timeout
killed it. The count-inflation direction of self-matching is well known; this is the other one:

> **A self-matching scan cannot observe absence. It does not report a wrong count — it converts a wait into a
> hang, and the hang looks like the thing you are waiting for being slow.**

Fix: wait on the **PID** (`until ! ps -p "$K" >/dev/null; do …`), which cannot match the waiter. Same lesson as
the entry it sits in — identity, not pattern.

**Method note, and it is the transferable part.** They labelled their mechanism as inferred and their three
outputs as verified, which is what let me test the mechanism instead of inheriting it — and testing it produced
a better explanation than either of us had. **Entry 48 in the other direction: a correction that inherits an
unexamined premise is the same mistake at higher confidence; a hypothesis published as a hypothesis is an
invitation to look.** Had the truncation guess been passed on as fact, `-ww` would have been the fix, it would
have changed nothing, and the silence would have survived with a plausible cause attached to it.

### 50. The disclosure of a leak can be a larger leak than the leak

The first entry here whose subject is a **correction** rather than a measurement.

A blind cross-instrument leg was set up between two repos: a 4D metric, stripped of provenance, no claim
attached, both instruments to report before being told anything. The operator then sent each participant a
short note on why the leg was worth their time. Mine said the object was *"neither of your two catalogued cases
— the intermediate one, and it discriminates."* I flagged that as a leak: it narrows the answer space, and a
verdict produced under it cannot be filed as blind.

**The operator agreed, and to show the damage honestly, quoted what they had sent the OTHER participant:**

> *"This object's invariant is polynomial in the momenta with non-polynomial coefficients in position — the
> intermediate case that discriminates, and neither of you knows that is what you are being handed."*

**That sentence had not reached me. The retraction delivered it.** Before the correction I had a hint about
*where* the answer sat; afterwards I had its **structure in both arguments** — that an invariant exists, that
it is polynomial in the momenta, and that its position dependence is not. For an instrument whose entire job is
to separate *no invariant* (flat degree ladder) from *an invariant my basis cannot represent* (descending,
never arriving — §178), that is not a narrowed space. **It is a statement of what the readout should print.**

> **A confession must say what was said, and saying it faithfully re-transmits it — to a recipient who, by
> hypothesis, did not have it.** The more scrupulous the retraction, the more completely it delivers the thing
> being retracted.

**And it is the same mechanism as the original, one level up.** The operator's diagnosis of their own leak was
that they *knew the answer while composing reasons the leg was worth doing, so every reason was drawn from the
answer* — and, more generally, that these leaks *are what care looks like when it takes the form of
explaining*. **A confession is care taking the form of explaining.** It inherits the failure exactly, which is
why the honest instinct — quote it verbatim so the reader can judge the damage — is the one that does the
damage.

**The repair that does not repeat the leak: name the CLASS, never the CONTENT.** "I stated the invariant's
structure" carries everything a reader needs to discount the verdict and none of what would bias it. The rule
generalises past leaks to any correction whose subject is information that should not have moved.

**A companion rule from the same exchange, about the other way a repair goes wrong** (the operator's, filed
here because it is the same family): **"withdrawn on provenance" and "withdrawn on accuracy" must never appear
in one sentence — the reader keeps the stronger one.** A peer's description of my work was retracted because it
had been derived by reading my repository rather than by asking. Checked against the files, **the description
was correct.** Retracting the route in language that reads as retracting the content leaves the record worse
than before the correction: a true statement is now on the books as withdrawn.

> **Both failures are in the repair, not in the original error.** A catalogue of ways to be fooled that never
> examines its own correction machinery is auditing only half the process — and the corrections are written
> under time pressure, by someone who has just been shown to be wrong, which is not the condition in which
> people are most careful.

### 51. An inherited figure is pre-attached to a conclusion, which is what makes it feel checked

Two failures of the same number on the same day, in two repos, with different causes — and the less excusable
one was mine.

A peer opened a coordination round with a motivating fact, in bold: *the bridge has not asked its own question
in **eleven weeks**, and nothing replaced the spine since it closed on 2026-06-17.* Four sessions read it, four
accepted it, and several reasoned from it. Days later the author built an unrelated gate, which made them run
`ls legs/`:

    41 leg directories.  33 created AFTER the spine closed.  Last activity 2026-08-22.
    The gap was ~6 weeks, not eleven.

**Their half is asymmetric access.** The closing date was measured; "therefore eleven weeks with no legs" was
inferred and never checked. It survived four careful readers because **only the asserting party could falsify
it** — they hold the directory. A claim whose sole possible referee is its author has no referee.

**My half is worse, because I had the data locally.** Having read their message I wrote into my own JOURNAL
that both of this project's finales "closed in June" and that the roadmap had been stale for **"eleven weeks"**.
I measured neither. One `git log --diff-filter=A` says:

    Finale 2 evidence      2026-06-13   ->  83 days = 11.9 weeks
    KK trilogy: mass       2026-07-03
    KK trilogy: axion      2026-07-10   ->  56 days =  8 weeks

"Closed in June" is false for the trilogy; "eleven weeks" is right for Finale 2 and wrong for the trilogy.
**The half that was right was right by coincidence** — an inherited interval attached to a claim it happened to
fit.

> **A figure that arrives inside someone else's argument is not evidence for yours, however careful they are.
> It arrives pre-attached to a conclusion, and that is exactly what makes it feel already checked.**

The two halves separate cleanly and both are worth watching for: **asymmetric access** lets a claim survive
expert readers who *cannot* check it; **inheritance** lets one survive an author who *can* and does not, because
it has already passed through someone careful. The second needs no special circumstances and is therefore the
common one.

**THE REPAIR, BUILT AND IMMEDIATELY WRONG.** A sibling supplied the missing half: they caught their own
version of this only because their user had asked them to audit the repo minutes earlier — *"luck wearing the
costume of rigour."* Which means **adding "check it anyway" to a protocol changes nothing, because the moment a
check needs to fire is the moment nobody is looking.** Only a pass that runs whether or not anyone is
suspicious reaches it. So this repo now has `curvature/scripts/audit_doc_claims.py` in `verify.sh`: catalogue
count vs actual entries, every cited results file and script number existing, no roadmap line marked done and
undone at once — the 2026-09-04 bug itself.

**It was wrong on its first live run.** It flagged `results/19_ckpt.pt` as a missing artifact. That file is
cited in exactly one place — the sentence recording that it was *renamed* to `19_ckpt_v1_failed.pt`, which
exists. The citation was correct and the absence was the point of it.

An hour earlier I had told the same sibling that their new gate encoded a distinction *"settled by argument
this afternoon and never tested against a case designed to break it — a gate whose own criterion is an
inference, whose known-fail control tests that the gate fires, not that the criterion is right."* **My own gate
then did exactly that, and the control I had written passed 5/5 while the rule was wrong.**

> **A known-fail control tests the MECHANISM. Only contact with real data tests the RULE.** A control is built
> from the same understanding as the thing it checks, so it cannot see the cases that understanding omits.

Fixed by exempting a documented rename — an arrow to a name that does exist — and by adding *both* directions
to the control: a documented rename must pass, and a rename to a target that is also missing must still fail.
The exemption is deliberately mechanical rather than clever, because **a wrong audit is worse than none: it
teaches you to ignore it.**

**Then a second fault, found in the same hour, and this one had been PASSING.** The count check used
`re.search` and took the *first* match. CLAUDE.md contains two such claims: a dated status block recording
*"silent_nulls → 18 entries"* (a correct historical statement about the count at that time) and the newest
block carrying the live one. The check should have compared against 18 and failed. **It passed only because
the historical line words it differently enough — `→ 18 entries**` — to miss the pattern.**

> **A gate that is right by an accident of formatting is indistinguishable, from the outside, from a gate that
> is right.** Both print PASS. The green tells you nothing about which one you have.

This is the same species as entry 46's argv match: the check appeared to work and its correctness rested on a
coincidence of how someone happened to write a string. Corrected to the actual semantics — historical claims
may be *below* the real count, the live claim (the maximum) must *equal* it, and any claim *above* it is always
wrong — with the multi-claim case added to the control. 9/9.

**A THIRD FAULT, AND IT SHOWS WHAT THE FIRST TWO FIXES ACTUALLY WERE.** A peer, checking this same rule
against their own gate, found it there twice — including the exact first-match shadowing — and diagnosed the
root cause as **a regex over a structured file**; they replaced theirs with a real TOML parse. That does not
transfer here, because my source genuinely is prose and there is nothing to parse. So I probed mine instead of
agreeing with them, and found a third case my "use the maximum" fix still passed:

    live claim correct, historical below         passes   correct
    aspirational claim above actual              FLAGS    correct
    STALE live claim, historical happens to
      equal the true count                       passes   WRONG

The mirror image of the second fault: a stale live claim shadowed by a *correct* historical one. `max()` cannot
see it, because the maximum is right while the live claim is wrong.

> **Each of my first two fixes was a narrower positional heuristic — first-match, then maximum — and only the
> third was the semantics: the LAST claim is the live one and must equal the count; no claim may exceed it.**
> A positional rule over prose is a guess about how someone will write, and each fix that keeps the guess and
> narrows it is the same defect at higher confidence — entry 48, inside a gate built to catch entry 48.

**Three faults in one small gate, in one evening, in the check whose entire job is catching stale claims —
written by an author who had spent the day cataloguing stale claims.** The first was caught by real data. The
second by re-reading output I had already accepted as green. **The third only by deliberately probing a rule I
had already fixed twice and believed.** Nothing about the greens distinguished the three states.

The one durable lesson under all of it, and it is the peer's, sharpened by the fact that it did not transfer:
**the defect is inferring structure from text that has no structure.** Where a structured format exists, parse
it and never regex it. Where it genuinely does not — prose — the only defence is to encode the *meaning*
(which claim is live, what relation must hold) rather than the *position*, and to probe the rule adversarially,
because a control written from your own understanding cannot contain the case that understanding omits.

**THE SHARPEST SPECIAL CASE, AND IT IS ABOUT PRAISE RATHER THAN NUMBERS.** The same peer drew a favourable
comparison between me and a third session on this exact failure — they had audited their docs, I had adopted
the figure. The third session **refused the credit and demolished the comparison**: their check happened only
because their user had asked them to audit the repo minutes earlier. *"Luck wearing the costume of rigour."*
Had the message landed two hours sooner they would have read it, agreed, and moved on — the same as me. The
difference was **context, not practice.**

The part worth recording is from the inside: **when the flattering comparison arrived, my first reaction was
that it sounded fair.** I did not run the cheap check on it. Neither did the peer who made it. It took the
party who *lost* by the comparison to refuse it.

> **A claim that flatters its recipient is the one class where the recipient is guaranteed not to run the cheap
> check** — and a claim that has already passed through a careful reader acquires the feeling of having been
> checked. Praise combines both, which is why an unearned credit survives longer than an unearned number.

**The repair is the same both times and it is not more scrutiny.** More reading would not have caught either —
four readings did not catch theirs, and mine was in a file I wrote myself. What caught both was **touching the
state**: an `ls`, a `git log`. Which sharpens entry 50's companion observation into the form the peer gave it,
better than my own:

> **A gate corrects you for reasons it was not designed to catch, because it makes you touch the data. Prose
> only corrects you for the reason it was written.**

Their error survived four prose referees — two commit messages, a README, four messages — and died in under a
minute to a gate that was not looking for it. Prose referees are pull-based and topic-scoped; an executable one
is push-based and hits whatever the state actually is. The same shape as this repo's own heartbeat blindness:
the entry describing it existed *before* the bug was found, and only running the fixed scan against a live suite
found it.

### 52. A pre-registration can register the interpretation and forget the correspondence

Entry 44 said naming a failure mode and detecting it are separate acts. This is the same split one level
earlier, and it voids the whole document rather than one clause.

TheBridge's own leg, reported against themselves: **three outcomes pre-registered for a scaling exponent, each
with a precise interpretation — and the exponent was measured at fixed `l` while the study ran at fixed
`l/L`.** Every registered reading was about what the number would *mean*. None was about whether the two setups
were measuring the same thing.

> **A pre-registration can name every outcome precisely and still be void, because it registered the
> interpretation and not the correspondence.** The interpretation clauses all look rigorous, and not one of
> them can fire, because they are conditioned on a quantity that was never the quantity in hand.

**Our own near-miss, on the sweep this was sent to protect.** §187 locates §42's criticality gate. The frozen
design said ξ would be **measured** from the correlation envelope rather than assumed from `1/(2m)`, and
reported the textbook value alongside as a comparator. Prompted to state the ξ convention exactly, we checked
it: for `h_{i,i+1}=1` at half filling `ε(k) = −2cos k`, so **`v_F = 2`** and `ξ = v_F/gap = 1/m`, **not
`1/(2m)`**. Confirmed from the data, not the algebra — `ξ_meas·m` → 0.85, 0.95, 1.07, 1.21 while `ξ_meas·2m` →
1.71, 1.90, 2.14, 2.42.

**The comparator column was wrong by exactly a factor of two, and it reached nothing**, because ξ was measured.
Had the pre-registration taken the textbook route it offered, the entire x-axis would have been off by 2 and
no gate, control or endpoint check in the run would have said so — `R_CoV`, the L1 endpoints and the
monotonicity all live on the mass axis and are blind to what the ξ column claims.

> **Measuring a quantity you could have derived is worth the cost precisely when the derivation carries a
> convention.** A derived axis inherits every assumption silently; a measured one can only be wrong in ways
> the data can show.

**A THIRD SPLIT IN THE SAME FAMILY, from the same run, and it is narrower than the first two.** §187's
pre-registration **did** name the trigger — *"measured ξ disagreeing with `1/(2m)` by more than 3× in the
regime where they should agree → the ξ fit is broken"* — and **did** build a guard. The guard was written for
the crossing landing at the **grid edge**. The actual failure was the **x-axis going unmeasurable at an
INTERIOR crossing**: comfortably inside the swept range, monotone, uncensored by the guard as written, and the
ξ value still meaningless because the envelope decays 3.2% across the fit window.

> **Naming a failure, and building a detector for the right failure in the wrong geometry, are separate acts.**
> The second feels much closer to done than the first, and produces a document that survives review — the
> trigger is there in writing, and a reader checking whether the mode was anticipated will find that it was.

So this family now has three rungs, each a step past the last: **naming ≠ detecting** (entry 44); **registering
the interpretation without the correspondence** (above); and **detecting the named failure in only one of its
geometries** (here). All three produce a pre-registration that reads as rigorous and cannot fire.

**And the part worth keeping about how it was caught.** Their pre-commit hook **refused the prediction file**
with `PREREG WITHOUT A SETUP-CORRESPONDENCE LINE`, and they nearly read it as formatting noise. That is the
third instance this month of a gate's own output being close to dismissed as decoration — alongside our
documentation audit, which **passed by an accident of formatting** (entry 49) and whose green was
indistinguishable from a green that meant something.

> **The failure mode of an executable referee is not that it stays silent. It is that its output arrives
> looking like paperwork.**

### 53. Sharpening a vague-but-correct statement into a precise-but-false one feels like an improvement

A peer looked at two ξ estimates disagreeing by 1.73× at a wall and said: *"that is what an unmeasurable axis
looks like from outside."* Vague, unfalsifiable as stated, and **right**.

I sharpened it. Having checked the ratio across the whole sweep and found it crossing 1.0 at `ξ/N ≈ 0.15`
rather than merely diverging, I wrote back that *"the two methods calibrate each other somewhere, and that
somewhere is inside the measurable band"* — and added that this was **a stronger statement than theirs and a
different one**. They agreed, adopted it over their own, and filed it.

It is false. Running it (§188) rather than narrating it:

    W = 64    ξ_cross = 31.9    ξ_cross/W = 0.498
    W = 128   ξ_cross = 69.4    ξ_cross/W = 0.542

**The crossing sits at ξ ≈ W/2 and moves with the fit window.** The two estimates do not calibrate each other;
they are two window-dependent curves that happen to intersect, and the intersection is a property of where the
line was drawn. The saturated ratio itself moves **3.38 → 1.72 → 0.78** across windows on *identical data* — a
334% swing — so `√3` was a coincidence of `W = N/4`.

> **A vague statement can be unfalsifiable and still true. Sharpening it adds content, and the added content is
> exactly the part that has not been checked** — because what was checked was the vague version.

The asymmetry that makes this dangerous: **sharpening feels like the rigorous move.** It converts a hand-wave
into something testable, which is the thing this whole catalogue argues for. And it is the right move — but the
sharpened claim arrives with the *credibility of the vague one it replaced*, and nobody re-checks a statement
that just got more precise. The peer adopted mine over theirs on the strength of its sharpness, not its
evidence, and neither of us noticed the evidence had not moved.

**THE FAILURE HAS TWO HALVES AND ONLY ONE IS MINE.** I proposed the sharpening; **the peer promoted it to the
record and checked nothing**, adopting it over their own sentence on the strength of its precision. Their
words: *"promotion is where the check was owed."* So the shape is not simply *an author oversharpens* — it is
that **a sharper sentence passes through a second party unchecked precisely because sharpening looks like
work already done.** A vague claim invites scrutiny; a precise one looks like the product of it.

**AND THE CHEAP INSTRUMENT WAS SITTING THERE TWICE, IN THE SAME TWO COLUMNS.** Their observation, and it is
better than either of my two findings:

- They divided `ξ_derived / ξ_measured` — two columns already in my results file — and got the 1.73 nobody had
  noticed. **That produced a diagnostic.**
- I then divided `ξ_cross / W` — again numbers already sitting in the same run — and got 0.498, 0.542.
  **That destroyed the diagnostic's interpretation.**

Same file, same run, one line each, and **neither division was done until someone went looking for something
else.**

> **A quantity that exists as two columns in your own output is the cheapest instrument you will ever have, and
> it stays unmade because making it is nobody's job.** Every pipeline produces these; a gate computes what it was told to
compute, and the ratios *between* its outputs are the part no one is assigned.

**THE PEER THEN FOUND A WORSE VARIANT IN THEIR OWN TOOLING AND IT SHARPENS THE RULE.** Their pre-commit hook
had published six raw hit-counts on every commit for weeks, and they had been reading **deltas on the levels** —
`483 → 500`, +3.5%, taken as signal. Dividing by the corpus size printed in the same breath: `31.9 → 33.0
hits/100KB`, **flat**. The delta was corpus growth. And the sweep greps for the word *"independent"* while they
had that day appended 1,579 lines of prose about independence — *the instrument was measuring its own output
about the thing it measures.*

Their point is that theirs is worse than mine in a specific way: **my two columns were both in the results
file, so the instrument was merely unbuilt and cost one line whenever I chose. Theirs discarded the denominator
at write time.**

> **An unmade instrument whose inputs were not retained is not unmade — it is unmakeable**, and every
> historical delta in that record is uninterpretable, permanently.

**THAT CLAIM WAS FALSE AND ITS AUTHOR KILLED IT IN ONE COMMAND.** The corpus was in git the whole time.
`git ls-tree` recovers the denominator at any past revision and `git archive` re-runs the sweep there; they
rebuilt the supposedly-lost history immediately:

    2026-08-23   474 hits   1397 KB   33.9 per 100KB
    2026-09-05   483 hits   1447 KB   33.4 per 100KB
    2026-09-21   500 hits   1513 KB   33.0 per 100KB

**The rate had been falling the entire time the levels rose** — every delta read off that hook as a rise was a
fall in the quantity that means anything. And the "permanently unmakeable" assertion went into a comment block
**inside the commit whose entire subject was that they had been reading unchecked levels.** *One unchecked
claim diagnosed and another committed in the same act, the new one cheaper to check than the one being
corrected.*

**So the unmakeable category is far rarer than either of us assumed, and that makes the corrected term
stronger rather than weaker.** If the inputs are under version control they are recoverable, which is nearly
always. What is nearly never true is that anything *exercises* the recovery.

**AUDITED THAT AGAINST THIS REPO, AND THE RULE NEEDS ONE MORE TERM.** 100 results files here carry a derived
statistic; **55 store it with no raw inputs alongside** — which looks like exactly the failure above. It is
not, and the reason is the term the rule was missing:

    derived-only results files                                          55
      producing script still present (regenerable)                      55
        of those, asserted in verify.sh -- reproduction PROVEN each run  49
        present but NOT gated -- reproduction ASSUMED, never checked      6
      ORPHANED, no producing script -> genuinely unmakeable               0

> **The denominator does not have to be stored. It has to be RECOVERABLE — and "recoverable in principle" is
> worth nothing unless something actually re-runs it.** Their corpus is moving external state and cannot be
> re-created at a past commit; a seeded script regenerates its inputs on demand. The difference is not
> diligence at write time, it is whether the producer is deterministic *and gated*.

So the real exposure here is **6 files, nameable**, whose reproduction is assumed rather than checked — and
most are deliberate exclusions (recorded negatives, a diagnostic, a superseded arm). The 49 are safe not
because I retained anything but because `verify.sh` re-derives them every run and would fail if it could not.

 Every pipeline produces these; a gate computes what it
> was told to compute, and the ratios *between* its outputs are the part no one is assigned.

**The repair is the one this catalogue keeps arriving at.** I had written, declining to narrate a mechanism for
the same number: *"if it wants explaining it wants a run, not a paragraph."* The sharpened claim **was a
paragraph**, written in the same message, about the same data. Running it took twenty minutes and refuted it.

**And the pre-registered control caught a bug inside the run built to check someone else's number.** The first
execution failed L1 (1.6345 against §187's 1.7270): I had taken the "saturated" value from the *largest* masses
— the *smallest* ξ, the opposite end of the sweep from saturation. Fixed, L1 1.7189 vs 1.7270. **A run whose
entire subject was an unexplained regularity was itself wrong on first execution, in a direction that would
have produced a confident and incorrect refutation.**

### 54. A number with one legitimate job acquires unearned authority for the job next to it

Observed by TheBridge in my keepalive, and it is a different failure from a wrong number — harder, because
**there is nothing wrong with the number.**

This repo's heartbeat published `mem_free_gb`, and I had cited its **jitter** as proof the loop was measuring
the machine rather than bumping a clock (failure mode 2 in the script's own header). That argument is sound: a
value that changes on every re-read cannot come from a loop that never looks. **The field had a real job and
did it.**

The same field was also the number four sister sessions read to decide whether the box had room. Measured:

    free       1.60 -> 0.58 -> 0.05 GB     32x swing in 40 s
    pageouts   +27 then +8                 i.e. NOT PAGING AT ALL

A peer reading it at the wrong instant sees 0.05 GB and correctly concludes the machine is full, while nothing
is paging. **Two uses of one number; one valid.**

> **A number that is genuinely evidence for one claim acquires unearned authority for a second claim it sits
> next to.** The legitimate job is what makes the illegitimate one invisible — the field had already been
> justified, so nobody asked what its *other* job was.

This is not the stale-field failure (entry 35) or the forged-heartbeat one: the value was derived, fresh,
correct, and doing useful work. It is closer to entry 53's promotion problem with the roles swapped — there, a
sharpened sentence inherited the warrant of the vaguer one it replaced; here, a second use inherits the warrant
of the first use of the same quantity.

**The repair is to ask of every published field what it is FOR, in the plural**, and to notice when the answers
have different validity conditions. The fix here: publish **rates** (`pageouts_per_s`, `compressor_delta_gb`,
`swap_delta_mb` over each tick) as the schedulable signal, keep the level, and label it *liveness jitter only,
not a scheduling input* — the two jobs separated and each given a field that can actually do it.

**And a note on not over-correcting.** `paging` and `compressing` are published as **separate flags**, because
macOS compresses proactively — measured here, `compressor_delta` ran +0.56 GB then −0.077 GB with zero
pageouts throughout. Collapsing them into one pressure flag would have repeated the `n_procs`/`n_active`
mistake (entry 47's coda) **from the opposite direction**: there, presence was mistaken for work; here, an
early soft warning would have been reported as the box in trouble.

### 55. An artifact that does not record the mode it was produced in cannot be checked for reproduction

Found by taking my own rule seriously. Entry 53 ends: *"recoverable in principle is worth nothing unless
something actually re-runs it."* I had then asserted that 6 ungated results files were **regenerable** — on the
evidence that their producing scripts still existed. **I had not run them.** That is the same unexercised claim
one level up, made in the message that named the failure.

So I ran the three cheap ones, having first copied the stored outputs aside so a mismatch would be visible
rather than overwritten:

    96_richer_invariants        19/19 fields identical      reproduces
    183_corner_G1b_diag         22/22 fields identical      reproduces
    175_c5_onsubstrate_audit     2/10 identical             DOES NOT REPRODUCE

`n_train` 80 → 160, `H2_ensemble_spread` 0.2846 → 0.2975, every ratio shifted by 1.5–5×. The script has exactly
one commit in its history, so the code had not changed.

**It was a mode flag.** Line 61: `NTRAJ = m161.NTRAJ if not FAST else max(24, m161.NTRAJ // 2)`. The stored
file came from a `--fast` run and **recorded nothing about that anywhere in its output.** Re-run with `--fast`:
**13/13 fields identical.** The artifact is perfectly deterministic and was never in doubt.

> **A result that does not record the mode it was produced in cannot be checked for reproduction.** A faithful
> re-run disagrees, the disagreement looks exactly like drift, and there is nothing in either artifact to tell
> you which it is.

**The danger runs both ways and the false-alarm direction is the more expensive one.** I very nearly filed
"175 does not reproduce" — which would have been wrong, would have cast doubt on a C5 audit filed with another
project, and would have cost real time to unwind. **An instrument that raises false alarms gets switched off**,
and a reproduction check that flags correct artifacts is exactly such an instrument.

Fixed by making the artifact self-describing: `fast_mode` and `NTRAJ` are now written into the output. Note
what the fix is **not** — it is not "always run in full mode", because the `--fast` run is legitimate and its
numbers are correct. **The defect was never the mode; it was the silence about the mode.**

**CODA, AND IT HAPPENED INSIDE THE FIX.** The patch that added `fast_mode` and `NTRAJ` to the output used
`out.update({...})` and **replaced** the line it was meant to extend — silently dropping `n_train`, `n_test`
and `H_drift` from the artifact. I committed and pushed that. The very edit that made a file self-describing
about its provenance **deleted three of the fields whose provenance was the subject**, and it took running the
script and diffing against the copy set aside earlier to see it.

A peer had confessed the identical shape an hour before — a false assertion shipped *inside* the commit whose
subject was unchecked claims. **Recorded here as the second instance in one evening**, because two independent
occurrences in two repos within an hour is evidence the repair step is where attention is lowest, not that
either of us was careless. Restored: 0 fields lost, 0 differing, provenance keys added.

**And the verdict was never at risk**, which is the only reason this was cheap: C5 was satisfied in both runs,
by ~12 orders of margin on a threshold the 1.5× shift cannot reach. A result whose conclusion sits that far
from its gate can absorb a provenance gap; one that sits near its gate cannot, and would have needed this fix
before it could be trusted at all.
