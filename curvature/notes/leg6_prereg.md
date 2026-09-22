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

**AND IT IS A PROOF, NOT A PROPERTY OF MY PARTICULAR LIST** (argument due to TheBridge, verified here). `K₁`'s
pole at the horizon is genuine, not cancelled: at `x = 2` every `(x−2)` factor in the numerator drops, leaving

    numerator(x=2) = 1024*chi^2*P_t^2*y^2*(y-1)*(y+1)     residue = 64*chi^2*P_t^2*y^2*(y^2-1)

nonzero at generic `P_t, y`, against a simple zero in the denominator. *(TheBridge quoted the residue as
`64χ²P_t²y²`; the `(y²−1)` factor belongs with it. The conclusion is unaffected.)*

My basis, as functions of `r`, spans only `{r², r, 1, 1/r, 1/r²}` — **every one analytic at r = 2.** A finite
linear combination of functions analytic at a point is analytic at that point. `K₁` has a pole there.
**Therefore it is not in the span, at any coefficients.**

> **The argument uses only the POLE LOCATION, not the degree.** Any basis whose r-dependence is built from
> powers of r — Laurent polynomials of *any* order, with poles only at r = 0 — misses it identically.
> **Extending the library to degree 4, 6 or 20 changes nothing.**

**The missing class has a name and a place: a pole at the HORIZON, r = 2M.** This basis has poles at `r = 0`
and `sinθ = 0` — the origin and the axis, both coordinate artefacts. **It has nothing at the horizon, the one
surface in the problem that is physically distinguished.** For §161 that is a sharper witness than `(r−2)`:
not a function that was forgotten, but **a class of singularity the construction cannot produce, located
exactly where the physics is.**

**This sharpens §161's biconditional exactly as that leg pre-registered.** `legible ⟺ integrable` survives in
the form `legible ⟺ integrable with a REPRESENTABLE invariant`, and `(r−2)` is a **concrete witness** to the
gap rather than a hypothetical one. The partial kill §161 anticipated has arrived, located, and in the
direction it predicted.

## What the numerical exponent does and does not decide

**The exponent-2 result confirms nothing, and I over-claimed it.** `K₁` is first-order perturbation theory: it
solves the O(ε¹) equation at χ⁰, χ¹, χ² and makes **no claim about the O(ε²) term**, which exists, is
generically nonzero, and whose coefficient nothing computed predicts. **So `A = 4.07e-07` measures an
unpredicted quantity — it had no value it was supposed to take, hence none it could have failed to take.**
ansatz's phrasing: *measuring that the residual goes as ε² is measuring that a smooth function has a quadratic
term.* The measurement is sound; calling it a confirmation was not.

**Worse, the ε route cannot test the proof even in principle.** If `K₁` were wrong at χ⁰–χ², the failure would
appear as an extra O(ε) term — and `c` is *defined* as the entire linear coefficient over `F₀`, so it would be
**silently absorbed.** The quantity that would reveal the error is definitionally incapable of revealing it. **The open question was basis representability, and it is answered
above without a single further run.**

## A circularity in `c`, and its escape

`c ≡ (excess/ε)/F₀` absorbs any O(ε) residual of `K₁` into itself, so measuring `c` cannot by itself
distinguish floor-drift from a `K₁` failure. It escapes only because the O(ε) cancellation is **proven**
through χ², leaving χ³+ as the only possible source. Truncation by construction rather than by assumption.
(TheBridge raised the circularity against their own proposed measurement.)

## Measured, against an assumption that was flagged and failed

`c` is not χ-independent at large χ — 0.2283 at χ = 0.075, 0.566 at χ = 0.01 — and I reported that as
**`c ∝ χ^−0.45`**, a power law fitted to **two points.**

**WITHDRAWN. The third point refutes it and I already had the data.**

    chi = 0.075   c = 0.2283
    chi = 0.010   c = 0.5660      local exponent -0.451
    chi = 0.003   c = 0.6041      local exponent -0.054

**`c` is SATURATING toward ~0.6, not following a power law.** The −0.45 was driven entirely by the χ = 0.075
endpoint. **I fitted a slope to two points and quoted it as a scaling**, having spent the same night watching a
peer's two-point slopes dissolve and having told them that fitting a constant to a marching sequence returns
its average rather than its limit. Two points always give a slope.

**AND THE CORRECTED READING IS THE TEST THAT COULD HAVE FAILED, PASSING.** ansatz's proof predicts the linear
term originates at χ³ and above; the ε = 0 floor also originates at χ³ (measured 3.032). So `c`, a ratio of two
χ³-origin quantities, **should be roughly flat** — and at small χ it is. Had `c` kept falling as a clean power
law, that would have implied a component of the linear term **not** from χ³+, contradicting an exact symbolic
proof. **That was the only reading in the thread where a measurement could contradict the algebra, and it does
not.**

---

# THE HORIZON-POLE EXTENSION: tested, and it does NOT cross (2026-09-22)

The obstruction proof says degree is the wrong axis — every Laurent polynomial in `r` is analytic at `r = 2` —
but the missing class is **one function**. So the proposed fix was cheap and specific: add
`{1/(r−2), r/(r−2), r²/(r−2), cos²θ/(r−2)}` to `d2_rat` and re-run at the conditions where the CERTIFY
verdicts were issued (χ = 0.6, ε = 0.05).

    obj   d2_rat BASELINE    d2_rat + 1/(r-2)    change
    A     5.5651e-08         1.0578e-07          0.53x   WORSE
    B     5.5807e-08         1.0566e-07          0.53x   WORSE
    C     1.1398e-08         1.6340e-08          0.70x   WORSE

**Adding the missing function class did not find the survivor. It degraded the margin by ~2×**, on all three
objects — consistent with the conditioning cost of extra near-degenerate features rather than any
representability gain. **The predicted crossing did not happen.**

## Why this was expected to work, and what its failure means

With `E` fixed globally across the ensemble, `P_t² = E²` is a constant, so `K₁`'s pole piece reduces to
`64χ²E²·cos²θ/(r−2)` — **a pure coordinate function, and exactly one of the four added.** The piece the proof
identifies as unrepresentable was therefore *present* in the extended library, and the rung still certified.

> **So the obstruction is not exhausted by the pole.** Either `K₁`'s regular part is also outside the
> degree-2 rational span, or the engine cannot exploit the added directions at this conditioning — and these
> are distinguishable, but not by this run.

## The tolerance fork, resolved, with a number that does not fit

TheBridge asked what relative tolerance the rung accepts, since a 1.6% unrepresentable component should be
findable by a screen with looser tolerance than that. Converted: `heldout` is a **variance** ratio, so an
unrepresented amplitude fraction `d` gives ratio `~d²`.

    EMIT threshold    1e-10  ->  d < 1.0e-05   (0.001%)
    CERTIFY threshold 1e-08  ->  d < 1.0e-04   (0.01%)
    pole fraction     1.6%   ->  would give variance ratio 2.6e-04

**My EMIT tolerance is ~1600× tighter than the pole fraction**, so a 1.6% unrepresentable component is far
more than enough to prevent EMIT. That half of the fork resolves cleanly.

**But one number does not fit and is recorded rather than smoothed:** the measured A margin of 4.474e-07
corresponds to `d = 0.067%` — **24× BETTER than dropping a 1.6% component would give.** So the engine is not
returning "`K₁` minus its pole"; it is finding some other near-conserved combination entirely. **That is
unexplained, and it is the reason the extension failing is not simply a conditioning story.**

## What survives unchanged

**The exactness argument is GLOBALLY true and OPERATIONALLY EMPTY on the domain this screen fits on.**

The proof stands as stated: `K₁` has a pole at `r = 2`, every function in the original basis is analytic there,
and a finite linear combination of functions analytic at a point is analytic at that point — so **`K₁` is not
in the span, exactly, on the whole manifold.**

**But the screen does not fit on the whole manifold.** It fits on `r ∈ [5.107, 9.147]`, which **excludes the
pole**. On that interval `1/(r−2)` is analytic, so by Weierstrass it is uniformly approximable by polynomials —
and measured directly against my ORIGINAL five r-functions `{1, r, r², 1/r, 1/r²}` over exactly that interval:

    max |residual| 3.863e-05    rms 8.789e-06    RELATIVE rms 4.14e-05   (0.0041%)

**My original basis already reaches `1/(r−2)` to four thousandths of a percent on the domain I sample.**

> **Exact non-representability on the manifold does not imply numerical non-representability on a compact
> subset that excludes the singularity.** I recorded the first and claimed the second, and built the §161
> witness on it.

**WITHDRAWN: the §161 framing.** *"Not a function you forgot, but a class of singularity your construction
cannot produce, located exactly where the physics is"* is wrong in its operative content. **The singularity is
real and the construction never needs to produce it, because the orbits never visit it.** (Correction due to
TheBridge, against their own proof, which I had adopted into this file and propagated.)

**AND IT EXPLAINS THE DEGRADATION EXACTLY, so that result stops being a puzzle.** Adding `1/(r−2)`, `r/(r−2)`,
`r²/(r−2)` to a basis that already reproduces them to 4e-05 adds **columns nearly collinear with existing
ones — no new reach, worse conditioning.** The 0.53× / 0.53× / 0.70× degradation is the predicted cost of
redundant features, and it **confirms the redundancy** rather than contradicting anything.

## So what is actually open

**If the basis can reach `K₁` to ~4e-05 relative on this domain, why did the rung certify empty at a tolerance
of 1e-10?** The pole is not the answer. Two candidates, not separable by anything run tonight:

- the **regular** part of `K₁` is outside the degree-2 rational span **in the momentum variables** — the fit
  above tested r-dependence only, not the momentum structure;
- the engine's **conditioning** is the binding constraint rather than the span.

**Recorded as open. No third story is being invented to close it.**

## The open question, narrowed to a measurement (2026-09-22)

Every span-based explanation is excluded **by measurement**, not argument:

    K1's dominant (0,0) term vs my 9 coordinate features, on 120,040 sampled points   1.4e-06
    1/(r-2) vs my original {1, r, r^2, 1/r, 1/r^2} on r in [5.107, 9.147]             4.2e-05
    p_r*p_theta cross term                                    PRESENT (10 features carry it)
    pole's share of the margin                                1 part in 26,947

Composed, the basis permits an amplitude floor of **7.8e-08** (variance 6.1e-15). The measured margin is
**6.7e-04** amplitude — **~8,600× worse than its own library allows.** A fit falling thousands of times short
of what its basis permits is a statement about the **solver**, not the library.

**Conditioning measured, and the sign confirms it:**

    full 39 features     kappa 2.333e+14    margin 5.569e-08
    reduced 27 features  kappa 7.295e+09    margin 2.966e-08

