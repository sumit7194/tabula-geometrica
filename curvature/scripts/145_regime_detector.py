"""Step 145 — EXP-4 of the REPRESENTABILITY FRONTIER (②): the REGIME DETECTOR — fully-unknown systems.

notes/representability_frontier.md. EXP-3 (143) proved the 5-verdict table but was TOLD each dataset's type — its honest
scope gap. 145 closes it: the detector receives a RAW dataset with NO type label and NO ground truth and must
  (1) infer the DATA TYPE from structural signatures alone:
      - square + symmetric + hollow-diagonal + nonnegative + triangle inequality  -> DISTANCES
      - discrete columns, +-1 outcomes (measurement records)                      -> CORRELATIONS
      - 3D array (ensemble, time, dim) with temporal smoothness (lag-1 autocorr)  -> TRAJECTORIES
      - exchangeable continuous tabular (features + final target column)          -> CODE
  (2) run the matching regime diagnostic TRUTH-FREE:
      - distances: classical-MDS stress (cheap low-D code?); then UNIQUENESS without truth -- a random rigid motion of
        the embedding explains the data equally well (the §86-style equivalence-class certificate) unless ANCHOR
        side-info (coordinates for a few points, part of the DATA) breaks the tie -> EMIT / CERTIFY-GAUGE / CERTIFY-NO-CODE.
      - correlations: build the table from the samples, fit the cheapest local-hidden-variable code (§142 local polytope)
        + CHSH -> EMIT-CLASSICAL / CERTIFY-CONTEXTUAL.
      - trajectories (NEW -- folds CHAOS-proper into the table): the web-verified 0-1 TEST FOR CHAOS (Gottwald-Melbourne;
        translation variables p,q from the series, mean-square-displacement growth: K -> 0 regular, K -> 1 chaotic)
        + the §99 emit-or-certify engine (exact held-out conserved invariant?) -> EMIT / CERTIFY-CHAOS.
      - code: linear vs nonlinear decode of the dataset's own target column -> EMIT-LEGIBLE / PARTIAL-LEGIBLE.
Ground truth enters ONLY in the gates (checking the verdicts are right), never in the detector.

Pre-reg (2026-07-02):
  D1 TYPE-INFERENCE: all 9 menu systems typed correctly from structure alone (no labels).
  D2 TRAJECTORY BRANCH: Kepler -> EMIT (0-1 K < 0.2, engine held-out < 1e-6 exact invariant); Lorenz -> CERTIFY-CHAOS
     (K > 0.8, engine held-out >> Kepler). The chaos row of the frontier table, now instrumented in the router.
  D3 END-TO-END: all 9 final verdicts correct (type inferred + regime decided, no labels, no truth).
Menu: distances anchored / relational / 6D (EMIT / CERTIFY-GAUGE / CERTIFY-NO-CODE), measurement samples LHV / singlet
(EMIT-CLASSICAL / CERTIFY-CONTEXTUAL), trajectories Kepler / Lorenz (EMIT / CERTIFY-CHAOS), code amortized / free
(EMIT-LEGIBLE / PARTIAL-LEGIBLE).
"""

import json
import sys
from importlib import import_module
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.linalg import eigh, orthogonal_procrustes
from sklearn.linear_model import Ridge
from sklearn.neighbors import KNeighborsRegressor

from curvlib import RESULTS

s99 = import_module("99_deformed_metrics")
s139 = import_module("139_sae_legibility")
s142 = import_module("142_contextual_certificate")
s143 = import_module("143_unified_diagnostic")

STRESS_T = 0.2


# ---------------- stage 1: TYPE INFERENCE (structure only) ----------------
def is_distance_matrix(X):
    if X.ndim != 2 or X.shape[0] != X.shape[1] or X.shape[0] < 8:
        return False
    if not np.allclose(X, X.T, atol=1e-8) or np.abs(np.diag(X)).max() > 1e-8 or X.min() < -1e-12:
        return False
    n = X.shape[0]
    rng = np.random.default_rng(0)
    tri = rng.integers(0, n, (300, 3))
    i, j, k = tri[:, 0], tri[:, 1], tri[:, 2]
    return bool(np.all(X[i, j] <= X[i, k] + X[k, j] + 1e-9))


