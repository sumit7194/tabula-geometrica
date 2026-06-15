"""Step 35 — EDGE 3: does the legibility law hold at SCALE and OUT of physics?

The law so far lives in small physics toys. This tests its core leg (amortize -> legible /
free-embedding -> scrambled) in a deliberately NON-physics, abstract task, across model sizes —
to show it's a property of HOW codes are learned, not of charge/geometry.

Abstract task: each "object" i has a hidden property p_i in R^2. A FIXED random "world
function" g (a frozen random MLP) maps (p_i, x) -> y for query inputs x. The model sees K
example (x,y) pairs of an object and predicts y on new x — using either an AMORTIZED code
(an encoder infers a code from the examples) or a FREE per-object embedding. We read out the
linear decodability of the true p_i from the code. Pre-reg: amortized linear_r >> free, and
the gap PERSISTS (does not wash out) as width and #objects grow.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
import torch
from curvlib import RESULTS, progress
from sklearn.linear_model import Ridge
from sklearn.neighbors import KNeighborsRegressor
from sklearn.model_selection import cross_val_predict
from torch import nn

XDIM, PDIM, KEX = 4, 2, 12


class World(nn.Module):
    """Frozen random world function g(p, x) -> y (the abstract 'physics')."""
    def __init__(self, width=128, seed=0):
        super().__init__()
        torch.manual_seed(seed)
        self.net = nn.Sequential(nn.Linear(PDIM + XDIM, width), nn.GELU(),
                                 nn.Linear(width, width), nn.GELU(), nn.Linear(width, 1))
        for q in self.parameters():
            q.requires_grad_(False)

    def forward(self, p, x):
        return self.net(torch.cat([p, x], -1))[..., 0]


def make_data(world, n_obj, per_obj, seed):
    rng = np.random.default_rng(seed)
    P = rng.uniform(-1, 1, (n_obj, PDIM)).astype(np.float32)
    with torch.no_grad():
        # K example pairs per object (for the encoder) + train/eval query pairs
        def pairs(m):
            x = torch.tensor(rng.uniform(-1, 1, (n_obj, m, XDIM)).astype(np.float32))
            y = world(torch.tensor(P)[:, None, :].expand(-1, m, -1), x)
            return x, y
        ex_x, ex_y = pairs(KEX)
        qx, qy = pairs(per_obj)
    return {"P": P, "ex": torch.cat([ex_x, ex_y[..., None]], -1),  # (n_obj,K,XDIM+1)
            "qx": qx, "qy": qy}


class Learner(nn.Module):
    def __init__(self, n_obj, width, mode):
        super().__init__()
        self.mode = mode
        cdim = 16
        if mode == "free":
            self.code_emb = nn.Embedding(n_obj, cdim)
        else:  # amortized: encode the K example pairs
            self.enc = nn.Sequential(nn.Linear(XDIM + 1, width), nn.GELU(),
                                     nn.Linear(width, width), nn.GELU(), nn.Linear(width, cdim))
        self.head = nn.Sequential(nn.Linear(XDIM + cdim, width), nn.GELU(),
                                  nn.Linear(width, width), nn.GELU(), nn.Linear(width, 1))

    def code(self, ex, idx):
        return self.code_emb(idx) if self.mode == "free" else self.enc(ex[idx]).mean(1)

    def forward(self, ex, idx, x):
        c = self.code(ex, idx)
        cc = c[:, None, :].expand(-1, x.shape[1], -1)
        return self.head(torch.cat([x, cc], -1))[..., 0]


def run(width, n_obj, mode, steps=6000, seed=0):
    world = World(width=128, seed=7)
    d = make_data(world, n_obj, per_obj=64, seed=seed)
    ex = d["ex"]; qx = d["qx"]; qy = d["qy"]
    torch.manual_seed(35); rng = np.random.default_rng(0)
    m = Learner(n_obj, width, mode); opt = torch.optim.Adam(m.parameters(), lr=2e-3)
    for step in range(steps):
        idx = torch.tensor(rng.integers(0, n_obj, 128))
        loss = nn.functional.mse_loss(m(ex, idx, qx[idx]), qy[idx])
        opt.zero_grad(); loss.backward(); opt.step()
        if step % 400 == 0:
            progress(f"35_{mode}_w{width}_n{n_obj}", step, steps, loss=float(loss.detach()))
    m.eval()
    with torch.no_grad():
        C = m.code(ex, torch.arange(n_obj)).numpy()
    P = d["P"]
    lin = np.mean([np.corrcoef(cross_val_predict(Ridge(1.0), C, P[:, j], cv=5), P[:, j])[0, 1] for j in range(PDIM)])
    nl = np.mean([np.corrcoef(cross_val_predict(KNeighborsRegressor(8), C, P[:, j], cv=5), P[:, j])[0, 1] for j in range(PDIM)])
    return {"width": width, "n_obj": n_obj, "mode": mode,
            "linear_r": float(lin), "nonlinear_r": float(nl)}


def main():
    out = []
    configs = [(64, 64), (256, 64), (256, 512)]   # (width, n_objects): small -> larger
    for w, n in configs:
        a = run(w, n, "amortized"); f = run(w, n, "free")
        gap = a["linear_r"] - f["linear_r"]
        out.append({"width": w, "n_obj": n, "amortized_linear": a["linear_r"],
                    "free_linear": f["linear_r"], "free_nonlinear": f["nonlinear_r"], "gap": gap})
        print(f"w={w} n={n}: amortized linear={a['linear_r']:.3f} | free linear={f['linear_r']:.3f} "
              f"(nonlinear {f['nonlinear_r']:.3f}) | GAP={gap:+.3f}")
    persists = all(r["gap"] > 0.2 for r in out)
    print(f"\nNON-PHYSICS + SCALE: amortize>free gap persists across all sizes: {persists}")
    print(f"  -> legibility law {'GENERALIZES' if persists else 'does NOT cleanly generalize'}")
    (RESULTS / "35_legibility_scale.json").write_text(json.dumps(out, indent=1))
    print("saved results/35_legibility_scale.json")


if __name__ == "__main__":
    main()
