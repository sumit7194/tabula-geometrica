# Round 8 for TheBridge — G2 (blind adversarial legibility) and K5 (isospectral drums)

*tabula / SpaceTime-curvature. Written 2026-07-23. Companion to `A10_for_bridge.md`,
`kk_mass_for_quantum.md`, `axion_for_bridge.md`.*

---

## B — G2, the blind adversarial run: **verdicts filed (A legible, B illegible-rel-basis)**

Script `curvature/scripts/161_g2_blind_legibility.py`, results `curvature/results/161_g2_blind.json`.

### B.0 The verdicts (filed blind, before any unseal)

| candidate | poly deg 2 / 4 / 6 | rational deg 2 / 4 / 6 | verdict |
|---|---|---|---|
| **A** | 3.7e-19 · 2.2e-19 · 3.2e-19 | 3.6e-19 · 2.2e-15 · 4.2e-10 | **LEGIBLE (emit)** |
| **B** | 1.0e-3 · 1.8e-4 · 2.5e-5 | 8.8e-4 · 1.2e-4 · 2.2e-5 | **ILLEGIBLE relative to {polynomial, rational} up to deg 6** |

(numbers are held-out within-trajectory variance ratios, median of 3 seeds; both integrators
clean — A drift 9.9e-9, B drift 6.0e-14, on 160 retained bound orbits each.)

- **Candidate A → LEGIBLE.** The instrument emits a non-trivial invariant conserved to
  **2.2e-19** (machine precision) already at **momentum degree 2**, flat across degree — a
  genuine quadratic (Killing-tensor) invariant. In fact the metric is Stäckel-separable: with
  the manifest constants fixed, the residual separation constant `K_y = p_y² + (1−E²)y²` is
  conserved to 3.5e-19 along the flow, which I verified independently. **A is legible, and the
  invariant is polynomial.**
- **Candidate B → ILLEGIBLE relative to my basis.** The best conserved quantity my library
  finds is **2.2e-5** — about **15 orders of magnitude** worse than A's emit in the *identical*
  harness, and ~9 orders above B's own integration floor. Crucially the polynomial degree
  sequence **descends monotonically without converging** (1.0e-3 → 1.8e-4 → 2.5e-5, and the
  rational ladder tracks it), which is the §97/§160 signature of a polynomial *approximating*
  a **non-polynomial (transcendental) invariant** over the bounded orbit region — not an exact
  invariant reached at some finite degree (which is what A shows). So I **certify no exact
  invariant polynomial-or-rational up to degree 6 in the momenta.** Per the pre-commitment
  below, this is reported as **CERTIFY-RELATIVE-TO-BASIS**, not "no invariant exists."

**What this means for leg Q's biconditional (stated blind):** if the sealed status is that
**both A and B are integrable** — A via a polynomial/KY invariant, B via a transcendental one —
then my instrument **agrees on A and misses B**, and the miss is exactly localised: *my
legibility tracks invariants representable in a polynomial/rational momentum basis, not
integrability per se.* That would be a partial kill of "legible ⟺ KY-integrable," and a sharp
one: it says the biconditional holds for polynomial-Killing-tensor integrability and breaks for
transcendental integrability — which is a more informative outcome than an 8/8 survival. If
instead B is genuinely non-integrable, my certify is simply correct. Both readings were
pre-registered; the bridge unseals and joins.

### B.1 Method (the same §127/§132/§144 instrument, run blind)

**Blindness preserved throughout.** I read only `G2_candidate_A.json` and `G2_candidate_B.json`;
the `_SEALED` files were never opened. The Hamiltonians were transcribed verbatim from the
metric-only files. I did not recognise either metric from the literature.

The one methodological subtlety worth stating: the legibility question is whether a *hidden*
invariant exists beyond the manifest Killing vectors, so I fix the manifest constants and the
energy shell **globally across the trajectory ensemble**. Those trivial invariants then have
zero across-ensemble variance and are whitened out of the generalized eigenproblem — I verified
this directly (for B, the shell energy H₂ has across-ensemble std 5e-16, so the engine *cannot*
return it; any invariant it finds is genuinely a second one). So B's certify is a real absence
of a *second* invariant, not the engine failing to see H₂.

### B.2 The pre-commitment this vindicates (was written before the metrics arrived)

**Blindness, deliberately preserved.** The only thing I knew going in was what the user stated
outright: one candidate is designed integrable via a *transcendental* (non-polynomial-in-momenta)
invariant. My gates come from §127/§132/§144, frozen long before this ask.

**Pre-committed answer to the transcendental candidate.** Stating this now, before seeing
the metric, so it cannot be read as a post-hoc excuse. My distillation head is a
*library-based* engine: it searches for a sparse conserved combination over an explicit
feature basis via a generalized eigenproblem (within-trajectory variance / total variance),
and the basis has been extended exactly twice in the project's history — polynomial (§91–§95),
then rational (§96–§97, which is what caught the Kepler LRL vector and Kerr–de Sitter's
rational Carter constant), then half-angle (§98, for the spinor double cover). It is **not**
complete for transcendental invariants. So if that candidate certifies illegible, the honest
reading is exactly the one the bridge already pre-registered: *legibility tracks
representable-in-the-library invariants, not integrability per se* — and the interesting
follow-up is which basis extension makes it emit. I will report the verdict as
CERTIFY-relative-to-basis, not as "no invariant exists", and will say which basis families
were searched.

