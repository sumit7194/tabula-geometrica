"""Step 34 — EDGE 1: close the legibility-law third-leg gap.

Leg 3 (orthogonal update) restored conservation fully but legibility only ~80% of the static
ceiling, with a small fit cost (the rotation generator was a shallow MLP optimized for
trajectory fit, not for tracking the charge). This gives it one clean shot: a RICHER rotation
generator (deeper/wider) + longer training. Does legibility reach the static ceiling while
keeping |w| conserved? Pre-reg: orthogonal-rich legibility >= 0.85 x static ceiling.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
import torch
from curvlib import RESULTS, V_MAX, X_RANGE, progress
from importlib import import_module
from sklearn.linear_model import Ridge
from sklearn.model_selection import cross_val_predict
from torch import nn

b = import_module("33_legibility_structure")
H, N_ROLL, TARGETS = b.H, b.N_ROLL, b.TARGETS
STEPS = 30000


class RichModel(nn.Module):
    """Same as 33.Model but with a richer orthogonal rotation generator."""
    def __init__(self, mode):
        super().__init__()
        self.mode = mode
        self.enc = nn.Sequential(nn.Linear(5, 64), nn.Tanh(), nn.Linear(64, 64), nn.Tanh(), nn.Linear(64, 3))
        self.xv = nn.Sequential(nn.Linear(5, 64), nn.Tanh(), nn.Linear(64, 64), nn.Tanh(), nn.Linear(64, 2))
        self.wu = nn.Sequential(nn.Linear(5, 128), nn.Tanh(), nn.Linear(128, 128), nn.Tanh(),
                                nn.Linear(128, 128), nn.Tanh(), nn.Linear(128, 3))

    def code(self, snip, body):
        return self.enc(snip[body]).mean(1)

    def rollout(self, snip, body, x0, v0, keep=False):
        w = self.code(snip, body); xv = torch.stack([x0, v0], 1)
        xs, ws = [], []
        for step in range(1, N_ROLL + 1):
            s = torch.cat([xv, w], 1)
            xv = xv + H * self.xv(s)
            if self.mode == "orthogonal":
                w = torch.bmm(torch.linalg.matrix_exp(b.skew(self.wu(s) * H)), w.unsqueeze(-1)).squeeze(-1)
            else:
                w = w + H * self.wu(s)
            if keep:
                ws.append(w.clone())
            if step in TARGETS:
                xs.append(xv[:, :1])
        return (torch.cat(xs, 1), torch.stack(ws, 1)) if keep else torch.cat(xs, 1)


def run(rotate, mode, seed=0):
    d = b.make_data(rotate, seed=seed)
    snip = torch.from_numpy(d["snip"]); bdy = torch.from_numpy(d["body"])
    X = torch.from_numpy(d["qx"]); V = torch.from_numpy(d["qv"]); Y = torch.from_numpy(d["qy"])
    seen = np.where(~np.isin(d["body"], d["held"]))[0]
    torch.manual_seed(34); rng = np.random.default_rng(0)
    m = RichModel(mode); opt = torch.optim.Adam(m.parameters(), lr=1e-3)
    tag = f"{'dyn' if rotate else 'stat'}_{mode}_rich"
    for step in range(STEPS):
        idx = seen[rng.integers(0, len(seen), 256)]
        loss = nn.functional.mse_loss(m.rollout(snip, bdy[idx], X[idx], V[idx]), Y[idx])
        opt.zero_grad(); loss.backward(); opt.step()
        if step % 500 == 0:
            progress(f"34_{tag}", step, STEPS, loss=float(loss.detach()))
    m.eval()
    rng2 = np.random.default_rng(11); n = 600
    hb = rng2.choice(d["held"], n)
    x0 = rng2.uniform(*X_RANGE, n).astype(np.float32); v0 = rng2.uniform(-V_MAX, V_MAX, n).astype(np.float32)
    qy = b.integ(x0.astype(float), v0.astype(float), d["q0"][hb], rotate)
    with torch.no_grad():
        pred, ws = m.rollout(snip, torch.from_numpy(hb), torch.from_numpy(x0), torch.from_numpy(v0), keep=True)
        w1 = float(((pred - torch.from_numpy(qy.astype(np.float32))) ** 2).mean())
    ws = ws.numpy()
    _, qt = b.integ(x0.astype(float), v0.astype(float), d["q0"][hb], rotate, keep_q=True)
    L = ws.reshape(-1, 3); Q = qt.reshape(-1, 3)
    lin = [float(np.corrcoef(cross_val_predict(Ridge(1.0), L, Q[:, j], cv=5), Q[:, j])[0, 1]) for j in range(3)]
    wn = np.linalg.norm(ws, axis=-1); drift = float(np.median(wn.std(1) / (wn.mean(1) + 1e-9)))
    print(f"[{tag}] W1={w1:.2e} legible(mean)={np.mean(lin):.3f} |w|drift={drift:.3f}")
    return {"tag": tag, "W1": w1, "legible_mean": float(np.mean(lin)), "drift": drift}


def main():
    out = {r["tag"]: r for r in (run(True, "orthogonal"), run(False, "generic"))}
    do_, sg = out["dyn_orthogonal_rich"], out["stat_generic_rich"]
    ratio = do_["legible_mean"] / sg["legible_mean"]
    print(f"\nrich-orthogonal legible {do_['legible_mean']:.3f} vs static ceiling {sg['legible_mean']:.3f} "
          f"= {ratio:.2f}x ceiling; |w|drift {do_['drift']:.3f}")
    print(f"LEG 3 {'CONFIRMED (reaches ceiling)' if ratio >= 0.85 and do_['drift'] < 0.05 else 'still partial'}")
    out["ceiling_ratio"] = ratio
    (RESULTS / "34_legibility_close.json").write_text(json.dumps(out, indent=1))
    print("saved results/34_legibility_close.json")


if __name__ == "__main__":
    main()
