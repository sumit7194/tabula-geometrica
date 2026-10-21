# §198 — Tomimatsu–Sato δ=2 thin-chaotic-layer scan (pre-registration, 2026-10-21)

Written and committed BEFORE the scan code (`scripts/198_ts_layer_scan.py`) exists. It is meant to run unattended
while the user travels, and it launches only on the user's go. The request came from The Bridge's brief
(.claude-coordination/inbox/tabula/2026-10-21_bridge_unattended_ts_layer_scan.md); the user confirmed in chat:
prepare, do not start.

## Question
Is there a thin chaotic layer in TS δ=2 bound timelike geodesics? A positive answer would reconcile Dubeibe,
Pachón & Sanabria-Gómez 2007 (gr-qc/0701065), who saw only regular sections and call TS "completely integrable",
with the fleet's non-integrability results: quantum's Morales–Ramis obstruction plus certified monodromy, and the
invariant-KT bound up to valence 10. A layer that exists can still be too thin to see. A null here is therefore a
statement about resolution, never about integrability.

## Prior work this builds on (not re-done)
- §196 TS near-separatrix run: 0/360 CHAOTIC at ε = −0.01…−0.05 (OPEN levels: the orbits plunge), T = 3e4.
- §196 deep levels: MEGNO's limit, because plungers inflate MEGNO even in Kerr. **This scan therefore uses CLOSED
  pockets only, so every orbit stays bound and the plunger contamination cannot arise.**
- §150 / `194.dubeibe_L`: Dubeibe's Fig. 1 level (E = 0.94, |L| = 3.12) is reproduced at p = 4/5, a closed pocket
  at x ∈ [9.96, 21.9], with sign L = −3.12. Dubeibe gives no p or q, no initial conditions and no integration time
  (checked 2026-10-21, ar5iv §III.1). (Context from private correspondence omitted.) So their exact
  sections cannot be recovered; p = 3/5 at the same (E, L) is a test, not a reproduction.

## Objects
- TS δ=2 from ansatz's sealed package: p = 4/5 (tag t1o3, σ = 0.4) and p = 3/5 (t1o2, σ = 0.3).
- Control: Kerr at the same mass and spin, through the same code path, integrator and seeding rule.
- Prograde sense (Dubeibe's sign), E = 0.94.

## Levels (6 per system, 12 in all)
For each p ∈ {4/5, 3/5}:
- **D:** Dubeibe's level, L = −3.12 (a closed pocket in both TS2 and Kerr at both p; verified 2026-10-21).
- **S1:** L = −l_sep·(1 + 0.003). **S2:** L = −l_sep·(1 + 0.01). Here l_sep is §196's barrier separatrix, computed
  for each system separately, and ε > 0 means a CLOSED pocket hugging the unstable circular orbit. That orbit's
  separatrix is where a stochastic layer is generically widest.

## Instrument (validated; unchanged)
- §196 `indicators()`: RK4 with an exact complex-step tangent, 4 deviation vectors, MEGNO ⟨Y⟩.
- New optional `sections=True` records each upward equatorial crossing (y = 0, p_y > 0) as (t, x, p_x), plus the
  radial-maximum count. It is VERIFIED to leave every MEGNO output bit-identical (sha256 of checkpoints,
  t_plunge, hdrift and series, identical with the option on and off, 2026-10-21).
- dt: §196's `pilot_dt_v2` (life drift ≤ 1e-10 on 12 evenly spread orbits; halve from 0.05; REFUSE on empty).
- Per-orbit acceptance: life drift ≤ 1e-9 up to the decision time. Otherwise the orbit is EXCLUDED (counted,
  never dropped silently).
- **Rotation number** ν = n_ycross / n_xmax, the ratio of polar to radial oscillations over the orbit's life
  (frequency-map proxy). Its resolution is about 1/n_xmax. The drift Δν (first half vs second half) is
  DESCRIPTIVE only (§195c: frequency drift needs thousands of cycles).

## Stages (all automatic; seeds on the equatorial line y = 0, p_x = 0, p_y > 0 from the shell)
1. **Survey:** 200 seeds uniform in x across each level's seed region (edges offset by step/5), T = 3e4, both
   systems. Cost about 12 × 200 × 3e4 orbit-τ.
2. **Zoom:** from each system's OWN stage-1 ν(x0), find the rationals p/q with q ≤ 8 that ν crosses between
   adjacent seeds. Take the 3 of lowest q (ties: smaller p/q first); each window is the bracketing seed interval
   widened by one step on each side. At S1/S2 levels add one MANDATORY window, the 3 innermost stage-1 seed steps
   (the separatrix side). Each window gets 60 uniform seeds, T = 3e4.
3. **Long:** for each level and system, re-run the 60 seeds of the window with the lowest q (at S levels, the
   mandatory separatrix window instead) at T = 1e5.
4. **Confirm:** every TS2 orbit CHAOTIC in any stage is re-integrated at dt/2 with the same seed and stage T (cap
   40 per level, chosen in seed order).

## Verdict rules (fixed now)
- **Stages 1–2 (T = 3e4):** §196's validated rule, `verdict_megno` with `196_threshold_table.json` (duration-binned
  class-wise p99 over the Kerr/integrable null; validated on unseen levels: integrable false alarm 0/180).
