"""Step 25 — Phase G foundation: the unified world/episode generator.

Eight world families, one episode format. An episode = context tokens (labeled
same-event pairs / tagged trajectory snippets / matter blobs) + queries (unlabeled
pairs or fresh-trajectory predictions). Every episode stores its TRUE world
parameters — the hidden ground truth the world-map probes (G-3) compare against.

Token (18): type onehot 4 [pair/traj/matter/null] + payload 14
  pair:   obs_a(5 padded) obs_b(5) label(1)
  traj:   tag(4) x0(2) v0(2) p1(2) p2(2) p3(2)
  matter: pos(2) mass(1)
Query (14): qtype onehot 2 + payload 12 [pair: obs_a(5) obs_b(5) | traj: tag(4) x0(2) v0(2)]
Target: 6 floats (binary in slot 0, or 3 positions x <=2 dims), + type/mask.

Usage: python 25_worldgen.py --n-per-family 3000 --out results/25_bank.npz
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np

RESULTS = Path(__file__).resolve().parent.parent / "results"
N_TOK, N_Q = 32, 16
TOKEN_DIM, Q_DIM, T_DIM = 18, 14, 6
TIMES = (1.0, 2.0, 3.0)
FAMILIES = ("flat1p1", "flat3p1", "well1p1", "aniso2p1",
            "chargedE", "magneticB", "twocharge", "matter")


def _tok(type_i, payload):
    t = np.zeros(TOKEN_DIM, dtype=np.float32)
    t[type_i] = 1
    t[4:4 + len(payload)] = payload
    return t


def _pair_tok(a, b, label):
    pa = np.zeros(5); pa[:len(a)] = a
    pb = np.zeros(5); pb[:len(b)] = b
    return _tok(0, np.concatenate([pa, pb, [label]]))


def _traj_tok(tag, x0, v0, ps):
    pl = np.zeros(14)
    pl[:4] = tag
    pl[4:4 + len(x0)] = x0
    pl[6:6 + len(v0)] = v0
    for i, p in enumerate(ps):
        pl[8 + 2 * i: 8 + 2 * i + len(np.atleast_1d(p))] = p
    return _tok(1, pl)


def _q_pair(a, b):
    q = np.zeros(Q_DIM, dtype=np.float32)
    q[0] = 1
    q[2:2 + len(a)] = a
    q[7:7 + len(b)] = b
    return q


def _q_traj(tag, x0, v0):
    q = np.zeros(Q_DIM, dtype=np.float32)
    q[1] = 1
    q[2:6] = tag
    q[6:6 + len(x0)] = x0
    q[8:8 + len(v0)] = v0
    return q


def _rk4(accel, x0, v0, dt=0.01):
    """Generic integrator; x0/v0 (n, dim). Returns positions at TIMES."""
    grab = {int(round(t / dt)): i for i, t in enumerate(TIMES)}
    x, v = x0.copy(), v0.copy()
    out = np.empty((len(x0), len(TIMES), x0.shape[1]))
    for step in range(1, int(round(TIMES[-1] / dt)) + 1):
        k1x, k1v = v, accel(x, v)
        k2x, k2v = v + 0.5 * dt * k1v, accel(x + 0.5 * dt * k1x, v + 0.5 * dt * k1v)
        k3x, k3v = v + 0.5 * dt * k2v, accel(x + 0.5 * dt * k2x, v + 0.5 * dt * k2v)
        k4x, k4v = v + dt * k3v, accel(x + dt * k3x, v + dt * k3v)
        x = x + dt / 6 * (k1x + 2 * k2x + 2 * k3x + k4x)
        v = v + dt / 6 * (k1v + 2 * k2v + 2 * k3v + k4v)
        if step in grab:
            out[:, grab[step]] = x
    return out


def _boost1(tau, eta):
    return np.stack([tau * np.cosh(eta), tau * np.sinh(eta)], -1)


def _pairs_episode(rng, obs_same, obs_diff):
    """Generic same-event pairs episode from two samplers."""
    toks, qs, ts = [], [], []
    for _ in range(N_TOK):
        if rng.random() < 0.5:
            a, b = obs_same(rng)
            toks.append(_pair_tok(a, b, 1.0))
        else:
            a, b = obs_diff(rng)
            toks.append(_pair_tok(a, b, 0.0))
    for _ in range(N_Q):
        if rng.random() < 0.5:
            a, b = obs_same(rng)
            lab = 1.0
        else:
            a, b = obs_diff(rng)
            lab = 0.0
        qs.append(_q_pair(a, b))
        t = np.zeros(T_DIM, dtype=np.float32)
        t[0] = lab
        ts.append(t)
    return toks, qs, ts


def gen_flat1p1(rng):
    def same(r):
        tau = r.uniform(0.5, 3.0)
        return (_boost1(tau, r.uniform(-1.5, 1.5)) + r.normal(0, 0.01, 2),
                _boost1(tau, r.uniform(-1.5, 1.5)) + r.normal(0, 0.01, 2))

    def diff(r):
        t1 = r.uniform(0.5, 3.0)
        t2 = t1
        while abs(t2 - t1) < 0.15:
            t2 = r.uniform(0.5, 3.0)
        return (_boost1(t1, r.uniform(-1.5, 1.5)) + r.normal(0, 0.01, 2),
                _boost1(t2, r.uniform(-1.5, 1.5)) + r.normal(0, 0.01, 2))

    return _pairs_episode(rng, same, diff), {}


def gen_flat3p1(rng):
    def shell(r, tau):
        eta = r.uniform(-1.5, 1.5)
        n = r.normal(size=3)
        n /= np.linalg.norm(n)
        return np.concatenate([[tau * np.cosh(eta)], tau * np.sinh(eta) * n]) \
            + r.normal(0, 0.01, 4)

    def same(r):
        tau = r.uniform(0.5, 3.0)
        return shell(r, tau), shell(r, tau)

    def diff(r):
        t1 = r.uniform(0.5, 3.0)
        t2 = t1
        while abs(t2 - t1) < 0.15:
            t2 = r.uniform(0.5, 3.0)
        return shell(r, t1), shell(r, t2)

    return _pairs_episode(rng, same, diff), {}


def gen_well1p1(rng):
    depth, width = rng.uniform(0.05, 0.25), rng.uniform(0.8, 1.3)

    def obs(r, xp, tau):
        A = 1 - 2 * depth * np.exp(-xp**2 / (2 * width**2))
        B = 1 + 2 * depth * np.exp(-xp**2 / (2 * width**2))
        eta = r.uniform(-1.5, 1.5)
        d = [tau * np.cosh(eta) / np.sqrt(A), tau * np.sinh(eta) / np.sqrt(B)]
        return np.array([xp, *d]) + np.array([0, *r.normal(0, 0.01, 2)])

    def same(r):
        xp, tau = r.uniform(-3, 3), r.uniform(0.5, 3.0)
        return obs(r, xp, tau), obs(r, xp, tau)

    def diff(r):
        xp, t1 = r.uniform(-3, 3), r.uniform(0.5, 3.0)
        t2 = t1
        while abs(t2 - t1) < 0.15:
            t2 = r.uniform(0.5, 3.0)
        return obs(r, xp, t1), obs(r, xp, t2)

    (toks, qs, ts) = _pairs_episode(rng, same, diff)
    return (toks, qs, ts), {"depth": depth, "width": width}


def gen_aniso2p1(rng):
    s_phi, s_b, s_d = rng.uniform(0.05, 0.2), rng.uniform(0.05, 0.3), rng.uniform(0.05, 0.25)

    def fields(x, y):
        ph = -s_phi * np.exp(-(x**2 + y**2) / 2)
        b = np.exp(-((x - 1) ** 2 + (y - 0.5) ** 2) / 2)
        dd = np.exp(-((x + 1) ** 2 + (y + 0.5) ** 2) / 2)
        A = 1 + 2 * ph
        return A, 1 - 2 * ph + s_b * b, 1 - 2 * ph - s_b * b, s_d * dd

    def obs(r, xp, yp, tau):
        A, B, C, D = fields(xp, yp)
        det = B * C - D * D
        s = np.sqrt(det)
        t = np.sqrt(B + C + 2 * s)
        i11, i12, i22 = (C + s) / (t * s), -D / (t * s), (B + s) / (t * s)
        eta, th = r.uniform(-1.5, 1.5), r.uniform(0, 2 * np.pi)
        fx, fy = tau * np.sinh(eta) * np.cos(th), tau * np.sinh(eta) * np.sin(th)
        return np.array([xp, yp, tau * np.cosh(eta) / np.sqrt(A),
                         i11 * fx + i12 * fy, i12 * fx + i22 * fy]) \
            + np.concatenate([[0, 0], r.normal(0, 0.01, 3)])

    def same(r):
        xp, yp, tau = r.uniform(-2.5, 2.5), r.uniform(-2.5, 2.5), r.uniform(0.5, 3.0)
        return obs(r, xp, yp, tau), obs(r, xp, yp, tau)

    def diff(r):
        xp, yp, t1 = r.uniform(-2.5, 2.5), r.uniform(-2.5, 2.5), r.uniform(0.5, 3.0)
        t2 = t1
        while abs(t2 - t1) < 0.15:
            t2 = r.uniform(0.5, 3.0)
        return obs(r, xp, yp, t1), obs(r, xp, yp, t2)

    (toks, qs, ts) = _pairs_episode(rng, same, diff)
    return (toks, qs, ts), {"s_phi": s_phi, "s_b": s_b, "s_d": s_d}


# last episode's per-query true labels (for the A3a equivariant-decode probe);
# captured here to avoid changing the return signature / all callers.
_LAST_QLABELS = None


def _jsonify(v):
    if v is None:
        return None
    a = np.atleast_1d(v).astype(float)
    return float(a[0]) if a.size == 1 else a.tolist()


def _traj_episode(rng, accel_for, labels, dim):
    """Generic trajectory episode: 6 bodies, 4 context snippets + queries."""
    global _LAST_QLABELS
    tags = np.eye(8)[rng.permutation(8)[:6], :4]
    toks, qs, ts = [], [], []
    for bi in range(6):
        acc = accel_for(labels[bi])
        for _ in range(4):
            x0 = rng.uniform(-2.5, 2.5, dim)
            v0 = rng.uniform(-0.3, 0.3, dim)
            ps = _rk4(acc, x0[None], v0[None])[0]
            toks.append(_traj_tok(tags[bi], x0, v0, ps))
    while len(toks) < N_TOK:
        toks.append(np.zeros(TOKEN_DIM, dtype=np.float32))
        toks[-1][3] = 1  # null
    qi = rng.integers(0, 6, N_Q)
    for bi in qi:
        acc = accel_for(labels[bi])
        x0 = rng.uniform(-2.5, 2.5, dim)
        v0 = rng.uniform(-0.3, 0.3, dim)
        ps = _rk4(acc, x0[None], v0[None])[0]
        qs.append(_q_traj(tags[bi], x0, v0))
        t = np.zeros(T_DIM, dtype=np.float32)
        for i, p in enumerate(ps):
            t[2 * i:2 * i + dim] = p
        ts.append(t)
    _LAST_QLABELS = [_jsonify(labels[bi]) for bi in qi]
    return toks, qs, ts


def _well_acc(depth, width):
    def a(x, v):
        return -depth * x * np.exp(-x**2 / (2 * width**2)) / width**2
    return a


def gen_chargedE(rng):
    depth, ec, ea = rng.uniform(0.1, 0.2), rng.uniform(0.3, 1.3), rng.uniform(0.15, 0.45)
    qms = np.where(rng.random(6) < 0.5, 0.0,
                   rng.choice([-1, 1], 6) * rng.uniform(0.3, 1.0, 6))

    def acc_for(qm):
        def a(x, v):
            return (_well_acc(depth, 1.0)(x, v)
                    + qm * ea * np.exp(-((x - ec) ** 2) / 2))
        return a

    return _traj_episode(rng, acc_for, qms, 1), \
        {"depth": depth, "e_center": ec, "e_amp": ea, "qms": qms.tolist()}


def gen_magneticB(rng):
    depth, ba = rng.uniform(0.1, 0.2), rng.uniform(0.3, 0.9)
    bc = rng.uniform(-1.2, 1.2, 2)
    qms = np.where(rng.random(6) < 0.5, 0.0,
                   rng.choice([-1, 1], 6) * rng.uniform(0.3, 1.0, 6))

    def acc_for(qm):
        def a(x, v):
            r2 = ((x - bc) ** 2).sum(-1)
            B = ba * np.exp(-r2 / 2)
            e = np.exp(-(x**2).sum(-1) / 2)
            ag = -depth * x * e[..., None]
            return ag + qm * np.stack([v[..., 1] * B, -v[..., 0] * B], -1)
        return a

    return _traj_episode(rng, acc_for, qms, 2), \
        {"depth": depth, "b_amp": ba, "b_center": bc.tolist(), "qms": qms.tolist()}


def gen_twocharge(rng):
    depth = rng.uniform(0.1, 0.2)
    p1 = dict(amp=rng.uniform(0.15, 0.45), c=rng.uniform(0.3, 1.3))
    p2 = dict(amp=rng.uniform(0.2, 0.5), c=rng.uniform(-1.6, -0.6))
    qm = np.zeros((6, 2))
    for j in range(2):
        ch = rng.random(6) < 0.6
        qm[ch, j] = rng.choice([-1, 1], int(ch.sum())) * rng.uniform(0.3, 1.0, int(ch.sum()))

    def acc_for(q):
        def a(x, v):
            return (_well_acc(depth, 1.0)(x, v)
                    + q[0] * p1["amp"] * np.exp(-((x - p1["c"]) ** 2) / 2)
                    + q[1] * p2["amp"] * np.exp(-((x - p2["c"]) ** 2) / 2))
        return a

    return _traj_episode(rng, acc_for, list(qm), 1), \
        {"depth": depth, "f1": p1, "f2": p2, "qms": qm.tolist()}


def gen_matter(rng):
    nb = int(rng.integers(1, 4))
    c = rng.uniform(-1.8, 1.8, (nb, 2))
    m = rng.uniform(0.3, 1.0, nb)

    def acc_for(_):
        def a(x, v):
            d = x[:, None, :] - c[None]
            r2 = (d**2).sum(-1) + 0.35**2
            return -(m[None, :, None] * d / r2[..., None] ** 1.5).sum(1)
        return a

    toks, qs, ts = _traj_episode(rng, acc_for, [None] * 6, 2)
    for i in range(nb):
        toks[N_TOK - 1 - i] = _tok(2, np.concatenate([c[i], [m[i]]]))
    return (toks, qs, ts), {"blobs": np.concatenate([c, m[:, None]], 1).tolist()}


GENS = dict(flat1p1=gen_flat1p1, flat3p1=gen_flat3p1, well1p1=gen_well1p1,
            aniso2p1=gen_aniso2p1, chargedE=gen_chargedE,
            magneticB=gen_magneticB, twocharge=gen_twocharge, matter=gen_matter)


class _WideRng:
    """Wraps a Generator so every uniform(lo,hi) range is expanded about its
    midpoint by `factor` (G2 zero-shot: wider worlds than training). All other
    draws (.random/.choice/.normal/.integers) pass through unchanged, so
    observation noise and discrete choices are untouched."""

    def __init__(self, rng, factor):
        self._rng, self._f = rng, factor

    def uniform(self, low=0.0, high=1.0, size=None):
        mid, half = (low + high) / 2, (high - low) / 2 * self._f
        return self._rng.uniform(mid - half, mid + half, size)

    def __getattr__(self, name):
        return getattr(self._rng, name)


def main() -> None:
    from curvlib import progress

    p = argparse.ArgumentParser()
    p.add_argument("--n-per-family", type=int, default=3000)
    p.add_argument("--out", default=str(RESULTS / "25_bank.npz"))
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--widen", type=float, default=1.0,
                   help="G2: expand every sampled range by this factor (1.25 = +25%)")
    p.add_argument("--emit-qlabels", action="store_true",
                   help="A3a probe: store per-query true labels in meta (q_labels)")
    args = p.parse_args()

    rng = np.random.default_rng(args.seed)
    if args.widen != 1.0:
        rng = _WideRng(rng, args.widen)
    T, Q, TG, FAM, META = [], [], [], [], []
    total = args.n_per_family * len(FAMILIES)
    k = 0
    for fi, fam in enumerate(FAMILIES):
        for _ in range(args.n_per_family):
            globals()["_LAST_QLABELS"] = None
            (toks, qs, ts), meta = GENS[fam](rng)
            if args.emit_qlabels:
                meta = {**meta, "q_labels": _LAST_QLABELS}
            T.append(np.stack(toks))
            Q.append(np.stack(qs))
            TG.append(np.stack(ts))
            FAM.append(fi)
            META.append(meta)
            k += 1
            if k % 500 == 0:
                # per-seed heartbeat name: parallel shards racing on one file
                # hit the atomic-rename collision (s3 died on os.replace)
                progress(f"25_worldgen_s{args.seed}", k, total)
    np.savez_compressed(
        args.out,
        tokens=np.stack(T).astype(np.float32),
        queries=np.stack(Q).astype(np.float32),
        targets=np.stack(TG).astype(np.float32),
        family=np.array(FAM, dtype=np.int64),
    )
    Path(args.out).with_suffix(".meta.json").write_text(json.dumps(META))
    print(f"bank: {len(T)} episodes -> {args.out}")


if __name__ == "__main__":
    main()
