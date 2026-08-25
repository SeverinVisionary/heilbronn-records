# 12-point unit-square Heilbronn research

This directory begins the executable part of [PR #8](https://github.com/SeverinVisionary/imo-gold/pull/8): maximize the least area among the 220 triangles determined by 12 points in `[0,1]^2`.

Before starting or resuming a campaign, read the current
[prior-art gate](PRIOR_ART.md), its
[2026-08-21 global novelty sweep](NOVELTY_GLOBAL_2026-08-20.md), and the
[2026-08-19 handoff](HANDOFF_2026-08-19.md). Heavy verification and search must
follow [CLOUD_JOB.md](CLOUD_JOB.md); it is not permitted on the operator's Mac.

## Frozen incumbent

The baseline is Comellas--Yebra's best-known `n = 12` configuration.  Let `x` be the root in `(0, 1/4)` of

```
4*x^3 - 12*x^2 + 10*x - 1 = 0
```

and let `y = 2*x^2 - 3*x + 1/2`.  The eight boundary points are

```
(x,0), (1-x,0), (x,1), (1-x,1),
(0,x), (1,x), (0,1-x), (1,1-x),
```

and the four interior points are

```
(1/2,y), (y,1/2), (1-y,1/2), (1/2,1-y).
```

Its minimum area is exactly `x/4 + x*y/2 - x^2/2`, approximately
`0.032598858691819698`.  That **area value** (not the coordinate `x`) is the
positive root of `64*z^3 + 80*z^2 + 28*z - 1`.  The source construction is
Comellas and Yebra, *New Lower Bounds for Heilbronn Numbers* (2002); the 2026
survey by Sudermann and Merx reports their `n = 12` configuration remains best
known.

## What is already reproducible

`incumbent.py` is the certification baseline.  It represents every coordinate and area in the exact cubic field `Q(x)`, isolates the boundary-coordinate root with rational bisection, enumerates all 220 triangles, and checks that the published formula is the exact minimum.  It also verifies the separate cubic for the record area, finds the `8+8+4` D4 active-triangle orbits, and recovers the unique minimum active-set hitting set (the four interior points).  It has an exact `Fraction` checker for later dyadic/rational candidates.

`decimal_verifier.py` independently reconstructs the same configuration using only `Decimal` arithmetic.  It is deliberately separate from the exact-field code, so a coordinate or determinant transcription error must pass two implementations to survive.

Run the reproducibility check with:

```
cd research/heilbronn_n12
make check
python3 incumbent.py
python3 decimal_verifier.py
```

The expected audit facts are a minimum of `0.032598858691819698...`, exactly 20 active triangles, and a strictly higher second area tier.  No rounded candidate is a record: a future candidate must be snapped to exact rationals and pass `strictly_beats_incumbent`.

## Next falsifiable steps

1. **Done:** `calibration.py` blind-recovers the known `n=8`, `n=9`, and `n=10` values from seeded structural templates.  The reproducible numerical gate and its scope are recorded in [CALIBRATION_2026-08-16.md](CALIBRATION_2026-08-16.md).
2. **Done:** `n11_insertion.py` exhaustively solves the exact one-point insertion problem for Goldberg's `n=11` configuration.  Its global optimum is insertion at `(1/2, 1/9)`, with full 12-point minimum `1/54`; it cannot beat the incumbent.  See [N11_INSERTION_RESULT.md](N11_INSERTION_RESULT.md).
3. **Done:** `d4_interval_certificate.py` gives an exact `2^-79`-wide bracket around the incumbent throughout its complete two-parameter D4 incidence family.  It is not a bound for every D4 pattern; see [D4_INTERVAL_CERTIFICATE_2026-08-16.md](D4_INTERVAL_CERTIFICATE_2026-08-16.md).
4. **Done:** [TRANSVERSAL_NO_GO.md](TRANSVERSAL_NO_GO.md) proves that changing any three or fewer labelled incumbent points cannot improve the minimum; the four interiors are the unique size-4 transversal.  Larger move sets remain open.
5. `frozen_boundary_search.py` runs the resulting eight-dimensional, four-interior-point stratum.  Its first eight seeded trials all re-enter the incumbent basin; see [FROZEN_BOUNDARY_2026-08-16.md](FROZEN_BOUNDARY_2026-08-16.md).  This is not an exhaustive search over larger move sets, and any apparent improvement must still be snapped to rationals and verified exactly.
6. **Done:** `tangent_certificate.py` gives an exact first-order local-isolation certificate at the incumbent: every nonzero feasible velocity lowers an active triangle at linear order.  It does not rule out remote configurations; see [TANGENT_CONE_CERTIFICATE_2026-08-16.md](TANGENT_CONE_CERTIFICATE_2026-08-16.md).
7. **Underway:** `transversal_search.py` systematically explores the three D4 size-5 support classes with their fixed complements and original-edge boundary incidences.  It records candidate provenance and D4-orbit distance but is numerical discovery only; see [SIZE5_TRANSVERSAL_SEARCH_2026-08-16.md](SIZE5_TRANSVERSAL_SEARCH_2026-08-16.md).
8. **Underway:** `c4_symmetry_search.py` explores the six-dimensional three-orbit C4 family, which contains the record but permits reflection-breaking configurations outside the two-parameter D4 certificate.  Its first four seeded trials re-entered a distinct rational `3/98` basin rather than improving; each reported point is dyadically audited.  See [C4_SYMMETRY_SEARCH_2026-08-17.md](C4_SYMMETRY_SEARCH_2026-08-17.md).
9. **Underway:** `c4_interval_certificate.py` is an exact six-dimensional Bernstein branch-and-bound over the full three-orbit C4 family.  Its parameterization contains the record and removes only orbit relabellings, while float values are scheduling hints rather than certificate inputs.  It completes a deliberately loose `2^-4` end-to-end bracket; the first target below `0.0549` remains explicitly incomplete after the 50,000-box orbit-radial run and subsequent exact seed-triangle-span diagnostics.  See [C4_INTERVAL_BRACKET_2026-08-17.md](C4_INTERVAL_BRACKET_2026-08-17.md).
10. **Underway:** `c2_boundary_search.py` examines an eight-dimensional half-turn boundary-incidence stratum that contains the record while breaking its C4/reflection constraints.  Its recorded four-seed campaign found no exact improvement; see [C2_BOUNDARY_SEARCH_2026-08-17.md](C2_BOUNDARY_SEARCH_2026-08-17.md).
11. **Underway:** `global_mccormick_relaxation.py` is an auditable five-boundary outer relaxation of the strict-improvement set.  It has exact incumbent lifts, factorized ordered-difference and transitive left-chord hulls, valid strip cuts, and optional joint x-cell/y-cell product envelopes.  `highs_milp.py` gives its HiGHS results an independent geometry readback, so an MILP epigraph is never confused with a point configuration.  See [GLOBAL_RELAXATION_2026-08-17.md](GLOBAL_RELAXATION_2026-08-17.md).
12. **Underway:** `global_interval_branch.py` is the exact `Fraction` branch-and-bound counterpart over the five-boundary normal form, conditional on the published boundary theorem.  It re-propagates target difference constraints, prunes only by concrete vertex-hull or strip-capacity rules, and surfaces an exact pinned improvement as a witness; a finite unresolved run reports `INCOMPLETE`.
13. **Underway:** `global_normal_form_search.py` performs blind numerical discovery over all 19 free coordinates of that same normal form, then signs-and-polishes the discovered cell and exactly audits a dyadic snap.  Its first four high-budget independent trials found no exact improvement; see [GLOBAL_NORMAL_FORM_SEARCH_2026-08-17.md](GLOBAL_NORMAL_FORM_SEARCH_2026-08-17.md).
