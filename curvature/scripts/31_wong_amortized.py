"""Step 31 — Phase H row 2 v2: Wong color with an AMORTIZED per-body code + strong field.

v1 was an honest negative confounded by (a) only ~12 deg precession, (b) a FREE per-body
embedding (illegible by construction — Phase I), (c) n=32. This fixes all three: gauge
field x6 (median ~41 deg rotation), per-body code INFERRED by a shared snippet-encoder
(Phase I's prescription), n=200. Crown test: does the internal state now LINEARLY track the
rotating, |Q|-conserved color charge? Pre-registration 2026-06-15.
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
from curvlib import RESULTS, TRAJ_TIMES, V_MAX, X_RANGE, progress
from importlib import import_module
from sklearn.linear_model import Ridge
from sklearn.neighbors import KNeighborsRegressor
from sklearn.model_selection import cross_val_predict
from torch import nn

w = import_module("30_wong_color")
H, N_ROLL, TARGETS = w.H, w.N_ROLL, w.TARGETS
ASCALE, LANES, STEPS = 6.0, 3, 35000  # fix round: longer for a cleaner W1 fit
A_AMP = w.A_AMP * ASCALE
K_SNIP = 6


def deriv(s):
    x, v, Q = s[..., 0], s[..., 1], s[..., 2:5]
    a = w._well(x) + (Q * w._Efield(x)).sum(-1)
    Af = A_AMP * np.exp(-((x[..., None] - w.A_C) ** 2) / 2)
    dQ = -v[..., None] * np.cross(Af, Q)
    return np.concatenate([v[..., None], a[..., None], dQ], -1)


def integ(x0, v0, Q0, dt=0.01, keep_Q=False):
    s = np.concatenate([x0[:, None], v0[:, None], Q0], 1).astype(float)
    grab = {int(round(t / dt)): i for i, t in enumerate(TRAJ_TIMES)}
    sub = int(round(H / dt))
    xout = np.empty((len(x0), len(TRAJ_TIMES)))
    Qout = np.empty((len(x0), N_ROLL, 3)) if keep_Q else None
    for step in range(1, int(round(TRAJ_TIMES[-1] / dt)) + 1):
        k1 = deriv(s); k2 = deriv(s + .5 * dt * k1)
        k3 = deriv(s + .5 * dt * k2); k4 = deriv(s + dt * k3)
        s = s + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        if step in grab:
            xout[:, grab[step]] = s[:, 0]
        if keep_Q and step % sub == 0:
            Qout[:, step // sub - 1] = s[:, 2:5]
    return (xout, Qout) if keep_Q else xout


def make_data(seed=0, n_bodies=200, per_body=120):
    rng = np.random.default_rng(seed)
    Q0 = rng.normal(size=(n_bodies, 3)); Q0 /= np.linalg.norm(Q0, axis=1, keepdims=True)
    Q0 *= rng.uniform(0.4, 1.0, (n_bodies, 1))
    snip, qx, qv, qy, body = [], [], [], [], []
    for i in range(n_bodies):
        sx = rng.uniform(*X_RANGE, K_SNIP); sv = rng.uniform(-V_MAX, V_MAX, K_SNIP)
        sp = integ(sx, sv, np.tile(Q0[i], (K_SNIP, 1)))
        snip.append(np.concatenate([sx[:, None], sv[:, None], sp], 1))
        x0 = rng.uniform(*X_RANGE, per_body); v0 = rng.uniform(-V_MAX, V_MAX, per_body)
        qy.append(integ(x0, v0, np.tile(Q0[i], (per_body, 1)))); qx.append(x0); qv.append(v0)
        body.append(np.full(per_body, i))
    held = np.arange(n_bodies - 20, n_bodies)
    return {"Q0": Q0, "held": held, "snip": np.array(snip, dtype=np.float32),
            "qx": np.concatenate(qx).astype(np.float32),
            "qv": np.concatenate(qv).astype(np.float32),
            "qy": np.concatenate(qy).astype(np.float32),
            "body": np.concatenate(body).astype(np.int64)}


class Model(nn.Module):
    def __init__(self):
        super().__init__()
        self.enc = nn.Sequential(nn.Linear(5, 64), nn.Tanh(), nn.Linear(64, 64),
                                 nn.Tanh(), nn.Linear(64, LANES))
        d = 2 + LANES
        self.F = nn.Sequential(nn.Linear(d, 128), nn.Tanh(), nn.Linear(128, 128),
                               nn.Tanh(), nn.Linear(128, d))

    def code(self, snip, body):
        return self.enc(snip[body]).mean(1)             # amortized w0 (R^LANES)

    def rollout(self, snip, body, x0, v0, keep=False):
        s = torch.cat([torch.stack([x0, v0], 1), self.code(snip, body)], 1)
        xs, lanes = [], []
        for step in range(1, N_ROLL + 1):
            s = s + H * self.F(s)
            if keep:
                lanes.append(s[:, 2:].clone())
            if step in TARGETS:
                xs.append(s[:, :1])
        return (torch.cat(xs, 1), torch.stack(lanes, 1)) if keep else torch.cat(xs, 1)


def main():
    d = make_data(seed=0)
    snip = torch.from_numpy(d["snip"]); bdy = torch.from_numpy(d["body"])
    X = torch.from_numpy(d["qx"]); V = torch.from_numpy(d["qv"]); Y = torch.from_numpy(d["qy"])
    is_h = np.isin(d["body"], d["held"]); seen = np.where(~is_h)[0]
    torch.manual_seed(31); rng = np.random.default_rng(0)
    m = Model(); opt = torch.optim.Adam(m.parameters(), lr=1e-3)
    for step in range(STEPS):
        idx = seen[rng.integers(0, len(seen), 256)]
        pred = m.rollout(snip, bdy[idx], X[idx], V[idx])
        loss = nn.functional.mse_loss(pred, Y[idx])
        opt.zero_grad(); loss.backward(); opt.step()
        if step % 500 == 0:
            progress("31_wong_amortized", step, STEPS, loss=float(loss.detach()))
    m.eval()
    hi = np.where(is_h)[0]
    with torch.no_grad():
        mse = float(((m.rollout(snip, bdy[hi], X[hi], V[hi]) - Y[hi]) ** 2).mean())
    print(f"W1 held-out fit: {mse:.2e}")

    # W3/W4: decode true Q(t) from internal state w(t) on held-out bodies
    rng2 = np.random.default_rng(11); n = 600
    hb = rng2.choice(d["held"], n)
    x0 = rng2.uniform(*X_RANGE, n).astype(np.float32); v0 = rng2.uniform(-V_MAX, V_MAX, n).astype(np.float32)
    with torch.no_grad():
        _, lanes = m.rollout(snip, torch.from_numpy(hb), torch.from_numpy(x0),
                             torch.from_numpy(v0), keep=True)
    lanes = lanes.numpy()
    _, Qtrue = integ(x0.astype(float), v0.astype(float), d["Q0"][hb], keep_Q=True)
    Lf = lanes.reshape(-1, LANES); Qf = Qtrue.reshape(-1, 3)
    rs = [float(np.corrcoef(cross_val_predict(Ridge(1.0), Lf, Qf[:, j], cv=5), Qf[:, j])[0, 1]) for j in range(3)]
    # nonlinear decode (probe ladder): is Q(t) tracked illegibly through the recurrent F?
    rs_nl = [float(np.corrcoef(cross_val_predict(KNeighborsRegressor(8), Lf, Qf[:, j], cv=5), Qf[:, j])[0, 1]) for j in range(3)]
    Qhat = Ridge(1.0).fit(Lf, Qf).predict(Lf).reshape(n, N_ROLL, 3)
    dn = np.linalg.norm(Qhat, axis=-1); dec_drift = float(np.median(dn.std(1) / (dn.mean(1) + 1e-9)))
    q0 = Qtrue[:, 0] / np.linalg.norm(Qtrue[:, 0], 1, keepdims=True)
    qT = Qtrue[:, -1] / np.linalg.norm(Qtrue[:, -1], 1, keepdims=True)
    rot = float(np.median(np.degrees(np.arccos(np.clip((q0 * qT).sum(1), -1, 1)))))

    # W3b: amortized per-body code w0 -> Q0, linear (Phase I predicts now-legible)
    with torch.no_grad():
        W0 = m.enc(snip).mean(1).numpy()                 # (n_bodies, LANES) amortized code
    sb = np.array([i for i in range(len(d["Q0"])) if i not in d["held"]])
    lin0 = [float(np.corrcoef(cross_val_predict(Ridge(1.0), W0[sb], d["Q0"][sb, j], cv=5), d["Q0"][sb, j])[0, 1]) for j in range(3)]

    out = {"W1_mse": mse, "W3_decodeQt_r": rs, "W3_min_r": float(min(rs)),
           "W3_decodeQt_nonlinear_r": rs_nl, "W3_min_nl_r": float(min(rs_nl)),
           "true_rotation_deg": rot, "W4_decoded_norm_drift": dec_drift,
           "W3b_w0_Q0_linear_r": lin0}
    print(f"W3 decode Q(t) from internal state: LINEAR r={[f'{x:.3f}' for x in rs]} "
          f"(min {min(rs):.3f}); NONLINEAR r={[f'{x:.3f}' for x in rs_nl]} (min {min(rs_nl):.3f}); "
          f"true rot {rot:.0f}deg")
    print(f"W4 decoded |Q| drift {dec_drift:.3f} (small=conserved)")
    print(f"W3b amortized w0->Q0 LINEAR r={[f'{x:.2f}' for x in lin0]} "
          f"(vs v1 free-embedding ~0 — legible if high)")
    (RESULTS / "31_wong_amortized.json").write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.bar(range(3), rs, color="crimson"); ax.axhline(0.9, ls="--", c="k", lw=.8)
    ax.set_xticks(range(3)); ax.set_xticklabels(["Q0", "Q1", "Q2"])
    ax.set_ylabel("linear decode r of true Q(t) from internal state")
    ax.set_title(f"Wong v2 (amortized): does the state track the rotating charge? rot~{rot:.0f}deg")
    fig.tight_layout(); fig.savefig(RESULTS / "31_wong_amortized.png", dpi=140)
    print("saved results/31_wong_amortized.json + .png")


if __name__ == "__main__":
    main()
