"""Step 56 — EXOTIC: dark matter vs modified gravity, as a SHAREABILITY/economy problem.

Expanding past black holes (user push): point our economy machinery at the real DM-vs-MOND debate.
Flat galaxy rotation curves can be explained two ways (web-verified):
  MOND (modified gravity): one UNIVERSAL modified law, g = (g_N + sqrt(g_N^2 + 4 g_N a0))/2 — a SHARED
       law, no extra matter. [the geometry / identity-blind side]
  Dark matter: Newtonian gravity + a PER-GALAXY hidden halo sourcing extra g. [the per-instance / free-code side]
This is exactly tonight's shared-vs-per-instance axis. The deciding knob (the real argument!) is
whether the anomaly is UNIVERSAL (one a0 everywhere -> MOND parsimonious & predictive) or PER-SYSTEM
(each galaxy its own halo -> dark matter).

Setup: many "galaxies" with different visible central mass M_i; the TRUE world is MOND with a0_i. Two
models fit the observed acceleration a(r):
  MOND-model:  a = f_shared(g_N)  — one shared function of the Newtonian acceleration (identity-blind
               across galaxies; CAN zero-shot a new galaxy because the law is universal).
  DM-model:    a = g_N + halo(r; emb_i) — Newtonian + a per-galaxy halo profile (CANNOT zero-shot).
Sweep the spread of a0_i across galaxies (universality knob).

Pre-reg (2026-06-17):
  D1 universal -> MOND wins/predicts: at spread=0, MOND held-out (zero-shot) nMSE < 0.1, and < 0.2 x
     DM held-out (DM can't zero-shot a new galaxy). A universal modified law predicts new galaxies; dark
     matter doesn't -> the net "discovers MOND" (no dark matter needed).
  D2 per-system -> DM needed: MOND in-sample nMSE rises with spread (a shared law stops fitting),
     max/min > 5, while DM in-sample stays low -> the anomaly is genuinely per-galaxy = dark matter.
  D3 MOND recovers the law: at spread=0, MOND predicted-vs-true on held-out R^2 > 0.99.
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

N_GAL, N_PTS, STEPS, HELD = 40, 300, 6000, 8
A0 = 0.5
SPREADS = [0.0, 0.5, 1.0, 2.0]


def mond_g(gN, a0):
    return (gN + np.sqrt(gN ** 2 + 4 * gN * a0)) / 2


def make_data(spread, seed=0):
    rng = np.random.default_rng(seed)
    M = rng.uniform(0.5, 2.0, N_GAL).astype(np.float32)
    a0 = (A0 * (1 + spread * rng.uniform(-0.5, 0.5, N_GAL))).astype(np.float32)
    gN, atrue, r_, gal = [], [], [], []
    for i in range(N_GAL):
        r = rng.uniform(0.5, 5.0, N_PTS).astype(np.float32)
        g = (M[i] / r ** 2).astype(np.float32)
        gN.append(g); atrue.append(mond_g(g, a0[i]).astype(np.float32)); r_.append(r); gal.append(np.full(N_PTS, i))
    return {"M": M, "a0": a0,
            "gN": np.concatenate(gN), "a": np.concatenate(atrue),
            "r": np.concatenate(r_), "gal": np.concatenate(gal).astype(np.int64)}


class MOND(nn.Module):                                   # shared universal law a = f(g_N)
    def __init__(s):
        super().__init__(); s.net = nn.Sequential(nn.Linear(1, 64), nn.GELU(), nn.Linear(64, 64), nn.GELU(), nn.Linear(64, 1))
    def forward(s, gN, gal=None):
        return s.net(gN[:, None])[:, 0]


class DM(nn.Module):                                     # Newtonian + per-galaxy halo a = g_N + halo(r; emb)
    def __init__(s, n):
        super().__init__(); s.emb = nn.Embedding(n, 4)
        s.halo = nn.Sequential(nn.Linear(1 + 4, 64), nn.GELU(), nn.Linear(64, 64), nn.GELU(), nn.Linear(64, 1))
    def forward(s, gN, r, gal):
        h = s.halo(torch.cat([r[:, None], s.emb(gal)], -1))[:, 0]
        return gN + h


def train(kind, d, seed=0):
    torch.manual_seed(seed); rng = np.random.default_rng(seed)
    gN = torch.from_numpy(d["gN"]); a = torch.from_numpy(d["a"]); r = torch.from_numpy(d["r"]); gal = torch.from_numpy(d["gal"])
    tr = np.where(d["gal"] < N_GAL - HELD)[0]
    m = MOND() if kind == "mond" else DM(N_GAL)
    opt = torch.optim.Adam(m.parameters(), lr=2e-3)
    for step in range(STEPS):
        idx = torch.from_numpy(rng.choice(tr, 256))
        pred = m(gN[idx]) if kind == "mond" else m(gN[idx], r[idx], gal[idx])
        loss = nn.functional.mse_loss(pred, a[idx])
        opt.zero_grad(); loss.backward(); opt.step()
        if step % 500 == 0: progress(f"56_{kind}", step, STEPS, loss=float(loss.detach()))
    return m


def nmse(pred, tgt):
    return float(np.mean((pred - tgt) ** 2) / np.var(tgt))


def evaluate(d):
    gN = torch.from_numpy(d["gN"]); r = torch.from_numpy(d["r"]); gal = torch.from_numpy(d["gal"]); a = d["a"]
    tr = d["gal"] < N_GAL - HELD; te = ~tr
    mo = train("mond", d); dm = train("dm", d)
    with torch.no_grad():
        mo_pred = mo(gN).numpy()
        # DM zero-shot on held-out: no trained embedding -> use mean of trained embeddings
        emb_mean = dm.emb.weight[:N_GAL - HELD].mean(0, keepdim=True)
        gal_eval = gal.clone()
        dm_pred = dm(gN, r, gal).numpy()
        # held-out DM: override embedding with mean (zero-shot, no galaxy-specific halo)
        h_held = dm.halo(torch.cat([r[te][:, None], emb_mean.expand(te.sum(), 4)], -1))[:, 0].numpy()
        dm_pred_held = d["gN"][te] + h_held
    out = {"mond_in": nmse(mo_pred[tr], a[tr]), "mond_out": nmse(mo_pred[te], a[te]),
           "dm_in": nmse(dm_pred[tr], a[tr]), "dm_out": nmse(dm_pred_held, a[te]),
           "mond_R2_out": float(1 - nmse(mo_pred[te], a[te]))}
    return out


def main():
    rows = []
    for sp in SPREADS:
        d = make_data(sp)
        e = evaluate(d); e["spread"] = sp; rows.append(e)
        print(f"spread {sp:.1f}: MOND in {e['mond_in']:.3f} out {e['mond_out']:.3f} | DM in {e['dm_in']:.3f} out {e['dm_out']:.3f}")

    r0 = rows[0]
    mond_in = [r["mond_in"] for r in rows]
    d1 = bool(r0["mond_out"] < 0.1 and r0["mond_out"] < 0.2 * r0["dm_out"])
    d2 = bool(max(mond_in) / (mond_in[0] + 1e-9) > 5 and rows[-1]["dm_in"] < 0.1)
    d3 = bool(r0["mond_R2_out"] > 0.99)
    out = {"sweep": rows, "D1_universal_MOND_predicts": d1, "D2_persystem_DM_needed": d2,
           "D3_MOND_recovers_law": d3, "dm_vs_mond_is_shareability": bool(d1 and d2 and d3)}
    print(f"\nD1 universal -> MOND predicts new galaxies (zero-shot {r0['mond_out']:.3f}<0.1 & << DM {r0['dm_out']:.3f}): {d1}")
    print(f"D2 per-system -> DM needed (MOND in-sample {mond_in[0]:.3f}->{mond_in[-1]:.3f}, DM stays {rows[-1]['dm_in']:.3f}): {d2}")
    print(f"D3 MOND recovers the law (held-out R^2 {r0['mond_R2_out']:.3f}>0.99): {d3}")
    print(f"\nDM-vs-MOND IS A SHAREABILITY VERDICT: {out['dm_vs_mond_is_shareability']}")
    (RESULTS / "56_dark_matter_vs_mond.json").write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(1, 2, figsize=(12, 4.6))
    ax[0].plot(SPREADS, mond_in, "o-", color="crimson", label="MOND (shared law) in-sample")
    ax[0].plot(SPREADS, [r["dm_in"] for r in rows], "s-", color="navy", label="dark matter (per-galaxy halo) in-sample")
    ax[0].set_xlabel("spread of a0 across galaxies (universality knob)"); ax[0].set_ylabel("normalized MSE")
    ax[0].set_title("per-system anomaly -> shared law fails -> dark matter needed"); ax[0].legend(fontsize=8)
    ax[1].bar([0, 1], [r0["mond_out"], r0["dm_out"]], color=["crimson", "navy"])
    ax[1].set_xticks([0, 1]); ax[1].set_xticklabels(["MOND\n(universal law)", "dark matter\n(per-galaxy halo)"])
    ax[1].set_ylabel("held-out galaxy nMSE (zero-shot)")
    ax[1].set_title("universal anomaly: MOND PREDICTS new galaxies,\ndark matter cannot")
    fig.tight_layout(); fig.savefig(RESULTS / "56_dark_matter_vs_mond.png", dpi=140)
    print("saved results/56_dark_matter_vs_mond.json + .png")


if __name__ == "__main__":
    main()
