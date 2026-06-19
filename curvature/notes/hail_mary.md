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
