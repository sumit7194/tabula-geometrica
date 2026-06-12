"""Step 21 — Option A: Matter Curves Spacetime in 3+1 Dimensions.

Rediscovering the gravitational superposition law in a 3D spatial world.
Supervised only by 3D trajectories, the CNN (using nn.Conv3d) must map
a 3D density grid to a 3D vector acceleration field, discovering that gravity
is linear in its source.
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
from curvlib import RESULTS, TRAJ_TIMES, progress
from torch import nn

GRID_N, DOM = 24, 3.0  # 24^3 = 13,824 voxels, lightweight and fast on CPU
EPS = 0.35
H = 0.1
N_ROLL = int(round(TRAJ_TIMES[-1] / H))
TARGETS = [int(round(t / H)) for t in TRAJ_TIMES]
STEPS = 8000
V_MAX = 0.3
DEVICE = torch.device("cpu")  # overridden by --device; cpu keeps the run identical


def trilerp(field, grid):
    """3D trilinear sample, a drop-in for
    F.grid_sample(field, grid, mode='bilinear', align_corners=True, padding_mode='border').
    Hand-rolled from gather + arithmetic so the BACKWARD runs on MPS, where
    aten::grid_sampler_3d_backward is unimplemented (pytorch#141287). field: (N,C,D,H,W);
    grid: (N,*out,3) normalized [-1,1], last dim (gx,gy,gz) addressing (W,H,D). -> (N,C,*out).
    """
    N, C, D, Hh, Ww = field.shape
    out_shape = grid.shape[1:-1]
    g = grid.reshape(N, -1, 3)
    Q = g.shape[1]
    # align_corners=True un-normalization; gx->W, gy->H, gz->D
    fx = (g[..., 0] + 1) * 0.5 * (Ww - 1)
    fy = (g[..., 1] + 1) * 0.5 * (Hh - 1)
    fz = (g[..., 2] + 1) * 0.5 * (D - 1)
    x0f, y0f, z0f = torch.floor(fx), torch.floor(fy), torch.floor(fz)
    wx1, wy1, wz1 = fx - x0f, fy - y0f, fz - z0f      # weights from UNclamped coord (border)
    wx0, wy0, wz0 = 1 - wx1, 1 - wy1, 1 - wz1
    x0, x1 = x0f.clamp(0, Ww - 1).long(), (x0f + 1).clamp(0, Ww - 1).long()
    y0, y1 = y0f.clamp(0, Hh - 1).long(), (y0f + 1).clamp(0, Hh - 1).long()
    z0, z1 = z0f.clamp(0, D - 1).long(), (z0f + 1).clamp(0, D - 1).long()
    flat = field.reshape(N, C, D * Hh * Ww)

    def gather(zz, yy, xx):
        idx = (zz * Hh * Ww + yy * Ww + xx)[:, None, :].expand(N, C, Q)
        return torch.gather(flat, 2, idx)

    out = (gather(z0, y0, x0) * (wz0 * wy0 * wx0)[:, None, :]
           + gather(z0, y0, x1) * (wz0 * wy0 * wx1)[:, None, :]
           + gather(z0, y1, x0) * (wz0 * wy1 * wx0)[:, None, :]
           + gather(z0, y1, x1) * (wz0 * wy1 * wx1)[:, None, :]
           + gather(z1, y0, x0) * (wz1 * wy0 * wx0)[:, None, :]
           + gather(z1, y0, x1) * (wz1 * wy0 * wx1)[:, None, :]
           + gather(z1, y1, x0) * (wz1 * wy1 * wx0)[:, None, :]
           + gather(z1, y1, x1) * (wz1 * wy1 * wx1)[:, None, :])
    return out.reshape(N, C, *out_shape)


def sample_world(rng, n_blobs):
    c = rng.uniform(-1.8, 1.8, (n_blobs, 3))
    m = rng.uniform(0.3, 1.0, n_blobs)
    return c, m


def true_accel(pts, c, m):
    # pts: (N_pts, 3), c: (n_blobs, 3), m: (n_blobs,)
    d = pts[:, None, :] - c[None, :, :]  # (N_pts, n_blobs, 3)
    r2 = (d**2).sum(-1) + EPS**2         # (N_pts, n_blobs)
    return -(m[None, :, None] * d / r2[..., None] ** 1.5).sum(1)  # (N_pts, 3)


def density_grid(c, m):
    g = np.linspace(-DOM, DOM, GRID_N)
    X, Y, Z = np.meshgrid(g, g, g, indexing='ij')  # shape: (GRID_N, GRID_N, GRID_N)
    rho = np.zeros_like(X)
    for (cx, cy, cz), mm in zip(c, m):
        rho += mm * np.exp(-(((X - cx) ** 2) + (Y - cy) ** 2 + (Z - cz) ** 2) / (2 * 0.15**2))
    return rho.astype(np.float32)


def integrate_world(x0, v0, c, m, dt=0.01):
    n_steps = int(round(TRAJ_TIMES[-1] / dt))
    grab = {int(round(t / dt)): i for i, t in enumerate(TRAJ_TIMES)}
    q, v = x0.copy(), v0.copy()
    out = np.empty((len(x0), len(TRAJ_TIMES), 3))
    for step in range(1, n_steps + 1):
        k1q, k1v = v, true_accel(q, c, m)
        k2q, k2v = v + 0.5 * dt * k1v, true_accel(q + 0.5 * dt * k1q, c, m)
        k3q, k3v = v + 0.5 * dt * k2v, true_accel(q + 0.5 * dt * k2q, c, m)
        k4q, k4v = v + dt * k3v, true_accel(q + dt * k3q, c, m)
        q = q + dt / 6 * (k1q + 2 * k2q + 2 * k3q + k4q)
        v = v + dt / 6 * (k1v + 2 * k2v + 2 * k3v + k4v)
        if step in grab:
            out[:, grab[step]] = q
    return out


def make_dataset(n_worlds, per_world, blob_choices, seed):
    rng = np.random.default_rng(seed)
    rho, X, Y, world_id, configs = [], [], [], [], []
    for w in range(n_worlds):
        c, m = sample_world(rng, int(rng.choice(blob_choices)))
        configs.append((c, m))
        rho.append(density_grid(c, m))
        x0 = rng.uniform(-2.5, 2.5, (per_world, 3))
        v0 = rng.uniform(-V_MAX, V_MAX, (per_world, 3))
        X.append(np.concatenate([x0, v0], 1))
        Y.append(integrate_world(x0, v0, c, m).reshape(per_world, -1))
        world_id.append(np.full(per_world, w))
    return (np.stack(rho), np.concatenate(X).astype(np.float32),
            np.concatenate(Y).astype(np.float32),
            np.concatenate(world_id).astype(np.int64), configs)


class LawNet3D(nn.Module):
    """rho 3D grid -> 3D acceleration field; trajectories by differentiable rollout."""

    def __init__(self):
        super().__init__()
        # 3D CNN setup
        self.cnn = nn.Sequential(
            nn.Conv3d(1, 8, 3, padding=1), nn.Tanh(),
            nn.Conv3d(8, 16, 3, padding=1), nn.Tanh(),
            nn.Conv3d(16, 16, 3, padding=1), nn.Tanh(),
            nn.Conv3d(16, 3, 3, padding=1),  # output: ax, ay, az channels
        )

    def field(self, rho):
        return self.cnn(rho[:, None, :, :, :])

    def rollout(self, field, X):
        q, v = X[:, :3], X[:, 3:]
        xs = []
        for step in range(1, N_ROLL + 1):
            def acc(qq):
                # PyTorch grid_sample 3D expects coordinates in (x, y, z) order,
                # where grid[..., 0]=width, grid[..., 1]=height, grid[..., 2]=depth.
                # Since indexing='ij' meshgrid stores X as depth, Y as height, Z as width,
                # we must reverse qq coordinates to (qz, qy, qx) to sample correctly.
                qq_rev = torch.stack([qq[:, 2], qq[:, 1], qq[:, 0]], dim=-1)
                gridc = (qq_rev / DOM).clamp(-1, 1)[:, None, None, None, :]
                a = trilerp(field, gridc)
                return a[:, :, 0, 0, 0]

            a1 = acc(q)
            qm, vm = q + 0.5 * H * v, v + 0.5 * H * a1
            q = q + H * vm
            v = v + H * acc(qm)
            if step in TARGETS:
                xs.append(q)
        return torch.cat(xs, dim=1)

    def forward(self, rho, X):
        return self.rollout(self.field(rho), X)


def evaluate(model, rho, X, Y, wid, configs, zero_rho=False):
    with torch.no_grad():
        rg = torch.from_numpy(rho).to(DEVICE)
        if zero_rho:
            rg = rg * 0
        fields = model.field(rg)
        mses, coss = [], []
        for w in range(len(rho)):
            mask = wid == w
            pred = model.rollout(fields[w:w + 1].expand(int(mask.sum()), -1, -1, -1, -1),
                                 torch.from_numpy(X[mask]).to(DEVICE))
            mses.append(float(((pred - torch.from_numpy(Y[mask]).to(DEVICE)) ** 2).mean()))

            # evaluate field alignment in 3D grid
            g = np.linspace(-DOM, DOM, GRID_N)
            GX, GY, GZ = np.meshgrid(g, g, g, indexing='ij')
            pts = np.stack([GX.ravel(), GY.ravel(), GZ.ravel()], 1)
            at = true_accel(pts, *configs[w])

            # Reshape CNN output: channels (ax, ay, az) -> (N_pts, 3)
            ah = fields[w].cpu().numpy().reshape(3, -1).T
            norm = np.linalg.norm(at, axis=1)
            sel = norm > np.percentile(norm, 20)
            cos = (ah[sel] * at[sel]).sum(1) / (
                np.linalg.norm(ah[sel], axis=1) * norm[sel] + 1e-12)
            coss.append(float(np.median(cos)))
    return float(np.mean(mses)), float(np.median(coss))


def main() -> None:
    global DEVICE
    parser = argparse.ArgumentParser()
    parser.add_argument("--device", default="cpu", choices=["cpu", "mps", "cuda"])
    DEVICE = torch.device(parser.parse_args().device)
    print(f"device: {DEVICE}")

    print("generating 3D worlds ...")
    tr = make_dataset(300, 80, (1, 2), seed=0)
    te = make_dataset(40, 80, (1, 2), seed=77)     # held-out 1-2 blob configurations
    sup = make_dataset(40, 80, (3,), seed=88)      # 3-blob worlds (unseen blob count)

    torch.manual_seed(21)
    model = LawNet3D().to(DEVICE)
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)
    rho_t = torch.from_numpy(tr[0]).to(DEVICE)

    ckpt = RESULTS / "21_ckpt.pt"
    start = 0
    if ckpt.exists():
        st = torch.load(ckpt, map_location=DEVICE, weights_only=False)
        model.load_state_dict(st["model"])
        opt.load_state_dict(st["opt"])
        start = st["step"]
        print(f"resumed from checkpoint at step {start}")

    rng = np.random.default_rng(2100 + start)
    for step in range(start, STEPS):
        idx = rng.integers(0, len(tr[1]), 48)
        w = tr[3][idx]
        pred = model(rho_t[w], torch.from_numpy(tr[1][idx]).to(DEVICE))
        loss = nn.functional.mse_loss(pred, torch.from_numpy(tr[2][idx]).to(DEVICE))
        opt.zero_grad()
        loss.backward()
        opt.step()
        
        if step % 250 == 0:
            progress("21_law_3p1", step, STEPS, loss=loss.item())
            if step % 1000 == 0 and step > 0:
                torch.save({"model": model.state_dict(),
                            "opt": opt.state_dict(), "step": step}, ckpt)
            if step % 2000 == 0:
                print(f"  step {step:5d}  mse {loss.item():.6f}")
                
    model.eval()

    f1, f2 = evaluate(model, *te)
    print(f"F1 3D held-out trajectory MSE: {f1:.2e}  (gate <= 1e-3)")
    print(f"F2 3D field recovery: median cos = {f2:.4f}  (gate > 0.98)")
    f1s, f2s = evaluate(model, *sup)
    print(f"F3 3D SUPERPOSITION (3-blob worlds): MSE {f1s:.2e} "
          f"(gate <= {2*max(f1,1e-3):.1e}), cos = {f2s:.4f} (gate > 0.96)")
    f1c, _ = evaluate(model, *te, zero_rho=True)
    print(f"F4 3D matter-blind control: MSE {f1c:.2e}  (gate >= 10x F1)")

    (RESULTS / "21_law_3p1.json").write_text(json.dumps(
        {"F1_mse": f1, "F2_cos": f2, "F3_mse": f1s, "F3_cos": f2s, "F4_blind": f1c},
        indent=1))

    # Save a 2D slice visualization at z = 0
    w = 0
    g = np.linspace(-DOM, DOM, 24)
    GX, GY = np.meshgrid(g, g, indexing='ij')
    pts_slice = np.stack([GX.ravel(), GY.ravel(), np.zeros_like(GX).ravel()], 1)
    
    # True acceleration field in slice
    at = true_accel(pts_slice, *sup[4][w]).reshape(24, 24, 3)
    
    # Learned field sampled via grid_sample at slice coordinates
    pts_t = torch.from_numpy(pts_slice).float()
    gridc = torch.stack([pts_t[:, 2], pts_t[:, 1], pts_t[:, 0]], dim=-1).clamp(-DOM, DOM) / DOM
    gridc = gridc[None, None, None, :, :]
    with torch.no_grad():
        fields = model.field(torch.from_numpy(sup[0][w:w + 1]).to(DEVICE))
        ah_sample = trilerp(fields, gridc.to(DEVICE))
        ah = ah_sample[0, :, 0, 0, :].cpu().numpy().T.reshape(24, 24, 3)
        
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 5.6))
    for ax, f, ttl in ((axes[0], ah, "LEARNED 3D field slice (z=0, 3 masses)"),
                       (axes[1], at, "true 3D field slice (z=0)")):
        # Plot quiver arrows in the xy plane (components 0 and 1)
        ax.quiver(GX, GY, f[..., 0], f[..., 1], scale=18)
        
        # Plot masses projected onto the slice plane
        for (cx, cy, cz), mm in zip(*sup[4][w]):
            # Highlight proximity to the slice z=0 by transparency
            alpha = max(0.1, 1.0 - abs(cz) / DOM)
            ax.scatter([cx], [cy], s=300 * mm, c="crimson", alpha=alpha * 0.7)
        ax.set_title(ttl)
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        
    fig.suptitle(f"3+1D Gravity Law: Superposition Slice (3-blob cos = {f2s:.3f})")
    fig.tight_layout()
    fig.savefig(RESULTS / "21_matter_to_geometry_3p1.png", dpi=140)
    print(f"3D slice plot -> {RESULTS / '21_matter_to_geometry_3p1.png'}")


if __name__ == "__main__":
    main()
