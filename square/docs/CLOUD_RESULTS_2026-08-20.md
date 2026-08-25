# Cloud Verification Results — n=12 Heilbronn — 2026-08-20

## Run history

- **Run 1** (`cloud/heilbronn-n12-verify-1`): BLOCKED by the solver-dependent
  `argmin`-triangle assertion in `test_highs_bridge_diagnoses_relaxation_gap`.
- **Run 2** (`cloud/heilbronn-n12-verify-2`): Fixed the `argmin` assertion, then
  BLOCKED by the exact-zero float residual assertion in the same test
  (residual was 3.33e-16 on Linux, expected exactly 0).
- **Run 3** (`cloud/heilbronn-n12-verify-3`, this document): Both prior assertions
  are fixed; the branch adds a new exact anchor-triangle propagation feature
  with its own gate test.

---

## Step 0 — Environment gate

```
Linux vm 6.18.5-fc-v20 #1 SMP PREEMPT_DYNAMIC @0 x86_64 x86_64 x86_64 GNU/Linux
vm
root
4
               total        used        free      shared  buff/cache   available
Mem:            15Gi       668Mi        14Gi       4.8Mi       563Mi        15Gi
Swap:             0B          0B          0B
Python 3.11.15
```

`uname -s` = Linux — gate passed; not Darwin.

---

## Step 1 — Pinned checkout

```
git fetch origin codex/heilbronn-n12-global
git checkout -B cloud/heilbronn-n12-verify-3 origin/codex/heilbronn-n12-global
git rev-parse HEAD
```

HEAD: **`fe33c10b6b54f3c28fc1588fcff671851b8c8bf6`** ✓

---

## Step 2 — Dependencies installed

```
numpy==2.0.2
scipy==1.13.1
Python 3.11.15
```

Exit 0.

---

## Step 3 — Proof and regression suite

### (a) Unit tests

Command: `python3 -m unittest -v`

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

----------------------------------------------------------------------
Ran 30 tests in 68.588s

