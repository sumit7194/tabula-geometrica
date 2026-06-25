"""Step 135 — Wong v4: does fuller OBSERVABILITY (multiple field probes) cross the dynamic-legibility ceiling?

Phase H row 2 / vm_plan E. Script 106 (Wong v3) showed a structure-preserving SO(3) charge update CONSERVES |Q| exactly
and roughly DOUBLES legibility of the rotating color charge (linear 0.29 -> 0.56-0.64) but does NOT reach the 0.70 gate
or the static ceiling (0.89). The refined lesson there: structure is NECESSARY but a DYNAMIC conserved quantity also
needs to be OBSERVABLE -- trajectory-only supervision sees Q only via the SCALAR a = well(x) + Q.E(x) along ONE field,
i.e. one projection of the rotating Q. This is a partial-observability ceiling.

v4 fix (this script): give the learner MULTIPLE FIELD PROBES. Each body is rolled out under K different color-electric
fields E^(k)(x) (diverse directions/centers) while the TRANSPORT field A(x) is SHARED (so the SO(3) structure of 106 is
kept; the charge still precesses by the same connection). K diverse projections Q.E^(k) triangulate the full rotating
Q(t). We train the SAME orthogonal-SO(3) model at K=1 (the 106 single-field baseline) and K=4 (full observability) and
test whether legibility crosses 0.70.

Pre-reg (2026-06-26):
  V1 FIT: the multi-field model fits held-out trajectories across all K fields (MSE comparable to single-field, < 2x).
  V2 CONSERVATION: model |Q(t)| drift < 1e-3 (orthogonal SO(3), by construction).
  V3 OBSERVABILITY CROSSES THE CEILING (headline): with K=4 fields, the linear decode of the true rotating Q(t) from the
     model's charge state has min-over-components > 0.70 AND beats the K=1 baseline by > 0.10 -- fuller observability is
     what the partial-observability ceiling needed. (Honest either way: if K=4 does NOT cross 0.70, the ceiling is deeper
     than observability and the dynamic charge has an intrinsic legibility limit under trajectory supervision.)
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
from sklearn.linear_model import Ridge
from sklearn.model_selection import cross_val_predict
from sklearn.neighbors import KNeighborsRegressor
from torch import nn

from curvlib import RESULTS, TRAJ_TIMES, V_MAX, WELL_DEPTH, WELL_WIDTH, X_RANGE, progress

H = 0.1
N_ROLL = int(round(TRAJ_TIMES[-1] / H))
TARGETS = [int(round(t / H)) for t in TRAJ_TIMES]
DEVICE = "cuda" if "--device" in sys.argv and torch.cuda.is_available() else (
    sys.argv[sys.argv.index("--device") + 1] if "--device" in sys.argv else "cpu")
STEPS = 30000

A_AMP = np.array([0.9, 0.7, 0.8]); A_C = np.array([-0.5, 0.6, 1.1])        # shared transport (gauge potential)
E_AMP_K = np.array([[0.30, 0.35, 0.25], [0.32, 0.10, 0.40],                # K=4 diverse color-electric probe fields
                    [0.15, 0.40, 0.30], [0.38, 0.28, 0.12]])
E_C_K = np.array([[0.8, -1.0, 0.2], [-0.6, 0.5, 1.0],
                  [1.0, 0.3, -0.8], [0.0, -0.4, 0.7]])
K_FIELDS = len(E_AMP_K)
K_SNIP = 4


def _well(x):
    return -WELL_DEPTH * x * np.exp(-x ** 2 / (2 * WELL_WIDTH ** 2)) / WELL_WIDTH ** 2


def deriv(state, e_amp, e_c):
    x, v, Q = state[..., 0], state[..., 1], state[..., 2:5]
    E = e_amp * np.exp(-((x[..., None] - e_c) ** 2) / 2)
    a = _well(x) + (Q * E).sum(-1)
    Af = A_AMP * np.exp(-((x[..., None] - A_C) ** 2) / 2)
    dQ = -v[..., None] * np.cross(Af, Q)                                  # shared SO(3) transport; |Q| conserved
    return np.concatenate([v[..., None], a[..., None], dQ], -1)


def integ(x0, v0, Q0, e_amp, e_c, dt=0.01, keep_Q=False):
    s = np.concatenate([x0[:, None], v0[:, None], Q0], 1).astype(float)
    grab = {int(round(t / dt)): i for i, t in enumerate(TRAJ_TIMES)}; sub = int(round(H / dt))
    xout = np.empty((len(x0), len(TRAJ_TIMES))); Qout = np.empty((len(x0), N_ROLL, 3)) if keep_Q else None
    for step in range(1, int(round(TRAJ_TIMES[-1] / dt)) + 1):
        k1 = deriv(s, e_amp, e_c); k2 = deriv(s + .5 * dt * k1, e_amp, e_c)
        k3 = deriv(s + .5 * dt * k2, e_amp, e_c); k4 = deriv(s + dt * k3, e_amp, e_c)
        s = s + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        if step in grab:
            xout[:, grab[step]] = s[:, 0]
        if keep_Q and step % sub == 0:
            Qout[:, step // sub - 1] = s[:, 2:5]
    return (xout, Qout) if keep_Q else xout


def make_data(seed=0, n_bodies=160, per_body=80):
    rng = np.random.default_rng(seed)
    Q0 = rng.normal(size=(n_bodies, 3)); Q0 /= np.linalg.norm(Q0, axis=1, keepdims=True)
    Q0 *= rng.uniform(0.4, 1.0, (n_bodies, 1))
    snip = np.empty((n_bodies, K_FIELDS * K_SNIP, 5), np.float32)
    qx, qv, qy, body, field = [], [], [], [], []
    for i in range(n_bodies):
        for k in range(K_FIELDS):
            sx = rng.uniform(*X_RANGE, K_SNIP); sv = rng.uniform(-V_MAX, V_MAX, K_SNIP)
            sp = integ(sx, sv, np.tile(Q0[i], (K_SNIP, 1)), E_AMP_K[k], E_C_K[k])
            snip[i, k * K_SNIP:(k + 1) * K_SNIP] = np.concatenate([sx[:, None], sv[:, None], sp], 1)
            x0 = rng.uniform(*X_RANGE, per_body); v0 = rng.uniform(-V_MAX, V_MAX, per_body)
            qy.append(integ(x0, v0, np.tile(Q0[i], (per_body, 1)), E_AMP_K[k], E_C_K[k]))
            qx.append(x0); qv.append(v0); body.append(np.full(per_body, i)); field.append(np.full(per_body, k))
    held = np.arange(n_bodies - 20, n_bodies)
    return {"Q0": Q0, "held": held, "snip": snip,
            "qx": np.concatenate(qx).astype(np.float32), "qv": np.concatenate(qv).astype(np.float32),
            "qy": np.concatenate(qy).astype(np.float32), "body": np.concatenate(body).astype(np.int64),
            "field": np.concatenate(field).astype(np.int64)}


def so3_exp(omega):
    n = omega.shape[0]; K = omega.new_zeros(n, 3, 3)
    a, b, c = omega[:, 0], omega[:, 1], omega[:, 2]
    K[:, 0, 1] = -c; K[:, 0, 2] = b; K[:, 1, 0] = c; K[:, 1, 2] = -a; K[:, 2, 0] = -b; K[:, 2, 1] = a
    return torch.matrix_exp(K)


class ModelV4(nn.Module):
    """amortized Q0 + shared SO(3) transport + field-conditioned kinematics (the only field dependence is the force)."""

    def __init__(self):
        super().__init__()
        self.enc = nn.Sequential(nn.Linear(5, 64), nn.Tanh(), nn.Linear(64, 64), nn.Tanh(), nn.Linear(64, 3))
        self.gen = nn.Sequential(nn.Linear(2, 128), nn.Tanh(), nn.Linear(128, 128), nn.Tanh(),
                                 nn.Linear(128, 128), nn.Tanh(), nn.Linear(128, 3))   # shared transport (field-indep)
        self.kin = nn.Sequential(nn.Linear(2 + 3 + K_FIELDS, 128), nn.Tanh(), nn.Linear(128, 128), nn.Tanh(),
                                 nn.Linear(128, 2))                                    # force depends on the field

    def code(self, snip, body):
        return self.enc(snip[body]).mean(1)

    def rollout(self, snip, body, x0, v0, fk, keep=False):
        Q = self.code(snip, body); xv = torch.stack([x0, v0], 1)
        oh = torch.zeros(len(body), K_FIELDS, device=xv.device); oh[torch.arange(len(body)), fk] = 1.0
        xs, Qs = [], []
        for step in range(1, N_ROLL + 1):
            Q = torch.bmm(so3_exp(H * self.gen(xv)), Q[..., None])[..., 0]
            xv = xv + H * self.kin(torch.cat([xv, Q, oh], 1))
            if keep:
                Qs.append(Q.clone())
            if step in TARGETS:
                xs.append(xv[:, :1])
        return (torch.cat(xs, 1), torch.stack(Qs, 1)) if keep else torch.cat(xs, 1)


def train(d, k_use, seed=0):
    """train on the first k_use field probes (k_use=1 -> the 106 single-field baseline)."""
    dev = DEVICE
    snip = torch.from_numpy(d["snip"]).to(dev)
    X = torch.from_numpy(d["qx"]).to(dev); V = torch.from_numpy(d["qv"]).to(dev); Y = torch.from_numpy(d["qy"]).to(dev)
    F = torch.from_numpy(d["field"]).to(dev); bdy = torch.from_numpy(d["body"]).to(dev)
    is_h = np.isin(d["body"], d["held"]); use = np.where((~is_h) & (d["field"] < k_use))[0]
    torch.manual_seed(135 + k_use); rng = np.random.default_rng(seed)
    m = ModelV4().to(dev); opt = torch.optim.Adam(m.parameters(), lr=1e-3)
    for step in range(STEPS):
        idx = use[rng.integers(0, len(use), 256)]
        pred = m.rollout(snip, bdy[idx], X[idx], V[idx], F[idx])
        loss = nn.functional.mse_loss(pred, Y[idx])
        opt.zero_grad(); loss.backward(); opt.step()
        if step % 1000 == 0:
            progress(f"135_wong_K{k_use}", step, STEPS, loss=float(loss.detach()))
    return m.eval()


def evaluate(m, d, k_use):
    dev = DEVICE
    snip = torch.from_numpy(d["snip"]).to(dev)
    is_h = np.isin(d["body"], d["held"]); hi = np.where(is_h & (d["field"] < k_use))[0]
    X = torch.from_numpy(d["qx"]).to(dev); V = torch.from_numpy(d["qv"]).to(dev); Y = torch.from_numpy(d["qy"]).to(dev)
    F = torch.from_numpy(d["field"]).to(dev); bdy = torch.from_numpy(d["body"]).to(dev)
    with torch.no_grad():
        mse = float(((m.rollout(snip, bdy[hi], X[hi], V[hi], F[hi]) - Y[hi]) ** 2).mean())
    # decode true Q(t) from the model's charge state, pooled over the k_use fields, held-out bodies
    rng = np.random.default_rng(11); n = 400
    L, Qt, drifts = [], [], []
    for k in range(k_use):
        hb = rng.choice(d["held"], n)
        x0 = rng.uniform(*X_RANGE, n).astype(np.float32); v0 = rng.uniform(-V_MAX, V_MAX, n).astype(np.float32)
        fk = torch.full((n,), k, dtype=torch.long, device=dev)
        with torch.no_grad():
            _, Qm = m.rollout(snip, torch.from_numpy(hb).to(dev), torch.from_numpy(x0).to(dev),
                              torch.from_numpy(v0).to(dev), fk, keep=True)
        Qm = Qm.cpu().numpy()
        _, Qtrue = integ(x0.astype(float), v0.astype(float), d["Q0"][hb], E_AMP_K[k], E_C_K[k], keep_Q=True)
        L.append(Qm.reshape(-1, 3)); Qt.append(Qtrue.reshape(-1, 3))
        qn = np.linalg.norm(Qm, axis=-1); drifts.append(np.median(qn.std(1) / (qn.mean(1) + 1e-9)))
    Lf = np.concatenate(L); Qf = np.concatenate(Qt)
    rs = [float(np.corrcoef(cross_val_predict(Ridge(1.0), Lf, Qf[:, j], cv=5), Qf[:, j])[0, 1]) for j in range(3)]
    rs_nl = [float(np.corrcoef(cross_val_predict(KNeighborsRegressor(8), Lf, Qf[:, j], cv=5), Qf[:, j])[0, 1]) for j in range(3)]
    return {"mse": mse, "decode_linear_r": rs, "min_linear_r": float(min(rs)),
            "min_nonlinear_r": float(min(rs_nl)), "model_Q_drift": float(np.median(drifts))}


def main():
    d = make_data(seed=0)
    print(f"device={DEVICE}, K={K_FIELDS} fields, n_bodies=160")
    m1 = train(d, 1); r1 = evaluate(m1, d, 1)                              # single-field baseline (~106)
    m4 = train(d, K_FIELDS); r4 = evaluate(m4, d, K_FIELDS)               # full observability

    v1 = bool(r4["mse"] < 2 * r1["mse"])
    v2 = bool(r4["model_Q_drift"] < 1e-3)
    v3 = bool(r4["min_linear_r"] > 0.70 and (r4["min_linear_r"] - r1["min_linear_r"]) > 0.10)

    out = {"K_fields": K_FIELDS, "single_field_K1": r1, "full_observability_K4": r4,
           "V1_fit": v1, "V2_conservation": v2, "V3_observability_crosses_ceiling": v3,
           "observability_resolves_ceiling": bool(v1 and v2 and v3),
           "verdict": ("OBSERVABILITY CROSSES THE DYNAMIC-LEGIBILITY CEILING. With the same orthogonal-SO(3) structure as "
                       "Wong v3 (|Q| drift {:.0e}, exact), adding MULTIPLE field probes (K={} diverse color-electric "
                       "fields, shared transport) raises the linear legibility of the rotating Q(t) from {:.2f} (single "
                       "field, ~the 106 ceiling) to {:.2f} (full observability) -- crossing 0.70. The partial-"
                       "observability ceiling was real: a dynamic conserved quantity geometrizes legibly once it is both "
                       "STRUCTURE-PRESERVED (SO(3)) AND OBSERVABLE (multiple projections). Closes the Wong open thread."
                       .format(r4["model_Q_drift"], K_FIELDS, r1["min_linear_r"], r4["min_linear_r"])
                       if (v1 and v2 and v3) else
                       "PARTIAL/HONEST -- see numbers. If K=4 did not cross 0.70, the ceiling is DEEPER than observability: "
                       "the rotating charge has an intrinsic legibility limit under trajectory supervision (structure + "
                       "observability still insufficient).")}
    print(f"\nsingle-field K=1: min linear r {r1['min_linear_r']:.3f} (nl {r1['min_nonlinear_r']:.3f}), mse {r1['mse']:.2e}")
    print(f"full-obs   K={K_FIELDS}: min linear r {r4['min_linear_r']:.3f} (nl {r4['min_nonlinear_r']:.3f}), mse {r4['mse']:.2e}, |Q|drift {r4['model_Q_drift']:.1e}")
    print(f"V1 fit {v1} | V2 conservation {v2} | V3 observability crosses 0.70 {v3}")
    print(f"\nOBSERVABILITY RESOLVES THE CEILING: {out['observability_resolves_ceiling']}")
    (RESULTS / "135_wong_observability.json").write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(figsize=(7.5, 5))
    x = np.arange(3); wd = 0.38
    ax.bar(x - wd / 2, r1["decode_linear_r"], wd, color="crimson", label=f"single field K=1 (min {r1['min_linear_r']:.2f})")
    ax.bar(x + wd / 2, r4["decode_linear_r"], wd, color="seagreen", label=f"K={K_FIELDS} probes (min {r4['min_linear_r']:.2f})")
    ax.axhline(0.70, ls="--", c="k", lw=0.7, label="legibility gate"); ax.set_xticks(x); ax.set_xticklabels(["Q0", "Q1", "Q2"])
    ax.set_ylabel("linear decode r of true rotating Q(t)"); ax.set_ylim(0, 1); ax.legend(fontsize=8)
    ax.set_title("Wong v4: fuller observability (multiple field probes) vs the single-field ceiling")
    fig.tight_layout(); fig.savefig(RESULTS / "135_wong_observability.png", dpi=140)
    print("saved results/135_wong_observability.json + .png")


if __name__ == "__main__":
    main()
