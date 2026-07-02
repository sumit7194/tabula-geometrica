"""Step 153 — EXP-12 of the REPRESENTABILITY FRONTIER (②): the SAMPLING axis instrumented — sample complexity diverges at the wall.

notes/representability_frontier.md. EXP-11 instrumented the PREDICTABILITY axis; EXP-6/10 handled the SAMPLING axis as a
binary abstain. EXP-12 makes the sampling axis QUANTITATIVE: how many samples does it take to resolve a verdict, as a
function of distance to the decision boundary? Near a wall the answer DIVERGES -- a critical-slowing-down analog with a
derivable law. We use the contextual wall (CHSH = 2): a Werner state at visibility v has CHSH = 2*sqrt2*v, so its margin
above the wall is delta = 2*sqrt2*v - 2. A normal-approx CI on the empirical CHSH (lower bound = CHSH_emp - 1.96*SE)
resolves to CONTEXTUAL once CHSH_true - 1.96*SE > 2, i.e. delta > 1.96*SE. Since SE ~ c/sqrt(N), the resolution sample
size scales as N_resolve ~ (1.96 c / delta)^2 ~ 1/delta^2. The 3rd frontier axis gets a quantity (sample complexity) and
a power law (the divergence exponent), not just an abstain flag.

Pre-reg (2026-07-02):
  S1 MONOTONIC-DIVERGENCE: N_resolve (smallest N where >=90% of seeds resolve to CONTEXTUAL) increases monotonically as
     the margin delta -> 0 (closer to the wall needs more data).
  S2 POWER-LAW ~ 1/delta^2: the log-log slope of N_resolve vs delta is approximately -2 (in [-2.5, -1.5]).
  S3 QUANTIFIED AXIS: N_resolve at the smallest margin is >> at the largest (a genuine divergence) -- the sampling axis
     is now a measured quantity (sample complexity), not a binary flag.
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

NGRID = [50, 100, 200, 400, 800, 1600, 3200, 6400, 12800, 25600, 51200, 102400, 204800, 409600, 819200]
SETTINGS = [(0, 0), (0, 1), (1, 0), (1, 1)]


def chsh_and_se(S):
    E = np.zeros(4); n = np.zeros(4)
    for k, (x, y) in enumerate(SETTINGS):
        m = (S[:, 0] == x) & (S[:, 1] == y); n[k] = m.sum()
        E[k] = (S[m, 2] * S[m, 3]).mean() if m.any() else 0.0
    vals = s142.CHSH_SIGNS @ E
    best = int(np.argmax(np.abs(vals)))
    chsh = float(abs(vals[best]))
    se = float(np.sqrt(np.sum((1 - E ** 2) / np.maximum(n, 1))))    # SE of the (signed) sum; signs don't change variance
    return chsh, se


def resolves_contextual(S):
    chsh, se = chsh_and_se(S)
    return (chsh - 1.96 * se) > 2.0


def n_resolve(v, seeds=24):
    table = v * s142.SINGLET
    for N in NGRID:
        frac = np.mean([resolves_contextual(s145.gen_samples(table, n=N, seed=1000 * int(v * 1e4) + s))
                        for s in range(seeds)])
        if frac >= 0.9:
            return N, float(frac)
    return None, 0.0


def main():
    deltas = [0.6, 0.3, 0.15, 0.08, 0.04, 0.02]
    rows = []
    for d in deltas:
        v = (2 + d) / (2 * np.sqrt(2))
        N, frac = n_resolve(v)
        rows.append({"delta": d, "v": v, "chsh_true": 2 + d, "N_resolve": N, "frac_at_resolve": frac})
        print(f"delta={d:.3f} (v={v:.4f}, CHSH={2+d:.3f}): N_resolve={N}")

    got = [r for r in rows if r["N_resolve"] is not None]
    Ns = [r["N_resolve"] for r in got]; ds = [r["delta"] for r in got]
    monotonic = all(Ns[i + 1] >= Ns[i] for i in range(len(Ns) - 1))   # deltas descending -> Ns ascending
    slope = None
    if len(got) >= 3:
        slope = float(np.polyfit(np.log(ds), np.log(Ns), 1)[0])
    s1 = bool(monotonic and len(got) >= 4)
    s2 = bool(slope is not None and -2.5 <= slope <= -1.5)
    s3 = bool(len(got) >= 2 and Ns[-1] >= 20 * Ns[0])

    out = {"rows": rows, "loglog_slope": slope, "S1_monotonic_divergence": s1, "S2_power_law_inverse_delta_sq": s2,
           "S3_quantified_axis": s3, "sampling_axis_instrumented": bool(s1 and s2 and s3),
           "verdict": ("SAMPLE COMPLEXITY DIVERGES AT THE WALL (② EXP-12): the frontier's SAMPLING axis is now a "
                       "QUANTITY, not a binary abstain. Resolving the contextual verdict for a Werner state a margin "
                       "delta = CHSH-2 above the wall needs N_resolve samples, and N_resolve DIVERGES as delta -> 0: from "
                       "{} samples at delta={} down to {} samples at delta={}, a {:.0f}x growth. The log-log slope is "
                       "{:.2f} ~ -2, matching the derivable law N_resolve ~ 1/delta^2 (empirical CHSH noise ~ 1/sqrt(N), "
                       "so you need delta > ~1.96*SE). This is a critical-slowing-down analog: near a decision boundary "
                       "the data cost to decide blows up as an inverse-square power law. With this, all THREE frontier "
                       "axes are instrumented -- discoverability (145), predictability (152), and sampling (153) -- the "
                       "last as a measured sample-complexity divergence."
                       .format(Ns[0], ds[0], Ns[-1], ds[-1], Ns[-1] / max(Ns[0], 1), slope if slope else float("nan"))
                       if (s1 and s2 and s3) else "PARTIAL/HONEST -- see per-delta N_resolve + slope.")}
    print(f"\nlog-log slope = {slope} (expect ~ -2)")
    print(f"S1 monotonic: {s1} | S2 power-law ~1/delta^2: {s2} | S3 quantified: {s3}")
    print(f"SAMPLING AXIS INSTRUMENTED: {out['sampling_axis_instrumented']}")
    (RESULTS / "153_sample_complexity.json").write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(figsize=(8, 5.2))
    ax.loglog(ds, Ns, "o-", color="purple", zorder=3, label="N_resolve (empirical)")
    if slope is not None:
        fit = np.exp(np.polyval(np.polyfit(np.log(ds), np.log(Ns), 1), np.log(ds)))
        ax.loglog(ds, fit, "--", color="gray", label=f"power-law fit (slope {slope:.2f})")
    ax.set_xlabel("margin above the wall  δ = CHSH − 2"); ax.set_ylabel("sample complexity N_resolve")
    ax.invert_xaxis(); ax.legend(fontsize=9)
    ax.set_title("② EXP-12 — the sampling axis: sample complexity diverges at the wall\nN_resolve ~ 1/δ² (a critical-slowing-down analog)")
    fig.tight_layout(); fig.savefig(RESULTS / "153_sample_complexity.png", dpi=140)
    print("saved results/153_sample_complexity.json + .png")


if __name__ == "__main__":
    main()
