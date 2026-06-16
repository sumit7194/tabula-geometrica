"""Step 71b — STRUCTURE vs LEGIBILITY, the faithful test: NONLINEAR readout (no linear anchor).

71 was an instructive negative: with a LINEAR readout y=<P,w>, BOTH update rules kept the rotating charge
linearly legible (0.99) — the readout anchored w to Q, so structure bought only conservation, not legibility.
To actually test the third leg ("structure restores legibility"), remove the linear anchor: a NONLINEAR
readout y = s + 0.7 s^3  (s=<P_t,Q_t>; monotone, invertible, info-preserving but not linear) read by a
NONLINEAR head MLP([w_t, P_t]). Now nothing forces w linearly onto Q — the latent is FREE to scramble.

Hypothesis: amortization makes w0 legible (Phase I); an ORTHOGONAL update rotates it rigidly so legibility
PERSISTS through time; a GENERIC update, unconstrained and with a nonlinear head to absorb any distortion,
ERODES the linear alignment over the path (info stays — nonlinear-decodable — but goes linearly illegible:
the probe-ladder scramble, Phase H Row 2 / Phase C).

Pre-reg (2026-06-17):
  O1 both fit: held-out y R^2 > 0.9.
  O2 STRUCTURE RESTORES LEGIBILITY: linear-decode Q(t) from w(t) — orthogonal > 0.8, generic < 0.7,
     margin > 0.2.
  O3 THE SCRAMBLE SIGNATURE: for the generic model, nonlinear (kNN) decode >> linear decode (info present
     but illegible); for orthogonal, linear ~ nonlinear (genuinely legible). Confirms it is a legibility
     loss, not an information loss.
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
from sklearn.linear_model import Ridge
from sklearn.neighbors import KNeighborsRegressor
from sklearn.model_selection import cross_val_predict
from curvlib import RESULTS, progress
from torch import nn

STEPS = 9000
T = 24
KOBS = 9
DEV = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
torch.manual_seed(0)
OMEGA = torch.randn(3, 2) * 0.30


def skew(w):
    z = torch.zeros(w.shape[:-1] + (1,), device=w.device, dtype=w.dtype)
    x, y, zc = w[..., 0:1], w[..., 1:2], w[..., 2:3]
    return torch.stack([torch.cat([z, -zc, y], -1), torch.cat([zc, z, -x], -1), torch.cat([-y, x, z], -1)], -2)


def rot(omega):
    theta = omega.norm(dim=-1, keepdim=True).clamp_min(1e-8)
    K = skew(omega); a = (torch.sin(theta) / theta)[..., None]; b = ((1 - torch.cos(theta)) / theta ** 2)[..., None]
    I = torch.eye(3, device=omega.device, dtype=omega.dtype).expand(K.shape)
    return I + a * K + b * (K @ K)


def readout(s):                                  # nonlinear, monotone, invertible (no linear anchor)
    return s + 0.7 * s ** 3


def gen_batch(B, seed):
    g = torch.Generator().manual_seed(seed)
    c = torch.randn(B, T, 2, generator=g) * 0.8
    P = torch.eye(3)[torch.arange(T) % 3].expand(B, T, 3).clone()
    Q0 = torch.randn(B, 3, generator=g); Q0 = Q0 / Q0.norm(dim=-1, keepdim=True)
    Q = [Q0]
    for t in range(T - 1):
        Q.append((rot(c[:, t] @ OMEGA.T) @ Q[-1][..., None])[..., 0])
    Q = torch.stack(Q, 1)
    s = (P * Q).sum(-1)
    y = readout(s) + 0.01 * torch.randn(B, T, generator=g)
    return c, P, y, Q


class Encoder(nn.Module):
    def __init__(s):
        super().__init__(); s.gru = nn.GRU(6, 96, batch_first=True); s.out = nn.Linear(96, 3)
    def forward(s, c, P, y):
        tok = torch.cat([c[:, :KOBS], P[:, :KOBS], y[:, :KOBS, None]], -1)
        h, _ = s.gru(tok); return s.out(h[:, -1])


class Model(nn.Module):
    def __init__(s, orthogonal):
        super().__init__(); s.orthogonal = orthogonal; s.enc = Encoder()
        s.f = nn.Sequential(nn.Linear(2 if orthogonal else 5, 96), nn.GELU(), nn.Linear(96, 96), nn.GELU(), nn.Linear(96, 3))
        s.head = nn.Sequential(nn.Linear(6, 96), nn.GELU(), nn.Linear(96, 96), nn.GELU(), nn.Linear(96, 1))   # [w,P]->y, NONLINEAR

    def rollout(s, c, P, y):
        w = s.enc(c, P, y); W = [w]
        for t in range(T - 1):
            w = (rot(s.f(c[:, t])) @ w[..., None])[..., 0] if s.orthogonal else w + s.f(torch.cat([w, c[:, t]], -1))
            W.append(w)
        W = torch.stack(W, 1)
        yhat = s.head(torch.cat([W, P], -1))[..., 0]
        return yhat, W


def train(orthogonal, tag):
    m = Model(orthogonal).to(DEV); opt = torch.optim.Adam(m.parameters(), lr=1e-3)
    for step in range(STEPS):
        c, P, y, _ = gen_batch(256, seed=step + 1)
        yhat, _ = m.rollout(c.to(DEV), P.to(DEV), y.to(DEV))
        loss = nn.functional.mse_loss(yhat[:, KOBS:], y.to(DEV)[:, KOBS:])
        opt.zero_grad(); loss.backward(); opt.step()
        if step % 500 == 0: progress(tag, step, STEPS, loss=float(loss.detach()))
    return m


def decode(W, Q, knn=False):
    est = KNeighborsRegressor(15) if knn else Ridge(1.0)
    pred = cross_val_predict(est, W, Q, cv=5)
    return float(1 - np.sum((pred - Q) ** 2) / np.sum((Q - Q.mean(0)) ** 2))


def evaluate(m):
    c, P, y, Q = gen_batch(400, seed=99); m.eval()
    with torch.no_grad():
        yhat, W = m.rollout(c.to(DEV), P.to(DEV), y.to(DEV))
    yh = yhat[:, KOBS:].cpu().numpy().ravel(); yt = y[:, KOBS:].numpy().ravel()
    r2 = float(1 - np.sum((yh - yt) ** 2) / np.sum((yt - yt.mean()) ** 2))
    Wn = W[:, KOBS:].reshape(-1, 3).cpu().numpy(); Qn = Q[:, KOBS:].reshape(-1, 3).numpy()
    lin = decode(Wn, Qn, knn=False); non = decode(Wn, Qn, knn=True)
    # legibility erosion over time: linear decode at the first vs last quarter of the post-KOBS path
    ts = np.arange(KOBS, T); early = ts[: len(ts) // 2]; late = ts[len(ts) // 2:]
    We = W[:, early].reshape(-1, 3).cpu().numpy(); Qe = Q[:, early].reshape(-1, 3).numpy()
    Wl = W[:, late].reshape(-1, 3).cpu().numpy(); Ql = Q[:, late].reshape(-1, 3).numpy()
    return r2, lin, non, decode(We, Qe), decode(Wl, Ql)


def main():
    mo = train(True, "71b_ortho"); mg = train(False, "71b_generic")
    r2o, lino, nono, eo, lo = evaluate(mo); r2g, ling, nong, eg, lg = evaluate(mg)
    out = {"orthogonal": {"y_R2": r2o, "Q_linear_decode": lino, "Q_knn_decode": nono, "linear_early": eo, "linear_late": lo},
           "generic": {"y_R2": r2g, "Q_linear_decode": ling, "Q_knn_decode": nong, "linear_early": eg, "linear_late": lg}}
    o1 = bool(r2o > 0.9 and r2g > 0.9)
    o2 = bool(lino > 0.8 and ling < 0.7 and (lino - ling) > 0.2)
    o3 = bool((nong - ling) > 0.2 and abs(nono - lino) < 0.15)
    res = {**out, "O1_both_fit": o1, "O2_structure_restores_legibility": o2, "O3_scramble_signature": o3,
           "structure_restores_confirmed": bool(o1 and o2 and o3)}
    print(f"orthogonal : y R^2 {r2o:.3f} | Q linear {lino:.3f} knn {nono:.3f} | early {eo:.3f} late {lo:.3f}")
    print(f"generic    : y R^2 {r2g:.3f} | Q linear {ling:.3f} knn {nong:.3f} | early {eg:.3f} late {lg:.3f}")
    print(f"\nO1 both fit (y R^2>0.9): {o1}")
    print(f"O2 STRUCTURE RESTORES LEGIBILITY (ortho lin>0.8, generic lin<0.7, margin>0.2): {o2}")
    print(f"O3 scramble signature (generic knn>>linear; ortho linear~knn): {o3}")
    print(f"\nSTRUCTURE RESTORES LEGIBILITY under a nonlinear readout: {res['structure_restores_confirmed']}")
    (RESULTS / "71b_nonlinear_readout.json").write_text(json.dumps(res, indent=1))

    fig, ax = plt.subplots(1, 2, figsize=(13, 5))
    x = np.arange(2); w = 0.35
    ax[0].bar(x - w / 2, [lino, ling], w, color="seagreen", label="linear decode")
    ax[0].bar(x + w / 2, [nono, nong], w, color="slategray", label="kNN (nonlinear) decode")
    ax[0].axhline(0.8, color="k", ls="--", lw=0.8)
    ax[0].set_xticks(x); ax[0].set_xticklabels(["ORTHOGONAL-F", "GENERIC-F"]); ax[0].set_ylabel("Q(t) decode R²")
    ax[0].set_title("nonlinear readout: does structure keep Q legible?\n(scramble = linear low, nonlinear high)")
    ax[0].legend(fontsize=8)
    ax[1].plot([0, 1], [eo, lo], "o-", color="seagreen", label="orthogonal")
    ax[1].plot([0, 1], [eg, lg], "s-", color="crimson", label="generic")
    ax[1].set_xticks([0, 1]); ax[1].set_xticklabels(["early path", "late path"])
    ax[1].set_ylabel("linear decode R²"); ax[1].set_title("legibility erosion through time")
    ax[1].legend(fontsize=8); fig.tight_layout(); fig.savefig(RESULTS / "71b_nonlinear_readout.png", dpi=140)
    print("saved results/71b_nonlinear_readout.json + .png")


if __name__ == "__main__":
    main()
