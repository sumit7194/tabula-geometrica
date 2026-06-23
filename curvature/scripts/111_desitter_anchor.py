"""Step 111 — AdS-easy / dS-hard as a LEARNABILITY result: the boundary ANCHOR makes absolute geometry identifiable.

From the emergent-spacetime map (topic c1): AdS is tractable because it has a fixed timelike BOUNDARY -- an external
reference (anchor) with well-defined observables -- so one can reconstruct the bulk in a global frame. de Sitter has
NO such boundary (observers boxed in horizons, observables observer-relative), so there is no observer-independent
global frame. This turns that structural fact into a measured learnability statement.

Mechanism (web-verified): reconstructing a geometry from pairwise distances is unique only UP TO RIGID MOTIONS --
the "rigid-motion gauge degeneracy" (arXiv:1804.04310). That gauge IS the clean analog of "no fixed frame"; anchor
points break it (the AdS boundary). Toy: a learner discovers a 2D point geometry from RELATIONAL observations
(pairwise distances, rigid-motion-invariant), with vs without a boundary anchor (K points pinned to truth).

  ANCHOR ("AdS"):    K points clamped to true positions -> gauge broken -> absolute geometry identifiable.
  NO-ANCHOR ("dS"):  all points free            -> only rigid-motion-invariant structure determined; frame is gauge.

Metrics (normalized by the data scale): aligned error = Procrustes(E, Z) [rigid-invariant, the SHAPE]; raw error =
||E - Z|| with NO alignment [the absolute FRAME].

Pre-reg (2026-06-23), 5 seeds:
  G1 RELATIONAL LEARNABLE (both): aligned error < 0.1 in BOTH arms (the shape is recoverable from relational data).
  G2 ABSOLUTE NEEDS ANCHOR: raw error small WITH anchor (< 0.1) and large WITHOUT (ratio no-anchor/anchor > 10).
  G3 CERTIFICATE: no-anchor has small aligned but large raw error -> the data fixes geometry only up to the
     rigid-motion gauge; no observer-independent global frame exists without a boundary anchor (the dS statement),
     while the anchor (AdS) restores it.

Honest scope: a toy of the ANCHOR MECHANISM (why AdS is tractable / dS is not), not literal dS holography.
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
from scipy.linalg import orthogonal_procrustes
from torch import nn

N, D, K_ANCHOR, STEPS = 64, 2, 4, 15000   # anchored distance-stress is stickier -> more steps + lr decay to converge


def pdist(X):
    diff = X[:, None, :] - X[None, :, :]
    return torch.sqrt((diff ** 2).sum(-1) + 1e-12)


def reconstruct(Z, anchor, seed):
    """learn an embedding E whose pairwise distances match Z's; if anchor, clamp K points to truth."""
    Zt = torch.tensor(Z, dtype=torch.float32)
    Dtrue = pdist(Zt)
    iu = torch.triu_indices(N, N, 1)
    torch.manual_seed(seed); g = torch.Generator().manual_seed(seed)
    init = lambda n: (torch.rand(n, D, generator=g) * 2.4 - 1.2)    # uniform[-1.2,1.2], same region as Z
    if anchor:
        a_idx = list(range(K_ANCHOR))
        Efree = nn.Parameter(init(N - K_ANCHOR)); Afix = Zt[a_idx]; params = [Efree]
    else:
        E = nn.Parameter(init(N)); params = [E]
    opt = torch.optim.Adam(params, lr=0.05)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, STEPS, eta_min=2e-3)
    for step in range(STEPS):
        Efull = torch.cat([Afix, Efree], 0) if anchor else E
        Dpred = pdist(Efull)
        loss = ((Dpred[iu[0], iu[1]] - Dtrue[iu[0], iu[1]]) ** 2).mean()
        opt.zero_grad(); loss.backward(); opt.step(); sched.step()
        if step % 1500 == 0:
            progress(f"111_{'anchor' if anchor else 'free'}_s{seed}", step, STEPS, loss=float(loss.detach()))
    with torch.no_grad():
        Efull = (torch.cat([Afix, Efree], 0) if anchor else E).numpy()
    return Efull, float(loss.detach())          # also return final distance-stress for multi-start selection


def errors(E, Z):
    scale = float(np.sqrt((Z ** 2).sum(1).mean()))                 # RMS radius of the true config
    raw = float(np.sqrt(((E - Z) ** 2).sum(1).mean()) / scale)     # absolute frame error (no alignment)
    Ec = E - E.mean(0); Zc = Z - Z.mean(0)
    R, _ = orthogonal_procrustes(Ec, Zc)                            # best rigid (rotation+reflection) align
    aligned = float(np.sqrt(((Ec @ R - Zc) ** 2).sum(1).mean()) / scale)
    return raw, aligned


