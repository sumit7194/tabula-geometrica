"""Step 36 — Phase G3-causal: is the generalist's world-map editable? (Othello-GPT style)

Find the linear direction in the world-summary w that encodes a world property (matter total
mass), push w along it, and check the model's predictions change as a genuine change in that
property would — beating an equal-norm random-direction control. If so, the internal world
model is causally used, not decorative. Pre-registration 2026-06-15.
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
from importlib import import_module
from sklearn.linear_model import Ridge

gen = import_module("26_generalist")
MATTER = 7
TIMES = np.array([1.0, 2.0, 3.0])


def summaries(model, bank, idx, device="cpu", bs=128):
    ws = []
    with torch.no_grad():
        for i in range(0, len(idx), bs):
            tk = torch.from_numpy(bank["tokens"][idx[i:i + bs]]).to(device)
            ws.append(model.summary(tk).cpu().numpy())
    return np.concatenate(ws)


def predict_from_w(model, w, queries):
    """Run the query head with an arbitrary (possibly steered) summary w."""
    with torch.no_grad():
        qe = model.q_embed(queries)
        B, Q, _ = queries.shape
        wq = torch.from_numpy(w).float()[:, None, :].expand(B, Q, gen.SUMMARY)
        h = model.head(torch.cat([qe, wq], dim=-1))
        return model.out_traj(h).numpy()


def traj_bend(pred, queries):
    """mean |predicted - free motion (x0 + v0 t)| over traj queries (matter: dim=2)."""
    q = queries.numpy()
    x0 = q[..., 6:8]; v0 = q[..., 8:10]           # _q_traj layout: tag 2:6, x0 6:8, v0 8:10
    free = x0[..., None, :] + v0[..., None, :] * TIMES[None, None, :, None]  # (B,Q,3,2)
    p = pred.reshape(*pred.shape[:2], 3, 2)
    is_traj = q[..., 1] > 0.5
    d = np.linalg.norm(p - free, axis=-1).mean(-1)   # (B,Q)
    return float(d[is_traj].mean())


def main():
    bank = dict(np.load(RESULTS / "25_bank.npz"))
    meta = json.loads((RESULTS / "25_bank.meta.json").read_text())
    model = gen.Generalist(); model.load_state_dict(torch.load(RESULTS / "26_generalist_120k.pt", map_location="cpu")); model.eval()

    idx = np.where(bank["family"] == MATTER)[0]
    W = summaries(model, bank, idx)
    mass = np.array([sum(b[2] for b in meta[i]["blobs"]) for i in idx])
    r = float(np.corrcoef(Ridge(1.0).fit(W, mass).predict(W), mass)[0, 1])

    # ON-MANIFOLD direction = high-mass centroid minus low-mass centroid (activation steering)
    lo = mass <= np.quantile(mass, 0.33); hi = mass >= np.quantile(mass, 0.67)
    d = W[hi].mean(0) - W[lo].mean(0)                # natural scale: beta=1 ~ full lo->hi shift
    print(f"mass decode r={r:.3f}; ||diff-of-means dir||={np.linalg.norm(d):.2f}")

    # steer LOW-mass held-out episodes toward high mass; compare to REAL high-mass bend
    rng = np.random.default_rng(0)
    lo_idx = idx[lo]; hi_idx = idx[hi]
    he = lo_idx[rng.permutation(len(lo_idx))[:64]]   # low-mass episodes to edit
    tq = torch.from_numpy(bank["queries"][he]); w0 = summaries(model, bank, he)
    hq = torch.from_numpy(bank["queries"][hi_idx[:64]])
    real_lo = traj_bend(predict_from_w(model, w0, tq), tq)
    real_hi = traj_bend(predict_from_w(model, summaries(model, bank, hi_idx[:64]), hq), hq)
    betas = np.linspace(0, 2, 9)

    def bend_curve(direction):
        return np.array([traj_bend(predict_from_w(model, w0 + b * direction[None, :], tq), tq)
                         for b in betas])

    bend_prop = bend_curve(d)
    rand = np.array([bend_curve((lambda rd: rd / np.linalg.norm(rd) * np.linalg.norm(d))(
        rng.normal(size=d.shape))) for _ in range(5)])

    prop_effect = float(bend_prop[-1] - bend_prop[0])
    rand_effect = float(np.median(np.abs(rand[:, -1] - rand[:, 0])))
    spec = prop_effect / (rand_effect + 1e-9)
    # at beta=1 (full lo->hi edit) does steered bend reach the REAL high-mass bend?
    b1 = float(bend_prop[np.argmin(np.abs(betas - 1.0))])
    reach = (b1 - real_lo) / (real_hi - real_lo + 1e-9)
    print(f"CS1 bend (lo->steered): {bend_prop[0]:.3f} -> {bend_prop[-1]:.3f}; "
          f"real low={real_lo:.3f}, real high={real_hi:.3f}")
    print(f"CS2 specificity: property effect {prop_effect:+.3f} vs random |effect| "
          f"{rand_effect:.3f} -> {spec:.1f}x ({'PASS' if spec >= 3 else 'FAIL'})")
    print(f"CS3 counterfactual: beta=1 reaches {reach*100:.0f}% of the real low->high bend gap "
          f"({'PASS' if reach >= 0.5 else 'FAIL'})")
    cs = bool(spec >= 3 and reach >= 0.5)

    out = {"mass_decode_r": r, "betas": betas.tolist(), "bend_property": bend_prop.tolist(),
           "bend_random_mean": rand.mean(0).tolist(), "real_low": real_lo, "real_high": real_hi,
           "specificity": spec, "counterfactual_reach": reach, "CS_pass": cs}
    (RESULTS / "36_causal.json").write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.plot(betas, bend_prop, "o-", color="crimson", label="mass direction (edit low->high)")
    ax.plot(betas, rand.mean(0), "--", color="gray", label="random dirs (control)")
    ax.axhline(real_lo, color="steelblue", ls=":", label="real low-mass bend")
    ax.axhline(real_hi, color="seagreen", ls=":", label="real high-mass bend")
    ax.set_xlabel("steering beta (0 = low-mass, 1 = full low->high edit)")
    ax.set_ylabel("predicted trajectory bend")
    ax.set_title(f"causal steering: edit the world-map (spec {spec:.0f}x, reach {reach*100:.0f}%)")
    ax.legend(fontsize=8); fig.tight_layout(); fig.savefig(RESULTS / "36_causal.png", dpi=140)
    print(f"saved; CS {'PASS' if cs else 'FAIL'}")


if __name__ == "__main__":
    main()
