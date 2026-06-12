"""Shared library for the curvature-discovery experiment (Phase A: flat spacetime).

Physics conventions
-------------------
1+1 dimensional flat (Minkowski) spacetime, units c=1. An "event" here is a
displacement four-vector from a shared origin, restricted to the FUTURE TIMELIKE
region (t > |x|): this region is closed under boosts, and its boost-orbits are
indexed by exactly ONE number, the interval s^2 = t^2 - x^2 (equivalently the
proper time tau = sqrt(s^2)). That gives the clean prediction the whole
experiment rests on: a bottleneck of width 1 should suffice, and the learned
scalar must be a monotone function of s^2.

The symmetry lives ONLY in the data: a positive pair is the same event seen by
two independently boosted observers. The network receives raw (t, x) coordinates
and nothing else -- no engineered features. The minus sign must be earned.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import torch
from torch import nn

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"
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


class Siamese(nn.Module):
    """Twin encoder + strict distance head (see README "Decisions")."""

    def __init__(self, k: int, in_dim: int = 2, hidden: int = 64):
        super().__init__()
        self.enc = nn.Sequential(
            nn.Linear(in_dim, hidden),
            nn.Tanh(),
            nn.Linear(hidden, hidden),
            nn.Tanh(),
            nn.Linear(hidden, k),
        )
        self.alpha = nn.Parameter(torch.tensor(1.0))
        self.beta = nn.Parameter(torch.tensor(1.0))

    def forward(self, a: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
        d = torch.norm(self.enc(a) - self.enc(b), dim=-1)
        return self.alpha - nn.functional.softplus(self.beta) * d


def bilerp(field: torch.Tensor, q: torch.Tensor) -> torch.Tensor:
    """Bilinear interpolation of a (B, C, H, W) field at normalized coords
    q (B, 2) in [-1, 1], align_corners semantics. Pure tensor ops — exists
    because grid_sampler_2d_backward is unimplemented on MPS (pytorch#141287;
    same issue the 3+1 trilerp solved). Used on MPS only: CPU keeps
    grid_sample so existing checkpoints stay bitwise-reproducible."""
    B, C, Hh, Ww = field.shape
    px = (q[:, 0].clamp(-1, 1) + 1) * 0.5 * (Ww - 1)
    py = (q[:, 1].clamp(-1, 1) + 1) * 0.5 * (Hh - 1)
    x0 = px.floor().long().clamp(0, Ww - 2)
    y0 = py.floor().long().clamp(0, Hh - 2)
    fx = (px - x0.float()).unsqueeze(1)
    fy = (py - y0.float()).unsqueeze(1)
    b = torch.arange(B, device=field.device)
    f00 = field[b, :, y0, x0]
    f01 = field[b, :, y0, x0 + 1]
    f10 = field[b, :, y0 + 1, x0]
    f11 = field[b, :, y0 + 1, x0 + 1]
    return ((1 - fx) * (1 - fy) * f00 + fx * (1 - fy) * f01
            + (1 - fx) * fy * f10 + fx * fy * f11)


def save_ckpt(path, model, opt, step: int, np_rng) -> None:
    """Checkpoint with FULL resume state: weights, optimizer, step, and the
    RNG states (numpy generator + torch) so resumes are bit-exact — interrupted
    runs stop contaminating results. Atomic write (tmp+rename): a power cut
    mid-save cannot corrupt the checkpoint."""
    tmp = path.with_suffix(".tmp")
    torch.save({"model": model.state_dict(), "opt": opt.state_dict(),
                "step": int(step), "np_rng": np_rng.bit_generator.state,
                "torch_rng": torch.get_rng_state()}, tmp)
    tmp.replace(path)


def load_ckpt(path, model, opt, fallback_seed: int = 0):
    """Restore a checkpoint. Returns (step, np_rng, bit_exact). Legacy
    checkpoints (no RNG state) fall back to step-seeded randomness —
    functional but NOT bit-exact; flagged via the third return."""
    st = torch.load(path, weights_only=False, map_location="cpu")
    model.load_state_dict(st["model"])
    opt.load_state_dict(st["opt"])
    step = st["step"]
    if "np_rng" in st:
        rng = np.random.default_rng()
        rng.bit_generator.state = st["np_rng"]
        torch.set_rng_state(st["torch_rng"])
        return step, rng, True
    return step, np.random.default_rng(fallback_seed + step), False


def load_model(stem: str) -> Siamese:
    """Rebuild a saved model from its sidecar meta json (results/{stem}.json)."""
    import json

    meta = json.loads((RESULTS / f"{stem}.json").read_text())
    m = Siamese(meta["k"], meta.get("in_dim", 2), meta.get("hidden", 64))
    m.load_state_dict(torch.load(RESULTS / f"{stem}.pt", weights_only=True))
    m.eval()
    return m

TAU_RANGE = (0.5, 3.0)  # proper times sampled
RAPIDITY_MAX = 1.5  # observer boosts up to v ~ 0.905c
NOISE_STD = 0.01  # measurement noise per coordinate (absolute units)
NEG_MARGIN = 0.15  # |tau1 - tau2| floor for negatives (see sample_pairs)


def boost(tau: np.ndarray, eta: np.ndarray) -> np.ndarray:
    """Observation of a rest-frame event (tau, 0) by an observer at rapidity eta."""
    return np.stack([tau * np.cosh(eta), tau * np.sinh(eta)], axis=-1)


def interval2(obs: np.ndarray) -> np.ndarray:
    return obs[..., 0] ** 2 - obs[..., 1] ** 2


def sample_pairs(
    n: int, rng: np.random.Generator
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Balanced same/different observation pairs: (a, b, label), label 1 = same.

    Negatives draw tau from the same marginal and use independent presentation
    boosts, so the classes differ systematically ONLY in the invariant. Two
    events closer than NEG_MARGIN in tau are excluded from the negative class:
    with measurement noise they are not "different" in any learnable sense, and
    keeping them would just inject label noise.
    """
    tau1 = rng.uniform(*TAU_RANGE, size=n)
    tau2 = rng.uniform(*TAU_RANGE, size=n)
    bad = np.abs(tau2 - tau1) < NEG_MARGIN
    while bad.any():
        tau2[bad] = rng.uniform(*TAU_RANGE, size=int(bad.sum()))
        bad = np.abs(tau2 - tau1) < NEG_MARGIN

    label = rng.integers(0, 2, size=n)
    tau_b = np.where(label == 1, tau1, tau2)

    eta_a = rng.uniform(-RAPIDITY_MAX, RAPIDITY_MAX, size=n)
    eta_b = rng.uniform(-RAPIDITY_MAX, RAPIDITY_MAX, size=n)
    a = boost(tau1, eta_a) + rng.normal(0, NOISE_STD, size=(n, 2))
    b = boost(tau_b, eta_b) + rng.normal(0, NOISE_STD, size=(n, 2))
    return a.astype(np.float32), b.astype(np.float32), label.astype(np.float32)


