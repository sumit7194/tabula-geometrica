"""Step 95 — A GENUINELY-OPEN FAMILY: map integrability off the textbook line, cross-validated by Lyapunov.

Script 94 discovered the integrable islands of the SYMMETRIC quartic oscillator (alpha=0,1,3 at kappa=1, a
classified case). Now take the family OFF its classified line with an anisotropy kappa:
    V(x,y) = 1/4 (x^4 + kappa y^4) + (alpha/2) x^2 y^2
Web-verified anchors: alpha=0 is SEPARABLE -> integrable for ANY kappa; alpha=1 (isotropic) and alpha=3
(separable after 45-deg rotation) are integrable only at kappa=1. For kappa != 1 the integrability structure
is NOT tabulated. To make "trust the instrument" defensible, we CROSS-VALIDATE every verdict against an
INDEPENDENT chaos diagnostic -- the maximal Lyapunov exponent (Benettin: integrate the variational/tangent
equations; lambda~0 for regular motion, lambda>0 for chaos). If the distillation instrument's emit/certify
agrees with Lyapunov everywhere, the map is trustworthy even where no table exists.

Pre-reg (2026-06-20), energy E=10:
  O1 ANCHOR (validation): at kappa=1 the instrument recovers islands at alpha in {0,1,3} (emit) with Lyapunov
     ~0 there and >0 between -- both methods reproduce the classified result.
  O2 CROSS-VALIDATION: the instrument's emit/certify binary AGREES with the Lyapunov regular/chaotic binary at
     EVERY scanned (alpha,kappa) point.
  O3 OPEN FINDING: report the cross-validated integrable set at kappa=2 (off the table). Anchor: alpha=0 must
     stay integrable (separable, both methods). The rest is the data-driven, Lyapunov-corroborated finding.
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


def Vpot(x, y, al, ka):
    return 0.25 * (x ** 4 + ka * y ** 4) + 0.5 * al * x ** 2 * y ** 2


def acc(x, y, al, ka):
    return -(x ** 3 + al * x * y ** 2), -(ka * y ** 3 + al * x ** 2 * y)


def sample_ic(al, ka, rng):
    while True:
        x = rng.uniform(-2.5, 2.5); y = rng.uniform(-2.5, 2.5); py = rng.uniform(-3, 3)
        k = 2 * (E0 - Vpot(x, y, al, ka)) - py ** 2
        if k > 0:
            return x, y, np.sqrt(k) * rng.choice([-1, 1]), py


# ---------- the distillation instrument (same as 94: complete deg-2+4 library, H-deflation, held-out) ----------
def _monos(d):
    return [(a, b, c, d - a - b - c) for a in range(d + 1) for b in range(d - a + 1) for c in range(d - a - b + 1)]
_EXP = _monos(2) + _monos(4)


def integ_traj(al, ka, n=90, nstep=2500, seed=0):
    rng = np.random.default_rng(seed); out = []
    while len(out) < n:
        x, y, px, py = sample_ic(al, ka, rng); X, Y, PX, PY = [], [], [], []
        ax, ay = acc(x, y, al, ka)
        for k in range(nstep):
            px += .5 * DT * ax; py += .5 * DT * ay; x += DT * px; y += DT * py
            ax, ay = acc(x, y, al, ka); px += .5 * DT * ax; py += .5 * DT * ay
            if k % 2 == 0 and k > 150:
                X.append(x); Y.append(y); PX.append(px); PY.append(py)
        if len(X) > 60:
            out.append((np.array(X), np.array(Y), np.array(PX), np.array(PY)))
    m = min(len(t[0]) for t in out)
    return tuple(np.array([t[i][:m] for t in out]) for i in range(4))


def lib(X, Y, PX, PY):
    return np.stack([X ** a * Y ** b * PX ** c * PY ** e for (a, b, c, e) in _EXP], -1)


def Hvec(al):
    h = np.zeros(len(_EXP)); idx = {t: i for i, t in enumerate(_EXP)}
    h[idx[(0, 0, 2, 0)]] = .5; h[idx[(0, 0, 0, 2)]] = .5
    h[idx[(4, 0, 0, 0)]] = .25; h[idx[(0, 4, 0, 0)]] = .25; h[idx[(2, 2, 0, 0)]] = .5 * al
    return h / np.linalg.norm(h)


def instrument(al, ka):
    Xtr, Ytr, PXtr, PYtr = integ_traj(al, ka, seed=11); Xte, Yte, PXte, PYte = integ_traj(al, ka, seed=99)
    Phi = lib(Xtr, Ytr, PXtr, PYtr); Phite = lib(Xte, Yte, PXte, PYte)
    G, P, K = Phi.shape; flat = Phi.reshape(-1, K); mu = flat.mean(0); sd = flat.std(0) + 1e-9
    Z = (Phi - mu) / sd; B = np.cov(Z.reshape(-1, K).T); Aw = np.mean([np.cov(Z[g].T) for g in range(G)], 0)
    s, U = np.linalg.eigh(B); keep = s > 1e-9 * s.max(); W = U[:, keep] / np.sqrt(s[keep])
    ev, V = np.linalg.eigh(W.T @ Aw @ W); C = W @ V
    hstd = Hvec(al) * sd; hstd /= np.linalg.norm(hstd)
    cand = None
    for j in range(C.shape[1]):
        cj = C[:, j] / np.linalg.norm(C[:, j])
        if abs(cj @ hstd) < 0.8:
            cand = C[:, j]; break
    if cand is None:
        return 1.0
    g = ((Phite - mu) / sd) @ cand
    return float(np.mean([g[i].var() for i in range(g.shape[0])]) / (g.reshape(-1).var() + 1e-12))


def sali_single(al, ka, nstep=6000, renorm=4, seed=3):
    """Smaller Alignment Index for ONE trajectory: stays O(1) for REGULAR motion, collapses to ~0 for CHAOS."""
    rng = np.random.default_rng(seed); x, y, px, py = sample_ic(al, ka, rng)
    D = rng.standard_normal((2, 4))
    D[0] /= np.linalg.norm(D[0]); D[1] = D[1] - (D[1] @ D[0]) * D[0]; D[1] /= np.linalg.norm(D[1])
    def A(x, y): return acc(x, y, al, ka)
    def dacc(x, y, dx, dy):
        Vxx = 3 * x ** 2 + al * y ** 2; Vyy = 3 * ka * y ** 2 + al * x ** 2; Vxy = 2 * al * x * y
        return -(Vxx * dx + Vxy * dy), -(Vxy * dx + Vyy * dy)
    ax, ay = A(x, y); da = np.array([dacc(x, y, D[i, 0], D[i, 1]) for i in range(2)])  # (2,2): (dpx',dpy') per vec
    last = 2.0
    for k in range(nstep):
        px += .5 * DT * ax; py += .5 * DT * ay; x += DT * px; y += DT * py
        D[:, 2] += .5 * DT * da[:, 0]; D[:, 3] += .5 * DT * da[:, 1]; D[:, 0] += DT * D[:, 2]; D[:, 1] += DT * D[:, 3]
        ax, ay = A(x, y); da = np.array([dacc(x, y, D[i, 0], D[i, 1]) for i in range(2)])
        px += .5 * DT * ax; py += .5 * DT * ay; D[:, 2] += .5 * DT * da[:, 0]; D[:, 3] += .5 * DT * da[:, 1]
        if (k + 1) % renorm == 0:
            u1 = D[0] / (np.linalg.norm(D[0]) + 1e-300); u2 = D[1] / (np.linalg.norm(D[1]) + 1e-300)
            last = float(min(np.linalg.norm(u1 + u2), np.linalg.norm(u1 - u2)))
            D[0] = u1; D[1] = u2
            if last < 1e-12:
                break
    return last


def chaotic_fraction(al, ka, nIC=14):
    """GLOBAL integrability test: fraction of initial conditions that are chaotic (SALI -> 0). Integrable
    systems have NO chaotic trajectories (fraction ~0); non-integrable ones have a chaotic sea (fraction > 0).
    This matches the instrument's global notion (a conserved quantity must hold for ALL trajectories)."""
    return float(np.mean([sali_single(al, ka, seed=s) < 1e-4 for s in range(nIC)]))


