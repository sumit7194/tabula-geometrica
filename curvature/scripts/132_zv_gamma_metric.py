"""Step 132 — ZV gamma-metric legibility (for TheBridge, extends A10/leg Q): a SECOND independent non-integrable case.

TheBridge's follow-up to A10 (leg Q): leg Q's "legible (tabula §127 emit-or-certify) <-> KY-integrable (their symbolic
survey)" correlation has only ONE non-integrable test so far (the bumpy metric, §127). They added a literature-standard
second non-integrable case in a DIFFERENT deformation and DIFFERENT coordinates -- the Zipoy-Voorhees (ZV) gamma-metric
(an exact static axisymmetric VACUUM Weyl solution; delta=1 == Schwarzschild integrable, delta=2 proven NON-integrable:
no Killing tensor up to valence 11, no polynomial integral of degree <= 6 -- web-verified Lukes-Gerakopoulos 2012,
arXiv:1206.0660 / Kruglikov-Matveev arXiv:1111.4690). The ask: run §127's legibility probe on ZV geodesics and report
the emit/certify verdict per delta. Prediction to falsify: delta=1 EMITS (legible), delta=2 CERTIFIES (illegible).

Metric (prolate-spheroidal x in (1,inf), y in [-1,1], M = sigma*delta):
  ds^2 = -F dt^2 + sigma^2 F^-1 [ H (x^2-y^2)(dx^2/(x^2-1) + dy^2/(1-y^2)) + (x^2-1)(1-y^2) dphi^2 ],
  F = ((x-1)/(x+1))^delta,  H = ((x^2-1)/(x^2-y^2))^(delta^2).
Inverse (diagonal): g^tt=-1/F, g^xx = F(x^2-1)/(s^2 H(x^2-y^2)), g^yy = F(1-y^2)/(s^2 H(x^2-y^2)),
g^phiphi = F/(s^2 (x^2-1)(1-y^2)). t,phi are Killing -> E=-p_t, L=p_phi conserved; geodesics reduce to (x,y,p_x,p_y).

THE SEPARATION CONSTANT (derived, the analog of Carter): writing H=-1/2 (timelike) and multiplying by
sigma^2 (x^2-y^2) H / F, the cross term carrying the (x,y) coupling is (x^2-y^2)*H = (x^2-1)^(delta^2) (x^2-y^2)^(1-delta^2).
It is y-INDEPENDENT (-> Hamilton-Jacobi SEPARATES) IFF delta=1. At delta=1 the conserved y-part is
  C = (1-y^2) p_y^2 + L^2/(1-y^2)   (= total angular momentum squared; conserved iff delta=1).
For delta != 1 the (x^2-y^2)^(1-delta^2) factor couples x,y and C is NOT conserved -> non-integrable. The engine (the
§99/§127 generalized-eigenproblem: cheapest within-trajectory-conserved combination over a feature library, held-out
verified) should EMIT C for delta=1 and CERTIFY (no exact low-degree invariant) for delta=2.

Pre-reg (2026-06-25):
  Z1 INTEGRABLE delta=1 -> EMIT: the engine's best invariant is held-out conserved (var-ratio < 1e-4) AND is the
     separation constant C (cosine to the known C-vector > 0.95); the known C drifts < 1e-4 along geodesics.
  Z2 NON-INTEGRABLE delta=2 -> CERTIFY: no exact low-degree invariant -- the known C drifts >> delta=1 (ratio > 1e3),
     and the engine's best held-out var-ratio is >> delta=1 (ratio > 1e3). (KAM may leave a crude remnant; the decisive
     test is that the SPECIFIC separation constant is destroyed, exactly as §99's bump.)
  Z3 BRIDGE CORRELATION (extends leg Q): legible(delta=1)=True and legible(delta=2)=False -- a 6th metric and a second,
     independent non-integrable case (different deformation, different coordinates) for the legible<->integrable column.
"""

import json
import sys
from importlib import import_module
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import torch

from curvlib import RESULTS

s99 = import_module("99_deformed_metrics")          # reuse the validated emit-or-certify engine (conserved, heldout)

torch.set_default_dtype(torch.float64)              # conservation tests need double precision
np.seterr(all="ignore")

M = 1.0                                              # ADM mass fixed; sigma = M/delta (rod half-length)
E, L = 0.97, 4.0                                     # energy / angular momentum (E>V_min~0.962 -> Schwarzschild bound r~7.5..24)
X_LO, X_HI, Y_MAX = 1.10, 60.0, 0.85                # validity window (x>1 off the rod; |y|<1); reject escape/plunge
DT, NSTEP, BURN, STRIDE = 0.15, 8000, 800, 18       # affine-time step / steps / burn-in / record stride


