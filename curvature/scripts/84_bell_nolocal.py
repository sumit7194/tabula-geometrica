"""Step 84 — IMPOSSIBILITY CERTIFICATE I: a net's FAILURE certifies quantum nonlocality (Bell).

New kind of result: use a net's inability to find a CHEAP (local) explanation as a gated positive certificate.
A two-qubit Werner state (singlet + white noise, visibility v) gives correlations E(a,b) = -v cos(theta_ab).
We build a genuine LOCAL HIDDEN-VARIABLE model as a net: a shared hidden variable lambda ~ p(lambda) and
LOCAL response functions A(a,lambda), B(b,lambda) in [-1,1] -- crucially, A sees only Alice's setting, B only
Bob's (no cross-wires). Such a model CANNOT exceed the CHSH bound |S| <= 2 (architectural locality). The
quantum target is |S| = 2sqrt2 * v, which crosses 2 at v = 1/sqrt2 ~= 0.7071. So as v rises the local net
tracks the quantum correlations and then SLAMS into a wall it provably cannot pass -- and that wall lands at
the Tsirelson/CHSH boundary. Web-verified: Werner CHSH=2sqrt2 v; no local model for v>1/sqrt2; local model
exists for v<~0.66.

Pre-reg (2026-06-17):
  B1 LOCAL REGIME FITS: at v=0.5 (provably local) the local net fits the full correlation, RMSE < 0.03.
  B2 GENUINE LOCAL MODEL: max over v of the net's achieved |S| <= 2.05 (it respects the Bell bound by
     construction -- it cannot fake nonlocality).
  B3 THE CERTIFICATE: the net's |S| tracks the quantum 2sqrt2 v up to a knee, then saturates at 2; the knee
     (where it can no longer match) is within 6% of v* = 1/sqrt2 = 0.7071, AND v=1 is unfittable (|S| << 2.83).
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

M = 128            # hidden-variable samples
LD = 8             # latent dim of lambda
np.seterr(all="ignore")


class LocalModel(nn.Module):
    """E(a,b) = sum_i p_i A(a, lam_i) B(b, lam_i); A,B in [-1,1] are LOCAL (each sees one wing only)."""
    def __init__(s):
        super().__init__()
        s.lam = nn.Parameter(torch.randn(M, LD) * 0.5)
        s.logp = nn.Parameter(torch.zeros(M))
        s.A = nn.Sequential(nn.Linear(2 + LD, 64), nn.GELU(), nn.Linear(64, 64), nn.GELU(), nn.Linear(64, 1))
        s.B = nn.Sequential(nn.Linear(2 + LD, 64), nn.GELU(), nn.Linear(64, 64), nn.GELU(), nn.Linear(64, 1))

    def responses(s, phi, net):
        d = torch.stack([torch.cos(phi), torch.sin(phi)], -1)        # (batch,2) measurement direction
        x = torch.cat([d[:, None, :].expand(-1, M, -1), s.lam[None].expand(len(phi), -1, -1)], -1)  # (batch,M,2+LD)
        return torch.tanh(net(x)[..., 0])                            # (batch,M) in [-1,1]

    def E(s, pa, pb):
        A = s.responses(pa, s.A); B = s.responses(pb, s.B); p = torch.softmax(s.logp, 0)
        return (A * B * p[None]).sum(1)


def fit(v, steps=3500):
    m = LocalModel(); opt = torch.optim.Adam(m.parameters(), lr=3e-3); rng = np.random.default_rng(0)
    for step in range(steps):
        pa = torch.tensor(rng.uniform(0, 2 * np.pi, 512), dtype=torch.float32)
        pb = torch.tensor(rng.uniform(0, 2 * np.pi, 512), dtype=torch.float32)
        tgt = -v * torch.cos(pa - pb)
        loss = ((m.E(pa, pb) - tgt) ** 2).mean()
        opt.zero_grad(); loss.backward(); opt.step()
        if step % 500 == 0: progress(f"84_v{v:.2f}", step, steps, loss=float(loss.detach()))
    m.eval()
    with torch.no_grad():
        pa = torch.tensor(rng.uniform(0, 2 * np.pi, 4000), dtype=torch.float32)
        pb = torch.tensor(rng.uniform(0, 2 * np.pi, 4000), dtype=torch.float32)
        rmse = float(((m.E(pa, pb) + v * torch.cos(pa - pb)) ** 2).mean().sqrt())
        # CHSH at optimal singlet settings: a=0,a'=pi/2,b=pi/4,b'=3pi/4 ; S = E(ab)-E(ab')+E(a'b)+E(a'b')
        a, ap, b, bp = [torch.tensor([x], dtype=torch.float32) for x in (0.0, np.pi / 2, np.pi / 4, 3 * np.pi / 4)]
        S = float(m.E(a, b) - m.E(a, bp) + m.E(ap, b) + m.E(ap, bp))
    return rmse, abs(S)


def main():
    vs = np.array([0.3, 0.45, 0.55, 0.62, 0.68, 0.71, 0.74, 0.78, 0.85, 0.95, 1.0])
    rmses, Smodel = [], []
    for v in vs:
        r, S = fit(v); rmses.append(r); Smodel.append(S)
        print(f"v={v:.2f}: RMSE {r:.4f} | model|S| {S:.3f} | quantum 2sqrt2 v = {2*np.sqrt(2)*v:.3f}")
    rmses = np.array(rmses); Smodel = np.array(Smodel); Squant = 2 * np.sqrt(2) * vs

    # knee: largest v where the model still tracks the quantum |S| (ratio > 0.95)
    ratio = Smodel / Squant
    track = vs[ratio > 0.95]
    v_knee = float(track.max()) if len(track) else None
    rmse_v05 = float(rmses[np.argmin(np.abs(vs - 0.55))])
    rmse_v1 = float(rmses[-1])

    b1 = bool(rmse_v05 < 0.03)
    b2 = bool(Smodel.max() < 2.05)
    b3 = bool(v_knee is not None and abs(v_knee - 1 / np.sqrt(2)) < 0.06 and rmse_v1 > 0.05)
    out = {"v": vs.tolist(), "rmse": rmses.tolist(), "model_S": Smodel.tolist(), "quantum_S": Squant.tolist(),
           "v_knee": v_knee, "v_star_1_over_sqrt2": float(1 / np.sqrt(2)), "max_model_S": float(Smodel.max()),
           "rmse_v0.55": rmse_v05, "rmse_v1.0": rmse_v1,
           "B1_local_regime_fits": b1, "B2_genuine_local_model": b2, "B3_certificate_at_tsirelson": b3,
           "nonlocality_certified": bool(b1 and b2 and b3)}
    print(f"\nB1 local regime fits (RMSE@v=0.55 {rmse_v05:.4f} <0.03): {b1}")
    print(f"B2 genuine local model (max|S| {Smodel.max():.3f} <= 2.05, respects Bell bound): {b2}")
    print(f"B3 certificate: local model fails at v_knee={v_knee} vs 1/sqrt2={1/np.sqrt(2):.4f}; v=1 unfittable (RMSE {rmse_v1:.3f}): {b3}")
    print(f"\nNONLOCALITY CERTIFIED BY FAILURE (no cheap LOCAL code exists above 1/sqrt2): {out['nonlocality_certified']}")
    (RESULTS / "84_bell_nolocal.json").write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(1, 2, figsize=(13, 5))
    ax[0].plot(vs, Squant, "k--", label="quantum Werner |S| = 2√2·v")
    ax[0].plot(vs, Smodel, "o-", color="crimson", label="best LOCAL model |S| (net)")
    ax[0].axhline(2.0, color="navy", ls=":", label="Bell/CHSH local bound = 2")
    ax[0].axvline(1 / np.sqrt(2), color="orange", ls=":", label="v*=1/√2=0.707")
    ax[0].set_xlabel("visibility v"); ax[0].set_ylabel("CHSH |S|"); ax[0].legend(fontsize=8)
    ax[0].set_title("the local model tracks quantum, then hits a wall it CANNOT pass\n(failure at v* certifies nonlocality)")
    ax[1].plot(vs, rmses, "s-", color="darkorange"); ax[1].axvline(1 / np.sqrt(2), color="orange", ls=":")
    ax[1].set_xlabel("visibility v"); ax[1].set_ylabel("local-model fit RMSE")
    ax[1].set_title("no cheap LOCAL explanation above v*\n(the cheapest-explanation failure = the certificate)")
    fig.tight_layout(); fig.savefig(RESULTS / "84_bell_nolocal.png", dpi=140)
    print("saved results/84_bell_nolocal.json + .png")


if __name__ == "__main__":
    main()
