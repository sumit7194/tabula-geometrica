# Leg 6 follow-on: the `dK` span test

Run order, and what each arm is for. Every script sets `NTRAJ, NSTEP = 40, 3000` and seed 1/51
explicitly, and minimises over **all** conserved directions — matching the reference that produced
the banked `1.947` exponent and `8.2238e-15` floor. Deviating on any of those five axes moved a
floor by 136x (silent_nulls 60).

| script | what it establishes |
|---|---|
| `make_dK.py` | builds `dK = -(K1 - 56 chi^2 dH)/8` to O(chi^2) from ansatz's recipe (their commit `004f564`), read not recalled |
| `dK_control.py` | **bridge validation.** Does `Q + eps*dK` drift at O(eps^2)? Two-sided: `K1` must reproduce its banked `0.11x`. Result: `623.7x` vs a pre-registered `627x`, split `b = 0.1%` = pure truncation |
| `expo_stability.py` | **is the exponent stable against the ULP that moved the floor 2.8x?** `A' = expand(A)` — same maths at every eps, different tree. Result: exponent shifts 1.5%, absolute margin 3.08x |
| `dK_floors.py` | **per-arm eps=0 floors.** A floor belongs to a (metric, basis, seed, readout, run-params) tuple, not to the apparatus |
| `dK_span_ext.py` | the span test on the **uncensored** grid `eps in {0.05, 0.1, 0.2}` |
| `sham_ext.py` | **the negative control.** Same structure as `dK`, coefficients permuted, does not solve the Killing equation |

## Result

`dK` suppresses the margin by ~2e5x for **both** A (Carter-preserving) and B (Carter-destroying),
ratio 1.23 against 3.08x seed scatter. The sham does **nothing** (1.5x) while sitting 25,000x above
its own floor. So the effect is real and specific to `dK`, and is *not* about completing Carter for
A. The pre-registered discriminator ran and the claim failed.

Not in `verify.sh`: the pre-registered discriminator failed, so there is no green gate to assert.
