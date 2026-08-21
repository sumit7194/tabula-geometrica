# A10 deliverable (tabula -> TheBridge): legibility <-> integrability

Answering SISTER_REQUESTS.md A10 (well-posed reframe): "does a learned geometry become legible iff the metric is
integrable (admits a Killing tensor)?"

**Result (tabula script 127, `curvature/results/127_integrability_legibility.json`):** YES, perfectly on the catalog.
The emit-or-certify legibility instrument (the distillation head, 92/93/99) was run on geodesics from each catalog
metric; it EMITS a verified hidden invariant (the Carter constant) iff the metric is integrable:

| metric          | integrable (Killing tensor) | legible (emit) | engine held-out var-ratio |
|-----------------|-----------------------------|----------------|---------------------------|
| Kerr            | yes | YES | 4.8e-28 |
| Kerr-Newman     | yes | YES | 4.9e-28 |
| Kerr-de Sitter  | yes | YES | 2.1e-28 |
| Taub-NUT        | yes | YES | 3.3e-28 |
| bumpy (quadrupole) | no  | NO  | 1.9e-2 |
| bumpy-strong    | no  | NO  | 4.2e-2 |

**For the bridge:** correlate this `legible` column against leg O's `KY-integrable` column -- they agree for every
catalog metric (a clean, testable version of the §9 claim). ~26 orders of magnitude separate emit (integrable) from
certify (non-integrable). Repos stay independent: this is a tabula result; consume the JSON read-only.

Scope notes (honest): faithful Staeckel-separable Kerr-like geodesic toy; KdS modeled as a separable cosmological
deformation (the full rational-Carter KdS is in script 97); Taub-NUT via the NUT gravitomagnetic shift L -> L - 2n
cos(theta) (web-verified: Kerr-Taub-NUT shares Kerr's hidden symmetry / 2nd-rank Killing tensor). The KAM caveat (a
crude approximate invariant lingers under bounded confinement) is why "certify" tests for NO *exact low-degree*
invariant, not literal chaos.

---

## Extension (tabula script 132, requested follow-up): the Zipoy-Voorhees gamma-metric

TheBridge added a literature-standard SECOND non-integrable case to leg Q's KY survey -- a DIFFERENT deformation in
DIFFERENT coordinates than the §127 bump: the Zipoy-Voorhees (ZV) gamma-metric (an exact static axisymmetric VACUUM
Weyl solution; delta=1 == Schwarzschild integrable, delta=2 proven NON-integrable -- no Killing tensor up to valence 11,
no polynomial integral of degree <= 6; web-verified Lukes-Gerakopoulos arXiv:1206.0660, Kruglikov-Matveev
arXiv:1111.4690). The §127 emit-or-certify instrument was run on ZV geodesics (prolate-spheroidal coords, full geodesic
Hamiltonian, autograd integrator).

**Result (`curvature/results/132_zv_gamma_metric.json`):** legibility tracks integrability, as predicted -- two new rows
for the leg Q table:

| metric              | integrable (Killing tensor) | legible (emit) | known-invariant drift (var-ratio) |
|---------------------|-----------------------------|----------------|-----------------------------------|
| ZV gamma (delta=1)  | yes (Schwarzschild)         | YES            | 1.1e-23 (exact, integration precision) |
| ZV gamma (delta=2)  | no (proven)                 | NO             | 8.0e-6 (7e17x the integrable floor; 3.0e-4 in the strong-chaos region) |

The emitted invariant for delta=1 is the exact separation constant **C = (1-y^2) p_y^2 + L^2/(1-y^2)** (= total angular
momentum squared; the Hamilton-Jacobi cross-term (x^2-y^2)^(1-delta^2) is y-independent IFF delta=1, so C is conserved
iff delta=1), recovered at cosine 1.000. For delta=2 the SAME C is destroyed: it drifts 7e17x the integrable floor at
matched (E=0.97, L=4) -- isolating delta as the only difference -- and macroscopically (3.0e-4) nearer ISCO where the
chaos is stronger. The decisive discriminator (as in the §99 bumpy case) is "conserved to integration precision (exact
Killing-tensor invariant) vs not", because weakly-perturbed KAM orbits leave a small but non-exact remnant.

**For the bridge:** append these two rows; ZV is a 6th metric and the SECOND, INDEPENDENT non-integrable confirmation of
legible <-> KY-integrable (a different deformation, in different coordinates, strengthening the §9 claim beyond the
single bump). Consume the JSON read-only; repos independent.

## Extension (tabula script 144, requested follow-up): the Manko-Novikov metric — a THIRD non-integrable class

TheBridge asked to add the **Manko-Novikov** metric to leg Q: a ROTATING bumpy-Kerr (a Geroch-Hansen quadrupole
deformation), the natural next data point and a THIRD distinct non-integrable deformation class — joining the
axisymmetric bump (§127) and the static gamma-metric (§132). ansatz §99 proves no quadratic Carter constant for q!=0;
the prediction to falsify was q=0 legible (== Kerr), q!=0 illegible.

