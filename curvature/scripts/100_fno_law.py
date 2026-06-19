"""Step 100 — F-v2 STEP 2A: the law from matter, with a FOURIER NEURAL OPERATOR (the global-operator fix).

Phase F (script 19) was an honest null: a LOCAL CNN learned matter->acceleration-field only to F1~0.058 / F2~0.937,
and the pre-registered diagnostics (22) pinned WHY -- overfit-one-batch FAILED at 0.047 (a representational wall),
the oracle floor is 1.2e-4 (so the 1e-3 gate IS feasible), and the magnitude needs the 1/r LONG-RANGE tail, which
a local convolution structurally cannot carry at any width/depth. The fv2_roadmap pre-registered the fix as Step
2A: a SPECTRAL layer -- "1/r is long-range; spectral methods represent it natively." This is that experiment.

ONE KNOB CHANGED (the clean test the 3+1 run wasn't): the field network goes CNN -> Fourier Neural Operator
(Li et al. 2020). Everything else -- data generator, differentiable Verlet rollout, the F1-F4 gates, the
evaluate() -- is reused verbatim from script 19. The FNO's spectral convolution (FFT -> multiply low modes ->
iFFT) gives every output pixel a GLOBAL receptive field in one layer, which is exactly what the 1/r kernel needs.

Pre-reg (2026-06-20), gates vs CNN baseline (F1=0.058, F2=0.937) and oracle floor (1.2e-4):
  P0 ARCHITECTURE (the decisive test): the FNO BREAKS the overfit-one-batch wall -- final loss < 5e-3 (vs the
     CNN's 0.047). If a global operator CAN memorize one batch, the Phase F wall was representational (locality),
     not data/training. This is the headline Mac result; it adjudicates the architecture hypothesis.
  P1 F1 trajectory MSE on held-out worlds: clearly beats the CNN's 0.058 (and aims at the 1e-3 gate).
  P2 F2 field cosine on unseen worlds: clearly beats the CNN's 0.937 (and aims at 0.98).
  P3 F4 matter-blind control: MSE >= 10x F1 (the field is really being used).
NOTE: full budget (12k steps x >=3 seeds, the headline F1/F2 numbers) is a VM job; this Mac run is sized to
adjudicate P0 decisively and show the P1/P2 trend. Device defaults to MPS; CPU path stays bit-reproducible.
"""

import argparse
import importlib.util
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import torch
from curvlib import RESULTS, load_ckpt, progress, save_ckpt
from torch import nn

_spec = importlib.util.spec_from_file_location("law19", str(Path(__file__).resolve().parent / "19_matter_to_geometry.py"))
law19 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(law19)
GRID_N, DOM = law19.GRID_N, law19.DOM


