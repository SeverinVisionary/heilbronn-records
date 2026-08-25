"""Exact Bernstein interval search for the full three-orbit C4 family.

Every nondegenerate 12-point configuration invariant under a quarter turn of
the unit square is three four-point C4 orbits.  An orbit has a representative
in the closed south-east quadrant ``[1/2, 1] x [0, 1/2]``; sorting the three
representatives by their first coordinate is only a relabelling.  Thus the
six-parameter root box below covers the entire three-orbit C4 family, including
the Comellas--Yebra record, without imposing a reflection symmetry.

For a parameter box, each signed triangle determinant is expanded exactly as
a polynomial and converted to tensor-product Bernstein form.  The Bernstein
convex-hull property gives a rigorous upper bound on its absolute value.
Boxes can also be pruned by ``Fraction``-exact necessary target consequences
of named triangles (and by canonical orbit ordering); those paths retain every
configuration whose least triangle area strictly exceeds the target.  NumPy is
used only to choose a likely triangle and split coordinate; floating-point
estimates never discard a box or establish a bracket.

Completing a finite cover proves an epsilon bracket *within this C4 family*.
It is not a theorem about arbitrary 12-point configurations, and a target
slightly above the algebraic record deliberately does not by itself rule out
an improvement smaller than that slack.
"""

from __future__ import annotations

import argparse
import heapq
from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations, product
from math import comb
from typing import Mapping, Sequence, Tuple

import numpy as np

from global_interval_branch import CAPACITY_SPLIT_BOUNDARIES, strip_capacity_feasible
from global_mccormick_relaxation import SpatialBox
from incumbent import Qx, algebraic_bounds, incumbent_points, incumbent_value, sign


Interval = Tuple[Fraction, Fraction]
Triangle = Tuple[int, int, int]
Exponent = Tuple[int, int, int, int, int, int]
Polynomial = Mapping[Exponent, Fraction]
PARAMETER_COUNT = 6
TRIANGLES: Tuple[Triangle, ...] = tuple(combinations(range(12), 3))
TRIANGLE_INDEX = {triangle: index for index, triangle in enumerate(TRIANGLES)}
ZERO_EXPONENT: Exponent = (0,) * PARAMETER_COUNT
HALF = Fraction(1, 2)


