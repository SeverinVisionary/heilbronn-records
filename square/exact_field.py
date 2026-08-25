"""Exact arithmetic over Q and over a real algebraic extension Q(alpha).

The n=12 scanner works in one hardcoded cubic field (``incumbent.Qx``).  The
generalized rigidity engine has to audit configurations whose coordinates are
rational (the whole unit-disk table, square n=6 and n=11), quadratic
(``sqrt(13)``, ``sqrt(65)``), or cubic (n=7, n=10, n=12), so it needs one
arithmetic interface that covers all of them.

Both element types expose the same protocol the engine uses:
``+ - * /``, unary ``-``, ``is_zero()``, ``sign()``, ``to_float()``, and
comparison against zero through ``sign``.  Every decision is exact: signs of
algebraic numbers are decided by refining an isolating interval of ``alpha``
until interval evaluation of the representing polynomial has a constant sign,
which terminates precisely because the minimal polynomial is irreducible and
therefore no nonzero polynomial of smaller degree vanishes at ``alpha``.

Irreducibility is *checked*, not assumed, for degrees 2 and 3 (rational-root
test); higher degrees must be declared by the caller with
``assume_irreducible=True``, which is recorded on the field so a write-up can
state the assumption instead of hiding it.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import List, Sequence, Tuple

Number = Fraction


class RefinementBudgetExhausted(ArithmeticError):
    """Sign refinement ran out of bisections; never a soundness failure.

    Deliberately NOT an AssertionError: certificate verifiers catch
    AssertionError subclasses to reject a candidate, and a budget limit must
    never be silently read as "certificate rejected".
    """


def _poly_trim(coefficients: Sequence[Fraction]) -> Tuple[Fraction, ...]:
    result = list(coefficients)
    while result and result[-1] == 0:
        result.pop()
    return tuple(result)


def _poly_multiply(left: Sequence[Fraction], right: Sequence[Fraction]) -> Tuple[Fraction, ...]:
    if not left or not right:
        return ()
    product = [Fraction(0)] * (len(left) + len(right) - 1)
    for i, a in enumerate(left):
        if a == 0:
            continue
        for j, b in enumerate(right):
            if b == 0:
                continue
            product[i + j] += a * b
    return _poly_trim(product)


def _poly_subtract(left: Sequence[Fraction], right: Sequence[Fraction]) -> Tuple[Fraction, ...]:
    width = max(len(left), len(right))
    padded_left = list(left) + [Fraction(0)] * (width - len(left))
    padded_right = list(right) + [Fraction(0)] * (width - len(right))
    return _poly_trim([a - b for a, b in zip(padded_left, padded_right)])


def _poly_divmod(
    numerator: Sequence[Fraction], denominator: Sequence[Fraction]
) -> Tuple[Tuple[Fraction, ...], Tuple[Fraction, ...]]:
    remainder = list(_poly_trim(numerator))
    divisor = _poly_trim(denominator)
    if not divisor:
        raise ZeroDivisionError("polynomial division by zero")
    quotient = [Fraction(0)] * max(0, len(remainder) - len(divisor) + 1)
    while len(remainder) >= len(divisor):
        shift = len(remainder) - len(divisor)
        factor = remainder[-1] / divisor[-1]
        quotient[shift] = factor
        for index, value in enumerate(divisor):
            remainder[shift + index] -= factor * value
        remainder = list(_poly_trim(remainder))
    return _poly_trim(quotient), _poly_trim(remainder)


def _poly_evaluate(coefficients: Sequence[Fraction], point: Fraction) -> Fraction:
    total = Fraction(0)
    for value in reversed(coefficients):
        total = total * point + value
    return total


def _poly_evaluate_interval(
    coefficients: Sequence[Fraction], low: Fraction, high: Fraction
) -> Tuple[Fraction, Fraction]:
    """Interval Horner evaluation; returns an enclosure of p([low, high])."""

    lower = upper = Fraction(0)
    for value in reversed(coefficients):
        candidates = (lower * low, lower * high, upper * low, upper * high)
        lower, upper = min(candidates) + value, max(candidates) + value
    return lower, upper


def _poly_derivative(coefficients: Sequence[Fraction]) -> Tuple[Fraction, ...]:
    return _poly_trim([value * index for index, value in enumerate(coefficients)][1:])


def _sturm_chain(coefficients: Sequence[Fraction]) -> List[Tuple[Fraction, ...]]:
    """Sturm chain of a squarefree polynomial (an irreducible one always is)."""

    chain = [_poly_trim(coefficients), _poly_derivative(coefficients)]
    while len(chain[-1]) > 1:
        _, remainder = _poly_divmod(chain[-2], chain[-1])
        if not remainder:
            break
        chain.append(_poly_trim([-value for value in remainder]))
    return chain


def _sign_variations(chain: Sequence[Sequence[Fraction]], point: Fraction) -> int:
    signs = []
    for polynomial in chain:
        value = _poly_evaluate(polynomial, point)
        if value != 0:
            signs.append(1 if value > 0 else -1)
    return sum(1 for a, b in zip(signs, signs[1:]) if a != b)


def real_root_count(coefficients: Sequence[Fraction], low: Fraction, high: Fraction) -> int:
    """Exact number of distinct real roots in the half-open interval ``(low, high]``."""

    chain = _sturm_chain(coefficients)
    return _sign_variations(chain, low) - _sign_variations(chain, high)


def _rational_root_candidates(coefficients: Sequence[Fraction]) -> List[Fraction]:
    """All rational roots admissible by the rational-root theorem."""

    scale = 1
    for value in coefficients:
        scale = scale * value.denominator // _gcd(scale, value.denominator)
    integral = [int(value * scale) for value in coefficients]
    while integral and integral[-1] == 0:
        integral.pop()
    if not integral:
        return []
    # A vanishing constant term means 0 is a root (the polynomial is divisible by
    # x), which the p/q enumeration below cannot express.  Reported by the 2026-08-21
    # panel: without this, x^3-2x = x(x^2-2) was accepted as irreducible, and in
    # such a ring the coefficient-vector zero test is no longer a field zero test.
    if integral[0] == 0:
        return [Fraction(0)]
    constant = integral[0]
    leading = integral[-1]
    candidates = []
    for numerator in _divisors(abs(constant)):
        for denominator in _divisors(abs(leading)):
            for signum in (1, -1):
                candidates.append(Fraction(signum * numerator, denominator))
    return candidates


def _gcd(left: int, right: int) -> int:
    while right:
        left, right = right, left % right
    return abs(left) or 1


def _divisors(value: int) -> List[int]:
    if value == 0:
        return [1]
    found = []
    candidate = 1
    while candidate * candidate <= value:
        if value % candidate == 0:
            found.append(candidate)
            found.append(value // candidate)
        candidate += 1
    return sorted(set(found))


@dataclass(frozen=True)
class RationalElement:
    """An element of Q, with the engine's exact-number protocol."""

    value: Fraction

    def __add__(self, other: "RationalElement") -> "RationalElement":
        return RationalElement(self.value + other.value)

    def __sub__(self, other: "RationalElement") -> "RationalElement":
        return RationalElement(self.value - other.value)

    def __mul__(self, other: "RationalElement") -> "RationalElement":
        return RationalElement(self.value * other.value)

    def __truediv__(self, other: "RationalElement") -> "RationalElement":
        if other.value == 0:
            raise ZeroDivisionError("division by zero in Q")
        return RationalElement(self.value / other.value)

    def __neg__(self) -> "RationalElement":
        return RationalElement(-self.value)

    def is_zero(self) -> bool:
        return self.value == 0

    def sign(self) -> int:
        return (self.value > 0) - (self.value < 0)

    def to_float(self) -> float:
        return float(self.value)

    def __repr__(self) -> str:  # pragma: no cover - display only
        return f"Q({self.value})"


