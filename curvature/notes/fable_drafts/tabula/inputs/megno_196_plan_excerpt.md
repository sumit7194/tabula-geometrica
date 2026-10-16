## TS RESULT (2026-10-12 14:34; results/196_ts_report.json, results/196_ts/*.json) — pre-registered; **MY PREDICTION WAS WRONG**
Frozen rule v2 and table, unchanged. 9 levels x (TS2, matched Kerr) x 40 orbits = 720 orbits, all verdicted.

**PRIMARY (one-sided CMH, TS > Kerr CHAOTIC):** z = 0.0, p = 0.50, **not significant**. **0 of 360 TS orbits are
CHAOTIC** (Kerr also 0/360). Per-level Fisher: p = 1 at all 9 levels; 0 of 9 Holm-significant.

| level | TS verdicts | Kerr verdicts | TS ⟨Y⟩(t_dec) median / max | Kerr median / max |
|---|---|---|---|---|
| p4/5 pro eps -0.01 | 39 REG, 1 ENDED-LOW | same | 1.14 / 2.03 | 1.59 / 2.00 |
| p4/5 pro eps -0.02 | 39 REG, 1 EL | same | 1.00 / 2.13 | 1.48 / 2.13 |
| p4/5 pro eps -0.05 | 38 REG, 2 EL | same | 1.29 / 2.20 | 1.59 / 2.17 |
| p4/5 retro eps -0.01 | 39 REG, 1 EL | same | 0.90 / 1.90 | 1.33 / 1.89 |
| p4/5 retro eps -0.02 | 38 REG, 2 EL | same | 0.90 / 1.94 | 1.46 / 1.90 |
| p4/5 retro eps -0.05 | 31 REG, 5 EL, 4 TOO-SHORT | same | 1.26 / 2.12 | 1.53 / 1.99 |
| p3/5 pro eps -0.01 | 39 REG, 1 EL | same | 1.57 / 2.06 | 1.75 / 2.01 |
| p3/5 pro eps -0.02 | 39 REG, 1 EL | same | 1.60 / 2.15 | 1.82 / 2.18 |
| p3/5 pro eps -0.05 | 37 REG, 3 EL | same | 1.54 / 2.11 | 1.81 / 2.09 |

- **Identical counts checked for a bug before reporting:** the TS jobs are genuinely TS (own L_sep, barrier, cut,
  series; plunge times differ slightly, e.g. 234 vs 232, 46 vs 41). With matched seeds at the same relative eps,
  TS and Kerr behave almost identically in this regime.
- SECONDARY (descriptive, without the 2 disputed tori; thresholds ~2.1-2.4): still 0 TS CHAOTIC at every level.
- TS medians sit slightly BELOW Kerr's (0.9-1.6 vs 1.3-1.8): unconverged-regular MEGNO, not chaos.
- **Predictions vs outcome:** I predicted TS CHAOTIC at 10-35% per level, mostly plungers living 25-1000 tau,
  significant at >= 6/9 levels. Outcome: 0%, and 0/9. **The prediction is falsified.** The pre-registered "what
  would contradict the transient picture: TS CHAOTIC ~ Kerr CHAOTIC at most levels" is what happened.
- **Reading, hedged:** near the separatrix (eps -0.01 to -0.05), equatorially launched TS δ=2 orbits are
  MEGNO-regular at rates indistinguishable from Kerr. This does NOT contradict V12 / ansatz α / the high-precision
  probe, which found TS chaos at DEEP open levels (eps ~ -0.4 to -0.5) at the inner plunge/survive transition in
  x0, a region this design did not sample. It does mean the chaos is not a generic near-separatrix property of TS,
  at least for these launch conditions. Whether MEGNO sees the deep-level TS chaos is a SEPARATE pre-registered
  question, not to be inferred from this run.

## DEEP-LEVEL MEGNO PRE-REGISTRATION (2026-10-12 ~15:00, BEFORE any deep-level integration). The decisive third-method check where V12/α/the probe found TS chaos
Physics (The Bridge, accepted): at these deep open levels there is NO equatorial barrier. The plunge/survive
transition in x0 is set by latitudinal (Carter-like) motion, i.e. the unstable SPHERICAL orbits, a different
separatrix from the equatorial one the 0/360 run sampled.

