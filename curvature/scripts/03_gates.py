"""Step 03 — the science gates: WHAT did the encoder learn?

The encoder is only pinned down up to a monotone reshaping of any invariant it
finds (any h(s²) with h' > 0 solves the task equally well), so every gate here
is reshaping-proof:

G1 invariant dependence — isotonic (monotone) fit of z against s²; report R².
G2 direction alignment — cosine between ∇z(t,x) and ∇s² = (2t, −2x) across
   on-distribution points. |cos| ≈ 1 everywhere means the net's notion of "what
   changes sameness" points along physics'. The stable SIGN pattern (z rising
   with t, falling with |x|, or the global flip) is the minus sign, earned.
G3 euclidean control — same alignment against ∇(t² + x²); must be poor. This is
   the "did it just learn distance-from-origin?" refutation.
G4 level sets — contours of z in the (x, t) plane against true hyperbolas.
   Hyperbolas = spacetime. Circles = it learned Euclidean junk.

For K > 1 the latent is reduced by PCA first; the explained-variance split tells
us how many latent dimensions the net actually used (prediction: one).
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
from curvlib import RESULTS, in_region, interval2, load_model, sample_observations
from sklearn.isotonic import IsotonicRegression


def scalar_latent(model, obs: torch.Tensor, k: int):
    """Reduce the K-dim latent to the scalar the net actually uses (PCA1)."""
    z = model.enc(obs)
    if k == 1:
        return z[:, 0], np.array([1.0])
    zc = z - z.mean(0)
    _, s, v = torch.linalg.svd(zc.detach(), full_matrices=False)
    evr = (s**2 / (s**2).sum()).numpy()
    return zc @ v[0], evr


def main() -> None:
    k = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    model = load_model(f"model_k{k}")
    rng = np.random.default_rng(99)

    obs_np = sample_observations(4000, rng)
    obs = torch.from_numpy(obs_np).requires_grad_(True)
    z, evr = scalar_latent(model, obs, k)
    (g,) = torch.autograd.grad(z.sum(), obs)
    g = g.detach().numpy()
    z = z.detach().numpy()
    s2 = interval2(obs_np)

    # G1: monotone fit z vs s2
    iso = IsotonicRegression(increasing="auto").fit(s2, z)
    pred = iso.predict(s2)
    r2 = 1 - np.sum((z - pred) ** 2) / np.sum((z - z.mean()) ** 2)

    # G2: alignment with the Minkowski gradient (2t, -2x)
    g_mink = np.stack([2 * obs_np[:, 0], -2 * obs_np[:, 1]], axis=1)
    cos_m = np.sum(g * g_mink, axis=1) / (
        np.linalg.norm(g, axis=1) * np.linalg.norm(g_mink, axis=1) + 1e-12
    )
    sign = np.sign(np.median(cos_m))
    align = float(np.median(np.abs(cos_m)))
    consistency = float(np.mean(np.sign(cos_m) == sign))

    # G3: euclidean control (2t, +2x)
    g_euc = 2 * obs_np
    cos_e = np.sum(g * g_euc, axis=1) / (
        np.linalg.norm(g, axis=1) * np.linalg.norm(g_euc, axis=1) + 1e-12
    )
    align_euc = float(np.median(np.abs(cos_e)))

    print(f"K={k}  (latent PCA explained variance: {np.round(evr, 3)})")
    print(f"G1 monotone fit z ~ h(s²):        R² = {r2:.4f}   (gate: > 0.95)")
    print(f"G2 Minkowski gradient alignment:  |cos| = {align:.4f}, "
          f"sign-consistency = {consistency:.4f}   (gate: > 0.95 both)")
    print(f"G3 Euclidean control alignment:   |cos| = {align_euc:.4f}   (gate: well below G2)")

    # G4: level sets over the sampled region
    tg = np.linspace(0.3, 7.2, 400)
    xg = np.linspace(-6.6, 6.6, 400)
    X, T = np.meshgrid(xg, tg)
    mask = in_region(T, X)
    pts = torch.from_numpy(
        np.stack([T.ravel(), X.ravel()], axis=1).astype(np.float32)
    )
    with torch.no_grad():
        zg, _ = scalar_latent(model, pts, k)
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
    ax.set_xlabel("x")
    ax.set_ylabel("t")
    ax.set_title(
        f"K={k}: level sets of the learned latent (filled) vs true hyperbolas "
        "t²−x²=const (dashed)\nIf they coincide, the net invented the spacetime interval."
    )
    out = RESULTS / f"03_gates_k{k}.png"
    fig.tight_layout()
    fig.savefig(out, dpi=140)
    print(f"plot -> {out}")

    (RESULTS / f"03_gates_k{k}.json").write_text(
        json.dumps(
            {
                "k": k,
                "explained_variance": evr.tolist(),
                "G1_isotonic_r2": float(r2),
                "G2_alignment": align,
                "G2_sign_consistency": consistency,
                "G3_euclidean_alignment": align_euc,
            },
            indent=1,
        )
    )


if __name__ == "__main__":
    main()