OK
```

Exit 0, elapsed 1m9.136s.

All 30 tests pass, including:
- `test_anchor_triangle_propagation_is_exact_sign_agnostic_and_keeps_the_incumbent` (new gate test)
- `test_highs_bridge_diagnoses_relaxation_gap` (previously blocked in runs 1 and 2)

### (b) incumbent.py

Command: `python3 incumbent.py`

```
minimum_area 0.032598858691819698218764006623515408
active_triangles 20
distinct_area_tiers 17
second_area 0.044370406987153863
active_orbit_sizes (4, 8, 8)
minimum_hitting_sets ((8, 9, 10, 11),)
active ((0, 2, 9), (0, 4, 8), (0, 4, 9), (0, 8, 10), (1, 3, 10), (1, 5, 8), (1, 5, 10), (1, 8, 9), (2, 6, 9), (2, 6, 11), (2, 10, 11), (3, 7, 10), (3, 7, 11), (3, 9, 11), (4, 5, 8), (4, 9, 11), (5, 10, 11), (6, 7, 11), (6, 8, 9), (7, 8, 10))
```

Exit 0, elapsed 0m0.184s.

### (c) decimal_verifier.py

Command: `python3 decimal_verifier.py`

```
minimum_area 0.032598858691819698218764006623515408049241988379776913777741905474205601650786197356667938855
active_triangles 20
second_area 0.044370406987153863211543091627759711453672796044365839397087692327799761362215049444887977252
active ((0, 2, 9), (0, 4, 8), (0, 4, 9), (0, 8, 10), (1, 3, 10), (1, 5, 8), (1, 5, 10), (1, 8, 9), (2, 6, 9), (2, 6, 11), (2, 10, 11), (3, 7, 10), (3, 7, 11), (3, 9, 11), (4, 5, 8), (4, 9, 11), (5, 10, 11), (6, 7, 11), (6, 8, 9), (7, 8, 10))
```

Exit 0, elapsed 0m0.026s.

### (d) tangent_certificate.py

Command: `python3 tangent_certificate.py`

```
orbit_weights (Qx(a0=Fraction(-4, 1), a1=Fraction(44, 1), a2=Fraction(-28, 1)), Qx(a0=Fraction(3, 1), a1=Fraction(-14, 1), a2=Fraction(8, 1)), Qx(a0=Fraction(1, 1), a1=Fraction(0, 1), a2=Fraction(0, 1)))
inward_normal Qx(a0=Fraction(-4, 1), a1=Fraction(34, 1), a2=Fraction(-22, 1))
inward_normal_decimal -0.370713120026876284610760824042171514
critical_minor Qx(a0=Fraction(-89, 2097152), a1=Fraction(419, 1048576), a2=Fraction(-9, 32768))
critical_minor_decimal 0.000000000933174599164018028363268593
certificate PASS
```

Exit 0, elapsed 0m0.278s.

### (e) n11_insertion.py

Command: `python3 n11_insertion.py`

```
fixed_n11_minimum 1/27
inserted_point (Fraction(1, 2), Fraction(1, 9))
new_double_minimum 1/27
full_n12_minimum 1/54
strictly_beats_incumbent False
active_constraints ('0-1', '0-3', '-(1-2)')
enumerated_bases 246905
nonsingular_bases 232134
```

Exit 0, elapsed 0m19.536s.

### (f) d4_interval_certificate.py

Command: `python3 d4_interval_certificate.py`

```
record_lower 0.032598858691819698218764006623515408
record_upper 0.032598858691819698218764006623515408
target_upper 0.032598858691819698218764833804127961
slack 1/1208925819614629174706176
visited_boxes 1843
discarded_boxes 922
maximum_depth 155
```

Exit 0, elapsed 0m13.495s.

---

## Step 4 — Traversal experiments

### Summary table (all six runs)

| run | policy | anchor | visited | discarded | triangle-upper | anchor-triangle | pending | max depth | anchor_trims | largest pending upper | strict-witnesses | status |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|---:|---|
| g | breadth | off | 40 | 0 | 0 | — | 41 | 5 | 0 | 0.217401141308180301800864 | 0 | INCOMPLETE |
| h | depth | off | 40 | 4 | 4 | — | 33 | 34 | 0 | 0.217401141308180301800864 | 0 | INCOMPLETE |
| i | breadth | off | 1000 | 0 | 0 | — | 1001 | 9 | 0 | 0.217401141308180301800864 | 0 | INCOMPLETE |
| j | depth | off | 1000 | 484 | 484 | — | 33 | 53 | 0 | 0.217401141308180301800864 | 0 | INCOMPLETE |
| k | breadth | anchored | 1000 | 0 | 0 | 0 | 1001 | 9 | 39 | 0.217401141308180301800864 | 0 | INCOMPLETE |
| l | depth | anchored | 1000 | 301 | 285 | 16 | 399 | 625 | 1856 | 0.217401141308180301800864 | 0 | INCOMPLETE |

### (g) 40-box breadth-first

Command: `python3 global_interval_branch.py --max-boxes 40 --queue-policy breadth`

```
visited_boxes 40
discarded_boxes 0
pending_boxes 41
maximum_depth 5
anchor_trims 0
largest_pending_upper 0.217401141308180301800864
strict_improvement_witnesses 0
complete False
discard_reasons {}
status INCOMPLETE: no global no-go claim
```

Exit 0, elapsed 0m7.333s.

Matches expected diagnostic exactly (breadth: visited 40, discarded 0, pending 41, max depth 5). ✓

### (h) 40-box depth-first

Command: `python3 global_interval_branch.py --max-boxes 40 --queue-policy depth`

```
visited_boxes 40
discarded_boxes 4
pending_boxes 33
maximum_depth 34
anchor_trims 0
largest_pending_upper 0.217401141308180301800864
strict_improvement_witnesses 0
complete False
discard_reasons {'triangle-upper': 4}
status INCOMPLETE: no global no-go claim
```

Exit 0, elapsed 0m6.170s.

Matches expected diagnostic exactly (depth: visited 40, discarded 4, pending 33, max depth 34). ✓

### (i) 1000-box breadth-first

Command: `python3 global_interval_branch.py --max-boxes 1000 --queue-policy breadth`

```
visited_boxes 1000
discarded_boxes 0
pending_boxes 1001
maximum_depth 9
anchor_trims 0
largest_pending_upper 0.217401141308180301800864
strict_improvement_witnesses 0
complete False
discard_reasons {}
status INCOMPLETE: no global no-go claim
```

Exit 0, elapsed 2m58.228s.

### (j) 1000-box depth-first

Command: `python3 global_interval_branch.py --max-boxes 1000 --queue-policy depth`

```
visited_boxes 1000
discarded_boxes 484
pending_boxes 33
maximum_depth 53
anchor_trims 0
largest_pending_upper 0.217401141308180301800864
strict_improvement_witnesses 0
complete False
discard_reasons {'triangle-upper': 484}
status INCOMPLETE: no global no-go claim
```

Exit 0, elapsed 1m33.062s.

### (k) 1000-box breadth-first, anchor-propagation anchored

Command: `python3 global_interval_branch.py --max-boxes 1000 --queue-policy breadth --anchor-propagation anchored`

```
visited_boxes 1000
discarded_boxes 0
pending_boxes 1001
maximum_depth 9
anchor_trims 39
largest_pending_upper 0.217401141308180301800864
strict_improvement_witnesses 0
complete False
discard_reasons {}
status INCOMPLETE: no global no-go claim
```

Exit 0, elapsed 4m5.096s.

anchor_trims: 39  
anchor-triangle discards: 0

### (l) 1000-box depth-first, anchor-propagation anchored

Command: `python3 global_interval_branch.py --max-boxes 1000 --queue-policy depth --anchor-propagation anchored`

```
visited_boxes 1000
discarded_boxes 301
pending_boxes 399
maximum_depth 625
anchor_trims 1856
largest_pending_upper 0.217401141308180301800864
strict_improvement_witnesses 0
complete False
discard_reasons {'anchor-triangle': 16, 'triangle-upper': 285}
status INCOMPLETE: no global no-go claim
```

Exit 0, elapsed 6m50.002s.

anchor_trims: 1856  
anchor-triangle discards: 16  
triangle-upper discards: 285  
total discarded: 301

---

## Scope guard

All six traversal runs terminate with `complete False` and a nonempty pending queue.
None of these runs constitute a global no-go certificate or record improvement claim.
The anchor-propagation is an exact optional reduction; it changes neither the meaning
of a completed cover nor the `INCOMPLETE` semantics of a finite budget.

---

## Overall result

**PASS** — all gates, tests, and traversal diagnostics completed without error.
No solver timeouts, numerical warnings, or unexpected nonzero exits.
No deviations from expected 40-box diagnostics.
