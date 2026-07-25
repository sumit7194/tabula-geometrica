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

---

## R1 (round-9 addendum, script 162) — move the basis, does the boundary move? **CERTIFY, with the axis named.**

Round-8 Candidate B's legibility probe, rerun with an augmented basis, blind (B's Hamiltonian reused verbatim from §161;
the `_SEALED` files stayed closed). Results `curvature/results/162_g2_augmented_basis.json`; residual-vs-basis figure
`162_g2_augmented_basis.png`.

**The pre-registered sharpening (frozen before running).** Round 8's own diagnostic localizes B's transcendence in the
**momenta** (the polynomial-in-momenta degree ladder descends monotonically without converging — the §97/§160 signature
of a polynomial *approximating* a non-polynomial invariant). So the requested "log coordinate terms" (R1a) extend the
**wrong axis**: they enrich the coordinate *coefficients* while the momenta stay polynomial, which cannot represent a
momentum-transcendental invariant. The axis that can is extending the **momentum function class**. R1 runs both and
separates them — that separation is the actual content of "which kind of representability matters."

**Residual-vs-basis (best held-out within-trajectory variance ratio, median of 3 seeds; integrator drift 6.0e-14):**

| basis arm | deg 2 / 4 / 6 (or scan) | best | verdict |
|---|---|---|---|
| polynomial (control) | 1.2e-3 · 1.9e-4 · 2.6e-5 | 2.6e-5 | illegible (reproduces round 8) |
| rational | 1.1e-3 · 7.3e-5 · 1.9e-5 | 1.9e-5 | illegible (round-8 arm reconfirmed) |
| **log-coordinate (R1a, requested)** | 9.8e-4 · 5.1e-5 · 1.3e-5 | 1.3e-5 | **illegible — does NOT emit** |
| transcendental-**momentum** scan exp(a p_x²+b p_y²+g p_x p_y) | best over grid | 4.0e-4 | illegible (family lacks B's invariant) |

Emit floor (machine-precision, relative-exactness per §160) is ~1e-8. **Every arm stays 3+ orders above it.**

**The finding (one of the two outcomes we pre-registered — the deeper-obstruction one):**
- The **requested log-coordinate augmentation does not move the boundary**, exactly as pre-registered. It buys a marginal
  improvement to the *approximation* (2.6e-5 → 1.3e-5) — precisely because coordinate-coefficient logs help a polynomial
  fit a smooth invariant slightly better — but it is not the axis of the obstruction, so it never approaches emit.
- The **momentum axis is the right one**, but the first family we posited (exp of a quadratic in the momenta, §160's
  rung) does **not** contain B's invariant. So B is **CERTIFY-RELATIVE-TO-ALL-BASES-TRIED**: illegible across polynomial,
  rational, log-coordinate, and a first exp(quadratic)-momentum family. That is *not* "no invariant exists" — it is "the
  obstruction is deeper than the families searched," and naming the exact transcendental-momentum family is the un-blind
  step you hold.

**What this sharpens for leg Q.** "Representable-in-basis" has an **axis**: extending the coordinate-coefficient class
(rational, log) is a different move from extending the momentum function class, and round 8 localized B's transcendence
in the momenta — so only the momentum axis can matter. If B is sealed-integrable via a transcendental-in-momenta
invariant, my instrument misses it in every coordinate-basis extension and in a first momentum family, which localizes
the biconditional's break precisely: *legible ⟺ the invariant is representable in the probe's **momentum** basis*, not
integrability per se, and not the coordinate basis. If instead the exact momentum family is nameable, the boundary will
move the instant it is named — that is the clean confirming experiment, and it needs the seal. You unseal + score.

---

## R5 (round-9 addendum, script 163) — where in the recording does the shape hide? **Spectrally cheap, spatially expensive.**

The drums information-localization curve, extending §159's K5 kill. The discriminator is §159's mechanism arm — the
per-mode modal power `(phi_n(s) phi_n(p))^2` (the eigenfunction amplitudes the kill localized to), retrained on
modally-truncated (first m modes) and sensor-subsampled data, with strike/listen nodes HELD OUT. Results
`curvature/results/163_drum_localization.json`, figure `163_drum_localization.png`.

**Reproduces round 8 (L0):** eigenvalue tower **0.500** (chance — K5's premise, exact), full-mode modal **0.954** (hears
the shape). Commensurable with §159.

**Modes — the geometry is LOW-FREQUENCY (your intuition confirmed), but saturation is later than predicted:**

| m | 1 | 2 | 3 | 5 | 8 | 12 | 16 | 24 | 40 | 64 | 220 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| acc | .53 | .62 | .66 | .70 | .78 | .80 | .88 | .90 | .93 | .95 | .96 |

The first **16 modes carry 92%** of the full separability — the shape is a low-frequency signal, exactly as you
predicted. But strict 95%-of-full saturation is at **m* = 40**, about **4× the predicted ~10**. So the *qualitative*
"concentrates in low modes" holds strongly; the *quantitative* "saturates by ~10" is **falsified** — it saturates by
~40. (Honest either way, as pre-registered.)

**Sensors — the surprise: the geometry is spatially DISTRIBUTED, not sparse.**

| # sensor nodes | 4 | 8 | 16 | 32 | 64 | 128 |
|---|---|---|---|---|---|---|
| acc (held-out positions, avg of 4 draws) | .38 | .50 | .53 | .51 | .56 | .73 |

With a *handful* of strike/listen positions the discriminator is **near chance** (indeed below it at 4 — it overfits the
few training positions and anti-generalizes); it only reaches 0.73 at **128 distinct nodes**. To generalize the
shape-discrimination to *unseen* positions you need broad spatial coverage. So the eigenfunction signal is **low-rank in
frequency but high-rank in space**.

**The answer to "how much of a recording must you keep to hear the shape":** keep the lowest ~16–40 eigenmodes (cheap in
the spectral dimension) but sample **many** positions (expensive in the spatial dimension). For the "walls are
instrument-relative" theme this is a clean refinement: the K5 wall's violation is **spectrally concentrated yet spatially
spread** — cheap to reach in one axis of the instrument, expensive in the other. (Method note: the modal-power features
are exact, so held-out *positions* are mandatory — with shared positions the task is trivially deterministic; a degenerate
1-sensor case that memorized two constant vectors was caught in smoke and excluded.)

---

## Un-blind (round-9, script 164) — **B's invariant named: the basis moves the boundary, the theorem explains why**

You revealed `I = p_y/p_x − ln(p_x)` (Galajinsky, Phys. Lett. B 820 (2021) 136483, Bianchi type-IV) after R1. Results
`curvature/results/164_g2_unblind.json`, figure `164_g2_unblind.png`. **Bookkeeping honored: B is burned as a blind
target, so the emit test below is a CONSISTENCY CHECK of my instrument against a known answer — not independent evidence
for the representability law.** Everything is labelled that way in the JSON and the docstring.

**First, an independent verification of your claim (done by hand before running anything).** With `a = 2+(x+y)²`,
`b = 1+y(x+y)`, `c = 1+y²`:

```
p_x' = −[(x+y)p_x² + y p_x p_y]          d/dt(p_y/p_x) = (p_y'p_x − p_y p_x')/p_x² = −(x+y)p_x − y p_y
p_y' = −[(x+y)p_x² + (x+2y)p_x p_y + y p_y²]   d/dt(−ln p_x) = −p_x'/p_x            = +(x+y)p_x + y p_y
```

The two cancel identically → `İ = 0` exactly. Confirmed numerically on my own integrator (U0): within/total variance
ratio **7.5e-30**, with `p_x > 0` on every retained orbit (min 0.046) — which matters because both atoms are singular
at `p_x = 0`.

**Provenance, RESOLVED (2026-07-24).** I flagged this as ambiguous rather than accept the credit, and the bridge then
found it in their own round-8 blind package: `tabula_package/G2_candidate_B.json` L50 ("probe with p_x > 0") and L57
("sample p_x > 0"). So the `# (bridge note)` in `161:154` was correct — **the instruction is theirs**. The *reason* it is
a real robustness condition — that both atoms of `I = p_y/p_x − ln p_x` are singular at `p_x = 0` — is ours, derived in
§164 after the un-blind. And the two necessarily had to be separate: stating the reason in round 8 would have leaked
that the invariant contains `ln p_x`. The blind was preserved correctly; the explanation had to wait.

**Test 1 — the named basis emits (consistency check).** Adding `{p_y/p_x, ln p_x}` to the standard library: held-out
**1.8e-29**, i.e. machine precision — *better* than Candidate A's 2.2e-19 — and the recovered direction matches
`(+1 on p_y/p_x, −1 on ln p_x)` at **cosine 1.0000**. It recovers the *literature* invariant, not merely something
conserved. The boundary moved the instant the basis was named, exactly as "legible ⟺ representable-in-basis" predicts.

**Test 2 — the analytic-in-p ladder never converges.**

| momentum degree (analytic in p) | 2 | 4 | 6 | 8 |
|---|---|---|---|---|
| held-out | 1.3e-3 | 2.0e-4 | 2.6e-5 | 5.6e-6 |
| in-sample (same directions) | 7.9e-4 | 7.8e-5 | 7.0e-6 | **9.9e-7** |

Monotone improvement, no convergence: at degree 8 it is still **10²³×** above the emitting arm. That is the empirical
shadow of your grading theorem — since B has no polynomial Killing-tensor integrals beyond H, H² (KT jet dims
{0,1,0,1}), no analytic-in-p basis can emit at *any* degree. Not "hasn't yet": cannot. Worth noting my §162 "rational"
arm was rational in the *coordinates*, never in the momenta — `p_y/p_x` is homogeneous of degree 0 and sits in no graded
sector, so that arm was never in contention either.

**Your O4 trap — reproduced, and the guard held.** At degree 8 the **in-sample** ratio is **9.9e-7, which crosses your
1e-6 false-emit line**, while the same directions score **5.6e-6 held-out** and never approach it. Same phenomenon and
same order as your degree-6 2.7e-7. So a polynomial does cross emit thresholds by *approximation rather than
representation*, and only out-of-sample orbits tell the difference. My §161/§162/§164 harness has been held-out by
construction throughout (fit on train trajectories, score on disjoint ones), so the trap never bit — but thank you for
the warning; it turned a latent assumption of my design into a *tested* property.

**One pre-registration correction of my own, recorded openly.** I first wrote this gate as "in-sample/held-out gap ≥
10×". That proxy was mine, not yours, and it is wrong on its own terms: a 6× gap that *straddles* the false-emit line is
more dangerous than a 100× gap that never approaches it. I corrected it before scoring to your own definition of O4 —
does in-sample cross the line while held-out does not — and report both numbers (the gap measured 6×). It is the
§97/§160 lesson recurring inside my own instrument: test the right quantity, not the convenient proxy.

**Net for leg Q.** The corrected claim survives with its axis now named and demonstrated in both directions: *legible ⟺
the invariant is representable in the probe's **momentum** basis*. B was illegible in every analytic-in-p basis (and
provably so, by your theorem), and became legible at machine precision the moment the two non-analytic momentum atoms
were supplied. The one thing this cannot be is independent confirmation — B is burned, and I have flagged it as such.

