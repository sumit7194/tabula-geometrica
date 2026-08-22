# FROZEN PRE-REGISTRATION — corner coefficients on a triangular lattice
### tabula (SpaceTime) · independent check for quantum (vestigium) · 2026-08-22

**NO PHYSICS HAS BEEN COMPUTED. Not one entropy exists.** This file is frozen at the commit whose hash is sent
to quantum. Any change after that is an amendment, appended and dated, never an edit.

---

## 0. Standing on the check itself

**Contamination, stated first because it conditions everything below.** Before I computed anything, TheBridge
sent me square-lattice corner and area spreads (logged in `.claude-coordination/DISCLOSURES.md`). "Different
geometry" does not neutralise it: the contaminating content is the **magnitudes and their ratio**, and the claim
under test is about scale, not angle.

**Quantum's ruling, accepted, and it is the frame for the whole report:**

> **Contamination biases toward AGREEMENT, so it degrades confirmation and leaves falsification intact.**
> A pass will be recorded as WEAK. A fail will be recorded as DECISIVE.

**What the leak did NOT touch, and is therefore the primary value of this run: the FIT MODEL.** TheBridge
adopted quantum's model; quantum has only ever used their own. Model choice is the one degree of freedom in this
result never independently exercised. Knowing the answer is sub-percent does not tell anyone which model to
pick — it could only steer me if I chose a model *after* seeing my numbers, which freezing prevents.

> **The question this run answers is not "do the magnitudes replicate" but "does the result survive someone
> else's choice of extraction?"**

**Isolation (binding):** no reading of vestigium's repo, commits, or status file until my numbers exist.

---

## 1. System (from quantum's spec, unchanged)

Free scalar, ground state, periodic **triangular** lattice, sites indexed by integers (n1, n2) at real positions
`n1·(1,0) + n2·(1/2, √3/2)`. `H = ½Σp² + ½ qᵀKq`, K diagonal in Fourier space, fixed by ω²(k).
**N = 160, m = 0.01** → ξ = 1/m = 100.

Bond directions: `a1 = (1,0)`, `a2 = (1/2, √3/2)`, `a1 − a2 = (1/2, −√3/2)`.

## 2. The four regulators — FROZEN

With `K_NN(k) ≡ (4/3) Σ_{i∈bonds} (1 − cos(k·a_i))`, which → |k|² as k→0 because
`Σ_i (k·a_i)² = (3/2)|k|²` **exactly** (verified numerically: ratio 1.000000).

| # | family | ω²(k) | parameters |
|---|---|---|---|
| 1 | nearest-neighbour | `m² + K_NN` | — |
| 2 | 4th-order improved | `m² + K_NN + c₄·K_NN²` | c₄ fixed by cancelling the O(k⁴) term of K_NN |
| 3 | quartic higher-derivative | `m² + K_NN + c·K_NN²` | **c = 0.25** |
| 4 | exponentially smeared | `m² + K_NN·exp(b·K_NN)` | **b = 0.15** |

