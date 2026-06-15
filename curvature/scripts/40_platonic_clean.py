"""Step 40 — the CLEAN Platonic test (fixes edge (b)'s input-distinguishability confound).

Edge (b)/script 37 found independent generalists agree on the family map (ARI 0.92), but an
UNTRAINED net already clusters families at 0.54 because the families are input-distinguishable —
so convergence was real (0.54->0.92) yet partly input-driven, not cleanly platonic.

Clean version: make the thing they converge on a LATENT that is NOT in any input. Reuse script 35's
abstract task — each object has a hidden property p in R^PDIM, and a FROZEN random world g(p,x)->y.
p never appears in the data; it is only recoverable by LEARNING to invert g. So:
  - independent AMORTIZED learners (different init AND width, same objects) should converge on the
    same internal code for p -> cross-net CCA high, and both recover the true p (the platonic object);
  - an UNTRAINED encoder cannot recover p (it can't invert g) -> cross-net CCA at the random-subspace
    floor, recover-p ~0. This is the honest control the family test lacked;
  - FREE per-object embeddings (no shared encoder) scramble (the legibility law) -> should NOT
    converge to the latent linearly either. A second contrast.

Gates (pre-reg 2026-06-16):
  P1 amortized recover-p > 0.8 AND cross-net CCA clearly above untrained -> learned convergence.
  P2 untrained recover-p < 0.4 -> the latent needs learning (confound removed).
  P3 amortized cross-net CCA > free cross-net CCA -> convergence is a property of shared inference.
Resumable: each net's per-object code cached to .npy.
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
from sklearn.linear_model import Ridge
from sklearn.model_selection import cross_val_predict
from torch import nn

s35 = import_module("35_legibility_scale")
XDIM, PDIM, KEX = s35.XDIM, s35.PDIM, s35.KEX
N_OBJ, PER_OBJ, STEPS = 256, 64, 12000  # fix round: 6k left codes under-converged (recover_p 0.77<0.8)
CONFIGS = [(96, 11), (128, 22), (160, 33)]  # (width, seed) — different capacities, same objects


def train_code(world, d, width, seed, mode):
    """Train one learner (amortized or free) and return its per-object code (n_obj, cdim)."""
    ex, qx, qy = d["ex"], d["qx"], d["qy"]
    torch.manual_seed(seed); rng = np.random.default_rng(seed)
    m = s35.Learner(N_OBJ, width, mode); opt = torch.optim.Adam(m.parameters(), lr=2e-3)
    for step in range(STEPS):
        idx = torch.tensor(rng.integers(0, N_OBJ, 128))
        loss = nn.functional.mse_loss(m(ex, idx, qx[idx]), qy[idx])
        opt.zero_grad(); loss.backward(); opt.step()
        if step % 500 == 0:
            progress(f"40_{mode}_w{width}", step, STEPS, loss=float(loss.detach()))
    m.eval()
    with torch.no_grad():
        return m.code(ex, torch.arange(N_OBJ)).numpy()


def untrained_code(d, width, seed):
    torch.manual_seed(seed)
    m = s35.Learner(N_OBJ, width, "amortized"); m.eval()
    with torch.no_grad():
        return m.code(d["ex"], torch.arange(N_OBJ)).numpy()


def cca_mean(X, Y, k):
    """Mean of the top-k canonical correlations between feature matrices X, Y (rows = objects).
    SVD-based: canonical corrs = singular values of Ux^T Uy where U = left singular vectors."""
    X = X - X.mean(0); Y = Y - Y.mean(0)
    Ux = np.linalg.svd(X, full_matrices=False)[0]
    Uy = np.linalg.svd(Y, full_matrices=False)[0]
    s = np.linalg.svd(Ux.T @ Uy, compute_uv=False)
    return float(np.mean(np.clip(s[:k], 0, 1)))


def recovered_phat(C, P):
    """Each net's linear readout of the latent (cross-val predicted, per dim)."""
    return np.stack([cross_val_predict(Ridge(1.0), C, P[:, j], cv=5) for j in range(PDIM)], 1)


def recover_p(C, P):
    ph = recovered_phat(C, P)
    return float(np.mean([np.corrcoef(ph[:, j], P[:, j])[0, 1] for j in range(PDIM)]))