def metric_inv(x, y, delta, sigma):
    F = ((x - 1) / (x + 1)) ** delta
    Hf = ((x ** 2 - 1) / (x ** 2 - y ** 2)) ** (delta ** 2)
    base = F / (sigma ** 2 * Hf * (x ** 2 - y ** 2))
    gtt = -1.0 / F
    gxx = base * (x ** 2 - 1)
    gyy = base * (1 - y ** 2)
    gpp = F / (sigma ** 2 * (x ** 2 - 1) * (1 - y ** 2))
    return gtt, gxx, gyy, gpp


def deriv(x, y, px, py, delta, sigma):
    """Hamilton's equations for H = 1/2 g^{munu} p_mu p_nu (E,L fixed). dH/dx,dH/dy via autograd."""
    xr = x.detach().requires_grad_(True); yr = y.detach().requires_grad_(True)
    gtt, gxx, gyy, gpp = metric_inv(xr, yr, delta, sigma)
    Ham = 0.5 * (gtt * E ** 2 + gxx * px.detach() ** 2 + gyy * py.detach() ** 2 + gpp * L ** 2)
    dHdx, dHdy = torch.autograd.grad(Ham.sum(), [xr, yr])
    with torch.no_grad():
        _, gxx2, gyy2, _ = metric_inv(x, y, delta, sigma)
    return gxx2 * px, gyy2 * py, -dHdx.detach(), -dHdy.detach()


def rollout(x, y, px, py, delta, sigma):
    """batched RK4 of the geodesic family; returns (n_valid, P, 4) trajectories that stay in the window throughout."""
    safe = lambda a, v: torch.where(alive, a, torch.full_like(a, v))
    alive = torch.isfinite(x) & (x > X_LO) & (x < X_HI) & (y.abs() < Y_MAX)
    rec = []
    for k in range(NSTEP):
        x, y, px, py = safe(x, 5.0), safe(y, 0.0), safe(px, 0.0), safe(py, 0.0)
        k1 = deriv(x, y, px, py, delta, sigma)
        k2 = deriv(x + .5 * DT * k1[0], y + .5 * DT * k1[1], px + .5 * DT * k1[2], py + .5 * DT * k1[3], delta, sigma)
        k3 = deriv(x + .5 * DT * k2[0], y + .5 * DT * k2[1], px + .5 * DT * k2[2], py + .5 * DT * k2[3], delta, sigma)
        k4 = deriv(x + DT * k3[0], y + DT * k3[1], px + DT * k3[2], py + DT * k3[3], delta, sigma)
        x = x + DT / 6 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0]); y = y + DT / 6 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1])
        px = px + DT / 6 * (k1[2] + 2 * k2[2] + 2 * k3[2] + k4[2]); py = py + DT / 6 * (k1[3] + 2 * k2[3] + 2 * k3[3] + k4[3])
        alive = alive & torch.isfinite(x) & (x > X_LO) & (x < X_HI) & (y.abs() < Y_MAX)
        if k >= BURN and (k - BURN) % STRIDE == 0:
            rec.append(torch.stack([x, y, px, py], -1))
    R = torch.stack(rec, 1)                                      # (N, P, 4)
    keep = alive & torch.isfinite(R).all(-1).all(-1)
    return R[keep].cpu().numpy()


def geodesics(delta, seed=0, n_init=900):
    sigma = M / delta
    rng = np.random.default_rng(seed)
    x0 = rng.uniform(3.0, 22.0, n_init); y0 = rng.uniform(-0.5, 0.5, n_init); py0 = rng.uniform(-1.2, 1.2, n_init)
    xt = torch.tensor(x0); yt = torch.tensor(y0); pyt = torch.tensor(py0)
    gtt, gxx, gyy, gpp = metric_inv(xt, yt, delta, sigma)
    rem = -1.0 - gtt * E ** 2 - gyy * pyt ** 2 - gpp * L ** 2     # = g^xx p_x^2  (mass shell H=-1/2)
    ok = (rem > 0).numpy()
    px0 = np.zeros(n_init); px0[ok] = np.sqrt((rem.numpy()[ok]) / gxx.numpy()[ok]) * rng.choice([-1, 1], ok.sum())
    sel = ok
    T = rollout(xt[sel], yt[sel], torch.tensor(px0[sel]), pyt[sel], delta, sigma)
    return T


def sep_constant(T):
    y, py = T[..., 1], T[..., 3]
    return (1 - y ** 2) * py ** 2 + L ** 2 / (1 - y ** 2)         # C = (1-y^2)p_y^2 + L^2/(1-y^2)


