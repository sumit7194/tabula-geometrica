# Pre-registration — §193: numerical screen of Tomimatsu–Sato δ=2 for additional polynomial integrals

*Frozen 2026-09-24, BEFORE any conservation statistic is computed on TS. Fleet plan chain 2, the "N rung",
assigned by The Bridge. It runs in parallel with quantum's proof tool (Morales–Ramis/Kovacic) and ansatz's exact
rung, each session on its own instrument.*

## Independence, stated first

- **Read:** only `conjecture_machine/data/sealed/TS2_for_quantum/TS2_METRIC.md` and the two component files.
- **Not read:** ansatz's sealed prediction (`TS2_PREDICTION_SEALED.md`), quantum's proof-tool records, and any
  published TS-specific integrability or chaos literature. The literature was avoided on purpose, so the verdict
  is blind to the published expectation as well as to ansatz's.
- **Priors I bring in:** my own ZV δ=2 work (§132, rank-2 CERTIFY) and 1302.4234, which The Bridge named for the
  ZV control. **ZV is the q=0 member of the same family** (manifest), so this is prior knowledge about a
  neighbour, and it is declared here.
- Results go to The Bridge only, until the bridge compares.

## Why this design (and not §168's)

§168 and §174 ran rank 3–4 screens on real stationary axisymmetric metrics with E, L and H **varying**, and both
were **REFUSED**. Their eps=0 controls failed: the reducible algebra grew large, and the readout could not see
Carter even where it certainly exists. This run uses the design that worked to degree 6 in §161 and in
§93/§94: the **fixed shell**.

- (E, L, μ=1) are pinned per ensemble.
- t and φ are cyclic, so the flow reduces to the 2-DOF system (x, y, p_x, p_y).
- On the shell, H and every product of the manifest constants are ensemble constants. They whiten out of the
  generalized eigenproblem, so **every conserved direction found is genuinely new at that shell**, and no
  deflation step is needed.
- **Reversibility.** At fixed (E, L) the reduced Hamiltonian is *natural*,
  H = ½(g^xx p_x² + g^yy p_y²) + V(x, y; E, L), with no terms linear in momentum. It is therefore reversible
  under p → −p, and the momentum-even and momentum-odd parts of any integral are separately conserved. The
  library is split by momentum parity, and each part is screened on its own.
- **Rank mapping.** A rank-r Killing tensor, restricted to the shell, becomes an integral whose momentum-even
  or momentum-odd part is a polynomial in (p_x, p_y) of degree ≤ r, with rational coefficients in (x, y).

## Units, the object, and the Hamiltonian

- **Units:** m = 1 throughout, so σ = p/2 for TS δ=2 (manifest: m = 2σ/p).
- **The two TS points:** (p, q) = (3/5, 4/5) and (4/5, 3/5).
- **Kerr control at matched spin:** the same J/m² = q, with m = 1, a = q and σ = p. It is built by me from
  Boyer–Lindquist via r = 1 + σx, cos θ = y, and not taken from ansatz's pipeline.
- **ZV δ=2 control:** f = ((x−1)/(x+1))², e^{2γ} = ((x²−1)/(x²−y²))⁴, σ = 1/2.
- All three go through **one** generic code path: five covariant components → exact (T, φ)-block inverse → H.
- **Geodesics:** timelike, H = ½ g^{ab} p_a p_b = −½, with p_T = −E and p_φ = L.

## Gates, in order. A failed earlier gate stops everything later, and TS stays unread.

### L0 — loader

My loaded TS components must reproduce the manifest's own formulas at 20 random points (relative error
≤ 1e-10):
- g_TT = −A/B;
- g_xx = σ²B / (p⁴ (x² − y²)³ (x² − 1)), which follows from f and e^{2γ};
- the Weyl–Papapetrou identity g_TT g_φφ − g_Tφ² = −σ²(x² − 1)(1 − y²);
- the twist equation for ω, by finite difference (relative error ≤ 1e-6);
- far-field m = 1 and J/m² = q (relative error ≤ 1e-3).

A loading error would mean screening the wrong object, which is the §124 failure.

### Shells

The shells are fixed from **bound-orbit existence alone**, before any conservation statistic is computed.
- Three (E, L) shells, the same for Kerr, ZV and TS at each q, with pericentres in the strong field
  (r ≲ 8m).
