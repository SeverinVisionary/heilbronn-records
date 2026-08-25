"""Exact, globally scoped interval branch-and-bound in the five-boundary form.

For every spatial box this module evaluates all 220 triangle determinants at
the box vertices using ``Fraction`` arithmetic.  A determinant is affine in
each of its six coordinate arguments, so its maximum absolute value on that
box occurs at a vertex.  The smallest of those 220 vertex maxima is therefore
a rigorous upper bound on the *least* triangle area of every configuration in
the box.

The root is the five-boundary normal form used by
``global_mccormick_relaxation``.  Conditional on the cited Sudermann--Merx
boundary theorem, an optimizer can be placed in that normal form, so an
emptied queue would be a global no-improvement proof.  A finite budget is
intentionally reported as ``INCOMPLETE``; it never establishes a global bound
by itself.
"""

from __future__ import annotations

import argparse
import heapq
from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations, product
from typing import Mapping, Tuple

from global_mccormick_relaxation import (
    SpatialBox,
    canonical_incumbent_points,
    root_spatial_box,
    strip_count_for_target,
    target_tightened_coordinate_bounds,
)
from incumbent import Qx, algebraic_bounds, incumbent_value, sign


Interval = Tuple[Fraction, Fraction]
PointBox = Tuple[Interval, Interval]
Triangle = Tuple[int, int, int]
TRIANGLES: Tuple[Triangle, ...] = tuple(combinations(range(12), 3))
# A strict record improver also exceeds this rational lower enclosure of the
# algebraic incumbent.  It is much tighter than the historical 1/31 filter yet
# remains strictly below the record, and the same 16-strip capacity theorem
# applies because 1/32 is still below this target.
TARGET_BISECTIONS = 64
TARGET, _ = algebraic_bounds(incumbent_value(), TARGET_BISECTIONS)
STRIP_COUNTS = (strip_count_for_target(TARGET), 20)
# A second valid partition at a half-cell phase catches triples that straddle
# an aligned-grid boundary.  Every cell remains no wider than 1/16, which is
# strictly less than twice the target area.
SHIFTED_STRIP_PARTITIONS = ((16, Fraction(1, 32)),)
# A two-dimensional cell of one of these grids has area strictly below
# ``2*TARGET``.  Therefore every such cell has capacity two: three points in
# it determine a triangle of area at most half the rectangle area.  Unlike
# separate x/y strip matchings, these grids retain the joint spatial coupling.
RECTANGLE_CAPACITY_PARTITIONS = ((4, 4), (2, 8), (8, 2), (3, 6), (6, 3))


@dataclass(frozen=True)
class DiscardedBox:
    """A box pruned by one exact one-sided target condition."""

    box: SpatialBox
    reason: str
    witness: Triangle | None
    witness_upper: Fraction


@dataclass(frozen=True)
class StrictImprovementWitness:
    """An exactly pinned rational configuration strictly above the record."""

    box: SpatialBox
    minimum_area: Fraction
    minimum_triangle: Triangle


@dataclass(frozen=True)
class Exploration:
    """Replayable state of one finite or complete exact cover attempt."""

    visited_boxes: int
    discarded_boxes: int
    pending_boxes: int
    maximum_depth: int
    complete: bool
    largest_pending_upper: Fraction | None
    discarded: Tuple[DiscardedBox, ...]
    pending: Tuple[SpatialBox, ...]
    strict_improvements: Tuple[StrictImprovementWitness, ...]
    anchor_trims: int = 0
    # The full per-slab audit trail: every trim's named triangle, removed
    # sub-box, and certified supremum survive into the returned exploration
    # so a downstream audit can re-verify each removal without re-running.
    anchor_trim_records: Tuple["AnchorTrim", ...] = ()


def points_for_box(box: SpatialBox) -> Tuple[PointBox, ...]:
    """Return all point-coordinate intervals represented by a spatial box."""

    return tuple((box.coordinate_bounds[f"x_{index}"], box.coordinate_bounds[f"y_{index}"]) for index in range(12))


