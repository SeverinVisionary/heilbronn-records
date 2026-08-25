"""Independent Decimal reconstruction of the Comellas--Yebra n=12 witness.

This module deliberately does not import the exact-field implementation.  It
is a numerical cross-check for transcription errors; certification remains in
``incumbent.py`` and uses rational arithmetic plus a root isolating interval.
"""

from __future__ import annotations

from decimal import Decimal, localcontext
from itertools import combinations
from typing import List, Sequence, Tuple


Point = Tuple[Decimal, Decimal]
Triangle = Tuple[int, int, int]


def _root(precision: int) -> Decimal:
    lower = Decimal(0)
    upper = Decimal(1) / Decimal(4)
    # Decimal bisection needs only a little headroom beyond the requested
    # output precision, and never invokes binary floats.
    for _ in range(precision * 5):
        midpoint = (lower + upper) / 2
        value = 4 * midpoint**3 - 12 * midpoint**2 + 10 * midpoint - 1
        if value < 0:
            lower = midpoint
        else:
            upper = midpoint
    return (lower + upper) / 2


def points(precision: int = 80) -> Tuple[Point, ...]:
    with localcontext() as context:
        context.prec = precision + 12
        one = Decimal(1)
        zero = Decimal(0)
        half = one / 2
        x = _root(precision + 12)
        y = 2 * x * x - 3 * x + half
        return (
            (x, zero),
            (one - x, zero),
            (x, one),
            (one - x, one),
            (zero, x),
            (one, x),
            (zero, one - x),
            (one, one - x),
            (half, y),
            (y, half),
            (one - y, half),
            (half, one - y),
        )


def areas(configuration: Sequence[Point]) -> List[Tuple[Triangle, Decimal]]:
    result = []
    for triangle in combinations(range(len(configuration)), 3):
        i, j, k = triangle
        xi, yi = configuration[i]
        xj, yj = configuration[j]
        xk, yk = configuration[k]
        result.append((triangle, abs((xj - xi) * (yk - yi) - (yj - yi) * (xk - xi)) / 2))
    return result


def analysis(precision: int = 80) -> Tuple[Decimal, Tuple[Triangle, ...], Decimal]:
    with localcontext() as context:
        context.prec = precision + 12
        all_areas = areas(points(precision))
        minimum = min(area for _, area in all_areas)
        tolerance = Decimal(10) ** (-(precision - 12))
        active = tuple(triangle for triangle, area in all_areas if abs(area - minimum) < tolerance)
        second = min(area for _, area in all_areas if area - minimum > tolerance)
        return +minimum, active, +second


def main() -> None:
    minimum, active, second = analysis()
    print("minimum_area", minimum)
    print("active_triangles", len(active))
    print("second_area", second)
    print("active", active)


if __name__ == "__main__":
    main()
