# Pre-registration — §194: orbit-manifold dimension as an independent regular/chaotic classifier for TS δ=2

*Written 2026-10-11, at the user's request through The Bridge. **Prepared, not run.** Execution waits for The Bridge
to report free Mac cores. The Kerr pilot (G0) is the first gate. No pilot has been run.*

## What this is, and what it is NOT

An "AI Poincaré"-style count of conserved quantities (Liu & Tegmark, arXiv:2011.04698), done per orbit. Each orbit
is a point cloud in the reduced phase space (x, y, p_x, p_y) at fixed (E, L, μ), and the count comes from that
cloud's local dimension d:
- d = 2 means the orbit fills a 2-torus. That gives **count 2** (H plus a local invariant): **REGULAR**.
- d = 3 means it fills a 3-D region of the energy shell. That gives **count 1** (H only): **CHAOTIC**.

**It is NOT an integrability test.** Regular orbits of a non-integrable system also lie on (KAM) tori and read
count 2. So "TS far field reads 2" is expected either way. That question is settled anyway: ansatz §149 found no
Killing tensor up to valence 10, and quantum's Morales–Ramis/Ziglin result shows TS is not integrable.

**What it IS:** an **independent-method replication** of ansatz §150, which found confirmed chaos in thin, sticky
layers at the survive/plunge boundary in every separatrix-distance bin, against none for Kerr. The instrument is
different (orbit geometry, not frequency drift or stretching) and so is the code. We read §150's level grid, so the
two can be compared; we did **not** read its per-orbit lists.

## Systems and units

These are the §193 objects, through the same loaders:
- **TS δ=2** at (p, q) = (3/5, 4/5) and (4/5, 3/5): ansatz's sealed-package metric, L0-verified in §193.
- **Kerr**, matched in J/m² (a = −q in the BL sign convention). This is the negative control: integrable, so 0
  chaotic orbits.
- **ZV δ=2.** This is the thin-layer positive control: §150 re-found a ZV layer at 3 of 5 levels.
- **Hénon–Heiles** at E = 0.1657 (just below the escape energy 1/6; mostly chaotic) and E = 1/12 (mostly regular). This is the classifier's
  calibration, against a twin-trajectory Lyapunov reference.

Units: m = 1; timelike geodesics, H = −1/2.

## Levels

- **Energies:** E ∈ {0.95, 0.97}, as in §150.
- **Senses:** prograde and retrograde.
- **Separatrix distance:** ε = (|L| − L_sep)/L_sep ∈ {−0.02, −0.01, −0.005, +0.005, +0.02}. Negative ε is an *open*
  level, where the outer region connects to the plunge. Positive ε is a closed pocket near the separatrix.
- **L_sep**, per spacetime, energy and sense, is the smallest |L| at which the equatorial outer pocket separates
  from the inner plunge region. It is found by bisection on the §193 equatorial-interval routine, from the
  potential alone.
- Kerr and TS are matched by ε against **their own** L_sep, as in §150.
- **Far field**, expected regular:
  - Dubeibe's level, E = 0.94, L = −3.12 (p = 4/5 only; §150 confirms a closed pocket there);
  - the §193 shared shell (0.97, −3.8), both p.
- **ZV:** the same E × ε grid. It is static, so there is one sense.

## Seeding and integration

- **Two-stage seeding per level.** This is §150's lesson: its uniform-seeded design v1 missed the ZV layer.
  - Stage 1: 200 equatorial seeds (y = 0, p_x = 0, p_y > 0 from the shell), uniform in r over the allowed equatorial
    region (r ≥ 3.5m).
  - Stage 2: 100 dense seeds inside each of the first 3 survive/plunge transitions found in stage 1, meaning
    adjacent seeds whose fates differ.
- **Integrator:** the vectorized fixed-step RK4 validated in §193, at dt = 0.05; the G0 pilot may set it to 0.025.
  - Window: T = 10⁴ τ, stride 10, giving 2×10⁴ samples per surviving orbit.
  - **PLUNGED** means r_like < 3m or a non-finite state. The plunge time is recorded and the orbit is frozen there.
  - An orbit whose H drift exceeds 1e-9 is DROPPED. The dropped fraction is reported per system, because
    near-boundary drops could bias the result.
- **Twin trajectory**, for the secondary classifier only: δ0 = 1e-8 in p_x, renormalized every 10 τ, giving a
  finite-time Lyapunov exponent λ_T.

