"""Hail Mary — Experiment 4b: Plan B done the PROPER way (the Coconut / Cache-to-Cache recipe we never ran).

Exp 4 trained the wide-stream two-stage net END-TO-END FROM SCRATCH and found it high-variance -- but that is NOT
the latent-communication recipe. Coconut bootstraps from a working DISCRETE (narrow, interpretable) interface and
only THEN relaxes to a latent stream, continuing to train jointly. The bet from the literature is that the stream
only carries useful structure if it is grown out of an already-working clean pipeline (gradients crossing a seam
that already means something), not learned cold.

Proper recipe here (same total training budget for every arm, fair):
  1. PRETRAIN a clean pipeline with a NARROW b=3 physical-state interface (the "discrete CoT" analog).
  2. RELAX: widen the interface to a b=32 latent stream, initialized so the function is PRESERVED exactly (stage2
     ignores the new channels at init), then FINE-TUNE jointly so the stream channels can grow to carry residual info.
Arms (all see steps_pre + steps_joint steps):
  clean        : b=3 the whole way (pretrain + continue).
  clean_wide   : b=3 but internal ch widened to capacity-match the stream (the honest capacity control).
  stream_scratch: b=32 from scratch for the full budget (= the original Exp 4).
  stream_proper : b=3 pretrain -> widen to b=32 -> joint fine-tune (THE recipe).

Pre-reg (2026-06-20), grid 32, vacuum, horizon 100, 3 seeds:
  B1 RECIPE BEATS CLEAN: stream_proper mean long-rollout MSE < clean_wide mean (capacity-matched) -- the latent
     stream, grown properly, actually lowers the splitting error.
  B2 RECIPE MATTERS: stream_proper mean < stream_scratch mean AND stream_proper's worst seed <= clean_wide's worst
     (the bootstrap fixes the from-scratch instability Exp 4 saw).
"""

import argparse
import copy
import json
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
sys.path.insert(0, str(Path(__file__).resolve().parent))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import torch

from maxwell import make_dataset
from modules import wavenumbers
from exp4_residual_stream import TwoStage, rollout_mse, train_pf


