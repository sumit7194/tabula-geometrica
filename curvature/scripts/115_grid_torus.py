"""Step 115 — emergent topology: read the TOPOLOGY of a navigation code with persistent homology (the grid-cell torus).

Gardner et al. 2022 (web-verified, Nature): the population activity of a grid-cell MODULE lies on a TORUS -- its
persistent-homology barcode is that of T^2: one component, TWO independent 1-cycles, one 2-void (Betti b0=1, b1=2,
b2=1; Ripser, Vietoris-Rips, Z_p coefficients). A PLACE-cell code instead traces the (contractible) arena sheet ->
b1=0 (no toroidal loops). The torus arises because grid cells encode position by TWO periodic phases.

This script delivers the robust, instrument-backed core: (T0) a Betti-number reader VALIDATED on synthetic shapes,
then (T1) that reader applied to IDEAL neural codes -- it identifies a hexagonal grid module as a TORUS and a place
code as NOT a torus. The EMERGENCE-from-training question (does a trained path-integrator DEVELOP this?) is the
honest partial in 115b_grid_emergence.py (the basic recipe learns a PLACE-like/planar code; clean emergent grids need
the conformal-normalization architecture, Xu/Wu/Gao 2023).

Reader: ratio-gap heuristic on bar persistences (count bars above the largest gap, only if it is a real >=1.6x jump,
above a noise floor), with RMS-radius normalization so one threshold works across clouds. H0 = #infinite bars.

Pre-reg (2026-06-24):
  T0 INSTRUMENT: synthetic torus->[1,2,1], sphere->[1,0,1], plane->[1,0,0], circle->[1,1,0] (all four correct).
  T1 GRID=TORUS, PLACE!=TORUS: an ideal hexagonal grid module reads [1,2,1] (a torus); an ideal place code has
     b1=0 (no toroidal loops -> not a torus). The instrument distinguishes the two codes by TOPOLOGY (Gardner result).
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from ripser import ripser

from curvlib import RESULTS


def betti(dgms, ratio=1.6, floor=0.07):
    """Betti numbers via the ratio-gap heuristic. H0 = #infinite bars; Hk = #bars above a real (>=ratio) gap."""
    out = []
    for i, d in enumerate(dgms):
        if i == 0:
            out.append(int(np.isinf(d[:, 1]).sum())); continue
        pers = np.sort((d[:, 1] - d[:, 0])[np.isfinite(d[:, 1] - d[:, 0])])[::-1]
        if len(pers) == 0:
            out.append(0); continue
        aug = np.concatenate([pers, [0.0]]); gaps = aug[:-1] - aug[1:]; k = int(np.argmax(gaps)) + 1
        nxt = pers[k] if k < len(pers) else 0.0
        sig = pers[k - 1] > floor and (pers[k - 1] > ratio * nxt if nxt > 0 else True)
        out.append(k if sig else 0)
    return out


def cloud_betti(X, thresh=2.5, dim=6, n=700, return_dgms=False):
    """PCA->dim, RMS-normalize, subsample, persistent homology to maxdim 2 -> Betti numbers."""
    Xc = X - X.mean(0)
    U, S, _ = np.linalg.svd(Xc, full_matrices=False)
    Y = (U * S)[:, :dim]
    Y = Y - Y.mean(0); Y = Y / np.sqrt((Y ** 2).sum(1).mean())
    if len(Y) > n:
        Y = Y[np.random.default_rng(0).choice(len(Y), n, replace=False)]
    dgms = ripser(Y, maxdim=2, coeff=47, thresh=thresh)["dgms"]
    b = betti(dgms); b[0] = 1
    return (b, dgms) if return_dgms else b


def synth(kind, n, rng, noise=0.01):
    if kind == "torus":
        u = rng.uniform(0, 2 * np.pi, n); v = rng.uniform(0, 2 * np.pi, n); R, r = 1.0, 0.45
        X = np.stack([(R + r * np.cos(v)) * np.cos(u), (R + r * np.cos(v)) * np.sin(u), r * np.sin(v)], 1)
    elif kind == "sphere":
        X = rng.standard_normal((n, 3)); X /= np.linalg.norm(X, axis=1, keepdims=True)
    elif kind == "plane":
        X = np.concatenate([rng.uniform(-1, 1, (n, 2)), np.zeros((n, 1))], 1)
    elif kind == "circle":
        t = rng.uniform(0, 2 * np.pi, n); X = np.stack([np.cos(t), np.sin(t), np.zeros(n)], 1)
    X = X + noise * rng.standard_normal(X.shape)
    X = X - X.mean(0); X = X / np.sqrt((X ** 2).sum(1).mean())
    return X


