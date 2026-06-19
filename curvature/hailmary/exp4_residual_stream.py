"""Hail Mary — Experiment 4: Plan B, the RESIDUAL-STREAM hand-off vs the clean-state hand-off.

Plan A (DOSnet) hands a *finished state* between modules -- clean and checkable, but LOSSY: the hand-off is
squeezed through the 3-channel width of a physical state. The user's Plan B (from the Coconut / Cache-to-Cache
latent-communication work): hand the next module the *raw hidden stream* instead, so info a clean output would
throw away is preserved. The bet: a richer hand-off shrinks the error (the lossy hand-off IS the splitting error).

Cleanest isolation: a 2-stage predictor where the ONLY difference is the inter-stage channel width b --
  CLEAN  (b=3):  stage1 squeezes to a 3-channel physical-state-width bottleneck, stage2 expands. (Plan A style.)
  STREAM (b=32): stage1 emits a wide latent, stage2 reads it. (Plan B style.)
Both push-forward trained (the stable method from Exp 3) and projected at rollout (constraint held either way).

Pre-reg (2026-06-20), grid 32, vacuum, horizon 100, 3 seeds:
  B1 STREAM HELPS: stream (b=32) mean long-rollout field MSE < clean (b=3) mean.
  B2 ROBUST: stream <= clean on >= 2/3 seeds AND stream's worst seed <= clean's worst (no new instability).
  (Honest caveat reported: the stream net has ~30% more params -- if it wins only marginally, capacity not
   hand-off-richness may explain it; a decisive win is the interesting outcome.)
"""

import argparse
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

from maxwell import make_dataset
from modules import div_E, leray_project, wavenumbers


class TwoStage(nn.Module):
    """state -> [stage1] -> hand-off (b channels) -> [stage2] -> residual next state. b=3 clean, b>>3 stream."""

    def __init__(self, b, ch=48):
        super().__init__()
        def block(cin, cout):
            return nn.Sequential(
                nn.Conv2d(cin, ch, 3, padding=1, padding_mode="circular"), nn.GELU(),
                nn.Conv2d(ch, ch, 3, padding=1, padding_mode="circular"), nn.GELU(),
                nn.Conv2d(ch, cout, 3, padding=1, padding_mode="circular"))
        self.s1 = block(3, b); self.s2 = block(b, 3)

    def forward(self, s):
        return s + self.s2(self.s1(s))


def project(s, KX, KY, K2safe):
    ex, ey = leray_project(s[:, 0], s[:, 1], KX, KY, K2safe)
    return torch.stack([ex, ey, s[:, 2]], 1)


def train_pf(net, tr, K, steps, KX, KY, K2safe, dev, seed):
    """push-forward training (Exp 3): j no-grad rollout steps, 1 graded step, grad-clip."""
    T, S = tr.shape[0], tr.shape[1] - 1
    opt = torch.optim.Adam(net.parameters(), lr=2e-3); rng = np.random.default_rng(seed); trd = torch.tensor(tr).to(dev)
    for st in range(steps):
        j = int(rng.integers(0, K)); ti = rng.integers(0, T, 32); t0 = rng.integers(0, S - j, 32)
        s = trd[ti, t0]
        if j > 0:
            with torch.no_grad():
                for _ in range(j):
                    s = project(net(s), KX, KY, K2safe)
        loss = nn.functional.mse_loss(project(net(s), KX, KY, K2safe), trd[ti, t0 + j + 1])
        opt.zero_grad(); loss.backward(); torch.nn.utils.clip_grad_norm_(net.parameters(), 1.0); opt.step()
    return net.eval()


