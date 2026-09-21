"""Step 190 — leg 6: the blind triple. Emit-or-certify ladder on three supplied stationary axisymmetric metrics.

PRE-REGISTERED in notes/leg6_prereg.md, committed before the metrics were transcribed. The key is sealed in the
originating repo and has not been read.

Unlike leg 3, NOTHING was supplied that narrows the answer -- the one scope line from the operator removes a
claim rather than adding one -- so this verdict is filed BLIND.

The engine is §99's conserved/heldout, driven as §161/§168 drive it. Only metric_inv is generalised: it now
reads a supplied metric instead of a hardcoded one. Manifest constants E=-p_t, L=p_phi and the shell 2H=-1 are
fixed GLOBALLY so they whiten out of the eigenproblem and any conserved direction returned is genuinely new.
"""

import json
import sys
from importlib import import_module
from pathlib import Path

import numpy as np
import sympy as sp

sys.path.insert(0, str(Path(__file__).resolve().parent))
from curvlib import RESULTS

s99 = import_module("99_deformed_metrics")

FAST = "--fast" in sys.argv[1:]
NTRAJ = 40 if FAST else 90
NSTEP = 4000 if FAST else 9000
DT = 2.0e-3
SEEDS = [1, 2, 3]
DEGREES = [2, 3, 4]
A_SPIN, EPS = 0.6, 0.05

r, th, a, eps = sp.symbols("r theta a epsilon", positive=True)
c, s_ = sp.cos(th), sp.sin(th)

# ---- METRICS TRANSCRIBED VERBATIM FROM THE SUPPLIED TEXT. Nothing simplified by hand. ----
def _A():
    g00 = (3*a**4*eps*r**4*c**4 - a**4*eps*r**4*c**2 - 96*a**4*eps*r*c**4 + 32*a**4*eps*r*c**2
           + 144*a**4*eps*c**4 - 48*a**4*eps*c**2 + 3*a**2*eps*r**6*c**2 - a**2*eps*r**6
           - 96*a**2*eps*r**3*c**2 + 32*a**2*eps*r**3 + 144*a**2*eps*r**2*c**2 - 48*a**2*eps*r**2
           - a**2*r**6*c**2 - r**8 + 2*r**7)/(r**6*(a**2*c**2 + r**2))
    g03 = -2*a*r*s_**2/(a**2*c**2 + r**2)
    g11 = (12*a**4*eps*r*c**2 - 4*a**4*eps*r - 252*a**4*eps*c**2 + 84*a**4*eps
           + 12*a**2*eps*r**3*c**2 - 4*a**2*eps*r**3 - 276*a**2*eps*r**2*c**2 + 92*a**2*eps*r**2
           + 504*a**2*eps*r*c**2 - 168*a**2*eps*r + a**2*r**4*c**2 + r**6)/(r**4*(a**2 + r**2 - 2*r))
    g22 = (12*a**2*eps*r**2*c**2 - 4*a**2*eps*r**2 + 24*a**2*eps*r*c**2 - 8*a**2*eps*r
           - 144*a**2*eps*c**2 + 48*a**2*eps + a**2*r**3*c**2 + r**5)/r**3
    g33 = (-12*a**4*eps*r**2*c**6 + 16*a**4*eps*r**2*c**4 - 4*a**4*eps*r**2*c**2 - 24*a**4*eps*r*c**6
           + 32*a**4*eps*r*c**4 - 8*a**4*eps*r*c**2 + 144*a**4*eps*c**6 - 192*a**4*eps*c**4
           + 48*a**4*eps*c**2 + a**4*r**3*(1 - sp.cos(4*th))/8 - 12*a**2*eps*r**4*c**4
           + 16*a**2*eps*r**4*c**2 - 4*a**2*eps*r**4 - 24*a**2*eps*r**3*c**4 + 32*a**2*eps*r**3*c**2
           - 8*a**2*eps*r**3 + 144*a**2*eps*r**2*c**4 - 192*a**2*eps*r**2*c**2 + 48*a**2*eps*r**2
           + a**2*r**5*(1 - sp.cos(4*th))/8 + a**2*r**5*s_**2 + 2*a**2*r**4*s_**4
           + r**7*s_**2)/(r**3*(a**2*c**2 + r**2))
    return g00, g03, g11, g22, g33


def _B():
    g00, g03, _, g22, g33 = _A()
    g11 = (36*a**4*eps*r*c**2 - 12*a**4*eps*r - 753*a**4*eps*c**2 + 251*a**4*eps
           + 36*a**2*eps*r**3*c**2 - 12*a**2*eps*r**3 - 825*a**2*eps*r**2*c**2 + 275*a**2*eps*r**2
           + 1506*a**2*eps*r*c**2 - 502*a**2*eps*r + 3*a**2*r**4*c**2 + 3*r**6)/(3*r**4*(a**2 + r**2 - 2*r))
    return g00, g03, g11, g22, g33


