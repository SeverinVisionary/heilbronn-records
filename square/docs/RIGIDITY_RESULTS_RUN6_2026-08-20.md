# Rigidity teeth test — RUN 6 (2026-08-20)

**Scope of this document.** Run 6 is composed of

- Part A **rescan** of `rigidity_core.py` — the exact rescan that
  incorporates the Stiemke resolver intended to close the 24 UNDECIDED
  subsets left open in RUN 5, and
- Part B **sampling campaign chunks 1–6** — six independent chunks of
  `rigidity_sampling.py` at `trials=50`, `popsize=16`, `maxiter=600`
  seeded at `2026082001, 2026082051, 2026082101, 2026082151, 2026082201,
  2026082251`, over the three Part-A minimal-core lists carried forward
  from RUN 5.

Every printed value is preserved verbatim. Part A is a first-order
rigidity statement at the incumbent — **NOT** global optimality, **NOT**
a record claim. Part B is descriptive floating-point sampling only —
**no** exactness claims and **no** candidate records may be quoted from
its output. Kept-sample scarcity (even a kept-count of 0) is a
descriptive result, never a failure. Both tools' own status lines are
preserved exactly.

## Step 0: environment gate

```
$ uname -a; hostname; whoami; nproc; free -h; python3 --version
Linux vm 6.18.5-fc-v20 #1 SMP PREEMPT_DYNAMIC @0 x86_64 x86_64 x86_64 GNU/Linux
vm
root
4
               total        used        free      shared  buff/cache   available
Mem:            15Gi       691Mi        14Gi       4.8Mi       555Mi        15Gi
Swap:             0B          0B          0B
Python 3.11.15
```

`uname -s` is `Linux`, not `Darwin`; the hostname is `vm`, not
not the operator's personal machine. Proceeded.

## Step 1: pinned checkout

Branch `cloud/heilbronn-n12-verify-6`, set up to track
`origin/codex/heilbronn-n12-global`.

```
$ git rev-parse HEAD
f93765e9e9cb5fe9bc5c77091192ec0d25048a5f
```

Matches the required pinned sha exactly. Working tree clean before compute.

## Step 2: dependencies

`python3 -m pip install -r requirements-research.txt` succeeded. Installed:

- numpy 2.0.2
- scipy 1.13.1

## Step 3(a): regression gate — `python3 -m unittest -v`

Executed in `<repo>`.
Log: `$HOME/heilbronn_logs/step_a_unittest.log` (outside the repo).
**Exit code: 0**
**Elapsed: 73.851 s** (unittest banner: `Ran 32 tests in 73.306s`)

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
Ran 32 tests in 73.306s

OK
```

## Step 3(b): full rigid-core rescan — `python3 rigidity_core.py`

Executed in `<repo>`.
Log: `$HOME/heilbronn_logs/step_b_scan.log` + `step_b_scan.err` (outside the repo).
**Exit code: 0**
**Elapsed: 22 m 53.062 s** (real); user 22m52.981s, sys 0m0.420s

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
core (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17) orbit_signature (4, 8, 6) d4_copies 4 least_negative_normal -0.058898129370378365988780
core (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15, 16, 18, 19) orbit_signature (2, 8, 8) d4_copies 2 least_negative_normal -0.250749824879366057668676
core (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 16, 18, 19) orbit_signature (3, 8, 6) d4_copies 8 least_negative_normal -0.036267268683650145293539
status COMPLETE: every subset in the scanned sizes carries an exact certificate
```

### stderr (verbatim):

```
real	22m53.062s
user	22m52.981s
sys	0m0.420s
```

### Run-5 vs Run-6 census comparison

| Size | Status    | RUN 5 | RUN 6 | Delta   | Note |
|------|-----------|-------|-------|---------|------|
| 16   | NONRIGID  | 4845  | 4845  | 0       | |
| 17   | NONRIGID  | 1116  | 1132  | +16     | former UNDECIDED, now resolved NONRIGID |
| 17   | RIGID     | 8     | 8     | 0       | unchanged |
| 17   | UNDECIDED | 16    | 0     | −16     | fully resolved by Stiemke resolver |
| 18   | NONRIGID  | 156   | 164   | +8      | former UNDECIDED, now resolved NONRIGID |
| 18   | RIGID     | 6     | 6     | 0       | unchanged |
| 18   | RIGID-by-monotonicity | 20 | 20 | 0 | unchanged |
| 18   | UNDECIDED | 8     | 0     | −8      | fully resolved by Stiemke resolver |
| 19   | NONRIGID  | 8     | 8     | 0       | |
| 19   | RIGID-by-monotonicity | 12 | 12 | 0 | unchanged |
| 20   | RIGID-by-monotonicity | 1  | 1  | 0 | unchanged |

Size-consistency checks (per-size totals must be equal across runs):
- Size 17: run-5 total = 1116+8+16 = **1140**; run-6 = 1132+8 = **1140** ✓
- Size 18: run-5 total = 156+6+20+8 = **190**; run-6 = 164+6+20 = **190** ✓

