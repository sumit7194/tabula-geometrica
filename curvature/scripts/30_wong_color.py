"""Step 30 — Phase H row 2: Wong color charge (the geometrization-survey crown).

A body carries a 3-component SU(2) color charge Q that PARALLEL-TRANSPORTS along its
path (Wong 1970): it precesses, dQ/dt = -v (A(x) x Q), so |Q| is conserved, while the
color-electric force a += sum_a Q^a E^a(x) depends on the rotating Q. We give the net
L internal lanes (the LaneModel machinery) and ask: (W2) how many lanes does color need
vs electric's 1? (W3) does the learned lane state ROTATE along the rollout (vs static for
electric)? (W4) is a quadratic form of the lane state conserved (the |Q| invariant)?
Pre-registration 2026-06-15. Classical Wong limit only.
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
from curvlib import RESULTS, TRAJ_TIMES, V_MAX, WELL_DEPTH, WELL_WIDTH, X_RANGE, progress
from torch import nn

H = 0.1
N_ROLL = int(round(TRAJ_TIMES[-1] / H))
TARGETS = [int(round(t / H)) for t in TRAJ_TIMES]
STEPS = 12000
LANES = (0, 1, 2, 3, 4)
E_AMP = np.array([0.30, 0.35, 0.25])      # 3 color-electric field strengths
E_C = np.array([0.8, -1.0, 0.2])          # their centers
A_AMP = np.array([0.9, 0.7, 0.8])         # precession-axis field (gauge potential)
A_C = np.array([-0.5, 0.6, 1.1])


def _well(x):
    return -WELL_DEPTH * x * np.exp(-x**2 / (2 * WELL_WIDTH**2)) / WELL_WIDTH**2


def _Efield(x):  # (..,3) color-electric scalars at x
    return E_AMP * np.exp(-((x[..., None] - E_C) ** 2) / 2)


def _Afield(x):  # (..,3) precession axis at x
    return A_AMP * np.exp(-((x[..., None] - A_C) ** 2) / 2)


def deriv(state, color):
    """state (...,5)=(x,v,Q0,Q1,Q2). color=False -> electric control (Q frozen)."""
    x, v, Q = state[..., 0], state[..., 1], state[..., 2:5]
    a = _well(x) + (Q * _Efield(x)).sum(-1)
    dx, dv = v, a
    if color:
        dQ = -v[..., None] * np.cross(_Afield(x), Q)   # SU(2) precession, |Q| conserved
    else:
        dQ = np.zeros_like(Q)
    return np.concatenate([dx[..., None], dv[..., None], dQ], -1)


def integrate(x0, v0, Q0, color, dt=0.01):
    grab = {int(round(t / dt)): i for i, t in enumerate(TRAJ_TIMES)}
    s = np.concatenate([x0[:, None], v0[:, None], Q0], 1).astype(float)
    out = np.empty((len(x0), len(TRAJ_TIMES)))
    for step in range(1, int(round(TRAJ_TIMES[-1] / dt)) + 1):
        k1 = deriv(s, color); k2 = deriv(s + .5 * dt * k1, color)
        k3 = deriv(s + .5 * dt * k2, color); k4 = deriv(s + dt * k3, color)
        s = s + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        if step in grab:
            out[:, grab[step]] = s[:, 0]
    return out


def make_dataset(color, seed=0, n_bodies=40, per_body=600):
    rng = np.random.default_rng(seed)
    Q0 = rng.normal(size=(n_bodies, 3))
    Q0 /= np.linalg.norm(Q0, axis=1, keepdims=True)
    Q0 *= rng.uniform(0.4, 1.0, (n_bodies, 1))     # per-body color charge (dir x mag)
    held = np.arange(n_bodies - 8, n_bodies)
    rows = []
    for i in range(n_bodies):
        x0 = rng.uniform(*X_RANGE, per_body); v0 = rng.uniform(-V_MAX, V_MAX, per_body)
        tg = integrate(x0, v0, np.tile(Q0[i], (per_body, 1)), color)
        rows.append((np.full(per_body, i), np.stack([x0, v0], 1), tg))
    body = np.concatenate([r[0] for r in rows]).astype(np.int64)
    X = np.concatenate([r[1] for r in rows]).astype(np.float32)
    Y = np.concatenate([r[2] for r in rows]).astype(np.float32)
    is_h = np.isin(body, held); seen = np.where(~is_h)[0]
    idx = seen[rng.permutation(len(seen))]; nte = len(seen) // 6
    return {"Q0": Q0, "train": (body[idx[nte:]], X[idx[nte:]], Y[idx[nte:]]),
            "test": (body[idx[:nte]], X[idx[:nte]], Y[idx[:nte]])}


class LaneModel(nn.Module):
    def __init__(self, n_bodies, lanes):
        super().__init__()
        self.lanes = lanes
        if lanes:
            self.w0 = nn.Embedding(n_bodies, lanes)
        d = 2 + lanes
        self.F = nn.Sequential(nn.Linear(d, 128), nn.Tanh(), nn.Linear(128, 128),
                               nn.Tanh(), nn.Linear(128, d))

    def rollout(self, X, body, keep_lanes=False):
        s = torch.cat([X, self.w0(body)], 1) if self.lanes else X
        xs, lanes = [], []
        for step in range(1, N_ROLL + 1):
            s = s + H * self.F(s)
            if keep_lanes and self.lanes:
                lanes.append(s[:, 2:].clone())
            if step in TARGETS:
                xs.append(s[:, :1])
        if keep_lanes:
            return torch.cat(xs, 1), torch.stack(lanes, 1)  # (B,T),(B,N_ROLL,L)
        return torch.cat(xs, 1)

    def forward(self, X, body):
        return self.rollout(X, body)


def train(data, L, tag, seed=0):
    torch.manual_seed(30 + L)
    rng = np.random.default_rng(seed)
    m = LaneModel(len(data["Q0"]), L)
    opt = torch.optim.Adam(m.parameters(), lr=1e-3)
    body, X, Y = data["train"]
    for step in range(STEPS):
        idx = rng.integers(0, len(X), 256)
        loss = nn.functional.mse_loss(
            m(torch.from_numpy(X[idx]), torch.from_numpy(body[idx])), torch.from_numpy(Y[idx]))
        opt.zero_grad(); loss.backward(); opt.step()
        if step % 500 == 0:
            progress(f"30_wong_{tag}_L{L}", step, STEPS, loss=float(loss.detach()))
    m.eval()
    tb, tx, ty = data["test"]
    with torch.no_grad():
        e = float(((m(torch.from_numpy(tx), torch.from_numpy(tb))
                    - torch.from_numpy(ty)) ** 2).mean())
    return m, e


def lane_motion(m, data):
    """W3/W4: angular travel + radius drift of the lane state along the rollout."""
    if m.lanes == 0:
        return None
    rng = np.random.default_rng(7)
    n = 200
    X = np.stack([rng.uniform(*X_RANGE, n), rng.uniform(-V_MAX, V_MAX, n)], 1).astype(np.float32)
    body = torch.from_numpy(rng.integers(0, len(data["Q0"]) - 8, n))
    with torch.no_grad():
        _, lanes = m.rollout(torch.from_numpy(X), body, keep_lanes=True)
    lanes = lanes.numpy()                       # (n, N_ROLL, L)
    v = lanes / (np.linalg.norm(lanes, axis=-1, keepdims=True) + 1e-9)
    cos = np.clip((v[:, 1:] * v[:, :-1]).sum(-1), -1, 1)
    ang = np.arccos(cos).sum(1)                 # total angular travel per body
    rad = np.linalg.norm(lanes, axis=-1)
    drift = (rad.std(1) / (rad.mean(1) + 1e-9))  # radius coefficient of variation
    return {"ang_travel_med": float(np.median(ang)),
            "radius_drift_med": float(np.median(drift))}


def main():
    out = {"color": {}, "electric": {}}
    for tag, color in (("color", True), ("electric", False)):
        data = make_dataset(color, seed=0)
        best = None
        for L in LANES:
            m, e = train(data, L, tag, seed=0)
            mot = lane_motion(m, data)
            out[tag][L] = {"test_mse": e, **(mot or {})}
            print(f"[{tag}] L={L}: test {e:.2e}" + (f" | ang {mot['ang_travel_med']:.2f}"
                  f" rad_drift {mot['radius_drift_med']:.3f}" if mot else ""))
            if L == 2:
                best = (m, data)
    (RESULTS / "30_wong.json").write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(1, 2, figsize=(12, 5))
    for tag, c in (("color", "crimson"), ("electric", "steelblue")):
        ax[0].semilogy(LANES, [out[tag][L]["test_mse"] for L in LANES], "o-", color=c, label=tag)
        ls = [L for L in LANES if L > 0]
        ax[1].plot(ls, [out[tag][L]["ang_travel_med"] for L in ls], "o-", color=c, label=tag)
    ax[0].set_xlabel("lanes L"); ax[0].set_ylabel("test MSE"); ax[0].set_title("W2 lane count"); ax[0].legend()
    ax[1].set_xlabel("lanes L"); ax[1].set_ylabel("median lane angular travel"); ax[1].set_title("W3 rotation"); ax[1].legend()
    fig.tight_layout(); fig.savefig(RESULTS / "30_wong.png", dpi=140)
    print("saved results/30_wong.json + .png")


if __name__ == "__main__":
    main()
