"""Step 07 — the economy gates: which explanation is cheaper, and what did the
embeddings discover?

For each trained mix:
  E1 head-to-head test MSE (geometry vs force) per body class
  E2 the SWAP TEST — permute body embeddings and re-measure the force model's
     error. If identity is irrelevant (gravity), swapping changes nothing; if
     identity matters (charge), swapping is catastrophic. Identity-relevance,
     measured behaviorally.
  E3 the embedding portrait — PCA of the per-body embeddings. Prediction:
     neutral mix -> a collapsed blob (the equivalence principle, visible in
     embedding space); charged mix -> spread along ONE axis whose coordinate is
     the body's q/m (the net discovers charge-to-mass ratio as the single
     number that matters).
  E4 zero-shot — the geometry model on held-out bodies it never saw.
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
from curvlib import RESULTS, make_dynamics_dataset
from torch import nn

spec = importlib.util.spec_from_file_location(
    "train_dyn", Path(__file__).resolve().parent / "06_train_dynamics.py"
)
train_dyn = importlib.util.module_from_spec(spec)
spec.loader.exec_module(train_dyn)


def mse_by_class(model, split, qm_body, body_override=None):
    body, X, Y = split
    b = body if body_override is None else body_override
    with torch.no_grad():
        pred = model(torch.from_numpy(X), torch.from_numpy(b))
        err = ((pred - torch.from_numpy(Y)) ** 2).mean(dim=1).numpy()
    charged = np.abs(qm_body[body]) > 1e-9
    out = {"all": float(err.mean())}
    if charged.any():
        out["charged"] = float(err[charged].mean())
    if (~charged).any():
        out["neutral"] = float(err[~charged].mean())
    return out


def main() -> None:
    mix = sys.argv[1] if len(sys.argv) > 1 else "neutral"
    meta = json.loads((RESULTS / f"dyn_{mix}.json").read_text())
    qm_body = np.array(meta["qm_body"])
    data = make_dynamics_dataset(mix, seed=meta["seed"])
    n_bodies = len(qm_body)

    geo = train_dyn.GeometryModel()
    geo.load_state_dict(torch.load(RESULTS / f"dyn_{mix}_geometry.pt", weights_only=True))
    geo.eval()
    frc = train_dyn.ForceModel(n_bodies)
    frc.load_state_dict(torch.load(RESULTS / f"dyn_{mix}_force.pt", weights_only=True))
    frc.eval()

    print(f"=== mix: {mix} ===")
    e1_geo = mse_by_class(geo, data["test"], qm_body)
    e1_frc = mse_by_class(frc, data["test"], qm_body)
    print(f"E1 test MSE  geometry: {e1_geo}")
    print(f"E1 test MSE  force:    {e1_frc}")

    # E2: permute embeddings among seen bodies (held-out bodies excluded)
    rng = np.random.default_rng(7)
    seen = np.setdiff1d(np.arange(n_bodies), np.array(meta["held_bodies"]))
    perm_map = dict(zip(seen, rng.permutation(seen)))
    body, _, _ = data["test"]
    body_sw = np.array([perm_map[b] for b in body], dtype=np.int64)
    e2 = mse_by_class(frc, data["test"], qm_body, body_override=body_sw)
    print(f"E2 swap test force MSE: {e2}  (vs unswapped {e1_frc})")

    # E3: embedding portrait. Raw PCA is swamped by leftover init noise (the
    # optimizer only shapes directions it has gradients for), so the honest
    # probe is DECODABILITY: leave-one-out linear readout of q/m from the
    # embedding — the standard probing lesson, variance ≠ information.
    emb = frc.emb.weight.detach().numpy()[seen]
    embc = emb - emb.mean(0)
    _, s, v = np.linalg.svd(embc, full_matrices=False)
    evr = s**2 / (s**2).sum()
    qm_seen = qm_body[seen]
    spread = float(np.linalg.norm(embc, axis=1).mean())
    print(f"E3 embedding spread (mean |e − ē|): {spread:.4f}; PCA evr {np.round(evr, 3)}")

    decoded = np.full(len(seen), np.nan)
    if np.abs(qm_seen).max() > 0:
        A = np.concatenate([embc, np.ones((len(seen), 1))], axis=1)
        loo = np.empty(len(seen))
        for i in range(len(seen)):
            m = np.arange(len(seen)) != i
            w, *_ = np.linalg.lstsq(A[m], qm_seen[m], rcond=None)
            loo[i] = A[i] @ w
        r_lin = float(np.corrcoef(loo, qm_seen)[0, 1])
        print(f"E3 linear decode of q/m from embedding (LOO): r = {r_lin:+.4f}")

        # Behavioral readout: which q/m does each embedding make the network
        # SIMULATE? Invert the net's predicted trajectories against the
        # generator. Information can be present and used yet invisible to
        # linear probes — behavior is the ground truth.
        from curvlib import E_CENTER, integrate_trajectories

        n_probe = 16
        px = np.linspace(E_CENTER - 0.8, E_CENTER + 0.8, n_probe).astype(np.float32)
        pv = np.zeros(n_probe, dtype=np.float32)
        probe_X = np.stack([px, pv], axis=1)
        qm_grid = np.linspace(-1.2, 1.2, 241)
        ref = np.stack(
            [
                integrate_trajectories(px.astype(float), pv.astype(float), np.full(n_probe, q))
                for q in qm_grid
            ]
        )
        with torch.no_grad():
            for j, b in enumerate(seen):
                pred = frc(
                    torch.from_numpy(probe_X), torch.full((n_probe,), int(b), dtype=torch.long)
                ).numpy()
                decoded[j] = qm_grid[np.argmin(((ref - pred) ** 2).mean(axis=(1, 2)))]
        corr = float(np.corrcoef(decoded, qm_seen)[0, 1])
        print(f"E3 BEHAVIORAL decode of q/m (trajectory inversion): r = {corr:+.4f}")
    else:
        corr = float("nan")

    e4 = mse_by_class(geo, data["held"], qm_body)
    print(f"E4 geometry zero-shot on unseen bodies: {e4}")

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    if np.abs(qm_seen).max() > 0:
        ch = np.abs(qm_seen) > 1e-9
        lims = [qm_seen.min() - 0.15, qm_seen.max() + 0.15]
        axes[0].plot(lims, lims, "k--", lw=1)
        axes[0].scatter(qm_seen[~ch], decoded[~ch], c="steelblue", label="neutral bodies")
        axes[0].scatter(qm_seen[ch], decoded[ch], c="crimson", label="charged bodies")
        axes[0].set_xlabel("true q/m")
        axes[0].set_ylabel("q/m decoded from the net's behavior")
        axes[0].set_title(
            f"the one number each embedding makes the net simulate\n"
            f"behavioral decode (trajectory inversion): r = {corr:+.3f}"
        )
        axes[0].legend()
    else:
        axes[0].scatter(emb[:, 0], emb[:, 1], c="steelblue")
        axes[0].set_xlabel("embedding dim 0")
        axes[0].set_ylabel("embedding dim 1")
        axes[0].set_title(
            f"embedding portrait (neutral mix)\nspread {spread:.4f}, flat PCA — "
            "no structure learned (identity irrelevant)"
        )

    labels, vals = [], []
    for name, d in (("geometry", e1_geo), ("force", e1_frc), ("force\n(swapped)", e2)):
        for cls in ("neutral", "charged"):
            if cls in d:
                labels.append(f"{name}\n{cls}")
                vals.append(d[cls])
        if "charged" not in d and "neutral" not in d:
            labels.append(name)
            vals.append(d["all"])
    axes[1].bar(labels, vals, color=["steelblue", "crimson"] * 3)
    axes[1].set_yscale("log")
    axes[1].set_ylabel("test MSE (log)")
    axes[1].set_title("the economy race: error by model and body class")

    out = RESULTS / f"07_economy_{mix}.png"
    fig.tight_layout()
    fig.savefig(out, dpi=140)
    print(f"plot -> {out}")

    (RESULTS / f"07_economy_{mix}.json").write_text(
        json.dumps(
            {
                "mix": mix,
                "E1_geometry": e1_geo,
                "E1_force": e1_frc,
                "E2_swap": e2,
                "E3_spread": spread,
                "E3_evr": evr.tolist(),
                "E3_loo_decode_r": corr,
                "E4_zero_shot": e4,
            },
            indent=1,
        )
    )


if __name__ == "__main__":
    main()
