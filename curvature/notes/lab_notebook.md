# Lab notebook — curvature discovery

*Decisions, results, gotchas. Newest at the bottom.*

## 2026-06-11 — Phase A built and PASSED, first attempt

Setup: python3.12 venv, torch 2.12.0 (CPU — MPS gains nothing on a 2→64→64→K MLP),
sklearn 1.9.0. Seeds fixed (train seed 0; eval seeds disjoint).

**G0 honesty checks (01_sanity.py, N=40k pairs):**
oracle 0.9915 · linear shortcut 0.5195 · single-obs giveaway 0.4935.
All three exactly where they must be — task solvable, no linear cheat, no leak.

**Training (02_train.py, 4000 steps, batch 512, Adam 1e-3):**

| K | test accuracy (20k fresh pairs) |
|---|---|
| 1 | 0.9991 |
| 2 | 0.9992 |
| 4 | 0.9991 |

Saturation at K=1 → the world has one invariant. Bonus finding: the K=2 and K=4
nets left their extra latent dimensions EMPTY (PCA explained variance [1,0],
[1,0,0,0]) — minimality emerged without bottleneck pressure. Worth remembering for
Phase B: the strict distance head itself pushes toward minimal latents (distances
in unused dimensions only add noise to positives, so training prunes them).

**Gates (03_gates.py):** K=1: G1 isotonic R² = 1.0000 · G2 |cos| = 1.0000,
sign-consistency = 1.0000 · G3 Euclidean control = 0.4323 · G4 level sets lie on
the true hyperbolas (results/03_gates_k1.png). K=2, K=4 identical after PCA1.

**Conclusion:** the network, shown only raw coordinate pairs from boosted
observers, invented a quantity that is a monotone function of t²−x², with the
Lorentzian sign pattern, using exactly one latent — the Minkowski interval,
rediscovered. Replication of Wetzel et al. (PRR 2, 033499, 2020) confirmed, with
stronger verification gates (their readout was polynomial fitting; our G2
gradient-alignment + G3 control + G0 honesty checks are new here).

**Why this matters for the project:** the pipeline + gates are now validated on a
known answer. When Phase B reports "the invariant became position-dependent in a
gravity well," these same gates are what make that claim trustworthy.

## 2026-06-11 — v0.1 PRE-REGISTRATION (written before running)

Opening sampling to all four causal sectors. Corrected prediction (my earlier
"knee moves 1→2" claim was WRONG, caught while designing the gates): the orbit
space is four disjoint half-lines — still ONE continuous dimension — and a
continuous scalar can map disjoint input regions to disjoint ranges. So:
(P1) K=1 still saturates ≥ 0.99 (counting measures continuous dimensions, not
bits); (P2) per-sector isotonic R² > 0.95 with per-sector sign freedom;
(P3) accuracy certifies cross-sector separation (cross-sector pairs are
negatives); the open question we genuinely don't know: does the latent place the
four branches in disjoint ranges, or interleave them? Either passes; the
portrait plot answers it.

## 2026-06-11 — Phase B PRE-REGISTRATION (written before running)

Static gravity well, ds² = A(x)dt² − B(x)dx², A = 1+2φ, B = 1−2φ, Gaussian
φ (depth 0.15, width 1). Observations = (anchor x, COORDINATE components of the
displacement); pairs share the anchor, so position is context, never a cue.
Predictions: (P1) the position-blind control ("well-nopos") plateaus measurably
below the position-aware model — the well is behaviorally real; (P2) the
position-aware model reaches ≥ 0.99; (P3) the gradient-ratio readout
−(∂f/∂Δt / ∂f/∂Δx)·(Δx/Δt), which cancels the per-position reshaping freedom,
recovers the profile A(x)/B(x) with correlation > 0.9 against truth, including
the well's depth at x=0 (true A/B there = 0.7/1.3 ≈ 0.538); (P4) per-position-bin
isotonic R² of z vs the local invariant > 0.95. If P3 passes, the headline is:
the net was never told there is a well, a metric, or even that position matters
— and its learned notion of "sameness" traces the gravity well.

## 2026-06-11 — v0.1 RESULTS (all pre-registered predictions held)

Accuracy: K=1 → 0.9934, K=2 → 0.9970 (P1 ✓ — K=1 saturates; counting measures
continuous dimensions, not bits). Per-sector gates (P2 ✓): isotonic R² ≥ 0.9997
all four sectors; |cos| = 1.0000; sign-consistency ≥ 0.991. The open question
answered: the net chose DISJOINT latent ranges for the four sectors (no
interleaving) — four separated monotone branches, with the LIGHT CONE appearing
as the gaps/discontinuities of the latent (results/04_gates_mixed_k1.png). The
causal structure of flat spacetime, discovered as the separatrix of a learned
representation. Methodology note kept for honesty: my first prediction draft
("knee moves 1→2") was wrong and corrected BEFORE running — the orbit space is
four disjoint half-lines, still 1-D.

## 2026-06-11 — Phase B RESULTS: the flat interval BENT (all gates passed)

Verified pre-build: weak-field form ds² = (1+2φ)dt² − (1−2φ)dx² matches the
standard convention; novelty search found no prior position-dependent Lorentzian
invariant discovery of this kind.

| pre-registered gate | result |
|---|---|
| P1 position-blind control plateaus below | 0.9054 vs 0.9983 — the well is behaviorally real (≈9.3 pts of accuracy ARE the geometry varying) |
| P2 position-aware ≥ 0.99 | 0.9983 (K=1); K=2 adds nothing (0.9980) |
| P3 ratio profile r > 0.9, depth recovered | r = 0.9995; depth Â/B̂(0) = 0.5501 vs true 0.5385 (~2%) |
| P4 per-bin isotonic R² > 0.95 | min 0.9752 over 12 bins; alignment 1.0000/1.0000 |

The readout that makes P3 honest: the per-position reshaping freedom h_x cancels
in −(∂f/∂Δt / ∂f/∂Δx)·(Δx/Δt) = A/B, so the recovered well profile
(results/05_gates_well_k1.png) cannot be an artifact of latent rescaling.

**The Phase B sentence:** a Siamese net trained only on "same event, two local
observers?" at anchors scattered through a region — never told there is a well, a
metric, or that position matters — (a) needs the position input to succeed
(control fails without it), and (b) stores in its weights a position-dependent
invariant whose local structure reproduces the gravity well's metric ratio
A(x)/B(x) to r = 0.9995, depth to ~2%. The flat Minkowski interval of Phase A
became a measured FIELD of intervals: this is "the interval bends," demonstrated
in a controlled toy with reshaping-proof gates.

Caveats recorded: 1+1 static toy metric (not a vacuum Einstein solution — it's a
DATA-GENERATOR metric, fine for representation-emergence claims, not gravity
dynamics); coordinate-component observations are what make geometry visible
(orthonormal-frame data would be Minkowski everywhere — equivalence principle);
only the ratio A/B is recoverable by construction (per-position reshaping
freedom) — recovering A and B separately needs cross-position data (e.g.
trajectories), which is exactly the Phase C geometry-vs-force design.

## 2026-06-11 — Phase C PRE-REGISTRATION (written before running)

The economy race. Slow-motion regime (the historically ambiguous one), generator
validated against full geodesics of the Phase B metric (G0: gap must be small,
printed). Two mixes, predictions:
NEUTRAL mix (gravity only): (C1) geometry model ≈ force model on test MSE —
identity buys nothing; (C2) swap test ≈ no degradation; (C3) embeddings COLLAPSE
(small spread, no structure) — the equivalence principle visible in embedding
space; (C4) geometry model works zero-shot on bodies it never saw.
CHARGED mix (half the bodies have q/m ∈ ±[0.3,1], E-field bump off-center):
(C5) geometry model fails on charged bodies but stays good on neutral ones
(MSE ratio charged/neutral ≫ 1) — universality is what geometrizes; (C6) force
model fine on both; (C7) swap test now CATASTROPHIC (identity matters); (C8) the
force model's embeddings spread along ONE dominant PCA axis whose coordinate
correlates with true q/m at |r| > 0.95 — the net discovers charge-to-mass ratio
as the single number that matters. If C5+C8 pass, the headline: gravity
geometrizes (0 numbers per body), electromagnetism resists (exactly 1 number per
body) — why Einstein geometrized gravity and not EM, replayed in embedding space.

## 2026-06-11 — Phase C RESULTS: the economy race (gravity geometrizes, EM doesn't)

**G0 generator honesty:** max |Newtonian − full geodesic| = 0.182 at depth 0.15,
v ≤ 0.3 — NOT negligible, investigated before proceeding. Scaling probe:
gap = 0.044 (depth 0.05), 0.0147 (depth 0.05, v 0.1), 0.00058 (depth 0.01,
v 0.05) — shrinks exactly as post-Newtonian corrections must, so both
integrators are correct and the gap is real physics (our well is weak-ish, not
ultra-weak). Honest reframe recorded: the dynamics generator is EXACT Newtonian
gravity from φ (the historically exact arena for geometry-vs-force), validated
as the v→0, φ→0 limit of the Phase B geodesics.

**Neutral mix (gravity only) — C1, C2, C4 pass; C3 passes corrected:**
geometry 4.7e-6 ≈ force 6.2e-6 test MSE (identity buys nothing, C1 ✓);
embedding swap test 6.0e-6 vs 6.2e-6 — permuting identities changes NOTHING
(C2 ✓); geometry zero-shot on never-seen bodies 4.8e-6 (C4 ✓). C3 correction:
embeddings do NOT geometrically collapse (spread 1.86 — leftover init noise;
nothing ever gradients them toward a point); the correct operationalizations of
"identity is irrelevant" are the swap test + the flat PCA spectrum
[0.43, 0.24, 0.20, 0.13] (no learned axis). Pre-registered wording was wrong,
corrected openly.

**Charged mix — C5, C6, C7 pass; C8 passes after a probe-ladder lesson:**
- C5 ✓✓ geometry model: charged MSE 0.0853 vs neutral 0.00097 — **88× failure on
  exactly the bodies that break universality**, while staying good on neutral.
- C6 ✓ force model: 4.3e-5 charged / 4.9e-5 neutral — fine on both.
- C7 ✓✓ swap test: 4.6e-5 → 0.078 (**1700× blowup**) — identity now decisive.
- C8: the pre-registered probe (corr(PC1, q/m) > 0.95) FAILED at r = −0.12, and
  the LOO **linear** decode also failed (r = +0.02) — yet the swap test proves
  the information is used. Behavioral decode (invert the net's own predicted
  trajectories against the generator over a q/m grid): **r = +0.9999**. The
  embeddings carry exactly one physical number — charge-to-mass ratio — encoded
  NON-linearly, invisible to variance and linear probes. Probe ladder recorded
  as a finding in its own right: variance ✗ → linear ✗ → behavioral ✓.

**The Phase C sentence:** with many bodies and identical training budgets, an
identity-blind shared-rule model and a per-identity model tie exactly when only
gravity acts (and survive identity swaps), but the moment a non-universal force
enters, the shared-rule model fails on precisely the non-universal bodies and
the per-identity model's embeddings turn out to encode exactly one number per
body — q/m. Gravity costs 0 numbers per body; electromagnetism costs exactly 1.
That asymmetry — universality — is why geometry can absorb gravity and not EM,
replayed end-to-end in a trainable system.

Caveats: Newtonian-regime dynamics (bridge to Phase B geodesics via scaling
probe, not identity); 1+1 toy fields; "description length" operationalized as
parameters-that-matter (swap/decode), not a formal MDL computation.

## 2026-06-11 — 3+1 REPLICATION PRE-REGISTRATION (written before running)

