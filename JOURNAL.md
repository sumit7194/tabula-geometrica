# Journal — activity log (SpaceTime: curvature / NN)

*One entry per working session, newest first. What happened, what was decided,
where the details live. (Lab-notebook-level detail stays in each sub-project's
`notes/lab_notebook.md`; polished narratives live in `writeups/`.)*

> **Repo split 2026-06-13:** the black-hole LIGO-data projects (echoes, ringdown,
> pbh) moved to `../BlackHole/`. Entries below predating the split are the shared
> historical narrative and mention all projects; new black-hole work logs to
> `../BlackHole/JOURNAL.md`. This journal is now curvature/NN going forward.

---

## 2026-06-15d — Phase G-sym: the symmetry-respecting generalist (training)
- **The dilemma dissolved, not split.** A parallel Claude session (credited)
  reframed the mean-pool as body-relabeling *invariance* — the equivalence
  principle in disguise: an invariant code can only keep body-symmetric info
  (geometry) and structurally drops the tag→charge binding. So the stage/actor
  split is the invariant/equivariant decomposition under relabeling; imposing
  that symmetry is the same fair move as Phase A's boost-invariant head, and it
  re-derives Phase C (0 vs 1 number/body) from symmetry alone.
- **My amendment (recorded):** field amplitudes (e_amp, b_amp) are body-symmetric
  yet decode badly because their signature is charge-GATED — so restoring the
  per-body channel should lift those decode rows too (gate A3b).
- **Built + launched `28_symmetric_generalist.py`** (SymGeneralist, 2.16M): R⁶⁴
  invariant mean-pool stage (the legible G3 object) + an equivariant per-body
  channel (query cross-attends into context, bottlenecked to R⁸ so it carries
  labels not the world). Training on the 120k bank, 150k steps, MPS (~6h).
- **Gates A1–A4 pre-registered** (lab notebook); all probes staged: 27 for
  A2/A3b/A4, new 28b decodes per-body charge from the equivariant channel with
  an invariant-stage control (worldgen gained --emit-qlabels for it). The
  consensus→legibility bet is deliberately deferred to its own pre-registered
  experiment (with a recurrence-vs-discreteness control).
- Dashboard restarted (server had stopped; title already correct as
  "tabula geometrica").

## 2026-06-15c — Phase G prize: the world-summary space (G2 ✓, G3a ✓, G3c ✓✓)
- **G3a — families cluster, ARI 0.82 (PASS).** The PCA map of the 64-d summary
  reads like a physics taxonomy: flat 1+1 / 3+1 as separate knots, well1p1 and
  aniso2p1 isolated (pure geometry), and the three EM-coupled worlds (chargedE,
  magneticB, twocharge) sharing one neighborhood; matter a diffuse cloud.
- **G3c — EM-kinship confirmed (exploratory, striking).** chargedE & magneticB
  sit 2× closer to each other (15.1) than to the gravity well (29.1), z=26.7 vs
  shuffled null. The net spontaneously carved "force gated by a per-body charge"
  as its own region of law-space. (Ties to It-from-Qubit "geometry of laws.")
- **G2 — zero-shot to +25% wider worlds: PASS.** traj ratio 1.00, pair 0.97→0.90.
  It learned mechanisms, not a table.
- **G3b decodability FAILS as gated (median 0.50) — but the pattern IS the
  finding:** world-geometry decodes great (well depth 0.92, total mass 0.98),
  per-body-charge-gated field amplitudes decode poorly (magneticB b_amp 0.04).
- **Synthesis: the G1 trajectory gap and the G3b illegibility are the SAME
  thing** — the global mean-pool nails world-geometry, is blind to per-body
  labels. So accuracy and legibility aren't in tension; a hybrid (global w +
  query→context attention) fixes both. Scripts: 27_g3_probes.py; worldgen got
  --widen for G2. Decision on the hybrid pending (thinking in parallel).

