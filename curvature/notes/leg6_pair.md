# 1a — a WELL-SEPARATED Carter pair: can the screen tell keep from break when the pair CAN be told apart?

Opened 2026-09-23, straight after the C anomaly (curvature/notes/c_anomaly.md), whose M2 result makes this
design possible. Pre-registered before any object here is built.

## Why leg 6's test could never run, and what this fixes

Leg 6's A (keeps Carter) and B (breaks it) were the same deformation to 0.03% (cos +1.000000), so the Carter
distinction sat ~7 orders below the noise. And A's first-order correction dK came from a truncated O(chi^2)
recipe, through another repo's solver, across a convention bridge.

M2 established, with controls, that in this code's own coordinates Kerr separates as
2*Sigma*H = R(r,p_r) + Theta(th,p_th), and that a deformation of 2*Sigma*H splits into
**radial** (bare Q exactly conserved), **angular** (Carter becomes Q + eps*dTheta exactly), and **mixed**
(separability broken). So I can BUILD both members of the pair, with the keeper's correction known in closed form:

    KEEP    purely angular:  Sigma*d(ith) = g(th)            conserved: Q + eps * g(th) * p_th^2, EXACTLY
    BREAK   purely mixed:    Sigma*d(ith) = f(r) * g(th)     with f zero-mean on the orbit region,
                                                              so it is nearly ORTHOGONAL to KEEP

## Two pairs, because "is the invariant in the basis" is the variable that matters

The screen's basis `d2_rat` contains `cos^2(th) * p_th^2` but not `cos^4(th) * p_th^2`.

    PAIR 1 (IN SPAN)      g(th) = (49/20) cos^2 th     KEEP's invariant is representable by the screen as-is
    PAIR 2 (OUT OF SPAN)  g(th) = (49/20) cos^4 th     KEEP's invariant is NOT; its correction column is
                                                        dTheta = (49/20) cos^4 th p_th^2, known exactly

## Requirements that must hold BEFORE any screen result is read

- **Separation:** cos(D_KEEP, D_BREAK) < 0.3 in each pair, on the sampled orbit region (leg 6 was +1.000000).
- **Construction checks via the M2 split:** KEEP's mixed part ~0 (it really is separable); BREAK's mixed part
  dominant (it really breaks separability).
- **Every arm on one configuration** (chi, seed, NTRAJ/NSTEP, readout) with its OWN eps=0 floor, eps grid
  {0.05, 0.1, 0.2} (the uncensored grid from leg 6).

## Predictions, registered now

    PAIR 1, unaugmented      KEEP EMITS at every eps (invariant in span, margin at the floor, no eps^2
                             scaling); BREAK certifies with exponent ~2.
                             -> the screen CAN see integrability when the invariant is representable.
    PAIR 2, unaugmented      KEEP and BREAK BOTH exponent ~2 -> the margin measures deformation amplitude
                             when the invariant is outside the basis (leg 6's finding, on a pair that can
                             actually be separated).
    PAIR 2, + dTheta column  KEEP collapses to its floor; BREAK stays at exponent ~2.
                             -> adding the missing column restores discrimination.

**Read by shape, not floor ratios** (floors carry ~2.8x ULP scatter). **Secondary, noise-immune readout:**
score the KNOWN direction `Q + eps*dTheta` directly with the within/total statistic (650x more stable than the
minimum over the basis). It needs no basis at all, so it is the cleanest check that KEEP keeps and BREAK breaks.

**If PAIR 2's augmented BREAK also collapses:** the column absorbs amplitude generically, the test is VOID, and
it is reported that way.
