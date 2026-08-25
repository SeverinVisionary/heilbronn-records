"""Field- and domain-generic first-order rigidity certificates for Heilbronn configurations.

``rigidity_core.py`` decides rigidity for the n=12 unit-square incumbent inside a
hardcoded five-boundary normal form.  This module states the same question
without any coordinate bookkeeping, so it applies to any number of points, any
of the standard domains (square, triangle, disk), and any exact coordinate
field (see ``exact_field.py``).

Model.  Let ``H`` be a set of active (minimum-area) triangles and let ``M`` be
the matrix whose rows are, in the full ``2n``-dimensional coordinate space:

* the exact gradient of each unsigned area ``A_e``, ``e`` in ``H``;
* the inward normal of each active domain constraint (an edge contact gives one
  row, a corner two, a disk contact one radial row);
* for a domain with a continuous symmetry, the generator of that symmetry as a
  *pair* of opposite rows, which encodes the gauge equality ``<g, v> = 0``.

The feasible first-order cone is ``C(H) = {v : Mv >= 0}``, and

    C(H) = {0}   <=>   ker(M) = {0}  and  there is y > 0 with M^T y = 0,

the second condition being Stiemke's alternative.  RIGID is certified by an
exact strictly positive ``y`` together with an exact full-rank witness;
NONRIGID by an exact nonzero ``v`` with ``Mv >= 0``.  Floating-point linear
programming only ever *proposes* a candidate; acceptance is decided by exact
arithmetic in the configuration's own field.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations
from typing import Callable, List, Sequence, Tuple

import numpy as np
from scipy.optimize import linprog

RIGID = "RIGID"
NONRIGID = "NONRIGID"
UNDECIDED = "UNDECIDED"


class CertificateRejected(AssertionError):
    """Raised when a proposed certificate fails its exact verification."""


# --------------------------------------------------------------------------
# domains
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class DomainConstraint:
    """One inequality ``g(p) >= 0`` bounding the domain, with its gradient."""

    value: Callable[[object, object], object]
    gradient: Callable[[object, object], Tuple[object, object]]
    label: str
    #: an affine ``g`` satisfies ``g(p + t v) = t <grad g, v>`` exactly, so a
    #: tangential direction stays feasible.  For a curved boundary it does not:
    #: at a disk contact, ``r^2 - |p + t v|^2 = -t^2 |v|^2 < 0`` for every
    #: ``t > 0`` even though the linearized row ``<grad g, v> >= 0`` admits it.
    #: Consumers must demand *strict* inwardness on non-affine contacts.
    affine: bool = True


class Domain:
    """A convex region given by exact inequality constraints."""

    name = "domain"
    #: generator of a continuous symmetry group, or None
    symmetry: str | None = None

    def constraints(self, field) -> Sequence[DomainConstraint]:
        raise NotImplementedError

    def area_normalization(self, field):
        """Exact area of the domain, used to normalize published values."""

        raise NotImplementedError


class Square(Domain):
    """The unit square [0,1]^2.  No continuous symmetry."""

    name = "unit-square"

    def constraints(self, field) -> Sequence[DomainConstraint]:
        one = field.one
        zero = field.zero
        return (
            DomainConstraint(lambda x, y: x, lambda x, y: (one, zero), "x>=0"),
            DomainConstraint(lambda x, y: one - x, lambda x, y: (-one, zero), "x<=1"),
            DomainConstraint(lambda x, y: y, lambda x, y: (zero, one), "y>=0"),
            DomainConstraint(lambda x, y: one - y, lambda x, y: (zero, -one), "y<=1"),
        )

    def area_normalization(self, field):
        return field.one


@dataclass(frozen=True)
class Polygon(Domain):
    """A convex polygon given by vertices in counter-clockwise order.

    Vertices are supplied as ``Fraction`` pairs and lifted into the working
    field, so the unit right triangle and the unit-area equilateral triangle
    (whose vertices are irrational) are both expressible.
    """

    vertices: Tuple[Tuple[Fraction, Fraction], ...]
    name: str = "polygon"

    def constraints(self, field) -> Sequence[DomainConstraint]:
        built = []
        count = len(self.vertices)
        for index in range(count):
            ax, ay = (field.from_fraction(value) for value in self.vertices[index])
            bx, by = (field.from_fraction(value) for value in self.vertices[(index + 1) % count])
            # inward half-plane of the directed edge a -> b for a CCW polygon:
            # (b - a) x (p - a) >= 0
            dx, dy = bx - ax, by - ay

            def value(x, y, ax=ax, ay=ay, dx=dx, dy=dy):
                return dx * (y - ay) - dy * (x - ax)

            def gradient(x, y, dx=dx, dy=dy):
                return (-dy, dx)

            built.append(DomainConstraint(value, gradient, f"edge{index}"))
        return tuple(built)

    def area_normalization(self, field):
        total = field.zero
        count = len(self.vertices)
        for index in range(count):
            ax, ay = (field.from_fraction(value) for value in self.vertices[index])
            bx, by = (field.from_fraction(value) for value in self.vertices[(index + 1) % count])
            total = total + (ax * by - bx * ay)
        return total / field.from_fraction(2)


@dataclass(frozen=True)
class Disk(Domain):
    """The disk of radius ``radius`` centred at the origin.

    The disk is rotation invariant, so rigidity is only meaningful modulo that
    rotation; the engine adds the gauge equality automatically.
    """

    radius: Fraction = Fraction(1)
    name: str = "disk"
    symmetry: str = "rotation"

    def constraints(self, field) -> Sequence[DomainConstraint]:
        squared = field.from_fraction(self.radius * self.radius)
        two = field.from_fraction(2)

        def value(x, y):
            return squared - x * x - y * y

        def gradient(x, y):
            return (-two * x, -two * y)

        return (DomainConstraint(value, gradient, "inside-disk", affine=False),)

    def area_normalization(self, field):
        raise NotImplementedError("the disk area is transcendental; compare within the disk model")


# --------------------------------------------------------------------------
# configurations
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class Configuration:
    """An exact point configuration with its provenance."""

    label: str
    field: object
    points: Tuple[Tuple[object, object], ...]
    domain: Domain
    source: str = ""
    published_value: str = ""

    @property
    def count(self) -> int:
        return len(self.points)


@dataclass(frozen=True)
class ActiveSystem:
    """The exact active data of a configuration."""

    configuration: Configuration
    minimum_area_doubled: object
    active_triangles: Tuple[Tuple[int, int, int], ...]
    orientation: Tuple[int, ...]
    contacts: Tuple[Tuple[int, str], ...]
    rows: Tuple[Tuple[object, ...], ...]
    row_labels: Tuple[str, ...]
    triangle_row_count: int
    #: indices of rows whose constraint is *not* affine; a feasible direction
    #: must make these strictly positive, not merely nonnegative
    strict_row_indices: Tuple[int, ...] = ()

    @property
    def dimension(self) -> int:
        return 2 * self.configuration.count


def _determinant(points, triple, field):
    (i, j, k) = triple
    (x1, y1), (x2, y2), (x3, y3) = points[i], points[j], points[k]
    return (x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1)


def _determinant_gradient(points, triple, field) -> List[Tuple[int, object]]:
    """Nonzero partial derivatives of the doubled signed area, as (index, value)."""

    (i, j, k) = triple
    (x1, y1), (x2, y2), (x3, y3) = points[i], points[j], points[k]
    return [
        (2 * i, y2 - y3),
        (2 * i + 1, x3 - x2),
        (2 * j, y3 - y1),
        (2 * j + 1, x1 - x3),
        (2 * k, y1 - y2),
        (2 * k + 1, x2 - x1),
    ]


def build_active_system(configuration: Configuration) -> ActiveSystem:
    """Exact minimum area, active triangles, domain contacts and constraint rows."""

    field = configuration.field
    points = configuration.points
    count = configuration.count
    zero = field.zero

    constraints = configuration.domain.constraints(field)
    for index, (x_value, y_value) in enumerate(points):
        for constraint in constraints:
            if constraint.value(x_value, y_value).sign() < 0:
                raise AssertionError(
                    f"point {index} violates domain constraint {constraint.label}"
                )

    doubled_areas = {}
    orientation = {}
    for triple in combinations(range(count), 3):
        determinant = _determinant(points, triple, field)
        signum = determinant.sign()
        if signum == 0:
            raise AssertionError(f"degenerate (collinear) triple {triple}")
        orientation[triple] = signum
        doubled_areas[triple] = determinant if signum > 0 else -determinant

    minimum = None
    for triple, value in doubled_areas.items():
        if minimum is None or (value - minimum).sign() < 0:
            minimum = value
    active = tuple(
        triple for triple in sorted(doubled_areas) if (doubled_areas[triple] - minimum).is_zero()
    )

    rows: List[Tuple[object, ...]] = []
    labels: List[str] = []
    for triple in active:
        gradient = [zero] * (2 * count)
        signum = orientation[triple]
        for index, value in _determinant_gradient(points, triple, field):
            gradient[index] = value if signum > 0 else -value
        rows.append(tuple(gradient))
        labels.append("area" + str(triple))
    triangle_row_count = len(rows)

    contacts: List[Tuple[int, str]] = []
    strict_rows: List[int] = []
    for index, (x_value, y_value) in enumerate(points):
        for constraint in constraints:
            if constraint.value(x_value, y_value).is_zero():
                gradient_x, gradient_y = constraint.gradient(x_value, y_value)
                row = [zero] * (2 * count)
                row[2 * index] = gradient_x
                row[2 * index + 1] = gradient_y
                if not constraint.affine:
                    strict_rows.append(len(rows))
                rows.append(tuple(row))
                labels.append(f"contact(p{index},{constraint.label})")
                contacts.append((index, constraint.label))

    if configuration.domain.symmetry == "rotation":
        generator = [zero] * (2 * count)
        for index, (x_value, y_value) in enumerate(points):
            generator[2 * index] = -y_value
            generator[2 * index + 1] = x_value
        rows.append(tuple(generator))
        labels.append("gauge(rotation,+)")
        rows.append(tuple(-value for value in generator))
        labels.append("gauge(rotation,-)")
    elif configuration.domain.symmetry is not None:
        raise NotImplementedError(f"unsupported symmetry {configuration.domain.symmetry}")

    return ActiveSystem(
        configuration,
        minimum,
        active,
        tuple(orientation[triple] for triple in active),
        tuple(contacts),
        tuple(rows),
        tuple(labels),
        triangle_row_count,
        tuple(strict_rows),
    )


# --------------------------------------------------------------------------
# exact linear algebra over the configuration's field
# --------------------------------------------------------------------------


def rank(matrix: Sequence[Sequence[object]], field) -> int:
    work = [list(row) for row in matrix]
    if not work:
        return 0
    columns = len(work[0])
    pivot = 0
    for column in range(columns):
        row_index = next((r for r in range(pivot, len(work)) if not work[r][column].is_zero()), None)
        if row_index is None:
            continue
        work[pivot], work[row_index] = work[row_index], work[pivot]
        pivot_value = work[pivot][column]
        for r in range(len(work)):
            if r == pivot or work[r][column].is_zero():
                continue
            factor = work[r][column] / pivot_value
            work[r] = [a - factor * b for a, b in zip(work[r], work[pivot])]
        pivot += 1
        if pivot == len(work):
            break
    return pivot


def kernel(matrix: Sequence[Sequence[object]], columns: int, field) -> List[List[object]]:
    """Basis of {v : Mv = 0}, exactly."""

    work = [list(row) for row in matrix]
    zero, one = field.zero, field.one
    pivots: List[int] = []
    pivot = 0
    for column in range(columns):
        row_index = next((r for r in range(pivot, len(work)) if not work[r][column].is_zero()), None)
        if row_index is None:
            continue
        work[pivot], work[row_index] = work[row_index], work[pivot]
        pivot_value = work[pivot][column]
        work[pivot] = [value / pivot_value for value in work[pivot]]
        for r in range(len(work)):
            if r == pivot:
                continue
            factor = work[r][column]
            if factor.is_zero():
                continue
            work[r] = [a - factor * b for a, b in zip(work[r], work[pivot])]
        pivots.append(column)
        pivot += 1
        if pivot == len(work):
            break
    free_columns = [column for column in range(columns) if column not in pivots]
    basis = []
    for free in free_columns:
        vector = [zero] * columns
        vector[free] = one
        for row_index, column in enumerate(pivots):
            vector[column] = -work[row_index][free]
        basis.append(vector)
    return basis


def _to_float_matrix(rows: Sequence[Sequence[object]]) -> np.ndarray:
    return np.array([[value.to_float() for value in row] for row in rows], dtype=float)


# --------------------------------------------------------------------------
# certificates
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class Verdict:
    status: str
    stress: Tuple[object, ...] | None = None
    velocity: Tuple[object, ...] | None = None
    rank_value: int = 0
    detail: str = ""


def _verify_stress(system: ActiveSystem, stress: Sequence[object]) -> None:
    """Exact check that ``y > 0`` and ``M^T y = 0``."""

    field = system.configuration.field
    if len(stress) != len(system.rows):
        raise CertificateRejected("stress length does not match the row count")
    for index, weight in enumerate(stress):
        if weight.sign() <= 0:
            raise CertificateRejected(f"stress weight {index} is not strictly positive")
    for column in range(system.dimension):
        total = field.zero
        for weight, row in zip(stress, system.rows):
            if not row[column].is_zero():
                total = total + weight * row[column]
        if not total.is_zero():
            raise CertificateRejected(f"stress does not annihilate column {column}")


def _verify_velocity(system: ActiveSystem, velocity: Sequence[object]) -> None:
    """Exact check that ``v != 0`` and ``Mv >= 0``."""

    field = system.configuration.field
    if all(value.is_zero() for value in velocity):
        raise CertificateRejected("velocity is zero")
    for label, row in zip(system.row_labels, system.rows):
        total = field.zero
        for value, coordinate in zip(row, velocity):
            if not value.is_zero() and not coordinate.is_zero():
                total = total + value * coordinate
        if total.sign() < 0:
            raise CertificateRejected(f"velocity violates constraint {label}")


def _propose_stress(system: ActiveSystem) -> List[object] | None:
    """Propose a strictly positive stress *inside the exact left kernel*.

    Rounding an LP solution for ``y`` directly almost never satisfies
    ``M^T y = 0`` exactly.  Instead the exact left kernel is computed first and
    the LP only chooses coefficients in that kernel basis, so the equality holds
    by construction and exact verification can only fail on positivity — which
    the LP's margin makes unlikely.
    """

    field = system.configuration.field
    transpose = [
        [system.rows[row][column] for row in range(len(system.rows))]
        for column in range(system.dimension)
    ]
    basis = kernel(transpose, len(system.rows), field)
    if not basis:
        return None
    matrix = np.array(
        [[vector[index].to_float() for vector in basis] for index in range(len(system.rows))],
        dtype=float,
    )
    scale = float(np.max(np.abs(matrix))) or 1.0
    matrix = matrix / scale
    width = len(basis)
    # maximize eps subject to  B c >= eps,  |c| <= 1
    result = linprog(
        c=np.concatenate([np.zeros(width), [-1.0]]),
        A_ub=np.hstack([-matrix, np.ones((matrix.shape[0], 1))]),
        b_ub=np.zeros(matrix.shape[0]),
        bounds=[(-1.0, 1.0)] * width + [(0.0, 1.0)],
        method="highs",
    )
    if not result.success or result.x[-1] <= 1e-9:
        return None
    coefficients = [Fraction(value).limit_denominator(10 ** 6) for value in result.x[:width]]
    combined = [field.zero] * len(system.rows)
    for coefficient, vector in zip(coefficients, basis):
        if coefficient == 0:
            continue
        weight = field.from_fraction(coefficient)
        combined = [total + weight * value for total, value in zip(combined, vector)]
    return combined


@dataclass(frozen=True)
class ImprovementDirection:
    """A feasible direction along which every active area strictly increases."""

    velocity: Tuple[object, ...]
    margin: object


def improvement_direction(system: ActiveSystem) -> ImprovementDirection | None:
    """Search for v with every active-area row strictly positive and every
    domain/gauge row nonnegative.

    Structurally this is the linear-programming improvement test of Donev,
    Torquato, Stillinger & Connelly, *A linear programming algorithm to test
    for jamming in hard-sphere packings*, J. Comput. Phys. 197 (2004) 139-166,
    with triple-area rows in place of pairwise contact rows.

    Such a v is a *first-order improvement*: for small t > 0 the minimum area
    strictly increases, because the inactive triangles are bounded away from
    the minimum.  The LP proposes; the exact arithmetic decides.
    """

    field = system.configuration.field
    # Gauge rows encode an equality and are irrelevant to an improvement search:
    # a symmetry component in the direction moves the configuration to a
    # congruent copy without changing any area.  They are also unrepresentable
    # after rationalizing an LP solution, which would reject every candidate.
    keep = [
        index for index, label in enumerate(system.row_labels) if not label.startswith("gauge(")
    ]
    rows = [system.rows[index] for index in keep]
    matrix = _to_float_matrix(rows)
    scale = float(np.max(np.abs(matrix))) or 1.0
    matrix = matrix / scale
    dimension = system.dimension
    area_rows = system.triangle_row_count
    # maximize eps subject to: area rows . v >= eps, other rows . v >= 0, |v| <= 1
    upper = np.hstack([-matrix, np.zeros((matrix.shape[0], 1))])
    upper[:area_rows, -1] = 1.0
    # A tangential direction at a curved boundary is infeasible at every t > 0,
    # so those contact rows need the same strict margin as the area rows.
    strict_positions = {keep.index(index) for index in system.strict_row_indices if index in keep}
    for position in strict_positions:
        upper[position, -1] = 1.0
    result = linprog(
        c=np.concatenate([np.zeros(dimension), [-1.0]]),
        A_ub=upper,
        b_ub=np.zeros(matrix.shape[0]),
        bounds=[(-1.0, 1.0)] * dimension + [(0.0, 1.0)],
        method="highs",
    )
    if not result.success or result.x[-1] <= 1e-9:
        return None
    velocity = [
        field.from_fraction(Fraction(value).limit_denominator(10 ** 6)) for value in result.x[:dimension]
    ]
    margin = None
    for index, row in enumerate(rows):
        total = field.zero
        for value, coordinate in zip(row, velocity):
            if not value.is_zero() and not coordinate.is_zero():
                total = total + value * coordinate
        if index < area_rows:
            if total.sign() <= 0:
                return None
            margin = total if margin is None or (total - margin).sign() < 0 else margin
        elif index in strict_positions:
            if total.sign() <= 0:   # curved boundary: tangential is not feasible
                return None
        elif total.sign() < 0:
            return None
    return ImprovementDirection(tuple(velocity), margin)


def _propose_velocity(system: ActiveSystem) -> List[Fraction] | None:
    """Float LP proposal for a nonzero v with Mv >= 0."""

    matrix = _to_float_matrix(system.rows)
    scale = float(np.max(np.abs(matrix))) or 1.0
    matrix = matrix / scale
    dimension = matrix.shape[1]
    best = None
    for column in range(dimension):
        for direction in (1.0, -1.0):
            objective = np.zeros(dimension)
            objective[column] = -direction
            result = linprog(
                c=objective,
                A_ub=-matrix,
                b_ub=np.zeros(matrix.shape[0]),
                bounds=[(-1.0, 1.0)] * dimension,
                method="highs",
            )
            if result.success and np.max(np.abs(result.x)) > 1e-6:
                candidate = result.x
                if best is None or np.max(np.abs(candidate)) > np.max(np.abs(best)):
                    best = candidate
        if best is not None:
            break
    if best is None:
        return None
    return [Fraction(value).limit_denominator(10 ** 6) for value in best]


def _exact_kernel_velocity(system: ActiveSystem) -> List[object] | None:
    """Any nonzero kernel vector is a feasible velocity (Mv = 0 >= 0)."""

    field = system.configuration.field
    basis = kernel(system.rows, system.dimension, field)
    return basis[0] if basis else None


def classify(system: ActiveSystem) -> Verdict:
    """Decide C(H) = {0} with an exact certificate."""

    field = system.configuration.field
    rank_value = rank(system.rows, field)

    if rank_value < system.dimension:
        velocity = _exact_kernel_velocity(system)
        if velocity is None:
            return Verdict(UNDECIDED, rank_value=rank_value, detail="rank deficient without kernel")
        _verify_velocity(system, velocity)
        return Verdict(
            NONRIGID,
            velocity=tuple(velocity),
            rank_value=rank_value,
            detail=f"rank {rank_value} < {system.dimension}: kernel motion",
        )

    stress = _propose_stress(system)
    if stress is not None:
        try:
            _verify_stress(system, stress)
            return Verdict(
                RIGID, stress=tuple(stress), rank_value=rank_value, detail="kernel-LP stress verified"
            )
        except CertificateRejected:
            pass

    exact_stress = _exact_stress_from_kernel(system)
    if exact_stress is not None:
        _verify_stress(system, exact_stress)
        return Verdict(RIGID, stress=tuple(exact_stress), rank_value=rank_value, detail="exact kernel stress")

    proposal = _propose_velocity(system)
    if proposal is not None:
        velocity = [field.from_fraction(value) for value in proposal]
        try:
            _verify_velocity(system, velocity)
            return Verdict(
                NONRIGID, velocity=tuple(velocity), rank_value=rank_value, detail="LP velocity verified"
            )
        except CertificateRejected:
            pass

    return Verdict(UNDECIDED, rank_value=rank_value, detail="no certificate found by either route")


def _exact_stress_from_kernel(system: ActiveSystem) -> List[object] | None:
    """Exact search for y > 0 in the left kernel when it is one-dimensional.

    The transpose kernel has dimension ``|rows| - rank``; when that is 1 the
    stress is unique up to scale, so the decision is a pure sign check and
    needs no search.  Higher dimensions fall through to the LP route and, if
    that fails, to UNDECIDED, which the caller must escalate.
    """

    field = system.configuration.field
    transpose = [
        [system.rows[row][column] for row in range(len(system.rows))]
        for column in range(system.dimension)
    ]
    basis = kernel(transpose, len(system.rows), field)
    if len(basis) != 1:
        return None
    candidate = basis[0]
    signs = {value.sign() for value in candidate}
    if 0 in signs:
        return None
    if signs == {1}:
        return list(candidate)
    if signs == {-1}:
        return [-value for value in candidate]
    return None


def audit(configuration: Configuration) -> Tuple[ActiveSystem, Verdict]:
    system = build_active_system(configuration)
    return system, classify(system)


def describe(system: ActiveSystem, verdict: Verdict) -> str:
    configuration = system.configuration
    minimum = system.minimum_area_doubled / configuration.field.from_fraction(2)
    lines = [
        f"configuration {configuration.label}",
        f"  domain {configuration.domain.name}  points {configuration.count}"
        f"  dimension {system.dimension}",
        f"  minimum area {minimum.to_float():.15f}",
        f"  active triangles {len(system.active_triangles)}"
        f"  domain contacts {len(system.contacts)}"
        f"  rows {len(system.rows)}",
        f"  rank {verdict.rank_value} of {system.dimension}",
        f"  verdict {verdict.status} ({verdict.detail})",
    ]
    if configuration.source:
        lines.append(f"  source {configuration.source}")
    return "\n".join(lines)

# --------------------------------------------------------------------------
# prestress stability (second-order rigidity for flexible configurations)
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class PrestressAnalysis:
    """Second-order verdict for a first-order flexible configuration.

    A configuration can be NONRIGID (``ker(M) != {0}``) and still be a strict
    local maximum.  The decisive objects, all exact:

    * a strictly positive stress ``y`` with ``M^T y = 0``.  Its existence
      collapses the feasible cone: for any ``v`` with ``Mv >= 0``,
      ``y^T M v = 0`` with ``y > 0`` forces ``Mv = 0``, so ``C(H) = ker(M)``
      and no cone direction escapes the flex space.
    * the stress-weighted second-order form ``Q(v) = sum_e y_e D^2 A_e(v,v)``
      on that flex space.  Because ``grad L = 0`` for ``L = sum_e y_e A_e +
      sum_j y_j g_j`` and the domain constraints are affine, the ``t^2``
      coefficient of ``L`` along *any* feasible curve with tangent ``v`` is
      ``Q(v)/2`` — the curve's second-order correction drops out.  With
      ``min_e A_e <= L / sum_e y_e``, ``Q(v) < 0`` for every nonzero ``v`` in
      the flex space makes the configuration a strict local maximum.

    This is prestress stability in the sense of Connelly & Whiteley, *Second-
    order rigidity and prestress stability for tensegrity frameworks*, SIAM J.
    Discrete Math. 9 (1996) 453-491, transported from bar-and-joint frameworks
    to the area hypergraph.

    NOTE: the affine-domain hypothesis is used.  ``Square`` and ``Polygon``
    satisfy it; ``Disk`` does not (its constraint is quadratic), so a disk
    configuration would need the boundary curvature term as well and is
    refused here rather than answered wrongly.
    """

    stress: Tuple[object, ...] | None
    flex_dimension: int
    second_order_form: object | None
    cone_equals_kernel: bool
    detail: str


def doubled_area_quadratic_coefficient(system: ActiveSystem, triple, velocity):
    """Exact ``t^2`` coefficient of the oriented doubled area along ``v``.

    A determinant is exactly quadratic along a line, so evaluating at
    ``t = 0, +1, -1`` and taking second differences is exact, not an estimate.
    Returned in *doubled*-area units, which is also ``D^2 A_e(v,v)`` since
    ``A_e = D_e / 2`` gives ``D^2 A_e(v,v) = 2 * (D_e's t^2 coefficient) / 2``.
    """

    field = system.configuration.field
    points = system.configuration.points
    two = field.from_fraction(2)

    def displaced(step):
        return tuple(
            (points[i][0] + step * velocity[2 * i], points[i][1] + step * velocity[2 * i + 1])
            for i in range(len(points))
        )

    base = _determinant(points, triple, field)
    forward = _determinant(displaced(field.one), triple, field)
    backward = _determinant(displaced(-field.one), triple, field)
    linear = (forward - backward) / two
    quadratic = (forward + backward) / two - base
    if base.sign() < 0:
        linear, quadratic = -linear, -quadratic
    return linear, quadratic


def prestress_analysis(system: ActiveSystem) -> PrestressAnalysis:
    """Exact prestress-stability analysis of a first-order flexible system."""

    field = system.configuration.field
    if system.configuration.domain.symmetry is not None or not isinstance(
        system.configuration.domain, (Square, Polygon)
    ):
        return PrestressAnalysis(
            None, 0, None, False,
            "refused: the barrier argument assumes affine domain constraints",
        )

    stress = _propose_stress(system)
    if stress is None:
        return PrestressAnalysis(None, 0, None, False, "no strictly positive stress found")
    _verify_stress(system, stress)

    flex = kernel(system.rows, system.dimension, field)
    if len(flex) != 1:
        return PrestressAnalysis(
            tuple(stress), len(flex), None, True,
            f"cone equals ker(M) (dimension {len(flex)}); "
            "definiteness on a multi-dimensional flex space is not decided here",
        )

    velocity = flex[0]
    total = field.zero
    for index, triple in enumerate(system.active_triangles):
        linear, quadratic = doubled_area_quadratic_coefficient(system, triple, velocity)
        if not linear.is_zero():
            raise CertificateRejected(
                f"active area {triple} is not stationary along a kernel direction"
            )
        total = total + stress[index] * quadratic
    return PrestressAnalysis(
        tuple(stress), 1, total, True,
        "cone equals ker(M), one-dimensional; Q < 0 certifies a strict local maximum"
        if total.sign() < 0
        else "cone equals ker(M), one-dimensional; Q is not negative",
    )
