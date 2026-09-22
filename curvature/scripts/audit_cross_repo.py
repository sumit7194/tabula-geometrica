#!/usr/bin/env python3
"""Cross-repo dependency gate: sibling-repo edges must be DECLARED, not asserted in prose.

WHY THIS EXISTS (silent_nulls 68). A pre-registration here said "their solver is not being imported
into any SpaceTime script." It was true when written -- those scripts were in a scratchpad. Then they
were PROMOTED into the repo, which is filing rather than claiming, and the sentence went false with
nothing to notice. An independence audit by a sibling session found it by asking a question this repo
had already answered in writing.

    Code has imports and a build breaks when a dependency moves.
    A claim in prose has no dependencies and never recompiles.

So the claim is moved out of prose: every sibling-repo reference must appear in DECLARED below, with
a reason. A new, undeclared edge fails the gate. A declared edge that disappears also fails, because
a stale allowlist is a scope statement with the same defect as the sentence it replaced.

This is a CENSUS, not a prohibition. Cross-repo reads are legitimate here; what is illegitimate is a
repo-level claim about them that nothing re-checks.
"""
from __future__ import annotations
import re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SIBLINGS = ("conjecture_machine", "TheBridge", "BlackHole", "quantum")

DECLARED: dict[str, str] = {
    "curvature/scripts/leg6_dK/make_dK.py":
        "imports conjecture_machine's _kt_* solver and reads data/triple/K1_A.txt to BUILD dK. "
        "File-level vendoring: any claim of the form 'dK does X' is ONE measurement, not two.",
    "curvature/scripts/leg6_dK/dK_control.py":
        "same solver import, for the K1 known-fail arm of the dK bridge control. Same scoping.",
}

SKIP_DIRS = {".git", ".venv", "__pycache__", "node_modules"}


def scan() -> dict[str, list[str]]:
    found: dict[str, list[str]] = {}
    for p in ROOT.rglob("*.py"):
        if any(d in p.parts for d in SKIP_DIRS):
            continue
        try:
            text = p.read_text(errors="ignore")
        except OSError:
            continue
        # MUST be a filesystem path, not a slash in prose. The first version of this gate matched
        # "ansatz/TheBridge's rule 33, adopted" in a comment and reported a code edge that does not
        # exist. A gate that cries wolf gets switched off (silent_nulls 55), so it anchors on the
        # repo root that a real cross-repo reference here always carries.
        hits = [s for s in SIBLINGS if re.search(rf"/Users/sumit/Github/{re.escape(s.split('/')[-1])}\b", text)]
        if hits:
            found[str(p.relative_to(ROOT))] = sorted(set(hits))
    return found


def main() -> int:
    if "--selftest" in sys.argv:
        # KNOWN-FAIL: a gate that cannot fail is not a gate.
        fake = {"curvature/scripts/leg6_dK/make_dK.py": ["conjecture_machine"],
                "curvature/scripts/999_undeclared.py": ["BlackHole"]}
        undeclared = sorted(set(fake) - set(DECLARED))
        ok = undeclared == ["curvature/scripts/999_undeclared.py"]
        print(f"  {'OK  ' if ok else 'BAD '} selftest: an undeclared edge is detected ({undeclared})")
        missing = sorted(set(DECLARED) - set(fake))
        ok2 = "curvature/scripts/leg6_dK/dK_control.py" in missing
        print(f"  {'OK  ' if ok2 else 'BAD '} selftest: a vanished declared edge is detected ({missing})")
        return 0 if (ok and ok2) else 1

    found = scan()
    undeclared = sorted(set(found) - set(DECLARED))
    vanished = sorted(set(DECLARED) - set(found))
    for path in sorted(found):
        mark = "declared" if path in DECLARED else "UNDECLARED"
        print(f"  {mark:<10} {path}  -> {', '.join(found[path])}")
    bad = []
    if undeclared:
        bad.append(f"UNDECLARED sibling-repo edge(s): {undeclared} -- add to DECLARED with a reason, "
                   f"or remove the reference. A prose claim about cross-repo scope is not sufficient.")
    if vanished:
        bad.append(f"DECLARED edge(s) no longer present: {vanished} -- remove from DECLARED. "
                   f"A stale allowlist has the same defect as the sentence it replaced.")
    if bad:
        print("FAIL  cross-repo dependency census")
        for b in bad:
            print("   - " + b)
        return 1
    print(f"PASS  cross-repo dependency census ({len(found)} declared edge(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
