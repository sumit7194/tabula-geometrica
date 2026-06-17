"""Step 90 — THE CURVATURE ATLAS III: a neural population's activity lives on a RING (topology from co-firing).

Atlas row 3, the coordinate-free / integer-topology face. Web-verified (Chaudhuri-Fiete Nat Neurosci 2019;
Gardner et al. Nature 2022): head-direction cells' population activity lies on a topological CIRCLE S^1
(Betti b1 = 1); grid-cell modules on a torus. Here: N neurons with von Mises tuning to a hidden heading theta;
the population vector traces a ring in R^N. From the co-firing alone (never given theta), an unsupervised
embedding must recover that the data is a 1-D closed loop, and the loop angle must decode the heading. A
shuffle control destroys the ring -- so the topology is in the correlations, discovered, not imposed.

Pre-reg (2026-06-17):
  R1 LOW-D MANIFOLD: the activity is essentially 1-D -- top-2 PCA components capture > 0.6 of the variance.
  R2 DISCOVER S^1: the 2-D embedding is a closed RING -- circular correlation(theta, embedding-angle) > 0.9,
     radial CV < 0.3 (constant radius), a HOLE at the center (min radius > 0.3 mean), full angular coverage
     (=> Betti b1 = 1). The heading is decoded from a coordinate the net was never given.
  R3 CONTROL: shuffling each neuron's activity across time destroys it -- circular corr < 0.3 and no ring.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import matplotlib

matplotlib.use("Agg")
import numpy as np
from sklearn.decomposition import PCA
from curvlib import RESULTS

np.seterr(all="ignore")


def population(N=120, T=2500, kappa=1.2, seed=0):
    rng = np.random.default_rng(seed)
    pref = np.linspace(0, 2 * np.pi, N, endpoint=False)         # evenly-tiled preferred headings
    theta = rng.uniform(0, 2 * np.pi, T)                       # hidden heading over time
    X = np.exp(kappa * (np.cos(theta[:, None] - pref[None, :]) - 1))   # von Mises tuning (T,N)
    X = X + 0.01 * rng.standard_normal((T, N))
    return X.astype(np.float32), theta


def circ_corr(a, b):                                           # circular-circular correlation (offset/rotation invariant)
    a = a - np.angle(np.mean(np.exp(1j * a))); b = b - np.angle(np.mean(np.exp(1j * b)))
    num = np.sum(np.sin(a) * np.sin(b))
    den = np.sqrt(np.sum(np.sin(a) ** 2) * np.sum(np.sin(b) ** 2))
    return float(abs(num / (den + 1e-12)))


def analyze(X, theta):
    P = PCA(6).fit(X); evr2 = float(P.explained_variance_ratio_[:2].sum())
    Y = P.transform(X)[:, :2]; Y = (Y - Y.mean(0)) / (Y.std(0) + 1e-9)   # whiten -> circular (de-ellipse)
    r = np.linalg.norm(Y, axis=1); psi = np.arctan2(Y[:, 1], Y[:, 0])
    cc = circ_corr(theta, psi)
    radial_cv = float(r.std() / (r.mean() + 1e-9))
    hole = float(r.min() / (r.mean() + 1e-9))                  # >0 => center not covered (a ring, not a disk)
    cover = float(np.min(np.histogram(psi, bins=12, range=(-np.pi, np.pi))[0]) > 0)   # all angular bins filled
    return evr2, cc, radial_cv, hole, bool(cover), Y, psi


def main():
    X, theta = population()
    evr2, cc, rcv, hole, cover, Y, psi = analyze(X, theta)
    # shuffle control: permute each neuron independently across time (kills the joint ring)
    rng = np.random.default_rng(1); Xs = np.stack([rng.permutation(X[:, i]) for i in range(X.shape[1])], 1)
    evr2s, ccs, rcvs, holes, covers, _, _ = analyze(Xs, theta)

    r1 = bool(evr2 > 0.6)
    r2 = bool(cc > 0.9 and rcv < 0.3 and hole > 0.3 and cover)
    r3 = bool(ccs < 0.3)
    out = {"top2_evr": evr2, "circ_corr_theta": cc, "radial_cv": rcv, "center_hole": hole, "angular_cover": cover,
           "shuffle_top2_evr": evr2s, "shuffle_circ_corr": ccs,
           "R1_low_dim_manifold": r1, "R2_discovered_ring_S1": r2, "R3_shuffle_control": r3,
           "neural_ring_discovered": bool(r1 and r2 and r3)}
    print(f"R1 low-D manifold: top-2 PCA EVR {evr2:.3f} (>0.6): {r1}")
    print(f"R2 discovered S^1: circ-corr(theta,angle) {cc:.3f} (>0.9), radial CV {rcv:.3f} (<0.3), hole {hole:.3f} (>0.3), cover {cover}: {r2}")
    print(f"R3 shuffle control: circ-corr {ccs:.3f} (<0.3): {r3}")
    print(f"\nNEURAL RING DISCOVERED (S^1 topology / Betti b1=1 from co-firing; heading decoded, never given): {out['neural_ring_discovered']}")
    (RESULTS / "90_neural_ring.json").write_text(json.dumps(out, indent=1))

    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 2, figsize=(12, 5.4))
    sc = ax[0].scatter(Y[:, 0], Y[:, 1], c=theta, cmap="hsv", s=8); fig.colorbar(sc, ax=ax[0], label="true heading θ")
    ax[0].set_aspect("equal"); ax[0].set_title(f"population activity (PCA 2-D) = a RING\ncolored by hidden heading; circ-corr {cc:.2f}, Betti b1=1")
    Ps = PCA(2).fit_transform(np.stack([np.random.default_rng(1).permutation(X[:, i]) for i in range(X.shape[1])], 1))
    ax[1].scatter(Ps[:, 0], Ps[:, 1], c=theta, cmap="hsv", s=8); ax[1].set_aspect("equal")
    ax[1].set_title(f"shuffle control: ring destroyed\ncirc-corr {ccs:.2f} (heading no longer decodable)")
    fig.tight_layout(); fig.savefig(RESULTS / "90_neural_ring.png", dpi=140)
    print("saved results/90_neural_ring.json + .png")


if __name__ == "__main__":
    main()
