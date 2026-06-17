"""Step 77 — TWO BLACK HOLES: the inspiral and the gravitational-wave CHIRP.

Second of the trio. Two compact objects orbit, lose energy to gravitational waves, spiral in, and the orbit
speeds up -> the "chirp" LIGO hears. Web-verified (Peters, circular, G=c=1):
  radiation reaction:  dr/dtau = -(64/5) m1 m2 (m1+m2) / r^3     (the -1/r^3 inspiral)
  Kepler:              omega_orb = sqrt(M_tot/r^3),  f_GW = 2 f_orb = omega_orb/pi
  => chirp time law:   f_GW(t) ∝ (t_c - t)^(-3/8)
  => chirp freq law:   df/dt ∝ f^(11/3)
  chirp mass:          Mc = (m1 m2)^(3/5)/(m1+m2)^(1/5) sets the rate.

A net learns the radiation-reaction rate from inspiral samples (it learns log|dr/dt| vs r, masses), then we
roll out the inspiral, build the GW frequency f(t), and ask whether the two chirp exponents emerge.

Pre-reg (2026-06-17):
  I1 learns the inspiral rate: log-space R^2 > 0.999.
  I2 CHIRP TIME-LAW: rolled-out f_GW(t) ∝ (t_c - t)^p with p within 10% of -3/8 = -0.375.
  I3 CHIRP FREQ-LAW: df/dt ∝ f^q with q within 10% of 11/3 = 3.667.
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

np.seterr(all="ignore")


def drdt(r, m1, m2):
    return -(64.0 / 5.0) * m1 * m2 * (m1 + m2) / r ** 3


def make_data(n=120000, seed=0):
    rng = np.random.default_rng(seed)
    r = rng.uniform(7, 70, n); m1 = rng.uniform(0.5, 2.0, n); m2 = rng.uniform(0.5, 2.0, n)
    y = np.log10(-drdt(r, m1, m2))                       # smooth target (power law -> linear in log r)
    X = np.stack([r, m1, m2], 1).astype(np.float32); Y = y.astype(np.float32)[:, None]
    return X, Y


class Inspiral(nn.Module):
    def __init__(s):
        super().__init__(); s.net = nn.Sequential(nn.Linear(3, 128), nn.GELU(), nn.Linear(128, 128), nn.GELU(),
                                                  nn.Linear(128, 128), nn.GELU(), nn.Linear(128, 1))
    def forward(s, x): return s.net(x)
    def rate(s, r, m1, m2):                               # dr/dt = -10^(net log-rate)
        x = torch.tensor([[r, m1, m2]], dtype=torch.float32)
        with torch.no_grad():
            return -10.0 ** float(s.net(x)[0, 0])


def main():
    X, Y = make_data()
    n = len(X); ntr = int(n * 0.9); idx = np.random.default_rng(0).permutation(n)
    Xt = torch.from_numpy(X[idx]); Yt = torch.from_numpy(Y[idx])
    m = Inspiral(); opt = torch.optim.Adam(m.parameters(), lr=1e-3); rng = np.random.default_rng(1)
    for step in range(7000):
        b = rng.integers(0, ntr, 256)
        loss = nn.functional.mse_loss(m(Xt[b]), Yt[b])
        opt.zero_grad(); loss.backward(); opt.step()
        if step % 400 == 0: progress("77_inspiral", step, 7000, loss=float(loss.detach()))
    m.eval()
    with torch.no_grad():
        P = m(Xt[ntr:]); r2 = float(1 - ((P - Yt[ntr:]) ** 2).sum() / ((Yt[ntr:] - Yt[ntr:].mean(0)) ** 2).sum())

    # roll out an equal-mass inspiral (m1=m2=1, M_tot=2) with adaptive proper-time stepping
    m1 = m2 = 1.0; Mtot = m1 + m2
    r, t = 60.0, 0.0; R, TT = [r], [t]
    for _ in range(4000):
        dr = m.rate(r, m1, m2); dt = 0.02 * r / abs(dr)           # local-timescale-fraction step
        rmid = r + 0.5 * dr * dt; dr2 = m.rate(rmid, m1, m2)      # RK2
        r += dr2 * dt; t += dt
        if r < 8.0 or r > 80:
            break
        R.append(r); TT.append(t)
    R = np.array(R); TT = np.array(TT)
    f_gw = np.sqrt(Mtot / R ** 3) / np.pi                          # GW frequency = omega_orb/pi

    # I2 chirp time-law: t_c from r^4 = r0^4 - 4A t (linear), then logf vs log(t_c - t)
    A4 = np.polyfit(TT, R ** 4, 1)                                 # slope=-4A, intercept=r0^4
    t_c = -A4[1] / A4[0]
    mask = (t_c - TT) > 0.02 * (t_c - TT[0])
    p_time = float(np.polyfit(np.log(t_c - TT[mask]), np.log(f_gw[mask]), 1)[0])

    # I3 chirp freq-law: df/dt vs f, log-log slope
    dfdt = np.gradient(f_gw, TT); good = dfdt > 0
    q_freq = float(np.polyfit(np.log(f_gw[good]), np.log(dfdt[good]), 1)[0])

    i1 = bool(r2 > 0.999)
    i2 = bool(abs(p_time - (-0.375)) < 0.10 * 0.375)
    i3 = bool(abs(q_freq - (11 / 3)) < 0.10 * (11 / 3))
    out = {"logRate_R2": r2, "tc": float(t_c), "chirp_time_exponent": p_time, "chirp_time_target": -0.375,
           "chirp_freq_exponent": q_freq, "chirp_freq_target": 11 / 3,
           "I1_learns_inspiral": i1, "I2_chirp_time_law": i2, "I3_chirp_freq_law": i3,
           "chirp_discovered": bool(i1 and i2 and i3)}
    print(f"I1 learns inspiral rate (log R^2) {r2:.5f}: {i1}")
    print(f"I2 chirp time-law f∝(t_c-t)^p: p={p_time:.4f} (target -0.375): {i2}")
    print(f"I3 chirp freq-law df/dt∝f^q: q={q_freq:.4f} (target 3.667): {i3}")
    print(f"\nGRAVITATIONAL-WAVE CHIRP DISCOVERED (inspiral -> rising-frequency chirp, both exponents): {out['chirp_discovered']}")
    (RESULTS / "77_binary_chirp.json").write_text(json.dumps(out, indent=1))

    # the chirp waveform: h(t) ~ f^(2/3) cos(phase), phase = 2*pi*integral f dt
    phase = 2 * np.pi * np.cumsum(f_gw * np.gradient(TT)); h = (f_gw ** (2 / 3)) * np.cos(phase)
    fig, ax = plt.subplots(1, 2, figsize=(13, 5.2))
    ax[0].plot(TT, R, color="navy"); ax[0].set_xlabel("time"); ax[0].set_ylabel("separation r")
    ax[0].set_title(f"the two black holes spiral in (r: 60 -> merger)\nt_c (coalescence) = {t_c:.0f}")
    ax[1].plot(TT, h, color="crimson", lw=0.7)
    ax[1].set_xlabel("time"); ax[1].set_ylabel("strain h(t)")
    ax[1].set_title(f"the gravitational-wave CHIRP\nf∝(t_c-t)^{p_time:.3f} (GR -0.375), df/dt∝f^{q_freq:.2f} (GR 3.67)")
    fig.tight_layout(); fig.savefig(RESULTS / "77_binary_chirp.png", dpi=140)
    print("saved results/77_binary_chirp.json + .png")


if __name__ == "__main__":
    main()
