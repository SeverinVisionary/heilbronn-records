"""Exact structure of the minimal rigid cores: stress spaces, intersections, flexes.

Implements the cheap items of the post-review program
(PROFESSOR_REVIEW_2026-08-20_RIGIDITY.md ranks 1, 3, 4): the stress-space
dimension of each minimal core class, the intersection/forcing structure of
the fourteen cores, and the exact first-order flex that appears when each
individually removable triangle is dropped from the full active set.  All
outputs are exact; decimals are display only.
"""

from __future__ import annotations

from fractions import Fraction
from typing import List, Sequence, Tuple

from incumbent import Qx, decimal_string, sign
import rigidity_core as rc

CORE_REPRESENTATIVES: Tuple[Tuple[int, ...], ...] = (
    (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 16, 18, 19),
    (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17),
    (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15, 16, 18, 19),
)


def all_minimal_cores(data: rc.ActiveData) -> List[Tuple[int, ...]]:
    """Expand the three representatives to all fourteen cores via D4."""

    cores = set()
    for representative in CORE_REPRESENTATIVES:
        for index_map in data.d4_index_maps:
            cores.add(tuple(sorted(index_map[member] for member in representative)))
    return sorted(cores)


def stress_space_dimension(core: Sequence[int], data: rc.ActiveData) -> int:
    """Exact dimension of {y : sum y_e grad_free A_e = 0} for the core."""

    transpose = [
        [data.free_rows[member][position] for member in core]
        for position in range(len(rc.FREE_COORDINATES))
    ]
    return len(rc._kernel(transpose, len(core)))


def describe_flex(witness: Sequence[Qx], data: rc.ActiveData) -> str:
    """Readable movement pattern of an exact first-order flex."""

    moving = []
    for point in range(12):
        components = []
        for coordinate, name in ((0, "x"), (1, "y")):
            value = witness[2 * point + coordinate]
            if not value.is_zero():
                components.append(f"{name}{'+' if sign(value) > 0 else '-'}")
        if components:
            moving.append(f"p{point}({''.join(components)})")
    return " ".join(moving) if moving else "(no movement?)"


def main() -> None:
    data = rc.active_data()
    cores = all_minimal_cores(data)
    print("total_minimal_cores", len(cores))

    # Rank 1: stress-space dimensions.  For a size-s core the free-kernel
    # dimension is s - 16 when the free rank is 16, so uniqueness up to
    # scale is expected exactly at size 17; compute rather than assume.
    for representative in CORE_REPRESENTATIVES:
        dimension = stress_space_dimension(representative, data)
        print(
            "core_class",
            rc._orbit_signature(representative, data),
            "size",
            len(representative),
            "stress_space_dimension",
            dimension,
            "stress_unique_up_to_scale",
            dimension == 1,
        )

    # Rank 3: intersection and forcing structure.
    everything = set(range(20))
    common = set.intersection(*(set(core) for core in cores))
    print("intersection_of_all_14_cores", sorted(common), "size", len(common))
    print(
        "intersection_orbit_signature",
        rc._orbit_signature(tuple(sorted(common)), data) if common else None,
    )
    never_dropped = sorted(common)
    droppable = sorted(everything - common)
    print("droppable_triangles", droppable)
    for member in sorted(everything):
        containing = sum(1 for core in cores if member in core)
        print(
            "triangle",
            member,
            data.triangles[member],
            "orbit",
            data.orbit_of[member],
            "in_cores",
            containing,
            "of",
            len(cores),
        )
    # Hitting number of the cores: the minimum number of triangles whose
    # removal from the active set meets (hence destroys) every minimal
    # core.  Since the common intersection is nonempty, one shared
    # triangle suffices; verify by brute force anyway.
    from itertools import combinations as subsets

    hitting = None
    for size in range(1, 4):
        for candidate in subsets(sorted(everything), size):
            chosen = set(candidate)
            if all(chosen & set(core) for core in cores):
                hitting = candidate
                break
        if hitting is not None:
            break
    print("core_hitting_number", None if hitting is None else len(hitting), "witness", hitting)

    # Rank 4: the emerging flex for each individually removable triangle.
    # The eight size-19 subsets classified NONRIGID in the scan are the
    # drops whose removal alone breaks rigidity of the remaining 19.
    print("flexes_from_single_drops")
    for drop in sorted(everything):
        subset = tuple(member for member in sorted(everything) if member != drop)
        verdict = rc.classify(subset, data)
        if verdict.status == rc.NONRIGID:
            print(
                "drop",
                drop,
                data.triangles[drop],
                "orbit",
                data.orbit_of[drop],
                "flex",
                describe_flex(verdict.witness, data),
            )
        else:
            print("drop", drop, data.triangles[drop], "orbit", data.orbit_of[drop], "status", verdict.status)


if __name__ == "__main__":
    main()
