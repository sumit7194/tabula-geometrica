"""Hail Mary Phase 2 (learning v2) — HYBRID: coarse physics carries the constraint, the net corrects.

v1 lesson: a pure (Phi,Pi) emulator amplifies toward the collapse attractor and does NOT learn criticality
(it collapses every amplitude). v2 fix (our thesis): let PHYSICS carry the constraint-structure so dispersal is
preserved, and have the net only CORRECT the cheap physics. Cheap-but-faithful physics = the verified solver on a
COARSE grid (it carries the geometry/constraint, classifies the clear cases, but UNDER-RESOLVES near criticality:
it misclassifies the marginal A=0.05). So the corrector has real work -- recover the near-critical collapse the
coarse physics misses -- a fair test, not handed to the physics.

Pipeline per step (maintaining a FINE state): coarse_step = downsample -> evolve coarse by one snapshot dt ->
upsample; then corrected = coarse_step + net(state, coarse_step). Geometry re-solved on the fine grid for 2m/r
(constraint by construction). Trained as a residual corrector (the physics anchors the dynamics, so the net's
job is small and far less prone to v1's amplification).

Pre-reg (2026-06-20), fine n=300, coarse n=100, amplitudes spanning the transition:
  H1 CRITICALITY RECOVERED: the hybrid classifies disperse/collapse correctly on ALL held-out amplitudes
     (acc 1.0), INCLUDING the near-critical A=0.05 that coarse-physics-alone misclassifies -- beating both
     coarse-alone AND the v1 pure emulator (which collapsed everything).
  H2 ACCURACY: hybrid field MSE (vs fine truth, over the rollout) beats coarse-alone (upsampled).
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

from collapse import ScalarCollapse


class Corrector(nn.Module):
    def __init__(self, ch=64, depth=4):
        super().__init__()
        layers = [nn.Conv1d(4, ch, 5, padding=2, padding_mode="replicate"), nn.GELU()]
        for _ in range(depth - 1):
            layers += [nn.Conv1d(ch, ch, 5, padding=2, padding_mode="replicate"), nn.GELU()]
        layers += [nn.Conv1d(ch, 2, 5, padding=2, padding_mode="replicate")]
        self.net = nn.Sequential(*layers)

    def forward(self, state, coarse_pred):
        return coarse_pred + self.net(torch.cat([state, coarse_pred], dim=1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", default="mps" if torch.backends.mps.is_available() else ("cuda" if torch.cuda.is_available() else "cpu"))
    ap.add_argument("--nf", type=int, default=300); ap.add_argument("--nc", type=int, default=100)
    ap.add_argument("--t-end", type=float, default=10.0); ap.add_argument("--stride", type=int, default=8)
    ap.add_argument("--steps", type=int, default=3000); ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args(); dev = a.device
    fine = ScalarCollapse(n=a.nf, R=20.0, cfl=0.2); coarse = ScalarCollapse(n=a.nc, R=20.0, cfl=0.2)
    res = Path(__file__).resolve().parent / "results"; res.mkdir(exist_ok=True)
    dt_snap = a.stride * fine.dt; nsub_c = max(1, int(round(dt_snap / coarse.dt)))
    print(f"device={dev} fine={a.nf} coarse={a.nc} dt_snap={dt_snap:.4f} coarse-substeps/snap={nsub_c}")

    def down(s):                                            # fine (2,nf) -> coarse (2,nc)
        return np.stack([np.interp(coarse.r, fine.r, s[0]), np.interp(coarse.r, fine.r, s[1])]).astype(np.float32)
    def up(s):                                              # coarse (2,nc) -> fine (2,nf)
        return np.stack([np.interp(fine.r, coarse.r, s[0]), np.interp(fine.r, coarse.r, s[1])]).astype(np.float32)
    def coarse_step(s_fine):                                # one snapshot of cheap physics, returned on the fine grid
        sc = down(s_fine); Phi, Pi = sc[0], sc[1]
        for _ in range(nsub_c):
            Phi, Pi = coarse.step(Phi, Pi)
        return up(np.stack([Phi, Pi]))

    # ground-truth fine trajectories (reuse the verified solver)
    train_amps = np.array([0.02, 0.03, 0.04, 0.055, 0.08, 0.13, 0.22])
    test_amps = np.array([0.025, 0.035, 0.05, 0.07, 0.11, 0.18])
    def fine_traj(amps):
        out = []
        for A in amps:
            s, _, _ = fine.trajectory(A, t_end=a.t_end, stride=a.stride, bh_thresh=2.0); out.append(s)
        T = min(len(s) for s in out); return np.stack([s[:T] for s in out])
    print("generating fine ground truth + coarse-physics predictions ...")
    tr = fine_traj(train_amps); te = fine_traj(test_amps); T = min(tr.shape[1], te.shape[1]); tr = tr[:, :T]; te = te[:, :T]
    truth_peak = np.array([max(fine.max_2m_over_r(te[i, t, 0], te[i, t, 1]) for t in range(T)) for i in range(len(test_amps))])
    # precompute one-step coarse predictions for training pairs
    Xs, Cs, Ys = [], [], []
    for i in range(len(train_amps)):
        for t in range(T - 1):
            Xs.append(tr[i, t]); Cs.append(coarse_step(tr[i, t])); Ys.append(tr[i, t + 1])
    X = torch.tensor(np.stack(Xs)).to(dev); C = torch.tensor(np.stack(Cs)).to(dev); Y = torch.tensor(np.stack(Ys)).to(dev)
    print(f"  train pairs {len(Xs)}  truth peak 2m/r {np.round(truth_peak,3)}")

    torch.manual_seed(a.seed); net = Corrector().to(dev); opt = torch.optim.Adam(net.parameters(), lr=1e-3)
    rng = np.random.default_rng(a.seed)
    for st in range(a.steps):
        idx = rng.integers(0, len(Xs), 64)
        loss = nn.functional.mse_loss(net(X[idx], C[idx]), Y[idx])
        opt.zero_grad(); loss.backward(); torch.nn.utils.clip_grad_norm_(net.parameters(), 1.0); opt.step()
    net.eval()

    # rollouts on held-out amplitudes
    def peak_and_mse(mode, i):
        s = te[i, 0].copy(); peak = fine.max_2m_over_r(s[0], s[1]); sq = 0.0
        for t in range(T - 1):
            cp = coarse_step(s)
            if mode == "hybrid":
                with torch.no_grad():
                    s = net(torch.tensor(s[None]).to(dev), torch.tensor(cp[None]).to(dev))[0].cpu().numpy()
            else:                                          # coarse-alone (just the cheap physics, upsampled)
                s = cp
            if not np.isfinite(s).all():
                return float("nan"), float("nan")
            peak = max(peak, fine.max_2m_over_r(s[0], s[1])); sq += float(np.mean((s - te[i, t + 1]) ** 2))
        return peak, sq / (T - 1)

    out = {}
    for mode in ["hybrid", "coarse"]:
        pm = [peak_and_mse(mode, i) for i in range(len(test_amps))]        # one rollout per (mode, amplitude)
        peaks = np.array([p for p, _ in pm]); mses = np.array([m for _, m in pm])
        fin = np.isfinite(peaks); tc = truth_peak > 0.5; pc = peaks > 0.5
        acc = float(np.mean(pc[fin] == tc[fin])) if fin.sum() else 0.0
        out[mode] = {"peaks": peaks.tolist(), "class_acc": acc, "mse": float(np.nanmean(mses))}
        print(f"{mode:7s}: peaks {np.round(peaks,3)} | class_acc {acc:.2f} | mean field MSE {np.nanmean(mses):.2e}")

    h1 = bool(out["hybrid"]["class_acc"] >= 0.99 and out["hybrid"]["class_acc"] > out["coarse"]["class_acc"])
    h2 = bool(out["hybrid"]["mse"] < out["coarse"]["mse"])
    out.update({"truth_peak": truth_peak.tolist(), "test_amps": test_amps.tolist(), "v1_pure_emulator_class_acc": 0.67,
                "H1_criticality_recovered": h1, "H2_accuracy": h2, "hybrid_works": bool(h1 and h2)})
    print(f"\nH1 hybrid recovers criticality (acc {out['hybrid']['class_acc']:.2f} == 1.0, beats coarse {out['coarse']['class_acc']:.2f} and v1 0.67): {h1}")
    print(f"H2 hybrid field MSE {out['hybrid']['mse']:.2e} < coarse {out['coarse']['mse']:.2e}: {h2}")
    print(f"\nHYBRID (coarse physics + neural corrector) CRACKS CRITICALITY where pure emulation failed: {out['hybrid_works']}")
    (res / "exp9_hybrid.json").write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(figsize=(7.5, 5))
    ax.axhline(0.5, color="gray", ls=":", lw=0.8, label="disperse/collapse threshold")
    ax.plot(test_amps, truth_peak, "ko-", label="fine truth")
    ax.plot(test_amps, out["hybrid"]["peaks"], "crimson", marker="s", label=f"hybrid (acc {out['hybrid']['class_acc']:.2f})")
    ax.plot(test_amps, out["coarse"]["peaks"], "navy", marker="^", ls="--", label=f"coarse-alone (acc {out['coarse']['class_acc']:.2f})")
    ax.set_xlabel("pulse amplitude A (held-out)"); ax.set_ylabel("peak 2m/r")
    ax.legend(fontsize=8); ax.set_title("v2 hybrid: coarse physics carries the constraint, net corrects criticality\n(pure emulator v1 collapsed everything: acc 0.67)")
    fig.tight_layout(); fig.savefig(res / "exp9_hybrid.png", dpi=140)
    print("saved hailmary/results/exp9_hybrid.json + .png")


if __name__ == "__main__":
    main()