## Classifier (primary): local-PCA curvature scaling

The per-orbit samples are standardized. The method:
1. Take 100 random anchors.
2. Find each anchor's k nearest neighbours for k ∈ {20, 40, 80, 160}, **excluding temporal neighbours** within a
   Theiler window of W = 200 samples.
3. Take the local covariance eigenvalues λ1 ≥ … ≥ λ4.
4. Fit the slope s_j of log λ_j against log r_k, where r_k is the mean neighbour distance.

The reasoning: on a 2-torus, λ3 comes only from curvature, so it scales as r⁴ (s3 ≈ 4). In a 3-D chaotic fill,
λ3 ∝ r² (s3 ≈ 2). λ4 is an internal control, since the energy shell itself is 3-D: s4 ≈ 4 for every orbit.

| per-orbit verdict | rule (median s3 over anchors) |
|---|---|
| REGULAR (count 2) | s3 ≥ 3.4 |
| CHAOTIC (count 1) | s3 ≤ 2.6 |
| ABSTAIN | anything else; also any orbit with s4 < 3.0 (the internal control failed) |

- **Plunged orbits** are classified only if they lived ≥ T/4. They are reported separately as STICKY-then-PLUNGED
  with their dimension verdict.
- **Time dependence:** each survivor is also classified on [0, T/4] and [0, T/2], so sticky orbits that look
  regular early are visible.

## Gates, in order. A failure stops the run, and TS is not read.

- **G0 — the Kerr pilot, which is the first gate.** Kerr p = 4/5, E = 0.97, prograde, ε ∈ {−0.01, +0.005}.
  1. *Integrator:* the maximum relative Carter drift over the window is ≤ 1e-8 for survivors, at the chosen dt.
  2. *Classifier:* ≥ 98% of survivors are REGULAR, 0 are CHAOTIC, and ABSTAIN is ≤ 2%.
  3. *Robustness*, on a 20-orbit subset: classifications are ≥ 95% unchanged under dt/2, W × 2, and the k-set
     shifted to {40, …, 320}.
- **G1 — calibration and positive control.**
  1. *Hénon–Heiles:* where the twin-trajectory λ is unambiguous (λ_T > 5× or < 0.2× the E = 1/12 median), the
     primary classifier agrees on ≥ 90% of orbits, at both energies.
  2. *ZV near-boundary:* ≥ 1 CHAOTIC orbit is found at ≥ 2 of the 5 ε levels. If this fails, the design is blind to
     thin layers. TS **presence** can still be reported, but no TS **absence** statement is allowed.
- **G2 — TS readout**, issued only after G0 and G1. Per (p, E, sense, ε), we report: survivors, plunged,
  STICKY-then-PLUNGED, the REGULAR/CHAOTIC/ABSTAIN counts, the dropped fraction, and the twin-λ agreement.

## Pre-registered predictions for TS (G2). Each is checked; none is assumed.

- **P1 — Kerr:** 0 CHAOTIC among survivors at every level. A Kerr CHAOTIC verdict is an instrument failure, and the
  rows are reported.
- **P2 — far field:** TS at Dubeibe's level and at the §193 shell has ≤ 1% CHAOTIC (regular, as Dubeibe saw).
- **P3 — near-boundary TS:** ≥ 1 CHAOTIC or STICKY-then-PLUNGED-chaotic orbit in ≥ half of the ε bins, at both p.
  Kerr has 0 in the same bins.
- **P4 — trend:** TS's chaotic fraction does not decrease as |ε| shrinks toward the separatrix. This is reported as
  a Spearman correlation with sign, not gated.

## Scope

- Numerical. It covers only bound and sticky geodesics on the listed levels, equatorial seeds with p_x = 0, and
  the window T.
- A REGULAR verdict means "a 2-D orbit closure within T", not "integrable".
- Vacuum is inherited from ansatz's Schwartz–Zippel check.
- Ring singularity: orbits are held at r ≥ 3m, as in §193.

## Resources (revised from the 10-11 estimate, because of the dense seeding)

- About 100 levels and ~20k orbits, with twins.
- Single core: ~11–12 h. Four workers: ~3 h.
- About 0.5–1 GB per worker, so ~3–4 GB at 4 workers.
- A halved variant is available if the Mac stays tight: 100 + 50 seeds, ~1.5 h on 4 workers.
- Runs only when The Bridge reports free cores. The G0 pilot (Kerr, 2 levels) costs ~10–20 min on 1 core.
