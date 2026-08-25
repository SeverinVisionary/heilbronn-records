"""Seeded calibration gate for the structured Heilbronn search pipeline.

The optimizer receives only a symmetry/boundary template and random seeds;
published coordinates are used solely by the regression tests below.  Passing
this gate demonstrates that the nonsmooth epigraph search can recover known
lower-n basins before it is used to rank any n=12 candidate.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from itertools import combinations
from math import sqrt
from typing import Callable, Dict, Sequence, Tuple

import numpy as np
from scipy.optimize import differential_evolution, minimize


Array = np.ndarray
Template = Callable[[Array], Array]


@dataclass(frozen=True)
class CalibrationCase:
    name: str
    n: int
    dimensions: int
    target: float
    tolerance: float
    template: Template
    seeds: Tuple[int, ...]
    required_hits: int
    popsize: int
    maxiter: int


@dataclass(frozen=True)
class Trial:
    seed: int
    differential_evolution_area: float
    epigraph_area: float
    nfev: int

    @property
    def area(self) -> float:
        return max(self.differential_evolution_area, self.epigraph_area)


def n8_template(parameters: Array) -> Array:
    """C2-symmetric n=8 template: six boundary points and an interior pair."""
    a, b, e, f = parameters
    return np.array(
        (
            (0.0, 0.0),
            (a, 0.0),
            (1.0, b),
            (1.0, 1.0),
            (0.0, 1.0 - b),
            (1.0 - a, 1.0),
            (e, f),
            (1.0 - e, 1.0 - f),
        ),
        dtype=float,
    )


def n9_template(parameters: Array) -> Array:
    """Anti-diagonal-reflection n=9 template with one fixed-axis interior point."""
    a, b, c, d, e = parameters
    return np.array(
        (
            (0.0, a),
            (1.0 - a, 1.0),
            (b, 0.0),
            (1.0, 1.0 - b),
            (1.0, c),
            (1.0 - c, 0.0),
            (d, 1.0),
            (0.0, 1.0 - d),
            (e, 1.0 - e),
        ),
        dtype=float,
    )


def n10_template(parameters: Array) -> Array:
    """C2-symmetric n=10 template: four boundary pairs and one interior pair."""
    a, b, c, d, e, f = parameters
    return np.array(
        (
            (a, 0.0),
            (1.0 - a, 1.0),
            (b, 0.0),
            (1.0 - b, 1.0),
            (0.0, c),
            (1.0, 1.0 - c),
            (1.0, d),
            (0.0, 1.0 - d),
            (e, f),
            (1.0 - e, 1.0 - f),
        ),
        dtype=float,
    )


CASES: Dict[str, CalibrationCase] = {
    "n8": CalibrationCase(
        name="n8",
        n=8,
        dimensions=4,
        target=(sqrt(13.0) - 1.0) / 36.0,
        tolerance=1e-9,
        template=n8_template,
        seeds=(20260816, 20260817, 20260818),
        required_hits=2,
        popsize=18,
        maxiter=700,
    ),
    "n9": CalibrationCase(
        name="n9",
        n=9,
        dimensions=5,
        target=(9.0 * sqrt(65.0) - 55.0) / 320.0,
        tolerance=1e-9,
        template=n9_template,
        seeds=(20260816, 20260817, 20260818, 20260819),
        required_hits=2,
        popsize=24,
        maxiter=2000,
    ),
    "n10": CalibrationCase(
        name="n10",
        n=10,
        dimensions=6,
        target=0.046537419582541775,
        tolerance=1e-9,
        template=n10_template,
        seeds=(20260816, 20260817, 20260818, 20260819),
        required_hits=3,
        popsize=24,
        maxiter=2500,
    ),
}


def triples(n: int) -> Array:
    return np.array(tuple(combinations(range(n), 3)), dtype=int)


def signed_areas(points: Array, triple_indices: Array) -> Array:
    first = points[triple_indices[:, 0]]
    second = points[triple_indices[:, 1]]
    third = points[triple_indices[:, 2]]
    return (
        (second[:, 0] - first[:, 0]) * (third[:, 1] - first[:, 1])
        - (second[:, 1] - first[:, 1]) * (third[:, 0] - first[:, 0])
    ) / 2.0


def minimum_area(parameters: Array, template: Template, triple_indices: Array) -> float:
    return float(np.min(np.abs(signed_areas(template(parameters), triple_indices))))


def epigraph_polish(parameters: Array, template: Template, triple_indices: Array) -> float:
    """Polish within the discovered orientation cell using an explicit epigraph."""
    signs = np.where(signed_areas(template(parameters), triple_indices) >= 0.0, 1.0, -1.0)
    start = np.append(parameters, minimum_area(parameters, template, triple_indices))

    def constraints(vector: Array) -> Array:
        return signs * signed_areas(template(vector[:-1]), triple_indices) - vector[-1]

    polished = minimize(
        lambda vector: -vector[-1],
        start,
        method="SLSQP",
        bounds=[(0.0, 1.0)] * len(start),
        constraints={"type": "ineq", "fun": constraints},
        options={"maxiter": 3000, "ftol": 1e-13},
    )
    if not polished.success:
        return minimum_area(parameters, template, triple_indices)
    return min(float(polished.x[-1]), minimum_area(polished.x[:-1], template, triple_indices))


def run_trial(case: CalibrationCase, seed: int) -> Trial:
    triple_indices = triples(case.n)
    result = differential_evolution(
        lambda vector: -minimum_area(vector, case.template, triple_indices),
        [(0.0, 1.0)] * case.dimensions,
        seed=seed,
        popsize=case.popsize,
        maxiter=case.maxiter,
        tol=1e-11,
        polish=True,
        workers=1,
        updating="immediate",
    )
    differential_evolution_area = minimum_area(result.x, case.template, triple_indices)
    return Trial(
        seed=seed,
        differential_evolution_area=differential_evolution_area,
        epigraph_area=epigraph_polish(result.x, case.template, triple_indices),
        nfev=result.nfev,
    )


def run_case(case: CalibrationCase, seed_limit: int | None = None) -> Tuple[Trial, ...]:
    seeds = case.seeds if seed_limit is None else case.seeds[:seed_limit]
    return tuple(run_trial(case, seed) for seed in seeds)


def passes(case: CalibrationCase, trials: Sequence[Trial]) -> bool:
    return sum(trial.area >= case.target - case.tolerance for trial in trials) >= case.required_hits


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", choices=tuple(CASES), action="append", help="case(s) to run; default is all")
    parser.add_argument("--seed-limit", type=int, help="run only the first N recorded seeds")
    arguments = parser.parse_args()
    selected = arguments.case or tuple(CASES)
    all_passed = True
    for name in selected:
        case = CASES[name]
        outcomes = run_case(case, arguments.seed_limit)
        hit_count = sum(outcome.area >= case.target - case.tolerance for outcome in outcomes)
        print(f"{case.name}: target={case.target:.15f} hits={hit_count}/{len(outcomes)}")
        for outcome in outcomes:
            print(
                f"  seed={outcome.seed} de={outcome.differential_evolution_area:.15f} "
                f"epigraph={outcome.epigraph_area:.15f} nfev={outcome.nfev}"
            )
        passed = passes(case, outcomes)
        print(f"  gate={'PASS' if passed else 'FAIL'}")
        all_passed = all_passed and passed
    if not all_passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
