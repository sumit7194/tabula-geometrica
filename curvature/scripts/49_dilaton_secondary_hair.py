"""Step 49 — NEW FIELD: the DILATON (secondary hair) — does a DETERMINED charge cost 0 lanes?

Web-verified (Einstein-Maxwell-dilaton): the scalar (dilaton) charge is SECONDARY hair — it is
DETERMINED by the mass and electric charge (proportional to the horizon electric potential x the
coupling), not stored independently. So a dilatonic body has two charges (q, s) but only ONE degree
of freedom: s = kappa*q.

Test (reusing the script-24 lane-counter): bodies carry two charges coupling to two field bumps;
sweep the number of internal lanes L. Two datasets:
  dilaton      q2 = kappa*q1  (the secondary charge is determined)  -> predict knee at L=1
  independent  q1, q2 independent (= script 24)                      -> knee at L=2 (replicate)
This is the NEURAL primary-vs-secondary-hair test, and it chains off the dimensionality refinement
(48): the dilaton body's true latent is 1-d, so its single lane should also be LEGIBLE.

Pre-reg (2026-06-16):
  DL1 dilaton knee=1: mse(L0)/mse(L1) > 3 (one lane needed) AND mse(L1)/mse(L2) < 1.5 (a 2nd buys ~0).
  DL2 independent knee=2: mse(L1)/mse(L2) > 1.7 (the 2nd lane genuinely helps) — replicate 24.
  DL3 legible 1-d code: dilaton L=1 lane decodes q1 linearly, r > 0.9 (1-d free code is legible, per 48).
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
from curvlib import RESULTS, V_MAX, X_RANGE, progress
from importlib import import_module
from torch import nn

s24 = import_module("24_two_charge_lanes")
KAPPA = 0.7
N_BODIES, PER_BODY, STEPS, HELD = 36, 400, 8000, 8
LANES = (0, 1, 2, 3)


def make_data(mode, seed=0):
    rng = np.random.default_rng(seed)
    qm = np.zeros((N_BODIES, 2))
    ch = rng.permutation(N_BODIES)[: int(N_BODIES * 0.6)]
    q1 = rng.choice([-1.0, 1.0], len(ch)) * rng.uniform(0.3, 1.0, len(ch))
    qm[ch, 0] = q1
    if mode == "dilaton":
        qm[ch, 1] = KAPPA * q1                       # secondary: determined by the primary
    else:                                            # independent: a second free charge (= script 24)
        ch2 = rng.permutation(N_BODIES)[: int(N_BODIES * 0.6)]
        qm[ch2, 1] = rng.choice([-1.0, 1.0], len(ch2)) * rng.uniform(0.3, 1.0, len(ch2))
    held = np.arange(N_BODIES - HELD, N_BODIES)
    rows = []
    for i in range(N_BODIES):
        x0 = rng.uniform(*X_RANGE, PER_BODY); v0 = rng.uniform(-V_MAX, V_MAX, PER_BODY)
        tg = s24.integrate(x0, v0, np.full(PER_BODY, qm[i, 0]), np.full(PER_BODY, qm[i, 1]))
        rows.append((np.full(PER_BODY, i), np.stack([x0, v0], 1), tg))
    body = np.concatenate([r[0] for r in rows]).astype(np.int64)
    X = np.concatenate([r[1] for r in rows]).astype(np.float32)
    Y = np.concatenate([r[2] for r in rows]).astype(np.float32)
    seen = np.where(~np.isin(body, held))[0]; rng.shuffle(seen)
    nt = len(seen) // 6
    return {"qm": qm, "held": held,
            "train": (body[seen[nt:]], X[seen[nt:]], Y[seen[nt:]]),
            "test": (body[seen[:nt]], X[seen[:nt]], Y[seen[:nt]])}


def run_arm(mode, L, data):
    torch.manual_seed(49 + L); rng = np.random.default_rng(0)
    m = s24.LaneModel(N_BODIES, L); opt = torch.optim.Adam(m.parameters(), lr=1e-3)
    body, X, Y = data["train"]
    for step in range(STEPS):
        idx = rng.integers(0, len(X), 256)
        loss = nn.functional.mse_loss(m(torch.from_numpy(X[idx]), torch.from_numpy(body[idx])),
                                      torch.from_numpy(Y[idx]))
        opt.zero_grad(); loss.backward(); opt.step()
        if step % 250 == 0:
            progress(f"49_{mode}_L{L}", step, STEPS, loss=float(loss.detach()))
    m.eval()
    tb, tX, tY = data["test"]
    with torch.no_grad():
        mse = float(nn.functional.mse_loss(m(torch.from_numpy(tX), torch.from_numpy(tb)),
                                           torch.from_numpy(tY)))
    leg = None
    if L == 1:
        seen = np.setdiff1d(np.arange(N_BODIES), data["held"])
        w0 = m.w0(torch.from_numpy(seen.astype(np.int64))).detach().numpy()[:, 0]
        q1 = data["qm"][seen, 0]
        leg = float(abs(np.corrcoef(w0, q1)[0, 1]))
    return mse, leg


def sweep(mode):
    data = make_data(mode)
    res = {}
    leg1 = None
    for L in LANES:
        mse, leg = run_arm(mode, L, data)
        res[L] = mse
        if leg is not None:
            leg1 = leg
        print(f"  {mode:11s} L={L}: test MSE {mse:.3e}" + (f" | L1 lane->q1 |r|={leg:.2f}" if leg is not None else ""))
    return res, leg1


def main():
    dil, dil_leg = sweep("dilaton")
    ind, _ = sweep("independent")

    dl1 = bool(dil[0] / dil[1] > 3 and dil[1] / dil[2] < 1.5)
    dl2 = bool(ind[1] / ind[2] > 1.7)
    dl3 = bool(dil_leg is not None and dil_leg > 0.9)
    out = {"dilaton_mse_by_L": {str(k): v for k, v in dil.items()},
           "independent_mse_by_L": {str(k): v for k, v in ind.items()},
           "dilaton_L1_lane_decode_q1": dil_leg, "kappa": KAPPA,
           "DL1_dilaton_knee_1": dl1, "DL2_independent_knee_2": dl2, "DL3_legible_1d_code": dl3,
           "secondary_hair_confirmed": bool(dl1 and dl2 and dl3)}
    print(f"\nDL1 dilaton knee=1 (L0/L1 {dil[0]/dil[1]:.1f}>3 & L1/L2 {dil[1]/dil[2]:.2f}<1.5): {dl1}")
    print(f"DL2 independent knee=2 (L1/L2 {ind[1]/ind[2]:.2f}>1.7): {dl2}")
    print(f"DL3 dilaton 1-d lane legible (|r| {dil_leg}): {dl3}")
    print(f"\nSECONDARY HAIR (determined charge costs 0 extra lanes): {out['secondary_hair_confirmed']}")
    (RESULTS / "49_dilaton.json").write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.plot(list(dil.keys()), list(dil.values()), "o-", color="purple", label="dilaton (q2=κq1, secondary) → knee 1")
    ax.plot(list(ind.keys()), list(ind.values()), "s--", color="darkorange", label="independent (q1,q2 free) → knee 2")
    ax.set_yscale("log"); ax.set_xticks(list(LANES)); ax.set_xlabel("internal lanes L")
    ax.set_ylabel("test MSE (log)"); ax.legend()
    ax.set_title("secondary hair: a DETERMINED charge needs no extra lane")
    fig.tight_layout(); fig.savefig(RESULTS / "49_dilaton.png", dpi=140)
    print("saved results/49_dilaton.json + .png")


if __name__ == "__main__":
    main()
