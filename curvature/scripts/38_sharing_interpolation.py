"""Step 38 — testing the Phronesis LLM findings back in the toy (credit: parallel session).

Their LLM result: pretrained transformers have NO free-embedding regime — parametric knowledge
is amortized through shared weights, so everything is linearly legible (no scramble). Suggested
two toy tests, done here in ONE harness on the abstract non-physics task (script 29's World):
  (#2) INTERPOLATE sharing: code = (1-lam)*free_embedding + lam*amortized_encoder; sweep lam.
       How much sharing flips scrambled->legible? (predicts why all-shared LLMs are legible)
  (#1) TRANSFORMER rung: does free still scramble / amortized still legible with a transformer
       set-encoder (not MLP)? If free still scrambles, the LLM null is purely 'no free regime'.
Pre-registration 2026-06-16.
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
from sklearn.linear_model import Ridge
from sklearn.neighbors import KNeighborsRegressor
from sklearn.model_selection import cross_val_predict
from torch import nn

s29 = import_module("35_legibility_scale")   # reuse World + make_data (the abstract task)
XDIM, PDIM, KEX, CDIM = s29.XDIM, s29.PDIM, s29.KEX, 16


class Interp(nn.Module):
    def __init__(self, n_obj, lam, enc="mlp", width=128):
        super().__init__()
        self.lam = lam; self.enc_type = enc
        self.free = nn.Embedding(n_obj, CDIM)
        if enc == "mlp":
            self.enc = nn.Sequential(nn.Linear(XDIM + 1, width), nn.GELU(),
                                     nn.Linear(width, width), nn.GELU(), nn.Linear(width, CDIM))
        else:  # transformer set-encoder over the K example (x,y) tokens
            self.proj = nn.Linear(XDIM + 1, width)
            layer = nn.TransformerEncoderLayer(width, 4, 2 * width, batch_first=True, dropout=0.0, norm_first=True)
            self.tf = nn.TransformerEncoder(layer, 2); self.to_c = nn.Linear(width, CDIM)
        self.head = nn.Sequential(nn.Linear(XDIM + CDIM, width), nn.GELU(),
                                  nn.Linear(width, width), nn.GELU(), nn.Linear(width, 1))

    def amortized(self, ex, idx):
        e = ex[idx]
        if self.enc_type == "mlp":
            return self.enc(e).mean(1)
        return self.to_c(self.tf(self.proj(e)).mean(1))

    def code(self, ex, idx):
        c = (1 - self.lam) * self.free(idx)
        if self.lam > 0:
            c = c + self.lam * self.amortized(ex, idx)
        return c

    def forward(self, ex, idx, x):
        c = self.code(ex, idx)
        return self.head(torch.cat([x, c[:, None, :].expand(-1, x.shape[1], -1)], -1))[..., 0]


def run(lam, enc, n_obj=256, steps=6000, tag=""):
    world = s29.World(width=128, seed=7)
    d = s29.make_data(world, n_obj, per_obj=64, seed=0)
    ex, qx, qy = d["ex"], d["qx"], d["qy"]
    torch.manual_seed(38); rng = np.random.default_rng(0)
    m = Interp(n_obj, lam, enc); opt = torch.optim.Adam(m.parameters(), lr=2e-3)
    for step in range(steps):
        idx = torch.tensor(rng.integers(0, n_obj, 128))
        loss = nn.functional.mse_loss(m(ex, idx, qx[idx]), qy[idx])
        opt.zero_grad(); loss.backward(); opt.step()
        if step % 500 == 0:
            progress(f"38_{tag}", step, steps, loss=float(loss.detach()))
    m.eval()
    with torch.no_grad():
        C = m.code(ex, torch.arange(n_obj)).numpy()
    P = d["P"]
    lin = float(np.mean([np.corrcoef(cross_val_predict(Ridge(1.0), C, P[:, j], cv=5), P[:, j])[0, 1] for j in range(PDIM)]))
    nl = float(np.mean([np.corrcoef(cross_val_predict(KNeighborsRegressor(8), C, P[:, j], cv=5), P[:, j])[0, 1] for j in range(PDIM)]))
    return lin, nl


def main():
    out = {"interpolation": [], "transformer": {}}
    print("#2 sharing interpolation (MLP encoder):")
    for lam in (0.0, 0.25, 0.5, 0.75, 1.0):
        lin, nl = run(lam, "mlp", tag=f"lam{lam}")
        out["interpolation"].append({"lam": lam, "linear": lin, "nonlinear": nl})
        print(f"  lam={lam:.2f} (free->amortized): linear={lin:.3f}  nonlinear={nl:.3f}")
    print("#1 transformer rung (free vs amortized, transformer encoder):")
    for lam in (0.0, 1.0):
        lin, nl = run(lam, "transformer", tag=f"tf_lam{lam}")
        out["transformer"][f"lam{lam}"] = {"linear": lin, "nonlinear": nl}
        print(f"  lam={lam:.2f} transformer: linear={lin:.3f}  nonlinear={nl:.3f}")

    lams = [r["lam"] for r in out["interpolation"]]
    lins = [r["linear"] for r in out["interpolation"]]
    flip = lins[-1] - lins[0]
    tf0 = out["transformer"]["lam0.0"]; tf1 = out["transformer"]["lam1.0"]
    out["sharing_flips_legibility"] = bool(flip > 0.2)
    out["transformer_free_scrambles"] = bool(tf0["linear"] < 0.4 and tf0["nonlinear"] - tf0["linear"] > 0.15)
    print(f"\nSharing flips legibility (lin {lins[0]:.2f}->{lins[-1]:.2f}, +{flip:.2f}): {out['sharing_flips_legibility']}")
    print(f"Transformer: free linear {tf0['linear']:.2f}/nl {tf0['nonlinear']:.2f} (scrambles={out['transformer_free_scrambles']}); "
          f"amortized linear {tf1['linear']:.2f} (legible)")
    (RESULTS / "38_sharing.json").write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.plot(lams, lins, "o-", color="seagreen", label="linear (legibility)")
    ax.plot(lams, [r["nonlinear"] for r in out["interpolation"]], "s--", color="gray", label="nonlinear (info)")
    ax.set_xlabel("lambda  (0 = free embedding,  1 = amortized encoder)")
    ax.set_ylabel("decode r of true property"); ax.set_ylim(0, 1)
    ax.set_title("how much SHARING flips scrambled -> legible?")
    ax.legend(); fig.tight_layout(); fig.savefig(RESULTS / "38_sharing.png", dpi=140)
    print("saved results/38_sharing.json + .png")


if __name__ == "__main__":
    main()