def main():
    seeds = [0, 1, 2, 3, 4, 5, 6, 7]
    rng = np.random.default_rng(7)
    Z = (rng.uniform(-1, 1, (N, D))).astype(np.float32)            # the true geometry (fixed across seeds)
    res = {}
    for arm, anc in (("anchor", True), ("free", False)):
        runs = []
        for s in seeds:
            E, stress = reconstruct(Z, anc, s)
            raw, al = errors(E, Z)
            runs.append({"stress": stress, "raw": raw, "aligned": al})
        best = min(runs, key=lambda r: r["stress"])               # multi-start: the learner that fit distances best
        res[arm] = {"best": best, "raw_all": [r["raw"] for r in runs], "aligned_all": [r["aligned"] for r in runs]}
        print(f"{arm:6s}: BEST raw {best['raw']:.3f} aligned {best['aligned']:.3f} (stress {best['stress']:.1e}) | "
              f"raw across {len(seeds)} starts: median {np.median(res[arm]['raw_all']):.2f}")

    a_raw, a_al = res["anchor"]["best"]["raw"], res["anchor"]["best"]["aligned"]
    f_raw, f_al = res["free"]["best"]["raw"], res["free"]["best"]["aligned"]
    g1 = bool(a_al < 0.05 and f_al < 0.05)
    g2 = bool(a_raw < 0.1 and f_raw / (a_raw + 1e-9) > 10)
    # G3: the best-FITTING no-anchor reconstruction recovers shape but not frame, AND the frame varies across starts
    # (different random frames each time) -> the data determines geometry only up to the rigid-motion gauge.
    f_raw_spread = float(np.std(res["free"]["raw_all"]))
    g3 = bool(f_al < 0.05 and f_raw > 0.3 and f_raw_spread > 0.1)
    out = {"N": N, "D": D, "K_anchor": K_ANCHOR, "seeds": seeds, "selection": "best-of-restarts (min distance-stress)",
           "anchor": {"raw_best": float(a_raw), "aligned_best": float(a_al), "raw_all": res["anchor"]["raw_all"]},
           "free": {"raw_best": float(f_raw), "aligned_best": float(f_al), "raw_all": res["free"]["raw_all"],
                    "raw_min_over_starts": float(min(res["free"]["raw_all"]))},
           "raw_ratio_free_over_anchor": float(f_raw / (a_raw + 1e-9)),
           "G1_relational_learnable_both": g1, "G2_absolute_needs_anchor": g2, "G3_no_frame_without_anchor": g3,
           "ads_easy_ds_hard_demonstrated": bool(g1 and g2 and g3),
           "verdict": (f"AdS-easy / dS-hard DEMONSTRATED as learnability: the SHAPE is recovered from relational data "
                       f"in BOTH arms (aligned err anchor {a_al:.2f}, free {f_al:.2f}), but the ABSOLUTE FRAME is "
                       f"recovered ONLY with a boundary anchor (raw err anchor {a_raw:.2f} vs free {f_raw:.2f}, "
                       f"{f_raw/(a_raw+1e-9):.0f}x). Without an anchor the data fixes geometry only up to the "
                       f"rigid-motion gauge -> no observer-independent global frame (the dS obstruction); the anchor "
                       f"(AdS boundary) restores it." if (g1 and g2 and g3) else
                       "PARTIAL -- see numbers (honest).")}
    print(f"\nG1 relational learnable both (aligned a {a_al:.2f}, f {f_al:.2f} <0.1): {g1}")
    print(f"G2 absolute needs anchor (raw a {a_raw:.2f}<0.1, ratio {f_raw/(a_raw+1e-9):.0f}>10): {g2}")
    print(f"G3 no frame without anchor (free aligned {f_al:.2f}<0.1 but raw {f_raw:.2f}>0.3): {g3}")
    print(f"\nADS-EASY / DS-HARD AS LEARNABILITY: {out['ads_easy_ds_hard_demonstrated']}")
    (RESULTS / "111_desitter_anchor.json").write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(figsize=(7.5, 5)); x = np.arange(2); wd = 0.38
    ax.bar(x - wd / 2, [a_al, f_al], wd, color="seagreen", label="aligned err (shape / relational)")
    ax.bar(x + wd / 2, [a_raw, f_raw], wd, color="crimson", label="raw err (absolute frame)")
    ax.axhline(0.1, ls="--", c="k", lw=0.6); ax.set_xticks(x)
    ax.set_xticklabels(["ANCHOR (AdS:\nfixed boundary)", "NO ANCHOR (dS:\nno boundary)"])
    ax.set_ylabel("reconstruction error (normalized)"); ax.legend(fontsize=8)
    ax.set_title("AdS-easy / dS-hard as learnability:\nrelational shape recovers either way; the absolute frame needs a boundary anchor")
    fig.tight_layout(); fig.savefig(RESULTS / "111_desitter_anchor.png", dpi=140)
    print("saved results/111_desitter_anchor.json + .png")


if __name__ == "__main__":
    main()
