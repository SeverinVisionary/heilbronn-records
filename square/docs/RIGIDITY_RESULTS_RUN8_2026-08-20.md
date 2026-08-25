# Rigidity teeth test — RUN 8 (2026-08-20)

**Scope of this document.** Run 8 is a disposition re-verification at commit
988ac6c (panel disposition batch 2: Stiemke resolver complete for dims 0..4,
plus batch 1 code fixes). Census is expected to be identical to run 6; the
new output is `normalized_margin` and `normalized_min_weight` columns on each
minimal-rigid-core line. This is a first-order rigidity statement at the
incumbent — **NOT** global optimality, **NOT** a record claim.

## Step 0: environment gate

```
$ uname -a; hostname; whoami; nproc; free -h; python3 --version
Linux vm 6.18.5-fc-v20 #1 SMP PREEMPT_DYNAMIC @0 x86_64 x86_64 x86_64 GNU/Linux
vm
root
4
               total        used        free      shared  buff/cache   available
Mem:            15Gi       664Mi        14Gi       4.8Mi       559Mi        15Gi
Swap:             0B          0B          0B
Python 3.11.15
```

`uname -s` is `Linux`, not `Darwin`; the hostname is `vm`, not
not the operator's personal machine. Proceeded.

## Step 1: pinned checkout

Branch `cloud/heilbronn-n12-verify-8`, set up to track
`origin/codex/heilbronn-n12-global`.

```
$ git rev-parse HEAD
988ac6cc45e5f018168536edd72ae03bce153459
```

Matches the required pinned sha exactly. Working tree clean before compute.

## Step 2: dependencies

`python3 -m pip install -r requirements-research.txt` succeeded. Installed:

- numpy 2.0.2
- scipy 1.13.1

## Step 3(a): regression gate — `python3 -m unittest -v`

Executed in `<repo>`.
Log: `$HOME/heilbronn_logs/` (outside the repo).
**Exit code: 0**
**Elapsed: 70 s** (unittest banner: `Ran 32 tests in 69.025s`)

Full per-test output (verbatim):

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
test_rigidity_sampling_matches_the_incumbent_frame_descriptively (test_incumbent.IncumbentTests.test_rigidity_sampling_matches_the_incumbent_frame_descriptively) ... ok
test_root_interval_is_rigorous (test_incumbent.IncumbentTests.test_root_interval_is_rigorous) ... ok
test_size5_interval_exploration_reports_incomplete_work_honestly (test_incumbent.IncumbentTests.test_size5_interval_exploration_reports_incomplete_work_honestly) ... ok
test_size5_orbit_distance_identifies_the_incumbent (test_incumbent.IncumbentTests.test_size5_orbit_distance_identifies_the_incumbent) ... ok
test_size5_strata_have_expected_dimensions_and_incumbent_embedding (test_incumbent.IncumbentTests.test_size5_strata_have_expected_dimensions_and_incumbent_embedding) ... ok
test_size5_vertex_hull_bounds_every_coordinate_box_determinant (test_incumbent.IncumbentTests.test_size5_vertex_hull_bounds_every_coordinate_box_determinant) ... ok
test_unrestricted_normal_form_parameterization_and_exact_snap (test_incumbent.IncumbentTests.test_unrestricted_normal_form_parameterization_and_exact_snap) ... ok

----------------------------------------------------------------------
Ran 32 tests in 69.025s

