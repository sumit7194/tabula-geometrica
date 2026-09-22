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

## RESULT (§192, results/192_leg6_pair.json) — with a separable pair, the screen tells keep from break

chi=0.075, seeds 1/51, 40/3000, readout min over ALL directions, own eps=0 floor per arm. Exit 0.

### Construction checks — all pass, so the screen results are readable

    pair 1: cos(KEEP, BREAK) = 0.131        pair 2: cos(KEEP, BREAK) = 0.221      (need < 0.3; leg 6 was 1.000000)
    KEEP1  angular 1.321   mixed 4e-32          KEEP2  angular 0.328   mixed 2e-64    (KEEP really is separable)
    BREAK1 angular 0       mixed 1.637          BREAK2 angular 0       mixed 0.431    (BREAK really is mixed)
    cos^4 in span{1, cos^2, 1/sin^2}: relative residual 4.0e-02   -> OUT of span, but only by 4%

### The screen

                       eps=0       0.05        0.10        0.20
    KEEP1             3.0e-15     1.3e-15     1.8e-14     8.4e-15     at floor: EMITS
    BREAK1            3.0e-15     2.3e-03     6.2e-03     3.6e-03     certifies, non-monotone
    KEEP2             3.0e-15     1.7e-08     2.0e-08     2.3e-08     7 orders above floor, nearly FLAT (exp 0.21)
    BREAK2            3.0e-15     1.5e-04     7.0e-04     4.5e-03     monotone, exp 2.46
    KEEP2  + dTheta   6.2e-15     3.3e-14     8.0e-16     1.2e-15     COLLAPSES to floor (1.9e7x at eps=0.2)
    BREAK2 + dTheta   6.2e-15     1.4e-04     6.6e-04     4.2e-03     unchanged (0.93-0.95x), exp 2.48

    SCORED KNOWN DIRECTION Q + eps*dTheta  (no basis, the noise-immune readout):
    KEEP1 / KEEP2     ~1e-26 at every eps  (integration floor)
    BREAK1            7.5e-02  2.7e-01  3.2e-01
    BREAK2            4.3e-03  1.9e-02  8.2e-02
    separation        4.0e24x (pair 1)   1.3e23x (pair 2)

### Scored against the pre-registration

| registered prediction | result |
|---|---|
| PAIR 1: KEEP emits at every eps | **HOLDS** — at floor throughout |
| PAIR 1: BREAK certifies with exponent ~2 | **certifies HOLDS (11 orders); exponent ~2 FAILS** — non-monotone (0.31). BREAK1's mixed part is 3.8x BREAK2's, so at eps=0.2 it leaves the perturbative regime; the scored readout saturates too (0.27 -> 0.32) |
| PAIR 2 unaugmented: KEEP and BREAK both exponent ~2, margin measures amplitude | **FAILS, in the informative direction.** KEEP2 sits 8.6e3-2.0e5x below BREAK2 and is nearly flat (exp 0.21) against BREAK2's 2.46. The screen discriminates pair 2 even WITHOUT the missing column |
| PAIR 2 + dTheta: KEEP collapses to floor | **HOLDS** — 1.9e7x drop |
| PAIR 2 + dTheta: BREAK stays at exp ~2 | **HOLDS** — 0.93-0.95x of unaugmented, exp 2.48 |
| VOID if augmented BREAK also collapses | **did not happen** — the column is specific, not generic |

### What this establishes

**Leg 6's "the margin measures deformation amplitude, not integrability" was a property of its PAIR, not of
the screen.** Given a keeper and a breaker that are actually different (cos 0.13-0.22 instead of 1.000000), the
unaugmented screen separates them by 4-12 orders, the missing column collapses the keeper by 7 orders while
leaving the breaker untouched, and the basis-free scored readout separates them by ~23 orders.

**My pair-2 prediction was wrong, and it is the most useful thing in the table.** I registered that an invariant
outside the basis would make the margin blind (both arms exponent ~2). It did not: an invariant only **4%**
outside the span leaves the keeper's margin flat and four orders below the breaker's. The screen partly sees an
approximately-representable invariant. So "outside the basis" is not binary: 4% out is still visible, and leg 6's
A was blind because its correction was FAR out, not because out-of-span means invisible.

**Not explained, recorded as open:** why KEEP2's unaugmented margin plateaus near 2e-8 and barely moves with eps.
The 4% span residual is the natural candidate; it is untested.

### Limits
Toy pair, one chi, built in-house rather than taken from ansatz's catalogue — so this validates the SCREEN on a
pair that can be told apart, not any claim about ansatz's A/B/C. The bridge from these results to their spacetimes
is the next step if anyone wants it.
