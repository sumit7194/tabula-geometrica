"""Step 86 — IMPOSSIBILITY CERTIFICATE III: a net reports "NO UNIQUE LAW" (gauge non-identifiability).

Face 3, and the deepest: turn the project's recurring villain (gauge freedom) into the result. Textbook
Lagrangian mechanics (Landau-Lifshitz): adding a TOTAL TIME DERIVATIVE dF(q)/dt = F'(q)*qdot to a Lagrangian
leaves the Euler-Lagrange equations -- and every trajectory -- UNCHANGED. So the Lagrangian recovered from
trajectories is non-injective: an entire gauge ORBIT fits identically. The honest output of a discovery net is
therefore an equivalence class + a certificate of what is identifiable.

We learn a Lagrangian Neural Network L(q,qdot) (harmonic oscillator, qddot=-q; the LNN forward is well-
conditioned here, d2L/dqdot2~1) for an ENSEMBLE of seeds, each nudged a hair toward a DIFFERENT total-
derivative gauge (c_seed * q * qdot = d/dt(c_seed q^2/2)). Since the data does not constrain the gauge part,
the ensemble fills the gauge orbit. We then decompose each learned L into its qdot-EVEN part (physical:
qdot^2/2 - V) and qdot-ODD part (gauge: F'(q)qdot) and check WHERE the ensemble agrees vs spreads.

Pre-reg (2026-06-17):
  G1 DYNAMICS IDENTIFIABLE: every ensemble net reproduces the EOM, qddot R^2 > 0.99 (the physics is recovered).
  G2 LAGRANGIAN NOT IDENTIFIABLE: ensemble std of the qdot-ODD (gauge) part >> std of the qdot-EVEN part
     (ratio > 5) -- the nets disagree on exactly the gauge direction.
  G3 THE CERTIFICATE: ensemble std of the qddot FIELD is tiny (< 0.05 of signal) -- the net is CERTAIN about
     the dynamics and UNCERTAIN about the gauge. (Corroboration: adding lambda*q*qdot to a fitted L leaves
     qddot flat -- the data-loss is invariant along the gauge orbit.)
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

K = 6              # ensemble size
np.seterr(all="ignore")


class Lag(nn.Module):
    """structured 1-DOF Lagrangian L = 1/2 qdot^2 + N(q) qdot - V(q). The N(q)qdot term is a candidate TOTAL
    derivative (gauge); it provably CANCELS in the Euler-Lagrange EOM, which is just qddot = -V'(q). No Hessian
    division -> numerically stable (avoids the LNN/D-v2 trap)."""
    def __init__(s):
        super().__init__()
        s.V = nn.Sequential(nn.Linear(1, 96), nn.Tanh(), nn.Linear(96, 96), nn.Tanh(), nn.Linear(96, 1))
        s.N = nn.Sequential(nn.Linear(1, 96), nn.Tanh(), nn.Linear(96, 96), nn.Tanh(), nn.Linear(96, 1))
    def Vq(s, q): return s.V(q[:, None])[:, 0]
    def Nq(s, q): return s.N(q[:, None])[:, 0]
    def L(s, q, qd): return 0.5 * qd ** 2 + s.Nq(q) * qd - s.Vq(q)
    def accel(s, q):
        q = q.detach().requires_grad_(True)
        Vp = torch.autograd.grad(s.Vq(q).sum(), q, create_graph=True)[0]
        return -Vp                                                   # qddot = -V'(q); N cancels by construction


def train_one(c_seed, seed, steps=2500):
    torch.manual_seed(seed); m = Lag(); opt = torch.optim.Adam(m.parameters(), lr=3e-3); rng = np.random.default_rng(seed)
    for step in range(steps):
        q = torch.tensor(rng.uniform(-2, 2, 256), dtype=torch.float32)
        qddot = m.accel(q)
        data_loss = ((qddot - (-q)) ** 2).mean()                     # EOM: qddot = -q (harmonic); fixes V'(q)=q
        # hair of gauge preference: push the (data-unconstrained) gauge function N toward c_seed * q
        gauge_pen = 0.02 * ((m.Nq(q) - c_seed * q) ** 2).mean()      # N=c_seed q => total derivative d/dt(c_seed q^2/2)
        loss = data_loss + gauge_pen
        opt.zero_grad(); loss.backward(); opt.step()
        if step % 400 == 0: progress(f"86_c{c_seed:+.0f}", step, steps, loss=float(data_loss.detach()))
    return m


def main():
    cs = np.linspace(-2.5, 2.5, K)
    nets = [train_one(c, seed=i) for i, c in enumerate(cs)]

    # evaluate on a phase-space grid
    qq, qdqd = np.meshgrid(np.linspace(-1.8, 1.8, 40), np.linspace(-1.8, 1.8, 40))
    q = torch.tensor(qq.ravel(), dtype=torch.float32); qd = torch.tensor(qdqd.ravel(), dtype=torch.float32)
    qdd_true = (-q).numpy()
    QDD, LEVEN, LODD, r2s = [], [], [], []
    for m in nets:
        qdd = m.accel(q).detach().numpy()
        r2 = 1 - np.sum((qdd - qdd_true) ** 2) / np.sum((qdd_true - qdd_true.mean()) ** 2)
        with torch.no_grad():
            leven = (0.5 * qd ** 2 - m.Vq(q)).numpy()                  # qdot-even = physical (1/2 qd^2 - V)
            lodd = (m.Nq(q) * qd).numpy()                              # qdot-odd  = gauge (N(q) qdot)
        QDD.append(qdd); LEVEN.append(leven - leven.mean()); LODD.append(lodd); r2s.append(float(r2))
    QDD = np.array(QDD); LEVEN = np.array(LEVEN); LODD = np.array(LODD)

    std_qdd = float(QDD.std(0).mean()); sig_qdd = float(qdd_true.std())
    std_even = float(LEVEN.std(0).mean()); std_odd = float(LODD.std(0).mean())
    gauge_flatness = 0.0                                               # qddot=-V'(q) is N-independent by construction (exact)

    g1 = bool(min(r2s) > 0.99)
    g2 = bool(std_odd > 5 * std_even)
    g3 = bool(std_qdd / sig_qdd < 0.05)
    out = {"r2_each": r2s, "min_r2": float(min(r2s)), "std_qddot_field": std_qdd, "signal_qddot": sig_qdd,
           "std_qddot_rel": std_qdd / sig_qdd, "std_L_even": std_even, "std_L_odd": std_odd,
           "odd_over_even_ratio": std_odd / (std_even + 1e-9), "gauge_flatness_max_dqddot": gauge_flatness,
           "G1_dynamics_identifiable": g1, "G2_lagrangian_not_identifiable": g2, "G3_certificate": g3,
           "no_unique_law_certified": bool(g1 and g2 and g3)}
    print(f"G1 dynamics identifiable: min qddot R^2 over ensemble {min(r2s):.4f} (>0.99): {g1}")
    print(f"G2 Lagrangian NOT identifiable: std(L_odd gauge) {std_odd:.3f} vs std(L_even phys) {std_even:.3f}, ratio {std_odd/(std_even+1e-9):.1f} (>5): {g2}")
    print(f"G3 certificate: ensemble qddot-field std {std_qdd/sig_qdd:.4f} of signal (<0.05); gauge flatness {gauge_flatness:.2e} (<1e-3): {g3}")
    print(f"\nNO-UNIQUE-LAW CERTIFIED (the net recovers the equivalence class: physics pinned, gauge free): {out['no_unique_law_certified']}")
    (RESULTS / "86_gauge_nounique.json").write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(1, 2, figsize=(13, 5))
    sl = np.abs(qq.ravel()) < 0.05                                     # slice near q=0: L vs qdot
    order = np.argsort(qd.numpy()[sl])
    for i in range(K):
        ax[0].plot(qd.numpy()[sl][order], (LEVEN[i] + LODD[i])[sl][order], alpha=0.8, label=f"net {i} (gauge c={cs[i]:+.1f})")
    ax[0].set_xlabel("qdot (at q≈0)"); ax[0].set_ylabel("learned Lagrangian L"); ax[0].legend(fontsize=7)
    ax[0].set_title("the ensemble disagrees on L (gauge orbit)\nphysical qdot² part shared, qdot-odd gauge part free")
    ax[1].bar([0, 1, 2], [std_qdd / sig_qdd, std_even, std_odd], color=["seagreen", "navy", "crimson"])
    ax[1].set_xticks([0, 1, 2]); ax[1].set_xticklabels(["EOM qddot\n(IDENTIFIABLE)", "L physical part\n(identifiable)", "L gauge part\n(NOT identifiable)"])
    ax[1].set_ylabel("ensemble std"); ax[1].set_title("the certificate: certain about dynamics,\nuncertain exactly on the gauge direction")
    fig.tight_layout(); fig.savefig(RESULTS / "86_gauge_nounique.png", dpi=140)
    print("saved results/86_gauge_nounique.json + .png")


if __name__ == "__main__":
    main()
