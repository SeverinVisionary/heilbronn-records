# Cloud Verification Results — 2026-08-20 (Run 2)

## Preamble

Run 1 (branch `cloud/heilbronn-n12-verify-1`) was BLOCKED by a solver-dependent assertion
in `test_incumbent.IncumbentTests.test_exact_n11_insertion_no_go` (the argmin-triangle
assertion, which depends on scipy's LP solver returning a specific vertex). That blocker
was reported to be fixed on the campaign branch `codex/heilbronn-n12-global`.

This run (Run 2, branch `cloud/heilbronn-n12-verify-2`) executes the fixed pinned commit
`6acd7a535d9fd8122d0840c6554c7f55e3649726` from `origin/codex/heilbronn-n12-global` in
accordance with `research/heilbronn_n12/CLOUD_JOB.md`. Run 2 encountered a **new** test
failure (a different test, `test_highs_bridge_diagnoses_relaxation_gap`) and is marked
BLOCKED below per the dispatch guardrails ("any failed gate, test failure, or unexpected
diff is a STOP-and-report").

---

## Step 0 — Environment Evidence (verbatim)

```
Linux vm 6.18.5-fc-v20 #1 SMP PREEMPT_DYNAMIC @0 x86_64 x86_64 x86_64 GNU/Linux
vm
root
4
               total        used        free      shared  buff/cache   available
Mem:            15Gi       662Mi        14Gi       4.8Mi       554Mi        15Gi
Swap:             0B          0B          0B
Python 3.11.15
```

- `uname -s` = `Linux` → NOT Darwin; environment gate **PASSED**
- Hostname `vm` (not a personal Mac) → gate **PASSED**
- Architecture: `x86_64` as expected
- CPUs: 4
- RAM: 15 GiB available

---

## Step 1 — Pinned Commit

Branch checked out: `cloud/heilbronn-n12-verify-2` tracking `origin/codex/heilbronn-n12-global`

```
HEAD: 6acd7a535d9fd8122d0840c6554c7f55e3649726
```

Expected: `6acd7a535d9fd8122d0840c6554c7f55e3649726` → **MATCH** ✓

Working tree was clean before any compute.

---

## Step 2 — Dependencies Installed

Command: `cd research/heilbronn_n12 && python3 -m pip install -r requirements-research.txt`

| Package | Version |
|---------|---------|
| numpy   | 2.0.2   |
| scipy   | 1.13.1  |

Python version: `3.11.15`

Exit code: 0

---

## Step 3 — Execution

### 3(a) `python3 -m unittest -v`

**Status: BLOCKED — test failure**

Elapsed: ~68 s (67 946 ms)

Full output (29 tests, 1 failure):

```
test_active_hypergraph_structure ... ok
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
test_highs_bridge_diagnoses_relaxation_gap ... FAIL
test_independent_decimal_reconstruction ... ok
test_rational_verifier_rejects_invalid_candidate ... ok
test_root_interval_is_rigorous ... ok
test_size5_interval_exploration_reports_incomplete_work_honestly ... ok
test_size5_orbit_distance_identifies_the_incumbent ... ok
test_size5_strata_have_expected_dimensions_and_incumbent_embedding ... ok
test_size5_vertex_hull_bounds_every_coordinate_box_determinant ... ok
test_unrestricted_normal_form_parameterization_and_exact_snap ... ok

======================================================================
FAIL: test_highs_bridge_diagnoses_relaxation_gap (test_incumbent.IncumbentTests.test_highs_bridge_diagnoses_relaxation_gap)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<repo>/test_incumbent.py", line 461,
      in test_highs_bridge_diagnoses_relaxation_gap
    self.assertEqual(report.maximum_constraint_violation, 0.0)
AssertionError: 3.3306690738754696e-16 != 0.0

----------------------------------------------------------------------
Ran 29 tests in 67.404s

FAILED (failures=1)
```

**Totals: 29 tests run, 28 passed, 1 FAILED**

The failing test `test_highs_bridge_diagnoses_relaxation_gap` asserts that
`report.maximum_constraint_violation == 0.0` (exact equality), but the HiGHS LP solver
returned `3.3306690738754696e-16` — one ULP of machine epsilon for double precision
(`~2^{-52}`). This is a solver numerical artefact: HiGHS reports a near-zero but
technically nonzero constraint violation for what is effectively a feasible LP solution.

This is a **different** test from the Run 1 blocker (which was `test_exact_n11_insertion_no_go`).
The Run 1 blocker test now **passes** (see output above: `test_exact_n11_insertion_no_go ... ok`).

Per the dispatch guardrails, this test failure is a **STOP** condition. No further steps
(3b through 4) were executed.

---

## BLOCKED

**Reason:** `test_highs_bridge_diagnoses_relaxation_gap` FAILED at step 3(a).

**Assertion:** `self.assertEqual(report.maximum_constraint_violation, 0.0)`

**Actual value:** `3.3306690738754696e-16`

**Analysis (informational, not a fix):** The value `3.33e-16 ≈ 2^{-51.9}` is one ULP of
machine epsilon — effectively zero, but HiGHS does not report it as exactly zero. The test
uses `assertEqual` (exact) rather than `assertAlmostEqual` or a tolerance check. A minimal
fix would be to change the assertion to `self.assertAlmostEqual(..., places=15)` or
`self.assertLessEqual(report.maximum_constraint_violation, 1e-12)`. However, this run does
not apply any fix per the "never improvise" rule.

**Steps completed:** 0 (env gate), 1 (checkout + SHA verification), 2 (deps)

**Steps NOT completed:** 3(b) through 4 (all deferred pending blocker resolution)

---

## Steps 3(b)–4 — NOT EXECUTED (BLOCKED)

Per dispatch guardrails, execution stopped after the first test failure. The following
commands were NOT run:

- `python3 incumbent.py`
- `python3 decimal_verifier.py`
- `python3 tangent_certificate.py`
- `python3 n11_insertion.py`
- `python3 d4_interval_certificate.py`
- `python3 global_interval_branch.py --max-boxes 40 --queue-policy breadth`
- `python3 global_interval_branch.py --max-boxes 40 --queue-policy depth`
- `python3 global_interval_branch.py --max-boxes 1000 --queue-policy breadth`
- `python3 global_interval_branch.py --max-boxes 1000 --queue-policy depth`

No traversal tables or discard-reason counts are available for this run.