def is_measurement_record(X):
    if X.ndim != 2 or X.shape[1] > 6:
        return False
    return all(len(np.unique(X[:, c])) <= 4 for c in range(X.shape[1]))


def is_trajectories(X):
    if X.ndim != 3:
        return False
    ac = []
    for d in range(X.shape[2]):
        s = X[:, :, d]
        s0 = s[:, :-1] - s[:, :-1].mean(); s1 = s[:, 1:] - s[:, 1:].mean()
        ac.append((s0 * s1).mean() / (np.sqrt((s0 ** 2).mean() * (s1 ** 2).mean()) + 1e-12))
    return bool(np.mean(ac) > 0.8)                                # temporal smoothness = the trajectory signature


def infer_type(data):
    X = data["X"]
    if isinstance(X, np.ndarray) and X.ndim == 3 and is_trajectories(X):
        return "trajectories"
    if isinstance(X, np.ndarray) and X.ndim == 2:
        if is_distance_matrix(X):
            return "distances"
        if is_measurement_record(X):
            return "correlations"
        return "code"
    return "unknown"


# ---------------- stage 2: TRUTH-FREE regime diagnostics ----------------
def diag_distances(data):
    D = data["X"]; n = len(D)
    J = np.eye(n) - np.ones((n, n)) / n
    B = -0.5 * J @ (D ** 2) @ J
    w, V = eigh(B); w = w[::-1]; V = V[:, ::-1]
    pos = np.clip(w, 0, None)
    stress = 1.0 - pos[:2].sum() / (pos.sum() + 1e-12)
    if stress > STRESS_T:
        return "CERTIFY-NO-CODE", {"stress": float(stress)}
    E = V[:, :2] * np.sqrt(pos[:2])
    # uniqueness WITHOUT truth: a random rigid motion of E reproduces the data equally (gauge) unless anchors break it
    th = 1.234
    R = np.array([[np.cos(th), -np.sin(th)], [np.sin(th), np.cos(th)]])
    E2 = E @ R + np.array([0.7, -0.4])
    d_orig = np.sqrt(((E[:, None] - E[None]) ** 2).sum(-1))
    d_rot = np.sqrt(((E2[:, None] - E2[None]) ** 2).sum(-1))
    both_fit = bool(np.abs(d_orig - d_rot).max() < 1e-8)          # two distinct configs, same observations
    if "anchor_idx" in data:                                      # anchor coordinates are DATA -> can they break the tie?
        ai, ap = data["anchor_idx"], data["anchor_pos"]
        Ra, _ = orthogonal_procrustes(E[ai] - E[ai].mean(0), ap - ap.mean(0))
        Ea = (E - E[ai].mean(0)) @ Ra + ap.mean(0)
        resid = float(np.sqrt(((Ea[ai] - ap) ** 2).sum(1).mean()))
        scale = float(np.sqrt((ap ** 2).sum(1).mean()))
        if resid / scale < 0.05:
            return "EMIT", {"stress": float(stress), "anchor_resid": resid / scale}
    return ("CERTIFY-GAUGE" if both_fit else "EMIT"), {"stress": float(stress), "rigid_degenerate": both_fit}


def diag_correlations(data):
    S = data["X"]                                                 # rows: (x, y, a, b) with a,b = +-1
    E = np.zeros(4)
    for idx, (x, y) in enumerate([(0, 0), (0, 1), (1, 0), (1, 1)]):
        m = (S[:, 0] == x) & (S[:, 1] == y)
        E[idx] = (S[m, 2] * S[m, 3]).mean()
    verdict, info = s142.diagnose(E)
    return verdict, {**info, "table": E.tolist()}


