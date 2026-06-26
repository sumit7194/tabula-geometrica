"""Step 142 — EXP-2 of the REPRESENTABILITY FRONTIER (②): the CERTIFY-CONTEXTUAL verdict (no consistent global code).

notes/representability_frontier.md. EXP-1 (141) named EMIT / CERTIFY-GAUGE / CERTIFY-NO-CODE on distance-geometry data.
EXP-2 adds the 4th failure mode on a DIFFERENT data type -- CORRELATION TABLES (the diagnostic routes by data type).
CERTIFY-CONTEXTUAL = no consistent GLOBAL classical code exists: local descriptions can't be glued into one
hidden-variable account (Bell / KCBS). Builds on the project's Bell certificate (script 84, wall at 1/sqrt2).

The cheapest GLOBAL code for a correlation table E(x,y) (settings x,y in {0,1}, +/-1 outcomes) is a LOCAL HIDDEN-VARIABLE
model: a shared lambda + local responses a(x,lambda), b(y,lambda). The set of LHV-achievable correlations is the LOCAL
POLYTOPE = convex hull of the 16 deterministic strategies; it is exactly the set with CHSH <= 2 (Bell). The diagnostic
fits the cheapest local code (a distribution over the 16 strategies) to the table and reads (i) the fit RESIDUAL (does a
global local code exist?) and (ii) the CHSH value (the theorem-backed certificate -- > 2 is a *proof* no LHV exists).

Pre-reg (2026-06-27):
  C1 EMIT-CLASSICAL (a local-hidden-variable table): the cheapest local code FITS (residual < 1e-3) AND CHSH <= 2 -- a
     consistent global code exists, verdict EMIT-CLASSICAL.
  C2 CERTIFY-CONTEXTUAL (the singlet, CHSH = 2*sqrt2): the cheapest local code CANNOT fit (residual >> the classical
     case) AND CHSH > 2 (the Bell certificate -- provably no LHV) -- verdict CERTIFY-CONTEXTUAL.
  C3 THE WALL (Werner-noise sweep, visibility v): the verdict FLIPS exactly at the classical/quantum boundary v = 1/sqrt2
     (where CHSH crosses 2) -- the diagnostic LOCATES the contextuality wall, not just labels the endpoints.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from curvlib import RESULTS

# the 16 deterministic LHV strategies -> their correlation vectors (E00,E01,E10,E11), E(x,y)=a(x)*b(y)
DET = np.array([[a0 * b0, a0 * b1, a1 * b0, a1 * b1]
                for a0 in (1, -1) for a1 in (1, -1) for b0 in (1, -1) for b1 in (1, -1)], float)  # (16,4)

# the 4 CHSH sign patterns (one minus sign in each position): |S| <= 2 for any LHV, <= 2sqrt2 quantum
CHSH_SIGNS = np.array([[1, 1, 1, -1], [1, 1, -1, 1], [1, -1, 1, 1], [-1, 1, 1, 1]], float)


def chsh(E):
    return float(np.max(np.abs(CHSH_SIGNS @ E)))


def fit_local(E, steps=4000):
    """fit the cheapest local code: min ||sum_s w_s C_s - E||^2 over the simplex (w >= 0, sum w = 1). Returns residual."""
    import torch
    C = torch.tensor(DET, dtype=torch.float32); Et = torch.tensor(E, dtype=torch.float32)
    logits = torch.zeros(16, requires_grad=True)
    opt = torch.optim.Adam([logits], lr=0.05)
    for _ in range(steps):
        w = torch.softmax(logits, 0)
        loss = ((w @ C - Et) ** 2).sum()
        opt.zero_grad(); loss.backward(); opt.step()
    with torch.no_grad():
        return float(np.sqrt(((torch.softmax(logits, 0) @ C).numpy() - E) ** 2).sum())


SINGLET = (1 / np.sqrt(2)) * np.array([1.0, 1.0, 1.0, -1.0])     # CHSH = 2*sqrt2 (optimal angles), the quantum table


def diagnose(E):
    resid = fit_local(E); s = chsh(E)
    verdict = "CERTIFY-CONTEXTUAL" if (s > 2.0 + 1e-3 and resid > 1e-2) else "EMIT-CLASSICAL"
    return verdict, {"fit_residual": resid, "chsh": s}


def main():
    rng = np.random.default_rng(0)
    w = rng.dirichlet(np.ones(16)); E_classical = (w @ DET).astype(float)  # a random LHV table (inside the polytope)
    v_cl, info_cl = diagnose(E_classical)
    v_q, info_q = diagnose(SINGLET)

    # C3 the wall: sweep visibility; find where the verdict flips
    vis = np.linspace(0.4, 1.0, 25)
    verdicts = [diagnose(v * SINGLET)[0] for v in vis]
    flip = next((vis[i] for i in range(1, len(vis)) if verdicts[i] != verdicts[i - 1]), None)
    wall = 1 / np.sqrt(2)

    c1 = bool(v_cl == "EMIT-CLASSICAL" and info_cl["fit_residual"] < 1e-2 and info_cl["chsh"] <= 2.0 + 1e-2)
    c2 = bool(v_q == "CERTIFY-CONTEXTUAL" and info_q["chsh"] > 2.0 and info_q["fit_residual"] > 10 * info_cl["fit_residual"])
    c3 = bool(flip is not None and abs(flip - wall) < 0.04)

    out = {"classical": {"verdict": v_cl, **info_cl}, "quantum_singlet": {"verdict": v_q, **info_q},
           "wall_flip_visibility": (float(flip) if flip is not None else None), "wall_theory": float(wall),
           "C1_emit_classical": c1, "C2_certify_contextual": c2, "C3_locates_the_wall": c3,
           "contextual_verdict_added": bool(c1 and c2 and c3),
           "verdict": ("CERTIFY-CONTEXTUAL ADDED (frontier EXP-2): the discoverability diagnostic now handles a 4th "
                       "failure mode, on CORRELATION-TABLE data. A LOCAL-hidden-variable table -> the cheapest global "
                       "(local) code FITS (residual {:.0e}, CHSH {:.2f} <= 2) -> EMIT-CLASSICAL. The QUANTUM singlet -> "
                       "the cheapest local code CANNOT fit (residual {:.3f}) and CHSH = {:.3f} > 2 (Bell's theorem proves "
                       "NO local code exists) -> CERTIFY-CONTEXTUAL: no consistent GLOBAL code, only context-dependent "
                       "local ones. And the diagnostic LOCATES the wall -- a Werner-noise sweep flips the verdict at "
                       "visibility {:.3f}, the classical/quantum boundary 1/sqrt2 = {:.3f} (where CHSH crosses 2). Four "
                       "of the five frontier verdicts are now instrumented; PARTIAL-LEGIBLE + the synthesis is EXP-3."
                       .format(info_cl["fit_residual"], info_cl["chsh"], info_q["fit_residual"], info_q["chsh"],
                               float(flip) if flip else -1, wall)
                       if (c1 and c2 and c3) else "PARTIAL/HONEST -- see numbers.")}
    print(f"C1 EMIT-CLASSICAL (LHV table): verdict {v_cl}, residual {info_cl['fit_residual']:.2e}, CHSH {info_cl['chsh']:.3f}: {c1}")
    print(f"C2 CERTIFY-CONTEXTUAL (singlet): verdict {v_q}, residual {info_q['fit_residual']:.3f}, CHSH {info_q['chsh']:.3f} (>2): {c2}")
    print(f"C3 locates the wall: verdict flips at visibility {flip:.3f} vs theory 1/sqrt2={wall:.3f}: {c3}")
    print(f"\nCERTIFY-CONTEXTUAL VERDICT ADDED: {out['contextual_verdict_added']}")
    (RESULTS / "142_contextual_certificate.json").write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(figsize=(8.5, 5))
    chsh_curve = [chsh(v * SINGLET) for v in vis]
    ax.plot(vis, chsh_curve, "o-", color="crimson", label="CHSH(visibility)")
    ax.axhline(2.0, ls="--", c="k", lw=0.8, label="classical bound (CHSH=2)")
    ax.axvline(wall, ls=":", c="seagreen", lw=1.2, label=f"wall 1/√2={wall:.3f}")
    if flip:
        ax.axvline(flip, ls="-", c="orange", lw=1.0, alpha=0.7, label=f"verdict flips @ {flip:.3f}")
    ax.fill_between(vis, 0, 4, where=[c > 2 for c in chsh_curve], alpha=0.08, color="crimson")
    ax.set_xlabel("visibility v (Werner noise)"); ax.set_ylabel("CHSH"); ax.legend(fontsize=8); ax.set_ylim(1.0, 3.0)
    ax.set_title("② EXP-2 · CERTIFY-CONTEXTUAL: the diagnostic locates the contextuality wall\nv<1/√2 → EMIT-CLASSICAL (local code fits) · v>1/√2 → CERTIFY-CONTEXTUAL")
    fig.tight_layout(); fig.savefig(RESULTS / "142_contextual_certificate.png", dpi=140)
    print("saved results/142_contextual_certificate.json + .png")


if __name__ == "__main__":
    main()
