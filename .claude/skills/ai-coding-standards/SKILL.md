---
name: ai-coding-standards
description: General engineering standards and anti-slop guardrails for AI-assisted coding in ANY language or framework. Use this skill whenever you write, review, refactor, or plan code in this project — features, bug fixes, dependency changes, tests, refactors — even for "quick fixes" and one-line changes. It encodes the working loop (search-before-write, smallest diff, verify-before-done), dependency restraint rules, and countermeasures for documented AI-generated-code failure modes (duplication, hallucinated packages, stale APIs, weakened tests, premature "done" claims). Grounded in 2024–2026 research (GitClear, DORA, METR, USENIX, Veracode).
---

# AI Coding Standards (framework-agnostic)

> Portable skill. To install: copy this folder to `<project>/.claude/skills/ai-coding-standards/` (project-level) or `~/.claude/skills/ai-coding-standards/` (all projects). Then fill in the "Project adaptation" section at the bottom for the specific stack.

## Why this exists — the evidence

Research on AI-generated code shows its failures are **additive**:

- Duplicated code blocks rose **~8× in 2024**; copy/paste exceeded refactoring for the first time on record (GitClear 2025, 211M changed lines).
- Each +25% AI adoption correlated with **−7.2% delivery stability**, driven by larger change batches; gains only materialize with small batches + strong tests (DORA 2024/2025).
- Experienced devs were **19% slower** with AI on real tasks — while believing they were ~20% faster (METR RCT 2025). Perceived speed is not real speed.
- **19.7%** of LLM-recommended packages don't exist; attackers pre-register hallucinated names with malware — "slopsquatting" (USENIX Security 2025).
- **45%** of AI-generated code introduced OWASP-class vulnerabilities; newer models were NOT more secure (Veracode 2025).
- Top developer frustration: "AI solutions that are *almost right, but not quite*" (66%, Stack Overflow 2025).

**The pattern:** AI failure is additive — more code, more duplication, more defensive bloat, bigger diffs, premature "done". Quality engineering is **subtractive and verificatory** — reuse, delete, scope down, prove. When in doubt, make the subtractive move.

## The loop — every task, no exceptions

