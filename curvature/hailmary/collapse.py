"""Hail Mary Phase 2 — ground-truth solver: spherical massless-scalar gravitational collapse (Choptuik).

Polar-areal (Schwarzschild-like) coordinates, G=c=1:  ds^2 = -alpha^2 dt^2 + a^2 dr^2 + r^2 dOmega^2.
First-order scalar variables:  Phi = phi' ,  Pi = (a/alpha) phi_dot.
The geometry is SLAVED to the field by the constraints (ODEs in r), re-solved every (sub)step:
    a'/a       = (1 - a^2)/(2r) + 2*pi*r*(Phi^2 + Pi^2)         (Hamiltonian constraint, a(0)=1)
    alpha'/alpha = (a^2 - 1)/(2r) + 2*pi*r*(Phi^2 + Pi^2)        (polar slicing; normalize alpha*a -> 1 at outer edge)
Field evolution (the geometry IS the constraint -- the perfect "enforce by construction" testbed):
    Phi_dot = d/dr( alpha*Pi/a )
    Pi_dot  = (1/r^2) d/dr( r^2 * alpha*Phi/a )
Apparent horizon (black hole) <=> 2m/r = 1 - 1/a^2 -> 1.

Correctness FIRST (north star): this file is the ground truth, and it is only trustworthy if it reproduces the
qualitative dichotomy -- SUBcritical data disperses (2m/r stays small), SUPERcritical data forms an apparent
horizon (2m/r -> 1). No learning here; that comes after this verifies.

Numerics: cell-centered grid (no point at r=0), parity ghost cells at the origin (phi even -> Phi odd, Pi even),
RK4 in time, centered differences in r, metric re-solved (RK4 in r) at each substep, outgoing outer boundary.
"""

import numpy as np

PI = np.pi
np.seterr(all="ignore")


