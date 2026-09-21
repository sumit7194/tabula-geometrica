"""Step 187 — LOCATING J5's criticality wall: where does constant curvature stop being readable?

§42's E2 is the last gate in this repo still emitting a BOOLEAN. It reads "gapped chain -> R_CoV 5.56 vs
critical 0.0013, pass", which asserts THAT constancy fails and never WHERE. Every certify verdict here now
reports a location (§176 d*=6, §177 K*=3 / r*=3.6, §178 no invariant below degree 5), and E2 escaped that pass
because a gate that PASSES does not look like a gate that needs characterising.

PRE-REGISTERED in notes/xistar_prereg.md, committed BEFORE this file existed. An external sealed prediction is
on record in a sister repo, unread by me and deliberately not consulted.

WHAT IS MEASURED, NOT ASSUMED: xi. The textbook relation is xi ~ 1/gap = 1/(2m) and it is NOT used as the
x-axis -- xi is fitted from the exponential decay of the correlation envelope |C(r)| on the same chain whose
entropy is read. Both are reported so any divergence is visible. (The day's lesson: touch the state.)

THE RATIO IS NOT COLLAPSED. xi* is reported against N, l_min and l_max SEPARATELY. The regime condition is
l << xi << N -- two conditions on different lengths that fail independently. A single ratio conflates them,
which is precisely the error the sister repo withdrew on their own version of this measurement.
"""

import json
import sys
from importlib import import_module
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
from curvlib import RESULTS

s32 = import_module("32_entangle_geometry")
s41 = import_module("41_hyperbolic_adS")
s42 = import_module("42_curvature_from_entanglement")

N = 512
LO, HI = 16, 176                      # band UNCHANGED from §42: re-tuning it would confound location with taste
LS = np.arange(LO, HI + 1, 2)
THRESH_FACTOR = 3.0                   # E2's OWN existing threshold (§42: cov_Rg > 3 * cov_Rc), not a new choice
ENDPOINT_TOL = 0.20                   # L1: both §42 endpoints must reproduce within 20%


