"""Hail Mary — Experiment 5 (stress test): does the projection generalize from the TRIVIAL constraint to a real one?

Exp 1 showed the projection holds the Gauss constraint -- but only in VACUUM (div E = 0, the easy linear case).
The honest stress test (robustness north star): a NON-TRIVIAL, affine constraint. Add static charges rho(x) so
the constraint is div E = rho (rho != 0). The dynamics are unchanged (with J=0, dE/dt = curl B is rho-independent
and preserves div E exactly), so this cleanly isolates ONE thing: does the projection generalize from the linear
subspace {div E = 0} to the affine surface {div E = rho}?

Affine Leray projection: E_new = E - grad(phi), lap(phi) = div E - rho  -> div(E_new) = rho by construction.
  BASELINE (monolith): dynamics MSE + soft penalty (div E - rho)^2; no projection at rollout.
  PLAN A   (modular):  dynamics MSE only; affine projection (div E = rho) each rollout step.

Pre-reg (2026-06-20), grid 32, charged (rho != 0), 3 seeds, horizon 100:
  C1 CONSTRAINT GENERALIZES: Plan A keeps max|div E - rho| <= 1e-4 over the rollout while the baseline's grows to
     >= 100x Plan A's -- the projection works on the non-trivial constraint, not just vacuum.
  C2 ACCURACY: Plan A field MSE <= baseline at the long horizon (mean over seeds).
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

from maxwell import Maxwell2D
from modules import PredictorCNN, div_E, wavenumbers


def affine_project_np(sim, Ex, Ey, rho):
    """numpy: project E so div E = rho (for data init + ground-truth checks)."""
    divE = sim.ddx(Ex) + sim.ddy(Ey)
    phi_hat = -np.fft.fft2(divE - rho) / sim.K2safe
    gx = np.real(np.fft.ifft2(1j * sim.KX * phi_hat)); gy = np.real(np.fft.ifft2(1j * sim.KY * phi_hat))
    return Ex - gx, Ey - gy


def affine_project_t(Ex, Ey, rho, KX, KY, K2safe):
    """torch: project E so div E = rho (the constraint-enforcing module, generalized to the affine surface)."""
    d = div_E(Ex, Ey, KX, KY)
    phi_hat = -torch.fft.fft2(d - rho) / K2safe
    gx = torch.fft.ifft2(1j * KX * phi_hat).real; gy = torch.fft.ifft2(1j * KY * phi_hat).real
    return Ex - gx, Ey - gy


def make_charged(n_traj, nsteps, grid, seed):
    sim = Maxwell2D(n=grid); rng = np.random.default_rng(seed); trajs, rhos = [], []
    for _ in range(n_traj):
        s = sim.random_state(rng)
        rho = sim.random_state(rng)[0] * 0.5
        rh = np.fft.fft2(rho)                                                  # band-limit rho to what the (Nyquist-
        if grid % 2 == 0:                                                      # zeroed) divergence operator can represent,
            rh[grid // 2, :] = 0; rh[:, grid // 2] = 0                         # else div E can never equal rho there
        rho = np.real(np.fft.ifft2(rh)); rho = rho - rho.mean()               # static zero-mean charge density
        Ex, Ey = affine_project_np(sim, s[0], s[1], rho)                       # start exactly on div E = rho
        s0 = np.stack([Ex, Ey, s[2]])
        trajs.append(sim.rollout(s0, nsteps)); rhos.append(rho)
    return np.stack(trajs).astype(np.float32), np.stack(rhos).astype(np.float32), sim


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", default="mps" if torch.backends.mps.is_available() else ("cuda" if torch.cuda.is_available() else "cpu"))
    ap.add_argument("--grid", type=int, default=32); ap.add_argument("--traj", type=int, default=96)
    ap.add_argument("--steps", type=int, default=3000); ap.add_argument("--horizon", type=int, default=100)
    ap.add_argument("--lam", type=float, default=1.0); ap.add_argument("--nseeds", type=int, default=3)
    a = ap.parse_args(); dev = a.device
    KX, KY, K2safe = wavenumbers(a.grid, 2 * np.pi, dev)
    res = Path(__file__).resolve().parent / "results"; res.mkdir(exist_ok=True)
    print(f"device={dev} grid={a.grid} steps={a.steps} horizon={a.horizon} nseeds={a.nseeds}")

    # ground-truth sanity: charged evolution preserves div E = rho
    tr0, rho0, sim = make_charged(2, 60, a.grid, 0)
    cdrift = max(np.abs(sim.ddx(tr0[0, t, 0]) + sim.ddy(tr0[0, t, 1]) - rho0[0]).max() for t in range(tr0.shape[1]))
    print(f"ground-truth |div E - rho| over 60 steps: {cdrift:.2e} (should be ~0 -- charged constraint is preserved)")

    base_div, plan_div, base_mse, plan_mse = [], [], [], []
    for seed in range(a.nseeds):
        tr, rho, sim = make_charged(a.traj, 40, a.grid, seed)
        X = torch.tensor(tr[:, :-1].reshape(-1, 3, a.grid, a.grid)); Yt = torch.tensor(tr[:, 1:].reshape(-1, 3, a.grid, a.grid))
        rho_pp = torch.tensor(np.repeat(rho, tr.shape[1] - 1, axis=0))         # rho per (traj,time) pair
        rhod = torch.tensor(rho).to(dev)

        def train(mode):
            torch.manual_seed(seed); net = PredictorCNN().to(dev); opt = torch.optim.Adam(net.parameters(), lr=2e-3)
            rng = np.random.default_rng(seed)
            for st in range(a.steps):
                idx = rng.integers(0, len(X), 64); xb = X[idx].to(dev); yb = Yt[idx].to(dev); rb = rho_pp[idx].to(dev)
                pred = net(xb); loss = nn.functional.mse_loss(pred, yb)
                if mode == "baseline":
                    d = div_E(pred[:, 0], pred[:, 1], KX, KY)
                    loss = loss + a.lam * ((d - rb) ** 2).mean()
                opt.zero_grad(); loss.backward(); opt.step()
            return net.eval()

        b = train("baseline"); p = train("plana")
        rng = np.random.default_rng(777 + seed)
        # held-out charged worlds
        te, rte, _ = make_charged(16, a.horizon, a.grid, 5000 + seed)
        truth = torch.tensor(te).to(dev); s0 = torch.tensor(te[:, 0]).to(dev); rt = torch.tensor(rte).to(dev)

        @torch.no_grad()
        def roll(net, proj):
            s = s0.clone()
            for _ in range(a.horizon):
                s = net(s)
                if proj:
                    ex, ey = affine_project_t(s[:, 0], s[:, 1], rt, KX, KY, K2safe); s = torch.stack([ex, ey, s[:, 2]], 1)
            cd = (div_E(s[:, 0], s[:, 1], KX, KY) - rt).abs().amax(dim=(-1, -2)).mean().item()
            mse = ((s - truth[:, -1]) ** 2).mean().item()
            return cd, mse

        bd, bm = roll(b, False); pd, pm = roll(p, True)
        base_div.append(bd); plan_div.append(pd); base_mse.append(bm); plan_mse.append(pm)
        print(f"seed {seed}: |divE-rho| base {bd:.2e} plan {pd:.2e} | field MSE base {bm:.2e} plan {pm:.2e}")

    bd, pd = np.array(base_div), np.array(plan_div); bm, pm = np.array(base_mse), np.array(plan_mse)
    c1 = bool(pd.max() <= 1e-4 and np.all(bd >= 100 * pd))
    c2 = bool(pm.mean() <= bm.mean())
    out = {"device": dev, "ground_truth_constraint_drift": float(cdrift),
           "base_div": base_div, "plan_div": plan_div, "base_mse": base_mse, "plan_mse": plan_mse,
           "C1_constraint_generalizes": c1, "C2_accuracy": c2, "projection_generalizes_to_charged": bool(c1 and c2)}
    print(f"\nC1 charged constraint held (plan |divE-rho| max {pd.max():.1e} <=1e-4, base >=100x): {c1}")
    print(f"C2 plan accuracy <= baseline (mean MSE plan {pm.mean():.2e} vs base {bm.mean():.2e}): {c2}")
    print(f"\nPROJECTION GENERALIZES TO THE NON-TRIVIAL (CHARGED) CONSTRAINT: {out['projection_generalizes_to_charged']}")
    (res / "exp5_charged_constraint.json").write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(1, 2, figsize=(13, 5)); x = np.arange(a.nseeds); w = 0.36
    ax[0].bar(x - w / 2, np.clip(bd, 1e-8, None), w, color="navy", label="baseline (soft penalty)")
    ax[0].bar(x + w / 2, np.clip(pd, 1e-8, None), w, color="crimson", label="Plan A (affine projection)")
    ax[0].set_yscale("log"); ax[0].set_xticks(x); ax[0].set_xticklabels([f"s{i}" for i in range(a.nseeds)])
    ax[0].set_ylabel("max |div E - rho| (charged constraint violation)"); ax[0].legend(fontsize=8)
    ax[0].set_title("Charged (rho!=0) constraint: does projection still hold it?")
    ax[1].bar(x - w / 2, np.clip(bm, 1e-8, None), w, color="navy", label="baseline")
    ax[1].bar(x + w / 2, np.clip(pm, 1e-8, None), w, color="crimson", label="Plan A")
    ax[1].set_yscale("log"); ax[1].set_xticks(x); ax[1].set_xticklabels([f"s{i}" for i in range(a.nseeds)])
    ax[1].set_ylabel("long-rollout field MSE"); ax[1].legend(fontsize=8); ax[1].set_title("Accuracy (charged)")
    fig.tight_layout(); fig.savefig(res / "exp5_charged_constraint.png", dpi=140)
    print("saved hailmary/results/exp5_charged_constraint.json + .png")


if __name__ == "__main__":
    main()
