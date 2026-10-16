# PROMPT 2 — Why MEGNO false-alarms on integrable Kerr orbits near an unstable orbit: a theory note with a predictive test

You are a fresh research session. Your working folder is `/Users/sumit/Github/fable_briefs/tabula/work_2/`. Write
everything there and nowhere else.

## Ground rules (from /Users/sumit/Github/fable_briefs/README_RULES.md; follow them exactly)
1. **Spawn independent agents in parallel** for the separable parts below, plus **one adversarial verifier agent**
   that tries to break the main result. Merge only after the verifier reports.
2. **Read only** the inputs listed here (read-only copies in `/Users/sumit/Github/fable_briefs/tabula/inputs/`) and
   public papers. Do not open, modify or run anything under `/Users/sumit/Github/<any repo>`, and do not touch git.
3. **Write all output** to new files in `work_2/`: a `REPORT.md` with every claim referenced and marked verified /
   partially verified / unverified, plus scripts with pinned versions (pip/venv inside `work_2/` only).
4. Do not post, email, publish, push, or contact anyone. Do not install system software.
5. Do not mention or investigate any vendor/OS security bug; it is out of scope.
6. **Pre-register before computing** (`PREREG.md`: question, method, pass/fail, one known-answer positive control,
   one negative control).
7. Prefer a short correct "no, because…" to a long speculative "yes". Say where you work from memory.

## Background (a claim to be checked)
MEGNO (Cincotta & Simó 2000) has a time-averaged ⟨Y⟩(t): → 2 on quasi-periodic tori, → 0 on stable periodic orbits,
and growing like λt/2 for chaos. A screen used a frozen threshold table (duration-binned, class-wise p99 of ⟨Y⟩
over integrable and torus nulls) and read each orbit at t_dec, the last 25-τ grid time before its end.
- At deep open levels of Kerr geodesics (no equatorial barrier; the plunge/survive transition is set by the unstable
  SPHERICAL orbits), integrable Kerr orbits were flagged CHAOTIC at 14/40, 18/40 and 13/40. **Every one was a
  plunger with lifetime 27–142 τ**, and ⟨Y⟩(t_dec) was about 2.4–3.5 against a 25–100-τ-bin threshold of 2.16.
- A Kerr-control gate then declared "MEGNO cannot discriminate at this window".
- The null table's 25–100-τ integrable-plunger bin was later found EMPTY at the run's accuracy standard.
- A working hypothesis, never tested: these are orbits transiting near a hyperbolic (unstable spherical) orbit,
  where finite-time stretching inflates ⟨Y⟩ in an integrable system.

## Questions (separable agents)
- **Q1, theory.** For an integrable 2-DOF Hamiltonian, derive the finite-time MEGNO ⟨Y⟩(t) for an orbit that
  spends a dwell time T_d within distance δ of a hyperbolic periodic orbit with Lyapunov exponent λ_h (linearised
  saddle passage), then leaves (or plunges). Give ⟨Y⟩(t) as a function of λ_h, T_d and t, and the condition under
  which ⟨Y⟩ exceeds a fixed threshold Y* at a short reading time. Compare with Hartl, Cincotta et al. or later work
  on MEGNO "chaos mimics" or "false positives" near separatrices: search the literature and cite equations.
- **Q2, the Kerr specifics.** For Kerr geodesics near an unstable spherical orbit (Teo 2003, arXiv:gr-qc/0206044;
  Wilkins 1972), give the radial Lyapunov exponent λ_h of the spherical orbit as a function of (a, E, L, Q), and the
  dwell time of a plunger launched at a given distance from the transition. Predict the ⟨Y⟩ range for plungers with
  lifetimes 27–142 τ (M = 1) at the three levels described in the input excerpt.
- **Q3, a predictive numerical test (pre-register first).** In Kerr, at one of the input's levels, generate plungers
  with controlled distance to the transition. Compute ⟨Y⟩(t_dec) and compare with Q1/Q2's prediction.
  - Positive control: an orbit started ON the separatrix's linearised stable direction, whose ⟨Y⟩ growth rate
    should match λ_h.
  - Negative control: generic bound Kerr tori, where ⟨Y⟩ → 2.
  - PASS if the predicted and measured ⟨Y⟩ agree within a stated tolerance, fixed BEFORE running.
- **Q4, the design lesson.** State, as a theorem or a clean conjecture, what any variational chaos indicator
  read at finite time must be calibrated against: a null matched in dwell near hyperbolic structure. Explain why
  non-variational indicators, or a two-window plateau test (λ(T₂)/λ(T₁)), are or are not immune. Be precise about
  what is proved and what is conjectured.
- **ADVERSARIAL VERIFIER:** look for an alternative explanation of the Kerr false alarms: integration error (the
  inputs record an accuracy failure in an earlier run), the empty null bin, the read-time convention, or the
  threshold construction. Rank the explanations by the evidence in the inputs.

## Inputs (read-only, in `/Users/sumit/Github/fable_briefs/tabula/inputs/`)
- `megno_196_plan_excerpt.md`: the screen's pre-registrations, amendments, results, the void run, the re-score and
  an outside audit.
- `megno_196_deep_v2_report.json`: per-level, per-orbit results for the deep levels (Kerr and the comparison
  spacetime), including lifetimes and ⟨Y⟩ at t_dec.
- `megno_196_threshold_table.json`: the frozen thresholds and their null composition.

## Deliverable
`work_2/REPORT.md`, giving:
- (1) the finite-time MEGNO derivation;
- (2) the Kerr λ_h and dwell-time numbers;
- (3) the pre-registered test and its outcome;
- (4) the design lesson, with theorem and conjecture kept separate;
- (5) the verifier's ranking;
- (6) a one-paragraph conclusion: does hyperbolic transit explain the data, yes / no / partially, and how strong is
  the evidence?