class RationalField:
    """The field Q, presented with the same interface as ``NumberField``."""

    degree = 1
    assumed_irreducible = False

    def from_fraction(self, value) -> RationalElement:
        return RationalElement(Fraction(value))

    @property
    def zero(self) -> RationalElement:
        return RationalElement(Fraction(0))

    @property
    def one(self) -> RationalElement:
        return RationalElement(Fraction(1))

    def __repr__(self) -> str:  # pragma: no cover - display only
        return "Q"


@dataclass(frozen=True)
class NumberFieldElement:
    """An element of Q(alpha), stored as coefficients of degree < deg(alpha)."""

    field: "NumberField"
    coefficients: Tuple[Fraction, ...]

    def _combine(self, other: "NumberFieldElement", subtract: bool = False) -> "NumberFieldElement":
        if other.field is not self.field:
            raise ValueError("elements of different fields cannot be combined")
        width = max(len(self.coefficients), len(other.coefficients))
        left = list(self.coefficients) + [Fraction(0)] * (width - len(self.coefficients))
        right = list(other.coefficients) + [Fraction(0)] * (width - len(other.coefficients))
        combined = [a - b if subtract else a + b for a, b in zip(left, right)]
        return NumberFieldElement(self.field, _poly_trim(combined))

    def __add__(self, other: "NumberFieldElement") -> "NumberFieldElement":
        return self._combine(other)

    def __sub__(self, other: "NumberFieldElement") -> "NumberFieldElement":
        return self._combine(other, subtract=True)

    def __mul__(self, other: "NumberFieldElement") -> "NumberFieldElement":
        if other.field is not self.field:
            raise ValueError("elements of different fields cannot be combined")
        product = _poly_multiply(self.coefficients, other.coefficients)
        return NumberFieldElement(self.field, self.field.reduce(product))

    def __neg__(self) -> "NumberFieldElement":
        return NumberFieldElement(self.field, _poly_trim([-value for value in self.coefficients]))

    def __truediv__(self, other: "NumberFieldElement") -> "NumberFieldElement":
        return self * other.inverse()

    def inverse(self) -> "NumberFieldElement":
        if self.is_zero():
            raise ZeroDivisionError("division by zero in Q(alpha)")
        # Extended Euclid against the minimal polynomial: gcd is a nonzero
        # constant because the minimal polynomial is irreducible.
        old_remainder, remainder = self.field.minimal_polynomial, _poly_trim(self.coefficients)
        old_cofactor: Tuple[Fraction, ...] = ()
        cofactor: Tuple[Fraction, ...] = (Fraction(1),)
        while remainder:
            quotient, next_remainder = _poly_divmod(old_remainder, remainder)
            old_remainder, remainder = remainder, next_remainder
            old_cofactor, cofactor = (
                cofactor,
                _poly_subtract(old_cofactor, _poly_multiply(quotient, cofactor)),
            )
        if len(old_remainder) != 1:
            raise AssertionError("minimal polynomial is not irreducible: gcd is nonconstant")
        scale = old_remainder[0]
        inverse = _poly_trim([value / scale for value in old_cofactor])
        return NumberFieldElement(self.field, self.field.reduce(inverse))

    def is_zero(self) -> bool:
        return not _poly_trim(self.coefficients)

    def sign(self) -> int:
        if self.is_zero():
            return 0
        return self.field.sign_of(self.coefficients)

    def to_float(self) -> float:
        return float(_poly_evaluate(self.coefficients, Fraction(self.field.approximate_root())))

    def __repr__(self) -> str:  # pragma: no cover - display only
        return f"{self.field}({list(self.coefficients)})"


