"""Scheduled documentation audit — the executable referee for CLAIMS, not results.

WHY THIS EXISTS. Every gate in verify.sh checks a NUMBER produced by a script. Nothing checked the CLAIMS the
documentation makes ABOUT those numbers, and on 2026-09-04 three of them were wrong at once: CLAUDE.md marked
two finished finales as not-done (eleven weeks), the JOURNAL carried an interval inherited from a peer's message
and never measured, and a peer's own motivating fact was off by ~2x for want of one `ls`.

THE FINDING THAT FORCED IT (deepstrain, relayed): they caught their version of the inherited figure only
because their user had asked them to audit the repo minutes earlier -- "luck wearing the costume of rigour."
Adding "check it anyway" to a protocol changes nothing, because THE MOMENT A CHECK NEEDS TO FIRE IS THE MOMENT
NOBODY IS LOOKING. Only a pass that runs whether or not anyone is suspicious reaches it -- the way a gate runs
whether or not anyone doubts the result.

SCOPE, deliberately narrow. Only claims that are MECHANICALLY checkable against repository state. No natural-
language parsing of physics claims: a check that is clever is a check that will be wrong, and a wrong audit is
worse than none because it teaches you to ignore it.

C5 SELF-APPLICATION. This file has a --selftest that PLANTS each inconsistency and requires the audit to catch
it. A gate whose known-fail control has never run is a gate that has only been shown to pass -- the criticism
made of a sibling's leg-gate the same afternoon, and it applies here first.
"""

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _read(rel):
    p = ROOT / rel
    return p.read_text(encoding="utf-8") if p.exists() else ""


def check_silent_nulls_count(claude_md, silent_nulls):
    """CLAUDE.md advertises a catalogue size. It is hand-edited every time an entry lands.

    THERE IS MORE THAN ONE SUCH CLAIM. Dated status blocks record the count as it was at the time ("silent_nulls
    → 18 entries"), which is a correct historical statement, while the newest block carries the live one. A
    first version of this check used re.search and took the FIRST match -- which would have compared against 18
    -- and passed only because the historical line words it differently enough to miss the pattern. **It was
    right by an accident of formatting**, which is not a property to build a gate on.

    Correct semantics: historical claims are <= actual, and the LIVE claim (the maximum) must EQUAL actual. A
    claim above the real count is always wrong; a claim below it may be a dated record.
    """
    claims = [int(x) for x in re.findall(r"silent_nulls → (\d+)", claude_md)]
    if not claims:
        return ["CLAUDE.md: no 'silent_nulls → N' claim found (was it renamed?)"]
    actual = silent_nulls.count("\n### ")
    bad = []
    # THE LIVE CLAIM IS THE LAST ONE. Status blocks are appended, so the newest block is furthest down.
    # Using max() instead -- the second version of this check -- passes a STALE live claim whenever some
    # historical line happens to equal the true count. Found by probing, not by reading: three faults now in
    # this one check, and each fix was a narrower positional heuristic until this one, which is the semantics.
    if claims[-1] != actual:
        bad.append(f"silent_nulls count: live claim (last in file) is {claims[-1]}, file has {actual} entries")
    # No claim may EXCEED the real count: a historical record is necessarily <= actual, so anything above it is
    # either stale-high or aspirational, and neither belongs in a status block.
    if max(claims) > actual:
        bad.append(f"silent_nulls count: a claim of {max(claims)} exceeds the actual {actual} entries")
    return bad


ART = re.compile(r"([0-9A-Za-z_.\-]+\.(?:json|pt|npz|npy|csv))")


def check_referenced_results_exist(*texts):
    """Every results artifact named in the docs must be on disk, or the claim citing it is unbacked.

    EXCEPT a DOCUMENTED RENAME. The first real run of this audit flagged `results/19_ckpt.pt`, which CLAUDE.md
    mentions only in the sentence recording that it was renamed to `19_ckpt_v1_failed.pt` -- a file that does
    exist. The citation is correct and the absence is the point of it.

    That was this gate being WRONG on its first live run, and it is the criticism made of a sibling's leg-gate
    the same afternoon landing on its author within the hour: the known-fail control proved the gate FIRES, not
    that its criterion was RIGHT. A control tests the mechanism; only contact with real data tests the rule.

    The exemption is kept deliberately mechanical -- an arrow to a name that exists, within a short window --
    rather than clever. A clever audit is one that will be wrong, and a wrong audit is worse than none because
    it teaches you to ignore it.
    """
    bad = []
    pat = re.compile(r"(?:curvature/)?results/([0-9A-Za-z_.\-]+\.(?:json|pt|npz|npy|csv))")
    seen = set()
    for t in texts:
        for m in pat.finditer(t):
            name = m.group(1)
            if name in seen:
                continue
            seen.add(name)
            if (ROOT / "curvature" / "results" / name).exists():
                continue
            tail = t[m.end():m.end() + 80]
            renamed = False
            if "→" in tail or "->" in tail:
                for cand in ART.findall(tail):
                    if (ROOT / "curvature" / "results" / cand).exists():
                        renamed = True
                        break
            if not renamed:
                bad.append(f"referenced results file missing: curvature/results/{name}")
    return bad


