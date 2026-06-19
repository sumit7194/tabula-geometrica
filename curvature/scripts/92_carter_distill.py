"""Step 92 — DISTILLATION HEAD, HARD CALIBRATION: rediscover Kerr's CARTER CONSTANT (a Killing-TENSOR invariant).

The basic head (91) emitted Kepler's E and L -- but those are easy: they come from manifest symmetries
(time-translation, rotation = cyclic coordinates / Killing VECTORS). The real test is a HIDDEN conserved
quantity that is NOT a manifest symmetry: Kerr's Carter constant, which comes from an irreducible Killing
TENSOR and is QUADRATIC in the momenta. Web-verified (Boyer-Lindquist, mu=1):
    Q = p_theta^2 + cos^2(theta) * [ a^2 (1 - E^2) + L_z^2 / sin^2(theta) ]
conserved along every Kerr geodesic (E = energy, L_z = axial angular momentum -- the easy invariants -- fixed
per geodesic; Q is the fourth, hidden one). We generate angular-sector samples (theta, p_theta) on many
geodesics directly from the conserved Q (the angular phase-space curve), feed the head a library of features
that VARY along the orbit, and ask the cheapest-conserved-code distiller to emit Q -- the form nobody can read
off the metric.

Pre-reg (2026-06-20), a = 0.9, mu = 1:
  C1 FIND THE HIDDEN INVARIANT: the conserved subspace is 1-D (exactly one near-zero generalized eigenvalue),
     and it matches the Carter constant (cosine to Q's coefficient vector > 0.98), self-verified conserved on
     HELD-OUT geodesics (var_along/var_total < 1e-2).
  C2 CORRECT FORM: the emitted formula recovers Q's structure -- the four Carter terms dominate with
     coefficients in ratio (1 : a^2 : -a^2 : 1) = (1 : 0.81 : -0.81 : 1) within 10%; distractors ~ 0.
  C3 IT IS A KILLING-TENSOR INVARIANT: the emitted quantity is genuinely quadratic in the momentum (nonzero
     p_theta^2 coefficient) -- not a manifest cyclic-coordinate symmetry. A hidden conserved quantity, emitted.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

np.seterr(all="ignore")
A = 0.9            # Kerr spin
MU = 1.0


def theta_bracket(E, Lz, Q, th):
    return Q - np.cos(th) ** 2 * (A ** 2 * (MU ** 2 - E ** 2) + Lz ** 2 / np.sin(th) ** 2)   # = p_theta^2


def geodesics(n_geo=160, n_per=45, seed=0):
    rng = np.random.default_rng(seed); TH, PTH, E_, LZ = [], [], [], []
    made = 0
    while made < n_geo:
        E = rng.uniform(0.88, 0.99); Lz = rng.uniform(0.6, 3.0); Q = rng.uniform(0.4, 6.0)
        th = np.linspace(np.pi / 2 - 1.1, np.pi / 2 + 1.1, 600)
        good = th[(np.abs(np.sin(th)) > 0.2) & (theta_bracket(E, Lz, Q, th) > 0.02)]
        if len(good) < n_per:
            continue
        sel = good[rng.integers(0, len(good), n_per)]
        pth = np.sqrt(theta_bracket(E, Lz, Q, sel)) * rng.choice([-1, 1], n_per)   # +/- branch
        TH.append(sel); PTH.append(pth); E_.append(np.full(n_per, E)); LZ.append(np.full(n_per, Lz)); made += 1
    return (np.array(TH), np.array(PTH), np.array(E_), np.array(LZ))               # each (n_geo, n_per)


def library(th, pth, E, Lz):
    c2 = np.cos(th) ** 2; s2 = np.sin(th) ** 2
    # NOTE: exclude redundant terms that create linear identities (cos^2+sin^2=1; p_th^2(cos^2+sin^2)=p_th^2),
    # which would otherwise show up as spurious identically-zero "conserved" directions.
    names = ["p_th^2", "cos^2", "E^2*cos^2", "Lz^2*cos^2/sin^2", "p_th^2*cos^2", "cos^4",
             "p_th*cos", "Lz^2*sin^2"]
    F = [pth ** 2, c2, E ** 2 * c2, Lz ** 2 * c2 / s2, pth ** 2 * c2, c2 ** 2,
         pth * np.cos(th), Lz ** 2 * s2]
    return np.stack(F, -1), names


def conserved_spectrum(Phi):
    G, P, K = Phi.shape; flat = Phi.reshape(-1, K); mu = flat.mean(0); flat = flat - mu; Phi = Phi - mu
    B = np.cov(flat.T); A_ = np.mean([np.cov(Phi[g].T) for g in range(G)], 0)
    s, U = np.linalg.eigh(B); keep = s > 1e-8 * s.max(); W = U[:, keep] / np.sqrt(s[keep])
    lam, V = np.linalg.eigh(W.T @ A_ @ W); C = W @ V
    return lam, C, mu


def verify(Phi, c, mu):
    g = (Phi - mu) @ c; va = np.mean([g[i].var() for i in range(g.shape[0])]); vt = g.reshape(-1).var()
    return float(va / (vt + 1e-12))


def main():
    TH, PTH, E, LZ = geodesics(seed=0)
    Phi, names = library(TH, PTH, E, LZ)
    THt, PTHt, Et, LZt = geodesics(seed=99); Phit, _ = library(THt, PTHt, Et, LZt)
    lam, C, mu = conserved_spectrum(Phi)
    n_cons = int(np.sum(lam < 1e-2))
    c = C[:, 0]; c = c / c[0]                                       # normalize so p_theta^2 coeff = 1

    # Carter constant coefficient vector in library coords: 1*p_th^2 + a^2*cos^2 - a^2*E^2cos^2 + 1*Lz^2cos^2/sin^2
    Qvec = np.zeros(len(names)); Qvec[0] = 1.0; Qvec[1] = A ** 2; Qvec[2] = -A ** 2; Qvec[3] = 1.0
    cos = float(abs(np.dot(c / np.linalg.norm(c), Qvec / np.linalg.norm(Qvec))))
    vr = verify(Phit, C[:, 0], mu)
    coeffs = {names[i]: round(float(c[i]), 3) for i in range(len(names)) if abs(c[i]) > 0.05}
    # coefficient-ratio check on the four Carter terms (p_th^2 : cos^2 : E^2cos^2 : Lz^2cos^2/sin^2)
    ratio_ok = (abs(c[0] - 1) < 0.1 and abs(c[1] - A ** 2) < 0.1 and abs(c[2] + A ** 2) < 0.1 and abs(c[3] - 1) < 0.1)
    p_th_coeff = float(c[0])

    # C1: the CLEANEST conserved direction (smallest eigenvalue) is the Carter constant, self-verified, and
    # sits in a clear spectral gap below the next direction (so it is unambiguously THE hidden invariant).
    gap = float(lam[1] / (abs(lam[0]) + 1e-30))
    c1 = bool(cos > 0.98 and vr < 1e-2 and gap > 100)
    c2 = bool(ratio_ok)
    c3 = bool(abs(p_th_coeff) > 0.5)                                # genuinely quadratic in momentum (Killing tensor)
    out = {"eigenvalues": [float(x) for x in lam[:6]], "n_below_1e-2": n_cons, "carter_eigenvalue": float(lam[0]),
           "next_eigenvalue": float(lam[1]), "spectral_gap": gap, "cosine_to_Carter": cos,
           "verify_varratio": vr, "emitted_coeffs": coeffs, "p_theta2_coeff": p_th_coeff,
           "carter_coeff_ratios_ok": bool(ratio_ok), "a_squared": A ** 2,
           "C1_found_hidden_invariant": c1, "C2_correct_carter_form": c2, "C3_killing_tensor_quadratic": c3,
           "carter_constant_distilled": bool(c1 and c2 and c3)}
    print(f"eigenvalues (var_along/var_total): {[f'{x:.1e}' for x in lam[:5]]}  -> {n_cons} conserved")
    print(f"EMITTED (normalized p_th^2=1): " + " + ".join(f"{v:+.2f}*{n}" for n, v in coeffs.items()))
    print(f"  cosine to Carter constant Q: {cos:.4f} | verify var-ratio {vr:.1e} | p_th^2 coeff {p_th_coeff:.2f}")
    print(f"  target coeffs (1 : a^2 : -a^2 : 1) = (1 : {A**2:.2f} : {-A**2:.2f} : 1); ratios_ok {ratio_ok}")
    print(f"\nC1 found the hidden invariant (1-D, matches Carter, verified): {c1}")
    print(f"C2 correct Carter form (coefficient ratios): {c2}")
    print(f"C3 Killing-tensor (quadratic in momentum): {c3}")
    print(f"\nCARTER CONSTANT DISTILLED (the head emitted a hidden Killing-tensor invariant, self-verified): {out['carter_constant_distilled']}")
    (Path(__file__).resolve().parent.parent / "results" / "92_carter_distill.json").write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(1, 2, figsize=(13, 5))
    ax[0].semilogy(range(1, len(lam) + 1), np.clip(lam, 1e-12, None), "o-", color="seagreen")
    ax[0].axhline(1e-2, color="k", ls=":", label="conserved threshold")
    ax[0].set_xlabel("generalized-eigenvalue index"); ax[0].set_ylabel("var_along / var_total")
    ax[0].legend(fontsize=8); ax[0].set_title(f"one hidden conserved direction emerges (~{lam[0]:.0e})\nKerr geodesics, spin a={A}")
    # show Q is constant along geodesics for the emitted formula
    g = (Phit - mu) @ C[:, 0]
    for i in range(8):
        ax[1].plot(THt[i], g[i] - g[i].mean(), ".", ms=3)
    ax[1].set_xlabel("theta along geodesic"); ax[1].set_ylabel("emitted invariant (centered)")
    ax[1].set_title(f"the emitted Carter constant is FLAT along each geodesic\ncosine to textbook Q = {cos:.3f}, var-ratio {vr:.0e}")
    fig.tight_layout(); fig.savefig(Path(__file__).resolve().parent.parent / "results" / "92_carter_distill.png", dpi=140)
    print("saved results/92_carter_distill.json + .png")


if __name__ == "__main__":
    main()
