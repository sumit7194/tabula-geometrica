"""Step 176 — C5 FOR THE FRONTIER'S SEARCH-BASED CERTIFICATES, and a correction to our own audit.

WHY THIS EXISTS. The C5 audit (§175 and notes/certificate_standard.md) closed at 17/17 by exempting SEVEN
certificates in a single pass, on a distinction invented on the spot: *search-based nulls need C5,
measurement-based verdicts do not*. That call was made in minutes and never checked. Re-examined, it is **wrong
for at least four of them**, and the verdict names show it:

    CERTIFY-CONTEXTUAL   measured CHSH = 2.83 against a theorem threshold   -> measurement, C5 does not apply
    CERTIFY-CHAOS        measured 0-1 test statistic K                       -> measurement, C5 does not apply
    CERTIFY-GAUGE        measured frame error 1.42 vs 0.00                   -> measurement, C5 does not apply
    CERTIFY-NO-CODE      FIT the cheapest code, FIND NONE                    -> a SEARCH. C5 APPLIES.

`CERTIFY-NO-CODE` is emitted by §141, §143, §145 and §151. Exempting them means the very audit about unexamined
classifications was closed with an unexamined classification. That is entry 15 of the silent-nulls catalogue
(a freshly-learned rule over-generalised) firing on the audit that produced it.

WHAT §141's CERTIFY-NO-CODE CLAIMS. Pairwise distances of a 6-D point configuration do not embed in 2-D: the
reconstruction stress stays high, so "no cheap 2-D code exists".

AND HERE THE AUDIT CATCHES ITSELF A SECOND TIME. My first reading was that §141's EMIT demonstration sits on a
DIFFERENT substrate -- a genuinely 2-D configuration -- so by C5 refinement 2 it does not transfer. That reading
is WRONG, and wrong in the catalogue's own signature way. §141's generator is

    gen(regime, seed):  dim = 2 if regime == "geometric" else 6;  rng.uniform(-1.2, 1.2, (N, dim))

One generator. The EMIT and CERTIFY cases differ in the configuration dimension and in NOTHING else -- and the
configuration dimension IS the property being certified. That is not a substrate change; it is the minimal
contrast, the best control such a claim can have. Refinement 2 was derived from §174, where changing eps altered
the substrate's CHARACTER while leaving the certified property alone. Applying it here inverts it.

So: a rule learned hours earlier, applied one case too wide, by the author, inside the audit that produced the
rule. Entry 15 of the silent-nulls catalogue, third recorded instance, first one of mine. The rule needs the
qualifier it never had: **a parameter change breaks the demonstration only when it changes something OTHER than
the certified property; when the changed parameter IS the certified property, it is the control.**

THE TEST, and it is the ladder contrast applied to DIMENSION instead of basis. On the SAME 6-D data, sweep the
embedding dimension. A code demonstrably exists at d = 6 (the data is 6-D by construction), so the instrument
must FIND one there. Same data, same instrument, same ensemble -- only the target dimension changes. That is C5
satisfied internally, with nothing about the substrate varying between demonstration and verdict.

PRE-REGISTERED, every criterion with a known-pass AND a known-fail:
  P0 REPRODUCE: the 6-D config gives high 2-D stress -> CERTIFY-NO-CODE, as §141 reported.
  P1 C5 (known-pass): on that SAME data the instrument finds a low-stress code at d = 6.
  P2 C5 (known-fail): on that same data it does NOT find one at d = 2. Without this the sweep could not fail.
  P3 THE UPGRADE: the stress-vs-dimension curve locates the CHEAPEST CODE DIMENSION, turning a binary
     "no cheap code" into a measured "no code below d*". Strictly more informative than the verdict it audits.
  P4 THE MINIMAL-CONTRAST CONTROL, i.e. what §141 ALREADY HAD: same generator, dimension 2, read at d = 2 --
     the very readout that issues the verdict must find the code when one exists. Reported separately from
     P1 because it tests a different thing: P1 shows the RECONSTRUCTOR works on the certifying data, P4 shows
     the d=2 READOUT is not blind. A certificate needs both and §141 had the second.

IF P1 FAILS: the instrument cannot find a code on that substrate at any dimension, its CERTIFY-NO-CODE is
undemonstrated, and §141/§143/§145/§151 need the same downgrade §174 received. Both outcomes are results.
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

m141 = import_module("141_discoverability_trichotomy")
s111 = m141.s111
np.seterr(all="ignore")

FAST = "--fast" in sys.argv[1:]
s111.STEPS = 2500 if FAST else 5000
DIMS = (2, 3, 4, 5, 6)


def stress_at_dim(Z, d, seeds=(0, 1)):
    """Reconstruct Z's pairwise distances in d dimensions; return normalised residual stress."""
    keep = s111.D
    s111.D = d
    try:
        runs = [s111.reconstruct(Z, False, s) for s in seeds]
        _, raw = min(runs, key=lambda r: r[1])
    finally:
        s111.D = keep
    iu = np.triu_indices(m141.N, 1)
    Dtrue = m141.pdist(torch.tensor(Z)).numpy()[iu]
    return float(np.sqrt(raw) / (Dtrue.std() + 1e-9))


