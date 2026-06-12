"""Step 04 — gates for the v0.1 mixed-sector model.

The orbit space is now four disjoint half-lines (one per causal sector), still
one continuous dimension — so K=1 should STILL saturate. The pre-registered
question is HOW one scalar covers four branches: the latent must be monotone in
s² *within* each sector while keeping different sectors' orbits separated
(injectivity is already certified behaviorally by test accuracy, since
cross-sector pairs are negatives).

Readouts:
  per-sector isotonic R² of z vs s²  (gate: > 0.95 in all four)
  per-sector gradient alignment with ∇s² = (2t, −2x), sign consistency per
  sector (a global sign per sector is allowed — reshaping freedom is per branch)
  the four-branch portrait: z vs s² colored by sector — the light cone appears
  as the gaps between branches
  level sets over the full (x, t) plane
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
from curvlib import (
    RESULTS,
    SECTOR_NAMES,
    in_region_mixed,
    interval2,
    load_model,
    sample_observations_mixed,
)
from sklearn.isotonic import IsotonicRegression


def main() -> None:
    k = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    model = load_model(f"model_mixed_k{k}")
    rng = np.random.default_rng(99)

    obs_np, sec = sample_observations_mixed(6000, rng)
    obs = torch.from_numpy(obs_np).requires_grad_(True)
    z = model.enc(obs)[:, 0] if k == 1 else None
    if z is None:
        zk = model.enc(obs)
        zc = zk - zk.mean(0)
        _, s, v = torch.linalg.svd(zc.detach(), full_matrices=False)
        print(f"PCA explained variance: {np.round((s**2 / (s**2).sum()).numpy(), 3)}")
        z = zc @ v[0]
    (g,) = torch.autograd.grad(z.sum(), obs)
    g = g.detach().numpy()
    z = z.detach().numpy()
    s2 = interval2(obs_np)

    g_mink = np.stack([2 * obs_np[:, 0], -2 * obs_np[:, 1]], axis=1)
    cos_m = np.sum(g * g_mink, axis=1) / (
        np.linalg.norm(g, axis=1) * np.linalg.norm(g_mink, axis=1) + 1e-12
    )

    results = {}
    print(f"K={k} mixed-sector gates:")
    for si, name in enumerate(SECTOR_NAMES):
        m = sec == si
        iso = IsotonicRegression(increasing="auto").fit(s2[m], z[m])
        pred = iso.predict(s2[m])
        r2 = 1 - np.sum((z[m] - pred) ** 2) / np.sum((z[m] - z[m].mean()) ** 2)
        sign = np.sign(np.median(cos_m[m]))
        align = float(np.median(np.abs(cos_m[m])))
        consist = float(np.mean(np.sign(cos_m[m]) == sign))
        results[name] = {"isotonic_r2": float(r2), "alignment": align, "sign_consistency": consist}
        print(f"  {name:6s}: isotonic R² = {r2:.4f}  |cos| = {align:.4f}  sign-consistency = {consist:.4f}")

    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    for si, name in enumerate(SECTOR_NAMES):
        m = sec == si
        axes[0].scatter(s2[m], z[m], s=3, alpha=0.4, label=name)
    axes[0].set_xlabel("true s² = t² − x²")
    axes[0].set_ylabel("learned latent z")
    axes[0].set_title("the four-branch portrait:\none scalar covering four causal sectors")
    axes[0].legend(markerscale=4)

    tg = np.linspace(-7.2, 7.2, 500)
    xg = np.linspace(-7.2, 7.2, 500)
    X, T = np.meshgrid(xg, tg)
    mask = in_region_mixed(T, X)
    pts = torch.from_numpy(np.stack([T.ravel(), X.ravel()], axis=1).astype(np.float32))
    with torch.no_grad():
        zz = model.enc(pts)
        zg = zz[:, 0] if k == 1 else (zz - zz.mean(0)) @ torch.linalg.svd(
            (zz - zz.mean(0)), full_matrices=False
        )[2][0]
    Z = zg.numpy().reshape(T.shape)
    Z[~mask] = np.nan
    cs = axes[1].contourf(X, T, Z, levels=24, cmap="viridis")
    fig.colorbar(cs, ax=axes[1], label="learned latent z")
    axes[1].plot([-7.2, 7.2], [-7.2, 7.2], "w:", lw=1)
    axes[1].plot([-7.2, 7.2], [7.2, -7.2], "w:", lw=1)
    axes[1].set_xlabel("x")
    axes[1].set_ylabel("t")
    axes[1].set_title("level sets over all four sectors\n(dotted = the light cone)")

    out = RESULTS / f"04_gates_mixed_k{k}.png"
    fig.tight_layout()
    fig.savefig(out, dpi=140)
    print(f"plot -> {out}")
    (RESULTS / f"04_gates_mixed_k{k}.json").write_text(json.dumps(results, indent=1))


if __name__ == "__main__":
    main()