class ScalarCollapse:
    def __init__(self, n=1200, R=20.0, cfl=0.2):
        self.n, self.R = n, R
        self.dr = R / n
        self.r = (np.arange(n) + 0.5) * self.dr           # cell-centered -> no singular point at r=0
        self.dt = cfl * self.dr

    # ---------- constraints: solve the geometry from the field (RK4 in r, outward) ----------
    def solve_metric(self, Phi, Pi):
        r, dr, n = self.r, self.dr, self.n
        S = Phi ** 2 + Pi ** 2
        # linear interpolation of S(r) for RK4 substeps between cell centers
        def Sat(x):
            return np.interp(x, r, S)
        a = np.empty(n)
        lna = 0.0                                          # ln a, with a->1 (lna->0) as r->0
        # integrate from r=0 to first cell center (a-1 ~ O(r^2), so lna(r0) ~ small)
        # then cell-to-cell with RK4 on d(lna)/dr = (1-a^2)/(2r) + 2*pi*r*S
        def dlna(x, lna_):
            av = np.exp(lna_)
            return (1 - av ** 2) / (2 * x) + 2 * PI * x * Sat(x)
        # seed: integrate 0 -> r[0] with a midpoint (S~S[0], a~1)
        x0 = 1e-6
        lna = 0.0
        # RK4 from x0 to r[0]
        h = r[0] - x0
        k1 = dlna(x0, lna); k2 = dlna(x0 + h / 2, lna + h / 2 * k1)
        k3 = dlna(x0 + h / 2, lna + h / 2 * k2); k4 = dlna(x0 + h, lna + h * k3)
        lna = lna + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        a[0] = np.exp(lna)
        for i in range(n - 1):
            x = r[i]; h = dr
            k1 = dlna(x, lna); k2 = dlna(x + h / 2, lna + h / 2 * k1)
            k3 = dlna(x + h / 2, lna + h / 2 * k2); k4 = dlna(x + h, lna + h * k3)
            lna = lna + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
            a[i + 1] = np.exp(lna)
        # alpha: d(ln alpha)/dr = (a^2-1)/(2r) + 2*pi*r*S, integrated on the grid (trapezoid is fine here)
        integ = (a ** 2 - 1) / (2 * r) + 2 * PI * r * S
        lnalpha = np.concatenate([[0.0], np.cumsum(0.5 * (integ[1:] + integ[:-1]) * dr)])
        alpha = np.exp(lnalpha)
        alpha *= (1.0 / a[-1]) / alpha[-1]                 # asymptotic flatness: alpha*a -> 1 at outer edge
        return a, alpha

    # ---------- field evolution RHS ----------
    def rhs(self, Phi, Pi):
        r, dr = self.r, self.dr
        a, alpha = self.solve_metric(Phi, Pi)
        F = alpha * Pi / a                                  # for Phi_dot = dF/dr
        G = alpha * Phi / a                                 # for Pi_dot = (1/r^2) d(r^2 G)/dr
        # parity ghosts at origin: Phi odd, Pi even -> F even, G odd ; outgoing extrapolation at outer edge
        F_l = F[0]; F_r = 2 * F[-1] - F[-2]                 # F even -> F[-1]=F[0]
        rg_l = -(r[0] ** 2 * G[0]); rg = r ** 2 * G; rg_r = 2 * rg[-1] - rg[-2]  # r^2 G odd -> ghost = -inner
        dF = np.empty_like(F); dF[1:-1] = (F[2:] - F[:-2]) / (2 * dr)
        dF[0] = (F[1] - F_l) / (2 * dr); dF[-1] = (F_r - F[-2]) / (2 * dr)
        drg = np.empty_like(rg); drg[1:-1] = (rg[2:] - rg[:-2]) / (2 * dr)
        drg[0] = (rg[1] - rg_l) / (2 * dr); drg[-1] = (rg_r - rg[-2]) / (2 * dr)
        Phi_dot = dF
        Pi_dot = drg / r ** 2
        return Phi_dot, Pi_dot, a, alpha

    def step(self, Phi, Pi):
        dt = self.dt
        k1p, k1q, a, al = self.rhs(Phi, Pi)
        k2p, k2q, _, _ = self.rhs(Phi + 0.5 * dt * k1p, Pi + 0.5 * dt * k1q)
        k3p, k3q, _, _ = self.rhs(Phi + 0.5 * dt * k2p, Pi + 0.5 * dt * k2q)
        k4p, k4q, _, _ = self.rhs(Phi + dt * k3p, Pi + dt * k3q)
        Phi = Phi + dt / 6 * (k1p + 2 * k2p + 2 * k3p + k4p)
        Pi = Pi + dt / 6 * (k1q + 2 * k2q + 2 * k3q + k4q)
        return Phi, Pi

    def initial_data(self, A, r0=5.0, sig=1.0):
        """time-symmetric (Pi=0) gaussian pulse in phi; Phi = phi'. Amplitude A tunes sub/supercritical."""
        r = self.r
        phi = A * np.exp(-((r - r0) / sig) ** 2)
        Phi = A * (-2 * (r - r0) / sig ** 2) * np.exp(-((r - r0) / sig) ** 2)
        Pi = np.zeros_like(r)
        return Phi, Pi

    def max_2m_over_r(self, Phi, Pi):
        a, _ = self.solve_metric(Phi, Pi)
        return float(np.max(1 - 1 / a ** 2))

    def evolve(self, A, t_end=25.0, r0=5.0, sig=1.0, bh_thresh=0.9):
        # NOTE: polar slicing is horizon-AVOIDING -- as a horizon forms, 2m/r -> 1 from below and the central
        # lapse alpha(0) COLLAPSES toward 0 (the evolution freezes). So black-hole formation = 2m/r -> ~1 AND
        # the lapse collapsing, not 2m/r literally reaching 1. (This is correct Choptuik physics, not a bug.)
        Phi, Pi = self.initial_data(A, r0, sig)
        nsteps = int(t_end / self.dt); peak = self.max_2m_over_r(Phi, Pi); t_bh = None; min_lapse = 1.0
        for s in range(nsteps):
            Phi, Pi = self.step(Phi, Pi)
            if not np.isfinite(Phi).all():
                break
            if s % 20 == 0:
                a, alpha = self.solve_metric(Phi, Pi)
                m = float(np.max(1 - 1 / a ** 2)); peak = max(peak, m); min_lapse = min(min_lapse, float(alpha[0]))
                if m > bh_thresh and t_bh is None:
                    t_bh = (s + 1) * self.dt; break
        return {"peak_2m_over_r": peak, "t_bh": t_bh, "min_central_lapse": min_lapse,
                "collapsed": peak > bh_thresh}


def _verify():
    """correctness gate: subcritical disperses; supercritical approaches a horizon (2m/r->~1) with lapse collapse."""
    sim = ScalarCollapse(n=800, R=20.0, cfl=0.2)
    print("verifying ground-truth collapse (subcritical disperses; supercritical -> horizon + lapse collapse)...")
    out = {}
    for label, A in [("subcritical A=0.02", 0.02), ("supercritical A=0.40", 0.40)]:
        r = sim.evolve(A, t_end=20.0)
        out[label] = r
        tag = "COLLAPSE (horizon)" if r["collapsed"] else "dispersed"
        print(f"  {label}: peak 2m/r = {r['peak_2m_over_r']:.3f}, min central lapse = {r['min_central_lapse']:.3f}  -> {tag}")
    sub, sup = out["subcritical A=0.02"], out["supercritical A=0.40"]
    ok = ((not sub["collapsed"]) and sub["peak_2m_over_r"] < 0.5 and sub["min_central_lapse"] > 0.7
          and sup["collapsed"] and sup["peak_2m_over_r"] > 0.9 and sup["min_central_lapse"] < 0.3)
    print(f"\nGROUND-TRUTH COLLAPSE VERIFIED (disperse vs horizon+lapse-collapse): {ok}")
    return ok


if __name__ == "__main__":
    _verify()