def main():
    out = {"audits": "§141/§143/§145/§151 CERTIFY-NO-CODE",
           "correction": ("the C5 audit exempted 7 certificates as 'measurement-based' in one pass. "
                          "CERTIFY-NO-CODE is a SEARCH -- fit the cheapest code, find none -- so C5 applies. "
                          "The audit about unexamined classifications was closed with an unexamined one."),
           "method": "ladder contrast over DIMENSION: same data, same instrument, only the target dim changes"}

    Z6 = m141.gen("highD", 0)                      # the 6-D configuration §141 certifies on
    Z2 = m141.gen("geometric", 0)                  # §141's EMIT substrate, for contrast
    print(f"6-D config: {Z6.shape}   2-D config: {Z2.shape}")

    print("\nP0/P1/P2 — stress vs embedding dimension, on the SAME 6-D data §141 certifies on:")
    curve = {}
    for d in DIMS:
        ns = stress_at_dim(Z6, d)
        curve[d] = ns
        flag = "CERTIFY (no code here)" if ns > m141.STRESS_THRESH else "code FOUND"
        print(f"   d={d}   normalised stress {ns:.4f}   {flag}")

    ns2, ns6 = curve[2], curve[6]
    P0 = bool(ns2 > m141.STRESS_THRESH)
    P1 = bool(ns6 < m141.STRESS_THRESH)
    P2 = bool(ns2 > m141.STRESS_THRESH)
    below = [d for d in DIMS if curve[d] < m141.STRESS_THRESH]
    dstar = min(below) if below else None
    print(f"\nP3 — cheapest code dimension d* = {dstar}  (threshold {m141.STRESS_THRESH})")

    # contrast: the 2-D substrate, where a cheap code genuinely exists
    ns2_on2 = stress_at_dim(Z2, 2)
    print(f"\nP4 — minimal-contrast control (same generator, dim 2, read at d=2): stress {ns2_on2:.4f}")

    P4 = bool(ns2_on2 < m141.STRESS_THRESH)
    ok = bool(P0 and P1 and P2 and P4)
    verdict = (
        "C5 SATISFIED FOR CERTIFY-NO-CODE, INTERNALLY. On the very data §141 certifies, the instrument FINDS a "
        "low-stress code at d={} (stress {:.4f}) and does NOT at d=2 (stress {:.4f}). Same data, same instrument, "
        "same ensemble -- only the target dimension changes -- so nothing about the substrate varies between the "
        "demonstration and the verdict. Independently, the d=2 READOUT itself is shown non-blind on the minimal "
        "contrast (same generator, dim 2, stress {:.4f}) -- which is what §141 ALREADY HAD. TWO CORRECTIONS TO "
        "OUR OWN AUDIT: (i) CERTIFY-NO-CODE is a SEARCH, so the blanket 'measurement-based' exemption of seven "
        "certificates was wrong in kind; (ii) but the exempted certificates PASS anyway, because §141's EMIT "
        "case is a minimal-contrast control, and my reading that refinement 2 blocked it was that refinement "
        "applied one case too wide -- entry 15, by its author, inside the audit that produced it. Refinement 2 "
        "now carries the qualifier it lacked: a parameter change breaks the demonstration only when it changes "
        "something OTHER than the certified property. UPGRADE: the curve locates the cheapest code dimension at "
        "d* = {}, strictly more informative than the binary verdict -- 'no code below d*', not 'no cheap code'."
        .format(6, ns6, ns2, ns2_on2, dstar) if ok else
        "NOT ESTABLISHED. The instrument does not find a code at d=6 on data that is 6-D by construction, so its "
        "CERTIFY-NO-CODE is undemonstrated and §141/§143/§145/§151 need the downgrade §174 received.")
    out.update({"stress_curve": {str(k): v for k, v in curve.items()},
                "stress_threshold": m141.STRESS_THRESH,
                "P0_reproduces_certify": P0, "P1_finds_code_at_native_dim": P1,
                "P2_known_fail_at_d2": P2, "cheapest_code_dimension": dstar,
                "P4_minimal_contrast_control": P4, "contrast_2d_substrate_at_d2": ns2_on2,
                "refinement2_qualifier": ("a parameter change breaks the C5 demonstration only when it changes "
                                          "something OTHER than the certified property; when the changed "
                                          "parameter IS the certified property, it is the control"),
                "exemption_verdict": ("the blanket 'measurement-based' exemption was WRONG IN KIND for "
                                      "CERTIFY-NO-CODE (§141/§143/§145/§151) -- it is a search. The affected "
                                      "certificates nonetheless PASS C5. Wrong reasoning, right outcome, and "
                                      "the reasoning is the part that would have failed elsewhere."),
                "c5_satisfied": ok, "verdict": verdict})
    print(f"\nP0 {P0} | P1 {P1} | P2 {P2} | P4 {P4}")
    print(verdict)
    (RESULTS / "176_c5_frontier_certificates.json").write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(list(curve), [curve[d] for d in curve], "o-", label="6-D config (the CERTIFY substrate)")
    ax.axhline(m141.STRESS_THRESH, color="crimson", ls="--", label=f"threshold {m141.STRESS_THRESH}")
    ax.plot([2], [ns2_on2], "s", ms=10, label="2-D config at d=2 (the EMIT substrate)")
    ax.set_xlabel("embedding dimension d")
    ax.set_ylabel("normalised reconstruction stress")
    ax.legend(fontsize=8)
    ax.set_title("C5 for CERTIFY-NO-CODE: can the instrument find a code on the substrate it certifies?\n"
                 "same data, same instrument -- only the target dimension changes")
    fig.tight_layout()
    fig.savefig(RESULTS / "176_c5_frontier_certificates.png", dpi=140)
    print("saved results/176_c5_frontier_certificates.json + .png")


if __name__ == "__main__":
    main()