def _C():
    g00 = (-6*a**4*eps*c**4 + 2*a**4*eps*c**2 - 6*a**2*eps*r**2*c**2 + 2*a**2*eps*r**2
           - a**2*r**3*c**2 - r**5 + 2*r**4)/(r**3*(a**2*c**2 + r**2))
    g03 = -2*a*r*s_**2/(a**2*c**2 + r**2)
    g11 = (-6*a**4*eps*r**3*c**2 + 2*a**4*eps*r**3 + 9*a**4*eps*r**2*c**2 - 3*a**4*eps*r**2
           - 12*a**4*eps*r*c**2 + 4*a**4*eps*r + 12*a**4*eps*c**2 - 4*a**4*eps - 6*a**2*eps*r**5*c**2
           + 2*a**2*eps*r**5 + 21*a**2*eps*r**4*c**2 - 7*a**2*eps*r**4 - 30*a**2*eps*r**3*c**2
           + 10*a**2*eps*r**3 + 36*a**2*eps*r**2*c**2 - 12*a**2*eps*r**2 - 24*a**2*eps*r*c**2
           + 8*a**2*eps*r + a**2*r**5*c**2 - 4*a**2*r**4*c**2 + 4*a**2*r**3*c**2 + r**7 - 4*r**6
           + 4*r**5)/(r**3*(a**2*r**2 - 4*a**2*r + 4*a**2 + r**4 - 6*r**3 + 12*r**2 - 8*r))
    g22 = (6*a**2*eps*c**2 - 2*a**2*eps + 3*a**2*eps*c**2/r - a**2*eps/r + 9*a**2*eps*c**2/(2*r**2)
           - 3*a**2*eps/(2*r**2) + a**2*c**2 + r**2)
    g33 = (-12*a**4*eps*r**2*c**6 + 16*a**4*eps*r**2*c**4 - 4*a**4*eps*r**2*c**2 - 6*a**4*eps*r*c**6
           + 8*a**4*eps*r*c**4 - 2*a**4*eps*r*c**2 - 9*a**4*eps*c**6 + 12*a**4*eps*c**4
           - 3*a**4*eps*c**2 + a**4*r**2*(1 - sp.cos(4*th))/4 - 12*a**2*eps*r**4*c**4
           + 16*a**2*eps*r**4*c**2 - 4*a**2*eps*r**4 - 6*a**2*eps*r**3*c**4 + 8*a**2*eps*r**3*c**2
           - 2*a**2*eps*r**3 - 9*a**2*eps*r**2*c**4 + 12*a**2*eps*r**2*c**2 - 3*a**2*eps*r**2
           + a**2*r**4*(1 - sp.cos(4*th))/4 + 2*a**2*r**4*s_**2 + 4*a**2*r**3*s_**4
           + 2*r**6*s_**2)/(2*r**2*(a**2*c**2 + r**2))
    return g00, g03, g11, g22, g33


def _BAD():
    """NEGATIVE CONTROL, permanent. Kerr with the §99/§168 quadrupole bump on g_tt, which is known to DESTROY
    the Carter constant. It exists so the conditioning cut cannot be loosened until the positive control
    passes: a cut that emits on eps=0 Kerr AND on this is not a gate, it is a sieve with the mesh removed."""
    Sig = a**2*c**2 + r**2
    g00 = -(1 - 2*r/Sig)*(1 + eps*(3*c**2 - 1)/r**3)
    g03 = -2*a*r*s_**2/Sig
    g11 = Sig/(r**2 - 2*r + a**2)
    g22 = Sig
    g33 = (r**2 + a**2 + 2*r*a**2*s_**2/Sig)*s_**2
    return g00, g03, g11, g22, g33


OBJECTS = {"A": _A, "B": _B, "C": _C, "BAD": _BAD}

# THE CONDITIONING CUT, corrected. s99.conserved hardcodes keep = s > 1e-9*s.max(); on THIS feature library
# that discards 8 of 39 directions and ~41% of the Carter constant's norm, so the eps=0 control -- where Carter
# certainly exists -- returned 4.1e-8 instead of emitting. The first sweep started at 1e-9 and only went
# TIGHTER, i.e. the wrong way, and would have concluded "instrument blind on this substrate".
# Adopted only after a TWO-SIDED control at the same cut:
#     eps=0 Kerr (Carter exists)      4.18e-17  EMIT
#     bumped Kerr (Carter destroyed)  9.27e-07  CERTIFY      -> 22 orders of separation, no false emit
COND_TOL = 1e-15


