"""Step 196 -- established chaos indicators (MEGNO, SALI, FLI) as the third method after §195's honest negative.
Plan: notes/established_indicator_plan.md (reviewed by The Bridge).

Tangent dynamics are EXACT via complex-step differentiation, J.v = Im f(z + i h v) / h with h = 1e-30 (no
subtractive cancellation). The generated reduced RHS is analytic (no abs/sign/where; checked), and only 193's
`.astype(float)` blocked complex input, so this file carries its own complex-safe copy of the RHS.

    .venv314ob/bin/python scripts/196_chaos_indicators.py --validate     # J.v vs Richardson FD (+ HH exact Jacobian)
"""

import argparse
import json
import sys
from importlib import import_module
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

m = import_module("195_invariant_learnability")         # BLAS threads = 1; 193's OpenBLAS tripwire
import numpy as np                                        # noqa: E402

m94, s193 = m.m94, m.s193
RESULTS = Path(__file__).resolve().parent.parent / "results"
H_CS = 1e-30


def rhs_c(mdl, z):
    """The reduced geodesic RHS of 193's Reduced.rhs, complex-safe. HH (no .st) is a polynomial and already safe."""
    if not hasattr(mdl, "st"):
        return mdl.rhs(z)
    x, y, px, py = z
    o = [np.broadcast_to(v, np.shape(x)).astype(np.result_type(x, float)) for v in mdl.st._f(x, y)]
    a, b, c = mdl.w
    Vx, Vy = (a * o[i] + b * o[i + 3] + c * o[i + 6] for i in (1, 2))
    gxx, gxxx, gxxy, gyy, gyyx, gyyy = o[9:15]
    return np.stack([gxx * px, gyy * py,
                     -(0.5 * (gxxx * px ** 2 + gyyx * py ** 2) + Vx),
                     -(0.5 * (gxxy * px ** 2 + gyyy * py ** 2) + Vy)])


def jvp(mdl, z, v):
    """Exact Jacobian-vector product of the RHS (complex step)."""
    return np.imag(rhs_c(mdl, z + 1j * H_CS * v)) / H_CS


def _fd(mdl, z, v, eps):
    return (mdl.rhs(z + eps * v) - mdl.rhs(z - eps * v)) / (2 * eps)


def hh_jac(z):
    x, y, _, _ = z
    J = np.zeros((4, 4) + np.shape(x))
    J[0, 2] = J[1, 3] = 1.0
    J[2, 0], J[2, 1] = -(1 + 2 * y), -2 * x
    J[3, 0], J[3, 1] = -2 * x, -(1 - 2 * y)
    return J


def sample_states(mdl, n, T=2000.0, dt=0.05):
    """Generic on-shell states: seeds, then a short integration, so y and px are nonzero."""
    if not hasattr(mdl, "st"):
        z0 = mdl.launch(n, np.random.default_rng(3))
    else:
        reg = m94.seed_region(mdl.st, mdl.E, mdl.L) if hasattr(mdl, "st") else None
        z0, _ = m94.seeds(mdl, np.linspace(reg[0], reg[1], n))
    res = m94.integrate(mdl, z0, T, dt, 100, twin=False)
    S = res["samples"][:, -1, :]
    return S[:, np.isfinite(S).all(0)]


def validate():
    sts, _ = m94.spacetimes("t1o3")
    zv = s193.Spacetime(*s193.zv2_components(), "ZV2")
    E = 0.97
    models = {"Kerr": sts["Kerr"].at(E, -m94.l_sep(sts["Kerr"], E, -1) * 1.005),
              "TS2": sts["TS2"].at(E, -m94.l_sep(sts["TS2"], E, -1) * 1.005),
              "ZV2": zv.at(0.95, 1.5), "HH": m94.HenonHeiles(1 / 12)}
    out = {}
    rng = np.random.default_rng(11)
    for name, mdl in models.items():
        z = sample_states(mdl, 12, dt=0.0025 if name == "HH" else 0.05)
        v = rng.standard_normal(z.shape)
        v /= np.linalg.norm(v, axis=0)
        cs = jvp(mdl, z, v)
        scale = np.abs(cs).max(0) + 1e-300
        rich = {}
        for e in (1e-3, 1e-4, 1e-5):                      # Richardson: (4 D(e/2) - D(e)) / 3, removes O(e^2)
            eps = e * (np.abs(z).max(0) + 1)
            d1, d2 = _fd(mdl, z, v, eps), _fd(mdl, z, v, eps / 2)
            rich[e] = float(np.max(np.abs((4 * d2 - d1) / 3 - cs).max(0) / scale))
        rec = {"n_states": int(z.shape[1]), "rel_err_vs_richardson": rich}
        if name == "HH":
            Jv = np.einsum("ijk,jk->ik", hh_jac(z), v)
            rec["rel_err_vs_exact"] = float(np.max(np.abs(Jv - cs).max(0) / scale))
        out[name] = rec
        print(name, rec, flush=True)
    (RESULTS / "196_validate_tangent.json").write_text(json.dumps(out, indent=1))


