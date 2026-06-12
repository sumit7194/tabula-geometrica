"""Step 01 — generator honesty checks, run BEFORE training anything.

Two ways this experiment could silently lie to us, both tested here:

1. A shortcut. If same/different is solvable from cheap linear reads of the raw
   coordinates, the net can score high without learning any invariant. Gate: a
   logistic-regression baseline must sit near chance, while an oracle that
   compares true intervals shows the task is solvable in principle.
2. A class giveaway. If positive-pair and negative-pair observations have
   different coordinate distributions, "same?" leaks from single observations.
   Gate: the marginals must overlap (plotted for eyeballing, plus a
   single-observation logistic probe that must sit at chance).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from curvlib import RESULTS, interval2, sample_pairs
from sklearn.linear_model import LogisticRegression

N = 40_000


def main() -> None:
    rng = np.random.default_rng(1)
    a, b, y = sample_pairs(N, rng)

    # oracle: threshold on |s2_a - s2_b| — proves the task is solvable
    gap = np.abs(interval2(a) - interval2(b))
    thresholds = np.linspace(0.01, 1.0, 200)
    oracle_acc = max(
        ((gap < th) == (y == 1)).mean() for th in thresholds
    )

    # shortcut probe: linear model on raw pair coordinates
    X = np.concatenate([a, b], axis=1)
    n_tr = N // 2
    clf = LogisticRegression(max_iter=2000).fit(X[:n_tr], y[:n_tr])
    linear_acc = clf.score(X[n_tr:], y[n_tr:])

    # giveaway probe: can a single observation predict its pair's label?
    clf1 = LogisticRegression(max_iter=2000).fit(a[:n_tr], y[:n_tr])
    single_acc = clf1.score(a[n_tr:], y[n_tr:])

    print(f"oracle (true-interval comparison): {oracle_acc:.4f}  — should be ~1")
    print(f"linear shortcut on raw pairs:      {linear_acc:.4f}  — should be ~0.5")
    print(f"single-observation giveaway:       {single_acc:.4f}  — should be ~0.5")

    fig, axes = plt.subplots(1, 3, figsize=(14, 4))
    pos, neg = y == 1, y == 0
    axes[0].scatter(a[pos][:2000, 1], a[pos][:2000, 0], s=2, alpha=0.3, label="positive pairs")
    axes[0].scatter(a[neg][:2000, 1], a[neg][:2000, 0], s=2, alpha=0.3, label="negative pairs")
    axes[0].set_xlabel("x")
    axes[0].set_ylabel("t")
    axes[0].set_title("observation cloud by pair label\n(must be indistinguishable)")
    axes[0].legend(markerscale=4)

    axes[1].hist(interval2(a[pos]), bins=60, alpha=0.6, label="positive")
    axes[1].hist(interval2(a[neg]), bins=60, alpha=0.6, label="negative")
    axes[1].set_xlabel("s² of first observation")
    axes[1].set_title("invariant marginal by label\n(must overlap)")
    axes[1].legend()

    axes[2].hist(gap[pos], bins=60, alpha=0.6, label="positive")
    axes[2].hist(gap[neg], bins=60, alpha=0.6, label="negative")
    axes[2].set_xlabel("|s²_a − s²_b|")
    axes[2].set_title("THE separating variable\n(this is what must be learned)")
    axes[2].legend()

    RESULTS.mkdir(exist_ok=True)
    out = RESULTS / "01_sanity.png"
    fig.tight_layout()
    fig.savefig(out, dpi=140)
    print(f"plot -> {out}")


if __name__ == "__main__":
    main()
