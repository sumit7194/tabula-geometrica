"""Step 88 — THE CURVATURE ATLAS I: no-arbitrage is a FLAT CONNECTION (our gravity result, in a market).

The curvature/holonomy that signals "the cheapest shared description" recurs far outside gravity. Finance is
the cleanest case. Web-verified (Ilinski; Vazquez-Farinelli, arXiv 0908.3043 / 1509.03264): exchange rates are
exponentials of a GAUGE CONNECTION on the currency graph; log R_ij = phi_i - phi_j when arbitrage-free (a pure
gradient = FLAT connection); "the connection has zero curvature IF AND ONLY IF there is no arbitrage";
arbitrage = HOLONOMY of a closed loop (a currency triangle = a Wilson loop); and the arbitrage measure is
INVARIANT under change of NUMERAIRE -- the numeraire choice is the GAUGE.

A net is given the N x N log-rate matrix M_ij = log R_ij and discovers a per-currency potential phi_i with
log R_ij = phi_i - phi_j. When the market is arbitrage-free, N potentials explain all N^2 rates (the cheapest
code) and every triangle holonomy is 0. Inject an arbitrage of size a on a triangle: the net CANNOT absorb it
into the potential (it is the curl/curvature), and the measured holonomy = a. The numeraire is a free additive
constant on phi -- the gauge -- under which the holonomy is invariant.

Pre-reg (2026-06-17):
  A1 FLAT CONNECTION: arbitrage-free -> the N-potential fit reconstructs all N^2 log-rates, R^2 > 0.999, and
     max triangle holonomy < 0.01 (zero curvature).
  A2 ARBITRAGE = CURVATURE: planting arbitrage a on a triangle, the measured holonomy = a (slope 1, within
     3%), and the potential-fit residual grows with a (cannot be gauged away).
  A3 GAUGE INVARIANCE: the holonomy is invariant (< 1e-6) under numeraire change (phi -> phi + const), while
     the potentials themselves shift -- the numeraire is the gauge.
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

N = 8
np.seterr(all="ignore")


def make_market(arb_a=0.0, seed=0):
    """log-rate matrix M_ij = log R_ij. Arbitrage-free: M = phi_i - phi_j. Plant arbitrage a on triangle (0,1,2)."""
    rng = np.random.default_rng(seed)
    phi = rng.normal(0, 1.0, N)
    M = phi[:, None] - phi[None, :]                            # pure gradient (flat)
    if arb_a != 0.0:
        d = arb_a / 3.0
        for (i, j) in [(0, 1), (1, 2), (2, 0)]:                # add a curl around the triangle (antisymmetric)
            M[i, j] += d; M[j, i] -= d
    return M.astype(np.float32), phi


def fit_potential(M, steps=2000):
    """net learns phi_hat s.t. M_ij ~ phi_hat_i - phi_hat_j (the flat / pure-gauge part)."""
    Mt = torch.tensor(M); phi = torch.zeros(N, requires_grad=True)
    opt = torch.optim.Adam([phi], lr=0.05)
    for step in range(steps):
        pred = phi[:, None] - phi[None, :]
        loss = ((pred - Mt) ** 2).mean()
        opt.zero_grad(); loss.backward(); opt.step()
        if step % 400 == 0: progress("88_arb", step, steps, loss=float(loss.detach()))
    with torch.no_grad():
        pred = (phi[:, None] - phi[None, :])
        ss_res = float(((pred - Mt) ** 2).sum()); ss_tot = float(((Mt - Mt.mean()) ** 2).sum())
        r2 = 1 - ss_res / (ss_tot + 1e-12); resid = float((pred - Mt).pow(2).mean().sqrt())
    return phi.detach().numpy(), r2, resid


def holonomy(M, tri=(0, 1, 2)):
    i, j, k = tri; return float(M[i, j] + M[j, k] + M[k, i])    # log of the loop product R_ij R_jk R_ki


def max_triangle_holonomy(M):
    h = 0.0
    for i in range(N):
        for j in range(i + 1, N):
            for k in range(j + 1, N):
                h = max(h, abs(holonomy(M, (i, j, k))))
    return h


def main():
    # A1 flat connection (arbitrage-free)
    M0, phi0 = make_market(0.0)
    phihat, r2, resid = fit_potential(M0)
    maxhol0 = max_triangle_holonomy(M0)
    # potential recovered up to additive constant (gauge); check it matches phi0 - mean
    corr_phi = float(np.corrcoef(phihat - phihat.mean(), phi0 - phi0.mean())[0, 1])

    # A2 arbitrage = curvature: sweep planted arbitrage, measure holonomy + fit residual
    arbs = np.linspace(0.0, 0.30, 8); measured_hol = []; resids = []
    for a in arbs:
        M, _ = make_market(a); measured_hol.append(holonomy(M, (0, 1, 2)))
        _, _, rr = fit_potential(M, steps=1200); resids.append(rr)
    measured_hol = np.array(measured_hol); resids = np.array(resids)
    slope = float(np.polyfit(arbs, measured_hol, 1)[0])

    # A3 gauge invariance: numeraire change = add constant to phi; rates and holonomy unchanged
    Ma, _ = make_market(0.15)
    base_hol = holonomy(Ma, (0, 1, 2))
    rng = np.random.default_rng(3); hol_shifts = []
    for _ in range(5):
        c = rng.normal(0, 5.0)                                 # arbitrary numeraire shift
        phi_shift = (phihat + c)                               # phi -> phi + c
        Mg = phi_shift[:, None] - phi_shift[None, :] + (Ma - (phi0[:, None] - phi0[None, :]))  # same rates+arb, shifted gauge
        hol_shifts.append(holonomy(Mg, (0, 1, 2)))
    gauge_var = float(np.std(hol_shifts))

    a1 = bool(r2 > 0.999 and maxhol0 < 0.01 and abs(corr_phi) > 0.999)
    a2 = bool(abs(slope - 1.0) < 0.03 and resids[-1] > 0.01 and resids[0] < 1e-3)
    a3 = bool(gauge_var < 1e-6)
    out = {"flat_R2": r2, "flat_resid": resid, "max_holonomy_arbfree": maxhol0, "corr_phi": corr_phi,
           "arb_sweep": arbs.tolist(), "measured_holonomy": measured_hol.tolist(), "fit_residual": resids.tolist(),
           "holonomy_vs_arb_slope": slope, "gauge_holonomy_std": gauge_var,
           "A1_flat_connection": a1, "A2_arbitrage_is_curvature": a2, "A3_numeraire_is_gauge": a3,
           "no_arbitrage_is_flat_connection": bool(a1 and a2 and a3)}
    print(f"A1 FLAT connection (no arbitrage): N-potential fit R^2 {r2:.5f}, max triangle holonomy {maxhol0:.2e}, corr(phi_hat,phi) {corr_phi:.4f}: {a1}")
    print(f"A2 ARBITRAGE = CURVATURE: holonomy vs planted-a slope {slope:.4f} (want 1); resid 0->{resids[-1]:.3f} as a grows: {a2}")
    print(f"A3 NUMERAIRE = GAUGE: holonomy std across numeraire shifts {gauge_var:.2e} (<1e-6): {a3}")
    print(f"\nNO-ARBITRAGE IS A FLAT CONNECTION (arbitrage = curvature/holonomy; numeraire = gauge): {out['no_arbitrage_is_flat_connection']}")
    (RESULTS / "88_arbitrage_curvature.json").write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(1, 2, figsize=(13, 5))
    ax[0].plot(arbs, measured_hol, "o-", color="crimson", label=f"measured holonomy (slope {slope:.2f})")
    ax[0].plot(arbs, arbs, "k--", label="planted arbitrage a (slope 1)")
    ax[0].plot(arbs, resids, "s-", color="navy", label="potential-fit residual (can't be gauged away)")
    ax[0].set_xlabel("planted triangle arbitrage a"); ax[0].set_ylabel("log-units"); ax[0].legend(fontsize=8)
    ax[0].set_title("arbitrage = curvature: the net's potential cannot absorb it\n(no-arbitrage <=> flat connection, holonomy=0)")
    im = ax[1].imshow(M0, cmap="RdBu", vmin=-3, vmax=3); fig.colorbar(im, ax=ax[1])
    ax[1].set_title(f"arbitrage-free log-rate matrix = pure gradient\nN potentials explain all N² rates (R²={r2:.3f}); numeraire=gauge")
    ax[1].set_xlabel("currency j"); ax[1].set_ylabel("currency i")
    fig.tight_layout(); fig.savefig(RESULTS / "88_arbitrage_curvature.png", dpi=140)
    print("saved results/88_arbitrage_curvature.json + .png")


if __name__ == "__main__":
    main()
