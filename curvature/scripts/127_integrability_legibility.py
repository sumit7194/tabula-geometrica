"""Step 127 — A10 (for TheBridge): does a learned geometry become LEGIBLE iff the metric is INTEGRABLE?

TheBridge's SISTER_REQUESTS A10 (well-posed reframe): tie tabula's geometrization/LEGIBILITY probe to leg O's catalog
INTEGRABILITY survey -- run the emit-or-certify (legibility) instrument on observations (geodesics) from each catalog
metric, report per-metric "geometrizes/legible", and the bridge correlates it against the "admits a Killing tensor
(integrable)" column. This script is that tabula deliverable; the bridge reads its JSON (read-only, repos independent).

We already showed legible<->integrable PIECEWISE: 92 (Kerr Carter), 97 (Kerr-de Sitter rational Carter), 99 (Kerr-
Newman survives vs bumpy breaks), 85 (chaos -> no invariant). This unifies them into ONE catalog survey on ONE
emit-or-certify pipeline (reusing 99's conserved/heldout) + adds Taub-NUT (web-verified integrable: shares Kerr's
hidden symmetry via a 2nd-rank Killing tensor; NUT gravitomagnetic shift L -> L - 2n cos(theta)).

Faithful Staeckel-separable Kerr-like geodesic Hamiltonian (the structure giving Carter), parameterized:
  Q   = charge (Kerr-Newman; Delta += Q^2)                            -- separability preserved (integrable)
  Lam = cosmological radial term (Kerr-de Sitter-like; r-only)         -- separable (integrable)
  nut = NUT charge (Taub-NUT; angular L -> L - 2 nut cos theta)        -- separable (integrable)
  eps = quadrupole bump eps (r-R)^2 cos^2(theta)  (NON-separable r-theta coupling) -- breaks Carter (NON-integrable)
Separation constant (Carter): K = 1/2 p_th^2 + 1/2 (L - 2 nut cos th)^2/sin^2 th - A^2 H0 cos^2 th (alive iff eps=0).

Pre-reg (2026-06-25):
  G1 INTEGRABLE -> EMIT (legible): Kerr, Kerr-Newman, Kerr-de Sitter, Taub-NUT each EMIT a verified 2nd invariant
     (engine held-out var-ratio < 1e-4) AND the known Carter is conserved (drift < 1e-2).
  G2 NON-INTEGRABLE -> CERTIFY (illegible): the bumpy metrics emit NO exact low-degree invariant (engine held-out
     >> integrable cases; known-Carter drift large) -- the KAM-lingering approximate invariant is not exact.
  G3 CORRELATION (the bridge's A10): "legible" (emit) <-> "integrable" (Killing tensor) agrees for ALL catalog metrics.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from curvlib import RESULTS
from importlib import import_module
s99 = import_module("99_deformed_metrics")          # reuse the validated emit-or-certify engine (conserved, heldout)

np.seterr(all="ignore")
A, R, KAP, L, H0, U0, DT = 0.6, 6.0, 0.6, 1.0, 0.2, 3.0, 0.01


def deriv(r, th, pr, pth, Q, eps, Lam, nut):
    Sig = r ** 2 + A ** 2 * np.cos(th) ** 2
    Del = r ** 2 - 2 * r + A ** 2 + Q ** 2
    u = L - 2 * nut * np.cos(th)                                    # NUT gravitomagnetic shift (Taub-NUT)
    N = 0.5 * Del * pr ** 2 + (H0 * r ** 2 + 0.5 * KAP * (r - R) ** 2 - U0 + Lam * r ** 2) \
        + 0.5 * pth ** 2 + 0.5 * u ** 2 / np.sin(th) ** 2 + eps * (r - R) ** 2 * np.cos(th) ** 2
    Hval = N / Sig
    dN_r = 0.5 * (2 * r - 2) * pr ** 2 + 2 * H0 * r + KAP * (r - R) + 2 * Lam * r + eps * 2 * (r - R) * np.cos(th) ** 2
    dN_th = u * (2 * nut * np.sin(th) ** 2 - u * np.cos(th)) / np.sin(th) ** 3 \
        + eps * (r - R) ** 2 * (-np.sin(2 * th))
    dSig_r = 2 * r; dSig_th = -A ** 2 * np.sin(2 * th)
    rdot = Del * pr / Sig; thdot = pth / Sig
    prdot = -(dN_r - Hval * dSig_r) / Sig; pthdot = -(dN_th - Hval * dSig_th) / Sig
    return rdot, thdot, prdot, pthdot, Hval


def rollout(r, th, pr, pth, p, nstep=2600):
    out = []
    for k in range(nstep):
        k1 = deriv(r, th, pr, pth, *p)
        k2 = deriv(r + .5 * DT * k1[0], th + .5 * DT * k1[1], pr + .5 * DT * k1[2], pth + .5 * DT * k1[3], *p)
        k3 = deriv(r + .5 * DT * k2[0], th + .5 * DT * k2[1], pr + .5 * DT * k2[2], pth + .5 * DT * k2[3], *p)
        k4 = deriv(r + DT * k3[0], th + DT * k3[1], pr + DT * k3[2], pth + DT * k3[3], *p)
        r += DT / 6 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0]); th += DT / 6 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1])
        pr += DT / 6 * (k1[2] + 2 * k2[2] + 2 * k3[2] + k4[2]); pth += DT / 6 * (k1[3] + 2 * k2[3] + 2 * k3[3] + k4[3])
        if not (R - 3 < r < R + 3) or not (0.3 < th < np.pi - 0.3):
            return None
        if k % 4 == 0 and k > 200:
            out.append([r, th, pr, pth])
    return np.array(out)


def geodesics(p, n=110, seed=0):
    Q, eps, Lam, nut = p
    rng = np.random.default_rng(seed); trajs = []; tries = 0
    while len(trajs) < n and tries < 80 * n:
        tries += 1
        r0 = R + rng.uniform(-1.5, 1.5); th0 = np.pi / 2 + rng.uniform(-0.7, 0.7); pth0 = rng.uniform(-0.6, 0.6)
        Del = r0 ** 2 - 2 * r0 + A ** 2 + Q ** 2; u0 = L - 2 * nut * np.cos(th0)
        rem = H0 * A ** 2 * np.cos(th0) ** 2 + U0 - 0.5 * KAP * (r0 - R) ** 2 - Lam * r0 ** 2 - 0.5 * pth0 ** 2 \
            - 0.5 * u0 ** 2 / np.sin(th0) ** 2 - eps * (r0 - R) ** 2 * np.cos(th0) ** 2   # = 1/2 Delta p_r^2
        if rem <= 0:
            continue
        pr0 = np.sqrt(2 * rem / Del) * rng.choice([-1, 1])
        tr = rollout(r0, th0, pr0, pth0, p)
        if tr is not None and len(tr) > 250:
            trajs.append(tr)
    if len(trajs) < 10:
        return None
    m = min(len(t) for t in trajs)
    return np.array([t[:m] for t in trajs])


def carter(T, nut):
    r, th, pr, pth = T[..., 0], T[..., 1], T[..., 2], T[..., 3]
    u = L - 2 * nut * np.cos(th)
    return 0.5 * pth ** 2 + 0.5 * u ** 2 / np.sin(th) ** 2 - A ** 2 * np.cos(th) ** 2 * H0


def lib(T):
    r, th, pr, pth = T[..., 0], T[..., 1], T[..., 2], T[..., 3]
    s2 = np.sin(th) ** 2
    F = [pth ** 2, 1 / s2, np.cos(th) ** 2, pr ** 2, (r - R) ** 2,
         np.cos(th) / s2, np.cos(th) ** 2 / s2]                    # last two: Taub-NUT (L-2n cos)^2/sin^2 expansion
    return np.stack(F, -1)


def run(p, seed=1):
    nut = p[3]
    Ttr = geodesics(p, seed=seed); Tte = geodesics(p, seed=seed + 50)
    if Ttr is None or Tte is None:
        return None
    Phitr = lib(Ttr); ev, C, mu, sd = s99.conserved(Phitr)
    Phite = lib(Tte)
    ho = s99.heldout(Phite, C[:, 0], mu, sd)                        # the single most-conserved direction (as 99)
    Kte = carter(Tte, nut)
    drift = float(np.mean([Kte[i].var() for i in range(Kte.shape[0])]) / (Kte.reshape(-1).var() + 1e-12))
    return ho, drift


def main():
    catalog = {                                                    # (Q, eps, Lam, nut), integrable (Killing tensor)?
        "Kerr": ((0.0, 0.0, 0.0, 0.0), True),
        "Kerr-Newman": ((0.5, 0.0, 0.0, 0.0), True),
        "Kerr-de Sitter": ((0.0, 0.0, 0.03, 0.0), True),
        "Taub-NUT": ((0.0, 0.0, 0.0, 0.3), True),
        "bumpy": ((0.0, 0.35, 0.0, 0.0), False),
        "bumpy-strong": ((0.0, 0.7, 0.0, 0.0), False),
    }
    rows = {}
    for name, (p, integ) in catalog.items():
        res = run(p)
        if res is None:
            rows[name] = {"integrable": integ, "engine_heldout": None, "carter_drift": None, "legible": None}
            print(f"{name:16s}: no trajectories (skip)"); continue
        ho, drift = res
        legible = bool(ho < 1e-4 and drift < 1e-2)
        rows[name] = {"integrable": integ, "engine_heldout": ho, "carter_drift": drift, "legible": legible}
        dec = "EMIT (legible)" if legible else "CERTIFY (no exact low-degree invariant)"
        print(f"{name:16s}: integrable={integ!s:5s} | engine held-out {ho:.2e} | Carter drift {drift:.2e} -> {dec}")

    valid = {k: v for k, v in rows.items() if v["legible"] is not None}
    g1 = bool(all(v["legible"] for k, v in valid.items() if v["integrable"]))
    g2 = bool(all(not v["legible"] for k, v in valid.items() if not v["integrable"]))
    g3 = bool(all(v["legible"] == v["integrable"] for v in valid.values()))
    out = {"catalog": rows, "G1_integrable_emit": g1, "G2_nonintegrable_certify": g2,
           "G3_legible_iff_integrable": g3, "legibility_tracks_integrability": bool(g1 and g2 and g3),
           "for_bridge": "correlate each metric's 'legible' (this JSON) against leg O's 'KY-integrable' column (A10)",
           "verdict": ("A10 (legibility <-> integrability) CONFIRMED on the catalog: the emit-or-certify legibility "
                       "instrument EMITS a verified hidden invariant (the Carter constant) for every INTEGRABLE metric "
                       "(Kerr, Kerr-Newman, Kerr-de Sitter, Taub-NUT) and CERTIFIES no exact low-degree invariant for "
                       "the NON-integrable (bumpy) metrics -- 'a learned geometry becomes legible IFF the metric is "
                       "integrable (admits a Killing tensor)'. Tabula deliverable for TheBridge: correlate this "
                       "per-metric 'legible' column against leg O's integrability column."
                       if (g1 and g2 and g3) else "PARTIAL -- see per-metric numbers (honest).")}
    print(f"\nG1 integrable->emit: {g1} | G2 non-integrable->certify: {g2} | G3 legible<->integrable: {g3}")
    print(f"LEGIBILITY TRACKS INTEGRABILITY (A10): {out['legibility_tracks_integrability']}")
    (RESULTS / "127_integrability_legibility.json").write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(figsize=(9, 5))
    names = [k for k in valid]; hos = [valid[k]["engine_heldout"] for k in names]
    cols = ["seagreen" if valid[k]["integrable"] else "crimson" for k in names]
    ax.bar(range(len(names)), np.clip(hos, 1e-30, None), color=cols, log=True)
    ax.axhline(1e-4, ls="--", c="k", lw=0.7, label="legible threshold (1e-4)")
    ax.set_xticks(range(len(names))); ax.set_xticklabels(names, rotation=20, ha="right")
    ax.set_ylabel("engine best invariant: held-out var-ratio (log)")
    ax.set_title("A10 · legible (emit) iff integrable: green=integrable (emit), red=non-integrable (certify)")
    ax.legend(fontsize=8); fig.tight_layout(); fig.savefig(RESULTS / "127_integrability_legibility.png", dpi=140)
    print("saved results/127_integrability_legibility.json + .png")


if __name__ == "__main__":
    main()
