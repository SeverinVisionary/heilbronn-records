"""Tests for the generalized exact rigidity engine and its configuration registry.

Three kinds of check:

* **field correctness** — arithmetic and exact sign decisions in Q and Q(alpha);
* **equivalence** — the engine must reproduce the audited ``rigidity_core``
  verdict for the n=12 incumbent through independent code;
* **controls with known answers** — a configuration with a point in no active
  triangle must come out NONRIGID and must admit a feasible inward motion of
  that point, and an obviously improvable configuration must yield a verified
  improvement direction, so a passing audit cannot be vacuous.
"""

from fractions import Fraction as F

import pytest

import heilbronn_configs as hc
import rigidity_core as rc
from incumbent import decimal_string
from exact_field import NumberField, RationalField, RefinementBudgetExhausted, sqrt_field
from rigidity_engine import (
    NONRIGID,
    RIGID,
    Configuration,
    Square,
    build_active_system,
    classify,
    improvement_direction,
    kernel,
    prestress_analysis,
    _determinant,
)


def test_rational_and_algebraic_arithmetic_is_exact():
    rationals = RationalField()
    assert (rationals.from_fraction(F(3, 4)) + rationals.from_fraction(F(-1, 3))).value == F(5, 12)

    quadratic = sqrt_field(13)
    root = quadratic.generator
    assert (root * root - quadratic.from_fraction(13)).is_zero()
    assert (root - quadratic.from_fraction(F(36, 10))).sign() == 1
    assert (root - quadratic.from_fraction(F(361, 100))).sign() == -1
    assert (root.inverse() * root - quadratic.one).is_zero()

    cubic = NumberField((F(-1), F(10), F(-12), F(4)), (F(0), F(1, 4)), name="x")
    x = cubic.generator
    identity = (
        x * x * x * cubic.from_fraction(4)
        - x * x * cubic.from_fraction(12)
        + x * cubic.from_fraction(10)
        - cubic.one
    )
    assert identity.is_zero()
    assert abs(x.to_float() - 0.1153538228806843) < 1e-15


def test_reducible_minimal_polynomial_is_rejected():
    with pytest.raises(ValueError):
        NumberField((F(-1), F(0), F(1)), (F(0), F(2)))  # x^2 - 1 factors over Q


@pytest.mark.parametrize("name", sorted(hc.REGISTRY))
def test_registry_entries_reproduce_their_published_minimum_area(name):
    # ``load`` raises unless the recomputed exact minimum equals the published
    # value, so this pins every transcription in the registry.
    configuration = hc.load(name)
    assert configuration.count == int(name.split("n")[-1])


def test_engine_reproduces_the_audited_n12_verdict():
    """Equivalence gate: independent code, no normal form, same verdict.

    The registry lists the twelve points in the paper's order and
    ``rigidity_core`` in its own, so the comparison first recovers the
    relabelling by matching coordinates (a labelling step, not a certificate;
    the points are separated by ~0.1 so the match is unambiguous).
    """

    configuration = hc.load("square-n12")
    system = build_active_system(configuration)
    reference = rc.active_data()

    core_points = [
        (float(decimal_string(x, 20)), float(decimal_string(y, 20))) for x, y in rc.incumbent_points()
    ]
    permutation = []
    for x_value, y_value in configuration.points:
        matches = [
            index
            for index, (x_core, y_core) in enumerate(core_points)
            if abs(x_value.to_float() - x_core) < 1e-12 and abs(y_value.to_float() - y_core) < 1e-12
        ]
        assert len(matches) == 1
        permutation.append(matches[0])
    assert sorted(permutation) == list(range(configuration.count))

    relabelled = tuple(
        sorted(tuple(sorted(permutation[vertex] for vertex in triangle)) for triangle in system.active_triangles)
    )
    assert relabelled == tuple(sorted(tuple(triangle) for triangle in reference.triangles))
    assert len(system.contacts) == len(rc.INWARD_COORDINATES)

    verdict = classify(system)
    assert verdict.status == RIGID
    assert verdict.rank_value == system.dimension
    assert improvement_direction(system) is None


def test_proved_optimal_n8_configuration_is_certified_rigid():
    system = build_active_system(hc.load("square-n8"))
    assert classify(system).status == RIGID
    assert improvement_direction(system) is None


