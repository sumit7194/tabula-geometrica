"""Hail Mary — Experiment 7 (final Phase-1 hardening): does the recipe survive SCALE?

The modular recipe (project for the constraint + push-forward for stability) passed at grid 32, horizon 100.
Last hardening before advancing: push it to a BIGGER grid (48) and a MUCH LONGER rollout (500 steps -- 5x the
test horizon, 12.5x the 40-step training trajectories). The questions:
  H1 does the constraint stay held by projection at higher resolution + long horizon?
  H2 does push-forward stability hold over 5x the horizon, or does autoregressive error eventually blow up?

Plan A only (the validated recipe): PredictorCNN, push-forward trained, projected every step. 3 seeds. We record
the constraint and field-MSE curves across the full 500-step rollout (not just endpoints).

Pre-reg (2026-06-20), grid 48, vacuum, horizon 500, 3 seeds:
  H1 CONSTRAINT AT SCALE: max|div E| <= 1e-4 over the full rollout, every seed (by construction).
  H2 STABILITY AT SCALE: field MSE stays bounded (no divergence) to 500 steps, every seed (final MSE < 0.05),
     i.e. the recipe extrapolates 5x beyond its test horizon without blowing up.
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

from maxwell import make_dataset
from modules import PredictorCNN, div_E, leray_project, wavenumbers


def project(s, KX, KY, K2safe):
    ex, ey = leray_project(s[:, 0], s[:, 1], KX, KY, K2safe)
    return torch.stack([ex, ey, s[:, 2]], 1)


def train_pf(tr, K, steps, KX, KY, K2safe, dev, seed):
    T, S = tr.shape[0], tr.shape[1] - 1
    torch.manual_seed(seed); net = PredictorCNN().to(dev); opt = torch.optim.Adam(net.parameters(), lr=2e-3)
    rng = np.random.default_rng(seed); trd = torch.tensor(tr).to(dev)
    for st in range(steps):
        j = int(rng.integers(0, K)); ti = rng.integers(0, T, 32); t0 = rng.integers(0, S - j, 32)
        s = trd[ti, t0]
        if j > 0:
            with torch.no_grad():
                for _ in range(j):
                    s = project(net(s), KX, KY, K2safe)
        loss = nn.functional.mse_loss(project(net(s), KX, KY, K2safe), trd[ti, t0 + j + 1])
        opt.zero_grad(); loss.backward(); torch.nn.utils.clip_grad_norm_(net.parameters(), 1.0); opt.step()
    return net.eval()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", default="mps" if torch.backends.mps.is_available() else ("cuda" if torch.cuda.is_available() else "cpu"))
    ap.add_argument("--grid", type=int, default=48); ap.add_argument("--traj", type=int, default=96)
    ap.add_argument("--K", type=int, default=4); ap.add_argument("--steps", type=int, default=2500)
    ap.add_argument("--horizon", type=int, default=500); ap.add_argument("--nseeds", type=int, default=3)
    ap.add_argument("--chk", type=int, default=25)
    a = ap.parse_args(); dev = a.device
    KX, KY, K2safe = wavenumbers(a.grid, 2 * np.pi, dev)
    res = Path(__file__).resolve().parent / "results"; res.mkdir(exist_ok=True)
    print(f"device={dev} grid={a.grid} K={a.K} steps={a.steps} horizon={a.horizon} nseeds={a.nseeds}")

    div_curves, mse_curves, final_div, final_mse = [], [], [], []
    for seed in range(a.nseeds):
        tr, sim = make_dataset(n_traj=a.traj, nsteps=40, grid=a.grid, seed=seed)
        net = train_pf(tr, a.K, a.steps, KX, KY, K2safe, dev, seed)
        rng = np.random.default_rng(777 + seed)
        s0 = np.stack([sim.random_state(rng) for _ in range(16)]).astype(np.float32)
        truth = np.stack([sim.rollout(s0[i], a.horizon) for i in range(len(s0))]).astype(np.float32)
        truth_t = torch.tensor(truth).to(dev)
        with torch.no_grad():
            s = torch.tensor(s0).to(dev); dvs, mss, steps_ax = [], [], []
            for t in range(1, a.horizon + 1):
                s = project(net(s), KX, KY, K2safe)
                if t % a.chk == 0:
                    dvs.append(div_E(s[:, 0], s[:, 1], KX, KY).abs().amax(dim=(-1, -2)).mean().item())
                    mss.append(((s - truth_t[:, t]) ** 2).mean().item()); steps_ax.append(t)
        div_curves.append(dvs); mse_curves.append(mss); final_div.append(dvs[-1]); final_mse.append(mss[-1])
        print(f"seed {seed}: @500 |div E| {dvs[-1]:.2e}  field MSE {mss[-1]:.2e}  (max div over rollout {max(dvs):.2e}, max mse {max(mss):.2e})")

    fd, fm = np.array(final_div), np.array(final_mse)
    maxdiv = max(max(c) for c in div_curves); maxmse = max(max(c) for c in mse_curves)
    h1 = bool(maxdiv <= 1e-4)
    h2 = bool(fm.max() < 0.05 and maxmse < 0.05)
    out = {"device": dev, "grid": a.grid, "horizon": a.horizon, "steps_axis": steps_ax,
           "div_curves": div_curves, "mse_curves": mse_curves, "final_div": final_div, "final_mse": final_mse,
           "max_div_over_rollout": maxdiv, "max_mse_over_rollout": maxmse,
           "H1_constraint_at_scale": h1, "H2_stability_at_scale": h2, "recipe_survives_scale": bool(h1 and h2)}
    print(f"\nH1 constraint held at grid {a.grid} over {a.horizon} steps (max |div E| {maxdiv:.1e} <= 1e-4): {h1}")
    print(f"H2 stable at scale (max field MSE {maxmse:.2e} < 0.05, no divergence): {h2}")
    print(f"\nRECIPE SURVIVES SCALE (grid {a.grid}, {a.horizon}-step rollout, push-forward + projection): {out['recipe_survives_scale']}")
    (res / "exp7_scale.json").write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(1, 2, figsize=(13, 5))
    for seed in range(a.nseeds):
        ax[0].semilogy(steps_ax, np.clip(div_curves[seed], 1e-9, None), label=f"seed {seed}")
        ax[1].semilogy(steps_ax, np.clip(mse_curves[seed], 1e-9, None), label=f"seed {seed}")
    ax[0].axhline(1e-4, color="k", ls=":", lw=0.8); ax[0].set_xlabel("rollout step"); ax[0].set_ylabel("max |div E|")
    ax[0].legend(fontsize=8); ax[0].set_title(f"Constraint over a {a.horizon}-step rollout (grid {a.grid})\nheld by projection, by construction")
    ax[1].axhline(0.05, color="k", ls=":", lw=0.8); ax[1].set_xlabel("rollout step"); ax[1].set_ylabel("field MSE vs truth")
    ax[1].legend(fontsize=8); ax[1].set_title(f"Stability over {a.horizon} steps (5x the test horizon)\ndoes push-forward extrapolate without blowing up?")
    fig.tight_layout(); fig.savefig(res / "exp7_scale.png", dpi=140)
    print("saved hailmary/results/exp7_scale.json + .png")


if __name__ == "__main__":
    main()