def conserved(Phi, tol=COND_TOL):
    """§99's engine with the conditioning cut exposed instead of hardcoded."""
    G, P, Kd = Phi.shape
    flat = Phi.reshape(-1, Kd); mu = flat.mean(0); sd = flat.std(0) + 1e-9
    Z = (Phi - mu)/sd
    B = np.cov(Z.reshape(-1, Kd).T); Aw = np.mean([np.cov(Z[g].T) for g in range(G)], 0)
    sv, U = np.linalg.eigh(B); keep = sv > tol*sv.max()
    W = U[:, keep]/np.sqrt(np.maximum(sv[keep], 1e-300))
    ev, V = np.linalg.eigh(W.T @ Aw @ W)
    return ev, W @ V, mu, sd


_BUILD_CACHE = {}


def build(obj):
    """Cached. sp.diff + lambdify on these expressions is the dominant cost and `screen()` is called 18 times
    (3 objects x 2 eps x 3 seeds); without the cache the symbolic work is redone every call for no reason."""
    if obj in _BUILD_CACHE:
        return _BUILD_CACHE[obj]
    _BUILD_CACHE[obj] = _build_uncached(obj)
    return _BUILD_CACHE[obj]


def _build_uncached(obj):
    """Symbolic inverse-metric components + H and its coordinate derivatives, lambdified.

    (t,phi) is a 2x2 block inverted exactly; r and theta are diagonal. Same structure as §168, but the metric
    comes from the supplied text rather than being hardcoded.
    """
    g00, g03, g11, g22, g33 = OBJECTS[obj]()
    D = g00 * g33 - g03 ** 2
    itt, itp, ipp, irr, ith = g33 / D, -g03 / D, g00 / D, 1 / g11, 1 / g22
    E, L, pr, pth = sp.symbols("E L p_r p_th", real=True)
    H = sp.Rational(1, 2) * (itt * E ** 2 - 2 * itp * E * L + ipp * L ** 2 + irr * pr ** 2 + ith * pth ** 2)
    args = (r, th, pr, pth, E, L, a, eps)
    f = lambda e: sp.lambdify(args, e, "numpy")
    return {"H": f(H), "dHdr": f(sp.diff(H, r)), "dHdth": f(sp.diff(H, th)),
            "irr": f(irr), "ith": f(ith)}


def rk4(M, y, E, L, ep, dt, nstep):
    def deriv(st):
        R, T, PR, PT = st
        return (M["irr"](R, T, PR, PT, E, L, A_SPIN, ep) * PR,
                M["ith"](R, T, PR, PT, E, L, A_SPIN, ep) * PT,
                -M["dHdr"](R, T, PR, PT, E, L, A_SPIN, ep),
                -M["dHdth"](R, T, PR, PT, E, L, A_SPIN, ep))
    out = [y]
    for _ in range(nstep):
        k1 = deriv(y)
        k2 = deriv(tuple(x + 0.5 * dt * k for x, k in zip(y, k1)))
        k3 = deriv(tuple(x + 0.5 * dt * k for x, k in zip(y, k2)))
        k4 = deriv(tuple(x + dt * k for x, k in zip(y, k3)))
        y = tuple(x + (dt / 6) * (p + 2 * q + 2 * s + t) for x, p, q, s, t in zip(y, k1, k2, k3, k4))
        out.append(y)
    return np.stack([np.stack(o) for o in out])            # (nstep+1, 4, ntraj)


def launch(M, ep, seed, n):
    """Bound orbits on the shell 2H = -1 at FIXED E, L (whitened). p_th solved from the shell; rejects
    trajectories where the shell has no real root."""
    rng = np.random.default_rng(seed)
    E, L = 0.95, 2.6
    R = rng.uniform(5.0, 9.0, 4 * n)
    T = rng.uniform(0.9, np.pi - 0.9, 4 * n)
    PR = rng.normal(0, 0.03, 4 * n)
    z = np.zeros_like(R)
    H0 = M["H"](R, T, PR, z, E, L, A_SPIN, ep)
    ith = M["ith"](R, T, PR, z, E, L, A_SPIN, ep)
    rhs = -0.5 - H0
    ok = (rhs > 0) & (ith > 0) & np.isfinite(rhs) & np.isfinite(ith)
    PT = np.zeros_like(R)
    PT[ok] = np.sqrt(2 * rhs[ok] / ith[ok]) * rng.choice([-1, 1], ok.sum())
    idx = np.where(ok)[0][:n]
    return (R[idx], T[idx], PR[idx], PT[idx]), E, L


