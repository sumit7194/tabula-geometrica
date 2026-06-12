"""Step 09 — the interpretability side quest: find and STEER the stored q/m.

The charged-mix force model provably stores and uses each body's q/m, yet the
embedding hides it from PCA and linear probes. This script runs the full
interpretability ladder on the network's HIDDEN layers:

  probes    linear decode of qm from layer-1 / layer-2 activations, trained on
            24 bodies, tested on 8 held-out bodies (S1: linearization w/ depth)
  SAE       overcomplete sparse autoencoder on layer-2; per-feature correlation
            with qm and with the physically-used product qm*E(x) (S2)
  steering  add alpha * (qm-direction) to layer-2 mid-forward and measure the
            behaviorally-decoded effective q/m of the steered network (S3),
            against random-direction controls (S4)

Layer indexing for the force model's net = Sequential(Linear(6,128), Tanh,
Linear(128,128), Tanh, Linear(128,3)): "layer 1" = after first Tanh, "layer 2"
= after second Tanh.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import importlib.util
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import torch
from curvlib import E_CENTER, RESULTS, X_RANGE, V_MAX, e_field, integrate_trajectories, make_dynamics_dataset
from torch import nn

spec = importlib.util.spec_from_file_location(
    "train_dyn", Path(__file__).resolve().parent / "06_train_dynamics.py"
)
train_dyn = importlib.util.module_from_spec(spec)
spec.loader.exec_module(train_dyn)

rng = np.random.default_rng(11)


def forward_parts(frc, X, body, steer=None, steer_layer=2):
    """Manual forward pass exposing hidden activations; optionally add a
    steering vector to layer-1 or layer-2 activations."""
    z = torch.cat([X, frc.emb(body)], dim=1)
    h1 = torch.tanh(frc.net[0](z))
    if steer is not None and steer_layer == 1:
        h1 = h1 + steer
    h2 = torch.tanh(frc.net[2](h1))
    if steer is not None and steer_layer == 2:
        h2 = h2 + steer
    out = frc.net[4](h2)
    return h1, h2, out


class SAE(nn.Module):
    def __init__(self, d=128, m=512):
        super().__init__()
        self.enc = nn.Linear(d, m)
        self.dec = nn.Linear(m, d)

    def forward(self, h):
        f = torch.relu(self.enc(h))
        return f, self.dec(f)


def ridge_probe(H_tr, y_tr, H_te, y_te, lam=1e-2):
    A = np.concatenate([H_tr, np.ones((len(H_tr), 1))], axis=1)
    w = np.linalg.solve(A.T @ A + lam * np.eye(A.shape[1]), A.T @ y_tr)
    pred = np.concatenate([H_te, np.ones((len(H_te), 1))], axis=1) @ w
    return float(np.corrcoef(pred, y_te)[0, 1]), w[:-1]


_PROBE_CACHE = {}


def behavioral_qm(frc, body_id, steer_vec, alpha, steer_layer=2):
    """Effective q/m of the (possibly steered) network by trajectory inversion,
    plus the inversion RESIDUAL — how far the steered behavior sits from the
    physics manifold (any valid q/m trajectory). On-manifold steering = low
    residual; off-manifold damage = high residual."""
    n_probe = 16
    px = np.linspace(E_CENTER - 0.8, E_CENTER + 0.8, n_probe).astype(np.float32)
    pv = np.zeros(n_probe, dtype=np.float32)
    probe_X = torch.from_numpy(np.stack([px, pv], axis=1))
    if "ref" not in _PROBE_CACHE:
        qm_grid = np.linspace(-1.5, 1.5, 301)
        _PROBE_CACHE["qm_grid"] = qm_grid
        _PROBE_CACHE["ref"] = np.stack(
            [
                integrate_trajectories(px.astype(float), pv.astype(float), np.full(n_probe, q))
                for q in qm_grid
            ]
        )
    qm_grid, ref = _PROBE_CACHE["qm_grid"], _PROBE_CACHE["ref"]
    steer = None
    if steer_vec is not None:
        steer = torch.from_numpy((alpha * steer_vec).astype(np.float32)).expand(n_probe, -1)
    with torch.no_grad():
        _, _, pred = forward_parts(
            frc, probe_X, torch.full((n_probe,), int(body_id), dtype=torch.long), steer,
            steer_layer,
        )
    mses = ((ref - pred.numpy()) ** 2).mean(axis=(1, 2))
    i = int(np.argmin(mses))
    return float(qm_grid[i]), float(mses[i])


def main() -> None:
    meta = json.loads((RESULTS / "dyn_charged.json").read_text())
    qm_body = np.array(meta["qm_body"])
    frc = train_dyn.ForceModel(len(qm_body))
    frc.load_state_dict(torch.load(RESULTS / "dyn_charged_force.pt", weights_only=True))
    frc.eval()

    seen = np.setdiff1d(np.arange(len(qm_body)), np.array(meta["held_bodies"]))
    probe_tr, probe_te = seen[:24], seen[24:]

    # activation dataset: 500 random states per body
    per = 500
    rows = {"h1": [], "h2": [], "qm": [], "qmE": [], "body": []}
    for b in seen:
        x0 = rng.uniform(*X_RANGE, per).astype(np.float32)
        v0 = rng.uniform(-V_MAX, V_MAX, per).astype(np.float32)
        X = torch.from_numpy(np.stack([x0, v0], axis=1))
        with torch.no_grad():
            h1, h2, _ = forward_parts(frc, X, torch.full((per,), int(b), dtype=torch.long))
        rows["h1"].append(h1.numpy())
        rows["h2"].append(h2.numpy())
        rows["qm"].append(np.full(per, qm_body[b]))
        rows["qmE"].append(qm_body[b] * e_field(x0))
        rows["body"].append(np.full(per, b))
    H1 = np.concatenate(rows["h1"])
    H2 = np.concatenate(rows["h2"])
    QM = np.concatenate(rows["qm"])
    QME = np.concatenate(rows["qmE"])
    BODY = np.concatenate(rows["body"])

    tr = np.isin(BODY, probe_tr)
    te = np.isin(BODY, probe_te)

    # S1: linearization with depth (held-out-BODY evaluation)
    r_h1, w_qm1 = ridge_probe(H1[tr], QM[tr], H1[te], QM[te])
    r_h2, w_qm2 = ridge_probe(H2[tr], QM[tr], H2[te], QM[te])
    print(f"S1 linear decode of qm, held-out bodies:  layer-1 r = {r_h1:+.4f}   layer-2 r = {r_h2:+.4f}")
    print("   (embedding baseline from step 07: r = +0.02)")

    # S2: SAE on layer-2. First run (L1=3e-4) was too dense (L0=251) — recorded
    # in the notebook; this stronger penalty is the tuned probe, not a new claim.
    torch.manual_seed(0)
    sae = SAE()
    opt = torch.optim.Adam(sae.parameters(), lr=1e-3)
    H2_t = torch.from_numpy(H2[tr].astype(np.float32))
    for step in range(8000):
        idx = torch.from_numpy(rng.integers(0, len(H2_t), 1024))
        f, rec = sae(H2_t[idx])
        loss = ((rec - H2_t[idx]) ** 2).mean() + 3e-3 * f.abs().mean()
        opt.zero_grad()
        loss.backward()
        opt.step()
    with torch.no_grad():
        F_te, rec_te = sae(torch.from_numpy(H2[te].astype(np.float32)))
    F_te = F_te.numpy()
    alive = F_te.std(0) > 1e-6
    l0 = float((F_te > 1e-6).sum(1).mean())
    rec_r2 = 1 - ((rec_te.numpy() - H2[te]) ** 2).mean() / H2[te].var()

    def best_corr(target):
        cs = np.zeros(F_te.shape[1])
        cs[alive] = [abs(np.corrcoef(F_te[:, j], target)[0, 1]) for j in np.where(alive)[0]]
        return int(np.argmax(cs)), float(cs.max())

    j_qm, r_qm = best_corr(QM[te])
    j_qme, r_qme = best_corr(QME[te])
    print(f"S2 SAE (512 features, mean L0 = {l0:.1f}, {int(alive.sum())} alive, rec R² = {rec_r2:.3f}):")
    print(f"   best feature vs qm:        #{j_qm}  |r| = {r_qm:.4f}")
    print(f"   best feature vs qm*E(x):   #{j_qme}  |r| = {r_qme:.4f}")

    # S3/S4: steering with the on-manifold metric. corr(alpha, qm_eff) measures
    # systematic control; the inversion residual measures whether the steered
    # behavior is still valid physics-at-some-charge (low) or off-manifold
    # damage (high). Random directions are graded on BOTH.
    alphas = np.linspace(-6, 6, 13)
    neutral_seen = [b for b in seen if abs(qm_body[b]) < 1e-9]
    body0 = neutral_seen[0]  # steer a NEUTRAL body: cleanest "give it charge"

    results_steer = {}
    for layer, w in ((1, w_qm1), (2, w_qm2)):
        direction = w / np.linalg.norm(w)
        out = [behavioral_qm(frc, body0, direction, a, layer) for a in alphas]
        qms = [o[0] for o in out]
        res = [o[1] for o in out]
        results_steer[layer] = {
            "qms": qms,
            "corr": float(np.corrcoef(alphas, qms)[0, 1]),
            "range": float(max(qms) - min(qms)),
            "residual": float(np.median(res)),
        }
        print(f"S3 steering at layer-{layer}: qm_eff spans [{min(qms):+.2f}, {max(qms):+.2f}], "
              f"corr = {results_steer[layer]['corr']:+.4f}, median residual = {results_steer[layer]['residual']:.5f}")

    rand_corr, rand_res, rand_span = [], [], []
    for _ in range(8):
        rd = rng.normal(size=128)
        rd /= np.linalg.norm(rd)
        out = [behavioral_qm(frc, body0, rd, a, 1) for a in alphas]
        qms_r = [o[0] for o in out]
        rand_corr.append(abs(np.corrcoef(alphas, qms_r)[0, 1]))
        rand_res.append(np.median([o[1] for o in out]))
        rand_span.append(max(qms_r) - min(qms_r))
    print(f"S4 random directions (layer-1, equal norm): mean |corr| = {np.mean(rand_corr):.3f} "
          f"(vs qm-dir {abs(results_steer[1]['corr']):.3f}), "
          f"mean span = {np.mean(rand_span):.3f} (vs qm-dir {results_steer[1]['range']:.3f}), "
          f"median residual = {np.median(rand_res):.5f} "
          f"(vs qm-dir {results_steer[1]['residual']:.5f})")

    steered = results_steer[1]["qms"]
    r_steer = results_steer[1]["corr"]
    steer_range = results_steer[1]["range"]

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    axes[0].plot(alphas, results_steer[1]["qms"], "o-", color="crimson", label="layer-1 qm-direction")
    axes[0].plot(alphas, results_steer[2]["qms"], "s-", color="darkorange", alpha=0.7, label="layer-2 qm-direction")
    axes[0].axhline(0, color="gray", lw=0.5)
    axes[0].set_xlabel("steering strength α")
    axes[0].set_ylabel("behaviorally-decoded effective q/m")
    axes[0].set_title(
        f"steering a neutral body's charge\nlayer-1: corr = {r_steer:+.3f}, "
        f"span {steer_range:.2f}; random dirs |corr| = {np.mean(rand_corr):.2f}"
    )
    axes[0].legend()

    axes[1].bar(
        ["embedding\n(linear)", "layer-1\nprobe", "layer-2\nprobe", "SAE best\nvs qm", "SAE best\nvs qm·E(x)"],
        [0.02, abs(r_h1), abs(r_h2), r_qm, r_qme],
        color=["gray", "steelblue", "steelblue", "seagreen", "seagreen"],
    )
    axes[1].set_ylabel("|r| with target")
    axes[1].set_title("where q/m becomes readable\n(probe ladder across the network)")
    fig.tight_layout()
    out = RESULTS / "09_sae_steering.png"
    fig.savefig(out, dpi=140)
    print(f"plot -> {out}")

    (RESULTS / "09_sae_steering.json").write_text(
        json.dumps(
            {
                "S1_layer1_r": r_h1,
                "S1_layer2_r": r_h2,
                "S2_sae_l0": l0,
                "S2_rec_r2": float(rec_r2),
                "S2_best_qm": {"feature": j_qm, "abs_r": r_qm},
                "S2_best_qmE": {"feature": j_qme, "abs_r": r_qme},
                "S3_by_layer": results_steer,
                "S4_random": {"mean_abs_corr": float(np.mean(rand_corr)),
                              "mean_span": float(np.mean(rand_span)),
                              "median_residual": float(np.median(rand_res))},
                "alphas": alphas.tolist(),
            },
            indent=1,
        )
    )


if __name__ == "__main__":
    main()
