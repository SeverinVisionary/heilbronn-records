"""Exact interval branch-and-bound bracket for the incumbent D4 incidence family.

The boundary parameter x and interior parameter y describe the same orbit
pattern as the Comellas--Yebra construction.  Each can be restricted to
[0, 1/2], because replacing either by 1-value leaves the unlabeled point set
unchanged.  This does not cover every conceivable D4-symmetric 12-point
pattern.  Every triangle determinant is interval-evaluated using only
``Fraction`` arithmetic.  If the minimum of the 220 per-triangle interval
upper bounds is at most U on a box, then no configuration in that box has
minimum area greater than U.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations
from typing import Sequence, Tuple

from incumbent import algebraic_bounds, incumbent_value


Interval = Tuple[Fraction, Fraction]
Point = Tuple[Interval, Interval]
Triangle = Tuple[int, int, int]
TRIANGLES: Tuple[Triangle, ...] = tuple(combinations(range(12), 3))
ZERO: Interval = (Fraction(0), Fraction(0))
ONE: Interval = (Fraction(1), Fraction(1))
HALF: Interval = (Fraction(1, 2), Fraction(1, 2))


@dataclass(frozen=True)
class Box:
    x: Interval
    y: Interval
    depth: int = 0


@dataclass(frozen=True)
class Certificate:
    target_upper: Fraction
    record_lower: Fraction
    record_upper: Fraction
    slack: Fraction
    visited_boxes: int
    discarded_boxes: int
    maximum_depth: int


def add(left: Interval, right: Interval) -> Interval:
    return left[0] + right[0], left[1] + right[1]


def subtract(left: Interval, right: Interval) -> Interval:
    return left[0] - right[1], left[1] - right[0]


def multiply(left: Interval, right: Interval) -> Interval:
    products = (left[0] * right[0], left[0] * right[1], left[1] * right[0], left[1] * right[1])
    return min(products), max(products)


def d4_points(box: Box) -> Tuple[Point, ...]:
    x, y = box.x, box.y
    one_minus_x = subtract(ONE, x)
    one_minus_y = subtract(ONE, y)
    return (
        (x, ZERO),
        (one_minus_x, ZERO),
        (x, ONE),
        (one_minus_x, ONE),
        (ZERO, x),
        (ONE, x),
        (ZERO, one_minus_x),
        (ONE, one_minus_x),
        (HALF, y),
        (y, HALF),
        (one_minus_y, HALF),
        (HALF, one_minus_y),
    )


def double_area_interval(points: Sequence[Point], triangle: Triangle) -> Interval:
    i, j, k = triangle
    xi, yi = points[i]
    xj, yj = points[j]
    xk, yk = points[k]
    first = multiply(subtract(xj, xi), subtract(yk, yi))
    second = multiply(subtract(yj, yi), subtract(xk, xi))
    return subtract(first, second)


def absolute_upper(interval: Interval) -> Fraction:
    return max(abs(interval[0]), abs(interval[1]))


def minimum_area_upper(box: Box) -> Fraction:
    """A rigorous upper bound on the least of all 220 triangle areas."""
    points = d4_points(box)
    return min(absolute_upper(double_area_interval(points, triangle)) / 2 for triangle in TRIANGLES)


def split(box: Box) -> Tuple[Box, Box]:
    x_width = box.x[1] - box.x[0]
    y_width = box.y[1] - box.y[0]
    if x_width >= y_width:
        midpoint = (box.x[0] + box.x[1]) / 2
        return (
            Box((box.x[0], midpoint), box.y, box.depth + 1),
            Box((midpoint, box.x[1]), box.y, box.depth + 1),
        )
    midpoint = (box.y[0] + box.y[1]) / 2
    return (
        Box(box.x, (box.y[0], midpoint), box.depth + 1),
        Box(box.x, (midpoint, box.y[1]), box.depth + 1),
    )


def certify(slack_bits: int = 80, root_bisections: int = 192) -> Certificate:
    """Cover the complete incumbent-D4-incidence parameter square below U."""
    if slack_bits <= 0 or root_bisections <= 0:
        raise ValueError("precision parameters must be positive")
    record_lower, record_upper = algebraic_bounds(incumbent_value(), root_bisections)
    slack = Fraction(1, 2**slack_bits)
    target = record_upper + slack
    pending = [Box((Fraction(0), Fraction(1, 2)), (Fraction(0), Fraction(1, 2)))]
    visited = 0
    discarded = 0
    maximum_depth = 0
    while pending:
        box = pending.pop()
        visited += 1
        maximum_depth = max(maximum_depth, box.depth)
        if minimum_area_upper(box) <= target:
            discarded += 1
            continue
        pending.extend(split(box))
    return Certificate(
        target_upper=target,
        record_lower=record_lower,
        record_upper=record_upper,
        slack=slack,
        visited_boxes=visited,
        discarded_boxes=discarded,
        maximum_depth=maximum_depth,
    )


def decimal(value: Fraction, digits: int = 30) -> str:
    from decimal import Decimal, localcontext

    with localcontext() as context:
        context.prec = digits + 8
        result = Decimal(value.numerator) / Decimal(value.denominator)
        return format(result, f".{digits}f")


def main() -> None:
    certificate = certify()
    print("record_lower", decimal(certificate.record_lower, 36))
    print("record_upper", decimal(certificate.record_upper, 36))
    print("target_upper", decimal(certificate.target_upper, 36))
    print("slack", certificate.slack)
    print("visited_boxes", certificate.visited_boxes)
    print("discarded_boxes", certificate.discarded_boxes)
    print("maximum_depth", certificate.maximum_depth)


if __name__ == "__main__":
    main()
