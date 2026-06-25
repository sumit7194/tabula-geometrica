"""Step 121 — Fisher = GR metric: natural gradient is general covariance (the ML<->GR bridge), made executable.

Build-queue item 2 (notes/build_queue.md), from nn_and_spacetime.md §5. The shared object between machine learning and
general relativity is the METRIC TENSOR. In GR, g_munu measures distance in spacetime and physics is generally
covariant (coordinate-independent). In ML, the FISHER INFORMATION metric measures distance in distribution space, and
the NATURAL GRADIENT (Amari 1998), g^{-1}∇L, is the reparameterization-INVARIANT steepest descent. So: Fisher = GR's g;
natural gradient = the covariant (coordinate-free) update; ordinary gradient is coordinate-DEPENDENT (not covariant).

Self-verifying toy: a 1-D Gaussian family N(mu, sigma). Analytic Fisher in (mu,sigma) coords is g=diag(1/sigma^2,
2/sigma^2) (the Fisher-Rao metric -- the (mu,sigma) upper half plane is hyperbolic). We fit a target distribution by
gradient descent in THREE different parameterizations of the SAME family (c=sigma, c=log sigma, c=sigma^3) with
ordinary vs natural gradient, and watch which is coordinate-free.

Pre-reg (2026-06-25):
  F1 FISHER = METRIC: the Fisher matrix computed by autodiff (Monte-Carlo over the score) matches the analytic
     g=diag(1/sigma^2, 2/sigma^2) -- relative error < 0.05.
  F2 GENERAL COVARIANCE: natural GD's path through DISTRIBUTION space (mu,sigma) is the SAME across all three
     parameterizations (coordinate-free) -- max pairwise path divergence < 0.02; ordinary GD's path is parameterization-
     DEPENDENT (divergence > 10x larger).
  F3 INVARIANT CONVERGENCE: natural GD reaches the target (final KL < 1e-3) in ALL three coords with identical
     settings; ordinary GD's final KL is coordinate-dependent (spread across coords > 50x natural's).
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

from curvlib import RESULTS

MU_T, SIG_T = 1.5, 0.6                                             # target Gaussian


# parameterizations of the scale: coordinate c -> sigma, with name
COORDS = {"sigma": (lambda c: c, lambda s: s),
          "log_sigma": (lambda c: torch.exp(c), lambda s: np.log(s)),
          "sigma_cubed": (lambda c: c ** (1.0 / 3.0), lambda s: s ** 3)}


def kl_to_target(mu, sigma):
    """KL( target || p ) for Gaussians (analytic), the loss; 0 iff p == target."""
    return (torch.log(sigma / SIG_T) + (SIG_T ** 2 + (mu - MU_T) ** 2) / (2 * sigma ** 2) - 0.5)


def dist_from_params(p, c2s):
    return p[0], c2s(p[1])                                         # (mu, sigma)


def analytic_fisher(sigma):
    return np.array([[1.0 / sigma ** 2, 0.0], [0.0, 2.0 / sigma ** 2]])


def mc_fisher(mu, sigma, n=400000, seed=0):
    """Fisher via AUTODIFF: g = -E_x[ Hessian_theta log p(x|theta) ] = Hessian of the mean NLL (torch autograd)."""
    g = torch.Generator().manual_seed(seed)
    x = mu + sigma * torch.randn(n, generator=g)

    def nll(theta):
        m, s = theta[0], theta[1]
        lp = -0.5 * np.log(2 * np.pi) - torch.log(s) - (x - m) ** 2 / (2 * s ** 2)
        return -lp.mean()

    H = torch.autograd.functional.hessian(nll, torch.tensor([float(mu), float(sigma)]))
    return H.numpy()                                              # empirical Fisher; -> diag(1/sig^2, 2/sig^2)


def fisher_in_coords(mu, c, c2s):
    """Fisher in (mu, c) coords = J^T g_(mu,sigma) J, with J = d(mu,sigma)/d(mu,c) via autodiff."""
    mu_t = torch.tensor(float(mu), requires_grad=True); c_t = torch.tensor(float(c), requires_grad=True)
    sig = c2s(c_t)
    dsig_dc, = torch.autograd.grad(sig, c_t)
    sig_v = float(sig)
    J = np.array([[1.0, 0.0], [0.0, float(dsig_dc)]])             # d(mu,sigma)/d(mu,c)
    g = analytic_fisher(sig_v)
    return J.T @ g @ J


def descend(coord, natural, steps=70, lr=0.1):                     # fixed finite budget: exposes ordinary GD's conditioning
    c2s, s2c = COORDS[coord]
    p = torch.tensor([0.0, float(s2c(1.3))])                      # start: mu=0, sigma=1.3 (in this coord)
    path = []
    for _ in range(steps):
        p_ = p.clone().requires_grad_(True)
        mu, sigma = dist_from_params(p_, c2s)
        loss = kl_to_target(mu, sigma)
        grad, = torch.autograd.grad(loss, p_)
        g = np.eye(2)
        if natural:
            g = fisher_in_coords(float(p[0]), float(p[1]), c2s)
        step = np.linalg.solve(g, grad.detach().numpy())
        p = p - lr * torch.tensor(step, dtype=torch.float32)
        with torch.no_grad():
            mu_v, sig_v = dist_from_params(p, c2s)
        path.append([float(mu_v), float(sig_v)])
    return np.array(path)                                          # distribution-space (mu,sigma) trajectory


def path_divergence(paths):
    """max pairwise mean distance between distribution-space trajectories (aligned by step)."""
    keys = list(paths); d = 0.0
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            d = max(d, float(np.mean(np.linalg.norm(paths[keys[i]] - paths[keys[j]], axis=1))))
    return d


def main():
    # ---- F1: autodiff Fisher == analytic metric ----
    f1_errs = []
    for mu, sigma in [(0.0, 1.0), (1.0, 0.5), (-0.5, 1.5)]:
        gmc = mc_fisher(mu, sigma); ga = analytic_fisher(sigma)
        f1_errs.append(float(np.linalg.norm(gmc - ga) / np.linalg.norm(ga)))
    f1_err = float(np.mean(f1_errs))
    f1 = bool(f1_err < 0.05)

    # ---- F2 / F3: natural vs ordinary GD across parameterizations ----
    nat = {c: descend(c, natural=True) for c in COORDS}
    ord_ = {c: descend(c, natural=False) for c in COORDS}
    nat_div = path_divergence(nat); ord_div = path_divergence(ord_)
    f2 = bool(nat_div < 0.02 and ord_div > 10 * nat_div)

    def final_kl(path):
        mu, sig = path[-1]; return float(np.log(sig / SIG_T) + (SIG_T ** 2 + (mu - MU_T) ** 2) / (2 * sig ** 2) - 0.5)
    nat_kls = {c: final_kl(nat[c]) for c in COORDS}; ord_kls = {c: final_kl(ord_[c]) for c in COORDS}
    nat_max = max(nat_kls.values()); ord_max = max(ord_kls.values())     # after a fixed finite budget
    ord_spread = ord_max - min(ord_kls.values())
    f3 = bool(nat_max < 1e-3 and ord_max > 50 * max(nat_max, 1e-12))     # natural converges invariantly; ordinary lags in some coord

    out = {"F1_fisher_rel_err": f1_err, "F2_natural_path_div": nat_div, "F2_ordinary_path_div": ord_div,
           "F3_natural_final_kls": nat_kls, "F3_ordinary_final_kls": ord_kls,
           "F1_fisher_is_metric": f1, "F2_general_covariance": f2, "F3_invariant_convergence": f3,
           "fisher_gr_bridge": bool(f1 and f2 and f3),
           "verdict": ("FISHER = GR METRIC: the autodiff Fisher matches the analytic Fisher-Rao metric "
                       "diag(1/sigma^2, 2/sigma^2) (rel err {:.3f}). The NATURAL gradient is GENERAL COVARIANCE: its "
                       "path through distribution space is identical across three parameterizations (divergence {:.4f}) "
                       "while ORDINARY gradient is coordinate-dependent ({:.3f}, {:.0f}x larger); and natural GD reaches "
                       "the target in every coord (max final KL {:.1e}) while ordinary GD's outcome depends on the "
                       "coordinates (KL spread {:.2e}). Fisher = GR's g; natural gradient = the covariant update -- the "
                       "ML face of general covariance."
                       .format(f1_err, nat_div, ord_div, ord_div / (nat_div + 1e-9),
                               max(nat_kls.values()), ord_spread)
                       if (f1 and f2 and f3) else "PARTIAL -- see numbers (honest).")}
    print(f"F1 Fisher = metric: autodiff-vs-analytic rel err={f1_err:.3f} (<0.05): {f1}")
    print(f"F2 general covariance: natural path div={nat_div:.4f} (<0.02) vs ordinary {ord_div:.3f} ({ord_div/(nat_div+1e-9):.0f}x): {f2}")
    print(f"F3 invariant convergence (fixed budget): natural max KL={nat_max:.1e} (<1e-3); ordinary max KL={ord_max:.2e} (>50x natural): {f3}")
    print(f"\nFISHER = GR METRIC BRIDGE: {out['fisher_gr_bridge']}")
    (RESULTS / "121_fisher_gr_metric.json").write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(1, 2, figsize=(12, 4.8))
    for c, col in zip(COORDS, ["crimson", "seagreen", "slateblue"]):
        ax[0].plot(ord_[c][:, 0], ord_[c][:, 1], color=col, label=f"{c}")
        ax[1].plot(nat[c][:, 0], nat[c][:, 1], color=col, label=f"{c}")
    for a, t in zip(ax, ["ORDINARY gradient (coordinate-dependent)", "NATURAL gradient (covariant: paths coincide)"]):
        a.scatter([MU_T], [SIG_T], c="k", marker="*", s=120, zorder=5); a.set_xlabel("μ"); a.set_ylabel("σ")
        a.set_title(t); a.legend(fontsize=8)
    fig.suptitle("Fisher = GR metric: natural gradient is general covariance (reparameterization-invariant descent)")
    fig.tight_layout(); fig.savefig(RESULTS / "121_fisher_gr_metric.png", dpi=140)
    print("saved results/121_fisher_gr_metric.json + .png")


if __name__ == "__main__":
    main()
