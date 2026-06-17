"""Step 89 — THE CURVATURE ATLAS II: hierarchies are intrinsically HYPERBOLIC (negative curvature).

Atlas row 2. Web-verified (Gromov; Nickel-Kiela 1705.08039; Sarkar 2011): a TREE metric is exactly delta=0
hyperbolic, and any tree embeds in the 2-D hyperbolic (Poincare) disk at arbitrarily low distortion -- while
EUCLIDEAN space CANNOT embed trees faithfully at low dimension (a tree's neighborhood grows exponentially,
Euclidean volume only polynomially). So "discover a hierarchy -> you are forced into NEGATIVE curvature." The
curvature SIGN is the discovered object (the "minus sign earned" of Phase A, now in concept space), and it is
DATA-SPECIFIC: a flat grid graph is NOT tree-hyperbolic and embeds fine in Euclidean.

A net embeds a graph's shortest-path metric into a 2-D Euclidean disk vs a 2-D Poincare (hyperbolic) disk and
we compare distortion; we also measure the Gromov delta of each metric. Tree -> hyperbolic wins big, delta~0;
grid -> no hyperbolic advantage, delta>0.

Pre-reg (2026-06-17):
  H1 TREE IS HYPERBOLIC: tree Gromov delta ~ 0 (< 0.1 path units) while a grid-graph delta > 0.4 -- the data's
     intrinsic curvature is negative for the hierarchy, ~flat for the grid.
  H2 NEGATIVE CURVATURE REQUIRED: for the tree at dim 2, hyperbolic distortion <= 0.5x Euclidean distortion
     (Euclidean provably fails; the net discovers it must go negative).
  H3 DATA-SPECIFIC SIGN: for the grid, hyperbolic gives NO advantage (hyp/Euc distortion ratio > 0.8) -- the
     discovered curvature sign flips with the data (hierarchy negative, grid flat).
"""

import json
import sys
from collections import deque
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import torch
from curvlib import RESULTS, progress
from torch import nn

np.seterr(all="ignore")


def all_pairs_sp(adj, n):
    D = np.full((n, n), 0.0)
    for s in range(n):
        dist = [-1] * n; dist[s] = 0; q = deque([s])
        while q:
            u = q.popleft()
            for w in adj[u]:
                if dist[w] < 0:
                    dist[w] = dist[u] + 1; q.append(w)
        D[s] = dist
    return D


def balanced_tree(b=2, depth=6):
    adj = {0: []}; nodes = [0]; frontier = [0]; nxt = 1
    for _ in range(depth):
        newf = []
        for p in frontier:
            for _ in range(b):
                adj[nxt] = [p]; adj[p].append(nxt); nodes.append(nxt); newf.append(nxt); nxt += 1
        frontier = newf
    return adj, nxt


def grid_graph(L=8):
    n = L * L; adj = {i: [] for i in range(n)}
    for r in range(L):
        for c in range(L):
            i = r * L + c
            if c + 1 < L: adj[i].append(i + 1); adj[i + 1].append(i)
            if r + 1 < L: adj[i].append(i + L); adj[i + L].append(i)
    return adj, n


def gromov_delta(D, n_samples=20000, seed=0):
    rng = np.random.default_rng(seed); n = len(D); worst = 0.0
    for _ in range(n_samples):
        w, x, y, z = rng.integers(0, n, 4)
        s = sorted([D[w, x] + D[y, z], D[w, y] + D[x, z], D[w, z] + D[x, y]])
        worst = max(worst, (s[2] - s[1]) / 2.0)
    return float(worst)


def poincare_dist(x):                                          # pairwise Poincare distances for points in the ball
    nrm = (x ** 2).sum(-1)
    sq = (x[:, None, :] - x[None, :, :]).pow(2).sum(-1)
    arg = 1 + 2 * sq / ((1 - nrm[:, None]) * (1 - nrm[None, :]) + 1e-9)
    return torch.acosh(torch.clamp(arg, min=1 + 1e-7))


