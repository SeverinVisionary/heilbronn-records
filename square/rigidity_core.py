"""Exact minimal-rigid-core scan of the incumbent's active-triangle hypergraph.

A subset ``H`` of the 20 active triangles is a rigid core when the only
feasible first-order velocity keeping every triangle of ``H`` nondecreasing
is zero.  Rigidity is certified by an exact strict stress plus an exact rank
computation; non-rigidity by an exact nonzero feasible velocity.  Float LP
is used only to propose candidates; every accepted certificate re-verifies
all identities and signs in ``Q(x)``.  See RIGIDITY_CORE_SPEC_2026-08-20.md.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations
from math import comb
from typing import Dict, List, Sequence, Tuple

from incumbent import (
    ONE,
    Qx,
    Triangle,
    _d4_permutations,
    active_structure,
    algebraic_bounds,
    compare,
    cubic,
    decimal_string,
    incumbent_analysis,
    incumbent_points,
    sign,
)


from tangent_certificate import (
    FREE_COORDINATES,
    INWARD_NORMAL,
    ORBIT_WEIGHTS,
    unsigned_area_gradient,
)

ZERO_QX = Qx(Fraction(0), Fraction(0), Fraction(0))


class CertificateRejected(AssertionError):
    """Raised only by the two exact certificate verifiers on a failed check.

    The classification pipeline may catch this to fall through to another
    proposal route; any other AssertionError is an implementation bug and
    must propagate.
    """

# Inward boundary-normal coordinates as (point, coordinate, inward sign),
# matching tangent_certificate._assert_certificate_shape.  The positive
# control below re-verifies the committed all-20 certificate through this
# table, so a transcription error here fails loudly rather than silently.
INWARD_COORDINATES: Tuple[Tuple[int, int, int], ...] = (
    (0, 1, 1),
    (1, 1, 1),
    (2, 1, -1),
    (3, 1, -1),
    (4, 0, 1),
    (5, 0, -1),
    (6, 0, 1),
    (7, 0, -1),
)

RIGID = "RIGID"
RIGID_INHERITED = "RIGID-by-monotonicity"
NONRIGID = "NONRIGID"
UNDECIDED = "UNDECIDED"


@dataclass(frozen=True)
class ActiveData:
    """Exact gradient rows of the 20 active triangles, split by coordinate role."""

    triangles: Tuple[Triangle, ...]
    free_rows: Tuple[Tuple[Qx, ...], ...]
    inward_rows: Tuple[Tuple[Qx, ...], ...]
    orbit_of: Tuple[int, ...]
    d4_index_maps: Tuple[Tuple[int, ...], ...]


@dataclass(frozen=True)
class Classification:
    """One subset's verdict with its exact certificate payload."""

    status: str
    stress: Tuple[Qx, ...] | None = None
    stress_normals: Tuple[Qx, ...] | None = None
    witness: Tuple[Qx, ...] | None = None


def _coordinate_layout_check() -> None:
    normal_flat = tuple(2 * point + coordinate for point, coordinate, _ in INWARD_COORDINATES)
    if set(FREE_COORDINATES) & set(normal_flat):
        raise AssertionError("free and inward coordinates must be disjoint")
    if set(FREE_COORDINATES) | set(normal_flat) != set(range(24)):
        raise AssertionError("free plus inward coordinates must cover all 24")
    # Zero-testing by coefficients equals the field zero test only because
    # the defining cubic is irreducible over Q; assert the rational-root
    # candidates all fail so the premise is checked, not assumed.
    for numerator in (1, -1):
        for denominator in (1, 2, 4):
            if cubic(Fraction(numerator, denominator)) == 0:
                raise AssertionError("the defining cubic must be irreducible over Q")


def _derived_layout_check(points: Sequence[Tuple[Qx, Qx]]) -> None:
    """Derive the boundary/interior layout from the exact coordinates.

    The scanner's whole feasibility model rests on ``INWARD_COORDINATES``
    naming exactly the boundary-pinned coordinates with the correct inward
    orientation, on no point sitting at a corner (which would need two
    normals), and on points 8-11 being strictly interior.  Check all of it
    against ``incumbent_points()`` instead of trusting the table.
    """

    declared = {(point, coordinate): inward for point, coordinate, inward in INWARD_COORDINATES}
    for point_index, (x_value, y_value) in enumerate(points):
        on_boundary = {}
        for coordinate, value in ((0, x_value), (1, y_value)):
            if value.is_zero():
                on_boundary[coordinate] = 1
            elif (value - ONE).is_zero():
                on_boundary[coordinate] = -1
            elif sign(value) <= 0 or sign(ONE - value) <= 0:
                raise AssertionError("every coordinate must lie inside the closed unit square")
        if len(on_boundary) == 2:
            raise AssertionError("a corner point would need two normals; the model forbids it")
        for coordinate, inward in on_boundary.items():
            if declared.get((point_index, coordinate)) != inward:
                raise AssertionError(
                    f"boundary coordinate ({point_index}, {coordinate}) missing or mis-oriented"
                )
        for coordinate in (0, 1):
            if (point_index, coordinate) in declared and on_boundary.get(coordinate) != declared[
                (point_index, coordinate)
            ]:
                raise AssertionError(
                    f"declared normal ({point_index}, {coordinate}) is not on the boundary"
                )
    if len(declared) != 8:
        raise AssertionError("the model requires exactly eight boundary normals")


