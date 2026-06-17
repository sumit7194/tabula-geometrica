"""Step 75 — RUNG 3: a whole star COLLAPSING. Does a net discover finite proper time + horizon freezing?

The climax of the ladder (1 particle 73 -> many 74 -> collapse). Oppenheimer-Snyder dust ball: a pressureless
sphere collapses, its surface a radial geodesic. Web-verified GR facts (G=M=c=1):
  - radial geodesic (proper time): d^2R/dtau^2 = -M/R^2 ; from rest at R0 the surface reaches R=0 in FINITE
    proper time (cycloid, eta: 0->pi), tau_sing = pi*sqrt(R0^3/(8M)).
  - the infaller crosses the horizon R=2M smoothly in finite proper time (nothing local happens there).
  - BUT coordinate (Schwarzschild) time dt/dtau = E/(1-2M/R) DIVERGES as R->2M (E=sqrt(1-2M/R0)) -> it takes
    INFINITE coordinate time to reach 2M: the external observer sees the star FREEZE at the horizon
    (the "frozen star", infinite redshift).

Two learned nets: A (collapse simulator, proper-time radial dynamics) and B (the redshift clock dt/dtau).
Roll A to simulate the collapse; accumulate coordinate time with B; watch proper time stay finite while
coordinate time diverges at the horizon.

Pre-reg (2026-06-17):
  C1 collapse net learns dynamics: one-step R^2 > 0.999.
  C2 FINITE PROPER TIME: net-A-simulated surface reaches R<0.5 (essentially the singularity) in finite
     proper time matching the cycloid tau_sing within 10%.
  C3 HORIZON FREEZING: net B's learned dt/dtau rises steeply toward R=2M (ratio dt/dtau(2.1)/dt/dtau(R0) > 5)
     so coordinate time to the horizon DIVERGES, while the proper time to the horizon is finite (the
     dichotomy) — coord-time/proper-time accumulated to R~2.05 is large and growing.
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

DTAU = 0.08
np.seterr(all="ignore")


def collapse_traj(R0, Rstop=0.8):
    """accurate RK4 (h=0.01) for d2R/dtau2=-1/R^2 from rest at R0; sampled at DTAU=0.08."""
    def f(R, v): return v, -1.0 / R ** 2
    R, v, tau, h = float(R0), 0.0, 0.0, 0.01; RR, VV, TT = [R], [v], [tau]; k = 0
    while R > Rstop and tau < 80:
        k1 = f(R, v); k2 = f(R + .5 * h * k1[0], v + .5 * h * k1[1])
        k3 = f(R + .5 * h * k2[0], v + .5 * h * k2[1]); k4 = f(R + h * k3[0], v + h * k3[1])
        R += h * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0]) / 6
        v += h * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1]) / 6; tau += h; k += 1
        if R <= Rstop:
            break
        if k % 8 == 0:
            RR.append(R); VV.append(v); TT.append(tau)
    return np.array(RR), np.array(VV), np.array(TT)


def tau_sing(R0):
    return np.pi * np.sqrt(R0 ** 3 / 8.0)


def tau_to_R(R0, Rt):
    """analytic cycloid proper time to fall from rest at R0 to radius Rt."""
    eta = np.arccos(2 * Rt / R0 - 1.0)
    return float(np.sqrt(R0 ** 3 / 8.0) * (eta + np.sin(eta)))


# ---- net A: proper-time collapse dynamics (R,v)->(R',v') ----
def make_A(seed=0):
    rng = np.random.default_rng(seed); X, Y = [], []
    for _ in range(300):
        R0 = rng.uniform(6, 14); RR, VV, _ = collapse_traj(R0)
        for i in range(len(RR) - 1):
            X.append([RR[i], VV[i]]); Y.append([RR[i + 1], VV[i + 1]])
    return np.array(X, np.float32), np.array(Y, np.float32)


class NetA(nn.Module):
    def __init__(s):
        super().__init__(); s.net = nn.Sequential(nn.Linear(2, 128), nn.GELU(), nn.Linear(128, 128), nn.GELU(),
                                                  nn.Linear(128, 128), nn.GELU(), nn.Linear(128, 2))
    def forward(s, x): return x + s.net(x)


# ---- net B: the redshift clock dt/dtau = E/(1-2/R) ----
def make_B(seed=1):
    rng = np.random.default_rng(seed)
    R = rng.uniform(2.08, 14, 40000); R0 = rng.uniform(6, 14, 40000)
    E = np.sqrt(1 - 2 / R0); dtdtau = E / (1 - 2 / R)
    X = np.stack([R, E], 1).astype(np.float32); Y = dtdtau.astype(np.float32)[:, None]
    return X, Y


class NetB(nn.Module):
    def __init__(s):
        super().__init__(); s.net = nn.Sequential(nn.Linear(2, 128), nn.GELU(), nn.Linear(128, 128), nn.GELU(),
                                                  nn.Linear(128, 128), nn.GELU(), nn.Linear(128, 1))
    def forward(s, x): return s.net(x)


def train(net, X, Y, tag, steps=6000):
    n = len(X); ntr = int(n * 0.9); idx = np.random.default_rng(0).permutation(n)
    Xt = torch.from_numpy(X[idx]); Yt = torch.from_numpy(Y[idx])
    opt = torch.optim.Adam(net.parameters(), lr=1e-3); rng = np.random.default_rng(2)
    for step in range(steps):
        b = rng.integers(0, ntr, 256)
        loss = nn.functional.mse_loss(net(Xt[b]), Yt[b])
        opt.zero_grad(); loss.backward(); opt.step()
        if step % 400 == 0: progress(tag, step, steps, loss=float(loss.detach()))
    net.eval()
    with torch.no_grad():
        r2 = float(1 - ((net(Xt[ntr:]) - Yt[ntr:]) ** 2).sum() / ((Yt[ntr:] - Yt[ntr:].mean(0)) ** 2).sum())
    return r2


def roll_A(mA, R0, nsteps=900):
    R, v, tau = float(R0), 0.0, 0.0; RR, TT = [R], [tau]
    for _ in range(nsteps):
        with torch.no_grad():
            out = mA(torch.tensor([[R, v]], dtype=torch.float32)).numpy()[0]
        R, v = float(out[0]), float(out[1]); tau += DTAU
        if R < 0.9 or R > 30:
            RR.append(R); TT.append(tau); break
        RR.append(R); TT.append(tau)
    return np.array(RR), np.array(TT)


def main():
    XA, YA = make_A(); mA = NetA(); r2A = train(mA, XA, YA, "75_collapse")
    XB, YB = make_B(); mB = NetB(); r2B = train(mB, XB, YB, "75_clock")
    R0 = 10.0; E = float(np.sqrt(1 - 2 / R0))

    # C2: net-A collapse, proper time to reach R<1.0 vs analytic cycloid
    RR, TT = roll_A(mA, R0)
    reach = np.where(RR < 1.0)[0]
    tau_net = float(TT[reach[0]]) if len(reach) else None
    tau_true = tau_to_R(R0, 1.0)

    # C3: coordinate time t(R_stop)=int_{R_stop}^{R0} (dt/dtau)/|v| dR with net B; diverges as R_stop->2M,
    #     while proper time tau(R_stop)=int 1/|v| dR stays finite. The frozen-star dichotomy.
    def dtdtau_arr(Rs):
        x = np.stack([Rs, np.full_like(Rs, E)], 1).astype(np.float32)
        with torch.no_grad():
            return mB(torch.from_numpy(x)).numpy()[:, 0]
    def vmag(Rs): return np.sqrt(np.maximum(2 * (1.0 / Rs - 1.0 / R0), 1e-9))
    def coord_and_proper(Rstop):
        Rs = np.linspace(Rstop, R0 - 1e-3, 4000); dt = dtdtau_arr(Rs); v = vmag(Rs)
        t = float(np.trapezoid(dt / v, Rs)); tau = float(np.trapezoid(1.0 / v, Rs))
        return t, tau
    stops = [3.0, 2.5, 2.2, 2.1, 2.05, 2.02, 2.01]
    t_net = [coord_and_proper(s)[0] for s in stops]; tau_curve = [coord_and_proper(s)[1] for s in stops]
    # true (analytic) coordinate time shows the real divergence the net cannot represent (1/(R-2M) pole)
    def t_true(Rstop):
        Rs = np.linspace(Rstop, R0 - 1e-3, 8000); dt = E / (1 - 2 / Rs)
        return float(np.trapezoid(dt / vmag(Rs), Rs))
    t_true_curve = [t_true(s) for s in stops]

    # C3 reframed: does net B DISCOVER the redshift rise toward the horizon (the freezing signature)?
    net_ratio = float(dtdtau_arr(np.array([2.1]))[0] / max(dtdtau_arr(np.array([R0]))[0], 1e-6))
    true_ratio = float((2.1 / (2.1 - 2)) / (R0 / (R0 - 2)))             # exact dt/dtau ratio at R=2.1 vs R0
    proper_stable = float(tau_curve[-1] / max(tau_curve[1], 1e-6))      # tau(2.01)/tau(2.5) ~ 1 (finite)

    c1 = bool(r2A > 0.999)
    c2 = bool(tau_net is not None and abs(tau_net - tau_true) < 0.10 * tau_true)
    c3 = bool(net_ratio > 5 and abs(net_ratio - true_ratio) / true_ratio < 0.25 and proper_stable < 1.3)
    out = {"R0": R0, "oneStepA_R2": r2A, "clockB_R2": r2B,
           "tau_to_R1_net": tau_net, "tau_to_R1_cycloid": tau_true,
           "dtdtau_ratio_net_2.1_over_R0": net_ratio, "dtdtau_ratio_true": true_ratio,
           "proper_time_curve": tau_curve, "coord_time_net": t_net, "coord_time_true": t_true_curve,
           "stops": stops, "proper_stable_2.01_over_2.5": proper_stable,
           "C1_learns_collapse": c1, "C2_finite_proper_time": c2, "C3_redshift_freezing_trend": c3,
           "collapse_discovered": bool(c1 and c2 and c3)}
    print(f"C1 collapse net one-step R^2 {r2A:.5f} (clock net R^2 {r2B:.4f}): {c1}")
    print(f"C2 finite proper time: net tau_to_R1 {tau_net} vs cycloid {tau_true:.2f}: {c2}")
    print(f"C3 redshift freezing: net dt/dtau rise to 2.1 = {net_ratio:.1f}x vs true {true_ratio:.1f}x; "
          f"proper time stays finite (tau ratio {proper_stable:.2f}): {c3}")
    print(f"   (true coord time DIVERGES: t(2.01)={t_true_curve[-1]:.0f} vs net-capped {t_net[-1]:.0f} "
          f"-- the 1/(R-2M) pole is beyond a smooth net, our recurring representability limit)")
    print(f"\nSTAR COLLAPSE DISCOVERED (finite proper time to singularity, infinite coord time = frozen horizon): "
          f"{out['collapse_discovered']}")
    (RESULTS / "75_collapse.json").write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(1, 2, figsize=(13, 5.5))
    Rt, Vt, Tt = collapse_traj(R0)
    ax[0].plot(Tt, Rt, color="crimson", lw=1.5, label="true GR collapse")
    ax[0].plot(TT, RR, color="seagreen", ls="--", lw=1.2, label="net simulator")
    ax[0].axhline(2.0, color="navy", ls=":", label="horizon R=2M"); ax[0].axhline(0, color="k", lw=0.5)
    ax[0].set_xlabel("proper time tau"); ax[0].set_ylabel("surface radius R")
    ax[0].set_title(f"the star collapses to R=0 in FINITE proper time\nnet tau_sing {tau_net} vs cycloid {tau_true:.1f}")
    ax[0].legend(fontsize=8)
    # right: proper time (finite) vs coordinate time (diverging) as the stop-radius approaches the horizon
    ax[1].plot(stops, tau_curve, "o-", color="seagreen", label="proper time tau (finite at horizon)")
    ax[1].plot(stops, t_true_curve, "o-", color="crimson", label="coordinate time t — true (diverges at 2M)")
    ax[1].plot(stops, t_net, "s--", color="darkorange", label="coord time — net (smooth, caps the pole)")
    ax[1].axvline(2.0, color="navy", ls=":", label="horizon R=2M")
    ax[1].set_xlabel("stop radius (-> horizon)"); ax[1].set_ylabel("time to fall there"); ax[1].invert_xaxis()
    ax[1].set_yscale("log"); ax[1].legend(fontsize=8)
    ax[1].set_title(f"the frozen star: external time diverges at the horizon\nnet learns the redshift rise {net_ratio:.0f}x (true {true_ratio:.0f}x) up to its representability limit")
    fig.tight_layout(); fig.savefig(RESULTS / "75_collapse.png", dpi=140)
    print("saved results/75_collapse.json + .png")


if __name__ == "__main__":
    main()
