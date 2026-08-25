"""Exact global 12th-point insertion experiment for Goldberg's n=11 set.

With the 11 points fixed, every new triangle area is half the absolute value
of an affine function of the inserted point.  The 55 zero-area lines split
the square into sign cells.  On each cell, maximizing the least new double
area is a three-variable linear program in (u_x, u_y, s).  A bounded LP has
an optimal vertex, so enumerating all rank-three intersections of its signed
area and box constraints is a complete exact search of every cell.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations
from typing import Iterable, List, Sequence, Tuple

from incumbent import incumbent_value, rational_triangle_areas, sign


RationalPoint = Tuple[Fraction, Fraction]


# Goldberg's n=11 best-known configuration, reproduced in Appendix A of
# Sudermann--Merx (2026).  It has minimum area exactly 1/27.
N11_POINTS: Tuple[RationalPoint, ...] = (
    (Fraction(1, 3), Fraction(0)),
    (Fraction(2, 3), Fraction(0)),
    (Fraction(0), Fraction(2, 9)),
    (Fraction(1), Fraction(2, 9)),
    (Fraction(1, 3), Fraction(4, 9)),
    (Fraction(2, 3), Fraction(4, 9)),
    (Fraction(0), Fraction(2, 3)),
    (Fraction(1), Fraction(2, 3)),
    (Fraction(1, 2), Fraction(7, 9)),
    (Fraction(1, 6), Fraction(1)),
    (Fraction(5, 6), Fraction(1)),
)


@dataclass(frozen=True)
class Constraint:
    """a*x + b*y + c - d*s >= 0, with an audit label."""

    a: Fraction
    b: Fraction
    c: Fraction
    d: Fraction
    label: str


@dataclass(frozen=True)
class InsertionResult:
    point: RationalPoint
    new_double_minimum: Fraction
    full_minimum_area: Fraction
    active_constraint_labels: Tuple[str, str, str]
    enumerated_bases: int
    nonsingular_bases: int


def _det3(rows: Sequence[Sequence[Fraction]]) -> Fraction:
    return (
        rows[0][0] * (rows[1][1] * rows[2][2] - rows[1][2] * rows[2][1])
        - rows[0][1] * (rows[1][0] * rows[2][2] - rows[1][2] * rows[2][0])
        + rows[0][2] * (rows[1][0] * rows[2][1] - rows[1][1] * rows[2][0])
    )


def _solve_equalities(active: Sequence[Constraint]) -> Tuple[Fraction, Fraction, Fraction] | None:
    """Solve three active affine constraints with Cramer's rule, exactly."""
    matrix = [(constraint.a, constraint.b, -constraint.d) for constraint in active]
    rhs = [-constraint.c for constraint in active]
    determinant = _det3(matrix)
    if determinant == 0:
        return None
    coordinates = []
    for column in range(3):
        replaced = [
            tuple(rhs[row] if index == column else matrix[row][index] for index in range(3))
            for row in range(3)
        ]
        coordinates.append(_det3(replaced) / determinant)
    return tuple(coordinates)  # type: ignore[return-value]


def _pair_double_area_forms(points: Sequence[RationalPoint]) -> Tuple[Constraint, ...]:
    """Forms D_ij(u) for twice the signed area of (p_i,p_j,u)."""
    forms = []
    for i, j in combinations(range(len(points)), 2):
        xi, yi = points[i]
        xj, yj = points[j]
        dx, dy = xj - xi, yj - yi
        # D_ij(u) = -dy*u_x + dx*u_y + dy*x_i - dx*y_i.
        forms.append(Constraint(-dy, dx, dy * xi - dx * yi, Fraction(1), f"{i}-{j}"))
    return tuple(forms)


def _candidate_constraints(points: Sequence[RationalPoint]) -> Tuple[Constraint, ...]:
    """All signed-area and box constraints that can define an LP vertex."""
    signed = []
    for form in _pair_double_area_forms(points):
        signed.append(form)
        signed.append(Constraint(-form.a, -form.b, -form.c, form.d, f"-({form.label})"))
    return tuple(signed) + (
        Constraint(Fraction(1), Fraction(0), Fraction(0), Fraction(0), "x=0"),
        Constraint(Fraction(-1), Fraction(0), Fraction(1), Fraction(0), "x=1"),
        Constraint(Fraction(0), Fraction(1), Fraction(0), Fraction(0), "y=0"),
        Constraint(Fraction(0), Fraction(-1), Fraction(1), Fraction(0), "y=1"),
        Constraint(Fraction(0), Fraction(0), Fraction(0), Fraction(-1), "s=0"),
    )


def _is_feasible(point: RationalPoint, double_minimum: Fraction, forms: Iterable[Constraint]) -> bool:
    x, y = point
    if not (0 <= x <= 1 and 0 <= y <= 1 and double_minimum >= 0):
        return False
    return all(abs(form.a * x + form.b * y + form.c) >= double_minimum for form in forms)


def solve_insertion(points: Sequence[RationalPoint] = N11_POINTS) -> InsertionResult:
    """Globally optimize an inserted point using exact exhaustive LP vertices."""
    fixed_areas = rational_triangle_areas(points)
    fixed_minimum = min(area for _, area in fixed_areas)
    if fixed_minimum != Fraction(1, 27):
        raise ValueError("input is not the audited n=11 configuration")

    forms = _pair_double_area_forms(points)
    constraints = _candidate_constraints(points)
    best_double = Fraction(-1)
    best_point: RationalPoint | None = None
    best_labels: Tuple[str, str, str] | None = None
    bases = 0
    nonsingular = 0
    for active in combinations(constraints, 3):
        bases += 1
        solution = _solve_equalities(active)
        if solution is None:
            continue
        nonsingular += 1
        x, y, double_minimum = solution
        if double_minimum <= best_double:
            continue
        point = (x, y)
        if _is_feasible(point, double_minimum, forms):
            best_double = double_minimum
            best_point = point
            best_labels = tuple(constraint.label for constraint in active)  # type: ignore[assignment]

    if best_point is None or best_labels is None:
        raise AssertionError("the compact insertion problem should have a feasible LP vertex")
    return InsertionResult(
        point=best_point,
        new_double_minimum=best_double,
        full_minimum_area=min(fixed_minimum, best_double / 2),
        active_constraint_labels=best_labels,
        enumerated_bases=bases,
        nonsingular_bases=nonsingular,
    )


def main() -> None:
    result = solve_insertion()
    print("fixed_n11_minimum", Fraction(1, 27))
    print("inserted_point", result.point)
    print("new_double_minimum", result.new_double_minimum)
    print("full_n12_minimum", result.full_minimum_area)
    print("strictly_beats_incumbent", sign(Fraction(result.full_minimum_area) - incumbent_value()) > 0)
    print("active_constraints", result.active_constraint_labels)
    print("enumerated_bases", result.enumerated_bases)
    print("nonsingular_bases", result.nonsingular_bases)


if __name__ == "__main__":
    main()
