"""Hail Mary — Experiment 2: the GAUGE wall, isolated (predict-invariant beats predict-gauge-dependent).

Exp 1 handled the constraint. This isolates gauge freedom — the "metric is not unique" wall, the one that stalled
numerical relativity for 40 years. In Maxwell (2-D), the vector potential A (with B_z = curl A) has gauge freedom
A -> A + grad(lambda): infinitely many potentials give the SAME physical field B. That is the degenerate valley in
ML terms — one physical input maps to many correct targets, so any net asked to predict the gauge-dependent
potential is solving an ill-posed regression and can only return the (wrong) mean.

The fix is our project's recurring lesson (judge by invariants, not gauge-dependent numbers; cert #86 no-unique-law):
predict in a FIXED gauge / predict the invariant. And the Coulomb gauge condition div A = 0 is enforced by exactly
the same Leray projection as the Gauss constraint in Exp 1 — so the modular pipeline handles gauge and constraint
with the SAME module.

Setup: distinct physical fields B_z; for each, G copies of its potential in RANDOM gauges (A = A_coulomb + grad
lambda). Map B_z -> A.
  BASELINE: predict the raw (random-gauge) A  -> ill-posed (one B_z, many A) -> test loss floored by gauge variance.
  PLAN:     predict A then the gauge-fix projection (div A = 0) -> unique Coulomb A -> well-posed -> low loss.

Pre-reg (2026-06-20):
  G1 GAUGE WALL: baseline test MSE >= 100x Plan test MSE (gauge-dependent target is ill-posed; gauge-fixed is well-posed).
  G2 INVARIANT PRESERVED: Plan's curl(predicted A) reproduces B_z (relative MSE < 1e-2) — the physics is recovered.
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

from modules import FNO2d, leray_project, wavenumbers

L = 2 * np.pi


def smooth_field(rng, n, KX, KY, kcut=4.0):
    f = rng.standard_normal((n, n)); K2 = (KX ** 2 + KY ** 2)
    F = np.fft.fft2(f) * np.exp(-K2 / (2 * kcut ** 2))
    g = np.real(np.fft.ifft2(F)); return (g / (g.std() + 1e-9)).astype(np.float32)


def curlA(Ax, Ay, KX, KY):
    """B_z = dAy/dx - dAx/dy (the gauge-invariant content of A)."""
    dAy_dx = torch.fft.ifft2(1j * KX * torch.fft.fft2(Ay)).real
    dAx_dy = torch.fft.ifft2(1j * KY * torch.fft.fft2(Ax)).real
    return dAy_dx - dAx_dy


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", default="mps" if torch.backends.mps.is_available() else ("cuda" if torch.cuda.is_available() else "cpu"))
    ap.add_argument("--grid", type=int, default=32)
    ap.add_argument("--nphys", type=int, default=200)     # distinct physical fields
    ap.add_argument("--gauges", type=int, default=4)       # random gauges per physical field (makes the valley explicit)
    ap.add_argument("--steps", type=int, default=3000)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--predictor", default="cnn", choices=["cnn", "fno"])
    ap.add_argument("--fno-modes", type=int, default=12)
    a = ap.parse_args(); dev = a.device; n = a.grid
    print(f"device={dev} grid={n} nphys={a.nphys} gauges={a.gauges} steps={a.steps} seed={a.seed}")

    KXn = np.fft.fftfreq(n, d=L / n) * 2 * np.pi
    KXnp, KYnp = np.meshgrid(KXn, KXn, indexing="ij")
    if n % 2 == 0:
        KXnp = KXnp.copy(); KYnp = KYnp.copy(); KXnp[n // 2, :] = 0.0; KYnp[:, n // 2] = 0.0
    K2safe_np = KXnp ** 2 + KYnp ** 2; K2safe_np[K2safe_np == 0] = 1.0
    KX, KY, K2safe = wavenumbers(n, L, dev)

    def coulomb_A(Bz):
        Bh = np.fft.fft2(Bz)
        Ax = np.real(np.fft.ifft2(1j * KYnp * Bh / K2safe_np))
        Ay = np.real(np.fft.ifft2(-1j * KXnp * Bh / K2safe_np))
        return Ax.astype(np.float32), Ay.astype(np.float32)

    def grad_lambda(rng):
        lam = smooth_field(rng, n, KXnp, KYnp); Lh = np.fft.fft2(lam)
        gx = np.real(np.fft.ifft2(1j * KXnp * Lh)); gy = np.real(np.fft.ifft2(1j * KYnp * Lh))
        return gx.astype(np.float32), gy.astype(np.float32)

    def dataset(seed, nphys):
        rng = np.random.default_rng(seed); Bz, Araw, Acoul = [], [], []
        for _ in range(nphys):
            b = smooth_field(rng, n, KXnp, KYnp); ax, ay = coulomb_A(b)
            for _ in range(a.gauges):                       # several random gauges of the SAME physics
                gx, gy = grad_lambda(rng)
                Bz.append(b); Araw.append(np.stack([ax + gx, ay + gy])); Acoul.append(np.stack([ax, ay]))
        return (torch.tensor(np.stack(Bz))[:, None], torch.tensor(np.stack(Araw)), torch.tensor(np.stack(Acoul)))

    Btr, Araw_tr, Acoul_tr = dataset(a.seed, a.nphys)
    Bte, Araw_te, Acoul_te = dataset(a.seed + 99, a.nphys // 4)

    def cnn():
        ch = 48
        return nn.Sequential(
            nn.Conv2d(1, ch, 3, padding=1, padding_mode="circular"), nn.GELU(),
            nn.Conv2d(ch, ch, 3, padding=1, padding_mode="circular"), nn.GELU(),
            nn.Conv2d(ch, ch, 3, padding=1, padding_mode="circular"), nn.GELU(),
            nn.Conv2d(ch, 2, 3, padding=1, padding_mode="circular"))

    def run(mode):
        torch.manual_seed(a.seed); net = (FNO2d(1, 2, modes=a.fno_modes) if a.predictor == "fno" else cnn()).to(dev); opt = torch.optim.Adam(net.parameters(), lr=2e-3)
        rng = np.random.default_rng(a.seed)
        tgt = (Araw_tr if mode == "baseline" else Acoul_tr)
        for st in range(a.steps):
            idx = rng.integers(0, len(Btr), 64); xb = Btr[idx].to(dev); yb = tgt[idx].to(dev)
            pred = net(xb)
            if mode == "plan":                              # gauge-fix module = the SAME Leray projection as Exp 1
                ex, ey = leray_project(pred[:, 0], pred[:, 1], KX, KY, K2safe); pred = torch.stack([ex, ey], 1)
            loss = nn.functional.mse_loss(pred, yb)
            opt.zero_grad(); loss.backward(); opt.step()
        net.eval()
        with torch.no_grad():
            xb = Bte.to(dev)
            pred = net(xb)
            if mode == "plan":
                ex, ey = leray_project(pred[:, 0], pred[:, 1], KX, KY, K2safe); pred = torch.stack([ex, ey], 1)
            ytgt = (Araw_te if mode == "baseline" else Acoul_te).to(dev)
            test_mse = nn.functional.mse_loss(pred, ytgt).item()
            # gauge-invariant check: does curl(pred A) reproduce B_z?
            bpred = curlA(pred[:, 0], pred[:, 1], KX, KY)
            inv = (((bpred - xb[:, 0]) ** 2).mean() / (xb[:, 0] ** 2).mean()).item()
        return test_mse, inv

    base_mse, base_inv = run("baseline")
    plan_mse, plan_inv = run("plan")
    g1 = bool(base_mse >= 100 * plan_mse)
    g2 = bool(plan_inv < 1e-2)
    out = {"device": dev, "grid": n, "gauges": a.gauges, "seed": a.seed,
           "baseline_test_mse": base_mse, "plan_test_mse": plan_mse, "ratio": base_mse / (plan_mse + 1e-12),
           "baseline_curl_recovers_Bz": base_inv, "plan_curl_recovers_Bz": plan_inv,
           "G1_gauge_wall": g1, "G2_invariant_preserved": g2, "invariant_beats_gaugedependent": bool(g1 and g2)}
    print(f"\nbaseline (predict raw-gauge A) test MSE: {base_mse:.3e}")
    print(f"plan (gauge-fix projection)      test MSE: {plan_mse:.3e}   (ratio {out['ratio']:.0f}x)")
    print(f"G1 gauge wall (baseline >= 100x plan -- gauge-dependent target ill-posed): {g1}")
    print(f"G2 invariant preserved (curl(plan A) recovers B_z, rel-MSE {plan_inv:.2e} < 1e-2): {g2}")
    print(f"\nPREDICT-INVARIANT BEATS PREDICT-GAUGE-DEPENDENT (gauge wall dissolved by the projection module): {out['invariant_beats_gaugedependent']}")
    res = Path(__file__).resolve().parent / "results"; res.mkdir(exist_ok=True)
    (res / f"exp2_gauge_{a.predictor}_s{a.seed}.json").write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.bar(["baseline\n(predict raw-gauge A)", "plan\n(gauge-fix projection)"], [base_mse, plan_mse],
           color=["navy", "crimson"]); ax.set_yscale("log"); ax.set_ylabel("held-out potential MSE")
    ax.set_title(f"The gauge wall: predicting a gauge-dependent potential is ill-posed\n"
                 f"(floored by gauge variance); the gauge-fix projection makes it well-posed ({out['ratio']:.0f}x)")
    fig.tight_layout(); fig.savefig(res / f"exp2_gauge_{a.predictor}_s{a.seed}.png", dpi=140)
    print(f"saved hailmary/results/exp2_gauge_{a.predictor}_s{a.seed}.json + .png")


if __name__ == "__main__":
    main()
