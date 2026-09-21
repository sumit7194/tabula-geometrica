# PRE-REGISTRATION — leg 6, the blind triple

**Frozen before the metrics are transcribed and before any number exists.** Three stationary axisymmetric
metrics (A, B, C) supplied by TheBridge, key sealed in ansatz's repo. **I have not read the key and will not.**

## What was supplied, and what was NOT

Supplied: the five non-zero components per object in `(t, r, θ, φ)`, plus `a` and `ε`. One scope line from the
operator — *"this does not test whether an invariant outside your basis is detectable"* — and nothing else: not
why the objects were chosen, not what is expected, not how they relate.

**Contrast with leg 3, deliberately.** There I was told the answer's structure before running and had to file the
verdict as INFORMED. Here I have been told **nothing that narrows the answer**, and the one scope line *removes*
a claim rather than adding one. So this verdict can be filed blind, and that is the difference between the two
legs.

## The instrument, unchanged

§99's `conserved`/`heldout` engine driven exactly as §161/§168 drive it. Nothing about the engine is re-tuned
for this leg; only `metric_inv` is generalised to accept a supplied metric instead of a hardcoded one.

**Manifest constants whitened GLOBALLY.** `E = −p_t` and `L = p_φ` are fixed to the same values across the whole
ensemble, so they carry zero across-ensemble variance and drop out of the generalized eigenproblem. Any
conserved direction returned is therefore a genuinely NEW invariant, not a repackaged Killing vector. The mass
shell `2H = −1` is fixed for the same reason.

## The ladder, frozen

Momentum degree **{2, 3, 4}** × coordinate basis **{polynomial, rational}**, held-out validated on disjoint
trajectories, 3 seeds. Reported per object as the full grid of held-out variance ratios — **the ladder, not a
label**, which is what was asked for.

## Verdicts, frozen

- **EMIT** := min held-out ratio over the grid **< 1e-10** — an invariant conserved to integration precision,
  as Kerr's Carter is (§92: 1e-28; §161-A: 2.2e-19).
- **CERTIFY-RELATIVE-TO-BASIS** := min held-out ratio **> 1e-8** across the whole grid, with a clean integrator.
- **In between: no label.** I report the number and say it is between the thresholds. Inventing a third verdict
  after seeing the data is how a screen becomes a story.

## KNOWN-FAIL CONTROL (L1) — binding, and it is per-object

At **ε = 0** every object should reduce to Kerr, where the Carter constant exists and **must** be recovered.
Run each object's own code path at ε = 0 and require EMIT.

> **If ε = 0 does not emit on an object, my instrument is blind on that object's substrate and NO VERDICT
> ISSUES for it.** Not a certify — no verdict. A screen that cannot find an invariant that is definitely there
> has not earned the right to report that one is absent.

This is §178's L1 discipline applied per-object rather than once for the leg, because the three objects have
different `g_rr` and a control that passes on A says nothing about C.

## Integrator gate (G0)

Relative drift in `H` along the flow **< 1e-7** for every object. A certify from a drifting integrator is an
artifact, and the floor must be set by the physics rather than by the step size.

## What I will NOT do

- **Not look at the sealed key**, before or after reporting.
- **Not tune per object.** Same degrees, same bases, same integrator settings, same seeds for all three. If one
  object needs different treatment, that is a finding to report, not a knob to turn.
- **Not report a rank ordering or a grouping.** I was given three objects with no stated relation; producing a
  "these two are alike" claim would be an inference dressed as a measurement.
- **Not explain a surprising result tonight.** Report the ladder; interpretation waits for the unblinding.

---

# L1 CONTROL FAILED ON FIRST RUN — instrument defect found and diagnosed (2026-09-22)

**No verdict has been issued for any object, and none will be until the control passes in both directions.**
This section records the failure and the diagnosis; nothing above this line was edited.

## What the first run gave

