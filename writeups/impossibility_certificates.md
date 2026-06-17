# Four impossibility certificates a discovery net can issue

*The negative space of the legibility law. Every other result in this project uses a net's **success** at
finding the cheapest explanation as the signal. These three use its **failure** — and turn that failure into
a gated, positive, falsifiable certificate.*

> Scripts: `curvature/scripts/84_bell_nolocal.py`, `85_nolaw_chaos.py`, `86_gauge_nounique.py`.
> All physics web-verified; all gates pre-registered; one fix round each where noted.

## The idea

The project's thesis is that the **cheapest / most shareable explanation wins** — and when many things share
one description, that description becomes geometry. The natural shadow of that thesis is: *what happens when
no cheap explanation exists?* If a net is **architecturally restricted** to a cheap hypothesis class, its
inability to fit the data is not a bug — it is a measurement. It certifies that the structure the net was
forbidden from using is really there.

Three classic "no-go" results of physics turn out to be exactly this, each with a sharp number the net's
failure must land on.

---

## Certificate I — no local code ⇒ quantum nonlocality (Bell)

**Setup.** A genuine **local hidden-variable model**, built as a net: a shared hidden variable `λ ~ p(λ)` and
local response functions `A(a, λ)`, `B(b, λ) ∈ [−1, 1]`, where `A` sees only Alice's setting and `B` only
Bob's — *no cross-wires*. Such a model obeys the CHSH bound `|S| ≤ 2` by construction. It is trained to
reproduce the two-qubit Werner-state correlations `E(a,b) = −v·cos θ_ab` as the visibility `v` rises.

**Result (3/3).** The local net tracks the quantum CHSH value `|S| = 2√2·v` *exactly* — until it saturates at
**|S| = 2.000**, the bound it physically cannot exceed, precisely where the quantum value crosses 2 at
**v = 1/√2 ≈ 0.707**. Above that it is stuck at 2 while quantum sails on to Tsirelson's 2√2 ≈ 2.83.

| v | 0.55 | 0.62 | 0.68 | 0.71 | 0.74 | 0.85 | 1.0 |
|---|---|---|---|---|---|---|---|
| local net \|S\| | 1.56 | 1.76 | 1.93 | 1.98 | 2.00 | 2.00 | **2.00** |
| quantum \|S\| | 1.56 | 1.75 | 1.92 | 2.01 | 2.09 | 2.40 | **2.83** |

**The certificate.** The failure to find a cheap *local* code, at the Tsirelson/CHSH boundary, certifies that
the correlations are nonlocal. (Web-verified: Werner CHSH = 2√2·v; no local model for v > 1/√2; a local model
provably exists below ≈0.66.)

---

## Certificate II — no invariant ⇒ no conservation law (chaos)

**Setup.** A conservation-law finder: a net `g(state) → ℝ`, standardized to unit total variance (so it cannot
collapse to a constant), trained to be **constant along trajectories**. Pointed at two worlds: **Kepler**
(2-body gravity, which has the local invariants energy `E` and angular momentum `L`) and the **chaotic Lorenz
system** (σ=10, ρ=28, β=8/3), web-verified to have *no nontrivial time-independent analytic constant of
motion* — its only known invariants are non-local in time, so a function of the instantaneous state cannot be
one.

**Result (3/3).**
- **Kepler:** the net finds a genuine invariant — along-trajectory variance **0.0000**, diversity ratio
  ρ = **52,000**, and the recovered quantity matches angular momentum to **r = 0.984** (energy to 0.965).
- **Lorenz:** the best unit-variance function *still wanders* — along-trajectory variance **0.445**
  (it cannot be made constant), ρ = **1.26**.

**The certificate.** A low along-trajectory variance is **necessary but not sufficient** for a conserved
quantity; the diversity ratio is the discriminator. The net's inability to find any constant-along-the-flow
function certifies that no local conservation law exists — the same free-vs-amortized lesson from the
legibility law, now in invariant-discovery clothing.