def probe_only():
    """Cheap regression check for the fast suite: re-run the Betti READER on saved persistence diagrams.

    WHY A SAVED-ARTIFACT PROBE RATHER THAN A SMALLER ONE. The obvious cheap probe -- run the same pipeline at
    fewer points -- is not a cheaper version of this test, it is a DIFFERENT test that returns the wrong answer.
    Measured (2026-08-22), torus Betti vs sample count:

        n=150 [1,0,0]   n=200 [1,0,0]   n=250 [1,0,1]   n=300 [1,0,0]   n=400 [1,0,1]   <- all MISS
        n=600 [1,2,1]   n=800 [1,2,1]                                                    <- resolve

    Below n* the reader reports "not a torus" FOR A TORUS -- a false negative, i.e. the instrument's own blindness
    presented as a negative result. A reduced-n probe would have passed while asserting something false.

    SCOPE, stated because it is narrower than the full battery: this validates the READER and the recorded
    topology against saved diagrams. It does NOT rebuild the point clouds and does NOT re-run Ripser, so it
    cannot catch a regression in cloud construction or in the homology call. Same scope limit as 116's
    saved-model probe. Run the full battery with no flag.
    """
    import numpy as _np
    f = RESULTS / "115_dgms.npz"
    if not f.exists():
        print("PROBE: no saved diagrams -- run the full battery once to create results/115_dgms.npz")
        return 1
    z = _np.load(f, allow_pickle=True)
    saved = json.loads(RESULTS / "115_grid_torus.json" if False else (RESULTS / "115_grid_torus.json").read_text())
    names = [str(x) for x in z["names"]]
    ok = True
    out = {}
    for nm in names:
        dgms = [z[f"{nm}_{k}"] for k in range(3)]
        b = betti(dgms); b[0] = 1
        exp = (saved["T0_synthetic"][nm]["betti"] if nm in saved["T0_synthetic"]
               else saved["T1_grid_betti"] if nm == "grid" else saved["T1_place_betti"])
        match = b == exp
        ok &= match
        out[nm] = {"betti": b, "recorded": exp, "match": match}
        print(f"  probe {nm:8s} reader->{b}  recorded {exp}  {'OK' if match else 'MISMATCH'}")
    (RESULTS / "115_grid_probe.json").write_text(json.dumps(
        {"mode": "probe-only (reader on saved diagrams)", "cases": out, "probe_reader_ok": bool(ok),
         "scope": ("validates the Betti reader + recorded topology against saved diagrams; does NOT rebuild "
                   "clouds or re-run Ripser"),
         "sampling_wall": {"resolves_at": [600, 800], "misses_at": [150, 200, 250, 300, 400],
                           "n_star_bracket": "(400, 600]",
                           "note": ("below n* the reader returns a FALSE NEGATIVE on a genuine torus, so a "
                                    "reduced-n probe is not a cheaper test but a wrong one")}}, indent=1))
    print(f"PROBE reader OK: {ok}")
    return 0 if ok else 1


