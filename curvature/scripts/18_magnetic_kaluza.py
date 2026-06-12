"""Step 18 — D-3: the MAGNETIC Kaluza. Velocity-dependent forces (q/m · v×B)
from an internal coordinate: in real KK theory the magnetic force IS the
Coriolis force of the hidden dimension. D-v1's proven recurrent machinery,
extended state (x, y, vx, vy, w); w-less control must fail on charged bodies.
Pre-registration M1-M4 in the lab notebook (2026-06-13, "PHASE D-3").
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
from curvlib import RESULTS, TRAJ_TIMES, B_CENTER, integrate_2d, make_magnetic_dataset, progress
from torch import nn

H = 0.1
N_ROLL = int(round(TRAJ_TIMES[-1] / H))
TARGETS = [int(round(t / H)) for t in TRAJ_TIMES]
STEPS = 12000


class MagneticKaluza(nn.Module):
    def __init__(self, n_bodies: int, use_w: bool = True):
        super().__init__()
        self.use_w = use_w
        if use_w:
            self.w0 = nn.Embedding(n_bodies, 1)
        d = 5 if use_w else 4
        self.F = nn.Sequential(
            nn.Linear(d, 128), nn.Tanh(), nn.Linear(128, 128), nn.Tanh(), nn.Linear(128, d)
        )

    def rollout(self, X, w0=None):
        s = torch.cat([X, w0[:, None]], dim=1) if self.use_w else X
        xs = []
        for step in range(1, N_ROLL + 1):
            s = s + H * self.F(s)
            if step in TARGETS:
                xs.append(s[:, :2])
        return torch.cat(xs, dim=1)

    def forward(self, X, body):
        w0 = self.w0(body)[:, 0] if self.use_w else None
        return self.rollout(X, w0)


def train(model, data, seed=0):
    torch.manual_seed(seed + (18 if model.use_w else 180))
    rng = np.random.default_rng(seed)
    body, X, Y = data["train"]
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)
    tag = "18_mag" + ("" if model.use_w else "_ctrl")
    for step in range(STEPS):
        idx = rng.integers(0, len(X), 256)
        loss = nn.functional.mse_loss(
            model(torch.from_numpy(X[idx]), torch.from_numpy(body[idx])),
            torch.from_numpy(Y[idx]))
        opt.zero_grad()
        loss.backward()
        opt.step()
        if step % 500 == 0:
            progress(tag, step, STEPS, loss=loss.item())
    return model


def mse_by_class(model, split, qm_body):
    body, X, Y = split
    with torch.no_grad():
        err = ((model(torch.from_numpy(X), torch.from_numpy(body))
                - torch.from_numpy(Y)) ** 2).mean(1).numpy()
    ch = np.abs(qm_body[body]) > 1e-9
    return {"all": float(err.mean()), "charged": float(err[ch].mean()),
            "neutral": float(err[~ch].mean())}


def behavioral_qm(model, w_vals):
    n = 16
    px = np.linspace(B_CENTER[0] - 0.8, B_CENTER[0] + 0.8, n).astype(np.float32)
    py = np.full(n, B_CENTER[1], dtype=np.float32)
    vx = np.full(n, 0.25, dtype=np.float32)  # magnetic force needs velocity
    vy = np.zeros(n, dtype=np.float32)
    X = torch.from_numpy(np.stack([px, py, vx, vy], 1))
    grid = np.linspace(-1.5, 1.5, 301)
    ref = np.stack([integrate_2d(px.astype(float), py.astype(float),
                                 vx.astype(float), vy.astype(float),
                                 np.full(n, q)).reshape(n, -1) for q in grid])
    out = []
    with torch.no_grad():
        for w in w_vals:
            pred = model.rollout(X, torch.full((n,), float(w))).numpy()
            out.append(float(grid[int(np.argmin(((ref - pred) ** 2).mean((1, 2))))]))
    return np.array(out)


def main() -> None:
    data = make_magnetic_dataset(seed=0)
    qm = data["qm_body"]
    n_bodies = len(qm)
    seen = np.setdiff1d(np.arange(n_bodies), np.array(data["held_bodies"]))

    print("training w-less control:")
    ctrl = train(MagneticKaluza(n_bodies, use_w=False), data)
    print("training magnetic Kaluza model:")
    model = train(MagneticKaluza(n_bodies, use_w=True), data)
    ctrl.eval(), model.eval()

    m1c = mse_by_class(ctrl, data["test"], qm)
    m1 = mse_by_class(model, data["test"], qm)
    print(f"M1 control (no w): {m1c}")
    print(f"M1 Kaluza:         {m1}   (gate: all <= 1e-4, control charged >> )")

    w0 = model.w0.weight.data.numpy()[seen, 0]
    qm_eff = behavioral_qm(model, w0)
    r = float(np.corrcoef(qm_eff, qm[seen])[0, 1])
    print(f"M2 behavioral decode w0 -> q/m: r = {r:+.4f}  (gate |r| > 0.99)")

    (RESULTS / "18_magnetic.json").write_text(json.dumps(
        {"M1_kaluza": m1, "M1_control": m1c, "M2_r": r,
         "w0": w0.tolist(), "qm_eff": qm_eff.tolist(), "qm_true": qm[seen].tolist()},
        indent=1))

    fig, ax = plt.subplots(figsize=(7, 5.5))
    ch = np.abs(qm[seen]) > 1e-9
    lims = [qm[seen].min() - 0.15, qm[seen].max() + 0.15]
    ax.plot(lims, lims, "k--", lw=1)
    ax.scatter(qm[seen][~ch], qm_eff[~ch], c="steelblue", label="neutral")
    ax.scatter(qm[seen][ch], qm_eff[ch], c="crimson", label="charged")
    ax.set_xlabel("true q/m")
    ax.set_ylabel("q/m decoded from the internal coordinate")
    ax.set_title(f"the MAGNETIC Kaluza: v×B forces from a hidden dimension\n"
                 f"behavioral decode r = {r:+.3f}")
    ax.legend()
    fig.tight_layout()
    fig.savefig(RESULTS / "18_magnetic_kaluza.png", dpi=140)
    print(f"plot -> {RESULTS / '18_magnetic_kaluza.png'}")


if __name__ == "__main__":
    main()
