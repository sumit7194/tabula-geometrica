"""Step 16 — Phase E: the full metric field of the 2+1 well, from trajectories.

One shared pair of learned FIELDS — S_theta(q) (SPD mass-matrix/metric via
Cholesky) and phi_theta(q) (potential) — must explain many trajectories through
the step-11 anisotropic world, with motion = mass-matrix mechanics in closed
form (no implicit solves). Pre-registration E1-E4 in the lab notebook.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import torch
from curvlib import RESULTS, XY_RANGE, fields_2p1, progress
from torch import nn

H = 0.1
TARGETS_T = (1.0, 2.0, 3.0)
N_ROLL = int(round(TARGETS_T[-1] / H))
TARGET_STEPS = [int(round(t / H)) for t in TARGETS_T]
V_MAX = 0.3
STEPS = 6000
FD = 1e-4


def gen_accel(qx, qy, vx, vy):
    """Generator EOM via finite differences of the true fields."""
    def SP(x, y):
        A, B, C, D = fields_2p1(x, y)
        return B, C, D, -0.5 * (A - 1)  # phi = -(A-1)/2: attractive Gaussian well

    B, C, D, _ = SP(qx, qy)
    out = []
    dBx = (SP(qx + FD, qy)[0] - SP(qx - FD, qy)[0]) / (2 * FD)
    dBy = (SP(qx, qy + FD)[0] - SP(qx, qy - FD)[0]) / (2 * FD)
    dCx = (SP(qx + FD, qy)[1] - SP(qx - FD, qy)[1]) / (2 * FD)
    dCy = (SP(qx, qy + FD)[1] - SP(qx, qy - FD)[1]) / (2 * FD)
    dDx = (SP(qx + FD, qy)[2] - SP(qx - FD, qy)[2]) / (2 * FD)
    dDy = (SP(qx, qy + FD)[2] - SP(qx, qy - FD)[2]) / (2 * FD)
    dpx = (SP(qx + FD, qy)[3] - SP(qx - FD, qy)[3]) / (2 * FD)
    dpy = (SP(qx, qy + FD)[3] - SP(qx, qy - FD)[3]) / (2 * FD)
    # d/dt(S qdot) = 0.5 qdot' dS qdot - grad(phi)
    f1 = 0.5 * (dBx * vx**2 + 2 * dDx * vx * vy + dCx * vy**2) - dpx
    f2 = 0.5 * (dBy * vx**2 + 2 * dDy * vx * vy + dCy * vy**2) - dpy
    # subtract (dS/dt) qdot
    St_v1 = (dBx * vx + dBy * vy) * vx + (dDx * vx + dDy * vy) * vy
    St_v2 = (dDx * vx + dDy * vy) * vx + (dCx * vx + dCy * vy) * vy
    r1, r2 = f1 - St_v1, f2 - St_v2
    det = B * C - D**2
    return (C * r1 - D * r2) / det, (B * r2 - D * r1) / det


def make_dataset(n: int, seed: int):
    rng = np.random.default_rng(seed)
    qx = rng.uniform(*XY_RANGE, n)
    qy = rng.uniform(*XY_RANGE, n)
    vx = rng.uniform(-V_MAX, V_MAX, n)
    vy = rng.uniform(-V_MAX, V_MAX, n)
    X = np.stack([qx, qy, vx, vy], axis=1).astype(np.float32)
    x, y, ux, uy = qx.copy(), qy.copy(), vx.copy(), vy.copy()
    dt = 0.01
    out = np.empty((n, len(TARGETS_T), 2))
    grab = {int(round(t / dt)): i for i, t in enumerate(TARGETS_T)}
    for step in range(1, int(round(TARGETS_T[-1] / dt)) + 1):
        def rk(xx, yy, uxx, uyy):
            ax, ay = gen_accel(xx, yy, uxx, uyy)
            return uxx, uyy, ax, ay

        k1 = rk(x, y, ux, uy)
        k2 = rk(x + 0.5 * dt * k1[0], y + 0.5 * dt * k1[1],
                ux + 0.5 * dt * k1[2], uy + 0.5 * dt * k1[3])
        k3 = rk(x + 0.5 * dt * k2[0], y + 0.5 * dt * k2[1],
                ux + 0.5 * dt * k2[2], uy + 0.5 * dt * k2[3])
        k4 = rk(x + dt * k3[0], y + dt * k3[1], ux + dt * k3[2], uy + dt * k3[3])
        x = x + dt / 6 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0])
        y = y + dt / 6 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1])
        ux = ux + dt / 6 * (k1[2] + 2 * k2[2] + 2 * k3[2] + k4[2])
        uy = uy + dt / 6 * (k1[3] + 2 * k2[3] + 2 * k3[3] + k4[3])
        if step in grab:
            out[:, grab[step], 0] = x
            out[:, grab[step], 1] = y
    return X, out.reshape(n, -1).astype(np.float32)


class FieldModel(nn.Module):
    """S_theta via Cholesky (SPD always), phi_theta scalar; closed-form EOM."""

    def __init__(self, constant: bool = False):
        super().__init__()
        self.constant = constant
        if constant:
            self.par = nn.Parameter(torch.tensor([1.0, 0.0, 1.0, 0.0]))
        else:
            self.net = nn.Sequential(
                nn.Linear(2, 128), nn.Tanh(), nn.Linear(128, 128), nn.Tanh(),
                nn.Linear(128, 4),
            )
            nn.init.zeros_(self.net[-1].weight)
            nn.init.zeros_(self.net[-1].bias)

    def fields(self, q):
        if self.constant:
            o = self.par.expand(len(q), 4)
        else:
            o = self.net(q)
        l11 = nn.functional.softplus(o[:, 0] + 0.55)  # softplus(0.55) ~ 1: kinetic seed
        l21 = o[:, 1]
        l22 = nn.functional.softplus(o[:, 2] + 0.55)
        B = l11**2 + 1e-3
        D = l11 * l21
        C = l21**2 + l22**2 + 1e-3
        return B, C, D, o[:, 3]

    def accel(self, q, v):
        q = q.requires_grad_(True)
        B, C, D, phi = self.fields(q)
        vx, vy = v[:, 0], v[:, 1]
        kin_quad = 0.5 * (B * vx**2 + 2 * D * vx * vy + C * vy**2)

        def grad_q(s):
            # constant fields have no q-dependence: their spatial gradient is
            # exactly zero, which autograd reports as "unused"
            g = torch.autograd.grad(s, q, create_graph=True, allow_unused=True)[0]
            return torch.zeros_like(q) if g is None else g

        gq = grad_q(kin_quad.sum() - phi.sum())
        gB = grad_q(B.sum())
        gC = grad_q(C.sum())
        gD = grad_q(D.sum())
        St_v1 = (gB[:, 0] * vx + gB[:, 1] * vy) * vx + (gD[:, 0] * vx + gD[:, 1] * vy) * vy
        St_v2 = (gD[:, 0] * vx + gD[:, 1] * vy) * vx + (gC[:, 0] * vx + gC[:, 1] * vy) * vy
        r1, r2 = gq[:, 0] - St_v1, gq[:, 1] - St_v2
        det = B * C - D**2
        return torch.stack([(C * r1 - D * r2) / det, (B * r2 - D * r1) / det], dim=1)

    def forward(self, X):
        q, v = X[:, :2], X[:, 2:]
        xs = []
        for step in range(1, N_ROLL + 1):
            a1 = self.accel(q, v)
            qm, vm = q + 0.5 * H * v, v + 0.5 * H * a1
            a2 = self.accel(qm, vm)
            q = q + H * vm
            v = v + H * a2
            if step in TARGET_STEPS:
                xs.append(q)
        return torch.cat(xs, dim=1)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--constant", action="store_true")
    args = p.parse_args()
    tag = "_const" if args.constant else ""

    print("generating trajectories ...")
    Xtr, Ytr = make_dataset(8000, seed=0)
    Xte, Yte = make_dataset(2000, seed=99)

    torch.manual_seed(16)
    model = FieldModel(constant=args.constant)
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)
    rng = np.random.default_rng(0)
    for step in range(STEPS):
        idx = rng.integers(0, len(Xtr), 192)
        pred = model(torch.from_numpy(Xtr[idx]))
        loss = nn.functional.mse_loss(pred, torch.from_numpy(Ytr[idx]))
        opt.zero_grad()
        loss.backward()
        opt.step()
        if step % 100 == 0:
            progress(f"16_field{tag}", step, STEPS, loss=loss.item())
            if step % 1000 == 0:
                print(f"  step {step:5d}  mse {loss.item():.6f}")
    model.eval()
    if not args.constant:
        torch.save(model.net.state_dict(), RESULTS / "16_field_model.pt")

    pred = model(torch.from_numpy(Xte[:1000]))
    e1 = float(nn.functional.mse_loss(pred, torch.from_numpy(Yte[:1000])).item())
    print(f"E1 held-out-IC test MSE: {e1:.2e}")

    out = {"E1_test_mse": e1, "constant": args.constant}
    if not args.constant:
        # E2/E4: field recovery on a probe grid, one GLOBAL scale + affine phi
        gx = np.linspace(XY_RANGE[0] + 0.2, XY_RANGE[1] - 0.2, 25)
        Gx, Gy = np.meshgrid(gx, gx)
        q = torch.from_numpy(np.stack([Gx.ravel(), Gy.ravel()], axis=1).astype(np.float32))
        Bh, Ch, Dh, ph = [t.detach().numpy() for t in model.fields(q)]
        A, B, C, D = fields_2p1(Gx.ravel(), Gy.ravel())
        phi_t = -0.5 * (A - 1)
        scale = float(np.sum(B * Bh + C * Ch) / np.sum(Bh**2 + Ch**2))
        vh = np.stack([scale * Bh, scale * Ch, scale * Dh], axis=1)
        vt = np.stack([B, C, D], axis=1)
        cos = np.sum(vh * vt, axis=1) / (
            np.linalg.norm(vh, axis=1) * np.linalg.norm(vt, axis=1) + 1e-12
        )
        r_phi = float(np.corrcoef(ph, phi_t)[0, 1])
        r_D = float(np.corrcoef(Dh, D)[0, 1])
        print(f"E2 field recovery: median cos = {np.median(cos):.4f}  (gate > 0.99); "
              f"corr(phi_hat, phi) = {r_phi:.4f}")
        print(f"E4 shear recovery: corr(D_hat, D) = {r_D:.4f}")
        out.update({"E2_median_cos": float(np.median(cos)), "E2_phi_corr": r_phi,
                    "E4_D_corr": r_D, "global_scale": scale})

        fig, axes = plt.subplots(1, 3, figsize=(15, 4.6))
        for ax, fld, ttl in ((axes[0], (scale * np.array(Dh)).reshape(Gx.shape),
                              "learned shear D̂ (scaled)"),
                             (axes[1], D.reshape(Gx.shape), "true shear D"),
                             (axes[2], np.array(ph).reshape(Gx.shape), "learned potential φ̂")):
            im = ax.contourf(Gx, Gy, fld, levels=16, cmap="viridis")
            fig.colorbar(im, ax=ax)
            ax.set_title(ttl)
        fig.suptitle("Phase E: the metric field, learned from trajectories alone")
        fig.tight_layout()
        fout = RESULTS / "16_field_from_trajectories.png"
        fig.savefig(fout, dpi=140)
        print(f"plot -> {fout}")

    (RESULTS / f"16_field{tag}.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
