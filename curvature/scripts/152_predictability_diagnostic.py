"""Step 152 — EXP-11 of the REPRESENTABILITY FRONTIER (②): the PREDICTABILITY diagnostic (the 2nd axis, instrumented).

notes/representability_frontier.md. EXP-5 found PREDICTABILITY is an axis orthogonal to the 5-cell DISCOVERABILITY table;
EXP-7 showed law-learnability and trajectory-predictability dissociate but lumped every unpredictable system together.
EXP-11 builds the finer taxonomy as a standalone instrument -- given a system, classify its trajectory predictability:
  RANDOM       -- no learnable one-step law (the local rule itself is unpredictable).
  PREDICTABLE  -- a learnable law AND a compressible/regular trajectory (a shortcut exists).
  CHAOTIC      -- a learnable smooth law but sensitive dependence (continuous; 0-1 test K high) -- no long-horizon shortcut.
  IRREDUCIBLE  -- a learnable discrete rule but an incompressible trajectory (Wolfram: no shortcut, must simulate).

Diagnostic (reuses validated measures): law-learnability = one-step forecast R^2 (continuous) / lookup accuracy (CA);
predictability = 0-1 test K (continuous) / zlib compress ratio (CA). Substrate (continuous vs discrete) routes the
chaos-vs-irreducibility distinction -- honest, since chaos is a continuous-dynamics notion (sensitive dependence) and
computational irreducibility is a discrete-computation notion (no algorithmic shortcut).

Pre-reg (2026-07-02):
  P1 CLASSIFIES ALL FIVE: Kepler->PREDICTABLE, Lorenz->CHAOTIC, Rule 250->PREDICTABLE, Rule 30->IRREDUCIBLE,
     iid-noise->RANDOM.
  P2 COMPLETE TAXONOMY: all four predictability classes are populated (PREDICTABLE, CHAOTIC, IRREDUCIBLE, RANDOM).
  P3 ORTHOGONAL TO DISCOVERABILITY: the four structured systems all have a learnable one-step law (law-score ~1) yet
     span three predictability classes -- the axis is genuinely independent of law-discoverability (EXP-7 via this instrument).
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
s146 = import_module("146_sixth_wall_hunt")
s148 = import_module("148_law_vs_predictability")


def predictability(system):
    kind = system["kind"]
    if kind == "continuous":
        T = system["X"]
        law = s148.onestep_R2_continuous(T)
        if law < 0.5:
            return "RANDOM", {"law_score": law, "measure": "one-step R2"}
        K = float(max(np.median([s145.zero_one_K(T[i, ::r, 0], seed=i) for i in range(len(T))]) for r in (3, 5, 10)))
        verdict = "PREDICTABLE" if K < 0.5 else "CHAOTIC"
        return verdict, {"law_score": law, "predictability_metric": K, "measure": "0-1 test K"}
    else:  # discrete CA
        g = system["X"]
        acc, _ = s146.onestep_accuracy(g)
        if acc < 0.5:
            return "RANDOM", {"law_score": acc, "measure": "one-step accuracy"}
        comp = s146.compress_ratio(g)
        verdict = "PREDICTABLE" if comp < 0.5 else "IRREDUCIBLE"
        return verdict, {"law_score": acc, "predictability_metric": comp, "measure": "compress ratio"}


def main():
    rng = np.random.default_rng(0)
    menu = [
        ("PREDICTABLE", "kepler", {"kind": "continuous", "X": s145.gen_kepler(n_traj=16, seed=3)}),
        ("CHAOTIC", "lorenz", {"kind": "continuous", "X": s145.gen_lorenz(n_traj=16, seed=4)}),
        ("PREDICTABLE", "rule250", {"kind": "discrete", "X": s146.elementary_ca(250, seed=0)}),
        ("IRREDUCIBLE", "rule30", {"kind": "discrete", "X": s146.elementary_ca(30, seed=0)}),
        ("RANDOM", "iid_noise", {"kind": "continuous", "X": rng.normal(0, 1, (16, 1000, 3))}),
    ]
    rows = []
    for expected, name, sysd in menu:
        verdict, info = predictability(sysd)
        rows.append({"name": name, "expected": expected, "verdict": verdict, "ok": bool(verdict == expected), **info})
        print(f"{name:10s} expected={expected:12s} -> {verdict:12s} {'OK' if verdict == expected else 'WRONG'}  {info}")

    p1 = bool(all(r["ok"] for r in rows))
    classes_seen = set(r["verdict"] for r in rows)
    p2 = bool({"PREDICTABLE", "CHAOTIC", "IRREDUCIBLE", "RANDOM"} <= classes_seen)
    structured = [r for r in rows if r["name"] != "iid_noise"]
    p3 = bool(all(r["law_score"] > 0.95 for r in structured) and len(set(r["verdict"] for r in structured)) >= 3)

    out = {"rows": [{k: r[k] for k in ("name", "expected", "verdict", "ok", "law_score")} for r in rows],
           "P1_classifies_all_five": p1, "P2_complete_taxonomy": p2, "P3_orthogonal_to_discoverability": p3,
           "predictability_axis_instrumented": bool(p1 and p2 and p3),
           "verdict": ("THE PREDICTABILITY DIAGNOSTIC (② EXP-11): the frontier's SECOND axis is now a first-class "
                       "instrument. Given a system it returns one of four predictability classes -- RANDOM (no learnable "
                       "rule), PREDICTABLE (learnable rule + compressible trajectory), CHAOTIC (learnable smooth rule but "
                       "sensitive dependence), IRREDUCIBLE (learnable discrete rule but incompressible trajectory). On a "
                       "5-system menu it classifies all correctly (Kepler/Rule250 PREDICTABLE, Lorenz CHAOTIC, Rule 30 "
                       "IRREDUCIBLE, iid-noise RANDOM) and populates all four classes. Crucially (P3) the four STRUCTURED "
                       "systems all have a learnable one-step law (law-score ~1) yet span three predictability classes -- "
                       "so predictability is genuinely ORTHOGONAL to law-discoverability, exactly as EXP-5/7 argued, now "
                       "wielded as an instrument. The 3-axis frontier (discoverability x predictability x sampling) has "
                       "its middle axis operationalized."
                       if (p1 and p2 and p3) else "PARTIAL/HONEST -- see per-system rows.")}
    print(f"\nP1 classifies all five: {p1} | P2 complete taxonomy: {p2} | P3 orthogonal: {p3}")
    print(f"PREDICTABILITY AXIS INSTRUMENTED: {out['predictability_axis_instrumented']}")
    (RESULTS / "152_predictability_diagnostic.json").write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(figsize=(8.5, 5))
    cls = {"RANDOM": (0, "gray"), "IRREDUCIBLE": (1, "crimson"), "CHAOTIC": (2, "orange"), "PREDICTABLE": (3, "seagreen")}
    for r in rows:
        yi, col = cls[r["verdict"]]
        ax.scatter(r["law_score"], yi + (rng.random() - 0.5) * 0.2, s=150, color=col, edgecolor="k", zorder=3)
        ax.annotate(r["name"], (r["law_score"], yi), fontsize=9, xytext=(6, 6), textcoords="offset points")
    ax.axvline(0.5, ls="--", c="k", lw=0.7)
    ax.set_yticks([0, 1, 2, 3]); ax.set_yticklabels(["RANDOM", "IRREDUCIBLE", "CHAOTIC", "PREDICTABLE"])
    ax.set_xlabel("one-step LAW learnability (R² / accuracy)"); ax.set_xlim(-0.15, 1.1)
    ax.set_title("② EXP-11 — the predictability diagnostic: 4 classes\nall structured systems have a learnable law (right of dashed line) yet span predictability")
    fig.tight_layout(); fig.savefig(RESULTS / "152_predictability_diagnostic.png", dpi=140)
    print("saved results/152_predictability_diagnostic.json + .png")


if __name__ == "__main__":
    main()
