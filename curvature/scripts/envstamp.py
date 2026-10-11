"""Write a reproducibility stamp for the interpreter that runs this script: curvature/ENVIRONMENT/<name>.json plus
a pip freeze next to it.

The stamp records the Python version and executable, the platform and macOS version, the key package versions,
numpy's and scipy's BLAS/LAPACK backends, and the git commit (with a dirty flag). A cited result is only
replicable if the stack that produced it is written down (fleet policy, 2026-10-11).

    .venv/bin/python scripts/envstamp.py py312        # -> ENVIRONMENT/py312.json + py312_freeze.txt
"""

import contextlib
import io
import json
import platform
import subprocess
import sys
from importlib import metadata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PKGS = ("numpy", "scipy", "sympy", "mpmath", "torch", "scikit-learn", "matplotlib", "networkx")


def _backend(mod):
    """BLAS/LAPACK names as reported by the module's show_config (best effort, never raises)."""
    try:
        m = __import__(mod)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            m.show_config()
        txt = buf.getvalue().lower()
        return {k: ("accelerate" if "accelerate" in txt.split(k, 1)[-1][:200] else
                    "openblas" if "openblas" in txt.split(k, 1)[-1][:200] else "unknown") for k in ("blas", "lapack")}
    except Exception as e:                                   # a stamp must never crash the run it describes
        return {"error": repr(e)}


def main():
    name = sys.argv[1] if len(sys.argv) > 1 else f"py{sys.version_info.major}{sys.version_info.minor}"
    out = ROOT / "ENVIRONMENT"
    out.mkdir(exist_ok=True)
    git = lambda *a: subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    stamp = {
        "python": sys.version.split()[0], "executable": sys.executable,
        "platform": platform.platform(), "machine": platform.machine(), "macos": platform.mac_ver()[0],
        "packages": {p: (metadata.version(p) if _has(p) else None) for p in PKGS},
        "numpy_backend": _backend("numpy"), "scipy_backend": _backend("scipy"),
        "git_commit": git("rev-parse", "HEAD"), "git_dirty": bool(git("status", "--porcelain")),
    }
    (out / f"{name}.json").write_text(json.dumps(stamp, indent=1))
    freeze = subprocess.run([sys.executable, "-m", "pip", "freeze"], capture_output=True, text=True).stdout
    (out / f"{name}_freeze.txt").write_text(freeze)
    print(json.dumps(stamp, indent=1))


def _has(p):
    try:
        metadata.version(p)
        return True
    except metadata.PackageNotFoundError:
        return False


if __name__ == "__main__":
    main()
