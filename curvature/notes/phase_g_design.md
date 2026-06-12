# Phase G/H design — the Generalist and the Geometrization Survey

*The next arc, set by the user's redirect (2026-06-14). For joint review BEFORE
the big build. Plain language on purpose.*

## The two ideas (user's), fused into one program

1. **One net for all worlds (Phase G — "the generalist").** Stop training one
   student per exam. Build a single model that receives a handful of
   observations from SOME world plus a question, figures out which world it is
   in, and answers — across every world family we have (flat, wells,
   anisotropic, charged-E, magnetic-B, and the new ones below). The scientific
   prize is not the accuracy: it is the model's internal "world summary" —
   a space WE did not design. Question: does the net's map of worlds mirror
   physics's map of laws? (Do charged and magnetic worlds sit together? Does
   "how curved" form an axis? Is the world-space itself geometric?)

2. **The geometrization survey (Phase H — "which labels can become lanes").**
   Phase D showed electric charge becomes a position in a hidden lane (and D-3
   the same for magnetic coupling). The survey: hand bodies progressively
   stranger labels — inspired by real particle properties — give the model
   optional extra lanes, and map WHERE geometrization works, how many lanes it
   needs, and where it fails. Anchored in real physics: non-abelian
   Kaluza–Klein and Wong's equations (classical color charge: the label
   ROTATES along the path, only its length is conserved — and that rotation IS
   motion in a curved hidden space).

## Phase G concretely

- **World families (initial 8):** flat 1+1 / flat 3+1 / static well /
  anisotropic 2+1 well / charged-E mix / magnetic-B mix / two-charge mix /
  color-charge (Wong) mix. Each family parameterized (well depths, field
  strengths, charge assignments) — thousands of distinct worlds.
- **Tasks (shared format):** context = K observations from the world
  (same-event pairs and/or trajectory snippets); query = predict a trajectory
  / answer same-event / forecast a clock comparison. One model, all tasks.
- **Model shape:** a set/sequence encoder over context (transformer-style —
  the in-context lesson from steps 12–12d says mean-pooling is too weak;
  attention is justified now) → world-summary vector w (the object of study)
  → task head conditioned on w. Size: first real use of the L4.
- **Gates (drafts, to refine together):**
  - G-1 competence: per-family performance within 1.5× of the per-family
    specialist models (our existing nets = the baselines, already built!).
  - G-2 zero-shot worlds: unseen parameter values (deeper wells, new field
    shapes) — graceful, not cliff-edge.
  - G-3 THE PRIZE — world-space structure: probe the summary space.
    Pre-registered questions: (a) do families cluster? (b) do physical
    parameters (depth, charge scale) form smooth directions? (c) does the
    E-world/B-world pair sit closer than either sits to gravity-worlds
    (electromagnetic kinship)? (d) dimensionality of the summary manifold vs
    the true parameter count of each family. Honest note: (c)-style findings
    are suggestive, not proofs — frame as exploration with controls (e.g.,
    distance comparisons against shuffled-label nulls).
- **Compute:** L4 (arrives ~1–2 days). Mac/MPS for the data generators and
  small ablations meanwhile.

## Phase H concretely (after G is reviewed/trained)

The survey table — each row a world family fed to the generalist WITH optional
internal lanes (D-v1-style state extension, the machinery that already worked):

| Label given to bodies | Physics expectation | What we measure |
|---|---|---|
| electric charge | 1 lane (done — control row) | re-verify in the generalist |
| magnetic coupling | same lane (done — control) | ditto |
| TWO independent charges | 2 lanes | does lane-count emerge = 2? (behavioral counting!) |
| color charge (Wong) | ≥2 lanes + label ROTATION, length conserved | the crown: does the net discover the rotation? the conservation of length? |
| friction/drag | should FAIL (dissipative — geometry conserves energy) | the boundary: lanes refuse the label |
| equivalence-breaking gravity (per-body G) | open | does it geometrize as a second gravity lane or stay a label? |

Gates per row mirror D-v1's (fit · behavioral decode of lane-state vs true
label · conservation/structure of the lane · zero-shot new bodies), plus the
new lane-COUNT question (sweep lanes offered, find the knee — now behavioral,
which dodges the step-12 readout wall).

## What this arc is honest about

- In our toys the net can only rediscover rules we wrote — EXCEPT in two
  places where we genuinely don't know the answer: the structure of the
  generalist's world-space (G-3), and a few survey rows (equivalence-breaking;
  whether lane-count emerges cleanly). Those are the experiments.
- True quantum behavior (superposition/entanglement/measurement) is out of
  scope; "color" here is the honest CLASSICAL limit (Wong 1970), exactly as
  physics defines it.
- Phase F's lesson carries: measure floors first, one knob at a time, ≥3 seeds
  for headlines, behavioral probes over structural ones.

## Open design questions for the joint review

1. Context format: same-event pairs, trajectory snippets, or both mixed?
2. Should the generalist also see the matter distribution (Phase-F-style maps)
   or only motion? (Motion-only is cleaner; maps reopen the locality problem.)
3. How big before world-space structure is even visible? (Plan: smallest
   generalist on Mac first as a pilot — 3 families — before the L4 run.)
4. Which G-3 probes are pre-registered vs exploratory? (Exploration is fine if
   labeled as such; gates only on the pre-registered subset.)

## DESIGN DECISIONS (user review, 2026-06-14) — MAXIMALIST

- Q1 context format: ALL of them mixed — same-event pairs AND trajectory
  snippets AND matter-blob tokens, in one shared token format. The model must
  infer the world from whatever evidence style it gets.
- Q2: matter worlds included; blobs enter as TOKENS (position+mass), not
  grids — sidesteps the Phase-F CNN locality trap entirely.
- Q3: NO design-down for the Mac. Full-fledged build now, run on Mac; if it
  doesn't fit, user shifts Ludo local and frees the L4.
- Families v1 (8): flat 1+1 · flat 3+1 · static well · anisotropic 2+1 well ·
  charged-E · magnetic-B · two-charge · matter-blob worlds. Color/Wong world
  joins as family 9 after survey row 2 validates its generator.
- Per-body labels are IN-CONTEXT: trajectory tokens carry body tags; the
  model must infer each body's hidden labels from its other snippets — the
  Kaluza move, amortized.
