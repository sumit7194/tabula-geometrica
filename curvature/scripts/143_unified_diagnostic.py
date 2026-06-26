"""Step 143 — EXP-3 of the REPRESENTABILITY FRONTIER (②): the 5th verdict + the UNIFIED diagnostic (one instrument, 5 cells).

notes/representability_frontier.md. EXP-1 (141) gave EMIT / CERTIFY-GAUGE / CERTIFY-NO-CODE on distance data; EXP-2 (142)
added CERTIFY-CONTEXTUAL on correlation data. EXP-3 adds the 5th and last verdict -- PARTIAL-LEGIBLE (the code EXISTS and
is used, but is not LINEARLY legible -- the legibility law's free-code case) -- and assembles ONE diagnostic that ROUTES
BY DATA TYPE and emits all five verdicts on a full menu. This closes the frontier table: every discovery wall the project
hit is one of five ways "the cheapest legible code" fails (doesn't exist / isn't unique / isn't globally consistent /
isn't linear), with EMIT when it is all four.

The unified diagnostic routes:
  DISTANCES (NxN)      -> classical MDS: residual STRESS (cheap low-D code?) + anchored frame error (unique or gauge?)
                         -> EMIT / CERTIFY-GAUGE / CERTIFY-NO-CODE   [141, here via fast classical MDS]
  CORRELATIONS (4-vec) -> cheapest local-hidden-variable fit + CHSH  -> EMIT-CLASSICAL / CERTIFY-CONTEXTUAL   [142]
  CODE (codes + prop)  -> linear vs nonlinear decode gap             -> EMIT-LEGIBLE / PARTIAL-LEGIBLE   [139, the 5th]

Pre-reg (2026-06-27):
  U1 PARTIAL-LEGIBLE (the new verdict): a FREE code (property stored non-linearly) -> linear decode LOW (< 0.6) but
     nonlinear decode HIGH (> 0.7) -> verdict PARTIAL-LEGIBLE; an AMORTIZED code -> linear HIGH (> 0.85) -> EMIT-LEGIBLE.
  U2 ONE INSTRUMENT, FIVE VERDICTS: the single routing diagnostic returns the correct verdict on all 7 menu cases
     (EMIT / CERTIFY-GAUGE / CERTIFY-NO-CODE / EMIT-CLASSICAL / CERTIFY-CONTEXTUAL / EMIT-LEGIBLE / PARTIAL-LEGIBLE) --
     the full frontier table, one diagnostic. The five distinct failure/success classes are all instrumented.
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
from scipy.linalg import eigh, orthogonal_procrustes
from sklearn.linear_model import Ridge
from sklearn.neighbors import KNeighborsRegressor

s142 = import_module("142_contextual_certificate")               # contextual branch (fast, self-contained)
s139 = import_module("139_sae_legibility")                       # code-legibility harness

STRESS_T, RAW_T = 0.2, 0.2


# ---------- distance branch (fast classical MDS) ----------
def pdist(X):
    d = X[:, None, :] - X[None, :, :]; return np.sqrt((d ** 2).sum(-1) + 1e-12)


def distance_verdict(Z, anchor):
    N = len(Z); D = pdist(Z); J = np.eye(N) - np.ones((N, N)) / N
    B = -0.5 * J @ (D ** 2) @ J
    w, V = eigh(B); w = w[::-1]; V = V[:, ::-1]
    pos = np.clip(w, 0, None)
    stress = 1.0 - pos[:2].sum() / (pos.sum() + 1e-12)            # fraction of distance-variance NOT in 2D
    if stress > STRESS_T:
        return "CERTIFY-NO-CODE", {"stress": float(stress), "raw": None}
    E = V[:, :2] * np.sqrt(pos[:2])                               # 2D embedding (arbitrary frame)
    Zt = Z[:, :2]; scale = np.sqrt((Zt ** 2).sum(1).mean())
    if anchor:                                                   # align via 4 anchor points -> frame fixed
        k = 4; R, _ = orthogonal_procrustes(E[:k] - E[:k].mean(0), Zt[:k] - Zt[:k].mean(0))
        Ealign = (E - E[:k].mean(0)) @ R + Zt[:k].mean(0)
        raw = float(np.sqrt(((Ealign - Zt) ** 2).sum(1).mean()) / scale)
    else:
        raw = float(np.sqrt(((E - E.mean(0) - (Zt - Zt.mean(0))) ** 2).sum(1).mean()) / scale)  # arbitrary frame
    return ("EMIT" if raw < RAW_T else "CERTIFY-GAUGE"), {"stress": float(stress), "raw": raw}


# ---------- code branch (legibility law, compact) ----------
def code_verdict(kind, base, coup):
    p, Z = s139.train(kind, base, coup, steps=10000)             # the free code needs ~139's regime to encode p nonlinearly
    lin = abs(s139.decode_r(Z, p, Ridge(1.0)))
    nl = abs(s139.decode_r(Z, p, KNeighborsRegressor(10)))
    if lin > 0.85:
        return "EMIT-LEGIBLE", {"linear": lin, "nonlinear": nl}
    if lin < 0.6 and nl > 0.7:
        return "PARTIAL-LEGIBLE", {"linear": lin, "nonlinear": nl}
    return "AMBIGUOUS", {"linear": lin, "nonlinear": nl}


def unified(case):
    k = case["kind"]
    if k == "distances":
        return distance_verdict(case["Z"], case["anchor"])
    if k == "correlations":
        return s142.diagnose(case["E"])
    if k == "code":
        return code_verdict(case["code_kind"], case["base"], case["coup"])


def main():
    rng = np.random.default_rng(0)
    base, coup = s139.make_world()
    Zg = rng.uniform(-1.2, 1.2, (40, 2)).astype(np.float32)
    Zh = rng.uniform(-1.2, 1.2, (40, 6)).astype(np.float32)
    w = rng.dirichlet(np.ones(16))
    menu = [
        ("EMIT", {"kind": "distances", "Z": Zg, "anchor": True}),
        ("CERTIFY-GAUGE", {"kind": "distances", "Z": Zg, "anchor": False}),
        ("CERTIFY-NO-CODE", {"kind": "distances", "Z": Zh, "anchor": False}),
        ("EMIT-CLASSICAL", {"kind": "correlations", "E": (w @ s142.DET).astype(float)}),
        ("CERTIFY-CONTEXTUAL", {"kind": "correlations", "E": s142.SINGLET}),
        ("EMIT-LEGIBLE", {"kind": "code", "code_kind": "amortized", "base": base, "coup": coup}),
        ("PARTIAL-LEGIBLE", {"kind": "code", "code_kind": "free", "base": base, "coup": coup}),
    ]
    rows = {}
    for expected, case in menu:
        verdict, info = unified(case)
        rows[expected] = {"verdict": verdict, "correct": bool(verdict == expected), **info}
        print(f"{expected:20s} -> {verdict:20s} {'OK' if verdict == expected else 'WRONG'}   {info}")

    u1 = bool(rows["EMIT-LEGIBLE"]["verdict"] == "EMIT-LEGIBLE" and rows["PARTIAL-LEGIBLE"]["verdict"] == "PARTIAL-LEGIBLE")
    u2 = bool(all(r["correct"] for r in rows.values()))

    out = {"menu": rows, "U1_partial_legible_verdict": u1, "U2_one_instrument_five_verdicts": u2,
           "frontier_table_complete": bool(u1 and u2),
           "verdict": ("THE FRONTIER TABLE IS COMPLETE (② EXP-3): ONE diagnostic, routing by data type, emits all FIVE "
                       "discoverability verdicts correctly on a full menu. PARTIAL-LEGIBLE (the new 5th) -- a FREE code "
                       "stores the property non-linearly (linear {:.2f} low, nonlinear {:.2f} high) = the code exists+used "
                       "but isn't legible; an AMORTIZED code is EMIT-LEGIBLE (linear {:.2f}). Together with EMIT / "
                       "CERTIFY-GAUGE / CERTIFY-NO-CODE (distances) and EMIT-CLASSICAL / CERTIFY-CONTEXTUAL (correlations), "
                       "every discovery wall the project hit is now one of five ways the cheapest legible code fails -- "
                       "doesn't exist (chaos/no-code), isn't unique (gauge), isn't globally consistent (contextual), isn't "
                       "linear (partial-legible) -- with EMIT when it is all four. A theory of the discoverable, executable."
                       .format(rows["PARTIAL-LEGIBLE"]["linear"], rows["PARTIAL-LEGIBLE"]["nonlinear"],
                               rows["EMIT-LEGIBLE"]["linear"])
                       if (u1 and u2) else "PARTIAL/HONEST -- a verdict was misclassified; see the menu.")}
    print(f"\nU1 PARTIAL-LEGIBLE verdict added: {u1}")
    print(f"U2 ONE INSTRUMENT, FIVE VERDICTS (all 7 menu cases correct): {u2}")
    print(f"FRONTIER TABLE COMPLETE: {out['frontier_table_complete']}")
    (RESULTS := Path(__file__).resolve().parent.parent / "results")
    (RESULTS / "143_unified_diagnostic.json").write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(figsize=(10, 3.4)); ax.axis("off")
    cells = [("EMIT", "unique cheap code", "distances+anchor / LHV / amortized"),
             ("CERTIFY-NO-CODE\n(chaos)", "no cheap code", "6D config / Lorenz"),
             ("CERTIFY-GAUGE", "code not unique", "relational distances"),
             ("CERTIFY-CONTEXTUAL", "no global code", "Bell singlet, CHSH>2"),
             ("PARTIAL-LEGIBLE", "code not linear", "free code")]
    for i, (v, what, ex) in enumerate(cells):
        ax.add_patch(plt.Rectangle((i * 2, 0), 1.9, 2.6, fc=("#d5f0d5" if v.startswith("EMIT") else "#f7d9d9"), ec="k"))
        ax.text(i * 2 + 0.95, 2.2, v, ha="center", va="top", fontsize=8, weight="bold")
        ax.text(i * 2 + 0.95, 1.3, what, ha="center", va="center", fontsize=7.5, style="italic")
        ax.text(i * 2 + 0.95, 0.5, ex, ha="center", va="center", fontsize=6.5)
    ax.set_xlim(-0.2, 10); ax.set_ylim(-0.2, 3.2)
    ax.set_title("② The representability frontier — one diagnostic, five verdicts (the table, all instrumented)")
    fig.tight_layout(); fig.savefig(RESULTS / "143_unified_diagnostic.png", dpi=140)
    print("saved results/143_unified_diagnostic.json + .png")


if __name__ == "__main__":
    main()
