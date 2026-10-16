/* K20 integrator (prereg 9aca9a4 + A1-A3). Fixed-step RK4 in proper time on z = (x, y, px, py), plus coordinate time t
   and nv exact tangent vectors (w' = J w, J from the generated analytic Jacobian). Sigma = {y = 0, p_y > 0}: a crossing
   is located exactly by one Henon step (independent variable y). Per accepted point, the domain is checked under
   B9 (counted, A3), B6, P (reported) and base (g_phiphi > 0, finite, det g < 0).
   Build: cc -O2 -shared -fPIC -o libk20.dylib integ.c   (includes mn_eval.c) */
#include <math.h>
#include <string.h>
#include "mn_eval.c"

#define NOUT 26
#define MAXNV 4
#define RCOLS 14
#define T_STALL 2.0e4
#define HMAX 0.5
#define HMIN 1e-13

typedef struct {
    const unsigned char *mask;  /* dilated CTC mask on [x0, x0 + nx h) x [y0, y0 + ny h); 1 = box touches CTC */
    int nx, ny;
    double x0, y0, h;
    const double *xctc;         /* P rule: x_CTC(y) on a uniform y table (-1 = no CTC at this y) */
    int nyt;
    double yt0, yth;
    double dx_global;           /* B6: x - 1 >= dx_global */
    double xesc;                /* escape radius in x */
} Dom;

typedef struct { int b9, b6, p, base; } Ok;

static Ok dom_check(const Dom *d, const double *z, const double *o) {
    Ok r = {1, 1, 1, 1};
    double x = z[0], y = z[1];
    int fin = isfinite(x) && isfinite(y) && isfinite(o[21]) && isfinite(o[22]) && isfinite(o[24]) && isfinite(o[25]);
    double R2 = x * x + y * y - 1.0;
    int base = fin && o[21] > 0.0 && o[22] > 0.0 && o[25] > 0.0 && (1.0 - y * y) > 0.0 && (x * x - 1.0) > 0.0;
    r.base = base;
    if (!base) { r.b9 = r.b6 = r.p = 0; return r; }
    int rad = (R2 >= 0.25);
    /* B9 (counted): box-inflated g_phiphi > 0 via the dilated mask; x - 1 >= 0.05; R >= 0.5 */
    int b9 = rad && (x - 1.0 >= 0.05);
    if (b9) {
        int i = (int)floor((x - d->x0) / d->h), j = (int)floor((y - d->y0) / d->h);
        if (i >= 0 && i < d->nx && j >= 0 && j < d->ny) b9 = !d->mask[(long)i * d->ny + j];
        else if (x < d->x0 + d->nx * d->h) b9 = 0;      /* inside the table's x range but off its y range: refuse */
    }
    r.b9 = b9;
    r.b6 = rad && (x - 1.0 >= d->dx_global);
    int j = (int)floor((y - d->yt0) / d->yth + 0.5);
    double xc = (j >= 0 && j < d->nyt) ? d->xctc[j] : 1e30;
    r.p = rad && (xc < 0.0 || x - xc >= 0.025);
    return r;
}

static void deriv(const double *par, const double *s, int nv, double *ds, double *o) {
    /* s = (x, y, px, py, t, w_0[4], ..., w_{nv-1}[4]) */
    mn_eval(par, s, o);
    ds[0] = o[0]; ds[1] = o[1]; ds[2] = o[2]; ds[3] = o[3]; ds[4] = o[20];
    for (int v = 0; v < nv; v++) {
        const double *w = s + 5 + 4 * v; double *dw = ds + 5 + 4 * v;
        for (int a = 0; a < 4; a++) {
            const double *J = o + 4 + 4 * a;
            dw[a] = J[0] * w[0] + J[1] * w[1] + J[2] * w[2] + J[3] * w[3];
        }
    }
}

