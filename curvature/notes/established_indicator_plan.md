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
