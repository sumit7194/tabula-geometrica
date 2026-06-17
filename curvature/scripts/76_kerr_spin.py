"""Step 76 — SPIN: a rotating (Kerr) black hole. Can a net discover frame-dragging + the ergosphere?

Beyond Schwarzschild: a spinning hole drags spacetime around with it. Web-verified equatorial Kerr geodesics
(Boyer-Lindquist, G=M=c=1, spin a in [0,1)):
  Delta = r^2 - 2r + a^2 ;  T = E(r^2+a^2) - L a
  r^2 dphi/dtau = V_phi = -(aE - L) + a T/Delta
  r^2 dt/dtau   = V_t   = -a(aE - L) + (r^2+a^2) T/Delta
  (r^2 dr/dtau)^2 = V_r = T^2 - Delta(r^2 + (L-aE)^2)
FRAME-DRAGGING fingerprint: a ZERO-angular-momentum particle (L=0, E=1) still rotates: dphi/dtau = 2a/(rDelta)
> 0 (Schwarzschild a=0 -> 0). ERGOSPHERE (static limit, equatorial r=2M): inside it NOTHING can stand still --
even a maximally counter-rotating particle is forced to co-rotate; algebraically V_phi(r=2)=4E/a>0 for ALL L,
and the large-counter-rotation limit of dphi/dt is -(r-2)/(2a), which crosses 0 exactly at r=2M.

A net learns (a_r, dphi/dtau, dt/dtau) as functions of (r, a, E, L) from Kerr orbit samples, then we read the
physics off the learned functions and roll out a dragged orbit.

Pre-reg (2026-06-17):
  K1 learns the dynamics: held-out R^2 > 0.999 (all three outputs).
  K2 FRAME DRAGGING: for L=0,E=1,a=0.9 the net's dphi/dtau matches 2a/(rDelta) within 10% (positive,
     rising inward); the a=0 control gives ~0. A zero-angular-momentum particle is dragged.
  K3 ERGOSPHERE: for a strongly counter-rotating particle (L=-12, a=0.9) the net's dphi/dt crosses zero
     (forced co-rotation) at r = 2M within 12% -- the static-limit surface emerges.
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

np.seterr(all="ignore")


def horizon(a): return 1.0 + np.sqrt(np.maximum(1 - a ** 2, 0))


def rdot2(r, a, E, L):
    D = r ** 2 - 2 * r + a ** 2; T = E * (r ** 2 + a ** 2) - L * a
    return (T ** 2 - D * (r ** 2 + (L - a * E) ** 2)) / r ** 4


def kerr_terms(r, a, E, L):
    D = r ** 2 - 2 * r + a ** 2; T = E * (r ** 2 + a ** 2) - L * a
    dphi = (-(a * E - L) + a * T / D) / r ** 2
    dt = (-a * (a * E - L) + (r ** 2 + a ** 2) * T / D) / r ** 2
    h = 1e-3
    ar = 0.5 * (rdot2(r + h, a, E, L) - rdot2(r - h, a, E, L)) / (2 * h)   # d^2r/dtau^2 = 1/2 d(rdot^2)/dr
    return ar, dphi, dt


def make_data(n=300000, seed=0):
    rng = np.random.default_rng(seed)
    a = rng.uniform(0.0, 0.95, n); E = rng.uniform(0.92, 1.08, n); L = rng.uniform(-12, 12, n)
    r = horizon(a) + 0.4 + rng.uniform(0, 20, n)         # stay off the near-horizon blow-up
    ar, dphi, dt = kerr_terms(r, a, E, L)
    X = np.stack([r, a, E, L], 1).astype(np.float32); Y = np.stack([ar, dphi, dt], 1).astype(np.float32)
    ok = np.isfinite(Y).all(1) & (np.abs(Y) < 40).all(1)  # tighter cap -> well-conditioned regression
    return X[ok], Y[ok]


class KerrNet(nn.Module):
    def __init__(s, mu, sd):
        super().__init__()
        s.register_buffer("mu", torch.tensor(mu)); s.register_buffer("sd", torch.tensor(sd))
        s.net = nn.Sequential(nn.Linear(4, 256), nn.GELU(), nn.Linear(256, 256), nn.GELU(),
                              nn.Linear(256, 256), nn.GELU(), nn.Linear(256, 256), nn.GELU(), nn.Linear(256, 3))
    def forward(s, x): return s.net(x) * s.sd + s.mu          # de-standardized outputs


def main():
    X, Y = make_data(); mu = Y.mean(0); sd = Y.std(0) + 1e-6
    n = len(X); ntr = int(n * 0.9); idx = np.random.default_rng(0).permutation(n)
    Xt = torch.from_numpy(X[idx]); Yt = torch.from_numpy(Y[idx])
    m = KerrNet(mu, sd); opt = torch.optim.Adam(m.parameters(), lr=1e-3)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, 14000); rng = np.random.default_rng(1)
    for step in range(14000):
        b = rng.integers(0, ntr, 1024)
        loss = nn.functional.mse_loss((m(Xt[b]) - m.mu) / m.sd, (Yt[b] - m.mu) / m.sd)
        opt.zero_grad(); loss.backward(); opt.step(); sched.step()
        if step % 700 == 0: progress("76_kerr", step, 14000, loss=float(loss.detach()))
    m.eval()
    with torch.no_grad():
        P = m(Xt[ntr:]); r2 = float(1 - ((P - Yt[ntr:]) ** 2).sum() / ((Yt[ntr:] - Yt[ntr:].mean(0)) ** 2).sum())

    def net_terms(r, a, E, L):
        x = torch.tensor(np.stack([r, np.full_like(r, a), np.full_like(r, E), np.full_like(r, L)], 1), dtype=torch.float32)
        with torch.no_grad():
            o = m(x).numpy()
        return o[:, 0], o[:, 1], o[:, 2]

    # K2 frame dragging: L=0, E=1. Measure the match where dragging is physically significant (inner region);
    # the rate ~2a/(rDelta) vanishes at large r so relative error there is ill-defined.
    rr = np.linspace(2.2, 20, 80)
    _, dphi_net, _ = net_terms(rr, 0.9, 1.0, 0.0)
    dphi_true = 2 * 0.9 / (rr * (rr ** 2 - 2 * rr + 0.81))
    _, dphi_schw, _ = net_terms(rr, 0.0, 1.0, 0.0)
    rr_d = np.linspace(2.2, 6.0, 60)
    _, dphi_net_d, _ = net_terms(rr_d, 0.9, 1.0, 0.0)
    dphi_true_d = 2 * 0.9 / (rr_d * (rr_d ** 2 - 2 * rr_d + 0.81))
    drag_err = float(np.median(np.abs(dphi_net_d - dphi_true_d) / (np.abs(dphi_true_d) + 1e-6)))
    drag_pos = bool(np.all(dphi_net_d > 0) and dphi_net_d[0] > dphi_net_d[-1])   # positive & rising inward
    schw_zero = float(np.median(np.abs(dphi_schw)))

    # K3 ergosphere: strongly counter-rotating L=-12, a=0.9; dphi/dt zero crossing -> 2M
    rr2 = np.linspace(1.9, 4.5, 140)
    _, dphi2, dt2 = net_terms(rr2, 0.9, 1.0, -12.0)
    dphidt = dphi2 / dt2
    sgn = np.where(np.diff(np.sign(dphidt)) != 0)[0]
    r_ergo_net = float(rr2[sgn[0]]) if len(sgn) else None

    k1 = bool(r2 > 0.999)
    k2 = bool(drag_err < 0.10 and drag_pos and schw_zero < 0.02)
    k3 = bool(r_ergo_net is not None and abs(r_ergo_net - 2.0) < 0.12 * 2.0)
    out = {"R2": r2, "frame_drag_median_relerr": drag_err, "frame_drag_positive_rising": drag_pos,
           "schwarzschild_dphi_dtau": schw_zero, "ergosphere_r_net": r_ergo_net, "ergosphere_r_true": 2.0,
           "K1_learns_dynamics": k1, "K2_frame_dragging": k2, "K3_ergosphere": k3,
           "kerr_spin_discovered": bool(k1 and k2 and k3)}
    print(f"K1 learns dynamics R^2 {r2:.5f}: {k1}")
    print(f"K2 frame dragging (L=0): net dphi/dtau matches 2a/(rD) relerr {drag_err:.3f}, positive&rising {drag_pos}, "
          f"a=0 control {schw_zero:.4f}: {k2}")
    print(f"K3 ergosphere: counter-rotating dphi/dt zero-crossing r_net {r_ergo_net} (want 2M): {k3}")
    print(f"\nKERR SPIN DISCOVERED (frame-dragging + ergosphere from a learned simulator): {out['kerr_spin_discovered']}")
    (RESULTS / "76_kerr_spin.json").write_text(json.dumps(out, indent=1))

    # roll out a dragged L=0 orbit (Kerr a=0.9) vs Schwarzschild (a=0): radial infall gets twisted
    def roll(a, r0=12.0, nsteps=1400, dtau=0.03):
        r, vr, phi = r0, 0.0, 0.0; R, PH = [r], [phi]
        for _ in range(nsteps):
            ar, dphi, _ = net_terms(np.array([r]), a, 1.0, 0.0)
            vr += dtau * float(ar[0]); r += dtau * vr; phi += dtau * float(dphi[0])
            if r < horizon(a) + 0.2 or r > 30: break
            R.append(r); PH.append(phi)
        return np.array(R), np.array(PH)
    Rk, PHk = roll(0.9); Rs, PHs = roll(0.0)
    fig, ax = plt.subplots(1, 2, figsize=(13, 5.5))
    ax[0].plot(Rk * np.cos(PHk), Rk * np.sin(PHk), color="crimson", lw=1, label="Kerr a=0.9 (dragged)")
    ax[0].plot(Rs * np.cos(PHs), Rs * np.sin(PHs), color="navy", lw=1, ls="--", label="Schwarzschild a=0 (radial)")
    th = np.linspace(0, 2 * np.pi, 100)
    ax[0].fill(horizon(0.9) * np.cos(th), horizon(0.9) * np.sin(th), "k")
    ax[0].plot(2 * np.cos(th), 2 * np.sin(th), color="orange", ls=":", label="ergosphere 2M")
    ax[0].set_aspect("equal"); ax[0].legend(fontsize=8)
    ax[0].set_title("frame-dragging: a zero-angular-momentum particle\nis twisted around the spinning hole (red) vs radial (blue)")
    ax[1].plot(rr, dphi_net, color="crimson", label="net dphi/dtau (L=0, a=0.9)")
    ax[1].plot(rr, dphi_true, "k:", label="GR 2a/(rDelta)")
    ax[1].plot(rr, dphi_schw, color="navy", ls="--", label="a=0 (no dragging)")
    ax[1].set_xlabel("r"); ax[1].set_ylabel("dphi/dtau (dragging rate)"); ax[1].legend(fontsize=8)
    ax[1].set_title(f"frame-dragging rate matches GR (relerr {drag_err:.2f}); ergosphere r_net={r_ergo_net:.2f}")
    fig.tight_layout(); fig.savefig(RESULTS / "76_kerr_spin.png", dpi=140)
    print("saved results/76_kerr_spin.json + .png")


if __name__ == "__main__":
    main()
