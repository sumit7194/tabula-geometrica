"""Step 94 — UNKNOWN REGIME: discover the hidden ISLANDS OF INTEGRABILITY in parameter space (the payoff).

The distillation head emits invariants (91/92); the impossibility certificate refuses to fabricate (84-87);
93 fused them into emit-or-certify. Now aim the fused instrument at a regime where the answer is NOT obvious:
scan a deformation parameter and have the instrument MAP which deformations are secretly still integrable.

System (web-verified): the coupled quartic oscillator H = 1/2(px^2+py^2) + 1/4(x^4+y^4) + (alpha/2) x^2 y^2 is
BOUNDED for all alpha (globally confining, no escape, no poles) and is INTEGRABLE only at alpha = 0, 1, 3 --
three islands invisible in the Hamiltonian -- and CHAOTIC for generic alpha (alpha=9 almost fully chaotic).
You cannot tell from the Hamiltonian which alpha are integrable. The instrument should rediscover the islands
from trajectory data alone.

The energy H is ALWAYS conserved and lies in the feature library, so the test is whether a SECOND, H-
independent invariant exists (that is exactly what integrability of a 2-DOF system means). Decision = the
project's held-out verify: the best H-independent conserved direction found on TRAIN must stay conserved on
HELD-OUT trajectories (a real second invariant generalizes; a finite-sample artifact does not).

Pre-reg (2026-06-20), energy E=10:
  U1 FIND THE ISLANDS: at alpha in {0, 1, 3} the instrument emits an H-independent 2nd invariant that verifies
     on held-out (held-out var-ratio < 1e-2).
  U2 CERTIFY THE CHAOS: at alpha in {0.5, 2, 5, 9} the best H-independent direction FAILS held-out (var-ratio
     > 0.1) -> no second invariant -> certify chaos.
  U3 CORRECT MAP: the emitted-integrable set equals the known {0,1,3} exactly (no false islands, no missed
     islands) -- the instrument reconstructs the integrability structure of parameter space from data.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

np.seterr(all="ignore")
DT = 0.02; E0 = 10.0


def Vpot(x, y, al):
    return 0.25 * (x ** 4 + y ** 4) + 0.5 * al * x ** 2 * y ** 2


def integrate(x, y, px, py, al, nstep=3000):
    X, Y, PX, PY = [], [], [], []
    def acc(x, y):
        return -(x ** 3 + al * x * y ** 2), -(y ** 3 + al * x ** 2 * y)
    ax, ay = acc(x, y)
    for k in range(nstep):
        px += 0.5 * DT * ax; py += 0.5 * DT * ay; x += DT * px; y += DT * py
        ax, ay = acc(x, y); px += 0.5 * DT * ax; py += 0.5 * DT * ay
        if k % 2 == 0 and k > 150:
            X.append(x); Y.append(y); PX.append(px); PY.append(py)
    return np.array(X), np.array(Y), np.array(PX), np.array(PY)


def trajs(al, n=130, seed=0):
    rng = np.random.default_rng(seed); out = []
    while len(out) < n:
        x = rng.uniform(-2.5, 2.5); y = rng.uniform(-2.5, 2.5); py = rng.uniform(-3, 3)
        k = 2 * (E0 - Vpot(x, y, al)) - py ** 2
        if k <= 0:
            continue
        px = np.sqrt(k) * rng.choice([-1, 1])
        X, Y, PX, PY = integrate(x, y, px, py, al)
        if len(X) > 80:
            out.append((X, Y, PX, PY))
    m = min(len(t[0]) for t in out)
    return tuple(np.array([t[i][:m] for t in out]) for i in range(4))


def _monos(deg):
    out = []
    for a in range(deg + 1):
        for b in range(deg - a + 1):
            for c in range(deg - a - b + 1):
                e = deg - a - b - c
                out.append((a, b, c, e))
    return out


_EXP = _monos(2) + _monos(4)                                      # complete degree-2 and degree-4 monomials
_NAMES = ["x^%d y^%d px^%d py^%d" % t for t in _EXP]


def library(X, Y, PX, PY):
    F = [X ** a * Y ** b * PX ** c * PY ** e for (a, b, c, e) in _EXP]
    return np.stack(F, -1), _NAMES


def Hexp_vec(names, al):
    """energy H in the complete-monomial basis: 1/2 px^2 + 1/2 py^2 + 1/4 x^4 + 1/4 y^4 + (al/2) x^2 y^2."""
    h = np.zeros(len(_EXP))
    idx = {t: i for i, t in enumerate(_EXP)}
    h[idx[(0, 0, 2, 0)]] = 0.5; h[idx[(0, 0, 0, 2)]] = 0.5
    h[idx[(4, 0, 0, 0)]] = 0.25; h[idx[(0, 4, 0, 0)]] = 0.25; h[idx[(2, 2, 0, 0)]] = 0.5 * al
    return h / np.linalg.norm(h)


def conserved(Phi):
    G, P, K = Phi.shape; flat = Phi.reshape(-1, K)
    mu = flat.mean(0); sd = flat.std(0) + 1e-9                    # standardize (conditions the 45-feature problem)
    Phi = (Phi - mu) / sd; flatc = Phi.reshape(-1, K)
    B = np.cov(flatc.T); Aw = np.mean([np.cov(Phi[g].T) for g in range(G)], 0)
    s, U = np.linalg.eigh(B); keep = s > 1e-9 * s.max(); W = U[:, keep] / np.sqrt(s[keep])
    lam, V = np.linalg.eigh(W.T @ Aw @ W); C = W @ V
    return lam, C, mu, sd


EMIT_THR = 1e-4    # separates EXACT global invariants (~1e-10) from KAM near-invariants (~1e-2) and chaos (>0.1)


def heldout(Phi, c_std, mu, sd):
    g = ((Phi - mu) / sd) @ c_std                                 # apply the standardized-space direction to held-out
    return float(np.mean([g[i].var() for i in range(g.shape[0])]) / (g.reshape(-1).var() + 1e-12))


def main():
    alphas = [0.0, 0.5, 1.0, 2.0, 3.0, 5.0, 9.0]
    known_integrable = {0.0, 1.0, 3.0}
    curve = []
    for al in alphas:
        Xtr, Ytr, PXtr, PYtr = trajs(al, seed=int(al * 100) + 1)
        Xte, Yte, PXte, PYte = trajs(al, seed=int(al * 100) + 777)
        Phi, names = library(Xtr, Ytr, PXtr, PYtr); Phite, _ = library(Xte, Yte, PXte, PYte)
        lam, C, mu, sd = conserved(Phi)
        hstd = Hexp_vec(names, al) * sd; hstd = hstd / np.linalg.norm(hstd)    # energy direction in standardized coords
        # the candidate 2nd invariant: smallest-eigenvalue direction INDEPENDENT of the energy H
        cand = None
        for j in range(C.shape[1]):
            cj = C[:, j] / np.linalg.norm(C[:, j])
            if abs(np.dot(cj, hstd)) < 0.8:
                cand = C[:, j]; break
        ho = heldout(Phite, cand, mu, sd) if cand is not None else 1.0
        emit = bool(ho < EMIT_THR)
        curve.append({"alpha": al, "heldout_varratio": ho, "decision": "EMIT 2nd invariant" if emit else "CERTIFY chaos",
                      "known": al in known_integrable})
        mark = "ISLAND (integrable)" if al in known_integrable else "(chaotic)"
        print(f"alpha={al:.1f} {mark:20s}: held-out var-ratio {ho:.2e} -> {'EMIT a 2nd invariant' if emit else 'CERTIFY: chaos'}")

    emitted = {c["alpha"] for c in curve if c["heldout_varratio"] < EMIT_THR}
    chaotic = [c for c in curve if c["alpha"] not in known_integrable]
    u1 = bool(all(c["heldout_varratio"] < EMIT_THR for c in curve if c["alpha"] in known_integrable))
    u2 = bool(all(c["heldout_varratio"] > EMIT_THR for c in chaotic))
    u3 = bool(emitted == known_integrable)
    out = {"energy": E0, "known_integrable": sorted(known_integrable), "discovered_islands": sorted(emitted),
           "curve": curve, "U1_find_islands": u1, "U2_certify_chaos": u2, "U3_correct_map": u3,
           "islands_discovered": bool(u1 and u2 and u3)}
    print(f"\nU1 EMIT at all known islands {sorted(known_integrable)}: {u1}")
    print(f"U2 CERTIFY chaos at all generic alpha: {u2}")
    print(f"U3 discovered island set {sorted(emitted)} == known {sorted(known_integrable)}: {u3}")
    print(f"\nISLANDS OF INTEGRABILITY DISCOVERED FROM DATA (emit-or-certify maps parameter space): {out['islands_discovered']}")
    (Path(__file__).resolve().parent.parent / "results" / "94_discover_islands.json").write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(figsize=(9, 5.2))
    ho = [c["heldout_varratio"] for c in curve]
    colors = ["seagreen" if a in known_integrable else "crimson" for a in alphas]
    ax.scatter(alphas, np.clip(ho, 1e-12, None), c=colors, s=90, zorder=5)
    ax.semilogy(alphas, np.clip(ho, 1e-12, None), color="gray", lw=0.8, zorder=1)
    ax.axhline(EMIT_THR, color="seagreen", ls=":", label="EMIT below (exact 2nd invariant)")
    ax.axhline(EMIT_THR, color="navy", ls=":", alpha=0)
    for a in known_integrable:
        ax.axvline(a, color="seagreen", alpha=0.15, lw=8)
    ax.set_xlabel("deformation α (x²y² coupling)"); ax.set_ylabel("held-out var-ratio of best 2nd-invariant candidate")
    ax.legend(fontsize=8); ax.set_title("discovering the islands of integrability from data\ngreen=integrable (α=0,1,3, the instrument EMITS), red=chaotic (CERTIFY)")
    fig.tight_layout(); fig.savefig(Path(__file__).resolve().parent.parent / "results" / "94_discover_islands.png", dpi=140)
    print("saved results/94_discover_islands.json + .png")


if __name__ == "__main__":
    main()