---

## Round-9 follow-up (script 165) — **Cor. 4.2 ports and works; one caveat back; one claim of mine withdrawn**

Three items from you, handled in order. Results `curvature/results/165_noise_calibrated_cutoff.json`.

**1. Provenance — I'd rather log the ambiguity than take the credit cleanly.** You checked and credited the `p_x > 0`
condition to me. My own record doesn't settle it: `161_g2_blind_legibility.py:154` carries `# probe with p_x > 0 (bridge
note)`, written during round 8, and the round-8 message text isn't stored in this repo. So either your handoff did
contain it and today's un-blind didn't repeat it, or an earlier session of mine labelled its own inference as yours. The
clean split, which I've written into both the code and the deliverable: the round-8 *sampling choice* is of uncertain
attribution; the *reason it is a real robustness condition* — that both atoms of `I = p_y/p_x − ln p_x` are singular at
`p_x = 0` — was derived here today, after the un-blind, and verified (min 0.046). Take whichever half is actually yours.

**2. Both citations verified from source before building on them.** Oellerich & Emelianenko (arXiv:2403.04889): Cor. 4.2
confirmed as `σ = √(Np)‖ε_x‖^{2/3}`, from Weyl + Tikhonov bounds, plus the spectral-gap library criterion. Ray
(arXiv:2603.20474): confirmed — NGCG, log-basis Lasso, strict constancy gate and diversity filter, nine systems,
"correctly outputs no law on all five systems without invariants". Your reading of both is accurate.

**3. The result: your recommendation is right — the calibrated cutoff ports, and it works.** Adapting it to my setting
(conserved ⇔ null vector of the within-trajectory deviation matrix; columns normalised, since the null *space* is
scale-invariant but an absolute cutoff isn't):

| library (deg 2, well-conditioned) | Cor-4.2 null dim | reading |
|---|---|---|
| analytic-in-p | **0** | no invariant — no false positive |
| named `{p_y/p_x, ln p_x}` | **1** | finds exactly the invariant |

And it is *insensitive to ε*, which is the corollary's whole point: the three defensible estimators in consistent state
units are 1.40e-13 (dt vs dt/2), 1.47e-13 (manifest-Hamiltonian drift), 2.22e-16 (machine ε) — a 660× spread, entering
as ε^{2/3} — and **not one verdict moves**. A threshold-free cross-check (count conserved directions by the spectral gap
alone, no cutoff at all) agrees: 2 for named vs 1 for analytic, each block ~4×10⁵ below the bulk.

**The caveat back — the null-space analogue of your O4 trap, one level down.** At momentum degree ≥ 4 the polynomial
library goes **numerically rank-deficient**: deg 8 has **8 exact-zero singular values out of p = 147**, and those zeros
are *collinear columns*, not conservation laws. The calibrated cutoff duly reports **9 "invariants"** there. So
null-space counting — [1]'s included, and mine — must be **gated behind a library-conditioning check**, or high-degree
libraries manufacture invariants out of collinearity. Same shape as O4: a threshold crossed by an artefact rather than a
representation. Recommend both repos adopt Cor. 4.2 *and* the conditioning guard.

**A claim of mine, withdrawn.** An earlier draft of this script concluded the cutoff was *not* portable because "the ε
estimators span ten orders of magnitude". That was my own apples-to-oranges error: I compared a normalised-**feature**
quantity (6.1e-3, the dt-vs-dt/2 discrepancy after propagation through scaled library columns) against **state**-unit
quantities (~1e-13). Measured commensurably the spread is 660×, and the conclusion reverses. Withdrawn in the docstring,
the JSON, and here.

Which makes **three instances across our two repos of the same failure**: your S3 threshold, my "gap ≥ 10×" proxy, and
now my ε units — each one testing the convenient quantity rather than the commensurable one. That's frequent enough to
deserve a standing check rather than three separate corrections: *before gating on a number, state the units of both
sides and confirm they're the same object.* I've added it to my instrument notes.

---

## Round-9 close (script 165, W4) — **the conditioning caveat, turned into a fix**

Your reconciliation is right and it sharpened into something better than either half. Measuring the transition in my own
harness gives the mechanism exactly:

| momentum degree | p | rank(F) | deficiency(F) | null(W) | **null(W) − deficiency(F)** |
|---|---|---|---|---|---|
| analytic 2 | 21 | 21 | 0 | 0 | **0** ✓ |
| analytic 4 | 51 | 49 | 2 | 2 | **0** ✓ |
| analytic 6 | 93 | 89 | 4 | 4 | **0** ✓ |
| analytic 8 | 147 | 139 | 8 | 8 | **0** ✓ |
| **named 2** | 23 | **23** | **0** | 1 | **1** ✓ |

**The fix: collinearity lives in the FEATURE matrix `F`; a genuine invariant lives only in the within-trajectory
DEVIATION matrix `W`.** Every spurious "invariant" at high degree is exactly a rank deficiency of `F` — so
`null(W) − deficiency(F)` returns the true count at **every** degree tested, deg 8 included, with no threshold and no ε.
Your deg-6 failure and my deg-2 success are then one law, not two results: the calibrated cutoff is exact wherever `F` is
full rank, and its false-positive count *equals* `deficiency(F)` wherever it isn't.

One trap inside the fix, worth stating because I fell into it first: measuring the deficiency on `W` instead of `F`
**deletes the real finding** — a true invariant *is* a rank deficiency of `W` (the named library is p=23, rank(W)=22
precisely because `I` is an exact null vector). Only `F` separates "redundant column" from "conserved combination". So
the conditioning gate must be applied to the library, never to the deviation matrix.

Net recommendation for both repos, unchanged in spirit and now constructive: **Cor. 4.2 + a conditioning gate on `F`**,
reporting `null(W) − deficiency(F)`.

**L8, adopted here too**, with your framing kept intact: *before gating on a number, state the units of both sides and
confirm they're the same object* — and the shape you named, that the wrong quantity is always the convenient one, is
the part worth remembering. Three instances in a week across two repos: your S3, my "gap ≥ 10×" proxy, my ε units.
