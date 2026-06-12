"""Step 05 — Phase B gates: did the net's invariant trace the gravity well?

The reshaping freedom is now PER POSITION (any h_x(g_x(Δ,Δ)) with h_x' > 0
solves the task), so the readout must cancel h_x. The gradient ratio does:

    ∂f/∂Δt = h' · 2A(x)Δt      ∂f/∂Δx = −h' · 2B(x)Δx

    ⇒  −(∂f/∂Δt / ∂f/∂Δx) · (Δx/Δt) = A(x)/B(x)     (h' cancels)

Gates (pre-registered in notes/lab_notebook.md):
  P3 the per-sample ratio estimate, binned over anchor position, reproduces the
     true profile A(x)/B(x) — correlation > 0.9, well depth recovered at x=0
  P4 per-position-bin isotonic R² of z vs the local invariant > 0.95
  plus the alignment gate against the LOCAL metric gradient (2AΔt, −2BΔx)
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
    X_RANGE,
    load_model,
    metric_A,
    metric_B,
    sample_observations_well,
    well_invariant,
)
from sklearn.isotonic import IsotonicRegression

N_BINS = 12
ETA_MIN = 0.25  # near eta=0 the dx-gradient vanishes and the ratio is 0/0 noise


def main() -> None:
    k = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    model = load_model(f"model_well_k{k}")
    rng = np.random.default_rng(99)

    obs_np, tau, eta = sample_observations_well(20_000, rng)
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
    g = g.detach().numpy()  # columns: d/dxp, d/dΔt, d/dΔx
    z = z.detach().numpy()

    xp, d = obs_np[:, 0], obs_np[:, 1:]
    inv_true = well_invariant(xp, d)

    # alignment with the LOCAL metric gradient
    g_loc = np.stack([2 * metric_A(xp) * d[:, 0], -2 * metric_B(xp) * d[:, 1]], axis=1)
    gd = g[:, 1:]
    cos = np.sum(gd * g_loc, axis=1) / (
        np.linalg.norm(gd, axis=1) * np.linalg.norm(g_loc, axis=1) + 1e-12
    )
    sign = np.sign(np.median(cos))
    align = float(np.median(np.abs(cos)))
    consist = float(np.mean(np.sign(cos) == sign))

    # the reshaping-proof ratio estimate, away from the eta ~ 0 degeneracy
    ok = np.abs(eta) > ETA_MIN
    ratio = -(g[ok, 1] / g[ok, 2]) * (d[ok, 1] / d[ok, 0])

    bins = np.linspace(*X_RANGE, N_BINS + 1)
    centers = 0.5 * (bins[:-1] + bins[1:])
    est, lo_q, hi_q, r2s = [], [], [], []
    xo = xp[ok]
    for i in range(N_BINS):
        m = (xo >= bins[i]) & (xo < bins[i + 1])
        est.append(np.median(ratio[m]))
        lo_q.append(np.quantile(ratio[m], 0.25))
        hi_q.append(np.quantile(ratio[m], 0.75))
        mb = (xp >= bins[i]) & (xp < bins[i + 1])
        iso = IsotonicRegression(increasing="auto").fit(inv_true[mb], z[mb])
        pred = iso.predict(inv_true[mb])
        r2s.append(1 - np.sum((z[mb] - pred) ** 2) / np.sum((z[mb] - z[mb].mean()) ** 2))

    est = np.array(est)
    truth = metric_A(centers) / metric_B(centers)
    corr = float(np.corrcoef(est, truth)[0, 1])
    depth_true = float(metric_A(np.zeros(1))[0] / metric_B(np.zeros(1))[0])
    depth_est = float(est[np.argmin(np.abs(centers))])

    print(f"K={k} gravity-well gates:")
    print(f"P4 per-bin isotonic R²: min = {min(r2s):.4f}  (gate: > 0.95)")
    print(f"   local-metric alignment: |cos| = {align:.4f}, sign-consistency = {consist:.4f}")
    print(f"P3 ratio-profile correlation with truth: r = {corr:.4f}  (gate: > 0.9)")
    print(f"   well depth at x=0: estimated A/B = {depth_est:.4f}, true = {depth_true:.4f}")

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    xs = np.linspace(*X_RANGE, 300)
    axes[0].plot(xs, metric_A(xs) / metric_B(xs), "k-", lw=2, label="true A(x)/B(x)")
    axes[0].errorbar(
        centers,
        est,
        yerr=[est - np.array(lo_q), np.array(hi_q) - est],
        fmt="o",
        color="crimson",
        capsize=3,
        label="read out of the trained network",
    )
    axes[0].set_xlabel("position x")
    axes[0].set_ylabel("A(x) / B(x)")
    axes[0].set_title("the gravity well, traced by the net's learned invariant\n"
                      "(never supervised on a metric, a well, or curvature)")
    axes[0].legend()

    axes[1].bar(centers, r2s, width=0.45, color="steelblue")
    axes[1].axhline(0.95, color="crimson", ls="--", lw=1)
    axes[1].set_ylim(0.9, 1.001)
    axes[1].set_xlabel("position x")
    axes[1].set_ylabel("isotonic R² (z vs local invariant)")
    axes[1].set_title("monotone dependence on the LOCAL invariant, per position bin")

    out = RESULTS / f"05_gates_well_k{k}.png"
    fig.tight_layout()
    fig.savefig(out, dpi=140)
    print(f"plot -> {out}")

    (RESULTS / f"05_gates_well_k{k}.json").write_text(
        json.dumps(
            {
                "k": k,
                "alignment": align,
                "sign_consistency": consist,
                "min_bin_isotonic_r2": float(min(r2s)),
                "ratio_profile_correlation": corr,
                "depth_estimated": depth_est,
                "depth_true": depth_true,
                "bin_centers": centers.tolist(),
                "ratio_estimate": est.tolist(),
            },
            indent=1,
        )
    )


if __name__ == "__main__":
    main()
