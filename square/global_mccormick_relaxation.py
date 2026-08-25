"""Auditable global MILP outer relaxation for the unit-square Heilbronn problem.

The continuous coordinates use the five-boundary-point normal form of
Sudermann--Merx (2026).  Each product ``x_i * y_j`` is replaced by its four
McCormick envelope inequalities, and each triangle gets a binary orientation
selector.  With no target filter, every configuration in the normal form maps
to a feasible MILP point with the same minimum triangle area.  With a positive
target filter, the model instead contains every normal-form configuration that
can strictly beat the incumbent (the target is chosen below that value).  In
either scope, an optimal MILP value is an outer upper bound for the
corresponding geometric question.

This module writes a CPLEX-LP model and can run GLPK when available.  GLPK uses
floating arithmetic, so a solver-reported bound is an auditable numerical outer
bound, not an exact mathematical certificate.  It is deliberately calibrated
on small n before any n=12 result is interpreted.

The five-boundary normal form is justified by Proposition 2 and the
symmetry-breaking construction in Sudermann--Merx, "From Computational
Certification to Exact Coordinates: Heilbronn's Triangle Problem on the Unit
Square Using Mixed-Integer Optimization" (2026), arXiv:2603.11107.  The source
implementation is https://github.com/spiralulam/heilbronn.
"""

from __future__ import annotations

import argparse
import math
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations
from pathlib import Path
from typing import Iterable, Literal, Mapping, Sequence, Tuple

from incumbent import Qx, algebraic_bounds, incumbent_points, incumbent_value, sign, signed_double_area


Triangle = Tuple[int, int, int]
Interval = Tuple[Fraction, Fraction]


@dataclass(frozen=True)
class RelaxationModel:
    """The LP text and exact metadata used to construct it."""

    n: int
    triangles: Tuple[Triangle, ...]
    binary_triangles: Tuple[Triangle, ...]
    coordinate_bounds: Mapping[str, Interval]
    area_upper_bound: Fraction
    big_m: Fraction
    lower_target: Fraction | None
    strip_count: int | None
    additional_strip_counts: Tuple[int, ...]
    piecewise_strip_products: bool
    joint_piecewise_strip_products: bool
    piecewise_cell_count: int | None
    piecewise_product_pairs: Tuple[Tuple[int, int], ...] | None
    text: str

    @property
    def product_count(self) -> int:
        return self.n * (self.n - 1)

    @property
    def binary_count(self) -> int:
        counts = () if self.strip_count is None else (self.strip_count,) + self.additional_strip_counts
        strip_binaries = 2 * self.n * sum(counts)
        return len(self.binary_triangles) + strip_binaries


@dataclass(frozen=True)
class SpatialBox:
    """A closed coordinate subbox of the canonical five-boundary domain."""

    coordinate_bounds: Mapping[str, Interval]
    depth: int = 0


@dataclass(frozen=True)
class WitnessVerification:
    """Exact row-level verification of a geometric witness lift."""

    n: int
    minimum_area: Fraction
    checked_products: int
    checked_triangles: int


@dataclass(frozen=True)
class IncumbentLift:
    """Exact strip assignments lifting the known n=12 witness into a model."""

    lower_target: Fraction
    strip_count: int
    x_strips: Tuple[int, ...]
    y_strips: Tuple[int, ...]
    additional_strip_counts: Tuple[int, ...] = ()
    additional_x_strips: Tuple[Tuple[int, ...], ...] = ()
    additional_y_strips: Tuple[Tuple[int, ...], ...] = ()


@dataclass(frozen=True)
class SolverReport:
    """Unrounded data reported by a numerical GLPK solve."""

    command: Tuple[str, ...]
    returncode: int
    status: str
    incumbent: float | None
    reported_upper: float | None
    output: str


RoundDirection = Literal["nearest", "down", "up"]


def _decimal(value: Fraction, direction: RoundDirection = "nearest") -> str:
    """Render an LP coefficient, optionally one IEEE step outwards.

    The model metadata retains the exact ``Fraction``.  This renderer is only
    for a numerical solver invocation.  For an inequality, coefficients and
    right-hand sides are emitted in the direction that enlarges the exact
    feasible set, rather than accidentally narrowing it through nearest-float
    conversion.  GLPK tolerances still mean solver output is not a certificate.
    """

    if direction not in ("nearest", "down", "up"):
        raise ValueError(f"unknown decimal rounding direction {direction!r}")
    numeric = float(value)
    if direction != "nearest" and Fraction.from_float(numeric) != value:
        numeric = math.nextafter(numeric, -math.inf if direction == "down" else math.inf)
    return repr(numeric)


def _variable(prefix: str, index: int) -> str:
    return f"{prefix}_{index}"


def _product(left: int, right: int) -> str:
    if left == right:
        raise ValueError("determinants never require a diagonal product")
    return f"w_{left}_{right}"


def _sign(triangle: Triangle) -> str:
    return "b_" + "_".join(str(index) for index in triangle)


def _triangle_name(triangle: Triangle) -> str:
    return "_".join(str(index) for index in triangle)


def _linear(terms: Iterable[Tuple[Fraction, str]], direction: RoundDirection = "nearest") -> str:
    """Render a nonempty affine expression with directed coefficient rounding."""

    rendered: list[str] = []
    for coefficient, variable in terms:
        if coefficient == 0:
            continue
        magnitude = abs(coefficient)
        if direction == "nearest":
            magnitude_direction: RoundDirection = "nearest"
        elif (direction == "down") == (coefficient > 0):
            magnitude_direction = "down"
        else:
            magnitude_direction = "up"
        atom = variable if magnitude == 1 else f"{_decimal(magnitude, magnitude_direction)} {variable}"
        if not rendered:
            rendered.append(atom if coefficient > 0 else f"- {atom}")
        else:
            rendered.append(("+ " if coefficient > 0 else "- ") + atom)
    return " ".join(rendered) or "0"


def _inequality(name: str, terms: Iterable[Tuple[Fraction, str]], relation: str, rhs: Fraction) -> str:
    """Render one inequality with coefficients rounded toward a relaxation.

    All variables in this model lie in ``[0, 1]``.  Therefore decreasing every
    coefficient and increasing the RHS relaxes a ``<=`` row; the opposite
    directions relax a ``>=`` row.
    """

    if relation == "<=":
        return f" {name}: {_linear(terms, 'down')} <= {_decimal(rhs, 'up')}"
    if relation == ">=":
        return f" {name}: {_linear(terms, 'up')} >= {_decimal(rhs, 'down')}"
    raise ValueError(f"unsupported inequality relation {relation!r}")


def canonical_coordinate_bounds(n: int) -> dict[str, Interval]:
    """Return the published five-boundary symmetry-breaking normal form.

    The first five labelled points are respectively left, bottom, right, top,
    and left boundary points.  All later points remain free, so configurations
    with more than five boundary points are still represented.
    """

    if n < 5:
        raise ValueError("the five-boundary normal form requires n >= 5")
    bounds = {
        **{_variable("x", index): (Fraction(0), Fraction(1)) for index in range(n)},
        **{_variable("y", index): (Fraction(0), Fraction(1)) for index in range(n)},
    }
    bounds[_variable("x", 0)] = (Fraction(0), Fraction(0))
    bounds[_variable("y", 1)] = (Fraction(0), Fraction(0))
    bounds[_variable("x", 2)] = (Fraction(1), Fraction(1))
    bounds[_variable("y", 3)] = (Fraction(1), Fraction(1))
    bounds[_variable("x", 4)] = (Fraction(0), Fraction(0))
    return bounds


def root_spatial_box(n: int) -> SpatialBox:
    """Return the full closed normalized domain for a point count."""

    return SpatialBox(canonical_coordinate_bounds(n))


def split_spatial_box(box: SpatialBox, variable: str) -> Tuple[SpatialBox, SpatialBox]:
    """Bisect one nondegenerate coordinate interval into a closed cover."""

    if variable not in box.coordinate_bounds:
        raise KeyError(f"unknown coordinate {variable!r}")
    lower, upper = box.coordinate_bounds[variable]
    if lower >= upper:
        raise ValueError(f"cannot split fixed coordinate {variable!r}")
    midpoint = (lower + upper) / 2
    left = dict(box.coordinate_bounds)
    right = dict(box.coordinate_bounds)
    left[variable] = (lower, midpoint)
    right[variable] = (midpoint, upper)
    return SpatialBox(left, box.depth + 1), SpatialBox(right, box.depth + 1)


def _validated_bounds(n: int, spatial_box: SpatialBox | None) -> dict[str, Interval]:
    """Merge a closed spatial box into the canonical bounds without widening it."""

    canonical = canonical_coordinate_bounds(n)
    if spatial_box is None:
        return canonical
    if set(spatial_box.coordinate_bounds) != set(canonical):
        raise ValueError("spatial box must specify exactly the canonical coordinates")
    for variable, interval in spatial_box.coordinate_bounds.items():
        lower, upper = interval
        canonical_lower, canonical_upper = canonical[variable]
        if lower > upper or lower < canonical_lower or upper > canonical_upper:
            raise ValueError(f"invalid subbox interval for {variable!r}")
        canonical[variable] = interval
    return canonical


def canonical_orderings(n: int) -> Tuple[Tuple[str, str], ...]:
    """Pairs ``(left, right)`` encoding the published ordering inequalities."""

    if n < 5:
        raise ValueError("the five-boundary normal form requires n >= 5")
    orderings = [(_variable("x", 1), _variable("x", 3)), (_variable("y", 0), _variable("y", 4))]
    orderings.extend((_variable("x", index - 1), _variable("x", index)) for index in range(5, n))
    return tuple(orderings)


def ordered_product_links(n: int) -> Tuple[Tuple[str, int, int, int], ...]:
    """Return RLT links implied by every canonical coordinate ordering.

    If ``x_left <= x_right`` and ``0 <= y_other <= 1``, then
    ``0 <= w_right,other - w_left,other <= x_right - x_left``.  The analogous
    statement holds for an ordered pair of ``y`` coordinates.  Diagonal
    products are deliberately absent from this formulation, so links needing
    one are skipped.
    """

    links: list[Tuple[str, int, int, int]] = []
    for left, right in canonical_orderings(n):
        axis, left_raw = left.split("_")
        right_axis, right_raw = right.split("_")
        if axis != right_axis:
            raise AssertionError("canonical ordering mixed coordinate axes")
        left_index, right_index = int(left_raw), int(right_raw)
        for other in range(n):
            if other not in (left_index, right_index):
                links.append((axis, left_index, right_index, other))
    return tuple(links)


def ordered_axis_pairs(n: int, axis: str) -> Tuple[Tuple[int, int], ...]:
    """Extract canonical ordering pairs for one coordinate axis."""

    if axis not in ("x", "y"):
        raise ValueError("axis must be 'x' or 'y'")
    pairs = []
    for left, right in canonical_orderings(n):
        left_axis, left_raw = left.split("_")
        right_axis, right_raw = right.split("_")
        if left_axis != right_axis:
            raise AssertionError("canonical ordering mixed coordinate axes")
        if left_axis == axis:
            pairs.append((int(left_raw), int(right_raw)))
    return tuple(pairs)


def _product_linearization(left: int, right: int, bounds: Mapping[str, Interval]) -> Tuple[Tuple[Fraction, str], ...] | None:
    """Represent ``x_left * y_right`` using an LP product or a fixed pin.

    The primary formulation omits diagonal products.  A few diagonal terms in
    rectangle-RLT rows are nevertheless linear because the normal form pins
    one factor to zero or one.  Return ``None`` only when an omitted diagonal
    remains genuinely bilinear.
    """

    if left != right:
        return ((Fraction(1), _product(left, right)),)
    x_lower, x_upper = bounds[_variable("x", left)]
    if x_lower == x_upper:
        if x_lower == 0:
            return ()
        return ((x_lower, _variable("y", right)),)
    y_lower, y_upper = bounds[_variable("y", right)]
    if y_lower == y_upper:
        if y_lower == 0:
            return ()
        return ((y_lower, _variable("x", left)),)
    return None


