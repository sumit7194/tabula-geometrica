"""197c -- Kretschmann scalar of the MN metric near the equatorial B = A = 0 ring (K20 build log, The Bridge's ask).
mpmath at high precision; metric derivatives by mp.diff; generic Christoffel -> Riemann -> K = R_abcd R^abcd.
Validated first on Kerr (beta = 0) against the closed form
  K = 48 M^2 (r^2 - a^2 c^2)[(r^2 + a^2 c^2)^2 - 16 r^2 a^2 c^2] / (r^2 + a^2 c^2)^6,  r = M + k x, c = y.

    .venv314ob/bin/python scripts/197c_kretschmann.py
"""
import json
import sys
from pathlib import Path

import mpmath as mp

sys.path.insert(0, str(Path(__file__).resolve().parent))
from importlib import import_module

s = import_module("197_k20_mn_screen")
RESULTS = Path(__file__).resolve().parent.parent / "results"
mp.mp.dps = 60


def metric(pp):
    _, al, k, be = (mp.mpf(v) for v in pp)
    w0 = 4 * k * al / (1 - al ** 2)

    def comps(x, y):
        R = mp.sqrt(x ** 2 + y ** 2 - 1); mu = x * y / R
        P = [1, mu, (3 * mu ** 2 - 1) / 2, (5 * mu ** 3 - 3 * mu) / 2]; Rm = [1 / R, 1 / R ** 2, 1 / R ** 3]
        psi = be * P[2] / R ** 3
        Sa = sum((x - y) * P[l] * Rm[l] for l in range(3))
        Sb = sum(((-1) ** (3 - l)) * (x + y) * P[l] * Rm[l] for l in range(3))
        a = -al * mp.e ** (-2 * be * (-1 + Sa)); b = al * mp.e ** (2 * be * (1 + Sb))
        Sg = sum((x - y + ((-1) ** (2 - l)) * (x + y)) * P[l] * Rm[l] for l in range(3))
        G = mp.e ** (3 * be ** 2 * R ** (-6) * (P[3] ** 2 - P[2] ** 2) + 2 * be * (Sg - 2))
        A = (x ** 2 - 1) * (1 + a * b) ** 2 - (1 - y ** 2) * (b - a) ** 2
        B = (x + 1 + (x - 1) * a * b) ** 2 + ((1 + y) * a + (1 - y) * b) ** 2
        C = (x ** 2 - 1) * (1 + a * b) * (b - a - y * (a + b)) + (1 - y ** 2) * (b - a) * (1 + a * b + x * (1 - a * b))
        e2 = mp.e ** (2 * psi)
        rho2 = k ** 2 * (x ** 2 - 1) * (1 - y ** 2)
        f = e2 * A / B
        w = 2 * k * C / (e2 * A) - w0
        gtt = -f
        gtp = (2 * k * C - w0 * e2 * A) / B                # = f w, regular at A = 0
        gpp = -f * w ** 2 + rho2 / f                         # fine at 60 digits away from A = 0 exactly
        gxx = k ** 2 * G * B / (e2 * (x ** 2 - 1) * (1 - al ** 2) ** 2)
        gyy = k ** 2 * G * B / (e2 * (1 - y ** 2) * (1 - al ** 2) ** 2)
        return {"tt": gtt, "tp": gtp, "pp": gpp, "xx": gxx, "yy": gyy, "B": B, "A": A}
    return comps


IDX = {"t": 0, "x": 1, "y": 2, "p": 3}
NONZERO = (("tt", 0, 0), ("tp", 0, 3), ("pp", 3, 3), ("xx", 1, 1), ("yy", 2, 2))


