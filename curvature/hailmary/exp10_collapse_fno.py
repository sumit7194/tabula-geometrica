"""Hail Mary Phase 2 (learning v3) — RIGOROUS: can a PROPER net (FNO) learn Choptuik criticality?

v1 used ONE modest local CNN and failed (collapsed everything). That was an honest negative for THAT config, NOT
proof nets can't do it -- and the literature (PINNs near criticality) shows it IS learnable with effort. The
single most likely untried lever is a SPECTRAL net (1-D FNO): Phase F showed spectral architectures crack exactly
the high-frequency/long-range structure a local CNN cannot. This is the rigorous test of the learned half.

Same emulator setup as v1 (predict the (Phi,Pi) flow map; re-solve the geometry for the 2m/r diagnostic), but:
  - PROPER architecture comparison: local CNN  vs  1-D FNO (spectral).
  - PROPER data: dense amplitudes SPANNING the disperse->collapse transition (critical ~0.05), incl. near-critical.
  - PROPER training: push-forward, longer, 3 seeds each.
  - PROPER gate: disperse/collapse classification on HELD-OUT amplitudes (the knife-edge), per architecture/seed.

Pre-reg (2026-06-20):
  V1 (does spectral crack it?): FNO mean held-out classification accuracy across 3 seeds clearly beats the CNN's
     and reaches >= 0.9 (i.e., it actually learns the disperse/collapse threshold the local CNN couldn't).
  V2 (honest control): report the CNN under the SAME proper data/training (so the comparison isolates architecture).
"""

import argparse
import json
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")                          # silence the harmless MPS rfft resize warning
sys.path.insert(0, str(Path(__file__).resolve().parent))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import torch
from torch import nn

from collapse import ScalarCollapse
from modules import FNO1d


class CNN1d(nn.Module):
    def __init__(self, ch=64, depth=4):
        super().__init__()
        layers = [nn.Conv1d(2, ch, 5, padding=2, padding_mode="replicate"), nn.GELU()]
        for _ in range(depth - 1):
            layers += [nn.Conv1d(ch, ch, 5, padding=2, padding_mode="replicate"), nn.GELU()]
        layers += [nn.Conv1d(ch, 2, 5, padding=2, padding_mode="replicate")]
        self.net = nn.Sequential(*layers)

    def forward(self, s):
        return s + self.net(s)


def gen(sim, amps, t_end, stride):
    snaps, peaks = [], []
    for A in amps:
        s, m, _ = sim.trajectory(A, t_end=t_end, stride=stride, bh_thresh=2.0)
        snaps.append(s); peaks.append(m.max())
    T = min(len(s) for s in snaps)
    return np.stack([s[:T] for s in snaps]), np.array(peaks)


def train_pf(make_net, data, steps, K, dev, seed):
    A, T = data.shape[0], data.shape[1]; d = torch.tensor(data).to(dev)
    torch.manual_seed(seed); net = make_net().to(dev); opt = torch.optim.Adam(net.parameters(), lr=1e-3)
    rng = np.random.default_rng(seed)
    for st in range(steps):
        j = int(rng.integers(0, K)); ai = rng.integers(0, A, 32); t0 = rng.integers(0, T - j - 1, 32)
        s = d[ai, t0]
        if j > 0:
            with torch.no_grad():
                for _ in range(j):
                    s = net(s)
        loss = nn.functional.mse_loss(net(s), d[ai, t0 + j + 1])
        opt.zero_grad(); loss.backward(); torch.nn.utils.clip_grad_norm_(net.parameters(), 1.0); opt.step()
    return net.eval()


