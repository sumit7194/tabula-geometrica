"""Step 64 — PHASE BH-3: what CHARGE does to the causal structure (Reissner-Nordström).

Web-verified (and BH-1/BH-2): adding charge Q gives f(r)=1-2M/r+Q^2/r^2. Two consequences a net should
read out of its LEARNED metric:
  (1) TWO horizons (outer r+ and inner/Cauchy r- = M ± sqrt(M^2-Q^2)) instead of one — g_vv flips sign TWICE.
  (2) the singularity becomes TIMELIKE (avoidable), NOT spacelike like Schwarzschild's "end of time":
      as r->0 the Q^2/r^2 term dominates -> f>0 -> g_vv<0 -> r is SPACELIKE near r=0 -> you can avoid r=0.
This is "what happens to other properties (charge) across the horizon" — calibrated on the KNOWN
Q -> timelike-singularity relation (the test the sister glass-box analyzer could independently verify).

Setup: one net learns g_vv(r, Q) for M=1, Q in [0,0.9], r in [0.15,6]. Read horizons (zero-crossings)
and the singularity character (sign of g_vv as r->0) vs Q.

Pre-reg (2026-06-17):
  C1 two horizons: for Q=0.8 the learned g_vv(r) crosses zero TWICE, near r-=0.4 and r+=1.6 (|err|<0.25 each).
  C2 charge -> TIMELIKE singularity: learned g_vv(r=0.2) is NEGATIVE for Q=0.8 (r spacelike, avoidable) but
     POSITIVE for Q=0 (Schwarzschild, spacelike/unavoidable) — charge FLIPS the singularity's causal character.
  C3 the contrast: #horizons goes 1 (Q=0) -> 2 (Q=0.8); singularity spacelike -> timelike.
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
R_LO, R_HI, STEPS = 0.15, 6.0, 11000


def g_vv(r, Q):
    return -(1 - 2 * M / r + Q ** 2 / r ** 2)


def make_data(n=200000, seed=0):
    rng = np.random.default_rng(seed)
    r = np.concatenate([rng.uniform(R_LO, R_HI, n // 2),
                        R_LO + (2.0 - R_LO) * rng.random(n // 2) ** 1.6]).astype(np.float32)   # dense near small r
    Q = rng.uniform(0.0, 0.9, len(r)).astype(np.float32)
    y = (g_vv(r, Q) + 0.01 * rng.standard_normal(len(r))).astype(np.float32)
    X = np.stack([r, Q], 1)
    return X, y


class MetricNet(nn.Module):
    def __init__(s):
        super().__init__(); s.net = nn.Sequential(nn.Linear(2, 160), nn.Tanh(), nn.Linear(160, 160), nn.Tanh(),
                                                  nn.Linear(160, 160), nn.Tanh(), nn.Linear(160, 1))
    def forward(s, x):
        return s.net(x)[:, 0]


def train():
    X, y = make_data(); Xt = torch.from_numpy(X); yt = torch.from_numpy(y)
    m = MetricNet(); opt = torch.optim.Adam(m.parameters(), lr=1e-3); rng = np.random.default_rng(0)
    for step in range(STEPS):
        idx = rng.integers(0, len(X), 512)
        loss = nn.functional.mse_loss(m(Xt[idx]), yt[idx])
        opt.zero_grad(); loss.backward(); opt.step()
        if step % 700 == 0: progress("64_bh3", step, STEPS, loss=float(loss.detach()))
    m.eval(); return m


def gvv_curve(m, Q, rs):
    X = np.stack([rs, np.full_like(rs, Q)], 1).astype(np.float32)
    with torch.no_grad():
        return m(torch.from_numpy(X)).numpy()


def zero_crossings(rs, g):
    cr = np.where(np.diff(np.sign(g)) != 0)[0]
    return [float(rs[i] + (rs[i + 1] - rs[i]) * (0 - g[i]) / (g[i + 1] - g[i])) for i in cr]


def main():
    m = train()
    rs = np.linspace(R_LO + 0.02, 4.0, 200).astype(np.float32)
    g_rn = gvv_curve(m, 0.8, rs); g_sch = gvv_curve(m, 0.0, rs)
    hor_rn = zero_crossings(rs, g_rn); hor_sch = zero_crossings(rs, g_sch)
    gv02_rn = float(gvv_curve(m, 0.8, np.array([0.2], np.float32))[0])
    gv02_sch = float(gvv_curve(m, 0.0, np.array([0.2], np.float32))[0])

    near = [h for h in hor_rn if 0.4 - 0.25 < h < 0.4 + 0.25]
    far = [h for h in hor_rn if 1.6 - 0.25 < h < 1.6 + 0.25]
    c1 = bool(len(near) >= 1 and len(far) >= 1)
    c2 = bool(gv02_rn < 0 and gv02_sch > 0)
    c3 = bool(len([h for h in hor_rn if h > R_LO + 0.05]) == 2 and len([h for h in hor_sch if h > R_LO + 0.05]) == 1 and c2)
    out = {"RN_horizons": hor_rn, "RN_true_horizons": [0.4, 1.6], "Schwarzschild_horizons": hor_sch,
           "gvv_at_r0.2_RN": gv02_rn, "gvv_at_r0.2_Schwarzschild": gv02_sch,
           "C1_two_horizons": c1, "C2_charge_makes_singularity_timelike": c2, "C3_contrast": c3,
           "charge_changes_causal_structure": bool(c1 and c2 and c3)}
    print(f"C1 two horizons (Q=0.8): learned {[round(h,2) for h in hor_rn]} vs true [0.4, 1.6] -> {c1}")
    print(f"C2 charge -> TIMELIKE singularity: g_vv(0.2) = {gv02_rn:+.1f} (Q=0.8, r spacelike=avoidable) vs {gv02_sch:+.1f} (Q=0, r timelike=unavoidable) -> {c2}")
    print(f"C3 contrast: Schwarzschild horizons {[round(h,2) for h in hor_sch]} (1, spacelike sing.) vs RN (2, timelike sing.) -> {c3}")
    print(f"\nCHARGE CHANGES THE CAUSAL STRUCTURE (2 horizons + timelike singularity): {out['charge_changes_causal_structure']}")
    (RESULTS / "64_blackhole_charge.json").write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(figsize=(7.5, 5))
    ax.plot(rs, g_sch, "-", color="navy", label="Schwarzschild (Q=0): 1 horizon, g_vv→+∞ (spacelike sing.)")
    ax.plot(rs, g_rn, "-", color="crimson", label="Reissner-Nordström (Q=0.8): 2 horizons, g_vv→−∞ (timelike sing.)")
    ax.axhline(0, color="k", lw=0.6); ax.set_ylim(-15, 12)
    for h in hor_rn: ax.axvline(h, color="crimson", ls=":", lw=0.8)
    ax.set_xlabel("r"); ax.set_ylabel("learned g_vv")
    ax.set_title("what charge does: a second (inner) horizon, and the singularity\nflips spacelike (end of time) → timelike (avoidable)")
    ax.legend(fontsize=7.5); fig.tight_layout(); fig.savefig(RESULTS / "64_blackhole_charge.png", dpi=140)
    print("saved results/64_blackhole_charge.json + .png")


if __name__ == "__main__":
    main()
