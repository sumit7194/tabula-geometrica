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
