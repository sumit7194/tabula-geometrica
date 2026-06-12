# Curvature discovery — can a network invent spacetime geometry?

*The project arc: train networks only on "adjacent" observable tasks — never show
them a metric, an interval, or Einstein's equations — and test whether geometry
emerges as the cheapest internal explanation. Phase A (flat spacetime, this folder):
rediscover the Minkowski interval, replicating Wetzel et al. (PRR 2, 033499, 2020)
with our own verification gates. Phase B (planned): a weak gravity well — does the
learned invariant become position-dependent, i.e. does the flat interval "bend"?*

**Status: ✅ Phase A · ✅ v0.1 (causal sectors) · ✅ Phase B (gravity well) ·
✅ Phase C (the geometry-vs-force economy race) — complete.** Headlines: the net
invented the Minkowski interval (A); discovered the light cone as the
discontinuities of its latent (v0.1); traced a gravity well it was never told
about to r = 0.9995 (B, `results/05_gates_well_k1.png`); and in the economy race
(C, `results/07_economy_charged.png`) an identity-blind geometry model ties the
per-body force model *exactly* while only gravity acts, then **fails 88× on
precisely the charged bodies** when a non-universal force enters — whose
embeddings turn out to encode exactly one number each, q/m (behavioral decode
r = 0.9999). **Gravity costs 0 numbers per body; EM costs exactly 1 — why
geometry absorbs gravity and not electromagnetism, replayed in a trainable
system.** Full numbers + honest probe-ladder corrections in
`notes/lab_notebook.md`.

---

## The experiment in plain words

Two observers fly past each other at constant speeds and each writes down the
coordinates `(t, x)` of the same flash of light's arrival — their numbers differ
because their frames differ. A tiny twin network gets one observation per twin and
must answer one question: **"could these be the same event?"** It is never told
physics. The only way to win is to compute, inside itself, something all observers
agree on — and in special relativity there is exactly one such thing: the interval
`s² = t² − x²`. If the net wins, it had to have *invented* that quantity. The gates
below check that it really did, and that it didn't cheat.

## Decisions (the ADR section — what we chose and why)

