"""Calibrated numerical search with the eight n=12 boundary points fixed.

This is the first high-value reduced stratum from the active-hypergraph audit:
the four interior points are the unique minimum hitting set.  Differential
evolution receives no incumbent coordinates; sign-fixed epigraph polishing is
applied only to the orientation cell it discovers.  Results are exploratory
until a rational candidate passes ``incumbent.strictly_beats_incumbent``.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from itertools import combinations
from typing import Sequence, Tuple

import numpy as np
from scipy.optimize import differential_evolution, minimize

import decimal_verifier


TRIPLES = np.array(tuple(combinations(range(12), 3)), dtype=int)
DEFAULT_SEEDS = (20260816, 20260817, 20260818, 20260819, 20260820, 20260821, 20260822, 20260823)
# Root isolation is intentionally performed once.  Rebuilding these Decimal
# coordinates inside the objective would make a 220-area numerical evaluation
# hundreds of times more expensive than the search itself.
_INCUMBENT_POINTS = np.asarray(decimal_verifier.points(60), dtype=float)


@dataclass(frozen=True)
class Trial:
    seed: int
    differential_evolution_area: float
    epigraph_area: float
    nfev: int
    selected_stage: str
    interior_points: Tuple[Tuple[float, float], ...]

    @property
    def area(self) -> float:
        return max(self.differential_evolution_area, self.epigraph_area)


def incumbent_boundary() -> np.ndarray:
    """The fixed eight boundary coordinates, independently reconstructed."""
    return _INCUMBENT_POINTS[:8]


def incumbent_interior() -> np.ndarray:
    return _INCUMBENT_POINTS[8:].reshape(-1)


def configuration(parameters: np.ndarray) -> np.ndarray:
    return np.vstack((incumbent_boundary(), np.asarray(parameters, dtype=float).reshape(4, 2)))


def signed_areas(parameters: np.ndarray) -> np.ndarray:
    points = configuration(parameters)
    first = points[TRIPLES[:, 0]]
    second = points[TRIPLES[:, 1]]
    third = points[TRIPLES[:, 2]]
    return (
        (second[:, 0] - first[:, 0]) * (third[:, 1] - first[:, 1])
        - (second[:, 1] - first[:, 1]) * (third[:, 0] - first[:, 0])
    ) / 2.0


def minimum_area(parameters: np.ndarray) -> float:
    return float(np.min(np.abs(signed_areas(parameters))))


def epigraph_polish(parameters: np.ndarray) -> Tuple[float, np.ndarray]:
    """Maximize the minimum inside the sign cell selected by a trial."""
    signs = np.where(signed_areas(parameters) >= 0.0, 1.0, -1.0)
    start = np.append(parameters, minimum_area(parameters))

    def constraints(vector: np.ndarray) -> np.ndarray:
        return signs * signed_areas(vector[:-1]) - vector[-1]

    polished = minimize(
        lambda vector: -vector[-1],
        start,
        method="SLSQP",
        bounds=[(0.0, 1.0)] * len(start),
        constraints={"type": "ineq", "fun": constraints},
        options={"maxiter": 3000, "ftol": 1e-13},
    )
    if not polished.success:
        return minimum_area(parameters), parameters
    candidate = polished.x[:-1]
    return min(float(polished.x[-1]), minimum_area(candidate)), candidate


def select_candidate(
    raw_area: float,
    raw_parameters: np.ndarray,
    polished_area: float,
    polished_parameters: np.ndarray,
) -> Tuple[str, np.ndarray]:
    """Return the coordinates that actually attain the reported trial score."""

    if polished_area >= raw_area:
        return "epigraph", polished_parameters
    return "de", raw_parameters


def run_trial(seed: int, popsize: int = 30, maxiter: int = 3000) -> Trial:
    result = differential_evolution(
        lambda parameters: -minimum_area(parameters),
        [(0.0, 1.0)] * 8,
        seed=seed,
        popsize=popsize,
        maxiter=maxiter,
        tol=1e-11,
        polish=True,
        workers=1,
        updating="immediate",
    )
    raw_area = minimum_area(result.x)
    polished_area, polished_parameters = epigraph_polish(result.x)
    selected_stage, selected_parameters = select_candidate(
        raw_area,
        result.x,
        polished_area,
        polished_parameters,
    )
    return Trial(
        seed=seed,
        differential_evolution_area=raw_area,
        epigraph_area=polished_area,
        nfev=result.nfev,
        selected_stage=selected_stage,
        interior_points=tuple(tuple(float(value) for value in point) for point in selected_parameters.reshape(4, 2)),
    )


def run_trials(seeds: Sequence[int]) -> Tuple[Trial, ...]:
    return tuple(run_trial(seed) for seed in seeds)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed-limit", type=int, help="run only the first N recorded seeds")
    parser.add_argument("--seed", type=int, action="append", help="run an explicit seed; may be repeated")
    arguments = parser.parse_args()
    seeds = tuple(arguments.seed) if arguments.seed else DEFAULT_SEEDS
    if arguments.seed_limit is not None:
        seeds = seeds[:arguments.seed_limit]
    incumbent = minimum_area(incumbent_interior())
    print(f"incumbent={incumbent:.18f}")
    for trial in run_trials(seeds):
        print(
            f"seed={trial.seed} de={trial.differential_evolution_area:.18f} "
            f"epigraph={trial.epigraph_area:.18f} selected={trial.selected_stage} "
            f"gap={trial.area - incumbent:+.3e} nfev={trial.nfev}"
        )
        print(f"  interiors={trial.interior_points}")


if __name__ == "__main__":
    main()
