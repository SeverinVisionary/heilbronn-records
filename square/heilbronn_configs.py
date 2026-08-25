"""Registry of exact best-known Heilbronn configurations, with provenance.

Every entry carries the published minimum area as an exact expression in the
configuration's own field, and ``load`` asserts that the value recomputed from
the coordinates equals it.  A transcription error therefore fails loudly
instead of producing a plausible-looking audit of the wrong configuration.

Sources
-------
* Comellas & Yebra, "New lower bounds for Heilbronn numbers", Electron. J.
  Combin. 9 (2002) #R6, §3 (square n = 7..12; the n = 11 entry is Goldberg's).
* M. Goldberg, "Maximizing the smallest triangle made by N points in a
  square", Math. Magazine 45 (1972) 135-144 (n = 11).
* Record status per Erich Friedman, "The Heilbronn Problem for Squares"
  (re-fetched 2026-08-21) and arXiv:2603.11107v2.
"""

from __future__ import annotations

from fractions import Fraction as F
from typing import Callable, Dict, Tuple

from exact_field import NumberField, RationalField, sqrt_field
from rigidity_engine import Configuration, Square


def _points(field, rows) -> Tuple[Tuple[object, object], ...]:
    return tuple((field.from_fraction(x) if isinstance(x, (int, F)) else x,
                  field.from_fraction(y) if isinstance(y, (int, F)) else y) for x, y in rows)


def square_n11_goldberg() -> Tuple[Configuration, object]:
    """Goldberg 1972, H_11 >= 1/27.  Fully rational; the oldest surviving square record."""

    field = RationalField()
    rows = [
        (F(1, 3), F(0)), (F(2, 3), F(0)),
        (F(0), F(2, 9)), (F(1), F(2, 9)),
        (F(1, 3), F(4, 9)), (F(2, 3), F(4, 9)),
        (F(0), F(2, 3)), (F(1), F(2, 3)),
        (F(1, 2), F(7, 9)),
        (F(1, 6), F(1)), (F(5, 6), F(1)),
    ]
    configuration = Configuration(
        label="square-n11-goldberg",
        field=field,
        points=_points(field, rows),
        domain=Square(),
        source="Goldberg 1972; coordinates as tabulated in Comellas-Yebra 2002 §3",
        published_value="1/27",
    )
    return configuration, field.from_fraction(F(1, 27))


def square_n12_comellas_yebra() -> Tuple[Configuration, object]:
    """The campaign incumbent: H_12 >= x/4 + xy/2 - x^2/2 with 4x^3-12x^2+10x-1 = 0."""

    field = NumberField((F(-1), F(10), F(-12), F(4)), (F(0), F(1, 4)), name="x")
    x = field.generator
    y = x * x * field.from_fraction(2) - x * field.from_fraction(3) + field.from_fraction(F(1, 2))
    one = field.one
    half = field.from_fraction(F(1, 2))
    rows = [
        (x, field.zero), (one - x, field.zero),
        (field.zero, x), (one, x),
        (half, y), (y, half), (one - y, half), (half, one - y),
        (field.zero, one - x), (one, one - x),
        (x, one), (one - x, one),
    ]
    value = x * field.from_fraction(F(1, 4)) + x * y * half - x * x * half
    configuration = Configuration(
        label="square-n12-comellas-yebra",
        field=field,
        points=tuple(rows),
        domain=Square(),
        source="Comellas-Yebra 2002 §3 (twelve points)",
        published_value="x/4 + xy/2 - x^2/2 = 0.032598858691819698...",
    )
    return configuration, value


def square_n10_comellas_yebra() -> Tuple[Configuration, object]:
    """H_10 >= 5z^2/8 - z^3/2 with 12z^3 - 27z^2 + 20z - 4 = 0, z = 0.315611...

    The cubic is derived from the paper's radical form: with u^3 = 63 + 8*sqrt(62)
    and w = u + 1/u one has w^3 - 3w - 126 = 0 (using (63)^2 - 62*8^2 = 1), and
    z = 3/4 - w/12.
    """

    field = NumberField((F(-4), F(20), F(-27), F(12)), (F(3, 10), F(8, 25)), name="z")
    z = field.generator
    x = z / field.from_fraction(2)
    y = field.one - z * field.from_fraction(3) + z * z * field.from_fraction(2)
    one, zero = field.one, field.zero
    rows = [
        (x, zero), (one - y, zero),
        (zero, x), (one, y),
        (one - z, z), (z, one - z),
        (zero, one - y), (one, one - x),
        (y, one), (one - x, one),
    ]
    value = z * z * field.from_fraction(F(5, 8)) - z * z * z * field.from_fraction(F(1, 2))
    configuration = Configuration(
        label="square-n10-comellas-yebra",
        field=field,
        points=tuple(rows),
        domain=Square(),
        source="Comellas-Yebra 2002 §3 (ten points)",
        published_value="5z^2/8 - z^3/2 = 0.046537...",
    )
    return configuration, value