# ---------------------------------------------------------------- MEGNO / FLI / SALI integrator

CHECK = (1e2, 3e2, 1e3, 3e3, 1e4, 3e4, 1e5, 1.5e5)
NVEC = 4                                   # two independent random pairs (Breiter: initial-vector dependence)


def indicators(mdl, z0, T, dt, seed):
    """RK4 on (z, w_1..w_4), w' = J(z) w exactly (complex step). Each vector is renormalised every step.
    MEGNO (Cincotta & Simo 2000): Y(t) = (2/t) int_0^t s*lam(s) ds with lam = w.Jw/|w|^2; <Y>(t) = (1/t) int_0^t Y.
    FLI = max over s <= t of the cumulative log-growth. SALI_pair = min(|w_a + w_b|, |w_a - w_b|) for normalised w.
    Returns, per checkpoint t <= T: <Y>, FLI and SALI for both pairs (NaN after a plunge), plus t_plunge and H drift."""
    G = z0.shape[1]
    rng = np.random.default_rng(seed)
    W = rng.standard_normal((NVEC, 4, G))
    W /= np.linalg.norm(W, axis=1, keepdims=True)
    z = z0.astype(float).copy()
    H0 = mdl.H(z)
    alive, t_plunge, hdrift = np.ones(G, bool), np.full(G, np.inf), np.zeros(G)
    logg = np.zeros((NVEC, G))
    fli = np.zeros((NVEC, G))
    I = np.zeros((NVEC, G))
    S = np.zeros((NVEC, G))
    lam_prev = np.zeros((NVEC, G))
    Y_prev = np.zeros((NVEC, G))
    nstep = int(round(T / dt))
    checks = {int(round(c / dt)): c for c in CHECK if c <= T}
    rec = {}

    def F(zz, ww):
        """One complex RHS call for all vectors: Re -> f(z) (exact; h^2 ~ 1e-60), Im/h -> J w_k."""
        Zr = np.broadcast_to(zz[:, None, :], (4, NVEC, G)).reshape(4, NVEC * G)
        c = rhs_c(mdl, Zr + 1j * H_CS * ww.transpose(1, 0, 2).reshape(4, NVEC * G))
        return np.real(c[:, :G]), (np.imag(c) / H_CS).reshape(4, NVEC, G).transpose(1, 0, 2)

    for i in range(1, nstep + 1):
        k1z, k1w = F(z, W)
        lam = np.einsum("kig,kig->kg", W, k1w)         # rate at t_{i-1} (|w| = 1): reuses RK stage 1
        if i > 1:
            t = (i - 1) * dt
            I = I + 0.5 * ((t - dt) * lam_prev + t * lam) * dt
            Y = 2 * I / t
            S = S + 0.5 * (Y_prev + Y) * dt if i > 2 else S + Y * dt
            Y_prev = Y
        lam_prev = lam
        k2z, k2w = F(z + 0.5 * dt * k1z, W + 0.5 * dt * k1w)
        k3z, k3w = F(z + 0.5 * dt * k2z, W + 0.5 * dt * k2w)
        k4z, k4w = F(z + dt * k3z, W + dt * k3w)
        zn = z + dt / 6 * (k1z + 2 * k2z + 2 * k3z + k4z)
        Wn = W + dt / 6 * (k1w + 2 * k2w + 2 * k3w + k4w)
        fin = np.isfinite(zn).all(0) & np.isfinite(Wn).all((0, 1))
        if mdl.sig is not None:
            fin &= (1 + mdl.sig * np.where(fin, zn[0], 0.0)) >= m94.R_PLUNGE
        t_plunge[alive & ~fin] = i * dt
        alive &= fin
        z = np.where(alive, zn, z)
        nrm = np.where(alive, np.linalg.norm(Wn, axis=1), 1.0)
        W = np.where(alive, Wn / nrm[:, None, :], W)
        logg = logg + np.log(nrm)
        fli = np.maximum(fli, logg)
        if i % 10 == 0:
            hdrift = np.where(alive, np.maximum(hdrift, np.abs(mdl.H(z) - H0) / np.abs(H0)), hdrift)
        if i in checks:
            tc = max((i - 1) * dt, dt)
            sali = np.stack([np.minimum(np.linalg.norm(W[a] + W[b], axis=0), np.linalg.norm(W[a] - W[b], axis=0))
                             for a, b in ((0, 1), (2, 3))])
            dead = ~alive
            mY, fl, sl = S / tc, fli.copy(), sali.copy()
            mY[:, dead], fl[:, dead], sl[:, dead] = np.nan, np.nan, np.nan
            rec[checks[i]] = {"megno": mY.tolist(), "fli": fl.tolist(), "sali": sl.tolist()}
    return {"checkpoints": rec, "t_plunge": t_plunge.tolist(), "hdrift": hdrift.tolist()}


