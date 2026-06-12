"""Step 10 — the formal MDL race: how many bits does each force of nature cost?

Two-part code over a body's data:
  L_total(d) = L_data(d) + L_param(d)
  L_data   prequential Gaussian code of held-out prediction residuals,
           sigma^2 = the model's train MSE (plug-in), position resolution
           delta = 1e-3 (stated constant, cancels in comparisons)
  L_param  per-body embedding bits: the coarsest quantization of the learned
           embeddings keeping test MSE within 5%, bits = sum_dims
           log2(span/Delta* + 1)

Sweep per-body code size d in {0 (= geometry: identity unusable), 1, 2, 4} on
both mixes. Predictions pre-registered in the lab notebook (M1-M4).
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
from scipy.stats import spearmanr

spec = importlib.util.spec_from_file_location(
    "train_dyn", Path(__file__).resolve().parent / "06_train_dynamics.py"
)
train_dyn = importlib.util.module_from_spec(spec)
spec.loader.exec_module(train_dyn)

DELTA = 1e-3  # stated position resolution for absolute bit counts
DIMS = (0, 1, 2, 4)
SEEDS = {"steps": 12000, "seed": 0}  # longer: MDL comparisons need convergence,
# not training noise (the d-sweep differences must be capacity, not luck)


def data_bits_per_target(model, split, sigma2):
    body, X, Y = split
    with torch.no_grad():
        pred = model(torch.from_numpy(X), torch.from_numpy(body)).numpy()
    err2 = ((pred - Y) ** 2).mean()
    return 0.5 * np.log2(2 * np.pi * sigma2) + err2 / (2 * sigma2 * np.log(2)) - np.log2(DELTA)


def param_bits_per_body(model, data, base_mse):
    """Coarsest embedding quantization keeping test MSE within 5%."""
    if not hasattr(model, "emb"):
        return 0.0, None
    W = model.emb.weight.data.clone()
    spans = (W.max(0).values - W.min(0).values).numpy()
    best = None
    for delta_q in np.logspace(1, -4, 26):
        model.emb.weight.data = torch.round(W / delta_q) * delta_q
        mse = train_dyn.mse_on(model, data["test"])
        model.emb.weight.data = W
        if mse <= 1.05 * base_mse:
            best = delta_q
            break
    if best is None:
        best = 1e-4
    bits = float(np.sum(np.log2(np.maximum(spans / best, 0) + 1)))
    return bits, float(best)


def main() -> None:
    out = {}
    for mix in ("neutral", "charged"):
        data = make_dynamics_dataset(mix, seed=SEEDS["seed"])
        n_bodies = len(data["qm_body"])
        per_body_targets = 3 * 500  # 600 segments/body, 5/6 seen-split, 3 targets
        out[mix] = {}
        for d in DIMS:
            # deterministic, distinct init per (mix, d) — torch's default
            # generator is process-random, which silently broke reproducibility
            torch.manual_seed(1000 + 10 * d + (0 if mix == "neutral" else 1))
            model = (
                train_dyn.GeometryModel()
                if d == 0
                else train_dyn.ForceModel(n_bodies, emb_dim=d)
            )
            print(f"[{mix}] training d={d} ...")
            train_dyn.train(model, data, SEEDS["steps"], SEEDS["seed"])
            model.eval()
            sigma2 = max(train_dyn.mse_on(model, data["train"]), 1e-10)
            test_mse = train_dyn.mse_on(model, data["test"])
            bits_t = data_bits_per_target(model, data["test"], sigma2)
            pbits, delta_q = param_bits_per_body(model, data, test_mse)
            total = bits_t * per_body_targets + pbits
            out[mix][d] = {
                "test_mse": test_mse,
                "data_bits_per_target": float(bits_t),
                "param_bits_per_body": pbits,
                "total_bits_per_body": float(total),
                "quant_delta": delta_q,
            }
            print(f"   test MSE {test_mse:.2e} | data bits/target {bits_t:.3f} | "
                  f"param bits/body {pbits:.2f} | TOTAL bits/body {total:.1f}")

            # M3: the d=1 charged code should be a clean monotone q/m code
            if mix == "charged" and d == 1:
                seen = np.setdiff1d(np.arange(n_bodies), np.array(data["held_bodies"]))
                e = model.emb.weight.data.numpy()[seen, 0]
                qm = data["qm_body"][seen]
                ch = np.abs(qm) > 1e-9
                rho_all = float(spearmanr(e, qm).statistic)
                rho_ch = float(spearmanr(e[ch], qm[ch]).statistic)
                out[mix]["d1_code"] = {"spearman_all": rho_all,
                                       "spearman_charged_only": rho_ch,
                                       "emb": e.tolist(), "qm": qm.tolist()}
                print(f"   M3: d=1 scalar vs q/m — spearman all {rho_all:+.4f}, "
                      f"charged-only {rho_ch:+.4f}")

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    for mix, color in (("neutral", "steelblue"), ("charged", "crimson")):
        totals = [out[mix][d]["total_bits_per_body"] for d in DIMS]
        rel = np.array(totals) - min(totals)
        axes[0].plot(DIMS, rel, "o-", color=color, label=f"{mix} mix")
        i_min = int(np.argmin(totals))
        axes[0].annotate(f"min @ d={DIMS[i_min]}", (DIMS[i_min], rel[i_min]),
                         textcoords="offset points", xytext=(8, 8), color=color)
    axes[0].set_xlabel("per-body code size d (embedding dims)")
    axes[0].set_ylabel("total bits/body − minimum (log-ish scale)")
    axes[0].set_yscale("symlog", linthresh=10)
    axes[0].set_xticks(DIMS)
    axes[0].set_title("the MDL race: description length vs per-body code size")
    axes[0].legend()

    c = out["charged"].get("d1_code")
    if c:
        qm_arr = np.array(c["qm"])
        ch = np.abs(qm_arr) > 1e-9
        e_arr = np.array(c["emb"])
        axes[1].scatter(qm_arr[~ch], e_arr[~ch], c="steelblue", label="neutral")
        axes[1].scatter(qm_arr[ch], e_arr[ch], c="crimson", label="charged")
        axes[1].set_xlabel("true q/m")
        axes[1].set_ylabel("learned 1-d per-body code")
        axes[1].set_title(
            f"the 1-d code: sufficient, not necessarily monotone\n"
            f"spearman all = {c['spearman_all']:+.3f}, "
            f"charged-only = {c['spearman_charged_only']:+.3f}"
        )
        axes[1].legend()
    fig.tight_layout()
    fout = RESULTS / "10_mdl.png"
    fig.savefig(fout, dpi=140)
    print(f"plot -> {fout}")

    (RESULTS / "10_mdl.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