def rectangle_rlt_links(n: int, bounds: Mapping[str, Interval]) -> Tuple[Tuple[int, int, int, int], ...]:
    """Return cross-order RLT rectangles representable in this LP.

    If ``x_i <= x_j`` and ``y_k <= y_l``, then

    ``0 <= (x_j-x_i)(y_l-y_k) <= min(x_j-x_i, y_l-y_k)``.

    Expanding the product yields three linear inequalities in the existing
    ``w_ij = x_i*y_j`` variables.  Fixed-coordinate diagonal terms are
    substituted exactly; a genuinely bilinear omitted diagonal is skipped.
    """

    links = []
    for x_left, x_right in ordered_axis_pairs(n, "x"):
        for y_left, y_right in ordered_axis_pairs(n, "y"):
            products = (
                (x_left, y_left),
                (x_right, y_right),
                (x_left, y_right),
                (x_right, y_left),
            )
            if all(_product_linearization(left, right, bounds) is not None for left, right in products):
                links.append((x_left, x_right, y_left, y_right))
    return tuple(links)


def target_x_spacing_pairs(n: int) -> Tuple[Tuple[int, int], ...]:
    """Triples whose known x-order forces a span of at least ``2 * z``.

    Points 0 and 4 both lie on ``x=0``.  Hence point 5 must be at least
    ``2*z`` to their right.  Every three consecutive ordered points among
    points 5 onward obeys the same span bound because a triangle in an
    x-interval of width ``d`` has area at most ``d/2``.
    """

    if n < 5:
        raise ValueError("the five-boundary normal form requires n >= 5")
    pairs: list[Tuple[int, int]] = []
    if n >= 6:
        pairs.append((4, 5))
    pairs.extend((index, index + 2) for index in range(5, n - 2))
    return tuple(pairs)


def target_left_strip_exclusion_indices(n: int) -> Tuple[int, ...]:
    """Return labels excluded from the full first x-strip by points 0 and 4.

    At a positive target with a valid capacity-two strip grid, the two pinned
    left-boundary points 0 and 4 already fill the first vertical strip.  Every
    other point must therefore have ``x >= 1/m`` (with equality allowed because
    adjacent closed strips meet at their boundary).  This is a valid continuous
    consequence of the strip theorem, independent of any chosen binary
    assignment in the LP.
    """

    if n < 5:
        raise ValueError("the five-boundary normal form requires n >= 5")
    return tuple(index for index in range(n) if index not in (0, 4))


def target_tightened_coordinate_bounds(
    n: int,
    coordinate_bounds: Mapping[str, Interval],
    lower_target: Fraction,
) -> dict[str, Interval]:
    """Propagate target-valid order, strip, span, and chord products into bounds.

    The returned box is an exact subset of ``coordinate_bounds`` containing
    every configuration whose minimum triangle area is strictly greater than
    ``lower_target``.  Applying these elementary difference constraints before
    emitting McCormick rows makes their envelopes tighter without excluding a
    strict geometric witness.  An empty propagated interval proves the
    supplied spatial box cannot strictly exceed the target; boundary
    configurations with minimum area exactly equal to the target may be
    removed.  In particular, every non-left point
    forms a triangle with the fixed left chord, so the exact product
    ``x_i * (y_4-y_0)`` must exceed ``2 * lower_target``.  The propagation only
    uses a product's current interval upper endpoints to raise lower bounds;
    it can retain infeasible values but cannot exclude a strict target violator.
    """

    if lower_target <= 0:
        raise ValueError("target bound propagation requires a positive target")
    bounds = dict(coordinate_bounds)
    expected = set(canonical_coordinate_bounds(n))
    if set(bounds) != expected:
        raise ValueError("target bound propagation requires every canonical coordinate")
    strip_count = strip_count_for_target(lower_target)
    for index in target_left_strip_exclusion_indices(n):
        variable = _variable("x", index)
        lower, upper = bounds[variable]
        # Every triangle (0, 4, index) has area
        # x_index * (y_4-y_0) / 2.  Since the chord height is at most one,
        # an area at least the target forces x_index >= 2*target.  This
        # dominates the weaker first-strip exclusion but both are retained as
        # independently auditable model rows below.
        bounds[variable] = (max(lower, Fraction(1, strip_count), 2 * lower_target), upper)

    # `left <= right` and `right - left >= 2*target` are both difference
    # constraints.  Iterate to their least fixed point over rational bounds.
    orderings = canonical_orderings(n)
    spans = (
        ((_variable("y", 0), _variable("y", 4)),)
        + tuple((_variable("x", left), _variable("x", right)) for left, right in target_x_spacing_pairs(n))
    )
    while True:
        changed = False
        for left, right in orderings:
            left_lower, left_upper = bounds[left]
            right_lower, right_upper = bounds[right]
            tightened_left = (left_lower, min(left_upper, right_upper))
            tightened_right = (max(right_lower, left_lower), right_upper)
            if tightened_left != bounds[left]:
                bounds[left] = tightened_left
                changed = True
            if tightened_right != bounds[right]:
                bounds[right] = tightened_right
                changed = True
        for left, right in spans:
            left_lower, left_upper = bounds[left]
            right_lower, right_upper = bounds[right]
            tightened_left = (left_lower, min(left_upper, right_upper - 2 * lower_target))
            tightened_right = (max(right_lower, left_lower + 2 * lower_target), right_upper)
            if tightened_left != bounds[left]:
                bounds[left] = tightened_left
                changed = True
            if tightened_right != bounds[right]:
                bounds[right] = tightened_right
                changed = True

        # Every triangle (0, 4, i) has ordinary area
        # x_i * (y_4-y_0) / 2, with both factors nonnegative in the canonical
        # form.  If the upper product is at most 2*target, no point in this
        # spatial box can be a strict target violator.  Otherwise using that
        # upper endpoint gives a deliberately weak but exact lower bound for
        # the other factor.  This is the interval counterpart of the
        # factorised left-chord McCormick rows below.
        y0_name, y4_name = _variable("y", 0), _variable("y", 4)
        chord_upper = bounds[y4_name][1] - bounds[y0_name][0]
        threshold = 2 * lower_target
        if chord_upper <= 0:
            raise ValueError("spatial box cannot meet the target left-chord product")
        required_chord_lower = Fraction(0)
        for index in target_left_strip_exclusion_indices(n):
            x_name = _variable("x", index)
            x_lower, x_upper = bounds[x_name]
            if x_upper * chord_upper <= threshold:
                raise ValueError(f"spatial box cannot meet the target left-chord product at {x_name!r}")
            tightened_x = (max(x_lower, threshold / chord_upper), x_upper)
            if tightened_x != bounds[x_name]:
                bounds[x_name] = tightened_x
                changed = True
            required_chord_lower = max(required_chord_lower, threshold / x_upper)

        y0_lower, y0_upper = bounds[y0_name]
        y4_lower, y4_upper = bounds[y4_name]
        tightened_y4 = (max(y4_lower, y0_lower + required_chord_lower), y4_upper)
        tightened_y0 = (y0_lower, min(y0_upper, y4_upper - required_chord_lower))
        if tightened_y4 != bounds[y4_name]:
            bounds[y4_name] = tightened_y4
            changed = True
        if tightened_y0 != bounds[y0_name]:
            bounds[y0_name] = tightened_y0
            changed = True
        for variable, (lower, upper) in bounds.items():
            if lower > upper:
                raise ValueError(f"spatial box cannot meet the target after propagation at {variable!r}")
        if not changed:
            return bounds


_PUBLISHED_NINE_POINT_UPPER = Fraction(549, 10_000)


def published_nine_point_upper_bound() -> Fraction:
    """Return a rational upper bound implied by the certified exact n=9 value.

    Sudermann--Merx (2026, Section 5.6) certifies

    ``Delta_9 = -11/64 + 9*sqrt(65)/320``.

    The returned ``549/10000`` is deliberately a little larger, so the only
    arithmetic this module needs is the exact inequality
    ``sqrt(65) < (320*q + 55)/9``.  Squaring is valid because the right side
    is positive.  This is used only from n=10 onward, avoiding circular use of
    a published n=9 result when calibrating an n=9 solve.
    """

    bound = _PUBLISHED_NINE_POINT_UPPER
    threshold = (320 * bound + 55) / 9
    if threshold <= 0 or threshold * threshold <= 65:
        raise AssertionError("published n=9 rational upper-bound derivation failed")
    return bound


def area_upper_bound(n: int) -> Fraction:
    """Return a proved global upper bound for the n-point objective.

    The elementary triangulation argument gives ``1 / (n - 2)``.  For
    ``n >= 10``, deleting points and the certified n=9 optimum additionally
    give ``Delta_n <= Delta_9 < 549/10000``.  The latter is materially tighter
    for the n=12 relaxation and reduces the valid big-M constant.
    """

    if n < 3:
        raise ValueError("at least three points are required")
    elementary = Fraction(1, n - 2)
    if n >= 10:
        return min(elementary, published_nine_point_upper_bound())
    return elementary


def strip_count_for_target(lower_target: Fraction) -> int:
    """Choose ``m`` with strip height ``1/m < 2 * lower_target``.

    Any three points in a horizontal or vertical strip of that height span a
    triangle of area at most ``1/(2*m) < lower_target``.  Thus a configuration
    with minimum area at least ``lower_target`` has capacity at most two in
    every such strip.
    """

    if lower_target <= 0:
        raise ValueError("strip target must be positive")
    reciprocal = Fraction(1, 1) / (2 * lower_target)
    count = reciprocal.numerator // reciprocal.denominator + 1
    if Fraction(1, 2 * count) >= lower_target:
        raise AssertionError("strip count must be strictly below target area")
    return count


def _strip_variable(axis: str, point: int, strip: int, grid: int | None = None) -> str:
    suffix = "" if grid is None else f"_{grid}"
    return f"h_{axis}{suffix}_{point}_{strip}"


def mccormick_inequalities(
    x_bounds: Interval,
    y_bounds: Interval,
) -> Tuple[Tuple[Fraction, Fraction, Fraction, Fraction, str], ...]:
    """Return the four ``a*w + b*x + c*y relation rhs`` inequalities.

    The tuple order is ``(a, b, c, rhs, relation)``.  The inequalities are the
    exact convex hull of ``w = x*y`` over a rectangular coordinate box.
    """

    lower_x, upper_x = x_bounds
    lower_y, upper_y = y_bounds
    return (
        (Fraction(1), -lower_y, -lower_x, -lower_x * lower_y, ">="),
        (Fraction(1), -upper_y, -upper_x, -upper_x * upper_y, ">="),
        (Fraction(1), -lower_y, -upper_x, -upper_x * lower_y, "<="),
        (Fraction(1), -upper_y, -lower_x, -lower_x * upper_y, "<="),
    )


def mccormick_contains(x: Fraction, y: Fraction, w: Fraction, x_bounds: Interval, y_bounds: Interval) -> bool:
    """Check the four exact McCormick inequalities for one point."""

    if not (x_bounds[0] <= x <= x_bounds[1] and y_bounds[0] <= y <= y_bounds[1]):
        return False
    for coefficient_w, coefficient_x, coefficient_y, rhs, relation in mccormick_inequalities(x_bounds, y_bounds):
        value = coefficient_w * w + coefficient_x * x + coefficient_y * y
        if relation == ">=" and value < rhs:
            return False
        if relation == "<=" and value > rhs:
            return False
    return True


def _mccormick_contains_qx(x: Qx, y: Qx, w: Qx, x_bounds: Interval, y_bounds: Interval) -> bool:
    """Exact cubic-field counterpart of ``mccormick_contains`` for the record."""

    for coefficient_w, coefficient_x, coefficient_y, rhs, relation in mccormick_inequalities(x_bounds, y_bounds):
        value = coefficient_w * w + coefficient_x * x + coefficient_y * y
        comparison = sign(value - Qx.rational(rhs))
        if relation == ">=" and comparison < 0:
            return False
        if relation == "<=" and comparison > 0:
            return False
    return True