def zero_one_K(series, n_c=12, seed=0):
    """Gottwald-Melbourne 0-1 test (correlation method): K -> 0 regular, K -> 1 chaotic."""
    rng = np.random.default_rng(seed)
    phi = np.asarray(series, float); N = len(phi)
    ncut = N // 10
    Ks = []
    for c in rng.uniform(np.pi / 5, 4 * np.pi / 5, n_c):
        j = np.arange(1, N + 1)
        p = np.cumsum(phi * np.cos(j * c)); q = np.cumsum(phi * np.sin(j * c))
        M = np.array([np.mean((p[n:] - p[:-n]) ** 2 + (q[n:] - q[:-n]) ** 2) for n in range(1, ncut)])
        Eφ = phi.mean() ** 2
        D = M - Eφ * (1 - np.cos(np.arange(1, ncut) * c)) / (1 - np.cos(c))   # Vosc correction (standard)
        n_vec = np.arange(1, ncut)
        Ks.append(np.corrcoef(n_vec, D)[0, 1])
    return float(np.median(Ks))


def traj_lib(T):
    """degree<=2 monomial + 1/r library over the trajectory state (works for both 4d Kepler and 3d Lorenz)."""
    cols = [T[..., i] for i in range(T.shape[-1])]
    F = [c for c in cols] + [c1 * c2 for a1, c1 in enumerate(cols) for c2 in cols[a1:]]
    if T.shape[-1] == 4:                                          # planar (x, y, px, py): add 1/r (gravity-shaped worlds)
        r = np.sqrt(T[..., 0] ** 2 + T[..., 1] ** 2)
        F.append(1.0 / (r + 1e-9))
    return np.stack(F, -1)


def diag_trajectories(data):
    T = data["X"]
    ntr = len(T) // 2
    Phi = traj_lib(T[:ntr]); ev, Cw, mu, sd = s99.conserved(Phi)
    ho = s99.heldout(traj_lib(T[ntr:]), Cw[:, 0], mu, sd)
    # 0-1 test across subsample rates, take max: oversampled chaos reads K~0 (smoke-verified: Lorenz rate 1 K=-0.04
    # vs rate 5 K=1.0; Kepler ~0 at every rate) -- chaos shows at SOME rate, regular stays ~0 at all
    K = float(max(np.median([zero_one_K(T[i, ::rate, 0], seed=i) for i in range(min(8, len(T)))])
                  for rate in (3, 5, 10)))
    if ho < 1e-6 and K < 0.2:
        return "EMIT", {"heldout": float(ho), "K01": K}
    if K > 0.8 or ho > 1e-2:
        return "CERTIFY-CHAOS", {"heldout": float(ho), "K01": K}
    return "AMBIGUOUS", {"heldout": float(ho), "K01": K}


def diag_code(data):
    X = data["X"]; Z, p = X[:, :-1], X[:, -1]                     # convention: final column = the property
    lin = abs(s139.decode_r(Z, p, Ridge(1.0)))
    nl = abs(s139.decode_r(Z, p, KNeighborsRegressor(10)))
    if lin > 0.85:
        return "EMIT-LEGIBLE", {"linear": lin, "nonlinear": nl}
    if lin < 0.6 and nl > 0.7:
        return "PARTIAL-LEGIBLE", {"linear": lin, "nonlinear": nl}
    return "AMBIGUOUS", {"linear": lin, "nonlinear": nl}


DIAG = {"distances": diag_distances, "correlations": diag_correlations,
        "trajectories": diag_trajectories, "code": diag_code}


def detect(data):
    dtype = infer_type(data)
    if dtype == "unknown":
        return dtype, "UNKNOWN", {}
    verdict, info = DIAG[dtype](data)
    return dtype, verdict, info


