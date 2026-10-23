# §199b — canonical splitting measures at the TS δ=2 saddle-centre (pre-registration, 2026-10-23)

Follows §199 (notes/separatrix_splitting_prereg.md). The user approved running it today, in my session. Attended,
≤ 4 cores. **Blinding:** The Bridge replicates these two measures blind. Embargo `tabula-199b-invariants-to-bridge`
is active in tools/EMBARGOES.json; no §199b number is sent until The Bridge has sealed its own. Results go to
results/199b_* and to the RESULT section of this file only.

## Why
§199's θ is an angle in (x, p_x), so it is coordinate-dependent. Two canonical (symplectic-invariant) measures:
1. **Lazutkin's homoclinic invariant** ω(ξ_u, ξ_s) at the primary symmetric homoclinic point h.
2. **The lobe area** (the flux) between h and the next intersection of W^u with W^s.
Both are exactly 0 for an integrable system, so Kerr is the exact-zero control.

## Definitions (fixed now)
- **Natural parametrisation:** W^u(t) = P^n(z* + (t/λ^n)·e_u), so that P(W^u(t)) = W^u(λt) and W^u'(0) = e_u.
  The reversor S(x, p_x) = (x, −p_x) satisfies P∘S = S∘P⁻¹, so W^s(t) := S·W^u(t) obeys P(W^s(t)) = W^s(t/λ)
  with e_s = S·e_u.
- **Normalisation:** |ω(e_u, e_s)| = 1, with ω((a,b),(c,d)) = ad − bc in (x, p_x). Since ω(v, S v) = −2 v_x v_p,
  e_u = v_u / √|2 v_ux v_up|.
- At the symmetric h = W^u(t_h) = S h, the stable-side parameter is the same t_h, ξ_u = W^u'(t_h) and
  ξ_s = S·ξ_u. **Invariant I = ω(ξ_u, ξ_s) = −2 ξ_ux ξ_up.**
- ξ_u = (dz/ds)/(c·λ^n), where z(s) = P^n(z* + s·v_u), c = √|2 v_ux v_up|, and dz/ds is the §199 central
  difference at δ ∈ {1e-4, 1e-5}. Same code path as §199; λ comes from the same Jacobian.
- **Lobe area:**
  - U = W^u(t) for t ∈ [t_h/λ, λ·t_h] (N points, geometric in t); Σ = S·U;
  - h2 = the first intersection of U (moving away from h, t > t_h) with Σ, other than h;
  - the lobe is the closed curve U[h → h2] + Σ[h2 → h];
  - the area comes from the shoelace formula in (x, p_x) (symplectic, invariant).
  Resolution variants: N = 800 and N = 1600 per fundamental domain. If no h2 is found, the level is reported as
  NO-SECOND-INTERSECTION.

## Levels
Lazutkin: all 6 readable-or-not §199 levels (p = 4/5 and 3/5 × ε ∈ {−0.003, −0.01, −0.03}), TS2 and Kerr,
rtol ∈ {1e-13, 1e-12}; it is cheap. Lobe area: p = 3/5 only (where §199 resolved θ), TS2 and Kerr, rtol 1e-13.

## Verdict (per measure, per level)
- **"canonical splitting measured: I (or A) = value ± err ≫ Kerr floor"** iff |TS value| > 10·F and the variant
  spread is < 20% of it, where F = max(|Kerr value| over its variants, the TS variant spread). Same structure as §199.
- Otherwise "below floor F at this precision". Never "integrable".
- **Sign:** reported, but carries no weight in the verdict.

## Predictions (stated now)
- p = 3/5: I and A both measured, ≫ Kerr, and increasing with h, like θ.
- p = 4/5: I below floor (as θ was); lobe not attempted.
- Kerr: I at its floor; A near 0 (if the curves coincide, a spurious h2 gives a near-zero area at the noise level).

## SEALED 2026-10-23 (numbers EMBARGOED for The Bridge's blind replication)
results/199b_invariants.json sha256 4c64da83f263950343eb8c52170623376268fd82003190b5993c1e22f0c86f03. The result summary is in notes/embargoed/ and results/199b_REPORT.md. Do
not read those until your own seal.

## RESULT (embargo LIFTED 2026-10-23: The Bridge sealed V16 at TheBridge dade806; sha256 verified)
| p | ε | Lazutkin I (TS2, headline) | variant spread | Kerr floor | lobe area A | spread | Kerr | verdict |
|---|---|---|---|---|---|---|---|---|
| 3/5 | −0.003 | −5.55e-8 | 2.0e-9 | 8.0e-10 | 1.430e-6 | 6e-10 | 7e-14 | both MEASURED |
| 3/5 | −0.01 | −1.781e-7 | 2.5e-9 | 5.8e-10 | 4.518e-6 | 6e-10 | 2e-13 | both MEASURED |
| 3/5 | −0.03 | −5.12e-7 | 3.3e-8 | 7.2e-10 | 1.160e-5 | 5e-10 | 5e-14 | both MEASURED |
| 4/5 | −0.003…−0.03 | −6e-9 … −2.4e-8 | ~1e-8 | ~2e-9 | — | — | — | I below floor (~1e-8) |
- **All predictions held** (p = 3/5 measured and increasing with h; p = 4/5 below floor; Kerr at floor).
- Scaling: I ∝ h^0.99 / h^1.04 and A ∝ h^0.98 / h^0.93 between consecutive levels, ~linear, not exponentially
  small.
- **BLIND REPLICATION (The Bridge, V16, its own code; Lazutkin invariant only, lobe not computed):** at p = 3/5,
  ε = −0.01, |Ω| = 1.790e-7 (3 of 4 variants agree to 0.1%) vs ours 1.781e-7. **Agreement 0.5%**, inside our 1.4%
  spread. The sign is opposite, a convention (ω orientation / tangent order); the sign was registered as carrying no
  verdict weight.
- **θ discrepancy resolved:** V16's θ = 7.54e-4 vs our 2.50e-3 (ratio 3.32). The Bridge's L and p_x are ours ÷ σ
  (l_sep ratio exactly 1/σ: 3.3333 for TS2 at σ = 0.3, 1.6667 for Kerr at σ = 0.6). The angle in (x, p_x) rescales
  by that factor, while the Lazutkin invariant is invariant under momentum rescaling, because its normalisation
  |ω(e_u, S e_u)| = 1 cancels the action unit. So the invariant agrees and θ differs by the unit factor. This is a
  live demonstration of why the canonical measure was needed.
- Process note: The Bridge's V16 commit SUBJECT stated its value (seen while verifying the seal). Ours was already
  sealed (dc8b808), so there was no contamination; recorded by class.
- **Agreed wording (both reports, The Bridge V16 FINDINGS 21ad8d0):** "transversal splitting of TS δ=2 (p = 3/5,
  ε = −0.01) independently replicated in the Lazutkin invariant by two codes (numerical, non-rigorous); θ agreement
  after the units convention."
