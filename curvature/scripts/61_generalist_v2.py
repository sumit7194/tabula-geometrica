"""Step 61 — GENERALIST v2: one in-context transformer across the full physics span (the main thread now).

User decision (2026-06-17): stop building one-off specialists; build ONE bigger generalist where
cross-pollination can happen and there's real internal structure to mech-interp. Applies our lessons:
amortized in-context inference (legibility), symmetry-respecting INVARIANT pool over the exchangeable
context (G-sym), MPS, built-in HOOKS for mech-interp from day one. Data = worldgen_v2 (gravity, charged,
scalar, Schwarzschild, Reissner-Nordstrom, Bloch). ~10-15M params target.

This file: architecture + an end-to-end SMOKE TRAIN to prove the pipeline (loss drops across all
families on MPS). The real long train + the law-space/BH probes follow.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import argparse

import numpy as np
import torch
from torch import nn
import worldgen_v2 as wg
from curvlib import progress, RESULTS, save_ckpt, load_ckpt

DMODEL, DEPTH, HEADS, K, Q, BATCH = 352, 8, 8, 16, 8, 64   # ~12M params; K=16 context for harder in-context inference


class GeneralistV2(nn.Module):
    def __init__(s, d=DMODEL, depth=DEPTH, heads=HEADS):
        super().__init__()
        s.fam = nn.Embedding(wg.NFAM, d)
        s.ctx_embed = nn.Linear(wg.DU + wg.DY, d)            # context (u,y) token
        s.q_embed = nn.Linear(wg.DU, d)                      # query u token
        s.layers = nn.ModuleList([nn.TransformerEncoderLayer(d, heads, 4 * d, batch_first=True, dropout=0.0, norm_first=True, activation="gelu") for _ in range(depth)])
        s.ln = nn.LayerNorm(d)
        s.head = nn.Sequential(nn.Linear(2 * d, 2 * d), nn.GELU(), nn.Linear(2 * d, d), nn.GELU(), nn.Linear(d, wg.DY))

    def encode(s, ctx_u, ctx_y, fam, cache=None):
        f = s.fam(fam)[:, None, :]
        h = s.ctx_embed(torch.cat([ctx_u, ctx_y], -1)) + f   # (B,K,d)
        for i, layer in enumerate(s.layers):
            h = layer(h)
            if cache is not None:
                cache[f"layer{i}"] = h.detach()
        code = s.ln(h).mean(1)                                # invariant pool over the exchangeable context
        if cache is not None:
            cache["code"] = code.detach()
        return code

    def forward(s, ctx_u, ctx_y, q_u, fam, cache=None):
        code = s.encode(ctx_u, ctx_y, fam, cache)
        f = s.fam(fam)[:, None, :]
        qt = s.q_embed(q_u) + f                               # (B,Q,d)
        cc = code[:, None, :].expand(-1, q_u.shape[1], -1)
        return s.head(torch.cat([qt, cc], -1))                # (B,Q,DY)


def masked_mse(pred, tgt, ymask):                         # RAW physical MSE (for eval / per-family floors)
    m = ymask[:, None, :]
    return ((pred - tgt) ** 2 * m).sum() / (m.expand_as(pred).sum() + 1e-9)


def balanced_loss(pred, tgt, ymask, fam, yvar):           # training: per-family scale-balanced so no family dominates
    m = ymask[:, None, :]
    se = ((pred - tgt) ** 2 * m).sum(-1) / (m.sum(-1) + 1e-9)   # (B,Q) mean over valid dims
    w = (1.0 / (yvar[fam] + 1e-9))[:, None]
    return (se * w).mean()


def to_dev(b, dev):
    return {k: (torch.from_numpy(v).to(dev) if isinstance(v, np.ndarray) else v) for k, v in b.items()}


def eval_families(m, dev):
    out = {}
    with torch.no_grad():
        for fid, fam in enumerate(wg.FAMILIES):
            b = to_dev(wg.make_batch(np.random.default_rng(100 + fid), 256, K, Q, fam_id=fid), dev)
            pred = m(b["ctx_u"], b["ctx_y"], b["q_u"], b["fam"])
            fl = float(masked_mse(pred, b["q_y"], b["ymask"]))
            base = b["ctx_y"].mean(1, keepdim=True).expand(-1, Q, -1)
            bl = float(masked_mse(base, b["q_y"], b["ymask"]))
            out[fam.name] = (fl, bl / (fl + 1e-12))
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--steps", type=int, default=40000); a = ap.parse_args()
    dev = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
    torch.manual_seed(0); rng = np.random.default_rng(0)
    m = GeneralistV2().to(dev)
    nparams = sum(p.numel() for p in m.parameters())
    print(f"device {dev} | GeneralistV2 params {nparams/1e6:.2f}M | families {wg.NFAM} | steps {a.steps}", flush=True)
    opt = torch.optim.Adam(m.parameters(), lr=3e-4)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=a.steps, eta_min=1e-5)
    yvar = torch.from_numpy(wg.fam_yvars()).to(dev)
    print(f"per-family y-var (loss-balanced): {dict(zip([f.name for f in wg.FAMILIES], yvar.cpu().numpy().round(4)))}", flush=True)
    ckpt = RESULTS / "61_gen2.pt"
    start = 0
    if ckpt.exists():
        start, rng, exact = load_ckpt(ckpt, m, opt, fallback_seed=0)
        for _ in range(start): sched.step()
        print(f"resumed at step {start} ({'bit-exact' if exact else 'legacy'})", flush=True)
    for step in range(start, a.steps):
        b = to_dev(wg.make_batch(rng, BATCH, K, Q), dev)
        pred = m(b["ctx_u"], b["ctx_y"], b["q_u"], b["fam"])
        loss = balanced_loss(pred, b["q_y"], b["ymask"], b["fam"], yvar)
        opt.zero_grad(); loss.backward(); opt.step(); sched.step()
        if step % 100 == 0:
            progress("61_gen2", step, a.steps, loss=float(loss.detach()))
        if step % 4000 == 0 and step > start:
            save_ckpt(ckpt, m, opt, step, rng)
            m.eval(); ef = eval_families(m, dev); m.train()
            print(f"[{step}] " + " ".join(f"{n[:4]}:{v[0]:.1e}({v[1]:.0f}x)" for n, v in ef.items()), flush=True)
    save_ckpt(ckpt, m, opt, a.steps, rng)
    m.eval(); ef = eval_families(m, dev)
    print(f"\nfinal train loss {float(loss.detach()):.4e}\nper-family test loss:")
    for n, v in ef.items():
        print(f"  {n:18s} loss {v[0]:.4e}  ({v[1]:.1f}x better than ctx-mean baseline)")


if __name__ == "__main__":
    main()
