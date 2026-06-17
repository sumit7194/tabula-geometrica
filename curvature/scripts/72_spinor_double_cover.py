"""Step 72 — OVERNIGHT #6: THE SPINOR DOUBLE COVER — can a net discover that 360deg != identity?

The edge-of-representability question (parked field menu: "Dirac/spinor — can a net discover a double-cover
state space?"). Web-verified: a spin-1/2 spinor needs a 720deg (4pi) rotation to return; a 360deg rotation
maps the spinor to its NEGATIVE (the famous -1). SU(2) double-covers SO(3). Crucially, the Bloch vector
r=<psi|sigma|psi> (quadratic in psi) is INVARIANT under psi->-psi, so it has 360deg periodicity and CANNOT
reveal the double cover; a phase-sensitive amplitude a=<ref|psi> (linear in psi) FLIPS SIGN at 360deg and so
exposes it.

A generic net (NO spin structure built in: generic latent + generic recurrent update) infers the hidden
state from a few observations of a rotation walk, then predicts the observable. Two observation channels:
  PHASE: a(t)=<ref|psi(t)> -> (Re,Im)         (linear in psi; sign-sensitive)
  BLOCH: r(t)=(<sx>,<sy>,<sz>)                (quadratic; sign-blind = the control)
Discovery test: roll the trained net along a CLEAN fixed-axis sweep (dtheta=pi/8/step) and read its predicted
observable at 0deg, 360deg (16 steps), 720deg (32 steps). If the PHASE net discovered the double cover, its
prediction ANTI-correlates with the start at 360deg and re-correlates at 720deg (period 4pi). The BLOCH net
can only show 360deg periodicity.

Pre-reg (2026-06-17):
  S1 both fit their observable: held-out R^2 > 0.9.
  S2 THE DISCOVERY: PHASE net predicted-obs cosine(360deg, start) < -0.8 AND cosine(720deg, start) > 0.8
     (it learned 720deg periodicity / the sign flip = discovered the double cover).
  S3 CONTROL: BLOCH net predicted-obs cosine(360deg, start) > 0.8 (period 360deg, blind to the double cover).
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

STEPS = 10000
T = 32
KOBS = 8
L = 8                       # generic latent width (net must find its own effective dim)
DEV = torch.device("mps" if torch.backends.mps.is_available() else "cpu")

SX = np.array([[0, 1], [1, 0]], complex); SY = np.array([[0, -1j], [1j, 0]], complex); SZ = np.array([[1, 0], [0, -1]], complex)
REF = np.array([1, 0], complex)


def su2(axis, dtheta):                       # exp(-i dtheta/2 n.sigma)
    n = axis / (np.linalg.norm(axis) + 1e-12)
    return np.cos(dtheta / 2) * np.eye(2) - 1j * np.sin(dtheta / 2) * (n[0] * SX + n[1] * SY + n[2] * SZ)


def bloch(psi):
    return np.array([np.real(psi.conj() @ SX @ psi), np.real(psi.conj() @ SY @ psi), np.real(psi.conj() @ SZ @ psi)])


def episode(rng, phase, fixed_axis=None, dtheta_fixed=None):
    re = rng.standard_normal(2); im = rng.standard_normal(2); psi = (re + 1j * im); psi /= np.linalg.norm(psi)
    ctx = np.zeros((T, 3), np.float32); obs = []
    for t in range(T):
        if fixed_axis is None:
            axis = rng.standard_normal(3); dth = rng.normal(0, 0.45)
        else:
            axis = np.array(fixed_axis, float); dth = dtheta_fixed
        rotvec = (axis / (np.linalg.norm(axis) + 1e-12)) * dth
        ctx[t] = rotvec.astype(np.float32)
        a = REF.conj() @ psi
        obs.append([a.real, a.imag] if phase else list(bloch(psi)))
        psi = su2(axis, dth) @ psi
    return ctx, np.array(obs, np.float32)


def make_batch(B, phase, seed):
    rng = np.random.default_rng(seed); C, O = [], []
    for _ in range(B):
        c, o = episode(rng, phase); C.append(c); O.append(o)
    return torch.from_numpy(np.stack(C)), torch.from_numpy(np.stack(O))


class Net(nn.Module):
    def __init__(s, odim):
        super().__init__()
        s.enc = nn.GRU(3 + odim, 96, batch_first=True); s.z0 = nn.Linear(96, L)
        s.f = nn.Sequential(nn.Linear(L + 3, 128), nn.GELU(), nn.Linear(128, 128), nn.GELU(), nn.Linear(128, L))
        s.head = nn.Sequential(nn.Linear(L, 96), nn.GELU(), nn.Linear(96, 96), nn.GELU(), nn.Linear(96, odim))

    def forward(s, ctx, obs):
        tok = torch.cat([ctx[:, :KOBS], obs[:, :KOBS]], -1)
        h, _ = s.enc(tok); z = s.z0(h[:, -1]); Z = [z]
        for t in range(T - 1):
            z = z + s.f(torch.cat([z, ctx[:, t]], -1)); Z.append(z)
        Z = torch.stack(Z, 1)
        return s.head(Z)


def train(phase, tag):
    odim = 2 if phase else 3; m = Net(odim).to(DEV); opt = torch.optim.Adam(m.parameters(), lr=1e-3)
    for step in range(STEPS):
        C, O = make_batch(192, phase, seed=step + 1); C, O = C.to(DEV), O.to(DEV)
        pred = m(C, O)
        loss = nn.functional.mse_loss(pred[:, KOBS:], O[:, KOBS:])
        opt.zero_grad(); loss.backward(); opt.step()
        if step % 500 == 0: progress(tag, step, STEPS, loss=float(loss.detach()))
    return m, odim


def heldout_r2(m, phase):
    C, O = make_batch(300, phase, seed=777); C, O = C.to(DEV), O.to(DEV)
    m.eval()
    with torch.no_grad():
        pred = m(C, O)
    p = pred[:, KOBS:].cpu().numpy().reshape(-1); o = O[:, KOBS:].cpu().numpy().reshape(-1)
    return float(1 - np.sum((p - o) ** 2) / np.sum((o - o.mean()) ** 2))


def sweep_cosines(m, phase, axis=(0, 0, 1)):
    """clean fixed-axis sweep dtheta=pi/6 (30deg/step): obs at step0 (0deg), step12 (360deg), step24 (720deg)."""
    rng = np.random.default_rng(55); C, O = [], []
    for _ in range(300):
        c, o = episode(rng, phase, fixed_axis=axis, dtheta_fixed=np.pi / 6); C.append(c); O.append(o)
    C = torch.from_numpy(np.stack(C)).to(DEV); O = torch.from_numpy(np.stack(O)).to(DEV)
    m.eval()
    with torch.no_grad():
        pred = m(C, O).cpu().numpy()                 # (B,T,odim)
    v0 = pred[:, 0]; v360 = pred[:, 12]; v720 = pred[:, 24]   # 0deg, 360deg, 720deg (exact steps)

    def cos(a, b):
        return float(np.mean(np.sum(a * b, 1) / (np.linalg.norm(a, axis=1) * np.linalg.norm(b, axis=1) + 1e-9)))
    return cos(v360, v0), cos(v720, v0), pred


def main():
    mp, _ = train(True, "72_phase"); mb, _ = train(False, "72_bloch")
    r2p = heldout_r2(mp, True); r2b = heldout_r2(mb, False)
    c360_p, c720_p, predp = sweep_cosines(mp, True)
    c360_b, c720_b, predb = sweep_cosines(mb, False)

    out = {"phase": {"y_R2": r2p, "cos_360_vs_start": c360_p, "cos_720_vs_start": c720_p},
           "bloch": {"y_R2": r2b, "cos_360_vs_start": c360_b, "cos_720_vs_start": c720_b}}
    s1 = bool(r2p > 0.9 and r2b > 0.9)
    s2 = bool(c360_p < -0.8 and c720_p > 0.8)
    s3 = bool(c360_b > 0.8)
    res = {**out, "S1_both_fit": s1, "S2_phase_discovers_double_cover": s2, "S3_bloch_blind_control": s3,
           "double_cover_discovered": bool(s1 and s2 and s3)}
    print(f"phase : y R^2 {r2p:.3f} | cos(360deg,start) {c360_p:+.3f} (want <-0.8) | cos(720deg,start) {c720_p:+.3f} (want >0.8)")
    print(f"bloch : y R^2 {r2b:.3f} | cos(360deg,start) {c360_b:+.3f} (want >0.8 = period 360, blind)")
    print(f"\nS1 both fit (R^2>0.9): {s1}")
    print(f"S2 PHASE net discovers double cover (anti at 360deg, back at 720deg): {s2}")
    print(f"S3 BLOCH control blind (period 360deg): {s3}")
    print(f"\nSPINOR DOUBLE COVER DISCOVERED (a net found 360deg != identity, 720deg = identity): {res['double_cover_discovered']}")
    (RESULTS / "72_spinor_double_cover.json").write_text(json.dumps(res, indent=1))

    # viz: predicted obs component 0 vs rotation angle, phase vs bloch
    ang = np.arange(T) * (np.pi / 6) * 180 / np.pi
    fig, ax = plt.subplots(1, 2, figsize=(13, 5))
    ax[0].plot(ang, predp[:50, :, 0].T, color="crimson", alpha=0.25)
    ax[0].axvline(360, color="k", ls="--", lw=0.8); ax[0].axvline(720, color="k", ls=":", lw=0.8)
    ax[0].set_title(f"PHASE net: predicted Re<ref|psi> vs rotation\n720deg-periodic (sign flips at 360deg) — double cover\ncos(360,start)={c360_p:+.2f}")
    ax[0].set_xlabel("total rotation (deg)"); ax[0].set_ylabel("predicted observable [0]")
    ax[1].plot(ang, predb[:50, :, 0].T, color="navy", alpha=0.25)
    ax[1].axvline(360, color="k", ls="--", lw=0.8)
    ax[1].set_title(f"BLOCH net (control): 360deg-periodic\nblind to the double cover — cos(360,start)={c360_b:+.2f}")
    ax[1].set_xlabel("total rotation (deg)"); ax[1].set_ylabel("predicted observable [0]")
    fig.tight_layout(); fig.savefig(RESULTS / "72_spinor_double_cover.png", dpi=140)
    print("saved results/72_spinor_double_cover.json + .png")


if __name__ == "__main__":
    main()
