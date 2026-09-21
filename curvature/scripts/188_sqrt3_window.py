"""Step 188 — is §187's unexplained 1.73 ratio a FIT-WINDOW artifact?

§187 reported two independent xi estimates whose ratio saturates near sqrt(3) at large xi, and deliberately
declined to narrate a mechanism. Pre-registered in notes/sqrt3_prereg.md before this file existed.

THE DESIGN IS THE WHOLE POINT: a window artifact MUST depend on the window. Arm A holds the chain, the
correlation matrix and the mass grid completely fixed and varies ONLY which points the line is fitted to.
Identical C(r); different W. Both outcomes were named in advance, and one of them refutes my own suspect.
"""

import json
import os
import sys
from importlib import import_module
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "2")        # be civil: two heavy jobs from sibling repos are live
os.environ.setdefault("MKL_NUM_THREADS", "2")

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
from curvlib import RESULTS

s32 = import_module("32_entangle_geometry")
s41 = import_module("41_hyperbolic_adS")


def envelope(C, n):
    """|C(r)| on even separations from the midpoint -- the same quantity §187 fits."""
    i0 = n // 2
    rs = np.arange(2, n // 2, 2)
    c = np.array([abs(C[i0, (i0 + r) % n]) for r in rs])
    return rs, c


def fit_exp(rs, c, w):
    """§187's fit, with the window as an explicit argument instead of hardwired to N/4."""
    keep = (rs < w) & (c > 1e-12)
    rs_f, c_f = rs[keep], c[keep]
    if len(rs_f) < 6:
        return np.nan
    keep2 = c_f > c_f[0] * 1e-6
    rs_f, c_f = rs_f[keep2], c_f[keep2]
    if len(rs_f) < 6:
        return np.nan
    A = np.vstack([rs_f, np.ones_like(rs_f)]).T
    sol, *_ = np.linalg.lstsq(A, np.log(c_f), rcond=None)
    return np.nan if sol[0] >= 0 else float(-1.0 / sol[0])


def fit_exp_power(rs, c, w):
    """Arm B: log|C| = A - r/xi - alpha*log r. Returns (xi, alpha)."""
    keep = (rs < w) & (c > 1e-12)
    rs_f, c_f = rs[keep], c[keep]
    if len(rs_f) < 8:
        return np.nan, np.nan
    A = np.vstack([-rs_f, -np.log(rs_f), np.ones_like(rs_f)]).T
    sol, *_ = np.linalg.lstsq(A, np.log(c_f), rcond=None)
    inv_xi, alpha = sol[0], sol[1]
    return (np.nan if inv_xi <= 0 else float(1.0 / inv_xi)), float(alpha)


def saturated_ratio(n, windows, masses):
    """For each window: ratio (1/m)/xi_measured in the LARGE-xi (saturated) regime."""
    out = {}
    cache = {}
    for m in masses:
        C = s32.corr_matrix(s41.chain_hop_gapped(n, m, periodic=True))
        cache[m] = envelope(C, n)
    for w in windows:
        rat = []
        for m in masses:                                  # masses ASCENDING -> xi DESCENDING
            rs, c = cache[m]
            xi = fit_exp(rs, c, w)
            if np.isfinite(xi) and xi > 0:
                rat.append((1.0 / m) / xi)
        # SATURATED = LARGEST xi = SMALLEST mass, i.e. the HEAD of this list. The first version took rat[-5:],
        # which is the largest masses -- the opposite end, where the ratio has not saturated at all. The L1
        # control caught it: W=N/4 returned 1.6345 against §187's 1.7270. A bug in the run built to test a
        # regularity, found by the control that run was required to pass.
        out[w] = float(np.median(rat[:5])) if len(rat) >= 5 else None
    return out, cache


def main():
    N = 512
    # masses chosen so xi = 1/m is FAR above every window -> the saturated regime
    masses = np.logspace(np.log10(1e-4), np.log10(2e-3), 9)
    windows = [N // 8, N // 4, N // 2, 3 * N // 4]

    print("ARM A -- same chain, same C(r), ONLY the fit window changes")
    ratios, cache = saturated_ratio(N, windows, masses)
    for w in windows:
        rs0, c0 = cache[masses[0]]
        keep = (rs0 < w) & (c0 > 1e-12)
        rsk, ck = rs0[keep], c0[keep]
        npts = int((ck > ck[0] * 1e-6).sum()) if len(ck) else 0
        print(f"   W = {w:<5} (N/{N/w:.3g})   saturated ratio (1/m)/xi_meas = {ratios[w]:.4f}   "
              f"[{npts} points actually fitted]")

    # --- known-fail control: W = N/4 must reproduce §187 ---
    ref = json.loads((RESULTS / "187_xistar_located.json").read_text())
    ref_ratio = ref["xi_estimate_ratio_at_star"]
    a_at_quarter = ratios[N // 4]
    l1 = bool(a_at_quarter is not None and abs(a_at_quarter - ref_ratio) / ref_ratio < 0.05)
    print(f"\n   L1 control: W=N/4 gives {a_at_quarter:.4f} vs §187's {ref_ratio:.4f} -> {'OK' if l1 else 'FAIL'}")

    spread = (max(ratios.values()) - min(ratios.values())) / min(ratios.values())
    window_dependent = bool(spread > 0.05)

    print("\nARM B -- refit with a power-law prefactor on the same data (W = N/4)")
    b_rows = []
    for m in masses[:5]:
        rs, c = cache[m]
        xi_p, alpha = fit_exp_power(rs, c, N // 4)
        xi_e = fit_exp(rs, c, N // 4)
        b_rows.append({"m": float(m), "xi_exp_only": xi_e, "xi_with_power": xi_p, "alpha": alpha,
                       "ratio_exp": (1 / m) / xi_e if np.isfinite(xi_e) else None,
                       "ratio_power": (1 / m) / xi_p if np.isfinite(xi_p) else None})
        print(f"   m={m:<10.4g} xi_exp={xi_e:<10.4g} xi_pow={xi_p:<10.4g} alpha={alpha:<8.3f} "
              f"ratio_exp={(1/m)/xi_e:<7.3f} ratio_pow={(1/m)/xi_p if np.isfinite(xi_p) else float('nan'):.3f}")

    # ARM C IS CONFOUNDED AND IS REPORTED AS SUCH. Varying N at a fixed window FRACTION changes the window AND
    # the finite-size scale together. At these masses xi = 1/m >> N for every N, so the chain's own length also
    # sets the decay -- the two cannot be separated here. Its near-flatness across N is NOT explained and is
    # NOT used to support the verdict, which rests on arm A alone (identical chain, identical C(r), only the
    # fitted points differ). Recorded rather than quietly dropped.
    print("\nARM C -- vary N at fixed window fraction N/4  [CONFOUNDED: window and finite size move together]")
    c_rows = {}
    for n in [256, 512, 1024]:
        ms = np.logspace(np.log10(1e-4), np.log10(2e-3), 5)
        r, _ = saturated_ratio(n, [n // 4], ms)
        c_rows[n] = r[n // 4]
        print(f"   N = {n:<6} saturated ratio = {r[n//4]:.4f}")

    # ---- ARM D: is the "agreement point" (ratio = 1) a property of the CHAIN or of the WINDOW? -----------
    # Added after arm A, because arm A's result implies it: if the ratio is window-set everywhere, the place
    # where the two estimates AGREE must be window-set too. That contradicts a claim I had already sent a peer
    # ("the two methods calibrate each other somewhere, and that somewhere is inside the band").
    ms_d = np.logspace(np.log10(1e-4), np.log10(0.2), 40)
    cache_d = {m: envelope(s32.corr_matrix(s41.chain_hop_gapped(N, m, periodic=True)), N) for m in ms_d}
    d_rows = []
    print("\nARM D -- where the two estimates AGREE (ratio = 1), as a function of window")
    for w in [N // 8, N // 4, N // 2]:
        xs, rr = [], []
        for m in ms_d:
            r, c = cache_d[m]
            xi = fit_exp(r, c, w)
            if np.isfinite(xi) and xi > 0:
                xs.append(xi); rr.append((1.0 / m) / xi)
        xs, rr = np.array(xs), np.array(rr)
        o = np.argsort(xs); xs, rr = xs[o], rr[o]
        k = np.where((rr[:-1] - 1) * (rr[1:] - 1) < 0)[0]
        if len(k):
            i = k[-1]
            f = (1 - rr[i]) / (rr[i + 1] - rr[i])
            xc = float(xs[i] + f * (xs[i + 1] - xs[i]))
            d_rows.append({"W": w, "xi_at_crossing": xc, "xi_cross_over_W": xc / w})
            print(f"   W = {w:<5} xi at crossing = {xc:<10.4g} xi_cross/W = {xc/w:.3f}")
    d_const = (max(r["xi_cross_over_W"] for r in d_rows) / min(r["xi_cross_over_W"] for r in d_rows)
               if len(d_rows) > 1 else None)

    out = {
        "prereg": "notes/sqrt3_prereg.md (committed before this script existed)",
        "armD_crossing": d_rows,
        "armD_xi_cross_over_W_spread": d_const,
        "armD_note": ("The AGREEMENT point sits at xi ~ W/2 and moves with the window. It is a property of the "
                      "fit, not of the chain. This REFUTES a claim already sent to a peer -- that the two "
                      "methods calibrate each other somewhere inside the band -- and the refutation came from "
                      "the same run, within the hour."),
        "L1_reproduces_187": l1, "L1_ref_ratio": ref_ratio, "L1_here": a_at_quarter,
        "armA_window_ratios": {str(k): v for k, v in ratios.items()},
        "armA_relative_spread": spread,
        "armA_window_dependent": window_dependent,
        "armB": b_rows,
        "armC_N_ratios": {str(k): v for k, v in c_rows.items()},
        "armC_confounded": True,
        "armC_note": ("Varying N at fixed window FRACTION moves the window and the finite-size scale together; "
                      "at these masses xi = 1/m >> N for every N, so the chain length also sets the decay. Its "
                      "near-flatness is UNEXPLAINED and supports nothing. The verdict rests on arm A, which "
                      "holds the chain fixed and varies only which points are fitted."),
        "sqrt3": float(np.sqrt(3)),
    }
    if not l1:
        out["verdict"] = ("NO CONCLUSION -- the L1 control failed: this harness does not reproduce §187's "
                          "ratio at W=N/4, so nothing here bears on §187's regularity.")
    elif window_dependent:
        out["verdict"] = (f"WINDOW ARTIFACT CONFIRMED: the saturated ratio moves by {spread*100:.1f}% across "
                          f"fit windows on IDENTICAL data ({ratios}). The 1.73 is a property of where the line "
                          f"was fitted, not of the chain. sqrt(3) is a coincidence of the N/4 window.")
    else:
        out["verdict"] = (f"WINDOW ARTIFACT REFUTED: the saturated ratio is unchanged (spread "
                          f"{spread*100:.2f}%) across fit windows spanning {min(windows)}..{max(windows)} on "
                          f"identical data. My own suspect is excluded. The ratio is a property of the "
                          f"correlation function, not of the fit. sqrt(3) REMAINS UNEXPLAINED -- now with one "
                          f"candidate mechanism eliminated rather than a story attached.")
    (RESULTS / "188_sqrt3_window.json").write_text(json.dumps(out, indent=2))
    print("\n" + out["verdict"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
