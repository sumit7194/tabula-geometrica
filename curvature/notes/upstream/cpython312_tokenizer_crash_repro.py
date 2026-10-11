"""Minimal repro DRAFT (not yet filed; filing is the user's call): sympy.parse_expr on a ~26 KB single-line,
deeply nested sympy srepr string intermittently SEGFAULTS, or silently corrupts the heap, under Homebrew
Python 3.12.13 on macOS (arm64).

Observed in tabula-geometrica §195, 2026-10-11 (Python 3.12.13, sympy 1.14.0, numpy 2.4.6):
- About 5 of 12 isolated processes crashed. Each parsed 9 such strings 2-3 times, then did numpy work.
- One faulthandler stack went straight into the tokenizer:
    tokenize.py:584 _generate_tokens_from_c_tokenizer
    sympy/parsing/sympy_parser.py:890 stringify_expr
    sympy/parsing/sympy_parser.py:1075 parse_expr
- The other crashes were DELAYED symptoms of heap corruption:
    EXC_BREAKPOINT in libsystem_malloc xzm_realloc inside numpy;
    "pthread_mutex_trylock: Invalid argument";
    segfaults in torch static destructors and in gc during Py_FinalizeEx.
- After replacing parse_expr with a tokenizer-free parser, the crashes stopped (see the §195 stress checks).
- The Bridge reports that restricted eval() on Python 3.14.5 was clean over 20 runs.

Usage:  python cpython312_tokenizer_crash_repro.py <file-with-'name = srepr'-lines> [iterations]
Mode A (default) uses sympy.parse_expr. Mode B ('compile') runs plain compile() on the same text: if B also crashes,
the bug is in CPython itself and not in sympy's use of tokenize.
Run under:  python -X faulthandler  and  PYTHONMALLOC=debug
"""
import sys

path = sys.argv[1]
iters = int(sys.argv[2]) if len(sys.argv) > 2 else 20
mode = sys.argv[3] if len(sys.argv) > 3 else "parse_expr"
lines = [l.split("=", 1)[1].strip() for l in open(path) if "=" in l and not l.startswith("#")]
print(f"{len(lines)} srepr strings, longest {max(map(len, lines))} chars, mode={mode}, iterations={iters}", flush=True)
if mode == "parse_expr":
    import sympy as sp
    from sympy.parsing.sympy_parser import parse_expr
    ns = {k: getattr(sp, k) for k in ("Mul", "Add", "Pow", "Integer", "Rational", "Symbol")}
    for i in range(iters):
        for s in lines:
            parse_expr(s, local_dict=ns)
        print("iteration", i, "ok", flush=True)
else:
    import io, tokenize
    for i in range(iters):
        for s in lines:
            compile(s, "<srepr>", "eval")                                          # PEG parser path
            list(tokenize.generate_tokens(io.StringIO(s).readline))                 # Python tokenize path
        print("iteration", i, "ok", flush=True)
print("completed without crash")
