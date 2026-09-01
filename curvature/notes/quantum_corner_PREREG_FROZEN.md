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

---

# AMENDMENT 2 — 2026-08-22, still before any physics
### My Amendment-1 patch was ALSO wrong. Independently re-verified here.

## A2.1 The admissible family is the TRIANGLE INEQUALITY

Amendment 1 corrected quantum's `max(p,q) < r < p+q` to `max(p,q) ≤ r < p+q`, because the regular hexagon
`p=q=r` was excluded by their own rule. **That patch is also too strong.** I tested only the upper boundary —
the one quantum had pointed at — and neither of us tested *below* `max(p,q)`.

**Independent exhaustive scan run here** (p,q ∈ 2..12, r ∈ 0..25, convex hull with collinear vertices dropped):

    3146 cases · 1133 true six-corner-120° hexagons · MISMATCHES vs the triangle inequality: 0

> **H(p,q,r) has six exactly-120° corners  ⟺  |p − q| < r < p + q.  Both bounds strict.**

Confirmed at both ends: `H(6,6,3)`, `H(6,6,4)`, `H(6,6,5)` are all valid hexagons that both earlier rules
discarded; `H(5,7,2)` and `H(5,7,1)` degenerate to the 120/60/120/60 rhombus, as does `H(6,6,12)` at the top.
**Both failure modes are the same failure** — whichever constraint goes slack drops you to four corners.

**Why the correct rule had to be symmetric, and the tell we both missed:** the three constraint families are
related by the lattice's 3-fold symmetry, so any correct condition is symmetric in (p,q,r). `max(p,q)`
privileges two of the three and therefore could not have been right. The regular hexagon (R,R,R) is an
equilateral triangle — deep in the interior, as it should be.

## A2.2 G1b becomes TWO-SIDED

**The frozen G1b design is untouched by A2.1** — `H(R,R,R+2)` and `H(R,R,R)` are admissible under all three
versions of the rule, and I am not re-planning around a correction that does not reach the design.

