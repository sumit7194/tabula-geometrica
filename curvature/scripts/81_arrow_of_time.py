"""Step 81 — PULL BACK: can a net discover the ARROW OF TIME (the second law) from REVERSIBLE dynamics?

Orthogonal to black holes, but tied to the project's time-reversal thread (friction 70, collapse 75). An ideal
gas freely expands in a box: the microscopic dynamics is exactly time-REVERSIBLE (reverse every velocity and
it re-clusters), yet the COARSE-GRAINED entropy rises (Boltzmann/Loschmidt). Give a net two coarse frames in
some order and ask "is this forward or backward in time?". To win it must DISCOVER the second law: the
higher-entropy frame comes later. The start region is randomized each episode, so no fixed spatial cue works
-- only entropy increase is consistent. And it must FAIL at equilibrium (entropy saturated -> no arrow).

Pre-reg (2026-06-17):
  A1 the net reads time's arrow: forward/backward accuracy on NON-equilibrium clips > 0.85.
  A2 it discovered ENTROPY: its decision tracks the sign of the coarse-grained entropy change -- a logistic
     on dS_coarse alone reaches within 0.05 of the net's accuracy, and corr(net logit, dS) > 0.8.
  A3 the arrow IS entropy (the boundary): on EQUILIBRIUM clips (entropy saturated) accuracy -> chance
     (0.45-0.55) -- no arrow when entropy is maximal. Reversibility restored.
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

G = 10            # coarse grid GxG
N = 200           # particles
DT = 0.02
np.seterr(all="ignore")


def simulate(rng, nsteps=64):
    """N free particles in [0,1]^2, reflecting walls; start clustered in a random sub-box. Reversible."""
    c = rng.uniform(0.0, 0.65, 2)                         # random start corner -> no fixed spatial cue
    x = c + rng.uniform(0, 0.35, (N, 2))
    ang = rng.uniform(0, 2 * np.pi, N); spd = rng.uniform(0.4, 1.4, N)   # spread of speeds -> equilibration
    v = spd[:, None] * np.stack([np.cos(ang), np.sin(ang)], 1)           # crosses the box in ~tens of steps
    grids = []
    for _ in range(nsteps):
        x = x + v * DT
        lo = x < 0; hi = x > 1
        x[lo] = -x[lo]; v[lo] = -v[lo]; x[hi] = 2 - x[hi]; v[hi] = -v[hi]
        h, _, _ = np.histogram2d(x[:, 0], x[:, 1], bins=G, range=[[0, 1], [0, 1]])
        grids.append((h / N).astype(np.float32))
    return np.array(grids)                                # (nsteps, G, G)


def entropy(g):
    p = g.ravel(); p = p[p > 0]; return float(-np.sum(p * np.log(p)))


def make_clips(n_ep, seed, eq):
    """clips = (frame_a, frame_b, label) where label=1 if in forward (causal) order. eq=True -> equilibrium."""
    rng = np.random.default_rng(seed); A, B, Y, dS = [], [], [], []
    for _ in range(n_ep):
        gr = simulate(rng)
        i = rng.integers(40, 57) if eq else rng.integers(0, 18)   # late (saturated) vs early (rising)
        a, b = gr[i], gr[i + 6]
        fwd = bool(rng.random() < 0.5)
        if fwd:
            A.append(a); B.append(b); Y.append(1)
        else:
            A.append(b); B.append(a); Y.append(0)
        dS.append(entropy(B[-1]) - entropy(A[-1]))       # entropy(second shown) - entropy(first shown)
    X = np.concatenate([np.array(A).reshape(n_ep, -1), np.array(B).reshape(n_ep, -1)], 1)
    return X.astype(np.float32), np.array(Y, np.float32), np.array(dS, np.float32)


class Clf(nn.Module):
    def __init__(s):
        super().__init__(); s.net = nn.Sequential(nn.Linear(2 * G * G, 384), nn.GELU(), nn.Linear(384, 384), nn.GELU(),
                                                  nn.Linear(384, 64), nn.GELU(), nn.Linear(64, 1))
    def forward(s, x): return s.net(x)[:, 0]


def main():
    Xtr, Ytr, _ = make_clips(8000, 0, eq=False)
    Xte, Yte, dSte = make_clips(3000, 1, eq=False)
    Xeq, Yeq, _ = make_clips(3000, 2, eq=True)
    Xt = torch.from_numpy(Xtr); Yt = torch.from_numpy(Ytr)
    m = Clf(); opt = torch.optim.Adam(m.parameters(), lr=1e-3); rng = np.random.default_rng(1)
    for step in range(11000):
        b = rng.integers(0, len(Xt), 256)
        loss = nn.functional.binary_cross_entropy_with_logits(m(Xt[b]), Yt[b])
        opt.zero_grad(); loss.backward(); opt.step()
        if step % 400 == 0: progress("81_arrow", step, 11000, loss=float(loss.detach()))
    m.eval()

    def acc(X, Y):
        with torch.no_grad():
            p = (m(torch.from_numpy(X)) > 0).numpy().astype(float)
        return float((p == Y).mean())
    def logits(X):
        with torch.no_grad():
            return m(torch.from_numpy(X)).numpy()
    a_noneq = acc(Xte, Yte); a_eq = acc(Xeq, Yeq)

    # A2: entropy-only baseline (logistic on dS) + correlation of net logit with dS
    from numpy import sign
    ent_acc = float(((dSte > 0).astype(float) == Yte).mean())   # "higher-entropy frame is later" rule
    lg = logits(Xte); corr = float(np.corrcoef(lg, dSte)[0, 1])

    a1 = bool(a_noneq > 0.85)
    a2 = bool(abs(ent_acc - a_noneq) < 0.05 and corr > 0.8)
    a3 = bool(0.45 <= a_eq <= 0.55)
    out = {"acc_nonequilibrium": a_noneq, "acc_equilibrium": a_eq, "entropy_rule_acc": ent_acc,
           "corr_logit_dS": corr, "A1_reads_arrow": a1, "A2_discovered_entropy": a2,
           "A3_no_arrow_at_equilibrium": a3, "arrow_of_time_discovered": bool(a1 and a2 and a3)}
    print(f"A1 reads time's arrow (non-eq acc {a_noneq:.3f} >0.85): {a1}")
    print(f"A2 discovered entropy (dS-rule acc {ent_acc:.3f} ~ net {a_noneq:.3f}; corr(logit,dS) {corr:.3f}): {a2}")
    print(f"A3 no arrow at equilibrium (eq acc {a_eq:.3f} ~ 0.5): {a3}")
    print(f"\nARROW OF TIME DISCOVERED (the second law from reversible dynamics; vanishes at equilibrium): {out['arrow_of_time_discovered']}")
    (RESULTS / "81_arrow_of_time.json").write_text(json.dumps(out, indent=1))

    # viz: an expansion's entropy curve + the net's arrow accuracy vs time-in-evolution
    rng2 = np.random.default_rng(9); gr = simulate(rng2); Scurve = [entropy(g) for g in gr]
    fig, ax = plt.subplots(1, 2, figsize=(13, 5))
    ax[0].plot(Scurve, color="crimson"); ax[0].set_xlabel("time step"); ax[0].set_ylabel("coarse-grained entropy")
    ax[0].set_title("reversible gas: coarse entropy rises then saturates\n(the arrow exists only while it rises)")
    ax[1].bar([0, 1], [a_noneq, a_eq], color=["seagreen", "gray"])
    ax[1].axhline(0.5, color="k", ls=":"); ax[1].set_xticks([0, 1]); ax[1].set_xticklabels(["non-equilibrium\n(entropy rising)", "equilibrium\n(saturated)"])
    ax[1].set_ylabel("arrow-of-time accuracy"); ax[1].set_title(f"net reads the arrow only out of equilibrium\nnon-eq {a_noneq:.2f} vs eq {a_eq:.2f} (chance)")
    fig.tight_layout(); fig.savefig(RESULTS / "81_arrow_of_time.png", dpi=140)
    print("saved results/81_arrow_of_time.json + .png")


if __name__ == "__main__":
    main()
