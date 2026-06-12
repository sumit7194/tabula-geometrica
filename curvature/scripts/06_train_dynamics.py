"""Step 06 — Phase C trainers: geometry vs force, same data, same budget.

Two rival explanations of free-fall, as architectures:

  geometry  MLP(x0, v0) -> positions. ONE shared rule for every body — body
            identity is architecturally impossible to use. This is "motion is
            a property of the arena."
  force     MLP(x0, v0, embedding[body]) -> positions, with a learned 4-d
            embedding per body. This is "motion depends on what the body is."

Both first run the geodesic_check: the Newtonian-limit generator must agree
with the FULL relativistic geodesics of the Phase B metric (printed, recorded).

Usage: 06_train_dynamics.py --mix neutral|charged
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
import torch
from curvlib import RESULTS, geodesic_check, make_dynamics_dataset
from torch import nn

EMB_DIM = 4


class GeometryModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(2, 128), nn.Tanh(), nn.Linear(128, 128), nn.Tanh(), nn.Linear(128, 3)
        )

    def forward(self, x, body=None):
        return self.net(x)


class ForceModel(nn.Module):
    def __init__(self, n_bodies: int, emb_dim: int = EMB_DIM):
        super().__init__()
        self.emb = nn.Embedding(n_bodies, emb_dim)
        self.net = nn.Sequential(
            nn.Linear(2 + emb_dim, 128), nn.Tanh(), nn.Linear(128, 128), nn.Tanh(),
            nn.Linear(128, 3),
        )

    def forward(self, x, body):
        return self.net(torch.cat([x, self.emb(body)], dim=1))


def train(model, data, steps, seed, run_name="dynamics"):
    torch.manual_seed(seed)
    rng = np.random.default_rng(seed)
    body, X, Y = data["train"]
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)
    for step in range(steps):
        idx = rng.integers(0, len(X), 512)
        pred = model(torch.from_numpy(X[idx]), torch.from_numpy(body[idx]))
        loss = nn.functional.mse_loss(pred, torch.from_numpy(Y[idx]))
        opt.zero_grad()
        loss.backward()
        opt.step()
        if step % 500 == 0:
            from curvlib import progress

            progress(run_name, step, steps, loss=loss.item())
            if step % 2000 == 0:
                print(f"  step {step:5d}  mse {loss.item():.6f}")
    return model


def mse_on(model, split):
    body, X, Y = split
    with torch.no_grad():
        pred = model(torch.from_numpy(X), torch.from_numpy(body))
        return float(nn.functional.mse_loss(pred, torch.from_numpy(Y)).item())


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--mix", choices=("neutral", "charged"), default="neutral")
    p.add_argument("--steps", type=int, default=8000)
    p.add_argument("--seed", type=int, default=0)
    args = p.parse_args()

    gap = geodesic_check()
    print(f"generator check: max |Newtonian − full geodesic| = {gap:.5f}  (slow-motion regime)")

    data = make_dynamics_dataset(args.mix, seed=args.seed)
    n_bodies = len(data["qm_body"])

    # seed BEFORE construction: torch's default generator is process-random,
    # so unseeded init made runs irreproducible (caught in step 10)
    print("training geometry model (no body identity possible):")
    torch.manual_seed(args.seed)
    geo = train(GeometryModel(), data, args.steps, args.seed)
    print("training force model (per-body embedding):")
    torch.manual_seed(args.seed + 1)
    frc = train(ForceModel(n_bodies), data, args.steps, args.seed)

    meta = {
        "mix": args.mix,
        "steps": args.steps,
        "seed": args.seed,
        "geodesic_check": gap,
        "qm_body": data["qm_body"].tolist(),
        "held_bodies": data["held_bodies"].tolist(),
        "test_mse": {"geometry": mse_on(geo, data["test"]), "force": mse_on(frc, data["test"])},
        "held_mse_geometry_zero_shot": mse_on(geo, data["held"]),
    }
    print(json.dumps(meta["test_mse"], indent=1))
    print(f"geometry zero-shot on held-out bodies: {meta['held_mse_geometry_zero_shot']:.6f}")

    RESULTS.mkdir(exist_ok=True)
    torch.save(geo.state_dict(), RESULTS / f"dyn_{args.mix}_geometry.pt")
    torch.save(frc.state_dict(), RESULTS / f"dyn_{args.mix}_force.pt")
    (RESULTS / f"dyn_{args.mix}.json").write_text(json.dumps(meta, indent=1))
    print(f"models -> {RESULTS}/dyn_{args.mix}_*.pt")


if __name__ == "__main__":
    main()
