"""Step 12d — the decisive encoder diagnostic: pool the sufficient statistic.

Peer-suggested fix (second-opinion session): the constraints u·g = 0 have
empirical second-moment matrix Σ uuᵀ as their sufficient statistic — its null
eigenvector IS the form. So pool vec(uuᵀ) ∈ R²¹ explicitly (no learned item
map at all) and give the head the exact statistic. If accuracy still misses the
oracle, the failure is in the code/readout, not the encoder. Stopping rule and
pre-registration (H1, H2) in the lab notebook.
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

DIMS = (2, 3, 4, 6)
K_CTX = 32
STEPS = 12000

IDX = [(0, 0), (0, 1), (0, 2), (1, 1), (1, 2), (2, 2)]
TRIU = [(i, j) for i in range(6) for j in range(i, 6)]  # 21 entries


def suff_stat(ctx: torch.Tensor) -> torch.Tensor:
    a, b = ctx[..., :3], ctx[..., 3:]
    u = torch.stack([a[..., i] * a[..., j] - b[..., i] * b[..., j] for i, j in IDX], dim=-1)
    uu = torch.stack([u[..., i] * u[..., j] for i, j in TRIU], dim=-1)
    return uu.mean(dim=1)  # (E, 21): the empirical second-moment matrix


class SuffStatSiamese(nn.Module):
    def __init__(self, d: int):
        super().__init__()
        self.head = nn.Sequential(
            nn.Linear(21, 128), nn.Tanh(), nn.Linear(128, 128), nn.Tanh(),
            nn.Linear(128, d),
        )
        self.inv = nn.Sequential(
            nn.Linear(3 + d, 128), nn.Tanh(), nn.Linear(128, 128), nn.Tanh(),
            nn.Linear(128, 1),
        )
        self.alpha = nn.Parameter(torch.tensor(1.0))
        self.beta = nn.Parameter(torch.tensor(1.0))

    def forward(self, ctx, qa, qb):
        m = self.head(suff_stat(ctx))
        za = self.inv(torch.cat([qa, m], dim=1))[:, 0]
        zb = self.inv(torch.cat([qb, m], dim=1))[:, 0]
        return self.alpha - nn.functional.softplus(self.beta) * torch.abs(za - zb)


def train_one(d: int, seed: int = 0) -> float:
    torch.manual_seed(7000 + d)
    rng = np.random.default_rng(seed)
    model = SuffStatSiamese(d)
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

    prev = json.loads((RESULTS / "12c_counting_quadfeat.json").read_text())["accuracy_vs_d"]
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(DIMS, [accs[d] for d in DIMS], "o-", color="darkslategray",
            label="sufficient-statistic pool (12d)")
    ds = sorted(int(x) for x in prev)
    ax.plot(ds, [prev[str(x)] for x in ds], "s--", color="gray", alpha=0.7,
            label="learned quad-feature pool (12c)")
    ax.axhline(0.992, color="seagreen", ls=":", lw=1.2, label="oracle (true form)")
    ax.axvline(3, color="crimson", ls="--", lw=1, label="form dof = 3 (projective)")
    ax.set_xlabel("code width d")
    ax.set_ylabel("test accuracy")
    ax.set_title("the decisive encoder diagnostic:\npooling the exact sufficient statistic")
    ax.legend()
    fig.tight_layout()
    out = RESULTS / "12d_counting_suffstat.png"
    fig.savefig(out, dpi=140)
    print(f"plot -> {out}")

    (RESULTS / "12d_counting_suffstat.json").write_text(
        json.dumps({"k_ctx": K_CTX, "accuracy_vs_d": {str(d): accs[d] for d in DIMS}},
                   indent=1)
    )


if __name__ == "__main__":
    main()
