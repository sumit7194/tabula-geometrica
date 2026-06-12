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
| **[writeups/curvature_field_guide.md](writeups/curvature_field_guide.md)** | 🧰 **The workshop version** — every phase A→E + all side quests: setups, mechanisms, numbers, corrections, the recurring patterns (gauge freedom; behavioral > structural probes; universality geometrizes), and the explicit list of **threads never pulled**. The document to think and argue with. |
| **[curvature/](curvature/README.md)** | 🧠 *The main thread (the whole repo now):* can a network **invent spacetime geometry** from raw observations? **Phases A → E all passed** + the Kaluza move (charge → internal coordinate, r = 0.9998) + the Gaussian curvature read out coordinate-free (corr 0.99). Now in **Phase G** (one generalist net across all world families — studying its internal world-summary space) and **Phase H** (which particle-like labels become hidden "lanes": two-charge knee lands at exactly 2). |

> **Black-hole LIGO projects moved out (2026-06-13):** `echoes/` (GW-echo search),
> `ringdown_spectroscopy/` (no-hair test via SBI), and `primordial_blackhole_search/`
> (subsolar-mass merger search) now live in `../BlackHole/`. This repo is the
> neural-network / curvature work only.

## The roadmap

1. ✅ **3+1 vs 2+1** concept map
2. ✅ **1+1 rung + scaling laws + 4+1 extrapolation** (incl. shapes, measures, horizons)
3. ⬜ **Gravity *is* curvature** — mass → Ricci curvature → geodesics that look like
   "falling"; intrinsic vs extrinsic curvature (*Theorema Egregium*)
4. ⬜ **The finale** — "is curvature another dimension?" The intrinsic answer (no), then
   the genuine exception: **Kaluza–Klein**, where adding a real 5th dimension *produces
   electromagnetism*. Saved as the payoff.

## How to read it

Two recurring conventions:
- **`n`** = space dimensions; **`D = n + 1`** = total spacetime dimensions.
- **Verdict tags** when comparing worlds: ✅ clean parity (just fewer/more numbers) ·
  ⚠️ degenerate / vanishes · 🔀 qualitatively different.

Each doc ends with **open threads** — pick one and we extend it. The docs are living
documents.
