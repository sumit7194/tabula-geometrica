"""Step 37 — Edge (b): the Platonic test. Do INDEPENDENT generalists converge to the same
internal map of physical law?

Train K compact generalists (different seeds AND sizes) on the same bank, then compare their
world-summary spaces with linear CKA + cluster-structure agreement (ARI), against an
untrained-init baseline. If independent nets build the same map, that's a 'platonic'
representation of physics (Huh et al. 2024), not a one-run artifact. Pre-reg 2026-06-15.
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
from curvlib import RESULTS, progress
from importlib import import_module
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score
from torch import nn

g26 = import_module("26_generalist")
SUMMARY = 64
CONFIGS = [(96, 3, 1), (96, 3, 2), (160, 4, 3), (128, 3, 4)]  # (width, layers, seed)
STEPS = 40000


class SmallGen(nn.Module):
    def __init__(self, d, layers, heads=4):
        super().__init__()
        self.embed = nn.Linear(18, d)
        enc = nn.TransformerEncoderLayer(d, heads, 3 * d, batch_first=True, dropout=0.0, norm_first=True)
        self.encoder = nn.TransformerEncoder(enc, layers)
        self.to_summary = nn.Linear(d, SUMMARY)
        self.q_embed = nn.Linear(14, d)
        self.head = nn.Sequential(nn.Linear(d + SUMMARY, 256), nn.GELU(), nn.Linear(256, 256), nn.GELU())
        self.out_pair = nn.Linear(256, 1); self.out_traj = nn.Linear(256, 6)
        self.d = d

    def summary(self, tokens):
        return self.to_summary(self.encoder(self.embed(tokens)).mean(1))

    def forward(self, tokens, queries):
        w = self.summary(tokens); qe = self.q_embed(queries)
        B, Q, _ = queries.shape
        h = self.head(torch.cat([qe, w[:, None, :].expand(B, Q, SUMMARY)], -1))
        return self.out_pair(h)[..., 0], self.out_traj(h)


def linear_cka(X, Y):
    """Linear CKA between two feature matrices (rows = same examples). Dimension-agnostic."""
    X = X - X.mean(0); Y = Y - Y.mean(0)
    xy = np.linalg.norm(X.T @ Y) ** 2
    xx = np.linalg.norm(X.T @ X); yy = np.linalg.norm(Y.T @ Y)
    return float(xy / (xx * yy + 1e-12))


def summaries(model, bank, idx, bs=128):
    ws = []
    with torch.no_grad():
        for i in range(0, len(idx), bs):
            ws.append(model.summary(torch.from_numpy(bank["tokens"][idx[i:i + bs]])).numpy())
    return np.concatenate(ws)


def main():
    bank = dict(np.load(RESULTS / "25_bank.npz"))
    val_mask = np.zeros(len(bank["family"]), dtype=bool)
    for fam in np.unique(bank["family"]):
        fi = np.where(bank["family"] == fam)[0]; val_mask[fi[-len(fi) // 10:]] = True
    tr = np.where(~val_mask)[0]; va = np.where(val_mask)[0]
    fam_va = bank["family"][va]

    Ws, labels = [], []
    # untrained baseline (random init)
    torch.manual_seed(999); base = SmallGen(96, 3)
    W_base = summaries(base, bank, va)

    for (d, L, seed) in CONFIGS:
        torch.manual_seed(seed); rng = np.random.default_rng(seed)
        m = SmallGen(d, L); opt = torch.optim.Adam(m.parameters(), lr=3e-4)
        for step in range(STEPS):
            b = tr[rng.integers(0, len(tr), 64)]
            lp, lt = g26.losses(m, torch.from_numpy(bank["tokens"][b]),
                                torch.from_numpy(bank["queries"][b]), torch.from_numpy(bank["targets"][b]))
            (lp + lt).backward(); opt.step(); opt.zero_grad()
            if step % 1000 == 0:
                progress(f"37_gen_d{d}_s{seed}", step, STEPS, loss=float((lp + lt).detach()))
        m.eval()
        W = summaries(m, bank, va); Ws.append(W)
        labels.append(KMeans(8, n_init=10, random_state=0).fit(W).labels_)
        print(f"  trained d={d} L={L} seed={seed}: summary ready")

    K = len(Ws)
    cka = np.array([[linear_cka(Ws[i], Ws[j]) for j in range(K)] for i in range(K)])
    cka_base = np.mean([linear_cka(Ws[i], W_base) for i in range(K)])
    ari = np.array([[adjusted_rand_score(labels[i], labels[j]) for j in range(K)] for i in range(K)])
    fam_ari = np.mean([adjusted_rand_score(fam_va, labels[i]) for i in range(K)])

    iu = np.triu_indices(K, 1)
    mean_cka = float(cka[iu].mean()); mean_ari = float(ari[iu].mean())
    print(f"\nP1 convergence: trained-trained mean CKA = {mean_cka:.3f} "
          f"(untrained baseline {cka_base:.3f}) -> {'PASS' if mean_cka > 0.5 and mean_cka >= 2 * cka_base else 'FAIL'}")
    print(f"P2 same map: trained-trained mean cluster ARI = {mean_ari:.3f} "
          f"(vs true family ARI {fam_ari:.3f}) -> {'PASS' if mean_ari > 0.6 else 'FAIL'}")
    out = {"configs": CONFIGS, "cka_matrix": cka.tolist(), "cka_untrained_baseline": cka_base,
           "ari_matrix": ari.tolist(), "mean_trained_cka": mean_cka, "mean_trained_ari": mean_ari,
           "mean_family_ari": float(fam_ari),
           "P1_pass": bool(mean_cka > 0.5 and mean_cka >= 2 * cka_base),
           "P2_pass": bool(mean_ari > 0.6)}
    (RESULTS / "37_platonic.json").write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(1, 2, figsize=(11, 4.5))
    im0 = ax[0].imshow(cka, vmin=0, vmax=1, cmap="viridis"); ax[0].set_title(f"world-summary CKA (mean {mean_cka:.2f})")
    fig.colorbar(im0, ax=ax[0]); ax[0].set_xticks(range(K)); ax[0].set_xticklabels([f"d{d}s{s}" for d,_,s in CONFIGS], fontsize=7, rotation=45); ax[0].set_yticks(range(K)); ax[0].set_yticklabels([f"d{d}s{s}" for d,_,s in CONFIGS], fontsize=7)
    im1 = ax[1].imshow(ari, vmin=0, vmax=1, cmap="magma"); ax[1].set_title(f"cluster ARI (mean {mean_ari:.2f})")
    fig.colorbar(im1, ax=ax[1])
    fig.suptitle("Platonic test: do independent generalists build the same map of law?")
    fig.tight_layout(); fig.savefig(RESULTS / "37_platonic.png", dpi=140)
    print("saved results/37_platonic.json + .png")


if __name__ == "__main__":
    main()
