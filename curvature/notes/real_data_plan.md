# Real-data + temporal arc — detailed plan (EXP-13, EXP-14, and fresh direction ③)

**Started 2026-07-02** (user-approved). The frontier detector suite (EXP-4..12, scripts 145–153) is validated on
synthetic menus. This arc takes it to REAL data and to TEMPORAL regime-switching, then toward the project's payoff swing.

## Shared philosophy (agreed with the user)

- **Gate against literature consensus, web-verified.** Real data has no ground-truth JSON. Same rigor, different oracle:
  each gated claim is checked against the established characterization of that dataset (cited in the docstring + notebook).
- **Abstain/mixture outputs are expected to earn their keep.** A detector that confidently labels every real series would
  be suspicious. Honest ABSTAIN on a genuinely ambiguous/underpowered dataset is a CORRECT result, not a failure.
- **verify.sh stays OFFLINE.** Download each dataset ONCE, commit the small CSV into the repo (`curvature/data/`), and gate
  on the cached file. No network dependency in the regression gate.
- **Segmentation caveat, stated honestly.** Real data is usually ONE long series; the trajectory branch wants an ensemble.
  We chop the series into contiguous segments (standard practice) and NOTE that segments are not independent draws.

---

## EXP-13 — the real / benchmark dataset test (script 154) — DONE 2026-07-02, R1/R2/R3 pass

**RESULT:** laser→CHAOTIC (R²0.97/K0.998, matches lit), tides→PREDICTABLE (R²0.998/K0.23), sunspots "not regular"+stable but SURROGATE test z=1.0 → consistent with STOCHASTIC not chaos (laser positive control z=10.2). The 0-1 test flags regular-vs-not; the surrogate test separates chaos-vs-stochastic. Bell-data bonus not attempted (deferred).

Point the robust detector (150) + emit-or-certify at real data. Menu (each a distinct role):

| dataset | source (verify first) | role | expected (literature) | gated? |
|---|---|---|---|---|
| **Santa Fe laser (set A)** | Santa Fe Time Series Competition, far-infrared NH3 laser | canonical REAL low-dim CHAOS | CERTIFY-CHAOS / CHAOTIC | ✅ |
| **Sea level / tide gauge** | NOAA CO-OPS API (CSV, no auth) OR a committed harmonic-tide CSV | REAL quasi-periodic (regular) | EMIT-regular / PREDICTABLE | ✅ |
| **Sunspot number (monthly)** | SIDC/SILSO (CSV) | REAL + genuinely AMBIGUOUS (lit: stochastic vs chaotic debated) | whatever it says | ⚠️ exploratory |

- **Gated rows (laser, tides):** the detector's verdict must match the literature consensus, AND be STABLE across
  segmentations/subsamples (no seed/segment cherry-picking). Laser → chaotic; tides → regular.
- **Exploratory row (sunspots):** report the verdict + evidence (0-1 K, one-step R²). Gate only: (i) the verdict is
  STABLE across subsamples (not flapping), and (ii) NO confident-wrong-able claim — if ambiguous, ABSTAIN is acceptable
  and honest. This is the row that tests whether the detector is honest on genuinely hard real data.
- **BONUS (ungated): real experimental Bell data.** If obtainable (Delft 2015 loophole-free test, Hensen et al., ~245
  trials, S=2.42±0.20): run the contextual branch. Prediction worth its own note — with only ~245 trials the
  abstain-aware detector may correctly ABSTAIN (a 2-sigma result is genuinely underpowered), which would be an honest,
  literature-consistent reading and a great story. Treated as a bonus row, not a gate (data-wrangling risk).

**Pre-reg gates (2026-07-02):**
- R1 LASER-CHAOTIC: the Santa Fe laser series → CHAOTIC/CERTIFY-CHAOS, stable across ≥3 segmentations.
- R2 TIDES-REGULAR: the tide/sea-level series → regular/PREDICTABLE, stable across ≥3 segmentations.
- R3 SUNSPOTS-HONEST: the sunspot verdict is stable across subsamples AND the detector does not make a confident claim it
  can't support (ABSTAIN allowed); report the verdict + evidence transparently.