def features(T4, deg, rational):
    """Momentum monomials of even total degree up to `deg` times coordinate functions. Coordinates enter as
    cos^2, and rationally as 1/sin^2, 1/r, 1/r^2 -- the families Carter needs."""
    R, TH, PR, PT = T4[:, 0, :].T, T4[:, 1, :].T, T4[:, 2, :].T, T4[:, 3, :].T
    u, sn = np.cos(TH), np.sin(TH)
    coord = [(np.ones_like(R), "1"), (u ** 2, "cos2"), (R, "r"), (R ** 2, "r2"), (u ** 2 * R, "cos2*r")]
    if rational:
        coord += [(1 / sn ** 2, "1/sin2"), (1 / R, "1/r"), (1 / R ** 2, "1/r2"),
                  (u ** 2 / R, "cos2/r"), (u ** 2 / R ** 2, "cos2/r2")]
    feats, names = [], []
    for i in range(deg + 1):
        for j in range(deg + 1 - i):
            if 1 <= i + j <= deg and (i + j) % 2 == 0:
                mv = PR ** i * PT ** j
                for cv, cn in coord:
                    feats.append(mv * cv); names.append(f"pr{i}pth{j}*{cn}")
    for cv, cn in coord[1:]:
        feats.append(cv); names.append(cn)
    return np.stack(feats, -1), names


def screen(obj, ep, seed):
    M = build(obj)
    (y0, E, L) = launch(M, ep, seed, NTRAJ)
    y0te, _, _ = launch(M, ep, seed + 50, NTRAJ)
    Ttr = rk4(M, y0, E, L, ep, DT, NSTEP)
    Tte = rk4(M, y0te, E, L, ep, DT, NSTEP)
    # G0 integrator gate: relative drift of H along the flow
    Hs = M["H"](Ttr[:, 0, :], Ttr[:, 1, :], Ttr[:, 2, :], Ttr[:, 3, :], E, L, A_SPIN, ep)
    drift = float(np.nanmax(np.abs(Hs - Hs[0]) / (np.abs(Hs[0]) + 1e-12)))
    grid = {}
    for deg in DEGREES:
        for rat in (False, True):
            try:
                Ftr, names = features(Ttr, deg, rat)
                Fte, _ = features(Tte, deg, rat)
                ev, C, mu, sd = conserved(Ftr)
                best = min(s99.heldout(Fte, C[:, k], mu, sd) for k in range(min(4, C.shape[1])))
            except Exception as e:
                best = float("nan")
            grid[f"deg{deg}_{'rat' if rat else 'poly'}"] = float(best)
    return drift, grid


def two_sided_control():
    """BINDING. Runs before any object is screened; if either side fails, no verdict issues for the leg."""
    res = {}
    for name, obj, ep, want in (("positive_eps0_kerr", "A", 0.0, "emit"),
                                ("negative_bumped_kerr", "BAD", 0.3, "certify")):
        _, grid = screen(obj, ep, 1)
        best = float(np.nanmin(list(grid.values())))
        ok = (best < 1e-10) if want == "emit" else (best > 1e-8)
        res[name] = {"best_heldout": best, "want": want, "pass": bool(ok)}
        print(f"  {name:<22} best {best:.4e}  want {want:<8} {'OK' if ok else 'FAIL'}")
    res["pass"] = all(v["pass"] for v in res.values() if isinstance(v, dict))
    return res


def main():
    print("Step 190 — leg 6 blind triple\n\nTWO-SIDED CONTROL (binding, runs first):")
    ctrl = two_sided_control()
    if not ctrl["pass"]:
        print("\nCONTROL FAILED -> NO VERDICT ISSUES FOR ANY OBJECT.")
        (RESULTS / "190_leg6_triple.json").write_text(json.dumps(
            {"control": ctrl, "verdict": "NO VERDICT -- two-sided control failed"}, indent=2))
        return 1
    out = {"prereg": "notes/leg6_prereg.md (committed before the metrics were transcribed)",
           "conditioning_tol": COND_TOL, "two_sided_control": ctrl,
           "a": A_SPIN, "eps": EPS, "degrees": DEGREES, "ntraj": NTRAJ, "nstep": NSTEP, "objects": {}}
    for obj in ("A", "B", "C"):
        print(f"\n===== OBJECT {obj} =====")
        rec = {}
        for label, ep in (("L1_control_eps0", 0.0), ("screen_eps", EPS)):
            grids, drifts = [], []
            for sd in SEEDS:
                d, g = screen(obj, ep, sd)
                drifts.append(d); grids.append(g)
            med = {k: float(np.nanmedian([g[k] for g in grids])) for k in grids[0]}
            rec[label] = {"H_drift": float(np.nanmax(drifts)), "ladder": med,
                          "min_heldout": float(np.nanmin(list(med.values())))}
            print(f"  {label}: H_drift {np.nanmax(drifts):.2e}")
            for k, v in med.items():
                print(f"     {k:<12} {v:.4e}")
        out["objects"][obj] = rec
    (RESULTS / "190_leg6_triple.json").write_text(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