def embed(D, hyperbolic, dim=2, steps=6000, seed=0):
    """fit dim-D embedding to the metric D; learnable global scale; return mean relative distortion."""
    torch.manual_seed(seed); n = len(D); Dt = torch.tensor(D, dtype=torch.float32)
    x = nn.Parameter(torch.randn(n, dim) * 0.1); logs = nn.Parameter(torch.zeros(1))
    opt = torch.optim.Adam([x, logs], lr=0.02)
    iu = torch.triu_indices(n, n, 1)
    for step in range(steps):
        if hyperbolic:
            nrm = (x ** 2).sum(-1, keepdim=True); xb = x * torch.tanh(torch.sqrt(nrm) + 1e-9) / (torch.sqrt(nrm) + 1e-9)
            de = poincare_dist(xb)
        else:
            de = (x[:, None, :] - x[None, :, :]).pow(2).sum(-1).clamp_min(1e-9).sqrt()
        s = torch.exp(logs)
        pred = s * de[iu[0], iu[1]]; tgt = Dt[iu[0], iu[1]]
        loss = (((pred - tgt) / tgt) ** 2).mean()              # relative distortion
        opt.zero_grad(); loss.backward(); opt.step()
        if step % 600 == 0: progress(f"89_{'hyp' if hyperbolic else 'euc'}", step, steps, loss=float(loss.detach()))
    with torch.no_grad():
        if hyperbolic:
            nrm = (x ** 2).sum(-1, keepdim=True); xb = x * torch.tanh(torch.sqrt(nrm) + 1e-9) / (torch.sqrt(nrm) + 1e-9)
            de = poincare_dist(xb)
        else:
            de = (x[:, None, :] - x[None, :, :]).pow(2).sum(-1).clamp_min(1e-9).sqrt()
        s = torch.exp(logs); pred = s * de[iu[0], iu[1]]; tgt = Dt[iu[0], iu[1]]
        dist = float((((pred - tgt) / tgt).abs()).mean())
    return dist


def main():
    tadj, tn = balanced_tree(); Dtree = all_pairs_sp(tadj, tn)
    gadj, gn = grid_graph(); Dgrid = all_pairs_sp(gadj, gn)
    dt = gromov_delta(Dtree); dg = gromov_delta(Dgrid)

    tree_euc = embed(Dtree, False); tree_hyp = embed(Dtree, True)
    grid_euc = embed(Dgrid, False); grid_hyp = embed(Dgrid, True)
    tree_ratio = tree_hyp / (tree_euc + 1e-9); grid_ratio = grid_hyp / (grid_euc + 1e-9)

    h1 = bool(dt < 0.1 and dg > 0.4)
    h2 = bool(tree_ratio < 0.5)
    h3 = bool(grid_ratio > 0.8)
    out = {"tree_gromov_delta": dt, "grid_gromov_delta": dg, "tree_dim2_euclidean_distortion": tree_euc,
           "tree_dim2_hyperbolic_distortion": tree_hyp, "tree_hyp_over_euc": tree_ratio,
           "grid_dim2_euclidean_distortion": grid_euc, "grid_dim2_hyperbolic_distortion": grid_hyp,
           "grid_hyp_over_euc": grid_ratio,
           "H1_tree_is_hyperbolic": h1, "H2_negative_curvature_required": h2, "H3_data_specific_sign": h3,
           "hierarchy_is_hyperbolic": bool(h1 and h2 and h3)}
    print(f"H1 tree Gromov delta {dt:.3f} (~0) vs grid {dg:.3f} (>0.4): {h1}")
    print(f"H2 TREE needs negative curvature: hyp distortion {tree_hyp:.3f} vs euc {tree_euc:.3f}, ratio {tree_ratio:.3f} (<0.5): {h2}")
    print(f"H3 GRID flat (no hyp advantage): hyp {grid_hyp:.3f} vs euc {grid_euc:.3f}, ratio {grid_ratio:.3f} (>0.8): {h3}")
    print(f"\nHIERARCHY IS HYPERBOLIC (discover a tree -> forced into negative curvature; sign is data-specific): {out['hierarchy_is_hyperbolic']}")
    (RESULTS / "89_hierarchy_hyperbolic.json").write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(1, 2, figsize=(13, 5))
    x = np.arange(2); w = 0.35
    ax[0].bar(x - w / 2, [tree_euc, grid_euc], w, color="navy", label="Euclidean (κ=0)")
    ax[0].bar(x + w / 2, [tree_hyp, grid_hyp], w, color="crimson", label="Hyperbolic (κ<0)")
    ax[0].set_xticks(x); ax[0].set_xticklabels(["TREE (hierarchy)", "GRID (control)"]); ax[0].set_ylabel("dim-2 distortion")
    ax[0].legend(fontsize=8); ax[0].set_title("the tree DEMANDS negative curvature; the grid does not\n(curvature sign is data-specific -- the 'minus sign earned')")
    ax[1].bar([0, 1], [dt, dg], color=["crimson", "navy"]); ax[1].set_xticks([0, 1]); ax[1].set_xticklabels(["TREE", "GRID"])
    ax[1].set_ylabel("Gromov δ (hyperbolicity; 0 = tree)"); ax[1].set_title(f"intrinsic curvature: tree δ={dt:.2f} (hyperbolic), grid δ={dg:.2f} (flat)")
    fig.tight_layout(); fig.savefig(RESULTS / "89_hierarchy_hyperbolic.png", dpi=140)
    print("saved results/89_hierarchy_hyperbolic.json + .png")


if __name__ == "__main__":
    main()
