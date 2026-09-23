# Moonshot queue — planned-but-unbuilt work, plus new proposals, ranked by ambition

Compiled 2026-09-23 at the user's request: everything the docs planned and never built, checked against
the script inventory (several "open" items turned out to be done — the stale-queue failure from this
week), plus new proposals, all informed by a literature sweep. Ranked by the user's criterion:
**high complexity, low odds, biggest impact first** — the moonshots on top, the safe wins at the bottom.

Scoring: Complexity C, Chance of a clean success P, Impact I, each 1-5. **Moonshot score = I x C x (6 - P).**

## Already done elsewhere — dropped from the list (verified, not assumed)
2D Chern (120) · Ollivier-Ricci (124) · orthogonal Wong update (106, 135) · geometry from entanglement
(32, 41, 42, 125) · curvature as bottleneck (129) · operational observers (130) · communication game (133)
· thermodynamic corner (119, 122, 112) · Dirac/spinor (98, 114) · real-data Newton (156) · bumped Kerr in BL
(168, 174) · global PINN paradigm (136-138) · FNO for Phase F (100, partial). **Turing-pattern topology**
dropped as a replication: persistent-homology classification of Turing patterns is published
(Spector, Harrington, Gaffney, arXiv:2409.20491). The Kerr orbit average stays BLOCKED-ON-INPUT.

## The ranked list

| # | task | origin | C | P | I | score |
|---|---|---|---|---|---|---|
| 1 | **New hidden symmetries in deformed black holes** — blind-recover the Papadopoulos-Kokkotas Carter-preserving family (instrument check), then search OUTSIDE it for rank-4 Killing tensors | new | 5 | 1 | 5 | 125 |
| 2 | **Explain Walrus's "murky physics" with the legibility law** — test storage mode (amortized vs free) as the cause of intermittent SAE features in a real physics foundation model | new | 5 | 2 | 5 | 100 |
| 3 | **Embodied agent living in curved spacetime** — does an RL agent's world model contain the metric / curvature invariant? (your original idea #4) | planned | 5 | 2 | 5 | 100 |
| 4 | **Learned time-dependent geometry** — discover a moving / oscillating metric from trajectories (the road to a DISCOVERED gravitational wave) | planned | 4 | 2 | 5 | 80 |
| 5 | **Discover the field law itself** (Phase F) — matter -> field; the FNO fixed locality but F1 sits at ~0.015 for an unknown reason | planned | 4 | 2 | 5 | 80 |
| 6 | **General relativity from real astronomical data** — S2 star's Schwarzschild precession (GRAVITY) or Hulse-Taylor orbital decay, through the §156 pipeline | new | 4 | 2 | 4 | 64 |
| 7 | **Grid cells in curved worlds** — train the §116 grid model on a sphere / hyperbolic plane; does the module stay a torus? | new | 4 | 3 | 4 | 48 |
| 8 | **Legibility -> DEPLOYMENT** — does amortization predict causal USE, not just decodability? (our law x "The Objective Decides" interchange metric) | new | 3 | 3 | 5 | 45 |
| 9 | **Kepler -> Newton transformers, read with our instruments** — is "temporal locality" working through amortization? does emit-or-certify find E, L in the Newtonian model and nothing in the curve-fitter? | new | 3 | 3 | 5 | 45 |
| 10 | **Does an LLM hold a light cone?** — probe an open LLM for causal / Minkowski structure in how it represents events | new | 3 | 1 | 3 | 45 |
| 11 | **3+1 Kaluza-Klein with a vector potential** — the charge->mass->axion trilogy in full 3+1 | planned | 4 | 3 | 3 | 36 |
| 12 | **Kaluza-Klein structural form via stabilized LNNs + gauge-invariant readout** — closes D-v2's "unverified, not refuted" | planned | 3 | 3 | 4 | 36 |
| 13 | **Larger symmetry-respecting generalist with a legibility regularizer** — resolve the accuracy<->legibility tension (GPU) | planned | 4 | 3 | 3 | 36 |
| 14 | **A public discoverability benchmark** — package the 5-cell detector + certificate standard as a suite that AI Poincare / NGCL / PySR can be run against | new | 3 | 4 | 4 | 24 |
| 15 | **Hashimoto depth-as-bulk, reframed** — which bulk features are IDENTIFIABLE vs gauge? (the field is mature; plain replication adds little) | planned | 3 | 4 | 2 | 12 → 18 with the gauge angle |
| 16 | **Separated-pair screen on ansatz's real deformed-Kerr catalogue** — bring today's §192 result to the real metrics | new | 3 | 4 | 3 | 18 |
| 17 | **Full-scale Choptuik PINN** — the published code is on Zenodo; our 0.36 -> their accuracy is compute, not idea | planned | 3 | 3 | 2 | 18 |
| 18 | **Stress-test NGCL with our certificate standard** — planted-nuisance (C4), rational/transcendental invariants, near-parallel conserved directions | new | 2 | 4 | 3 | 12 |
| 19 | **C-anomaly follow-ups + retrofit the scored-direction readout** (650x more stable) into the screen | planned | 2 | 4 | 3 | 12 |
| 20 | **Grid torus at the reference's full scale** (stable per-cell grids) | planned | 2 | 3 | 2 | 12 |
| 21 | **Synthesis writeup** — one shareable story across the last three months | planned | 2 | 5 | 4 | 8 |
| 22 | **Dimensional-ladder threads** — 1+1 table, 4D chirality, diagrams | planned | 1 | 5 | 2 | 2 |

