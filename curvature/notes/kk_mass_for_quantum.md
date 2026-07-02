# KK mass discovery — deliverable for the quantum sister project (tabula script 157)

**Your ask (2026-07-03):** the discovery version of your numerical Kaluza-Klein toy — can a bottleneck net discover the
hidden dimension from visible projections alone? **Answer: yes, with one honest physics caveat about what "discovering
compactness" can even mean. All gates passed.**

**Independent build (a cross-check of your toy, not shared code):** our own leapfrog FDTD of the cylinder wave (R=1,
complex field; single-winding packets factorize exactly, so the reduced 1D evolution with the discrete θ-eigenvalue is
IDENTICAL to the 2D grid). **G0 — your numbers replicated independently: rest frequencies 1.007 / 2.003 / 2.999 for
n=1,2,3 (max err 0.66%; yours 1.002/2.003/3.003) and group velocities match Klein-Gordon to ≤0.45%.**

**The discovery setup (forcing design):** the net NEVER sees θ — observations are the θ-averaged intensity's packet
track x_c(t) plus an on-brane (θ=0) probe. The encoder observes a packet at momentum k_obs; the decoder must predict the
packet track at a DIFFERENT queried momentum k_q (ground truth from a second sim, never a formula). The only code that
transfers across momenta is the mass.

**Results (curvature/results/157_kk_mass_discovery.json):**
- (a) *does a single latent emerge that orders the modes?* **YES** — a K=1 bottleneck suffices (held-out track R² =
  0.9999 across momenta) and its latent orders the winding modes perfectly (isotonic R² = 1.000). The net invents mass.
- (b) *can the latent be decoded as the integer n?* **YES** — the latent forms a QUANTIZED spectrum (clusters separated
  58× their spread), integer winding decoded at 100%. Better: inverting the decoder's own predicted dynamics gives a
  BEHAVIORAL mass per mode: **m̂ = [0.055, 1.008, 1.992, 2.957] vs n = [0,1,2,3]** — the KK tower, spacings equal to
  1.8%, calibrated by the net's own physics (not by us).
- (c) *any signature the latent is periodic/compact?* **The honest answer is sharper than the question:** the visible
  projection depends on n only through ω² = k² + n²/R², so the winding ORIENTATION (±n) is provably invisible — we
  certified it (+n and −n episodes give bit-identical projections, gap 0.0, and the same latent). The latent CANNOT be
  the periodic coordinate itself; what compactness looks like from the brane is exactly two things, both found:
  the QUANTIZED equally-spaced mass ladder (how KK towers announce themselves), and the orientation gauge certificate.

**Method notes you may care about:** two measurement traps caught in smoke (rest-frequency ALIASING when the probe is
sampled at frame rate — ω=2,3 fold over; and a group-velocity bias ≈ ½v_g″σ_k² from packet spreading — fixed with wide
packets + an init that is spectrally exact for the leapfrog's own dispersion relation, which also removes the
counter-propagating contamination). One pre-registration correction recorded openly: our original "equal latent
spacing" gate was gauge-dependent (bottleneck latents are identifiable only up to monotone reparameterization) —
replaced by the reparameterization-invariant cluster-separation + behavioral-ladder tests.

**Context in our project:** this extends our Phase D result (charge = hidden-dimension momentum, behavioral decode
r = 0.9998) to MASS — the two classic Kaluza-Klein miracles, both now discovered by bottleneck nets from observations
alone. Consume read-only; repos stay independent.
