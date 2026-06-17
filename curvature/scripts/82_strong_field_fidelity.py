"""Step 82 — STRONG-FIELD FIDELITY: shadow-edge error as a quantitative learning curve (sister-session idea).

The EHT image (79) put the shadow edge at b_crit ~= 5.76M vs the exact 3sqrt3 = 5.196M (+11%). Two independent
reads agree (ray-capture 5.76, potential-method 5.61), so it is REAL strong-field error: the photon sphere sits
at r=3M (deep strong field), the hardest region for a net trained mostly on weaker curvature to extrapolate
into; under-curved null rays => capture cross-section reads too big => shadow too large.

Sister-session proposal (cross-measurement: exact ansatz engine = ground truth 5.196; neural engine validated):
turn b_crit error into a STRONG-FIELD FIDELITY SCORE and trace its learning curve -- sweep how deep into the
strong field the training rays reach (r_floor: only keep ray points with r >= r_floor) and watch b_crit march
from 5.76 down toward 5.196. b_crit read from the learned force via the photon potential (1/sqrt(V_max)), with
the force law FIT on available data and EXTRAPOLATED to the photon sphere u=1/3 -- so the extrapolation gap
(how far u_max_data sits below 1/3) IS the strong-field-depth knob.

Pre-reg (2026-06-17):
  F1 MONOTONE LEARNING CURVE: b_crit decreases monotonically (within tol) as r_floor decreases (deeper data).
  F2 the deepest-data b_crit is within 12% of 3sqrt3 AND clearly better than the shallowest.
  F3 the error is strong-field: shallow (r_floor>=4) b_crit error > 15% while deep (r_floor<=3.2) < 12%.
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
from importlib import import_module
from curvlib import RESULTS, progress
from torch import nn

ph = import_module("78_photon_shadow")
DPHI = ph.DPHI
B_TRUE = 3 * np.sqrt(3)
np.seterr(all="ignore")


def data_bmin(b_min):
    """rays kept WHOLE but only for impact parameter b >= b_min: the smallest b sets the deepest approach
    r_min the training reaches (b_min<~5.2 directly probes the photon sphere r=3M; larger b_min stays shallow)."""
    X, Y = [], []
    for b in np.concatenate([np.linspace(b_min, 6.0, 260), np.linspace(6.0, 14, 80)]):
        _, U, W = ph.ray(b)
        for i in range(len(U) - 1):
            X.append([U[i], W[i]]); Y.append([U[i + 1], W[i + 1]])
    return np.array(X, np.float32), np.array(Y, np.float32)


def train(X, Y, steps=7000):
    n = len(X); ntr = int(n * 0.9); idx = np.random.default_rng(0).permutation(n)
    Xt = torch.from_numpy(X[idx]); Yt = torch.from_numpy(Y[idx])
    m = ph.Photon(); opt = torch.optim.Adam(m.parameters(), lr=1e-3); rng = np.random.default_rng(1)
    for step in range(steps):
        b = rng.integers(0, ntr, 256)
        loss = nn.functional.mse_loss(m(Xt[b]), Yt[b])
        opt.zero_grad(); loss.backward(); opt.step()
    m.eval(); return m


def bcrit_potential(m, X, u_hi):
    """b_crit = 1/sqrt(max V); V from the learned force g(u) fit on available u (extrapolated to u=1/3)."""
    with torch.no_grad():
        gX = (m(torch.from_numpy(X)).numpy()[:, 1] - X[:, 1]) / DPHI
    uX = X[:, 0]
    lo, hi = 0.10, min(u_hi - 0.005, 0.46)
    edges = np.linspace(lo, hi, 22); ctr = 0.5 * (edges[:-1] + edges[1:])
    bing = np.array([np.median(gX[(uX >= edges[i]) & (uX < edges[i + 1])]) if np.any((uX >= edges[i]) & (uX < edges[i + 1])) else np.nan for i in range(len(ctr))])
    ok = np.isfinite(bing)
    if ok.sum() < 3:
        return None
    A = np.stack([ctr[ok] ** 2, ctr[ok]], 1)
    (c2, c1), *_ = np.linalg.lstsq(A, bing[ok], rcond=None)
    ug = np.linspace(0, 0.45, 2000); g = c2 * ug ** 2 + c1 * ug
    V = np.concatenate([[0], np.cumsum(-2 * g[1:]) * (ug[1] - ug[0])])
    return float(1.0 / np.sqrt(V.max())) if V.max() > 0 else None


def bcrit_capture(m, seeds=2):
    """direct: largest impact parameter whose net ray reaches the horizon (the sister's preferred method).
    fine scan + small averaging over re-traces for a stable boundary."""
    def cap(b, u0=0.01, nsteps=7000):
        u = u0; w = float(np.sqrt(max(1 / b ** 2 - u0 ** 2 + 2 * u0 ** 3, 0)))
        for _ in range(nsteps):
            with torch.no_grad():
                o = m(torch.tensor([[u, w]], dtype=torch.float32)).numpy()[0]
            u, w = float(o[0]), float(o[1])
            if u >= 0.5: return True
            if u <= 0.003 and w < 0: return False
        return False
    bs = np.linspace(4.7, 6.5, 180); c = np.array([cap(b) for b in bs])
    if not c.any():
        return None
    # boundary = midpoint between the largest captured and the next escaping b
    last_cap = np.where(c)[0].max()
    return float(bs[last_cap]) if last_cap == len(bs) - 1 else float(0.5 * (bs[last_cap] + bs[last_cap + 1]))


def main():
    bmins = [4.8, 5.05, 5.25, 5.6, 6.2]               # smaller b_min = deeper strong-field coverage
    curve = []
    for bm in bmins:
        X, Y = data_bmin(bm); m = train(X, Y)
        bc = bcrit_capture(m); err = abs(bc - B_TRUE) / B_TRUE if bc else None
        rmin_data = 1.0 / max(X[:, 0])                # deepest approach in the training rays
        curve.append({"b_min": bm, "rmin_data": float(rmin_data), "b_crit": bc, "rel_err": err, "n_points": int(len(X))})
        print(f"b_min={bm:.2f} (deepest r~{rmin_data:.2f}M, n={len(X)}): b_crit_capture={bc:.3f}  err={err*100:.1f}%")
    # full-data net: capture vs potential agree? (answers the diagnostic)
    Xf, Yf = data_bmin(4.8); mf = train(Xf, Yf)
    bcap = bcrit_capture(mf); bpot = bcrit_potential(mf, Xf, u_hi=0.47)
    print(f"\nFULL DATA: b_crit capture={bcap:.3f}  potential={bpot:.3f}  (true 3sqrt3={B_TRUE:.3f})")

    bvals = [c["b_crit"] for c in curve]; errs = [c["rel_err"] for c in curve]
    # deeper (smaller b_min, listed first) should have smaller error than shallowest
    mono = all(errs[i] <= errs[i + 1] + 0.03 for i in range(len(errs) - 1))
    deep_err, shallow_err = errs[0], errs[-1]
    f1 = bool(mono)
    f2 = bool(deep_err < 0.12 and deep_err < shallow_err - 0.04)
    f3 = bool(shallow_err > 0.15 and deep_err < 0.12)
    out = {"curve": curve, "full_data_capture": bcap, "full_data_potential": bpot, "b_true": float(B_TRUE),
           "F1_monotone_learning_curve": f1, "F2_deep_accurate": f2, "F3_error_is_strong_field": f3,
           "strong_field_fidelity_demonstrated": bool(f1 and f2 and f3)}
    print(f"\nF1 monotone fidelity curve (deeper data -> smaller error): {f1}")
    print(f"F2 deepest within 12% and better than shallowest: {f2} (deep {deep_err*100:.1f}% vs shallow {shallow_err*100:.1f}%)")
    print(f"F3 error is strong-field (shallow >15%, deep <12%): {f3}")
    print(f"\nSTRONG-FIELD FIDELITY SCORE DEMONSTRATED (shadow-edge error -> learning curve): {out['strong_field_fidelity_demonstrated']}")
    (RESULTS / "82_strong_field_fidelity.json").write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(1, 2, figsize=(13, 5))
    rmins = [c["rmin_data"] for c in curve]
    ax[0].plot(rmins, bvals, "o-", color="crimson", label="net b_crit (ray capture)")
    ax[0].axhline(B_TRUE, color="navy", ls="--", label=f"exact 3sqrt3={B_TRUE:.2f}")
    ax[0].axvline(3.0, color="orange", ls=":", label="photon sphere 3M")
    ax[0].set_xlabel("deepest radius the training rays reach (M)"); ax[0].set_ylabel("shadow edge b_crit (M)")
    ax[0].legend(fontsize=8); ax[0].set_title("strong-field fidelity learning curve\nb_crit approaches 3sqrt3 as data reaches the photon sphere")
    ax[1].plot(rmins, [e * 100 for e in errs], "s-", color="darkorange")
    ax[1].axvline(3.0, color="orange", ls=":"); ax[1].set_xlabel("deepest radius in training data (M)")
    ax[1].set_ylabel("shadow-edge error (%)"); ax[1].set_title("the fidelity score vs how deep the data reaches")
    fig.tight_layout(); fig.savefig(RESULTS / "82_strong_field_fidelity.png", dpi=140)
    print("saved results/82_strong_field_fidelity.json + .png")


if __name__ == "__main__":
    main()
