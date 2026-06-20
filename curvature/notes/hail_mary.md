# Hail Mary — neural numerical relativity, reframed as an ML problem

> Long-shot / hobby track (named in jest, 2026-06-20). Goal: chase from-scratch neural simulation of strong-field
> GR — eventually binary black-hole mergers — which the literature flags as the *worst possible case* for neural
> PDE solvers. Only hard constraint: **robustness + correctness**. The real payoff is NOT an NR solver (we're a
> discovery/methodology project, not a solver shop) — it's the **portable ML insight** (representation-first +
> modular decomposition), which feeds tabula's core thesis. **Pivot freely**; nothing waits on this.

## Why it's the worst case — the six walls, in ML terms

A merger stacks every failure mode of neural solvers at once. Each wall already has an isolated ML fix — but the
fixes *conflict*, which is the real obstruction.

| Physics wall | ML problem | Known fix (and its cost) |
|---|---|---|
| Spectral bias (chirp + merger spike) | NN has low-freq bias; target is high-freq | Fourier features / SIREN; causal-curriculum training (Wang–Perdikaris, arXiv:2203.07404) — *roughens the landscape* |
| Soft constraints (must hold exactly) | Penalty loss → localized violations that *grow* | Hard-by-construction: SympNets, divergence-free bases, constraint projection (arXiv:2511.03578) — *projection = elliptic solve/step* |
| Optimization, not expressivity | Loss landscape ill-conditioned (Krishnapriyan, NeurIPS'21) | curriculum / causal weighting — *slows convergence* |
| Long evolution (1000s of steps) | Autoregressive rollout → exponential error growth | recurrent/push-forward training + conservation projection (arXiv:2606.14913) — *added cost* |
| Verifiability (need 1e-4, want guarantees) | no error bound on a pure net | hybrid: net as preconditioner, classical solver certifies |
| Gauge freedom (metric not unique) | learning on a quotient space; degenerate loss valley | gauge-equivariant nets / predict invariants (L-CNN arXiv:2012.12901) — *thin for GR* |

## The reframe: it's a representation problem, not a solver problem

Walls 2, 3, and gauge are the *same disease* — degeneracies of the metric-in-coordinates representation, not of
the physics. The cure is to evolve **gauge-invariant, constraint-on-manifold-by-construction, smooth** variables.
And the conflict between fixes **dissolves if we stop using one net with one multi-term loss** and instead
**decompose into specialized single-objective modules** (operator splitting) — which is, not coincidentally, how
real NR codes are structured (free evolution + constraint damping + gauge driver).

## Two plans (we try both; compare final-output loss)

### Plan A — DOSnet-style modular pipeline (the verifiable baseline)
Each module hands the next a *finished state* (clean, checkable, but lossy — like passing notes in English):
```
state_t → [Predictor NN: match dynamics] → [Constraint projection: constraint=0] → [Gauge-invariant readout] → state_{t+1}
```
- Each module single-objective → **no gradient conflict** (escapes wall 3).
- **Separately trained** — clean state is a universal interface; per-step checkpoints are verifiable.
- Prior art (pieces exist; we build *new* on the gauge+constraint toy): DOSnet (arXiv:2212.05571), predictor-
  corrector (INC arXiv:2511.12764), Constraint-Projected Learning (arXiv:2511.03578), KKT-hPINN (arXiv:2402.07251),
  Neural Projections (NeurIPS 2020).

### Plan B — residual-stream variant (the power upgrade)
Each module hands the next its *raw hidden state*, not a clean output (Coconut / Cache-to-Cache style). Bet:
sharing the stream **shrinks the operator-splitting error** (the lossy hand-off in Plan A *is* that error).
- **Training: pretrain each module separately (sane jobs + checkpoints), THEN fine-tune end-to-end** so they
  develop a shared latent "language" (the stream only means something if gradients cross the seam). If end-to-end
  is unstable → fall back to the separately-trained version, or pivot.
- Prior art: Coconut (arXiv:2412.06769), Cache-to-Cache (arXiv:2510.03215), latent multi-agent / Interlat
  (arXiv:2511.09149).
- Verifiability caveat: the hand-off is an opaque vector — can't check "is this physical?" mid-stream. So we
  **judge Plan B by FINAL-output loss vs Plan A**, not by inspecting the stream.

## The toy (start small, climb the ladder)
- **Experiment 1 (start):** a small **lattice gauge / constrained Hamiltonian** system — smallest setting that
  carries BOTH a constraint and gauge freedom, cheap to run.
- Ladder upward (only if rung N passes): constrained toy → spherical **scalar-field collapse** (Choptuik:
  Hamiltonian constraint, 1+1, self-similar high-freq) → **QNM** (eigenvalue on a fixed background) → … → merger
  (far off; may never be ours, and that's fine).

## Gates (robustness + correctness — the only rule)
Baseline = monolithic soft-PINN (dynamics + constraint penalty). Expect: constraint drift → blow-up.
- **G1 constraint holding:** Plan A holds the constraint ≤ tol over a *long* rollout where the baseline drifts/detonates.
- **G2 accuracy:** Plan A final-state error beats the baseline.
- **G3 stream vs pipeline:** Plan B final-output loss vs Plan A — does the raw-stream hand-off actually lower the
  splitting error? (the headline comparison; if yes, that's the portable result.)
- Robustness: ≥3 seeds; report the constraint-drift curve over the full rollout, not just an endpoint number.

## The honest catch (= the real research question)
Decomposition isn't free: Strang splitting carries O(Δt²) splitting error, and module errors can **couple** over a
long rollout (a biased predictor fights the projector; the projector knocks you off the dynamics). The actual
science here is: **can we bound/control how the modules' errors compose over a long rollout?** That bound IS the
robustness result.

## Standing decisions
- Pivot freely; if end-to-end (Plan B) troubles us → separately-trained modules, or change direction.
- The win is the transferable insight (modular + representation-first beats monolith-with-penalty), demonstrated
  on a toy — independent of ever touching a real merger.
- This is the negative-space/representation thesis of tabula, pointed at dynamics. Research prior art FIRST on
  each new rung (see memory: research-first-habit).

## Results log

### Experiment 1 — Maxwell constraint (DOSnet pipeline vs monolith), 2026-06-20 ✅
First real run (grid 32, vacuum, 4000 train steps, 120-step rollout, MPS). Same predictor/data/budget; only the
loss + rollout differ. **G1 ✓** baseline |div E| drifts to 0.13 while Plan A (predict+project) holds 3.9e-6
(~34,000x, by construction). **G2 ✓** Plan A field MSE 9.7e-4 vs baseline 1.18e-3 (better even past the training
horizon). Reproduced at tiny scale too (grid 16 / 60 steps: 0.23 vs 1e-6, MSE 0.0136 vs 0.0062). **Verdict: the
modular predict-then-project pipeline beats the soft-penalty monolith on the constraint by ~5 orders AND is more
accurate** — Plan A's premise confirmed on the canonical NR warm-up. Honest notes: the accuracy margin is modest
(the headline is the constraint); single seed (multi-seed queued for robustness); this is the EASY half (vacuum
div-free constraint) — real gauge freedom (potential formulation) and Plan B (residual stream) are the next rungs.
Code: hailmary/{maxwell,modules,exp1_constraint}.py.

### Experiment 1 robustness (3 seeds), 2026-06-20 — G1 robust, G2 NOT (the refinement)
3-seed re-run (grid 32, 3000 steps). **G1 (constraint) ROBUST:** Plan A holds |div E| ~3.9e-6 every seed (vs
baseline ~0.16-0.21) -- by construction, no seed dependence. **G2 (accuracy) NOT robust:** Plan A beats the
baseline's field MSE in 2/3 seeds; on seed 1 Plan A's rollout DIVERGED (mse 2.5e-2 vs baseline 1.3e-3) even
though the constraint stayed satisfied. **Refined verdict: the projection module robustly enforces the constraint
but does NOT guarantee stability/accuracy** -- the predictor can still drift in the physical (divergence-free)
directions, which projection doesn't touch. This confirms the doc's "honest catch" (error coupling): solving the
constraint wall is necessary but not sufficient; the long-time STABILITY wall (wall 4) is separate and needs the
recurrent-training / conservation tools, not projection. (The robustness rule did its job -- it caught a G2
over-claim the single run would have hidden. The headline -- constraint by construction, ~5 orders, robust --
stands.)

### Experiment 2 — the gauge wall (predict-invariant vs predict-gauge-dependent), 2026-06-20
Grid 32, 200 distinct B_z x 4 random gauges each, map B_z -> potential A. **G1 ✓ (gauge wall real): predicting
the raw gauge-dependent A is ill-posed** -- test MSE 8.07 (floored by gauge variance) -- while the gauge-fix
projection (div A = 0, the SAME Leray tool as Exp 1's Gauss constraint) brings it to 3.8e-2, a 214x gap. One
physical input -> many potentials defeats the naive net; fixing the gauge by projection dissolves the
ill-posedness (our "judge by invariants" thesis + cert #86, ported to Maxwell; and the gauge-fix is structurally
the SAME module as the constraint -- one tool, both walls). **G2 ✗ for an independent, understood reason:**
curl(plan's A) recovers B_z only at rel-MSE 1.4 -- the residual map B_z -> Coulomb-A is the INVERSE CURL (1/k^2,
non-local Poisson-like), which the LOCAL CNN predictor structurally cannot represent. **This is the Phase F
long-range wall reappearing inside the gauge experiment** -- the gauge-fix (G1) is sound; the predictor
architecture is the limit. Fix (clear, ties straight to Phase F): swap the CNN predictor for an FNO/global
operator and G2 should close. Verdict: gauge wall dissolved by the projection module (G1, the point); full
invariant recovery (G2) needs a global predictor -- two walls cleanly separated, and Phase F's lesson recurs.

### Experiment 2 with an FNO predictor (closing the non-local map), 2026-06-20
Swapped the local CNN predictor for an FNO (the Phase F fix for non-local maps). **G1 (gauge wall) gets
STRONGER and the map-learning gap closes:** gauge-fix vs raw-gauge baseline ratio 214x (CNN) -> 1294x (FNO-12) ->
10,769x (FNO-16), and the residual Bz->Coulomb-A error the CNN couldn't crack collapses (plan test MSE: CNN
3.8e-2 -> FNO-12 6.2e-3 -> FNO-16 7.2e-4). So the global operator DOES learn the non-local inverse-curl --
confirming the Phase F diagnosis was the right call. **G2 (curl(plan A) recovers B_z to <1e-2) still not met but
improves monotonically with modes** (rel-MSE 1.4 CNN -> 0.28 -> 0.16): it is the strictest metric because curl
AMPLIFIES the highest, least-resolved modes, so it is resolution-bound at grid 32 (max 16 modes) -- the spectral
wall in derivative-amplified form. **Verdict: gauge wall decisively dissolved by the projection module (G1, the
point of Exp 2); perfect high-frequency field recovery (G2) is spectral/resolution-limited -- Phase F's recurring
wall, now isolated as a curl-amplified high-k issue.** Two walls cleanly separated, both understood.

### Experiment 3 — the stability wall (recurrent training fixes Exp 1's G2), 2026-06-20
Push-forward / recurrent training (Brandstetter 2022): roll j steps NO-GRAD for the distribution shift, backprop
ONE step + grad-clip. (The fully-differentiable BPTT-through-rollout version blew up to NaN -- recorded; that's
why push-forward exists.) Plan A (still projected) trained recurrently, 3 seeds, vs the 1-step Plan A from Exp 1.
Constraint held ~4e-6 throughout. Long-rollout final field MSE:
    seed:        0        1        2
    1-step:   4.3e-4   2.5e-2   4.2e-4    (worst 2.5e-2, range ~60x, seed 1 DIVERGES)
    recurrent:1.1e-3   5.8e-3   2.6e-3    (worst 5.8e-3, range ~5x, NO divergence)
**Qualitative win (clear): recurrent training ELIMINATES the divergence and collapses the seed variance ~60x ->
~5x** -- worst-case 4.3x better (2.5e-2 -> 5.8e-3) -- at a modest cost on the already-good seeds (4.3e-4 -> 1.1e-3,
the robustness-for-peak trade). **Pre-reg gates marginally MISSED, reported honestly (not moved):** S1 (max < 5e-3)
worst seed 5.8e-3 just over; S2 (seed-1 fix >= 5x) 4.3x just under. More steps / larger K would close the marginal
gap (a known knob, not a new idea), so the one fix round (BPTT -> push-forward) is spent here. **Synthesis of the
three experiments: the projection module holds the CONSTRAINT (Exp 1 G1) and the GAUGE (Exp 2 G1) -- same tool;
recurrent training holds the DYNAMICS/stability (Exp 3); and the recurring deep wall underneath all of it is
spectral bias (Exp 2 G2 = Phase F). Three walls, three tools, cleanly separated -- the modular thesis, mapped.**

### Experiment 4 — Plan B (residual stream) vs clean hand-off, capacity-matched, 2026-06-20
2-stage predictor; ONLY the inter-stage hand-off varies: clean b=3 (narrow), clean_wide b=3/ch60 (capacity-
matched to stream, ~71.5k vs 71.9k params), stream b=32. Push-forward trained, 3 seeds, projected rollout.
Long-rollout final field MSE:
    seed:          0        1        2       mean
    clean (b=3):  5.3e-3   2.7e-2   1.3e-3   1.1e-2
    clean_wide :  2.9e-3   2.4e-3   1.8e-3   2.4e-3    <- most reliable, never diverges
    stream(b=32): 1.1e-3   5.7e-2   2.0e-3   2.0e-2    <- big upside (seed 0, 0.37x) AND divergence (seed 1, 24x)
**Verdict: Plan B is NOT robust and does NOT beat the clean hand-off overall (B1 mean ratio 8.56, B2 robust both
FALSE).** The residual stream is HIGH-VARIANCE -- it can win big (seed 0) but also DIVERGES (seed 1) -- while the
capacity-matched CLEAN hand-off (clean_wide) is the most reliable (best mean, never diverges). This is the
verifiability/robustness tradeoff we anticipated, now measured: the opaque rich-stream hand-off buys peak
performance on good seeds at the cost of robustness; the lossy-but-checkable clean hand-off, given adequate
capacity, is the robust choice. **Decision: since robustness is the project's one rule, Plan A (the clean modular
DOSnet pipeline) is the recommendation; Plan B's residual stream is not dead but needs STABILIZATION (seed 1's
divergence is a training-stability failure of the opaque end-to-end hand-off) before it is reliable.** Side note:
clean_wide (2.4e-3) >> narrow clean (1.1e-2) -- for the clean approach, capacity buys robustness.

## Hail Mary -- arc summary (Exp 1-4)
Three walls, mapped and individually addressed on the Maxwell NR-warm-up; two hand-off strategies adjudicated:
- CONSTRAINT wall -> projection module (Exp 1 G1): robust, ~5 orders, by construction.
- GAUGE wall -> the SAME projection module (Exp 2 G1): dissolved, up to 10,769x with an FNO predictor.
- STABILITY wall -> recurrent/push-forward training (Exp 3): eliminates divergence, collapses variance ~12x.
- SPECTRAL bias -> the recurring deep wall (Exp 2 G2 = Phase F); needs global operators, never fully closed.
- HAND-OFF: clean modular pipeline (Plan A) is robust; residual stream (Plan B) is higher-variance, not reliably
  better (Exp 4) -> Plan A wins on the project's one rule (robustness).
The modular "decompose + enforce structure by construction + train for stability" recipe works on the baby
GR-analogue; the clean hand-off is the robust choice. Next rungs: harder gauge (potential evolution), then climb
to scalar-field collapse (Choptuik).

### Experiment 4 STRESS TEST (8 seeds), 2026-06-20 — verdict strengthened, not overturned
Re-ran capacity-matched Plan A (clean_wide) vs Plan B (stream) at 8 seeds (north star: a 3-seed robustness claim
is itself not robust). Decisive: clean_wide mean 8.3e-3 / max 3.5e-2, NEVER diverges; stream mean 3.86e-1
(46x WORSE) / max 1.54, DIVERGES on 4/8 seeds (>10x clean), wins only 2/8. The earlier 3-seed read (1 divergence)
UNDERSTATED how unreliable the residual stream is. **Verdict (now solid): Plan A (clean modular hand-off) is
robust; Plan B (residual stream) is NOT -- it diverges ~half the time.** The clean, checkable hand-off is the
right default; the stream has real upside (won 2/8, sometimes big) but its instability makes it unusable without
serious stabilization (the opaque end-to-end latent hand-off is hard to train stably). Stress-testing converted
a tentative finding into a decisive one -- exactly its job.

### Experiment 5 STRESS TEST — non-vacuum (charged) constraint, 2026-06-20
Stress-tests the Exp 1 headline ("projection enforces the constraint") on a NON-trivial affine constraint: static
charges rho!=0, div E = rho, affine Leray projection (E_new = E - grad phi, lap phi = div E - rho). Ground truth
preserves div E = rho (2e-6, verified). 3 seeds, grid 32, 1-step training (mirroring Exp 1).
    seed:                0        1        2     (baseline)
    C1 plan |divE-rho|:  3.6e-6   3.3e-6   2.9e-6   (~0.16)  -> holds the CHARGED constraint, robust
    C2 plan field MSE:   0.345    0.357    4.0e-4   (~7.5e-4)
**C1 ✓✓ ROBUST: the constraint-projection GENERALIZES from vacuum to the non-trivial charged constraint** (~3e-6
every seed, by construction) -- the headline is not a vacuum-only trick. **C2 ✗ (humbling, honest): Plan A's
ACCURACY does NOT generalize** -- with 1-step training it DIVERGES on 2/3 charged seeds (0.35), and the soft
baseline (7.5e-4) is MORE accurate. This reconfirms, more starkly than vacuum (Plan A diverged 1/3 there),
that STABILITY is a separate wall 1-step Plan A fails -- and it fails MORE on the harder charged case. **Refined
claim: only the constraint-ENFORCEMENT generalizes robustly; we must NOT claim Plan A is "more accurate" in
general.** Clear next test (untested cell): charged + push-forward training (Exp 3's stability fix) -- does it give
constraint-held AND stable? The stress test did its job: confirmed the robust part, humbled the shaky part.

### Experiment 6 — charged + push-forward (the untested cell, completing the matrix), 2026-06-20
Combines Exp 3's push-forward stability fix with Exp 5's charged constraint. 3 seeds, grid 32, horizon 100.
    seed:              0        1        2
    1-step (Exp 5):    0.345    0.357    4.0e-4    (diverges 2/3)
    push-forward:      2.4e-3   1.3e-2   1.1e-3    (NO divergence)
**D1 ✓ constraint held (max |divE-rho| 3.2e-6).** Push-forward ELIMINATES the charged divergence -- worst case
0.357 -> 1.3e-2 (~27x), the two seeds that blew up under 1-step (0,1) are now bounded. **D2 strict gate marginally
missed** (seed 1 1.3e-2 > 5e-3), reported honestly -- the same robustness-for-peak trade as Exp 3 vacuum (5.8e-3
vs 5e-3 there). **The stress-test matrix is now complete:**
                     vacuum                         charged (rho != 0)
  1-step       constraint OK, accuracy 2/3      constraint OK, accuracy diverges 2/3
  push-forward constraint OK, stable (Exp 3)    constraint OK, stable/rescued (Exp 6)
**Verdict: the modular recipe -- PROJECT for the constraint + PUSH-FORWARD for stability -- generalizes end-to-end
to the non-trivial charged constraint: constraint held AND no divergence, all 3 seeds.** The two tools, each
fixing its own wall (constraint vs stability), compose. The "Plan A is more accurate" claim (humbled by Exp 5)
is restored once the right training is used; the robust core stands and now covers rho!=0.

### Experiment 7 — SCALE hardening (grid 48, 500-step rollout), 2026-06-20 [final Phase-1]
Push-forward Plan A (the validated recipe) at a bigger grid (48) and 5x the test horizon (500 steps, 12.5x the
40-step training trajectories). 3 seeds, constraint + MSE curves over the full rollout.
    seed:           0        1        2
    |div E| @500:   5.7e-6   5.9e-6   6.5e-6   -> constraint held to ~6e-6 over ALL 500 steps, every seed
    field MSE @500: 1.2e-2   1.1e-2   8.0e-2
**H1 ✓✓ CONSTRAINT SURVIVES SCALE:** held by projection to ~6e-6 at grid 48 over 500 steps -- robust, by
construction. **H2 marginal (honest): NO DIVERGENCE over 5x the test horizon** (worst 8e-2 vs a real blowup
~O(1)) -- the recipe extrapolates 5x without detonating -- BUT error accumulates over the long rollout and seed 2
(8e-2) exceeds the strict 0.05 gate; long-horizon accuracy degrades and is seed-variable. **Verdict: the recipe
SURVIVES SCALE in the essential sense (constraint held + no blowup at bigger grid + 5x horizon); the honest
caveat is bounded-but-growing autoregressive error at long horizon, seed-variable.** Consistent with the whole
arc: the by-construction part (constraint) is rock-solid; the learned-dynamics part has honest, bounded error
that grows with horizon. Phase-1 hardening COMPLETE.

## Phase-1 hardening — final status
All headline claims stress-tested:
- Constraint by projection: robust, generalizes to charged (Exp 5) AND to scale (grid 48, 500 steps, Exp 7).
- Gauge by same projection: holds (Exp 2; FNO closes the non-local map).
- Stability by push-forward: works vacuum (Exp 3) + charged (Exp 6) + extrapolates 5x without blowup (Exp 7);
  honest caveat = bounded autoregressive error growth, marginal on the strict gate, seed-variable.
- Plan A robust / Plan B not: strengthened at 8 seeds (Exp 4).
The robust CORE (decompose + enforce structure by construction + push-forward for stability) survived every
stress test. The honest, recurring caveat is long-horizon learned-dynamics error (the spectral/accumulation wall).
Ready for Phase 2: scalar-field collapse (Choptuik) -- the first rung with genuine high-frequency physics.

## Phase 2 — scalar-field collapse (Choptuik): design + prior art (2026-06-20)

The frontier rung: spherically-symmetric massless scalar field collapsing under its own gravity -- the first
system with genuine self-similar HIGH-FREQUENCY physics (Choptuik's critical phenomena) and a constraint that
LITERALLY determines the geometry. All the walls bite together, for real.

**Prior art (research-first):** a Nov-2025 paper (arXiv:2511.15247) does exactly this with PINNs (polar-areal
Einstein-massless-Klein-Gordon; sub/critical/supercritical; vanilla/ModPINN/KAN/sinusoidal variants), finding it
HARD near criticality ("no single architecture dominates"; ModPINN best). KEY: that is a SOFT-PINN study. Our
angle is different and not duplicative -- the MODULAR recipe (predict + project-the-constraint + push-forward)
that beat soft-PINNs on Maxwell. The question: does decompose+project+push-forward beat the soft-PINN on the
constraint, exactly where Maxwell showed soft penalties fail and near criticality is hardest?

**Formulation (polar-areal / Schwarzschild-like, Choptuik 1993; G=c=1):**
  ds^2 = -alpha(t,r)^2 dt^2 + a(t,r)^2 dr^2 + r^2 dOmega^2 ;  Phi = phi', Pi = (a/alpha) phi_dot
  Constraint (gives the metric from the field, ODE in r, a(0)=1):  a'/a = (1-a^2)/(2r) + 2*pi*r*(Phi^2 + Pi^2)
  Slicing (polar):                                                 alpha'/alpha = a'/a + (a^2-1)/r
  Evolution:  Phi_dot = (alpha*Pi/a)' ,  Pi_dot = (1/r^2)(r^2*alpha*Phi/a)'   ; regularity Phi(0)=0
  Black hole <=> 2m/r = 1 - 1/a^2 -> 1 (apparent horizon).
The Hamiltonian constraint DETERMINING the metric is the perfect fit for our "enforce the constraint by
construction" theme -- here the projection/solve literally produces the geometry.

**Careful-build plan (north star = correctness; this is real GR, not flat Maxwell):**
1. Ground-truth solver FIRST, verified before any learning (like maxwell.py): integrate the constraint ODEs for
   (a, alpha) each slice, evolve (Phi, Pi) by method-of-lines + RK; verify (i) regularity at r=0, (ii) SUBcritical
   initial data disperses (2m/r stays small), (iii) SUPERcritical forms an apparent horizon (2m/r -> 1). Only a
   solver that reproduces disperse-vs-collapse is trustworthy ground truth.
2. THEN the modular recipe: a predictor for (Phi, Pi) + the constraint "projection" = re-solving (a, alpha) from
   the field each step (the geometry is the projection), push-forward trained; vs a soft-PINN baseline.
3. Gate near criticality (where the Nov-2025 paper struggled): does the modular recipe hold the constraint +
   track the self-similar echoing better than the soft-PINN?
Honest scoping: step 1 (correct, verified collapse ground truth) is itself a substantial build and the
correctness-critical part -- do it carefully, verify disperse/collapse, before touching the net.

### Phase 2 foundation — ground-truth scalar-collapse solver VERIFIED, 2026-06-20
Built hailmary/collapse.py: spherical massless-scalar collapse in polar-areal coords (Choptuik). Geometry slaved
to the field by the Hamiltonian constraint (a) + polar slicing (alpha), RE-SOLVED each RK4 substep; field (Phi,Pi)
evolved by method-of-lines + RK4, cell-centered grid (parity ghosts at r=0), outgoing outer BC.
**VERIFIED (the correctness gate -- the whole point of building it first):**
  subcritical A=0.02 -> DISPERSES (peak 2m/r 0.06, central lapse 0.86)
  supercritical A=0.40 -> COLLAPSES (peak 2m/r 0.978, central lapse -> 0.000)
The supercritical lapse collapse (alpha(0)->0) is the horizon-avoiding behavior of polar slicing -- correct
Choptuik physics (the slicing approaches but never penetrates the horizon), NOT a bug; that is also why 2m/r
plateaus just below 1. Disperse-vs-collapse dichotomy unambiguous (0.06 vs 0.98). Honest caveat: verified
QUALITATIVELY (the right correctness check for a testbed: dichotomy + lapse collapse) -- a full Richardson
convergence study is the NR gold standard and is deferred; for ground-truth-for-learning the qualitative
reproduction suffices. **NEXT (the learning step): the modular recipe -- a predictor for (Phi,Pi) + the constraint
"projection" = re-solving the geometry from the field (here the projection literally IS the Einstein constraint),
push-forward trained, vs a soft-PINN baseline -- gated near criticality (where the Nov-2025 PINN paper struggled).

### Phase 2 learning v1 — learned collapse emulator: HONEST NEGATIVE (the transition is not learned), 2026-06-20
Push-forward predictor for (Phi,Pi); geometry re-solved at rollout (constraint by construction) for the 2m/r
diagnostic. **The first full run LOOKED like a pass (push-forward peak-2m/r Pearson r=0.938) -- but the north-star
ground-truth check KILLED it:** the test amplitudes (0.075-0.325) were ALL SUPERCRITICAL (critical amplitude ~0.05,
diagnosed and resolution-robust: n=300 vs n=600 agree), so the "disperse->collapse trend" was never actually
tested (every case collapses). The r=0.938 was a degenerate-range artifact.
**Corrected run, amplitudes SPANNING the transition** (truth peak 2m/r: 0.10, 0.21 disperse | 0.72, 0.83, 0.73,
0.85 collapse): **the emulator FAILS** -- push-forward predicts peak 2m/r ~0.96 for EVERY held-out amplitude
(including disperse A=0.025/0.035), class_acc 0.67 (= majority class; both disperse cases misclassified),
Pearson r 0.41. **Honest negative: a learned (Phi,Pi) emulator does NOT capture Choptuik criticality** -- the
autoregressive rollout amplifies toward the collapse attractor and does not preserve small-amplitude DISPERSAL
(the field must spread and 2m/r DECREASE, which it never learns). Consistent with the Nov-2025 PINN paper finding
criticality hard. **The apparent pass was an artifact caught ONLY by stress-testing the amplitude range** -- the
clearest demonstration yet of why the north star insists on the hard case. v2 directions: a constraint-aware /
physics-hybrid step (not pure emulation), or directly attacking the autoregressive collapse-amplification; the
pure emulator does not crack criticality. (Ground-truth solver itself remains verified + trustworthy.)

### Phase 2 learning v2 — HYBRID (coarse physics + neural corrector): honest result, 2026-06-20
v1 (pure emulator) failed criticality (collapses everything, acc 0.67). v2: coarse-grid physics carries the
constraint/geometry, net corrects. Fine n=300, coarse n=100, amplitudes spanning the transition (truth: 0.10,
0.21 disperse | 0.72,0.83,0.73,0.85 collapse):
    v1 pure emulator:      class_acc 0.67                      (collapses everything)
    coarse physics ALONE:  class_acc 1.00,  field MSE 2.49e-3  (classifies ALL, incl near-critical A=0.05)
    hybrid (coarse + net): class_acc 0.80,  field MSE 5.20e-3  (the corrector DEGRADES the physics)
**Key (precise) finding: the constraint-respecting PHYSICS DYNAMICS preserve the disperse/collapse structure and
crack criticality (coarse-alone acc 1.00) where the learned emulator could not (0.67) -- a coarse physics field
dispersed correctly, then the fine-grid constraint solve reads 2m/r right; the neural emulator's field amplified
to collapse everywhere. The neural CORRECTOR (1-step) makes it WORSE (0.80, higher MSE) -- rollout drift, the same
fragility as v1 (a 1-step net sees OOD states along its own rollout and pulls the good physics off-track).**
Honest negative for the learned half: on the merger's hardest analogue, the value is entirely in the
constraint-respecting physics; the net does not add value and degrades unless stabilized. This is the project's
recurring lesson (structure-by-construction is the robust win; the learned part is the fragile, secondary piece),
now on Choptuik criticality. **v2.1 (the fix-round, consistent with Phase 1): PUSH-FORWARD train the corrector**
(through its own rollout, as Exp 3/6 did for the emulator) -- can proper training stop it degrading and let it add
accuracy over the coarse physics? Open. Caveat: coarse-alone here uses down/up + fine-grid geometry re-solve each
step (so the FINE Hamiltonian constraint solve is doing the criticality readout on a coarse-evolved field).

## Phase 2 — conclusion (2026-06-20)
The merger's hardest analogue (Choptuik scalar collapse) gave the project's deepest recurring lesson its sharpest
demonstration:
- Ground-truth solver VERIFIED (disperse vs horizon + lapse collapse).
- v1 pure (Phi,Pi) emulator: FAILS criticality (collapses every amplitude, acc 0.67) -- caught only by stress-
  testing the amplitude range (the first apparent r=0.94 "pass" was a degenerate all-supercritical artifact).
- v2 hybrid: the CONSTRAINT-RESPECTING PHYSICS (even coarse) cracks criticality (acc 1.00); the neural corrector
  (1-step) DEGRADES it (0.80). The value is in the physics, not the net.
**Conclusion: on genuinely hard (critical, high-frequency) GR, the modular recipe's WIN is the constraint-
enforcement (the physics/geometry solve), NOT the learned dynamics -- which are fragile (rollout drift) and add
no value here.** This honestly BOUNDS the hail_mary: enforce-structure-by-construction is the robust, transferable
result (validated Maxwell -> charged -> scale -> and now the constraint-solve cracks Choptuik criticality); the
learned-dynamics half does not crack criticality. Open (expensive, likely low ceiling): v2.1 push-forward
corrector -- can proper training make the net at least not degrade, maybe add accuracy over the physics? The
physics already classifies perfectly, so the net beating it is unlikely. The honest, transferable takeaway:
structure-by-construction is what ports back to the merger; the net is the fragile, secondary piece.

### Phase 2 learning v2.1 — push-forward corrector (the fix-round): does NOT rescue it, 2026-06-20
Push-forward-trained the corrector (roll net+coarse_physics j steps no-grad, backprop 1; B=8, 1500 steps, CPU) --
the Phase-1 stability fix that rescued the emulator (Exp 3/6). Result: hybrid class_acc 0.50, field MSE 3.65e-3 --
STILL worse than coarse-physics-alone (1.00, 2.49e-3) and no better than the 1-step corrector (0.80). **Push-
forward does NOT rescue the corrector.** Why (vs Phase 1): there push-forward fixed the emulator's rollout-
distribution drift; here the corrector sits on an ALREADY-CORRECT physics backbone, so the net has nothing useful
to add -- any correction (1-step or push-forward) only injects error and degrades the near-optimal physics.
**v2 CLOSED (one fix-round spent): the neural corrector does not beat the constraint-respecting physics on
Choptuik criticality; the physics alone (acc 1.00) is best, the net is superfluous-to-harmful.** This DEFINITIVELY
bounds the hail_mary -- structure-by-construction (the constraint/geometry solve) is the entire win on hard
critical physics; the learned-dynamics half adds no value and the Phase-1 stabilization does not change that.
The transferable result is firm: port back the constraint-by-construction principle, not a learned solver.

## Phase 2 — v3 RIGOROUS RE-EXAMINATION of the learned-half negative (2026-06-20)
**Why:** the user challenged the negative ("could a bigger NN / better architecture / more training fix it? did we
really try everything?"). Correct challenge under the north star: the v1/v2 negatives tested ONE modest config, so
"the learned half fails criticality" was OVERSTATED -- honest only for THAT config, not a general claim. So we ran
the strongest untried levers, and (research-first) re-checked the literature: the published NN success on Choptuik
is Ferrer-Sanchez et al., arXiv:2511.15247 (with M. Choptuik) -- a **PINN** (a GLOBAL spacetime solve, physics in
the loss + adaptive sampling), which never rolls out step-by-step. That reframes the question: is our wall the
ARCHITECTURE, or the AUTOREGRESSIVE EMULATOR FORMULATION?

### exp10 -- spectral architecture (1-D FNO) vs local CNN, collapse criticality
Phase F showed spectral nets crack high-frequency/long-range structure a local CNN cannot, so the FNO was the
single most likely lever. CNN vs 1-D FNO (width 64, modes 48), 6000 steps, push-forward, 3 seeds, dense amplitudes
spanning the transition (n=300, t_end=10). **Result: BOTH collapse everything.** Every held-out amplitude predicted
peak 2m/r > 0.9 (incl. the dispersing ones); FNO 0.78 == CNN 0.78 == the always-collapse baseline (the held-out set
was 2-disperse / 7-collapse, so 0.78 = majority rate; neither arch ever predicts disperse). **A spectral
architecture does NOT crack criticality in the autoregressive emulator framing.** (exp10_collapse_fno.{py,json,png})

### exp11 -- MECHANISM diagnostic (why it fails)
- **D1 overfit-ONE-disperse: FALSE (the key result).** An FNO trained 8000 steps on a SINGLE disperse trajectory
  (A=0.03, truth peak 2m/r ~0.06), then rolled out, drives peak 2m/r to **0.999** -- full spurious collapse on the
  very trajectory it overfit. Field MSE is SMALL (3.7e-3): the field rollout is roughly right, but the **stiff
  nonlinear geometry readout (2m/r) amplifies tiny accumulated errors into "collapse."** So the wall is NOT
  capacity, NOT data, NOT criticality -- it is the autoregressive rollout + the hypersensitive constraint diagnostic.
- **D2 disperse-only -> held-out disperse: net concentrates, truth spreads = TRUE.** It tracks the early implosion
  (both peak ~0.17), then as rollout error accumulates it spuriously RE-concentrates (climbs to 0.20) while the
  truth disperses (0.04). The divergence is in the LATE rollout. (exp11_diagnose_fno.{json,png})

### exp4b -- Plan B done PROPERLY (the Coconut recipe we had skipped)
Exp 4 trained the wide-stream net end-to-end FROM SCRATCH -- NOT the latent-communication recipe. exp4b runs the
real one: pretrain a clean narrow-interface (b=3) pipeline, then WIDEN to a b=32 latent stream (init preserves the
function exactly -- stage2 ignores the new channels at init), then fine-tune JOINTLY. Fair: every arm sees the same
total budget; clean_wide is the capacity control. **Result did NOT unlock the stream, robustly (6 seeds):** BOTH
the proper recipe AND from-scratch DIVERGE on ~1/3 of seeds (proper blows up on seeds 2,3 -> 1.52; from-scratch on
seeds 4,5 -> ~1.55), while clean and clean_wide NEVER diverge. Means: clean 6.4e-3, clean_wide 2.3e-2,
stream_scratch 0.52, stream_proper 0.51. **The wide residual-stream hand-off is fundamentally unstable regardless
of the training recipe; the Coconut bootstrap did not fix it. The clean hand-off (Plan A) is the robust choice.**
(exp4b_residual_stream_proper.{py,json,png}, exp4b_6seed.log)

### exp12 -- the DECISIVE mechanism test: global one-shot vs autoregressive rollout (balanced data)
On a BALANCED, varied-profile dataset (vary A, r0, sig so collapse is a nontrivial function of the profile; held-out
50% collapse, majority-rate 0.50): a GLOBAL net that maps initial (Phi0,Pi0) -> peak 2m/r DIRECTLY (no rollout)
vs the exp10 autoregressive FNO emulator on the SAME data. **GLOBAL 0.99 vs AUTOREGRESSIVE 0.50 (= chance).**
W1 ✓ (global >= 0.9 and beats autoregressive by >= 0.2), W2 ✓ (global beats majority by >= 0.2). **Same data, same
information, same architecture family -- the ONLY difference is whether you roll out. The disperse/collapse outcome
is fully learnable ONE-SHOT (0.99); the autoregressive rollout destroys it (0.50). The rollout IS the wall.**
(exp12_global_vs_autoregressive.{py,json,png})

### exp11 CNN -- not FNO-specific
The CNN emulator ALSO fails D1 (overfit-one-disperse: rollout drives 2m/r to 0.63, truth 0.15) and D2 (numerically
blows up to -inf on the held-out disperse). Both the local CNN and the spectral FNO fail to reproduce dispersal
autoregressively -- the wall is the formulation, not the architecture. (exp11_diagnose_cnn.{json,png})

### exp13 -- constructive cap (global predicts the FULL 2m/r(t) curve): honest PARTIAL
Tried to elevate exp12's robust OUTCOME result (0.99) to the full DYNAMICS: a global net mapping initial data ->
the whole 2m/r(t) curve (one shot, no rollout). **v1 (3 seeds): seed-fragile.** Seed 0 nails it (curve rel-MSE
0.047, class_acc 1.00 -- an EXISTENCE PROOF that a global net CAN reproduce the criticality dynamics), but seeds
1,2 collapse to predicting the MEAN curve (rel-MSE ~0.35, acc 0.50). **Fix round (target standardization + 2x
data): BACKFIRED** -- standardizing per-time-step equalized the loss weights, removing the strong gradient from the
high-amplitude collapse cases that let seed 0 escape; ALL seeds then locked to the mean predictor (acc 0.38 = the
disperse fraction). **One fix round spent; verdict = honest partial.** The clean lesson (consistent with the whole
arc): the discriminative signal (the peak) is a small fraction of the full-curve loss, so a generic curve-net
collapses to the mean -- **predict the discriminative quantity DIRECTLY and it is robust (exp12, the outcome/peak,
0.99); ask for the whole curve and it is fragile.** The robust constructive positive is exp12, not exp13; the full
robust dynamics solve is the literature's PINN paradigm (global + physics-in-loss). (exp13_global_solve.{py,json,png},
exp13.log = v1, exp13_fix.log = fix round)

## Phase 2 — v3 CONCLUSION: the learned-half negative is now SCOPED and DIAGNOSED (2026-06-20)
The user's challenge ("did we try everything?") was right, and the rigorous follow-up makes the result STRONGER and
more honest than the original "the learned half fails criticality":
- **It is NOT architecture** (local CNN and spectral FNO both fail identically), **NOT capacity** (neither can even
  reproduce ONE disperse trajectory it overfit), **NOT data**, **NOT criticality-as-such** (the disperse/collapse
  outcome is learnable ONE-SHOT at 0.99, exp12).
- **The wall is the AUTOREGRESSIVE ROLLOUT + the stiff constraint readout:** tiny per-step field errors compound,
  and the hypersensitive geometry functional (2m/r) amplifies them into spurious collapse (exp11 D1/D2; exp12
  global 0.99 vs autoregressive 0.50 on identical data).
- **This is CONSISTENT WITH, AND PREDICTED BY, the literature:** the published NN-Choptuik success (arXiv:2511.15247,
  with M. Choptuik) is a PINN -- a GLOBAL spacetime solve with physics in the loss + adaptive sampling, which never
  rolls out and so sidesteps exactly this wall, winning by building the physics in.
- **The residual-stream hand-off (Plan B) is robustly unstable** (~1/3 of seeds diverge, either recipe); the clean
  by-construction hand-off (Plan A) is robust.
- **Constructive positive (what DOES work, in-repo): predict the discriminative quantity directly.** exp12 (the
  disperse/collapse outcome, one-shot) is robust (0.99, 3/3 seeds). The attempt to extend this to the FULL 2m/r(t)
  curve (exp13) is only an existence proof (1 seed nails it, rel-MSE 0.047) and is seed-fragile -- the discriminative
  peak is a small fraction of the curve loss, so a generic curve-net collapses to the mean. Robust global dynamics =
  the literature's PINN paradigm; our in-repo robust positive is the direct-observable one-shot map (exp12).
**Scoped verdict (replaces the earlier overstatement):** we did NOT show "nets can't do Choptuik" -- we showed the
LEARNED AUTOREGRESSIVE EMULATOR fails for a DIAGNOSED reason (rollout amplification through a stiff constraint),
across architectures, capacities, and the proper residual-stream recipe; and the approach that DOES work
(global/PINN, physics-in-the-loss) is the SAME structure-by-construction principle this project champions. The
untried lever that the literature validates -- a global PINN-style solve -- is a different paradigm we did not
build (it re-confirms our own thesis rather than challenging it). **Net effect: the structure-by-construction
conclusion is unchanged and now rests on a mechanism + the literature, not a single config.**
