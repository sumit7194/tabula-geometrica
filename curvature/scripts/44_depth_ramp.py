"""Step 44 — thread D follow-up #2: a DEEP-composition latent -> a gradual depth RAMP (MPS).

Script 43 confirmed the precondition (latent illegible to linear pooling -> emergence) but found
emergence is a ONE-LAYER STEP, because a 2D rotation is a shallow nonlinearity (one layer computes
the angle). The Phronesis L4->L36 GRADUAL ramp needs a latent built by DEEP SEQUENTIAL COMPOSITION.

Task (non-commuting SO(3) product — deep yet illegible-at-input): u in R^3; the map is
M(theta) = R_{a_D}(theta) ... R_{a_1}(theta), a product of D rotations by the SAME latent angle
theta about D DIFFERENT fixed axes (SO(3) is non-abelian, so this is NOT a single rotation by
D*theta). token = (u_i, M(theta) u_i). Because M is LINEAR in u, E[M u]=M E[u]=0 for centered u ->
the pooled mean is theta-independent -> theta is ILLEGIBLE to linear pooling (the property a
state-dependent map leaked away). Recovering theta requires composing D non-commuting rotations.
Probe linear legibility of theta at each layer -> deep D=6 vs shallow control D=1.

Gates (pre-reg 2026-06-16):
  F1 deep RAMP: deep last-layer - layer1 > 0.3 AND layer1 < 0.6 (didn't saturate in one layer).
  F2 deep input illegible: deep layer0 < 0.3.
  F3 deep task solved: deep query R^2 > 0.8 (so a low early curve is genuine, not under-training).
  F4 shallow STEPS: D=1 control saturates fast (its layer1 > 0.7) -> the contrast.
Runs on MPS (user-enabled).
"""

import argparse
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
from sklearn.linear_model import RidgeCV
from sklearn.model_selection import cross_val_predict
from torch import nn

DEPTH, DMODEL, KEX, QN = 8, 128, 24, 4
STEPS, N_PROBE = 12000, 512
AXES = np.random.default_rng(999).normal(size=(6, 3))
AXES = (AXES / np.linalg.norm(AXES, axis=1, keepdims=True)).astype(np.float32)  # 6 fixed distinct axes


def iterate(u, theta, D):
    """z_0=u; z <- R_{a_t}(theta) z for t=0..D-1 (Rodrigues, different axis each step). u:(...,3)."""
    z = u.copy()
    cth = np.cos(theta)[..., None]; sth = np.sin(theta)[..., None]   # (...,1)
    for t in range(D):
        a = AXES[t]                                                  # (3,)
        dot = (z * a).sum(-1, keepdims=True)                         # a.z
        cr = np.cross(np.broadcast_to(a, z.shape), z)               # a x z
        z = z * cth + cr * sth + a * dot * (1 - cth)                 # rotate z about a by theta
    return z


def make_batch(B, rng, D):
    theta = rng.uniform(-1.0, 1.0, B).astype(np.float32)
    U = rng.normal(size=(B, KEX, 3)).astype(np.float32)
    Uq = rng.normal(size=(B, QN, 3)).astype(np.float32)
    th2 = np.repeat(theta[:, None], KEX, 1)
    thq = np.repeat(theta[:, None], QN, 1)
    V = iterate(U, th2, D).astype(np.float32)
    Vq = iterate(Uq, thq, D).astype(np.float32)
    tokens = np.concatenate([U, V], -1).astype(np.float32)          # (B,KEX,6)
    return tokens, Uq, Vq, theta


class TF(nn.Module):
    def __init__(self, depth=DEPTH, d=DMODEL):
        super().__init__()
        self.embed = nn.Linear(6, d)
        self.layers = nn.ModuleList([
            nn.TransformerEncoderLayer(d, 4, 2 * d, batch_first=True, dropout=0.0, norm_first=True)
            for _ in range(depth)])
        self.head = nn.Sequential(nn.Linear(3 + d, d), nn.GELU(), nn.Linear(d, d), nn.GELU(), nn.Linear(d, 3))

    def layer_reps(self, tokens):
        h = self.embed(tokens)
        reps = [h.mean(1)]
        for layer in self.layers:
            h = layer(h)
            reps.append(h.mean(1))
        return reps

    def forward(self, tokens, Uq):
        c = self.layer_reps(tokens)[-1]
        return self.head(torch.cat([Uq, c[:, None, :].expand(-1, Uq.shape[1], -1)], -1))


