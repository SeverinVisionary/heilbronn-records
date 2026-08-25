"""Free-coordinate discovery search over every size-5 active-transversal class.

Any strict improvement obtained by changing exactly five labelled points of the
Comellas--Yebra configuration must move a size-5 transversal of its twenty
active triangles.  Those transversals have three D4 classes.  Earlier
``transversal_search.py`` examined one edge-locked representative of each
class; this module keeps the same seven-point complement fixed but lets all
five moved labels vary freely in the unit square (ten dimensions).

The search is numerical discovery only.  A printed float is not a record; the
optional dyadic snap is passed through the existing exact ``Fraction`` checker.
No finite collection of trials proves a five-label no-go theorem.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from itertools import combinations
from typing import Iterable, Sequence, Tuple

import numpy as np
from scipy.optimize import differential_evolution, minimize

import decimal_verifier
from global_mccormick_relaxation import area_upper_bound
from global_normal_form_search import exact_snap_report
from incumbent import active_hitting_sets
from transversal_search import STRATA, Stratum


Array = np.ndarray
Triangle = Tuple[int, int, int]
PointIndex = Tuple[int, int]

TRIPLES = np.array(tuple(combinations(range(12), 3)), dtype=int)
DEFAULT_SEEDS = (2026081601, 2026081602, 2026081603, 2026081604)
_INCUMBENT_POINTS = np.asarray(decimal_verifier.points(80), dtype=float)
UPPER_AREA_BOUND = float(area_upper_bound(12))


@dataclass(frozen=True)
class Trial:
    """One free-coordinate numerical trial for a fixed active transversal."""

    stratum: str
    support: Tuple[int, ...]
    seed: int
    differential_evolution_area: float
    epigraph_area: float
    epigraph_success: bool
    nfev: int
    selected_stage: str
    minimum_area: float
    active_triangles: Tuple[Triangle, ...]
    points: Tuple[Tuple[float, float], ...]


def parameter_coordinates(stratum: Stratum) -> Tuple[PointIndex, ...]:
    """Return both free coordinates for every label in the moved support."""

    return tuple((label, axis) for label in stratum.moved_labels for axis in range(2))


def configuration(stratum: Stratum, parameters: Array) -> Array:
    """Embed a ten-dimensional moved-support vector into the fixed complement."""

    coordinates = parameter_coordinates(stratum)
    values = np.asarray(parameters, dtype=float)
    if values.shape != (len(coordinates),):
        raise ValueError(f"{stratum.name} expects {len(coordinates)} free coordinates")
    points = _INCUMBENT_POINTS.copy()
    for value, (label, axis) in zip(values, coordinates):
        points[label, axis] = value
    return points


def incumbent_parameters(stratum: Stratum) -> Array:
    """Extract the exact-record float coordinates for a round-trip check."""

    return np.asarray([_INCUMBENT_POINTS[label, axis] for label, axis in parameter_coordinates(stratum)], dtype=float)


def signed_areas(points: Array) -> Array:
    """Return all 220 oriented ordinary areas."""

    first = points[TRIPLES[:, 0]]
    second = points[TRIPLES[:, 1]]
    third = points[TRIPLES[:, 2]]
    return (
        (second[:, 0] - first[:, 0]) * (third[:, 1] - first[:, 1])
        - (second[:, 1] - first[:, 1]) * (third[:, 0] - first[:, 0])
    ) / 2.0


def minimum_area(points: Array) -> float:
    """Return the actual geometric minimum rather than a reported epigraph."""

    return float(np.min(np.abs(signed_areas(points))))


def active_triangles(points: Array, tolerance: float = 1e-9) -> Tuple[Triangle, ...]:
    """Return triangles numerically tied with the current minimum."""

    areas = np.abs(signed_areas(points))
    minimum = float(np.min(areas))
    return tuple(tuple(int(value) for value in triangle) for triangle, area in zip(TRIPLES, areas) if area <= minimum + tolerance)


def epigraph_polish(stratum: Stratum, parameters: Array) -> Tuple[float, Array, bool]:
    """Maximize the epigraph inside the sign cell discovered by one trial."""

    initial_points = configuration(stratum, parameters)
    signs = np.where(signed_areas(initial_points) >= 0.0, 1.0, -1.0)
    start = np.append(parameters, minimum_area(initial_points))

    def constraints(vector: Array) -> Array:
        return signs * signed_areas(configuration(stratum, vector[:-1])) - vector[-1]

    polished = minimize(
        lambda vector: -vector[-1],
        start,
        method="SLSQP",
        bounds=[(0.0, 1.0)] * len(parameters) + [(0.0, UPPER_AREA_BOUND)],
        constraints={"type": "ineq", "fun": constraints},
        options={"maxiter": 8000, "ftol": 1e-13},
    )
    if not polished.success:
        return minimum_area(initial_points), parameters, False
    candidate = polished.x[:-1]
    actual = minimum_area(configuration(stratum, candidate))
    return min(float(polished.x[-1]), actual), candidate, True


def select_candidate(
    raw_area: float,
    raw_parameters: Array,
    polished_area: float,
    polished_parameters: Array,
) -> Tuple[str, float, Array]:
    """Associate a reported score with the coordinates that attain it."""

    if polished_area >= raw_area:
        return "epigraph", polished_area, polished_parameters
    return "differential-evolution", raw_area, raw_parameters


def run_trial(stratum: Stratum, seed: int, *, popsize: int = 24, maxiter: int = 2500) -> Trial:
    """Run one full-free-coordinate trial without injecting record coordinates."""

    if not 0 <= seed < 2**32:
        raise ValueError("SciPy differential-evolution seeds must lie in [0, 2**32)")
    dimension = len(parameter_coordinates(stratum))
    result = differential_evolution(
        lambda parameters: -minimum_area(configuration(stratum, parameters)),
        [(0.0, 1.0)] * dimension,
        seed=seed,
        popsize=popsize,
        maxiter=maxiter,
        tol=1e-11,
        polish=False,
        workers=1,
        updating="immediate",
    )
    raw_area = minimum_area(configuration(stratum, result.x))
    polished_area, polished_parameters, polished_success = epigraph_polish(stratum, result.x)
    selected_stage, selected_area, selected_parameters = select_candidate(
        raw_area, result.x, polished_area, polished_parameters
    )
    selected_points = configuration(stratum, selected_parameters)
    selected_area = min(selected_area, minimum_area(selected_points))
    return Trial(
        stratum=stratum.name,
        support=stratum.moved_labels,
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


def _selected_strata(names: Iterable[str]) -> Tuple[Stratum, ...]:
    """Validate that the named representatives remain genuine size-5 transversals."""

    transversals = set(active_hitting_sets(5))
    selected = tuple(STRATA[name] for name in names)
    if any(stratum.moved_labels not in transversals for stratum in selected):
        raise AssertionError("each selected support must hit every active incumbent triangle")
    return selected


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stratum", choices=tuple(STRATA), action="append", help="stratum(s); default is all D4 representatives")
    parser.add_argument("--seed", type=int, action="append", help="explicit seed(s); default is the recorded campaign")
    parser.add_argument("--seed-limit", type=int, help="run only the first N selected seeds")
    parser.add_argument("--popsize", type=int, default=24)
    parser.add_argument("--maxiter", type=int, default=2500)
    parser.add_argument("--snap-bits", type=int, help="exactly audit each selected result after dyadic rounding")
    arguments = parser.parse_args()
    if arguments.popsize <= 0 or arguments.maxiter < 0:
        raise ValueError("popsize must be positive and maxiter must be nonnegative")
    selected = _selected_strata(arguments.stratum or tuple(STRATA))
    seeds = tuple(arguments.seed) if arguments.seed else DEFAULT_SEEDS
    if arguments.seed_limit is not None:
        seeds = seeds[: arguments.seed_limit]
    incumbent = minimum_area(_INCUMBENT_POINTS)
    print(f"incumbent={incumbent:.18f} global_upper_bound={UPPER_AREA_BOUND:.18f}")
    for stratum in selected:
        print(f"stratum={stratum.name} support={stratum.moved_labels} dimensions={len(parameter_coordinates(stratum))}")
        for seed in seeds:
            trial = run_trial(stratum, seed, popsize=arguments.popsize, maxiter=arguments.maxiter)
            points = np.asarray(trial.points, dtype=float)
            print(
                f"  seed={trial.seed} de={trial.differential_evolution_area:.18f} "
                f"epigraph={trial.epigraph_area:.18f} epigraph_success={trial.epigraph_success} "
                f"selected={trial.selected_stage} minimum={trial.minimum_area:.18f} "
                f"gap={trial.minimum_area - incumbent:+.3e} active={len(trial.active_triangles)} nfev={trial.nfev}"
            )
            print(f"    points={trial.points}")
            print("    classification=NUMERICAL_DISCOVERY_ONLY")
            if arguments.snap_bits is not None:
                report = exact_snap_report(points, arguments.snap_bits)
                print(
                    f"    dyadic_bits={report.bits} exact_minimum={report.minimum_area} "
                    f"strictly_beats_incumbent={report.strictly_beats_incumbent} active={len(report.active_triangles)}"
                )


if __name__ == "__main__":
    main()
