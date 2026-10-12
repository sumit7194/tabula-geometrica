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


# ---------------------------------------------------------------- non-variational truth label (bounded HH)

def zero_one_K(series, n_c=12, seed=0):
    """Gottwald-Melbourne 0-1 test, correlation method (copied from 145_regime_detector.zero_one_K, which imports
    torch/sklearn): K -> 0 regular, K -> 1 chaotic. A time-series test, NOT a tangent/Lyapunov one, so it is not a
    cousin of the indicator under test (The Bridge, measurement 2 review)."""
    rng = np.random.default_rng(seed)
    phi = np.asarray(series, float)
    N = len(phi)
    ncut = N // 10
    Ks = []
    for c in rng.uniform(np.pi / 5, 4 * np.pi / 5, n_c):
        j = np.arange(1, N + 1)
        p = np.cumsum(phi * np.cos(j * c))
        q = np.cumsum(phi * np.sin(j * c))
        M = np.array([np.mean((p[n:] - p[:-n]) ** 2 + (q[n:] - q[:-n]) ** 2) for n in range(1, ncut)])
        D = M - phi.mean() ** 2 * (1 - np.cos(np.arange(1, ncut) * c)) / (1 - np.cos(c))
        Ks.append(np.corrcoef(np.arange(1, ncut), D)[0, 1])
    return float(np.median(Ks))


def k01(x, seed=0):
    """Max over subsample rates (145's lesson: oversampled chaos reads K ~ 0; chaos shows at SOME rate)."""
    x = np.asarray(x, float)[:6000]
    return float(max(zero_one_K(x[::r], seed=seed) for r in (3, 5, 10)))


# ---------------------------------------------------------------- MEGNO / FLI / SALI integrator

CHECK = (1e2, 3e2, 1e3, 3e3, 1e4, 3e4, 1e5, 1.5e5)
NVEC = 4                                   # two independent random pairs (Breiter: initial-vector dependence)


def indicators(mdl, z0, T, dt, seed, series_dt=None):
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
    series_every = int(round(series_dt / dt)) if series_dt else 0
    ser = {"t": [], "YA": [], "YB": []}

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
        if series_every and i % series_every == 0:
            tc = (i - 1) * dt
            ser["t"].append(tc)
            ser["YA"].append(np.where(alive, S[0] / tc, np.nan).tolist())
            ser["YB"].append(np.where(alive, S[2] / tc, np.nan).tolist())
        if i in checks:
            tc = max((i - 1) * dt, dt)
            sali = np.stack([np.minimum(np.linalg.norm(W[a] + W[b], axis=0), np.linalg.norm(W[a] - W[b], axis=0))
                             for a, b in ((0, 1), (2, 3))])
            dead = ~alive
            mY, fl, sl = S / tc, fli.copy(), sali.copy()
            mY[:, dead], fl[:, dead], sl[:, dead] = np.nan, np.nan, np.nan
            rec[checks[i]] = {"megno": mY.tolist(), "fli": fl.tolist(), "sali": sl.tolist()}
    out = {"checkpoints": rec, "t_plunge": t_plunge.tolist(), "hdrift": hdrift.tolist()}
    if series_every:
        out["series"] = ser
    return out


# ---------------------------------------------------------------- measurement (plan; distributions, not verdicts)

OUTD = RESULTS / "196_measure"
DRIFT_TARGET = 1e-10                       # pilot max |dH/H| over T; 10x margin under the 1e-9 acceptance cut


def pilot_dt(mdl, z, T, use_all=False):
    """Halve from 0.05 until a 12-orbit pilot's max H drift over T is <= DRIFT_TARGET (pilot used for nothing else)."""
    dt = 0.05
    while True:
        res = m94.integrate(mdl, z[:, :12], T, dt, max(1, int(round(0.5 / dt))), twin=False)
        keep = np.ones(len(res["hdrift"]), bool) if use_all else ~np.isfinite(res["t_plunge"])
        drift = float(np.max(res["hdrift"][keep], initial=0.0))   # use_all: escaping orbits count over their life
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