def train(D, seed, dev):
    torch.manual_seed(seed); rng = np.random.default_rng(seed)
    m = TF().to(dev); opt = torch.optim.Adam(m.parameters(), lr=1e-3)
    tag = f"44_D{D}"
    for step in range(STEPS):
        tk, Uq, Vq, _ = make_batch(128, rng, D)
        loss = nn.functional.mse_loss(m(torch.from_numpy(tk).to(dev), torch.from_numpy(Uq).to(dev)),
                                      torch.from_numpy(Vq).to(dev))
        opt.zero_grad(); loss.backward(); opt.step()
        if step % 500 == 0:
            progress(tag, step, STEPS, loss=float(loss.detach()))
    m.eval()
    return m


def probe_curve(m, D, dev):
    rng = np.random.default_rng(123)
    tk, Uq, Vq, theta = make_batch(N_PROBE, rng, D)
    with torch.no_grad():
        reps = [r.cpu().numpy() for r in m.layer_reps(torch.from_numpy(tk).to(dev))]
        pred = m(torch.from_numpy(tk).to(dev), torch.from_numpy(Uq).to(dev)).cpu().numpy()
    r2 = float(1 - np.mean((pred - Vq) ** 2) / np.var(Vq))
    curve = [float(np.corrcoef(cross_val_predict(RidgeCV(alphas=[0.1, 1, 10, 100]), R, theta, cv=5), theta)[0, 1])
             for R in reps]
    return curve, r2


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--device", default="mps"); a = ap.parse_args()
    dev = torch.device(a.device if (a.device != "mps" or torch.backends.mps.is_available()) else "cpu")
    print(f"device: {dev}")

    deep = train(6, 0, dev); deep_curve, deep_r2 = probe_curve(deep, 6, dev)
    shal = train(1, 1, dev); shal_curve, shal_r2 = probe_curve(shal, 1, dev)

    f1 = bool(deep_curve[-1] - deep_curve[1] > 0.3 and deep_curve[1] < 0.6)
    f2 = bool(deep_curve[0] < 0.3)
    f3 = bool(deep_r2 > 0.8)
    f4 = bool(shal_curve[1] > 0.7)
    out = {"deep_curve": deep_curve, "deep_query_R2": deep_r2, "shallow_curve": shal_curve,
           "shallow_query_R2": shal_r2, "D_deep": 6, "D_shallow": 1,
           "F1_deep_ramp": f1, "F2_deep_input_illegible": f2, "F3_deep_solved": f3,
           "F4_shallow_steps": f4, "depth_ramp_confirmed": bool(f1 and f2 and f3 and f4)}
    print("deep (D=6) legibility by layer:   ", [f"{r:.2f}" for r in deep_curve], f"| R²={deep_r2:.3f}")
    print("shallow (D=1) legibility by layer:", [f"{r:.2f}" for r in shal_curve], f"| R²={shal_r2:.3f}")
    print(f"F1 deep ramp (last {deep_curve[-1]:.2f} - layer1 {deep_curve[1]:.2f} >0.3 & layer1<0.6): {f1}")
    print(f"F2 deep input illegible (layer0 {deep_curve[0]:.2f} <0.3): {f2}")
    print(f"F3 deep solved (R² {deep_r2:.2f} >0.8): {f3}")
    print(f"F4 shallow steps fast (layer1 {shal_curve[1]:.2f} >0.7): {f4}")
    print(f"\nDEPTH RAMP (deep-composition latent): {out['depth_ramp_confirmed']}")
    (RESULTS / "44_depth_ramp.json").write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(figsize=(7.5, 5))
    ax.plot(range(len(deep_curve)), deep_curve, "o-", color="seagreen", label=f"deep D=6 (sequential) — R²={deep_r2:.2f}")
    ax.plot(range(len(shal_curve)), shal_curve, "s--", color="crimson", label=f"shallow D=1 — R²={shal_r2:.2f}")
    ax.set_xlabel("layer  (0 = input embedding,  last = output)")
    ax.set_ylabel("linear legibility r of latent θ"); ax.set_ylim(-0.2, 1)
    ax.set_title("depth-of-emergence RAMP: deep composition climbs layer by layer")
    ax.legend(fontsize=8); fig.tight_layout(); fig.savefig(RESULTS / "44_depth_ramp.png", dpi=140)
    print("saved results/44_depth_ramp.json + .png")


if __name__ == "__main__":
    main()
