"""Step 136 — global PINN for scalar-field collapse: the untried lever (physics-in-loss, NO rollout).

Hail-mary Phase 2 / vm_plan C. Our learned AUTOREGRESSIVE emulator failed Choptuik collapse for a DIAGNOSED reason
(exp11/exp12): tiny per-step field errors compound and the stiff geometry readout (2m/r) amplifies them into spurious
collapse -- the ROLLOUT is the wall (global one-shot 0.99 vs autoregressive 0.50 on identical data, exp12). The
literature's NN-Choptuik success (Choptuik et al., arXiv:2511.15247, Mach. Learn. Sci. Technol. 2026) is a PINN: a
GLOBAL space-time solve with the physics in the loss, which never rolls out and so sidesteps exactly this wall. This
script builds that untried lever in-repo -- a global PINN -- and asks whether it reproduces the disperse-vs-collapse
behavior the rollout could not.

HONEST SCOPE (stated up front, no overclaim): this is a PLAIN-MLP PINN, NOT the paper's ModPINN (which adds QRes
layers, RBF/tanh embeddings, temporal+spatial causality weighting, residual-adaptive remeshing, SOAP, 100k epochs on an
A100). We aim to DEMONSTRATE THE PARADIGM (a global physics-in-loss solve, no rollout, reproduces the FD reference and
the disperse/collapse dichotomy), NOT to match near-critical accuracy or recover the mass-scaling exponent -- those need
the full ModPINN machinery (cited). Reference = our verified FD solver curvature/hailmary/collapse.py.

Formulation (polar-areal, G=c=1; collapse.py's exact forms). Outputs (Phi, Pi, C, alpha) of (t,r); a = 1/sqrt(1-C):
  field:        d_t Phi = d_r( alpha Pi / a )                                  (R_Phi)
                d_t Pi  = (1/r^2) d_r( r^2 alpha Phi / a )                      (R_Pi)
  constraints:  d_r ln a     = (1 - a^2)/(2r) + 2 pi r (Phi^2 + Pi^2)          (R_a, Hamiltonian)
                d_r ln alpha = (a^2 - 1)/(2r) + 2 pi r (Phi^2 + Pi^2)          (R_al, polar slicing)
  IC (t=0): Phi=phi'(0,r), Pi=0 (time-symmetric), C,alpha from the FD constraint solve.
  BC: r=r_min (regularity) and r=R (outer) anchored to the FD reference. 2m/r = C; C->1 = apparent horizon.

Pre-reg (2026-06-26):
  G1 GLOBAL SOLVE WORKS (subcritical A=0.02): the PINN matches the FD reference on the field -- relative L2 of Phi over
     the interior space-time < 0.20 -- AND reproduces DISPERSAL (max C < 0.2, no spurious horizon). The global
     physics-in-loss solve succeeds in the regime where the autoregressive rollout spuriously collapsed (exp11 D1).
  G2 DICHOTOMY (criticality, qualitative): a supercritical PINN (A=0.40) drives C far higher than the subcritical one
     (max C_super > 3x max C_sub, and > 0.5) -- the global solve distinguishes collapse from dispersal. (Honest: the
     near-horizon region is the hard part for a plain MLP; we report the achieved max C, not a claim of horizon-exact.)
  G3 NO ROLLOUT (the thesis): the solve is purely global (physics-in-loss over collocation points; zero autoregressive
     steps), so it structurally cannot suffer the rollout-amplification wall (exp12) -- confirmed by construction +
     reported residuals. Re-confirms the project's structure-by-construction thesis from the literature's own paradigm.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "hailmary"))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import torch
from torch import nn

from curvlib import RESULTS, progress
from collapse import ScalarCollapse

PI = np.pi
DEVICE = (sys.argv[sys.argv.index("--device") + 1] if "--device" in sys.argv else "cpu")
R_MIN, R_MAX, T_END = 0.1, 20.0, 14.0
N_R, N_T = 96, 64                                                  # FD reference grid for IC/BC/comparison
STEPS = 40000


def fd_reference(A):
    """FD ground truth on a (N_T x N_R) grid: Phi, Pi, C, alpha. Reuses collapse.py (verified solver)."""
    sim = ScalarCollapse(n=600, R=R_MAX, cfl=0.2)
    Phi, Pi = sim.initial_data(A)
    dt = sim.dt; nsteps = int(T_END / dt)
    t_grid = np.linspace(0, T_END, N_T)
    grab = {int(round(t / dt)): i for i, t in enumerate(t_grid)}
    rfull = sim.r
    rec = {}
    cur = (Phi.copy(), Pi.copy())
    for step in range(0, nsteps + 1):
        if step in grab:
            a, al = sim.solve_metric(*cur)
            C = 1 - 1 / a ** 2
            rec[grab[step]] = np.stack([cur[0], cur[1], C, al])     # (4, n_full)
        if step < nsteps:
            cur = sim.step(*cur)
            if not np.isfinite(cur[0]).all():
                # horizon/lapse collapse -> freeze last good slice for remaining times (FD evolution halts)
                for k in range(len(t_grid)):
                    rec.setdefault(k, rec[max(rec)])
                break
    r_grid = np.linspace(R_MIN, R_MAX, N_R)
    G = np.zeros((N_T, N_R, 4), np.float32)
    for ti in range(N_T):
        sl = rec.get(ti, rec[max(rec)])
        for c in range(4):
            G[ti, :, c] = np.interp(r_grid, rfull, sl[c])
    return t_grid.astype(np.float32), r_grid.astype(np.float32), G


class PINN(nn.Module):
    def __init__(s, w=96, depth=5):
        super().__init__()
        layers = [nn.Linear(2, w), nn.Tanh()]
        for _ in range(depth - 1):
            layers += [nn.Linear(w, w), nn.Tanh()]
        layers += [nn.Linear(w, 4)]
        s.net = nn.Sequential(*layers)

    def forward(s, t, r):
        h = s.net(torch.stack([t / T_END, r / R_MAX], -1))
        Phi = h[..., 0]; Pi = h[..., 1]
        C = 0.999 * torch.sigmoid(h[..., 2])                       # C in [0,1)  (2m/r)
        al = torch.nn.functional.softplus(h[..., 3]) + 1e-3        # alpha > 0
        return Phi, Pi, C, al


def grads(y, t, r):
    g = torch.autograd.grad(y, [t, r], grad_outputs=torch.ones_like(y), create_graph=True)
    return g[0], g[1]


def residuals(m, t, r):
    t = t.requires_grad_(True); r = r.requires_grad_(True)
    Phi, Pi, C, al = m(t, r)
    a = 1.0 / torch.sqrt(torch.clamp(1 - C, min=1e-4))
    Phi_t, Phi_r = grads(Phi, t, r)
    Pi_t, Pi_r = grads(Pi, t, r)
    _, C_r = grads(C, t, r)
    _, al_r = grads(al, t, r)
    a_r = 0.5 * a / torch.clamp(1 - C, min=1e-4) * C_r             # d a/dr from a=(1-C)^{-1/2}
    S = 2 * PI * r * (Phi ** 2 + Pi ** 2)
    # field eqs (expand d_r of the fluxes via product rule using autograd pieces)
    F = al * Pi / a                                                # flux for Phi_dot
    F_r = (al_r * Pi + al * Pi_r) / a - al * Pi * a_r / a ** 2
    R_Phi = Phi_t - F_r
    Gf = al * Phi / a                                              # r^2 Gf flux for Pi_dot
    Gf_r = (al_r * Phi + al * Phi_r) / a - al * Phi * a_r / a ** 2
    R_Pi = Pi_t - (2.0 / r * Gf + Gf_r)                            # (1/r^2) d_r(r^2 Gf) = 2/r Gf + Gf_r
    R_a = a_r / a - ((1 - a ** 2) / (2 * r) + S)
    R_al = al_r / al - ((a ** 2 - 1) / (2 * r) + S)
    return R_Phi, R_Pi, R_a, R_al


def solve(A, seed=0):
    torch.manual_seed(seed); rng = np.random.default_rng(seed)
    tg, rg, G = fd_reference(A)
    dev = DEVICE
    Gt = torch.tensor(G, device=dev)
    tG = torch.tensor(tg, device=dev); rG = torch.tensor(rg, device=dev)
    # IC points (t=0, all r) and BC points (r=r_min and r=R, all t), anchored to FD
    r_ic = rG; t_ic = torch.zeros_like(rG); y_ic = Gt[0]                       # (N_R,4)
    t_bc = tG; rL = torch.full_like(tG, R_MIN); rR = torch.full_like(tG, R_MAX)
    yL = Gt[:, 0, :]; yR = Gt[:, -1, :]
    m = PINN().to(dev); opt = torch.optim.Adam(m.parameters(), lr=1.5e-3)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, STEPS, eta_min=2e-4)
    for step in range(STEPS):
        tc = torch.rand(4096, device=dev) * T_END
        rc = R_MIN + torch.rand(4096, device=dev) * (R_MAX - R_MIN)
        R_Phi, R_Pi, R_a, R_al = residuals(m, tc, rc)
        l_pde = (R_Phi ** 2).mean() + (R_Pi ** 2).mean() + (R_a ** 2).mean() + (R_al ** 2).mean()
        Phi_ic, Pi_ic, C_ic, al_ic = m(t_ic, r_ic)
        l_ic = ((Phi_ic - y_ic[:, 0]) ** 2 + (Pi_ic - y_ic[:, 1]) ** 2
                + (C_ic - y_ic[:, 2]) ** 2 + (al_ic - y_ic[:, 3]) ** 2).mean()
        out_L = m(t_bc, rL); out_R = m(t_bc, rR)
        l_bc = sum(((out_L[k] - yL[:, k]) ** 2 + (out_R[k] - yR[:, k]) ** 2).mean() for k in range(4))
        loss = l_pde + 1e3 * l_ic + 1e2 * l_bc
        opt.zero_grad(); loss.backward(); opt.step(); sched.step()
        if step % 2000 == 0:
            progress(f"136_pinn_A{A}", step, STEPS, loss=float(loss.detach()), pde=float(l_pde.detach()))
    # evaluate on the interior FD grid
    m.eval()
    TT, RR = torch.meshgrid(tG, rG, indexing="ij")
    with torch.no_grad():
        Phi_p, Pi_p, C_p, al_p = m(TT.reshape(-1), RR.reshape(-1))
    Phi_p = Phi_p.reshape(N_T, N_R).cpu().numpy(); C_p = C_p.reshape(N_T, N_R).cpu().numpy()
    relL2_Phi = float(np.sqrt(((Phi_p - G[..., 0]) ** 2).sum()) / (np.sqrt((G[..., 0] ** 2).sum()) + 1e-9))
    relL2_C = float(np.sqrt(((C_p - G[..., 2]) ** 2).sum()) / (np.sqrt((G[..., 2] ** 2).sum()) + 1e-9))
    return {"A": A, "relL2_Phi": relL2_Phi, "relL2_C": relL2_C,
            "max_C_pinn": float(C_p.max()), "max_C_fd": float(G[..., 2].max()),
            "_grids": (tg, rg, G, Phi_p, C_p)}


def main():
    print(f"device={DEVICE}")
    sub = solve(0.02); sup = solve(0.40)
    g1 = bool(sub["relL2_Phi"] < 0.20 and sub["max_C_pinn"] < 0.2)
    g2 = bool(sup["max_C_pinn"] > 3 * sub["max_C_pinn"] and sup["max_C_pinn"] > 0.5)
    g3 = True  # no rollout by construction (global physics-in-loss); reported, not gated numerically

    out = {"subcritical": {k: v for k, v in sub.items() if not k.startswith("_")},
           "supercritical": {k: v for k, v in sup.items() if not k.startswith("_")},
           "G1_global_solve_subcritical": g1, "G2_dichotomy": g2, "G3_no_rollout": g3,
           "global_pinn_demonstrates_paradigm": bool(g1 and g2),
           "scope_caveat": ("plain-MLP PINN, NOT the paper's ModPINN; demonstrates the global physics-in-loss paradigm "
                            "(no rollout) + the disperse/collapse dichotomy; does NOT claim near-critical accuracy or "
                            "mass-scaling (those need ModPINN + adaptive sampling + A100, arXiv:2511.15247)."),
           "verdict": ("GLOBAL PINN DEMONSTRATES THE PARADIGM (the untried lever). A plain-MLP global physics-in-loss "
                       "solve -- ZERO autoregressive steps -- reproduces the FD reference for the SUBCRITICAL collapse "
                       "(relative L2 of Phi {:.3f}, max 2m/r {:.3f} -> DISPERSES, no spurious horizon) where the learned "
                       "AUTOREGRESSIVE emulator spuriously collapsed (exp11/exp12, the rollout wall). And it reproduces "
                       "the DICHOTOMY: the supercritical solve drives 2m/r to {:.3f} (vs {:.3f} subcritical). The global "
                       "solve sidesteps the rollout-amplification wall by construction -- the literature's PINN paradigm "
                       "(arXiv:2511.15247) is the same structure-by-construction principle this project champions. SCOPE: "
                       "plain MLP, paradigm demonstration; near-critical accuracy needs the full ModPINN (cited)."
                       .format(sub["relL2_Phi"], sub["max_C_pinn"], sup["max_C_pinn"], sub["max_C_pinn"])
                       if (g1 and g2) else "PARTIAL/HONEST -- see numbers; the plain MLP may not fully resolve the "
                       "near-horizon supercritical region (expected; ModPINN territory).")}
    print(f"G1 subcritical global solve: relL2_Phi={sub['relL2_Phi']:.3f} (<0.20), max C_pinn={sub['max_C_pinn']:.3f} (<0.2, disperses): {g1}")
    print(f"G2 dichotomy: max C super={sup['max_C_pinn']:.3f} vs sub={sub['max_C_pinn']:.3f} (super>3x & >0.5): {g2}")
    print(f"   (FD reference max C: sub {sub['max_C_fd']:.3f}, super {sup['max_C_fd']:.3f}; PINN relL2_C sub {sub['relL2_C']:.3f})")
    print(f"\nGLOBAL PINN DEMONSTRATES PARADIGM: {out['global_pinn_demonstrates_paradigm']}")
    (RESULTS / "136_choptuik_pinn.json").write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(2, 2, figsize=(12, 8))
    for col, (res, ttl) in enumerate([(sub, "subcritical A=0.02 (disperses)"), (sup, "supercritical A=0.40 (collapses)")]):
        tg, rg, G, Phi_p, C_p = res["_grids"]
        ax[0, col].pcolormesh(rg, tg, G[..., 2], shading="auto", vmin=0, vmax=1, cmap="inferno")
        ax[0, col].set_title(f"FD 2m/r — {ttl}"); ax[0, col].set_ylabel("t")
        im = ax[1, col].pcolormesh(rg, tg, C_p, shading="auto", vmin=0, vmax=1, cmap="inferno")
        ax[1, col].set_title(f"PINN 2m/r (relL2_Phi {res['relL2_Phi']:.2f})"); ax[1, col].set_xlabel("r"); ax[1, col].set_ylabel("t")
    fig.colorbar(im, ax=ax, label="2m/r", shrink=0.6)
    fig.suptitle("Global PINN (physics-in-loss, no rollout) vs FD reference — paradigm demonstration")
    fig.savefig(RESULTS / "136_choptuik_pinn.png", dpi=130)
    print("saved results/136_choptuik_pinn.json + .png")


if __name__ == "__main__":
    main()
