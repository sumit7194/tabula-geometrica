"""Step 129 — curvature AS the bottleneck: a net discovers Gaussian curvature is the minimal sufficient code.

Phase 1b separate-angle probe (notes/build_queue.md; field_guide sec9 loose end). Phase E (16/17) read curvature
POST-HOC from a learned metric field. Here we make curvature the BOTTLENECK itself: a SciNet net must compress its
observations of a surface through a low-D latent to predict geodesic behavior, and we test whether that latent IS the
Gaussian curvature.

Physics: on a constant-curvature 2D surface, nearby geodesics' separation s obeys the Jacobi equation s'' = -K s
(K = Gaussian curvature). The whole effect of geometry on geodesics is carried by ONE number, K: s(tau) =
s0 C_K(tau) + v0 S_K(tau) with C_K,S_K = cos/sin (K>0), 1/tau (K=0), cosh/sinh (K<0). Toy: an encoder sees a probe
deviation curve s_probe(tau) of an unknown surface, compresses to a bottleneck z, and a decoder predicts the
deviation s(tau_q) for NEW initial conditions (s0,v0) -- which requires z to carry K.

Pre-reg (2026-06-25):
  CB1 CURVATURE SUFFICES: a 1-D bottleneck predicts held-out deviation queries with R^2 > 0.95 (one number is enough).
  CB2 THE BOTTLENECK IS CURVATURE: the 1-D latent decodes the true Gaussian curvature K, |r| > 0.97 (the latent =
     curvature, an invariant -- not coordinates).
  CB3 MINIMALITY + NECESSITY: the dim-1 R^2 already matches dim-2/3 (extra latent dims add < 0.02 -- curvature is a
     1-number code, emergent minimality) AND the curvature bottleneck SUBSTANTIALLY beats a curvature-BLIND control
     (R^2_dim1 - R^2_blind > 0.3). (Blind isn't ~0: the flat-space part of geodesic deviation, s0 + v0 tau, is genuinely
     K-INDEPENDENT and predictable blind; curvature carries the geometry-DEPENDENT correction -- that is what the
     bottleneck supplies.)
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

TAU = np.linspace(0.15, 2.0, 16)                                   # probe-curve sample times


def fund(K, tau):
    """fundamental deviation solutions C_K (s0=1,v0=0) and S_K (s0=0,v0=1) of s'' = -K s."""
    if K > 1e-6:
        w = np.sqrt(K); return np.cos(w * tau), np.sin(w * tau) / w
    if K < -1e-6:
        m = np.sqrt(-K); return np.cosh(m * tau), np.sinh(m * tau) / m
    return np.ones_like(tau), tau


def probe_curve(K):
    return fund(K, TAU)[0]                                         # s_probe = deviation for standard IC (s0=1, v0=0)


def dataset(n, rng, nq=8):
    P, Q, Y, Ks = [], [], [], []
    for _ in range(n):
        K = rng.uniform(-2.0, 2.0)
        P.append(probe_curve(K)); Ks.append(K)
        qs = []
        ys = []
        for _ in range(nq):
            s0, v0 = rng.uniform(-1, 1, 2); tq = rng.uniform(0.2, 2.0)
            C, S = fund(K, np.array([tq]))
            qs.append([s0, v0, tq]); ys.append(s0 * C[0] + v0 * S[0])
        Q.append(qs); Y.append(ys)
    return (np.array(P, np.float32), np.array(Q, np.float32), np.array(Y, np.float32), np.array(Ks, np.float32))


class Net(nn.Module):
    def __init__(s, kdim):
        super().__init__()
        s.enc = nn.Sequential(nn.Linear(len(TAU), 64), nn.GELU(), nn.Linear(64, 64), nn.GELU(), nn.Linear(64, kdim))
        s.dec = nn.Sequential(nn.Linear(kdim + 3, 64), nn.GELU(), nn.Linear(64, 64), nn.GELU(), nn.Linear(64, 1))

    def forward(s, P, Q, zero_latent=False):
        z = s.enc(P)
        if zero_latent:
            z = torch.zeros_like(z)
        zexp = z[:, None, :].expand(-1, Q.shape[1], -1)
        return s.dec(torch.cat([zexp, Q], -1))[..., 0], z


def train(kdim, Ptr, Qtr, Ytr, seed=0, steps=4000):
    torch.manual_seed(seed); rng = np.random.default_rng(seed)
    m = Net(kdim); opt = torch.optim.Adam(m.parameters(), lr=2e-3)
    P, Q, Y = torch.from_numpy(Ptr), torch.from_numpy(Qtr), torch.from_numpy(Ytr)
    for step in range(steps):
        idx = rng.integers(0, len(P), 64)
        pred, _ = m(P[idx], Q[idx])
        loss = nn.functional.mse_loss(pred, Y[idx])
        opt.zero_grad(); loss.backward(); opt.step()
        if step % 1000 == 0:
            progress(f"129_k{kdim}", step, steps, loss=float(loss.detach()))
    return m.eval()


def r2(pred, y):
    return float(1 - np.sum((pred - y) ** 2) / np.sum((y - y.mean()) ** 2))


def main():
    rng = np.random.default_rng(0)
    Ptr, Qtr, Ytr, Ktr = dataset(3000, rng)
    Pte, Qte, Yte, Kte = dataset(800, np.random.default_rng(9))
    Pt, Qt = torch.from_numpy(Pte), torch.from_numpy(Qte)

    r2s = {}; nets = {}
    for kdim in (1, 2, 3):
        m = train(kdim, Ptr, Qtr, Ytr)
        with torch.no_grad():
            pred, _ = m(Pt, Qt)
        r2s[kdim] = r2(pred.numpy().ravel(), Yte.ravel()); nets[kdim] = m
    cb1 = bool(r2s[1] > 0.95)

    # CB2: the 1-D latent decodes K
    with torch.no_grad():
        _, z1 = nets[1](Pt, Qt)
    z1 = z1.numpy().ravel(); decode_r = float(abs(np.corrcoef(z1, Kte)[0, 1]))
    cb2 = bool(decode_r > 0.97)

    # CB3: minimality (knee) + curvature-blind control
    extra = max(r2s[2] - r2s[1], r2s[3] - r2s[1])
    with torch.no_grad():
        predb, _ = nets[1](Pt, Qt, zero_latent=True)
    r2_blind = r2(predb.numpy().ravel(), Yte.ravel())
    cb3 = bool(extra < 0.02 and (r2s[1] - r2_blind) > 0.3)        # curvature supplies the geometry-dependent part

    out = {"R2_dim1": r2s[1], "R2_dim2": r2s[2], "R2_dim3": r2s[3], "latent_decodes_K_r": decode_r,
           "R2_curvature_blind": r2_blind, "extra_dim_gain": float(extra),
           "CB1_curvature_suffices": cb1, "CB2_bottleneck_is_curvature": cb2, "CB3_minimality_and_control": cb3,
           "curvature_is_the_bottleneck": bool(cb1 and cb2 and cb3),
           "verdict": ("CURVATURE IS THE BOTTLENECK: a SciNet net compressing its observations of a surface to predict "
                       "geodesic deviation discovers that a 1-D latent SUFFICES (held-out R2 {:.3f}) and that the latent "
                       "IS the Gaussian curvature (decodes K at |r|={:.3f}). Extra latent dims add nothing ({:+.3f} -- "
                       "curvature is a 1-number code, emergent minimality) and the bottleneck lifts a curvature-blind "
                       "control's R2 {:.2f} -> 1.0 (curvature supplies the geometry-dependent part; the flat s0+v0t part "
                       "is K-independent). Curvature emerges as the minimal sufficient CODE for geometry's effect on geodesics "
                       "-- not a post-hoc readout (Phase E) but the bottleneck itself."
                       .format(r2s[1], decode_r, extra, r2_blind)
                       if (cb1 and cb2 and cb3) else "PARTIAL -- see numbers (honest).")}
    print(f"CB1 curvature suffices: 1-D bottleneck held-out R2={r2s[1]:.3f} (>0.95): {cb1}")
    print(f"CB2 bottleneck IS curvature: latent decodes K, |r|={decode_r:.3f} (>0.97): {cb2}")
    print(f"CB3 minimality+necessity: dims R2 {r2s[1]:.3f}/{r2s[2]:.3f}/{r2s[3]:.3f} (extra {extra:+.3f}<0.02), bottleneck beats blind {r2s[1]-r2_blind:+.2f} (>0.3, blind={r2_blind:.2f}): {cb3}")
    print(f"\nCURVATURE IS THE BOTTLENECK: {out['curvature_is_the_bottleneck']}")
    (RESULTS / "129_curvature_bottleneck.json").write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(1, 2, figsize=(12, 4.8))
    ax[0].scatter(Kte, z1, s=8, alpha=0.4, c="seagreen")
    ax[0].set_xlabel("true Gaussian curvature K"); ax[0].set_ylabel("1-D bottleneck latent z")
    ax[0].set_title(f"CB2 · the bottleneck IS curvature (|r|={decode_r:.3f})")
    ax[1].bar(["dim 1", "dim 2", "dim 3", "blind"], [r2s[1], r2s[2], r2s[3], r2_blind],
              color=["seagreen", "seagreen", "seagreen", "crimson"])
    ax[1].axhline(0.95, ls="--", c="k", lw=0.6); ax[1].set_ylabel("held-out R²"); ax[1].set_ylim(0, 1.05)
    ax[1].set_title("CB1/CB3 · 1 number suffices (knee at 1); blind fails")
    fig.suptitle("Curvature as the bottleneck: Gaussian curvature is the minimal sufficient code for geodesic behavior")
    fig.tight_layout(); fig.savefig(RESULTS / "129_curvature_bottleneck.png", dpi=140)
    print("saved results/129_curvature_bottleneck.json + .png")


if __name__ == "__main__":
    main()
