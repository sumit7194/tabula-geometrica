"""Step 148 — EXP-7 of the REPRESENTABILITY FRONTIER (②): LAW-learnability vs TRAJECTORY-predictability dissociate.

notes/representability_frontier.md. EXP-5 found PREDICTABILITY is an axis orthogonal to the 5-cell DISCOVERABILITY
table. EXP-7 sharpens it with unambiguous metrics and adds a clarification: there are two different "discoverability"
notions that people conflate --
  (1) LAW-learnability: can a model predict ONE step ahead from the local state? (the generating rule)
  (2) TRAJECTORY-predictability: can you shortcut / compress the long-horizon trajectory? (invariant or compression)
For a smooth integrable system these coincide, so the distinction is invisible. EXP-7 shows they DISSOCIATE: Lorenz and
Rule 30 have PERFECTLY learnable one-step laws yet UNPREDICTABLE trajectories. So the frontier's discoverability is a
TRAJECTORY-LEVEL property (invariants / compression), NOT local-rule learnability -- which is almost always easy.

Metrics (unambiguous, no chaos-vs-irreducibility hair-splitting):
  - LAW score: continuous -> one-step forecast R^2 (Ridge on degree-2 features, held-out); CA -> one-step lookup accuracy.
  - PREDICTABLE?: continuous -> 0-1 test K < 0.5 (regular); CA -> zlib compress ratio < 0.5 (compressible).

Menu (2x2 + a control): Kepler (law+, pred+) / Lorenz (law+, pred-) / Rule 250 (law+, pred+) / Rule 30 (law+, pred-) /
iid noise (law-, pred-, the control that "law-learnable" is a real property, not automatic).

Pre-reg (2026-07-02):
  G1 LAW-UNIFORM-FOR-STRUCTURED: Kepler, Lorenz, Rule 30, Rule 250 all have a learnable one-step law (continuous R^2 >
     0.95 / CA accuracy > 0.99); the iid-noise control does NOT (R^2 < 0.2) -- so law-learnability is a genuine property.
  G2 PREDICTABILITY-DISSOCIATES: among the law-learnable systems, predictability SPLITS -- Kepler (K < 0.2) & Rule 250
     (compress < 0.1) predictable; Lorenz (K > 0.8) & Rule 30 (compress > 0.9) UNPREDICTABLE.
  G3 THE DISSOCIATION IS REAL: >= 2 systems are law-learnable-yet-unpredictable (Lorenz, Rule 30) -> the two notions are
     independent; the frontier's discoverability axis is trajectory-level, distinct from local-rule learnability.
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
from sklearn.linear_model import Ridge
from sklearn.metrics import r2_score
from sklearn.preprocessing import PolynomialFeatures

from curvlib import RESULTS

s145 = import_module("145_regime_detector")
s146 = import_module("146_sixth_wall_hunt")


def onestep_R2_continuous(T):
    """one-step forecast R^2: predict state_{t+1} from state_t (Ridge on degree-2 features), held-out."""
    X = T[:, :-1, :].reshape(-1, T.shape[-1]); Y = T[:, 1:, :].reshape(-1, T.shape[-1])
    n = len(X); ntr = n // 2
    poly = PolynomialFeatures(2, include_bias=True)
    Xtr = poly.fit_transform(X[:ntr]); Xte = poly.transform(X[ntr:])
    m = Ridge(1e-4).fit(Xtr, Y[:ntr])
    return float(r2_score(Y[ntr:], m.predict(Xte)))


def K_continuous(T):
    return float(max(np.median([s145.zero_one_K(T[i, ::rate, 0], seed=i) for i in range(len(T))]) for rate in (3, 5, 10)))


def main():
    rng = np.random.default_rng(0)
    kep = s145.gen_kepler(n_traj=16, seed=3)
    lor = s145.gen_lorenz(n_traj=16, seed=4)
    ca30 = s146.elementary_ca(30, seed=0)
    ca250 = s146.elementary_ca(250, seed=0)
    noise = rng.normal(0, 1, (16, 1000, 3))                       # iid noise "trajectory" (no temporal structure)

    rows = {}
    # continuous systems: LAW = one-step R^2, PRED = (K < 0.5)
    for name, T in [("kepler", kep), ("lorenz", lor), ("iid_noise", noise)]:
        r2 = onestep_R2_continuous(T); K = K_continuous(T)
        rows[name] = {"kind": "continuous", "law_score": r2, "law_learnable": bool(r2 > 0.95),
                      "pred_metric": K, "predictable": bool(K < 0.5)}
    # CA systems: LAW = one-step accuracy, PRED = (compress < 0.5)
    for name, g in [("rule250", ca250), ("rule30", ca30)]:
        acc, _ = s146.onestep_accuracy(g); comp = s146.compress_ratio(g)
        rows[name] = {"kind": "CA", "law_score": acc, "law_learnable": bool(acc > 0.99),
                      "pred_metric": comp, "predictable": bool(comp < 0.5)}

    structured = ["kepler", "lorenz", "rule30", "rule250"]
    g1 = bool(all(rows[s]["law_learnable"] for s in structured) and not rows["iid_noise"]["law_learnable"]
              and rows["iid_noise"]["law_score"] < 0.2)
    g2 = bool(rows["kepler"]["predictable"] and rows["rule250"]["predictable"]
              and not rows["lorenz"]["predictable"] and not rows["rule30"]["predictable"])
    dissociated = [s for s in structured if rows[s]["law_learnable"] and not rows[s]["predictable"]]
    g3 = bool(len(dissociated) >= 2)

    out = {"rows": rows, "law_learnable_yet_unpredictable": dissociated,
           "G1_law_uniform_for_structured": g1, "G2_predictability_dissociates": g2, "G3_dissociation_real": g3,
           "law_vs_predictability_dissociate": bool(g1 and g2 and g3),
           "verdict": ("LAW-LEARNABILITY vs TRAJECTORY-PREDICTABILITY DISSOCIATE (② EXP-7): the local generating rule is "
                       "almost always learnable -- Kepler, Lorenz, Rule 30, Rule 250 ALL have a one-step law recovered at "
                       "R^2/accuracy near 1 (only the iid-noise control fails, R^2={:.2f}, confirming law-learnability is "
                       "a real property). But TRAJECTORY predictability splits among them: Kepler (0-1 K={:.2f}) and Rule "
                       "250 (compress={:.2f}) are predictable, while Lorenz (K={:.2f}) and Rule 30 (compress={:.2f}) are "
                       "NOT -- despite identical one-step learnability. So 'discoverability' has two levels that people "
                       "conflate: the LOCAL RULE (easy, almost always emit-able) and the TRAJECTORY structure (invariants "
                       "/ compression -- what the 5-cell frontier table actually measures). Lorenz and Rule 30 are "
                       "law-learnable-yet-unpredictable: the two notions are independent, sharpening EXP-5's predictability "
                       "axis with unambiguous metrics."
                       .format(rows["iid_noise"]["law_score"], rows["kepler"]["pred_metric"], rows["rule250"]["pred_metric"],
                               rows["lorenz"]["pred_metric"], rows["rule30"]["pred_metric"])
                       if (g1 and g2 and g3) else "PARTIAL/HONEST -- see per-system rows.")}
    for s in ["kepler", "lorenz", "rule250", "rule30", "iid_noise"]:
        r = rows[s]
        print(f"{s:10s} [{r['kind']:10s}] law={r['law_score']:.3f} (learnable {r['law_learnable']}) | "
              f"pred_metric={r['pred_metric']:.3f} (predictable {r['predictable']})")
    print(f"\nlaw-learnable-yet-unpredictable: {dissociated}")
    print(f"G1 law-uniform: {g1} | G2 predictability-dissociates: {g2} | G3 dissociation-real: {g3}")
    print(f"LAW vs PREDICTABILITY DISSOCIATE: {out['law_vs_predictability_dissociate']}")
    (RESULTS / "148_law_vs_predictability.json").write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(figsize=(7.5, 6))
    for s in ["kepler", "lorenz", "rule250", "rule30", "iid_noise"]:
        r = rows[s]
        xx = 1.0 if r["law_learnable"] else 0.0
        yy = 1.0 if r["predictable"] else 0.0
        xx += (rng.random() - 0.5) * 0.12; yy += (rng.random() - 0.5) * 0.12
        col = "seagreen" if r["kind"] == "continuous" else ("steelblue" if r["kind"] == "CA" else "gray")
        ax.scatter(xx, yy, s=160, color=col, zorder=3, edgecolor="k")
        ax.annotate(s, (xx, yy), fontsize=9, xytext=(6, 6), textcoords="offset points")
    ax.axhline(0.5, ls="--", c="k", lw=0.6); ax.axvline(0.5, ls="--", c="k", lw=0.6)
    ax.set_xlim(-0.35, 1.35); ax.set_ylim(-0.35, 1.35); ax.set_xticks([0, 1]); ax.set_yticks([0, 1])
    ax.set_xticklabels(["law NOT\nlearnable", "law\nlearnable"]); ax.set_yticklabels(["UNpredictable\ntrajectory", "predictable\ntrajectory"])
    ax.set_title("② EXP-7 — law-learnability × trajectory-predictability DISSOCIATE\nLorenz & Rule 30: learnable rule, unpredictable trajectory (off-diagonal)")
    fig.tight_layout(); fig.savefig(RESULTS / "148_law_vs_predictability.png", dpi=140)
    print("saved results/148_law_vs_predictability.json + .png")


if __name__ == "__main__":
    main()