def double_area_vertex_upper(points: Tuple[PointBox, ...], triangle: Triangle) -> Fraction:
    """Return the exact vertex maximum of one absolute double area."""

    first, second, third = triangle
    coordinates = points[first] + points[second] + points[third]
    varying = tuple(index for index, interval in enumerate(coordinates) if interval[0] != interval[1])
    values = [interval[0] for interval in coordinates]
    maximum = Fraction(0)
    for endpoints in product((0, 1), repeat=len(varying)):
        for index, endpoint in zip(varying, endpoints):
            values[index] = coordinates[index][endpoint]
        x_first, y_first, x_second, y_second, x_third, y_third = values
        determinant = (x_second - x_first) * (y_third - y_first) - (y_second - y_first) * (x_third - x_first)
        maximum = max(maximum, abs(determinant))
    return maximum


def minimum_area_upper(box: SpatialBox) -> Tuple[Fraction, Triangle]:
    """Return an exact upper bound and a witness triangle for one box."""

    points = points_for_box(box)
    candidates = tuple((double_area_vertex_upper(points, triangle) / 2, triangle) for triangle in TRIANGLES)
    return min(candidates, key=lambda candidate: candidate[0])


def cannot_strictly_beat_incumbent(upper: Fraction) -> bool:
    """Decide exactly whether a rational box upper bound is at most the record."""

    return sign(Qx.rational(upper) - incumbent_value()) <= 0


# The five points pinned to a square side by the published normal form.  A
# triangle containing one of them has at least one exactly known coordinate,
# so its determinant enclosure is materially tighter than a free triple's.
ANCHOR_POINTS = (0, 1, 2, 3, 4)


@dataclass(frozen=True)
class AnchorTrim:
    """One certified interval removal produced by anchor-triangle propagation.

    ``removed_box`` is the exact closed sub-box that was cut away and
    ``removed_supremum`` is the exact vertex supremum of the named triangle's
    absolute double area on it.  The construction guarantees the supremum is
    at most the propagation threshold, so no strict improver is removed.
    """

    variable: str
    removed: Interval
    triangle: Triangle
    removed_box: SpatialBox
    removed_supremum: Fraction


@dataclass(frozen=True)
class AnchorPropagation:
    """Outcome of one anchor-triangle propagation call.

    ``box=None`` means the whole input box was discarded: the named
    ``prune_triangle`` has exact absolute-double-area supremum
    ``prune_supremum <= threshold`` on the residual box, and every earlier
    trim in ``trims`` certifies its own removed part the same way.
    """

    box: SpatialBox | None
    trims: Tuple[AnchorTrim, ...]
    prune_triangle: Triangle | None
    prune_supremum: Fraction | None


def anchored_triangles() -> Tuple[Triangle, ...]:
    """Return every triangle containing at least one pinned boundary point."""

    return tuple(triangle for triangle in TRIANGLES if any(point in ANCHOR_POINTS for point in triangle))


def _oriented_determinant_bounds(bounds: Mapping[str, Interval], triangle: Triangle) -> Tuple[Fraction, Fraction]:
    """Return the exact signed determinant range of one oriented triple.

    The determinant is multilinear in its six coordinates, so both extremes
    over a closed box are attained at box vertices; enumerating the vertices
    of the nondegenerate coordinates is therefore exact, not an enclosure.
    """

    first, second, third = triangle
    names = (f"x_{first}", f"y_{first}", f"x_{second}", f"y_{second}", f"x_{third}", f"y_{third}")
    intervals = tuple(bounds[name] for name in names)
    varying = tuple(index for index, interval in enumerate(intervals) if interval[0] != interval[1])
    values = [interval[0] for interval in intervals]
    minimum: Fraction | None = None
    maximum: Fraction | None = None
    for endpoints in product((0, 1), repeat=len(varying)):
        for index, endpoint in zip(varying, endpoints):
            values[index] = intervals[index][endpoint]
        x_first, y_first, x_second, y_second, x_third, y_third = values
        determinant = (x_second - x_first) * (y_third - y_first) - (y_second - y_first) * (x_third - x_first)
        minimum = determinant if minimum is None or determinant < minimum else minimum
        maximum = determinant if maximum is None or determinant > maximum else maximum
    assert minimum is not None and maximum is not None
    return minimum, maximum


