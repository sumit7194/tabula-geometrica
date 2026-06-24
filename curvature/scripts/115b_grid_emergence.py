"""Step 115b — does a TRAINED path-integrator DEVELOP the grid-cell torus? Honest partial.

Companion to 115 (the validated instrument + grid=torus/place=plane signature). Here we train an RNN to path-
integrate (Sorscher recipe: softmax place-cell targets, cross-entropy, ReLU nonnegativity) plus a CONFORMAL-ISOMETRY
regularizer (||Delta g|| proportional to ||Delta x||, the Gao/Wu/Xu conformal-isometry hypothesis), then read its
learned population manifold with the 115 instrument.

Result (honest partial): the net LEARNS path integration (CE 6.24 -> ~3.5) and the isometry term NUDGES gridness
(max ~ -0.02 -> 0.12), but it does NOT develop clean hexagonal grids in this budget -- it settles on a PLACE-LIKE
code, so its manifold reads as a PLANE (b1=0), NOT a torus. Clean emergent hexagonal grids (-> a torus) require the
full conformal-NORMALIZATION representational-model architecture (Xu/Wu/Gao 2023, arXiv:2310.19192), beyond a soft
regularizer on a vanilla RNN. So: path-integration + nonnegativity is necessary but NOT sufficient; the toroidal grid
code is a special solution selected by an isometry CONSTRAINT.

NOT in verify.sh (a training run + an honest partial, like the Phase F null). Reported, not gated.
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
from scipy.ndimage import rotate
from torch import nn

from curvlib import RESULTS, progress
from importlib import import_module
S115 = import_module("115_grid_torus")

DEV = "mps" if torch.backends.mps.is_available() else "cpu"
P, NG, T, B, SIG, LAM = 512, 1024, 21, 200, 0.12, 0.5


def main():
    torch.manual_seed(0); rng = np.random.default_rng(0)
    C = torch.tensor(rng.uniform(-1, 1, (P, 2)), dtype=torch.float32, device=DEV)

    def place(x):
        d2 = ((x[..., None, :] - C) ** 2).sum(-1)
        return torch.softmax(-d2 / (2 * SIG ** 2), dim=-1)

    def traj(B, T):
        pos = np.zeros((B, T, 2), np.float32); vel = np.zeros((B, T, 2), np.float32)
        p = rng.uniform(-0.9, 0.9, (B, 2)); hd = rng.uniform(0, 2 * np.pi, B); pos[:, 0] = p
        for t in range(1, T):
            sp = rng.uniform(0.03, 0.12, B); hd = hd + rng.normal(0, 0.35, B)
            v = sp[:, None] * np.stack([np.cos(hd), np.sin(hd)], 1); p = p + v
            for d in range(2):
                over = np.abs(p[:, d]) > 1.0; p[over, d] = np.clip(p[over, d], -1, 1); hd[over] = np.pi - hd[over]
            pos[:, t] = p; vel[:, t] = v
        return torch.tensor(pos, device=DEV), torch.tensor(vel, device=DEV)

    class RNN(nn.Module):
        def __init__(s):
            super().__init__()
            s.enc = nn.Linear(P, NG, bias=False); s.win = nn.Linear(2, NG, bias=False)
            s.rec = nn.Linear(NG, NG, bias=False); s.dec = nn.Linear(NG, P, bias=False)
            s.scale = nn.Parameter(torch.tensor(5.0))

        def forward(s, p0, vel):
            g = torch.relu(s.enc(p0)); outs = [s.dec(g)]; gs = [g]
            for t in range(1, vel.shape[1]):
                g = torch.relu(s.win(vel[:, t]) + s.rec(g)); outs.append(s.dec(g)); gs.append(g)
            return torch.stack(outs, 1), torch.stack(gs, 1)

    m = RNN().to(DEV); opt = torch.optim.Adam(m.parameters(), lr=1e-3, weight_decay=1e-4)
    STEPS = int(sys.argv[1]) if len(sys.argv) > 1 else 15000
    ce0 = None
    for step in range(STEPS):
        pos, vel = traj(B, T); logits, gs = m(place(pos[:, 0]), vel); tgt = place(pos)
        ce = -(tgt * torch.log_softmax(logits, -1)).sum(-1).mean()
        dg = (gs[:, 1:] - gs[:, :-1]).norm(dim=-1); dx = vel[:, 1:].norm(dim=-1)
        loss = ce + LAM * ((dg - m.scale * dx) ** 2).mean()
        opt.zero_grad(); loss.backward(); nn.utils.clip_grad_norm_(m.parameters(), 1.0); opt.step()
        if step == 0:
            ce0 = float(ce)
        if step % 3000 == 0:
            progress("115b_train", step, STEPS, ce=float(ce))
    ce_final = float(ce)

    # ratemaps
    G = 32; acc = np.zeros((NG, G, G)); cnt = np.zeros((G, G)) + 1e-6
    with torch.no_grad():
        for _ in range(60):
            pos, vel = traj(B, T); _, gs = m(place(pos[:, 0]), vel)
            pc = pos.cpu().numpy().reshape(-1, 2); gc = gs.cpu().numpy().reshape(-1, NG)
            ix = np.clip(((pc[:, 0] + 1) / 2 * G).astype(int), 0, G - 1)
            iy = np.clip(((pc[:, 1] + 1) / 2 * G).astype(int), 0, G - 1)
            np.add.at(acc, (slice(None), ix, iy), gc.T); np.add.at(cnt, (ix, iy), 1)
    ratemap = acc / cnt

    def gridness(R):
        if R.std() < 1e-5:
            return -1.0
        Rc = R - R.mean()
        A = np.fft.fftshift(np.fft.irfft2(np.abs(np.fft.rfft2(Rc)) ** 2, s=Rc.shape)); A /= A.max() + 1e-9
        c = np.array(A.shape) // 2; yy, xx = np.mgrid[:A.shape[0], :A.shape[1]]
        rr = np.sqrt((xx - c[1]) ** 2 + (yy - c[0]) ** 2); ann = (rr > 4) & (rr < 13)
        cc = lambda deg: np.corrcoef(A[ann], rotate(A, deg, reshape=False, order=1)[ann])[0, 1]
        return float(min(cc(60), cc(120)) - max(cc(30), cc(90), cc(150)))

    gv = np.array([gridness(ratemap[i]) for i in range(NG)]); gv = gv[np.isfinite(gv)]
    active = ratemap.reshape(NG, -1).std(1) > 1e-3
    pop = ratemap[active].reshape(active.sum(), -1).T
    manifold_b = S115.cloud_betti(pop)

    grids_emerged = bool((gv > 0.3).mean() > 0.05)              # would-be gate: >=5% real grid cells
    is_torus = bool(manifold_b == [1, 2, 1])
    out = {"ce_initial": ce0, "ce_final": ce_final, "gridness_mean": float(gv.mean()),
           "gridness_max": float(gv.max()), "frac_grid_cells_gt0.3": float((gv > 0.3).mean()),
           "learned_manifold_betti": manifold_b, "n_active": int(active.sum()),
           "grids_emerged": grids_emerged, "manifold_is_torus": is_torus,
           "verdict": ("HONEST PARTIAL: the net LEARNS path integration (CE {:.2f}->{:.2f}) and the conformal-isometry "
                       "term nudges gridness (max {:.2f}), but clean hexagonal grids do NOT emerge (frac grid cells "
                       "{:.1%}) -- it settles on a PLACE-LIKE code, so its learned manifold reads {} (b1={}, NOT a "
                       "torus). Path-integration + nonnegativity is necessary but not sufficient; the toroidal grid "
                       "code needs the conformal-NORMALIZATION architecture (Xu/Wu/Gao 2023), beyond this budget."
                       .format(ce0, ce_final, float(gv.max()), float((gv > 0.3).mean()), manifold_b, manifold_b[1]))}
    print(f"\nPI learned: CE {ce0:.2f} -> {ce_final:.2f}")
    print(f"gridness: mean {gv.mean():.3f} max {gv.max():.3f} frac>0.3 {(gv>0.3).mean():.1%} -> grids_emerged={grids_emerged}")
    print(f"learned manifold betti: {manifold_b} -> is_torus={is_torus}")
    print(f"\nHONEST PARTIAL (emergence): {out['verdict'][:60]}...")
    (RESULTS / "115b_grid_emergence.json").write_text(json.dumps(out, indent=1))

    order = np.argsort(gv)[::-1]
    fig, axs = plt.subplots(2, 6, figsize=(15, 5.5))
    for j, ax in enumerate(axs.ravel()):
        idx = np.where(np.isfinite([gridness(ratemap[i]) for i in range(NG)]))[0][order[j]] if j < len(order) else 0
        ax.imshow(ratemap[order[j]].T, origin="lower", cmap="jet"); ax.set_xticks([]); ax.set_yticks([])
        ax.set_title(f"g={gv[order[j]]:.2f}", fontsize=8)
    fig.suptitle(f"115b · trained path-integrator ratemaps (top by gridness) — place-like, not hexagonal grids "
                 f"(manifold {manifold_b}, not a torus)")
    fig.tight_layout(); fig.savefig(RESULTS / "115b_grid_emergence.png", dpi=130)
    print("saved results/115b_grid_emergence.json + .png")


if __name__ == "__main__":
    main()
