"""Step 117 — topological band theory: a net discovers a QUANTIZED invariant (SSH winding) + bulk-boundary correspondence.

Caps the topology/holonomy cluster (AB winding 113 -> Berry curvature 54 -> grid torus 115/116 -> band topology). The
Su-Schrieffer-Heeger (SSH) model (web-verified, BDI class): a 1D chain with intracell hopping v and intercell hopping
w. Bloch Hamiltonian H(k) = d_x(k) sigma_x + d_y(k) sigma_y with d(k) = (v + w cos k, w sin k). The WINDING NUMBER of
d(k) around the origin as k:0->2pi is a topological invariant: 0 (trivial, v>w) or 1 (topological, w>v) -- it is a
HOLONOMY of the d-vector over the Brillouin zone. Bulk-boundary correspondence: the bulk winding number equals the
number of protected zero-energy EDGE modes of a finite open chain (winding 1 <-> a pair of edge states; 0 <-> none).

Three things a net discovers, each distinct:
  B1 THE INVARIANT: from the bulk d(k) trajectory (unit vectors -> angles only), a DeepSets net summing local angle
     increments recovers the winding number, QUANTIZED to integers matching v vs w (R^2 ~ 1, rounds exactly).
  B2 QUANTIZED / ROBUST (certificate): gap-preserving deformations of d(k) (never crossing the origin) leave the
     winding UNCHANGED; sweeping across the gap closing (v=w) is the ONLY way to flip it 0<->1.
  B3 BULK-BOUNDARY: the BULK winding predicts the BOUNDARY -- a net reading only bulk d(k) predicts the open-chain
     zero-energy edge-mode count (2*winding), matching exact diagonalization.

Pre-reg (2026-06-24):
  B1: winding-net test R^2 > 0.95 vs analytic winding AND integer-rounding accuracy = 1.0.
  B2: under gap-preserving deformations |Delta winding| < 0.1; across a v-sweep the winding steps 0->1 exactly at v=w.
  B3: 2*round(net winding) == open-chain edge-mode count for > 0.95 of held-out configs (bulk-boundary correspondence).
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
from torch import nn

NK, NCELLS, STEPS = 64, 20, 4000


def d_traj(v, w, nk=NK):
    k = np.linspace(0, 2 * np.pi, nk, endpoint=False)
    return np.stack([v + w * np.cos(k), w * np.sin(k)], 1)        # [nk,2]


def winding(d):
    phi = np.arctan2(d[:, 1], d[:, 0])
    dphi = np.diff(np.concatenate([phi, phi[:1]]))
    dphi = (dphi + np.pi) % (2 * np.pi) - np.pi                   # wrap to (-pi,pi]
    return float(dphi.sum() / (2 * np.pi))


def edge_count(v, w, ncells=NCELLS, tol=0.05):
    n = 2 * ncells; H = np.zeros((n, n))
    for j in range(n - 1):
        t = v if j % 2 == 0 else w                               # intracell v, intercell w
        H[j, j + 1] = H[j + 1, j] = t
    E = np.linalg.eigvalsh(H)
    return int((np.abs(E) < tol).sum())


def unit(d):
    return d / (np.linalg.norm(d, axis=-1, keepdims=True) + 1e-9)


class WindNet(nn.Module):
    """DeepSets over BZ segments: sum a per-segment MLP of (d_k, d_{k+1}) unit vectors -> winding (a holonomy)."""
    def __init__(s):
        super().__init__()
        s.phi = nn.Sequential(nn.Linear(4, 32), nn.GELU(), nn.Linear(32, 32))
        s.rho = nn.Sequential(nn.Linear(32, 32), nn.GELU(), nn.Linear(32, 1))

    def forward(s, d):                                            # d: [B,NK,2] unit vectors
        seg = torch.cat([d, torch.roll(d, -1, dims=1)], -1)      # [B,NK,4] consecutive pairs (closed)
        return s.rho(s.phi(seg).sum(1))[:, 0]


def make(n, rng):
    V, W, Y, EC = [], [], [], []
    for _ in range(n):
        v, w = rng.uniform(0.2, 2.0, 2)
        d = d_traj(v, w)
        V.append(unit(d)); W.append(winding(d)); Y.append([v, w]); EC.append(edge_count(v, w))
    return np.array(V, np.float32), np.array(W, np.float32), np.array(Y, np.float32), np.array(EC)


def main():
    rng = np.random.default_rng(0)
    Dtr, Wtr, _, _ = make(3000, rng)
    Dte, Wte, VWte, ECte = make(800, np.random.default_rng(9))

    torch.manual_seed(0); net = WindNet(); opt = torch.optim.Adam(net.parameters(), lr=2e-3)
    dt = torch.from_numpy(Dtr); wt = torch.from_numpy(Wtr); g = np.random.default_rng(1)
    for step in range(STEPS):
        idx = g.integers(0, len(dt), 128)
        loss = nn.functional.mse_loss(net(dt[idx]), wt[idx])
        opt.zero_grad(); loss.backward(); opt.step()
        if step % 1000 == 0:
            progress("117_wind", step, STEPS, loss=float(loss.detach()))
    net.eval()
    with torch.no_grad():
        pred = net(torch.from_numpy(Dte)).numpy()
    r2 = float(1 - np.sum((pred - Wte) ** 2) / np.sum((Wte - Wte.mean()) ** 2))
    round_acc = float((np.round(pred) == np.round(Wte)).mean())
    b1 = bool(r2 > 0.95 and round_acc == 1.0)

    # B2: gap-preserving deformation invariance + the gap-closing sweep
    grng = np.random.default_rng(5); defl = []
    for i in range(len(Dte)):
        v, w = VWte[i]; d = d_traj(v, w)
        k = np.linspace(0, 2 * np.pi, NK, endpoint=False)
        pert = 0.15 * min(v, w) * np.stack([np.sin(2 * k + grng.uniform(0, 6)), np.cos(3 * k + grng.uniform(0, 6))], 1)
        dd = d + pert                                            # small -> keeps |d|>0, winding preserved
        defl.append(unit(dd))
    with torch.no_grad():
        pred_def = net(torch.from_numpy(np.array(defl, np.float32))).numpy()
    deform_delta = float(np.mean(np.abs(np.round(pred_def) - np.round(pred))))
    # sweep v across w (gap closes at v=w)
    wfix = 1.0; vs = np.linspace(0.3, 1.7, 29)
    sweep = np.array([unit(d_traj(v, wfix)) for v in vs], np.float32)
    with torch.no_grad():
        sweep_w = net(torch.from_numpy(sweep)).numpy()
    below = np.round(sweep_w[vs < 0.95]).mean(); above = np.round(sweep_w[vs > 1.05]).mean()
    b2 = bool(deform_delta < 0.1 and abs(below - 1) < 0.1 and abs(above - 0) < 0.1)

    # B3: bulk-boundary correspondence -- bulk winding predicts open-chain edge modes (2*winding)
    bulk_pred_edges = (2 * np.round(pred)).astype(int)
    bb_acc = float((bulk_pred_edges == ECte).mean())
    b3 = bool(bb_acc > 0.95)

    out = {"B1_winding_R2": r2, "B1_round_accuracy": round_acc, "B2_deform_delta": deform_delta,
           "B2_sweep_below_vw": float(below), "B2_sweep_above_vw": float(above),
           "B3_bulk_boundary_accuracy": bb_acc,
           "B1_learns_invariant": b1, "B2_quantized_robust": b2, "B3_bulk_boundary": b3,
           "topological_invariant_discovered": bool(b1 and b2 and b3),
           "verdict": ("TOPOLOGICAL INVARIANT DISCOVERED: a DeepSets net reading the bulk SSH d(k) trajectory recovers "
                       "the WINDING NUMBER as a quantized integer (R2 {:.3f}, rounding accuracy {:.0%}) -- a holonomy "
                       "of the d-vector over the Brillouin zone. It is ROBUST to gap-preserving deformations "
                       "(|delta|={:.3f}) and flips 0<->1 only across the gap closing at v=w (below {:.1f}, above "
                       "{:.1f}). And the BULK winding predicts the BOUNDARY: 2*winding = open-chain zero-energy edge "
                       "modes for {:.0%} of configs (bulk-boundary correspondence). Ties AB (113, winding) + Berry "
                       "(54, curvature) + the certificate quantization."
                       .format(r2, round_acc, deform_delta, below, above, bb_acc)
                       if (b1 and b2 and b3) else "PARTIAL -- see numbers (honest).")}
    print(f"B1 learns invariant: winding R2={r2:.3f} (>0.95), round-acc={round_acc:.0%}: {b1}")
    print(f"B2 quantized/robust: deform delta={deform_delta:.3f} (<0.1); sweep below v=w ->{below:.1f}, above ->{above:.1f}: {b2}")
    print(f"B3 bulk-boundary: 2*winding == edge modes for {bb_acc:.0%} of configs: {b3}")
    print(f"\nTOPOLOGICAL INVARIANT DISCOVERED: {out['topological_invariant_discovered']}")
    (RESULTS / "117_topological_band.json").write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(1, 3, figsize=(15, 4.6))
    for v, w, c in [(0.5, 1.5, "seagreen"), (1.5, 0.5, "crimson")]:
        d = d_traj(v, w); ax[0].plot(np.append(d[:, 0], d[0, 0]), np.append(d[:, 1], d[0, 1]),
                                     color=c, label=f"v={v},w={w} (wind {int(round(winding(d)))})")
    ax[0].scatter([0], [0], c="k", marker="+", s=80); ax[0].set_aspect("equal"); ax[0].legend(fontsize=8)
    ax[0].set_title("B1 · d(k) over BZ\nwinding = encircles origin?"); ax[0].set_xlabel("d_x"); ax[0].set_ylabel("d_y")
    ax[1].plot(vs, sweep_w, "o-", color="slateblue"); ax[1].axvline(wfix, ls="--", c="k", lw=0.7)
    ax[1].set_xlabel("v  (w=1, gap closes at v=w)"); ax[1].set_ylabel("net winding")
    ax[1].set_title("B2 · quantized; flips only at gap closing")
    ax[2].scatter(np.round(pred), ECte, alpha=0.3, c="darkorange")
    ax[2].set_xlabel("net bulk winding"); ax[2].set_ylabel("open-chain edge modes")
    ax[2].set_title(f"B3 · bulk-boundary (acc {bb_acc:.0%})\nedges = 2 x winding")
    fig.suptitle("Topological band theory: a net discovers the SSH winding number + bulk-boundary correspondence")
    fig.tight_layout(); fig.savefig(RESULTS / "117_topological_band.png", dpi=140)
    print("saved results/117_topological_band.json + .png")


if __name__ == "__main__":
    main()
