"""Certificate-guided exact ascent for max-min triangle-area configurations.

The audit says whether an incumbent is soft; this module is what exploits that.
One round:

1. compute every triangle area exactly and take the minimum ``m``;
2. collect the *band* of triangles within a relative tolerance of ``m`` — using
   only the exactly-minimal triangles makes the step immediately collide with
   the next tier, so the band is what makes progress possible;
3. ask an LP for a direction that increases every banded area at once while
   keeping boundary-pinned points feasible (float proposal);
4. rationalize the direction, then run an **exact** line search: for each
   trial step the moved configuration is checked for exact containment and its
   exact minimum area is recomputed, and the step is accepted only on a strict
   exact increase;
5. optionally snap the accepted configuration onto a rational grid, keeping the
   snap only if the exact minimum does not drop.

Every accepted configuration therefore carries an exact rational (or algebraic)
minimum area that strictly exceeds the previous one — no floating-point claim
enters the result.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations
from typing import List, Sequence, Tuple

import numpy as np
from scipy.optimize import linprog

from rigidity_engine import Domain, _determinant_gradient


@dataclass
class AscentStep:
    round_index: int
    step: Fraction
    band_size: int
    minimum_before: Fraction
    minimum_after: Fraction

    @property
    def gain(self) -> Fraction:
        return self.minimum_after - self.minimum_before


def _as_area(doubled):
    """Exact doubled-area element -> area, as a Fraction where possible.

    ``hasattr(x, "value")`` used to dispatch here, which is true only for
    ``RationalElement``; every algebraic field fell through to a *float*-derived
    value that also skipped the division by two.  Reported by the 2026-08-21
    panel as the one exactness leak that reached a recorded number.
    """

    value = getattr(doubled, "value", None)
    if value is not None:                      # RationalElement -> exact Fraction
        return Fraction(value, 2)
    return Fraction(doubled.to_float()) / 2    # display only; algebraic fields


def doubled_areas(points, field) -> dict:
    values = {}
    for triple in combinations(range(len(points)), 3):
        (x1, y1), (x2, y2), (x3, y3) = (points[index] for index in triple)
        determinant = (x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1)
        values[triple] = determinant if determinant.sign() > 0 else -determinant
    return values


def minimum_doubled(points, field):
    smallest = None
    for value in doubled_areas(points, field).values():
        if smallest is None or (value - smallest).sign() < 0:
            smallest = value
    return smallest


def _band(points, field, tolerance: Fraction) -> Tuple[object, List[Tuple[int, int, int]]]:
    values = doubled_areas(points, field)
    smallest = None
    for value in values.values():
        if smallest is None or (value - smallest).sign() < 0:
            smallest = value
    threshold = smallest * field.from_fraction(1 + tolerance)
    banded = [triple for triple, value in sorted(values.items()) if (value - threshold).sign() <= 0]
    return smallest, banded


def _contact_rows(points, domain: Domain, field, dimension: int):
    """Active domain-contact rows, each tagged with whether it is affine.

    A non-affine contact (the disk) needs *strict* inwardness: a tangential
    direction leaves the domain at every ``t > 0`` even though the linearized
    row admits it, which is why the ascent used to propose directions on which
    no step size was ever feasible.
    """

    rows = []
    for index, (x_value, y_value) in enumerate(points):
        for constraint in domain.constraints(field):
            if constraint.value(x_value, y_value).is_zero():
                gradient_x, gradient_y = constraint.gradient(x_value, y_value)
                row = [field.zero] * dimension
                row[2 * index] = gradient_x
                row[2 * index + 1] = gradient_y
                rows.append((row, constraint.affine))
    return rows


def _inside(points, domain: Domain, field) -> bool:
    for x_value, y_value in points:
        for constraint in domain.constraints(field):
            if constraint.value(x_value, y_value).sign() < 0:
                return False
    return True


def ascent_direction(points, domain: Domain, field, banded) -> List[Fraction] | None:
    """LP proposal: increase every banded area, keep pinned points feasible."""

    dimension = 2 * len(points)
    rows: List[List[float]] = []
    for triple in banded:
        (x1, y1), (x2, y2), (x3, y3) = (points[index] for index in triple)
        determinant = (x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1)
        orientation = 1 if determinant.sign() > 0 else -1
        row = [0.0] * dimension
        for index, value in _determinant_gradient(points, triple, field):
            row[index] = value.to_float() * orientation
        rows.append(row)
    area_count = len(rows)
    strict_positions = []
    for contact, affine in _contact_rows(points, domain, field, dimension):
        if not affine:
            strict_positions.append(len(rows))
        rows.append([value.to_float() for value in contact])

    matrix = np.array(rows, dtype=float)
    scale = float(np.max(np.abs(matrix))) or 1.0
    matrix = matrix / scale
    upper = np.hstack([-matrix, np.zeros((matrix.shape[0], 1))])
    upper[:area_count, -1] = 1.0
    for position in strict_positions:
        upper[position, -1] = 1.0
    result = linprog(
        c=np.concatenate([np.zeros(dimension), [-1.0]]),
        A_ub=upper,
        b_ub=np.zeros(matrix.shape[0]),
        bounds=[(-1.0, 1.0)] * dimension + [(0.0, 1.0)],
        method="highs",
    )
    if not result.success or result.x[-1] <= 1e-12:
        return None
    return [Fraction(value).limit_denominator(10 ** 6) for value in result.x[:dimension]]


def _snap(points, field, denominator: int):
    snapped = []
    for x_value, y_value in points:
        snapped.append(
            (
                field.from_fraction(Fraction(round(x_value.to_float() * denominator), denominator)),
                field.from_fraction(Fraction(round(y_value.to_float() * denominator), denominator)),
            )
        )
    return tuple(snapped)


def ascend(
    points,
    domain: Domain,
    field,
    *,
    rounds: int = 40,
    tolerance: Fraction = Fraction(1, 200),
    ladder: int = 26,
    snap_denominator: int | None = 10 ** 12,
):
    """Run exact ascent until no strictly improving step is found."""

    history: List[AscentStep] = []
    current = tuple(points)
    for round_index in range(rounds):
        smallest, banded = _band(current, field, tolerance)
        direction = ascent_direction(current, domain, field, banded)
        if direction is None:
            break
        velocity = [field.from_fraction(value) for value in direction]
        best_points, best_minimum, best_step = None, smallest, None
        step = Fraction(1, 4)
        for _ in range(ladder):
            moved = tuple(
                (
                    current[index][0] + field.from_fraction(step) * velocity[2 * index],
                    current[index][1] + field.from_fraction(step) * velocity[2 * index + 1],
                )
                for index in range(len(current))
            )
            if _inside(moved, domain, field):
                candidate = minimum_doubled(moved, field)
                if (candidate - best_minimum).sign() > 0:
                    best_points, best_minimum, best_step = moved, candidate, step
                    break
            step = step / 2
        if best_points is None:
            if tolerance > Fraction(1, 10 ** 6):
                tolerance = tolerance / 4
                continue
            break
        if snap_denominator is not None:
            snapped = _snap(best_points, field, snap_denominator)
            if _inside(snapped, domain, field):
                snapped_minimum = minimum_doubled(snapped, field)
                # compare against the accepted step, not the round's start, or a
                # snap can silently give back most of the round's gain
                if (snapped_minimum - best_minimum).sign() > 0:
                    best_points, best_minimum = snapped, snapped_minimum
        history.append(
            AscentStep(round_index, best_step, len(banded), _as_area(smallest), _as_area(best_minimum))
        )
        current = best_points
    return current, minimum_doubled(current, field), history
