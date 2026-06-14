"""Step 33 — the legibility law, third leg: does invariant-preserving STRUCTURE recover
legible dynamics?

One harness, three cells (amortized per-body code throughout; one variable = the update):
  (dynamic, generic)    charge precesses, w-update = w + MLP(state)   -> expect scrambled (Wong)
  (dynamic, orthogonal) same data, w-update = R(state) w, R in SO(3)  -> expect legible + |w| kept
  (static, generic)     charge frozen                                  -> anchors static leg (Phase I)
Legibility = linear decode r of the true charge q(t) from the evolved internal state w(t).
Pre-registration 2026-06-15. Physics = minimal Wong (web-verified earlier).
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
from curvlib import RESULTS, TRAJ_TIMES, V_MAX, WELL_DEPTH, WELL_WIDTH, X_RANGE, progress
from sklearn.linear_model import Ridge
from sklearn.neighbors import KNeighborsRegressor
from sklearn.model_selection import cross_val_predict
from torch import nn

H = 0.1
N_ROLL = int(round(TRAJ_TIMES[-1] / H))
TARGETS = [int(round(t / H)) for t in TRAJ_TIMES]
E_AMP = np.array([0.30, 0.35, 0.25]); E_C = np.array([0.8, -1.0, 0.2])
A_AMP = np.array([5.4, 4.2, 4.8]); A_C = np.array([-0.5, 0.6, 1.1])
K_SNIP, STEPS = 6, 14000


def deriv(s, rotate):
    x, v, q = s[..., 0], s[..., 1], s[..., 2:5]
    a = -WELL_DEPTH * x * np.exp(-x**2 / (2 * WELL_WIDTH**2)) / WELL_WIDTH**2 \
        + (q * (E_AMP * np.exp(-((x[..., None] - E_C) ** 2) / 2))).sum(-1)
    if rotate:
        Af = A_AMP * np.exp(-((x[..., None] - A_C) ** 2) / 2)
        dq = -v[..., None] * np.cross(Af, q)
    else:
        dq = np.zeros_like(q)
    return np.concatenate([v[..., None], a[..., None], dq], -1)


def integ(x0, v0, q0, rotate, dt=0.01, keep_q=False):
    s = np.concatenate([x0[:, None], v0[:, None], q0], 1).astype(float)
    grab = {int(round(t / dt)): i for i, t in enumerate(TRAJ_TIMES)}
    sub = int(round(H / dt))
    xo = np.empty((len(x0), len(TRAJ_TIMES)))
    qo = np.empty((len(x0), N_ROLL, 3)) if keep_q else None
    for step in range(1, int(round(TRAJ_TIMES[-1] / dt)) + 1):
        k1 = deriv(s, rotate); k2 = deriv(s + .5 * dt * k1, rotate)
        k3 = deriv(s + .5 * dt * k2, rotate); k4 = deriv(s + dt * k3, rotate)
        s = s + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        if step in grab:
            xo[:, grab[step]] = s[:, 0]
        if keep_q and step % sub == 0:
            qo[:, step // sub - 1] = s[:, 2:5]
    return (xo, qo) if keep_q else xo


def make_data(rotate, seed=0, n_bodies=200, per_body=120):
    rng = np.random.default_rng(seed)
    q0 = rng.normal(size=(n_bodies, 3)); q0 /= np.linalg.norm(q0, axis=1, keepdims=True)
    q0 *= rng.uniform(0.4, 1.0, (n_bodies, 1))
    snip, qx, qv, qy, body = [], [], [], [], []
    for i in range(n_bodies):
        sx = rng.uniform(*X_RANGE, K_SNIP); sv = rng.uniform(-V_MAX, V_MAX, K_SNIP)
        sp = integ(sx, sv, np.tile(q0[i], (K_SNIP, 1)), rotate)
        snip.append(np.concatenate([sx[:, None], sv[:, None], sp], 1))
        x0 = rng.uniform(*X_RANGE, per_body); v0 = rng.uniform(-V_MAX, V_MAX, per_body)
        qy.append(integ(x0, v0, np.tile(q0[i], (per_body, 1)), rotate)); qx.append(x0); qv.append(v0)
        body.append(np.full(per_body, i))
    held = np.arange(n_bodies - 20, n_bodies)
    return {"q0": q0, "held": held, "snip": np.array(snip, np.float32),
            "qx": np.concatenate(qx).astype(np.float32), "qv": np.concatenate(qv).astype(np.float32),
            "qy": np.concatenate(qy).astype(np.float32), "body": np.concatenate(body).astype(np.int64)}


def skew(a):  # (...,3) -> (...,3,3) skew-symmetric
    z = torch.zeros_like(a[..., 0])
    return torch.stack([torch.stack([z, -a[..., 2], a[..., 1]], -1),
                        torch.stack([a[..., 2], z, -a[..., 0]], -1),
                        torch.stack([-a[..., 1], a[..., 0], z], -1)], -2)


class Model(nn.Module):
    def __init__(self, mode):
        super().__init__()
        self.mode = mode  # 'generic' | 'orthogonal'
        self.enc = nn.Sequential(nn.Linear(5, 64), nn.Tanh(), nn.Linear(64, 64), nn.Tanh(), nn.Linear(64, 3))
        self.xv = nn.Sequential(nn.Linear(5, 64), nn.Tanh(), nn.Linear(64, 64), nn.Tanh(), nn.Linear(64, 2))
        self.wu = nn.Sequential(nn.Linear(5, 64), nn.Tanh(), nn.Linear(64, 64), nn.Tanh(), nn.Linear(64, 3))

    def code(self, snip, body):
        return self.enc(snip[body]).mean(1)

    def rollout(self, snip, body, x0, v0, keep=False):
        w = self.code(snip, body); xv = torch.stack([x0, v0], 1)
        xs, ws = [], []
        for step in range(1, N_ROLL + 1):
            s = torch.cat([xv, w], 1)
            xv = xv + H * self.xv(s)
            if self.mode == "orthogonal":
                R = torch.linalg.matrix_exp(skew(self.wu(s) * H))
                w = torch.bmm(R, w.unsqueeze(-1)).squeeze(-1)
            else:
                w = w + H * self.wu(s)
            if keep:
                ws.append(w.clone())
            if step in TARGETS:
                xs.append(xv[:, :1])
        return (torch.cat(xs, 1), torch.stack(ws, 1)) if keep else torch.cat(xs, 1)


def run_cell(rotate, mode, seed=0):
    d = make_data(rotate, seed=seed)
    snip = torch.from_numpy(d["snip"]); bdy = torch.from_numpy(d["body"])
    X = torch.from_numpy(d["qx"]); V = torch.from_numpy(d["qv"]); Y = torch.from_numpy(d["qy"])
    seen = np.where(~np.isin(d["body"], d["held"]))[0]
    torch.manual_seed(33); rng = np.random.default_rng(0)
    m = Model(mode); opt = torch.optim.Adam(m.parameters(), lr=1e-3)
    tag = f"{'dyn' if rotate else 'stat'}_{mode}"
    for step in range(STEPS):
        idx = seen[rng.integers(0, len(seen), 256)]
        loss = nn.functional.mse_loss(m.rollout(snip, bdy[idx], X[idx], V[idx]), Y[idx])
        opt.zero_grad(); loss.backward(); opt.step()
        if step % 500 == 0:
            progress(f"33_{tag}", step, STEPS, loss=float(loss.detach()))
    m.eval()
    rng2 = np.random.default_rng(11); n = 600
    hb = rng2.choice(d["held"], n)
    x0 = rng2.uniform(*X_RANGE, n).astype(np.float32); v0 = rng2.uniform(-V_MAX, V_MAX, n).astype(np.float32)
    with torch.no_grad():
        _, ws = m.rollout(snip, torch.from_numpy(hb), torch.from_numpy(x0), torch.from_numpy(v0), keep=True)
    ws = ws.numpy()
    _, qtrue = integ(x0.astype(float), v0.astype(float), d["q0"][hb], rotate, keep_q=True)
    L = ws.reshape(-1, 3); Q = qtrue.reshape(-1, 3)
    lin = [float(np.corrcoef(cross_val_predict(Ridge(1.0), L, Q[:, j], cv=5), Q[:, j])[0, 1]) for j in range(3)]
    nl = [float(np.corrcoef(cross_val_predict(KNeighborsRegressor(8), L, Q[:, j], cv=5), Q[:, j])[0, 1]) for j in range(3)]
    wn = np.linalg.norm(ws, axis=-1)
    drift = float(np.median(wn.std(1) / (wn.mean(1) + 1e-9)))
    res = {"cell": tag, "linear_min": float(min(lin)), "linear": lin,
           "nonlinear_min": float(min(nl)), "w_norm_drift": drift}
    print(f"[{tag:16s}] linear_min={min(lin):.3f} nonlinear_min={min(nl):.3f} |w|drift={drift:.3f}")
    return res


def main():
    cells = [(True, "generic"), (True, "orthogonal"), (False, "generic")]
    out = {r["cell"]: r for r in (run_cell(rot, mode) for rot, mode in cells)}
    (RESULTS / "33_legibility.json").write_text(json.dumps(out, indent=1))
    dg, do_, sg = out["dyn_generic"], out["dyn_orthogonal"], out["stat_generic"]
    print("\n=== the legibility law (linear decode of the evolving code) ===")
    print(f"  static + generic     (anchor):   {sg['linear_min']:.3f}  [legible static]")
    print(f"  dynamic + generic    (Wong):     {dg['linear_min']:.3f}  [scrambled]  |w|drift {dg['w_norm_drift']:.3f}")
    print(f"  dynamic + orthogonal (structure):{do_['linear_min']:.3f}  [?]          |w|drift {do_['w_norm_drift']:.3f}")
    ok = do_["linear_min"] > dg["linear_min"] + 0.2 and do_["w_norm_drift"] < dg["w_norm_drift"]
    print(f"\nTHIRD LEG {'CONFIRMED' if ok else 'NOT confirmed'}: structure recovers legible dynamics"
          f" ({do_['linear_min']:.2f} vs generic {dg['linear_min']:.2f})")

    fig, ax = plt.subplots(figsize=(7, 5))
    labels = ["static\n+generic", "dynamic\n+generic", "dynamic\n+orthogonal"]
    vals = [sg["linear_min"], dg["linear_min"], do_["linear_min"]]
    ax.bar(labels, vals, color=["steelblue", "crimson", "seagreen"])
    ax.axhline(0.9, ls="--", c="k", lw=.8); ax.set_ylabel("linear decode r of true charge")
    ax.set_title("the legibility law: amortize (static) / scramble (dynamic) / structure recovers")
    fig.tight_layout(); fig.savefig(RESULTS / "33_legibility.png", dpi=140)
    print("saved results/33_legibility.json + .png")


if __name__ == "__main__":
    main()
