# PRE-REGISTRATION — locating J5's criticality wall (ξ\*)

**Frozen before the sweep script exists and before any number is produced.** Committed first, deliberately, so
its git timestamp precedes the result. TheBridge states that `../quantum` filed a sealed prediction for this
sweep in their own repo on 2026-09-05, before my instrument ran, and did not send it. **I have not read it and
will not look.** I have read access to that repository; not using it is the whole point. Leg 3 died because the
party administering the blinding spent it in the sentence announcing it (`silent_nulls` 50) — the failure mode
here would be mine alone and entirely avoidable.

## What is wrong with the gate today

§42's E2 reads: gapped chain → `R_CoV = 5.56` vs critical `0.0013`, pass. **That is a boolean** — *constancy
holds at criticality and fails when gapped* — in a project where every other certify verdict now reports a
location: `d* = 6` (§176), `K* = 3` and `r* = 3.6` (§177), *no invariant below degree 5* (§178).

> **A gate that can fail, and passes, has still not been characterised.** E2 says *that* constancy fails and
> never *where*.

I missed it for three months because E2 **passes**, and I had been auditing verdicts that certify rather than
controls that pass.

## The system, unchanged from §42 on purpose

`N = 512`, band `l ∈ [16, 176]` even, staggered mass `±m` (gap `2m`), `R(l) = Ω(l)·(N/π)²·sin²(πl/N)`,
statistic `R_CoV = std(R)/|mean(R)|` — the *same* `omega`, `R_const` and `cov` functions §42 already uses.
**Nothing about the instrument is re-tuned.** Changing N or the band would confound the location with a
re-tuning, and the object of this run is to locate the wall of *the gate that already exists*.

## Frozen choices

1. **Mass grid.** `m = 0` (critical baseline) plus 24 log-spaced points `m ∈ [1e-4, 0.5]`. The upper end
   reproduces §42's existing gapped point; the lower end pushes ξ past the box.
2. **ξ is MEASURED, never assumed.** The textbook relation is `ξ ~ 1/gap = 1/(2m)`, and I am not using it as
   the x-axis. ξ is fitted from the exponential decay of the correlation envelope `|C(r)|` on the same chain
   whose entropy is being read. **Both the measured ξ and `1/(2m)` are reported**, so any divergence between
   them is visible rather than absorbed. *Touch the state; do not reason about it.*
3. **The wall.** `ξ* = ξ at which R_CoV first crosses 3× the critical baseline`, interpolated on the log-ξ
   axis. The factor 3 is **not chosen now** — it is E2's own existing threshold (`cov_Rg > 3 * cov_Rc`, §42
   line 157). This run locates the boundary of the gate as written; inventing a new threshold would make the
   location an artifact of this run's taste.
4. **THE RATIO IS NOT COLLAPSED.** ξ\* is reported as `ξ*/N`, `ξ*/l_min` and `ξ*/l_max` **separately, never as
   one number.** The regime condition is `l ≪ ξ ≪ N` — *two* conditions on *different* lengths, which fail
   independently. Quantum's own withdrawal of their ξ/L threshold is the reason this clause exists: their
   chain had one length besides ξ, so a single ratio conflated "region ≪ ξ" with "ξ ≪ box". Mine has both, so
   there is no excuse for reporting one number.

## Known-fail control (L1) — binding

The sweep must reproduce **both** §42 endpoints on the same code path: critical `R_CoV ≈ 0.0013` and `m = 0.5`
→ `R_CoV ≈ 5.56`, each within 20%. **If either endpoint is missed, the instrument is broken, no ξ\* is issued,
and that is the reported result.** A sweep that cannot recover the two points it is interpolating between has
not earned the right to interpolate.

## Censoring guard (entry 19 / §177 W3)

If the crossing lies at the **boundary** of the swept range rather than inside it, the statistic is censored:
**ABSTAIN, report a bound, and widen the grid** — do not report an edge value as a location. Fraction of grid
points pinned at an extreme is checked first.

## What would make me re-examine the INSTRUMENT rather than the physics

Stated now, so it cannot be decided after seeing the number:

- **Either endpoint not reproduced** (above) → instrument, no verdict.
- **`R_CoV` non-monotone in ξ** → instrument *first*. It becomes a physics claim only if the non-monotonicity
  tracks `ξ/N` crossing 1, which is the box condition biting independently of the region condition — and that
  must be shown, not asserted.
- **Crossing at the edge of the grid** → censored, abstain, widen.
- **Measured ξ disagreeing with `1/(2m)` by more than 3× in the regime where they should agree (`ξ ≪ N`)** →
  the ξ fit is broken, not the physics.

