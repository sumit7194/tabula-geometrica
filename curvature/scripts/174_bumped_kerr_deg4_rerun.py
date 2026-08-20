"""Step 174 — RERUN §168's degree-4 rungs on bumped Kerr, with the readout §173 validated for this regime.

WHY REOPEN A CLOSED RUNG. §168 REFUSED its degree-4 rungs on bumped Kerr. §172 then appeared to justify that --
the readout could not isolate a KNOWN rank-4 Killing tensor on the Cariglia-Galajinsky substrate. But §173 showed
the CG substrate is HARDER than bumped Kerr: CG has THREE Killing vectors and a 70-element reducible list, and at
a TWO-Killing-vector restriction of the same substrate the readout isolates the known rank-4 tensor cleanly --
K residual 2.79e-06 against a non-conserved control at 2.02e-01, five orders. Bumped Kerr has two Killing
vectors. So the refusal rested on a control drawn from the hardest available case, and the rung deserves a rerun.

HOW THE INSTRUMENT IS VALIDATED HERE, STATED PLAINLY BECAUSE IT IS THE WEAK POINT. Bumped Kerr has NO known
irreducible rank-4 Killing tensor -- that is the open question -- so no positive control can be run ON THIS
SUBSTRATE. The validation is therefore BY REGIME MATCH: §173 validated this readout at degree 4 on a substrate
with two Killing vectors and a reducible list of 30, and we check below that bumped Kerr's reducible list is
comparable. **That is an argument, not an on-substrate measurement**, and it is weaker than §169/§171/§172's
controls. It is reported as such and the verdict is scoped accordingly.

THE READOUT is §172's, which is the one §173 validated: geodesic VELOCITIES rather than momenta, a named
coordinate family, conserved directions from the held-out within/total ratio, then K-style residual-in-span
against a smooth non-conserved control that must score worse.

PRE-REGISTERED:
  R0 REGIME MATCH: bumped Kerr's degree-4 reducible list is comparable to the validated regime (order 30, not 70),
     and its exploration matches (the §172 lesson -- an ensemble that does not explore cannot distinguish a
     conserved direction from a slowly varying one). If the regime does NOT match, the rerun is REFUSED and
     §168's refusal stands.
  R1 CHAIN CHECK at eps=0: the readout recovers the reducibles and Carter's degree-4 products on undeformed Kerr.
     Known-fail: a smooth non-conserved degree-4 function must NOT be admitted.
  R2 THE QUESTION, at eps = 2, 5, 10: after projecting off the measured reducibles, does ANY direction survive as
     conserved out-of-sample? Survivor -> ESCALATE (a lead for ansatz's exact prover, never a claim).
     None -> CERTIFY-NO-INVARIANT-IN[named family, degree 4], scoped to the family and to this readout.
  R3 STABILITY: any survivor must be stable across the eps sweep. A count that moves with the deformation is a
     noise floor, not an invariant (the §168 lesson that withdrew 31/15/12).

WHAT THIS CANNOT DO. A CERTIFY here is relative to the named family and to a numerically-screened readout whose
validation is by regime match. ansatz's exact GF(p) prover has no conditioning wall and is the instrument that
can settle it; this produces a lead or a cheap rule-out, never a theorem.
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

m168 = import_module("168_bumped_kerr_screen")
m172 = import_module("172_degree4_geodesic_control")
s99 = m168.s99
torch.set_default_dtype(torch.float64)
np.seterr(all="ignore")

# The conditioning truncation was itself the limit on representability -- catalogue mode 2, "the conditioning
# step removed the ability". Measured, not chosen: at tol 1e-9 the known invariants represent only to ~1e-8
# (E 9.2e-09, L 4.3e-09, H 1.5e-08); at 1e-13 they reach ~1e-12 and clear the pre-registered 1e-9 bar by three
# orders. THE GATE IS UNCHANGED -- the instrument was fixed so it can meet it, which is the opposite of moving it.
COND_TOL = 1e-13
FAST = "--fast" in sys.argv[1:]
NTRAJ = 150 if FAST else 300
EPS_LIST = (2.0, 5.0, 10.0)


def setup(fast):
    m168.NTRAJ = NTRAJ
    m168.NSTEP = 4000 if fast else 6000
    m168.STRIDE = 27 if fast else 40


def vels(T, eps):
    """Geodesic velocities u^A = g^{AB} p_B for bumped Kerr, coords (t, r, theta, phi)."""
    r, th, pr, pth, E, L = [T[..., i] for i in range(6)]
    itt, itp, ipp, irr, ithth = m168.metric_inv(torch.tensor(r), torch.cos(torch.tensor(th)), eps)
    itt, itp, ipp, irr, ithth = [x.numpy() for x in (itt, itp, ipp, irr, ithth)]
    pt = -E
    ut = itt * pt + itp * L
    uph = itp * pt + ipp * L
    return np.stack([ut, irr * pr, ithth * pth, uph], -1)


def metric_low(r, u, eps):
    """LOWER-index metric components. Needed because p_t and p_phi are g_{A B} u^B: a library carrying only the
    INVERSE components cannot express the Killing momenta, and they are the most basic reducibles. Measured:
    with inverse components alone, L was representable only to 4.6e-04 and the resulting "no survivor" was not
    evidence of absence. Fourth appearance of basis inadequacy in this project, in a new disguise."""
    s2 = 1.0 - u ** 2
    Sig = r ** 2 + m168.SPIN ** 2 * u ** 2
    Del = r ** 2 - 2.0 * r + m168.SPIN ** 2
    bump = 1.0 + eps * (3.0 * u ** 2 - 1.0) / r ** 3
    g_tt = -(1.0 - 2.0 * r / Sig) * bump
    g_tp = -2.0 * m168.SPIN * r * s2 / Sig
    g_pp = (r ** 2 + m168.SPIN ** 2 + 2.0 * m168.SPIN ** 2 * r * s2 / Sig) * s2
    return g_tt, g_tp, g_pp, Sig / Del, Sig


def library(T, eps):
    """Momentum-degree <= 4 monomials in the four velocities x a NAMED coordinate family in (r, cos theta).
    The family must carry what Carter needs (cos^2, cot^2) and what H needs (the inverse-metric components), or
    the reducibles are not representable -- the bug this project has hit three times."""
    r, th = T[..., 0], T[..., 1]
    u = vels(T, eps)
    c2 = np.cos(th) ** 2
    s2 = 1 - c2
    one = np.ones_like(r)
    itt, itp, ipp, irr, ithth = m168.metric_inv(torch.tensor(r), torch.cos(torch.tensor(th)), eps)
    ltt, ltp, lpp, lrr, lthth = metric_low(r, np.cos(th), eps)
    coord = [(one, "1"), (c2, "u2"), (c2 / s2, "cot2"), (1 / s2, "csc2"), (r, "r"), (1 / r, "1/r"),
             (itt.numpy(), "gtt"), (itp.numpy(), "gtp"), (ipp.numpy(), "gpp"),
             (irr.numpy(), "grr"), (ithth.numpy(), "gthth"),
             (ltt, "g_tt"), (ltp, "g_tp"), (lpp, "g_pp"), (lrr, "g_rr"), (lthth, "g_thth")]
    feats = []
    for e in m172._mono(4, 4):
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
    return np.stack(feats, -1)


def H_of(T, eps):
    return m168.energy(T, eps)


def reducibles(T, eps, carter_alive):
    """Monomials in the Killing momenta {E, L}, H, and (at eps=0) Carter, total momentum degree <= 4."""
    E, L = T[..., 4], T[..., 5]
    H = H_of(T, eps)
    gens = [(E, 1, "E"), (L, 1, "L"), (H, 2, "H")]
    if carter_alive:
        gens.append((m168.carter(T, eps), 2, "K"))
    out = []

    def rec(i, acc, d, lab):
        if d > 4:
            return
        if i == len(gens):
            if lab:
                out.append((acc, lab))
            return
        v, dv, nm = gens[i]
        p = np.ones_like(E)
        e = 0
        while d + e * dv <= 4:
            rec(i + 1, acc * p, d + e * dv, lab + (f"{nm}^{e}" if e else ""))
            e += 1
            p = p * v
    rec(0, np.ones_like(E), 0, "")
    return out


def known_fail(T, eps):
    u = vels(T, eps)
    return T[..., 0] * u[..., 0] + 0.3 * u[..., 1] ** 2


def represent_check(Ttr, Tte, eps):
    """R1's missing half: are the invariants KNOWN to be there actually representable? Pre-registered and, in the
    first version of this script, never implemented -- so a "no survivor" could not be told from "the library
    cannot express what is there"."""
    Fa, Fb = library(Ttr, eps), library(Tte, eps)
    V = m172.cond_basis(Fa, tol=COND_TOL)
    Fk = Fa @ V
    Z = ((Fk - Fk.reshape(-1, Fk.shape[-1]).mean(0)) / (Fk.reshape(-1, Fk.shape[-1]).std(0) + 1e-300))
    Z = Z.reshape(-1, Fk.shape[-1])
    Za = np.concatenate([Z, np.ones((len(Z), 1))], 1)
    out = {}
    for nm, yv in [("E", Ttr[..., 4]), ("L", Ttr[..., 5]), ("H", H_of(Ttr, eps))]:
        y = yv.reshape(-1)
        c, *_ = np.linalg.lstsq(Za, y, rcond=None)
        out[nm] = float(np.linalg.norm(Za @ c - y) / (np.linalg.norm(y - y.mean()) + 1e-300))
    return out