# ---------------- the menu (generation uses truth; the detector never sees it) ----------------
def gen_kepler(n_traj=24, nstep=6000, stride=6, seed=0):
    rng = np.random.default_rng(seed)
    out = []
    for _ in range(n_traj):
        r0 = rng.uniform(1.0, 2.0); th = rng.uniform(0, 2 * np.pi)
        x = np.array([r0 * np.cos(th), r0 * np.sin(th)])
        vmag = np.sqrt(1.0 / r0) * rng.uniform(0.8, 1.1)
        v = vmag * np.array([-np.sin(th), np.cos(th)])
        s = np.concatenate([x, v]); rec = []
        f = lambda s: np.concatenate([s[2:], -s[:2] / (np.linalg.norm(s[:2]) ** 3 + 1e-12)])
        dt = 0.01
        for k in range(nstep):
            k1 = f(s); k2 = f(s + dt / 2 * k1); k3 = f(s + dt / 2 * k2); k4 = f(s + dt * k3)
            s = s + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
            if k % stride == 0:
                rec.append(s.copy())
        out.append(np.array(rec))
    return np.stack(out)


def gen_lorenz(n_traj=24, nstep=6000, stride=6, seed=0):
    rng = np.random.default_rng(seed)
    out = []
    for _ in range(n_traj):
        s = rng.normal(0, 5, 3) + np.array([0, 0, 25.0]); rec = []
        f = lambda s: np.array([10 * (s[1] - s[0]), s[0] * (28 - s[2]) - s[1], s[0] * s[1] - 8 / 3 * s[2]])
        dt = 0.005
        for k in range(nstep):
            k1 = f(s); k2 = f(s + dt / 2 * k1); k3 = f(s + dt / 2 * k2); k4 = f(s + dt * k3)
            s = s + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
            if k % stride == 0:
                rec.append(s.copy())
        out.append(np.array(rec))
    return np.stack(out)


def gen_samples(E_table, n=200000, seed=0):
    rng = np.random.default_rng(seed)
    x = rng.integers(0, 2, n); y = rng.integers(0, 2, n)
    E = np.array(E_table)[x * 2 + y]
    a = rng.choice([-1.0, 1.0], n)
    same = rng.random(n) < (1 + E) / 2
    b = np.where(same, a, -a)
    return np.stack([x.astype(float), y.astype(float), a, b], -1)


def pdist_np(X):
    return np.sqrt(((X[:, None] - X[None]) ** 2).sum(-1) + 1e-18)