def sample_observations(n: int, rng: np.random.Generator) -> np.ndarray:
    """On-distribution single observations, for probing the trained encoder."""
    tau = rng.uniform(*TAU_RANGE, size=n)
    eta = rng.uniform(-RAPIDITY_MAX, RAPIDITY_MAX, size=n)
    return boost(tau, eta).astype(np.float32)


def in_region(t: np.ndarray, x: np.ndarray) -> np.ndarray:
    """Mask for the sampled region (probes must not grade extrapolation)."""
    s2 = t**2 - x**2
    with np.errstate(divide="ignore", invalid="ignore"):
        eta = np.arctanh(np.clip(np.abs(x) / np.where(t > 0, t, np.inf), 0, 1 - 1e-9))
    tau = np.sqrt(np.clip(s2, 0, None))
    return (
        (t > 0)
        & (s2 > 0)
        & (tau >= TAU_RANGE[0])
        & (tau <= TAU_RANGE[1])
        & (eta <= RAPIDITY_MAX)
    )


# ------------------------------------------------- v0.1: all four causal sectors
# Sectors: 0 = future timelike, 1 = past timelike, 2 = right spacelike,
# 3 = left spacelike. Each is closed under boosts; orbits within a sector are
# indexed by |s²| alone, so the full orbit space is four disjoint half-lines —
# still ONE continuous dimension, but with a 2-bit discrete label on top.
SECTOR_NAMES = ("future", "past", "right", "left")


def _sector_vec(tau: np.ndarray, eta: np.ndarray, sector: np.ndarray) -> np.ndarray:
    c, s = np.cosh(eta), np.sinh(eta)
    timelike = sector < 2
    sign = np.where(sector % 2 == 0, 1.0, -1.0)
    t = sign * tau * np.where(timelike, c, s)
    x = sign * tau * np.where(timelike, s, c)
    return np.stack([t, x], axis=-1)


def sector_of(obs: np.ndarray) -> np.ndarray:
    t, x = obs[..., 0], obs[..., 1]
    timelike = np.abs(t) > np.abs(x)
    lead = np.where(timelike, t, x)
    return np.where(timelike, 0, 2) + (lead < 0).astype(int)


