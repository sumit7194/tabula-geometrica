"""Step 172 — THE DEGREE-4 POSITIVE CONTROL IN GEODESIC FLOW. Closing P3's last instrument gap.

WHY THIS AND NOT §171. §171 gave degree 4 a positive control in a NATURAL Hamiltonian (Toda tr L^4, 5/5). That
tests the readout but not the setting: P3 asks about Killing tensors of a SPACETIME, i.e. geodesic flow, which is
also the only setting where the grading argument (bracket raises momentum degree by exactly one) applies. A
control in the wrong setting leaves the actual rung uncontrolled.

THE SUBSTRATE. Cariglia & Galajinsky, arXiv:1503.02162, Eq (26): a five-dimensional Ricci-flat spacetime of
signature (2,3) admitting an irreducible RANK-4 Killing tensor, obtained by oxidising Drach's cubic-integral
system with respect to a free parameter. ansatz independently identified this as the route and asked that it be
built independently rather than taken from them; this is that build.

    dtau^2 = -2( alpha*y + gamma/sqrt(x) - (alpha*x)^2/2 ) dt^2 + 2 dt ds + 2 dx dy + 2 alpha*x dt dw + dw^2

THE TARGET, AND A TRANSCRIPTION TRAP WORTH RECORDING. Eq (29) lists the rank-4 Killing tensor. Transcribed
directly as read, the contraction is NOT conserved (relative drift 3.0e-01, under either index convention and on
null or generic geodesics). Deriving it instead -- from Eq (24)'s quartic charge, which DOES transcribe correctly
(verified conserved to 1.6e-14), uplifted via Eq (28)'s velocity relations and multiplied by (dt/dtau)^4 --
gives a conserved quantity, and expanding it term by term reproduces every component of Eq (29) except one index
label: the third component must be K_ttxw (t,t,x,w), NOT K_tttw (t,t,t,w). Same value alpha*x/6; the multiplicity
changes 4 -> 12 and that is exactly what closes it. Confirmed: K_tttw reading drifts 3.02e-01, K_ttxw reading is
conserved to 3.6e-14.

RESOLVED, and it makes the derivation worth more than a transcription would have been. ansatz fetched Eq (29)
from the paper's HTML rendering: the published text reads K_ttxw. So the PAPER IS CORRECT and our PDF-to-text
path collapsed the `x` into a `t`. No erratum, nothing to report to the authors -- and the derived tensor
INDEPENDENTLY RECOVERED WHAT THE AUTHORS ACTUALLY PUBLISHED, index placement included, from a source that had it
wrong. THE FAILURE MODE IS STILL THE DANGEROUS ONE and the warning stands for anyone transcribing from a PDF: a
silently wrong target tensor makes a prover fail to find the known invariant, which reads as "the control failed"
or, far worse, as "no rank-4 KT exists" -- a transcription error presenting as a null. The general rule, which is
the same one that says verify a transcribed metric is Ricci-flat before calling it a spacetime: VERIFY THE
PAPER\'S INVARIANT IS CONSERVED BEFORE USING IT AS A TARGET. The input to a null must be validated, or the null
is about your transcription.

BASIS, NAMED (C1). Monomials of total degree <= 4 in the five geodesic VELOCITIES u^A = dz^A/dtau, times a
coordinate family {1, x, x^2, 1/sqrt(x), y, x*y}. Velocities rather than momenta because K's coefficients are
simple in u and messy in p; p_A = g_AB u^B is linear at each point so the span is equivalent, and every reducible
below is representable in it (checked, not assumed).

PRE-REGISTERED, every criterion with a KNOWN-PASS AND A KNOWN-FAIL (the rule adopted after two pre-registrations
in one day turned out to be the faulty check):
  G0 SUBSTRATE VERIFIED BEFORE USE (ansatz's Taub-NUT lesson: their metric was neither Taub-NUT nor vacuum).
     (a) Ricci-flat, computed by autograd -- known-fail: the paper's Eq (4) says R_tt = 2*U_xy is the ONLY
         nonzero Ricci component, so adding a c*x*y term to U must produce exactly R_tt = 2c and nothing else.
     (b) H and the three Killing momenta conserved; (c) the derived K conserved;
     (d) known-fail: a smooth NON-conserved function of the state must drift.
  G1 K IS IRREDUCIBLE -- not a function of the lower-degree invariants {p_t, p_s, p_w, H} up to degree 4.
  G2 THE INSTRUMENT CONTROL: the readout finds it -- conserved count exceeds the measured reducible rank by
     exactly one, and K lies in the conserved span.
  G3 the residual spectrum SEPARATES after projecting off the reducibles.
  G4 KNOWN-FAIL: a smooth non-conserved degree-4 function must NOT be admitted.

The reducible rank is MEASURED, never hand-counted -- ansatz expected 6 on their control and the truth was 10,
because that system is superintegrable. IF G2/G3 FAIL: the ladder is blind at degree 4 in geodesic flow, and
every degree-4 rung run on a spacetime is REFUSED rather than null. Both outcomes are pre-registered.

RESULT: G2 FAILS, and the pre-registered consequence stands. The substrate is verified (Ricci-flat exactly, with
the known-fail reproducing the paper\'s own R_tt = 2*U_xy prediction to the digit), K is representable (2.9e-15),
genuinely conserved (1.8e-13) and verified irreducible (R^2 = 0.40 on 45 measured reducibles) -- and the readout
STILL does not isolate it: K\'s residual in the top-46 conserved span is 2.6e-02, against a smooth non-conserved
control at 1.8e-01. Roughly 30 directions are well conserved where 45 reducibles plus K exist.

THE MECHANISM, which is the useful part. In geodesic flow the degree-4 reducible algebra is 45 elements generated
by only FOUR quantities (p_t, p_s, p_w, H), so its members are inherently near-collinear -- §167\'s near-parallel
powers at scale. The extraction cannot isolate one irreducible direction inside a large, nearly degenerate
reducible span. §171 works precisely because Toda\'s degree-4 reducible set is 10 elements and well separated.

ONE FIX ROUND SPENT, and it failed informatively: widening the ensemble\'s momentum spread (the §167 remedy) makes
it WORSE -- at spread 0.8 and 1.5 there are ZERO directions below 1e-9 and the known-fail residual falls to
5.5e-02 / 9.1e-02, converging on K\'s and destroying what discrimination remained. Stopped there per the
one-fix-round rule rather than tuning until it passed.

WHAT THIS LICENSES -- SCOPED TO THE READOUT, which is narrower than the first draft of this docstring claimed.
ansatz\'s correction, accepted: near-collinearity is a property of a FLOATING-POINT spectrum. Over GF(p) two
vectors are either dependent or independent and there is no condition number, so their exact-arithmetic prover
faces no such wall -- and indeed it returns one irreducible against ten reducibles (generated by three
quantities) on this same substrate at rank 3, in 1.4 seconds. **So this is a statement about NUMERICAL SCREENING
at degree 4, not about degree 4.** The question stays answerable; this instrument is what cannot answer it.

Bounded further by §173: at a TWO-Killing-vector restriction of this same substrate the readout DOES isolate K
(residual 2.79e-06 against a control at 2.02e-01). Bumped Kerr has two Killing vectors, so this failure does not
transfer to it and §168\'s degree-4 rungs deserve a rerun rather than a refusal. What remains established here is
that the numerical readout fails on THIS substrate, with three Killing vectors and a 70-element reducible list.
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

s99 = import_module("99_deformed_metrics")
torch.set_default_dtype(torch.float64)
np.seterr(all="ignore")

AL, GA = 0.3, 0.5                      # alpha, gamma
FAST = "--fast" in sys.argv[1:]
NTRAJ = 150 if FAST else 300
NSTEP = 6000 if FAST else 9000
STRIDE = 40 if FAST else 45
DT = 0.001
# The integration window is LOAD-BEARING and was set by measurement, not taste. At 1500 steps the geodesics
# barely move (mean x-spread 0.22) and the readout collapses: K's own best fit is conserved only to 4.1e-07 and
# the engine's spectrum is flat at ~2.5e-04 with no separation at all. At 6000 steps (x-spread 0.90) K's fit
# reaches 7.6e-23. An ensemble that does not EXPLORE cannot distinguish a conserved direction from a slowly
# varying one -- every direction looks conserved over a short enough arc.
X_LO, X_HI = 0.3, 60.0


def metric(x, y, cxy=0.0):
    """Eq (26). `cxy` adds a NON-additive c*x*y term to U -- the known-fail for the Ricci check."""
    U = AL * y + GA / torch.sqrt(x) - (AL * x) ** 2 / 2 + cxy * x * y
    n = x.shape[0]
    g = torch.zeros(n, 5, 5, dtype=x.dtype)
    g[:, 0, 0] = -2 * U
    g[:, 0, 1] = g[:, 1, 0] = 1.0
    g[:, 2, 3] = g[:, 3, 2] = 1.0
    g[:, 0, 4] = g[:, 4, 0] = AL * x
    g[:, 4, 4] = 1.0
    return g


def ricci(x0, y0, cxy=0.0):
    """R_AB by autograd. g depends only on (x, y), so only d/dx and d/dy are nonzero."""
    xy = torch.tensor([[x0, y0]], requires_grad=True)

    def gof(v):
        return metric(v[:, 0], v[:, 1], cxy)[0]

    J = torch.autograd.functional.jacobian(gof, xy, vectorize=True).reshape(5, 5, 2)
    Hs = torch.autograd.functional.hessian(lambda v: gof(v).sum(), xy)  # placeholder, recomputed below
    d2 = torch.zeros(5, 5, 2, 2)
    for b in range(5):
        for c in range(5):
            hh = torch.autograd.functional.hessian(lambda v, b=b, c=c: gof(v)[b, c], xy, vectorize=True)
            d2[b, c] = hh.reshape(2, 2)
    g = gof(xy).detach()
    gi = torch.linalg.inv(g)
    dg = torch.zeros(5, 5, 5)                     # dg[a,b,c] = d_a g_bc
    dg[2] = J[:, :, 0]
    dg[3] = J[:, :, 1]
    ddg = torch.zeros(5, 5, 5, 5)                 # ddg[a,d,b,c] = d_a d_d g_bc
    for a_i, a in enumerate((2, 3)):
        for d_i, d in enumerate((2, 3)):
            ddg[a, d] = d2[:, :, a_i, d_i]
    Gam = 0.5 * torch.einsum('ad,bdc->abc', gi, dg.permute(1, 0, 2) * 0 + dg.permute(1, 0, 2)) * 0
    Gam = torch.zeros(5, 5, 5)
    for a in range(5):
        for b in range(5):
            for c in range(5):
                Gam[a, b, c] = 0.5 * sum(gi[a, d] * (dg[b, d, c] + dg[c, d, b] - dg[d, b, c]) for d in range(5))
    dGam = torch.zeros(5, 5, 5, 5)                # dGam[e,a,b,c] = d_e Gamma^a_bc
    for e in (2, 3):
        for a in range(5):
            for b in range(5):
                for c in range(5):
                    t = 0.0
                    for d in range(5):
                        dgi = -sum(gi[a, m] * dg[e, m, n] * gi[n, d] for m in range(5) for n in range(5))
                        t += 0.5 * dgi * (dg[b, d, c] + dg[c, d, b] - dg[d, b, c])
                        t += 0.5 * gi[a, d] * (ddg[e, b, d, c] + ddg[e, c, d, b] - ddg[e, d, b, c])
                    dGam[e, a, b, c] = t
    R = torch.zeros(5, 5)
    for b in range(5):
        for c in range(5):
            t = 0.0
            for a in range(5):
                t += dGam[a, a, b, c] - dGam[c, a, b, a]
                for d in range(5):
                    t += Gam[a, a, d] * Gam[d, b, c] - Gam[a, c, d] * Gam[d, b, a]
            R[b, c] = t
    return R


def ham(z, p):
    gi = torch.linalg.inv(metric(z[:, 2], z[:, 3]))
    return 0.5 * torch.einsum('nab,na,nb->n', gi, p, p)


def deriv(z, p):
    zz = z.detach().requires_grad_(True)
    H = ham(zz, p.detach())
    dHdz, = torch.autograd.grad(H.sum(), [zz])
    with torch.no_grad():
        gi = torch.linalg.inv(metric(z[:, 2], z[:, 3]))
        return torch.einsum('nab,nb->na', gi, p), -dHdz


def geodesics(seed=0, n=None):
    n = n or NTRAJ
    g = np.random.default_rng(seed)
    z = torch.tensor(np.stack([g.uniform(0, 1, n), g.uniform(0, 1, n), g.uniform(2.0, 3.0, n),
                               g.uniform(-1, 1, n), g.uniform(-1, 1, n)], -1))
    p = torch.tensor(g.uniform(-0.3, 0.3, (n, 5)))
    alive = torch.ones(n, dtype=torch.bool)
    rec = []
    for i in range(NSTEP):
        k1z, k1p = deriv(z, p)
        k2z, k2p = deriv(z + .5 * DT * k1z, p + .5 * DT * k1p)
        k3z, k3p = deriv(z + .5 * DT * k2z, p + .5 * DT * k2p)
        k4z, k4p = deriv(z + DT * k3z, p + DT * k3p)
        z = z + DT / 6 * (k1z + 2 * k2z + 2 * k3z + k4z)
        p = p + DT / 6 * (k1p + 2 * k2p + 2 * k3p + k4p)
        alive = alive & torch.isfinite(z).all(-1) & torch.isfinite(p).all(-1) \
            & (z[:, 2] > X_LO) & (z[:, 2] < X_HI)
        z = torch.where(alive[:, None], z, torch.tensor([0., 0., 1., 0., 0.]))
        p = torch.where(alive[:, None], p, torch.zeros(5))
        if i % STRIDE == 0:
            rec.append(torch.cat([z, p], -1))
    T = torch.stack(rec, 1)[alive]
    return T.numpy()


def vels(T):
    Z, P = torch.tensor(T[..., :5]), torch.tensor(T[..., 5:])
    gi = torch.linalg.inv(metric(Z[..., 2].reshape(-1), Z[..., 3].reshape(-1))).reshape(*Z.shape[:-1], 5, 5)
    return torch.einsum('...ab,...b->...a', gi, P).numpy()


def K_of(T):
    """The DERIVED rank-4 invariant (see module docstring): Eq (29)'s values with the third component read as
    K_ttxw. Multinomial weights: 4 for a 3+1 index pattern, 12 for 2+1+1."""
    x = T[..., 2]
    u = vels(T)
    ut, us, ux, uy, uw = [u[..., i] for i in range(5)]
    return (4 * ((AL * x) ** 2 / 2 + GA / (4 * np.sqrt(x))) * ut ** 3 * ux
            + 4 * (AL * x / 2) * ut ** 3 * uy
            + 12 * (AL * x / 6) * ut ** 2 * ux * uw
            + 4 * (AL * x / 4) * ut * ux ** 3
            + 12 * (1 / 12) * ut * ux ** 2 * uy
            + 4 * (1 / 4) * ux ** 3 * uw)


def H_of(T):
    Z, P = torch.tensor(T[..., :5]), torch.tensor(T[..., 5:])
    return ham(Z.reshape(-1, 5), P.reshape(-1, 5)).reshape(T.shape[:-1]).numpy()


def known_fail(T):
    """Smooth, NOT conserved. Must drift, and must be excluded by the readout."""
    u = vels(T)
    return T[..., 2] * u[..., 0] + 0.3 * u[..., 2] ** 2


def reducibles(T):
    """Monomials in the Killing momenta {p_t, p_s, p_w} and H, total degree <= 4. The RANK of this set is
    measured downstream, never assumed."""
    P = T[..., 5:]
    pt, ps, pw = P[..., 0], P[..., 1], P[..., 4]
    H = H_of(T)
    out = []
    base = [(pt, "pt"), (ps, "ps"), (pw, "pw")]
    for i, (a, na) in enumerate(base):
        out.append((a, na))
        for j, (b, nb) in enumerate(base[i:], i):
            out.append((a * b, f"{na}{nb}"))
            for k, (c, nc) in enumerate(base[j:], j):
                out.append((a * b * c, f"{na}{nb}{nc}"))
                for d, nd in base[k:]:
                    out.append((a * b * c * d, f"{na}{nb}{nc}{nd}"))
    out.append((H, "H"))
    for a, na in base:
        out.append((a * H, f"{na}H"))
        for b, nb in base:
            out.append((a * b * H, f"{na}{nb}H"))
    out.append((H * H, "HH"))
    return out


def library(T):
    u = vels(T)
    x, y = T[..., 2], T[..., 3]
    one = np.ones_like(x)
    # The metric's own potential U is a basis element, not y and x*y. y grows SECULARLY along geodesics, so
    # y-bearing columns are non-stationary and wreck conditioning: with {y, xy} the engine's best direction sits
    # at 3.9e-07, with U it reaches 4.2e-12. U also keeps H representable in ONE column instead of several
    # (H needs U*(u^t)^2), so nothing is lost -- measured, both H and K represent to ~3e-15 either way.
    U = AL * y + GA / np.sqrt(x) - (AL * x) ** 2 / 2
    coord = [(one, "1"), (x, "x"), (x ** 2, "x2"), (1 / np.sqrt(x), "xinvsqrt"), (U, "U")]
    feats, names = [], []
    for e in _mono(5, 4):
        mv = one.copy()
        lab = ""
        for j, ej in enumerate(e):
            if ej:
                mv = mv * u[..., j] ** ej
                lab += f"u{j}^{ej}"
        for cv, cn in coord:
            if not lab and cn == "1":
                continue
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


def cond_basis(F, tol=1e-9):
    Fm = F.reshape(-1, F.shape[-1])
    sc = Fm.std(0) + 1e-300
    _, sv, Vt = np.linalg.svd(Fm / sc, full_matrices=False)
    return (Vt[:int((sv > sv[0] * tol).sum())].T / sc[:, None])


def rel_drift(A):
    return float(np.mean(A.std(1) / (np.abs(A.mean(1)) + 1e-30)))


def var_ratio(A):
    return float(np.mean([A[i].var() for i in range(len(A))]) / (A.reshape(-1).var() + 1e-30))


def in_span(vals, target):
    X = np.concatenate([vals, np.ones((len(vals), 1))], 1)
    c, *_ = np.linalg.lstsq(X, target, rcond=None)
    return float(np.linalg.norm(X @ c - target) / (np.linalg.norm(target - target.mean()) + 1e-300))


def gap_rank(M):
    Z = (M - M.mean(0)) / (M.std(0) + 1e-300)
    sv = np.linalg.svd(Z, compute_uv=False)
    lg = np.log10(np.maximum(sv, sv[0] * 1e-300))
    gaps = np.diff(lg)
    return int(np.argmin(gaps) + 1) if len(gaps) and gaps.min() < -3.0 else len(sv)


def main():
    out = {"substrate": "Cariglia-Galajinsky arXiv:1503.02162 Eq (26), 5D Ricci-flat, signature (2,3)",
           "why": "the degree-4 positive control in GEODESIC FLOW; §171 had it only for a natural Hamiltonian",
           "alpha": AL, "gamma": GA}

    # ---- G0(a) Ricci-flat, with a known-fail ----
    R0 = ricci(2.5, 0.3, cxy=0.0)
    C = 0.25
    R1 = ricci(2.5, 0.3, cxy=C)
    off = float(R1[0, 0])
    rest = float((R1 - torch.diag(torch.tensor([R1[0, 0], 0., 0., 0., 0.]))).abs().max())
    print(f"G0a Ricci: max|R_AB| additive U = {float(R0.abs().max()):.2e}  (must be ~0)")
    print(f"    known-fail (U += {C}*x*y): R_tt = {off:.4f} vs predicted 2c = {2*C:.4f}; "
          f"max|other component| = {rest:.2e}")
    G0a = bool(float(R0.abs().max()) < 1e-8 and abs(off - 2 * C) < 1e-6 and rest < 1e-8)

    Ttr, Tte = geodesics(seed=1), geodesics(seed=51)
    print(f"    ensemble: {len(Ttr)} train / {len(Tte)} test geodesics, {Ttr.shape[1]} samples each")

    # ---- G0(b,c,d) conservation, with a known-fail ----
    dH, dK, dkf = rel_drift(H_of(Tte)), rel_drift(K_of(Tte)), rel_drift(known_fail(Tte))
    dkill = max(rel_drift(Tte[..., 5]), rel_drift(Tte[..., 6]), rel_drift(Tte[..., 9]))
    print(f"G0  drift: H {dH:.2e}  Killing momenta {dkill:.2e}  K(rank-4) {dK:.2e}  |  known-fail {dkf:.2e}")
    G0 = bool(G0a and dH < 1e-10 and dkill < 1e-10 and dK < 1e-10 and dkf > 1e-3)

    # ---- G1 irreducibility ----
    red = reducibles(Tte)
    R = np.stack([v.mean(1) for v, _ in red], 1)
    rank_red = gap_rank(R)
    yK = K_of(Tte).mean(1)
    r2 = 1 - in_span(R, yK) ** 2
    print(f"G1  K on {R.shape[1]} reducibles (measured rank {rank_red}): R^2 = {r2:.6f}")
    G1 = bool(r2 < 0.99)

    # ---- G2/G3/G4 the instrument control ----
    Fa, names = library(Ttr)
    Fb, _ = library(Tte)
    V = cond_basis(Fa)
    Fk, Ftek = Fa @ V, Fb @ V
    ev, Cm, mu, sd = s99.conserved(Fk)
    ratios = np.array([s99.heldout(Ftek, Cm[:, k], mu, sd) for k in range(Cm.shape[1])])
    order = np.argsort(ratios)
    rs = ratios[order]
    floor = max(var_ratio(H_of(Tte)), var_ratio(Tte[..., 5]))
    n_cons = int((rs <= floor * 1e3).sum())
    cons = np.stack([(((Ftek - mu) / sd) @ Cm[:, k]).mean(1) for k in order[:n_cons]], 1) \
        if n_cons else np.zeros((len(Tte), 0))
    k_res = in_span(cons, yK) if n_cons else 1.0
    kf_res = in_span(cons, known_fail(Tte).mean(1)) if n_cons else 1.0
    Rz = (R - R.mean(0)) / (R.std(0) + 1e-300)
    Q, _ = np.linalg.qr(Rz)
    Cz = (cons - cons.mean(0)) / (cons.std(0) + 1e-300) if n_cons else np.zeros((len(Tte), 0))
    resid = Cz - Q @ (Q.T @ Cz) if n_cons else Cz
    spec = np.linalg.svd(resid, compute_uv=False) if n_cons else np.zeros(0)
    spec = spec / (spec[0] + 1e-300) if len(spec) else spec
    sep = float(spec[0] / spec[1]) if len(spec) > 1 else float("inf")
    print(f"G2  p={Fk.shape[-1]}  conserved={n_cons}  reducible rank={rank_red}  K residual in span={k_res:.2e}")
    print(f"G3  residual spectrum {['%.1e' % v for v in spec[:5]]}  separation={sep:.2e}")
    print(f"G4  known-fail residual={kf_res:.2e} "
          f"({'correctly EXCLUDED' if kf_res > 1e-2 else 'WRONGLY ADMITTED'})")
    # G3 and G4 are UNDEFINED when nothing was found, not passing. With n_cons = 0 an empty spectrum reports
    # separation = inf and an empty span "excludes" every control -- two passes by construction, which is the
    # exact failure this project catalogued (a control that cannot fail is not a control). Caught in our own
    # output before committing; they now report REFUSED rather than True.
    evaluable = n_cons > 0
    G2 = bool(k_res < 1e-3 and n_cons > rank_red)
    G3 = bool(evaluable and sep > 1e3)
    G4 = bool(evaluable and kf_res > 1e-2)
    if not evaluable:
        print("    G3/G4 REFUSED: nothing was found, so neither the spectrum nor the exclusion test is defined")

    works = bool(G0 and G1 and G2 and G3 and G4)
    out.update({"G3_G4_evaluable": bool(evaluable),
                "G0_substrate_verified": G0, "G0a_ricci_flat": G0a, "G1_irreducible": G1,
                "G2_readout_finds_it": G2, "G3_spectrum_separates": G3, "G4_known_fail_excluded": G4,
                "ricci_max_additive": float(R0.abs().max()), "ricci_knownfail_Rtt": off,
                "ricci_knownfail_predicted": 2 * C, "drift_H": dH, "drift_killing": dkill,
                "drift_K": dK, "drift_known_fail": dkf, "reducible_r2": r2,
                "n_reducible_measured": rank_red, "n_conserved": n_cons, "k_residual_in_span": k_res,
                "known_fail_residual": kf_res, "separation": sep, "p": int(Fk.shape[-1]),
                "residual_spectrum": [float(v) for v in spec[:6]],
                "works_at_degree4_geodesic": works,
                "eq29_transcription_note": ("Eq (29) as read does NOT give a conserved quantity (drift 3.0e-01). "
                                            "The third component must be K_ttxw (t,t,x,w), not K_tttw; same value "
                                            "alpha*x/6, multiplicity 4 -> 12. Derived from Eq (24) + Eq (28) and "
                                            "cross-checked term by term against every other component."),
                "verdict": ("THE READOUT IS NOT BLIND AT DEGREE 4 IN GEODESIC FLOW. On a Ricci-flat spacetime "
                            "carrying a genuine irreducible rank-4 Killing tensor, the readout finds it (K in the "
                            "conserved span at {:.0e}, separation {:.0e}) and correctly excludes a smooth "
                            "non-conserved control ({:.0e}). A degree-4 null on a spacetime is therefore a "
                            "statement about the basis, not about the instrument.".format(k_res, sep, kf_res)
                            if works else
                            "NOT ESTABLISHED at degree 4 in geodesic flow -- see which G failed. If G2/G3 are "
                            "the failures, every degree-4 rung run on a spacetime is REFUSED, not null.")})
    print(f"\nG0 {G0} | G1 {G1} | G2 {G2} | G3 {G3} | G4 {G4}")
    print(out["verdict"])
    (RESULTS / "172_degree4_geodesic_control.json").write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(figsize=(8, 5))
    if len(spec):
        ax.semilogy(range(1, len(spec[:8]) + 1), np.maximum(spec[:8], 1e-20), "o-")
    ax.set_xlabel("residual direction")
    ax.set_ylabel("singular value (normalized)")
    ax.set_title("Degree-4 positive control in GEODESIC FLOW (Cariglia-Galajinsky rank-4 KT)\n"
                 "one direction standing out after the reducibles are removed")
    fig.tight_layout()
    fig.savefig(RESULTS / "172_degree4_geodesic_control.png", dpi=140)
    print("saved results/172_degree4_geodesic_control.json + .png")


if __name__ == "__main__":
    main()
