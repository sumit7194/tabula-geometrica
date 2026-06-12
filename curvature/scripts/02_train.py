"""Step 02 — train the Siamese encoder on a same-event task.

One trainer for every task (the generator is the experiment; the model never
changes shape except input width):

  future      Phase A: future-timelike events, flat spacetime (the control)
  mixed       v0.1: all four causal sectors, flat spacetime
  well        Phase B: events at anchors inside a gravity well, observer
              position included in the input
  well-nopos  Phase B control: same data, position WITHHELD — its accuracy
              ceiling measures how much the geometry actually varies

Architecture decisions + reasons in ../README.md. K (--k) is the experiment's
dial: the width where accuracy saturates counts the world's invariants.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
import torch
from curvlib import (
    RESULTS,
    Siamese,
    sample_pairs,
    sample_pairs_3p1,
    sample_pairs_mixed,
    sample_pairs_well,
)
from torch import nn

TASKS = {
    # name -> (generator(n, rng), input width, hidden width)
    "future": (sample_pairs, 2, 64),
    "mixed": (sample_pairs_mixed, 2, 64),
    "flat3p1": (sample_pairs_3p1, 4, 64),
    "well": (lambda n, rng: sample_pairs_well(n, rng, with_position=True), 3, 128),
    "well-nopos": (lambda n, rng: sample_pairs_well(n, rng, with_position=False), 2, 128),
}


def stem_for(task: str, k: int) -> str:
    # Phase A keeps its original artifact names
    return f"model_k{k}" if task == "future" else f"model_{task}_k{k}"


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--task", choices=TASKS, default="future")
    p.add_argument("--k", type=int, default=1)
    p.add_argument("--steps", type=int, default=4000)
    p.add_argument("--seed", type=int, default=0)
    args = p.parse_args()

    gen, in_dim, hidden = TASKS[args.task]
    torch.manual_seed(args.seed)
    rng = np.random.default_rng(args.seed)
    model = Siamese(args.k, in_dim, hidden)
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)
    lossf = nn.BCEWithLogitsLoss()

    for step in range(args.steps):
        a, b, y = gen(512, rng)
        loss = lossf(model(torch.from_numpy(a), torch.from_numpy(b)), torch.from_numpy(y))
        opt.zero_grad()
        loss.backward()
        opt.step()
        if step % 500 == 0:
            from curvlib import progress

            progress(f"02_{args.task}_k{args.k}", step, args.steps, loss=loss.item())
            if step % 1000 == 0:
                print(f"step {step:5d}  loss {loss.item():.4f}")

    # fresh pairs from an unseen seed — accuracy is measured, never assumed
    a, b, y = gen(20_000, np.random.default_rng(10_000 + args.seed))
    with torch.no_grad():
        pred = model(torch.from_numpy(a), torch.from_numpy(b)) > 0
        acc = (pred.float() == torch.from_numpy(y)).float().mean().item()
    print(f"task={args.task} K={args.k}: test accuracy {acc:.4f}")

    RESULTS.mkdir(exist_ok=True)
    stem = stem_for(args.task, args.k)
    torch.save(model.state_dict(), RESULTS / f"{stem}.pt")
    (RESULTS / f"{stem}.json").write_text(
        json.dumps(
            {
                "task": args.task,
                "k": args.k,
                "in_dim": in_dim,
                "hidden": hidden,
                "steps": args.steps,
                "seed": args.seed,
                "test_accuracy": acc,
            }
        )
    )
    print(f"model -> {RESULTS / f'{stem}.pt'}")


if __name__ == "__main__":
    main()