# Coefficient of each coordinate in the oriented determinant, as the exact
# difference of two other coordinates: position -> axis -> (plus, minus),
# where entries index the oriented triple.  E.g. the coefficient of ``x_a``
# in ``(x_b-x_a)(y_c-y_a) - (y_b-y_a)(x_c-x_a)`` is ``y_b - y_c``.
_COEFFICIENT_TABLE = {
    (0, "x"): ("y", 1, 2),
    (0, "y"): ("x", 2, 1),
    (1, "x"): ("y", 2, 0),
    (1, "y"): ("x", 0, 2),
    (2, "x"): ("y", 0, 1),
    (2, "y"): ("x", 1, 0),
}


def _oriented_coefficient(
    bounds: Mapping[str, Interval], triangle: Triangle, position: int, axis: str
) -> Interval:
    """Return the exact interval of one coordinate's determinant coefficient."""

    other_axis, plus, minus = _COEFFICIENT_TABLE[(position, axis)]
    plus_lower, plus_upper = bounds[f"{other_axis}_{triangle[plus]}"]
    minus_lower, minus_upper = bounds[f"{other_axis}_{triangle[minus]}"]
    return plus_lower - minus_upper, plus_upper - minus_lower


def _certified_trim(
    bounds: Mapping[str, Interval],
    variable: str,
    removed: Interval,
    named: Triangle,
    threshold: Fraction,
) -> AnchorTrim:
    """Re-certify one removed slab against the named triangle's exact supremum."""

    removed_bounds = dict(bounds)
    removed_bounds[variable] = removed
    removed_box = SpatialBox(removed_bounds)
    supremum = double_area_vertex_upper(points_for_box(removed_box), named)
    if supremum > threshold:
        raise AssertionError(
            f"anchor trim of {variable!r} by triangle {named} is not certified: "
            f"removed supremum {supremum} exceeds threshold {threshold}"
        )
    return AnchorTrim(variable, removed, named, removed_box, supremum)


def _forced_positive_trims(
    bounds: dict[str, Interval],
    oriented: Triangle,
    named: Triangle,
    threshold: Fraction,
    trims: list[AnchorTrim],
) -> bool:
    """Tighten coordinates under the forced one-sided rule ``det >= threshold``.

    The caller must already have proved, from the exact signed range on the
    same ``bounds``, that ``det >= -threshold`` holds everywhere on the box,
    so a strict target violator can only satisfy the positive branch.  For a
    coordinate ``v`` the determinant is ``c*v + r`` with ``c`` and ``r``
    multilinear in the other coordinates; treating their exact ranges as
    independent only weakens the derived bound, never unsoundly strengthens
    it.  The corner quotient is valid without any sign assumption on the
    coordinates themselves: with ``0`` outside the coefficient interval,
    ``(threshold - r) / c`` is monotone in ``r`` for fixed ``c`` and monotone
    in ``c`` for fixed ``r``, so its extremes over the ``(r, c)`` rectangle
    are attained at the four corners.  Every removed slab is additionally
    re-certified by the exact vertex supremum of the named triangle before
    the bounds are narrowed, so a bound error can only crash, never remove
    a strict improver.
    """

    changed = False
    for position, point in enumerate(oriented):
        for axis in ("x", "y"):
            variable = f"{axis}_{point}"
            lower, upper = bounds[variable]
            if lower == upper:
                continue
            coefficient_lower, coefficient_upper = _oriented_coefficient(bounds, oriented, position, axis)
            if coefficient_lower <= 0 <= coefficient_upper:
                continue
            rest_bounds = dict(bounds)
            rest_bounds[variable] = (Fraction(0), Fraction(0))
            rest_lower, rest_upper = _oriented_determinant_bounds(rest_bounds, oriented)
            corners = tuple(
                (threshold - rest) / coefficient
                for rest in (rest_lower, rest_upper)
                for coefficient in (coefficient_lower, coefficient_upper)
            )
            if coefficient_lower > 0:
                bound = min(corners)
                if bound <= lower:
                    continue
                if bound > upper:
                    raise AssertionError(
                        "a fully removable box must be caught by the whole-box supremum prune"
                    )
                trims.append(_certified_trim(bounds, variable, (lower, bound), named, threshold))
                bounds[variable] = (bound, upper)
            else:
                bound = max(corners)
                if bound >= upper:
                    continue
                if bound < lower:
                    raise AssertionError(
                        "a fully removable box must be caught by the whole-box supremum prune"
                    )
                trims.append(_certified_trim(bounds, variable, (bound, upper), named, threshold))
                bounds[variable] = (lower, bound)
            changed = True
    return changed