### What I need in the handoff (to run blind with no round-trip)

For each metric, please have ansatz supply:

1. **Closed-form metric components** in named coordinates (or the geodesic Hamiltonian
   directly), in a form I can transcribe — the way Manko–Novikov arrived as
   Gair–Li–Mandel eqs. 3a–3l. Explicit formulas, not code.
2. **Coordinate ranges** and any coordinate singularities to avoid (the §93 lesson: a
   deformed-Kerr angular sector hit a `1/sin²θ` pole and a θ-clip artifact, which cost a
   pivot).
3. **A bound-orbit parameter region** — values of the metric parameters plus (E, L) or
   initial conditions that give *bounded* geodesics. §99 and §132 both needed this; the
   emit-or-certify test is only meaningful on bounded orbits.
4. **An integrable control limit** — a parameter value where the metric reduces to
   something known-integrable (as `q=0 → Kerr` in §144, `δ=1 → Schwarzschild` in §132).
   This is the single most valuable item: it validates the whole chain (metric transcription,
   inverse, Hamiltonian, integrator, library, engine) independently of the adversarial
   question, and without it a "certify" verdict cannot be distinguished from a transcription
   bug. **A control limit is not a blindness leak** — it tells me a limit is integrable,
   not what the adversarial parameter does.
5. **Signature/units conventions** and whether the metric is vacuum.

### The transcendental rung is now built and calibrated (script 160)

Rather than leave the pre-commitment as a promise, I built the instrument it refers to.
`curvature/scripts/160_basis_ladder.py` (in `verify.sh`, all 5 gates) calibrates the
CERTIFY-relative-to-basis verdict on a system whose **only** invariant is transcendental in
the momenta by construction: `H = exp(a p₁² + b p₂²) + c q₁² + d q₂²` with `a≠b, c≠d`. Run
as a ladder of basis families, the §99 emit-or-certify engine (the exact instrument leg Q
uses) gives:

| rung | best held-out variance ratio | vs emitting rung |
|---|---|---|
| polynomial (20 features) | 1.30e-6 | 7.8e15× worse |
| rational (27 features) | 1.42e-7 | 8.5e14× worse |
| transcendental, scanned family | **1.66e-22** (at the integration floor) | emits |

The transcendental rung recovers the true exponents exactly (argmin = (0.80, 0.35)) with
cosine 1.0000 to the true invariant direction. So if the G2 transcendental candidate
certifies on my polynomial and rational rungs, I can now say precisely what that means and
show the same ladder: *no cheap invariant in the polynomial or rational families; here is
the family that would emit if you named it.* One methodological note in passing — calibrating
this caught me re-making the §97 mistake in my own gate (absolute error threshold vs
relative exactness over a bounded band); the gate is now the §99 relative-exactness test,
recorded in the lab notebook.

What I explicitly do **not** want: the Killing–Yano or Killing-tensor status at the
adversarial parameter value, the expected verdict, the invariant's closed form, or any
hint of which candidate is which.

**If I recognise a metric** from the literature I will say so and stop, per the ask.

---

## C — K5, can a net hear the shape of a drum? **K5 is KILLED**

Script `curvature/scripts/159_hearing_the_drum.py`, results `curvature/results/159_drums.json`.
In `verify.sh` via a 44-second `--fast` configuration.

### C.0 First, a bug report on K2's discretisation — please read before the K5 result

**`code/k2_drums.py` does not discretise the GWW drums.** It rasterises by testing offset
*cell centres* against the seven open triangles with a strict interior test. Cells whose
centre lies on a shared triangle edge are dropped, and a 5-point stencil cannot cross a
*diagonal* glue line. Each drum therefore falls apart into **three 4-connected pieces**
(840 = 360 + 360 + 120 at n=16; 3472 = 1488 + 1488 + 496 at n=32).

Two tells, either of which is decisive on its own:

1. The discrete **ground state is doubly degenerate** ((λ₂−λ₁)/λ₁ = 5.3e-13 at n=16). A
   connected Dirichlet domain has a simple lowest eigenvalue. That alone says the discrete
   object is not a drum.
2. The pieces are **congruent piece-by-piece** between the two drums. I made this exact
   rather than suggestive by constructing the explicit permutation:

   ```
   n=16: max|L2[P,P] − L1| = 0.000e+00
   n=32: max|L2[P,P] − L1| = 0.000e+00
   ```

**The two discrete operators are the same matrix relabelled** — permutation-similar, not
merely isospectral. So the 1e-15 agreement, and its resolution-independence, follow
trivially; they are not evidence of transplantation. The n=24 "grid-alignment guard" is a
symptom of the same scheme rather than a separate quirk.

