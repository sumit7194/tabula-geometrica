"""197b -- K20 domain-D geometry at p1/p2/F5-R/P0 (geometry only, no orbits): x_CTC, delta_x by quantum rule, R_s, and the D cut on the C0/F5-R inner region. Output: stdout (recorded in notes/k20_build_log.md)."""
import sys, numpy as np
sys.path.insert(0, __import__("os").path.dirname(__file__))
from importlib import import_module
s = import_module("197_k20_mn_screen")
xs = 1 + np.logspace(-6, np.log10(9.0), 2400)
ys = np.concatenate([np.linspace(-0.99999, 0.99999, 2001)])
X, Y = np.meshgrid(xs, ys, indexing="ij")
for name in ("p1", "p2", "F5R", "P0"):
    chi, al, k, be = s.point_params(name)
    g = s.gphiphi(X, Y, al, k, be)
    ctc = np.isfinite(g) & (g < 0) | ~np.isfinite(g) & (X > 1.0)    # non-finite inside counts as pathological, listed separately
    ctc_true = np.isfinite(g) & (g < 0)
    xc = xs[ctc_true.any(1)].max() if ctc_true.any() else None
    dx = None if xc is None else np.ceil(((xc - 1) + 0.025) / 0.05 - 1e-12) * 0.05
    # R_s: radius in R where any metric function is non-finite or |.| > 1e12 (over the grid)
    m = s.metric_parts(X, Y, al, k, be)
    bad = np.zeros_like(X, bool)
    for key in ("f", "w", "A", "B", "G", "e2psi"):
        v = m[key]; bad |= ~np.isfinite(v) | (np.abs(v) > 1e12)
    bad |= ~np.isfinite(g) | (np.abs(g) > 1e12)
    R = np.sqrt(np.maximum(X**2 + Y**2 - 1, 0))
    Rs = R[bad].max() if bad.any() else 0.0
    eq = ctc_true[:, np.argmin(abs(ys))]
    print(f"{name}: chi {chi:.5f} beta {be:.5f} | x_CTC {xc} -> delta_x {dx} | equatorial CTC x range {(xs[eq].min(), xs[eq].max()) if eq.any() else None} | R_s {Rs:.4f} -> R_min {max(0.5, 2*Rs):.4f}")
print("--- R_s restricted to x-1 >= delta_x (the part of the grid D keeps), and the cut on the C0 / F5-R inner region")
from scipy import ndimage
for name, dxq in (("p1", 0.10), ("p2", 0.15), ("F5R", None), ("P0", None)):
    chi, al, k, be = s.point_params(name)
    g = s.gphiphi(X, Y, al, k, be); m = s.metric_parts(X, Y, al, k, be)
    bad = ~np.isfinite(g) | (np.abs(g) > 1e12)
    for key in ("f", "w", "A", "B", "G", "e2psi"):
        v = m[key]; bad |= ~np.isfinite(v) | (np.abs(v) > 1e12)
    xc = xs[(np.isfinite(g) & (g < 0)).any(1)].max()
    dx = dxq if dxq else np.ceil(((xc - 1) + 0.025) / 0.05 - 1e-12) * 0.05
    R = np.sqrt(np.maximum(X**2 + Y**2 - 1, 0))
    keep = X - 1 >= dx
    Rs = R[bad & keep].max() if (bad & keep).any() else 0.0
    print(f"{name}: delta_x {dx:.2f} | R_s within x-1>=delta_x: {Rs:.4f}")
    if name in ("P0", "F5R"):
        K = s.kinetic(X, Y, 0.95, 3.0, al, k, be); ok = np.isfinite(K) & (K >= 0)
        lab, n = ndimage.label(ok)
        x_in = np.sqrt(1 + (1.0 / k) ** 2); c = lab[np.argmin(abs(xs - x_in)), np.argmin(abs(ys))]
        inner = lab == c
        Rmin = max(0.5, 2 * Rs)
        inD = inner & keep & (R >= Rmin) & np.isfinite(g) & (g > 0)
        # area weights in (x, y) cells are uneven; report cell fraction and equatorial rho cut
        eqj = np.argmin(abs(ys)); eq_in = inner[:, eqj]; eq_D = inD[:, eqj]
        rr = s.rho_of_x(xs, k)
        print(f"   inner region (E .95, L 3): cells {inner.sum()}, kept by D {inD.sum()} ({inD.sum()/inner.sum():.2f}) | equatorial rho {rr[eq_in].min():.3f}-{rr[eq_in].max():.3f} -> in D {rr[eq_D].min():.3f}-{rr[eq_D].max():.3f} | R_min {Rmin:.3f}")
