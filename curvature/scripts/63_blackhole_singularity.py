"""Step 63 — PHASE BH-2: the SINGULARITY. From a learned black-hole metric, is the horizon SMOOTH
(finite curvature = a coordinate flip) while r=0 is a REAL singularity (curvature diverges), and is the
singularity SPACELIKE — a moment in time, the end of time?

Web-verified (BH-1 + standard GR): the r=2M horizon is a COORDINATE singularity (regular in EF coords),
the r=0 singularity is a real CURVATURE singularity; the Schwarzschild singularity is SPACELIKE (you
cannot avoid it — inside the horizon the future light cone tips so every future direction decreases r).
2D Ricci scalar of the radial metric: R = f'' = -g_vv'' = -4M/r^3 — FINITE at r=2M, DIVERGES as r->0.

Setup: a smooth net learns the metric component g_vv(r) for Schwarzschild (M=1) from noisy samples; we
read the curvature off its LEARNED metric via autodiff: R_hat(r) = -d^2 g_vv/dr^2 (2nd derivatives
amplify fit error -> a sensitive test). Causal structure: outgoing-null dr/dv = -g_vv/2 (escape if >0).

Pre-reg (2026-06-17):
  S1 horizon is SMOOTH: learned curvature is FINITE at r=2M and tracks -4M/r^3 there (the flip is a
     coordinate effect, NOT a singularity) — |R_hat(2) - (-0.5)| < 0.25 and corr(R_hat, true) > 0.95 on r>1.
  S2 r=0 is a REAL singularity: R_hat DIVERGES toward r->0, |R_hat(0.4)| > 15x |R_hat(2)| (the 1/r^3 blowup).
  S3 SPACELIKE singularity (end of time): the outgoing-null escape direction dr/dv = -g_vv/2 flips from
     POSITIVE (escape) outside r=2M to NEGATIVE (trapped) inside — r=0 becomes an unavoidable FUTURE.
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

M = 1.0
R_LO, R_HI, STEPS = 0.3, 6.0, 9000


def g_vv(r):
    return -(1 - 2 * M / r)


def make_data(n=120000, seed=0):
    rng = np.random.default_rng(seed)
    r = np.concatenate([rng.uniform(R_LO, R_HI, n // 2),
                        R_LO + (1.5 - R_LO) * rng.random(n // 2) ** 1.5]).astype(np.float32)  # extra density near small r
    y = (g_vv(r) + 0.01 * rng.standard_normal(len(r))).astype(np.float32)
    return r, y


class MetricNet(nn.Module):
    def __init__(s):
        super().__init__(); s.net = nn.Sequential(nn.Linear(1, 128), nn.Tanh(), nn.Linear(128, 128), nn.Tanh(),
                                                  nn.Linear(128, 128), nn.Tanh(), nn.Linear(128, 1))
    def forward(s, r):
        return s.net(r)[:, 0]


def train():
    r, y = make_data(); rt = torch.from_numpy(r)[:, None]; yt = torch.from_numpy(y)
    m = MetricNet(); opt = torch.optim.Adam(m.parameters(), lr=1e-3); rng = np.random.default_rng(0)
    for step in range(STEPS):
        idx = rng.integers(0, len(r), 512)
        loss = nn.functional.mse_loss(m(rt[idx]), yt[idx])
        opt.zero_grad(); loss.backward(); opt.step()
        if step % 600 == 0: progress("63_bh2", step, STEPS, loss=float(loss.detach()))
    m.eval(); return m


def curvature(m, rs):
    r = torch.tensor(rs, dtype=torch.float32, requires_grad=True)
    y = m(r[:, None])
    g1 = torch.autograd.grad(y.sum(), r, create_graph=True)[0]
    g2 = torch.autograd.grad(g1.sum(), r, create_graph=True)[0]
    return (-g2).detach().numpy()                       # R_hat = -g_vv''


def main():
    m = train()
    rs = np.linspace(R_LO + 0.05, R_HI - 0.05, 120).astype(np.float32)
    Rhat = curvature(m, rs); Rtrue = -4 * M / rs ** 3
    with torch.no_grad():
        gvv_hat = m(torch.from_numpy(rs)[:, None]).numpy()

    def at(rv): return float(Rhat[np.argmin(np.abs(rs - rv))])
    R_horizon = at(2.0); R_small = at(0.4)
    mid = rs > 1.0
    corr_mid = float(np.corrcoef(Rhat[mid], Rtrue[mid])[0, 1])
    # causal: outgoing-null escape dr/dv = -g_vv/2
    esc_out = -gvv_hat[np.argmin(np.abs(rs - 4.0))] / 2     # outside horizon (r=4)
    esc_in = -gvv_hat[np.argmin(np.abs(rs - 1.0))] / 2      # inside horizon (r=1)

    s1 = bool(abs(R_horizon - (-0.5)) < 0.25 and corr_mid > 0.95)
    s2 = bool(abs(R_small) > 15 * abs(R_horizon))
    s3 = bool(esc_out > 0.05 and esc_in < -0.05)
    out = {"R_at_horizon_r2": R_horizon, "R_true_horizon": -0.5, "R_at_small_r04": R_small,
           "blowup_ratio": abs(R_small) / abs(R_horizon), "curvature_corr_outside": corr_mid,
           "escape_outside_r4": float(esc_out), "escape_inside_r1": float(esc_in),
           "S1_horizon_smooth": s1, "S2_singularity_diverges": s2, "S3_spacelike_endoftime": s3,
           "singularity_understood": bool(s1 and s2 and s3)}
    print(f"S1 horizon SMOOTH: R_hat(2M)={R_horizon:.2f} (true -0.5), curvature corr(outside)={corr_mid:.3f} -> {s1}")
    print(f"S2 r=0 REAL singularity: R_hat(0.4)={R_small:.1f}, blowup {abs(R_small)/abs(R_horizon):.0f}x horizon -> {s2}")
    print(f"S3 SPACELIKE (end of time): escape dr/dv = {esc_out:+.2f} outside -> {esc_in:+.2f} inside (trapped) -> {s3}")
    print(f"\nSINGULARITY UNDERSTOOD (smooth horizon / divergent spacelike singularity): {out['singularity_understood']}")
    (RESULTS / "63_blackhole_singularity.json").write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(1, 2, figsize=(12, 4.6))
    ax[0].plot(rs, Rhat, "o-", color="purple", ms=3, label="learned curvature −g_vv''")
    ax[0].plot(rs, Rtrue, "--", color="gray", label="true −4M/r³")
    ax[0].axvline(2.0, color="crimson", ls=":", label="horizon r=2M (finite!)"); ax[0].set_ylim(-80, 5)
    ax[0].set_xlabel("r"); ax[0].set_ylabel("curvature R"); ax[0].legend(fontsize=8)
    ax[0].set_title("horizon SMOOTH (finite curvature), r→0 diverges = the real singularity")
    esc = -gvv_hat / 2
    ax[1].plot(rs, esc, "o-", color="seagreen", ms=3); ax[1].axhline(0, color="k", lw=0.6)
    ax[1].axvline(2.0, color="crimson", ls=":")
    ax[1].set_xlabel("r"); ax[1].set_ylabel("outgoing-null dr/dv (escape if >0)")
    ax[1].set_title("light cone tips over at the horizon:\noutside escapes (>0), inside is trapped (<0) → r=0 is the future")
    fig.tight_layout(); fig.savefig(RESULTS / "63_blackhole_singularity.png", dpi=140)
    print("saved results/63_blackhole_singularity.json + .png")


if __name__ == "__main__":
    main()
