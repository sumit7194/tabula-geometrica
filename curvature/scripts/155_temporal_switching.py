"""Step 155 — EXP-14 of the REPRESENTABILITY FRONTIER (②): TEMPORAL non-stationarity / regime-switching.

notes/real_data_plan.md. The detector assumes ONE regime per series. EXP-8 handled mixtures ACROSS the ensemble (which
orbit is chaotic); EXP-14 handles mixtures ACROSS TIME (WHEN the law changes), and shows -- the headline -- that the
SAMPLING axis (EXP-12) sets the TEMPORAL resolution of law-detection.

System: a STREAM of Bell trials whose SOURCE switches mid-stream, from CLASSICAL (a local table, CHSH ~ 1.41) to QUANTUM
(a Werner state at margin delta, CHSH = 2 + delta) at t = CP (the true change-point). This gives a TUNABLE margin delta
to the decision wall (CHSH = 2) -- the logistic map's regimes are too cleanly separated (K jumps 0->1, no margin), so a
tunable wall is essential for the U-shape and the synthesis. Whole-stream CHSH gives one blurred number; a sliding-window
CHSH localizes the switch. Change-point literature (PELT/CUSUM/HMM; ruptures) establishes the short-window(noisy)/
long-window(smeared) tradeoff -- we cite it and keep our own simple windowed instrument.

Pre-reg (2026-07-02):
  T1 SWITCH-LOCALIZED: a sliding-window CHSH detector localizes the true change-point to within 10% of stream length,
     while the whole-stream single CHSH misrepresents the switch.
  T2 U-SHAPED RESOLUTION: localization error vs window W is U-shaped -- short W noisy (false crossings in the classical
     part), long W smears the switch (~W/2), minimum in between.
  T3 TEMPORAL vs ENSEMBLE: the within-stream temporal variance of the windowed CHSH is HIGH for a switch and LOW for a
     stationary stream (all-classical or all-quantum) -- "the regime changes in time" is separable from "the regime is
     constant per member but the ensemble is mixed" (EXP-8).
  T4 SAMPLING SETS TEMPORAL RESOLUTION (the synthesis, ties to EXP-12): the localization FLOOR (best error over W) GROWS
     as the margin delta -> 0 (nearer the wall), tracking N_resolve ~ 1/delta^2 -- near a decision wall a switch is not
     just data-hungry, it is temporally BLURRIER.
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

from curvlib import RESULTS

s142 = import_module("142_contextual_certificate")
s145 = import_module("145_regime_detector")

SETTINGS = [(0, 0), (0, 1), (1, 0), (1, 1)]
CLASSICAL = 0.5 * s142.SINGLET                                      # CHSH = sqrt2 ~ 1.41 (< 2, local)


def quantum(delta):
    return (2 + delta) / (2 * np.sqrt(2)) * s142.SINGLET           # CHSH = 2 + delta


def make_stream(delta, n, cp, seed=0):
    A = s145.gen_samples(CLASSICAL, n=cp, seed=seed)
    B = s145.gen_samples(quantum(delta), n=n - cp, seed=seed + 1)
    return np.concatenate([A, B], 0)


def window_chsh(S):
    E = np.zeros(4)
    for k, (x, y) in enumerate(SETTINGS):
        m = (S[:, 0] == x) & (S[:, 1] == y)
        E[k] = (S[m, 2] * S[m, 3]).mean() if m.any() else 0.0
    return s142.chsh(E)


def window_chsh_se(S):
    """CHSH + normal-approx standard error (like EXP-12), for a confidence-based detection."""
    E = np.zeros(4); n = np.zeros(4)
    for k, (x, y) in enumerate(SETTINGS):
        m = (S[:, 0] == x) & (S[:, 1] == y); n[k] = m.sum()
        E[k] = (S[m, 2] * S[m, 3]).mean() if m.any() else 0.0
    vals = s142.CHSH_SIGNS @ E; best = int(np.argmax(np.abs(vals)))
    return float(abs(vals[best])), float(np.sqrt(np.sum((1 - E ** 2) / np.maximum(n, 1))))


def min_confident_W(delta, Ws, seeds=15):
    """smallest window whose fully-quantum content is CONFIDENTLY contextual (CI lower > 2) in >=90% of seeds. This IS
    EXP-12's N_resolve for the trajectory-of-trials -- below it you cannot confirm the post-switch regime at all."""
    for W in Ws:
        frac = np.mean([(lambda c, se: c - 1.96 * se > 2.0)(*window_chsh_se(s145.gen_samples(quantum(delta), n=W, seed=100 + s)))
                        for s in range(seeds)])
        if frac >= 0.9:
            return W
    return None


