"""Step 11 — discover the NUMBER of metric components (2+1 anisotropic well).

Position information reaches the encoder ONLY through a learned per-point code
m(p) of width d. The local geometry (A:B:C:D up to per-anchor reshaping) truly
carries 3 numbers per point, so the accuracy-vs-d curve should be deficient for
d <= 2 and saturate at d = 3: the network discovers how many numbers per point
its world's geometry needs. Gates N1-N4 pre-registered in the lab notebook.
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
    RAPIDITY_MAX,
    RESULTS,
    TAU_RANGE,
    XY_RANGE,
    _well2p1_obs,
    sample_pairs_well2p1,
    true_G,
    well2p1_invariant,
)
from sklearn.isotonic import IsotonicRegression
from torch import nn

DIMS = (0, 1, 2, 3, 4, 6)
STEPS = 12000


class CodedSiamese(nn.Module):
    """Encoder f(Δ; m(p)) — position only ever enters through the d-wide code."""

    def __init__(self, d: int):
        super().__init__()
        self.d = d
        if d > 0:
            self.pos = nn.Sequential(
                nn.Linear(2, 64), nn.Tanh(), nn.Linear(64, 64), nn.Tanh(), nn.Linear(64, d)
            )
        self.inv = nn.Sequential(
            nn.Linear(3 + d, 128), nn.Tanh(), nn.Linear(128, 128), nn.Tanh(), nn.Linear(128, 1)
        )
        self.alpha = nn.Parameter(torch.tensor(1.0))
        self.beta = nn.Parameter(torch.tensor(1.0))

    def encode(self, obs):
        delta = obs[:, 2:]
        if self.d > 0:
            return self.inv(torch.cat([delta, self.pos(obs[:, :2])], dim=1))[:, 0]
        return self.inv(delta)[:, 0]

    def forward(self, a, b):
        dist = torch.abs(self.encode(a) - self.encode(b))
        return self.alpha - nn.functional.softplus(self.beta) * dist


def train_one(d: int, seed: int = 0):
    torch.manual_seed(2000 + d)
    rng = np.random.default_rng(seed)
    model = CodedSiamese(d)
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)
    lossf = nn.BCEWithLogitsLoss()
    for step in range(STEPS):
        a, b, y = sample_pairs_well2p1(512, rng)
        loss = lossf(model(torch.from_numpy(a), torch.from_numpy(b)), torch.from_numpy(y))
        opt.zero_grad()
        loss.backward()
        opt.step()
    a, b, y = sample_pairs_well2p1(20_000, np.random.default_rng(10_000 + seed))
    with torch.no_grad():
        acc = float(
            ((model(torch.from_numpy(a), torch.from_numpy(b)) > 0).float()
             == torch.from_numpy(y)).float().mean()
        )
    return model, acc


def anchored_observations(n_anchor: int, per: int, rng):
    """`per` observations at each of `n_anchor` shared anchors (for per-anchor
    gates: the reshaping freedom is per-anchor, so probes must be too)."""
    xp = np.repeat(rng.uniform(*XY_RANGE, n_anchor), per)
    yp = np.repeat(rng.uniform(*XY_RANGE, n_anchor), per)
    tau = rng.uniform(*TAU_RANGE, n_anchor * per)
    d = _well2p1_obs(
        xp, yp, tau,
        rng.uniform(-RAPIDITY_MAX, RAPIDITY_MAX, n_anchor * per),
        rng.uniform(0, 2 * np.pi, n_anchor * per),
        rng,
    )
    obs = np.concatenate([np.stack([xp, yp], axis=1), d], axis=1).astype(np.float32)
    return obs


def recover_G(deltas: np.ndarray, grads: np.ndarray) -> np.ndarray:
    """Least-squares symmetric G (up to scale) from G·Δ_i ∥ ∇f_i constraints
    (cross products vanish). Unknowns g = (g00,g01,g02,g11,g12,g22)."""
    rows = []
    for dlt, v in zip(deltas, grads):
        v = v / (np.linalg.norm(v) + 1e-12)
        d0, d1, d2 = dlt

        def gd(coef):  # (G·Δ) components as linear functions of g
            return np.array(coef)

        GD = [
            gd([d0, d1, d2, 0, 0, 0]),
            gd([0, d0, 0, d1, d2, 0]),
            gd([0, 0, d0, 0, d1, d2]),
        ]
        rows.append(GD[1] * v[2] - GD[2] * v[1])
        rows.append(GD[2] * v[0] - GD[0] * v[2])
        rows.append(GD[0] * v[1] - GD[1] * v[0])
    _, _, vt = np.linalg.svd(np.array(rows))
    return vt[-1]


def g_vec_true(x, y):
    G = true_G(np.array(x), np.array(y))
    return np.array([G[0, 0], G[0, 1], G[0, 2], G[1, 1], G[1, 2], G[2, 2]])


def main() -> None:
    results = {}
    models = {}
    for d in DIMS:
        model, acc = train_one(d)
        models[d] = model
        results[d] = {"accuracy": acc}
        print(f"d={d}: test accuracy {acc:.4f}")

    # N2 + N3 on the best saturated model (d = 4: safely past the predicted knee)
    probe = models[4]
    rng = np.random.default_rng(99)
    n_anchor, per = 200, 30
    obs_np = anchored_observations(n_anchor, per, rng)
    obs = torch.from_numpy(obs_np).requires_grad_(True)
    z = probe.encode(obs)
    (g,) = torch.autograd.grad(z.sum(), obs)
    g_delta = g.detach().numpy()[:, 2:]
    z = z.detach().numpy()
    inv_true = well2p1_invariant(obs_np[:, :2], obs_np[:, 2:])

    r2s, cosines = [], []
    for i in range(n_anchor):
        s = slice(i * per, (i + 1) * per)
        iso = IsotonicRegression(increasing="auto").fit(inv_true[s], z[s])
        pred = iso.predict(inv_true[s])
        denom = np.sum((z[s] - z[s].mean()) ** 2)
        if denom > 1e-12:
            r2s.append(1 - np.sum((z[s] - pred) ** 2) / denom)
        ghat = recover_G(obs_np[s, 2:], g_delta[s])
        gtru = g_vec_true(obs_np[i * per, 0], obs_np[i * per, 1])
        c = abs(np.dot(ghat, gtru) / (np.linalg.norm(ghat) * np.linalg.norm(gtru)))
        cosines.append(c)

    n2 = float(np.median(r2s))
    n3 = float(np.median(cosines))
    print(f"N2 per-anchor isotonic R² (median over {n_anchor} anchors): {n2:.4f}")
    print(f"N3 local-form recovery |cos(Ĝ, G_true)| (median): {n3:.4f}")

    accs = [results[d]["accuracy"] for d in DIMS]
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    axes[0].plot(DIMS, accs, "o-", color="darkslategray")
    axes[0].axvline(3, color="crimson", ls="--", lw=1, label="true count = 3")
    axes[0].set_xlabel("per-point geometry code width d")
    axes[0].set_ylabel("test accuracy")
    axes[0].set_title("counting the metric components:\naccuracy vs how many numbers per point the net may keep")
    axes[0].legend()

    axes[1].hist(cosines, bins=30, color="lightsteelblue", edgecolor="white")
    axes[1].axvline(n3, color="crimson", lw=2, label=f"median {n3:.3f}")
    axes[1].set_xlabel("|cos(recovered local form, true local form)|")
    axes[1].set_title("N3: the local metric, read out anchor by anchor (d=4 model)")
    axes[1].legend()
    fig.tight_layout()
    out = RESULTS / "11_metric_components.png"
    fig.savefig(out, dpi=140)
    print(f"plot -> {out}")

    (RESULTS / "11_metric_components.json").write_text(
        json.dumps({"accuracy_vs_d": {str(d): results[d]["accuracy"] for d in DIMS},
                    "N2_median_r2": n2, "N3_median_cos": n3}, indent=1)
    )


if __name__ == "__main__":
    main()