def orientation_big_m_contains(area: Fraction, z: Fraction, orientation: int, upper: Fraction) -> bool:
    """Check the two linear big-M sign constraints at an exact point."""

    if orientation not in (-1, 1):
        raise ValueError("orientation must be -1 or 1")
    if not (Fraction(0) <= z <= upper):
        return False
    binary = Fraction(1) if orientation > 0 else Fraction(0)
    big_m = Fraction(1, 2) + upper
    return z - area <= big_m * (1 - binary) and z + area <= big_m * binary


def _signed_area_terms(triangle: Triangle, multiplier: Fraction) -> Tuple[Tuple[Fraction, str], ...]:
    """Terms for ``multiplier * A_signed`` in product variables."""

    i, j, k = triangle
    half = multiplier * Fraction(1, 2)
    return (
        (half, _product(i, j)),
        (-half, _product(i, k)),
        (-half, _product(j, i)),
        (half, _product(j, k)),
        (half, _product(k, i)),
        (-half, _product(k, j)),
    )


def fixed_orientation(triangle: Triangle) -> int | None:
    """Return a canonical boundary orientation forced by the normal form."""

    if triangle[2] <= 4:
        return 1
    if triangle[0] == 0 and triangle[1] == 4:
        return -1
    return None


def _add_strip_constraints(
    lines: list[str],
    binary_variables: list[str],
    n: int,
    axis: str,
    count: int,
    *,
    grid: int | None = None,
) -> None:
    """Add a closed equal-strip assignment with capacity two per strip."""

    name_axis = axis if grid is None else f"{axis}_{grid}"
    for point in range(n):
        memberships = tuple(_strip_variable(axis, point, strip, grid) for strip in range(count))
        binary_variables.extend(memberships)
        lines.append(f" strip_assignment_{name_axis}_{point}: {_linear((Fraction(1), variable) for variable in memberships)} = 1")
        coordinate = _variable(axis, point)
        for strip, membership in enumerate(memberships):
            lower = Fraction(strip, count)
            upper = Fraction(strip + 1, count)
            lines.append(
                _inequality(
                    f"strip_lower_{name_axis}_{point}_{strip}",
                    ((Fraction(1), coordinate), (Fraction(-1), membership)),
                    ">=",
                    lower - 1,
                )
            )
            lines.append(
                _inequality(
                    f"strip_upper_{name_axis}_{point}_{strip}",
                    ((Fraction(1), coordinate), (Fraction(1), membership)),
                    "<=",
                    upper + 1,
                )
            )
    for strip in range(count):
        memberships = tuple(_strip_variable(axis, point, strip, grid) for point in range(n))
        lines.append(
            _inequality(
                f"strip_capacity_{name_axis}_{strip}",
                ((Fraction(1), variable) for variable in memberships),
                "<=",
                Fraction(2),
            )
        )


def _add_rectangle_rlt_constraints(
    lines: list[str],
    n: int,
    bounds: Mapping[str, Interval],
) -> None:
    """Add cross-order RLT cuts for every representable canonical rectangle."""

    for x_left, x_right, y_left, y_right in rectangle_rlt_links(n, bounds):
        products = (
            (Fraction(1), x_left, y_left),
            (Fraction(1), x_right, y_right),
            (Fraction(-1), x_left, y_right),
            (Fraction(-1), x_right, y_left),
        )
        cross_terms: list[Tuple[Fraction, str]] = []
        for coefficient, left, right in products:
            representation = _product_linearization(left, right, bounds)
            if representation is None:
                raise AssertionError("rectangle link was not LP-representable")
            cross_terms.extend((coefficient * inner_coefficient, variable) for inner_coefficient, variable in representation)
        label = f"rectangle_rlt_x_{x_left}_{x_right}_y_{y_left}_{y_right}"
        lines.append(_inequality(f"{label}_lower", cross_terms, ">=", Fraction(0)))
        lines.append(
            _inequality(
                f"{label}_x_span",
                tuple(cross_terms)
                + ((Fraction(-1), _variable("x", x_right)), (Fraction(1), _variable("x", x_left))),
                "<=",
                Fraction(0),
            )
        )
        lines.append(
            _inequality(
                f"{label}_y_span",
                tuple(cross_terms)
                + ((Fraction(-1), _variable("y", y_right)), (Fraction(1), _variable("y", y_left))),
                "<=",
                Fraction(0),
            )
        )


def _add_bound_strengthened_ordered_product_constraints(
    lines: list[str],
    n: int,
    bounds: Mapping[str, Interval],
) -> None:
    """Tighten ordered-product RLT links using the other factor's bounds.

    For example, from ``y_left <= y_right`` and
    ``l <= x_other <= u`` we obtain

    ``l * (y_right-y_left) <= w_other,right-w_other,left <= u * (y_right-y_left)``.

    The existing RLT rows are the special case ``l=0, u=1``.  Target-bound
    propagation supplies nontrivial `l` or `u` values, so these rows preserve
    every geometric point while tightening the product relaxation.
    """

    for axis, left, right, other in ordered_product_links(n):
        if axis == "x":
            difference = ((Fraction(1), _product(right, other)), (Fraction(-1), _product(left, other)))
            span = ((Fraction(1), _variable("x", right)), (Fraction(-1), _variable("x", left)))
            factor_lower, factor_upper = bounds[_variable("y", other)]
        else:
            difference = ((Fraction(1), _product(other, right)), (Fraction(-1), _product(other, left)))
            span = ((Fraction(1), _variable("y", right)), (Fraction(-1), _variable("y", left)))
            factor_lower, factor_upper = bounds[_variable("x", other)]
        label = f"rlt_bound_{axis}_{left}_{right}_{other}"
        if factor_lower > 0:
            lines.append(
                _inequality(
                    f"{label}_lower",
                    difference + tuple((-factor_lower * coefficient, variable) for coefficient, variable in span),
                    ">=",
                    Fraction(0),
                )
            )
        if factor_upper < 1:
            lines.append(
                _inequality(
                    f"{label}_upper",
                    difference + tuple((-factor_upper * coefficient, variable) for coefficient, variable in span),
                    "<=",
                    Fraction(0),
                )
            )


def left_chord_span_bounds(bounds: Mapping[str, Interval], lower_target: Fraction) -> Interval:
    """Return valid bounds for the vertical chord from point 0 to point 4.

    In the canonical boundary form, points 0 and 4 lie on ``x=0`` and the
    ordering gives ``y_0 <= y_4``.  A configuration above ``lower_target``
    also has ``y_4-y_0 >= 2*lower_target``: otherwise the triangle formed
    with point 2, whose x-coordinate is one, would be too small.  This
    interval is deliberately computed from the current spatial box, so the
    same factorisation remains valid after spatial branching.
    """

    if lower_target <= 0:
        raise ValueError("left-chord product cuts require a positive target")
    y0_lower, y0_upper = bounds[_variable("y", 0)]
    y4_lower, y4_upper = bounds[_variable("y", 4)]
    lower = max(Fraction(2) * lower_target, y4_lower - y0_upper)
    upper = y4_upper - y0_lower
    if lower > upper:
        raise ValueError("spatial box cannot meet the target left-chord span")
    return lower, upper


def _add_left_chord_product_constraints(
    lines: list[str],
    n: int,
    bounds: Mapping[str, Interval],
    lower_target: Fraction,
) -> None:
    """Add a second, coupled hull for triangles based on the fixed left chord.

    Every point ``i`` other than the two left-edge points satisfies

    ``x_i * (y_4-y_0) = w_i4-w_i0``.

    The usual directed-product envelopes relax the two terms on the right
    independently.  Applying McCormick directly to the factorised left-hand
    product gives four additional valid linear rows for their *difference*.
    It is especially useful here because each corresponding fixed-sign
    triangle already requires that difference to be at least ``2*z``.
    """

    chord_bounds = left_chord_span_bounds(bounds, lower_target)
    for index in target_left_strip_exclusion_indices(n):
        x_name = _variable("x", index)
        difference = ((Fraction(1), _product(index, 4)), (Fraction(-1), _product(index, 0)))
        for row, (coefficient_product, coefficient_x, coefficient_chord, rhs, relation) in enumerate(
            mccormick_inequalities(bounds[x_name], chord_bounds)
        ):
            terms = (
                tuple((coefficient_product * coefficient, variable) for coefficient, variable in difference)
                + ((coefficient_x, x_name),)
                + (
                    (coefficient_chord, _variable("y", 4)),
                    (-coefficient_chord, _variable("y", 0)),
                )
            )
            lines.append(_inequality(f"left_chord_mccormick_{index}_{row}", terms, relation, rhs))


def _target_difference_edges(n: int, axis: str, lower_target: Fraction) -> Tuple[Tuple[int, int, Fraction], ...]:
    """Return the directed target-valid coordinate-difference inequalities."""

    edges = []
    for left, right in canonical_orderings(n):
        edge_axis, left_raw = left.split("_")
        _, right_raw = right.split("_")
        if edge_axis == axis:
            edges.append((int(left_raw), int(right_raw), Fraction(0)))
    if axis == "x":
        edges.extend((left, right, 2 * lower_target) for left, right in target_x_spacing_pairs(n))
    elif axis == "y":
        edges.append((0, 4, 2 * lower_target))
    else:
        raise ValueError("target difference axis must be 'x' or 'y'")
    return tuple(edges)


def target_ordered_span_lower_bound(
    n: int,
    axis: str,
    left: int,
    right: int,
    lower_target: Fraction,
) -> Fraction:
    """Compute the strongest path-implied lower bound on ``right-left``.

    The packing inequalities form a small directed difference-constraints
    graph.  Its longest path is a valid lower bound for every ordered pair,
    including nonadjacent interior labels; for example, it recovers
    ``x_11-x_4 >= 8*target`` at ``n=12``.
    """

    if not (0 <= left < n and 0 <= right < n):
        raise ValueError("ordered span indices must lie in range")
    if lower_target <= 0:
        raise ValueError("target ordered span requires a positive target")
    negative_infinity: Fraction | None = None
    distance: list[Fraction | None] = [negative_infinity] * n
    distance[left] = Fraction(0)
    for _ in range(n - 1):
        changed = False
        for source, destination, minimum_span in _target_difference_edges(n, axis, lower_target):
            if distance[source] is None:
                continue
            candidate = distance[source] + minimum_span
            if distance[destination] is None or candidate > distance[destination]:
                distance[destination] = candidate
                changed = True
        if not changed:
            break
    return max(Fraction(0), distance[right] if distance[right] is not None else Fraction(0))


def ordered_difference_span_bounds(
    n: int,
    axis: str,
    left: int,
    right: int,
    bounds: Mapping[str, Interval],
    lower_target: Fraction,
) -> Interval:
    """Bound one nonnegative canonical coordinate span inside a target box.

    The canonical ordering supplies the zero lower bound.  A handful of
    target-valid packing spans are stronger; retaining them here lets the
    factorised McCormick hull use the same information as the primary model
    rows rather than merely the independent coordinate intervals.
    """

    if axis not in ("x", "y"):
        raise ValueError("ordered span axis must be 'x' or 'y'")
    if lower_target <= 0:
        raise ValueError("ordered-difference product cuts require a positive target")
    left_bounds = bounds[_variable(axis, left)]
    right_bounds = bounds[_variable(axis, right)]
    lower = max(Fraction(0), right_bounds[0] - left_bounds[1])
    upper = right_bounds[1] - left_bounds[0]
    lower = max(lower, target_ordered_span_lower_bound(n, axis, left, right, lower_target))
    if lower > upper:
        raise ValueError(f"spatial box cannot meet the target ordered span ({axis}, {left}, {right})")
    return lower, upper


