"""Attack the Friedman/Cantrell 2007 best-known circle table.

Two ideas, both cheap:

1. **Softness audit.** For the published unit-area circle constants, ``n^2 H_n``
   should vary smoothly.  A row that dips below both neighbours is
   under-optimized, and says where to spend compute before spending any.
2. **Multistart annealing + exact snap.**  Floating point proposes; the reported
   number is an exact rational recomputed from integer-scaled coordinates that
   are verified to lie in the closed unit disk.

Normalization: MathWorld tabulates the UNIT-AREA circle.  Scaling to the
unit-radius disk multiplies lengths by sqrt(pi), hence areas by pi:
    alpha_disk(n) = pi * H_n^{unit-area}
"""

from __future__ import annotations

import json
import math
import os
import sys
from fractions import Fraction as F
from itertools import combinations
from multiprocessing import Pool

import numpy as np

# Friedman (2007); D. Cantrell (pers. comm. 1998-06-18 / 2007-06-18), unit-AREA circle.
# Re-fetched from MathWorld 2026-08-23.  Several rows are published to far more
# than six decimals; the extra digits are kept because a "beat" of a few parts
# per million against a six-decimal copy is indistinguishable from the rounding
# of that copy.  Rows still shown to six decimals are six decimals at the source.
MATHWORLD_UNIT_AREA = {
    7: 0.093700,
    8: 0.069055,
    9: 0.05531071895608711,
    10: 0.047869,
    11: 0.03494193340280051,
    12: 0.03339560352492413,
    13: 0.02726586326658908,
    14: 0.02414611295141071,
    15: 0.02229427231706078,
    16: 0.021051,
}
# Closed-form optima for the small n, unit-AREA circle.  Used as a correctness
# gate: an annealer that BEATS any of these has a containment or area bug.
#   H_3 = 3 sqrt(3) / (4 pi)                  (equilateral triangle)
#   H_4 = 1 / pi                              (square)
#   H_5 = sqrt(5/2 (5 - sqrt(5))) / (4 pi)    (regular pentagon)
#   H_6 = sqrt(3) / (4 pi)                    (regular hexagon)
CLOSED_FORM_UNIT_AREA = {
    3: 3 * math.sqrt(3) / (4 * math.pi),
    4: 1 / math.pi,
    5: math.sqrt(5 / 2 * (5 - math.sqrt(5))) / (4 * math.pi),
    6: math.sqrt(3) / (4 * math.pi),
}
SCALE = 10 ** 12


def softness_audit(table=MATHWORLD_UNIT_AREA):
    """Rank published rows by how far n^2 H_n falls below its neighbours."""

    ns = sorted(table)
    scaled = {n: n * n * table[n] for n in ns}
    report = []
    for index, n in enumerate(ns):
        neighbours = [scaled[ns[j]] for j in (index - 1, index + 1) if 0 <= j < len(ns)]
        expected = sum(neighbours) / len(neighbours)
        report.append({"n": n, "n2H": scaled[n], "neighbour_mean": expected,
                       "shortfall": expected / scaled[n] - 1.0})
    report.sort(key=lambda row: -row["shortfall"])
    return report


def build_index(n):
    triples = np.array(list(combinations(range(n), 3)))
    per_point = [np.where((triples == i).any(axis=1))[0] for i in range(n)]
    return triples, per_point


def areas_of(points, triples, rows=None):
    selected = triples if rows is None else triples[rows]
    a, b, c = points[selected[:, 0]], points[selected[:, 1]], points[selected[:, 2]]
    return 0.5 * np.abs((b[:, 0] - a[:, 0]) * (c[:, 1] - a[:, 1])
                        - (c[:, 0] - a[:, 0]) * (b[:, 1] - a[:, 1]))