- (bonus) B1 BELL-DATA: if acquired, run the contextual branch; report verdict (likely ABSTAIN at ~245 trials) — ungated.

**Engineering:** `download_data.py` (one-shot, network) fetches + writes `curvature/data/*.csv` (committed). `154_real_data.py`
loads ONLY the cached CSVs (offline), segments, runs `s150.detect_robust` (+ the 0-1/one-step measures), gates.

---

## EXP-14 — temporal non-stationarity / regime-switching (script 155) — DONE 2026-07-02, T1/T2/T3/T4 pass

**RESULT:** Bell-stream classical→quantum switch (tunable margin; logistic dropped). Sliding-window CHSH localizes the switch (err 0) vs whole-stream blur; U-shaped error-vs-W; temporal-vs-ensemble separable (within-stream variance). SYNTHESIS (T4): localization floor = N_resolve/2, grows ~1/δ² (slope -1.71) as δ→wall — the sampling axis sets the TEMPORAL resolution of law-detection. Corrections logged (logistic→correlation stream; first-crossing→confidence-based floor).

The detector assumes ONE regime for the whole series. Real/interesting systems SWITCH law in time. EXP-8 did mixtures
ACROSS the ensemble (which orbit is chaotic); EXP-14 does mixtures ACROSS TIME (WHEN the law changes).

- **Generator:** a series that switches law mid-stream — e.g., logistic map drifting through periodic ↔ chaotic windows
  (r sweeps 3.5 → 3.9 → 3.5), or concatenated Lorenz → harmonic oscillator → Lorenz. Whole-series verdict misrepresents it.
- **Fix:** a SLIDING-WINDOW detector that runs the per-window chaos measure and localizes change-points. Research-first:
  cite change-point literature (PELT/HMM/CUSUM); keep our own simple windowed instrument (threshold the windowed 0-1 K).
- **THE SYNTHESIS RESULT (the headline, ties to EXP-12):** an UNCERTAINTY PRINCIPLE for law-detection. To decide a regime
  needs ~N_resolve samples (diverges ~1/δ² near a wall, EXP-12). So a switch CANNOT be localized to better than ~N_resolve
  in time: short windows ABSTAIN (too few samples), long windows SMEAR the switch. Prediction: switch-localization error
  vs window length is U-SHAPED, with the floor set by the sampling axis. Headline: *"the sampling axis sets the temporal
  resolution of law-detection — near-wall regimes aren't just data-hungry, they're temporally blurry."*
- **Closes a loop:** ensemble-mixture (EXP-8, "which orbit") vs temporal-switching (EXP-14, "when") — the windowed detector
  distinguishes them (temporally CLUSTERED verdicts = switching; INTERLEAVED across the ensemble = mixture).

**Pre-reg gates:**
- T1 SWITCH-DETECTED: the sliding-window detector localizes the known change-point(s) within a tolerance a whole-series
  verdict cannot (whole-series gives one label / wrong; windowed recovers the switch).
- T2 U-SHAPED RESOLUTION: switch-localization error vs window length is U-shaped — too-short windows abstain/noisy,
  too-long windows smear; there's an optimal window, and its floor tracks the sampling-axis N_resolve (EXP-12 synthesis).
- T3 ENSEMBLE-vs-TEMPORAL: the windowed detector distinguishes a temporally-switching series (clustered) from an
  ensemble-mixture (interleaved) — the two kinds of "mixture" are separable.

---

## ③ Fresh direction (after EXP-13/14) — DISCOVERY ON REAL PHYSICS DATA

