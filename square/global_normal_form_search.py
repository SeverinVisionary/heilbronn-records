"""Reproducible unrestricted numerical discovery in the five-boundary form.

This search ranges over all 19 free coordinates in the five-boundary normal
form used by :mod:`global_mccormick_relaxation`: five boundary coordinates,
then seven ordered free x-coordinates and seven free y-coordinates.  It is
therefore materially broader than the frozen-boundary and D4-support searches.

Differential evolution receives no incumbent coordinates.  After it discovers
an orientation cell, an explicit epigraph SLSQP solve polishes that cell.  This
is a numerical discovery tool only: a floating score is never reported as a
new record.  An optional dyadic snap is checked by ``incumbent.py`` in exact
``Fraction`` arithmetic before any strict-improvement statement is made.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations
from typing import Sequence, Tuple

import numpy as np
from scipy.optimize import differential_evolution, minimize

import decimal_verifier
from global_mccormick_relaxation import CANONICAL_INCUMBENT_LABELS, area_upper_bound
from incumbent import Qx, incumbent_value, sign, verify_rational_candidate


Array = np.ndarray
Triangle = Tuple[int, int, int]
RationalPoint = Tuple[Fraction, Fraction]

TRIPLES = np.array(tuple(combinations(range(12), 3)), dtype=int)
DEFAULT_SEEDS = (2026081601, 2026081602, 2026081603, 2026081604)
UPPER_AREA_BOUND = float(area_upper_bound(12))

# The variable order is deliberately explicit so a trial can be reconstructed
# without relying on an implicit reshape convention.
PARAMETER_COORDINATES: Tuple[Tuple[str, int], ...] = (
    ("y", 0),
    ("x", 1),
    ("y", 2),
    ("x", 3),
    ("y", 4),
    *(("x", index) for index in range(5, 12)),
    *(("y", index) for index in range(5, 12)),
)
PARAMETER_COUNT = len(PARAMETER_COORDINATES)
if PARAMETER_COUNT != 19:
    raise AssertionError("the n=12 five-boundary normal form has 19 free coordinates")


@dataclass(frozen=True)
class Trial:
    """One independently seeded numerical search outcome."""

    seed: int
    differential_evolution_area: float
    epigraph_area: float
    epigraph_success: bool
    nfev: int
    selected_stage: str
    minimum_area: float
    active_triangles: Tuple[Triangle, ...]
    points: Tuple[Tuple[float, float], ...]


@dataclass(frozen=True)
class SnapReport:
    """Exact result after an explicitly requested dyadic snap."""

    bits: int
    minimum_area: Fraction
    active_triangles: Tuple[Triangle, ...]
    strictly_beats_incumbent: bool
    points: Tuple[RationalPoint, ...]


def canonical_incumbent_points() -> Array:
    """Return the independent Decimal reconstruction in normal-form labels."""

    points = np.asarray(decimal_verifier.points(80), dtype=float)
    return points[np.asarray(CANONICAL_INCUMBENT_LABELS, dtype=int)].copy()


def normalize_parameters(parameters: Array) -> Array:
    """Map a unit-cube vector onto the canonical ordering domain.

    Sorting does not discard a normal-form configuration: points 5 through 11
    are labelled only after their x-order is selected, and the two paired
    boundary orderings are represented by their sorted values.  This decoder
    lets differential evolution remain box-constrained rather than giving it
    a penalty for every intermediate ordering violation.
    """

    result = np.asarray(parameters, dtype=float).copy()
    if result.shape != (PARAMETER_COUNT,):
        raise ValueError(f"normal form requires exactly {PARAMETER_COUNT} parameters")
    result[[0, 4]] = np.sort(result[[0, 4]])  # y_0 <= y_4
    result[[1, 3]] = np.sort(result[[1, 3]])  # x_1 <= x_3
    result[5:12] = np.sort(result[5:12])  # x_5 <= ... <= x_11
    return result


def configuration(parameters: Array, *, normalize: bool = False) -> Array:
    """Embed a free vector into twelve points with the five required pins."""

    values = normalize_parameters(parameters) if normalize else np.asarray(parameters, dtype=float)
    if values.shape != (PARAMETER_COUNT,):
        raise ValueError(f"normal form requires exactly {PARAMETER_COUNT} parameters")
    points = np.zeros((12, 2), dtype=float)
    points[2, 0] = 1.0
    points[3, 1] = 1.0
    for value, (axis, index) in zip(values, PARAMETER_COORDINATES):
        points[index, 0 if axis == "x" else 1] = value
    return points


def parameters_for_points(points: Array) -> Array:
    """Extract the 19 free coordinates from an already normalized point set."""

    values = np.asarray(points, dtype=float)
    if values.shape != (12, 2):
        raise ValueError("a normal-form configuration must have shape (12, 2)")
    if not is_normal_form(values):
        raise ValueError("points do not satisfy the five-boundary normal form")
    return np.asarray([values[index, 0 if axis == "x" else 1] for axis, index in PARAMETER_COORDINATES], dtype=float)


def normal_form_slacks(points: Array) -> Array:
    """Return the nine ordering slacks, all nonnegative in normal form."""

    values = np.asarray(points, dtype=float)
    if values.shape != (12, 2):
        raise ValueError("a normal-form configuration must have shape (12, 2)")
    return np.concatenate(
        (
            np.asarray((values[3, 0] - values[1, 0], values[4, 1] - values[0, 1])),
            np.diff(values[4:, 0]),
        )
    )


def is_normal_form(points: Array, tolerance: float = 1e-12) -> bool:
    """Check pins, square containment, and every canonical ordering."""

    values = np.asarray(points, dtype=float)
    if values.shape != (12, 2):
        return False
    pins = ((0, 0, 0.0), (1, 1, 0.0), (2, 0, 1.0), (3, 1, 1.0), (4, 0, 0.0))
    return bool(
        np.all(values >= -tolerance)
        and np.all(values <= 1.0 + tolerance)
        and all(abs(values[index, axis] - expected) <= tolerance for index, axis, expected in pins)
        and np.all(normal_form_slacks(values) >= -tolerance)
    )


def signed_areas(points: Array) -> Array:
    """Return the 220 oriented ordinary areas in lexicographic triangle order."""

    first = points[TRIPLES[:, 0]]
    second = points[TRIPLES[:, 1]]
    third = points[TRIPLES[:, 2]]
    return (
        (second[:, 0] - first[:, 0]) * (third[:, 1] - first[:, 1])
        - (second[:, 1] - first[:, 1]) * (third[:, 0] - first[:, 0])
    ) / 2.0


def minimum_area(points: Array) -> float:
    """Return the actual geometric minimum, never the epigraph variable alone."""

    return float(np.min(np.abs(signed_areas(points))))


def active_triangles(points: Array, tolerance: float = 1e-9) -> Tuple[Triangle, ...]:
    """Return all triangles within a numerical tie tolerance of the minimum."""

    areas = np.abs(signed_areas(points))
    minimum = float(np.min(areas))
    return tuple(tuple(int(value) for value in triangle) for triangle, area in zip(TRIPLES, areas) if area <= minimum + tolerance)


def epigraph_polish(parameters: Array) -> Tuple[float, Array, bool]:
    """Polish one discovered sign cell with a constrained epigraph solve."""

    start_parameters = normalize_parameters(parameters)
    initial_points = configuration(start_parameters)
    signs = np.where(signed_areas(initial_points) >= 0.0, 1.0, -1.0)
    start = np.append(start_parameters, minimum_area(initial_points))

    def constraints(vector: Array) -> Array:
        points = configuration(vector[:-1])
        return np.concatenate((signs * signed_areas(points) - vector[-1], normal_form_slacks(points)))

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
    if not is_normal_form(candidate_points, tolerance=1e-8):
        return minimum_area(initial_points), start_parameters, False
    actual = minimum_area(candidate_points)
    return min(float(polished.x[-1]), actual), candidate, True


def select_candidate(
    raw_area: float,
    raw_parameters: Array,
    polished_area: float,
    polished_parameters: Array,
) -> Tuple[str, float, Array]:
    """Keep the parameters that attain the score selected for a trial."""

    if polished_area >= raw_area:
        return "epigraph", polished_area, polished_parameters
    return "differential-evolution", raw_area, raw_parameters


def run_trial(seed: int, *, popsize: int = 20, maxiter: int = 2000) -> Trial:
    """Run one random-start full-normal-form discovery trial.

    The raw differential-evolution vector is decoded into the normal form, so
    the optimizer receives neither incumbent coordinates nor an incumbent
    objective value.
    """

    if not 0 <= seed < 2**32:
        raise ValueError("SciPy differential-evolution seeds must lie in [0, 2**32)")
    result = differential_evolution(
        lambda vector: -minimum_area(configuration(vector, normalize=True)),
        [(0.0, 1.0)] * PARAMETER_COUNT,
        seed=seed,
        popsize=popsize,
        maxiter=maxiter,
        tol=1e-11,
        polish=False,
        workers=1,
        updating="immediate",
    )
    raw_parameters = normalize_parameters(result.x)
    raw_area = minimum_area(configuration(raw_parameters))
    polished_area, polished_parameters, polished_success = epigraph_polish(raw_parameters)
    selected_stage, selected_area, selected_parameters = select_candidate(
        raw_area, raw_parameters, polished_area, polished_parameters
    )
    selected_points = configuration(selected_parameters)
    # A defense against reporting a stale epigraph value after numerical noise.
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


def dyadic_snap(points: Array, bits: int) -> Tuple[RationalPoint, ...]:
    """Round a floating point set to a dyadic grid for an exact audit."""

    if bits <= 0:
        raise ValueError("dyadic precision must be positive")
    denominator = 1 << bits
    values = np.asarray(points, dtype=float)
    if values.shape != (12, 2):
        raise ValueError("a candidate must have shape (12, 2)")
    return tuple(
        (Fraction(int(np.rint(x * denominator)), denominator), Fraction(int(np.rint(y * denominator)), denominator))
        for x, y in values
    )


def exact_snap_report(points: Array, bits: int) -> SnapReport:
    """Run the existing exact candidate verifier on an explicit dyadic snap."""

    snapped = dyadic_snap(points, bits)
    minimum, active = verify_rational_candidate(snapped)
    beats = sign(Qx.rational(minimum) - incumbent_value()) > 0
    return SnapReport(bits, minimum, active, beats, snapped)


def _format_trial(trial: Trial, incumbent: float) -> str:
    """Render enough provenance to rerun and independently inspect a trial."""

    return (
        f"seed={trial.seed} de={trial.differential_evolution_area:.18f} "
        f"epigraph={trial.epigraph_area:.18f} epigraph_success={trial.epigraph_success} "
        f"selected={trial.selected_stage} minimum={trial.minimum_area:.18f} "
        f"gap={trial.minimum_area - incumbent:+.3e} active={len(trial.active_triangles)} nfev={trial.nfev}"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, action="append", help="explicit seed(s); default is the recorded campaign")
    parser.add_argument("--seed-limit", type=int, help="run only the first N selected seeds")
    parser.add_argument("--popsize", type=int, default=20)
    parser.add_argument("--maxiter", type=int, default=2000)
    parser.add_argument("--snap-bits", type=int, help="exactly audit each selected result after dyadic rounding")
    arguments = parser.parse_args()
    if arguments.popsize <= 0 or arguments.maxiter < 0:
        raise ValueError("popsize must be positive and maxiter must be nonnegative")
    seeds = tuple(arguments.seed) if arguments.seed else DEFAULT_SEEDS
    if arguments.seed_limit is not None:
        seeds = seeds[: arguments.seed_limit]
    incumbent = float(decimal_verifier.analysis(80)[0])
    baseline = canonical_incumbent_points()
    print(f"incumbent={incumbent:.18f}")
    print(f"normal_form_dimension={PARAMETER_COUNT} baseline_minimum={minimum_area(baseline):.18f}")
    for seed in seeds:
        trial = run_trial(seed, popsize=arguments.popsize, maxiter=arguments.maxiter)
        points = np.asarray(trial.points, dtype=float)
        print(_format_trial(trial, incumbent))
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