static void rk4(const double *par, double *s, int n, int nv, double h, double *o) {
    double k1[5 + 4 * MAXNV], k2[5 + 4 * MAXNV], k3[5 + 4 * MAXNV], k4[5 + 4 * MAXNV], tmp[5 + 4 * MAXNV];
    deriv(par, s, nv, k1, o);
    for (int i = 0; i < n; i++) tmp[i] = s[i] + 0.5 * h * k1[i];
    deriv(par, tmp, nv, k2, o);
    for (int i = 0; i < n; i++) tmp[i] = s[i] + 0.5 * h * k2[i];
    deriv(par, tmp, nv, k3, o);
    for (int i = 0; i < n; i++) tmp[i] = s[i] + h * k3[i];
    deriv(par, tmp, nv, k4, o);
    for (int i = 0; i < n; i++) s[i] += h / 6.0 * (k1[i] + 2 * k2[i] + 2 * k3[i] + k4[i]);
}

/* Dormand-Prince 5(4) (A5): one attempted step of size *h on s (n vars); error control on z = s[0..3] only.
   Returns 1 if accepted (s advanced, *h_used set), 0 if rejected; *h is updated either way. */
static int dopri(const double *par, double *s, int n, int nv, double *h, double tol, double hmax, double *h_used,
                 double *o) {
    static const double c2 = 1.0/5, c3 = 3.0/10, c4 = 4.0/5, c5 = 8.0/9;
    static const double a21 = 1.0/5;
    static const double a31 = 3.0/40, a32 = 9.0/40;
    static const double a41 = 44.0/45, a42 = -56.0/15, a43 = 32.0/9;
    static const double a51 = 19372.0/6561, a52 = -25360.0/2187, a53 = 64448.0/6561, a54 = -212.0/729;
    static const double a61 = 9017.0/3168, a62 = -355.0/33, a63 = 46732.0/5247, a64 = 49.0/176, a65 = -5103.0/18656;
    static const double b1 = 35.0/384, b3 = 500.0/1113, b4 = 125.0/192, b5 = -2187.0/6784, b6 = 11.0/84;
    static const double e1 = 71.0/57600, e3 = -71.0/16695, e4 = 71.0/1920, e5 = -17253.0/339200, e6 = 22.0/525,
                        e7 = -1.0/40;
    (void)c2; (void)c3; (void)c4; (void)c5;
    double k1[5+4*MAXNV], k2[5+4*MAXNV], k3[5+4*MAXNV], k4[5+4*MAXNV], k5[5+4*MAXNV], k6[5+4*MAXNV], k7[5+4*MAXNV];
    double t[5+4*MAXNV], y5[5+4*MAXNV];
    double hh = *h;
    deriv(par, s, nv, k1, o);
    for (int i = 0; i < n; i++) t[i] = s[i] + hh*(a21*k1[i]);
    deriv(par, t, nv, k2, o);
    for (int i = 0; i < n; i++) t[i] = s[i] + hh*(a31*k1[i] + a32*k2[i]);
    deriv(par, t, nv, k3, o);
    for (int i = 0; i < n; i++) t[i] = s[i] + hh*(a41*k1[i] + a42*k2[i] + a43*k3[i]);
    deriv(par, t, nv, k4, o);
    for (int i = 0; i < n; i++) t[i] = s[i] + hh*(a51*k1[i] + a52*k2[i] + a53*k3[i] + a54*k4[i]);
    deriv(par, t, nv, k5, o);
    for (int i = 0; i < n; i++) t[i] = s[i] + hh*(a61*k1[i] + a62*k2[i] + a63*k3[i] + a64*k4[i] + a65*k5[i]);
    deriv(par, t, nv, k6, o);
    for (int i = 0; i < n; i++) y5[i] = s[i] + hh*(b1*k1[i] + b3*k3[i] + b4*k4[i] + b5*k5[i] + b6*k6[i]);
    deriv(par, y5, nv, k7, o);
    double err = 0.0;
    int finite = 1;
    for (int i = 0; i < 4; i++) {
        double ei = hh*(e1*k1[i] + e3*k3[i] + e4*k4[i] + e5*k5[i] + e6*k6[i] + e7*k7[i]);
        double sc = tol*(1.0 + fmax(fabs(s[i]), fabs(y5[i])));
        double r = fabs(ei)/sc;
        if (!isfinite(r) || !isfinite(y5[i])) finite = 0;
        if (r > err) err = r;
    }
    if (!finite) { *h = 0.25*hh; return 0; }
    double fac = (err > 0.0) ? 0.9*pow(err, -0.2) : 5.0;
    if (fac > 5.0) fac = 5.0;
    if (fac < 0.2) fac = 0.2;
    if (err <= 1.0) {
        memcpy(s, y5, sizeof(double)*n);
        *h_used = hh;
        *h = fmin(hh*fac, hmax);
        return 1;
    }
    *h = hh*fac;
    return 0;
}

