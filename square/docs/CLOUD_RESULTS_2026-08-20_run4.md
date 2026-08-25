# Cloud Verification Run 4 — 2026-08-20

**Scope:** Run 4 is a suite-only verification of two disposition/documentation commits: `02a34eb` (DeepSeek reviewer-response disposition) and `9c150aa` (professor-review documentation). The full B&B pipeline including four 1000-box traversal runs was already verified in Run 3 at commit `fe33c10` on branch `cloud/heilbronn-n12-verify-3`; those standing measurements are not repeated here.

---

## Step 0 — Environment Gate

```
Linux vm 6.18.5-fc-v20 #1 SMP PREEMPT_DYNAMIC @0 x86_64 x86_64 x86_64 GNU/Linux
vm
root
4
               total        used        free      shared  buff/cache   available
Mem:            15Gi       618Mi        14Gi       4.8Mi       562Mi        15Gi
Swap:             0B          0B          0B
Python 3.11.15
```

Platform: Linux x86_64 — PASS (not Darwin / local Mac).

---

## Step 1 — Pinned Checkout

Branch: `origin/codex/heilbronn-n12-global`  
Local branch: `cloud/heilbronn-n12-verify-4`  
**HEAD: `9c150aa5d4ee0b853650cf89e48d3c2c85720cd9`** — MATCHES EXPECTED SHA.

---

## Step 2 — Dependencies

```
numpy==2.0.2   (installed)
scipy==1.13.1  (installed)
```

---

## Step 3 — Execution (strictly serial)

### (a) Test Suite

```
python3 -m unittest -v
```

| Metric | Value |
|--------|-------|
| Exit code | 0 |
| Elapsed (real) | 1m 25.173s |
| Tests run | 30 |
| Failures | 0 |
| Errors | 0 |

**Result: OK — 30/30 tests passed.**

<details>
<summary>All 30 test names</summary>

```
test_active_hypergraph_structure ... ok
test_anchor_triangle_propagation_is_exact_sign_agnostic_and_keeps_the_incumbent ... ok
test_c2_boundary_family_contains_the_incumbent_without_c4_locking ... ok
test_c4_bernstein_interval_engine_keeps_dependence_and_scope_exact ... ok
test_c4_symmetry_family_contains_the_incumbent ... ok
test_calibration_templates_reproduce_known_values ... ok
test_calibration_templates_stay_in_the_unit_square ... ok
test_cubic_field_inversion ... ok
test_d4_interval_certificate_brackets_incumbent ... ok
test_d4_interval_certificate_documented_precision ... ok
test_d4_interval_contains_every_exact_triangle_at_a_sample_point ... ok
test_enumeration_matches_published_formula ... ok
test_exact_n11_insertion_no_go ... ok
test_first_order_tangent_certificate ... ok
test_free_size5_transversal_search_lifts_the_incumbent_without_edge_locking ... ok
test_frozen_boundary_coordinates_match_selected_score ... ok
test_frozen_boundary_incumbent_round_trip ... ok
test_global_interval_branch_stays_exact_and_reports_incompleteness ... ok
test_global_mccormick_glpk_parser_keeps_lp_and_mip_results_distinct ... ok
test_global_mccormick_lp_rounding_enlarges_the_exact_relaxation ... ok
test_global_mccormick_n6_witness_lift_and_spatial_boxes ... ok
test_highs_bridge_diagnoses_relaxation_gap ... ok
test_independent_decimal_reconstruction ... ok
test_rational_verifier_rejects_invalid_candidate ... ok
test_root_interval_is_rigorous ... ok
test_size5_interval_exploration_reports_incomplete_work_honestly ... ok
test_size5_orbit_distance_identifies_the_incumbent ... ok
test_size5_strata_have_expected_dimensions_and_incumbent_embedding ... ok
test_size5_vertex_hull_bounds_every_coordinate_box_determinant ... ok
test_unrestricted_normal_form_parameterization_and_exact_snap ... ok
```
</details>

---

### (b) 40-box Breadth-First Traversal

```
python3 global_interval_branch.py --max-boxes 40 --queue-policy breadth
```

| Metric | Observed | Expected |
|--------|----------|----------|
| visited_boxes | 40 | 40 |
| discarded_boxes | 0 | 0 |
| pending_boxes | 41 | 41 |
| maximum_depth | 5 | 5 |
| complete | False | False |
| status | INCOMPLETE: no global no-go claim | INCOMPLETE |

| Run metric | Value |
|------------|-------|
| Exit code | 0 |
| Elapsed (real) | 0m 8.628s |

**Result: PASS — all fields match expected.**

---

### (c) 40-box Depth-First Traversal

```
python3 global_interval_branch.py --max-boxes 40 --queue-policy depth
```

| Metric | Observed | Expected |
|--------|----------|----------|
| visited_boxes | 40 | 40 |
| discarded_boxes | 4 | 4 |
| pending_boxes | 33 | 33 |
| maximum_depth | 34 | 34 |
| complete | False | False |
| status | INCOMPLETE: no global no-go claim | INCOMPLETE |
| discard_reasons | {'triangle-upper': 4} | — |

| Run metric | Value |
|------------|-------|
| Exit code | 0 |
| Elapsed (real) | 0m 7.824s |

**Result: PASS — all fields match expected.**

---

## Summary

All gates passed. 30/30 unit tests green. Both 40-box diagnostics match expected values exactly. No pipeline regressions detected at commit `9c150aa`. Logs written to `$HOME/heilbronn_logs/` outside the repo.
