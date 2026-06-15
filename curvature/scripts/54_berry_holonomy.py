"""Step 54 — OVERNIGHT Run 4 (quantum): does a net discover a HOLONOMY (geometric phase = area)?

Berry phase essence (web-verified): the geometric phase of a cyclic process = the flux of a curvature
through the enclosed surface (Stokes) — for spin-1/2, gamma = -1/2 * solid angle. Its defining
property is PATH-INDEPENDENCE: it depends only on the ENCLOSED AREA, not on the traversal, so RETRACED
("whisker") path segments add ZERO geometric phase (a dynamical, path-length quantity does not share
this). Can a net discover that the geometric phase is a holonomy with this invariance?

Toy (planar Berry-curvature, F=1 so gamma = signed enclosed AREA): loops are closed polygons; the net
predicts the geometric phase. We give it the natural Stokes structure (a sum of LOCAL edge
contributions — the discretized line integral), and test whether it discovers the holonomy:
  - learns the signed area, and
  - is INVARIANT to whiskers (back-and-forth spikes that add length but no area),
contrasted with a net trained on PERIMETER (a dynamical, path-length quantity) which is NOT invariant.

Pre-reg (2026-06-16):
  B1 learns the geometric phase: area-net test R^2 > 0.95.
  B2 holonomy/whisker invariance: adding whiskers changes the area-net prediction by < 0.1 (relative).
  B3 it's geometric not dynamical: the length-net's whisker change >> the area-net's (by > 5x) —
     the geometric phase ignores retraced paths, the dynamical one does not.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import torch
from curvlib import RESULTS, progress
from torch import nn

K, STEPS = 12, 6000


def _loop(rng, k=K):
    c = rng.uniform(-1, 1, 2)
    ang = np.sort(rng.uniform(0, 2 * np.pi, k))
    rad = rng.uniform(0.3, 1.2, k)
    v = c + rad[:, None] * np.stack([np.cos(ang), np.sin(ang)], 1)
    if rng.random() < 0.5:
        v = v[::-1].copy()                                   # both orientations -> signed area spans +/-
    return v.astype(np.float32)


def _edges(v):
    nxt = np.roll(v, -1, 0)
    return np.concatenate([v, nxt], 1)                       # (k, 4): [x_i,y_i,x_{i+1},y_{i+1}]


def _area(v):
    x, y = v[:, 0], v[:, 1]
    return float(0.5 * np.sum(x * np.roll(y, -1) - np.roll(x, -1) * y))


def _perimeter(v):
    return float(np.sum(np.linalg.norm(np.roll(v, -1, 0) - v, axis=1)))


def add_whisker(v, rng):
    """Insert a back-and-forth spike at a random vertex: adds length, ZERO area (retraced edge)."""
    i = rng.integers(0, len(v))
    p = v[i] + rng.uniform(-1, 1, 2).astype(np.float32)
    return np.insert(v, i + 1, [p, v[i]], axis=0)


def make_data(n, target, seed):
    rng = np.random.default_rng(seed)
    loops = [_loop(rng) for _ in range(n)]
    E = np.stack([_edges(v) for v in loops]).astype(np.float32)
    fn = _area if target == "area" else _perimeter
    Y = np.array([fn(v) for v in loops], np.float32)
    return torch.from_numpy(E), torch.from_numpy(Y), loops


class EdgeSum(nn.Module):
    """gamma = sum_edges f(edge): the discretized Stokes line integral (local-additive holonomy form)."""
    def __init__(self):
        super().__init__()
        self.f = nn.Sequential(nn.Linear(4, 128), nn.GELU(), nn.Linear(128, 128), nn.GELU(), nn.Linear(128, 1))

    def forward(self, E):
        return self.f(E).sum(1)[:, 0]


def train(target, seed=0):
    E, Y, _ = make_data(4000, target, seed)
    ntr = 3400
    m = EdgeSum(); opt = torch.optim.Adam(m.parameters(), lr=1e-3); rng = np.random.default_rng(0)
    for step in range(STEPS):
        idx = rng.integers(0, ntr, 128)
        loss = nn.functional.mse_loss(m(E[idx]), Y[idx])
        opt.zero_grad(); loss.backward(); opt.step()
        if step % 400 == 0:
            progress(f"54_{target}", step, STEPS, loss=float(loss.detach()))
    m.eval()
    with torch.no_grad():
        r2 = float(1 - ((m(E[ntr:]) - Y[ntr:]) ** 2).mean() / Y[ntr:].var())
    return m, r2


def whisker_change(m, target, seed=1):
    """How much does adding whiskers change the net's prediction? (true area unchanged; length grows.)"""
    rng = np.random.default_rng(seed)
    loops = [_loop(rng) for _ in range(300)]
    base = torch.from_numpy(np.stack([_edges(v) for v in loops]).astype(np.float32))
    with torch.no_grad():
        pb = m(base).numpy()
    deltas = []
    for v, p0 in zip(loops, pb):
        vw = v
        for _ in range(3):
            vw = add_whisker(vw, rng)
        ew = torch.from_numpy(_edges(vw)[None].astype(np.float32))
        with torch.no_grad():
            pw = float(m(ew)[0])
        deltas.append(abs(pw - p0))
    scale = float(np.mean(np.abs(pb)))
    return float(np.mean(deltas)) / (scale + 1e-9)


def main():
    m_area, r2_area = train("area")
    m_len, r2_len = train("perimeter")
    print(f"area-net  test R^2 {r2_area:.3f} | perimeter-net test R^2 {r2_len:.3f}")

    wc_area = whisker_change(m_area, "area")
    wc_len = whisker_change(m_len, "perimeter")
    print(f"whisker-induced relative change: area-net {wc_area:.3f} | length-net {wc_len:.3f}")

    b1 = bool(r2_area > 0.95)
    b2 = bool(wc_area < 0.1)
    b3 = bool(wc_len > 5 * wc_area)
    out = {"area_R2": r2_area, "perimeter_R2": r2_len, "whisker_change_area": wc_area,
           "whisker_change_length": wc_len, "B1_learns_geometric_phase": b1,
           "B2_holonomy_whisker_invariant": b2, "B3_geometric_not_dynamical": b3,
           "holonomy_discovered": bool(b1 and b2 and b3)}
    print(f"\nB1 learns geometric phase (area R^2 {r2_area:.3f}>0.95): {b1}")
    print(f"B2 holonomy/whisker invariance (area Δ {wc_area:.3f}<0.1): {b2}")
    print(f"B3 geometric not dynamical (length Δ {wc_len:.2f} > 5x area Δ {wc_area:.3f}): {b3}")
    print(f"\nHOLONOMY (geometric phase = area, path-independent) DISCOVERED: {out['holonomy_discovered']}")
    (RESULTS / "54_berry_holonomy.json").write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.bar([0, 1], [wc_area, wc_len], color=["seagreen", "crimson"])
    ax.set_xticks([0, 1]); ax.set_xticklabels([f"geometric phase\n(area, R²={r2_area:.2f})", f"dynamical\n(length, R²={r2_len:.2f})"])
    ax.set_ylabel("relative prediction change under whiskers")
    ax.set_title("Berry/holonomy: the geometric phase ignores retraced paths\n(area is whisker-invariant; length is not)")
    fig.tight_layout(); fig.savefig(RESULTS / "54_berry_holonomy.png", dpi=140)
    print("saved results/54_berry_holonomy.json + .png")


if __name__ == "__main__":
    main()