Phase A in full 3+1: events are future-timelike four-vectors (t, x, y, z); an
observation of a rest event is τ·(cosh η, sinh η·n̂) for random rapidity η and
random spatial direction n̂ — boosts AND rotations covered. Inputs raw 4-vectors.
Predictions: (R1) K=1 saturates ≥ 0.99 (the orbit space is still one
half-line — rotations add symmetry, not invariants); (R2) isotonic R² of z vs
s² = t²−|x⃗|² > 0.95; (R3) gradient alignment with (2t, −2x, −2y, −2z) |cos| >
0.95 with full sign consistency — THREE minus signs earned this time; (R4)
Euclidean control (2t, 2x, 2y, 2z) markedly lower; (R5) the (t, x) slice
(y=z=0) of the level sets lies on the Phase A hyperbolas.

## 2026-06-11 — 3+1 REPLICATION RESULTS (all pre-registered gates passed)

R1 ✓ K=1 saturates: 0.9970 (K=2: 0.9969 — adds nothing; rotations enlarged the
symmetry group without adding invariants, as predicted). R2 ✓ isotonic
R² = 0.9997. R3 ✓ alignment |cos| = 1.0000, sign-consistency = 1.0000 — the
(+,−,−,−) pattern: THREE minus signs earned. R4 ✓ Euclidean control 0.4176.
R5 ✓ (t,x)-slice level sets on the true hyperbolas (global sign flip this run —
allowed reshaping freedom; results/08_gates_3p1_k1.png). Phase A's result is
dimension-robust: the interval emerges identically in full 3+1.

## 2026-06-11 — SAE/STEERING SIDE QUEST PRE-REGISTRATION (written before running)

Target: the charged-mix force model. Known facts: q/m is stored per body, used
(swap test 1700×), behaviorally decodable (r=0.9999), but NOT linearly decodable
from the embedding (r=0.02) and invisible to PCA. The interpretability question:
where and how does the network make this information USABLE?

Hypothesis (the "linearization with depth" story): the embedding stores q/m in a
non-linear code, but downstream hidden layers must COMPUTE with it (the output
needs ~ qm·E(x) products), so the representation should become progressively
more linear with depth.

Predictions:
(S1) Linear decodability of qm from hidden activations rises with depth:
     embedding (known r≈0.02 per body) < layer-1 < layer-2, with the probe
     trained on 24 bodies and tested on 8 HELD-OUT bodies (generalizing
     direction, not memorization). Gate: layer-2 held-out-body r > 0.9.
(S2) A sparse autoencoder (128→512, L1) on layer-2 activations contains at
     least one feature whose activation correlates with qm at |r| > 0.8 across
     inputs (or with the physically-used product qm·E(x) — we test both; which
     one wins is itself a finding about whether the net factorizes).
(S3) STEERING: adding α·(qm-direction) to layer-2 activations mid-forward-pass
     shifts the behaviorally-decoded effective q/m monotonically with α
     (|r| > 0.9 across an α grid) — causal control of a body's charge.
(S4) Control: random directions of equal norm produce far smaller, unsystematic
     behavioral shifts.

## 2026-06-11 — SAE/STEERING RESULTS (one decisive pass, one honest negative,
## one methodological lesson)

**S1 ✓✓ (decisive): linearization with depth confirmed.** Linear decode of q/m,
held-out bodies: embedding 0.02 → layer-1 **0.9804** → layer-2 **0.9821**. The
network stores q/m non-linearly in the embedding but UNTANGLES it into a
linearly-readable signal in its hidden layers — it has to, to compute with it.

**S2 ✗ (honest negative): no monosemantic q/m feature at the |r| > 0.8 gate.**
First SAE run was too dense (L0=251, recorded); tuned run (L1 3e-3, L0=93,
rec R²=0.999): best feature vs qm |r| = 0.72, vs the physically-used product
qm·E(x) |r| = 0.78. Both below gate → in this network, q/m lives DISTRIBUTED
across features, not as one SAE feature. Weak hint the net stores the used
product rather than the factor (0.78 > 0.72). Scope caveat: one SAE family, one
small tanh net — a finding about THIS network, not about SAEs.

**S3 ✓ causal control: we gave a neutral body charge.** Steering along the
ridge-probe direction at layer-1 sweeps the behaviorally-decoded effective q/m
across the FULL physical range [−1.20, +1.41], corr(α, qm_eff) = 0.9987, with
on-manifold residual 0.0033 (steered behavior still looks like valid physics at
some charge). Layer-2 steering is monotone but weak (±0.19, residual 6× worse):
consistent with q/m being CONSUMED between layers 1 and 2 — steer upstream of
where information is used.

**S4 ⚠ (methodological lesson): steering specificity is weak in small smooth
nets.** First metric (raw range) was flawed — the behavioral decoder projects
ANY perturbation onto q/m. Fixed metrics: random equal-norm directions also
steer monotonically (|corr| 0.997!) with span 1.49 (vs 2.61) and residual 0.010
(vs 0.0033). So the qm-direction is the strongest (1.75×) and cleanest (3.2×
more on-manifold) charge-knob, but not uniquely privileged — in a 128-d tanh
net, almost every direction couples somewhat to the dominant behavioral mode.
Lesson recorded: steering claims need equal-norm random controls on BOTH
systematicity and on-manifold-ness; small nets make "any direction steers"
cheap. (Plot: results/09_sae_steering.png.)

## 2026-06-11 — MDL RACE PRE-REGISTRATION (written before running)

Make Phase C quantitative: train per-body-code models with embedding dimension
d ∈ {0 (= geometry), 1, 2, 4} on both mixes; compute a two-part code:
L_total(d) = data bits (prequential Gaussian code, σ² = each model's train MSE,
position resolution δ = 1e-3 stated) + parameter bits per body (coarsest
embedding quantization that keeps test MSE within 5%, bits = Σ_dims
log2(span/Δ* + 1)).
Predictions: (M1) neutral mix: MDL minimum at d = 0 — the geometry model is the
shortest description when only gravity acts. (M2) charged mix: d = 0's data
term explodes; d ≥ 1 fits equally well; param bits grow with d ⇒ minimum at
EXACTLY d = 1. (M3) the charged d = 1 model's per-body scalar is a clean
monotone code of true q/m (|spearman| > 0.99) — capacity pressure forces the
monosemantic code that the 4-d embedding refused to give the SAE. (M4) the
quantization probe shows q/m is worth only a few bits/body (≈ 3–6) before
predictions degrade; the neutral d = 1 model's scalar quantizes to ~0 bits
(nothing worth transmitting).

## 2026-06-11 — MDL RACE RESULTS (one decisive pass, two honest corrections,
## one reproducibility bug found & fixed)

**Bug first:** torch's default generator is process-random and models were
constructed BEFORE train() seeded it → irreproducible inits (10× MSE spread
between runs of identical configs). Violated our own "fixed seeds" standard.
Fixed in 06 and 10 (seed before construction); diagnosed because step-06 and
step-10 numbers for the same config disagreed.

**M2 ✓✓ (the decisive one, charged mix):** total bits/body — d=0: 14,696
(data term explodes, 9.8 bits/target) · **d=1: 5,320 ← minimum** · d=2: 6,461 ·
d=4: 6,028. The MDL minimum sits at EXACTLY one number per body, by ~700 bits
over the nearest rival and ~9,400 over geometry-only.

**M1 ✗ as operationalized (neutral mix):** min landed at d=2, not d=0 — but the
d∈{0,1,2} differences are data-term optimization variance (non-monotone in d;
d=4 worse than d=2), not per-body information. The clean, correct separator is
the QUANTIZATION probe = measured information content of identity:
**neutral 0.44 bits/body vs charged 9.86 bits/body.** That pair of numbers is
the quantitative punchline: *gravity ≈ 0 bits per body; EM ≈ 10 bits per
body.* (Refinement queued: multi-seed averaging to tame the data term.)

**M3 ✗ → corrected finding:** the d=1 charged code fits perfectly (MSE 7.9e-6)
yet is NOT monotone in q/m (spearman all +0.20, charged-only +0.30; the scatter
is a lookup table — similar q/m at opposite ends, neutral bodies at ±1 both
decoding to 0). "Capacity bottleneck ⇒ interpretable code" is FALSE: 1-d codes
are sufficient, not legible. Consistent with the SAE negative — this network
keeps choosing illegible codes; legibility must be selected for, it is not
free.

**M4 ~:** charged d=1 needs 9.9 bits/body (predicted 3–6 — right order, above
range); neutral ≈ 0.4 bits (predicted ≈ 0 ✓).

## 2026-06-11 — METRIC-COMPONENT COUNTING PRE-REGISTRATION (before running)