class OpenHH(m94.HenonHeiles):
    """Open Henon-Heiles (E > 1/6): escape through the saddles (|q| = 1) is registered when |q| > R_ESC, by
    returning NaN there, so 194's integrator and this file's both record the escape time as the orbit's end."""
    R_ESC = 2.0

    def rhs(self, z):
        f = super().rhs(z)
        far = (np.real(z[0]) ** 2 + np.real(z[1]) ** 2) > self.R_ESC ** 2
        return np.where(far, np.nan, f)


def level_model(system, tag, E, sense, eps, Lscale=None):
    """Levels relative to the BARRIER separatrix (gated against BPT for Kerr); sets the per-level plunge cut."""
    if system == "SCHW":
        st = s193.Spacetime(s193.kerr_components(0, 1), 1, "SCHW")
    else:
        st = m94.spacetimes(tag)[0][system]
    m94.R_PLUNGE = 3.0
    ls_old = m94.l_sep(st, E, sense)                     # the old r < 3 cut-based value, for the record
    ls = l_sep_barrier(st, E, sense)
    L = sense * ls * (Lscale if Lscale else (1 + eps))
    mdl = st.at(E, L)
    rb, Vb = barrier(mdl)
    m94.R_PLUNGE = r_cut_for(mdl)                        # process-local (spawn worker); used by integrate/seeding
    return mdl, {"l_sep": ls, "L": L, "r_barrier": rb, "V_barrier": Vb, "r_cut": m94.R_PLUNGE,
                 "l_sep_old_cut3": ls_old, "l_sep_pocket_newcut": m94.l_sep(st, E, sense)}


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
    outd = Path(job.get("outdir", OUTD))
    outd.mkdir(parents=True, exist_ok=True)
    sdt = job.get("series_dt")
    if kind == "kerrlike":
        mdl, info = level_model(job["system"], job.get("tag"), job["E"], job["sense"], job.get("eps", 0.0),
                                job.get("Lscale"))
        z, r0 = seeds_offset(mdl, job["n"], 1 / 7)
        meta.update(info, r0=list(map(float, r0)))
    elif kind in ("hh", "hh_open"):
        mdl = (OpenHH if kind == "hh_open" else m94.HenonHeiles)(job["E"])
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
            r = indicators(mdl, zz, T, dt, job["seed"], series_dt=sdt)
            lab = m94.integrate(mdl, zz, T, dt, max(1, int(round(0.5 / dt))), twin=True)
            r.update({"L": L, "x0": xs.tolist(), "dt": dt, "pilot_drift": drift, "ftle": lab["ftle"].tolist()})
            out_all.append(r)
        meta["parts"] = out_all
        (outd / f"{name}.json").write_text(json.dumps(meta, default=float))
        return name
    dt, drift = pilot_dt(mdl, z, T, use_all=(kind == "hh_open"))
    r = indicators(mdl, z, T, dt, job["seed"], series_dt=sdt)
    if kind in ("hh", "hh_open") or job.get("labels"):      # truth labels: twin FTLE (over each orbit's life) + gap
        lab = m94.integrate(mdl, z, T, dt, max(1, int(round(0.5 / dt))), twin=True)
        r["ftle"] = lab["ftle"].tolist()
        r["section_gap"] = [m94b_gap(m.valid(lab, g)) for g in range(z.shape[1])]
        if kind == "hh":                                    # non-variational truth for bounded HH
            r["k01"] = [k01(m.valid(lab, g)[:, 0], seed=g) if len(m.valid(lab, g)) > 3000 else None
                        for g in range(z.shape[1])]
    meta.update(r, dt=dt, pilot_drift=drift)
    (outd / f"{name}.json").write_text(json.dumps(meta, default=float))
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


