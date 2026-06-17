"""Step 73 — RUNG 1: can a net SIMULATE a test particle near a black hole? (the GR-only signatures)

User's exploration: "give one particle, simulate how it behaves" around a black hole. The interesting test
is whether a learned simulator reproduces the effects a NEWTONIAN sim cannot: perihelion PRECESSION (the
Mercury effect) and the ISCO (innermost stable circular orbit). Web-verified Schwarzschild equatorial
geodesics (geometric units G=M=c=1): effective potential V(r)=(1-2/r)(1+L^2/r^2); radial proper-time
dynamics d^2r/dtau^2 = -1/2 V'(r) = L^2/r^3 - 1/r^2 - 3L^2/r^4 (the -3L^2/r^4 is the GR term -> precession;
Newtonian drops it), dphi/dtau = L/r^2; precession Delta_phi = 6*pi*(M/L)^2 per orbit; ISCO at r=6M.

A net learns the ONE-STEP map (r, v_r, L) -> (r', v_r') from GR orbit segments (identity-blind in phi), then
we roll it out autoregressively (phi from L/r^2) to SIMULATE orbits it never saw, and measure the physics.

Pre-reg (2026-06-17):
  B1 learns the dynamics: held-out one-step R^2 > 0.999.
  B2 PRECESSION (the headline): the rolled-out net orbit precesses; measured precession/orbit matches the
     true GR integrator within 15% AND is clearly nonzero (a Newtonian-force control gives ~0).
  B3 ISCO: the net's learned radial force (read at v_r=0) yields circular orbits whose marginal-stability
     radius (ISCO) is 6M within 20%.
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

DTAU = 0.4
DEV = torch.device("cpu")


def accel(r, L, newton=False):
    a = L ** 2 / r ** 3 - 1.0 / r ** 2
    if not newton:
        a = a - 3.0 * L ** 2 / r ** 4          # the GR term -> precession
    return a


def integrate(r0, L, nsteps, newton=False, vr0=0.0):
    """velocity-Verlet in proper time; returns r, phi, vr arrays."""
    r = float(r0); vr = float(vr0); phi = 0.0
    R, PH, VR = [r], [phi], [vr]
    for _ in range(nsteps):
        a = accel(r, L, newton); vr_half = vr + 0.5 * DTAU * a
        r = r + DTAU * vr_half
        if r < 2.05 or r > 80:                  # plunged or escaped
            break
        a2 = accel(r, L, newton); vr = vr_half + 0.5 * DTAU * a2
        phi = phi + DTAU * L / r ** 2
        R.append(r); PH.append(phi); VR.append(vr)
    return np.array(R), np.array(PH), np.array(VR)


def make_segments(n_orbits=400, seed=0):
    rng = np.random.default_rng(seed); X, Y = [], []
    for _ in range(n_orbits):
        L = rng.uniform(3.7, 5.2); r0 = rng.uniform(9, 22)      # bound, precessing (L>sqrt12)
        R, PH, VR = integrate(r0, L, 600)
        if len(R) >= 50:
            for i in range(len(R) - 1):
                X.append([R[i], VR[i], L]); Y.append([R[i + 1], VR[i + 1]])
    # near-circular orbits across radii: populate the (r, vr~0, L) region so the ISCO is readable
    for _ in range(n_orbits):
        rc = rng.uniform(4.2, 20.0)
        if rc <= 3.2:
            continue
        L = np.sqrt(rc ** 2 / (rc - 3.0))                       # circular-orbit L at radius rc
        R, PH, VR = integrate(rc, L, 400, vr0=rng.normal(0, 0.06))
        if len(R) >= 30:
            for i in range(len(R) - 1):
                X.append([R[i], VR[i], L]); Y.append([R[i + 1], VR[i + 1]])
    return np.array(X, np.float32), np.array(Y, np.float32)


class Sim(nn.Module):
    def __init__(s):
        super().__init__(); s.net = nn.Sequential(nn.Linear(3, 128), nn.GELU(), nn.Linear(128, 128), nn.GELU(),
                                                  nn.Linear(128, 128), nn.GELU(), nn.Linear(128, 2))

    def forward(s, x):                          # (r,vr,L) -> (r',vr'); residual on (r,vr) for stability
        return x[:, :2] + s.net(x)


def roll(m, r0, L, nsteps):
    r, vr, phi = float(r0), 0.0, 0.0; R, PH = [r], [phi]
    for _ in range(nsteps):
        with torch.no_grad():
            out = m(torch.tensor([[r, vr, L]], dtype=torch.float32)).numpy()[0]
        rn, vr = float(out[0]), float(out[1])
        phi = phi + DTAU * L / r ** 2; r = rn
        if r < 2.05 or r > 80:
            break
        R.append(r); PH.append(phi)
    return np.array(R), np.array(PH)


def precession_per_orbit(R, PH):
    """phi advance between successive periapsis passages (local minima of r), minus 2pi."""
    mins = [i for i in range(1, len(R) - 1) if R[i] < R[i - 1] and R[i] < R[i + 1]]
    if len(mins) < 2:
        return None
    dphis = np.diff(PH[mins])
    return float(np.mean(dphis) - 2 * np.pi)


def net_accel(m, r, L):                         # read learned radial force at vr=0: a ~ (vr' - 0)/dtau
    with torch.no_grad():
        out = m(torch.tensor([[r, 0.0, L]], dtype=torch.float32)).numpy()[0]
    return (out[1] - 0.0) / DTAU


def circular_L(m, r, Lgrid=np.linspace(3.0, 6.5, 240)):
    """L of the circular orbit at radius r: the L where net_accel(r,L)=0 (accel rises with L)."""
    a = np.array([net_accel(m, r, L) for L in Lgrid])
    s = np.where(np.diff(np.sign(a)) != 0)[0]
    if len(s) == 0:
        return None
    return float(Lgrid[s[0]])


def isco_from_net(m, rgrid=np.linspace(4.2, 13.0, 90)):
    """ISCO = radius minimizing the circular-orbit L curve (true GR: min at r=6, L=sqrt12)."""
    rL = [(r, circular_L(m, r)) for r in rgrid]; rL = [(r, L) for r, L in rL if L is not None]
    if len(rL) < 5:
        return None, rL
    rs = np.array([r for r, _ in rL]); Ls = np.array([L for _, L in rL])
    return float(rs[int(np.argmin(Ls))]), rL


def main():
    X, Y = make_segments()
    n = len(X); ntr = int(n * 0.9); idx = np.random.default_rng(0).permutation(n)
    Xt = torch.from_numpy(X[idx]); Yt = torch.from_numpy(Y[idx])
    m = Sim(); opt = torch.optim.Adam(m.parameters(), lr=1e-3); rng = np.random.default_rng(1)
    for step in range(6000):
        b = rng.integers(0, ntr, 256)
        loss = nn.functional.mse_loss(m(Xt[b]), Yt[b])
        opt.zero_grad(); loss.backward(); opt.step()
        if step % 400 == 0: progress("73_orbit", step, 6000, loss=float(loss.detach()))
    m.eval()
    with torch.no_grad():
        pr = m(Xt[ntr:]); r2 = float(1 - ((pr - Yt[ntr:]) ** 2).sum() / ((Yt[ntr:] - Yt[ntr:].mean(0)) ** 2).sum())

    # B2 precession: a held-out orbit
    Ltest, r0test = 4.0, 16.0
    Rn, PHn = roll(m, r0test, Ltest, 1500)
    Rt, PHt, _ = integrate(r0test, Ltest, 1500)
    RtN, PHtN, _ = integrate(r0test, Ltest, 1500, newton=True)
    prec_net = precession_per_orbit(Rn, PHn); prec_true = precession_per_orbit(Rt, PHt)
    prec_newt = precession_per_orbit(RtN, PHtN)
    prec_formula = 6 * np.pi * (1.0 / Ltest) ** 2

    # B3 ISCO: radius minimizing the circular-orbit L curve (GR: r=6, L=sqrt12)
    isco_r, rLcurve = isco_from_net(m)

    b1 = bool(r2 > 0.999)
    b2 = bool(prec_net is not None and prec_true is not None and abs(prec_net - prec_true) < 0.15 * abs(prec_true)
              and prec_net > 0.1 and (prec_newt is None or abs(prec_newt) < 0.1))
    b3 = bool(isco_r is not None and abs(isco_r - 6.0) < 1.2)
    out = {"oneStep_R2": r2,
           "precession_net_rad": prec_net, "precession_true_rad": prec_true,
           "precession_newton_rad": prec_newt, "precession_formula_6pi_M_over_L2": float(prec_formula),
           "isco_radius_net": isco_r,
           "B1_learns_dynamics": b1, "B2_precession_matches_GR": b2, "B3_ISCO_at_6M": b3,
           "blackhole_orbit_simulated": bool(b1 and b2 and b3)}
    print(f"B1 one-step R^2 {r2:.5f}: {b1}")
    print(f"B2 precession/orbit — net {prec_net:.3f} rad | true GR {prec_true:.3f} | formula 6pi(M/L)^2 {prec_formula:.3f} "
          f"| Newtonian {prec_newt}: {b2}")
    print(f"B3 ISCO radius from net {isco_r} (want ~6M): {b3}")
    print(f"\nBLACK-HOLE ORBIT SIMULATED (precession + ISCO from a learned simulator): {out['blackhole_orbit_simulated']}")
    (RESULTS / "73_blackhole_orbits.json").write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(1, 2, figsize=(13, 5.5))
    ax[0].plot(Rt * np.cos(PHt), Rt * np.sin(PHt), color="crimson", lw=0.8, label="true GR (precessing)")
    ax[0].plot(Rn * np.cos(PHn), Rn * np.sin(PHn), color="seagreen", lw=0.8, ls="--", label="net simulator")
    ax[0].plot(0, 0, "ko", ms=6); ax[0].set_aspect("equal"); ax[0].legend(fontsize=8)
    ax[0].set_title(f"learned simulator reproduces perihelion precession\nnet {prec_net:.2f} rad/orbit vs GR {prec_true:.2f} (Newtonian=0)")
    rr = np.array([r for r, _ in rLcurve]); LL = np.array([L for _, L in rLcurve])
    ax[1].plot(rr, LL, "o-", color="navy", ms=3, label="net circular-orbit L(r)")
    Lc_true = np.sqrt(rr ** 2 / (rr - 3.0)); ax[1].plot(rr, Lc_true, color="gray", ls=":", label="GR L_c(r)=r²/(r-3)")
    ax[1].axvline(6.0, color="crimson", ls="--", label="ISCO = 6M (GR)")
    if isco_r: ax[1].axvline(isco_r, color="seagreen", ls="-", lw=1, label=f"net ISCO = {isco_r:.1f}M")
    ax[1].set_xlabel("radius r"); ax[1].set_ylabel("circular-orbit L"); ax[1].legend(fontsize=8)
    ax[1].set_title("the ISCO emerges as the minimum of L_c(r)")
    fig.tight_layout(); fig.savefig(RESULTS / "73_blackhole_orbits.png", dpi=140)
    print("saved results/73_blackhole_orbits.json + .png")


if __name__ == "__main__":
    main()
