"""Step 62 — the REAL evaluation harness for Generalist v2 (judge on physics, not loss).

User's correction (2026-06-17): watching loss drop / beating the ctx-mean baseline is naive. A model
has LEARNED a family only if it (a) sits near the SPECIALIST FLOOR, (b) GENERALIZES to held-out and
out-of-range worlds, (c) reproduces the actual PHYSICS (physical gates), and (d) its inferred world-code
RECOVERS the true latent (the law-space prize). This harness measures all of that on a checkpoint and is
meant to GOVERN training (train until these plateau), not the loss curve.

Probes per family:
  - heldout MSE (fresh in-distribution worlds) + EXTRAPOLATION MSE (out-of-range params).
  - SPECIALIST FLOOR: a same-data single-family in-context net (the right yardstick); report ratio.
  - WORLD-CODE DECODE: ridge-decode the true world latent (q, M, Q, Bloch r) from the inferred code -> R^2.
Physical gates: Bloch Born rule (pred affine in n with slope=recovered r, |r|~1); Schwarzschild signature
flip (learned g_vv crosses 0 at r=2M). Law-space: cluster codes across families (ARI vs family).
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
import torch
from torch import nn
from importlib import import_module
from sklearn.linear_model import Ridge
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score
from sklearn.model_selection import cross_val_predict

import worldgen_v2 as wg
from curvlib import RESULTS, load_ckpt
g2 = import_module("61_generalist_v2")

DEV = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
K, Q = g2.K, g2.Q


def world_vec(fam_id, w):
    f = wg.FAMILIES[fam_id].name
    if f == "gravity": return np.array([w["depth"]], np.float32)
    if f == "charged": return np.array([w["q"]], np.float32)
    if f == "scalar": return np.array([w["rho"]], np.float32)
    if f == "schwarzschild": return np.array([w["M"]], np.float32)
    if f == "reissner_nordstrom": return np.array([w["M"], w["Q"]], np.float32)
    return w["r"].astype(np.float32)                       # bloch: (rx,ry,rz)


def gen_family(fam_id, N, seed, extrap=False):
    rng = np.random.default_rng(seed); fam = wg.FAMILIES[fam_id]
    cu = np.zeros((N, K, wg.DU), np.float32); cy = np.zeros((N, K, wg.DY), np.float32)
    qu = np.zeros((N, Q, wg.DU), np.float32); qy = np.zeros((N, Q, wg.DY), np.float32)
    wv = []
    for b in range(N):
        w = fam.world(rng)
        if extrap:                                         # push params out of the training range
            for k in w:
                if k == "M": w[k] = rng.uniform(1.6, 2.2)
                elif k == "q": w[k] = rng.choice([-1, 1]) * rng.uniform(1.2, 1.8)
                elif k == "rho": w[k] = rng.uniform(1.7, 2.5)
                elif k == "Q": w[k] = rng.uniform(0.85, 1.0)
        u, y = fam.obs(w, rng, K + Q)
        cu[b], cy[b], qu[b], qy[b] = u[:K], y[:K], u[K:], y[K:]
        wv.append(world_vec(fam_id, w))
    return {"ctx_u": cu, "ctx_y": cy, "q_u": qu, "q_y": qy, "ymask": fam.ymask, "fam": np.full(N, fam_id, np.int64)}, np.stack(wv)


def to_dev(b):
    return {k: (torch.from_numpy(v).to(DEV) if isinstance(v, np.ndarray) else v) for k, v in b.items()}


def heldout_and_code(m, fam_id, N=256, seed=0, extrap=False):
    b, wv = gen_family(fam_id, N, seed, extrap)
    bd = to_dev(b)
    ym = torch.from_numpy(np.broadcast_to(b["ymask"], (N, wg.DY)).copy()).to(DEV)
    with torch.no_grad():
        code = m.encode(bd["ctx_u"], bd["ctx_y"], bd["fam"]).cpu().numpy()
        pred = m(bd["ctx_u"], bd["ctx_y"], bd["q_u"], bd["fam"])
        mse = float(g2.masked_mse(pred, bd["q_y"], ym))
    return mse, code, wv


def specialist_floor(fam_id, steps=8000):
    """Same in-context architecture, trained on ONE family — the honest 'best a dedicated net does' floor."""
    torch.manual_seed(1); rng = np.random.default_rng(1)
    sp = g2.GeneralistV2(d=192, depth=4).to(DEV)            # smaller dedicated net
    opt = torch.optim.Adam(sp.parameters(), lr=5e-4)
    for step in range(steps):
        b = to_dev(wg.make_batch(rng, 64, K, Q, fam_id=fam_id))
        ym = torch.from_numpy(np.broadcast_to(b["ymask"].cpu().numpy() if torch.is_tensor(b["ymask"]) else b["ymask"], (64, wg.DY)).copy()).to(DEV)
        pred = sp(b["ctx_u"], b["ctx_y"], b["q_u"], b["fam"])
        loss = g2.masked_mse(pred, b["q_y"], ym)
        opt.zero_grad(); loss.backward(); opt.step()
    sp.eval(); mse, _, _ = heldout_and_code(sp, fam_id, 256, 7)
    return mse


def decode_R2(code, wv):
    return float(np.mean([np.corrcoef(cross_val_predict(Ridge(1.0), code, wv[:, j], cv=5), wv[:, j])[0, 1] ** 2
                          if np.std(wv[:, j]) > 1e-6 else np.nan for j in range(wv.shape[1])]))


def born_gate(m):
    """Bloch: model prediction should be AFFINE in the query axis n with slope = recovered r, |r|~1."""
    fam_id = [f.name for f in wg.FAMILIES].index("bloch")
    rng = np.random.default_rng(3); fam = wg.FAMILIES[fam_id]
    w = fam.world(rng); u, y = fam.obs(w, rng, K)
    cz = rng.uniform(-1, 1, 300); phi = rng.uniform(0, 2 * np.pi, 300); s = np.sqrt(1 - cz ** 2)
    nax = np.stack([s * np.cos(phi), s * np.sin(phi), cz], 1).astype(np.float32)
    qu = wg._pad(nax, wg.DU)
    ctx_u = torch.from_numpy(u[None]).to(DEV); ctx_y = torch.from_numpy(y[None]).to(DEV)
    fam_t = torch.tensor([fam_id]).to(DEV); q = torch.from_numpy(qu[None]).to(DEV)
    with torch.no_grad():
        pred = m(ctx_u, ctx_y, q, fam_t)[0, :, 0].cpu().numpy()
    A = np.concatenate([np.ones((300, 1)), nax], 1)        # fit pred = a + b.n  (Born rule = affine in n)
    coef, *_ = np.linalg.lstsq(A, pred, rcond=None)
    fit = A @ coef
    r_rec = 2 * coef[1:]                                    # slope b = r/2 -> r = 2b
    cos_true = float(abs(np.dot(r_rec, w["r"]) / (np.linalg.norm(r_rec) * np.linalg.norm(w["r"]) + 1e-9)))
    return {"born_affine_R2": float(1 - np.sum((pred - fit) ** 2) / (np.sum((pred - pred.mean()) ** 2) + 1e-9)),
            "recovered_r_norm": float(np.linalg.norm(r_rec)), "cos_to_true_r": cos_true}


def _horizon_at(m, fam_id, M, rng):
    """Metric family now predicts g_vv(r) directly: query a grid of r (context = a world with mass M),
    find where the predicted g_vv crosses zero = the learned horizon."""
    fam = wg.FAMILIES[fam_id]; u, y = fam.obs({"M": M}, rng, K)
    ctx_u = torch.from_numpy(u[None]).to(DEV); ctx_y = torch.from_numpy(y[None]).to(DEV); fam_t = torch.tensor([fam_id]).to(DEV)
    rs = np.linspace(0.8, 5.5, 60).astype(np.float32)
    qu = wg._pad(rs[:, None], wg.DU)
    with torch.no_grad():
        gvv = m(ctx_u, ctx_y, torch.from_numpy(qu[None]).to(DEV), fam_t)[0, :, 0].cpu().numpy()
    cross = np.where(np.diff(np.sign(gvv)) != 0)[0]
    if not len(cross): return float("nan")
    i = cross[0]
    return float(rs[i] + (rs[i + 1] - rs[i]) * (0 - gvv[i]) / (gvv[i + 1] - gvv[i]))


def flip_gate(m):
    """Schwarzschild: does the learned g_vv flip at r=2M, AND does the horizon TRACK M (r*~2M across M)?
    The multi-M test is the real check: passing only at one M while ignoring M is the failure to catch."""
    fam_id = [f.name for f in wg.FAMILIES].index("schwarzschild")
    rng = np.random.default_rng(4)
    Ms = [0.8, 1.0, 1.3]; stars = [_horizon_at(m, fam_id, M, rng) for M in Ms]
    true = [2 * M for M in Ms]
    tracks = bool(np.all(np.isfinite(stars)) and np.corrcoef(stars, true)[0, 1] > 0.9 and
                  np.all(np.abs(np.array(stars) - np.array(true)) < 0.5))
    return {"M_values": Ms, "horizon_r_star": stars, "true_horizons": true, "horizon_tracks_M": tracks}


def main():
    m = g2.GeneralistV2().to(DEV)
    opt = torch.optim.Adam(m.parameters())
    step, *_ = load_ckpt(RESULTS / "61_gen2.pt", m, opt, fallback_seed=0)
    m.eval(); print(f"loaded checkpoint @ step {step} on {DEV}\n")

    rows = {}; codes_all, fams_all = [], []
    for fid, fam in enumerate(wg.FAMILIES):
        mse, code, wv = heldout_and_code(m, fid, 256, 0)
        ex_mse, _, _ = heldout_and_code(m, fid, 256, 5, extrap=True)
        floor = specialist_floor(fid)
        dR2 = decode_R2(code, wv)
        rows[fam.name] = {"heldout_mse": mse, "extrap_mse": ex_mse, "specialist_floor": floor,
                          "ratio_to_floor": mse / (floor + 1e-12), "world_decode_R2": dR2}
        codes_all.append(code[:128]); fams_all.append(np.full(128, fid))
        print(f"{fam.name:18s} mse {mse:.2e} | floor {floor:.2e} | x{mse/(floor+1e-12):5.1f} of floor | "
              f"extrap {ex_mse:.2e} | world-decode R^2 {dR2:.3f}")

    born = born_gate(m); flip = flip_gate(m)
    codes_all = np.concatenate(codes_all); fams_all = np.concatenate(fams_all)
    ari = float(adjusted_rand_score(fams_all, KMeans(wg.NFAM, n_init=10, random_state=0).fit(codes_all).labels_))
    print(f"\nBloch Born gate: affine-R^2 {born['born_affine_R2']:.3f}, |r_rec| {born['recovered_r_norm']:.2f}, cos-to-true {born['cos_to_true_r']:.3f}")
    print(f"Schwarzschild flip gate: horizon r* {[round(s,2) for s in flip['horizon_r_star']]} vs true {flip['true_horizons']} (tracks M: {flip['horizon_tracks_M']})")
    print(f"Law-space: family-cluster ARI {ari:.3f}")

    out = {"checkpoint_step": step, "per_family": rows, "born_gate": born, "flip_gate": flip, "lawspace_ARI": ari}
    (RESULTS / "62_generalist_eval.json").write_text(json.dumps(out, indent=1))
    print("\nsaved results/62_generalist_eval.json")
    # honest verdict
    near_floor = [n for n, r in rows.items() if r["ratio_to_floor"] < 3]
    print(f"\nVERDICT — near specialist floor (<3x): {near_floor}")
    print(f"physical gates: Born {'PASS' if born['born_affine_R2']>0.9 and abs(born['recovered_r_norm']-1)<0.2 else 'FAIL'}, "
          f"flip-tracks-M {'PASS' if flip['horizon_tracks_M'] else 'FAIL'}")


if __name__ == "__main__":
    main()
