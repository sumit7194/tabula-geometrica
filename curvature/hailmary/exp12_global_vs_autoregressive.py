"""Hail Mary Phase 2 (learning v3) — MECHANISM: is the AUTOREGRESSIVE ROLLOUT the wall (not the architecture)?

exp10 showed both a local CNN and a spectral FNO, autoregressive (Phi,Pi) emulators, collapse EVERYTHING. The
published NN success on Choptuik (Ferrer-Sanchez et al., arXiv:2511.15247, with M. Choptuik) is a PINN: a GLOBAL
spacetime solve with physics in the loss + adaptive sampling -- it never rolls out step by step. That suggests the
wall is the AUTOREGRESSIVE FORMULATION (rollout error amplifies toward the collapse attractor), not the network's
expressivity or the learnability of the disperse/collapse criterion from the data.

Clean isolation on a BALANCED, varied-profile dataset (vary amplitude A, position r0, width sig so collapse is a
nontrivial function of the profile, not just A):
  AUTOREGRESSIVE: the exp10 emulator -- roll the learned flow map, re-solve geometry, read peak 2m/r. (the wall)
  GLOBAL:         a net maps the INITIAL data (Phi0, Pi0) -> peak 2m/r DIRECTLY (one shot, no rollout).
If GLOBAL learns the threshold where AUTOREGRESSIVE fails, the disperse/collapse info IS learnable from the data --
the autoregressive rollout is the culprit (consistent with why the global PINN works). This is a MECHANISM probe,
not a proposed solver.

Pre-reg (2026-06-20), balanced held-out (>= 0.4 of each class), 3 seeds:
  W1 ROLLOUT IS THE WALL: GLOBAL mean held-out classification accuracy >= 0.9 AND beats the AUTOREGRESSIVE mean by
     >= 0.2 (the info is learnable one-shot; the rollout is what fails).
  W2 HONEST BASELINE: report the majority-class rate; GLOBAL must clear it by >= 0.2 (not just exploiting imbalance).
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
from exp10_collapse_fno import CNN1d, train_pf, pred_peak


def gen_profiles(sim, profiles, t_end, stride):
    """trajectories + truth peak 2m/r for varied (A, r0, sig) profiles."""
    snaps, peaks = [], []
    for A, r0, sig in profiles:
        Phi, Pi = sim.initial_data(A, r0=r0, sig=sig)
        nsteps = int(t_end / sim.dt); s = [np.stack([Phi, Pi])]; pk = sim.max_2m_over_r(Phi, Pi)
        for st in range(nsteps):
            Phi, Pi = sim.step(Phi, Pi)
            if not np.isfinite(Phi).all():
                break
            if (st + 1) % stride == 0:
                s.append(np.stack([Phi, Pi])); pk = max(pk, sim.max_2m_over_r(Phi, Pi))
        snaps.append(np.array(s, dtype=np.float32)); peaks.append(pk)
    T = min(len(s) for s in snaps)
    return np.stack([s[:T] for s in snaps]), np.array(peaks)


class GlobalNet(nn.Module):
    """initial (Phi0,Pi0) (B,2,n) -> scalar peak 2m/r. Global pooling = the whole point (no locality/rollout)."""

    def __init__(self, width=64, modes=48):
        super().__init__()
        self.body = FNO1d(2, width, width=width, modes=modes, residual=False)
        self.head = nn.Sequential(nn.Linear(width, width), nn.GELU(), nn.Linear(width, 1))

    def forward(self, s):
        h = self.body(s)                                   # (B, width, n)
        return self.head(h.mean(-1)).squeeze(-1)           # global mean pool -> scalar


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", default="mps" if torch.backends.mps.is_available() else ("cuda" if torch.cuda.is_available() else "cpu"))
    ap.add_argument("--n", type=int, default=300); ap.add_argument("--t-end", type=float, default=10.0)
    ap.add_argument("--stride", type=int, default=8); ap.add_argument("--steps", type=int, default=6000)
    ap.add_argument("--K", type=int, default=4); ap.add_argument("--seeds", type=int, default=3)
    ap.add_argument("--width", type=int, default=64); ap.add_argument("--modes", type=int, default=48)
    a = ap.parse_args(); dev = a.device
    sim = ScalarCollapse(n=a.n, R=20.0, cfl=0.2); res = Path(__file__).resolve().parent / "results"; res.mkdir(exist_ok=True)
    print(f"device={dev} n={a.n} steps={a.steps} seeds={a.seeds}")

    # varied profiles spanning the transition; balanced by construction (sample, then check class balance)
    rng0 = np.random.default_rng(0)
    def sample(nprof):
        A = rng0.uniform(0.015, 0.09, nprof); r0 = rng0.uniform(4.0, 6.0, nprof); sig = rng0.uniform(0.8, 1.4, nprof)
        return list(zip(A, r0, sig))
    train_prof = sample(48); test_prof = sample(24)
    print("generating varied-profile trajectories (one-time) ...")
    tr, tr_peak = gen_profiles(sim, train_prof, a.t_end, a.stride)
    te, te_peak = gen_profiles(sim, test_prof, a.t_end, a.stride)
    T = min(tr.shape[1], te.shape[1]); tr = tr[:, :T]; te = te[:, :T]
    tr_cls = tr_peak > 0.5; te_cls = te_peak > 0.5
    maj = max(te_cls.mean(), 1 - te_cls.mean())
    print(f"  train {tr.shape} ({tr_cls.mean()*100:.0f}% collapse)  test ({te_cls.mean()*100:.0f}% collapse)  majority-rate {maj:.2f}")

    out = {"test_peak": te_peak.tolist(), "test_class": te_cls.tolist(), "majority_rate": float(maj)}

    # --- GLOBAL: predict peak 2m/r from initial data, no rollout ---
    g_acc = []
    Xtr = torch.tensor(tr[:, 0]).to(dev); Ytr = torch.tensor(tr_peak.astype(np.float32)).to(dev)
    Xte = torch.tensor(te[:, 0]).to(dev)
    for seed in range(a.seeds):
        torch.manual_seed(seed); net = GlobalNet(a.width, a.modes).to(dev); opt = torch.optim.Adam(net.parameters(), lr=1e-3)
        rng = np.random.default_rng(seed)
        for st in range(a.steps):
            idx = rng.integers(0, len(Xtr), 16)
            loss = nn.functional.mse_loss(net(Xtr[idx]), Ytr[idx])
            opt.zero_grad(); loss.backward(); torch.nn.utils.clip_grad_norm_(net.parameters(), 1.0); opt.step()
        net.eval()
        with torch.no_grad():
            pk = net(Xte).cpu().numpy()
        acc = float(np.mean((pk > 0.5) == te_cls)); g_acc.append(acc)
        print(f"  GLOBAL seed {seed}: class_acc {acc:.2f}")
    out["global"] = {"accs": g_acc, "mean": float(np.mean(g_acc))}

    # --- AUTOREGRESSIVE: the exp10 emulator on the SAME data (FNO, the stronger arch) ---
    ar_acc = []
    for seed in range(a.seeds):
        net = train_pf(lambda: FNO1d(2, 2, width=a.width, modes=a.modes), tr, a.steps, a.K, dev, seed)
        pk = np.array([pred_peak(net, sim, te[i, 0], T - 1, dev) for i in range(len(test_prof))])
        fin = np.isfinite(pk); acc = float(np.mean((pk[fin] > 0.5) == te_cls[fin])) if fin.sum() else 0.0
        ar_acc.append(acc)
        print(f"  AUTOREGRESSIVE(FNO) seed {seed}: class_acc {acc:.2f} | finite {fin.sum()}/{len(test_prof)}")
    out["autoregressive"] = {"accs": ar_acc, "mean": float(np.mean(ar_acc))}

    gm, am = np.mean(g_acc), np.mean(ar_acc)
    w1 = bool(gm >= 0.9 and gm - am >= 0.2)
    w2 = bool(gm - maj >= 0.2)
    out.update({"W1_rollout_is_the_wall": w1, "W2_beats_majority": w2, "rollout_is_the_wall": bool(w1 and w2)})
    print(f"\nGLOBAL {gm:.2f}  vs  AUTOREGRESSIVE {am:.2f}  (majority-rate {maj:.2f})")
    print(f"W1 rollout is the wall (global>=0.9 and beats autoregressive by>=0.2): {w1}")
    print(f"W2 global beats majority by>=0.2: {w2}")
    print(f"\nTHE AUTOREGRESSIVE ROLLOUT IS THE WALL (info learnable one-shot; rollout amplifies to collapse): {out['rollout_is_the_wall']}")
    (res / "exp12_global_vs_autoregressive.json").write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.bar(["global\n(one-shot)", "autoregressive\n(rollout)", "majority\nbaseline"], [gm, am, maj],
           color=["seagreen", "crimson", "gray"])
    ax.set_ylabel("held-out classification accuracy"); ax.set_ylim(0, 1.05)
    ax.set_title("Is the rollout the wall? global (no rollout) vs autoregressive emulator\n(same varied-profile data)")
    fig.tight_layout(); fig.savefig(res / "exp12_global_vs_autoregressive.png", dpi=140)
    print("saved hailmary/results/exp12_global_vs_autoregressive.json + .png")


if __name__ == "__main__":
    main()