def screen(Ttr, Tte, eps, carter_alive):
    red = reducibles(Tte, eps, carter_alive)
    R = np.stack([v.mean(1) for v, _ in red], 1)
    Rz = (R - R.mean(0)) / (R.std(0) + 1e-300)
    sv = np.linalg.svd(Rz, compute_uv=False)
    deficient = bool(sv[-1] / sv[0] < 1e-10)
    Fa, Fb = library(Ttr, eps), library(Tte, eps)
    V = m172.cond_basis(Fa, tol=COND_TOL)
    Fk, Ftek = Fa @ V, Fb @ V
    ev, C, mu, sd = s99.conserved(Fk)
    rat = np.array([s99.heldout(Ftek, C[:, k], mu, sd) for k in range(C.shape[1])])
    o = np.argsort(rat)
    ntake = min(R.shape[1] + 3, C.shape[1])
    cons = np.stack([(((Ftek - mu) / sd) @ C[:, k]).mean(1) for k in o[:ntake]], 1)
    # residual of the conserved values after removing everything the reducibles explain
    Q, _ = np.linalg.qr(Rz)
    Cz = (cons - cons.mean(0)) / (cons.std(0) + 1e-300)
    resid = Cz - Q @ (Q.T @ Cz)
    spec = np.linalg.svd(resid, compute_uv=False)
    spec = spec / (spec[0] + 1e-300)
    sep = float(spec[0] / spec[1]) if len(spec) > 1 else float("inf")
    kf = m172.in_span(cons, known_fail(Tte, eps).mean(1))
    return {"eps": eps, "n_reducible_list": int(R.shape[1]), "reducible_deficient": deficient,
            "p": int(Fk.shape[-1]), "n_conserved_1e9": int((rat <= 1e-9).sum()),
            "separation": sep, "residual_spectrum": [float(v) for v in spec[:5]],
            "known_fail_residual": float(kf), "best_heldout": float(rat.min()),
            "x_spread": float(np.mean(Tte[..., 0].max(1) - Tte[..., 0].min(1)))}