class NumberField:
    """Q(alpha) for a real root ``alpha`` isolated in a rational interval.

    ``minimal_polynomial`` is given in ascending coefficient order and must be
    irreducible over Q; ``interval`` must contain exactly that one real root,
    with the polynomial taking opposite nonzero signs at the endpoints.
    """

    def __init__(
        self,
        minimal_polynomial: Sequence[Fraction],
        interval: Tuple[Fraction, Fraction],
        *,
        name: str = "alpha",
        assume_irreducible: bool = False,
    ) -> None:
        polynomial = _poly_trim([Fraction(value) for value in minimal_polynomial])
        if len(polynomial) < 2:
            raise ValueError("the minimal polynomial must have degree at least 1")
        self.minimal_polynomial = polynomial
        self.degree = len(polynomial) - 1
        self.name = name
        low, high = Fraction(interval[0]), Fraction(interval[1])
        if low >= high:
            raise ValueError("the isolating interval must be nonempty")
        value_low = _poly_evaluate(polynomial, low)
        value_high = _poly_evaluate(polynomial, high)
        if value_low == 0 or value_high == 0:
            raise ValueError("the isolating interval must not have a root at an endpoint")
        if (value_low > 0) == (value_high > 0):
            raise ValueError("the minimal polynomial must change sign across the interval")
        self._low, self._high = low, high
        self.assumed_irreducible = assume_irreducible
        self._check_irreducible(assume_irreducible)
        # A sign change only proves an ODD number of roots.  With three real
        # roots in the interval, ring arithmetic stays valid but sign() and
        # to_float() would silently describe a different real embedding — a
        # conjugate configuration — and the registry's is_zero() guard, being
        # embedding-independent, would not catch it.  Reported by the
        # 2026-08-21 panel; matters as soon as a totally real field appears.
        count = real_root_count(polynomial, low, high)
        if count != 1:
            raise ValueError(
                f"the interval ({low}, {high}] contains {count} real roots of the minimal "
                "polynomial; it must isolate exactly one"
            )

    def _check_irreducible(self, assume_irreducible: bool) -> None:
        if self.degree == 1:
            return
        if self.degree in (2, 3):
            for candidate in _rational_root_candidates(self.minimal_polynomial):
                if _poly_evaluate(self.minimal_polynomial, candidate) == 0:
                    raise ValueError(
                        f"degree-{self.degree} minimal polynomial has the rational root {candidate}"
                    )
            return
        if not assume_irreducible:
            raise ValueError(
                "irreducibility of a degree >= 4 minimal polynomial must be declared "
                "explicitly with assume_irreducible=True"
            )

    def reduce(self, coefficients: Sequence[Fraction]) -> Tuple[Fraction, ...]:
        _, remainder = _poly_divmod(coefficients, self.minimal_polynomial)
        return remainder

    def from_fraction(self, value) -> NumberFieldElement:
        return NumberFieldElement(self, _poly_trim([Fraction(value)]))

    @property
    def zero(self) -> NumberFieldElement:
        return NumberFieldElement(self, ())

    @property
    def one(self) -> NumberFieldElement:
        return NumberFieldElement(self, (Fraction(1),))

    @property
    def generator(self) -> NumberFieldElement:
        return NumberFieldElement(self, self.reduce((Fraction(0), Fraction(1))))

    def bounds(self) -> Tuple[Fraction, Fraction]:
        return self._low, self._high

    def refine_to(self, width: Fraction) -> None:
        """Bisect the isolating interval until it is narrower than ``width``."""

        while self._high - self._low > width:
            self._bisect()

    def approximate_root(self, width: Fraction = Fraction(1, 10 ** 25)) -> Fraction:
        self.refine_to(width)
        return (self._low + self._high) / 2

    def _bisect(self) -> None:
        middle = (self._low + self._high) / 2
        value_middle = _poly_evaluate(self.minimal_polynomial, middle)
        if value_middle == 0:
            raise AssertionError("a rational root contradicts irreducibility")
        value_low = _poly_evaluate(self.minimal_polynomial, self._low)
        if (value_low > 0) != (value_middle > 0):
            self._high = middle
        else:
            self._low = middle

    def sign_of(self, coefficients: Sequence[Fraction], *, max_refinements: int | None = None) -> int:
        """Exact sign of ``p(alpha)`` for a nonzero ``p`` of degree < deg(alpha).

        Termination is guaranteed: the minimal polynomial is irreducible and
        ``deg p < deg(alpha)``, so ``p(alpha) != 0`` and some finite refinement
        separates it from zero.  Only the *budget* can run out, and the budget
        needed grows with the height of ``p`` — each bisection buys one bit — so
        it is scaled from the coefficients rather than fixed.  A fixed cap of 400
        was reported by the 2026-08-21 panel: it rejected a legitimate value of
        height 2^444 while blaming the field.
        """

        trimmed = _poly_trim(coefficients)
        if not trimmed:
            return 0
        if len(trimmed) == 1:
            return (trimmed[0] > 0) - (trimmed[0] < 0)
        if max_refinements is None:
            height = max(
                max(abs(value.numerator).bit_length(), value.denominator.bit_length())
                for value in trimmed
            )
            max_refinements = 64 + 4 * height
        for _ in range(max_refinements):
            low, high = _poly_evaluate_interval(trimmed, self._low, self._high)
            if low > 0:
                return 1
            if high < 0:
                return -1
            self._bisect()
        raise RefinementBudgetExhausted(
            f"sign refinement budget of {max_refinements} bisections exhausted; the value is "
            "provably nonzero in an irreducible field, so this is a budget limit, not a "
            "soundness failure — re-call with a larger max_refinements"
        )

    def __repr__(self) -> str:  # pragma: no cover - display only
        return f"Q({self.name})"


def sqrt_field(radicand: int, *, name: str | None = None) -> NumberField:
    """Q(sqrt(radicand)) for a positive non-square integer."""

    root = int(radicand ** 0.5)
    while root * root < radicand:
        root += 1
    while root * root > radicand:
        root -= 1
    if root * root == radicand:
        raise ValueError("radicand is a perfect square; use RationalField")
    return NumberField(
        (Fraction(-radicand), Fraction(0), Fraction(1)),
        (Fraction(root), Fraction(root + 1)),
        name=name or f"sqrt{radicand}",
    )
