# Pre-registration — §193b: the rank-6 discriminator for TS δ=2's approximate Carter-like direction

*Frozen 2026-09-24, before any rank-6 statistic. It is not to be run until The Bridge gives the go (ansatz's
overnight job has priority).*

## The question

§193 found TS δ=2 **NONE up to rank 4**, but it carries an APPROXIMATE Carter-like direction that improves
150–1.8e5× from rank 2 to rank 4. ZV δ=2, on the same far-field shells, changes by only 0.09–8×. Two readings
fit:
- **(a) an approximant:** a convergent formal series on regular orbits of a near-Kerr, non-integrable flow;
- **(b) an exact invariant:** of rank > 4, or not polynomial in the momenta.

Rank 6 separates them where (b) is a rank-6 polynomial. If (b) is non-polynomial, rank 6 reads as (a), so the
verdict wording says "polynomial, rank ≤ 6".

## The design: identical to §193 except the rank

- The same code (193_ts2_screen.py and its engine), both q, both arms, **the same shells**, the same ensembles
  (60 + 60 orbits, 20000 RK4 steps at dt = 0.1, stride 20).
- The same band (10³) and APPROXIMATE ceiling (1e-6).
- **Cells:**
  - CR even r = 6 at d = 4 and d = 6 (s = 3);
  - CR odd r = 5 at d = 4 (s = 3; its floor comes from the even r = 6, d = 4 Kerr cell, per the A5 rule).
  - d = 6 at r = 6 runs only if the footprint probe allows it under the house watchdog. If it doesn't, it is
    dropped, and the verdict is scoped to d = 4.

## Gates, in order. Controls first; TS is not integrated unless they pass.

- **K6 — Kerr count table at rank 6** (every shell, both q, both arms). Even r = 6 must give:
  - **2** at d = 4 (K, K²; K³ needs y⁶ and is not representable);
  - **3** at d = 6 (K, K², K³).
  - Odd r = 5 must give **0**.
  - Carter must be in span with residual < 1e-3.
  - Any failure → REFUSED, and TS is not read.
- **Z6 — ZV at rank 6:** 0 in every shared-arm cell (the negative control; there is none in the strong arm).

## TS verdicts at rank 6, per (q, arm, cell)

- **floor** = the Kerr ratio of the last expected direction in that cell (as in §193).
- **ratio_TS** = TS's best held-out ratio in that cell.
- **EXACT (polynomial, rank ≤ 6):** ratio_TS ≤ 10³ × floor on **every** shell of the arm.
- **APPROXIMANT:** ratio_TS > **10⁵** × floor on **every** shell, meaning at least two decades outside the band.
  It is sub-labelled from the rank-4 → rank-6 change in ratio_TS (same q, arm, shell, d = 4):
  - *continuing descent:* improvement ≥ 10× on every shell;
  - *stalled:* improvement < 10× on every shell;
  - *mixed:* anything else.
- **INCONCLUSIVE:** anything else. That means:
  - (i) any shell with ratio_TS in the grey zone (10³, 10⁵] × floor; or
  - (ii) some shells within the band and others not.
  Case (ii) is reported as a candidate SHELL-RESTRICTED integral and never as a Killing tensor (The Bridge's
  rule from §193).

The verdicts are reported per arm and **never merged** across arms. The strong arm stays "Kerr-controlled only".

## What each outcome would mean (fixed now)

- **EXACT in both arms** → escalate to ansatz's exact rung and quantum's proof tool as a candidate rank-≤6
  polynomial integral, with the coefficient vector exported. It is not a claim until symbolic verification.
- **APPROXIMANT** → the rank-axis descent is a formal-series approximant. The rank-≤6 null stands, and the
  post-hoc pattern of §193 is explained.
- **INCONCLUSIVE** → report it as such. There is no fix round without a new pre-registration.

## Scope

As §193: numerical, the named family, bound prograde timelike orbits on the same shells, vacuum via ansatz's
Schwartz–Zippel check, and the odd-degree reduction validated only indirectly.

## Amendment 1 — from the Kerr-only footprint probe (n = 20), before any rank-6 TS statistic

**The probe numbers:**

| Kerr cell | p | smallest held-out ratios | peak footprint |
|---|---|---|---|
| even r=6, d=4 | 1679 | 1.4e-21 (K) · 1.2e-17 (K²) · **1.7e-14** (K³ approximant, not representable) · 0.78 | — |
| odd r=5, d=4 | 1260 | 0.97 | — |
| even r=6, d=6 | 3135 | 2.7e-20 · 3.0e-18 · 2.2e-16 (K³) · 0.78 | **3435 MB** |

**The weakness it exposed.** At rank 6 the band is anchored on the *worst-resolved* expected Kerr power. At d = 4
that is K² at 1.2e-17, so the band reaches 1.2e-14, and a non-representable K³ *approximant* sits only 1.4×
outside it. A TS approximant could therefore fall inside a band this generous and read as EXACT. §193's
rank-4 margins were not like this.

**R1, a resolution gate added before any TS statistic.** A cell can issue EXACT or APPROXIMANT only if its Kerr
control *resolves*: the ratio between Kerr's first non-expected direction and its last expected direction must be
≥ 10⁵ (the same two decades that separate APPROXIMANT from the band). A cell that fails this is
**UNRESOLVED → REFUSED**, and TS is not read in it. With this gate, a TS approximant cannot win just because the
control was noisy there.

**R2, footprint.** 3.4 GB peak at d = 6 (p = 3135). If The Bridge's watchdog budget does not allow it when the
go arrives, the d = 6 cells are dropped and the verdict is scoped to d = 4, as pre-registered.