c and b are chosen once, here, before any entropy: values that differ appreciably at k~π while leaving the
small-k limit intact. **They are not tuned later.** (2 and 3 share a functional form and differ in the sign and
origin of the coefficient: 2's c₄ is *derived* to cancel the lattice artefact, 3's c is *imposed* as a
deformation. If the derived c₄ coincides with 0.25 I will change 3's c to 0.5 and record the change here.)

## 3. Regions and sizes — FROZEN

- **Equilateral triangle**, three 60° corners. Linear size L = side length in lattice units.
- **Regular hexagon**, six 120° corners. Linear size L = side length in lattice units.
- **Sizes: L ∈ {6, 8, 10, 12, 14, 16}** for both shapes — six points for a three-parameter fit.
- Constraint check, reported: max L/ξ = 0.16, max L/N = 0.10.

**Q2 (square lattice, a(90°)) is DROPPED** per quantum's ruling — most compromised by the leak, and it carried
C3, itself a recall check.

## 4. Entropy and the fit — FROZEN

Ground-state correlators `X = ½K^{-1/2}`, `P = ½K^{1/2}`; restrict to region A; symplectic eigenvalues ν from
`sqrt(eig(X_A P_A))`; `S = Σ [(ν+½)ln(ν+½) − (ν−½)ln(ν−½)]`.

**Fit model (this is the frozen choice, and the thing being independently exercised):**

```
S(L) = α·P(L)  +  β·ln(L)  +  γ
```

with `P(L)` the boundary length in lattice units and `L` the **side length** — this is the length scale inside
the logarithm, frozen. For a region with `n` corners of angle θ: **a(θ) = −β / n**. So a(60) from the triangle
(n=3) and a(120) from the hexagon (n=6). **α is the area (boundary-law) coefficient.**

**Convergence / rejection rules:** a (regulator, shape) fit is REJECTED and reported as rejected if fit R² <
0.999, or if any ν < ½ by more than the clip tolerance, or if any S is NaN/complex. Rejected points are
reported, never dropped silently.

## 5. Gate order — physics-independent FIRST

1. **G0 — small-k convergence of all four regulators.** `ω²/(m²+k²) − 1 → 0` as k→0, at the expected order.
   **Known-fail: any regulator not converging invalidates everything downstream and the run stops.**
2. **G1 — triangle-vs-hexagon AREA agreement.** Same cut, same lattice, so `α_tri` and `α_hex` must agree.
   **Known-fail: relative difference > 5% ⇒ my extraction is broken ⇒ THE STUDY IS DEAD ON MY SIDE AND I SEND
   NO CORNER NUMBERS AT ALL.** Untouched by the leak; independent of whether anyone's physics is right.
3. **G2 — corner extraction**: a(60), a(120), all four regulators, with across-regulator spread (max−min)/mean.
4. **G3 — the free positive control (quantum's, adopted): the AREA coefficient must FAIL to be universal.**
   Its spread must be LARGE. **A small area spread indicts MY extraction, not their claim** — the strongest
   control shape available, because its only pass is a failure of the thing one would naively want.
5. **G4 — the clip band.** Sweep the floor on ν−½ over `{1e-14, 1e-12, 1e-10, 1e-8}` and quote how far every
   reported number moves. **Known-fail: if the clip band is comparable to the corner spread, then the spread IS
   the floor, the universality question is unanswered, and I report that instead of a number.**

## 6. My priors, stated so they are auditable rather than denied

I expect a(60) > a(120), corner spreads well under 1%, and an area spread of tens of percent. **This expectation
is not independent evidence** — it comes from the literature (which supplies the *shape*) and, since the leak,
from bridge's magnitudes. Recorded here so that a result matching it can be discounted appropriately and a
result contradicting it can be recognised as the informative outcome.

**A pass confirms weakly. A disagreement, or a G1/G4 failure, is the finding.**

## 7. What I will report regardless of outcome

The model; these priors; the control designs **and why they were chosen**; the clip band; every rejected fit;
and the across-regulator spreads with their uncertainties. Control *design* is untouched by the leak and quantum
has said it is as informative to them as the numbers.

---

# AMENDMENT 1 — 2026-08-22, after freeze `e283d21`, before any physics
### Appended, not edited. Prompted by quantum; the geometry claim verified here before adoption.

## A1.1 A STRICTLY BETTER G1: two shapes with IDENTICAL corner content

The limitation I flagged in §5 — that G1 compares α across shapes with *different* corner counts (3 vs 6), so a
systematic in the corner extraction shifts both α's together and slips through — has a clean fix, due to
quantum. Use two shapes whose corner content is **identical**, so the corner term cancels *exactly* in the
difference rather than being subtracted approximately.

    H(p, q, r) = { (n1, n2) : |n1| <= p , |n2| <= q , |n1 + n2| <= r }

**VERIFIED HERE, not assumed** (numerically, via convex hull with collinear vertices merged):

    H(6,6,6)   -> 6 corners, all exactly 120.0 deg
    H(6,6,7)   -> 6 corners, all exactly 120.0 deg
    H(5,7,9)   -> 6 corners, all exactly 120.0 deg
    H(6,6,11)  -> 6 corners, all exactly 120.0 deg
    H(6,6,12)  -> DEGENERATES: 4 corners, angles 120/60/120/60 (a rhombus)

**Correction to the stated admissibility condition.** Quantum gave `max(p,q) < r < p+q`. The regular hexagon
`p = q = r` violates the strict lower inequality and nonetheless yields six exact 120° corners. The upper bound
is exactly right — the construction degenerates at `r = p+q`. Corrected condition:

> **max(p, q) ≤ r < p + q**

**NEW GATE G1b — the corner-extraction isolation test.** Fit the *same* frozen 3-parameter model to the
**difference** between an elongated and a regular hexagon at matched scale:

    S_H(R,R,R+2)(L) - S_H(R,R,R)(L)      has ZERO corner content by construction

**Known-fail: β must come out ≈ 0. A non-zero β means my extraction is MANUFACTURING a logarithm, and the study
is dead on my side — no corner numbers sent.** This is what I wanted G1 to be able to say and could not. G1 is
retained as well: it tests something different (α independent of shape at all) and costs nothing.

## A1.2 REPORT THE FULL PAIRWISE MATRIX, not only max−min spread

Quantum ran a mechanism test on a square lattice sweeping `c` in the `m² + K + c·K²` family and found the
pairwise disagreement with the nearest-neighbour regulator **changes sign** at a particular c, while the
dispersion mismatch driving it is strictly positive and monotone. So there is a c at which the quartic regulator
*accidentally agrees* with nn for reasons unrelated to universality.

**Hazard for this run:** if my *derived* c₄ lands near such a cancellation, regulator 2 agrees with regulator 1
spuriously and the across-regulator spread comes out **artificially small** — I would report strong universality
and it would be an artifact of one accidental pairing.

**Mitigation, adopted:** report the **full 6-entry pairwise matrix** of corner coefficients, not only the
max−min spread. A max−min statistic does not even move when one accidentally-tight pair sits between the
extrema, so collapsing to a single number *hides exactly this failure*. The matrix makes it legible at no cost.

**On why this disclosure was accepted despite the isolation agreement** — quantum's test, and it is a good one:

> **The question is whether a disclosure biases toward AGREEMENT or toward SKEPTICISM.** This one tells me a
> small spread may be artifactual, which makes me *harder* to satisfy, not easier. Withholding a hazard that
> could make my result spuriously support theirs would be the worse error.

Logged in `DISCLOSURES.md` as sent.

## A1.3 CONDITIONING — L RANGE KEPT, condition number reported

Quantum computed the design-matrix condition number for `[L, ln L, 1]`:

    L = 6..16 (frozen)  cond = 407      L = 6..20  cond = 370      6..24  cond = 361      6..28  cond = 364

**Decision: the frozen range 6..16 STANDS**, for a physics reason rather than inertia — extending to L = 20
puts L/ξ at 0.20, and the clean corner logarithm assumes region ≪ correlation length. A 12% conditioning gain
does not buy a weakened `L ≪ ξ`.

**But the flag is real**, so: `cond = 407` is reported alongside every fit, and the fits are **additionally**
repeated on L = 6..20 as a **robustness check explicitly labelled as outside the frozen range**. Frozen result
and robustness check are reported separately and never merged.
