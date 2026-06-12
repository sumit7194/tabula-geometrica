"""Step 14 — Phase D: the Kaluza–Klein migration (v1).

Kaluza 1921: the one number per body that electromagnetism costs IS
geometrizable — charged motion in d dimensions is free motion in d+1, with
q/m as conserved momentum around the extra dimension. Here: a shared,
identity-blind one-step dynamics F on an EXTENDED state (x, v, w), rolled out
recurrently; bodies differ only in a learned initial condition w0. If training
turns w0 into an internal coordinate whose value behaves as the body's charge,
the per-body identity has migrated from model parameters into STATE — the
Kaluza move, rediscovered by economy. Gates D1-D4 pre-registered in the lab
notebook.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import torch
from curvlib import RESULTS, TRAJ_TIMES, E_CENTER, integrate_trajectories, make_dynamics_dataset
from torch import nn

H = 0.1  # rollout step; targets at steps 10, 20, 30 (t = 1, 2, 3)
N_STEPS_ROLL = int(round(TRAJ_TIMES[-1] / H))
TARGET_STEPS = [int(round(t / H)) for t in TRAJ_TIMES]
STEPS = 12000


class KaluzaModel(nn.Module):
    """Shared residual one-step map on (x, v, w); per-body w0 enters as state."""

    def __init__(self, n_bodies: int):
        super().__init__()
        self.w0 = nn.Embedding(n_bodies, 1)
        self.F = nn.Sequential(
            nn.Linear(3, 128), nn.Tanh(), nn.Linear(128, 128), nn.Tanh(), nn.Linear(128, 3)
        )

    def rollout(self, x0, v0, w0):
        s = torch.stack([x0, v0, w0], dim=1)
        xs, ws = [], []
        for step in range(1, N_STEPS_ROLL + 1):
            s = s + H * self.F(s)
            if step in TARGET_STEPS:
                xs.append(s[:, 0])
            ws.append(s[:, 2])
        return torch.stack(xs, dim=1), torch.stack(ws, dim=1)

    def forward(self, X, body):
        return self.rollout(X[:, 0], X[:, 1], self.w0(body)[:, 0])[0]


def train(model, data, steps, seed):
    rng = np.random.default_rng(seed)
    body, X, Y = data["train"]
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)
    for step in range(steps):
        idx = rng.integers(0, len(X), 256)
        pred = model(torch.from_numpy(X[idx]), torch.from_numpy(body[idx]))
        loss = nn.functional.mse_loss(pred, torch.from_numpy(Y[idx]))
        opt.zero_grad()
        loss.backward()
        opt.step()
        if step % 500 == 0:
            from curvlib import progress

            progress("14_kaluza", step, steps, loss=loss.item())
            if step % 2000 == 0:
                print(f"  step {step:5d}  mse {loss.item():.6f}")
    return model


def mse_on(model, split):
    body, X, Y = split
    with torch.no_grad():
        pred = model(torch.from_numpy(X), torch.from_numpy(body))
        return float(nn.functional.mse_loss(pred, torch.from_numpy(Y)).item())


def behavioral_qm_of_w(model, w_values):
    """Effective q/m the trained F assigns to each internal-coordinate value,
    by inverting rolled-out trajectories against the true generator."""
    n_probe = 16
    px = np.linspace(E_CENTER - 0.8, E_CENTER + 0.8, n_probe).astype(np.float32)
    pv = np.zeros(n_probe, dtype=np.float32)
    qm_grid = np.linspace(-1.5, 1.5, 301)
    ref = np.stack(
        [integrate_trajectories(px.astype(float), pv.astype(float), np.full(n_probe, q))
         for q in qm_grid]
    )
    out = []
    with torch.no_grad():
        for w in w_values:
            xs, _ = model.rollout(
                torch.from_numpy(px), torch.from_numpy(pv),
                torch.full((n_probe,), float(w)),
            )
            mses = ((ref - xs.numpy()) ** 2).mean(axis=(1, 2))
            out.append(float(qm_grid[int(np.argmin(mses))]))
    return np.array(out)


def main() -> None:
    data = make_dynamics_dataset("charged", seed=0)
    n_bodies = len(data["qm_body"])
    qm_body = data["qm_body"]
    seen = np.setdiff1d(np.arange(n_bodies), np.array(data["held_bodies"]))

    torch.manual_seed(42)
    model = KaluzaModel(n_bodies)
    print("training the Kaluza model (shared F, per-body w0 as state):")
    train(model, data, STEPS, seed=0)
    model.eval()

    d1 = mse_on(model, data["test"])
    print(f"D1 test MSE: {d1:.2e}  (force-model d=1 reference: 7.9e-06; gate <= 1e-4)")

    # D2: behavioral decode of each body's learned w0
    w0 = model.w0.weight.data.numpy()[seen, 0]
    qm_eff = behavioral_qm_of_w(model, w0)
    r_mig = float(np.corrcoef(qm_eff, qm_body[seen])[0, 1])
    print(f"D2 behavioral decode of w0 vs true q/m: r = {r_mig:+.4f}  (gate |r| > 0.99)")

    # D3: does the learned F conserve the internal coordinate?
    body_t, X_t, _ = data["test"]
    with torch.no_grad():
        _, ws = model.rollout(
            torch.from_numpy(X_t[:2000, 0]), torch.from_numpy(X_t[:2000, 1]),
            model.w0(torch.from_numpy(body_t[:2000]))[:, 0],
        )
    drift = float(np.median(np.abs(ws[:, -1].numpy() - ws[:, 0].numpy())))
    spread = float(np.std(w0))
    print(f"D3 internal-coordinate drift |w(T)−w(0)| median = {drift:.4f} "
          f"vs w0 population spread = {spread:.4f}  (conserved if drift << spread)")

    # D4: zero-shot state estimation for held-out bodies — fit w0 (one scalar,
    # grid search) from the FIRST target point only, predict the rest
    body_h, X_h, Y_h = data["held"]
    w_grid = np.linspace(w0.min() - 1, w0.max() + 1, 201)
    errs = []
    with torch.no_grad():
        for b in np.unique(body_h):
            m = body_h == b
            Xb, Yb = X_h[m][:50], Y_h[m][:50]
            best_w, best_e = None, np.inf
            for w in w_grid:
                xs, _ = model.rollout(
                    torch.from_numpy(Xb[:, 0]), torch.from_numpy(Xb[:, 1]),
                    torch.full((len(Xb),), float(w)),
                )
                e1 = float(((xs[:, 0].numpy() - Yb[:, 0]) ** 2).mean())
                if e1 < best_e:
                    best_e, best_w = e1, w
            xs, _ = model.rollout(
                torch.from_numpy(Xb[:, 0]), torch.from_numpy(Xb[:, 1]),
                torch.full((len(Xb),), float(best_w)),
            )
            errs.append(((xs[:, 1:].numpy() - Yb[:, 1:]) ** 2).mean())
    d4 = float(np.mean(errs))
    print(f"D4 zero-shot (w0 from one point, no weight updates): "
          f"later-target MSE = {d4:.2e}  (in-training test: {d1:.2e})")

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    ch = np.abs(qm_body[seen]) > 1e-9
    lims = [qm_body[seen].min() - 0.15, qm_body[seen].max() + 0.15]
    axes[0].plot(lims, lims, "k--", lw=1)
    axes[0].scatter(qm_body[seen][~ch], qm_eff[~ch], c="steelblue", label="neutral")
    axes[0].scatter(qm_body[seen][ch], qm_eff[ch], c="crimson", label="charged")
    axes[0].set_xlabel("true q/m")
    axes[0].set_ylabel("q/m implied by the body's internal coordinate w0")
    axes[0].set_title(f"the Kaluza migration: charge as a position in an\n"
                      f"internal dimension of a SHARED geometry  (r = {r_mig:+.3f})")
    axes[0].legend()

    axes[1].scatter(qm_body[seen], w0, c=np.where(ch, "crimson", "steelblue"))
    axes[1].set_xlabel("true q/m")
    axes[1].set_ylabel("learned internal coordinate w0")
    axes[1].set_title(f"the raw internal coordinate\n(drift {drift:.3f} vs spread {spread:.3f})")
    fig.tight_layout()
    out = RESULTS / "14_kaluza.png"
    fig.savefig(out, dpi=140)
    print(f"plot -> {out}")

    (RESULTS / "14_kaluza.json").write_text(
        json.dumps({"D1_test_mse": d1, "D2_migration_r": r_mig,
                    "D3_drift": drift, "D3_spread": spread, "D4_zero_shot_mse": d4,
                    "w0": w0.tolist(), "qm_eff": qm_eff.tolist(),
                    "qm_true": qm_body[seen].tolist()}, indent=1)
    )


if __name__ == "__main__":
    main()
