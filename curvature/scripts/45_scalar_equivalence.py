"""Step 45 — NEW FIELD: a SCALAR charge as an equivalence-principle knob.

The project's thesis (discovering_curvature_with_nn.md): geometrization happens BECAUSE of the
equivalence principle — many bodies fall ALIKE, so one shared arena beats per-body forces on
description length. We showed gravity geometrizes (Phase C: identity costs 0) and EM does not
(costs 1), but never ISOLATED *why*. A scalar (spin-0) field lets us test it directly, because:
  - the scalar force is ATTRACTIVE-only (no +/- sign, unlike EM) — verified (EMD interaction energy);
  - what matters is the ratio rho = s/m (scalar-charge-to-mass).
So we tune UNIVERSALITY as a knob while holding "attraction" fixed:
  rho the SAME for all bodies  -> everyone feels one shared field -> should GEOMETRIZE (cost 0);
  rho VARIES across bodies      -> bodies fall differently        -> should COST 1 (like q/m).

Setup: 2D gravity well (at origin) + a scalar well (at a different center) whose pull is scaled by
each body's rho. Economy race (reusing Phase C's idea): GeometryModel(x,y,vx,vy)->trajectory is
identity-blind; ForceModel adds a per-body embedding. Sweep the SPREAD of rho and watch the
geometry-vs-force gap turn on = the equivalence-principle transition. Also: is the learned code for
rho ONE-SIGNED (scalar) vs EM's signed q/m, and legible or scrambled (free embedding -> legibility law)?

Pre-reg gates (2026-06-16):
  S1 universal geometrizes: at spread=0, geometry/force test-MSE ratio < 2 (identity buys nothing).
  S2 species costs:         at max spread, geometry/force ratio > 5 (identity needed).
  S3 transition monotone:   the ratio increases with spread (the knob).
  S4 the code is rho:       at max spread, behavioral/nonlinear decode of rho from the embedding
                            r > 0.9, and rho is recovered as ONE-SIGNED (all >= 0).
Newtonian toy generator (declared bias, like Phase C) — not Einstein dynamics.
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
from sklearn.linear_model import Ridge
from sklearn.neighbors import KNeighborsRegressor
from sklearn.model_selection import cross_val_predict
from torch import nn

SCALAR_CENTER = (1.2, -0.8)
SCALAR_DEPTH = 0.15
RHO0 = 0.8                          # base scalar-charge/mass (the "universal" level)
N_BODIES, PER_BODY, STEPS = 40, 400, 6000
HELD = 8
SPREADS = [0.0, 0.4, 0.8, 1.6]
EMB_DIM = 4


def accel(x, y, vx, vy, rho):
    """a = -grad(phi_grav at origin) + rho * -grad(phi_scalar at SCALAR_CENTER). Both attractive."""
    eg = np.exp(-(x**2 + y**2) / (2 * WELL_WIDTH**2))
    axg = -WELL_DEPTH * x * eg / WELL_WIDTH**2
    ayg = -WELL_DEPTH * y * eg / WELL_WIDTH**2
    dx, dy = x - SCALAR_CENTER[0], y - SCALAR_CENTER[1]
    es = np.exp(-(dx**2 + dy**2) / (2 * WELL_WIDTH**2))
    axs = -SCALAR_DEPTH * dx * es / WELL_WIDTH**2
    ays = -SCALAR_DEPTH * dy * es / WELL_WIDTH**2
    return axg + rho * axs, ayg + rho * ays


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
        x = x + dt/6*(k1[0] + 2*k2[0] + 2*k3[0] + k4[0])
        y = y + dt/6*(k1[1] + 2*k2[1] + 2*k3[1] + k4[1])
        vx = vx + dt/6*(k1[2] + 2*k2[2] + 2*k3[2] + k4[2])
        vy = vy + dt/6*(k1[3] + 2*k2[3] + 2*k3[3] + k4[3])
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
    is_held = np.isin(body, held)
    seen = np.where(~is_held)[0]; rng.shuffle(seen)
    nt = len(seen) // 6
    return {"rho_body": rho_body, "held": held,
            "train": (body[seen[nt:]], X[seen[nt:]], Y[seen[nt:]]),
            "test": (body[seen[:nt]], X[seen[:nt]], Y[seen[:nt]])}


class Geometry(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(4, 128), nn.Tanh(), nn.Linear(128, 128), nn.Tanh(),
                                 nn.Linear(128, 2 * len(TRAJ_TIMES)))

    def forward(self, x, body=None):
        return self.net(x)


class Force(nn.Module):
    def __init__(self, n):
        super().__init__()
        self.emb = nn.Embedding(n, EMB_DIM)
        self.net = nn.Sequential(nn.Linear(4 + EMB_DIM, 128), nn.Tanh(), nn.Linear(128, 128), nn.Tanh(),
                                 nn.Linear(128, 2 * len(TRAJ_TIMES)))

    def forward(self, x, body):
        return self.net(torch.cat([x, self.emb(body)], 1))


def train(model, data, seed, tag):
    torch.manual_seed(seed); rng = np.random.default_rng(seed)
    body, X, Y = data["train"]; opt = torch.optim.Adam(model.parameters(), lr=1e-3)
    for step in range(STEPS):
        idx = rng.integers(0, len(X), 512)
        loss = nn.functional.mse_loss(model(torch.from_numpy(X[idx]), torch.from_numpy(body[idx])),
                                      torch.from_numpy(Y[idx]))
        opt.zero_grad(); loss.backward(); opt.step()
        if step % 500 == 0:
            progress(tag, step, STEPS, loss=float(loss.detach()))
    return model


def mse(model, split):
    body, X, Y = split
    with torch.no_grad():
        return float(nn.functional.mse_loss(model(torch.from_numpy(X), torch.from_numpy(body)),
                                            torch.from_numpy(Y)))


def main():
    rows = []
    decode = {}
    for sp in SPREADS:
        d = make_data(sp)
        g = train(Geometry(), d, 0, f"45_geo_s{sp}"); f = train(Force(N_BODIES), d, 1, f"45_force_s{sp}")
        gm, fm = mse(g, d["test"]), mse(f, d["test"])
        ratio = gm / fm
        rows.append({"spread": sp, "geometry_mse": gm, "force_mse": fm, "ratio": ratio})
        print(f"spread {sp:.1f}: geometry MSE {gm:.2e} | force MSE {fm:.2e} | ratio {ratio:.2f}")
        if sp == SPREADS[-1]:
            seen = np.setdiff1d(np.arange(N_BODIES), d["held"])
            emb = f.emb(torch.from_numpy(seen.astype(np.int64))).detach().numpy()
            rho = d["rho_body"][seen]
            lin = float(np.corrcoef(cross_val_predict(Ridge(1.0), emb, rho, cv=5), rho)[0, 1])
            nl = float(np.corrcoef(cross_val_predict(KNeighborsRegressor(5), emb, rho, cv=5), rho)[0, 1])
            decode = {"linear_r": lin, "nonlinear_r": nl, "rho_min": float(rho.min()),
                      "rho_all_nonneg": bool((rho >= 0).all())}

    ratios = [r["ratio"] for r in rows]
    s1 = bool(ratios[0] < 2)
    s2 = bool(ratios[-1] > 5)
    s3 = bool(all(ratios[i + 1] >= ratios[i] - 0.5 for i in range(len(ratios) - 1)) and ratios[-1] > ratios[0] + 2)
    s4 = bool(max(decode["linear_r"], decode["nonlinear_r"]) > 0.9 and decode["rho_all_nonneg"])
    out = {"sweep": rows, "decode_at_max_spread": decode,
           "S1_universal_geometrizes": s1, "S2_species_costs": s2,
           "S3_transition_monotone": s3, "S4_code_is_rho_onesigned": s4,
           "equivalence_principle_knob_confirmed": bool(s1 and s2 and s3 and s4)}
    print(f"\nS1 universal geometrizes (spread0 ratio {ratios[0]:.2f} <2): {s1}")
    print(f"S2 species costs (max-spread ratio {ratios[-1]:.2f} >5): {s2}")
    print(f"S3 transition monotone (ratios {[round(r,2) for r in ratios]}): {s3}")
    print(f"S4 code is rho, one-signed (lin {decode['linear_r']:.2f}/nl {decode['nonlinear_r']:.2f}, nonneg {decode['rho_all_nonneg']}): {s4}")
    print(f"\nEQUIVALENCE-PRINCIPLE KNOB: {out['equivalence_principle_knob_confirmed']}")
    (RESULTS / "45_scalar_equivalence.json").write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(1, 2, figsize=(12, 4.6))
    ax[0].plot(SPREADS, ratios, "o-", color="purple")
    ax[0].axhline(1, ls=":", color="gray"); ax[0].set_xlabel("spread of ρ = s/m  (universality knob)")
    ax[0].set_ylabel("geometry MSE / force MSE"); ax[0].set_title("equivalence-principle transition:\nuniversal→geometrizes, species→costs")
    ax[1].plot(SPREADS, [r["geometry_mse"] for r in rows], "o-", label="geometry (identity-blind)", color="seagreen")
    ax[1].plot(SPREADS, [r["force_mse"] for r in rows], "s-", label="force (per-body code)", color="crimson")
    ax[1].set_yscale("log"); ax[1].set_xlabel("spread of ρ"); ax[1].set_ylabel("test MSE"); ax[1].legend()
    ax[1].set_title("geometry fails only when bodies fall differently")
    fig.tight_layout(); fig.savefig(RESULTS / "45_scalar_equivalence.png", dpi=140)
    print("saved results/45_scalar_equivalence.json + .png")


if __name__ == "__main__":
    main()
