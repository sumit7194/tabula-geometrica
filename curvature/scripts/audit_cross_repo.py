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
file.

The case that WOULD have been missed entirely -- a file using a sibling with neither an absolute
path nor an in-file sys.path.insert -- is now closed by SIBLING_MODULE_PREFIXES, which detects the
module namespace directly. Verified against this repo: all four bare `_kt_*` imports live in files
the path census already flags, so the hole is not live today; the second signal exists because
nothing guarantees tomorrow. The symmetric case in TheBridge was 20 bare sibling imports hidden
behind a caught path constant -- same structure, opposite direction.

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

# A SECOND, PATH-INDEPENDENT SIGNAL. A bare `import _kt_double` carries no path and works only
# because a sys.path.insert ran earlier in the SAME file -- so a path-only census sees the insert
# and not the import, and a file with the import and NO insert (importing via PYTHONPATH, a .pth,
# or an installed package) would be missed ENTIRELY. TheBridge hit this from the other direction:
# 20 bare sibling-module imports hiding behind a caught path constant. Detecting the module
# namespace closes the case neither path-census could see.
SIBLING_MODULE_PREFIXES = {"_kt_": "conjecture_machine"}

DECLARED: dict[str, str] = {
    "curvature/scripts/leg6_dK/make_dK.py":
        "imports conjecture_machine's _kt_* solver and reads data/triple/K1_A.txt to BUILD dK. "
        "File-level vendoring: any claim of the form 'dK does X' is ONE measurement, not two.",
    "curvature/scripts/leg6_dK/dK_control.py":
        "same solver import, for the K1 known-fail arm of the dK bridge control. Same scoping.",
}

SKIP_DIRS = {".git", ".venv", "__pycache__", "node_modules"}


_LOCAL_MODULES: set[str] | None = None


def _resolves_locally(mod: str) -> bool:
    """True if this repo itself provides the module -- then it is not a sibling edge."""
    global _LOCAL_MODULES
    if _LOCAL_MODULES is None:
        _LOCAL_MODULES = {q.stem for q in ROOT.rglob("*.py")
                          if not any(d in q.parts for d in SKIP_DIRS)}
    return mod in _LOCAL_MODULES


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
        for line in text.splitlines():
            m = re.match(r"\s*(?:from|import)\s+(_[a-z0-9_]+)", line)
            if m:
                mod = m.group(1)
                for pref, sib in SIBLING_MODULE_PREFIXES.items():
                    # RESOLVE, do not assume. A hand-built namespace list mislabels any LOCAL module
                    # that happens to share the prefix. TheBridge's empirical build caught four of
                    # their own modules that a by-eye list would have declared sibling edges, so the
                    # prefix is necessary and not sufficient: it is an edge only if nothing here
                    # provides the module.
                    if mod.startswith(pref) and not _resolves_locally(mod):
                        hits.append(f"NAMESPACE:{sib}")
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
        # KNOWN-FAIL ARMS THAT EXERCISE scan() ITSELF. The first version of this control built a
        # FAKE dict and tested only the set logic -- it would have passed with the scanner entirely
        # broken, which is a control on its way to being decoration (quantum hit exactly this: their
        # known-fail turned out to be dead code and reported a live gate as ornamental).
        import tempfile, shutil
        tmp = Path(tempfile.mkdtemp(prefix="xrepo_selftest_", dir=ROOT / "curvature" / "scripts"))
        ok = []
        try:
            (tmp / "planted_path.py").write_text(
                "x = '/Users/sumit/Github/BlackHole/thing.py'\n")
            (tmp / "planted_nopath.py").write_text("import _kt_double as KD\n")
            (tmp / "planted_local.py").write_text("import _kt_localonly\n")
            (tmp / "_kt_localonly.py").write_text("# a LOCAL module sharing the sibling prefix\n")
            global _LOCAL_MODULES
            _LOCAL_MODULES = None
            found = scan()
            rel = lambda n: f"{tmp.relative_to(ROOT)}/{n}"
            # a bare path CONSTANT is a REF, not an IMPORT -- the requirement is that it registers
            # as a non-VENV edge at all, not that it lands in a particular class. Asserting the
            # class was my own wrong expectation, and the first run of this arm caught it: the
            # previous fake-dict control could not have, because it never called scan().
            hits_p = found.get(rel("planted_path.py"), [])
            a = any(h.endswith(":BlackHole") and not h.startswith("VENV:") for h in hits_p)
            b = any(h.startswith("NAMESPACE:") for h in found.get(rel("planted_nopath.py"), []))
            c = rel("planted_local.py") not in found
            for lbl, v in (("absolute-path edge detected", a),
                           ("path-less sibling import detected", b),
                           ("LOCAL module sharing the prefix NOT flagged", c)):
                print(f"  {'OK  ' if v else 'BAD '} selftest: {lbl}")
                ok.append(v)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
            _LOCAL_MODULES = None
        return 0 if all(ok) else 1

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