def anchor_triangle_propagated_box(
    box: SpatialBox,
    *,
    scope: str = "anchored",
    threshold: Fraction | None = None,
    passes: int = 1,
) -> AnchorPropagation:
    """Propagate the exact one-sided rule ``|det| > 2*TARGET`` for each triangle.

    Sign-agnostic by construction: the exact signed determinant range decides
    which branch of ``|det| > threshold`` remains possible, without assuming
    the incumbent's orientation cell.  When both branches remain possible the
    triangle yields no tightening; when neither does, the whole box is
    discarded with the named triangle as its certificate.  A configuration
    whose minimum double area equals the threshold exactly may be removed;
    every strict target violator is retained.
    """

    if passes <= 0:
        raise ValueError("anchor propagation needs at least one pass")
    if scope == "anchored":
        triangles = anchored_triangles()
    elif scope == "all":
        triangles = TRIANGLES
    else:
        raise ValueError("anchor propagation scope must be 'anchored' or 'all'")
    threshold = 2 * TARGET if threshold is None else threshold
    if threshold <= 0:
        raise ValueError("anchor propagation requires a positive threshold")

    bounds = dict(box.coordinate_bounds)
    trims: list[AnchorTrim] = []
    for _ in range(passes):
        changed = False
        for named in triangles:
            minimum, maximum = _oriented_determinant_bounds(bounds, named)
            if maximum <= threshold and minimum >= -threshold:
                supremum = max(maximum, -minimum)
                return AnchorPropagation(None, tuple(trims), named, supremum)
            if minimum >= -threshold:
                oriented = named
            elif maximum <= threshold:
                # Swapping two vertices negates the determinant, so the
                # forced negative branch reuses the positive-branch rule.
                oriented = (named[0], named[2], named[1])
            else:
                continue
            if _forced_positive_trims(bounds, oriented, named, threshold, trims):
                changed = True
        if not changed:
            break
    return AnchorPropagation(SpatialBox(bounds, box.depth), tuple(trims), None, None)


def _strip_candidates(interval: Interval, count: int) -> Tuple[int, ...]:
    """Return all closed equal strips that a coordinate-box interval can meet."""

    lower, upper = interval
    return tuple(
        strip
        for strip in range(count)
        if not (upper < Fraction(strip, count) or lower > Fraction(strip + 1, count))
    )


def shifted_strip_partition(count: int, offset: Fraction) -> Tuple[Fraction, ...]:
    """Return a closed partition with cells of width at most ``1/count``.

    The first and last cells are shortened by a phase ``offset``; all middle
    cells retain the ordinary equal-strip width.  Thus the capacity-two strip
    theorem applies to every cell, while this partition sees triples spanning
    an aligned-grid boundary.
    """

    if count <= 0 or not Fraction(0) < offset < Fraction(1, count):
        raise ValueError("shifted strip offset must lie strictly inside one cell")
    endpoints = (Fraction(0), offset) + tuple(offset + Fraction(strip, count) for strip in range(1, count)) + (Fraction(1),)
    if any(left >= right for left, right in zip(endpoints, endpoints[1:])):
        raise AssertionError("shifted strip endpoints must be strictly increasing")
    if any(right - left > Fraction(1, count) for left, right in zip(endpoints, endpoints[1:])):
        raise AssertionError("shifted strip cell is wider than the aligned grid")
    return endpoints


def capacity_split_boundaries() -> Tuple[Fraction, ...]:
    """Return every interior endpoint used by the exact capacity partitions."""

    endpoints = {Fraction(strip, count) for count in STRIP_COUNTS for strip in range(1, count)}
    for count, offset in SHIFTED_STRIP_PARTITIONS:
        endpoints.update(shifted_strip_partition(count, offset)[1:-1])
    return tuple(sorted(endpoints))


