"""Step 22 — F-v2 autonomous diagnostics (pre-registered, no Claude in the loop).

Runs the methodology battery for the 2+1 law (Phase F missed 3/4 gates; see lab
notebook 2026-06-12). Answers the questions a fix round must answer BEFORE touching
architecture: is the F1 gate even feasible (oracle floor)? is the loss expressivity-,
capacity-, data-, or optimizer-bound? Reuses script 19's data/model/eval machinery
(no duplication). Resumable: results checkpoint after EACH experiment, so a power loss
re-runs only the unfinished one. Launch once in the background and walk away:

    nohup .venv/bin/python scripts/22_fv2_diagnostics.py > /tmp/fv2_diag.log 2>&1 &

Watch live on the dashboard (run names 22_*); final table -> results/22_fv2_diag.json.
"""

import argparse
import importlib.util
import json
import time
from pathlib import Path

import numpy as np
import torch
from torch import nn

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("s19", HERE / "19_matter_to_geometry.py")
s19 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(s19)  # __name__ != "__main__", so its main() does not run

from curvlib import RESULTS, progress  # noqa: E402  (reuse the dashboard heartbeat)

OUT = RESULTS / "22_fv2_diag.json"


class FlexNet(s19.LawNet):
    """Phase F's net with configurable width/kernel; inherits field/rollout/forward."""

    def __init__(self, width=1.0, k=5):
        nn.Module.__init__(self)
        c = [int(16 * width), int(32 * width), int(32 * width)]
        p = k // 2
        self.cnn = nn.Sequential(
            nn.Conv2d(1, c[0], k, padding=p), nn.Tanh(),
            nn.Conv2d(c[0], c[1], k, padding=p), nn.Tanh(),
            nn.Conv2d(c[1], c[2], k, padding=p), nn.Tanh(),
            nn.Conv2d(c[2], 2, k, padding=p))


def oracle_floor(te):
    """Roll out the TRUE field through the same grid + grid_sample + coarse-Verlet path
    the model uses. Its trajectory MSE is the achievable floor: no model can beat it,
    because the model also only ever sees the gridded/interpolated field. If this floor
    is above the F1 gate (1e-3), the gate was partly unpassable by construction."""
    rho, X, Y, wid, configs = te
    g = np.linspace(-s19.DOM, s19.DOM, s19.GRID_N)
    GX, GY = np.meshgrid(g, g)
    net = s19.LawNet()  # used only for its .rollout
    mses = []
    with torch.no_grad():
        for w in range(len(rho)):
            at = s19.true_accel(np.stack([GX.ravel(), GY.ravel()], 1), *configs[w])
            field = np.stack([at[:, 0].reshape(s19.GRID_N, s19.GRID_N),
                              at[:, 1].reshape(s19.GRID_N, s19.GRID_N)]).astype(np.float32)
            field_t = torch.from_numpy(field)[None]
            mask = wid == w
            pred = net.rollout(field_t.expand(int(mask.sum()), -1, -1, -1),
                               torch.from_numpy(X[mask]))
            mses.append(float(((pred - torch.from_numpy(Y[mask])) ** 2).mean()))
    return {"oracle_F1_floor": float(np.mean(mses))}


def train_eval(tr, te, steps, lr, width=1.0, k=5, tag="22_diag"):
    """Short cosine-decayed train; report final train loss + held-out F1/F2."""
    torch.manual_seed(19)
    model = FlexNet(width, k)
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, steps)
    rho_t = torch.from_numpy(tr[0])
    rng = np.random.default_rng(1000)
    loss = torch.tensor(float("nan"))
    for step in range(steps):
        idx = rng.integers(0, len(tr[1]), 192)
        w = tr[3][idx]
        pred = model(rho_t[w], torch.from_numpy(tr[1][idx]))
        loss = nn.functional.mse_loss(pred, torch.from_numpy(tr[2][idx]))
        opt.zero_grad()
        loss.backward()
        opt.step()
        sched.step()
        if step % 250 == 0:
            progress(tag, step, steps, loss=loss.item())
    model.eval()
    f1, f2 = s19.evaluate(model, *te)
    return {"final_train_loss": float(loss.item()), "F1_mse": f1, "F2_cos": f2}


def overfit_one_batch(tr, steps, lr=1e-3):
    """Can the net drive ONE batch to ~0? Tests raw expressivity, decoupled from data."""
    torch.manual_seed(19)
    model = FlexNet()
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    rng = np.random.default_rng(0)
    idx = rng.integers(0, len(tr[1]), 192)
    rb = torch.from_numpy(tr[0])[tr[3][idx]]
    xb, yb = torch.from_numpy(tr[1][idx]), torch.from_numpy(tr[2][idx])
    loss = torch.tensor(float("nan"))
    for step in range(steps):
        loss = nn.functional.mse_loss(model(rb, xb), yb)
        opt.zero_grad()
        loss.backward()
        opt.step()
        if step % 250 == 0:
            progress("22_overfit", step, steps, loss=loss.item())
    return {"overfit_final_loss": float(loss.item())}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--steps", type=int, default=3000, help="steps per diagnostic run")
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()
    s = args.steps

    print("generating worlds (standard + double) ...")
    tr = s19.make_dataset(300, 80, (1, 2), seed=0)
    tr2 = s19.make_dataset(600, 80, (1, 2), seed=0)   # data_2x
    te = s19.make_dataset(40, 80, (1, 2), seed=77)

    plan = [
        ("oracle_floor", lambda: oracle_floor(te)),
        ("overfit_one_batch", lambda: overfit_one_batch(tr, s)),
        ("lr_3e-4", lambda: train_eval(tr, te, s, 3e-4, tag="22_lr_lo")),
        ("lr_1e-3", lambda: train_eval(tr, te, s, 1e-3, tag="22_lr_mid")),
        ("lr_3e-3", lambda: train_eval(tr, te, s, 3e-3, tag="22_lr_hi")),
        ("capacity_2x", lambda: train_eval(tr, te, s, 1e-3, width=2.0, tag="22_cap2x")),
        ("data_2x", lambda: train_eval(tr2, te, s, 1e-3, tag="22_data2x")),
    ]

    results = json.loads(args.out.read_text()) if args.out.exists() else {}
    for name, fn in plan:
        if name in results:
            print(f"skip {name} (already done)")
            continue
        print(f"running {name} ...")
        t0 = time.time()
        results[name] = fn()
        results[name]["seconds"] = round(time.time() - t0, 1)
        args.out.write_text(json.dumps(results, indent=1))  # checkpoint after each
        print(f"  {name}: {results[name]}")

    floor = results.get("oracle_floor", {}).get("oracle_F1_floor")
    print("\n==== F-v2 DIAGNOSTICS COMPLETE ====")
    if floor is not None:
        print(f"oracle F1 floor = {floor:.2e}  (Phase F gate was 1e-3; "
              f"{'gate INFEASIBLE — floor above it' if floor > 1e-3 else 'gate feasible'})")
    print(f"full table -> {args.out}")


if __name__ == "__main__":
    main()