def _rotate_triangle(triangle: Triangle) -> Triangle:
    """Rotate each labelled C4-orbit position by one quarter turn."""

    return tuple(sorted(4 * (index // 4) + (index + 1) % 4 for index in triangle))


def _triangle_c4_orbit(triangle: Triangle) -> Tuple[Triangle, ...]:
    """Return the four equal-area triples in one quarter-turn orbit."""

    orbit = []
    current = triangle
    while current not in orbit:
        orbit.append(current)
        current = _rotate_triangle(current)
    if current != triangle or len(orbit) != 4:
        raise AssertionError("a three-point C4 triangle orbit must have length four")
    return tuple(sorted(orbit))


def _triangle_c4_orbits() -> Tuple[Tuple[Triangle, ...], ...]:
    remaining = set(TRIANGLES)
    orbits = []
    while remaining:
        orbit = _triangle_c4_orbit(min(remaining))
        if not set(orbit) <= remaining:
            raise AssertionError("C4 triangle orbit partition overlaps unexpectedly")
        remaining -= set(orbit)
        orbits.append(orbit)
    return tuple(orbits)


TRIANGLE_C4_ORBITS = _triangle_c4_orbits()
REPRESENTATIVE_TRIANGLES: Tuple[Triangle, ...] = tuple(orbit[0] for orbit in TRIANGLE_C4_ORBITS)
REPRESENTATIVE_INDEX = {triangle: index for index, triangle in enumerate(REPRESENTATIVE_TRIANGLES)}
if len(TRIANGLE_C4_ORBITS) != 55 or any(len(orbit) != 4 for orbit in TRIANGLE_C4_ORBITS):
    raise AssertionError("the 220 labelled triples must split into 55 C4 orbits")


@dataclass(frozen=True)
class Box:
    """A six-parameter C4 box in canonical representative coordinates."""

    parameters: Tuple[Interval, ...]
    depth: int = 0


@dataclass(frozen=True)
class DiscardedBox:
    """One exact discard reason and its optional geometric witness."""

    box: Box
    reason: str
    triangle: Triangle | None
    upper: Fraction | None


@dataclass(frozen=True)
class StrictImprovementWitness:
    """A fully pinned rational C4 configuration above the algebraic record."""

    box: Box
    minimum_area: Fraction
    minimum_triangle: Triangle


@dataclass(frozen=True)
class Exploration:
    """Replayable state of a finite or complete C4 epsilon-bracket cover."""

    target_upper: Fraction
    record_lower: Fraction
    record_upper: Fraction
    slack: Fraction
    visited_boxes: int
    discarded_boxes: int
    pending_boxes: int
    maximum_depth: int
    complete: bool
    smallest_pending_heuristic_upper: float | None
    discarded: Tuple[DiscardedBox, ...]
    pending: Tuple[Box, ...]
    strict_improvements: Tuple[StrictImprovementWitness, ...]


@dataclass(frozen=True)
class TargetPropagation:
    """One exact target-propagation result and its optional discard witness."""

    box: Box | None
    reason: str | None = None
    triangle: Triangle | None = None
    upper: Fraction | None = None


def _clean(polynomial: dict[Exponent, Fraction]) -> dict[Exponent, Fraction]:
    return {exponent: coefficient for exponent, coefficient in polynomial.items() if coefficient}


def _add(left: Polynomial, right: Polynomial, right_factor: Fraction = Fraction(1)) -> dict[Exponent, Fraction]:
    result = dict(left)
    for exponent, coefficient in right.items():
        result[exponent] = result.get(exponent, Fraction(0)) + right_factor * coefficient
    return _clean(result)


def _subtract(left: Polynomial, right: Polynomial) -> dict[Exponent, Fraction]:
    return _add(left, right, Fraction(-1))


def _multiply(left: Polynomial, right: Polynomial) -> dict[Exponent, Fraction]:
    result: dict[Exponent, Fraction] = {}
    for left_exponent, left_coefficient in left.items():
        for right_exponent, right_coefficient in right.items():
            exponent = tuple(
                left_degree + right_degree
                for left_degree, right_degree in zip(left_exponent, right_exponent)
            )
            result[exponent] = result.get(exponent, Fraction(0)) + left_coefficient * right_coefficient
    return _clean(result)


def _affine(constant: Fraction | int, parameter: int | None = None, coefficient: Fraction | int = 1) -> dict[Exponent, Fraction]:
    result = {ZERO_EXPONENT: Fraction(constant)}
    if parameter is not None:
        if not 0 <= parameter < PARAMETER_COUNT:
            raise ValueError("parameter index out of range")
        exponent = list(ZERO_EXPONENT)
        exponent[parameter] = 1
        result[tuple(exponent)] = Fraction(coefficient)
    return _clean(result)


def _orbit_point_polynomials(orbit: int, position: int) -> Tuple[Polynomial, Polynomial]:
    """Return one orbit point as affine polynomial coordinate pairs."""

    if not 0 <= orbit < 3 or not 0 <= position < 4:
        raise ValueError("invalid C4 orbit point")
    horizontal = 2 * orbit
    vertical = horizontal + 1
    if position == 0:
        return _affine(0, horizontal), _affine(0, vertical)
    if position == 1:
        return _affine(1, vertical, -1), _affine(0, horizontal)
    if position == 2:
        return _affine(1, horizontal, -1), _affine(1, vertical, -1)
    return _affine(0, vertical), _affine(1, horizontal, -1)


POINT_POLYNOMIALS: Tuple[Tuple[Polynomial, Polynomial], ...] = tuple(
    _orbit_point_polynomials(orbit, position) for orbit in range(3) for position in range(4)
)


def determinant_polynomial(triangle: Triangle) -> dict[Exponent, Fraction]:
    """Expand a signed double-area determinant in the six C4 parameters."""

    first, second, third = triangle
    x_first, y_first = POINT_POLYNOMIALS[first]
    x_second, y_second = POINT_POLYNOMIALS[second]
    x_third, y_third = POINT_POLYNOMIALS[third]
    return _subtract(
        _multiply(_subtract(x_second, x_first), _subtract(y_third, y_first)),
        _multiply(_subtract(y_second, y_first), _subtract(x_third, x_first)),
    )


DETERMINANT_POLYNOMIALS: Tuple[Polynomial, ...] = tuple(determinant_polynomial(triangle) for triangle in TRIANGLES)
POLYNOMIAL_DEGREES: Tuple[Exponent, ...] = tuple(
    tuple(max(exponent[parameter] for exponent in polynomial) for parameter in range(PARAMETER_COUNT))
    for polynomial in DETERMINANT_POLYNOMIALS
)
if any(any(degree > 2 for degree in degrees) for degrees in POLYNOMIAL_DEGREES):
    raise AssertionError("C4 triangle determinant unexpectedly exceeds degree two")


INTRA_ORBIT_TRIANGLES: Tuple[Triangle, ...] = ((0, 1, 2), (4, 5, 6), (8, 9, 10))
INTRA_ORBIT_TRIANGLE_TO_INDEX = {triangle: orbit for orbit, triangle in enumerate(INTRA_ORBIT_TRIANGLES)}


def root_box() -> Box:
    """Return the canonical six-dimensional C4 root box.

    Even parameters are south-east representative horizontal coordinates and
    odd parameters are vertical coordinates.  The three horizontal values are
    sorted so orbit names do not create six duplicate copies of the same set.
    """

    return Box(
        tuple((HALF, Fraction(1)) if parameter % 2 == 0 else (Fraction(0), HALF) for parameter in range(PARAMETER_COUNT))
    )


def _one_minus(interval: Interval) -> Interval:
    return Fraction(1) - interval[1], Fraction(1) - interval[0]


def point_coordinate_bounds(box: Box) -> Tuple[Tuple[Interval, Interval], ...]:
    """Return a rigorous coordinate outer box for the twelve C4 points."""

    if len(box.parameters) != PARAMETER_COUNT:
        raise ValueError("C4 boxes require six parameters")
    points = []
    for orbit in range(3):
        horizontal = box.parameters[2 * orbit]
        vertical = box.parameters[2 * orbit + 1]
        points.extend(
            (
                (horizontal, vertical),
                (_one_minus(vertical), horizontal),
                (_one_minus(horizontal), _one_minus(vertical)),
                (vertical, _one_minus(horizontal)),
            )
        )
    return tuple(points)


def spatial_box(box: Box) -> SpatialBox:
    """Embed a C4 parameter box into coordinate intervals for safe grid cuts."""

    return SpatialBox(
        {
            f"{axis}_{index}": interval
            for index, point in enumerate(point_coordinate_bounds(box))
            for axis, interval in zip(("x", "y"), point)
        },
        box.depth,
    )


def _ordered_box(box: Box) -> Box | None:
    """Propagate the harmless representative ordering ``a0 <= a1 <= a2``."""

    if len(box.parameters) != PARAMETER_COUNT:
        raise ValueError("C4 boxes require six parameters")
    parameters = list(box.parameters)
    while True:
        changed = False
        for left, right in zip((0, 2), (2, 4)):
            left_lower, left_upper = parameters[left]
            right_lower, right_upper = parameters[right]
            tightened_right = (max(right_lower, left_lower), right_upper)
            tightened_left = (left_lower, min(left_upper, right_upper))
            if tightened_right != parameters[right]:
                parameters[right] = tightened_right
                changed = True
            if tightened_left != parameters[left]:
                parameters[left] = tightened_left
                changed = True
        if not changed:
            break
    if any(lower > upper for lower, upper in parameters):
        return None
    return Box(tuple(parameters), box.depth)


def _sqrt_lower(value: Fraction, bits: int = 32) -> Fraction:
    """Return a dyadic lower bound on a nonnegative rational square root."""

    if value < 0 or bits <= 0:
        raise ValueError("square-root lower bound requires a nonnegative value and positive precision")
    lower, upper = Fraction(0), Fraction(1)
    while upper * upper < value:
        upper *= 2
    for _ in range(bits):
        midpoint = (lower + upper) / 2
        if midpoint * midpoint <= value:
            lower = midpoint
        else:
            upper = midpoint
    return lower


def _seed_triangle_rectangle_upper(parameters: Sequence[Interval]) -> Fraction:
    """Bound triangle ``(0, 4, 8)`` by its south-east seed rectangle."""

    horizontal_lower = parameters[0][0]
    horizontal_upper = parameters[4][1]
    vertical_lower = min(parameters[index][0] for index in (1, 3, 5))
    vertical_upper = max(parameters[index][1] for index in (1, 3, 5))
    return (horizontal_upper - horizontal_lower) * (vertical_upper - vertical_lower) / 2


def _target_propagation(box: Box, target: Fraction, *, sqrt_bits: int = 32) -> TargetPropagation:
    """Propagate each orbit's exact own-triangle area requirement.

    Every three consecutive points of orbit ``q`` form a triangle of area
    ``(a_q-1/2)^2 + (1/2-b_q)^2``.  Therefore any configuration that could
    violate an upper target must make every such value strictly greater than
    ``target``.  A rational lower square-root enclosure makes this a safe
    one-sided box tightening; it can retain extra values near the circle but
    never discard a strict target violator.
    """

    if target <= 0 or sqrt_bits <= 0:
        raise ValueError("target propagation requires a positive target and precision")
    parameters = list(box.parameters)
    while True:
        ordered = _ordered_box(Box(tuple(parameters), box.depth))
        if ordered is None:
            return TargetPropagation(None, "orbit-ordering")
        parameters = list(ordered.parameters)
        before = tuple(parameters)
        for orbit in range(3):
            horizontal_lower, horizontal_upper = parameters[2 * orbit]
            vertical_lower, vertical_upper = parameters[2 * orbit + 1]
            if horizontal_lower < HALF or vertical_upper > HALF:
                raise ValueError("box left the canonical C4 representative sector")
            maximum_u = horizontal_upper - HALF
            maximum_v = HALF - vertical_lower
            orbit_upper = maximum_u * maximum_u + maximum_v * maximum_v
            if orbit_upper <= target:
                return TargetPropagation(None, "orbit-triangle", INTRA_ORBIT_TRIANGLES[orbit], orbit_upper)

            needed_u_squared = target - maximum_v * maximum_v
            if needed_u_squared > 0:
                horizontal_lower = max(horizontal_lower, HALF + _sqrt_lower(needed_u_squared, sqrt_bits))

            needed_v_squared = target - maximum_u * maximum_u
            if needed_v_squared > 0:
                vertical_upper = min(vertical_upper, HALF - _sqrt_lower(needed_v_squared, sqrt_bits))

            if horizontal_lower > horizontal_upper or vertical_lower > vertical_upper:
                return TargetPropagation(None, "orbit-triangle", INTRA_ORBIT_TRIANGLES[orbit], orbit_upper)
            parameters[2 * orbit] = (horizontal_lower, horizontal_upper)
            parameters[2 * orbit + 1] = (vertical_lower, vertical_upper)

        # The three south-east representatives are points 0, 4, and 8.  Their
        # triangle lies in an axis-aligned rectangle whose horizontal extent
        # is a2-a0 because the representatives are ordered.  A triangle in a
        # W-by-H rectangle has area at most W*H/2.  This gives an exact target
        # span consequence without choosing a determinant sign.
        rectangle_upper = _seed_triangle_rectangle_upper(parameters)
        if rectangle_upper <= target:
            return TargetPropagation(None, "seed-triangle-rectangle", (0, 4, 8), rectangle_upper)
        vertical_range_upper = max(parameters[index][1] for index in (1, 3, 5)) - min(
            parameters[index][0] for index in (1, 3, 5)
        )
        if vertical_range_upper <= 0:
            raise AssertionError("positive seed-triangle rectangle bound requires positive vertical span")
        required_horizontal_span = 2 * target / vertical_range_upper
        first_lower, first_upper = parameters[0]
        third_lower, third_upper = parameters[4]
        parameters[0] = (first_lower, min(first_upper, third_upper - required_horizontal_span))
        parameters[4] = (max(third_lower, first_lower + required_horizontal_span), third_upper)
        if parameters[0][0] > parameters[0][1] or parameters[4][0] > parameters[4][1]:
            return TargetPropagation(None, "seed-triangle-rectangle", (0, 4, 8), rectangle_upper)
        if tuple(parameters) == before:
            return TargetPropagation(Box(tuple(parameters), box.depth))


def target_propagated_box(box: Box, target: Fraction, *, sqrt_bits: int = 32) -> Box | None:
    """Return the target-tightened box, or ``None`` after an exact prune."""

    return _target_propagation(box, target, sqrt_bits=sqrt_bits).box


def _is_pinned(box: Box) -> bool:
    return all(lower == upper for lower, upper in box.parameters)


def _affine_power_terms(lower: Fraction, width: Fraction, power: int) -> Mapping[int, Fraction]:
    """Expand ``(lower + width*t)**power`` for the degree-two determinants."""

    if power == 0:
        return {0: Fraction(1)}
    if power == 1:
        return {0: lower, 1: width}
    if power == 2:
        return {0: lower * lower, 1: 2 * lower * width, 2: width * width}
    raise AssertionError("determinant degree should be at most two")


def _substitute_box(polynomial: Polynomial, box: Box) -> dict[Exponent, Fraction]:
    """Express a determinant polynomial in unit-box power coordinates."""

    result: dict[Exponent, Fraction] = {}
    for exponent, coefficient in polynomial.items():
        partial: dict[Exponent, Fraction] = {ZERO_EXPONENT: coefficient}
        for parameter, power in enumerate(exponent):
            lower, upper = box.parameters[parameter]
            terms = _affine_power_terms(lower, upper - lower, power)
            expanded: dict[Exponent, Fraction] = {}
            for partial_exponent, partial_coefficient in partial.items():
                for extra_degree, extra_coefficient in terms.items():
                    next_exponent = list(partial_exponent)
                    next_exponent[parameter] += extra_degree
                    key = tuple(next_exponent)
                    expanded[key] = expanded.get(key, Fraction(0)) + partial_coefficient * extra_coefficient
            partial = _clean(expanded)
        result = _add(result, partial)
    return result


def _bernstein_upper(polynomial: Polynomial, degrees: Exponent, box: Box) -> Fraction:
    """Return an exact Bernstein-hull bound on one absolute determinant."""

    power_coefficients = _substitute_box(polynomial, box)
    maximum = Fraction(0)
    for beta in product(*(range(degree + 1) for degree in degrees)):
        coefficient = Fraction(0)
        for alpha, power_coefficient in power_coefficients.items():
            if any(alpha_degree > beta_degree for alpha_degree, beta_degree in zip(alpha, beta)):
                continue
            conversion = Fraction(1)
            for alpha_degree, beta_degree, degree in zip(alpha, beta, degrees):
                conversion *= Fraction(comb(beta_degree, alpha_degree), comb(degree, alpha_degree))
            coefficient += power_coefficient * conversion
        maximum = max(maximum, abs(coefficient))
    return maximum


def double_area_bernstein_upper(box: Box, triangle: Triangle) -> Fraction:
    """Return a rigorous exact upper bound on one absolute double area."""

    index = TRIANGLE_INDEX[triangle]
    return _bernstein_upper(DETERMINANT_POLYNOMIALS[index], POLYNOMIAL_DEGREES[index], box)


def evaluate_determinant(parameters: Sequence[Fraction], triangle: Triangle) -> Fraction:
    """Evaluate one signed double area exactly at a rational C4 parameter point."""

    if len(parameters) != PARAMETER_COUNT:
        raise ValueError("C4 configurations require six parameters")
    polynomial = DETERMINANT_POLYNOMIALS[TRIANGLE_INDEX[triangle]]
    result = Fraction(0)
    for exponent, coefficient in polynomial.items():
        term = coefficient
        for value, degree in zip(parameters, exponent):
            term *= value**degree
        result += term
    return result


def orbit_triangle_upper(box: Box, orbit: int) -> Fraction:
    """Bound the exact area of any three consecutive points of one orbit.

    In the canonical south-east sector that area is
    ``(a-1/2)^2 + (b-1/2)^2``.  It is monotone in the relevant directions,
    so the south-east corner of the parameter rectangle is its exact maximum.
    """

    if not 0 <= orbit < 3:
        raise ValueError("orbit index out of range")
    horizontal_lower, horizontal_upper = box.parameters[2 * orbit]
    vertical_lower, vertical_upper = box.parameters[2 * orbit + 1]
    if horizontal_lower < HALF or vertical_upper > HALF:
        raise ValueError("box left the canonical C4 representative sector")
    return (horizontal_upper - HALF) ** 2 + (HALF - vertical_lower) ** 2


def area_upper_for_triangle(box: Box, triangle: Triangle) -> Fraction:
    """Return the strongest exact area bound currently available for a triple."""

    upper = double_area_bernstein_upper(box, triangle) / 2
    orbit = INTRA_ORBIT_TRIANGLE_TO_INDEX.get(triangle)
    if orbit is not None:
        upper = min(upper, orbit_triangle_upper(box, orbit))
    return upper


def minimum_area_upper(box: Box) -> Tuple[Fraction, Triangle]:
    """Return an exact C4-box upper bound on its least triangle area.

    Quarter turns preserve every ordinary triangle area, so evaluating one
    representative from each of the 55 triple orbits is enough.  This reduces
    exact work by four without replacing a bound by a numerical symmetry guess.
    """

    return min(
        ((area_upper_for_triangle(box, triangle), triangle) for triangle in REPRESENTATIVE_TRIANGLES),
        key=lambda candidate: candidate[0],
    )


def _float_power_coefficients() -> np.ndarray:
    result = np.zeros((len(REPRESENTATIVE_TRIANGLES),) + (3,) * PARAMETER_COUNT, dtype=float)
    for index, triangle in enumerate(REPRESENTATIVE_TRIANGLES):
        polynomial = DETERMINANT_POLYNOMIALS[TRIANGLE_INDEX[triangle]]
        for exponent, coefficient in polynomial.items():
            result[(index,) + exponent] = float(coefficient)
    return result


FLOAT_POWER_COEFFICIENTS = _float_power_coefficients()
# Rows are power degrees and columns are the new unit-box power degree.
FLOAT_BERNSTEIN_TRANSFORM = np.asarray(((1.0, 0.0, 0.0), (1.0, 0.5, 0.0), (1.0, 1.0, 1.0)))


def _float_affine_power_transform(lower: float, width: float) -> np.ndarray:
    return np.asarray(
        ((1.0, 0.0, 0.0), (lower, width, 0.0), (lower * lower, 2.0 * lower * width, width * width))
    )


def heuristic_area_uppers(box: Box) -> np.ndarray:
    """Return non-certifying float Bernstein bounds used only for scheduling.

    The exact conversion in :func:`double_area_bernstein_upper` is the sole
    source of pruning.  This batched version merely avoids spending exact
    rational work on all 220 triples before a likely bottleneck is known.
    """

    coefficients = FLOAT_POWER_COEFFICIENTS
    for parameter, (lower, upper) in enumerate(box.parameters):
        coefficients = np.moveaxis(coefficients, parameter + 1, -1) @ _float_affine_power_transform(
            float(lower), float(upper - lower)
        )
        coefficients = np.moveaxis(coefficients, -1, parameter + 1)
    for parameter in range(PARAMETER_COUNT):
        coefficients = np.moveaxis(coefficients, parameter + 1, -1) @ FLOAT_BERNSTEIN_TRANSFORM.T
        coefficients = np.moveaxis(coefficients, -1, parameter + 1)
    result = np.max(np.abs(coefficients), axis=tuple(range(1, PARAMETER_COUNT + 1))) / 2.0
    for triangle, orbit in INTRA_ORBIT_TRIANGLE_TO_INDEX.items():
        index = REPRESENTATIVE_INDEX[triangle]
        result[index] = min(result[index], float(orbit_triangle_upper(box, orbit)))
    return result


def _preferred_parameter(box: Box, triangle: Triangle) -> int | None:
    """Choose a widest currently relevant parameter for a non-certifying split."""

    polynomial = DETERMINANT_POLYNOMIALS[TRIANGLE_INDEX[triangle]]
    used = tuple(
        parameter
        for parameter in range(PARAMETER_COUNT)
        if any(exponent[parameter] for exponent in polynomial)
        and box.parameters[parameter][0] < box.parameters[parameter][1]
    )
    candidates = used or tuple(
        parameter
        for parameter, (lower, upper) in enumerate(box.parameters)
        if lower < upper
    )
    return max(candidates, key=lambda parameter: box.parameters[parameter][1] - box.parameters[parameter][0], default=None)


def split(box: Box, parameter: int, *, split_strategy: str = "midpoint") -> Tuple[Box, ...]:
    """Split one parameter and propagate canonical orbit ordering.

    ``capacity`` uses a nearest exact grid boundary whenever possible.  The
    global partitions are symmetric under ``v -> 1-v``, so a split of a C4
    representative also aligns its quarter-turn images with the same grids.
    Both strategies retain closed children and therefore cover the parent.
    """

    if not 0 <= parameter < PARAMETER_COUNT:
        raise ValueError("parameter index out of range")
    lower, upper = box.parameters[parameter]
    if lower >= upper:
        raise ValueError("cannot split a fixed parameter")
    midpoint = (lower + upper) / 2
    if split_strategy == "midpoint":
        split_point = midpoint
    elif split_strategy == "capacity":
        candidates = tuple(boundary for boundary in CAPACITY_SPLIT_BOUNDARIES if lower < boundary < upper)
        split_point = min(candidates, key=lambda boundary: abs(boundary - midpoint)) if candidates else midpoint
    else:
        raise ValueError("split strategy must be 'midpoint' or 'capacity'")
    result = []
    for interval in ((lower, split_point), (split_point, upper)):
        parameters = list(box.parameters)
        parameters[parameter] = interval
        child = _ordered_box(Box(tuple(parameters), box.depth + 1))
        if child is not None:
            result.append(child)
    return tuple(result)


def root_covers_canonical_incumbent() -> bool:
    """Verify the sorted C4 representatives of the exact record are covered."""

    x = incumbent_points()[0][0]
    y = incumbent_points()[8][1]
    parameters = (Qx.rational(HALF), y, Qx.rational(1) - x, Qx.rational(0), Qx.rational(1), x)
    root = root_box()
    if _ordered_box(root) != root:
        raise AssertionError("root ordering propagation should leave the root unchanged")
    for value, (lower, upper) in zip(parameters, root.parameters):
        if sign(value - Qx.rational(lower)) < 0 or sign(Qx.rational(upper) - value) < 0:
            return False
    return sign(parameters[0] - parameters[2]) <= 0 and sign(parameters[2] - parameters[4]) <= 0


def _cannot_exceed_target(upper: Fraction, target: Fraction) -> bool:
    return upper <= target


def _strictly_beats_incumbent(area: Fraction) -> bool:
    return sign(Qx.rational(area) - incumbent_value()) > 0


def _exact_target_prune(
    box: Box,
    heuristic: np.ndarray,
    target: Fraction,
    *,
    screen_margin: float = 1e-9,
) -> Tuple[Fraction, Triangle] | None:
    """Certify a likely float bottleneck exactly, or conservatively keep it.

    The margin can only cause extra exact work.  If it misses a useful cut,
    the branch is retained and remains sound; it never creates a false prune.
    """

    target_float = float(target)
    for index in np.argsort(heuristic):
        if heuristic[index] > target_float + screen_margin:
            break
        triangle = REPRESENTATIVE_TRIANGLES[int(index)]
        upper = area_upper_for_triangle(box, triangle)
        if _cannot_exceed_target(upper, target):
            return upper, triangle
    return None


def _pinned_minimum(box: Box) -> Tuple[Fraction, Triangle]:
    """Evaluate a degenerate rational box with the exact Bernstein path."""

    if not _is_pinned(box):
        raise ValueError("pinned minimum requested for a nondegenerate box")
    return minimum_area_upper(box)


def _queue_key(box: Box, heuristic: np.ndarray, counter: int, queue_strategy: str) -> tuple[float, float, int]:
    """Return a non-certifying queue key without changing the covered boxes."""

    smallest = float(np.min(heuristic))
    if queue_strategy == "breadth":
        return float(box.depth), smallest, counter
    if queue_strategy == "best-upper":
        return smallest, float(box.depth), counter
    raise ValueError("queue strategy must be 'breadth' or 'best-upper'")


def explore(
    *,
    slack_bits: int = 20,
    root_bisections: int = 128,
    max_boxes: int | None = 1000,
    split_strategy: str = "midpoint",
    queue_strategy: str = "breadth",
) -> Exploration:
    """Cover the C4 family up to ``record_upper + 2**-slack_bits``.

    Only ``complete=True`` establishes the stated C4 epsilon bracket.  It is
    deliberately not labelled a global no-improvement theorem.
    """

    if slack_bits <= 0 or root_bisections <= 0:
        raise ValueError("precision parameters must be positive")
    if max_boxes is not None and max_boxes <= 0:
        raise ValueError("max_boxes must be positive when supplied")
    if split_strategy not in ("midpoint", "capacity"):
        raise ValueError("split strategy must be 'midpoint' or 'capacity'")
    if queue_strategy not in ("breadth", "best-upper"):
        raise ValueError("queue strategy must be 'breadth' or 'best-upper'")
    if not root_covers_canonical_incumbent():
        raise AssertionError("C4 root failed to cover the canonical incumbent")

    record_lower, record_upper = algebraic_bounds(incumbent_value(), root_bisections)
    slack = Fraction(1, 2**slack_bits)
    target = record_upper + slack
    root_propagation = _target_propagation(root_box(), target)
    root = root_propagation.box
    if root is None:
        root_discarded = DiscardedBox(
            root_box(),
            root_propagation.reason or "target-propagation",
            root_propagation.triangle,
            root_propagation.upper,
        )
        return Exploration(
            target_upper=target,
            record_lower=record_lower,
            record_upper=record_upper,
            slack=slack,
            visited_boxes=0,
            discarded_boxes=1,
            pending_boxes=0,
            maximum_depth=0,
            complete=True,
            smallest_pending_heuristic_upper=None,
            discarded=(root_discarded,),
            pending=(),
            strict_improvements=(),
        )
    root_heuristic = heuristic_area_uppers(root)
    counter = 0
    root_key = _queue_key(root, root_heuristic, counter, queue_strategy)
    pending_heap: list[tuple[float, float, int, Box, np.ndarray]] = [(*root_key, root, root_heuristic)]
    discarded: list[DiscardedBox] = []
    strict_improvements: list[StrictImprovementWitness] = []
    visited = 0
    maximum_depth = 0

    while pending_heap and (max_boxes is None or visited < max_boxes):
        _, _, _, box, heuristic = heapq.heappop(pending_heap)
        visited += 1
        maximum_depth = max(maximum_depth, box.depth)

        if _is_pinned(box):
            exact_minimum, triangle = _pinned_minimum(box)
            if _strictly_beats_incumbent(exact_minimum):
                strict_improvements.append(StrictImprovementWitness(box, exact_minimum, triangle))
            else:
                discarded.append(DiscardedBox(box, "pinned-nonimprovement", triangle, exact_minimum))
            continue

        # This is a necessary condition only for a configuration whose least
        # area exceeds the record-plus-slack target: it then also exceeds
        # 1/31, the target used by the independently validated grid lemma.
        # The coordinate interval image is an outer box, so matching failure
        # safely discards the entire correlated C4 parameter box.
        if not strip_capacity_feasible(spatial_box(box)):
            discarded.append(DiscardedBox(box, "strip-capacity", None, None))
            continue

        exact_prune = _exact_target_prune(box, heuristic, target)
        if exact_prune is not None:
            upper, triangle = exact_prune
            discarded.append(DiscardedBox(box, "bernstein-target", triangle, upper))
            continue

        triangle = REPRESENTATIVE_TRIANGLES[int(np.argmin(heuristic))]
        parameter = _preferred_parameter(box, triangle)
        if parameter is None:
            raise AssertionError("non-pinned box has no available split")
        for raw_child in split(box, parameter, split_strategy=split_strategy):
            child_propagation = _target_propagation(raw_child, target)
            child = child_propagation.box
            if child is None:
                discarded.append(
                    DiscardedBox(
                        raw_child,
                        child_propagation.reason or "target-propagation",
                        child_propagation.triangle,
                        child_propagation.upper,
                    )
                )
                continue
            child_heuristic = heuristic_area_uppers(child)
            counter += 1
            heapq.heappush(
                pending_heap,
                (*_queue_key(child, child_heuristic, counter, queue_strategy), child, child_heuristic),
            )

    pending = tuple(entry[3] for entry in pending_heap)
    smallest_pending = min((entry[1] for entry in pending_heap), default=None)
    return Exploration(
        target_upper=target,
        record_lower=record_lower,
        record_upper=record_upper,
        slack=slack,
        visited_boxes=visited,
        discarded_boxes=len(discarded),
        pending_boxes=len(pending),
        maximum_depth=maximum_depth,
        complete=not pending and not strict_improvements,
        smallest_pending_heuristic_upper=smallest_pending,
        discarded=tuple(discarded),
        pending=pending,
        strict_improvements=tuple(strict_improvements),
    )


def decimal(value: Fraction, digits: int = 30) -> str:
    """Render one rational endpoint without losing its exact source value."""

    from decimal import Decimal, localcontext

    with localcontext() as context:
        context.prec = digits + 8
        return format(Decimal(value.numerator) / Decimal(value.denominator), f".{digits}f")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-boxes", type=int, default=1000, help="finite budget; use 0 only for an unbounded cover")
    parser.add_argument("--slack-bits", type=int, default=20)
    parser.add_argument("--root-bisections", type=int, default=128)
    parser.add_argument("--split-strategy", choices=("midpoint", "capacity"), default="midpoint")
    parser.add_argument("--queue-strategy", choices=("breadth", "best-upper"), default="breadth")
    arguments = parser.parse_args()
    result = explore(
        slack_bits=arguments.slack_bits,
        root_bisections=arguments.root_bisections,
        max_boxes=None if arguments.max_boxes == 0 else arguments.max_boxes,
        split_strategy=arguments.split_strategy,
        queue_strategy=arguments.queue_strategy,
    )
    print("record_lower", decimal(result.record_lower, 30))
    print("record_upper", decimal(result.record_upper, 30))
    print("target_upper", decimal(result.target_upper, 30))
    print("slack", result.slack)
    print("visited_boxes", result.visited_boxes)
    print("discarded_boxes", result.discarded_boxes)
    print("pending_boxes", result.pending_boxes)
    print("maximum_depth", result.maximum_depth)
    print("smallest_pending_heuristic_upper", result.smallest_pending_heuristic_upper)
    print("strict_improvement_witnesses", len(result.strict_improvements))
    print("complete", result.complete)
    reason_counts = {
        reason: sum(discarded.reason == reason for discarded in result.discarded)
        for reason in sorted({discarded.reason for discarded in result.discarded})
    }
    print("discard_reasons", reason_counts)
    if result.strict_improvements:
        for witness in result.strict_improvements:
            print("status", "STRICT_IMPROVEMENT_WITNESS: exact rational C4 configuration found")
            print("witness_minimum_area", decimal(witness.minimum_area))
            print("witness_minimum_triangle", witness.minimum_triangle)
    elif not result.complete:
        print("status", "INCOMPLETE: no C4 bracket claim")


if __name__ == "__main__":
    main()
