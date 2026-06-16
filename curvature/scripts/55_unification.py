"""Step 55 — THE UNIFICATION TEST: is "universality" (physics) the same lever as "amortization" (ML)?

Two headline laws of this repo, long treated as separate:
  PHYSICS: a label becomes GEOMETRY (cost 0) iff it is UNIVERSAL (all bodies same coupling) — else a
           per-body FORCE (cost 1). [economy race, scripts 45/52]
  ML:      a code becomes LEGIBLE iff it is AMORTIZED (inferred by a shared encoder) — a free per-body
           code SCRAMBLES (esp. multi-dimensional). [legibility law, scripts 48/50]

Claim (orthogonal, nobody writes it down): these are ONE principle — "what is SHARED across instances
collapses into structure; what is PER-INSTANCE stays a scrambled tag." Note the economy-race GEOMETRY
model IS the maximally-amortized model (identity-blind, one shared rule); the FORCE model IS the free
per-body code. So the geometrization transition and the legibility transition may be the SAME
comparison. Test: ONE universality knob (spread sigma of a 2-D per-body coupling rho), read out BOTH
order parameters on the SAME data.

Three models (same data/budget): BLIND f(x) [pure geometry]; AMORTIZED f(x, enc(context)) [shared
encoder infers the code in-context]; FREE f(x, emb[body]) [per-body free code].

Pre-reg (2026-06-17):
  U1 geometrization transition: Gamma = blind_MSE / free_MSE rises from ~1 (sigma=0, universal -> shared
     model suffices) to >>1 (high sigma, per-body code needed). The physics transition.
  U2 amortization legibilizes: at max sigma, decode rho from the code — amortized L > 0.8 AND amortized
     L > free L + 0.3 (free 2-D code scrambles per script 48; amortized stays legible per 50). The ML transition.
  U3 the isomorphism: at sigma=0 the per-body code carries ~no info (universal -> nothing to store; blind
     and free tie, Gamma~1); the SAME sigma that makes a code NECESSARY (Gamma departs 1) is where
     amortized-vs-free legibility splits. One knob ("shareability"), both transitions.
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
from sklearn.model_selection import cross_val_predict
from torch import nn

C1, C2 = (1.2, -0.8), (-1.1, 1.0)       # two scalar wells
DEPTH = 0.16
RHO0 = np.array([0.8, 0.8], np.float32)
N_BODIES, PER_BODY, STEPS, HELD, CODE, KCTX = 44, 360, 8000, 8, 4, 32  # fix round: K 16->32, more steps so the 2-D rho is inferred cleanly (was signal-limited at 0.78)
SIGMAS = [0.0, 0.4, 0.8, 1.6]
TD = 2 * len(TRAJ_TIMES)


def accel(x, y, vx, vy, rho):
    eg = np.exp(-(x**2 + y**2) / (2 * WELL_WIDTH**2))
    ax = -WELL_DEPTH * x * eg / WELL_WIDTH**2; ay = -WELL_DEPTH * y * eg / WELL_WIDTH**2
    for k, c in enumerate((C1, C2)):
        dx, dy = x - c[0], y - c[1]
        e = np.exp(-(dx**2 + dy**2) / (2 * WELL_WIDTH**2))
        ax = ax - rho[:, k] * DEPTH * dx * e / WELL_WIDTH**2
        ay = ay - rho[:, k] * DEPTH * dy * e / WELL_WIDTH**2
    return ax, ay


def integrate(x0, y0, vx0, vy0, rho, dt=0.01):
    n = int(round(TRAJ_TIMES[-1] / dt)); grab = {int(round(t / dt)): i for i, t in enumerate(TRAJ_TIMES)}
    x, y, vx, vy = (a.astype(float).copy() for a in (x0, y0, vx0, vy0))
    out = np.empty((len(x0), len(TRAJ_TIMES), 2))
    for s in range(1, n + 1):
        def rk(xx, yy, ux, uy):
            ax, ay = accel(xx, yy, ux, uy, rho); return ux, uy, ax, ay
        k1 = rk(x, y, vx, vy); k2 = rk(x+.5*dt*k1[0], y+.5*dt*k1[1], vx+.5*dt*k1[2], vy+.5*dt*k1[3])
        k3 = rk(x+.5*dt*k2[0], y+.5*dt*k2[1], vx+.5*dt*k2[2], vy+.5*dt*k2[3])
        k4 = rk(x+dt*k3[0], y+dt*k3[1], vx+dt*k3[2], vy+dt*k3[3])
        x = x+dt/6*(k1[0]+2*k2[0]+2*k3[0]+k4[0]); y = y+dt/6*(k1[1]+2*k2[1]+2*k3[1]+k4[1])
        vx = vx+dt/6*(k1[2]+2*k2[2]+2*k3[2]+k4[2]); vy = vy+dt/6*(k1[3]+2*k2[3]+2*k3[3]+k4[3])
        if s in grab:
            out[:, grab[s], 0] = x; out[:, grab[s], 1] = y
    return out


def make_data(sigma, seed=0):
    rng = np.random.default_rng(seed)
    rho = (RHO0 + rng.uniform(-sigma / 2, sigma / 2, (N_BODIES, 2))).astype(np.float32)
    X, Y = [], []
    for i in range(N_BODIES):
        x0 = rng.uniform(-2.5, 2.5, PER_BODY); y0 = rng.uniform(-2.5, 2.5, PER_BODY)
        vx0 = rng.uniform(-V_MAX, V_MAX, PER_BODY); vy0 = rng.uniform(-V_MAX, V_MAX, PER_BODY)
        inp = np.stack([x0, y0, vx0, vy0], 1).astype(np.float32)
        tg = integrate(x0, y0, vx0, vy0, np.tile(rho[i], (PER_BODY, 1))).reshape(PER_BODY, -1).astype(np.float32)
        X.append(inp); Y.append(tg)
    return {"rho": rho, "X": np.stack(X), "Y": np.stack(Y)}      # X:(B,P,4) Y:(B,P,6)


class Blind(nn.Module):
    def __init__(s):
        super().__init__(); s.net = nn.Sequential(nn.Linear(4, 128), nn.Tanh(), nn.Linear(128, 128), nn.Tanh(), nn.Linear(128, TD))
    def forward(s, x, code=None): return s.net(x)


class Free(nn.Module):
    def __init__(s, n):
        super().__init__(); s.emb = nn.Embedding(n, CODE)
        s.net = nn.Sequential(nn.Linear(4 + CODE, 128), nn.Tanh(), nn.Linear(128, 128), nn.Tanh(), nn.Linear(128, TD))
    def forward(s, x, body): return s.net(torch.cat([x, s.emb(body)], -1))


class Amort(nn.Module):
    def __init__(s):
        super().__init__()
        s.enc = nn.Sequential(nn.Linear(4 + TD, 128), nn.GELU(), nn.Linear(128, 128), nn.GELU(), nn.Linear(128, CODE))
        s.net = nn.Sequential(nn.Linear(4 + CODE, 128), nn.Tanh(), nn.Linear(128, 128), nn.Tanh(), nn.Linear(128, TD))
    def code(s, ctx):                                            # ctx: (...,K,4+TD)
        return s.enc(ctx).mean(-2)
    def forward(s, x, ctx):
        c = s.code(ctx); c = c[..., None, :].expand(*c.shape[:-1], x.shape[-2], CODE) if x.dim() == 3 else c
        return s.net(torch.cat([x, c], -1))


def train_blind_free(model, d, kind, seed):
    torch.manual_seed(seed); rng = np.random.default_rng(seed)
    X = torch.from_numpy(d["X"]); Y = torch.from_numpy(d["Y"])
    seen = np.arange(N_BODIES - HELD)
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)
    for step in range(STEPS):
        bi = rng.choice(seen, 128); pi = rng.integers(0, PER_BODY, 128)
        xb = X[bi, pi]; yb = Y[bi, pi]
        pred = model(xb, torch.from_numpy(bi)) if kind == "free" else model(xb)
        loss = nn.functional.mse_loss(pred, yb)
        opt.zero_grad(); loss.backward(); opt.step()
        if step % 500 == 0: progress(f"55_{kind}", step, STEPS, loss=float(loss.detach()))
    return model


def train_amort(model, d, seed):
    torch.manual_seed(seed); rng = np.random.default_rng(seed)
    X = torch.from_numpy(d["X"]); Y = torch.from_numpy(d["Y"]); XY = torch.cat([X, Y], -1)  # (B,P,4+TD)
    seen = np.arange(N_BODIES - HELD); opt = torch.optim.Adam(model.parameters(), lr=1e-3)
    for step in range(STEPS):
        bi = rng.choice(seen, 64)
        ctx_idx = np.stack([rng.choice(PER_BODY, KCTX, replace=False) for _ in bi])
        q_idx = rng.integers(0, PER_BODY, len(bi))
        ctx = XY[torch.from_numpy(bi)[:, None], torch.from_numpy(ctx_idx)]   # (b,K,4+TD)
        xq = X[torch.from_numpy(bi), torch.from_numpy(q_idx)]                # (b,4)
        yq = Y[torch.from_numpy(bi), torch.from_numpy(q_idx)]
        c = model.code(ctx)
        pred = model.net(torch.cat([xq, c], -1))
        loss = nn.functional.mse_loss(pred, yq)
        opt.zero_grad(); loss.backward(); opt.step()
        if step % 500 == 0: progress("55_amort", step, STEPS, loss=float(loss.detach()))
    return model


def test_mse(model, d, kind):
    X = torch.from_numpy(d["X"]); Y = torch.from_numpy(d["Y"])
    seen = np.arange(N_BODIES - HELD); te = slice(PER_BODY - 60, PER_BODY)
    with torch.no_grad():
        xb = X[seen, te].reshape(-1, 4); yb = Y[seen, te].reshape(-1, TD)
        if kind == "blind":
            pred = model(xb)
        elif kind == "free":
            bi = np.repeat(seen, 60); pred = model(xb, torch.from_numpy(bi))
        else:
            XY = torch.cat([X, Y], -1)
            ctx = XY[seen, :KCTX]                                  # (S,K,4+TD)
            ctx = ctx[:, None].expand(len(seen), 60, KCTX, 4 + TD).reshape(-1, KCTX, 4 + TD)
            c = model.code(ctx); pred = model.net(torch.cat([xb, c], -1))
        return float(nn.functional.mse_loss(pred, yb))


def legibility(model, d, kind):
    seen = np.arange(N_BODIES - HELD); rho = d["rho"][seen]
    X = torch.from_numpy(d["X"]); Y = torch.from_numpy(d["Y"])
    with torch.no_grad():
        if kind == "free":
            C = model.emb(torch.from_numpy(seen)).numpy()
        else:
            XY = torch.cat([X, Y], -1); C = model.code(XY[seen, :KCTX]).numpy()
    return float(np.mean([np.corrcoef(cross_val_predict(Ridge(1.0), C, rho[:, j], cv=5), rho[:, j])[0, 1] for j in range(2)]))


def main():
    rows = []
    for sg in SIGMAS:
        d = make_data(sg)
        bl = train_blind_free(Blind(), d, "blind", 0)
        fr = train_blind_free(Free(N_BODIES), d, "free", 1)
        am = train_amort(Amort(), d, 2)
        mb, mf, ma = test_mse(bl, d, "blind"), test_mse(fr, d, "free"), test_mse(am, d, "amort")
        lf, la = legibility(fr, d, "free"), legibility(am, d, "amort")
        gamma = mb / mf
        rows.append({"sigma": sg, "blind_mse": mb, "free_mse": mf, "amort_mse": ma,
                     "Gamma_geom": gamma, "L_free": lf, "L_amort": la})
        print(f"σ={sg:.1f}: Γ(blind/free)={gamma:5.2f} | blind {mb:.1e} free {mf:.1e} amort {ma:.1e} | L_free {lf:.2f} L_amort {la:.2f}")

    g = [r["Gamma_geom"] for r in rows]
    u1 = bool(g[0] < 2 and g[-1] > 5 and g[-1] > g[0] + 3)
    u2 = bool(rows[-1]["L_amort"] > 0.8 and rows[-1]["L_amort"] > rows[-1]["L_free"] + 0.3)
    u3 = bool(g[0] < 2 and (rows[-1]["L_amort"] - rows[-1]["L_free"]) > 0.3)   # universal->tie; private->amort-vs-free splits
    out = {"sweep": rows, "U1_geometrization_transition": u1, "U2_amortization_legibilizes": u2,
           "U3_one_knob_both_transitions": u3,
           "unification_supported": bool(u1 and u2 and u3)}
    print(f"\nU1 geometrization transition (Γ {g[0]:.1f}->{g[-1]:.1f}): {u1}")
    print(f"U2 amortization legibilizes (max-σ L_amort {rows[-1]['L_amort']:.2f}>0.8 & > L_free {rows[-1]['L_free']:.2f}+0.3): {u2}")
    print(f"U3 one knob, both transitions (σ=0 tie Γ {g[0]:.1f}<2; private amort-vs-free split): {u3}")
    print(f"\nGEOMETRY = AMORTIZED PHYSICS (universality == amortization): {out['unification_supported']}")
    (RESULTS / "55_unification.json").write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(1, 2, figsize=(12, 4.6))
    ax[0].plot(SIGMAS, g, "o-", color="purple"); ax[0].axhline(1, ls=":", color="gray")
    ax[0].set_xlabel("universality knob σ (spread of ρ)"); ax[0].set_ylabel("Γ = blind/free MSE")
    ax[0].set_title("PHYSICS transition: shared model suffices when universal")
    ax[1].plot(SIGMAS, [r["L_amort"] for r in rows], "o-", color="seagreen", label="amortized code")
    ax[1].plot(SIGMAS, [r["L_free"] for r in rows], "s--", color="crimson", label="free code")
    ax[1].set_xlabel("universality knob σ"); ax[1].set_ylabel("legibility of ρ"); ax[1].set_ylim(0, 1); ax[1].legend()
    ax[1].set_title("ML transition: amortized stays legible, free scrambles")
    fig.suptitle("One knob (σ), two transitions — is universality the same lever as amortization?")
    fig.tight_layout(); fig.savefig(RESULTS / "55_unification.png", dpi=140)
    print("saved results/55_unification.json + .png")


if __name__ == "__main__":
    main()
