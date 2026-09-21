"""Step 189 — the systematic hunt for UNMADE FREE INSTRUMENTS across this repo's results.

A quantity that exists as two columns in your own output is the cheapest instrument available, and it stays
unmade because making it is nobody's job: a gate computes what it was told to compute, and the ratios BETWEEN
its outputs are the part no one is assigned. §187 carried two such pairs and neither was made until someone
went looking for something else.

PRE-REGISTERED in notes/free_instruments_prereg.md before this file existed, because the hunt is trivially
fishable: 255 files x dozens of fields gives an enormous number of computable ratios, almost all meaningless,
and an unbounded search always "finds something".

SCOPE, frozen: only pairs whose KEY NAMES are identical apart from ONE qualifier token from a fixed list --
the cases where the author already believed the two numbers were comparable. No free-form pairing.
"""

import json
import re
import sys
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "curvature" / "results"

QUALIFIERS = {
    "measured", "derived", "true", "predicted", "analytic", "textbook", "fit",
    "control", "baseline", "random", "shuffled", "blind",
    "poly", "polynomial", "rational", "transcendental",
    "train", "test", "heldout", "held",
    "before", "after",
    "crit", "critical", "gapped",
}
RATIO_HI, RATIO_LO = 3.0, 1.0 / 3.0


def tokens(key):
    return [t for t in re.split(r"[_.\-]+", key.lower()) if t]


def flat(o, pre=""):
    out = {}
    if isinstance(o, dict):
        for k, v in o.items():
            out.update(flat(v, f"{pre}.{k}" if pre else str(k)))
    elif isinstance(o, (int, float)) and not isinstance(o, bool):
        out[pre] = float(o)
    return out


def differ_by_one_qualifier(a, b):
    """True iff the two key token-lists are identical except at ONE position, where both differ and at
    least one side is a known qualifier."""
    ta, tb = tokens(a), tokens(b)
    if len(ta) != len(tb):
        return None
    diffs = [i for i, (x, y) in enumerate(zip(ta, tb)) if x != y]
    if len(diffs) != 1:
        return None
    i = diffs[0]
    if ta[i] in QUALIFIERS or tb[i] in QUALIFIERS:
        return (ta[i], tb[i])
    return None


def main():
    hits, pairs_examined, files_with_pairs = [], 0, 0
    for f in sorted(RESULTS.glob("*.json")):
        try:
            d = json.load(open(f))
        except Exception:
            continue
        if not isinstance(d, dict):
            continue
        verdict_text = " ".join(str(v) for v in d.values() if isinstance(v, str))
        nums = flat(d)
        keys = list(nums)
        found_here = False
        for a, b in combinations(keys, 2):
            q = differ_by_one_qualifier(a, b)
            if not q:
                continue
            va, vb = nums[a], nums[b]
            if va == 0 or vb == 0 or not all(map(lambda x: x == x and abs(x) != float("inf"), (va, vb))):
                continue
            pairs_examined += 1
            found_here = True
            r = va / vb
            ar = abs(r)
            if ar > RATIO_HI or ar < RATIO_LO:
                # pre-registered suppression: skip if the ratio is already quoted in the file's own prose
                rs = f"{ar:.3g}"
                if rs[:3] in verdict_text:
                    continue
                hits.append({"file": f.name, "key_a": a, "key_b": b, "qualifiers": list(q),
                             "val_a": va, "val_b": vb, "ratio": r})
        files_with_pairs += int(found_here)

    # ---- CLASSIFY, because "flagged" is not "missed" -------------------------------------------------
    # Two defects this scan found in ITSELF on first contact with the repo, both recorded rather than
    # quietly patched:
    #   (i)  the qualifier match pairs INCOMPATIBLE METRICS -- `X_heldout` against `X_R2` is an error against
    #        a goodness-of-fit, not two estimates of one quantity. Loose matching, not a finding.
    #   (ii) the suppression check read only the file's PROSE, so it missed ratios already stored as their
    #        OWN FIELD (§178 keeps `control_improves_more_by` = 41464.8; §41 keeps `slope_ratio_gap_over_crit`).
    #        An instrument already made under another name is still made.
    INCOMPATIBLE = {"r2"}
    for h in hits:
        try:
            f = json.load(open(RESULTS / h["file"]))
        except Exception:
            continue
        nums, prose = flat(f), " ".join(str(v) for v in f.values() if isinstance(v, str)).lower()
        qa, qb = h["qualifiers"]
        if {qa, qb} & INCOMPATIBLE:
            h["class"] = "false-pair: qualifier matched across incompatible metrics"
            continue
        r = abs(h["ratio"])
        where = None
        for k, v in nums.items():
            if k in (h["key_a"], h["key_b"]) or v == 0:
                continue
            if any(abs(v - t) / max(abs(t), 1e-300) < 0.01 for t in (r, 1 / r)):
                where = k
                break
        if where or any(c in prose for c in {f"{r:,.0f}", f"{1/r:,.0f}"} if len(c) > 2):
            h["class"] = f"already-made: stored as `{where}`" if where else "already-made: quoted in prose"
        else:
            h["class"] = "unmade-or-asserted-as-a-gate"

    hits.sort(key=lambda h: -abs(h["ratio"]) if abs(h["ratio"]) > 1 else -1 / abs(h["ratio"]))
    out = {
        "prereg": "notes/free_instruments_prereg.md (committed before this script existed)",
        "files_scanned": len(list(RESULTS.glob("*.json"))),
        "files_containing_a_qualified_pair": files_with_pairs,
        "pairs_examined": pairs_examined,
        "threshold": {"ratio_hi": RATIO_HI, "ratio_lo": RATIO_LO},
        "n_hits": len(hits),
        "hits": hits[:40],
        "scope_limit": (
            "THE SCAN CANNOT DISTINGUISH 'nobody noticed' FROM 'asserted as a gate rather than stored as a "
            "ratio'. §65's steer-vs-control 78x and §18's kaluza-vs-control are the POINT of those gates and "
            "are asserted as thresholds (a beats b by X) without the quotient ever being written down. That is "
            "not a missed instrument. Naming this limit is the honest result of tonight's run; separating the "
            "two classes needs the gate ASSERTIONS parsed, not the results files, and that is a further build."),
        "note": ("A hit is a FLAG FOR A LOOK, not a result. Per the pre-registration none is explained here; "
                 "explaining a surprising ratio the moment it appears is how a fishing expedition becomes a "
                 "finding. Near-unity pairs are reported only as a count."),
    }
    (RESULTS / "189_free_instruments.json").write_text(json.dumps(out, indent=2))
    print(f"  files scanned            {out['files_scanned']}")
    print(f"  files with a qualified pair {files_with_pairs}")
    print(f"  qualified pairs examined {pairs_examined}")
    print(f"  HITS (|ratio|>3 or <1/3, not already quoted in the file's prose): {len(hits)}")
    for h in hits[:20]:
        print(f"     {h['file']:<38} {h['key_a']} / {h['key_b']}")
        print(f"        {h['val_a']:.6g} / {h['val_b']:.6g} = {h['ratio']:.4g}   [{h['qualifiers'][0]} vs {h['qualifiers'][1]}]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
