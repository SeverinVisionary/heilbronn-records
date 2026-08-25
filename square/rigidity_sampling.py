"""Near-record sampling of active hypergraphs (Part B of the rigidity teeth test).

Every number printed by this module is descriptive floating-point statistics
about independently optimized numerical samples.  Nothing here is exact, no
sample is a candidate record, and no exactness claim may be quoted from this
output.  See RIGIDITY_CORE_SPEC_2026-08-20.md for the protocol and the
teeth/kill criteria this feeds.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from itertools import combinations
from typing import Dict, List, Sequence, Tuple

import numpy as np

import global_normal_form_search as gnfs
from incumbent import algebraic_bounds, incumbent_analysis, incumbent_points, incumbent_value

Triangle = Tuple[int, int, int]

# The eight square symmetries as coordinate maps applied to a point array.
D4_COORDINATE_MAPS = (
    lambda p: p,
    lambda p: np.stack([1.0 - p[:, 0], p[:, 1]], axis=1),
    lambda p: np.stack([p[:, 0], 1.0 - p[:, 1]], axis=1),
    lambda p: 1.0 - p,
    lambda p: p[:, ::-1].copy(),
    lambda p: np.stack([1.0 - p[:, 1], p[:, 0]], axis=1),
    lambda p: np.stack([p[:, 1], 1.0 - p[:, 0]], axis=1),
    lambda p: np.stack([1.0 - p[:, 1], 1.0 - p[:, 0]], axis=1),
)

ALL_TRIANGLES: Tuple[Triangle, ...] = tuple(combinations(range(12), 3))


@dataclass(frozen=True)
class Sample:
    """One kept near-record sample with its incumbent-frame interpretation."""

    seed: int
    minimum_area: float
    match_distance: float
    matched: bool
    near_active_incumbent_labels: Dict[float, Tuple[Triangle, ...]]
    near_active_raw: Dict[float, Tuple[Triangle, ...]]


def incumbent_float_points() -> np.ndarray:
    """Float midpoints of the exact incumbent, in the original labels."""

    rows = []
    for x_value, y_value in incumbent_points():
        x_lower, x_upper = algebraic_bounds(x_value, 96)
        y_lower, y_upper = algebraic_bounds(y_value, 96)
        rows.append((float((x_lower + x_upper) / 2), float((y_lower + y_upper) / 2)))
    return np.asarray(rows, dtype=float)


def match_to_incumbent(points: np.ndarray, incumbent: np.ndarray) -> Tuple[float, Tuple[int, ...]]:
    """Best assignment distance to any D4 image of the incumbent.

    Returns the summed squared assignment distance and the label map sending
    each sample index to an incumbent label (of the best D4 image).
    """

    from scipy.optimize import linear_sum_assignment

    best_cost = float("inf")
    best_map: Tuple[int, ...] = tuple(range(12))
    for transform in D4_COORDINATE_MAPS:
        image = transform(incumbent)
        cost = ((points[:, None, :] - image[None, :, :]) ** 2).sum(axis=2)
        rows, columns = linear_sum_assignment(cost)
        total = float(cost[rows, columns].sum())
        if total < best_cost:
            best_cost = total
            mapping = [0] * 12
            for sample_index, incumbent_label in zip(rows, columns):
                mapping[sample_index] = int(incumbent_label)
            best_map = tuple(mapping)
    return best_cost, best_map


def near_active(points: np.ndarray, minimum: float, delta: float) -> Tuple[Triangle, ...]:
    areas = np.abs(gnfs.signed_areas(points))
    return tuple(
        triangle for triangle, area in zip(ALL_TRIANGLES, areas) if area <= minimum + delta
    )


def analyze_sample(
    trial: "gnfs.Trial",
    incumbent: np.ndarray,
    deltas: Sequence[float],
    match_tolerance: float,
) -> Sample:
    points = np.asarray(trial.points, dtype=float)
    distance, label_map = match_to_incumbent(points, incumbent)
    matched = distance <= match_tolerance
    raw: Dict[float, Tuple[Triangle, ...]] = {}
    mapped: Dict[float, Tuple[Triangle, ...]] = {}
    for delta in deltas:
        triangles = near_active(points, trial.minimum_area, delta)
        raw[delta] = triangles
        mapped[delta] = tuple(
            tuple(sorted(label_map[vertex] for vertex in triangle)) for triangle in triangles
        )
    return Sample(trial.seed, trial.minimum_area, distance, matched, mapped, raw)


def run_perturbed_trial(seed: int, *, sigma: float) -> "gnfs.Trial":
    """Perturb the incumbent's parameters and locally re-optimize.

    This generator samples the near-record basin reachable from the
    incumbent's neighborhood; it is NOT independent global optimization
    (blind mode remains the generator for that question).  The returned
    Trial reuses the search module's own polish and stage selection.
    """

    rng = np.random.default_rng(seed)
    base = gnfs.parameters_for_points(gnfs.canonical_incumbent_points())
    start = gnfs.normalize_parameters(
        np.clip(base + rng.normal(0.0, sigma, size=base.shape), 0.0, 1.0)
    )
    raw_area = gnfs.minimum_area(gnfs.configuration(start))
    polished_area, polished_parameters, polished_success = gnfs.epigraph_polish(start)
    stage, area, parameters = gnfs.select_candidate(
        raw_area, start, polished_area, polished_parameters
    )
    points = gnfs.configuration(parameters)
    area = min(area, gnfs.minimum_area(points))
    return gnfs.Trial(
        seed=seed,
        differential_evolution_area=raw_area,
        epigraph_area=polished_area,
        epigraph_success=polished_success,
        nfev=0,
        selected_stage=stage,
        minimum_area=area,
        active_triangles=gnfs.active_triangles(points),
        points=tuple(tuple(float(value) for value in point) for point in points),
    )


def parse_cores(text: str, active: Tuple[Triangle, ...]) -> List[Tuple[Triangle, ...]]:
    """Parse ';'-separated ','-lists of active-triangle indices into triangles."""

    cores = []
    for chunk in filter(None, (piece.strip() for piece in text.split(";"))):
        indices = tuple(int(token) for token in chunk.split(","))
        if any(index < 0 or index >= len(active) for index in indices):
            raise ValueError("core indices must address the 20 active triangles")
        cores.append(tuple(active[index] for index in indices))
    return cores


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trials", type=int, default=100)
    parser.add_argument("--seed-base", type=int, default=2026082001)
    parser.add_argument("--popsize", type=int, default=16)
    parser.add_argument("--maxiter", type=int, default=600)
    parser.add_argument(
        "--threshold-offsets",
        default="1e-4,1e-5,1e-6",
        help="comma-separated offsets below the incumbent value",
    )
    parser.add_argument("--deltas", default="1e-3,1e-4", help="near-active area slack values")
    parser.add_argument(
        "--match-tolerance",
        type=float,
        default=1e-3,
        help="summed squared assignment distance below which a sample counts as the incumbent orbit",
    )
    parser.add_argument(
        "--cores",
        default="",
        help="';'-separated ','-lists of active-triangle indices from the Part A scan",
    )
    parser.add_argument(
        "--seed-mode",
        choices=("blind", "perturbed"),
        default="blind",
        help="blind = independent random-start optimization; perturbed = incumbent + noise, locally polished",
    )
    parser.add_argument(
        "--sigma",
        type=float,
        default=0.02,
        help="perturbation amplitude for --seed-mode perturbed",
    )
    arguments = parser.parse_args()

    incumbent = incumbent_float_points()
    _, active, _ = incumbent_analysis()
    cores = parse_cores(arguments.cores, tuple(active))
    offsets = tuple(float(token) for token in arguments.threshold_offsets.split(","))
    deltas = tuple(float(token) for token in arguments.deltas.split(","))
    lower, upper = algebraic_bounds(incumbent_value(), 96)
    incumbent_float = float((lower + upper) / 2)
    thresholds = tuple(incumbent_float - offset for offset in offsets)

    print("DESCRIPTIVE-ONLY: float statistics; no exactness claims; no candidate records")
    print("incumbent_float", incumbent_float)
    print("thresholds", thresholds)
    print("seed_mode", arguments.seed_mode, "sigma", arguments.sigma if arguments.seed_mode == "perturbed" else "n/a")
    if arguments.seed_mode == "perturbed":
        print("CAVEAT: perturbed mode samples the basin reachable from the incumbent's")
        print("CAVEAT: neighborhood; it is not independent global optimization")
    print("trials", arguments.trials, "popsize", arguments.popsize, "maxiter", arguments.maxiter)

    samples: List[Tuple[float, Sample]] = []
    for index in range(arguments.trials):
        seed = arguments.seed_base + index
        if arguments.seed_mode == "perturbed":
            trial = run_perturbed_trial(seed, sigma=arguments.sigma)
        else:
            trial = gnfs.run_trial(seed, popsize=arguments.popsize, maxiter=arguments.maxiter)
        best_threshold = max(
            (threshold for threshold in thresholds if trial.minimum_area >= threshold),
            default=None,
        )
        if best_threshold is None:
            continue
        sample = analyze_sample(trial, incumbent, deltas, arguments.match_tolerance)
        samples.append((best_threshold, sample))
        print(
            "sample",
            seed,
            "min_area",
            f"{trial.minimum_area:.9f}",
            "best_threshold",
            f"{best_threshold:.9f}",
            "match_distance",
            f"{sample.match_distance:.3e}",
            "matched",
            sample.matched,
        )

    for threshold in thresholds:
        kept = [sample for best, sample in samples if best >= threshold]
        print("threshold", f"{threshold:.9f}", "kept", len(kept), "of", arguments.trials)
        if not kept:
            continue
        matched = [sample for sample in kept if sample.matched]
        print("  matched_to_incumbent_orbit", len(matched))
        distances = sorted(sample.match_distance for sample in kept)
        print(
            "  match_distance_min_median_max",
            f"{distances[0]:.3e}",
            f"{distances[len(distances) // 2]:.3e}",
            f"{distances[-1]:.3e}",
        )
        for delta in deltas:
            active_set = set(active)
            contains_active = sum(
                1
                for sample in matched
                if active_set <= set(sample.near_active_incumbent_labels[delta])
            )
            print("  delta", delta, "matched_samples_covering_all_20_active", contains_active)
            for core_index, core in enumerate(cores):
                covering = sum(
                    1
                    for sample in matched
                    if set(core) <= set(sample.near_active_incumbent_labels[delta])
                )
                print("  delta", delta, "core", core_index, "covered_by", covering, "of", len(matched))
            unmatched = [sample for sample in kept if not sample.matched]
            distinct = {sample.near_active_raw[delta] for sample in unmatched}
            print("  delta", delta, "unmatched_samples", len(unmatched), "distinct_hypergraphs", len(distinct))
            for hypergraph in sorted(distinct)[:5]:
                print("    unmatched_hypergraph_size", len(hypergraph))
    print(
        "status",
        "DESCRIPTIVE: sampling evidence only; rigidity verdicts come from the exact Part A scan",
    )


if __name__ == "__main__":
    main()
