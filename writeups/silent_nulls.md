# Silent nulls: nine ways a bug reads as a result

*A field guide assembled from measured instances, 2026-08-16. Every entry below was found by a controlled
measurement, not by reading code and not by being careful. Four of the nine refuted the claim of whoever ran the
measurement, including several of mine.*

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

Nine mechanisms, and the common thread in how they surfaced:

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
