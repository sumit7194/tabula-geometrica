"""Regression gate: re-run every probe script against the SAVED models and
assert the pre-registered thresholds. Fast (no training) — this is the
"did anything rot?" check, runnable any time. Exit code 0 = all green."""

import json
import resource
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
R = ROOT / "results"
PY = str(ROOT / ".venv" / "bin" / "python")

# battery: (name, command, results json, {dotted.key: (op, threshold)})
BATTERIES = [
    ("Phase A (interval)", ["scripts/03_gates.py", "1"], "03_gates_k1.json",
     {"G1_isotonic_r2": (">", 0.95), "G2_alignment": (">", 0.95),
      "G2_sign_consistency": (">", 0.95)}),
    ("v0.1 (light cone)", ["scripts/04_gates_mixed.py", "1"], "04_gates_mixed_k1.json",
     {"future.isotonic_r2": (">", 0.95), "past.isotonic_r2": (">", 0.95),
      "right.isotonic_r2": (">", 0.95), "left.isotonic_r2": (">", 0.95)}),
    ("Phase B (well)", ["scripts/05_gates_well.py", "1"], "05_gates_well_k1.json",
     {"ratio_profile_correlation": (">", 0.9), "min_bin_isotonic_r2": (">", 0.95)}),
    ("Phase C (economy)", ["scripts/07_gates_economy.py", "charged"], "07_economy_charged.json",
     {"E1_force.charged": ("<", 1e-4), "E2_swap.charged": (">", 0.01),
      "E3_loo_decode_r": (">", 0.99)}),
    ("3+1 replication", ["scripts/08_gates_3p1.py", "1"], "08_gates_3p1_k1.json",
     {"isotonic_r2": (">", 0.95), "alignment": (">", 0.95)}),
    ("Phase E + curvature", ["scripts/17_curvature_invariant.py"], "17_curvature.json",
     {"G0_sphere_err": ("<", 0.01), "K1_corr": (">", 0.95)}),
    ("Phase J5 (curvature from entanglement)", ["scripts/42_curvature_from_entanglement.py"],
     "42_curvature_entanglement.json",
     {"E0_calculator.pass": (">", 0.5), "E1_critical.pass": (">", 0.5), "E2_gapped.pass": (">", 0.5),
      "E1_critical.c_from_curvature": (">", 0.8)}),
    ("Certificate V (no observer-independent time)", ["scripts/101_time_gauge_certificate.py"],
     "101_time_gauge.json",
     {"C1_no_global_time.pass_all_seeds": (">", 0.5), "C2_relational_time.pass_all_seeds": (">", 0.5),
      "C3_time_is_gauge.pass_all_seeds": (">", 0.5)}),
    ("de Sitter anchor (AdS-easy/dS-hard learnability)", ["scripts/111_desitter_anchor.py"],
     "111_desitter_anchor.json",
     {"G1_relational_learnable_both": (">", 0.5), "G2_absolute_needs_anchor": (">", 0.5),
      "G3_no_frame_without_anchor": (">", 0.5)}),
    ("Page curve + information return", ["scripts/112_page_curve.py"], "112_page_curve.json",
     {"P1_page_turnover": (">", 0.5), "P2_information_return": (">", 0.5), "P3_thermal_contrast": (">", 0.5)}),
    ("Aharonov-Bohm holonomy", ["scripts/113_aharonov_bohm.py"], "113_aharonov_bohm.json",
     {"AB1_learns_holonomy": (">", 0.5), "AB2_topological_not_geometric": (">", 0.5),
      "AB3_no_local_field_code": (">", 0.5)}),
    ("Spinor double cover (discovery)", ["scripts/114_spinor_double_cover.py"], "114_spinor_double_cover.json",
     {"S1_learnable": (">", 0.5), "S2_representability_certificate": (">", 0.5),
      "S3_two_sheets_720_return": (">", 0.5)}),
    ("Grid-cell torus (topology instrument)", ["scripts/115_grid_torus.py"], "115_grid_torus.json",
     {"T0_instrument_validated": (">", 0.5), "T1_grid_torus_place_not": (">", 0.5)}),
    ("Emergent grid torus (saved model probe)", ["scripts/116_grid_torus_emergence.py", "--probe-only"],
     "116_grid_probe.json", {"H2_emergent_torus_controlled": (">", 0.5)}),
    ("Topological band theory (SSH winding)", ["scripts/117_topological_band.py"], "117_topological_band.json",
     {"B1_learns_invariant": (">", 0.5), "B2_quantized_robust": (">", 0.5), "B3_bulk_boundary": (">", 0.5)}),
    ("Emergent dimension from RG (depth=log xi)", ["scripts/118_emergent_dimension_rg.py"],
     "118_emergent_dimension_rg.json",
     {"R1_emergent_depth_eq_logxi": (">", 0.5), "R2_radial_homogeneity_critical": (">", 0.5)}),
    ("Arrow of time (fluctuation theorem)", ["scripts/119_arrow_of_time.py"], "119_arrow_of_time.json",
     {"A1_discover_arrow": (">", 0.5), "A2_fluctuation_theorem": (">", 0.5),
      "A3_reversibility_certificate": (">", 0.5)}),
    ("2D Chern number (topological invariant)", ["scripts/120_chern_number.py"], "120_chern_number.json",
     {"C1_learns_invariant": (">", 0.5), "C2_quantized_robust": (">", 0.5), "C3_bulk_boundary_pass": (">", 0.5)}),
    ("Fisher = GR metric (natural gradient)", ["scripts/121_fisher_gr_metric.py"], "121_fisher_gr_metric.json",
     {"F1_fisher_is_metric": (">", 0.5), "F2_general_covariance": (">", 0.5), "F3_invariant_convergence": (">", 0.5)}),
    ("Horizon entropy S=A/4 (Bekenstein-Hawking)", ["scripts/122_horizon_entropy.py"], "122_horizon_entropy.json",
     {"H1_discovers_S_eq_A_over_4": (">", 0.5), "H2_holographic_area_not_volume": (">", 0.5),
      "H3_black_hole_surprises": (">", 0.5)}),
    ("Gravitational waves (quadrupole radiation)", ["scripts/123_gravitational_waves.py"], "123_gravitational_waves.json",
     {"W1_quadrupole_sourcing": (">", 0.5), "W2_no_monopole_dipole_radiation": (">", 0.5),
      "W3_propagation_at_c": (">", 0.5)}),
    ("Ollivier-Ricci curvature (network structure)", ["scripts/124_ollivier_ricci.py"], "124_ollivier_ricci.json",
     {"O1_bimodal_signature": (">", 0.5), "O2_ricci_surgery_recovers": (">", 0.5),
      "O3_curvature_carries_signal": (">", 0.5)}),
    ("Geometry from entanglement: dimension + grid (J2)", ["scripts/125_entanglement_dimension.py"],
     "125_entanglement_dimension.json",
     {"J2a_intrinsic_dimension": (">", 0.5), "J2b_grid_recovered": (">", 0.5), "J2c_geometry_real": (">", 0.5)}),
    ("A10 legibility<->integrability (for bridge)", ["scripts/127_integrability_legibility.py"],
     "127_integrability_legibility.json",
     {"G1_integrable_emit": (">", 0.5), "G2_nonintegrable_certify": (">", 0.5), "G3_legible_iff_integrable": (">", 0.5)}),
    ("Huygens tail by dimension", ["scripts/128_huygens_tail.py"], "128_huygens_tail.json",
     {"H1_huygens_by_dimension": (">", 0.5), "H2_same_front_speed": (">", 0.5), "H3_analytic_tail_shape": (">", 0.5)}),
    ("Curvature as the bottleneck", ["scripts/129_curvature_bottleneck.py"], "129_curvature_bottleneck.json",
     {"CB1_curvature_suffices": (">", 0.5), "CB2_bottleneck_is_curvature": (">", 0.5),
      "CB3_minimality_and_control": (">", 0.5)}),
    ("Operational observers (interval from radar timings)", ["scripts/130_operational_observers.py"],
     "130_operational_observers.json",
     {"O1_interval_from_timings": (">", 0.5), "O2_clock_noise_robust": (">", 0.5),
      "O3_product_not_euclidean": (">", 0.5)}),
    ("Relativistic rapidity (additive coordinate of boosts)", ["scripts/131_relativistic_rapidity.py"],
     "131_relativistic_rapidity.json",
     {"R1_additive_coordinate_fits": (">", 0.5), "R2_coordinate_is_rapidity": (">", 0.5),
      "R3_relativistic_not_galilean": (">", 0.5)}),
    ("ZV gamma-metric legibility (for TheBridge, A10 ext)", ["scripts/132_zv_gamma_metric.py"],
     "132_zv_gamma_metric.json",
     {"Z1_integrable_emit": (">", 0.5), "Z2_nonintegrable_certify": (">", 0.5),
      "Z3_legible_iff_integrable": (">", 0.5)}),
    ("Legibility predicts SAE monosemanticity", ["scripts/139_sae_legibility.py"], "139_sae_legibility.json",
     {"L1_replicates_legibility_law": (">", 0.5), "S1_amortized_monosemantic": (">", 0.5),
      "S2_free_superposed": (">", 0.5), "S3_legibility_predicts_monosemanticity": (">", 0.5)}),
    ("SAE-legibility in a real activation (sharpen)", ["scripts/140_sae_activations.py"], "140_sae_activations.json",
     {"A1_legibility": (">", 0.5), "A2_amortized_localizable_in_activation": (">", 0.5),
      "A3_localizability_contrast": (">", 0.5)}),
    ("Discoverability trichotomy (frontier EXP-1)", ["scripts/141_discoverability_trichotomy.py"],
     "141_discoverability_trichotomy.json",
     {"F1_emit": (">", 0.5), "F2_certify_gauge": (">", 0.5), "F3_certify_no_code": (">", 0.5),
      "F4_one_diagnostic_all_three": (">", 0.5)}),    ("Certify-contextual verdict (frontier EXP-2)", ["scripts/142_contextual_certificate.py"],
     "142_contextual_certificate.json",
     {"C1_emit_classical": (">", 0.5), "C2_certify_contextual": (">", 0.5), "C3_locates_the_wall": (">", 0.5)}),
    ("Manko-Novikov legibility (for TheBridge, A10 ext)", ["scripts/144_manko_novikov.py"],
     "144_manko_novikov.json",
     {"M1_kerr_emit": (">", 0.5), "M2_mn_certify": (">", 0.5), "M3_legible_iff_integrable": (">", 0.5),
      "V0_pass": (">", 0.5)}),
    ("Regime detector (frontier EXP-4)", ["scripts/145_regime_detector.py"], "145_regime_detector.json",
     {"D1_type_inference": (">", 0.5), "D2_trajectory_branch": (">", 0.5), "D3_end_to_end": (">", 0.5)}),
    ("Sixth-wall exhaustiveness hunt (frontier EXP-5)", ["scripts/146_sixth_wall_hunt.py"],
     "146_sixth_wall_hunt.json",
     {"W1_partial_obs_absorbed": (">", 0.5), "W2_irreducibility_misfit": (">", 0.5),
      "W3_underdetermination_gap": (">", 0.5)}),
    ("Abstain-aware detector (frontier EXP-6)", ["scripts/147_abstain_detector.py"], "147_abstain_detector.json",
     {"A1_pass": (">", 0.5), "A2_pass": (">", 0.5), "A3_pass": (">", 0.5)}),
    ("Law vs predictability dissociation (frontier EXP-7)", ["scripts/148_law_vs_predictability.py"],
     "148_law_vs_predictability.json",
     {"G1_law_uniform_for_structured": (">", 0.5), "G2_predictability_dissociates": (">", 0.5),
      "G3_dissociation_real": (">", 0.5)}),
    ("Mixed-regime robustness (frontier EXP-8)", ["scripts/149_mixed_regime.py"], "149_mixed_regime.json",
     {"X1_mixture_is_real": (">", 0.5), "X2_single_verdict_loses_it": (">", 0.5),
      "X3_mixture_aware_recovers_it": (">", 0.5)}),
    ("Unified robust detector (frontier EXP-9)", ["scripts/150_robust_detector.py"], "150_robust_detector.json",
     {"U1_confident_correct": (">", 0.5), "U2_mixture_detected": (">", 0.5),
      "U3_abstain_when_underdetermined": (">", 0.5), "U4_one_instrument_all_outcomes": (">", 0.5)}),
    ("Noise robustness profile (frontier EXP-10)", ["scripts/151_noise_robustness.py"], "151_noise_robustness.json",
     {"N1_low_noise_correct": (">", 0.5), "N2_chaos_robust": (">", 0.5), "N3_degradation_profiled": (">", 0.5)}),
    ("Predictability diagnostic (frontier EXP-11)", ["scripts/152_predictability_diagnostic.py"],
     "152_predictability_diagnostic.json",
     {"P1_classifies_all_five": (">", 0.5), "P2_complete_taxonomy": (">", 0.5),
      "P3_orthogonal_to_discoverability": (">", 0.5)}),
    ("Sample complexity diverges at wall (frontier EXP-12)", ["scripts/153_sample_complexity.py"],
     "153_sample_complexity.json",
     {"S1_monotonic_divergence": (">", 0.5), "S2_power_law_inverse_delta_sq": (">", 0.5),
      "S3_quantified_axis": (">", 0.5)}),
    ("Real-data test vs literature (frontier EXP-13)", ["scripts/154_real_data.py"], "154_real_data.json",
     {"R1_laser_chaotic": (">", 0.5), "R2_tides_predictable": (">", 0.5), "R3_sunspots_stable_honest": (">", 0.5)}),
    ("Temporal regime-switching (frontier EXP-14)", ["scripts/155_temporal_switching.py"], "155_temporal_switching.json",
     {"T1_switch_localized": (">", 0.5), "T2_U_shaped_resolution": (">", 0.5), "T3_temporal_vs_ensemble": (">", 0.5),
      "T4_sampling_sets_temporal_resolution": (">", 0.5)}),
    ("Newton from ephemerides (real data, EXP-15)", ["scripts/156_newton_from_ephemerides.py"],
     "156_newton_from_ephemerides.json",
     {"P1_emit_E_measure_GM": (">", 0.5), "P2_emit_L": (">", 0.5), "P3_LRL_one_over_r_specific": (">", 0.5),
      "P4_perihelion_precession_soft": (">", 0.5)}),
    ("KK mass discovery (quantum sister, script 157)", ["scripts/157_kk_mass_discovery.py"],
     "157_kk_mass_discovery.json",
     {"G0_replication": (">", 0.5), "K1_mass_emerges": (">", 0.5), "K2_quantized_ladder": (">", 0.5),
      "K3_orientation_certificate": (">", 0.5)}),
    ("Axion discovery (bridge capstone, script 158)", ["scripts/158_axion_discovery.py"],
     "158_axion_discovery.json",
     {"S0": (">", 0.5), "A1_knee_at_1": (">", 0.5), "A2_blind_splitting": (">", 0.5),
      "B1_three_latents": (">", 0.5), "B2_moduli_decode": (">", 0.5),
      "C1_modular_certificate": (">", 0.5), "C2_hyperbolic_limit": (">", 0.5)}),
    # Isospectral drums (bridge Ledger K5, script 159). --fast is the regression configuration; it asserts the
    # INSTRUMENT (D0, incl. the permutation-similarity confound in the bridge's cell-centred scheme), K5's premise
    # (D1), and the MECHANISM (D4 modal arm + both amplitude-stripped controls). The raw-waveform arms D2/D3 need the
    # full budget and are deliberately NOT asserted here -- D2 misses its pre-registered strength gate even at full
    # scale (0.618 vs 0.80, though z=18.8), which is recorded as an honest partial, not a green gate.
    ("Isospectral drums / K5 (bridge round 8, script 159)", ["scripts/159_hearing_the_drum.py", "--fast"],
     "159_drums_fast.json",
     {"D0.passed": (">", 0.5), "D0.confound_confirmed": (">", 0.5), "D1_pass": (">", 0.5),
      "D4_modal_pass": (">", 0.5), "D4_stripped_pass": (">", 0.5), "k5_killed": (">", 0.5)}),
    # Basis ladder (G2 prep, script 160): calibrates CERTIFY-relative-to-basis on a system whose only invariant is
    # transcendental in the momenta -- polynomial + rational certify, a scanned transcendental family emits.
    ("Basis ladder / G2 prep (bridge round 8, script 160)", ["scripts/160_basis_ladder.py"],
     "160_basis_ladder.json",
     {"T0_pass": (">", 0.5), "T1_polynomial_certifies": (">", 0.5), "T2_rational_certifies": (">", 0.5),
      "T3_transcendental_emits": (">", 0.5), "T4_ladder_localises": (">", 0.5)}),
    # G2 blind legibility (script 161): emit-or-certify on the bridge's two adversarial metrics. A emits an exact
    # invariant (legible); B certifies (illegible relative to polynomial/rational up to deg 6). Asserts the verdicts +
    # that both integrators are clean. Runs ~5 min.
    ("G2 blind legibility (bridge round 8, script 161)", ["scripts/161_g2_blind_legibility.py"],
     "161_g2_blind.json",
     {"A.G0_pass": (">", 0.5), "A.emit": (">", 0.5), "B.G0_pass": (">", 0.5),
      "B.certify": (">", 0.5), "B.approximation_signature": (">", 0.5)}),
    ("G2 augmented basis R1 (bridge round-9, script 162)", ["scripts/162_g2_augmented_basis.py", "--fast"],
     "162_g2_augmented_basis.json",
     {"G0_integrator": (">", 0.5), "G1_control_reproduces_round8": (">", 0.5),
      "G2_augmented_characterized": (">", 0.5)}),
    ("Drum information-localization R5 (bridge round-9, script 163)", ["scripts/163_drum_localization.py", "--fast"],
     "163_drum_localization_fast.json" if False else "163_drum_localization.json",
     {"L0_spectrum_blind_full_kill": (">", 0.5), "L1_low_mode_concentration": (">", 0.5),
      "L3_sensor_saturation": (">", 0.5)}),
    ("G2 un-blind: named basis emits (bridge round-9, script 164)", ["scripts/164_g2_unblind.py", "--fast"],
     "164_g2_unblind.json",
     {"U0_invariant_verified": (">", 0.5), "U1_named_basis_emits": (">", 0.5),
      "U2_analytic_ladder_never_converges": (">", 0.5), "U3_O4_trap_confirmed_and_guarded": (">", 0.5)}),
    ("Noise-calibrated cutoff + conditioning caveat (bridge round-9, script 165)",
     ["scripts/165_noise_calibrated_cutoff.py", "--fast"], "165_noise_calibrated_cutoff.json",
     {"W1_cor42_separates_robustly": (">", 0.5), "W2_conditioning_confound": (">", 0.5),
      "W3_threshold_free_cross_check": (">", 0.5)}),
    ("The certificate standard (script 166)", ["scripts/166_certificate_standard.py", "--fast"],
     "166_certificate_standard.json",
     {"S1_genuine_passes": (">", 0.5), "S2_confound_gap_closed": (">", 0.5),
      "S3_true_null_scoped": (">", 0.5), "S4_conditioning_fires": (">", 0.5)}),
    # P3 screen (script 167): the K0 control is the load-bearing assert -- at eps=0 the engine must REDISCOVER
    # Carter unaided after deflating the reducibles, which is what makes every CERTIFY at eps>0 meaningful.
    ("P3 Killing-tensor screen (script 167)", ["scripts/167_p3_killing_tensor_screen.py", "--fast"],
     "167_p3_killing_tensor_screen.json",
     {"K0_control_limit": (">", 0.5), "K1_carter_dies": (">", 0.5), "K2_rank34_screened": (">", 0.5),
      "K3_conditioning_honesty": (">", 0.5), "carter_drift_ratio": (">", 1e6)}),
    # 169: the degree-3 POSITIVE control. Asserts the readout can find a known irreducible cubic invariant --
    # without this, a degree-3 null anywhere in the ladder is not a null (it is "no positive control was run").
    ("Degree-3 positive control, Toda cubic (script 169)",
     ["scripts/169_degree3_positive_control.py", "--fast"], "169_degree3_positive_control.json",
     {"T0_cubic_conserved": (">", 0.5), "T1_cubic_irreducible": (">", 0.5),
      "T2_readout_finds_it": (">", 0.5), "T3_spectrum_separates": (">", 0.5),
      "separation": (">", 1e3)}),
    # 171: the degree-4 POSITIVE control (Toda tr L^4 from the Lax matrix). Q4 is the known-FAIL half -- a smooth
    # non-conserved function must be EXCLUDED -- without which the criteria are tested in one direction only.
    ("Degree-4 positive control, Toda tr L^4 (script 171)",
     ["scripts/171_degree4_positive_control.py", "--fast"], "171_degree4_positive_control.json",
     {"Q0_conserved": (">", 0.5), "Q1_irreducible": (">", 0.5), "Q2_readout_finds_it": (">", 0.5),
      "Q3_spectrum_separates": (">", 0.5), "Q4_known_fail_excluded": (">", 0.5),
      "separation": (">", 1e3)}),
    # 172: the degree-4 GEODESIC-FLOW control. G2 FAILS -- the readout does not isolate a genuine rank-4 Killing
    # tensor when the reducible algebra is large and near-degenerate -- so only the ESTABLISHED half is asserted:
    # the substrate (Ricci-flat, with a known-fail matching the paper's own R_tt = 2*U_xy) and the target
    # (conserved, irreducible). These protect the CG transcription + derivation from regression. G2 is NOT
    # asserted; the negative is the result and lives in the notes.
    ("Degree-4 geodesic substrate + target (script 172)",
     ["scripts/172_degree4_geodesic_control.py", "--fast"], "172_degree4_geodesic_control.json",
     {"G0_substrate_verified": (">", 0.5), "G0a_ricci_flat": (">", 0.5), "G1_irreducible": (">", 0.5),
      "drift_K": ("<", 1e-10), "drift_H": ("<", 1e-10), "ricci_max_additive": ("<", 1e-8)}),

    # 176: C5 for the frontier's SEARCH-based certificate. CERTIFY-NO-CODE (141/143/145/151) was exempted from
    # C5 as "measurement-based"; it is a search, so the clause applies. Asserts the ladder contrast (same 6-D
    # data, code found at d=6 and not at d=2) AND the minimal-contrast control (same generator at dim 2, found
    # at d=2) -- the two halves test the reconstructor and the verdict-issuing readout respectively.
    ("C5 for CERTIFY-NO-CODE, dimension ladder (script 176)",
     ["scripts/176_c5_frontier_certificates.py", "--fast"], "176_c5_frontier_certificates.json",
     {"P0_reproduces_certify": (">", 0.5), "P1_finds_code_at_native_dim": (">", 0.5),
      "P2_known_fail_at_d2": (">", 0.5), "P4_minimal_contrast_control": (">", 0.5),
      "c5_satisfied": (">", 0.5), "stress_curve.6": ("<", 0.12), "stress_curve.2": (">", 0.5)}),

    # 177: the located-wall upgrade generalised across the frontier's certify verdicts, with the censoring guard.
    # W1 K*=3 is the reflection argument (2 anchors fix rotation+translation but leave a mirror; 3 non-collinear
    # do not); W2 r* against the Feigenbaum point; W3 the guard's known-FAIL -- a capped statistic must ABSTAIN;
    # W4 the guard must not fire on the honest sweeps. Three readouts and two guard designs were rejected getting
    # here and both rejections are recorded in the script.
    ("Located walls + censoring guard (script 177)",
     ["scripts/177_located_walls.py", "--fast"], "177_located_walls.json",
     {"W1_gauge_wall.K_star": (">", 2.5), "W1_gauge_wall.pass": (">", 0.5),
      "W2_chaos_wall.pass": (">", 0.5), "W3_censoring_guard.abstained": (">", 0.5),
      "W4_guard_not_trigger_happy": (">", 0.5), "W5_guard_flags_not_decides.pass": (">", 0.5),
      "all_pass": (">", 0.5)}),
]


