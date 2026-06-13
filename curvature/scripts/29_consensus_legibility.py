"""Step 29 — Phase I: does AGREEMENT/recurrence select code LEGIBILITY?

A shared encoder infers a per-body code c from K trajectory snippets; a shared
head rolls out dynamics from (x, v, c). We vary ONLY the charge distribution and
read out whether c is LINEARLY decodable to the true charge (legible) or merely
nonlinearly decodable (scrambled — the Phase C signature). Arms A/B/C isolate
recurrence from discreteness; D is the free-embedding (Phase C) reference.
Pre-registration 2026-06-15. Fast (CPU); self-contained.
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
from curvlib import RESULTS, WELL_DEPTH, WELL_WIDTH
from sklearn.linear_model import Ridge
from sklearn.neighbors import KNeighborsRegressor
from sklearn.model_selection import cross_val_predict
from torch import nn

TIMES = (1.0, 2.0, 3.0)
H, N_ROLL = 0.1, 30
TARGETS = [int(round(t / H)) for t in TIMES]
FIELD = dict(amp=0.35, c=0.8)
N_BODIES, K_SNIP, PER_BODY = 80, 6, 120
D_CODE, STEPS = 4, 8000


def accel(x, q):
    e = np.exp(-(x**2) / (2 * WELL_WIDTH**2))
    return -WELL_DEPTH * x * e / WELL_WIDTH**2 + q * FIELD["amp"] * np.exp(
        -((x - FIELD["c"]) ** 2) / 2)


def integrate(x0, v0, q, dt=0.01):
    n = int(round(TIMES[-1] / dt))
    grab = {int(round(t / dt)): i for i, t in enumerate(TIMES)}
    x, v = x0.astype(float).copy(), v0.astype(float).copy()
    out = np.empty((len(x0), len(TIMES)))
    for s in range(1, n + 1):
        k1x, k1v = v, accel(x, q)
        k2x, k2v = v + .5 * dt * k1v, accel(x + .5 * dt * k1x, q)
        k3x, k3v = v + .5 * dt * k2v, accel(x + .5 * dt * k2x, q)
        k4x, k4v = v + dt * k3v, accel(x + dt * k3x, q)
        x = x + dt / 6 * (k1x + 2 * k2x + 2 * k3x + k4x)
        v = v + dt / 6 * (k1v + 2 * k2v + 2 * k3v + k4v)
        if s in grab:
            out[:, grab[s]] = x
    return out


def charges(arm, rng):
    if arm == "A":   # recurring-discrete: 8-value alphabet, many bodies per value
        alpha = np.linspace(-1, 1, 8)
        return alpha[rng.integers(0, 8, N_BODIES)]
    if arm == "B":   # unique-discrete: distinct quantized values, ~no recurrence
        grid = np.round(np.linspace(-1, 1, 256), 4)
        return rng.choice(grid, N_BODIES, replace=False)
    return rng.uniform(-1, 1, N_BODIES)  # C / D: unique-continuous


def make_data(arm, rng):
    qm = charges(arm, rng)
    snip, qx, qv, qy, body = [], [], [], [], []
    for i in range(N_BODIES):
        sx = rng.uniform(-2.5, 2.5, K_SNIP); sv = rng.uniform(-.3, .3, K_SNIP)
        sp = integrate(sx, sv, qm[i])
        snip.append(np.concatenate([sx[:, None], sv[:, None], sp], 1))  # (K,5)
        x0 = rng.uniform(-2.5, 2.5, PER_BODY); v0 = rng.uniform(-.3, .3, PER_BODY)
        qy.append(integrate(x0, v0, qm[i])); qx.append(x0); qv.append(v0)
        body.append(np.full(PER_BODY, i))
    return {"qm": qm, "snip": np.array(snip, dtype=np.float32),
            "qx": np.concatenate(qx).astype(np.float32),
            "qv": np.concatenate(qv).astype(np.float32),
            "qy": np.concatenate(qy).astype(np.float32),
            "body": np.concatenate(body).astype(np.int64)}


class Model(nn.Module):
    def __init__(self, free_emb):
        super().__init__()
        self.free = free_emb
        if free_emb:
            self.emb = nn.Embedding(N_BODIES, D_CODE)
        else:
            self.enc = nn.Sequential(nn.Linear(5, 64), nn.Tanh(), nn.Linear(64, 64),
                                     nn.Tanh(), nn.Linear(64, D_CODE))
        self.F = nn.Sequential(nn.Linear(2 + D_CODE, 128), nn.Tanh(),
                               nn.Linear(128, 128), nn.Tanh(), nn.Linear(128, 2))

    def code(self, snip, body):
        if self.free:
            return self.emb(body)
        return self.enc(snip[body]).mean(1)  # mean-pool K snippets -> R^D_CODE

    def forward(self, snip, body, x0, v0):
        c = self.code(snip, body)
        s = torch.stack([x0, v0], 1)
        xs = []
        for step in range(1, N_ROLL + 1):
            s = s + H * self.F(torch.cat([s, c], 1))
            if step in TARGETS:
                xs.append(s[:, :1])
        return torch.cat(xs, 1)


def run_arm(arm, seed=0):
    rng = np.random.default_rng(seed)
    d = make_data(arm, rng)
    torch.manual_seed(29)
    m = Model(free_emb=(arm == "D"))
    opt = torch.optim.Adam(m.parameters(), lr=1e-3)
    snip = torch.from_numpy(d["snip"])
    bdy = torch.from_numpy(d["body"]); X = torch.from_numpy(d["qx"])
    V = torch.from_numpy(d["qv"]); Y = torch.from_numpy(d["qy"])
    for step in range(STEPS):
        idx = rng.integers(0, len(X), 256)
        pred = m(snip, bdy[idx], X[idx], V[idx])
        loss = nn.functional.mse_loss(pred, Y[idx])
        opt.zero_grad(); loss.backward(); opt.step()
    m.eval()
    with torch.no_grad():
        C = m.code(snip, torch.arange(N_BODIES)).numpy()  # per-body code
    q = d["qm"]
    lin = float(np.corrcoef(cross_val_predict(Ridge(1.0), C, q, cv=5), q)[0, 1])
    nl = float(np.corrcoef(
        cross_val_predict(KNeighborsRegressor(5), C, q, cv=5), q)[0, 1])
    print(f"  arm {arm}: fit {float(loss):.2e} | LINEAR r={lin:.3f} (legible) "
          f"| nonlinear r={nl:.3f} (info) | n_distinct_q={len(np.unique(q))}")
    return {"arm": arm, "fit_mse": float(loss), "linear_r": lin, "nonlinear_r": nl,
            "n_distinct_q": int(len(np.unique(q)))}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=3)
    args = ap.parse_args()
    out = {}
    for arm in ("A", "B", "C", "D"):
        rs = [run_arm(arm, s) for s in range(args.seeds)]
        out[arm] = {"linear_r": float(np.mean([r["linear_r"] for r in rs])),
                    "linear_r_std": float(np.std([r["linear_r"] for r in rs])),
                    "nonlinear_r": float(np.mean([r["nonlinear_r"] for r in rs])),
                    "fit_mse": float(np.mean([r["fit_mse"] for r in rs])),
                    "n_distinct_q": rs[0]["n_distinct_q"]}
    names = {"A": "amortized recurring-discrete", "B": "amortized unique-discrete",
             "C": "amortized unique-continuous", "D": "free-embedding (Phase C ref)"}
    print("\n=== consensus -> legibility (mean over seeds) ===")
    for a in "ABCD":
        print(f"{a} {names[a]:32s} linear_r={out[a]['linear_r']:.3f}"
              f"±{out[a]['linear_r_std']:.3f}  nonlinear_r={out[a]['nonlinear_r']:.3f}")
    dAB = out["A"]["linear_r"] - out["B"]["linear_r"]
    dBC = out["B"]["linear_r"] - out["C"]["linear_r"]
    print(f"\nrecurrence effect (A-B linear_r) = {dAB:+.3f} | "
          f"discreteness effect (B-C) = {dBC:+.3f}")
    print("consensus SUPPORTED" if dAB > 0.1 and abs(dBC) < dAB
          else "consensus NOT cleanly supported (see arms)")
    (RESULTS / "29_consensus.json").write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(figsize=(8, 5))
    xs = np.arange(4)
    ax.bar(xs - .2, [out[a]["linear_r"] for a in "ABCD"], .4, label="linear (legible)")
    ax.bar(xs + .2, [out[a]["nonlinear_r"] for a in "ABCD"], .4, label="nonlinear (info)")
    ax.set_xticks(xs); ax.set_xticklabels(["A rec-disc", "B uniq-disc", "C uniq-cont", "D free-emb"])
    ax.set_ylabel("decode r vs true charge"); ax.legend()
    ax.set_title("consensus -> legibility: is the code linearly readable?")
    fig.tight_layout(); fig.savefig(RESULTS / "29_consensus.png", dpi=140)
    print(f"saved results/29_consensus.json + .png")


if __name__ == "__main__":
    main()