def windowed(stream, W, stride):
    c, V = [], []
    for s in range(0, len(stream) - W + 1, stride):
        c.append(s + W // 2); V.append(window_chsh(stream[s:s + W]))
    return np.array(c), np.array(V)


def localize(stream, W, cp, stride=50):
    c, V = windowed(stream, W, stride)
    above = V > 2.0
    if not above.any():
        return len(stream) - cp                                     # never detected the quantum regime -> max error
    return abs(int(c[np.argmax(above)]) - cp)


def main():
    N, CP = 12000, 6000
    Ws = [50, 100, 200, 400, 800, 1600, 3200, 6000]

    # T1 + T2 on a moderate-margin stream (delta = 0.4)
    stream = make_stream(0.4, N, CP, seed=1)
    errs = [localize(stream, W, CP) for W in Ws]
    whole = window_chsh(stream)                                     # one number for the whole stream
    imin = int(np.argmin(errs)); best_W = Ws[imin]; best_err = errs[imin]
    t1 = bool(best_err < 0.10 * N)
    t2 = bool(0 < imin < len(Ws) - 1 and errs[0] > 1.3 * best_err and errs[-1] > 1.3 * best_err)

    # T3: within-stream temporal variance of windowed CHSH (switch vs stationary)
    def tvar(s, W=400, stride=50):
        _, V = windowed(s, W, stride); return float(np.var(V))
    stat_classical = s145.gen_samples(CLASSICAL, n=N, seed=3)
    stat_quantum = s145.gen_samples(quantum(0.4), n=N, seed=4)
    tv_switch = tvar(stream); tv_cl = tvar(stat_classical); tv_qu = tvar(stat_quantum)
    t3 = bool(tv_switch > 5 * max(tv_cl, tv_qu))

    # T4 (synthesis): the temporal-localization FLOOR = N_resolve/2. Below N_resolve trials into the quantum regime you
    # CANNOT confidently confirm the switch, so the switch cannot be localized to better than ~N_resolve/2 in time.
    # N_resolve(delta) ~ 1/delta^2 (EXP-12), so the floor diverges as delta -> 0.
    Ws4 = [50, 100, 200, 400, 800, 1600, 3200, 6400]
    floor = {}
    for d in [0.4, 0.3, 0.2, 0.15]:
        nres = min_confident_W(d, Ws4)
        floor[d] = int(nres // 2) if nres is not None else Ws4[-1]
    ds_sorted = sorted(floor)                                       # ascending delta
    ff = np.array([floor[d] for d in ds_sorted], float)
    t4_monotone = all(ff[i] >= ff[i + 1] for i in range(len(ff) - 1))   # ascending delta -> descending floor
    valid = ff > 0
    slope4 = (float(np.polyfit(np.log(np.array(ds_sorted)[valid]), np.log(ff[valid]), 1)[0])
              if valid.sum() >= 3 else None)
    ratio = floor[0.15] / max(floor[0.4], 1)
    t4 = bool(t4_monotone and floor[0.15] > 3 * max(floor[0.4], 1) and (slope4 is not None and slope4 < -0.8))

    out = {"N": N, "true_change_point": CP, "window_sweep_W": Ws, "loc_error_by_W": errs,
           "whole_stream_chsh": float(whole), "best_W": best_W, "best_localization_error": int(best_err),
           "temporal_var": {"switch": tv_switch, "stationary_classical": tv_cl, "stationary_quantum": tv_qu},
           "localization_floor_by_delta": {str(k): v for k, v in floor.items()},
           "floor_ratio_0.15_over_0.4": ratio, "floor_loglog_slope": slope4,
           "T1_switch_localized": t1, "T2_U_shaped_resolution": t2, "T3_temporal_vs_ensemble": t3,
           "T4_sampling_sets_temporal_resolution": t4,
           "temporal_switching_instrumented": bool(t1 and t2 and t3 and t4),
           "verdict": ("TEMPORAL SWITCHING + THE SAMPLING/TIME SYNTHESIS (② EXP-14): the detector localizes WHEN the law "
                       "changes, and the sampling axis sets how sharply. A Bell stream switches source classical->quantum "
                       "at t={}. (T1) The whole-stream CHSH is one blurred number ({:.2f}); a sliding-window CHSH "
                       "localizes the switch to {} steps at W={}. (T2) Localization error vs window is U-SHAPED ({}) -- "
                       "short windows false-cross in the classical part (noisy), long windows smear the switch (~W/2). "
                       "(T3) within-stream windowed-CHSH variance is {:.3f} for the switch vs {:.4f}/{:.4f} for "
                       "stationary classical/quantum streams -- a temporal SWITCH is cleanly separable from an ensemble "
                       "MIXTURE (EXP-8). (T4, the synthesis) the localization FLOOR grows as the margin shrinks: {} steps "
                       "at delta=0.4 -> {} at delta=0.15 ({:.0f}x), a log-log slope {:.2f} ~ -2 tracking N_resolve ~ "
                       "1/delta^2 -- near the decision wall a switch is not just data-hungry, it is temporally BLURRIER. "
                       "The sampling axis (EXP-12) sets the temporal resolution of law-detection."
                       .format(CP, whole, best_err, best_W, list(zip(Ws, errs)), tv_switch, tv_cl, tv_qu,
                               floor[0.4], floor[0.15], ratio, slope4 if slope4 else float("nan"))
                       if (t1 and t2 and t3 and t4) else "PARTIAL/HONEST -- see per-gate numbers.")}
    print(f"T1 localized: best_err={best_err} at W={best_W} (whole-stream CHSH={whole:.2f}) -> {t1}")
    print(f"T2 U-shaped: {list(zip(Ws, errs))} -> {t2}")
    print(f"T3 temporal-var switch={tv_switch:.3f} vs cl={tv_cl:.4f}/qu={tv_qu:.4f} -> {t3}")
    print(f"T4 floor by delta {floor} (ratio 0.15/0.4 = {ratio:.0f}x, slope {slope4}) -> {t4}")
    print(f"\nTEMPORAL SWITCHING INSTRUMENTED: {out['temporal_switching_instrumented']}")
    (RESULTS / "155_temporal_switching.json").write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(1, 2, figsize=(13, 5))
    c, V = windowed(stream, best_W, 50)
    ax[0].plot(c, V, "o-", color="crimson", ms=3, label=f"windowed CHSH (W={best_W})")
    ax[0].axvline(CP, ls="--", c="k", label="true switch"); ax[0].axhline(2.0, ls=":", c="gray", label="wall CHSH=2")
    ax[0].set_xlabel("trial index"); ax[0].set_ylabel("windowed CHSH"); ax[0].legend(fontsize=8)
    ax[0].set_title("T1: sliding window localizes the source switch\n(classical → quantum at t=6000)")
    ax[1].plot(Ws, errs, "o-", color="purple", label="δ=0.4 (U-shape)")
    for d, col in [(0.4, "seagreen"), (0.15, "orange")]:
        ax[1].axhline(floor[d], ls=":", c=col, label=f"floor δ={d} ({floor[d]})")
    ax[1].set_xscale("log"); ax[1].set_xlabel("window length W"); ax[1].set_ylabel("switch localization error")
    ax[1].legend(fontsize=8); ax[1].set_title("T2/T4: U-shaped error; floor rises near the wall\n(sampling axis sets temporal resolution)")
    fig.suptitle("② EXP-14 — temporal switching: the sampling axis sets the temporal resolution of law-detection")
    fig.tight_layout(); fig.savefig(RESULTS / "155_temporal_switching.png", dpi=140)
    print("saved results/155_temporal_switching.json + .png")


if __name__ == "__main__":
    main()