## What this run cannot establish

`R_CoV` rising is the *geometry* degenerating, which is what E2 already asserts. Locating it does **not** show
that a central charge read off that geometry inherits a universality condition — that is a further claim and
this sweep does not test it. The c-from-curvature number in §42 is read at exact criticality using the
finite-size chord form, and nothing here changes its status.

**Frozen. Next commit in this file's history that touches the result is the result.**

---

# RESULT (appended 2026-09-21, after the run; nothing above this line was edited)

**SPLIT VERDICT: located in mass, ABSTAIN in ξ.**

    L1 known-fail control:  critical R_CoV 0.0012985 (want ~0.0013)  OK
                            gapped  R_CoV 5.5566    (want ~5.56)    OK
    R_CoV monotone in ξ:    yes
    threshold (3× critical): 0.0038955

    m*  = 1.467e-4          LOCATED   (interior crossing, control parameter, not inferred)
    ξ*  = 3947 sites        ABSTAIN   (= 7.71 × the box)

**The mass axis is clean.** Both §42 endpoints reproduce on this code path, `R_CoV` is monotone across four
decades of mass, the crossing is interior, and it lands on a parameter I *set* rather than one I *infer*.

**The ξ axis is not.** The correlation length is fitted from the decay envelope over `r ≤ N/4 = 128`. At the
crossing, ξ ≈ 3947, so the envelope decays by **3.2% across the entire fit window** (fit r² 0.81). A
correlation length extracted from an essentially flat curve is not a measurement, and 7 of 24 grid points sit
above ξ = N. So `ξ*/N = 7.71` is reported as a **bound on nothing useful**, not a location.

## What that actually says, which is more interesting than the number I went looking for

`R_CoV` departs the critical baseline **while ξ is still far outside the box.** At the wall of this gate the
condition `ξ ≪ N` is already violated — so **E2's boundary cannot be written as a ξ/N ratio on this system at
all.** The two conditions (`l ≪ ξ` and `ξ ≪ N`) do not merely fail independently here, which was the
anticipated subtlety; the second is *already broken where the gate fires*. Any single-ratio statement of this
wall — mine or anyone's — would have been a number with no measurement under it.

The gate itself is unharmed: E2 asserts the geometry degenerates when gapped, and it does, monotonically, from
m ≈ 1.5e-4 upward. What changes is that its wall is now quotable **in mass** and known to be **unquotable in
ξ**, with the reason measured rather than argued.

## Deviation from the frozen text, recorded not folded in

The pre-registration named *"the ξ fit is broken"* as an instrument-re-examination trigger and wrote the
censoring guard for **the crossing landing at the grid edge**. It did not anticipate **the x-axis itself going
unmeasurable at an interior crossing** — the crossing here is comfortably inside the swept range and the ξ
value is still meaningless. The guard added after the first run (`decay across the fit window > 50%`) is a new
clause, added with the result already visible, and is flagged as such rather than presented as foreseen.
**The threshold was not moved and the mass result is exactly what the frozen procedure produced.**

## Still not consulted

`../quantum`'s sealed prediction, which TheBridge confirms was filed 2026-09-05 before this instrument ran.
I have read access to that repository and have not looked, before or after producing these numbers.

---

# SETUP CORRESPONDENCE (appended 2026-09-21, read off committed code — not reconstructed)

Requested by TheBridge for cross-repo comparability, after the run. **Every item below is quoted from the
committed source, not recalled** — `187_xistar_located.py` and `42_curvature_from_entanglement.py` are in git
and each line is cited. The warning that reconstructions in this family have a bad record is correct; this is
not one, and that distinction is the reason it can still be trusted post-hoc.

| item | this run |
|---|---|
| **interval scaling** | **ABSOLUTE lattice sites at a single L.** `LS = arange(16, 177, 2)`, `N = 512` fixed. Mass is swept; the band is never rescaled. NOT a fixed fraction of the ring. |
| **block fraction** | consequently **varies across the band**: `l/N` runs 0.03125 → 0.34375 |
| **boundary** | **PERIODIC ring** — `chain_hop(N, periodic=True)`, `chain_hop_gapped(N, m, periodic=True)` |
| **cut count** | **TWO.** The region is one contiguous block `range(N//2 − l//2, N//2 + l//2)` on a ring → two boundary points |
| **CFT form** | **`c/3`**, consistent with two cuts: `S_analytic = (c/3)·ln[(N/π)·sin(πl/N)]` |
| **ξ definition** | **`\|C(r)\| ~ exp(−r/ξ)`**, r in **lattice sites**, even separations only, fitted over `r ∈ [2, N/4)` on the envelope of the single-particle correlation matrix `C_ij = ⟨c_i† c_j⟩`. **Not** from the entropy, **not** from the gap. |
| **statistic** | `R_CoV` aggregated **across the whole band**, so each mass point mixes a range of `l/ξ` |

