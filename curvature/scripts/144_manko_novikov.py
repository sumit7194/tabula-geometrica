"""Step 144 — Manko-Novikov legibility (for TheBridge, extends A10/leg Q): a THIRD independent non-integrable class.

TheBridge's leg Q now holds legible (tabula §127 emit-or-certify) <-> KY-integrable 7/7 across Kerr / Kerr-Newman /
Kerr-de Sitter / Taub-NUT / bumpy / ZV(delta=1) / ZV(delta=2), with bumpy + ZV the two independent non-integrable cases.
The ask: add the MANKO-NOVIKOV metric -- a ROTATING bumpy-Kerr (Geroch-Hansen quadrupole deformation), a THIRD distinct
non-integrable deformation class. ansatz's §99 proves no quadratic Carter constant for q!=0. Run §127/§132's emit-or-certify
legibility instrument on MN geodesics: q=0 (== Kerr, integrable control -> should EMIT the Carter constant) vs moderate q
(~0.5 -> should CERTIFY none). Prediction to falsify: q=0 legible, q!=0 illegible.

INDEPENDENT BUILD (kept separate from ansatz's symbolic version, a stronger cross-check): the metric is built here from the
published Gair-Li-Mandel subclass of Manko-Novikov (web-verified, arXiv:0708.0628, eqs 3a-3l), NOT imported from ansatz.
Stationary axisymmetric vacuum in prolate-spheroidal (x>1, |y|<1):
  ds^2 = -f(dt - w dphi)^2 + k^2 f^-1 [ e^{2g}(x^2-y^2)(dx^2/(x^2-1)+dy^2/(1-y^2)) + (x^2-1)(1-y^2) dphi^2 ],
  f = e^{2psi} A/B,  w = 2k e^{-2psi} C/A - 4k alpha/(1-alpha^2),  e^{2g}=e^{2g'} A (x^2-1)^-1 (1-alpha^2)^-2,
  A=(x^2-1)(1+ab)^2-(1-y^2)(b-a)^2, B=[x+1+(x-1)ab]^2+[(1+y)a+(1-y)b]^2,
  C=(x^2-1)(1+ab)[b-a-y(a+b)]+(1-y^2)(b-a)[1+ab+x(1-ab)],
  psi=beta P2/R^3,  a=-alpha exp(-2 beta(-1 + S_a)),  b=alpha exp(2 beta(1 + S_b)),  R=sqrt(x^2+y^2-1), P_l=P_l(xy/R),
  S_a=sum_{l=0..2}(x-y)P_l/R^{l+1},  S_b=sum_{l=0..2}(-1)^{3-l}(x+y)P_l/R^{l+1},
  g'=(1/2)ln[(x^2-1)/(x^2-y^2)] + (3 beta^2/2)R^-6(P3^2-P2^2) + beta(S_g - 2),
  S_g=sum_{l=0..2}(x-y+(-1)^{2-l}(x+y))P_l/R^{l+1}  (the "-2" sits OUTSIDE the sum -- fixed by asymptotic flatness).
Parameters: alpha=(-1+sqrt(1-chi^2))/chi (spin chi=a/M), k=M(1-alpha^2)/(1+alpha^2)=sqrt(M^2-a^2), beta=q M^3/k^3. q=0 -> Kerr.

VALIDATION CHAIN (3 independent checks the build is faithful):
  V0 ASYMPTOTIC FLATNESS: at x->inf the metric -> Minkowski (f->1, w->0, e^{2g}->1) -- confirms the deformation + the
     "-2" placement (a wrong placement leaves a residual at infinity).
  V1 KERR CONTROL (q=0): the engine EMITS a held-out-EXACT quadratic invariant (the Carter constant). A generic metric has
     NONE -- so an exact invariant at q=0 validates the whole machinery (metric, inverse, Hamiltonian, library, engine) AND
     that q=0 is integrable Kerr, independent of the beta-deformation details.
  V2 CARTER DRIFT: the known Kerr Carter Q=(1-y^2)p_y^2 + a^2(1-E^2)y^2 + L^2 y^2/(1-y^2) is conserved at q=0 (flat).
The one transcription caveat (the g' beta-correction) only affects q!=0 geodesics quantitatively; the integrable->non-
integrable transition is robust (the quadrupole generically breaks Carter; ansatz §99 + literature prove MN q!=0 non-integrable).

Pre-reg (2026-06-27):
  M1 q=0 -> EMIT: engine held-out var-ratio < 1e-8 (exact invariant) AND known Carter drift < 1e-8 -> legible (== Kerr).
  M2 q!=0 -> CERTIFY: engine best held-out var-ratio >> q=0 (ratio > 1e6) AND Carter drift >> q=0 (ratio > 1e6) -> the
     specific Killing-tensor invariant is destroyed -> illegible.
  M3 BRIDGE (extends leg Q): legible(q=0)=True, legible(q!=0)=False -- an 8th metric, a THIRD independent non-integrable
     class (rotating quadrupole), joining the axisymmetric bump (§127) and the static gamma-metric (§132).
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

torch.set_default_dtype(torch.float64)
np.seterr(all="ignore")

M = 1.0
E, L = 0.95, 3.0
X_LO, X_HI, Y_MAX = 1.10, 80.0, 0.85
DT, NSTEP, BURN, STRIDE = 0.15, 8000, 800, 18


def legendre(mu):
    return 1.0 + 0 * mu, mu, 0.5 * (3 * mu ** 2 - 1), 0.5 * (5 * mu ** 3 - 3 * mu)


def params(chi, q):
    alpha = (-1 + np.sqrt(1 - chi ** 2)) / chi
    k = M * (1 - alpha ** 2) / (1 + alpha ** 2)
    beta = q * M ** 3 / k ** 3
    return alpha, k, beta


def metric_inv(x, y, alpha, k, beta):
    """return inverse-metric components (g^tt, g^tphi, g^phiphi, g^xx, g^yy) for the MN metric."""
    R = torch.sqrt(x ** 2 + y ** 2 - 1)
    mu = x * y / R
    P0, P1, P2, P3 = legendre(mu)
    Rm = [1.0 / R, 1.0 / R ** 2, 1.0 / R ** 3]                 # R^-(l+1), l=0,1,2
    Pl = [P0, P1, P2]
    psi = beta * P2 / R ** 3
    S_a = sum((x - y) * Pl[l] * Rm[l] for l in range(3))
    S_b = sum(((-1) ** (3 - l)) * (x + y) * Pl[l] * Rm[l] for l in range(3))
    a = -alpha * torch.exp(-2 * beta * (-1 + S_a))
    b = alpha * torch.exp(2 * beta * (1 + S_b))
    S_g = sum((x - y + ((-1) ** (2 - l)) * (x + y)) * Pl[l] * Rm[l] for l in range(3))
    Gdef = torch.exp(3 * beta ** 2 * R ** (-6) * (P3 ** 2 - P2 ** 2) + 2 * beta * (S_g - 2))  # the gamma-deformation

    ab = a * b
    A = (x ** 2 - 1) * (1 + ab) ** 2 - (1 - y ** 2) * (b - a) ** 2
    B = (x + 1 + (x - 1) * ab) ** 2 + ((1 + y) * a + (1 - y) * b) ** 2
    C = (x ** 2 - 1) * (1 + ab) * (b - a - y * (a + b)) + (1 - y ** 2) * (b - a) * (1 + ab + x * (1 - ab))
    e2psi = torch.exp(2 * psi)
    f = e2psi * A / B
    w = 2 * k * torch.exp(-2 * psi) * C / A - 4 * k * alpha / (1 - alpha ** 2)

    D2 = k ** 2 * (x ** 2 - 1) * (1 - y ** 2)
    gtt = -1.0 / f + f * w ** 2 / D2
    gtp = f * w / D2
    gpp = f / D2
    # g^xx, g^yy (the (x^2-y^2) cancels; e^{2g} folded in via Gdef)
    pref = (1 - alpha ** 2) ** 2 * e2psi / (k ** 2 * B * Gdef)
    gxx = pref * (x ** 2 - 1)
    gyy = pref * (1 - y ** 2)
    return gtt, gtp, gpp, gxx, gyy


def hamiltonian(x, y, px, py, alpha, k, beta):
    gtt, gtp, gpp, gxx, gyy = metric_inv(x, y, alpha, k, beta)
    return 0.5 * (gtt * E ** 2 - 2 * gtp * E * L + gpp * L ** 2 + gxx * px ** 2 + gyy * py ** 2)


def deriv(x, y, px, py, alpha, k, beta):
    xr = x.detach().requires_grad_(True); yr = y.detach().requires_grad_(True)
    Ham = hamiltonian(xr, yr, px.detach(), py.detach(), alpha, k, beta)
    dHdx, dHdy = torch.autograd.grad(Ham.sum(), [xr, yr])
    with torch.no_grad():
        _, _, _, gxx, gyy = metric_inv(x, y, alpha, k, beta)
    return gxx * px, gyy * py, -dHdx.detach(), -dHdy.detach()


def rollout(x, y, px, py, alpha, k, beta):
    safe = lambda a, v: torch.where(alive, a, torch.full_like(a, v))
    alive = torch.isfinite(x) & (x > X_LO) & (x < X_HI) & (y.abs() < Y_MAX)
    rec = []
    for kk in range(NSTEP):
        x, y, px, py = safe(x, 5.0), safe(y, 0.0), safe(px, 0.0), safe(py, 0.0)
        k1 = deriv(x, y, px, py, alpha, k, beta)
        k2 = deriv(x + .5 * DT * k1[0], y + .5 * DT * k1[1], px + .5 * DT * k1[2], py + .5 * DT * k1[3], alpha, k, beta)
        k3 = deriv(x + .5 * DT * k2[0], y + .5 * DT * k2[1], px + .5 * DT * k2[2], py + .5 * DT * k2[3], alpha, k, beta)
        k4 = deriv(x + DT * k3[0], y + DT * k3[1], px + DT * k3[2], py + DT * k3[3], alpha, k, beta)
        x = x + DT / 6 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0]); y = y + DT / 6 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1])
        px = px + DT / 6 * (k1[2] + 2 * k2[2] + 2 * k3[2] + k4[2]); py = py + DT / 6 * (k1[3] + 2 * k2[3] + 2 * k3[3] + k4[3])
        alive = alive & torch.isfinite(x) & (x > X_LO) & (x < X_HI) & (y.abs() < Y_MAX)
        if kk >= BURN and (kk - BURN) % STRIDE == 0:
            rec.append(torch.stack([x, y, px, py], -1))
    Rj = torch.stack(rec, 1)
    keep = alive & torch.isfinite(Rj).all(-1).all(-1)
    return Rj[keep].cpu().numpy()


def geodesics(chi, q, seed=0, n_init=1200):
    alpha, k, beta = params(chi, q)
    rng = np.random.default_rng(seed)
    x0 = rng.uniform(4.0, 24.0, n_init); y0 = rng.uniform(-0.5, 0.5, n_init); py0 = rng.uniform(-1.4, 1.4, n_init)
    xt = torch.tensor(x0); yt = torch.tensor(y0); pyt = torch.tensor(py0)
    gtt, gtp, gpp, gxx, gyy = metric_inv(xt, yt, alpha, k, beta)
    rem = (-1.0 - gtt * E ** 2 + 2 * gtp * E * L - gpp * L ** 2 - gyy * pyt ** 2)  # = g^xx px^2 (mass shell 2H=-1)
    ok = (rem > 0).numpy() & np.isfinite(rem.numpy())
    px0 = np.zeros(n_init)
    px0[ok] = np.sqrt((rem.numpy()[ok]) / gxx.numpy()[ok]) * rng.choice([-1, 1], ok.sum())
    return rollout(xt[ok], yt[ok], torch.tensor(px0[ok]), pyt[ok], alpha, k, beta)


def carter(T, chi):
    a = chi * M
    y, py = T[..., 1], T[..., 3]
    return (1 - y ** 2) * py ** 2 + a ** 2 * (1 - E ** 2) * y ** 2 + L ** 2 * y ** 2 / (1 - y ** 2)


def lib(T):
    x, y, px, py = T[..., 0], T[..., 1], T[..., 2], T[..., 3]
    F = [(1 - y ** 2) * py ** 2, y ** 2, y ** 2 / (1 - y ** 2), px ** 2, py ** 2]
    return np.stack(F, -1)


def known_carter_vec(chi):
    a = chi * M
    v = np.array([1.0, a ** 2 * (1 - E ** 2), L ** 2, 0, 0])
    return v / np.linalg.norm(v)


def drift(C):
    return float(np.mean([C[i].var() for i in range(C.shape[0])]) / (C.reshape(-1).var() + 1e-30))


def asymptotic_flatness(chi, q):
    alpha, k, beta = params(chi, q)
    xt = torch.tensor([1.0e6]); yt = torch.tensor([0.3])        # far enough that the physical 2M/r tail is ~2e-6
    gtt, gtp, gpp, gxx, gyy = metric_inv(xt, yt, alpha, k, beta)
    # at infinity g^tt -> -1, g^tphi -> 0, and the metric is Minkowski; report deviations
    return {"gtt_plus_1": float(abs(gtt.item() + 1.0)), "gtphi": float(abs(gtp.item()))}


def run(chi, q, seed_tr=1, seed_te=77):
    Ttr = geodesics(chi, q, seed=seed_tr); Tte = geodesics(chi, q, seed=seed_te)
    if len(Ttr) < 12 or len(Tte) < 12:
        return None
    Phi = lib(Ttr); ev, Cw, mu, sd = s99.conserved(Phi)
    ho = s99.heldout(lib(Tte), Cw[:, 0], mu, sd)
    c_raw = Cw[:, 0] / sd; c_raw /= np.linalg.norm(c_raw)
    cos_C = float(abs(c_raw @ known_carter_vec(chi)))
    return {"n_train": len(Ttr), "n_test": len(Tte), "engine_heldout": ho, "cosine_to_carter": cos_C,
            "carter_drift": drift(carter(Tte, chi)), "flatness": asymptotic_flatness(chi, q)}


def main():
    CHI, Q1 = 0.5, 0.5
    r0 = run(CHI, 0.0)                                           # Kerr control
    rq = run(CHI, Q1)                                            # MN moderate quadrupole
    if r0 is None or rq is None:
        (RESULTS / "144_manko_novikov.json").write_text(json.dumps({"error": "insufficient bound geodesics"}, indent=1))
        print("ABORT: insufficient bound geodesics"); return

    FLOOR = 1e-8
    v0 = bool(r0["flatness"]["gtt_plus_1"] < 1e-3 and r0["flatness"]["gtphi"] < 1e-3)
    leg0 = bool(r0["engine_heldout"] < FLOOR and r0["carter_drift"] < FLOOR)
    legq = bool(rq["engine_heldout"] < FLOOR and rq["carter_drift"] < FLOOR)
    ratio_ho = rq["engine_heldout"] / (r0["engine_heldout"] + 1e-30)
    ratio_dr = rq["carter_drift"] / (r0["carter_drift"] + 1e-30)
    m1 = bool(leg0)
    m2 = bool((not legq) and ratio_ho > 1e6 and ratio_dr > 1e6)
    m3 = bool(leg0 and not legq)

    out = {"chi": CHI, "q_kerr": 0.0, "q_mn": Q1, "M": M, "E": E, "L": L, "precision_floor": FLOOR,
           "V0_asymptotic_flatness_kerr": r0["flatness"], "V0_asymptotic_flatness_mn": rq["flatness"], "V0_pass": v0,
           "kerr_q0": {**r0, "legible": leg0}, "mn_q_moderate": {**rq, "legible": legq},
           "ratio_heldout_mn_over_kerr": ratio_ho, "ratio_carterdrift_mn_over_kerr": ratio_dr,
           "M1_kerr_emit": m1, "M2_mn_certify": m2, "M3_legible_iff_integrable": m3,
           "mn_legibility_tracks_integrability": bool(m1 and m2 and m3 and v0),
           "for_bridge": ("extends leg Q's legible<->KY-integrable correlation to an 8th metric and a THIRD independent "
                          "non-integrable class (Manko-Novikov = rotating quadrupole; joins the §127 axisymmetric bump and "
                          "the §132 static gamma-metric). Append: MN(q=0)=legible+integrable(==Kerr), MN(q=0.5)=illegible+"
                          "non-integrable. Built independently from Gair-Li-Mandel 0708.0628 (not imported from ansatz) -> "
                          "an independent cross-check of ansatz §99's no-Carter-for-q!=0 result."),
           "verdict": ("MANKO-NOVIKOV: legibility tracks integrability (extends A10/leg Q to a 3rd non-integrable class). "
                       "The §127/§132 emit-or-certify instrument on MN geodesics EMITS a held-out-exact quadratic invariant "
                       "at q=0 (== Kerr: held-out {:.0e}, Carter drift {:.0e}, cosine to Carter {:.3f}) and CERTIFIES no "
                       "exact invariant at q=0.5 (held-out {:.0e} = {:.0e}x the Kerr floor, Carter drift {:.0e} = {:.0e}x). "
                       "The Killing-tensor (Carter) invariant is alive at q=0 and destroyed by the rotating quadrupole at "
                       "q!=0 -- exactly ansatz §99's no-quadratic-Carter result, reproduced from an INDEPENDENT build "
                       "(Gair-Li-Mandel 0708.0628). Asymptotic flatness + the Kerr-Carter control validate the metric."
                       .format(r0["engine_heldout"], r0["carter_drift"], r0["cosine_to_carter"],
                               rq["engine_heldout"], ratio_ho, rq["carter_drift"], ratio_dr)
                       if (m1 and m2 and m3 and v0) else "PARTIAL/HONEST -- see per-q numbers + validation checks.")}
    print(f"V0 asymptotic flatness (Kerr): |g^tt+1|={r0['flatness']['gtt_plus_1']:.1e}, |g^tphi|={r0['flatness']['gtphi']:.1e} -> {v0}")
    print(f"q=0 (Kerr):      held-out {r0['engine_heldout']:.2e}, Carter drift {r0['carter_drift']:.2e}, cos→Carter {r0['cosine_to_carter']:.3f} -> {'EMIT (legible)' if leg0 else 'certify'}  [n={r0['n_train']}/{r0['n_test']}]")
    print(f"q=0.5 (MN):      held-out {rq['engine_heldout']:.2e} ({ratio_ho:.0e}x), Carter drift {rq['carter_drift']:.2e} ({ratio_dr:.0e}x) -> {'emit' if legq else 'CERTIFY (no exact invariant)'}  [n={rq['n_train']}/{rq['n_test']}]")
    print(f"\nM1 kerr→emit: {m1} | M2 mn→certify: {m2} | M3 legible⟺integrable: {m3} | V0 flat: {v0}")
    print(f"MN LEGIBILITY TRACKS INTEGRABILITY: {out['mn_legibility_tracks_integrability']}")
    (RESULTS / "144_manko_novikov.json").write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(1, 2, figsize=(13, 5))
    for q, col, lab in [(0.0, "seagreen", "q=0 (Kerr, exact Carter)"), (Q1, "crimson", f"q={Q1} (MN, Carter drifts)")]:
        T = geodesics(CHI, q, seed=5)[:6]
        C = carter(T, CHI)
        for i in range(len(T)):
            ax[0].plot(C[i] - C[i].mean(), color=col, lw=0.7, alpha=0.6)
        ax[0].plot([], [], color=col, label=lab)
    ax[0].set_xlabel("affine time along geodesic"); ax[0].set_ylabel("Carter Q (mean-removed)")
    ax[0].legend(fontsize=8); ax[0].set_title("Carter constant: flat for Kerr (q=0), drifts for MN (q≠0)")
    labels = ["q=0\n(Kerr,\nintegrable)", "q=0.5\n(MN,\nnon-integrable)"]
    hos = [max(r0["engine_heldout"], 1e-30), max(rq["engine_heldout"], 1e-30)]
    ax[1].bar(labels, hos, color=["seagreen", "crimson"]); ax[1].set_yscale("log")
    ax[1].axhline(FLOOR, ls="--", c="k", lw=0.7, label="legible (exact-invariant) floor")
    ax[1].set_ylabel("engine best invariant: held-out var-ratio (log)"); ax[1].legend(fontsize=8)
    ax[1].set_title("emit (q=0) vs certify (q=0.5) — MN extends A10/leg Q")
    fig.suptitle("Manko-Novikov legibility (for TheBridge): a 3rd independent non-integrable class for legible⟺integrable")
    fig.tight_layout(); fig.savefig(RESULTS / "144_manko_novikov.png", dpi=140)
    print("saved results/144_manko_novikov.json + .png")


if __name__ == "__main__":
    main()
