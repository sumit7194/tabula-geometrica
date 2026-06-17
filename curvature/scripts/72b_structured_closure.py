"""Step 72b — THE SPINOR CAPSTONE: structure-preservation closes the 4pi loop (72's prediction + Leg-3 tie).

72 found a generic net DETECTS the double cover (anti-correlates at 360deg) but does NOT achieve clean 4pi
closure (720deg cos -0.14) -- because a generic recurrent update doesn't preserve the SU(2) group structure
over a full double-loop. Tonight's Leg-3 result (71/71c) says the same thing in the legibility setting:
structure preserves invariants, generic drifts. PREDICTION: give the latent a NORM-PRESERVING SO(L) update
(matrix-exp of a learned skew matrix -- the structure-preserving analog, NOT the hardcoded SU(2) answer) and
it should close the loop cleanly: 360deg -> sign flip, 720deg -> return to identity. Head-to-head vs a generic
update in the SAME harness/data.

Pre-reg (2026-06-17):
  P1 both fit: held-out phase R^2 > 0.9.
  P2 STRUCTURE closes the double cover: structured cos(360deg,start) < -0.8 AND cos(720deg,start) > 0.8.
  P3 GENERIC fails to close (the contrast IS the result): generic cos(720deg,start) < 0.5.
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

STEPS = 6000
T = 32
KOBS = 8
L = 4                       # spinor C^2 ~ R^4: SU(2) sits inside SO(4)
DEV = torch.device("cpu")   # 4x4 matrix_exp is reliable + cheap on CPU

SX = np.array([[0, 1], [1, 0]], complex); SY = np.array([[0, -1j], [1j, 0]], complex); SZ = np.array([[1, 0], [0, -1]], complex)
REF = np.array([1, 0], complex)

# antisymmetric basis for so(4): 6 generators G_k (one per i<j pair)
_PAIRS = [(i, j) for i in range(4) for j in range(i + 1, 4)]
_G = np.zeros((6, 4, 4), np.float32)
for k, (i, j) in enumerate(_PAIRS):
    _G[k, i, j] = 1.0; _G[k, j, i] = -1.0
G = torch.from_numpy(_G)


def su2(axis, dtheta):
    n = axis / (np.linalg.norm(axis) + 1e-12)
    return np.cos(dtheta / 2) * np.eye(2) - 1j * np.sin(dtheta / 2) * (n[0] * SX + n[1] * SY + n[2] * SZ)


def episode(rng, fixed_axis=None, dtheta_fixed=None):
    re = rng.standard_normal(2); im = rng.standard_normal(2); psi = (re + 1j * im); psi /= np.linalg.norm(psi)
    ctx = np.zeros((T, 3), np.float32); obs = []
    for t in range(T):
        if fixed_axis is None:
            axis = rng.standard_normal(3); dth = rng.normal(0, 0.45)
        else:
            axis = np.array(fixed_axis, float); dth = dtheta_fixed
        ctx[t] = (axis / (np.linalg.norm(axis) + 1e-12) * dth).astype(np.float32)
        a = REF.conj() @ psi; obs.append([a.real, a.imag])
        psi = su2(axis, dth) @ psi
    return ctx, np.array(obs, np.float32)


def make_batch(B, seed):
    rng = np.random.default_rng(seed); C, O = [], []
    for _ in range(B):
        c, o = episode(rng); C.append(c); O.append(o)
    return torch.from_numpy(np.stack(C)), torch.from_numpy(np.stack(O))


class Net(nn.Module):
    def __init__(s, structured):
        super().__init__(); s.structured = structured
        s.enc = nn.GRU(3 + 2, 96, batch_first=True); s.z0 = nn.Linear(96, L)
        nin = 3 if structured else L + 3
        nout = 6 if structured else L
        s.f = nn.Sequential(nn.Linear(nin, 128), nn.GELU(), nn.Linear(128, 128), nn.GELU(), nn.Linear(128, nout))
        s.head = nn.Sequential(nn.Linear(L, 96), nn.GELU(), nn.Linear(96, 96), nn.GELU(), nn.Linear(96, 2))

    def step(s, z, ctx):
        if s.structured:
            A = torch.einsum('bk,kij->bij', s.f(ctx), G.to(z.device))      # so(4) element
            R = torch.matrix_exp(A)                                        # SO(4) rotation (norm-preserving)
            return (R @ z.unsqueeze(-1)).squeeze(-1)
        return z + s.f(torch.cat([z, ctx], -1))

    def forward(s, ctx, obs):
        tok = torch.cat([ctx[:, :KOBS], obs[:, :KOBS]], -1)
        h, _ = s.enc(tok); z = s.z0(h[:, -1]); Z = [z]
        for t in range(T - 1):
            z = s.step(z, ctx[:, t]); Z.append(z)
        return s.head(torch.stack(Z, 1))


def train(structured, tag):
    m = Net(structured).to(DEV); opt = torch.optim.Adam(m.parameters(), lr=1e-3)
    for step in range(STEPS):
        C, O = make_batch(192, seed=step + 1)
        pred = m(C.to(DEV), O.to(DEV))
        loss = nn.functional.mse_loss(pred[:, KOBS:], O.to(DEV)[:, KOBS:])
        opt.zero_grad(); loss.backward(); opt.step()
        if step % 400 == 0: progress(tag, step, STEPS, loss=float(loss.detach()))
    return m


def heldout_r2(m):
    C, O = make_batch(300, seed=777); m.eval()
    with torch.no_grad():
        pred = m(C.to(DEV), O.to(DEV))
    p = pred[:, KOBS:].cpu().numpy().reshape(-1); o = O[:, KOBS:].numpy().reshape(-1)
    return float(1 - np.sum((p - o) ** 2) / np.sum((o - o.mean()) ** 2))


def sweep(m, axis=(0, 0, 1)):
    rng = np.random.default_rng(55); C, O = [], []
    for _ in range(300):
        c, o = episode(rng, fixed_axis=axis, dtheta_fixed=np.pi / 6); C.append(c); O.append(o)
    m.eval()
    with torch.no_grad():
        pred = m(torch.from_numpy(np.stack(C)).to(DEV), torch.from_numpy(np.stack(O)).to(DEV)).cpu().numpy()
    v0, v360, v720 = pred[:, 0], pred[:, 12], pred[:, 24]

    def cos(a, b):
        return float(np.mean(np.sum(a * b, 1) / (np.linalg.norm(a, axis=1) * np.linalg.norm(b, axis=1) + 1e-9)))
    return cos(v360, v0), cos(v720, v0), pred


def main():
    ms = train(True, "72b_struct"); mg = train(False, "72b_generic")
    r2s, r2g = heldout_r2(ms), heldout_r2(mg)
    c360s, c720s, preds = sweep(ms); c360g, c720g, predg = sweep(mg)
    out = {"structured": {"y_R2": r2s, "cos_360": c360s, "cos_720": c720s},
           "generic": {"y_R2": r2g, "cos_360": c360g, "cos_720": c720g}}
    p1 = bool(r2s > 0.9 and r2g > 0.9)
    p2 = bool(c360s < -0.8 and c720s > 0.8)
    p3 = bool(c720g < 0.5)
    res = {**out, "P1_both_fit": p1, "P2_structure_closes_4pi": p2, "P3_generic_fails_to_close": p3,
           "structure_closes_double_cover": bool(p1 and p2 and p3)}
    print(f"structured : y R^2 {r2s:.3f} | cos(360) {c360s:+.3f} (want<-0.8) | cos(720) {c720s:+.3f} (want>0.8)")
    print(f"generic    : y R^2 {r2g:.3f} | cos(360) {c360g:+.3f} | cos(720) {c720g:+.3f} (want<0.5 = drifts)")
    print(f"\nP1 both fit: {p1}")
    print(f"P2 STRUCTURE closes the 4pi loop (sign flip at 360, return at 720): {p2}")
    print(f"P3 GENERIC fails to close (drifts): {p3}")
    print(f"\nSTRUCTURE CLOSES THE DOUBLE COVER (720deg=identity) where generic only caught the flip: {res['structure_closes_double_cover']}")
    (RESULTS / "72b_structured_closure.json").write_text(json.dumps(res, indent=1))

    ang = np.arange(T) * 30.0
    fig, ax = plt.subplots(1, 2, figsize=(13, 5))
    for a, pred, t, c in [(ax[0], preds, f"STRUCTURED (SO(4)): closes 4pi\ncos(720,start)={c720s:+.2f}", "seagreen"),
                          (ax[1], predg, f"GENERIC: catches flip, drifts\ncos(720,start)={c720g:+.2f}", "crimson")]:
        a.plot(ang, pred[:60, :, 0].T, color=c, alpha=0.25)
        a.axvline(360, color="k", ls="--", lw=0.8); a.axvline(720, color="k", ls=":", lw=0.8)
        a.set_xlabel("total rotation (deg)"); a.set_ylabel("predicted Re<ref|psi>"); a.set_title(t)
    fig.tight_layout(); fig.savefig(RESULTS / "72b_structured_closure.png", dpi=140)
    print("saved results/72b_structured_closure.json + .png")


if __name__ == "__main__":
    main()
