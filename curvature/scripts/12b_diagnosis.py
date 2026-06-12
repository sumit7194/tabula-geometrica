"""Step 12b — diagnose the flat in-context counting curve (root cause first).

Fork: (H-noise) form-estimation noise from k context pairs caps accuracy →
accuracy rises with k. (H-opt) set-encoder/training bottleneck → oracle code
(true form fed directly) restores high accuracy while k barely matters.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
import torch
from curvlib import NEG_MARGIN, RAPIDITY_MAX, RESULTS, TAU_RANGE, _form_obs, sample_episodes, sample_forms
from torch import nn

STEPS = 12000


class OracleSiamese(nn.Module):
    """Invariant net with the TRUE (scale-normalized) form as the code."""

    def __init__(self):
        super().__init__()
        self.inv = nn.Sequential(
            nn.Linear(3 + 3, 128), nn.Tanh(), nn.Linear(128, 128), nn.Tanh(),
            nn.Linear(128, 1),
        )
        self.alpha = nn.Parameter(torch.tensor(1.0))
        self.beta = nn.Parameter(torch.tensor(1.0))

    def forward(self, code, qa, qb):
        za = self.inv(torch.cat([qa, code], dim=1))[:, 0]
        zb = self.inv(torch.cat([qb, code], dim=1))[:, 0]
        return self.alpha - nn.functional.softplus(self.beta) * torch.abs(za - zb)


def sample_oracle_episodes(n_ep, rng):
    A, B, C, D = sample_forms(n_ep, rng)
    code = np.stack([B / A, C / A, D / A], axis=1)  # the form, scale-free

    def obs(tau):
        return _form_obs(
            A, B, C, D, tau,
            rng.uniform(-RAPIDITY_MAX, RAPIDITY_MAX, n_ep),
            rng.uniform(0, 2 * np.pi, n_ep),
            rng,
        )

    tau1 = rng.uniform(*TAU_RANGE, n_ep)
    tau2 = rng.uniform(*TAU_RANGE, n_ep)
    bad = np.abs(tau2 - tau1) < NEG_MARGIN
    while bad.any():
        tau2[bad] = rng.uniform(*TAU_RANGE, int(bad.sum()))
        bad = np.abs(tau2 - tau1) < NEG_MARGIN
    label = rng.integers(0, 2, n_ep)
    tau_b = np.where(label == 1, tau1, tau2)
    return (
        code.astype(np.float32),
        obs(tau1).astype(np.float32),
        obs(tau_b).astype(np.float32),
        label.astype(np.float32),
    )


def train_oracle(seed=0):
    torch.manual_seed(4000)
    rng = np.random.default_rng(seed)
    model = OracleSiamese()
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)
    lossf = nn.BCEWithLogitsLoss()
    for _ in range(STEPS):
        code, qa, qb, y = sample_oracle_episodes(512, rng)
        loss = lossf(
            model(torch.from_numpy(code), torch.from_numpy(qa), torch.from_numpy(qb)),
            torch.from_numpy(y),
        )
        opt.zero_grad()
        loss.backward()
        opt.step()
    code, qa, qb, y = sample_oracle_episodes(20_000, np.random.default_rng(10_000))
    with torch.no_grad():
        return float(
            ((model(torch.from_numpy(code), torch.from_numpy(qa), torch.from_numpy(qb)) > 0)
             .float() == torch.from_numpy(y)).float().mean()
        )


def train_k(k, d=3, seed=0):
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "ic", Path(__file__).resolve().parent / "12_incontext_counting.py"
    )
    ic = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ic)
    torch.manual_seed(3000 + d)
    rng = np.random.default_rng(seed)
    model = ic.InContextSiamese(d)
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)
    lossf = nn.BCEWithLogitsLoss()
    for _ in range(STEPS):
        ctx, qa, qb, y = sample_episodes(256, k, rng)
        loss = lossf(
            model(torch.from_numpy(ctx), torch.from_numpy(qa), torch.from_numpy(qb)),
            torch.from_numpy(y),
        )
        opt.zero_grad()
        loss.backward()
        opt.step()
    ctx, qa, qb, y = sample_episodes(20_000, k, np.random.default_rng(10_000))
    with torch.no_grad():
        return float(
            ((model(torch.from_numpy(ctx), torch.from_numpy(qa), torch.from_numpy(qb)) > 0)
             .float() == torch.from_numpy(y)).float().mean()
        )


def main() -> None:
    out = {"oracle": train_oracle()}
    print(f"oracle code (true form, no estimation): {out['oracle']:.4f}")
    for k in (32, 128):
        out[f"k{k}_d3"] = train_k(k)
        print(f"k={k}, d=3: {out[f'k{k}_d3']:.4f}")
    (RESULTS / "12b_diagnosis.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
