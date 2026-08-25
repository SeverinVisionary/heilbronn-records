# C4 interval-bracket campaign — 2026-08-17

## Scope

`c4_interval_certificate.py` is an exact branch-and-bound engine for the
full three-orbit `C4` family: configurations invariant under a quarter turn
about the centre of the unit square.  It is a strict extension of the earlier
two-parameter D4-incidence certificate because it allows all three C4 orbit
seeds to break reflection symmetry.

This is **not** a certificate for arbitrary 12-point configurations and it is
not a claim that the Heilbronn problem is solved.  A completed run establishes
only its stated epsilon bracket inside this C4 family.  In particular, a
target `record + epsilon` cannot rule out an improvement smaller than
`epsilon`.

For a 12-point configuration with distinct points, there is no missing
smaller C4 orbit type: a noncentral point has a four-point orbit under a
quarter turn, while the centre is the sole fixed point.  A distinct
12-point C4-invariant set therefore consists of exactly three four-point
orbits.  (A repeated centre or another coincident point has minimum area zero
and cannot improve the record.)

## Canonical parameter box

Each orbit has one representative in the closed south-east quadrant
`[1/2,1] x [0,1/2]`.  Writing those representatives as

```
(a0,b0), (a1,b1), (a2,b2),
```

and relabelling orbits so `a0 <= a1 <= a2` gives a six-dimensional root box
that still covers every C4 point set.  The Comellas--Yebra configuration is
covered by the sorted representatives

```
(1/2, y), (1-x, 0), (1, x),
```

where `x` and `y` are the exact cubic-field coordinates used by `incumbent.py`.

## Exact bounding rule

Each of the 220 signed double-area determinants is expanded as a polynomial in
the six parameters.  It has degree at most two in every parameter.  On each
rational parameter box, the engine converts that polynomial to tensor-product
Bernstein form using only `Fraction` arithmetic.  The Bernstein convex-hull
property yields a rigorous upper bound on the absolute determinant, hence a
rigorous upper bound on the least triangle area.  A box can also be discarded
by a separately stated, `Fraction`-exact necessary consequence of a named
triangle target; those consequences are documented and accounted for below.

NumPy evaluates the same coefficient transformation only to select a likely
triangle and a split coordinate.  Floating point never decides a prune,
certificate, or candidate.  The engine also applies the existing 16/20-strip
capacity matching as a necessary condition: any configuration exceeding the
record-plus-slack target also exceeds the global brancher's 64-bisection
rational lower enclosure of the record (and hence `1/31`), so it must pass
that independent grid test.  Its coordinate image is enlarged before matching,
making a failed match a safe C4-box discard.

## Calibration

As an end-to-end exactness check, the complete C4 cover at the intentionally
loose slack `2^-4` visited 9 boxes, discarded 5, and left no pending boxes.
Its rational target was `0.095098858691819698...`, which is weaker than the
existing `0.0549` global bound from the certified nine-point result.  It is
therefore a replayable certificate-engine sanity check, not a new numerical
bound for the problem.

### Initial Bernstein baseline (before radial target propagation)

With 96 bisections for the algebraic record enclosure and a coarse slack of
`2^-12`, the exact target was

```
0.032842999316819698218764006627...
```

The root's exact Bernstein least-area upper bound is `1/8`.  A bounded
midpoint campaign produced:

| Split policy | Box budget | Discarded exactly | Pending | Max depth | Strict witnesses | Status |
|---|---:|---:|---:|---:|---:|---|
| midpoint | 1,000 | 214 | 573 | 11 | 0 | incomplete |
| midpoint | 10,000 | 3,958 | 2,085 | 17 | 0 | incomplete |
| capacity | 10,000 | 3,961 | 2,079 | 17 | 0 | incomplete |
| capacity + best-upper queue | 10,000 | 2,901 | 4,199 | 248 | 0 | incomplete |

At 1,000 boxes, capacity-boundary splitting had the same summary as midpoint
splitting.  At 10,000 it was marginally ahead in both exact prunes and pending
boxes, so both policies remain available rather than over-reading a small
diagnostic.  No capacity matching prune had yet triggered in the 1,000-box
audit; that is not evidence against the capacity rule at deeper cells.

