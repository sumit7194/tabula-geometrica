"""Step 27 — Phase G gates G2 (zero-shot) + G3 (the prize: world-summary space).

G3 probes the 64-d summary w the generalist builds per episode, against the TRUE
world params (meta.json). No training — just read out structure.
  G3a family clustering (KMeans-8 ARI vs family)        pre-registered > 0.8
  G3b within-family param decodability (ridge, held-out r)  pre-registered > 0.9
  G3c EM-kinship: is d(chargedE, magneticB) < d(either, well1p1)?  EXPLORATORY
  G3d intrinsic dimensionality of w (participation ratio)         EXPLORATORY
G2 zero-shot: loss on a range-widened bank vs the in-range val loss (< 2x).

Usage: 27_g3_probes.py --model results/26_generalist_120k.pt \
         --bank results/25_bank.npz [--g2-bank results/25_bank_wide.npz] --device mps
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import torch
from curvlib import RESULTS
from importlib import import_module
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.linear_model import Ridge
from sklearn.metrics import adjusted_rand_score, r2_score
from sklearn.model_selection import cross_val_predict

gen = import_module("26_generalist")
FAMS = ["flat1p1", "flat3p1", "well1p1", "aniso2p1",
        "chargedE", "magneticB", "twocharge", "matter"]
# one world-level scalar per family for the decodability probe (varies per world)
DECODE_KEY = {"well1p1": "depth", "aniso2p1": "s_phi", "chargedE": "e_amp",
              "magneticB": "b_amp", "twocharge": ("f1", "amp"), "matter": "m_total"}


def summaries(model, bank, idx, device, bs=128):
    ws = []
    with torch.no_grad():
        for i in range(0, len(idx), bs):
            b = idx[i:i + bs]
            tk = torch.from_numpy(bank["tokens"][b]).to(device)
            ws.append(model.summary(tk).cpu().numpy())
    return np.concatenate(ws)


def val_idx(bank):
    m = np.zeros(len(bank["family"]), dtype=bool)
    for fam in np.unique(bank["family"]):
        fi = np.where(bank["family"] == fam)[0]
        m[fi[-len(fi) // 10:]] = True
    return np.where(m)[0]


def scalar_from_meta(meta, key):
    if key == "m_total":  # matter: blobs = list of [cx, cy, mass]
        return float(np.sum([b[2] for b in meta["blobs"]]))
    if isinstance(key, tuple):
        return float(meta[key[0]][key[1]])
    return float(meta[key])


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--model", default=str(RESULTS / "26_generalist_120k.pt"))
    p.add_argument("--bank", default=str(RESULTS / "25_bank.npz"))
    p.add_argument("--g2-bank", default="")
    p.add_argument("--device", default="cpu")
    args = p.parse_args()

    bank = dict(np.load(args.bank))
    meta = json.loads(Path(args.bank).with_suffix(".meta.json").read_text())
    model = gen.Generalist()
    model.load_state_dict(torch.load(args.model, map_location="cpu"))
    model.to(args.device).eval()

    vi = val_idx(bank)
    W = summaries(model, bank, vi, args.device)
    fam = bank["family"][vi]
    out = {}

    # G3a — clustering
    km = KMeans(n_clusters=8, n_init=10, random_state=0).fit(W)
    ari = float(adjusted_rand_score(fam, km.labels_))
    out["G3a_cluster_ARI"] = ari
    print(f"G3a clustering ARI = {ari:.3f}  (gate >0.8 {'PASS' if ari > 0.8 else 'FAIL'})")

    # G3b — within-family param decodability (5-fold CV held-out r)
    out["G3b_decode_r"] = {}
    for fi, name in enumerate(FAMS):
        if name not in DECODE_KEY:
            continue
        sel = np.where(fam == fi)[0]
        y = np.array([scalar_from_meta(meta[vi[s]], DECODE_KEY[name]) for s in sel])
        if np.std(y) < 1e-9:
            continue
        Xf = W[sel]
        pred = cross_val_predict(Ridge(alpha=1.0), Xf, y, cv=5)
        r = float(np.corrcoef(pred, y)[0, 1])
        out["G3b_decode_r"][name] = r
        print(f"G3b decode {name:10s} {str(DECODE_KEY[name]):14s} r={r:.3f}")
    rs = list(out["G3b_decode_r"].values())
    out["G3b_median_r"] = float(np.median(rs))
    print(f"G3b median r = {out['G3b_median_r']:.3f}  "
          f"(gate >0.9 {'PASS' if min(rs) > 0.9 else 'FAIL (min %.2f)' % min(rs)})")

    # centroids for kinship
    cent = {name: W[fam == fi].mean(0) for fi, name in enumerate(FAMS)}

    def d(a, b):
        return float(np.linalg.norm(cent[a] - cent[b]))

    # G3c — EM kinship (exploratory) with shuffled-family null
    em = d("chargedE", "magneticB")
    ref = 0.5 * (d("chargedE", "well1p1") + d("magneticB", "well1p1"))
    rng = np.random.default_rng(0)
    null = []
    for _ in range(1000):
        fsh = rng.permutation(fam)
        c = {fi: W[fsh == fi].mean(0) for fi in range(8)}
        null.append(np.linalg.norm(c[4] - c[5]))  # 4=chargedE,5=magneticB
    z = float((em - np.mean(null)) / (np.std(null) + 1e-9))
    out["G3c_kinship"] = {"d_E_B": em, "d_to_gravity": ref,
                          "closer_than_gravity": bool(em < ref), "z_vs_null": z}
    print(f"G3c EM-kinship: d(E,B)={em:.3f} vs d(.,gravity)={ref:.3f} "
          f"-> {'CLOSER' if em < ref else 'not closer'}; z vs shuffled null = {z:.2f}")

    # G3d — intrinsic dimensionality (participation ratio of PCA spectrum)
    ev = PCA().fit(W).explained_variance_
    pr = float((ev.sum() ** 2) / (ev ** 2).sum())
    out["G3d_participation_ratio"] = pr
    print(f"G3d intrinsic dim (participation ratio) = {pr:.2f} of {W.shape[1]}")

    # G2 — zero-shot widened bank
    if args.g2_bank and Path(args.g2_bank).exists():
        wb = dict(np.load(args.g2_bank))
        all_idx = np.arange(len(wb["family"]))
        vacc, vmse = gen.evaluate(model, bank, vi, args.device)
        wacc, wmse = gen.evaluate(model, wb, all_idx, args.device)

        def agg(d_):
            return float(np.mean(list(d_.values())))
        g2 = {"in_pair": agg(vacc), "wide_pair": agg(wacc),
              "in_traj": agg(vmse), "wide_traj": agg(wmse),
              "traj_ratio": agg(wmse) / agg(vmse)}
        out["G2"] = g2
        print(f"G2 zero-shot: traj MSE in={g2['in_traj']:.4f} wide={g2['wide_traj']:.4f} "
              f"(ratio {g2['traj_ratio']:.2f}, gate <2 "
              f"{'PASS' if g2['traj_ratio'] < 2 else 'FAIL'}); "
              f"pair in={g2['in_pair']:.3f} wide={g2['wide_pair']:.3f}")

    (RESULTS / "27_g3.json").write_text(json.dumps(out, indent=1))

    # 2D PCA map of the world-summary space
    P = PCA(n_components=2).fit_transform(W)
    fig, ax = plt.subplots(figsize=(8, 7))
    for fi, name in enumerate(FAMS):
        m = fam == fi
        ax.scatter(P[m, 0], P[m, 1], s=8, alpha=0.5, label=name)
    ax.set_title(f"world-summary space (PCA), ARI={ari:.2f}, partic.dim={pr:.1f}")
    ax.legend(markerscale=2, fontsize=8)
    fig.tight_layout()
    fig.savefig(RESULTS / "27_world_space.png", dpi=140)
    print(f"saved results/27_g3.json + 27_world_space.png")


if __name__ == "__main__":
    main()
