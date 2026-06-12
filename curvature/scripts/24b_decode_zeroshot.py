"""Step 24b — Phase H row 1 gates H3 + H4.

H3 behavioral decode: for each trained body, find the (qm1, qm2) whose TRUE
generator trajectories best match the lane model's rollouts (grid argmin) —
the lanes are read out by what the body DOES, not by probing weights. Gate:
joint decode r > 0.99 per label after one linear mixing (gauge allowed).
H4 zero-shot: held-out body (embedding never trained) — fit its two lane
coordinates from ONE observed trajectory, frozen net; measure prediction MSE
on its remaining trajectories + decode the fitted lanes.
Pre-registration in the lab notebook (2026-06-14).
"""

import importlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import torch
from curvlib import RESULTS, V_MAX, X_RANGE

mod = importlib.import_module("24_two_charge_lanes")

N_PROBE = 64
GRID = np.linspace(-1.3, 1.3, 61)


def main() -> None:
    data = mod.make_dataset()
    qm, held = data["qm"], data["held_bodies"]
    n_bodies = len(qm)
    model = mod.LaneModel(n_bodies, 2)
    model.load_state_dict(torch.load(RESULTS / "24_model_L2.pt", map_location="cpu"))
    model.eval()

    rng = np.random.default_rng(7)
    x0 = rng.uniform(*X_RANGE, N_PROBE)
    v0 = rng.uniform(-V_MAX, V_MAX, N_PROBE)
    X = np.stack([x0, v0], 1).astype(np.float32)
    Xt = torch.from_numpy(X)

    # generator bank: true trajectories for every (qm1, qm2) grid point
    Q1, Q2 = np.meshgrid(GRID, GRID, indexing="ij")
    g1, g2 = Q1.ravel(), Q2.ravel()
    G = len(g1)
    print(f"building generator bank: {G} grid points x {N_PROBE} probes")
    bank = mod.integrate(np.tile(x0, G), np.tile(v0, G),
                         np.repeat(g1, N_PROBE), np.repeat(g2, N_PROBE))
    bank = bank.reshape(G, N_PROBE, 3)

    def decode(roll):
        """argmin over the grid of mean traj MSE -> effective (qm1, qm2)."""
        mse = ((bank - roll[None]) ** 2).mean(axis=(1, 2))
        j = int(mse.argmin())
        return g1[j], g2[j], float(mse[j])

    # ---- H3: decode every TRAINED body from behavior ----
    seen = [i for i in range(n_bodies) if i not in held]
    dec = np.zeros((len(seen), 2))
    with torch.no_grad():
        for k, i in enumerate(seen):
            roll = model(Xt, torch.full((N_PROBE,), i)).numpy()
            dec[k, 0], dec[k, 1], _ = decode(roll)
    true = qm[seen]
    # one linear mixing allowed (lanes may rotate; this is the gauge freedom)
    A = np.hstack([dec, np.ones((len(seen), 1))])
    mix, *_ = np.linalg.lstsq(A, true, rcond=None)
    mixed = A @ mix
    r_raw = [float(np.corrcoef(dec[:, j], true[:, j])[0, 1]) for j in range(2)]
    r_mix = [float(np.corrcoef(mixed[:, j], true[:, j])[0, 1]) for j in range(2)]
    print(f"H3 raw decode r: qm1 {r_raw[0]:.4f}  qm2 {r_raw[1]:.4f}")
    print(f"H3 after linear mixing r: qm1 {r_mix[0]:.4f}  qm2 {r_mix[1]:.4f}"
          f"  -> gate r>0.99 {'PASS' if min(r_mix) > 0.99 else 'FAIL'}")

    # ---- H4: held-out bodies, lanes fitted from ONE trajectory ----
    hb, hX, hY = data["held"]
    h4 = []
    for i in held:
        rows = np.where(hb == i)[0]
        one, rest = rows[0], rows[1:]
        x1 = torch.from_numpy(hX[one:one + 1])
        y1 = torch.from_numpy(hY[one:one + 1])
        best = None
        for init in ([0.0, 0.0], [0.5, -0.5], [-0.5, 0.5]):
            w = torch.tensor([init], dtype=torch.float32, requires_grad=True)
            opt = torch.optim.Adam([w], lr=0.05)
            for _ in range(400):
                loss = torch.nn.functional.mse_loss(model.rollout(x1, w), y1)
                opt.zero_grad()
                loss.backward()
                opt.step()
            if best is None or float(loss) < best[0]:
                best = (float(loss), w.detach())
        w_fit = best[1]
        with torch.no_grad():
            roll = model.rollout(torch.from_numpy(hX[rest]),
                                 w_fit.expand(len(rest), 2)).numpy()
            mse_rest = float(((roll - hY[rest]) ** 2).mean())
            roll_probe = model.rollout(Xt, w_fit.expand(N_PROBE, 2)).numpy()
        d1, d2, _ = decode(roll_probe)
        h4.append({"body": int(i), "true_qm": qm[i].tolist(),
                   "decoded_qm": [d1, d2], "one_pt_loss": best[0],
                   "mse_rest": mse_rest})
        print(f"H4 body {i}: true ({qm[i,0]:+.2f},{qm[i,1]:+.2f}) "
              f"decoded ({d1:+.2f},{d2:+.2f})  mse_rest {mse_rest:.2e}")

    h4_dec = np.array([r["decoded_qm"] for r in h4])
    h4_true = np.array([r["true_qm"] for r in h4])
    Ah = np.hstack([h4_dec, np.ones((len(h4), 1))])
    h4_mixed = Ah @ mix  # SAME mixing as H3 (fit on seen bodies only)
    r_h4 = [float(np.corrcoef(h4_mixed[:, j], h4_true[:, j])[0, 1]) for j in range(2)]
    med_mse = float(np.median([r["mse_rest"] for r in h4]))
    print(f"H4 decode r (seen-body mixing): qm1 {r_h4[0]:.4f}  qm2 {r_h4[1]:.4f}; "
          f"median mse_rest {med_mse:.2e} (seen-body test was 1.2e-4)")

    out = {"r_raw": r_raw, "r_mix": r_mix, "mix": mix.tolist(),
           "h3_pass": bool(min(r_mix) > 0.99),
           "h4": h4, "h4_r_mixed": r_h4, "h4_median_mse": med_mse}
    (RESULTS / "24b_decode.json").write_text(json.dumps(out, indent=1))

    fig, axes = plt.subplots(1, 2, figsize=(11, 5))
    for j, ax in enumerate(axes):
        ax.scatter(true[:, j], mixed[:, j], c="darkslategray", label="trained bodies")
        ax.scatter(h4_true[:, j], h4_mixed[:, j], c="crimson", marker="s",
                   label="held-out (1-pt fit)")
        lim = [-1.3, 1.3]
        ax.plot(lim, lim, "k--", lw=0.8)
        ax.set_xlabel(f"true qm{j+1}")
        ax.set_ylabel(f"behavioral decode (after mixing)")
        ax.set_title(f"label {j+1}: r={r_mix[j]:.4f}")
        ax.legend()
    fig.suptitle("two-charge lanes: behavioral decode of BOTH labels")
    fig.tight_layout()
    fig.savefig(RESULTS / "24b_decode.png", dpi=140)
    print(f"saved results/24b_decode.json + .png")


if __name__ == "__main__":
    main()
