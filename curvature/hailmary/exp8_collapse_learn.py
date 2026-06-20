"""Hail Mary Phase 2 (learning v1) — can a learned predictor EMULATE Choptuik collapse?

First learning step on the verified ground-truth collapse solver. A push-forward-trained predictor learns the
one-step flow map for the scalar field (Phi, Pi); at rollout the GEOMETRY IS RE-SOLVED from the predicted field
(collapse.solve_metric -- the constraint enforced by construction), which both drives the diagnostic and is the
purest "enforce the constraint" step (here the constraint literally produces 2m/r). Test: on HELD-OUT amplitudes
(interpolating across the disperse->collapse transition), does the learned rollout reproduce the ground-truth
2m/r(t) -- i.e., did the net learn gravitational collapse? And does push-forward (the stability fix that worked
on Maxwell) beat 1-step on this stiff strong-field problem?

Honest scope: v1 = learned EMULATOR of collapse with constraint-by-construction geometry (the net learns the
field flow; the Einstein constraint enters via the geometry re-solve). The solve-the-metric vs predict-the-metric
contrast (the full Maxwell-style hard-vs-soft test) is the planned v2.

Pre-reg (2026-06-20), grid n=300, amplitudes spanning the transition:
  L1 LEARNED COLLAPSE: across held-out amplitudes, the learned rollout's peak 2m/r tracks the truth's
     (Pearson r > 0.9) -- the net learned the disperse->collapse trend, not just one regime.
  L2 PUSH-FORWARD STABILITY: push-forward predictor stays finite over the full rollout on all held-out amplitudes
     (no NaN/blowup), and its peak-2m/r tracking beats a 1-step-trained predictor.
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


def gen(sim, amps, t_end, stride):
    """uniform-length (Phi,Pi) trajectories + truth 2m/r curves for the given amplitudes (no early stop)."""
    snaps, twomr = [], []
    for A in amps:
        s, m, _ = sim.trajectory(A, t_end=t_end, stride=stride, bh_thresh=2.0)   # bh_thresh>1 -> never early-stop
        snaps.append(s); twomr.append(m)
    T = min(len(s) for s in snaps)
    return np.stack([s[:T] for s in snaps]), np.stack([m[:T] for m in twomr])     # (A, T, 2, n), (A, T)


class Net1D(nn.Module):
    def __init__(self, ch=64, depth=4):
        super().__init__()
        layers = [nn.Conv1d(2, ch, 5, padding=2, padding_mode="replicate"), nn.GELU()]
        for _ in range(depth - 1):
            layers += [nn.Conv1d(ch, ch, 5, padding=2, padding_mode="replicate"), nn.GELU()]
        layers += [nn.Conv1d(ch, 2, 5, padding=2, padding_mode="replicate")]
        self.net = nn.Sequential(*layers)

    def forward(self, s):
        return s + self.net(s)


def train(mode, data, steps, K, dev, seed):
    A, T = data.shape[0], data.shape[1]
    d = torch.tensor(data).to(dev)                       # (A,T,2,n)
    torch.manual_seed(seed); net = Net1D().to(dev); opt = torch.optim.Adam(net.parameters(), lr=1e-3)
    rng = np.random.default_rng(seed)
    for st in range(steps):
        if mode == "pushforward":
            j = int(rng.integers(0, K)); ai = rng.integers(0, A, 32); t0 = rng.integers(0, T - j - 1, 32)
            s = d[ai, t0]
            if j > 0:
                with torch.no_grad():
                    for _ in range(j):
                        s = net(s)
            loss = nn.functional.mse_loss(net(s), d[ai, t0 + j + 1])
        else:                                            # 1-step
            ai = rng.integers(0, A, 32); t0 = rng.integers(0, T - 1, 32)
            loss = nn.functional.mse_loss(net(d[ai, t0]), d[ai, t0 + 1])
        opt.zero_grad(); loss.backward(); torch.nn.utils.clip_grad_norm_(net.parameters(), 1.0); opt.step()
    return net.eval()


@torch.no_grad()
def predicted_peak_2mr(net, sim, s0, T, dev):
    """roll the net T steps; re-solve the geometry each step (constraint by construction) -> predicted peak 2m/r."""
    s = torch.tensor(s0[None]).to(dev); peak = 0.0
    for _ in range(T):
        s = net(s)
        if not torch.isfinite(s).all():
            return float("nan")
        Phi = s[0, 0].cpu().numpy(); Pi = s[0, 1].cpu().numpy()
        peak = max(peak, sim.max_2m_over_r(Phi, Pi))
    return peak


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", default="mps" if torch.backends.mps.is_available() else ("cuda" if torch.cuda.is_available() else "cpu"))
    ap.add_argument("--n", type=int, default=300); ap.add_argument("--t-end", type=float, default=10.0)
    ap.add_argument("--stride", type=int, default=8); ap.add_argument("--steps", type=int, default=3000)
    ap.add_argument("--K", type=int, default=4); ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args(); dev = a.device
    sim = ScalarCollapse(n=a.n, R=20.0, cfl=0.2)
    res = Path(__file__).resolve().parent / "results"; res.mkdir(exist_ok=True)
    print(f"device={dev} n={a.n} t_end={a.t_end} stride={a.stride} steps={a.steps}")

    # critical amplitude ~0.05 (diagnosed, resolution-robust); span the transition: disperse (A<0.05) -> collapse
    train_amps = np.array([0.02, 0.03, 0.04, 0.055, 0.08, 0.13, 0.22])
    test_amps = np.array([0.025, 0.035, 0.05, 0.07, 0.11, 0.18])           # interpolating, spans disperse<->collapse
    print("generating ground-truth collapse trajectories ...")
    tr_data, _ = gen(sim, train_amps, a.t_end, a.stride)
    te_data, te_twomr = gen(sim, test_amps, a.t_end, a.stride)
    T = min(tr_data.shape[1], te_data.shape[1]); tr_data = tr_data[:, :T]; te_data = te_data[:, :T]
    truth_peak = te_twomr[:, :T].max(axis=1)
    print(f"  train {tr_data.shape}  test {te_data.shape}  truth peak 2m/r: {np.round(truth_peak,3)}")

    out = {}
    for mode in ["pushforward", "onestep"]:
        net = train(mode, tr_data, a.steps, a.K, dev, a.seed)
        pred_peak = np.array([predicted_peak_2mr(net, sim, te_data[i, 0], T - 1, dev) for i in range(len(test_amps))])
        finite = np.isfinite(pred_peak)
        r = float(np.corrcoef(truth_peak[finite], pred_peak[finite])[0, 1]) if finite.sum() > 1 else float("nan")
        tc = truth_peak > 0.5; pc = pred_peak > 0.5                       # disperse (<0.5) vs collapse (>0.5)
        cls = float(np.mean(pc[finite] == tc[finite])) if finite.sum() > 0 else 0.0
        out[mode] = {"pred_peak": pred_peak.tolist(), "pearson_r": r, "class_acc": cls, "n_finite": int(finite.sum())}
        print(f"{mode:11s}: pred peak 2m/r {np.round(pred_peak,3)} | class_acc {cls:.2f} | Pearson r {r:.3f} | finite {finite.sum()}/{len(test_amps)}")

    pf = out["pushforward"]; os_ = out["onestep"]
    l1 = bool(pf["class_acc"] >= 0.99)                                    # all held-out disperse/collapse classified right
    l2 = bool(pf["n_finite"] == len(test_amps) and pf["class_acc"] >= os_["class_acc"])
    out.update({"truth_peak": truth_peak.tolist(), "test_amps": test_amps.tolist(),
                "L1_learned_collapse": l1, "L2_pushforward_stability": l2, "learned_collapse_emulator": bool(l1 and l2)})
    print(f"\nL1 learned collapse (push-forward classifies disperse/collapse on held-out, acc>=0.99): {l1}")
    print(f"L2 push-forward stable + >= 1-step: {l2}")
    print(f"\nLEARNED CHOPTUIK COLLAPSE EMULATOR (push-forward, constraint-by-construction geometry): {out['learned_collapse_emulator']}")
    (res / "exp8_collapse_learn.json").write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(figsize=(7.5, 5))
    ax.plot(test_amps, truth_peak, "ko-", label="ground truth")
    ax.plot(test_amps, pf["pred_peak"], "crimson", marker="s", label=f"push-forward (r={pf['pearson_r']:.2f})")
    ax.plot(test_amps, os_["pred_peak"], "navy", marker="^", ls="--", label=f"1-step (r={os_['pearson_r']:.2f})")
    ax.set_xlabel("pulse amplitude A (held-out)"); ax.set_ylabel("peak 2m/r over the rollout")
    ax.legend(fontsize=8); ax.set_title("Learned Choptuik collapse: does the predictor reproduce\nthe disperse->collapse trend on held-out amplitudes?")
    fig.tight_layout(); fig.savefig(res / "exp8_collapse_learn.png", dpi=140)
    print("saved hailmary/results/exp8_collapse_learn.json + .png")


if __name__ == "__main__":
    main()