The 24 UNDECIDED subsets (16 at size 17, 8 at size 18) have been entirely
resolved by the Stiemke resolver; all 24 resolved as NONRIGID. No
previously-RIGID core has vanished. Minimal-core count and D4 orbit
structure are unchanged.

**Minimal rigid cores (verbatim from scanner, unchanged from run 5):**

| Core (triangle indices) | Size | Orbit sig | D4 copies | Least-neg normal margin |
|---|---|---|---|---|
| `(0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17)` | 18 | (4,8,6) | 4 | −0.058898129370378365988780 |
| `(0,1,2,3,4,5,6,7,8,9,10,11,12,13,15,16,18,19)` | 18 | (2,8,8) | 2 | −0.250749824879366057668676 |
| `(0,1,2,3,4,5,6,7,8,9,10,11,12,14,16,18,19)` | 17 | (3,8,6) | 8 | −0.036267268683650145293539 |

D4 copy check: 4 + 2 + 8 = 14 raw minimal cores ✓

**Status line (verbatim):**
```
status COMPLETE: every subset in the scanned sizes carries an exact certificate
```

The status is now `COMPLETE` (was `COMPLETE-WITH-UNDECIDED` in run 5).
Minimality claims are now unconditional within the scanned sizes.

## Step 3(c): sampling chunk 1 — seed-base 2026082001

Command:
```
python3 rigidity_sampling.py --trials 50 --seed-base 2026082001 \
  --popsize 16 --maxiter 600 \
  --cores "0,1,2,3,4,5,6,7,8,9,10,11,12,14,16,18,19;\
0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17;\
0,1,2,3,4,5,6,7,8,9,10,11,12,13,15,16,18,19"
```

**Exit code: 0**
**Elapsed: 16 m 38.744 s** (real); user 16m38.868s, sys 0m0.163s

Complete stdout (verbatim):
```
DESCRIPTIVE-ONLY: float statistics; no exactness claims; no candidate records
incumbent_float 0.0325988586918197
thresholds (0.0324988586918197, 0.0325888586918197, 0.0325978586918197)
trials 50 popsize 16 maxiter 600
threshold 0.032498859 kept 0 of 50
threshold 0.032588859 kept 0 of 50
threshold 0.032597859 kept 0 of 50
status DESCRIPTIVE: sampling evidence only; rigidity verdicts come from the exact Part A scan
```

## Step 3(d): sampling chunk 2 — seed-base 2026082051

Command:
```
python3 rigidity_sampling.py --trials 50 --seed-base 2026082051 \
  --popsize 16 --maxiter 600 \
  --cores "0,1,2,3,4,5,6,7,8,9,10,11,12,14,16,18,19;\
0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17;\
0,1,2,3,4,5,6,7,8,9,10,11,12,13,15,16,18,19"
```

**Exit code: 0**
**Elapsed: 16 m 25.529 s** (real); user 16m25.757s, sys 0m0.140s

Complete stdout (verbatim):
```
DESCRIPTIVE-ONLY: float statistics; no exactness claims; no candidate records
incumbent_float 0.0325988586918197
thresholds (0.0324988586918197, 0.0325888586918197, 0.0325978586918197)
trials 50 popsize 16 maxiter 600
threshold 0.032498859 kept 0 of 50
threshold 0.032588859 kept 0 of 50
threshold 0.032597859 kept 0 of 50
status DESCRIPTIVE: sampling evidence only; rigidity verdicts come from the exact Part A scan
```

## Step 3(e): sampling chunk 3 — seed-base 2026082101

Command:
```
python3 rigidity_sampling.py --trials 50 --seed-base 2026082101 \
  --popsize 16 --maxiter 600 \
  --cores "0,1,2,3,4,5,6,7,8,9,10,11,12,14,16,18,19;\
0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17;\
0,1,2,3,4,5,6,7,8,9,10,11,12,13,15,16,18,19"
```

**Exit code: 0**
**Elapsed: 16 m 34.472 s** (real); user 16m34.666s, sys 0m0.111s

Note: stderr contained a scipy SLSQP RuntimeWarning (values clipped to bounds
during optimizer step); this is expected numerical behavior and does not affect
the kept-sample counts.

Complete stdout (verbatim):
```
DESCRIPTIVE-ONLY: float statistics; no exactness claims; no candidate records
incumbent_float 0.0325988586918197
thresholds (0.0324988586918197, 0.0325888586918197, 0.0325978586918197)
trials 50 popsize 16 maxiter 600
threshold 0.032498859 kept 0 of 50
threshold 0.032588859 kept 0 of 50
threshold 0.032597859 kept 0 of 50
status DESCRIPTIVE: sampling evidence only; rigidity verdicts come from the exact Part A scan
```

## Step 3(f): sampling chunk 4 — seed-base 2026082151

Command:
```
python3 rigidity_sampling.py --trials 50 --seed-base 2026082151 \
  --popsize 16 --maxiter 600 \
  --cores "0,1,2,3,4,5,6,7,8,9,10,11,12,14,16,18,19;\
0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17;\
0,1,2,3,4,5,6,7,8,9,10,11,12,13,15,16,18,19"
```

