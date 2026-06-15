"""Step 46 — refining the legibility law: WHAT makes a FREE code legible?

The legibility law says free per-body codes scramble (linear-illegible, nonlinear-legible). But
script 45 found a free code that was LINEARLY legible (scalar rho, r=0.98), while Phase C's free
code for EM's q/m scrambled (linear 0.02, behavioral 0.9999). Both are free 4-d embeddings — so
free-vs-amortized is NOT the whole story. Two suspects differ between them:
  SIGN:     rho is one-signed [>0];   q/m is signed [+/-].
  COUPLING: rho couples through POSITION (a potential well, a += c*grad);
            q/m coupled through VELOCITY (magnetic, a += c*(v x B)).

Clean 2x2 factorial (sign x coupling), everything else fixed: same |charge| range, same gravity
background, same free 4-d embedding, same training. Decode the charge from the embedding in each
cell (linear ridge = legibility; kNN = info presence). Which factor controls legibility?

Pre-reg (2026-06-16): prediction SIGN dominates.
  L1 replicate 45: one-signed+position linear-decode > 0.85.
  L2 replicate Phase C: signed+velocity linear-decode < 0.5 (but nonlinear > 0.8 = info present).
  L3 discriminator: report sign_effect vs coupling_effect; clean if one > 0.3 and the other < 0.15.
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
from curvlib import RESULTS, WELL_DEPTH, WELL_WIDTH, TRAJ_TIMES, V_MAX, progress
from sklearn.linear_model import Ridge
from sklearn.neighbors import KNeighborsRegressor
from sklearn.model_selection import cross_val_predict
from torch import nn

SCALAR_CENTER = (1.2, -0.8)
SCALAR_DEPTH = 0.15
B_AMP, B_CENTER = 0.6, (0.8, -0.5)
N_BODIES, PER_BODY, STEPS, HELD, EMB_DIM = 48, 300, 6000, 8, 4


def accel(x, y, vx, vy, c, coupling):
    eg = np.exp(-(x**2 + y**2) / (2 * WELL_WIDTH**2))
    axg = -WELL_DEPTH * x * eg / WELL_WIDTH**2
    ayg = -WELL_DEPTH * y * eg / WELL_WIDTH**2
    if coupling == "position":
        dx, dy = x - SCALAR_CENTER[0], y - SCALAR_CENTER[1]
        es = np.exp(-(dx**2 + dy**2) / (2 * WELL_WIDTH**2))
        return axg - c * SCALAR_DEPTH * dx * es / WELL_WIDTH**2, ayg - c * SCALAR_DEPTH * dy * es / WELL_WIDTH**2
    bx, by = x - B_CENTER[0], y - B_CENTER[1]
    B = B_AMP * np.exp(-(bx**2 + by**2) / 2.0)
    return axg + c * vy * B, ayg - c * vx * B


def integrate(x0, y0, vx0, vy0, c, coupling, dt=0.01):
    n_steps = int(round(TRAJ_TIMES[-1] / dt))
    grab = {int(round(t / dt)): i for i, t in enumerate(TRAJ_TIMES)}
    x, y, vx, vy = (a.astype(float).copy() for a in (x0, y0, vx0, vy0))
    out = np.empty((len(x0), len(TRAJ_TIMES), 2))
    for step in range(1, n_steps + 1):
        def rk(xx, yy, ux, uy):
            ax, ay = accel(xx, yy, ux, uy, c, coupling)
            return ux, uy, ax, ay
        k1 = rk(x, y, vx, vy)
        k2 = rk(x + .5*dt*k1[0], y + .5*dt*k1[1], vx + .5*dt*k1[2], vy + .5*dt*k1[3])
        k3 = rk(x + .5*dt*k2[0], y + .5*dt*k2[1], vx + .5*dt*k2[2], vy + .5*dt*k2[3])
        k4 = rk(x + dt*k3[0], y + dt*k3[1], vx + dt*k3[2], vy + dt*k3[3])
        x = x + dt/6*(k1[0]+2*k2[0]+2*k3[0]+k4[0]); y = y + dt/6*(k1[1]+2*k2[1]+2*k3[1]+k4[1])
        vx = vx + dt/6*(k1[2]+2*k2[2]+2*k3[2]+k4[2]); vy = vy + dt/6*(k1[3]+2*k2[3]+2*k3[3]+k4[3])
        if step in grab:
            out[:, grab[step], 0] = x; out[:, grab[step], 1] = y
    return out


def make_data(sign_mode, coupling, seed=0):
    rng = np.random.default_rng(seed)
    mag = rng.uniform(0.4, 1.6, N_BODIES)
    c_body = mag if sign_mode == "onesigned" else mag * rng.choice([-1.0, 1.0], N_BODIES)
    held = np.arange(N_BODIES - HELD, N_BODIES)
    body, X, Y = [], [], []
    for i in range(N_BODIES):
        x0 = rng.uniform(-2.5, 2.5, PER_BODY); y0 = rng.uniform(-2.5, 2.5, PER_BODY)
        vx0 = rng.uniform(-V_MAX, V_MAX, PER_BODY); vy0 = rng.uniform(-V_MAX, V_MAX, PER_BODY)
        tg = integrate(x0, y0, vx0, vy0, np.full(PER_BODY, c_body[i]), coupling).reshape(PER_BODY, -1)
        body.append(np.full(PER_BODY, i)); X.append(np.stack([x0, y0, vx0, vy0], 1)); Y.append(tg)
    body = np.concatenate(body).astype(np.int64)
    X = np.concatenate(X).astype(np.float32); Y = np.concatenate(Y).astype(np.float32)
    seen = np.where(~np.isin(body, held))[0]; rng.shuffle(seen)
    return {"c_body": c_body, "held": held, "train": (body[seen], X[seen], Y[seen])}


class Force(nn.Module):
    def __init__(self, n):
        super().__init__()
        self.emb = nn.Embedding(n, EMB_DIM)
        self.net = nn.Sequential(nn.Linear(4 + EMB_DIM, 128), nn.Tanh(), nn.Linear(128, 128), nn.Tanh(),
                                 nn.Linear(128, 2 * len(TRAJ_TIMES)))

    def forward(self, x, body):
        return self.net(torch.cat([x, self.emb(body)], 1))


def train_decode(sign_mode, coupling):
    d = make_data(sign_mode, coupling)
    torch.manual_seed(0); rng = np.random.default_rng(0)
    body, X, Y = d["train"]; m = Force(N_BODIES); opt = torch.optim.Adam(m.parameters(), lr=1e-3)
    for step in range(STEPS):
        idx = rng.integers(0, len(X), 512)
        loss = nn.functional.mse_loss(m(torch.from_numpy(X[idx]), torch.from_numpy(body[idx])),
                                      torch.from_numpy(Y[idx]))
        opt.zero_grad(); loss.backward(); opt.step()
        if step % 500 == 0:
            progress(f"46_{sign_mode}_{coupling}", step, STEPS, loss=float(loss.detach()))
    seen = np.setdiff1d(np.arange(N_BODIES), d["held"])
    emb = m.emb(torch.from_numpy(seen.astype(np.int64))).detach().numpy()
    c = d["c_body"][seen]
    lin = float(np.corrcoef(cross_val_predict(Ridge(1.0), emb, c, cv=5), c)[0, 1])
    nl = float(np.corrcoef(cross_val_predict(KNeighborsRegressor(5), emb, c, cv=5), c)[0, 1])
    return {"linear": lin, "nonlinear": nl, "train_mse": float(loss.detach())}


def main():
    cells = {}
    for sign_mode in ("onesigned", "signed"):
        for coupling in ("position", "velocity"):
            r = train_decode(sign_mode, coupling)
            cells[f"{sign_mode}_{coupling}"] = r
            print(f"{sign_mode:9s} x {coupling:8s}: linear {r['linear']:.2f} | nonlinear {r['nonlinear']:.2f} "
                  f"| mse {r['train_mse']:.1e}")

    lin = {k: v["linear"] for k, v in cells.items()}
    sign_effect = (lin["onesigned_position"] + lin["onesigned_velocity"]) / 2 - \
                  (lin["signed_position"] + lin["signed_velocity"]) / 2
    coupling_effect = (lin["onesigned_position"] + lin["signed_position"]) / 2 - \
                      (lin["onesigned_velocity"] + lin["signed_velocity"]) / 2
    l1 = bool(lin["onesigned_position"] > 0.85)
    l2 = bool(lin["signed_velocity"] < 0.5 and cells["signed_velocity"]["nonlinear"] > 0.8)
    dom = "sign" if abs(sign_effect) > abs(coupling_effect) else "coupling"
    clean = bool((abs(sign_effect) > 0.3 and abs(coupling_effect) < 0.15) or
                 (abs(coupling_effect) > 0.3 and abs(sign_effect) < 0.15))
    out = {"cells": cells, "sign_effect": sign_effect, "coupling_effect": coupling_effect,
           "dominant_factor": dom, "clean_separation": clean,
           "L1_replicate45": l1, "L2_replicatePhaseC": l2}
    print(f"\nsign_effect (one-signed minus signed) = {sign_effect:+.2f}")
    print(f"coupling_effect (position minus velocity) = {coupling_effect:+.2f}")
    print(f"L1 one-signed+position legible (>0.85): {l1}")
    print(f"L2 signed+velocity scrambles (lin<0.5, nl>0.8): {l2}")
    print(f"DOMINANT FACTOR: {dom}  (clean separation: {clean})")
    (RESULTS / "46_what_makes_legible.json").write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(figsize=(7, 5.2))
    grid = np.array([[lin["onesigned_position"], lin["onesigned_velocity"]],
                     [lin["signed_position"], lin["signed_velocity"]]])
    im = ax.imshow(grid, vmin=0, vmax=1, cmap="RdYlGn")
    ax.set_xticks([0, 1]); ax.set_xticklabels(["position\ncoupling", "velocity\ncoupling"])
    ax.set_yticks([0, 1]); ax.set_yticklabels(["one-signed", "signed (±)"])
    for i in range(2):
        for j in range(2):
            ax.text(j, i, f"{grid[i, j]:.2f}", ha="center", va="center", fontsize=15, fontweight="bold")
    fig.colorbar(im, label="linear legibility of charge from free code")
    ax.set_title(f"what makes a free code legible?\nsign Δ={sign_effect:+.2f}  coupling Δ={coupling_effect:+.2f}  → {dom}")
    fig.tight_layout(); fig.savefig(RESULTS / "46_what_makes_legible.png", dpi=140)
    print("saved results/46_what_makes_legible.json + .png")


if __name__ == "__main__":
    main()
