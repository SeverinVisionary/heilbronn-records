"""Exact first-order obstruction at the Comellas--Yebra configuration.

This module proves an exact first-order local-isolation certificate, not global
optimality.  No nonzero feasible velocity lies in the critical cone in which
every currently active triangle area is nondecreasing.  Thus every nonzero
first-order displacement lowers at least one active triangle area.  Remote
configurations remain possible.

The certificate is a positive weighted sum of the 20 active unsigned-area
gradients.  It vanishes in every free/tangential coordinate and points strictly
outward at the eight boundary coordinates, so its directional derivative is
nonpositive on the unit-square tangent cone.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Tuple

from incumbent import (
    ONE,
    X,
    ZERO,
    Point,
    Qx,
    Triangle,
    active_structure,
    decimal_string,
    incumbent_analysis,
    incumbent_points,
    sign,
    signed_double_area,
)


Gradient = Tuple[Tuple[Qx, Qx], ...]


@dataclass(frozen=True)
class FirstOrderCertificate:
    """Exact weights and the common inward boundary derivative."""

    orbit_weights: Tuple[Qx, Qx, Qx]
    inward_normal: Qx
    weighted_gradient: Gradient
    critical_minor: Qx


# These weights correspond, in ``active_structure`` order, to the active
# D4-orbits of sizes 4, 8, and 8.  Multiplying all three by a positive element
# would produce the same certificate, so no normalization is needed.
ORBIT_WEIGHTS: Tuple[Qx, Qx, Qx] = (
    -4 * ONE + 44 * X - 28 * X * X,
    3 * ONE - 14 * X + 8 * X * X,
    ONE,
)

# The derivative of the weighted active-area sum in each inward boundary-normal
# direction.  It is strictly negative in the selected real embedding.
INWARD_NORMAL = -4 * ONE + 34 * X - 22 * X * X

# Flat coordinate indices for the eight boundary-tangential components followed
# by all eight interior components.  Once the weighted certificate forces the
# eight inward normal components to zero, these are the remaining free variables.
FREE_COORDINATES: Tuple[int, ...] = (0, 2, 4, 6, 9, 11, 13, 15) + tuple(range(16, 24))

# Indices in the lexicographically ordered active-triangle tuple.  The selected
# 16-by-16 derivative minor is nonzero exactly in Q(x), proving that the
# remaining critical-cone equations have only the zero solution.
CRITICAL_ACTIVE_INDICES: Tuple[int, ...] = (0, 4, 14, 17, 3, 13, 10, 7, 18, 19, 15, 16, 9, 5, 2, 11)
CRITICAL_MINOR = Qx(Fraction(-89, 2**21), Fraction(419, 2**20), Fraction(-9, 2**15))


def unsigned_area_gradient(points: Tuple[Point, ...], triangle: Triangle) -> Gradient:
    """Return the exact gradient of the triangle's unsigned area.

    Every active determinant is nonzero, so its unsigned-area derivative is
    the signed determinant derivative times ``sign(det)/2``.
    """

    i, j, k = triangle
    xi, yi = points[i]
    xj, yj = points[j]
    xk, yk = points[k]
    rows = [[ZERO, ZERO] for _ in range(12)]
    rows[i] = [yj - yk, xk - xj]
    rows[j] = [yk - yi, xi - xk]
    rows[k] = [yi - yj, xj - xi]
    orientation = sign(signed_double_area(points, triangle))
    if orientation == 0:
        raise AssertionError("an active triangle must have nonzero area")
    scale = Fraction(orientation, 2)
    return tuple(tuple(scale * entry for entry in row) for row in rows)


def _zero_gradient() -> list[list[Qx]]:
    return [[ZERO, ZERO] for _ in range(12)]


def _frozen_gradient(rows: list[list[Qx]]) -> Gradient:
    return tuple(tuple(row) for row in rows)


def _determinant(matrix: list[list[Qx]]) -> Qx:
    """Compute a square determinant by exact Gaussian elimination."""

    dimension = len(matrix)
    if any(len(row) != dimension for row in matrix):
        raise ValueError("determinant requires a square matrix")
    work = [row[:] for row in matrix]
    determinant = ONE
    for column in range(dimension):
        pivot_row = next((row for row in range(column, dimension) if not work[row][column].is_zero()), None)
        if pivot_row is None:
            return ZERO
        if pivot_row != column:
            work[column], work[pivot_row] = work[pivot_row], work[column]
            determinant = -determinant
        pivot = work[column][column]
        determinant *= pivot
        for row in range(column + 1, dimension):
            if work[row][column].is_zero():
                continue
            factor = work[row][column] / pivot
            for trailing in range(column + 1, dimension):
                work[row][trailing] -= factor * work[column][trailing]
    return determinant


def critical_minor() -> Qx:
    """Return the exact nonzero active-gradient minor on the critical cone."""

    points = incumbent_points()
    _, active, _ = incumbent_analysis()
    if len(active) != 20:
        raise AssertionError("unexpected active-triangle count")
    gradients = tuple(unsigned_area_gradient(points, triangle) for triangle in active)
    matrix = [
        [gradients[active_index][coordinate // 2][coordinate % 2] for coordinate in FREE_COORDINATES]
        for active_index in CRITICAL_ACTIVE_INDICES
    ]
    determinant = _determinant(matrix)
    if not (determinant - CRITICAL_MINOR).is_zero():
        raise AssertionError("critical minor changed unexpectedly")
    if sign(determinant) <= 0:
        raise AssertionError("critical minor must be strictly positive")
    return determinant


def certificate() -> FirstOrderCertificate:
    """Construct and check the exact tangent-cone certificate."""

    points = incumbent_points()
    orbits, _ = active_structure()
    if tuple(len(orbit) for orbit in orbits) != (4, 8, 8):
        raise AssertionError("unexpected active-orbit decomposition")

    total = _zero_gradient()
    for weight, orbit in zip(ORBIT_WEIGHTS, orbits):
        for triangle in orbit:
            gradient = unsigned_area_gradient(points, triangle)
            for point_index in range(12):
                for coordinate in range(2):
                    total[point_index][coordinate] += weight * gradient[point_index][coordinate]

    result = _frozen_gradient(total)
    _assert_certificate_shape(result)
    if any(sign(weight) <= 0 for weight in ORBIT_WEIGHTS):
        raise AssertionError("active-orbit weights must be strictly positive")
    if sign(INWARD_NORMAL) >= 0:
        raise AssertionError("inward normal must point strictly downhill")
    return FirstOrderCertificate(ORBIT_WEIGHTS, INWARD_NORMAL, result, critical_minor())


def _assert_certificate_shape(gradient: Gradient) -> None:
    """Check exact stationarity plus the eight identical inward normals."""

    # Bottom/top boundary points: x is tangential.  Left/right boundary
    # points: y is tangential.  All interior coordinates are free.
    for point_index in range(4):
        if not gradient[point_index][0].is_zero():
            raise AssertionError("boundary tangential gradient must vanish")
    for point_index in range(4, 8):
        if not gradient[point_index][1].is_zero():
            raise AssertionError("boundary tangential gradient must vanish")
    for point_index in range(8, 12):
        if not all(component.is_zero() for component in gradient[point_index]):
            raise AssertionError("interior gradient must vanish")

    inward_coordinates = (
        (0, 1, 1),
        (1, 1, 1),
        (2, 1, -1),
        (3, 1, -1),
        (4, 0, 1),
        (5, 0, -1),
        (6, 0, 1),
        (7, 0, -1),
    )
    for point_index, coordinate, inward_sign in inward_coordinates:
        if not (gradient[point_index][coordinate] * inward_sign - INWARD_NORMAL).is_zero():
            raise AssertionError("all inward boundary derivatives must agree")


def main() -> None:
    result = certificate()
    print("orbit_weights", result.orbit_weights)
    print("inward_normal", result.inward_normal)
    print("inward_normal_decimal", decimal_string(result.inward_normal, 36))
    print("critical_minor", result.critical_minor)
    print("critical_minor_decimal", decimal_string(result.critical_minor, 36))
    print("certificate", "PASS")


if __name__ == "__main__":
    main()
