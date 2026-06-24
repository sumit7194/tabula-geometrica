"""Step 114 — spinor double cover, the DISCOVERY paradigm: a net invents the 720-degree state space.

Companion to script 98 (which did the SYMBOLIC-LIBRARY version: half-angle features needed + sign-unobservable-from-
Bloch certificate). This is the DISCOVERY version, and it adds two things 98 did not: (a) a NET learns the double
cover from interference data, and (b) the double cover shown as TWO SHEETS over the same lab-frame point, framed as a
continuous-rotation HOLONOMY (the spinor-sign cousin of Aharonov-Bohm/Berry, scripts 113/54).

Physics (web-verified): SU(2) -> SO(3) is a DOUBLE COVER. Rotating a spin-1/2 by angle alpha acts as exp(-i alpha
sigma/2): a 360-degree rotation gives -1 on the STATE (not the identity), 720 degrees returns. The lab-frame
orientation / Bloch vector is 360-degree-periodic and CANNOT see the sign; a two-path interferometer CAN -- the
fringe signal S(alpha) = cos(alpha/2) has period 720 degrees (Rauch-Werner neutron interferometry).

Toy: spin-1/2 rotated by a continuous angle alpha in [0, 4pi]; measurable interference S(alpha) = cos(alpha/2)
[720-periodic]; lab-frame observable b(alpha) = (cos alpha, sin alpha) [360-periodic]. Two nets predict S:
  SPINOR-NET: input = the continuous rotation parameter alpha (trackable by a continuous lift) -> can represent 720.
  BLOCH-NET:  input = the instantaneous lab-frame observable (cos alpha, sin alpha) [360] -> provably cannot.

Pre-reg (2026-06-24):
  S1 LEARNABLE: spinor-net test R^2 > 0.95 (a net learns the 720-degree interference).
  S2 REPRESENTABILITY CERTIFICATE: bloch-net R^2 < 0.5 -- no 2pi-periodic (lab-frame) input can produce a 4pi-periodic
     output; the double cover is invisible to single-time spin measurements.
  S3 TWO SHEETS / 720-RETURN: at the SAME lab-frame orientation (alpha vs alpha+2pi) the spinor-net gives OPPOSITE
     predictions (mean |diff| > 0.8), with pred(360deg) ~ -1 and pred(720deg) ~ +1 -- two sheets over each lab point,
     720 degrees to return. (The bloch-net is FORCED to give identical predictions there -- it cannot tell the sheets
     apart -- which is exactly S2.)

Honest scope: complements 98 (function class) with the discovery/two-sheets/holonomy framing; not new physics.
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
from torch import nn

STEPS = 5000
TWO_PI = 2 * np.pi


class Net(nn.Module):
    def __init__(self, din):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(din, 64), nn.GELU(), nn.Linear(64, 64), nn.GELU(), nn.Linear(64, 1))

    def forward(self, x):
        return self.net(x)[:, 0]


def feats(alpha, kind):
    if kind == "spinor":
        return (alpha / TWO_PI)[:, None].astype(np.float32)                  # continuous rotation parameter
    return np.stack([np.cos(alpha), np.sin(alpha)], 1).astype(np.float32)    # lab-frame observable (360-periodic)


def train(kind, seed=0):
    torch.manual_seed(seed); rng = np.random.default_rng(seed)
    a_tr = rng.uniform(0, 4 * np.pi, 6000); X = torch.from_numpy(feats(a_tr, kind))
    y = torch.from_numpy(np.cos(a_tr / 2).astype(np.float32))
    m = Net(X.shape[1]); opt = torch.optim.Adam(m.parameters(), lr=2e-3)
    for step in range(STEPS):
        idx = rng.integers(0, len(X), 256)
        loss = nn.functional.mse_loss(m(X[idx]), y[idx])
        opt.zero_grad(); loss.backward(); opt.step()
        if step % 1500 == 0:
            progress(f"114_{kind}", step, STEPS, loss=float(loss.detach()))
    return m.eval()


def r2(pred, y):
    return float(1 - np.sum((pred - y) ** 2) / (np.sum((y - y.mean()) ** 2) + 1e-12))


def predict(m, alpha, kind):
    with torch.no_grad():
        return m(torch.from_numpy(feats(alpha, kind))).numpy()


def main():
    spinor = train("spinor"); bloch = train("bloch")
    a_te = np.random.default_rng(99).uniform(0, 4 * np.pi, 2000); y_te = np.cos(a_te / 2)
    r_spin = r2(predict(spinor, a_te, "spinor"), y_te)
    r_bloch = r2(predict(bloch, a_te, "bloch"), y_te)

    # S3: two sheets over the same lab-frame orientation (alpha vs alpha+2pi -> identical cos/sin, opposite cos(a/2))
    a0 = np.linspace(0, TWO_PI, 400, endpoint=False)
    sheet_diff = float(np.mean(np.abs(predict(spinor, a0, "spinor") - predict(spinor, a0 + TWO_PI, "spinor"))))
    bloch_sheet_diff = float(np.mean(np.abs(predict(bloch, a0, "bloch") - predict(bloch, a0 + TWO_PI, "bloch"))))
    p_360 = float(predict(spinor, np.array([TWO_PI]), "spinor")[0])           # 360 deg -> -1 (destructive)
    p_720 = float(predict(spinor, np.array([2 * TWO_PI]), "spinor")[0])       # 720 deg -> +1 (return)

    s1 = bool(r_spin > 0.95)
    s2 = bool(r_bloch < 0.5)
    s3 = bool(sheet_diff > 0.8 and abs(p_360 + 1) < 0.15 and abs(p_720 - 1) < 0.15)
    out = {"S1_spinor_R2": r_spin, "S2_bloch_R2": r_bloch, "spinor_sheet_diff": sheet_diff,
           "bloch_sheet_diff": bloch_sheet_diff, "pred_at_360deg": p_360, "pred_at_720deg": p_720,
           "S1_learnable": s1, "S2_representability_certificate": s2, "S3_two_sheets_720_return": s3,
           "double_cover_discovered": bool(s1 and s2 and s3),
           "verdict": ("SPINOR DOUBLE COVER DISCOVERED: a net learns the 720-degree interference cos(alpha/2) "
                       f"(R2 {r_spin:.3f}) from the continuous rotation parameter, but a net restricted to the lab-"
                       f"frame observable (cos a, sin a) CANNOT (R2 {r_bloch:.2f}) -- no 2pi-periodic input yields a "
                       f"4pi output. Over the SAME lab orientation the spinor-net gives OPPOSITE predictions "
                       f"(sheet diff {sheet_diff:.2f}; bloch-net forced to {bloch_sheet_diff:.2f}) -- two sheets, with "
                       f"-1 at 360deg and +1 at 720deg: 720 degrees to return. The double cover is a holonomy of the "
                       "continuous rotation, invisible to single-time spin measurements (cousin of AB/Berry)."
                       if (s1 and s2 and s3) else "PARTIAL -- see numbers (honest).")}
    print(f"S1 spinor learns cos(a/2): R2={r_spin:.3f} (>0.95): {s1}")
    print(f"S2 certificate (lab-frame can't): bloch R2={r_bloch:.3f} (<0.5): {s2}")
    print(f"S3 two sheets: spinor sheet-diff={sheet_diff:.2f} (>0.8, bloch forced {bloch_sheet_diff:.2f}); "
          f"pred(360)={p_360:.2f}~-1, pred(720)={p_720:.2f}~+1: {s3}")
    print(f"\nSPINOR DOUBLE COVER DISCOVERED: {out['double_cover_discovered']}")
    (RESULTS / "114_spinor_double_cover.json").write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(1, 2, figsize=(13, 5))
    ag = np.linspace(0, 4 * np.pi, 600)
    ax[0].plot(ag / np.pi, np.cos(ag / 2), "k--", lw=1, label="true cos(α/2) [720°]")
    ax[0].plot(ag / np.pi, predict(spinor, ag, "spinor"), color="seagreen", label=f"spinor-net (R²={r_spin:.2f})")
    ax[0].plot(ag / np.pi, predict(bloch, ag, "bloch"), color="crimson", label=f"bloch-net (R²={r_bloch:.2f})")
    for xv in (2, 4):
        ax[0].axvline(xv, ls=":", c="gray", lw=0.7)
    ax[0].set_xlabel("rotation α (units of π)"); ax[0].set_ylabel("interference signal")
    ax[0].set_title("S1/S2 · the 720° interference\nspinor-net learns it; lab-frame bloch-net cannot"); ax[0].legend(fontsize=8)
    ax[1].bar(["spinor-net\n(two sheets)", "bloch-net\n(one sheet)"], [sheet_diff, bloch_sheet_diff],
              color=["seagreen", "crimson"])
    ax[1].axhline(0.8, ls="--", c="k", lw=0.6)
    ax[1].set_ylabel("|pred(α) − pred(α+2π)|  (same lab orientation)")
    ax[1].set_title("S3 · two sheets over each lab point\nspinor distinguishes them; bloch is blind (720° to return)")
    fig.suptitle("Spinor double cover (discovery): a 720° state space invisible to lab-frame observables")
    fig.tight_layout(); fig.savefig(RESULTS / "114_spinor_double_cover.png", dpi=140)
    print("saved results/114_spinor_double_cover.json + .png")


if __name__ == "__main__":
    main()