def check_referenced_scripts_exist(claude_md):
    """'script NNN' in the status blocks must correspond to a real scripts/NNN_*.py."""
    bad = []
    nums = sorted({int(n) for n in re.findall(r"\bscripts?\s+(\d{1,3})\b", claude_md)})
    sd = ROOT / "curvature" / "scripts"
    have = {int(m.group(1)) for f in sd.glob("*.py") if (m := re.match(r"(\d{1,3})_", f.name))}
    for n in nums:
        if n not in have:
            bad.append(f"CLAUDE.md cites 'script {n}' but curvature/scripts/{n}_*.py does not exist")
    return bad


def check_roadmap_marks(claude_md):
    """A roadmap item marked done must not sit beside an item claiming it is 'Next'.

    The 2026-09-04 bug exactly: items 4 and 5 read '⬜ Next' for eleven weeks after they closed.
    """
    bad = []
    for line in claude_md.splitlines():
        if "⬜" in line and re.search(r"\bCLOSED\b|\bDONE\b|✅", line):
            bad.append(f"roadmap line marked both undone and done: {line.strip()[:90]}")
    return bad


def run_audit():
    claude_md = _read("CLAUDE.md")
    silent_nulls = _read("writeups/silent_nulls.md")
    journal = _read("JOURNAL.md")
    readme = _read("README.md")
    problems = []
    problems += check_silent_nulls_count(claude_md, silent_nulls)
    problems += check_referenced_results_exist(claude_md, readme, journal)
    problems += check_referenced_scripts_exist(claude_md)
    problems += check_roadmap_marks(claude_md)
    return problems


def selftest():
    """KNOWN-FAIL CONTROL: plant each inconsistency, require detection. Nothing is written to disk."""
    claude_md = _read("CLAUDE.md")
    silent_nulls = _read("writeups/silent_nulls.md")
    results = []

    n = silent_nulls.count("\n### ")
    hit = check_silent_nulls_count(f"**silent_nulls → {n + 7}** blah", silent_nulls)
    results.append(("count drift (over)", bool(hit)))
    hit = check_silent_nulls_count(f"**silent_nulls → {n - 3}** blah", silent_nulls)
    results.append(("count drift (under)", bool(hit)))
    # a dated historical claim BELOW the live one must not trip it -- the multi-claim case the first
    # version of this check would have got wrong, and passed anyway by an accident of wording.
    hit = check_silent_nulls_count(f"old block: silent_nulls → 18 entries ... new block: **silent_nulls → {n}**",
                                   silent_nulls)
    results.append(("historical claim beside live claim", not hit))
    # fault 3, the mirror of a sibling's: a STALE live claim shadowed by a historical line that happens to
    # match the true count. The max() version of this check passed it.
    hit = check_silent_nulls_count(f"silent_nulls → {n} entries (old) ... **silent_nulls → {n - 1}**", silent_nulls)
    results.append(("stale live claim shadowed by correct historical", bool(hit)))
    # an aspirational target above the real count
    hit = check_silent_nulls_count(f"**silent_nulls → {n}** ... aiming for silent_nulls → {n + 40}", silent_nulls)
    results.append(("aspirational claim above actual", bool(hit)))

    hit = check_referenced_results_exist("see curvature/results/999_does_not_exist.json for the gate")
    results.append(("missing results file", bool(hit)))

    # the false positive this gate produced on its own first live run: a DOCUMENTED rename must pass...
    hit = check_referenced_results_exist("Stale results/19_ckpt.pt renamed → 19_ckpt_v1_failed.pt (trap defused)")
    results.append(("documented rename NOT flagged", not hit))
    # ...but an arrow to a file that also does not exist must still fail.
    hit = check_referenced_results_exist("results/19_ckpt.pt renamed → 998_also_missing.pt")
    results.append(("rename to a missing target still flagged", bool(hit)))

    hit = check_referenced_scripts_exist("as shown in script 997 the effect vanishes")
    results.append(("missing script", bool(hit)))

    hit = check_roadmap_marks("5. ⬜ **Finale 3 — Kaluza-Klein. CLOSED, and it became a trilogy.**")
    results.append(("roadmap contradiction", bool(hit)))

    clean = check_silent_nulls_count(claude_md, silent_nulls) + check_roadmap_marks(claude_md)
    results.append(("no false positive on real docs", not clean))

    print("--- known-fail control (each planted fault must be CAUGHT) ---")
    ok = True
    for name, caught in results:
        print(f"  {'CAUGHT ' if caught else 'MISSED '} {name}")
        ok &= caught
    return ok


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(0 if selftest() else 1)
    probs = run_audit()
    if probs:
        print("FAIL  documentation claims audit")
        for p in probs:
            print("   -", p)
        sys.exit(1)
    print("PASS  documentation claims audit (counts, cited results, cited scripts, roadmap marks)")