def _add_ordered_difference_mccormick_constraints(
    lines: list[str],
    n: int,
    bounds: Mapping[str, Interval],
    lower_target: Fraction,
) -> None:
    """Couple every ordered-product RLT difference through its true product.

    For an x-order ``x_left <= x_right`` the existing relaxation contains
    ``w_right,other-w_left,other``.  At a geometric point this is exactly

    ``(x_right-x_left) * y_other``.

    Applying the four McCormick rows to that factorisation supplies the
    complement of the usual RLT lower/upper pair (notably
    ``difference >= span + factor - 1`` in the unit-box case).  The same
    construction applies to y-orderings.  The left-edge chord is emitted
    separately under a more descriptive name, so it is skipped here.
    """

    for axis, left, right, other in ordered_product_links(n):
        if axis == "y" and (left, right) == (0, 4):
            continue
        span_bounds = ordered_difference_span_bounds(n, axis, left, right, bounds, lower_target)
        if axis == "x":
            difference = ((Fraction(1), _product(right, other)), (Fraction(-1), _product(left, other)))
            span = ((Fraction(1), _variable("x", right)), (Fraction(-1), _variable("x", left)))
            factor = _variable("y", other)
        else:
            difference = ((Fraction(1), _product(other, right)), (Fraction(-1), _product(other, left)))
            span = ((Fraction(1), _variable("y", right)), (Fraction(-1), _variable("y", left)))
            factor = _variable("x", other)
        label = f"rlt_mccormick_{axis}_{left}_{right}_{other}"
        for row, (coefficient_product, coefficient_span, coefficient_factor, rhs, relation) in enumerate(
            mccormick_inequalities(span_bounds, bounds[factor])
        ):
            terms = (
                tuple((coefficient_product * coefficient, variable) for coefficient, variable in difference)
                + tuple((coefficient_span * coefficient, variable) for coefficient, variable in span)
                + ((coefficient_factor, factor),)
            )
            lines.append(_inequality(f"{label}_{row}", terms, relation, rhs))


def transitive_x_ordered_pairs(n: int) -> Tuple[Tuple[int, int], ...]:
    """Return the nonadjacent pairs in the ordered interior x-chain."""

    if n < 5:
        raise ValueError("the five-boundary normal form requires n >= 5")
    return tuple((left, right) for left in range(4, n) for right in range(left + 2, n))


def transitive_x_ordered_product_links(n: int) -> Tuple[Tuple[int, int, int], ...]:
    """Return nonadjacent product links from the ordered interior x-chain.

    Adjacent links alone imply the basic monotonicity rows after summation,
    but they do not imply the far-pair McCormick complement.  Each returned
    triple represents ``(x_right-x_left) * y_other`` for a nonadjacent pair
    in the chain ``x_4 <= x_5 <= ... <= x_(n-1)``.
    """

    return tuple(
        (left, right, other)
        for left, right in transitive_x_ordered_pairs(n)
        for other in range(n)
        if other not in (left, right)
    )


def _add_transitive_x_difference_mccormick_constraints(
    lines: list[str],
    n: int,
    bounds: Mapping[str, Interval],
    lower_target: Fraction,
) -> None:
    """Add factorised McCormick rows for nonadjacent interior x-order pairs."""

    for left, right, other in transitive_x_ordered_product_links(n):
        span_bounds = ordered_difference_span_bounds(n, "x", left, right, bounds, lower_target)
        difference = ((Fraction(1), _product(right, other)), (Fraction(-1), _product(left, other)))
        span = ((Fraction(1), _variable("x", right)), (Fraction(-1), _variable("x", left)))
        factor = _variable("y", other)
        label = f"rlt_mccormick_transitive_x_{left}_{right}_{other}"
        for row, (coefficient_product, coefficient_span, coefficient_factor, rhs, relation) in enumerate(
            mccormick_inequalities(span_bounds, bounds[factor])
        ):
            terms = (
                tuple((coefficient_product * coefficient, variable) for coefficient, variable in difference)
                + tuple((coefficient_span * coefficient, variable) for coefficient, variable in span)
                + ((coefficient_factor, factor),)
            )
            lines.append(_inequality(f"{label}_{row}", terms, relation, rhs))


def _add_transitive_left_chord_rectangle_constraints(
    lines: list[str],
    n: int,
    bounds: Mapping[str, Interval],
    lower_target: Fraction,
) -> None:
    """Apply a joint product hull to every transitive x-span and left chord.

    For a nonadjacent ordered pair, the rectangle product

    ``(x_right-x_left) * (y_4-y_0)``

    expands into four existing directed products.  The adjacent version is
    covered by the basic rectangle RLT family; this adds the stronger four-row
    McCormick hull for every transitive pair, with target-derived span bounds
    on both factors.
    """

    chord_bounds = left_chord_span_bounds(bounds, lower_target)
    chord = ((Fraction(1), _variable("y", 4)), (Fraction(-1), _variable("y", 0)))
    for left, right in transitive_x_ordered_pairs(n):
        products = (
            (Fraction(1), left, 0),
            (Fraction(1), right, 4),
            (Fraction(-1), left, 4),
            (Fraction(-1), right, 0),
        )
        difference: list[Tuple[Fraction, str]] = []
        for coefficient, product_left, product_right in products:
            representation = _product_linearization(product_left, product_right, bounds)
            if representation is None:
                raise AssertionError("transitive left-chord rectangle was not LP-representable")
            difference.extend((coefficient * inner_coefficient, variable) for inner_coefficient, variable in representation)
        span_bounds = ordered_difference_span_bounds(n, "x", left, right, bounds, lower_target)
        span = ((Fraction(1), _variable("x", right)), (Fraction(-1), _variable("x", left)))
        label = f"rectangle_mccormick_transitive_x_{left}_{right}"
        for row, (coefficient_product, coefficient_span, coefficient_chord, rhs, relation) in enumerate(
            mccormick_inequalities(span_bounds, chord_bounds)
        ):
            terms = (
                tuple((coefficient_product * coefficient, variable) for coefficient, variable in difference)
                + tuple((coefficient_span * coefficient, variable) for coefficient, variable in span)
                + tuple((coefficient_chord * coefficient, variable) for coefficient, variable in chord)
            )
            lines.append(_inequality(f"{label}_{row}", terms, relation, rhs))


_PIECEWISE_DEACTIVATION_M = Fraction(2)


def _intersection(left: Interval, right: Interval) -> Interval | None:
    lower, upper = max(left[0], right[0]), min(left[1], right[1])
    return None if lower > upper else (lower, upper)


def _add_piecewise_mccormick_rows(
    lines: list[str],
    n: int,
    bounds: Mapping[str, Interval],
    strip_count: int,
    cell_count: int,
    product_pairs: Sequence[Tuple[int, int]] | None = None,
) -> None:
    """Condition McCormick envelopes on the existing strip-assignment binaries.

    Every coordinate already chooses one closed fine strip.  Grouping those
    choices into equal coarse cells activates a tighter McCormick hull for the
    selected cell.  This is a disjunctive outer relaxation of the true product
    graph; inactive rows are made redundant with a valid ``M=2``.
    """

    pairs = (
        tuple((left, right) for left in range(n) for right in range(n) if left != right)
        if product_pairs is None
        else product_pairs
    )
    for left, right in pairs:
        product = _product(left, right)
        x_name, y_name = _variable("x", left), _variable("y", right)
        for axis, coordinate_name, membership_point in (
            ("x", x_name, left),
            ("y", y_name, right),
        ):
            strips_per_cell = strip_count // cell_count
            for cell in range(cell_count):
                first_strip = cell * strips_per_cell
                cell_bounds = (Fraction(cell, cell_count), Fraction(cell + 1, cell_count))
                coordinate_bounds = _intersection(bounds[coordinate_name], cell_bounds)
                if coordinate_bounds is None:
                    continue
                x_bounds, y_bounds = (
                    (coordinate_bounds, bounds[y_name]) if axis == "x" else (bounds[x_name], coordinate_bounds)
                )
                memberships = tuple(
                    _strip_variable(axis, membership_point, strip)
                    for strip in range(first_strip, first_strip + strips_per_cell)
                )
                for row, (coefficient_w, coefficient_x, coefficient_y, rhs, relation) in enumerate(
                    mccormick_inequalities(x_bounds, y_bounds)
                ):
                    terms: Tuple[Tuple[Fraction, str], ...] = (
                        (coefficient_w, product),
                        (coefficient_x, x_name),
                        (coefficient_y, y_name),
                    )
                    label = f"piecewise_{axis}_{left}_{right}_{cell}_{row}"
                    if relation == ">=":
                        lines.append(
                            _inequality(
                                label,
                                terms + tuple((-_PIECEWISE_DEACTIVATION_M, membership) for membership in memberships),
                                ">=",
                                rhs - _PIECEWISE_DEACTIVATION_M,
                            )
                        )
                    else:
                        lines.append(
                            _inequality(
                                label,
                                terms + tuple((_PIECEWISE_DEACTIVATION_M, membership) for membership in memberships),
                                "<=",
                                rhs + _PIECEWISE_DEACTIVATION_M,
                            )
                        )


def _joint_product_cell_variable(left: int, right: int, x_cell: int, y_cell: int) -> str:
    """Return the continuous AND variable for one directed product cell."""

    return f"g_{left}_{right}_{x_cell}_{y_cell}"


def _cell_memberships(axis: str, point: int, cell: int, strip_count: int, cell_count: int) -> Tuple[str, ...]:
    """Return the primary-strip memberships belonging to one coarse cell."""

    strips_per_cell = strip_count // cell_count
    first_strip = cell * strips_per_cell
    return tuple(_strip_variable(axis, point, strip) for strip in range(first_strip, first_strip + strips_per_cell))


def _add_joint_piecewise_mccormick_rows(
    lines: list[str],
    joint_variables: list[str],
    n: int,
    bounds: Mapping[str, Interval],
    strip_count: int,
    cell_count: int,
    product_pairs: Sequence[Tuple[int, int]] | None = None,
) -> None:
    """Add a joint x-cell/y-cell product disjunction for selected products.

    A primary strip assignment selects exactly one coarse x cell and one coarse
    y cell for each product.  For every directed product, continuous variables
    ``g`` are the exact ANDs of those two *binary* cell selections.  Thus one
    local McCormick envelope is active for the true cell pair.  The added rows
    remain an outer relaxation because every geometric product can set the
    corresponding ``g`` variable to that cell-pair indicator.

    Unlike the older axis-wise rows, this activates the envelope over the full
    local rectangle, not merely one of its two coordinate intervals.  The
    ``g`` variables need not be declared binary: the existing strip variables
    are binary and force each AND exactly at integral solutions.
    """

    pairs = (
        tuple((left, right) for left in range(n) for right in range(n) if left != right)
        if product_pairs is None
        else product_pairs
    )
    for left, right in pairs:
        product = _product(left, right)
        x_name, y_name = _variable("x", left), _variable("y", right)
        assignment: list[Tuple[Fraction, str]] = []
        for x_cell in range(cell_count):
            x_interval = _intersection(bounds[x_name], (Fraction(x_cell, cell_count), Fraction(x_cell + 1, cell_count)))
            if x_interval is None:
                continue
            x_memberships = _cell_memberships("x", left, x_cell, strip_count, cell_count)
            for y_cell in range(cell_count):
                y_interval = _intersection(
                    bounds[y_name], (Fraction(y_cell, cell_count), Fraction(y_cell + 1, cell_count))
                )
                if y_interval is None:
                    continue
                y_memberships = _cell_memberships("y", right, y_cell, strip_count, cell_count)
                joint = _joint_product_cell_variable(left, right, x_cell, y_cell)
                joint_variables.append(joint)
                assignment.append((Fraction(1), joint))
                label = f"joint_cell_{left}_{right}_{x_cell}_{y_cell}"
                lines.append(
                    _inequality(
                        f"{label}_x_upper",
                        ((Fraction(1), joint),) + tuple((Fraction(-1), membership) for membership in x_memberships),
                        "<=",
                        Fraction(0),
                    )
                )
                lines.append(
                    _inequality(
                        f"{label}_y_upper",
                        ((Fraction(1), joint),) + tuple((Fraction(-1), membership) for membership in y_memberships),
                        "<=",
                        Fraction(0),
                    )
                )
                lines.append(
                    _inequality(
                        f"{label}_lower",
                        ((Fraction(1), joint),)
                        + tuple((Fraction(-1), membership) for membership in x_memberships)
                        + tuple((Fraction(-1), membership) for membership in y_memberships),
                        ">=",
                        Fraction(-1),
                    )
                )
                for row, (coefficient_w, coefficient_x, coefficient_y, rhs, relation) in enumerate(
                    mccormick_inequalities(x_interval, y_interval)
                ):
                    terms: Tuple[Tuple[Fraction, str], ...] = (
                        (coefficient_w, product),
                        (coefficient_x, x_name),
                        (coefficient_y, y_name),
                    )
                    piece_label = f"joint_piecewise_{left}_{right}_{x_cell}_{y_cell}_{row}"
                    if relation == ">=":
                        lines.append(
                            _inequality(
                                piece_label,
                                terms + ((-_PIECEWISE_DEACTIVATION_M, joint),),
                                ">=",
                                rhs - _PIECEWISE_DEACTIVATION_M,
                            )
                        )
                    else:
                        lines.append(
                            _inequality(
                                piece_label,
                                terms + ((_PIECEWISE_DEACTIVATION_M, joint),),
                                "<=",
                                rhs + _PIECEWISE_DEACTIVATION_M,
                            )
                        )
        if not assignment:
            raise AssertionError(f"joint cell construction lost every cell for product ({left}, {right})")
        lines.append(f" joint_cell_assignment_{left}_{right}: {_linear(assignment)} = 1")


