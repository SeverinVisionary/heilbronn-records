# Rigid-core scan results (Part A of the rigidity teeth test)

Run 5. Part A of the rigidity teeth test per
[RIGIDITY_CORE_SPEC_2026-08-20.md](RIGIDITY_CORE_SPEC_2026-08-20.md);
Part B (near-record sampling) is a separate future job and was not run
here. This document records the environment gate, the pinned commit, the
full verbatim outputs of Step 3(a) (unit test suite, 31 tests) and
Step 3(b) (`python3 rigidity_core.py`, the full 6196-subset scan), and
the exit codes and elapsed times for each command.  All status lines
are reproduced verbatim; no reinterpretation; any UNDECIDED count is
surfaced as a first-class result.

## Step 0: environment gate

```
$ uname -a; hostname; whoami; nproc; free -h; python3 --version
Linux vm 6.18.5-fc-v20 #1 SMP PREEMPT_DYNAMIC @0 x86_64 x86_64 x86_64 GNU/Linux
vm
root
4
               total        used        free      shared  buff/cache   available
Mem:            15Gi       616Mi        14Gi       4.8Mi       554Mi        15Gi
Swap:             0B          0B          0B
Python 3.11.15
```

`uname -s` is `Linux`, not `Darwin`. Not the operator's Mac. Proceeded.

## Step 1: pinned checkout

Branch: `cloud/heilbronn-n12-verify-5`, set up to track
`origin/codex/heilbronn-n12-global`.

```
$ git rev-parse HEAD
1e3756f2d55997626c689ced0e7a97eb0c1b52f2
```

HEAD matches the required pinned sha exactly. Working tree clean before
compute.

## Step 2: dependencies

`python3 -m pip install -r requirements-research.txt` succeeded.
Installed versions:

- numpy 2.0.2
- scipy 1.13.1

## Step 3(a): regression gate — `python3 -m unittest -v`

Executed in: `<repo>`  
Log: `$HOME/heilbronn_logs/unittest.log` (outside the repo)  
**Exit code: 0**  
**Elapsed: 59 s** (unittest banner: `Ran 31 tests in 58.877s`)

Full per-test output (verbatim from `$HOME/heilbronn_logs/unittest.log`):

```
test_active_hypergraph_structure (test_incumbent.IncumbentTests.test_active_hypergraph_structure) ... ok
test_anchor_triangle_propagation_is_exact_sign_agnostic_and_keeps_the_incumbent (test_incumbent.IncumbentTests.test_anchor_triangle_propagation_is_exact_sign_agnostic_and_keeps_the_incumbent) ... ok
test_c2_boundary_family_contains_the_incumbent_without_c4_locking (test_incumbent.IncumbentTests.test_c2_boundary_family_contains_the_incumbent_without_c4_locking) ... ok
test_c4_bernstein_interval_engine_keeps_dependence_and_scope_exact (test_incumbent.IncumbentTests.test_c4_bernstein_interval_engine_keeps_dependence_and_scope_exact) ... ok
test_c4_symmetry_family_contains_the_incumbent (test_incumbent.IncumbentTests.test_c4_symmetry_family_contains_the_incumbent) ... ok
test_calibration_templates_reproduce_known_values (test_incumbent.IncumbentTests.test_calibration_templates_reproduce_known_values) ... ok
test_calibration_templates_stay_in_the_unit_square (test_incumbent.IncumbentTests.test_calibration_templates_stay_in_the_unit_square) ... ok
test_cubic_field_inversion (test_incumbent.IncumbentTests.test_cubic_field_inversion) ... ok
test_d4_interval_certificate_brackets_incumbent (test_incumbent.IncumbentTests.test_d4_interval_certificate_brackets_incumbent) ... ok
test_d4_interval_certificate_documented_precision (test_incumbent.IncumbentTests.test_d4_interval_certificate_documented_precision) ... ok
test_d4_interval_contains_every_exact_triangle_at_a_sample_point (test_incumbent.IncumbentTests.test_d4_interval_contains_every_exact_triangle_at_a_sample_point) ... ok
test_enumeration_matches_published_formula (test_incumbent.IncumbentTests.test_enumeration_matches_published_formula) ... ok
test_exact_n11_insertion_no_go (test_incumbent.IncumbentTests.test_exact_n11_insertion_no_go) ... ok
test_first_order_tangent_certificate (test_incumbent.IncumbentTests.test_first_order_tangent_certificate) ... ok
test_free_size5_transversal_search_lifts_the_incumbent_without_edge_locking (test_incumbent.IncumbentTests.test_free_size5_transversal_search_lifts_the_incumbent_without_edge_locking) ... ok
test_frozen_boundary_coordinates_match_selected_score (test_incumbent.IncumbentTests.test_frozen_boundary_coordinates_match_selected_score) ... ok
test_frozen_boundary_incumbent_round_trip (test_incumbent.IncumbentTests.test_frozen_boundary_incumbent_round_trip) ... ok
test_global_interval_branch_stays_exact_and_reports_incompleteness (test_incumbent.IncumbentTests.test_global_interval_branch_stays_exact_and_reports_incompleteness) ... ok
test_global_mccormick_glpk_parser_keeps_lp_and_mip_results_distinct (test_incumbent.IncumbentTests.test_global_mccormick_glpk_parser_keeps_lp_and_mip_results_distinct) ... ok
test_global_mccormick_lp_rounding_enlarges_the_exact_relaxation (test_incumbent.IncumbentTests.test_global_mccormick_lp_rounding_enlarges_the_exact_relaxation) ... ok
test_global_mccormick_n6_witness_lift_and_spatial_boxes (test_incumbent.IncumbentTests.test_global_mccormick_n6_witness_lift_and_spatial_boxes) ... ok
test_highs_bridge_diagnoses_relaxation_gap (test_incumbent.IncumbentTests.test_highs_bridge_diagnoses_relaxation_gap) ... ok
test_independent_decimal_reconstruction (test_incumbent.IncumbentTests.test_independent_decimal_reconstruction) ... ok
test_rational_verifier_rejects_invalid_candidate (test_incumbent.IncumbentTests.test_rational_verifier_rejects_invalid_candidate) ... ok
test_rigidity_core_certificates_are_exact_and_two_sided (test_incumbent.IncumbentTests.test_rigidity_core_certificates_are_exact_and_two_sided) ... ok
test_root_interval_is_rigorous (test_incumbent.IncumbentTests.test_root_interval_is_rigorous) ... ok
test_size5_interval_exploration_reports_incomplete_work_honestly (test_incumbent.IncumbentTests.test_size5_interval_exploration_reports_incomplete_work_honestly) ... ok
test_size5_orbit_distance_identifies_the_incumbent (test_incumbent.IncumbentTests.test_size5_orbit_distance_identifies_the_incumbent) ... ok
test_size5_strata_have_expected_dimensions_and_incumbent_embedding (test_incumbent.IncumbentTests.test_size5_strata_have_expected_dimensions_and_incumbent_embedding) ... ok
test_size5_vertex_hull_bounds_every_coordinate_box_determinant (test_incumbent.IncumbentTests.test_size5_vertex_hull_bounds_every_coordinate_box_determinant) ... ok
test_unrestricted_normal_form_parameterization_and_exact_snap (test_incumbent.IncumbentTests.test_unrestricted_normal_form_parameterization_and_exact_snap) ... ok

----------------------------------------------------------------------
Ran 31 tests in 58.877s

OK
```

