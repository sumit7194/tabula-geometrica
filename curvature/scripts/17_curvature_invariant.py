"""Step 17 — the closing readout: the CURVATURE of the learned geometry.

Differentiate Phase E's trained metric-field network twice (Brioschi formula)
to get the Gaussian curvature of the geometry it learned from trajectories,
and compare against the true world's curvature. Invariants are coordinate-free
(Theorema Egregium): this is the one comparison that cannot be a coordinate
artifact. Pre-registration (G0, K1-K3) in the lab notebook.
"""

import importlib.util
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import torch
from curvlib import RESULTS, XY_RANGE, fields_2p1

spec = importlib.util.spec_from_file_location(
    "fe", Path(__file__).resolve().parent / "16_field_from_trajectories.py"
)
fe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fe)

FD = 1e-3


def brioschi(E, F, G, d):
    """Gaussian curvature from metric components and their derivative arrays.
    d holds first derivatives (Eu, Ev, Fu, Fv, Gu, Gv) and the three needed
    second derivatives (Evv, Fuv, Guu)."""
    m1 = np.stack([
        np.stack([-0.5 * d["Evv"] + d["Fuv"] - 0.5 * d["Guu"], 0.5 * d["Eu"],
                  d["Fu"] - 0.5 * d["Ev"]], -1),
        np.stack([d["Fv"] - 0.5 * d["Gu"], E, F], -1),
        np.stack([0.5 * d["Gv"], F, G], -1),
    ], -2)
    m2 = np.stack([
        np.stack([np.zeros_like(E), 0.5 * d["Ev"], 0.5 * d["Gu"]], -1),
        np.stack([0.5 * d["Ev"], E, F], -1),
        np.stack([0.5 * d["Gu"], F, G], -1),
    ], -2)
    return (np.linalg.det(m1) - np.linalg.det(m2)) / (E * G - F**2) ** 2


def K_from_func(metric_fn, X, Y, h=FD):
    """Curvature via finite differences of any metric function (E,F,G)(x,y)."""
    def at(dx, dy):
        return metric_fn(X + dx * h, Y + dy * h)

    E0, F0, G0 = at(0, 0)
    d = {}
    for name, idx in (("E", 0), ("F", 1), ("G", 2)):
        d[name + "u"] = (at(1, 0)[idx] - at(-1, 0)[idx]) / (2 * h)
        d[name + "v"] = (at(0, 1)[idx] - at(0, -1)[idx]) / (2 * h)
    d["Evv"] = (at(0, 1)[0] - 2 * E0 + at(0, -1)[0]) / h**2
    d["Guu"] = (at(1, 0)[2] - 2 * G0 + at(-1, 0)[2]) / h**2
    d["Fuv"] = (at(1, 1)[1] - at(1, -1)[1] - at(-1, 1)[1] + at(-1, -1)[1]) / (4 * h**2)
    return brioschi(E0, F0, G0, d)


def main() -> None:
    # G0: validate the curvature calculator on a known answer (2-sphere patch)
    gx = np.linspace(0.6, 2.2, 40)
    X, Y = np.meshgrid(gx, gx)
    K_sphere = K_from_func(
        lambda x, y: (np.ones_like(x), np.zeros_like(x), np.sin(x) ** 2), X, Y
    )
    err = float(np.median(np.abs(K_sphere - 1.0)))
    print(f"G0 sphere check: median |K - 1| = {err:.4f}  (gate < 0.01)")
    if err > 0.01:
        raise SystemExit("G0 failed — fix the curvature calculator first")

    # learned metric: rebuild Phase E model, query through torch
    model = fe.FieldModel()
    # retrain-free load: Phase E saved no weights — rerun guard
    ckpt = RESULTS / "16_field_model.pt"
    if not ckpt.exists():
        raise SystemExit("Phase E model weights not found — run step 16 with saving")
    model.net.load_state_dict(torch.load(ckpt, weights_only=True))
    model.eval()
    scale = json.loads((RESULTS / "16_field.json").read_text())["global_scale"]

    def learned_metric(x, y):
        q = torch.from_numpy(np.stack([x.ravel(), y.ravel()], 1).astype(np.float32))
        with torch.no_grad():
            B, C, D, _ = model.fields(q)
        return (scale * B.numpy().reshape(x.shape),
                scale * D.numpy().reshape(x.shape),
                scale * C.numpy().reshape(x.shape))

    def true_metric(x, y):
        A, B, C, D = fields_2p1(x, y)
        return B, D, C

    gx = np.linspace(XY_RANGE[0] + 0.3, XY_RANGE[1] - 0.3, 50)
    X, Y = np.meshgrid(gx, gx)
    K_hat = K_from_func(learned_metric, X, Y, h=5e-3)
    K_true = K_from_func(true_metric, X, Y)

    r = float(np.corrcoef(K_hat.ravel(), K_true.ravel())[0, 1])
    mag = float(np.median(np.abs(K_hat - K_true)) / (np.median(np.abs(K_true)) + 1e-12))
    far = (np.abs(X) > 1.9) & (np.abs(Y) > 1.9)  # grid ends at 2.2: corners only
    print(f"K1 corr(K_hat, K_true) = {r:.4f}  (gate > 0.95)")
    print(f"K2 median |K_hat - K_true| / median|K_true| = {mag:.3f}  (gate < 0.2 relative-ish)")
    print(f"K3 far-field: median |K_hat| = {np.median(np.abs(K_hat[far])):.4f}, "
          f"|K_true| = {np.median(np.abs(K_true[far])):.4f}")

    fig, axes = plt.subplots(1, 2, figsize=(12.5, 5))
    lim = np.percentile(np.abs(K_true), 99)
    for ax, K, ttl in ((axes[0], K_hat, "curvature of the LEARNED geometry"),
                       (axes[1], K_true, "curvature of the true world")):
        im = ax.contourf(X, Y, np.clip(K, -lim, lim), levels=18, cmap="RdBu_r",
                         vmin=-lim, vmax=lim)
        fig.colorbar(im, ax=ax)
        ax.set_title(ttl)
    fig.suptitle(f"Theorema Egregium, by autodiff: corr = {r:.3f}\n"
                 "(Gaussian curvature — the coordinate-free invariant — of a metric "
                 "learned from watching things move)")
    fig.tight_layout()
    out = RESULTS / "17_curvature_invariant.png"
    fig.savefig(out, dpi=140)
    print(f"plot -> {out}")
    (RESULTS / "17_curvature.json").write_text(
        json.dumps({"G0_sphere_err": err, "K1_corr": r, "K2_mag": mag}, indent=1)
    )


if __name__ == "__main__":
    main()