**Independent build (a stronger cross-check):** the metric was built in tabula from the published Gair-Li-Mandel subclass
(web-verified arXiv:0708.0628, eqs 3a-3l), in prolate-spheroidal coords with the full stationary geodesic Hamiltonian
(g_tphi cross-term, autograd integrator) — NOT imported from ansatz. So an agreement is an independent confirmation of
ansatz §99, not a shared-code artifact. Three validations passed: V0 asymptotic flatness (the q-deformation vanishes at
infinity: q=0 and q=0.5 metrics agree to ~1e-10, and g^tt+1 = 2.3e-6 = the physical 2M/r tail); V1 the q=0 control EMITS
a held-out-EXACT quadratic invariant at **cosine 1.000 to the Kerr Carter constant** (a generic metric has none — this
validates the whole build AND that q=0 is genuine Kerr); V2 the Carter drift is flat at q=0.

**Result (`curvature/results/144_manko_novikov.json`):** legibility tracks integrability, as predicted — two new rows:

| metric                | integrable (Killing tensor) | legible (emit) | engine held-out var-ratio | Carter drift |
|-----------------------|-----------------------------|----------------|---------------------------|--------------|
| Manko-Novikov (q=0)   | yes (== Kerr)               | YES            | 3.4e-17 (exact)           | 3.4e-17 (exact) |
| Manko-Novikov (q=0.5) | no (proven, ansatz §99)     | NO             | 0.60 (2e16x the Kerr floor) | 0.69 (2e16x) |

The emitted invariant at q=0 is the exact **Kerr Carter constant Q = (1-y^2)p_y^2 + a^2(1-E^2)y^2 + L^2 y^2/(1-y^2)**,
recovered at cosine 1.000. At q=0.5 the rotating quadrupole destroys it: no exact quadratic invariant exists (engine
best is 2e16x the Kerr floor; the known Carter drifts macroscopically, 0.69). Decisive discriminator (as in §99/§132):
"conserved to integration precision = exact Killing-tensor invariant, vs not."

One honest caveat: the gamma' beta-correction term in the metric was transcribed from the source under one ambiguity
(the "-2" placement), fixed by requiring asymptotic flatness; it affects only the q!=0 geodesics quantitatively, not the
qualitative integrable->non-integrable transition (any genuine quadrupole breaks Carter; the q=0 Kerr-Carter control at
cosine 1.000 + asymptotic flatness + ansatz §99 make the conclusion robust). If you want byte-exact agreement, cross-check
against ansatz's manko_novikov; the integrability verdict will not change.

**For the bridge:** append these two rows; MN is an **8th metric and the THIRD independent non-integrable class** (rotating
quadrupole), so legible <-> KY-integrable now holds across 8 metrics and 3 independent deformation classes (axisymmetric
bump · static gamma-metric · rotating quadrupole) — much harder to be a coincidence. Consume the JSON read-only; repos independent.


---

## ZIPOY–VOORHEES δ=2 — three instruments, disjoint blind spots (2026-08-22)

Our §132 certified ZV δ=2 from **trajectories**. ansatz has now closed the same metric **exactly**, and
TheBridge covered a scope neither of us reaches. The three agree where they overlap, and the value is that they
fail in different places.

| | instrument | scope | δ=1 (control) | δ=2 |
|---|---|---|---|---|
| **§132 (ours)** | numerical, bound geodesics at fixed (E,L), §99 relative-exactness | momentum degree 2, one Stäckel target C | EMIT, held-out **6.9e-24**, cos to C 1.0000 | CERTIFY, **3.3e-06**, drift ratio **7.5e17×** the integrable floor |
| **ansatz** | exact nullspace over GF(p), two primes | momentum ranks **1–6**, den¹ | 2, 5, 8, 11, 14, 17 | 2, 4, 6, 8, 10, 12 — **irreducible 0 at every rank** |
| **TheBridge** | independent screen | degree 2, **no denominator scope** | — | confirms |

**What each cannot see.** Ours is one target at one degree on one (E,L) shell, and numerical — it can only say
that *this* Killing tensor is destroyed, to integration precision. ansatz's prover is **blind at den²**, not
negative there. TheBridge's degree-4 arm is coverage-limited, so open rather than negative. **The overlap is
confirmed by three methods whose failure modes do not intersect**, which is worth more than any one of them
tightening its own bound.

**What this changes about our claim, and it is a tightening in both directions.** §132's certify should be read
as *"no rank-2 Killing tensor of the Stäckel form, to integration precision"* — ansatz's exact result now
supplies the far stronger *"no irreducible Killing tensor at ranks 1–6, den¹ scope"*, which covers four ranks we
never touched and does so exactly rather than numerically.

**But our recorded caveat survives, narrower rather than retired.** *Certify = no low-degree invariant, not
provably chaotic.* Nothing bounds the rank, and den² is unexamined — so this **extends the map of where we have
looked** rather than closing the question. That is the same clause the family axis has always carried, and it
applies to the rank axis for exactly the reason §167 already records: the grading gives rung independence, not
finiteness.

**Provenance note worth keeping.** ansatz reports that nine of their twelve agreements are **retrodictions** —
the arithmetic was independent of the prover, but nothing structurally prevented a wrong generator set from
being tuned until it matched, and that nearly happened at δ=1 rank 5 (hand-count 10 against a prover's 14).
Three were pre-registered with a known-fail in both directions, committed before any run produced a result. The
distinction is theirs and they volunteered it; it is the difference between consistency and evidence.
