"""Step 195b -- root-cause check of the §195 G0 failure. Kerr only, so no TS is read.

Hypothesis 1: the two false-CHAOTIC Kerr orbits are integration round-off. Re-integrating at dt/2 should cut r*
               by >= 16x (RK4 error ~ dt^4, so variance ~ dt^8).
Hypothesis 2: the splice null failed because the test half was centred on its OWN mean. A global invariant (Carter)
               is constant on any orbit, so "constant on the test half" is satisfied by the WRONG orbit. Measuring the
               test half about the TRAIN mean ("the invariant keeps its value") should reject splices.
The reference cloud is rebuilt from 60 stage-1 seeds of each level (approximate R; diagnostic only).
"""

import json
import sys
from importlib import import_module
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np

from curvlib import RESULTS

m = import_module("195_invariant_learnability")
m94 = m.m94


def level(sense, eps):
    sts, _ = m94.spacetimes("t1o3")
    st = sts["Kerr"]
    L = sense * m94.l_sep(st, 0.97, sense) * (1 + eps)
    mdl = st.at(0.97, L)
    reg = m94.seed_region(st, 0.97, L)
    z, r0 = m94.seeds(mdl, np.linspace(reg[0], reg[1], 60))
    res = m94.integrate(mdl, z, m.T_PRIMARY, m.DT, m.STRIDE, twin=False)
    acc = m.accepted_mask(res, m.T_PRIMARY)
    rng = np.random.default_rng(1)
    pts = np.concatenate([m.valid(res, g) for g in np.where(acc)[0]])
    R = pts[np.sort(rng.choice(len(pts), size=min(m.R_POINTS, len(pts)), replace=False))]
    return mdl, m.build_refs(R, True), res, acc


def score_value(ref, Ztr, Zte):
    """Like Reference.score, but r_test measured about the TRAIN mean (the invariant keeps its value)."""
    tot, n = 0.0, 0
    for Zc in m._chunks(Ztr, 4000):
        F = ref.scaled(Zc)
        tot = tot + F.sum(0)
        n += len(F)
    mtr = tot / n
    Rw = m._stream_qr(ref.scaled(Zc) - mtr for Zc in m._chunks(Ztr, 4000))
    _, S2, V2t = np.linalg.svd(Rw @ ref.W, full_matrices=False)
    c = ref.W @ V2t[-1]
    vtr_mean = float(mtr @ c)
    v = np.concatenate([ref.scaled(Zc) @ c for Zc in m._chunks(Zte, 4000)])
    return float(S2[-1] ** 2 / n * ref.NR), float(np.mean((v - vtr_mean) ** 2) * ref.NR), float(np.var(v) * ref.NR)


def main():
    out = {}
    # H1: re-integrate the two false-CHAOTIC orbits at dt and dt/2
    for sense, eps, r0 in ((-1, 0.005, 27.197), (1, -0.01, 5.867)):
        mdl, refs, _, _ = level(sense, eps)
        rows = json.loads((m.OUT / f"G0_Kerr_t1o3_E0.97_{'pro' if sense < 0 else 'retro'}_eps{eps:+}.json").read_text())["rows"]
        r_exact = min((r["r0"] for r in rows), key=lambda x: abs(x - r0))
        z, _ = m94.seeds(mdl, np.array([r_exact]))
        rec = {}
        for dt, stride in ((m.DT, m.STRIDE), (m.DT / 2, 2 * m.STRIDE)):
            res = m94.integrate(mdl, z, m.T_PRIMARY, dt, stride, twin=False)
            sc = m.orbit_scores(m.valid(res, 0), refs, m.T_PRIMARY)["primary"]
            rec[f"dt{dt}"] = {"r_star": sc["r_star"], "r_train": sc["r_train"], "dstar": sc["dstar"],
                              "hdrift": float(res["hdrift"][0])}
        rec["drop"] = rec[f"dt{m.DT}"]["r_star"] / rec[f"dt{m.DT / 2}"]["r_star"]
        out[f"H1_{'pro' if sense < 0 else 'retro'}_eps{eps:+}_r0{r_exact:.3f}"] = rec
        print("H1", r_exact, rec, flush=True)
    # H2: splices on the level where the null failed, scored about the train mean
    mdl, refs, res, acc = level(-1, -0.01)
    surv = [g for g in np.where(acc)[0] if not np.isfinite(res["t_plunge"][g])]
    sp = []
    for i in range(min(20, len(surv) - 10)):
        A, B = m.valid(res, surv[i]), m.valid(res, surv[i + 10])
        n = min(len(A), len(B))
        own = m.orbit_scores(A, refs, m.T_PRIMARY)["primary"]
        ref = refs[int(own["dstar"])]
        rtr, r_val, r_own = score_value(ref, A[:n // 2], B[n // 2:n])
        _, r_val_self, r_own_self = score_value(ref, A[:n // 2], A[n // 2:n])
        sp.append({"splice_valuecentred": r_val, "splice_selfcentred": r_own, "real_valuecentred": r_val_self,
                   "real_selfcentred": r_own_self, "r_train": rtr})
    out["H2"] = sp
    for s in sp[:8]:
        print("H2", {k: f"{v:.1e}" for k, v in s.items()}, flush=True)
    (RESULTS / "195b_diagnose_g0.json").write_text(json.dumps(out, indent=1, default=float))


if __name__ == "__main__":
    main()
