"""Step 39 — the candidate SECOND law: legibility != steerability (read vs control).

Is a legible amortized code always a causal lever? Hypothesis: REDUNDANCY decouples read from
control — a property packed in one tight direction is read==control; a property spread
redundantly is readable from any piece but writing ONE direction gets overridden by the others.
Two amortized models on the abstract task (35): COMPACT (code dim 2) vs REDUNDANT (code dim 32 +
dropout on the code). Read = linear decode of p; Control = steer the read direction and measure
the output's counterfactual reach, vs an equal-norm random control. Pre-reg 2026-06-16.
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
from importlib import import_module
from sklearn.linear_model import Ridge
from torch import nn

s = import_module("35_legibility_scale")
XDIM, PDIM, KEX = s.XDIM, s.PDIM, s.KEX


class Amort2(nn.Module):
    """TWO encoder channels c1,c2 + channel-dropout -> p is redundantly encoded in BOTH, so the
    head can read it from either. Then steering ONE channel is overridden by the other."""
    def __init__(self, ch=8, width=128):
        super().__init__()
        mk = lambda: nn.Sequential(nn.Linear(XDIM + 1, width), nn.GELU(),
                                   nn.Linear(width, width), nn.GELU(), nn.Linear(width, ch))
        self.e1 = mk(); self.e2 = mk(); self.ch = ch
        self.head = nn.Sequential(nn.Linear(XDIM + 2 * ch, width), nn.GELU(),
                                  nn.Linear(width, width), nn.GELU(), nn.Linear(width, 1))

    def codes(self, ex, idx):
        e = ex[idx]; return self.e1(e).mean(1), self.e2(e).mean(1)

    def forward(self, ex, idx, x, train_drop=False, c1=None, c2=None):
        if c1 is None:
            c1, c2 = self.codes(ex, idx)
        if train_drop:  # randomly zero one channel so each must carry p
            r = torch.rand(c1.shape[0], 1)
            c1 = c1 * (r > 0.3).float(); c2 = c2 * (r < 0.7).float()
        c = torch.cat([c1, c2], 1)
        return self.head(torch.cat([x, c[:, None, :].expand(-1, x.shape[1], -1)], -1))[..., 0]


def train(steps=7000, n_obj=256, tag="redundant2ch"):
    world = s.World(width=128, seed=7)
    d = s.make_data(world, n_obj, per_obj=64, seed=0)
    ex, qx, qy = d["ex"], d["qx"], d["qy"]
    torch.manual_seed(39); rng = np.random.default_rng(0)
    m = Amort2(); opt = torch.optim.Adam(m.parameters(), lr=2e-3)
    for step in range(steps):
        idx = torch.tensor(rng.integers(0, n_obj, 128))
        loss = nn.functional.mse_loss(m(ex, idx, qx[idx], train_drop=True), qy[idx])
        opt.zero_grad(); loss.backward(); opt.step()
        if step % 500 == 0:
            progress(f"39_{tag}", step, steps, loss=float(loss.detach()))
    m.eval(); return m, d


def diff_dir(C, lo, hi):
    return C[hi].mean(0) - C[lo].mean(0)


def read_and_control(m, d, j=0):
    ex = d["ex"]; P = d["P"]; n = len(P); qx = d["qx"]
    with torch.no_grad():
        C1, C2 = m.codes(ex, torch.arange(n)); C1 = C1.numpy(); C2 = C2.numpy()
    # READ: decode p[j] from channel 1 ALONE (is it legible from a part?)
    read_r = float(np.corrcoef(Ridge(1.0).fit(C1, P[:, j]).predict(C1), P[:, j])[0, 1])
    lo = P[:, j] <= np.quantile(P[:, j], 0.33); hi = P[:, j] >= np.quantile(P[:, j], 0.67)
    d1 = diff_dir(C1, lo, hi); d2 = diff_dir(C2, lo, hi)     # on-manifold low->high per channel
    li = np.where(lo)[0]; hidx = np.where(hi)[0]
    c1l = torch.from_numpy(C1[li]).float(); c2l = torch.from_numpy(C2[li]).float()
    D1 = torch.from_numpy(d1).float(); D2 = torch.from_numpy(d2).float()

    def y_of(c1, c2):
        with torch.no_grad():
            return m(ex, torch.from_numpy(li), qx[li], c1=c1, c2=c2).numpy().mean()
    base = y_of(c1l, c2l)
    with torch.no_grad():
        hi_y = m(ex, torch.from_numpy(hidx), qx[hidx],
                 c1=torch.from_numpy(C1[hidx]).float(), c2=torch.from_numpy(C2[hidx]).float()).numpy().mean()
    reach = lambda v: float((v - base) / (hi_y - base + 1e-9))
    ctrl_one = reach(y_of(c1l + D1, c2l))        # steer ONE channel (read direction)
    ctrl_both = reach(y_of(c1l + D1, c2l + D2))  # steer BOTH (full intervention)
    print(f"READ p[{j}] from channel-1 alone: r={read_r:.3f}")
    print(f"CONTROL via channel-1 only: reach={ctrl_one:.3f} (read-only if low)")
    print(f"CONTROL via both channels:  reach={ctrl_both:.3f} (full lever)")
    return {"read_r": read_r, "control_one_channel": ctrl_one, "control_both": ctrl_both}


def main():
    m, d = train()
    r = read_and_control(m, d, j=0)
    second_law = bool(r["read_r"] > 0.8 and r["control_one_channel"] < 0.5 and r["control_both"] > 0.6)
    print(f"\nSECOND LAW (legible from a part, but that part is NOT the lever): "
          f"{'CONFIRMED' if second_law else 'NOT confirmed'}")
    print(f"  read {r['read_r']:.2f} (legible) | control via that channel {r['control_one_channel']:.2f} "
          f"(read-only) | control via both {r['control_both']:.2f} (lever)")
    r["second_law_confirmed"] = second_law
    (RESULTS / "39_read_vs_control.json").write_text(json.dumps(r, indent=1))

    fig, ax = plt.subplots(figsize=(6.5, 5))
    ax.bar([0, 1, 2], [r["read_r"], r["control_one_channel"], r["control_both"]],
           color=["seagreen", "crimson", "steelblue"])
    ax.set_xticks([0, 1, 2]); ax.set_xticklabels(["READ\n(1 channel)", "CONTROL\n(that channel)", "CONTROL\n(both)"])
    ax.axhline(0.5, ls="--", c="k", lw=0.6); ax.set_ylabel("score")
    ax.set_title("legibility != steerability: a readable direction need not be a lever")
    fig.tight_layout(); fig.savefig(RESULTS / "39_read_vs_control.png", dpi=140)
    print("saved results/39_read_vs_control.json + .png")


if __name__ == "__main__":
    main()