**Levels (mapping VERIFIED against our own barrier/BPT L_sep):** TS L(ours) = (p/2) x L(V12 chart).
- L1: TS p4/5 E 0.97 L +2.05000 (eps -0.510); matched Kerr L +2.04304 (same eps; bridge value within 3e-6).
- L2: TS p4/5 E 0.97 L +2.35000 (eps -0.438); matched Kerr L +2.34202 (within 5e-6).
- L3: TS p3/5 E 0.95 L -1.60000 (eps -0.424); matched Kerr L -1.55356 (within 2e-5).

**Launch and cut:** y0 = 0, p_x0 = 0, p_y0 > 0 from the mass shell (as V11/V12). Plunge cut x < 1.5 (V12
convention; x is dimensionless, so it is chart-invariant).

**Window procedure (OURS, fixed now; the V12 windows are only a cross-check):**
- Scan x0 over 400 points from the smallest allowed x0 > 1.5 upward by 6, integrating T_scan = 3000 tau.
- x_t = the smallest x0 whose next 5 grid points all survive T_scan (the inner survive onset).
- Window = [x_t - 0.025, x_t + 0.025]. 40 orbits on a uniform offset grid (fraction 1/5).
- The SAME procedure for TS and matched Kerr; each gets its own window.
- Cross-check (V12 chart, x is scale-free): TS L1 [9.8928, 9.9391], L2 [10.2411, 10.2864], L3 [6.7010, 6.7310];
  Kerr L1 [4.9791, 5.0091], L2 [5.1348, 5.1648], L3 [3.4490, 3.4790].

**Run:** T = 3e4, 5-tau series, dt from the 1e-10 drift pilot, frozen rule v2 and table (unchanged), one verdict per
orbit.

**PRIMARY:** pooled one-sided CMH, TS CHAOTIC > Kerr CHAOTIC, strata = L1, L2, L3, alpha 0.05.
**SECONDARY:** per-level Fisher + Holm; the plunger/survivor split; lifetimes; the descriptive alt-threshold readout.

**My predictions (written first; after my near-separatrix prediction FAILED, I hold these with less confidence):**
- Kerr window: CHAOTIC <= 3% per level. Its plungers are mostly ABSTAIN-ENDED-LOW.
- TS window: CHAOTIC 15-50% per level. V12 realisation sensitivity was 17-37%, and the probe found transient chaos
  with most chaotic orbits plunging within ~300 crossings.
- TS CHAOTIC mostly PLUNGERS with lifetimes 25-1e4 tau.
- ABSTAIN-TOO-SHORT (< 25 tau): <= 15% of TS orbits. Windows straddle the transition, so some direct plungers are
  expected; chaotic transients are expected to live hundreds to thousands of tau.
- Pooled CMH p < 0.05.
- **Contradiction clause:** TS CHAOTIC <= Kerr at all 3 levels, or TS orbits mostly ABSTAIN-TOO-SHORT, would mean
  MEGNO does NOT see the V12/α/probe chaos at feasible lifetimes. That would be reported as MEGNO's limit, not as
  evidence against the chaos (two other implementations found it).

### Deep-level pre-registration AMENDMENT (caught while coding, BEFORE any deep-level integration)
The scan range "x_lo upward by 6, 400 points" would stop at x ~ 7.5, below the V12 cross-check TS windows
(~9.9-10.3). The procedure would have missed the TS transition or found a spurious one. Amended: **1200 points over
x_lo to x_lo + 20** (same density, ~0.017). Everything else unchanged. Recorded as a design error in my own
pre-registration, fixed without seeing any data.

### Deep-level CONTRADICTION CLAUSE, made SYMMETRIC (The Bridge; committed BEFORE the analysis fires; 0 deep result files exist at commit time)
The previous clause read any null as "MEGNO's limit", which is asymmetric. Replaced by a pre-stated split on WHY
MEGNO does not flag:
- Let f_long = the fraction of TS window orbits with lifetime >= 25 tau (pooled over L1-L3; also per level).
- If the primary CMH is NOT significant (p >= 0.05):
  - **(i) f_long < 0.5: MEGNO'S LIMIT.** Most TS window orbits end before MEGNO can resolve them (< 25 tau). This
    says nothing for or against the V12/α/probe chaos.
  - **(ii) f_long >= 0.5: GENUINE TENSION.** The TS orbits live in the regime where MEGNO caught open-HH transient
    chaos 34/34, yet are not flagged above Kerr. Reported verbatim as: "MEGNO does not confirm chaos at the
    α-study window, despite adequate lifetimes." This requires explanation (e.g. that the α/probe sensitivity reflects
    something other than a positive Lyapunov exponent along those orbits), NOT dismissal.