The payoff swing, and the most "tabula geometrica" thing we could do: point the WHOLE instrument suite (emit-or-certify
engine + detector) at REAL solar-system data (JPL Horizons ephemerides). Does it EMIT the Newtonian invariants (energy,
angular momentum, the Laplace-Runge-Lenz vector) from REAL planetary trajectories — the thesis (*discover the law from
observation*) finally leaving the sandbox? EXP-13 builds the exact data-plumbing this needs (cached real data + offline
gate). Ranked #1 of the fresh options; alternatives noted: ① SAE-legibility on a real small LLM's activations
(cross-session with Phronesis); a consolidation "instruments of tabula geometrica" writeup + dashboard.

## Order of work
1. EXP-13 research-first (verify each data source URL/format/license) → download_data.py → commit CSVs → 154 → gate → doc.
2. EXP-14 (155) → gate → doc.
3. Discuss ③ with the user (payoff swing).

---

## ③ EXP-15 — NEWTON FROM EPHEMERIDES (script 156) — DONE 2026-07-02, P1/P2/P3 + P4 soft ALL PASS

**RESULT:** μ̂ = GM☉ to 0.0001% (twice, independently: energy + LRL coefficients); L conserved; LRL conserved on 6
bodies (wrong-μ 535×, emit cosine 1.00000); Mercury perihelion precession MEASURED from the LRL drift: 568.4″/cy vs
known ~575 (1.1%). Fix round: near-circular orbits carry no LRL signal → added Icarus/Phaethon; eigen-ordering →
sub-library emit. The thesis, delivered on the actual solar system.

The payoff swing: point the emit-or-certify engine at REAL solar-system data. Data (fetched + committed, offline gate):
JPL Horizons state vectors, heliocentric ecliptic, AU & AU/day — Mercury/Venus/EMB/Mars 2023–2025 @1d (732 rows each)
+ Mercury 1900–2020 @10d (4383 rows) for the precession measurement. All invariants are POINTWISE functions of the
state (no integration), so sampling density is not a limitation.

Known two-body invariants (per unit mass, μ = GM☉): E = ½v² − μ/r; L = r×v; LRL A = v²·r − (r·v)·v − μ·r̂
(A_x = v²x − (r·v)vx − μx/r). Real planets are PERTURBED (Venus/Jupiter etc.), so these are conserved only to
perturbation level (~1e-5..1e-3 relative) — the residual is REAL PHYSICS, framed as such (user-agreed). The engine's
feature library: [v², 1/r, Lx, Ly, Lz, v²x, (r·v)vx, x/r, v²y, (r·v)vy, y/r, v²z, (r·v)vz, z/r] — segments of each
planet's series are the "trajectories" (invariant constant within a planet, DIFFERENT across planets).

Pre-reg gates:
- P1 EMIT E + MEASURE GM☉: on the [v², 1/r] library the engine's most-conserved direction is the energy; the
  coefficient ratio measures μ̂ = −0.5·c₂/c₁, gated within 1% of the known GM☉ = k² = 2.9591220828559e-4 AU³/day²
  (Gaussian gravitational constant squared). Planet-holdout: μ̂ fitted WITHOUT Mercury keeps Mercury's E conserved
  (relative drift < 1e-3).
- P2 EMIT L: angular-momentum components conserved on the real data (relative drift < 1e-3 per planet).
- P3 LRL — THE 1/r-SPECIFIC INVARIANT (the headline): the LRL vector is conserved ONLY for a 1/r potential with the
  right μ. Gates: real-data LRL relative drift < 1e-2 (perturbation level) for all planets AND a wrong-μ control
  (μ×1.2) drifts > 30× more; the engine's full-library conserved span CONTAINS the LRL directions (projection
  residual < 0.05). Second independent μ̂ from the LRL coefficients.
- P4 (exploratory, the crown if it lands): Mercury 1900–2020 — the LRL AZIMUTH drifts linearly = the apsidal
  (perihelion) precession. In the inertial (ICRF/ecliptic) frame the known total is ~575″/century (≈532″ planetary
  perturbations + 43″ GR). Soft gate: measured slope within ±25% of 575″/cy; report honestly either way. If it lands:
  "the discovered invariant's slow failure MEASURES Mercury's perihelion precession from real data."
