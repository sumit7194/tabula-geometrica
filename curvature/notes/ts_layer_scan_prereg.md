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

## Amendment 2 (2026-10-21, after smoke testing, BEFORE any launch; no real-scan data exists)
Found by the toy-size smoke runs (results/198_smoke, deleted after testing) and the forced-path tests:
- **Duplicate windows:** two rationals bracketed by the same seed pair gave identical stage-2 windows (wasted
  compute). A rational whose bracket equals an already-picked window is skipped, and the next-lowest q is taken.
- **Two implementation-vs-text mismatches, fixed TO the text (silent_nulls 42):**
  - the confirm cap applied per stage; the text says 40 per LEVEL in seed order, which the code now does;
  - the cluster test counted only stage-2/3 orbits inside a window; the text says "seeds lie in one stage-2 window",
    any stage, which the code now does.
  Both were caught because the forced-path test returned a different LAYER set than the text implies.
- **Test-only switch** `TABULA198_SMOKE_FORCE` (=1 forces TS2 calls to CHAOTIC; =all also Kerr). It raises unless
  the output directory is results/198_smoke. Verified: the TS2 force gives LAYER with Kerr 0; the all force trips
  the Kerr gate (p ≈ 4e-28) and gives UNREADABLE, never LAYER; outside smoke it refuses.
- **Memory:**
  - building a spacetime costs about 0.5 GB that Python never returns;
  - the parent therefore never builds one (geometry and seed lines run in a throwaway child);
  - pool workers are recycled after every job (`maxtasksperchild=1`).
  Measured smoke peak 2229 → 1540 MB (whole tree, MEM+CMPRS); the full run is expected at ~1.9 GB.
- **Launcher** `scripts/198_launch.sh`:
  - os.setsid detach; caffeinate; nice 10; watch_footprint (MAXMB 3000, MINDISK 5, MINFREEPCT 10);
  - each attempt runs in its own process group, which is killed whole before a retry;
  - up to 6 attempts with a 5, 10, 15… minute backoff, resuming from finished jobs.
  Tested: killing only the watchdog mid-run left no orphans; attempt 2 resumed the one unfinished job and finished
  DONE. A first version would have left the scan running unwatched to race the next attempt (caught by this test).
- **Runtime estimate:** about 3.7e8 orbit-τ at ~1 ms per orbit-τ (measured under today's load average ~30 on 10
  cores) gives ~34 h on 3 workers. The stated range is 30–45 h; the live ETA is in results/198_status.json.

## Amendment 3 (2026-10-21, power-loss robustness at the user's request, BEFORE any launch)
- **Nothing in /tmp or $TMPDIR:** outputs, logs, status, the pid lock, job JSONs and checkpoints all live under
  curvature/results/. Only multiprocessing's transient semaphores use the system temp, and they matter only to a
  live process.
- **In-job checkpoints** (none existed: a stage-3 batch runs ~1–3 h, a stage-3 pilot ~1–3 h over its trials):
  - §196 `indicators(..., ckpt=, ckpt_every=1800)` saves the whole loop state every 30 min (atomic, fsync);
  - `_pilot_trial`/`pilot_dt_v2` likewise save in-trial state and keep completed trials;
  - files sit under results/198_ts_layer/ckpt/ and are deleted when the job writes its JSON.
- **Bit-identity verified:**
  - checkpointing off: hash unchanged (aee43f…);
  - indicators kill -9 at step 1599/30000 then resume: identical hash;
  - pilot kill -9 mid-trial: identical;
  - pilot kill -9 in trial 2 with trial 1 kept: identical;
  - full launcher power-loss test (below): 34/34 job files and the report identical to an uninterrupted run.
- **Power-loss test:**
  - stale pid file planted;
  - launch, kill -9 of the launcher and the whole attempt group during stage 3, with 3 live checkpoints;
  - relaunch with the same command and no manual lock clearing: it resumed (only the 4 stage-3 jobs re-ran), status
    starts = 2, DONE, 34/34 identical.
- **Lock fixed:** the stale-pid check matched any command line containing "198_launch.sh", including the shell that
  typed the launch command, and FALSELY REFUSED the relaunch. It now requires the exact shape
  `bash <path>/198_launch.sh`.
