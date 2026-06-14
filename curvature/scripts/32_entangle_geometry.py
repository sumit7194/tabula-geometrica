"""Step 32 — Phase J: geometry from entanglement (the It-from-Qubit bridge).

Free-fermion ground states (classically computable) -> entanglement structure -> learn a
geometry from the mutual-information table alone (never positions). Premise: Van Raamsdonk
2010 / Ryu-Takayanagi / You-Qi 2018 — spatial geometry emerges from entanglement.

J0 (floor, run first): the engine reproduces the c=1 CFT scaling S(l)=(1/3)ln l + const.
J1 geometry emerges (embedding distance isotonic in true lattice distance).
J2 dimension (intrinsic dim of embedding tracks lattice dim).
J3 Van Raamsdonk pinch-off (decouple two halves -> embedding pulls apart).
Pre-registration 2026-06-15. Physics web-verified (Peschel correlation-matrix method).
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
from sklearn.decomposition import PCA
from sklearn.isotonic import IsotonicRegression
from sklearn.metrics import r2_score
from torch import nn


def corr_matrix(hop):
    """Ground-state correlation matrix C_ij=<c_i^dag c_j> for hopping matrix `hop`,
    half-filled (lowest N/2 modes occupied)."""
    n = hop.shape[0]
    evals, V = np.linalg.eigh(hop)
    occ = V[:, : n // 2]                      # lowest N/2 modes
    return occ @ occ.conj().T                 # sum_occ |psi><psi|


def region_entropy(C, idx):
    xi = np.linalg.eigvalsh(C[np.ix_(idx, idx)]).real
    xi = np.clip(xi, 1e-12, 1 - 1e-12)
    return float(-(xi * np.log(xi) + (1 - xi) * np.log(1 - xi)).sum())


def mutual_info(C):
    """Pairwise single-site MI I(i,j)=S_i+S_j-S_ij for all i,j."""
    n = C.shape[0]
    Si = np.array([region_entropy(C, [i]) for i in range(n)])
    I = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            Sij = region_entropy(C, [i, j])
            I[i, j] = I[j, i] = max(Si[i] + Si[j] - Sij, 0.0)
    return I


def chain_hop(n, periodic=True):
    h = np.zeros((n, n))
    for i in range(n - 1):
        h[i, i + 1] = h[i + 1, i] = -1.0
    if periodic:
        h[0, n - 1] = h[n - 1, 0] = -1.0
    return h


def grid_hop(L):
    n = L * L
    h = np.zeros((n, n))
    idx = lambda r, c: (r % L) * L + (c % L)
    for r in range(L):
        for c in range(L):
            for dr, dc in ((0, 1), (1, 0)):
                a, b = idx(r, c), idx(r + dr, c + dc)
                h[a, b] = h[b, a] = -1.0
    return h


def two_chain_hop(n_each, tc):
    """Two periodic chains of n_each, joined by two cross links of strength tc."""
    n = 2 * n_each
    h = np.zeros((n, n))
    for c0 in (0, n_each):
        for i in range(n_each - 1):
            h[c0 + i, c0 + i + 1] = h[c0 + i + 1, c0 + i] = -1.0
        h[c0, c0 + n_each - 1] = h[c0 + n_each - 1, c0] = -1.0
    # join the two rings at one bond
    h[0, n_each] = h[n_each, 0] = -tc
    return h


# ---------- J0: validation floor ----------
def j0_validation():
    n = 256
    C = corr_matrix(chain_hop(n, periodic=True))
    Ls = np.array([4, 8, 16, 32, 48, 64])
    S = np.array([region_entropy(C, list(range(n // 2 - L // 2, n // 2 + L // 2))) for L in Ls])
    # S = (c/3) ln L + const ; fit slope vs ln L
    A = np.vstack([np.log(Ls), np.ones_like(Ls, float)]).T
    slope, const = np.linalg.lstsq(A, S, rcond=None)[0]
    c_eff = 3 * slope
    print(f"J0: S(l) fit slope={slope:.3f} -> c={c_eff:.3f} (CFT: c=1, slope=1/3=0.333); "
          f"{'PASS' if abs(slope - 1 / 3) < 0.05 else 'FAIL'}")
    return {"slope": float(slope), "c_eff": float(c_eff), "Ls": Ls.tolist(), "S": S.tolist(),
            "pass": bool(abs(slope - 1 / 3) < 0.05)}


# ---------- the learner: embed sites so geometry explains the MI table ----------
def ent_distance(I):
    """Entanglement distance: high MI -> small distance (Van Raamsdonk). d = -log(I/Imax)."""
    D = -np.log(I / (I.max() + 1e-12) + 1e-4)
    np.fill_diagonal(D, 0.0)
    return D


def learn_geometry(I, d=8, steps=6000, seed=0):
    """Embed sites in R^d (generous, so DIMENSION can emerge) by stress-minimizing
    |z_i - z_j| against the entanglement distance d_ent (metric MDS by SGD). Positions
    are NEVER given — only the mutual-information table."""
    n = I.shape[0]
    De = ent_distance(I)
    iu = np.triu_indices(n, 1)
    tgt = torch.tensor(De[iu], dtype=torch.float32)
    tgt = tgt / tgt.mean()
    torch.manual_seed(seed)
    z = nn.Parameter(torch.randn(n, d) * 0.5)
    opt = torch.optim.Adam([z], lr=5e-3)
    ii = torch.tensor(iu[0]); jj = torch.tensor(iu[1])
    for _ in range(steps):
        dist = (z[ii] - z[jj]).norm(dim=1)
        loss = ((dist - tgt) ** 2).mean()      # stress (no flexible f -> dim can collapse)
        opt.zero_grad(); loss.backward(); opt.step()
    return z.detach().numpy()


def emb_dist(z):
    from scipy.spatial.distance import squareform, pdist
    return squareform(pdist(z))


def isotonic_r2(emb_d, true_d):
    iu = np.triu_indices(len(emb_d), 1)
    x, y = emb_d[iu], true_d[iu]
    yhat = IsotonicRegression(out_of_bounds="clip").fit_transform(x, y)
    return float(r2_score(y, yhat))


def participation_ratio(z):
    ev = PCA().fit(z - z.mean(0)).explained_variance_
    return float((ev.sum() ** 2) / (ev ** 2).sum())


def block_mi(C, B):
    """Coarse-grain into blocks of B contiguous sites; MI between BLOCKS (region-based,
    RT-faithful) — averages over the free-fermion parity oscillation that makes
    single-site MI pathological (even-separation correlations vanish at half filling)."""
    n = C.shape[0]
    nb = n // B
    blocks = [list(range(b * B, b * B + B)) for b in range(nb)]
    Sb = np.array([region_entropy(C, blk) for blk in blocks])
    I = np.zeros((nb, nb))
    for a in range(nb):
        for b in range(a + 1, nb):
            Sab = region_entropy(C, blocks[a] + blocks[b])
            I[a, b] = I[b, a] = max(Sb[a] + Sb[b] - Sab, 0.0)
    return I


def chain_true_dist(n):
    i = np.arange(n)
    return np.abs(i[:, None] - i[None, :]).astype(float)


def grid_true_dist(L):
    rc = np.array([(r, c) for r in range(L) for c in range(L)], float)
    from scipy.spatial.distance import squareform, pdist
    return squareform(pdist(rc))


def j1_j2(B=4):
    res = {}
    # open chain coarse-grained into blocks of B -> expect 1D embedding
    n = 128
    Cc = corr_matrix(chain_hop(n, periodic=False))
    nb = n // B
    z = learn_geometry(block_mi(Cc, B))
    r2 = isotonic_r2(emb_dist(z), chain_true_dist(nb)); pr = participation_ratio(z)
    res["chain"] = {"isotonic_r2": r2, "participation_dim": pr, "B": B}
    print(f"J1 chain (blocks of {B}): isotonic R2={r2:.3f} (gate>0.9 {'PASS' if r2>0.9 else 'FAIL'}); "
          f"J2 dim={pr:.2f} (expect ~1)")
    # 2D grid coarse-grained into 2x2 blocks -> expect 2D embedding
    L = 12
    Cg = corr_matrix(grid_hop(L))
    Ig, bd = grid_block_mi(Cg, L, 2)
    zg = learn_geometry(Ig)
    r2g = isotonic_r2(emb_dist(zg), bd); prg = participation_ratio(zg)
    res["grid"] = {"isotonic_r2": r2g, "participation_dim": prg}
    print(f"J1 grid (2x2 blocks): isotonic R2={r2g:.3f} (gate>0.9 {'PASS' if r2g>0.9 else 'FAIL'}); "
          f"J2 dim={prg:.2f} (expect ~2)")
    return res


def grid_block_mi(C, L, b):
    """2D block-MI on an LxL grid coarse-grained into bxb blocks + true block distances."""
    nbl = L // b
    blocks, centers = [], []
    for br in range(nbl):
        for bc in range(nbl):
            sites = [(br * b + r) * L + (bc * b + c) for r in range(b) for c in range(b)]
            blocks.append(sites); centers.append((br, bc))
    m = len(blocks)
    Sb = np.array([region_entropy(C, blk) for blk in blocks])
    I = np.zeros((m, m))
    for a in range(m):
        for d2 in range(a + 1, m):
            Sad = region_entropy(C, blocks[a] + blocks[d2])
            I[a, d2] = I[d2, a] = max(Sb[a] + Sb[d2] - Sad, 0.0)
    from scipy.spatial.distance import squareform, pdist
    return I, squareform(pdist(np.array(centers, float)))


def j3_pinchoff():
    """Decouple two chains; as cross-link t_c -> 0, cross-MI and embedding separation."""
    n_each = 24
    rows = []
    B = 4
    nb = n_each // B
    for tc in (1.0, 0.6, 0.3, 0.1, 0.03, 0.0):
        C = corr_matrix(two_chain_hop(n_each, tc))
        I = block_mi(C, B)                       # block-MI over all 2*nb blocks
        cross_mi = float(I[:nb, nb:].mean())
        z = learn_geometry(I, steps=4000)
        d = emb_dist(z)
        within = (d[:nb, :nb].sum() + d[nb:, nb:].sum()) / 2
        within /= (nb * (nb - 1))
        across = float(d[:nb, nb:].mean())
        rows.append({"tc": tc, "cross_mi": cross_mi,
                     "across_over_within": across / (within + 1e-9)})
        print(f"J3 tc={tc:.2f}: cross-MI={cross_mi:.2e}  across/within emb dist={across/(within+1e-9):.2f}")
    # gate: monotone — separation grows as tc falls
    sep = [r["across_over_within"] for r in rows]
    monotone = all(sep[i] <= sep[i + 1] + 0.05 for i in range(len(sep) - 1))
    print(f"J3 pinch-off: separation grows as coupling falls -> {'PASS' if monotone else 'CHECK'}")
    return {"rows": rows, "monotone_separation": bool(monotone)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", default="all", choices=("j0", "all"))
    args = ap.parse_args()
    out = {"J0": j0_validation()}
    if args.stage == "all":
        out["J1_J2"] = j1_j2()
        out["J3"] = j3_pinchoff()
    (RESULTS / "32_entangle.json").write_text(json.dumps(out, indent=1))
    print("saved results/32_entangle.json")


if __name__ == "__main__":
    main()
