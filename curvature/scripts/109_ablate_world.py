"""Step 109 — decisive ablation: is the WORLD FUNCTION the missing ingredient of the free-code scramble?

Three fresh harnesses (103/107/108) never reproduced the s35 free-code scramble (free legible ~0.9) although s35
scrambles robustly (0.24, confirmed 104 + Phronesis/AlphaLudo). Output richness (107), capacity (105), and batching
regime (108) were all REFUTED. The remaining concrete difference: the world function. s35.World is a DEFAULT-init
frozen random MLP; my fresh worlds re-init weights to N(0,0.7) (large -> saturated/high-frequency). This swaps ONLY
the data-generating world into my exact free learner + per-object training:
  world A = my make_world (large-weight randnet, generic)
  world B = s35.World (default-init MLP) -- the actual harness that scrambles
D=1, OUT=1, free per-object code, 3 seeds. If B scrambles and A does not, the WORLD is the ingredient (the scramble
needs a specific class of target function); if both stay legible, the scramble is even more elusive (honest).

Pre-reg (2026-06-23):
  A1 s35-WORLD SCRAMBLES: world B free linear-decode < 0.55 (reproduces the s35 scramble through my learner).
  A2 MY-WORLD LEGIBLE: world A free linear-decode > 0.7 (the large-weight world is 'easy').
  (If A1 fails: the scramble is not the world either -> ingredient unidentified; the free->scramble leg is fragile.)
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
from sklearn.linear_model import Ridge
from sklearn.neighbors import KNeighborsRegressor
from sklearn.model_selection import cross_val_predict
from torch import nn
from importlib import import_module

s35 = import_module("35_legibility_scale")
s107 = import_module("107_output_richness")
N_OBJ, PER_OBJ, XDIM, CDIM, STEPS = s107.N_OBJ, s107.PER_OBJ, s107.XDIM, s107.CDIM, s107.STEPS


def data_myworld(seed):
    return s107.make_data("generic", 1, 1, seed)            # (P, body, X, Y) large-weight randnet world


def data_s35world(seed):
    """generate (P, body, X, Y) from s35.World (default-init MLP), D=1, scalar output."""
    s35.PDIM = 1
    rng = np.random.default_rng(seed)
    world = s35.World(width=128, seed=7)
    P = rng.uniform(-1, 1, (N_OBJ, 1)).astype(np.float32)
    body, X, Y = [], [], []
    with torch.no_grad():
        for i in range(N_OBJ):
            x = rng.uniform(-1, 1, (PER_OBJ, XDIM)).astype(np.float32)
            y = world(torch.from_numpy(np.tile(P[i], (PER_OBJ, 1))), torch.from_numpy(x)).numpy()
            body.append(np.full(PER_OBJ, i)); X.append(x); Y.append(y[:, None])
    return P, np.concatenate(body).astype(np.int64), np.concatenate(X), np.concatenate(Y).astype(np.float32)


def train_perobject(P, body, X, Y, seed):
    Xr = X.reshape(N_OBJ, PER_OBJ, XDIM); Yr = Y.reshape(N_OBJ, PER_OBJ, 1)
    Xrt = torch.from_numpy(Xr); Yrt = torch.from_numpy(Yr)
    torch.manual_seed(seed); rng = np.random.default_rng(seed)
    m = s107.Free(1); opt = torch.optim.Adam(m.parameters(), lr=2e-3)
    for step in range(STEPS):
        ob = rng.integers(0, N_OBJ, 32)
        emb = m.emb(torch.from_numpy(ob))[:, None, :].expand(-1, PER_OBJ, -1)
        loss = nn.functional.mse_loss(m.head(torch.cat([Xrt[ob], emb], -1)), Yrt[ob])
        opt.zero_grad(); loss.backward(); opt.step()
        if step % 2000 == 0:
            progress(f"109_s{seed}", step, STEPS, loss=float(loss.detach()))
    with torch.no_grad():
        C = m.emb(torch.arange(N_OBJ)).numpy()
    lin = float(np.corrcoef(cross_val_predict(Ridge(1.0), C, P[:, 0], cv=5), P[:, 0])[0, 1])
    nl = float(np.corrcoef(cross_val_predict(KNeighborsRegressor(8), C, P[:, 0], cv=5), P[:, 0])[0, 1])
    return lin, nl


def main():
    seeds = [0, 1, 2]
    A = np.array([train_perobject(*data_myworld(s), s) for s in seeds])      # my world
    B = np.array([train_perobject(*data_s35world(s), s) for s in seeds])     # s35 world
    a_lin, a_nl = float(A[:, 0].mean()), float(A[:, 1].mean())
    b_lin, b_nl = float(B[:, 0].mean()), float(B[:, 1].mean())
    print(f"world A (my large-weight randnet): linear {a_lin:.3f} | kNN {a_nl:.3f}")
    print(f"world B (s35 default-init MLP)    : linear {b_lin:.3f} | kNN {b_nl:.3f}")
    a1 = bool(b_lin < 0.55); a2 = bool(a_lin > 0.7)
    out = {"seeds": seeds, "world_A_myrandnet": {"linear": a_lin, "knn": a_nl},
           "world_B_s35": {"linear": b_lin, "knn": b_nl},
           "A1_s35world_scrambles": a1, "A2_myworld_legible": a2,
           "world_is_the_ingredient": bool(a1 and a2),
           "verdict": (f"THE WORLD FUNCTION is the missing ingredient: the s35 default-init MLP world scrambles a "
                       f"free code (linear {b_lin:.2f}) while my large-weight world stays legible ({a_lin:.2f}), at "
                       f"identical learner/capacity/batching. The free->scramble needs a specific target-function "
                       f"class; the law's framing should note this dependence." if (a1 and a2) else
                       f"NOT the world either (s35-world {b_lin:.2f}, my-world {a_lin:.2f}). After refuting output "
                       "richness (107), capacity (105), batching (108), and now the world (109), the s35 scramble's "
                       "ingredient remains UNISOLATED in fresh code -> the free->scramble leg is fragile/setup-"
                       "specific; the robust, theorem-backed direction is amortize->legible (Roeder). Honest bound.")}
    print(f"\nA1 s35-world scrambles ({b_lin:.2f}<0.55): {a1}")
    print(f"A2 my-world legible ({a_lin:.2f}>0.7): {a2}")
    print(f"WORLD IS THE INGREDIENT: {out['world_is_the_ingredient']}")
    (RESULTS / "109_ablate_world.json").write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(figsize=(6.5, 5))
    ax.bar(["my world\n(large-weight)", "s35 world\n(default init)"], [a_lin, b_lin], color=["seagreen", "crimson"])
    ax.axhline(0.55, ls="--", c="k", lw=0.6); ax.set_ylabel("free D=1 linear decode r"); ax.set_ylim(0, 1)
    ax.set_title("ablating the world function (identical learner/capacity/batching)\nis the target function the scramble's ingredient?")
    fig.tight_layout(); fig.savefig(RESULTS / "109_ablate_world.png", dpi=140)
    print("saved results/109_ablate_world.json + .png")


if __name__ == "__main__":
    main()
