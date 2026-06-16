"""Step 57 — EXOTIC: a WORMHOLE from entanglement (ER=EPR), the inverse of Phase J's pinch-off.

Phase J (script 32) showed DECOUPLING two halves (cross-MI -> 0) flings them apart in the emergent
MI-geometry (Van Raamsdonk pinch-off). ER=EPR (web-verified, Maldacena-Susskind 2013): entanglement
between two regions IS a wormhole connecting them. So the inverse test: ADD entanglement between two
FAR-APART chain regions and ask whether their EMERGENT distance collapses into a shortcut — a wormhole
— even though their chain (boundary) distance is maximal.

Setup (free-fermion chain, Phase J machinery): n-site chain; regions A={0,1} and B={n/2,n/2+1} are
maximally far on the chain. Add a direct "bridge" hopping of strength t between site 0 and site n/2
(this entangles A and B). Sweep t. Emergent distance d(A,B) = -log(mutual information I(A,B)).

Pre-reg (2026-06-17):
  W1 baseline (t=0): A,B are FAR — I(A,B) tiny, d(A,B) large (~ a maximally-separated pair), while
     adjacent regions have high MI. The chain geometry: distance tracks chain separation.
  W2 wormhole (t large): adding entanglement COLLAPSES d(A,B) — it drops by > 50% from t=0, toward the
     adjacent-region (neighbor) distance, WITHOUT changing chain positions. A shortcut appears.
  W3 dose-response: d(A,B) decreases monotonically as the bridge entanglement t grows (more
     entanglement = shorter wormhole).
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from curvlib import RESULTS
from importlib import import_module

s32 = import_module("32_entangle_geometry")
N = 32
A = [0, 1]
B = [N // 2, N // 2 + 1]
NBR = [1, 2]                                   # an adjacent pair, for "what close looks like"
TS = [0.0, 0.3, 0.6, 1.0, 1.5]


def hop_with_bridge(n, t):
    h = s32.chain_hop(n, periodic=False)
    h[0, n // 2] = h[n // 2, 0] = -t           # the entanglement bridge between the two far regions
    return h


def region_mi(C, X, Y):
    sx = s32.region_entropy(C, X); sy = s32.region_entropy(C, Y); sxy = s32.region_entropy(C, X + Y)
    return max(sx + sy - sxy, 1e-9)


def main():
    rows = []
    for t in TS:
        C = s32.corr_matrix(hop_with_bridge(N, t))
        iAB = region_mi(C, A, B); iNbr = region_mi(C, [0, 1], [2, 3])
        dAB = -np.log(iAB); dNbr = -np.log(iNbr)
        rows.append({"t": t, "I_AB": float(iAB), "d_AB": float(dAB), "I_nbr": float(iNbr), "d_nbr": float(dNbr)})
        print(f"t={t:.1f}: I(A,B)={iAB:.2e} d(A,B)={dAB:5.2f} | neighbor I={iNbr:.2e} d={dNbr:5.2f}")

    d = [r["d_AB"] for r in rows]
    w1 = bool(rows[0]["d_AB"] > rows[0]["d_nbr"] + 1.0)            # baseline: far pair is far vs neighbors
    w2 = bool(d[-1] < 0.5 * d[0] and d[-1] < rows[-1]["d_nbr"] + 1.5)   # wormhole: collapses toward neighbor distance
    w3 = bool(all(d[i + 1] <= d[i] + 1e-6 for i in range(len(d) - 1)) and d[-1] < d[0] - 1.0)
    out = {"sweep": rows, "chain_distance_AB": N // 2,
           "W1_baseline_far": w1, "W2_wormhole_shortcut": w2, "W3_dose_response": w3,
           "wormhole_from_entanglement": bool(w1 and w2 and w3)}
    print(f"\nW1 baseline far (d(A,B) {d[0]:.2f} >> neighbor {rows[0]['d_nbr']:.2f}): {w1}")
    print(f"W2 wormhole shortcut (d(A,B) {d[0]:.2f} -> {d[-1]:.2f}, <50% & ~neighbor): {w2}")
    print(f"W3 dose-response (monotone decrease, Δ {d[0]-d[-1]:.2f}): {w3}")
    print(f"\nWORMHOLE FROM ENTANGLEMENT (ER=EPR shortcut): {out['wormhole_from_entanglement']}")
    (RESULTS / "57_wormhole.json").write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(figsize=(7.5, 5))
    ax.plot(TS, d, "o-", color="purple", label=f"emergent d(A,B) — chain-distance {N//2}")
    ax.axhline(rows[0]["d_nbr"], ls=":", color="seagreen", label="adjacent-region distance ('close')")
    ax.set_xlabel("bridge entanglement t (between the two far regions)")
    ax.set_ylabel("emergent distance d(A,B) = −log I(A,B)")
    ax.set_title("ER=EPR: adding entanglement collapses emergent distance\n(a wormhole shortcut between far regions)")
    ax.legend(fontsize=8); fig.tight_layout(); fig.savefig(RESULTS / "57_wormhole.png", dpi=140)
    print("saved results/57_wormhole.json + .png")


if __name__ == "__main__":
    main()
