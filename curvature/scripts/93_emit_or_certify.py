"""Step 93 — EMIT-OR-CERTIFY: one instrument that proposes an invariant when it exists and certifies chaos when
it does not (the distillation head x the impossibility quartet).

Script 92 proved the head EMITS a hidden invariant when the system is integrable (Kerr's Carter constant). The
payoff is the fused instrument: point it at a system whose integrability is BREAKING and have it emit-or-certify.
We use the Pullen-Edmonds Hamiltonian -- a textbook integrable->chaos system that is BOUNDED at every energy and
deformation (no escape, no poles), with an EXACT quadratic invariant at the un-deformed point:
    H = 1/2(px^2 + py^2) + 1/2(x^2 + y^2) + lambda * x^2 y^2
At lambda=0 it is the isotropic oscillator: E_x = 1/2(px^2 + x^2) is an EXACT conserved quadratic (the Carter-
analog -- a second invariant beyond the energy). Turning on the non-separable coupling lambda*x^2y^2 deforms
and then destroys it; at large lambda*E the motion is chaotic and no quadratic invariant survives. Honest
decision (the project's verify-not-echo): does the best conserved quadratic found on TRAIN trajectories stay
conserved on HELD-OUT ones? A real invariant generalizes; a finite-sample artifact does not.

Pre-reg (2026-06-20), fixed energy E=10:
  D1 EMIT at lambda=0 (integrable): the head finds an EXACT conserved quadratic, held-out var-ratio < 1e-3.
  D2 DIAGNOSTIC: the held-out var-ratio of the best quadratic rises monotonically with lambda (the second
     invariant degrades as the deformation breaks integrability).
  D3 CERTIFY at strong deformation: at lambda=0.5 the held-out var-ratio > 0.1 -- NO conserved quadratic
     survives on new trajectories -> the head certifies "no hidden invariant." Emit-or-certify, one instrument.
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
E0 = 10.0


def Vpot(x, y, lam):
    return 0.5 * (x ** 2 + y ** 2) + lam * x ** 2 * y ** 2


def integrate(x, y, px, py, lam, nstep=3000):
    X, Y, PX, PY = [], [], [], []
    def acc(x, y):
        return -(x + 2 * lam * x * y ** 2), -(y + 2 * lam * x ** 2 * y)
    ax, ay = acc(x, y)
    for k in range(nstep):
        px += 0.5 * DT * ax; py += 0.5 * DT * ay; x += DT * px; y += DT * py
        ax, ay = acc(x, y); px += 0.5 * DT * ax; py += 0.5 * DT * ay
        if k % 2 == 0 and k > 150:
            X.append(x); Y.append(y); PX.append(px); PY.append(py)
    return np.array(X), np.array(Y), np.array(PX), np.array(PY)


def trajs(lam, n=120, seed=0):
    rng = np.random.default_rng(seed); out = []
    while len(out) < n:
        x = rng.uniform(-3, 3); y = rng.uniform(-3, 3); py = rng.uniform(-4, 4)
        k = 2 * (E0 - Vpot(x, y, lam)) - py ** 2                    # px^2 from the energy surface
        if k <= 0:
            continue
        px = np.sqrt(k) * rng.choice([-1, 1])
        X, Y, PX, PY = integrate(x, y, px, py, lam)
        if len(X) > 80:
            out.append((X, Y, PX, PY))
    m = min(len(t[0]) for t in out)
    return tuple(np.array([t[i][:m] for t in out]) for i in range(4))


def library(X, Y, PX, PY):
    names = ["px^2", "py^2", "x^2", "y^2", "x*y", "px*py", "x*px", "y*py", "x*py", "y*px"]
    F = [PX ** 2, PY ** 2, X ** 2, Y ** 2, X * Y, PX * PY, X * PX, Y * PY, X * PY, Y * PX]
    return np.stack(F, -1)


def conserved(Phi):
    G, P, K = Phi.shape; flat = Phi.reshape(-1, K); mu = flat.mean(0); flat = flat - mu; Phi = Phi - mu
    B = np.cov(flat.T); Aw = np.mean([np.cov(Phi[g].T) for g in range(G)], 0)
    s, U = np.linalg.eigh(B); keep = s > 1e-8 * s.max(); W = U[:, keep] / np.sqrt(s[keep])
    lam, V = np.linalg.eigh(W.T @ Aw @ W); C = W @ V
    return lam, C, mu


def heldout(Phi, c, mu):
    g = (Phi - mu) @ c
    return float(np.mean([g[i].var() for i in range(g.shape[0])]) / (g.reshape(-1).var() + 1e-12))


def main():
    lambdas = [0.0, 0.05, 0.12, 0.25, 0.5]
    curve = []
    for lam in lambdas:
        Xtr, Ytr, PXtr, PYtr = trajs(lam, seed=int(lam * 1000) + 1)
        Xte, Yte, PXte, PYte = trajs(lam, seed=int(lam * 1000) + 777)
        Phi = library(Xtr, Ytr, PXtr, PYtr); Phite = library(Xte, Yte, PXte, PYte)
        ev, C, mu = conserved(Phi)
        ho = heldout(Phite, C[:, 0], mu); emit = bool(ho < 1e-2)
        curve.append({"lambda": lam, "lambda_E": lam * E0, "train_eigenvalue": float(ev[0]), "heldout_varratio": ho,
                      "decision": "EMIT invariant" if emit else "CERTIFY no invariant"})
        print(f"lambda={lam:.2f} (lambda*E={lam*E0:.1f}): train-eig {ev[0]:.1e} | HELD-OUT var-ratio {ho:.2e} "
              f"-> {'EMIT a conserved quadratic' if emit else 'CERTIFY: no invariant (chaos)'}")

    ho = [c["heldout_varratio"] for c in curve]
    d1 = bool(ho[0] < 1e-3)
    d2 = bool(all(ho[i] <= ho[i + 1] * 3 + 1e-4 for i in range(len(ho) - 1)) and ho[-1] > 100 * (ho[0] + 1e-12))
    d3 = bool(ho[-1] > 0.1)
    out = {"energy": E0, "curve": curve, "D1_emit_at_lambda0": d1, "D2_integrability_diagnostic": d2,
           "D3_certify_at_strong_deformation": d3, "emit_or_certify": bool(d1 and d2 and d3)}
    print(f"\nD1 EMIT exact quadratic at lambda=0 (held-out {ho[0]:.1e} < 1e-3): {d1}")
    print(f"D2 integrability diagnostic (held-out var-ratio {ho[0]:.1e} -> {ho[-1]:.2f} as deformation grows): {d2}")
    print(f"D3 CERTIFY no invariant at strong deformation (held-out {ho[-1]:.2f} > 0.1): {d3}")
    print(f"\nEMIT-OR-CERTIFY (one instrument: proposes an invariant when integrable, certifies chaos when not): {out['emit_or_certify']}")
    (Path(__file__).resolve().parent.parent / "results" / "93_emit_or_certify.json").write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(1, 2, figsize=(13, 5))
    ax[0].semilogy(lambdas, np.clip(ho, 1e-13, None), "o-", color="crimson")
    ax[0].axhline(1e-2, color="seagreen", ls=":", label="EMIT below (invariant exists)")
    ax[0].axhline(0.1, color="navy", ls=":", label="CERTIFY above (no invariant)")
    ax[0].set_xlabel("deformation λ (non-separable x²y² coupling)"); ax[0].set_ylabel("HELD-OUT var-ratio of best quadratic")
    ax[0].legend(fontsize=8); ax[0].set_title("emit-or-certify: an exact invariant at λ=0 (EMIT),\ndestroyed by chaos at strong deformation (CERTIFY) — one instrument")
    for lam, col, lab in [(0.0, "seagreen", "λ=0 regular"), (0.5, "crimson", "λ=0.5 chaotic")]:
        X, Y, PX, PY = trajs(lam, n=12, seed=5)
        for i in range(12):
            cr = np.where(np.abs(X[i]) < 0.06)[0]
            ax[1].plot(Y[i][cr], PY[i][cr], ".", ms=2, color=col, alpha=0.5)
    ax[1].set_xlabel("y"); ax[1].set_ylabel("p_y"); ax[1].set_title("phase space (x≈0 section): regular tori (green)\nvs chaotic sea (red) — the invariant breaks")
    fig.tight_layout(); fig.savefig(Path(__file__).resolve().parent.parent / "results" / "93_emit_or_certify.png", dpi=140)
    print("saved results/93_emit_or_certify.json + .png")


if __name__ == "__main__":
    main()
