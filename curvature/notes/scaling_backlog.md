# Scaling / optimization backlog (parked until the L4 VM frees up)

> Written 2026-06-20. The VM is busy with Ludo training; these are the NN optimizations to revisit
> when it's free. Sorted by the capacity-vs-architecture-vs-structure analysis (the honest answer to
> "could a bigger net / more training fix the negatives?"). See JOURNAL 2026-06-20 for the full discussion.

## The framing
Three kinds of negative in this project; only the first is cured by scale:
- **A — capacity / optimization / statistical power**: scale or a better optimizer genuinely helps.
- **B — wrong inductive bias**: a bigger version of the SAME net does nothing; a DIFFERENT architecture fixes it.
- **C — structural / theorem / function-class / ill-conditioning**: nothing fixes it, and that IS the result
  (impossibility certificates, gauge non-uniqueness, polynomial-vs-rational, the b_crit separatrix). Do NOT
  "fix" these — a net that "succeeds" would be a leakage bug.

## A — quick wins (cheap, high-yield, do these first)
1. **Hierarchy H2 (script 89)** — distortion stalled at 0.61 (gate <0.5) on *vanilla Poincaré SGD*. This is an
   optimization limit, not a structural one. Retry with a real Riemannian optimizer (RiemannianAdam, burn-in
   LR, more epochs / geoopt). Expected: 2/3 -> 3/3. ~30 min. This is the cleanest demonstration of the
   capacity-vs-structure distinction (converts an under-optimized null into a pass).
2. **MDL M1 (script 13)** — neutral-mix MDL minimum unresolvable (data-term variance swamps the param term).
   Pure statistical power: average over many more seeds (and/or more trajectories per seed). Should resolve the
   d=0 minimum at significance.
3. **Form-counting ~5% readout gap (scripts 12c/12d)** — needs near-oracle inference. A bigger / better set
   encoder (deeper, attention pooling instead of mean-pool) may close part of it. Lower priority (partly B).

## B — architecture bets (need the L4 compute; "bigger" alone won't help)
4. **Phase F / the law — FNO instead of CNN.** Overfit-one-batch FAILED at 0.047 = a representational wall; the
   1/r long-range magnitude needs a GLOBAL operator. A local CNN is local at any width/depth. Build a Fourier
   Neural Operator (or a global-attention field net) for matter->acceleration-field. Oracle floor 1.2e-4 is
   banked (the gate is feasible). This is the single biggest open architecture bet. (Re-confirmed by Proca
   script 53: locality is the learnability knob.)
5. **Wong dynamic charge Q(t) — orthogonal/Hamiltonian update (the "v3").** A generic recurrent F re-scrambles
   the clean amortized w0 as it evolves (|Q| drift 0.47). Need an update that conserves |Q| BY CONSTRUCTION
   (orthogonal/skew-symmetric generator, or a Hamiltonian/symplectic parameterization). Bigger generic net
   won't conserve it; the structural constraint will. Tests whether STRUCTURE recovers the legible rotation
   (the session-synthesis open thread).
6. **Larger G-sym generalist** — the equivariant cross-attention fix worked but surfaced a real
   accuracy<->legibility tension (clustering 0.82->0.69). A legibility-preserving variant at larger scale
   (more families, more capacity, an explicit legibility regularizer on the stage pool) is worth the compute.
7. **J2 dimension / 2D grid (script 32)** — PCA overcounts on curved manifolds. Swap to a spectral / persistent-
   homology dimension estimator (not a bigger net). Method change, cheap-ish.

## C — do NOT scale (the result is the wall)
- Impossibility certificates (84-87): theorems. - D-v2 KK gauge: loss is gauge-invariant. - 97/95 polynomial-
  vs-rational: function class. - strong-field b_crit (82/83): ill-conditioned separatrix. - accuracy<->legibility
  (G-sym): a genuine trade-off, not a capacity limit.

## The meta-caveat (important for this project specifically)
For a DISCOVERY / interpretability project, bigger is often WORSE for the claim. The thesis is minimal
description length — what structure is FORCED when the net barely fits. Phase A's "K=1 saturates, extra latents
stay empty, the minus sign is earned" is meaningful *because* the net is tiny; a big net that memorizes the
interval weakens "it discovered geometry" into "it fit the data." Measured directly in G-sym: added capacity
bought accuracy and COST legibility (0.82->0.69). So scale the Category-B *architectures* deliberately, but keep
the interpretability probes minimal — don't reflexively scale the discovery nets.
