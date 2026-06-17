"""Step 74 — RUNG 2: MANY particles. Does the net-simulated ensemble show the ISCO truncation + plunge?

User's ladder: 1 particle (73) -> many particles -> collapse. Rung 2: release a swarm of test particles
around the black hole and roll each through the SAME learned simulator (script 73's net). The collective
fingerprint of the single-particle ISCO: orbits with L > sqrt(12) ~= 3.464 are stable (a disk with an inner
edge at the ISCO r=6M); orbits with L < sqrt(12) PLUNGE through the horizon. So the many-body system should
self-organize into a disk truncated at 6M with an empty plunging region inside — the ISCO as a collective,
emergent edge.

Pre-reg (2026-06-17):
  A1 the simulator learns (one-step R^2 > 0.999, sanity).
  A2 PLUNGE/STABLE split at the ISCO: the critical angular momentum separating plunging from stable
     net-rolled orbits is sqrt(12)=3.464 within 8%.
  A3 INNER EDGE: the smallest periapsis among the net's STABLE (non-plunging) orbits ~ 6M within 20%
     (the disk is truncated at the ISCO; nothing stable orbits closer).
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

bo = import_module("73_blackhole_orbits")
np.seterr(all="ignore")


def train_sim():
    X, Y = bo.make_segments()
    n = len(X); ntr = int(n * 0.9); idx = np.random.default_rng(0).permutation(n)
    Xt = torch.from_numpy(X[idx]); Yt = torch.from_numpy(Y[idx])
    m = bo.Sim(); opt = torch.optim.Adam(m.parameters(), lr=1e-3); rng = np.random.default_rng(1)
    for step in range(6000):
        b = rng.integers(0, ntr, 256)
        loss = nn.functional.mse_loss(m(Xt[b]), Yt[b])
        opt.zero_grad(); loss.backward(); opt.step()
        if step % 400 == 0: progress("74_sim", step, 6000, loss=float(loss.detach()))
    m.eval()
    with torch.no_grad():
        r2 = float(1 - ((m(Xt[ntr:]) - Yt[ntr:]) ** 2).sum() / ((Yt[ntr:] - Yt[ntr:].mean(0)) ** 2).sum())
    return m, r2


def roll_classify(m, r0, L, nsteps=2500):
    """roll the net; return (plunged, min_radius, R, PH)."""
    r, vr, phi = float(r0), 0.0, 0.0; R, PH = [r], [phi]; plunged = False
    for _ in range(nsteps):
        with torch.no_grad():
            out = m(torch.tensor([[r, vr, L]], dtype=torch.float32)).numpy()[0]
        rn, vr = float(out[0]), float(out[1]); phi += bo.DTAU * L / r ** 2; r = rn
        if r < 2.1:
            plunged = True; R.append(r); PH.append(phi); break
        if r > 80:
            break
        R.append(r); PH.append(phi)
    return plunged, float(np.min(R)), np.array(R), np.array(PH)


def main():
    m, r2 = train_sim()
    # release a swarm: each particle starts at r0 (apoapsis-ish) with a range of L
    rng = np.random.default_rng(3)
    parts = []
    for _ in range(400):
        L = rng.uniform(3.0, 5.2); r0 = rng.uniform(7, 24)
        plunged, rmin, R, PH = roll_classify(m, r0, L)
        parts.append({"L": L, "r0": r0, "plunged": plunged, "rmin": rmin})
    Ls = np.array([p["L"] for p in parts]); plg = np.array([p["plunged"] for p in parts])
    rmins = np.array([p["rmin"] for p in parts])

    # A2 critical L: midpoint between max-L-that-plunges and min-L-that-is-stable
    plungeL = Ls[plg]; stableL = Ls[~plg]
    Lcrit = float((plungeL.max() + stableL.min()) / 2) if plg.any() and (~plg).any() else None
    # A3 inner edge: smallest periapsis among stable orbits
    inner_edge = float(rmins[~plg].min()) if (~plg).any() else None

    a1 = bool(r2 > 0.999)
    a2 = bool(Lcrit is not None and abs(Lcrit - np.sqrt(12)) < 0.08 * np.sqrt(12))
    a3 = bool(inner_edge is not None and abs(inner_edge - 6.0) < 1.2)
    out = {"oneStep_R2": r2, "L_crit_net": Lcrit, "L_crit_GR_sqrt12": float(np.sqrt(12)),
           "inner_edge_net": inner_edge, "n_plunged": int(plg.sum()), "n_stable": int((~plg).sum()),
           "A1_simulator_ok": a1, "A2_plunge_split_at_ISCO": a2, "A3_inner_edge_6M": a3,
           "accretion_ISCO_emergent": bool(a1 and a2 and a3)}
    print(f"A1 one-step R^2 {r2:.5f}: {a1}")
    print(f"A2 critical L (plunge|stable) net {Lcrit} vs GR sqrt12={np.sqrt(12):.3f}: {a2}")
    print(f"A3 inner disk edge net {inner_edge} (want ~6M): {a3}")
    print(f"   ({int(plg.sum())} plunged, {int((~plg).sum())} stable of {len(parts)})")
    print(f"\nACCRETION ISCO EMERGENT (many-particle disk truncated at 6M, low-L plunge): {out['accretion_ISCO_emergent']}")
    (RESULTS / "74_accretion_ensemble.json").write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(1, 2, figsize=(13, 5.5))
    # left: the swarm — plot a sample of stable (green) and plunging (red) trajectories
    for p, (L, r0) in zip(parts, [(p["L"], p["r0"]) for p in parts]):
        pass
    rng2 = np.random.default_rng(7); shown = rng2.choice(len(parts), 60, replace=False)
    for i in shown:
        plunged, rmin, R, PH = roll_classify(m, parts[i]["r0"], parts[i]["L"])
        c = "crimson" if plunged else "seagreen"
        ax[0].plot(R * np.cos(PH), R * np.sin(PH), color=c, lw=0.4, alpha=0.6)
    th = np.linspace(0, 2 * np.pi, 100)
    ax[0].plot(2 * np.cos(th), 2 * np.sin(th), "k-", lw=1.2); ax[0].fill(2 * np.cos(th), 2 * np.sin(th), "k")
    ax[0].plot(6 * np.cos(th), 6 * np.sin(th), color="navy", ls="--", lw=1, label="ISCO 6M")
    ax[0].set_aspect("equal"); ax[0].set_xlim(-25, 25); ax[0].set_ylim(-25, 25); ax[0].legend(fontsize=8)
    ax[0].set_title("net-simulated swarm: stable disk (green) vs plunging (red)\nhorizon=black, ISCO=dashed")
    ax[1].scatter(Ls[~plg], rmins[~plg], s=10, color="seagreen", label="stable (periapsis)")
    ax[1].scatter(Ls[plg], rmins[plg], s=10, color="crimson", label="plunged (min r)")
    ax[1].axvline(np.sqrt(12), color="navy", ls="--", label="L=sqrt12 (ISCO)")
    ax[1].axhline(6.0, color="gray", ls=":", label="r=6M")
    ax[1].set_xlabel("angular momentum L"); ax[1].set_ylabel("min radius reached"); ax[1].legend(fontsize=8)
    ax[1].set_title(f"plunge/stable split at L~{Lcrit:.2f}; inner edge ~{inner_edge:.1f}M")
    fig.tight_layout(); fig.savefig(RESULTS / "74_accretion_ensemble.png", dpi=140)
    print("saved results/74_accretion_ensemble.json + .png")


if __name__ == "__main__":
    main()