Integrator clean: `H` drift **6.7e-15 … 8.8e-15**, four orders inside the 1e-7 gate. But the **ε = 0 control**,
where every object reduces to Kerr and the Carter constant definitely exists, returned a best held-out of
**4.1e-8** — five orders short of EMIT (1e-10), and formally in CERTIFY territory. **The screen could not find
an invariant that is certainly there.** Per the frozen text, that means *no verdict issues*, not a certify.

One useful side-result: at ε = 0 the ladder is **numerically identical across A, B and C**
(2.8434e-07 / 5.5270e-08 / …), which is what it should be if all three reduce to the same Kerr metric — an
unplanned check that the three transcriptions share the correct ε → 0 limit.

## The diagnosis, in the order it was done

1. **Is the invariant actually conserved on my trajectories?** Analytic Carter
   `Q = p_θ² + cos²θ[a²(1−E²) + L²/sin²θ]` drifts **4.6e-14** along the flow, and its across-ensemble spread is
   **8.5e-2** — present, conserved, and *not* whitened out. Meanwhile `H`'s across-ensemble spread is exactly
   **0**, so the shell is correctly whitened. The physics side is sound.
2. **Is it in the library's span?** Yes — the analytic Carter direction scores held-out **2.7e-27**, a perfect
   emit, while the engine's best over *all 31* returned directions is 6.0e-8. **The engine could represent it
   and could not find it.**
3. **Degenerate null cluster?** No. One small eigenvalue (1.65e-09), then a jump to 5.67e-05.
4. **Tighter conditioning?** Worse monotonically (6.0e-8 → 7.7e-4 as the cut goes 1e-9 → 1e-2).
5. **The actual cause: the whitening cut was discarding the directions Carter lives in.** `s99.conserved`
   hardcodes `keep = s > 1e-9 · s.max()`, which drops 8 of 39 directions here, and Carter has ~41% of its norm
   in the discarded subspace:

        tol      kept    engine best      Carter captured
        1e-9     31/39   6.0044e-08       0.5892
        1e-11    36/39   6.1220e-11       0.7494
        1e-13    38/39   1.9848e-12       0.7771
        1e-15    39/39   4.1794e-17       1.0000

**My conditioning sweep started at 1e-9 and only went tighter.** The fix was in the direction I never tested,
and I would have concluded "instrument blind on this substrate" on a sweep that never looked the right way.

## The trap this fix walks into, and the control that must clear it

**Loosening a cut until the control passes is how a gate stops being a gate** — deepstrain's line, and it
applies directly. A looser cut widens the searchable space, which risks a FALSE EMIT on an object with no
invariant. So the conditioning cut is not adopted on the strength of the ε = 0 side alone.

**A two-sided control is running:** the same cut must (a) EMIT on ε = 0 Kerr, where Carter exists, **and**
(b) CERTIFY on Kerr with the §99/§168 quadrupole bump, which is known to destroy Carter. **A cut that passes
(a) and fails (b) is rejected**, however good the ε = 0 number looks.

Held-out validation is the structural reason to expect this can work: conditioning decides what is
*searchable*, held-out decides what is *real*, and a spurious direction admitted by a loose cut should not
generalise to disjoint trajectories. That is an argument, not a measurement — hence the control.

---

# RESULT — the ladder per object (2026-09-22). Nothing above this line edited.

**Two-sided control PASSES**, so verdicts may issue:

    positive (eps=0 Kerr, Carter EXISTS)        3.73e-17   EMIT      OK
    negative (bumped Kerr, Carter DESTROYED)    4.97e-06   CERTIFY   OK

**Per-object L1 control PASSES on all three** — the instrument is demonstrably not blind on any of these
substrates, which is what earns the right to report an absence:

    A   eps=0  min 7.8543e-18  EMIT     |  B  1.0238e-17  EMIT  |  C  9.1393e-18  EMIT

Integrator drift 9.3e-15 … 1.3e-14 throughout, four orders inside the 1e-7 gate.

## The ladders at eps = 0.05

