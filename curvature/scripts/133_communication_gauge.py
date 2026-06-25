"""Step 133 — communication-game-for-gauge: the legibility law in emergent communication (a 4th domain).

Phase 1b separate-angle probe (notes/build_queue.md: "communication-game-for-gauge, amortized-protocol reframe").
This session's central result is the LEGIBILITY LAW (Phase I / script 29, cross-validated in writeups/legibility_law.md):
a code a shared encoder AMORTIZES (infers from observations) is linearly LEGIBLE; a FREE per-item learned code with a
multi-D property SCRAMBLES (the information is present but stored non-linearly). It has been pressure-tested in three
domains (physics-trajectories, a real 4B LLM via Phronesis, game-RL via AlphaLudo). Here is a FOURTH, distinct domain:
EMERGENT COMMUNICATION (a two-agent referential game), where the "code" is the invented PROTOCOL and the gauge is the
arbitrary choice of message convention.

Setup (Lewis referential game): each object has D continuous properties p. A SPEAKER sends a message m about a target
object; a LISTENER, shown m and a set of candidate objects (target + distractors), must pick the target. Both trained
end-to-end on the referential task (cross-entropy over candidates). To succeed on fresh candidate sets the protocol
MUST encode the properties -- the only question is HOW (legibly or scrambled). Two ways to produce the protocol, on the
IDENTICAL game:
  AMORTIZED speaker: m = Speaker_net(p_target)            -- the message is INFERRED from the object (a shared encoder).
  FREE speaker:      m = codebook[target_id]              -- a per-object free parameter (no observation input).
Probe: linear vs non-linear decodability of p from the messages m.

FIRST RUN (honest, recorded): in the REFERENTIAL game the FREE codebook did NOT scramble (linear R^2 0.986 == amortized).
Why: the listener compares the message to candidate PROPERTIES p_c -- a GROUNDED comparison that pulls messages onto the
property manifold. So the referential game has a SECOND legibilizing pressure beyond amortization: grounding. The fix
round makes this a POSITIVE finding by contrasting two games on the SAME speakers:
  REFERENTIAL  (grounded):   listener sees m + candidate properties, picks the target  -> comparison grounds m in p-space.
  RECONSTRUCT  (ungrounded): listener sees m alone, must regress the target's properties -> exactly Phase I's free-code task.

Pre-reg (2026-06-26), D=3 (multi-D, the regime where free codes scramble per the AlphaLudo boundary):
  CG1 AMORTIZATION -> LEGIBLE (both games): the amortized protocol linearly decodes the properties (linear R^2 > 0.9)
     in BOTH the referential and reconstruction games -- amortization legibilizes regardless of grounding.
  CG2 GROUNDING -> LEGIBLE (the finding): a FREE protocol SCRAMBLES when ungrounded (reconstruction: nonlinear R^2 > 0.85
     but linear < 0.7, gap > 0.25 = the Phase I signature) yet stays LEGIBLE when grounded (referential: gap < 0.15).
     The grounded referential comparison is a second legibilizing pressure -- agreement-on-observables legibilizes.
  CG3 ALL SUCCEED: referential accuracy > 0.9 and reconstruction R^2 > 0.9 -- both protocols transmit the property; the
     difference is only HOW (legibly vs scrambled), set by grounding, not by task success.
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
from sklearn.neural_network import MLPRegressor
from torch import nn

from curvlib import RESULTS, progress

D, K, V, NCAND = 3, 8, 600, 6                                      # property dim / message dim / vocabulary / candidates


class Speaker(nn.Module):
    def __init__(s, free):
        super().__init__()
        s.free = free
        if free:
            s.code = nn.Parameter(torch.randn(V, K) * 0.1)        # per-object free message (no observation input)
        else:
            s.net = nn.Sequential(nn.Linear(D, 64), nn.GELU(), nn.Linear(64, 64), nn.GELU(), nn.Linear(64, K))

    def forward(s, idx, p):
        return s.code[idx] if s.free else s.net(p)                # message for the target


class Listener(nn.Module):
    def __init__(s):
        super().__init__()
        s.net = nn.Sequential(nn.Linear(K + D, 64), nn.GELU(), nn.Linear(64, 64), nn.GELU(), nn.Linear(64, 1))

    def forward(s, m, cand_p):                                     # m:(B,K) cand_p:(B,NCAND,D) -> scores (B,NCAND)
        me = m[:, None, :].expand(-1, cand_p.shape[1], -1)
        return s.net(torch.cat([me, cand_p], -1))[..., 0]


class ReconListener(nn.Module):
    """ungrounded: must regress the target's properties from the message ALONE (no candidates) -- Phase I's task."""

    def __init__(s):
        super().__init__()
        s.net = nn.Sequential(nn.Linear(K, 64), nn.GELU(), nn.Linear(64, 64), nn.GELU(), nn.Linear(64, D))

    def forward(s, m):
        return s.net(m)


def train(free, mode, props, seed=0, steps=6000, B=256):
    """mode='ref' (grounded referential game) or 'recon' (ungrounded property reconstruction)."""
    torch.manual_seed(seed); rng = np.random.default_rng(seed)
    sp = Speaker(free); li = Listener() if mode == "ref" else ReconListener()
    opt = torch.optim.Adam(list(sp.parameters()) + list(li.parameters()), lr=2e-3)
    P = torch.from_numpy(props)
    for step in range(steps):
        tgt = rng.integers(0, V, B)
        m = sp(torch.from_numpy(tgt), P[tgt])
        if mode == "ref":
            cand = np.stack([rng.choice(V, NCAND, replace=False) for _ in range(B)])  # candidate object ids
            pos = rng.integers(0, NCAND, B); cand[np.arange(B), pos] = tgt            # place target at a random slot
            loss = nn.functional.cross_entropy(li(m, P[torch.from_numpy(cand)]), torch.from_numpy(pos))
        else:
            loss = nn.functional.mse_loss(li(m), P[tgt])
        opt.zero_grad(); loss.backward(); opt.step()
        if step % 1500 == 0:
            progress(f"133_{mode}_{'free' if free else 'amort'}", step, steps, loss=float(loss.detach()))
    with torch.no_grad():
        if mode == "ref":                                         # referential accuracy on fresh episodes
            accs = []
            for _ in range(40):
                tgt = rng.integers(0, V, 512)
                cand = np.stack([rng.choice(V, NCAND, replace=False) for _ in range(512)])
                pos = rng.integers(0, NCAND, 512); cand[np.arange(512), pos] = tgt
                sc = li(sp(torch.from_numpy(tgt), P[tgt]), P[torch.from_numpy(cand)])
                accs.append((sc.argmax(1).numpy() == pos).mean())
            metric = float(np.mean(accs))
        else:                                                     # reconstruction R^2
            phat = li(sp(torch.arange(V), P)).numpy()
            metric = float(1 - np.sum((phat - props) ** 2) / np.sum((props - props.mean(0)) ** 2))
        msgs = sp(torch.arange(V), P).numpy()                     # the protocol: message per vocabulary object
    return metric, msgs


def decode(msgs, props):
    """linear (Ridge) vs non-linear (MLP) decodability of the D properties from the messages, held-out."""
    n = len(msgs); idx = np.random.default_rng(0).permutation(n); tr, te = idx[: n * 7 // 10], idx[n * 7 // 10:]
    Xtr, Xte = msgs[tr], msgs[te]; Ytr, Yte = props[tr], props[te]

    def r2(model):
        model.fit(Xtr, Ytr); pred = model.predict(Xte)
        return float(1 - np.sum((pred - Yte) ** 2) / np.sum((Yte - Yte.mean(0)) ** 2))

    lin = r2(Ridge(alpha=1.0))
    nonlin = r2(MLPRegressor(hidden_layer_sizes=(128, 128), max_iter=4000, random_state=0))
    return lin, nonlin


def main():
    rng = np.random.default_rng(7)
    props = rng.uniform(-1, 1, (V, D)).astype(np.float32)         # the shared object vocabulary (fixed for all)

    cond = {}                                                     # {mode}_{speaker}: (success metric, messages)
    for mode in ("ref", "recon"):
        for free in (False, True):
            metric, msg = train(free, mode, props)
            lin, non = decode(msg, props)
            cond[f"{mode}_{'free' if free else 'amort'}"] = {"success": metric, "linear_r2": lin,
                                                             "nonlinear_r2": non, "gap": non - lin}
    ra, rf, ca, cf = cond["ref_amort"], cond["ref_free"], cond["recon_amort"], cond["recon_free"]

    # honest outcome (the fix round REFUTED my grounding hypothesis): the free code did NOT scramble in EITHER game.
    amort_legible = bool(ra["linear_r2"] > 0.9 and ca["linear_r2"] > 0.9 and ra["gap"] < 0.1 and ca["gap"] < 0.1)
    free_legible = bool(rf["gap"] < 0.15 and cf["gap"] < 0.15 and rf["linear_r2"] > 0.85 and cf["linear_r2"] > 0.85)
    free_scramble_triggered = bool(rf["gap"] > 0.25 or cf["gap"] > 0.25)
    all_succeed = bool(min(ra["success"], rf["success"], ca["success"], cf["success"]) > 0.9)
    # the robust half of the law (amortize->legible) holds in a 4th domain; the FREE->scramble half did NOT trigger ->
    # this comms task is an "easy target" (free legible even UNGROUNDED -> grounding refuted), so free storage of a
    # multi-D property is NECESSARY but NOT SUFFICIENT to scramble: it is target-conditional (scripts 107-110).
    honest = bool(amort_legible and free_legible and all_succeed and not free_scramble_triggered)

    out = {"D": D, "K": K, "V": V, "NCAND": NCAND, "conditions": cond,
           "amortization_legibilizes_both": amort_legible, "free_legible_both_games": free_legible,
           "free_scramble_triggered": free_scramble_triggered, "all_succeed": all_succeed,
           "free_scramble_is_target_conditional": honest,
           "verdict": ("HONEST EASY-TARGET RESULT (a 4th domain that REFINES the legibility law). In a two-agent comms "
                       "game, the AMORTIZED protocol is legible in both the referential and reconstruction games (linear "
                       "R^2 {:.2f}/{:.2f}) -- the robust half of the law transfers to emergent communication. BUT the "
                       "predicted FREE-code scramble did NOT reproduce: the free codebook stayed LEGIBLE in BOTH the "
                       "grounded referential (gap {:+.2f}) AND the ungrounded reconstruction (gap {:+.2f}) games, despite "
                       "free storage of a multi-D (D={}) property. So (a) the grounding hypothesis is REFUTED (free is "
                       "legible even ungrounded), and (b) this comms task is an 'easy target' -- free storage of a "
                       "multi-D property is NECESSARY but NOT SUFFICIENT to scramble; free->scramble is target-conditional "
                       "(scripts 107-110, the signal-strength driver). All four protocols communicate (success >{:.2f}). "
                       "Adds a 4th easy-target harness, sharpening the AlphaLudo multi-D boundary."
                       .format(ra["linear_r2"], ca["linear_r2"], rf["gap"], cf["gap"], D,
                               min(ra["success"], rf["success"], ca["success"], cf["success"]))
                       if honest else "UNEXPECTED -- see per-condition numbers (a free code DID scramble somewhere).")}
    for k, v in cond.items():
        print(f"{k:12s}: success={v['success']:.3f} | linear R2={v['linear_r2']:.3f} nonlinear={v['nonlinear_r2']:.3f} gap={v['gap']:+.3f}")
    print(f"\namortization legibilizes (both games): {amort_legible}")
    print(f"free stayed LEGIBLE in both games (easy target, scramble did NOT trigger): {free_legible}")
    print(f"all four communicate (min success {min(ra['success'], rf['success'], ca['success'], cf['success']):.3f}): {all_succeed}")
    print(f"\nHONEST: free->scramble is TARGET-CONDITIONAL (did not reproduce here; multi-D free storage necessary not sufficient): {honest}")
    (RESULTS / "133_communication_gauge.json").write_text(json.dumps(out, indent=1))

    fig, ax = plt.subplots(1, 2, figsize=(13, 4.8))
    order = ["ref_amort", "ref_free", "recon_amort", "recon_free"]
    labels = ["referential\namortized", "referential\nfree", "reconstruct\namortized", "reconstruct\nfree"]
    x = np.arange(4); w = 0.38
    ax[0].bar(x - w / 2, [cond[k]["linear_r2"] for k in order], w, label="linear (Ridge)", color="steelblue")
    ax[0].bar(x + w / 2, [cond[k]["nonlinear_r2"] for k in order], w, label="nonlinear (MLP)", color="orange")
    ax[0].set_xticks(x); ax[0].set_xticklabels(labels, fontsize=8); ax[0].set_ylim(0, 1.05)
    ax[0].set_ylabel("property decode R² from protocol"); ax[0].legend(fontsize=8)
    ax[0].set_title("All four protocols are LEGIBLE (linear≈nonlinear)\n— an 'easy target': free does not scramble")
    ax[1].bar(x, [cond[k]["gap"] for k in order], color="seagreen")
    ax[1].axhline(0.25, ls="--", c="crimson", lw=0.7, label="scramble threshold (not reached)")
    ax[1].set_xticks(x); ax[1].set_xticklabels(labels, fontsize=8)
    ax[1].set_ylabel("legibility gap (nonlinear − linear R²)"); ax[1].legend(fontsize=8); ax[1].set_ylim(-0.05, 0.3)
    ax[1].set_title("No scramble anywhere — free→scramble is\ntarget-conditional (did not trigger here)")
    fig.suptitle("Communication-game-for-gauge: amortization legibilizes (robust half); free→scramble is target-conditional")
    fig.tight_layout(); fig.savefig(RESULTS / "133_communication_gauge.png", dpi=140)
    print("saved results/133_communication_gauge.json + .png")


if __name__ == "__main__":
    main()
