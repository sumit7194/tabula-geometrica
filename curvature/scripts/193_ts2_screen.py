"""Step 193 — numerical screen of Tomimatsu-Sato delta=2 for additional polynomial integrals (fleet chain 2, N rung).

Pre-registration frozen at notes/ts2_screen_prereg.md (commit e7c038d) BEFORE this file was written.

THE OBJECT is ansatz's sealed package (conjecture_machine/data/sealed/TS2_for_quantum/): exact rational metric
components at (p, q) = (3/5, 4/5) and (4/5, 3/5). Only TS2_METRIC.md and the two component files are read.

THE DESIGN is the FIXED SHELL. (E, L, mu=1) are pinned per ensemble, so the reduced flow in (x, y, p_x, p_y) is a
natural reversible Hamiltonian and every manifest constant whitens out of the eigenproblem: any conserved direction
is genuinely new at that shell. §168/§174 varied E, L, H and were REFUSED at rank 3-4; this is the design §161 ran
to degree 6.

MODES
  --probe   L0 loader gate + shell selection + orbit feasibility + footprint. Computes NO conservation statistic
            on TS (the Kerr integrator floor is computed, because Kerr is the control and its answer is known).
"""

import argparse
import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
import sympy as sp
from sympy.parsing.sympy_parser import parse_expr

from curvlib import RESULTS

PKG = Path("/Users/sumit/Github/conjecture_machine/data/sealed/TS2_for_quantum")
POINTS = {"t1o2": (sp.Rational(3, 5), sp.Rational(4, 5)), "t1o3": (sp.Rational(4, 5), sp.Rational(3, 5))}
X, Y, SIG = sp.symbols("x y sigma", real=True)
R_GUARD = 3.0                     # drop any orbit reaching r_like = 1 + sigma x < 3m (pre-registered rule)
Y_GUARD = 0.98                    # drop any orbit reaching the chart's axis boundary
H_DRIFT_KEEP = 1e-10              # relative H drift above this -> orbit dropped as an integration artifact

# The component files are sympy srepr. They are parsed only after checking that every token is one srepr of a
# rational function can contain -- a sibling repo's file is data, and must not be able to run code here.
_SREPR_OK = re.compile(r"^(?:Mul|Add|Pow|Integer|Rational|Symbol|'x'|'y'|'sigma'|real=True|[-\d\s(),])+$")


# ---------------------------------------------------------------- the three spacetimes, one code path

def load_ts(tag):
    """Exact components from ansatz's package, sigma set to p/2 (units m = 1; manifest: m = 2 sigma / p)."""
    local = {"Mul": sp.Mul, "Add": sp.Add, "Pow": sp.Pow, "Integer": sp.Integer, "Rational": sp.Rational,
             "Symbol": sp.Symbol, "Float": sp.Float}
    comps = {}
    for line in (PKG / f"ts2_metric_components_{tag}.txt").read_text().splitlines():
        if "=" not in line or line.startswith("#"):
            continue
        k, v = line.split("=", 1)
        v = v.strip()
        if not _SREPR_OK.match(v):
            raise ValueError(f"{tag}:{k.strip()} contains tokens outside a rational-function srepr; refusing to parse")
        comps[k.strip()] = parse_expr(v, local_dict=local, global_dict={"__builtins__": {}}, evaluate=True)
    p, q = POINTS[tag]
    sig = p / 2
    return {k: v.subs(SIG, sig) for k, v in comps.items()}, p, q, sig


def kerr_components(a, sig):
    """Kerr (m = 1) from Boyer-Lindquist via r = 1 + sigma x, cos(theta) = y, sigma = sqrt(1 - a^2).
    Built here, NOT from ansatz's pipeline: the control must be independent of the object's supplier."""
    r = 1 + sig * X
    Sg = r ** 2 + a ** 2 * Y ** 2
    return {"g_TT": -(1 - 2 * r / Sg), "g_Tphi": -2 * a * r * (1 - Y ** 2) / Sg,
            "g_phiphi": (r ** 2 + a ** 2 + 2 * a ** 2 * r * (1 - Y ** 2) / Sg) * (1 - Y ** 2),
            "g_xx": Sg / (X ** 2 - 1), "g_yy": Sg / (1 - Y ** 2)}


def zv2_components():
    """Zipoy-Voorhees delta = 2 (m = 1, sigma = 1/2): the q = 0 member of the TS delta = 2 family."""
    sig = sp.Rational(1, 2)
    f = ((X - 1) / (X + 1)) ** 2
    e2g = ((X ** 2 - 1) / (X ** 2 - Y ** 2)) ** 4
    return {"g_TT": -f, "g_Tphi": sp.Integer(0), "g_phiphi": sig ** 2 * (X ** 2 - 1) * (1 - Y ** 2) / f,
            "g_xx": e2g * sig ** 2 * (X ** 2 - Y ** 2) / (f * (X ** 2 - 1)),
            "g_yy": e2g * sig ** 2 * (X ** 2 - Y ** 2) / (f * (1 - Y ** 2))}, sig


