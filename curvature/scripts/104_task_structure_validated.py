"""Step 104 — definitive re-test of the AlphaLudo task-structure refinement, in the VALIDATED harness (script 35).

Owed follow-up. My quick toy (103) failed to reproduce even the baseline free-code scramble, so it could not test
AlphaLudo's §2 claim ("'1-D free code stays legible' holds only under linear/monotone coupling; a generic random-MLP
map scrambles even D=1"). This uses script 35's EXACT harness — the one that demonstrably scrambles (free PDIM=2
linear ~0.2; reproduced independently by both Phronesis and AlphaLudo at ~0.22) — and changes ONLY the world's
coupling, to test the refinement faithfully.

Script 35's world g(p,x) is a frozen random MLP -> the property p enters through a GENERIC nonlinear map. We add a
LINEAR-coupling world  g(p,x) = base(x) + Σ_k p_k · coup_k(x)  (p enters linearly; coefficients are nonlinear in x,
like charge→force in our physics). Same Learner (free per-object embedding vs amortized encoder), same decode
(Ridge = legibility, kNN = info present). Sweep PDIM ∈ {1,2}, 3 seeds.

Pre-reg (2026-06-22) — the AlphaLudo prediction:
  G1 BASELINE SCRAMBLE REPRODUCES: in the GENERIC world, the FREE code scrambles — free PDIM=2 linear < 0.55 (the
     known script-35 result) AND free PDIM=1 linear < 0.55 (AlphaLudo's "generic scrambles even D=1", their 0.36).
  G2 LINEAR COUPLING RESCUES D=1: in the LINEAR world, free PDIM=1 is legible — linear > 0.6 (AlphaLudo's 0.61).
  G3 THE FLIP IS REAL: (linear-world free D=1) − (generic-world free D=1) > 0.2, with kNN high in both (info present).
  (Control: amortized is legible everywhere.)
If G1 fails (our generic harness does NOT scramble at D=1), that is itself the honest finding — the D=1 scramble
would then be specific to AlphaLudo's setup, not general.
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
XDIM = s35.XDIM


class LinearWorld(nn.Module):
    """g(p,x) = base(x) + Σ_k p_k · coup_k(x): the property enters LINEARLY (coeffs nonlinear in x)."""
    def __init__(self, pdim, width=128, seed=0):
        super().__init__()
        torch.manual_seed(seed)
        def mlp(dout):
            return nn.Sequential(nn.Linear(XDIM, width), nn.GELU(), nn.Linear(width, width), nn.GELU(),
                                 nn.Linear(width, dout))
        self.base = mlp(1); self.coup = mlp(pdim)
        for q in self.parameters():
            q.requires_grad_(False)

    def forward(self, p, x):
        return self.base(x)[..., 0] + (p * self.coup(x)).sum(-1)


def run(world_type, pdim, mode, seed, n_obj=256, steps=6000):
    s35.PDIM = pdim                                           # script 35's World/make_data read this global
    world = s35.World(width=128, seed=7) if world_type == "generic" else LinearWorld(pdim, seed=7)
    d = s35.make_data(world, n_obj, per_obj=64, seed=seed)
    ex, qx, qy = d["ex"], d["qx"], d["qy"]
    torch.manual_seed(seed); rng = np.random.default_rng(seed)
    m = s35.Learner(n_obj, 128, mode); opt = torch.optim.Adam(m.parameters(), lr=2e-3)
    for step in range(steps):
        idx = torch.tensor(rng.integers(0, n_obj, 128))
        loss = nn.functional.mse_loss(m(ex, idx, qx[idx]), qy[idx])
        opt.zero_grad(); loss.backward(); opt.step()
        if step % 1500 == 0:
            progress(f"104_{world_type}_p{pdim}_{mode}_s{seed}", step, steps, loss=float(loss.detach()))
    m.eval()
    with torch.no_grad():
        C = m.code(ex, torch.arange(n_obj)).numpy()
    P = d["P"]
    lin = float(np.mean([np.corrcoef(cross_val_predict(Ridge(1.0), C, P[:, j], cv=5), P[:, j])[0, 1] for j in range(pdim)]))
    nl = float(np.mean([np.corrcoef(cross_val_predict(KNeighborsRegressor(8), C, P[:, j], cv=5), P[:, j])[0, 1] for j in range(pdim)]))
    return lin, nl


def agg(world_type, pdim, mode, seeds):
    rs = [run(world_type, pdim, mode, s) for s in seeds]
    return {"linear": float(np.mean([r[0] for r in rs])), "linear_std": float(np.std([r[0] for r in rs])),
            "nonlinear": float(np.mean([r[1] for r in rs]))}


def main():
    seeds = [0, 1, 2]
    R = {}
    for wt in ("generic", "linear"):
        for pd in (1, 2):
            for md in ("free", "amortized"):
                R[(wt, pd, md)] = agg(wt, pd, md, seeds)
                v = R[(wt, pd, md)]
                print(f"{wt:8s} PDIM={pd} {md:9s}: linear {v['linear']:.3f}±{v['linear_std']:.2f} | kNN {v['nonlinear']:.3f}")

    gen_f1 = R[("generic", 1, "free")]["linear"]; gen_f2 = R[("generic", 2, "free")]["linear"]
    lin_f1 = R[("linear", 1, "free")]["linear"]
    g1 = bool(gen_f2 < 0.55 and gen_f1 < 0.55)
    g2 = bool(lin_f1 > 0.6)
    g3 = bool(lin_f1 - gen_f1 > 0.2 and R[("generic", 1, "free")]["nonlinear"] > 0.6 and R[("linear", 1, "free")]["nonlinear"] > 0.6)
    confirmed = bool(g1 and g2 and g3)
    out = {"seeds": seeds, "results": {f"{wt}_p{pd}_{md}": R[(wt, pd, md)] for (wt, pd, md) in R},
           "G1_baseline_scramble_reproduces": g1, "G2_linear_rescues_D1": g2, "G3_flip_is_real": g3,
           "alphaludo_refinement_confirmed_in_validated_harness": confirmed,
           "verdict": (("CONFIRMED: in script 35's validated harness, the GENERIC-coupling world scrambles the free "
                        f"code even at D=1 (linear {gen_f1:.2f}) while LINEAR coupling rescues it (D=1 linear "
                        f"{lin_f1:.2f}) — so '1-D free legible' is task-dependent (needs linear/monotone coupling), "
                        "exactly as AlphaLudo found. BOTH dimensionality and coupling-linearity gate free-code "
                        "legibility.") if confirmed else
                       ("PARTIAL/NEGATIVE: see numbers. If G1 failed, our generic harness does not scramble at D=1 "
                        f"either (gen free D=1 linear {gen_f1:.2f}) — then AlphaLudo's D=1 scramble is setup-specific, "
                        "not general (honest either way)."))}
    print(f"\nG1 baseline scramble reproduces (gen free D1 {gen_f1:.2f} & D2 {gen_f2:.2f} <0.55): {g1}")
    print(f"G2 linear coupling rescues D=1 (lin free D1 {lin_f1:.2f} >0.6): {g2}")
    print(f"G3 the flip is real (Δ {lin_f1 - gen_f1:.2f} >0.2): {g3}")
    print(f"\nALPHALUDO REFINEMENT CONFIRMED IN VALIDATED HARNESS: {confirmed}")
    (RESULTS / "104_task_structure_validated.json").write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(figsize=(8, 5))
    labels = ["generic\nD=1", "generic\nD=2", "linear\nD=1", "linear\nD=2"]
    free = [R[("generic", 1, "free")]["linear"], R[("generic", 2, "free")]["linear"],
            R[("linear", 1, "free")]["linear"], R[("linear", 2, "free")]["linear"]]
    amort = [R[("generic", 1, "amortized")]["linear"], R[("generic", 2, "amortized")]["linear"],
             R[("linear", 1, "amortized")]["linear"], R[("linear", 2, "amortized")]["linear"]]
    x = np.arange(4); w = 0.38
    ax.bar(x - w / 2, free, w, color="crimson", label="free per-object code")
    ax.bar(x + w / 2, amort, w, color="seagreen", label="amortized (control)")
    ax.axhline(0.55, ls="--", c="k", lw=0.6); ax.set_xticks(x); ax.set_xticklabels(labels)
    ax.set_ylabel("linear decode r of property (legibility)"); ax.set_ylim(0, 1); ax.legend(fontsize=8)
    ax.set_title("AlphaLudo refinement in the validated harness:\ngeneric coupling scrambles even D=1; linear coupling rescues D=1")
    fig.tight_layout(); fig.savefig(RESULTS / "104_task_structure_validated.png", dpi=140)
    print("saved results/104_task_structure_validated.json + .png")


if __name__ == "__main__":
    main()
