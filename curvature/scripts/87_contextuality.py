"""Step 87 — IMPOSSIBILITY CERTIFICATE IV: a net's failure certifies CONTEXTUALITY (Kochen-Specker / KCBS).

The single-system cousin of Bell (Certificate I): Bell rules out LOCAL hidden variables (2 parties); KCBS rules
out NON-CONTEXTUAL hidden variables (1 system) -- a more fundamental no-go (Bell nonlocality is a special case
of contextuality). Web-verified KCBS: five yes/no projectors P_1..P_5 on a qutrit arranged in a pentagon
(5-cycle) with exclusivity (adjacent projectors are mutually exclusive). A NON-CONTEXTUAL hidden-variable model
assigns each P_i a context-independent value in {0,1} respecting exclusivity; the sum is bounded by the
independence number of C_5: sum<P_i> <= 2. Quantum mechanics reaches sum<P_i> = sqrt5 ~= 2.236.

We build a genuine non-contextual model as a learnable distribution over the 11 valid value-assignments (the
independent sets of C_5). Scaling the symmetric quantum predictions by a visibility v (each <P_i> = v/sqrt5,
sum = v*sqrt5), the NC model tracks quantum up to sum=2, then SLAMS into the non-contextual bound it cannot
pass -- and the wall lands at v* = 2/sqrt5 ~= 0.894. The failure certifies contextuality.

Pre-reg (2026-06-17):
  K1 NON-CONTEXTUAL REGIME FITS: at v=0.7 (sum=1.565<2) the NC model matches the target, residual < 1e-3.
  K2 GENUINE NC MODEL: max achievable sum over all v <= 2.02 (it respects the KCBS bound by construction).
  K3 THE CERTIFICATE: the NC model tracks quantum sum=v*sqrt5 up to a knee, then caps at 2; the knee is within
     6% of v* = 2/sqrt5 = 0.894, AND v=1 (sum=sqrt5) is unfittable.
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

np.seterr(all="ignore")

# the 11 valid non-contextual value-assignments = independent sets of the 5-cycle C_5 (no two adjacent =1)
EDGES = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)]
def independent_sets():
    sets = []
    for mask in range(32):
        v = [(mask >> i) & 1 for i in range(5)]
        if all(not (v[a] and v[b]) for a, b in EDGES):
            sets.append(v)
    return np.array(sets, np.float32)                          # (11, 5): {}, 5 singletons, 5 non-adjacent pairs
VERTS = independent_sets()
SQRT5 = float(np.sqrt(5))


def fit_nc(v, steps=1500):
    """learnable non-contextual model: distribution p over the assignment vertices; match <P_i> = v/sqrt5."""
    V = torch.tensor(VERTS); logits = torch.zeros(len(VERTS), requires_grad=True)
    opt = torch.optim.Adam([logits], lr=0.05)
    target = torch.full((5,), v / SQRT5)
    for step in range(steps):
        p = torch.softmax(logits, 0)
        pred = (p[:, None] * V).sum(0)                          # <P_i> = sum_v p_v vertex_v[i]
        loss = ((pred - target) ** 2).sum()
        opt.zero_grad(); loss.backward(); opt.step()
        if step % 300 == 0: progress(f"87_v{v:.2f}", step, steps, loss=float(loss.detach()))
    with torch.no_grad():
        p = torch.softmax(logits, 0); pred = (p[:, None] * V).sum(0)
        resid = float(((pred - target) ** 2).sum().sqrt()); achieved = float(pred.sum())
    return resid, achieved


def main():
    vs = np.array([0.5, 0.6, 0.7, 0.8, 0.85, 0.894, 0.92, 0.96, 1.0])
    resids, sums = [], []
    for v in vs:
        r, S = fit_nc(v); resids.append(r); sums.append(S)
        print(f"v={v:.3f}: NC residual {r:.4f} | NC sum {S:.3f} | quantum v*sqrt5 = {v*SQRT5:.3f}")
    resids = np.array(resids); sums = np.array(sums); quant = vs * SQRT5

    ratio = sums / quant                                        # 1 while NC tracks quantum, <1 once it caps at 2
    track = vs[ratio > 0.98]; v_knee = float(track.max()) if len(track) else None
    v_star = 2 / SQRT5
    k1 = bool(resids[np.argmin(np.abs(vs - 0.7))] < 1e-3)
    k2 = bool(sums.max() < 2.02)
    k3 = bool(v_knee is not None and abs(v_knee - v_star) < 0.06 and resids[-1] > 0.02)
    out = {"v": vs.tolist(), "nc_residual": resids.tolist(), "nc_sum": sums.tolist(), "quantum_sum": quant.tolist(),
           "v_knee": v_knee, "v_star_2_over_sqrt5": v_star, "max_nc_sum": float(sums.max()),
           "K1_nc_regime_fits": k1, "K2_genuine_nc_model": k2, "K3_certificate_at_kcbs_bound": k3,
           "contextuality_certified": bool(k1 and k2 and k3)}
    print(f"\nK1 NC regime fits (residual@v=0.7 < 1e-3): {k1}")
    print(f"K2 genuine NC model (max sum {sums.max():.3f} <= 2.02, respects KCBS bound): {k2}")
    print(f"K3 certificate: NC model fails at v_knee={v_knee} vs 2/sqrt5={v_star:.4f}; v=1 unfittable (resid {resids[-1]:.3f}): {k3}")
    print(f"\nCONTEXTUALITY CERTIFIED BY FAILURE (no non-contextual code above 2/sqrt5): {out['contextuality_certified']}")
    (RESULTS / "87_contextuality.json").write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(1, 2, figsize=(13, 5))
    ax[0].plot(vs, quant, "k--", label="quantum KCBS Σ = v·√5")
    ax[0].plot(vs, sums, "o-", color="crimson", label="best NON-CONTEXTUAL model Σ")
    ax[0].axhline(2.0, color="navy", ls=":", label="KCBS non-contextual bound = 2")
    ax[0].axvline(2 / SQRT5, color="orange", ls=":", label="v*=2/√5=0.894")
    ax[0].set_xlabel("visibility v"); ax[0].set_ylabel("Σ⟨Pᵢ⟩"); ax[0].legend(fontsize=8)
    ax[0].set_title("the non-contextual model tracks quantum, then hits a wall\n(failure at v* certifies contextuality)")
    ax[1].plot(vs, resids, "s-", color="darkorange"); ax[1].axvline(2 / SQRT5, color="orange", ls=":")
    ax[1].set_xlabel("visibility v"); ax[1].set_ylabel("non-contextual fit residual")
    ax[1].set_title("no non-contextual code above v*\n(cheapest-explanation failure = the certificate)")
    fig.tight_layout(); fig.savefig(RESULTS / "87_contextuality.png", dpi=140)
    print("saved results/87_contextuality.json + .png")


if __name__ == "__main__":
    main()
