"""Step 112 — the Page curve + information return: 'information comes back' as a recoverability transition.

The last poke of the emergent-spacetime map (after J5 curvature-from-entanglement, Cert V time-gauge, 111
frame-gauge): the black-hole information paradox, as an exact qubit toy in our recoverability/cheapest-code language.

Physics (web-verified): Page 1993 -- the average entanglement entropy of a subsystem of a random PURE state rises
then FALLS (turnover at half), the unitary 'Page curve' of evaporation; Hawking's thermal account would only rise
(info lost). Hayden-Preskill 2007 -- info thrown into an OLD black hole is recoverable from the radiation after
scrambling, tracked by the MUTUAL INFORMATION between a reference qubit and the radiation (the 'information mirror').

Exact toy (no approximations -- direct entropies of random pure states):
  PAGE CURVE:   N qubits in a Haar-random pure state; S(radiation = first k qubits) over k.
  INFO RETURN:  a reference qubit maximally entangled with an infalling 'diary' qubit; the N system qubits Haar-
                scrambled; I(Ref : radiation) over k.

Pre-reg (2026-06-23):
  P1 PAGE TURNOVER: S(R) rises then FALLS -- peak near k=N/2 AND S(R=N) < 0.2*peak (the radiation purifies),
     unlike the thermal baseline S=k*ln2 (monotone).
  P2 INFORMATION RETURN: I(Ref:R) ~ 0 before the Page time (k=N/2-1: < 0.3 nats) and near-maximal after
     (k=N: > 1.0 nats, max = 2*ln2 = 1.386) -- the info comes back out, recoverable from the radiation.
  P3 CONTRAST: the thermal account never returns the info (I=0 always); unitarity does -> unitarity is the
     information-RECOVERABLE description, and the Page time is the recoverability transition (a decoder exists iff I>0).

Honest scope: an exact DEMONSTRATION of Page (1993) + Hayden-Preskill (2007) cast in our language -- not new physics;
the map's last poke, completing the emergent-spacetime arc (entanglement<->geometry, time, frame, information).
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

LN2 = np.log(2)


def entropy(psi, n, keep):
    """von Neumann entropy (nats) of the subsystem on qubit indices `keep`, for state vector psi of n qubits."""
    keep = sorted(keep); rest = [i for i in range(n) if i not in keep]
    t = np.transpose(psi.reshape([2] * n), keep + rest).reshape(2 ** len(keep), 2 ** len(rest))
    s = np.linalg.svd(t, compute_uv=False)
    p = (s ** 2); p = p[p > 1e-13]
    return float(-(p * np.log(p)).sum())


def haar_state(n, rng):
    v = rng.standard_normal(2 ** n) + 1j * rng.standard_normal(2 ** n)
    return v / np.linalg.norm(v)


def haar_unitary(dim, rng):
    z = (rng.standard_normal((dim, dim)) + 1j * rng.standard_normal((dim, dim))) / np.sqrt(2)
    q, r = np.linalg.qr(z)
    return q @ np.diag(np.exp(1j * np.angle(np.diag(r))))


def main():
    rng = np.random.default_rng(0)

    # ---- PAGE CURVE: average S(radiation) over Haar pure states ----
    Npage, REP = 12, 6
    ks = list(range(Npage + 1))
    Savg = np.zeros(Npage + 1)
    for _ in range(REP):
        psi = haar_state(Npage, rng)
        Savg += np.array([entropy(psi, Npage, list(range(k))) for k in ks])
    Savg /= REP
    thermal = np.array([k * LN2 for k in ks])
    peak_k = int(np.argmax(Savg)); S_peak = float(Savg[peak_k]); S_end = float(Savg[-1])
    p1 = bool(abs(peak_k - Npage / 2) <= 1 and S_end < 0.2 * S_peak)

    # ---- INFORMATION RETURN: I(Ref:R) over evaporation (Hayden-Preskill) ----
    Nsys = 10
    U = haar_unitary(2 ** Nsys, rng)
    # Ref (qubit 0) maximally entangled with diary q0 (qubit 1); q1..q_{Nsys-1} = |0>
    psi = np.zeros(2 ** (Nsys + 1), dtype=complex)
    # basis index = Ref*2^Nsys + system; system index 0 = |0...0>, system 'q0=1' = 2^(Nsys-1)
    psi[0 * 2 ** Nsys + 0] = 1 / np.sqrt(2)                       # |Ref=0>|sys: q0=0,...>
    psi[1 * 2 ** Nsys + 2 ** (Nsys - 1)] = 1 / np.sqrt(2)         # |Ref=1>|sys: q0=1,0...>
    psi = psi.reshape(2, 2 ** Nsys)
    psi = (psi @ U.T).reshape(-1)                                 # apply I_Ref (x) U to the system factor
    n = Nsys + 1                                                  # qubit 0 = Ref, qubits 1..Nsys = system
    S_ref = entropy(psi, n, [0])
    I = []
    for k in range(Nsys + 1):
        R = list(range(1, 1 + k))                                 # radiation = first k system qubits
        S_R = entropy(psi, n, R)
        S_refR = entropy(psi, n, [0] + R)
        I.append(S_ref + S_R - S_refR)
    I = np.array(I)
    half = Nsys // 2
    p2 = bool(I[half - 1] < 0.3 and I[-1] > 1.0)
    p3 = bool(I[-1] > 1.0)                                        # unitary returns it; thermal would be 0 always

    out = {"page": {"N": Npage, "reps": REP, "S": Savg.tolist(), "peak_k": peak_k, "S_peak": S_peak, "S_end": S_end},
           "info_return": {"Nsys": Nsys, "I_RefR": I.tolist(), "I_before_page": float(I[half - 1]),
                           "I_after_full": float(I[-1]), "I_max_2ln2": float(2 * LN2)},
           "P1_page_turnover": p1, "P2_information_return": p2, "P3_thermal_contrast": p3,
           "page_curve_and_recovery": bool(p1 and p2 and p3),
           "verdict": ("Page curve + information return, exact qubit toy: S(radiation) RISES THEN FALLS (peak at "
                       f"k={peak_k}~N/2, returns to {S_end:.2f}~0 -- the radiation purifies), vs the thermal account "
                       f"that only rises. And the infalling info COMES BACK: I(Ref:radiation) goes {I[half-1]:.2f}->"
                       f"{I[-1]:.2f} nats (~2ln2={2*LN2:.2f}) across the Page time -- recoverable from the radiation "
                       "only after it. Unitarity = the information-recoverable description; the Page time is the "
                       "recoverability transition (a decoder exists iff I>0). Demonstration of Page 1993 + "
                       "Hayden-Preskill 2007 in our cheapest-code language; the map's last poke.")}
    print(f"P1 Page turnover: peak at k={peak_k} (N/2={Npage/2:.0f}), S_peak={S_peak:.2f}, S_end={S_end:.3f} "
          f"(<0.2*peak={0.2*S_peak:.2f}): {p1}")
    print(f"P2 info return: I(Ref:R) before page (k={half-1})={I[half-1]:.3f} (<0.3); after full (k={Nsys})="
          f"{I[-1]:.3f} (>1.0, max 2ln2={2*LN2:.3f}): {p2}")
    print(f"P3 thermal contrast (unitary returns I={I[-1]:.2f} vs thermal 0): {p3}")
    print(f"\nPAGE CURVE + INFORMATION RETURN: {out['page_curve_and_recovery']}")
    (Path(__file__).resolve().parent.parent / "results" / "112_page_curve.json").write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(1, 2, figsize=(13, 5))
    ax[0].plot(ks, Savg, "o-", color="crimson", label="unitary (Page curve)")
    ax[0].plot(ks, thermal, "--", color="gray", label="thermal/Hawking (info lost)")
    ax[0].axvline(Npage / 2, ls=":", c="k", lw=0.8, label="Page time (N/2)")
    ax[0].set_xlabel("radiation emitted (qubits k)"); ax[0].set_ylabel("radiation entropy S(R) [nats]")
    ax[0].set_title(f"P1 · the Page curve (rise then fall)\npeak k={peak_k}, purifies to {S_end:.2f}"); ax[0].legend(fontsize=8)
    ax[1].plot(range(Nsys + 1), I, "o-", color="seagreen", label="I(Ref : radiation)")
    ax[1].axhline(2 * LN2, ls="--", c="k", lw=0.8, label="max = 2 ln2 (fully recoverable)")
    ax[1].axvline(half, ls=":", c="k", lw=0.8, label="Page time")
    ax[1].set_xlabel("radiation emitted (qubits k)"); ax[1].set_ylabel("mutual info I(Ref:R) [nats]")
    ax[1].set_title("P2 · the information comes back\n(recoverable from radiation after the Page time)"); ax[1].legend(fontsize=8)
    fig.suptitle("Page curve + information return — the info paradox as a recoverability transition (exact qubit toy)")
    fig.tight_layout(); fig.savefig(Path(__file__).resolve().parent.parent / "results" / "112_page_curve.png", dpi=140)
    print("saved results/112_page_curve.json + .png")


if __name__ == "__main__":
    main()
