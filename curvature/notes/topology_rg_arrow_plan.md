# Plan: three pokes — topological band theory · emergent dimension from RG · arrow of time

Created 2026-06-24 (evening). User picked all three, to be done one at a time. This doc is executable cold (no chat
context): each poke has motivation, research-first checklist (web-verify BEFORE building), the toy, pre-registered
gates, and ties to existing work. Standard loop: research-first → pre-register gates → build → run → honest gate →
document (JOURNAL + lab_notebook + CLAUDE.md) → add to verify.sh if a saved-gate result → commit. One fix round each.

Order: (1) topological band theory → (2) emergent dimension from RG → (3) arrow of time.

---

## Poke 1 — Topological band theory (SSH winding number, then Chern) — script 117

**Why:** caps the topology/holonomy cluster (AB winding 113 → Berry curvature 54 → grid torus 115/116 → band
topology). A net discovers a QUANTIZED topological invariant of a band structure + the bulk-boundary correspondence.

**Research-first (web-verify):** Su-Schrieffer-Heeger (SSH) model; Bloch Hamiltonian H(k) and the d-vector
d(k)=(d_x,d_y); winding number of d(k) around the origin as k:0→2π = topological invariant (0 trivial / 1 topological);
the gap-closing transition at v=w; chiral symmetry; bulk-boundary correspondence (winding = # of protected zero-energy
edge modes on an open chain). For the 2D extension: Qi-Wu-Zhang / Haldane Chern insulator, Chern number = (1/2π)∫_BZ
Berry curvature = integer.

**Toy:** SSH chain, intracell hopping v, intercell hopping w. H(k)=[[0, v+w e^{-ik}],[v+w e^{+ik},0]];
d(k)=(v+w cos k, w sin k). Winding w(d) = (1/2π)∮ (d_x dd_y − d_y dd_x)/|d|² = 0 if v>w else 1.

**Pre-reg gates (refine after research):**
- B1 LEARNS THE INVARIANT: a net/readout, from d(k) over the BZ, recovers the winding number = INTEGER matching v vs w
  (0 for v>w, 1 for w>v), R²≈1 against the analytic winding.
- B2 QUANTIZED / ROBUST (certificate): deform d(k) by random gap-preserving perturbations (never crossing origin) →
  winding UNCHANGED (integer, Δ=0); a perturbation that closes the gap (crosses origin) is the ONLY way to change it.
- B3 BULK-BOUNDARY: diagonalize a finite OPEN chain → # of zero-energy edge modes = the bulk winding number (0 vs 1).

**Ties:** AB (113, winding holonomy), Berry (54, curvature), grid torus, impossibility-certificate quantization.

---

## Poke 2 — Emergent dimension from coarse-graining / RG (holographic depth=scale) — script 118

**Why:** make the project's emergent_dimension.md executable. Does coarse-graining / RG flow GENERATE an emergent
(scale/radial) dimension? The holographic "depth = scale" idea. Complements J4 (hyperbolic AdS from entanglement) and
J5 (curvature from entanglement) via a REAL-SPACE-RG route instead of entanglement entropy.

**Research-first (web-verify):** real-space / block-spin RG (Kadanoff); RG scale as an emergent radial direction;
MERA = a discrete realization of AdS (Swingle 2012); the emergent dimension is the RG/entanglement scale; the scale
geometry is HYPERBOLIC (AdS-like) at criticality and trivial/flat when gapped (finite correlation length → finite
depth). Hashimoto deep-learning-and-AdS-CFT (depth=emergent dimension in ML). Cross-check against J4's log-law result.

**Toy options (pick the cleanest after research):**
- (a) Real-space RG on a critical chain/2D-Ising: build the coarse-graining tree; the tree depth = RG scale; measure
  the geometry of scale-space (Gromov δ / curvature) → hyperbolic at T=Tc, flat off-criticality.
- (b) A learned coarse-grainer (stacked autoencoder / lattice RG net): show its "depth" tracks the correlation-length
  halving (the RG scale), and the scale-stack metric is AdS-like only at criticality.

**Pre-reg gates (DRAFT — refine after research):**
- R1 DEPTH = SCALE: the coarse-graining hierarchy's depth correlates with log(correlation length) / RG scale.
- R2 HYPERBOLIC ONLY AT CRITICALITY: the scale-space geometry is negatively curved / Gromov-hyperbolic at T=Tc and
  flat/trivial when gapped (finite depth). Quantify vs a flat control.
- R3 EMERGENT DIMENSION ⟺ CRITICAL: the emergent radial dimension exists only when ξ→∞ (criticality), matching J4.

**Risk:** needs the most research to nail a clean, non-circular toy (avoid baking the geometry in). Flagged.

**Ties:** J4 (41, hyperbolic AdS), J5 (42, curvature from entanglement), emergent_dimension.md, It-from-Qubit.

---

## Poke 3 — Arrow of time / fluctuation theorem (entropy production) — script 119

**Why:** extends the friction boundary (70, "universal-but-dissipative does NOT geometrize"). From trajectories alone,
a net discovers IRREVERSIBILITY and entropy production — the second law as the cheapest description distinguishing
forward from reverse. The arrow of time as a learned functional.

**Research-first (web-verify):** Crooks fluctuation theorem P_F(+W)/P_R(−W)=e^{(W−ΔF)/kT}; Jarzynski equality
⟨e^{−W/kT}⟩=e^{−ΔF/kT}; entropy production = log ratio of forward/reverse PATH probabilities = KL divergence between
forward and time-reversed path ensembles; detailed balance (equilibrium → zero entropy production) vs driven/broken.

**Toy:** driven overdamped Langevin system — e.g., a dragged harmonic trap (breathing/translating) or a driven
double well. Generate forward-protocol trajectories and time-reversed ones.

**Pre-reg gates (refine after research):**
- A1 DISCOVER THE ARROW: a learned scalar functional distinguishes forward from reverse trajectories; its value
  matches the analytic entropy production / dissipated work (corr ≈ 1) — the cheapest forward-vs-reverse code IS
  entropy production.
- A2 CROOKS SYMMETRY: the learned work/EP distribution satisfies P(+Σ)/P(−Σ)=e^{Σ} (the fluctuation theorem), and
  Jarzynski ⟨e^{−W}⟩ recovers ΔF.
- A3 CERTIFICATE (reversibility boundary): an equilibrium / detailed-balance (conservative) system has ZERO entropy
  production → forward and reverse are INDISTINGUISHABLE (the net cannot read time's direction). Irreversibility ⟺
  entropy production > 0. Ties to friction (70).

**Ties:** friction (70), the legibility/cheapest-code framing, certificates (84-87/101), time (Cert V 101).

---

## Status tracker
- [x] Poke 1 — topological band theory (117) DONE 3/3: B1 R2 0.999, B2 robust+gap-flip, B3 bulk-boundary 97%
- [x] Poke 2 — emergent dimension from RG (118) DONE 2/3: R1 depth=log2 xi (R2 1.0), R2 scale-inv only critical; R3 hyperbolic = weak instrument in 1D classical -> deferred to J4
- [ ] Poke 3 — arrow of time / fluctuation theorem (119)