def test_n10_incumbent_has_a_one_dimensional_flex_killed_at_second_order():
    configuration = hc.load("square-n10")
    field = configuration.field
    system = build_active_system(configuration)

    verdict = classify(system)
    assert verdict.status == NONRIGID
    assert verdict.rank_value == system.dimension - 1

    basis = kernel(system.rows, system.dimension, field)
    assert len(basis) == 1
    flex = basis[0]
    moving = [
        index
        for index in range(configuration.count)
        if not flex[2 * index].is_zero() or not flex[2 * index + 1].is_zero()
    ]
    assert len(moving) == configuration.count  # not a rattler: every point moves

    used = set()
    for triangle in system.active_triangles:
        used.update(triangle)
    assert used == set(range(configuration.count))

    def displaced(step):
        return tuple(
            (
                configuration.points[index][0] + step * flex[2 * index],
                configuration.points[index][1] + step * flex[2 * index + 1],
            )
            for index in range(configuration.count)
        )

    one, two = field.one, field.from_fraction(2)
    forward, backward = displaced(one), displaced(-one)
    negative = 0
    for triangle in system.active_triangles:
        base = _determinant(configuration.points, triangle, field)
        orientation = 1 if base.sign() > 0 else -1
        plus = _determinant(forward, triangle, field)
        minus = _determinant(backward, triangle, field)
        linear = (plus - minus) / two
        quadratic = (plus + minus) / two - base
        if orientation < 0:
            linear, quadratic = -linear, -quadratic
        assert linear.is_zero()  # the flex is stationary for every active area
        if quadratic.sign() < 0:
            negative += 1
    assert negative == 12  # the minimum strictly decreases along the flex

    assert improvement_direction(system) is None


def _rattler_configuration() -> Configuration:
    """Three corner points plus an interior point; the unique minimal triangle
    omits the origin, which is therefore free to move inward."""

    field = RationalField()
    points = tuple(
        (field.from_fraction(x), field.from_fraction(y))
        for x, y in ((F(0), F(0)), (F(1), F(0)), (F(0), F(1)), (F(2, 5), F(2, 5)))
    )
    return Configuration(
        label="control-rattler", field=field, points=points, domain=Square(), source="synthetic control"
    )


def test_rattler_control_is_nonrigid_and_the_free_corner_may_move_inward():
    configuration = _rattler_configuration()
    field = configuration.field
    system = build_active_system(configuration)
    assert system.active_triangles == ((1, 2, 3),)

    verdict = classify(system)
    assert verdict.status == NONRIGID
    assert verdict.velocity is not None

    # Point 0 appears in no active triangle, so moving it inward off the corner
    # is feasible: the area row is untouched and both of its contact rows turn
    # strictly positive.  This motion lives in C(H) but not in ker(M) — the
    # distinction the engine's two certificate routes have to respect.
    inward = [field.zero] * system.dimension
    inward[0] = field.one
    inward[1] = field.one
    area_row, contact_rows = system.rows[0], system.rows[1:]
    total = field.zero
    for value, coordinate in zip(area_row, inward):
        total = total + value * coordinate
    assert total.is_zero()
    positive = 0
    for row in contact_rows:
        entry = field.zero
        for value, coordinate in zip(row, inward):
            entry = entry + value * coordinate
        assert entry.sign() >= 0
        positive += entry.sign() > 0
    assert positive == 2


def test_improvable_control_yields_a_verified_improvement_direction():
    """The same control read the other way: moving the interior point away from
    the opposite edge strictly increases the unique minimal triangle, so the
    improvement test must fire.  This keeps 'no improvement found' honest."""

    configuration = _rattler_configuration()
    field = configuration.field
    system = build_active_system(configuration)
    direction = improvement_direction(system)
    assert direction is not None
    assert direction.margin.sign() > 0

    # exact re-check: every active area strictly increases along the direction
    for row in system.rows[: system.triangle_row_count]:
        total = field.zero
        for value, coordinate in zip(row, direction.velocity):
            total = total + value * coordinate
        assert total.sign() > 0


# --- regression tests for defects found by the 2026-08-21 HEAVY panel (Codex leg) ---


def test_polynomial_with_vanishing_constant_term_is_rejected_as_reducible():
    """x^3 - 2x = x(x^2 - 2) was accepted as irreducible.

    The rational-root enumeration builds candidates p/q from divisors of the
    constant term, which cannot express the root 0, so a polynomial divisible by
    x slipped through.  In such a ring the coefficient-vector zero test is no
    longer a field zero test, which would silently unsound every certificate
    decision made in it.
    """

    with pytest.raises(ValueError, match="rational root 0"):
        NumberField((F(0), F(-2), F(0), F(1)), (F(-1, 2), F(1, 2)))


def test_sign_refinement_budget_scales_with_coefficient_height():
    """A fixed 400-bisection cap rejected legitimate values of height ~2^444.

    The element below is a Pell convergent difference: genuinely nonzero, in the
    field, with an irreducible minimal polynomial — the old code raised an
    AssertionError blaming the field.  A budget limit must also never be an
    AssertionError, because certificate verifiers catch those to mean "candidate
    rejected".
    """

    field = sqrt_field(2)
    numerator, denominator = 1, 0
    for _ in range(350):
        numerator, denominator = numerator + 2 * denominator, numerator + denominator
    assert field.sign_of((F(-numerator), F(denominator))) in (1, -1)
    assert not issubclass(RefinementBudgetExhausted, AssertionError)


