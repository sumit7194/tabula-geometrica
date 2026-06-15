"""Step 48 — the clean isolation: does LATENT DIMENSIONALITY scramble a free code?

The 45->47 arc: 1-d smooth charges give LEGIBLE free codes (45 rho 0.98, 46 all 0.99-1.00), but a
2-d charge (47 control) was only 0.70 linear / 0.94 nonlinear — a partial scramble — and the
neutral-mix / random-MLP arms muddied it with confounds (magnetic c2 weakly identifiable, random
map possibly non-injective). 47 POINTED at dimensionality. This isolates it cleanly:

  charge c in R^D drives D independent SCALAR wells (linear coupling, no magnetic confound), one
  well per component, all one-signed (sign already ruled out in 46). Sweep D in {1,2,3}, well-
  powered (N=200 bodies), fixed 8-d free embedding. Decode c from the embedding (linear=legibility,
  kNN=info present). If dimensionality is the cause: linear legibility falls with D while info stays.

This would UNIFY the whole picture: 1-d (45/46) legible, higher-d (Phase I's 2-d latent) scrambled —
the "free->scramble" leg of the legibility law is conditional on latent dimensionality.

Pre-reg (2026-06-16):
  Q1 1-d legible: D=1 linear > 0.9.
  Q2 dimensionality scrambles: linear legibility decreases monotonically with D, D=3 linear < 0.7.
  Q3 info preserved: nonlinear (kNN) decode > 0.85 at all D (scramble = hidden, not lost).
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

CENTERS = [(1.2, -0.8), (-1.1, 1.0), (0.1, 1.6)]   # up to 3 well-separated scalar wells
DEPTH_S = 0.18
N_BODIES, PER_BODY, STEPS, HELD, EMB_DIM = 200, 120, 7000, 20, 4  # tight 4-d code (45/46's legible regime); isolate latent-D at fixed capacity


def accel(x, y, vx, vy, c):
    """a = gravity(origin) + sum_k c[:,k] * scalar-well_k.  c: (n, D)."""
    eg = np.exp(-(x**2 + y**2) / (2 * WELL_WIDTH**2))
    ax = -WELL_DEPTH * x * eg / WELL_WIDTH**2
    ay = -WELL_DEPTH * y * eg / WELL_WIDTH**2
    for k in range(c.shape[1]):
        cx, cy = CENTERS[k]
        dx, dy = x - cx, y - cy
        e = np.exp(-(dx**2 + dy**2) / (2 * WELL_WIDTH**2))
        ax = ax - c[:, k] * DEPTH_S * dx * e / WELL_WIDTH**2
        ay = ay - c[:, k] * DEPTH_S * dy * e / WELL_WIDTH**2
    return ax, ay


def integrate(x0, y0, vx0, vy0, c, dt=0.01):
    n_steps = int(round(TRAJ_TIMES[-1] / dt))
    grab = {int(round(t / dt)): i for i, t in enumerate(TRAJ_TIMES)}
    x, y, vx, vy = (a.astype(float).copy() for a in (x0, y0, vx0, vy0))
    out = np.empty((len(x0), len(TRAJ_TIMES), 2))
    for step in range(1, n_steps + 1):
        def rk(xx, yy, ux, uy):
            ax, ay = accel(xx, yy, ux, uy, c)
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


def make_data(D, seed=0):
    rng = np.random.default_rng(seed)
    c_body = rng.uniform(0.4, 1.6, (N_BODIES, D))
    held = np.arange(N_BODIES - HELD, N_BODIES)
    body, X, Y = [], [], []
    for i in range(N_BODIES):
        x0 = rng.uniform(-2.5, 2.5, PER_BODY); y0 = rng.uniform(-2.5, 2.5, PER_BODY)
        vx0 = rng.uniform(-V_MAX, V_MAX, PER_BODY); vy0 = rng.uniform(-V_MAX, V_MAX, PER_BODY)
        c = np.tile(c_body[i], (PER_BODY, 1))
        tg = integrate(x0, y0, vx0, vy0, c).reshape(PER_BODY, -1)
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


def run(D):
    d = make_data(D)
    torch.manual_seed(0); rng = np.random.default_rng(0)
    body, X, Y = d["train"]; m = Force(N_BODIES); opt = torch.optim.Adam(m.parameters(), lr=1e-3)
    for step in range(STEPS):
        idx = rng.integers(0, len(X), 512)
        loss = nn.functional.mse_loss(m(torch.from_numpy(X[idx]), torch.from_numpy(body[idx])),
                                      torch.from_numpy(Y[idx]))
        opt.zero_grad(); loss.backward(); opt.step()
        if step % 500 == 0:
            progress(f"48_D{D}", step, STEPS, loss=float(loss.detach()))
    seen = np.setdiff1d(np.arange(N_BODIES), d["held"])
    emb = m.emb(torch.from_numpy(seen.astype(np.int64))).detach().numpy()
    c = d["c_body"][seen]
    lin = float(np.mean([np.corrcoef(cross_val_predict(Ridge(1.0), emb, c[:, j], cv=5), c[:, j])[0, 1]
                         for j in range(D)]))
    nl = float(np.mean([np.corrcoef(cross_val_predict(KNeighborsRegressor(7), emb, c[:, j], cv=5), c[:, j])[0, 1]
                        for j in range(D)]))
    return {"D": D, "linear": lin, "nonlinear": nl, "train_mse": float(loss.detach())}


def main():
    res = [run(D) for D in (1, 2, 3)]
    for r in res:
        print(f"D={r['D']}: linear {r['linear']:.2f} | nonlinear {r['nonlinear']:.2f} | mse {r['train_mse']:.1e}")
    lins = [r["linear"] for r in res]
    q1 = bool(lins[0] > 0.9)
    q2 = bool(lins[0] > lins[1] > lins[2] and lins[2] < 0.7)
    q3 = bool(all(r["nonlinear"] > 0.85 for r in res))
    out = {"sweep": res, "Q1_1d_legible": q1, "Q2_dimensionality_scrambles": q2,
           "Q3_info_preserved": q3, "dimensionality_is_the_cause": bool(q1 and q2 and q3)}
    print(f"\nQ1 1-d legible (lin {lins[0]:.2f} >0.9): {q1}")
    print(f"Q2 dimensionality scrambles (lin {[round(x,2) for x in lins]} decreasing, D3<0.7): {q2}")
    print(f"Q3 info preserved (nl all >0.85): {q3}")
    print(f"\nDIMENSIONALITY IS THE CAUSE: {out['dimensionality_is_the_cause']}")
    (RESULTS / "48_legibility_dimension.json").write_text(json.dumps(out, indent=1))

    Ds = [r["D"] for r in res]
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.plot(Ds, lins, "o-", color="seagreen", label="linear (legibility)")
    ax.plot(Ds, [r["nonlinear"] for r in res], "s--", color="gray", label="nonlinear (info present)")
    ax.axhline(0.7, ls=":", color="crimson"); ax.set_xticks(Ds)
    ax.set_xlabel("latent charge dimensionality D"); ax.set_ylabel("decode r of charge from FREE code")
    ax.set_ylim(0, 1); ax.legend()
    ax.set_title("free-code legibility falls with latent dimensionality\n(1-d legible → higher-d scrambles; info preserved)")
    fig.tight_layout(); fig.savefig(RESULTS / "48_legibility_dimension.png", dpi=140)
    print("saved results/48_legibility_dimension.json + .png")


if __name__ == "__main__":
    main()