A best-upper queue is also available, but this first matched 10,000-box trial
chased a very deep easy-to-prune path (depth 248) and left more boxes pending.
Breadth-first therefore remains the default; queue order changes neither the
exact Bernstein rule nor the set covered by a completed run.

### Orbit-radial propagation baseline

For a strict target violator, each C4 orbit's own three-point triangle must
exceed the target:

```
(a - 1/2)^2 + (1/2 - b)^2 > target.
```

`target_propagated_box` applies this condition after every split using a
dyadic lower enclosure of the required square root.  The enclosure is only
used to weaken the circle boundary, so it can retain extra values but cannot
exclude a strict target violator.  Every child rejected by this propagation is
recorded with an exact `orbit-triangle` or ordering reason; subsequent
Bernstein and capacity discards remain separately recorded.

With the current propagation and capacity splitting, the first bracket below
the `0.0549` global cap remains incomplete:

| Slack | Box budget | Discarded | Pending | Max depth | Strict witnesses | Status |
|---:|---:|---:|---:|---:|---:|---|
| `2^-6` | 1,000 | 455 | 91 | 28 | 0 | incomplete |
| `2^-6` | 5,000 | 1,242 | 2,517 | 35 | 0 | incomplete |
| `2^-6` | 50,000 | 6,249 | 37,503 | 40 | 0 | incomplete |

The target at `2^-6` is `0.048223858691819698...`.  All recorded 1,000- and
50,000-box discards were exact Bernstein target certificates; no capacity or
orbit-circle whole-box rejection had yet fired in those traces.  The radial
tightening improves early pruning but does not solve the remaining
cross-triangle feasibility coupling.

No configuration above the incumbent was found or certified.  The next
falsifiable milestones are completion at progressively smaller slacks and a
direct comparison of midpoint versus capacity splitting at a shared deeper
budget.

### Seed-triangle span propagation (current diagnostic)

The three ordered south-east representatives are labelled `0`, `4`, and `8`.
Their triangle is contained in a rectangle with

```
W = a2 - a0,
H = max(b0,b1,b2) - min(b0,b1,b2).
```

Every triangle in a `W`-by-`H` rectangle has area at most `W*H/2`.  Thus a
strict target violator must satisfy `W > 2*target/H`.  The engine first drops a
box when its exact rectangle upper bound is at most the target; otherwise it
tightens only the two ordered horizontal endpoint intervals using that strict
necessary span.  It does not choose a determinant sign or use a floating-point
bound.

At the same `2^-6` target, two new bounded diagnostics gave:

| Split policy | Box budget | Discarded | Pending | Max depth | Strict witnesses | Exact discard reasons | Status |
|---|---:|---:|---:|---:|---:|---|---|
| midpoint | 1,000 | 403 | 208 | 13 | 0 | 390 Bernstein; 13 seed-rectangle | incomplete |
| capacity | 1,000 | 409 | 196 | 13 | 0 | 396 Bernstein; 13 seed-rectangle | incomplete |

These are diagnostics rather than a comparison against the radial-only table:
tightening changes the scheduling geometry and therefore the first 1,000
visited cells.  They establish only that the new exact rule fires and that no
strict C4 witness was found in those finite runs; they do not establish a C4
bracket or improve the global bound.

## Reproduction

```sh
cd research/heilbronn_n12

# This completes, but is deliberately much too loose to be a useful bound.
python3 c4_interval_certificate.py --max-boxes 0 --slack-bits 4 --root-bisections 96

# A finite run is deliberately reported as INCOMPLETE.
python3 c4_interval_certificate.py --max-boxes 1000 --slack-bits 12 --root-bisections 96
python3 c4_interval_certificate.py --max-boxes 1000 --slack-bits 12 --root-bisections 96 \
  --split-strategy capacity

# First target below the known global cap; still incomplete at finite budgets.
python3 c4_interval_certificate.py --max-boxes 50000 --slack-bits 6 --root-bisections 96 \
  --split-strategy capacity
```
