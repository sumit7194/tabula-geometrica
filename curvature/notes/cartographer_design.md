# The Cartographer: a generalist discovery network (design proposal, 2026-10-06)

*This is a proposal, not a result. It was written after a four-direction literature sweep: modern LLM
architectures, multimodal and physics foundation models, learning-for-discovery methods, and a prior-art check for
"generalist discovery networks". Nothing has been built or run.*

## The one-line idea

Pretrain one network on a huge procedurally generated **universe of worlds**. Then show it observations of an
**unknown** system, in context, with no retraining. It returns four things:

1. **a law code**, a compact latent;
2. **candidate invariants and equations**, which are checked exactly by our emit-or-certify engine;
3. **a calibrated verdict** on *why* a law can or cannot be found: EMIT / CHAOS / GAUGE / CONTEXTUAL /
   PARTIAL-LEGIBLE / ABSTAIN ("need more data");
4. **the next experiment** worth running to separate the remaining hypotheses.

It is named for what it does: it maps the discoverable. It takes our hand-built 5-cell detector (§141–§150) and
emit-or-certify engine (§91–§99, §166–§178), and amortizes them into one model.

## What the literature says is already done, and what is open

**Done, per piece:**
- **Pretraining on synthetic laws, then inferring in context:**
  - NeSymReS 2106.06427; Kamienny 2204.10532;
  - ODEFormer 2310.05573; FIM-ODE 2510.12650;
  - Panda 2505.13755 (about 20k chaotic systems).
- **Per-system conserved-quantity discovery:**
  - AI Poincaré 2011.04698; ConservNet 2102.04008; Doshi 2511.00102;
  - **Ray 2603.20474 (NGCG)**, which reports zero false discoveries and outputs "no law" on law-free systems.
    *This is the closest prior art to emit-or-certify, and it must be cited and benchmarked against.*
- **Single-purpose verdict classifiers:**
  - chaos: 1908.06848, 2402.12359;
  - integrability: 2402.16244;
  - Bell nonlocality: 1808.07069, 1907.10552.
- **Agentic discovery with experiment design:**
  - AI-Newton 2504.01538; BoxingGym 2501.01540;
  - DiscoverPhysics 2605.26087, where the best agents fail on hidden structure.
- **The template for training only on synthetic worlds:** TabPFN (Nature 637, 2025) and PFNs 2112.10510.

**Open. None of the surveyed work does any of these:**
- (a) A **calibrated multi-way "why no law" verdict**. The GAUGE and CONTEXTUAL cells have no machine-learning
  prior art as verdict categories.
- (b) **No-law, gauge-ambiguous and transcendental-invariant worlds included as labelled classes in pretraining.**
- (c) **Amortized, in-context discovery of conserved quantities.** Every existing invariant method runs per system.
- (d) **A test of whether amortization makes the law code linearly legible.** Our legibility law predicts it does.
  Walrus's SAE features (2606.11657) show the opposite at scale, for a model trained only to predict.
- (e) **An exact certificate verifier inside the loop of an in-context model.**

## Architecture: each block is justified by a paper and by our own results

1. **The world generator** is our unique asset.
   - Most families already exist as scripts in this repo:
     - integrable systems: Kepler, Stäckel/Kerr-like, Toda, KdS, Taub-NUT;
     - non-integrable systems: Hénon–Heiles, ZV, bumped Kerr, Lorenz;
     - gauge-ambiguous worlds: relational distances, the reparametrized metric;
     - contextual worlds: Bell/KCBS/Werner correlation tables;
     - dissipative worlds: friction;
     - transcendental-invariant worlds: §160;
     - quantum worlds: Bloch;
     - field worlds: Phase F/G.
   - The labels come free: the true invariants and the true verdict cell.
   - Following TabPFN, the generator *is* the prior. Following LLM-SRBench, hold out law families the generator
     never shows.
2. **Front end: any observation becomes tokens.**
   - A Perceiver / Universal-Physics-Transformer encoder maps a set of tokens (trajectory samples, correlation-table
     entries, distance-matrix entries) into a fixed latent array. Each token carries a modality tag.
   - Values stay continuous rather than quantized; Transfusion shows continuous values beat VQ tokens.