def square_n8_comellas_yebra() -> Tuple[Configuration, object]:
    """H_8 = (sqrt(13) - 1)/36, proved optimal by Dehbi & Zeng 2022."""

    field = sqrt_field(13, name="r13")
    r = field.generator
    one, zero = field.one, field.zero
    rows = [
        (zero, zero),
        ((one + r) / field.from_fraction(6), zero),
        (one, (field.from_fraction(7) - r) / field.from_fraction(18)),
        ((field.from_fraction(5) - r) / field.from_fraction(6), (field.from_fraction(7) - r) / field.from_fraction(9)),
        ((one + r) / field.from_fraction(6), (field.from_fraction(2) + r) / field.from_fraction(9)),
        (zero, (field.from_fraction(11) + r) / field.from_fraction(18)),
        ((field.from_fraction(5) - r) / field.from_fraction(6), one),
        (one, one),
    ]
    value = (r - one) / field.from_fraction(36)
    configuration = Configuration(
        label="square-n8-comellas-yebra",
        field=field,
        points=tuple(rows),
        domain=Square(),
        source="Comellas-Yebra 2002 §3 (eight points); optimal per Dehbi-Zeng 2022",
        published_value="(sqrt(13)-1)/36 = 0.072376...",
    )
    return configuration, value



def square_n7_comellas_yebra() -> Tuple[Configuration, object]:
    """H_7 = (1 - 14z - 2z^2)/38 with z^3 + 5z^2 - 5z + 1 = 0, z = 0.287258...

    The cubic is TOTALLY REAL (roots -5.879, 0.287258, 0.592104), so the
    isolating interval must be (1/4, 1/2): a wider one would select a conjugate
    configuration silently.  ``NumberField`` enforces this with a Sturm count.
    Proved optimal by Zeng & Chen 2011.
    """

    field = NumberField((F(1), F(-5), F(5), F(1)), (F(1, 4), F(1, 2)), name="z")
    z = field.generator
    one, zero = field.one, field.zero
    q = lambda a, b=1: field.from_fraction(F(a, b))

    rows = [
        (-z * q(50, 19) - z * z * q(17, 38) + q(37, 38), zero),
        (one, zero),
        (zero, z),
        (q(9, 19) + z * z * q(1, 19) + z * q(7, 19), z),
        (z * z * q(40, 19) + z * q(223, 19) - q(58, 19), -one + z * q(6) + z * z),
        (z * q(58, 19) - q(15, 19) + z * z * q(11, 19), one),
        (one, one),
    ]
    # The paper prints this constant in a sign convention that evaluates
    # negative at its own stated root z = 0.287258; the magnitude matches its
    # decimal 0.083859, and this form is what the coordinates reproduce.
    value = (z * q(14) + z * z * q(2) - one) / q(38)
    configuration = Configuration(
        label="square-n7-comellas-yebra",
        field=field,
        points=tuple(rows),
        domain=Square(),
        source="Comellas-Yebra 2002 §3 (seven points); optimal per Zeng-Chen 2011",
        published_value="(14z+2z^2-1)/38 = 0.083859009007513... (paper prints 0.083859)",
    )
    return configuration, value


def square_n9_comellas_yebra() -> Tuple[Configuration, object]:
    """H_9 = (9*sqrt(65) - 55)/320, proved optimal by Sudermann-Merx 2026."""

    field = sqrt_field(65, name="r65")
    r = field.generator
    one, zero = field.one, field.zero
    q = lambda a, b=1: field.from_fraction(F(a, b))

    rows = [
        ((q(10) - r) / q(10), zero),
        ((q(25) + r) / q(40), zero),
        (zero, (q(15) - r) / q(40)),
        (one, (q(15) - r) / q(40)),
        ((q(15) - r) / q(20), (q(5) + r) / q(20)),
        (zero, (q(35) + r * q(3)) / q(80)),
        (one, r / q(10)),
        ((q(45) - r * q(3)) / q(80), one),
        ((q(25) + r) / q(40), one),
    ]
    value = (r * q(9) - q(55)) / q(320)
    configuration = Configuration(
        label="square-n9-comellas-yebra",
        field=field,
        points=tuple(rows),
        domain=Square(),
        source="Comellas-Yebra 2002 §3 (nine points); optimal per Sudermann-Merx 2026",
        published_value="(9*sqrt(65)-55)/320 = 0.054876...",
    )
    return configuration, value


REGISTRY: Dict[str, Callable[[], Tuple[Configuration, object]]] = {
    "square-n7": square_n7_comellas_yebra,
    "square-n8": square_n8_comellas_yebra,
    "square-n9": square_n9_comellas_yebra,
    "square-n10": square_n10_comellas_yebra,
    "square-n11": square_n11_goldberg,
    "square-n12": square_n12_comellas_yebra,
}


def load(name: str, *, check: bool = True) -> Configuration:
    """Build a registered configuration and verify its published minimum area."""

    configuration, expected = REGISTRY[name]()
    if check:
        from rigidity_engine import build_active_system

        system = build_active_system(configuration)
        computed = system.minimum_area_doubled / configuration.field.from_fraction(2)
        if not (computed - expected).is_zero():
            raise AssertionError(
                f"{name}: recomputed minimum area {computed.to_float():.15f} does not equal the "
                f"published value {expected.to_float():.15f} — coordinates are mis-transcribed"
            )
    return configuration
