# The Representability Frontier — a theory of the discoverable

*A synthesis writeup (2026-06-27). The shareable version of the second big arc (②): pulling the project's scattered
limits-of-discovery into one picture, and making that picture an instrument.*

## The question

This whole project asks one thing: **can a neural network discover the structure of the world just by watching it?** Not
told the law — given only adjacent observations, and asked to find the cheapest description that fits. Across forty-odd
experiments it has watched nets *succeed* (rediscover the spacetime interval, Kepler's hidden invariants, a black hole's
curvature, geometry from entanglement) and watched them *fail* — hit walls they provably cannot cross (Bell
nonlocality, chaos, gauge freedom, the spinor's double cover).

The natural next question: **are those walls random, or is there a structure to them?** This writeup says there is — a
small, finite structure — and turns it into a single diagnostic that, handed a system, tells you in advance which side
of the frontier you're on.

## The one idea

Every discovery the project has done is the same move under the hood: **find the cheapest *legible* code for the
observations.** "Cheapest" because a shorter description that still predicts is a better theory (Occam, MDL). "Legible"
because a code you can *read* — linearly decode the meaningful quantity out of — is the one that counts as understanding,
not just compression.

So every *wall* is a way that single thing can fail. And it turns out there are exactly **four ways it fails**, plus the
success case — a five-cell table:

| verdict | the cheapest legible code… | plain-language | example |
|---|---|---|---|
| **EMIT** | …exists, is unique, and is legible | "the net just learns the law" | the interval, Kepler E/L, Carter constant |
| **CERTIFY-NO-CODE** *(chaos)* | …does not exist | "there is no short description" | Lorenz; a high-dimensional cloud |
| **CERTIFY-GAUGE** | …exists but is not unique | "the law is fixed only up to a frame you can't observe" | relational positions (no anchor); time itself |
| **CERTIFY-CONTEXTUAL** | …exists locally but won't glue into one global code | "every local story is fine; no single global story is" | Bell singlet (CHSH > 2) |
| **PARTIAL-LEGIBLE** | …exists and is used, but is not *linear* | "the info is in there, just not readable off cleanly" | a free-stored charge (the legibility law) |

**EMIT is when the code is all four at once** — it exists, it's unique, it's global, and it's linear. The four failure
rows are the four ways one of those breaks. That's the whole frontier.

## The instrument: one diagnostic, five verdicts

The payoff is that this isn't just a classification on paper — it's **runnable**. A single diagnostic routes by the
*type* of data it's handed and returns the verdict plus its evidence ([script 143](../curvature/scripts/143_unified_diagnostic.py)):

- **Distances** (a table of pairwise distances) → reconstruct the geometry, read the **residual stress** (does a cheap
  low-dimensional code exist at all?) and then the **frame error** (is it unique, or only fixed up to a gauge?). →
  EMIT / CERTIFY-GAUGE / CERTIFY-NO-CODE.
- **Correlations** (a measurement table) → fit the cheapest **local hidden-variable code** (the local polytope) and read
  the **CHSH value** (Bell's theorem: > 2 *proves* no global classical code exists). → EMIT-CLASSICAL / CERTIFY-CONTEXTUAL.
- **Code** (learned representations + a property) → measure **linear vs nonlinear decodability** of the property. → EMIT-
  LEGIBLE / PARTIAL-LEGIBLE.

Run on a controlled menu where each regime is dialed in on purpose, the single instrument calls **all seven cases
correctly** — the complete table, one diagnostic:

```
EMIT                 stress 2e-7, raw 5e-8       (2D config + anchor: unique cheap code)
CERTIFY-GAUGE        stress 2e-7, raw 1.46       (same config, relational: frame is a gauge)
CERTIFY-NO-CODE      stress 0.47                 (6D config: no cheap 2D code)
EMIT-CLASSICAL       residual 0.005, CHSH 0.64   (local table: a global code fits)
CERTIFY-CONTEXTUAL   residual 0.83, CHSH 2.83    (Bell singlet: no global code, Bell's theorem)
EMIT-LEGIBLE         linear 0.99                 (amortized code: linearly readable)
PARTIAL-LEGIBLE      linear 0.45, nonlinear 0.75 (free code: info present, not linear)
```

## The five verdicts, with their evidence

**EMIT — the law is discoverable.** The project's positive results all live here: the emit-or-certify engine extracts a
held-out-exact conserved invariant ([91–97](../curvature/scripts/), [127](../curvature/scripts/127_integrability_legibility.py)),
the interval emerges from boosted observations (Phase A), curvature from trajectories (Phase E). The cheapest code
exists, is unique, global, and linear.

**CERTIFY-NO-CODE / chaos — there is no short description.** A chaotic system has no low-degree conserved invariant; the
engine searches and comes up empty, and that *emptiness is the result* ([85](../curvature/scripts/85_chaos_certificate.py),
[93–95](../curvature/scripts/)). In the geometry version, a high-dimensional point cloud simply does not embed in a
cheap low-dimensional space — the residual stress stays high. "No cheap code" is a *positive* statement once you've
proven the search was thorough.

**CERTIFY-GAUGE — the law is fixed only up to something you can't see.** Watch points by their relative distances alone
and you recover their *shape* perfectly but never their absolute position and orientation — that frame is a gauge, and
re-running lands it somewhere different every time ([111, the dS anchor](../curvature/scripts/111_desitter_anchor.py)).
The same wall, wearing different masks, is the deepest recurring villain in the project: *no observer-independent time*
([Certificate V, 101](../curvature/scripts/101_time_gauge_certificate.py)), *no observer-independent frame*, gauge
field theory ([86](../curvature/scripts/)). An *anchor* collapses gauge back to EMIT — which is exactly the AdS-boundary
story.

**CERTIFY-CONTEXTUAL — every local story works; no global one does.** The Bell singlet's correlations can be reproduced
by a local hidden-variable model *for any pair of settings* — but no single such model covers all of them at once, and
Bell's theorem (CHSH > 2) *proves* it ([84](../curvature/scripts/), [142](../curvature/scripts/142_contextual_certificate.py)).
The diagnostic even **locates the wall**: tune quantum noise down and the verdict flips back to EMIT-CLASSICAL exactly at
the classical/quantum boundary (visibility 1/√2, where CHSH crosses 2).

**PARTIAL-LEGIBLE — the info is there, just not readable.** This is the **legibility law**, the project's other crown
jewel ([29](../curvature/scripts/), [139](../curvature/scripts/139_sae_legibility.py)). A property that a shared encoder
*infers* (amortized) comes out linearly legible for free; the *same* property stored as a free per-item parameter gets
scrambled — present and used (nonlinear decode 0.75) but not linearly readable (0.45). The code exists and works; it
just isn't legible. This is the verdict that connects the frontier to interpretability: a model can *know* something it
can't cleanly *tell* you.

## Why this matters

Three things fall out of having the table:

1. **The walls were never random.** Bell, chaos, gauge, the legibility ceiling, the no-fixed-reference results, the
   spinor double cover — they looked like a grab-bag of unrelated negative results. They're four faces of one object.
2. **It's predictive, not just descriptive.** Handed a new system, you can *run the diagnostic* and get a verdict before
   investing in a big model — and when the verdict is a CERTIFY, you've learned something true about the world, not just
   failed to fit it.
3. **The negatives are the result.** A discovery project's instinct is to chase EMIT everywhere. The frontier says the
   CERTIFY cells are where the physics is: "you cannot discover X" is a theorem about the world, gated against a real
   one (Bell, Liouville, the gauge orbit, Roeder identifiability) — an *impossibility certificate*, the project's most
   distinctive kind of finding.

## The detector (the scope gap, closed)

The first version of the instrument had an honest limitation: it had to be *told* each dataset's type. That gap is now
closed ([script 145](../curvature/scripts/145_regime_detector.py)): the **regime detector** takes a raw dataset with
**no type label and no ground truth**, infers the data type from structural signatures alone (a symmetric, hollow matrix
obeying the triangle inequality is distance data; discrete ±1 records are measurements; temporally smooth ensembles are
trajectories; exchangeable tables are codes), and then decides the regime *truth-free* — gauge is certified by exhibiting
two distinct configurations that explain the data equally well (unless anchor coordinates, which are data, break the
tie); contextuality is read from the samples' own CHSH; legibility from decoding the dataset's own target. Ground truth
enters only in the gates. It also folds **chaos-proper** into the router via the trajectory branch: the
Gottwald–Melbourne **0–1 test for chaos** (K→0 regular, K→1 chaotic) plus the invariant engine — Kepler → EMIT (K=−0.06,
a machine-exact conserved invariant at 7e-18) and Lorenz → CERTIFY-CHAOS (K=0.997, no invariant). On a 9-system menu the
detector types and verdicts **all nine correctly**. One instructive gotcha, caught in the smoke test: *oversampled*
chaos reads as regular (Lorenz at the raw sampling rate gives K=−0.04; subsampled, K=1.0) — the detector evaluates K
across subsampling rates and takes the max.

**Knowing when not to answer ([EXP-6, script 147](../curvature/scripts/147_abstain_detector.py)).** A detector that
always emits a verdict is dishonest near a decision boundary or under-sampling. So each branch's decision statistic is
wrapped in a bootstrap confidence interval; when the interval straddles the threshold (or the sample is below a
reliability floor) the detector returns **ABSTAIN** instead of guessing. On well-sampled inputs it stays confident and
correct; on three underdetermined inputs — a near-boundary Werner state at 16 samples, a 6-point distance matrix, a
short chaotic series — it abstains with *zero* wrong verdicts; and as data grows the same input resolves ABSTAIN →
confident verdict. Underdetermination (EXP-5's third axis) becomes an explicit output: "not enough data," and more data
fixes it.

**Two levels of "discoverable" ([EXP-7, script 148](../curvature/scripts/148_law_vs_predictability.py)).** People
conflate two things the frontier keeps separate: the *local rule* (can you predict one step ahead?) and the *trajectory*
(can you compress or shortcut the whole run?). For a smooth integrable system these coincide, so the distinction hides.
Measure them separately and they **dissociate**: Kepler, Lorenz, Rule 30 and Rule 250 all have a perfectly learnable
one-step law (R²/accuracy ≈ 1; only an iid-noise control fails), yet their trajectory predictability splits — Kepler and
Rule 250 are predictable, Lorenz and Rule 30 are not. Lorenz and Rule 30 sit off-diagonal: a trivially learnable rule, an
unpredictable trajectory. So the frontier's discoverability axis is a *trajectory-level* property (invariants,
compression), not the local rule — which is almost always easy.

## Honest scope and open threads

- **Mixed regimes — a real limitation, and its fix ([EXP-8, script 149](../curvature/scripts/149_mixed_regime.py)).**
  The detector assumes one clean regime per dataset; a KAM system (Hénon–Heiles at intermediate energy) has regular and
  chaotic orbits *coexisting*. Cross-validated by the Lyapunov exponent, the per-orbit chaos measure is genuinely
  bimodal at E=1/8 (its two modes coincide with the pure-regular and pure-chaotic ensembles), so a single verdict can't
  represent it — but a **fraction-chaotic readout** does, tracking the chaotic fraction monotonically across energy
  exactly as KAM predicts. The honest fix: report a *distribution*, not a label. (A bonus the test surfaced: the 0–1
  chaos instrument false-positives on quasiperiodic orbits only at *short* integration — an under-sampling artifact that
  EXP-6's abstain mechanism guards against; the Lyapunov exponent is the robust measure for Hamiltonian systems.)
- Still untested: genuinely real-world data (measurement noise, types outside the four structural signatures), and
  wiring the mixture/abstain modes into the detector proper (both EXP-6 and EXP-8 demonstrate the fix; folding them into
  the single instrument is a clean engineering follow-up).

**The detector matured into a robust instrument (EXP-9–11).** Three follow-ups took the detector from a menu classifier
to something that degrades honestly. *EXP-9* ([script 150](../curvature/scripts/150_robust_detector.py)) folds abstain
(EXP-6) and mixture (EXP-8) into **one data-driven instrument**: on a 9-case menu it returns a confident verdict, an
ABSTAIN, or a MIXTURE-with-fraction as appropriate, with zero wrong confident verdicts. *EXP-10*
([script 151](../curvature/scripts/151_noise_robustness.py)) stress-tested it under measurement noise and found the
brittleness lived not in the regime diagnostics but in **type inference** — a noisy distance matrix violates the strict
triangle inequality and gets mistyped; the fix is a noise-tolerant distance signature. With that, chaos detection is
fully noise-robust, and regular-orbit detection degrades gracefully (abstains before it false-positives). *EXP-11*
([script 152](../curvature/scripts/152_predictability_diagnostic.py)) turns the **predictability axis** — the orthogonal
axis EXP-5 discovered — into its own instrument: a four-class diagnostic (RANDOM / PREDICTABLE / CHAOTIC / IRREDUCIBLE)
that classifies systems correctly and confirms the axis is independent of discoverability (all structured systems have a
learnable one-step law, yet span three predictability classes). *EXP-12*
([script 153](../curvature/scripts/153_sample_complexity.py)) instruments the third axis, **sampling**, as a *quantity*
rather than a binary abstain: how many samples does it take to resolve a verdict, as a function of distance to a decision
wall? Near the contextual wall (CHSH = 2) the sample complexity **diverges** — N_resolve grows from 400 to 409,600 as the
margin shrinks from 0.6 to 0.02, a log-log slope of −1.96 ≈ −2 that matches the derivable law N_resolve ~ 1/δ² (a
critical-slowing-down analog). So **all three axes of the frontier are now operationalized as instruments** —
discoverability, predictability, and sampling — and the discoverability detector is uncertainty-, mixture-, and
noise-aware.
- **The exhaustiveness question, answered (EXP-5, script 146).** We threw three adversarial systems that were *not*
  built to fit the table at the detector. The result: no sixth cell — but the table is **one face of a three-axis
  space**. (a) *Partial observability* is absorbed, not a new wall: a single scalar observable still yields the correct
  regular/chaotic verdict (Kepler K=−0.06, Lorenz K=0.998), because Takens' delay embedding reconstructs the attractor
  and the 0–1 test is built for scalar series. (b) *Computational irreducibility* is a genuine misfit on an orthogonal
  **predictability** axis: elementary cellular automata (Rules 30/90/250) all have perfectly discoverable one-step laws
  (they'd all read EMIT), yet their trajectories split on compressibility — Rule 30 is incompressible (Wolfram's RNG),
  Rule 250 compresses. Discoverability ≠ predictability. (A nuance: Rule 90 is *algebraically* reducible, closed-form
  XOR, yet *statistically* incompressible — predictability itself has flavors.) (c) *Finite samples* are an orthogonal
  **underdetermination** axis that bites near a decision wall: a near-boundary Werner state (CHSH 2.07) is decided
  correctly only 65% of the time at N=16 versus 100% at N=200k, while a far-from-wall singlet is robust even at N=16 —
  the detector needs an *abstain* output near boundaries. So the frontier is DISCOVERABILITY (this table) ×
  PREDICTABILITY × SAMPLING; the five cells are exhaustive on the first axis, for well-sampled stationary systems.

The instrument: [143](../curvature/scripts/143_unified_diagnostic.py). The sub-verdicts, each gated:
[141](../curvature/scripts/141_discoverability_trichotomy.py) (trichotomy),
[142](../curvature/scripts/142_contextual_certificate.py) (contextual),
[139](../curvature/scripts/139_sae_legibility.py) (legibility). Framework + roadmap:
[representability_frontier.md](../curvature/notes/representability_frontier.md).
