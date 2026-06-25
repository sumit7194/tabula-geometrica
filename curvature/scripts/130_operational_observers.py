"""Step 130 — operational observers: discover the interval from RADAR light-timings (+ clock noise), not given coords.

Phase 1b separate-angle probe (notes/build_queue.md; field_guide sec9 loose end). Phase A discovered the Minkowski
interval from GIVEN coordinates (t,x). Here the observers are OPERATIONAL: an observer assigns an event its radar
coordinates via light signals -- send a pulse at proper time T_send, it reflects off the event, returns at T_receive
(on the observer's OWN, noisy clock). The net never sees (t,x); only the raw light-signal timings.

Bondi k-calculus (web-known): for an event with rest-frame interval s^2 = t^2 - x^2 (timelike, t>|x|), the radar
timings are T_send = t - x, T_receive = t + x, so s^2 = T_send * T_receive. Under a boost of rapidity phi the timings
DOPPLER-scale, T_send -> T_send * e^{-phi}, T_receive -> T_receive * e^{+phi} (the factors are Bondi's k = e^{phi}),
so each observer measures DIFFERENT timings but the PRODUCT T_send*T_receive is INVARIANT = s^2. The unique function
of (T_send, T_receive) invariant under that scaling is a function of the product -- so a strict-distance Siamese net
("same event seen by two observers' radar?") is FORCED to discover s^2 = T_send*T_receive.

Pre-reg (2026-06-25):
  O1 INTERVAL FROM OPERATIONAL TIMINGS: a K=1 Siamese net saturates (same/different-event accuracy > 0.9) and its
     1-D latent decodes the interval s^2 = T_send*T_receive (isotonic R^2 > 0.95) -- the interval emerges from raw
     light-signal timings, never given coordinates.
  O2 CLOCK-NOISE ROBUST: with realistic multiplicative clock noise on the timings, the invariant still emerges
     (accuracy > 0.85, isotonic R^2 > 0.9).
  O3 IT IS THE PRODUCT (Lorentz/k-calculus), NOT EUCLIDEAN: the latent tracks the product s^2=T_s*T_r (|r|>0.95), and
     the product is DOPPLER-INVARIANT across observers (CoV~0) while the Euclidean T_s^2+T_r^2 is not (CoV_euclid >
     5*CoV_product) -- so the only viable invariant is the product.
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
from scipy.stats import spearmanr
from torch import nn

from curvlib import RESULTS, progress


def observe(t, x, phi, noise, rng):
    """operational radar timings of event (t,x) by an observer of rapidity phi, with multiplicative clock noise."""
    Ts = (t - x) * np.exp(-phi); Tr = (t + x) * np.exp(phi)       # Bondi Doppler scaling; product invariant = s^2
    Ts = Ts * (1 + noise * rng.standard_normal(*np.shape(t)))
    Tr = Tr * (1 + noise * rng.standard_normal(*np.shape(t)))
    return np.stack([Ts, Tr], -1)


def make_pairs(n, noise, rng):
    """positive: same event, two random observers; negative: different events."""
    obsA, obsB, same, s2 = [], [], [], []
    for _ in range(n):
        t = rng.uniform(1.0, 5.0); x = rng.uniform(-0.9, 0.9) * t  # timelike future event
        phiA, phiB = rng.uniform(-1.4, 1.4, 2)
        a = observe(np.array(t), np.array(x), phiA, noise, rng)
        if rng.random() < 0.5:
            b = observe(np.array(t), np.array(x), phiB, noise, rng); same.append(1.0)
        else:
            t2 = rng.uniform(1.0, 5.0); x2 = rng.uniform(-0.9, 0.9) * t2
            b = observe(np.array(t2), np.array(x2), phiB, noise, rng); same.append(0.0)
        obsA.append(a); obsB.append(b); s2.append((t - x) * (t + x))
    return (np.array(obsA, np.float32), np.array(obsB, np.float32), np.array(same, np.float32), np.array(s2, np.float32))


class Siam(nn.Module):
    def __init__(s, K):
        super().__init__()
        s.f = nn.Sequential(nn.Linear(2, 64), nn.Tanh(), nn.Linear(64, 64), nn.Tanh(), nn.Linear(64, K))
        s.logb = nn.Parameter(torch.zeros(1))

    def forward(s, a, b):
        za, zb = s.f(a), s.f(b)
        d = ((za - zb) ** 2).sum(-1)
        return torch.sigmoid(s.logb - d), za                      # P(same) = sigmoid(bias - distance)


def train(K, noise, seed=0, steps=4000):
    torch.manual_seed(seed); rng = np.random.default_rng(seed)
    A, B, Y, _ = make_pairs(6000, noise, rng)
    mu = A.reshape(-1, 2).mean(0); sd = A.reshape(-1, 2).std(0) + 1e-6   # standardize raw timings
    At = torch.from_numpy((A - mu) / sd); Bt = torch.from_numpy((B - mu) / sd); Yt = torch.from_numpy(Y)
    m = Siam(K); opt = torch.optim.Adam(m.parameters(), lr=2e-3)
    g = np.random.default_rng(seed + 1)
    for step in range(steps):
        idx = g.integers(0, len(At), 256)
        p, _ = m(At[idx], Bt[idx])
        loss = nn.functional.binary_cross_entropy(p.clamp(1e-6, 1 - 1e-6), Yt[idx])
        opt.zero_grad(); loss.backward(); opt.step()
        if step % 1000 == 0:
            progress(f"130_K{K}_n{noise}", step, steps, loss=float(loss.detach()))
    return m.eval(), (mu, sd)


def evaluate(m, norm, noise, seed=99):
    mu, sd = norm; rng = np.random.default_rng(seed)
    A, B, Y, s2 = make_pairs(2000, noise, rng)
    At = torch.from_numpy((A - mu) / sd); Bt = torch.from_numpy((B - mu) / sd)
    with torch.no_grad():
        p, za = m(At, Bt)
    acc = float(((p.numpy() > 0.5) == (Y > 0.5)).mean())
    z = za.numpy()[:, 0]
    # isotonic R^2 of the 1-D latent vs the true interval s^2 (monotone, auto direction)
    from sklearn.isotonic import IsotonicRegression
    order = np.argsort(s2); zr = z[order]
    iso = IsotonicRegression(out_of_bounds="clip", increasing="auto").fit(s2[order], zr)
    pred = iso.predict(s2[order]); r2 = float(1 - np.sum((zr - pred) ** 2) / (np.sum((zr - zr.mean()) ** 2) + 1e-12))
    Ts, Tr = A[:, 0], A[:, 1]
    r_prod = abs(float(spearmanr(z, Ts * Tr).correlation))
    # Doppler-invariance: across observers of a FIXED event, is the product invariant but the Euclidean combo not?
    rng = np.random.default_rng(123); covp, cove = [], []
    for _ in range(120):
        t = rng.uniform(1, 5); x = rng.uniform(-0.9, 0.9) * t
        phis = rng.uniform(-1.4, 1.4, 12)
        Tsf = (t - x) * np.exp(-phis); Trf = (t + x) * np.exp(phis)
        prod = Tsf * Trf; eucl = Tsf ** 2 + Trf ** 2
        covp.append(prod.std() / (abs(prod.mean()) + 1e-9)); cove.append(eucl.std() / (abs(eucl.mean()) + 1e-9))
    return acc, r2, r_prod, float(np.mean(covp)), float(np.mean(cove))


def main():
    # O1: clean (no noise), K=1 saturates + decodes the interval
    m1, n1 = train(1, 0.0); acc1, r2_1, rprod, covp, cove = evaluate(m1, n1, 0.0)
    o1 = bool(acc1 > 0.9 and r2_1 > 0.95)

    # O2: clock-noise robust
    m1n, n1n = train(1, 0.05); acc_n, r2_n, _, _, _ = evaluate(m1n, n1n, 0.05)
    o2 = bool(acc_n > 0.85 and r2_n > 0.9)

    # O3: product (Lorentz/k-calculus) is Doppler-invariant, Euclidean is not
    o3 = bool(rprod > 0.95 and cove > 5 * covp)

    out = {"O1_acc": acc1, "O1_isotonic_r2": r2_1, "O2_acc_noisy": acc_n, "O2_isotonic_r2_noisy": r2_n,
           "O3_latent_vs_product": rprod, "O3_cov_product": covp, "O3_cov_euclidean": cove,
           "O1_interval_from_timings": o1, "O2_clock_noise_robust": o2, "O3_product_not_euclidean": o3,
           "operational_interval_discovered": bool(o1 and o2 and o3),
           "verdict": ("OPERATIONAL INTERVAL DISCOVERED: from raw RADAR light-signal timings (T_send, T_receive) -- "
                       "never given coordinates -- a strict-distance Siamese net discovers the Minkowski interval. K=1 "
                       "saturates (same/diff-event acc {:.2f}) and the 1-D latent decodes s^2 = T_send*T_receive "
                       "(isotonic R^2 {:.3f}). It survives clock noise (acc {:.2f}, R^2 {:.2f}). And the invariant is "
                       "the PRODUCT (Bondi k-calculus / Lorentz, latent |r|={:.3f}): across observers of a fixed event "
                       "the product is Doppler-INVARIANT (CoV {:.3f}) while the Euclidean T_s^2+T_r^2 is not (CoV {:.2f}) "
                       "-- so the product is the only viable invariant. The interval emerges from operational "
                       "measurements (no fixed coordinate frame given)."
                       .format(acc1, r2_1, acc_n, r2_n, rprod, covp, cove)
                       if (o1 and o2 and o3) else "PARTIAL -- see numbers (honest).")}
    print(f"O1 interval from timings: K=1 acc={acc1:.2f} (>0.9), isotonic R2={r2_1:.3f} (>0.95): {o1}")
    print(f"O2 clock-noise robust: acc={acc_n:.2f} (>0.85), R2={r2_n:.3f} (>0.9): {o2}")
    print(f"O3 product (Doppler-invariant) not euclidean: latent|r|={rprod:.3f}, CoV product={covp:.3f} vs euclidean={cove:.2f} (>5x): {o3}")
    print(f"\nOPERATIONAL INTERVAL DISCOVERED: {out['operational_interval_discovered']}")
    (RESULTS / "130_operational_observers.json").write_text(json.dumps(out, indent=1))

    rng = np.random.default_rng(7); A, B, Y, s2 = make_pairs(1500, 0.0, rng)
    At = torch.from_numpy((A - n1[0]) / n1[1])
    with torch.no_grad():
        _, za = m1(At, At)
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.8))
    ax[0].scatter(s2, za.numpy()[:, 0], s=8, alpha=0.4, c="seagreen")
    ax[0].set_xlabel("true interval s² = T_send·T_receive"); ax[0].set_ylabel("K=1 latent")
    ax[0].set_title(f"O1 · interval from radar timings (iso R²={r2_1:.3f})")
    ax[1].bar(["product\nT_s·T_r", "Euclidean\nT_s²+T_r²"], [covp, cove], color=["seagreen", "crimson"])
    ax[1].set_ylabel("CoV across observers (same event)"); ax[1].set_yscale("log")
    ax[1].set_title(f"O3 · product is Doppler-INVARIANT (CoV {covp:.3f} vs {cove:.2f})")
    fig.suptitle("Operational observers: the interval from radar light-timings (Bondi k-calculus), no coordinates given")
    fig.tight_layout(); fig.savefig(RESULTS / "130_operational_observers.png", dpi=140)
    print("saved results/130_operational_observers.json + .png")


if __name__ == "__main__":
    main()
