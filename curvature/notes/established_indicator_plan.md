# Third chaos method after §195: measurement plan for an established indicator (DRAFT for The Bridge)

**Status:** a measurement plan only. Nothing here is a design, a threshold or a gate. It answers one question:
*can an established indicator separate regular from chaotic orbits in the cycle-poor near-separatrix regime,
without firing on integrable Kerr?* A design is proposed only after these distributions exist, and it is then
validated on unseen levels.

## Research (2026-10-11)
- **MEGNO** (Cincotta & Simó 2000): ⟨Y⟩ → 2 on quasi-periodic orbits, → 0 on stable periodic orbits, and grows like
  λt/2 for chaos. Its time weighting damps transients.
- **FLI** is analytically related to MEGNO (Mestre, Cincotta & Giordano). It comes from the same tangent
  integration.
- **SALI** (= GALI₂ for 2 DOF; Skokos): from two deviation vectors. It tends to a non-zero constant on tori and decays
  exponentially for chaos. It is often faster than MEGNO in few cycles. Commonly quoted threshold: 1e-8.
- **Known pitfalls:**
  - (a) Variational indicators show SPURIOUS structures when the initial deviation vector aligns with special
    directions (Breiter et al.). Mitigation: random initial vectors, and reporting dependence on them.
  - (b) Sticky orbits are misclassified by EVERY indicator if the run is too short. Practical remedy: classify as a
    function of T and accept only verdicts that are stable in T.
  - (c) No published benchmark on Kerr zoom-whirl orbits was found. The Bridge's V11: a finite-time Lyapunov-type
    statistic (S_ex) FIRED ON INTEGRABLE KERR near the separatrix (hyperbolic passage + shear). So this must be
    measured, not assumed.
- **Structural difference from §195:** these indicators need the FLOW's tangent map, so they cannot be applied to
  surrogate time series. Their false-positive controls are INTEGRABLE DYNAMICS instead: Kerr (Carter),
  Schwarzschild, and ZV δ=1 (Schwarzschild in Weyl form). The surrogate nulls are not used.

## Implementation (to be validated before use)
- One integration carries the orbit plus 2 deviation vectors with random unit initial directions (pitfall a).
  Tangent dynamics come from a central directional difference of the reduced RHS, J·w ≈ [f(z+εw) − f(z−εw)]/2ε,
  ε = 1e-7·|z|.
  - **Validation:** on Hénon–Heiles, compare with the exact analytic Jacobian (agreement of ⟨Y⟩ and SALI over T).
- Renormalise each deviation vector every step (SALI uses the normalised pair).
- ⟨Y⟩ is accumulated per Cincotta–Simó, and FLI = max log|w|. The 0-1 test is report-only, from x(t).
- Per-system dt by the drift target (Kerr 0.05, HH 0.0025, ZV measured), sampling every 0.5 τ for checkpoints.

## Controls (fresh seeds; none reused later as validation)
| group | role |
|---|---|
| Kerr real, near-separatrix level (pro, ε = −0.01, E 0.97), 40 orbits | false-positive control in the hard regime (zoom-whirl) |
| Kerr real, a generic (far-from-separatrix) level, 20 orbits | does Kerr settle to ⟨Y⟩ = 2 there? |
| Schwarzschild / ZV δ=1, 20 orbits | integrable static control |
| HH E = 1/12 regular-truth, E = 0.1657 chaotic-truth (FTLE + section-gap labels) | separation where truth is known |
| ZV δ=2: the V11 regular orbit, deep x0 ∈ [7.8, 9.5], the two V11 layer orbits | the target-like regime |

## Readouts (distributions, not verdicts)
- ⟨Y⟩(t), SALI(t), FLI(t) at log-spaced checkpoints up to T = 3e4, and to 1.5e5 for Kerr and ZV.
- For integrable Kerr: the SETTLING time (first t after which |⟨Y⟩ − 2| < 0.1 stays true), its relation to cycles
  completed, and to periapsis proximity to the unstable circular orbit (the zoom-whirl transient). Also the minimum
  SALI over the run and when it occurs.
