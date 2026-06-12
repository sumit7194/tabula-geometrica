#!/bin/bash
# SpaceTime regression gate — curvature / NN project only.
# (echoes, ringdown, pbh moved to ../BlackHole; their gate is BlackHole/verify.sh)
set -u
cd "$(dirname "$0")"
FAIL=0

./curvature/verify.sh || FAIL=1

echo "--- curvature invariant + magnetic Kaluza artifacts (17/18)"
./curvature/.venv/bin/python - << 'PYEOF2' || FAIL=1
import json
k = json.loads(open("curvature/results/17_curvature.json").read())
assert k["K1_corr"] > 0.95 and k["G0_sphere_err"] < 0.01, k
m = json.loads(open("curvature/results/18_magnetic.json").read())
assert abs(m["M2_r"]) > 0.99, m["M2_r"]
print("PASS  curvature invariant + magnetic Kaluza artifacts")
PYEOF2

echo "========================================"
[ $FAIL -eq 0 ] && echo "SPACETIME GATE: ALL GREEN" || echo "SPACETIME GATE: FAILURES"
exit $FAIL