class Spacetime:
    """Compiled once per metric. V is quadratic in (E, L), so its three coefficient functions and their gradients
    are lambdified here and every shell reuses them -- recompiling per shell made the shell scan take minutes."""

    def __init__(self, comps, sig, label):
        self.label, self.sig = label, float(sig)
        D2 = -sig ** 2 * (X ** 2 - 1) * (1 - Y ** 2)
        terms = [comps["g_phiphi"] / (2 * D2), 2 * comps["g_Tphi"] / (2 * D2), comps["g_TT"] / (2 * D2)]
        gxx, gyy = 1 / comps["g_xx"], 1 / comps["g_yy"]
        exprs = []
        for t in terms + [gxx, gyy]:
            exprs += [t, sp.diff(t, X), sp.diff(t, Y)]
        self._f = sp.lambdify((X, Y), exprs, modules="numpy", cse=True)

    def at(self, E, L):
        return Reduced(self, E, L)


class Reduced:
    """Fixed-shell reduced Hamiltonian H = 1/2 (g^xx px^2 + g^yy py^2) + V(x, y; E, L), p_T = -E, p_phi = L.
    The (T, phi) block is inverted with the Weyl-Papapetrou identity D2 = -sigma^2 (x^2-1)(1-y^2); L0 checks that
    identity on the TS components, and it holds exactly for Kerr (Delta sin^2) and ZV by construction."""

    def __init__(self, st, E, L):
        self.st, self.label, self.sig, self.E, self.L = st, st.label, st.sig, float(E), float(L)
        self.w = (self.E ** 2, self.E * self.L, self.L ** 2)

    def parts(self, x, y):
        o = [np.broadcast_to(v, np.shape(x)).astype(float) for v in self.st._f(x, y)]
        a, b, c = self.w
        V, Vx, Vy = (a * o[i] + b * o[i + 3] + c * o[i + 6] for i in range(3))
        return [V, Vx, Vy, o[9], o[10], o[11], o[12], o[13], o[14]]

    def H(self, z):
        x, y, px, py = z
        V, _, _, gxx, _, _, gyy, _, _ = self.parts(x, y)
        return 0.5 * (gxx * px ** 2 + gyy * py ** 2) + V

    def rhs(self, z):
        x, y, px, py = z
        V, Vx, Vy, gxx, gxxx, gxxy, gyy, gyyx, gyyy = self.parts(x, y)
        return np.stack([gxx * px, gyy * py,
                         -(0.5 * (gxxx * px ** 2 + gyyx * py ** 2) + Vx),
                         -(0.5 * (gxxy * px ** 2 + gyyy * py ** 2) + Vy)])

    def py2_on_shell(self, x, y, px):
        V, _, _, gxx, _, _, gyy, _, _ = self.parts(x, y)
        return (-1.0 - 2 * V - gxx * px ** 2) / gyy          # from H = -1/2


def rk4(model, z, nstep, dt, stride):
    rec = []
    for i in range(nstep):
        k1 = model.rhs(z)
        k2 = model.rhs(z + 0.5 * dt * k1)
        k3 = model.rhs(z + 0.5 * dt * k2)
        k4 = model.rhs(z + dt * k3)
        z = z + (dt / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)
        if i % stride == 0:
            rec.append(z.copy())
    return np.stack(rec, 1)                                   # (4, P, G)


def launch(model, n, rng, x_lo, x_hi):
    """Sample (x, y, px) in a box, solve py from the shell; keep only points inside the allowed region."""
    xs, ys, pxs, pys = [], [], [], []
    for _ in range(200):
        if len(xs) >= n:
            break
        x = rng.uniform(x_lo, x_hi, 4 * n)
        y = rng.uniform(-0.6, 0.6, 4 * n)
        px = rng.normal(0, 1, 4 * n) * 0.05
        py2 = model.py2_on_shell(x, y, px)
        ok = py2 > 0
        xs += list(x[ok]); ys += list(y[ok]); pxs += list(px[ok])
        pys += list(np.sqrt(py2[ok]) * rng.choice([-1, 1], ok.sum()))
    return np.array([xs[:n], ys[:n], pxs[:n], pys[:n]])


def keep_mask(model, traj):
    x, y = traj[0], traj[1]
    drift = np.max(np.abs(model.H(traj) + 0.5), axis=0) / 0.5
    band = (1 + model.sig * x.min(0) >= R_GUARD) & (np.abs(y).max(0) <= Y_GUARD) & np.isfinite(traj).all((0, 1))
    return band & (drift < H_DRIFT_KEEP), drift


def carter_shell(traj, a, E, L):
    """Kerr's Carter constant on the shell (mu = 1), prolate chart: p_theta^2 = (1 - y^2) p_y^2, cos(theta) = y."""
    y, py = traj[1], traj[3]
    return (1 - y ** 2) * py ** 2 + y ** 2 * (a ** 2 * (1 - E ** 2) + L ** 2 / (1 - y ** 2))


# ---------------------------------------------------------------- L0: the loader gate

