# Build queue — knocking out the backlog (started 2026-06-25)

Ordered execution queue derived from `open_threads_backlog.md` (the full catalog). Strategy: do everything LOCAL +
high-payoff first (the L4 is busy with Ludo); defer compute-bets; consolidation last. Each item: research-first →
pre-register gates in the script docstring → build → run → honest gate → document (JOURNAL + lab_notebook + CLAUDE.md)
→ add to verify.sh if a saved gate → commit. One fix round each. Scripts numbered 120+.

Sister-project note: conjecture_machine ("ansatz machine") is SEPARATE and does NOT use our code (confirmed by their
session). Stay inside /Users/sumit/Github/SpaceTime; never touch their processes (ansatz_status.py :8080,
_weyl_quadrupole.py) or pkill broadly. Our dashboard is :8788. No resource contention (they're CPU/SymPy, we're MPS).

---

## PHASE 1 — local, buildable now (the bulk of the knock-out)
- [x] **120 · 2D Chern number** DONE 3/3 (R2 0.992, round 100%, sweep 0/-1/+1/0, bulk-boundary) -- — cap the topology cluster. QWZ model H(k)=sin kx σx+sin ky σy+(m+cos kx+cos ky)σz;
  Chern C=±1 for 0<|m|<2 (sign=sgn m), 0 for |m|>2; C=(1/2π)∫_BZ Berry curvature. Gates: C1 net recovers C=integer
  matching m; C2 quantized/robust, flips only at gap closing (|m|=0,2); C3 bulk-boundary (#chiral edge modes on a
  strip = |C|). Quick (analytic, like 117). Research-first: QWZ/Haldane Berry curvature + bulk-boundary.
- [x] **121 · Fisher = GR metric (natural gradient)** DONE 3/3 (F1 autodiff=analytic 0.005, F2 covariant path 103x, F3 invariant conv) -- — the cleanest ML↔GR bridge. 2-param Gaussian (μ, log σ); Fisher
  g (g_μμ=1/σ², g_σσ=2/σ²). Gates: F1 autodiff Fisher matches analytic; F2 natural GD is reparameterization-INVARIANT
  (same distribution-space path under a coord change) while ordinary GD is not; F3 geometry corrects the step. Frame:
  Fisher = GR's g, natural gradient = general covariance in ML. From nn_and_spacetime §5. Cheap.
- [ ] **122 · Horizon thermodynamics / S = A/4** ⭐ — the project's origin (Bekenstein-Hawking). RESEARCH-FIRST HEAVY:
  find the cleanest learnable toy where entropy ∝ horizon AREA (microstate counting / Hawking / Rindler). Verify it's
  unbuilt (Phase BH did geometry, 112 did info-return; the area-LAW link appears unbuilt). Gates pre-registered after
  research. Highest thematic payoff.
- [ ] **123 · Time-dependent geometry → gravitational-wave toy** ⭐ — all learned geometry so far is static. Moving/
  breathing well; toward radiative structure (quadrupole formula). RESEARCH-FIRST. Gates after research.
- [ ] **124 · Graph Ollivier-Ricci curvature** — curvature-atlas row. Ricci curvature negative on inter-community
  edges / bridges, positive within; Ricci flow detects communities. Web-verify Ollivier-Ricci + Ni et al.
- [ ] **125 · J2 spectral dimension + 2D entanglement grid** — close geometry-from-entanglement loose ends: swap
  PCA→spectral/persistent-homology dimension; recover a 2D grid via spectral embedding. Reuses s32/s42 machinery.
- [ ] **126 · Quick wins** — Hierarchy H2 with RiemannianAdam (89 stalled at 0.61); MDL multi-seed (13). From
  scaling_backlog A.

## PHASE 1b — more separate-angle probes (after the above, as appetite allows)
- [ ] Discrete/graph worlds (does geometry emerge without a continuum?) · operational observers (noisy clocks/finite
  signaling) · curvature-as-bottleneck · relativistic-regime learning · Huygens-tail PINN (2+1 vs 3+1) · Hashimoto
  depth=bulk · extrapolation-failure probe · communication-game-for-gauge (amortized-protocol reframe).

## PHASE 2 — compute bets (need the L4; defer until it frees from Ludo)
- [ ] Phase F law via FNO (the 1/r long-range wall) · larger G-sym + legibility regularizer · Wong v3 fuller
  observability · 3+1 Kaluza with vector potential · hail-mary global PINN (Choptuik).

## PHASE 3 — consolidation (weekends)
- [ ] Synthesis writeup (J5 + Cert V + 111 + 112 + legibility law + certificate quintet + holonomy cluster + grid
  torus, one shareable narrative) · roadmap Finale 2 (gravity=curvature) + Finale 3 (Kaluza) docs · dimensional_ladder
  open threads (1+1 rung, 4D chirality, diagrams).

## DO NOT re-grind (walls that are results)
D-v2 KK gauge · Choptuik learned-emulator rollout wall · form-counting ceiling · impossibility certificates ·
accuracy↔legibility tension · "bigger is worse for discovery".

---

## Status tracker
(update as we go)
