"""Step 195c -- diagnosis of the §195 G0 run-2 failure (phase-random null 0.90 at one level). Exploratory: it informs
amendment 3 and gates nothing. No TS is read.

Question: which per-orbit statistic separates GENUINE invariant structure {Kerr exact, Henon-Heiles KAM tori (and ZV
delta=2 regular orbits when added)} from {phase-random surrogates, spliced orbits, Henon-Heiles chaos} WITHOUT
calibrating to Kerr exactness? TS delta=2 has no exact extra integral, so a Kerr-exactness criterion would read every
TS torus as chaotic by construction (The Bridge's circularity point).

Per orbit:
  M1 frozen verdict, r*, ladder v{2,4,6} (195 code unchanged)
  M2 ladder shape: v2/v4, v4/v6
  M3 window consistency: invariant direction fitted on two disjoint windows; |cosine| of the coefficient vectors
  M4 horizon growth: fit on an early window, value-centred error on test windows at increasing offsets
  M5 Laskar frequency drift: dominant frequency of each coordinate, first half vs second half (relative change)
  M6 spectral line concentration: fraction of power in the top 20 FFT bins (per coordinate, mean)
Kerr orbits are FRESH seeds at the run-2 failing level (offset from run 2's grid), so they stay usable for nothing
else; amendment-3 validation must use levels unseen in run 2.

    .venv314ob/bin/python scripts/195c_diagnose_regular_band.py [--smoke]
"""

import argparse
import json
import sys
from importlib import import_module
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

m = import_module("195_invariant_learnability")         # sets BLAS threads = 1, imports 193 (OpenBLAS tripwire)
import numpy as np                                        # noqa: E402

m94, m94b = m.m94, m.m94b
RESULTS = Path(__file__).resolve().parent.parent / "results"
T = m.T_PRIMARY
DT_S = m.DT * m.STRIDE
DT_HH = 0.0025        # HH's period ~6 vs Kerr's ~10^2: dt 0.05 drifts H by 3e-4 over T; 0.0025 gives ~1e-10 (measured)


def fit_dir(ref, Z):
    """The invariant direction fitted on Z at this rung (same algebra as Reference.score): coefficients c, train mean."""
    tot, n = 0.0, 0
    for Zc in m._chunks(Z, 4000):
        F = ref.scaled(Zc)
        tot = tot + F.sum(0)
        n += len(F)
    mu = tot / n
    Rw = m._stream_qr(ref.scaled(Zc) - mu for Zc in m._chunks(Z, 4000))
    _, _, V2t = np.linalg.svd(Rw @ ref.W, full_matrices=False)
    return ref.W @ V2t[-1], mu


def value_err(ref, c, mu, Z):
    v = np.concatenate([ref.scaled(Zc) @ c for Zc in m._chunks(Z, 4000)])
    return float(np.mean((v - float(mu @ c)) ** 2)) * ref.NR


def dom_freq(x):
    return m94b.freqs(x, DT_S)


def measures(Z, refs, noise):
    sc = m.orbit_scores(Z, refs, T)["primary"]
    out = {"verdict": m.verdict(sc, noise), "r_star": sc.get("r_star"), "g_star": sc.get("g_star"),
           "dstar": sc.get("dstar"), "v": sc.get("v")}
    if not sc:
        return out
    v = {int(k): x for k, x in sc["v"].items()}
    out["M2"] = {f"v{a}/v{b}": v[a] / max(v[b], 1e-300) for a, b in ((2, 4), (4, 6)) if a in v and b in v}
    ref = refs[int(sc["dstar"])]
    n = min(len(Z), int(round(T / DT_S)))
    w = n // 8
    cA, muA = fit_dir(ref, Z[:w])
    cB, _ = fit_dir(ref, Z[4 * w:5 * w])
    out["M3_cos"] = float(abs(cA @ cB) / (np.linalg.norm(cA) * np.linalg.norm(cB) + 1e-300))
    out["M4"] = {f"off{k}": value_err(ref, cA, muA, Z[k * w:(k + 1) * w]) for k in (1, 2, 4, 7)}
    out["M4_growth"] = out["M4"]["off7"] / max(out["M4"]["off1"], 1e-300)
    h = n // 2
    drift = []
    for j in range(4):
        f1, f2 = dom_freq(Z[:h, j]), dom_freq(Z[h:2 * h, j])
        drift.append(abs(f2 - f1) / max(abs(f1), 1e-300))
    out["M5_drift"] = float(np.median(drift))
    conc = []
    for j in range(4):
        P = np.abs(np.fft.rfft((Z[:n, j] - Z[:n, j].mean()) * np.hanning(n))) ** 2
        conc.append(float(np.sort(P)[-20:].sum() / P.sum()))
    out["M6_lineconc"] = float(np.mean(conc))
    return out


