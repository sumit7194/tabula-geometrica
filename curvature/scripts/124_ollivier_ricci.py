"""Step 124 — graph Ollivier-Ricci curvature: curvature as the geometric signature of network structure.

Build-queue item 5 (notes/build_queue.md); a curvature-atlas row (after finance 88 / hierarchy 89 / neuroscience 90)
extending "curvature/holonomy is the universal signature of the cheapest shared description" BEYOND gravity, to
discrete networks. Web-verified (Ollivier 2009; Sia-Jonckheere-Bogdan / Ni-Lin-Gao-Saucan, Sci Rep 2019): the
Ollivier-Ricci curvature of an edge (x,y) is kappa = 1 - W1(m_x, m_y)/d(x,y), where m_x is a lazy-random-walk measure
and W1 the Wasserstein-1 (earth-mover) distance. In networks with community structure the curvature is BIMODAL:
intra-community edges are POSITIVELY curved (neighborhoods overlap) and inter-community BRIDGES are NEGATIVELY curved
(bottlenecks) -- so cutting the negative edges recovers the communities ("Ricci surgery").

Toy: a stochastic block model (planted communities). Compute ORC for every edge (W1 via a small optimal-transport LP,
cost = graph distances). Test the curvature signature.

Pre-reg (2026-06-25):
  O1 BIMODAL SIGNATURE: ORC separates intra- from inter-community edges -- intra mean > 0 > inter mean, and the
     ROC-AUC of (-ORC) predicting "is a bridge" > 0.85.
  O2 RICCI SURGERY RECOVERS COMMUNITIES: cutting the negatively-curved edges and taking connected components recovers
     the planted communities -- adjusted Rand index ARI > 0.7.
  O3 CONTROL (curvature carries the signal): random edge removal of the SAME count gives ARI ~ 0 (< 0.2); and an
     Erdos-Renyi graph (no communities) has NO bimodal separation (|intra-inter ORC gap| collapses).
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import networkx as nx
from scipy.optimize import linprog
from sklearn.metrics import adjusted_rand_score, roc_auc_score

from curvlib import RESULTS


def ot_w1(a, b, C):
    """Wasserstein-1 between measures a (on rows) and b (on cols) with cost C, via an optimal-transport LP."""
    n, m = C.shape
    A_eq = np.zeros((n + m, n * m))
    for i in range(n):
        A_eq[i, i * m:(i + 1) * m] = 1.0                          # row sums = a
    for j in range(m):
        A_eq[n + j, j::m] = 1.0                                   # col sums = b
    res = linprog(C.ravel(), A_eq=A_eq, b_eq=np.concatenate([a, b]), bounds=(0, None), method="highs")
    return float(res.fun)


def orc(G, dist, alpha=0.5):
    """Ollivier-Ricci curvature for every edge; lazy random walk (mass alpha stays, 1-alpha spreads to neighbors)."""
    kappa = {}
    for x, y in G.edges():
        nx_, ny_ = list(G.neighbors(x)), list(G.neighbors(y))
        Sx, Sy = [x] + nx_, [y] + ny_
        mx = np.array([alpha] + [(1 - alpha) / len(nx_)] * len(nx_))
        my = np.array([alpha] + [(1 - alpha) / len(ny_)] * len(ny_))
        C = np.array([[dist[a][b] for b in Sy] for a in Sx], float)
        kappa[(x, y)] = 1.0 - ot_w1(mx, my, C) / dist[x][y]
    return kappa


def components_partition(G, n):
    lab = np.full(n, -1)
    for c, comp in enumerate(nx.connected_components(G)):
        for v in comp:
            lab[v] = c
    return lab


def main():
    rng = np.random.default_rng(0)
    K, per = 3, 30; N = K * per
    sizes = [per] * K
    G = nx.stochastic_block_model(sizes, np.array([[0.35 if i == j else 0.03 for j in range(K)] for i in range(K)]),
                                  seed=7)
    G = G.subgraph(max(nx.connected_components(G), key=len)).copy()  # largest connected component
    G = nx.convert_node_labels_to_integers(G)
    truth = np.array([G.nodes[v]["block"] for v in G.nodes()])
    n = G.number_of_nodes()
    dist = dict(nx.all_pairs_shortest_path_length(G))

    kappa = orc(G, dist)
    edges = list(kappa)
    kvals = np.array([kappa[e] for e in edges])
    is_bridge = np.array([truth[x] != truth[y] for x, y in edges])

    # O1: bimodal separation
    intra_mean = float(kvals[~is_bridge].mean()); inter_mean = float(kvals[is_bridge].mean())
    auc = float(roc_auc_score(is_bridge, -kvals))                 # negative curvature -> bridge
    o1 = bool(intra_mean > 0 > inter_mean and auc > 0.85)

    # O2: Ricci surgery -- cut negatively-curved edges, connected components = communities
    Gs = G.copy()
    Gs.remove_edges_from([e for e in edges if kappa[e] < 0])
    pred = components_partition(Gs, n)
    ari = float(adjusted_rand_score(truth, pred))
    o2 = bool(ari > 0.7)

    # O3a: control -- remove the SAME number of RANDOM edges
    ncut = int((kvals < 0).sum())
    Gr = G.copy()
    ridx = rng.choice(len(edges), ncut, replace=False)
    Gr.remove_edges_from([edges[i] for i in ridx])
    ari_rand = float(adjusted_rand_score(truth, components_partition(Gr, n)))
    # O3b: ER control (no communities) -- bimodal gap should collapse
    Ger = nx.gnm_random_graph(n, G.number_of_edges(), seed=3)
    Ger = Ger.subgraph(max(nx.connected_components(Ger), key=len)).copy()
    Ger = nx.convert_node_labels_to_integers(Ger)
    der = dict(nx.all_pairs_shortest_path_length(Ger))
    ker = np.array(list(orc(Ger, der).values()))
    sbm_gap = intra_mean - inter_mean
    er_spread = float(ker.std())
    o3 = bool(ari_rand < 0.2 and sbm_gap > 3 * er_spread)

    out = {"O1_intra_mean": intra_mean, "O1_inter_mean": inter_mean, "O1_bridge_auc": auc,
           "O2_surgery_ari": ari, "O3_random_cut_ari": ari_rand, "O3_sbm_gap": float(sbm_gap),
           "O3_er_curvature_spread": er_spread, "n_negative_edges": int(ncut),
           "O1_bimodal_signature": o1, "O2_ricci_surgery_recovers": o2, "O3_curvature_carries_signal": o3,
           "ollivier_ricci_demonstrated": bool(o1 and o2 and o3),
           "verdict": ("OLLIVIER-RICCI CURVATURE = the geometric signature of network structure: on a planted-community "
                       "graph the edge curvature is BIMODAL -- intra-community edges positively curved (mean {:.2f}) and "
                       "inter-community BRIDGES negatively curved (mean {:.2f}), AUC {:.2f} for detecting bridges. "
                       "RICCI SURGERY (cutting the negative edges) recovers the communities (ARI {:.2f}) whereas random "
                       "edge removal of the same count gives ARI {:.2f}, and an Erdos-Renyi graph has no bimodal gap -- "
                       "the curvature carries the community signal. Curvature beyond gravity: the cheapest geometric "
                       "description of a discrete network's structure (curvature-atlas row)."
                       .format(intra_mean, inter_mean, auc, ari, ari_rand)
                       if (o1 and o2 and o3) else "PARTIAL -- see numbers (honest).")}
    print(f"O1 bimodal: intra ORC {intra_mean:.2f} > 0 > inter {inter_mean:.2f}, bridge AUC={auc:.2f} (>0.85): {o1}")
    print(f"O2 Ricci surgery recovers communities: ARI={ari:.2f} (>0.7): {o2}")
    print(f"O3 control: random-cut ARI={ari_rand:.2f} (<0.2), SBM gap {sbm_gap:.2f} > 3x ER spread {er_spread:.2f}: {o3}")
    print(f"\nOLLIVIER-RICCI CURVATURE DEMONSTRATED: {out['ollivier_ricci_demonstrated']}")
    (RESULTS / "124_ollivier_ricci.json").write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(1, 2, figsize=(12, 4.8))
    ax[0].hist(kvals[~is_bridge], bins=20, alpha=0.6, color="seagreen", label="intra-community")
    ax[0].hist(kvals[is_bridge], bins=20, alpha=0.6, color="crimson", label="inter (bridge)")
    ax[0].axvline(0, ls="--", c="k", lw=0.7); ax[0].set_xlabel("Ollivier-Ricci curvature κ"); ax[0].legend(fontsize=8)
    ax[0].set_title(f"O1 · bimodal: bridges negative (AUC {auc:.2f})")
    pos = nx.spring_layout(G, seed=1)
    nx.draw_networkx_nodes(G, pos, node_color=truth, cmap="tab10", node_size=40, ax=ax[1])
    ec = ["crimson" if kappa[e] < 0 else "lightgray" for e in edges]
    nx.draw_networkx_edges(G, pos, edgelist=edges, edge_color=ec, ax=ax[1], width=0.8)
    ax[1].set_title(f"O2 · negative-curvature edges (red) = bridges\nRicci surgery ARI={ari:.2f}"); ax[1].axis("off")
    fig.suptitle("Ollivier-Ricci curvature: the geometric signature of community structure (curvature beyond gravity)")
    fig.tight_layout(); fig.savefig(RESULTS / "124_ollivier_ricci.png", dpi=140)
    print("saved results/124_ollivier_ricci.json + .png")


if __name__ == "__main__":
    main()