def sample_pairs_mixed(
    n: int, rng: np.random.Generator
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Same/different pairs over all four sectors. Cross-sector pairs are always
    legitimate negatives (no boost connects sectors); same-sector negatives keep
    the tau margin for the same label-noise reason as sample_pairs."""
    tau1 = rng.uniform(*TAU_RANGE, size=n)
    sec1 = rng.integers(0, 4, size=n)
    tau2 = rng.uniform(*TAU_RANGE, size=n)
    sec2 = rng.integers(0, 4, size=n)
    bad = (sec2 == sec1) & (np.abs(tau2 - tau1) < NEG_MARGIN)
    while bad.any():
        tau2[bad] = rng.uniform(*TAU_RANGE, size=int(bad.sum()))
        bad = (sec2 == sec1) & (np.abs(tau2 - tau1) < NEG_MARGIN)

    label = rng.integers(0, 2, size=n)
    tau_b = np.where(label == 1, tau1, tau2)
    sec_b = np.where(label == 1, sec1, sec2)

    eta_a = rng.uniform(-RAPIDITY_MAX, RAPIDITY_MAX, size=n)
    eta_b = rng.uniform(-RAPIDITY_MAX, RAPIDITY_MAX, size=n)
    a = _sector_vec(tau1, eta_a, sec1) + rng.normal(0, NOISE_STD, size=(n, 2))
    b = _sector_vec(tau_b, eta_b, sec_b) + rng.normal(0, NOISE_STD, size=(n, 2))
    return a.astype(np.float32), b.astype(np.float32), label.astype(np.float32)


def sample_observations_mixed(
    n: int, rng: np.random.Generator
) -> tuple[np.ndarray, np.ndarray]:
    tau = rng.uniform(*TAU_RANGE, size=n)
    eta = rng.uniform(-RAPIDITY_MAX, RAPIDITY_MAX, size=n)
    sec = rng.integers(0, 4, size=n)
    return _sector_vec(tau, eta, sec).astype(np.float32), sec


def in_region_mixed(t: np.ndarray, x: np.ndarray) -> np.ndarray:
    at, ax = np.abs(t), np.abs(x)
    lo, hi = np.minimum(at, ax), np.maximum(at, ax)
    with np.errstate(divide="ignore", invalid="ignore"):
        eta = np.arctanh(np.clip(lo / np.where(hi > 0, hi, np.inf), 0, 1 - 1e-9))
    tau = np.sqrt(np.abs(t**2 - x**2))
    return (tau >= TAU_RANGE[0]) & (tau <= TAU_RANGE[1]) & (eta <= RAPIDITY_MAX)


# ------------------------------------- Phase B: a static gravity well (1+1)
# Metric ds² = A(x)dt² − B(x)dx² with a weak Gaussian potential well φ(x):
# A = 1+2φ, B = 1−2φ (the standard weak-field form). Observers at anchor x
# report COORDINATE components of small displacements — that choice is what
# makes geometry visible: orthonormal-frame components would be Minkowski
# everywhere (the equivalence principle) and there would be nothing to find.
WELL_DEPTH = 0.15  # |φ| at the bottom; A ranges [0.7, 1] — weak but not subtle
WELL_WIDTH = 1.0
X_RANGE = (-3.0, 3.0)


def phi(x: np.ndarray) -> np.ndarray:
    return -WELL_DEPTH * np.exp(-(x**2) / (2 * WELL_WIDTH**2))


def metric_A(x: np.ndarray) -> np.ndarray:
    return 1 + 2 * phi(x)


def metric_B(x: np.ndarray) -> np.ndarray:
    return 1 - 2 * phi(x)


def well_invariant(xp: np.ndarray, d: np.ndarray) -> np.ndarray:
    return metric_A(xp) * d[..., 0] ** 2 - metric_B(xp) * d[..., 1] ** 2


def _well_obs(
    xp: np.ndarray, tau: np.ndarray, eta: np.ndarray, rng: np.random.Generator
) -> np.ndarray:
    """Coordinate components of a future-timelike displacement of proper time tau,
    seen by a local observer at rapidity eta, at anchor xp."""
    dt = tau * np.cosh(eta) / np.sqrt(metric_A(xp))
    dx = tau * np.sinh(eta) / np.sqrt(metric_B(xp))
    d = np.stack([dt, dx], axis=-1)
    return d + rng.normal(0, NOISE_STD, size=d.shape)


def sample_pairs_well(
    n: int, rng: np.random.Generator, with_position: bool = True
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Same-event pairs at a SHARED anchor inside the well. Sharing the anchor
    means position is never a label cue — only context the net may use to adapt
    its invariant. with_position=False trains the control that must fail."""
    xp = rng.uniform(*X_RANGE, size=n)
    tau1 = rng.uniform(*TAU_RANGE, size=n)
    tau2 = rng.uniform(*TAU_RANGE, size=n)
    bad = np.abs(tau2 - tau1) < NEG_MARGIN
    while bad.any():
        tau2[bad] = rng.uniform(*TAU_RANGE, size=int(bad.sum()))
        bad = np.abs(tau2 - tau1) < NEG_MARGIN

    label = rng.integers(0, 2, size=n)
    tau_b = np.where(label == 1, tau1, tau2)

    eta_a = rng.uniform(-RAPIDITY_MAX, RAPIDITY_MAX, size=n)
    eta_b = rng.uniform(-RAPIDITY_MAX, RAPIDITY_MAX, size=n)
    a2 = _well_obs(xp, tau1, eta_a, rng)
    b2 = _well_obs(xp, tau_b, eta_b, rng)
    if with_position:
        a2 = np.concatenate([xp[:, None], a2], axis=1)
        b2 = np.concatenate([xp[:, None], b2], axis=1)
    return a2.astype(np.float32), b2.astype(np.float32), label.astype(np.float32)


def sample_observations_well(
    n: int, rng: np.random.Generator
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Observations (xp, dt, dx) plus the hidden (tau, eta) for probing."""
    xp = rng.uniform(*X_RANGE, size=n)
    tau = rng.uniform(*TAU_RANGE, size=n)
    eta = rng.uniform(-RAPIDITY_MAX, RAPIDITY_MAX, size=n)
    d = _well_obs(xp, tau, eta, rng)
    obs = np.concatenate([xp[:, None], d], axis=1).astype(np.float32)
    return obs, tau, eta


# ----------------------------------------------- 3+1 flat replication (Phase A')
# The orbit of a rest event (tau,0,0,0) under the full proper orthochronous
# Lorentz group (boosts AND rotations) is the future mass shell, parameterized
# in closed form as tau*(cosh eta, sinh eta * nhat) — no matrices needed.
def _unit_vectors(n: int, rng: np.random.Generator) -> np.ndarray:
    v = rng.normal(size=(n, 3))
    return v / np.linalg.norm(v, axis=1, keepdims=True)


def _shell_vec(tau: np.ndarray, eta: np.ndarray, nhat: np.ndarray) -> np.ndarray:
    t = tau * np.cosh(eta)
    xyz = (tau * np.sinh(eta))[:, None] * nhat
    return np.concatenate([t[:, None], xyz], axis=1)


def interval2_3p1(obs: np.ndarray) -> np.ndarray:
    return obs[..., 0] ** 2 - np.sum(obs[..., 1:] ** 2, axis=-1)


def sample_pairs_3p1(
    n: int, rng: np.random.Generator
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Same/different pairs of future-timelike events in full 3+1."""
    tau1 = rng.uniform(*TAU_RANGE, size=n)
    tau2 = rng.uniform(*TAU_RANGE, size=n)
    bad = np.abs(tau2 - tau1) < NEG_MARGIN
    while bad.any():
        tau2[bad] = rng.uniform(*TAU_RANGE, size=int(bad.sum()))
        bad = np.abs(tau2 - tau1) < NEG_MARGIN
    label = rng.integers(0, 2, size=n)
    tau_b = np.where(label == 1, tau1, tau2)
    a = _shell_vec(
        tau1, rng.uniform(-RAPIDITY_MAX, RAPIDITY_MAX, n), _unit_vectors(n, rng)
    ) + rng.normal(0, NOISE_STD, size=(n, 4))
    b = _shell_vec(
        tau_b, rng.uniform(-RAPIDITY_MAX, RAPIDITY_MAX, n), _unit_vectors(n, rng)
    ) + rng.normal(0, NOISE_STD, size=(n, 4))
    return a.astype(np.float32), b.astype(np.float32), label.astype(np.float32)


def sample_observations_3p1(n: int, rng: np.random.Generator) -> np.ndarray:
    tau = rng.uniform(*TAU_RANGE, size=n)
    eta = rng.uniform(-RAPIDITY_MAX, RAPIDITY_MAX, size=n)
    return _shell_vec(tau, eta, _unit_vectors(n, rng)).astype(np.float32)


# --------------- metric-component counting: a 2+1 static ANISOTROPIC well
# ds² = A dt² − (B dx² + 2D dxdy + C dy²). Three independent smooth fields
# (φ, b, d̃) make the local form, up to per-anchor reshaping (scale), carry
# exactly THREE numbers per point: (A:B:C:D). The experiment asks a code-width
# sweep to discover that count.
XY_RANGE = (-2.5, 2.5)


def _bump(x, y, cx, cy):
    return np.exp(-(((x - cx) ** 2) + (y - cy) ** 2) / 2.0)


def fields_2p1(x, y):
    ph = -0.15 * _bump(x, y, 0.0, 0.0)
    b = _bump(x, y, 1.0, 0.5)
    dt_ = _bump(x, y, -1.0, -0.5)
    A = 1 + 2 * ph
    B = 1 - 2 * ph + 0.2 * b
    C = 1 - 2 * ph - 0.2 * b
    D = 0.15 * dt_
    return A, B, C, D


def true_G(x, y):
    """Local metric as a (..., 3, 3) symmetric matrix, signature (+,−,−)."""
    A, B, C, D = fields_2p1(x, y)
    G = np.zeros(np.shape(A) + (3, 3))
    G[..., 0, 0] = A
    G[..., 1, 1] = -B
    G[..., 2, 2] = -C
    G[..., 1, 2] = G[..., 2, 1] = -D
    return G


def _spatial_inv_sqrt(B, C, D):
    """S^{-1/2} for the SPD spatial block S = [[B, D], [D, C]], closed form."""
    det = B * C - D**2
    tr = B + C
    s = np.sqrt(det)
    t = np.sqrt(tr + 2 * s)
    # S^{1/2} = (S + s·I)/t  ->  S^{-1/2} = inverse of that 2x2
    a11, a12, a22 = (B + s) / t, D / t, (C + s) / t
    idet = 1.0 / (a11 * a22 - a12**2)
    return idet * a22, -idet * a12, idet * a11  # entries of S^{-1/2}


def _well2p1_obs(xp, yp, tau, eta, theta, rng):
    """Coordinate components of a future-timelike displacement (proper time
    tau) seen by a local observer at rapidity eta, direction theta."""
    A, B, C, D = fields_2p1(xp, yp)
    dt = tau * np.cosh(eta) / np.sqrt(A)
    fx = tau * np.sinh(eta) * np.cos(theta)
    fy = tau * np.sinh(eta) * np.sin(theta)
    i11, i12, i22 = _spatial_inv_sqrt(B, C, D)
    dx = i11 * fx + i12 * fy
    dy = i12 * fx + i22 * fy
    d = np.stack([dt, dx, dy], axis=-1)
    return d + rng.normal(0, NOISE_STD, size=d.shape)


def well2p1_invariant(p, d):
    A, B, C, D = fields_2p1(p[..., 0], p[..., 1])
    return (
        A * d[..., 0] ** 2
        - B * d[..., 1] ** 2
        - C * d[..., 2] ** 2
        - 2 * D * d[..., 1] * d[..., 2]
    )


def sample_pairs_well2p1(
    n: int, rng: np.random.Generator
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Same-event pairs at a shared 2-d anchor; observations are (x, y, dt,
    dx, dy). Same margin logic as the 1+1 well."""
    xp = rng.uniform(*XY_RANGE, size=n)
    yp = rng.uniform(*XY_RANGE, size=n)
    tau1 = rng.uniform(*TAU_RANGE, size=n)
    tau2 = rng.uniform(*TAU_RANGE, size=n)
    bad = np.abs(tau2 - tau1) < NEG_MARGIN
    while bad.any():
        tau2[bad] = rng.uniform(*TAU_RANGE, size=int(bad.sum()))
        bad = np.abs(tau2 - tau1) < NEG_MARGIN
    label = rng.integers(0, 2, size=n)
    tau_b = np.where(label == 1, tau1, tau2)

    def obs(tau):
        return _well2p1_obs(
            xp,
            yp,
            tau,
            rng.uniform(-RAPIDITY_MAX, RAPIDITY_MAX, n),
            rng.uniform(0, 2 * np.pi, n),
            rng,
        )

    pos = np.stack([xp, yp], axis=1)
    a = np.concatenate([pos, obs(tau1)], axis=1)
    b = np.concatenate([pos, obs(tau_b)], axis=1)
    return a.astype(np.float32), b.astype(np.float32), label.astype(np.float32)


def sample_observations_well2p1(
    n: int, rng: np.random.Generator
) -> tuple[np.ndarray, np.ndarray]:
    xp = rng.uniform(*XY_RANGE, size=n)
    yp = rng.uniform(*XY_RANGE, size=n)
    tau = rng.uniform(*TAU_RANGE, size=n)
    d = _well2p1_obs(
        xp, yp, tau,
        rng.uniform(-RAPIDITY_MAX, RAPIDITY_MAX, n),
        rng.uniform(0, 2 * np.pi, n),
        rng,
    )
    obs = np.concatenate([np.stack([xp, yp], axis=1), d], axis=1).astype(np.float32)
    return obs, tau


# --------------- in-context form counting: random forms, no position at all
# Counting a field's per-point dof by bottlenecking POSITION fails (the address
# is always a sufficient code — measured in step 11). Here the form is drawn
# fresh per episode, decoupled from any base manifold: the only route to the
# query is a set-encoded code over k context same-event pairs, so the bottleneck
# must carry the FORM itself. Family: A ~ U[0.7,1.3]; spatial SPD block from
# eigenvalues U[0.7,1.3] and rotation U[0,π) → 4 components, 3 dof up to scale.
def sample_forms(n: int, rng: np.random.Generator):
    A = rng.uniform(0.7, 1.3, n)
    l1 = rng.uniform(0.7, 1.3, n)
    l2 = rng.uniform(0.7, 1.3, n)
    psi = rng.uniform(0, np.pi, n)
    c, s = np.cos(psi), np.sin(psi)
    B = c**2 * l1 + s**2 * l2
    C = s**2 * l1 + c**2 * l2
    D = c * s * (l1 - l2)
    return A, B, C, D


def _form_obs(A, B, C, D, tau, eta, theta, rng):
    """Coordinate components of a future-timelike displacement under the form
    diag-time A / spatial block (B, D; D, C). Shapes broadcast."""
    dt = tau * np.cosh(eta) / np.sqrt(A)
    fx = tau * np.sinh(eta) * np.cos(theta)
    fy = tau * np.sinh(eta) * np.sin(theta)
    i11, i12, i22 = _spatial_inv_sqrt(B, C, D)
    d = np.stack([dt, i11 * fx + i12 * fy, i12 * fx + i22 * fy], axis=-1)
    return d + rng.normal(0, NOISE_STD, size=d.shape)


def sample_episodes(
    n_ep: int, k_ctx: int, rng: np.random.Generator
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Episodes: (ctx, query_a, query_b, label). ctx[(e, i)] is a same-event
    pair under episode e's form, concatenated to R^6 — the only information
    about the geometry the network ever gets."""
    A, B, C, D = sample_forms(n_ep, rng)

    def obs(tau, shape):
        eta = rng.uniform(-RAPIDITY_MAX, RAPIDITY_MAX, shape)
        theta = rng.uniform(0, 2 * np.pi, shape)
        return _form_obs(
            A[:, None] if len(shape) > 1 else A,
            B[:, None] if len(shape) > 1 else B,
            C[:, None] if len(shape) > 1 else C,
            D[:, None] if len(shape) > 1 else D,
            tau, eta, theta, rng,
        )

    tau_ctx = rng.uniform(*TAU_RANGE, (n_ep, k_ctx))
    ctx = np.concatenate(
        [obs(tau_ctx, (n_ep, k_ctx)), obs(tau_ctx, (n_ep, k_ctx))], axis=-1
    )

    tau1 = rng.uniform(*TAU_RANGE, n_ep)
    tau2 = rng.uniform(*TAU_RANGE, n_ep)
    bad = np.abs(tau2 - tau1) < NEG_MARGIN
    while bad.any():
        tau2[bad] = rng.uniform(*TAU_RANGE, int(bad.sum()))
        bad = np.abs(tau2 - tau1) < NEG_MARGIN
    label = rng.integers(0, 2, n_ep)
    tau_b = np.where(label == 1, tau1, tau2)
    qa = obs(tau1, (n_ep,))
    qb = obs(tau_b, (n_ep,))
    return (
        ctx.astype(np.float32),
        qa.astype(np.float32),
        qb.astype(np.float32),
        label.astype(np.float32),
    )


# --------------- D-3: 2-d charged dynamics with a MAGNETIC field (v × B)
B_AMP = 0.6
B_CENTER = (0.8, -0.5)


def b_field(x, y):
    return B_AMP * np.exp(-(((x - B_CENTER[0]) ** 2) + (y - B_CENTER[1]) ** 2) / 2.0)


def accel_2d(x, y, vx, vy, qm):
    """a = −∇φ + (q/m)(v × B ẑ): gravity well + out-of-plane magnetic bump."""
    # phi = -WELL_DEPTH * exp(-r^2/2w^2)  =>  a_grav = -grad(phi) (attractive)
    e = np.exp(-(x**2 + y**2) / (2 * WELL_WIDTH**2))
    ax_g = -WELL_DEPTH * x * e / WELL_WIDTH**2
    ay_g = -WELL_DEPTH * y * e / WELL_WIDTH**2
    B = b_field(x, y)
    return ax_g + qm * vy * B, ay_g - qm * vx * B


def integrate_2d(x0, y0, vx0, vy0, qm, dt=0.01):
    n_steps = int(round(TRAJ_TIMES[-1] / dt))
    grab = {int(round(t / dt)): i for i, t in enumerate(TRAJ_TIMES)}
    x, y, vx, vy = (a.astype(float).copy() for a in (x0, y0, vx0, vy0))
    out = np.empty((len(x0), len(TRAJ_TIMES), 2))
    for step in range(1, n_steps + 1):
        def rk(xx, yy, ux, uy):
            ax, ay = accel_2d(xx, yy, ux, uy, qm)
            return ux, uy, ax, ay

        k1 = rk(x, y, vx, vy)
        k2 = rk(x + 0.5 * dt * k1[0], y + 0.5 * dt * k1[1],
                vx + 0.5 * dt * k1[2], vy + 0.5 * dt * k1[3])
        k3 = rk(x + 0.5 * dt * k2[0], y + 0.5 * dt * k2[1],
                vx + 0.5 * dt * k2[2], vy + 0.5 * dt * k2[3])
        k4 = rk(x + dt * k3[0], y + dt * k3[1], vx + dt * k3[2], vy + dt * k3[3])
        x = x + dt / 6 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0])
        y = y + dt / 6 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1])
        vx = vx + dt / 6 * (k1[2] + 2 * k2[2] + 2 * k3[2] + k4[2])
        vy = vy + dt / 6 * (k1[3] + 2 * k2[3] + 2 * k3[3] + k4[3])
        if step in grab:
            out[:, grab[step], 0] = x
            out[:, grab[step], 1] = y
    return out