CAPACITY_SPLIT_BOUNDARIES = capacity_split_boundaries()


def _partition_candidates(interval: Interval, endpoints: Tuple[Fraction, ...]) -> Tuple[int, ...]:
    """Return all closed partition cells that a coordinate interval can meet."""

    lower, upper = interval
    return tuple(
        cell
        for cell, (cell_lower, cell_upper) in enumerate(zip(endpoints, endpoints[1:]))
        if not (upper < cell_lower or lower > cell_upper)
    )


def _has_capacity_two_assignment(candidates: Tuple[Tuple[int, ...], ...], count: int) -> bool:
    """Test an exact capacity-two strip matching without making choices numeric."""

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

    return all(augment(point, set()) for point in range(len(candidates)))


def strip_capacity_feasible(box: SpatialBox, counts: Tuple[int, ...] = STRIP_COUNTS) -> bool:
    """Return whether the box can still satisfy every valid capacity-two grid.

    Any strict record improvement has minimum area above the rational
    record-lower ``TARGET``.  Since a 16-strip cell has width ``1/16`` and
    area at most ``1/32 < TARGET`` for any three of its points, no horizontal
    or vertical cell can contain three points.  If even the enlarged interval
    choices admit no capacity-two matching for one grid, the entire box is
    impossible for an improvement.
    """

    if sign(incumbent_value() - Qx.rational(TARGET)) <= 0:
        raise AssertionError("the strip target must remain strictly below the record")
    for count in counts:
        if count < strip_count_for_target(TARGET):
            raise ValueError("strip count is too coarse for the proved target")
        for axis in ("x", "y"):
            candidates = tuple(_strip_candidates(box.coordinate_bounds[f"{axis}_{point}"], count) for point in range(12))
            if not _has_capacity_two_assignment(candidates, count):
                return False
    for count, offset in SHIFTED_STRIP_PARTITIONS:
        if count < strip_count_for_target(TARGET):
            raise AssertionError("shifted strip grid is too coarse for the proved target")
        endpoints = shifted_strip_partition(count, offset)
        for axis in ("x", "y"):
            candidates = tuple(
                _partition_candidates(box.coordinate_bounds[f"{axis}_{point}"], endpoints) for point in range(12)
            )
            if not _has_capacity_two_assignment(candidates, len(endpoints) - 1):
                return False
    return True


def rectangle_capacity_feasible(
    box: SpatialBox,
    partitions: Tuple[Tuple[int, int], ...] = RECTANGLE_CAPACITY_PARTITIONS,
) -> bool:
    """Return whether every valid two-dimensional capacity grid can fit the box.

    For an ``x_count``-by-``y_count`` grid, each closed cell has area
    ``1/(x_count*y_count) < 2*TARGET``.  Any three points in one cell have
    triangle area at most half that area, below the strict target.  The
    capacity-two matching is an outer test: a point interval is allowed every
    closed cell it intersects, so failure proves that no strict improver lies
    in the whole spatial box.
    """

    for x_count, y_count in partitions:
        if x_count <= 0 or y_count <= 0 or Fraction(1, x_count * y_count) >= 2 * TARGET:
            raise ValueError("rectangle-capacity grid is too coarse for the proved target")
        candidates = tuple(
            tuple(
                x_cell * y_count + y_cell
                for x_cell in _strip_candidates(box.coordinate_bounds[f"x_{point}"], x_count)
                for y_cell in _strip_candidates(box.coordinate_bounds[f"y_{point}"], y_count)
            )
            for point in range(12)
        )
        if not _has_capacity_two_assignment(candidates, x_count * y_count):
            return False
    return True