class SpectralConv2d(nn.Module):
    """global-receptive-field layer: keep the lowest `modes` Fourier modes, mix channels with learned complex weights."""

    def __init__(self, cin, cout, modes):
        super().__init__()
        self.modes = modes; scale = 1.0 / (cin * cout)
        self.w1 = nn.Parameter(scale * torch.randn(cin, cout, modes, modes, dtype=torch.cfloat))
        self.w2 = nn.Parameter(scale * torch.randn(cin, cout, modes, modes, dtype=torch.cfloat))

    def forward(self, x):
        B, C, Hh, Ww = x.shape; m = self.modes
        xf = torch.fft.rfft2(x)
        out = torch.zeros(B, self.w2.shape[1], Hh, Ww // 2 + 1, dtype=torch.cfloat, device=x.device)
        out[:, :, :m, :m] = torch.einsum("bixy,ioxy->boxy", xf[:, :, :m, :m], self.w1)
        out[:, :, -m:, :m] = torch.einsum("bixy,ioxy->boxy", xf[:, :, -m:, :m], self.w2)
        return torch.fft.irfft2(out, s=(Hh, Ww))


class FNOLawNet(law19.LawNet):
    """same interface as LawNet (field + rollout), but the field net is an FNO. rollout/forward inherited verbatim."""

    def __init__(self, width=32, modes=14, depth=4):
        nn.Module.__init__(self)
        self.lift = nn.Conv2d(1, width, 1)
        self.spec = nn.ModuleList([SpectralConv2d(width, width, modes) for _ in range(depth)])
        self.point = nn.ModuleList([nn.Conv2d(width, width, 1) for _ in range(depth)])
        self.proj = nn.Sequential(nn.Conv2d(width, width, 1), nn.GELU(), nn.Conv2d(width, 2, 1))

    def field(self, rho):
        x = self.lift(rho[:, None, :, :])
        for s, p in zip(self.spec, self.point):
            x = nn.functional.gelu(s(x) + p(x))
        return self.proj(x)


def main():
    _def_dev = "cuda" if torch.cuda.is_available() else ("mps" if torch.backends.mps.is_available() else "cpu")
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", default=_def_dev)
    ap.add_argument("--worlds", type=int, default=240)
    ap.add_argument("--overfit-steps", type=int, default=1200)
    ap.add_argument("--steps", type=int, default=5000)
    ap.add_argument("--lr", type=float, default=2e-3)
    ap.add_argument("--seed", type=int, default=100)
    ap.add_argument("--modes", type=int, default=14)        # FNO Fourier modes kept (max grid//2)
    ap.add_argument("--width", type=int, default=32)
    ap.add_argument("--grid", type=int, default=48)         # field grid resolution (NEW knob: data + FNO both at this res)
    ap.add_argument("--tag", default="")                    # suffix for ckpt/results/progress so sweep arms don't collide
    a = ap.parse_args(); dev = a.device
    law19.GRID_N = a.grid; GRID_N = a.grid                  # propagate resolution into the data generator + plot
    OVF, LAW = f"100_fno_overfit{a.tag}", f"100_fno_law{a.tag}"
    print(f"device={dev}  worlds={a.worlds}  steps={a.steps}  grid={a.grid}  modes={a.modes}  width={a.width}  tag='{a.tag}'  seed={a.seed}")

    print("generating worlds ...")
    tr = law19.make_dataset(a.worlds, 80, (1, 2), seed=0)
    te = law19.make_dataset(40, 80, (1, 2), seed=77)
    sup = law19.make_dataset(40, 80, (3,), seed=88)
    rho_t = torch.from_numpy(tr[0]).to(dev)
    Xtr = torch.from_numpy(tr[1]).to(dev); Ytr = torch.from_numpy(tr[2]).to(dev); wid = tr[3]

    # ---------------- P0: the decisive architecture test -- can the FNO overfit ONE batch? ----------------
    if a.overfit_steps > 0:
        torch.manual_seed(a.seed); fno = FNOLawNet(width=a.width, modes=a.modes).to(dev)
        opt = torch.optim.Adam(fno.parameters(), lr=a.lr)
        rng = np.random.default_rng(0); ob = rng.integers(0, len(wid), 192)
        rb, xb, yb = rho_t[wid[ob]], Xtr[ob], Ytr[ob]
        t0 = time.time()
        for step in range(a.overfit_steps):
            loss = nn.functional.mse_loss(fno(rb, xb), yb)
            opt.zero_grad(); loss.backward(); opt.step()
            if step % 200 == 0:
                progress(OVF, step, a.overfit_steps, loss=loss.item())
                print(f"  [overfit] step {step:5d}  loss {loss.item():.5f}")
        overfit_loss = float(loss.item())
        print(f"P0 FNO overfit-one-batch final loss {overfit_loss:.5f}  (CNN wall 0.047; gate < 5e-3)  [{time.time()-t0:.0f}s]")
    else:                                                              # resume: P0 already established in a prior run
        hb = RESULTS / "progress" / f"{OVF}.json"
        overfit_loss = float(json.loads(hb.read_text())["metrics"]["loss"]) if hb.exists() else float("nan")
        print(f"P0 overfit skipped (resume); prior overfit-one-batch final loss {overfit_loss:.5f} (CNN wall 0.047)")

    # ---------------- P1-P3: full training (fresh net), resumable ----------------
    torch.manual_seed(a.seed); fno = FNOLawNet(width=a.width, modes=a.modes).to(dev)
    nparam = sum(p.numel() for p in fno.parameters())
    opt = torch.optim.Adam(fno.parameters(), lr=a.lr)
    ckpt = RESULTS / f"100_fno_ckpt{a.tag}.pt"; start = 0; rng = np.random.default_rng(1000)
    if ckpt.exists():
        start, rng, exact = load_ckpt(ckpt, fno, opt, fallback_seed=1000)
        print(f"resumed full-train at step {start} ({'bit-exact' if exact else 'legacy'})")
    t0 = time.time()
    for step in range(start, a.steps):
        idx = rng.integers(0, len(wid), 192); w = wid[idx]
        loss = nn.functional.mse_loss(fno(rho_t[w], Xtr[idx]), Ytr[idx])
        opt.zero_grad(); loss.backward(); opt.step()
        if step % 250 == 0:
            progress(LAW, step, a.steps, loss=loss.item())
            if step % 500 == 0 and step > start:                      # frequent ckpt (repeated power losses)
                save_ckpt(ckpt, fno, opt, step, rng)
            if step % 1000 == 0:
                print(f"  [train] step {step:5d}  loss {loss.item():.6f}  [{time.time()-t0:.0f}s]")

    fno.to("cpu"); fno.eval()
    f1, f2 = law19.evaluate(fno, *te)
    f1s, f2s = law19.evaluate(fno, *sup)
    f1c, _ = law19.evaluate(fno, *te, zero_rho=True)
    print(f"\nP1 F1 held-out trajectory MSE: {f1:.2e}  (CNN 0.058; gate <= 1e-3, oracle floor 1.2e-4)")
    print(f"P2 F2 field cosine (unseen worlds): {f2:.4f}  (CNN 0.937; gate > 0.98)")
    print(f"   F3 superposition (3-blob, never seen): MSE {f1s:.2e}, cos {f2s:.4f}")
    print(f"P3 F4 matter-blind control: MSE {f1c:.2e}  (gate >= 10x F1 = {10*f1:.2e})")

    p0 = bool(overfit_loss < 5e-3)
    p1 = bool(f1 < 0.058)
    p2 = bool(f2 > 0.937)
    p3 = bool(f1c >= 10 * f1)
    out = {"device": dev, "n_params": nparam, "worlds": a.worlds, "steps": a.steps,
           "grid": a.grid, "modes": a.modes, "width": a.width, "seed": a.seed, "tag": a.tag,
           "P0_overfit_one_batch": overfit_loss, "CNN_overfit_wall": 0.047, "oracle_floor": 1.2e-4,
           "F1_mse": f1, "F2_cos": f2, "F3_mse": f1s, "F3_cos": f2s, "F4_blind": f1c,
           "CNN_baseline_F1": 0.058, "CNN_baseline_F2": 0.937,
           "P0_breaks_overfit_wall": p0, "P1_beats_CNN_F1": p1, "P2_beats_CNN_F2": p2, "P3_control": p3}
    print(f"\nP0 FNO breaks the overfit-one-batch wall (architecture, not data): {p0}")
    print(f"P1 beats CNN F1 / P2 beats CNN F2 / P3 control: {p1} / {p2} / {p3}")
    (RESULTS / f"100_fno_law{a.tag}.json").write_text(json.dumps(out, indent=1))

    # plot: learned vs true field on a 3-blob world (the superposition test)
    w = 0; g = np.linspace(-DOM, DOM, GRID_N); GX, GY = np.meshgrid(g, g)
    pts = np.stack([GX.ravel(), GY.ravel()], 1)
    at = law19.true_accel(pts, *sup[4][w]).reshape(GRID_N, GRID_N, 2)
    with torch.no_grad():
        ah = fno.field(torch.from_numpy(sup[0][w:w + 1]))[0].numpy()
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 5.6)); sp = max(1, GRID_N // 24)
    for ax, f, ttl in ((axes[0], np.transpose(ah, (1, 2, 0)), f"FNO field (3 masses, never trained) — F2 cos {f2s:.3f}"),
                       (axes[1], at, "true 1/r field")):
        ax.quiver(GX[::sp, ::sp], GY[::sp, ::sp], f[::sp, ::sp, 0], f[::sp, ::sp, 1], scale=18)
        for (cx, cy), mm in zip(*sup[4][w]):
            ax.scatter([cx], [cy], s=300 * mm, c="crimson", alpha=0.6)
        ax.set_title(ttl)
    fig.suptitle(f"F-v2 Step 2A: a Fourier Neural Operator for the gravity law\n"
                 f"overfit-one-batch {overfit_loss:.4f} (CNN wall 0.047) — F1 {f1:.3e} (CNN 0.058)")
    fig.tight_layout(); fig.savefig(RESULTS / f"100_fno_law{a.tag}.png", dpi=140)
    print(f"saved results/100_fno_law{a.tag}.json + .png")


if __name__ == "__main__":
    main()
