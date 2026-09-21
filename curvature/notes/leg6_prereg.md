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
