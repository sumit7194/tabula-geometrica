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
