"""Step 169 — THE MISSING POSITIVE CONTROL AT DEGREE 3. Does the ladder work at all above degree 2?

WHY THIS EXISTS, and it is a correction to our own conclusion. §168 reported that at momentum degree >= 3 on
deformed Kerr "nothing separates after deflating the reducibles", and we called that a third answer -- neither a
coverage limit nor a miscount. ansatz pointed out that it is not established, and they are right:

    At degree 3 the deflation removes p_t*K and p_phi*K -- every place Carter appears at that degree. So the
    eps=0 control was asking the engine to find something that, as far as anyone knows, ISN'T THERE. An empty
    complement is then consistent with BOTH readings and discriminates neither:
        "correctly nothing"  -- no irreducible rank-3 KT exists on Kerr, and the instrument works perfectly
        "instrument blind"   -- structure exists at degree >= 3 and the readout cannot resolve it

A NULL AT A RUNG WITH NO POSITIVE CONTROL IS NOT A NULL. That is our own REFUSED-LIBRARY principle one level up,
and the fourth instance of the pattern we named: "didn't happen" and "happened and found nothing" producing the
same output. ansatz also checked whether "correctly nothing" is a theorem for Kerr and could not find one, so it
is an expectation, not a fact, and must not be cited as one.

THE CONTROL. We need a system whose degree-3 answer is KNOWN AND NONZERO. ansatz proposed Cariglia & Galajinsky
(arXiv:1503.02162), Ricci-flat signature-(2,q) spacetimes with irreducible rank-3/4 Killing tensors built by
Eisenhart-lifting Drach's 2D integrable systems -- verified to exist and to say that. We use the simpler, older
member of the same family, because a positive control needs a KNOWN answer rather than an exotic one: the

    3-PARTICLE OPEN TODA CHAIN,  H = 1/2 (p1^2+p2^2+p3^2) + exp(q1-q2) + exp(q2-q3)

whose third integral is CUBIC in the momenta (web-verified; the Lax formulation gives it as ~tr L^3). Its
conserved quantities are P = sum p_i (degree 1), H (degree 2), and I3 (degree 3, irreducible).

We do NOT trust the recalled formula: T0 verifies numerically that our I3 is conserved to machine precision, and
T1 verifies numerically that it is IRREDUCIBLE (not expressible through P and H at degree 3). Only then is it
used as the target.

PRE-REGISTERED, and both outcomes are results:
  T0 the candidate I3 is conserved along trajectories (rel drift < 1e-10) -- else our formula is wrong
  T1 I3 is IRREDUCIBLE: regressing it on {P, P^2, P^3, H, P*H} leaves a large residual -- else it is bookkeeping
  T2 THE INSTRUMENT CONTROL: the §168 readout, run at degree 3, finds EXACTLY ONE irreducible direction, and I3
     lies in the conserved span. -> the ladder works at degree 3, and §168's degree-3 null on deformed Kerr is a
     genuine null rather than an artifact.
  T3 the residual spectrum SEPARATES (ratio > 1e3), the same non-definitional statistic that read 2.8e5 at
     degree 2 and 1.7 at degree 3 on deformed Kerr.
  IF T2/T3 FAIL: the instrument is blind at degree >= 3, every degree-3/4 rung we have ever run is REFUSED
  rather than null, and §168's "third answer" is withdrawn entirely.

SCOPE, stated rather than discovered later. Toda is a natural Hamiltonian (T + V), not pure geodesic flow, so
ansatz's grading result (bracket raises momentum degree by exactly one) does NOT apply here -- with a potential
the bracket lands in k+1 AND k-1 and only parity decouples. That does not matter for what this run tests: the
question is whether the READOUT can resolve a genuine irreducible cubic invariant when one is present, and that
question is signature- and grading-independent. It is an instrument control, not a physics claim.
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

s99 = import_module("99_deformed_metrics")
np.seterr(all="ignore")

FAST = "--fast" in sys.argv[1:]
NTRAJ = 120 if FAST else 250
NSTEP = 4000 if FAST else 8000
STRIDE = 16 if FAST else 8
DT = 0.004


def deriv(q, p):
    """Hamilton's equations for the 3-particle OPEN Toda chain."""
    a = np.exp(q[..., 0] - q[..., 1])
    b = np.exp(q[..., 1] - q[..., 2])
    dq = p
    dp = np.stack([-a, a - b, b], -1)
    return dq, dp


