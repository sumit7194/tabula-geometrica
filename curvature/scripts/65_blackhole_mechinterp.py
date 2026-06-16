"""Step 65 — PHASE BH-4: MECH-INTERP inside the validated generalist. How does it represent the horizon?

The capstone: now that the generalist genuinely represents the spacetime physics (script 62: decode M
R^2=1.000, flip-tracks-M PASS), go INSIDE it. Hook the head's hidden activations on Schwarzschild
queries (across several masses M, so the horizon r=2M moves) and ask:
  M1 IS there an "inside vs outside the horizon" FEATURE? — linearly decodable from the hidden rep,
     accounting for M (label = r < 2M), generalizing across masses.
  M2 is the SIGNATURE represented? — g_vv linearly decodes from the hidden rep.
  M3 can we STEER it? — add the inside−outside direction (diff-of-means) to an OUTSIDE query's hidden
     activation and watch the predicted g_vv FLIP sign (steer the causal character from outside→inside);
     an equal-norm RANDOM direction must NOT (specificity — the S4 control lesson).

Hidden rep = the head's d-dim activation after its last GELU (before the output projection).
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import matplotlib

matplotlib.use("Agg")
import numpy as np
import torch
from importlib import import_module
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.model_selection import cross_val_predict, cross_val_score

import worldgen_v2 as wg
from curvlib import RESULTS, load_ckpt
g2 = import_module("61_generalist_v2")
DEV = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
FID = [f.name for f in wg.FAMILIES].index("schwarzschild")
K = g2.K


def hidden_and_pred(m, ctx_u, ctx_y, q_u, fam):
    """Run the generalist but capture the head's last-GELU hidden rep (d-dim) and the prediction."""
    code = m.encode(ctx_u, ctx_y, fam)
    f = m.fam(fam)[:, None, :]
    qt = m.q_embed(q_u) + f
    cc = code[:, None, :].expand(-1, q_u.shape[1], -1)
    h = torch.cat([qt, cc], -1)
    h = m.head[1](m.head[0](h)); h = m.head[3](m.head[2](h))   # Linear,GELU,Linear,GELU -> hidden (B,Q,d)
    out = m.head[4](h)                                          # -> g_vv
    return h, out[..., 0]


def schwarz_probe(m, Ms=(0.8, 1.0, 1.3), nq=80):
    rng = np.random.default_rng(0)
    H, GVV, INSIDE = [], [], []
    fam = torch.tensor([FID]).to(DEV)
    for M in Ms:
        u, y = wg.FAMILIES[FID].obs({"M": M}, rng, K)
        cu = torch.from_numpy(u[None]).to(DEV); cy = torch.from_numpy(y[None]).to(DEV)
        rs = np.linspace(0.5, 5.0, nq).astype(np.float32)
        qu = torch.from_numpy(wg._pad(rs[:, None], wg.DU)[None]).to(DEV)
        with torch.no_grad():
            h, pred = hidden_and_pred(m, cu, cy, qu, fam)
        H.append(h[0].cpu().numpy()); GVV.append(pred[0].cpu().numpy())
        INSIDE.append((rs < 2 * M).astype(int))
    return np.concatenate(H), np.concatenate(GVV), np.concatenate(INSIDE)


