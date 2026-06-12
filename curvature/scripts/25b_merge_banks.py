"""Step 25b — merge worldgen shard banks into one npz (+ merged meta).

Usage: 25b_merge_banks.py --out results/25_bank_48k.npz results/25_bank_s1.npz ...
Concatenates episodes across shards; family labels ride along per episode, so
downstream per-family splits keep working.
"""

import argparse
import json
from pathlib import Path

import numpy as np


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("shards", nargs="+")
    p.add_argument("--out", required=True)
    args = p.parse_args()

    parts = [dict(np.load(s)) for s in args.shards]
    meta = []
    for s in args.shards:
        meta += json.loads(Path(s).with_suffix(".meta.json").read_text())
    merged = {k: np.concatenate([p_[k] for p_ in parts]) for k in parts[0]}
    np.savez_compressed(args.out, **merged)
    Path(args.out).with_suffix(".meta.json").write_text(json.dumps(meta))
    print(f"merged {len(args.shards)} shards -> {args.out}: "
          f"{len(merged['family'])} episodes")


if __name__ == "__main__":
    main()
