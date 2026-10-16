# K20 literature: MN chaos (full-text read, 2026-10-16)

*Read from the arXiv PDFs via pdftotext, and checked against the rendered pages, by a subagent of tabula. Figure
values marked (plot) are readings off the plots, not numbers stated in the text.*

## Gair, Li, Mandel 2008 (arXiv:0708.0628): the parametrization
- **Parameters (Eq. 5):** α = (−1+√(1−χ²))/χ, k = M(1−α²)/(1+α²) = √(1−χ²)M, **β = qM³/k³**.
- **q ≡ −(M₂ − M₂^Kerr)/M³** (Eq. 4: M₂ = −k³[β + 4α²(1+α²)(1−α²)⁻³]). q > 0 is oblate and q < 0 prolate.
- **Coordinates (Eq. 6):** ρ = k√((x²−1)(1−y²)), z = kxy.
- **Pathologies:** a partial horizon on ρ = 0, |z| ≤ k, broken by a line singularity at x = 1, y = 0. For χ ≠ 0
  there is an ergosphere and a CTC region (g_φφ < 0); for q > 0, the outer edge of the CTC region lies inside the
  ergoregion.
- **Eq. 3h hazard:** the −2 is typeset inside Σ_{ℓ=0}^{2}. The asymptotically flat reading has a single −2β, the form
  LGAC 2010 adopts. tabula script 144 already uses it (V0 asymptotic-flatness gate).
- **Fiducial point** χ = 0.9, q = 0.95, E = 0.95, Lz = 3M:
  - a plunging region connected to ρ = 0, intersecting the CTC region;
  - inner bound region ρ ≈ 0.72–2.12;
  - outer bound region ρ ≈ 2.39–13.6.
- **Integration:** Bulirsch–Stoer in τ, conserved quantities to parts in 1e10.

## LGAC 2010 (Lukes-Gerakopoulos, Apostolatos, Contopoulos; arXiv:1003.3120, PRD 81 124005)
- **Setup:**
  - Same parametrization; γ′ with a single −2β (Eq. 5h).
  - V_eff = ½e^{−2γ}[f − E² + ((f/ρ)(Lz − ωE))²] (Eq. 14). Allowed where V_eff ≤ 0; the boundary is the CZV.
  - Section (ρ, ρ̇) at z = 0, ż > 0, in proper time.
- **Points:**
  - fiducial: χ = 0.9, q = 0.95, E = 0.95, Lz = 3;
  - neck case: Lz = 2.995, neck at ρ ≈ 2.25;
  - sweeps: Lz 1–3, E 0.94–1.0, q 0.4–1.0, χ 0.5–1.0.
- **Chaos:**
  - Outer region: KAM, with thin layers around islands.
  - Inner region: a period-1 island (ρ ≈ 0.8–1.05) and a period-3 chain. "The rest of the inner region seems to be
    occupied by chaotic orbits."
  - Mechanism: a deep V_eff hole (to −1e5) near the inner edge acts as a "stochastic scatterer".
  - Neck case: heteroclinic chaos, with stickiness near the outer main island.
- **Island width:** peaks near Lz ≈ 2, and is about zero for q ≲ 0.4 (Fig. 6).
- **CTC:** the allowed region does not overlap the CTC region, though the borders may touch.
- **Integrator:** RK6. Outer region at step 0.1 (refined to 1e-8 at the section), L error ≤ 1e-10 over 1e3 crossings.
  Inner region adaptive 1e-4 to 1e-8, error ≤ 1e-8.
- **Indicator:** rotation number only; no Lyapunov exponents.

## CLA 2011 (Contopoulos, Lukes-Gerakopoulos, Apostolatos; arXiv:1108.5057, IJBC 21 2261)
- **Setup:** χ = 0.9, q = 0.95 only (q > 0). Section as above. Integrator and tolerances not stated.
- **Thresholds at E = 0.95:**
  - The regions join for Lz < 2.99761912 (saddle near ρ ≈ 2).
  - The outer region vanishes at Lz ≈ 3.40935.
  - Plunge channels open as Lz decreases (1.7, 1.6, 1.0).
  - u₀′ is stable for Lz > 2.6125.
- **Thresholds at Lz = 3:**
  - The regions are separate for E ≤ 0.95038.
  - The outer region vanishes at E ≈ 0.93210.
  - Escape for E < 0.1901.
- **Chaotic area fraction (Fig. 10c, plot):** about 20% at Lz = 3, rising above 80% for Lz ≤ 1.6. "The most
  important chaotic region is mainly present in the inner closed CZV."
- **Typo:** Eq. 3 prints √(χ²−1); the correct factor is √(1−χ²).

## CHL 2012 (Contopoulos, Harsoula, Lukes-Gerakopoulos; arXiv:1203.1010)
- **Setup:** χ = 0.9, q = 0.95, Lz = 3, with E scanned (0.95, 0.5, 0.96, 0.7, 0.192 … 0.1899). Integrator not stated.
- **Thresholds:**
  - regions join for E > 0.9504; the outer region vanishes at E ≃ 0.9321;
  - inner boundary at ρ ≃ 0.72;
  - inner z = 0 orbit stable for E < 0.67;
  - tangent bifurcation at E = 0.19236; E_esc ≈ 0.1901.
- **Chaos:** at E = 0.95, the inner region is "most orbits chaotic", tied to the unstable inner z = 0 orbit. At
  E = 0.96, chaos dominates the inner region and the boundary.
  - u₀‴'s asymptotic curves form a homoclinic tangle; the first homoclinic point lies on ρ̇ = 0 (Figs. 18, 19a).
  - Chaotic plus escaping fraction: Eq. 17 and Fig. 23.
- **CTC:** "Regions of closed timelike curves exist outside the horizon."

## Consequences for K20
- All published MN chaos is at χ = 0.9, q = +0.95. p1 (χ 0.6, q +0.10) and p2 (χ 0.385, q −0.26) lie outside the
  studied range, and prolate MN chaos is unstudied. So the papers supply a POSITIVE CONTROL (C0), not a location.
- No published Lyapunov thresholds exist, so the indicator must be calibrated on our own matched Kerr null.
- The published chaos sits next to the CTC edge and the deep V_eff hole. That is why the exterior check is
  load-bearing.
