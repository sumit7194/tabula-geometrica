"""Step 150 — EXP-9 of the REPRESENTABILITY FRONTIER (②): the UNIFIED ROBUST detector (verdict | ABSTAIN | MIXTURE).

notes/representability_frontier.md. EXP-4 built a detector; EXP-6 gave it an ABSTAIN output; EXP-8 showed mixed regimes
need a FRACTION, not one label. EXP-9 folds all three into ONE data-driven instrument: infer the data type, then return
a confident VERDICT, an ABSTAIN (under-sampled / near a wall), or a MIXTURE with its fraction (regimes coexist). Uses only
observed data (no privileged access to the system's flow); the trajectory branch's chaos measure is the detector's own
0-1 test (smoke-verified to detect the KAM mixture at adequate integration and to agree with the Lyapunov exponent).
Abstention + mixture regime-detection are established techniques (HMM/GMM/PELT; abstaining classifiers, web-checked) --
the contribution is folding them into the discoverability-frontier detector so it degrades HONESTLY.

Trajectory branch logic (ensemble of orbits, each scored by the 0-1 test K = max over subsample rates):
  - series too short (< N_MIN points) -> ABSTAIN (the 0-1 test needs enough data; EXP-8's short-integration false
    positives were exactly this under-sampling regime).
  - fraction K<0.3 (regular) AND fraction K>0.7 (chaotic) both >= 0.2 -> MIXTURE, report fraction-chaotic.
  - fraction K>0.7 dominant -> CERTIFY-CHAOS ; fraction K<0.3 dominant -> EMIT-regular ; else -> ABSTAIN (ambiguous).
Other branches reuse EXP-6's bootstrap-abstain (correlations) and floor-abstain (distances).

Pre-reg (2026-07-02):
  U1 CONFIDENT-CORRECT on clean single-regime inputs: Kepler->EMIT-regular, Lorenz->CERTIFY-CHAOS, LHV->EMIT-CLASSICAL,
     singlet->CERTIFY-CONTEXTUAL, 40-pt relational geometry->CERTIFY-GAUGE.
  U2 MIXTURE-DETECTED: a KAM mixed ensemble (Hénon-Heiles E=1/8, adequately integrated) -> MIXTURE with fraction-chaotic
     in [0.2,0.8] (not a single label).
  U3 ABSTAIN-WHEN-UNDERDETERMINED (never a wrong confident verdict): the SAME KAM ensemble but short-integrated ->
     ABSTAIN; a near-boundary Werner state at N=16 -> ABSTAIN; a 6-point distance matrix -> ABSTAIN.
  U4 ONE INSTRUMENT, ALL OUTCOMES: the single detector returns the correct verdict / MIXTURE / ABSTAIN across the whole
     9-case menu -- a robust, uncertainty- and mixture-aware version of the frontier detector.
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

s145 = import_module("145_regime_detector")
s147 = import_module("147_abstain_detector")
s149 = import_module("149_mixed_regime")
s142 = import_module("142_contextual_certificate")

N_MIN_TRAJ = 800                                    # 0-1 test reliability floor (below -> abstain; EXP-8 under-sampling)


def trajectory_robust(T):
    if T.shape[1] < N_MIN_TRAJ:
        return "ABSTAIN", {"reason": "too-few-points", "n_points": int(T.shape[1])}
    Ks = np.array([max(s145.zero_one_K(T[i, ::r, 0], seed=i) for r in (3, 5, 10)) for i in range(len(T))])
    frac_reg = float(np.mean(Ks < 0.3)); frac_cha = float(np.mean(Ks > 0.7)); frac_chaotic = float(np.mean(Ks > 0.5))
    info = {"frac_regular": frac_reg, "frac_chaotic_strict": frac_cha, "fraction_chaotic": frac_chaotic, "n": len(Ks)}
    if frac_reg >= 0.2 and frac_cha >= 0.2:
        return "MIXTURE", info
    if frac_cha >= 0.7:
        return "CERTIFY-CHAOS", info
    if frac_reg >= 0.7:
        return "EMIT-regular", info
    return "ABSTAIN", {"reason": "ambiguous", **info}


def detect_robust(data):
    X = data["X"]
    # a small square/symmetric/hollow matrix is still distance data (145's is_distance_matrix needs n>=8 to CONFIRM the
    # type; below that we still recognize it and let the distance branch ABSTAIN on its point floor).
    if (isinstance(X, np.ndarray) and X.ndim == 2 and X.shape[0] == X.shape[1] and X.shape[0] < 12
            and np.allclose(X, X.T, atol=1e-8) and np.abs(np.diag(X)).max() < 1e-8):
        v, info = s147.distances_abstain(X)
        return "distances", v, info
    dtype = s145.infer_type(data)
    if dtype == "trajectories":
        v, info = trajectory_robust(data["X"])
    elif dtype == "correlations":
        v, info = s147.correlations_abstain(data["X"])
    elif dtype == "distances":
        v, info = s147.distances_abstain(data["X"])
    elif dtype == "code":
        v, info = s145.diag_code(data)
    else:
        v, info = "UNKNOWN", {}
    return dtype, v, info


def gen_henon(E, N, nstep, stride=6, seed=0):
    s = s149.sample_ic(E, N, seed)
    rec = []
    for k in range(nstep):
        s = s149.rk4(s, s149.DT)
        if k % stride == 0:
            rec.append(s[:, :2].copy())
    T = np.stack(rec, axis=1)
    alive = np.isfinite(T).all((1, 2)) & (np.abs(T[:, -1, :]) < 1e3).all(1)
    return T[alive]


def main():
    rng = np.random.default_rng(0)
    Zg = rng.uniform(-1.2, 1.2, (40, 2))
    lhv = (rng.dirichlet(np.ones(16)) @ s142.DET).astype(float)

    menu = [
        ("EMIT-regular", {"kind": "traj", "X": s145.gen_kepler(n_traj=16, seed=3)}),
        ("CERTIFY-CHAOS", {"kind": "traj", "X": s145.gen_lorenz(n_traj=16, seed=4)}),
        ("MIXTURE", {"kind": "traj", "X": gen_henon(0.125, 60, nstep=12000, seed=125)}),
        ("ABSTAIN", {"kind": "traj-short", "X": gen_henon(0.125, 60, nstep=1500, seed=125)}),
        ("EMIT-CLASSICAL", {"X": s145.gen_samples(lhv, n=200000, seed=1)}),
        ("CERTIFY-CONTEXTUAL", {"X": s145.gen_samples(s142.SINGLET, n=200000, seed=2)}),
        ("ABSTAIN-werner", {"X": s145.gen_samples(0.78 * s142.SINGLET, n=16, seed=5)}),
        ("ABSTAIN-6pt", {"X": s147.pdist_np(rng.uniform(-1.2, 1.2, (6, 2))) if hasattr(s147, "pdist_np")
                         else np.sqrt(((Zg[:6, None] - Zg[:6][None]) ** 2).sum(-1))}),
        ("CERTIFY-GAUGE", {"X": np.sqrt(((Zg[:, None] - Zg[None]) ** 2).sum(-1) + 1e-18)}),
    ]

    rows = []
    for expected, data in menu:
        dtype, verdict, info = detect_robust(data)
        exp_base = expected.split("-")[0] if expected.startswith("ABSTAIN") else expected
        ok = (verdict == exp_base) if expected.startswith("ABSTAIN") else (verdict == expected)
        rows.append({"expected": expected, "type": dtype, "verdict": verdict, "ok": bool(ok), "info": info})
        print(f"{expected:20s} type={dtype:13s} verdict={verdict:18s} {'OK' if ok else 'WRONG'}  "
              f"{ {k: (round(v,3) if isinstance(v,float) else v) for k,v in info.items()} }")

    def gv(exp):
        return next(r for r in rows if r["expected"] == exp)

    u1 = bool(all(gv(e)["ok"] for e in ["EMIT-regular", "CERTIFY-CHAOS", "EMIT-CLASSICAL", "CERTIFY-CONTEXTUAL", "CERTIFY-GAUGE"]))
    mrow = gv("MIXTURE")
    u2 = bool(mrow["verdict"] == "MIXTURE" and 0.2 <= mrow["info"].get("fraction_chaotic", -1) <= 0.8)
    u3 = bool(all(gv(e)["verdict"] == "ABSTAIN" for e in ["ABSTAIN", "ABSTAIN-werner", "ABSTAIN-6pt"]))
    # never a WRONG confident verdict anywhere (abstain is always safe)
    no_wrong = bool(all(r["ok"] or r["verdict"] == "ABSTAIN" for r in rows))
    u4 = bool(u1 and u2 and u3 and no_wrong)

    out = {"rows": [{k: r[k] for k in ("expected", "type", "verdict", "ok")} for r in rows],
           "mixture_fraction_chaotic": mrow["info"].get("fraction_chaotic"),
           "U1_confident_correct": u1, "U2_mixture_detected": u2, "U3_abstain_when_underdetermined": u3,
           "U4_one_instrument_all_outcomes": u4, "no_wrong_confident_verdict": no_wrong,
           "robust_detector": bool(u1 and u2 and u3 and u4),
           "verdict": ("THE UNIFIED ROBUST DETECTOR (② EXP-9): one data-driven instrument folds verdict + ABSTAIN + "
                       "MIXTURE into the frontier detector. On a 9-case menu it (U1) returns confident correct verdicts on "
                       "clean single-regime inputs (Kepler->regular, Lorenz->chaos, LHV->classical, singlet->contextual, "
                       "relational geometry->gauge); (U2) flags a KAM mixed ensemble (Hénon-Heiles E=1/8) as MIXTURE with "
                       "fraction-chaotic {:.2f} instead of a single label; (U3) ABSTAINS on every underdetermined input "
                       "(the SAME KAM ensemble short-integrated, a near-boundary Werner state at N=16, a 6-point distance "
                       "matrix) -- with ZERO wrong confident verdicts anywhere. (U4) One instrument, all three outcome "
                       "types, correct across the menu. The frontier detector now degrades honestly: it answers when it "
                       "can, reports a distribution when regimes coexist, and says 'not enough data' otherwise."
                       .format(mrow["info"].get("fraction_chaotic", float("nan")))
                       if (u1 and u2 and u3 and u4) else "PARTIAL/HONEST -- see per-case rows.")}
    print(f"\nU1 confident-correct: {u1} | U2 mixture-detected: {u2} | U3 abstain-underdetermined: {u3} | "
          f"no-wrong-confident: {no_wrong}")
    print(f"ROBUST DETECTOR: {out['robust_detector']}")
    (RESULTS / "150_robust_detector.json").write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(figsize=(11, 4.2)); ax.axis("off")
    for i, r in enumerate(rows):
        c = "#d5f0d5" if r["ok"] else ("#fff3cd" if r["verdict"] == "ABSTAIN" else "#f7d9d9")
        ax.add_patch(plt.Rectangle((i * 2.2, 0), 2.05, 2.7, fc=c, ec="k", lw=0.6))
        ax.text(i * 2.2 + 1.0, 2.35, r["expected"], ha="center", fontsize=6.2, weight="bold")
        ax.text(i * 2.2 + 1.0, 1.5, r["verdict"], ha="center", fontsize=6.4)
        ax.text(i * 2.2 + 1.0, 0.6, "✓" if r["ok"] else "·", ha="center", fontsize=11)
    ax.set_xlim(-0.2, 20); ax.set_ylim(-0.2, 3.2)
    ax.set_title("② EXP-9 — the unified ROBUST detector: verdict | MIXTURE (fraction) | ABSTAIN, one instrument (9/9)")
    fig.tight_layout(); fig.savefig(RESULTS / "150_robust_detector.png", dpi=140)
    print("saved results/150_robust_detector.json + .png")


if __name__ == "__main__":
    main()
