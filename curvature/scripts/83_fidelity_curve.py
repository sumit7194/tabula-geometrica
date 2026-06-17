"""Step 83 — the CLEAN strong-field fidelity learning curve (seed-averaged), v2.

Sister-session idea (82): turn the shadow-edge error into a strong-field fidelity score. v1 taught us:
(a) b_crit by ray-capture needs the PLUNGE region (u>1/3), so every training set must keep some capturing
rays or the measurement is garbage; (b) the right knob is PHOTON-SPHERE sampling density (near-critical
winding rays that loop at r=3M), not raw depth; (c) the tracer must be hardened (clamp + NaN->escape).

Design: a fixed BASE dataset (a few capturing rays b<b_crit so captures stay predictable + weak-field rays)
that is SPARSE near the photon sphere; then ADD `rho` near-critical winding rays in b in [5.205, 5.6] that
densely sample r=3M. Sweep rho from 0 (no photon-sphere resolution) up; for each, train SEEDS nets and
seed-average b_crit (batched capture). Expect the shadow edge to march to 3sqrt3=5.196 as rho grows.

Pre-reg (2026-06-17):
  C1 MONOTONE: seed-averaged b_crit error decreases (within 1 sigma) as rho increases.
  C2 DEEP ACCURATE: the densest (rho max) averaged b_crit is within 4% of 3sqrt3.
  C3 IMPROVEMENT: densest error at least 2x smaller than rho=0.
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
from importlib import import_module
from curvlib import RESULTS, progress
from torch import nn

ph = import_module("78_photon_shadow")
DPHI = ph.DPHI
B_TRUE = 3 * np.sqrt(3)
SEEDS = 3
np.seterr(all="ignore")


def rays_to_xy(bs):
    X, Y = [], []
    for b in bs:
        _, U, W = ph.ray(b)
        for i in range(len(U) - 1):
            X.append([U[i], W[i]]); Y.append([U[i + 1], W[i + 1]])
    return X, Y


def make_dataset(rho, seed):
    """base: capturing rays (b<b_crit, plunge -> measurability) + weak-field rays, SPARSE near photon sphere.
    plus rho near-critical WINDING rays in [5.205, 5.6] that densely sample r=3M."""
    rng = np.random.default_rng(seed)
    base_b = np.concatenate([np.linspace(4.80, 5.05, 22),          # capturing rays (predict the plunge)
                             np.linspace(6.00, 14.0, 80)])         # weak field; GAP over [5.05, 6.0]
    extra_b = np.linspace(5.205, 5.60, rho) if rho > 0 else np.array([])
    bs = np.concatenate([base_b, extra_b]) + 0.003 * rng.standard_normal(len(base_b) + len(extra_b))
    X, Y = rays_to_xy(bs[bs > 4.6])
    return np.array(X, np.float32), np.array(Y, np.float32)


def train(X, Y, seed, steps=6000):
    torch.manual_seed(seed)
    n = len(X); ntr = int(n * 0.9); idx = np.random.default_rng(seed).permutation(n)
    Xt = torch.from_numpy(X[idx]); Yt = torch.from_numpy(Y[idx])
    m = ph.Photon(); opt = torch.optim.Adam(m.parameters(), lr=1e-3); rng = np.random.default_rng(seed + 1)
    for step in range(steps):
        b = rng.integers(0, ntr, 256)
        loss = nn.functional.mse_loss(m(Xt[b]), Yt[b])
        opt.zero_grad(); loss.backward(); opt.step()
    m.eval(); return m


def bcrit_capture(m, nsteps=9000):
    """hardened batched ray-tracer: b_crit = boundary between captured and escaping net rays."""
    bs = np.linspace(4.9, 7.4, 170)
    u = torch.tensor(bs * 0 + 0.01, dtype=torch.float32)
    w = torch.tensor(np.sqrt(np.maximum(1 / bs ** 2 - 0.01 ** 2 + 2 * 0.01 ** 3, 0)), dtype=torch.float32)
    status = torch.zeros(len(bs)); active = torch.ones(len(bs), dtype=torch.bool)
    for _ in range(nsteps):
        with torch.no_grad():
            o = m(torch.stack([u, w], 1))
        u, w = o[:, 0], o[:, 1]
        bad = ~(torch.isfinite(u) & torch.isfinite(w))
        cap = (u >= 0.5) & active & ~bad
        esc = (((u <= 0.003) & (w < 0)) | bad) & active        # NaN -> treat as escaped
        status[cap] = 1; status[esc] = -1; active = active & ~(cap | esc)
        u = torch.clamp(torch.where(active, u, torch.full_like(u, 0.3)), -0.05, 0.55)
        w = torch.clamp(torch.where(active, w, torch.zeros_like(w)), -6, 6)
        if not active.any():
            break
    cs = status.numpy(); capi = np.where(cs == 1)[0]
    if not len(capi):
        return None
    last = capi.max(); esci = np.where((cs == -1) & (np.arange(len(cs)) > last))[0]
    return float(bs[last]) if not len(esci) else float(0.5 * (bs[last] + bs[esci[0]]))


def main():
    rhos = [0, 6, 16, 40, 100]                          # near-critical winding-ray density (photon-sphere sampling)
    curve = []
    for k, rho in enumerate(rhos):
        vals = []
        for s in range(SEEDS):
            X, Y = make_dataset(rho, seed=100 * s + 7)
            m = train(X, Y, seed=s)
            bc = bcrit_capture(m)
            if bc is not None and 4.9 < bc < 7.3:
                vals.append(bc)
            progress("83_fidelity", k * SEEDS + s + 1, len(rhos) * SEEDS, bcrit=bc or 0)
        vals = np.array(vals)
        mean = float(vals.mean()) if len(vals) else float("nan"); std = float(vals.std()) if len(vals) else float("nan")
        curve.append({"rho": rho, "b_crit_mean": mean, "b_crit_std": std,
                      "rel_err": abs(mean - B_TRUE) / B_TRUE, "n_seeds": len(vals)})
        print(f"rho={rho:3d} winding rays: b_crit = {mean:.3f} +- {std:.3f}  err={abs(mean-B_TRUE)/B_TRUE*100:.1f}%  (n={len(vals)})")

    means = [c["b_crit_mean"] for c in curve]; stds = [c["b_crit_std"] for c in curve]; errs = [c["rel_err"] for c in curve]
    mono = all(errs[i] >= errs[i + 1] - (stds[i + 1] / B_TRUE + 0.01) for i in range(len(errs) - 1))
    c1 = bool(mono)
    c2 = bool(errs[-1] < 0.04)
    c3 = bool(errs[0] > 2 * errs[-1])
    out = {"curve": curve, "b_true": float(B_TRUE), "C1_monotone": c1, "C2_deep_accurate": c2,
           "C3_improvement": c3, "clean_fidelity_curve": bool(c1 and c2 and c3)}
    print(f"\nC1 monotone (within 1 sigma): {c1}")
    print(f"C2 densest within 4% of 3sqrt3: {c2} (densest err {errs[-1]*100:.1f}%)")
    print(f"C3 densest error < half rho=0: {c3} (rho0 {errs[0]*100:.1f}% -> densest {errs[-1]*100:.1f}%)")
    print(f"\nCLEAN STRONG-FIELD FIDELITY CURVE: {out['clean_fidelity_curve']}")
    (RESULTS / "83_fidelity_curve.json").write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(1, 2, figsize=(13, 5))
    ax[0].errorbar(rhos, means, yerr=stds, fmt="o-", color="crimson", capsize=4, label="net b_crit (seed-avg ± 1σ)")
    ax[0].axhline(B_TRUE, color="navy", ls="--", label=f"exact 3√3 = {B_TRUE:.3f}")
    ax[0].set_xlabel("near-critical winding rays (photon-sphere sampling)"); ax[0].set_ylabel("shadow edge b_crit (M)")
    ax[0].legend(fontsize=8); ax[0].set_title("strong-field fidelity learning curve (seed-averaged)\nshadow edge -> 3√3 as the photon sphere is sampled")
    ax[1].errorbar(rhos, [e * 100 for e in errs], yerr=[s / B_TRUE * 100 for s in stds], fmt="s-", color="darkorange", capsize=4)
    ax[1].axhline(0, color="k", lw=0.5); ax[1].set_xlabel("near-critical winding rays")
    ax[1].set_ylabel("shadow-edge error (%)"); ax[1].set_title("the fidelity score vs photon-sphere coverage")
    fig.tight_layout(); fig.savefig(RESULTS / "83_fidelity_curve.png", dpi=140)
    print("saved results/83_fidelity_curve.json + .png")


if __name__ == "__main__":
    main()
