"""worldgen_v2 — unified in-context episode generator across the FULL physics span (Generalist v2).

The foundation for the big generalist (user decision 2026-06-17: full span, ~10-15M, build now). Every
family is cast into ONE schema so the model can build a single law-space connecting gravity, EM, charge,
scalar forces, curved spacetime (Schwarzschild + charged black holes), and quantum state geometry.

Schema (amortized in-context regression over a hidden world):
  episode = (family_id, K context (u,y) pairs, query u_q -> predict y_q).
  u in R^DU (padded), y in R^DY (padded), with a per-family y-mask (which outputs are real).
  The model infers the hidden world (e.g. charge q, mass M, Bloch vector) from the context and answers.

Families span 3 modalities: TRAJECTORY (gravity/charged/scalar -> acceleration), METRIC (Schwarzschild/
Reissner-Nordstrom -> interval ds^2), QUANTUM (Bloch -> Born probability). Physics is web-verified in the
specialist scripts that introduced each (45 scalar, 46 magnetic, 51 Bloch, 56 RN-f, 60 EF metric).
"""

import numpy as np

DU, DY = 6, 4
WELL_W = 1.0
B_AMP, B_CTR = 0.7, (0.6, -0.4)
SCAL_CTR = (1.2, -0.8)


def _grav(x, y):
    e = np.exp(-(x ** 2 + y ** 2) / (2 * WELL_W ** 2))
    return -0.2 * x * e / WELL_W ** 2, -0.2 * y * e / WELL_W ** 2


def _pad(arr, d):
    out = np.zeros((len(arr), d), np.float32); out[:, : arr.shape[1]] = arr; return out


# ---- TRAJECTORY families: u = (x,y,vx,vy), y = (ax,ay) ----
def _traj_inputs(rng, n):
    return np.stack([rng.uniform(-2.5, 2.5, n), rng.uniform(-2.5, 2.5, n),
                     rng.uniform(-0.5, 0.5, n), rng.uniform(-0.5, 0.5, n)], 1).astype(np.float32)


class Gravity:
    name = "gravity"; ymask = np.array([1, 1, 0, 0], np.float32)
    def world(self, rng): return {"depth": rng.uniform(0.1, 0.35)}
    def obs(self, w, rng, n):
        u = _traj_inputs(rng, n); x, y = u[:, 0], u[:, 1]
        e = np.exp(-(x ** 2 + y ** 2) / (2 * WELL_W ** 2))
        ax = -w["depth"] * x * e / WELL_W ** 2; ay = -w["depth"] * y * e / WELL_W ** 2
        return _pad(u, DU), _pad(np.stack([ax, ay], 1), DY)


class Charged:
    name = "charged"; ymask = np.array([1, 1, 0, 0], np.float32)
    def world(self, rng): return {"q": rng.uniform(-1, 1)}
    def obs(self, w, rng, n):
        u = _traj_inputs(rng, n); x, y, vx, vy = u.T
        gx, gy = _grav(x, y)
        B = B_AMP * np.exp(-(((x - B_CTR[0]) ** 2) + (y - B_CTR[1]) ** 2) / 2.0)
        ax = gx + w["q"] * vy * B; ay = gy - w["q"] * vx * B
        return _pad(u, DU), _pad(np.stack([ax, ay], 1), DY)


class Scalar:
    name = "scalar"; ymask = np.array([1, 1, 0, 0], np.float32)
    def world(self, rng): return {"rho": rng.uniform(0.0, 1.5)}
    def obs(self, w, rng, n):
        u = _traj_inputs(rng, n); x, y = u[:, 0], u[:, 1]
        gx, gy = _grav(x, y)
        dx, dy = x - SCAL_CTR[0], y - SCAL_CTR[1]
        es = np.exp(-(dx ** 2 + dy ** 2) / (2 * WELL_W ** 2))
        ax = gx - w["rho"] * 0.15 * dx * es / WELL_W ** 2; ay = gy - w["rho"] * 0.15 * dy * es / WELL_W ** 2
        return _pad(u, DU), _pad(np.stack([ax, ay], 1), DY)


