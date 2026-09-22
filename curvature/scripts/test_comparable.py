import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comparable import Value, Mismatch, check

BASE = dict(metric="A", basis="base", ntraj=40, nstep=3000, seed=1, readout="all", chi=0.075)
fails = 0

def known_fail(name, a, b, axis, expect_key):
    global fails
    try:
        a.ratio(b, axis=axis)
    except Mismatch as e:
        ok = expect_key in str(e)
        print(f"  {'OK  ' if ok else 'BAD '} {name:<22} raised, names {expect_key}: {ok}")
        fails += 0 if ok else 1
        return
    print(f"  BAD  {name:<22} did NOT raise -- the gate is blind to this axis")
    fails += 1

print("KNOWN-FAILS: the five real mismatches from 2026-09-22, each must raise and name its axis")
known_fail("1 basis",   Value(1.3e-15, "margin", **{**BASE, "basis": "base+dK"}),
                        Value(8.2e-15, "floor",  **BASE), ("eps",), "basis")
known_fail("2 ensemble",Value(1.0, "A+dK/floorA", **{**BASE, "metric": "A"}),
                        Value(1.0, "B+dK/floorB", **{**BASE, "metric": "B"}), ("eps",), "metric")
known_fail("3 runparam",Value(4.9e-10, "margin", **{**BASE, "ntraj": 90, "nstep": 9000}),
                        Value(8.2e-15, "floor",  **BASE), ("eps",), "ntraj")
known_fail("4 seed",    Value(6.0e-17, "floor0", **{**BASE, "seed": 0}),
                        Value(8.2e-15, "floor1", **BASE), ("eps",), "seed")
known_fail("5 readout", Value(6.0e-17, "min4",   **{**BASE, "readout": "min4"}),
                        Value(8.2e-15, "minall", **BASE), ("eps",), "readout")

print("\nMUST NOT RAISE: a legitimate comparison along the declared axis")
try:
    r = Value(4.9e-10, "m(.05)", **BASE).ratio(Value(8.2e-15, "floor", **BASE), axis=("eps",))
    print(f"  OK   same config, axis eps  -> {r.x:.4g}, within={r.within}")
except Mismatch as e:
    print(f"  BAD  legitimate comparison raised: {e}"); fails += 1

print("\nTRANSPORTABILITY: a within-config ratio is marked transportable")
w = Value(2.87e-3, "bareQ", **BASE).ratio(Value(3.66e-5, "dK", **{**BASE, "basis": "base+dK"}), axis=("basis",))
print(f"  {'OK  ' if w.within else 'BAD '} improvement ratio within={w.within} (78.4x class)")
fails += 0 if w.within else 1

print(f"\n{'PASS' if fails==0 else 'FAIL'}  comparable.py  ({fails} problem(s))")
sys.exit(1 if fails else 0)
