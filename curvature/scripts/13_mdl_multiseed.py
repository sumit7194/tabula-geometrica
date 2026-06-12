"""Step 13 — multi-seed MDL refinement (the M1 follow-up).

Step 10's neutral-mix MDL minimum was unresolvable: the data term's
seed-to-seed optimization variance swamps the tiny per-body parameter term.
This rerun averages the two-part code over several seeds per (mix, d) so the
capacity signal can be separated from training luck. Pre-registered refinement:
with variance averaged down, (M1') the neutral curve flattens across d (no
resolvable per-body information — consistent with identity being worth ~0.4
bits) while (M2') the charged minimum at d = 1 is stable across seeds.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import importlib.util

import numpy as np
import torch
from curvlib import RESULTS, make_dynamics_dataset

spec = importlib.util.spec_from_file_location(
    "mdl", Path(__file__).resolve().parent / "10_mdl.py"
)
mdl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mdl)

spec6 = importlib.util.spec_from_file_location(
    "train_dyn", Path(__file__).resolve().parent / "06_train_dynamics.py"
)
train_dyn = importlib.util.module_from_spec(spec6)
spec6.loader.exec_module(train_dyn)

SEEDS = (0, 1, 2)
DIMS = (0, 1, 2, 4)
STEPS = 12000


def main() -> None:
    out = {}
    for mix in ("neutral", "charged"):
        out[mix] = {}
        for d in DIMS:
            totals, datas, params = [], [], []
            for seed in SEEDS:
                data = make_dynamics_dataset(mix, seed=seed)
                n_bodies = len(data["qm_body"])
                torch.manual_seed(5000 + 100 * seed + 10 * d + (mix == "charged"))
                model = (
                    train_dyn.GeometryModel()
                    if d == 0
                    else train_dyn.ForceModel(n_bodies, emb_dim=d)
                )
                train_dyn.train(model, data, STEPS, seed)
                model.eval()
                sigma2 = max(train_dyn.mse_on(model, data["train"]), 1e-10)
                test_mse = train_dyn.mse_on(model, data["test"])
                bits_t = mdl.data_bits_per_target(model, data["test"], sigma2)
                pbits, _ = mdl.param_bits_per_body(model, data, test_mse)
                datas.append(float(bits_t))
                params.append(float(pbits))
                totals.append(float(bits_t * 1500 + pbits))
            out[mix][d] = {
                "total_mean": float(np.mean(totals)),
                "total_std": float(np.std(totals)),
                "data_bits_mean": float(np.mean(datas)),
                "param_bits_mean": float(np.mean(params)),
            }
            print(f"[{mix}] d={d}: total {np.mean(totals):.0f} ± {np.std(totals):.0f} "
                  f"bits/body (data {np.mean(datas):.3f}/target, param {np.mean(params):.2f}/body)")

    (RESULTS / "13_mdl_multiseed.json").write_text(json.dumps(out, indent=1))
    for mix in out:
        means = {d: out[mix][d]["total_mean"] for d in DIMS}
        d_min = min(means, key=means.get)
        print(f"{mix}: minimum at d={d_min}; "
              f"separations vs std: "
              + ", ".join(f"d={d}: {(means[d]-means[d_min]):.0f}±{out[mix][d]['total_std']:.0f}"
                          for d in DIMS))


if __name__ == "__main__":
    main()
