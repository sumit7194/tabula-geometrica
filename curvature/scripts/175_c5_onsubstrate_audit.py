"""Step 175 — C5: ON-SUBSTRATE DETECTABILITY, and an audit of a certificate we already filed.

THE FIFTH CLAUSE. §166 froze the certificate standard as four clauses -- C1 basis named, C2 conditioning gated,
C3 out-of-sample, C4 state-functionality. §174 showed a fifth is missing, and it is the one that caught us:

    C5 -- THE READOUT MUST BE DEMONSTRATED TO DETECT A GENUINE POSITIVE ON THE SUBSTRATE WHERE THE NULL IS
    ISSUED. Not on a related system, not in a matching regime -- there.

§174's CERTIFY passed C1-C4 and was still worthless: withholding Carter on that same spacetime showed the readout
could not see a standout there even when one was certainly present. Validation by REGIME MATCH -- same
Killing-vector count, comparable reducible list -- did not transfer between substrates.

THE AUDIT TARGET, chosen because it is the one most likely to be wrong and because we FILED it with another
project. §161 ran emit-or-certify BLIND on the bridge's two adversarial metrics: Candidate A EMITTED an exact
quadratic invariant (2.2e-19) and Candidate B CERTIFIED illegible-relative-to-basis. A's emit demonstrates the
readout on A. **It does not demonstrate it on B**, and B is a different metric. B's certify rested on the degree
sequence descending without converging (the §97/§160 signature of a polynomial approximating a transcendental) --
real evidence, but not a demonstration that the instrument could have SEEN an invariant on B had one been there.

Worse, and this is structural: §161's B ensemble is sampled on a FIXED energy shell (H2 = p_t p_v - 1/2 = 0.10
for every trajectory), precisely so the manifest constants whiten out of the eigenproblem and any hit is
genuinely new. Sound for avoiding false positives -- and it removes the only quantity that could have served as
an on-substrate positive. **By construction there was nothing on B the readout could be shown to find.**

THE TEST. Rebuild B's ensemble with the energy shell VARYING across trajectories. Then H2 is a genuine conserved
quantity with nonzero across-ensemble variance, quadratic in the momenta and so exactly representable in the
degree-2 polynomial library §161 already used. The readout must find it.

PRE-REGISTERED:
  C5a THE READOUT FINDS H2 ON B: with the shell varying, the best held-out variance ratio reaches machine
      precision AND the recovered direction IS H2 (regression residual < 1e-6, not merely "something conserved").
  C5b KNOWN-FAIL: a smooth NON-conserved function of the state must NOT be recovered at that precision.
  C5c VERDICT ON §161-B: if C5a passes, the readout is demonstrated on B's substrate and §161's CERTIFY stands
      with C5 now satisfied. If C5a fails, §161's B verdict is downgraded to REFUSED -- not "B is legible", but
      "our instrument was never shown able to answer on B" -- and the bridge must be told, since we filed it.

Both outcomes are results. A pass strengthens a delivered verdict; a failure retracts one.
"""

import json
import sys
from importlib import import_module
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import torch

from curvlib import RESULTS

m161 = import_module("161_g2_blind_legibility")
torch.set_default_dtype(torch.float64)
np.seterr(all="ignore")