# ---------------------------------------------------------------- measurement (plan; distributions, not verdicts)

OUTD = RESULTS / "196_measure"
DRIFT_TARGET = 1e-10                       # pilot max |dH/H| over T; 10x margin under the 1e-9 acceptance cut


def pilot_dt(mdl, z, T):
    """Halve from 0.05 until a 12-orbit pilot's max H drift over T is <= DRIFT_TARGET (pilot used for nothing else)."""
    dt = 0.05
    while True:
        res = m94.integrate(mdl, z[:, :12], T, dt, max(1, int(round(0.5 / dt))), twin=False)
        drift = float(np.max(res["hdrift"][~np.isfinite(res["t_plunge"])], initial=0.0))
        if drift <= DRIFT_TARGET or dt < 1e-3:
            return dt, drift
        dt /= 2


# Plunge geometry (2026-10-11, The Bridge's catch, verified here against exact BPT): 194's universal cut r < 3m sits
# OUTSIDE the prograde barrier (unstable circular orbit at r 2.1-2.9), so its pocket-based l_sep came from the CUT
# (+0.7..+7% prograde; retro exact) and "plunges" there were cut artifacts. Here: L_sep from the barrier itself, and
# a per-level cut midway between the horizon (x = 1) and the barrier; ZV (no barrier outside x = 1) uses V11's x < 1.5.

def barrier(mdl, r_hi=14.0):
    """Outermost local maximum of the equatorial potential V(r; E, L) for x > 1 (the barrier facing the pocket)."""
    r = np.linspace(1 + mdl.sig * 1.0005, r_hi, 200000)
    x = (r - 1) / mdl.sig
    V = mdl.parts(x, np.zeros_like(x))[0]
    ok = np.isfinite(V)
    idx = np.where(ok[1:-1] & ok[:-2] & ok[2:] & (V[1:-1] > V[:-2]) & (V[1:-1] >= V[2:]) & (V[1:-1] < 100))[0] + 1
    return (float(r[idx[-1]]), float(V[idx[-1]])) if len(idx) else (None, None)   # V < 100: excludes TS's
                                                                                  # near-singular x ~ 1 peaks (V ~ 1e6)


def l_sep_barrier(st, E, sense, lo=1.0, hi=6.0):
    """L at which the barrier peak equals the shell value -1/2 (the unstable circular orbit of energy E)."""
    f = lambda L: (barrier(st.at(E, sense * L))[1] or -np.inf) + 0.5
    if f(hi) < 0:
        return None
    a, b = lo, hi
    if f(a) > 0:
        raise ValueError(f"barrier already closed at L = {lo}: widen the bracket")
    for _ in range(50):
        c = 0.5 * (a + b)
        a, b = (c, b) if f(c) < 0 else (a, c)
    return 0.5 * (a + b)


