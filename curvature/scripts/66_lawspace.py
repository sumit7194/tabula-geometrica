"""Step 66 — THE LAW-SPACE PRIZE: how does the generalist organize physical law in its code space?

The cross-pollination reason for the generalist. Where does it place gravity, EM (charged), scalar,
Schwarzschild, charged-BH (Reissner-Nordstrom), and quantum (Bloch) RELATIVE to each other? Is there a
meaningful taxonomy of law in there?

Honest design: the model is GIVEN the family id (fam embedding added in the encoder), so family-
separability is partly trivial; the meaningful question is the RELATIVE geometry — which families the
model placed CLOSE (shared structure). Two complementary reads:
  (1) the learned FAMILY EMBEDDINGS (model.fam.weight): the model's direct 6-point taxonomy of law.
  (2) the world-CODE centroids (mean inferred code per family): corroboration from the inference side.
Plus the honest ARI story (clustering vs classifiability; within-family spread from world-params).

Pre-reg expectations (2026-06-17):
  L1 the taxonomy is MEANINGFUL: schwarzschild <-> reissner_nordstrom are the CLOSEST pair (RN = Schw +
     charge), in BOTH the fam-embedding and code-centroid geometries.
  L2 MODALITY structure: the three modalities (trajectory {gravity,charged,scalar} / metric {schw,RN} /
     quantum {bloch}) are recoverable — within-modality distances < cross-modality (a clean separation).
  L3 the honest ARI: report KMeans ARI AND family-classification acc; show acc >> ARI (the law-space is
     structured/classifiable even where flat clustering looks weak — within-family world-param spread).
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
from importlib import import_module
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import adjusted_rand_score
from sklearn.model_selection import cross_val_score

import worldgen_v2 as wg
from curvlib import RESULTS, load_ckpt
g2 = import_module("61_generalist_v2")
DEV = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
NAMES = [f.name for f in wg.FAMILIES]
MODALITY = {"gravity": "traj", "charged": "traj", "scalar": "traj",
            "schwarzschild": "metric", "reissner_nordstrom": "metric", "bloch": "quantum"}


def codes_per_family(m, N=200, K=16):
    rng = np.random.default_rng(0); C, F = [], []
    for fid in range(wg.NFAM):
        cu = np.zeros((N, K, wg.DU), np.float32); cy = np.zeros((N, K, wg.DY), np.float32)
        for b in range(N):
            ep = wg.make_episode(rng, fid, K, 1); cu[b], cy[b] = ep["ctx_u"], ep["ctx_y"]
        with torch.no_grad():
            code = m.encode(torch.from_numpy(cu).to(DEV), torch.from_numpy(cy).to(DEV),
                            torch.full((N,), fid, dtype=torch.long).to(DEV)).cpu().numpy()
        C.append(code); F.append(np.full(N, fid))
    return np.concatenate(C), np.concatenate(F)


def rdm(vecs):
    v = vecs / (np.linalg.norm(vecs, axis=1, keepdims=True) + 1e-9)
    return 1 - v @ v.T                                    # cosine distance matrix


def closest_pair(D):
    n = D.shape[0]; best = (None, None, 9e9)
    for i in range(n):
        for j in range(i + 1, n):
            if D[i, j] < best[2]: best = (i, j, D[i, j])
    return NAMES[best[0]], NAMES[best[1]], float(best[2])


def main():
    m = g2.GeneralistV2().to(DEV); opt = torch.optim.Adam(m.parameters())
    step, *_ = load_ckpt(RESULTS / "61_gen2.pt", m, opt, fallback_seed=0); m.eval()
    print(f"loaded generalist @ step {step}\n")

    # (1) family-embedding taxonomy
    famemb = m.fam.weight.detach().cpu().numpy()
    Demb = rdm(famemb); ep_a, ep_b, ep_d = closest_pair(Demb)

    # (2) world-code centroids
    C, F = codes_per_family(m)
    cent = np.stack([C[F == k].mean(0) for k in range(wg.NFAM)])
    Dcode = rdm(cent); cp_a, cp_b, cp_d = closest_pair(Dcode)

    # L2 modality separation (on codes): mean within-modality vs cross-modality centroid distance
    mods = np.array([MODALITY[n] for n in NAMES])
    iu = [(i, j) for i in range(wg.NFAM) for j in range(i + 1, wg.NFAM)]
    within = np.mean([Dcode[i, j] for i, j in iu if mods[i] == mods[j]])
    cross = np.mean([Dcode[i, j] for i, j in iu if mods[i] != mods[j]])

    # L3 ARI vs classification
    ari = float(adjusted_rand_score(F, KMeans(wg.NFAM, n_init=10, random_state=0).fit(C).labels_))
    acc = float(np.mean(cross_val_score(LogisticRegression(max_iter=2000, C=1.0), C, F, cv=5)))

    l1 = bool({ep_a, ep_b} == {"schwarzschild", "reissner_nordstrom"} or {cp_a, cp_b} == {"schwarzschild", "reissner_nordstrom"})
    l2 = bool(within < cross - 0.05)
    l3 = bool(acc > 0.9)
    out = {"checkpoint_step": step,
           "fam_emb_closest_pair": [ep_a, ep_b, ep_d], "code_centroid_closest_pair": [cp_a, cp_b, cp_d],
           "modality_within_dist": float(within), "modality_cross_dist": float(cross),
           "ARI": ari, "family_classification_acc": acc,
           "L1_taxonomy_meaningful": l1, "L2_modality_structure": l2, "L3_ari_vs_classifiable": l3}
    print(f"L1 closest pair — fam-emb: {ep_a}<->{ep_b} (d={ep_d:.3f}); code-centroid: {cp_a}<->{cp_b} (d={cp_d:.3f})")
    print(f"   (Schwarzschild<->RN closest = RN is Schw+charge): {l1}")
    print(f"L2 modality structure: within-modality dist {within:.3f} < cross {cross:.3f}: {l2}")
    print(f"L3 ARI vs classifiable: KMeans ARI {ari:.3f}, family-classification acc {acc:.3f} (acc>>ARI = structured): {l3}")
    print(f"\n=== code-centroid distance matrix (cosine) ===")
    print("           " + " ".join(f"{n[:5]:>6}" for n in NAMES))
    for i, n in enumerate(NAMES):
        print(f"{n[:10]:>10} " + " ".join(f"{Dcode[i,j]:6.2f}" for j in range(wg.NFAM)))
    (RESULTS / "66_lawspace.json").write_text(json.dumps(out, indent=1))

    # PCA viz of codes
    P = PCA(2).fit_transform(C)
    fig, ax = plt.subplots(1, 2, figsize=(13, 5.2))
    cmap = {"traj": "seagreen", "metric": "crimson", "quantum": "navy"}
    for k, n in enumerate(NAMES):
        ax[0].scatter(P[F == k, 0], P[F == k, 1], s=8, alpha=0.5, color=cmap[MODALITY[n]], label=None)
        cx, cy = P[F == k].mean(0); ax[0].annotate(n, (cx, cy), fontsize=8, fontweight="bold")
    ax[0].set_title(f"law-space (PCA of world-codes), colored by modality\ntraj=green metric=red quantum=blue | ARI {ari:.2f}, classif acc {acc:.2f}")
    im = ax[1].imshow(Dcode, cmap="viridis"); fig.colorbar(im, ax=ax[1])
    ax[1].set_xticks(range(wg.NFAM)); ax[1].set_xticklabels([n[:5] for n in NAMES], rotation=45, fontsize=7)
    ax[1].set_yticks(range(wg.NFAM)); ax[1].set_yticklabels([n[:5] for n in NAMES], fontsize=7)
    ax[1].set_title("family-centroid distance matrix (the taxonomy of law)")
    fig.tight_layout(); fig.savefig(RESULTS / "66_lawspace.png", dpi=140)
    print("\nsaved results/66_lawspace.json + .png")


if __name__ == "__main__":
    main()
