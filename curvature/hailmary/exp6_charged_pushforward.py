"""Hail Mary — Experiment 6: the untested cell -- CHARGED constraint + PUSH-FORWARD training.

The stress-test matrix:
                 vacuum                         charged (rho != 0)
  1-step       constraint OK, accuracy 2/3      constraint OK, accuracy DIVERGES 2/3 (Exp 5)
  push-forward constraint OK, STABLE (Exp 3)    <- THIS experiment
Exp 5 showed the affine projection holds the charged constraint robustly, but Plan A with 1-step training
diverges on charged (the stability wall, worse than vacuum). Exp 3 showed push-forward training fixes the
stability wall in vacuum. Does it also rescue accuracy on the harder charged case -- giving constraint-held AND
stable end-to-end on the non-trivial constraint?

Plan A here = PredictorCNN, push-forward trained (j no-grad rollout steps + 1 graded step + grad-clip), affine-
projected (div E = rho) every step. Compared to Exp 5's charged 1-step Plan A (diverged 2/3 at ~0.35).

Pre-reg (2026-06-20), grid 32, charged, 3 seeds, horizon 100:
  D1 CONSTRAINT: plan keeps max|div E - rho| <= 1e-4 every seed (by construction).
  D2 STABILITY RESCUED: push-forward charged Plan A field MSE is bounded on ALL 3 seeds (max < 5e-3, no
     divergence) -- fixing the 1-step charged divergence (Exp 5: 2/3 seeds blew up to ~0.35).
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

from exp5_charged_constraint import affine_project_t, make_charged
from modules import PredictorCNN, div_E, wavenumbers


def proj(s, rho, KX, KY, K2safe):
    ex, ey = affine_project_t(s[:, 0], s[:, 1], rho, KX, KY, K2safe)
    return torch.stack([ex, ey, s[:, 2]], 1)


def train_pf_charged(tr, rho, K, steps, KX, KY, K2safe, dev, seed):
    T, S = tr.shape[0], tr.shape[1] - 1
    torch.manual_seed(seed); net = PredictorCNN().to(dev); opt = torch.optim.Adam(net.parameters(), lr=2e-3)
    rng = np.random.default_rng(seed); trd = torch.tensor(tr).to(dev); rhod = torch.tensor(rho).to(dev)
    for st in range(steps):
        j = int(rng.integers(0, K)); ti = rng.integers(0, T, 32); t0 = rng.integers(0, S - j, 32)
        s = trd[ti, t0]; rb = rhod[ti]
        if j > 0:
            with torch.no_grad():
                for _ in range(j):
                    s = proj(net(s), rb, KX, KY, K2safe)
        loss = nn.functional.mse_loss(proj(net(s), rb, KX, KY, K2safe), trd[ti, t0 + j + 1])
        opt.zero_grad(); loss.backward(); torch.nn.utils.clip_grad_norm_(net.parameters(), 1.0); opt.step()
    return net.eval()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", default="mps" if torch.backends.mps.is_available() else ("cuda" if torch.cuda.is_available() else "cpu"))
    ap.add_argument("--grid", type=int, default=32); ap.add_argument("--traj", type=int, default=96)
    ap.add_argument("--K", type=int, default=4); ap.add_argument("--steps", type=int, default=2500)
    ap.add_argument("--horizon", type=int, default=100); ap.add_argument("--nseeds", type=int, default=3)
    a = ap.parse_args(); dev = a.device
    KX, KY, K2safe = wavenumbers(a.grid, 2 * np.pi, dev)
    res = Path(__file__).resolve().parent / "results"; res.mkdir(exist_ok=True)
    print(f"device={dev} grid={a.grid} K={a.K} steps={a.steps} horizon={a.horizon}")

    cdrift, mses = [], []
    onestep = [3.45e-1, 3.57e-1, 4.03e-4]                                 # Exp 5 charged 1-step Plan A, for reference
    for seed in range(a.nseeds):
        tr, rho, sim = make_charged(a.traj, 40, a.grid, seed)
        net = train_pf_charged(tr, rho, a.K, a.steps, KX, KY, K2safe, dev, seed)
        te, rte, _ = make_charged(16, a.horizon, a.grid, 5000 + seed)
        truth = torch.tensor(te).to(dev); s0 = torch.tensor(te[:, 0]).to(dev); rt = torch.tensor(rte).to(dev)
        with torch.no_grad():
            s = s0.clone()
            for _ in range(a.horizon):
                s = proj(net(s), rt, KX, KY, K2safe)
            cd = (div_E(s[:, 0], s[:, 1], KX, KY) - rt).abs().amax(dim=(-1, -2)).mean().item()
            mse = ((s - truth[:, -1]) ** 2).mean().item()
        cdrift.append(cd); mses.append(mse)
        ref = onestep[seed] if seed < len(onestep) else float("nan")
        print(f"seed {seed}: |divE-rho| {cd:.2e} | field MSE {mse:.2e}  (Exp5 1-step was {ref:.2e})")

    cd = np.array(cdrift); m = np.array(mses)
    d1 = bool(cd.max() <= 1e-4)
    d2 = bool(m.max() < 5e-3)
    out = {"device": dev, "K": a.K, "constraint_drift": cdrift, "field_mse": mses,
           "exp5_1step_charged_mse": onestep, "D1_constraint": d1, "D2_stability_rescued": d2,
           "charged_pushforward_works": bool(d1 and d2)}
    print(f"\nD1 charged constraint held (max |divE-rho| {cd.max():.1e} <= 1e-4): {d1}")
    print(f"D2 stability rescued (max field MSE {m.max():.2e} < 5e-3, no divergence): {d2}")
    print(f"\nCHARGED + PUSH-FORWARD: constraint held AND stable end-to-end on the non-trivial constraint: {out['charged_pushforward_works']}")
    (res / "exp6_charged_pushforward.json").write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(figsize=(8, 5)); x = np.arange(a.nseeds); w = 0.36
    ax.bar(x - w / 2, np.clip(onestep[:a.nseeds], 1e-6, None), w, color="navy", label="Exp 5: charged 1-step (diverges)")
    ax.bar(x + w / 2, np.clip(m, 1e-6, None), w, color="crimson", label="Exp 6: charged push-forward")
    ax.set_yscale("log"); ax.set_xticks(x); ax.set_xticklabels([f"s{i}" for i in range(a.nseeds)])
    ax.set_ylabel("charged long-rollout field MSE"); ax.legend(fontsize=8)
    ax.set_title(f"Charged + push-forward: does the stability fix rescue accuracy on the non-trivial constraint?\nmax MSE {m.max():.1e} (1-step diverged to ~0.35)")
    fig.tight_layout(); fig.savefig(res / "exp6_charged_pushforward.png", dpi=140)
    print("saved hailmary/results/exp6_charged_pushforward.json + .png")


if __name__ == "__main__":
    main()
