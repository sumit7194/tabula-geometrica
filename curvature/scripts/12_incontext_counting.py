"""Step 12 — in-context form counting: the corrected N1.

Random Lorentzian forms per episode (no position anywhere in this world). The
network infers the geometry from k = 8 context same-event pairs via a DeepSets
set-encoder whose output code has width d — the bottleneck must carry the FORM.
Sweep d; the accuracy knee should land at the family's true 3 dof, where the
address-bottleneck version (step 11) was capped at 2 by the base dimension.
Pre-registration F1-F4 in the lab notebook.
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
K_CTX = 8
STEPS = 12000


class InContextSiamese(nn.Module):
    def __init__(self, d: int):
        super().__init__()
        self.item = nn.Sequential(
            nn.Linear(6, 64), nn.Tanh(), nn.Linear(64, 64), nn.Tanh()
        )
        self.head = nn.Sequential(nn.Linear(64, 64), nn.Tanh(), nn.Linear(64, d))
        self.inv = nn.Sequential(
            nn.Linear(3 + d, 128), nn.Tanh(), nn.Linear(128, 128), nn.Tanh(),
            nn.Linear(128, 1),
        )
        self.alpha = nn.Parameter(torch.tensor(1.0))
        self.beta = nn.Parameter(torch.tensor(1.0))

    def code(self, ctx):
        return self.head(self.item(ctx).mean(dim=1))

    def forward(self, ctx, qa, qb):
        m = self.code(ctx)
        za = self.inv(torch.cat([qa, m], dim=1))[:, 0]
        zb = self.inv(torch.cat([qb, m], dim=1))[:, 0]
        return self.alpha - nn.functional.softplus(self.beta) * torch.abs(za - zb)


def train_one(d: int, seed: int = 0):
    torch.manual_seed(3000 + d)
    rng = np.random.default_rng(seed)
    model = InContextSiamese(d)
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)
    lossf = nn.BCEWithLogitsLoss()
    for step in range(STEPS):
        ctx, qa, qb, y = sample_episodes(256, K_CTX, rng)
        logit = model(torch.from_numpy(ctx), torch.from_numpy(qa), torch.from_numpy(qb))
        loss = lossf(logit, torch.from_numpy(y))
        opt.zero_grad()
        loss.backward()
        opt.step()
    ctx, qa, qb, y = sample_episodes(20_000, K_CTX, np.random.default_rng(10_000 + seed))
    with torch.no_grad():
        acc = float(
            ((model(torch.from_numpy(ctx), torch.from_numpy(qa), torch.from_numpy(qb)) > 0)
             .float() == torch.from_numpy(y)).float().mean()
        )
    return acc


def main() -> None:
    accs = {}
    for d in DIMS:
        accs[d] = train_one(d)
        print(f"d={d}: test accuracy {accs[d]:.4f}")

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(DIMS, [accs[d] for d in DIMS], "o-", color="darkslategray",
            label="form bottleneck (this step)")
    addr = json.loads((RESULTS / "11_metric_components.json").read_text())["accuracy_vs_d"]
    ds11 = sorted(int(k) for k in addr)
    ax.plot(ds11, [addr[str(k)] for k in ds11], "s--", color="gray", alpha=0.7,
            label="address bottleneck (step 11)")
    ax.axvline(3, color="crimson", ls="--", lw=1, label="form dof = 3")
    ax.axvline(2, color="gray", ls=":", lw=1, label="base dim = 2")
    ax.set_xlabel("code width d")
    ax.set_ylabel("test accuracy")
    ax.set_title("counting geometry the right way:\n"
                 "bottleneck the FORM (in-context) vs bottleneck the ADDRESS")
    ax.legend()
    fig.tight_layout()
    out = RESULTS / "12_incontext_counting.png"
    fig.savefig(out, dpi=140)
    print(f"plot -> {out}")

    (RESULTS / "12_incontext_counting.json").write_text(
        json.dumps({"k_ctx": K_CTX, "accuracy_vs_d": {str(d): accs[d] for d in DIMS}},
                   indent=1)
    )


if __name__ == "__main__":
    main()
