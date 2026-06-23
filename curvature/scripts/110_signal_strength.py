"""Step 110 — capstone for the 1-D mystery: is the property's SIGNAL STRENGTH the knob for free-code legibility?

109 showed the TARGET FUNCTION drives the free-code scramble (s35 default-init world scrambles 0.25; a large-weight
world is legible 0.78), at identical learner/capacity/batching. The plausible mechanism: how strongly the property
is expressed in the observations. This isolates exactly that -- scale ONLY the property's contribution, holding the
base function and everything else fixed:

    y = base(x) + alpha * p * coup(x)          (base, coup frozen; alpha = property signal strength)

Sweep alpha; D=1, OUT=1, free per-object code (the s35 regime). Decode p from the free embedding (Ridge=legible,
kNN=info present). Prediction: linear legibility RISES with alpha -- weak signal scrambles (or hides), strong signal
is legible -- turning '109's target-dependence into a measured one-knob mechanism.

Pre-reg (2026-06-23):
  M1 SIGNAL STRENGTH IS THE KNOB: linear decode rises with alpha and (legible at large alpha > 0.7) - (small alpha)
     > 0.3, i.e. a monotone-ish climb from scrambled/weak to legible.
  M2 SCRAMBLE vs NO-INFO: report kNN -- distinguishes a true scramble (kNN high, linear low) from info-absent
     (both low) in the weak-signal regime.
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
from importlib import import_module

s107 = import_module("107_output_richness")
N_OBJ, PER_OBJ, XDIM, CDIM, STEPS = s107.N_OBJ, s107.PER_OBJ, s107.XDIM, s107.CDIM, s107.STEPS


def make_data(alpha, seed):
    gen = torch.Generator().manual_seed(2000 + seed)
    base = s107.randnet(XDIM, 1, gen); coup = s107.randnet(XDIM, 1, gen)   # frozen base + coupling (x0.7)
    rng = np.random.default_rng(seed)
    P = rng.uniform(-1, 1, (N_OBJ, 1)).astype(np.float32)
    body, X, Y = [], [], []
    with torch.no_grad():
        for i in range(N_OBJ):
            x = rng.uniform(-1, 1, (PER_OBJ, XDIM)).astype(np.float32)
            xt = torch.from_numpy(x)
            y = (base(xt) + alpha * float(P[i, 0]) * coup(xt)).numpy()      # (PER_OBJ,1); ONLY p's effect scaled
            body.append(np.full(PER_OBJ, i)); X.append(x); Y.append(y)
    return P, np.concatenate(body).astype(np.int64), np.concatenate(X), np.concatenate(Y).astype(np.float32)


def run(alpha, seed):
    P, body, X, Y = make_data(alpha, seed)
    Xr = torch.from_numpy(X.reshape(N_OBJ, PER_OBJ, XDIM)); Yr = torch.from_numpy(Y.reshape(N_OBJ, PER_OBJ, 1))
    torch.manual_seed(seed); rng = np.random.default_rng(seed)
    m = s107.Free(1); opt = torch.optim.Adam(m.parameters(), lr=2e-3)
    for step in range(STEPS):
        ob = rng.integers(0, N_OBJ, 32)                                    # per-object batching (s35 regime)
        emb = m.emb(torch.from_numpy(ob))[:, None, :].expand(-1, PER_OBJ, -1)
        loss = nn.functional.mse_loss(m.head(torch.cat([Xr[ob], emb], -1)), Yr[ob])
        opt.zero_grad(); loss.backward(); opt.step()
        if step % 2000 == 0:
            progress(f"110_a{alpha}_s{seed}", step, STEPS, loss=float(loss.detach()))
    with torch.no_grad():
        C = m.emb(torch.arange(N_OBJ)).numpy()
    lin = float(np.corrcoef(cross_val_predict(Ridge(1.0), C, P[:, 0], cv=5), P[:, 0])[0, 1])
    nl = float(np.corrcoef(cross_val_predict(KNeighborsRegressor(8), C, P[:, 0], cv=5), P[:, 0])[0, 1])
    return lin, nl


def main():
    alphas = [0.05, 0.15, 0.4, 1.0, 2.5]; seeds = [0, 1, 2]
    R = {}
    for a in alphas:
        rs = [run(a, s) for s in seeds]
        R[a] = (float(np.mean([r[0] for r in rs])), float(np.std([r[0] for r in rs])), float(np.mean([r[1] for r in rs])))
        print(f"alpha={a:5.2f}: linear {R[a][0]:.3f}±{R[a][1]:.2f} | kNN {R[a][2]:.3f}")

    lo, hi = R[alphas[0]][0], R[alphas[-1]][0]
    m1 = bool(hi > 0.7 and hi - lo > 0.3)
    out = {"alphas": alphas, "seeds": seeds,
           "results": {a: {"linear": R[a][0], "std": R[a][1], "knn": R[a][2]} for a in alphas},
           "M1_signal_strength_is_the_knob": m1,
           "verdict": (f"SIGNAL STRENGTH IS THE KNOB: free D=1 linear legibility climbs from {lo:.2f} (weak signal, "
                       f"alpha={alphas[0]}) to {hi:.2f} (strong signal, alpha={alphas[-1]}) as ONLY the property's "
                       f"effect on the output is scaled (base fixed). Confirms 109's target-dependence is, "
                       f"mechanistically, the property's signal strength in the observations." if m1 else
                       f"Signal strength does NOT cleanly explain it (alpha {alphas[0]}->{alphas[-1]}: linear "
                       f"{lo:.2f}->{hi:.2f}) -- honest; see kNN to tell scramble from info-absent.")}
    print(f"\nM1 signal strength is the knob (alpha {alphas[0]} {lo:.2f} -> {alphas[-1]} {hi:.2f}, rise>0.3): {m1}")
    (RESULTS / "110_signal_strength.json").write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(figsize=(7.5, 5))
    ax.plot(alphas, [R[a][0] for a in alphas], "o-", color="seagreen", label="linear (legibility)")
    ax.plot(alphas, [R[a][2] for a in alphas], "s--", color="gray", lw=1, label="kNN (info present)")
    ax.axhline(0.55, ls=":", c="k", lw=0.6); ax.set_xscale("log"); ax.set_xticks(alphas)
    ax.get_xaxis().set_major_formatter(plt.matplotlib.ticker.ScalarFormatter())
    ax.set_xlabel("property signal strength  α  (scales ONLY p's effect on the output)")
    ax.set_ylabel("free D=1 decode r"); ax.set_ylim(0, 1); ax.legend(fontsize=8)
    ax.set_title("capstone: the property's signal strength is the knob for free-code legibility\n(weak signal scrambles; strong signal is legible — base function fixed)")
    fig.tight_layout(); fig.savefig(RESULTS / "110_signal_strength.png", dpi=140)
    print("saved results/110_signal_strength.json + .png")


if __name__ == "__main__":
    main()