def _widest_variable(bounds: Mapping[str, Interval], triangle: Triangle) -> str | None:
    """Prefer the widest coordinate that can change the bottleneck determinant.

    A point occurring in a triangle does not make both of its coordinates
    relevant.  For example, for the left-chord triangle ``(0, 4, i)``, the
    coefficient of ``y_i`` is ``x_0-x_4 = 0``.  Splitting that coordinate only
    wastes an exact branch node.  An interval coefficient is identically zero
    exactly when its two opposing coordinate intervals are the same singleton;
    otherwise it can vary somewhere in the current outer box and remains a
    valid split candidate.
    """

    candidates = []
    for position, index in enumerate(triangle):
        other = triangle[(position + 1) % 3], triangle[(position + 2) % 3]
        x_name, y_name = f"x_{index}", f"y_{index}"
        y_left, y_right = bounds[f"y_{other[0]}"], bounds[f"y_{other[1]}"]
        x_left, x_right = bounds[f"x_{other[0]}"], bounds[f"x_{other[1]}"]
        if (
            bounds[x_name][0] < bounds[x_name][1]
            and not (y_left[0] == y_left[1] == y_right[0] == y_right[1])
        ):
            candidates.append(x_name)
        if (
            bounds[y_name][0] < bounds[y_name][1]
            and not (x_left[0] == x_left[1] == x_right[0] == x_right[1])
        ):
            candidates.append(y_name)
    candidates = tuple(candidates)
    if not candidates:
        candidates = tuple(variable for variable, interval in bounds.items() if interval[0] < interval[1])
    return max(candidates, key=lambda variable: bounds[variable][1] - bounds[variable][0], default=None)


def root_covers_canonical_incumbent() -> bool:
    """Check the exact record lies inside the target-tightened root box."""

    bounds = target_root_spatial_box().coordinate_bounds
    for index, point in enumerate(canonical_incumbent_points()):
        for axis, coordinate in zip(("x", "y"), point):
            lower, upper = bounds[f"{axis}_{index}"]
            if sign(coordinate - Qx.rational(lower)) < 0 or sign(Qx.rational(upper) - coordinate) < 0:
                return False
    return True


def target_root_spatial_box() -> SpatialBox:
    """Return the normal-form root restricted only by valid target consequences.

    Points 0 and 4 occupy both slots in the first vertical ``1/16`` strip of
    any configuration whose minimum area exceeds the record.  Applying this
    bound at the root is therefore a safe global reduction for the strict
    improvement question; it does not assume the unknown optimizer resembles
    the incumbent beyond the published normal form.
    """

    root = root_spatial_box(12)
    return SpatialBox(target_tightened_coordinate_bounds(12, root.coordinate_bounds, TARGET), root.depth)


def target_propagated_box(box: SpatialBox) -> SpatialBox | None:
    """Re-propagate every exact target difference constraint after a split.

    A child may fix one coordinate tightly enough to force further order or
    packing bounds on other coordinates.  This exact fixed-point propagation
    costs little compared with a determinant hull and can also prove a child
    empty immediately.  Returning ``None`` is therefore a sound prune, never
    a numerical heuristic.
    """

    try:
        bounds = target_tightened_coordinate_bounds(12, box.coordinate_bounds, TARGET)
    except ValueError:
        return None
    return SpatialBox(bounds, box.depth)


def split_target_spatial_box(
    box: SpatialBox,
    variable: str,
    *,
    split_strategy: str = "midpoint",
) -> Tuple[SpatialBox, ...]:
    """Split by a selected exact policy, then propagate target-feasible children.

    ``midpoint`` is the baseline geometry-first policy.  ``capacity`` splits
    at the nearest strip-partition boundary when possible, rapidly turning
    broad membership intervals into exact capacity cells.  Both children are
    closed and meet at the split, so either policy remains an exact cover.
    """

    if variable not in box.coordinate_bounds:
        raise KeyError(f"unknown coordinate {variable!r}")
    lower, upper = box.coordinate_bounds[variable]
    if lower >= upper:
        raise ValueError(f"cannot split fixed coordinate {variable!r}")
    midpoint = (lower + upper) / 2
    if split_strategy == "midpoint":
        split = midpoint
    elif split_strategy == "capacity":
        candidates = tuple(boundary for boundary in CAPACITY_SPLIT_BOUNDARIES if lower < boundary < upper)
        split = min(candidates, key=lambda boundary: abs(boundary - midpoint)) if candidates else midpoint
    else:
        raise ValueError("split strategy must be 'midpoint' or 'capacity'")
    left_bounds = dict(box.coordinate_bounds)
    right_bounds = dict(box.coordinate_bounds)
    left_bounds[variable] = (lower, split)
    right_bounds[variable] = (split, upper)

    children = []
    for raw_child in (SpatialBox(left_bounds, box.depth + 1), SpatialBox(right_bounds, box.depth + 1)):
        propagated = target_propagated_box(raw_child)
        if propagated is not None:
            children.append(propagated)
    return tuple(children)