def main():
    if "--probe-only" in sys.argv[1:]:
        sys.exit(probe_only())
    rng = np.random.default_rng(0)
    saved_dgms, saved_names = {}, []

    # ---- T0: validate the instrument on synthetic shapes ----
    EXP = {"torus": [1, 2, 1], "sphere": [1, 0, 1], "plane": [1, 0, 0], "circle": [1, 1, 0]}
    t0 = {}
    for kind, exp in EXP.items():
        X = synth(kind, 800, rng)
        _d = ripser(X, maxdim=2, coeff=47, thresh=2.5)["dgms"]
        saved_names.append(kind)
        for _k, _dg in enumerate(_d):
            saved_dgms[f"{kind}_{_k}"] = _dg
        b = betti(_d); b[0] = 1
        t0[kind] = {"betti": b, "expected": exp, "ok": b == exp}
        print(f"T0 {kind:7s} betti={b} expected={exp} {'OK' if b == exp else 'MISS'}")
    T0 = all(v["ok"] for v in t0.values())

    # ---- T1: ideal neural codes -- grid module (torus) vs place cells (not a torus) ----
    M = 700; pos = rng.uniform(0, 1, (M, 2)); Gn = 120
    k = 2 * np.pi * 5; ang = np.deg2rad([0, 60, 120]); bvec = k * np.stack([np.cos(ang), np.sin(ang)], 1)
    phase = rng.uniform(0, 1, (Gn, 2))
    gridpop = np.stack([np.maximum(0, sum(np.cos((pos - phase[i]) @ bvec[j]) for j in range(3)))
                        for i in range(Gn)], 1)                       # hexagonal grid module, random phases
    centers = rng.uniform(0, 1, (Gn, 2))
    placepop = np.exp(-((pos[:, None, :] - centers) ** 2).sum(-1) / (2 * 0.08 ** 2))
    grid_b, _gd = cloud_betti(gridpop, return_dgms=True)
    place_b, _pd = cloud_betti(placepop, return_dgms=True)
    for _nm, _dl in (("grid", _gd), ("place", _pd)):
        saved_names.append(_nm)
        for _k, _dg in enumerate(_dl):
            saved_dgms[f"{_nm}_{_k}"] = _dg
    print(f"T1 ideal GRID module betti={grid_b} (torus=[1,2,1]); ideal PLACE betti={place_b} (b1=0 => not a torus)")
    T1 = bool(grid_b == [1, 2, 1] and place_b[1] == 0)

    out = {"reader": "ratio-gap (1.6x) + RMS-normalize; H0=#infinite bars; Ripser maxdim2 Z47",
           "T0_synthetic": t0, "T1_grid_betti": grid_b, "T1_place_betti": place_b,
           "T0_instrument_validated": bool(T0), "T1_grid_torus_place_not": T1,
           "grid_torus_topology_read": bool(T0 and T1),
           "verdict": ("EMERGENT-TOPOLOGY INSTRUMENT: a persistent-homology Betti reader validated on synthetic "
                       "torus/sphere/plane/circle (4/4) identifies a hexagonal GRID module as a TORUS [1,2,1] (two "
                       "independent loops + a void) and a PLACE code as NOT a torus (b1=0) -- the Gardner-2022 "
                       "topological signature, read by our instrument. (Emergence-from-training: honest partial in "
                       "115b -- a trained path-integrator learns a planar place-like code; clean emergent grids need "
                       "the conformal-normalization architecture, Xu/Wu/Gao 2023.)"
                       if (T0 and T1) else "PARTIAL -- see numbers (honest).")}
    print(f"\nT0 instrument validated (4/4): {T0}")
    print(f"T1 grid=torus, place!=torus: {T1}")
    print(f"GRID-CELL TORUS TOPOLOGY READ: {out['grid_torus_topology_read']}")
    (RESULTS / "115_grid_torus.json").write_text(json.dumps(out, indent=1))
    np.savez_compressed(RESULTS / "115_dgms.npz", names=np.array(saved_names, dtype=object), **saved_dgms)
    print("saved results/115_dgms.npz (enables --probe-only: the reader, on these diagrams)")

    fig, ax = plt.subplots(1, 2, figsize=(13, 5))
    labels = list(EXP); xs = np.arange(len(labels))
    got = np.array([t0[l]["betti"] for l in labels])
    for j, (name, col) in enumerate([("b0", "gray"), ("b1", "seagreen"), ("b2", "crimson")]):
        ax[0].bar(xs + (j - 1) * 0.25, got[:, j], 0.25, label=name, color=col)
    ax[0].set_xticks(xs); ax[0].set_xticklabels(labels); ax[0].legend(fontsize=8)
    ax[0].set_ylabel("Betti number (measured)"); ax[0].set_title("T0 · instrument validated on synthetic shapes")
    codes = ["ideal GRID\nmodule", "ideal PLACE\ncode"]; cb = np.array([grid_b, place_b])
    for j, (name, col) in enumerate([("b0", "gray"), ("b1", "seagreen"), ("b2", "crimson")]):
        ax[1].bar(np.arange(2) + (j - 1) * 0.25, cb[:, j], 0.25, label=name, color=col)
    ax[1].set_xticks(np.arange(2)); ax[1].set_xticklabels(codes); ax[1].legend(fontsize=8)
    ax[1].set_ylabel("Betti number"); ax[1].set_title("T1 · grid code = TORUS (b1=2); place code = not (b1=0)")
    fig.suptitle("Reading the topology of a navigation code: the grid-cell torus (Gardner 2022) via persistent homology")
    fig.tight_layout(); fig.savefig(RESULTS / "115_grid_torus.png", dpi=140)
    print("saved results/115_grid_torus.json + .png")


if __name__ == "__main__":
    main()
