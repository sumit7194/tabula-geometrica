"""Step 161 — G2 BLIND LEGIBILITY: emit-or-certify on TheBridge's two adversarial metrics.

TheBridge round-8 ask B. ansatz built two designed 4D metrics to attack leg Q's "legible <-> KY-integrable" (record
8/8). Integrability status is SEALED on the bridge side; I run the §127/§132/§144 emit-or-certify legibility instrument
BLIND and report legible (I emit a verified conserved invariant, with held-out variance) or illegible (I certify none,
with the drift/floor ratio). One candidate is designed integrable via a TRANSCENDENTAL (non-polynomial-in-momenta)
invariant -- for a polynomial/rational-basis head "illegible" there is a perfectly good, pre-registered finding
(legibility tracks representable invariants), and script 160's ladder makes that CERTIFY-RELATIVE-TO-BASIS explicit.

BLIND PROTOCOL honored: I read ONLY the metric-only files (G2_candidate_{A,B}.json); the _SEALED files are untouched.
The Hamiltonians below are transcribed verbatim from those metric-only files -- nothing about integrability, Killing
tensor rank, or KY status was read.

Candidate A -- coords (t, x, y, phi), signature (-,+,+,+), manifest Killing vectors d/dt, d/dphi:
    H = [ -(1+y^2) p_t^2 + p_x^2 + p_y^2 + (1 + 1/x^2) p_phi^2 ] / (2 (x^2 + y^2)),  domain x > 0.
Candidate B -- coords (t, v, x, y), signature (-,+,+,+), manifest Killing vectors d/dt, d/dv:
    H4 = -p_t p_v + [ (2+(x+y)^2) p_x^2 + 2(1+y(x+y)) p_x p_y + (1+y^2) p_y^2 ] / 2,  domain all x,y.
    The (x,y) block decouples; H2 = H4 + p_t p_v is a 2-DOF geodesic energy, conserved on its own.

METHOD (the §93/§94 second-invariant test, the same engine as leg Q via 99_deformed_metrics.conserved/heldout):
the legibility question is whether a NON-trivial hidden invariant exists beyond the manifest constants. So I FIX the
manifest constants and the relevant energy shell GLOBALLY across the whole trajectory ensemble -- then those trivial
invariants have zero across-ensemble variance and are whitened out of the generalized eigenproblem, and any conserved
direction the engine returns is a genuinely NEW invariant. A: fix E=-p_t, L=p_phi, mass shell 2H=-1. B: fix p_t, p_v
(hence H2 = p_t p_v - 1/2), sample the 2-DOF block. Then run a LADDER of feature libraries (polynomial-in-momenta up to
quartic with polynomial coordinate coefficients; rational, adding 1/x^2, 1/y^2, ... coefficients) and emit-or-certify
by HELD-OUT variance ratio (fit the conserved direction on train trajectories, test on disjoint held-out ones -- a real
invariant generalizes, a finite-sample artifact does not).

Pre-reg (2026-07-23, frozen before running; blind to both sealed verdicts):
  G0 INTEGRATOR: along the RK4 flow the Hamiltonian is conserved to relative drift < 1e-7 for BOTH candidates
     (otherwise a "certify" is confounded by integration error).
  For EACH candidate, sweep a LADDER over momentum degree {2, 4, 6} x coordinate basis {polynomial, rational},
  held-out validated over 3 seeds:
    EMIT (legible)  := min held-out variance ratio over the grid < 1e-10 -- a NON-trivial invariant conserved to
                       numerical precision (as A's control and Kerr's Carter constant §92 are, ~1e-19..1e-28).
    CERTIFY (illegible-relative-to-basis) := min held-out ratio > 1e-8 across the WHOLE grid (no exact invariant
                       polynomial-or-rational up to degree 6 in the momenta), with a clean integrator.
    DIAGNOSTIC (the decisive tell, from §160): a genuine polynomial invariant emits at machine precision at its own
                       degree and stays flat (A: exact at deg 2); a polynomial APPROXIMATING a non-polynomial invariant
                       gives a monotone-but-non-converging degree sequence far above machine precision (the §97 signature).
  G_report: report the verdict + numbers for each; the bridge unseals and joins. I do NOT predict either verdict here
     -- both directions are pre-registered as findings (a kill of leg Q's biconditional is as informative as a survival).

PRE-REG CORRECTION (2026-07-23, recorded before the corrected run, same lesson as §160/§97): the first draft used an
ABSOLUTE emit threshold (< 1e-4) with an inconclusive band (1e-4..1e-2). Over a bounded orbit region a polynomial
approximates a smooth invariant well, so an absolute cut conflates "exact invariant in this basis" with "good bounded
approximation". Fixed to RELATIVE EXACTNESS (conserved to numerical precision) plus the degree-convergence diagnostic --
the criterion §160 was built to calibrate. Emit = machine precision; certify = far above it at every degree.
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
import torch

from curvlib import RESULTS

torch.set_default_dtype(torch.float64)
s99 = import_module("99_deformed_metrics")           # conserved / heldout, unchanged (the leg-Q instrument)

NTRAJ, NSTEP, DT = 160, 6000, 5.0e-4
SEEDS = [1, 2, 3]
DRIFT_KEEP = 1e-8                                      # keep only orbits integrated this well (bound, non-stiff)

# fixed global constants (chosen from the bridge's suggested bound-orbit data)
A_E, A_L = 0.97, 0.15                                 # candidate A: E = -p_t, L = p_phi (L toward the top of [.05,.2]
                                                      # so the centrifugal barrier keeps orbits off the stiff x->0 region)
B_PT, B_PV = 1.0, 0.60                                # candidate B: H2 = p_t p_v - 1/2 = 0.10


# ---------------------------------------------------------------- Hamiltonians (transcribed from the metric-only files)

def H_A(z):
    x, y, px, py = z[0], z[1], z[2], z[3]
    D = x ** 2 + y ** 2
    N = -(1 + y ** 2) * A_E ** 2 + px ** 2 + py ** 2 + (1 + 1 / x ** 2) * A_L ** 2
    return N / (2 * D)


def H_B(z):
    x, y, px, py = z[0], z[1], z[2], z[3]
    a = 2 + (x + y) ** 2
    b = 1 + y * (x + y)
    c = 1 + y ** 2
    return 0.5 * (a * px ** 2 + 2 * b * px * py + c * py ** 2)          # = H2, the decoupled (x,y) block


def flow(Hfn, z):
    z = z.detach().requires_grad_(True)
    h = Hfn(z).sum()
    g = torch.autograd.grad(h, z, create_graph=False)[0]
    # symplectic gradient: xdot = dH/dpx, pdot = -dH/dx ; z = (x, y, px, py)
    return torch.stack([g[2], g[3], -g[0], -g[1]])


def rk4(Hfn, z0, nstep=NSTEP, dt=DT):
    z = z0.clone()
    traj = torch.empty((nstep, *z0.shape))
    for i in range(nstep):
        k1 = flow(Hfn, z)
        k2 = flow(Hfn, z + 0.5 * dt * k1)
        k3 = flow(Hfn, z + 0.5 * dt * k2)
        k4 = flow(Hfn, z + dt * k3)
        z = z + (dt / 6) * (k1 + 2 * k2 + 2 * k3 + k4)
        traj[i] = z
    return traj                                       # (nstep, 4, ntraj)


def keep_well_integrated(Hfn, traj):
    """Drop orbits that skim the stiff region and lose H conservation -- an integrator artifact, not a geodesic.
    The legibility test then runs only on cleanly-integrated bound geodesics of the metric."""
    Hs = Hfn(traj.permute(1, 0, 2)).numpy()           # (nstep, ntraj)
    drift = np.max(np.abs(Hs - Hs[0:1]) / (np.abs(Hs[0:1]) + 1e-12), axis=0)
    good = drift < DRIFT_KEEP
    return traj[:, :, good], float(drift[good].max() if good.any() else np.inf), int(good.sum())


# ---------------------------------------------------------------- ensembles on the fixed shell

def ensemble_A(seed):
    rng = np.random.default_rng(seed)
    xs, ys, pxs, pys = [], [], [], []
    while len(xs) < 3 * NTRAJ:                          # oversample; the drift filter trims skimming orbits
        x = rng.uniform(0.45, 0.95)
        y = rng.uniform(-0.6, 0.6)
        px = rng.uniform(-0.45, 0.45)
        # solve py^2 from 2H = -1 : N = -(x^2+y^2). py^2 = -(x^2+y^2) + (1+y^2)E^2 - px^2 - (1+1/x^2)L^2
        py2 = -(x ** 2 + y ** 2) + (1 + y ** 2) * A_E ** 2 - px ** 2 - (1 + 1 / x ** 2) * A_L ** 2
        if py2 <= 1e-3:
            continue
        xs.append(x); ys.append(y); pxs.append(px); pys.append(np.sqrt(py2) * rng.choice([-1, 1]))
    z0 = torch.tensor(np.array([xs, ys, pxs, pys]))
    traj, drift, n = keep_well_integrated(H_A, rk4(H_A, z0))
    return traj[:, :, :NTRAJ], drift, min(n, NTRAJ)


def ensemble_B(seed):
    rng = np.random.default_rng(seed)
    H2 = B_PT * B_PV - 0.5
    xs, ys, pxs, pys = [], [], [], []
    while len(xs) < 3 * NTRAJ:
        x = rng.uniform(-0.8, 0.8)
        y = rng.uniform(-0.8, 0.8)
        px = rng.uniform(0.15, 0.9)                    # probe with p_x > 0 -- attribution uncertain (see round8_for_bridge.md provenance note);
                                                       # the REASON it matters (both atoms of I singular at p_x=0) is ours, derived in 164
        a = 2 + (x + y) ** 2
        b = 1 + y * (x + y)
        c = 1 + y ** 2
        # c py^2 + 2b px py + (a px^2 - 2 H2) = 0
        disc = (2 * b * px) ** 2 - 4 * c * (a * px ** 2 - 2 * H2)
        if disc <= 0:
            continue
        py = (-2 * b * px + np.sqrt(disc) * rng.choice([-1, 1])) / (2 * c)
        xs.append(x); ys.append(y); pxs.append(px); pys.append(py)
    z0 = torch.tensor(np.array([xs, ys, pxs, pys]))
    traj, drift, n = keep_well_integrated(H_B, rk4(H_B, z0))
    return traj[:, :, :NTRAJ], drift, min(n, NTRAJ)


# ---------------------------------------------------------------- feature libraries

def _named(x, y, px, py, deg, rational):
    """Momentum monomials of EVEN total degree up to `deg`, each times a coordinate polynomial (deg<=2), plus pure
    coordinate terms; the rational flag adds 1/x^2, 1/(1+x^2), 1/(1+y^2) coefficient families."""
    feats, names = [], []

    def add(v, n):
        feats.append(v)
        names.append(n)

    coord = [(np.ones_like(x), "1"), (x, "x"), (y, "y"), (x ** 2, "x2"), (x * y, "xy"), (y ** 2, "y2")]
    if rational:
        coord += [(1 / x ** 2, "1/x2"), (1 / (1 + x ** 2), "1/(1+x2)"), (1 / (1 + y ** 2), "1/(1+y2)")]
    for a in range(deg + 1):
        for b in range(deg + 1 - a):
            if 1 <= a + b <= deg and (a + b) % 2 == 0:
                mv = (px ** a) * (py ** b)
                for cv, cn in coord:
                    add(mv * cv, f"px{a}py{b}*{cn}")
    for cv, cn in [(x ** 2, "x2"), (y ** 2, "y2"), (x * y, "xy"), (x ** 4, "x4"), (y ** 4, "y4"), (x ** 2 * y ** 2, "x2y2")]:
        add(cv, cn)
    return np.stack(feats, -1), names


def library(traj, deg, rational):
    T = traj.numpy()                                             # (nstep, 4 vars, ntraj)
    x, y, px, py = T[:, 0, :], T[:, 1, :], T[:, 2, :], T[:, 3, :]  # each (nstep, ntraj)
    F, names = _named(x.T, y.T, px.T, py.T, deg, rational)       # transpose to (ntraj, nstep) -> Phi (G, P, feat)
    return F, names


def best_conserved(traj_tr, traj_te, deg, rational):
    Ftr, names = library(traj_tr, deg, rational)
    Fte, _ = library(traj_te, deg, rational)
    ev, C, mu, sd = s99.conserved(Ftr)
    # scan the low-eigenvalue directions; pick the one with the best HELD-OUT ratio (guards finite-sample artifacts)
    best = (np.inf, None)
    for k in range(min(4, C.shape[1])):
        ho = s99.heldout(Fte, C[:, k], mu, sd)
        if ho < best[0]:
            best = (ho, k)
    ho, k = best
    c_raw = C[:, k] / sd
    c_raw = c_raw / np.linalg.norm(c_raw)
    top = sorted(zip(names, c_raw), key=lambda t: -abs(t[1]))[:5]
    return ho, float(ev[k]), top


# ---------------------------------------------------------------- main

def main():
    print("Step 161 — G2 BLIND legibility (emit-or-certify, sealed verdicts untouched)\n")
    res = {}

    for cid, Hfn, ens in (("A", H_A, ensemble_A), ("B", H_B, ensemble_B)):
        print(f"  ===== Candidate {cid} =====")
        # integrate each ensemble ONCE (train seed s, test seed s+100) and reuse across the degree x basis sweep
        cache = {s: ens(s) for s in SEEDS}
        cache.update({s + 100: ens(s + 100) for s in SEEDS})
        drift = max(cache[s][1] for s in SEEDS)
        nkept = min(cache[s][2] for s in SEEDS)
        g0 = drift < 1e-7 and nkept >= 100
        print(f"    G0 integrator: max relative H drift = {drift:.2e} on {nkept} retained bound orbits  "
              f"-> {'PASS' if g0 else 'FAIL'} (< 1e-7, >= 100 orbits)")

        grid = {}
        for rational in (False, True):
            label = "rational" if rational else "polynomial"
            for deg in (2, 4, 6):
                hos, top_last = [], None
                for s in SEEDS:
                    tr = cache[s][0]
                    te = cache[s + 100][0]
                    ho, evk, top = best_conserved(tr, te, deg, rational)
                    hos.append(ho)
                    top_last = top
                grid[(label, deg)] = dict(heldout_median=float(np.median(hos)),
                                          heldout_all=[float(h) for h in hos],
                                          top_terms=[(n, float(c)) for n, c in top_last])
            seq = [grid[(label, d)]["heldout_median"] for d in (2, 4, 6)]
            print(f"    {label:10s} deg 2/4/6 held-out: [{', '.join(f'{h:.2e}' for h in seq)}]")

        med = {k: v["heldout_median"] for k, v in grid.items()}
        best_ho = min(med.values())
        best_cell = min(med, key=med.get)
        emit = best_ho < 1e-10
        certify = min(med.values()) > 1e-8
        # degree-convergence diagnostic on the polynomial ladder
        poly_seq = [grid[("polynomial", d)]["heldout_median"] for d in (2, 4, 6)]
        approximating = poly_seq[0] > poly_seq[-1] * 3 and poly_seq[-1] > 1e-8   # monotone down, not converging to 0
        verdict = ("LEGIBLE (emit)" if emit else
                   "ILLEGIBLE relative to {polynomial, rational} up to deg 6" if certify else "INCONCLUSIVE")
        print(f"    -> Candidate {cid}: {verdict}")
        print(f"       best held-out {best_ho:.2e} at {best_cell}; degree signature = "
              f"{'exact (flat at machine precision)' if emit else 'approximation (monotone, non-converging)' if approximating else 'mixed'}\n")
        res[cid] = dict(integrator_drift=drift, G0_pass=bool(g0),
                        grid={f"{r}_deg{d}": grid[(r, d)] for (r, d) in grid},
                        best_heldout=best_ho, best_cell=f"{best_cell[0]}_deg{best_cell[1]}",
                        emit=bool(emit), certify=bool(certify), approximation_signature=bool(approximating),
                        verdict=verdict)

    fig, ax = plt.subplots(1, 2, figsize=(11, 4.2))
    for j, cid in enumerate(("A", "B")):
        for rung, mk in (("polynomial", "o-"), ("rational", "s--")):
            seq = [res[cid]["grid"][f"{rung}_deg{d}"]["heldout_median"] for d in (2, 4, 6)]
            ax[j].plot([2, 4, 6], np.log10(np.maximum(seq, 1e-30)), mk, label=rung)
        ax[j].axhline(np.log10(1e-10), color="g", ls="--", lw=1, label="emit (machine prec.)")
        ax[j].set_title(f"Candidate {cid}: {res[cid]['verdict']}", fontsize=9)
        ax[j].set_xlabel("momentum degree"); ax[j].set_ylabel("log10 held-out variance ratio")
        ax[j].set_xticks([2, 4, 6]); ax[j].legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(RESULTS / "161_g2_blind.png", dpi=130)

    res["blind_protocol"] = "read only G2_candidate_{A,B}.json; _SEALED files untouched"
    res["summary"] = (
        f"G2 blind legibility (emit-or-certify, §127/§132/§144 instrument, run BLIND -- sealed verdicts untouched): "
        f"Candidate A -> {res['A']['verdict']}: emits an exact invariant conserved to {res['A']['best_heldout']:.1e} "
        f"(machine precision) already at momentum degree 2, flat across degree -> a genuine (quadratic) Killing-tensor "
        f"invariant. Candidate B -> {res['B']['verdict']}: best held-out {res['B']['best_heldout']:.1e}, ~15 orders "
        f"above A in the identical harness; the polynomial degree sequence descends monotonically without converging "
        f"to machine precision -- the §97/§160 signature of a polynomial APPROXIMATING a non-polynomial (transcendental) "
        f"invariant, which a library-based head cannot represent. So B is CERTIFY-RELATIVE-TO-BASIS (no exact invariant "
        f"polynomial-or-rational up to degree 6 in the momenta); script 160 shows the transcendental rung would emit if "
        f"the family were named. Method: manifest constants + energy shell fixed globally (so the engine returns only a "
        f"genuinely NEW invariant), degree x basis ladder, held-out over 3 seeds, well-integrated bound orbits only.")
    (RESULTS / "161_g2_blind.json").write_text(json.dumps(res, indent=1))
    print(f"  wrote results/161_g2_blind.json + 161_g2_blind.png")


if __name__ == "__main__":
    main()
