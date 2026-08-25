"""The published record for n points in a CIRCLE, and how to compare against it.

Two sources, and they do not agree everywhere.

PRIMARY -- Erich Friedman, "The Heilbronn Problem for Circles".  That page lives
at its own path, NOT under the Packing Center index, which is why an earlier
prior-art check in this repo missed it.  Values are for the UNIT-RADIUS circle
and are printed to only 3-4 significant digits with a trailing "+", e.g.
".113+", so a row can be *matched* but a small excess over it cannot be
resolved.  The normalization is confirmed by the page's own n=5 closed form
sqrt(50 - 10 sqrt 5)/8 = 0.657163890148917, which is exactly the regular
pentagon inscribed in the unit-radius circle.

SECONDARY -- MathWorld's Heilbronn Triangle Problem table, UNIT-AREA circle,
attributed to Friedman (2007) and D. Cantrell (pers. comm. 2007-06-18).  Convert
with alpha_disk = pi * H.  MathWorld carries more digits and agrees with
Friedman at n = 7..10 and 12..16.

KNOWN ERRATUM.  At n=11 the two disagree and MathWorld is wrong:
    MathWorld  H_11 = 0.03494193340280051  ->  pi * H = 0.109773530502
    Friedman   A_11 = ".113+", David Cantrell, August 2006, horizontally symmetric
A configuration achieving 0.113938117431 exists (circle_configs/circle_n11.json)
and falls inside Friedman's ".113+" bracket.  So that row is NOT soft: the
softness audit's ~13.5% outlier at n=11 was detecting the MathWorld database
error, not an under-optimized configuration.

Consequence for claims: a row counts as improved only if it exceeds the PRIMARY
bracket.  Beating the MathWorld number alone proves nothing at n=11, and
elsewhere the printed precision is what limits the claim.
"""
from fractions import Fraction as F

# pi to 60 digits: the unit-area -> unit-radius transport stays in exact rationals.
PI = F("3.14159265358979323846264338327950288419716939937510582097494")

# MathWorld, UNIT-AREA circle.  Six decimals except where the source prints more.
MATHWORLD_UNIT_AREA = {
    7: "0.093700", 8: "0.069055", 9: "0.05531071895608711", 10: "0.047869",
    11: "0.03494193340280051", 12: "0.03339560352492413",
    13: "0.02726586326658908", 14: "0.02414611295141071",
    15: "0.02229427231706078", 16: "0.021051",
}

# Friedman, UNIT-RADIUS circle, as printed with a trailing "+".  PRIMARY.
# The true value lies in [printed, printed + 1 ulp of the last printed digit),
# so only 3-4 significant figures are resolvable and a small excess cannot be
# claimed.  The page also annotates a symmetry class for every row (below).
FRIEDMAN_UNIT_RADIUS = {
    7: "0.294", 8: "0.216", 9: "0.173", 10: "0.150", 11: "0.113",
    12: "0.104", 13: "0.0856", 14: "0.0758", 15: "0.0700", 16: "0.0661",
}

# Friedman's stated symmetry class for each of Cantrell's configurations.  If the
# 2007 table was produced under a symmetry ansatz, a row can only be improved by
# leaving its class -- so this is the thing to test an unrestricted search against.
FRIEDMAN_SYMMETRY = {
    7: "completely symmetric", 8: "completely symmetric",
    9: "horizontally symmetric", 10: "completely symmetric",
    11: "horizontally symmetric", 12: "symmetry of an equilateral triangle",
    13: "horizontally symmetric", 14: "horizontally symmetric",
    15: "horizontally symmetric", 16: "symmetry of a square",
}

# A relative margin below this cannot be claimed as an improvement: the primary
# source prints only 3-4 significant figures.
CLAIM_FLOOR = 5e-4

MATHWORLD_ERRATA = {
    11: "MathWorld's n=11 row (0.03494193340280051 unit-area = 0.109773530502 "
        "unit-radius) is below Friedman/Cantrell's .113+ unit-radius value. "
        "MathWorld is in error; Friedman is primary.",
}


def mathworld_lower(n):
    """MathWorld's printed value transported to the unit-radius disk."""
    return F(MATHWORLD_UNIT_AREA[n]) * PI


def mathworld_upper(n):
    """Largest value MathWorld's printed decimal could stand for."""
    d = len(MATHWORLD_UNIT_AREA[n].split(".")[1])
    return (F(MATHWORLD_UNIT_AREA[n]) + F(5, 10 ** (d + 1))) * PI


def friedman_bracket(n):
    """(lower, upper) that Friedman's printed 'x+' can stand for, unit radius."""
    s = FRIEDMAN_UNIT_RADIUS[n]
    d = len(s.split(".")[1])
    return F(s), F(s) + F(1, 10 ** d)


def published_upper(n):
    """The bar a construction must clear to count as an improvement: the largest
    value any published source could be standing for.  Friedman is primary, so
    MathWorld is only consulted where it does not contradict Friedman."""
    hi = friedman_bracket(n)[1]
    if n not in MATHWORLD_ERRATA:
        hi = max(hi, mathworld_upper(n))
    return hi


def classify(n, value):
    """'improves' / 'matches' / 'below', against the PRIMARY record.

    'improves' additionally requires clearing CLAIM_FLOOR, because a margin
    smaller than the source's printed precision is not a claim."""
    hi = published_upper(n)
    if value >= hi and float(value / hi) - 1.0 >= CLAIM_FLOOR:
        return "improves"
    if value >= friedman_bracket(n)[0]:
        return "matches"
    return "below"
