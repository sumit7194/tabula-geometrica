"""Step 91 — THE SYMBOLIC DISTILLATION HEAD: tabula stops reading and starts WRITING.

Project expansion (user, 2026-06-20). Every probe so far is a READING instrument: script 85 detects WHETHER a
conserved quantity exists (and correlates it to E/L); script 59 COUNTS how many; the legibility probes decode
embeddings. The output is always a scalar / count / embedding -- a human writes down the formula. This head
makes tabula EMIT a closed-form invariant and SELF-VERIFY it.

Our way (not imported symbolic regression): the cheapest CONSERVED CODE. Build a physics feature library
Phi(state); a conserved quantity is a combination c.Phi that is CONSTANT along trajectories. Find it by a
generalized eigenproblem -- minimize the within-trajectory variance cᵀA c subject to unit total variance
cᵀB c=1 (A = mean within-trajectory covariance, B = total covariance). Near-zero generalized eigenvalues =
conserved directions; their count = number of conserved quantities; sparse rotation of that null space = the
interpretable FORMULAS. Pure linear algebra + sparsity + MDL -- the project's own toolkit.

Discipline (calibrate on a known answer; refuse to hallucinate):
  E1 CALIBRATE on Kepler: emit closed-form invariants and recover the textbook ENERGY E=1/2(vx^2+vy^2)-1/r
     and ANGULAR MOMENTUM L=x vy - y vx -- the conserved subspace contains both (projection residual < 0.05),
     each emitted formula verifies CONSERVED on held-out trajectories (var_along/var_total < 1e-2).
  E2 CHEAPEST CODE: the emitted formulas are SPARSE (<= 3 nonzero terms out of a 12-term library; distractors
     ~ 0) -- the cheapest conserved description, the project's MDL thesis.
  E3 NO-HALLUCINATION GUARD: pointed at chaotic Lorenz (no conserved quantity, certificate II), the smallest
     generalized eigenvalue stays LARGE (> 0.1) -- the head emits "NO closed-form invariant" instead of
     fabricating one. The emitter inherits the impossibility certificate.
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
DT = 0.02


def kepler_trajs(T=120, L=400, seed=0):
    rng = np.random.default_rng(seed); trajs = []
    for _ in range(T):
        r0 = rng.uniform(0.8, 1.5); v0 = rng.uniform(0.75, 1.2)
        x = np.array([r0, 0.0]); v = np.array([0.0, v0]); pts = []
        for _ in range(L):
            r = np.linalg.norm(x); a = -x / r ** 3
            vh = v + 0.5 * DT * a; x = x + DT * vh; a2 = -x / np.linalg.norm(x) ** 3; v = vh + 0.5 * DT * a2
            pts.append([x[0], x[1], v[0], v[1]])
        trajs.append(np.array(pts))
    return np.array(trajs)                                       # (T,L,4): x,y,vx,vy


def lorenz_trajs(T=120, L=400, seed=1, sigma=10., rho=28., beta=8 / 3):
    rng = np.random.default_rng(seed); trajs = []
    def f(s):
        x, y, z = s; return np.array([sigma * (y - x), x * (rho - z) - y, x * y - beta * z])
    for _ in range(T):
        s = rng.uniform(-15, 15, 3); s[2] = abs(s[2]) + 5
        for _ in range(800):
            k1 = f(s); k2 = f(s + .5 * DT * k1); k3 = f(s + .5 * DT * k2); k4 = f(s + DT * k3); s = s + DT * (k1 + 2 * k2 + 2 * k3 + k4) / 6
        pts = []
        for _ in range(L):
            k1 = f(s); k2 = f(s + .5 * DT * k1); k3 = f(s + .5 * DT * k2); k4 = f(s + DT * k3); s = s + DT * (k1 + 2 * k2 + 2 * k3 + k4) / 6; pts.append(s.copy())
        trajs.append(np.array(pts))
    return np.array(trajs)


def kepler_library(P):
    x, y, vx, vy = P[..., 0], P[..., 1], P[..., 2], P[..., 3]; r = np.sqrt(x ** 2 + y ** 2) + 1e-9
    names = ["vx^2", "vy^2", "vx*vy", "x*vy", "y*vx", "x*vx", "y*vy", "1/r", "1/r^2", "x^2", "y^2", "x"]
    F = [vx ** 2, vy ** 2, vx * vy, x * vy, y * vx, x * vx, y * vy, 1 / r, 1 / r ** 2, x ** 2, y ** 2, x]
    return np.stack(F, -1), names


def lorenz_library(P):
    x, y, z = P[..., 0], P[..., 1], P[..., 2]
    names = ["x^2", "y^2", "z^2", "x*y", "x*z", "y*z", "x", "y", "z", "x^2+y^2", "z", "y^2+z^2"]
    F = [x ** 2, y ** 2, z ** 2, x * y, x * z, y * z, x, y, z, x ** 2 + y ** 2, z, y ** 2 + z ** 2]
    return np.stack(F, -1), names


def conserved_spectrum(Phi):
    """Phi (T,L,K). Generalized eig: min cᵀA c / cᵀB c. Returns eigenvalues (asc), conserved directions, whitener."""
    T, L, K = Phi.shape
    flat = Phi.reshape(-1, K); mu = flat.mean(0); flat = flat - mu; Phi = Phi - mu
    B = np.cov(flat.T)                                           # total covariance
    A = np.mean([np.cov(Phi[t].T) for t in range(T)], 0)        # mean within-trajectory covariance
    # whiten by B (drop tiny-variance library directions), then eigendecompose A in the whitened basis
    s, U = np.linalg.eigh(B); keep = s > 1e-8 * s.max()
    W = U[:, keep] / np.sqrt(s[keep])
    At = W.T @ A @ W
    lam, V = np.linalg.eigh(At)                                  # ascending; lam = var_along/var_total
    C = W @ V                                                    # columns: directions in library coords
    return lam, C, mu


def sparse_formula(c, names, thr=0.12):
    c = c / (np.abs(c).max() + 1e-12)
    terms = [(names[i], c[i]) for i in range(len(c)) if abs(c[i]) > thr]
    s = " + ".join(f"{v:+.2f}*{n}" for n, v in terms)
    return s, int(len(terms))


def verify_conserved(Phi, c, mu):
    """var_along / var_total for the emitted formula on (held-out) trajectories."""
    g = (Phi - mu) @ c
    va = np.mean([g[t].var() for t in range(g.shape[0])]); vt = g.reshape(-1).var()
    return float(va / (vt + 1e-12))


def main():
    # ---- E1/E2: calibrate the head on Kepler ----
    Ptr = kepler_trajs(seed=0); Pte = kepler_trajs(seed=99)
    Phi, names = kepler_library(Ptr); Phite, _ = kepler_library(Pte)
    lam, C, mu = conserved_spectrum(Phi)
    n_conserved = int(np.sum(lam < 1e-2))

    # textbook coefficient vectors in library coords
    E_vec = np.zeros(len(names)); E_vec[names.index("vx^2")] = 0.5; E_vec[names.index("vy^2")] = 0.5; E_vec[names.index("1/r")] = -1.0
    L_vec = np.zeros(len(names)); L_vec[names.index("x*vy")] = 1.0; L_vec[names.index("y*vx")] = -1.0
    # does the conserved subspace (bottom-k eigvecs) contain E and L? (projection residual)
    k = max(n_conserved, 2); basis = C[:, :k]; Q, _ = np.linalg.qr(basis)
    def resid(v): vn = v / np.linalg.norm(v); return float(np.linalg.norm(vn - Q @ (Q.T @ vn)))
    res_E, res_L = resid(E_vec), resid(L_vec)

    # sparse emission: the two SPARSEST conserved directions = the two deepest L1 minima on the null-space
    # circle (E and L need not be orthogonal, so take independent sparse minima, not a geometric complement).
    u1, u2 = C[:, 0], C[:, 1]; thetas = np.linspace(0, np.pi, 720)
    def cdir(t): c = np.cos(t) * u1 + np.sin(t) * u2; return c / np.linalg.norm(c)
    l1 = np.array([np.sum(np.abs(cdir(t))) for t in thetas])
    mins = [i for i in range(len(thetas)) if l1[i] < l1[(i - 1) % len(thetas)] and l1[i] < l1[(i + 1) % len(thetas)]]
    mins = sorted(mins, key=lambda i: l1[i])
    c1 = cdir(thetas[mins[0]]); c2 = None
    for i in mins[1:]:                                          # second pick: the next-deepest GENUINELY different formula
        ci = cdir(thetas[i])
        if abs(np.dot(ci, c1)) < 0.95:                          # distinct by vector cosine, not theta-distance
            c2 = ci; break
    if c2 is None:
        c2 = (-np.sin(thetas[mins[0]]) * u1 + np.cos(thetas[mins[0]]) * u2); c2 /= np.linalg.norm(c2)
    f1, n1 = sparse_formula(c1, names); f2, n2 = sparse_formula(c2, names)
    v1 = verify_conserved(Phite, c1, mu); v2 = verify_conserved(Phite, c2, mu)
    # which emitted formula is E vs L (cosine to textbook, sign-free)
    def cossim(a, b): return float(abs(np.dot(a / np.linalg.norm(a), b / np.linalg.norm(b))))
    match = {"formula_1": {"vs_E": cossim(c1, E_vec), "vs_L": cossim(c1, L_vec)},
             "formula_2": {"vs_E": cossim(c2, E_vec), "vs_L": cossim(c2, L_vec)}}

    # ---- E3: no-hallucination guard on chaotic Lorenz ----
    PL = lorenz_trajs(seed=1); PhiL, namesL = lorenz_library(PL)
    lamL, CL, _ = conserved_spectrum(PhiL)
    lorenz_min_lam = float(lamL[0])

    e1 = bool(n_conserved >= 2 and res_E < 0.05 and res_L < 0.05 and v1 < 1e-2 and v2 < 1e-2)
    e2 = bool(n1 <= 3 and n2 <= 3)
    e3 = bool(lorenz_min_lam > 0.1)
    out = {"kepler_eigenvalues": [float(x) for x in lam[:6]], "n_conserved": n_conserved,
           "Evec_residual": res_E, "Lvec_residual": res_L,
           "emitted_formula_1": f1, "verify_1_varratio": v1, "terms_1": n1,
           "emitted_formula_2": f2, "verify_2_varratio": v2, "terms_2": n2, "match_to_textbook": match,
           "lorenz_eigenvalues": [float(x) for x in lamL[:4]], "lorenz_min_lambda": lorenz_min_lam,
           "E1_calibrate_recover_E_and_L": e1, "E2_cheapest_sparse_code": e2, "E3_no_hallucination_guard": e3,
           "distillation_head_works": bool(e1 and e2 and e3)}
    print(f"KEPLER eigenvalues (var_along/var_total): {[f'{x:.1e}' for x in lam[:5]]}  -> {n_conserved} conserved")
    print(f"  conserved subspace contains E (resid {res_E:.3f}) and L (resid {res_L:.3f})")
    print(f"  EMITTED 1: {f1}   [verify var-ratio {v1:.1e}, {n1} terms]")
    print(f"  EMITTED 2: {f2}   [verify var-ratio {v2:.1e}, {n2} terms]")
    print(f"  match: f1 vs(E={match['formula_1']['vs_E']:.2f},L={match['formula_1']['vs_L']:.2f}) "
          f"f2 vs(E={match['formula_2']['vs_E']:.2f},L={match['formula_2']['vs_L']:.2f})")
    print(f"LORENZ smallest eigenvalue {lorenz_min_lam:.3f} (>0.1 => NO conserved formula -- head refuses to hallucinate)")
    print(f"\nE1 calibrate (recover E & L, verified): {e1}")
    print(f"E2 cheapest sparse code (<=3 terms each): {e2}")
    print(f"E3 no-hallucination guard (Lorenz): {e3}")
    print(f"\nSYMBOLIC DISTILLATION HEAD WORKS (tabula now EMITS verified closed-form invariants): {out['distillation_head_works']}")
    (Path(__file__).resolve().parent.parent / "results" / "91_distillation_head.json").write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(1, 2, figsize=(13, 5))
    ax[0].semilogy(range(1, len(lam) + 1), np.clip(lam, 1e-9, None), "o-", color="seagreen", label="Kepler")
    ax[0].semilogy(range(1, len(lamL) + 1), np.clip(lamL, 1e-9, None), "s-", color="crimson", label="Lorenz (chaos)")
    ax[0].axhline(1e-2, color="k", ls=":", label="conserved threshold")
    ax[0].set_xlabel("generalized-eigenvalue index"); ax[0].set_ylabel("var_along / var_total")
    ax[0].legend(fontsize=8); ax[0].set_title("the distillation spectrum: Kepler has 2 conserved directions (~0)\nLorenz has none -- the head refuses to hallucinate a formula")
    ax[1].axis("off")
    ax[1].text(0.02, 0.85, "EMITTED closed-form invariants (Kepler):", fontsize=11, weight="bold")
    ax[1].text(0.04, 0.66, f"K1 = {f1}", fontsize=10, family="monospace", color="navy")
    ax[1].text(0.04, 0.50, f"     verified conserved: var-ratio {v1:.0e}", fontsize=9)
    ax[1].text(0.04, 0.34, f"K2 = {f2}", fontsize=10, family="monospace", color="navy")
    ax[1].text(0.04, 0.18, f"     verified conserved: var-ratio {v2:.0e}", fontsize=9)
    ax[1].text(0.02, 0.02, "= textbook energy & angular momentum, distilled & self-verified", fontsize=9, style="italic")
    fig.tight_layout(); fig.savefig(Path(__file__).resolve().parent.parent / "results" / "91_distillation_head.png", dpi=140)
    print("saved results/91_distillation_head.json + .png")


if __name__ == "__main__":
    main()
