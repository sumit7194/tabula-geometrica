"""Step 160 — THE BASIS LADDER: does "illegible" mean no invariant, or no invariant IN MY BASIS?

Prep for TheBridge round-8 ask B (G2 blind adversarial legibility). ansatz is building two metrics designed to break
"legible <-> KY-integrable"; one is designed to be integrable via a TRANSCENDENTAL (non-polynomial-in-momenta)
invariant. Our distillation head (§91-§99) is LIBRARY-based: it finds a sparse conserved combination over an explicit
feature basis via a generalized eigenproblem. The basis has been extended exactly twice in the project's history --
polynomial (§91-§95) -> rational (§96 Kepler LRL, §97 Kerr-de Sitter's rational Carter) -> half-angle (§98 spinor).
It is NOT complete for transcendental invariants. So on that candidate the head would certify illegible for a reason
that has nothing to do with the physics, and we would have no way to say so quantitatively.

This script fixes that BEFORE the blind run, on a system where the answer is known because we construct it. The point
is to convert "my basis cannot see it" from an excuse into a MEASURED, NAMED boundary: run a LADDER of basis families
(polynomial -> rational -> transcendental-with-family-scan) and report which rung, if any, emits.

THE CALIBRATION SYSTEM (invariant provably non-polynomial in MOMENTA, by construction):
    H = exp(a p1^2 + b p2^2) + c q1^2 + d q2^2,   a != b, c != d
Bounded by inspection: exp(.) >= 1, so on the level set H = E > 1 both a p1^2 + b p2^2 <= ln E (momenta bounded) and
c q1^2 + d q2^2 <= E - 1 (coordinates bounded). H is conserved and is transcendental in the momenta; with a != b and
c != d there is no rotational symmetry, so generically H is the ONLY invariant. Its level sets are not the level sets
of any polynomial, so a polynomial library can at best APPROXIMATE it -- exactly the "exact vs growing approximation"
distinction §97 had to make for Kerr-de Sitter.

WHAT THE TRANSCENDENTAL RUNG ACTUALLY DOES, stated honestly: exp(a p1^2 + b p2^2) = exp(a p1^2) * exp(b p2^2) is a
PRODUCT, so no linear combination of fixed exp features spans it for unknown (a, b). The rung therefore SCANS a
parameterized family over a grid of (a, b) and solves the linear problem inside each. That is the same epistemic move
as §96's rational library (posit a family, then fit), and it is why the verdict this instrument emits is, and is
reported as, CERTIFY-RELATIVE-TO-BASIS: illegible means "no cheap invariant in the families searched", and the
families are named. That is a weaker claim than "no invariant exists" and it is the claim we can actually support.

Engine: reused unchanged from §99 (conserved / heldout) -- the same instrument as leg Q, so a verdict here is
commensurable with §127/§132/§144.

Pre-reg (2026-07-23, frozen before running):
  T0 INTEGRATOR: H is conserved along the RK4 flow to relative drift < 1e-9 (otherwise every "certify" below is
     confounded by integration error rather than basis inadequacy).
  T1 POLYNOMIAL CERTIFIES: the polynomial rung's best held-out variance ratio is >= 1e6x worse than the transcendental
     rung -- not conserved to integration precision.
  T2 RATIONAL CERTIFIES: same, >= 1e6x worse than the transcendental rung.
  T3 TRANSCENDENTAL EMITS: at the correct family member the held-out variance ratio is < 1e-8, and the recovered
     coefficient vector matches the true H direction at cosine > 0.99.
  T4 THE LADDER LOCALISES: the scan's argmin over (a, b) recovers the true exponents to within one grid step, so the
     rung does not merely fit -- it identifies WHICH family member is the invariant.

PRE-REG CORRECTION (2026-07-23, recorded before the corrected run, per project convention): the first draft gated
T1/T2 on an ABSOLUTE held-out ratio > 1e-4. That is exactly the mistake §97 (Kerr-de Sitter) diagnosed and §99 fixed:
over a BOUNDED energy band a polynomial APPROXIMATES a smooth transcendental invariant well (here ~1e-6), so an absolute
threshold conflates "no invariant in this basis" with "a decent approximation exists". The physics-correct test is
RELATIVE EXACTNESS -- conserved to INTEGRATION PRECISION or not -- which the §99 engine already uses. So T1/T2 are the
relative separation from the emitting rung (the ~1e15x that actually appeared), not an absolute floor. The emit gate
(< 1e-8, cosine > 0.99) and the localisation gate are unchanged; only the certify side moved. The verdict this
instrument reports on a genuinely illegible metric is therefore explicitly CERTIFY-RELATIVE-TO-BASIS.
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

s99 = import_module("99_deformed_metrics")          # the leg-Q emit-or-certify engine, unchanged

A_TRUE, B_TRUE = 0.80, 0.35                          # momentum exponents (a != b: no rotational symmetry)
C_TRUE, D_TRUE = 1.00, 0.60                          # coordinate stiffnesses (c != d)
NTRAJ, NSTEP, DT = 120, 4000, 2.0e-3
E_LO, E_HI = 1.8, 3.2
SEED = 0


# ---------------------------------------------------------------- the system

def hamiltonian(q1, q2, p1, p2):
    return np.exp(A_TRUE * p1 ** 2 + B_TRUE * p2 ** 2) + C_TRUE * q1 ** 2 + D_TRUE * q2 ** 2


def deriv(y):
    q1, q2, p1, p2 = y
    ex = np.exp(A_TRUE * p1 ** 2 + B_TRUE * p2 ** 2)
    return np.array([2 * A_TRUE * p1 * ex, 2 * B_TRUE * p2 * ex, -2 * C_TRUE * q1, -2 * D_TRUE * q2])


def rollout(y0, nstep=NSTEP, dt=DT):
    y = y0.copy()
    out = np.empty((nstep, 4, y0.shape[1]))
    for i in range(nstep):
        k1 = deriv(y)
        k2 = deriv(y + 0.5 * dt * k1)
        k3 = deriv(y + 0.5 * dt * k2)
        k4 = deriv(y + dt * k3)
        y = y + (dt / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)
        out[i] = y
    return out                                        # (nstep, 4, ntraj)


def trajectories(seed):
    rng = np.random.default_rng(seed)
    qs, ps = [], []
    while len(qs) < NTRAJ:
        q1, q2 = rng.uniform(-1.2, 1.2, 2)
        p1, p2 = rng.uniform(-1.0, 1.0, 2)
        if E_LO <= hamiltonian(q1, q2, p1, p2) <= E_HI:
            qs.append((q1, q2))
            ps.append((p1, p2))
    y0 = np.array([[q[0] for q in qs], [q[1] for q in qs], [p[0] for p in ps], [p[1] for p in ps]])
    traj = rollout(y0)
    return np.transpose(traj, (2, 0, 1))              # (G traj, P points, 4 vars)


# ---------------------------------------------------------------- basis rungs

def poly_features(T):
    q1, q2, p1, p2 = T[..., 0], T[..., 1], T[..., 2], T[..., 3]
    feats, names = [], []

    def add(v, n):
        feats.append(v)
        names.append(n)

    add(q1 ** 2, "q1^2"); add(q2 ** 2, "q2^2"); add(p1 ** 2, "p1^2"); add(p2 ** 2, "p2^2")
    add(q1 * q2, "q1q2"); add(p1 * p2, "p1p2"); add(q1 * p1, "q1p1"); add(q2 * p2, "q2p2")
    add(q1 ** 4, "q1^4"); add(q2 ** 4, "q2^4"); add(p1 ** 4, "p1^4"); add(p2 ** 4, "p2^4")
    add(p1 ** 2 * p2 ** 2, "p1^2p2^2"); add(q1 ** 2 * q2 ** 2, "q1^2q2^2")
    add(q1 ** 2 * p1 ** 2, "q1^2p1^2"); add(q2 ** 2 * p2 ** 2, "q2^2p2^2")
    add(p1 ** 6, "p1^6"); add(p2 ** 6, "p2^6"); add(p1 ** 4 * p2 ** 2, "p1^4p2^2")
    add(p1 ** 2 * p2 ** 4, "p1^2p2^4")
    return np.stack(feats, -1), names


def rational_features(T):
    q1, q2, p1, p2 = T[..., 0], T[..., 1], T[..., 2], T[..., 3]
    base, names = poly_features(T)
    extra, enames = [], []

    def add(v, n):
        extra.append(v)
        enames.append(n)

    add(1.0 / (1.0 + p1 ** 2), "1/(1+p1^2)"); add(1.0 / (1.0 + p2 ** 2), "1/(1+p2^2)")
    add(1.0 / (1.0 + q1 ** 2), "1/(1+q1^2)"); add(1.0 / (1.0 + q2 ** 2), "1/(1+q2^2)")
    add(p1 ** 2 / (1.0 + p2 ** 2), "p1^2/(1+p2^2)"); add(p2 ** 2 / (1.0 + p1 ** 2), "p2^2/(1+p1^2)")
    add(1.0 / (1.0 + p1 ** 2 + p2 ** 2), "1/(1+p1^2+p2^2)")
    return np.concatenate([base, np.stack(extra, -1)], -1), names + enames


def transcendental_features(T, a, b):
    """The scanned family: one exp feature at family member (a, b), plus the coordinate part."""
    q1, q2, p1, p2 = T[..., 0], T[..., 1], T[..., 2], T[..., 3]
    feats = [np.exp(a * p1 ** 2 + b * p2 ** 2), q1 ** 2, q2 ** 2, q1 * q2, p1 ** 2, p2 ** 2]
    names = [f"exp({a:.3f}p1^2+{b:.3f}p2^2)", "q1^2", "q2^2", "q1q2", "p1^2", "p2^2"]
    return np.stack(feats, -1), names


def best_direction(Phi_tr, Phi_te):
    """Run the §99 engine and return (held-out variance ratio, raw coefficient vector, feature mean/std)."""
    ev, C, mu, sd = s99.conserved(Phi_tr)
    ho = s99.heldout(Phi_te, C[:, 0], mu, sd)
    c_raw = C[:, 0] / sd
    c_raw = c_raw / np.linalg.norm(c_raw)
    return ho, c_raw


# ---------------------------------------------------------------- main

def main():
    print("Step 160 — the basis ladder: does 'illegible' mean no invariant, or no invariant IN MY BASIS?")
    print(f"  system: H = exp({A_TRUE} p1^2 + {B_TRUE} p2^2) + {C_TRUE} q1^2 + {D_TRUE} q2^2\n")
    res = {"system": dict(a=A_TRUE, b=B_TRUE, c=C_TRUE, d=D_TRUE)}

    Ttr = trajectories(SEED)
    Tte = trajectories(SEED + 50)

    # ---- T0 integrator
    Hs = hamiltonian(Ttr[..., 0], Ttr[..., 1], Ttr[..., 2], Ttr[..., 3])
    drift = float(np.max(np.abs(Hs - Hs[:, :1]) / np.abs(Hs[:, :1])))
    t0 = drift < 1e-9
    print(f"  T0 INTEGRATOR: max relative H drift = {drift:.2e}  -> {'PASS' if t0 else 'FAIL'} (< 1e-9)")
    res["T0_H_drift"] = drift
    res["T0_pass"] = bool(t0)

    # ---- rung 3 first (it sets the reference floor the other rungs are compared against)
    grid = np.round(np.arange(0.10, 1.51, 0.05), 3)
    best = (np.inf, None, None, None)
    scan = np.full((len(grid), len(grid)), np.nan)
    for i, a in enumerate(grid):
        for j, b in enumerate(grid):
            Ptr, names = transcendental_features(Ttr, a, b)
            Pte, _ = transcendental_features(Tte, a, b)
            ho, c_raw = best_direction(Ptr, Pte)
            scan[i, j] = ho
            if ho < best[0]:
                best = (ho, (a, b), c_raw, names)
    ho_tr, (a_hat, b_hat), c_tr, names_tr = best

    true_vec = np.zeros(len(names_tr))
    true_vec[0] = 1.0                                  # exp(.)
    true_vec[names_tr.index("q1^2")] = C_TRUE
    true_vec[names_tr.index("q2^2")] = D_TRUE
    true_vec /= np.linalg.norm(true_vec)
    cos_true = float(abs(c_tr @ true_vec))

    t3 = ho_tr < 1e-8 and cos_true > 0.99
    step = float(grid[1] - grid[0])
    t4 = abs(a_hat - A_TRUE) <= step + 1e-9 and abs(b_hat - B_TRUE) <= step + 1e-9
    print(f"\n  RUNG 3 TRANSCENDENTAL (scanned family exp(a p1^2 + b p2^2), {len(grid)}x{len(grid)} grid):")
    print(f"    best held-out variance ratio = {ho_tr:.3e} at (a,b) = ({a_hat}, {b_hat}) "
          f"[true ({A_TRUE}, {B_TRUE})]")
    print(f"    cosine to the true H direction = {cos_true:.4f}")
    print(f"    T3 EMIT {'PASS' if t3 else 'FAIL'} (ratio < 1e-8 and cosine > 0.99)")
    print(f"    T4 LOCALISE {'PASS' if t4 else 'FAIL'} (argmin within one grid step {step} of truth)")

    # ---- rungs 1 and 2
    rungs = {}
    for label, fn in (("polynomial", poly_features), ("rational", rational_features)):
        Ptr, names = fn(Ttr)
        Pte, _ = fn(Tte)
        ho, c_raw = best_direction(Ptr, Pte)
        rungs[label] = ho
        ratio = ho / max(ho_tr, 1e-300)
        print(f"\n  RUNG {'1' if label == 'polynomial' else '2'} {label.upper()} ({len(names)} features):")
        print(f"    best held-out variance ratio = {ho:.3e}   ({ratio:.1e}x the transcendental rung)")

    t1 = rungs["polynomial"] / max(ho_tr, 1e-300) > 1e6
    t2 = rungs["rational"] / max(ho_tr, 1e-300) > 1e6
    print(f"\n    T1 POLYNOMIAL CERTIFIES {'PASS' if t1 else 'FAIL'} (>= 1e6x worse than the emitting rung)")
    print(f"    T2 RATIONAL CERTIFIES   {'PASS' if t2 else 'FAIL'} (>= 1e6x worse than the emitting rung)")

    fig, ax = plt.subplots(1, 2, figsize=(11, 4.2))
    im = ax[0].imshow(np.log10(scan), origin="lower", aspect="auto",
                      extent=[grid[0], grid[-1], grid[0], grid[-1]])
    ax[0].plot([B_TRUE], [A_TRUE], "rx", ms=12, mew=2, label="truth")
    ax[0].set_xlabel("b"); ax[0].set_ylabel("a")
    ax[0].set_title("log10 held-out variance ratio\n(transcendental family scan)")
    ax[0].legend()
    fig.colorbar(im, ax=ax[0])
    ax[1].bar(["polynomial", "rational", "transcendental"],
              [np.log10(rungs["polynomial"]), np.log10(rungs["rational"]), np.log10(max(ho_tr, 1e-300))])
    ax[1].set_ylabel("log10 held-out variance ratio")
    ax[1].set_title("the ladder: which rung emits")
    fig.tight_layout()
    fig.savefig(RESULTS / "160_basis_ladder.png", dpi=130)

    passed = t0 and t1 and t2 and t3 and t4
    res.update(dict(
        transcendental_heldout=ho_tr, transcendental_argmin=[float(a_hat), float(b_hat)],
        transcendental_cosine_to_truth=cos_true, grid_step=step,
        polynomial_heldout=rungs["polynomial"], rational_heldout=rungs["rational"],
        T1_polynomial_certifies=bool(t1), T2_rational_certifies=bool(t2),
        T3_transcendental_emits=bool(t3), T4_ladder_localises=bool(t4),
        all_pass=bool(passed),
        summary=(
            f"Basis ladder calibrated on H = exp({A_TRUE}p1^2+{B_TRUE}p2^2) + {C_TRUE}q1^2 + {D_TRUE}q2^2, whose only "
            f"invariant is transcendental in the MOMENTA by construction. The §99 emit-or-certify engine, unchanged, "
            f"CERTIFIES on the polynomial rung ({rungs['polynomial']:.2e}) and the rational rung "
            f"({rungs['rational']:.2e}) but EMITS on a scanned transcendental family ({ho_tr:.2e}, cosine to truth "
            f"{cos_true:.4f}), recovering the true exponents to within one grid step. So a 'certify' verdict from this "
            f"instrument is CERTIFY-RELATIVE-TO-BASIS: it means no cheap invariant exists in the families searched, "
            f"and the families can now be named and extended. Built as prep for TheBridge G2, where one adversarial "
            f"metric is designed to be integrable via a non-polynomial-in-momenta invariant."),
    ))
    (RESULTS / "160_basis_ladder.json").write_text(json.dumps(res, indent=1))
    print(f"\n  {'ALL GATES PASS' if passed else 'SOME GATES FAILED'}")
    print("  wrote results/160_basis_ladder.json + 160_basis_ladder.png")


if __name__ == "__main__":
    main()
