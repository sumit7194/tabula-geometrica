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

## Is the equatorial B = A = 0 ring known? (full-text check, 2026-10-16; Opus subagent, key claim re-verified by tabula)
**No paper we could read identifies a singularity off the horizon in MN, and one states the opposite.**
- **Brink 2008, "Spacetime Encodings II" (arXiv:0807.1179, PRD 78 102002), Fig. 10, reads "Curvature Singularity on
  Horizon Equator (No singularities outside)".** Verified by tabula on the rendered page.
  - His Appendix C metric has the same B = [x+1+(x−1)ab]² + [(1+y)a+(1−y)b]² as ours. (His second ln(b/α) line prints
    P₂/r² for P₂/r³, a typo.)
  - His Fig. 6 parameters correspond to χ = 0.9, q = 0.95.
  - GLM cite Brink (by private communication) for the x = 1, y = 0 singularity.
- **GLM 2008 §II.A** names only "a circular line singularity at x=1, y=0". §II.B describes the ρ ≈ 0.72 edge as where
  "the outermost edge of the CTC region touches the innermost edge of the region of bound motion". In §III they
  speculate that "singular behavior of the metric as the CTC region is approached" may drive the ergodicity, which
  is not an identification of a singularity.
- **LGAC 2010** (§2.1, §3.4), **CLA 2011** (§2-3) and **CHL 2012** (§1, §4):
  - the horizon is "broken … by a line singularity" at ρ = z = 0;
  - the inner boundary is "an almost constant ρ ≃ 0.72";
  - the "deep hole … works as a stochastic scatterer" (to −1e5).
  None calls it a singularity, and none mentions B.
- **Later works place the singularity only at x = 1, y = 0:**
  - Bambi & Barausse arXiv:1108.4740 §II;
  - Bambi & Lukes-Gerakopoulos arXiv:1302.0565 §II;
  - Destounis & Kokkotas arXiv:2108.02782 §II, at exactly χ 0.9, q 0.95, E 0.95, Lz 3;
  - Staelens et al. arXiv:2303.02111 §II.C;
  - Geyer MSc 2013 (Stellenbosch, hdl 10019.1/80306) Ch. 6.
  None computes a curvature scalar for MN.
- **Unflagged prior plots of the feature** (subagent's plot readings, ±0.03; our x_s = 1.929828 is ρ_prolate =
  arccosh x_s = 1.2755):
  - Brink Fig. 5 (g_tt) shows concentric contours on the equator at ρ ≈ 1.2–1.26;
  - Geyer Fig. 6.2(b) (g_φφ, q 0.95, χ 0.9) shows a pole-like blob at ρ ≈ 1.25–1.28.
- **Structural precedent in a different spacetime:** Kodama & Hikida, gr-qc/0304064 §3.1.3. In Tomimatsu–Sato δ = 2,
  Ψ₂ ∝ 1/B³ and Ψ₀Ψ₄ ∝ 1/B⁶ diverge at an equatorial B = 0 point x₀ > 1 off the horizon rod ("the famous ring
  singularity"), where the inner ergo-boundary meets the equator and the CTC region touches. GLM call TS "quite
  similar" to MN. Nobody has carried this over to MN.
- **Manko & Novikov 1992** (CQG 9 2477): closed access, NOT read.
- **Our status:** Kretschmann ∝ d⁻⁶ at the ring (197c; code validated on Kerr's closed form to 2e-16). So the
  "B = 0 alone isn't proof" caveat is met by a direct invariant. The claim we can make is: **a naked curvature ring
  singularity outside the horizon at χ 0.9, q 0.95 (and at F5-R), not identified in the MN literature, and
  contradicting Brink 2008's "no singularities outside"**, with the TS2 analogue as precedent. p1 also has an exact
  B = A = 0 equatorial point (x = 1.07596). Its Kretschmann was not computed.