def surviving(res, Tw):
    acc = m.accepted_mask(res, Tw)
    return [g for g in np.where(acc)[0] if not np.isfinite(res["t_plunge"][g])]


def kerr_set(n):
    sts, _ = m94.spacetimes("t1o3")
    st = sts["Kerr"]
    L = -m94.l_sep(st, 0.97, -1) * (1 - 0.01)          # the run-2 failing level: pro, eps = -0.01
    mdl = st.at(0.97, L)
    reg = m94.seed_region(st, 0.97, L)
    step = (reg[1] - reg[0]) / (n - 1)
    r = np.linspace(reg[0] + step / 3, reg[1] - step / 3, n)  # offset from run 2's uniform grid
    z, _ = m94.seeds(mdl, r)
    res = m94.integrate(mdl, z, T, m.DT, m.STRIDE, twin=False)
    return [m.valid(res, g) for g in surviving(res, T)], True


def hh_set(E, n, seed):
    hh = m94.HenonHeiles(E)
    z = hh.launch(n, np.random.default_rng(seed))
    res = m94.integrate(hh, z, T, DT_HH, int(round(DT_S / DT_HH)), twin=True)   # same 0.5 sampling
    keep = surviving(res, T)
    return [m.valid(res, g) for g in keep], [float(res["ftle"][g]) for g in keep], \
        [m94b.section_coverage(m.valid(res, g))[1] for g in keep]


def refs_from(orbits, geo, seed):
    rng = np.random.default_rng(seed)
    k = int(np.ceil(m.R_POINTS / len(orbits)))
    R = np.concatenate([Z[np.sort(rng.choice(len(Z), size=min(k, len(Z)), replace=False))] for Z in orbits])
    return m.build_refs(R, geo)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    nK, nH, nPR = (8, 12, 2) if a.smoke else (40, 80, 5)
    rng = np.random.default_rng(195)
    out = {"T": T, "smoke": a.smoke, "groups": {}}

    def add(group, rows):
        out["groups"].setdefault(group, []).extend(rows)
        vs = [r["verdict"] for r in rows]
        print(group, len(rows), {v: vs.count(v) for v in set(vs)}, flush=True)

    K, geo = kerr_set(nK)
    refK = refs_from(K, True, 1)
    base = [measures(Z, refK, None) for Z in K]
    noiseK = float(np.percentile([r["r_star"] for r in base if r.get("r_star")], 99))
    for r in base:
        r["verdict"] = m.verdict({"v": r["v"], "r_star": r["r_star"], "r_train": r["r_star"] / max(r["g_star"], 1e-300)},
                                 noiseK)
    out["noise_kerr"] = noiseK
    add("kerr_real", base)
    prs = []
    for Z, src in zip(K, base):
        for _ in range(nPR):
            r = measures(m.phase_randomize(Z, rng), refK, noiseK)
            r["src_M6"] = src.get("M6_lineconc")              # The Bridge: source line-concentration as covariate
            prs.append(r)
    add("kerr_phase_random", prs)
    sp = []
    for i in range(len(K) - len(K) // 2):
        A, B = K[i], K[i + len(K) // 2]
        nn = min(len(A), len(B))
        sp.append(measures(np.concatenate([A[:nn // 2], B[nn // 2:nn]]), refK, noiseK))
    add("kerr_splice", sp)

    for E, tag in ((1 / 12, "hh_low"), (0.1657, "hh_high")):
        Zs, ftle, gap = hh_set(E, nH, 7 if tag == "hh_low" else 8)
        refH = refs_from(Zs, False, 2)
        rows = []
        for Z, f, g in zip(Zs, ftle, gap):
            r = measures(Z, refH, None)
            r.update({"ftle": f, "section_gap": g})
            rows.append(r)
        add(tag, rows)
        if tag == "hh_low":
            hp = []
            for Z, src in zip(Zs[:max(4, nH // 4)], rows):
                r = measures(m.phase_randomize(Z, rng), refH, None)
                r["src_M6"] = src.get("M6_lineconc")
                hp.append(r)
            add("hh_low_phase_random", hp)
        out[f"{tag}_ftle_median"] = float(np.median(ftle))

    name = "195c_diagnose_smoke.json" if a.smoke else "195c_diagnose.json"
    (RESULTS / name).write_text(json.dumps(out, default=float))
    print("saved", name, flush=True)


if __name__ == "__main__":
    main()