def l0_loader(tag, rng):
    comps, p, q, sig = load_ts(tag)
    N = sp.expand(p ** 2 * X ** 4 + q ** 2 * Y ** 4 - 1 - 2 * sp.I * p * q * X * Y * (X ** 2 - Y ** 2))
    D = sp.expand(2 * p * X * (X ** 2 - 1) - 2 * sp.I * q * Y * (1 - Y ** 2))
    Nr, Ni, Dr, Di = sp.re(N), sp.im(N), sp.re(D), sp.im(D)
    A = Nr ** 2 + Ni ** 2 - Dr ** 2 - Di ** 2
    B = (Nr + Dr) ** 2 + (Ni + Di) ** 2
    chi = 2 * (Ni * Dr - Nr * Di) / B                               # Im(N conj(D)) = Ni Dr - Nr Di
    f = A / B
    w = comps["omega"]
    checks = {
        "g_TT=-A/B": (comps["g_TT"] + A / B, comps["g_TT"]),
        "g_xx(f,gamma)": (comps["g_xx"] - B * sig ** 2 / (p ** 4 * (X ** 2 - Y ** 2) ** 3 * (X ** 2 - 1)), comps["g_xx"]),
        "g_yy(f,gamma)": (comps["g_yy"] - B * sig ** 2 / (p ** 4 * (X ** 2 - Y ** 2) ** 3 * (1 - Y ** 2)), comps["g_yy"]),
        "Weyl": (comps["g_TT"] * comps["g_phiphi"] - comps["g_Tphi"] ** 2 + sig ** 2 * (X ** 2 - 1) * (1 - Y ** 2),
                 sig ** 2 * (X ** 2 - 1) * (1 - Y ** 2)),
        "g_Tphi=f*omega": (comps["g_Tphi"] - f * w, comps["g_Tphi"]),
        "twist_x": (sp.diff(w, X) - sig * (1 - Y ** 2) / f ** 2 * sp.diff(chi, Y), sp.diff(w, X)),
        "twist_y": (sp.diff(w, Y) + sig * (X ** 2 - 1) / f ** 2 * sp.diff(chi, X), sp.diff(w, Y)),
    }
    pts = [(sp.Rational(int(rng.integers(1300, 9000)), 1000), sp.Rational(int(rng.integers(-900, 900)), 1000))
           for _ in range(20)]
    out = {}
    for k, (e, s) in checks.items():
        worst = 0.0
        for xv, yv in pts:
            sub = {X: xv, Y: yv}
            worst = max(worst, float(abs(sp.N(e.subs(sub), 30)) / (abs(sp.N(s.subs(sub), 30)) + sp.Float("1e-300"))))
        out[k] = worst
    # far field, BL sign convention: 1 + g_TT ~ 2m/r and g_Tphi ~ -2 J (1-y^2)/r, with r ~ 1 + sigma x
    xv, yv = sp.Integer(10) ** 7, sp.Rational(1, 3)
    r = 1 + sig * xv
    m_read = float(sp.N((1 + comps["g_TT"].subs({X: xv, Y: yv})) * r / 2, 30))
    J_read = float(sp.N(-comps["g_Tphi"].subs({X: xv, Y: yv}) * r / (2 * (1 - yv ** 2)), 30))
    out["m_far"] = m_read
    out["J_over_m2_far"] = J_read / m_read ** 2
    passed = all(out[k] <= (1e-6 if k.startswith("twist") else 1e-10) for k in checks) \
        and abs(m_read - 1) <= 1e-3 and abs(abs(J_read) - float(q)) <= 1e-3
    return out, bool(passed), comps, p, q, sig, float(np.sign(J_read))


# ---------------------------------------------------------------- shell selection (bound-orbit existence only)

def equatorial_intervals(model, x_grid):
    """Allowed region along y = 0 at px = 0 (py^2 > 0), as connected intervals of x."""
    ok = model.py2_on_shell(x_grid, np.zeros_like(x_grid), np.zeros_like(x_grid)) > 0
    iv, start = [], None
    for i, o in enumerate(ok):
        if o and start is None:
            start = i
        if start is not None and (not o or i == len(ok) - 1):
            iv.append((float(x_grid[start]), float(x_grid[i if o else i - 1])))
            start = None
    return iv