def latent_agreement(Cs, P):
    """Confound-free convergence: do independent nets recover the SAME latent object-by-object?
    (Raw-code CCA is input-confounded — even untrained nets share input-driven directions.)"""
    phs = [recovered_phat(C, P) for C in Cs]
    iu = [(i, j) for i in range(len(Cs)) for j in range(i + 1, len(Cs))]
    return float(np.mean([np.corrcoef(phs[i][:, d], phs[j][:, d])[0, 1] for i, j in iu for d in range(PDIM)]))


def codes_for(world, d, mode):
    Cs = []
    for (width, seed) in CONFIGS:
        sp = RESULTS / f"40_code_{mode}_w{width}_s{seed}.npy"
        if sp.exists():
            C = np.load(sp); print(f"  [resume] {mode} w{width} s{seed}: cached")
        else:
            C = untrained_code(d, width, seed) if mode == "untrained" else train_code(world, d, width, seed, mode)
            np.save(sp, C); print(f"  {mode} w{width} s{seed}: code saved")
        Cs.append(C)
    return Cs


def summarize(Cs, P):
    iu = [(i, j) for i in range(len(Cs)) for j in range(i + 1, len(Cs))]
    cca = float(np.mean([cca_mean(Cs[i], Cs[j], PDIM) for i, j in iu]))  # DIAGNOSTIC (input-confounded)
    rp = float(np.mean([recover_p(C, P) for C in Cs]))
    return {"latent_agreement": latent_agreement(Cs, P), "recover_p": rp, "cross_net_cca_diagnostic": cca}


def main():
    world = s35.World(width=128, seed=7)
    d = s35.make_data(world, N_OBJ, PER_OBJ, seed=0)
    P = d["P"]

    res = {}
    for mode in ("amortized", "free", "untrained"):
        print(f"\n=== {mode} ===")
        res[mode] = summarize(codes_for(world, d, mode), P)
        print(f"  latent-agreement = {res[mode]['latent_agreement']:.3f} | recover true p = "
              f"{res[mode]['recover_p']:.3f} | (CCA diag {res[mode]['cross_net_cca_diagnostic']:.3f})")

    a, f, u = res["amortized"], res["free"], res["untrained"]
    # convergence metric = latent_agreement (confound-free); CCA kept only as a diagnostic because
    # raw-code CCA aligns on input-driven directions even UNTRAINED (~1.0) — the edge-(b) inflation.
    p1 = bool(a["recover_p"] > 0.8 and a["latent_agreement"] > u["latent_agreement"] + 0.3)
    p2 = bool(u["recover_p"] < 0.4)
    p3 = bool(a["latent_agreement"] > f["latent_agreement"])
    res["P1_learned_convergence"] = p1
    res["P2_confound_removed"] = p2
    res["P3_convergence_is_shared_inference"] = p3
    res["clean_platonic_confirmed"] = bool(p1 and p2 and p3)
    res["note_cca_confounded"] = ("cross_net_cca is input-confounded: untrained ~1.0 because random "
                                  "encoders of the SAME inputs share input-driven directions. Use "
                                  "latent_agreement (cross-net recovery of the non-input latent).")
    print(f"\nP1 amortized recovers latent (>0.8) & agrees across nets (>untrained+0.3): {p1}")
    print(f"P2 untrained can't recover the latent (recover<0.4 = confound removed): {p2}")
    print(f"P3 amortized agreement > free agreement (convergence needs shared inference): {p3}")
    print(f"CLEAN PLATONIC: {res['clean_platonic_confirmed']}")
    (RESULTS / "40_platonic_clean.json").write_text(json.dumps(res, indent=1))

    modes = ["amortized", "free", "untrained"]
    x = np.arange(3)
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.bar(x - 0.2, [res[m]["latent_agreement"] for m in modes], 0.4, label="latent agreement (convergence)", color="steelblue")
    ax.bar(x + 0.2, [res[m]["recover_p"] for m in modes], 0.4, label="recover true latent p", color="seagreen")
    ax.set_xticks(x); ax.set_xticklabels(modes); ax.set_ylim(0, 1); ax.legend()
    ax.set_title("Clean Platonic: do independent nets converge on a LEARNED latent?")
    fig.tight_layout(); fig.savefig(RESULTS / "40_platonic_clean.png", dpi=140)
    print("saved results/40_platonic_clean.json + .png")


if __name__ == "__main__":
    main()