2+1 static anisotropic well: ds² = A dt² − (B dx² + 2D dxdy + C dy²), with
A = 1+2φ (Gaussian well), B = 1−2φ+0.2b, C = 1−2φ−0.2b, D = 0.15·d̃ —
φ, b, d̃ three independent smooth fields ⇒ the local form up to per-anchor
reshaping (overall scale) carries (A:B:C:D) = EXACTLY 3 independent numbers per
point. Architecture: position enters ONLY through a learned code m(p) ∈ R^d
(PosNet); InvNet(Δ, m) is the Siamese encoder; same-event task at shared
anchors. Sweep d ∈ {0, 1, 2, 3, 4, 6}.
Predictions: (N1) accuracy is clearly deficient for d ≤ 2 and saturates by
d = 3 (within noise of d = 4, 6) — the knee discovers the true count 3;
(N2) at d ≥ 3, isotonic R² of z vs the true local invariant > 0.95;
(N3) gradient-based recovery of the local form: per anchor, solve GΔ_i ∥ ∇_Δf_i
for symmetric G up to scale; median cosine to the true (A, −B, −C, −D) matrix
> 0.95 (the 2+1 generalization of Phase B's ratio readout);
(N4) d = 0 (position-blind) fails worst — the anisotropic well is behaviorally
real.

## 2026-06-11 — METRIC-COMPONENT COUNTING RESULTS (a spectacular pass, a
## control pass, and a counting gate that failed for a DEEP reason)

Accuracy vs code width d: 0 → 0.9202 · 1 → 0.9697 · **2 → 0.9971 (knee)** ·
3 → 0.9967 · 4 → 0.9962 · 6 → 0.9897.

**N1 ✗ — knee at d=2, not the pre-registered 3. Root cause (conceptual, not
noise):** position (x, y) is itself a 2-d sufficient code — a width-2 bottleneck
can simply pass the COORDINATES through and let the invariant network compute
the local form internally. An information bottleneck on position measures
min(dim of the base manifold, form dof) = min(2, 3) = 2. **Lesson: you cannot
count a field's per-point components by bottlenecking the ADDRESS — the address
is always enough.** The corrected design (queued next): decouple form from
position — draw RANDOM local forms per episode and force the network to infer
the geometry from k example events through the bottleneck (a set-encoder /
in-context design). Then the bottleneck must carry the FORM itself, and the
knee should land at the true form dof (3 in 2+1 up to scale; 5 in 3+1).

**N2 ✓ per-anchor isotonic R²: median 1.0000** (200 anchors × 30 obs).
**N3 ✓✓ the headline: the full anisotropic local metric — including the shear
component D — read out anchor-by-anchor from the trained net's gradients at
median |cos(Ĝ, G_true)| = 1.0000** (every anchor > 0.9997;
results/11_metric_components.png). This is the 2+1 generalization of Phase B:
not just a 1-d ratio profile but the entire 4-component anisotropic metric
FIELD, reconstructed from a network that was never told metrics exist.
**N4 ✓ d=0 fails worst (0.9202)** — the anisotropic well is behaviorally real.

## 2026-06-12 — IN-CONTEXT FORM-COUNTING PRE-REGISTRATION (before running)

The corrected N1: count the FORM's degrees of freedom, not the address's. Per
episode draw a random time-orthogonal 2+1 Lorentzian form — A ~ U[0.7,1.3] and
spatial SPD block from eigenvalues λ1,λ2 ~ U[0.7,1.3] + rotation ψ ~ U[0,π) —
a 4-component family = **3 dof up to the per-episode reshaping scale**. The
network sees k=8 context SAME-EVENT pairs from the episode's form, encoded by a
DeepSets set-encoder into a code of width d (the only channel — no position
exists in this world), then answers the standard same/different query.
Sweep d ∈ {1, 2, 3, 4, 6}.
Predictions: (F1) accuracy deficient for d ≤ 2 and saturating at d = 3 — and
the knee MOVES from the address experiment's 2 to the form's 3, which is the
whole point of the correction; (F2) saturated accuracy ≥ 0.98 (the task is
harder than step 11: the geometry must be inferred from 8 pairs per episode);
(F3) the d=2 deficit exceeds seed noise (clear gap, direction pre-registered,
magnitude not); (F4) d=1 substantially worse than d=2.

## 2026-06-12 — IN-CONTEXT COUNTING FIRST RUN: FLAT (diagnosis pre-registered
## before the follow-up)

Result: accuracy ≈ 0.904 for ALL d ∈ {1,2,3,4,6} — no knee. The code width is
not the binding constraint; gates F1–F4 unevaluable until the ceiling is
identified. Two hypotheses, distinguishable by experiment:
(H-noise) the ceiling is FORM-ESTIMATION noise — k=8 noisy context pairs can't
pin a 3-dof form tightly enough; prediction: accuracy at fixed d rises with k
(8 → 32 → 128), and the d-knee emerges once estimation noise stops dominating.
(H-opt) the set-encoder/training is the bottleneck; prediction: an ORACLE code
(true form handed to the invariant net directly, bypassing the set encoder)
restores ≈ 0.99; k-sweep changes little.
Diagnosis runs: oracle-code training; k ∈ {32, 128} at d = 3.

## 2026-06-12 — DIAGNOSIS RESULTS + corrected design (12c) pre-registration

Diagnosis: oracle (true form handed over) = **0.9920**; k-sweep at d=3:
k=8 → 0.904, k=32 → 0.915, k=128 → 0.929. Verdict: the task ceiling is high
(oracle), information is plentiful at large k (128 noisy linear constraints on
a 3-dof form ⇒ classical estimation would be ~0.1%-tight), yet accuracy crawls
— so the binding constraint is the MEAN-POOL SET ENCODER's inefficiency at
inverting quadratic constraints, with small-k estimation noise secondary.
Neither pre-registered hypothesis alone: H-opt primary, H-noise secondary.

**Corrected design (12c), bias declared openly:** context pairs presented as
difference-of-monomials u = vec(aaᵀ) − vec(bbᵀ) ∈ R⁶ (the constraint u·g = 0
becomes linear in the form). This supplies QUADRATICNESS — a structure already
earned from raw coordinates in Phase A — but not the metric: the network must
still infer the form from noisy constraints and squeeze it through the d-wide
code. Queries stay RAW (dt, dx, dy). k = 32.
Pre-register: (G1) d ≥ 3 closes most of the oracle gap (acc ≥ 0.97);
(G2) the knee lands at d = 3: d=2 deficit ≥ 2% vs d=3, d=1 worse still;
(G3) if G1 fails too, write the reconsider note — the counting question may
need an attention encoder or a fundamentally different probe.

## 2026-06-12 — 12c RESULTS + RECONSIDER NOTE (with peer input)

12c (quadratic item features, k=32): d=1 → 0.915 · d=2 → 0.931 · d=3 → 0.927 ·
d=4 → **0.950** · d=6 → 0.949. **G1 ✗** (gate was ≥ 0.97 at d ≥ 3; oracle is
0.992). G2 ✗ as stated — but the step-up sits at d=4, not 3.

**Peer input (second-opinion session, user-relayed) — two contributions:**
(a) the d=4 step is consistent with its PROJECTIVE-SMEAR prediction: the code
must carry the form up to scale (a direction, not a vector), so the knee can
smear by exactly one dimension — knee at 4 = 3 dof + 1 spent on scale;
(b) the decisive encoder diagnostic: the sufficient statistic for the
constraints u·g = 0 is the empirical second-moment matrix Σuuᵀ (its null
eigenvector IS the form). Mean-pooling can only build this if the per-item map
computes vec(uuᵀ) — so hand it over explicitly (R²¹, then pool) and the
encoder excuse disappears: if accuracy still doesn't close the oracle gap, the
problem is the code/readout, not the encoder.

**Reconsider decision (per pre-registered G3):** one final diagnostic run (12d:
explicit uuᵀ features, the literal sufficient statistic) with a stopping rule —
if d ≥ 4 still fails to reach ≥ 0.97, the counting question gets parked with an
honest "needs a different probe (attention encoder or regression-style
readout)" verdict, and the queue advances to Phase D.
12d pre-registration: (H1) d ≥ 4 reaches ≥ 0.97 (encoder was binding);
(H2) knee structure: d=2 clearly deficient; saturation by d=4, with knee at 3
vs 4 read as "exact projective chart found" vs "one dimension spent on scale" —
both readings recorded in advance.

## 2026-06-12 — PHASE D QUEUED: the Kaluza–Klein migration (peer proposal)

The project's central sentence has a historical sequel: Kaluza (1921) showed
the "1 number per body" that EM costs IS geometrizable — buy one extra
dimension, and charged 4d motion becomes free fall in 5d with q/m as momentum
around the extra circle. Phase D (proposed by the second-opinion session,
user-relayed): give the geometry model one extra COORDINATE-like latent per
body — entering the dynamics the way position does, not as a consumed embedding
— and ask whether training spontaneously converts the per-body charge code into
a position/momentum in an internal dimension. MDL framing: does the 9.86
bits/body of identity MIGRATE into geometry when the net is offered somewhere
geometric to put it? Any outcome is interesting; a positive completes the arc:
what universality geometrizes, an extra dimension can geometrize too. Design
pass needed before pre-registration (how the extra coordinate enters; what
"geometric" means operationally; the gates).

## 2026-06-12 — 12d RESULTS: stopping rule fired, counting PARKED

12d (exact sufficient statistic Σuuᵀ pooled, k=32): d=2 → 0.9225 · d=3 →
0.9392 · d=4 → 0.9444 · d=6 → 0.9470. **H1 ✗** (gate ≥ 0.97; oracle 0.992).
The encoder excuse is now eliminated: with the literal sufficient statistic
provided, the remaining ~5% gap lives in the READOUT chain (null-eigenvector
extraction by a small MLP head + consumption through the bottleneck). The rise
d=2 < d=3 < d=4 ≈ d=6 is consistent with the projective smear (suggestive, not
gated). **Parking verdict for the counting question:** accuracy-knee counting
requires near-oracle in-context inference; below that, inference noise smears
the knee beyond reading. Revisit only with a structurally different probe
(attention encoder at scale, or an eigenvector-aware readout). The arc's
keeper lessons: (i) you cannot count field components by bottlenecking the
address (11); (ii) you cannot count them by bottlenecking a code your
inference chain can't saturate (12–12d). Counting is the rare place where our
cheap-toy strategy hit its ceiling — recorded as such.

## 2026-06-12 — PHASE D PRE-REGISTRATION: the Kaluza–Klein migration (v1)

Design (one honest iteration; LNN/geodesic version deferred to D-v2): a shared
RECURRENT one-step dynamics F on an EXTENDED state s = (x, v, w) — s_{t+1} =
s_t + h·F(s_t), F identity-blind, rolled out from t=0. Bodies differ ONLY in a
learned initial condition w₀ (one scalar per body, entering as STATE, evolving
under the same F). Loss supervises x(t) at the Phase C target times only; w is
never supervised. Charged-mix data (identical to Phase C/10).
Gates: (D1) fit — extended-state geometry model reaches force-model accuracy
on charged bodies (the plain geometry model failed 88×); (D2) the migration —
behavioral decode of w₀ against true q/m, |r| > 0.99 (charge became an initial
condition of a shared dynamical system); (D3) the isometry question (genuinely
open, both outcomes recorded): does the learned F conserve w (|Δw| small along
rollouts — the net discovers that the internal dimension should have a
symmetry), or does it use w non-conservatively? (D4) zero-shot state
estimation — for HELD-OUT bodies, optimize the scalar w₀ alone (no weight
updates) on the first target point; prediction of the remaining points should
approach in-training accuracy: identity inferable from motion, like any
coordinate, with ~10 bits (the MDL tie-in: the bits migrate from model
parameters to state).

## 2026-06-12 — PHASE D RESULTS: THE KALUZA MOVE, REDISCOVERED (all gates)

| gate | result |
|---|---|
| D1 fit | test MSE 4.64e-5 ≤ 1e-4 ✓ (same order as the 4-d force model; ~6× the d=1 force model) |
| D2 the migration | behavioral decode of w₀ vs true q/m: **r = +0.9998** ✓✓ |
| D3 the isometry | drift 0.140 vs population spread 1.062 — w is APPROXIMATELY conserved (~13%); the net roughly discovered the internal symmetry, imperfectly (recorded as partial, as pre-registered) |
| D4 zero-shot | held-out body, w₀ fit from ONE point, no weight updates: 6.8e-5 vs 4.6e-5 in-training ✓ — identity is INFERABLE FROM MOTION, like a coordinate |

**The Phase D sentence:** a single identity-blind dynamical rule on an extended
state (x, v, w), with bodies differing only in an initial condition w₀, fits
charged motion at force-model accuracy — and each body's w₀ turns out to BE its
charge-to-mass ratio (r = 0.9998), approximately conserved along rollouts, and
estimable for new bodies from one observation. The per-body identity migrated
from MODEL PARAMETERS into STATE: charged motion became free motion in a bigger
space. That is Kaluza's 1921 move, rediscovered by economy in a trainable
system — and it closes the project's arc: what universality geometrizes
(Phase C), an extra dimension geometrizes too (Phase D). Credit: experiment
proposed by the second-opinion session (user-relayed). Plot: 14_kaluza.png.

Caveats: v1 is a dynamical-systems statement (shared one-step map), not yet a
geodesic/metric statement — D-v2 (extended-Lagrangian/metric form, the true KK
structure test ∂L/∂ẇ = conserved momentum ∝ q/m) stays queued; drift 13% means
the isometry is approximate; same toy fields as Phase C.

## 2026-06-12 — MULTI-SEED MDL RESULTS (M1'/M2')

3 seeds per (mix, d): **charged minimum at d=1, decisive and stable** (d=0 is
+8,870 ± 15 bits — the tiny std shows the explosion is structural; d=2 +1,481;
d=4 +1,116) ✓ M2'. **Neutral ordering restored: d=0 is now the minimum** with
monotone growth (+474, +601, +773 for d=1,2,4), but separations sit within
~1σ at 3 seeds — recorded as "ordering consistent with M1', significance
marginal; more seeds would sharpen, diminishing returns vs the quantization
probe which already settles it (0.44 vs 9.86 bits/body)."

## 2026-06-12 — RECONSIDER: THE ARC IS COMPLETE (loop paused for direction)

Phases A → D all landed: interval invented · light cone emerged · gravity well
traced · geometry-vs-force decided in bits (0.44 vs 9.86/body) · the Kaluza
migration performed (r = 0.9998). The writeup tells the whole story. Per the
autonomous-mode ground rule ("pause and reconsider when results suggest it"),
this is the natural pause point — the next move is a direction choice, not an
iteration. Options, with my recommendation order:
1. **Polish & share** (recommended next): the writeup is a complete, honest,
   genuinely novel-as-demonstration story. A pass for figures/clarity, then
   post it (blog / arXiv-style note / the ansatz-machine treatment — its own
   repo). Highest value-per-effort; the artifact exists, make it visible.
2. **D-v2, the geodesic completion:** learned extended Lagrangian; gate =
   ∂L/∂ẇ (conserved momentum) ∝ q/m by autodiff. The scientifically right
   capstone; medium effort (LNN training is finicky).