def get(d, dotted):
    for k in dotted.split("."):
        d = d[k]
    return d


# Batteries excluded from the default pass, with the reason. A suite that silently omits nothing is worth more
# than one that quietly skips; each name here is printed as SKIP so an omission can never read as a pass.
SKIP = {
    "Grid-cell torus (topology instrument)":
        "OBSERVED PEAK 6.75 GB resident (battery 13/62; a sister session independently saw 6.11 GB minutes "
        "earlier). The footprint FLUCTUATES rather than climbs -- ripser allocates and frees per homology "
        "dimension, and it read 2.77 GB at the moment it was killed -- so any single sample is a lower bound "
        "on the peak and the sampling instant decides which. 115 has no --probe-only path (that is 116's). "
        "Quarantined from the fast pass until it gets one. Run explicitly with --all. NOT a silent omission: "
        "it prints as SKIP.",
}


def main() -> int:
    failures = 0
    run_all = "--all" in sys.argv[1:]
    n = len(BATTERIES)
    for idx, (name, cmd, jname, gates) in enumerate(BATTERIES, 1):
        # Per-item progress, added 2026-08-21. A suite that emits nothing cannot distinguish HUNG from WORKING,
        # so a green pass from it carries less information than it appears to. This one line is why the next
        # anomaly is legible from our own log instead of from a sister session's `ps`. Peak RSS is reported for
        # the same reason: every threshold in this file is about physics and none was ever about the instrument's
        # own footprint, which is how a battery grew to 3 GB without any gate noticing. (ansatz's push.)
        if name in SKIP and not run_all:
            print(f"[{idx}/{n}] SKIP  {name}\n        reason: {SKIP[name]}", flush=True)
            continue
        t0 = time.time()
        r0 = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss   # bytes on macOS; high-water mark
        print(f"[{idx}/{n}] {name} ...", flush=True)
        try:
            subprocess.run([PY] + cmd, cwd=ROOT, check=True,
                           capture_output=True, timeout=900)
            res = json.loads((R / jname).read_text())
            bad = []
            for key, (op, thr) in gates.items():
                v = float(get(res, key))
                ok = v > thr if op == ">" else v < thr
                if not ok:
                    bad.append(f"{key}={v:.4g} !{op} {thr}")
            dt = time.time() - t0
            # UNITS, and this line was wrong on its first run in a way worth keeping a comment about:
            # macOS reports ru_maxrss in BYTES (Linux uses KB), and RUSAGE_CHILDREN is a HIGH-WATER MARK over
            # every child ever reaped, not this child's usage. So the honest readout is "did this battery raise
            # the high-water mark, and to what" -- not a per-battery total. Reported only when it moves.
            hw = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss / 1073741824
            cost = f"{dt:6.1f}s" + (f"  new peak {hw:.2f} GB" if hw > r0 / 1073741824 + 1e-9 else "")
            if bad:
                failures += 1
                print(f"FAIL  {name}  [{cost}]: " + "; ".join(bad), flush=True)
            else:
                print(f"PASS  {name}  [{cost}]", flush=True)
        except Exception as e:
            failures += 1
            print(f"FAIL  {name}: {type(e).__name__}: {e}")
    print("=" * 40)
    print("ALL GREEN" if failures == 0 else f"{failures} BATTERY(IES) FAILED")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
