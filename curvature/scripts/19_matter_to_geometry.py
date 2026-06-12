"""Step 19 — Phase F: THE LAW ITSELF. "Matter tells spacetime how to curve,"
learned as a mapping: random matter configurations → their geometry, supervised
only by trajectories. The killer gate is SUPERPOSITION: trained on 1-2 mass
worlds, the net must predict 3-mass worlds — discovering that gravity is
linear in its source. Pre-registration F1-F4 in the lab notebook (2026-06-13).
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
from curvlib import RESULTS, TRAJ_TIMES, load_ckpt, progress, save_ckpt
from torch import nn

GRID_N, DOM = 48, 3.0
EPS = 0.35
H = 0.1
N_ROLL = int(round(TRAJ_TIMES[-1] / H))
TARGETS = [int(round(t / H)) for t in TRAJ_TIMES]
STEPS = 12000
V_MAX = 0.3


def sample_world(rng, n_blobs):
    c = rng.uniform(-1.8, 1.8, (n_blobs, 2))
    m = rng.uniform(0.3, 1.0, n_blobs)
    return c, m


def true_accel(pts, c, m):
    d = pts[:, None, :] - c[None, :, :]
    r2 = (d**2).sum(-1) + EPS**2
    return -(m[None, :, None] * d / r2[..., None] ** 1.5).sum(1)


def density_grid(c, m):
    g = np.linspace(-DOM, DOM, GRID_N)
    X, Y = np.meshgrid(g, g)  # row = y, col = x
    rho = np.zeros_like(X)
    for (cx, cy), mm in zip(c, m):
        rho += mm * np.exp(-(((X - cx) ** 2) + (Y - cy) ** 2) / (2 * 0.15**2))
    return rho.astype(np.float32)


def integrate_world(x0, v0, c, m, dt=0.01):
    n_steps = int(round(TRAJ_TIMES[-1] / dt))
    grab = {int(round(t / dt)): i for i, t in enumerate(TRAJ_TIMES)}
    q, v = x0.copy(), v0.copy()
    out = np.empty((len(x0), len(TRAJ_TIMES), 2))
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
        x0 = rng.uniform(-2.5, 2.5, (per_world, 2))
        v0 = rng.uniform(-V_MAX, V_MAX, (per_world, 2))
        X.append(np.concatenate([x0, v0], 1))
        Y.append(integrate_world(x0, v0, c, m).reshape(per_world, -1))
        world_id.append(np.full(per_world, w))
    return (np.stack(rho), np.concatenate(X).astype(np.float32),
            np.concatenate(Y).astype(np.float32),
            np.concatenate(world_id).astype(np.int64), configs)


class LawNet(nn.Module):
    """rho grid -> acceleration field; trajectories by differentiable rollout."""

    def __init__(self):
        super().__init__()
        self.cnn = nn.Sequential(
            nn.Conv2d(1, 16, 5, padding=2), nn.Tanh(),
            nn.Conv2d(16, 32, 5, padding=2), nn.Tanh(),
            nn.Conv2d(32, 32, 5, padding=2), nn.Tanh(),
            nn.Conv2d(32, 2, 5, padding=2),
        )

    def field(self, rho):
        return self.cnn(rho[:, None, :, :])

    def rollout(self, field, X):
        from curvlib import bilerp

        q, v = X[:, :2], X[:, 2:]
        use_bilerp = field.device.type == "mps"  # grid_sample bwd missing on MPS
        xs = []
        for step in range(1, N_ROLL + 1):
            def acc(qq):
                if use_bilerp:
                    return bilerp(field, (qq / DOM).clamp(-1, 1))
                # grid_sample: normalized coords, x -> width axis, y -> height
                gridc = (qq / DOM).clamp(-1, 1)[:, None, None, :]
                a = nn.functional.grid_sample(
                    field, gridc, align_corners=True, padding_mode="border")
                return a[:, :, 0, 0]

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
        rg = torch.from_numpy(rho)
        if zero_rho:
            rg = rg * 0
        fields = model.field(rg)
        mses, coss = [], []
        for w in range(len(rho)):
            mask = wid == w
            pred = model.rollout(fields[w:w + 1].expand(int(mask.sum()), -1, -1, -1),
                                 torch.from_numpy(X[mask]))
            mses.append(float(((pred - torch.from_numpy(Y[mask])) ** 2).mean()))
            g = np.linspace(-DOM, DOM, GRID_N)
            GX, GY = np.meshgrid(g, g)
            pts = np.stack([GX.ravel(), GY.ravel()], 1)
            at = true_accel(pts, *configs[w])
            ah = fields[w].numpy().reshape(2, -1).T  # channels (ax, ay)
            norm = np.linalg.norm(at, axis=1)
            sel = norm > np.percentile(norm, 20)
            cos = (ah[sel] * at[sel]).sum(1) / (
                np.linalg.norm(ah[sel], axis=1) * norm[sel] + 1e-12)
            coss.append(float(np.median(cos)))
    return float(np.mean(mses)), float(np.median(coss))


def main() -> None:
    print("generating worlds ...")
    tr = make_dataset(300, 80, (1, 2), seed=0)
    te = make_dataset(40, 80, (1, 2), seed=77)     # F1/F2: unseen configs
    sup = make_dataset(40, 80, (3,), seed=88)      # F3: unseen blob COUNT

    torch.manual_seed(19)
    model = LawNet()
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)
    rho_t = torch.from_numpy(tr[0])
    # power-loss resilience: bit-exact resume (weights + optimizer + RNG state)
    ckpt = RESULTS / "19_ckpt.pt"
    start = 0
    rng = np.random.default_rng(1000)
    if ckpt.exists():
        start, rng, exact = load_ckpt(ckpt, model, opt, fallback_seed=1000)
        print(f"resumed at step {start} "
              f"({'bit-exact' if exact else 'LEGACY ckpt — not bit-exact'})")
    for step in range(start, STEPS):
        idx = rng.integers(0, len(tr[1]), 192)
        w = tr[3][idx]
        pred = model(rho_t[w], torch.from_numpy(tr[1][idx]))
        loss = nn.functional.mse_loss(pred, torch.from_numpy(tr[2][idx]))
        opt.zero_grad()
        loss.backward()
        opt.step()
        if step % 250 == 0:
            progress("19_law", step, STEPS, loss=loss.item())
            if step % 1000 == 0 and step > 0:
                save_ckpt(ckpt, model, opt, step, rng)
            if step % 2000 == 0:
                print(f"  step {step:5d}  mse {loss.item():.6f}")
    model.eval()

    f1, f2 = evaluate(model, *te)
    print(f"F1 held-out-world trajectory MSE: {f1:.2e}  (gate <= 1e-3)")
    print(f"F2 field recovery on unseen worlds: median cos = {f2:.4f}  (gate > 0.98)")
    f1s, f2s = evaluate(model, *sup)
    print(f"F3 SUPERPOSITION (3-blob worlds, never seen): MSE {f1s:.2e} "
          f"(gate <= {2*max(f1,1e-3):.1e}), cos = {f2s:.4f} (gate > 0.96)")
    f1c, _ = evaluate(model, *te, zero_rho=True)
    print(f"F4 matter-blind control: MSE {f1c:.2e}  (gate >= 10x F1)")

    (RESULTS / "19_law.json").write_text(json.dumps(
        {"F1_mse": f1, "F2_cos": f2, "F3_mse": f1s, "F3_cos": f2s, "F4_blind": f1c},
        indent=1))

    w = 0
    g = np.linspace(-DOM, DOM, GRID_N)
    GX, GY = np.meshgrid(g, g)
    pts = np.stack([GX.ravel(), GY.ravel()], 1)
    at = true_accel(pts, *sup[4][w]).reshape(GRID_N, GRID_N, 2)
    with torch.no_grad():
        ah = model.field(torch.from_numpy(sup[0][w:w + 1]))[0].numpy()
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 5.6))
    for ax, f, ttl in ((axes[0], np.transpose(ah, (1, 2, 0)),
                        "LEARNED field (3 masses — a count never trained on)"),
                       (axes[1], at, "true field")):
        sp = max(1, GRID_N // 24)
        ax.quiver(GX[::sp, ::sp], GY[::sp, ::sp],
                  f[::sp, ::sp, 0], f[::sp, ::sp, 1], scale=18)
        for (cx, cy), mm in zip(*sup[4][w]):
            ax.scatter([cx], [cy], s=300 * mm, c="crimson", alpha=0.6)
        ax.set_title(ttl)
    fig.suptitle(f"Phase F: the law itself — superposition discovered "
                 f"(3-blob cos = {f2s:.3f})")
    fig.tight_layout()
    fig.savefig(RESULTS / "19_matter_to_geometry.png", dpi=140)
    print(f"plot -> {RESULTS / '19_matter_to_geometry.png'}")


if __name__ == "__main__":
    main()