Reported as **four distinct rungs, not six**: the feature builder includes only EVEN total momentum degree, so
`deg3` is identical to `deg2` by construction. Presenting six would make the ladder look wider than it is.

    object   d2_poly     d2_rat      d4_poly     d4_rat      min        verdict
    A        2.237e-06   5.373e-07   6.455e-07   4.474e-07   4.474e-07  CERTIFY
    B        2.237e-06   5.370e-07   6.452e-07   4.527e-07   4.527e-07  CERTIFY
    C        1.535e-06   7.698e-08   1.636e-07   8.195e-08   7.698e-08  CERTIFY

**All three CERTIFY-RELATIVE-TO-BASIS** by the frozen threshold (min held-out > 1e-8 across the whole grid,
clean integrator, control passing). None falls in the 1e-10 … 1e-8 no-label band.

**Located margin:** the same engine on the same code path reaches **1e-17 … 1e-18** when an invariant IS
present. The screened objects bottom out at **1e-7 … 1e-8** — roughly **ten orders** above the emit level. The
certificate is not marginal.

## What this does NOT say

Per the pre-registration, and per the operator's own scope line: **this does not test whether an invariant
outside the basis is detectable.** A certify here is CERTIFY-RELATIVE-TO-{polynomial, rational} up to momentum
degree 4 — the §160/§161 verdict class, a measured boundary of the basis and not a claim of non-existence.

**No ordering or grouping is asserted.** Three objects were supplied with no stated relation; the ladders are
reported per object as requested and any relation between them is for the unblinding, not for me to infer from
three numbers.

## Unplanned check that came free

At eps = 0 the polynomial rungs are numerically **identical across all three objects** (1.3236e-06 and
5.5114e-08 to five significant figures). That is what must happen if the three transcriptions share the correct
Kerr limit, and it is an independent check on the transcription that the design did not ask for.

---

# AMENDMENT — the ε-scan, pre-registered before running (2026-09-22)

Unsealed: **A keeps Carter (rank-2), B destroys it (A with one coefficient × 1/3), C keeps it rationally.**
ansatz corrected their own scope before any conclusion was drawn: **their claim that A keeps Carter is FIRST
ORDER in ε, and the test ran at ε = 0.05.** A first-order invariant leaves an O(ε²) residual at finite ε, so
A's Carter is not an exact invariant of the object actually sent and **the test as constructed could not
separate A from B.** The naive reading — a false CERTIFY on A, a partial kill of `legible ⟺ integrable` — is
therefore not available, in either direction.

## The discriminator is the SCALING EXPONENT, not the magnitude

TheBridge's sharpening, and it is the right instrument: if A's Carter survives at first order and B's does not,
their residuals carry **different powers of ε** and must separate as ε shrinks, whereas anything common to both
metrics scales identically and leaves `B/A ≈ 1` at every ε.

**Their arithmetic needs one correction, and it makes the test easier rather than harder.** They tabulated A as
ε² and B as ε¹. But the reported margin is `heldout = mean_traj(var_within) / var_total` — a **variance**, i.e.
the residual amplitude **squared**. So:

    residual amplitude   ->   held-out ratio      predicted exponent
    A   O(eps^2)              O(eps^4)            4
    B   O(eps^1)              O(eps^2)            2

    eps       A (eps^4)    B (eps^2)    B/A        [their B/A]
    0.05      4.474e-07    4.527e-07        1.0    [1.0]
    0.005     4.474e-11    4.527e-09      101      [10.1]
    0.0005    4.474e-15    4.527e-11    10119      [101]

**Frozen predictions, and each can fail:**

- **(i) FINITE-ε explanation holds** → fitted exponents **A ≈ 4, B ≈ 2**, separating by ~10² per decade of ε.
- **(ii) BASIS explanation** → A's first-order correction is unrepresentable in my features, A does not follow
  ε⁴, and the exponents do not split as predicted.
