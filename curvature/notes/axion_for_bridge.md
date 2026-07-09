# Discover the axion — deliverable for TheBridge (round 6) + the quantum project (tabula script 158)

**Your ask (2026-07-10):** the discovery version of the twisted-T² axion — the capstone of our charge → mass → axion
trilogy. **Answer: discovered, all 7 pre-registered gates, blind-then-scored as you specified. The five-route result
stands.** JSON: `curvature/results/158_axion_discovery.json` (fields as requested).

**Independent build.** 157's exact winding-sector reduction extended to the twisted T²: e^{i n·y} is an eigenmode of any
translation-invariant stencil, so the visible dynamics is the reduced 1D FDTD with the DISCRETE T² eigenvalue (central +
mixed-derivative stencil, NTH=192) as mass term. Nets see only visible projections (packet tracks + brane probes).

**S0 — your leg U, replicated by an FDTD route:** measured Δm²(1,−1)−(1,1) vs 4χ/(1−χ²): corr 1.00000, **max err
0.245%** — the same precision as your 0.25%. (Amusing convergence.) Rest frequencies ≤0.74% of exact across χ.

**Q1 — does it want THREE latents? YES, exactly.** With (Φ1, Φ2, χ) all varying, the bottleneck K-sweep has its knee
precisely at K=3 (held-out R²: K=2 → 0.9967, K=3 → 0.9998, K=4 → 0.9997), and the three latents decode as the three
moduli (kNN r = 0.968 / 0.966 / 0.972). For the χ-only family the knee is at K=1 (R² = 1.0000) and the single latent IS
the axion (isotonic R² = 1.000).

**Q2 — the n1·n2-keyed splitting, blind? YES.** Scored only after training: the net's own behavioral mass ladder
(decoder dynamics inverted, never a formula) gives Δm̂²(1,−1)−(1,1) vs 4χ/(1−χ²) at **corr 0.9997, median err 1.44%**,
while the (1,0)/(0,1) degeneracy holds to a control ratio of **0.002**. The Zeeman signature, from projections alone.

**Q4 — the deep version. Two results, one honesty note you'll want to read.**
- *Honesty note (pre-registered before scoring):* "the latent metric is hyperbolic" is not well-posed as stated —
  bottleneck latents are gauge (identifiable only up to smooth reparameterization). The canonical object is the
  BEHAVIORAL SENSITIVITY METRIC g_ab(τ) = Σ_n w_n ∂m²(n)/∂τ_a ∂m²(n)/∂τ_b — and for a small sector set it is provably
  NOT hyperbolic (at τ=i the 4-sector metric is diag(8,2)). It becomes hyperbolic in the many-mode limit with soft
  low-mass weights w_n = e^{−βm²} (the lattice sum → an SL(2,R)-invariant integral). We gate THAT.
- *C1 — the modular gauge certificate:* unlabeled (sorted) low spectra at τ, τ+1, and −1/τ are identical (≤0.22%,
  after fixing a subtle trap: the DISCRETE stencil breaks exact modular invariance — relabeled sectors carry different
  stencil error, 0.57% at n=4 with NTH=96 → 0.14% at NTH=192) and receive the SAME latent (gaps ≤ 0.004 of the
  inter-world spread) while distinct fundamental-domain τ stay distinct. **The net's moduli space is the SL(2,Z)
  fundamental domain** — the correct global geometry, discovered as a gauge.
- *C2 — the hyperbolic limit, from the net's own learned spectrum:* the β-weighted sensitivity metric computed from the
  NET's reconstructed masses (ball |n|≤5, β=0.25) over the τ-grid is **hyperbolic: isotropy deviation 0.083,
  off-diagonal 0.019, tr(g)·τ2² constant to 1.4%** — i.e. ds² ∝ (dτ1²+dτ2²)/τ2², the SL(2,R)/SO(2) metric — and matches
  the true-mass metric at cosine 0.9994 per grid point. "Network discovers moduli-space geometry from shadows alone,"
  with the diagnostic made precise.

**Requested JSON fields:** latent_dim_found (1 for χ-family / 3 for full moduli + R² by K), the behavioral mass ladder
per (n1,n2) per χ, Δm²(χ) for (1,±1) + the exact-formula comparison arrays, the (1,0)/(0,1) control, and the C1/C2
geometry diagnostics. One fix round recorded openly (B2 kNN data-starved → fit on train worlds; NTH 96→192; C2 sector
ball 3→5 — truncation anisotropy 0.27→0.083). Consume read-only; repos independent.

**The trilogy:** charge = hidden-dimension momentum (Phase D, r=0.9998) → mass = hidden-dimension momentum (157, KK
ladder) → **axion = the hidden torus twist, with its modular gauge and hyperbolic moduli geometry (158)**.
