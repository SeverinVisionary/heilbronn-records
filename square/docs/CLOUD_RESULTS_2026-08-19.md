# Cloud Verification Results — 2026-08-19

Run date: 2026-08-20 (UTC)  
Branch: `cloud/heilbronn-n12-verify-1`  
Pinned commit: `e7b115a518d3290cea84b88cc6d99d72494352fe`

---

## Step 0 — Environment Evidence (verbatim)

```
Linux vm 6.18.5-fc-v20 #1 SMP PREEMPT_DYNAMIC @0 x86_64 x86_64 x86_64 GNU/Linux
vm
root
4
               total        used        free      shared  buff/cache   available
Mem:            15Gi       687Mi        14Gi       4.8Mi       554Mi        15Gi
Swap:             0B          0B          0B
Python 3.11.15
```

Platform: Linux x86_64 — gate PASSED (not Darwin/Mac).

---

## Step 1 — Pinned Checkout

```
git fetch origin codex/heilbronn-n12-global
git checkout -B cloud/heilbronn-n12-verify-1 origin/codex/heilbronn-n12-global
git rev-parse HEAD
```

HEAD: `e7b115a518d3290cea84b88cc6d99d72494352fe` ✓ (matches pinned commit exactly)

Working tree: clean before compute.

---

## Step 2 — Dependencies

```
python3 -m pip install -r requirements-research.txt
```

Installed:
- numpy==2.0.2
- scipy==1.13.1

Python: 3.11.15

---

## Step 3 — Execution

### Step 3(a): python3 -m unittest -v

**Command:** `python3 -m unittest -v`  
**Elapsed:** 57.087s (real)  
**Exit code:** 1 (FAILED — one test failure; tee exit code recorded as 0 but unittest returned failure)

```
Ran 29 tests in 56.520s

FAILED (failures=1)
```

**Test results:**

| Test | Result |
|------|--------|
| test_active_hypergraph_structure | ok |
| test_c2_boundary_family_contains_the_incumbent_without_c4_locking | ok |
| test_c4_bernstein_interval_engine_keeps_dependence_and_scope_exact | ok |
| test_c4_symmetry_family_contains_the_incumbent | ok |
| test_calibration_templates_reproduce_known_values | ok |
| test_calibration_templates_stay_in_the_unit_square | ok |
| test_cubic_field_inversion | ok |
| test_d4_interval_certificate_brackets_incumbent | ok |
| test_d4_interval_certificate_documented_precision | ok |
| test_d4_interval_contains_every_exact_triangle_at_a_sample_point | ok |
| test_enumeration_matches_published_formula | ok |
| test_exact_n11_insertion_no_go | ok |
| test_first_order_tangent_certificate | ok |
| test_free_size5_transversal_search_lifts_the_incumbent_without_edge_locking | ok |
| test_frozen_boundary_coordinates_match_selected_score | ok |
| test_frozen_boundary_incumbent_round_trip | ok |
| test_global_interval_branch_stays_exact_and_reports_incompleteness | ok |
| test_global_mccormick_glpk_parser_keeps_lp_and_mip_results_distinct | ok |
| test_global_mccormick_lp_rounding_enlarges_the_exact_relaxation | ok |
| test_global_mccormick_n6_witness_lift_and_spatial_boxes | ok |
| **test_highs_bridge_diagnoses_relaxation_gap** | **FAIL** |
| test_independent_decimal_reconstruction | ok |
| test_rational_verifier_rejects_invalid_candidate | ok |
| test_root_interval_is_rigorous | ok |
| test_size5_interval_exploration_reports_incomplete_work_honestly | ok |
| test_size5_orbit_distance_identifies_the_incumbent | ok |
| test_size5_strata_have_expected_dimensions_and_incumbent_embedding | ok |
| test_size5_vertex_hull_bounds_every_coordinate_box_determinant | ok |
| test_unrestricted_normal_form_parameterization_and_exact_snap | ok |

**Failure detail (verbatim):**

```
======================================================================
FAIL: test_highs_bridge_diagnoses_relaxation_gap (test_incumbent.IncumbentTests.test_highs_bridge_diagnoses_relaxation_gap)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<repo>/test_incumbent.py", line 453, in test_highs_bridge_diagnoses_relaxation_gap
    self.assertEqual(report.geometric_minimum_triangle, (0, 1, 4))
AssertionError: Tuples differ: (0, 1, 2) != (0, 1, 4)

First differing element 2:
2
4

- (0, 1, 2)
?        ^

+ (0, 1, 4)
?        ^
```

---

## BLOCKED

**Reason:** Test failure in `test_highs_bridge_diagnoses_relaxation_gap`.

The test at `test_incumbent.py:453` expected `report.geometric_minimum_triangle == (0, 1, 4)` but received `(0, 1, 2)`.

Per the job spec failure mode: "any failed gate, test failure, or unexpected diff is a STOP-and-report — record it in the results doc under the word BLOCKED, commit, push, and stop — never improvise around it."

**Steps 3(b) through 3(j) were NOT executed.**

The unit suite must pass cleanly before continuation. This result is recorded as-is without reinterpretation.

---

## Summary

| Step | Status |
|------|--------|
| Step 0: Environment gate | PASSED (Linux x86_64) |
| Step 1: Pinned checkout | PASSED (HEAD = e7b115a518d3290cea84b88cc6d99d72494352fe) |
| Step 2: Deps install | PASSED (numpy 2.0.2, scipy 1.13.1) |
| Step 3(a): unittest -v | **BLOCKED (1 test FAILED)** |
| Steps 3(b)–3(j) | NOT RUN |
