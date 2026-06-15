"""Step 53 — OVERNIGHT Run 3 (quantum field): Proca / range as a LEARNABILITY knob.

Phase F was our one parked NULL: a local CNN could not learn the matter->field law for LONG-RANGE
1/r gravity (a known FNO-class result — magnitude needs global operators). The diagnosis was LOCALITY.
A Proca (massive) mediator screens the force into a short-range Yukawa e^{-mu r}/r. So sweeping the
mediator mass mu turns the force from long-range (mu=0, 1/r) to short-range (large mu), and should
flip learnability ON for a fixed small-receptive-field CNN once the range fits inside the RF. This
turns the parked failure into a tunable phase transition — and shows the Phase F wall was RANGE.

Setup: 32x32 grid (coords [-4,4]); a point source at a random location sources a Yukawa field
phi(x)=e^{-mu r}/(r+eps). A small-RF CNN (4x 3x3 conv, RF~9px~2.25 coord units) maps source->field.
Sweep mu. CONTROL: a large-RF CNN (dilated) at mu=0 should learn it (=> the wall is RF-vs-range,
not unlearnability in principle).

Pre-reg (2026-06-16):
  P1 short-range learnable: large-mu (range < RF) reconstruction R^2 > 0.9.
  P2 long-range fails:      mu=0 (1/r) small-RF R^2 < 0.6.
  P3 monotone transition:   R^2 increases as mu grows (range shrinks).
  P4 it's RF-vs-range:      large-RF CNN at mu=0 R^2 > small-RF at mu=0 by > 0.3 (range was the wall).
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

G = 32
STEPS = 4000
MUS = [0.0, 0.5, 1.0, 2.5]
coords = np.linspace(-4, 4, G).astype(np.float32)
GX, GY = np.meshgrid(coords, coords)


def make_data(mu, n=2500, seed=0):
    rng = np.random.default_rng(seed)
    x0 = rng.uniform(-3, 3, (n, 2)).astype(np.float32)
    src = np.exp(-((GX[None] - x0[:, 0, None, None]) ** 2 + (GY[None] - x0[:, 1, None, None]) ** 2) / (2 * 0.3 ** 2))
    r = np.sqrt((GX[None] - x0[:, 0, None, None]) ** 2 + (GY[None] - x0[:, 1, None, None]) ** 2)
    fld = np.exp(-mu * r) / (r + 0.5)
    fld = (fld - fld.mean()) / (fld.std() + 1e-8)                    # standardize for comparable R^2
    src = (src / (src.std() + 1e-8)).astype(np.float32)
    return torch.from_numpy(src[:, None]).float(), torch.from_numpy(fld[:, None]).float()


class CNN(nn.Module):
    def __init__(self, dilation=1):
        super().__init__()
        d = dilation
        self.net = nn.Sequential(
            nn.Conv2d(1, 32, 3, padding=d, dilation=d), nn.GELU(),
            nn.Conv2d(32, 32, 3, padding=d, dilation=d), nn.GELU(),
            nn.Conv2d(32, 32, 3, padding=d, dilation=d), nn.GELU(),
            nn.Conv2d(32, 1, 3, padding=d, dilation=d))

    def forward(self, x):
        return self.net(x)


def train_eval(mu, dilation, tag):
    src, fld = make_data(mu, seed=0)
    ntr = int(len(src) * 0.85)
    m = CNN(dilation); opt = torch.optim.Adam(m.parameters(), lr=2e-3)
    rng = np.random.default_rng(0)
    for step in range(STEPS):
        idx = rng.integers(0, ntr, 32)
        loss = nn.functional.mse_loss(m(src[idx]), fld[idx])
        opt.zero_grad(); loss.backward(); opt.step()
        if step % 250 == 0:
            progress(tag, step, STEPS, loss=float(loss.detach()))
    m.eval()
    with torch.no_grad():
        pred = m(src[ntr:]); tgt = fld[ntr:]
        r2 = float(1 - ((pred - tgt) ** 2).mean() / tgt.var())
    return r2


def main():
    smallRF = {}
    for mu in MUS:
        smallRF[mu] = train_eval(mu, 1, f"53_mu{mu}")
        print(f"small-RF  mu={mu:.1f} (range~{('inf' if mu==0 else round(1/mu,1))}): R^2 {smallRF[mu]:.3f}")
    bigRF_mu0 = train_eval(0.0, 3, "53_bigRF_mu0")   # dilated => larger RF, same depth
    print(f"large-RF  mu=0.0 (control): R^2 {bigRF_mu0:.3f}")

    r2s = [smallRF[mu] for mu in MUS]
    p1 = bool(r2s[-1] > 0.9)
    p2 = bool(r2s[0] < 0.6)
    p3 = bool(all(r2s[i + 1] >= r2s[i] - 0.05 for i in range(len(r2s) - 1)) and r2s[-1] > r2s[0] + 0.3)
    p4 = bool(bigRF_mu0 > smallRF[0.0] + 0.3)
    out = {"smallRF_R2_by_mu": {str(k): v for k, v in smallRF.items()}, "bigRF_mu0_R2": bigRF_mu0,
           "P1_shortrange_learnable": p1, "P2_longrange_fails": p2, "P3_monotone_transition": p3,
           "P4_wall_is_RF_vs_range": p4, "range_is_the_learnability_knob": bool(p1 and p2 and p3 and p4)}
    print(f"\nP1 short-range learnable (mu={MUS[-1]} R^2 {r2s[-1]:.2f}>0.9): {p1}")
    print(f"P2 long-range fails (mu=0 R^2 {r2s[0]:.2f}<0.6): {p2}")
    print(f"P3 monotone transition ({[round(x,2) for x in r2s]}): {p3}")
    print(f"P4 wall is RF-vs-range (bigRF mu0 {bigRF_mu0:.2f} > smallRF mu0 {smallRF[0.0]:.2f}+0.3): {p4}")
    print(f"\nRANGE IS THE LEARNABILITY KNOB (Phase F wall was locality): {out['range_is_the_learnability_knob']}")
    (RESULTS / "53_proca_range.json").write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.plot(MUS, r2s, "o-", color="teal", label="small-RF CNN (fixed ~9px)")
    ax.scatter([0.0], [bigRF_mu0], color="crimson", zorder=5, label="large-RF CNN @ mu=0 (control)")
    ax.axhline(0.9, ls=":", color="gray"); ax.set_xlabel("mediator mass μ  (range = 1/μ; μ=0 is 1/r)")
    ax.set_ylabel("field reconstruction R²"); ax.set_ylim(0, 1); ax.legend()
    ax.set_title("Proca range knob: short-range (local) is learnable, 1/r is not\n(the Phase F wall was locality)")
    fig.tight_layout(); fig.savefig(RESULTS / "53_proca_range.png", dpi=140)
    print("saved results/53_proca_range.json + .png")


if __name__ == "__main__":
    main()
