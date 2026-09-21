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

---

# RESULT (appended 2026-09-21; nothing above this line edited)

**WINDOW ARTIFACT CONFIRMED. √3 is a coincidence of the N/4 window, not a property of the chain.**

**Arm A — identical chain, identical `C(r)`, only the fitted points differ:**

    W = N/8  (64)    saturated ratio 3.3832     [31 points fitted]
    W = N/4  (128)   saturated ratio 1.7189     [63 points]    <- §187's window
    W = N/2  (256)   saturated ratio 0.7792     [127 points]
    W = 3N/4 (384)   saturated ratio 0.7792     [127 points — the amplitude cut binds before the window]

**The answer moves by 334% on data that never changed.** The fitted ξ is a property of where the line was
drawn. `√3 = 1.732` sits at `W = N/4` and nowhere else.

**Arm B — my own suspect, refuted.** The obvious mechanism was a power-law prefactor `C ~ e^{−r/ξ}/r^α`
biasing a pure-exponential fit. Refitting with α free gives **α = 0.008 … 0.034 — essentially zero** — and the
three-parameter fit is degenerate (ξ unrecoverable). **The prefactor is not the cause.** The cause is simply
that a straight line through a window much shorter than ξ has its slope set by the window.

**Arm D — and this refutes something I had already sent a peer.** I wrote to TheBridge that the two estimates
*"calibrate each other somewhere, and that somewhere is inside the band."* They do cross — at

    W = 64    ξ_cross = 31.9    ξ_cross/W = 0.498
    W = 128   ξ_cross = 69.4    ξ_cross/W = 0.542

**ξ_cross ≈ W/2.** The agreement point is set by the *fit window*, not by the chain. It is not a calibration
between two methods; it is where two window-dependent curves happen to intersect, and it moves when the window
moves. **Corrected within the hour of having claimed it, by the run built to test something else.**

**Arm C is confounded and supports nothing.** Varying N at fixed window *fraction* moves the window and the
finite-size scale together, and at these masses `ξ = 1/m ≫ N` for every N, so the chain's own length also sets
the decay. Its near-flatness (1.66 / 1.69 / 1.67) is **unexplained** and is not used. The verdict rests on
arm A alone.

## The control did its job, on the run built to test a regularity

**The first execution FAILED L1** — 1.6345 against §187's 1.7270. The bug: I took the saturated ratio from
`rat[-5:]`, the *largest* masses, which is the *smallest* ξ — the opposite end of the sweep from saturation.
A real bug, in the run designed to check someone else's number, caught by the control that run was required to
pass. Fixed; L1 now 1.7189 vs 1.7270.

## What §187 keeps and what it loses

**Keeps:** the ABSTAIN verdict, entirely. It rests on the envelope decay (3.2% across the fit window) and the
box violation, both measured, and √3 was deliberately kept out of it.

**Loses:** the third signature's *interpretation*. The two-estimate ratio is still a usable measurability
diagnostic — a large disagreement still says the fit is window-dominated — but its numerical value, its
saturation and its crossing point are all properties of the window and none is a constant of the system.
Updated in `xistar_prereg.md`.