def anneal_once(job):
    """One restart.  Returns (min area, coordinates)."""

    n, seed, iterations = job
    rng = np.random.default_rng(seed)
    triples, per_point = build_index(n)

    boundary = max(3, int(rng.uniform(0.5, 1.0) * n))
    angles = np.sort(rng.uniform(0, 2 * np.pi, boundary))
    points = [np.c_[np.cos(angles), np.sin(angles)]]
    interior = n - boundary
    if interior:
        theta = rng.uniform(0, 2 * np.pi, interior)
        radius = np.sqrt(rng.uniform(0.02, 0.98, interior))
        points.append(np.c_[radius * np.cos(theta), radius * np.sin(theta)])
    points = np.vstack(points)

    areas = areas_of(points, triples)
    current = areas.min()
    step = 0.10
    for iteration in range(iterations):
        temperature = max(1e-12, 0.02 * current * (1 - iteration / iterations) ** 2)
        index = rng.integers(n)
        previous, previous_areas = points[index].copy(), areas[per_point[index]].copy()
        points[index] = points[index] + rng.normal(0, step, 2)
        radius = math.hypot(points[index, 0], points[index, 1])
        if radius > 1.0:
            points[index] /= radius
        areas[per_point[index]] = areas_of(points, triples, per_point[index])
        candidate = areas.min()
        if candidate > current or rng.random() < math.exp((candidate - current) / temperature):
            current = candidate
        else:
            points[index] = previous
            areas[per_point[index]] = previous_areas
        if iteration % 20000 == 19999:
            step = max(step * 0.6, 1e-6)
    return float(areas.min()), points.tolist()


def snap_to_disk(points, scale=SCALE):
    """Integer-scale the coordinates and pull any rounding escapee back inside."""

    snapped = []
    for x, y in points:
        integer_x, integer_y = int(round(x * scale)), int(round(y * scale))
        while integer_x * integer_x + integer_y * integer_y > scale * scale:
            if abs(integer_x) >= abs(integer_y):
                integer_x -= int(math.copysign(1, integer_x))
            else:
                integer_y -= int(math.copysign(1, integer_y))
        snapped.append((integer_x, integer_y))
    return snapped


def exact_minimum(integer_points, scale=SCALE):
    """Exact minimum triangle area, plus an exact containment check."""

    rationals = [(F(x, scale), F(y, scale)) for x, y in integer_points]
    for x, y in rationals:
        if x * x + y * y > 1:
            raise AssertionError("configuration leaves the unit disk")
    smallest = None
    for a, b, c in combinations(range(len(rationals)), 3):
        (x1, y1), (x2, y2), (x3, y3) = rationals[a], rationals[b], rationals[c]
        area = abs((x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1))
        if smallest is None or area < smallest:
            smallest = area
    return smallest / 2


def attack(n, restarts, iterations, workers, seed_base=10 ** 6):
    jobs = [(n, seed_base + 7919 * n + r, iterations) for r in range(restarts)]
    with Pool(workers) as pool:
        results = pool.map(anneal_once, jobs)
    value, points = max(results, key=lambda row: row[0])
    integers = snap_to_disk(points)
    return exact_minimum(integers), integers


def main():
    low = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    high = int(sys.argv[2]) if len(sys.argv) > 2 else 16
    restarts = int(sys.argv[3]) if len(sys.argv) > 3 else 96
    iterations = int(sys.argv[4]) if len(sys.argv) > 4 else 400000
    workers = int(sys.argv[5]) if len(sys.argv) > 5 else os.cpu_count()

    print("softness audit (largest shortfall = most under-optimized row):")
    for row in softness_audit():
        print(f"  n={row['n']:2d}  n^2*H_n={row['n2H']:.4f}  "
              f"neighbour mean={row['neighbour_mean']:.4f}  shortfall={row['shortfall']:+.2%}")
    print(flush=True)

    rows = []
    for n in range(low, high + 1):
        exact, integers = attack(n, restarts, iterations, workers)
        record = {"n": n, "ours_exact": str(exact), "ours": float(exact),
                  "scale": SCALE, "points": integers}
        if n in MATHWORLD_UNIT_AREA:
            target = MATHWORLD_UNIT_AREA[n] * math.pi
            record.update(mathworld_unit_area=MATHWORLD_UNIT_AREA[n],
                          target_unit_radius=target, ratio=float(exact) / target)
            flag = "  >>> BEATS THE 2007 TABLE" if float(exact) > target else ""
            print(f"n={n:2d} ours={float(exact):.9f} target={target:.9f} "
                  f"ratio={float(exact)/target:.5f}{flag}", flush=True)
        else:
            print(f"n={n:2d} ours={float(exact):.9f} (no published circle row)", flush=True)
        rows.append(record)
    with open(f"circle_attack_{low}_{high}.json", "w") as handle:
        json.dump(rows, handle, indent=1)


if __name__ == "__main__":
    main()