- Per group and checkpoint: the separation between the integrable and chaotic-truth distributions (min/median/max,
  overlap counts), and dependence on the initial deviation vector (two random draws per orbit).
- Cost and memory, to size any later design.

## What would make the indicator usable (to be proposed AFTER measurement, not frozen here)
Integrable Kerr settles (⟨Y⟩ → 2, SALI bounded away from 0) within a feasible T at the near-separatrix levels, AND
chaotic-truth orbits separate from it by a pre-agreed margin at that T. If Kerr does not settle in feasible T, that
is reported as the indicator's limit in this regime, just as §195's was.

## MEASUREMENT 1 RESULTS (2026-10-12 03:44; results/196_measure/*.json; code 89ae240)
Environment: py314_openblas, BLAS threads 1. Barrier separatrix (Kerr gated vs BPT), per-level cut, per-system dt
(drift pilot <= 1e-10: Kerr 0.05, p 3/5 pro and the long job 0.025, ZV 0.0125, HH 0.0016).

**Integrable controls** (max ⟨Y⟩ over survivors, both vector pairs):
| group | t <= 1e3 | t >= 3e3 (all later checkpoints) | min SALI (at T) |
|---|---|---|---|
| Kerr p4/5 pro near-sep (39/40 survive) | up to 2.33 (transient) | <= 1.97 | 4e-4 |
| Kerr p4/5 retro near-sep (19/20) | <= 1.93 | <= 1.90 | 3e-4 |
| Kerr p3/5 pro near-sep (19/20) | <= 2.09 | <= 2.03 | 1e-4 |
| Kerr generic (20/20) | <= 1.94 | <= 2.02 | 8e-4 |
| Kerr p4/5 pro near-sep LONG to 1.5e5 (20/20) | up to 2.19 | <= 2.08 (at 1.5e5) | 2e-4 |
| Schwarzschild near-sep (19/20) | up to 2.14 | <= 1.95 | 3e-5 |
- **No false alarms after settling.** From t = 3e3 on, every integrable orbit stays at ⟨Y⟩ <= 2.08. Early
  transients reach 2.33, so any rule must use t >= 3e3. The Bridge's zoom-whirl worry (V11 S_ex) does NOT show
  in time-weighted MEGNO.
- SALI decays slowly on integrable orbits (3e-5 to 8e-4 by T, still decreasing): far above the 1e-8 folklore
  threshold, but not constant. It is a weaker discriminator here.

**Truth-labelled HH:** E = 1/12 tori: ⟨Y⟩ <= 2.36 at 1e4 and <= 2.15 at 3e4 (1/80 over 2.1), with an early transient
up to 4.32 at 1e3. KAM tori in a NON-integrable system wobble above 2, so a 2.1 cut is too tight for them.
E = 0.1657 chaos: ⟨Y⟩ >= 10 by t = 100, >= 504 at 3e4. SALI 0.

**ZV δ=2** (new cut x < 1.5): the V11 regular orbit (x0 7.62) and 7 deep seeds survive with ⟨Y⟩(3e4) 1.64-2.13
(pair A; the 2.13 is x0 8.2, whose pair B gives 1.85). **The two V11 layer orbits PLUNGE before T** (9380, 24404 tau),
with ⟨Y⟩ rising to only 2.8 / 4.4 before plunging.

**Reading:** MEGNO is a clean NO-FALSE-ALARM instrument here (integrable Kerr/Schwarzschild settle by 3e3, ≤ 2.08
to 1.5e5), and strong chaos separates by > 200x. The open question is WEAK, SHORT-LIVED separatrix-layer chaos:
⟨Y⟩ of 2.8-4.4 before plunge against torus wobble up to ~2.4 is a thin margin, from n = 2.
**Next measurement (proposed):** a ZV δ=2 near-separatrix population large enough to matter (several eps levels,
dozens of seeds, FTLE truth against the Schwarzschild reference), recording ⟨Y⟩(t) up to the plunge, and testing
whether a GROWTH statistic (the slope of ⟨Y⟩ ~ λt/2 over the surviving window) separates weak layer chaos from
torus wobble better than a final value does.