def signed_area(points: Sequence[Tuple[Fraction, Fraction]], triangle: Triangle) -> Fraction:
    """Return the ordinary signed area, including the factor ``1/2``."""

    i, j, k = triangle
    xi, yi = points[i]
    xj, yj = points[j]
    xk, yk = points[k]
    return ((xj - xi) * (yk - yi) - (yj - yi) * (xk - xi)) / 2


def n6_calibration_witness() -> Tuple[Tuple[Fraction, Fraction], ...]:
    """Canonical six-point witness of exact minimum area ``1/8``."""

    return (
        (Fraction(0), Fraction(0)),
        (Fraction(1, 2), Fraction(0)),
        (Fraction(1), Fraction(1, 2)),
        (Fraction(1, 2), Fraction(1)),
        (Fraction(0), Fraction(1, 2)),
        (Fraction(1), Fraction(1)),
    )


def verify_witness(points: Sequence[Tuple[Fraction, Fraction]]) -> WitnessVerification:
    """Lift a canonical witness and check every generated model invariant exactly."""

    n = len(points)
    bounds = canonical_coordinate_bounds(n)
    values = {
        **{_variable("x", index): point[0] for index, point in enumerate(points)},
        **{_variable("y", index): point[1] for index, point in enumerate(points)},
    }
    for variable, (lower, upper) in bounds.items():
        if not lower <= values[variable] <= upper:
            raise AssertionError(f"witness violates coordinate bound {variable}")
    for left, right in canonical_orderings(n):
        if values[left] > values[right]:
            raise AssertionError(f"witness violates ordering {left} <= {right}")
    for axis, left, right, other in ordered_product_links(n):
        if axis == "x":
            smaller = points[left][0] * points[other][1]
            larger = points[right][0] * points[other][1]
            coordinate_span = points[right][0] - points[left][0]
        else:
            smaller = points[other][0] * points[left][1]
            larger = points[other][0] * points[right][1]
            coordinate_span = points[right][1] - points[left][1]
        if smaller > larger or larger - smaller > coordinate_span:
            raise AssertionError(f"witness violates RLT product link ({axis}, {left}, {right}, {other})")
        if axis == "x":
            factor_lower, factor_upper = bounds[_variable("y", other)]
        else:
            factor_lower, factor_upper = bounds[_variable("x", other)]
        difference = larger - smaller
        if difference < factor_lower * coordinate_span or difference > factor_upper * coordinate_span:
            raise AssertionError(f"witness violates bound-strengthened RLT ({axis}, {left}, {right}, {other})")
    for x_left, x_right, y_left, y_right in rectangle_rlt_links(n, bounds):
        cross_difference = (
            points[x_left][0] * points[y_left][1]
            + points[x_right][0] * points[y_right][1]
            - points[x_left][0] * points[y_right][1]
            - points[x_right][0] * points[y_left][1]
        )
        x_span = points[x_right][0] - points[x_left][0]
        y_span = points[y_right][1] - points[y_left][1]
        if cross_difference < 0 or cross_difference > x_span or cross_difference > y_span:
            raise AssertionError(f"witness violates rectangle RLT ({x_left}, {x_right}, {y_left}, {y_right})")

    checked_products = 0
    for left in range(n):
        for right in range(n):
            if left == right:
                continue
            x_name = _variable("x", left)
            y_name = _variable("y", right)
            if not mccormick_contains(
                values[x_name], values[y_name], values[x_name] * values[y_name], bounds[x_name], bounds[y_name]
            ):
                raise AssertionError(f"McCormick envelope lost true product ({left}, {right})")
            checked_products += 1

    triangles: Tuple[Triangle, ...] = tuple(combinations(range(n), 3))
    areas = tuple(signed_area(points, triangle) for triangle in triangles)
    minimum = min(abs(area) for area in areas)
    if minimum == 0:
        raise ValueError("calibration witness must have positive minimum area")
    upper = area_upper_bound(n)
    if minimum > upper:
        raise AssertionError("elementary area upper bound is invalid for witness")
    for triangle, area in zip(triangles, areas):
        orientation = fixed_orientation(triangle)
        if orientation is None:
            orientation = 1 if area > 0 else -1
            if not orientation_big_m_contains(area, minimum, orientation, upper):
                raise AssertionError(f"big-M sign rows reject triangle {triangle}")
        elif orientation * area < minimum:
            raise AssertionError(f"fixed sign rows reject triangle {triangle}")
        if not Fraction(-1, 2) <= area <= Fraction(1, 2):
            raise AssertionError(f"signed-area bound fails for triangle {triangle}")
    return WitnessVerification(n, minimum, checked_products, len(triangles))


# A concrete relabelling of the exact Comellas--Yebra witness into the
# five-boundary normal form: left, bottom, right, top, left, then nondecreasing
# x-coordinate for the remaining points.  Equalities are deliberately allowed.
CANONICAL_INCUMBENT_LABELS: Tuple[int, ...] = (4, 0, 5, 2, 6, 9, 8, 11, 10, 1, 3, 7)


def canonical_incumbent_points() -> Tuple[Tuple[Qx, Qx], ...]:
    """Return the exact n=12 witness in five-boundary canonical label order."""

    points = incumbent_points()
    return tuple(points[index] for index in CANONICAL_INCUMBENT_LABELS)


def _coordinate(points: Sequence[Tuple[Qx, Qx]], variable: str) -> Qx:
    axis, raw_index = variable.split("_")
    return points[int(raw_index)][0 if axis == "x" else 1]


def _strip_candidates(value: Qx, count: int) -> Tuple[int, ...]:
    """Find every closed strip containing an exact algebraic coordinate."""

    candidates = []
    for strip in range(count):
        lower = Fraction(strip, count)
        upper = Fraction(strip + 1, count)
        if sign(value - Qx.rational(lower)) >= 0 and sign(Qx.rational(upper) - value) >= 0:
            candidates.append(strip)
    if not candidates:
        enclosure = algebraic_bounds(value, 192)
        raise AssertionError(f"coordinate escaped all strips: {enclosure}")
    return tuple(candidates)


def _capacity_two_assignment(candidates: Sequence[Tuple[int, ...]], count: int) -> Tuple[int, ...]:
    """Assign each point to a closed strip with at most two points per strip."""

    matched = [-1] * (2 * count)

    def augment(point: int, seen: set[int]) -> bool:
        for strip in candidates[point]:
            for copy in (2 * strip, 2 * strip + 1):
                if copy in seen:
                    continue
                seen.add(copy)
                if matched[copy] == -1 or augment(matched[copy], seen):
                    matched[copy] = point
                    return True
        return False

    if not all(augment(point, set()) for point in range(len(candidates))):
        raise AssertionError("no capacity-two strip assignment exists")
    assignment = [-1] * len(candidates)
    for copy, point in enumerate(matched):
        if point != -1:
            assignment[point] = copy // 2
    if any(strip == -1 for strip in assignment):
        raise AssertionError("matching lost a point")
    return tuple(assignment)


def _verify_exact_strip_rows(
    points: Sequence[Tuple[Qx, Qx]],
    count: int,
    x_strips: Sequence[int],
    y_strips: Sequence[int],
) -> None:
    """Evaluate every assignment, membership, and capacity row exactly."""

    for axis, assignments in (("x", x_strips), ("y", y_strips)):
        if len(assignments) != len(points):
            raise AssertionError("strip assignment has the wrong point count")
        for point_index, selected in enumerate(assignments):
            if not 0 <= selected < count:
                raise AssertionError("strip assignment index out of range")
            coordinate = points[point_index][0 if axis == "x" else 1]
            for strip in range(count):
                membership = Qx.rational(1 if strip == selected else 0)
                lower, upper = Fraction(strip, count), Fraction(strip + 1, count)
                if sign(coordinate - membership - Qx.rational(lower - 1)) < 0:
                    raise AssertionError(f"strip lower row rejects ({axis}, {point_index}, {strip})")
                if sign(Qx.rational(upper + 1) - coordinate - membership) < 0:
                    raise AssertionError(f"strip upper row rejects ({axis}, {point_index}, {strip})")
        for strip in range(count):
            if assignments.count(strip) > 2:
                raise AssertionError(f"strip capacity row rejects ({axis}, {strip})")


