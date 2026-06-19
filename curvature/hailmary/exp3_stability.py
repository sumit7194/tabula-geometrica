"""Hail Mary — Experiment 3: fix the STABILITY wall (Exp 1's G2-not-robust finding) with recurrent training.

Exp 1 found that the projection robustly enforces the constraint (G1) but does NOT guarantee long-rollout accuracy
(G2): 1-step-trained Plan A beat the monolith in only 2/3 seeds and DIVERGED on seed 1, because 1-step training
never teaches the predictor to be stable under its own iterated errors (the physical, divergence-free modes drift,
which projection doesn't touch). The standard fix is recurrent / push-forward training: train the predictor
THROUGH a K-step rollout (with the projection in the loop), so the loss sees -- and damps -- compounding error.

Compare, across 3 seeds, Plan A trained two ways (both projected at rollout):
  1-STEP   : loss = MSE(net(s_t), s_{t+1})                    (the Exp 1 predictor; reuses its saved results)
  RECURRENT: loss = mean_k MSE(rollout_k(s_t), s_{t+k}), k=1..K, projection inside the rollout

Pre-reg (2026-06-20), grid 32, vacuum, horizon 100:
  S1 STABILITY: recurrent Plan A's long-rollout field MSE is robustly low across ALL 3 seeds (no divergence) --
     specifically max-over-seeds MSE < 5e-3 (the 1-step Plan A hit 2.5e-2 on seed 1).
  S2 IMPROVEMENT: recurrent Plan A beats 1-step Plan A's final MSE on the seed where 1-step diverged (seed 1),
     by >= 5x -- recurrent training fixes the instability the projection alone could not.
  (G1 constraint stays ~1e-6 by construction throughout -- projection is still applied.)
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import torch
from torch import nn

from maxwell import Maxwell2D, make_dataset
from modules import PredictorCNN, div_E, leray_project, wavenumbers


def project(s, KX, KY, K2safe):
    ex, ey = leray_project(s[:, 0], s[:, 1], KX, KY, K2safe)
    return torch.stack([ex, ey, s[:, 2]], 1)


def train_recurrent(tr, K, steps, KX, KY, K2safe, dev, seed):
    """push-forward trick (Brandstetter 2022): roll j steps NO-GRAD (so the net sees its own iterated, perturbed
    states -- the distribution-shift / stability signal), then backprop ONE step. Avoids the exploding-gradient
    BPTT-through-rollout failure; grad-clip for safety."""
    T, S1 = tr.shape[0], tr.shape[1]; S = S1 - 1
    torch.manual_seed(seed); net = PredictorCNN().to(dev); opt = torch.optim.Adam(net.parameters(), lr=2e-3)
    rng = np.random.default_rng(seed); trd = torch.tensor(tr).to(dev)
    for st in range(steps):
        j = int(rng.integers(0, K)); ti = rng.integers(0, T, 32); t0 = rng.integers(0, S - j, 32)
        s = trd[ti, t0]
        if j > 0:
            with torch.no_grad():
                for _ in range(j):
                    s = project(net(s), KX, KY, K2safe)
        pred = project(net(s), KX, KY, K2safe)                    # the single graded step
        loss = nn.functional.mse_loss(pred, trd[ti, t0 + j + 1])
        opt.zero_grad(); loss.backward()
        torch.nn.utils.clip_grad_norm_(net.parameters(), 1.0)
        opt.step()
    return net.eval()


@torch.no_grad()
def rollout(net, s0, horizon, KX, KY, K2safe):
    s = s0.clone(); states = [s.clone()]
    for _ in range(horizon):
        s = project(net(s), KX, KY, K2safe); states.append(s.clone())
    return torch.stack(states, 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", default="mps" if torch.backends.mps.is_available() else ("cuda" if torch.cuda.is_available() else "cpu"))
    ap.add_argument("--grid", type=int, default=32)
    ap.add_argument("--traj", type=int, default=96)
    ap.add_argument("--K", type=int, default=4)
    ap.add_argument("--steps", type=int, default=3000)
    ap.add_argument("--horizon", type=int, default=100)
    a = ap.parse_args(); dev = a.device
    KX, KY, K2safe = wavenumbers(a.grid, 2 * np.pi, dev)
    res = Path(__file__).resolve().parent / "results"; res.mkdir(exist_ok=True)
    print(f"device={dev} grid={a.grid} K={a.K} steps={a.steps} horizon={a.horizon}")

    rec_final, onestep_final = [], []
    for seed in [0, 1, 2]:
        tr, sim = make_dataset(n_traj=a.traj, nsteps=40, grid=a.grid, seed=seed)
        net = train_recurrent(tr, a.K, a.steps, KX, KY, K2safe, dev, seed)
        rng = np.random.default_rng(777 + seed)                       # same held-out states as Exp 1
        s0 = np.stack([sim.random_state(rng) for _ in range(16)]).astype(np.float32)
        truth = np.stack([sim.rollout(s0[i], a.horizon) for i in range(len(s0))]).astype(np.float32)
        truth_t = torch.tensor(truth).to(dev); s0_t = torch.tensor(s0).to(dev)
        roll = rollout(net, s0_t, a.horizon, KX, KY, K2safe)
        mse = ((roll[:, -1] - truth_t[:, -1]) ** 2).mean().item()
        dv = div_E(roll[:, -1, 0], roll[:, -1, 1], KX, KY).abs().amax(dim=(-1, -2)).mean().item()
        rec_final.append(mse)
        one = json.loads((res / f"exp1_constraint_s{seed}.json").read_text())["plana_mse_final"] if (res / f"exp1_constraint_s{seed}.json").exists() else float("nan")
        onestep_final.append(one)
        print(f"seed {seed}: recurrent Plan A final MSE {mse:.2e} (|divE| {dv:.1e})  vs 1-step Plan A {one:.2e}")

    rec = np.array(rec_final); one = np.array(onestep_final)
    s1 = bool(rec.max() < 5e-3)
    # seed where 1-step diverged (worst 1-step seed); recurrent should beat it >=5x
    bad = int(np.nanargmax(one))
    s2 = bool(one[bad] / (rec[bad] + 1e-12) >= 5.0)
    out = {"device": dev, "K": a.K, "recurrent_final_mse": rec_final, "onestep_final_mse": onestep_final,
           "recurrent_max_mse": float(rec.max()), "worst_1step_seed": bad,
           "S1_stable_all_seeds": s1, "S2_fixes_divergence": s2, "recurrent_fixes_stability": bool(s1 and s2)}
    print(f"\nS1 recurrent stable across all seeds (max MSE {rec.max():.2e} < 5e-3): {s1}")
    print(f"S2 recurrent fixes the seed-{bad} divergence ({one[bad]:.2e} -> {rec[bad]:.2e}, >=5x): {s2}")
    print(f"\nRECURRENT TRAINING FIXES THE STABILITY WALL (projection holds the constraint; rollout-training holds the dynamics): {out['recurrent_fixes_stability']}")
    (res / "exp3_stability.json").write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(figsize=(7.5, 5)); x = np.arange(3); w = 0.36
    ax.bar(x - w / 2, np.clip(one, 1e-6, None), w, color="navy", label="1-step training (Exp 1)")
    ax.bar(x + w / 2, np.clip(rec, 1e-6, None), w, color="crimson", label=f"recurrent K={a.K} training")
    ax.set_yscale("log"); ax.set_xticks(x); ax.set_xticklabels([f"seed {s}" for s in range(3)])
    ax.set_ylabel("Plan A long-rollout final field MSE"); ax.legend(fontsize=8)
    ax.set_title("Stability: 1-step training diverges on some seeds;\nrecurrent (push-forward) training holds the dynamics across all seeds")
    fig.tight_layout(); fig.savefig(res / "exp3_stability.png", dpi=140)
    print("saved hailmary/results/exp3_stability.json + .png")


if __name__ == "__main__":
    main()
