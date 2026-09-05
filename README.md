# tabula geometrica — can a network invent spacetime geometry?

*tabula geometrica* — "the geometric blank slate." Train neural networks only on raw
observations — never a metric, an interval, or Einstein's equations — and test whether
**geometry emerges as the cheapest internal explanation.** The live experiments are in
**[curvature/](curvature/README.md)**; the conceptual on-ramp is a step-by-step
**dimensional ladder** (1+1 → 2+1 → 3+1 → 4+1) toward the real question:

> **how gravity curves spacetime — and whether that curvature "is" an extra dimension.**

Every load-bearing claim (numbers, formulas, dimension-dependent facts) is verified
against the literature before it goes in, with sources cited in each doc.

## The docs

| Doc | What's in it |
|---|---|
| **[3plus1_vs_2plus1.md](3plus1_vs_2plus1.md)** | Our world vs *Flatland*, concept by concept: coordinates, rotation (axis vs plane), light cones, the wave "tail," 1/r² → 1/r forces, why 2+1 gravity is hollow, knots, chirality, trapping. |
| **[dimensional_ladder.md](dimensional_ladder.md)** | The **1+1** bottom rung; the **scaling laws** (one master table of features vs dimension); **shapes & measures** (line/square/cube/tesseract; length/area/volume/hypervolume); **black-hole horizons** across the ladder; **extrapolation to 4+1** with new vocabulary; the **bridge to gravity-as-curvature**. |
| **[nn_and_spacetime.md](nn_and_spacetime.md)** | A side-exploration: what *really* connects **neural networks** (embeddings, training, curvature) to spacetime physics. The metric tensor as the shared object; hyperbolic/Lorentz-model embeddings; PINNs; depth-as-emergent-dimension (holography reappearing in ML); the honest category errors; and toy experiments worth building. Confidence-tagged and cited. |
| **[emergent_dimension.md](emergent_dimension.md)** | "Is the extra dimension *real*?" The holographic emergent dimension explained CS-first (mipmap → RG → AdS/CFT → entanglement → Hashimoto's trainable network), the honest "is it real" verdict, and the **three-way contrast** (holographic-emergent vs Kaluza–Klein vs GR-curvature) that frames both finales. Ties `S=A/4` back to the black-hole chat. |
| **[discovering_curvature_with_nn.md](discovering_curvature_with_nn.md)** | The ambitious one: can an NN **discover** that spacetime is curved — unsupervised, from adjacent observables, never told the law? Names the paradigm (SciNet bottleneck), the precedent (a net already discovered the Minkowski interval), the honest feasibility verdict (pure dream impossible; equivalence-principle variant buildable), a concrete 2+1 experiment, and the genuinely novel angle (let the minus sign *emerge*; make geometry-vs-force compete). |
| **[JOURNAL.md](JOURNAL.md)** | 📓 The activity log — one dated entry per working session. |
| **[writeups/emergent_geometry.md](writeups/emergent_geometry.md)** | ⭐ **The shareable note, now complete:** five acts — interval → light cone → gravity well → why gravity geometrizes (0 vs ~10 bits/body) → **the Kaluza ending** (charge migrates into an internal coordinate, r = 0.9998). With methods, failed-probe corrections, and honest limits. Start here. |
| **[writeups/curvature_field_guide.md](writeups/curvature_field_guide.md)** | 🧰 **The workshop version** — every phase A→E + the generalist arc (G/H/I/J) + all side quests: setups, mechanisms, numbers, corrections, recurring patterns, and the explicit list of **threads never pulled**. The document to think and argue with. |
| **[writeups/legibility_law.md](writeups/legibility_law.md)** | 🔑 **The crystallized result** — the project's most novel finding as a standalone, three-part claim: *a learned per-object code is legible when it's **inferred, not stored**; generic evolution re-scrambles it; invariant-preserving structure restores it.* Backed by three controlled experiments; the through-line that explains the whole project. |
| **[writeups/impossibility_certificates.md](writeups/impossibility_certificates.md)** | 🚫 **The negative-space companion:** a network's *failure* to find a cheap explanation, gated against a real theorem, as a positive result. Bell/no-local-code, chaos/no-invariant, gauge/no-unique-law, contextuality — four certificates, one shape. |
| **[writeups/silent_nulls.md](writeups/silent_nulls.md)** | 🕳️ **The methods companion:** nine measured ways a *bug* reads as a *result* — one shape underneath (*wherever "didn't happen" and "happened and found nothing" produce the same output*), each entry an instance we actually hit, with the diagnostic that caught it. Includes the two rules that generalize furthest: **a control that cannot fail is not a control**, and **a threshold tested in one direction only is not tested**. |
| **[writeups/representability_frontier.md](writeups/representability_frontier.md)** | 🗺️ **The unifying theory of the discoverable.** Every wall the project has hit is one of five ways "the cheapest legible code" fails (doesn't exist / isn't unique / isn't globally consistent / isn't linear) — crystallized into a single **discoverability diagnostic** that infers a system's regime from raw data (no labels, no ground truth), abstains honestly when underdetermined, and has been run on real chaotic/regular/ambiguous datasets. |
| **[curvature/](curvature/README.md)** | 🧠 *The main thread (the whole repo now):* can a network **invent spacetime geometry** from raw observations? **Phases A → E all passed** + the full **Kaluza–Klein trilogy** — charge (Phase D, r = 0.9998), mass (a KK cylinder toy, the tower discovered as a quantized ladder), and the axion (a twisted-torus modulus, its modular gauge and hyperbolic moduli-space geometry measured from the net's own learned spectrum) — plus the Gaussian curvature read out coordinate-free (corr 0.99). **Phases G/H/I** — a generalist net's world-summary space clusters into a physics taxonomy (ARI 0.82); which particle labels become hidden "lanes"; the legibility law (amortized codes are legible, free-stored codes scramble). **Phase J** — geometry, curvature, and a holographic (AdS-like) extra dimension recovered from entanglement alone. Since then the project climbed past its own roadmap into **the representability frontier** (a predictive theory of what nets can and cannot discover) and **real-world validation** — a real chaotic laser, tidal records, and ambiguous sunspot data; Newton's constant and Mercury's perihelion precession measured from real JPL ephemerides. Ongoing three-way collaboration with sister projects (see below) has independently cross-checked several of these results. |

> **Black-hole LIGO projects moved out (2026-06-13):** `echoes/` (GW-echo search),
> `ringdown_spectroscopy/` (no-hair test via SBI), and `primordial_blackhole_search/`
> (subsolar-mass merger search) now live in `../BlackHole/`. This repo is the
> neural-network / curvature work only.

## The roadmap

1. ✅ **3+1 vs 2+1** concept map
2. ✅ **1+1 rung + scaling laws + 4+1 extrapolation** (incl. shapes, measures, horizons)
3. ✅ **Gravity *is* curvature** — curvature emerges as the minimal bottleneck code for
   geodesic deviation, and its Gaussian invariant is read out coordinate-free (corr 0.99)
   straight from trajectories, no metric ever shown.
4. ✅ **The finale, and then some** — Kaluza–Klein confirmed as a full trilogy: **charge**
   (Phase D), **mass** (a KK cylinder — the tower discovered as a quantized ladder), and
   **the axion** (a twisted-torus modulus, with its modular gauge and hyperbolic
   moduli-space geometry measured from the net's own learned spectrum).

The original roadmap is complete — the project kept going. It's now past the finale, into
**the representability frontier** (a predictive theory of what a network can and cannot
discover, instrumented as a single diagnostic) and validation against **real data**: a real
chaotic laser, real tidal records, ambiguous real sunspot data, and Newton's constant plus
Mercury's perihelion precession measured from real JPL ephemerides. See `curvature/`,
`writeups/representability_frontier.md`, and `JOURNAL.md` for the current frontier.

## Sister projects

This repo is one of a small constellation of independent projects that periodically
cross-validate each other's results — proving, inferring, or measuring the same claim by
different methods, then comparing notes:

- **[ansatz-machine](https://github.com/sumit7194/ansatz-machine)** — a propose → verify →
  evolve loop hunting exact solutions of Einstein's field equations (genetic programming +
  SymPy proof, not neural).
- **[deepstrain](https://github.com/sumit7194/deepstrain)** — deep-learning searches of real
  LIGO/Virgo data for black-hole signatures (post-merger echoes, ringdown, subsolar mergers).
- **[trivium](https://github.com/sumit7194/trivium)** ("the Bridge") — cross-validates the
  others' results directly; several of this repo's findings (the Kaluza–Klein trilogy, the
  legibility/integrability correlation, the representability frontier) were extended or
  independently confirmed through Bridge rounds.
- **[vestigium](https://github.com/sumit7194/vestigium)** — a verified lab for the quantum
  measurement problem; proposed and cross-checked the Kaluza–Klein mass-discovery experiment
  with this repo.
- **[cuspis](https://github.com/sumit7194/cuspis)** — the entanglement-entropy corner function
  `a(θ)` in 3d conformal field theories: why theories with different content agree on the
  normalised curve, and by how much they do not. Joined 2026-09-05.

Each project stays independent (own code, own gates); only questions and results cross.

## How to read it

Two recurring conventions:
- **`n`** = space dimensions; **`D = n + 1`** = total spacetime dimensions.
- **Verdict tags** when comparing worlds: ✅ clean parity (just fewer/more numbers) ·
  ⚠️ degenerate / vanishes · 🔀 qualitatively different.

Each doc ends with **open threads** — pick one and we extend it. The docs are living
documents.
