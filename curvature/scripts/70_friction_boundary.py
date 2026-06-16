"""Step 70 — OVERNIGHT #4: THE FRICTION BOUNDARY — universality is necessary but NOT sufficient.

The field zoo (68) showed COUPLING universality decides geometrize-vs-force. Friction is the sharp
counterexample that finds the SECOND condition. Kinetic friction is UNIVERSAL — its deceleration is
mass-independent (a = mu*g, same for every body, just like the equivalence principle) — yet it does NOT
geometrize. Why? Web-verified: dissipative forces are NON-CONSERVATIVE (Bauer 1931: no variational
principle yields a first-order dissipation term; not even a velocity-dependent potential), and
non-conservative forces BREAK TIME-REVERSAL symmetry, whereas geodesic/Lagrangian (geometry) dynamics are
time-reversible. So geometrization needs universality AND conservativeness; friction has the first, not the
second.

Both worlds are UNIVERSAL (mass-independent, identical for all bodies) — universality is held FIXED so the
test isolates conservativeness:
  CONSERVATIVE:  a = -x            (a central restoring field; time-reversible, geometry-compatible)
  FRICTION:      a = -x - gamma*v  (adds dissipative drag; irreversible, no Lagrangian)

Economy race on the CONSERVATIVE-vs-DISSIPATIVE axis:
  GeometryModel: a = f(x)          (position-only = reversible/geodesic-compatible)
  DissipModel:   a = f(x) + h(v)   (a velocity channel = can represent drag)
  R = MSE_geom / MSE_dissip :  R~1 geometrizes (velocity channel useless) ; R>>1 cannot.

Pre-reg (2026-06-17):
  T1 both worlds learnable by the dissip model (sanity R^2>0.95).
  T2 GEOMETRIZATION SPLIT: conservative R<2 (geometrizes) ; friction R>5 (cannot) — same universality,
     opposite verdict.
  T3 THE WHY (time-reversal): roll a trajectory forward, flip v, roll back; the conservative world RETRACES
     (small return error) but friction does NOT (large) — geometry fails exactly because friction breaks
     reversibility. Conclusion: geometrize <=> universal AND conservative.
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

STEPS = 4000
GAMMA = 0.5
DEV = torch.device("mps" if torch.backends.mps.is_available() else "cpu")


def accel(x, v, friction):
    a = -x
    if friction:
        a = a - GAMMA * v
    return a


def make_data(friction, n=80000, seed=0):
    rng = np.random.default_rng(seed)
    x = rng.uniform(-3, 3, (n, 2)).astype(np.float32)
    v = rng.uniform(-3, 3, (n, 2)).astype(np.float32)
    a = accel(x, v, friction).astype(np.float32)
    return x, v, a


class GeometryModel(nn.Module):                    # position-only = reversible / geodesic-compatible
    def __init__(s):
        super().__init__(); s.fx = nn.Sequential(nn.Linear(2, 128), nn.GELU(), nn.Linear(128, 128), nn.GELU(),
                                                 nn.Linear(128, 2))
    def forward(s, x, v): return s.fx(x)


class DissipModel(nn.Module):                      # adds a velocity channel = can represent drag
    def __init__(s):
        super().__init__()
        s.fx = nn.Sequential(nn.Linear(2, 128), nn.GELU(), nn.Linear(128, 128), nn.GELU(), nn.Linear(128, 2))
        s.hv = nn.Sequential(nn.Linear(2, 128), nn.GELU(), nn.Linear(128, 128), nn.GELU(), nn.Linear(128, 2))
    def forward(s, x, v): return s.fx(x) + s.hv(v)


def train_eval(model, x, v, a, tag):
    xt = torch.from_numpy(x).to(DEV); vt = torch.from_numpy(v).to(DEV); at = torch.from_numpy(a).to(DEV)
    n = len(x); ntr = int(n * 0.9); m = model.to(DEV); opt = torch.optim.Adam(m.parameters(), lr=1e-3)
    rng = np.random.default_rng(0)
    for step in range(STEPS):
        idx = rng.integers(0, ntr, 512)
        loss = nn.functional.mse_loss(m(xt[idx], vt[idx]), at[idx])
        opt.zero_grad(); loss.backward(); opt.step()
        if step % 500 == 0: progress(tag, step, STEPS, loss=float(loss.detach()))
    m.eval()
    with torch.no_grad():
        mse = float(((m(xt[ntr:], vt[ntr:]) - at[ntr:]) ** 2).mean())
        r2 = float(1 - mse / at[ntr:].var())
    return mse, r2


def reversibility(friction, nstep=60, dt=0.05, ntraj=200, seed=1):
    """roll forward, flip v, roll back; return error normalized by trajectory spread (the TRUE dynamics)."""
    rng = np.random.default_rng(seed)
    x = rng.uniform(-2, 2, (ntraj, 2)); v = rng.uniform(-2, 2, (ntraj, 2)); x0 = x.copy()
    traj = [x.copy()]
    for _ in range(nstep):                              # semi-implicit Euler forward
        v = v + dt * accel(x, v, friction); x = x + dt * v; traj.append(x.copy())
    v = -v                                              # time reversal: flip velocity
    for _ in range(nstep):
        v = v + dt * accel(x, v, friction); x = x + dt * v
    spread = np.std(np.array(traj), axis=(0, 1)).mean()
    return float(np.mean(np.linalg.norm(x - x0, axis=1)) / (spread + 1e-9))


def main():
    out = {}
    for friction in (False, True):
        tag = "friction" if friction else "conservative"
        x, v, a = make_data(friction)
        torch.manual_seed(0); mg, r2g = train_eval(GeometryModel(), x, v, a, f"70_geo_{tag}")
        torch.manual_seed(0); md, r2d = train_eval(DissipModel(), x, v, a, f"70_dis_{tag}")
        R = mg / (md + 1e-12); rev = reversibility(friction)
        out[tag] = {"MSE_geometry": mg, "MSE_dissip": md, "R2_dissip": r2d, "ratio": R, "return_error": rev}
        print(f"{tag:12s}: geom MSE {mg:.2e} | dissip MSE {md:.2e} | R={R:7.2f} "
              f"-> {'GEOMETRY' if R<2 else 'NOT-geometry' if R>5 else 'mixed'} | reverse-return-err {rev:.3f}")

    c, f = out["conservative"], out["friction"]
    t1 = bool(c["R2_dissip"] > 0.95 and f["R2_dissip"] > 0.95)
    t2 = bool(c["ratio"] < 2.0 and f["ratio"] > 5.0)
    t3 = bool(c["return_error"] < 0.2 and f["return_error"] > 0.5)
    res = {**out, "T1_both_learnable": t1, "T2_geometrization_split": t2, "T3_reversibility_explains": t3,
           "friction_boundary_confirmed": bool(t1 and t2 and t3)}
    print(f"\nT1 both learnable (dissip R^2>0.95): {t1}")
    print(f"T2 geometrization split (conservative R<2, friction R>5, SAME universality): {t2}")
    print(f"T3 the why — reversibility (conservative retraces <0.2, friction does not >0.5): {t3}")
    print(f"\nFRICTION BOUNDARY (universality is necessary but NOT sufficient; geometry also needs "
          f"conservativeness): {res['friction_boundary_confirmed']}")
    (RESULTS / "70_friction_boundary.json").write_text(json.dumps(res, indent=1))

    fig, ax = plt.subplots(1, 2, figsize=(13, 5))
    ax[0].bar([0, 1], [c["ratio"], f["ratio"]], color=["seagreen", "crimson"])
    ax[0].set_yscale("log"); ax[0].axhline(2, color="k", ls="--", lw=0.8, label="geometrize threshold")
    ax[0].set_xticks([0, 1]); ax[0].set_xticklabels(["conservative\n(a=-x)", "friction\n(a=-x-γv)"])
    ax[0].set_ylabel("R = MSE_geom / MSE_dissip"); ax[0].legend(fontsize=8)
    ax[0].set_title("same UNIVERSALITY, opposite verdict:\nfriction is universal yet does not geometrize")
    ax[1].bar([0, 1], [c["return_error"], f["return_error"]], color=["seagreen", "crimson"])
    ax[1].set_xticks([0, 1]); ax[1].set_xticklabels(["conservative", "friction"])
    ax[1].set_ylabel("reverse-and-return error (irreversibility)")
    ax[1].set_title("the WHY: friction breaks time-reversal\n(geometry needs conservativeness)")
    fig.tight_layout(); fig.savefig(RESULTS / "70_friction_boundary.png", dpi=140)
    print("saved results/70_friction_boundary.json + .png")


if __name__ == "__main__":
    main()
