"""Regression gate: re-run every probe script against the SAVED models and
assert the pre-registered thresholds. Fast (no training) — this is the
"did anything rot?" check, runnable any time. Exit code 0 = all green."""

import json
import subprocess
import sys
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
]


def get(d, dotted):
    for k in dotted.split("."):
        d = d[k]
    return d


def main() -> int:
    failures = 0
    for name, cmd, jname, gates in BATTERIES:
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
            if bad:
                failures += 1
                print(f"FAIL  {name}: " + "; ".join(bad))
            else:
                print(f"PASS  {name}")
        except Exception as e:
            failures += 1
            print(f"FAIL  {name}: {type(e).__name__}: {e}")
    print("=" * 40)
    print("ALL GREEN" if failures == 0 else f"{failures} BATTERY(IES) FAILED")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
