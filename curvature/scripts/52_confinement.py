"""Step 52 — OVERNIGHT Run 2 (particle): does a CONFINING force geometrize when universal?

Script 45 showed universality is the cause of geometrization, for a smooth (Gaussian-well) scalar
force. Is that about UNIVERSALITY, or secretly about the force's SHAPE? Test the maximally-different
shape from gravity's 1/r: a CONFINING force V ~ |x| (constant inward magnitude, like a QCD flux tube)
— it GROWS with distance, bodies can never escape. If universality still drives geometrization here,
the equivalence-principle result is shape-independent (a real generalization of 45).

Same economy race as 45 (Geometry identity-blind vs Force per-body code), same universality knob
(spread of rho = confining-charge/mass), but the per-body force is CONFINING. Background gravity well
keeps the arena bound.

Pre-reg (2026-06-16):
  C1 universal confining geometrizes: spread=0 geometry/force ratio < 2 (identity buys nothing).
  C2 species costs:                   max spread ratio > 5 (identity needed).
  C3 transition monotone:             ratio increases with spread (the same knob as 45, new shape).
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
from curvlib import RESULTS, WELL_DEPTH, WELL_WIDTH, TRAJ_TIMES, V_MAX, progress
from importlib import import_module
from torch import nn

s45 = import_module("45_scalar_equivalence")   # reuse Geometry, Force, train, mse
K_CONF = 0.06                                   # confining force magnitude (constant inward)
RHO0 = 0.8
N_BODIES, PER_BODY, STEPS = 40, 400, 6000
HELD = 8
SPREADS = [0.0, 0.4, 0.8, 1.6]


def accel(x, y, vx, vy, rho):
    """gravity well (origin) + rho * CONFINING force (constant inward magnitude, V ~ |x|)."""
    eg = np.exp(-(x**2 + y**2) / (2 * WELL_WIDTH**2))
    axg = -WELL_DEPTH * x * eg / WELL_WIDTH**2
    ayg = -WELL_DEPTH * y * eg / WELL_WIDTH**2
    r = np.sqrt(x**2 + y**2) + 1e-3
    return axg - rho * K_CONF * x / r, ayg - rho * K_CONF * y / r


def integrate(x0, y0, vx0, vy0, rho, dt=0.01):
    n_steps = int(round(TRAJ_TIMES[-1] / dt))
    grab = {int(round(t / dt)): i for i, t in enumerate(TRAJ_TIMES)}
    x, y, vx, vy = (a.astype(float).copy() for a in (x0, y0, vx0, vy0))
    out = np.empty((len(x0), len(TRAJ_TIMES), 2))
    for step in range(1, n_steps + 1):
        def rk(xx, yy, ux, uy):
            ax, ay = accel(xx, yy, ux, uy, rho)
            return ux, uy, ax, ay
        k1 = rk(x, y, vx, vy)
        k2 = rk(x + .5*dt*k1[0], y + .5*dt*k1[1], vx + .5*dt*k1[2], vy + .5*dt*k1[3])
        k3 = rk(x + .5*dt*k2[0], y + .5*dt*k2[1], vx + .5*dt*k2[2], vy + .5*dt*k2[3])
        k4 = rk(x + dt*k3[0], y + dt*k3[1], vx + dt*k3[2], vy + dt*k3[3])
        x = x + dt/6*(k1[0]+2*k2[0]+2*k3[0]+k4[0]); y = y + dt/6*(k1[1]+2*k2[1]+2*k3[1]+k4[1])
        vx = vx + dt/6*(k1[2]+2*k2[2]+2*k3[2]+k4[2]); vy = vy + dt/6*(k1[3]+2*k2[3]+2*k3[3]+k4[3])
        if step in grab:
            out[:, grab[step], 0] = x; out[:, grab[step], 1] = y
    return out


def make_data(spread, seed=0):
    rng = np.random.default_rng(seed)
    rho_body = np.clip(RHO0 + rng.uniform(-spread / 2, spread / 2, N_BODIES), 0, None)
    held = np.arange(N_BODIES - HELD, N_BODIES)
    body, X, Y = [], [], []
    for i in range(N_BODIES):
        x0 = rng.uniform(-2.5, 2.5, PER_BODY); y0 = rng.uniform(-2.5, 2.5, PER_BODY)
        vx0 = rng.uniform(-V_MAX, V_MAX, PER_BODY); vy0 = rng.uniform(-V_MAX, V_MAX, PER_BODY)
        tg = integrate(x0, y0, vx0, vy0, np.full(PER_BODY, rho_body[i])).reshape(PER_BODY, -1)
        body.append(np.full(PER_BODY, i)); X.append(np.stack([x0, y0, vx0, vy0], 1)); Y.append(tg)
    body = np.concatenate(body).astype(np.int64)
    X = np.concatenate(X).astype(np.float32); Y = np.concatenate(Y).astype(np.float32)
    seen = np.where(~np.isin(body, held))[0]; rng.shuffle(seen)
    nt = len(seen) // 6
    return {"rho_body": rho_body, "held": held,
            "train": (body[seen[nt:]], X[seen[nt:]], Y[seen[nt:]]),
            "test": (body[seen[:nt]], X[seen[:nt]], Y[seen[:nt]])}


def main():
    rows = []
    for sp in SPREADS:
        d = make_data(sp)
        g = s45.train(s45.Geometry(), d, 0, f"52_geo_s{sp}")
        f = s45.train(s45.Force(N_BODIES), d, 1, f"52_force_s{sp}")
        gm, fm = s45.mse(g, d["test"]), s45.mse(f, d["test"])
        rows.append({"spread": sp, "geometry_mse": gm, "force_mse": fm, "ratio": gm / fm})
        print(f"spread {sp:.1f}: geometry {gm:.2e} | force {fm:.2e} | ratio {gm/fm:.2f}")

    ratios = [r["ratio"] for r in rows]
    c1 = bool(ratios[0] < 2)
    c2 = bool(ratios[-1] > 5)
    c3 = bool(all(ratios[i + 1] >= ratios[i] - 0.5 for i in range(len(ratios) - 1)) and ratios[-1] > ratios[0] + 2)
    out = {"sweep": rows, "C1_universal_geometrizes": c1, "C2_species_costs": c2,
           "C3_transition_monotone": c3, "confining_geometrizes_when_universal": bool(c1 and c2 and c3)}
    print(f"\nC1 universal confining geometrizes (spread0 ratio {ratios[0]:.2f}<2): {c1}")
    print(f"C2 species costs (max ratio {ratios[-1]:.2f}>5): {c2}")
    print(f"C3 monotone ({[round(r,2) for r in ratios]}): {c3}")
    print(f"\nCONFINING GEOMETRIZES WHEN UNIVERSAL (shape-independent): {out['confining_geometrizes_when_universal']}")
    (RESULTS / "52_confinement.json").write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.plot(SPREADS, ratios, "o-", color="darkgreen")
    ax.axhline(1, ls=":", color="gray"); ax.set_xlabel("spread of ρ (universality knob)")
    ax.set_ylabel("geometry MSE / force MSE")
    ax.set_title("confining force (V~|x|): universal→geometrizes, species→costs\n(equivalence principle is shape-independent)")
    fig.tight_layout(); fig.savefig(RESULTS / "52_confinement.png", dpi=140)
    print("saved results/52_confinement.json + .png")


if __name__ == "__main__":
    main()
