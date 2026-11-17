# §200 — Does the measured tangle produce chaos? Escape-time uncertainty + MEGNO (pre-registration, 2026-11-17)

Item 1 of the go relayed by The Bridge from Sumit, 2026-11-17 (slot: 2 cores, < 2 GB, ~3 h, unattended allowed).
Written and committed BEFORE the code. Tag: **macOS 27.2** (regression spot check 72aee06, 4/4 identical).

## Question
§199/§199b measured a transversal homoclinic intersection (a tangle) at TS δ=2, p = 3/5, on the OPEN levels
ε ∈ {−0.003, −0.01, −0.03}. §196's MEGNO saw 0/360 chaotic orbits on open levels. Does the tangle produce
observable chaos, i.e. a chaotic saddle that orbits pass through transiently before plunging? Or is it real but
invisible to the instruments used so far?

## Instrument 1 (PRIMARY): the uncertainty exponent of the escape-count function
Research-first (2026-11-17): in open Hamiltonian systems a chaotic saddle makes the escape-time function singular
on a fractal set. That structure is invariant under coordinate changes (Fernández, López, Seoane & Sanjuán 2020,
arXiv:2003.05265) and is the classic signature in black-hole scattering (Aguirregabiria 1996, gr-qc/9604032).
- **Seeds:** a segment on the section y = 0 (p_y > 0) along the p_x = 0 line, centred on §199's primary symmetric
  homoclinic point x_h, half-width 2% of x_h. It crosses W^u ∩ W^s at x_h.
- **Outcome:** n(x0) = the number of upward section crossings before the orbit plunges (r below §196's r_cut), capped
  at N_cap = 300 returns (capped orbits are counted and reported).
- **Uncertainty fraction:** f(δ) = the fraction of 2,000 random base points x0 on the segment with n(x0) ≠ n(x0 + δ·L)
  (L = segment length), for δ ∈ {1e-2, 3e-3, 1e-3, 3e-4, 1e-4, 3e-5, 1e-5, 3e-6, 1e-6}.
- **Exponent:** α = the slope of log f against log δ (least squares over the δ with 10 ≤ count ≤ 1,900), with a
  bootstrap 95% CI (1,000 resamples of base points).
- **Integrable expectation (Kerr):** finitely many singularities on the segment, so α ≈ 1. A chaotic saddle gives a
  fractal singular set, so α = 1 − D < 1.
- **Integrator:** vectorised RK4 on all seeds at once, at dt = 0.025 (§196's dt for p = 3/5 at these levels),
  plus a dt/2 rerun of the full δ ladder at ONE level (p = 3/5, ε = −0.01) for both systems, as an accuracy check
  on α.

## Instrument 2 (SECONDARY): MEGNO on the same segment
60 evenly spaced seeds, §196's validated rule (duration-binned p99 table, life drift ≤ 1e-9, pilot dt), and the
deep-v2 Kerr gate (binomial p0 = 0.03, alpha 0.05). Reported per level. Its known limit (plungers inflate MEGNO
even in Kerr, §196 deep-v2) is why it is secondary.

## Levels
p = 3/5 at ε ∈ {−0.003, −0.01, −0.03} (tangle measured) and p = 4/5 at the same ε (splitting below floor), each
for TS2 and Kerr (same mass and spin, ε relative to each system's own l_sep, §199's saved levels and x_h).
12 level-systems.

## Gates and verdict (per level)
- **VALIDITY:**
  - Kerr α within [0.85, 1.15], with its CI overlapping 1;
  - the dt/2 check moves α by < 0.05 at the checked level;
  - capped seeds < 25% (otherwise UNREADABLE).
  If the Kerr gate fails at a level, that level is UNREADABLE.
- **CHAOTIC SADDLE SEEN:** α_TS < 0.85 AND the bootstrap CIs of TS and Kerr do not overlap.
- **Otherwise "no chaotic saddle resolved at δ ≥ 1e-6"** (not "integrable").
- MEGNO is reported alongside, descriptive unless its Kerr gate passes.

## Predictions (stated now)
- Kerr: α ≈ 1 everywhere.
- TS p = 3/5: chaotic saddle SEEN at ε = −0.01 and −0.03 (splitting θ ~ 2.5e-3 and 7e-3 makes lobes wide enough for a
  measurable fractal dimension); at ε = −0.003 maybe.
- TS p = 4/5: α ≈ 1 (no resolved saddle), consistent with its below-floor splitting.
- MEGNO: likely still unable to discriminate (the deep-v2 limit), which would explain §196's 0/360 together with
  this result.
- Confidence in the TS p = 3/5 prediction: moderate. A clean α ≈ 1 there would mean the tangle's lobes are too
  thin for δ ≥ 1e-6, itself informative.

## Operations
2 worker processes, nice 10, detached (setsid), per-job JSON checkpoints with skip-if-done, watch_footprint (MAXMB
2000, MINDISK 5 GB, MINFREEPCT = pressure guard), verified-PID stop file, ≤ 1 GB new disk. Launch and finish are
reported to The Bridge.
