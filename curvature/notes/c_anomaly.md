# The C anomaly — why is C's Carter quantity so well conserved?

Opened 2026-09-23. Queue item 1b. Pre-registered before any run in this file.

## What is claimed, and the provenance defect found on opening

Leg 6's closing arc reported that object C conserves bare Carter `Q` far better than object A,
"confirmed by two independent instruments agreeing to a factor of 2.24":

    analytic Q-drift (amplitude)   A/C = 13.9   -> as a variance, 193
    engine heldout(Q)  (variance)  A/C = 432

**Opening this file, I recovered the analytic-drift command from the session transcript. It reads
`a = m.A_SPIN` and never assigns it, so it ran at 190's default `A_SPIN = 0.6`. The engine
statistic was run with `s.A_SPIN = 0.075`.** Seed (1/51), NTRAJ (40), NSTEP (3000) and eps (0.05)
match; **chi does not.** The celebrated agreement compared quantities at two different spins — a
SIXTH borrowed denominator, on the chi axis.

> **Correction to the sentence as first written** ("an axis `comparable.py` never listed"): wrong in
> kind. The gate is AXIS-AGNOSTIC -- any configuration key that differs raises. The chi mismatch was not
> an axis the gate missed; **the comparison never passed through the gate at all.** It was made in prose,
> in a message to a peer, from two numbers that had never been wrapped with their configuration. A gate
> only protects comparisons routed through it, and the most consequential comparisons of the week were
> made in conversation. The chi arm added to the known-fail suite below documents the instance; it does
> not close the gap, which is structural.
It may still hold (if A's and C's deformations scale identically in chi the ratio is chi-free),
but that is an assumption, not a measurement, and it is being measured below.

## M1 — re-measure at ONE configuration (pre-registered)

Both instruments, all three objects, at chi = 0.6 AND chi = 0.075, identical seed / NTRAJ / NSTEP /
eps. Compared at matched power: `(drift ratio)^2` against the heldout ratio.

    if A/C matches across instruments at each chi   -> the anomaly is real at that chi
    if A/C is chi-independent                        -> last night's cross-chi 2.24 was valid
                                                        by luck of scaling, now shown
    if A/C moves with chi                            -> the 2.24 was an artefact of mixing chi

## M2 — mechanism (pre-registered prediction, stated before computing it)

Kerr separates: `2*Sigma*H = R(r, p_r) + Theta(theta, p_theta)` with `Sigma = r^2 + a^2 cos^2 theta`,
so `Theta - 2H a^2 cos^2 theta = 2H r^2 - R` is conserved — Carter's constant (Carter 1968). **A
deformation of `2*Sigma*H` depending on (r, p_r) ONLY leaves that same expression conserved, so bare
`Q` stays exactly conserved.** Only the part of the deformation that is angular or non-separable
can make bare `Q` drift at O(eps).

    PREDICTION: C's deformation of Sigma*H is dominated by a radial-only part, and its
    angular + non-separable part is ~13.9x smaller than A's at chi=0.6 (amplitude).

**Known-positive control:** a synthetic RADIAL-ONLY deformation must give bare-Q drift at the
integration floor (the eps=0 value); a synthetic angular one must not. If the radial control drifts,
the separability argument is wrong in this code's conventions and M2 issues no verdict.

## M1 RESULT — the anomaly is real at every configuration; the celebrated 2.24x was an artefact of mixing chi

Both instruments, both trajectory sets, both chi, eps = 0.05, 40/3000. The first row reproduces the leg-6
analytic drift **to all digits (7.1304e-03)**, so this is the same instrument.

         chi seed obj   drift(eps=0)     drift      heldout
         0.6    1   A     4.006e-14   7.1304e-03  9.3116e-05
         0.6    1   C     4.027e-14   5.1363e-04  3.0009e-07
         0.6   51   A     4.460e-14   6.2995e-03  9.3308e-05
         0.6   51   C     4.397e-14   4.3419e-04  2.8592e-07
       0.075    1   A     4.640e-14   1.1632e-04  2.3575e-07
       0.075    1   C     4.609e-14   6.8927e-06  6.0002e-10
       0.075   51   A     2.761e-14   1.0079e-04  2.0054e-07
       0.075   51   C     2.792e-14   5.7350e-06  4.6401e-10

    A/C at MATCHED power, same config:
         chi  seed   drift A/C   (drift A/C)^2   heldout A/C   agreement
         0.6     1       13.88          192.7          310.3       1.61x
         0.6    51       14.51          210.5          326.3       1.55x
       0.075     1       16.88          284.8          392.9       1.38x
       0.075    51       17.57          308.9          432.2       1.40x

**1. The anomaly is real, at both chi and both seeds.** C conserves bare Q 14-18x better than A in amplitude,
310-430x in variance, every eps=0 floor at ~4e-14.

**2. At matched configuration the two instruments agree to 1.38-1.61x**, systematically in one direction
(heldout above drift^2, as expected from a variance ratio against a global max). **The celebrated 2.24x was
WORSE than the true agreement**, because it divided a chi=0.6 drift by a chi=0.075 heldout.

**3. The ratio is NOT chi-independent**: drift A/C moves 13.88 -> 16.88 and heldout 310 -> 393 from chi=0.6 to
0.075, a 20-27% shift. So the cross-chi comparison was not valid "by luck of scaling". It landed within 2.24x
because two shifts partly cancelled, which is no reason to trust it.

**4. A and B are identical to every printed digit** (drift 7.1304e-03 vs 7.1305e-03; heldout equal). That is the
0.03% deformation overlap from leg 6 showing up in a third, engine-free statistic.
