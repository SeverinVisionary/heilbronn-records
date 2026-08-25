"""Structured discovery search for the three D4 classes of size-5 supports.

The fixed complement is the exact Comellas--Yebra configuration.  Each moved
boundary point remains on its original edge in this first pass, while moved
interior points are free in the unit square.  This is a deliberately named,
restricted numerical discovery stream, not a global no-go proof and not a
record certificate.  Any apparent improvement must be independently enclosed
or converted to exact coordinates before it can be reported as a witness.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from itertools import combinations
from typing import Dict, Iterable, Sequence, Tuple

import numpy as np
from scipy.optimize import differential_evolution, minimize

import decimal_verifier
from incumbent import active_hitting_sets


PointIndex = Tuple[int, int]
TRIPLES = np.array(tuple(combinations(range(12), 3)), dtype=int)
DEFAULT_SEEDS = (2026081601, 2026081602, 2026081603, 2026081604)
_INCUMBENT_POINTS = np.asarray(decimal_verifier.points(80), dtype=float)


@dataclass(frozen=True)
class Stratum:
    """A fixed-complement, edge-locked moved-label support."""

    name: str
    moved_labels: Tuple[int, ...]
    description: str

    @property
    def parameter_coordinates(self) -> Tuple[PointIndex, ...]:
        coordinates = []
        for label in self.moved_labels:
            if label < 4:
                coordinates.append((label, 0))  # bottom/top edge: x is free.
            elif label < 8:
                coordinates.append((label, 1))  # left/right edge: y is free.
            else:
                coordinates.extend(((label, 0), (label, 1)))
        return tuple(coordinates)

    @property
    def dimensions(self) -> int:
        return len(self.parameter_coordinates)


STRATA: Dict[str, Stratum] = {
    "four-interiors-plus-boundary": Stratum(
        "four-interiors-plus-boundary",
        (0, 8, 9, 10, 11),
        "one boundary point plus all four interiors (9 edge-locked variables)",
    ),
    "two-boundary-three-interior-a": Stratum(
        "two-boundary-three-interior-a",
        (0, 2, 8, 10, 11),
        "minimal support {0,2,8,10,11} (8 edge-locked variables)",
    ),
    "two-boundary-three-interior-b": Stratum(
        "two-boundary-three-interior-b",
        (0, 5, 9, 10, 11),
        "minimal support {0,5,9,10,11} (8 edge-locked variables)",
    ),
}


@dataclass(frozen=True)
class Trial:
    stratum: str
    seed: int
    differential_evolution_area: float
    epigraph_area: float
    nfev: int
    selected_stage: str
    minimum_area: float
    orbit_distance: float
    active_triangles: Tuple[Tuple[int, int, int], ...]
    points: Tuple[Tuple[float, float], ...]

    @property
    def classification(self) -> str:
        return "incumbent-orbit" if self.orbit_distance <= 1e-8 else "distinct-topology"


def incumbent_parameters(stratum: Stratum) -> np.ndarray:
    """Return the stratum parameters of the incumbent itself."""

    return np.array([_INCUMBENT_POINTS[label, coordinate] for label, coordinate in stratum.parameter_coordinates])


def configuration(stratum: Stratum, parameters: np.ndarray) -> np.ndarray:
    """Embed an edge-locked stratum parameter vector into twelve points."""

    if len(parameters) != stratum.dimensions:
        raise ValueError(f"{stratum.name} expects {stratum.dimensions} parameters")
    points = _INCUMBENT_POINTS.copy()
    for value, (label, coordinate) in zip(parameters, stratum.parameter_coordinates):
        points[label, coordinate] = value
    return points


def signed_areas(points: np.ndarray) -> np.ndarray:
    first = points[TRIPLES[:, 0]]
    second = points[TRIPLES[:, 1]]
    third = points[TRIPLES[:, 2]]
    return (
        (second[:, 0] - first[:, 0]) * (third[:, 1] - first[:, 1])
        - (second[:, 1] - first[:, 1]) * (third[:, 0] - first[:, 0])
    ) / 2.0


def minimum_area(points: np.ndarray) -> float:
    return float(np.min(np.abs(signed_areas(points))))


def active_triangles(points: np.ndarray, tolerance: float = 1e-9) -> Tuple[Tuple[int, int, int], ...]:
    areas = np.abs(signed_areas(points))
    minimum = float(np.min(areas))
    return tuple(tuple(int(index) for index in triple) for triple, area in zip(TRIPLES, areas) if area <= minimum + tolerance)


def epigraph_polish(stratum: Stratum, parameters: np.ndarray) -> Tuple[float, np.ndarray]:
    """Polish only inside the orientation cell chosen by differential evolution."""

    initial_points = configuration(stratum, parameters)
    signs = np.where(signed_areas(initial_points) >= 0.0, 1.0, -1.0)
    start = np.append(parameters, minimum_area(initial_points))

    def constraints(vector: np.ndarray) -> np.ndarray:
        points = configuration(stratum, vector[:-1])
        return signs * signed_areas(points) - vector[-1]

    polished = minimize(
        lambda vector: -vector[-1],
        start,
        method="SLSQP",
        bounds=[(0.0, 1.0)] * len(start),
        constraints={"type": "ineq", "fun": constraints},
        options={"maxiter": 4000, "ftol": 1e-13},
    )
    if not polished.success:
        return minimum_area(initial_points), parameters
    candidate = polished.x[:-1]
    return min(float(polished.x[-1]), minimum_area(configuration(stratum, candidate))), candidate


def select_candidate(
    raw_area: float,
    raw_parameters: np.ndarray,
    polished_area: float,
    polished_parameters: np.ndarray,
) -> Tuple[str, float, np.ndarray]:
    """Keep the coordinates associated with the score that is reported."""

    if polished_area >= raw_area:
        return "epigraph", polished_area, polished_parameters
    return "de", raw_area, raw_parameters


def _d4_images(points: np.ndarray) -> Tuple[np.ndarray, ...]:
    x = points[:, 0]
    y = points[:, 1]
    return (
        np.column_stack((x, y)),
        np.column_stack((1.0 - y, x)),
        np.column_stack((1.0 - x, 1.0 - y)),
        np.column_stack((y, 1.0 - x)),
        np.column_stack((1.0 - x, y)),
        np.column_stack((x, 1.0 - y)),
        np.column_stack((y, x)),
        np.column_stack((1.0 - y, 1.0 - x)),
    )


def _has_perfect_matching(adjacency: Sequence[Sequence[int]], right_size: int) -> bool:
    """Kuhn matching, adequate for the twelve-point bottleneck check."""

    matched = [-1] * right_size

    def augment(left: int, seen: set[int]) -> bool:
        for right in adjacency[left]:
            if right in seen:
                continue
            seen.add(right)
            if matched[right] == -1 or augment(matched[right], seen):
                matched[right] = left
                return True
        return False

    return all(augment(left, set()) for left in range(len(adjacency)))


def _bottleneck_distance(left: np.ndarray, right: np.ndarray) -> float:
    distances = np.max(np.abs(left[:, np.newaxis, :] - right[np.newaxis, :, :]), axis=2)
    candidates = np.unique(distances)
    low, high = 0, len(candidates) - 1
    while low < high:
        midpoint = (low + high) // 2
        threshold = candidates[midpoint]
        adjacency = [tuple(int(index) for index in np.flatnonzero(row <= threshold)) for row in distances]
        if _has_perfect_matching(adjacency, len(right)):
            high = midpoint
        else:
            low = midpoint + 1
    return float(candidates[low])


def incumbent_orbit_distance(points: np.ndarray) -> float:
    """Unlabeled bottleneck distance to the incumbent, modulo D4."""

    return min(_bottleneck_distance(points, image) for image in _d4_images(_INCUMBENT_POINTS))


def run_trial(stratum: Stratum, seed: int, popsize: int = 30, maxiter: int = 3000) -> Trial:
    result = differential_evolution(
        lambda parameters: -minimum_area(configuration(stratum, parameters)),
        [(0.0, 1.0)] * stratum.dimensions,
        seed=seed,
        popsize=popsize,
        maxiter=maxiter,
        tol=1e-11,
        polish=True,
        workers=1,
        updating="immediate",
    )
    raw_area = minimum_area(configuration(stratum, result.x))
    polished_area, polished_parameters = epigraph_polish(stratum, result.x)
    selected_stage, selected_area, selected_parameters = select_candidate(
        raw_area,
        result.x,
        polished_area,
        polished_parameters,
    )
    selected_points = configuration(stratum, selected_parameters)
    return Trial(
        stratum=stratum.name,
        seed=seed,
        differential_evolution_area=raw_area,
        epigraph_area=polished_area,
        nfev=result.nfev,
        selected_stage=selected_stage,
        minimum_area=selected_area,
        orbit_distance=incumbent_orbit_distance(selected_points),
        active_triangles=active_triangles(selected_points),
        points=tuple(tuple(float(value) for value in point) for point in selected_points),
    )


def _validate_strata() -> None:
    transversals = set(active_hitting_sets(5))
    if any(stratum.moved_labels not in transversals for stratum in STRATA.values()):
        raise AssertionError("every declared size-5 support must hit the active hypergraph")


def _selected_strata(names: Iterable[str]) -> Tuple[Stratum, ...]:
    selected = tuple(STRATA[name] for name in names)
    _validate_strata()
    return selected


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stratum", choices=tuple(STRATA), action="append", help="stratum(s) to run; default is all")
    parser.add_argument("--seed", type=int, action="append", help="explicit seed(s); default is the recorded seed set")
    parser.add_argument("--seed-limit", type=int, help="run only the first N selected seeds")
    parser.add_argument("--popsize", type=int, default=30)
    parser.add_argument("--maxiter", type=int, default=3000)
    arguments = parser.parse_args()
    selected = _selected_strata(arguments.stratum or tuple(STRATA))
    seeds = tuple(arguments.seed) if arguments.seed else DEFAULT_SEEDS
    if arguments.seed_limit is not None:
        seeds = seeds[:arguments.seed_limit]
    incumbent = minimum_area(_INCUMBENT_POINTS)
    print(f"incumbent={incumbent:.18f}")
    for stratum in selected:
        print(f"stratum={stratum.name} support={stratum.moved_labels} dimensions={stratum.dimensions}")
        for seed in seeds:
            trial = run_trial(stratum, seed, arguments.popsize, arguments.maxiter)
            print(
                f"  seed={trial.seed} de={trial.differential_evolution_area:.18f} "
                f"epigraph={trial.epigraph_area:.18f} selected={trial.selected_stage} "
                f"minimum={trial.minimum_area:.18f} gap={trial.minimum_area - incumbent:+.3e} "
                f"orbit_distance={trial.orbit_distance:.3e} class={trial.classification} "
                f"active={len(trial.active_triangles)} nfev={trial.nfev}"
            )
            print(f"    points={trial.points}")


if __name__ == "__main__":
    main()
