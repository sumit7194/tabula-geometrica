"""Step 196 -- established chaos indicators (MEGNO, SALI, FLI) as the third method after §195's honest negative.
Plan: notes/established_indicator_plan.md (reviewed by The Bridge).

Tangent dynamics are EXACT via complex-step differentiation, J.v = Im f(z + i h v) / h with h = 1e-30 (no
subtractive cancellation). The generated reduced RHS is analytic (no abs/sign/where; checked), and only 193's
`.astype(float)` blocked complex input, so this file carries its own complex-safe copy of the RHS.

    .venv314ob/bin/python scripts/196_chaos_indicators.py --validate     # J.v vs Richardson FD (+ HH exact Jacobian)
"""

import argparse
import json
import sys
from importlib import import_module
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

m = import_module("195_invariant_learnability")         # BLAS threads = 1; 193's OpenBLAS tripwire
import numpy as np                                        # noqa: E402

m94, s193 = m.m94, m.s193
RESULTS = Path(__file__).resolve().parent.parent / "results"
H_CS = 1e-30


def rhs_c(mdl, z):
    """The reduced geodesic RHS of 193's Reduced.rhs, complex-safe. HH (no .st) is a polynomial and already safe."""
    if not hasattr(mdl, "st"):
        return mdl.rhs(z)
    x, y, px, py = z
    o = [np.broadcast_to(v, np.shape(x)).astype(np.result_type(x, float)) for v in mdl.st._f(x, y)]
    a, b, c = mdl.w
    Vx, Vy = (a * o[i] + b * o[i + 3] + c * o[i + 6] for i in (1, 2))
    gxx, gxxx, gxxy, gyy, gyyx, gyyy = o[9:15]
    return np.stack([gxx * px, gyy * py,
                     -(0.5 * (gxxx * px ** 2 + gyyx * py ** 2) + Vx),
                     -(0.5 * (gxxy * px ** 2 + gyyy * py ** 2) + Vy)])


def jvp(mdl, z, v):
    """Exact Jacobian-vector product of the RHS (complex step)."""
    return np.imag(rhs_c(mdl, z + 1j * H_CS * v)) / H_CS


def _fd(mdl, z, v, eps):
    return (mdl.rhs(z + eps * v) - mdl.rhs(z - eps * v)) / (2 * eps)


def hh_jac(z):
    x, y, _, _ = z
    J = np.zeros((4, 4) + np.shape(x))
    J[0, 2] = J[1, 3] = 1.0
    J[2, 0], J[2, 1] = -(1 + 2 * y), -2 * x
    J[3, 0], J[3, 1] = -2 * x, -(1 - 2 * y)
    return J


def sample_states(mdl, n, T=2000.0, dt=0.05):
    """Generic on-shell states: seeds, then a short integration, so y and px are nonzero."""
    if not hasattr(mdl, "st"):
        z0 = mdl.launch(n, np.random.default_rng(3))
    else:
        reg = m94.seed_region(mdl.st, mdl.E, mdl.L) if hasattr(mdl, "st") else None
        z0, _ = m94.seeds(mdl, np.linspace(reg[0], reg[1], n))
    res = m94.integrate(mdl, z0, T, dt, 100, twin=False)
    S = res["samples"][:, -1, :]
    return S[:, np.isfinite(S).all(0)]


def validate():
    sts, _ = m94.spacetimes("t1o3")
    zv = s193.Spacetime(*s193.zv2_components(), "ZV2")
    E = 0.97
    models = {"Kerr": sts["Kerr"].at(E, -m94.l_sep(sts["Kerr"], E, -1) * 1.005),
              "TS2": sts["TS2"].at(E, -m94.l_sep(sts["TS2"], E, -1) * 1.005),
              "ZV2": zv.at(0.95, 1.5), "HH": m94.HenonHeiles(1 / 12)}
    out = {}
    rng = np.random.default_rng(11)
    for name, mdl in models.items():
        z = sample_states(mdl, 12, dt=0.0025 if name == "HH" else 0.05)
        v = rng.standard_normal(z.shape)
        v /= np.linalg.norm(v, axis=0)
        cs = jvp(mdl, z, v)
        scale = np.abs(cs).max(0) + 1e-300
        rich = {}
        for e in (1e-3, 1e-4, 1e-5):                      # Richardson: (4 D(e/2) - D(e)) / 3, removes O(e^2)
            eps = e * (np.abs(z).max(0) + 1)
            d1, d2 = _fd(mdl, z, v, eps), _fd(mdl, z, v, eps / 2)
            rich[e] = float(np.max(np.abs((4 * d2 - d1) / 3 - cs).max(0) / scale))
        rec = {"n_states": int(z.shape[1]), "rel_err_vs_richardson": rich}
        if name == "HH":
            Jv = np.einsum("ijk,jk->ik", hh_jac(z), v)
            rec["rel_err_vs_exact"] = float(np.max(np.abs(Jv - cs).max(0) / scale))
        out[name] = rec
        print(name, rec, flush=True)
    (RESULTS / "196_validate_tangent.json").write_text(json.dumps(out, indent=1))


