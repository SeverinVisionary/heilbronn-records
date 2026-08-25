#!/usr/bin/env python3
"""Standalone verifier for the deposited Heilbronn circle configurations.

Depends on the Python standard library only, and on nothing outside this
deposit.  Run it and it will re-derive every claim from the integer coordinates:

    python3 verify.py            # verifies ./configs
    python3 verify.py <dir>

For each configuration it checks, in exact integer / rational arithmetic:

  * the point count matches the recorded n, and the points are distinct;
  * every point lies in the CLOSED unit-radius disk, i.e. X^2 + Y^2 <= scale^2;
  * no three points are collinear (no zero-area triple);
  * all C(n,3) triples are enumerated -- none skipped;
  * the minimum triangle area, recomputed from scratch, equals the recorded
    exact rational bit-for-bit;
  * that minimum against the published record of D. Cantrell.

NORMALIZATION.  Every coordinate is an integer to be divided by `scale`, and the
domain is the CLOSED disk of RADIUS 1 (area pi).  Cantrell's constants are
published in two conventions and they must not be mixed:

    Friedman, "The Heilbronn Problem for Circles"  -- unit RADIUS  (used here)
    MathWorld, "Heilbronn Triangle Problem"        -- unit AREA

    alpha_disk(n) = pi * H_n^{unit area}

MathWorld's n = 11 entry disagrees with the source it cites and is erroneous;
this deposit therefore treats Friedman's printed values as authoritative and
states margins against the TOP of his printed bracket, which is the
worst case for us.
"""

from __future__ import annotations

import json
import pathlib
import sys
from fractions import Fraction
from itertools import combinations

# Erich Friedman, "The Heilbronn Problem for Circles" (unit RADIUS), giving
# D. Cantrell's constructions of 2006-2007.  A printed ".0758+" means the value
# lies in [0.0758, 0.0759); we compare against the TOP of that interval.
FRIEDMAN = {
    7: ("0.294", "0.295"), 8: ("0.216", "0.217"), 9: ("0.173", "0.174"),
    10: ("0.150", "0.151"), 11: ("0.113", "0.114"), 12: ("0.104", "0.105"),
    13: ("0.0856", "0.0857"), 14: ("0.0758", "0.0759"),
    15: ("0.0700", "0.0701"), 16: ("0.0661", "0.0662"),
}


def check(path: pathlib.Path):
    data = json.loads(path.read_text())
    n = int(data["n"])
    scale = int(data["scale"])
    points = [(int(x), int(y)) for x, y in data["points"]]

    if len(points) != n:
        return False, f"{path.name}: {len(points)} points but n = {n}"
    if len(set(points)) != n:
        return False, f"{path.name}: duplicate points"
    for x, y in points:
        if x * x + y * y > scale * scale:
            return False, f"{path.name}: a point lies outside the closed unit disk"

    smallest, count, degenerate = None, 0, 0
    for a, b, c in combinations(range(n), 3):
        (x1, y1), (x2, y2), (x3, y3) = points[a], points[b], points[c]
        doubled = abs((x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1))
        count += 1
        if doubled == 0:
            degenerate += 1
        if smallest is None or doubled < smallest:
            smallest = doubled
    expected = n * (n - 1) * (n - 2) // 6
    if count != expected:
        return False, f"{path.name}: enumerated {count} triples, expected {expected}"
    if degenerate:
        return False, f"{path.name}: {degenerate} degenerate (collinear) triples"

    minimum = Fraction(smallest, 2 * scale * scale)
    recorded = data.get("min_area_exact")
    if recorded is None:
        return False, f"{path.name}: no min_area_exact recorded -- refusing to certify"
    if Fraction(recorded) != minimum:
        return False, f"{path.name}: recomputed minimum does not match the recorded value"

    if n not in FRIEDMAN:
        return True, f"{path.name}: PASS  n={n}  min={float(minimum):.15f}  (no published row)"
    low, high = (Fraction(v) for v in FRIEDMAN[n])
    if minimum >= high:
        margin = float(minimum / high) - 1
        note = f"IMPROVES on Cantrell: clears the bracket top {float(high)} by {margin:+.4%}"
    elif minimum >= low:
        note = f"matches Cantrell, inside the printed bracket [{float(low)}, {float(high)})"
    else:
        note = f"BELOW the published bracket [{float(low)}, {float(high)})"
    return True, f"{path.name}: PASS  n={n}  min={float(minimum):.15f}  {note}"


# The advertised headline result.  Pinned here so that a deposit whose data has
# drifted from its own documentation fails loudly instead of quietly verifying
# some other configuration.
HEADLINE_FILE = "circle_n14_converged.json"
HEADLINE_SCALE = 10 ** 33
HEADLINE_MINIMUM = Fraction(
    76715885771028939751784775506633485800988522351575884799934177551,
    10 ** 66,
)
EXPECTED_FILES = 12


def check_headline(directory: pathlib.Path):
    path = directory / HEADLINE_FILE
    if not path.exists():
        return False, f"headline configuration {HEADLINE_FILE} is missing"
    data = json.loads(path.read_text())
    if int(data["scale"]) != HEADLINE_SCALE:
        return False, (f"{HEADLINE_FILE}: scale is {data['scale']}, "
                       f"but this release documents 10^33")
    if Fraction(data["min_area_exact"]) != HEADLINE_MINIMUM:
        return False, f"{HEADLINE_FILE}: exact minimum differs from the advertised value"
    return True, (f"headline pinned: {HEADLINE_FILE}, scale 10^33, "
                  f"minimum {float(HEADLINE_MINIMUM):.18f}")


def main() -> int:
    directory = pathlib.Path(sys.argv[1] if len(sys.argv) > 1
                             else pathlib.Path(__file__).parent / "configs")
    files = sorted(directory.glob("circle_n*.json"),
                   key=lambda p: (int(json.loads(p.read_text())["n"]), p.stem))
    if not files:
        print(f"no configurations found in {directory}")
        return 1
    failures = 0
    for path in files:
        ok, message = check(path)
        print(message if ok else f"FAIL  {message}")
        failures += 0 if ok else 1

    ok, message = check_headline(directory)
    print(("\n" + message) if ok else f"\nFAIL  {message}")
    failures += 0 if ok else 1

    if len(files) != EXPECTED_FILES:
        print(f"FAIL  manifest: found {len(files)} configurations, expected {EXPECTED_FILES}")
        failures += 1

    print(f"\n{len(files) - failures} of {len(files)} configurations verified"
          if not failures else f"\n{failures} check(s) FAILED")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
