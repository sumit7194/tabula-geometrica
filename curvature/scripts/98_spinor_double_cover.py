"""Step 98 — THE FUNCTION-CLASS RUNG: the spinor double cover (a net's library must reach the half-angle sheet).

The distillation arc climbed function classes: polynomial invariants (91/92), then rational (96 LRL, 97 Kerr-de
Sitter Carter). The next rung is the one genuinely-open item on the field menu: the DIRAC/SPINOR double cover.
Web-verified (SU(2) double-covers SO(3); Rauch-Werner neutron interferometry 1974): a spin-1/2 state needs a
4*pi (720-degree) rotation to return to itself -- a 2*pi rotation flips its SIGN. All SO(3) observables (the
Bloch vector / expectation values) are 2*pi-periodic; only an INTERFERENCE measurement (recombining the rotated
beam with an un-rotated reference) sees the sign, and its fringe is 4*pi-periodic, going as cos(alpha/2) -- a
HALF-ANGLE function living on the other sheet of the double cover.

Concretely: prepare |psi0> = (+x eigenstate), rotate about z by alpha. The Bloch vector is (cos alpha, sin
alpha, 0) [2*pi-periodic]; the interference amplitude <psi0|psi(alpha)> = cos(alpha/2) [4*pi-periodic]. We build
the spinor numerically and ask the distillation library to REPRESENT the interference signal.

Pre-reg (2026-06-20):
  G1 FUNCTION-CLASS RUNG: an INTEGER-angle library {cos k*alpha, sin k*alpha} -- the class that represents every
     SO(3) observable -- CANNOT represent the interference cos(alpha/2) (held-out R^2 < 0.1); a DOUBLE-COVER
     (half-angle) library {cos(alpha/2), sin(alpha/2), ...} CAN (held-out R^2 > 0.999). The half-angle sheet is
     a required new feature class.
  G2 DOUBLE-COVER CERTIFICATE: the spinor sign is UNOBSERVABLE from the SO(3) Bloch vector -- representing the
     interference from the Bloch observables fails (held-out R^2 < 0.1), and the collision is exact: at alpha
     and alpha+2*pi the Bloch vector is identical (< 1e-9) while the interference is exactly opposite. A
     2*pi-periodic input cannot produce a 4*pi-periodic output -> certify (an impossibility, like 84-87).
  G3 THE 720 DEGREES: the faithful coordinate's period is 4*pi = TWICE the Bloch period (2*pi); the interference
     at 360 deg is -1 (destructive) and at 720 deg is +1 (constructive) -- the Rauch-Werner fermion signature.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

np.seterr(all="ignore")
S2 = np.sqrt(2.0)


def spinor(alpha):
    """|psi0> = +x eigenstate, rotated about z by alpha: amplitudes (a, b)."""
    a = np.exp(-1j * alpha / 2) / S2; b = np.exp(1j * alpha / 2) / S2
    return a, b


def observables(alpha):
    a, b = spinor(alpha); a0, b0 = spinor(0.0 * alpha)
    bloch_x = 2 * np.real(np.conj(a) * b)          # = cos(alpha), 2pi-periodic
    bloch_y = 2 * np.imag(np.conj(a) * b)          # = sin(alpha), 2pi-periodic
    bloch_z = np.abs(a) ** 2 - np.abs(b) ** 2       # = 0
    interf = np.real(np.conj(a0) * a + np.conj(b0) * b)   # <psi0|psi(alpha)> real part = cos(alpha/2), 4pi-periodic
    return bloch_x, bloch_y, bloch_z, interf


def integer_lib(alpha):
    return np.stack([np.ones_like(alpha)] + [f(k * alpha) for k in (1, 2, 3, 4) for f in (np.cos, np.sin)], -1)


def halfangle_lib(alpha):
    return np.stack([np.ones_like(alpha)] + [f(k * alpha / 2) for k in (1, 2, 3, 4) for f in (np.cos, np.sin)], -1)


def bloch_lib(alpha):
    bx, by, bz, _ = observables(alpha)              # polynomials in the SO(3) Bloch vector (all 2pi-periodic)
    return np.stack([np.ones_like(alpha), bx, by, bx * by, bx ** 2, by ** 2, bx ** 2 * by, bx * by ** 2], -1)


def fit_heldout(lib, target, seed=0):
    rng = np.random.default_rng(seed)
    a_tr = rng.uniform(0, 4 * np.pi, 600); a_te = rng.uniform(0, 4 * np.pi, 600)
    Ptr = lib(a_tr); Pte = lib(a_te)
    *_, ttr = (None,); ttr = target(a_tr); tte = target(a_te)
    c, *_ = np.linalg.lstsq(Ptr, ttr, rcond=None)
    pred = Pte @ c
    r2 = float(1 - np.var(tte - pred) / (np.var(tte) + 1e-12))
    return r2


def main():
    interf_target = lambda a: observables(a)[3]
    r2_int = fit_heldout(integer_lib, interf_target)
    r2_half = fit_heldout(halfangle_lib, interf_target)
    r2_bloch = fit_heldout(bloch_lib, interf_target)

    # G2 collision: Bloch identical at alpha and alpha+2pi, interference exactly opposite
    a = np.linspace(0.2, 2 * np.pi - 0.2, 50)
    bx, by, bz, I = observables(a); bx2, by2, bz2, I2 = observables(a + 2 * np.pi)
    bloch_gap = float(np.max(np.abs(bx - bx2)) + np.max(np.abs(by - by2)))
    sign_flip = float(np.max(np.abs(I + I2)))                 # I(alpha+2pi) == -I(alpha) -> this is ~0

    # G3 the 720 degrees
    I_360 = float(observables(np.array([2 * np.pi]))[3][0])   # cos(pi)  = -1 destructive
    I_720 = float(observables(np.array([4 * np.pi]))[3][0])   # cos(2pi) = +1 constructive
    bloch_period_repeat = float(abs(observables(np.array([2 * np.pi]))[0][0] - observables(np.array([0.0]))[0][0]))

    g1 = bool(r2_int < 0.1 and r2_half > 0.999)
    g2 = bool(r2_bloch < 0.1 and bloch_gap < 1e-9 and sign_flip < 1e-9)
    g3 = bool(abs(I_360 + 1) < 1e-6 and abs(I_720 - 1) < 1e-6 and bloch_period_repeat < 1e-9)
    out = {"R2_integer_lib": r2_int, "R2_halfangle_lib": r2_half, "R2_bloch_observable_lib": r2_bloch,
           "bloch_collision_gap_alpha_vs_alpha+2pi": bloch_gap, "interference_sign_flip": sign_flip,
           "interference_at_360deg": I_360, "interference_at_720deg": I_720, "bloch_period_repeat_at_2pi": bloch_period_repeat,
           "G1_function_class_rung": g1, "G2_double_cover_certificate": g2, "G3_the_720_degrees": g3,
           "double_cover_caught": bool(g1 and g2 and g3)}
    print(f"G1 FUNCTION-CLASS RUNG: integer-angle library R2 {r2_int:.3f} (fails) vs half-angle library R2 {r2_half:.4f} (catches cos(a/2)): {g1}")
    print(f"G2 DOUBLE-COVER CERTIFICATE: from SO(3) Bloch observables R2 {r2_bloch:.3f} (fails); Bloch(a)==Bloch(a+2pi) gap {bloch_gap:.1e}, "
          f"interference exactly opposite {sign_flip:.1e} -> sign unobservable: {g2}")
    print(f"G3 THE 720 DEGREES: interference at 360deg {I_360:+.4f} (destructive), 720deg {I_720:+.4f} (constructive); "
          f"Bloch already repeats at 2pi ({bloch_period_repeat:.1e}): {g3}")
    print(f"\nSPINOR DOUBLE COVER CAUGHT (the half-angle sheet is a required new function class; the sign is an SO(3)-invisible certificate): {out['double_cover_caught']}")
    (Path(__file__).resolve().parent.parent / "results" / "98_spinor_double_cover.json").write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(1, 2, figsize=(13, 5))
    a = np.linspace(0, 4 * np.pi, 800); bx, by, bz, I = observables(a)
    ax[0].plot(a / np.pi, bx, color="navy", label="Bloch ⟨σx⟩ = cos α  (SO(3), 2π-periodic)")
    ax[0].plot(a / np.pi, I, color="crimson", lw=2, label="interference = cos(α/2)  (spinor, 4π-periodic)")
    for xp in (2, 4):
        ax[0].axvline(xp, color="gray", ls=":", lw=0.8)
    ax[0].axhline(0, color="k", lw=0.4)
    ax[0].annotate("360°: −1\n(destructive)", (2, -1), (2.1, -0.6), fontsize=8, color="crimson")
    ax[0].annotate("720°: +1\n(constructive)", (4, 1), (3.0, 0.5), fontsize=8, color="crimson")
    ax[0].set_xlabel("rotation angle α  (units of π)"); ax[0].set_ylabel("signal")
    ax[0].legend(fontsize=8, loc="lower left"); ax[0].set_title("The Bloch vector returns at 360°; the spinor needs 720°.\nThe interference (half-angle) lives on the double cover's other sheet.")

    labels = ["integer-angle\n(SO(3) class)", "half-angle\n(double cover)", "Bloch\nobservables"]
    ax[1].bar(labels, [r2_int, r2_half, r2_bloch], color=["navy", "crimson", "gray"])
    ax[1].axhline(0.999, color="seagreen", ls=":", label="represents the spinor interference")
    ax[1].set_ylabel("held-out R² representing cos(α/2)"); ax[1].set_ylim(-0.05, 1.05)
    ax[1].legend(fontsize=8); ax[1].set_title("Only the half-angle feature class represents the spinor;\nthe SO(3) observables cannot see the sign (the certificate).")
    fig.tight_layout(); fig.savefig(Path(__file__).resolve().parent.parent / "results" / "98_spinor_double_cover.png", dpi=140)
    print("saved results/98_spinor_double_cover.json + .png")


if __name__ == "__main__":
    main()
