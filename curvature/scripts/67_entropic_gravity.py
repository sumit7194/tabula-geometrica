"""Step 67 — OVERNIGHT #1: ENTROPIC / EMERGENT gravity — can a net discover a force that is BOOKKEEPING?

Web-verified: an entropic force F = T*dS/dx scales with TEMPERATURE (rubber elasticity: modulus = kBT per
strand, force grows with T) and VANISHES at T->0; Verlinde derives Newtonian gravity as exactly such an
entropic force from a holographic screen (gravity as emergent bookkeeping, not a fundamental field). The
sharp falsifiable signature vs a fundamental ENERGETIC force (F = -dU/dx, T-independent): entropic force
is LINEAR in T and goes to ZERO at T=0.

Setup: a probe feels an attractive force toward a center. Two worlds, same spatial form g(x):
  ENTROPIC:  a(x,T) = T * g(x)   (force ∝ T; vanishes at T->0 = "no temperature, no gravity")
  ENERGETIC: a(x,T) = g(x)       (T-independent, a fundamental field)
A net learns a(x,T) from (position, temperature). Does it discover the entropic signature?

Pre-reg (2026-06-17):
  E1 learns both: test R^2 > 0.95 for both worlds.
  E2 ENTROPIC SIGNATURE: entropic net's force is LINEAR in T — a(2T)/a(T) ~ 2 and a(T->0) ~ 0 — while the
     energetic net's force is T-INDEPENDENT — a(2T)/a(T) ~ 1 and a(T->0) ~ a(T=1).
  E3 LEARNED THE LAW (extrapolation): entropic net extrapolates to out-of-range T (a(T=4)/a(T=2) ~ 2),
     i.e. it learned F ∝ T, not a memorized lookup.
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

STEPS = 7000


def gfield(x, y):
    r = np.sqrt(x ** 2 + y ** 2) + 0.3
    return -x / r, -y / r                                # attractive toward origin (softened)


def make_data(entropic, n=120000, seed=0, Tlo=0.5, Thi=2.0):
    rng = np.random.default_rng(seed)
    x = rng.uniform(-3, 3, n).astype(np.float32); y = rng.uniform(-3, 3, n).astype(np.float32)
    T = rng.uniform(Tlo, Thi, n).astype(np.float32)
    gx, gy = gfield(x, y)
    s = T if entropic else 1.0
    ax = (s * gx).astype(np.float32); ay = (s * gy).astype(np.float32)
    X = np.stack([x, y, T], 1); Y = np.stack([ax, ay], 1)
    return X, Y


class ForceNet(nn.Module):
    def __init__(s):
        super().__init__(); s.net = nn.Sequential(nn.Linear(3, 128), nn.GELU(), nn.Linear(128, 128), nn.GELU(),
                                                  nn.Linear(128, 128), nn.GELU(), nn.Linear(128, 2))
    def forward(s, x):
        return s.net(x)


def train(entropic):
    X, Y = make_data(entropic); Xt = torch.from_numpy(X); Yt = torch.from_numpy(Y)
    ntr = int(len(X) * 0.9); m = ForceNet(); opt = torch.optim.Adam(m.parameters(), lr=1e-3); rng = np.random.default_rng(0)
    for step in range(STEPS):
        idx = rng.integers(0, ntr, 512)
        loss = nn.functional.mse_loss(m(Xt[idx]), Yt[idx])
        opt.zero_grad(); loss.backward(); opt.step()
        if step % 500 == 0: progress(f"67_{'ent' if entropic else 'enr'}", step, STEPS, loss=float(loss.detach()))
    m.eval()
    with torch.no_grad():
        r2 = float(1 - ((m(Xt[ntr:]) - Yt[ntr:]) ** 2).mean() / Yt[ntr:].var())
    return m, r2


def force_mag_at_T(m, T, seed=3, n=400):
    rng = np.random.default_rng(seed)
    x = rng.uniform(-3, 3, n).astype(np.float32); y = rng.uniform(-3, 3, n).astype(np.float32)
    X = np.stack([x, y, np.full(n, T, np.float32)], 1)
    with torch.no_grad():
        a = m(torch.from_numpy(X)).numpy()
    return np.linalg.norm(a, axis=1)


def main():
    out = {}
    for entropic in (True, False):
        tag = "entropic" if entropic else "energetic"
        m, r2 = train(entropic)
        f1 = force_mag_at_T(m, 1.0).mean(); f2 = force_mag_at_T(m, 2.0).mean()
        f0 = force_mag_at_T(m, 0.1).mean(); f4 = force_mag_at_T(m, 4.0).mean()  # 4.0 is out-of-range (trained 0.5-2)
        out[tag] = {"R2": r2, "ratio_2T_T": float(f2 / (f1 + 1e-9)), "force_at_T0.1_over_T1": float(f0 / (f1 + 1e-9)),
                    "extrap_ratio_4T_2T": float(f4 / (f2 + 1e-9))}
        print(f"{tag:9s}: R^2 {r2:.3f} | a(2T)/a(T) {f2/(f1+1e-9):.2f} | a(0.1)/a(1) {f0/(f1+1e-9):.2f} | extrap a(4)/a(2) {f4/(f2+1e-9):.2f}")

    e, n = out["entropic"], out["energetic"]
    e1 = bool(e["R2"] > 0.95 and n["R2"] > 0.95)
    e2 = bool(1.7 < e["ratio_2T_T"] < 2.3 and e["force_at_T0.1_over_T1"] < 0.25
              and 0.85 < n["ratio_2T_T"] < 1.15 and n["force_at_T0.1_over_T1"] > 0.7)
    e3 = bool(1.7 < e["extrap_ratio_4T_2T"] < 2.3)
    res = {"results": out, "E1_learns_both": e1, "E2_entropic_signature": e2, "E3_learned_the_law": e3,
           "entropic_gravity_discovered": bool(e1 and e2 and e3)}
    print(f"\nE1 learns both (R^2>0.95): {e1}")
    print(f"E2 entropic signature (F∝T & vanishes at T->0; energetic T-independent): {e2}")
    print(f"E3 learned the law (extrapolates a∝T to T=4): {e3}")
    print(f"\nENTROPIC GRAVITY DISCOVERED (force = T-scaled bookkeeping, vanishes at T=0): {res['entropic_gravity_discovered']}")
    (RESULTS / "67_entropic_gravity.json").write_text(json.dumps(res, indent=1))

    Ts = np.linspace(0.0, 4.0, 30)
    me, _ = train(True); mn, _ = train(False)
    fe = [force_mag_at_T(me, t).mean() for t in Ts]; fn = [force_mag_at_T(mn, t).mean() for t in Ts]
    fig, ax = plt.subplots(figsize=(7.5, 5))
    ax.plot(Ts, fe, "o-", color="crimson", label="entropic gravity: F ∝ T (vanishes at T=0)")
    ax.plot(Ts, fn, "s-", color="navy", label="energetic force: T-independent")
    ax.axvspan(0.5, 2.0, alpha=0.1, color="gray", label="training T range"); ax.axvline(0, color="k", lw=0.6)
    ax.set_xlabel("temperature T"); ax.set_ylabel("learned force magnitude")
    ax.set_title("gravity as bookkeeping: the entropic force scales with T and dies at T=0\n(net learns the law, extrapolates past the training range)")
    ax.legend(fontsize=8); fig.tight_layout(); fig.savefig(RESULTS / "67_entropic_gravity.png", dpi=140)
    print("saved results/67_entropic_gravity.json + .png")


if __name__ == "__main__":
    main()
