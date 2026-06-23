"""Step 107 — cracking the 1-D boundary mystery: is OUTPUT RICHNESS the variable that flips D=1 legibility?

The puzzle: SAME linear coupling, SAME free per-object embedding, OPPOSITE outcome --
  - script 48 (physics, TRAJECTORY output, cdim 4): free D=1 LEGIBLE (0.86)
  - scripts 104/105 (abstract, SCALAR output): free D=1 SCRAMBLED (0.19-0.30)
Capacity was refuted (105, non-monotonic). The remaining suspect is the OUTPUT structure: a scalar target lets the
free embedding encode the 1-D property however it likes (scramble); a rich/high-dim target where the property
modulates MANY outputs linearly should FORCE the embedding to align with the property linearly (legible).

Controlled isolation (one harness, faithful to script 35; ONLY the output dimension OUT varies):
  property p in R^D (D=1); free per-object embedding (fixed cdim=16); world outputs R^OUT.
  LINEAR world:  y = base(x) + sum_k p_k * coup_k(x),  base/coup: R^XDIM -> R^OUT  (p enters linearly)
  GENERIC world: y = randMLP([p, x]) in R^OUT                                        (p enters nonlinearly)
Sweep OUT in {1,2,4,8,16,64} (scalar -> 'trajectory'), decode p from the free embedding (Ridge=legible, kNN=info).

Pre-reg (2026-06-23):
  L1 HARNESS VALID: linear world, D=1, OUT=1 free linear-decode < 0.55 (reproduces the 104/105 scalar scramble).
  L2 RICHNESS FLIPS IT: linear world D=1 free linear-decode RISES with OUT and is legible at OUT=64 (> 0.7).
  L3 EXPLAINS 48-vs-104: the rise is the mechanism -- a trajectory (high OUT) is legible, a scalar (OUT=1) scrambles,
     at identical coupling+capacity. (Contrast: does richness also rescue the GENERIC world?)
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
from sklearn.linear_model import Ridge
from sklearn.neighbors import KNeighborsRegressor
from sklearn.model_selection import cross_val_predict
from torch import nn

XDIM, CDIM, WIDTH, N_OBJ, PER_OBJ, STEPS = 4, 16, 128, 256, 64, 6000


def randnet(din, dout, gen):
    net = nn.Sequential(nn.Linear(din, WIDTH), nn.GELU(), nn.Linear(WIDTH, WIDTH), nn.GELU(), nn.Linear(WIDTH, dout))
    with torch.no_grad():
        for p in net.parameters():
            p.copy_(torch.randn(p.shape, generator=gen) * 0.7)
    return net.eval()


def make_world(kind, D, OUT, seed):
    gen = torch.Generator().manual_seed(2000 + seed)
    if kind == "linear":
        base = randnet(XDIM, OUT, gen); coup = [randnet(XDIM, OUT, gen) for _ in range(D)]

        def world(p, x):
            with torch.no_grad():
                y = base(x)
                for k in range(D):
                    y = y + p[:, k:k + 1] * coup[k](x)
            return y
    else:
        net = randnet(XDIM + D, OUT, gen)

        def world(p, x):
            with torch.no_grad():
                return net(torch.cat([p, x], 1))
    return world


def make_data(kind, D, OUT, seed):
    rng = np.random.default_rng(seed); world = make_world(kind, D, OUT, seed)
    P = rng.uniform(-1, 1, (N_OBJ, D)).astype(np.float32)
    body, X, Y = [], [], []
    for i in range(N_OBJ):
        x = rng.uniform(-1, 1, (PER_OBJ, XDIM)).astype(np.float32)
        y = world(torch.from_numpy(np.tile(P[i], (PER_OBJ, 1))), torch.from_numpy(x)).numpy()
        body.append(np.full(PER_OBJ, i)); X.append(x); Y.append(y)
    return P, np.concatenate(body).astype(np.int64), np.concatenate(X), np.concatenate(Y).astype(np.float32)


class Free(nn.Module):
    def __init__(self, OUT):
        super().__init__()
        self.emb = nn.Embedding(N_OBJ, CDIM)
        self.head = nn.Sequential(nn.Linear(XDIM + CDIM, WIDTH), nn.GELU(), nn.Linear(WIDTH, WIDTH), nn.GELU(),
                                  nn.Linear(WIDTH, OUT))

    def forward(self, idx, x):
        return self.head(torch.cat([x, self.emb(idx)], 1))


def run(kind, D, OUT, seed):
    P, body, X, Y = make_data(kind, D, OUT, seed)
    Xt = torch.from_numpy(X); Yt = torch.from_numpy(Y); bt = torch.from_numpy(body)
    torch.manual_seed(seed); rng = np.random.default_rng(seed)
    m = Free(OUT); opt = torch.optim.Adam(m.parameters(), lr=2e-3)
    for step in range(STEPS):
        idx = rng.integers(0, len(X), 256)
        loss = nn.functional.mse_loss(m(bt[idx], Xt[idx]), Yt[idx])
        opt.zero_grad(); loss.backward(); opt.step()
        if step % 2000 == 0:
            progress(f"107_{kind}_O{OUT}_s{seed}", step, STEPS, loss=float(loss.detach()))
    with torch.no_grad():
        C = m.emb(torch.arange(N_OBJ)).numpy()
    lin = float(np.mean([np.corrcoef(cross_val_predict(Ridge(1.0), C, P[:, j], cv=5), P[:, j])[0, 1] for j in range(D)]))
    nl = float(np.mean([np.corrcoef(cross_val_predict(KNeighborsRegressor(8), C, P[:, j], cv=5), P[:, j])[0, 1] for j in range(D)]))
    return lin, nl


def agg(kind, OUT, seeds, D=1):
    rs = [run(kind, D, OUT, s) for s in seeds]
    return float(np.mean([r[0] for r in rs])), float(np.std([r[0] for r in rs])), float(np.mean([r[1] for r in rs]))


def main():
    OUTS = [1, 2, 4, 8, 16, 64]; seeds = [0, 1, 2]
    lin = {o: agg("linear", o, seeds) for o in OUTS}
    gen = {o: agg("generic", o, seeds) for o in (1, 64)}
    for o in OUTS:
        print(f"linear  OUT={o:2d}: linear {lin[o][0]:.3f}±{lin[o][1]:.2f} | kNN {lin[o][2]:.3f}")
    for o in (1, 64):
        print(f"generic OUT={o:2d}: linear {gen[o][0]:.3f} | kNN {gen[o][2]:.3f}")

    l1 = bool(lin[1][0] < 0.55)
    l2 = bool(lin[64][0] > 0.7 and lin[64][0] - lin[1][0] > 0.2)
    l3 = bool(l1 and l2)
    out = {"OUTS": OUTS, "seeds": seeds,
           "linear": {o: {"linear_r": lin[o][0], "std": lin[o][1], "knn": lin[o][2]} for o in OUTS},
           "generic": {o: {"linear_r": gen[o][0], "knn": gen[o][2]} for o in (1, 64)},
           "L1_harness_reproduces_scalar_scramble": l1, "L2_richness_flips_to_legible": l2,
           "L3_output_richness_explains_divergence": l3,
           "verdict": (f"OUTPUT RICHNESS is the flip variable: at fixed linear coupling + capacity, a free D=1 code is "
                       f"SCRAMBLED for a scalar output (OUT=1 linear {lin[1][0]:.2f}) and LEGIBLE for a rich output "
                       f"(OUT=64 linear {lin[64][0]:.2f}). This explains 48-vs-104: a trajectory is a high-dim output "
                       f"that forces the embedding to align linearly with the property; a scalar does not. Generic "
                       f"coupling at OUT=64 = {gen[64][0]:.2f} ({'also rescued' if gen[64][0]>0.7 else 'still scrambled'})."
                       if l3 else "Output richness does NOT cleanly explain the flip -- see numbers (honest).")}
    print(f"\nL1 harness reproduces scalar scramble (OUT=1 {lin[1][0]:.2f}<0.55): {l1}")
    print(f"L2 richness flips to legible (OUT=64 {lin[64][0]:.2f}>0.7, rise>0.2): {l2}")
    print(f"L3 output richness explains the 48-vs-104 divergence: {l3}")
    (RESULTS / "107_output_richness.json").write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(figsize=(7.5, 5))
    ax.plot(OUTS, [lin[o][0] for o in OUTS], "o-", color="seagreen", label="linear coupling (legibility)")
    ax.plot(OUTS, [lin[o][2] for o in OUTS], "o--", color="gray", lw=1, label="linear coupling (kNN/info)")
    ax.plot([1, 64], [gen[1][0], gen[64][0]], "s-", color="crimson", label="generic coupling")
    ax.axhline(0.55, ls=":", c="k", lw=0.6); ax.set_xscale("log", base=2); ax.set_xticks(OUTS)
    ax.get_xaxis().set_major_formatter(plt.matplotlib.ticker.ScalarFormatter())
    ax.set_xlabel("output dimensionality OUT (scalar → 'trajectory')"); ax.set_ylabel("free D=1 decode r")
    ax.set_ylim(0, 1); ax.legend(fontsize=8)
    ax.set_title("the 1-D mystery: output richness flips free D=1 legibility\n(scalar scrambles; rich/trajectory output is legible — at fixed coupling+capacity)")
    fig.tight_layout(); fig.savefig(RESULTS / "107_output_richness.png", dpi=140)
    print("saved results/107_output_richness.json + .png")


if __name__ == "__main__":
    main()
