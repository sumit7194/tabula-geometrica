"""Step 15 — D-v2: the Lagrangian Kaluza. One learned scalar L(x, w, ẋ, ẇ)
generates ALL motion via Euler–Lagrange; bodies differ only in initial internal
velocity ẇ₀. The Kaluza–Klein statement becomes an autodiff test: the conserved
momentum ∂L/∂ẇ should BE the body's charge. Gates E1-E4 in the lab notebook.
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
from curvlib import RESULTS, TRAJ_TIMES, make_dynamics_dataset, progress
from torch import nn
from torch.func import grad, hessian, vmap

H = 0.1
N_ROLL = int(round(TRAJ_TIMES[-1] / H))
TARGETS = [int(round(t / H)) for t in TRAJ_TIMES]
STEPS = 5000
RIDGE = 1e-3 * torch.eye(2)

# --cyclic: the fix round. The first run showed economy does not select gauge —
# the net used w as a label channel. Imposing the isometry as architecture
# (L never sees w) is a DECLARED bias; what remains discoverable is whether the
# conserved momentum self-organizes into the charge.
CYCLIC = False


class LagrangianKaluza(nn.Module):
    def __init__(self, n_bodies: int):
        super().__init__()
        self.vw0 = nn.Embedding(n_bodies, 1)
        nn.init.normal_(self.vw0.weight, std=0.5)
        self.f = nn.Sequential(
            nn.Linear(3 if CYCLIC else 4, 128), nn.Tanh(),
            nn.Linear(128, 128), nn.Tanh(), nn.Linear(128, 1),
        )
        nn.init.zeros_(self.f[-1].weight)
        nn.init.zeros_(self.f[-1].bias)

    def lagrangian(self, z):  # z: (4,) = (x, w, vx, vw) -> scalar
        feats = torch.stack([z[0], z[2], z[3]]) if CYCLIC else z
        return 0.5 * (z[2] ** 2 + z[3] ** 2) + self.f(feats)[0]

    def accel(self, s):  # s: (B, 4) -> (B, 2) accelerations of (x, w)
        g = vmap(grad(self.lagrangian))(s)
        Hf = vmap(hessian(self.lagrangian))(s)
        Hvv = Hf[:, 2:, 2:] + RIDGE
        rhs = g[:, :2] - (Hf[:, 2:, :2] @ s[:, 2:, None]).squeeze(-1)
        return torch.linalg.solve(Hvv, rhs)

    def rollout(self, x0, v0, vw0, keep_pw=False):
        s = torch.stack([x0, torch.zeros_like(x0), v0, vw0], dim=1)
        xs, pws = [], []
        for step in range(1, N_ROLL + 1):
            def deriv(state):
                a = self.accel(state)
                return torch.cat([state[:, 2:], a], dim=1)

            k1 = deriv(s)
            k2 = deriv(s + 0.5 * H * k1)
            s = s + H * k2
            if step in TARGETS:
                xs.append(s[:, 0])
            if keep_pw:
                pws.append(vmap(grad(self.lagrangian))(s)[:, 3])
        xs = torch.stack(xs, dim=1)
        return (xs, torch.stack(pws, dim=1)) if keep_pw else (xs, None)

    def forward(self, X, body):
        return self.rollout(X[:, 0], X[:, 1], self.vw0(body)[:, 0])[0]


def mse_on(model, split, n=4000):
    body, X, Y = split
    with torch.no_grad():
        pred = model(torch.from_numpy(X[:n]), torch.from_numpy(body[:n]))
        return float(nn.functional.mse_loss(pred, torch.from_numpy(Y[:n])).item())


def main() -> None:
    global CYCLIC
    p = argparse.ArgumentParser()
    p.add_argument("--cyclic", action="store_true")
    args = p.parse_args()
    CYCLIC = args.cyclic
    tag = "_cyclic" if CYCLIC else ""

    data = make_dynamics_dataset("charged", seed=0)
    n_bodies = len(data["qm_body"])
    qm_body = data["qm_body"]
    seen = np.setdiff1d(np.arange(n_bodies), np.array(data["held_bodies"]))

    torch.manual_seed(15)
    model = LagrangianKaluza(n_bodies)
    body, X, Y = data["train"]
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)
    rng = np.random.default_rng(0)
    print("training the Lagrangian Kaluza model:")
    for step in range(STEPS):
        idx = rng.integers(0, len(X), 192)
        pred = model(torch.from_numpy(X[idx]), torch.from_numpy(body[idx]))
        loss = nn.functional.mse_loss(pred, torch.from_numpy(Y[idx]))
        opt.zero_grad()
        loss.backward()
        opt.step()
        if step % 100 == 0:
            progress(f"15_kaluza_lagrangian{tag}", step, STEPS, loss=loss.item())
            if step % 1000 == 0:
                print(f"  step {step:5d}  mse {loss.item():.6f}")
    model.eval()

    e1 = mse_on(model, data["test"])
    print(f"E1 test MSE: {e1:.2e}  (gate <= 1e-4)")

    # E2: the conserved internal momentum vs true charge
    probe_n = 40
    rows = []
    with torch.no_grad():
        for b in seen:
            m = data["test"][0] == b
            Xb = data["test"][1][m][:probe_n]
            if not len(Xb):
                continue
            _, pw = model.rollout(
                torch.from_numpy(Xb[:, 0]), torch.from_numpy(Xb[:, 1]),
                model.vw0(torch.full((len(Xb),), int(b), dtype=torch.long))[:, 0],
                keep_pw=True,
            )
            rows.append((b, float(pw.mean()), float((pw[:, -1] - pw[:, 0]).abs().median())))
    bodies_p = np.array([r[0] for r in rows])
    pw_mean = np.array([r[1] for r in rows])
    pw_drift = np.array([r[2] for r in rows])
    r_kk = float(np.corrcoef(pw_mean, qm_body[bodies_p])[0, 1])
    spread = float(np.std(pw_mean))
    print(f"E2 conserved-momentum identity: corr(p_w, q/m) = {r_kk:+.4f}  (gate |r| > 0.99)")
    print(f"   conservation: median drift {np.median(pw_drift):.4f} vs spread {spread:.4f}")

    # E3: cyclicity — does the learned L ignore w?
    s_probe = torch.from_numpy(
        np.stack([
            rng.uniform(-3, 3, 2000), rng.uniform(-2, 2, 2000),
            rng.uniform(-0.3, 0.3, 2000), rng.uniform(-1.5, 1.5, 2000),
        ], axis=1).astype(np.float32)
    )
    g = vmap(grad(model.lagrangian))(s_probe).detach().numpy()
    cyc = float(np.median(np.abs(g[:, 1])) / np.median(np.abs(g[:, 0])))
    print(f"E3 cyclicity |dL/dw| / |dL/dx| = {cyc:.4f}  (gate < 0.2)")

    # E4: zero-shot — held-out body, fit vw0 from the first target only
    body_h, X_h, Y_h = data["held"]
    vgrid = np.linspace(pw_mean.min() - 1, pw_mean.max() + 1, 121)
    errs = []
    with torch.no_grad():
        for b in np.unique(body_h):
            m = body_h == b
            Xb, Yb = X_h[m][:30], Y_h[m][:30]
            best_v, best_e = None, np.inf
            for v in vgrid:
                xs, _ = model.rollout(
                    torch.from_numpy(Xb[:, 0]), torch.from_numpy(Xb[:, 1]),
                    torch.full((len(Xb),), float(v)),
                )
                e = float(((xs[:, 0].numpy() - Yb[:, 0]) ** 2).mean())
                if e < best_e:
                    best_e, best_v = e, v
            xs, _ = model.rollout(
                torch.from_numpy(Xb[:, 0]), torch.from_numpy(Xb[:, 1]),
                torch.full((len(Xb),), float(best_v)),
            )
            errs.append(((xs[:, 1:].numpy() - Yb[:, 1:]) ** 2).mean())
    e4 = float(np.mean(errs))
    print(f"E4 zero-shot later-target MSE: {e4:.2e}  (in-training: {e1:.2e})")

    fig, ax = plt.subplots(figsize=(7, 5.5))
    ch = np.abs(qm_body[bodies_p]) > 1e-9
    ax.scatter(qm_body[bodies_p][~ch], pw_mean[~ch], c="steelblue", label="neutral")
    ax.scatter(qm_body[bodies_p][ch], pw_mean[ch], c="crimson", label="charged")
    ax.set_xlabel("true q/m")
    ax.set_ylabel("conserved internal momentum  p_w = ∂L/∂ẇ")
    ax.set_title(f"the Kaluza–Klein identity, by autodiff on a learned Lagrangian\n"
                 f"corr = {r_kk:+.4f} · cyclicity {cyc:.3f} · drift/spread "
                 f"{np.median(pw_drift)/max(spread,1e-9):.3f}")
    ax.legend()
    fig.tight_layout()
    out = RESULTS / f"15_kaluza_lagrangian{tag}.png"
    fig.savefig(out, dpi=140)
    print(f"plot -> {out}")

    (RESULTS / f"15_kaluza_lagrangian{tag}.json").write_text(
        json.dumps({"E1_test_mse": e1, "E2_corr": r_kk,
                    "E2_drift_median": float(np.median(pw_drift)), "E2_spread": spread,
                    "E3_cyclicity": cyc, "E4_zero_shot": e4}, indent=1)
    )


if __name__ == "__main__":
    main()
