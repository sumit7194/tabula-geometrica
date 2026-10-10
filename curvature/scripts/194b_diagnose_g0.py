"""Step 194b -- root-cause trace of the §194 G0 failure. Kerr only, so no TS is read.

Reconstructs the pilot's closed level (Kerr p=4/5, E=0.97, prograde, eps=+0.005; same deterministic seeds) and asks
of individual orbits:
  - how many radial periods and y=0 section crossings the 1e4-tau window gives;
  - the rotation number (polar/radial frequency ratio) and the nearest low-order resonance;
  - how well the window covers the orbit's section curve (max angular gap);
  - how the PCA slopes s3/s4 depend on the neighbourhood scale;
  - whether a 10x longer window (1e5 tau) brings s3 to the torus value of ~4.
"""

import json
import sys
from fractions import Fraction
from importlib import import_module
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np

from curvlib import RESULTS

m = import_module("194_orbit_dimension")
s193 = m.s193


def freqs(series, dt_s):
    """Dominant frequency (cycles per tau) of a 1-D series, via FFT with parabolic peak refinement."""
    x = series - series.mean()
    n = len(x)
    F = np.abs(np.fft.rfft(x * np.hanning(n)))
    F[0] = 0
    k = int(np.argmax(F[1:]) + 1)
    if 1 <= k < len(F) - 1:
        a, b, c = np.log(F[k - 1] + 1e-300), np.log(F[k] + 1e-300), np.log(F[k + 1] + 1e-300)
        k = k + 0.5 * (a - c) / (a - 2 * b + c)
    return k / (n * dt_s)


def section_coverage(Z):
    """Upward y=0 crossings; their angular coverage around the section curve's centroid in (x, p_x)."""
    y = Z[:, 1]
    idx = np.where((y[:-1] < 0) & (y[1:] >= 0))[0]
    if len(idx) < 3:
        return len(idx), None
    pts = Z[idx][:, [0, 2]]
    pts = (pts - pts.mean(0)) / (pts.std(0) + 1e-300)
    ang = np.sort(np.arctan2(pts[:, 1], pts[:, 0]))
    gaps = np.diff(np.concatenate([ang, [ang[0] + 2 * np.pi]]))
    return len(idx), float(gaps.max() / (2 * np.pi))


def nearest_resonance(w, qmax=12):
    best = min(((abs(w - Fraction(p, q)), p, q) for q in range(1, qmax + 1) for p in range(0, 4 * q + 1)),
               key=lambda t: t[0])
    return float(best[0]), f"{best[1]}/{best[2]}"


def slopes_by_scale(Z, rng):
    """s3, s4 for successive k-pairs (scale dependence) plus the pre-registered k-set."""
    out = {}
    for ks in ((10, 20), (20, 40), (40, 80), (80, 160), (160, 320), (20, 40, 80, 160)):
        s3, s4 = m.local_slopes(Z, rng, ks=ks)
        out[str(ks)] = [round(s3, 2) if np.isfinite(s3) else None, round(s4, 2) if np.isfinite(s4) else None]
    return out


def main():
    sts, spin = m.spacetimes("t1o3")
    st = sts["Kerr"]
    ls = m.l_sep(st, 0.97, -1)
    L = -ls * 1.005
    mdl = st.at(0.97, L)
    reg = m.seed_region(st, 0.97, L)
    z, r0 = m.seeds(mdl, np.linspace(reg[0], reg[1], m.N_STAGE1))
    pilot = json.loads((RESULTS / "194_pilot.json").read_text())
    lv = next(v for v in pilot["levels"] if v["dt"] == 0.05 and v["eps"] == 0.005)
    rows = lv["rows"]
    flagged = [i for i, r in enumerate(rows) if r.get("verdict") in ("CHAOTIC", "ABSTAIN")]
    regular = [i for i, r in enumerate(rows) if r.get("verdict") == "REGULAR"][::40][:5]
    pick = flagged + regular
    print(f"level L_sep={ls:.4f} L={L:.4f} region r={reg}; flagged {len(flagged)}, comparison regular {len(regular)}")
    rng = np.random.default_rng(3)
    out = {"level": {"L_sep": ls, "L": L, "E": 0.97, "region": reg}, "orbits": []}
    zs = z[:, pick]
    short = m.integrate(mdl, zs, 1.0e4, 0.05, 10, twin=False)
    long_ = m.integrate(mdl, zs, 1.0e5, 0.05, 10, twin=False)
    for j, i in enumerate(pick):
        Zs = short["samples"][:, :, j].T
        Zl = long_["samples"][:, :, j].T
        r_series = 1 + mdl.sig * Zs[:, 0]
        f_r, f_y = freqs(r_series, 0.5), freqs(Zs[:, 1], 0.5)
        w = f_y / f_r
        dres, res = nearest_resonance(w)
        n_cross_s, gap_s = section_coverage(Zs)
        n_cross_l, gap_l = section_coverage(Zl)
        rec = {"row": i, "r0": float(r0[i]), "pilot_verdict": rows[i]["verdict"],
               "pilot_s3": rows[i].get("s3@1.0"), "radial_periods_1e4": float(1e4 * f_r),
               "rotation_number": float(w), "nearest_resonance": res, "resonance_distance": dres,
               "section_crossings_1e4": n_cross_s, "section_max_gap_1e4": gap_s,
               "section_crossings_1e5": n_cross_l, "section_max_gap_1e5": gap_l,
               "slopes_1e4": slopes_by_scale(Zs, rng), "slopes_1e5": slopes_by_scale(Zl, rng),
               "verdict_1e5": m.verdict(*m.local_slopes(Zl, rng))}
        out["orbits"].append(rec)
        print(f"row {i:3d} r0={rec['r0']:.2f} {rec['pilot_verdict']:8s} s3={rec['pilot_s3']:.2f} | "
              f"radial periods {rec['radial_periods_1e4']:.0f}, w={w:.4f} ~{res} (d={dres:.4f}) | "
              f"crossings {n_cross_s} gap {gap_s} -> 1e5: {n_cross_l} gap {gap_l} | "
              f"s3 by scale 1e4 {[v[0] for v in rec['slopes_1e4'].values()]} | "
              f"1e5 {[v[0] for v in rec['slopes_1e5'].values()]} -> {rec['verdict_1e5']}", flush=True)
    (RESULTS / "194b_diagnose_g0.json").write_text(json.dumps(out, indent=1, default=float))
    print("saved results/194b_diagnose_g0.json")


if __name__ == "__main__":
    main()