**Removing 12 features — shrinking the span — IMPROVED the margin 1.88×.** That is conditioning and not
representability; a span deficit cannot improve when the span shrinks. The singular-value cutoff is *not*
binding (all 39 retained at `COND_TOL = 1e-15`); the binding constraint is that `κ = 2.3e14` sits within a
factor ~20 of the double-precision limit, so the whitening `W = U/√s` amplifies the worst direction by 4e+06
and `eps·κ ≈ 0.05`.

**And the two points give the SENSITIVITY, which is stronger than "insufficient".** `heldout` is a variance,
so amplitude `d = √heldout`:

    full 39     kappa 2.333e+14   d 2.360e-04
    reduced 27  kappa 7.295e+09   d 1.722e-04
    kappa moved 4.50 decades, d moved 0.137 decades   ->   d ~ kappa^0.0304

**The exponent is 0.03, not 1.** Closing the remaining 3.34 decades to the basis floor at that sensitivity
would require **110 decades of κ.**

> **Conditioning is not insufficient — it CANNOT close the gap at any achievable κ.** The 1.88× is not a small
> effect awaiting a larger one; it is the entirety of what four and a half decades of conditioning buys.

**So BOTH standing candidates are excluded by measurement rather than by elimination**, and by the same two
points: shrinking the library improved the margin (span excluded by mechanism), and the sensitivity exponent
is 0.03 (conditioning excluded by extrapolation). One test, two verdicts, opposite directions.

**The residual belongs to something neither party has named.** Recorded open, with a floor (7.8e-08), a
condition number (2.3e+14), and a measured sensitivity (κ^0.03), so the next attempt starts from numbers
rather than from suspicion. (Sensitivity analysis due to TheBridge; verified here.)

**One hypothesis tried and failed, recorded so it is not re-derived:** that the χ²-truncation makes the
screened object non-conserved, so no basis could find it. That fails for A, which admits an exact rank-2
Killing tensor — an exactly conserved object does exist there, and A's margin is the one in the table.

## CORRECTION, found after the close: the span exclusions test the WRONG OBJECT

Every representability test either party ran was on **`chain4 + εK₁`** — the pole, the `(0,0)` sector, the
cross term, all of it. **But the screen does not search for `chain4 + εK₁`. It searches for ANY conserved
quantity, and on A one exists exactly.** `chain4 + εK₁` is an O(ε), χ²-truncated *approximation* to it.

> **So "the span is not the limitation" is a claim about the approximation, not about the object the screen is
> actually looking for.** The exact rank-2 Killing tensor of A has never been tested for representability, and
> neither party holds it — it is ansatz's machinery.

**Fifth instance tonight of "I checked the thing, and the thing I checked was not the thing" — and this one is
inside the exclusions that close the leg, committed by both parties.**

**AND MY DISCOUNT OF THE GAP WAS INVALID, in the night's own signature species.** I wrote that *"the measured
margin is smaller than the approximation's own truncation error, which cuts against it."* The two numbers are
not comparable:

    truncation drift  2.2e-03   max|Q - Q0|/|Q0| ALONG a trajectory, normalised per-trajectory
    measured margin   2.36e-04  sqrt(mean_traj(var_within)/var_total), normalised by the
                                ACROSS-ENSEMBLE variance

**A max relative deviation against a ratio of within- to across-ensemble variances.** Different statistics,
different denominators; the 10× between them is not a number about the physics. *Two quantities that look
commensurable because both are small and both concern the same object* — which is the species this entire
night began on, arriving in the sentence that discounted the last open gap. **The gap stands undiscounted.**

## What survives and what does not

**SURVIVES:** the shrink-test exclusions, because they are about the *screen's behaviour* rather than its
target. A span deficit cannot improve when the span shrinks, whatever the target is; and `d ~ κ^0.03` is a
property of the fit, measured on whatever the fit was doing.

**DOES NOT SURVIVE:** the inference from *"the approximation is in span"* to *"span is not the limitation."*

**The better-specified open question: is A's EXACT rank-2 Killing tensor in `d2_rat`'s span on the sampled
domain?** One object, one fit, and it is ansatz's to produce. (Correction due to TheBridge, after the close.)

---

# THE PRE-REGISTERED OUTCOME (iii) LANDED — and it is the leg's real conclusion (2026-09-22)

The slow five-point ε-scan finished after the cheap targeted runs had already reshaped the question. It is the
one measurement made before any of tonight's corrections, and it returns the outcome the amendment named as
*"a real possible outcome and the one I would most want to know about."*

    A  exponent 1.999   R2 1.0000   0 censored     A KEEPS Carter exactly
    B  exponent 1.999   R2 1.0000   0 censored     B DESTROYS it
    C  exponent 2.001   R2 1.0000   0 censored     C keeps it RATIONALLY

    B/A across eps: 1.00  1.00  1.00  1.00  1.00

**Three objects with three different integrability structures give the SAME exponent to three decimals, and
A and B agree in magnitude to four significant figures across two decades of ε.**

> **THE MARGIN IS NOT MEASURING INTEGRABILITY.**

The mechanism is generic and requires nothing about Killing tensors: a best-fit conserved direction with an
O(ε) residual yields a **variance** ~ ε² for *any* O(ε) deformation. **That is the response to being deformed
at all** — identical whether the invariant survives, dies, or turns rational.

## Why this explains the whole leg

Everything that looked puzzling follows:

- **A and B were indistinguishable at ε = 0.05** (4.474e-07 vs 4.527e-07, 1.2% apart) — not because the
  deformations are tiny, but because **the statistic does not respond to the property that separates them.**
- **The 8,600× gap to the basis-permitted floor** is not a span deficit and not conditioning: the margin is
  floored by the generic ε-response, which no basis and no solver can remove.
- **The `d ~ κ^0.03` insensitivity** is what a statistic dominated by a term independent of the fit's quality
  should show.
- **The `(iii)` reading was pre-registered as "the margin is measuring something COMMON to both metrics that
  neither party has named."** It is now named: **the deformation itself.**

## What this costs and what it does not

**The CERTIFY verdicts stand.** No object emitted, and none should have — the screen correctly reported that
it found no conserved quantity at its tolerance.

**What falls is the diagnostic reading of the margin's MAGNITUDE.** A margin of 4.5e-07 versus 7.7e-08 was
being read as a statement about how nearly an invariant was found. On this evidence it is closer to a
statement about deformation amplitude. **§161's ladder-shape diagnostic (flat vs descending across degree) is
untouched** — that compares a single object against itself across basis size, and never across objects.

## THE OPEN QUESTION IS ANSWERED — by the same scan, and A's exponent is NOT generic

**A's exponent-2 carries information and B's does not**, and the difference is whether an exact invariant
existed to be missed. Argument due to TheBridge; the premise is in this repo's own measurements.

    A at eps=0     margin 7.8543e-18    EMITS -- so K_0 (Carter on Kerr) IS in the span, and found
    A at eps=0.05  margin 6.0244e-07    eleven orders higher
    A exponent     1.999 over two decades, R2 1.0000

A's invariant **survives exactly at every ε**: `K_A(ε) = K₀ + ε·δK + O(ε²)`. **The screen's basis is
ε-independent** — coordinate functions times momentum monomials — so if `K_A(ε)` were in the span the fit
would find it at every ε and **the margin would stay at the ε=0 floor (~1e-17): exponent 0.**

It does not. It rises as ε² over two decades.

> **So `K_A(ε)` is not in the span. `K₀` is — it emits at ε = 0. Therefore `δK` is NOT**, and the only
> alternative (the fit can reach it but fails to) is conditioning, excluded at `d ~ κ^0.03`.

**A's exact first-order Killing tensor correction is outside `d2_rat`'s span on the sampled domain.** That is
the open question, answered by the scan that had been running since before anyone knew what to ask it.

**B is the control that makes it an argument rather than an assertion.** B has no exact invariant, so nothing
exists for the basis to miss and its exponent-2 is purely the generic ε-response. **Same number, opposite
information content, and the difference is supplied by ansatz's algebra rather than by any measurement.**

**AND IT DOES NOT CONFLICT WITH `K₁` BEING REPRESENTABLE, because `δK` is not `K₁`:**

    K1  corrects  chain4 = -8L^2 + P_phi^2 + 56 chi^2 (H + P_t^2)     chi^2-TRUNCATED
    dK  corrects  CARTER                                              exact in chi

Different objects. **`K₁`'s representability to 1.4e-06 says nothing about `δK`'s** — the fifth-instance error
in its final form, and the reason the gap was real.

**Falsifiable consequence for whoever picks this up:** add `δK` to the library and **A's exponent must collapse
from 2 toward 0 while B's must not move.** Two objects, opposite predicted signs, one run. Needs `δK` from
ansatz.

## What the leg establishes, stated so it is not over-read either way

**The margin's MAGNITUDE does not discriminate integrability** — `B/A = 1.00` across two decades, the cleanest
single measurement of the night.

**The margin's EXPONENT is not uniformly uninformative**: generic for an object with nothing to find, a
*statement* for an object with something to find. **§161's ladder survives because it compares one object
against itself across basis size. The exponent survives too, but only where an exact invariant is known to
exist independently** — which is precisely where the symbolic side has to supply the premise.

## Premise rows for the dK test (2026-09-22, both PASS)

Before asking a peer for `dK`, TheBridge's three-way go/no-go, adopted as stated. Two rows, because
their catch was that my first script was **one column short** -- it had the floor and one margin,
enough to see headroom and not enough to measure an exponent at all. Filed as silent_nulls 45a.

**Row 1 -- does A still emit at eps=0 at the lower chi?** (chi=0.075 chosen because the `dK` recipe
is stated only to O(chi^2), so at chi=0.6 the truncation is large.)

| chi | eps | A margin (d2_rat) | emits? |
|---|---|---|---|
| 0.6 | 0 | 2.8517e-17 | YES |
| 0.6 | 0.05 | 5.5651e-08 | no |
| 0.075 | 0 | 8.2238e-15 | YES |
| 0.075 | 0.05 | 4.9073e-10 | no |

PASS, with the honest number stated: the floor at chi=0.075 is **8.22e-15, ~300x worse than at
chi=0.6**. Separation from the eps=0.05 margin is 60,000x -- ample, and smaller than the 2e9 at
chi=0.6. `K_0` is in the span at both.

**Row 2 -- is there a 2 to collapse?**

| eps | A margin |
|---|---|
| 0.05 | 4.9073e-10 |
| 0.0158 | 5.1566e-11 |
| 0.005 | 5.5446e-12 |