def verify_canonical_incumbent_lift(
    lower_target: Fraction = Fraction(1, 31),
    *,
    strip_count: int | None = None,
    additional_strip_counts: Sequence[int] = (),
) -> IncumbentLift:
    """Evaluate every non-piecewise root-model row at the exact incumbent."""

    if sign(incumbent_value() - Qx.rational(lower_target)) <= 0:
        raise AssertionError("strip target must lie strictly below the incumbent")
    points = canonical_incumbent_points()
    bounds = target_tightened_coordinate_bounds(12, canonical_coordinate_bounds(12), lower_target)
    for variable, (lower, upper) in bounds.items():
        coordinate = _coordinate(points, variable)
        if sign(coordinate - Qx.rational(lower)) < 0 or sign(Qx.rational(upper) - coordinate) < 0:
            raise AssertionError(f"canonical incumbent violates coordinate bound {variable}")
        if lower == upper and sign(coordinate - Qx.rational(lower)) != 0:
            raise AssertionError(f"canonical incumbent violates pinned coordinate {variable}")
    for left, right in canonical_orderings(12):
        if sign(_coordinate(points, right) - _coordinate(points, left)) < 0:
            raise AssertionError(f"canonical incumbent violates {left} <= {right}")
    for axis, left, right, other in ordered_product_links(12):
        if axis == "x":
            smaller = points[left][0] * points[other][1]
            larger = points[right][0] * points[other][1]
            coordinate_span = points[right][0] - points[left][0]
        else:
            smaller = points[other][0] * points[left][1]
            larger = points[other][0] * points[right][1]
            coordinate_span = points[right][1] - points[left][1]
        if sign(smaller - larger) > 0 or sign(larger - smaller - coordinate_span) > 0:
            raise AssertionError(f"canonical incumbent violates RLT product link ({axis}, {left}, {right}, {other})")
        if axis == "x":
            factor_lower, factor_upper = bounds[_variable("y", other)]
        else:
            factor_lower, factor_upper = bounds[_variable("x", other)]
        difference = larger - smaller
        if (
            sign(difference - Qx.rational(factor_lower) * coordinate_span) < 0
            or sign(difference - Qx.rational(factor_upper) * coordinate_span) > 0
        ):
            raise AssertionError(f"canonical incumbent violates bound-strengthened RLT ({axis}, {left}, {right}, {other})")
    for axis, left, right, other in ordered_product_links(12):
        if axis == "y" and (left, right) == (0, 4):
            continue
        span_bounds = ordered_difference_span_bounds(12, axis, left, right, bounds, lower_target)
        if axis == "x":
            span = points[right][0] - points[left][0]
            factor = points[other][1]
        else:
            span = points[right][1] - points[left][1]
            factor = points[other][0]
        factorized_product = span * factor
        for coefficient_product, coefficient_span, coefficient_factor, rhs, relation in mccormick_inequalities(
            span_bounds,
            bounds[_variable("y" if axis == "x" else "x", other)],
        ):
            value = coefficient_product * factorized_product + coefficient_span * span + coefficient_factor * factor
            comparison = sign(value - Qx.rational(rhs))
            if (relation == ">=" and comparison < 0) or (relation == "<=" and comparison > 0):
                raise AssertionError(f"canonical incumbent violates factorized RLT ({axis}, {left}, {right}, {other})")
    for left, right, other in transitive_x_ordered_product_links(12):
        span_bounds = ordered_difference_span_bounds(12, "x", left, right, bounds, lower_target)
        span = points[right][0] - points[left][0]
        factor = points[other][1]
        factorized_product = span * factor
        for coefficient_product, coefficient_span, coefficient_factor, rhs, relation in mccormick_inequalities(
            span_bounds,
            bounds[_variable("y", other)],
        ):
            value = coefficient_product * factorized_product + coefficient_span * span + coefficient_factor * factor
            comparison = sign(value - Qx.rational(rhs))
            if (relation == ">=" and comparison < 0) or (relation == "<=" and comparison > 0):
                raise AssertionError(f"canonical incumbent violates transitive factorized RLT ({left}, {right}, {other})")
    chord_bounds = left_chord_span_bounds(bounds, lower_target)
    chord_span = points[4][1] - points[0][1]
    for left, right in transitive_x_ordered_pairs(12):
        span_bounds = ordered_difference_span_bounds(12, "x", left, right, bounds, lower_target)
        span = points[right][0] - points[left][0]
        factorized_product = span * chord_span
        for coefficient_product, coefficient_span, coefficient_chord, rhs, relation in mccormick_inequalities(
            span_bounds,
            chord_bounds,
        ):
            value = coefficient_product * factorized_product + coefficient_span * span + coefficient_chord * chord_span
            comparison = sign(value - Qx.rational(rhs))
            if (relation == ">=" and comparison < 0) or (relation == "<=" and comparison > 0):
                raise AssertionError(f"canonical incumbent violates transitive left-chord rectangle ({left}, {right})")
    for x_left, x_right, y_left, y_right in rectangle_rlt_links(12, bounds):
        cross_difference = (
            points[x_left][0] * points[y_left][1]
            + points[x_right][0] * points[y_right][1]
            - points[x_left][0] * points[y_right][1]
            - points[x_right][0] * points[y_left][1]
        )
        x_span = points[x_right][0] - points[x_left][0]
        y_span = points[y_right][1] - points[y_left][1]
        if (
            sign(cross_difference) < 0
            or sign(cross_difference - x_span) > 0
            or sign(cross_difference - y_span) > 0
        ):
            raise AssertionError(f"canonical incumbent violates rectangle RLT ({x_left}, {x_right}, {y_left}, {y_right})")
    minimum_count = strip_count_for_target(lower_target)
    for index in target_left_strip_exclusion_indices(12):
        if sign(points[index][0] - Qx.rational(Fraction(1, minimum_count))) < 0:
            raise AssertionError(f"canonical incumbent violates left-strip exclusion row ({index})")
        if sign(points[index][0] - Qx.rational(2 * lower_target)) < 0:
            raise AssertionError(f"canonical incumbent violates left-chord x row ({index})")
    if sign(points[4][1] - points[0][1] - Qx.rational(2 * lower_target)) < 0:
        raise AssertionError("canonical incumbent violates left-chord y-span row")
    for left, right in target_x_spacing_pairs(12):
        if sign(points[right][0] - points[left][0] - Qx.rational(2 * lower_target)) < 0:
            raise AssertionError(f"canonical incumbent violates x-span packing row ({left}, {right})")
    chord_bounds = left_chord_span_bounds(bounds, lower_target)
    chord_span = points[4][1] - points[0][1]
    for index in target_left_strip_exclusion_indices(12):
        factorized_product = points[index][0] * chord_span
        for coefficient_product, coefficient_x, coefficient_chord, rhs, relation in mccormick_inequalities(
            bounds[_variable("x", index)], chord_bounds
        ):
            value = (
                coefficient_product * factorized_product
                + coefficient_x * points[index][0]
                + coefficient_chord * chord_span
            )
            comparison = sign(value - Qx.rational(rhs))
            if (relation == ">=" and comparison < 0) or (relation == "<=" and comparison > 0):
                raise AssertionError(f"canonical incumbent violates left-chord McCormick row ({index})")

    for left in range(12):
        for right in range(12):
            if left == right:
                continue
            x_name, y_name = _variable("x", left), _variable("y", right)
            product = points[left][0] * points[right][1]
            if not _mccormick_contains_qx(points[left][0], points[right][1], product, bounds[x_name], bounds[y_name]):
                raise AssertionError(f"canonical incumbent violates McCormick row ({left}, {right})")

    z = Qx.rational(lower_target)
    maximum_area = Qx.rational(area_upper_bound(12))
    if sign(z - maximum_area) > 0:
        raise AssertionError("target exceeds the model's elementary z upper bound")
    big_m = Qx.rational(Fraction(1, 2) + area_upper_bound(12))
    for triangle in combinations(range(12), 3):
        area = signed_double_area(points, triangle) * Fraction(1, 2)
        if sign(area - Qx.rational(Fraction(-1, 2))) < 0 or sign(Qx.rational(Fraction(1, 2)) - area) < 0:
            raise AssertionError(f"canonical incumbent violates signed-area bounds for {triangle}")
        orientation = fixed_orientation(triangle)
        if orientation == 1:
            if sign(z - area) > 0:
                raise AssertionError(f"canonical incumbent violates fixed-positive z row for {triangle}")
        elif orientation == -1:
            if sign(z + area) > 0:
                raise AssertionError(f"canonical incumbent violates fixed-negative z row for {triangle}")
        else:
            binary = Qx.rational(1 if sign(area) >= 0 else 0)
            if sign(z - area + big_m * binary - big_m) > 0 or sign(z + area - big_m * binary) > 0:
                raise AssertionError(f"canonical incumbent violates free-sign z rows for {triangle}")

    count = minimum_count if strip_count is None else strip_count
    if count < minimum_count:
        raise ValueError("strip count is too small for the proved lower target")
    x_strips = _capacity_two_assignment(tuple(_strip_candidates(point[0], count) for point in points), count)
    y_strips = _capacity_two_assignment(tuple(_strip_candidates(point[1], count) for point in points), count)
    _verify_exact_strip_rows(points, count, x_strips, y_strips)
    extras = tuple(sorted(set(additional_strip_counts)))
    if any(extra < minimum_count for extra in extras):
        raise ValueError("additional strip count is too small for the proved lower target")
    extras = tuple(extra for extra in extras if extra != count)
    extra_x = tuple(
        _capacity_two_assignment(tuple(_strip_candidates(point[0], extra) for point in points), extra)
        for extra in extras
    )
    extra_y = tuple(
        _capacity_two_assignment(tuple(_strip_candidates(point[1], extra) for point in points), extra)
        for extra in extras
    )
    for extra, extra_x_assignment, extra_y_assignment in zip(extras, extra_x, extra_y):
        _verify_exact_strip_rows(points, extra, extra_x_assignment, extra_y_assignment)
    return IncumbentLift(lower_target, count, x_strips, y_strips, extras, extra_x, extra_y)


def _validated_piecewise_product_pairs(
    n: int,
    product_pairs: Sequence[Tuple[int, int]] | None,
) -> Tuple[Tuple[int, int], ...] | None:
    """Canonicalize an optional nonempty subset of directed product pairs."""

    if product_pairs is None:
        return None
    normalized = []
    for pair in product_pairs:
        if len(pair) != 2:
            raise ValueError("each piecewise product must contain exactly two indices")
        left, right = pair
        if not (0 <= left < n and 0 <= right < n) or left == right:
            raise ValueError("piecewise product indices must be distinct point indices in range")
        normalized.append((left, right))
    if not normalized:
        raise ValueError("piecewise product selection must be nonempty; omit it to select every product")
    return tuple(sorted(set(normalized)))


def verify_canonical_incumbent_piecewise_lift(
    lower_target: Fraction = Fraction(1, 31),
    *,
    strip_count: int | None = None,
    piecewise_cell_count: int | None = None,
    piecewise_product_pairs: Sequence[Tuple[int, int]] | None = None,
) -> IncumbentLift:
    """Check every strip-conditioned McCormick row at the exact incumbent."""

    lift = verify_canonical_incumbent_lift(lower_target, strip_count=strip_count)
    cell_count = lift.strip_count if piecewise_cell_count is None else piecewise_cell_count
    if not 2 <= cell_count <= lift.strip_count or lift.strip_count % cell_count:
        raise ValueError("piecewise cell count must divide the strip count and be between 2 and that count")
    points = canonical_incumbent_points()
    bounds = target_tightened_coordinate_bounds(12, canonical_coordinate_bounds(12), lower_target)
    pairs = _validated_piecewise_product_pairs(12, piecewise_product_pairs)
    pairs = (
        tuple((left, right) for left in range(12) for right in range(12) if left != right)
        if pairs is None
        else pairs
    )
    for left, right in pairs:
        x_name, y_name = _variable("x", left), _variable("y", right)
        x, y, product = points[left][0], points[right][1], points[left][0] * points[right][1]
        for axis, selected_strip in (("x", lift.x_strips[left]), ("y", lift.y_strips[right])):
            coordinate_name = x_name if axis == "x" else y_name
            strips_per_cell = lift.strip_count // cell_count
            for current_cell in range(cell_count):
                segment = _intersection(
                    bounds[coordinate_name],
                    (Fraction(current_cell, cell_count), Fraction(current_cell + 1, cell_count)),
                )
                if segment is None:
                    continue
                x_bounds, y_bounds = (segment, bounds[y_name]) if axis == "x" else (bounds[x_name], segment)
                membership = Fraction(
                    current_cell * strips_per_cell <= selected_strip < (current_cell + 1) * strips_per_cell
                )
                for coefficient_w, coefficient_x, coefficient_y, rhs, relation in mccormick_inequalities(
                    x_bounds, y_bounds
                ):
                    value = coefficient_w * product + coefficient_x * x + coefficient_y * y
                    if relation == ">=":
                        if sign(value - _PIECEWISE_DEACTIVATION_M * membership - Qx.rational(rhs - _PIECEWISE_DEACTIVATION_M)) < 0:
                            raise AssertionError(f"piecewise lower row rejects incumbent ({axis}, {left}, {right}, {current_cell})")
                    elif sign(value + _PIECEWISE_DEACTIVATION_M * membership - Qx.rational(rhs + _PIECEWISE_DEACTIVATION_M)) > 0:
                        raise AssertionError(f"piecewise upper row rejects incumbent ({axis}, {left}, {right}, {current_cell})")
    return lift