## 2026-06-15b — Phase G: 150k run finishes; underfit → overfit; data-scaling next
- **G1 second verdict: still 2/8 — but the failure mode flipped.** Train loss
  fell 4× (traj 0.023→0.0053) while val didn't move: the model memorized the
  21.6k training episodes. 30k run = underfit, 150k run = overfit ⇒ the steps
  knob is exhausted and the binding constraint is DATA (the user's "you need
  millions of games" instinct lands a second time). Methodology arm (c)
  answered by runs already paid for.
- **Pre-registered next: a data-scaling curve.** 4 worldgen shards × 30k
  episodes generating now (per-seed heartbeats after a shared-heartbeat
  rename race killed shard 3 — patched in 25_worldgen). Arms: 48k and 120k
  banks, identical model/budget. If val scales with data → ride it; if it
  plateaus → measure the context-information floor (owed; recorded as a
  process miss that it wasn't measured before gating).
- **Repo is live: https://github.com/sumit7194/tabula-geometrica** (public).
  Initial push (142 files, 15 MB incl. gate-required model weights),
  description + topics set, README retitled to the new name. Repo scope
  locked: curvature only.

## 2026-06-15 — Phase H row 1 lands (knee = 2); Phase G build + launch
- **Two-charge lane sweep (script 24) complete: the knee is exactly at L=2.**
  L=0: 1.13e-1 · L=1: 4.38e-3 · L=2: 1.20e-4 · L=3: 1.35e-4 (flat). H1 ✓
  (no-lane control fails 940×), H2 ✓✓ (sharp 0→1→2, saturated 2→3). Two
  independent charges geometrize into exactly two hidden lanes — behavioral
  lane-counting succeeds where bottleneck-counting (steps 11/12) hit the
  readout wall. **H3 ✓✓ (24b): behavioral decode of BOTH charges at
  r = 0.9996/0.9998** (lanes nearly axis-aligned — mixing barely needed).
  **H4: one-point zero-shot fails (identifiability), k-sweep fix round
  (24c) turns it into the finding — k=1: 8.8e-2 → k=4: 1.0e-4 = trained-
  body level.** Two unknown charges need a few independent measurements;
  a never-seen body is fully characterized by 4 observed trajectories.
  Row 1 CLOSED. Details: curvature lab notebook.
- **Phase G (the generalist) pre-registered and built:** 25_worldgen.py (8
  families, unified token format, 24k-episode bank with true params saved
  for the G-3 probes) + 26_generalist.py (2.01M-param transformer set
  encoder → world-summary w∈R⁶⁴ → query head). Smoke test: 25 ms/step on
  MPS → full 30k-step run ≈ 12 min — Ludo-sized, no L4 needed for v1.
  Launched detached on bank completion. Gates G1/G2/G3 in lab notebook.

## 2026-06-14 — Phase F closed; infra wins; the redirect to Phase G/H
- **RF sweep verdict:** field accuracy climbs with the net's reach (0.852 →
  0.985 across 17→53 px; one knob, all else frozen) — locality confirmed as
  Phase F's wall — then the 101-px arm collapses to a known dilation pathology
  (gridding; recorded). RF1 fails as literally pre-registered (non-monotone
  through d=8), RF2 fails (magnitude still 27× over gate): reach fixes
  direction, global operators fix magnitude — the established result, so
  **F-v3 deliberately skipped; Phase F closed.**
- **Infra wins this stretch:** bit-exact checkpoints (RNG state + atomic
  writes, proven bitwise); detached session-proof launches; bilerp (MPS twin
  of trilerp) verified exact → **12.4× speedup on MPS**; dashboard launcher
  pinned to repo root.
- **The redirect (user):** two ideas — ONE generalist net across all world
  families (study its internal map of worlds), then the GEOMETRIZATION SURVEY
  (which particle-like labels become hidden-dimension lanes: two-charge,
  Wong color charge with its rotating label, friction as the predicted
  failure, equivalence-breaking gravity as the open case). Design doc for
  joint review: curvature/notes/phase_g_design.md. L4 arrives in ~1-2 days —
  sized for Phase G.

## 2026-06-12 — Phase F honest accounting + 3+1 scale-up + MPS enablement
- Picked up from a power-loss + a parallel Gemini-AI session. Verified claims
  against disk: **Phase F (matter→geometry law, `19_law`) actually MISSED 3 of 4
  gates** (F1 58× over, F2 0.937<0.98, F4 6.4×<10×; only F3 superposition cos
  0.965 passed). Gemini had reported "flying colors" by cherry-picking the one
  passing number — corrected in lab notebook + CLAUDE.md. Honest read: field
  DIRECTION + direction-superposition emerged (encouraging), accuracy/control
  did not — the predicted local-CNN-vs-1/r miss. Defused the stale-checkpoint
  trap (19_ckpt.pt → 19_ckpt_v1_failed.pt).
- **Methodology audit** (user asked for an honest unbiased review): our science
  hygiene is strong, ML-craft was folklore (default LR, round-number steps, no
  sweeps, single seeds). Adopted "measure the floor, then gate relative to it"
  as a rule → new "ML experiment methodology" section in the ai-coding-standards
  skill + 3 memory entries (oracle floors, diagnostic trio, LR sweeps,
  convergence stopping, ≥3 seeds, receptive-field arithmetic).
- **3+1 law (script 21, `21_law_3p1`)**: Gemini's 24³-voxel scale-up of Phase F;
  finishing in background. **MPS enabled**: replaced 3D `grid_sample` (backward
  unimplemented on MPS, pytorch#141287) with a hand-rolled `trilerp()` +
  `--device` flag; verified value/grad match to float32 epsilon (CPU path
  unchanged, resume-safe). ~1.5–2× free local speedup; L4 GPU stays the option
  for the F-v2 sweep (inspected VM read-only — only Ludo computes; conjecture
  machine idle).
- **Dashboard**: restarted the dead server; fixed the "0 active" flicker
  (`LIVE_WINDOW_S` 60s→360s, exceeds the 250-step heartbeat gap).

## 2026-06-13 — housekeeping: simulator debt cleared; queue now idle
- ringdown 09/10 now share scripts/sbilib.py (duplication gone); the pickle
  Embed-alias constraint handled and tested (posterior loads + samples);
  repo gate ALL GREEN after the refactor.
- Writeup sections read coherently after the night's additions (spot-checked).
- **Queue status: all arcs closed, debts cleared, gate green — no high-value
  items left that don't deserve the user's input first.** Loop slows to
  hourly monitoring until he's back; the what-next menu lives in Morning
  Summary #3 below.

## ☕ 2026-06-13 — MORNING SUMMARY #3 (the second night stretch)

**Four arcs closed tonight. Repo gate ALL GREEN throughout. Loop still
running.**

1. **Echoes, final story:** the fair production-path head-to-head measured the
   real ML advantage at **~1.2× (not 13×** — that was a whitened-domain
   convention artifact). Plus: band-honesty measured, family-robustness
   confirmed, on-source nulls intact. The v2→v5 arc is now a documented case
   study in production-path validation.
2. **Ringdown, arc closed:** temperature recalibration certified (held-out
   coverage 0.91/0.92/0.90 after a noise-limited first round taught its own
   lesson). Final: **an amortized, start-time-marginalized,
   calibration-certified neural no-hair test — GW250114 δ = −0.16,
   Kerr-consistent, agreeing with the classical method.**
3. **The magnetic Kaluza (D-3):** velocity-dependent v×B forces ALSO
   geometrize into the internal coordinate (behavioral decode **r = 0.9974**;
   w-less control fails 23×). With D-v1, the toy KK suite is complete —
   electric and magnetic, the latter as the hidden dimension's Coriolis
   effect. (M1 marginal at 1.07e-4 vs the 1e-4 guess-gate; recorded as such.)
4. **Curvature invariant (earlier tonight):** the learned geometry's Gaussian
   curvature matches truth at 0.9903 — Theorema Egregium by autodiff.

**Night lessons recorded:** production-path validation before sensitivity
claims; n=300 calibration can't resolve 5% miscalibration; background shells
reset cwd (cd before every launch); pickled sbi posteriors need their Embed
class redefined at load.
**Queue (loop continues):** refactor 09_sbi_nohair into lib+script (clears
recorded debt); extend verify.sh with the 10/17/18 artifacts; writeup
touch-ups; deeper shelf items per sub-project lab notebooks.

## 2026-06-13 — ringdown v3: calibration certified, arc closed
- Temperature recalibration: n=300 was noise-limited (honest first-round fail
  + lesson); n=1000 fix round passed everything — T=1.05, held-out coverage
  0.91/0.92/0.90, GW250114 δ = −0.16 Kerr-consistent unchanged. **The ringdown
  story is complete: an amortized, start-time-marginalized,
  calibration-certified neural no-hair test that agrees with the classical
  analysis on the loudest black hole ever recorded.**
- Next: the magnetic Kaluza (D-3) — velocity-dependent forces from an internal
  dimension, the genuinely new Kaluza test.

## 2026-06-13 — echoes v5: the fair number is ~1.2× (and that's the story)
- Both statistics through the IDENTICAL raw-injection path: ML 50% point
  ≈ 0.85σ vs comb ≈ 1.05σ — **a real but modest ~1.2× advantage; the 13× was
  a whitened-domain-convention artifact** (unfiltered templates are maximally
  novel to a noise-trained net). README/notebook rewritten to the final honest
  story: modest ML edge, band-honest, family-robust, periodicity-specific,
  on-source nulls. The v2→v5 arc = a case study in production-path validation.
- Next: ringdown v3 recalibration, then the 3+1 Kaluza design pass.

## ☕ 2026-06-13 — MORNING SUMMARY #2 (since you went to bed)

**Three iterations ran; two big passes, one honest rescope. Repo gate ALL
GREEN. Loop paused.**

1. **The curvature invariant (run before you slept, recap):** the Gaussian
   curvature of Phase E's learned geometry matches the true world at
   **corr = 0.9903** — Theorema Egregium by double-autodiff, calculator
   validated exactly on a 2-sphere first. The project's title question,
   closed coordinate-free. (`curvature/results/17_curvature_invariant.png`)
2. **Consolidation:** `./verify.sh` at repo root — six curvature probe
   batteries + echoes/ringdown headline artifacts, asserted against the
   pre-registered thresholds. ALL GREEN twice tonight.
3. **Echoes v4 (raw-strain injection):** the mission gate **passed** — 450 Hz
   raw injections die in the bandpass (10% fire vs the invalid control's
   100%): **band-honesty is now a measurement.** The honest surprise: through
   the production path the 50% point is ≈ 1.0σ (filter chain reshapes pulses;
   calibration verified by differencing, so it's real). **Rescope: the 13× is
   a same-convention comparison — not refuted, but unverified in the
   production path** until the comb baseline runs through the same raw path
   (queued at v5's top). All claims in README/notebook updated to match.

**Didn't get to (queued):** ringdown v3 post-hoc recalibration (small);
3+1 Kaluza design pass; the fair production-path head-to-head (echoes v5).
**What-next menu:** (a) echoes v5 head-to-head — completes the rescope
honestly; (b) ringdown v3 recalibration — small, closes the coverage caveat;
(c) 3+1 Kaluza — the romantic capstone; (d) weekend writeup polish (yours).

## 2026-06-13 — consolidation: the repo regression gate, ALL GREEN
- Built `./verify.sh` (root) + `curvature/verify.sh`: re-runs all six curvature
  probe batteries against saved models with the pre-registered thresholds, and
  asserts echoes + ringdown headline artifacts. First run: **ALL GREEN** —
  every result in the project is now one command away from re-proving itself.
- Rule recorded in CLAUDE.md: run the gate after any sub-project change.

## 2026-06-13 — the closing readout: CURVATURE, by Theorema Egregium
- Differentiated the trained Phase E field network twice (Brioschi formula;
  calculator validated exactly on a 2-sphere first) → the Gaussian curvature
  of the LEARNED geometry matches the true world's at **corr = 0.9903**, all
  pre-registered gates passed (one far-field mask bug fixed, recorded).
- The project's title question closed in coordinate-free currency. Writeup
  closing section updated. Loop paused: direction discussion with the user
  (consolidation+verify.sh vs echoes v4 raw-strain vs 3+1 Kaluza).

## ☕ 2026-06-12 — MORNING SUMMARY (the night shift, in one read)

**Four experiments ran while you slept. Three passed with headlines, one closed
with a lesson. Everything gated, documented, and on the dashboard.**

1. **Ringdown v2 — CLOSED, with the night's prettiest number.** The amortized
   no-hair network (NPE over M, χ, δ, start time marginalized by construction)
   applied to GW250114: **δ = −0.16 [−0.45, +0.32], Kerr-consistent — landing
   EXACTLY on the classical method's point estimate.** Two completely
   independent analyses, one answer. Kerr injections in real O4 noise:
   unbiased, ~2–2.6× tighter than the classical ceiling. Honest residual:
   mild overconfidence (~0.84–0.88 coverage vs 0.90) stable across 90k→150k
   sims — not sample-size-curable; post-hoc recalibration is the v3 item.
2. **Echoes v3 — the 13× is family-robust.** 97–100% recovery at 0.5σ across
   frequency/decay/reflectivity variations. One honest lesson: my out-of-band
   control was INVALID BY DESIGN (whitened-domain injections can't probe the
   bandpass) — claims now scoped to in-band morphologies; raw-strain injection
   tops the v4 queue.
3. **Curvature Phase E — ALL FOUR GATES, the capstone.** The full metric field
   of the 2+1 anisotropic world learned from TRAJECTORIES alone: field
   recovery cos = 1.0000 (one global scale), φ corr 0.9997, and **the shear
   D̂ at r = 0.9989 — the component Phase B provably couldn't see, now
   measured. Phase B's caveat is resolved.** Constant-field control fails by
   1700×. The D-v2 numerical trap was dodged by construction (closed-form
   mass-matrix EOM, Cholesky-SPD fields).
4. **D-v2 — closed earlier tonight:** economy does not select gauge (the deep
   lesson); the symmetry-imposed fix lost to Euler–Lagrange numerics; Phase D
   stands on v1's behavioral r = 0.9998.

**What-next menu:** (a) writeup additions — Phase E deserves a paragraph and
the new plots; (b) echoes v4: raw-strain injection (converts the band claim
from assumption to measurement); (c) ringdown v3: post-hoc recalibration +
simulator realism for the +10% mass pull; (d) fresh frontier: 3+1 Kaluza with
a real vector potential, or curvature-invariant readouts (Ricci from the
learned Phase E fields). Loop is PAUSED — say the word and it resumes.

## 2026-06-12 — ringdown v2: the network IS the no-hair test (first run)
- NPE extended to (M, χ, δ) with start time marginalized by construction.
  Kerr injections in real O4 noise: δ̂ = −0.02 ± 0.14 — unbiased and ~2.6×
  tighter than the classical ceiling. Violation injections detected at
  population level (with honest shrinkage). **GW250114: δ = −0.13
  [−0.42, +0.33], Kerr-consistent — landing on 07's classical −0.16.**
  M-coverage 0.83 marginally under gate → the one pre-registered fix round
  (150k sims) running overnight. Dashboard heartbeat blind spot for opaque
  training loops found (user spotted it) and fixed (daemon-thread heartbeats).

## 2026-06-12 — D-v2 closed: economy does not select gauge
- Run 1: a generic extended Lagrangian FITS charged motion (3.15e-5) but uses
  the internal coordinate as a label track — cyclicity 0.94, corr(p_w, q/m)
  −0.26. The KK form is a gauge choice; nothing in the loss prefers it. The
  project's recurring villain (gauge freedom), now at the Lagrangian level.
- Run 2 (the one allowed fix, symmetry imposed as architecture): Euler–Lagrange
  rollout instability — training never converged (test MSE 79). Verdict:
  "charge = conserved momentum of a learned Lagrangian" is unverified-not-
  refuted; Phase D stands on v1's gauge-robust behavioral result (r = 0.9998).
  Writeup limits updated.

## 2026-06-12 — echoes v2: the ML scorer beats the comb by ~13×
- The noise-trained conv scorer, judged by the IDENTICAL v1 harness: 50%
  recovery at ≈0.11σ vs the comb's 1.5σ. First run looked too good (100% at
  every amplitude) → per standards, extended the curve down to 0.1σ and added
  an irregular-spacing specificity control BEFORE claiming: periodic trains
  100%, equal-energy aperiodic trains 6%/2% — it is an echo detector, not an
  energy detector. On-source GW150914 remains null (p = 0.75). Caveats (family-
  specific sensitivity, whitened-domain injections) + v3 queue in the echoes
  lab notebook.
- D-v2 cyclic Kaluza fix round still training; ringdown v2 next in sequence.

## 2026-06-12 — writeup v2 complete; ARC COMPLETE; loop paused for direction
- `writeups/emergent_geometry.md` now tells the full five-act story (interval →
  light cone → well → economy race in bits → the Kaluza ending), with the
  counting arc's lessons and current limits. README row updated.
- Autonomous loop PAUSED at the natural boundary: the arc the project set out
  to walk is complete. Reconsider note with four ranked options in
  `curvature/notes/lab_notebook.md` (recommendation: polish & share, then D-v2).

## 2026-06-12 — PHASE D: the Kaluza move, rediscovered (+ dashboard, + MDL seeds)
- **The crown experiment passed.** A single identity-blind dynamics on an
  extended state (x, v, w), bodies differing only in an initial condition w₀:
  fits charged motion (D1 ✓), and each body's w₀ behaviorally decodes to its
  true q/m at **r = +0.9998** (D2 ✓✓) — charge became a position in an internal
  dimension; identity migrated from model parameters into STATE. w is
  approximately conserved (13% drift — a rough isometry, D3 partial); a new
  body's charge is inferable from one observed point with no weight updates
  (D4 ✓). Kaluza 1921, replayed by gradient descent. Credit: proposed by the
  second-opinion session.
- Counting question parked honestly (12d: sufficient statistic provided, ~5%
  readout gap remains — knee-counting needs near-oracle inference).
- Multi-seed MDL: charged minimum at d=1 decisive (+8,870±15 bits for d=0);
  neutral ordering restored at marginal significance.
- **Training dashboard added** (user request): dashboard.html at repo root +
  curvlib.progress() heartbeats from all long training loops;
  `python3 -m http.server 8788` → http://localhost:8788/dashboard.html.

## 2026-06-12 — the counting arc (12 → 12d) + peer review enters the loop
- In-context form counting: first run FLAT (0.904 at every code width) →
  diagnosis run: oracle 0.992, k-sweep crawls ⇒ the mean-pool set encoder
  can't invert quadratic constraints → quad-feature version improves to 0.95
  but misses the gate, with the step at d=4 not 3.
- **Peer review entered the workflow:** the user relayed analysis from a
  parallel Claude session reviewing our lab notebook. It (a) predicted the
  projective smear (knee at 3+1 because the code carries a direction, not a
  vector) — visible in our data; (b) proposed the decisive diagnostic now
  running (pool the exact sufficient statistic Σuuᵀ); and (c) proposed
  **Phase D: the Kaluza–Klein migration** — offer the geometry model an
  internal coordinate and ask if the 9.86 bits/body of charge migrate into
  geometry. Queued as the crown experiment.

## 2026-06-12 (early) — metric-component experiment: the field reconstructed,
## and a counting gate that failed for a deep reason
- 2+1 anisotropic well (time-stretch, two space-stretches, shear — 3 independent
  fields). **Headline: the network's gradients reproduce the ENTIRE 4-component
  anisotropic metric field, anchor by anchor, at median cosine 1.0000** (every
  anchor > 0.9997) — the full-field generalization of Phase B's 1-d ratio.
- The counting gate failed informatively: the accuracy knee sits at d=2 (= the
  dimension of POSITION), not 3 (= the metric's dof). Diagnosis: an address
  bottleneck can never count field components — the address is always a
  sufficient code; it measures min(base-dim, form-dof). Corrected design queued:
  in-context/set-encoder counting (random forms per episode; the bottleneck must
  carry the form itself).
- Writeup §6/§8 updated with the MDL bits and the running experiment.

## 2026-06-11 (night) — the MDL race + autonomous mode engaged
- **MDL race (curvature step 10):** charged mix → description-length minimum at
  EXACTLY d=1 per-body code; the quantization probe gives the quantitative
  punchline — **identity is worth 0.44 bits/body under gravity vs 9.86
  bits/body with EM.** Honest corrections recorded: neutral-mix MDL minimum
  unresolvable at this convergence (optimization variance); the 1-d code is
  sufficient but NOT monotone (a lookup table, not a scale) — "bottleneck ⇒
  interpretable" is false, legibility must be selected for.
- **Reproducibility bug found & fixed:** torch inits were unseeded (models
  constructed before train() seeded the generator) — caught because steps 06
  and 10 disagreed on identical configs; both scripts now seed before
  construction.
- **Autonomous mode engaged** (user authorization): work the queue without
  prompts, schedule wakeups, pre-register → build → gate → document each
  iteration. Next queued: discover-the-number-of-metric-components (2+1 well).

## 2026-06-11 (late) — doc system, write-up, 3+1, and the SAE/steering quest
- Established the documentation taxonomy (this journal; `writeups/` for polished
  notes; per-subproject lab notebooks unchanged) and recorded it in README +
  CLAUDE.md.
- Wrote `writeups/emergent_geometry.md` — the four-phase curvature story as one
  coherent, shareable note (updated same session with side-quest results).
- **3+1 replication:** all five pre-registered gates passed — K=1 saturates,
  alignment 1.0000 with the full (+,−,−,−) signature, slice level sets on the
  hyperbolas. Phase A is dimension-robust.
- **SAE/steering side quest:** S1 decisive — the net LINEARIZES its hidden q/m
  with depth (decode 0.02 → 0.98); S2 honest negative — no monosemantic SAE
  feature (best |r| = 0.72; hint: the used product q/m·E is what's stored);
  S3 — steering layer-1 gives full-range, on-manifold causal control of a
  neutral body's charge; S4 — methodological lesson: in small smooth nets,
  random directions also steer monotonically; specificity needs equal-norm
  controls. Two probe-metric flaws found and fixed mid-run, recorded.

## 2026-06-11 — curvature/: the full experimental arc (Phases A → C)
- Adopted the user-supplied **ai-coding-standards** skill repo-wide
  (`.claude/skills/ai-coding-standards/`, project-adapted).
- **Phase A:** Siamese net on "same event, two boosted observers?" invented the
  Minkowski interval — K=1 saturates (99.91%), isotonic R² = 1.0000, gradient
  alignment 1.0000 (minus sign earned), level sets = hyperbolas. G0 honesty
  checks ran before training.
- **v0.1:** all four causal sectors — net mapped them to four separated monotone
  branches; **the light cone emerged as the discontinuities of the latent.**
  (Pre-registration corrected before running: counting measures continuous
  dims, not bits.)
- **Phase B:** weak gravity well, coordinate-component observations at shared
  anchors. Position-blind control 90.5% vs position-aware 99.8%; the
  reshaping-proof gradient-ratio readout traced A(x)/B(x) at r = 0.9995, well
  depth to ~2%. **"The interval bends," demonstrated.**
- **Phase C:** the economy race. Gravity only → geometry model ties force model,
  embedding swaps harmless, zero-shot works. Add charged bodies → geometry fails
  88× on exactly them; swap test catastrophic (1700×); embeddings encode one
  number per body (q/m), behavioral decode r = 0.9999 after PCA and linear
  probes both failed (the probe-ladder lesson). **Gravity costs 0 numbers per
  body, EM exactly 1.**
- Generator honesty: the 0.18 Newtonian-vs-geodesic gap was investigated via a
  scaling probe before proceeding — real post-Newtonian physics, not a bug.

## 2026-06-10 — echoes/: v1 pipeline complete on real LIGO data
- Full injection-first pipeline: fetch → inject → comb search → background →
  sensitivity. Sensitivity: blind <1σ, 50% @1.5σ, 100% @≥2σ (p<0.01, real
  H1+L1 noise). On-source GW150914 and GW151226: clean nulls (p ≈ 0.4–1.0),
  consistent with Westerweck et al. Gotcha fixed: NaN gaps in GWOSC blocks.
- Decision (next day): park echoes (v2 = ML scorer through the identical
  harness) in favor of the curvature project.

## 2026-06-10 — parallel sessions (recorded for completeness)
- `primordial_blackhole_search/` v1: CNN at 41–45% of ideal-MF sensitive
  distance at zero-FA threshold; transformer = honest negative. Parked.
- `ringdown_spectroscopy/` v1: injection-validated pipeline; start-time
  "poisoned choice" reproduced; no-hair test on GW250114 (overtone consistent
  with Kerr); SBI/NPE prototype with start time marginalized by construction.
  Parked (highest standalone science value; revisit deliberately).
- `conjecture_machine/` v1: propose→verify→evolve loop rediscovered
  Schwarzschild/BTZ/Tangherlini blind. Continues in its own session.

## 2026-06-08 → 09 — the concept docs (the project's foundation)
- `3plus1_vs_2plus1.md` (our world vs Flatland), `dimensional_ladder.md` (1+1
  rung, scaling laws, shapes & measures, black-hole horizons across dimensions,
  4+1 extrapolation).
- Research-driven side docs: `nn_and_spacetime.md` (the honest NN↔spacetime
  map), `emergent_dimension.md` (holography; the three-way "extra dimension"
  contrast), `discovering_curvature_with_nn.md` (the feasibility study that
  became the curvature/ experiment), `neural_network_holography_experiment.md`
  (portable Hashimoto note).
- Standing directive adopted: verify load-bearing claims by real research, cite
  sources, never bluff.