def active_data() -> ActiveData:
    """Build all exact rows once; assert the expected active structure."""

    _coordinate_layout_check()
    points = incumbent_points()
    _derived_layout_check(points)
    _, active, _ = incumbent_analysis()
    if len(active) != 20:
        raise AssertionError("unexpected active-triangle count")
    orbits, _ = active_structure()
    if tuple(len(orbit) for orbit in orbits) != (4, 8, 8):
        raise AssertionError("unexpected active-orbit decomposition")
    orbit_of = []
    for triangle in active:
        membership = [index for index, orbit in enumerate(orbits) if triangle in orbit]
        if len(membership) != 1:
            raise AssertionError("every active triangle sits in exactly one orbit")
        orbit_of.append(membership[0])

    free_rows = []
    inward_rows = []
    for triangle in active:
        gradient = unsigned_area_gradient(points, triangle)
        free_rows.append(tuple(gradient[flat // 2][flat % 2] for flat in FREE_COORDINATES))
        inward_rows.append(
            tuple(gradient[point][coordinate] * inward for point, coordinate, inward in INWARD_COORDINATES)
        )

    triangle_index = {triangle: index for index, triangle in enumerate(active)}
    index_maps = []
    for permutation in _d4_permutations(points):
        mapped = tuple(
            triangle_index[tuple(sorted(permutation[vertex] for vertex in triangle))] for triangle in active
        )
        index_maps.append(mapped)

    return ActiveData(tuple(active), tuple(free_rows), tuple(inward_rows), tuple(orbit_of), tuple(index_maps))


def _rank(matrix: Sequence[Sequence[Qx]]) -> int:
    """Exact rank by Gaussian elimination over Q(x)."""

    work = [list(row) for row in matrix]
    rank = 0
    columns = len(work[0]) if work else 0
    for column in range(columns):
        pivot_row = next(
            (row for row in range(rank, len(work)) if not work[row][column].is_zero()), None
        )
        if pivot_row is None:
            continue
        work[rank], work[pivot_row] = work[pivot_row], work[rank]
        pivot = work[rank][column]
        for row in range(rank + 1, len(work)):
            if work[row][column].is_zero():
                continue
            factor = work[row][column] / pivot
            for trailing in range(column, columns):
                work[row][trailing] -= factor * work[rank][trailing]
        rank += 1
        if rank == min(len(work), columns):
            break
    return rank


def _kernel(matrix: Sequence[Sequence[Qx]], columns: int) -> List[List[Qx]]:
    """Exact kernel basis of ``matrix @ v = 0`` over Q(x)."""

    work = [list(row) for row in matrix]
    pivot_columns: List[int] = []
    row_index = 0
    for column in range(columns):
        pivot_row = next(
            (row for row in range(row_index, len(work)) if not work[row][column].is_zero()), None
        )
        if pivot_row is None:
            continue
        work[row_index], work[pivot_row] = work[pivot_row], work[row_index]
        pivot = work[row_index][column]
        work[row_index] = [entry / pivot for entry in work[row_index]]
        for row in range(len(work)):
            if row == row_index or work[row][column].is_zero():
                continue
            factor = work[row][column]
            work[row] = [entry - factor * lead for entry, lead in zip(work[row], work[row_index])]
        pivot_columns.append(column)
        row_index += 1
    free_columns = [column for column in range(columns) if column not in pivot_columns]
    basis = []
    for free_column in free_columns:
        vector = [ZERO_QX] * columns
        vector[free_column] = Qx(Fraction(1), Fraction(0), Fraction(0))
        for pivot_position, pivot_column in enumerate(pivot_columns):
            vector[pivot_column] = -work[pivot_position][free_column]
        basis.append(vector)
    return basis


def _to_float(value: Qx) -> float:
    lower, upper = algebraic_bounds(value, 64)
    return float((lower + upper) / 2)


def _verify_stress(
    subset: Sequence[int], data: ActiveData, weights: Sequence[Qx]
) -> Tuple[Tuple[Qx, ...], Tuple[Qx, ...]]:
    """Exactly re-verify a proposed strict stress; raise on any failed check."""

    if len(weights) != len(subset):
        raise CertificateRejected("stress length must match the subset")
    for weight in weights:
        if sign(weight) <= 0:
            raise CertificateRejected("stress weights must be strictly positive")
    for free_position in range(len(FREE_COORDINATES)):
        total = ZERO_QX
        for weight, member in zip(weights, subset):
            total += weight * data.free_rows[member][free_position]
        if not total.is_zero():
            raise CertificateRejected("stress must vanish on every free coordinate")
    normals = []
    for normal_position in range(len(INWARD_COORDINATES)):
        total = ZERO_QX
        for weight, member in zip(weights, subset):
            total += weight * data.inward_rows[member][normal_position]
        if sign(total) >= 0:
            raise CertificateRejected("stress must be strictly negative on every inward normal")
        normals.append(total)
    return tuple(weights), tuple(normals)


def _verify_velocity(subset: Sequence[int], data: ActiveData, velocity24: Sequence[Qx]) -> Tuple[Qx, ...]:
    """Exactly re-verify a proposed nonzero feasible velocity; raise on failure."""

    if all(component.is_zero() for component in velocity24):
        raise CertificateRejected("a non-rigidity witness must be nonzero")
    for point, coordinate, inward in INWARD_COORDINATES:
        if sign(velocity24[2 * point + coordinate] * inward) < 0:
            raise CertificateRejected("witness must be feasible at every boundary normal")
    for member in subset:
        gradient_free = data.free_rows[member]
        gradient_inward = data.inward_rows[member]
        derivative = ZERO_QX
        for position, flat in enumerate(FREE_COORDINATES):
            derivative += gradient_free[position] * velocity24[flat]
        for position, (point, coordinate, inward) in enumerate(INWARD_COORDINATES):
            derivative += gradient_inward[position] * (velocity24[2 * point + coordinate] * inward)
        if sign(derivative) < 0:
            raise CertificateRejected("witness must keep every subset triangle nondecreasing")
    return tuple(velocity24)


def _velocity_from_free(free_vector: Sequence[Qx]) -> List[Qx]:
    velocity = [ZERO_QX] * 24
    for position, flat in enumerate(FREE_COORDINATES):
        velocity[flat] = free_vector[position]
    return velocity


def _propose_stress_coefficients(
    kernel_basis: Sequence[Sequence[Qx]], subset: Sequence[int], data: ActiveData
) -> List[Fraction] | None:
    """Float LP proposing rational kernel coefficients with a positive margin."""

    from scipy.optimize import linprog

    dimension = len(kernel_basis)
    members = len(subset)
    basis_float = [[_to_float(entry) for entry in vector] for vector in kernel_basis]
    normal_float = [
        [
            sum(
                basis_float[i][e] * _to_float(data.inward_rows[member][j])
                for e, member in enumerate(subset)
            )
            for i in range(dimension)
        ]
        for j in range(len(INWARD_COORDINATES))
    ]
    # Variables: c_1..c_d, t.  Maximize t subject to (Bc)_e >= t and n_j(c) <= -t.
    rows = []
    rhs = []
    for e in range(members):
        rows.append([-basis_float[i][e] for i in range(dimension)] + [1.0])
        rhs.append(0.0)
    for j in range(len(INWARD_COORDINATES)):
        rows.append([normal_float[j][i] for i in range(dimension)] + [1.0])
        rhs.append(0.0)
    objective = [0.0] * dimension + [-1.0]
    bounds = [(-1.0, 1.0)] * dimension + [(0.0, 1.0)]
    result = linprog(objective, A_ub=rows, b_ub=rhs, bounds=bounds, method="highs")
    if not result.success or result.x is None or result.x[-1] <= 1e-9:
        return None
    return [Fraction(coefficient).limit_denominator(10**9) for coefficient in result.x[:dimension]]


def _propose_velocity(subset: Sequence[int], data: ActiveData) -> List[Fraction] | None:
    """Float LP proposing a strictly interior feasible velocity, if one exists."""

    from scipy.optimize import linprog

    members = list(subset)
    rows = []
    rhs = []
    normal_flat = {2 * point + coordinate: inward for point, coordinate, inward in INWARD_COORDINATES}
    for member in members:
        gradient = [0.0] * 24
        for position, flat in enumerate(FREE_COORDINATES):
            gradient[flat] = _to_float(data.free_rows[member][position])
        for position, (point, coordinate, inward) in enumerate(INWARD_COORDINATES):
            gradient[2 * point + coordinate] = _to_float(data.inward_rows[member][position]) * inward
        rows.append([-value for value in gradient] + [1.0])
        rhs.append(0.0)
    for flat, inward in normal_flat.items():
        row = [0.0] * 24
        row[flat] = -inward
        rows.append(row + [1.0])
        rhs.append(0.0)
    objective = [0.0] * 24 + [-1.0]
    bounds = [(-1.0, 1.0)] * 24 + [(0.0, 1.0)]
    result = linprog(objective, A_ub=rows, b_ub=rhs, bounds=bounds, method="highs")
    if not result.success or result.x is None or result.x[-1] <= 1e-9:
        return None
    return [Fraction(component).limit_denominator(10**9) for component in result.x[:24]]


def _combined_rows(subset: Sequence[int], data: ActiveData) -> List[List[Qx]]:
    """Rows of ``M`` with ``C(H) = {u : M u >= 0}`` in inward-oriented coordinates.

    Columns 0..15 are the free coordinates, columns 16..23 the inward-oriented
    boundary normals; the last eight rows are the unit feasibility rows.
    """

    one = Qx(Fraction(1), Fraction(0), Fraction(0))
    rows = [
        list(data.free_rows[member]) + list(data.inward_rows[member]) for member in subset
    ]
    for normal_position in range(len(INWARD_COORDINATES)):
        unit = [ZERO_QX] * 24
        unit[16 + normal_position] = one
        rows.append(unit)
    return rows


def _oriented_to_velocity(oriented: Sequence[Qx]) -> List[Qx]:
    velocity = [ZERO_QX] * 24
    for position, flat in enumerate(FREE_COORDINATES):
        velocity[flat] = oriented[position]
    for position, (point, coordinate, inward) in enumerate(INWARD_COORDINATES):
        velocity[2 * point + coordinate] = oriented[16 + position] * inward
    return velocity


def _solve_exact(rows: Sequence[Sequence[Qx]], rhs: Sequence[Qx]) -> List[Qx]:
    """Any exact solution of ``rows @ u = rhs``; raises if inconsistent."""

    columns = len(rows[0])
    work = [list(row) + [target] for row, target in zip(rows, rhs)]
    pivot_columns: List[int] = []
    row_index = 0
    for column in range(columns):
        pivot_row = next(
            (row for row in range(row_index, len(work)) if not work[row][column].is_zero()), None
        )
        if pivot_row is None:
            continue
        work[row_index], work[pivot_row] = work[pivot_row], work[row_index]
        pivot = work[row_index][column]
        work[row_index] = [entry / pivot for entry in work[row_index]]
        for row in range(len(work)):
            if row == row_index or work[row][column].is_zero():
                continue
            factor = work[row][column]
            work[row] = [entry - factor * lead for entry, lead in zip(work[row], work[row_index])]
        pivot_columns.append(column)
        row_index += 1
    for row in range(row_index, len(work)):
        if not work[row][columns].is_zero():
            raise AssertionError("inconsistent exact linear system")
    solution = [ZERO_QX] * columns
    for position, column in enumerate(pivot_columns):
        solution[column] = work[position][columns]
    return solution


def _stress_from_positive_kernel(
    subset: Sequence[int], data: ActiveData, vector: Sequence[Qx]
) -> Classification:
    """Turn a strictly positive combined kernel vector into a verified stress."""

    weights = list(vector[: len(subset)])
    if _rank([data.free_rows[member] for member in subset]) != len(FREE_COORDINATES):
        raise AssertionError("a RIGID verdict requires free rank 16, not just a stress")
    stress, normals = _verify_stress(subset, data, weights)
    return Classification(RIGID, stress=stress, stress_normals=normals)


def _witness_from_row_space(
    subset: Sequence[int], data: ActiveData, rows: Sequence[Sequence[Qx]], target: Sequence[Qx]
) -> Classification:
    """Solve ``M u = target`` (``target`` nonnegative, nonzero, in the range of ``M``)."""

    oriented = _solve_exact(rows, target)
    velocity = _oriented_to_velocity(oriented)
    return Classification(NONRIGID, witness=_verify_velocity(subset, data, velocity))


def _slice_point(
    lower_ratios: Sequence[Qx], upper_ratios: Sequence[Qx]
) -> Qx | None:
    """An exact point strictly between the largest lower and smallest upper ratio."""

    lower = None
    for ratio in lower_ratios:
        if lower is None or compare(ratio, lower) > 0:
            lower = ratio
    upper = None
    for ratio in upper_ratios:
        if upper is None or compare(ratio, upper) < 0:
            upper = ratio
    one = Qx(Fraction(1), Fraction(0), Fraction(0))
    if lower is None and upper is None:
        return ZERO_QX
    if lower is None:
        return upper - one
    if upper is None:
        return lower + one
    if compare(lower, upper) >= 0:
        return None
    return (lower + upper) / 2


def _positive_combination_2d(
    first: Sequence[Qx], second: Sequence[Qx]
) -> Tuple[Qx, Qx] | None:
    """Exact ``(s, t)`` with ``s*first + t*second`` entrywise strictly positive.

    Scaling invariance reduces the search to the slices ``t = 1``, ``t = -1``
    and ``t = 0``; each slice is an exact one-dimensional strict interval
    problem in ``Q(x)``.  Returning ``None`` is a proof that no strictly
    positive combination exists.
    """

    one = Qx(Fraction(1), Fraction(0), Fraction(0))
    for t_sign in (1, -1):
        t_value = one if t_sign == 1 else -one
        lower_ratios: List[Qx] = []
        upper_ratios: List[Qx] = []
        feasible = True
        for a, b in zip(first, second):
            constant = b * t_sign
            a_sign = sign(a)
            if a_sign > 0:
                lower_ratios.append(-constant / a)
            elif a_sign < 0:
                upper_ratios.append(-constant / a)
            elif sign(constant) <= 0:
                feasible = False
                break
        if feasible:
            point = _slice_point(lower_ratios, upper_ratios)
            if point is not None:
                return point, t_value
    for s_sign in (1, -1):
        if all(sign(a * s_sign) > 0 for a in first):
            return (one if s_sign == 1 else -one), ZERO_QX
    return None


def _gordan_nonnegative_dependence(
    kernel_basis: Sequence[Sequence[Qx]],
    *,
    screened: bool = False,
) -> List[Qx] | None:
    """Exact Gordan certificate: a nonnegative nonzero ``lambda`` with
    ``sum lambda_e * (z_1[e], ..., z_d[e]) = 0``, or ``None`` if none exists.

    By Gordan's alternative, ``None`` proves a strictly positive combination
    of the kernel basis vectors exists.  Completeness follows from
    Caratheodory: if zero is a nonnegative nontrivial combination of the
    ``m`` column vectors in ``R^d``, it is one of at most ``d + 1`` of them,
    so enumerating supports of size ``1..d+1`` decides exactly.  The
    normalization ``sum lambda = 1`` makes every consistent nonnegative
    solution nonzero.
    """

    dimension = len(kernel_basis)
    size = len(kernel_basis[0])
    one = Qx(Fraction(1), Fraction(0), Fraction(0))
    basis_float = None
    if screened:
        import numpy as np

        basis_float = np.array(
            [[_to_float(entry) for entry in vector] for vector in kernel_basis]
        )
    for support_size in range(1, dimension + 2):
        for support in combinations(range(size), support_size):
            if screened:
                # Cheap float screen: only supports whose least-squares
                # solution is plausibly nonnegative get the exact solve.  A
                # screened miss can only delay the answer to the unscreened
                # backstop pass, never change a verdict.
                import numpy as np

                block = np.vstack(
                    [basis_float[:, list(support)], np.ones((1, support_size))]
                )
                target = np.zeros(dimension + 1)
                target[-1] = 1.0
                solution_float, residual, *_ = np.linalg.lstsq(block, target, rcond=None)
                fitted = block @ solution_float - target
                if float(np.linalg.norm(fitted)) > 1e-7 or float(solution_float.min()) < -1e-6:
                    continue
            rows = [
                [kernel_basis[axis][position] for position in support]
                for axis in range(dimension)
            ]
            rows.append([one] * support_size)
            rhs = [ZERO_QX] * dimension + [one]
            try:
                solution = _solve_exact(rows, rhs)
            except AssertionError:
                continue
            if any(sign(entry) < 0 for entry in solution):
                continue
            weights = [ZERO_QX] * size
            for position, entry in zip(support, solution):
                weights[position] = entry
            return weights
    return None


def _resolve_stiemke(subset: Sequence[int], data: ActiveData) -> Classification:
    """Decide ``C(H) = {0}`` exactly via Stiemke's alternative when possible.

    ``C(H) = {u : M u >= 0}`` is trivial exactly when ``M`` has full column
    rank and the kernel of ``M^T`` contains a strictly positive vector.  The
    column-rank side is checked first and standalone: a nonzero column-kernel
    vector satisfies every constraint with equality and is itself an exact
    witness.  When no strictly positive kernel vector exists, some
    nonnegative nonzero ``c`` orthogonal to the kernel lies in the range of
    ``M`` and ``M u = c`` yields an exact witness.  Kernel dimensions 0, 1,
    and 2 are decided completely; higher dimensions return UNDECIDED for the
    float-LP path to handle.
    """

    rows = _combined_rows(subset, data)
    column_kernel = _kernel(rows, 24)
    if column_kernel:
        velocity = _oriented_to_velocity(column_kernel[0])
        return Classification(NONRIGID, witness=_verify_velocity(subset, data, velocity))
    transpose = [[rows[row][column] for row in range(len(rows))] for column in range(24)]
    kernel = _kernel(transpose, len(rows))
    ones = [Qx(Fraction(1), Fraction(0), Fraction(0))] * len(rows)
    if not kernel:
        return _witness_from_row_space(subset, data, rows, ones)
    if len(kernel) == 1:
        vector = kernel[0]
        signs = [sign(entry) for entry in vector]
        if all(entry_sign > 0 for entry_sign in signs):
            return _stress_from_positive_kernel(subset, data, vector)
        if all(entry_sign < 0 for entry_sign in signs):
            return _stress_from_positive_kernel(subset, data, [-entry for entry in vector])
        target = [ZERO_QX] * len(rows)
        zero_position = next((index for index, entry_sign in enumerate(signs) if entry_sign == 0), None)
        if zero_position is not None:
            target[zero_position] = ones[0]
        else:
            positive = signs.index(1)
            negative = signs.index(-1)
            target[positive] = -vector[negative]
            target[negative] = vector[positive]
        return _witness_from_row_space(subset, data, rows, target)
    if len(kernel) == 2:
        combination = _positive_combination_2d(kernel[0], kernel[1])
        if combination is not None:
            s_value, t_value = combination
            vector = [s_value * a + t_value * b for a, b in zip(kernel[0], kernel[1])]
            for entry in vector:
                if sign(entry) <= 0:
                    raise AssertionError("2d slice point must give a strictly positive vector")
            return _stress_from_positive_kernel(subset, data, vector)
    if len(kernel) <= 4:
        # Gordan's alternative, decided exactly: either a nonnegative
        # nontrivial dependence of the kernel columns exists (its weights
        # are orthogonal to the kernel, hence in range(M): an exact
        # witness), or a strictly positive kernel combination exists.
        # Order of attack: the LP-proposed positive combination first
        # (fast on rigid subsets), then a float-screened dependence search
        # (fast on non-rigid ones), and only then the exhaustive exact
        # enumeration as the completeness backstop.
        for coefficients in _propose_positive_combinations(kernel):
            vector = [ZERO_QX] * len(rows)
            for position in range(len(rows)):
                total = ZERO_QX
                for coefficient, basis_vector in zip(coefficients, kernel):
                    total += basis_vector[position] * coefficient
                vector[position] = total
            if all(sign(entry) > 0 for entry in vector):
                return _stress_from_positive_kernel(subset, data, vector)
        dependence = _gordan_nonnegative_dependence(kernel, screened=True)
        if dependence is None:
            dependence = _gordan_nonnegative_dependence(kernel, screened=False)
        if dependence is not None:
            return _witness_from_row_space(subset, data, rows, dependence)
        # A strictly positive combination provably exists (Gordan, from the
        # exhaustive pass) but the constructive search failed; report
        # honestly rather than claim.
        return Classification(UNDECIDED)
    return Classification(UNDECIDED)


def _propose_positive_combinations(
    kernel_basis: Sequence[Sequence[Qx]],
) -> List[List[Fraction]]:
    """Float LP proposals (one per rationalization precision) for a strictly
    positive kernel combination; the caller re-verifies every sign exactly."""

    from scipy.optimize import linprog

    dimension = len(kernel_basis)
    size = len(kernel_basis[0])
    basis_float = [[_to_float(entry) for entry in vector] for vector in kernel_basis]
    rows = [
        [-basis_float[axis][position] for axis in range(dimension)] + [1.0]
        for position in range(size)
    ]
    result = linprog(
        [0.0] * dimension + [-1.0],
        A_ub=rows,
        b_ub=[0.0] * size,
        bounds=[(-1.0, 1.0)] * dimension + [(0.0, 1.0)],
        method="highs",
    )
    if not result.success or result.x is None or result.x[-1] <= 1e-9:
        return []
    return [
        [Fraction(coefficient).limit_denominator(denominator) for coefficient in result.x[:dimension]]
        for denominator in (10**12, 10**9, 10**6)
    ]


def classify(subset: Sequence[int], data: ActiveData) -> Classification:
    """Classify one subset with exact certificates on both sides."""

    subset = tuple(subset)
    # A boundary normal reached by no subset triangle gives an immediate
    # exact witness: the inward unit move there changes nothing in H.
    for normal_position, (point, coordinate, inward) in enumerate(INWARD_COORDINATES):
        if all(data.inward_rows[member][normal_position].is_zero() for member in subset):
            velocity = [ZERO_QX] * 24
            velocity[2 * point + coordinate] = Qx(Fraction(inward), Fraction(0), Fraction(0))
            return Classification(NONRIGID, witness=_verify_velocity(subset, data, velocity))

    free_matrix = [data.free_rows[member] for member in subset]
    if _rank(free_matrix) < len(FREE_COORDINATES):
        free_kernel = _kernel(free_matrix, len(FREE_COORDINATES))
        if not free_kernel:
            raise AssertionError("a rank-deficient free system must have a kernel vector")
        velocity = _velocity_from_free(free_kernel[0])
        return Classification(NONRIGID, witness=_verify_velocity(subset, data, velocity))

    transpose = [
        [data.free_rows[member][position] for member in subset]
        for position in range(len(FREE_COORDINATES))
    ]
    kernel_basis = _kernel(transpose, len(subset))
    if kernel_basis:
        coefficients = _propose_stress_coefficients(kernel_basis, subset, data)
        if coefficients is not None:
            weights = []
            for e in range(len(subset)):
                weight = ZERO_QX
                for coefficient, vector in zip(coefficients, kernel_basis):
                    weight += vector[e] * coefficient
                weights.append(weight)
            try:
                stress, normals = _verify_stress(subset, data, weights)
                return Classification(RIGID, stress=stress, stress_normals=normals)
            except CertificateRejected:
                pass

    proposal = _propose_velocity(subset, data)
    if proposal is not None:
        velocity = [Qx(component, Fraction(0), Fraction(0)) for component in proposal]
        try:
            return Classification(NONRIGID, witness=_verify_velocity(subset, data, velocity))
        except CertificateRejected:
            pass
    return _resolve_stiemke(subset, data)


def _canonical_subset(subset: Tuple[int, ...], data: ActiveData) -> Tuple[int, ...]:
    return min(tuple(sorted(index_map[member] for member in subset)) for index_map in data.d4_index_maps)


def _orbit_signature(subset: Sequence[int], data: ActiveData) -> Tuple[int, int, int]:
    counts = [0, 0, 0]
    for member in subset:
        counts[data.orbit_of[member]] += 1
    return tuple(counts)


def full_set_controls(data: ActiveData) -> None:
    """Positive and negative controls; every one must run on every invocation."""

    # Positive: the committed all-20 orbit-weight certificate must pass the
    # scanner's own verifier, with each normal equal to the committed value.
    committed = [ORBIT_WEIGHTS[data.orbit_of[member]] for member in range(20)]
    _, normals = _verify_stress(tuple(range(20)), data, committed)
    for normal in normals:
        if not (normal - INWARD_NORMAL).is_zero():
            raise AssertionError("all-20 stress must reproduce the committed inward normal")

    # Negative: a mis-signed stress must fail exact verification.
    broken = list(committed)
    broken[0] = -broken[0]
    try:
        _verify_stress(tuple(range(20)), data, broken)
    except AssertionError:
        pass
    else:
        raise AssertionError("negative control failed: mis-signed stress verified")

    # Negative: 15 triangles can never reach rank 16.
    fifteen = classify(tuple(range(15)), data)
    if fifteen.status != NONRIGID:
        raise AssertionError("negative control failed: a 15-subset must be NONRIGID")

    # The exact Stiemke resolver must reach the same verdicts standalone:
    # NONRIGID on a rank-deficient subset via its column-kernel witness, and
    # RIGID on the scan's size-17 core (cloud run 5) via the sign analysis of
    # the one-dimensional combined kernel - an LP-free cross-validation of
    # that core's stress certificate.
    resolved = _resolve_stiemke(tuple(range(16)), data)
    if resolved.status != NONRIGID:
        raise AssertionError("resolver control failed: rank-deficient subset must be NONRIGID")
    seventeen_core = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 16, 18, 19)
    resolved = _resolve_stiemke(seventeen_core, data)
    if resolved.status != RIGID:
        raise AssertionError("resolver control failed: the run-5 size-17 core must resolve RIGID")

    # Negative: dropping every triangle that reaches one boundary normal
    # must be certified by the explicit inward unit vector.
    exercised = 0
    for normal_position in range(len(INWARD_COORDINATES)):
        untouched = tuple(
            member
            for member in range(20)
            if data.inward_rows[member][normal_position].is_zero()
        )
        if untouched:
            verdict = classify(untouched, data)
            if verdict.status != NONRIGID:
                raise AssertionError("negative control failed: untouched normal must be NONRIGID")
            exercised += 1
    if exercised == 0:
        raise AssertionError("no boundary normal admits the untouched-normal control")


def scan(
    data: ActiveData,
    *,
    sizes: Sequence[int],
    max_subsets: int | None = None,
) -> Dict[str, object]:
    """Bottom-up scan with superset inheritance; returns the full census."""

    census: Dict[int, Dict[str, int]] = {size: {} for size in sizes}
    minimal_cores: List[Tuple[Tuple[int, ...], Classification]] = []
    undecided: List[Tuple[int, ...]] = []
    processed = 0
    truncated = False
    # Rigidity is upward-closed, and sizes ascend, so any superset of a found
    # core inherits its certificate and every RIGID verdict below is
    # inclusion-minimal among certificate-backed rigid sets by construction.
    # A monotonicity contradiction (NONRIGID above a core) is therefore
    # structurally unobservable here; the two certificate verifiers are the
    # gates that keep the closure argument honest.
    for size in sorted(sizes):
        for subset in combinations(range(20), size):
            if max_subsets is not None and processed >= max_subsets:
                truncated = True
                break
            if any(set(core).issubset(subset) for core, _ in minimal_cores):
                census[size][RIGID_INHERITED] = census[size].get(RIGID_INHERITED, 0) + 1
                processed += 1
                continue
            verdict = classify(subset, data)
            census[size][verdict.status] = census[size].get(verdict.status, 0) + 1
            processed += 1
            if verdict.status == RIGID:
                minimal_cores.append((subset, verdict))
            elif verdict.status == UNDECIDED:
                undecided.append(subset)
        if truncated:
            break

    expected = sum(comb(20, size) for size in sizes)
    return {
        "census": census,
        "minimal_cores": minimal_cores,
        "undecided": undecided,
        "processed": processed,
        "expected": expected,
        "complete": (not truncated) and processed == expected,
        # Minimality is only meaningful when every smaller size in 16..max
        # was scanned; a gapped size list must never print minimal cores.
        "prefix_complete": sorted(sizes) == list(range(16, max(sizes) + 1)),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sizes", default="16,17,18,19,20", help="comma-separated subset sizes to scan")
    parser.add_argument("--max-subsets", type=int, default=0, help="0 = no cap; any cap makes the scan INCOMPLETE")
    arguments = parser.parse_args()
    sizes = tuple(sorted({int(token) for token in arguments.sizes.split(",")}))
    if any(size < 16 or size > 20 for size in sizes):
        raise SystemExit("sizes must lie in 16..20: rank 16 is impossible below 16 triangles")

    data = active_data()
    full_set_controls(data)
    print("controls", "PASS")

    result = scan(data, sizes=sizes, max_subsets=arguments.max_subsets or None)
    print("processed", result["processed"], "of", result["expected"])
    for size in sizes:
        print("census", size, dict(sorted(result["census"][size].items())))
    print("undecided_count", len(result["undecided"]))
    if not result["prefix_complete"]:
        print("status", "PARTIAL: size list is not the downward-closed prefix 16..max; no minimality claim")
        return
    cores = result["minimal_cores"]
    print("minimal_rigid_cores", len(cores))
    canonical = {}
    for core, verdict in cores:
        canonical.setdefault(_canonical_subset(core, data), []).append((core, verdict))
    print("minimal_rigid_cores_up_to_d4", len(canonical))
    for representative, instances in sorted(canonical.items()):
        core, verdict = instances[0]
        margin = verdict.stress_normals[0]
        for normal in verdict.stress_normals[1:]:
            if compare(normal, margin) > 0:
                margin = normal
        total = ZERO_QX
        for weight in verdict.stress:
            total += weight
        minimum_weight = verdict.stress[0]
        for weight in verdict.stress[1:]:
            if compare(weight, minimum_weight) < 0:
                minimum_weight = weight
        # Raw normals are scale artifacts of the kernel normalization; the
        # certified quantities are the sum-normalized margin and weight.
        print(
            "core",
            core,
            "orbit_signature",
            _orbit_signature(core, data),
            "d4_copies",
            len(instances),
            "normalized_margin",
            decimal_string(margin / total, 24),
            "normalized_min_weight",
            decimal_string(minimum_weight / total, 24),
        )
    if not result["complete"]:
        print("status", "INCOMPLETE: subset budget truncated the scan; no minimality claim")
    elif result["undecided"]:
        print("status", "COMPLETE-WITH-UNDECIDED: minimality claims exclude undecided subsets")
    else:
        print("status", "COMPLETE: every subset in the scanned sizes carries an exact certificate")


if __name__ == "__main__":
    main()
