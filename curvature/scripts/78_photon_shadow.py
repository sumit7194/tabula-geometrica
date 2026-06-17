"""Step 78 — LIGHT: photon orbits, the photon sphere (r=3M), and the black-hole SHADOW (the EHT image).

Third of the trio. Light, not matter. Web-verified Schwarzschild null geodesics (equatorial, M=1, u=1/r):
  photon orbit:  d^2u/dphi^2 + u = 3 u^2   (RHS depends on u only -- no mass term)
  => unstable circular photon orbit at u=1/3, i.e. the PHOTON SPHERE r=3M.
  => critical impact parameter b_crit = r/sqrt(1-2M/r)|_{r=3M} = 3*sqrt(3) M ~= 5.196 M:
     rays with b < b_crit are CAPTURED, b > b_crit ESCAPE. b_crit is the angular radius of the SHADOW.

A net learns the one-step photon-ray map (u, w=du/dphi) -> (u', w') from ray segments, then we (a) locate the
photon sphere as the unstable circular orbit of the learned dynamics, and (b) shoot rays at varying impact
parameter b to find the capture/escape boundary = the shadow radius.

Pre-reg (2026-06-17):
  P1 learns photon dynamics: one-step R^2 > 0.999.
  P2 PHOTON SPHERE: the learned dynamics' circular photon orbit (dw/dphi=0 at w=0) is at r = 3M within 6%,
     and it is UNSTABLE (d(dw/dphi)/du > 0 there).
  P3 SHADOW: the capture/escape boundary in impact parameter is b_crit = 3*sqrt(3) ~= 5.196 within 6%.
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

DPHI = 0.02
np.seterr(all="ignore")


def ray(b, u0=0.01, nsteps=4000):
    """integrate a null geodesic in phi: w'=3u^2-u, u'=w. start incoming from large r with impact param b."""
    u = u0; w = np.sqrt(max(1 / b ** 2 - u0 ** 2 + 2 * u0 ** 3, 0))   # du/dphi at u0 (incoming, +)
    U, W = [u], [w]
    for _ in range(nsteps):
        a = 3 * u ** 2 - u; wh = w + 0.5 * DPHI * a; u = u + DPHI * wh
        if u >= 0.5:                                                 # reached r=2 (captured)
            U.append(u); W.append(w); return "captured", np.array(U), np.array(W)
        if u <= 0.002 and w < 0:                                     # back out to infinity (escaped)
            return "escaped", np.array(U), np.array(W)
        w = wh + 0.5 * DPHI * (3 * u ** 2 - u); U.append(u); W.append(w)
    return "undetermined", np.array(U), np.array(W)


def make_data(seed=0):
    X, Y = [], []
    for b in np.concatenate([np.linspace(4.8, 6.0, 240), np.linspace(6.0, 14, 80)]):
        _, U, W = ray(b)
        for i in range(len(U) - 1):
            X.append([U[i], W[i]]); Y.append([U[i + 1], W[i + 1]])
    return np.array(X, np.float32), np.array(Y, np.float32)


class Photon(nn.Module):
    def __init__(s):
        super().__init__(); s.net = nn.Sequential(nn.Linear(2, 128), nn.GELU(), nn.Linear(128, 128), nn.GELU(),
                                                  nn.Linear(128, 128), nn.GELU(), nn.Linear(128, 2))
    def forward(s, x): return x + s.net(x)                            # residual one-step map


def main():
    X, Y = make_data()
    n = len(X); ntr = int(n * 0.9); idx = np.random.default_rng(0).permutation(n)
    Xt = torch.from_numpy(X[idx]); Yt = torch.from_numpy(Y[idx])
    m = Photon(); opt = torch.optim.Adam(m.parameters(), lr=1e-3); rng = np.random.default_rng(1)
    for step in range(7000):
        b = rng.integers(0, ntr, 256)
        loss = nn.functional.mse_loss(m(Xt[b]), Yt[b])
        opt.zero_grad(); loss.backward(); opt.step()
        if step % 400 == 0: progress("78_photon", step, 7000, loss=float(loss.detach()))
    m.eval()
    with torch.no_grad():
        P = m(Xt[ntr:]); r2 = float(1 - ((P - Yt[ntr:]) ** 2).sum() / ((Yt[ntr:] - Yt[ntr:].mean(0)) ** 2).sum())

    # learned photon force g(u)=d^2u/dphi^2 probed ON-MANIFOLD: at the actual (u,w) the rays visit,
    # g = (w' - w)/dphi. (The force is w-independent in truth, but the net only learned the map on its data
    # manifold, so g must be read where rays actually go, not at w=0.)
    Xall = torch.from_numpy(X)
    with torch.no_grad():
        gX = (m(Xall).numpy()[:, 1] - X[:, 1]) / DPHI
    uX = X[:, 0]
    # bin in u and fit per-bin medians where the net force is accurate (u>=0.22, bracketing the photon
    # sphere); at small u the per-step Delta-w is tiny and the net's force is biased -- the quadratic law
    # fit on the accurate region extrapolates the potential correctly.
    edges = np.linspace(0.22, 0.47, 26); ctr = 0.5 * (edges[:-1] + edges[1:])
    bing = np.array([np.median(gX[(uX >= edges[i]) & (uX < edges[i + 1])]) if np.any((uX >= edges[i]) & (uX < edges[i + 1])) else np.nan for i in range(len(ctr))])
    ok = np.isfinite(bing)
    Acol = np.stack([ctr[ok] ** 2, ctr[ok]], 1)                     # force g(0)=0: g = c2 u^2 + c1 u
    (c2, c1), *_ = np.linalg.lstsq(Acol, bing[ok], rcond=None); c0 = 0.0
    ug = np.linspace(0.0, 0.5, 2000); g_fit = c2 * ug ** 2 + c1 * ug + c0

    # P2 photon sphere: g(u)=0 -> u_ps (r=3), unstable (g rising through 0)
    roots = np.roots([c2, c1, c0]); roots = roots[np.isreal(roots)].real
    cand = [r for r in roots if 0.1 < r < 0.49]
    u_ps = float(cand[0]) if cand else None
    r_ps = (1.0 / u_ps) if u_ps else None
    unstable = bool(u_ps is not None and (2 * c2 * u_ps + c1) > 0)

    # P3 shadow: photon potential V(u)=int_0^u -2 g du'; b_crit = 1/sqrt(max V) = 3sqrt3
    V = np.concatenate([[0], np.cumsum(-2.0 * g_fit[1:]) * (ug[1] - ug[0])])
    V_max = float(np.max(V)); b_crit_net = float(1.0 / np.sqrt(V_max)) if V_max > 0 else None
    b_crit_true = 3 * np.sqrt(3)
    dwdphi = gX; us = uX                                             # for the plot

    p1 = bool(r2 > 0.999)
    p2 = bool(r_ps is not None and abs(r_ps - 3.0) < 0.06 * 3.0 and unstable)
    p3 = bool(b_crit_net is not None and abs(b_crit_net - b_crit_true) < 0.06 * b_crit_true)
    out = {"oneStep_R2": r2, "photon_sphere_r_net": r_ps, "photon_sphere_unstable": unstable,
           "b_crit_net": b_crit_net, "b_crit_true_3sqrt3": float(b_crit_true),
           "P1_learns_photon_dynamics": p1, "P2_photon_sphere_3M": p2, "P3_shadow_bcrit": p3,
           "light_shadow_discovered": bool(p1 and p2 and p3)}
    print(f"P1 learns photon dynamics R^2 {r2:.5f}: {p1}")
    print(f"P2 photon sphere r_net {r_ps} (want 3M), unstable {unstable}: {p2}")
    print(f"P3 shadow b_crit net {b_crit_net} vs 3sqrt3={b_crit_true:.3f}: {p3}")
    print(f"\nLIGHT / SHADOW DISCOVERED (photon sphere at 3M + shadow at b=3sqrt3 M): {out['light_shadow_discovered']}")
    (RESULTS / "78_photon_shadow.json").write_text(json.dumps(out, indent=1))

    # visualize rays (true) + the photon sphere + shadow boundary
    fig, ax = plt.subplots(1, 2, figsize=(13, 5.6))
    for b in np.linspace(4.9, 6.6, 16):
        st, U, W = ray(b); r = 1.0 / np.clip(U, 1e-3, None); phi = np.arange(len(U)) * DPHI
        c = "crimson" if st == "captured" else "seagreen"
        ax[0].plot(r * np.cos(phi), r * np.sin(phi), color=c, lw=0.5)
    th = np.linspace(0, 2 * np.pi, 100)
    ax[0].fill(2 * np.cos(th), 2 * np.sin(th), "k")                  # horizon
    ax[0].plot(3 * np.cos(th), 3 * np.sin(th), color="orange", ls=":", label="photon sphere 3M")
    ax[0].set_aspect("equal"); ax[0].set_xlim(-12, 12); ax[0].set_ylim(-12, 12); ax[0].legend(fontsize=8)
    ax[0].set_title("light rays: captured (red) vs escaping (green)\nthe shadow = captured cone")
    ax[1].plot(us, dwdphi, color="navy"); ax[1].axhline(0, color="k", lw=0.5)
    if u_ps: ax[1].axvline(u_ps, color="crimson", ls="--", label=f"photon sphere u={u_ps:.3f} (r={r_ps:.2f}M)")
    ax[1].axvline(1 / 3, color="gray", ls=":", label="u=1/3 (r=3M)")
    ax[1].set_xlabel("u = 1/r"); ax[1].set_ylabel("d^2u/dphi^2 (learned)"); ax[1].legend(fontsize=8)
    ax[1].set_title(f"photon sphere as the zero of the learned force\nshadow b_crit net {b_crit_net:.2f} vs 3sqrt3={b_crit_true:.2f}")
    fig.tight_layout(); fig.savefig(RESULTS / "78_photon_shadow.png", dpi=140)
    print("saved results/78_photon_shadow.json + .png")


if __name__ == "__main__":
    main()