@torch.no_grad()
def rollout_mse(net, s0, truth_t, horizon, KX, KY, K2safe):
    s = s0.clone()
    for _ in range(horizon):
        s = project(net(s), KX, KY, K2safe)
    return ((s - truth_t[:, -1]) ** 2).mean().item()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", default="mps" if torch.backends.mps.is_available() else ("cuda" if torch.cuda.is_available() else "cpu"))
    ap.add_argument("--grid", type=int, default=32); ap.add_argument("--traj", type=int, default=96)
    ap.add_argument("--K", type=int, default=4); ap.add_argument("--steps", type=int, default=2500)
    ap.add_argument("--horizon", type=int, default=100); ap.add_argument("--stream", type=int, default=32)
    ap.add_argument("--nseeds", type=int, default=3)
    a = ap.parse_args(); dev = a.device
    KX, KY, K2safe = wavenumbers(a.grid, 2 * np.pi, dev)
    res = Path(__file__).resolve().parent / "results"; res.mkdir(exist_ok=True)
    CHW = 60                                                          # widen clean's internal ch to match stream's params
    P = {"clean": sum(p.numel() for p in TwoStage(3).parameters()),
         "clean_wide": sum(p.numel() for p in TwoStage(3, ch=CHW).parameters()),
         "stream": sum(p.numel() for p in TwoStage(a.stream).parameters())}
    print(f"device={dev} grid={a.grid} K={a.K} steps={a.steps} | params {P}")

    cm, cwm, sm = [], [], []
    for seed in range(a.nseeds):
        tr, sim = make_dataset(n_traj=a.traj, nsteps=40, grid=a.grid, seed=seed)
        rng = np.random.default_rng(777 + seed)
        s0 = np.stack([sim.random_state(rng) for _ in range(16)]).astype(np.float32)
        truth = np.stack([sim.rollout(s0[i], a.horizon) for i in range(len(s0))]).astype(np.float32)
        truth_t = torch.tensor(truth).to(dev); s0_t = torch.tensor(s0).to(dev)
        def fit(net):
            return rollout_mse(train_pf(net.to(dev), tr, a.K, a.steps, KX, KY, K2safe, dev, seed), s0_t, truth_t, a.horizon, KX, KY, K2safe)
        torch.manual_seed(seed); mc = fit(TwoStage(3))
        torch.manual_seed(seed); mcw = fit(TwoStage(3, ch=CHW))
        torch.manual_seed(seed); ms = fit(TwoStage(a.stream))
        cm.append(mc); cwm.append(mcw); sm.append(ms)
        print(f"seed {seed}: clean(b=3,ch48) {mc:.2e}  clean_wide(b=3,ch{CHW}) {mcw:.2e}  stream(b={a.stream},ch48) {ms:.2e}  | stream/clean_wide {ms/mcw:.2f}")

    c, cw, s = np.array(cm), np.array(cwm), np.array(sm)
    b1 = bool(s.mean() < cw.mean())                                   # FAIR: stream vs capacity-matched clean
    b2 = bool(np.mean(s <= cw) >= 0.6 and s.max() <= cw.max())       # robust = wins on a clear majority AND never diverges
    out = {"device": dev, "stream_width": a.stream, "params": P,
           "clean_mse": cm, "clean_wide_mse": cwm, "stream_mse": sm,
           "clean_mean": float(c.mean()), "clean_wide_mean": float(cw.mean()), "stream_mean": float(s.mean()),
           "stream_over_cleanwide": float(s.mean() / cw.mean()), "stream_over_clean": float(s.mean() / c.mean()),
           "B1_stream_helps_vs_capacity_matched": b1, "B2_robust": b2, "residual_stream_beats_clean": bool(b1 and b2)}
    print(f"\nmean MSE: clean {c.mean():.2e}  clean_wide {cw.mean():.2e}  stream {s.mean():.2e}")
    print(f"  stream / clean_wide (FAIR, capacity-matched) = {s.mean()/cw.mean():.2f}")
    print(f"B1 stream beats capacity-matched clean (mean): {b1}")
    print(f"B2 robust (>=2/3 seeds + no worse worst-case vs clean_wide): {b2}")
    print(f"\nRESIDUAL-STREAM HAND-OFF BEATS CLEAN HAND-OFF (capacity-matched): {out['residual_stream_beats_clean']}")
    (res / "exp4_residual_stream.json").write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(figsize=(8.5, 5)); x = np.arange(a.nseeds); w = 0.27
    ax.bar(x - w, np.clip(c, 1e-6, None), w, color="silver", label="clean b=3 (narrow)")
    ax.bar(x, np.clip(cw, 1e-6, None), w, color="navy", label=f"clean b=3, ch{CHW} (capacity-matched)")
    ax.bar(x + w, np.clip(s, 1e-6, None), w, color="crimson", label=f"residual stream b={a.stream}")
    ax.set_yscale("log"); ax.set_xticks(x); ax.set_xticklabels([f"s{i}" for i in range(a.nseeds)])
    ax.set_ylabel("long-rollout final field MSE"); ax.legend(fontsize=8)
    ax.set_title(f"Plan B: rich latent hand-off vs clean state hand-off (capacity-matched)\nmean stream/clean_wide = {s.mean()/cw.mean():.2f}")
    fig.tight_layout(); fig.savefig(res / "exp4_residual_stream.png", dpi=140)
    print("saved hailmary/results/exp4_residual_stream.json + .png")


if __name__ == "__main__":
    main()
