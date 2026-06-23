"""Step 108 — the real ingredient of the free-code scramble: PER-OBJECT vs PER-QUERY batching.

Two fresh harnesses (103, 107) failed to reproduce the free-code scramble (free stayed legible ~0.9-1.0) that the
s35 harness shows robustly (0.24, reproduced by Phronesis 0.22 + AlphaLudo 0.216). 107 also refuted OUTPUT RICHNESS
as the driver (legible at every OUT). The structural clue: the LEGIBLE cases (script 48 phys 0.86; script 107 0.93)
train PER-QUERY (random query points across all objects); the SCRAMBLED case (s35/104, 0.24) trains PER-OBJECT (each
embedding updated on a coherent batch of its OWN queries). Hypothesis: per-object batching lets each free code
specialize NONLINEARLY (scramble); per-query keeps it linear (legible).

Controlled isolation (107's exact world/model/capacity; ONLY the batching regime varies; D=1, free code, 3 seeds):
  per-query:  each step = 256 random (object,query) pairs (each embedding gets ~1 query's gradient).
  per-object: each step = 32 objects x all PER_OBJ queries (each embedding gets a coherent 64-query gradient).
Cross with OUT in {1,16} to confirm richness is not the driver under either regime.

Pre-reg (2026-06-23):
  B1 PER-OBJECT SCRAMBLES: per-object OUT=1 free linear-decode < 0.55 (reproduces the s35 scramble in fresh code).
  B2 PER-QUERY STAYS LEGIBLE: per-query OUT=1 free linear-decode > 0.7 (matches 48/107).
  B3 BATCHING IS THE DRIVER: (per-query - per-object) linear gap > 0.3 at OUT=1, with kNN high in both (info present).
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

s107 = import_module("107_output_richness")
N_OBJ, PER_OBJ, XDIM, CDIM, STEPS = s107.N_OBJ, s107.PER_OBJ, s107.XDIM, s107.CDIM, s107.STEPS


def run(regime, OUT, seed, D=1):
    P, body, X, Y = s107.make_data("linear", D, OUT, seed)
    Xr = X.reshape(N_OBJ, PER_OBJ, XDIM); Yr = Y.reshape(N_OBJ, PER_OBJ, OUT)  # grouped by object
    Xt = torch.from_numpy(X); Yt = torch.from_numpy(Y); bt = torch.from_numpy(body)
    Xrt = torch.from_numpy(Xr); Yrt = torch.from_numpy(Yr)
    torch.manual_seed(seed); rng = np.random.default_rng(seed)
    m = s107.Free(OUT); opt = torch.optim.Adam(m.parameters(), lr=2e-3)
    for step in range(STEPS):
        if regime == "perquery":
            idx = rng.integers(0, len(X), 256)
            loss = nn.functional.mse_loss(m(bt[idx], Xt[idx]), Yt[idx])
        else:  # perobject: 32 objects x all their queries, one embedding lookup each (s35-style)
            ob = rng.integers(0, N_OBJ, 32)
            emb = m.emb(torch.from_numpy(ob))[:, None, :].expand(-1, PER_OBJ, -1)
            pred = m.head(torch.cat([Xrt[ob], emb], -1))
            loss = nn.functional.mse_loss(pred, Yrt[ob])
        opt.zero_grad(); loss.backward(); opt.step()
        if step % 2000 == 0:
            progress(f"108_{regime}_O{OUT}_s{seed}", step, STEPS, loss=float(loss.detach()))
    with torch.no_grad():
        C = m.emb(torch.arange(N_OBJ)).numpy()
    lin = float(np.mean([np.corrcoef(cross_val_predict(Ridge(1.0), C, P[:, j], cv=5), P[:, j])[0, 1] for j in range(D)]))
    nl = float(np.mean([np.corrcoef(cross_val_predict(KNeighborsRegressor(8), C, P[:, j], cv=5), P[:, j])[0, 1] for j in range(D)]))
    return lin, nl


def agg(regime, OUT, seeds):
    rs = [run(regime, OUT, s) for s in seeds]
    return float(np.mean([r[0] for r in rs])), float(np.std([r[0] for r in rs])), float(np.mean([r[1] for r in rs]))


def main():
    seeds = [0, 1, 2]
    R = {(reg, o): agg(reg, o, seeds) for reg in ("perquery", "perobject") for o in (1, 16)}
    for (reg, o), v in R.items():
        print(f"{reg:9s} OUT={o:2d}: linear {v[0]:.3f}±{v[1]:.2f} | kNN {v[2]:.3f}")

    pq1 = R[("perquery", 1)][0]; po1 = R[("perobject", 1)][0]
    b1 = bool(po1 < 0.55)
    b2 = bool(pq1 > 0.7)
    b3 = bool(pq1 - po1 > 0.3 and R[("perquery", 1)][2] > 0.6 and R[("perobject", 1)][2] > 0.6)
    out = {"seeds": seeds, "results": {f"{reg}_OUT{o}": {"linear": R[(reg, o)][0], "std": R[(reg, o)][1], "knn": R[(reg, o)][2]} for (reg, o) in R},
           "B1_perobject_scrambles": b1, "B2_perquery_legible": b2, "B3_batching_is_the_driver": b3,
           "verdict": (f"BATCHING IS THE DRIVER of the free-code scramble: at identical world/capacity/output, a free "
                       f"D=1 code is SCRAMBLED under per-object batching (OUT=1 linear {po1:.2f}) but LEGIBLE under "
                       f"per-query batching (OUT=1 linear {pq1:.2f}). Output richness is NOT the driver (107). This "
                       f"reframes the 1-D 'mystery': script 48 (legible) trains per-query, the s35 harness (scrambled) "
                       f"per-object -- the regime, not the output, flips it. The free->scramble leg is conditional on "
                       f"per-object coherent gradients letting each code specialize nonlinearly."
                       if (b1 and b2 and b3) else
                       f"Batching does NOT cleanly explain it (per-query {pq1:.2f}, per-object {po1:.2f}) -- honest; "
                       "the scramble ingredient remains unisolated (see numbers).")}
    print(f"\nB1 per-object scrambles (OUT=1 {po1:.2f}<0.55): {b1}")
    print(f"B2 per-query legible (OUT=1 {pq1:.2f}>0.7): {b2}")
    print(f"B3 batching is the driver (gap {pq1-po1:.2f}>0.3): {b3}")
    (RESULTS / "108_scramble_ingredient.json").write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(figsize=(7.5, 5))
    x = np.arange(2); wd = 0.38
    ax.bar(x - wd / 2, [R[("perquery", o)][0] for o in (1, 16)], wd, color="seagreen", label="per-query batching")
    ax.bar(x + wd / 2, [R[("perobject", o)][0] for o in (1, 16)], wd, color="crimson", label="per-object batching")
    ax.axhline(0.55, ls="--", c="k", lw=0.6); ax.set_xticks(x); ax.set_xticklabels(["OUT=1 (scalar)", "OUT=16"])
    ax.set_ylabel("free D=1 linear decode r"); ax.set_ylim(0, 1); ax.legend(fontsize=8)
    ax.set_title("the real scramble ingredient: per-OBJECT batching scrambles a free code,\nper-QUERY keeps it legible (output richness is not the driver)")
    fig.tight_layout(); fig.savefig(RESULTS / "108_scramble_ingredient.png", dpi=140)
    print("saved results/108_scramble_ingredient.json + .png")


if __name__ == "__main__":
    main()