/* Henon: d(s)/dy = deriv/ydot, plus dtau/dy = 1/ydot; one RK4 step of size -y lands on y = 0. */
static void henon_deriv(const double *par, const double *s, int nv, double *ds, double *o) {
    deriv(par, s, nv, ds, o);
    double iy = 1.0 / ds[1];
    for (int i = 0; i < 5 + 4 * nv; i++) ds[i] *= iy;
    ds[5 + 4 * nv] = iy;                       /* tau */
}

static void henon(const double *par, double *s, int nv, double *o) {
    int n = 6 + 4 * nv;
    double k1[6 + 4 * MAXNV], k2[6 + 4 * MAXNV], k3[6 + 4 * MAXNV], k4[6 + 4 * MAXNV], tmp[6 + 4 * MAXNV];
    double h = -s[1];
    henon_deriv(par, s, nv, k1, o);
    for (int i = 0; i < n; i++) tmp[i] = s[i] + 0.5 * h * k1[i];
    henon_deriv(par, tmp, nv, k2, o);
    for (int i = 0; i < n; i++) tmp[i] = s[i] + 0.5 * h * k2[i];
    henon_deriv(par, tmp, nv, k3, o);
    for (int i = 0; i < n; i++) tmp[i] = s[i] + h * k3[i];
    henon_deriv(par, tmp, nv, k4, o);
    for (int i = 0; i < n; i++) s[i] += h / 6.0 * (k1[i] + 2 * k2[i] + 2 * k3[i] + k4[i]);
    s[1] = 0.0;
}

/* Trace one orbit.
   st (in/out): x, y, px, py, t, then nv tangent vectors (4 each).
   mode: 0 = FTLE (renormalise every `renorm` steps; log-growth of vector 0 accumulated);
         1 = section map (tangents projected onto the section at each crossing, never renormalised).
   rec (out): one row of RCOLS per crossing:
     0 tau, 1 t, 2 x, 3 px, 4 py, 5 cum log|w0|, 6 running max |H + 1/2| / (1/2), 7 ydot at the crossing,
     8 running min(x - 1), 9 running min g_phiphi, 10 running min R^2, 11 running min (1 - y^2),
     12 running ergoregion time (f < 0), 13 flags (bit0 B9 ok so far, bit1 B6, bit2 P, bit3 base)
   orb (out, 9 slots): 0 n_cross, 1 tau_end, 2 end code (0 n_ret reached, 1 max_steps, 2 base exit / plunge,
              3 escape, 4 non-finite, 5 stalled: no crossing for T_STALL tau), 3 tau exit B9 (-1 = never), 4 tau exit B6, 5 tau exit P,
              6 running max drift overall, 7 cum log|w0| at the end, 8 accepted steps
   dt (A5): the Dormand-Prince tolerance (rtol = atol scale), not a step size; 6 = step underflow
   Returns the number of crossings. */
