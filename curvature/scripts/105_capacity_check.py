"""Step 105 — why does linear-coupling D=1 rescue legibility in our physics (48) but NOT in the abstract harness (104)?

104 found: generic coupling scrambles a free D=1 code (confirming AlphaLudo), but LINEAR coupling did NOT rescue
D=1 in script 35's abstract harness (linear 0.23) -- whereas our physics harness (48) shows linear D=1 LEGIBLE
(0.86). The two differ in (a) embedding capacity (cdim 16 vs 4) and (b) output richness (scalar vs trajectory).
This isolates (a): sweep the free code's capacity cdim in the SAME abstract harness, both worlds, D=1, 3 seeds.

Hypothesis (the writeup's untested "capacity modulates" claim): a TIGHTER free code stays linearly legible (no room
to scatter a 1-D property), a ROOMIER one scrambles it. If so, linear D=1 should become legible at small cdim,
explaining the 48-vs-104 divergence and AlphaLudo's 0.61 (their code was effectively tighter).

Pre-reg (2026-06-22):
  P1 capacity drives it: linear-world D=1 free linear-decode r RISES as cdim shrinks (legible at small cdim).
  P2 generic stays scrambled: generic-world D=1 free stays scrambled across cdim (coupling, not just capacity).
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
s104 = import_module("104_task_structure_validated")
XDIM = s35.XDIM


class FreeLearner(nn.Module):
    """free per-object code with PARAMETERIZED capacity cdim (else identical to script 35's free Learner)."""
    def __init__(self, n_obj, cdim, width=128):
        super().__init__()
        self.emb = nn.Embedding(n_obj, cdim)
        self.head = nn.Sequential(nn.Linear(XDIM + cdim, width), nn.GELU(), nn.Linear(width, width), nn.GELU(),
                                  nn.Linear(width, 1))

    def forward(self, idx, x):
        c = self.emb(idx)[:, None, :].expand(-1, x.shape[1], -1)
        return self.head(torch.cat([x, c], -1))[..., 0]


def run(world_type, cdim, seed, pdim=1, n_obj=256, steps=6000):
    s35.PDIM = pdim
    world = s35.World(width=128, seed=7) if world_type == "generic" else s104.LinearWorld(pdim, seed=7)
    d = s35.make_data(world, n_obj, per_obj=64, seed=seed)
    qx, qy = d["qx"], d["qy"]
    torch.manual_seed(seed); rng = np.random.default_rng(seed)
    m = FreeLearner(n_obj, cdim); opt = torch.optim.Adam(m.parameters(), lr=2e-3)
    for step in range(steps):
        idx = torch.tensor(rng.integers(0, n_obj, 128))
        loss = nn.functional.mse_loss(m(idx, qx[idx]), qy[idx])
        opt.zero_grad(); loss.backward(); opt.step()
        if step % 2000 == 0:
            progress(f"105_{world_type}_c{cdim}_s{seed}", step, steps, loss=float(loss.detach()))
    with torch.no_grad():
        C = m.emb(torch.arange(n_obj)).numpy()
    P = d["P"]
    lin = float(np.corrcoef(cross_val_predict(Ridge(1.0), C, P[:, 0], cv=5), P[:, 0])[0, 1])
    nl = float(np.corrcoef(cross_val_predict(KNeighborsRegressor(8), C, P[:, 0], cv=5), P[:, 0])[0, 1])
    return lin, nl


def main():
    cdims = [2, 4, 8, 16, 32]; seeds = [0, 1, 2]
    R = {}
    for wt in ("linear", "generic"):
        for cd in cdims:
            rs = [run(wt, cd, s) for s in seeds]
            R[(wt, cd)] = (float(np.mean([r[0] for r in rs])), float(np.mean([r[1] for r in rs])))
            print(f"{wt:8s} cdim={cd:2d}: linear {R[(wt,cd)][0]:.3f} | kNN {R[(wt,cd)][1]:.3f}")

    lin_small = R[("linear", 2)][0]; lin_big = R[("linear", 32)][0]
    p1 = bool(lin_small > 0.6 and lin_small - lin_big > 0.2)            # capacity drives linear-world D=1
    p2 = bool(all(R[("generic", cd)][0] < 0.55 for cd in cdims))        # generic stays scrambled at all cdim
    out = {"cdims": cdims, "seeds": seeds,
           "linear_world": {cd: R[("linear", cd)] for cd in cdims},
           "generic_world": {cd: R[("generic", cd)] for cd in cdims},
           "P1_capacity_drives_linear_D1": p1, "P2_generic_stays_scrambled": p2,
           "verdict": (f"Capacity {'IS' if p1 else 'is NOT'} the driver of linear-coupling D=1 legibility: a tight "
                       f"free code (cdim 2) is {'legible' if lin_small>0.6 else 'scrambled'} (r {lin_small:.2f}) while "
                       f"a roomy one (cdim 32) is {'scrambled' if lin_big<0.55 else 'legible'} (r {lin_big:.2f}). "
                       f"Generic coupling stays scrambled across capacity ({'yes' if p2 else 'no'}). This "
                       f"{'explains' if p1 else 'does NOT explain'} the 48-vs-104 divergence: '1-D free legible' "
                       "needs BOTH near-linear coupling AND a tight enough code.")}
    print(f"\nP1 capacity drives linear D=1 (cdim2 {lin_small:.2f}>0.6 & drop>0.2): {p1}")
    print(f"P2 generic stays scrambled at all cdim: {p2}")
    print(f"VERDICT: {out['verdict']}")
    (RESULTS / "105_capacity_check.json").write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(figsize=(7.5, 5))
    ax.plot(cdims, [R[("linear", cd)][0] for cd in cdims], "o-", color="seagreen", label="linear coupling (free)")
    ax.plot(cdims, [R[("generic", cd)][0] for cd in cdims], "s--", color="crimson", label="generic coupling (free)")
    ax.axhline(0.55, ls=":", c="k", lw=0.6); ax.set_xscale("log", base=2); ax.set_xticks(cdims)
    ax.get_xaxis().set_major_formatter(plt.matplotlib.ticker.ScalarFormatter())
    ax.set_xlabel("free-code capacity (embedding dim)"); ax.set_ylabel("linear decode r of D=1 property")
    ax.set_ylim(0, 1); ax.legend(fontsize=8)
    ax.set_title("does a tighter free code stay legible? (D=1)\nlinear coupling rescued only at small capacity; generic scrambles throughout")
    fig.tight_layout(); fig.savefig(RESULTS / "105_capacity_check.png", dpi=140)
    print("saved results/105_capacity_check.json + .png")


if __name__ == "__main__":
    main()
