"""Step 12c — in-context form counting with the quadratic-feature context
encoder (bias declared: quadraticness supplied, the metric still inferred).

Context pairs enter as u = vec(a aᵀ) − vec(b bᵀ) ∈ R^6, making the same-event
constraint u·g = 0 linear in the form; the set encoder pools learned features
of the u's and must compress the inferred form through a code of width d.
Queries remain raw (dt, dx, dy). Pre-registration G1-G3 in the lab notebook.
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
from curvlib import RESULTS, sample_episodes
from torch import nn

DIMS = (1, 2, 3, 4, 6)
K_CTX = 32
STEPS = 12000

# symmetric-matrix vectorization indices for the 3-vector observations
IDX = [(0, 0), (0, 1), (0, 2), (1, 1), (1, 2), (2, 2)]


def monomial_diff(ctx: torch.Tensor) -> torch.Tensor:
    a, b = ctx[..., :3], ctx[..., 3:]
    feats = []
    for i, j in IDX:
        feats.append(a[..., i] * a[..., j] - b[..., i] * b[..., j])
    return torch.stack(feats, dim=-1)


class QuadInContextSiamese(nn.Module):
    def __init__(self, d: int):
        super().__init__()
        self.item = nn.Sequential(
            nn.Linear(6, 128), nn.Tanh(), nn.Linear(128, 128), nn.Tanh()
        )
        self.head = nn.Sequential(nn.Linear(128, 128), nn.Tanh(), nn.Linear(128, d))
        self.inv = nn.Sequential(
            nn.Linear(3 + d, 128), nn.Tanh(), nn.Linear(128, 128), nn.Tanh(),
            nn.Linear(128, 1),
        )
        self.alpha = nn.Parameter(torch.tensor(1.0))
        self.beta = nn.Parameter(torch.tensor(1.0))

    def code(self, ctx):
        return self.head(self.item(monomial_diff(ctx)).mean(dim=1))

    def forward(self, ctx, qa, qb):
        m = self.code(ctx)
        za = self.inv(torch.cat([qa, m], dim=1))[:, 0]
        zb = self.inv(torch.cat([qb, m], dim=1))[:, 0]
        return self.alpha - nn.functional.softplus(self.beta) * torch.abs(za - zb)


def train_one(d: int, seed: int = 0) -> float:
    torch.manual_seed(6000 + d)
    rng = np.random.default_rng(seed)
    model = QuadInContextSiamese(d)
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)
    lossf = nn.BCEWithLogitsLoss()
    for _ in range(STEPS):
        ctx, qa, qb, y = sample_episodes(256, K_CTX, rng)
        loss = lossf(
            model(torch.from_numpy(ctx), torch.from_numpy(qa), torch.from_numpy(qb)),
            torch.from_numpy(y),
        )
        opt.zero_grad()
        loss.backward()
        opt.step()
    ctx, qa, qb, y = sample_episodes(20_000, K_CTX, np.random.default_rng(10_000 + seed))
    with torch.no_grad():
        return float(
            ((model(torch.from_numpy(ctx), torch.from_numpy(qa), torch.from_numpy(qb)) > 0)
             .float() == torch.from_numpy(y)).float().mean()
        )


def main() -> None:
    accs = {}
    for d in DIMS:
        accs[d] = train_one(d)
        print(f"d={d}: test accuracy {accs[d]:.4f}")

    flat = json.loads((RESULTS / "12_incontext_counting.json").read_text())["accuracy_vs_d"]
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(DIMS, [accs[d] for d in DIMS], "o-", color="darkslategray",
            label="quadratic-feature context (12c, k=32)")
    ds = sorted(int(x) for x in flat)
    ax.plot(ds, [flat[str(x)] for x in ds], "s--", color="gray", alpha=0.7,
            label="raw mean-pool context (12, k=8)")
    ax.axhline(0.992, color="seagreen", ls=":", lw=1.2, label="oracle (true form)")
    ax.axvline(3, color="crimson", ls="--", lw=1, label="form dof = 3")
    ax.set_xlabel("code width d")
    ax.set_ylabel("test accuracy")
    ax.set_title("counting the form's degrees of freedom (in-context)")
    ax.legend()
    fig.tight_layout()
    out = RESULTS / "12c_counting_quadfeat.png"
    fig.savefig(out, dpi=140)
    print(f"plot -> {out}")

    (RESULTS / "12c_counting_quadfeat.json").write_text(
        json.dumps({"k_ctx": K_CTX, "accuracy_vs_d": {str(d): accs[d] for d in DIMS}},
                   indent=1)
    )


if __name__ == "__main__":
    main()
