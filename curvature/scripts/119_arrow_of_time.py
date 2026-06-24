"""Step 119 — the arrow of time: a net discovers irreversibility & entropy production (the fluctuation theorem).

Poke 3 of 3 (notes/topology_rg_arrow_plan.md). Extends the friction boundary (70: universal-but-dissipative does NOT
geometrize). From trajectories ALONE, a net discovers the second law -- the entropy production as the cheapest
description that distinguishes forward from time-reversed dynamics.

Physics (web-verified, Crooks 1999): for microscopically-reversible dynamics, P_forward[x]/P_reverse[x~] = e^(sigma),
sigma = entropy produced along the trajectory; so the BAYES-OPTIMAL forward-vs-reverse discriminator's log-odds IS the
entropy production. Crooks symmetry P_F(W)/P_R(-W)=e^(W-dF); Jarzynski <e^-W>=e^-dF. Toy: overdamped Langevin particle
(gamma=kT=1) in a harmonic trap whose center is DRAGGED, U=1/2 k (x-lambda)^2; dF=0 (trap free energy is center-
independent), so sigma = dissipated work W. Driving speed (drag distance L over fixed time) sets the irreversibility.

Pre-reg (2026-06-24):
  A1 DISCOVER THE ARROW: a DeepSets net trained ONLY to classify forward vs time-reversed trajectories has a logit
     that matches the analytic entropy production -- corr(logit, W) > 0.9. The cheapest forward-vs-reverse code IS
     entropy production.
  A2 FLUCTUATION THEOREM: the work distributions satisfy Crooks -- ln[P_F(W)/P_R(-W)] is linear in W with slope ~1 --
     AND Jarzynski <e^-W>_F = 1 (= e^-dF, dF=0).
  A3 CERTIFICATE (reversibility boundary): a near-quasistatic (slow) protocol has ~zero entropy production -> forward
     and reverse are INDISTINGUISHABLE (classifier AUC ~ 0.5); fast driving -> AUC >> 0.5. Irreversibility <=> EP>0.
     Ties friction (70): time's arrow is readable iff entropy is produced.
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
from sklearn.metrics import roc_auc_score
from torch import nn

from curvlib import RESULTS, progress

K, DT, D, T = 1.0, 0.02, 1.0, 50                                   # stiffness, timestep, diffusion (kT/gamma), steps


def run(lam, rng, m):
    """m overdamped Langevin trajectories under protocol lam[T+1] (trap centers). Returns x paths [m,T+1]."""
    x = lam[0] + np.sqrt(D / K) * rng.standard_normal(m)          # start in equilibrium of the initial trap
    xs = [x.copy()]
    for n in range(T):
        x = x + DT * (-K * (x - lam[n])) + np.sqrt(2 * D * DT) * rng.standard_normal(m)
        xs.append(x.copy())
    return np.stack(xs, 1)                                        # [m, T+1]


def work(xpath, lam):
    """Sekimoto work = sum_n [U(x_n, lam_{n+1}) - U(x_n, lam_n)] (energy change from moving the trap at fixed x)."""
    xn = xpath[:, :-1]
    return (0.5 * K * ((xn - lam[1:]) ** 2 - (xn - lam[:-1]) ** 2)).sum(1)


def features(xpath, lam):
    """per-step features (x, lambda, dlambda, dx) for a DeepSets discriminator (entropy production is a path sum)."""
    xn = xpath[:, :-1]
    dl = (lam[1:] - lam[:-1])[None, :].repeat(len(xpath), 0)
    dx = xpath[:, 1:] - xpath[:, :-1]
    ln = lam[:-1][None, :].repeat(len(xpath), 0)
    return np.stack([xn, ln, dl, dx], -1).astype(np.float32)      # [m, T, 4]


def time_reverse(xpath, lam):
    """time-reversed realization: reverse the path AND the protocol (what the reverse process produces)."""
    return xpath[:, ::-1].copy(), lam[::-1].copy()


class Disc(nn.Module):
    def __init__(s):
        super().__init__()
        s.phi = nn.Sequential(nn.Linear(4, 64), nn.GELU(), nn.Linear(64, 64))
        s.rho = nn.Sequential(nn.Linear(64, 64), nn.GELU(), nn.Linear(64, 1))

    def forward(s, f):
        return s.rho(s.phi(f).sum(1))[:, 0]                       # sum over steps -> logit (= entropy production)


def make_class_data(L, rng, m=4000):
    """forward-process and reverse-process trajectories as classifier data (label 1=forward, 0=reverse)."""
    lamF = np.linspace(0, L, T + 1)                              # drag 0 -> L
    xF = run(lamF, rng, m)
    lamR = np.linspace(L, 0, T + 1)                              # reverse protocol: drag L -> 0
    xR = run(lamR, rng, m)
    fF = features(xF, lamF)
    # reverse-process trajectories, viewed in the SAME (forward) frame via time-reversal
    xRr, lamRr = time_reverse(xR, lamR)
    fR = features(xRr, lamRr)
    return fF, fR, xF, lamF


def train_disc(fF, fR, seed=0, steps=2500):
    torch.manual_seed(seed); rng = np.random.default_rng(seed)
    X = torch.from_numpy(np.concatenate([fF, fR], 0))
    y = torch.from_numpy(np.concatenate([np.ones(len(fF)), np.zeros(len(fR))]).astype(np.float32))
    m = Disc(); opt = torch.optim.Adam(m.parameters(), lr=2e-3)
    for step in range(steps):
        idx = rng.integers(0, len(X), 256)
        loss = nn.functional.binary_cross_entropy_with_logits(m(X[idx]), y[idx])
        opt.zero_grad(); loss.backward(); opt.step()
        if step % 800 == 0:
            progress(f"119_disc_L{int(10*X.shape[0])}", step, steps, loss=float(loss.detach()))
    m.eval()
    with torch.no_grad():
        logit = m(X).numpy()
    return m, logit, y.numpy()


def main():
    rng = np.random.default_rng(0)

    # ---- A1: net discovers entropy production (logit ~ analytic work) ----
    fF, fR, xF, lamF = make_class_data(L=3.0, rng=rng, m=4000)
    disc, logit, lab = train_disc(fF, fR, seed=0)
    with torch.no_grad():
        logitF = disc(torch.from_numpy(fF)).numpy()
    W_F = work(xF, lamF)
    a1_corr = float(np.corrcoef(logitF, W_F)[0, 1])
    a1 = bool(a1_corr > 0.9)

    # ---- A2: Crooks symmetry + Jarzynski ----
    big = np.random.default_rng(5)
    lamF3 = np.linspace(0, 3.0, T + 1); lamR3 = np.linspace(3.0, 0, T + 1)
    WF = work(run(lamF3, big, 60000), lamF3)
    WR = work(run(lamR3, big, 60000), lamR3)
    jarzynski = float(np.mean(np.exp(-WF)))                       # should be e^-dF = 1
    bins = np.linspace(min(WF.min(), (-WR).min()), max(WF.max(), (-WR).max()), 31)
    ctr = 0.5 * (bins[1:] + bins[:-1])
    hF, _ = np.histogram(WF, bins, density=True); hR, _ = np.histogram(-WR, bins, density=True)
    ok = (hF > 1e-3) & (hR > 1e-3)
    lr = np.log(hF[ok] / hR[ok]); slope = float(np.polyfit(ctr[ok], lr, 1)[0])  # Crooks: slope ~ 1
    a2 = bool(abs(jarzynski - 1.0) < 0.15 and abs(slope - 1.0) < 0.25)

    # ---- A3: certificate -- AUC ~0.5 when reversible (slow), >>0.5 when driven (fast) ----
    res = {}
    for tag, L, sd in [("slow", 0.2, 11), ("fast", 3.0, 22)]:
        f1, f0, xf, lf = make_class_data(L=L, rng=np.random.default_rng(sd), m=3000)
        _, lg, yy = train_disc(f1, f0, seed=1)
        auc = float(roc_auc_score(yy, lg)); meanW = float(work(xf, lf).mean())
        res[tag] = {"auc": auc, "mean_sigma": meanW}
    a3 = bool(res["slow"]["auc"] < 0.6 and res["fast"]["auc"] > 0.7 and res["fast"]["mean_sigma"] > 5 * res["slow"]["mean_sigma"])

    out = {"A1_logit_work_corr": a1_corr, "A2_jarzynski_mean_exp_negW": jarzynski, "A2_crooks_slope": slope,
           "A3_slow": res["slow"], "A3_fast": res["fast"],
           "A1_discover_arrow": a1, "A2_fluctuation_theorem": a2, "A3_reversibility_certificate": a3,
           "arrow_of_time_discovered": bool(a1 and a2 and a3),
           "verdict": ("ARROW OF TIME DISCOVERED: a net trained ONLY to tell forward from time-reversed trajectories "
                       "learns a logit that IS the entropy production (corr to analytic dissipated work = {:.3f}) -- the "
                       "cheapest forward-vs-reverse code is the second law. The work obeys the fluctuation theorem "
                       "(Crooks log-ratio slope {:.2f}~1; Jarzynski <e^-W>={:.2f}~1=e^-dF). And the certificate: a "
                       "near-quasistatic protocol produces ~zero entropy (mean sigma {:.3f}) so forward and reverse are "
                       "INDISTINGUISHABLE (AUC {:.2f}~0.5), while fast driving (sigma {:.2f}) is readable (AUC {:.2f}). "
                       "Time's arrow is legible iff entropy is produced -- ties the friction boundary (70)."
                       .format(a1_corr, slope, jarzynski, res["slow"]["mean_sigma"], res["slow"]["auc"],
                               res["fast"]["mean_sigma"], res["fast"]["auc"])
                       if (a1 and a2 and a3) else "PARTIAL -- see numbers (honest).")}
    print(f"A1 discover the arrow: corr(logit, work)={a1_corr:.3f} (>0.9): {a1}")
    print(f"A2 fluctuation theorem: Jarzynski <e^-W>={jarzynski:.3f} (~1), Crooks slope={slope:.2f} (~1): {a2}")
    print(f"A3 certificate: slow AUC={res['slow']['auc']:.2f} (sigma {res['slow']['mean_sigma']:.3f}) vs "
          f"fast AUC={res['fast']['auc']:.2f} (sigma {res['fast']['mean_sigma']:.2f}): {a3}")
    print(f"\nARROW OF TIME DISCOVERED: {out['arrow_of_time_discovered']}")
    (RESULTS / "119_arrow_of_time.json").write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(1, 3, figsize=(15, 4.6))
    ax[0].scatter(W_F, logitF, alpha=0.2, c="seagreen", s=8)
    ax[0].set_xlabel("analytic entropy production σ = W"); ax[0].set_ylabel("net logit (forward vs reverse)")
    ax[0].set_title(f"A1 · the net discovers entropy production\ncorr={a1_corr:.3f}")
    ax[1].plot(ctr[ok], lr, "o", color="crimson"); ax[1].plot(ctr[ok], ctr[ok], "k--", lw=0.8, label="slope 1 (Crooks)")
    ax[1].set_xlabel("W"); ax[1].set_ylabel("ln[P_F(W)/P_R(-W)]")
    ax[1].set_title(f"A2 · fluctuation theorem\nslope={slope:.2f}, Jarzynski={jarzynski:.2f}"); ax[1].legend(fontsize=8)
    ax[2].bar(["slow\n(reversible)", "fast\n(driven)"], [res["slow"]["auc"], res["fast"]["auc"]],
              color=["slateblue", "darkorange"])
    ax[2].axhline(0.5, ls="--", c="k", lw=0.6); ax[2].set_ylim(0.4, 1.0); ax[2].set_ylabel("classifier AUC (read time's arrow)")
    ax[2].set_title("A3 · arrow legible iff entropy produced")
    fig.suptitle("The arrow of time: a net discovers entropy production as the cheapest forward-vs-reverse code")
    fig.tight_layout(); fig.savefig(RESULTS / "119_arrow_of_time.png", dpi=140)
    print("saved results/119_arrow_of_time.json + .png")


if __name__ == "__main__":
    main()