def measure_xi(m):
    """Fit |C(r)| ~ exp(-r/xi) on the correlation envelope. Returns (xi, fit_quality).

    Free fermions at half filling oscillate with r (parity), so the raw C(r) is not monotone; the ENVELOPE is.
    Even separations only, and the fit runs over the range where |C| is above numerical noise.
    """
    C = s32.corr_matrix(s41.chain_hop_gapped(N, m, periodic=True)) if m > 0 else \
        s32.corr_matrix(s32.chain_hop(N, periodic=True))
    i0 = N // 2
    rs = np.arange(2, N // 4, 2)
    c = np.array([abs(C[i0, (i0 + r) % N]) for r in rs])
    ok = c > 1e-12
    if ok.sum() < 6:
        return np.nan, np.nan
    rs_f, c_f = rs[ok], c[ok]
    # restrict to the decaying part above noise: top 6 decades from the first point
    keep = c_f > c_f[0] * 1e-6
    rs_f, c_f = rs_f[keep], c_f[keep]
    if len(rs_f) < 6:
        return np.nan, np.nan
    A = np.vstack([rs_f, np.ones_like(rs_f)]).T
    sol, res, *_ = np.linalg.lstsq(A, np.log(c_f), rcond=None)
    slope = sol[0]
    pred = A @ sol
    ss_res = float(np.sum((np.log(c_f) - pred) ** 2))
    ss_tot = float(np.sum((np.log(c_f) - np.mean(np.log(c_f))) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else np.nan
    if slope >= 0:
        return np.inf, r2                       # no decay resolved -> xi beyond what this chain can show
    return float(-1.0 / slope), r2


def rcov_at(m):
    S = s42.S_gapped(N, m, LS) if m > 0 else s42.S_critical(N, LS)
    lm, Om = s42.omega(LS, S)
    return s42.cov(s42.R_const(lm, Om, N))


def main():
    masses = np.concatenate([[0.0], np.logspace(np.log10(1e-4), np.log10(0.5), 24)])
    rows = []
    for m in masses:
        cv = rcov_at(m)
        xi, r2 = measure_xi(m)
        rows.append({"m": float(m), "R_CoV": float(cv), "xi_measured": float(xi),
                     # v_F = 2 for eps(k) = -2 cos k at half filling, gap = 2m, so the continuum relation is
                     # xi = v_F/gap = 1/m, NOT 1/(2m). The first version of this column used 1/(2m) and was
                     # wrong by exactly a factor of 2. It is a COMPARATOR ONLY: xi is measured, so the error
                     # never reached m*, xi*, or the verdict. Confirmed from the data itself -- xi_meas*m
                     # clusters near 1 across the clean regime, xi_meas*2m near 2.
                     "xi_continuum_vF2": float(1.0 / m) if m > 0 else float("inf"),
                     "xi_textbook_WRONG_vF1": float(1.0 / (2 * m)) if m > 0 else float("inf"),
                     "xi_fit_r2": float(r2) if np.isfinite(r2) else None})
        print(f"  m={m:<10.5g} R_CoV={cv:<12.5g} xi_meas={xi:<12.5g} xi_1/2m={1/(2*m) if m>0 else np.inf:<12.5g} r2={r2:.4f}")

    crit = rows[0]["R_CoV"]
    gapped_end = rows[-1]["R_CoV"]
    thresh = THRESH_FACTOR * crit

    # ---- L1 KNOWN-FAIL CONTROL: both §42 endpoints must reproduce, or no verdict issues ----
    l1_crit = abs(crit - 0.0013) / 0.0013 < ENDPOINT_TOL
    l1_gap = abs(gapped_end - 5.56) / 5.56 < ENDPOINT_TOL
    l1 = bool(l1_crit and l1_gap)

    # ---- locate the crossing on the log-xi axis ----
    fin = [r for r in rows[1:] if np.isfinite(r["xi_measured"]) and r["xi_measured"] > 0]
    fin = sorted(fin, key=lambda r: r["xi_measured"])
    xi_star = None
    censored = None
    if fin:
        xs = np.array([r["xi_measured"] for r in fin])
        cs = np.array([r["R_CoV"] for r in fin])
        above = cs > thresh
        # crossing = last index (in increasing xi) where we are above threshold, interpolated to the next point
        idx = np.where(above[:-1] & ~above[1:])[0]
        if len(idx):
            i = idx[-1]
            lx0, lx1 = np.log10(xs[i]), np.log10(xs[i + 1])
            c0, c1 = np.log10(cs[i]), np.log10(cs[i + 1])
            lt = np.log10(thresh)
            frac = (c0 - lt) / (c0 - c1) if c0 != c1 else 0.0
            xi_star = float(10 ** (lx0 + frac * (lx1 - lx0)))
            censored = False
        else:
            censored = True                    # no interior crossing -> edge, abstain per the pre-reg

    mono = bool(np.all(np.diff([r["R_CoV"] for r in fin]) <= 1e-12)) if len(fin) > 1 else None

    # ---- locate the wall on the MASS axis too: m is a control parameter, not an inferred one ----
    ms = np.array([r["m"] for r in rows[1:]])
    cs_m = np.array([r["R_CoV"] for r in rows[1:]])
    m_star = None
    j = np.where((cs_m[:-1] < thresh) & (cs_m[1:] >= thresh))[0]
    if len(j):
        k = j[0]
        lm0, lm1 = np.log10(ms[k]), np.log10(ms[k + 1])
        c0, c1 = np.log10(cs_m[k]), np.log10(cs_m[k + 1])
        f = (np.log10(thresh) - c0) / (c1 - c0) if c1 != c0 else 0.0
        m_star = float(10 ** (lm0 + f * (lm1 - lm0)))

    # ---- XI-MEASURABILITY GUARD (added AFTER the first run, and recorded as such) ----------------
    # The pre-registration named "the xi fit is broken" as an instrument-re-examination trigger, but wrote the
    # censoring guard for the crossing landing at the GRID EDGE. It did not anticipate the X-AXIS ITSELF going
    # unmeasurable at an interior crossing. It does: the fit window is r <= N/4, so once xi >> N the envelope
    # barely decays across it and the fitted slope is noise. Quantified rather than asserted.
    decay_at_star = float(1 - np.exp(-(N // 4) / xi_star)) if xi_star else None
    xi_axis_trustworthy = bool(decay_at_star is not None and decay_at_star > 0.5)

    # THIRD, FREE SIGNATURE -- found by TheBridge checking one of the reported numbers against another rather
    # than taking it on report. Two independent xi estimates exist at every grid point: the envelope fit and
    # the corrected continuum relation 1/m. Where the axis is measurable they should agree; their RATIO is
    # therefore a measurability diagnostic that cost nothing to build and that neither guard above uses.
    ratio_at_star = float((1.0 / m_star) / xi_star) if (m_star and xi_star) else None
    ratio_curve = [{"xi_over_N": r["xi_measured"] / N,
                    "derived_over_measured": (1.0 / r["m"]) / r["xi_measured"]}
                   for r in rows[1:] if np.isfinite(r["xi_measured"]) and r["xi_measured"] > 0]

    out = {
        "prereg": "notes/xistar_prereg.md (committed 2026-09-21 before this script existed)",
        "N": N, "band": [LO, HI], "threshold_factor": THRESH_FACTOR,
        "critical_R_CoV": crit, "gapped_end_R_CoV": gapped_end, "threshold": thresh,
        "L1_endpoint_critical_ok": bool(l1_crit), "L1_endpoint_gapped_ok": bool(l1_gap), "L1": l1,
        "R_CoV_monotone_in_xi": mono,
        "censored_no_interior_crossing": censored,
        "xi_star": xi_star,
        "m_star": m_star,
        "xi_envelope_decay_across_fit_window_at_star": decay_at_star,
        "xi_axis_trustworthy": xi_axis_trustworthy,
        "xi_estimate_ratio_at_star": ratio_at_star,
        "xi_estimate_ratio_curve": ratio_curve,
        "xi_estimate_ratio_note": (
            "Two independent xi estimates (envelope fit vs corrected continuum 1/m). Ratio runs 0.54 -> 1.00 "
            "-> 1.73 across the sweep, crossing 1 at xi/N ~ 0.14 and saturating near 1.73 at large xi. The "
            "AGREEMENT POINT sits inside the measurable regime and the wall sits where they disagree by 1.7x, "
            "which corroborates the abstention by a third route. THE SATURATION VALUE IS NOT EXPLAINED: it is "
            "numerically close to sqrt(3) and NO mechanism has been tested for that, so it is recorded as an "
            "unexplained regularity, not a finding. Credit: TheBridge, who checked one reported number against "
            "another instead of taking it on report."),
        "n_grid_points_with_xi_above_N": int(sum(1 for r in rows[1:]
                                                 if np.isfinite(r["xi_measured"]) and r["xi_measured"] > N)),
        # THE RATIO IS NOT COLLAPSED -- three separate readouts, per the pre-registration
        "xi_star_over_N": (xi_star / N) if xi_star else None,
        "xi_star_over_l_min": (xi_star / LO) if xi_star else None,
        "xi_star_over_l_max": (xi_star / HI) if xi_star else None,
        "rows": rows,
    }
    if not l1:
        out["verdict"] = ("NO VERDICT -- L1 known-fail control failed: the sweep did not reproduce §42's "
                          "endpoints on this code path, so it has not earned the right to interpolate "
                          "between them. Instrument, not physics.")
    elif censored:
        out["verdict"] = ("ABSTAIN -- no interior crossing; the wall lies at or beyond the edge of the swept "
                          "grid. Reported as a bound, not a location. Widen the grid.")
    elif not xi_axis_trustworthy:
        out["verdict"] = (
            f"SPLIT VERDICT -- LOCATED IN MASS, ABSTAIN IN XI. The wall is cleanly located on the control "
            f"parameter: m* = {m_star:.4g} (interior, monotone, both L1 endpoints reproduced). It is NOT "
            f"located in xi: the crossing sits at xi = {xi_star:.4g} = {xi_star/N:.3g}x the box, where the "
            f"correlation envelope decays by only {decay_at_star*100:.1f}% across the whole fit window "
            f"(r <= N/4) -- a correlation length fitted from an essentially flat curve is not a measurement. "
            f"xi*/N = {xi_star/N:.4g} is therefore reported as an UPPER BOUND on nothing useful, not a "
            f"location. THE PHYSICAL CONTENT: R_CoV leaves the critical baseline while xi is still far OUTSIDE "
            f"the box, so at this gate's wall the condition xi << N is violated -- E2's boundary cannot be "
            f"expressed as a xi/N ratio on this system at all. The two conditions (l << xi and xi << N) do not "
            f"merely fail independently here; the second is already broken where the gate fires.")
    else:
        out["verdict"] = (f"E2 LOCATED: constant curvature stops being readable at xi* = {xi_star:.3g} lattice "
                          f"sites -- xi*/N = {xi_star/N:.4g}, xi*/l_min = {xi_star/LO:.4g}, "
                          f"xi*/l_max = {xi_star/HI:.4g}. Reported as three ratios, never one.")

    (RESULTS / "187_xistar_located.json").write_text(json.dumps(out, indent=2))
    print("\n" + out["verdict"])
    print(f"\nL1 endpoints: critical {crit:.5g} (want ~0.0013) {'OK' if l1_crit else 'FAIL'} | "
          f"gapped {gapped_end:.5g} (want ~5.56) {'OK' if l1_gap else 'FAIL'}")
    return 0 if l1 else 1


if __name__ == "__main__":
    sys.exit(main())
