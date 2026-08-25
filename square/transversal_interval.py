"""Exact interval branch-and-bound engine for named size-5 support strata.

This generalizes the D4 certificate's safe pruning rule to a fixed-complement
stratum.  A box is discarded only when exact interval arithmetic proves that
some triangle has area at most the chosen rational target throughout the box.
For each determinant, the bound is the exact vertex hull over its coordinate
interval box, avoiding the dependency loss of a naive difference/product
evaluation.  The command intentionally has a finite box budget by default; an
incomplete run is reported as incomplete and is never a no-go certificate.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations, product
from typing import Sequence, Tuple

from incumbent import algebraic_bounds, incumbent_points, incumbent_value
from transversal_search import STRATA, Stratum


Interval = Tuple[Fraction, Fraction]
Point = Tuple[Interval, Interval]
Triangle = Tuple[int, int, int]
TRIANGLES: Tuple[Triangle, ...] = tuple(combinations(range(12), 3))
ZERO: Interval = (Fraction(0), Fraction(0))
ONE: Interval = (Fraction(1), Fraction(1))


@dataclass(frozen=True)
class Box:
    parameters: Tuple[Interval, ...]
    depth: int = 0


@dataclass(frozen=True)
class DiscardedBox:
    box: Box
    witness: Triangle
    witness_upper: Fraction


@dataclass(frozen=True)
class Exploration:
    stratum: str
    target_upper: Fraction
    record_lower: Fraction
    record_upper: Fraction
    visited_boxes: int
    discarded_boxes: int
    pending_boxes: int
    maximum_depth: int
    complete: bool
    discarded: Tuple[DiscardedBox, ...]
    pending: Tuple[Box, ...]


def add(left: Interval, right: Interval) -> Interval:
    return left[0] + right[0], left[1] + right[1]


def subtract(left: Interval, right: Interval) -> Interval:
    return left[0] - right[1], left[1] - right[0]


def multiply(left: Interval, right: Interval) -> Interval:
    products = (left[0] * right[0], left[0] * right[1], left[1] * right[0], left[1] * right[1])
    return min(products), max(products)


def absolute_upper(interval: Interval) -> Fraction:
    return max(abs(interval[0]), abs(interval[1]))


def incumbent_interval_points(root_bisections: int) -> Tuple[Point, ...]:
    """Enclose every frozen incumbent coordinate with rational endpoints."""

    return tuple(
        tuple(algebraic_bounds(component, root_bisections) for component in point)  # type: ignore[return-value]
        for point in incumbent_points()
    )


def root_box(stratum: Stratum) -> Box:
    return Box(tuple((Fraction(0), Fraction(1)) for _ in stratum.parameter_coordinates))


def points_for_box(stratum: Stratum, box: Box, root_bisections: int) -> Tuple[Point, ...]:
    if len(box.parameters) != stratum.dimensions:
        raise ValueError("box dimension does not match the stratum")
    points = [list(point) for point in incumbent_interval_points(root_bisections)]
    for interval, (label, coordinate) in zip(box.parameters, stratum.parameter_coordinates):
        points[label][coordinate] = interval
    return tuple(tuple(point) for point in points)  # type: ignore[return-value]


def double_area_interval(points: Sequence[Point], triangle: Triangle) -> Interval:
    i, j, k = triangle
    xi, yi = points[i]
    xj, yj = points[j]
    xk, yk = points[k]
    first = multiply(subtract(xj, xi), subtract(yk, yi))
    second = multiply(subtract(yj, yi), subtract(xk, xi))
    return subtract(first, second)


def double_area_vertex_upper(points: Sequence[Point], triangle: Triangle) -> Fraction:
    """Return a tight coordinate-box upper bound for one absolute determinant.

    A signed triangle determinant is affine in each of its six coordinate
    arguments separately.  Its maximum absolute value on an independent
    coordinate box is therefore attained at a box vertex.  Frozen algebraic
    coordinates are enclosed independently here; that only enlarges the true
    fixed-complement set, so the resulting upper bound remains rigorous.
    """

    i, j, k = triangle
    coordinates = points[i] + points[j] + points[k]
    varying = tuple(index for index, interval in enumerate(coordinates) if interval[0] != interval[1])
    values = [interval[0] for interval in coordinates]
    maximum = Fraction(0)
    for endpoints in product((0, 1), repeat=len(varying)):
        for index, endpoint in zip(varying, endpoints):
            values[index] = coordinates[index][endpoint]
        xi, yi, xj, yj, xk, yk = values
        determinant = (xj - xi) * (yk - yi) - (yj - yi) * (xk - xi)
        maximum = max(maximum, abs(determinant))
    return maximum


def minimum_area_upper(stratum: Stratum, box: Box, root_bisections: int) -> Tuple[Fraction, Triangle]:
    """Return a valid upper bound on the box's least triangle area and witness."""

    points = points_for_box(stratum, box, root_bisections)
    candidates = tuple((double_area_vertex_upper(points, triangle) / 2, triangle) for triangle in TRIANGLES)
    return min(candidates, key=lambda item: item[0])