def main():
    setup(FAST)
    out = {"question": "rerun §168's degree-4 rungs on bumped Kerr with the readout §173 validated at 2 KVs",
           "validation": ("BY REGIME MATCH, not on-substrate: bumped Kerr has no known rank-4 KT so no positive "
                          "control is possible here. §173 validated this readout at degree 4 with two Killing "
                          "vectors and a reducible list of 30. This is an argument, not a measurement."),
           "rows": []}
    print("R0/R1 — chain check on UNDEFORMED Kerr (eps=0), Carter alive")
    T0tr, T0te = m168.geodesics(0.0, seed=1), m168.geodesics(0.0, seed=51)
    r0 = screen(T0tr, T0te, 0.0, carter_alive=True)
    print(f"   reducible list {r0['n_reducible_list']} (deficient={r0['reducible_deficient']})  p={r0['p']}  "
          f"conserved<1e-9={r0['n_conserved_1e9']}  x-spread={r0['x_spread']:.3f}")
    print(f"   separation={r0['separation']:.2e}  known-fail residual={r0['known_fail_residual']:.2e}")
    out["rows"].append({"label": "eps=0 (control)", **r0})
    # regime match: comparable to §173's validated case (list 30), not to the failing one (list 70)
    regime_ok = bool(20 <= r0["n_reducible_list"] <= 45 and r0["x_spread"] > 0.3)
    kf_ok = bool(r0["known_fail_residual"] > 1e-2)
    # R1b THE ON-SUBSTRATE POSITIVE CONTROL, which replaces the regime-match ARGUMENT with a MEASUREMENT.
    # At eps=0 Carter is genuinely conserved. Withhold it from the reducible list and it MUST stand out. If it
    # does not, the readout cannot see a standout on THIS substrate and a "no survivor" at eps>0 is not evidence
    # of absence -- it is the instrument finding nothing, which is the failure this project exists to catch.
    r0_withheld = screen(T0tr, T0te, 0.0, carter_alive=False)
    sep_ratio = r0_withheld["separation"] / max(r0["separation"], 1e-30)
    onsub_ok = bool(r0_withheld["separation"] > 1e3)
    out["onsubstrate_control"] = {"separation_carter_in_list": r0["separation"],
                                  "separation_carter_withheld": r0_withheld["separation"],
                                  "ratio": float(sep_ratio), "passes": onsub_ok}
    print(f"R1b on-substrate control: Carter withheld -> separation {r0_withheld['separation']:.3e} "
          f"vs {r0['separation']:.3e} with it in the list (ratio {sep_ratio:.2f}) -> "
          f"{'CAN see a standout' if onsub_ok else 'CANNOT see a standout'}")
    rep = represent_check(T0tr, T0te, 0.0)
    rep_ok = bool(max(rep.values()) < 1e-9)
    out["representability_eps0"] = rep
    print(f"   representability of the KNOWN invariants: " + "  ".join(f"{k}={v:.1e}" for k, v in rep.items())
          + f"   -> {'OK' if rep_ok else 'INADEQUATE (a null here would not be evidence of absence)'}")
    print(f"R0 regime match: {regime_ok} | R1 known-fail excluded: {kf_ok} | R1 reducibles representable: {rep_ok}")

    print("R2/R3 — the question, deformed:")
    for eps in EPS_LIST:
        Ttr, Tte = m168.geodesics(eps, seed=2), m168.geodesics(eps, seed=52)
        r = screen(Ttr, Tte, eps, carter_alive=False)
        surv = bool(r["separation"] > 1e3)
        r["survivor"] = surv
        out["rows"].append({"label": f"eps={eps}", **r})
        print(f"   eps={eps:<5} list={r['n_reducible_list']:3d} p={r['p']:4d} "
              f"cons<1e-9={r['n_conserved_1e9']:3d} sep={r['separation']:.2e} "
              f"knownfail={r['known_fail_residual']:.2e} -> {'ESCALATE' if surv else 'no survivor'}")
    survs = [r for r in out["rows"] if r.get("survivor")]
    stable = bool(len(survs) in (0, len(EPS_LIST)))
    out.update({"R0_regime_match": regime_ok, "R1_known_fail_excluded": kf_ok,
                "R2_survivors": len(survs), "R3_stable_across_eps": stable,
                "R1_reducibles_representable": rep_ok, "R1b_onsubstrate_control": onsub_ok,
                "rerun_valid": bool(regime_ok and kf_ok and rep_ok and onsub_ok)})
    if not (regime_ok and kf_ok and rep_ok and onsub_ok):
        out["verdict"] = (
            "RERUN REFUSED, and the ON-SUBSTRATE CONTROL is why. At eps=0 Carter is genuinely conserved; "
            "withholding it from the reducible list gives separation {:.3f} against {:.3f} with it included -- "
            "ratio {:.2f}. **The readout cannot see a standout on this substrate even when one is certainly "
            "there**, so the eps>0 'no survivor' is the instrument finding nothing, not evidence of absence. "
            "§168's refusal of these rungs STANDS. This also refutes our own regime-match argument: §173 "
            "validated the readout at two Killing vectors ON THE CG SUBSTRATE, and that does NOT transfer to "
            "bumped Kerr despite matching on Killing-vector count and reducible-list size. Regime match on "
            "coarse variables is not sufficient; readout capability is substrate-specific and must be measured "
            "where it is used."
            .format(r0_withheld["separation"], r0["separation"], sep_ratio)
            if not onsub_ok else
            "RERUN REFUSED: the regime does not match, the known-fail control was admitted, or the library "
            "cannot represent the invariants already known to be present. §168's refusal stands.")
    elif not survs:
        out["verdict"] = ("CERTIFY-NO-INVARIANT-IN[velocity-monomial x {1, cos^2, cot^2, csc^2, r, 1/r, inverse-"
                          "metric components}, momentum degree <= 4] on bumped Kerr at eps = 2, 5, 10. Scoped to "
                          "that family AND to a numerical readout validated by REGIME MATCH rather than by a "
                          "positive control on this substrate. Not a theorem; ansatz's exact GF(p) prover is the "
                          "instrument that can settle it.")
    elif not stable:
        out["verdict"] = ("SURVIVORS UNSTABLE across the eps sweep -- a count that moves with the deformation is "
                          "a noise floor, not an invariant (the §168 lesson). Withdrawn, not escalated.")
    else:
        out["verdict"] = ("ESCALATE: a direction survives at every eps after the measured reducibles are removed. "
                          "A LEAD for the exact prover, never a claim.")
    print("\n" + out["verdict"])
    (RESULTS / "174_bumped_kerr_deg4_rerun.json").write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(figsize=(8, 5))
    for r in out["rows"]:
        sp = np.maximum(r["residual_spectrum"], 1e-20)
        ax.semilogy(range(1, len(sp) + 1), sp, "o-", label=r["label"])
    ax.set_xlabel("residual direction")
    ax.set_ylabel("singular value (normalized)")
    ax.legend(fontsize=8)
    ax.set_title("Bumped Kerr, degree 4, reducibles removed\na direction standing out = ESCALATE")
    fig.tight_layout()
    fig.savefig(RESULTS / "174_bumped_kerr_deg4_rerun.png", dpi=140)
    print("saved results/174_bumped_kerr_deg4_rerun.json + .png")


if __name__ == "__main__":
    main()