| Decision | Choice | Why (plain words) |
|---|---|---|
| Where the symmetry lives | **In the data only** (boosted pairs); architecture is symmetry-agnostic | If we used Lorentz-equivariant layers the answer would be wired in — nothing discovered. Inputs are raw `(t,x)`; the minus sign must be earned. |
| Head | **Strict**: `logit = α − softplus(β)·‖z_a − z_b‖` | Forces the *encoder itself* to output frame-agreeing values — the invariant lives in `z`, where we can probe it. A flexible MLP head could hide the invariant inside the head. |
| Loss | **BCE on the distance** (not InfoNCE) | Explicit pairs let us *control* exactly how hard the negatives are (the science depends on that); in-batch contrastive losses give up that control for throughput we don't need. |
| Bottleneck width K | **Sweep K = 1, 2, 4 as separate runs** | K is the experiment, not a hyperparameter: the width where accuracy saturates *counts the world's invariants*. Separate runs answer "what does the task need"; probing one wide run only answers "what did this net happen to use" — we got both anyway, see results. |
| Noise | **On from day one** (1% per coordinate) | Real measurements are noisy; exact-match shortcuts die; the net must learn the smooth concept, not memorize numbers. Negatives closer than the noise floor are excluded (they'd be label noise). |
| Activations | **tanh, not ReLU** | The gates differentiate the *trained network* (gradients of `z`). ReLU's derivatives are piecewise-flat junk for that purpose; tanh is smooth. |
| Region | **Future-timelike events only** (`t > |x|`) | This region is closed under boosts and has *exactly one* invariant — making "K=1 suffices" a sharp, falsifiable prediction. Mixed regions add a discrete branch label; that's the planned v0.1 extension. |
| Probes | **Reshaping-proof gates only** (below) | The net is only pinned down up to a monotone reshaping `h(s²)`; naive comparisons to `t²−x²` would under- or over-credit it. |

## The gates (and why each is shaped that way)

- **G0 honesty (before training):** an oracle comparing true intervals must solve the
  task (≈1) while a linear model on raw coordinates and a single-observation probe
  must sit at chance (≈0.5). If G0 fails, high accuracy means nothing — the
  experiment would be lying to us. *(Passed: 0.99 / 0.52 / 0.49.)*
- **G1 monotone dependence:** isotonic fit of `z` against `s²`, R² > 0.95. Tests "is
  the latent a function of the interval and nothing else" without penalizing the
  allowed reshaping. *(Passed: R² = 1.0000.)*
- **G2 gradient alignment + the minus sign:** the direction of steepest change of
  `z` must match physics' `∇s² = (2t, −2x)` everywhere — opposite signs on the time
  and space components *is* the Lorentzian signature, read out of the weights.
  Chosen over Hessian eigensigns because a monotone reshaping can bend curvature
  but can never rotate gradients. *(Passed: |cos| = 1.0000, consistency 1.0000.)*
- **G3 Euclidean control:** same alignment against `∇(t²+x²)` must be poor — refutes
  "it just learned distance from the origin." *(Passed: 0.43 vs 1.00.)*
- **G4 level sets:** contours of `z` vs true hyperbolas. The single most readable
  artifact: hyperbolas = spacetime, circles = junk. *(Passed — see
  `results/03_gates_k1.png`.)*
- **Counting:** accuracy vs K saturates at K=1 (99.91%), and nets *given* K=2/4
  leave the extra dimensions empty (PCA explained variance `[1, 0, 0, 0]`) — the
  world's invariant count, discovered twice over.

## Setup & verify

```
python3.12 -m venv .venv
./.venv/bin/pip install -r requirements.txt   # torch 2.12, numpy, sklearn, matplotlib, scipy
./verify.sh                                    # re-runs every probe vs saved models; must print ALL GREEN
```

Add `--device mps` to the longer training scripts on an Apple-silicon Mac.

## Layout

```
scripts/curvlib.py     physics + generator + model + ckpt/progress helpers (shared)
scripts/01_sanity.py   G0 honesty checks — run before any training
scripts/02_train.py    train at a given --k (4000 steps, ~40 s CPU)
scripts/03_gates.py    G1–G4 for a trained k
requirements.txt       pinned dependency versions
results/               models, gate JSONs, plots (heartbeats in results/progress/)
notes/lab_notebook.md  decisions, results, gotchas (the changelog)
```

## Phase B (built — design notes)

Weak static well `ds² = A(x)dt² − B(x)dx²` (`A = 1+2φ`, `B = 1−2φ`, Gaussian φ;
standard weak-field form, verified). Observers at a shared anchor report
**coordinate** components of displacements — the deliberate design choice that
makes geometry visible: orthonormal-frame components would be Minkowski
everywhere (that's the equivalence principle, and the reason "curvature is
invisible locally" is physics, not a bug). Both pair members share the anchor, so
position is context, never a label cue. The reshaping-proof readout: per-position
monotone freedom `h_x` cancels in the gradient ratio
`−(∂f/∂Δt / ∂f/∂Δx)·(Δx/Δt) = A(x)/B(x)` — what we plot was *forced* to be
geometry. Scripts: `02_train.py --task well|well-nopos`, `05_gates_well.py`.

## Phase C (built — design notes)

Trajectories of many bodies in the well (slow-motion regime — the historically
ambiguous one; generator = exact Newtonian gravity, validated as the limit of
the Phase B geodesics by a scaling probe). Two rivals, identical data and
budget: **geometry** = MLP(x₀, v₀) with body identity architecturally impossible
to use; **force** = MLP(x₀, v₀, embedding[body]). Mixes: `neutral` (gravity
only) and `charged` (half the bodies feel an off-center E-field ∝ q/m).
Readouts: the **swap test** (permute embeddings — harmless under gravity,
catastrophic with charge), zero-shot on unseen bodies, and the **probe ladder**
on the embeddings: PCA ✗ → linear decode ✗ → behavioral decode (invert the
net's own trajectories) ✓ r = 0.9999 against true q/m. Scripts:
`06_train_dynamics.py --mix neutral|charged`, `07_gates_economy.py`.

## Next

3+1 flat replication; the depth-wise SAE side quest (how is the invariant
assembled layer by layer — and is non-linear embedding storage like Phase C's
q/m an SAE-recoverable feature?); formal MDL version of the economy race;
writing the four phases up as a single coherent note.