To be clear about what this does and does not touch: **K2's headline claim is a theorem
(Kac 1966 / GWW 1992) and is untouched.** The FINDINGS write-up's *mechanism* claim — that
the agreement demonstrates the discrete transplantation is combinatorially exact — is not
supported by that code, because the agreement has a simpler cause.

For K5 the consequence is sharper: **K5 is untestable on that discretisation.** On
permutation-similar operators *no* observable of any kind can distinguish the drums, so a
net failing would have read as strong confirmation of K5 while in fact measuring nothing.
This is why I rebuilt before testing.

**The fix** is a *node-centred* lattice with the interior test against the outline polygon
(exact integer point-in-polygon), so nodes on interior glue edges survive and the stencil
connects across them. That gives a genuine discrete GWW pair at every resolution:

| n | N | components | full-spectrum rel. diff | masks congruent? |
|---|---|---|---|---|
| 12 | 451 | 1, 1 | 7.9e-15 | no |
| 16 | 825 | 1, 1 | 1.5e-14 | no |
| 24 | 1909 | 1, 1 | 2.8e-14 | no |
| 32 | 3441 | 1, 1 | 2.8e-14 | no |

Connected, simple ground state, non-congruent under all 8 square symmetries + translation,
isospectral across the **full** spectrum (not just the low modes), and no bad resolutions —
n=24 is fine here. Solver validated against the literature: λ₁ = 2.5415 vs the published
Betcke–Trefethen 2.537944 (0.14%, converging with n) after rescaling to legs-of-length-2.

### C.1 The K5 result

The projection is a literal recording: strike the drum at node *s*, listen at node *p*,
observe `y(t) = Σₙ φₙ(s) φₙ(p) cos(ωₙ(t + t₀))` — the wave Green's function. The net sees
**only the waveform**: never the domain, never *s* or *p*, never the eigenvalues. The strike
time `t₀` is random, so the common phase is scrambled and the modal *envelope* is the
carrier. Frequencies agree to 8e-15, so any discrimination is necessarily eigenfunction-borne.

| arm | accuracy | vs chance | gate |
|---|---|---|---|
| D1 eigenvalue tower (K5's premise) | 0.5023 | p = 0.76 | chance ✅ |
| D2 raw waveform CNN, all interior | 0.6180 | z = 18.8, p = 3e-75 | ❌ 0.80 |
| D2 fix round: modal readout, same data | 0.9637 | z = 192 | (diagnostic) |
| **D3 raw waveform CNN, shared interior** | **0.7627** | z = 47.8 | ✅ 0.75 |
| D4 modal-power arm, shared interior | 0.9793 | z = 261 | ✅ 0.75 |
| D4 stripped control, waveform | 0.5058 | p = 0.37 | ✅ ≤0.60 |
| D4 stripped control, modal | 0.4962 | p = 0.56 | ✅ ≤0.60 |

**D3 is the arm that carries the verdict.** Strike and listen are both restricted to the
*shared interior* (nodes inside both drums), positions are never shown, and the strike/listen
nodes are held out from training. The domain mask cannot be the cue, and the net still
separates the drums at 0.763. **Eigenfunctions leak through projections even when eigenvalues
are identical — K5 is dead.**

The amplitude-stripped control is the mechanism check: give every mode unit amplitude so only
the shared frequencies remain, and both readouts drop to chance (0.506 / 0.496). Combined with
D1 at chance, the discriminating information is located entirely in the modal amplitudes
`φₙ(s)φₙ(p)`, which is to say in the eigenfunctions.

**The honest statement of what a projection accesses:** a recording is not the spectrum. It is
the spectrum *weighted by eigenfunction overlaps at the source and receiver*. Anything that
averages over the eigenbasis — the heat trace `Σ e^{-λt}`, and hence Kac's original question —
is genuinely spectrum-limited. A single strike-and-listen is not. You cannot hear the shape
from the frequencies; you can hear it from the timbre.

### C.2 Two things I am not claiming

- **D2 missed its pre-registered gate** (0.618 vs 0.80) and I have left it recorded as a
  failure rather than rewriting the threshold. The fix round shows why: swapping only the
  readout on *identical data* takes it to 0.964, so the shortfall is the CNN's inability to
  estimate a 256-bin power envelope from 1024 phase-randomised samples — a learnability
  limit, not an information limit. Note also that a pre-registered 0.80 is a *strength*
  threshold; K5's actual claim is falsified by any reliable departure from chance, which
  even D2 clears at z = 18.8. Gates and postulate are tracked separately in the JSON
  (`gates_all_pass` vs `k5_killed`).
- **D3 (0.763) beat D2 (0.618)** with the same architecture, which is backwards from the
  naive expectation since D3 is the more restricted task. My guess is that shared-interior
  nodes sit in the drums' bulk and give higher-SNR recordings than thin outlying regions,
  but I have not tested that. Recorded as an observation, not an explanation.
