"""Hail Mary — Experiment 1: does the modular DOSnet pipeline beat the monolithic soft-PINN on the constraint?

The core wall, isolated. Same predictor architecture, data, and budget for both; the only differences:
  BASELINE (monolith): trained with dynamics MSE + soft div-penalty; rolled out WITHOUT projection.
  PLAN A  (modular):   trained with dynamics MSE only; rolled out WITH the Leray projection each step.

Then autoregressively roll out far beyond the training horizon and watch the Gauss-law constraint. The NR claim
in miniature: the soft penalty lets |div E| drift and grow (error feeds back, the inspiral-detonation analogue),
while the projection holds it on the manifold by construction and keeps the field accurate longer.

Pre-reg (2026-06-20), grid 32, vacuum:
  G1 CONSTRAINT: over the long rollout, Plan A keeps max|div E| <= 1e-4 (float32 projection floor) while the
     baseline's grows to >= 100x Plan A's.
  G2 STABILITY/ACCURACY: at the long horizon, Plan A's field MSE <= the baseline's (staying on the manifold
     prevents the unphysical-mode error blowup).
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


def pairs(traj):
    """(T, S+1, 3, n, n) -> consecutive (state_t, state_{t+1}) flattened over trajectories and time."""
    a = traj[:, :-1].reshape(-1, *traj.shape[2:]); b = traj[:, 1:].reshape(-1, *traj.shape[2:])
    return torch.tensor(a), torch.tensor(b)


def train(mode, X, Y, KX, KY, K2safe, dev, steps, lam, seed=0):
    torch.manual_seed(seed); net = PredictorCNN().to(dev)
    opt = torch.optim.Adam(net.parameters(), lr=2e-3)
    rng = np.random.default_rng(seed)
    for st in range(steps):
        idx = rng.integers(0, len(X), 64); xb, yb = X[idx].to(dev), Y[idx].to(dev)
        pred = net(xb)
        loss = nn.functional.mse_loss(pred, yb)
        if mode == "baseline":                                # soft constraint penalty (the monolith's tool)
            d = div_E(pred[:, 0], pred[:, 1], KX, KY)
            loss = loss + lam * (d ** 2).mean()
        opt.zero_grad(); loss.backward(); opt.step()
    return net.eval()


@torch.no_grad()
def rollout(net, s0, horizon, project, KX, KY, K2safe, dev):
    s = s0.clone().to(dev); states = [s.clone()]
    for _ in range(horizon):
        s = net(s)
        if project:
            ex, ey = leray_project(s[:, 0], s[:, 1], KX, KY, K2safe)
            s = torch.stack([ex, ey, s[:, 2]], 1)
        states.append(s.clone())
    return torch.stack(states, 1)                             # (B, horizon+1, 3, n, n)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", default="mps" if torch.backends.mps.is_available() else ("cuda" if torch.cuda.is_available() else "cpu"))
    ap.add_argument("--grid", type=int, default=32)
    ap.add_argument("--traj", type=int, default=96)
    ap.add_argument("--train-steps", type=int, default=4000)
    ap.add_argument("--horizon", type=int, default=120)       # eval rollout (>> 40-step training trajectories)
    ap.add_argument("--lam", type=float, default=1.0)
    a = ap.parse_args(); dev = a.device
    print(f"device={dev} grid={a.grid} traj={a.traj} train_steps={a.train_steps} horizon={a.horizon} lam={a.lam}")

    tr, sim = make_dataset(n_traj=a.traj, nsteps=40, grid=a.grid, seed=0)
    X, Y = pairs(tr)
    KX, KY, K2safe = wavenumbers(a.grid, 2 * np.pi, dev)

    base = train("baseline", X, Y, KX, KY, K2safe, dev, a.train_steps, a.lam)
    plana = train("plana", X, Y, KX, KY, K2safe, dev, a.train_steps, a.lam)

    # held-out test initial states + ground-truth long rollout
    rng = np.random.default_rng(777)
    s0 = np.stack([sim.random_state(rng) for _ in range(16)]).astype(np.float32)
    truth = np.stack([sim.rollout(s0[i], a.horizon) for i in range(len(s0))]).astype(np.float32)  # (16,H+1,3,n,n); f32 for MPS
    truth_t = torch.tensor(truth).to(dev)
    s0_t = torch.tensor(s0).to(dev)

    rb = rollout(base, s0_t, a.horizon, False, KX, KY, K2safe, dev)
    ra = rollout(plana, s0_t, a.horizon, True, KX, KY, K2safe, dev)

    def curves(roll):
        dvals, mse = [], []
        for t in range(roll.shape[1]):
            d = div_E(roll[:, t, 0], roll[:, t, 1], KX, KY).abs().amax(dim=(-1, -2)).mean().item()
            m = ((roll[:, t] - truth_t[:, t]) ** 2).mean().item()
            dvals.append(d); mse.append(m)
        return np.array(dvals), np.array(mse)

    db, mb = curves(rb); da, ma = curves(ra)
    g1 = bool(da.max() <= 1e-4 and db[-1] >= 100 * da.max())
    g2 = bool(ma[-1] <= mb[-1])
    out = {"device": dev, "horizon": a.horizon, "lam": a.lam,
           "baseline_divE_final": float(db[-1]), "plana_divE_final": float(da[-1]), "plana_divE_max": float(da.max()),
           "baseline_mse_final": float(mb[-1]), "plana_mse_final": float(ma[-1]),
           "G1_constraint_held": g1, "G2_accuracy": g2, "modular_beats_monolith": bool(g1 and g2)}
    print(f"\nfinal |div E|:  baseline {db[-1]:.2e}   Plan A {da[-1]:.2e}  (Plan A max {da.max():.2e})")
    print(f"final field MSE: baseline {mb[-1]:.2e}   Plan A {ma[-1]:.2e}")
    print(f"G1 constraint held (Plan A <=1e-4, baseline >=100x): {g1}")
    print(f"G2 Plan A accuracy <= baseline at long horizon: {g2}")
    print(f"\nMODULAR (predict+project) BEATS MONOLITH (soft penalty): {out['modular_beats_monolith']}")
    res = Path(__file__).resolve().parent / "results"; res.mkdir(exist_ok=True)
    (res / "exp1_constraint.json").write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(1, 2, figsize=(13, 5)); t = np.arange(a.horizon + 1)
    ax[0].semilogy(t, db + 1e-12, color="navy", label="baseline (soft penalty)")
    ax[0].semilogy(t, da + 1e-12, color="crimson", label="Plan A (predict + project)")
    ax[0].axvline(40, color="gray", ls=":", lw=0.8, label="training horizon")
    ax[0].set_xlabel("rollout step"); ax[0].set_ylabel("max |div E| (constraint violation)")
    ax[0].legend(fontsize=8); ax[0].set_title("Constraint: soft penalty drifts, projection holds it on the manifold")
    ax[1].semilogy(t, mb + 1e-12, color="navy", label="baseline")
    ax[1].semilogy(t, ma + 1e-12, color="crimson", label="Plan A")
    ax[1].axvline(40, color="gray", ls=":", lw=0.8)
    ax[1].set_xlabel("rollout step"); ax[1].set_ylabel("field MSE vs ground truth")
    ax[1].legend(fontsize=8); ax[1].set_title("Accuracy over a long rollout (beyond the training horizon)")
    fig.tight_layout(); fig.savefig(res / "exp1_constraint.png", dpi=140)
    print(f"saved hailmary/results/exp1_constraint.json + .png")


if __name__ == "__main__":
    main()