def probe(args):
    rng = np.random.default_rng(0)
    out = {"mode": "probe", "L0": {}, "shells": {}, "orbits": {}}
    t0 = time.time()
    for tag in POINTS:
        res, ok, comps, p, q, sig, Jsign = l0_loader(tag, rng)
        out["L0"][tag] = {"checks": res, "pass": ok, "J_sign_BL": Jsign}
        print(f"L0 {tag} (p,q)=({p},{q}): {'PASS' if ok else 'FAIL'}  " + "  ".join(f"{k}:{v:.1e}" for k, v in res.items()),
              flush=True)
        if not ok:
            continue
        a = Jsign * q                                       # matched spin AND matched sign
        spaces = {"TS2": Spacetime(comps, sig, "TS2"), "Kerr": Spacetime(kerr_components(a, p), p, "Kerr"),
                  "ZV2": Spacetime(*zv2_components(), "ZV2")}
        models = {}
        # Shell rule (deviation from the pre-reg's first grid, recorded): each spacetime must have exactly ONE bound
        # outer interval on the equator, disjoint from any inner plunge region, apocentre <= 25. ZV delta=2 plunges
        # unless |L| >~ 3.8, and the shells are SHARED (pre-registered), so pericentres land at ~7.5-9.5m rather than
        # the pre-reg's "r <~ 8m". Orbits are prograde: L carries the sign of J.
        chosen = []
        for E in np.round(np.arange(0.950, 0.9801, 0.005), 4):
            for L in np.round(np.arange(-4.2, -3.29, 0.1), 2):
                ivs, good = {}, True
                for nm, st in spaces.items():
                    mdl = st.at(E, L)
                    models[(nm, E, L)] = mdl
                    xg = np.linspace((R_GUARD - 1) / st.sig, 80 / st.sig, 8000)
                    iv = [(1 + st.sig * lo, 1 + st.sig * hi) for lo, hi in equatorial_intervals(mdl, xg)]
                    outer = [v for v in iv if v[0] > R_GUARD + 0.3 and v[1] < 60]
                    ivs[nm] = outer
                    good = good and len(outer) == 1 and outer[0][1] <= 25
                if good:
                    chosen.append({"E": float(E), "L": float(L), "r_intervals": ivs,
                                   "max_pericentre": max(v[0][0] for v in ivs.values())})
        chosen = sorted(chosen, key=lambda c: c["max_pericentre"])[:3]
        out["shells"][tag] = chosen
        print(f"  shells (shared, bound, apocentre <= 25): " + "; ".join(
            f"(E={c['E']}, L={c['L']}) peri<= {c['max_pericentre']:.2f}" for c in chosen), flush=True)
        if not chosen:
            continue
        sh = chosen[0]
        for nm, st in spaces.items():
            s = st.sig
            mdl = models[(nm, sh["E"], sh["L"])]
            lo, hi = sh["r_intervals"][nm][0]
            z0 = launch(mdl, args.n, rng, (lo - 1) / float(s), (hi - 1) / float(s))
            tt = time.time()
            traj = rk4(mdl, z0, args.nstep, args.dt, args.stride)
            dt_run = time.time() - tt
            keep, drift = keep_mask(mdl, traj)
            rec = {"n": int(z0.shape[1]), "kept": int(keep.sum()), "median_H_drift": float(np.median(drift)),
                   "seconds": dt_run, "tau_total": args.nstep * args.dt}
            if keep.any():
                rec["max_H_drift_kept"] = float(drift[keep].max())
                rec["min_r_like_kept"] = float(1 + float(s) * traj[0][:, keep].min())
                rec["max_abs_y_kept"] = float(np.abs(traj[1][:, keep]).max())
                if nm == "TS2":
                    Bf = sp.lambdify((X, Y), comps["B"], "numpy")
                    rec["min_x_kept"] = float(traj[0][:, keep].min())
                    rec["min_B_kept"] = float(Bf(traj[0][:, keep], traj[1][:, keep]).min())
                if nm == "Kerr":
                    K = carter_shell(traj[:, :, keep], float(a), sh["E"], sh["L"])
                    rec["kerr_carter_within_over_total"] = float(K.var(0).mean() / K.var())
            out["orbits"][f"{tag}/{nm}"] = rec
            print(f"  {nm:5s} (E,L)=({sh['E']},{sh['L']}): kept {rec['kept']}/{rec['n']}, H drift med "
                  f"{rec['median_H_drift']:.1e}, {dt_run:.1f}s; " +
                  ", ".join(f"{k}={v:.3g}" for k, v in rec.items() if k in (
                      "min_r_like_kept", "max_abs_y_kept", "min_x_kept", "min_B_kept", "kerr_carter_within_over_total")),
                  flush=True)
    out["wall_seconds"] = time.time() - t0
    (RESULTS / "193_ts2_probe.json").write_text(json.dumps(out, indent=1, default=float))
    print(f"saved results/193_ts2_probe.json  ({out['wall_seconds']:.0f}s)")

# ================================================================ production engine (runs only after The Bridge's go)

BAND = 1e3                        # conserved iff held-out ratio <= BAND x the Kerr floor (§168's margin)
APPROX_CEIL = 1e-6                # between the band and this: APPROXIMATE, never a detection
RANKS = {"even": (2, 4), "odd": (1, 3)}   # even r=3 == even r=2 (degree-3 has no even part), so parity carries r
DEGS = (2, 4, 6)


def coord_family(x, y, d, s, xref):
    """CR(d, s): x~^i y^j (i+j <= d, x~ = x/xref, a pure rescaling that leaves the span unchanged) times
    {1, (x^2-1)^-k, (1-y^2)^-k : k <= s}."""
    xt = x / xref
    nums = [(xt ** i * y ** j, f"x{i}y{j}") for i in range(d + 1) for j in range(d + 1 - i)]
    dens = [(1.0, "")] + [((x ** 2 - 1) ** -k, f"/(x2-1)^{k}") for k in range(1, s + 1)] \
        + [((1 - y ** 2) ** -k, f"/(1-y2)^{k}") for k in range(1, s + 1)]
    return [(nv * dv, nn + dn) for nv, nn in nums for dv, dn in dens]


def mom_monomials(px, py, r, parity):
    out = []
    for deg in range(0 if parity == "even" else 1, r + 1):
        if (deg % 2 == 0) != (parity == "even"):
            continue
        for a in range(deg + 1):
            out.append((px ** a * py ** (deg - a), f"px{a}py{deg - a}"))
    return out