## What the research changed (per item)

- **#1** — Papadopoulos & Kokkotas already give the most general Carter-preserving Kerr deformation family (three free
  radial functions; arXiv:1807.08594; see also GRG 2021 invariant separability criterion). So recovering it is an
  instrument check, not a discovery. The moonshot is the OTHER side: "the Carter symmetry is very fragile" and
  whether higher-rank (rank-4) irreducible Killing tensors exist in deformed Kerr is actively open
  (arXiv:2508.20191; irreducible-KT work arXiv:2504.18287). Our §167/§178 degree ladder is exactly the instrument.
  Most likely outcome: a certified "none below degree N" on a new family — still a real, citable null.
- **#2** — Walrus (1.3B, Polymathic, arXiv:2511.15684) reproduces continuum physics but its SAE features are
  "intermittent" and do not map onto physical decompositions (arXiv:2606.11657). Steerable directions do exist
  (arXiv:2511.20798). Our §139 says free storage -> superposed, amortized -> monosemantic. Nobody has tested storage
  mode as a CAUSE. Needs a big model and SAE training.
- **#3** — RL agents do build spatial / cognitive-map representations (arXiv:2504.11419; hyperbolic deep RL
  arXiv:2210.01542 puts hyperbolic geometry in the LATENT space). No one we found places an agent inside a
  physically curved world and asks whether its world model holds the curvature invariant. Uses AlphaLudo muscle.
- **#4** — Stabilized LNNs recover a static AdS4 metric from geodesics (arXiv:2601.12519, Jan 2026). Nothing found
  that learns a TIME-DEPENDENT metric from trajectories.
- **#5** — Lemos et al. rediscovered Newton's pairwise force law from real solar-system data (arXiv:2202.02306);
  a continuum FIELD law from matter density is a harder, still-open version.
- **#6** — S2's Schwarzschild precession is detected at ~10 sigma (A&A 2020, GRAVITY); Hulse-Taylor decay matches the
  quadrupole formula to 0.997 +/- 0.002. No ML rediscovery found. Risk: data scarcity (one pericentre for S2).
- **#7** — Theory predicts grid cells can tile hyperbolic surfaces (2015 work); conformal-isometry grid models exist
  (arXiv:2405.16865). We found no emergence test of grid topology in curved environments.
- **#8** — "The Objective Decides" (arXiv:2607.03728, Jul 2026): invariants can be linearly decodable (R^2 ~ 1) yet
  causally inert; interchange-based deployment predicts OOD accuracy at r = +0.97 where decodability fails. Our
  legibility law is a DECODABILITY law. Whether it extends to deployment is untested either way.
- **#9** — Vafa et al. (ICML 2025, arXiv:2507.06952): orbit-trained foundation models predict well but do not apply
  Newtonian mechanics. Follow-up (arXiv:2602.06923, Feb 2026): temporal locality turns a curve-fitter into a
  Newtonian. PhyIP (arXiv:2602.12218): fine-tuning collapses latent physics (rho ~ 0.05) that frozen linear probes
  recover (rho > 0.9). A shared public benchmark we can contribute to directly.
- **#10** — LLMs linearly encode space and time (Gurnee & Tegmark 2023; arXiv:2506.02996). Nothing found on causal /
  light-cone structure. Speculative; low odds.
- **#12** — The stabilized-LNN paper does not address gauge / coordinate non-uniqueness of the recovered metric —
  exactly what D-v2 hit ("economy does not select gauge"). Our gauge-invariant readouts fill that gap.
- **#15** — Holographic deep learning is a mature field (Hashimoto 2018 -> tabletop-QG 2024 arXiv:2411.16052 -> 2025
  review arXiv:2511.22522). Worth doing only with the identifiability / gauge angle.
- **#17** — Ferrer-Sanchez, ..., Choptuik (arXiv:2511.15247, MLST March 2026) with code on Zenodo (record 18687036).
- **#18** — NGCL (arXiv:2603.20474, Mar 2026) reports zero false discoveries and outputs "no law" on invariant-free
  systems, but does not test rational/transcendental function classes or planted per-realization nuisance
  constants — the two traps our certificate standard (§166) was built around.
