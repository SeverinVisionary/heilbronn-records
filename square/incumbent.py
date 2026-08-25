"""Exact arithmetic for the Comellas--Yebra 12-point square configuration.

The coordinates belong to Q(x), where x is the boundary coordinate satisfying
    4 x^3 - 12 x^2 + 10 x - 1 = 0.
Representing elements in the basis (1, x, x^2) keeps the published incumbent
and every one of its 220 triangle areas exact, without a CAS dependency.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from functools import cmp_to_key
from functools import lru_cache
from itertools import combinations
from typing import Callable, List, Sequence, Tuple


# x^3 = 1/4 - 5*x/2 + 3*x^2.
_X3 = (Fraction(1, 4), Fraction(-5, 2), Fraction(3))


@dataclass(frozen=True)
class Qx:
    """An element a0 + a1*x + a2*x^2 of Q(x)."""

    a0: Fraction = Fraction(0)
    a1: Fraction = Fraction(0)
    a2: Fraction = Fraction(0)

    @classmethod
    def rational(cls, value: Fraction | int) -> "Qx":
        return cls(Fraction(value))

    def __add__(self, other: "Qx | Fraction | int") -> "Qx":
        other = _as_qx(other)
        return Qx(self.a0 + other.a0, self.a1 + other.a1, self.a2 + other.a2)

    __radd__ = __add__

    def __neg__(self) -> "Qx":
        return Qx(-self.a0, -self.a1, -self.a2)

    def __sub__(self, other: "Qx | Fraction | int") -> "Qx":
        return self + (-_as_qx(other))

    def __rsub__(self, other: "Qx | Fraction | int") -> "Qx":
        return _as_qx(other) - self

    def __mul__(self, other: "Qx | Fraction | int") -> "Qx":
        other = _as_qx(other)
        product = [Fraction(0)] * 5
        left = (self.a0, self.a1, self.a2)
        right = (other.a0, other.a1, other.a2)
        for i, left_coefficient in enumerate(left):
            for j, right_coefficient in enumerate(right):
                product[i + j] += left_coefficient * right_coefficient

        # x^4 = 3/4 - 29*x/4 + 13*x^2/2, obtained from x*x^3.
        return Qx(
            product[0] + product[3] * _X3[0] + product[4] * Fraction(3, 4),
            product[1] + product[3] * _X3[1] - product[4] * Fraction(29, 4),
            product[2] + product[3] * _X3[2] + product[4] * Fraction(13, 2),
        )

    __rmul__ = __mul__

    def inverse(self) -> "Qx":
        """Return the multiplicative inverse in the cubic field."""
        if self.is_zero():
            raise ZeroDivisionError("zero has no inverse in Q(x)")
        columns = (
            self,
            self * X,
            self * X * X,
        )
        matrix = tuple(
            tuple((column.a0, column.a1, column.a2)[index] for column in columns)
            for index in range(3)
        )
        determinant = _fraction_det3(matrix)
        if determinant == 0:
            raise AssertionError("nonzero field element produced singular multiplication map")
        rhs = (Fraction(1), Fraction(0), Fraction(0))
        solution = []
        for target_column in range(3):
            replaced = tuple(
                tuple(rhs[row] if column == target_column else matrix[row][column] for column in range(3))
                for row in range(3)
            )
            solution.append(_fraction_det3(replaced) / determinant)
        return Qx(*solution)

    def __truediv__(self, other: "Qx | Fraction | int") -> "Qx":
        return self * _as_qx(other).inverse()

    def __rtruediv__(self, other: "Qx | Fraction | int") -> "Qx":
        return _as_qx(other) * self.inverse()

    def is_zero(self) -> bool:
        return self.a0 == self.a1 == self.a2 == 0


def _as_qx(value: Qx | Fraction | int) -> Qx:
    return value if isinstance(value, Qx) else Qx.rational(value)


def _fraction_det3(rows: Sequence[Sequence[Fraction]]) -> Fraction:
    return (
        rows[0][0] * (rows[1][1] * rows[2][2] - rows[1][2] * rows[2][1])
        - rows[0][1] * (rows[1][0] * rows[2][2] - rows[1][2] * rows[2][0])
        + rows[0][2] * (rows[1][0] * rows[2][1] - rows[1][1] * rows[2][0])
    )


X = Qx(Fraction(0), Fraction(1), Fraction(0))
ZERO = Qx.rational(0)
ONE = Qx.rational(1)
HALF = Qx.rational(Fraction(1, 2))


def cubic(value: Fraction) -> Fraction:
    """The defining polynomial of the boundary coordinate x, exactly."""
    return 4 * value**3 - 12 * value**2 + 10 * value - 1


@lru_cache(maxsize=None)
def root_bounds(bisections: int = 256) -> Tuple[Fraction, Fraction]:
    """Return a rational isolating interval for the positive root x.

    The polynomial is strictly increasing on [0, 1/4], so bisection from this
    interval isolates the boundary-coordinate root with rational endpoints.
    """
    lower, upper = Fraction(0), Fraction(1, 4)
    if not cubic(lower) < 0 < cubic(upper):
        raise AssertionError("invalid initial interval for incumbent root")
    for _ in range(bisections):
        midpoint = (lower + upper) / 2
        if cubic(midpoint) < 0:
            lower = midpoint
        else:
            upper = midpoint
    return lower, upper


def _bounds(value: Qx, lower: Fraction, upper: Fraction) -> Tuple[Fraction, Fraction]:
    """Bound a0+a1*x+a2*x^2 on a positive interval for x."""
    lower_value = value.a0
    upper_value = value.a0
    for coefficient, lower_term, upper_term in (
        (value.a1, lower, upper),
        (value.a2, lower * lower, upper * upper),
    ):
        if coefficient >= 0:
            lower_value += coefficient * lower_term
            upper_value += coefficient * upper_term
        else:
            lower_value += coefficient * upper_term
            upper_value += coefficient * lower_term
    return lower_value, upper_value


def algebraic_bounds(value: Qx, bisections: int = 256) -> Tuple[Fraction, Fraction]:
    """Return a rational enclosure for an element of the incumbent field."""
    return _bounds(value, *root_bounds(bisections))


def sign(value: Qx) -> int:
    """Determine the exact sign of a Q(x) element using rational intervals."""
    if value.is_zero():
        return 0
    for bisections in range(32, 1025, 32):
        lower, upper = root_bounds(bisections)
        lower_value, upper_value = _bounds(value, lower, upper)
        if lower_value > 0:
            return 1
        if upper_value < 0:
            return -1
    raise ArithmeticError("unable to isolate sign; increase root precision")


def absolute(value: Qx) -> Qx:
    return value if sign(value) >= 0 else -value


def compare(left: Qx, right: Qx) -> int:
    """Compare two Q(x) elements exactly."""
    return sign(left - right)


Point = Tuple[Qx, Qx]
Triangle = Tuple[int, int, int]


def incumbent_points() -> Tuple[Point, ...]:
    """Published n=12 unit-square configuration, in a fixed labeled order."""
    x = X
    y = 2 * x * x - 3 * x + HALF
    return (
        (x, ZERO),
        (ONE - x, ZERO),
        (x, ONE),
        (ONE - x, ONE),
        (ZERO, x),
        (ONE, x),
        (ZERO, ONE - x),
        (ONE, ONE - x),
        (HALF, y),
        (y, HALF),
        (ONE - y, HALF),
        (HALF, ONE - y),
    )


def signed_double_area(points: Sequence[Point], triangle: Triangle) -> Qx:
    i, j, k = triangle
    xi, yi = points[i]
    xj, yj = points[j]
    xk, yk = points[k]
    return (xj - xi) * (yk - yi) - (yj - yi) * (xk - xi)


def triangle_areas(points: Sequence[Point]) -> List[Tuple[Triangle, Qx]]:
    """Return all exact unsigned areas in lexicographic triple order."""
    return [
        (triangle, absolute(signed_double_area(points, triangle)) * Fraction(1, 2))
        for triangle in combinations(range(len(points)), 3)
    ]


def incumbent_value() -> Qx:
    x = X
    y = 2 * x * x - 3 * x + HALF
    return x * Fraction(1, 4) + x * y * Fraction(1, 2) - x * x * Fraction(1, 2)


def record_cubic(value: Qx) -> Qx:
    """The cubic satisfied by the record *area* (not boundary coordinate)."""
    return 64 * value * value * value + 80 * value * value + 28 * value - ONE


def incumbent_analysis() -> Tuple[Qx, Tuple[Triangle, ...], Tuple[Qx, ...]]:
    """Return exact minimum, its active triples, and sorted distinct areas."""
    areas = triangle_areas(incumbent_points())
    minimum = areas[0][1]
    for _, area in areas[1:]:
        if compare(area, minimum) < 0:
            minimum = area
    active = tuple(triangle for triangle, area in areas if (area - minimum).is_zero())
    distinct = []
    ordered = sorted((area for _, area in areas), key=cmp_to_key(compare))
    for area in ordered:
        if not distinct or not (area - distinct[-1]).is_zero():
            distinct.append(area)
    return minimum, active, tuple(distinct)


def _d4_permutations(points: Sequence[Point]) -> Tuple[Tuple[int, ...], ...]:
    """Return the eight label permutations induced by square symmetries."""
    transforms: Tuple[Callable[[Qx, Qx], Point], ...] = (
        lambda a, b: (a, b),
        lambda a, b: (ONE - b, a),
        lambda a, b: (ONE - a, ONE - b),
        lambda a, b: (b, ONE - a),
        lambda a, b: (ONE - a, b),
        lambda a, b: (a, ONE - b),
        lambda a, b: (b, a),
        lambda a, b: (ONE - b, ONE - a),
    )
    result = []
    for transform in transforms:
        permutation = []
        for point in points:
            transformed = transform(*point)
            try:
                permutation.append(points.index(transformed))
            except ValueError as error:
                raise AssertionError("D4 transform left published configuration") from error
        result.append(tuple(permutation))
    return tuple(result)


def active_structure() -> Tuple[Tuple[Tuple[Triangle, ...], ...], Tuple[Tuple[int, ...], ...]]:
    """Compute D4 active-triangle orbits and minimum hitting sets exactly."""
    points = incumbent_points()
    _, active, _ = incumbent_analysis()
    active_set = set(active)
    permutations = _d4_permutations(points)
    orbits = []
    remaining = set(active)
    while remaining:
        seed = min(remaining)
        orbit = {
            tuple(sorted(permutation[index] for index in seed))
            for permutation in permutations
        }
        if not orbit <= active_set:
            raise AssertionError("active set should be invariant under D4")
        orbits.append(tuple(sorted(orbit)))
        remaining -= orbit

    for size in range(13):
        hitting_sets = active_hitting_sets(size, active)
        if hitting_sets:
            return tuple(sorted(orbits, key=lambda orbit: orbit[0])), hitting_sets
    raise AssertionError("finite active hypergraph has no hitting set")


def active_hitting_sets(size: int, active: Tuple[Triangle, ...] | None = None) -> Tuple[Tuple[int, ...], ...]:
    """Return all size-``size`` transversals of the exact active hypergraph."""
    if not 0 <= size <= 12:
        raise ValueError("hitting-set size must be between zero and 12")
    if active is None:
        _, active, _ = incumbent_analysis()
    return tuple(
        candidate
        for candidate in combinations(range(12), size)
        if all(set(candidate).intersection(triangle) for triangle in active)
    )


def rational_triangle_areas(
    points: Sequence[Tuple[Fraction, Fraction]],
) -> List[Tuple[Triangle, Fraction]]:
    return [
        (
            triangle,
            abs(
                (points[triangle[1]][0] - points[triangle[0]][0])
                * (points[triangle[2]][1] - points[triangle[0]][1])
                - (points[triangle[1]][1] - points[triangle[0]][1])
                * (points[triangle[2]][0] - points[triangle[0]][0])
            )
            / 2,
        )
        for triangle in combinations(range(len(points)), 3)
    ]


def verify_rational_candidate(
    points: Sequence[Tuple[Fraction, Fraction]],
) -> Tuple[Fraction, Tuple[Triangle, ...]]:
    """Exactly validate a 12-point rational candidate and return its minimum.

    This is intentionally separate from the algebraic-incumbent construction:
    candidates snapped to dyadic rationals can be checked with only Fraction
    arithmetic before being compared to the exact incumbent below.
    """
    if len(points) != 12:
        raise ValueError("a Heilbronn n=12 candidate must contain exactly 12 points")
    normalized = tuple((Fraction(x), Fraction(y)) for x, y in points)
    if any(x < 0 or x > 1 or y < 0 or y > 1 for x, y in normalized):
        raise ValueError("candidate point lies outside the unit square")
    if len(set(normalized)) != len(normalized):
        raise ValueError("candidate contains coincident points")
    areas = rational_triangle_areas(normalized)
    minimum = min(area for _, area in areas)
    active = tuple(triangle for triangle, area in areas if area == minimum)
    return minimum, active


def strictly_beats_incumbent(points: Sequence[Tuple[Fraction, Fraction]]) -> bool:
    """Prove a rational candidate is strictly above the algebraic incumbent."""
    minimum, _ = verify_rational_candidate(points)
    return sign(Qx.rational(minimum) - incumbent_value()) > 0


def decimal_string(value: Qx, digits: int = 30) -> str:
    """Render a correctly rounded-ish enclosure midpoint without float arithmetic."""
    from decimal import Decimal, localcontext

    lower, upper = root_bounds(max(128, digits * 5))
    midpoint = (lower + upper) / 2
    with localcontext() as context:
        context.prec = digits + 8
        decimal_x = Decimal(midpoint.numerator) / Decimal(midpoint.denominator)
        decimal_value = (
            Decimal(value.a0.numerator) / Decimal(value.a0.denominator)
            + Decimal(value.a1.numerator) / Decimal(value.a1.denominator) * decimal_x
            + Decimal(value.a2.numerator) / Decimal(value.a2.denominator) * decimal_x * decimal_x
        )
        return format(decimal_value, f".{digits}f")


def main() -> None:
    minimum, active, distinct = incumbent_analysis()
    expected = incumbent_value()
    if not (minimum - expected).is_zero():
        raise AssertionError("published formula does not equal enumerated minimum")
    if not record_cubic(minimum).is_zero():
        raise AssertionError("record area does not satisfy its published cubic")
    orbits, hitting_sets = active_structure()
    print("minimum_area", decimal_string(minimum, 36))
    print("active_triangles", len(active))
    print("distinct_area_tiers", len(distinct))
    print("second_area", decimal_string(distinct[1], 18))
    print("active_orbit_sizes", tuple(len(orbit) for orbit in orbits))
    print("minimum_hitting_sets", hitting_sets)
    print("active", active)


if __name__ == "__main__":
    main()
