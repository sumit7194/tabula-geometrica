"""Step 60 — PHASE BH-1: does the SPACE<->TIME FLIP emerge in a net that learns a black-hole interior?

The capstone return to black holes, armed with everything we've built. Web-verified physics: inside the
Schwarzschild horizon, t becomes SPACELIKE and r becomes TIMELIKE (timelike/spacelike curves switch
causal nature at r=2M); the r=0 singularity is SPACELIKE (a moment in time). Eddington-Finkelstein
coordinates (v,r) are REGULAR across the horizon, and the flip shows in the sign of g_vv.

EF metric (1+1 radial), M=1:  ds^2 = -(1 - 2M/r) dv^2 + 2 dv dr  (g_vv=-(1-2/r), g_vr=1, g_rr=0).
g_vv < 0 OUTSIDE (r>2, v is timelike) -> g_vv > 0 INSIDE (r<2, v is spacelike): the SPACE<->TIME swap.

Experiment (Phase-A/E paradigm): a generic net learns the local interval ds^2 from (position r,
displacement dv,dr) — NEVER told where the horizon is. We then PROBE the learned metric (fit the local
quadratic form per r) and ask whether the signature flip EMERGES at r=2.

Pre-reg (2026-06-17):
  BH1a learns the metric: fitted g_vv(r) matches true -(1-2/r), R^2 > 0.95 over the range.
  BH1b the flip is discovered: learned g_vv(r) crosses ZERO at r* with |r*-2| < 0.3 — the net located the
       horizon as the signature-flip locus, never told it.
  BH1c space<->time swap (causal character inverts): the learned g_vv is NEGATIVE outside (v timelike,
       r=5: g_vv<-0.2) and POSITIVE inside (v spacelike, r=1: g_vv>+0.2) — the v-direction that was your
       TIME becomes a SPACE direction. (In EF the swap lives in g_vv's sign; the timelike eigenvector
       also tilts toward r, reported as illustrative.)
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
R_MIN, R_MAX, STEPS = 0.6, 6.0, 9000


def g_vv_true(r):
    return -(1 - 2 * M / r)


def ds2(r, dv, dr):
    return g_vv_true(r) * dv ** 2 + 2 * dv * dr        # + g_rr dr^2, g_rr=0


def make_data(n=120000, seed=0):
    rng = np.random.default_rng(seed)
    r = rng.uniform(R_MIN, R_MAX, n).astype(np.float32)
    dv = rng.uniform(-0.3, 0.3, n).astype(np.float32)
    dr = rng.uniform(-0.3, 0.3, n).astype(np.float32)
    s = ds2(r, dv, dr).astype(np.float32)
    X = np.stack([r, dv, dr], 1)
    return X, s


class IntervalNet(nn.Module):
    """Generic black-box net: (r, dv, dr) -> ds^2. No metric structure imposed."""
    def __init__(s):
        super().__init__()
        s.net = nn.Sequential(nn.Linear(3, 128), nn.GELU(), nn.Linear(128, 128), nn.GELU(),
                              nn.Linear(128, 128), nn.GELU(), nn.Linear(128, 1))
    def forward(s, x):
        return s.net(x)[:, 0]


def train():
    X, y = make_data()
    Xt = torch.from_numpy(X); yt = torch.from_numpy(y)
    ntr = int(len(X) * 0.9)
    m = IntervalNet(); opt = torch.optim.Adam(m.parameters(), lr=1e-3)
    rng = np.random.default_rng(0)
    for step in range(STEPS):
        idx = torch.from_numpy(rng.integers(0, ntr, 512))
        loss = nn.functional.mse_loss(m(Xt[idx]), yt[idx])
        opt.zero_grad(); loss.backward(); opt.step()
        if step % 600 == 0: progress("60_bh", step, STEPS, loss=float(loss.detach()))
    m.eval()
    with torch.no_grad():
        test_r2 = float(1 - ((m(Xt[ntr:]) - yt[ntr:]) ** 2).mean() / yt[ntr:].var())
    return m, test_r2


def learned_metric(m, r):
    """Fit ds2_pred(dv,dr) = a dv^2 + 2b dv dr + c dr^2 at fixed r -> (a,b,c) = (g_vv,g_vr,g_rr)."""
    rng = np.random.default_rng(1)
    dv = rng.uniform(-0.25, 0.25, 400).astype(np.float32); dr = rng.uniform(-0.25, 0.25, 400).astype(np.float32)
    X = np.stack([np.full(400, r, np.float32), dv, dr], 1)
    with torch.no_grad():
        s = m(torch.from_numpy(X)).numpy()
    A = np.stack([dv ** 2, 2 * dv * dr, dr ** 2], 1)
    coef, *_ = np.linalg.lstsq(A, s, rcond=None)
    return coef                                          # (g_vv, g_vr, g_rr)


def timelike_angle(g):
    G = np.array([[g[0], g[1]], [g[1], g[2]]])
    w, V = np.linalg.eigh(G)
    v_time = V[:, np.argmin(w)]                          # negative eigenvalue = timelike direction
    return float(np.degrees(np.arctan2(abs(v_time[1]), abs(v_time[0]))))   # angle from v-axis (0=v, 90=r)


def main():
    m, test_r2 = train()
    rs = np.linspace(R_MIN + 0.05, R_MAX - 0.05, 60)
    gv = np.array([learned_metric(m, r) for r in rs])
    gvv_hat = gv[:, 0]; gvv_true = g_vv_true(rs)
    r2_metric = float(1 - np.sum((gvv_hat - gvv_true) ** 2) / np.sum((gvv_true - gvv_true.mean()) ** 2))
    # zero crossing of learned g_vv
    sgn = np.sign(gvv_hat)
    cross = np.where(np.diff(sgn) != 0)[0]
    r_star = float(rs[cross[0]] + (rs[cross[0] + 1] - rs[cross[0]]) * (0 - gvv_hat[cross[0]]) / (gvv_hat[cross[0] + 1] - gvv_hat[cross[0]])) if len(cross) else float("nan")
    ang_out = timelike_angle(learned_metric(m, 5.0)); ang_in = timelike_angle(learned_metric(m, 1.0))
    gvv_out = float(gvv_hat[np.argmin(abs(rs - 5.0))]); gvv_in = float(gvv_hat[np.argmin(abs(rs - 1.0))])

    bh1a = bool(r2_metric > 0.95)
    bh1b = bool(abs(r_star - 2.0) < 0.3)
    bh1c = bool(gvv_out < -0.2 and gvv_in > 0.2)         # v: timelike outside -> spacelike inside (the swap)
    out = {"interval_test_R2": test_r2, "metric_recover_R2": r2_metric, "horizon_r_star": r_star,
           "gvv_outside_r5": gvv_out, "gvv_inside_r1": gvv_in,
           "timelike_angle_outside_r5": ang_out, "timelike_angle_inside_r1": ang_in,
           "BH1a_learns_metric": bh1a, "BH1b_flip_discovered_at_horizon": bh1b,
           "BH1c_spacetime_swap": bh1c, "spacetime_flip_emerges": bool(bh1a and bh1b and bh1c)}
    print(f"interval test R^2 {test_r2:.4f}")
    print(f"BH1a learns metric (g_vv recover R^2 {r2_metric:.3f}>0.95): {bh1a}")
    print(f"BH1b flip discovered — learned g_vv crosses 0 at r*={r_star:.2f} (true horizon 2.0, |.|<0.3): {bh1b}")
    print(f"BH1c space<->time swap — learned g_vv: {gvv_out:+.2f} (out, v timelike) -> {gvv_in:+.2f} (in, v spacelike): {bh1c}")
    print(f"     (illustrative: timelike-direction angle {ang_out:.0f}° outside -> {ang_in:.0f}° inside, tilting toward r)")
    print(f"\nSPACE<->TIME FLIP EMERGES in the learned black-hole interior: {out['spacetime_flip_emerges']}")
    (RESULTS / "60_blackhole.json").write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(1, 2, figsize=(12, 4.6))
    ax[0].plot(rs, gvv_hat, "o-", color="purple", ms=3, label="learned g_vv")
    ax[0].plot(rs, gvv_true, "--", color="gray", label="true −(1−2M/r)")
    ax[0].axhline(0, color="k", lw=0.6); ax[0].axvline(2.0, color="crimson", ls=":", label="horizon r=2M")
    ax[0].set_xlabel("r"); ax[0].set_ylabel("g_vv (signature)"); ax[0].legend(fontsize=8)
    ax[0].set_title(f"g_vv flips sign at the horizon (learned r*={r_star:.2f})\nv is timelike outside, spacelike inside = the swap")
    angs = [timelike_angle(learned_metric(m, r)) for r in rs]
    ax[1].plot(rs, angs, "o-", color="seagreen", ms=3); ax[1].axvline(2.0, color="crimson", ls=":")
    ax[1].set_xlabel("r"); ax[1].set_ylabel("timelike direction angle (°): 0=v, 90=r")
    ax[1].set_title("the net's TIME direction rotates from v to r\nacross the horizon (space↔time swap)")
    fig.tight_layout(); fig.savefig(RESULTS / "60_blackhole.png", dpi=140)
    print("saved results/60_blackhole.json + .png")


if __name__ == "__main__":
    main()