def rollout(q, p, nstep=None):
    nstep = nstep or NSTEP
    rec = []
    for i in range(nstep):
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
    """P and H both VARY across realizations, so the reducibles are present and must be recovered first."""
    n = n or NTRAJ
    rng = np.random.default_rng(seed)
    q = np.stack([rng.uniform(0.6, 1.6, n), rng.uniform(-0.4, 0.4, n), rng.uniform(-1.6, -0.6, n)], -1)
    p = rng.uniform(-0.9, 0.9, (n, 3))
    T = rollout(q, p)
    # Open Toda SCATTERS: the particles separate, so positions grow without bound and a |position| cutoff
    # rejects every trajectory at longer integration times (it silently emptied the full-length run). What must
    # stay bounded is the momenta and the exponentials, so those are what we filter on.
    q_, p_ = T[..., :3], T[..., 3:]
    exps = np.stack([np.exp(q_[..., 0] - q_[..., 1]), np.exp(q_[..., 1] - q_[..., 2])], -1)
    keep = (np.isfinite(T).all(-1).all(-1) & (np.abs(p_).max(-1).max(-1) < 20)
            & np.isfinite(exps).all(-1).all(-1) & (exps.max(-1).max(-1) < 1e6))
    return T[keep]


def H_of(T):
    q, p = T[..., :3], T[..., 3:]
    return 0.5 * (p ** 2).sum(-1) + np.exp(q[..., 0] - q[..., 1]) + np.exp(q[..., 1] - q[..., 2])


def P_of(T):
    return T[..., 3:].sum(-1)


def I3_of(T):
    """The cubic integral. NOT trusted from memory -- T0 verifies it numerically before it is used."""
    q, p = T[..., :3], T[..., 3:]
    a = np.exp(q[..., 0] - q[..., 1])
    b = np.exp(q[..., 1] - q[..., 2])
    return (p ** 3).sum(-1) / 3.0 + (p[..., 0] + p[..., 1]) * a + (p[..., 1] + p[..., 2]) * b


def reducibles(T, deg=3):
    """Everything expressible through the LOWER-degree invariants P (deg 1) and H (deg 2) up to degree 3."""
    P, H = P_of(T), H_of(T)
    return [(P, "P"), (P ** 2, "P^2"), (P ** 3, "P^3"), (H, "H"), (P * H, "P*H")]


def library(T, deg=3):
    """Momentum monomials in (p1,p2,p3) of total degree 1..deg times a NAMED coordinate family. The family must
    carry the exponentials, because I3 contains p*exp(q_i - q_j) terms -- a basis that cannot represent the
    target cannot test the readout (ansatz's slice-specific-basis lesson, applied before the fact)."""
    q, p = T[..., :3], T[..., 3:]
    a = np.exp(q[..., 0] - q[..., 1])
    b = np.exp(q[..., 1] - q[..., 2])
    one = np.ones_like(a)
    coord = [(one, "1"), (a, "a"), (b, "b"), (a * b, "ab"), (a ** 2, "a^2"), (b ** 2, "b^2")]
    # MOMENTUM DEGREE 0 IS INCLUDED. Requiring degree >= 1 makes H unrepresentable -- its potential term a+b
    # carries no momentum factor -- so H drops out of the conserved span and the reducible count is overstated
    # by one. §167 hit the identical bug on Carter's -A^2 cos^2(theta) H0 term. The recurring form is: a known
    # invariant with a pure-coordinate piece is invisible to a library that insists on a momentum factor.
    feats, names = [], []
    for i in range(deg + 1):
        for j in range(deg + 1 - i):
            for k in range(deg + 1 - i - j):
                if i + j + k > deg:
                    continue
                mv = (p[..., 0] ** i) * (p[..., 1] ** j) * (p[..., 2] ** k)
                for cv, cn in coord:
                    if i + j + k == 0 and cn == "1":
                        continue                      # the bare constant: zero variance, trivially "conserved"
                    feats.append(mv * cv)
                    names.append(f"p1^{i}p2^{j}p3^{k}*{cn}")
    return np.stack(feats, -1), names


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


