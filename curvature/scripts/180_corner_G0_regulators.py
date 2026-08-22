"""Step 180 / G0 — the four regulators, and the gate that stops the run if any fails to converge.

FROZEN PRE-REGISTRATION: notes/quantum_corner_PREREG_FROZEN.md @ e283d21 (+ Amendments 1, 2).
This is the FIRST gate. Its known-fail is absolute: a regulator that does not reduce to m^2 + k^2 at small k
invalidates every downstream number, so if G0 fails the run STOPS and no corner coefficient is computed.

WHY THIS IS A REAL GATE AND NOT A FORMALITY. quantum built their own regulators and has only their own word
that they converge. I build mine independently; if both converge, the shared assumption is tested twice. If
mine do not, the fault is mine and the run ends before it can produce a plausible-looking wrong answer.

THE ONE DERIVATION THIS GATE DEPENDS ON, checked here rather than assumed. With theta_i = k.a_i over the three
bonds (a1, a2, a1-a2):

    K_NN = (4/3) sum_i (1 - cos theta_i)
         = (2/3) sum theta^2  -  (1/18) sum theta^4  +  O(theta^6)

and (2/3) sum theta_i^2 = |k|^2 EXACTLY (algebra: sum theta^2 = 2(t1^2 + t2^2 - t1 t2), and
|k|^2 = t1^2 + (2 t2 - t1)^2 / 3 = (4/3)(t1^2 + t2^2 - t1 t2)).

The O(k^4) term is ISOTROPIC on this lattice -- measured: sum theta^4 / |k|^4 = 1.125000 with spread 9e-16
across the full 60-degree symmetry sector. THAT IS WHY the frozen form m^2 + K + c4*K^2 can cancel it at all:
on a SQUARE lattice the quartic error is theta_x^4 + theta_y^4, which is not proportional to |k|^4, and no
coefficient in this family would work. The triangular lattice earns its place here for a second reason beyond
the 60/120-degree angles.

    => c4 = 1.125 / 18 = 1/16 = 0.0625, DERIVED, not fitted.

and 0.0625 != 0.25, so the frozen collision contingency (regulator 3 moving to c = 0.5) does NOT fire.
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

N, MASS = 160, 0.01
C_QUARTIC, B_SMEAR = 0.25, 0.15          # FROZEN in the pre-registration, not tuned here
C4 = 1.0 / 16.0                          # DERIVED above


def thetas(m1, m2):
    """Phase differences across the three bonds for integer mode indices (m1, m2)."""
    t1 = 2 * np.pi * m1 / N
    t2 = 2 * np.pi * m2 / N
    return t1, t2, t1 - t2


def ksq(t1, t2):
    """|k|^2 in real units from the two independent phases (exact, see docstring)."""
    kx = t1
    ky = (2 * t2 - t1) / np.sqrt(3.0)
    return kx ** 2 + ky ** 2


def K_NN(t1, t2, t3):
    return (4.0 / 3.0) * ((1 - np.cos(t1)) + (1 - np.cos(t2)) + (1 - np.cos(t3)))


def omega2(name, m1, m2):
    t1, t2, t3 = thetas(m1, m2)
    K = K_NN(t1, t2, t3)
    if name == "nn":
        return MASS ** 2 + K
    if name == "improved":
        return MASS ** 2 + K + C4 * K ** 2
    if name == "quartic":
        return MASS ** 2 + K + C_QUARTIC * K ** 2
    if name == "smeared":
        return MASS ** 2 + K * np.exp(B_SMEAR * K)
    raise ValueError(name)


REGULATORS = ("nn", "improved", "quartic", "smeared")
EXPECTED_ORDER = {"nn": 4, "improved": 6, "quartic": 4, "smeared": 4}


def main():
    out = {"prereg": "notes/quantum_corner_PREREG_FROZEN.md @ e283d21 (+A1, +A2)",
           "N": N, "mass": MASS, "c_quartic": C_QUARTIC, "b_smear": B_SMEAR, "c4_derived": C4}

    # --- the derivation the gate rests on, re-measured here ---
    ang = np.linspace(0, np.pi / 3, 25)
    iso = []
    for eps in (1e-2, 1e-3):
        for a in ang:
            k = eps * np.array([np.cos(a), np.sin(a)])
            t1 = k[0]; t2 = k[0] / 2 + k[1] * np.sqrt(3) / 2
            iso.append((t1 ** 4 + t2 ** 4 + (t1 - t2) ** 4) / (k @ k) ** 2)
    iso = np.array(iso)
    iso_spread = float(iso.max() / iso.min() - 1)
    print(f"quartic-error isotropy: sum(theta^4)/|k|^4 = {iso.mean():.6f}  spread {iso_spread:.1e}")
    out["quartic_error_isotropic"] = {"value": float(iso.mean()), "spread": iso_spread}

    # --- G0: does each regulator reduce to m^2 + k^2, and at the expected order? ---
    print("\nG0 — small-k convergence. rel = |omega^2 - (m^2 + k^2)| / k^2, along a generic lattice direction")
    scales = np.array([32, 16, 8, 4, 2])              # mode index; k ~ 2*pi*m/N
    rows = {}
    for reg in REGULATORS:
        rel, kk = [], []
        for s in scales:
            m1, m2 = int(s), int(s // 2) + 1          # generic direction, not a symmetry axis
            t1, t2, t3 = thetas(m1, m2)
            k2 = ksq(t1, t2)
            w2 = omega2(reg, m1, m2)
            rel.append(abs(w2 - (MASS ** 2 + k2)) / k2)
            kk.append(np.sqrt(k2))
        rel, kk = np.array(rel), np.array(kk)
        # fitted convergence order: rel ~ k^p  =>  p from successive ratios
        p = float(np.polyfit(np.log(kk), np.log(rel), 1)[0])
        rows[reg] = {"k": kk.tolist(), "rel_err": rel.tolist(), "fitted_order": p,
                     "expected_order_minus_2": EXPECTED_ORDER[reg] - 2}
        # GATE ON THE FROZEN CRITERION ONLY. The pre-registration says: "omega^2/(m^2+k^2) - 1 -> 0 as k->0,
        # at the expected order." Run 1 of this script ALSO required rel[-1] < 1e-3 -- an absolute magnitude
        # clause that appears NOWHERE in the frozen file and that I added while coding. It fired on the quartic
        # regulator (1.54e-3) and looked exactly like a real G0 failure.
        #
        # The quartic's larger magnitude is BY DESIGN: c = 0.25 is a deliberate deformation ~4x the derived
        # c4 = 0.0625, so its O(k^4) coefficient is correspondingly larger. It converges at the right ORDER
        # (1.91 ~ 2), which is what the frozen criterion asks and what the physics requires. Magnitudes are
        # reported below rather than gated, because the regulators are REQUIRED to differ (G0b) -- gating them
        # toward agreement would defeat the purpose of having four.
        ok = abs(p - (EXPECTED_ORDER[reg] - 2)) < 0.35 and rel[0] > rel[-1]
        rows[reg]["pass"] = bool(ok)
        rows[reg]["rel_err_smallest_k"] = float(rel[-1])
        rows[reg]["unfrozen_1e-3_clause_would_pass"] = bool(rel[-1] < 1e-3)
        print(f"  {reg:9s} rel err {rel[0]:.3e} -> {rel[-1]:.3e}   fitted k-power {p:.2f} "
              f"(expect {EXPECTED_ORDER[reg]-2})   {'OK' if ok else 'FAIL'}")

    G0 = all(rows[r]["pass"] for r in REGULATORS)

    # --- the regulators must actually DIFFER at the lattice scale, or 'across-regulator spread' is vacuous ---
    m1, m2 = N // 2, N // 4
    edge = {r: float(omega2(r, m1, m2)) for r in REGULATORS}
    vals = np.array(list(edge.values()))
    spread_edge = float((vals.max() - vals.min()) / vals.mean())
    print(f"\n  at the lattice scale (m1={m1}, m2={m2}): omega^2 = "
          + ", ".join(f"{r}={edge[r]:.3f}" for r in REGULATORS))
    print(f"  fractional spread there: {spread_edge:.3f}  "
          f"{'(they genuinely differ)' if spread_edge > 0.05 else '(TOO SIMILAR -- spread would be vacuous)'}")
    G0b = bool(spread_edge > 0.05)

    ok = bool(G0 and G0b)
    out.update({"G0_rows": rows, "G0_all_converge": G0,
                "criterion_note": ("gated on the FROZEN criterion (convergence at the expected order) only. "
                                   "Run 1 additionally required rel_err < 1e-3 at the smallest k -- a clause "
                                   "never present in the pre-registration, added during implementation, which "
                                   "fired on the quartic and looked like a real failure. Removed as an "
                                   "un-frozen criterion, not as a relaxed one; the frozen text is quoted in "
                                   "the lab notebook."),
                "G0b_differ_at_lattice_scale": G0b, "edge_omega2": edge, "edge_spread": spread_edge,
                "collision_contingency_fired": bool(abs(C4 - C_QUARTIC) < 1e-9),
                "all_pass": ok,
                "verdict": ("G0 PASSED. All four regulators reduce to m^2 + k^2 at small k at their expected "
                            "orders (improved converges two powers faster, as its derived c4 = 1/16 requires), "
                            "and they differ by {:.0f}% at the lattice scale so an across-regulator spread is a "
                            "real measurement rather than a vacuous one. The quartic lattice error is ISOTROPIC "
                            "here ({:.6f}|k|^4, spread {:.0e}), which is what makes the frozen m^2+K+cK^2 form "
                            "able to cancel it at all -- on a square lattice it could not. Proceeding to G1b."
                            .format(spread_edge * 100, iso.mean(), iso_spread) if ok else
                            "G0 FAILED -- per the frozen pre-registration the run STOPS here and no corner "
                            "coefficient is computed. A regulator that does not converge invalidates everything "
                            "downstream.")})
    print(f"\nG0 converge: {G0} | G0b differ at cutoff: {G0b}")
    print(out["verdict"])
    (RESULTS / "180_corner_G0.json").write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(1, 2, figsize=(13, 4.6))
    for r in REGULATORS:
        ax[0].loglog(rows[r]["k"], rows[r]["rel_err"], "o-", label=f"{r} (p={rows[r]['fitted_order']:.2f})")
    ax[0].set_xlabel("|k|"); ax[0].set_ylabel(r"$|\omega^2-(m^2+k^2)|/k^2$")
    ax[0].set_title("G0 · small-k convergence"); ax[0].legend(fontsize=8)
    mm = np.arange(1, N // 2)
    for r in REGULATORS:
        ax[1].plot(2 * np.pi * mm / N, [omega2(r, i, i // 2 + 1) for i in mm], label=r)
    ax[1].set_xlabel(r"$\theta_1$"); ax[1].set_ylabel(r"$\omega^2$")
    ax[1].set_title("the four regulators, full Brillouin range"); ax[1].legend(fontsize=8)
    fig.tight_layout(); fig.savefig(RESULTS / "180_corner_G0.png", dpi=140)
    print("saved results/180_corner_G0.json + .png")


if __name__ == "__main__":
    main()
