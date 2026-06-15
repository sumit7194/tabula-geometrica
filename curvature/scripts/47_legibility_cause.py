"""Step 47 — discriminator: WHAT actually scrambles a free code? map-nonlinearity vs charge-irrelevance.

Script 46 falsified sign and coupling-type (all four cells legible). By elimination the Phase C /
Phase I scramble comes from either (a) the NONLINEARITY of the charge->behavior map, or (b) the
NEUTRAL+CHARGED MIX (bodies where the charge is irrelevant get arbitrary embeddings). Test both in
ONE harness, decoding the underlying charge c from the free embedding:

  control      clean uniform c, smooth LINEAR coupling (= script 46)            -> expect LEGIBLE
  neutral_mix  half the bodies have c=0, half spread (the Phase C structure)    -> tests (b)
  nonlinear    clean uniform c, but behavior depends on c only through two
               NON-MONOTONE channels (sin,cos)(c) — injective (5 rad < 2pi) so c
               is still identifiable, but c is a NONLINEAR function of what's
               behaviorally used (the Phase I mechanism)                         -> tests (a)

Decode c: linear ridge (legibility) + kNN (info presence). A scramble = linear LOW, nonlinear HIGH.

Pre-reg (2026-06-16):
  M1 control legible: linear > 0.9.
  M2 nonlinear scrambles: linear < 0.5 AND nonlinear > 0.8 (the Phase-I-style scramble reproduced).
  M3 mix effect: report neutral_mix linear; scramble if < 0.5 while nonlinear > 0.8.
  Conclusion = whichever arm(s) reproduce the scramble.
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
N_BODIES, PER_BODY, STEPS, HELD, EMB_DIM = 200, 120, 7000, 20, 4  # N bumped: 32-body decode was underpowered


def accel(x, y, vx, vy, s_scal, s_mag):
    eg = np.exp(-(x**2 + y**2) / (2 * WELL_WIDTH**2))
    axg = -WELL_DEPTH * x * eg / WELL_WIDTH**2
    ayg = -WELL_DEPTH * y * eg / WELL_WIDTH**2
    dx, dy = x - SCALAR_CENTER[0], y - SCALAR_CENTER[1]
    es = np.exp(-(dx**2 + dy**2) / (2 * WELL_WIDTH**2))
    axs = -SCALAR_DEPTH * dx * es / WELL_WIDTH**2
    ays = -SCALAR_DEPTH * dy * es / WELL_WIDTH**2
    bx, by = x - B_CENTER[0], y - B_CENTER[1]
    B = B_AMP * np.exp(-(bx**2 + by**2) / 2.0)
    return axg + s_scal * axs + s_mag * vy * B, ayg + s_scal * ays - s_mag * vx * B


def integrate(x0, y0, vx0, vy0, s_scal, s_mag, dt=0.01):
    n_steps = int(round(TRAJ_TIMES[-1] / dt))
    grab = {int(round(t / dt)): i for i, t in enumerate(TRAJ_TIMES)}
    x, y, vx, vy = (a.astype(float).copy() for a in (x0, y0, vx0, vy0))
    out = np.empty((len(x0), len(TRAJ_TIMES), 2))
    for step in range(1, n_steps + 1):
        def rk(xx, yy, ux, uy):
            ax, ay = accel(xx, yy, ux, uy, s_scal, s_mag)
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


def _random_world(c, seed=3):
    """Fixed random 2-layer MLP R^2 -> R^2 (Phase-I-style nonlinear world) mapping charge->couplings."""
    torch.manual_seed(seed)
    g = nn.Sequential(nn.Linear(2, 32), nn.Tanh(), nn.Linear(32, 32), nn.Tanh(), nn.Linear(32, 2))
    with torch.no_grad():
        return g(torch.from_numpy(c.astype(np.float32))).numpy()


def body_couplings(arm, rng):
    """Return (c_body (N,2), s_scal (N,), s_mag (N,)): the 2-d charge and how it enters dynamics.
    All arms: a 2-d charge drives (scalar-coupling, magnetic-coupling). What differs is the MAP."""
    c = rng.uniform(-1.2, 1.2, (N_BODIES, 2))
    if arm == "control":                         # LINEAR map: couplings = the charge itself
        return c, c[:, 0].copy(), c[:, 1].copy()
    if arm == "neutral_mix":                     # linear map, but half the bodies are NEUTRAL (charge irrelevant)
        neutral = rng.permutation(N_BODIES)[: N_BODIES // 2]
        c[neutral] = 0.0
        return c, c[:, 0].copy(), c[:, 1].copy()
    f = _random_world(c)                          # NONLINEAR map: a random MLP world (Phase I mechanism)
    return c, f[:, 0], f[:, 1]


def make_data(arm, seed=0):
    rng = np.random.default_rng(seed)
    c_body, s_scal, s_mag = body_couplings(arm, rng)
    held = np.arange(N_BODIES - HELD, N_BODIES)
    body, X, Y = [], [], []
    for i in range(N_BODIES):
        x0 = rng.uniform(-2.5, 2.5, PER_BODY); y0 = rng.uniform(-2.5, 2.5, PER_BODY)
        vx0 = rng.uniform(-V_MAX, V_MAX, PER_BODY); vy0 = rng.uniform(-V_MAX, V_MAX, PER_BODY)
        tg = integrate(x0, y0, vx0, vy0, np.full(PER_BODY, s_scal[i]), np.full(PER_BODY, s_mag[i])).reshape(PER_BODY, -1)
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


def train_decode(arm):
    d = make_data(arm)
    torch.manual_seed(0); rng = np.random.default_rng(0)
    body, X, Y = d["train"]; m = Force(N_BODIES); opt = torch.optim.Adam(m.parameters(), lr=1e-3)
    for step in range(STEPS):
        idx = rng.integers(0, len(X), 512)
        loss = nn.functional.mse_loss(m(torch.from_numpy(X[idx]), torch.from_numpy(body[idx])),
                                      torch.from_numpy(Y[idx]))
        opt.zero_grad(); loss.backward(); opt.step()
        if step % 500 == 0:
            progress(f"47_{arm}", step, STEPS, loss=float(loss.detach()))
    seen = np.setdiff1d(np.arange(N_BODIES), d["held"])
    emb = m.emb(torch.from_numpy(seen.astype(np.int64))).detach().numpy()
    c = d["c_body"][seen]                                          # (n_seen, 2)
    lin = float(np.mean([np.corrcoef(cross_val_predict(Ridge(1.0), emb, c[:, j], cv=5), c[:, j])[0, 1]
                         for j in range(c.shape[1])]))
    nl = float(np.mean([np.corrcoef(cross_val_predict(KNeighborsRegressor(5), emb, c[:, j], cv=5), c[:, j])[0, 1]
                        for j in range(c.shape[1])]))
    return {"linear": lin, "nonlinear": nl, "train_mse": float(loss.detach())}


def main():
    arms = {}
    for arm in ("control", "neutral_mix", "nonlinear"):
        r = train_decode(arm); arms[arm] = r
        print(f"{arm:12s}: linear {r['linear']:.2f} | nonlinear {r['nonlinear']:.2f} | mse {r['train_mse']:.1e}")

    def scrambled(a):
        return arms[a]["linear"] < 0.5 and arms[a]["nonlinear"] > 0.8
    m1 = bool(arms["control"]["linear"] > 0.9)
    m2 = bool(scrambled("nonlinear"))
    m3 = bool(scrambled("neutral_mix"))
    cause = [name for name, ok in (("map_nonlinearity", m2), ("charge_irrelevance_mix", m3)) if ok]
    out = {"arms": arms, "M1_control_legible": m1, "M2_nonlinear_scrambles": m2,
           "M3_mix_scrambles": m3, "scramble_cause": cause}
    print(f"\nM1 control legible (>0.9): {m1}")
    print(f"M2 nonlinear-map scrambles (lin<0.5, nl>0.8): {m2}")
    print(f"M3 neutral-mix scrambles (lin<0.5, nl>0.8): {m3}")
    print(f"SCRAMBLE CAUSE -> {cause if cause else 'neither reproduced the scramble'}")
    (RESULTS / "47_legibility_cause.json").write_text(json.dumps(out, indent=1))

    names = ["control", "neutral_mix", "nonlinear"]
    x = np.arange(3)
    fig, ax = plt.subplots(figsize=(7.5, 5))
    ax.bar(x - 0.2, [arms[a]["linear"] for a in names], 0.4, label="linear (legibility)", color="seagreen")
    ax.bar(x + 0.2, [arms[a]["nonlinear"] for a in names], 0.4, label="nonlinear (info present)", color="gray")
    ax.axhline(0.5, ls=":", color="crimson"); ax.set_xticks(x); ax.set_xticklabels(names)
    ax.set_ylabel("decode r of underlying charge"); ax.set_ylim(0, 1); ax.legend()
    ax.set_title("what scrambles a free code? linear-low + nonlinear-high = scramble")
    fig.tight_layout(); fig.savefig(RESULTS / "47_legibility_cause.png", dpi=140)
    print("saved results/47_legibility_cause.json + .png")


if __name__ == "__main__":
    main()