OUTD2 = RESULTS / "196_measure2"
_zv_grid = [round(x, 4) for x in np.linspace(7.45, 7.75, 31)]
JOBS2 = [                                   # measurement 2 (The Bridge's scope): transient chaos, duration-matched
    *[{"name": f"hh_open_E{E}", "kind": "hh_open", "E": E, "n": 60, "T": 3e4, "seed": 300 + k, "series_dt": 5.0}
      for k, E in enumerate((0.18, 0.21, 0.25))],
    {"name": "hh_mixed_E0.125", "kind": "hh", "E": 0.125, "n": 60, "T": 3e4, "seed": 310, "series_dt": 25.0},
    {"name": "hh_low_series", "kind": "hh", "E": 1 / 12, "n": 40, "T": 3e4, "seed": 311, "series_dt": 25.0},
    {"name": "zv2_layer_L1.5", "kind": "zv", "E": 0.95, "T": 3e4, "seed": 320, "series_dt": 25.0,
     "orbits": [(x, 1.5) for x in _zv_grid]},
    {"name": "zv2_layer_L1.45", "kind": "zv", "E": 0.95, "T": 3e4, "seed": 321, "series_dt": 25.0,
     "orbits": [(x, 1.45) for x in _zv_grid]},
    {"name": "kerr_null_p45_pro", "kind": "kerrlike", "system": "Kerr", "tag": "t1o3", "E": 0.97, "sense": -1,
     "eps": -0.01, "n": 20, "T": 3e4, "seed": 330, "series_dt": 25.0, "labels": True},
    {"name": "kerr_null_p45_retro", "kind": "kerrlike", "system": "Kerr", "tag": "t1o3", "E": 0.97, "sense": 1,
     "eps": -0.01, "n": 20, "T": 3e4, "seed": 331, "series_dt": 25.0, "labels": True},
    {"name": "kerr_null_p35_pro", "kind": "kerrlike", "system": "Kerr", "tag": "t1o2", "E": 0.95, "sense": -1,
     "eps": -0.01, "n": 20, "T": 3e4, "seed": 332, "series_dt": 25.0, "labels": True},
    {"name": "schw_ref", "kind": "kerrlike", "system": "SCHW", "E": 0.95, "sense": 1, "eps": -0.01, "n": 20,
     "T": 3e4, "seed": 333, "series_dt": 25.0, "labels": True},
]
for _j in JOBS2:
    _j["outdir"] = str(OUTD2)

OUTD3 = RESULTS / "196_calibrate"
JOBS3 = [                                   # calibration of the frozen threshold table: 5-tau series, 0-1 labels
    {"name": "cal_hh_1o12", "kind": "hh", "E": 1 / 12, "n": 60, "T": 3e4, "seed": 401, "series_dt": 5.0},
    {"name": "cal_hh_0.125", "kind": "hh", "E": 0.125, "n": 60, "T": 3e4, "seed": 402, "series_dt": 5.0},
    {"name": "cal_kerr_p45_pro", "kind": "kerrlike", "system": "Kerr", "tag": "t1o3", "E": 0.97, "sense": -1,
     "eps": -0.01, "n": 20, "T": 3e4, "seed": 403, "series_dt": 5.0},
    {"name": "cal_kerr_p45_retro", "kind": "kerrlike", "system": "Kerr", "tag": "t1o3", "E": 0.97, "sense": 1,
     "eps": -0.01, "n": 20, "T": 3e4, "seed": 404, "series_dt": 5.0},
    {"name": "cal_kerr_p35_pro", "kind": "kerrlike", "system": "Kerr", "tag": "t1o2", "E": 0.95, "sense": -1,
     "eps": -0.01, "n": 20, "T": 3e4, "seed": 405, "series_dt": 5.0},
    {"name": "cal_schw", "kind": "kerrlike", "system": "SCHW", "E": 0.95, "sense": 1, "eps": -0.01, "n": 20,
     "T": 3e4, "seed": 406, "series_dt": 5.0},
]
for _j in JOBS3:
    _j["outdir"] = str(OUTD3)


def measure(workers, only=None, jobs_list=None):
    from multiprocessing import get_context
    OUTD.mkdir(parents=True, exist_ok=True)
    jobs = [j for j in (jobs_list or JOBS) if not only or j["name"] in only]
    jobs.sort(key=lambda j: -j["T"])                     # longest first
    with get_context("spawn").Pool(min(workers, len(jobs))) as pool:
        for nm in pool.imap_unordered(job_run, jobs):
            print("done", nm, flush=True)


# ---------------------------------------------------------------- measurement 2 analysis (plan fixed before results)

BINS = ((25, 100), (100, 300), (300, 1e3), (1e3, 3e3), (3e3, 3.0001e4))


