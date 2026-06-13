"""Step 28b — gate A3a: does the EQUIVARIANT channel carry the per-body charge?

For each charged-family probe episode, decode each query's true charge from
(i) the equivariant per-body code b (R^8) and (ii) the invariant stage w (R^64,
control). The split predicts: b decodes charge (r>0.9), w does NOT (it's the same
vector for every body in an episode, so it structurally cannot — the equivalence-
principle invariance, measured). Needs the labeled probe bank (25_worldgen
--emit-qlabels) and the trained SymGeneralist.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
import torch
from curvlib import RESULTS
from importlib import import_module
from sklearn.linear_model import Ridge
from sklearn.model_selection import cross_val_predict

m28 = import_module("28_symmetric_generalist")
FAMS = ["flat1p1", "flat3p1", "well1p1", "aniso2p1",
        "chargedE", "magneticB", "twocharge", "matter"]
CHARGED = {"chargedE": 4, "magneticB": 5, "twocharge": 6}


def decode_r(X, y):
    """5-fold CV held-out correlation per charge component."""
    y = np.atleast_2d(y.T).T if y.ndim == 1 else y
    rs = []
    for j in range(y.shape[1]):
        pred = cross_val_predict(Ridge(alpha=1.0), X, y[:, j], cv=5)
        rs.append(float(np.corrcoef(pred, y[:, j])[0, 1]) if np.std(y[:, j]) > 1e-6 else float("nan"))
    return rs


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--model", default=str(RESULTS / "28_symgen_sym.pt"))
    p.add_argument("--bank", default=str(RESULTS / "25_bank_probe.npz"))
    p.add_argument("--device", default="cpu")
    args = p.parse_args()

    bank = dict(np.load(args.bank))
    meta = json.loads(Path(args.bank).with_suffix(".meta.json").read_text())
    model = m28.SymGeneralist()
    model.load_state_dict(torch.load(args.model, map_location="cpu"))
    model.to(args.device).eval()

    out = {}
    for name, fi in CHARGED.items():
        idx = np.where(bank["family"] == fi)[0]
        B, W, Y = [], [], []
        with torch.no_grad():
            for s in range(0, len(idx), 128):
                bi = idx[s:s + 128]
                tk = torch.from_numpy(bank["tokens"][bi]).to(args.device)
                q = torch.from_numpy(bank["queries"][bi]).to(args.device)
                b, _, _ = model.perbody(tk, q)            # (n, Nq, 8) equivariant
                w = model.summary(tk)                     # (n, 64) invariant
                B.append(b.cpu().numpy())
                W.append(np.repeat(w.cpu().numpy()[:, None, :], q.shape[1], axis=1))
                for e in bi:
                    Y.extend(meta[e]["q_labels"])
        Bm = np.concatenate(B).reshape(-1, m28.PERBODY)
        Wm = np.concatenate(W).reshape(-1, 64)
        Ym = np.array(Y, dtype=float)
        out[name] = {"equivariant_r": decode_r(Bm, Ym),
                     "invariant_ctrl_r": decode_r(Wm, Ym), "n": len(Ym)}
        eq, ct = out[name]["equivariant_r"], out[name]["invariant_ctrl_r"]
        print(f"{name:10s} equivariant b r={[f'{x:.3f}' for x in eq]}  "
              f"invariant-w ctrl r={[f'{x:.3f}' for x in ct]}  (n={len(Ym)})")

    allr = [r for v in out.values() for r in v["equivariant_r"]]
    pas = all(r > 0.9 for r in allr)
    print(f"A3a: per-body charge from equivariant channel min r={min(allr):.3f} "
          f"-> gate >0.9 {'PASS' if pas else 'FAIL'}")
    out["A3a_pass"] = bool(pas)
    (RESULTS / "28b_perbody_decode.json").write_text(json.dumps(out, indent=1))
    print("saved results/28b_perbody_decode.json")


if __name__ == "__main__":
    main()