def make_magnetic_dataset(seed: int = 0, n_bodies: int = 40, per_body: int = 600):
    """Charged mix in the magnetic world; same split conventions as Phase C."""
    rng = np.random.default_rng(seed)
    qm_body = np.zeros(n_bodies)
    ch = rng.permutation(n_bodies)[: n_bodies // 2]
    qm_body[ch] = rng.choice([-1.0, 1.0], len(ch)) * rng.uniform(0.3, 1.0, len(ch))
    held = np.arange(n_bodies - 8, n_bodies)
    rows = []
    for i in range(n_bodies):
        x0 = rng.uniform(*X_RANGE, per_body)
        y0 = rng.uniform(*X_RANGE, per_body)
        vx0 = rng.uniform(-V_MAX, V_MAX, per_body)
        vy0 = rng.uniform(-V_MAX, V_MAX, per_body)
        tg = integrate_2d(x0, y0, vx0, vy0, np.full(per_body, qm_body[i]))
        rows.append((np.full(per_body, i), np.stack([x0, y0, vx0, vy0], 1), tg.reshape(per_body, -1)))
    body = np.concatenate([r[0] for r in rows]).astype(np.int64)
    X = np.concatenate([r[1] for r in rows]).astype(np.float32)
    Y = np.concatenate([r[2] for r in rows]).astype(np.float32)
    is_held = np.isin(body, held)
    n_seen = int((~is_held).sum())
    perm = rng.permutation(n_seen)
    idx = np.where(~is_held)[0][perm]
    n_te = n_seen // 6
    return {"qm_body": qm_body, "held_bodies": held,
            "train": (body[idx[n_te:]], X[idx[n_te:]], Y[idx[n_te:]]),
            "test": (body[idx[:n_te]], X[idx[:n_te]], Y[idx[:n_te]]),
            "held": (body[is_held], X[is_held], Y[is_held])}


# ---------------------- Phase C: dynamics — the geometry-vs-force economy race
# Slow-motion regime (|v| ≤ 0.3): the regime where curved-geometry and
# force-in-flat-space were historically indistinguishable for a single body —
# which is exactly the ambiguity the experiment is about. The Newtonian-limit
# generator is validated against the FULL relativistic geodesics of the Phase B
# metric (geodesic_check), so "geometry" here is the real thing, not a stand-in.
# A second, non-gravitational field (an electric bump, displaced off-center so
# its profile can't be confused with the well's) gives charged bodies a
# composition-DEPENDENT acceleration — the foil that gravity's universality is
# measured against.
E_AMP = 0.3
E_CENTER = 0.8
E_WIDTH = 1.0

TRAJ_TIMES = (1.0, 2.0, 3.0)  # prediction targets
V_MAX = 0.3


def phi_prime(x: np.ndarray) -> np.ndarray:
    return WELL_DEPTH * x / WELL_WIDTH**2 * np.exp(-(x**2) / (2 * WELL_WIDTH**2))


def e_field(x: np.ndarray) -> np.ndarray:
    return E_AMP * np.exp(-((x - E_CENTER) ** 2) / (2 * E_WIDTH**2))


def accel(x: np.ndarray, qm: np.ndarray) -> np.ndarray:
    """Total acceleration: universal gravity −φ' plus composition-dependent qE/m."""
    return -phi_prime(x) + qm * e_field(x)


def integrate_trajectories(
    x0: np.ndarray, v0: np.ndarray, qm: np.ndarray, dt: float = 0.01
) -> np.ndarray:
    """Vectorized RK4; returns positions at TRAJ_TIMES, shape (n, len(TRAJ_TIMES))."""
    n_steps = int(round(TRAJ_TIMES[-1] / dt))
    grab = {int(round(t / dt)): i for i, t in enumerate(TRAJ_TIMES)}
    x, v = x0.astype(float).copy(), v0.astype(float).copy()
    out = np.empty((len(x0), len(TRAJ_TIMES)))
    for step in range(1, n_steps + 1):
        k1x, k1v = v, accel(x, qm)
        k2x, k2v = v + 0.5 * dt * k1v, accel(x + 0.5 * dt * k1x, qm)
        k3x, k3v = v + 0.5 * dt * k2v, accel(x + 0.5 * dt * k2x, qm)
        k4x, k4v = v + dt * k3v, accel(x + dt * k3x, qm)
        x = x + dt / 6 * (k1x + 2 * k2x + 2 * k3x + k4x)
        v = v + dt / 6 * (k1v + 2 * k2v + 2 * k3v + k4v)
        if step in grab:
            out[:, grab[step]] = x
    return out


def geodesic_check(n: int = 64, seed: int = 5) -> float:
    """Max |Δx| between the Newtonian generator and the FULL geodesics of the
    Phase B metric, for neutral bodies — the honesty bridge between Phase C
    dynamics and Phase B geometry."""
    rng = np.random.default_rng(seed)
    x0 = rng.uniform(*X_RANGE, n)
    v0 = rng.uniform(-V_MAX, V_MAX, n)
    newt = integrate_trajectories(x0, v0, np.zeros(n))[:, -1]

    # geodesic ODE in proper time for ds² = A dt² − B dx²; state (t, x, ut, ux)
    dtau = 0.005
    A, B = metric_A, metric_B
    Ap = lambda x: 2 * phi_prime(x)
    Bp = lambda x: -2 * phi_prime(x)
    t, x = np.zeros(n), x0.astype(float).copy()
    ut = 1.0 / np.sqrt(A(x) - B(x) * v0**2)
    ux = v0 * ut

    def rhs(state):
        t_, x_, ut_, ux_ = state
        return np.stack(
            [
                ut_,
                ux_,
                -(Ap(x_) / A(x_)) * ut_ * ux_,
                -Ap(x_) / (2 * B(x_)) * ut_**2 - Bp(x_) / (2 * B(x_)) * ux_**2,
            ]
        )

    state = np.stack([t, x, ut, ux])
    xs_prev, ts_prev = state[1].copy(), state[0].copy()
    target_t = TRAJ_TIMES[-1]
    done = np.zeros(n, dtype=bool)
    x_at_t = np.empty(n)
    for _ in range(int(round(target_t / dtau * 2.5))):
        k1 = rhs(state)
        k2 = rhs(state + 0.5 * dtau * k1)
        k3 = rhs(state + 0.5 * dtau * k2)
        k4 = rhs(state + dtau * k3)
        ts_prev, xs_prev = state[0].copy(), state[1].copy()
        state = state + dtau / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        crossed = (~done) & (state[0] >= target_t)
        if crossed.any():
            f = (target_t - ts_prev[crossed]) / (state[0][crossed] - ts_prev[crossed])
            x_at_t[crossed] = xs_prev[crossed] + f * (state[1][crossed] - xs_prev[crossed])
            done |= crossed
        if done.all():
            break
    return float(np.max(np.abs(newt - x_at_t)))


def make_dynamics_dataset(mix: str, seed: int = 0, n_bodies: int = 40, per_body: int = 600):
    """Trajectory dataset for the economy race. mix='neutral': every body is
    uncharged (gravity only). mix='charged': half the bodies carry q/m in
    ±[0.3, 1] — identity matters for them and only them. Returns a dict with
    train/test splits by SEGMENT and a held-out-BODY set (zero-shot gate)."""
    rng = np.random.default_rng(seed)
    if mix == "neutral":
        qm_body = np.zeros(n_bodies)
    else:
        qm_body = np.zeros(n_bodies)
        ch = rng.permutation(n_bodies)[: n_bodies // 2]
        sign = rng.choice([-1.0, 1.0], size=len(ch))
        qm_body[ch] = sign * rng.uniform(0.3, 1.0, size=len(ch))

    held_bodies = np.arange(n_bodies - 8, n_bodies)
    rows = {"body": [], "x0": [], "v0": [], "targets": []}
    for i in range(n_bodies):
        x0 = rng.uniform(*X_RANGE, per_body)
        v0 = rng.uniform(-V_MAX, V_MAX, per_body)
        tg = integrate_trajectories(x0, v0, np.full(per_body, qm_body[i]))
        rows["body"].append(np.full(per_body, i))
        rows["x0"].append(x0)
        rows["v0"].append(v0)
        rows["targets"].append(tg)
    body = np.concatenate(rows["body"]).astype(np.int64)
    X = np.stack(
        [np.concatenate(rows["x0"]), np.concatenate(rows["v0"])], axis=1
    ).astype(np.float32)
    Y = np.concatenate(rows["targets"]).astype(np.float32)

    is_held = np.isin(body, held_bodies)
    n_seen = (~is_held).sum()
    perm = rng.permutation(n_seen)
    seen_idx = np.where(~is_held)[0][perm]
    n_test = n_seen // 6
    return {
        "qm_body": qm_body,
        "held_bodies": held_bodies,
        "train": (body[seen_idx[n_test:]], X[seen_idx[n_test:]], Y[seen_idx[n_test:]]),
        "test": (body[seen_idx[:n_test]], X[seen_idx[:n_test]], Y[seen_idx[:n_test]]),
        "held": (body[is_held], X[is_held], Y[is_held]),
    }