- **Stage 3 (T = 1e5, beyond the validated table): the Kerr null threshold.** thr3 = the MAX of ⟨Y⟩(1e5) over
  every accepted, bound Kerr stage-3 orbit pooled across levels (n ≈ 360). A TS2 orbit is CHAOTIC iff
  ⟨Y⟩(1e5) > thr3 AND ⟨Y⟩(1e5) > ⟨Y⟩(3e4) + 1 (still growing). If fewer than 200 Kerr stage-3 orbits are
  accepted, stage 3 is UNREADABLE.
- **Kerr-control gate, per level:** the Kerr CHAOTIC count over stages 1–2 is tested against p0 = 0.03, one-sided
  binomial. p < 0.01 makes the level UNREADABLE (the §196 deep-v2 gate). More than 25% of TS2 orbits excluded on
  drift also makes it UNREADABLE.
- **LAYER at a level** requires all of the following:
  - the level passes the Kerr gate;
  - ≥ 3 TS2 orbits are CHAOTIC (stage 1–2 rule or stage-3 rule);
  - each of those is bound for its full T, accepted on drift, and still CHAOTIC at dt/2;
  - their seeds lie in one stage-2 window, or within 3 adjacent stage-1 seeds;
  - the matched Kerr window or region has 0 CHAOTIC.
  The layer is reported with its ν range and the nearest p/q.
- **Overall:** LAYER-FOUND (list the levels); else NO-LAYER-RESOLVED, reported with the resolution reached
  (minimum seed spacing in x, T, ν resolution) and stated as "not seen at this resolution", never as
  "integrable"; else UNREADABLE (every level unreadable).
- **Descriptive, never a verdict:** sections (x, p_x) of every orbit at D and S1, saved for plots; FLI; Δν; Fisher
  TS-vs-Kerr per level.

## Predictions (stated now)
- Kerr: 0 CHAOTIC everywhere (it is integrable); the gate passes.
- TS2 at D: NO-LAYER-RESOLVED (Dubeibe saw regular sections there, and a mid-depth pocket is far from any
  separatrix).
- TS2 at S1/S2: the best chance. My expectation is a 30% chance of LAYER at S1 and less at S2. If a layer exists
  it should sit at the separatrix window or at a low-q resonance.

## Operations (unattended)
- A plain detached process: new session (os.setsid), caffeinate, nice 10, under `watch_footprint.sh` (MAXMB
  3000, MINDISK 5 GB, MINFREEPCT 10), 3 worker processes, OpenBLAS with BLAS threads = 1.
- Checkpointing: one JSON per job (level × system × stage × batch). On restart, a job whose output exists with
  identical settings is skipped.
- Status: `results/198_status.json` is rewritten after every job. Its `updated` field changes only with content
  (stage, jobs done/total, ETA, errors).
- Final: `results/198_summary.json` + `results/198_REPORT.md` (plain-language verdict for the user).
- A failed job is recorded in status and the run continues. Pilot REFUSE means that job is UNREADABLE.

## Amendment 1 (2026-10-21, before any scan code ran; found while reading §196's code to reuse it)
- **Kerr gate alpha:** the text above says "p < 0.01 … (the §196 deep-v2 gate)". deep-v2 actually used
  P(X ≥ k | n, 0.03) < **0.05** (`KERR_GATE_ALPHA`). The claimed equivalence was wrong. To keep it TRUE, the gate is
  set to deep-v2's: p < 0.05 makes the level UNREADABLE. This is the stricter-for-Kerr choice (it trips more
  easily), so it can only remove levels, never add a LAYER.
- **"Matched Kerr window or region has 0 CHAOTIC"** is implemented as: the Kerr LEVEL has 0 accepted CHAOTIC orbits
  across all its stages. Kerr's windows are chosen from Kerr's own ν, so a window-by-window match is not
  well defined. The level-wide condition is stricter and simpler.
- **Δν (descriptive) is dropped:** `sections=True` records radial-maximum COUNTS, not times, so a half-split ν is
  unavailable. It was descriptive only. ν itself is unaffected.
- **Pilot granularity:** one `pilot_dt_v2` per (system, level) at T = 3e4 serves stages 1–2. A separate pilot at
  T = 1e5 runs on each stage-3 seed set. The confirm stage uses half that dt. The per-orbit 1e-9 acceptance applies
  everywhere regardless.
