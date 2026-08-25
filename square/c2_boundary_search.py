"""Reflection-breaking C2 boundary-incidence search for Heilbronn n=12.

This numerical discovery family keeps the record's eight boundary incidences
while relaxing its quarter-turn and reflection symmetry.  Two bottom seeds
generate two top points under a half turn; two left seeds generate two right
points; and two free interior seeds generate their opposite partners.  The
resulting family has eight real parameters, contains the Comellas--Yebra
configuration exactly, and permits C4/reflection breaking.  It is a distinct
boundary-incidence stratum, not a cover of the full C4 family or of all
12-point configurations.

Differential evolution discovers a sign cell without receiving the incumbent
coordinates.  A sign-fixed epigraph SLSQP solve then polishes that cell.  This
is numerical discovery only: every selected point can be dyadically snapped
and checked in exact rational arithmetic before it is described as an
improvement.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from itertools import combinations
from typing import Tuple

import numpy as np
from scipy.optimize import differential_evolution, minimize

import decimal_verifier
from global_mccormick_relaxation import area_upper_bound
from global_normal_form_search import exact_snap_report


Array = np.ndarray
Triangle = Tuple[int, int, int]
TRIPLES = np.asarray(tuple(combinations(range(12), 3)), dtype=int)
PARAMETER_COUNT = 8
DEFAULT_SEEDS = (2026081723, 2026081724, 2026081725, 2026081726)
UPPER_AREA_BOUND = float(area_upper_bound(12))


@dataclass(frozen=True)
class Trial:
    """One reproducible C2-boundary numerical discovery trial."""

    seed: int
    differential_evolution_area: float
    epigraph_area: float
    epigraph_success: bool
    nfev: int
    selected_stage: str
    minimum_area: float
    active_triangles: Tuple[Triangle, ...]
    points: Tuple[Tuple[float, float], ...]


def half_turn(point: Array) -> Array:
    """Rotate a point by 180 degrees about the square centre."""

    values = np.asarray(point, dtype=float)
    if values.shape != (2,):
        raise ValueError("a point must contain exactly two coordinates")
    return np.asarray((1.0 - values[0], 1.0 - values[1]), dtype=float)


def configuration(parameters: Array) -> Array:
    """Embed eight boundary/interior parameters into twelve labelled points."""

    values = np.asarray(parameters, dtype=float)
    if values.shape != (PARAMETER_COUNT,):
        raise ValueError(f"the C2 boundary family requires exactly {PARAMETER_COUNT} parameters")
    bottom_first, bottom_second, left_first, left_second, interior_ax, interior_ay, interior_bx, interior_by = values
    bottom = np.asarray(((bottom_first, 0.0), (bottom_second, 0.0)), dtype=float)
    left = np.asarray(((0.0, left_first), (0.0, left_second)), dtype=float)
    interior = np.asarray(((interior_ax, interior_ay), (interior_bx, interior_by)), dtype=float)
    return np.vstack((bottom, tuple(half_turn(point) for point in bottom), left, tuple(half_turn(point) for point in left), interior, tuple(half_turn(point) for point in interior)))


def canonical_incumbent_parameters() -> Array:
    """Return the published record in this C2-boundary parameter convention."""

    points = np.asarray(decimal_verifier.points(80), dtype=float)
    return np.concatenate(
        (
            (points[0, 0], points[1, 0]),
            (points[4, 1], points[6, 1]),
            points[8],
            points[9],
        )
    )


def canonical_incumbent_points() -> Array:
    """Return the record in this module's boundary-pair labelling convention."""

    return configuration(canonical_incumbent_parameters())


def signed_areas(points: Array) -> Array:
    """Return all 220 oriented ordinary areas in lexicographic triple order."""

    values = np.asarray(points, dtype=float)
    if values.shape != (12, 2):
        raise ValueError("a C2-boundary configuration must have shape (12, 2)")
    first = values[TRIPLES[:, 0]]
    second = values[TRIPLES[:, 1]]
    third = values[TRIPLES[:, 2]]
    return (
        (second[:, 0] - first[:, 0]) * (third[:, 1] - first[:, 1])
        - (second[:, 1] - first[:, 1]) * (third[:, 0] - first[:, 0])
    ) / 2.0


def minimum_area(points: Array) -> float:
    """Return the actual geometric least triangle area."""

    return float(np.min(np.abs(signed_areas(points))))


def active_triangles(points: Array, tolerance: float = 1e-9) -> Tuple[Triangle, ...]:
    """Return triples tied with the actual minimum to a numerical tolerance."""

    areas = np.abs(signed_areas(points))
    minimum = float(np.min(areas))
    return tuple(
        tuple(int(index) for index in triangle)
        for triangle, area in zip(TRIPLES, areas)
        if area <= minimum + tolerance
    )


def is_c2_boundary_configuration(points: Array, tolerance: float = 1e-12) -> bool:
    """Check containment, four boundary pairs, and the two interior C2 pairs."""

    values = np.asarray(points, dtype=float)
    if values.shape != (12, 2) or np.any(values < -tolerance) or np.any(values > 1.0 + tolerance):
        return False
    if not np.all(np.abs(values[0:2, 1]) <= tolerance) or not np.all(np.abs(values[4:6, 0]) <= tolerance):
        return False
    return bool(
        all(np.max(np.abs(values[right] - half_turn(values[left]))) <= tolerance for left, right in ((0, 2), (1, 3), (4, 6), (5, 7), (8, 10), (9, 11)))
    )