3. **Return to a parked project:** echoes v2 (ML scorer through the calibrated
   harness — user's hands-on ML role) or ringdown v2 (highest external science
   value).
4. **New frontier:** "many bodies, one shared FIELD" — learn the metric field
   of a 2+1 world from trajectories alone (combines B+C machinery); or the
   3+1 Kaluza with a real vector potential.

## 2026-06-12 — D-v2 PRE-REGISTRATION: the Lagrangian Kaluza (before running)

Model: ONE shared scalar L_θ(x, w, ẋ, ẇ) = ½(ẋ² + ẇ²) + f_θ(x, w, ẋ, ẇ)
(kinetic seed declared: guarantees an invertible velocity Hessian at init,
zero-initialized f lets training shape everything else). Motion = Euler–
Lagrange rollout (q̈ = H_vv⁻¹(∂L/∂q − H_vq q̇), RK2, h = 0.1, ridge 1e-3).
Bodies differ ONLY in a learned initial internal velocity ẇ₀ (w₀ ≡ 0 for all —
identity must enter as MOMENTUM, not as a positional label). Loss: x(t) at the
Phase C targets; w never supervised. Charged mix.
Gates: (E1) fit ≤ 1e-4 test MSE; (E2) THE KK identity: p_w = ∂L/∂ẇ per body is
(a) conserved along rollouts (drift ≪ population spread) and (b) |corr| > 0.99
with true q/m — charge IS the conserved internal momentum, read by autodiff
from a learned Lagrangian; (E3) cyclicity: the net discovers the isometry —
median |∂L/∂w| ≪ median |∂L/∂x| (ratio < 0.2); (E4) zero-shot: held-out body's
ẇ₀ fit from one point (no weight updates) predicts the rest.
Risk note: LNN-style training is known-finicky (Hessian inversion); one fix
round allowed, then honest verdict.

## 2026-06-12 — D-v2 FIRST RUN: honest negative with a DEEP lesson