def _orbits(d):
    """Yield (t_series, Y_series, lifetime, ftle, extra) per orbit of a job file (handles ZV 'parts')."""
    for p in (d["parts"] if "parts" in d else [d]):
        t = np.array(p["series"]["t"])
        YA = np.array(p["series"]["YA"], float)
        for g in range(YA.shape[1]):
            tp = p["t_plunge"][g]
            life = float(tp) if np.isfinite(tp) else float(d["T"])
            yield t, YA[:, g], life, (p.get("ftle") or d.get("ftle") or [np.nan] * YA.shape[1])[g], \
                {"x0": (p.get("x0") or [None] * YA.shape[1])[g],
                 "gap": (d.get("section_gap") or [None] * YA.shape[1])[g]}


def _stats(t, Y, tau):
    ok = np.isfinite(Y) & (t <= tau)
    if ok.sum() < 3:
        return None
    tt, yy = t[ok], Y[ok]
    w = tt >= tau / 2
    if w.sum() < 2:
        return None
    return float(yy[-1]), float(np.polyfit(tt[w], yy[w], 1)[0])


def _auc(pos, neg):
    pos, neg = np.asarray(pos), np.asarray(neg)
    if not len(pos) or not len(neg):
        return None
    allv = np.concatenate([pos, neg])
    ranks = allv.argsort().argsort() + 1.0
    return float((ranks[:len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


def analyze2():
    D = {f.stem: json.load(open(f)) for f in sorted(OUTD2.glob("*.json"))}
    O = {k: list(_orbits(v)) for k, v in D.items()}
    schw_f = [o[3] for o in O["schw_ref"] if o[2] >= D["schw_ref"]["T"]]
    hl_f = [o[3] for o in O["hh_low_series"]]
    chaotic, null = [], []
    for k in ("hh_open_E0.18", "hh_open_E0.21", "hh_open_E0.25"):
        chaotic += [(k, o) for o in O[k] if 25 <= o[2] < D[k]["T"]]
    for k in ("zv2_layer_L1.5", "zv2_layer_L1.45"):
        chaotic += [(k, o) for o in O[k] if o[3] > 3 * max(schw_f)]
        null += [(k, o) for o in O[k] if o[2] >= D[k]["T"] and o[3] <= 1.5 * np.median(schw_f)]
    chaotic += [("hh_mixed", o) for o in O["hh_mixed_E0.125"] if o[3] > 3 * max(hl_f)]
    null += [("hh_mixed", o) for o in O["hh_mixed_E0.125"]
             if o[3] <= 1.5 * np.median(hl_f) and (o[4]["gap"] is not None and o[4]["gap"] <= 0.05)]
    for k in ("kerr_null_p45_pro", "kerr_null_p45_retro", "kerr_null_p35_pro", "schw_ref"):
        null += [(k, o) for o in O[k] if o[2] >= D[k]["T"]]
    null += [("hh_low", o) for o in O["hh_low_series"]
             if o[3] <= 1.5 * np.median(hl_f) and (o[4]["gap"] is not None and o[4]["gap"] <= 0.05)]
    rows = []
    for lo, hi in BINS:
        cs = [(k, o) for k, o in chaotic if lo <= o[2] < hi]
        c1, c2, lyap, ns1, ns2 = [], [], [], [], []
        for k, o in cs:
            st = _stats(o[0], o[1], o[2])
            if st is None:
                continue
            c1.append(st[0]); c2.append(st[1]); lyap.append(o[2] * o[3])
            for _, n in null:                               # duration-matched: the null truncated at this tau
                sn = _stats(n[0], n[1], o[2])
                if sn:
                    ns1.append(sn[0]); ns2.append(sn[1])
        rec = {"bin": [lo, hi], "n_chaotic": len(c1), "by_group": {g: sum(1 for k, o in cs if k == g) for g in
                                                                     sorted({k for k, _ in cs})}}
        if c1 and ns1:
            for nm, c, n in (("S1", c1, ns1), ("S2", c2, ns2)):
                q99 = float(np.percentile(n, 99))
                rec[nm] = {"auc": _auc(c, n), "null_p99": q99, "chaotic_median": float(np.median(c)),
                           "detect_at_1pct": float(np.mean(np.array(c) > q99))}
            rec["lyap_times_median"] = float(np.median(lyap))
        rows.append(rec)
        print(json.dumps(rec), flush=True)
    out = {"n_chaotic": len(chaotic), "n_null": len(null),
           "chaotic_groups": {g: sum(1 for k, _ in chaotic if k == g) for g in sorted({k for k, _ in chaotic})},
           "null_groups": {g: sum(1 for k, _ in null if k == g) for g in sorted({k for k, _ in null})},
           "schw_ftle_max": max(schw_f), "bins": rows}
    print({k: v for k, v in out.items() if k != "bins"})
    (RESULTS / "196_measure2_analysis.json").write_text(json.dumps(out, indent=1))


# ---------------------------------------------------------------- the MEGNO rule: table, verdicts, validation

GRID = 25.0                                # decision times are multiples of 25 tau (series every 5 tau)
TABLE_FILE = RESULTS / "196_threshold_table.json"


def _grid_value(t, Y, tdec):
    i = np.where((np.abs(t - tdec) < 1e-6) | (t <= tdec))[0]
    i = i[np.isfinite(Y[i])]
    return float(Y[i[-1]]) if len(i) else None


def _bin_of(t):
    for k, (lo, hi) in enumerate(BINS):
        if lo <= t < hi:
            return k
    return len(BINS) - 1


def null_orbits(dirpath):
    """Calibration null: integrable Kerr/Schwarzschild survivors, plus HH survivors with 0-1 K < 0.2 (tori)."""
    out, audit = [], {}
    for f in sorted(Path(dirpath).glob("*.json")):
        d = json.load(open(f))
        n_in, n_used = 0, 0
        for g, o in enumerate(_orbits(d)):
            n_in += 1
            surv = o[2] >= d["T"]
            k = (d.get("k01") or [None] * 10 ** 6)[g]
            if d["kind"] == "kerrlike" and surv or d["kind"] == "hh" and surv and k is not None and k < 0.2:
                out.append((d["name"], o)); n_used += 1
        audit[d["name"]] = {"n_in": n_in, "n_used": n_used}
    return out, audit


def build_table():
    nulls, audit = null_orbits(OUTD3)
    pools = [[] for _ in BINS]
    for _, (t, Y, life, f, ex) in nulls:
        for tk in np.arange(GRID, life + 1e-9, GRID):
            v = _grid_value(t, Y, tk)
            if v is not None:
                pools[_bin_of(tk)].append(v)
    table = {"bins": [list(b) for b in BINS], "threshold_p99": [float(np.percentile(p, 99)) for p in pools],
             "max": [float(np.max(p)) for p in pools], "n_values": [len(p) for p in pools], "audit": audit,
             "null_composition": {k: sum(1 for n, _ in nulls if n == k) for k in sorted({n for n, _ in nulls})}}
    TABLE_FILE.write_text(json.dumps(table, indent=1))
    print(json.dumps(table, indent=1))
    return table


def verdict_megno(t, Y, life, T, table):
    """CHAOTIC iff <Y>(t_dec) > table[bin(t_dec)], t_dec = the last 25-tau grid time <= life. Every orbit gets a
    verdict; nothing is dropped (silent_nulls 72)."""
    tdec = np.floor(min(life, T) / GRID) * GRID
    if tdec < GRID:
        return "ABSTAIN-TOO-SHORT", None
    v = _grid_value(t, Y, tdec)
    if v is None:
        return "ABSTAIN-NO-VALUE", None
    if v > table["threshold_p99"][_bin_of(tdec)]:
        return "CHAOTIC", v
    return ("REGULAR", v) if life >= T else ("ABSTAIN-ENDED-LOW", v)


OUTD4 = RESULTS / "196_validate"
_zv_grid5 = [round(x, 4) for x in np.linspace(7.45, 7.75, 31)]
JOBS4 = [                                   # validation on UNSEEN levels/energies (5-tau series everywhere)
    {"name": "val_kerr_p45_pro_eps-0.02", "kind": "kerrlike", "system": "Kerr", "tag": "t1o3", "E": 0.97,
     "sense": -1, "eps": -0.02, "n": 20, "T": 3e4, "seed": 501, "series_dt": 5.0},
    {"name": "val_kerr_p45_retro_eps-0.02", "kind": "kerrlike", "system": "Kerr", "tag": "t1o3", "E": 0.97,
     "sense": 1, "eps": -0.02, "n": 20, "T": 3e4, "seed": 502, "series_dt": 5.0},
    {"name": "val_kerr_p35_pro_E0.97", "kind": "kerrlike", "system": "Kerr", "tag": "t1o2", "E": 0.97,
     "sense": -1, "eps": -0.01, "n": 20, "T": 3e4, "seed": 503, "series_dt": 5.0},
    {"name": "val_kerr_p45_pro_E0.95", "kind": "kerrlike", "system": "Kerr", "tag": "t1o3", "E": 0.95,
     "sense": -1, "eps": -0.01, "n": 20, "T": 3e4, "seed": 504, "series_dt": 5.0},
    {"name": "val_schw_E0.97_eps-0.02", "kind": "kerrlike", "system": "SCHW", "E": 0.97, "sense": 1, "eps": -0.02,
     "n": 20, "T": 3e4, "seed": 505, "series_dt": 5.0},
    {"name": "val_hh_0.10", "kind": "hh", "E": 0.10, "n": 60, "T": 3e4, "seed": 506, "series_dt": 5.0},
    {"name": "val_hh_1o12", "kind": "hh", "E": 1 / 12, "n": 40, "T": 3e4, "seed": 507, "series_dt": 5.0},
    {"name": "val_hh_0.14", "kind": "hh", "E": 0.14, "n": 60, "T": 3e4, "seed": 508, "series_dt": 5.0},
    {"name": "val_hh_open_0.20", "kind": "hh_open", "E": 0.20, "n": 60, "T": 3e4, "seed": 509, "series_dt": 5.0},
    {"name": "val_zv2_L1.475", "kind": "zv", "E": 0.95, "T": 3e4, "seed": 510, "series_dt": 5.0,
     "orbits": [(x, 1.475) for x in _zv_grid5]},
]
for _j in JOBS4:
    _j["outdir"] = str(OUTD4)


def analyze_validation():
    table = json.load(open(TABLE_FILE))
    rep = {}
    for f in sorted(OUTD4.glob("*.json")):
        d = json.load(open(f))
        rows = []
        for g, (t, Y, life, ftle, ex) in enumerate(_orbits(d)):
            v, val = verdict_megno(t, Y, life, d["T"], table)
            k = (d.get("k01") or [None] * 10 ** 6)[g]
            if d["kind"] == "kerrlike":
                truth = "integrable"
            elif d["kind"] == "hh_open":
                truth = "transient-chaos" if 25 <= life < d["T"] else ("direct-escape" if life < 25 else "survivor")
            elif d["kind"] == "hh":
                truth = "torus" if (k is not None and k < 0.2) else ("chaos" if (k is not None and k > 0.8)
                                                                      else "unlabelled")
            else:
                truth = "zv-report-only"
            rows.append({"verdict": v, "Y": val, "life": life, "truth": truth, "k01": k, "ftle": ftle, **ex})
        counts = {}
        for r_ in rows:
            counts.setdefault(r_["truth"], {}).setdefault(r_["verdict"], 0)
            counts[r_["truth"]][r_["verdict"]] += 1
        rep[d["name"]] = {"n": len(rows), "counts": counts, "rows": rows}
        print(d["name"], len(rows), counts, flush=True)
    (RESULTS / "196_validate_report.json").write_text(json.dumps(rep, default=float))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--measure", action="store_true")
    ap.add_argument("--measure2", action="store_true")
    ap.add_argument("--analyze2", action="store_true")
    ap.add_argument("--calibrate", action="store_true")
    ap.add_argument("--build-table", action="store_true")
    ap.add_argument("--validate-rule", action="store_true")
    ap.add_argument("--analyze-validation", action="store_true")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--only", nargs="*")
    a = ap.parse_args()
    if a.validate:
        validate()
    if a.measure:
        measure(a.workers, a.only)
    if a.measure2:
        measure(a.workers, a.only, JOBS2)
    if a.analyze2:
        analyze2()
    if a.calibrate:
        measure(a.workers, a.only, JOBS3)
    if a.build_table:
        build_table()
    if a.validate_rule:
        if not TABLE_FILE.exists():
            raise SystemExit("threshold table not frozen: run --build-table and commit it first")
        measure(a.workers, a.only, JOBS4)
    if a.analyze_validation:
        analyze_validation()