def verify_canonical_incumbent_joint_piecewise_lift(
    lower_target: Fraction = Fraction(1, 31),
    *,
    strip_count: int | None = None,
    piecewise_cell_count: int | None = None,
    piecewise_product_pairs: Sequence[Tuple[int, int]] | None = None,
) -> IncumbentLift:
    """Check every joint-cell activation and local envelope at the record.

    This is the exact-field counterpart of
    :func:`_add_joint_piecewise_mccormick_rows`.  It validates both the
    continuous AND rows and every active/inactive local McCormick inequality,
    rather than merely checking that the record falls in a coarse cell.
    """

    lift = verify_canonical_incumbent_lift(lower_target, strip_count=strip_count)
    cell_count = lift.strip_count if piecewise_cell_count is None else piecewise_cell_count
    if not 2 <= cell_count <= lift.strip_count or lift.strip_count % cell_count:
        raise ValueError("joint piecewise cell count must divide the strip count and be between 2 and that count")
    points = canonical_incumbent_points()
    bounds = target_tightened_coordinate_bounds(12, canonical_coordinate_bounds(12), lower_target)
    pairs = _validated_piecewise_product_pairs(12, piecewise_product_pairs)
    pairs = (
        tuple((left, right) for left in range(12) for right in range(12) if left != right)
        if pairs is None
        else pairs
    )
    strips_per_cell = lift.strip_count // cell_count
    for left, right in pairs:
        x_name, y_name = _variable("x", left), _variable("y", right)
        x, y, product = points[left][0], points[right][1], points[left][0] * points[right][1]
        assignment = Fraction(0)
        for x_cell in range(cell_count):
            x_bounds = _intersection(bounds[x_name], (Fraction(x_cell, cell_count), Fraction(x_cell + 1, cell_count)))
            if x_bounds is None:
                continue
            x_membership = Fraction(
                x_cell * strips_per_cell <= lift.x_strips[left] < (x_cell + 1) * strips_per_cell
            )
            for y_cell in range(cell_count):
                y_bounds = _intersection(
                    bounds[y_name], (Fraction(y_cell, cell_count), Fraction(y_cell + 1, cell_count))
                )
                if y_bounds is None:
                    continue
                y_membership = Fraction(
                    y_cell * strips_per_cell <= lift.y_strips[right] < (y_cell + 1) * strips_per_cell
                )
                joint = x_membership * y_membership
                assignment += joint
                if joint > x_membership or joint > y_membership or joint < x_membership + y_membership - 1:
                    raise AssertionError(f"joint cell AND rows reject incumbent ({left}, {right}, {x_cell}, {y_cell})")
                for coefficient_w, coefficient_x, coefficient_y, rhs, relation in mccormick_inequalities(x_bounds, y_bounds):
                    value = coefficient_w * product + coefficient_x * x + coefficient_y * y
                    if relation == ">=":
                        if sign(
                            value
                            - Qx.rational(_PIECEWISE_DEACTIVATION_M * joint)
                            - Qx.rational(rhs - _PIECEWISE_DEACTIVATION_M)
                        ) < 0:
                            raise AssertionError(
                                f"joint piecewise lower row rejects incumbent ({left}, {right}, {x_cell}, {y_cell})"
                            )
                    elif sign(
                        value
                        + Qx.rational(_PIECEWISE_DEACTIVATION_M * joint)
                        - Qx.rational(rhs + _PIECEWISE_DEACTIVATION_M)
                    ) > 0:
                        raise AssertionError(
                            f"joint piecewise upper row rejects incumbent ({left}, {right}, {x_cell}, {y_cell})"
                        )
        if assignment != 1:
            raise AssertionError(f"joint-cell assignment misses incumbent product ({left}, {right})")
    return lift


def build_model(
    n: int = 12,
    *,
    spatial_box: SpatialBox | None = None,
    lower_target: Fraction | None = None,
    strip_count_override: int | None = None,
    additional_strip_counts: Sequence[int] = (),
    piecewise_strip_products: bool = False,
    joint_piecewise_strip_products: bool = False,
    piecewise_cell_count: int | None = None,
    piecewise_product_pairs: Sequence[Tuple[int, int]] | None = None,
) -> RelaxationModel:
    """Build a global or closed-subbox five-boundary McCormick relaxation."""

    bounds = _validated_bounds(n, spatial_box)
    triangles: Tuple[Triangle, ...] = tuple(combinations(range(n), 3))
    upper = area_upper_bound(n)
    if lower_target is not None and not Fraction(0) < lower_target <= upper:
        raise ValueError("lower target must lie in (0, elementary upper bound]")
    if lower_target is not None:
        bounds = target_tightened_coordinate_bounds(n, bounds, lower_target)
    if lower_target is None and (strip_count_override is not None or additional_strip_counts):
        raise ValueError("a strip count requires a proved lower target")
    minimum_strip_count = strip_count_for_target(lower_target) if lower_target is not None else None
    if lower_target is not None and strip_count_override is not None and strip_count_override < minimum_strip_count:
        raise ValueError("strip count is too small for the proved lower target")
    strip_count = strip_count_override if strip_count_override is not None else minimum_strip_count
    extra_counts = tuple(sorted(set(additional_strip_counts)))
    if lower_target is not None and any(count < minimum_strip_count for count in extra_counts):
        raise ValueError("additional strip count is too small for the proved lower target")
    if strip_count is not None:
        extra_counts = tuple(count for count in extra_counts if count != strip_count)
    uses_piecewise_products = piecewise_strip_products or joint_piecewise_strip_products
    if uses_piecewise_products and strip_count is None:
        raise ValueError("piecewise strip products require a proved lower target")
    if piecewise_cell_count is not None and not uses_piecewise_products:
        raise ValueError("a piecewise cell count requires axis-wise or joint piecewise strip products")
    if piecewise_product_pairs is not None and not uses_piecewise_products:
        raise ValueError("piecewise product selection requires axis-wise or joint piecewise strip products")
    effective_piecewise_cells = None
    effective_piecewise_pairs = None
    if uses_piecewise_products:
        assert strip_count is not None
        effective_piecewise_cells = strip_count if piecewise_cell_count is None else piecewise_cell_count
        if not 2 <= effective_piecewise_cells <= strip_count or strip_count % effective_piecewise_cells:
            raise ValueError("piecewise cell count must divide the primary strip count and be between 2 and that count")
        effective_piecewise_pairs = _validated_piecewise_product_pairs(n, piecewise_product_pairs)
    big_m = Fraction(1, 2) + upper
    lines = ["Maximize", " objective: z", "Subject To"]
    binary_triangles: list[Triangle] = []
    binary_variables: list[str] = []
    joint_variables: list[str] = []

    for index, (left, right) in enumerate(canonical_orderings(n)):
        lines.append(_inequality(f"ordering_{index}", ((Fraction(1), left), (Fraction(-1), right)), "<=", Fraction(0)))

    for axis, left, right, other in ordered_product_links(n):
        if axis == "x":
            smaller_product = _product(left, other)
            larger_product = _product(right, other)
            smaller_coordinate = _variable("x", left)
            larger_coordinate = _variable("x", right)
        else:
            smaller_product = _product(other, left)
            larger_product = _product(other, right)
            smaller_coordinate = _variable("y", left)
            larger_coordinate = _variable("y", right)
        label = f"rlt_{axis}_{left}_{right}_{other}"
        lines.append(
            _inequality(
                f"{label}_lower",
                ((Fraction(1), smaller_product), (Fraction(-1), larger_product)),
                "<=",
                Fraction(0),
            )
        )
        lines.append(
            _inequality(
                f"{label}_upper",
                (
                    (Fraction(1), larger_product),
                    (Fraction(-1), smaller_product),
                    (Fraction(-1), larger_coordinate),
                    (Fraction(1), smaller_coordinate),
                ),
                "<=",
                Fraction(0),
            )
        )

    _add_bound_strengthened_ordered_product_constraints(lines, n, bounds)
    _add_rectangle_rlt_constraints(lines, n, bounds)

    if lower_target is not None and strip_count is not None:
        lines.append(_inequality("target_floor", ((Fraction(1), "z"),), ">=", lower_target))
        assert minimum_strip_count is not None
        for index in target_left_strip_exclusion_indices(n):
            lines.append(
                _inequality(
                    f"packing_x_left_strip_{index}",
                    ((Fraction(1), _variable("x", index)),),
                    ">=",
                    Fraction(1, minimum_strip_count),
                )
            )
            lines.append(
                _inequality(
                    f"packing_x_left_chord_{index}",
                    ((Fraction(1), _variable("x", index)),),
                    ">=",
                    2 * lower_target,
                )
            )
        lines.append(
            _inequality(
                "packing_y_left_chord_span",
                ((Fraction(1), _variable("y", 4)), (Fraction(-1), _variable("y", 0))),
                ">=",
                2 * lower_target,
            )
        )
        for left, right in target_x_spacing_pairs(n):
            lines.append(
                _inequality(
                    f"packing_x_span_{left}_{right}",
                    ((Fraction(1), _variable("x", right)), (Fraction(-1), _variable("x", left))),
                    ">=",
                    2 * lower_target,
                )
            )
        _add_ordered_difference_mccormick_constraints(lines, n, bounds, lower_target)
        _add_transitive_x_difference_mccormick_constraints(lines, n, bounds, lower_target)
        _add_left_chord_product_constraints(lines, n, bounds, lower_target)
        _add_transitive_left_chord_rectangle_constraints(lines, n, bounds, lower_target)
        _add_strip_constraints(lines, binary_variables, n, "x", strip_count)
        _add_strip_constraints(lines, binary_variables, n, "y", strip_count)
        for count in extra_counts:
            _add_strip_constraints(lines, binary_variables, n, "x", count, grid=count)
            _add_strip_constraints(lines, binary_variables, n, "y", count, grid=count)

    for left in range(n):
        for right in range(n):
            if left == right:
                continue
            product = _product(left, right)
            x_name = _variable("x", left)
            y_name = _variable("y", right)
            for index, (coefficient_w, coefficient_x, coefficient_y, rhs, relation) in enumerate(
                mccormick_inequalities(bounds[x_name], bounds[y_name])
            ):
                lines.append(
                    _inequality(
                        f"mccormick_{left}_{right}_{index}",
                        ((coefficient_w, product), (coefficient_x, x_name), (coefficient_y, y_name)),
                        relation,
                        rhs,
                    )
                )

    if piecewise_strip_products:
        assert strip_count is not None
        assert effective_piecewise_cells is not None
        _add_piecewise_mccormick_rows(
            lines,
            n,
            bounds,
            strip_count,
            effective_piecewise_cells,
            effective_piecewise_pairs,
        )
    if joint_piecewise_strip_products:
        assert strip_count is not None
        assert effective_piecewise_cells is not None
        _add_joint_piecewise_mccormick_rows(
            lines,
            joint_variables,
            n,
            bounds,
            strip_count,
            effective_piecewise_cells,
            effective_piecewise_pairs,
        )

    for triangle in triangles:
        name = _triangle_name(triangle)
        area_terms = _signed_area_terms(triangle, Fraction(1))
        lines.append(_inequality(f"area_upper_{name}", area_terms, "<=", Fraction(1, 2)))
        lines.append(_inequality(f"area_lower_{name}", area_terms, ">=", Fraction(-1, 2)))
        orientation = fixed_orientation(triangle)
        if orientation == 1:
            fixed_positive = ((Fraction(1), "z"),) + tuple((-coefficient, variable) for coefficient, variable in area_terms)
            lines.append(_inequality(f"fixed_positive_{name}", fixed_positive, "<=", Fraction(0)))
        elif orientation == -1:
            fixed_negative = ((Fraction(1), "z"),) + area_terms
            lines.append(_inequality(f"fixed_negative_{name}", fixed_negative, "<=", Fraction(0)))
        else:
            binary = _sign(triangle)
            positive = ((Fraction(1), "z"),) + tuple((-coefficient, variable) for coefficient, variable in area_terms) + ((big_m, binary),)
            negative = ((Fraction(1), "z"),) + area_terms + ((-big_m, binary),)
            lines.append(_inequality(f"sign_positive_{name}", positive, "<=", big_m))
            lines.append(_inequality(f"sign_negative_{name}", negative, "<=", Fraction(0)))
            binary_triangles.append(triangle)
            binary_variables.append(binary)

    lines.append("Bounds")
    for variable in sorted(bounds):
        lower, upper_coordinate = bounds[variable]
        lines.append(f" {_decimal(lower, 'down')} <= {variable} <= {_decimal(upper_coordinate, 'up')}")
    for left in range(n):
        for right in range(n):
            if left != right:
                lines.append(f" 0 <= {_product(left, right)} <= 1")
    for variable in joint_variables:
        lines.append(f" 0 <= {variable} <= 1")
    z_lower = Fraction(0) if lower_target is None else lower_target
    lines.append(f" {_decimal(z_lower, 'down')} <= z <= {_decimal(upper, 'up')}")
    lines.append("Binary")
    lines.extend(f" {variable}" for variable in binary_variables)
    lines.append("End")
    return RelaxationModel(
        n,
        triangles,
        tuple(binary_triangles),
        bounds,
        upper,
        big_m,
        lower_target,
        strip_count,
        extra_counts,
        piecewise_strip_products,
        joint_piecewise_strip_products,
        effective_piecewise_cells,
        effective_piecewise_pairs,
        "\n".join(lines) + "\n",
    )


