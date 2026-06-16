"""Step 68 — OVERNIGHT #2: the FIELD ZOO — why is gravity the odd one out? (the reachable QFT lens)

The Feynman/Standard-Model question, made buildable. The fundamental interactions differ on two axes:
  COUPLING:  UNIVERSAL (couples to mass/energy, the SAME for every body = equivalence principle, gravity)
             vs  CHARGE-SPECIFIC (couples to a per-body charge q/m that VARIES = EM/strong, a "force")
  MEDIATOR MASS:  MASSLESS (long-range, force ~ 1/r^2, photon/graviton)
             vs  MASSIVE (short-range Yukawa, force ~ e^(-mu r)(1+mu r)/r^2, W/Z, web-verified above)

We run our economy race in each of the 2x2 cells and ask which cells GEOMETRIZE.
  GeometryModel: a = g_net(x)            — identity-blind = AMORTIZED (one shared law). Geometry/equivalence.
  ForceModel:    a = scale_i * h_net(x)  — one free scalar per body (a per-instance charge). A "force".
  geometrization ratio  R = MSE_geometry / MSE_force  (held-out positions, same bodies):
    R ~ 1  -> the per-body code buys NOTHING -> universal coupling -> GEOMETRY basin (gravity-like)
    R >> 1 -> the per-body code is essential   -> charge coupling   -> stays a FORCE (EM-like)

The thesis on trial (scripts 45/55): geometrization is set by the COUPLING axis (universality), and is
INDEPENDENT of the MASS axis (range/learnability is orthogonal to whether it geometrizes). Gravity =
universal x massless = the deepest geometry cell; it is universality, NOT masslessness, that puts it there.

Pre-reg (2026-06-17):
  Z1 the two UNIVERSAL cells geometrize: R < 2.0 (force code near-useless).
  Z2 the two CHARGE cells do NOT: R > 5.0 (force code essential).
  Z3 the verdict is set by COUPLING, not MASS: min(universal R's) and max over mass within universal stay
     < 2, AND charge cells stay > 5 in BOTH mass settings — i.e. swapping the mass axis never flips a
     geometrize verdict (gravity's place is bought by universality, not range).
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
from torch import nn

STEPS = 4000
NBODY = 64
DEV = torch.device("mps" if torch.backends.mps.is_available() else "cpu")


def field(x, y, massive, mu=1.2):
    """Central attractive field at positions (x,y). massless: 1/r^2 ; massive: Yukawa (1+mu r)e^(-mu r)/r^2."""
    r = np.sqrt(x ** 2 + y ** 2) + 0.3
    inv = 1.0 / r ** 2
    if massive:
        inv = inv * (1.0 + mu * r) * np.exp(-mu * r)
    return (-x / r) * inv, (-y / r) * inv          # unit-vector * magnitude


def make_data(universal, massive, n_per=1500, seed=0):
    """Per (body, position) acceleration. universal: rho_i=1 for all. charge: rho_i = q_i/m_i varies."""
    rng = np.random.default_rng(seed)
    rho = np.ones(NBODY, np.float32) if universal else rng.uniform(0.3, 2.0, NBODY).astype(np.float32)
    B, X, Y, A = [], [], [], []
    for i in range(NBODY):
        x = rng.uniform(-3, 3, n_per).astype(np.float32); y = rng.uniform(-3, 3, n_per).astype(np.float32)
        gx, gy = field(x, y, massive)
        B.append(np.full(n_per, i)); X.append(np.stack([x, y], 1))
        A.append(rho[i] * np.stack([gx, gy], 1).astype(np.float32))
    return np.concatenate(B), np.concatenate(X).astype(np.float32), np.concatenate(A).astype(np.float32), rho


class GeometryModel(nn.Module):                    # identity-blind = amortized (one shared field)
    def __init__(s):
        super().__init__(); s.net = nn.Sequential(nn.Linear(2, 128), nn.GELU(), nn.Linear(128, 128), nn.GELU(),
                                                  nn.Linear(128, 128), nn.GELU(), nn.Linear(128, 2))
    def forward(s, x, b): return s.net(x)


class ForceModel(nn.Module):                       # one free scalar per body (a per-instance charge)
    def __init__(s):
        super().__init__(); s.net = nn.Sequential(nn.Linear(2, 128), nn.GELU(), nn.Linear(128, 128), nn.GELU(),
                                                  nn.Linear(128, 128), nn.GELU(), nn.Linear(128, 2))
        s.scale = nn.Embedding(NBODY, 1)
    def forward(s, x, b): return s.net(x) * s.scale(b)


def train_eval(model, B, X, A, tag):
    Bt = torch.from_numpy(B).long().to(DEV); Xt = torch.from_numpy(X).to(DEV); At = torch.from_numpy(A).to(DEV)
    n = len(B); ntr = int(n * 0.9); perm = np.random.default_rng(0).permutation(n)
    tr, te = perm[:ntr], perm[ntr:]
    m = model.to(DEV); opt = torch.optim.Adam(m.parameters(), lr=1e-3); rng = np.random.default_rng(0)
    for step in range(STEPS):
        idx = tr[rng.integers(0, ntr, 512)]
        loss = nn.functional.mse_loss(m(Xt[idx], Bt[idx]), At[idx])
        opt.zero_grad(); loss.backward(); opt.step()
        if step % 500 == 0: progress(tag, step, STEPS, loss=float(loss.detach()))
    m.eval()
    with torch.no_grad():
        mse = float(((m(Xt[te], Bt[te]) - At[te]) ** 2).mean())
    return mse


def main():
    cells = [("universal", True, False), ("universal", True, True),
             ("charge", False, False), ("charge", False, True)]
    out = {}
    for label, universal, massive in cells:
        mass = "massive" if massive else "massless"
        key = f"{label}_{mass}"
        B, X, A, rho = make_data(universal, massive)
        torch.manual_seed(0); mg = train_eval(GeometryModel(), B, X, A, f"68_geo_{key}")
        torch.manual_seed(0); mf = train_eval(ForceModel(), B, X, A, f"68_for_{key}")
        R = mg / (mf + 1e-12)
        out[key] = {"coupling": label, "mediator": mass, "MSE_geometry": mg, "MSE_force": mf, "ratio": R}
        print(f"{key:22s}: MSE geom {mg:.2e} | force {mf:.2e} | ratio R={R:6.2f} "
              f"-> {'GEOMETRY' if R < 2 else 'FORCE' if R > 5 else 'mixed'}")

    uml, uma = out["universal_massless"]["ratio"], out["universal_massive"]["ratio"]
    cml, cma = out["charge_massless"]["ratio"], out["charge_massive"]["ratio"]
    z1 = bool(uml < 2.0 and uma < 2.0)
    z2 = bool(cml > 5.0 and cma > 5.0)
    z3 = bool(max(uml, uma) < 2.0 and min(cml, cma) > 5.0)   # mass-swap never flips a verdict
    res = {"cells": out,
           "Z1_universal_cells_geometrize": z1, "Z2_charge_cells_stay_force": z2,
           "Z3_coupling_not_mass_decides": z3,
           "gravity_is_universal_not_massless": bool(z1 and z2 and z3)}
    print(f"\nZ1 universal cells geometrize (R<2 both): {z1}")
    print(f"Z2 charge cells stay force (R>5 both): {z2}")
    print(f"Z3 COUPLING decides, not MASS (mass-swap never flips a verdict): {z3}")
    print(f"\nGRAVITY'S PLACE = UNIVERSAL COUPLING, NOT MASSLESSNESS: {res['gravity_is_universal_not_massless']}")
    (RESULTS / "68_field_zoo.json").write_text(json.dumps(res, indent=1))

    fig, ax = plt.subplots(figsize=(7.8, 5.2))
    grid = np.array([[uml, uma], [cml, cma]])
    im = ax.imshow(np.log10(grid), cmap="RdYlGn_r", aspect="auto")
    ax.set_xticks([0, 1]); ax.set_xticklabels(["massless\n(long-range)", "massive\n(Yukawa)"])
    ax.set_yticks([0, 1]); ax.set_yticklabels(["UNIVERSAL\n(grav-like)", "CHARGE\n(EM-like)"])
    for i in range(2):
        for j in range(2):
            v = grid[i, j]
            ax.annotate(f"R={v:.1f}\n{'GEOMETRY' if v<2 else 'FORCE' if v>5 else 'mixed'}",
                        (j, i), ha="center", va="center", fontsize=10, fontweight="bold")
    ax.set_title("the field zoo: which cells GEOMETRIZE?\n(R=MSE_geom/MSE_force; low=geometry, high=force)\n"
                 "gravity = top-left; its place is bought by UNIVERSAL coupling, not masslessness")
    fig.colorbar(im, ax=ax, label="log10 ratio R"); fig.tight_layout()
    fig.savefig(RESULTS / "68_field_zoo.png", dpi=140)
    print("saved results/68_field_zoo.json + .png")


if __name__ == "__main__":
    main()
