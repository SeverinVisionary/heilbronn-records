"""Reflection-breaking C4 search for the 12-point square Heilbronn problem.

The Comellas--Yebra record is D4-symmetric, but the two-parameter D4 interval
certificate does not cover every configuration invariant only under a
quarter-turn.  This module searches the full three-orbit C4 family: each orbit
is generated from one free seed point by rotation about the square centre, so
the family has six real parameters and contains the published record exactly.

Differential evolution discovers a sign cell without receiving the incumbent
coordinates.  A sign-fixed epigraph SLSQP solve then polishes that cell.  This
is numerical discovery only; an optional dyadic snap is checked in exact
rational arithmetic before any candidate could be called an improvement.
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
PARAMETER_COUNT = 6
DEFAULT_SEEDS = (2026081702, 2026081703, 2026081704, 2026081705)
UPPER_AREA_BOUND = float(area_upper_bound(12))


@dataclass(frozen=True)
class Trial:
    """One reproducible C4-constrained numerical discovery trial."""

    seed: int
    differential_evolution_area: float
    epigraph_area: float
    epigraph_success: bool
    nfev: int
    selected_stage: str
    minimum_area: float
    active_triangles: Tuple[Triangle, ...]
    points: Tuple[Tuple[float, float], ...]


def quarter_turn(point: Array) -> Array:
    """Rotate one point counterclockwise by 90 degrees about ``(1/2, 1/2)``."""

    return np.asarray((1.0 - point[1], point[0]), dtype=float)


def orbit(seed: Array) -> Array:
    """Return the four labelled points in the C4 orbit of one seed."""

    values = np.asarray(seed, dtype=float)
    if values.shape != (2,):
        raise ValueError("a C4 seed must contain exactly two coordinates")
    result = np.empty((4, 2), dtype=float)
    result[0] = values
    for index in range(1, 4):
        result[index] = quarter_turn(result[index - 1])
    return result


def configuration(parameters: Array) -> Array:
    """Embed three C4 seed points into a labelled twelve-point configuration."""

    values = np.asarray(parameters, dtype=float)
    if values.shape != (PARAMETER_COUNT,):
        raise ValueError(f"the C4 family requires exactly {PARAMETER_COUNT} parameters")
    return np.vstack(tuple(orbit(values[2 * index : 2 * index + 2]) for index in range(3)))


def canonical_incumbent_parameters() -> Array:
    """Return the three quarter-turn orbit representatives of the record."""

    points = np.asarray(decimal_verifier.points(80), dtype=float)
    # The published labelling decomposes into the orbits
    # (0, 5, 3, 6), (1, 7, 2, 4), and (8, 10, 11, 9).
    return np.concatenate((points[0], points[1], points[8]))


def canonical_incumbent_points() -> Array:
    """Return the record in this module's orbit-labelling convention."""

    return configuration(canonical_incumbent_parameters())


def signed_areas(points: Array) -> Array:
    """Return all 220 oriented ordinary areas in lexicographic triple order."""

    values = np.asarray(points, dtype=float)
    if values.shape != (12, 2):
        raise ValueError("a C4 configuration must have shape (12, 2)")
    first = values[TRIPLES[:, 0]]
    second = values[TRIPLES[:, 1]]
    third = values[TRIPLES[:, 2]]
    return (
        (second[:, 0] - first[:, 0]) * (third[:, 1] - first[:, 1])
        - (second[:, 1] - first[:, 1]) * (third[:, 0] - first[:, 0])
    ) / 2.0


def minimum_area(points: Array) -> float:
    """Return the actual geometric minimum triangle area."""

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


def is_c4_configuration(points: Array, tolerance: float = 1e-12) -> bool:
    """Check containment and this module's three labelled C4 orbits."""

    values = np.asarray(points, dtype=float)
    if values.shape != (12, 2) or np.any(values < -tolerance) or np.any(values > 1.0 + tolerance):
        return False
    return bool(
        all(
            np.max(np.abs(values[4 * orbit_index + position] - quarter_turn(values[4 * orbit_index + position - 1])))
            <= tolerance
            for orbit_index in range(3)
            for position in range(1, 4)
        )
        and all(
            np.max(np.abs(quarter_turn(values[4 * orbit_index + 3]) - values[4 * orbit_index])) <= tolerance
            for orbit_index in range(3)
        )
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
        options={"maxiter": 8000, "ftol": 1e-13},
    )
    if not polished.success:
        return minimum_area(initial_points), start_parameters, False
    candidate = polished.x[:-1]
    candidate_points = configuration(candidate)
    if not is_c4_configuration(candidate_points, tolerance=1e-8):
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
    """Run a seeded C4 family search without injecting record coordinates."""

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