- **Worst case after a power loss:** ≤ 30 min of integration per running job (3 in parallel), plus a relaunch. The
  run itself needs no clean-up, because the stale lock is ignored.

## LAUNCHED 2026-10-21 21:59:07 IST
On the user's go, relayed by The Bridge, which ran the unchanged command. Launcher pid 75015, detached (ppid 1).
Attempt 1, phase pilot1, 0/12 jobs, no errors (checked at +1 min). Code at cd3ec0a. Expected 30–45 h.

## RUN FAILURE + FIX (2026-10-23, NOT science)
- Attempt 1 completed stages 1–3 (21:59 Oct 21 → 22:11 Oct 22), then crashed in the verdict's RESOLUTION field.
  `min()` ran over an empty window list: p = 3/5 at level D has NO stage-2 windows because the registered rule
  found none (its ν range 1.3548–1.3730 contains no rational with q ≤ 8; nearest 4/3 and 11/8). Resume
  re-crashed deterministically within ~35 s, 5 times, and the launcher GAVE UP at 23:59 Oct 22.
- The Bridge flagged it on Oct 22. **I failed to act on that message** (replied "no response requested"), so the
  run sat stopped until the user returned on Oct 23. A process lapse, recorded.
- Fix: that field is None when a level has no windows. This is a one-line reporting fix; no rule, threshold or
  data changes. By the registered rule, p = 3/5 D therefore has no stage 2/3, and the report states it.
- Dry run on the real data after the fix (read-only, nothing written): 0 TS2 CHAOTIC at every level, Kerr 0 at
  every level, thr3 = 2.077 from 300 Kerr stage-3 orbits. Relaunched with the unchanged command to finish confirm +
  verdict.

## RESULT (2026-10-23 07:17, sealed in results/198_summary.json + 198_REPORT.md)
**NO-LAYER-RESOLVED.** TS2: 0 CHAOTIC of 2,340 accepted orbits across all 6 levels (stages 1–3), so nothing went to
confirmation. Kerr: 0 CHAOTIC everywhere, and every Kerr gate passed (p = 1.0). Stage 3 ran at 5 levels (p = 3/5 D
had no windows by rule); thr3 = 2.077 from 300 Kerr orbits.
- **Resolution reached** (the null's scope):
  - stage-1 seed spacing Δx 0.045–0.148; stage-2 Δx 0.0030–0.0074;
  - T up to 1e5 (≈ 500+ radial periods);
  - ν resolution ≈ 0.002–0.005.
- **Descriptive only:** stage-3 ⟨Y⟩(1e5) has TS2 median 1.952 / max 2.136 and Kerr median 1.977 / max 2.077. One
  TS2 orbit sits 3% above the Kerr maximum but is NOT growing (the registered growth clause fails), and ⟨Y⟩ ≈ 2
  is the regular-motion value. The two distributions overlap.
- **Predictions:** Kerr 0 ✓. TS2 at D: no layer ✓. **My "30% chance of a layer at S1" did not happen; a single
  outcome cannot refute a probability, recorded anyway.**
- **Reading:** agrees with Dubeibe et al. 2007 (regular sections) AT THIS RESOLUTION. It does not contradict the
  fleet's non-integrability results: a layer narrower than Δx ≈ 0.003, or slower than T = 1e5 to show MEGNO
  growth, is not excluded. Exponentially thin separatrix layers are the generic expectation for weak
  non-integrability, so a null at finite resolution is the expected look of such a system too.

## CORRECTION (2026-10-23, found while designing §199): the S1/S2 rationale was wrong
At S1/S2 the shell lies BELOW the barrier top (closed pocket), so there is no Lyapunov orbit and no saddle separatrix
on the energy surface. The claim above, that those levels hug "the unstable circular orbit's separatrix, where a
stochastic layer is generically widest", is withdrawn. They probe long-period near-saddle tori. The VERDICT
(NO-LAYER-RESOLVED, with its resolution) is unaffected. See notes/separatrix_splitting_prereg.md.