**Exit code: 0**
**Elapsed: 18 m 10.720 s** (real); user 18m10.916s, sys 0m0.144s

Complete stdout (verbatim):
```
DESCRIPTIVE-ONLY: float statistics; no exactness claims; no candidate records
incumbent_float 0.0325988586918197
thresholds (0.0324988586918197, 0.0325888586918197, 0.0325978586918197)
trials 50 popsize 16 maxiter 600
threshold 0.032498859 kept 0 of 50
threshold 0.032588859 kept 0 of 50
threshold 0.032597859 kept 0 of 50
status DESCRIPTIVE: sampling evidence only; rigidity verdicts come from the exact Part A scan
```

## Step 3(g): sampling chunk 5 — seed-base 2026082201

Command:
```
python3 rigidity_sampling.py --trials 50 --seed-base 2026082201 \
  --popsize 16 --maxiter 600 \
  --cores "0,1,2,3,4,5,6,7,8,9,10,11,12,14,16,18,19;\
0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17;\
0,1,2,3,4,5,6,7,8,9,10,11,12,13,15,16,18,19"
```

**Exit code: 0**
**Elapsed: 16 m 21.080 s** (real); user 16m21.293s, sys 0m0.112s

Complete stdout (verbatim):
```
DESCRIPTIVE-ONLY: float statistics; no exactness claims; no candidate records
incumbent_float 0.0325988586918197
thresholds (0.0324988586918197, 0.0325888586918197, 0.0325978586918197)
trials 50 popsize 16 maxiter 600
threshold 0.032498859 kept 0 of 50
threshold 0.032588859 kept 0 of 50
threshold 0.032597859 kept 0 of 50
status DESCRIPTIVE: sampling evidence only; rigidity verdicts come from the exact Part A scan
```

## Step 3(h): sampling chunk 6 — seed-base 2026082251

Command:
```
python3 rigidity_sampling.py --trials 50 --seed-base 2026082251 \
  --popsize 16 --maxiter 600 \
  --cores "0,1,2,3,4,5,6,7,8,9,10,11,12,14,16,18,19;\
0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17;\
0,1,2,3,4,5,6,7,8,9,10,11,12,13,15,16,18,19"
```

**Exit code: 0**
**Elapsed: 16 m 25.137 s** (real); user 16m25.359s, sys 0m0.120s

Complete stdout (verbatim):
```
DESCRIPTIVE-ONLY: float statistics; no exactness claims; no candidate records
incumbent_float 0.0325988586918197
thresholds (0.0324988586918197, 0.0325888586918197, 0.0325978586918197)
trials 50 popsize 16 maxiter 600
threshold 0.032498859 kept 0 of 50
threshold 0.032588859 kept 0 of 50
threshold 0.032597859 kept 0 of 50
status DESCRIPTIVE: sampling evidence only; rigidity verdicts come from the exact Part A scan
```

## Totals (Part B — chunks 1–6 combined)

| Chunk | Seed-base  | Trials | Exit | Elapsed (real) | Kept (all thresholds) |
|-------|------------|--------|------|----------------|-----------------------|
| 1     | 2026082001 | 50     | 0    | 16m38.744s     | 0 / 0 / 0             |
| 2     | 2026082051 | 50     | 0    | 16m25.529s     | 0 / 0 / 0             |
| 3     | 2026082101 | 50     | 0    | 16m34.472s     | 0 / 0 / 0             |
| 4     | 2026082151 | 50     | 0    | 18m10.720s     | 0 / 0 / 0             |
| 5     | 2026082201 | 50     | 0    | 16m21.080s     | 0 / 0 / 0             |
| 6     | 2026082251 | 50     | 0    | 16m25.137s     | 0 / 0 / 0             |

_Columns "Kept" show count at thresholds
0.032498859 / 0.032588859 / 0.032597859 respectively._

**Total trials: 300** (6 × 50)

**Total kept per threshold:**
- threshold 0.032498859 (−1×10⁻⁴ below incumbent): **0** of 300
- threshold 0.032588859 (−1×10⁻⁵ below incumbent): **0** of 300
- threshold 0.032597859 (−1×10⁻⁶ below incumbent): **0** of 300

**Matched to incumbent orbit:** N/A — no samples kept at any threshold.

**Core-coverage counts:** N/A — no matched samples.

**Distinct unmatched hypergraphs:** N/A — no samples kept at any threshold.

All 300 trials failed to reach the loosest near-record threshold. This is
a descriptive result: the differential evolution optimizer (popsize 16,
maxiter 600) did not produce any configuration with minimum triangle area
at or above incumbent − 10⁻⁴ across 300 independent seeds. No exactness
claims and no candidate-record claims may be derived from this output.

## Scope guard (reiterated verbatim from dispatch)

Part A is a first-order rigidity statement at the incumbent — NOT
global optimality, NOT a record claim. Part B is descriptive sampling —
no exactness claims. Both tools' own status lines are preserved exactly
in this document.