fitted exponent **1.947** (pairwise 1.956, 1.938) against the 1.999 reference at chi=0.6. PASS.

**Both pass -> ask ansatz for `dK`.** Pre-registered prediction, on the record before the object
exists: adding `dK` to the basis must collapse **A's** exponent toward 0 while leaving **B's** at ~2.
If A's exponent does *not* move, `dK` is not what is missing and the span exclusion stands as measured.
If **both** collapse, the added column is absorbing deformation amplitude generically and the test is
void -- that is the outcome the B control exists to catch.

## The dK span test -- PRE-REGISTERED 2026-09-22, before the object is built

Both premise rows passed, so the test is on. Ansatz has ended as a session; the recipe is not
carried in my head -- it is recorded in their commit `004f564` (`docs/PARKED.md`), read before use:

    chain4 = -8Q - 7 P_phi^2 + 56 chi^2 (H + P_t^2)
    P_phi^2, P_t^2 exactly conserved and eps-independent, so at O(eps):
    dK = -(K1 - 56 chi^2 dH)/8        to O(chi^2)

`K1_A` exists as a symbolic text file in their repo. **Cross-repo scope:** reading a finished
symbolic object is the "concepts cross as a lens" mode this project runs in; their solver is not
being imported into any SpaceTime script. The object is transcribed with an explicit convention map.

### The bridge is the risk, and it has a known-fail

Their momenta and mine are not the same symbols (`y = cos θ`, `P_y = -p_θ/sin θ` here). A wrong
convention map and the interesting negative result **produce the same output**: an exponent that
fails to collapse. That is silent_nulls 45a, and it disqualifies the test unless a control separates
them. The control:

> **C: does `Q + eps*dK` drift at O(eps^2) along A's flow?** No engine, no basis, no conditioning --
> just RK4 and evaluate. If the map is right the drift exponent goes 1 -> 2. If it is wrong, dK is
> numerically garbage and the exponent stays at 1.

**Its known-fail is already banked:** the same test on `Q + eps*K1` gave exponent **1.001** (bare Q
gave 1.002) -- no improvement, because K1 corrects chain4 and not Carter. So a readout that cannot
tell `Q + eps*dK` from `Q + eps*K1` is blind, and **C must reproduce the 1.001 on K1 in the same run**
as a two-sided control. **No span test runs unless C passes both sides.**

### Disambiguating the outcome ansatz flagged in advance

They stated before any run that dK is producible only to O(chi^2), so **partial collapse is ambiguous**
between "dK is the missing span" and "dK is only partly right at this chi". That ambiguity is itself
measurable, because the truncation error scales as chi^2 and the span question does not:

| outcome at chi = 0.075 AND 0.0375 | reading |
|---|---|
| A collapses to ~0 at both | dK IS the missing span; the exclusion is overturned |
| A's residual exponent **shrinks** with chi | truncation-limited -- dK is right, the O(chi^2) recipe is not enough; a LOCATED limit, not a verdict |
| A's residual exponent **chi-independent** | dK is NOT the missing span; the exclusion stands as measured |
| **B moves too** | the column absorbs deformation amplitude generically; test VOID -- this is why B ships |

B is the control that makes any of it an argument, and it runs at both chi as well.

Committed before `dK` is constructed.

### Amendment, before the run: a sign the calibrator cannot see

Source convention confirmed by reading their code, not assumed: `_kt_double.py:332` states
`(t, x=r, y=cos th, phi)`. So the map is `x->r`, `y->cos th`, `P_x->p_r`, `P_y->sigma*p_th/sin th`,
`P_t->-E`, `P_phi->L`, `chi->a`.

**Two conventions do NOT need fixing**, which shrinks the risk: a span test is invariant to (a) the
overall scale of `dK` and (b) adding any multiple of an already-spanned invariant (`P_phi^2`, `P_t^2`,
`H` are all in the library). So normalisation and additive-offset differences between the repos
cannot affect the verdict. What remains is the functional form -- the `(x,y)` map and the `P_y`
Jacobian.

**The gap:** I intended to calibrate the map against Carter, but **Carter is even in every momentum**,
so it is blind to `sigma`. `dK` carries a `P_x*P_y` cross term, which is not. A calibrator that cannot
see the thing it is calibrating is 45a again, so the sign is stated as an open discrete choice and
resolved by the control, which has a known-fail:

| control outcome over sigma = +1, -1 | reading |
|---|---|
| exactly one sigma gives drift exponent ~2 | that is the map; a wrong bridge hitting exactly 2 by accident is not credible |
| neither (both ~1, like K1's 1.001) | dK as transcribed does not complete Carter -- **no span test runs** |
| both give ~2 | the object is absorbing generically; test VOID |

Selecting sigma by the control is legitimate *only* because the control can fail for both values,
which is what makes it a measurement rather than a fit. Stated before running it.

### Reading rule for the control, fixed before the numbers land

The exponent ALONE is not enough, and noticing that is 45a applied to my own control. If the bridge
maps `dK` to something numerically negligible then `Q + eps*dK ~= Q`, the exponent stays at bare-Q's
1.001, and that is **indistinguishable from "dK is wrong"** -- while actually meaning the control
never tested anything. The table already carries the cure (every row reports its own `d` values
against the bare-Q row), so the readout is a three-way, not a threshold:

| exponent | improvement vs bare Q | reading |
|---|---|---|
| ~2 | large (>=10x) | bridge right, `dK` completes Carter -> **span test runs** |
| ~1.00 | **~1.00x exactly** | `dK` is numerically negligible here -- VACUOUS, tests nothing, no verdict |
| ~1.00 | anything else | `dK` present and wrong -- e.g. K1's banked **0.11x (worse than bare Q)** |

K1's banked row is the known-fail for the third case specifically, and bare Q is the known-fail for
the second. Both must appear in the same table as the object under test.

### Correction: the bridge matched nothing, and the sign is now PREDICTED not merely resolved

The first bridge matched `"P_x"`/`"P_y"`. **The source momenta are named `p_t, p_r, p_u, p_phi`**, so
the substitution dict matched **no momentum at all** and `subs` silently did nothing -- `subs` never
errors on a key that is not present. Worse than a clean miss: `p_r` exists in both namespaces (theirs
`real=True`, mine `positive=True`), so `lambdify` would have bound *that one* correctly by NAME while
`p_u`, `p_t`, `p_phi` became undefined globals. A bridge right about one coordinate and silently
absent on three. Fixed with a **completeness assertion** in both directions: every source symbol must
be mapped, and nothing unexpected may survive the substitution.

Reading the real names also settles the Jacobian from physics rather than from the control. Their
`y` IS `u = cos th`, and the momentum conjugate to it is

    u = cos th  =>  du = -sin th dth  =>  p_u = p_th (dth/du) = -p_th / sin th

**So sigma = -1 is the physically correct branch, predicted before the run.** Both branches still run,
because the prediction is worth testing rather than assuming, but the pre-registration changes shape:
sigma = -1 passing the control is a **confirmation**, and sigma = +1 passing instead would mean
something is wrong with my reading of their convention and the run would not be usable either way.

### The reading rule had THREE cells and needed FOUR (recorded mid-run, before chi=0.075 landed)

First half of the control, chi=0.6:

    chi     object       d(.05)      d(.005)  exponent   improvement vs bare Q
    0.6     bare Q   2.8715e-03   2.8660e-04     1.001    1.00x
    0.6         K1   2.6709e-02   2.6662e-03     1.001    0.11x   <- banked known-fail, to the digit
    0.6    dK s=+1   9.2331e-05   9.5861e-06     0.984    31.1x

**The known-fail reproduced exactly** (K1 at 0.11x, exponent 1.001 against bare Q's 1.001), so this
is the same instrument that produced the reference and a wrong object still reads as wrong in it.

**But `dK s=+1` is not cleanly any of my three declared outcomes.** Improvement 31.1x clears the
`>=10x` clause; the exponent is 0.984, not 2. As WRITTEN the rule calls that "present and wrong", and
**that verdict stands for this row** -- the rule is not being moved after seeing the number. What is
being recorded is that **my three cases were not exhaustive**:

| exponent | improvement | cell |
|---|---|---|
| ~2 | large | right (declared) |
| ~1.00 | ~1.00x | negligible / vacuous (declared) |
| ~1.00 | <1 or small | present and wrong (declared) -- K1's 0.11x |
| **~1.00** | **large (31x)** | **right but TRUNCATED -- NOT DECLARED** |

A 31x reduction at unchanged exponent 1 means `dK` cancels ~97% of the O(eps) drift and leaves ~3%.
A wrong object does not cancel 97% of anything -- K1, one row up, makes it **9x worse**. This is what
an O(chi^2)-truncated `dK` should do at chi=0.6, where chi^2 = 0.36.

I wrote the rule assuming `dK` is right, wrong, or negligible. **"Right but truncated" produces large
improvement at exponent 1**, and it was invisible to me because the three enumerated cells all
produce plausible-looking output -- the same species as an always-true guard that is output-identical
to a working one. TheBridge's framing: I pre-registered a way for the test to return *nothing*, but
not a way for it to return *partially*.

**This makes the two-chi design load-bearing rather than precautionary**, and the discriminator was
already committed: truncation scales as chi^2 and a bad convention map does not. At chi = 0.075,
chi^2 falls 64x, so
- **truncation** -> residual shrinks sharply, exponent climbs toward 2;
- **bad bridge** -> 31x and exponent ~1 persist, because a wrong map does not care about chi.

Written before those rows existed.

### TheBridge sharpens the fourth cell into a NUMBER, and corrects my exponent expectation

Received before the chi=0.075 rows existed; recorded before they land. Credit theirs.

**The prediction.** The deformation carries `a^2`, so `drift(bare Q) = eps*[A2 chi^2 + A3 chi^3 + ...]`.
A chi^2-accurate `dK` cancels `A2 chi^2` and leaves `eps*[A3 chi^3 + ...]`, so

    residual fraction = A3 chi^3 / A2 chi^2 = (A3/A2)*chi      =>   IMPROVEMENT ~ 1/chi

Calibrated on my own chi=0.6 row (`1/31.1 = 0.0322` => `A3/A2 = 0.0536`):

    truncation-limited   improvement ~249x at chi=0.075    (exactly 8x better, = 0.6/0.075)
    wrong bridge         improvement ~31x                  (unchanged; a bad map has no chi-dependence)

**The 8x is not fitted** -- it is the ratio of the two chi values, and the linearity rests on the
chi^3 parity result measured last night for the chain4 floor (exponent 3.032), for an unrelated
reason. A number banked for one purpose is the free parameter of a prediction made for another.

**THE CORRECTION, which cuts against the clean story I told.** I said the exponent must climb toward
2. **It need not**, and my saying so was the tidier claim rather than the true one:

    drift(Q + eps*dK) = eps*[A3 chi^3]  +  eps^2*[B chi^2] + ...
                        truncation         genuine O(eps^2)

A chi^2-truncated `dK` never fully cancels the O(eps) term at ANY chi > 0, so the linear piece
survives and the exponent stays 1 until the quadratic overtakes it, at `eps > (A3/B)*chi`. At fixed
eps it does climb (linear falls as chi^3, quadratic only as chi^2) but the crossover may sit outside
my eps grid entirely -- **in which case the exponent stays at 1 at chi=0.075 and nothing is wrong.**

> **So the discriminator is the IMPROVEMENT, not the exponent.** The 1/chi scaling is a
> one-parameter prediction with no free constants; the exponent's behaviour needs a crossover
> neither of us can locate without `B`.

This supersedes the "exponent climbs toward 2" clause of the previous section as the *discriminator*,
and it is a correction to my reasoning, not a relaxation after seeing data -- the chi=0.075 rows had
not been produced when this was written.

### sigma RESOLVED, as predicted: s=-1 wins by 2.5x

    0.6    dK s=+1   9.2331e-05   exponent 0.984   improvement 31.1x
    0.6    dK s=-1   3.6644e-05   exponent 1.039   improvement 78.4x

**`sigma = -1` is the branch, confirming the prediction committed before any dK row existed** --
read from `_kt_double.py:332` (their `y` IS `u = cos th`) rather than assumed, giving
`p_u = -p_th/sin th` by calculus. The control separates the two branches by 2.5x, so the cross term
DOES carry enough weight to be seen; the sign was calibratable after all, and the check could have
rejected (a check that cannot reject was the live worry).

**Recalibrating TheBridge's 1/chi prediction onto the correct branch:** `1/78.4 = 0.01276` at
chi=0.6 gives `A3/A2 = 0.02126`, so at chi=0.075 the truncation-limited improvement is

    78.4x * 8  =  ~627x        (truncation-limited)
    ~78x                        (wrong bridge -- unchanged)

Same 8x, same no-free-constants structure, applied to the branch the control selected.

### The binary becomes a MEASUREMENT: every value in [78.4, 627] splits the residual

TheBridge again, committed before the rows landed. Write the residual fraction as truncation plus a
chi-independent remainder:

    residual_fraction(chi) = a*chi + b
    anchor    0.6a  + b = 1/78.4 = 0.01276
    measure   0.075a + b = 1/I(0.075)          two equations, two unknowns

So `I(0.075)` does not pick a branch -- it **splits** the residual:

    I(0.075)   a (truncation)   b (chi-indep)   b as % of the chi=0.6 residual
        78.4          0.00000        0.012755            100.0%
       150.0          0.01160        0.005797             45.4%
       250.0          0.01668        0.002749             21.6%
       400.0          0.01953        0.001035              8.1%
       627.0          0.02126        0.000001              0.0%

Bounded in BOTH directions, with named diagnostics outside the range:

    I = 627     b = 0   PURE TRUNCATION -- dK right, only error is O(chi^3)
    I = 78.4    a = 0   PURE chi-INDEPENDENT -- bridge wrong by a fixed amount no chi removes
    I > 627             faster than 1/chi -- the MODEL is wrong, not the object
    I < 78.4            improvement WORSE at smaller chi -- neither hypothesis predicts it;
                        that would be the interesting outcome

**This is the structural repair of the fourth cell, not a patch on it.** The missing branch existed
because a partial result had nowhere to go; this gives every partial result a number. The lesson
generalises past this test: *when a pre-registration enumerates outcomes, ask whether the statistic
can express the outcomes BETWEEN them.*

**Their check on the sigma result:** if the cross term contributes `+/-C` against base `B`, then
`|B+C|/|B-C| = 2.5` gives **`C = 0.43*B`** -- the cross term is 43% of the base. That is *why* the
control could reject: not a small correction, and 2.5x is what a 43% term must produce.

**And they credit an observation of mine as stronger than their own derivation:** `s=-1` has exponent
**1.039**, HIGHER than `s=+1`'s **0.984**, while being 2.5x better on improvement. The exponent
ANTI-CORRELATES with quality across the one pair where the better object is known independently. My
discarded clause would have read the better object as marginally worse -- a measured demonstration
that the exponent is not the discriminator, rather than an argument for it.

**The general form of the entry-46 amendment, now with two instances:** `updated` exists for
staleness; their `r in [5.1, 9.1]` exists for bound orbits. **Neither was put there to prevent the
fault it prevented.** A near-miss that depends on an unchosen property is not a control, and writing
it up as one converts luck into false confidence exactly where the next instance will land.

### WITHDRAWN: "the 7% shortfall is in the direction a positive A3 would put it"

I wrote that the bare-Q ratio (59.5 vs the pure-chi^2 prediction of 64) was "in the direction a
positive A3 admixture would put it", and told a peer the assumption was now "measured rather than
assumed". **It is wrong, and in the opposite direction.** Verified here rather than taken:

    ratio(A3/A2 = r) = 64*(1 + 0.6r)/(1 + 0.075r)

      r = -0.1326   ratio 59.50   <- what the measurement actually implies
      r =  0.0      ratio 64.00
      r = +0.02126  ratio 64.71   <- what the improvement anchor implies

A positive A3 contributes relatively more at the LARGER chi and so **raises** the ratio above 64.
I measured **below**. The improvement route gives `A3/A2 = +0.02126`, predicting 64.71; the bare-Q
ratio needs `-0.133`. **The two routes disagree in SIGN and by ~6x in magnitude.**

**What survives:** bare Q IS A2-dominated -- a 7% deviation from pure chi^2 is what a subleading term
of *either* sign looks like, and that is the assumption the 1/chi argument rests on. The row checks
the thing I wanted checked.

**What does not:** the attribution of the 7% to a positive A3, and the phrase "measured rather than
assumed", which claimed more than the row supports.

**Likely cause (TheBridge), and it is why neither route measures A3 cleanly:** at chi=0.6,
`chi^4 = 0.1296` is not small, so a two-term model is inadequate and the 7% is not attributable to A3
at all. Same shape as the chain4 floor reading 3.13 that became 3.032 once a subleading term was
included -- **a two-point fit across a wide chi range returns a blend, not a coefficient.**

**The `a*chi + b` split is unaffected**: it does not require knowing A3, it FITS it. Whether the
truncation coefficient is +0.021 or -0.13 or a blend with A4 changes the value of `a` recovered, not
the validity of recovering it. Run as planned; the A3 sign claim does not go into the write-up.

**This is silent_nulls 53, first-hand, about an hour after cataloguing it.** I had a vague-but-correct
statement (bare Q is A2-dominated, 59.5-vs-64 confirms the model) and SHARPENED it into a
precise-but-false one (the shortfall has a specific sign and it is positive). The sharpened version
inherited the credibility of the correct one, and I shipped it to a peer as a strengthening. **The
sharpening felt like the rigorous move -- which is exactly what 53 says it feels like.**

## CONTROL RESULT: PASSED, both sides. The bridge is right and the residual is PURE TRUNCATION.

      chi     object       d(.05)     exp   improvement
      0.6     bare Q   2.8715e-03   1.001          1.0x
      0.6         K1   2.6709e-02   1.001          0.1x
      0.6    dK s=+1   9.2331e-05   0.984         31.1x
      0.6    dK s=-1   3.6644e-05   1.039         78.4x     <- anchor
    0.075     bare Q   4.8231e-05   1.000          1.0x
    0.075         K1   4.3793e-04   1.000          0.1x
    0.075    dK s=+1   9.6243e-07   1.000         50.1x
    0.075    dK s=-1   7.7333e-08   1.004        623.7x     <- PRE-REGISTERED 627x

    PRE-REGISTERED  ~627x pure truncation  /  ~78x bridge wrong
    MEASURED        623.7x                                      (0.5% from the prediction)
    SPLIT           a = 0.02125   b = 0.000009   ->  b = 0.1% of the chi=0.6 residual

**Verdict: PURE TRUNCATION.** `b` is 0.1%, i.e. there is no chi-independent component -- the bridge
carries no fixed error. `dK` is correct and its only defect is the O(chi^3) truncation the recipe
was known to have.

**NOT two confirmations, one.** `a = 0.02125` is fixed almost entirely by the anchor once `b ~ 0`
(`a = (1/78.4)/0.6 = 0.02126`), so "a matches the improvement-route A3/A2" is circular. The single
non-trivial fact is that **the second measurement fell on the pure-1/chi line**, which is `b ~ 0` and
`623.7 ~ 627` stated twice. Recording this because double-counting one result as two is the failure
this whole apparatus exists to catch.

**Two-sided, and the negative side is the stronger half:** K1 reproduced **0.11x at BOTH chi**. A
wrong object stays wrong by the same factor at both scales -- which is precisely the `b`-only corner
of the split, appearing as a worked example carried by an object independently known to be wrong.

**The exponent never left 1**, exactly as TheBridge derived before the rows existed: a chi^2-truncated
`dK` never fully cancels the O(eps) term at any chi > 0, so the linear piece survives until the
quadratic overtakes it, and that crossover is outside this eps grid. **Had I kept my own
"exponent must climb to 2" clause, this decisive pass would have read as a failure.**

### The span test therefore RUNS, with a sharpened prediction

At chi=0.075 the residual fraction is `a*chi + b = 0.00160`, so **`dK` is 99.84% correct there**.
The margin is a variance ratio, so amplitude enters squared: adding `dK` should shrink A's margin by
~`(0.0016)^2 = 2.6e-6`, taking `4.9e-10 -> ~1.3e-15`, which is **below the emit floor of 8.2e-15**.

    PREDICTION  A + dK  ->  margin pinned at the floor for all eps  ->  exponent ~0 (COLLAPSE)
                B + dK  ->  exponent stays ~2 (nothing exact to complete)
                A alone ->  reproduces 1.947 (else the harness changed)

Committed before the span test is run.

### Three refinements to the span-test reading, recorded BEFORE the result (TheBridge)

**(1) The headroom is 2.5x, not orders, and must be stated that way.** The arithmetic checks --
`f = a*chi + b = 0.001603`, `f^2 = 2.57e-6`, `4.9073e-10 * 2.57e-6 = 1.26e-15` against the `8.2238e-15`
floor, so it collapses by 6.5x. **But staying ABOVE the floor needs only `f > 0.41%` against the
predicted `0.16%` -- a factor of 2.55 in the residual fraction.** If `dK` were 99.6% correct instead
of 99.84%, there is no collapse. The chi-sweep constrains `f` well, but "below the floor" is being
asserted with 2.5x of room and is not a comfortable margin.

**(2) REPORT EMIT / NO-EMIT PER eps, NOT ONLY THE EXPONENT -- this is my own censoring guard, missed
on my own test.** If `A + dK` pins at the floor, **its exponent is CENSORED, and a censored exponent
is not a measurement.** That is §177's W3 and silent_nulls 19, written in this repo, by me, and not
applied here until a peer pointed at it. The clean statement is stronger anyway:

> **"the screen now EMITS at every eps" -- it finds a conserved quantity where before it found none.**

**Emit/no-emit is a binary the floor cannot corrupt**, and it does not require anyone to distinguish
"exponent 0 because pinned" from "exponent 0 because the response vanished". The span test's headline
therefore becomes the emit verdict per eps; the exponent is reported but is not load-bearing.

**(3) READ B's EXPONENT, NOT B's MARGIN.** Adding `dK` adds a basis function, and **more basis always
fits somewhat better**, so B's margin may improve even though `dK` completes nothing for B. If B's
margin improves while its exponent holds at ~2, **that is still the clean negative.** Only B's
EXPONENT collapsing means the column is absorbing deformation amplitude generically and the test is
void. Easy to mis-call on the margin alone, which is exactly the job B exists for.

### Wrinkle in (2): the repo's emit threshold is ABSOLUTE and the margins scale with eps^2

Adopting the emit/no-emit readout, the obvious threshold is §190's own
(`emit` iff `best < 1e-10`, `certify` iff `best > 1e-8`). **But that is an absolute cut, and the
margin scales as eps^2**, so A-alone at chi=0.075 already crosses it without any `dK`:

    eps      A-alone margin     vs 1e-10
    0.05       4.9073e-10       above  -> no emit
    0.0158     5.1566e-11       BELOW  -> "emits"
    0.005      5.5446e-12       BELOW  -> "emits"

So "the screen now emits at every eps" cannot be read off an absolute threshold -- the unaugmented
arm would already pass it at two of three eps, purely because a smaller deformation has a smaller
margin. **The binary is corrupted by the same eps-dependence the exponent was measuring.**

**The uncorrupted version is FLOOR-RELATIVE:** the emit floor at chi=0.075 is `8.2238e-15` (measured,
the eps=0 row), and the question is whether the margin sits AT the floor rather than below a fixed
number. So the reported readout is `margin / floor` per eps, for all three arms:

    margin/floor ~ 1        the screen finds the invariant -- collapse
    margin/floor >> 1       it does not

This keeps TheBridge's point -- the headline is a per-eps verdict, not a censored exponent -- while
not inheriting an absolute cut that eps itself can satisfy. Recorded before the numbers.

### The DENOMINATOR is basis-dependent too -- four floors, not one (TheBridge, before the result)

My floor-relative fix caught the eps-corruption in the numerator and **left the same defect in the
denominator.** The floor `8.2238e-15` was measured on **A-ALONE's** basis. `A + dK` has one extra
basis function, and **more basis always fits better** -- the very point (3) makes about B's margin --
so `A + dK`'s own `eps=0` floor may be LOWER. Dividing `A + dK`'s margins by A-alone's floor borrows
a denominator from a different experiment and **can manufacture a collapse.**

**How it bites concretely:** the predicted `A + dK` margin sits only **6.5x** under the borrowed
floor. If `A + dK`'s true floor is ~6x lower the verdict still holds -- **but for a reason nobody
checked**, and the identical arithmetic with a 20x lower floor would read "collapse" from a margin
that had not moved at all.

**Fix: measure `eps=0` separately for each of the four arms** -- A-alone, A+dK, B-alone, B+dK -- and
divide each arm's margins by ITS OWN floor. Four cheap rows (`scratchpad/dK_floors.py`), running now.
`B-alone` is added even though the span test does not use it, because B+dK needs its own comparison.

**The pattern across both halves of this readout is one thing:** "more basis fits better" is not a
caveat about one number, it is a property of the instrument that contaminates **every** quantity
computed from the enlarged basis -- margins, floors, and any ratio built from them. Catching it in
one place is not catching it.

*And symmetric failure, worth recording:* TheBridge proposed the emit binary as the repair for a
censored statistic, and **the binary they proposed carried the identical eps-corruption it was
repairing.** So my catalogue entry did not fire for me, their own correction did not fire for them,
and in both cases the thing that caught it was the other party reading it.

### The four floor rows contain two IDENTITY checks (TheBridge) -- premise verified symbolically

At `eps = 0` the deformation vanishes, so A, B and C are the same metric. **Verified rather than
assumed**, by simplifying each metric component at `eps=0`:

    A(eps=0) == B(eps=0) : True
    A(eps=0) == C(eps=0) : True

So two of the four queued rows are the same computation run twice:

    PAIR 1   A-alone(eps=0)  ==  B-alone(eps=0)     same metric, same basis
    PAIR 2   A+dK(eps=0)     ==  B+dK(eps=0)        same metric, same basis

**If they agree:** the floor is a property of `(metric, basis)` -- the premise the whole
floor-relative readout rests on -- confirmed for free, no extra run.

**If they disagree:** the floor also carries something about the A-ensemble vs the B-ensemble
(trajectory initial conditions or sampling). Dividing each arm by its own floor would still be right,
**but the A-vs-B COMPARISON would be contaminated** -- `A+dK/floor_A` and `B+dK/floor_B` would be
ratios against different baselines, and **the discriminator the entire span test turns on, "A
collapses and B does not", would be comparing two differently-normalised numbers.** Nothing else in
the design catches that.

**It is the borrowed-denominator problem one level out:** there the denominator came from a different
BASIS, here it would come from a different ENSEMBLE. Both are "the two numbers came from different
experiments", and both are invisible in a table that shows only ratios.

**The generalisation this forces, replacing mine:** I wrote that more basis contaminates every
quantity computed from the enlarged basis. The version this instance demands is broader --

> **every quantity in a comparison must be checked for what it SHARES with the thing it is compared
> against, not only for what changed.** The enlarged basis was merely the first way two numbers came
> from different experiments.

**And the row that supplies the check is the one added for symmetry.** `B-alone` is not used by the
span test; it went in because asymmetric treatment of the control arm is how controls stop
controlling. That reason turned out to be the wrong reason for the right action -- it is PAIR 1's
existence that matters.

### The 136x floor discrepancy was EXACTLY two axes, and the reference now reproduces to all digits

    quoted reference floor (premise run)      8.2238e-15
    my harness, seed 0 + min(4,.) readout     6.0405e-17     136x off
    my harness, seed 1 + all-columns readout  8.2238e-15     EXACT MATCH

So the discrepancy was entirely `seed` (1/51 vs 0/50) and `readout` (`range(C.shape[1])` vs
`range(min(4, C.shape[1]))`), with nothing else hiding underneath. **This is a reproduction check
passing, not merely a mismatch explained** -- the difference is fully accounted for and the number
returns to all four quoted digits once both axes are matched.

**Instance 5 is a species worth naming: I was inconsistent with the REFERENCE by being consistent
with the LIBRARY.** §190's own `screen()` uses `min(4, C.shape[1])`; the premise script that produced
the banked numbers used `range(C.shape[1])`. Both readings are defensible, there was no way to be
right by following a single source, and the disagreement is invisible unless you diff two files
nobody intended to compare. That is worse than two of my own scripts disagreeing, because neither
party did anything wrong.

**And the near-miss is the headline itself:** had I divided the relaunched margins by the quoted
`8.2238e-15` while computing them at seed 0 with the `min(4,.)` readout, the collapse verdict would
have flipped on a 136x factor measuring nothing but configuration drift. **One careless division from
a headline determined by inconsistency.**

### A+dK's OWN floor is 4.14x lower, and it takes most of the headroom

    A-alone floor  (borrowed)   8.2238e-15
    A+dK   floor   (its own)    1.9853e-15     4.14x LOWER -- "more basis fits better", measured

Recomputing the collapse prediction against the correct denominator:

    residual fraction f         0.001603      (f^2 = 2.5688e-06)
    predicted A+dK margin       1.2606e-15
      vs borrowed floor         ratio 0.153x   headroom 6.52x     <- what I claimed all night
      vs ITS OWN floor          ratio 0.635x   headroom 1.57x     <- correct

    f needed to stay ABOVE its own floor   0.2011%
    predicted f                            0.1603%
    ROOM IN f: factor 1.25                 (I stated 2.55x)

**The prediction still says COLLAPSE -- the margin is below the floor -- but it is MARGINAL, not
comfortable.** `f` would need to be only **25% larger** for there to be no collapse, against the
2.55x of room I reported. TheBridge's warning was exact: *"the verdict still holds, but it holds for
a reason nobody checked."* It holds, and the reason has now been checked, and it nearly did not hold.

**The gate fires on this exact comparison**, which is the first time tonight an instrument rather
than a person caught one:

    Mismatch: cannot compare 'A-alone margin(eps=.05)' with 'A+dK floor':
    declared axis ['eps'], but configurations differ on ['basis'] -> basis: 'base' vs 'base+dK'

**Standing correction to every headroom figure I reported tonight:** 6.5x and 2.55x were computed
against a floor belonging to a different basis. The correct figures are **1.57x and 1.25x**.

## BOTH PAIR CHECKS FAIL. The floor is a NOISE-LIMITED quantity, and the collapse verdict is UNRESOLVABLE.

    A unaugmented   8.2238e-15        B unaugmented   2.9502e-15     PAIR 1  ratio 2.79  DISAGREE
    A + dK          1.9853e-15        B + dK          5.1712e-15     PAIR 2  ratio 2.60  DISAGREE

A and B at `eps=0` are the SAME METRIC -- verified symbolically earlier. So each pair is one
computation run twice, and each disagrees by ~2.7x. **Cause measured, not guessed:**

    launch inputs bitwise-identical            True
    H, ith, dHdr, dHdth  bitwise-identical     True
    irr                  max|A-B| 2.220e-16    rel 2.86e-16   <- ONE ULP
    trajectories         max|diff| 1.041e-17

**A single ULP of floating-point rounding in one metric component -- because `_A()` and `_B()` are
different expression trees that are mathematically equal at `eps=0` -- propagates to a 2.8x
difference in the floor.**

### What this costs

**1. The floor is not a property of `(metric, basis)`.** It is not a property of anything stable. It
is set by rounding, amplified through 3000 RK4 steps and a generalized eigenproblem.

**2. Any floor-based verdict needs > ~2.8x of headroom to mean anything. The collapse prediction has
1.57x.** So:

> **THE COLLAPSE VERDICT CANNOT BE READ FROM THE FLOOR COMPARISON. It is below the noise.**

**3. The 4.14x "basis effect" is not cleanly a basis effect either.** `A+dK / A-alone = 4.14x` sits
only 1.5x above the 2.7x pair-noise. **So the inference that `dK` is capturing real structure the
base basis missed at 1e-15 is NOT supported by this measurement** -- 4.14x against a 2.8x noise level
is not a signal. (That inference was drawn by TheBridge from the 4.14x before the pair rows existed;
it is withdrawn on the noise level, not on its reasoning.)

**4. Every headroom figure tonight was computed against a quantity with 2.8x of intrinsic scatter** --
6.52x, then the corrected 1.57x, and the `f`-room figures 2.55x and 1.25x. None of them were ever
resolvable.

### What survives, and it is the thing that never had a denominator

**B's EXPONENT.** An exponent holding at ~2 versus collapsing is a *shape* comparison within a single
arm: no cross-arm normalisation, no absolute threshold, no floor. As TheBridge put it before these
rows landed -- **everything that has gone wrong in the last three hours has gone wrong in a
denominator, and B's verdict has no denominator.** The span test's own A-unaugmented arm already
reproduced the banked reference exactly (`4.9073e-10 / 5.1566e-11 / 5.5446e-12`, exponent **1.947**),
so exponents in this harness are stable and comparable even though floors are not.

**The pair check was proposed as a cheap confirmation of a premise. It fired, and it invalidated the
readout it was checking.** That is the most expensive possible outcome and the reason to run it.

## A + dK: the margin COLLAPSES and LOSES ITS eps-SCALING

       eps      A-alone         A+dK        ratio    A+dK / its own floor
      0.05   4.9073e-10   1.4286e-14   2.911e-05          7.20x
    0.0158   5.1566e-11   1.8291e-15   3.547e-05          0.92x
     0.005   5.5446e-12   4.5618e-14   8.227e-03         22.98x

    A-alone  monotone in eps: TRUE    exponent  1.947
    A + dK   monotone in eps: FALSE   exponent -0.504

**The headline is not the exponent value and not a floor comparison. It is that the eps-dependence is
GONE.** A-alone falls monotonically by 88.5x across the eps range, exactly as eps^2 requires. A+dK
scatters 24.9x with no ordering -- down, then up -- around the 2e-15 level. `-0.504` is a straight-line
fit to noise and should not be quoted as a number.

**This is the readout that has no denominator.** Monotone-vs-scattered is a within-arm shape
statement: no cross-arm normalisation, no absolute threshold, and it does not care that the floor
carries 2.8x of scatter. The three `A+dK / floor` values (7.20x, 0.92x, 22.98x) span 25x precisely
BECAUSE the quantity is pinned -- which is why the floor comparison was never going to settle this
and the shape does.

**Magnitude, honestly:** suppression at eps=0.05 is 2.9e-5 against a predicted `f^2 = 2.57e-6`, so
**11.3x more residual survives than predicted** -- 34,350x improvement where 389,286x was forecast.
`dK` removes ~99.5% of the O(eps) obstruction, not the predicted 99.84%. The pre-registration
predicted collapse and collapse is what happened; **the predicted MAGNITUDE was optimistic by an
order of magnitude**, which is consistent with a two-point fit for `f` and with the O(chi^3)
truncation being larger than the anchor implied.

**Still required, and it is the whole claim:** `B + dK`. If B's exponent also collapses, the column
absorbs deformation amplitude generically and the test is VOID. Only `A` collapsing while `B` holds
at ~2 carries the result.

## SPAN TEST: BOTH arms collapse -- and the arm needed to read it was not run

      chi              arm  monotone   max/min   exponent
    0.075    A unaugmented      True      88.5      1.947
    0.075           A + dK     False      24.9     -0.504
    0.075           B + dK     False       3.5     -0.081
   0.0375    A unaugmented      True     151.4      2.180
   0.0375           A + dK     False       2.6      0.287
   0.0375           B + dK      True      15.9      1.202

`B + dK` sits at ~1e-14 alongside `A + dK`, non-monotone at chi=0.075. Read naively that is the
**pre-registered VOID** condition: *"if both collapse, the column absorbs deformation amplitude
generically and the test is void."*

**It cannot be read yet, because `B unaugmented` at eps > 0 WAS NEVER RUN.** The span script's arms
are `A unaugmented / A + dK / B + dK`. So the observed `B + dK ~ 1e-14` is consistent with two
opposite readings and the data cannot separate them:

    B-alone ~ 1e-10  ->  B COLLAPSED too   ->  the column absorbs generically  ->  VOID
    B-alone ~ 1e-14  ->  B DID NOT MOVE    ->  dK does nothing for B           ->  CLAIM HOLDS

**This is the SAME omission I identified and fixed hours ago -- in the FLOORS run.** I added
`B-alone` there explicitly, writing that *asymmetric treatment of the control arm is how controls
stop controlling*, and then left the span test with exactly that asymmetry. **The control arm has a
baseline; the treated arm has a baseline; the control's baseline was the one I dropped.**

Assuming B-alone's margins resemble A-alone's -- which leg 6 measured at chi=0.6, `B/A = 1.00` --
would be the borrowed-denominator move for the sixth time tonight, on an arm's own baseline, at a
different chi. **Running it instead.** No verdict issues until it lands.

## EXPONENT STABILITY: measured, against the exact perturbation that destroyed the floor

TheBridge's catch: A-unaugmented reproducing its banked reference is *same tree, same seed* --
that demonstrates DETERMINISM, not robustness. The ULP lives between `_A()` and `_B()`, and the
pair check could not reach it because A and B coincide only at `eps=0`, where no exponent exists.

Direct test instead: **`A' = sp.expand(A)`** -- mathematically identical to A at EVERY eps, a
different expression tree, hence different `lambdify` rounding. Perturbation size verified first:

    A vs A' at eps=0.05, max abs component diff
      H 3.331e-16   irr 3.331e-16   ith 6.939e-18   dHdr 4.649e-16   dHdth 2.359e-16

Machine epsilon -- the same ULP class as the A-vs-B difference that moved the floor 2.79x.

               arm  seed         0.05       0.0158        0.005   exponent
                 A     1   4.9073e-10   5.1566e-11   5.5446e-12      1.947
                 A     2   4.3452e-10   6.8613e-11   6.9283e-12      1.797
                 A     3   1.6093e-10   1.6697e-11   1.8509e-12      1.939
              Aexp     1   4.9494e-10   5.0043e-11   5.9752e-12      1.918

    ACROSS TREES (the ULP mechanism)   exponent 1.947 -> 1.918    delta 0.029  = 1.5%
    ACROSS SEEDS (far larger)          spread 0.1496              = 8.3%
    THE ABSOLUTE MARGIN, same runs     scatters 3.08x
    the floor, measured earlier        scatters 2.79x

**So the last unvalidated assumption under the surviving readout is now measured rather than argued:
a 1-ULP change in the metric moves the absolute number by ~3x and the exponent by 1.5%.** The ratio
cancels the perturbation; the absolute number does not. `within=True` is a physical property.

### And it calibrates what the exponents can resolve

Seed-dominated uncertainty is **+/- ~0.15**. Therefore:

    A unaugmented   1.947 / 2.180    consistent with 2
    A + dK         -0.504 / 0.287    decisively NOT 2
    B + dK         -0.081 / 1.202    decisively NOT 2

**1.202 is distinguishable from 2 at this resolution; 1.8 would not have been.** Stating the
resolution matters because the whole claim rests on "B holds at ~2", and B does not.

## VOID, CONFIRMED ON THE NOISE-IMMUNE STATISTIC (not on the margins)

TheBridge: neither augmented arm is PINNED, so the exponent is readable and I had not quoted it.

         arm   margin(0.05)   its OWN floor   ratio
        A+dK     1.4286e-14     1.9853e-15     7.20
        B+dK     3.1139e-14     5.1712e-15     6.02

Both sit 6-7x above their own floors -- signal, not censoring. So at chi=0.075, on the statistic
that survives ULP noise and needs no denominator:

    arm              exponent        reading
    A unaugmented       1.947        ~2
    B unaugmented       1.955        ~2
    A + dK             -0.504        ~0   COLLAPSED
    B + dK             -0.081        ~0   COLLAPSED

**Both control and treatment fall from ~1.95 to ~0. The VOID is confirmed on the exponent**, which
is the quantity I established hours ago as the only one with no denominator -- and I had been making
the call on margins that scatter 3.08x. Correct verdict, wrong statistic, corrected.

**Independent support that does not compare A to B at all:** `A+dK/floor_A = 7.20` vs
`B+dK/floor_B = 6.02` -- indistinguishable against 2.8x floor scatter. **Both arms sit the same
distance above their own baselines**, which is the generic signature in a form needing no cross-arm
comparison.

**Caveat on the second chi:** at chi=0.0375 the exponents are A+dK 0.287 and B+dK 1.202, which
differ by more than the +/-0.15 resolution. **But no floors were measured at chi=0.0375**, so
whether either arm is pinned there is unknown and those two numbers cannot be read. Not quoting them
as a discrimination. The verdict rests on chi=0.075, where the floors exist.

### VERDICT: VOID -- and what that does and does not mean

The pre-registered condition fired exactly as written: *"if both collapse, the column is absorbing
deformation amplitude generically and the test is void."* So:

    NOT SHOWN  that dK was the missing span (the test cannot distinguish it)
    NOT SHOWN  that dK is in the span either
    SHOWN      that adding a chi^2, degree-2, higher-coordinate-degree column collapses the
               eps-scaling of BOTH an object that keeps Carter and one that destroys it

**Leg 6's original argument is untouched and unconfirmed.** It stands where it stood: on `K_0` being
in the span at eps=0 and the margin rising as eps^2, with `dK` inferred to be outside. The span test
was built to TEST that inference and returned void.

### The complete four-arm table, both chi

      chi   A-alone   B-alone   A + dK   B + dK
    0.075     1.947     1.955   -0.504   -0.081
    0.0375    2.180     2.268    0.287    1.202

**Both unaugmented arms sit at ~2 at both chi** (1.947 / 1.955 / 2.180 / 2.268), which is itself a
useful check: the exponent-2 behaviour is a property of the deformation, not of which object it is,
and it reproduces across metric AND chi.

**Both augmented arms fall at both chi.** The VOID condition is met at chi=0.075, where floors exist
and neither arm is pinned.

**Honest nuance at chi=0.0375, stated and not leaned on:** A+dK falls to 0.287 while B+dK falls only
to 1.202 -- a gap of 0.915, well outside the +/-0.15 resolution, **in the direction the claim
predicted** (A completes, B does not). But B moved from 2.268 to 1.202, which is a substantial fall,
so the void condition is still met; and **no floors were measured at chi=0.0375**, so I cannot show
either arm is unpinned there. The gap is recorded as an observation that the data does not license a
verdict on, not as a partial rescue. Measuring floors at chi=0.0375 would settle whether it is real,
and is the obvious next step if this is ever resumed.

## VOID WITHDRAWN AS STATED: the eps grid was CENSORED for both augmented arms

TheBridge checked "neither augmented arm is pinned" at ONE eps and I generalised it to three. **It is
wrong.** Projecting each augmented arm down the eps^2 line from its measured 0.05 point, against its
OWN floor:

       eps       A proj   /floorA        A obs |       B proj   /floorB        B obs
      0.05   1.4286e-14     7.20    1.4286e-14 |   3.1139e-14     6.02    3.1139e-14
    0.0158   1.4265e-15     0.72*   1.8291e-15 |   3.1094e-15     0.60*   1.0607e-14
     0.005   1.4286e-16     0.07*   4.5618e-14 |   3.1139e-16     0.06*   3.7540e-14

`*` = projected BELOW its own floor. **Both augmented arms clear their floors only at the LARGEST
eps. The three-point exponent fit is one signal point and two floor readings.** The observed
eps=0.005 value (4.56e-14) sits **320x above** where eps^2 scaling puts it (1.43e-16) -- pure floor
scatter.

**And the negative exponent was the tell I failed to read.** `-0.504` says the margin GROWS as the
deformation shrinks. That is not physics; it is floor scatter fitted as a slope. I quoted it as
"~0, collapsed" when its sign should have stopped me.

### So the verdict is right and the STATED REASON IS WITHDRAWN

    WITHDRAWN   "both collapsed, so the column absorbs deformation amplitude generically"
                -- may be true; THIS RUN CANNOT SHOW IT.
    STANDS      the discriminator never ran. Both arms are censored at two of three points,
                for the same reason, by construction of the eps RANGE.

**A test that returns the same answer for treatment and control because both sit below the
instrument's floor has not compared them.** The failure is the GRID, not the objects.

**It also resolves the chi=0.0375 nuance, and more sharply than my "cannot show it is readable":**
at smaller chi the floors are lower, so MORE of the eps grid clears them -- which is exactly why
A+dK reads 0.287 there instead of -0.504, and B+dK 1.202 instead of -0.081. **The gap appears at the
chi where less of the grid is censored.** That is not evidence for the claim; it is evidence that
censoring drove the chi=0.075 numbers.

### The fix is the same lesson for the THIRD time today: push the EXACT parameter

       eps         A+dK  /floorA             B+dK  /floorB
       0.050   1.4286e-14      7.2        3.1139e-14      6.0
       0.100   5.7144e-14     28.8        1.2456e-13     24.1
       0.200   2.2858e-13    115.1        4.9822e-13     96.3

`eps in {0.05, 0.1, 0.2}` puts every arm 6x-115x above its own floor at every point. **eps is EXACT
in these metrics -- raising it costs no truncation, unlike chi.** Same asymmetry that made the
eps-upward sweep right earlier: exact in eps, truncated in chi, so eps is the one to push. Three
times today the answer has been *"you are sweeping the wrong parameter in the wrong direction."*

**The sham inherits the defect** -- on the old grid A+SHAM and B+SHAM would both read ~0 and that
would look like "sham collapses both, so the collapse is generic" when it is "everything collapses
on this grid." Sham killed and relaunched on the uncensored grid, with its own eps=0 floors.

## THE UNCENSORED GRID: the discriminator RAN, and dK fails it -- but is NOT generic

`eps in {0.05, 0.10, 0.20}`, chi=0.075, all six arms, sham floors measured.

         arm  exponent  monotone      suppression vs its own unaugmented arm
     A unaug     2.008      True      --
     B unaug     1.985      True      --
      A + dK     0.634      True      34,350x   120,200x   230,837x
      B + dK     0.224     False      16,297x   515,152x   187,115x
    A + SHAM     1.999      True            1x        1x         1x
    B + SHAM     2.002      True            2x        1x         1x

         arm        floor    margin/floor at each eps
      A + dK   1.9853e-15       7.2x      8.4x     17.3x
      B + dK   5.1712e-15       6.0x      0.7x      8.2x
    A + SHAM   1.3460e-14   24,873x  101,181x  397,370x

### 1. The SHAM is a clean negative control and it PASSES

**A structurally identical object that does not solve the Killing equation does NOTHING** --
exponent 1.999 / 2.002, suppression 1-2x. And it is **fully uncensored**, sitting 25,000x to
1,000,000x above its own floor, so this is a measurement and not a floor artifact.

> **The collapse is NOT generic to the function class. `dK` is special.** Same momentum degree, same
> chi^2 scaling, same coordinate degrees, same magnitude class, coefficients permuted -- and the
> effect vanishes entirely. That is the control TheBridge asked for, and it separates "the test
> cannot see it" from "there was nothing to see."

### 2. But dK does NOT discriminate A from B

Suppression at eps=0.2: **230,837x for A, 187,115x for B -- a ratio of 1.23**, against a measured
seed scatter of 3.08x. **Indistinguishable.** `dK` helps the Carter-DESTROYING deformation as much as
the Carter-preserving one.

### 3. So the pre-registered discriminator ran, and the claim it was built to test FAILS

    NOT "void because the column absorbs amplitude generically"  -- the SHAM refutes that
    NOT "void because everything was censored"                   -- the sham arms are 1e5x above floor
    BUT: dK is a real, specific object that suppresses the margin by ~2e5x for BOTH A and B

**`dK` was derived as the O(eps) correction to Carter for A. If its effect were about completing
Carter for A, it could not do the same for B, whose deformation destroys Carter.** It does. So the
span test cannot support "dK was the missing span for A" -- and the failure is informative rather
than vacuous, because the sham shows the effect is not something any column of that shape would
produce.

**Honest caveat on the dK exponents:** 0.634 and 0.224 are NOT clean. Those arms sit only 7-17x
above their floors (B's middle point is 0.7x -- still censored), so an additive background dominates
the eps-dependence. **The suppression factor is the readable statistic here, not the exponent**, and
it is 5 orders clear of the sham. Pushing eps higher still would clean the exponents; the suppression
result does not need it.

**Leading hypothesis for why dK helps B, recorded not tested:** A's and B's deformations may share
most of their structure, with `dK` completing the common part. That is checkable by applying dK to a
deformation sharing nothing with A's, and is the obvious next build.

## THE SUMMAND SPLIT: one summand is IDENTICALLY ZERO, so dK = -K1/8

TheBridge's mechanism for the non-discrimination: `dK = -K1/8 + 7*chi^2*dH`, and `dH` is the
DEFORMATION's own Hamiltonian contribution -- so a column containing `dH` could absorb the
deformation's leading term regardless of Carter. That would explain "large specific effect, no
discrimination" and would mean the sham excluded the function class but not the mechanism.

**Tested by computing the summands. The dH piece is identically zero:**

    A's deformation, inverse metric by chi order:  chi^0 none, chi^1 none, chi^2 nonzero
    its Hamiltonian contribution:  dH[0] ZERO   dH[1] ZERO   dH[2] nonzero (115 ops)

`56*chi^2*dH` truncated to O(chi^2) keeps only `chi^2*dH[0]`, and **`dH[0] = 0`**, so the entire term
vanishes. Confirmed symbolically: `chi^2*dH` exports as 0 ops with no free symbols, and the identity
`dK == -K1/8 + 7*chi^2*dH` to O(chi^2) evaluates **True** with the second term absent.

> **So to O(chi^2), `dK = -K1/8`. The two summands are not two objects -- one of them is zero, and
> `K1` carries the entire effect.**

**The dH-absorption hypothesis is REFUTED**, and by TheBridge's own pre-registered reading:
*"K1 carries it -> the non-discrimination is a real puzzle rather than an artefact of how dK was
built."*

### A claim from earlier in this leg is now WITHDRAWN

The notes above record, from ansatz's recipe commit and repeated by me:

    K1  corrects  chain4 = -8L^2 + P_phi^2 + 56 chi^2 (H + P_t^2)   chi^2-TRUNCATED
    dK  corrects  CARTER                                            exact in chi
    "Different objects. K1's representability says nothing about dK's."

**At O(chi^2) that is false for THIS deformation.** They differ by the scalar `-1/8`, so **as span
columns they are identical** -- any statement about one is a statement about the other. The
distinction is real only at orders beyond chi^2, which is exactly where the recipe cannot reach.

**This does NOT contradict the drift control**, which found `Q + eps*K1` at 0.11x (worse) and
`Q + eps*dK` at 623.7x. A drift test is sensitive to NORMALISATION -- it adds the object with
coefficient exactly `eps`, so it was measuring that `-1/8` is the right coefficient and `+1` is not.
A span test is scale-invariant. **The same two objects are distinguishable by the drift test and
identical to the span test, and both results are correct.**

**Consistency check running:** adding `K1` as the span column must reproduce the `dK` numbers
exactly. If it does not, the pipeline has a bug.

## RESOLVED: A and B are THE SAME DEFORMATION to 0.03%, so the test was impossible by construction

TheBridge's hypothesis -- `A = Kerr + eps(D_common + D_A')`, `B = Kerr + eps(D_common + D_B')`, with
the Carter property living in a small differing part while the margin is dominated by the common
part. **Tested directly and symbolically** (`D = dg/d(eps)` at `eps=0`, evaluated over the sampled
orbit region), with their caveat adopted: *the 3.4% agreement between the A-unaug and B-unaug margins
is NOT evidence, because two ORTHOGONAL deformations of equal amplitude give equal margins.*

    D_A vs D_B:  cosine +1.000000   ||D_A-D_B|| / ||D_A|| = 0.0003
    D_A vs D_C:  cosine +0.993280   best-scale 3.5732, residual 0.1157
    ||D_A|| = ||D_B|| = 2.0290e-01      ||D_C|| = 7.2990e-01

> **A's and B's deformations are the same object to three parts in ten thousand.** Not "mostly
> common with small differing parts" -- essentially identical. The entire Carter distinction
> (A preserves it, B destroys it) lives in a **0.03%** difference.

### Which makes the non-discrimination a structural impossibility, not a puzzle

The margin goes as amplitude squared, so a discriminating part at 0.03% of the amplitude contributes

    (3e-4)^2 = 9e-8  of the margin

against a measured A/B suppression ratio of 1.23 and a seed scatter of 3.08x. **The discrimination
signal sits ~7 orders of magnitude below the noise.** No span test on this pair could have
discriminated -- at any eps, on any grid, with any floor, with a perfect `dK`. **The verdict was
fixed by the choice of contrast pair before any code ran.**

### The design-level finding, and the irony in it

**The triple was built to ISOLATE the Carter property -- which is exactly why A and B are maximally
similar apart from it. And that similarity is precisely what makes them indistinguishable to the
screen.**

> **A good contrast pair for the ALGEBRAIC question is a bad contrast pair for the SCREEN question.**
> Isolating a property minimises everything else; a numerical screen measures everything else.

**So the honest status of the whole arc:** the pre-registered discriminator did not fail, and it did
not return void. **It was never able to run**, for a reason visible in ten lines of symbolic algebra
that neither party computed before building the test, the control, the sham, the floors, the
uncensored grid, or the five borrowed-denominator corrections along the way.

**What a real test would need:** a Carter-destroying deformation that is NOT a small perturbation of
a Carter-preserving one -- i.e. a contrast pair chosen to be far apart in deformation space, with the
Carter property differing. `D_C` is a start (cosine 0.993 but 3.57x the amplitude and 11.6% residual),
though still nearly parallel. Selecting such a pair is the actual next build, and it is a
*requirement on the pair*, not on the instrument.

## REPRODUCIBILITY BOUND: the span statistic is stable to ~1.33x under an exact identity

Since `dK = -K1/8` and a span column is scale-invariant, `A + K1` MUST reproduce `A + dK`. Ran it
rather than assuming -- TheBridge's point that *an identity holding in symbols still has to survive
the pipeline*, and today already produced three transfers that should have been exact and were not.

    A + dK   1.4286e-14  1.6678e-14  3.4391e-14   exponent 0.634
    A + K1   1.8949e-14  3.5865e-14  7.5913e-14   exponent 1.001

**Diagnosed rather than left as a discrepancy.** The `+1e-9` in `sd = flat.std(0) + 1e-9` is an
ABSOLUTE regulariser and would break scale invariance for a small column -- but the columns' stds are
`3.9651e-03` (dK) and `3.1721e-02` (K1), ratio **exactly 8.0**, both seven orders above the
regulariser. So whitening is fine. What the comparison actually shows:

    columns retained              dK 40      K1 40            identical
    smallest gen. eigenvalues     -1.16e-15  +2.17e-15         both numerically ZERO
    next eigenvalues              7.40561e-06 / 7.41004e-06    agree to 6e-6 relative
    heldout, 2nd..5th smallest    1.97507e-02 / 1.97351e-02    agree to ~1e-3 relative
    heldout MINIMUM               1.4286e-14 / 1.8949e-14      differ by 1.326x

> **Everything agrees except the single statistic we read.** Its generalized eigenvalue straddles
> zero, so the conserved direction is an eigenvector of a numerically-null eigenvalue -- and the
> minimum over near-degenerate directions is the least stable functional available, which is the same
> mechanism that gives the floor its 2.8x scatter.

**So the span statistic is reproducible to ~1.33x under an exact algebraic rescaling.** That is a
measured instrument bound, better than the floor's 2.8x, and it bounds what any comparison of
suppressions can claim.

**Consequence for the headline, tightening it:** the measured A-vs-B suppression ratio is **1.23**.
That is **below the 1.33x reproducibility bound**, independently of the 3.08x seed scatter. So the
A/B difference is unreadable twice over -- by the pair's 0.03% separation, and by the instrument's
own reproducibility.

## A-vs-C POSITIVE CONTROL -- pre-registered before the numbers (TheBridge)

**The prior question, now that A/B is known to be untestable:** *can this instrument discriminate at
all?* **A null from an instrument never shown able to return a positive cannot be interpreted**, and
so far it has not been.

**Caveat stated first:** C keeps Carter **rationally**, so A-vs-C is *polynomial survivor vs rational
survivor*, not *survivor vs none*. **It does not answer the leg's original question.** It answers
whether the screen can separate two deformations at all.

    requirement, from dK's own residual after correcting A = 1/230,837 = 4.33e-06
      marginal (1x)   needs ||delta||/||D|| > 0.21%
      clean (10x)                           > 0.66%
      decisive (100x)                       > 2.08%

    A/B   0.0300%   signal/limit     1/48    <- fails against a PERFECT instrument, before noise
    A/C  11.5700%   signal/limit   3090x     <- clears it by three orders

**Prediction.** In a span test the scale is free, so C's `best-scale 3.5732` drops out and only the
SHAPE residual matters: `0.1157^2 = 1.339e-02`.

    PREDICTED  C + dK suppression   ~75x
    MEASURED   A + dK suppression    230,837x
    PREDICTED  ratio                ~3090x     -- 2300x above the 1.33x reproducibility bound

**A's number is a measurement, not a ceiling** -- checked, because a floor-capped suppression would
make this a bound against a measurement rather than two measurements:

    A unaug at eps=0.2  7.852e-09    A+dK  3.401e-14    A's floor 1.9853e-15
    margin/floor 17.1x  UNCENSORED   dynamic-range ceiling 3.95e+06x, i.e. 17x of headroom

**The honest weakening, and it is theirs:** the 11.57% is measured in DEFORMATION space, while what
matters is the angle in VIOLATION space -- the image under the map producing the O(eps)
Poisson-bracket residual -- **and that map need not preserve angles.** So `75x` is an ORDER OF
MAGNITUDE, not a number.

    C + dK lands in the tens-to-hundreds   dK is SPECIFIC; the instrument CAN discriminate,
                                           and the A/B null is a property of the PAIR
    C + dK lands near 230,000x             dK is GENERIC after all, and the sham result needs
                                           re-examining -- it excluded the function class, not a
                                           mechanism acting for any deformation

**75 versus 200 does not discriminate. The order of magnitude does.** Committed before the run.

**Design note:** `A + dK` is re-run inside the same job as `C + dK`, so the comparison shares every
configuration axis by construction. **The fingerprint gate catches a mismatch; building the job so no
mismatch is possible is strictly better**, and this is the first time today that happened by design
rather than by correction.

## POSITIVE CONTROL PASSES: the instrument CAN discriminate, and dK is specific

       eps       A supp     C supp     ratio |  A+dK/floor  C+dK/floor
      0.05      34,350x        55x      622x |       7.2x        5.7x
      0.10     120,200x       145x      829x |       8.4x       11.4x
      0.20     230,837x       192x    1,204x |      17.3x       32.6x

    PREDICTED  C+dK suppression ~75x, as an ORDER OF MAGNITUDE (tens-to-hundreds)
    MEASURED                    55x .. 192x                        IN THE BAND
    PREDICTED  ratio ~3090x     MEASURED 1,204x                    SAME ORDER

**Both arms uncensored** (minimum margin/floor 7.2x and 5.7x), and the ratio sits **905x clear of the
1.33x reproducibility bound**. `C + dK` is monotone in eps with exponent 1.255; `A + dK` is monotone
at 0.634.

> **`dK` suppresses the deformation it was derived from by ~2e5x and a DIFFERENT deformation by
> ~1e2x -- a separation of three orders. The screen is not generic, and it CAN discriminate once the
> pair is actually separated.**

### What this settles, and what it does not

    SETTLED   The instrument can return a positive. A null from it is now interpretable at all,
              which it was not before this ran.
    SETTLED   dK is SPECIFIC to A's deformation -- consistent with the sham (same shape, no effect)
              and now shown from the other side (different deformation, 1000x less effect).
    SETTLED   The A/B null is a property of the PAIR. Same instrument, same column, same grid:
              0.03% separation -> ratio 1.23 (unreadable); 11.57% separation -> ratio 1,204.
    NOT       The leg's original question. C keeps Carter RATIONALLY, so this is
              polynomial-survivor vs rational-survivor, not survivor vs none.

**A noted asymmetry, recorded not explained:** `C unaug` has a **3.6x LARGER** deformation than A
(`||D_C||` 0.7299 vs 0.2029) yet a **24x SMALLER** margin (2.02e-11 vs 4.91e-10). Plausibly because C
keeps Carter rationally and the library IS rational (`d2_rat`), so part of C's invariant is already
representable. Consistent with the picture; not tested here.

**The prediction's weak leg held.** It was committed as an order of magnitude precisely because the
11.57% is an angle in DEFORMATION space while the relevant angle lives in VIOLATION space, and that
map need not preserve angles. The measured 1,204x against a predicted ~3090x is a factor of 2.6 --
well inside an order, so the angle is approximately preserved here. **That is a bonus finding about
the map, not something the prediction was entitled to.**

## The C-margin loose end, split into two prints (TheBridge)

**The asymmetry is larger than I stated it.** `||D_C||/||D_A|| = 3.60`, so amplitude^2 predicts C's
margin should be **12.9x LARGER**. Measured **24.3x smaller**. Total discrepancy **315x** -- not a
detail I can leave as "plausibly because".

**And it splits, because `heldout = mean_traj(var_within) / var_total` is a RATIO and the two
explanations live in different halves of it:**

    (1) REPRESENTABILITY (my hypothesis). Part of C's invariant is already in the rational
        span, so the best fit is genuinely better and the NUMERATOR is small.
        PREDICTS  var_within(C) ~24x SMALLER than A's   -> ratio ~0.04

    (2) NORMALISATION. A 3.6x larger deformation gives a larger across-ensemble spread of
        the candidate quantity, so the DENOMINATOR is larger and the ratio falls with no
        representability at all.
        PREDICTS  var_within(C) ~13x LARGER than A's    -> ratio ~13

**They differ by ~315x in the numerator and point in OPPOSITE directions.** Printing `var_within`
and `var_total` separately for A and C either closes the loose end or makes it real. Two prints, no
new run -- and I had written "plausibly because C keeps Carter rationally" as an explanation when the
data to test it was already inside the statistic.

### A tension to flag now, before the numbers

**Leg 6 recorded C's rational rung as CERTIFY-RELATIVE-TO-BASIS -- C's survivor is OUTSIDE
`d2_rat`.** Hypothesis (1) says part of it is INSIDE. Different statistics on different objects, so
not formally contradictory, **but they point opposite ways about the same question, and whichever
survives the other needs its scope restated.** If (1) holds it is the more interesting outcome,
because the leg-6 C conclusion is one of the few things from that leg still standing.

**Pre-registered before the print:** `var_within(C)/var_within(A) < 0.3` reads as (1),
`> 3` reads as (2), and anything between is neither cleanly and stays an open loose end rather than
being assigned to whichever story I prefer.