OK
```

All 32 tests passed. Gate: **GO**.

## Step 3(b): prefix guard check — `python3 rigidity_core.py --sizes 18 --max-subsets 2`

Executed in `<repo>`.
**Exit code: 0**
**Elapsed: 4 s**

Complete stdout (verbatim):

```
controls PASS
processed 2 of 190
census 18 {'NONRIGID': 1, 'RIGID': 1}
undecided_count 0
status PARTIAL: size list is not the downward-closed prefix 16..max; no minimality claim
```

Final line is `status PARTIAL: size list is not the downward-closed prefix 16..max; no minimality claim`.
No `minimal_rigid_cores` lines present. Guard: **PASS**.

## Step 3(c): full rigid-core rescan — `python3 rigidity_core.py`

Executed in `<repo>`.
Log: `$HOME/heilbronn_logs/run8_full_stdout.txt` (outside the repo).
**Exit code: 0**
**Elapsed: 1311 s** (21 m 51 s)

### Complete stdout (verbatim):

```
controls PASS
processed 6196 of 6196
census 16 {'NONRIGID': 4845}
census 17 {'NONRIGID': 1132, 'RIGID': 8}
census 18 {'NONRIGID': 164, 'RIGID': 6, 'RIGID-by-monotonicity': 20}
census 19 {'NONRIGID': 8, 'RIGID-by-monotonicity': 12}
census 20 {'RIGID-by-monotonicity': 1}
undecided_count 0
minimal_rigid_cores 14
minimal_rigid_cores_up_to_d4 3
core (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17) orbit_signature (4, 8, 6) d4_copies 4 normalized_margin -0.004957633380764903289845 normalized_min_weight 0.004957633380764898574326
core (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15, 16, 18, 19) orbit_signature (2, 8, 8) d4_copies 2 normalized_margin -0.016299429345909849109382 normalized_min_weight 0.022932786148646374864878
core (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 16, 18, 19) orbit_signature (3, 8, 6) d4_copies 8 normalized_margin -0.003152025699654618852730 normalized_min_weight 0.017415606601691597803597
status COMPLETE: every subset in the scanned sizes carries an exact certificate
```

## Run-6 vs Run-8 comparison

### Census comparison

| Size | Status              | RUN 6 | RUN 8 | Match? |
|------|---------------------|-------|-------|--------|
| 16   | NONRIGID            | 4845  | 4845  | ✓      |
| 17   | NONRIGID            | 1132  | 1132  | ✓      |
| 17   | RIGID               | 8     | 8     | ✓      |
| 18   | NONRIGID            | 164   | 164   | ✓      |
| 18   | RIGID               | 6     | 6     | ✓      |
| 18   | RIGID-by-monotonicity | 20  | 20    | ✓      |
| 19   | NONRIGID            | 8     | 8     | ✓      |
| 19   | RIGID-by-monotonicity | 12  | 12    | ✓      |
| 20   | RIGID-by-monotonicity | 1   | 1     | ✓      |
| any  | UNDECIDED           | 0     | 0     | ✓      |

**Census: identical ✓**

### Core sets comparison

Run 6 printed three canonical cores (triangle-index tuples); run 8 prints the
same three tuples with additional `normalized_margin` and
`normalized_min_weight` columns. The tuples and orbit signatures are
bit-for-bit identical:

| Core (triangle indices) | Size | Orbit sig | D4 copies | R6 match? |
|---|---|---|---|---|
| `(0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17)` | 18 | (4,8,6) | 4 | ✓ |
| `(0,1,2,3,4,5,6,7,8,9,10,11,12,13,15,16,18,19)` | 18 | (2,8,8) | 2 | ✓ |
| `(0,1,2,3,4,5,6,7,8,9,10,11,12,14,16,18,19)` | 17 | (3,8,6) | 8 | ✓ |

D4 copy check: 4 + 2 + 8 = 14 raw minimal cores ✓

**Core sets: identical ✓**

### New columns: normalized margins

| Core | Size | normalized_margin | Expected (brief) | Match? |
|---|---|---|---|---|
| `(0,1,...,16,17)` | 18 | −0.00496 | ~−0.00496 | ✓ |
| `(0,1,...,18,19)` | 18 | −0.01630 | ~−0.0163 | ✓ |
| `(0,1,...,16,18,19)` | 17 | −0.00315 | ~−0.00315 | ✓ |

All three normalized margins match the expected values stated in the run-8
brief.

**Status line (verbatim):**
```
status COMPLETE: every subset in the scanned sizes carries an exact certificate
```

The status is `COMPLETE`; undecided_count is 0. Minimality claims are
unconditional within the scanned sizes 16–20.