- **(iii) Neither** → **both objects fit the SAME exponent**, `B/A` stays ~1 at every ε, and the margin is
  measuring something common to both metrics that **neither ansatz nor I have named.** This is a real possible
  outcome and the one I would most want to know about.

**If I measure A ≈ 2 and B ≈ 1, my own derivation above is wrong** — the statistic would not be behaving as a
variance — and that is a finding about my instrument, not about the objects.

## Design

Five log-spaced ε per object (A, B **and C**, since C costs the same code path and its exponent is informative),
`{0.05, 0.0158, 0.005, 0.00158, 0.0005}`, exponent fitted by least squares on log(min held-out) vs log(ε)
across all five — **a fitted slope, not a two-point ratio.**

**CENSORING GUARD (§177 W3, entry 19).** The ε = 0 control emits at ~1e-17, which is the instrument floor. A's
predicted 4.5e-15 at ε = 0.0005 clears it by ~2.5 orders, but **if any point sits at the floor the exponent fit
is censored and that point is excluded with the exclusion reported** — a truncated statistic carries less than
the boolean, and fitting through a floor manufactures a shallow exponent.

**Blinding note:** the key is now known, so **this scan is NOT blind** and will not be reported as if it were.
It is a mechanism test with a frozen prediction, run after unsealing, and labelled as such.

---

# ANALYTIC CARTER DRIFT — engine-free, and it does not support the hypothesis (2026-09-22)

Measured directly along the flow: `Q = p_θ² + cos²θ[a²(1−E²) + L²/sin²θ]`. **No engine, no basis, no
conditioning, no eigenproblem, no fit statistic** — the residual itself rather than a statistic derived from it.

    obj   drift(eps=0.05)   drift(eps=0.005)   ratio    fitted exponent
    A     7.13040e-03       7.10580e-04        10.03    1.002
    B     7.13050e-03       7.10580e-04        10.03    1.002
    C     5.13630e-04       5.09950e-05        10.07    1.003
    all   4.01e-14 at eps=0 (integrator floor)

**A and B are identical to five significant figures** (1.4e-05 relative at ε=0.05, indistinguishable at 0.005),
and **every exponent is 1, not 2**. So A does not conserve `Q` better than B, and the finite-ε rescue fails its
own prediction.

## The scope limit, stated against my own result

I measured the drift of the **undeformed Kerr** `Q`. If A's survivor is a **deformed** invariant `Q + ε·K₁` —
and ansatz's description of C's survivor has exactly that form — then bare `Q` drifts at O(ε) while the real
invariant is conserved, producing precisely this table. **So this does NOT establish that A has no rank-2
invariant.** It establishes something narrower: *whatever distinguishes A from B is not visible in the drift of
`Q`.* Whether a deformed rank-2 invariant survives is what the screen searches, and the screen certified.
TheBridge has asked ansatz for `K₁` explicitly; with it the same engine-free measurement settles the branch.

## THE PRE-SCAN CONSTRAINT — measured, hypothesis-free, and it survives the scan either way

    A-B gap in the RESIDUAL    1.40e-05 relative
    A-B gap in the MARGIN      1.19e-02 relative
    ratio                            845x

> **~~Under any power law `margin ~ residual^n` with n > 0, the margin gap must TRACK the residual gap.~~**

**WITHDRAWN, within the hour, and the withdrawal is the point.** TheBridge proposed this framing, called it
"the strongest result of the night", and I recorded it here on that basis. **It does not hold.** ansatz then
established from their own solver that **A's survivor is `Q + ε·K₁`, never bare `Q`** — a deformation is
compatible *iff `Q` can be corrected*, not iff `Q` survives untouched.

So the two gaps being divided are **gaps in different objects**: the margin is the residual of the *best object
in my basis*, while the 1.4e-05 is the residual of *bare `Q`*, which is the wrong object for A and B alike.
**There is no reason they should track.** The arithmetic was mine and correct; the inference was TheBridge's
and I adopted it into a permanent record without checking what the two quantities were residuals *of*.