def verify_canonical_incumbent_model_lift(
    lower_target: Fraction = Fraction(1, 31),
    *,
    strip_count_override: int | None = None,
    additional_strip_counts: Sequence[int] = (),
    piecewise_strip_products: bool = False,
    joint_piecewise_strip_products: bool = False,
    piecewise_cell_count: int | None = None,
    piecewise_product_pairs: Sequence[Tuple[int, int]] | None = None,
) -> IncumbentLift:
    """Exactly audit the incumbent against every symbolic root-model row family.

    The LP text itself is deliberately numerical, but this checker follows the
    same model-generation parameters using the cubic-field record coordinates.
    It verifies pins, orderings, RLT rows, all product and triangle rows, every
    enabled strip grid, and optional primary-grid piecewise rows.
    """

    model = build_model(
        12,
        lower_target=lower_target,
        strip_count_override=strip_count_override,
        additional_strip_counts=additional_strip_counts,
        piecewise_strip_products=piecewise_strip_products,
        joint_piecewise_strip_products=joint_piecewise_strip_products,
        piecewise_cell_count=piecewise_cell_count,
        piecewise_product_pairs=piecewise_product_pairs,
    )
    if model.strip_count is None:
        raise AssertionError("root incumbent audit requires an enabled primary strip grid")
    lift = verify_canonical_incumbent_lift(
        lower_target,
        strip_count=model.strip_count,
        additional_strip_counts=model.additional_strip_counts,
    )
    if model.piecewise_strip_products:
        piecewise_lift = verify_canonical_incumbent_piecewise_lift(
            lower_target,
            strip_count=model.strip_count,
            piecewise_cell_count=model.piecewise_cell_count,
            piecewise_product_pairs=model.piecewise_product_pairs,
        )
        if piecewise_lift.x_strips != lift.x_strips or piecewise_lift.y_strips != lift.y_strips:
            raise AssertionError("piecewise and root lift selected different primary strips")
    if model.joint_piecewise_strip_products:
        joint_lift = verify_canonical_incumbent_joint_piecewise_lift(
            lower_target,
            strip_count=model.strip_count,
            piecewise_cell_count=model.piecewise_cell_count,
            piecewise_product_pairs=model.piecewise_product_pairs,
        )
        if joint_lift.x_strips != lift.x_strips or joint_lift.y_strips != lift.y_strips:
            raise AssertionError("joint piecewise and root lift selected different primary strips")
    return lift


_MIP_PROGRESS = re.compile(
    r"mip\s*=\s*(?:(?P<incumbent>[+\-0-9.eE]+)|not\s+found\s+yet)"
    r"\s*<=\s*(?P<upper>\+inf|tree\s+is\s+empty|[+\-0-9.eE]+)"
)
_MIP_CANDIDATE = re.compile(r">>>>>\s*(?P<incumbent>[+\-0-9.eE]+)\s*<=\s*(?P<upper>\+inf|[+\-0-9.eE]+)")
_LP_PROGRESS = re.compile(r"obj\s*=\s*([+\-0-9.eE]+)")


def _as_float(token: str | None) -> float | None:
    if token is None:
        return None
    try:
        value = float(token)
    except ValueError:
        return None
    return value if math.isfinite(value) else None


def _fraction_argument(value: str) -> Fraction:
    try:
        return Fraction(value)
    except (ValueError, ZeroDivisionError) as error:
        raise argparse.ArgumentTypeError(f"invalid rational value: {value!r}") from error


def _product_pair_argument(value: str) -> Tuple[int, int]:
    """Parse one directed product selector of the form ``LEFT,RIGHT``."""

    fields = value.split(",")
    if len(fields) != 2:
        raise argparse.ArgumentTypeError("piecewise product must have form LEFT,RIGHT")
    try:
        return int(fields[0]), int(fields[1])
    except ValueError as error:
        raise argparse.ArgumentTypeError(f"invalid piecewise product: {value!r}") from error


def _parse_glpsol_report(
    model: RelaxationModel,
    command: Tuple[str, ...],
    returncode: int,
    output: str,
) -> SolverReport:
    """Interpret GLPK output without confusing LP and MIP termination states.

    GLPK prints ``OPTIMAL LP SOLUTION FOUND`` before beginning branch-and-bound.
    That is an upper bound for a maximization MIP, not evidence that its integer
    problem was solved.  Likewise, a timed-out search may have no feasible MIP
    incumbent even though its LP relaxation has an objective value.
    """

    events = [
        (match.start(), match)
        for expression in (_MIP_PROGRESS, _MIP_CANDIDATE)
        for match in expression.finditer(output)
    ]
    events.sort(key=lambda event: event[0])
    incumbent = None
    reported_upper = None
    for _, event in events:
        event_incumbent = _as_float(event.group("incumbent"))
        event_upper = _as_float(event.group("upper"))
        if event_incumbent is not None:
            incumbent = event_incumbent
        if event_upper is not None:
            reported_upper = event_upper

    root_lp_output = output.split("Integer optimization begins", 1)[0]
    objectives = list(_LP_PROGRESS.finditer(root_lp_output))
    lp_upper = (
        _as_float(objectives[-1].group(1))
        if "OPTIMAL LP SOLUTION FOUND" in root_lp_output and objectives
        else None
    )

    has_integer_variables = model.binary_count > 0
    if "INTEGER OPTIMAL SOLUTION FOUND" in output:
        if incumbent is not None:
            status = "optimal"
            reported_upper = incumbent
        else:
            # Do not label a root-LP fallback as the solved integer optimum.
            # It remains a numerical outer upper bound, but the integer value
            # was not recovered from the log grammar.
            status = "optimal-unparsed"
            if reported_upper is None:
                reported_upper = lp_upper
    elif "TIME LIMIT EXCEEDED" in output:
        status = "time-limit"
        if reported_upper is None:
            reported_upper = lp_upper
    elif "PROBLEM HAS NO INTEGER FEASIBLE SOLUTION" in output:
        status = "infeasible"
    elif not has_integer_variables and "OPTIMAL LP SOLUTION FOUND" in output:
        status = "optimal"
        incumbent = lp_upper
        reported_upper = lp_upper
    else:
        status = "other"

    return SolverReport(command, returncode, status, incumbent, reported_upper, output)


def run_glpsol(
    model: RelaxationModel,
    *,
    time_limit_seconds: int = 30,
    solver: str = "glpsol",
    export_lp: Path | None = None,
    export_solution: Path | None = None,
) -> SolverReport:
    """Run GLPK and return its numerical MIP progress without embellishment."""

    if time_limit_seconds <= 0:
        raise ValueError("time limit must be positive")
    executable = shutil.which(solver)
    if executable is None:
        raise FileNotFoundError(f"{solver!r} is not available on PATH")
    if export_lp is not None:
        export_lp.write_text(model.text)
    with tempfile.TemporaryDirectory(prefix="heilbronn-mccormick-") as temporary:
        lp_path = Path(temporary) / "model.lp"
        lp_path.write_text(model.text)
        command = (executable, "--lp", str(lp_path), "--tmlim", str(time_limit_seconds), "--cuts", "--fpump")
        if export_solution is not None:
            command += ("--output", str(export_solution))
        completed = subprocess.run(command, check=False, capture_output=True, text=True)
    output = completed.stdout + completed.stderr
    return _parse_glpsol_report(model, command, completed.returncode, output)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n", type=int, default=5, help="point count; n=5 is the calibration default")
    parser.add_argument("--time-limit", type=int, default=30, help="GLPK time limit in seconds")
    parser.add_argument("--solver", default="glpsol")
    parser.add_argument("--export-lp", type=Path, help="optional persistent LP export path")
    parser.add_argument("--export-solution", type=Path, help="optional persistent GLPK solution export")
    parser.add_argument(
        "--lower-target",
        type=_fraction_argument,
        help="proved lower target; enables valid horizontal/vertical strip-capacity cuts",
    )
    parser.add_argument("--strip-count", type=int, help="optional finer strip count (must satisfy the target inequality)")
    parser.add_argument(
        "--additional-strip-count",
        type=int,
        action="append",
        help="add an independent valid strip grid; may be passed more than once",
    )
    parser.add_argument(
        "--piecewise-strips",
        action="store_true",
        help="activate strip-conditioned McCormick rows using the primary strip grid",
    )
    parser.add_argument(
        "--joint-piecewise-strips",
        action="store_true",
        help="activate joint x-cell/y-cell McCormick disjunctions using the primary strip grid",
    )
    parser.add_argument(
        "--piecewise-cells",
        type=int,
        help="equal coarse cells for --piecewise-strips (default: every primary strip)",
    )
    parser.add_argument(
        "--piecewise-product",
        type=_product_pair_argument,
        action="append",
        help="restrict piecewise rows to directed product LEFT,RIGHT; may be repeated",
    )
    parser.add_argument("--no-solve", action="store_true", help="only print model dimensions")
    arguments = parser.parse_args()
    model = build_model(
        arguments.n,
        lower_target=arguments.lower_target,
        strip_count_override=arguments.strip_count,
        additional_strip_counts=arguments.additional_strip_count or (),
        piecewise_strip_products=arguments.piecewise_strips,
        joint_piecewise_strip_products=arguments.joint_piecewise_strips,
        piecewise_cell_count=arguments.piecewise_cells,
        piecewise_product_pairs=arguments.piecewise_product,
    )
    print("n", model.n)
    print("triangles", len(model.triangles))
    print("products", model.product_count)
    print("binary_variables", model.binary_count)
    print("area_upper_bound", _decimal(model.area_upper_bound))
    print("big_m", _decimal(model.big_m))
    print("lower_target", None if model.lower_target is None else _decimal(model.lower_target))
    print("strip_count", model.strip_count)
    print("additional_strip_counts", model.additional_strip_counts)
    print("piecewise_strip_products", model.piecewise_strip_products)
    print("joint_piecewise_strip_products", model.joint_piecewise_strip_products)
    print("piecewise_cell_count", model.piecewise_cell_count)
    print("piecewise_product_pairs", model.piecewise_product_pairs)
    if arguments.no_solve:
        if arguments.export_lp is not None:
            arguments.export_lp.write_text(model.text)
            print("export_lp", arguments.export_lp)
        return
    report = run_glpsol(
        model,
        time_limit_seconds=arguments.time_limit,
        solver=arguments.solver,
        export_lp=arguments.export_lp,
        export_solution=arguments.export_solution,
    )
    print("solver_status", report.status)
    print("solver_returncode", report.returncode)
    print("solver_incumbent", report.incumbent)
    print("solver_reported_upper", report.reported_upper)
    print("interpretation", "NUMERICAL OUTER RELAXATION ONLY; not an exact certificate")


if __name__ == "__main__":
    main()
