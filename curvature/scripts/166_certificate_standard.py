"""Step 166 — THE CERTIFICATE STANDARD: what a certified null must carry before it counts.

notes/certificate_standard.md (pre-registration frozen 2026-08-16 BEFORE this file was written).
User-authorized after the PROGRAM_II round.

WHY. Three repos converged, with no coordination, on the same product: ansatz's P1(a') is a certified
classification to stated order, P3 is certify-non-existence to stated order, and our §160-§165 ladder is
certified basis-relative non-existence. The distinctive output of this program is THE CERTIFIED NULL --
which is exactly why the certification has to be airtight. We have hit FOUR ways it silently isn't:

  1. BASIS-RELATIVITY -- "no invariant" always means "not in my library" (§162, §164).
  2. LIBRARY CONDITIONING -- collinear columns manufacture null directions (§165: deg 8 gave 8 exact zeros
     out of p=147, and the calibrated cutoff duly reported 9 "invariants").
  3. IN-SAMPLE APPROXIMATION -- a polynomial crosses an emit threshold by approximating rather than
     representing (§164 U3 / the bridge's O4: in-sample 9.9e-7 crossed the 1e-6 line, held-out 5.6e-6 did not).
  4. CONFOUNDING -- a per-realization NUISANCE CONSTANT is constant-within and varying-across, so the engine
     finds it AND IT PASSES OUT-OF-SAMPLE VALIDATION PERFECTLY. Held-out validation catches OVERFITTING, not
     CONFOUNDING: a calibration offset or a subject identity is genuinely constant, so it generalizes flawlessly.

1-3 we patched piecemeal and never asserted as required clauses. 4 was identified in the PROGRAM_II P4 read
(2026-08-16) and has never been tested by anyone here. It is the new work.

THE STANDARD (a certificate is admissible only with all four clauses; any one missing => curiosity, not certificate):
  C1 BASIS NAMED           -- verdict states family F and order N; the instrument is structurally incapable of
                              emitting an unqualified "no invariant exists".
  C2 CONDITIONING GATED    -- rank(F) reported; count is null(W) - deficiency(F), never raw null(W) (§165).
  C3 OUT-OF-SAMPLE         -- conservation statistic on HELD-OUT REALIZATIONS, never in-sample (§164/R7).
  C4 STATE-FUNCTIONALITY   -- NEW. A candidate invariant must be A FUNCTION OF THE DYNAMICAL STATE ALONE,
                              verified by predicting it on HELD-OUT REALIZATIONS from their states. A genuine
                              invariant I(z) is determined by the state, so a regressor z -> I generalizes across
                              realizations; a nuisance constant is not a function of the state, so it cannot.

Pre-registered gates (frozen in the notes file before this script existed):
  S1 GENUINE INVARIANT PASSES: Kepler ensemble -> engine emits; all four clauses pass; C4 cross-realization R^2 > 0.9.
     [CORRECTED, see below: the 0.9 was unreachable BY CONSTRUCTION; restated as >= 0.7 x a positive control.]
  S2 THE CONFOUND GAP, DEMONSTRATED AND CLOSED (headline, all three halves required): same ensemble + a planted
     per-realization nuisance channel. (a) the engine FINDS it (at least as conserved as the truth); (b) it PASSES
     C3 -- our existing defence does not catch it; (c) C4 REJECTS it (R^2 < 0.3 vs > 0.9 genuine). If (b) fails,
     failure mode 4 is not real, C4 is ceremony, and that honest null is the result.

PRE-REGISTRATION CORRECTION (recorded openly; the numbers are unchanged and all are reported). S1's C4 gate was frozen
as "absolute R^2 > 0.9". It was UNREACHABLE BY CONSTRUCTION, and the first run measured why: feeding C4 the TRUE ENERGY
-- a quantity that is definitionally a function of the state -- scores only R^2 = 0.658 (depth 8) / 0.750 (unbounded
depth) in this harness. The engine's own candidate scores 0.61-0.70, i.e. THE SAME BAND. Raising the trajectory count
moved it 0.606 -> 0.698 and then plateaued, so this is a held-out-REALIZATION extrapolation ceiling (a forest cannot
extrapolate to state-space regions no training realization visited), not a capacity limit and not a defect of the
candidate. Setting a threshold above a ceiling I had not measured is precisely the bridge's S3 error and my own §164
"gap >= 10x" proxy -- the third instance in this family of testing the convenient quantity instead of the commensurable
one, and this time it was mine again.

THE FIX IS A POSITIVE CONTROL, NOT A LOWERED BAR. C4's statistic is the candidate's state-functionality RELATIVE to a
MANIFEST invariant of the same system measured in the IDENTICAL harness (the Hamiltonian -- known conserved without
solving anything; §165 used the same object as its noise floor). Pass = >= 0.7 x control; reject = near zero or
negative. This is self-calibrating: any implementation of C4 must ship its own control, and the absolute ceiling stops
mattering. Where no manifest invariant exists, C4 can only REJECT and never confirm -- stated as scope, not hidden.
  S3 A TRUE NULL CERTIFIES, SCOPED: Henon-Heiles chaotic (H conserved, no second invariant) -> CERTIFY with F and N
     attached, never an unqualified non-existence claim.
  S4 CONDITIONING CLAUSE FIRES: an over-rich library on the S1 data -- raw null(W) inflates, null(W)-deficiency(F) does not.
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
from sklearn.ensemble import RandomForestRegressor

from curvlib import RESULTS

s99 = import_module("99_deformed_metrics")
s145 = import_module("145_regime_detector")
s149 = import_module("149_mixed_regime")

FAST = "--fast" in sys.argv[1:]
NTRAJ = 40                      # NOT reduced by --fast: trajectory COUNT is exactly the ensemble coverage C4 needs
STRIDE = 16 if FAST else 8      # --fast trims TIME samples instead, which C4's coverage does not depend on


# ------------------------------------------------------------------ ensembles (known answers by construction)

def kepler_ensemble(n=NTRAJ, seed=0, confound=False):
    """Planar Kepler: many bodies, one law, DIFFERENT invariant values (the §156 structure).
    Dynamical state z = (x, y, vx, vy). If confound, append a per-realization NUISANCE channel: a constant with no
    dynamical meaning (a calibration-offset stand-in) -- constant within a realization, varying across."""
    T = s145.gen_kepler(n_traj=n, seed=seed)[:, ::STRIDE, :]     # (G, P, 4)
    rng = np.random.default_rng(seed + 777)
    aux = None
    if confound:
        c = rng.uniform(1.0, 2.0, len(T))                        # per-realization constant, independent of the state
        aux = np.repeat(c[:, None, None], T.shape[1], axis=1)    # (G, P, 1)
    return T, aux


def henon_ensemble(n=NTRAJ, seed=3):
    """Henon-Heiles at E=0.15 (chaotic-dominated): H is conserved, no second invariant -> the true-null case."""
    ic = s149.sample_ic(0.15, n, seed)
    rec = []
    s = ic.copy()
    for k in range(6000):
        s = s149.rk4(s, s149.DT)
        if k % 25 == 0:
            rec.append(s.copy())
    T = np.stack(rec, 1)                                          # (G, P, 4)
    ok = np.isfinite(T).all((1, 2)) & (np.abs(T[:, -1, :]) < 1e3).all(1)
    return T[ok], None


# ------------------------------------------------------------------ library

def library(T, aux, deg=2, rich=False):
    """Polynomial features in the dynamical state, plus the auxiliary channel if present.
    `rich` deliberately over-parameterises (degree 4 + duplicated blocks) to trip the conditioning clause."""
    z = [T[..., i] for i in range(T.shape[-1])]
    feats, names = [], []
    for i in range(len(z)):
        feats.append(z[i]); names.append(f"z{i}")
    for i in range(len(z)):
        for j in range(i, len(z)):
            feats.append(z[i] * z[j]); names.append(f"z{i}z{j}")
    r = np.sqrt(z[0] ** 2 + z[1] ** 2) + 1e-12
    feats.append(1.0 / r); names.append("1/r")
    if deg >= 4 or rich:
        for i in range(len(z)):
            for j in range(i, len(z)):
                for k in range(j, len(z)):
                    for l in range(k, len(z)):
                        feats.append(z[i] * z[j] * z[k] * z[l]); names.append(f"z{i}z{j}z{k}z{l}")
    if rich:                                                      # exact duplicates -> guaranteed collinearity
        for i in range(len(z)):
            feats.append(z[i] * 1.0); names.append(f"dup_z{i}")
        feats.append(1.0 / r); names.append("dup_1/r")
    if aux is not None:
        feats.append(aux[..., 0]); names.append("AUX_nuisance")
    return np.stack(feats, -1), names


# ------------------------------------------------------------------ the four clauses

def c2_conditioning(F):
    """§165: collinearity lives in the FEATURE matrix F, a genuine invariant only in the deviation matrix W."""
    Fm = F.reshape(-1, F.shape[-1])
    sc = Fm.std(0) + 1e-300
    Fm = Fm / sc
    W = (F / sc - (F / sc).mean(axis=1, keepdims=True)).reshape(-1, F.shape[-1])
    svF = np.sqrt(np.clip(np.linalg.eigvalsh(Fm.T @ Fm), 0, None))[::-1]
    svW = np.sqrt(np.clip(np.linalg.eigvalsh(W.T @ W), 0, None))[::-1]
    p = F.shape[-1]
    rankF = int((svF > svF[0] * 1e-12).sum())
    nullW = p - int((svW > svW[0] * 1e-12).sum())
    return {"p": p, "rankF": rankF, "deficiencyF": p - rankF, "nullW_raw": nullW,
            "corrected_count": nullW - (p - rankF)}


def c3_out_of_sample(F, split):
    """Fit the most-conserved direction on train realizations, score it on HELD-OUT realizations."""
    ev, C, mu, sd = s99.conserved(F[:split])
    best, cbest = np.inf, None
    for k in range(min(4, C.shape[1])):
        ho = s99.heldout(F[split:], C[:, k], mu, sd)
        if ho < best:
            best, cbest = ho, C[:, k]
    vals = ((F - mu) / sd) @ cbest                                # (G, P) candidate invariant per realization
    return float(best), vals


def manifest_invariant(T, system):
    """A POSITIVE CONTROL for C4: a quantity known to be conserved WITHOUT solving the problem (the manifest
    Hamiltonian). §165 used the same object as its noise floor. For a real unknown system this is the generally
    available control; where none exists, C4 can only REJECT (near-zero R^2), never confirm -- stated as scope."""
    r = np.sqrt(T[..., 0] ** 2 + T[..., 1] ** 2) + 1e-12
    if system == "kepler":
        return 0.5 * (T[..., 2] ** 2 + T[..., 3] ** 2) - 1.0 / r
    return 0.5 * (T[..., 2] ** 2 + T[..., 3] ** 2) + s149.Vpot(T[..., 0], T[..., 1])   # Henon-Heiles H


def c4_state_functionality(T, vals, split):
    """NEW. Is the candidate a FUNCTION OF THE DYNAMICAL STATE, on HELD-OUT REALIZATIONS?
    A genuine invariant I(z) is determined by the state -> a regressor z -> I generalizes to unseen realizations.
    A per-realization nuisance constant is not a function of the state -> it cannot generalize, however perfectly
    it passed C3. Auxiliary/metadata channels are EXCLUDED from the regressor by construction."""
    per = vals.mean(1)                                            # one value per realization (it is ~constant within)
    G, P, _ = T.shape
    Xtr = T[:split].reshape(-1, T.shape[-1]); ytr = np.repeat(per[:split], P)
    Xte = T[split:].reshape(-1, T.shape[-1]); yte = np.repeat(per[split:], P)
    rf = RandomForestRegressor(n_estimators=60, max_depth=8, random_state=0, n_jobs=1).fit(Xtr, ytr)
    pred = rf.predict(Xte)
    ss_res = ((pred - yte) ** 2).sum(); ss_tot = ((yte - yte.mean()) ** 2).sum() + 1e-300
    return float(1 - ss_res / ss_tot)


def c4_with_control(T, vals, split, system):
    """C4's statistic is the candidate's state-functionality RELATIVE to the positive control, because the absolute
    R^2 has a measured coverage ceiling (see the pre-reg correction in the docstring)."""
    cand = c4_state_functionality(T, vals, split)
    ctrl = c4_state_functionality(T, manifest_invariant(T, system), split)
    return cand, ctrl, float(cand / ctrl) if ctrl > 0.05 else float("nan")


def certify(T, aux, family, order, rich=False, system="kepler"):
    """The full standard. Returns a certificate that is structurally incapable of an unqualified null (C1)."""
    F, names = library(T, aux, deg=order, rich=rich)
    split = len(T) // 2
    cond = c2_conditioning(F)
    ho, vals = c3_out_of_sample(F, split)
    r2, ctrl, rel = c4_with_control(T, vals, split, system)
    EMIT_LINE = 1e-6
    conserved = ho < EMIT_LINE
    if not conserved:
        verdict = f"CERTIFY-NO-INVARIANT-IN[{family},order{order}]"     # C1: always scoped, never unqualified
    elif not (rel >= 0.7):                                              # relative to the positive control
        verdict = "REJECT-CONFOUND (conserved, but not a function of the state)"
    else:
        verdict = "EMIT"
    return {"family": family, "order": order, "verdict": verdict,
            "C1_scoped": True, "C2": cond, "C3_heldout_ratio": ho,
            "C4_state_R2": r2, "C4_control_R2": ctrl, "C4_relative": rel,
            "n_features": len(names), "has_aux": aux is not None}


# ------------------------------------------------------------------ the menu

def main():
    print("=== S1: genuine invariant (Kepler ensemble) ===")
    T1, _ = kepler_ensemble()
    c1 = certify(T1, None, "poly(state)", 2)
    print(f"  verdict={c1['verdict']}  C3 held-out={c1['C3_heldout_ratio']:.2e}  "
          f"C4 state-R2={c1['C4_state_R2']:.3f} (control {c1['C4_control_R2']:.3f}, relative {c1['C4_relative']:.2f})")
    S1 = bool(c1["verdict"] == "EMIT" and c1["C4_relative"] >= 0.7)

    print("=== S2: THE CONFOUND (same ensemble + planted per-realization nuisance channel) ===")
    T2, aux2 = kepler_ensemble(confound=True)
    c2 = certify(T2, aux2, "poly(state)+aux", 2)
    found = c2["C3_heldout_ratio"] <= max(c1["C3_heldout_ratio"], 1e-30) * 10      # (a) engine finds it
    passes_c3 = c2["C3_heldout_ratio"] < 1e-6                                       # (b) our old defence lets it through
    rejected_by_c4 = bool(not (c2["C4_relative"] >= 0.7) and c2["C4_state_R2"] < 0.3)   # (c) only C4 catches it
    print(f"  verdict={c2['verdict']}")
    print(f"  (a) engine finds it: held-out {c2['C3_heldout_ratio']:.2e} vs genuine {c1['C3_heldout_ratio']:.2e} -> {found}")
    print(f"  (b) PASSES C3 (old defence blind): {passes_c3}")
    print(f"  (c) rejected by C4: state-R2 {c2['C4_state_R2']:.3f} (control {c2['C4_control_R2']:.3f}, "
          f"relative {c2['C4_relative']:.2f}) -> {rejected_by_c4}")
    S2 = bool(found and passes_c3 and rejected_by_c4)

    print("=== S3: a true null certifies, SCOPED (Henon-Heiles chaotic) ===")
    T3, _ = henon_ensemble()
    c3 = certify(T3, None, "poly(state)", 2, system="henon")
    print(f"  verdict={c3['verdict']}  C3 held-out={c3['C3_heldout_ratio']:.2e}")
    S3 = bool(c3["verdict"].startswith("CERTIFY-NO-INVARIANT-IN[") and "order" in c3["verdict"])

    print("=== S4: conditioning clause fires (over-rich library on S1 data) ===")
    c4r = certify(T1, None, "poly(state)-RICH", 4, rich=True)
    cond = c4r["C2"]
    print(f"  p={cond['p']} rank(F)={cond['rankF']} deficiency={cond['deficiencyF']} "
          f"raw null(W)={cond['nullW_raw']} -> corrected={cond['corrected_count']}")
    S4 = bool(cond["deficiencyF"] > 0 and cond["corrected_count"] < cond["nullW_raw"])

    print(f"\nS1 genuine passes: {S1}")
    print(f"S2 CONFOUND GAP demonstrated + closed: {S2}")
    print(f"S3 true null certifies scoped: {S3}")
    print(f"S4 conditioning clause fires: {S4}")

    out = {"standard": {"C1": "basis named -- every null scoped to (family, order)",
                        "C2": "conditioning gated -- null(W) - deficiency(F), never raw null(W) [165]",
                        "C3": "out-of-sample -- held-out REALIZATIONS, never in-sample [164/R7]",
                        "C4": "state-functionality (NEW) -- candidate must be a function of the DYNAMICAL STATE, "
                              "verified on held-out realizations; rejects per-realization nuisance constants"},
           "S1_genuine": c1, "S2_confound": c2, "S3_true_null": c3, "S4_rich": c4r,
           "S2_engine_finds_confound": bool(found), "S2_confound_passes_C3": bool(passes_c3),
           "S2_confound_rejected_by_C4": bool(rejected_by_c4),
           "S1_genuine_passes": S1, "S2_confound_gap_closed": S2, "S3_true_null_scoped": S3,
           "S4_conditioning_fires": S4,
           "certificate_standard_validated": bool(S1 and S2 and S3 and S4),
           "honest_limitations": [
               "C4 requires the auxiliary/state split to be DECLARED. A confound that contaminates a STATE channel "
               "(e.g. a multiplicative per-run gain on an observable) is not caught by C4 as specified.",
               "C4's power depends on the ensemble spanning enough state space for z -> I to be learnable; a "
               "degenerate ensemble makes C4 uninformative rather than negative.",
               "C2 inherits §165's measured rank-estimate sensitivity (exact at full sampling, +-1 at coarse)."],
           "verdict": ("THE CERTIFICATE STANDARD, VALIDATED. Four clauses, each earned from a way our own "
                       "certification silently failed. The headline is C4 and the gap it closes: a planted "
                       "per-realization nuisance constant (a calibration-offset stand-in, no dynamical meaning) is "
                       "found by the engine at held-out ratio {:.0e} -- as conserved as the genuine invariant's "
                       "{:.0e} -- and it PASSES our existing out-of-sample defence completely. Held-out validation "
                       "catches overfitting, not confounding: a nuisance constant generalizes flawlessly because it "
                       "is genuinely constant. Only C4 rejects it, by asking whether the candidate is A FUNCTION OF "
                       "THE DYNAMICAL STATE: the genuine invariant predicts on held-out realizations at R^2={:.2f}, "
                       "the confound at R^2={:.2f}. The other three clauses hold their own traps: a true null "
                       "certifies SCOPED to (family, order) rather than as non-existence, and an over-rich library's "
                       "raw null count of {} is corrected to {} by the conditioning clause. This is the form a "
                       "certified null has to take here before it counts as one."
                       .format(c2["C3_heldout_ratio"], c1["C3_heldout_ratio"], c1["C4_state_R2"], c2["C4_state_R2"],
                               cond["nullW_raw"], cond["corrected_count"])
                       if (S1 and S2 and S3 and S4) else "PARTIAL/HONEST -- see per-gate numbers.")}
    print(f"CERTIFICATE STANDARD VALIDATED: {out['certificate_standard_validated']}")
    (RESULTS / "166_certificate_standard.json").write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(1, 2, figsize=(13, 5))
    labels = ["genuine\ninvariant", "planted\nconfound"]
    ax[0].bar(labels, [max(c1["C3_heldout_ratio"], 1e-32), max(c2["C3_heldout_ratio"], 1e-32)],
              color=["seagreen", "crimson"])
    ax[0].set_yscale("log"); ax[0].axhline(1e-6, ls="--", c="k", lw=0.8, label="emit line")
    ax[0].set_ylabel("C3 held-out variance ratio"); ax[0].legend(fontsize=8)
    ax[0].set_title("C3 (out-of-sample) is BLIND to the confound\nboth look perfectly conserved")
    ax[1].bar(labels, [c1["C4_state_R2"], c2["C4_state_R2"]], color=["seagreen", "crimson"])
    ax[1].axhline(0.3, ls="--", c="k", lw=0.8, label="C4 reject line")
    ax[1].set_ylabel("C4 state-functionality R² (held-out realizations)"); ax[1].legend(fontsize=8)
    ax[1].set_title("C4 separates them: is it a function of the STATE?\n(the clause held-out validation cannot supply)")
    fig.suptitle("166 — the certificate standard: what a certified null must carry before it counts")
    fig.tight_layout(); fig.savefig(RESULTS / "166_certificate_standard.png", dpi=140)
    print("saved results/166_certificate_standard.json + .png")


if __name__ == "__main__":
    main()