## Step 3(b): full rigid-core scan — `python3 rigidity_core.py`

Executed in: `<repo>`  
Log: `$HOME/heilbronn_logs/scan.log` and `$HOME/heilbronn_logs/scan.err` (outside the repo)  
**Exit code: 0** (process exited cleanly; stderr contained only the `time` summary, no Python exceptions)  
**Elapsed: 18 m 12.200 s** (real); user 18m12.054s, sys 0m0.528s

### Complete stdout (verbatim from `$HOME/heilbronn_logs/scan.log`):

```
controls PASS
processed 6196 of 6196
census 16 {'NONRIGID': 4845}
census 17 {'NONRIGID': 1116, 'RIGID': 8, 'UNDECIDED': 16}
census 18 {'NONRIGID': 156, 'RIGID': 6, 'RIGID-by-monotonicity': 20, 'UNDECIDED': 8}
census 19 {'NONRIGID': 8, 'RIGID-by-monotonicity': 12}
census 20 {'RIGID-by-monotonicity': 1}
undecided_count 24
minimal_rigid_cores 14
minimal_rigid_cores_up_to_d4 3
core (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17) orbit_signature (4, 8, 6) d4_copies 4 least_negative_normal -0.058898129370378365988780
core (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15, 16, 18, 19) orbit_signature (2, 8, 8) d4_copies 2 least_negative_normal -0.250749824879366057668676
core (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 16, 18, 19) orbit_signature (3, 8, 6) d4_copies 8 least_negative_normal -0.036267268683650145293539
status COMPLETE-WITH-UNDECIDED: minimality claims exclude undecided subsets
```

### stderr from `$HOME/heilbronn_logs/scan.err` (verbatim):

```
real	18m12.200s
user	18m12.054s
sys	0m0.528s
```

### Scan summary (derived from above without reinterpretation)

**UNDECIDED count: 24** (16 at size 17; 8 at size 18). These are
first-class results; per the spec, minimality claims exclude any
UNDECIDED subset. A rigid core that is a strict superset of an UNDECIDED
subset cannot be claimed minimal until Part B or a future exact pass
resolves those 24 subsets.

**Minimal rigid cores (raw): 14**

**Minimal rigid cores up to D4: 3** canonical orbits, all at sizes 17–18:

| Core (triangle indices) | Size | Orbit sig | D4 copies | Least-neg normal margin |
|---|---|---|---|---|
| `(0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17)` | 18 | (4,8,6) | 4 | −0.058898129370378365988780 |
| `(0,1,2,3,4,5,6,7,8,9,10,11,12,13,15,16,18,19)` | 18 | (2,8,8) | 2 | −0.250749824879366057668676 |
| `(0,1,2,3,4,5,6,7,8,9,10,11,12,14,16,18,19)` | 17 | (3,8,6) | 8 | −0.036267268683650145293539 |

D4 copy counts check: 4 + 2 + 8 = 14 raw minimal cores ✓; matches
`minimal_rigid_cores 14` in the scanner output.

**Status line (verbatim):**
```
status COMPLETE-WITH-UNDECIDED: minimality claims exclude undecided subsets
```

## Scope guard

Reiterated verbatim from the dispatch: this scan is a first-order
rigidity statement at the incumbent; it is NOT a global optimality
claim, NOT a record improvement, and says nothing about remote
configurations. The scanner's own status line is preserved exactly
above. Part B (near-record sampling) is a separate future job and was
not implemented in this run.