def residual_spectrum(cons_vals, T):
    """Conserved values with everything the reducibles explain projected out. Threshold-free; the separation
    RATIO is the statistic, never a cutoff calibrated between the top two values (which would make the control
    return 1 by construction -- a control that cannot fail is not a control)."""
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
    out = {"system": "3-particle open Toda chain, H = 1/2 sum p_i^2 + exp(q1-q2) + exp(q2-q3)",
           "why": "the degree-3 POSITIVE CONTROL §168 never had: a system whose degree-3 answer is known nonzero",
           "scope": ("Toda is a natural Hamiltonian, not geodesic flow, so the grading result does not apply. "
                     "This tests whether the READOUT resolves a genuine irreducible cubic invariant, which is "
                     "grading- and signature-independent. Instrument control, not a physics claim.")}
    Ttr, Tte = ensemble(seed=1), ensemble(seed=51)
    print(f"ensemble: {len(Ttr)} train / {len(Tte)} test trajectories, {Ttr.shape[1]} samples each")

    # ---- T0: is our cubic actually conserved? ----
    dH, dP, dI = rel_drift(H_of(Tte)), rel_drift(P_of(Tte)), rel_drift(I3_of(Tte))
    print(f"T0  drift: H {dH:.2e}   P {dP:.2e}   I3 {dI:.2e}")
    T0 = bool(dI < 1e-10 and dH < 1e-10)

    # ---- T1: is it IRREDUCIBLE (not a function of P and H)? ----
    R = np.stack([v.mean(1) for v, _ in reducibles(Tte)], 1)
    Ra = np.concatenate([R, np.ones((len(R), 1))], 1)
    y = I3_of(Tte).mean(1)
    coef, *_ = np.linalg.lstsq(Ra, y, rcond=None)
    r2 = 1 - float(((Ra @ coef - y) ** 2).sum()) / (float(((y - y.mean()) ** 2).sum()) + 1e-300)
    print(f"T1  I3 regressed on reducibles {{P,P^2,P^3,H,P*H}}: R^2 = {r2:.6f} "
          f"(irreducible if well below 1)")
    T1 = bool(r2 < 0.99)

    # ---- T2/T3: THE INSTRUMENT CONTROL -- can the readout find it? ----
    Fa, names = library(Ttr, 3)
    Fb, _ = library(Tte, 3)
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
    # does I3 lie in the conserved span?
    if n_cons:
        X = np.concatenate([cons_vals, np.ones((len(cons_vals), 1))], 1)
        c2, *_ = np.linalg.lstsq(X, y, rcond=None)
        i3_resid = float(np.linalg.norm(X @ c2 - y) / (np.linalg.norm(y - y.mean()) + 1e-300))
    else:
        i3_resid = 1.0
    spec = residual_spectrum(cons_vals, Tte)
    sep = float(spec[0] / spec[1]) if len(spec) > 1 else float("inf")
    n_red = 5
    print(f"T2  p={Fk.shape[-1]} conserved={n_cons} (reducibles present: {n_red})  "
          f"I3 residual in conserved span = {i3_resid:.2e}")
    print(f"T3  residual spectrum {['%.1e' % x for x in spec[:5]]}  separation = {sep:.2e}")
    T2 = bool(i3_resid < 1e-3 and n_cons > n_red)
    T3 = bool(sep > 1e3)

    works = bool(T0 and T1 and T2 and T3)
    verdict = ("THE READOUT IS NOT BLIND AT DEGREE 3. Given a system with a genuine irreducible cubic "
               "invariant in a library that can represent it, the readout FINDS it: I3 lies in the conserved "
               "span (residual {:.0e}) and the residual spectrum separates by {:.0e}, against 1.7 on deformed "
               "Kerr. WHAT THIS DOES AND DOES NOT LICENSE: it removes 'the instrument cannot resolve degree 3' "
               "as a general explanation. It does NOT retroactively validate §168's degree-3 rungs -- those "
               "failed their OWN eps=0 controls and remain REFUSED on their own terms -- and it says nothing "
               "about degree 4, which still has no positive control. The open question is now specific and "
               "answerable: why did the deformed-Kerr degree-3 control fail when the readout demonstrably "
               "works at that degree?".format(i3_resid, sep)
               if works else
               "THE LADDER IS BLIND AT DEGREE 3. A known irreducible cubic invariant is present and verified "
               "(conserved to {:.0e}, irreducible R^2 {:.3f}) and the readout does NOT cleanly resolve it "
               "(I3 residual {:.0e}, separation {:.1e}). Therefore every degree-3/4 rung we have run is "
               "REFUSED, not null, and §168's 'nothing separates' says nothing about the spacetime."
               .format(dI, r2, i3_resid, sep))
    out.update({"T0_cubic_conserved": T0, "T1_cubic_irreducible": T1,
                "T2_readout_finds_it": T2, "T3_spectrum_separates": T3,
                "drift_H": dH, "drift_P": dP, "drift_I3": dI, "reducible_r2": r2,
                "n_conserved": n_cons, "n_reducible": n_red, "i3_residual_in_span": i3_resid,
                "separation": sep, "residual_spectrum": [float(x) for x in spec[:6]],
                "p": int(Fk.shape[-1]), "ladder_works_at_degree3": works, "verdict": verdict})
    print(f"\nT0 {T0} | T1 {T1} | T2 {T2} | T3 {T3}")
    print(verdict)
    (RESULTS / "169_degree3_positive_control.json").write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.semilogy(range(1, len(spec[:8]) + 1), np.maximum(spec[:8], 1e-20), "o-")
    ax.set_xlabel("residual direction")
    ax.set_ylabel("singular value (normalized)")
    ax.set_title("Degree-3 positive control (Toda cubic invariant)\n"
                 "does one direction stand out after the reducibles are removed?")
    fig.tight_layout()
    fig.savefig(RESULTS / "169_degree3_positive_control.png", dpi=140)
    print("saved results/169_degree3_positive_control.json + .png")


if __name__ == "__main__":
    main()
