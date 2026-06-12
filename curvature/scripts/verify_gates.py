"""Regression gate: re-run every probe script against the SAVED models and
assert the pre-registered thresholds. Fast (no training) — this is the
"did anything rot?" check, runnable any time. Exit code 0 = all green."""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
R = ROOT / "results"
PY = str(ROOT / ".venv" / "bin" / "python")

# battery: (name, command, results json, {dotted.key: (op, threshold)})
BATTERIES = [
    ("Phase A (interval)", ["scripts/03_gates.py", "1"], "03_gates_k1.json",
     {"G1_isotonic_r2": (">", 0.95), "G2_alignment": (">", 0.95),
      "G2_sign_consistency": (">", 0.95)}),
    ("v0.1 (light cone)", ["scripts/04_gates_mixed.py", "1"], "04_gates_mixed_k1.json",
     {"future.isotonic_r2": (">", 0.95), "past.isotonic_r2": (">", 0.95),
      "right.isotonic_r2": (">", 0.95), "left.isotonic_r2": (">", 0.95)}),
    ("Phase B (well)", ["scripts/05_gates_well.py", "1"], "05_gates_well_k1.json",
     {"ratio_profile_correlation": (">", 0.9), "min_bin_isotonic_r2": (">", 0.95)}),
    ("Phase C (economy)", ["scripts/07_gates_economy.py", "charged"], "07_economy_charged.json",
     {"E1_force.charged": ("<", 1e-4), "E2_swap.charged": (">", 0.01),
      "E3_loo_decode_r": (">", 0.99)}),
    ("3+1 replication", ["scripts/08_gates_3p1.py", "1"], "08_gates_3p1_k1.json",
     {"isotonic_r2": (">", 0.95), "alignment": (">", 0.95)}),
    ("Phase E + curvature", ["scripts/17_curvature_invariant.py"], "17_curvature.json",
     {"G0_sphere_err": ("<", 0.01), "K1_corr": (">", 0.95)}),
]


def get(d, dotted):
    for k in dotted.split("."):
        d = d[k]
    return d


def main() -> int:
    failures = 0
    for name, cmd, jname, gates in BATTERIES:
        try:
            subprocess.run([PY] + cmd, cwd=ROOT, check=True,
                           capture_output=True, timeout=900)
            res = json.loads((R / jname).read_text())
            bad = []
            for key, (op, thr) in gates.items():
                v = float(get(res, key))
                ok = v > thr if op == ">" else v < thr
                if not ok:
                    bad.append(f"{key}={v:.4g} !{op} {thr}")
            if bad:
                failures += 1
                print(f"FAIL  {name}: " + "; ".join(bad))
            else:
                print(f"PASS  {name}")
        except Exception as e:
            failures += 1
            print(f"FAIL  {name}: {type(e).__name__}: {e}")
    print("=" * 40)
    print("ALL GREEN" if failures == 0 else f"{failures} BATTERY(IES) FAILED")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