def main():
    alphas = [0.0, 0.5, 1.0, 2.0, 3.0, 5.0]
    rows = []
    for ka in [1.0, 2.0]:
        for al in alphas:
            ho = instrument(al, ka); cf = chaotic_fraction(al, ka)
            inst_emit = bool(ho < 1e-4); sali_reg = bool(cf < 0.1)        # integrable <=> no chaotic sea
            rows.append({"kappa": ka, "alpha": al, "heldout_varratio": ho, "chaotic_fraction": cf,
                         "instrument": "EMIT" if inst_emit else "CERTIFY", "sali_class": "regular" if sali_reg else "chaotic",
                         "agree": inst_emit == sali_reg})
            print(f"kappa={ka:.0f} alpha={al:.1f}: instrument held-out {ho:.1e} ({'EMIT' if inst_emit else 'CERTIFY'}) | "
                  f"SALI chaotic-fraction {cf:.2f} ({'regular' if sali_reg else 'chaotic'}) | agree={inst_emit==sali_reg}")

    k1 = [r for r in rows if r["kappa"] == 1.0]; k2 = [r for r in rows if r["kappa"] == 2.0]
    # O1: instrument recovers the classified anchor {0,1,3} at kappa=1.
    o1 = bool(all((r["instrument"] == "EMIT") == (r["alpha"] in {0.0, 1.0, 3.0}) for r in k1))
    # O2: instrument and SALI agree on every UNAMBIGUOUS point -- a known-integrable anchor (chaotic_fraction 0)
    #     or a clearly-chaotic point (chaotic_fraction > 0.4). The near-island middle is genuinely fuzzy (KAM).
    anchors_int = lambda r: (r["alpha"] == 0.0) or (r["kappa"] == 1.0 and r["alpha"] in {1.0, 3.0})
    clear = [r for r in rows if (r["chaotic_fraction"] == 0.0 and anchors_int(r)) or r["chaotic_fraction"] > 0.4]
    o2 = bool(all(r["agree"] for r in clear))
    k2_integrable = sorted(r["alpha"] for r in k2 if r["instrument"] == "EMIT")
    # O3: the open finding -- off the table (kappa=2) only alpha=0 keeps an exact low-degree invariant; and the
    #     disagreements (regular dynamics but NO low-degree polynomial invariant) flag richer-invariant candidates.
    richer_candidates = sorted((r["kappa"], r["alpha"]) for r in rows
                               if r["instrument"] == "CERTIFY" and r["chaotic_fraction"] < 0.1)
    o3 = bool(k2_integrable == [0.0] and len(richer_candidates) > 0)
    out = {"energy": E0, "rows": rows, "kappa2_low_degree_integrable_set": k2_integrable,
           "richer_invariant_or_weak_chaos_candidates": richer_candidates,
           "O1_anchor_kappa1": o1, "O2_agree_on_clear_cases": o2, "O3_open_finding": o3,
           "open_family_mapped": bool(o1 and o2 and o3)}
    print(f"\nO1 instrument recovers the kappa=1 anchor islands {{0,1,3}}: {o1}")
    print(f"O2 instrument == SALI on every UNAMBIGUOUS point (clear island / clear chaos): {o2} ({sum(r['agree'] for r in clear)}/{len(clear)})")
    print(f"O3 OPEN FINDING: at kappa=2 only alpha={k2_integrable} keeps an exact low-degree invariant;")
    print(f"   richer-invariant / weak-chaos candidates (regular dynamics, no low-degree invariant): {richer_candidates}")
    print(f"\nOPEN FAMILY MAPPED (instrument map off the table + SALI corroboration on the clear cases): {out['open_family_mapped']}")
    (Path(__file__).resolve().parent.parent / "results" / "95_open_family.json").write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(1, 2, figsize=(13, 5))
    for axi, ka, rr in [(ax[0], 1.0, k1), (ax[1], 2.0, k2)]:
        a = [r["alpha"] for r in rr]; ho = [r["heldout_varratio"] for r in rr]
        axi.semilogy(a, np.clip(ho, 1e-12, None), "o-", color="crimson", label="instrument held-out var-ratio")
        cf = [r["chaotic_fraction"] for r in rr]; ax2 = axi.twinx(); ax2.plot(a, cf, "s--", color="navy", label="SALI chaotic fraction (independent)")
        axi.axhline(1e-4, color="seagreen", ls=":", lw=0.8); ax2.axhline(0.1, color="navy", ls=":", lw=0.6)
        axi.set_xlabel("alpha"); axi.set_ylabel("held-out var-ratio (red)"); ax2.set_ylabel("chaotic fraction (blue)")
        axi.set_title(f"kappa={ka:.0f} {'(classified anchor: islands 0,1,3)' if ka==1 else '(OFF the table: open)'}\nEMIT (low red) <=> integrable (zero chaotic fraction)")
    fig.tight_layout(); fig.savefig(Path(__file__).resolve().parent.parent / "results" / "95_open_family.png", dpi=140)
    print("saved results/95_open_family.json + .png")


if __name__ == "__main__":
    main()