**Entry 51, committed tonight, in the file where I am writing about entry 51.** An inherited figure arrives
pre-attached to a conclusion, and "strongest result of the night" is about as pre-attached as a conclusion
gets. What survives is a **question**: the margin separates A from B by 1.2% while bare `Q` separates them by
0.0014%, and that is unexplained — but it is not evidence about whether my margin tracks Carter, because
nobody has yet measured the thing it would have to track. **`K₁` is what makes it measurable.**

## The unpredicted signal, flagged so it does not get absorbed

**C's drift is 13.9× below A's and B's, at both ε.** Engine-free, and **no one's hypothesis mentions it** — the
prediction under dispute was about A-versus-B. C was supposed to be the object with the *rational* survivor,
not the one whose *undeformed* `Q` is best conserved. Recorded as wanting an explanation rather than as
evidence for anybody's account.

**A PROPOSED DISSOLUTION THAT I COULD NOT REPRODUCE.** TheBridge relayed that C's deformation is simply ~13.5×
smaller (`|h_A| ≈ 0.0873` vs `|h_C| ≈ 0.00646` at r = 6.998), matching my 13.88 to 2.7%. **Computed here
independently, it goes the other way.** Relative deformation `|g(0.05) − g(0)| / |g(0)|` at the same radius:

    comp       A           C          C/A
    g_tt       3.114e-04   9.604e-05   0.31
    g_rr       1.980e-04   5.570e-04   2.81
    g_thth     1.427e-04   5.214e-04   3.65
    g_phph     1.415e-04   5.171e-04   3.65
    summed     1.3e-04     4.8e-04     3.6

**C's deformation is LARGER than A's on four of five components — and C's `Q` drift is 13.9× SMALLER.** Their
`|h_A| = 0.0873` matches no component ratio I can compute, so the two of us are measuring different quantities
and calling both `|h|`. That is the same "divided things that looked commensurable" failure they had just
confessed to, appearing immediately in the comparison of our two definitions of it.

**So C's 13.9× is NOT dissolved as far as I can verify**, and it stays on the open list.

**THREE PROXIES NOW, ALL FAILING.** TheBridge then made the correct objection to *my* proxy as well: `dQ/dλ`
runs through the **connection**, so it depends on **derivatives** of the perturbation, not on `|Δg|/|g|`.
Computed:

    ansatz   coefficient-space |h|            C is 13.5x SMALLER
    mine     metric-space |dg|/|g|            C is  3.6x LARGER
    derived  |d(dg)|/|d(g0)|   d/dr           A/C = 1.82
                               d/dtheta       A/C = 0.28
    MEASURED Q-drift                          A/C = 13.88

**Not one of the three reproduces 13.88**, including the derivative proxy that was supposed to be the right
kind of quantity.

**And there is a reason norms were always going to fail here.** `Q = K_ab p^a p^b` with `K` the Kerr Killing
tensor; since `∇⁽⁰⁾₍c K_ab₎ = 0`, the drift comes entirely from the perturbation to the connection,
`δΓ ~ ∂(Δg)`, **contracted with `K` and three momenta in one specific combination.** A norm over components
discards exactly that contraction structure — it cannot see cancellations between components, and the
components here differ in *opposite directions* (C larger in θθ, smaller in tt). **So the governing quantity is
not any norm of the perturbation; it is one contraction of its derivative, and nobody has computed it.**

TheBridge reached the same conclusion from the other side — *"the one that governs the drift is a third
thing"* — and this measurement says the obvious third thing is not it either. **C's 13.9× is open, and open for
a better reason than a naming collision: the explanatory variable has not been identified by anyone, and three
natural candidates are now excluded.**

---

# K₁ MEASURED — it does not make `Q + εK₁` conserved on A (2026-09-22)

