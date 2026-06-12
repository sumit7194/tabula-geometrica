"""Step 08 — gates for the 3+1 replication of Phase A.

Same reshaping-proof readouts as step 03, in full dimensionality:
isotonic R² of z vs s² = t² − |x⃗|²; gradient alignment with the Minkowski
gradient (2t, −2x, −2y, −2z) — three minus signs to earn now; Euclidean control;
and the (t, x) slice (y = z = 0) of the level sets against the true hyperbolas.
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
from curvlib import RESULTS, in_region, interval2_3p1, load_model, sample_observations_3p1
from sklearn.isotonic import IsotonicRegression


def main() -> None:
    k = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    model = load_model(f"model_flat3p1_k{k}")
    rng = np.random.default_rng(99)

    obs_np = sample_observations_3p1(6000, rng)
    obs = torch.from_numpy(obs_np).requires_grad_(True)
    zk = model.enc(obs)
    if k == 1:
        z = zk[:, 0]
    else:
        zc = zk - zk.mean(0)
        _, s, v = torch.linalg.svd(zc.detach(), full_matrices=False)
        print(f"PCA explained variance: {np.round((s**2 / (s**2).sum()).numpy(), 3)}")
        z = zc @ v[0]
    (g,) = torch.autograd.grad(z.sum(), obs)
    g = g.detach().numpy()
    z = z.detach().numpy()
    s2 = interval2_3p1(obs_np)

    iso = IsotonicRegression(increasing="auto").fit(s2, z)
    r2 = 1 - np.sum((z - iso.predict(s2)) ** 2) / np.sum((z - z.mean()) ** 2)

    g_mink = np.concatenate([2 * obs_np[:, :1], -2 * obs_np[:, 1:]], axis=1)
    cos_m = np.sum(g * g_mink, axis=1) / (
        np.linalg.norm(g, axis=1) * np.linalg.norm(g_mink, axis=1) + 1e-12
    )
    sign = np.sign(np.median(cos_m))
    align = float(np.median(np.abs(cos_m)))
    consist = float(np.mean(np.sign(cos_m) == sign))

    g_euc = 2 * obs_np
    cos_e = np.sum(g * g_euc, axis=1) / (
        np.linalg.norm(g, axis=1) * np.linalg.norm(g_euc, axis=1) + 1e-12
    )
    align_euc = float(np.median(np.abs(cos_e)))

    print(f"K={k} 3+1 gates:")
    print(f"R2 monotone fit z ~ h(s²):        R² = {r2:.4f}   (gate: > 0.95)")
    print(f"R3 Minkowski gradient alignment:  |cos| = {align:.4f}, sign-consistency = {consist:.4f}")
    print(f"R4 Euclidean control alignment:   |cos| = {align_euc:.4f}   (gate: well below R3)")

    tg = np.linspace(0.3, 7.2, 400)
    xg = np.linspace(-6.6, 6.6, 400)
    X, T = np.meshgrid(xg, tg)
    mask = in_region(T, X)
    pts = np.stack(
        [T.ravel(), X.ravel(), np.zeros(T.size), np.zeros(T.size)], axis=1
    ).astype(np.float32)
    with torch.no_grad():
        zz = model.enc(torch.from_numpy(pts))
        zg = zz[:, 0] if k == 1 else (zz - zz.mean(0)) @ torch.linalg.svd(
            zz - zz.mean(0), full_matrices=False
        )[2][0]
    Z = zg.numpy().reshape(T.shape)
    Z[~mask] = np.nan

    fig, ax = plt.subplots(figsize=(9, 6))
    cs = ax.contourf(X, T, Z, levels=18, cmap="viridis")
    fig.colorbar(cs, label="learned latent z")
    for tau in (0.75, 1.25, 1.75, 2.25, 2.75):
        xs = np.linspace(-6.6, 6.6, 400)
        ts = np.sqrt(tau**2 + xs**2)
        m = in_region(ts, xs)
        ax.plot(xs[m], ts[m], "w--", lw=1)
    ax.set_xlabel("x  (slice y = z = 0)")
    ax.set_ylabel("t")
    ax.set_title(f"3+1, K={k}: (t,x)-slice of the learned latent vs true hyperbolas")
    out = RESULTS / f"08_gates_3p1_k{k}.png"
    fig.tight_layout()
    fig.savefig(out, dpi=140)
    print(f"plot -> {out}")

    (RESULTS / f"08_gates_3p1_k{k}.json").write_text(
        json.dumps(
            {
                "k": k,
                "isotonic_r2": float(r2),
                "alignment": align,
                "sign_consistency": consist,
                "euclidean_alignment": align_euc,
            },
            indent=1,
        )
    )


if __name__ == "__main__":
    main()
