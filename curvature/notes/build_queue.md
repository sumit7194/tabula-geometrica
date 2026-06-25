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
- [x] **122 · Horizon thermodynamics / S = A/4** DONE 3/3 (S=A/4 slope 0.250 R2 1.0; holographic area>volume; neg specific heat) ⭐ — the project's origin (Bekenstein-Hawking). RESEARCH-FIRST HEAVY:
  find the cleanest learnable toy where entropy ∝ horizon AREA (microstate counting / Hawking / Rindler). Verify it's
  unbuilt (Phase BH did geometry, 112 did info-return; the area-LAW link appears unbuilt). Gates pre-registered after
  research. Highest thematic payoff.
- [x] **123 · Time-dependent geometry → gravitational-wave toy** DONE 3/3 (W1 quadrupole R2 0.993 vs mono+dipole 0.053; W2 no mono/dipole radiation ~1e27x; W3 speed c, 1/r) ⭐ — all learned geometry so far is static. Moving/
  breathing well; toward radiative structure (quadrupole formula). RESEARCH-FIRST. Gates after research.
- [x] **124 · Graph Ollivier-Ricci curvature** DONE 3/3 (O1 bimodal AUC 1.00; O2 Ricci surgery ARI 1.00; O3 control ARI 0.00) -- — curvature-atlas row. Ricci curvature negative on inter-community
  edges / bridges, positive within; Ricci flow detects communities. Web-verify Ollivier-Ricci + Ni et al.
- [x] **125 · J2 spectral dimension + 2D entanglement grid** DONE 3/3 (J2a dim chain 1.11/grid 1.83 vs PCA overcount; J2b grid Procrustes 0.99; J2c geodesic spearman 1.00/0.95) -- — close geometry-from-entanglement loose ends: swap
  PCA→spectral/persistent-homology dimension; recover a 2D grid via spectral embedding. Reuses s32/s42 machinery.
- [x] **126 · Quick wins** ASSESSED (honest): MDL multi-seed (13) ALREADY DONE; H2 (89) RiemannianAdam swap REGRESSED (0.131->0.160/0.462) -> restored original; H2 partial stands (needs Sarkar tree-construction, not a swap -- logged as future, not shipped). From scaling_backlog A.

## PHASE 1b — more separate-angle probes (after the above, as appetite allows)
- [x] **Huygens-tail by dimension (128)** DONE 3/3: 3D sharp (tail 0.00) / 2D tail 0.226, same front speed, 2D tail ~1/sqrt(t^2-r^2) corr 1.00 -- validates dimensional_ladder sec5.
- [x] **curvature-as-bottleneck (129)** DONE 3/3: 1-D bottleneck R2 1.000, latent decodes K r=0.999, minimality + beats blind +0.40.
- [x] **operational observers (130)** DONE 3/3: interval from radar light-timings (Bondi k-calculus), not coordinates;
  K=1 isotonic R2 0.999, clock-noise robust (R2 0.994), invariant is the Doppler-invariant PRODUCT T_s*T_r (CoV 0.000 vs
  euclidean 0.95). Deepens "no fixed reference" (Cert V/111).
- [x] **relativistic regime / rapidity (131)** DONE 3/3 (clean): additive-bottleneck net discovers boosts compose
  additively in RAPIDITY atanh(v) (R1 R2 1.000, R2 psi=atanh |r|1.000, R3 Galilean superluminal 36% + MSE 732x).
- [ ] Discrete/graph worlds (does geometry emerge without a continuum?) · Huygens-tail PINN (2+1 vs 3+1) · Hashimoto
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