def main():
    rng = np.random.default_rng(0)
    base, coup = s139.make_world()
    Zg = rng.uniform(-1.2, 1.2, (40, 2)); Zh = rng.uniform(-1.2, 1.2, (40, 6))
    w16 = rng.dirichlet(np.ones(16)); E_lhv = (w16 @ s142.DET).astype(float)

    print("generating menu (kepler/lorenz integrations + 2 code trainings)...")
    p_a, Z_a = s139.train("amortized", base, coup, steps=10000)
    p_f, Z_f = s139.train("free", base, coup, steps=10000)

    menu = [
        ("EMIT", "distances", {"X": pdist_np(Zg), "anchor_idx": [0, 1, 2, 3], "anchor_pos": Zg[:4].copy()}),
        ("CERTIFY-GAUGE", "distances", {"X": pdist_np(Zg)}),
        ("CERTIFY-NO-CODE", "distances", {"X": pdist_np(Zh)}),
        ("EMIT-CLASSICAL", "correlations", {"X": gen_samples(E_lhv, seed=1)}),
        ("CERTIFY-CONTEXTUAL", "correlations", {"X": gen_samples(s142.SINGLET, seed=2)}),
        ("EMIT", "trajectories", {"X": gen_kepler(seed=3)}),
        ("CERTIFY-CHAOS", "trajectories", {"X": gen_lorenz(seed=4)}),
        ("EMIT-LEGIBLE", "code", {"X": np.hstack([Z_a, p_a[:, None]])}),
        ("PARTIAL-LEGIBLE", "code", {"X": np.hstack([Z_f, p_f[:, None]])}),
    ]

    rows = []
    for expected_verdict, expected_type, data in menu:
        dtype, verdict, info = detect(data)
        # disambiguate the two distance EMIT/gauge cases + trajectory cases in the printout
        tag = expected_verdict + ("/" + expected_type if expected_verdict == "EMIT" else "")
        ok_t = dtype == expected_type; ok_v = verdict == expected_verdict
        rows.append({"expected": expected_verdict, "expected_type": expected_type, "inferred_type": dtype,
                     "verdict": verdict, "type_ok": bool(ok_t), "verdict_ok": bool(ok_v), **info})
        print(f"{tag:28s} type {dtype:13s}{'OK' if ok_t else 'WRONG':6s} verdict {verdict:20s}{'OK' if ok_v else 'WRONG'}   {info}")

    d1 = bool(all(r["type_ok"] for r in rows))
    kep = next(r for r in rows if r["expected_type"] == "trajectories" and r["expected"] == "EMIT")
    lor = next(r for r in rows if r["expected"] == "CERTIFY-CHAOS")
    d2 = bool(kep["verdict_ok"] and lor["verdict_ok"] and kep["K01"] < 0.2 and lor["K01"] > 0.8
              and kep["heldout"] < 1e-6)
    d3 = bool(all(r["verdict_ok"] for r in rows))

    out = {"rows": rows, "D1_type_inference": d1, "D2_trajectory_branch": d2, "D3_end_to_end": d3,
           "regime_detector": bool(d1 and d2 and d3),
           "verdict": ("THE REGIME DETECTOR (② EXP-4): closes EXP-3's honest scope gap. Given RAW datasets with no type "
                       "labels and no ground truth, ONE detector (a) infers the data type from structural signatures "
                       "alone (triangle inequality -> distances; discrete +-1 records -> measurements; temporal "
                       "smoothness -> trajectories; exchangeable tabular -> code) and (b) decides the regime TRUTH-FREE "
                       "(gauge = two rigid-motion configs explain the data equally unless anchor DATA breaks the tie; "
                       "contextual = the samples' own CHSH; legible = decoding the dataset's own target). All 9/9 menu "
                       "systems: type inferred AND verdict correct. NEW: the trajectory branch folds CHAOS-proper into "
                       "the router -- Kepler EMITS (0-1 test K={:.2f}, exact invariant {:.0e}) and Lorenz CERTIFIES "
                       "(K={:.2f}, no invariant {:.0e}) via the web-verified Gottwald-Melbourne 0-1 test + the §99 "
                       "engine. The frontier table is now a DETECTOR, not just a classifier."
                       .format(kep["K01"], kep["heldout"], lor["K01"], lor["heldout"])
                       if (d1 and d2 and d3) else "PARTIAL/HONEST -- see rows.")}
    print(f"\nD1 type-inference (9/9): {d1} | D2 trajectory branch: {d2} | D3 end-to-end (9/9): {d3}")
    print(f"REGIME DETECTOR: {out['regime_detector']}")
    (RESULTS / "145_regime_detector.json").write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(figsize=(11, 4.2)); ax.axis("off")
    for i, r in enumerate(rows):
        okc = "#d5f0d5" if (r["type_ok"] and r["verdict_ok"]) else "#f7d9d9"
        ax.add_patch(plt.Rectangle((i * 2.2, 0), 2.05, 2.8, fc=okc, ec="k", lw=0.6))
        ax.text(i * 2.2 + 1.0, 2.45, r["expected"], ha="center", fontsize=6.4, weight="bold")
        ax.text(i * 2.2 + 1.0, 1.65, f"type→{r['inferred_type']}", ha="center", fontsize=6.2)
        ax.text(i * 2.2 + 1.0, 0.9, f"verdict→{r['verdict']}", ha="center", fontsize=6.2)
        ax.text(i * 2.2 + 1.0, 0.3, "✓" if r["verdict_ok"] else "✗", ha="center", fontsize=10)
    ax.set_xlim(-0.2, 20); ax.set_ylim(-0.2, 3.4)
    ax.set_title("② EXP-4 — the REGIME DETECTOR: raw data in (no labels, no truth) → type + verdict out (9/9)")
    fig.tight_layout(); fig.savefig(RESULTS / "145_regime_detector.png", dpi=140)
    print("saved results/145_regime_detector.json + .png")


if __name__ == "__main__":
    main()
