"""Step 28 — PHASE G-sym: the symmetry-respecting generalist.

Body-relabeling symmetry, made architectural. Two readouts off the encoded
context H:
  (1) INVARIANT stage  w = to_summary(mean(H)) in R^64  — permutation-invariant,
      keeps body-SYMMETRIC info (geometry); the legible G3 object.
  (2) EQUIVARIANT per-body: the query cross-attends into H, bottlenecked to R^8 —
      small by design so it carries per-body LABELS (charges), not the world.
The stage/actor split = the invariant/equivariant decomposition under relabeling
(pre-registration 2026-06-15; frame credited to a parallel Claude session).
Same forward(tokens, queries) interface as step 26, so its losses/evaluate and
the step-27 probes reuse unchanged. Bit-exact ckpts; --device mps.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
import torch
from curvlib import RESULTS, load_ckpt, progress, save_ckpt
from torch import nn
from importlib import import_module

g26 = import_module("26_generalist")
D, SUMMARY, LAYERS, HEADS = g26.D, g26.SUMMARY, g26.LAYERS, g26.HEADS
BATCH, LR = g26.BATCH, g26.LR
PERBODY = 8  # equivariant-channel bottleneck: a few per-body numbers, not the world


class SymGeneralist(nn.Module):
    def __init__(self):
        super().__init__()
        self.embed = nn.Linear(18, D)
        enc = nn.TransformerEncoderLayer(D, HEADS, 3 * D, batch_first=True,
                                         dropout=0.0, norm_first=True)
        self.encoder = nn.TransformerEncoder(enc, LAYERS)
        self.to_summary = nn.Linear(D, SUMMARY)          # invariant stage
        self.q_embed = nn.Linear(14, D)
        self.cross = nn.MultiheadAttention(D, HEADS, batch_first=True)  # equivariant
        self.to_perbody = nn.Linear(D, PERBODY)
        self.head = nn.Sequential(
            nn.Linear(D + SUMMARY + PERBODY, 256), nn.GELU(),
            nn.Linear(256, 256), nn.GELU(),
        )
        self.out_pair = nn.Linear(256, 1)
        self.out_traj = nn.Linear(256, 6)

    def _encode(self, tokens):
        return self.encoder(self.embed(tokens))

    def summary(self, tokens):  # the G3 object — invariant stage channel
        return self.to_summary(self._encode(tokens).mean(dim=1))

    def perbody(self, tokens, queries):
        """Equivariant per-body code: each query pulls its own body from H."""
        H = self._encode(tokens)
        qe = self.q_embed(queries)
        c, _ = self.cross(qe, H, H, need_weights=False)
        return self.to_perbody(c), H, qe

    def forward(self, tokens, queries):
        H = self._encode(tokens)
        w = self.to_summary(H.mean(dim=1))                # (B, SUMMARY) invariant
        qe = self.q_embed(queries)                        # (B, Q, D)
        c, _ = self.cross(qe, H, H, need_weights=False)   # (B, Q, D) equivariant
        b = self.to_perbody(c)                            # (B, Q, PERBODY)
        B, Q, _ = queries.shape
        wq = w[:, None, :].expand(B, Q, SUMMARY)
        h = self.head(torch.cat([qe, wq, b], dim=-1))
        return self.out_pair(h)[..., 0], self.out_traj(h)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--device", default="cpu", choices=("cpu", "mps"))
    p.add_argument("--bank", default=str(RESULTS / "25_bank_120k.npz"))
    p.add_argument("--val-bank", default=str(RESULTS / "25_bank.npz"))
    p.add_argument("--steps", type=int, default=150000)
    p.add_argument("--tag", default="_sym")
    args = p.parse_args()

    bank = dict(np.load(args.bank))
    vbank = dict(np.load(args.val_bank))
    vmask = np.zeros(len(vbank["family"]), dtype=bool)
    for fam in np.unique(vbank["family"]):
        fi = np.where(vbank["family"] == fam)[0]
        vmask[fi[-len(fi) // 10:]] = True
    va_idx = np.where(vmask)[0]
    tr_idx = np.arange(len(bank["family"]))
    print(f"train {len(tr_idx)} (bank {Path(args.bank).name}) / val {len(va_idx)}")

    torch.manual_seed(28)
    model = SymGeneralist()
    print(f"SymGeneralist: {sum(p_.numel() for p_ in model.parameters())/1e6:.2f}M "
          f"params (perbody bottleneck={PERBODY}), device {args.device}")
    opt = torch.optim.Adam(model.parameters(), lr=LR)
    rng = np.random.default_rng(0)
    ckpt = RESULTS / f"28_ckpt{args.tag}.pt"
    start = 0
    if ckpt.exists():
        start, rng, exact = load_ckpt(ckpt, model, opt, fallback_seed=0)
        print(f"resumed at {start} ({'bit-exact' if exact else 'legacy'})")
    model.to(args.device)
    for st in opt.state.values():
        for k, v in st.items():
            if torch.is_tensor(v):
                st[k] = v.to(args.device)

    for step in range(start, args.steps):
        b = tr_idx[rng.integers(0, len(tr_idx), BATCH)]
        tk = torch.from_numpy(bank["tokens"][b]).to(args.device)
        q = torch.from_numpy(bank["queries"][b]).to(args.device)
        tg = torch.from_numpy(bank["targets"][b]).to(args.device)
        l_pair, l_traj = g26.losses(model, tk, q, tg)
        loss = l_pair + l_traj
        opt.zero_grad()
        loss.backward()
        opt.step()
        if step % 200 == 0:
            progress(f"28_symgen{args.tag}", step, args.steps, loss=float(loss.detach()),
                     pair=float(l_pair.detach()), traj=float(l_traj.detach()))
            if step % 1000 == 0 and step > 0:
                save_ckpt(ckpt, model, opt, step, rng)
            if step % 4000 == 0:
                print(f"  step {step}: pair {float(l_pair):.4f} traj {float(l_traj):.5f}")

    model.eval()
    accs, mses = g26.evaluate(model, vbank, va_idx, args.device)
    fams = ["flat1p1", "flat3p1", "well1p1", "aniso2p1",
            "chargedE", "magneticB", "twocharge", "matter"]
    table = {}
    for fi, name in enumerate(fams):
        row = {}
        if fi in accs:
            row["pair_acc"] = accs[fi]
        if fi in mses:
            row["traj_mse"] = mses[fi]
        table[name] = row
        print(f"A1 {name:10s}: {row}")
    torch.save(model.state_dict(), RESULTS / f"28_symgen{args.tag}.pt")
    (RESULTS / f"28_g1{args.tag}.json").write_text(json.dumps(table, indent=1))
    print("saved model + A1 table")


if __name__ == "__main__":
    main()