3. **Core: an amortized fast-weight "law module"** (TTT layers 2407.04620; Titans 2501.00663).
   - Per world, a small network's weights are written by a *shared learned update rule* from the observations.
   - **Those fast weights are the law code.**
   - By the legibility law, an inferred code should be linearly legible. That is the scientific test inside the
     engineering.
4. **A looped refiner** (recurrent depth 2502.05171; TRM 2510.04871). The law hypothesis is iterated to a fixed
   point. More loops means more test-time compute on harder worlds.
5. **Inductive biases taken as given, not rediscovered.**
   - Temporal locality, noisy-context training and continuous regression (Kepler→Newton 2602.06923). Our own Phase
     F / Proca locality finding agrees.
   - A Markovian minimal state, with dimension read off by knee-counting (the Phase A bottleneck lesson).
   - Equivariance as a *switchable arm*, never imposed, so a symmetry can be earned (GATr / Clifford nets as the
     control).
6. **Four heads.**
   - **Prediction:** masked cross-view prediction (4M / JEPA), used only as an auxiliary signal, never as the score.
   - **Invariant proposer:** sparse formulas over a named library, the amortized form of emit-or-certify.
   - **Verdict:** five cells plus ABSTAIN, wrapped in conformal sets. ABSTAIN means the set contains more than one
     cell. This is the principled form of EXP-6.
   - **Experiment chooser:** Deep Adaptive Design (2103.02438) picks the next initial condition or probe with the
     highest expected information gain. It would have flagged leg 6's indistinguishable pair before anything ran.
7. **The verifier in the loop.**
   - Every proposed invariant is checked by our engine on held-out data: exact or not, with C1–C4.
   - That check is an ungameable reward for RL on the proposer, R1/GRPO-style (2501.12948).
   - **The network proposes; the engine disposes.**

## Gates: anti-Vafa by construction

Vafa 2507.06952 showed that good prediction does not mean the law was found.
- **Never score by prediction.** Score by:
  - invariant exactness on held-out data;
  - verdict accuracy *and calibration*;
  - frozen linear probes on the law code (PhyIP 2602.12218);
  - the inductive-bias probe.
- **Held-out law families** the generator never showed, plus synthetic non-textbook laws (the LLM-SRBench lesson).
- **Baselines:** NGCG, ODEFormer, FIM-ODE, and our own per-system engine and §150 detector. The amortized model has
  to approach the per-system engine on its home turf to earn its keep.
- **Legibility:** compare the fast-weight code against a free-embedding baseline. This is the direct test of the
  legibility law at a new scale.

## A milestone ladder, so a failure anywhere is still a result

| step | what | compute | fails informatively if |
|---|---|---|---|
| M0 | Worldgen v2: unify the existing scripts into one labelled generator, including no-law, gauge, contextual and transcendental worlds | Mac, CPU | the labels disagree with our per-system engine |
| M1 | In-context **verdict** model: Perceiver plus verdict head, conformal-calibrated, against the §150 detector | Mac (MPS) | it cannot match the hand-built detector in distribution |
| M2 | Amortized **invariant counting and proposal**, verified by the engine | Mac / L4 | it overclaims on law-free worlds (we measure its false-discovery rate against NGCG's claimed 0) |
| M3 | Fast-weight **law module plus legibility test** | L4 | its fast weights scramble, which would refute or bound the legibility law |
| M4 | **Experiment chooser** (DAD) | L4 | its chosen probes are no better than random |
| M5 | **Unknowns:** the fleet's open targets (deformed-Kerr families, TS-like metrics, mixed KAM systems), real ephemerides | as needed | — |

## Honest risks

- **The generator bounds it.** A "no law" verdict is relative to the training prior. That is why the per-system
  engine stays the final arbiter and the network is the fast triage plus hypothesis source. The network does not
  issue certificates.
- **Identifiability and gauge.** The law code is defined only up to an equivalence class (Locatello; our D-v2). Score
  only gauge-invariant readouts.
- **Mixed phase spaces and sampling.** KAM systems break single labels (EXP-8), so a MIXTURE output is needed.
  Chaos labels depend on sampling (EXP-4/6).
- **Hype.** It will not "discover new physics" by itself. Its realistic value is fast amortized triage plus
  verified proposals, and one clean scientific test: the legibility law at foundation-model scale.
