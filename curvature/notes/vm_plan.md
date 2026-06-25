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

### A (headline) — Phase F law via FNO: crack the 1/r long-range wall
- **Why GPU:** the documented Phase-F wall — a local CNN provably can't represent the 1/r long-range tail (overfit-
  one-batch failed at 0.047; Proca 53 isolated locality as the knob). A **Fourier Neural Operator** (global spectral
  conv) CAN represent long-range/global kernels (FNO-class result). Training FNOs over fields, many epochs = GPU.
- **Build:** new script (127) — FNO mapping matter density -> acceleration field, differentiable rollout, trajectories-
  only (same task as 19/22). 2D first, then 3D. Oracle discretization floor banked (1.2e-4) -> the gate IS feasible.
- **Pre-reg gates (from fv2_roadmap):** F1 traj MSE <= ~1e-3 (vs CNN 0.058); F2 field cos > 0.98 (vs CNN 0.937);
  F3 superposition cos > 0.96 on unseen multi-blob; F4 blind/identity-removal control >= 10x. PLUS the methodology:
  oracle floor first, 3-pt LR sweep, diagnostic trio (overfit-one-batch, RF sweep), THEN the FNO.
- **Value:** the biggest scientific payoff — turning a documented NULL (Phase F) into a positive by the literature-
  identified fix (global operator). Honest either way (if FNO also misses, that's a sharper FNO-class statement).

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
B0 (finish 21, shovel-ready) -> A (FNO, the headline wall) -> C (global PINN) -> D (G-sym) -> E (Wong). A is the
highest-value; B0 is the fastest. Methodology-heavy (LR sweeps x seeds) applies throughout — the GPU's other win.

## PRE-BUILD LOCALLY (while the VM spins up)
- Write + CPU-smoke-test the FNO script (127) and a CUDA device path, so it's launch-ready on the VM.
- Confirm 21's --device cuda path + gates are wired.
- A tiny `vm_setup.sh` (clone + venv + cuda-torch + sanity) to paste on the VM.

## STATUS
- [ ] VM spun up + GPU verified free
- [ ] B0 (21) · [ ] A (FNO 127) · [ ] C (PINN) · [ ] D (G-sym) · [ ] E (Wong)
