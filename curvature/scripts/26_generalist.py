"""Step 26 — PHASE G: the generalist. One model, eight world families.

Reads context tokens (pairs/trajectories/matter, family never given), pools a
world-summary w, answers queries conditioned on w. The summary space is the
scientific object (G-3 probes). Pre-registration in the lab notebook
(2026-06-15). Bit-exact checkpoints; detached-friendly; --device mps.
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

D, SUMMARY, LAYERS, HEADS = 192, 64, 5, 6
STEPS, BATCH, LR = 30000, 64, 3e-4


class Generalist(nn.Module):
    def __init__(self):
        super().__init__()
        self.embed = nn.Linear(18, D)
        enc = nn.TransformerEncoderLayer(D, HEADS, 3 * D, batch_first=True,
                                         dropout=0.0, norm_first=True)
        self.encoder = nn.TransformerEncoder(enc, LAYERS)
        self.to_summary = nn.Linear(D, SUMMARY)
        self.q_embed = nn.Linear(14, D)
        self.head = nn.Sequential(
            nn.Linear(D + SUMMARY, 256), nn.GELU(), nn.Linear(256, 256), nn.GELU(),
        )
        self.out_pair = nn.Linear(256, 1)
        self.out_traj = nn.Linear(256, 6)

    def summary(self, tokens):
        h = self.encoder(self.embed(tokens))
        return self.to_summary(h.mean(dim=1))

    def forward(self, tokens, queries):
        w = self.summary(tokens)  # (B, SUMMARY)
        B, Q, _ = queries.shape
        qe = self.q_embed(queries)  # (B, Q, D)
        wq = w[:, None, :].expand(B, Q, SUMMARY)
        h = self.head(torch.cat([qe, wq], dim=-1))
        return self.out_pair(h)[..., 0], self.out_traj(h)


def losses(model, tokens, queries, targets):
    logit, reg = model(tokens, queries)
    is_pair = queries[..., 0] > 0.5
    l_pair = nn.functional.binary_cross_entropy_with_logits(
        logit[is_pair], targets[..., 0][is_pair]) if is_pair.any() else logit.sum() * 0
    is_traj = ~is_pair
    l_traj = nn.functional.mse_loss(
        reg[is_traj], targets[is_traj]) if is_traj.any() else reg.sum() * 0
    return l_pair, l_traj


def evaluate(model, bank, idx, device, bs=128):
    accs, mses = {}, {}
    with torch.no_grad():
        for fam in np.unique(bank["family"][idx]):
            fidx = idx[bank["family"][idx] == fam]
            correct = total = 0
            se = n_t = 0.0
            for i in range(0, len(fidx), bs):
                b = fidx[i:i + bs]
                tk = torch.from_numpy(bank["tokens"][b]).to(device)
                q = torch.from_numpy(bank["queries"][b]).to(device)
                tg = torch.from_numpy(bank["targets"][b]).to(device)
                logit, reg = model(tk, q)
                is_pair = q[..., 0] > 0.5
                if is_pair.any():
                    pred = (logit[is_pair] > 0).float()
                    correct += float((pred == tg[..., 0][is_pair]).sum())
                    total += int(is_pair.sum())
                if (~is_pair).any():
                    se += float(((reg[~is_pair] - tg[~is_pair]) ** 2).mean()
                                * int((~is_pair).sum()))
                    n_t += int((~is_pair).sum())
            if total:
                accs[int(fam)] = correct / total
            if n_t:
                mses[int(fam)] = se / n_t
    return accs, mses


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--device", default="cpu", choices=("cpu", "mps"))
    p.add_argument("--bank", default=str(RESULTS / "25_bank.npz"))
    p.add_argument("--steps", type=int, default=STEPS)
    p.add_argument("--tag", default="", help="artifact suffix, e.g. _48k (own ckpt/outputs)")
    p.add_argument("--val-bank", default="", help="if set: train on ALL of --bank, "
                   "val on this bank's standard split (shared val across scaling arms)")
    args = p.parse_args()

    bank = dict(np.load(args.bank))
    n = len(bank["family"])
    if args.val_bank:
        vbank = dict(np.load(args.val_bank))
        vmask = np.zeros(len(vbank["family"]), dtype=bool)
        for fam in np.unique(vbank["family"]):
            fi = np.where(vbank["family"] == fam)[0]
            vmask[fi[-len(fi) // 10:]] = True
        va_idx = np.where(vmask)[0]
        tr_idx = np.arange(n)
    else:
        vbank = bank
        val_mask = np.zeros(n, dtype=bool)
        for fam in np.unique(bank["family"]):
            fi = np.where(bank["family"] == fam)[0]
            val_mask[fi[-len(fi) // 10:]] = True
        tr_idx = np.where(~val_mask)[0]
        va_idx = np.where(val_mask)[0]
    print(f"bank {n} episodes: {len(tr_idx)} train / {len(va_idx)} val (unseen worlds)")

    torch.manual_seed(26)
    model = Generalist()
    n_par = sum(p_.numel() for p_ in model.parameters())
    print(f"generalist: {n_par/1e6:.2f}M params, device {args.device}")
    opt = torch.optim.Adam(model.parameters(), lr=LR)
    rng = np.random.default_rng(0)
    ckpt = RESULTS / f"26_ckpt{args.tag}.pt"
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
        b = rng.integers(0, len(tr_idx), BATCH)
        idx = tr_idx[b]
        tk = torch.from_numpy(bank["tokens"][idx]).to(args.device)
        q = torch.from_numpy(bank["queries"][idx]).to(args.device)
        tg = torch.from_numpy(bank["targets"][idx]).to(args.device)
        l_pair, l_traj = losses(model, tk, q, tg)
        loss = l_pair + l_traj
        opt.zero_grad()
        loss.backward()
        opt.step()
        if step % 200 == 0:
            progress(f"26_generalist{args.tag}", step, args.steps,
                     loss=float(loss.detach()),
                     pair=float(l_pair.detach()), traj=float(l_traj.detach()))
            if step % 1000 == 0 and step > 0:
                save_ckpt(ckpt, model, opt, step, rng)
            if step % 4000 == 0:
                print(f"  step {step}: pair {float(l_pair):.4f} traj {float(l_traj):.5f}")

    model.eval()
    accs, mses = evaluate(model, vbank, va_idx, args.device)
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
        print(f"G1 {name:10s}: {row}")
    torch.save(model.state_dict(), RESULTS / f"26_generalist{args.tag}.pt")
    (RESULTS / f"26_g1{args.tag}.json").write_text(json.dumps(table, indent=1))
    print(f"saved model + G1 table ({args.tag or 'default'})")


if __name__ == "__main__":
    main()