def test_n10_prestress_stability_is_certified_by_committed_code():
    """The flagship n=10 theorem, pinned end-to-end.

    Both HEAVY-panel legs (2026-08-21) found this result asserted in prose with
    no committed code path: ``classify`` returns NONRIGID as soon as
    ``rank < dim`` and never computes a stress, so the cone-collapse and the
    stress-weighted second-order form existed only in the write-up.
    """

    system = build_active_system(hc.load("square-n10"))
    analysis = prestress_analysis(system)

    # a strictly positive stress exists and is exactly verified inside the call
    assert analysis.stress is not None
    assert all(weight.sign() > 0 for weight in analysis.stress)

    # hence every feasible direction lies in ker(M): the cone cannot escape
    assert analysis.cone_equals_kernel
    assert analysis.flex_dimension == 1

    # and the stress-weighted second-order form is exactly negative
    assert analysis.second_order_form.sign() < 0
    assert abs(analysis.second_order_form.to_float() + 109.24100719117776) < 1e-9


def test_prestress_analysis_refuses_curved_domains():
    """The barrier argument needs affine constraints; a disk must be refused,
    not answered, because its boundary contributes a curvature term."""

    from rigidity_engine import Disk

    field = RationalField()
    points = tuple(
        (field.from_fraction(x), field.from_fraction(y))
        for x, y in ((F(0), F(0)), (F(1, 2), F(0)), (F(0), F(1, 2)), (F(-1, 2), F(-1, 4)))
    )
    configuration = Configuration(
        label="control-disk", field=field, points=points, domain=Disk(), source="synthetic control"
    )
    analysis = prestress_analysis(build_active_system(configuration))
    assert analysis.stress is None
    assert "affine" in analysis.detail


def test_isolating_interval_must_contain_exactly_one_root():
    """A sign change only proves an *odd* root count.

    The Comellas-Yebra n=7 cubic is the live case: z^3 + 5z^2 - 5z + 1 is
    totally real with roots -5.879, 0.287258 and 0.592104, so a careless
    interval selects the wrong real embedding — a conjugate configuration —
    while all ring arithmetic and the registry's is_zero() guard stay happy.
    """

    from exact_field import real_root_count

    cubic = (F(1), F(-5), F(5), F(1))
    assert real_root_count(cubic, F(-10), F(10)) == 3
    assert real_root_count(cubic, F(0), F(1)) == 2

    with pytest.raises(ValueError, match="real roots"):
        NumberField(cubic, (F(-10), F(10)))          # 3 roots, but signs do change

    field = NumberField(cubic, (F(1, 4), F(1, 2)))   # the genuine isolating interval
    assert abs(float(field.approximate_root()) - 0.28725773761738527) < 1e-15


def _disk_configuration() -> Configuration:
    """Six points on a rational circle-inscribed hexagon-ish arrangement."""

    from rigidity_engine import Disk

    field = RationalField()
    # exact rational points on the unit circle via Pythagorean parametrisation
    rationals = [F(0), F(1, 2), F(3, 4), F(-3, 5), F(-4, 5), F(2, 5)]
    points = []
    for index, u in enumerate(rationals):
        x = (1 - u * u) / (1 + u * u)
        y = 2 * u / (1 + u * u)
        if index % 2:
            y = -y
        points.append((field.from_fraction(x), field.from_fraction(y)))
    return Configuration(
        label="control-disk-hexagon", field=field, points=tuple(points), domain=Disk(),
        source="synthetic control: exact rational points on the unit circle",
    )


def test_disk_domain_builds_contacts_gauge_and_strict_rows():
    """The disk path had zero coverage: deleting the whole gauge block used to
    fail no test at all."""

    system = build_active_system(_disk_configuration())

    # every point is exactly on the circle, so every one contributes a contact
    assert len(system.contacts) == 6
    assert all(label == "inside-disk" for _, label in system.contacts)

    # the rotation gauge is present as an opposite row PAIR encoding an equality
    gauge = [label for label in system.row_labels if label.startswith("gauge(")]
    assert gauge == ["gauge(rotation,+)", "gauge(rotation,-)"]
    plus = system.rows[system.row_labels.index("gauge(rotation,+)")]
    minus = system.rows[system.row_labels.index("gauge(rotation,-)")]
    for a, b in zip(plus, minus):
        assert (a + b).is_zero()

    # the rotation generator must annihilate every area row and every radial
    # contact row, which is what makes the gauge slice exact
    field = system.configuration.field
    for label, row in zip(system.row_labels, system.rows):
        if label.startswith("gauge("):
            continue
        total = field.zero
        for value, coordinate in zip(row, plus):
            total = total + value * coordinate
        assert total.is_zero(), f"rotation generator not orthogonal to {label}"

    # disk contacts are non-affine and must be flagged for strict inwardness
    assert len(system.strict_row_indices) == 6


def test_curved_boundary_contacts_reject_tangential_directions():
    """At a curved boundary, r^2 - |p + t v|^2 = -t^2 |v|^2 < 0 for every t > 0,
    so a tangential direction is infeasible even though the linearized contact
    row admits it.  `improvement_direction` must not return such a direction."""

    system = build_active_system(_disk_configuration())
    field = system.configuration.field
    direction = improvement_direction(system)
    if direction is None:
        return  # nothing proposed is trivially safe
    for index in system.strict_row_indices:
        total = field.zero
        for value, coordinate in zip(system.rows[index], direction.velocity):
            total = total + value * coordinate
        assert total.sign() > 0, "tangential (or outward) motion at a curved contact"