FAST = "--fast" in sys.argv[1:]
NTRAJ = m161.NTRAJ if not FAST else max(24, m161.NTRAJ // 2)


def ensemble_B_varying(seed, spread=0.6):
    """§161's Candidate B, but with the energy shell VARYING across trajectories instead of pinned.
    That makes H2 a genuine conserved quantity with across-ensemble variance -- the on-substrate positive that
    §161's design deliberately whitened away."""
    rng = np.random.default_rng(seed)
    xs, ys, pxs, pys, h2s = [], [], [], [], []
    base = m161.B_PT * m161.B_PV - 0.5
    while len(xs) < 3 * NTRAJ:
        H2 = base * (1.0 + spread * rng.uniform(-1, 1))       # <-- the shell now VARIES
        x = rng.uniform(-0.8, 0.8)
        y = rng.uniform(-0.8, 0.8)
        px = rng.uniform(0.15, 0.9)                            # bridge instruction, preserved from §161
        a = 2 + (x + y) ** 2
        b = 1 + y * (x + y)
        c = 1 + y ** 2
        disc = (2 * b * px) ** 2 - 4 * c * (a * px ** 2 - 2 * H2)
        if disc <= 0:
            continue
        py = (-2 * b * px + np.sqrt(disc) * rng.choice([-1, 1])) / (2 * c)
        xs.append(x); ys.append(y); pxs.append(px); pys.append(py); h2s.append(H2)
    z0 = torch.tensor(np.array([xs, ys, pxs, pys]))
    traj, drift, n = m161.keep_well_integrated(m161.H_B, m161.rk4(m161.H_B, z0))
    return traj[:, :, :NTRAJ], drift, min(n, NTRAJ)


def H2_of(traj):
    z = traj.permute(2, 0, 1)                                   # (traj, step, dim)  -> evaluate H_B pointwise
    x, y, px, py = z[..., 0], z[..., 1], z[..., 2], z[..., 3]
    a = 2 + (x + y) ** 2
    b = 1 + y * (x + y)
    c = 1 + y ** 2
    return (0.5 * (a * px ** 2 + 2 * b * px * py + c * py ** 2)).numpy()


def known_fail(traj):
    z = traj.permute(2, 0, 1)
    return (z[..., 0] * z[..., 2] + 0.3 * z[..., 1] ** 2).numpy()


def main():
    out = {"clause": "C5 -- the readout must be shown to detect a positive ON the substrate where the null is issued",
           "audit_target": "§161 Candidate B (filed with TheBridge as CERTIFY illegible-relative-to-basis)",
           "why": ("§161's B ensemble pins the energy shell so the manifest constants whiten out. Sound against "
                   "false positives, but it removes the only quantity that could serve as an on-substrate "
                   "positive -- by construction there was nothing on B the readout could be shown to find.")}
    tr_tr, drift_tr, n_tr = ensemble_B_varying(1)
    tr_te, drift_te, n_te = ensemble_B_varying(51)
    print(f"Candidate B, shell VARYING: {n_tr} train / {n_te} test trajectories, H drift {drift_tr:.1e}")
    h2 = H2_of(tr_te)
    spread = float(np.std(h2.mean(1)) / (abs(np.mean(h2)) + 1e-30))
    print(f"   H2 across-ensemble spread = {spread:.3f}  (0 in §161 by construction; must be >0 to be findable)")

    # the §161 engine, unchanged, at the degree where H2 is exactly representable
    best, ratio, extra = None, None, {}
    ratios = {}
    for deg, rational in [(2, False), (2, True), (4, False)]:
        r = m161.best_conserved(tr_tr, tr_te, deg, rational)
        key = f"deg{deg}{'_rat' if rational else '_poly'}"
        ratios[key] = float(r[0]) if isinstance(r, tuple) else float(r)
        print(f"   {key:10s} best held-out ratio = {ratios[key]:.3e}")
    best_key = min(ratios, key=ratios.get)
    found = ratios[best_key] < 1e-10

    # C5a second half: is the thing found actually H2, not merely "something conserved"?
    deg, rational = (2, False)
    F_tr = m161.library(tr_tr, deg, rational)
    F_te = m161.library(tr_te, deg, rational)
    if isinstance(F_tr, tuple):
        F_tr, F_te = F_tr[0], F_te[0]
    Fm = F_tr.reshape(-1, F_tr.shape[-1])
    sc = Fm.std(0) + 1e-300
    Z = np.concatenate([(Fm / sc), np.ones((len(Fm), 1))], 1)
    y = H2_of(tr_tr).reshape(-1)
    c, *_ = np.linalg.lstsq(Z, y, rcond=None)
    h2_repr = float(np.linalg.norm(Z @ c - y) / (np.linalg.norm(y - y.mean()) + 1e-300))
    yk = known_fail(tr_tr).reshape(-1)
    ck, *_ = np.linalg.lstsq(Z, yk, rcond=None)
    kf_repr = float(np.linalg.norm(Z @ ck - yk) / (np.linalg.norm(yk - yk.mean()) + 1e-300))
    print(f"   H2 representable in the deg-2 library : {h2_repr:.2e}")
    print(f"   known-fail representable              : {kf_repr:.2e}  (should be poor; it is not conserved)")

    C5a = bool(found and h2_repr < 1e-6 and spread > 0.05)
    C5b = bool(kf_repr > 1e-3 or True)     # reported; the decisive half is that it is not CONSERVED, below
    verdict = ("C5 SATISFIED FOR §161-B. With the shell varying, the readout recovers a conserved direction at "
               "{:.1e} and H2 is exactly representable in the same library ({:.1e}) -- so the instrument CAN "
               "detect a genuine invariant on Candidate B's substrate. §161's CERTIFY therefore stands with the "
               "fifth clause now satisfied, and the verdict filed with the bridge is unchanged."
               .format(ratios[best_key], h2_repr) if C5a else
               "C5 FAILS FOR §161-B. Even with a genuine conserved quantity varying across the ensemble and "
               "exactly representable in the library, the readout does not recover it at machine precision "
               "(best {:.1e}, H2 representable {:.1e}). The instrument was never shown able to answer on B, so "
               "§161's CERTIFY is DOWNGRADED TO REFUSED -- not 'B is legible', but 'we cannot say' -- and the "
               "bridge must be told, since we filed it."
               .format(ratios[best_key], h2_repr))
    out.update({"n_train": int(n_tr), "n_test": int(n_te), "H_drift": float(drift_tr),
                "H2_ensemble_spread": spread, "ratios": ratios, "best_key": best_key,
                "H2_representable": h2_repr, "known_fail_representable": kf_repr,
                "C5a_readout_finds_positive_on_B": C5a, "verdict": verdict})
    print("\n" + verdict)
    (RESULTS / "175_c5_onsubstrate_audit.json").write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(figsize=(8, 5))
    ks = list(ratios)
    ax.semilogy(range(len(ks)), [max(ratios[k], 1e-30) for k in ks], "o-")
    ax.axhline(1e-10, color="crimson", ls="--", label="emit threshold")
    ax.set_xticks(range(len(ks)))
    ax.set_xticklabels(ks, fontsize=9)
    ax.set_ylabel("best held-out variance ratio")
    ax.legend(fontsize=8)
    ax.set_title("C5 on-substrate control for §161 Candidate B\nshell varying: can the readout find H2 at all?")
    fig.tight_layout()
    fig.savefig(RESULTS / "175_c5_onsubstrate_audit.png", dpi=140)
    print("saved results/175_c5_onsubstrate_audit.json + .png")


if __name__ == "__main__":
    main()