def features(z, spec, model):
    """One trajectory (4, P) -> (P, p). spec = (family, parity, r, d, xref)."""
    family, parity, r, d, xref = spec
    x, y, px, py = z
    if family == "exp":                                    # Toda control: the basis that can represent I3
        s3 = np.sqrt(3.0)
        coord = [(np.ones_like(x), "1"), (np.exp(2 * y + 2 * s3 * x), "e+"), (np.exp(2 * y - 2 * s3 * x), "e-"),
                 (np.exp(-4 * y), "e0")]
        coord = [(cv * x ** i * y ** j, f"{cn}x{i}y{j}") for cv, cn in coord for i in range(3) for j in range(3 - i)]
    else:
        coord = coord_family(x, y, d, (r + 1) // 2, xref)
        if family == "CR+":
            V, _, _, gxx, _, _, gyy, _, _ = model.parts(x, y)
            xt = x / xref
            coord += [(h * xt ** i * y ** j, f"{hn}x{i}y{j}") for h, hn in ((gxx, "gxx"), (gyy, "gyy"), (V, "V"))
                      for i in range(3) for j in range(3 - i)]
    cols = []
    for mv, mn in mom_monomials(px, py, r, parity):
        for cv, cn in coord:
            if mn == "px0py0" and cn in ("x0y0", "1x0y0"):
                continue                                   # the constant carries no information
            cols.append(mv * cv)
    return np.stack(cols, -1)


def _moments(trajs, spec, model):
    """Chan-combined mean and variance of the raw features over a dataset (robust to scale)."""
    n, mean, M2 = 0, None, None
    for g in range(trajs.shape[2]):
        F = features(trajs[:, :, g], spec, model)
        nb, mb = len(F), F.mean(0)
        M2b = ((F - mb) ** 2).sum(0)
        if mean is None:
            n, mean, M2 = nb, mb, M2b
            continue
        delta = mb - mean
        tot = n + nb
        mean, M2, n = mean + delta * nb / tot, M2 + M2b + delta ** 2 * n * nb / tot, tot
    return mean, np.sqrt(M2 / n) + 1e-300


def sqrt_stats(trajs, spec, model, sd, chunk=6):
    """SQUARE-ROOT form of the §99 engine's inputs: R factors with R_w^T R_w = within scatter and R_t^T R_t = total
    scatter, accumulated by streamed QR. FIX ROUND 1 (Kerr control, before any TS statistic): forming the covariance
    matrices squares the condition number; on Kerr it left the engine's floor at ~1e-10 against Carter's true 4e-25
    and put the exactly-representable K^2 at 6000x the floor (C1 would have failed). Same generalized eigenproblem,
    no squaring. Total scatter is about the dataset's OWN mean, as §99's held-out ratio uses."""
    mean, _ = _moments(trajs, spec, model)
    Rw = Rt = None
    G = trajs.shape[2]
    for g0 in range(0, G, chunk):
        Zw, Zt = [], []
        for g in range(g0, min(G, g0 + chunk)):
            Z = (features(trajs[:, :, g], spec, model) - mean) / sd
            Zw.append(Z - Z.mean(0))
            Zt.append(Z)
        Zw, Zt = np.concatenate(Zw), np.concatenate(Zt)
        Rw = np.linalg.qr(Zw if Rw is None else np.vstack([Rw, Zw]), mode="r")
        Rt = np.linalg.qr(Zt if Rt is None else np.vstack([Rt, Zt]), mode="r")
    return Rw, Rt


COND_TOL = 1e-12                  # total-scatter singular values below this x max are the shell's exact constants
                                  # (H, and every product with H + 1/2) plus basis redundancy: pruned, and counted


def engine(tr, te, spec, model):
    _, sd = _moments(tr, spec, model)
    Rw, Rt = sqrt_stats(tr, spec, model, sd)
    Rw_te, Rt_te = sqrt_stats(te, spec, model, sd)
    _, S, Vt = np.linalg.svd(Rt)
    keep = S > COND_TOL * S[0]
    W = Vt[keep].T / S[keep]
    _, S2, V2t = np.linalg.svd(Rw @ W)
    C = W @ V2t[::-1].T                                   # ascending within/total on train
    num = np.sum((Rw_te @ C) ** 2, 0)
    den = np.sum((Rt_te @ C) ** 2, 0)
    ratios = num / np.maximum(den, 1e-300)
    order = np.argsort(ratios)
    return {"ratios": ratios[order], "C": C[:, order], "sd": sd, "p": int(len(sd)),
            "n_pruned": int((~keep).sum())}


def values_along(traj, spec, model, res, k):
    """Per-trajectory mean value of conserved direction k (for span checks against a known invariant)."""
    c = res["C"][:, k]
    return np.array([(features(traj[:, :, g], spec, model) / res["sd"] @ c).mean()
                     for g in range(traj.shape[2])])


class TodaModel:
    """Periodic 3-particle Toda, Henon's reduced 2-DOF form -- the odd-degree READOUT control (C3). Natural
    Hamiltonian, not geodesic flow: it validates the readout, not the geodesic reduction (stated in the pre-reg)."""
    label, sig = "Toda", None
    S3 = np.sqrt(3.0)

    def __init__(self, energy):
        self.E0 = energy

    def _pot(self, x, y):
        a, b, c = np.exp(2 * y + 2 * self.S3 * x), np.exp(2 * y - 2 * self.S3 * x), np.exp(-4 * y)
        return (a + b + c) / 24 - 1 / 8, a, b, c

    def H(self, z):
        x, y, px, py = z
        return 0.5 * (px ** 2 + py ** 2) + self._pot(x, y)[0]

    def rhs(self, z):
        x, y, px, py = z
        _, a, b, c = self._pot(x, y)
        return np.stack([px, py, -(2 * self.S3 * (a - b)) / 24, -(2 * a + 2 * b - 4 * c) / 24])

    def I3(self, z):
        x, y, px, py = z
        _, a, b, c = self._pot(x, y)
        return 8 * px * (px ** 2 - 3 * py ** 2) + (px + self.S3 * py) * b + (px - self.S3 * py) * a - 2 * px * c

    def launch(self, n, rng):
        pts = []
        while len(pts) < n:
            x, y = rng.uniform(-0.4, 0.4), rng.uniform(-0.4, 0.4)
            ke = self.E0 - self._pot(np.array(x), np.array(y))[0]
            if ke <= 0.01:
                continue
            th = rng.uniform(0, 2 * np.pi)
            v = np.sqrt(2 * ke)
            pts.append((x, y, v * np.cos(th), v * np.sin(th)))
        return np.array(pts).T


def ensemble(model, n, seed, nstep, dt, stride, x_lo=None, x_hi=None):
    rng = np.random.default_rng(seed)
    if isinstance(model, TodaModel):
        traj = rk4(model, model.launch(n, rng), nstep, dt, stride)
        Hs = model.H(traj)
        keep = (np.max(np.abs(Hs - Hs[:, :1]), 0) / model.E0 < H_DRIFT_KEEP) & np.isfinite(traj).all((0, 1))
        return traj[:, :, keep]
    got = []
    for _ in range(6):
        z0 = launch(model, 2 * n, rng, x_lo, x_hi)
        traj = rk4(model, z0, nstep, dt, stride)
        k, _ = keep_mask(model, traj)
        got.append(traj[:, :, k])
        if sum(g.shape[2] for g in got) >= n:
            break
    traj = np.concatenate(got, 2)[:, :, :n]
    if traj.shape[2] < n:
        raise RuntimeError(f"{model.label}: only {traj.shape[2]} kept orbits (needed {n})")
    return traj


SHELLS = ((0.97, -3.8), (0.97, -3.9), (0.965, -3.8))          # amendment 1, A2
CELLS = [("CR", par, r, d) for par in ("even", "odd") for r in RANKS[par] for d in DEGS] \
    + [("CR+", "even", 4, 6), ("CR+", "odd", 3, 6)]


def expected_kerr(fam, parity, r, d):
    if parity == "odd":
        return 0
    return 1 if r == 2 else (2 if (d >= 4 or fam == "CR+") else 1)


def span_residual(traj, spec, model, res, k, target):
    """Is a known invariant (per-trajectory values) inside the span of the first k conserved directions?"""
    if k == 0:
        return 1.0
    V = np.stack([values_along(traj, spec, model, res, j) for j in range(k)], 1)
    X_ = np.concatenate([V, np.ones((len(V), 1))], 1)
    coef, *_ = np.linalg.lstsq(X_, target, rcond=None)
    return float(np.linalg.norm(X_ @ coef - target) / (np.linalg.norm(target - target.mean()) + 1e-300))


def toda_control(args, out):
    mdl = TodaModel(0.1)
    tr = ensemble(mdl, args.n, 11, args.nstep, 0.02, args.stride)
    te = ensemble(mdl, args.n, 61, args.nstep, 0.02, args.stride)
    rows = {}
    for par, r in (("odd", 1), ("odd", 3), ("even", 2), ("even", 4)):
        res = engine(tr, te, ("exp", par, r, 0, 1.0), mdl)
        rows[f"{par}{r}"] = res
    floor = rows["odd3"]["ratios"][0]
    counts = {k: int((v["ratios"] <= BAND * floor).sum()) for k, v in rows.items()}
    I3 = np.array([mdl.I3(te[:, :, g]).mean() for g in range(te.shape[2])])
    resid = span_residual(te, ("exp", "odd", 3, 0, 1.0), mdl, rows["odd3"], 1, I3)
    ok = counts == {"odd1": 0, "odd3": 1, "even2": 0, "even4": 0} and resid < 1e-3
    out["C3_toda"] = {"floor": float(floor), "counts": counts, "I3_span_residual": resid, "pass": bool(ok),
                      "ratios": {k: [float(x) for x in v["ratios"][:6]] for k, v in rows.items()},
                      "scope": "natural Hamiltonian, not geodesic flow: validates the readout at odd degree, "
                               "not the geodesic reduction"}
    print(f"C3 Toda: counts {counts}, I3 span residual {resid:.1e}, floor {floor:.1e} -> {'PASS' if ok else 'FAIL'}",
          flush=True)
    return ok


def run_space(model, lo_hi, args, seed, cells):
    xl, xh = ((lo_hi[0] - 1) / model.sig, (lo_hi[1] - 1) / model.sig)
    tr = ensemble(model, args.n, seed, args.nstep, args.dt, args.stride, xl, xh)
    te = ensemble(model, args.n, seed + 50, args.nstep, args.dt, args.stride, xl, xh)
    xref = 0.5 * (xl + xh)
    res = {c: engine(tr, te, c + (xref,), model) for c in cells}
    return tr, te, xref, res


SHELLS_STRONG = {"t1o2": ((0.935, -2.9), (0.94, -3.0), (0.945, -3.1)),       # amendment 2: TS + Kerr only,
                 "t1o3": ((0.94, -3.05), (0.935, -3.05), (0.94, -3.15))}    # pericentre 4.0-5.5m, no ZV


def outer_interval(mdl):
    xg = np.linspace((R_GUARD - 1) / mdl.sig, 80 / mdl.sig, 8000)
    iv = [(1 + mdl.sig * a_, 1 + mdl.sig * b_) for a_, b_ in equatorial_intervals(mdl, xg)]
    return [v for v in iv if v[0] > R_GUARD + 0.3 and v[1] < 60][0]


def control_cells(nm, res, te, xref, mdl, floors, si, q, E, L):
    cells, ok_all = {}, True
    for c in CELLS:
        fam, par, r, d = c
        if nm == "Kerr":
            e = expected_kerr(fam, par, r, d)
            if e:
                floors[(si, c)] = res[c]["ratios"][e - 1]
        fl = floors[(si, c)] if par == "even" else floors[(si, (fam, "even", r + 1, d))]
        cnt = int((res[c]["ratios"] <= BAND * fl).sum())
        cell = {"p": res[c]["p"], "pruned": res[c]["n_pruned"], "floor": float(fl), "count": cnt,
                "ratios": [float(v) for v in res[c]["ratios"][:8]]}
        if nm == "Kerr":
            e = expected_kerr(fam, par, r, d)
            cell["expected"] = e
            ok = cnt == e
            if e:
                Kv = np.array([carter_shell(te[:, :, g], float(-q), E, L).mean() for g in range(te.shape[2])])
                cell["carter_span_residual"] = span_residual(te, c + (xref,), mdl, res[c], cnt, Kv)
                ok = ok and cell["carter_span_residual"] < 1e-3
                if e == 2:
                    cell["K2_span_residual"] = span_residual(te, c + (xref,), mdl, res[c], cnt, Kv ** 2)
                    ok = ok and cell["K2_span_residual"] < 1e-3
        else:
            ok = cnt == 0
        cell["pass"] = bool(ok)
        ok_all = ok_all and ok
        cells["/".join(map(str, c))] = cell
    return cells, ok_all


def ts_cells(res, floors, si):
    cells = {}
    for c in CELLS:
        fam, par, r, d = c
        fl = floors[(si, c)] if par == "even" else floors[(si, (fam, "even", r + 1, d))]
        rs = res[c]["ratios"]
        cnt = int((rs <= BAND * fl).sum())
        appr = rs[(rs > BAND * fl) & (rs <= APPROX_CEIL)]
        # The Bridge's rule, fixed before any TS statistic: a direction outside the band is "APPROXIMATE, not
        # detected", always reported with its ratio to the floor so it cannot round up to a detection.
        cells["/".join(map(str, c))] = {
            "p": res[c]["p"], "pruned": res[c]["n_pruned"], "floor": float(fl), "count": cnt,
            "approximate": int(len(appr)), "approximate_over_floor": [float(v / fl) for v in appr[:4]],
            "ratios": [float(v) for v in rs[:8]], "refused": bool(cnt > 3 * max(expected_kerr(fam, par, r, d), 1))}
    return cells


def verdicts(A, nshell):
    V = {}
    for c in CELLS:
        key = "/".join(map(str, c))
        cs = [A["shells"][str(si)]["TS2"]["cells"][key] for si in range(nshell)]
        if any(x["refused"] for x in cs):
            v = "REFUSED-LIBRARY"
        elif all(x["count"] >= 1 for x in cs):
            v = f"DETECTED at rank {c[2]} ({c[1]} part) in basis {c[0]}(d={c[3]})"
        elif any(x["count"] >= 1 for x in cs):
            v = "SHELL-RESTRICTED INTEGRAL (not a Killing tensor): shells " + \
                ",".join(str(si) for si, x in enumerate(cs) if x["count"] >= 1)
        else:
            v = f"NONE up to rank {c[2]} ({c[1]} part) in basis {c[0]}(d={c[3]})"
            if any(x["approximate"] for x in cs):
                v += " -- APPROXIMATE, not detected, on shells " + ",".join(
                    f"{si}(x{min(x['approximate_over_floor']):.1e} floor)" for si, x in enumerate(cs) if x["approximate"])
        V[key] = v
    return V


def run_arm(tag, spaces, shells, with_zv, args, A, q, prog):
    """One arm: controls first on every shell; TS is integrated and read only if every control cell passes."""
    floors, ok_all = {}, True
    names = ("Kerr", "ZV2") if with_zv else ("Kerr",)
    for si, (E, L) in enumerate(shells):
        S = A["shells"][str(si)] = {"E": E, "L": L}
        for nm in names:
            mdl = spaces[nm].at(E, L)
            outer = outer_interval(mdl)
            tr, te, xref, res = run_space(mdl, outer, args, 100 * si + (1 if nm == "Kerr" else 2), CELLS)
            prog(nm, si)
            cells, ok = control_cells(nm, res, te, xref, mdl, floors, si, q, E, L)
            S[nm] = {"interval_r": outer, "cells": cells}
            ok_all = ok_all and ok
            print(f"  {tag} {A['arm']} shell {si} {nm}: " + " ".join(
                f"{k}:{v['count']}{'' if v['pass'] else '(FAIL)'}" for k, v in cells.items()), flush=True)
    A["controls_pass"] = bool(ok_all)
    if not ok_all:
        A["verdict"] = "REFUSED: a control count failed; TS NOT integrated, NOT read"
        print(f"  {tag} {A['arm']}: {A['verdict']}", flush=True)
        return
    if args.skip_ts:                                        # driver smoke: controls only, TS never integrated
        return
    Bf = sp.lambdify((X, Y), spaces["TS2"].B, "numpy")
    for si, (E, L) in enumerate(shells):
        S = A["shells"][str(si)]
        mdl = spaces["TS2"].at(E, L)
        outer = outer_interval(mdl)
        tr, te, xref, res = run_space(mdl, outer, args, 100 * si + 3, CELLS)
        prog("TS2", si)
        S["TS2"] = {"interval_r": outer, "min_x": float(min(tr[0].min(), te[0].min())),
                    "min_B": float(min(Bf(tr[0], tr[1]).min(), Bf(te[0], te[1]).min())),
                    "max_abs_y": float(max(np.abs(tr[1]).max(), np.abs(te[1]).max())),
                    "cells": ts_cells(res, floors, si)}
        print(f"  {tag} {A['arm']} shell {si} TS2 (min x {S['TS2']['min_x']:.1f}): " + " ".join(
            f"{k}:{v['count']}" + (f"~{v['approximate']}" if v["approximate"] else "")
            for k, v in S["TS2"]["cells"].items()), flush=True)
    A["verdicts"] = verdicts(A, len(shells))
    if with_zv:
        A["descent"] = {}
        for par in ("even", "odd"):
            for r in RANKS[par]:
                for si in range(len(shells)):
                    get = lambda nm, d: A["shells"][str(si)][nm]["cells"][f"CR/{par}/{r}/{d}"]["ratios"][0]
                    ts = [get("TS2", d) for d in DEGS]
                    zv = [get("ZV2", d) for d in DEGS]
                    f_ts, f_zv = ts[0] / max(ts[-1], 1e-300), zv[0] / max(zv[-1], 1e-300)
                    A["descent"][f"{par}{r}/shell{si}"] = {
                        "ts_best_by_d": ts, "zv_best_by_d": zv, "ts_factor": f_ts, "zv_factor": f_zv,
                        "shape": "DESCENDING" if (ts[0] > ts[1] > ts[2] and f_ts >= 10 * f_zv) else "FLAT"}
    for k, v in A["verdicts"].items():
        print(f"  {tag} {A['arm']} {k}: {v}", flush=True)


def production(args):
    from curvlib import progress
    out = {"prereg": "notes/ts2_screen_prereg.md (e7c038d + amendments 9595b80, 2)", "band": BAND,
           "approx_ceiling": APPROX_CEIL, "n_per_ensemble": args.n, "nstep": args.nstep, "dt": args.dt,
           "cells": [list(c) for c in CELLS], "q": {}}
    t0 = time.time()
    if not toda_control(args, out):
        out["verdict"] = "REFUSED: the odd-degree readout control failed; TS not read"
        (RESULTS / "193_ts2_screen.json").write_text(json.dumps(out, indent=1))
        print(out["verdict"])
        return
    state = {"step": 0}
    total = len(POINTS) * 3 * (3 + 2)

    def prog(nm, si):
        state["step"] += 1
        progress("193_ts2", state["step"], total, spacetime=nm, shell=si)

    for tag in POINTS:
        comps, p, q, sig = load_ts(tag)
        spaces = {"Kerr": Spacetime(kerr_components(-q, p), p, "Kerr"), "ZV2": Spacetime(*zv2_components(), "ZV2"),
                  "TS2": Spacetime(comps, sig, "TS2")}
        spaces["TS2"].B = comps["B"]
        Q = out["q"][tag] = {"p": str(p), "q": str(q)}
        Q["shared"] = {"arm": "shared-shell (Kerr + ZV controlled)", "shells": {}}
        run_arm(tag, spaces, SHELLS, True, args, Q["shared"], q, prog)
        Q["strong"] = {"arm": "strong-field (Kerr-controlled only; NEVER merged with the shared arm)", "shells": {}}
        run_arm(tag, spaces, SHELLS_STRONG[tag], False, args, Q["strong"], q, prog)
        (RESULTS / "193_ts2_screen.json").write_text(json.dumps(out, indent=1, default=float))
    out["wall_seconds"] = time.time() - t0
    (RESULTS / "193_ts2_screen.json").write_text(json.dumps(out, indent=1, default=float))
    print(f"saved results/193_ts2_screen.json ({out['wall_seconds']:.0f}s)")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe", action="store_true")
    ap.add_argument("--production", action="store_true")
    ap.add_argument("--skip-ts", action="store_true")
    ap.add_argument("--n", type=int, default=16)
    ap.add_argument("--nstep", type=int, default=20000)
    ap.add_argument("--dt", type=float, default=0.1)
    ap.add_argument("--stride", type=int, default=20)
    args = ap.parse_args()
    if args.probe:
        probe(args)
    elif args.production:
        args.n = 60 if args.n == 16 else args.n
        production(args)
