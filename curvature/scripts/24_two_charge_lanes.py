"""Step 24 — Phase H row 1: TWO charges — how many hidden lanes?

Bodies carry two independent labels (qm1, qm2) coupling to two separate field
bumps. The model gets L internal lanes (extended state); sweep L in {0,1,2,3}.
The question: does the practical lane-count knee land at 2 — and do the two
lanes decode to the two labels (up to mixing)? Pre-registration H1-H4 in the
lab notebook (2026-06-14). Detached + bit-exact checkpoints.
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
from curvlib import (
    RESULTS,
    TRAJ_TIMES,
    V_MAX,
    X_RANGE,
    WELL_DEPTH,
    WELL_WIDTH,
    load_ckpt,
    progress,
    save_ckpt,
)
from torch import nn

H = 0.1
N_ROLL = int(round(TRAJ_TIMES[-1] / H))
TARGETS = [int(round(t / H)) for t in TRAJ_TIMES]
STEPS = 12000
LANES = (0, 1, 2, 3)

E1 = dict(amp=0.3, c=0.8, w=1.0)
E2 = dict(amp=0.35, c=-1.2, w=1.0)


def field(x, p):
    return p["amp"] * np.exp(-((x - p["c"]) ** 2) / (2 * p["w"] ** 2))


def accel(x, qm1, qm2):
    # gravity (attractive well) + two independent label-coupled fields
    e = np.exp(-(x**2) / (2 * WELL_WIDTH**2))
    a_grav = -WELL_DEPTH * x * e / WELL_WIDTH**2
    return a_grav + qm1 * field(x, E1) + qm2 * field(x, E2)


def integrate(x0, v0, qm1, qm2, dt=0.01):
    n_steps = int(round(TRAJ_TIMES[-1] / dt))
    grab = {int(round(t / dt)): i for i, t in enumerate(TRAJ_TIMES)}
    x, v = x0.astype(float).copy(), v0.astype(float).copy()
    out = np.empty((len(x0), len(TRAJ_TIMES)))
    for step in range(1, n_steps + 1):
        k1x, k1v = v, accel(x, qm1, qm2)
        k2x, k2v = v + 0.5 * dt * k1v, accel(x + 0.5 * dt * k1x, qm1, qm2)
        k3x, k3v = v + 0.5 * dt * k2v, accel(x + 0.5 * dt * k2x, qm1, qm2)
        k4x, k4v = v + dt * k3v, accel(x + dt * k3x, qm1, qm2)
        x = x + dt / 6 * (k1x + 2 * k2x + 2 * k3x + k4x)
        v = v + dt / 6 * (k1v + 2 * k2v + 2 * k3v + k4v)
        if step in grab:
            out[:, grab[step]] = x
    return out


def make_dataset(seed=0, n_bodies=40, per_body=600):
    rng = np.random.default_rng(seed)
    qm = np.zeros((n_bodies, 2))
    for j in range(2):
        ch = rng.permutation(n_bodies)[: int(n_bodies * 0.6)]
        qm[ch, j] = rng.choice([-1.0, 1.0], len(ch)) * rng.uniform(0.3, 1.0, len(ch))
    held = np.arange(n_bodies - 8, n_bodies)
    rows = []
    for i in range(n_bodies):
        x0 = rng.uniform(*X_RANGE, per_body)
        v0 = rng.uniform(-V_MAX, V_MAX, per_body)
        tg = integrate(x0, v0, np.full(per_body, qm[i, 0]), np.full(per_body, qm[i, 1]))
        rows.append((np.full(per_body, i), np.stack([x0, v0], 1), tg))
    body = np.concatenate([r[0] for r in rows]).astype(np.int64)
    X = np.concatenate([r[1] for r in rows]).astype(np.float32)
    Y = np.concatenate([r[2] for r in rows]).astype(np.float32)
    is_held = np.isin(body, held)
    n_seen = int((~is_held).sum())
    idx = np.where(~is_held)[0][rng.permutation(n_seen)]
    n_te = n_seen // 6
    return {"qm": qm, "held_bodies": held,
            "train": (body[idx[n_te:]], X[idx[n_te:]], Y[idx[n_te:]]),
            "test": (body[idx[:n_te]], X[idx[:n_te]], Y[idx[:n_te]]),
            "held": (body[is_held], X[is_held], Y[is_held])}


class LaneModel(nn.Module):
    def __init__(self, n_bodies: int, lanes: int):
        super().__init__()
        self.lanes = lanes
        if lanes > 0:
            self.w0 = nn.Embedding(n_bodies, lanes)
        d = 2 + lanes
        self.F = nn.Sequential(
            nn.Linear(d, 128), nn.Tanh(), nn.Linear(128, 128), nn.Tanh(), nn.Linear(128, d)
        )

    def rollout(self, X, w0):
        s = torch.cat([X, w0], dim=1) if self.lanes > 0 else X
        xs = []
        for step in range(1, N_ROLL + 1):
            s = s + H * self.F(s)
            if step in TARGETS:
                xs.append(s[:, :1])
        return torch.cat(xs, dim=1)

    def forward(self, X, body):
        w0 = self.w0(body) if self.lanes > 0 else None
        return self.rollout(X, w0)


def mse_by_class(model, split, qm):
    body, X, Y = split
    with torch.no_grad():
        err = ((model(torch.from_numpy(X), torch.from_numpy(body))
                - torch.from_numpy(Y)) ** 2).mean(1).numpy()
    both = (np.abs(qm[body, 0]) > 1e-9) & (np.abs(qm[body, 1]) > 1e-9)
    return {"all": float(err.mean()),
            "doubly_charged": float(err[both].mean()) if both.any() else None}


def run_arm(L, data, seed=0):
    torch.manual_seed(24 + L)
    rng = np.random.default_rng(seed)
    n_bodies = len(data["qm"])
    model = LaneModel(n_bodies, L)
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)
    body, X, Y = data["train"]
    ckpt = RESULTS / f"24_ckpt_L{L}.pt"
    start = 0
    if ckpt.exists():
        start, rng, exact = load_ckpt(ckpt, model, opt, fallback_seed=seed)
        print(f"  [L={L}] resumed at {start} ({'bit-exact' if exact else 'legacy'})")
    for step in range(start, STEPS):
        idx = rng.integers(0, len(X), 256)
        loss = nn.functional.mse_loss(
            model(torch.from_numpy(X[idx]), torch.from_numpy(body[idx])),
            torch.from_numpy(Y[idx]))
        opt.zero_grad()
        loss.backward()
        opt.step()
        if step % 250 == 0:
            progress(f"24_lanes_L{L}", step, STEPS, loss=float(loss.detach()))
            if step % 1000 == 0 and step > 0:
                save_ckpt(ckpt, model, opt, step, rng)
    model.eval()
    res = mse_by_class(model, data["test"], data["qm"])
    print(f"  [L={L}] test {res}")
    if L > 0:
        torch.save(model.state_dict(), RESULTS / f"24_model_L{L}.pt")
    return {"L": L, **res}


def main() -> None:
    data = make_dataset()
    out = []
    done_f = RESULTS / "24_two_charge.json"
    if done_f.exists():
        out = json.loads(done_f.read_text())
    for L in LANES:
        if any(r["L"] == L for r in out):
            continue
        print(f"arm: {L} lanes")
        out.append(run_arm(L, data))
        done_f.write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.semilogy([r["L"] for r in out], [r["all"] for r in out], "o-",
                color="darkslategray", label="all bodies")
    ax.semilogy([r["L"] for r in out],
                [r["doubly_charged"] for r in out], "s--", color="crimson",
                label="doubly-charged bodies")
    ax.set_xlabel("internal lanes offered (L)")
    ax.set_ylabel("test MSE (log)")
    ax.set_xticks(list(LANES))
    ax.set_title("two charges: how many hidden lanes does the net need?")
    ax.legend()
    fig.tight_layout()
    fig.savefig(RESULTS / "24_two_charge.png", dpi=140)
    print(f"plot -> {RESULTS / '24_two_charge.png'}")


if __name__ == "__main__":
    main()