**Before writing code:**
1. Read the 2–3 nearest existing files. Match their style, naming, and patterns exactly — consistency beats personal preference.
2. Search the codebase for existing helpers/components/modules that already do the job. A near-duplicate of existing code is a defect, not a style issue.
3. If the repo already solves a class of problem (error handling, HTTP client, DI, validation, date formatting), extend that solution. Introducing a parallel mechanism for a solved problem requires explicit human approval first.
4. Verify every API against the **installed** version (lockfile + that package's docs/changelog), not memory — training data is stale.
5. Plan briefly. For multi-file work, state the plan before editing.

**While writing:**
- Smallest diff that completes the task. No drive-by reformatting, renames, or refactors mixed in — propose those separately.
- Comments explain *why* only — never narrate what the next line does. No emoji, no "Step 1/2/3" comments, no banner comments.
- No speculative abstraction: no interface/abstract class with one implementation, no manager/wrapper/config layers "for later". Rule of three before extracting.
- Trust the type system: no redundant null/undefined checks on values the types already guarantee; every try/catch, retry, or timeout must name the failure scenario it handles.

**Before claiming done — the gate:**
1. Run the project's full local gate: formatter + linter/static analysis (zero findings) + test suite. If the project has a verify script, use it.
2. Show the real output. Never state that tests/analysis pass without fresh output from this session. "It should work" is not a status.
3. Self-review the diff hunk by hunk against the checklist below: dead code deleted, old paths removed, unused imports gone, docs updated if behavior or commands changed.
4. If a gate fails: fix it or report the failure honestly. Never weaken, skip, or delete a test to get green — if a test looks wrong, stop and say so.

**When stuck:** after 2 failed fix attempts, stop adding code. Re-read the code, reproduce the failure deliberately, write a one-line root-cause hypothesis, then edit. Layering workarounds (band-aid retries, swallowing errors, widening types, casting away) is forbidden.

## Dependency restraint (a top documented complaint)

Order of preference, strictly: **standard library → framework built-in → an existing dependency in the project → a new dependency**. A new dependency is a last resort with a stated justification, not a convenience.

Before adding ANY package:
1. Does the stdlib/framework or an existing dep already cover this? If yes, stop.
2. Confirm it **exists** on the official registry (npm/PyPI/pub.dev/crates.io/Maven) — query the registry, don't trust memory. ~20% of LLM package suggestions are hallucinated, and those names get weaponized.
3. Vet it: maintained (release within ~12 months), known/verified publisher, healthy adoption (downloads/stars), active issue tracker, compatible license, sane transitive dependency count.
4. Add with a standard version constraint; **commit the lockfile** (for applications). Version pinning lives in the lockfile, not the manifest.
5. One major-version upgrade per PR, with the changelog read and the full test suite run.
6. Dependency overrides/resolutions are temporary: each carries a TODO with an upstream issue link.

Never add a dependency to avoid writing 20 lines of code. Never add two packages that solve the same problem class.

## Failure-mode catalog → rules

1. **"Almost right, but not quite"** → Never trust plausibility. Prove every change with executed checks plus a deliberate trace of edge cases: empty, null/missing, error path, concurrent/duplicate call.
2. **Duplication instead of reuse** → Search before writing (by concept, not just exact name). Extending the existing helper is the default; near-duplicates block review.
3. **Ignoring conventions / second pattern for a solved problem** → Copy the style of neighboring files; one pattern per problem class (one error model, one HTTP client, one DI style, one state approach).
4. **False "done" claims** → No completion claim without fresh verification output shown in the same message.
5. **Weak or gamed tests** → Tests are a contract: never delete/skip/weaken an assertion to pass; never special-case test inputs in production code; assert behavior (outputs, state transitions), not internals.
6. **Swallowed exceptions / silent fallbacks** → No empty catch; no catch-log-return-null; no broad catch without a typed clause outside top-level handlers. Handle with a real recovery strategy or rethrow. Errors must surface.
7. **Doom loops — fixing by adding** → The 2-strikes rule above. Root cause before the third edit.
8. **Over-engineering** → Solve today's problem in the fewest concepts. No config layers, plugin systems, or generic frameworks for one caller.
9. **Hallucinated packages/APIs** → Registry check before adding; signature check against installed version before calling.
10. **Stale-training-data APIs** → Treat memorized API knowledge as suspect; check current docs for anything deprecated-prone; keep the linter/compiler strict so it catches what review misses.
11. **Huge unfocused diffs** → Touch only task-required files; keep changes reviewable (aim under ~300 changed lines per PR). DORA links big batches directly to instability.
12. **Narration comments** → Comments state constraints and *why*. Delete any comment restating the line below it.
13. **Dead code and leftovers** → Replacing logic means deleting the old path, its imports, and helpers in the same change. Commented-out code is never committed. Deleting code is progress.
14. **Defensive bloat** → See "trust the type system" above. Cargo-cult retries/timeouts without a named failure scenario get removed.
15. **Stale docs** → Any change altering behavior, commands, or setup updates the corresponding doc (README/CHANGELOG/comments) in the same diff — or states explicitly that none exists.

## Self-review checklist (run before every "done")

- [ ] Full gate run (format + lint/analyze + tests); real output shown; green
- [ ] No near-duplicate of an existing helper introduced
- [ ] Old code paths, unused imports, orphaned helpers deleted; no commented-out code
- [ ] Diff contains only task-related changes
- [ ] Every catch handles specifically or rethrows; nothing silently swallowed
- [ ] New dependencies registry-verified and vetted; APIs checked against installed versions
- [ ] Comments are why-only; zero narration
- [ ] Tests assert behavior; none weakened, skipped, or deleted
- [ ] Edge cases traced: empty, null, error path, concurrent/duplicate
- [ ] Docs/CHANGELOG updated if behavior, commands, or setup changed

## Project bookkeeping (generic)

- **Small scoped tasks**: well-defined tasks with clear acceptance criteria produce dramatically less slop than "build the whole thing" prompts. Decompose before generating.
- **Lockfiles committed** for applications; dependency audit (outdated check) monthly; routine upgrades in their own PR.
- **CHANGELOG.md** (Keep-a-Changelog): user-visible changes add a line under `[Unreleased]` in the same PR.
- **ADRs** (`docs/adr/NNNN-title.md`, Status/Context/Decision/Consequences): significant decisions are written down; accepted ADRs are superseded, never silently contradicted. Check `docs/adr/` before proposing architectural changes.
- **CI as the backstop**: the same gate (format check, lint with zero findings, tests, coverage floor that ratchets up) runs on every PR. A bug fix without a regression test isn't done.
- **README honesty**: setup commands in the README must actually work; they're part of the same-diff doc rule.

## Project adaptation — SpaceTime repo (curvature / NN)

This repo is the **curvature** project: can a neural network discover spacetime
geometry from raw observations? Prose/concept docs at the root, the live build in
`curvature/`. (The LIGO-data black-hole projects moved to the sibling `../BlackHole/`
repo on 2026-06-13 — their lessons are still cited below as precedent.)

- **Stack**: Python **3.12.13** in `curvature/.venv` (brew Python, never the system
  one). Pinned: **torch 2.12.0, numpy 2.4.6, scikit-learn 1.9.0, matplotlib 3.10.9,
  scipy 1.17.1** (see `curvature/requirements.txt`). MPS-capable Mac.
- **One pattern per problem** (copy the neighbors, don't invent):
  - Layout: `curvature/scripts/` (numbered steps `NN_name.py` + the one shared
    `curvlib.py`), `curvature/results/` (plots + saved arrays + heartbeats),
    `curvature/notes/lab_notebook.md` (pre-registrations, results, gotchas).
  - Scripts: standalone, runnable as `.venv/bin/python scripts/NN_name.py`, module
    docstring stating purpose, `matplotlib.use("Agg")`, save plots to `results/`
    and print the path. Shared logic lives in `curvlib.py`, never duplicated.
  - Long runs: launch **detached** (`nohup … & disown`) — session restarts kill
    harness-child tasks; monitor via `curvlib.progress()` heartbeats + the
    dashboard. Use `curvlib.save_ckpt`/`load_ckpt` for bit-exact resumable state.
  - Reproducibility: seed BEFORE model construction (torch inits are unseeded
    otherwise); validate physics claims against a closed-form answer before use.
- **The verify gate**: `./verify.sh` at the repo root re-runs every curvature probe
  against the saved models and asserts the pre-registered thresholds (+ the 17/18
  invariant/magnetic artifacts). Run it after any curvature change; a result isn't
  real until the gate is green. Show fresh output; record results in the lab notebook
  in the same change.
- **ADR equivalent**: design decisions go in `curvature/README.md` ("Decisions") or
  `notes/lab_notebook.md` with date + why. The CHANGELOG role is served by root
  `JOURNAL.md` (append one entry per session). Root `CLAUDE.md` carries the compact
  status block — update it when a milestone lands.
- **Deprecation / hardware traps seen in this repo**: MPS lacks
  `grid_sampler_2d_backward` (pytorch#141287) → use the hand-rolled `curvlib.bilerp`
  (verified exact, 12.4× speedup); construct models on CPU then `.to(device)` so
  seeds reproduce; after `load_ckpt`, move Adam state tensors to the device
  explicitly; the CPU path is kept byte-identical for resume continuity.
- **Dependency restraint here**: numpy / scipy / matplotlib / torch / scikit-learn
  are the approved set. Anything beyond needs a stated justification in the lab
  notebook.

### ML experiment methodology (adopted 2026-06-13 after the Phase F audit)

Our science hygiene (pre-register → control → gate → report nulls honestly) is
strong; our ML-craft was folklore (defaults + round numbers), and Phase F — the
first phase with a *hard quantitative* gate — is where that gap showed (3/4 gates
missed against guessed thresholds). The throughline of every careful phase we DID
get right: **measure the achievable floor first, then gate relative to it** (echoes
sensitivity-via-injections; ringdown calibration at matched loudness; Phase A oracle
0.99 before training). Make that the rule, not the exception:

1. **Oracle floor before any quantitative gate.** Run the *true* system through the
   same discretization/interpolation/rollout and measure ITS error. Gate as "within
   k× of oracle," never an absolute number pulled from intuition. (Phase F's
   `MSE ≤ 1e-3` was never checked against the grid+`grid_sample` floor — possibly
   unpassable by construction. A few minutes would have caught it.)
2. **Diagnostic trio on a failed gate, BEFORE any fix round** (~1 h): (a) overfit a
   single batch → tests expressivity/capacity; (b) 2× model, same data → capacity-
   bound?; (c) same model, 2× data → data-bound? This says *which* knob failed
   instead of guessing architecture.
3. **LR is not a default.** 3-point sweep (3e-4 / 1e-3 / 3e-3, ~500 steps each) +
   cosine decay per phase. Removes the "was it the optimizer?" ambiguity that left
   Phase F's plateau uninterpretable. (Adam-1e-3 survived everywhere only because
   earlier gates were qualitative — cos≈1.0, tuning-insensitive.)
4. **Convergence-based length, not round numbers.** Stop on val-loss plateau; add a
   feasibility check at ~25% of budget to abort doomed runs early (Phase F's miss
   was visible at step ~6000 of 12000). When changing batch size, hold
   *samples-seen* roughly fixed — cutting steps 12000→8000 *and* batch 192→48 means
   6× fewer samples, the opposite of the stated "more updates" rationale.
5. **≥3 seeds for any headline number** (we learned this in MDL #13, then didn't
   generalize). Single-seed = anecdote.
6. **Receptive-field / capacity arithmetic before choosing an architecture.** Phase
   F's local CNN (4×5² convs ≈ 17px) vs a long-range 1/r law on a 48px grid was a
   pen-and-paper mismatch, recorded as "suspect" but never computed up front.

Not relevant to us (asked, answered): **KL-anchor / KL-penalty** is an
RLHF/fine-tuning device (keep a policy near a reference model) — nothing here
fine-tunes against a reference. Our only legitimate tuned knob to date is ringdown's
post-hoc temperature T=1.05 (fitted on held-out sims, coverage-checked) — the model
to copy when a knob genuinely needs setting.