- **The ring singularity** sits at x ≈ 1.137 (p = 3/5) or x ≈ 1.057 (p = 4/5), with y = 0, which is r ≈ 0.3m.
  - Any orbit with min x < x_guard is **dropped, not clipped**. x_guard is the value corresponding to r = 3m,
    about 7–10 times the ring's x.
  - Any orbit with |y| > 0.98 is dropped as well (the chart's axis boundary).
  - I report the kept orbits' min x, max |y| and min B = |N + D|², so the distance from the singular set is
    measured, not asserted.
- **Integration:** H drift must be ≤ 1e-10 relative, or the orbit is dropped.

### Library, named per §166 C1

- **Momentum part:** monomials p_x^a p_y^b with 1 ≤ a + b ≤ r, split into even and odd a + b.
- **Coordinate family** CR(d, s), "chart-rational":
  - numerators x^i y^j with i + j ≤ d;
  - denominators in {1, (x² − 1)^{−k}, (1 − y²)^{−k} : k ≤ s};
  - with s = ⌈r/2⌉;
  - plus pure coordinate terms.
- **Ladder:** rank r ∈ {2, 3, 4} × coordinate degree d ∈ {2, 4, 6}. The d axis is what feeds the §178
  descent-vs-flat readout.
- **Second family** CR⁺ at the largest d: CR augmented by the inverse-metric components
  {g^TT, g^Tφ, g^φφ, g^xx, g^yy} times each momentum monomial. This is the analogue of §168's "rational+metric",
  and it brings TS's own denominator B into the basis.
- **Engine:** §99's whitened generalized eigenproblem, computed in covariance form
  (held-out ratio = cᵀ A_within c / cᵀ B_total c on unseen trajectories). The mathematics is unchanged; it is
  streamed so that p ≈ 2000 fits in memory.

### C1 — Kerr count check, both q, every shell. A failure means REFUSED, and TS is not read.

The expected number of conserved directions comes from representability. Carter on the shell is
K = (1 − y²) p_y² + a²(1 − E²) y² + L² y² / (1 − y²):
- even parity:
  - r = 2, d ≥ 2 → **1** (K);
  - r = 3, d ≥ 2 → **1**;
  - r = 4 → **2** (K, K²) when d ≥ 4 and s = 2, and **1** at d = 2, where K² is not representable;
- odd parity → **0** everywhere.

The count must match on every shell. This measures whether the readout isolates the right number of directions
**on geodesic flow of a real rotating metric**, which is exactly where §168/§174 failed.

**Detection threshold.** The Kerr floor at a given (q, shell, r, family, parity) is the held-out ratio of the
last direction in its expected count. A direction is **conserved** if its ratio ≤ 10³ × that floor. That is
§168's margin, and it is calibrated on the case whose answer is known. Ratios between the band and 1e-6 are
reported as **APPROXIMATE**, and are never counted as detections.

### C2 — ZV δ=2: 0 at every rung, shell and family

This is the literature expectation (1302.4234 as named; §132 at rank 2). ZV's pattern along the d axis is also
recorded as the reference shape for a **real absence**, which the §178 readout compares against.

### C3 — Toda, an odd-degree readout control

- **System:** the reduced 3-particle Toda chain, on a fixed energy shell, with an exponential coordinate family
  that can represent the known cubic I3.
- **Required:** 0 at r = 2 (H has whitened out), **1 at r = 3 in the odd part, with I3 in the conserved span**,
  and 0 in the even part at r = 3.
- **Limitation, stated as The Bridge asked.** Toda is a natural Hamiltonian, not geodesic flow on a metric. It
  validates the *readout* at odd degree, not the *geodesic reduction*. The reduced TS flow *is* a natural
  Hamiltonian, with a curved kinetic metric, but no spacetime positive control at odd rank is available to me
  that I am blind to.
- **So a TS null at rank 3 reads "none found, with the odd-degree reduction validated only indirectly".**

### C4 — conditioning honesty (§166 C2)

A rung returns **REFUSED-LIBRARY**, and is never absorbed into a null, if either:
- its Kerr control count fails; or
- more than 3× the expected count read as conserved (the floor did not transfer to a library of this size).

§166's C4 (state-functionality) is **vacuous** here: the library is built from state only, so nothing can fail
it. It is reported for completeness.

## Verdicts. TS is read only after C1–C3 pass.

Every (q, shell, r, family, parity) cell gets one of:
- **DETECTED at rank r in basis B**: ≥ 1 conserved direction on **every** shell at that q.
- **SHELL-RESTRICTED INTEGRAL**, The Bridge's note 1: conserved on some shells and not on others. This is
  reported separately as "a shell-restricted integral, not a Killing tensor", and **never folded into the rank
  verdict**.
- **NONE up to rank N in basis B**: no conserved direction on any shell. The §178 d-axis readout then adds either:
  - **FLAT**: consistent with real absence, and shaped like ZV; or
  - **DESCENDING**: basis-limited, so an invariant outside B cannot be excluded, and the verdict is scoped
    down.
- **REFUSED-LIBRARY**: see C4.

## Scope, travelling with every verdict

- It is numerical and proves nothing.
- It covers the named family, up to r = 4.
- It covers the two supplied (p, q) points only.
- It covers bound timelike geodesics in the kept region (r ≳ 3m) only. It says nothing about orbits near the
  ring or the x = 1 poles.
- The vacuum property is inherited from ansatz's Schwartz–Zippel check, which is probabilistic, not symbolic.
- Grading gives independence between rungs, not finiteness of the ladder.

## Resources

1. A small probe first: L0 plus a handful of orbits, with the whole-process-tree footprint read from top
   MEM + CMPRS.
2. The number goes to The Bridge.
3. Production waits for The Bridge's go.
4. Watchdog: kill if free disk < 5 GB or free swap < 512 MB.