But the corrected family makes a strictly stronger test available at no cost (quantum's suggestion):
`H(R,R,R−2)` sits on the *other* side of the reference shape and is equally valid. **G1b is now two-sided:**

    beta[ S_H(R,R,R+2) - S_H(R,R,R) ] ~ 0     AND     beta[ S_H(R,R,R-2) - S_H(R,R,R) ] ~ 0

> An extraction that manufactures a logarithm out of the shape change would have to manufacture it with the
> **same sign in both directions** to escape a two-sided test. One-sided, a systematic slips through.

## A2.3 A standing correction to how I read this collaborator

Quantum's note, which I am recording because it changes how I should treat their input rather than being a
courtesy: the elongated-hexagon claim was asserted *from reasoning about which constraints are active* and never
executed — **"a claim that felt derived, never actually run."** It was wrong twice, and both errors were found
only by drawing the hulls.

> **Standing rule for this collaboration: any claim carrying "clearly" or "by construction" with no evidence it
> was executed is UNVERIFIED until I run it.** Applied to A2.1 itself — I did not adopt their triangle
> inequality on their say-so; the 3146-case scan above is mine.

---

# AMENDMENT 3 — 2026-08-22, before G1b/G2 have been run
### Anti-guards found in my own frozen gates. Two of them, one being the headline claim.

**The failure class** (found by TheBridge, named by ansatz, relayed by quantum as a skepticism-increasing
disclosure): **any assertion phrased as a ratio, relative error, or fraction-of-baseline has a MEASURED
denominator** — so corrupting the data can inflate the denominator until the check passes. Sensitivity runs
backwards: *the more damaged the data, the easier the gate is to satisfy.* An **anti-guard**. Quantum found two
in their own harness and all 26 assertions stayed green on areas wrong by three orders of magnitude.

**Audit of my frozen gates:**

| gate | statistic | denominator | verdict |
|---|---|---|---|
| G0 | \|fitted_p − expected\| < 0.35 | k² is **chosen** (mode index) | safe |
| G1 | \|α_tri − α_hex\| / mean(α) | mean(α) **measured** | **ANTI-GUARD** |
| G1b | \|β\| < tol | tol relative to a measured scale | at risk |
| G2 | (max−min)/mean of a(θ) | mean **measured** | **ANTI-GUARD — the headline** |
| G3 | (max−min)/mean must be LARGE | inflating the mean makes it *harder* | guard-correct (inverted) |
| G4 | band / spread | both measured | at risk |

**G2 is the one that matters.** "Corner spread is small" is the universality claim, and as written a broken
extraction that inflates every a(θ) equally would *strengthen* it.

**MITIGATION, adopted verbatim from quantum: pair every relative assertion with an ABSOLUTE bound on its
denominator.** Concretely, and these are now part of the frozen design:

- **G1** additionally requires `α_tri` and `α_hex` each finite, positive, and within a stated absolute band;
  the relative agreement is only read if both absolute bounds hold.
- **G1b** additionally requires the *single-shape* β to exceed an absolute floor. Without that, β_difference ≈ 0
  is satisfied trivially by an extraction that returns β ≈ 0 for **everything** — including shapes that do have
  corners. **The zero-test needs a demonstrated non-zero.**
- **G2** additionally requires each a(θ) to lie within a stated absolute band before its spread is quoted.
- **G4** additionally requires absolute bounds on both the clip band and the spread.

**AND THE MUTATION TEST THAT CATCHES THIS MUST BE ADDITIVE.** Quantum's detail, which is the part I would have
got wrong: **a common multiplicative rescaling leaves every ratio exactly invariant**, so the obvious corruption
test — scale the data and confirm the gates fire — shows nothing, and the conclusion is "clean". Corrupt
**additively** instead. I will run an additive mutation against the full gate set before filing any number, and
report which gates caught it.

> **A gate that gets easier as the data gets worse is not a weak gate. It is a gate pointing the wrong way**,
> and it will be greenest exactly when it matters most.

---

# AMENDMENT 4 — 2026-08-23. A NEW gate (G1b-v2), not a retry of the failed one.
### Designed and power-analysed BEFORE running. User-authorised after quantum's session ended.

**STANDING CHANGE OF CLAIM, stated first.** quantum's session is gone and never ruled. This continues as
**tabula's own instrument check**, NOT an independent replication — that claim died with the contamination and
cannot be revived by finishing the work. Any result below is "does *my* extraction survive *my* gates".

## A4.1 Why the obvious repair does not work, found before freezing it

The post-mortem blamed `corr(log R, 1/R) = -0.9899` over R = 6..16 and I was about to widen the range. Measured
first:

    range ratio   2.7    5.0    6.0    8.0   10.0
    corr        -0.990 -0.973 -0.967 -0.958 -0.955

**Widening does not fix it.** log R and 1/R are intrinsically similar over any bounded positive range; ratio 10
still leaves 95% collinearity. **A gate that needs β estimated cannot be rescued by more range.**

## A4.2 The fix is a different STATISTIC: never estimate β, ask whether the log column is NEEDED

    model A:  [dP, 1, 1/R]              subleading structure, NO log
    model B:  [dP, 1, 1/R, log R]       adds the log
    statistic: nested F-test, p-value

This never requires β to be identified. **1/R must be in BOTH models** — omit it and log R proxies for it and
the test fires with no corner content present (that is the trap quantum's diagnostic exposed).

## A4.3 MEASURED POWER, pre-registered — the thing G1b never had

Monte Carlo, realistic 1/R structure, noise 3e-5, α = 0.01, effect = β at 10% of the single-shape logarithm:

    range              n    false-positive    power
    6..16 step2 (G1b)  6         9%            12%      <- THE ORIGINAL GATE
    5..24 geom        12         1.5%          72.8%
    6..30 geom        12         2.0%          74.0%
    3..24 geom        11         2.8%          99.8%    (rejected: R=3 is 37 sites, artifact regime)
    5..30 geom        12         0.0%          95.8%    <- ADOPTED

> **The original G1b had 12% power and a 9% false-positive rate.** It could not have detected a real violation,
> and its FP rate is the same order as the 15-23% residual it reported. **It was measuring noise.** That is a
> stronger and more useful statement than "under-powered", and it is the number the first design never produced.

## A4.4 FROZEN DESIGN

- **R = [5, 6, 7, 8, 10, 11, 13, 16, 18, 22, 25, 30]** (12 points, geometric)
- **Elongation SCALES with R: δ = round(R/2)**, giving H(R,R,R+δ) and H(R,R,R−δ), both admissible under the
  triangle inequality at every R (checked). **dP now varies 8..60 instead of being constant at 8**, so the
  design matrix is no longer rank-deficient: **cond 6.0e16 → 449.7**.
- **Two-sided**, as before.
- **Known-fail: p < 0.01 on either side ⇒ log structure exists beyond the subleading term ⇒ the extraction is
  implicated ⇒ THE STUDY IS DEAD AND NO CORNER NUMBERS ARE SENT.**
- **Absolute floor (Amendment 3):** the same F-test on the SINGLE shape must fire decisively, or the test cannot
  distinguish a working extraction from one that never needs a log column.

## A4.5 A DECLARED DEVIATION, not a quiet one

R = 30 gives **L/ξ = 0.30**, which is not "≪ correlation length" as the frozen file words it. Power required
either small R (lattice-artifact regime, 37 sites) or large R; I took large. **Declared, with a control:** the
whole gate is re-run at **m = 0.005** (ξ = 200, so L/ξ = 0.15) and the verdict must not change. If it does, the
deviation is doing the work and the result is withdrawn.

## A4.6 Numerical note (not a model change)

ν² are the eigenvalues of `X_A P_A`; since X_A is SPD this is similar to the symmetric PSD matrix
`X_A^{1/2} P_A X_A^{1/2}`, so `eigvalsh` replaces `eigvals` — faster and real-by-construction rather than
real-by-discarding-an-imaginary-part. Same spectrum, better conditioning. Verified equal on the old sizes.
