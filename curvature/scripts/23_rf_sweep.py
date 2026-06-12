"""Step 23 — F-v2 Step 3: the clean locality experiment. ONE knob (receptive
field via dilation schedule), everything else frozen at the diagnosed best.
If F2_cos climbs with receptive field, the local-CNN-vs-1/r hypothesis is
proven and the spectral fix (F-v3) is justified. Pre-registration RF1/RF2 in
the lab notebook (2026-06-14)."""

import importlib.util
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import torch
from curvlib import RESULTS, load_ckpt, progress, save_ckpt
from torch import nn

spec = importlib.util.spec_from_file_location(
    "law", Path(__file__).resolve().parent / "19_matter_to_geometry.py"
)
law = importlib.util.module_from_spec(spec)
spec.loader.exec_module(law)

LR = 3e-3  # best of the 22-diagnostics sweep (documented choice, not default)
STEPS = 12000
ARMS = (1, 2, 4, 8)  # max dilation; RF ~= 17, 29, 53, 101 px on the 48 grid


class DilatedLawNet(law.LawNet):
    def __init__(self, d: int):
        super().__init__()
        self.cnn = nn.Sequential(
            nn.Conv2d(1, 16, 5, padding=2), nn.Tanh(),
            nn.Conv2d(16, 32, 5, padding=2 * min(2, d), dilation=min(2, d)), nn.Tanh(),
            nn.Conv2d(32, 32, 5, padding=2 * min(4, d), dilation=min(4, d)), nn.Tanh(),
            nn.Conv2d(32, 2, 5, padding=2 * d, dilation=d),
        )


def run_arm(d: int, tr, te, sup, device: str = "cpu") -> dict:
    torch.manual_seed(23)  # init on CPU before .to(device): same weights everywhere
    model = DilatedLawNet(d)
    opt = torch.optim.Adam(model.parameters(), lr=LR)
    rng = np.random.default_rng(0)
    ckpt = RESULTS / f"23_ckpt_d{d}.pt"
    start = 0
    if ckpt.exists():
        start, rng, exact = load_ckpt(ckpt, model, opt, fallback_seed=0)
        print(f"  [d={d}] resumed at step {start} "
              f"({'bit-exact' if exact else 'LEGACY ckpt — not bit-exact, flagged'})")
    model.to(device)
    for state in opt.state.values():  # Adam state follows the params' device
        for k, v in state.items():
            if torch.is_tensor(v):
                state[k] = v.to(device)
    rho_t = torch.from_numpy(tr[0]).to(device)
    X_t = torch.from_numpy(tr[1]).to(device)
    Y_t = torch.from_numpy(tr[2]).to(device)
    for step in range(start, STEPS):
        idx = rng.integers(0, len(tr[1]), 192)
        w = tr[3][idx]
        loss = nn.functional.mse_loss(model(rho_t[w], X_t[idx]), Y_t[idx])
        opt.zero_grad()
        loss.backward()
        opt.step()
        if step % 250 == 0:
            progress(f"23_rf_d{d}", step, STEPS, loss=float(loss.detach()))
            if step % 1000 == 0 and step > 0:
                save_ckpt(ckpt, model, opt, step, rng)
    model.cpu().eval()  # evaluate() runs on CPU tensors
    f1, f2 = law.evaluate(model, *te)
    f1s, f2s = law.evaluate(model, *sup)
    print(f"  [d={d}] F1 {f1:.2e}  F2 {f2:.4f}  F3cos {f2s:.4f}")
    return {"d": d, "F1": f1, "F2": f2, "F3_mse": f1s, "F3_cos": f2s}


def main() -> None:
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("--device", default="cpu", choices=("cpu", "mps"))
    args = p.parse_args()

    print(f"generating worlds (shared across arms) ... [device: {args.device}]")
    tr = law.make_dataset(300, 80, (1, 2), seed=0)
    te = law.make_dataset(40, 80, (1, 2), seed=77)
    sup = law.make_dataset(40, 80, (3,), seed=88)

    out = []
    done_f = RESULTS / "23_rf_sweep.json"
    if done_f.exists():
        out = json.loads(done_f.read_text())
        print(f"resuming sweep with {len(out)} arms already complete")
    for d in ARMS:
        if any(r["d"] == d for r in out):
            continue
        print(f"arm: max dilation {d}")
        out.append(run_arm(d, tr, te, sup, args.device))
        done_f.write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(figsize=(8, 5))
    rf = {1: 17, 2: 29, 4: 53, 8: 101}
    ax.plot([rf[r["d"]] for r in out], [r["F2"] for r in out], "o-",
            color="darkslategray", label="F2: field cos (unseen worlds)")
    ax.plot([rf[r["d"]] for r in out], [r["F3_cos"] for r in out], "s--",
            color="crimson", label="F3: superposition cos (3-blob)")
    ax.axhline(0.98, color="gray", ls=":", lw=1)
    ax.set_xlabel("receptive field [pixels on the 48-grid]")
    ax.set_ylabel("median cos(learned field, true field)")
    ax.set_title("the locality experiment: can a longer reach see 1/r?\n"
                 "(one knob — dilation; all else frozen)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(RESULTS / "23_rf_sweep.png", dpi=140)
    print(f"plot -> {RESULTS / '23_rf_sweep.png'}")


if __name__ == "__main__":
    main()