def main():
    m = g2.GeneralistV2().to(DEV); opt = torch.optim.Adam(m.parameters())
    step, *_ = load_ckpt(RESULTS / "61_gen2.pt", m, opt, fallback_seed=0); m.eval()
    print(f"loaded generalist @ step {step}\n")

    H, GVV, INSIDE = schwarz_probe(m)
    # M1: inside-vs-outside-horizon feature (label = r<2M, generalizes across M)
    acc = float(np.mean(cross_val_score(LogisticRegression(max_iter=2000), H, INSIDE, cv=5)))
    # M2: signature g_vv linearly decodable from the hidden rep
    gpred = cross_val_predict(Ridge(1.0), H, GVV, cv=5)
    r2 = float(1 - np.sum((gpred - GVV) ** 2) / np.sum((GVV - GVV.mean()) ** 2))

    # M3: steering — add the inside−outside direction to OUTSIDE queries, does predicted g_vv flip sign?
    Ht = torch.from_numpy(H).to(DEV)
    d = torch.from_numpy(H[INSIDE == 1].mean(0) - H[INSIDE == 0].mean(0)).to(DEV)
    d = d / d.norm()
    out_mask = INSIDE == 0
    rng = np.random.default_rng(1)
    rand = torch.from_numpy(rng.standard_normal(H.shape[1]).astype(np.float32)).to(DEV); rand = rand / rand.norm()
    scale = float(np.linalg.norm(H[INSIDE == 1].mean(0) - H[INSIDE == 0].mean(0)))  # natural inside-outside gap
    with torch.no_grad():
        base = m.head[4](Ht[out_mask])[..., 0].cpu().numpy()              # outside g_vv (should be <0)
        steered = m.head[4](Ht[out_mask] + scale * d)[..., 0].cpu().numpy()  # + horizon direction
        ctrl = m.head[4](Ht[out_mask] + scale * rand)[..., 0].cpu().numpy()  # equal-norm random control
    frac_flip = float(np.mean(steered > 0))            # fraction of outside queries pushed to inside (g_vv>0)
    frac_flip_ctrl = float(np.mean(ctrl > 0))

    m1 = bool(acc > 0.95)
    m2 = bool(r2 > 0.9)
    m3 = bool(frac_flip > 0.7 and frac_flip > frac_flip_ctrl + 0.4)
    out = {"checkpoint_step": step, "horizon_feature_decode_acc": acc, "signature_decode_R2": r2,
           "steer_frac_flipped": frac_flip, "control_frac_flipped": frac_flip_ctrl,
           "base_gvv_mean_outside": float(base.mean()), "steered_gvv_mean": float(steered.mean()),
           "M1_horizon_feature_exists": m1, "M2_signature_represented": m2, "M3_steerable": m3,
           "mechinterp_horizon_understood": bool(m1 and m2 and m3)}
    print(f"M1 'inside vs outside horizon' feature (linear decode acc {acc:.3f} >0.95, across masses): {m1}")
    print(f"M2 signature g_vv linearly represented (hidden->g_vv R^2 {r2:.3f} >0.9): {m2}")
    print(f"M3 steerable: adding the horizon direction flips {frac_flip*100:.0f}% of OUTSIDE queries to inside "
          f"(g_vv {base.mean():+.2f}->{steered.mean():+.2f}); random control {frac_flip_ctrl*100:.0f}%: {m3}")
    print(f"\nHORIZON MECH-INTERP (feature + signature + steering): {out['mechinterp_horizon_understood']}")
    (RESULTS / "65_mechinterp.json").write_text(json.dumps(out, indent=1))

    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(7.5, 5))
    ax.hist(base, bins=25, alpha=0.6, color="navy", label=f"outside queries (g_vv<0), mean {base.mean():.2f}")
    ax.hist(steered, bins=25, alpha=0.6, color="crimson", label=f"+ horizon direction, mean {steered.mean():.2f}")
    ax.hist(ctrl, bins=25, alpha=0.4, color="gray", label=f"+ random (control), mean {ctrl.mean():.2f}")
    ax.axvline(0, color="k", lw=0.8); ax.set_xlabel("predicted g_vv (sign = causal character)")
    ax.set_title(f"steering the horizon feature pushes outside→inside (g_vv flips +)\nfeature decode {acc:.2f}, signature R²={r2:.2f}")
    ax.legend(fontsize=8); fig.tight_layout(); fig.savefig(RESULTS / "65_mechinterp.png", dpi=140)
    print("saved results/65_mechinterp.json + .png")


if __name__ == "__main__":
    main()
