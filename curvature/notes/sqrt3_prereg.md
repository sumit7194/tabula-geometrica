# PRE-REGISTRATION — is the 1.73 ratio a FIT-WINDOW artifact?

**Frozen before the script exists.** §187 left an unexplained regularity: the two independent ξ estimates
(envelope fit vs corrected continuum `1/m`) have a ratio that runs 0.54 → 1.00 → **1.73** across the sweep,
saturating near √3 = 1.732 at large ξ. I declined to narrate a mechanism and wrote: *"if it wants explaining it
wants a run, not a paragraph."* This is the run.

## The suspect, and why it is not obviously right

Obvious suspect: a power-law prefactor in `C(r) ~ e^{−r/ξ}/r^α` biasing a pure-exponential fit. **But a
window-dominated bias should make `ξ_measured` SATURATE at a constant, and it does not — it stays ∝ 1/m with a
constant multiplicative offset.** So the obvious suspect may already be refuted by data I have. That is why
this is a run and not a paragraph.

## The decisive test: same data, different window

**A window artifact must depend on the window.** Arm A holds the chain, the correlation matrix and the mass
grid **completely fixed** (N = 512) and varies ONLY the fit window `r ∈ [2, W)` over `W ∈ {N/8, N/4, N/2,
3N/4}`. Identical `C(r)` in every case; the only thing that changes is which points the line is fitted to.

    PREDICTION (window artifact):   the saturated ratio MOVES systematically with W
    PREDICTION (real constant):     the saturated ratio is UNCHANGED across W

Both outcomes are informative and the second **refutes my own suspect**, which is the point of running it.

## Arm B — the power-law fit

Refit as `log|C| = A − r/ξ − α·log r` (three parameters) on the same data. If the prefactor is the cause, the
recovered ξ should track `1/m` (ratio → 1) and α should come out stable and positive. If ξ stays biased, the
prefactor is not the cause.

## Arm C — vary N

Window scales with N. `N ∈ {256, 512, 1024}` at fixed window fraction confirms or breaks A.

## Known-fail control

Arm A must reproduce §187's number exactly at `W = N/4` (ratio 1.727 at the wall, on the same code path).
**If it does not, the harness differs from §187's and no conclusion is drawn about §187's regularity.**

## What I will NOT do

Report a mechanism that arm A and B do not jointly support. If the ratio is window-independent AND the
power-law fit does not fix it, the honest outcome is **"√3 remains unexplained, and two candidate mechanisms
are now excluded"** — which is worth more than a plausible story.

**This changes nothing in §187.** The abstention rests on the envelope decay (3.2%) and the box violation, both
measured; √3 was already kept out of that verdict.
