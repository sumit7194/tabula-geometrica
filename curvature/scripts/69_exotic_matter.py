"""Step 69 — OVERNIGHT #3: EXOTIC MATTER — what source holds a wormhole throat open? (roadmap #60)

The most speculative queue item, made honest and buildable. Web-verified (Morris-Thorne): a static
spherically-symmetric wormhole has shape function b(r) with throat b(r0)=r0; the FLARE-OUT condition
b'(r0)<1 is what makes it traversable, and flare-out ENTAILS violation of the null energy condition ->
the matter sourcing it is EXOTIC (negative energy density). With zero redshift the standard MT diagnostics
(geometric units) are:
    energy density   rho   ∝  b'(r) / r^2
    radial NEC combo (rho + p_r) ∝ (r b'(r) - b(r)) / r^3
A traversable throat forces these NEGATIVE at the throat; ordinary matter keeps them positive.

The discovery question: a net learns a geometry from RULER OBSERVATIONS ONLY (local proper-distance stretch
s(r) = dl/dr = 1/sqrt(1 - b/r), what an in-place observer measures with a rod) — never told about energy.
When we then ask what matter must source its LEARNED geometry (Einstein eq, read via autodiff of b_hat),
does it find that holding the shortcut open requires NEGATIVE energy?

Two worlds (b never given; only noisy rulers s(r)):
  THROAT (traversable):  b(r) = r0^2 / r     (b(r0)=r0, b'(r0)=-1<1 flare-out OK; s=r/sqrt(r^2-r0^2))
  STAR   (normal matter): b(r) = r^3 / R^2    (uniform-density ball, b(0)=0, no throat; s=1/sqrt(1-r^2/R^2))

Pre-reg (2026-06-17):
  X1 net learns both geometries: b_hat vs b_true held-out R^2 > 0.95.
  X2 NEC sign discovered: throat's learned (r b_hat' - b_hat) < 0 near the throat (exotic / NEC-violating);
     star's > 0 (normal). A clean sign split.
  X3 NEGATIVE ENERGY: throat's learned energy density rho_hat ∝ b_hat' < 0 (exotic matter), star's > 0,
     separated by a clear margin -> a net that learned a traversable shortcut needs negative-energy matter.
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
from curvlib import RESULTS, progress
from torch import nn

STEPS = 6000
R0 = 1.0          # throat radius
RSTAR = 3.0       # star outer radius


def b_true(r, throat):
    return R0 ** 2 / r if throat else r ** 3 / RSTAR ** 2


def stretch_obs(r, throat):
    """local ruler reading s = dl/dr = 1/sqrt(1 - b/r)."""
    return 1.0 / np.sqrt(1.0 - b_true(r, throat) / r)


def sample(throat, n=4000, seed=0):
    rng = np.random.default_rng(seed)
    if throat:
        r = rng.uniform(R0 * 1.05, 3.0, n)         # stay just off the throat (s finite)
    else:
        r = rng.uniform(0.1, RSTAR * 0.95, n)
    s = stretch_obs(r, throat).astype(np.float32)
    s = s * (1 + 0.01 * rng.standard_normal(n)).astype(np.float32)   # 1% ruler noise
    return r.astype(np.float32), s


class ShapeNet(nn.Module):
    """outputs b_hat(r) constrained to 0 < b_hat < r so the metric stays Lorentzian."""
    def __init__(s):
        super().__init__(); s.net = nn.Sequential(nn.Linear(1, 96), nn.GELU(), nn.Linear(96, 96), nn.GELU(),
                                                  nn.Linear(96, 96), nn.GELU(), nn.Linear(96, 1))
    def forward(s, r):
        z = s.net(r)
        return r * torch.sigmoid(z)                 # 0 < b_hat < r


def train(throat):
    r, s = sample(throat)
    rt = torch.from_numpy(r[:, None]); st = torch.from_numpy(s[:, None])
    ntr = int(len(r) * 0.9); m = ShapeNet(); opt = torch.optim.Adam(m.parameters(), lr=1e-3)
    rng = np.random.default_rng(0)
    for step in range(STEPS):
        idx = rng.integers(0, ntr, 256)
        bh = m(rt[idx]); shat = 1.0 / torch.sqrt(torch.clamp(1.0 - bh / rt[idx], min=1e-4))
        loss = nn.functional.mse_loss(shat, st[idx])
        opt.zero_grad(); loss.backward(); opt.step()
        if step % 500 == 0: progress(f"69_{'throat' if throat else 'star'}", step, STEPS, loss=float(loss.detach()))
    m.eval()
    # held-out fit of b_hat vs b_true
    rte = rt[ntr:]
    with torch.no_grad():
        bh = m(rte).numpy().ravel()
    bt = np.array([b_true(float(x), throat) for x in rte.numpy().ravel()])
    r2 = float(1 - np.sum((bh - bt) ** 2) / np.sum((bt - bt.mean()) ** 2))
    return m, r2


def nec_and_rho(m, throat, n=60):
    """read the NEC combo (r b' - b) and energy density (∝ b') from the LEARNED b_hat via autodiff."""
    if throat:
        rr = np.linspace(R0 * 1.08, 2.5, n)
    else:
        rr = np.linspace(0.2, RSTAR * 0.9, n)
    r = torch.tensor(rr[:, None], dtype=torch.float32, requires_grad=True)
    b = m(r)
    bprime = torch.autograd.grad(b.sum(), r, create_graph=False)[0]
    necs = (r * bprime - b).detach().numpy().ravel()        # ∝ rho + p_r
    rho = bprime.detach().numpy().ravel()                   # ∝ energy density (×1/8pi r^2 >0)
    return rr, necs, rho


def main():
    out = {}
    mt, r2t = train(True); ms, r2s = train(False)
    rr_t, nec_t, rho_t = nec_and_rho(mt, True)
    rr_s, nec_s, rho_s = nec_and_rho(ms, False)

    # near-throat representative (smallest few radii = closest to throat) vs star inner region
    nt_near = float(np.mean(nec_t[:10])); rho_t_near = float(np.mean(rho_t[:10]))
    ns_near = float(np.mean(nec_s[:10])); rho_s_near = float(np.mean(rho_s[:10]))
    out = {"throat": {"b_fit_R2": r2t, "NEC_combo_near_throat": nt_near, "energy_density_near_throat": rho_t_near},
           "star": {"b_fit_R2": r2s, "NEC_combo_inner": ns_near, "energy_density_inner": rho_s_near}}

    x1 = bool(r2t > 0.95 and r2s > 0.95)
    x2 = bool(nt_near < 0 and ns_near > 0)
    x3 = bool(rho_t_near < 0 and rho_s_near > 0 and (rho_s_near - rho_t_near) > 0.1)
    res = {**out, "X1_learns_both": x1, "X2_NEC_sign_split": x2, "X3_throat_needs_negative_energy": x3,
           "exotic_matter_discovered": bool(x1 and x2 and x3)}
    print(f"throat: b-fit R^2 {r2t:.3f} | NEC(r b'-b) near throat {nt_near:+.3f} | energy density {rho_t_near:+.3f}")
    print(f"star  : b-fit R^2 {r2s:.3f} | NEC(r b'-b) inner       {ns_near:+.3f} | energy density {rho_s_near:+.3f}")
    print(f"\nX1 learns both geometries (R^2>0.95): {x1}")
    print(f"X2 NEC sign split (throat<0 exotic, star>0 normal): {x2}")
    print(f"X3 throat needs NEGATIVE energy density (star positive, clear margin): {x3}")
    print(f"\nEXOTIC MATTER DISCOVERED (holding a shortcut open requires NEC-violating negative energy): "
          f"{res['exotic_matter_discovered']}")
    (RESULTS / "69_exotic_matter.json").write_text(json.dumps(res, indent=1))

    fig, ax = plt.subplots(1, 2, figsize=(13, 5))
    ax[0].axhline(0, color="k", lw=0.8)
    ax[0].plot(rr_t, rho_t, color="crimson", label="THROAT (traversable): rho < 0 = EXOTIC")
    ax[0].plot(rr_s, rho_s, color="navy", label="STAR (normal matter): rho > 0")
    ax[0].set_xlabel("areal radius r"); ax[0].set_ylabel("learned energy density  ∝ b_hat'(r)")
    ax[0].set_title("what matter sources the LEARNED geometry?\n(net saw only rulers, never energy)")
    ax[0].legend(fontsize=8)
    ax[1].axhline(0, color="k", lw=0.8)
    ax[1].plot(rr_t, nec_t, color="crimson", label="THROAT: rho+p_r < 0 (NEC violated)")
    ax[1].plot(rr_s, nec_s, color="navy", label="STAR: rho+p_r > 0 (NEC satisfied)")
    ax[1].set_xlabel("areal radius r"); ax[1].set_ylabel("NEC combo  ∝ (r b_hat' - b_hat)")
    ax[1].set_title("the throat forces null-energy-condition violation\n= exotic matter holds the shortcut open")
    ax[1].legend(fontsize=8); fig.tight_layout(); fig.savefig(RESULTS / "69_exotic_matter.png", dpi=140)
    print("saved results/69_exotic_matter.json + .png")


if __name__ == "__main__":
    main()
