"""Step 43 — thread D follow-up: a RELATIONAL latent that's illegible at input -> real depth climb.

Script 42's depth-of-emergence was a NULL because the latent was already ~0.70 linearly legible at
layer 0 (a smooth regression latent is readable from pooled examples). The diagnosis: depth-of-
emergence needs the latent to be INITIALLY linearly inaccessible — a property the net must COMPUTE
over depth. Here we engineer exactly that.

Task (in-context rotation): each example token is a pair (u_i, v_i = R(theta) u_i + noise); the
latent theta is the rotation ANGLE relating the pair — a RELATION (angle(v)-angle(u)), nonlinear in
the token and ZERO under linear pooling (mean of R(theta)u over random u ~ 0, independent of theta).
The model must infer theta in-context to answer a held-out query u_q -> R(theta) u_q. Probe the linear
legibility of theta at each layer's pooled rep -> expect a CLIMB (illegible input -> legible output).

Control (additive): v_i = u_i + theta*c with c fixed -> mean(v-u) = theta*c, so theta IS linearly
present at the input -> expect a FLAT-HIGH curve (depth climb is specific to the relational latent).

Trained on FRESH in-context batches each step (the net learns the general skill, not fixed objects);
probed on a held-out fixed set. Gates (pre-reg 2026-06-16):
  E1 emergence (rotation): last-layer legibility - layer1 > 0.3.
  E2 input illegible (rotation): layer0 (pooled embedding) legibility < 0.3.
  E3 control flat-high (additive): layer0 > 0.6 AND last - layer0 < 0.2.
  E4 task solved (rotation): query R^2 > 0.9 (theta is actually used, so a low early curve = genuine).
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
from sklearn.linear_model import RidgeCV
from sklearn.model_selection import cross_val_predict
from torch import nn

DEPTH, DMODEL, KEX, QN = 6, 128, 32, 4
STEPS, N_PROBE = 9000, 512
CVEC = np.array([1.0, -0.5], dtype=np.float32)


def make_batch(B, rng, noise=0.1, easy=False):
    theta = rng.uniform(-1.0, 1.0, B).astype(np.float32)            # latent angle in [-1,1] rad
    U = rng.normal(size=(B, KEX, 2)).astype(np.float32)
    Uq = rng.normal(size=(B, QN, 2)).astype(np.float32)
    if easy:
        V = U + theta[:, None, None] * CVEC[None, None, :]
        Vq = Uq + theta[:, None, None] * CVEC[None, None, :]
    else:
        c, s = np.cos(theta)[:, None], np.sin(theta)[:, None]       # (B,1)
        V = np.stack([c * U[..., 0] - s * U[..., 1], s * U[..., 0] + c * U[..., 1]], -1)
        Vq = np.stack([c * Uq[..., 0] - s * Uq[..., 1], s * Uq[..., 0] + c * Uq[..., 1]], -1)
        V = V + noise * rng.normal(size=V.shape).astype(np.float32)  # noisy examples -> reward aggregation
    tokens = np.concatenate([U, V], -1).astype(np.float32)          # (B,KEX,4)
    return (torch.from_numpy(tokens), torch.from_numpy(Uq), torch.from_numpy(Vq),
            torch.from_numpy(theta))


class TF(nn.Module):
    def __init__(self, depth=DEPTH, d=DMODEL):
        super().__init__()
        self.embed = nn.Linear(4, d)
        self.layers = nn.ModuleList([
            nn.TransformerEncoderLayer(d, 4, 2 * d, batch_first=True, dropout=0.0, norm_first=True)
            for _ in range(depth)])
        self.head = nn.Sequential(nn.Linear(2 + d, d), nn.GELU(), nn.Linear(d, d), nn.GELU(), nn.Linear(d, 2))

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


def train(easy, seed):
    torch.manual_seed(seed); rng = np.random.default_rng(seed)
    m = TF(); opt = torch.optim.Adam(m.parameters(), lr=1e-3)
    tag = "easy" if easy else "rot"
    for step in range(STEPS):
        tokens, Uq, Vq, _ = make_batch(128, rng, easy=easy)
        loss = nn.functional.mse_loss(m(tokens, Uq), Vq)
        opt.zero_grad(); loss.backward(); opt.step()
        if step % 500 == 0:
            progress(f"43_{tag}", step, STEPS, loss=float(loss.detach()))
    m.eval()
    return m


def probe_curve(m, easy):
    rng = np.random.default_rng(123)
    tokens, Uq, Vq, theta = make_batch(N_PROBE, rng, easy=easy)
    theta = theta.numpy()
    with torch.no_grad():
        reps = [r.numpy() for r in m.layer_reps(tokens)]
        pred = m(tokens, Uq).numpy()
    r2 = float(1 - np.mean((pred - Vq.numpy()) ** 2) / np.var(Vq.numpy()))
    curve = []
    for R in reps:
        yh = cross_val_predict(RidgeCV(alphas=[0.1, 1, 10, 100]), R, theta, cv=5)
        curve.append(float(np.corrcoef(yh, theta)[0, 1]))
    return curve, r2


def main():
    rot = train(False, 0); rot_curve, rot_r2 = probe_curve(rot, False)
    easy = train(True, 1); easy_curve, easy_r2 = probe_curve(easy, True)

    e1 = bool(rot_curve[-1] - rot_curve[1] > 0.3)
    e2 = bool(rot_curve[0] < 0.3)
    e3 = bool(easy_curve[0] > 0.6 and easy_curve[-1] - easy_curve[0] < 0.2)
    e4 = bool(rot_r2 > 0.9)
    out = {"rotation_curve": rot_curve, "rotation_query_R2": rot_r2,
           "additive_curve": easy_curve, "additive_query_R2": easy_r2,
           "E1_emergence": e1, "E2_input_illegible": e2, "E3_control_flat_high": e3,
           "E4_task_solved": e4, "depth_of_emergence_confirmed": bool(e1 and e2 and e3 and e4)}
    print("rotation (relational) legibility by layer:", [f"{r:.2f}" for r in rot_curve], f"| query R²={rot_r2:.3f}")
    print("additive (linear)     legibility by layer:", [f"{r:.2f}" for r in easy_curve], f"| query R²={easy_r2:.3f}")
    print(f"E1 emergence (rot last {rot_curve[-1]:.2f} - layer1 {rot_curve[1]:.2f} > 0.3): {e1}")
    print(f"E2 input illegible (rot layer0 {rot_curve[0]:.2f} < 0.3): {e2}")
    print(f"E3 control flat-high (add layer0 {easy_curve[0]:.2f}>0.6, last-layer0 {easy_curve[-1]-easy_curve[0]:.2f}<0.2): {e3}")
    print(f"E4 task solved (rot query R² {rot_r2:.2f} > 0.9): {e4}")
    print(f"\nDEPTH-OF-EMERGENCE (relational latent): {out['depth_of_emergence_confirmed']}")
    (RESULTS / "43_depth_emergence.json").write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(figsize=(7.5, 5))
    L = range(len(rot_curve))
    ax.plot(L, rot_curve, "o-", color="seagreen", label=f"rotation (relational, illegible input) — R²={rot_r2:.2f}")
    ax.plot(L, easy_curve, "s--", color="crimson", label=f"additive (linear, legible input) — R²={easy_r2:.2f}")
    ax.set_xlabel("layer  (0 = input embedding,  last = output)")
    ax.set_ylabel("linear legibility r of latent θ"); ax.set_ylim(0, 1)
    ax.set_title("depth-of-emergence appears only when the latent is illegible at the input")
    ax.legend(fontsize=8); fig.tight_layout(); fig.savefig(RESULTS / "43_depth_emergence.png", dpi=140)
    print("saved results/43_depth_emergence.json + .png")


if __name__ == "__main__":
    main()
