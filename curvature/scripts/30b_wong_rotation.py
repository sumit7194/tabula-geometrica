"""Step 30b — Phase H row 2 fix round: does the lane state TRACK the rotating color charge?

The crude angular-travel metric (run 1) was confounded. The rigorous probe: the true color
charge Q(t) PRECESSES along the path (Wong). Retrain a color L=3 lane model, then for
held-out bodies decode the TRUE Q(t) (computed from the generator along the path) from the
lane-state trajectory w(t) via a single linear map.
  W3 (rotation, the crown): linear decode r of Q(t) from w(t) is HIGH (the internal state
     tracks the rotating charge) AND the decoded Q genuinely rotates (angle Q0->QT > 0).
  W4 (conservation): |decoded Q(t)| is ~constant along the rollout (the |Q| invariant).
Contrast: a 1-scalar electric body has no rotating vector — its internal state can't track one.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
import torch
from curvlib import RESULTS, V_MAX, X_RANGE
from importlib import import_module
from sklearn.linear_model import Ridge
from sklearn.model_selection import cross_val_predict

w = import_module("30_wong_color")


def true_Q_traj(x0, v0, Q0, dt=0.01):
    """True (x,v,Q) integrated; return Q sampled at the model's rollout times k*H."""
    s = np.concatenate([x0[:, None], v0[:, None], Q0], 1).astype(float)
    sub = int(round(w.H / dt))
    times = w.N_ROLL
    out = np.empty((len(x0), times, 3))
    step = 0
    for t in range(times):
        for _ in range(sub):
            k1 = w.deriv(s, True); k2 = w.deriv(s + .5 * dt * k1, True)
            k3 = w.deriv(s + .5 * dt * k2, True); k4 = w.deriv(s + dt * k3, True)
            s = s + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        out[:, t] = s[:, 2:5]
    return out


def main():
    data = w.make_dataset(True, seed=0)
    model, mse = w.train(data, 3, "fix", seed=0)
    print(f"color L=3 retrained: test {mse:.2e}")

    # held-out bodies: fresh starts, record model lane-state traj + true Q(t)
    rng = np.random.default_rng(11)
    n = 400
    held = np.arange(len(data["Q0"]) - 8, len(data["Q0"]))
    bsel = rng.choice(held, n)
    x0 = rng.uniform(*X_RANGE, n); v0 = rng.uniform(-V_MAX, V_MAX, n)
    X = np.stack([x0, v0], 1).astype(np.float32)
    with torch.no_grad():
        _, lanes = model.rollout(torch.from_numpy(X), torch.from_numpy(bsel), keep_lanes=True)
    lanes = lanes.numpy()                                  # (n, N_ROLL, 3)
    Qtrue = true_Q_traj(x0, v0, data["Q0"][bsel])          # (n, N_ROLL, 3)

    # W3: linear decode of true Q(t) from lane state w(t), pooled over bodies+times
    L = lanes.reshape(-1, lanes.shape[-1]); Q = Qtrue.reshape(-1, 3)
    rs = [float(np.corrcoef(cross_val_predict(Ridge(1.0), L, Q[:, j], cv=5), Q[:, j])[0, 1])
          for j in range(3)]
    # does the true charge actually rotate over the rollout? (angle Q0->QT)
    q0 = Qtrue[:, 0] / np.linalg.norm(Qtrue[:, 0], axis=1, keepdims=True)
    qT = Qtrue[:, -1] / np.linalg.norm(Qtrue[:, -1], axis=1, keepdims=True)
    rot = np.degrees(np.arccos(np.clip((q0 * qT).sum(1), -1, 1)))
    # W4: true |Q| conservation (sanity) + decoded |Q| conservation
    fit = Ridge(1.0).fit(L, Q)
    Qhat = fit.predict(L).reshape(n, w.N_ROLL, 3)
    dec_norm = np.linalg.norm(Qhat, axis=-1)
    dec_drift = float(np.median(dec_norm.std(1) / (dec_norm.mean(1) + 1e-9)))
    true_norm = np.linalg.norm(Qtrue, axis=-1)
    true_drift = float(np.median(true_norm.std(1) / true_norm.mean(1)))

    # probe ladder on the per-body code w0 vs the body's true Q0 (the embedding is FREE,
    # so Phase I predicts linear scramble + nonlinear recovery if the charge IS captured)
    from sklearn.neighbors import KNeighborsRegressor
    seen = np.array([i for i in range(len(data["Q0"])) if i not in held])
    W0 = model.w0(torch.from_numpy(seen)).detach().numpy()
    Q0s = data["Q0"][seen]
    lin0 = [float(np.corrcoef(cross_val_predict(Ridge(1.0), W0, Q0s[:, j], cv=5), Q0s[:, j])[0, 1]) for j in range(3)]
    nl0 = [float(np.corrcoef(cross_val_predict(KNeighborsRegressor(4), W0, Q0s[:, j], cv=5), Q0s[:, j])[0, 1]) for j in range(3)]
    print(f"w0->Q0 LINEAR r={[f'{x:.2f}' for x in lin0]} | NONLINEAR r={[f'{x:.2f}' for x in nl0]} "
          f"(nonlinear>>linear => free-embedding scramble per Phase I; info IS captured)")

    out = {"color_L3_mse": mse, "W3_decodeQ_r": rs, "W3_min_r": float(min(rs)),
           "w0_Q0_linear_r": lin0, "w0_Q0_nonlinear_r": nl0,
           "true_rotation_deg_med": float(np.median(rot)),
           "W4_decoded_norm_drift": dec_drift, "true_norm_drift": true_drift}
    print(f"W3 decode Q(t) from lane state: r = {[f'{x:.3f}' for x in rs]} "
          f"(min {min(rs):.3f}; gate >0.9 {'PASS' if min(rs) > 0.9 else 'FAIL'})")
    print(f"   true charge rotation over rollout: {np.median(rot):.1f}deg median "
          f"(confirms there IS a rotation to track)")
    print(f"W4 |Q| drift: decoded {dec_drift:.3f} vs true {true_drift:.4f} "
          f"(decoded should be small if conservation is tracked)")
    (RESULTS / "30b_wong_rotation.json").write_text(json.dumps(out, indent=1))
    print("saved results/30b_wong_rotation.json")


if __name__ == "__main__":
    main()
