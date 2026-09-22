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
