"""Step 58 — EXOTIC: does a net discover CHARGE CONJUGATION (C / antimatter symmetry)?

Web-verified: C replaces every particle by its antiparticle (opposite charge); electromagnetism is
C-invariant (Lorentz force a=(q/m)v×B is ODD in q -> antiparticle curves oppositely); weak interactions
VIOLATE C; CPT is exact. Orthogonal question: can a net DISCOVER C as a structure-preserving symmetry —
that negating the (internal) charge gives the antiparticle's dynamics — and DETECT when C is violated?

Setup: charged bodies (q in [-1,1], both signs = matter+antimatter) in a magnetic field; predict the
ACCELERATION a(state; q) (odd in q makes C clean). An AMORTIZED net infers a signed charge code from
context (state, accel) pairs, predicts accel on query states. C operation = NEGATE the code.
Two worlds: C-SYMMETRIC (a = q v×B, odd in q) vs C-VIOLATING (add an even-in-q term eps*q^2*field).

Pre-reg (2026-06-17):
  A1 signed legible code: |corr(code, q)| > 0.9 (the net represents the charge incl. sign).
  A2 C discovered (symmetric world): negating the code flips the predicted force — pred(state,-code) ≈
     -pred(state,code), median cosine > 0.9. (Negating the internal charge = the antiparticle.)
  A3 C-violation detected: in the C-violating world the same equivariance cosine is LOWER by > 0.3 —
     the net discovers C exactly when the law is odd in charge, and sees it break otherwise.
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
from sklearn.linear_model import Ridge
from sklearn.model_selection import cross_val_predict
from torch import nn

B_AMP, B_CTR = 0.8, (0.6, -0.4)
WELL_W = 1.2
N_BODIES, PER_BODY, STEPS, HELD, CODE, KCTX = 48, 300, 6000, 8, 4, 24


def accel(state, q, eps):
    x, y, vx, vy = state[..., 0], state[..., 1], state[..., 2], state[..., 3]
    B = B_AMP * np.exp(-(((x - B_CTR[0]) ** 2) + (y - B_CTR[1]) ** 2) / 2.0)
    ax = q * vy * B; ay = -q * vx * B                              # magnetic: ODD in q (C-symmetric)
    g = np.exp(-(x ** 2 + y ** 2) / (2 * WELL_W ** 2))
    ax = ax + eps * q ** 2 * (-x) * g; ay = ay + eps * q ** 2 * (-y) * g   # EVEN in q -> C-violating
    return np.stack([ax, ay], -1)


def make_data(eps, seed=0):
    rng = np.random.default_rng(seed)
    q = rng.uniform(-1, 1, N_BODIES).astype(np.float32)
    S, A = [], []
    for i in range(N_BODIES):
        st = np.stack([rng.uniform(-2.5, 2.5, PER_BODY), rng.uniform(-2.5, 2.5, PER_BODY),
                       rng.uniform(-0.5, 0.5, PER_BODY), rng.uniform(-0.5, 0.5, PER_BODY)], 1).astype(np.float32)
        S.append(st); A.append(accel(st, q[i], eps).astype(np.float32))
    return {"q": q, "S": np.stack(S), "A": np.stack(A)}            # S:(B,P,4) A:(B,P,2)


class Amort(nn.Module):
    def __init__(s):
        super().__init__()
        s.enc = nn.Sequential(nn.Linear(6, 128), nn.GELU(), nn.Linear(128, 128), nn.GELU(), nn.Linear(128, CODE))
        s.net = nn.Sequential(nn.Linear(4 + CODE, 128), nn.GELU(), nn.Linear(128, 128), nn.GELU(), nn.Linear(128, 2))
    def code(s, ctx):
        return s.enc(ctx).mean(-2)
    def pred(s, state, code):
        c = code[:, None, :].expand(-1, state.shape[1], -1) if state.dim() == 3 else code
        return s.net(torch.cat([state, c], -1))


def train(d, seed=0):
    torch.manual_seed(seed); rng = np.random.default_rng(seed)
    S = torch.from_numpy(d["S"]); A = torch.from_numpy(d["A"]); SA = torch.cat([S, A], -1)
    seen = np.arange(N_BODIES - HELD); m = Amort(); opt = torch.optim.Adam(m.parameters(), lr=1e-3)
    for step in range(STEPS):
        bi = rng.choice(seen, 64)
        ci = np.stack([rng.choice(PER_BODY, KCTX, replace=False) for _ in bi])
        qi = rng.integers(0, PER_BODY, len(bi))
        ctx = SA[torch.from_numpy(bi)[:, None], torch.from_numpy(ci)]
        code = m.code(ctx)
        st = S[torch.from_numpy(bi), torch.from_numpy(qi)]; tg = A[torch.from_numpy(bi), torch.from_numpy(qi)]
        loss = nn.functional.mse_loss(m.net(torch.cat([st, code], -1)), tg)
        opt.zero_grad(); loss.backward(); opt.step()
        if step % 500 == 0: progress(f"58_eps{int(10*d.get('eps',0))}", step, STEPS, loss=float(loss.detach()))
    return m


def analyze(m, d):
    S = torch.from_numpy(d["S"]); A = torch.from_numpy(d["A"]); SA = torch.cat([S, A], -1)
    seen = np.arange(N_BODIES - HELD)
    with torch.no_grad():
        codes = m.code(SA[seen, :KCTX]).numpy()                    # (S, CODE)
    A1 = float(abs(np.corrcoef(cross_val_predict(Ridge(1.0), codes, d["q"][seen], cv=5), d["q"][seen])[0, 1]))
    # C-equivariance: pred(state, -code) vs -pred(state, code)
    with torch.no_grad():
        c = m.code(SA[seen, :KCTX])
        st = S[seen, KCTX:KCTX + 80]                               # query states
        pp = m.pred(st, c).numpy(); pn = m.pred(st, -c).numpy()
    pp = pp.reshape(-1, 2); pn = pn.reshape(-1, 2)
    cos = np.sum(pn * (-pp), 1) / (np.linalg.norm(pn, axis=1) * np.linalg.norm(pp, axis=1) + 1e-9)
    return A1, float(np.median(cos))


def main():
    sym = make_data(0.0); sym["eps"] = 0.0
    vio = make_data(0.7); vio["eps"] = 0.7
    A1_s, ceq_s = analyze(train(sym), sym)
    A1_v, ceq_v = analyze(train(vio), vio)
    print(f"C-symmetric world: code->q |r|={A1_s:.2f} | C-equivariance cos={ceq_s:.2f}")
    print(f"C-violating world: code->q |r|={A1_v:.2f} | C-equivariance cos={ceq_v:.2f}")

    a1 = bool(A1_s > 0.9)
    a2 = bool(ceq_s > 0.9)
    a3 = bool(ceq_s - ceq_v > 0.3)
    out = {"symmetric": {"code_decode_q": A1_s, "C_equivariance_cos": ceq_s},
           "violating": {"code_decode_q": A1_v, "C_equivariance_cos": ceq_v},
           "A1_signed_legible_code": a1, "A2_C_discovered": a2, "A3_violation_detected": a3,
           "charge_conjugation_discovered": bool(a1 and a2 and a3)}
    print(f"\nA1 signed legible code (sym |r| {A1_s:.2f}>0.9): {a1}")
    print(f"A2 C discovered — negate code flips force (sym cos {ceq_s:.2f}>0.9): {a2}")
    print(f"A3 C-violation detected (sym {ceq_s:.2f} - vio {ceq_v:.2f} > 0.3): {a3}")
    print(f"\nCHARGE CONJUGATION (C / antimatter symmetry) DISCOVERED: {out['charge_conjugation_discovered']}")
    (RESULTS / "58_antimatter_cpt.json").write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.bar([0, 1], [ceq_s, ceq_v], color=["seagreen", "crimson"])
    ax.set_xticks([0, 1]); ax.set_xticklabels(["C-symmetric world\n(a odd in q)", "C-violating world\n(even q² term)"])
    ax.set_ylabel("C-equivariance: cos(pred(−code), −pred(code))"); ax.set_ylim(0, 1)
    ax.axhline(0.9, ls=":", color="gray")
    ax.set_title("antimatter: negating the internal charge flips the force\n(the net discovers C — and detects its violation)")
    fig.tight_layout(); fig.savefig(RESULTS / "58_antimatter_cpt.png", dpi=140)
    print("saved results/58_antimatter_cpt.json + .png")


if __name__ == "__main__":
    main()