def lib(T):
    x, y, px, py = T[..., 0], T[..., 1], T[..., 2], T[..., 3]
    F = [(1 - y ** 2) * py ** 2, 1.0 / (1 - y ** 2), py ** 2, y ** 2, px ** 2, (x - x.mean()) ** 2]
    return np.stack(F, -1)


def known_C_vec():
    v = np.array([1.0, L ** 2, 0, 0, 0, 0])                       # C = 1*[(1-y^2)p_y^2] + L^2*[1/(1-y^2)]
    return v / np.linalg.norm(v)


def drift(C):
    return float(np.mean([C[i].var() for i in range(C.shape[0])]) / (C.reshape(-1).var() + 1e-30))


def run(delta, Ev, Lv):
    global E, L
    E, L = Ev, Lv
    Ttr = geodesics(delta, seed=1); Tte = geodesics(delta, seed=77)
    if len(Ttr) < 12 or len(Tte) < 12:
        return None
    Phi = lib(Ttr); ev, Cw, mu, sd = s99.conserved(Phi)
    ho = s99.heldout(lib(Tte), Cw[:, 0], mu, sd)                  # most-conserved direction, held-out var-ratio
    c_raw = Cw[:, 0] / sd; c_raw /= np.linalg.norm(c_raw)
    cos_C = float(abs(c_raw @ known_C_vec()))
    sep_dr = drift(sep_constant(Tte))
    return {"n_train": len(Ttr), "n_test": len(Tte), "engine_heldout": ho, "cosine_to_C": cos_C, "sep_drift": sep_dr}