def explore(
    *,
    max_boxes: int | None = 1000,
    split_strategy: str = "midpoint",
    queue_policy: str = "breadth",
    anchor_propagation: str = "off",
    anchor_passes: int = 1,
) -> Exploration:
    """Explore a global cover; only ``complete=True`` proves the no-go result.

    A fully pinned box whose exact minimum exceeds the record is surfaced as a
    strict-improvement witness rather than being hidden among unfinished work.

    ``breadth`` is the default diagnostic policy: it distributes the first
    finite budget across the global cover.  ``depth`` instead always chooses a
    deepest pending child, breaking equal-depth/equal-bound ties toward the
    most recently generated child.  It can reach the exact triangle and
    capacity prunes that only fire on narrow boxes much sooner.  Queue order
    changes neither a child, a prune predicate, nor the meaning of a completed
    cover.
    """

    if max_boxes is not None and max_boxes <= 0:
        raise ValueError("max_boxes must be positive when supplied")
    if queue_policy not in ("breadth", "depth"):
        raise ValueError("queue_policy must be 'breadth' or 'depth'")
    if anchor_propagation not in ("off", "anchored", "all"):
        raise ValueError("anchor_propagation must be 'off', 'anchored', or 'all'")
    if not root_covers_canonical_incumbent():
        raise AssertionError("the global root does not cover the canonical record")

    def queue_key(box: SpatialBox, upper: Fraction, order: int) -> tuple[int, Fraction, int]:
        if queue_policy == "breadth":
            return box.depth, -upper, order
        # Negative depth is a min-heap encoding of a depth-first stack.  The
        # negative generation order is the deterministic LIFO tie-breaker.
        return -box.depth, -upper, -order

    counter = 0
    root = target_root_spatial_box()
    root_upper, root_witness = minimum_area_upper(root)
    # The default breadth policy comes before the numerical bound.  A pure
    # best-first queue can repeatedly chase one loose branch forever when its
    # vertex hull stays at 1/2, producing a misleadingly deep finite campaign;
    # that focused behavior is available only through the explicit depth mode.
    root_key = queue_key(root, root_upper, counter)
    pending_heap: list[tuple[int, Fraction, int, SpatialBox, Triangle]] = [(*root_key, root, root_witness)]
    discarded: list[DiscardedBox] = []
    strict_improvements: list[StrictImprovementWitness] = []
    visited = 0
    maximum_depth = 0
    anchor_trim_records: list[AnchorTrim] = []
    while pending_heap and (max_boxes is None or visited < max_boxes):
        _, negative_upper, _, box, witness = heapq.heappop(pending_heap)
        upper = -negative_upper
        visited += 1
        maximum_depth = max(maximum_depth, box.depth)
        if not rectangle_capacity_feasible(box):
            discarded.append(DiscardedBox(box, "rectangle-capacity", None, upper))
            continue
        if not strip_capacity_feasible(box):
            discarded.append(DiscardedBox(box, "strip-capacity", None, upper))
            continue
        if cannot_strictly_beat_incumbent(upper):
            discarded.append(DiscardedBox(box, "triangle-upper", witness, upper))
            continue
        if anchor_propagation != "off":
            propagation = anchor_triangle_propagated_box(
                box, scope=anchor_propagation, passes=anchor_passes
            )
            anchor_trim_records.extend(propagation.trims)
            if propagation.box is None:
                # The recorded upper is the certificate: the named triangle's
                # exact area supremum on the residual box, at most TARGET —
                # not the box's (typically larger) minimum-area upper bound.
                discarded.append(
                    DiscardedBox(
                        box,
                        "anchor-triangle",
                        propagation.prune_triangle,
                        propagation.prune_supremum / 2,
                    )
                )
                continue
            if propagation.trims:
                box = propagation.box
                upper, witness = minimum_area_upper(box)
                if cannot_strictly_beat_incumbent(upper):
                    discarded.append(DiscardedBox(box, "triangle-upper", witness, upper))
                    continue
        variable = _widest_variable(box.coordinate_bounds, witness)
        if variable is None:
            # Every coordinate is exact, so the vertex-hull upper is the
            # actual geometric minimum.  The earlier prune established that
            # it strictly exceeds the algebraic incumbent.
            strict_improvements.append(StrictImprovementWitness(box, upper, witness))
            continue
        for child in split_target_spatial_box(box, variable, split_strategy=split_strategy):
            child_upper, child_witness = minimum_area_upper(child)
            counter += 1
            heapq.heappush(
                pending_heap,
                (*queue_key(child, child_upper, counter), child, child_witness),
            )

    pending = tuple(entry[3] for entry in pending_heap)
    largest = max((-entry[1] for entry in pending_heap), default=None)
    return Exploration(
        visited_boxes=visited,
        discarded_boxes=len(discarded),
        pending_boxes=len(pending),
        maximum_depth=maximum_depth,
        complete=not pending and not strict_improvements,
        largest_pending_upper=largest,
        discarded=tuple(discarded),
        pending=pending,
        strict_improvements=tuple(strict_improvements),
        anchor_trims=len(anchor_trim_records),
        anchor_trim_records=tuple(anchor_trim_records),
    )


