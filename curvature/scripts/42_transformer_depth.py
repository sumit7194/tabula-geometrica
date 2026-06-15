"""Step 42 — thread D: the transformer toy-port + depth-of-emergence (cross-confirm Phronesis).

Phronesis (parallel LLM session) found legibility RISES with depth on Qwen3-4B: a latent the model
tracks is linearly readable at r=0.40 in layer 4 but r=0.92 by layer 36. Script 38 already showed
the legibility law survives a transformer ENCODER (free scrambles, amortized legible). This ports
the DEPTH observable: in an in-context transformer that infers a latent from K examples, does the
linear legibility of the true latent grow LAYER BY LAYER? And does a free-embedding control stay
scrambled?

Setup: script 35's abstract task (hidden p in R^2, frozen world g(p,x)->y). The amortized learner is
a depth-L transformer over the K example (x,y) tokens; after training, probe the mean-pooled rep at
EACH layer (linear ridge-cv decode of true p) -> a depth curve. Free control = per-object embedding.

Gates (pre-reg 2026-06-16):
  D1 depth-of-emergence: amortized last-layer legibility - first-layer > 0.2 (rises with depth).
  D2 transformer scramble (legibility law): free linear r < 0.4 AND nonlinear - linear > 0.15.
  D3 amortized legible & wins: amortized last-layer linear r > 0.6 and > free linear r + 0.3.
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
from curvlib import RESULTS, progress
from importlib import import_module
from sklearn.decomposition import PCA
from sklearn.linear_model import Ridge
from sklearn.neighbors import KNeighborsRegressor
from sklearn.model_selection import cross_val_predict
from torch import nn

s35 = import_module("35_legibility_scale")
XDIM, PDIM, KEX = s35.XDIM, s35.PDIM, s35.KEX
N_OBJ, STEPS, DEPTH, DMODEL = 256, 8000, 6, 128


class TFLearner(nn.Module):
    """In-context transformer: infer a code from K example tokens, answer a query."""
    def __init__(self, depth=DEPTH, d=DMODEL):
        super().__init__()
        self.embed = nn.Linear(XDIM + 1, d)
        self.layers = nn.ModuleList([
            nn.TransformerEncoderLayer(d, 4, 2 * d, batch_first=True, dropout=0.0, norm_first=True)
            for _ in range(depth)])
        self.head = nn.Sequential(nn.Linear(XDIM + d, d), nn.GELU(), nn.Linear(d, d), nn.GELU(), nn.Linear(d, 1))

    def layer_reps(self, ex_idx):
        """Mean-pooled token rep after the input embedding and after each layer: list of (B,d)."""
        h = self.embed(ex_idx)
        reps = [h.mean(1)]
        for layer in self.layers:
            h = layer(h)
            reps.append(h.mean(1))
        return reps

    def forward(self, ex, idx, x):
        c = self.layer_reps(ex[idx])[-1]
        return self.head(torch.cat([x, c[:, None, :].expand(-1, x.shape[1], -1)], -1))[..., 0]


class FreeLearner(nn.Module):
    def __init__(self, n_obj, d=DMODEL):
        super().__init__()
        self.emb = nn.Embedding(n_obj, d)
        self.head = nn.Sequential(nn.Linear(XDIM + d, d), nn.GELU(), nn.Linear(d, d), nn.GELU(), nn.Linear(d, 1))

    def code(self, idx):
        return self.emb(idx)

    def forward(self, ex, idx, x):
        c = self.emb(idx)
        return self.head(torch.cat([x, c[:, None, :].expand(-1, x.shape[1], -1)], -1))[..., 0]


def reduce16(C):
    """PCA-reduce to 16 dims so the probe ladder is valid (raw 128-d reps overfit ridge / curse kNN)."""
    k = min(16, C.shape[1], C.shape[0])
    return PCA(n_components=k).fit_transform(C)


def lin_r(C, P):
    C = reduce16(C)
    return float(np.mean([np.corrcoef(cross_val_predict(Ridge(1.0), C, P[:, j], cv=5), P[:, j])[0, 1]
                          for j in range(PDIM)]))


def nl_r(C, P):
    C = reduce16(C)
    return float(np.mean([np.corrcoef(cross_val_predict(KNeighborsRegressor(8), C, P[:, j], cv=5), P[:, j])[0, 1]
                          for j in range(PDIM)]))


def train(model, d, free=False):
    ex, qx, qy = d["ex"], d["qx"], d["qy"]
    rng = np.random.default_rng(0); opt = torch.optim.Adam(model.parameters(), lr=1e-3)
    tag = "free" if free else "tf"
    for step in range(STEPS):
        idx = torch.tensor(rng.integers(0, N_OBJ, 128))
        loss = nn.functional.mse_loss(model(ex, idx, qx[idx]), qy[idx])
        opt.zero_grad(); loss.backward(); opt.step()
        if step % 500 == 0:
            progress(f"42_{tag}", step, STEPS, loss=float(loss.detach()))
    model.eval()


def main():
    world = s35.World(width=128, seed=7)
    d = s35.make_data(world, N_OBJ, 64, seed=0)
    P = d["P"]

    torch.manual_seed(0)
    tf = TFLearner(); train(tf, d)
    with torch.no_grad():
        reps = tf.layer_reps(d["ex"][torch.arange(N_OBJ)])
    depth_curve = [lin_r(r.numpy(), P) for r in reps]   # legibility per layer (0=embedding .. DEPTH)

    torch.manual_seed(1)
    fr = FreeLearner(N_OBJ); train(fr, d, free=True)
    with torch.no_grad():
        Cf = fr.code(torch.arange(N_OBJ)).numpy()
    free_lin, free_nl = lin_r(Cf, P), nl_r(Cf, P)

    d1 = bool(depth_curve[-1] - depth_curve[1] > 0.2)   # vs first transformer layer (idx 1)
    d2 = bool(free_lin < 0.4 and free_nl - free_lin > 0.15)
    d3 = bool(depth_curve[-1] > 0.6 and depth_curve[-1] > free_lin + 0.3)
    out = {"depth_curve_linear_legibility": depth_curve, "free_linear": free_lin, "free_nonlinear": free_nl,
           "D1_depth_of_emergence": d1, "D2_transformer_scramble": d2, "D3_amortized_legible_wins": d3,
           "thread_D_confirmed": bool(d1 and d2 and d3)}
    print("legibility by layer (0=embed .. {}=last): {}".format(DEPTH, [f"{r:.2f}" for r in depth_curve]))
    print(f"D1 depth-of-emergence (last {depth_curve[-1]:.2f} - layer1 {depth_curve[1]:.2f} > 0.2): {d1}")
    print(f"D2 free scrambles (linear {free_lin:.2f}<0.4, nl {free_nl:.2f}-lin>0.15): {d2}")
    print(f"D3 amortized legible & wins (last {depth_curve[-1]:.2f}>0.6 & >free+0.3): {d3}")
    print(f"\nTHREAD D (transformer port + depth-of-emergence): {out['thread_D_confirmed']}")
    (RESULTS / "42_transformer_depth.json").write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.plot(range(len(depth_curve)), depth_curve, "o-", color="seagreen", label="amortized transformer (in-context)")
    ax.axhline(free_lin, ls="--", color="crimson", label=f"free embedding linear ({free_lin:.2f}, scrambled)")
    ax.axhline(free_nl, ls=":", color="gray", label=f"free embedding nonlinear ({free_nl:.2f}, info present)")
    ax.set_xlabel("layer  (0 = input embedding,  last = output)"); ax.set_ylabel("linear legibility r of true latent")
    ax.set_ylim(0, 1); ax.set_title("depth-of-emergence: legibility rises layer by layer (cross-confirms Phronesis)")
    ax.legend(fontsize=8); fig.tight_layout(); fig.savefig(RESULTS / "42_transformer_depth.png", dpi=140)
    print("saved results/42_transformer_depth.json + .png")


if __name__ == "__main__":
    main()
