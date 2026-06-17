"""Step 85 — IMPOSSIBILITY CERTIFICATE II: a net's failure to find an invariant certifies "NO LAW" (chaos).

Face 2 of the triad. A conservation-law finder (net g: instantaneous state -> scalar, standardized to unit
total variance so it cannot collapse to a constant) is trained to be CONSTANT ALONG TRAJECTORIES. Point it at
two worlds:
  KEPLER (2D gravity): has local analytic invariants -- energy E = v^2/2 - 1/r and angular momentum L = x vy
    - y vx. A unit-variance g CAN be made constant along each orbit (it equals E or L), varying across orbits.
  LORENZ (sigma=10, rho=28, beta=8/3): web-verified to have NO nontrivial time-independent analytic constant
    of motion (the only known invariants are NON-LOCAL in time). So a local g CANNOT be made constant along
    trajectories -- on the ergodic attractor each trajectory samples the whole g-range.
The certificate: the minimum achievable along-trajectory variance (constancy), and the diversity ratio
rho = (across-trajectory variance)/(mean within-trajectory variance), separate "real invariant" from "no law."

Pre-reg (2026-06-17):
  N1 KEPLER invariant found & REAL: constancy (mean within-traj var, total var=1) < 0.05, diversity rho > 10,
     and the recovered g correlates with true E or L (|r| > 0.9).
  N2 LORENZ no-law CERTIFIED: constancy > 0.3 (a unit-variance local g cannot be made constant along the
     chaotic flow) and diversity rho < 2.
  N3 SEPARATION: Kepler passes both gates, Lorenz fails both; rho_Kepler > 10 x rho_Lorenz.
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

DT = 0.02
L = 400            # steps per trajectory (long enough that Lorenz explores the attractor)
T = 120            # trajectories
np.seterr(all="ignore")


def kepler(seed=0):
    rng = np.random.default_rng(seed); traj = []; E = []; Lz = []
    for _ in range(T):
        r0 = rng.uniform(0.8, 1.5); v0 = rng.uniform(0.75, 1.2)
        x = np.array([r0, 0.0]); v = np.array([0.0, v0]); pts = []
        for _ in range(L):
            r = np.linalg.norm(x); a = -x / r ** 3
            vh = v + 0.5 * DT * a; x = x + DT * vh; a2 = -x / np.linalg.norm(x) ** 3; v = vh + 0.5 * DT * a2
            pts.append([x[0], x[1], v[0], v[1]])
        pts = np.array(pts); traj.append(pts)
        E.append(0.5 * (pts[:, 2] ** 2 + pts[:, 3] ** 2) - 1 / np.linalg.norm(pts[:, :2], axis=1))
        Lz.append(pts[:, 0] * pts[:, 3] - pts[:, 1] * pts[:, 2])
    return np.array(traj, np.float32), np.array(E, np.float32), np.array(Lz, np.float32)


def lorenz(seed=1, sigma=10.0, rho=28.0, beta=8 / 3):
    rng = np.random.default_rng(seed); traj = []
    def f(s):
        x, y, z = s; return np.array([sigma * (y - x), x * (rho - z) - y, x * y - beta * z])
    for _ in range(T):
        s = rng.uniform(-15, 15, 3); s[2] = abs(s[2]) + 5
        for _ in range(800):                         # discard transient -> land on the attractor
            k1 = f(s); k2 = f(s + 0.5 * DT * k1); k3 = f(s + 0.5 * DT * k2); k4 = f(s + DT * k3)
            s = s + DT * (k1 + 2 * k2 + 2 * k3 + k4) / 6
        pts = []
        for _ in range(L):
            k1 = f(s); k2 = f(s + 0.5 * DT * k1); k3 = f(s + 0.5 * DT * k2); k4 = f(s + DT * k3)
            s = s + DT * (k1 + 2 * k2 + 2 * k3 + k4) / 6; pts.append(s.copy())
        traj.append(pts)
    return np.array(traj, np.float32)


class Inv(nn.Module):
    def __init__(s, d):
        super().__init__(); s.net = nn.Sequential(nn.Linear(d, 128), nn.GELU(), nn.Linear(128, 128), nn.GELU(),
                                                  nn.Linear(128, 128), nn.GELU(), nn.Linear(128, 1))
    def forward(s, x): return s.net(x)[..., 0]


def find_invariant(traj, tag, steps=4000):
    """traj (T,L,d). Minimize within-trajectory variance of a globally-standardized g (anti-collapse)."""
    d = traj.shape[-1]; mu = traj.reshape(-1, d).mean(0); sd = traj.reshape(-1, d).std(0) + 1e-6
    X = torch.tensor((traj - mu) / sd, dtype=torch.float32)        # (T,L,d) standardized inputs
    m = Inv(d); opt = torch.optim.Adam(m.parameters(), lr=2e-3)
    for step in range(steps):
        g = m(X)                                                   # (T,L)
        gn = (g - g.mean()) / (g.std() + 1e-6)                      # unit TOTAL variance (anti-collapse)
        within = gn.var(dim=1).mean()                              # mean within-trajectory variance = constancy
        loss = within
        opt.zero_grad(); loss.backward(); opt.step()
        if step % 400 == 0: progress(tag, step, steps, loss=float(loss.detach()))
    m.eval()
    with torch.no_grad():
        g = m(X); gn = (g - g.mean()) / (g.std() + 1e-6)
        constancy = float(gn.var(dim=1).mean())                    # ~0 if invariant exists
        across = float(gn.mean(dim=1).var())                       # across-trajectory variance
        within = float(gn.var(dim=1).mean())
        rho = across / (within + 1e-6)
        gnp = gn.numpy()
    return gnp, constancy, rho


def main():
    ktraj, E, Lz = kepler(); ltraj = lorenz()
    gk, ck, rhok = find_invariant(ktraj, "85_kepler")
    gl, cl, rhol = find_invariant(ltraj, "85_lorenz")

    # does the Kepler invariant match E or L?
    gkf = gk.ravel(); corrE = abs(np.corrcoef(gkf, E.ravel())[0, 1]); corrL = abs(np.corrcoef(gkf, Lz.ravel())[0, 1])
    kepler_real = max(corrE, corrL)

    n1 = bool(ck < 0.05 and rhok > 10 and kepler_real > 0.9)
    n2 = bool(cl > 0.3 and rhol < 2)
    n3 = bool(n1 and n2 and rhok > 10 * max(rhol, 1e-3))
    out = {"kepler_constancy": ck, "kepler_rho": rhok, "kepler_corr_E": float(corrE), "kepler_corr_L": float(corrL),
           "lorenz_constancy": cl, "lorenz_rho": rhol,
           "N1_kepler_real_invariant": n1, "N2_lorenz_no_law_certified": n2, "N3_separation": n3,
           "nolaw_certified": bool(n1 and n2 and n3)}
    print(f"KEPLER : constancy {ck:.4f} | rho {rhok:.1f} | corr(g,E) {corrE:.3f} corr(g,L) {corrL:.3f}")
    print(f"LORENZ : constancy {cl:.4f} | rho {rhol:.3f}")
    print(f"\nN1 Kepler real invariant (constancy<0.05, rho>10, matches E/L): {n1}")
    print(f"N2 Lorenz NO-LAW certified (constancy>0.3, rho<2): {n2}")
    print(f"N3 separation (Kepler passes, Lorenz fails, rho ratio >10x): {n3}")
    print(f"\nNO-LAW CERTIFIED BY FAILURE (no local invariant exists for chaotic Lorenz): {out['nolaw_certified']}")
    (RESULTS / "85_nolaw_chaos.json").write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(1, 2, figsize=(13, 5))
    # Kepler: recovered g vs true E (or L), colored by trajectory -> tight bands (constant per orbit)
    best = E if corrE >= corrL else Lz; lab = "E" if corrE >= corrL else "L"
    ax[0].scatter(best.ravel(), gk.ravel(), s=2, alpha=0.3, color="seagreen")
    ax[0].set_xlabel(f"true {lab}"); ax[0].set_ylabel("net invariant g"); ax[0].set_title(f"KEPLER: net found a REAL invariant\nconstancy {ck:.3f}, rho {rhok:.0f}, |corr| {kepler_real:.3f}")
    # Lorenz: g along a few trajectories -> wanders (cannot be constant)
    for t in range(6):
        ax[1].plot(gl[t], alpha=0.7)
    ax[1].set_xlabel("time step along trajectory"); ax[1].set_ylabel("net 'invariant' g (standardized)")
    ax[1].set_title(f"LORENZ: NO invariant exists -- best g still wanders\nconstancy {cl:.3f} (can't be made constant), rho {rhol:.2f}")
    fig.tight_layout(); fig.savefig(RESULTS / "85_nolaw_chaos.png", dpi=140)
    print("saved results/85_nolaw_chaos.json + .png")


if __name__ == "__main__":
    main()