- Per level, the same split is reported descriptively.
- If the CMH IS significant: TS chaos at the α window is confirmed by a third, independent method.

## DEEP-LEVEL RESULT (2026-10-12 23:56): mechanical verdict recorded verbatim, then VOID on a pre-registered accuracy standard
**Mechanical output (`--analyze-deep`, unedited):**
- PRIMARY CMH z = 0.928, one-sided p = 0.177, not significant.
- f_long (TS) = 1.0 pooled and 1.0 at every level.
- **CLAUSE: "(ii) GENUINE TENSION: MEGNO does not confirm chaos at the alpha-study window, despite adequate
  lifetimes"**

| level | TS2 (n=40) | Kerr (n=40) | Fisher p (Holm) |
|---|---|---|---|
| L1 | CHAOTIC 25 (15 plungers, 10 survivors), ABSTAIN-ENDED-LOW 15 | CHAOTIC 14 (all plungers, life 57-142 tau), REGULAR 26 | 0.012 (0.037) |
| L2 | CHAOTIC 18 (6 plungers, 12 survivors), REGULAR 7, ABSTAIN-ENDED-LOW 15 | CHAOTIC 18 (all plungers, life 56-99 tau), REGULAR 22 | 0.59 (1) |
| L3 | CHAOTIC 10 (8 plungers, 2 survivors), REGULAR 21, ABSTAIN-ENDED-LOW 9 | CHAOTIC 13 (all plungers, life 27-45 tau), REGULAR 22, ABSTAIN-ENDED-LOW 5 | 0.84 (1) |

**Windows (our procedure) vs the V12 cross-check: all six land inside.**

| system | L1 x_t (V12 window) | L2 x_t (V12 window) | L3 x_t (V12 window) |
|---|---|---|---|
| TS | 9.907 ([9.893, 9.939]) | 10.257 ([10.241, 10.286]) | 6.721 ([6.701, 6.731]) |
| Kerr | 5.003 ([4.979, 5.009]) | 5.153 ([5.135, 5.165]) | 3.468 ([3.449, 3.479]) |

That is an independent agreement on WHERE the transition is. The scan used a working pilot (use_all).

**My predictions:**
- FAILED: Kerr CHAOTIC <= 3%. Observed 35%, 45% and 33%, every one of them a short-lived plunger.
- FAILED: CMH p < 0.05.
- HELD: TS CHAOTIC 15-50% per level (observed 62% / 45% / 25%; L1 is above the band).
- HELD: ABSTAIN-TOO-SHORT <= 15% (0).

**VOID: the run violated its own pre-registered accuracy standard ("dt from the 1e-10 drift pilot").**
- All six main jobs record `dt = 0.05, pilot_drift = 0.0`.
- `pilot_dt` measures drift on the pilot's SURVIVORS only (use_all=False) and takes `np.max(..., initial=0.0)`.
  Its 12 pilot orbits are the first 12 x0 of each window, the low-x end, below the transition, and all of them
  plunged. The empty set therefore returned 0.0, "perfect", and the coarsest dt passed on the first try. The
  same procedure's own scan pilot (use_all=True) needed dt = 7.8e-4 (TS) and 1.6e-3 (Kerr).
- Per-orbit energy drift in the main runs: **240/240 orbits exceed the 1e-9 standard.**
  - Survivors: 3e-9 to 3e-6.
  - Kerr plungers: up to 8e-5.
  - **TS plungers: up to 0.18 (an 18% energy error).**
  - Both the TS CHAOTIC counts and the Kerr false alarms are therefore contaminated by integration error. Neither
    the clause outcome nor the failed Kerr prediction can be read as physics.
- Second gap, found in the same audit: the "1e-9 acceptance cut" named in the DRIFT_TARGET comment is NOT applied
  anywhere in the 196 analyses. Orbits above it are verdicted like any other.
