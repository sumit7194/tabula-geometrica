# Is there chaos around a Tomimatsu–Sato "black hole"? A measured tangle, and why nobody saw it

*Draft, 2026-11-17. tabula-geometrica's half of a possible combined story with ansatz-machine's TS δ=2 chaos work
(its "transient chaos at the capture edge" and Killing-tensor nulls). Joint or separate is Sumit's call. Terminology
is aligned with ansatz; units are stated explicitly (see the box at the end). Everything here is numerical and
non-rigorous unless it says otherwise.*

## The puzzle, in plain words

Some spinning objects in general relativity have orbits so orderly that every orbit is pinned down by a hidden
conserved quantity. Kerr, the standard rotating black hole, is the famous example: its "Carter constant" makes
orbits as predictable as planets. Change the object's shape and that hidden quantity can disappear. Orbits can then
become chaotic, unpredictable in the long run like a double pendulum.

The **Tomimatsu–Sato (TS) δ=2** spacetime is a rotating, deformed relative of Kerr. The evidence pointed both ways:
- **Orderly:** a 2007 study (Dubeibe, Pachón & Sanabria-Gómez) drew orbit "slices" (Poincaré sections) and saw only
  orderly curves, calling the motion "completely integrable".
- **Chaotic:** the mathematics says otherwise. A sister project in this fleet showed by an algebraic theorem
  (Morales–Ramis) that TS has no extra hidden conserved quantity, and ansatz-machine found no Killing tensor up to
  high order.

So either the chaos is somewhere nobody looked, or it is too faint to see. This write-up is about finding *where*
and *how faint*.

## Step 1: looking for a chaotic layer, and not finding one (§198)

In a nearly-orderly system, chaos usually shows up first as thin "layers" squeezed between the orderly orbits, near
resonances (where two orbital rhythms lock into a simple ratio) or near a separatrix (the dividing line between
orbits that stay and orbits that fall in).

We ran an unattended scan: 2,340 orbits in TS and the same number in Kerr as a control, through one code path, at
Dubeibe's own setting and at settings close to the falling-in edge. Each orbit got a chaos indicator (MEGNO) with
thresholds calibrated on Kerr, where chaos is impossible.

**Result: zero chaotic orbits in TS, zero in Kerr.** At our resolution (starting positions about 0.003 apart,
integrations of about 500 orbital periods) there is no layer. That agrees with the 2007 paper *at that resolution*,
and it is NOT a claim that TS is orderly.

**A correction we found afterwards.** We had registered the "near the edge" settings as hugging the separatrix,
where layers are widest. They don't: at those settings the energy is below the top of the barrier, so the
separatrix isn't on that energy surface at all. The scan's result stands; that part of its rationale was wrong and
is withdrawn.

## Step 2: measuring the engine of chaos directly (§199, §199b)

Instead of hunting for chaotic orbits, measure the mechanism that makes them.

At the top of the barrier sits an unstable circular orbit (a "saddle-centre"). Just above that energy, an unstable
periodic orbit (the "Lyapunov orbit") lives there. Two special families of orbits attach to it: those that leave it
(its unstable manifold) and those that arrive at it (its stable manifold).
- **Orderly world (Kerr):** the leaving curve and the arriving curve are the *same* curve, a clean loop.
- **Chaotic world:** they cross at an angle. Each crossing forces infinitely many more, folding phase space into a
  **homoclinic tangle**, the textbook engine of chaos (Smale–Birkhoff).

So the clean question is: in TS, do the two curves cross, and by how much?

**Method in brief.**
- On the slice y = 0 (crossed upward), find the Lyapunov orbit and grow its unstable curve.
- A symmetry of the system (time reversal combined with the equatorial mirror) gives the stable curve for free, as
  the mirror image of the unstable one.
- Find where they meet on the symmetry line, and measure how they cross.
- Kerr, run through the identical code, measures the numerical floor.

**Results** (TS δ=2, p = 3/5, open levels just above the saddle):

| measure | ε = −0.003 | ε = −0.01 | ε = −0.03 | Kerr (floor) |
|---|---|---|---|---|
| crossing angle θ (coordinate-dependent) | 7.9e-4 | 2.5e-3 | 6.9e-3 * | ~2e-6 |
| Lazutkin homoclinic invariant (coordinate-free) | −5.6e-8 | −1.8e-7 | −5.1e-7 | ~1e-9 |
| lobe area / flux (coordinate-free) | 1.4e-6 | 4.5e-6 | 1.2e-5 | ~1e-13 |

\* The ε = −0.03 angle misses its pre-registered bar narrowly (9.5× its floor, 10× required); both coordinate-free
measures pass at all three levels.

- **The curves cross, measurably.** The coordinate-free measures sit 2–8 orders of magnitude above Kerr's floor, and
  they are stable across step sizes and tolerances.
- **The size grows about linearly** with the energy above the saddle. It is not exponentially small, as the classic
  near-integrable theory might have suggested.
- **At the other shape tested (p = 4/5)** the splitting is below our double-precision floor. A high-precision
  follow-up is planned.
- **Independent replication.** The Bridge, with its own code, reproduced the Lazutkin invariant at p = 3/5,
  ε = −0.01, to 0.5% (sign is a convention). The first comparison of *angles* disagreed by a factor 3.3. That turned
  out to be the two codes measuring momenta in different units: the angle depends on units, the invariant doesn't.
  A live demonstration of why coordinate-free measures matter.

## Why nobody saw it: putting the two steps together

The tangle is real but tiny and lives in a narrow place:
- **Region:** it exists only on *open* levels (energy above the barrier top), where orbits near it can also fall in.
  So any chaos it causes is **transient**: an orbit wanders chaotically for a while, then plunges. The 2007 paper's
  orderly slices and our §198 scan were both at *closed* levels.
- **Scale:** the measured lobe area predicts that the tangle's fine structure sits within about one part in a
  million of the separatrix, shrinking roughly 50× per pass. Ordinary sampling, with starting points thousands of
  times further apart, steps straight over it.
- **Ongoing (§200):** zooming in on the separatrix crossing to see whether the escape-time function develops the
  fractal structure a chaotic saddle must produce. Its results are kept blind from ansatz's related capture-edge work
  until the Bridge compares them.

## Honest scope
- All results are numerical (double precision; DOP853 at tolerance 1e-13), not computer-assisted proofs. A rigorous
  (interval-arithmetic) certificate of the crossing would upgrade "numerically transversal" to a theorem.
- One spacetime family (TS δ=2), two shapes, prograde orbits, one energy (E = 0.94).
- The angle θ depends on coordinates and units; only the Lazutkin invariant and the lobe area should be compared
  across codes.

> **Units box.** tabula uses mass units m = 1 with σ = p/2 (the sealed TS2 metric package's convention), prolate
> coordinates (x, y), and a reduced Hamiltonian with shell H = −1/2. ansatz uses σ = 1. Angular momentum and p_x
> differ by a factor σ between the conventions, so raw angles differ by that factor while the invariants agree.

*Sources: notes/ts_layer_scan_prereg.md (§198), notes/separatrix_splitting_prereg.md (§199),
notes/homoclinic_invariant_prereg.md (§199b), notes/tangle_escape_prereg.md (§200); Dubeibe, Pachón &
Sanabria-Gómez 2007, gr-qc/0701065.*
