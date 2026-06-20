"""Hail Mary Phase 2 (learning v3) — DIAGNOSTIC: WHY does the (Phi,Pi) emulator drive everything to collapse?

If exp10 shows even a spectral FNO fails the criticality classification, this isolates the MECHANISM (the
ai-coding-standards "overfit one batch" + targeted reproduction diagnostics), so the negative is explained, not
just observed. Two questions:

  D1 CAPACITY (overfit one trajectory): train the net on a SINGLE disperse trajectory and test reproduction of
     THAT trajectory. If it cannot even reproduce one disperse rollout (peak 2m/r stays low, field MSE small),
     the wall is representational/optimization -- NOT data or criticality. (Expect: this is the real wall.)

  D2 DISSIPATION/CONCENTRATION (the mechanism): train on disperse-only, roll a held-out disperse case, and track
     peak-2m/r(t) and field-MSE(t) vs truth. Truth disperses (peak 2m/r DROPS as the pulse spreads outward);
     if the net's peak-2m/r instead CLIMBS, the emulator concentrates when it should spread -- the direct cause
     of "collapse everything." Pinpoints WHEN the rollout departs the truth.

Self-contained (own train + ground truth). Arch selectable (--arch fno|cnn) so we diagnose the better one.
"""

import argparse
import json
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
sys.path.insert(0, str(Path(__file__).resolve().parent))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import torch
from torch import nn

from collapse import ScalarCollapse
from modules import FNO1d
from exp10_collapse_fno import CNN1d, gen, train_pf


@torch.no_grad()
def rollout(net, sim, s0, T, dev):
    """roll net T steps; return field-MSE-able states + peak-2m/r(t) curve."""
    s = torch.tensor(s0[None]).to(dev); states = [s0.copy()]; peak_t = [sim.max_2m_over_r(s0[0], s0[1])]
    for _ in range(T):
        s = net(s)
        if not torch.isfinite(s).all():
            break
        a = s[0].cpu().numpy(); states.append(a); peak_t.append(sim.max_2m_over_r(a[0], a[1]))
    return np.array(states), np.array(peak_t)


def make_net(arch, width, modes):
    return FNO1d(2, 2, width=width, modes=modes) if arch == "fno" else CNN1d(ch=width)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", default="mps" if torch.backends.mps.is_available() else ("cuda" if torch.cuda.is_available() else "cpu"))
    ap.add_argument("--arch", default="fno", choices=["fno", "cnn"])
    ap.add_argument("--n", type=int, default=300); ap.add_argument("--t-end", type=float, default=10.0)
    ap.add_argument("--stride", type=int, default=8); ap.add_argument("--steps", type=int, default=8000)
    ap.add_argument("--K", type=int, default=4); ap.add_argument("--width", type=int, default=64); ap.add_argument("--modes", type=int, default=48)
    a = ap.parse_args(); dev = a.device
    sim = ScalarCollapse(n=a.n, R=20.0, cfl=0.2); res = Path(__file__).resolve().parent / "results"; res.mkdir(exist_ok=True)
    print(f"device={dev} arch={a.arch} n={a.n} steps={a.steps}")

    # --- D1: overfit ONE disperse trajectory ---
    one = gen(sim, np.array([0.03]), a.t_end, a.stride)[0]          # (1, T, 2, n), clearly disperse
    T = one.shape[1]
    net1 = train_pf(lambda: make_net(a.arch, a.width, a.modes), one, a.steps, a.K, dev, 0)
    states, peak_t = rollout(net1, sim, one[0, 0], T - 1, dev)
    truth_peak_t = np.array([sim.max_2m_over_r(one[0, t, 0], one[0, t, 1]) for t in range(T)])
    n_done = len(states)
    field_mse = float(np.mean((states[:n_done] - one[0, :n_done]) ** 2))
    d1 = bool(n_done == T and peak_t.max() < 0.5 and field_mse < 1e-2)
    print(f"D1 overfit-one-disperse: net peak2m/r {peak_t.max():.3f} (truth {truth_peak_t.max():.3f}) | "
          f"field MSE {field_mse:.2e} | finite {n_done}/{T} -> reproduces disperse: {d1}")

    # --- D2: train disperse-only, roll a HELD-OUT disperse case, track concentration vs dissipation ---
    disp_train = gen(sim, np.array([0.02, 0.025, 0.03, 0.035, 0.04]), a.t_end, a.stride)[0]
    Td = disp_train.shape[1]
    net2 = train_pf(lambda: make_net(a.arch, a.width, a.modes), disp_train, a.steps, a.K, dev, 1)
    held = gen(sim, np.array([0.032]), a.t_end, a.stride)[0][0]      # held-out disperse
    Th = min(Td, held.shape[0]); held = held[:Th]
    st2, peak2 = rollout(net2, sim, held[0], Th - 1, dev)
    truth_peak2 = np.array([sim.max_2m_over_r(held[t, 0], held[t, 1]) for t in range(Th)])
    climbs = bool(len(peak2) > 3 and peak2[-1] > peak2[0] + 0.05)    # net concentrates (wrong) instead of spreading
    truth_drops = bool(truth_peak2[-1] < truth_peak2[0])
    print(f"D2 disperse-only -> held-out disperse: truth peak2m/r {truth_peak2[0]:.3f}->{truth_peak2[-1]:.3f} (drops {truth_drops}); "
          f"net {peak2[0]:.3f}->{peak2[-1]:.3f} (climbs {climbs})")
    print(f"   MECHANISM: emulator concentrates when truth spreads = {climbs and truth_drops}")

    out = {"arch": a.arch, "D1_overfit_one_disperse": d1, "D1_net_peak": float(peak_t.max()),
           "D1_field_mse": field_mse, "D1_finite": f"{n_done}/{T}",
           "D2_truth_peak_traj": truth_peak2.tolist(), "D2_net_peak_traj": peak2.tolist(),
           "D2_net_concentrates_truth_spreads": bool(climbs and truth_drops)}
    (res / f"exp11_diagnose_{a.arch}.json").write_text(json.dumps(out, indent=1))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5))
    ax1.plot(truth_peak_t, "k-", label="truth"); ax1.plot(peak_t, "crimson", label=f"{a.arch} rollout")
    ax1.axhline(0.5, color="gray", ls=":", lw=0.8); ax1.set_title(f"D1 overfit ONE disperse traj (field MSE {field_mse:.1e})")
    ax1.set_xlabel("snapshot"); ax1.set_ylabel("peak 2m/r"); ax1.legend(fontsize=8)
    ax2.plot(truth_peak2, "k-", label="truth (disperses)"); ax2.plot(peak2, "crimson", label=f"{a.arch} (concentrates?)")
    ax2.axhline(0.5, color="gray", ls=":", lw=0.8); ax2.set_title("D2 disperse-only -> held-out disperse")
    ax2.set_xlabel("snapshot"); ax2.set_ylabel("peak 2m/r"); ax2.legend(fontsize=8)
    fig.suptitle(f"Mechanism of the emulator failure ({a.arch})"); fig.tight_layout()
    fig.savefig(res / f"exp11_diagnose_{a.arch}.png", dpi=140)
    print(f"saved hailmary/results/exp11_diagnose_{a.arch}.json + .png")


if __name__ == "__main__":
    main()
