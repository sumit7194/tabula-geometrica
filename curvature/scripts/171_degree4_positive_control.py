"""Step 171 — THE DEGREE-4 POSITIVE CONTROL. The last unvalidated rung of the ladder.

WHY. §169 established the principle the hard way: a null at a rung with no positive control is not a null, it is
"no positive control was run". That closed degree 3. **Degree 4 was left explicitly uncontrolled** -- §168's
degree-4 rungs, and the degree-4 half of every CERTIFY we have ever written, rest on an instrument never shown to
find a degree-4 invariant when one exists.

THE CONTROL. ansatz proposed Cariglia & Galajinsky (arXiv:1503.02162), Ricci-flat signature-(2,q) spacetimes with
irreducible rank-4 Killing tensors via Eisenhart lift of Drach's systems -- verified to exist and say that. We
take the simpler route for the same reason as §169: a positive control needs a KNOWN answer, not an exotic one.
The **4-particle open Toda chain** extends §169's 3-particle system by one site and its Lax matrix supplies a
genuine QUARTIC integral.

    H = 1/2 sum_{i=1..4} p_i^2 + sum_{i=1..3} exp(q_i - q_{i+1})

    L = symmetric tridiagonal,  L_ii = p_i/2,  L_{i,i+1} = L_{i+1,i} = (1/2) exp((q_i - q_{i+1})/2)

    eigenvalues of L are conserved  =>  tr L^k conserved for every k.  H = 2 tr L^2, and tr L^4 is DEGREE 4.

**The invariant is COMPUTED FROM THE MATRIX, not recalled as a polynomial.** §169's near-miss was a recalled
formula; here tr L^4 is evaluated numerically from L at every sample, so there is no expansion to get wrong. Q0
still verifies conservation numerically and Q1 verifies irreducibility numerically before it is used as a target.

PRE-REGISTERED, with a known-pass AND a known-fail for every criterion (the rule adopted this session after two
pre-registrations in one day turned out to be the faulty check):
  Q0 tr L^4 is CONSERVED along trajectories (rel drift < 1e-9)          [known-fail: a non-conserved control]
  Q1 tr L^4 is IRREDUCIBLE -- not a function of the lower integrals {P, H, I3} and their degree-<=4 products
  Q2 THE INSTRUMENT CONTROL: the readout finds it -- n_conserved exceeds the reducible count by one, and I4 lies
     in the conserved span
  Q3 the residual spectrum SEPARATES (ratio > 1e3) after projecting off the reducibles
  Q4 KNOWN-FAIL: a smooth, NON-conserved degree-4 function of the state must NOT be admitted. Without this the
     criteria are tested in one direction only, which is how §170's floor passed while admitting everything.

IF Q2/Q3 FAIL: the ladder is blind at degree 4, and every degree-4 rung we have run -- including §168's -- is
REFUSED rather than null. Both outcomes are results and both are pre-registered.

SCOPE. Toda is a natural Hamiltonian (T + V), not geodesic flow, so the grading argument does not apply and this
is not a claim about any spacetime. It tests whether the READOUT resolves a genuine irreducible quartic invariant
when one is present, which is what every degree-4 verdict silently assumes.
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

from curvlib import RESULTS

s99 = import_module("99_deformed_metrics")
np.seterr(all="ignore")

N = 4
FAST = "--fast" in sys.argv[1:]
NTRAJ = 120 if FAST else 220
NSTEP = 4000 if FAST else 7000
STRIDE = 16 if FAST else 10
DT = 0.004


def deriv(q, p):
    a = np.exp(q[..., :-1] - q[..., 1:])                    # (..., 3)
    dp = np.zeros_like(p)
    dp[..., :-1] -= a
    dp[..., 1:] += a
    return p, dp


def rollout(q, p):
    rec = []
    for i in range(NSTEP):
        k1q, k1p = deriv(q, p)
        k2q, k2p = deriv(q + 0.5 * DT * k1q, p + 0.5 * DT * k1p)
        k3q, k3p = deriv(q + 0.5 * DT * k2q, p + 0.5 * DT * k2p)
        k4q, k4p = deriv(q + DT * k3q, p + DT * k3p)
        q = q + (DT / 6) * (k1q + 2 * k2q + 2 * k3q + k4q)
        p = p + (DT / 6) * (k1p + 2 * k2p + 2 * k3p + k4p)
        if i % STRIDE == 0:
            rec.append(np.concatenate([q, p], -1))
    return np.stack(rec, 1)


def ensemble(seed=0, n=None):
    n = n or NTRAJ
    rng = np.random.default_rng(seed)
    q = np.sort(rng.uniform(-1.8, 1.8, (n, N)), axis=1)[:, ::-1].copy()   # q1 > q2 > ... keeps exponents O(1)
    p = rng.uniform(-0.8, 0.8, (n, N))
    T = rollout(q, p)
    qq, pp = T[..., :N], T[..., N:]
    ex = np.exp(qq[..., :-1] - qq[..., 1:])
    keep = (np.isfinite(T).all(-1).all(-1) & (np.abs(pp).max(-1).max(-1) < 20)
            & np.isfinite(ex).all(-1).all(-1) & (ex.max(-1).max(-1) < 1e6))
    return T[keep]


def lax_traces(T):
    """tr L^k for k = 1..4, computed FROM THE MATRIX at every sample. No polynomial expansion to misremember."""
    q, p = T[..., :N], T[..., N:]
    a = 0.5 * np.exp(0.5 * (q[..., :-1] - q[..., 1:]))
    L = np.zeros(T.shape[:-1] + (N, N))
    idx = np.arange(N)
    L[..., idx, idx] = 0.5 * p
    L[..., idx[:-1], idx[:-1] + 1] = a
    L[..., idx[:-1] + 1, idx[:-1]] = a
    tr = []
    M = np.eye(N) + np.zeros(T.shape[:-1] + (N, N))
    for _ in range(4):
        M = M @ L
        tr.append(np.trace(M, axis1=-2, axis2=-1))
    return tr                                                # [tr L, tr L^2, tr L^3, tr L^4]


def P_of(T):
    return T[..., N:].sum(-1)


def H_of(T):
    q, p = T[..., :N], T[..., N:]
    return 0.5 * (p ** 2).sum(-1) + np.exp(q[..., :-1] - q[..., 1:]).sum(-1)


def reducibles(T):
    """Everything reachable from the LOWER integrals P (deg 1), H (deg 2), I3 (deg 3) at total degree <= 4."""
    tr = lax_traces(T)
    P, H, I3 = P_of(T), H_of(T), tr[2]
    return [(P, "P"), (P ** 2, "P^2"), (P ** 3, "P^3"), (P ** 4, "P^4"),
            (H, "H"), (H ** 2, "H^2"), (P * H, "P*H"), (P ** 2 * H, "P^2*H"),
            (I3, "I3"), (P * I3, "P*I3")]


def library(T, deg=4):
    """Momentum monomials in (p1..p4) of total degree 0..deg times a NAMED coordinate family.

    Momentum degree 0 IS included: H's potential term and I4's pure-potential part carry no momentum factor, and
    a library with a momentum floor makes them unrepresentable (§167 and §169 both hit exactly that)."""
    q, p = T[..., :N], T[..., N:]
    a = np.exp(q[..., :-1] - q[..., 1:])                     # a1, a2, a3
    one = np.ones_like(a[..., 0])
    coord = [(one, "1")]
    for i in range(N - 1):
        coord.append((a[..., i], f"a{i}"))
        coord.append((a[..., i] ** 2, f"a{i}^2"))
    for i in range(N - 1):
        for j in range(i + 1, N - 1):
            coord.append((a[..., i] * a[..., j], f"a{i}a{j}"))
    feats, names = [], []
    for e in _mono(N, deg):
        mv = one.copy()
        lab = ""
        for j, ej in enumerate(e):
            if ej:
                mv = mv * p[..., j] ** ej
                lab += f"p{j}^{ej}"
        for cv, cn in coord:
            if not lab and cn == "1":
                continue                                     # the bare constant
            feats.append(mv * cv)
            names.append(f"{lab or '1'}*{cn}")
    return np.stack(feats, -1), names


def _mono(k, deg):
    if k == 1:
        for e in range(deg + 1):
            yield (e,)
        return
    for e in range(deg + 1):
        for rest in _mono(k - 1, deg - e):
            yield (e,) + rest


def conditioning_basis(F, tol=1e-9):
    Fm = F.reshape(-1, F.shape[-1])
    sc = Fm.std(0) + 1e-300
    _, sv, Vt = np.linalg.svd(Fm / sc, full_matrices=False)
    k = int((sv > sv[0] * tol).sum())
    return Vt[:k].T / sc[:, None]


def rel_drift(A):
    return float(np.mean(np.std(A, 1) / (np.abs(np.mean(A, 1)) + 1e-30)))


def var_ratio(A):
    return float(np.mean([A[i].var() for i in range(len(A))]) / (A.reshape(-1).var() + 1e-30))


def in_span(vals, target):
    X = np.concatenate([vals, np.ones((len(vals), 1))], 1)
    c, *_ = np.linalg.lstsq(X, target, rcond=None)
    return float(np.linalg.norm(X @ c - target) / (np.linalg.norm(target - target.mean()) + 1e-300))


def residual_spectrum(cons_vals, T):
    R = np.stack([v.mean(1) for v, _ in reducibles(T)], 1)
    if cons_vals.shape[1] == 0:
        return np.zeros(0)
    C = (cons_vals - cons_vals.mean(0)) / (cons_vals.std(0) + 1e-300)
    Rz = (R - R.mean(0)) / (R.std(0) + 1e-300)
    Q, _ = np.linalg.qr(Rz)
    C = C - Q @ (Q.T @ C)
    sv = np.linalg.svd(C, compute_uv=False)
    return sv / (sv[0] + 1e-300)


def main():
    out = {"system": f"{N}-particle open Toda chain",
           "why": "the degree-4 positive control the ladder has never had; every degree-4 CERTIFY assumes it",
           "invariant": "tr L^4 from the Lax matrix, evaluated numerically (no recalled polynomial)",
           "scope": ("natural Hamiltonian, not geodesic flow -- tests the READOUT at degree 4, not any "
                     "spacetime. ansatz's Cariglia-Galajinsky metrics (arXiv:1503.02162) are the exotic route.")}
    Ttr, Tte = ensemble(seed=1), ensemble(seed=51)
    print(f"ensemble: {len(Ttr)} train / {len(Tte)} test, {Ttr.shape[1]} samples each")

    tr_te = lax_traces(Tte)
    I4 = tr_te[3]
    dH, dP, dI4 = rel_drift(H_of(Tte)), rel_drift(P_of(Tte)), rel_drift(I4)
    known_fail = Tte[..., 0] * np.cos(Tte[..., N]) + 0.3 * Tte[..., N + 1] ** 2      # smooth, NOT conserved
    d_kf = rel_drift(known_fail)
    print(f"Q0  drift: H {dH:.2e}  P {dP:.2e}  trL^4 {dI4:.2e}   |  known-fail control {d_kf:.2e}")
    Q0 = bool(dI4 < 1e-9 and dH < 1e-9 and d_kf > 1e-3)

    R = np.stack([v.mean(1) for v, _ in reducibles(Tte)], 1)
    y4 = I4.mean(1)
    r2 = 1 - in_span(R, y4) ** 2
    print(f"Q1  trL^4 regressed on the 10 reducibles: R^2 = {r2:.6f}  (irreducible if well below 1)")
    Q1 = bool(r2 < 0.99)

    Fa, names = library(Ttr, 4)
    Fb, _ = library(Tte, 4)
    V = conditioning_basis(Fa)
    Fk, Ftek = Fa @ V, Fb @ V
    ev, C, mu, sd = s99.conserved(Fk)
    ratios = np.array([s99.heldout(Ftek, C[:, k], mu, sd) for k in range(C.shape[1])])
    order = np.argsort(ratios)
    rs = ratios[order]
    floor = max(var_ratio(H_of(Tte)), var_ratio(P_of(Tte)))
    n_cons = int((rs <= floor * 1e3).sum())
    cons_vals = np.stack([(((Ftek - mu) / sd) @ C[:, k]).mean(1) for k in order[:n_cons]], 1) \
        if n_cons else np.zeros((len(Tte), 0))
    i4_resid = in_span(cons_vals, y4) if n_cons else 1.0
    kf_resid = in_span(cons_vals, known_fail.mean(1)) if n_cons else 1.0
    n_red = R.shape[1]
    spec = residual_spectrum(cons_vals, Tte)
    sep = float(spec[0] / spec[1]) if len(spec) > 1 else float("inf")
    print(f"Q2  p={Fk.shape[-1]}  conserved={n_cons}  reducibles={n_red}  "
          f"trL^4 residual in span = {i4_resid:.2e}")
    print(f"Q3  residual spectrum {['%.1e' % x for x in spec[:5]]}   separation = {sep:.2e}")
    print(f"Q4  KNOWN-FAIL residual in span = {kf_resid:.2e} "
          f"({'correctly EXCLUDED' if kf_resid > 1e-2 else 'WRONGLY ADMITTED'})")
    Q2 = bool(i4_resid < 1e-3 and n_cons > n_red)
    Q3 = bool(sep > 1e3)
    Q4 = bool(kf_resid > 1e-2)

    works = bool(Q0 and Q1 and Q2 and Q3 and Q4)
    verdict = ("THE READOUT IS NOT BLIND AT DEGREE 4. Given a genuine irreducible quartic invariant in a library "
               "that can represent it, the readout finds it: trL^4 lies in the conserved span (residual {:.0e}), "
               "the residual spectrum separates by {:.0e}, and a smooth non-conserved control is correctly "
               "excluded ({:.0e}). Degree 4 now has the positive control degree 3 got in §169, so a degree-4 "
               "null elsewhere in the ladder is a null about the basis rather than about the instrument."
               .format(i4_resid, sep, kf_resid) if works else
               "THE LADDER IS BLIND AT DEGREE 4 (or the control is mis-specified -- see which Q failed). A known "
               "irreducible quartic invariant is present and verified, and the readout does not cleanly resolve "
               "it. Every degree-4 rung run so far, §168's included, is REFUSED rather than null.")
    out.update({"Q0_conserved": Q0, "Q1_irreducible": Q1, "Q2_readout_finds_it": Q2,
                "Q3_spectrum_separates": Q3, "Q4_known_fail_excluded": Q4,
                "drift_H": dH, "drift_P": dP, "drift_I4": dI4, "drift_known_fail": d_kf,
                "reducible_r2": r2, "n_conserved": n_cons, "n_reducible": n_red,
                "i4_residual_in_span": i4_resid, "known_fail_residual": kf_resid,
                "separation": sep, "residual_spectrum": [float(x) for x in spec[:6]],
                "p": int(Fk.shape[-1]), "ladder_works_at_degree4": works, "verdict": verdict})
    print(f"\nQ0 {Q0} | Q1 {Q1} | Q2 {Q2} | Q3 {Q3} | Q4 {Q4}")
    print(verdict)
    (RESULTS / "171_degree4_positive_control.json").write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.semilogy(range(1, len(spec[:8]) + 1), np.maximum(spec[:8], 1e-20), "o-")
    ax.set_xlabel("residual direction")
    ax.set_ylabel("singular value (normalized)")
    ax.set_title("Degree-4 positive control (Toda tr L^4)\n"
                 "one direction standing out = the readout resolves a genuine quartic invariant")
    fig.tight_layout()
    fig.savefig(RESULTS / "171_degree4_positive_control.png", dpi=140)
    print("saved results/171_degree4_positive_control.json + .png")


if __name__ == "__main__":
    main()
