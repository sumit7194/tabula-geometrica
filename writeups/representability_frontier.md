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

## Honest scope and open threads

- The diagnostic proves the table on *controlled menus* where each regime is dialed in. It is a **classifier of known
  regimes**, not yet a detector that discovers which regime a fully-unknown system is in without being told the data
  type — routing-by-data-type is a real limitation. Closing that (a single instrument that *infers* the data type and
  the regime together) is the next swing.
- CERTIFY-NO-CODE is shown here in its distance-geometry form (no low-D embedding); CHAOS-proper (Lorenz held-out drift)
  is the same verdict via the trajectory engine — unifying both routes into the one instrument is open.
- The five cells may not be exhaustive. The honest claim is: *every wall the project has hit so far is one of these
  five.* Finding a sixth would be a genuine result.

The instrument: [143](../curvature/scripts/143_unified_diagnostic.py). The sub-verdicts, each gated:
[141](../curvature/scripts/141_discoverability_trichotomy.py) (trichotomy),
[142](../curvature/scripts/142_contextual_certificate.py) (contextual),
[139](../curvature/scripts/139_sae_legibility.py) (legibility). Framework + roadmap:
[representability_frontier.md](../curvature/notes/representability_frontier.md).
