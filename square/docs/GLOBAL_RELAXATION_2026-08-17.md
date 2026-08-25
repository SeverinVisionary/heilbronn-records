# Global relaxation and interval campaign — 2026-08-17

## Scope

This is a global research track, not a claim that the `n = 12` problem is
solved. Conditional on the five-boundary theorem of Sudermann--Merx (2026), an
improving configuration has an optimizer that can be relabelled into this
normal form. Therefore, an exact completed cover of this form would rule out
every strict improvement.

The Comellas--Yebra value remains
`0.032598858691819698...`. No configuration above it was found or certified in
this campaign.

## Outer MILP relaxation

`global_mccormick_relaxation.py` replaces every directed product `x_i * y_j`
with a McCormick variable and uses binary orientation selectors for triangle
absolute values. It includes exact normal-form pins and orderings, ordered
product and rectangle RLT cuts, capacity-two strip grids at the proved target
`1/31`, and a rational `0.0549` cap derived from the certified `n = 9` value
and `Delta_n <= Delta_9` for `n >= 10`. With this target filter enabled, the
model is an outer relaxation of the **strict-improvement set**, not of every
normal-form configuration: `1/31` lies strictly below the incumbent.

Before product envelopes are emitted, the valid target difference constraints
are propagated into the coordinate box. In particular the two fixed left-edge
points fill the first 16-strip cell, and the ordered x-span triangles imply
`x_5 in [2/31,25/31]`, `x_7 in [4/31,27/31]`, and `x_11 >= 8/31` for any strict
improvement. The exact record still lies in this tightened box. The model also
uses factorized hulls that are absent from independent directed products:

- `w_i4-w_i0 = x_i(y_4-y_0)` for every non-left-edge point;
- `(w_right,other-w_left,other) = (x_right-x_left)y_other` (and the y-order
  analogue), including nonadjacent pairs in the ordered interior x-chain;
- `(x_right-x_left)(y_4-y_0)` expanded into four directed products for every
  nonadjacent interior x-pair.

Every one of these rows is checked at the exact cubic-field incumbent before a
model is emitted.

The optional joint x-cell/y-cell envelope uses continuous cell-AND variables.
Their two cell memberships are already binary, so the three AND rows force the
correct local rectangle at every integer solution. The exact cubic-field lift
checks the published record against every generated row family, including the
inactive big-M rows.

`highs_milp.py` accepts only the LP grammar emitted by the builder, rejects
unknown syntax, and reports both the MILP `z` and the actual 220-triangle
minimum of returned coordinates. It is a numerical bridge, never an exact
certificate.

## Reproducible diagnostics

All figures use target `1/31`, aligned 16- and 20-strip grids, and four coarse
cells per selected product. A cap-level MILP value is only a feasible point of
the outer relaxation. The first three rows are pre-propagation baselines; they
remain useful for documenting how the joint cuts move product error.

| Joint product set | HiGHS outcome | Actual coordinate minimum |
|---|---|---:|
| four selected products | optimal `z = 0.0549` | `0.00015615` |
| sixteen adaptive products | optimal `z = 0.0549` | `0.00156250` |
| twenty-eight adaptive products | 180-second limit; primal `0.047017...`, dual cap `0.0549` | `0.00028942` |
| all 132 products | 180-second limit before an integer feasible point | not available |
| four selected products after the left-chord hull | optimal `z = 0.0549` | `0.00128974` |
| ordered and transitive factorized hulls | 90-second limit; primal `0.03870967...`, dual cap `0.0549` | below `1e-16` |

The joint rows and factorized cuts are active: they change the MIP primal and
move product error, but they do **not** yield a geometric candidate or a global
upper bound near the record. After adding the transitive left-chord rectangles,
the current continuous root relaxation still optimizes numerically to `0.0549`.
That LP result has no point configuration attached and is not a certificate.

Two distinct cap-level relaxation coordinates were passed to the true nonlinear
epigraph polish in `global_normal_form_search.py`. They reached only about
`0.00964` and `0.01129`; their 24-bit dyadic snaps were exact non-improvements.

## Exact global interval track

