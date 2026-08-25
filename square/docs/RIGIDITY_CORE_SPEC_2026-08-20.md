# Spec: minimal rigid core of the active-triangle hypergraph (teeth test)

**Date:** 2026-08-20. **Status:** spec for the first milestone of the
post-review direction; implements the two-week teeth test of avenue 5.1 in
[PROFESSOR_REVIEW_2026-08-20.md](PROFESSOR_REVIEW_2026-08-20.md).

## Objective

Find every inclusion-minimal subhypergraph `H` of the 20 incumbent-active
triangles whose first-order critical cone is already trivial, with a
two-sided exact certificate for every subset scanned. This upgrades the
existing all-20 tangent-cone certificate
([TANGENT_CONE_CERTIFICATE_2026-08-16.md](TANGENT_CONE_CERTIFICATE_2026-08-16.md))
into the rigid-core object the rigidity paper and any future global
argument would quote.

## Definitions

Coordinates follow `tangent_certificate.py`: 24 coordinates for 12 points;
points 0-3 sit on the bottom/top edges, 4-7 on the left/right edges, 8-11
are interior. That yields 8 inward boundary-normal coordinates (with the
inward orientation of `_assert_certificate_shape`) and 16 free coordinates
(8 boundary-tangential + 8 interior, `FREE_COORDINATES` order).

For a velocity `v` in R^24, feasibility means every inward normal
component is >= 0 (boundary points may only move inward at first order);
free components are unconstrained. For an active triangle `e`, `D_e(v)` is
the exact derivative of its unsigned area (`unsigned_area_gradient`).

For `H` a subset of the 20 active triangles:

```text
C(H) = { v feasible : D_e(v) >= 0 for every e in H }.
```

`H` is a **rigid core** when `C(H) = {0}`: every nonzero feasible velocity
strictly decreases some triangle of `H`.

## Certificates (both sides exact, no numeric verdicts)

**RIGID(H)** requires two exact objects, verified in `Q(x)`:

1. *Strict stress.* Weights `y_e > 0` (`e in H`, sign-checked by root
   isolation) such that `G(y) = sum y_e grad A_e` vanishes identically on
   all 16 free coordinates and is strictly negative on each of the 8
   inward normal coordinates. Then for feasible `v`,
   `sum y_e D_e(v) = <G(y), v> <= 0`, while `D_e(v) >= 0` for all `e`
   forces the sum `>= 0`; equality kills every inward component (strictly
   negative coefficients) and every `D_e(v)` (strictly positive weights).
2. *Rank.* The `|H| x 16` matrix of free-coordinate gradients has exact
   rank 16, so `D_e(v) = 0` for all `e in H` together with zero inward
   components forces `v = 0`.

**NONRIGID(H)** requires one exact object: a nonzero feasible `v` with
`D_e(v) >= 0` for every `e in H` (all signs checked exactly). Sources:
a kernel vector of the free-coordinate system when the rank is below 16,
or an inward unit vector at a boundary point whose normal coordinate no
triangle of `H` reaches.

A subset where neither certificate is found is reported **UNDECIDED**,
never resolved by a solver status. (The stress search uses float LP only
to *propose* rational weights; every accepted certificate re-verifies all
signs and identities in `Q(x)`.)

## Search space

Rank 16 forces `|H| >= 16`, so the scan enumerates all subsets of the 20
active triangles with `16 <= |H| <= 20` — 6,196 subsets, each classified
with a certificate. Minimal rigid cores are the RIGID subsets none of
whose one-triangle-deletions is RIGID. Cores are reported both raw and
deduplicated by the D4 action on the active set (`active_structure`
orbits).

## Gates

- **Positive control:** `H = all 20` must come out RIGID, and the
  orbit-constant stress must reproduce the committed `ORBIT_WEIGHTS`
  certificate shape (inward normal `-4 + 34x - 22x^2`) exactly.
- **Negative controls:** (a) any `H` with `|H| = 15` fails the rank bound
  by construction — assert the scan refuses it; (b) delete all triangles
  meeting one chosen boundary point's normal: the explicit inward unit
  vector must certify NONRIGID exactly; (c) a deliberately mis-signed
  stress (one weight negated) must fail the exact re-verification.
- **No implicit parameters:** the 16/8 coordinate split and orbit sizes
  (4, 8, 8) are asserted, not assumed.
- **Completeness certificate:** the run asserts
  `classified == C(20,16)+C(20,17)+C(20,18)+C(20,19)+C(20,20) == 6196`
  and prints the RIGID / NONRIGID / UNDECIDED counts; any UNDECIDED > 0
  is reported prominently and blocks the "minimal core" claim for the
  affected sizes.

## Part B (sampling, numerical; separate job step)

Generate independently optimized near-record configurations at thresholds
`z0 - 1e-4`, `z0 - 1e-5`, `z0 - 1e-6` (hundreds per threshold, reusing the
`global_normal_form_search.py` optimizer), quotient by D4, and record each
sample's near-active hypergraph (triangles within `delta` of its minimum,
`delta` in {1e-3, 1e-4}). Compare against the minimal cores from Part A.
Numerical output here is descriptive statistics only — no exactness claim.

## Teeth / kill criteria (professor's, adopted verbatim in substance)

- **Teeth:** a small rigid core exists, has a large exact dual margin, and
  (Part B) recurs inside the near-active hypergraph of essentially every
  near-record sample.
- **Dead:** near-record samples exhibit many unrelated flexible
  hypergraphs, or no rigid core below the full 20 exists and the dual
  margin is tiny. If dead, the lever is dropped and the rigidity paper
  proceeds with the all-20 certificate as-is.
