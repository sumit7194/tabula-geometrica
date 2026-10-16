# PROMPT 1 — The Manko–Novikov equatorial ring singularity: where it exists, why it is a curvature singularity, and who knew

You are a fresh research session. Your working folder is `/Users/sumit/Github/fable_briefs/tabula/work_1/`. Write
everything there and nowhere else.

## Ground rules (from /Users/sumit/Github/fable_briefs/README_RULES.md; follow them exactly)
1. **Spawn independent agents in parallel** for the separable parts below, plus **one adversarial verifier agent**
   that tries to break the main result. Merge only after the verifier reports.
2. **Read only** the inputs listed here (read-only copies in `/Users/sumit/Github/fable_briefs/tabula/inputs/`) and
   public papers. Do not open, modify or run anything under `/Users/sumit/Github/<any repo>`, and do not touch git.
3. **Write all output** to new files in `work_1/`:
   - a `REPORT.md` with every claim referenced (arXiv id + equation/section, or file + line) and marked verified /
     partially verified / unverified;
   - any scripts you write, with pinned package versions (pip/venv only inside `work_1/`).
4. Do not post, email, publish, push, or contact anyone. Do not install system software.
5. Do not mention or investigate any vendor/OS security bug; it is out of scope.
6. **Pre-register before computing.** Write `PREREG.md` (question, method, pass/fail criteria, one known-answer
   positive control, one negative control) BEFORE running any computation.
7. Prefer a short correct "no, because…" to a long speculative "yes". Say explicitly where you work from memory.

## Background (what we found; treat it as a claim to be checked, not a fact)
The metric is the Manko–Novikov (MN) "q-anomaly" subclass as written in Gair, Li & Mandel 2008 (arXiv:0708.0628,
Eqs. 2–7) and Brink 2008 (arXiv:0807.1179, App. C), in prolate spheroidal (x, y) with x > 1, |y| < 1:
- A = (x²−1)(1+ab)² − (1−y²)(b−a)²;
- B = [x+1+(x−1)ab]² + [(1+y)a+(1−y)b]²;
- C = (x²−1)(1+ab)[b−a−y(a+b)] + (1−y²)(b−a)[1+ab+x(1−ab)];
- a = −α exp(−2β(−1+Σ_{l=0}^{2}(x−y)P_l/R^{l+1})), b = α exp(2β(1+Σ_{l=0}^{2}(−1)^{3−l}(x+y)P_l/R^{l+1})),
  with R = √(x²+y²−1) and P_l = P_l(xy/R);
- α = (−1+√(1−χ²))/χ, k = M√(1−χ²), β = qM³/k³; q = 0 is Kerr.

Two independent sessions found numerically that at (χ, q) = (0.9, 0.95), and at the nearby rational point
(M, a, q) = (89, 80, 19/20):
- **B = A = 0 exactly at one equatorial point** (y = 0), with a = −b and a² = (x+1)/(x−1). This is at
  x_s = 1.929828259 (Weyl ρ = 0.7194 M) and x_s = 1.921922588 respectively. In φ it is a ring OUTSIDE the horizon
  segment (ρ = 0, |z| ≤ k), at R ≈ 1.65.
- **The Kretschmann scalar diverges as d⁻⁶** in the distance d to that point, along every ray tested (two
  implementations, one with numerical and one with exact derivatives, both validated on Kerr's closed form).
- **At (χ, q) = (0.6, 0.1024) there is also an exact B = A = 0 point,** at x = 1.0759622, inside R < 0.5.

A literature search found no MN paper that identifies a singularity off the horizon. Brink 2008 Fig. 10 says
"No singularities outside". The closest precedent is Kodama & Hikida (gr-qc/0304064 §3.1.3) for Tomimatsu–Sato δ = 2,
where Weyl scalars ∝ 1/B³ diverge at an equatorial B = 0 point. Manko & Novikov 1992 (CQG 9, 2477) was not
accessible to us.

## Questions (each a separable agent)
- **Q1, existence map (analytic plus numeric).** On y = 0, B = 0 ⇔ a = −b and a² = (x+1)/(x−1). Derive the
  equatorial equations for a(x, 0) and b(x, 0) in closed form (the Legendre sums simplify at y = 0). Find for which
  (χ, q), with q of either sign and χ ∈ (0, 1), a real solution x_s > 1 exists, and whether it lies inside R < 0.5 or
  outside it. Map the region in the (χ, q) plane, with the boundary curve analytically if possible. Check whether
  B = 0 can also occur off the equator.
- **Q2, curvature singularity: an analytic argument, not only numerics.** Show, following the Kodama–Hikida
  structure, that a curvature invariant (Kretschmann, or Ψ₂ in a suitable tetrad) carries an uncancelled 1/B^k with
  k ≥ 1 at B = A = 0, and give the leading exponent in d (we measured 6). Independently re-derive the d⁻⁶ law
  numerically at one point, with your own code (positive control: Kerr's closed-form Kretschmann; negative control:
  a generic point far from the ring, where K is finite and smooth).
- **Q3, relation to the ergosurface and the CTC region.** f ∝ A/B, so A = 0 is the ergosurface. Is it generic that
  the ergosurface, the boundary of the g_φφ < 0 (CTC) region and B = 0 all meet at the ring? Our numerics put g_φφ
  at a POLE there, not a zero. Explain, analytically if possible.
- **Q4, literature (full text, not abstracts):** do Manko & Novikov 1992, or any paper since (MN, "bumpy black
  holes", Tomimatsu–Sato comparisons, MN shadows/imaging, MN geodesic chaos), identify this ring? Search
  arXiv/INSPIRE/ADS. If MN 1992 is reachable through any legitimate open copy, read it; if not, say so. Quote at most
  15 words per quote. Check whether Brink's "No singularities outside" refers to a specific parameter point or is a
  general statement.
- **ADVERSARIAL VERIFIER:** try to show the "singularity" is a coordinate or transcription artefact. Possible routes:
  a different γ convention (the "−2 inside or outside the Σ" ambiguity in GLM Eq. 3h), a typo in the a/b exponents,
  or B = 0 being a removable coordinate degeneracy. Check whether the conclusion depends on the transcription.

## Inputs (read-only, in `/Users/sumit/Github/fable_briefs/tabula/inputs/`)
- `k20_literature.md`: our literature notes, including the ring section and citations.
- `k20_build_log_redacted.md`: our build log. The sections "FINDING … singular ring" and "Kretschmann near the ring"
  are the relevant ones.
- `kretschmann_197c.py` and `kretschmann_197c_results.json`: our Kretschmann code (mpmath) and its values.
- `mn_codegen_with_regularisation_identity.py`: our metric transcription, including the exact identity
  ρ²B² − 4k²C² = k²·A·Q (polynomial division, zero remainder) that removes the 1/A poles.

## Deliverable
`work_1/REPORT.md`, giving:
- (1) the existence map, with method and checks;
- (2) the analytic singularity argument, with its exponent;
- (3) the ergosurface/CTC geometry;
- (4) a literature verdict, "identified by X" or "not identified in Y (list)", with what could not be read;
- (5) the verifier's attack and its outcome;
- (6) a one-paragraph summary a physicist could check in ten minutes.
Mark every claim verified, partially verified or unverified.
