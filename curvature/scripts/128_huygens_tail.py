"""Step 128 — Huygens' principle by dimension: a sharp signal stays sharp in 3D but leaves a TAIL in 2D.

Phase 1b separate-angle probe (notes/build_queue.md), validating dimensional_ladder.md sec 5. Web-verified
(Hadamard; Ehrenfest's anthropic note on 3+1): the wave equation satisfies Huygens' principle in ODD spatial
dimension (d=3: a compact pulse propagates as a sharp shell, the field returns to ZERO after the wavefront) and
VIOLATES it in EVEN spatial dimension (d=2: a lingering radiation TAIL after the front, ~1/sqrt(t^2 - r^2), the
2D cylindrical Green's function). This is why a clean "now" exists in 3+1 -- a reason our world is 3+1.

Toy (the nn_and_spacetime sec5 "two solvers differing only in dimension" -- here a reliable radial FDTD; a PINN
would learn the same but is finicky for long-time waves): solve the radial wave equation u_tt = u_rr + ((d-1)/r) u_r
driven by a compact source pulse near the origin, and record the field at a fixed radius r0 vs time. The ONLY
difference between the two runs is the dimension d (the (d-1)/r coefficient).

Pre-reg (2026-06-25):
  H1 HUYGENS BY DIMENSION: after the wavefront passes r0, the 3D field returns to ~0 (tail/peak < 0.03) while the 2D
     field retains a tail (tail/peak > 0.1).
  H2 SAME FRONT SPEED: the wavefront ARRIVES at r0 at the same time in 2D and 3D (|dt_arrival| < 0.2) -- the speed c
     is dimension-independent; the difference is the WAKE, not the propagation speed (a genuine Huygens tail).
  H3 ANALYTIC TAIL SHAPE: the 2D post-front field follows the cylindrical Green's-function tail 1/sqrt((t-t0)^2 - r0^2)
     (correlation > 0.85) -- the real Huygens tail, not numerical noise.
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

R0, RMAX, DR, T, T0, TAU = 5.0, 16.0, 0.02, 11.0, 0.6, 0.15


def fdtd(d):
    """source-driven radial wave: u_tt = u_rr + ((d-1)/r) u_r + S(r,t). Returns (time grid, u at r0)."""
    r = np.arange(1, int(RMAX / DR)) * DR; n = len(r); dt = 0.4 * DR; k = d - 1
    src_sp = np.exp(-(r / 0.3) ** 2)
    um = np.zeros(n); u = np.zeros(n); i0 = int(round(R0 / DR)) - 1
    nt = int(T / dt); rec = []
    for s in range(nt):
        t = s * dt; St = np.exp(-((t - T0) / TAU) ** 2)
        lap = np.zeros(n)
        lap[1:-1] = (u[2:] - 2 * u[1:-1] + u[:-2]) / DR ** 2 + k * (u[2:] - u[:-2]) / (2 * DR * r[1:-1])
        un = 2 * u - um + dt ** 2 * (lap + src_sp * St)
        un[0] = un[1]; un[-1] = 0.0                                # regularity at r~0; Dirichlet at RMAX (no return)
        um, u = u, un; rec.append(u[i0])
    return np.arange(nt) * dt, np.array(rec)


def metrics(tg, rec):
    peak = float(np.abs(rec).max())
    arrival = float(tg[np.argmax(np.abs(rec) > 0.1 * peak)])       # first time the front reaches r0
    tail_mask = tg > (T0 + R0) + 2.0                              # well after the wavefront
    tail = float(np.sqrt(np.mean(rec[tail_mask] ** 2)) / peak)
    return peak, arrival, tail, tail_mask


def main():
    tg3, rec3 = fdtd(3); tg2, rec2 = fdtd(2)
    p3, a3, tail3, _ = metrics(tg3, rec3)
    p2, a2, tail2, tmask = metrics(tg2, rec2)

    h1 = bool(tail3 < 0.03 and tail2 > 0.1)
    h2 = bool(abs(a2 - a3) < 0.2)

    # H3: 2D post-front tail vs analytic cylindrical Green tail 1/sqrt((t-t0)^2 - r0^2)
    tt = tg2[tmask]; analytic = 1.0 / np.sqrt(np.clip((tt - T0) ** 2 - R0 ** 2, 1e-6, None))
    corr = float(np.corrcoef(np.abs(rec2[tmask]), analytic)[0, 1])
    h3 = bool(corr > 0.85)

    out = {"tail3D_over_peak": tail3, "tail2D_over_peak": tail2, "arrival3D": a3, "arrival2D": a2,
           "tail_shape_corr_2D": corr, "H1_huygens_by_dimension": h1, "H2_same_front_speed": h2,
           "H3_analytic_tail_shape": h3, "huygens_tail_by_dimension": bool(h1 and h2 and h3),
           "verdict": ("HUYGENS BY DIMENSION (dimensional_ladder sec5 validated): a compact source pulse, propagated by "
                       "the radial wave equation, leaves the 3D field SHARP -- it returns to {:.3f} of peak after the "
                       "wavefront (Huygens' principle holds) -- while the 2D field retains a TAIL ({:.2f} of peak). The "
                       "wavefront ARRIVES at the same time in both (2D {:.2f}, 3D {:.2f}: speed c is dimension-"
                       "independent), so the difference is the WAKE, not the speed. The 2D tail follows the cylindrical "
                       "Green's-function form 1/sqrt((t-t0)^2 - r0^2) (corr {:.2f}). A clean 'now' exists only in odd "
                       "spatial dimension -- a reason our world is 3+1 (Ehrenfest)."
                       .format(tail3, tail2, a2, a3, corr)
                       if (h1 and h2 and h3) else "PARTIAL -- see numbers (honest).")}
    print(f"H1 Huygens by dim: 3D tail/peak={tail3:.4f} (<0.03), 2D tail/peak={tail2:.3f} (>0.1): {h1}")
    print(f"H2 same front speed: arrival 2D={a2:.2f} vs 3D={a3:.2f} (|d|<0.2): {h2}")
    print(f"H3 analytic 2D tail shape: corr to 1/sqrt(t^2-r^2) = {corr:.2f} (>0.85): {h3}")
    print(f"\nHUYGENS TAIL BY DIMENSION: {out['huygens_tail_by_dimension']}")
    (RESULTS / "128_huygens_tail.json").write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(1, 2, figsize=(13, 5))
    ax[0].plot(tg3, rec3, color="seagreen", label="3D (sharp, no tail)")
    ax[0].plot(tg2, rec2, color="crimson", label="2D (tail)")
    ax[0].axvline(T0 + R0, ls=":", c="k", lw=0.7, label="wavefront")
    ax[0].set_xlabel("time t"); ax[0].set_ylabel(f"field u(r0={R0}, t)"); ax[0].legend(fontsize=8)
    ax[0].set_title("Huygens' principle by dimension\n3D returns to 0; 2D leaves a tail")
    tt = tg2[tmask]
    ax[1].plot(tt, np.abs(rec2[tmask]), color="crimson", label="2D |field| (tail)")
    an = 1 / np.sqrt(np.clip((tt - T0) ** 2 - R0 ** 2, 1e-6, None))
    ax[1].plot(tt, an / an.max() * np.abs(rec2[tmask]).max(), "k--", lw=1, label="1/√(t²−r²) (cylindrical Green)")
    ax[1].set_xlabel("time t"); ax[1].set_ylabel("|field|"); ax[1].legend(fontsize=8)
    ax[1].set_title(f"2D tail shape (corr {corr:.2f})")
    fig.suptitle("Huygens tail by dimension: a clean 'now' exists only in odd spatial dimension (validates dimensional_ladder §5)")
    fig.tight_layout(); fig.savefig(RESULTS / "128_huygens_tail.png", dpi=140)
    print("saved results/128_huygens_tail.json + .png")


if __name__ == "__main__":
    main()