@torch.no_grad()
def pred_peak(net, sim, s0, T, dev):
    s = torch.tensor(s0[None]).to(dev); peak = 0.0
    for _ in range(T):
        s = net(s)
        if not torch.isfinite(s).all():
            return float("nan")
        peak = max(peak, sim.max_2m_over_r(s[0, 0].cpu().numpy(), s[0, 1].cpu().numpy()))
    return peak


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", default="mps" if torch.backends.mps.is_available() else ("cuda" if torch.cuda.is_available() else "cpu"))
    ap.add_argument("--n", type=int, default=300); ap.add_argument("--t-end", type=float, default=10.0)
    ap.add_argument("--stride", type=int, default=8); ap.add_argument("--steps", type=int, default=6000)
    ap.add_argument("--K", type=int, default=4); ap.add_argument("--seeds", type=int, default=3)
    ap.add_argument("--modes", type=int, default=48); ap.add_argument("--width", type=int, default=64)
    a = ap.parse_args(); dev = a.device
    sim = ScalarCollapse(n=a.n, R=20.0, cfl=0.2); res = Path(__file__).resolve().parent / "results"; res.mkdir(exist_ok=True)
    print(f"device={dev} n={a.n} steps={a.steps} seeds={a.seeds} fno(modes={a.modes},width={a.width})")

    # dense amplitudes spanning the transition (critical ~0.05), with extra resolution near the knife-edge
    train_amps = np.array([0.02, 0.03, 0.04, 0.045, 0.05, 0.055, 0.06, 0.07, 0.09, 0.12, 0.16, 0.22, 0.30])
    test_amps = np.array([0.025, 0.035, 0.047, 0.052, 0.058, 0.08, 0.10, 0.14, 0.20])
    print("generating ground-truth trajectories (one-time) ...")
    tr, _ = gen(sim, train_amps, a.t_end, a.stride)
    te, truth_peak = gen(sim, test_amps, a.t_end, a.stride)
    T = min(tr.shape[1], te.shape[1]); tr = tr[:, :T]; te = te[:, :T]
    truth_cls = truth_peak > 0.5
    print(f"  train {tr.shape}  test peaks {np.round(truth_peak,2)}  -> truth class {''.join('C' if c else 'd' for c in truth_cls)}")

    archs = {"CNN": lambda: CNN1d(ch=a.width), "FNO": lambda: FNO1d(2, 2, width=a.width, modes=a.modes)}
    out = {"test_amps": test_amps.tolist(), "truth_peak": truth_peak.tolist(), "truth_class": truth_cls.tolist()}
    for name, mk in archs.items():
        accs, all_pred = [], []
        for seed in range(a.seeds):
            net = train_pf(mk, tr, a.steps, a.K, dev, seed)
            pk = np.array([pred_peak(net, sim, te[i, 0], T - 1, dev) for i in range(len(test_amps))])
            fin = np.isfinite(pk); acc = float(np.mean((pk[fin] > 0.5) == truth_cls[fin])) if fin.sum() else 0.0
            accs.append(acc); all_pred.append(pk.tolist())
            print(f"  {name} seed {seed}: pred peaks {np.round(pk,2)} | class_acc {acc:.2f} | finite {fin.sum()}/{len(test_amps)}")
        out[name] = {"class_accs": accs, "mean_acc": float(np.mean(accs)), "preds": all_pred}
        print(f"{name}: mean held-out classification accuracy {np.mean(accs):.2f} (seeds {np.round(accs,2)})")

    v1 = bool(out["FNO"]["mean_acc"] >= 0.9 and out["FNO"]["mean_acc"] > out["CNN"]["mean_acc"] + 0.05)
    out["V1_spectral_cracks_criticality"] = v1
    print(f"\nV1 FNO learns the disperse/collapse threshold (mean acc>=0.9 and clearly beats CNN): {v1}")
    print(f"   FNO {out['FNO']['mean_acc']:.2f}  vs  CNN {out['CNN']['mean_acc']:.2f}  (v1 modest-CNN was ~0.67)")
    (res / "exp10_collapse_fno.json").write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.axhline(0.5, color="gray", ls=":", lw=0.8, label="disperse/collapse threshold")
    ax.plot(test_amps, truth_peak, "ko-", label="ground truth")
    ax.plot(test_amps, np.nanmean(out["FNO"]["preds"], axis=0), "crimson", marker="s", label=f"FNO (acc {out['FNO']['mean_acc']:.2f})")
    ax.plot(test_amps, np.nanmean(out["CNN"]["preds"], axis=0), "navy", marker="^", ls="--", label=f"CNN (acc {out['CNN']['mean_acc']:.2f})")
    ax.set_xlabel("pulse amplitude A (held-out)"); ax.set_ylabel("peak 2m/r (mean over seeds)")
    ax.legend(fontsize=8); ax.set_title("v3 rigorous: does a spectral net (FNO) learn the collapse knife-edge\nwhere the local CNN could not?")
    fig.tight_layout(); fig.savefig(res / "exp10_collapse_fno.png", dpi=140)
    print("saved hailmary/results/exp10_collapse_fno.json + .png")


if __name__ == "__main__":
    main()
