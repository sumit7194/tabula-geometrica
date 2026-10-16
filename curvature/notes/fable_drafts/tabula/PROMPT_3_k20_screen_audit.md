# PROMPT 3 — An adversarial audit of a chaos-screen design for a computer-assisted horseshoe proof (Manko–Novikov geodesics)

You are a fresh research session acting as an outside referee. Your working folder is
`/Users/sumit/Github/fable_briefs/tabula/work_3/`. Write everything there and nowhere else.

## Ground rules (from /Users/sumit/Github/fable_briefs/README_RULES.md; follow them exactly)
1. **Spawn independent agents in parallel** for the separable parts below, plus **one adversarial verifier agent**
   that attacks the audit's own findings, since a referee can be wrong too. Merge only after the verifier reports.
2. **Read only** the inputs listed here (read-only copies in `/Users/sumit/Github/fable_briefs/tabula/inputs/`) and
   public papers. Do not open, modify or run anything under `/Users/sumit/Github/<any repo>`, and do not touch git.
3. **Write all output** to new files in `work_3/`: a `REPORT.md` with every claim referenced (file + line, or arXiv
   id + section) and marked verified / partially verified / unverified, plus any scripts with pinned versions
   (pip/venv inside `work_3/` only; a C compiler is assumed present).
4. Do not post, email, publish, push, or contact anyone. Do not install system software.
5. Do not mention or investigate any vendor/OS security bug; it is out of scope.
6. **Pre-register before computing** (`PREREG.md`: question, method, pass/fail, one positive control, one negative
   control) if you run anything.
7. Prefer a short correct "no, because…" to a long speculative "yes". Say where you work from memory.

## Context
A screen ("K20") is meant to locate a chaotic sea in Manko–Novikov (MN) geodesic motion, as input for a later
interval-arithmetic horseshoe proof. Its parts:
- a pre-registration plus eleven amendments;
- a C integrator: adaptive Dormand–Prince 5(4), an exact tangent from a sympy Hessian, Hénon section crossings and
  per-step domain checks;
- two chaos indicators combined by an AND rule:
  - **I1:** a two-window FTLE plateau ratio;
  - **I2:** the Grassberger–Procaccia correlation dimension of the orbit's section cloud, over two fixed windows;
- thresholds from a pooled Kerr null, which the inputs argue cannot be proximity-matched, by separability;
- a second integrable null: a separable double well with an exact saddle;
- a domain D (a box-inflated g_φφ > 0 margin, x − 1 ≥ 0.05, R ≥ 0.5);
- a "saddle-in-D" verdict defined in two tiers.
The C-gates are reported as PASSED. Your job is to find what is wrong, weak, or silently vacuous, before the counted
results are trusted.

## Audit questions (separable agents)
- **A1, indicator validity.**
  - I1: is the claimed regular-orbit scaling ρλ = λ(T₂)/λ(T₁) ≈ (ln T₂/ln T₁)(T₁/T₂) right for tangent growth on a
    torus (linear growth)? What does ρλ do on sticky orbits, or on orbits trapped near cantori for long times?
  - I2: with N = 2000 points and windows r ∈ [0.01, 0.05] and [0.02, 0.10] in normalised section units, what are
    the bias and variance of D₂ for a smooth closed curve, for an area-filling ergodic cloud, and for a chaotic layer
    thinner than the window? The inputs already admit one vacuous case (a cloud smaller than the window) and add a
    saturation guard. Find the others.
  - Is the AND rule's false-negative rate on thin chaotic layers acceptable for a horseshoe search? Quantify it if
    you can, with a toy (standard map or Hénon–Heiles) run under pre-registration.
- **A2, the nulls.**
  - Is the separability argument right: no long-lived bound Kerr orbit near a hyperbolic periodic orbit, and every
    orbit above the barrier plunging within about one radial period?
  - Does the pooled class-wise-max threshold make the screen too conservative, or not conservative enough?
  - Does the double-well null test what it claims?
- **A3, numerics.**
  - Check the integrator design in `integ.c`: DP5(4) error control on z only, h_max = 0.5, the Hénon crossing step,
    the tangent not error-controlled, the drift measure.
  - Check the regularisation identity (ρ²B² − 4k²C² = k²AQ) and its use in `mn_codegen_with_regularisation_identity.py`.
  - Are there silent failure paths? Examples: an empty set read as a pass, a guard that checks only one side, a
    comparison made under different settings.
- **A4, the domain and the verdict logic.**
  - Is "tier 2 = a transversal homo/heteroclinic connection inside D within 30 + 30 iterates of manifolds grown from
    ε = 1e-6 segments" a sound proxy for "a horseshoe candidate exists in D"?
  - What does "none found within the search" license, and what does it not?
  - Is anything in the transversality criterion (angle > 1e-3 rad, persisting within 50% between ε = 1e-6 and 1e-7)
    likely to give false positives or false negatives?
- **A5, protocol.** Read the amendment trail as a referee would. Which amendments were made after seeing data, and
  could any of them have been tuned on it? Is the sealing and blind-exchange protocol with the second screen sound?
- **ADVERSARIAL VERIFIER:** for each of the audit's top five findings, try to show it is wrong or harmless, citing
  file + line.

## Inputs (read-only, in `/Users/sumit/Github/fable_briefs/tabula/inputs/`)
- `k20_prereg.md`: the pre-registration (§0–§11).
- `k20_build_log_redacted.md`: amendments A1–A11, gate results, findings, and the corrections made along the way.
- `k20_screen_197.py`: the Python driver (geometry, pilot, UPO search, indicators, thresholds, verdicts, manifolds).
- `integ.c`, `dw_eval.c`, `mn_codegen_with_regularisation_identity.py`: the C kernel, the double-well vector field,
  and the code generator.
- `k20_cgates_results.json`: the C-gate results (already exchanged; not blind).
- `k20_literature.md`: the literature the design rests on.

## Deliverable
`work_3/REPORT.md`, with findings ranked by severity:
- **BLOCKING:** could invert a verdict.
- **MATERIAL:** biases a number.
- **MINOR.**
For each finding give the file:line evidence, a concrete fix, and the verifier's response. End with a list of what
you checked and found SOUND. That list matters as much as the problems.