int trace(const double *par, double *st, int nv, int mode, double dt, long max_steps, int n_ret, int renorm,
          const Dom *dom, double *rec, double *orb) {
    double o[NOUT];
    int n = 5 + 4 * nv, nc = 0;
    double tau = 0.0, logw = 0.0, maxdrift = 0.0;
    double mxm1 = 1e300, mgpp = 1e300, mR2 = 1e300, my2 = 1e300, ergo = 0.0;
    double ex9 = -1, ex6 = -1, exp_ = -1;
    int flags = 15, code = 1;
    double last_cross = 0.0, h = 1e-3;
    long nsteps = 0;
    mn_eval(par, st, o);
    Ok ok = dom_check(dom, st, o);
    if (!ok.base) { orb[0] = 0; orb[1] = 0; orb[2] = 2; orb[3] = orb[4] = orb[5] = 0; orb[6] = 0; orb[7] = 0; return 0; }
    for (long it = 1; it <= max_steps; it++) {
        double prev[5 + 4 * MAXNV];
        memcpy(prev, st, sizeof(double) * n);
        double hu = 0.0;
        int acc = 0;
        for (int tries = 0; tries < 60 && !acc; tries++) {
            acc = dopri(par, st, n, nv, &h, dt, HMAX, &hu, o);
            if (h < HMIN) break;
        }
        if (!acc) { code = 6; break; }                               /* step underflow: unresolvable */
        tau += hu;
        nsteps++;
        mn_eval(par, st, o);
        if (!(isfinite(st[0]) && isfinite(st[1]) && isfinite(st[2]) && isfinite(st[3]) && isfinite(o[23]))) {
            code = 4; break;
        }
        double dr = fabs(o[23] + 0.5) / 0.5;
        if (dr > maxdrift) maxdrift = dr;
        double x = st[0], y = st[1];
        if (x - 1.0 < mxm1) mxm1 = x - 1.0;
        if (o[21] < mgpp) mgpp = o[21];
        if (x * x + y * y - 1.0 < mR2) mR2 = x * x + y * y - 1.0;
        if (1.0 - y * y < my2) my2 = 1.0 - y * y;
        if (o[24] < 0.0) ergo += hu;
        ok = dom_check(dom, st, o);
        if (!ok.b9 && ex9 < 0) { ex9 = tau; flags &= ~1; }
        if (!ok.b6 && ex6 < 0) { ex6 = tau; flags &= ~2; }
        if (!ok.p && exp_ < 0) { exp_ = tau; flags &= ~4; }
        if (!ok.base) { flags &= ~8; code = 2; break; }
        if (x > dom->xesc) { code = 3; break; }
        if (tau - last_cross > T_STALL) { code = 5; break; }      /* no section crossing for T_STALL: stalled */
        if (mode == 0 && renorm > 0 && it % renorm == 0 && nv > 0) {
            for (int v = 0; v < nv; v++) {
                double *w = st + 5 + 4 * v;
                double nn = sqrt(w[0] * w[0] + w[1] * w[1] + w[2] * w[2] + w[3] * w[3]);
                if (v == 0) logw += log(nn);
                for (int a = 0; a < 4; a++) w[a] /= nn;
            }
        }
        if (prev[1] < 0.0 && st[1] >= 0.0 && st[3] > 0.0) {
            /* exact crossing: Henon step from the current point back to y = 0 */
            double s2[6 + 4 * MAXNV];
            memcpy(s2, st, sizeof(double) * n);
            s2[n] = 0.0;                         /* tau offset accumulator */
            henon(par, s2, nv, o);
            double tc = tau + s2[n];
            mn_eval(par, s2, o);
            double lw = logw;
            if (nv > 0) {
                const double *w0 = s2 + 5;
                lw += log(sqrt(w0[0] * w0[0] + w0[1] * w0[1] + w0[2] * w0[2] + w0[3] * w0[3]));
            }
            double *r = rec + (long)nc * RCOLS;
            r[0] = tc; r[1] = s2[4]; r[2] = s2[0]; r[3] = s2[2]; r[4] = s2[3]; r[5] = lw; r[6] = maxdrift;
            r[7] = o[1]; r[8] = mxm1; r[9] = mgpp; r[10] = mR2; r[11] = my2; r[12] = ergo; r[13] = flags;
            nc++;
            last_cross = tau;
            if (mode == 1) {
                /* section map: put the state exactly on the section, project the tangents onto it */
                for (int v = 0; v < nv; v++) {
                    double *w = s2 + 5 + 4 * v;
                    double c = w[1] / o[1];
                    for (int a = 0; a < 4; a++) w[a] -= c * o[a];
                }
                memcpy(st, s2, sizeof(double) * n);
                tau = tc;
            }
            if (nc >= n_ret) { code = 0; break; }
        }
    }
    orb[0] = nc; orb[1] = tau; orb[2] = code; orb[3] = ex9; orb[4] = ex6; orb[5] = exp_; orb[6] = maxdrift;
    orb[7] = logw;
    orb[8] = (double)nsteps;
    return nc;
}
