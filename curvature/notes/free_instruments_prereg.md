# PRE-REGISTRATION — the systematic hunt for unmade free instruments

**Frozen before the scanner exists.** Entry 53 ended with a rule I have not yet applied to myself:

> **A quantity that exists as two columns in your own output is the cheapest instrument you will ever have, and
> it stays unmade because making it is nobody's job.**

It fired twice in one run of §187 — a peer divided `ξ_derived/ξ_measured` and found a diagnostic; I divided
`ξ_cross/W` and destroyed that diagnostic's interpretation. Both were one line, both on numbers already sitting
in the results file, and **neither was made until someone went looking for something else.** I said at the time
I would look at the rest of the repo with that in mind. This is that, done as a measurement rather than a
browse.

## The danger, and why this is pre-registered

**This hunt can trivially become fishing.** 255 results files × dozens of numeric fields each gives an enormous
number of computable ratios, almost all meaningless, and a hunt with no stated target will always "find
something." Searching for surprising ratios and then explaining the surprising ones is exactly the
`silent_nulls` failure this catalogue exists to prevent.

## What I am scanning for — narrow and stated in advance

**Only pairs of fields in the SAME file whose KEY NAMES differ by a single qualifier from a fixed, frozen
list**, because those are the cases where the author already believed the two numbers were comparable:

    measured / derived / true / predicted / analytic / textbook / fit
    control / baseline / random / shuffled / blind
    poly / rational / transcendental
    train / test / heldout
    before / after
    crit / critical / gapped

A pair qualifies only if: both values are finite numbers, both non-zero, and the key names are identical apart
from one qualifier token. **No free-form pairing. No searching over all field combinations.**

## What counts as a FINDING, decided now

A pair is worth a human look **only if** the ratio is far from 1 AND the file's own verdict does not already
quote it. Specifically: `ratio > 3` or `ratio < 1/3`, and the ratio value does not appear anywhere in the
file's verdict/conclusion strings.

**Everything else is reported as a count, not a list.** I am not going to browse near-unity ratios looking for
meaning.

## What I will NOT do

- **Not explain any hit tonight.** A hit is a flag for a look, not a result. Explaining a surprising ratio the
  moment it appears is how a fishing expedition becomes a finding.
- **Not modify any result.** This is read-only over `curvature/results/`.
- **Not treat a null as a disappointment.** If the scan returns nothing above threshold, that is the honest
  outcome and means the repo's derived quantities were already computed where they mattered.

## Expected outcome, stated so it can be wrong

I expect **few or no** real hits: most gate files store a statistic and its threshold, not two estimates of one
quantity. §187 was unusual in carrying two independent estimates of ξ. If the scan returns many hits, the more
likely explanation is that my qualifier list is matching unrelated fields, and I should check that before
believing any of them.

---

# RESULT (appended 2026-09-22; nothing above this line edited)

    files scanned                         240
    files containing a qualified pair      22
    qualified pairs examined               61
    hits (|ratio| > 3 or < 1/3)            20

    of those:   2  false-pair (qualifier matched across incompatible metrics)
                2  already-made (the ratio is stored as its OWN FIELD elsewhere in the file)
               16  unmade-or-asserted-as-a-gate

**The pre-registration's stated expectation was "few or no real hits". That was too optimistic, but not in the
direction it looks.** The honest number is not 16 missed instruments — it is 16 **flags**, and the scan cannot
tell two very different things apart.

## The scope limit, which is tonight's actual result

**The scan cannot distinguish *"nobody noticed"* from *"asserted as a gate rather than stored as a ratio"*.**
§65's steer-vs-control (78×) and §18's kaluza-vs-control are the **entire point** of those gates; they are
asserted as thresholds — *a beats b by X* — with the quotient never written to the results file. **That is not
a missed instrument.** Separating the two classes requires parsing the gate *assertions*, not the results
files, and that is a further build, not a conclusion available tonight.

So the scan, as built, measures *"pairs whose ratio is not stored"*, which is a weaker thing than the one I
set out to find. Recording that rather than presenting 16 flags as 16 findings.

## Two defects the scan found in ITSELF, on first contact with the repo

Both recorded, neither quietly patched:

1. **The qualifier match pairs incompatible metrics.** `X_heldout` against `X_R2` is an *error* against a
   *goodness-of-fit* — not two estimates of one quantity. Two of the twenty hits are this, from §97.
2. **The suppression check read only the file's PROSE**, so it missed ratios already stored as their own
   field. §178 keeps `control_improves_more_by = 41464.8`; §41 keeps `slope_ratio_gap_over_crit`. **An
   instrument already made under another name is still made** — and my first classification pass reported
   *zero* already-quoted, which was the tell that the check was looking in the wrong place.

Defect 2 is the more interesting one: the scan hunting for unmade instruments **failed to see instruments that
had been made**, because it looked for them in the narrative rather than in the data. That is the same error
it was built to find, committed by the finder, on its first run.

## Per the pre-registration: no hit is explained here

A hit is a flag for a look, not a result. Explaining a surprising ratio the moment it appears is how a fishing
expedition becomes a finding, and the 16 will keep until there is a reason to open one.
