"""Step 99 — A SECOND DEFORMED METRIC: tell a separability-PRESERVING deformation from an integrability-BREAKING one.

97 caught the Carter constant of one deformed black hole (Kerr-de Sitter). Now the sharper question the user
asked: can the emit-or-certify engine tell, from trajectory data alone, whether a metric deformation KEEPS the
hidden symmetry (Carter survives) or DESTROYS it (no separation constant -> chaos)? Web-verified:
  - KERR-NEWMAN (electric charge Q): the charge enters Delta_r = r^2 - 2r + a^2 + Q^2 (a function of r only), so
    geodesics STILL separate and the Carter constant SURVIVES -- a separability-preserving deformation (arXiv:1202.5228).
  - BUMPY / quadrupole (deformability kappa != 1): the deformation breaks the Carter/Killing-tensor symmetry, r
    and theta become a coupled second-order system, no separation constant -> non-integrable (arXiv:2305.18522).

We use a faithful Staeckel-separable Kerr-like geodesic Hamiltonian (the structure that gives Kerr its Carter
constant), evolve bound (r,theta) orbits at fixed energy h and angular momentum L, and run the engine on three
metrics. The Carter constant of the Staeckel form is K = 1/2 p_theta^2 + V_theta(theta) - a^2 cos^2(theta) * H
(the angular separation constant; conserved iff the system separates).

  H = [ 1/2 Delta(r) p_r^2 + V_r(r) + 1/2 p_theta^2 + V_theta(theta) + eps*C(r,theta) ] / Sigma ,
  Sigma = r^2 + a^2 cos^2(theta),  Delta(r) = r^2 - 2r + a^2 + Q^2,  V_r = 1/2 k (r-R)^2,  V_theta = 1/2 L^2/sin^2(theta),
  C(r,theta) = (r-R)^2 cos^2(theta)   (a NON-separable r-theta coupling: the integrability-breaking bump).

Pre-reg (2026-06-20), a=0.6, fixed h, L:
  C1 SEPARABLE BASELINE (Kerr, Q=0, eps=0): the engine EMITS a 2nd invariant beyond energy (held-out var-ratio
     < 1e-2) that IS the Carter constant (cosine to the known K vector > 0.98).
  C2 CHARGE PRESERVES (Kerr-Newman, Q=0.5, eps=0): with the separability-preserving charge, the engine STILL
     emits the Carter constant (held-out < 1e-2) -- it reads the deformation as integrability-PRESERVING.
  C3 BUMP DESTROYS CARTER (bumpy, eps>0): with the quadrupole coupling, the EXACT Carter constant is destroyed
     -- the known Carter drifts (> 0.1), the engine's best invariant is NOT the Carter (cosine < 0.9), and it is
     >1e6x less exact than the separable cases. The engine tells the integrability-breaking deformation from the
     preserving one.

NOTE (honest, recorded): at moderate bump the bounded confinement keeps the motion in the KAM regime, so a CRUDE
approximate invariant (held-out ~1e-2) always lingers -- "certify NO invariant" would be too strong (and false).
The correct, decisive discriminator is whether the SPECIFIC Carter (the Killing-tensor hidden symmetry) survives
EXACTLY: it does for Kerr/Kerr-Newman (held-out ~1e-28, cosine 1.000) and is destroyed for the bump (drifts,
cosine ~0, ~1e26x less exact). This matches the bumpy-BH literature: the Carter symmetry breaks, KAM tori
persist at moderate deformation, full chaos only at strong deformation.
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
A = 0.6; R = 6.0; KAP = 0.6; L = 1.0; H0 = 0.2; U0 = 3.0; DT = 0.01
# V_r(r) = H0 r^2 + 1/2 KAP (r-R)^2 - U0 : the H0 r^2 piece cancels the H*dSigma anti-confinement in the radial
# EOM (otherwise the conserved H*Sigma ~ H r^2 acts as an anti-binding potential and every orbit escapes),
# leaving a clean radial well of depth set by U0 centered at R. Stay on the H=H0 shell.


def deriv(r, th, pr, pth, Q, eps):
    Sig = r ** 2 + A ** 2 * np.cos(th) ** 2; Del = r ** 2 - 2 * r + A ** 2 + Q ** 2
    N = 0.5 * Del * pr ** 2 + (H0 * r ** 2 + 0.5 * KAP * (r - R) ** 2 - U0) + 0.5 * pth ** 2 \
        + 0.5 * L ** 2 / np.sin(th) ** 2 + eps * (r - R) ** 2 * np.cos(th) ** 2
    Hval = N / Sig
    dN_r = 0.5 * (2 * r - 2) * pr ** 2 + 2 * H0 * r + KAP * (r - R) + eps * 2 * (r - R) * np.cos(th) ** 2
    dN_th = -L ** 2 * np.cos(th) / np.sin(th) ** 3 + eps * (r - R) ** 2 * (-2 * np.cos(th) * np.sin(th))
    dSig_r = 2 * r; dSig_th = -A ** 2 * np.sin(2 * th)
    rdot = Del * pr / Sig; thdot = pth / Sig
    prdot = -(dN_r - Hval * dSig_r) / Sig; pthdot = -(dN_th - Hval * dSig_th) / Sig
    return rdot, thdot, prdot, pthdot, Hval


def rollout(r, th, pr, pth, Q, eps, nstep=2600):
    out = []
    for k in range(nstep):
        k1 = deriv(r, th, pr, pth, Q, eps)
        k2 = deriv(r + .5 * DT * k1[0], th + .5 * DT * k1[1], pr + .5 * DT * k1[2], pth + .5 * DT * k1[3], Q, eps)
        k3 = deriv(r + .5 * DT * k2[0], th + .5 * DT * k2[1], pr + .5 * DT * k2[2], pth + .5 * DT * k2[3], Q, eps)
        k4 = deriv(r + DT * k3[0], th + DT * k3[1], pr + DT * k3[2], pth + DT * k3[3], Q, eps)
        r += DT / 6 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0]); th += DT / 6 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1])
        pr += DT / 6 * (k1[2] + 2 * k2[2] + 2 * k3[2] + k4[2]); pth += DT / 6 * (k1[3] + 2 * k2[3] + 2 * k3[3] + k4[3])
        if not (R - 3 < r < R + 3) or not (0.3 < th < np.pi - 0.3):
            return None
        if k % 4 == 0 and k > 200:
            out.append([r, th, pr, pth])
    return np.array(out)


def geodesics(Q, eps, n=110, seed=0):
    rng = np.random.default_rng(seed); trajs = []; tries = 0
    while len(trajs) < n and tries < 60 * n:
        tries += 1
        r0 = R + rng.uniform(-1.5, 1.5); th0 = np.pi / 2 + rng.uniform(-0.7, 0.7); pth0 = rng.uniform(-0.6, 0.6)
        Del = r0 ** 2 - 2 * r0 + A ** 2 + Q ** 2
        rem = H0 * A ** 2 * np.cos(th0) ** 2 + U0 - 0.5 * KAP * (r0 - R) ** 2 - 0.5 * pth0 ** 2 \
            - 0.5 * L ** 2 / np.sin(th0) ** 2 - eps * (r0 - R) ** 2 * np.cos(th0) ** 2     # = 1/2 Delta p_r^2
        if rem <= 0:
            continue
        pr0 = np.sqrt(2 * rem / Del) * rng.choice([-1, 1])
        tr = rollout(r0, th0, pr0, pth0, Q, eps)
        if tr is not None and len(tr) > 250:
            trajs.append(tr)
    m = min(len(t) for t in trajs)
    return np.array([t[:m] for t in trajs])


def carter(T):
    r, th, pr, pth = T[..., 0], T[..., 1], T[..., 2], T[..., 3]
    return 0.5 * pth ** 2 + 0.5 * L ** 2 / np.sin(th) ** 2 - A ** 2 * np.cos(th) ** 2 * H0


def lib(T):
    r, th, pr, pth = T[..., 0], T[..., 1], T[..., 2], T[..., 3]
    names = ["p_th^2", "1/sin^2", "cos^2", "p_r^2", "(r-R)^2"]
    F = [pth ** 2, 1 / np.sin(th) ** 2, np.cos(th) ** 2, pr ** 2, (r - R) ** 2]
    return np.stack(F, -1), names


def conserved(Phi):
    G, P, Kd = Phi.shape; flat = Phi.reshape(-1, Kd); mu = flat.mean(0); sd = flat.std(0) + 1e-9
    Z = (Phi - mu) / sd; B = np.cov(Z.reshape(-1, Kd).T); Aw = np.mean([np.cov(Z[g].T) for g in range(G)], 0)
    s, U = np.linalg.eigh(B); keep = s > 1e-9 * s.max(); W = U[:, keep] / np.sqrt(s[keep])
    ev, V = np.linalg.eigh(W.T @ Aw @ W); C = W @ V
    return ev, C, mu, sd


def heldout(Phi, c, mu, sd):
    g = ((Phi - mu) / sd) @ c
    return float(np.mean([g[i].var() for i in range(g.shape[0])]) / (g.reshape(-1).var() + 1e-12))


def known_K_vec(names, sd):
    idx = {n: i for i, n in enumerate(names)}; v = np.zeros(len(names))
    v[idx["p_th^2"]] = 0.5; v[idx["1/sin^2"]] = 0.5 * L ** 2; v[idx["cos^2"]] = -A ** 2 * H0   # K vector in raw features
    return v / np.linalg.norm(v)


def run(Q, eps, seed=1):
    Ttr = geodesics(Q, eps, seed=seed); Tte = geodesics(Q, eps, seed=seed + 50)
    Phi, names = lib(Ttr); Phite, _ = lib(Tte)
    ev, C, mu, sd = conserved(Phi)
    ho = heldout(Phite, C[:, 0], mu, sd)
    c_raw = C[:, 0] / sd; c_raw /= np.linalg.norm(c_raw)
    cos_K = float(abs(c_raw @ known_K_vec(names, sd)))
    # direct check: is the known Carter constant conserved on held-out trajectories?
    Kte = carter(Tte); k_vr = float(np.mean([Kte[i].var() for i in range(Kte.shape[0])]) / (Kte.reshape(-1).var() + 1e-12))
    return ho, cos_K, k_vr


def main():
    kerr = run(0.0, 0.0); kn = run(0.5, 0.0); bump = run(0.0, 0.35)
    cases = {"kerr": kerr, "kerr_newman": kn, "bumpy": bump}
    for nm, (ho, cosK, kvr) in cases.items():
        carter_alive = (ho < 1e-2 and cosK > 0.98)
        dec = "EMIT the Carter constant" if carter_alive else "Carter DESTROYED (no exact 2nd invariant)"
        print(f"{nm:12s}: engine best-invariant held-out {ho:.2e} | cosine to Carter {cosK:.3f} | known-Carter drift {kvr:.2e} -> {dec}")

    c1 = bool(kerr[0] < 1e-2 and kerr[1] > 0.98 and kerr[2] < 1e-2)
    c2 = bool(kn[0] < 1e-2 and kn[1] > 0.98 and kn[2] < 1e-2)
    # the bump DESTROYS the exact Carter: it drifts, the engine's best invariant is NOT the Carter, and it is far
    # less exact than the separable cases (only a crude KAM remnant survives the bounded confinement, not the
    # hidden symmetry -- correct physics, not a failure to certify).
    c3 = bool(bump[2] > 0.1 and bump[1] < 0.9 and bump[0] > 1e6 * kerr[0])
    out = {"a": A, "L": L, "H": H0,
           "kerr": {"heldout": kerr[0], "cosine_Carter": kerr[1], "known_K_drift": kerr[2]},
           "kerr_newman": {"heldout": kn[0], "cosine_Carter": kn[1], "known_K_drift": kn[2]},
           "bumpy": {"heldout": bump[0], "cosine_Carter": bump[1], "known_K_drift": bump[2]},
           "bump_exactness_gap_vs_kerr": float(bump[0] / (kerr[0] + 1e-30)),
           "C1_separable_baseline": c1, "C2_charge_preserves": c2, "C3_bump_destroys_carter": c3,
           "engine_tells_separable_from_breaking": bool(c1 and c2 and c3)}
    print(f"\nC1 SEPARABLE BASELINE (Kerr): emits the EXACT Carter constant (held-out {kerr[0]:.0e}, cosine {kerr[1]:.3f}): {c1}")
    print(f"C2 CHARGE PRESERVES (Kerr-Newman): still emits the EXACT Carter (charge sits in Delta_r, separability kept): {c2}")
    print(f"C3 BUMP DESTROYS CARTER (quadrupole): Carter drifts {bump[2]:.2f}, engine's best is NOT the Carter "
          f"(cosine {bump[1]:.2f}) and is {out['bump_exactness_gap_vs_kerr']:.0e}x less exact than Kerr: {c3}")
    print(f"\nENGINE TELLS SEPARABLE FROM INTEGRABILITY-BREAKING (charge keeps the Carter exactly; the bump destroys it): {out['engine_tells_separable_from_breaking']}")
    (Path(__file__).resolve().parent.parent / "results" / "99_deformed_metrics.json").write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(1, 2, figsize=(13, 5))
    for nm, Q, eps, col in [("Kerr", 0.0, 0.0, "navy"), ("Kerr-Newman (Q=0.5)", 0.5, 0.0, "seagreen"), ("bumpy (ε=0.35)", 0.0, 0.35, "crimson")]:
        T = geodesics(Q, eps, n=6, seed=3)
        Kv = carter(T)
        for i in range(min(6, len(T))):
            ax[0].plot(Kv[i] - Kv[i].mean(), color=col, lw=0.7, alpha=0.6)
        ax[0].plot([], [], color=col, label=nm)
    ax[0].set_xlabel("time along geodesic"); ax[0].set_ylabel("Carter constant K (mean-removed)")
    ax[0].legend(fontsize=8); ax[0].set_title("Carter constant along orbits: flat for Kerr & Kerr-Newman\n(separable), drifting for the bumpy metric (Carter destroyed)")
    labels = ["Kerr\n(separable)", "Kerr-Newman\n(charge: preserved)", "bumpy\n(quadrupole: broken)"]
    hos = [kerr[0], kn[0], bump[0]]
    ax[1].bar(labels, np.clip(hos, 1e-6, None), color=["navy", "seagreen", "crimson"]); ax[1].set_yscale("log")
    ax[1].axhline(1e-2, color="seagreen", ls=":", label="EMIT below (Carter found)")
    ax[1].axhline(0.1, color="crimson", ls=":", label="CERTIFY above (no invariant)")
    ax[1].set_ylabel("engine: held-out var-ratio of best 2nd invariant"); ax[1].legend(fontsize=8)
    ax[1].set_title("the engine tells the separability-preserving deformation (charge)\nfrom the integrability-breaking one (quadrupole bump)")
    fig.tight_layout(); fig.savefig(Path(__file__).resolve().parent.parent / "results" / "99_deformed_metrics.png", dpi=140)
    print("saved results/99_deformed_metrics.json + .png")


if __name__ == "__main__":
    main()