ansatz supplied `K₁` for A, the O(ε) correction such that `Q + ε·K₁` should be conserved to O(ε²). Measured
along the flow, **normalised against `|Q|`** — the same denominator as the bare-`Q` number, because `K₁` is
fixed only up to a background Killing tensor and dividing by `|Q + εK₁|` would be a convention-dependent ratio
wearing the same name (TheBridge's warning; at `χ=0.9, y=0.2` the correction is 11× `Q`).

    eps        bare Q drift      Q + eps*K1 drift    ratio
    0.0        4.0062e-14        4.0062e-14          1.00x
    0.05       7.1304e-03        6.3180e-02          0.11x
    0.005      7.1058e-04        6.3055e-03          0.11x

    exponent:  bare Q 1.002      Q + eps*K1 1.001    (predicted 2)

**`Q + εK₁` drifts 8.9× WORSE than bare `Q`, and still at exponent 1.**

## The convention branch is closed, from two directions

I pre-stated that exponent-1-with-no-drop would be ambiguous between *"`K₁` is not A's survivor"* and *"my
`P_y` convention is wrong"*. Both routes now close it:

**(a) Structurally.** `K₁` is given in `y = cos θ`, so `P_y` conjugate to `y` requires `p_θ² = P_y²(1−y²)` —
a `P_y²` term must carry `(1−y²)` and a `P_φ²` term must carry `1/(1−y²)`. The `P_y²` bracket factors exactly
(verified symbolically, `lhs − rhs → 0`, not at sample points):

    -x²y⁴+2x²y²-x²-4xy⁴+6xy²-2x+18y⁴-27y²+9  ==  -(y-1)(y+1)(x²y²-x²+4xy²-2x-18y²+9)

which is Carter's own pairing. **`P_y = −p_θ/sin θ` is correct.** (Argument due to TheBridge; verified here.)

**(b) Empirically.** All eight momentum/energy conventions give **exponent 1.001 and 0.11×**:

    -p_th/sin ±E   6.3180e-02   1.001      p_th  ±E   6.6415e-02   1.001
    +p_th/sin ±E   6.5578e-02   1.001     -p_th  ±E   6.4362e-02   1.001

**No convention rescues it**, so the result never depended on the choice.

## What this does and does not establish

**Does:** `K₁` as transcribed into this harness does not correct `Q` on A; it degrades it.

**Does NOT:** distinguish (i) the solver's `K₁` is wrong, (ii) a transcription slip in transit, (iii) a
convention difference *other* than momentum — `M=1` vs `a=0.6`, their `x` vs my `r`, signature. **The momentum
convention was checked to destruction; the others were not**, and six of the night's seven dissolutions were
exactly this species, so the remaining ones are not assumed fine because the checked one was.

**The falsifiable split, one command on their side:** if ansatz evaluates `dQ/dλ` and `d(Q+εK₁)/dλ` on their
own geodesics with their own conventions and gets a **drop**, the fault is in transit; if they get the same
**rise**, `K₁` is wrong at the source.

## The one instance caught BEFORE a number existed

The `y = cos θ` Jacobian — `P_y = p_θ·(dθ/dy) = −p_θ/sin θ`, a factor running 1.0 to 1.28 and flipping sign
across the band. Feeding `p_θ` straight in would have produced a **plausible** wrong answer in the decisive
measurement, silently. Every other instance tonight was found *after* a number existed and had travelled. The
habit that caught it was deriving the Jacobian rather than assuming it; the lesson that made me flag it for
confirmation rather than proceed on my own derivation was the 845×, three hours old.

---

# LEG 6 RESOLVED — the CERTIFY on A is correct, and the missing function class is named (2026-09-22)

## The measurement that worked, and the one that did not

**ε swept UPWARD succeeded.** The objects are **exact in ε and truncated in χ**, so raising ε costs no
truncation error and helps quadratically; every sweep for three rounds went the other way, shrinking the
parameter that was already exact while holding the truncated one large.

    excess/eps = F0*c + A*eps        five points, eps = 0.05 .. 0.30, at chi = 0.075

    A    = 4.0708e-07      K1's QUADRATIC residual coefficient, MEASURED
    F0*c = 7.3811e-07      the floor's own O(eps) drift, SEPARATED
    max relative residual  5.94e-06
    quadratic share at eps=0.30: 14.2%

**The crossover `ε* ≈ 1.8` was never reachable and never needed.** A two-parameter fit separates two terms;
it does not require one to dominate. "Push ε past ε\*" was the framing that sent me chasing an unreachable
target, and it was retracted by its author.

**χ swept DOWNWARD stayed censored at every point** — corrected/floor exponent 0.011 at χ=0.01, 0.012 at
χ=0.003. The floor carries its own O(ε) drift, so it rises with ε in lockstep and no amount of χ-lowering
separates them.

## Why the χ floor exists at all, and why it is χ³ exactly

`g_tφ = −2ar sin²θ/Σ` is **odd in a** — verified from my own metric (`g_tt` even, `g_tφ` odd, `g^tφ` odd). So
`H` carries odd powers of χ while chain4 is even and stops at χ². The bracket therefore vanishes at χ⁰, χ¹, χ²
— which is all ansatz claimed and all they could check — and **the first unchecked order is χ³**. Measured
floor exponent: **3.032** on an independent sweep (first sweep gave 3.13; the marching sequence 3.17/3.13/3.08
was χ³ approached from above). Mechanism due to TheBridge; the number that refused to be 4 is what located it.

## THE FINDING FOR THIS PROJECT — and it is settled from the expression, not from a run

    K1's denominator:   x^4 (x-2) (y^2-1)    i.e.  r^4 (r-2) sin^2(theta)
    my d2_rat library:  1, cos2, r, r2, cos2*r, 1/sin2, 1/r, 1/r2, cos2/r, cos2/r2

**There is no `(r−2)` denominator in my basis at all.** Not present with wrong coefficients — the function
class is absent by construction. So `chain4 + εK₁` is **not representable in my degree-2 rational library at
any coefficients.**

> **The CERTIFY on A is therefore correct AS A CERTIFY-RELATIVE-TO-BASIS. The invariant exists, the screen did
> not find it, and the reason is precisely the one the operator's scope line named in the opening message:
> *"this does not test whether an invariant outside your basis is detectable."*** Not a miss — the boundary,
> with the missing function class identified by name.

**This sharpens §161's biconditional exactly as that leg pre-registered.** `legible ⟺ integrable` survives in
the form `legible ⟺ integrable with a REPRESENTABLE invariant`, and `(r−2)` is a **concrete witness** to the
gap rather than a hypothetical one. The partial kill §161 anticipated has arrived, located, and in the
direction it predicted.

## What the numerical exponent does and does not decide

ansatz proved `{H_def, chain4 + εK₁} = 0` at O(ε) **exactly, through χ²**. So a numerical exponent-2 result is
an **independent-route confirmation of a symbolic result** — real value given how many relayed claims failed
tonight, but not the leg's open question. **The open question was basis representability, and it is answered
above without a single further run.**

## A circularity in `c`, and its escape

`c ≡ (excess/ε)/F₀` absorbs any O(ε) residual of `K₁` into itself, so measuring `c` cannot by itself
distinguish floor-drift from a `K₁` failure. It escapes only because the O(ε) cancellation is **proven**
through χ², leaving χ³+ as the only possible source. Truncation by construction rather than by assumption.
(TheBridge raised the circularity against their own proposed measurement.)

## Measured, against an assumption that was flagged and failed

`c` is **not χ-independent**: 0.2279 at χ = 0.075, 0.566 at χ = 0.01 — `c ∝ χ^−0.45`. Every headroom figure
resting on χ-independence moves. **Flagged in advance by the party who could not check it, and it is the second
such flag tonight to land on the assumption that broke** (the first was `q`). The flag works by naming the
boundary of one's own instruments rather than by being cautious in general.