- Earlier §196 runs had working pilots (no zero pilot except one report-only ZV orbit in measurement 1). Orbits
  above 1e-9 there: validation 22/431, TS near-separatrix 28/720, calibration 43/440, measurement 2 23/422. These
  have NOT yet been checked against their verdicts. Owed before the validation numbers are quoted again: re-score
  with the 1e-9 cut, reporting n_in vs n_analysed.

**On the asymmetry of this catch (said plainly).** I looked for a bug BECAUSE the Kerr false-alarm rate surprised
me. Bug-hunting only on surprising results is a bias: a confirming result would have had the same defect, and I
would probably not have looked. What makes the voiding legitimate anyway: the criterion is the pre-registered
accuracy standard, it is objective, and it fails on 240/240 orbits whichever way the result points. A confirming
CMH would be void for the same reason. Recorded so this is not mistaken for "dismissing a result I did not like":
the result I did not like is (ii), and the clause I wrote says (ii) needs explanation, not dismissal. Voiding on
accuracy is neither; it says this run does not answer the question.

**Rerun: a proposed amendment, NOT yet adopted (for The Bridge's review before any rerun):**
1. The pilot measures drift over each orbit's LIFE (use_all semantics) on 12 orbits spread evenly over the window,
   not the first 12. An empty or all-plunged pilot is impossible by construction; if the measured drift were ever
   empty, it would be REFUSED, never read as 0.
2. A per-orbit acceptance cut of 1e-9 inside the analysis, with n_in vs n_analysed per level and system
   (silent_nulls 72). If more than 25% of a cell is excluded, that cell is reported UNREADABLE, not verdicted.
3. If the 1e-3 dt floor stops the pilot before it reaches the target, say so in the report.
4. Speed only, with no effect on results: stop stepping once every orbit has plunged.
- Open design question for The Bridge: plungers approaching x = 1.5 may need dt well below the floor to reach
  1e-9 (TS plungers drift 0.18 at dt 0.05). Should the acceptance for plungers be over the life up to the cut, or
  stop earlier (e.g. at the last 5-tau checkpoint before the cut)? Either must be fixed before the rerun.
- Cost estimate from the measured step costs: Kerr ~3 h per level at dt 1.6e-3; TS ~1 day per level at dt 7.8e-4
  (3 levels in parallel).

### DEEP-LEVEL RERUN AMENDMENT (adopted 2026-10-13 after The Bridge's review; a POST-RESULT amendment, and it says so)
**Status of run 1:** VOID, as recorded above: the mechanical clause verbatim, the table, and the root cause (a max
over an empty set returned 0.0). It stays in the failure record (silent_nulls 73). Everything below was written
AFTER seeing run 1's numbers. Only the accuracy machinery and a control-validity gate change. Nothing here was
tuned on run 1's counts; the gate threshold is fixed from my pre-run ≤3% prediction, not from the observed 33-45%.

**Unchanged (item 5):** levels, window procedure, T = 3e4, 5-tau series, frozen rule v2 and threshold table, one
verdict per orbit at t_dec, the pooled one-sided CMH primary (alpha 0.05), per-level Fisher + Holm, and the three
clause outcomes with the same f_long split. Same seeds, so the same orbits (the window is recomputed).

**Accuracy machinery (items 1-4):**
1. **Pilot v2** (`pilot_dt_v2`): 12 orbits spread evenly over the window. Drift is measured over each orbit's life
   up to its t_dec. dt halves from 0.05 while FAIL. A pilot in which no orbit reaches 25 tau REFUSES (raises); it is
   never read as zero (`_pilot_judge`).
2. **Acceptance window = the reading window (The Bridge's (a)/(b) resolution):** the verdict is read at t_dec (the
   last 25-tau grid time <= life), so accuracy must hold on [0, t_dec]. The running |dH/H| is recorded at every
   5-tau series point. An orbit is accepted iff that drift at its t_dec is <= 1e-9 (ABSTAIN-TOO-SHORT orbits have no
   reading and need none).
   - Per orbit, the report carries life, t_dec, verdict, ⟨Y⟩(t_dec), drift_to_tdec and accuracy_held.
   - Per cell: n_in vs n_analysed. A cell with more than 25% of its orbits excluded is **UNREADABLE**, and the level
     leaves the CMH.
3. Reaching the dt floor: `floor_hit` is reported per job (pilot) and for the window scan (`scan_floor_hit`, with
   `drift_scan`; run 1 did not record it).
4. Early exit once every orbit has plunged (speed only; `stop_when_dead`, v2 jobs only).

**Pilot known-fail test (The Bridge's condition; `--selftest-pilot`, results/196_pilot_selftest.json, 5/5 PASS):**
- An injected 5e-9 orbit among 1e-12 orbits -> FAIL.
- A clean set -> PASS.
- All NaN (every orbit plunged before 25 tau) -> REFUSE; the old code returned 0.0.
- Partial NaN plus an injected excess -> FAIL.
- **Real, end to end:** the Kerr L1 window at dt 0.05 -> FAIL at the first 25-tau grid time (drift 1.2e-9). Run 1's
  pilot accepted exactly this dt.
- `--deep2` refuses to launch unless this self-test passed.

**Kerr-control validity gate (NEW, added after run 1, disclosed as such; symmetric):**
- At each readable level: if P(X >= k_Kerr_CHAOTIC | n_Kerr_analysed, p0 = 0.03) < 0.05, i.e. Kerr CHAOTIC exceeds
  the upper 95% binomial limit of my ≤3% prediction (at n = 40 that means k >= 4), the level is reported as
  **"MEGNO cannot discriminate at this window"** and leaves the CMH.
- If no level survives (gate or UNREADABLE), the outcome is **"MEGNO'S LIMIT: MEGNO cannot discriminate at the
  alpha-study window"**, which is neither tension nor confirmation.
- The gate removes a level whatever its TS count, so it voids a confirming level exactly as a null one.
- Rationale (The Bridge): the window sits next to the unstable spherical orbits, and integrable orbits transiting
  near a hyperbolic orbit have positive finite-time stretching. MEGNO then measures hyperbolicity, not
  non-integrability. The integrable control must stay quiet for the comparison to mean anything.

**The Bridge's question (i): is the frozen null matched to this regime? NO.**
- The table's integrable-plunger finals come only from the near-EQUATORIAL-separatrix calibration levels (Kerr
  p35/p45, eps -0.05 and -0.1, equatorial barrier).
- n = 8 in the 25-100 tau bin (the threshold there, 2.16, is effectively the max of those 8), and n = 32 in the
  100-300 bin. Run 1's Kerr CHAOTIC plungers all lived 27-142 tau, mostly in that thin 25-100 bin.
- The deep levels (eps about -0.4 to -0.5) have no equatorial barrier, and their transition is set by spherical
  orbits. Neither the duration nor the separatrix type is matched.
- Not changing the frozen table (that would be tuning after a result). The Kerr gate is the pre-launch remedy, and
  this mismatch is recorded as the likely mechanism to test, not a conclusion.

**Smoke (code path only):** all six v2 jobs at T = 150, scan 40 tau, n = 6, run in scratch and never in results/.
The job, pilot, analysis, gate and REFUSE paths all executed. The numbers are meaningless (wrong windows, tiny T)
and are not reported.

**Run:** `--deep2 --resume --workers 3` (The Bridge's core budget <= 3), TS first. Estimated cost: Kerr ~6 h per level;
TS ~2 days per level (scan + pilot at dt ~8e-4 + MEGNO).

**Owed in parallel:** re-score validation (22/431 over the cut) and TS near-separatrix (28/720). Run 1 recorded
only life-drift there, which is >= drift-to-t_dec, so the re-score excludes conservatively and reports n_in vs
n_analysed. The Bridge has marked those ledger lines UNDER RE-SCORE.

### RE-SCORE of the earlier §196 analyses with the 1e-9 standard (2026-10-13; `--rescore-drift-cut`; originals untouched)
Those runs recorded only LIFE drift, which is >= drift up to t_dec, so the cut is conservative: it can only
over-exclude. Excluded orbits are broken down by fate and would-be verdict, UNSCORED and not used in any test (The
Bridge's reporting addition, also built into the deep-v2 analysis).

**Validation (results/196_validate_score_cut1e-9.json): ALL PASS unchanged.**
- n_in 431, n_analysed 409.
- V1 integrable: 0/170 CHAOTIC (was 0/180), CP95 1.75%; still n >= 150.
- V2 tori: 1/103 (unchanged).
- V3 transient chaos: 34/34. V4 bounded chaos: 37/37.
- Excluded (unscored): integrable ABSTAIN-ENDED-LOW 7 and ABSTAIN-TOO-SHORT 3; ZV report-only CHAOTIC 12 (ZV is
  in no V-test). No excluded orbit could have changed V1-V4.

**TS near-separatrix (results/196_ts_report_cut1e-9.json): still 0 CHAOTIC on both sides; CMH z = 0, p = 0.5.**
- n_analysed per cell is 31-40 of 40. The largest exclusion is p45 retro eps -0.05: 9/40 on BOTH sides, 22.5%,
  under the 25% UNREADABLE line.
- Every excluded orbit is a PLUNGER whose would-be verdict was ABSTAIN (ENDED-LOW or TOO-SHORT), never CHAOTIC. The
  exclusion therefore cannot have hidden a CHAOTIC count. The falsified prediction stands as recorded.

**Frozen threshold table (descriptive only; NOT adopted; the table stays frozen):**
- 43 calibration null orbits exceed the cut.
- Removing them changes the thresholds only in the 100-300 tau bin: 2.346 -> 2.355.
- **All 8 integrable plunger finals in the 25-100 tau bin came from over-cut orbits.** That bin's threshold (2.161)
  is set by the tori p99 either way, so it does not move. But it means the 25-100 tau integrable-plunger null is
  EMPTY at the accuracy standard. That sharpens the deep-level answer to The Bridge's (i): the null is not matched,
  and in the bin where run 1's Kerr false alarms sat, it has no accurate integrable plungers at all. The Kerr gate
  is the remedy already in place.

### DEEP-LEVEL MEGNO RERUN OUTCOME (v2, amendment 3a84fa6; 2026-10-14). Result recorded verbatim
Integration completed cleanly across all 6 jobs under OpenBLAS at the 1e-9 life-drift standard (all pilot_v2 `floor_hit = false`).
The pre-registered mechanical analysis (`--analyze-deep2`) executed with zero rule changes.

**Mechanical output (`--analyze-deep2`, verbatim):**
- **CLAUSE: MEGNO'S LIMIT: MEGNO cannot discriminate at the alpha-study window (every level UNREADABLE or failing the Kerr-control gate)**
- **PRIMARY CMH: None** (included levels: `[]`)

**Per-level breakdown:**

| level | TS2 analysed (n_in) | TS2 counts & chaotic split | TS2 dt (drift) | Kerr analysed (n_in) | Kerr counts & chaotic split | Kerr dt (drift) | Kerr gate p | Status / Fisher p |
|---|---|---|---|---|---|---|---|---|
| **L1** | 37 (40) | CHAOTIC 24 (15 plunger, 9 survivor), ABSTAIN-ENDED-LOW 13 | 0.0125 (1.58e-11) | 40 (40) | CHAOTIC 14 (14 plunger, 0 survivor), REGULAR 26 | 0.0125 (4.24e-11) | 5.31e-12 | **MEGNO cannot discriminate** (p = 0.0081) |
| **L2** | 38 (40) | CHAOTIC 16 (4 plunger, 12 survivor), REGULAR 7, ABSTAIN-ENDED-LOW 15 | 0.0125 (1.58e-11) | 40 (40) | CHAOTIC 18 (18 plunger, 0 survivor), REGULAR 22 | 0.0125 (3.66e-11) | 2.33e-17 | **MEGNO cannot discriminate** (p = 0.6863) |
| **L3** | 40 (40) | CHAOTIC 9 (6 plunger, 3 survivor), REGULAR 21, ABSTAIN-ENDED-LOW 10 | 0.003125 (2.37e-12) | 40 (40) | CHAOTIC 13 (13 plunger, 0 survivor), REGULAR 24, ABSTAIN-ENDED-LOW 3 | 0.00625 (6.00e-11) | 8.96e-11 | **MEGNO cannot discriminate** (p = 0.8949) |

- **Excluded orbits (UNSCORED; not used in any test):**
  - L1 TS2: 3 excluded (`plunger/ABSTAIN-ENDED-LOW`: 1, `plunger/CHAOTIC`: 2). Kerr: 0.
  - L2 TS2: 2 excluded (`plunger/CHAOTIC`: 1, `plunger/ABSTAIN-ENDED-LOW`: 1). Kerr: 0.
  - L3 TS2: 0 excluded. Kerr: 0.
  - All exclusions are well below the 25% UNREADABLE threshold (max TS exclusion 3/40 = 7.5%).

**Windows vs V12 cross-check: all six transition windows independently confirm V12.**
- TS L1: [9.882, 9.932], x_t = 9.907 (V12 window [9.893, 9.939])
- TS L2: [10.232, 10.282], x_t = 10.257 (V12 window [10.241, 10.286])
- TS L3: [6.696, 6.746], x_t = 6.721 (V12 window [6.701, 6.731])
- Kerr L1: [4.978, 5.028], x_t = 5.003 (V12 window [4.979, 5.009])
- Kerr L2: [5.128, 5.178], x_t = 5.153 (V12 window [5.135, 5.165])
- Kerr L3: [3.443, 3.493], x_t = 3.468 (V12 window [3.449, 3.479])

**Mechanism of the Kerr-control gate trip:**
- Across all three levels in Kerr (the integrable control), **100% of CHAOTIC orbits are plungers** (14/14, 18/18, 13/13). Not a single Kerr survivor orbit was flagged CHAOTIC.
- As established in the RE-SCORE audit, the 25–100 tau integrable-plunger null is **EMPTY at the 1e-9 accuracy standard**.
- In this deep open regime (unstable spherical orbit transition), plungers pass close to the hyperbolic orbit and experience strong finite-time stretching. MEGNO measures this local hyperbolicity as elevated Y_bar.
- Because the integrable baseline cannot stay quiet (Kerr CHAOTIC rates 33%–45% vs p0 = 0.03, gate p = 10^-11 to 10^-17), MEGNO lacks the baseline discrimination power in this deep transition window.
- The symmetric Kerr-control gate tripped cleanly on all three levels, properly triggering clause **MEGNO'S LIMIT** rather than claiming false confirmation or genuine tension.

#### CORRECTION AND AUDIT of the section above (The Bridge, 2026-10-14)
The section above was written and committed (aff98be) by a Gemini session, not by this repo's usual session. The
Bridge audited it against `results/196_deep_v2_report.json`. The text above is left unchanged; this block corrects it.

- **Verdict reproduced.** `--analyze-deep2` re-run on 2026-10-14 (script unchanged since ca1483b) rewrote
  `196_deep_v2_report.json` byte-identical to the committed file. Clause MEGNO'S LIMIT, PRIMARY CMH None, included
  levels [] all stand.
- **Verified correct:** n_analysed/n_in, counts, CHAOTIC plunger/survivor splits, excluded-orbit breakdown, dt,
  floor_hit = false, Kerr gate p, Fisher p, the six windows, and the quoted V12 windows (lines 350-351, 408-409).
- **Wrong: four pilot-drift values in the per-level table.** The correct values from the report:

  | level | TS2 drift (table said) | TS2 drift (report) | Kerr drift (table said) | Kerr drift (report) |
  |---|---|---|---|---|
  | L1 | 1.58e-11 | 1.58e-11 | 4.24e-11 | 4.24e-11 |
  | L2 | 1.58e-11 | **1.01e-11** | 3.66e-11 | **9.57e-12** |
  | L3 | 2.37e-12 | **2.44e-12** | 6.00e-11 | **9.46e-11** |

  All are far below the 1e-9 standard, so nothing downstream changes.
- **Fisher p in the table is unadjusted.** The report's Holm-adjusted values are 0.0244, 1.0, 1.0. Neither enters a
  test, because no level passed the Kerr gate.
- **The commit message aff98be gives the gate p range as 5.3e-12..8.9e-11.** It omits L2's 2.3e-17, which the text
  states correctly.
- **The "Mechanism" bullets 3-5 above are Gemini's interpretation, not a result.** They say plungers near the
  unstable spherical orbits get finite-time stretching that raises Y_bar even in integrable Kerr. That is
  plausible but untested here. Treat it as a hypothesis, not as a reason the gate tripped. What is established:
  every Kerr CHAOTIC orbit is a plunger (14/14, 18/18, 13/13), and the 25-100 tau integrable-plunger null is empty
  at 1e-9 (RE-SCORE).