def epigraph_polish(parameters: Array) -> Tuple[float, Array, bool]:
    """Optimize within the sign cell selected by a discovery point."""

    start_parameters = np.asarray(parameters, dtype=float)
    initial_points = configuration(start_parameters)
    signs = np.where(signed_areas(initial_points) >= 0.0, 1.0, -1.0)
    start = np.append(start_parameters, minimum_area(initial_points))

    def constraints(vector: Array) -> Array:
        return signs * signed_areas(configuration(vector[:-1])) - vector[-1]

    polished = minimize(
        lambda vector: -vector[-1],
        start,
        method="SLSQP",
        bounds=[(0.0, 1.0)] * PARAMETER_COUNT + [(0.0, UPPER_AREA_BOUND)],
        constraints={"type": "ineq", "fun": constraints},
        options={"maxiter": 12_000, "ftol": 1e-13},
    )
    if not polished.success:
        return minimum_area(initial_points), start_parameters, False
    candidate = polished.x[:-1]
    candidate_points = configuration(candidate)
    if not is_c2_boundary_configuration(candidate_points, tolerance=1e-8):
        return minimum_area(initial_points), start_parameters, False
    return min(float(polished.x[-1]), minimum_area(candidate_points)), candidate, True


def select_candidate(
    raw_area: float,
    raw_parameters: Array,
    polished_area: float,
    polished_parameters: Array,
) -> Tuple[str, float, Array]:
    """Keep coordinates attaining the score that is actually reported."""

    if polished_area >= raw_area:
        return "epigraph", polished_area, polished_parameters
    return "differential-evolution", raw_area, raw_parameters


def run_trial(seed: int, *, popsize: int = 32, maxiter: int = 4000) -> Trial:
    """Run a seeded C2-boundary search without injecting record coordinates."""

    if not 0 <= seed < 2**32:
        raise ValueError("SciPy differential-evolution seeds must lie in [0, 2**32)")
    result = differential_evolution(
        lambda parameters: -minimum_area(configuration(parameters)),
        [(0.0, 1.0)] * PARAMETER_COUNT,
        seed=seed,
        popsize=popsize,
        maxiter=maxiter,
        tol=1e-11,
        polish=False,
        workers=1,
        updating="immediate",
    )
    raw_area = minimum_area(configuration(result.x))
    polished_area, polished_parameters, polished_success = epigraph_polish(result.x)
    selected_stage, selected_area, selected_parameters = select_candidate(
        raw_area, result.x, polished_area, polished_parameters
    )
    selected_points = configuration(selected_parameters)
    selected_area = min(selected_area, minimum_area(selected_points))
    return Trial(
        seed=seed,
        differential_evolution_area=raw_area,
        epigraph_area=polished_area,
        epigraph_success=polished_success,
        nfev=int(result.nfev),
        selected_stage=selected_stage,
        minimum_area=selected_area,
        active_triangles=active_triangles(selected_points),
        points=tuple(tuple(float(value) for value in point) for point in selected_points),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, action="append", help="explicit seed(s); default is the recorded campaign")
    parser.add_argument("--seed-limit", type=int, help="run only the first N selected seeds")
    parser.add_argument("--popsize", type=int, default=32)
    parser.add_argument("--maxiter", type=int, default=4000)
    parser.add_argument("--snap-bits", type=int, help="exactly audit each selected result after dyadic rounding")
    arguments = parser.parse_args()
    if arguments.popsize <= 0 or arguments.maxiter < 0:
        raise ValueError("popsize must be positive and maxiter must be nonnegative")
    seeds = tuple(arguments.seed) if arguments.seed else DEFAULT_SEEDS
    if arguments.seed_limit is not None:
        seeds = seeds[: arguments.seed_limit]
    incumbent = canonical_incumbent_points()
    print(f"incumbent={minimum_area(incumbent):.18f} parameters={tuple(canonical_incumbent_parameters())}")
    for seed in seeds:
        trial = run_trial(seed, popsize=arguments.popsize, maxiter=arguments.maxiter)
        points = np.asarray(trial.points, dtype=float)
        print(
            f"seed={trial.seed} de={trial.differential_evolution_area:.18f} "
            f"epigraph={trial.epigraph_area:.18f} epigraph_success={trial.epigraph_success} "
            f"selected={trial.selected_stage} minimum={trial.minimum_area:.18f} "
            f"gap={trial.minimum_area - minimum_area(incumbent):+.3e} "
            f"active={len(trial.active_triangles)} nfev={trial.nfev}"
        )
        print(f"  points={trial.points}")
        print("  classification=NUMERICAL_DISCOVERY_ONLY")
        if arguments.snap_bits is not None:
            report = exact_snap_report(points, arguments.snap_bits)
            print(
                f"  dyadic_bits={report.bits} exact_minimum={report.minimum_area} "
                f"strictly_beats_incumbent={report.strictly_beats_incumbent} active={len(report.active_triangles)}"
            )


if __name__ == "__main__":
    main()
