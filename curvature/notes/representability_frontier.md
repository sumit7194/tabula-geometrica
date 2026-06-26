# ② The Representability Frontier — a theory of the discoverable

**Started 2026-06-27** (after the SAE-legibility bridge ①). The big-swing arc: unify the project's scattered
LIMITS-of-discovery into ONE coherent account of *what a net can / cannot extract from observation, and why* — and make
that account a **predictive diagnostic**. Executable cold (this doc + the cited scripts).

## The thesis (one sentence)

Every "discovery" the project has done is a search for the **cheapest legible code** for the observations; every WALL
it has hit is a distinct *way that cheapest legible code fails to exist or fails to be unique*. The frontier is the
boundary of that search, and it has a small number of named failure modes.

## The taxonomy (the regimes a discovery-net lands in)

| verdict | what it means | the instrument (existing) | example scripts |
|---|---|---|---|
| **EMIT** | a UNIQUE cheap conserved code exists → the net extracts the law | emit-or-certify engine (generalized-eigenproblem invariant finder), held-out exact | 91–97, 127 (Kepler E/L, Kerr Carter, LRL) |
| **CERTIFY-CHAOS** | NO cheap invariant exists → the net provably can't find one | same engine: held-out var-ratio stays high; no low-degree polynomial invariant | 85, 93–95, 132 (Lorenz, chaotic quartic, ZV δ=2) |
| **CERTIFY-GAUGE** | a cheap code exists but only UP TO a gauge (frame / relabeling redundancy) → recovered law is non-unique | relational-vs-anchored: shape recovers, the absolute frame does not | 86, 111 (dS anchor), 101 (time gauge) |
| **CERTIFY-CONTEXTUAL** | NO consistent GLOBAL code → local descriptions can't be glued | a classical-bound test: the cheapest local-code score exceeds the bound | 84 (Bell, 1/√2), 87 (KCBS, 2/√5) |
| **PARTIAL-LEGIBLE** | the code EXISTS and is used, but is not LINEARLY legible (stored nonlinearly) | the legibility law: linear vs nonlinear decode gap; amortize→legible | 29, 106/135 (Wong dynamic ceiling), 139/140 |

**The unifying lens:** EMIT = the cheapest code is unique + legible. The four CERTIFY/PARTIAL rows are the four ways
that breaks: it doesn't exist (chaos), it isn't unique (gauge), it isn't globally consistent (contextual), or it isn't
linear (partial-legible). The frontier IS this 5-cell classification.

## The deliverable: a DISCOVERABILITY DIAGNOSTIC

One instrument that, given a system's observations, runs the appropriate sub-tests and returns the verdict + the
evidence (the conserved code if EMIT; the certificate if CERTIFY). The emit-or-certify engine (93/127) is the seed; the
arc extends it to the other failure modes and proves the whole table on a controlled MENU where each regime is dialed in
on demand.

## Experiment roadmap

- **EXP-1 (DONE 2026-06-27, script 141, 4/4): the discoverability trichotomy — EMIT / CERTIFY-GAUGE / CERTIFY-NO-CODE.**
  Built on the cleanest common substrate: PAIRWISE DISTANCES of a point configuration (reuses dS-anchor 111's
  reconstruct/errors/pdist). One diagnostic reads the residual 2D STRESS (does a cheap low-D code exist?) then the RAW
  frame error (unique, or a gauge?) and emits the verdict. EMIT = 2D config + anchor (stress 0, raw 0, unique);
  CERTIFY-GAUGE = same config relational (stress 0, shape aligned, raw 1.42 = frame is a gauge); CERTIFY-NO-CODE = a 6D
  config that does not embed in 2D (stress 1.29 = no cheap low-D code, the geometric analog of "no conserved invariant"
  / chaos). So beyond integrable-vs-chaotic, one instrument names the GAUGE failure. (The trajectory/emit-or-certify
  version of CHAOS proper — Lorenz held-out drift — folds into the same diagnostic in the synthesis; NO-CODE is its
  distance-geometry analog here.)
- **EXP-2: add CERTIFY-CONTEXTUAL.** Fold the Bell/KCBS classical-bound test (84/87) into the diagnostic (different
  observation structure: correlation tables, not trajectories) — the instrument routes by data type.
- **EXP-3: add PARTIAL-LEGIBLE + synthesize.** The legibility-law linear-vs-nonlinear gap (139) as the 5th verdict;
  then a `writeups/representability_frontier.md` that states the full table as one result.

## EXP-1 result (script 141, distance-geometry realization)

A distance-geometry menu, one diagnostic (read STRESS, then RAW frame error), correct verdict on each (all PASSED):
- F1 EMIT (2D config, anchored): low 2D stress (a cheap code exists, 0.000) AND low raw error (the frame is UNIQUE,
  0.000) → verdict EMIT.
- F2 CERTIFY-GAUGE (2D config, relational/no-anchor): low stress + low ALIGNED shape error (0.000) BUT high RAW frame
  error (1.42) → the absolute frame is a gauge → verdict CERTIFY-GAUGE.
- F3 CERTIFY-NO-CODE (6D config): HIGH 2D stress (1.29) — distances don't embed in 2D → verdict CERTIFY-NO-CODE (the
  geometric analog of "no conserved invariant" / chaos).
- F4 ONE DIAGNOSTIC, ALL THREE: the single verdict function classifies all three correctly.

**Honest scope (stated up front):** EXP-1 is the distance-geometry subset (NO-CODE stands in for trajectory CHAOS here);
the CONTEXTUAL (Bell/KCBS) + PARTIAL-LEGIBLE (legibility law) rows are EXP-2/3, and the trajectory emit-or-certify engine
(Lorenz drift = CHAOS proper) folds in at the synthesis. The point: ONE diagnostic already names three discovery
failure modes, not just integrable-vs-chaotic — the seed of the full frontier table.
