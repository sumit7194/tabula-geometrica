# VM work plan — GPU (L4) tasks for tabula-geometrica (2026-06-25)

The L4 box is free again; planning the GPU-only work before spinning it up. Everything local-feasible is already done
(build-queue Phase 1: 120-125 + the pokes). This doc is the Phase-2 (compute-bet) plan — the items that genuinely need
a GPU, sized + pre-registered, executable cold.

## VM facts (from memory: gcp-vm-alphaludo)
- `alphaludo-l4`, zone `us-east1-d`, `g2-standard-8` (8 vCPU, 31 GB RAM, 1× NVIDIA L4 24 GB).
- Connect: `gcloud compute ssh alphaludo-l4 --zone=us-east1-d --command='...'` (acct sumit.ridingagain@gmail.com,
  project project-452de276-1c16-46a7-8bb). **User spins it up; Claude does not start/stop it.**

## OPERATIONAL RULES (hard constraints)
1. Work ONLY inside the tabula-geometrica checkout on the VM. NEVER touch `~/AlphaLudo` (Ludo) or any conjecture_machine
   files/processes. Never broad `pkill`; verify process provenance (cwd/venv/cmdline) before signalling anything.
2. Before any heavy run: `nvidia-smi` to confirm the GPU is free (Ludo's `train_v12.py` is GPU-bound ~91% if running).
   If Ludo is training, STOP and ask the user — do not contend (degrades both); do not pause Ludo ourselves.
3. Long runs DETACHED (`nohup ... & disown`), resume-safe checkpoints (curvlib save_ckpt), dashboard heartbeats
   (curvlib.progress), `./verify.sh` after. Same loop as local.

## SETUP CHECKLIST (once the VM is up)
- [ ] `nvidia-smi` — GPU free? (else stop, ask user)
- [ ] clone/pull: `git clone https://github.com/sumit7194/tabula-geometrica` (or `git pull` if it exists) into a
      SpaceTime-only dir (NOT under ~/AlphaLudo).
- [ ] venv: python3.12 + `pip install -r curvature/requirements.txt` with **CUDA** torch (the requirements pin CPU
      torch for the Mac; on the VM install the CUDA build: `pip install torch --index-url <cuda wheel>`).
- [ ] device: run GPU scripts with `--device cuda` (curvlib + 21 + 61 already have a --device flag; trilerp/grid_sample
      work on CUDA — the MPS 3D-grid_sample gap, pytorch#141287, does NOT apply on CUDA).
- [ ] sanity: `python -c "import torch;print(torch.cuda.is_available())"` -> True.

---

## TASKS (prioritized)

### B0 (shovel-ready) — finish the 3+1 matter->geometry law (script 21) on CUDA
- **Why GPU:** 24^3-voxel 3D fields + 3D rollout; 3D grid_sample backward is unimplemented on MPS (pytorch#141287) so
  it could only run on CPU locally (slow) — CUDA is the natural home. Script EXISTS (21_matter_to_geometry_3p1.py,
  --device cuda), gates PENDING.
- **Do:** run 21 to completion on CUDA; evaluate its pre-registered gates; document + (if a saved gate) verify.sh.
- **Value:** quickest win (no new code); a locality probe in 3D (larger relative receptive field than 2D).

### A (headline, ALREADY BUILT — just run the sweep) — Phase F law via FNO: the 1/r long-range wall
- **Status:** script 100_fno_law.py EXISTS and ALREADY CRACKS THE WALL on the Mac (MPS): P0 overfit-one-batch
  3.7e-6 (vs the CNN's 0.047 representational wall -> the Phase-F failure WAS locality), F2 field cos 0.997 (gate
  0.98 PASS; CNN 0.937), F1 MSE 0.0144 (CNN 0.058), F4 control 0.39 (>>10x). P0-P3 all pass. The architecture
  hypothesis is CONFIRMED -- a global spectral operator carries the 1/r tail a local CNN cannot.
- **Remaining (VM):** only the absolute F1 trajectory-MSE gate (1e-3, oracle floor 1.2e-4). The modes sweep
  (run_fno_sweep.sh) already showed F1 SATURATES at ~0.015 at the 48-grid (Nyquist-limited: modes 24 == 14) -> the
  fix is a FINER GRID. **Run `scripts/run_fno_grid_sweep.sh` (grid 64/96, modes=grid//2, 3 seeds, 12k steps,
  --device cuda)** to resolve the near-mass field magnitude and drive F1 toward 1e-3. Pure scaling run, no new code.
- **Why GPU:** finer grids (64/96) x 12k steps x 3 seeds x 2 grids = the methodology-heavy budget the Mac can't do.
- **Value:** the biggest payoff -- turning the documented Phase-F NULL into a positive (P0 already does the headline
  adjudication; the grid sweep closes the last magnitude gate, or honestly bounds it at the grid-resolution floor).

### C — hail-mary global PINN (Choptuik), the untried lever
- **Why GPU:** PINN global solve (collocation + 2nd-order autodiff over a space-time domain) — moderate GPU.
- **Build:** in curvature/hailmary/ — a GLOBAL PINN solve of the Choptuik collapse (physics-in-loss, NO autoregressive
  rollout), the paradigm the literature (arXiv:2511.15247, w/ M. Choptuik) shows WINS where our autoregressive emulator
  hit the rollout wall (exp12). Re-confirms the structure-by-construction thesis from a new angle.
- **Pre-reg gates:** the PINN reproduces the critical solution / scaling where the learned emulator could not (the
  rollout wall, exp12, was the documented failure). Honest scope: a different paradigm, not the emulator.

### D — larger G-sym generalist + explicit legibility regularizer
- **Why GPU:** a bigger in-context/transformer generalist (script 28/61 line) + more episodes.
- **Build:** scale the symmetry-respecting generalist (28) and ADD a legibility loss term; test whether scale +
  regularizer resolves the accuracy<->legibility tension (stage clustering dropped 0.82->0.69 as per-body info migrated
  out). Pre-reg: accuracy retained AND clustering/legibility recovered (the tension broken, or confirmed fundamental).

### E — Wong color-charge v3, fuller observability
- **Why GPU:** modest; bundle with the others.
- **Build:** give the learner MULTIPLE field probes so the rotating Q(t) is OBSERVABLE (the partial-observability
  ceiling: trajectory-only sees Q only via Q.E along the path). Re-test dynamic legibility (static ceiling 0.89 / gate
  0.70; orthogonal-F v3 reached 0.56-0.64). Pre-reg: with full observability, dynamic legibility crosses 0.70.

### (optional) F — Phase G generalist at scale
- The in-context model (61, ~12.7M) at L4 scale; the world-summary-space structure prize (G3) at larger data.

---

## RECOMMENDED ORDER
A and B0 are BOTH shovel-ready (scripted, --device cuda) -> run them FIRST, in parallel-ish:
  A: `bash scripts/run_fno_grid_sweep.sh`  (FNO grid sweep -> F1 toward 1e-3; the headline)
  B0: `python scripts/21_matter_to_geometry_3p1.py --device cuda`  (finish the 3+1 law; gate F1-F4)
then the BUILDS: C (global PINN) -> D (G-sym + legibility reg) -> E (Wong fuller observability).

## PRE-BUILD STATUS (checked 2026-06-25 — mostly already done by past work)
- FNO (A): script 100 BUILT + Mac-validated (P0-P3 pass); modes sweep done (F1 saturates 0.015 @ 48-grid);
  run_fno_sweep.sh + run_fno_grid_sweep.sh scripted for the VM. -> JUST RUN the grid sweep.
- 3+1 law (B0): script 21 BUILT + --device cuda + F1-F4 gates wired. -> JUST RUN on CUDA.
- The only missing piece is environment bring-up on the VM:

## VM BRING-UP (paste once the VM is up + GPU verified free)
```
nvidia-smi                                            # confirm GPU free (Ludo not training); else STOP, ask user
cd ~/spacetime/tabula-geometrica 2>/dev/null || git clone https://github.com/sumit7194/tabula-geometrica ~/spacetime/tabula-geometrica
cd ~/spacetime/tabula-geometrica && git pull
cd curvature
python3.12 -m venv .venv 2>/dev/null; . .venv/bin/activate
pip install -q torch --index-url https://download.pytorch.org/whl/cu124   # CUDA torch (NOT the CPU pin)
pip install -q -r requirements.txt
python -c "import torch; assert torch.cuda.is_available(); print('CUDA OK', torch.cuda.get_device_name(0))"
```
(The repo + venv likely already exist from the earlier modes-sweep run -> then it's just `git pull` + verify CUDA.)

## STATUS
- [x] VM spun up + GPU verified free (2026-06-26: L4 stockout cleared; GPU 0 MiB, Ludo not training; CUDA torch 2.12.1+cu130)
- [x] **A (FNO grid sweep) DONE — pre-registered honest-null confirmed:** the sweep was launched + pre-registered
  2026-06-20 (lab_notebook); the g64/g96 numbers (filled in 2026-06-26) are F1 0.0141-0.0169 ~ the 48-grid's 0.015,
  F2_cos ~0.995. F1 is NOT resolution-limited (pre-reg conclusion holds); FNO resolves locality/F2 but the absolute F1
  gate stays bounded ~0.015. New content = the g64/g96 numbers; the finding was pre-registered.
- [x] **B0 (21, 3+1 law) — already documented 2026-06-12, NOT new:** the gate table (F1 0.041, F2 0.417, failed all
  gates) was written up in the lab_notebook on 2026-06-12 and is flagged CONFOUNDED there (3+1 changed kernels/channels/
  training-samples vs 2+1 all at once) -- so "locality worse in 3D" is NOT a valid clean claim (RETRACTED). Only the
  stale CLAUDE.md "Gates pending" status line was corrected 2026-06-26.
- [x] **E (Wong v4 fuller observability, script 135) DONE — honest negative (confounded):** K=4 four-field-probe model
  did NOT cross the 0.70 dynamic-legibility gate (min-r 0.295 ≤ K=1's 0.376); observability did not help at matched
  budget. |Q| exact (1.4e-7). CAVEAT: confounded (K=4 = 4× data at same steps, under-converged) -> not cleanly refuted;
  step-matched-per-field K=4 parked. Partial-observability hypothesis NOT supported at matched budget. (Rodrigues SO(3),
  ran on VM CPU.)
- [x] **C (global PINN Choptuik, script 136) DONE — honest partial:** plain-MLP global PINN reproduces the disperse/
  collapse DICHOTOMY (G2 ✓: subcritical max 2m/r 0.024 disperses, supercritical 0.977 collapses vs FD 0.980) with ZERO
  rollout -- the qualitative criticality the autoregressive emulator couldn't. BUT field accuracy poor (G1 ✗: relL2_Phi
  0.62) -- plain MLP, not the paper's ModPINN. Demonstrates the paradigm qualitatively (physics-in-loss > rollout),
  honestly scoped. (VM GPU.)
- [ ] D (G-sym + legibility reg) — not started (the user requested "Wong then PINN"; D not requested).
