"""Step 131 — relativistic regime: a net discovers that boosts compose ADDITIVELY in RAPIDITY (not velocity).

Phase 1b separate-angle probe (notes/build_queue.md). The project's gravity phases (C, E) all ran SLOW-MOTION
(Newtonian geodesics). Here we go to the relativistic regime and ask the cleanest question in it: how do velocities
combine? Galileo says w = v1 + v2; Einstein says w = (v1 + v2)/(1 + v1 v2) (c=1). The deep fact (web-known special
relativity): the Lorentz group in 1+1 is just the real line under ADDITION, parameterized by RAPIDITY phi = atanh(v) --
boosts compose by phi = phi1 + phi2, and the messy velocity-addition law is only its nonlinear shadow w = tanh(phi).

Toy: an ADDITIVE-bottleneck net. A shared per-velocity map psi(v) (small MLP), summed psi(v1)+psi(v2), then a decoder
predicts the composed velocity w. The architecture BAKES IN only "boosts compose additively in SOME coordinate"; the
net must DISCOVER which coordinate makes addition correct. Because the 1+1 Lorentz group's additive parameter is unique
up to scale, the net is forced to find psi proportional to rapidity atanh(v) -- it rediscovers rapidity from the
composition law alone.

Pre-reg (2026-06-25):
  R1 ADDITIVE COORDINATE FITS: the additive-bottleneck net predicts the relativistic composition w on held-out
     (v1,v2) with R^2 > 0.98 -- boosts DO compose additively in the learned coordinate.
  R2 THE COORDINATE IS RAPIDITY: the learned psi(v) recovers rapidity atanh(v), |corr| > 0.99 (and psi is monotone
     odd, psi(0)=0) -- the net discovers rapidity as the natural additive coordinate of the Lorentz group.
  R3 RELATIVISTIC, NOT GALILEAN: a Galilean baseline (w = v1 + v2) FAILS in this regime -- it predicts SUPERLUMINAL
     |w| > 1 on a large fraction of high-speed pairs (> 0.2) and its MSE is >> the relativistic net's (ratio > 10);
     psi is NONLINEAR, coinciding with the Galilean psi=v only at low speed (atanh slope 1 at v=0).
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
from torch import nn

from curvlib import RESULTS, progress

VMAX = 0.95                                                        # sample boosts up to 0.95c (well into relativistic)


def compose(v1, v2):
    return (v1 + v2) / (1 + v1 * v2)                              # Einstein velocity addition (c=1)


def data(n, rng):
    v1 = rng.uniform(-VMAX, VMAX, n); v2 = rng.uniform(-VMAX, VMAX, n)
    return v1.astype(np.float32), v2.astype(np.float32), compose(v1, v2).astype(np.float32)


class Additive(nn.Module):
    """psi(v1) + psi(v2) -> decode w. The ONLY bias: boosts compose additively in SOME learned coordinate."""

    def __init__(s):
        super().__init__()
        s.psi = nn.Sequential(nn.Linear(1, 32), nn.Tanh(), nn.Linear(32, 32), nn.Tanh(), nn.Linear(32, 1))
        s.dec = nn.Sequential(nn.Linear(1, 32), nn.Tanh(), nn.Linear(32, 32), nn.Tanh(), nn.Linear(32, 1))

    def coord(s, v):
        return s.psi(v[:, None])[:, 0]

    def forward(s, v1, v2):
        sm = s.coord(v1) + s.coord(v2)
        return s.dec(sm[:, None])[:, 0]


def train(seed=0, steps=6000):
    torch.manual_seed(seed); rng = np.random.default_rng(seed)
    v1, v2, w = data(20000, rng)
    v1t, v2t, wt = torch.from_numpy(v1), torch.from_numpy(v2), torch.from_numpy(w)
    m = Additive(); opt = torch.optim.Adam(m.parameters(), lr=2e-3)
    g = np.random.default_rng(seed + 1)
    for step in range(steps):
        idx = g.integers(0, len(v1t), 512)
        pred = m(v1t[idx], v2t[idx])
        loss = nn.functional.mse_loss(pred, wt[idx])
        opt.zero_grad(); loss.backward(); opt.step()
        if step % 1500 == 0:
            progress("131_rapidity", step, steps, loss=float(loss.detach()))
    return m.eval()


def r2(pred, y):
    return float(1 - np.sum((pred - y) ** 2) / np.sum((y - y.mean()) ** 2))


def main():
    m = train()
    rng = np.random.default_rng(123)
    v1, v2, w = data(4000, rng)
    with torch.no_grad():
        pred = m(torch.from_numpy(v1), torch.from_numpy(v2)).numpy()
    R2 = r2(pred, w)
    r1 = bool(R2 > 0.98)

    # R2: the learned coordinate psi(v) vs rapidity atanh(v)
    vg = np.linspace(-VMAX, VMAX, 200).astype(np.float32)
    with torch.no_grad():
        psi = m.coord(torch.from_numpy(vg)).numpy()
    psi = psi - psi[len(vg) // 2]                                 # center so psi(0)=0 (additive coordinate origin)
    rap = np.arctanh(vg)
    corr_rap = float(abs(np.corrcoef(psi, rap)[0, 1]))
    corr_lin = float(abs(np.corrcoef(psi, vg)[0, 1]))             # vs the Galilean coordinate (velocity itself)
    r2g = bool(corr_rap > 0.99 and corr_rap > corr_lin)

    # R3: Galilean baseline fails in the relativistic regime
    hi = np.abs(v1) > 0.6                                          # high-speed pairs
    w_gal = v1 + v2
    frac_superluminal = float(np.mean(np.abs(w_gal[hi]) > 1.0))
    mse_gal = float(np.mean((w_gal - w) ** 2)); mse_rel = float(np.mean((pred - w) ** 2))
    ratio = mse_gal / (mse_rel + 1e-12)
    r3 = bool(frac_superluminal > 0.2 and ratio > 10 and corr_rap > corr_lin)

    out = {"R1_R2_fit": R2, "R2_psi_vs_rapidity": corr_rap, "R2_psi_vs_velocity": corr_lin,
           "R3_frac_superluminal_galilean": frac_superluminal, "R3_mse_galilean": mse_gal, "R3_mse_relativistic": mse_rel,
           "R3_mse_ratio": ratio, "R1_additive_coordinate_fits": r1, "R2_coordinate_is_rapidity": r2g,
           "R3_relativistic_not_galilean": r3, "relativistic_rapidity_discovered": bool(r1 and r2g and r3),
           "verdict": ("RAPIDITY DISCOVERED: an additive-bottleneck net -- biased ONLY to compose boosts additively in "
                       "some learned coordinate -- predicts Einstein's velocity addition (held-out R^2 {:.3f}) and the "
                       "coordinate it discovers IS rapidity atanh(v) (|corr| {:.3f}, vs {:.3f} for velocity). Boosts "
                       "compose additively in rapidity; the messy w=(v1+v2)/(1+v1 v2) is just its tanh shadow. The "
                       "Galilean law w=v1+v2 fails relativistically: it predicts SUPERLUMINAL |w|>1 on {:.0%} of "
                       "high-speed pairs and its MSE is {:.0f}x the relativistic net's. The net learns relativity from "
                       "the composition law alone."
                       .format(R2, corr_rap, corr_lin, frac_superluminal, ratio)
                       if (r1 and r2g and r3) else "PARTIAL -- see numbers (honest).")}
    print(f"R1 additive coordinate fits: held-out R2={R2:.3f} (>0.98): {r1}")
    print(f"R2 coordinate is rapidity: |corr(psi, atanh)|={corr_rap:.3f} (>0.99) vs velocity {corr_lin:.3f}: {r2g}")
    print(f"R3 relativistic not galilean: Galilean superluminal frac={frac_superluminal:.2f} (>0.2), MSE ratio={ratio:.0f} (>10): {r3}")
    print(f"\nRELATIVISTIC RAPIDITY DISCOVERED: {out['relativistic_rapidity_discovered']}")
    (RESULTS / "131_relativistic_rapidity.json").write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(1, 2, figsize=(12, 4.8))
    ax[0].plot(vg, psi / np.abs(psi).max(), color="seagreen", lw=2, label="learned ψ(v) (rescaled)")
    ax[0].plot(vg, rap / np.abs(rap).max(), "k--", lw=1.2, label="rapidity atanh(v)")
    ax[0].plot(vg, vg / np.abs(vg).max(), color="crimson", ls=":", lw=1.2, label="velocity v (Galilean)")
    ax[0].set_xlabel("velocity v"); ax[0].set_ylabel("additive coordinate (rescaled)"); ax[0].legend(fontsize=8)
    ax[0].set_title(f"R2 · the net discovers rapidity (|r|={corr_rap:.3f})")
    ax[1].scatter(w, pred, s=6, alpha=0.3, c="seagreen", label=f"relativistic net (R²={R2:.3f})")
    ax[1].scatter(w[hi], w_gal[hi], s=6, alpha=0.3, c="crimson", label="Galilean v₁+v₂ (high-v)")
    ax[1].axhline(1, ls=":", c="k", lw=0.6); ax[1].axhline(-1, ls=":", c="k", lw=0.6)
    ax[1].plot([-1, 1], [-1, 1], "k-", lw=0.5); ax[1].set_xlabel("true composed w"); ax[1].set_ylabel("predicted")
    ax[1].legend(fontsize=8); ax[1].set_title("R3 · Galilean goes superluminal (|w|>1)")
    fig.suptitle("Relativistic regime: boosts compose additively in rapidity (the net discovers atanh from the law alone)")
    fig.tight_layout(); fig.savefig(RESULTS / "131_relativistic_rapidity.png", dpi=140)
    print("saved results/131_relativistic_rapidity.json + .png")


if __name__ == "__main__":
    main()