def widen(net3, b, ch=48, scale=0.01):
    """grow the clean b=3 interface to a b-channel latent stream, PRESERVING the function at init.

    stage1's last conv gains extra output channels (small random); stage2's first conv zeros the matching extra
    input channels, so at init the stream is ignored and the net == the pretrained clean net exactly. Joint
    fine-tuning then lets stage2 grow connections into the stream.
    """
    big = TwoStage(b, ch=ch)
    big.s1[0].load_state_dict(net3.s1[0].state_dict())
    big.s1[2].load_state_dict(net3.s1[2].state_dict())
    with torch.no_grad():
        big.s1[4].weight.zero_(); big.s1[4].weight[:3] = net3.s1[4].weight
        big.s1[4].weight[3:] = scale * torch.randn_like(big.s1[4].weight[3:])
        big.s1[4].bias.zero_(); big.s1[4].bias[:3] = net3.s1[4].bias
        big.s2[0].weight.zero_(); big.s2[0].weight[:, :3] = net3.s2[0].weight   # extra inputs = 0 -> ignored at init
        big.s2[0].bias.copy_(net3.s2[0].bias)
    big.s2[2].load_state_dict(net3.s2[2].state_dict())
    big.s2[4].load_state_dict(net3.s2[4].state_dict())
    return big


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", default="mps" if torch.backends.mps.is_available() else ("cuda" if torch.cuda.is_available() else "cpu"))
    ap.add_argument("--grid", type=int, default=32); ap.add_argument("--traj", type=int, default=96)
    ap.add_argument("--K", type=int, default=4); ap.add_argument("--pre", type=int, default=1500); ap.add_argument("--joint", type=int, default=1500)
    ap.add_argument("--horizon", type=int, default=100); ap.add_argument("--stream", type=int, default=32)
    ap.add_argument("--cw", type=int, default=60); ap.add_argument("--nseeds", type=int, default=3)
    a = ap.parse_args(); dev = a.device
    KX, KY, K2safe = wavenumbers(a.grid, 2 * np.pi, dev)
    res = Path(__file__).resolve().parent / "results"; res.mkdir(exist_ok=True)
    P = {"clean": sum(p.numel() for p in TwoStage(3).parameters()),
         "clean_wide": sum(p.numel() for p in TwoStage(3, ch=a.cw).parameters()),
         "stream": sum(p.numel() for p in TwoStage(a.stream).parameters())}
    print(f"device={dev} grid={a.grid} pre={a.pre} joint={a.joint} | params {P}")

    arms = ["clean", "clean_wide", "stream_scratch", "stream_proper"]
    M = {k: [] for k in arms}
    for seed in range(a.nseeds):
        tr, sim = make_dataset(n_traj=a.traj, nsteps=40, grid=a.grid, seed=seed)
        rng = np.random.default_rng(777 + seed)
        s0 = np.stack([sim.random_state(rng) for _ in range(16)]).astype(np.float32)
        truth = np.stack([sim.rollout(s0[i], a.horizon) for i in range(len(s0))]).astype(np.float32)
        truth_t = torch.tensor(truth).to(dev); s0_t = torch.tensor(s0).to(dev)
        tp = lambda net, steps, sd: train_pf(net.to(dev), tr, a.K, steps, KX, KY, K2safe, dev, sd)
        fit = lambda net: rollout_mse(net, s0_t, truth_t, a.horizon, KX, KY, K2safe)

        # pretrain the clean b=3 pipeline once; every arm branches from a fair starting point / same budget
        torch.manual_seed(seed); base = TwoStage(3)
        tp(base, a.pre, seed)

        m_clean = fit(tp(copy.deepcopy(base), a.joint, seed))                       # clean: continue b=3
        torch.manual_seed(seed); cw = TwoStage(3, ch=a.cw); m_cw = fit(tp(cw, a.pre + a.joint, seed))   # capacity control, full budget
        torch.manual_seed(seed); ss = TwoStage(a.stream); m_ss = fit(tp(ss, a.pre + a.joint, seed))      # stream from scratch (= Exp 4)
        sp = widen(copy.deepcopy(base), a.stream); m_sp = fit(tp(sp, a.joint, seed))                      # PROPER: pretrain->widen->joint

        for k, v in zip(arms, [m_clean, m_cw, m_ss, m_sp]):
            M[k].append(v)
        print(f"seed {seed}: clean {m_clean:.2e}  clean_wide {m_cw:.2e}  stream_scratch {m_ss:.2e}  stream_proper {m_sp:.2e}  "
              f"| proper/clean_wide {m_sp/m_cw:.2f}  proper/scratch {m_sp/m_ss:.2f}")

    A = {k: np.array(v) for k, v in M.items()}
    b1 = bool(A["stream_proper"].mean() < A["clean_wide"].mean())
    b2 = bool(A["stream_proper"].mean() < A["stream_scratch"].mean() and A["stream_proper"].max() <= A["clean_wide"].max())
    out = {"device": dev, "params": P, "means": {k: float(A[k].mean()) for k in arms}, "per_seed": {k: M[k] for k in arms},
           "proper_over_cleanwide": float(A["stream_proper"].mean() / A["clean_wide"].mean()),
           "proper_over_scratch": float(A["stream_proper"].mean() / A["stream_scratch"].mean()),
           "B1_recipe_beats_clean": b1, "B2_recipe_matters_and_stable": b2, "proper_recipe_unlocks_stream": bool(b1 and b2)}
    print(f"\nmeans: " + "  ".join(f"{k} {A[k].mean():.2e}" for k in arms))
    print(f"B1 stream_proper beats capacity-matched clean: {b1}  (proper/clean_wide {out['proper_over_cleanwide']:.2f})")
    print(f"B2 recipe beats from-scratch + stable: {b2}  (proper/scratch {out['proper_over_scratch']:.2f})")
    print(f"\nPROPER RECIPE (pretrain->relax->joint) UNLOCKS THE RESIDUAL STREAM: {out['proper_recipe_unlocks_stream']}")
    (res / "exp4b_residual_stream_proper.json").write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(figsize=(9, 5)); x = np.arange(a.nseeds); w = 0.2
    colors = {"clean": "silver", "clean_wide": "navy", "stream_scratch": "darkorange", "stream_proper": "crimson"}
    for i, k in enumerate(arms):
        ax.bar(x + (i - 1.5) * w, np.clip(A[k], 1e-6, None), w, color=colors[k], label=k)
    ax.set_yscale("log"); ax.set_xticks(x); ax.set_xticklabels([f"s{i}" for i in range(a.nseeds)])
    ax.set_ylabel("long-rollout final field MSE"); ax.legend(fontsize=8)
    ax.set_title(f"Plan B proper recipe: pretrain->relax->joint vs from-scratch vs clean\nproper/clean_wide={out['proper_over_cleanwide']:.2f}  proper/scratch={out['proper_over_scratch']:.2f}")
    fig.tight_layout(); fig.savefig(res / "exp4b_residual_stream_proper.png", dpi=140)
    print("saved hailmary/results/exp4b_residual_stream_proper.json + .png")


if __name__ == "__main__":
    main()
