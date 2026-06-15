"""Step 50 — the decisive 2x2: is AMORTIZATION an OBJECTIVE-INDEPENDENT lever for legibility?

External review (credited, parallel Claude session) located our defensible contribution: the
published "why are representations linear" theories tie linearity to the LANGUAGE-MODELING objective
(Jiang-Veitch ICML 2024: next-token softmax-CE loss + implicit bias; Ravfogel 2025: co-occurrence)
or to discriminative training (Roeder-Metz-Kingma ICML 2021: linear identifiability). Our legibility
law isolates a different, complementary lever — AMORTIZATION (shared encoder vs free per-object code)
— and we get it in a REGRESSION/contrastive harness with NO softmax-CE at all. If amortization flips
legibility in BOTH objective columns, and the objective barely matters once amortized, then
amortization is a more basic lever than the LM-objective story (their setting a special case of it).

2x2 on the script-35 abstract task (latent p in R^2, frozen world g(p,x)->y):
  objective ∈ {regression (MSE on y),  softmax-CE (predict y's quantile bin, an LM-style token)}
  storage   ∈ {free per-object embedding,  amortized shared encoder over the K examples}
Read out linear (legibility) and nonlinear (info present) decode of the true p from the code.

Pre-reg (2026-06-16):
  O1 amortized-regression legible: linear > 0.8.
  O2 amortized-CE legible:         linear > 0.8   (the KEY: legibility WITHOUT the regression objective).
  O3 free scrambles under BOTH:    free linear < 0.6 AND nonlinear-linear > 0.2 in both columns.
  O4 amortization dominates objective: amort_effect (amortized-free, avg over objectives) > 0.3
     AND objective_effect (|regression-CE| within amortized) < 0.15.
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

s35 = import_module("35_legibility_scale")
XDIM, PDIM, KEX = s35.XDIM, s35.PDIM, s35.KEX
N_OBJ, PER_OBJ, STEPS, CDIM, WIDTH, K_BINS = 256, 64, 7000, 16, 128, 12


class Learner(nn.Module):
    def __init__(self, n_obj, storage, objective):
        super().__init__()
        self.storage, self.objective = storage, objective
        if storage == "free":
            self.emb = nn.Embedding(n_obj, CDIM)
        else:
            self.enc = nn.Sequential(nn.Linear(XDIM + 1, WIDTH), nn.GELU(),
                                     nn.Linear(WIDTH, WIDTH), nn.GELU(), nn.Linear(WIDTH, CDIM))
        out = K_BINS if objective == "ce" else 1
        self.head = nn.Sequential(nn.Linear(XDIM + CDIM, WIDTH), nn.GELU(),
                                  nn.Linear(WIDTH, WIDTH), nn.GELU(), nn.Linear(WIDTH, out))

    def code(self, ex, idx):
        return self.emb(idx) if self.storage == "free" else self.enc(ex[idx]).mean(1)

    def forward(self, ex, idx, x):
        c = self.code(ex, idx)
        h = torch.cat([x, c[:, None, :].expand(-1, x.shape[1], -1)], -1)
        return self.head(h)                      # (B,Q,1) regression  or  (B,Q,K_BINS) ce


def run(storage, objective, world, d, bin_edges, seed=0):
    ex, qx, qy = d["ex"], d["qx"], d["qy"]
    torch.manual_seed(50 + seed); rng = np.random.default_rng(seed)
    m = Learner(N_OBJ, storage, objective); opt = torch.optim.Adam(m.parameters(), lr=2e-3)
    qy_bins = torch.from_numpy(np.digitize(qy.numpy(), bin_edges).clip(0, K_BINS - 1).astype(np.int64))
    for step in range(STEPS):
        idx = torch.tensor(rng.integers(0, N_OBJ, 128))
        pred = m(ex, idx, qx[idx])
        if objective == "ce":
            loss = nn.functional.cross_entropy(pred.reshape(-1, K_BINS), qy_bins[idx].reshape(-1))
        else:
            loss = nn.functional.mse_loss(pred[..., 0], qy[idx])
        opt.zero_grad(); loss.backward(); opt.step()
        if step % 500 == 0:
            progress(f"50_{storage}_{objective}", step, STEPS, loss=float(loss.detach()))
    m.eval()
    with torch.no_grad():
        C = m.code(ex, torch.arange(N_OBJ)).numpy()
    P = d["P"]
    lin = float(np.mean([np.corrcoef(cross_val_predict(Ridge(1.0), C, P[:, j], cv=5), P[:, j])[0, 1] for j in range(PDIM)]))
    nl = float(np.mean([np.corrcoef(cross_val_predict(KNeighborsRegressor(8), C, P[:, j], cv=5), P[:, j])[0, 1] for j in range(PDIM)]))
    return {"linear": lin, "nonlinear": nl}


SEEDS = (0, 1, 2)


def main():
    keys = [f"{s}_{o}" for s in ("amortized", "free") for o in ("regression", "ce")]
    per_seed = {k: {"linear": [], "nonlinear": []} for k in keys}
    for seed in SEEDS:
        world = s35.World(width=128, seed=7 + seed)
        d = s35.make_data(world, N_OBJ, PER_OBJ, seed=seed)
        bin_edges = np.quantile(d["qy"].numpy(), np.linspace(0, 1, K_BINS + 1)[1:-1])
        for storage in ("amortized", "free"):
            for objective in ("regression", "ce"):
                r = run(storage, objective, world, d, bin_edges, seed=seed)
                per_seed[f"{storage}_{objective}"]["linear"].append(r["linear"])
                per_seed[f"{storage}_{objective}"]["nonlinear"].append(r["nonlinear"])
        print(f"  seed {seed} done")

    cells = {k: {"linear": float(np.mean(v["linear"])), "linear_std": float(np.std(v["linear"])),
                 "nonlinear": float(np.mean(v["nonlinear"]))} for k, v in per_seed.items()}
    for k, v in cells.items():
        print(f"{k:22s}: linear {v['linear']:.2f}±{v['linear_std']:.2f} | nonlinear {v['nonlinear']:.2f}")

    lin = {k: v["linear"] for k, v in cells.items()}
    amort_effect = (lin["amortized_regression"] - lin["free_regression"] +
                    lin["amortized_ce"] - lin["free_ce"]) / 2
    objective_effect = abs(lin["amortized_regression"] - lin["amortized_ce"])
    o1 = bool(lin["amortized_regression"] > 0.8)
    o2 = bool(lin["amortized_ce"] > 0.8)
    o3 = bool(lin["free_regression"] < 0.6 and cells["free_regression"]["nonlinear"] - lin["free_regression"] > 0.2 and
              lin["free_ce"] < 0.6 and cells["free_ce"]["nonlinear"] - lin["free_ce"] > 0.2)
    o4 = bool(amort_effect > 0.3 and objective_effect < 0.15)
    out = {"cells": cells, "amortization_effect": amort_effect, "objective_effect": objective_effect,
           "O1_amort_regression_legible": o1, "O2_amort_ce_legible": o2,
           "O3_free_scrambles_both": o3, "O4_amortization_dominates_objective": o4,
           "amortization_is_objective_independent": bool(o1 and o2 and o3 and o4)}
    print(f"\namortization effect (avg over objectives) = {amort_effect:+.2f}")
    print(f"objective effect (within amortized)        = {objective_effect:.2f}")
    print(f"O1 amort-regression legible (>0.8): {o1}")
    print(f"O2 amort-CE legible (>0.8) [legibility WITHOUT regression objective]: {o2}")
    print(f"O3 free scrambles under BOTH objectives: {o3}")
    print(f"O4 amortization dominates objective (amort>0.3, obj<0.15): {o4}")
    print(f"\nAMORTIZATION IS AN OBJECTIVE-INDEPENDENT LEVER: {out['amortization_is_objective_independent']}")
    (RESULTS / "50_objective_x_storage.json").write_text(json.dumps(out, indent=1))

    grid = np.array([[lin["amortized_regression"], lin["amortized_ce"]],
                     [lin["free_regression"], lin["free_ce"]]])
    fig, ax = plt.subplots(figsize=(7, 5.2))
    im = ax.imshow(grid, vmin=0, vmax=1, cmap="RdYlGn")
    ax.set_xticks([0, 1]); ax.set_xticklabels(["regression\n(MSE)", "softmax-CE\n(LM-style)"])
    ax.set_yticks([0, 1]); ax.set_yticklabels(["amortized", "free"])
    for i in range(2):
        for j in range(2):
            ax.text(j, i, f"{grid[i, j]:.2f}", ha="center", va="center", fontsize=16, fontweight="bold")
    fig.colorbar(im, label="linear legibility of latent p")
    ax.set_title(f"amortization flips legibility in BOTH objective columns\namort Δ={amort_effect:+.2f}  objective Δ={objective_effect:.2f}")
    fig.tight_layout(); fig.savefig(RESULTS / "50_objective_x_storage.png", dpi=140)
    print("saved results/50_objective_x_storage.json + .png")


if __name__ == "__main__":
    main()