def decimal(value: Fraction, digits: int = 24) -> str:
    """Render an exact rational with a controlled decimal precision."""

    from decimal import Decimal, localcontext

    with localcontext() as context:
        context.prec = digits + 8
        return format(Decimal(value.numerator) / Decimal(value.denominator), f".{digits}f")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-boxes", type=int, default=1000, help="finite budget; use 0 only for an unbounded full cover")
    parser.add_argument("--split-strategy", choices=("midpoint", "capacity"), default="midpoint")
    parser.add_argument(
        "--queue-policy",
        choices=("breadth", "depth"),
        default="breadth",
        help="finite-budget traversal only; either policy has the same exact completed-cover semantics",
    )
    parser.add_argument(
        "--anchor-propagation",
        choices=("off", "anchored", "all"),
        default="off",
        help="exact one-sided |det| > 2*TARGET interval propagation per visited box",
    )
    parser.add_argument(
        "--anchor-passes",
        type=int,
        default=1,
        help="fixed number of propagation sweeps per visited box; any prefix is exact",
    )
    arguments = parser.parse_args()
    result = explore(
        max_boxes=None if arguments.max_boxes == 0 else arguments.max_boxes,
        split_strategy=arguments.split_strategy,
        queue_policy=arguments.queue_policy,
        anchor_propagation=arguments.anchor_propagation,
        anchor_passes=arguments.anchor_passes,
    )
    print("visited_boxes", result.visited_boxes)
    print("discarded_boxes", result.discarded_boxes)
    print("pending_boxes", result.pending_boxes)
    print("maximum_depth", result.maximum_depth)
    print("anchor_trims", result.anchor_trims)
    print("largest_pending_upper", None if result.largest_pending_upper is None else decimal(result.largest_pending_upper))
    print("strict_improvement_witnesses", len(result.strict_improvements))
    print("complete", result.complete)
    reason_counts = {
        reason: sum(discarded.reason == reason for discarded in result.discarded)
        for reason in sorted({discarded.reason for discarded in result.discarded})
    }
    print("discard_reasons", reason_counts)
    if result.strict_improvements:
        for witness in result.strict_improvements:
            print("status", "STRICT_IMPROVEMENT_WITNESS: exact rational configuration found")
            print("witness_minimum_area", decimal(witness.minimum_area))
            print("witness_minimum_triangle", witness.minimum_triangle)
    elif not result.complete:
        print("status", "INCOMPLETE: no global no-go claim")


if __name__ == "__main__":
    main()