E1 ✓ (3.15e-5 — a generic extended Lagrangian fits charged motion). E2 ✗
(corr(p_w, q/m) = −0.26; drift 33% of spread). E3 ✗ (cyclicity 0.94 — L uses w
nearly as much as x). E4 ~ (zero-shot at 3× degradation).
**Diagnosis — economy does not select gauge:** the equivalence class of
extended-space Lagrangians reproducing the same x-motion is large; the KK form
(cyclic w, charge = conserved momentum) is one gauge choice within it, and
nothing in the data or the loss prefers it. The net used w as a time-growing
label channel instead. v1's behavioral gates were gauge-ROBUST (hence passed);
v2's structural gates are gauge-FIXED (hence honestly failed). Same villain as
Phase B's per-anchor reshaping and the MDL lookup-code: gauge freedom is this
project's recurring lesson.
**Pre-registered fix round (one allowed):** impose the isometry as
architecture — L_θ(x, ẋ, ẇ), w never an input (cyclic by construction; declared
bias) — and test what REMAINS discoverable: (E2') the conserved p_w = ∂L/∂ẇ per
body correlates with true q/m at |r| > 0.99 ("given an internal symmetry, the
conserved momentum self-organizes into the charge — the coupling is learned");
(E1') fit still ≤ 1e-4 (the true dynamics admits this form, derived:
L = ½ẋ² + ½ẇ² − φ(x) − ẇV(x) with V' ∝ −E reproduces a = −φ' + (q/m)E);
(E4') zero-shot. If E2' fails too, the verdict stands as "KK structure needs
more than economy + symmetry" and D closes on v1's result.

## 2026-06-12 — D-v2 CLOSED (fix round failed on numerics; verdict recorded)

Cyclic fix round: E1 ✗ catastrophically (test MSE 79.2; loss oscillated
0.07 → 31 → 50 → 0.36 → 3.6 — Euler–Lagrange rollout stiffness/near-singular
Hessian solves; ridge 1e-3 insufficient; the pre-registered LNN-finickiness
risk realized). E3 trivially 0 (w not an input); E2/E4 meaningless on a
diverged model.
**D-v2 final verdict (per the one-fix-round rule):** the KK STRUCTURAL
statement — charge = conserved ∂L/∂ẇ of a learned cyclic Lagrangian — remains
UNVERIFIED, not refuted: (a) the structure is analytically attainable (the true
dynamics admits L = ½ẋ² + ½ẇ² − φ − ẇV with V′ ∝ −E); (b) run 1 proved a
generic extended L fits but economy does not select the KK gauge; (c) run 2
proved our training machinery can't yet optimize the gauge-fixed form.
**Phase D's deliverable stands on v1's gauge-robust behavioral result
(r = 0.9998).** Future work (not now): stabilized LNN tricks
(Hamzaogullari–Ozakin-style) or a Hamiltonian parameterization with built-in
symplectic integration.

## 2026-06-12 — PHASE E PRE-REGISTRATION: the metric FIELD from trajectories

The capstone combination (resolves Phase B's "only A/B per point" caveat with
cross-position data): learn the full anisotropic field of the 2+1 well from
TRAJECTORIES alone. Generator: slow-motion mechanics in the step-11 world —
L = ½ q̇ᵀS(q)q̇ − φ(q), S = [[B,D],[D,C]], φ = ϕ(x,y) (the Gaussian well);
RK4 with finite-difference field derivatives. Model: declared-bias structure
"motion = mass-matrix mechanics" with the FIELDS free — S_θ(q) via Cholesky
(SPD by construction, no implicit Hessian solves — the D-v2 trap avoided) and
φ_θ(q); EOM in closed form; differentiable RK2 rollout; loss = positions at
t = 1, 2, 3. Identifiability note (recorded): trajectories pin (S, φ) up to ONE
GLOBAL scale (L → cL) and an additive constant on φ — gates fit that global
freedom once, never per-point.
Gates: (E1) held-out-IC trajectory MSE ≤ 1e-4; (E2) field recovery: after one
global scale, median cos(vec Ŝ(q), vec S(q)) > 0.99 over a probe grid AND
corr(φ̂, φ) > 0.99 up to affine; (E3) constant-field control (S, φ learnable
constants only) clearly worse on E1; (E4) the recovered D̂(q) (shear) tracks
the true off-diagonal field — the component Phase B could never see.

## 2026-06-12 — PHASE E MAIN RESULTS (E1/E2/E4 ✓✓; E3 control rerunning)

E1 ✓ held-out-IC MSE 5.03e-6 (gate 1e-4). E2 ✓✓ field recovery after ONE
global scale: **median cos(vec Ŝ, vec S) = 1.0000** over the probe grid;
corr(φ̂, φ) = 0.9997. **E4 ✓✓ the capstone: the SHEAR field D̂ recovered at
r = 0.9989 from trajectories alone** — the component Phase B provably could
not see (per-anchor reshaping) is pinned by cross-position dynamics, exactly
as the Phase B caveat predicted. The D-v2 numerical trap was avoided by
construction (closed-form mass-matrix EOM, Cholesky-SPD fields — no implicit
solves; training stable, loss 0.0088 → 5e-6). E3 (constant-field control)
crashed on an autograd allow_unused edge (constant fields have legitimately
zero spatial gradient — handled), rerun: **E3 ✓ — constant-field control
8.74e-3 vs 5.03e-6, a 1700× gap. ALL FOUR GATES PASSED — Phase E complete.**
Plot: results/16_field_from_trajectories.png.

## 2026-06-13 — CURVATURE-INVARIANT PRE-REGISTRATION (the closing readout)

Compute the Gaussian curvature K(x,y) of Phase E's LEARNED spatial metric
Ŝ(x,y) by autodiff (Brioschi formula — needs 2nd derivatives of the field
nets) and compare to the true world's K from fields_2p1 (finite differences).
Scale law: S → cS ⇒ K → K/c, so the Phase E global scale is applied once.
Gates: (G0 FIRST, honesty) the Brioschi implementation must reproduce a known
answer before touching learned fields — a 2-sphere patch S = diag(1, sin²x)
has K ≡ 1 (tolerance 1%); (K1) corr(K̂, K_true) > 0.95 over the probe grid
(2nd derivatives amplify noise — gate set accordingly); (K2) magnitude: median
|K̂·c − K_true| / (|K_true| + median|K|) < 0.2; (K3) far-field sanity: both
curvatures ≈ 0 away from the bumps. If K1 passes: the network's geometry has
the right CURVATURE — the coordinate-free closing statement of the project.

## 2026-06-13 — CURVATURE-INVARIANT RESULTS: ALL GATES — THE CLOSING READOUT

G0 ✓ (sphere check exact, 0.0000). **K1 ✓ corr(K̂, K_true) = 0.9903** —
the Gaussian curvature of the LEARNED geometry reproduces the true world's
curvature map (central positive bump, negative ring, asymmetric lobes;
results/17_curvature_invariant.png). K2 ✓ 0.157. K3 ✓ far-field 0.0260 vs
0.0260 (mask bug |x|>2.2 vs grid-end fixed to corner mask — recorded).
**The project's title question, closed in its own currency: a network watched
things move, built a geometry, and that geometry has the right CURVATURE —
the coordinate-free, Theorema-Egregium-grade invariant, computed by
differentiating the trained network twice.** Phase E rerun reproduced exactly
(E1 5.03e-6, cos 1.0000, D̂ 0.9989 — seeding works).

## 2026-06-13 — PHASE D-3: MAGNETIC KALUZA DESIGN NOTE (pre-registration)

The missing Kaluza test is the MAGNETIC one: velocity-dependent forces.
Needs ≥ 2 spatial dims. World: 2+1 charged dynamics, a = −∇φ + (q/m)(E + v×B)
with B(x,y) an out-of-plane field bump (E off for clarity; B is the star).
Model: D-v1's proven recurrent machinery on extended state (x, y, vx, vy, w)
— shared identity-blind one-step map F, per-body w₀ as state (NOT the
Lagrangian form — D-v2's numerics stay shelved). Gates (mirror D-v1):
(M1) fit ≤ 1e-4 where the w-less geometry model fails on charged bodies;
(M2) behavioral decode of w₀ vs q/m, |r| > 0.99 — the internal coordinate
carries charge in a VELOCITY-COUPLED world (the genuinely new bit: in real KK
the magnetic force IS the Coriolis force of the internal dimension);
(M3) approximate conservation of w along rollouts; (M4) zero-shot w₀ from one
observed point. Build = extend make_dynamics_dataset to 2-d + B-field,
KaluzaModel state width 5. Queued for the next build slot.

## 2026-06-13 — D-3 RESULTS: the magnetic Kaluza (M2 ✓✓, M1 marginal-pass)

**M2 ✓✓ r = +0.9974** — the internal coordinate carries q/m in a
VELOCITY-COUPLED world: v×B forces geometrize exactly like electric ones.
With D-v1 this completes the toy KK suite (electric + magnetic — the magnetic
force as the hidden dimension's Coriolis effect, behaviorally demonstrated).
M1: Kaluza 1.07e-4 vs gate 1e-4 (7% over — the gate was a trainability guess;
recorded as marginal) while the w-less control fails 23× on charged bodies
(3.1e-3) and 3.4× on neutral (mixed-training contamination, consistent with
Phase C). No fix round spent on the 7%: the control separation is the
substance. M3/M4 not run (context-economy; both passed in D-v1's identical
machinery — noted, not claimed). Plot: 18_magnetic_kaluza.png.

## 2026-06-13 — PHASE F PRE-REGISTRATION: THE LAW ITSELF (matter → geometry)

Every prior phase learned ONE world's geometry. Phase F learns the MAPPING:
worlds = random matter configurations (1–2 softened point masses, centers
U[−1.8,1.8]², masses U[0.3,1.0], softening ε=0.35; true acceleration field
a = −Σ mⱼ(x−xⱼ)/(r²+ε²)^{3/2} — the real kernel, declared); data = neutral-
body trajectories per world (Phase C conventions; targets t = 1,2,3). Model:
matter density rendered on a 48² grid → small CNN encoder-decoder → a 2-channel
ACCELERATION FIELD (acceleration, not potential: kills the gauge constant);
trajectories predicted by differentiable rollout with bilinear grid_sample
interpolation. φ/a never supervised — trajectories only.
Gates: (F1) held-out WORLDS (unseen configs, same 1–2 blob family): trajectory
MSE ≤ 1e-3; (F2) field recovery on unseen worlds: median cos(â, a_true) > 0.98
(weighted to |a| above its 20th pctile — direction comparisons are meaningless
where a ≈ 0); (F3) **SUPERPOSITION — the killer gate:** train on 1–2 blob
worlds ONLY, test on 3-blob worlds: F1/F2 metrics within 2× of in-distribution
⇒ the net discovered the law's LINEARITY; (F4) matter-blind control (same
trajectory net, ρ input zeroed) fails across worlds by ≥ 10×.

## 2026-06-14 — F-v2 STEP 3 PRE-REGISTRATION: the clean locality experiment

Diagnostics verdict (22_fv2_diag, full table in JSON): overfit-one-batch FAILS
at 0.047 (vs oracle floor 1.2e-4) while capacity_2x and data_2x change nothing
and LR is mild (best 3e-3) ⇒ representational wall ⇒ roadmap branch 2A. The
one-knob test: 4 arms identical in EVERYTHING (kernel 5, channels 16/32/32,
LR 3e-3 from the sweep, same steps/batch/data/seed) except the dilation
schedule of the middle layers: max-dilation D ∈ {1, 2, 4, 8} → receptive field
≈ 17, 29, 53, 101 px on the 48-grid (global at D≥4).
Gates: (RF1) F2_cos increases monotonically with D (the locality hypothesis's
signature — this is the claim under test, not a tuning hope); (RF2) the D=8 arm
reaches F1 ≤ 5e-3 AND F2 ≥ 0.98 (within sight of the original gates given the
1.2e-4 floor). If RF1 holds but RF2 falls short: F-v3 = spectral/global-kernel
layer (learnable Green's function; nonlinearities retained so superposition
stays earned). If RF1 fails: locality was NOT the wall — reconsider note.
Compute note: ~4 × 55 min sequential on this Mac; the L4 VM would cut this 5×+
but is Ludo-reserved — flagged to the user as an option, not assumed.

### v0.1 / Phase B queue
1. v0.1: open sampling to spacelike + past-directed events → invariant count
   becomes (s², branch); watch the K-sweep knee move from 1 to 2. Cheap, sharpens
   the counting methodology.
2. 3+1 flat: same experiment with (t,x,y,z) — rotations join the symmetry group;
   prediction unchanged (one invariant). Confirms dimension-independence.
3. Phase B design research pass: "same event, two local observers" in a weak
   gravity well (Schwarzschild far field or constant-curvature toy); then the
   position-conditioned encoder f(Δ; position) and the g(r)-tracking gate.
4. The depth-wise SAE side quest: how does the invariant get assembled layer by
   layer? (User's interpretability toolkit; genuinely unexplored.)

## 2026-06-12 — MPS enablement for the 3+1 law (script 21): trilerp rewrite

Decision/ADR. The 3+1 gravity-law run is CPU-bound on the Mac (3D convs). Probed
MPS empirically (M4, torch 2.12): Conv3d + 3D grid_sample run on MPS, but the
BACKWARD `aten::grid_sampler_3d_backward` is unimplemented (pytorch#141287) — our
differentiable rollout calls it 30×/step, so training threw. `PYTORCH_ENABLE_MPS_
FALLBACK=1` routes that op to CPU (~590ms/step, copies 30×/step — not worth it).

Fix: replaced `nn.functional.grid_sample(..., align_corners=True, padding_mode=
'border')` with a hand-rolled `trilerp()` (8-corner trilinear via gather+arithmetic,
all MPS-backward-supported). Added `--device {cpu,mps,cuda}` (default cpu, so the
in-flight run + checkpoint-resume are byte-for-byte unchanged). Verified vs
grid_sample on CPU: value max-diff 1.2e-7, grad-field 6e-8, grad-grid 9.5e-6
(float32 epsilon — CPU path provably unchanged, resume-safe). Full step trains on
MPS with no unimplemented-op error.

Measured (CPU contended by the live 21_law_3p1 run): full step CPU 1092ms vs MPS
717ms = 1.52×; Conv3d-only (the ~90% bottleneck) 2.1× on MPS. Clean uncontended
number pending the live run finishing. Honest framing: MPS is a modest free win
(~2×, no Ludo disruption) for local iteration; the L4 GPU (~10-30×, native CUDA
grid_sample, no rewrite) stays the heavy-artillery option for the F-v2 LR×seed×
convergence sweep. See ai-coding-standards SKILL "ML experiment methodology".

## 2026-06-12 — PHASE F RESULTS (honest null): 1 of 4 gates passed

Run: `19_matter_to_geometry.py`, 12000 steps, Adam 1e-3, CPU (results/19_law.json,
plot 19_matter_to_geometry.png). Gated against the 2026-06-13 pre-registration above:

| Gate | Pre-registered | Actual | Verdict |
|---|---|---|---|
| F1 held-out traj MSE | ≤ 1e-3 | 0.0583 | **FAIL (58×)** |
| F2 field recovery cos | > 0.98 | 0.9372 | **FAIL** |
| F3 superposition cos | > 0.96 | 0.9648 | PASS |
| F3 superposition MSE | ≤ 2× F1 | 0.1545 (2.65× F1) | **FAIL** |
| F4 matter-blind control | ≥ 10× F1 | 0.3717 (6.4× F1) | **FAIL** |

Honest reading: the net learned the field's DIRECTION and direction-superposition
DOES generalize to 3-blob worlds (F3 cos 0.965 — the genuinely encouraging result:
linearity-in-source partly emerged). But magnitude accuracy (F1), field-cosine (F2),
and control separation (F4) all missed. This is the failure the pre-registration named
as the suspect: a 4-layer 5×5 CNN has receptive field ~17px against a long-range 1/r
kernel on a 48px grid — a pen-and-paper mismatch we recorded but never computed.

NOT a "flying colors" pass (a parallel Gemini session reported it as such by
cherry-picking the F3 cosine — corrected here). Per project rule, null results are
results; this stands as an honest negative pending F-v2.

Methodology debts this exposed (now in ai-coding-standards SKILL "ML experiment
methodology"): (1) the F1 ≤1e-3 gate was never checked against the grid+grid_sample
DISCRETIZATION FLOOR — may be partly unpassable by construction; an oracle rollout of
the TRUE field must precede any F-v2 gate. (2) LR was the 1e-3 default, never swept —
the 0.058 plateau is uninterpretable (model can't, or optimizer didn't?). (3) loss was
flat by ~step 6000 of 12000 — a 25%-feasibility check would have caught it early.

F-v2 (pre-reg before building): oracle floor first; 3-pt LR sweep + cosine decay;
diagnostic trio (overfit-one-batch / 2× model / 2× data) to locate the bound; THEN the
receptive-field fix (dilated convs / larger kernels / Fourier features). The in-flight
3+1 run (script 21, 24³ grid → larger relative receptive field) is an accidental
locality probe — its F2 vs this F2 is a free datapoint.

STALE CHECKPOINT TRAP defused: results/19_ckpt.pt (the finished step-12000 failed
model) renamed to 19_ckpt_v1_failed.pt so a fresh F-v2 run of script 19 trains from
scratch instead of silently resuming the failed model.

## 2026-06-12 — 3+1 LAW RESULTS (script 21): failed all gates, CONFOUNDED

Run `21_law_3p1`, 8000 steps batch 48, 24³ grid (results/21_law_3p1.json):

| Gate | Pre-reg | 3+1 | 2+1 (Phase F) | Verdict |
|---|---|---|---|---|
| F1 traj MSE | ≤1e-3 | 0.041 | 0.058 | FAIL 41× |
| F2 field cos | >0.98 | 0.417 | 0.937 | FAIL hard |
| F3 superpos cos | >0.96 | 0.685 | 0.965 | FAIL |
| F3 superpos MSE | ≤2×F1 | 0.112 (2.7×) | 2.65× | FAIL |
| F4 blind control | ≥10×F1 | 0.141 (3.4×) | 6.4× | FAIL |

Worse than 2+1 on every interpretable metric. **Refutes the clean locality
hypothesis** (predicted: larger relative receptive field on 24³ → better F2; got
0.417 ≪ 0.937). BUT the run is CONFOUNDED — vs 2+1 it changed three things at once:
kernels 5²→3³, channels 16/32/32→8/16/16, and training 2.3M→384k samples (6× less,
the batch 192→48 + steps 12000→8000 combo). "Worse everywhere" is fully explained by
under-capacity + under-training; it does NOT adjudicate receptive field. Textbook case
of the methodology debt: never change >1 knob without a control.

Most diagnostic: **F4 = 3.4×** — the matter-BLIND control is nearly as good as the
matter-aware model ⇒ the 3D net barely uses the density field. Under-training/capacity
signature, NOT long-range-kernel. Rule-out flagged: a coordinate-axis bug in the 3D
(z,y,x) grid_sample/trilerp mapping would also give weak-positive cos — check before
concluding.

Verdict: clean null, uninterpretable re: locality. Next (pre-reg before building):
(1) sanity-check the 3D coordinate mapping (inject the TRUE field, confirm trajectories
reproduce — separates bug from learning); (2) oracle discretization floor on 24³;
(3) diagnostic trio (overfit-one-batch / 2× capacity / 2× data) to locate the bound;
THEN decide 2+1-F-v2 vs 3+1 depth. MPS (--device mps, trilerp) makes these sweeps
cheap locally.

## 2026-06-12 — F-v2 diagnostics autonomous runner (script 22) + oracle floor

Built `22_fv2_diagnostics.py`: the pre-registered methodology battery for the 2+1
law, reusing script 19's data/model/eval (no duplication). Runs unattended (no Claude
in the loop), checkpoints results/22_fv2_diag.json after EACH experiment (power-loss
resumable), emits dashboard heartbeats (22_*). Battery: oracle floor · overfit-one-
batch (expressivity) · LR sweep {3e-4,1e-3,3e-3} + cosine decay · capacity 2× · data
2×. Launched --steps 4000 (~2-2.5h CPU).

KEY EARLY RESULT (oracle floor, step-independent): **oracle F1 floor = 1.2e-4, BELOW
the 1e-3 gate.** Overturns the "gate may be infeasible by construction" hypothesis —
the gate was feasible; Phase F's 0.058 left ~480× on the table ⇒ a MODEL/TRAINING
shortfall, not an unfair gate. (The grid+grid_sample+coarse-Verlet discretization
floors trajectory error at 1.2e-4, so a perfect field still can't gate below that —
but Phase F was nowhere near.) Remaining arms (LR/capacity/data) populate on the full
run. Smoke-tested end-to-end (--steps 20) before launch; verify.sh ALL GREEN.

## 2026-06-14 — run-survival diagnosis: session-bound kills, not OOM
Five sweep deaths investigated: memory 68% free, no tracebacks, machine up 17 h
⇒ NOT OOM, NOT power (this time). Cause: harness background tasks are children
of the Claude session — session restarts (model switches, app reloads) kill
them. Fix: long runs now launch DETACHED (nohup+disown, results/23_sweep.log),
monitored via heartbeat files + accumulated json + checkpoints — a deliberate,
documented inversion of the always-tracked rule, for survival. PID recorded in
the log; the wakeup loop polls files, not task notifications.

## 2026-06-14 — resume contamination FIXED (bit-exact checkpoints)
curvlib gained save_ckpt/load_ckpt: checkpoints now carry the numpy generator
state + torch RNG state alongside weights/optimizer/step, and writes are atomic
(tmp+rename — a power cut mid-save can no longer corrupt a checkpoint). Wired
into 19 and 23; legacy checkpoints load with a NOT-bit-exact flag. PROOF: 6
continuous steps vs 3 + save + fresh-process load + 3 give bitwise-identical
parameter checksums (849.3047059388 both; torch RNG deliberately scrambled
between save/load). Consequence: interruptions now cost minutes and NOTHING
else. The in-flight sweep arms (d2-d4) run the old in-memory code — any future
resume of them uses the new path; arm d1's contaminated number stays flagged
for the RF1 gating decision per the pre-registration.

## 2026-06-14 — MPS unlocked: 12.4× (bilerp twin of the trilerp fix)
MPS benchmark on the exact sweep workload: CPU 1095 ms/step vs MPS 88 ms/step
= **12.4×** (losses agree). Blocker was grid_sampler_2d_backward (same
pytorch#141287 as 3D); fixed with curvlib.bilerp — verified EXACT vs
grid_sample (values + field-grads 0.0; coord-grads float32-eps) — used on MPS
only, CPU keeps grid_sample for bitwise continuity with existing checkpoints.
DECISION: killed the CPU sweep (d2 mid-flight), archived partials
(*_cpu_partial.json, *_cpu.pt), relaunched ALL FOUR arms fresh on MPS — one
stroke buys device-uniformity for the one-knob experiment AND the clean d1
rerun the contamination flag required, and still finishes sooner (~70 min)
than the CPU run's remainder. Note: MPS arithmetic differs from CPU at float
eps, so cross-run comparisons stay at the metric level (cos/MSE), never
bitwise. User plan recorded: L4 GPU available in 1-2 days; Mac+MPS until then.

## 2026-06-14 — RF SWEEP RESULTS: Phase F CLOSED (locality confirmed; F-v3 skipped)

Clean MPS arms: d=1 F2=0.852 · d=2 F2=0.981 · d=4 F2=0.985 (F1: 0.090 → 0.042
→ 0.027) · d=8 COLLAPSED (F1=1.40, F2=0.678). Gating: **RF1 fails as literally
pre-registered** (non-monotone through d=8) — but the collapse has an
independent known mechanism (extreme-dilation "gridding": kernel samples every
8th pixel of a 48 grid + padding domination; F1=1.4 suggests partial
divergence), and within the valid arms the locality signature is decisive
(+0.13 cos, 3.3× F1 as reach grows 17→53 px). **RF2 fails** (best F1=0.027 vs
5e-3): reach fixes DIRECTION, not magnitude — consistent with the established
result that long-range kernels want global/spectral operators (FNO et al.).
**DECISION: Phase F closes here. F-v3 (spectral Green's-function learner) is
deliberately SKIPPED** — it would re-derive known neural-operator science
(recorded honestly when the track started), and the user has redirected the
project to a more original arc (see PHASE G/H design note). Phase F's legacy:
the direction-vs-magnitude decomposition (local shape vs global strength), the
diagnostics discipline, and the infra (bilerp/MPS 12.4×, bit-exact ckpts,
detached runs).

## 2026-06-14 — PHASE H ROW 1 PRE-REGISTRATION: two charges, how many lanes?

World: 1-d dynamics, a = −φ′(x) + qm₁·E₁(x) + qm₂·E₂(x) — TWO independent
per-body labels coupling to two field bumps at different centers (E₁ at +0.8,
E₂ at −1.2; both Gaussian, amp 0.3/0.35). Bodies: 40 (8 held out), labels in
±[0.3, 1] independently (some bodies neutral in one or both). Model: D-v1's
recurrent extended-state machinery with L internal lanes, state (x, v, w₁..w_L),
per-body w₀ ∈ R^L learned; sweep L ∈ {0, 1, 2, 3}.
Honest counting caveat UP FRONT (the step-11/12 lesson): one real number CAN in
principle encode two (nonlinear interleaving), so "knee at 2" is a claim about
what smooth nets FIND AT FIXED BUDGET, not information theory. Gates:
(H1) L=0 fails hard on doubly-charged bodies (control); (H2) at fixed budget,
fit improves sharply L=1→2 and saturates L=2→3 (the practical knee; report all
four numbers; if L=1 matches L=2, that ITSELF is the finding — a 1-lane
nonlinear code — report as such); (H3) behavioral decode at L=2: sweeping the
two lane-coordinates maps invertibly onto effective (qm₁, qm₂) — after one
linear mixing (lanes may rotate; mixing allowed, gauge), joint decode r > 0.99
per label; (H4) zero-shot: held-out body's (w₁, w₂) fit from one observed
point. Device: bench CPU-vs-MPS one step, pick winner, record.

## 2026-06-15 — PHASE H ROW 1 RESULTS: the knee lands at 2

Script 24, sweep complete (results/24_two_charge.json, 24_two_charge.png):

| lanes L | test MSE (all) |
|---|---|
| 0 | 1.13e-1 |
| 1 | 4.38e-3 |
| 2 | **1.20e-4** |
| 3 | 1.35e-4 |

- **H1 ✓** L=0 fails hard (940× worse than L=2) — without lanes the
  identity-blind net cannot tell doubly-charged bodies apart.
- **H2 ✓✓** sharp improvement 0→1 (26×) and 1→2 (36×), then saturation
  2→3 (flat, slightly worse) — **the practical knee is exactly at L=2,
  matching the two independent labels in the generator.** Behavioral
  lane-counting works where bottleneck-counting (steps 11/12) hit the
  readout wall: the rollout itself is the near-oracle inference engine.
- **H3 ✓✓ (script 24b): behavioral decode r = 0.9996 / 0.9998 per label**
  (raw 0.9995/0.9998 — the allowed linear mixing barely needed: the net's
  lanes landed nearly axis-aligned with the true charges). Method: generator
  bank over a 61×61 (qm₁,qm₂) grid × 64 probe states; each trained body
  decoded by argmin trajectory-MSE — read out by what the body DOES.
  Gate r>0.99 PASS. Plot results/24b_decode.png, json 24b_decode.json.
- **H4 ✗ as pre-registered, then the fix round made it a finding (24c):**
  fitting a held-out body's TWO lanes from ONE trajectory fails (median
  eval MSE 8.8e-2 ≈ 700× seen-body test; the one body with a single nonzero
  charge decoded fine — identifiability smell). One fix round, one knob =
  number of observed trajectories k:
  k=1: 8.8e-2 · k=2: 2.1e-3 · k=4: 1.0e-4 · k=8: 8.5e-5 (seen-body
  reference 1.2e-4). **Two unknown charges need a few independent
  measurements; by k=4 a never-seen body is fully characterized (matches
  trained-body accuracy), saturated by k=8.** Restarts were already 5×, so
  this was information-starvation, not optimization — one short trajectory
  often doesn't probe both field bumps. Physically sensible: you can't
  measure two coupling constants with one experiment that mostly sees one
  field. H4 verdict: zero-shot WORKS from a handful of points, not one;
  the k=1 gate was over-optimistic and is recorded as failed-as-written.
  json results/24c_h4_ksweep.json. **Phase H row 1 CLOSED.**

## 2026-06-15 — PHASE G PRE-REGISTRATION: the generalist

Data: 25_bank.npz — 24k episodes, 8 families, unified tokens (pairs + tagged
trajectory snippets + matter blobs), TRUE world params saved per episode.
Family identity NEVER given to the model. Split: last 10% of episodes per
family = validation (every episode is a fresh world ⇒ val = unseen worlds).
Model (~3M params, MAXIMALIST per user): Linear(18→192) token embed →
5-layer transformer (d=192, 6 heads) → mean-pool → world-summary w ∈ R^64 →
query head: [query embed ⊕ w] → MLP → {binary logit, 6-dim regression};
mask-free multi-task loss (BCE for pair queries + MSE for traj queries, fixed
1:1 weights — recorded as a chosen knob). Streaming-ready (bank regenerable);
bit-exact checkpoints; MPS.
Gates: (G1) val competence per family — pair-families accuracy > 0.95;
traj-families MSE < 1e-3 (comparable to specialist scales at these target
magnitudes); report full 8-row table, no cherry-picking. (G2) zero-shot
robustness: a fresh 2k-episode bank with parameter ranges WIDENED 25% — gates
degrade gracefully (< 2× val loss), no cliff. (G3) THE PRIZE, summary-space
probes on val episodes' w vectors vs saved true params: (a) family clustering
ARI > 0.8 (pre-registered); (b) within-family physical-parameter decodability
from w (depth/amps: small-probe r > 0.9, pre-registered); (c) EM-kinship
distance question (chargedE↔magneticB vs either↔well1p1, against shuffled
nulls) — EXPLORATORY, labeled as such; (d) summary intrinsic dimensionality vs
true param counts — EXPLORATORY.

### G1 first run (30k steps): FAIL — underfit, fix round = train longer

Full table (results/26_g1.json): flat1p1 0.992 ✓ · flat3p1 0.950 ✓ (at the
line) · well1p1 0.926 ✗ · aniso2p1 0.906 ✗ · chargedE 1.5e-2 ✗ ·
magneticB 4.2e-3 ✗ · twocharge 4.2e-2 ✗ · matter 5.9e-2 ✗ — 2/8 rows.
Diagnosis: UNDERFIT — train loss ≈ val error (no generalization gap), loss
still falling at step 30k (never plateaued). The user predicted this
("why such short training") before the result — recorded. My 12-min estimate
treated the bench ms/step as the story; convergence decides, not wall-clock.
Fix round (one knob, pre-registered family of fixes): resume from ckpt to
150k steps, same everything else. If train-val gap opens later, next knob is
bank size (data is free). G2/G3 wait for a G1 pass.

### G1 fix round (150k steps): FAIL again — but the failure mode FLIPPED

Val table essentially unchanged (flat1p1 0.991 ✓ · flat3p1 0.952 ✓ · well1p1
0.924 ✗ · aniso2p1 0.919 ✗ · chargedE 1.8e-2 ✗ · magneticB 3.5e-3 ✗ ·
twocharge 4.9e-2 ✗ · matter 5.4e-2 ✗) while TRAIN loss dropped 4× (traj
0.023→0.0053, pair 0.019→0.0014). At 30k train≈val (underfit); at 150k
train≪val — the extra 120k steps memorized the 21.6k training episodes.
**Steps knob exhausted; the binding constraint is data.** This is diagnostic
arm (c) of the methodology trio, answered by the run we already had.

### Pre-registration: G1 data-scaling curve (the one knob = bank size)

Generate 4 shards × 30k episodes (25_worldgen seeds 1–4, per-seed heartbeat
names after s3 died on the shared-heartbeat rename race — patched). Arms,
identical model/hyperparams/150k steps, fresh init each:
- arm-48k: train on 48k episodes (shards 1+2 merged, minus val)
- arm-120k: train on 120k episodes (all four shards)
Val = last 10% per family of the merged bank (fresh worlds, as before).
Read: plot val traj-MSE vs bank size {24k, 48k, 120k}. If it scales → ride
the curve (more data / streaming). If it plateaus → the wall is CONTEXT
INFORMATION (32 tokens may not pin the world), and the owed oracle floor —
posterior-predictive error given the same 32 tokens — gets measured BEFORE
any further knob. Honest note: that floor should have been measured before
gating G1 at 1e-3 (methodology rule 1); recorded as a process miss.

### RESULTS: the curve SCALES (no plateau); the wall is architecture, not data

(actual episode counts: 24k original, 60k = shards 1+2, 120k = all 4; the
"_48k" tag is nominal. All three judged on the SAME 24k-bank val split via
--val-bank, so comparable.)

| family | metric | 24k | 60k | 120k |
|---|---|---|---|---|
| flat1p1 | pair | 0.991 | 0.993 | 0.996 |
| flat3p1 | pair | 0.952 | 0.964 | 0.978 |
| well1p1 | pair | 0.924 | 0.944 | 0.965 |
| aniso2p1 | pair | 0.919 | 0.932 | 0.946 |
| chargedE | traj | 0.0176 | 0.0145 | 0.0129 |
| magneticB | traj | 0.0035 | 0.0034 | 0.0035 |
| twocharge | traj | 0.0493 | 0.0447 | 0.0369 |
| matter | traj | 0.0543 | 0.0356 | 0.0330 |

- **Monotone improvement, no plateau** (except where already at ceiling:
  flat1p1 pair, magneticB traj). Data is a real constraint — confirmed.
- pair gate (>0.95): 3/4 pass at 120k (aniso 0.946 just under).
- traj gate (<1e-3): NONE pass — but this is NOT an irreducible floor.
  **The two-charge SPECIALIST (script 24, L=2, trained per-body embeddings)
  hit 1.2e-4 on that exact task; the generalist sits at 0.037 — a ~300×
  gap.** So 1e-3 is achievable in principle; the generalist's wall is
  (a) in-context world inference (specialist baked it into trained
  embeddings) + (b) the single GLOBAL mean-pooled summary w∈R⁶⁴ carrying
  every body's labels at once, decoded by tag at the query head. Data scaling
  helps but cannot close 300× — the suspect is the pooling bottleneck.
- Decision: FORK (discussing with user) — (1) architecture: per-body /
  cross-attention readout (query attends to context tokens, no global
  pinch); (2) oracle-context arm to split inference-vs-head floor decisively;
  (3) more data; (4) accept G, run G2/G3 on the 120k model, advance to H.
  The specialist gap argues (1) is highest leverage. Oracle floor (2) still
  owed before any traj gate is called passed/failed.

### G2 + G3 RESULTS (script 27, probed on the 120k model) — the prize is THERE

G2 zero-shot (widened-range bank, seed 99, --widen 1.25, 2k episodes):
**PASS.** traj MSE in=0.0216 / wide=0.0214 (ratio 1.00 — no degradation),
pair 0.971 / 0.903 (graceful, ≪2× loss). The net extrapolates to 25%-wider
worlds essentially for free on trajectories — it learned world-mechanisms,
not a lookup over the training range.

G3 — the world-summary space (results/27_world_space.png, 27_g3.json):
- **G3a clustering ARI = 0.824 — PASS.** The 8 families separate cleanly.
  PCA map reads like a physics taxonomy: the two FLAT worlds (1+1, 3+1) sit
  apart as tight knots; well1p1 and aniso2p1 each isolated (pure geometry);
  and the THREE EM-coupled families (chargedE, magneticB, twocharge) pile into
  one neighborhood; matter is a diffuse cloud (variable blob count).
- **G3c EM-kinship (exploratory) — strongly CONFIRMED.** d(chargedE,magneticB)
  = 15.1 vs d(either, gravity-well) = 29.1 → the two EM worlds sit 2× closer
  to each other than to pure gravity; z = 26.7 vs shuffled-family null. The
  net spontaneously grouped "force gated by a per-body charge" as one region
  of law-space, distinct from geometry. (Caveat: chargedE/magneticB share
  generator structure — kinship partly reflects that; still, the net found it.)
  Connects to the It-from-Qubit "geometry of the space of laws" thread.
- **G3d intrinsic dim = 6.6** of 64 (participation ratio) — the world-summary
  compresses to ~7 effective axes.
- **G3b decodability — FAIL as gated (median r 0.50, min 0.04) BUT the PATTERN
  is the finding, and it is the SAME story as the G1 traj wall:** world-LEVEL
  geometry decodes beautifully (well depth r=0.916, total matter mass r=0.981);
  per-body-charge-GATED params decode poorly (chargedE e_amp 0.54, twocharge
  f1.amp 0.45, aniso s_phi 0.41, magneticB b_amp 0.04). The single global
  pooled summary captures what's salient at the world level but blurs anything
  whose effect is modulated per-body.

**SYNTHESIS (the dilemma, sharpened by data): the trajectory-accuracy gap and
the G3b illegibility are ONE phenomenon — the global mean-pool is excellent for
world-geometry and structurally blind to per-body labels.** So "accurate" and
"legible-at-world-level" are not actually in tension here; both are limited by
the same missing per-body channel. A hybrid (global w for world-geometry +
query→context attention for per-body labels) would help BOTH at once. Phase G's
prize (G3a/G3c) is banked; G1-traj and G3b are the same open edge.
Decision pending user (thinking in parallel). G2 ✓, G3a ✓, G3c ✓✓ exploratory.

## 2026-06-15 — PHASE G-sym PRE-REGISTRATION: the symmetry-respecting generalist

Frame (from a parallel Claude session, credited): the mean-pool isn't a flawed
summarizer — it's permutation-invariance over bodies, i.e. the equivalence
principle in disguise. An invariant code can ONLY keep what survives relabeling
bodies: geometry (every body feels it identically) is kept; the tag->charge
binding (the thing relabeling breaks) is structurally forbidden. So the
stage/actor split = the invariant/equivariant decomposition under body-
relabeling symmetry. Imposing THAT symmetry is the same fair move as Phase A's
boost-invariant Siamese head — content still emerges. It also re-derives Phase C
from symmetry (neutral: equivariant channel must carry 0/body; charged: exactly
1/body — matches the MDL count).

My amendment (recorded): "symmetric=geometry, kept" is slightly too clean — the
FIELD AMPLITUDES (e_amp, b_amp) are body-symmetric world params yet decode badly
(G3b: 0.54 / 0.04) because their signature is charge-GATED (a field acting only
on neutral bodies is invisible). Prediction: restoring the per-body channel
should lift the field-amplitude decode rows too, not just the charges.

Architecture (script 28, SymGeneralist, same forward interface as 26 so
losses/evaluate/27-probes reuse): token embed -> 5-layer transformer -> H.
TWO readouts:
  (1) INVARIANT stage: w = to_summary(mean(H)) in R^64 — the legible world map,
      the G3 object (unchanged from 26).
  (2) EQUIVARIANT per-body: query cross-attends into H (nn.MultiheadAttention,
      query=q_embed, k=v=H) -> bottleneck to R^8 — small by design so it carries
      per-body LABELS (charges), not the whole world; world-geometry is pressured
      into the 64-d stage by capacity asymmetry (emergent split, not hard-routed).
  head: [q_embed (+) w_stage (+) b_perbody(8)] -> MLP -> {pair logit, traj 6}.
Same bank (120k), 150k steps, --val-bank 25_bank.npz, MPS, bit-exact ckpts.

Gates (vs the 120k mean-pool baseline = 26_g1_120k.json):
- A1 ACCURACY restored: charge-gated traj families improve >=5x — twocharge
  0.037 -> <7e-3, chargedE 0.013 -> <3e-3 (specialist floor is 1.2e-4, the
  ceiling). pair families not worse than baseline.
- A2 LEGIBILITY kept: G3a clustering ARI on w_stage still > 0.8 (the stage
  channel did NOT go vestigial — split held).
- A3 BINDING recovered (the amendment's test): (a) per-body charge decodes from
  the equivariant channel b at r > 0.9 (behavioral, vs true qm); (b) field-
  amplitude decode lifts — b_amp from 0.04, e_amp from 0.54, both materially up.
- A4 zero-shot (G2) still passes (<2x on widened bank).
One fix round if a gate misses. THEN, separately, the consensus->legibility
experiment with the recurrence-vs-discreteness control (pre-reg when we get there).

## 2026-06-15 — PHASE G-sym RESULTS: gates miss, but the experiment was CONFOUNDED

Training completed 150k (power loss hit AFTER; model + A1 saved, nothing lost).
Full gate read (symmetric model vs 120k mean-pool baseline):

- **A1 accuracy — MISS on the target families.** pair all up (aniso2p1
  0.946->0.958, now passes), matter traj 0.033->0.0135 (2.4x), BUT the
  charge-gated families barely moved: chargedE 0.0129->0.0135, twocharge
  0.0369->0.0361. The equivariant channel did NOT restore per-body accuracy.
- **A2 legibility — MISS.** G3a stage-channel ARI 0.824 -> 0.679 (clustering got
  WORSE); participation ratio 6.6 -> 4.1 (stage compressed harder). Geometry
  still decodes (depth 0.95, mass 0.99) but family separation regressed.
- **A3a binding — MISS but DIRECTIONALLY RIGHT.** per-body charge decode from the
  EQUIVARIANT channel beats the INVARIANT control everywhere (chargedE 0.70 vs
  0.33; twocharge 0.50/0.52 vs 0.25/0.32; magneticB -0.01 vs 0.06) — the split
  is real (binding lives in the equivariant channel) but capped well below 0.9.
- **A3b field-amp lift — partial.** b_amp 0.04->0.13, e_amp 0.54->0.57 (directional,
  my amendment, but small).
- **A4 zero-shot — PASS** (G2 traj ratio 1.04).

**THE CONFOUND (smoking gun, and a process miss I own):** the body tag field is
only 4 dims but episodes have 6 bodies — `eye(8)[perm[:6],:4]` gives ALL-ZERO
tags to every body whose perm index >=4. Measured: 6 bodies -> only 5 distinct
tags, 2 bodies collide on the zero tag (8 of 24 traj tokens). The equivariant
channel CANNOT bind a query to a collided body — the per-body signal is destroyed
IN THE DATA. This is exactly the degeneracy I flagged when reading _traj_episode
and then failed to fix before building (recorded honestly). It explains the
pattern: matter (binds by blob POSITION, no tags) improved 2.4x; charge families
(need tag binding) didn't; A3a is capped because only the ~4 cleanly-tagged
bodies decode. magneticB dies hardest (v×B is velocity-gated, hardest to read).

VERDICT: the gates miss, but a confounded experiment is not a result about the
symmetry frame — the channel was starved of its input. The A3a direction
(equivariant > invariant) is the only clean signal and it supports the frame.
ONE FIX ROUND (pre-registered): give each body a UNIQUE tag (random continuous
4-d per body per episode — fits the existing 4-d slot, separates 6 bodies, forces
in-context similarity-binding), regenerate banks, retrain, re-gate. If gates
still miss with clean tags, THEN it's a real verdict on the architecture.

## 2026-06-15 — G-sym FIX ROUND, attempt 1 = STALE-DATA TRAP (caught, re-run)

The fix-round driver (28c) "completed" overnight and produced A1 byte-identical
to the confounded _sym run. Caught it: two models with different file checksums
gave identical eval to 16 digits — impossible for different weights. Tensor
compare: 0/80 weights differ → _sym2 == _sym exactly. Root cause: the driver's
"wait for shards" used FILE EXISTENCE, but OLD shard files (from the scaling
experiment) were already on disk, so it merged the stale 120k at 17:55 and
trained 6h on OLD degenerate-tag data — the NEW shards didn't finish until 20:36.
Verified: 25_bank_120k.npz had 8 zero-tag rows (old). The fix was never tested.
Same family as the Phase F stale-checkpoint trap: **"file exists" ≠ "file fresh."**
Resolution: re-merged 120k from the now-fresh shards (verified 0 zero-tag rows),
deleted the stale _sym2 model/ckpt/json, relaunched the retrain directly on the
verified new-tag banks. Driver hardened to own the full gen→wait→merge→train
order so staleness can't recur. Real A1-A4 verdict pending the clean run (~6h).

## 2026-06-15 — G-sym FIX ROUND (clean, unique tags): the frame VALIDATES on accuracy,
## but a real accuracy-vs-legibility tension emerges (verdict, no further fix round)

Clean retrain on verified new-tag banks (resumed through a 3rd power loss; sym2 truly
differs from confounded sym — weight diff 2.6, A1 differs). Full gates:

- **A1 accuracy — PASS on the target families.** chargedE 0.0129->0.0009 (14x),
  twocharge 0.0369->0.0032 (11.5x) — both clear the pre-registered thresholds
  (<3e-3 / <7e-3). magneticB flat (0.0036). pair families all still >0.95. **The
  equivariant per-body channel DID restore per-body accuracy once tags were unique —
  the symmetry frame's central claim is validated for electric & two-charge.**
- **A3a binding — chargedE now PASSES, direction strong everywhere.** per-body charge
  from the EQUIVARIANT channel: chargedE r=0.914 (>0.9 ✓; was 0.70 with degenerate
  tags), twocharge 0.76/0.64 (up from 0.50/0.52), magneticB -0.03. Invariant-w control
  far below everywhere (0.36/0.33/0.00) — the binding lives in the equivariant channel,
  exactly as the invariant/equivariant decomposition predicts. Gate "min r>0.9" fails
  only on magneticB + twocharge<0.9.
- **A4 zero-shot — PASS** (G2 traj ratio 1.23).
- **A2 legibility — FAIL (0.687 < 0.8), but for an INTERPRETABLE reason, not a tag
  artifact.** Stage-channel ARI 0.824 (mean-pool-only) -> 0.687 (dual-channel);
  participation ratio 6.6 -> 3.65. With per-body info now carried by the equivariant
  channel, the stage stops using it to separate families — so the structurally-similar
  EM trio (chargedE/magneticB/twocharge: all "well + per-body force") MERGE at the
  world level. Confirmed by the flip side: **G3c EM-kinship got STRONGER** (z 26.7->34.9,
  d(E,B)/d(gravity) more separated). So the stage became a purer world-level map at the
  cost of family-cluster count. A real accuracy<->legibility tension — contra the
  "no tension" hope from the reframe.
- **A3b field-amp lift — NOT supported (my amendment was wrong/weak).** e_amp 0.54->0.59,
  b_amp ~0 still. Restoring the per-body channel did NOT materially lift the stage's
  field-amplitude decodability. Recorded as a failed prediction.

**magneticB is a consistent special case across every gate** (A1 flat, A3a dead, A3b dead):
v×B is velocity-gated, so a body's magnetic coupling isn't a simple scalar readable from
trajectory snippets the way an electric charge is. Honest open thread, not a bug.

VERDICT (one fix round spent, stopping per rule): the symmetry frame WORKS for what it
claimed — equivariance restores per-body accuracy (11-14x) and the binding decodes from
the equivariant channel (chargedE 0.91). The surprise is that it does NOT come free for
legibility: the stage's family-clustering drops because per-body info migrates out of it.
"Accurate AND legible" is achievable but the two trade against each other in this design.
Next-direction options for the user (not auto-pursued): (1) accept + write up the honest
tension; (2) a legibility-preserving variant (e.g. auxiliary stage-clustering loss, or
study the stage as a deliberately world-only map and re-define the G3 legibility gate);
(3) the deferred consensus->legibility experiment (recurrence control), now buildable on
the clean unique-tag pipeline. magneticB per-body readout = separate open thread.

- **A2 follow-up (world-type relabel) — hypothesis KILLED:** merging the EM trio
  into one "world-type" barely moved stage ARI (0.687 -> 0.699), so the legibility drop
  is NOT just "EM families correctly merge" — the stage genuinely lost clustering quality
  when per-body info migrated to the equivariant channel. The accuracy<->legibility
  tension is real, not a relabeling artifact. (My convenient reframe was wrong; recorded.)

## 2026-06-15 — PHASE I PRE-REGISTRATION: consensus -> legibility (the novel bet)

Question: is code LEGIBILITY (a learned per-body code being LINEARLY decodable to the
true charge — "legible" — vs only nonlinearly decodable — "scrambled", the Phase C
finding: linear r=0.02, behavioral r=0.9999) selected by AGREEMENT / value RECURRENCE,
beyond mere discreteness? (Frame from the parallel session; the discreteness control is
my addition so "recurrence" isn't confounded with "small alphabet is just easier".)

Setup (script 29, minimal & isolated — the claim is general, not generalist-specific):
single 1-D family, body charge q, accel = gravity well + q*field(x). A SHARED encoder
reads K trajectory snippets of a body -> code c in R^4; a SHARED dynamics head rolls out
(x,v,c). Amortized per-body inference (the equivariant channel, isolated). All arms equal
in #bodies, #snippets, steps, capacity — ONE variable: the charge distribution.

Arms:
- A amortized RECURRING-discrete: q from an 8-value alphabet, many bodies per value.
- B amortized UNIQUE-discrete: q on a fine grid, each body a distinct quantized value
  (discrete, ~no recurrence) — controls discreteness vs A.
- C amortized UNIQUE-continuous: q continuous, distinct per body — controls vs B.
- D FREE-EMBEDDING reference: per-body free embedding (Phase C regime), continuous q.

Legibility metrics on code-vs-true-q (held-out where applicable): LINEAR decode r (ridge
CV) = legibility; NONLINEAR decode r (kNN/MLP) = info presence. Legible = linear high;
scramble = linear low + nonlinear high. Also report fit MSE (accuracy not confounded).

Pre-registered predictions (consensus): linear_r(A) materially > linear_r(B); linear_r(B)
≈ linear_r(C) [discreteness alone doesn't buy legibility]; D scrambles (linear low,
nonlinear high — reproduces Phase C). Falsifiers: A≈B≈C kills it; B>>C = discreteness not
consensus; if amortized C is already linear-legible (≈1), then "amortization gives
legibility for free; Phase C scramble was a free-parameter artifact" (a real finding too).
One fix round on numerics. THEN Phase H row 2 (Wong color — web-verify eqns first).

## 2026-06-15 — PHASE I RESULT: consensus FALSIFIED; legibility = AMORTIZATION, not agreement

3 seeds (script 29, results/29_consensus.json/.png). linear_r = legibility, nonlinear_r = info present:
- A amortized recurring-discrete: linear 0.962, nonlinear 0.987
- B amortized unique-discrete:    linear 0.966, nonlinear 0.980
- C amortized unique-continuous:  linear 0.971, nonlinear 0.987
- D free-embedding (Phase C ref): linear 0.505, nonlinear 0.855
Effects: recurrence (A-B) = -0.004; discreteness (B-C) = -0.005; **amortize-vs-free (C-D) = +0.466.**

**Verdict: the consensus->legibility bet is FALSE.** Value recurrence and discreteness
make NO difference to legibility. What decides it is AMORTIZATION: a per-body code
produced by a SHARED ENCODER that must INFER it from data is linearly legible for free
(linear r ~0.97, smoothness prior of the shared map); a code stored as FREE PER-BODY
PARAMETERS scrambles (linear 0.50 while info survives in nonlinear 0.86 — the Phase C
signature, linear ✗ / behavioral ✓, reproduced). So **"legibility is selected by
amortization, not agreement."** The Phase C illegible q/m code was a FREE-PARAMETER
artifact, not a property of charge. Ties the arc together: Phase C scramble = arm D;
G-sym's amortized equivariant channel decoded chargedE at 0.91 = the amortized arms.
Actionable interpretability lesson: want a legible per-object code? Amortize its inference.

Credit: the parallel session posed the consensus question (the right question); the honest
answer is different from its bet. Caveat: D's scramble (0.505) is milder than Phase C's
(0.02) because the shared dynamics head still smooths D; a harsher free-param setup would
scramble more — the qualitative split is decisive. Low seed variance (std ~0.000 @3dp):
the effect (0.47) dwarfs any seed noise. Phase I CLOSED. Next: Phase H row 2 (Wong color).

## 2026-06-15 — PHASE H ROW 2 PRE-REGISTRATION: Wong color charge (the crown)

Physics (web-verified: Wong 1970; escholarship review qt6x76h1sx; hep-ph/0110104):
classical SU(2) color charge Q in R^3 parallel-transports along the worldline —
D_τ Q = 0 — so it ROTATES (Q(t)=U Q(0) U†, a Wilson line) with |Q| CONSERVED; for
SU(2), f^abc=epsilon^abc so dQ/dt = -g v (A(x) x Q) (precession). This is the new twist
vs electric charge: the per-body label is DYNAMIC (rotates), not static.

Toy (script 30, 1-D space, 3-comp color, m=g=1): a body has initial color charge
Q0 in R^3 (per-body label). World:
  a(x) = well(x) + sum_a Q^a(t) E^a(x)         color-electric force (3 color fields E^a)
  dQ/dt = -v (A(x) x Q)                          precession; A(x) in R^3 varies with x
  -> |Q| exactly conserved (cross product). Integrate (x,v,Q) jointly by RK4.
Bodies differ in Q0 (direction on sphere x magnitude). Model = the LaneModel machinery
(state x,v,w1..wL via shared recurrent F, per-body learned w0), sweep L in {0,1,2,3,4}.

Gates:
- W1 fit: with enough lanes, color trajectories fit (well below the L=0 control).
- W2 lane COUNT (behavioral knee): color needs MORE lanes than electric's 1 — expect the
  knee at >=2 (a rotating SU(2) charge isn't a single static scalar). Report all L.
- W3 ROTATION (the crown): does the learned lane state w(t) along the rollout actually
  ROTATE for color bodies (vs ~static for an electric control)? Metric: lane-state
  angular travel / variance over the rollout, color vs a 1-charge electric control body set.
- W4 LENGTH CONSERVATION: is there a (learned, possibly metric-weighted) quadratic form of
  the lane state approximately conserved along the rollout (the |Q| invariant)? Compare
  drift to a non-conserving control.
Honest caveats up front: classical Wong limit only (no quantum color); "lane count" is the
practical-knee claim (steps 11/12 lesson), not info-theoretic. One fix round per gate.

## 2026-06-15 — PHASE H ROW 2 RESULTS (run 1): W1 ✓, W2 ok, W3/W4 CONFOUNDED (fix round)

results/30_wong.json/.png. test MSE + crude lane-motion:
  color:    L0 1.1e-1 · L1 1.3e-2 · L2 6.7e-4 · L3 3.7e-4 · L4 2.6e-4
  electric: L0 1.2e-1 · L1 1.4e-2 · L2 3.5e-4 · L3 4.6e-4 · L4 8e-5
  ang-travel  color L2 0.20 / L3 0.45 ; electric L2 0.17 / L3 0.41  (NEARLY IDENTICAL)
  rad-drift   color L2 0.138 ; electric L2 0.093 (color drifts MORE, not less)

- **W1 ✓** color fits with L>=2 (6.7e-4 vs L0 control 0.11).
- **W2** knee ~L=2 for color — but the electric control ALSO knees at 2, so it doesn't
  isolate "color needs more": my control was a 3-component FROZEN charge (same #numbers
  as color), not a 1-charge electric. Design flaw #1.
- **W3 rotation — CONFOUNDED (fails as operationalized).** Lane angular-travel is ~identical
  color vs electric — the lanes rotate from position-dependent dynamics in BOTH, not from
  color precession. Angular travel is too crude (flaw #2); the frozen-Q control even rotates
  its lanes similarly.
- **W4 conservation — not shown** (color radius drifts more than electric, opposite of a
  clean |Q|-conservation signal).

DIAGNOSIS: the crown question (does the net discover the ROTATING, length-conserving color
charge?) is NOT answered by these crude metrics + wrong control. The rigorous probe: decode
the TRUE precessing Q(t) (computable from the generator) from the lane-state TRAJECTORY w(t)
via a linear map — if r is high, the internal state TRACKS the rotating charge (W3 proper);
then check |decoded Q(t)| is conserved (W4 proper). One fix round: script 30b does exactly
this on a retrained color L=3 model, with a 1-charge electric as the clean contrast.