def bpt_L(a, E, pro):
    """Exact Kerr (M = 1) unstable circular equatorial orbit of energy E (Bardeen-Press-Teukolsky): |L|."""
    from scipy.optimize import brentq
    s = 1 if pro else -1

    def EL(r):
        den = r ** 0.75 * np.sqrt(r ** 1.5 - 3 * r ** 0.5 + s * 2 * a)
        return (r ** 1.5 - 2 * r ** 0.5 + s * a) / den, (r * r - s * 2 * a * r ** 0.5 + a * a) / den
    rph = 2 * (1 + np.cos(2 / 3 * np.arccos(-s * a)))
    Z1 = 1 + (1 - a * a) ** (1 / 3) * ((1 + a) ** (1 / 3) + (1 - a) ** (1 / 3))
    Z2 = np.sqrt(3 * a * a + Z1 * Z1)
    risco = 3 + Z2 - s * np.sqrt((3 - Z1) * (3 + Z1 + 2 * Z2))
    try:
        r = brentq(lambda r: EL(r)[0] - E, rph * 1.0001, risco)
    except ValueError:
        return None
    return float(EL(r)[1])


def r_cut_for(mdl):
    rb, _ = barrier(mdl)
    rplus = 1 + mdl.sig
    return rplus + 0.5 * (rb - rplus) if rb else rplus + 0.5


def level_model(system, tag, E, sense, eps, Lscale=None):
    """Levels relative to the BARRIER separatrix (gated against BPT for Kerr); sets the per-level plunge cut."""
    if system == "SCHW":
        st = s193.Spacetime(s193.kerr_components(0, 1), 1, "SCHW")
    else:
        st = m94.spacetimes(tag)[0][system]
    ls = l_sep_barrier(st, E, sense)
    L = sense * ls * (Lscale if Lscale else (1 + eps))
    mdl = st.at(E, L)
    rb, Vb = barrier(mdl)
    m94.R_PLUNGE = r_cut_for(mdl)                        # process-local (spawn worker); used by integrate/seeding
    return mdl, {"l_sep": ls, "L": L, "r_barrier": rb, "V_barrier": Vb, "r_cut": m94.R_PLUNGE,
                 "l_sep_old_cutbased": m94.l_sep(st, E, sense)}


def seeds_offset(mdl, n, frac):
    """Equatorial seeds in the outer allowed region, outside the barrier (inside it they plunge at once)."""
    reg = m94.seed_region(mdl.st, mdl.E, mdl.L)
    rb = barrier(mdl)[0]
    reg = (max(reg[0], (rb or 0) * 1.02), reg[1])
    step = (reg[1] - reg[0]) / (n - 1)
    z, r0 = m94.seeds(mdl, np.linspace(reg[0] + frac * step, reg[1] - frac * step, n))
    return z, r0


