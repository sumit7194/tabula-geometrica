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

KNOWN BLIND SPOT, stated because a census that claims completeness it does not have is worse than
one that bounds itself. This matches ABSOLUTE paths. A script that does

    os.chdir("/Users/sumit/Github/conjecture_machine")   <- caught
    open("data/triple/K1_A.txt")                         <- INVISIBLE, relative after the chdir

has a data dependency this gate cannot see. Both currently-declared files do exactly that, so the
census reports their IMPORT edge and misses their DATA edge. The chdir is always caught, so the FILE
is never missed -- what is under-reported is the KIND and count of edges within an already-flagged
file. A file that read sibling data with no import and no absolute path would be missed entirely.

Classification (TheBridge's VENV/IMPORT split, adopted): running under a sibling's interpreter is a
dependency on their ENVIRONMENT, not their code, and VENV references are reported but do NOT count
as edges. A census that cannot tell an interpreter from an import produces a big number and no
finding -- the first job of an edge census is to be believed.
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
        # The census does not scan ITSELF: its docstring documents the pattern it matches, so
        # writing down what it looks for made it flag itself as an edge. Excluded by resolved FILE
        # IDENTITY, never by a name pattern -- `grep -v grep` deletes any neighbour that happens to
        # be a grep (silent_nulls 49), whereas one exact path removes exactly one file.
        if p.resolve() == Path(__file__).resolve():
            continue
        try:
            text = p.read_text(errors="ignore")
        except OSError:
            continue
        # MUST be a filesystem path, not a slash in prose. The first version of this gate matched
        # "ansatz/TheBridge's rule 33, adopted" in a comment and reported a code edge that does not
        # exist. A gate that cries wolf gets switched off (silent_nulls 55), so it anchors on the
        # repo root that a real cross-repo reference here always carries.
        hits = []
        for sib in SIBLINGS:
            pat = rf"/Users/sumit/Github/{re.escape(sib)}\b"
            for line in text.splitlines():
                if not re.search(pat, line):
                    continue
                # CLASSIFY. Running under a sibling's interpreter is a dependency on their
                # ENVIRONMENT, not on their code. Folding the two together reports coupling that
                # is not there, and a census that cannot tell an interpreter from an import
                # produces a big number and no finding. (TheBridge's VENV/IMPORT split, adopted:
                # their run had 94 of 151 path references as .venv shebangs.)
                if re.search(r"\.venv|bin/python", line):
                    kind = "VENV"
                elif re.search(r"sys\.path|import\b|chdir", line):
                    kind = "IMPORT"
                elif re.search(r"open\(|read_text|load|\.txt|\.json|\.npz|\.csv", line):
                    kind = "DATA"
                else:
                    kind = "REF"
                hits.append(f"{kind}:{sib}")
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
    code_edges = {k: v for k, v in found.items() if any(not h.startswith("VENV:") for h in v)}
    undeclared = sorted(set(code_edges) - set(DECLARED))
    vanished = sorted(set(DECLARED) - set(code_edges))
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
    venv_only = len(found) - len(code_edges)
    print(f"PASS  cross-repo dependency census ({len(code_edges)} declared code edge(s)"
          + (f", {venv_only} environment-only, not edges" if venv_only else "") + ")")
    return 0


if __name__ == "__main__":
    sys.exit(main())