## The factor of 2, caught by this check, and where it did and did not reach

TheBridge flagged that a factor of 2 in the ξ convention moves everything. It did — in my comparator column.

For `h_{i,i+1} = 1` at half filling, `ε(k) = −2cos k`, so **`v_F = 2`**; with gap `= 2m` the continuum relation
is `ξ = v_F/gap = **1/m**`, not `1/(2m)`. The first version of this script reported `xi_textbook = 1/(2m)` —
**wrong by exactly a factor of 2.** Confirmed from the data rather than from the algebra:

    xi_meas · m    = 0.854, 0.951, 1.071, 1.209, ...   (-> 1 in the clean regime)
    xi_meas · 2m   = 1.708, 1.902, 2.142, 2.418, ...   (-> 2)

> **It never reached `m*`, `ξ*`, or the verdict, because ξ was MEASURED rather than derived.** The frozen
> choice to fit ξ from the correlation envelope instead of assuming `1/(2m)` confined a real convention error
> to a cosmetic column. Had I taken the textbook route the pre-registration offered, the entire x-axis would
> have been off by 2 and nothing in the run would have said so.

Column corrected to `xi_continuum_vF2 = 1/m`, with the wrong one retained as `xi_textbook_WRONG_vF1` rather
than deleted.

## The composite actually being scanned, stated so a mismatch is visible

At the located wall `m* = 1.467e-4`:

    l/ξ  across the band   0.0023 .. 0.026     l ≪ ξ    SATISFIED, deeply
    ξ/N                    13.3                ξ ≪ N    VIOLATED, inverted ~13×

So this run scans **deep in `l ≪ ξ` while `ξ ≪ N` is inverted.** That is the correspondence fact that matters
for any comparison: a prediction framed as a threshold in `ξ/L` for a setup where `ξ ≪ box` holds is **not
describing this regime**, and the honest outcome would be **NOT COMPARABLE** — neither confirmation nor
falsification. It is also, independently, *why* the ξ-axis abstains: the gate fires in a regime where ξ exceeds
the system, and a correlation length larger than the box is not a length this system can report.

## Still not consulted

`../quantum`'s sealed prediction. Not read before the run, not read after, and **I will not ask whether the
number matches** — a peer's interim "close" or "not close" is exactly the channel that would end the blinding.
The comparison belongs in one place, with the correspondence check above done first.

---

# A THIRD SIGNATURE, FOUND BY CHECKING ONE REPORTED NUMBER AGAINST ANOTHER (appended 2026-09-21)

Credit: TheBridge, who verified an arithmetic claim of mine instead of taking it on report — and in doing so
found a diagnostic neither of my two guards uses.

Two independent ξ estimates exist at **every** grid point: the envelope fit, and the corrected continuum
relation `1/m`. Where the axis is measurable they should agree, so their **ratio is a free measurability
check**. Across the sweep:

    ξ/N        derived/measured
    0.007      0.544      deep gapped: ξ ~ a few sites, continuum relation not expected to hold
    0.15       1.051      the two estimates CROSS — agreement sits INSIDE the measurable band
    1.29       1.637
    7.71       1.727      <- the wall
    11.3       1.733      saturating

**The agreement point lies inside the measurable regime and the wall lies where the estimates disagree by
1.73×.** That corroborates the abstention by a route neither the envelope-decay guard nor the `ξ > N` count
uses, and it cost nothing to build — it was already in the results file, unread, as two columns nobody had
divided.

**WHAT IS NOT CLAIMED.** The large-ξ saturation value is **numerically close to √3 = 1.732 and I have no
tested mechanism for that.** A power-law prefactor in `C(r)` biasing a pure-exponential fit is the obvious
suspect, and it is a *guess* — the kind of inference this catalogue records as the unreliable half of the day's
work. Recorded as an **unexplained regularity**, not a finding. It does not enter the verdict, which rests on
the envelope decay (3.2%) and the box violation, both measured.

> **Two estimates of the same quantity are a free instrument, and the cheapest one anybody has: the second
> column was already sitting in the output.** What it took was someone dividing them, and that someone was not
> the author.