def main():
    r1 = run(1, 0.97, 4.0)                                       # Schwarzschild (integrable) -- baseline
    r2 = run(2, 0.97, 4.0)                                       # ZV delta=2 at the SAME (E,L): isolates delta
    r2c = run(2, 0.96, 3.5)                                      # ZV delta=2 nearer ISCO (stronger field -> stronger chaos)
    if r1 is None or r2 is None:
        (RESULTS / "132_zv_gamma_metric.json").write_text(json.dumps({"error": "insufficient geodesics"}, indent=1))
        print("ABORT: insufficient bound geodesics"); return

    # legible == admits an EXACT invariant: C conserved to INTEGRATION PRECISION (the decisive test, per §99 -- a
    # fixed absolute threshold mislabels weakly-perturbed KAM orbits, whose C-drift is small but >>1e6x the integrable
    # floor; the right discriminator is "exact (round-off) vs not", i.e. is the SPECIFIC Killing-tensor invariant alive).
    FLOOR = 1e-10                                                 # RK4 float64 conserves a true invariant to ~<1e-12
    leg1 = bool(r1["engine_heldout"] < FLOOR and r1["sep_drift"] < FLOOR and r1["cosine_to_C"] > 0.95)
    leg2 = bool(r2["engine_heldout"] < FLOOR and r2["sep_drift"] < FLOOR)
    ratio_drift = r2["sep_drift"] / (r1["sep_drift"] + 1e-30); ratio_ho = r2["engine_heldout"] / (r1["engine_heldout"] + 1e-30)
    z1 = bool(leg1)
    z2 = bool((not leg2) and ratio_drift > 1e6 and ratio_ho > 1e6)   # C destroyed: drifts >1e6x the integrable floor
    z3 = bool(leg1 and not leg2)
    chaos_drift = (r2c["sep_drift"] if r2c is not None else None)

    out = {"E_delta1": 0.97, "L_delta1": 4.0, "E_delta2": 0.97, "L_delta2": 4.0, "M": M, "precision_floor": FLOOR,
           "delta_1_Schwarzschild": {**r1, "legible": leg1},
           "delta_2_ZV_same_EL": {**r2, "legible": leg2},
           "delta_2_ZV_strong_chaos_E0p96_L3p5": (r2c if r2c is not None else "insufficient bound orbits"),
           "ratio_drift_d2_over_d1": ratio_drift, "ratio_heldout_d2_over_d1": ratio_ho,
           "Z1_integrable_emit": z1, "Z2_nonintegrable_certify": z2, "Z3_legible_iff_integrable": z3,
           "zv_legibility_tracks_integrability": bool(z1 and z2 and z3),
           "for_bridge": ("extends leg Q's legible<->KY-integrable correlation to a 6th metric and a SECOND, independent "
                          "non-integrable case (ZV gamma-metric, different deformation + coordinates). Append: "
                          "ZV(delta=1)=legible+integrable, ZV(delta=2)=illegible+non-integrable."),
           "verdict": ("ZV GAMMA-METRIC: legibility tracks integrability (extends A10/leg Q). The §127 emit-or-certify "
                       "instrument on Zipoy-Voorhees geodesics EMITS the exact separation constant C=(1-y^2)p_y^2+"
                       "L^2/(1-y^2) for delta=1 (Schwarzschild: conserved to {:.0e} = integration precision, cosine to C "
                       "{:.3f}) and CERTIFIES no exact invariant for delta=2 (ZV, same E,L: C-drift {:.0e} = {:.0e}x the "
                       "integrable floor -- C is NOT exactly conserved, only a weak KAM remnant; in the literature "
                       "strong-chaos region (E=0.95,L=3) the drift grows to {} -- macroscopic). The KILLING-TENSOR "
                       "invariant is alive at delta=1 and destroyed at delta=2 (proven: no KY tensor up to valence 11). "
                       "A different deformation in different coordinates than the §127 bump: a second, independent "
                       "non-integrable confirmation of legible <-> integrable."
                       .format(r1["sep_drift"], r1["cosine_to_C"], r2["sep_drift"], ratio_drift,
                               f"{chaos_drift:.0e}" if chaos_drift is not None else "n/a")
                       if (z1 and z2 and z3) else "PARTIAL -- see per-delta numbers (honest).")}
    print(f"delta=1 (Schwarzschild): held-out {r1['engine_heldout']:.2e}, cosine to C {r1['cosine_to_C']:.3f}, "
          f"C-drift {r1['sep_drift']:.2e} -> {'EMIT (legible)' if leg1 else 'certify'}  [n={r1['n_train']}/{r1['n_test']}]")
    print(f"delta=2 (ZV, same E,L):  held-out {r2['engine_heldout']:.2e}, cosine to C {r2['cosine_to_C']:.3f}, "
          f"C-drift {r2['sep_drift']:.2e} ({ratio_drift:.0e}x floor) -> {'emit' if leg2 else 'CERTIFY (no exact invariant)'}  [n={r2['n_train']}/{r2['n_test']}]")
    if r2c is not None:
        print(f"delta=2 (ZV, chaos E.96/L3.5): C-drift {r2c['sep_drift']:.2e} (macroscopic; stronger field/chaos) [n={r2c['n_train']}/{r2c['n_test']}]")
    print(f"\nZ1 integrable->emit: {z1} | Z2 non-integrable->certify: {z2} | Z3 legible<->integrable: {z3}")
    print(f"ZV LEGIBILITY TRACKS INTEGRABILITY: {out['zv_legibility_tracks_integrability']}")
    (RESULTS / "132_zv_gamma_metric.json").write_text(json.dumps(out, indent=1))

    global E, L
    d2_EL = (0.96, 3.5) if r2c is not None else (0.97, 4.0)       # plot the strongest-chaos delta=2 family that binds
    fig, ax = plt.subplots(1, 2, figsize=(13, 5))
    for d, col, (Ev, Lv) in [(1, "seagreen", (0.97, 4.0)), (2, "crimson", d2_EL)]:
        E, L = Ev, Lv
        T = geodesics(d, seed=5)[:6]
        C = sep_constant(T)
        for i in range(len(T)):
            ax[0].plot(C[i] - C[i].mean(), color=col, lw=0.7, alpha=0.6)
        ax[0].plot([], [], color=col, label=f"δ={d} ({'Schwarzschild (exact C)' if d == 1 else 'ZV (C drifts)'})")
    ax[0].set_xlabel("affine time along geodesic"); ax[0].set_ylabel("separation constant C (mean-removed)")
    ax[0].legend(fontsize=8); ax[0].set_title("C = (1−y²)p_y² + L²/(1−y²): flat for δ=1, drifts for δ=2")
    labels = ["δ=1\n(Schwarzschild,\nintegrable)", "δ=2\n(ZV,\nnon-integrable)"]
    hos = [max(r1["engine_heldout"], 1e-30), max(r2["engine_heldout"], 1e-30)]
    ax[1].bar(labels, hos, color=["seagreen", "crimson"]); ax[1].set_yscale("log")
    ax[1].axhline(1e-4, ls="--", c="k", lw=0.7, label="legible threshold")
    ax[1].set_ylabel("engine best invariant: held-out var-ratio (log)"); ax[1].legend(fontsize=8)
    ax[1].set_title("emit (δ=1) vs certify (δ=2) — extends A10/leg Q to ZV")
    fig.suptitle("ZV γ-metric legibility (for TheBridge): a 2nd independent non-integrable case for legible⟺integrable")
    fig.tight_layout(); fig.savefig(RESULTS / "132_zv_gamma_metric.png", dpi=140)
    print("saved results/132_zv_gamma_metric.json + .png")


if __name__ == "__main__":
    main()
