"""Torch-free copy of curvlib.progress (the dashboard heartbeat), so §193 runs on .venv314ob, which has no torch.

Copied verbatim from curvlib.py on 2026-10-15 by The Bridge (amendment 1 of notes/openblas_repro_193_194_prereg.md).
Root cause: 6aca281 removed torch from 193's module-level imports, but three lazy `from curvlib import progress` lines
inside production(), rank6() and rank6_strong() still import curvlib, and curvlib imports torch. So those modes could
not start on the required OpenBLAS venv. This writes a progress JSON for the dashboard only; no numerical effect.
"""
from pathlib import Path

RESULTS = Path(__file__).resolve().parent.parent / "results"
PROGRESS = RESULTS / "progress"


def progress(run: str, step: int, total: int, **metrics) -> None:
    """Heartbeat for the repo dashboard (dashboard.html at repo root).

    Each run owns its own file (no cross-process clobbering); an index file
    lists run names so the static dashboard can discover them. Cheap enough to
    call every few hundred steps.
    """
    import json
    import time

    PROGRESS.mkdir(parents=True, exist_ok=True)
    f = PROGRESS / f"{run}.json"
    hist = []
    if f.exists():
        try:
            hist = json.loads(f.read_text()).get("history", [])
        except json.JSONDecodeError:
            pass
    loss = metrics.get("loss")
    if loss is not None:
        hist = (hist + [[step, float(loss)]])[-200:]
    tmp = f.with_suffix(".tmp")
    tmp.write_text(
        json.dumps(
            {"run": run, "step": int(step), "total": int(total),
             "metrics": {k: float(v) for k, v in metrics.items()},
             "history": hist, "updated": time.time()}
        )
    )
    tmp.replace(f)
    idx = PROGRESS / "index.json"
    try:
        names = json.loads(idx.read_text()) if idx.exists() else []
    except json.JSONDecodeError:
        names = []
    if run not in names:
        names.append(run)
        idx.write_text(json.dumps(names))