def kretschmann(comps, x0, y0):
    x0, y0 = mp.mpf(x0), mp.mpf(y0)
    zero = mp.mpf(0)
    g = [[zero] * 4 for _ in range(4)]
    dg = [[[zero] * 4 for _ in range(4)] for _ in range(4)]          # dg[e][a][b] = d_e g_ab
    ddg = [[[[zero] * 4 for _ in range(4)] for _ in range(4)] for _ in range(4)]   # ddg[e][f][a][b]
    base = comps(x0, y0)
    for key, i, j in NONZERO:
        fn = lambda xx, yy, key=key: comps(xx, yy)[key]
        v = base[key]
        d1 = {1: mp.diff(fn, (x0, y0), (1, 0)), 2: mp.diff(fn, (x0, y0), (0, 1))}
        d2 = {(1, 1): mp.diff(fn, (x0, y0), (2, 0)), (2, 2): mp.diff(fn, (x0, y0), (0, 2)),
              (1, 2): mp.diff(fn, (x0, y0), (1, 1))}
        d2[(2, 1)] = d2[(1, 2)]
        for (aa, bb) in {(i, j), (j, i)}:
            g[aa][bb] = v
            for e_ in (1, 2):
                dg[e_][aa][bb] = d1[e_]
                for f_ in (1, 2):
                    ddg[e_][f_][aa][bb] = d2[(e_, f_)]
    gm = mp.matrix(g)
    gi = gm ** -1
    gi = [[gi[a, b] for b in range(4)] for a in range(4)]
    # d_e g^ab = - g^am d_e g_mn g^nb
    dgi = [[[-sum(gi[a][m] * dg[e][m][n] * gi[n][b] for m in range(4) for n in range(4)) for b in range(4)]
            for a in range(4)] for e in range(4)]
    G = [[[sum(gi[a][d] * (dg[b][d][c] + dg[c][d][b] - dg[d][b][c]) for d in range(4)) / 2 for c in range(4)]
          for b in range(4)] for a in range(4)]
    dG = [[[[(sum(dgi[e][a][d] * (dg[b][d][c] + dg[c][d][b] - dg[d][b][c]) for d in range(4))
             + sum(gi[a][d] * (ddg[e][b][d][c] + ddg[e][c][d][b] - ddg[e][d][b][c]) for d in range(4))) / 2
            for c in range(4)] for b in range(4)] for a in range(4)] for e in range(4)]
    # R^a_bcd = d_c G^a_db - d_d G^a_cb + G^a_ce G^e_db - G^a_de G^e_cb
    Rm = [[[[dG[c][a][d][b] - dG[d][a][c][b] + sum(G[a][c][e] * G[e][d][b] - G[a][d][e] * G[e][c][b] for e in range(4))
             for d in range(4)] for c in range(4)] for b in range(4)] for a in range(4)]
    Rlow = [[[[sum(g[a][m] * Rm[m][b][c][d] for m in range(4)) for d in range(4)] for c in range(4)] for b in range(4)]
            for a in range(4)]
    Rup = [[[[sum(gi[b][n] * gi[c][p] * gi[d][q] * Rm[a][n][p][q] for n in range(4) for p in range(4) for q in range(4))
              for d in range(4)] for c in range(4)] for b in range(4)] for a in range(4)]
    K = sum(Rlow[a][b][c][d] * Rup[a][b][c][d] for a in range(4) for b in range(4) for c in range(4) for d in range(4))
    return K, base


def kerr_closed(pp, x, y):
    chi, al, k, be = (mp.mpf(v) for v in pp)
    M = mp.mpf(1); a = chi; r = M + k * mp.mpf(x); c = mp.mpf(y)
    S = r ** 2 + a ** 2 * c ** 2
    return 48 * M ** 2 * (r ** 2 - a ** 2 * c ** 2) * (S ** 2 - 16 * r ** 2 * a ** 2 * c ** 2) / S ** 6


def main():
    out = {}
    pk = s.point_params("P0", kerr=True)
    ck = metric(pk)
    val = []
    for (x, y) in ((3.0, 0.2), (2.0, -0.5), (6.0, 0.7)):
        K, _ = kretschmann(ck, x, y)
        Kc = kerr_closed(pk, x, y)
        val.append({"x": x, "y": y, "K": float(K), "closed": float(Kc), "rel": float(abs(K - Kc) / abs(Kc))})
        print("Kerr check", val[-1], flush=True)
    out["kerr_validation"] = val
    for name, xs in (("P0", "1.929828258520"), ("F5R", "1.921922587920")):
        pp = s.point_params(name)
        cm = metric(pp)
        # locate the ring point precisely (minimise B on y = 0)
        Bx = lambda x: cm(x, mp.mpf(0))["B"]
        xr = mp.findroot(lambda x: mp.diff(Bx, x), mp.mpf(xs))
        rows = []
        for label, (ux, uy) in (("y=0, x>x_s", (1, 0)), ("y=0, x<x_s", (-1, 0)), ("45deg", (mp.sqrt(2) / 2, mp.sqrt(2) / 2)),
                                ("axis-ward 90deg", (0, 1))):
            for d in ("1e-1", "1e-2", "1e-3", "1e-4", "1e-5"):
                dd = mp.mpf(d)
                K, base = kretschmann(cm, xr + ux * dd, uy * dd)
                rows.append({"ray": label, "d": float(dd), "K": float(K), "B": float(base["B"]), "A": float(base["A"])})
                print(name, rows[-1], flush=True)
        out[name] = {"x_ring": float(xr), "B_at_ring": float(Bx(xr)), "rows": rows}
    # p1's near-zero of B at x ~ 1.076 (inside R < 0.5): exact or not?
    cp1 = metric(s.point_params("p1"))
    Bx1 = lambda x: cp1(x, mp.mpf(0))["B"]
    xs = [mp.mpf("1.0001") + i * mp.mpf("0.0002") for i in range(1000)]     # real bracket on y = 0, x in (1, 1.2)
    i0 = min(range(len(xs)), key=lambda i: Bx1(xs[i]))
    lo, hi = xs[max(i0 - 1, 0)], xs[min(i0 + 1, len(xs) - 1)]
    gr = (mp.sqrt(5) - 1) / 2
    for _ in range(200):                                                  # golden-section, real throughout
        c1, c2 = hi - gr * (hi - lo), lo + gr * (hi - lo)
        if Bx1(c1) < Bx1(c2):
            hi = c2
        else:
            lo = c1
    xm = (lo + hi) / 2
    out["p1_equatorial_B_min"] = {"x": float(xm), "B": float(Bx1(xm)), "A": float(cp1(xm, mp.mpf(0))["A"])}
    print("p1 B min", out["p1_equatorial_B_min"], flush=True)
    (RESULTS / "197c_kretschmann.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
