"""Step 71 — OVERNIGHT #5: STRUCTURE RESTORES LEGIBILITY — the third leg of the legibility law.

The legibility law has three claimed legs: amortize->legible (static, Phase I); generic evolution->scrambles
(dynamic, Phase H Row 2 — the Wong color charge Q(t) tracked only NONLINEARLY, |Q| drift 0.47); and
structure->restores. The third leg was an OPEN HYPOTHESIS. This tests it cleanly.

A hidden color charge Q(t) in R^3 parallel-transports along a path: Q(t+1) = exp(skew(omega_t)) Q(t), an
ORTHOGONAL rotation driven by the observed gauge context c_t (|Q| conserved — web-verified Wong dynamics).
Observable each step: y_t = <P_t, Q(t)> (a known probe projection of the hidden charge). An AMORTIZED
encoder infers w0 from the first k steps; then a learned update F evolves w(t) and predicts y_t. Two F's,
SAME 3-D latent and similar capacity (the only difference is structure):
  GENERIC-F:    w(t+1) = w(t) + MLP([w(t), c_t])           (unconstrained — the scrambler)
  ORTHOGONAL-F: w(t+1) = exp(skew(MLP(c_t))) w(t)          (a rotation — conserves |w| by construction)

Pre-reg (2026-06-17):
  O1 both fit the observable: held-out y R^2 > 0.9.
  O2 STRUCTURE RESTORES LEGIBILITY: linear decode of the true Q(t) from w(t) — ORTHOGONAL-F R^2 > 0.8
     (legible), GENERIC-F clearly lower and < 0.7 (scrambled), margin > 0.2. (The Phase H Row 2 effect,
     fixed by structure.)
  O3 CONSERVATION: |w(t)| relative drift across the path — orthogonal near 0 (< 0.02), generic large
     (> 0.1). The invariant is preserved exactly only by the structure-preserving update.
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
from sklearn.model_selection import cross_val_predict
from curvlib import RESULTS, progress
from torch import nn

STEPS = 9000
T = 24            # path length
KOBS = 9          # steps the encoder sees to infer w0 (3 full basis cycles)
DEV = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
torch.manual_seed(0)
OMEGA = torch.randn(3, 2) * 0.30          # fixed world map: context(2) -> rotation vector(3) (gentle)


def skew(w):                               # w (...,3) -> (...,3,3)
    z = torch.zeros(w.shape[:-1] + (1,), device=w.device, dtype=w.dtype)
    x, y, zc = w[..., 0:1], w[..., 1:2], w[..., 2:3]
    row0 = torch.cat([z, -zc, y], -1); row1 = torch.cat([zc, z, -x], -1); row2 = torch.cat([-y, x, z], -1)
    return torch.stack([row0, row1, row2], -2)


def rot(omega):                            # exp(skew(omega)), orthogonal (...,3,3)
    theta = omega.norm(dim=-1, keepdim=True).clamp_min(1e-8)
    K = skew(omega)
    a = (torch.sin(theta) / theta)[..., None]
    b = ((1 - torch.cos(theta)) / theta ** 2)[..., None]
    I = torch.eye(3, device=omega.device, dtype=omega.dtype).expand(K.shape)
    return I + a * K + b * (K @ K)


def gen_batch(B, seed):
    """returns context c (B,T,2), probe P (B,T,3), obs y (B,T), true charge Q (B,T,3)."""
    g = torch.Generator().manual_seed(seed)
    c = torch.randn(B, T, 2, generator=g) * 0.8
    basis = torch.eye(3)[torch.arange(T) % 3]         # cycling probe e1,e2,e3,... -> identifiable w0
    P = basis.expand(B, T, 3).clone()
    Q0 = torch.randn(B, 3, generator=g); Q0 = Q0 / Q0.norm(dim=-1, keepdim=True)
    Q = [Q0]
    for t in range(T - 1):
        om = c[:, t] @ OMEGA.T                       # (B,3)
        Q.append((rot(om) @ Q[-1][..., None])[..., 0])
    Q = torch.stack(Q, 1)                            # (B,T,3)
    y = (P * Q).sum(-1) + 0.01 * torch.randn(B, T, generator=g)
    return c, P, y, Q


class Encoder(nn.Module):                  # amortized: GRU over first KOBS (c,P,y) -> w0
    def __init__(s):
        super().__init__(); s.gru = nn.GRU(6, 96, batch_first=True); s.out = nn.Linear(96, 3)
    def forward(s, c, P, y):
        tok = torch.cat([c[:, :KOBS], P[:, :KOBS], y[:, :KOBS, None]], -1)   # (B,KOBS,6)
        h, _ = s.gru(tok)
        return s.out(h[:, -1])                                               # last hidden -> (B,3)


class Model(nn.Module):
    def __init__(s, orthogonal):
        super().__init__(); s.orthogonal = orthogonal; s.enc = Encoder()
        if orthogonal:
            s.f = nn.Sequential(nn.Linear(2, 96), nn.GELU(), nn.Linear(96, 96), nn.GELU(), nn.Linear(96, 3))
        else:
            s.f = nn.Sequential(nn.Linear(5, 96), nn.GELU(), nn.Linear(96, 96), nn.GELU(), nn.Linear(96, 3))

    def rollout(s, c, P, y):
        w = s.enc(c, P, y); W = [w]
        for t in range(T - 1):
            if s.orthogonal:
                w = (rot(s.f(c[:, t])) @ w[..., None])[..., 0]
            else:
                w = w + s.f(torch.cat([w, c[:, t]], -1))
            W.append(w)
        W = torch.stack(W, 1)                         # (B,T,3)
        yhat = (P * W).sum(-1)                         # (B,T)
        return yhat, W


def train(orthogonal, tag):
    m = Model(orthogonal).to(DEV); opt = torch.optim.Adam(m.parameters(), lr=1e-3)
    for step in range(STEPS):
        c, P, y, _ = gen_batch(256, seed=step + 1)
        c, P, y = c.to(DEV), P.to(DEV), y.to(DEV)
        yhat, _ = m.rollout(c, P, y)
        loss = nn.functional.mse_loss(yhat[:, KOBS:], y[:, KOBS:])     # predict beyond the observed window
        opt.zero_grad(); loss.backward(); opt.step()
        if step % 500 == 0: progress(tag, step, STEPS, loss=float(loss.detach()))
    return m


def evaluate(m):
    c, P, y, Q = gen_batch(400, seed=99); c, P, y = c.to(DEV), P.to(DEV), y.to(DEV)
    m.eval()
    with torch.no_grad():
        yhat, W = m.rollout(c, P, y)
    yh = yhat[:, KOBS:].cpu().numpy().ravel(); yt = y[:, KOBS:].cpu().numpy().ravel()
    r2 = float(1 - np.sum((yh - yt) ** 2) / np.sum((yt - yt.mean()) ** 2))
    # legibility: linear decode of true Q(t) from w(t) over t>=KOBS
    Wn = W[:, KOBS:].reshape(-1, 3).cpu().numpy(); Qn = Q[:, KOBS:].reshape(-1, 3).numpy()
    pred = cross_val_predict(Ridge(1.0), Wn, Qn, cv=5)
    leg = float(1 - np.sum((pred - Qn) ** 2) / np.sum((Qn - Qn.mean(0)) ** 2))
    # conservation: relative drift of |w(t)| across the path
    norms = W.norm(dim=-1).cpu().numpy()               # (B,T)
    drift = float(np.mean(norms.std(1) / (norms.mean(1) + 1e-9)))
    return r2, leg, drift


def main():
    mo = train(True, "71_ortho"); mg = train(False, "71_generic")
    r2o, lego, drifto = evaluate(mo); r2g, legg, driftg = evaluate(mg)
    out = {"orthogonal": {"y_R2": r2o, "Q_decode_R2": lego, "norm_drift": drifto},
           "generic": {"y_R2": r2g, "Q_decode_R2": legg, "norm_drift": driftg}}
    o1 = bool(r2o > 0.9 and r2g > 0.9)
    o2 = bool(lego > 0.8 and legg < 0.7 and (lego - legg) > 0.2)
    o3 = bool(drifto < 0.02 and driftg > 0.1)
    res = {**out, "O1_both_fit": o1, "O2_structure_restores_legibility": o2, "O3_conservation": o3,
           "structure_restores_confirmed": bool(o1 and o2 and o3)}
    print(f"orthogonal : y R^2 {r2o:.3f} | Q(t) linear-decode R^2 {lego:.3f} | |w| drift {drifto:.4f}")
    print(f"generic    : y R^2 {r2g:.3f} | Q(t) linear-decode R^2 {legg:.3f} | |w| drift {driftg:.4f}")
    print(f"\nO1 both fit observable (y R^2>0.9): {o1}")
    print(f"O2 STRUCTURE RESTORES LEGIBILITY (ortho>0.8, generic<0.7, margin>0.2): {o2}")
    print(f"O3 conservation (|w| drift ortho<0.02, generic>0.1): {o3}")
    print(f"\nSTRUCTURE RESTORES LEGIBILITY (3rd leg of the legibility law): {res['structure_restores_confirmed']}")
    (RESULTS / "71_orthogonal_F.json").write_text(json.dumps(res, indent=1))

    fig, ax = plt.subplots(1, 2, figsize=(13, 5))
    ax[0].bar([0, 1], [lego, legg], color=["seagreen", "crimson"])
    ax[0].axhline(0.8, color="k", ls="--", lw=0.8, label="legible threshold")
    ax[0].set_xticks([0, 1]); ax[0].set_xticklabels(["ORTHOGONAL-F\n(structure)", "GENERIC-F\n(scrambler)"])
    ax[0].set_ylabel("linear decode R² of the rotating charge Q(t)")
    ax[0].set_title("structure restores legibility of a DYNAMIC charge\n(same latent, same capacity)")
    ax[0].legend(fontsize=8)
    ax[1].bar([0, 1], [drifto, driftg], color=["seagreen", "crimson"])
    ax[1].set_xticks([0, 1]); ax[1].set_xticklabels(["ORTHOGONAL-F", "GENERIC-F"])
    ax[1].set_ylabel("|w(t)| relative drift"); ax[1].set_title("the conserved invariant |Q|:\nheld by structure, lost by a generic update")
    fig.tight_layout(); fig.savefig(RESULTS / "71_orthogonal_F.png", dpi=140)
    print("saved results/71_orthogonal_F.json + .png")


if __name__ == "__main__":
    main()
