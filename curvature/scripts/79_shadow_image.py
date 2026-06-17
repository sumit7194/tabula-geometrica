"""Step 79 — THE SHADOW, PROPERLY: ray-trace the net's photon map into an EHT-style image.

Turn the learned photon dynamics (script 78) into a picture. Schwarzschild is radially symmetric, so image
brightness depends only on the impact parameter b: trace a photon backward from each image-plane radius b with
the NET's learned ray map -> captured (b < b_crit) = the dark SHADOW; escaping rays that swing near the photon
sphere (b ~ b_crit) wind and pick up emission = the bright PHOTON RING; far rays = dim background. Map the
radial brightness B(b) onto the 2D sky and add Doppler brightening on the approaching side (the EHT look).

Pre-reg (2026-06-17):
  G1 the image has a dark shadow: the dark-disk radius (capture boundary) matches the net's b_crit within 8%.
  G2 the bright photon ring sits just outside the shadow, at b within 12% of the shadow radius.
  (Deliverable: results/79_shadow_image.png -- the rendered black-hole image.)
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import torch
from importlib import import_module
from curvlib import RESULTS, progress
from torch import nn

ph = import_module("78_photon_shadow")
DPHI = ph.DPHI
np.seterr(all="ignore")


def train_photon():
    X, Y = ph.make_data()
    n = len(X); ntr = int(n * 0.9); idx = np.random.default_rng(0).permutation(n)
    Xt = torch.from_numpy(X[idx]); Yt = torch.from_numpy(Y[idx])
    m = ph.Photon(); opt = torch.optim.Adam(m.parameters(), lr=1e-3); rng = np.random.default_rng(1)
    for step in range(7000):
        b = rng.integers(0, ntr, 256)
        loss = nn.functional.mse_loss(m(Xt[b]), Yt[b])
        opt.zero_grad(); loss.backward(); opt.step()
        if step % 500 == 0: progress("79_photon", step, 7000, loss=float(loss.detach()))
    m.eval(); return m


def trace(m, b, u0=0.01, nsteps=6000):
    """net photon ray; return (captured, r_min, total_winding_phi)."""
    u = u0; w = float(np.sqrt(max(1 / b ** 2 - u0 ** 2 + 2 * u0 ** 3, 0))); umax = u; phi = 0.0
    for _ in range(nsteps):
        with torch.no_grad():
            o = m(torch.tensor([[u, w]], dtype=torch.float32)).numpy()[0]
        u, w = float(o[0]), float(o[1]); phi += DPHI; umax = max(umax, u)
        if u >= 0.5:
            return True, 1.0 / umax, phi
        if u <= 0.004 and w < 0:
            return False, 1.0 / umax, phi
    return False, 1.0 / umax, phi


def main():
    m = train_photon()
    bs = np.linspace(0.05, 11.0, 300)
    cap, rmin, wind = [], [], []
    for b in bs:
        c, rm, ph_ = trace(m, b); cap.append(c); rmin.append(rm); wind.append(ph_)
    cap = np.array(cap); rmin = np.array(rmin); wind = np.array(wind)

    # shadow radius = largest captured b; photon ring = brightness peak (winding ~ path near photon sphere)
    b_shadow = float(bs[cap].max()) if cap.any() else None
    # brightness profile: dark inside shadow; ring from winding (long dwell near photon sphere); dim falloff
    glow = np.exp(-((rmin - 3.0) / 0.7) ** 2)                  # emission peaked at the photon sphere r=3M
    bright = np.where(cap, 0.0, 0.15 + 1.0 * (wind / wind.max()) ** 2 + 0.6 * glow)
    bright = bright / bright.max()
    ring_b = float(bs[np.argmax(bright)])

    # map radial B(b) onto the 2D sky + Doppler brightening (approaching side)
    N = 600; ext = 9.0
    ax_ = np.linspace(-ext, ext, N); AX, AY = np.meshgrid(ax_, ax_)
    B = np.sqrt(AX ** 2 + AY ** 2); TH = np.arctan2(AY, AX)
    Bimg = np.interp(B, bs, bright, right=bright[-1])
    doppler = 1.0 + 0.55 * np.cos(TH - np.pi / 2)             # brighter on one side (disk rotation)
    img = Bimg * doppler

    g1 = bool(b_shadow is not None and abs(b_shadow - ph_bcrit(m)) < 0.08 * ph_bcrit(m))
    g2 = bool(ring_b >= b_shadow * 0.9 and abs(ring_b - b_shadow) < 0.12 * b_shadow)
    out = {"b_shadow_image": b_shadow, "b_crit_net": ph_bcrit(m), "b_crit_true_3sqrt3": float(3 * np.sqrt(3)),
           "photon_ring_b": ring_b, "G1_shadow_disk": g1, "G2_photon_ring": g2,
           "shadow_image_rendered": bool(g1 and g2)}
    print(f"G1 dark shadow disk radius {b_shadow:.2f} vs net b_crit {ph_bcrit(m):.2f} (true 3sqrt3={3*np.sqrt(3):.2f}): {g1}")
    print(f"G2 photon ring at b {ring_b:.2f} (just outside shadow {b_shadow:.2f}): {g2}")
    print(f"\nEHT-STYLE SHADOW IMAGE RENDERED: {out['shadow_image_rendered']}")
    (RESULTS / "79_shadow_image.json").write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(1, 2, figsize=(13, 6))
    ax[0].imshow(img, extent=[-ext, ext, -ext, ext], cmap="afmhot", origin="lower", vmin=0, vmax=1.0)
    ax[0].set_facecolor("k"); ax[0].set_title("the black hole, imaged from the net's photon map\n(dark shadow + bright photon ring, Doppler-brightened — the EHT look)")
    ax[0].set_xlabel("impact parameter alpha (M)"); ax[0].set_ylabel("beta (M)")
    th = np.linspace(0, 2 * np.pi, 200)
    ax[0].plot(b_shadow * np.cos(th), b_shadow * np.sin(th), color="cyan", lw=0.6, ls=":")
    ax[1].plot(bs, bright, color="crimson"); ax[1].axvline(b_shadow, color="k", ls="--", label=f"shadow edge {b_shadow:.2f}")
    ax[1].axvline(3 * np.sqrt(3), color="navy", ls=":", label=f"3sqrt3={3*np.sqrt(3):.2f}")
    ax[1].set_xlabel("impact parameter b (M)"); ax[1].set_ylabel("brightness"); ax[1].legend(fontsize=8)
    ax[1].set_title("radial brightness: dark shadow -> photon ring -> falloff")
    fig.tight_layout(); fig.savefig(RESULTS / "79_shadow_image.png", dpi=140)
    print("saved results/79_shadow_image.json + .png")


def ph_bcrit(m):
    """net's b_crit via the photon potential (same method as script 78)."""
    X, _ = ph.make_data()
    with torch.no_grad():
        gX = (m(torch.from_numpy(X)).numpy()[:, 1] - X[:, 1]) / DPHI
    uX = X[:, 0]; edges = np.linspace(0.22, 0.47, 26); ctr = 0.5 * (edges[:-1] + edges[1:])
    bing = np.array([np.median(gX[(uX >= edges[i]) & (uX < edges[i + 1])]) if np.any((uX >= edges[i]) & (uX < edges[i + 1])) else np.nan for i in range(len(ctr))])
    ok = np.isfinite(bing); A = np.stack([ctr[ok] ** 2, ctr[ok]], 1)
    (c2, c1), *_ = np.linalg.lstsq(A, bing[ok], rcond=None)
    ug = np.linspace(0, 0.5, 2000); g = c2 * ug ** 2 + c1 * ug
    V = np.concatenate([[0], np.cumsum(-2 * g[1:]) * (ug[1] - ug[0])])
    return float(1.0 / np.sqrt(V.max()))


if __name__ == "__main__":
    main()