# ---------------------------------------------------------------- MEGNO / FLI / SALI integrator

CHECK = (1e2, 3e2, 1e3, 3e3, 1e4, 3e4, 1e5, 1.5e5)
NVEC = 4                                   # two independent random pairs (Breiter: initial-vector dependence)


def indicators(mdl, z0, T, dt, seed):
    """RK4 on (z, w_1..w_4), w' = J(z) w exactly (complex step). Each vector is renormalised every step.
    MEGNO (Cincotta & Simo 2000): Y(t) = (2/t) int_0^t s*lam(s) ds with lam = w.Jw/|w|^2; <Y>(t) = (1/t) int_0^t Y.
    FLI = max over s <= t of the cumulative log-growth. SALI_pair = min(|w_a + w_b|, |w_a - w_b|) for normalised w.
    Returns, per checkpoint t <= T: <Y>, FLI and SALI for both pairs (NaN after a plunge), plus t_plunge and H drift."""
    G = z0.shape[1]
    rng = np.random.default_rng(seed)
    W = rng.standard_normal((NVEC, 4, G))
    W /= np.linalg.norm(W, axis=1, keepdims=True)
    z = z0.astype(float).copy()
    H0 = mdl.H(z)
    alive, t_plunge, hdrift = np.ones(G, bool), np.full(G, np.inf), np.zeros(G)
    logg = np.zeros((NVEC, G))
    fli = np.zeros((NVEC, G))
    I = np.zeros((NVEC, G))
    S = np.zeros((NVEC, G))
    lam_prev = np.zeros((NVEC, G))
    Y_prev = np.zeros((NVEC, G))
    nstep = int(round(T / dt))
    checks = {int(round(c / dt)): c for c in CHECK if c <= T}
    rec = {}

    def F(zz, ww):
        """One complex RHS call for all vectors: Re -> f(z) (exact; h^2 ~ 1e-60), Im/h -> J w_k."""
        Zr = np.broadcast_to(zz[:, None, :], (4, NVEC, G)).reshape(4, NVEC * G)
        c = rhs_c(mdl, Zr + 1j * H_CS * ww.transpose(1, 0, 2).reshape(4, NVEC * G))
        return np.real(c[:, :G]), (np.imag(c) / H_CS).reshape(4, NVEC, G).transpose(1, 0, 2)

    for i in range(1, nstep + 1):
        k1z, k1w = F(z, W)
        lam = np.einsum("kig,kig->kg", W, k1w)         # rate at t_{i-1} (|w| = 1): reuses RK stage 1
        if i > 1:
            t = (i - 1) * dt
            I = I + 0.5 * ((t - dt) * lam_prev + t * lam) * dt
            Y = 2 * I / t
            S = S + 0.5 * (Y_prev + Y) * dt if i > 2 else S + Y * dt
            Y_prev = Y
        lam_prev = lam
        k2z, k2w = F(z + 0.5 * dt * k1z, W + 0.5 * dt * k1w)
        k3z, k3w = F(z + 0.5 * dt * k2z, W + 0.5 * dt * k2w)
        k4z, k4w = F(z + dt * k3z, W + dt * k3w)
        zn = z + dt / 6 * (k1z + 2 * k2z + 2 * k3z + k4z)
        Wn = W + dt / 6 * (k1w + 2 * k2w + 2 * k3w + k4w)
        fin = np.isfinite(zn).all(0) & np.isfinite(Wn).all((0, 1))
        if mdl.sig is not None:
            fin &= (1 + mdl.sig * np.where(fin, zn[0], 0.0)) >= m94.R_PLUNGE
        t_plunge[alive & ~fin] = i * dt
        alive &= fin
        z = np.where(alive, zn, z)
        nrm = np.where(alive, np.linalg.norm(Wn, axis=1), 1.0)
        W = np.where(alive, Wn / nrm[:, None, :], W)
        logg = logg + np.log(nrm)
        fli = np.maximum(fli, logg)
        if i % 10 == 0:
            hdrift = np.where(alive, np.maximum(hdrift, np.abs(mdl.H(z) - H0) / np.abs(H0)), hdrift)
        if i in checks:
            tc = max((i - 1) * dt, dt)
            sali = np.stack([np.minimum(np.linalg.norm(W[a] + W[b], axis=0), np.linalg.norm(W[a] - W[b], axis=0))
                             for a, b in ((0, 1), (2, 3))])
            dead = ~alive
            mY, fl, sl = S / tc, fli.copy(), sali.copy()
            mY[:, dead], fl[:, dead], sl[:, dead] = np.nan, np.nan, np.nan
            rec[checks[i]] = {"megno": mY.tolist(), "fli": fl.tolist(), "sali": sl.tolist()}
    return {"checkpoints": rec, "t_plunge": t_plunge.tolist(), "hdrift": hdrift.tolist()}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--validate", action="store_true")
    a = ap.parse_args()
    if a.validate:
        validate()