---

## Certificate III — no unique law ⇒ the gauge equivalence class (Lagrangian gauge freedom)

**Setup.** Adding a total time derivative `dF/dt` to a Lagrangian leaves the Euler–Lagrange equations — and
every trajectory — unchanged (Landau–Lifshitz). So the Lagrangian is **non-injective** from trajectory data.
We learn a structured Lagrangian `L = ½q̇² + N(q)q̇ − V(q)`, in which the gauge term `N(q)q̇` provably cancels
in the EOM `q̈ = −V′(q)` (this also sidesteps the Hessian-division blow-up that wrecks a naïve Lagrangian
neural network — the first attempt diverged to R² = −67000; the structured form fixed it). An ensemble of nets
is each nudged a hair toward a *different* total-derivative gauge `N = c·q`.

**Result (3/3).**
- **Dynamics identifiable:** every ensemble net reproduces the EOM, q̈ R² = **1.0000**.
- **Lagrangian not identifiable:** ensemble std of the gauge part = **1.455** vs the physical part = **0.001**
  — a **1508×** split. The nets disagree *only* on the gauge direction.
- **The certificate:** the q̈ field's ensemble std is **0.15% of signal** — the net is *certain* about the
  dynamics and *free* on the gauge.

**The certificate.** The honest output of a discovery net is not one equation but an **equivalence class plus
a statement of what is identifiable**. This converts the project's recurring nulls (Phase-B reshaping
cancellation, MDL lookup codes, the D-v2 "economy does not select gauge") into a positive methodological
result: discovery = recover the gauge orbit + certify which directions are gauge.

---

## Certificate IV — no non-contextual code ⇒ quantum contextuality (Kochen–Specker / KCBS)

**Setup.** The single-system cousin of Certificate I: Bell rules out *local* hidden variables (two parties);
KCBS rules out *non-contextual* ones (one system) — a more fundamental no-go. Five yes/no projectors on a
qutrit are arranged in a pentagon (5-cycle) with exclusivity (adjacent projectors are mutually exclusive). A
genuine **non-contextual model** — a learnable distribution over the 11 valid value-assignments (the
independent sets of C₅) — obeys `Σ⟨Pᵢ⟩ ≤ 2` (the independence number). It is fit to the symmetric quantum
predictions scaled by visibility v (each `⟨Pᵢ⟩ = v/√5`, `Σ = v·√5`).

**Result (3/3).** The non-contextual model tracks the quantum sum *exactly* until it pins at **Σ = 2.00** — the
KCBS bound it cannot exceed — precisely at **v* = 2/√5 ≈ 0.894** (measured knee: 0.894, exact). Above that it
is stuck at 2 while quantum rises to √5 ≈ 2.236.

**The certificate.** The failure to find a cheap *non-contextual* code certifies quantum contextuality at the
KCBS bound. (Web-verified: non-contextual bound 2; quantum value √5.)

---

## The through-line

Four faces of one principle — *no cheap code / no invariant / no unique code / no non-contextual code*:

| Certificate | Forbidden-but-real structure | The wall the net hits | Sharp number |
|---|---|---|---|
| I — Bell | nonlocal correlation | CHSH bound \|S\| = 2 | v* = 1/√2 |
| II — chaos | conserved quantity (none exists) | unit-variance g can't go constant | constancy 0.45 vs 0.00 |
| III — gauge | a unique Lagrangian (none exists) | data flat along the gauge orbit | 1508× gauge/physical split |
| IV — KCBS | a non-contextual assignment | Σ⟨Pᵢ⟩ = 2 (independence number) | v* = 2/√5 |

The legibility law asked *what is the cheapest legible code?* These three ask its mirror question — *where
does no cheap code exist, and can the net certify it?* A net restricted to a cheap hypothesis class is a
**measuring instrument for the impossible**: its failure, gated against a theorem, is a positive result.
