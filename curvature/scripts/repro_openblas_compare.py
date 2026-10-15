"""OpenBLAS reproducibility rerun of §193/193b/193c/194/194b: compare the rerun's JSON outputs against the committed
originals (Accelerate, Python 3.12). Written and committed BEFORE the rerun produced any output; the reading rules are
in notes/openblas_repro_193_194_prereg.md and are applied mechanically here.

usage: python repro_openblas_compare.py RERUN_RESULTS_DIR [BASELINE_REV]
  The baseline is read with `git show BASELINE_REV:curvature/results/<file>` (default HEAD), never from the working tree.

Leaf classes (aligned by key / list index):
  bool                 -> CATEGORICAL (must match)
  str                  -> CATEGORICAL after replacing every numeric token by '#'; the numbers inside are DESCRIPTIVE
  int                  -> COUNT (must match for "REPRODUCED"; a shift alone gives "REPRODUCED WITH COUNT SHIFTS")
  float                -> DESCRIPTIVE (|log10 ratio| when same sign and nonzero, else |difference|)
  missing key / list length change -> STRUCTURAL
Ignored keys: timing (wall_seconds and any key containing 'seconds' or 'wall'). The d=6 resource guard (d6_dropped) is
reported separately and never counted as a difference.
"""
import json
import math
import re
import subprocess
import sys
from pathlib import Path

FILES = ["193_ts2_probe.json", "193_ts2_screen.json", "193b_rank6.json", "193c_strong.json",
         "193c_farfield_direction.json", "194_pilot.json", "194b_diagnose_g0.json"]
NUM = re.compile(r"[-+]?(?:\d+\.\d*|\.\d+|\d+)(?:[eE][-+]?\d+)?")
REPO = Path(__file__).resolve().parents[2]


def ignored(key):
    k = str(key).lower()
    return "seconds" in k or "wall" in k or k == "d6_dropped"


def fdist(a, b):
    if a == b:
        return 0.0
    if a != 0 and b != 0 and (a > 0) == (b > 0) and math.isfinite(a) and math.isfinite(b):
        return abs(math.log10(a / b))
    return abs(a - b)


def walk(a, b, path, out):
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b), key=str):
            if ignored(k):
                if k == "d6_dropped" and a.get(k) != b.get(k):
                    out["guard"].append((path + [k], a.get(k), b.get(k)))
                continue
            if k not in a or k not in b:
                out["structural"].append((path + [k], "missing in " + ("baseline" if k not in a else "rerun")))
            else:
                walk(a[k], b[k], path + [k], out)
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            out["structural"].append((path, f"list length {len(a)} -> {len(b)}"))
        for i, (x, y) in enumerate(zip(a, b)):
            walk(x, y, path + [i], out)
    elif isinstance(a, bool) or isinstance(b, bool):
        if a != b:
            out["categorical"].append((path, a, b))
    elif isinstance(a, int) and isinstance(b, int):
        if a != b:
            out["counts"].append((path, a, b))
    elif isinstance(a, (int, float)) and isinstance(b, (int, float)):
        out["floats"].append((path, float(a), float(b), fdist(float(a), float(b))))
    elif isinstance(a, str) and isinstance(b, str):
        if NUM.sub("#", a) != NUM.sub("#", b):
            out["categorical"].append((path, a, b))
        else:
            na, nb = NUM.findall(a), NUM.findall(b)
            for x, y in zip(na, nb):
                fx, fy = float(x), float(y)
                out["strnums"].append((path, fx, fy, fdist(fx, fy)))
    elif a is None and b is None:
        pass
    elif type(a) is not type(b):
        out["categorical"].append((path, a, b))
    elif a != b:
        out["categorical"].append((path, a, b))


def p(path):
    return "/".join(str(x) for x in path)


def main():
    rerun = Path(sys.argv[1])
    rev = sys.argv[2] if len(sys.argv) > 2 else "HEAD"
    report = {"baseline_rev": rev, "files": {}}
    overall = "REPRODUCED"
    rank = {"REPRODUCED": 0, "REPRODUCED WITH COUNT SHIFTS": 1, "NOT REPRODUCED": 2, "MISSING": 3}
    for f in FILES:
        rf = rerun / f
        if not rf.exists():
            report["files"][f] = {"reading": "MISSING"}
            overall = max(overall, "MISSING", key=rank.get)
            continue
        base = json.loads(subprocess.check_output(["git", "-C", str(REPO), "show", f"{rev}:curvature/results/{f}"]))
        new = json.loads(rf.read_text())
        out = {k: [] for k in ("categorical", "counts", "structural", "floats", "strnums", "guard")}
        walk(base, new, [], out)
        if out["categorical"] or out["structural"]:
            reading = "NOT REPRODUCED"
        elif out["counts"]:
            reading = "REPRODUCED WITH COUNT SHIFTS"
        else:
            reading = "REPRODUCED"
        overall = max(overall, reading, key=rank.get)
        dl = sorted(out["floats"] + out["strnums"], key=lambda t: -t[3])
        report["files"][f] = {
            "reading": reading,
            "categorical_diffs": [(p(a), str(x)[:200], str(y)[:200]) for a, x, y in out["categorical"]],
            "structural_diffs": [(p(a), m) for a, m in out["structural"]],
            "count_shifts": [(p(a), x, y) for a, x, y in out["counts"]],
            "resource_guard": [(p(a), x, y) for a, x, y in out["guard"]],
            "n_floats": len(dl),
            "float_max_dist": dl[0][3] if dl else None,
            "float_median_dist": dl[len(dl) // 2][3] if dl else None,
            "float_top10": [(p(a), x, y, d) for a, x, y, d in dl[:10]],
        }
        r = report["files"][f]
        print(f"{f:32s} {reading:28s} cat {len(r['categorical_diffs'])} struct {len(r['structural_diffs'])} "
              f"counts {len(r['count_shifts'])} | floats {r['n_floats']} max dist {r['float_max_dist']} "
              f"median {r['float_median_dist']}")
    report["OVERALL"] = overall
    print("OVERALL:", overall)
    (rerun / "repro_openblas_compare.json").write_text(json.dumps(report, indent=1, default=str))


if __name__ == "__main__":
    main()
