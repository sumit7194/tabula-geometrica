"""Step 80 — HAWKING RADIATION / THERMODYNAMICS: does a net discover T ~ 1/M and S = A/4?

Back to the Brian-Cox black-hole-entropy thread (S=A/4, Planck tiles on the horizon, the holographic bit).
Web-verified Schwarzschild thermodynamics (G=c=hbar=1): metric f(r)=1-2M/r; surface gravity kappa=1/2 f'(r_h)
=1/(4M); Hawking temperature T=kappa/2pi=1/(8piM); horizon area A=16pi M^2; Bekenstein-Hawking entropy
S=A/4=4pi M^2; first law dM=T dS (=> dS=8pi M dM). A net learns the metric f(r,M) from samples; from it we
read the horizon (f=0), the SURFACE GRAVITY (1/2 f' there) -> T, and the AREA -> then ask whether the
thermodynamic entropy int dM/T equals a quarter of the area.

Pre-reg (2026-06-17):
  H1 T ~ 1/M: the net's temperature T(M)=kappa/2pi (from the learned surface gravity) has log-log slope
     -1 vs M within 8%.
  H2 AREA LAW (holographic): the thermodynamic entropy S(M)=int dM/T scales as M^2 (∝ area), log-log slope
     +2 within 8% -- entropy tracks AREA, not volume.
  H3 S = A/4: the thermodynamic Delta-S equals Delta(A/4) across the mass range within 10% (the holographic
     quarter -- entropy is exactly one quarter of the horizon area).
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


def make_data(n=160000, seed=0):
    rng = np.random.default_rng(seed)
    M = rng.uniform(0.5, 5.0, n); r = 2 * M + 0.05 + rng.uniform(0, 18, n)
    f = 1.0 - 2 * M / r
    X = np.stack([r, M], 1).astype(np.float32); Y = f.astype(np.float32)[:, None]
    return X, Y


class Metric(nn.Module):
    def __init__(s):
        super().__init__(); s.net = nn.Sequential(nn.Linear(2, 128), nn.GELU(), nn.Linear(128, 128), nn.GELU(),
                                                  nn.Linear(128, 128), nn.GELU(), nn.Linear(128, 1))
    def forward(s, x): return s.net(x)


def main():
    X, Y = make_data()
    n = len(X); ntr = int(n * 0.9); idx = np.random.default_rng(0).permutation(n)
    Xt = torch.from_numpy(X[idx]); Yt = torch.from_numpy(Y[idx])
    m = Metric(); opt = torch.optim.Adam(m.parameters(), lr=1e-3); rng = np.random.default_rng(1)
    for step in range(7000):
        b = rng.integers(0, ntr, 256)
        loss = nn.functional.mse_loss(m(Xt[b]), Yt[b])
        opt.zero_grad(); loss.backward(); opt.step()
        if step % 400 == 0: progress("80_hawking", step, 7000, loss=float(loss.detach()))
    m.eval()
    with torch.no_grad():
        r2 = float(1 - ((m(Xt[ntr:]) - Yt[ntr:]) ** 2).sum() / ((Yt[ntr:] - Yt[ntr:].mean(0)) ** 2).sum())

    def f_and_df(r, M):                                   # net f and df/dr at (r,M)
        rt = torch.tensor([[r, M]], dtype=torch.float32, requires_grad=True)
        f = m(rt); df = torch.autograd.grad(f, rt)[0][0, 0].item()
        return f.item(), df

    Ms = np.linspace(0.7, 4.5, 40)
    r_h, kappa, area, T = [], [], [], []
    for M in Ms:
        rs = np.linspace(max(0.6, 2 * M - 1.0), 2 * M + 1.5, 400)   # find horizon: net f=0
        fv = np.array([m(torch.tensor([[r, M]], dtype=torch.float32)).item() for r in rs])
        s = np.where(np.diff(np.sign(fv)) != 0)[0]
        if not len(s):
            r_h.append(np.nan); kappa.append(np.nan); area.append(np.nan); T.append(np.nan); continue
        rh = float(rs[s[0]]); _, df = f_and_df(rh, M)
        k = 0.5 * df                                     # surface gravity = 1/2 f'(r_h)
        r_h.append(rh); kappa.append(k); area.append(4 * np.pi * rh ** 2); T.append(k / (2 * np.pi))
    Ms = np.array(Ms); T = np.array(T); area = np.array(area); ok = np.isfinite(T) & (T > 0)
    Ms, T, area = Ms[ok], T[ok], area[ok]

    # H1 T ~ 1/M
    sT = float(np.polyfit(np.log(Ms), np.log(T), 1)[0])
    # H2 area law: thermodynamic entropy S=int dM/T (anchor to area/4 at the first M), check S ~ M^2
    dM = np.diff(Ms); S = np.concatenate([[area[0] / 4], area[0] / 4 + np.cumsum(0.5 * (1 / T[1:] + 1 / T[:-1]) * dM)])
    sS = float(np.polyfit(np.log(Ms), np.log(S), 1)[0])
    # H3 S = A/4: thermodynamic S vs area/4
    Sarea = area / 4
    rel = float(np.median(np.abs(S - Sarea) / Sarea))
    ratio = float(np.median(S / area))                   # ~ 1/4

    h1 = bool(abs(sT - (-1)) < 0.08)
    h2 = bool(abs(sS - 2) < 0.08 * 2)
    h3 = bool(rel < 0.10 and abs(ratio - 0.25) < 0.03)
    out = {"metric_R2": r2, "T_vs_M_slope": sT, "entropy_vs_M_slope": sS,
           "S_vs_Aover4_median_relerr": rel, "S_over_A_ratio": ratio,
           "H1_T_inverse_M": h1, "H2_area_law": h2, "H3_S_equals_A_over_4": h3,
           "hawking_thermo_discovered": bool(h1 and h2 and h3)}
    print(f"H1 T ~ 1/M: log-log slope {sT:.3f} (want -1): {h1}")
    print(f"H2 area law S ~ M^2 (∝ A): slope {sS:.3f} (want 2): {h2}")
    print(f"H3 S = A/4: thermo-S vs A/4 relerr {rel:.3f}, S/A ratio {ratio:.3f} (want 0.25): {h3}")
    print(f"\nHAWKING THERMODYNAMICS DISCOVERED (T~1/M, S=A/4 holographic): {out['hawking_thermo_discovered']}")
    (RESULTS / "80_hawking_entropy.json").write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(1, 3, figsize=(16, 4.6))
    ax[0].loglog(Ms, T, "o", color="crimson", label=f"net T (slope {sT:.2f})"); ax[0].loglog(Ms, 1 / (8 * np.pi * Ms), "k:", label="1/(8πM)")
    ax[0].set_xlabel("mass M"); ax[0].set_ylabel("Hawking temperature T"); ax[0].legend(fontsize=8); ax[0].set_title("T ~ 1/M (from surface gravity)")
    ax[1].loglog(Ms, S, "o", color="navy", label=f"thermo S=∫dM/T (slope {sS:.2f})"); ax[1].loglog(Ms, 4 * np.pi * Ms ** 2, "k:", label="4πM²")
    ax[1].set_xlabel("mass M"); ax[1].set_ylabel("entropy S"); ax[1].legend(fontsize=8); ax[1].set_title("S ~ M² ∝ AREA (holographic)")
    ax[2].plot(area, S, "o", color="seagreen"); ax[2].plot(area, area / 4, "k:", label="S = A/4")
    ax[2].set_xlabel("horizon area A"); ax[2].set_ylabel("thermodynamic entropy S"); ax[2].legend(fontsize=8)
    ax[2].set_title(f"S = A/4 (ratio {ratio:.3f})")
    fig.tight_layout(); fig.savefig(RESULTS / "80_hawking_entropy.png", dpi=140)
    print("saved results/80_hawking_entropy.json + .png")


if __name__ == "__main__":
    main()