`global_interval_branch.py` works entirely in `Fraction` arithmetic. For each
spatial box it takes the exact vertex maximum of every signed determinant and
uses the smallest of the 220 maxima as a rigorous upper bound on the box's
least triangle area. It re-propagates every target difference constraint after
each split, then discards a box if its enlarged coordinate intervals cannot
admit a capacity-two matching in aligned 16- or 20-strip grids or a shifted
16-strip partition. Both discard rules are one-sided and safe. A fully pinned
box above the incumbent is reported as an exact strict-improvement witness,
never hidden as a pending box.

The outer MILP track above continues to use the deliberately coarser `1/31`
target.  The exact branch now uses instead the 64-bisection rational lower
enclosure `0.032598858691819698199...` of the algebraic incumbent.  It is
strictly below the record in exact field arithmetic, so every strict record
improver survives, while `1/32 < target` keeps the same 16-strip capacity
theorem.  It also propagates the exact left-chord product consequence
`x_i * (y_4-y_0) > 2*target` for every non-left point.  The selector skips
coordinates whose determinant coefficient is identically zero; this changes
branch order only, never a cover or prune rule.

The branch also checks five aligned two-dimensional capacity-two grids:
`4x4`, `2x8`, `8x2`, `3x6`, and `6x3`.  Each cell has area below `2*target`,
so three points in it would determine a triangle below the target.  A
bipartite matching gives each interval box every closed grid cell it can meet;
failure is consequently an exact outer-box discard.  This is strictly stronger
than the one-dimensional tests: a regression box with
`y0=0`, `y4=1/8`, `x5=1/8`, and `y5=1/16` passes all strip matchings but fails
the rectangle matching.  The exact cubic-field incumbent is separately
enclosed by rational intervals and passes every rectangle grid.

A pre-propagation 1,000-box diagnostic discarded 44 boxes and left 913 pending
at depth at most 10, with a largest remaining vertex-hull upper bound of `1/2`.
The historical `1/31` target-propagation diagnostic had the midpoint policy
visit
1,000 boxes, discarded 35, left 931 pending at depth at most 9, and had largest
pending upper `0.199596774193548...`. The capacity-boundary policy discarded 39
and left 923 pending, but its largest pending upper `0.201108870967741...` was
slightly worse; both policies remain selectable rather than treating either as
dominant. Neither run found a strict-improvement witness. Both are explicitly
`INCOMPLETE` and prove no global no-go result.

At the current record-lower target with product propagation,
determinant-relevant selection, and the aligned rectangle grids, the 1,000-box
capacity diagnostic visited 1,000 boxes, discarded 0, left 1,001 pending at
depth 9, and had largest pending upper `0.21875`.  It found no witness and is
`INCOMPLETE`.  The new target and 2D rule are sounder/tighter necessary
conditions, but have not yet produced a throughput improvement under the
present breadth-first schedule; they are recorded as such rather than treated
as a new bound.

Traversal order is now explicit and does not alter the covered set or any
discard predicate.  The default `breadth` policy spreads a small budget over
the root cover; the alternative `depth` policy follows a narrow child until an
exact bound fires.  On the same record-lower root with midpoint splitting and a
40-box budget, breadth-first visited depth 5, discarded 0, and left 41 boxes;
depth-first reached depth 34, discarded 4 by the existing exact triangle-upper
rule, and left 33 boxes.  Both runs found no witness and remain `INCOMPLETE`.
This is a scheduling diagnostic only, not a new geometric inequality or a
global bound.

## Commands

```sh
cd research/heilbronn_n12
make global-highs-smoke
make global-interval-smoke

python3 highs_milp.py --n 12 --lower-target 1/31 --additional-strip-count 20 \
  --joint-piecewise-strips --piecewise-cells 4 \
  --piecewise-product 10,9 --piecewise-product 1,9 \
  --piecewise-product 11,8 --piecewise-product 1,7 --time-limit 90

# A nonzero budget remains incomplete by design.
python3 global_interval_branch.py --max-boxes 1000
python3 global_interval_branch.py --max-boxes 1000 --split-strategy capacity

# Explore a narrow exact branch early; still incomplete at any nonzero budget.
python3 global_interval_branch.py --max-boxes 40 --queue-policy depth
```

Sources: [Sudermann--Merx 2026](https://arxiv.org/html/2603.11107v2) and its
[reference implementation](https://github.com/spiralulam/heilbronn).