def split(box: Box) -> Tuple[Box, Box]:
    if not box.parameters:
        raise ValueError("cannot split a zero-dimensional box")
    index = max(range(len(box.parameters)), key=lambda candidate: box.parameters[candidate][1] - box.parameters[candidate][0])
    lower, upper = box.parameters[index]
    midpoint = (lower + upper) / 2
    left = list(box.parameters)
    right = list(box.parameters)
    left[index] = (lower, midpoint)
    right[index] = (midpoint, upper)
    return Box(tuple(left), box.depth + 1), Box(tuple(right), box.depth + 1)


def explore(
    stratum: Stratum,
    *,
    slack_bits: int = 40,
    root_bisections: int = 128,
    max_boxes: int | None = 1000,
) -> Exploration:
    """Explore a stratum safely; only ``complete=True`` is a full cover."""

    if slack_bits <= 0 or root_bisections <= 0:
        raise ValueError("precision parameters must be positive")
    if max_boxes is not None and max_boxes <= 0:
        raise ValueError("max_boxes must be positive when supplied")
    record_lower, record_upper = algebraic_bounds(incumbent_value(), root_bisections)
    target = record_upper + Fraction(1, 2**slack_bits)
    pending = [root_box(stratum)]
    discarded = []
    visited = 0
    maximum_depth = 0
    while pending and (max_boxes is None or visited < max_boxes):
        box = pending.pop()
        visited += 1
        maximum_depth = max(maximum_depth, box.depth)
        upper, witness = minimum_area_upper(stratum, box, root_bisections)
        if upper <= target:
            discarded.append(DiscardedBox(box, witness, upper))
        else:
            pending.extend(split(box))
    return Exploration(
        stratum=stratum.name,
        target_upper=target,
        record_lower=record_lower,
        record_upper=record_upper,
        visited_boxes=visited,
        discarded_boxes=len(discarded),
        pending_boxes=len(pending),
        maximum_depth=maximum_depth,
        complete=not pending,
        discarded=tuple(discarded),
        pending=tuple(pending),
    )


def decimal(value: Fraction, digits: int = 30) -> str:
    from decimal import Decimal, localcontext

    with localcontext() as context:
        context.prec = digits + 8
        result = Decimal(value.numerator) / Decimal(value.denominator)
        return format(result, f".{digits}f")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stratum", choices=tuple(STRATA), default="four-interiors-plus-boundary")
    parser.add_argument("--max-boxes", type=int, default=1000, help="finite budget; use 0 only to request an unbounded full cover")
    parser.add_argument("--slack-bits", type=int, default=40)
    parser.add_argument("--root-bisections", type=int, default=128)
    arguments = parser.parse_args()
    budget = None if arguments.max_boxes == 0 else arguments.max_boxes
    result = explore(
        STRATA[arguments.stratum],
        slack_bits=arguments.slack_bits,
        root_bisections=arguments.root_bisections,
        max_boxes=budget,
    )
    print("stratum", result.stratum)
    print("target_upper", decimal(result.target_upper, 30))
    print("visited_boxes", result.visited_boxes)
    print("discarded_boxes", result.discarded_boxes)
    print("pending_boxes", result.pending_boxes)
    print("maximum_depth", result.maximum_depth)
    print("complete", result.complete)
    if not result.complete:
        print("status", "INCOMPLETE: no no-go claim")


if __name__ == "__main__":
    main()
