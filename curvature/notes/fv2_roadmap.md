# F-v2 roadmap — the gravity-law track, next few steps

Self-contained so it can be executed without the chat context that produced it.
**Where we are (2026-06-12):** the "matter → geometry" law (Phase F, 2+1) and its
3+1 scale-up are BOTH honest nulls. The pre-registered diagnostics (`scripts/
22_fv2_diagnostics.py`) are running to tell us *why* before we touch architecture.

**Non-negotiable guardrails (this is what we got wrong before):**
- Measure the achievable floor, then gate relative to it. Oracle F1 floor = **1.2e-4**
  (already measured) — the 1e-3 gate is feasible; Phase F's 0.058 is a real shortfall.
- Change **one knob at a time** + keep a control. The 3+1 run changed kernel + channels
  + data-budget at once → uninterpretable. Never repeat that.
- Report **every** gate, never cherry-pick the one that passed. Null results are results.
- ≥3 seeds for any headline number. LR is a swept choice, not a default.

---

## STEP 1 — Read the diagnostics (when `results/22_fv2_diag.json` is complete)

Compare each arm to Phase F baseline (F1=0.058, F2=0.937) and the oracle floor (1.2e-4):

| Signal in `22_fv2_diag.json` | Reading | Points to |
|---|---|---|
| `overfit_one_batch` loss ≪ 0.058 (e.g. <1e-3) | net CAN represent a field | NOT raw expressivity → it's generalization/training |
| `overfit_one_batch` loss stays high (~0.05+) | can't fit even ONE batch | architecture wall (receptive field / capacity) → go to Step 2A |
| best `lr_*` F1 ≪ `lr_1e-3` F1 | 1e-3 was a bad default | optimizer-bound → Step 2B |
| `capacity_2x` F1/F2 clearly beats baseline | width helps | capacity-bound → Step 2A |
| `data_2x` F1/F2 clearly beats baseline | more worlds help | data-bound → Step 2C |

Most real outcomes are a mix; rank the effects by size and address the biggest first.

## STEP 2 — Pick the F-v2 intervention from the dominant signal

**2A. Receptive-field / capacity bound** (the leading hypothesis: a local CNN vs a
long-range 1/r kernel). Fix options, cheapest first: larger kernels (5→7) or **dilated
convs** (cheap receptive-field gain); a small **U-Net** (downsample→upsample widens RF
without param blow-up); or **Fourier features / a spectral layer** (1/r is long-range —
spectral methods represent it natively). Pre-register the SAME gates; this time it's a
clean test because only the RF/capacity changes.

**2B. Optimizer bound.** Adopt the best swept LR + cosine decay + longer training
(plateau-based, not round numbers), re-run Phase F proper, re-gate.

**2C. Data bound.** Scale worlds (600→1200), maybe widen the mass/position priors.

## STEP 3 — The CLEAN locality experiment (what 3+1 should have been)

Hold capacity, channels, data, steps, LR **fixed**; vary **only** receptive field
(kernel size ∈ {3,5,7,9} or dilation ∈ {1,2,4}) on the 2+1 problem. Plot F2_cos vs RF.
This is the one-knob test that actually adjudicates the locality hypothesis. If F2
climbs with RF → locality confirmed, and 2A is the right family.

## STEP 4 — Redo 3+1 honestly

Only after 2+1 passes. Match **samples-seen** to the 2+1 run (don't cut steps when you
cut batch), match capacity (5³ kernels or dilation, comparable channels). **First** run
the coordinate sanity check: inject the TRUE field into the 3D rollout and confirm it
reproduces the ground-truth trajectories — separates a `(z,y,x)` grid_sample/trilerp
bug from a learning failure (the 3+1 F4=3.4× left this open). Use `--device mps` for
cheap local iteration; reserve the L4 GPU for any multi-seed sweep.

## STEP 5 — Back onto the main arc

A clean 2+1 (and 3+1) matter→geometry law is the launchpad for the project's stated
finale: gravity *as* curvature (mass → Ricci → geodesics) and then Kaluza–Klein. The
curvature-invariant readout (`17_curvature_invariant.py`, corr 0.99 on Phase E) is the
template for expressing the learned law in coordinate-free currency.

---

## Ready-to-run commands

```bash
cd curvature
# the diagnostics (already running; relaunch resumes — skips finished arms):
nohup .venv/bin/python scripts/22_fv2_diagnostics.py --steps 4000 > /tmp/fv2_diag.log 2>&1 &

# Phase F fresh re-run (stale ckpt already renamed; trains from scratch):
.venv/bin/python scripts/19_matter_to_geometry.py

# 3+1, fast local GPU path:
.venv/bin/python scripts/21_matter_to_geometry_3p1.py --device mps

# after ANY change, the regression gate must stay green:
cd .. && ./verify.sh
```

Live progress (no Claude needed): http://localhost:8788/dashboard.html ·
results in `curvature/results/*.json` · decisions/results in this `notes/` folder.

## How the diagnostics run — and reading the dashboard

`22_fv2_diagnostics.py` runs the arms **strictly one at a time, sequentially** (oracle →
overfit → lr_lo → lr_mid → lr_hi → cap2x → data2x). It does NOT run them in parallel.
At any moment only ONE `22_*` card is genuinely advancing; the others are either
not-yet-started or finished-and-frozen at their last step.

Dashboard gotcha: a card is "live" only if its step number is *increasing* — a green
"Running" badge just means the heartbeat file is recent (<6 min), so a recently-finished
arm or a leftover smoke-test file (look for a tiny total like `/20`) can show green
without moving. If a `22_*` card sits at the same step, it is not running; trust the
advancing one. To purge stale heartbeats: `rm curvature/results/progress/22_*.json` for
any arm that isn't the current one (they regenerate when their real arm starts).

Prefer to drive manually instead of the battery? Run the individual scripts (19 fresh
Phase F, 21 the 3+1, with the commands above) one at a time — same results, full control,
no batch driver. The battery is just those same runs sequenced + checkpointed.
