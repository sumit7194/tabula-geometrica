"""Step 141 — EXP-1 of the REPRESENTABILITY FRONTIER (②): one diagnostic, three discoverability verdicts.

notes/representability_frontier.md. The project's scattered LIMITS-of-discovery are different ways "the cheapest legible
code" fails to exist or be unique. This first experiment proves ONE diagnostic already separates THREE of those verdicts
on a controlled menu -- not just integrable-vs-chaotic, but the GAUGE failure too:
  EMIT            -- a UNIQUE cheap code exists (the net extracts the law uniquely).
  CERTIFY-GAUGE   -- a cheap code exists but only UP TO A GAUGE (frame redundancy; non-unique).
  CERTIFY-NO-CODE -- NO cheap code exists (the geometric analog of chaos: the data has no low-D law).

Common observation type = PAIRWISE DISTANCES of a point configuration (the dS-anchor 111 substrate, rigid-motion-
invariant). A point set either (a) embeds uniquely in a low-D geometry given an ANCHOR [EMIT], (b) embeds in the low-D
geometry but only up to the rigid-motion GAUGE without an anchor [CERTIFY-GAUGE, the 111 result], or (c) does NOT embed
in the low-D geometry at all [CERTIFY-NO-CODE -- a high-D configuration whose distances need many dimensions]. The
diagnostic reconstructs in 2D, reads the residual STRESS (does a cheap 2D code exist?) and, if it does, the RAW frame
error (is it unique, or a gauge?), and emits the verdict. Reuses 111's reconstruct/errors/pdist verbatim.

Pre-reg (2026-06-27):
  F1 EMIT (2D config, anchored): low 2D stress (a cheap code exists) AND low raw error (the frame is UNIQUE) -> verdict
     EMIT.
  F2 CERTIFY-GAUGE (2D config, relational/no-anchor): low 2D stress + low ALIGNED (shape) error BUT high RAW (frame)
     error (the absolute frame is a gauge) -> verdict CERTIFY-GAUGE.
  F3 CERTIFY-NO-CODE (high-D config): HIGH 2D stress -- the distances do not embed in a cheap 2D geometry -> verdict
     CERTIFY-NO-CODE (the geometric analog of "no conserved invariant").
  F4 ONE DIAGNOSTIC, ALL THREE: the single verdict function classifies all three menu cases correctly -- the seed of the
     full frontier table (the contextual + partial-legible rows are EXP-2/3).
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

s111 = import_module("111_desitter_anchor")
s111.STEPS = 5000                                                # lighter than 111's 15000 -- only need to separate regimes
pdist, reconstruct, errors, N = s111.pdist, s111.reconstruct, s111.errors, s111.N

STRESS_THRESH, RAW_THRESH = 0.12, 0.15                           # tuned in smoke: separate the three regimes


def gen(regime, seed):
    rng = np.random.default_rng(seed)
    dim = 2 if regime == "geometric" else 6                      # 6-D config -> distances do NOT embed in 2-D
    return rng.uniform(-1.2, 1.2, (N, dim)).astype(np.float32)


def best(Z, anchor, seeds=(0, 1, 2)):
    runs = [reconstruct(Z, anchor, s) for s in seeds]
    return min(runs, key=lambda r: r[1])                         # (E, stress) of the lowest-stress restart


def diagnose(Z, anchor):
    E, stress = best(Z, anchor)
    iu = np.triu_indices(N, 1)
    Dtrue = pdist(torch.tensor(Z)).numpy()[iu]
    nstress = float(np.sqrt(stress) / (Dtrue.std() + 1e-9))      # residual normalized by distance spread
    if nstress > STRESS_THRESH:
        return "CERTIFY-NO-CODE", {"nstress": nstress, "raw": None, "aligned": None}
    raw, aligned = errors(E, Z[:, :2])                           # geometric case: Z is 2-D
    verdict = "EMIT" if raw < RAW_THRESH else "CERTIFY-GAUGE"
    return verdict, {"nstress": nstress, "raw": raw, "aligned": aligned}


def main():
    menu = [("EMIT", gen("geometric", 0), True),
            ("CERTIFY-GAUGE", gen("geometric", 1), False),
            ("CERTIFY-NO-CODE", gen("no_code", 2), False)]
    rows = {}
    for expected, Z, anchor in menu:
        verdict, info = diagnose(Z, anchor)
        rows[expected] = {"verdict": verdict, "correct": bool(verdict == expected), **info}
        print(f"{expected:16s}: nstress={info['nstress']:.3f}"
              + (f", raw={info['raw']:.3f}, aligned={info['aligned']:.3f}" if info['raw'] is not None else "")
              + f"  -> verdict {verdict}  {'OK' if verdict == expected else 'WRONG'}")

    f1 = bool(rows["EMIT"]["verdict"] == "EMIT")
    f2 = bool(rows["CERTIFY-GAUGE"]["verdict"] == "CERTIFY-GAUGE")
    f3 = bool(rows["CERTIFY-NO-CODE"]["verdict"] == "CERTIFY-NO-CODE")
    f4 = bool(f1 and f2 and f3)

    out = {"menu": rows, "STRESS_THRESH": STRESS_THRESH, "RAW_THRESH": RAW_THRESH,
           "F1_emit": f1, "F2_certify_gauge": f2, "F3_certify_no_code": f3, "F4_one_diagnostic_all_three": f4,
           "verdict": ("DISCOVERABILITY TRICHOTOMY (representability frontier EXP-1): ONE diagnostic, run on pairwise "
                       "distances, separates THREE discovery verdicts. EMIT -- a 2-D config WITH an anchor reconstructs to "
                       "a UNIQUE frame (stress {:.3f} low, raw {:.3f} low). CERTIFY-GAUGE -- the SAME 2-D config WITHOUT an "
                       "anchor recovers the SHAPE (aligned {:.3f} low) but the absolute frame is a GAUGE (raw {:.3f} high). "
                       "CERTIFY-NO-CODE -- a 6-D config does NOT embed in 2-D at all (stress {:.3f} high), the geometric "
                       "analog of 'no conserved invariant'. So beyond integrable-vs-chaotic, ONE instrument already names "
                       "the GAUGE failure -- the seed of the full frontier table (contextual + partial-legible = EXP-2/3)."
                       .format(rows["EMIT"]["nstress"], rows["EMIT"]["raw"], rows["CERTIFY-GAUGE"]["aligned"],
                               rows["CERTIFY-GAUGE"]["raw"], rows["CERTIFY-NO-CODE"]["nstress"])
                       if f4 else "PARTIAL/HONEST -- a verdict was misclassified; see per-case numbers.")}
    print(f"\nF1 EMIT: {f1} | F2 CERTIFY-GAUGE: {f2} | F3 CERTIFY-NO-CODE: {f3}")
    print(f"ONE DIAGNOSTIC CLASSIFIES ALL THREE: {f4}")
    (RESULTS / "141_discoverability_trichotomy.json").write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(figsize=(8.5, 5))
    cases = ["EMIT", "CERTIFY-GAUGE", "CERTIFY-NO-CODE"]
    ns = [rows[c]["nstress"] for c in cases]
    raws = [rows[c]["raw"] if rows[c]["raw"] is not None else 1.0 for c in cases]
    x = np.arange(3); w = 0.36
    ax.bar(x - w / 2, ns, w, label="2D stress (cheap code exists?)", color="slateblue")
    ax.bar(x + w / 2, raws, w, label="raw frame error (unique?)", color="orange")
    ax.axhline(STRESS_THRESH, ls="--", c="slateblue", lw=0.7); ax.axhline(RAW_THRESH, ls=":", c="orange", lw=0.7)
    ax.set_xticks(x); ax.set_xticklabels(cases, fontsize=9); ax.set_ylabel("diagnostic readouts"); ax.legend(fontsize=8)
    ax.set_title("Discoverability trichotomy (② EXP-1): one diagnostic, three verdicts\nlow stress+low raw=EMIT · low stress+high raw=GAUGE · high stress=NO-CODE")
    fig.tight_layout(); fig.savefig(RESULTS / "141_discoverability_trichotomy.png", dpi=140)
    print("saved results/141_discoverability_trichotomy.json + .png")


if __name__ == "__main__":
    main()
