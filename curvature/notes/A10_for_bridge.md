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