# ---- METRIC families: u = (r, dv, dr), y = (ds^2) ----  (Eddington-Finkelstein, regular across horizon)
class Schwarzschild:
    name = "schwarzschild"; ymask = np.array([1, 0, 0, 0], np.float32)
    def world(self, rng): return {"M": rng.uniform(0.7, 1.5)}
    def obs(self, w, rng, n):
        r = rng.uniform(0.6, 6.0, n).astype(np.float32)
        dv = rng.uniform(-0.3, 0.3, n).astype(np.float32); dr = rng.uniform(-0.3, 0.3, n).astype(np.float32)
        ds2 = -(1 - 2 * w["M"] / r) * dv ** 2 + 2 * dv * dr
        return _pad(np.stack([r, dv, dr], 1), DU), _pad(ds2[:, None], DY)


class ReissnerNordstrom:
    name = "reissner_nordstrom"; ymask = np.array([1, 0, 0, 0], np.float32)
    def world(self, rng): return {"M": rng.uniform(0.8, 1.3), "Q": rng.uniform(0.0, 0.8)}
    def obs(self, w, rng, n):
        r = rng.uniform(0.5, 6.0, n).astype(np.float32)
        dv = rng.uniform(-0.3, 0.3, n).astype(np.float32); dr = rng.uniform(-0.3, 0.3, n).astype(np.float32)
        f = 1 - 2 * w["M"] / r + w["Q"] ** 2 / r ** 2                # charged: f(r)=1-2M/r+Q^2/r^2
        ds2 = -f * dv ** 2 + 2 * dv * dr
        return _pad(np.stack([r, dv, dr], 1), DU), _pad(ds2[:, None], DY)


# ---- QUANTUM family: u = (measurement axis n), y = (Born probability) ----
class Bloch:
    name = "bloch"; ymask = np.array([1, 0, 0, 0], np.float32)
    def world(self, rng):
        cz = rng.uniform(-1, 1); phi = rng.uniform(0, 2 * np.pi); s = np.sqrt(1 - cz ** 2)
        return {"r": np.array([s * np.cos(phi), s * np.sin(phi), cz], np.float32)}
    def obs(self, w, rng, n):
        cz = rng.uniform(-1, 1, n); phi = rng.uniform(0, 2 * np.pi, n); s = np.sqrt(1 - cz ** 2)
        nax = np.stack([s * np.cos(phi), s * np.sin(phi), cz], 1).astype(np.float32)
        prob = (1 + nax @ w["r"]) / 2
        return _pad(nax, DU), _pad(prob[:, None], DY)


FAMILIES = [Gravity(), Charged(), Scalar(), Schwarzschild(), ReissnerNordstrom(), Bloch()]
NFAM = len(FAMILIES)


def make_episode(rng, fam_id, K, Q):
    fam = FAMILIES[fam_id]; w = fam.world(rng)
    u, y = fam.obs(w, rng, K + Q)
    return {"fam": fam_id, "ctx_u": u[:K], "ctx_y": y[:K], "q_u": u[K:], "q_y": y[K:],
            "ymask": fam.ymask, "world": w}


def make_batch(rng, B, K, Q, fam_id=None):
    """Batch of B episodes (random families unless fam_id given). Returns arrays for the model."""
    fams = rng.integers(0, NFAM, B) if fam_id is None else np.full(B, fam_id)
    cu = np.zeros((B, K, DU), np.float32); cy = np.zeros((B, K, DY), np.float32)
    qu = np.zeros((B, Q, DU), np.float32); qy = np.zeros((B, Q, DY), np.float32)
    ym = np.zeros((B, DY), np.float32)
    for b in range(B):
        ep = make_episode(rng, int(fams[b]), K, Q)
        cu[b], cy[b], qu[b], qy[b], ym[b] = ep["ctx_u"], ep["ctx_y"], ep["q_u"], ep["q_y"], ep["ymask"]
    return {"fam": fams.astype(np.int64), "ctx_u": cu, "ctx_y": cy, "q_u": qu, "q_y": qy, "ymask": ym}


if __name__ == "__main__":
    rng = np.random.default_rng(0)
    for fid, fam in enumerate(FAMILIES):
        ep = make_episode(rng, fid, 8, 4)
        err = float(np.mean(((ep["q_y"] - ep["ctx_y"].mean(0)) * ep["ymask"]) ** 2))  # naive-baseline scale
        print(f"{fam.name:18s} ctx_u{ep['ctx_u'].shape} ctx_y{ep['ctx_y'].shape} ymask{ep['ymask']} "
              f"y-var(masked)~{err:.4f} world={ {k: (round(float(np.mean(v)),3) if np.ndim(v) else round(v,3)) for k,v in ep['world'].items()} }")
    b = make_batch(rng, 16, 8, 4)
    print("batch:", {k: v.shape for k, v in b.items() if hasattr(v, 'shape')})