def job_run(job):
    name, T = job["name"], job["T"]
    kind = job["kind"]
    meta = {k: v for k, v in job.items()}
    if kind == "kerrlike":
        mdl, info = level_model(job["system"], job.get("tag"), job["E"], job["sense"], job.get("eps", 0.0),
                                job.get("Lscale"))
        z, r0 = seeds_offset(mdl, job["n"], 1 / 7)
        meta.update(info, r0=list(map(float, r0)))
    elif kind == "hh":
        mdl = m94.HenonHeiles(job["E"])
        z = mdl.launch(job["n"], np.random.default_rng(job["seed"]))
    else:                                                  # zv: explicit (x0, L) list, E fixed
        zv = s193.Spacetime(*s193.zv2_components(), "ZV2")
        m94.R_PLUNGE = 1 + zv.sig * 1.5                  # no barrier outside x = 1; V11's plunge cut x < 1.5
        meta["r_cut"] = m94.R_PLUNGE
        cols, Ls = [], sorted({L for _, L in job["orbits"]})
        mdl = None
        out_all = []
        for L in Ls:
            mdl = zv.at(job["E"], L)
            xs = np.array([x for x, LL in job["orbits"] if LL == L])
            py2 = mdl.py2_on_shell(xs, np.zeros_like(xs), np.zeros_like(xs))
            zz = np.array([xs, np.zeros_like(xs), np.zeros_like(xs), np.sqrt(np.clip(py2, 0, None))])
            dt, drift = pilot_dt(mdl, np.repeat(zz, 12 // zz.shape[1] + 1, axis=1)[:, :12], T)
            r = indicators(mdl, zz, T, dt, job["seed"])
            lab = m94.integrate(mdl, zz, T, dt, max(1, int(round(0.5 / dt))), twin=True)
            r.update({"L": L, "x0": xs.tolist(), "dt": dt, "pilot_drift": drift, "ftle": lab["ftle"].tolist()})
            out_all.append(r)
        meta["parts"] = out_all
        (OUTD / f"{name}.json").write_text(json.dumps(meta, default=float))
        return name
    dt, drift = pilot_dt(mdl, z, T)
    r = indicators(mdl, z, T, dt, job["seed"])
    if kind == "hh":                                       # truth labels: twin FTLE + section gap (pre-registration)
        lab = m94.integrate(mdl, z, T, dt, max(1, int(round(0.5 / dt))), twin=True)
        r["ftle"] = lab["ftle"].tolist()
        r["section_gap"] = [m94b_gap(m.valid(lab, g)) for g in range(z.shape[1])]
    meta.update(r, dt=dt, pilot_drift=drift)
    (OUTD / f"{name}.json").write_text(json.dumps(meta, default=float))
    return name


def m94b_gap(Z):
    g = m.m94b.section_coverage(Z)[1] if len(Z) > 10 else None
    return None if g is None else float(g)


JOBS = [
    {"name": "kerr_sep_p45_E097_pro", "kind": "kerrlike", "system": "Kerr", "tag": "t1o3", "E": 0.97, "sense": -1,
     "eps": -0.01, "n": 40, "T": 3e4, "seed": 101},
    {"name": "kerr_sep_p45_E097_retro", "kind": "kerrlike", "system": "Kerr", "tag": "t1o3", "E": 0.97, "sense": 1,
     "eps": -0.01, "n": 20, "T": 3e4, "seed": 102},
    {"name": "kerr_sep_p35_E095_pro", "kind": "kerrlike", "system": "Kerr", "tag": "t1o2", "E": 0.95, "sense": -1,
     "eps": -0.01, "n": 20, "T": 3e4, "seed": 103},
    {"name": "kerr_generic_p45_E097_pro", "kind": "kerrlike", "system": "Kerr", "tag": "t1o3", "E": 0.97, "sense": -1,
     "Lscale": 1.3, "n": 20, "T": 3e4, "seed": 104},
    {"name": "schw_sep_E097", "kind": "kerrlike", "system": "SCHW", "E": 0.97, "sense": 1, "eps": -0.01, "n": 20,
     "T": 3e4, "seed": 105},
    {"name": "hh_low", "kind": "hh", "E": 1 / 12, "n": 40, "T": 3e4, "seed": 21},
    {"name": "hh_high", "kind": "hh", "E": 0.1657, "n": 40, "T": 3e4, "seed": 22},
    {"name": "zv2_v11", "kind": "zv", "E": 0.95, "T": 3e4, "seed": 107,
     "orbits": [(7.62, 1.5), (7.8, 1.5), (8.0, 1.5), (8.2, 1.5), (8.5, 1.5), (8.8, 1.5), (9.1, 1.5), (9.5, 1.5),
                (7.57274, 1.5), (7.56263, 1.45)]},
    {"name": "kerr_sep_p45_E097_pro_long", "kind": "kerrlike", "system": "Kerr", "tag": "t1o3", "E": 0.97,
     "sense": -1, "eps": -0.01, "n": 20, "T": 1.5e5, "seed": 109},
]


def measure(workers, only=None):
    from multiprocessing import get_context
    OUTD.mkdir(parents=True, exist_ok=True)
    jobs = [j for j in JOBS if not only or j["name"] in only]
    jobs.sort(key=lambda j: -j["T"])                     # longest first
    with get_context("spawn").Pool(min(workers, len(jobs))) as pool:
        for nm in pool.imap_unordered(job_run, jobs):
            print("done", nm, flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--measure", action="store_true")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--only", nargs="*")
    a = ap.parse_args()
    if a.validate:
        validate()
    if a.measure:
        measure(a.workers, a.only)
