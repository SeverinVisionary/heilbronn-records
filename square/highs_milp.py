"""Numerically solve an emitted Heilbronn MILP with SciPy/HiGHS.

``global_mccormick_relaxation`` deliberately owns the model construction and
the exact witness checks.  This module is only a strict parser for that
module's small CPLEX-LP dialect plus a numerical SciPy/HiGHS bridge.  It makes
the solver experiment reproducible when GLPK's feasibility heuristics stall.

Neither a HiGHS primal nor its dual bound is an exact mathematical
certificate.  In particular, every returned coordinate vector is separately
checked against the *geometric* triangle areas, so a loose MILP lift can never
be mistaken for an improved point configuration.
"""

from __future__ import annotations

import argparse
import math
import re
from collections import defaultdict
from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations
from typing import Mapping, Sequence, Tuple

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import csc_matrix, coo_matrix

from global_mccormick_relaxation import RelaxationModel, _fraction_argument, _product_pair_argument, build_model, signed_area


_NUMBER = r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?"
_TERM = re.compile(
    rf"\s*(?P<sign>[+-])?\s*(?:(?P<coefficient>(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)\s+)?(?P<variable>[A-Za-z_]\w*)"
)
_RELATION = re.compile(rf"(?P<expression>.*?)\s(?P<relation><=|>=|=)\s+(?P<rhs>{_NUMBER})\s*$")
_BOUND = re.compile(rf"\s*(?P<lower>{_NUMBER})\s+<=\s+(?P<variable>\w+)\s+<=\s+(?P<upper>{_NUMBER})\s*$")


@dataclass(frozen=True)
class ParsedMilp:
    """A checked numerical representation of the emitted LP text."""

    variable_names: Tuple[str, ...]
    row_names: Tuple[str, ...]
    matrix: csc_matrix
    row_lower: np.ndarray
    row_upper: np.ndarray
    variable_lower: np.ndarray
    variable_upper: np.ndarray
    integrality: np.ndarray


@dataclass(frozen=True)
class HighsReport:
    """A numerical HiGHS result plus geometry and residual diagnostics."""

    status: int
    message: str
    objective: float | None
    maximization_dual_bound: float | None
    mip_gap: float | None
    mip_nodes: int | None
    maximum_constraint_violation: float | None
    maximum_integrality_violation: float | None
    geometric_minimum_area: float | None
    geometric_minimum_triangle: Tuple[int, int, int] | None
    largest_product_gaps: Tuple[Tuple[float, int, int], ...]
    points: Tuple[Tuple[float, float], ...] | None


def _parse_expression(expression: str) -> Mapping[str, float]:
    """Parse exactly the signed variable-sum grammar emitted by ``_linear``."""

    expression = expression.strip()
    if expression == "0":
        return {}
    position = 0
    terms: defaultdict[str, float] = defaultdict(float)
    while position < len(expression):
        match = _TERM.match(expression, position)
        if match is None or match.end() == position:
            raise ValueError(f"unsupported LP expression near {expression[position:]!r}")
        sign, coefficient, variable = match.group("sign", "coefficient", "variable")
        magnitude = 1.0 if coefficient is None else float(coefficient)
        terms[variable] += -magnitude if sign == "-" else magnitude
        position = match.end()
    return {variable: coefficient for variable, coefficient in terms.items() if coefficient != 0.0}


def parse_model(model: RelaxationModel) -> ParsedMilp:
    """Strictly parse one model emitted by :func:`build_model`.

    The parser does not attempt to accept arbitrary CPLEX-LP.  Failing closed
    on an unfamiliar token is intentional: it prevents a new emitter feature
    from being silently omitted by a numerical experiment.
    """

    lines = model.text.splitlines()
    if lines[:3] != ["Maximize", " objective: z", "Subject To"] or not lines or lines[-1] != "End":
        raise ValueError("unexpected model header or footer")
    section = "rows"
    rows: list[tuple[str, Mapping[str, float], str, float]] = []
    numeric_bounds: dict[str, tuple[float, float]] = {}
    binaries: set[str] = set()
    variables: set[str] = set()
    for raw_line in lines[3:-1]:
        line = raw_line.strip()
        if line == "Bounds":
            if section != "rows":
                raise ValueError("LP Bounds section is out of order")
            section = "bounds"
            continue
        if line == "Binary":
            if section != "bounds":
                raise ValueError("LP Binary section is out of order")
            section = "binary"
            continue
        if not line:
            continue
        if section == "rows":
            if ":" not in line:
                raise ValueError(f"constraint lacks a name: {line!r}")
            name, body = line.split(":", 1)
            relation = _RELATION.fullmatch(body)
            if relation is None:
                raise ValueError(f"unsupported constraint syntax: {line!r}")
            expression = _parse_expression(relation.group("expression"))
            rows.append((name.strip(), expression, relation.group("relation"), float(relation.group("rhs"))))
            variables.update(expression)
        elif section == "bounds":
            bound = _BOUND.fullmatch(line)
            if bound is None:
                raise ValueError(f"unsupported bound syntax: {line!r}")
            variable = bound.group("variable")
            if variable in numeric_bounds:
                raise ValueError(f"duplicate numerical bound for {variable!r}")
            numeric_bounds[variable] = (float(bound.group("lower")), float(bound.group("upper")))
            variables.add(variable)
        else:
            if not re.fullmatch(r"[A-Za-z_]\w*", line):
                raise ValueError(f"unsupported binary variable syntax: {line!r}")
            binaries.add(line)
            variables.add(line)

    if section != "binary":
        raise ValueError("LP omitted Bounds or Binary section")
    unbounded = variables - set(numeric_bounds) - binaries
    if unbounded:
        raise ValueError(f"unbounded nonbinary variables: {sorted(unbounded)!r}")
    if len(binaries) != model.binary_count:
        raise ValueError(f"binary count mismatch: parsed {len(binaries)}, model metadata {model.binary_count}")
    if len({name for name, _, _, _ in rows}) != len(rows):
        raise ValueError("duplicate constraint name")
    if "z" not in variables:
        raise ValueError("objective variable z is absent")

    names = tuple(sorted(variables))
    index = {name: position for position, name in enumerate(names)}
    variable_lower = np.full(len(names), -np.inf)
    variable_upper = np.full(len(names), np.inf)
    integrality = np.zeros(len(names), dtype=np.uint8)
    for variable, (lower, upper) in numeric_bounds.items():
        variable_lower[index[variable]] = lower
        variable_upper[index[variable]] = upper
    for variable in binaries:
        variable_lower[index[variable]] = 0.0
        variable_upper[index[variable]] = 1.0
        integrality[index[variable]] = 1

    coefficients: list[float] = []
    row_indices: list[int] = []
    column_indices: list[int] = []
    row_lower: list[float] = []
    row_upper: list[float] = []
    for row_index, (_, expression, relation, rhs) in enumerate(rows):
        for variable, coefficient in expression.items():
            row_indices.append(row_index)
            column_indices.append(index[variable])
            coefficients.append(coefficient)
        row_lower.append(-np.inf if relation == "<=" else rhs)
        row_upper.append(np.inf if relation == ">=" else rhs)
    matrix = coo_matrix((coefficients, (row_indices, column_indices)), shape=(len(rows), len(names))).tocsc()
    return ParsedMilp(
        names,
        tuple(name for name, _, _, _ in rows),
        matrix,
        np.asarray(row_lower),
        np.asarray(row_upper),
        variable_lower,
        variable_upper,
        integrality,
    )


def solve_highs(model: RelaxationModel, *, time_limit_seconds: float = 90.0) -> HighsReport:
    """Numerically maximize the emitted MILP and diagnose its geometry.

    The `geometric_minimum_area` is calculated from coordinate products, not
    from the MILP `z` variable.  A material gap between them identifies a loose
    outer-relaxation solution rather than a candidate arrangement.
    """

    if time_limit_seconds <= 0:
        raise ValueError("time limit must be positive")
    parsed = parse_model(model)
    index = {name: position for position, name in enumerate(parsed.variable_names)}
    objective = np.zeros(len(parsed.variable_names))
    objective[index["z"]] = -1.0  # SciPy minimizes.
    result = milp(
        c=objective,
        integrality=parsed.integrality,
        bounds=Bounds(parsed.variable_lower, parsed.variable_upper),
        constraints=LinearConstraint(parsed.matrix, parsed.row_lower, parsed.row_upper),
        options={"time_limit": float(time_limit_seconds), "mip_rel_gap": 0.0, "disp": False},
    )
    if result.x is None:
        dual = getattr(result, "mip_dual_bound", None)
        return HighsReport(
            int(result.status),
            str(result.message),
            None,
            None if dual is None or not math.isfinite(float(dual)) else -float(dual),
            None,
            None,
            None,
            None,
            None,
            None,
            (),
            None,
        )

    values = result.x
    activity = parsed.matrix @ values
    violations = np.maximum(
        np.maximum(parsed.row_lower - activity, 0.0),
        np.maximum(activity - parsed.row_upper, 0.0),
    )
    integrality_error = max(
        (abs(values[position] - round(values[position])) for position, flag in enumerate(parsed.integrality) if flag),
        default=0.0,
    )
    points = tuple(
        (float(values[index[f"x_{point}"]]), float(values[index[f"y_{point}"]])) for point in range(model.n)
    )
    geometric = min((abs(float(signed_area(points, triangle))), triangle) for triangle in combinations(range(model.n), 3))
    gaps = sorted(
        (
            (
                abs(values[index[f"w_{left}_{right}"]] - points[left][0] * points[right][1]),
                left,
                right,
            )
            for left in range(model.n)
            for right in range(model.n)
            if left != right
        ),
        reverse=True,
    )
    dual = getattr(result, "mip_dual_bound", None)
    return HighsReport(
        int(result.status),
        str(result.message),
        float(values[index["z"]]),
        None if dual is None or not math.isfinite(float(dual)) else -float(dual),
        None if getattr(result, "mip_gap", None) is None else float(result.mip_gap),
        None if getattr(result, "mip_node_count", None) is None else int(result.mip_node_count),
        float(np.max(violations)),
        float(integrality_error),
        geometric[0],
        geometric[1],
        tuple(gaps[:12]),
        points,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n", type=int, default=12)
    parser.add_argument("--time-limit", type=float, default=90.0)
    parser.add_argument("--lower-target", type=_fraction_argument)
    parser.add_argument("--additional-strip-count", type=int, action="append")
    parser.add_argument("--piecewise-strips", action="store_true")
    parser.add_argument("--joint-piecewise-strips", action="store_true")
    parser.add_argument("--piecewise-cells", type=int)
    parser.add_argument("--piecewise-product", type=_product_pair_argument, action="append")
    arguments = parser.parse_args()
    model = build_model(
        arguments.n,
        lower_target=arguments.lower_target,
        additional_strip_counts=arguments.additional_strip_count or (),
        piecewise_strip_products=arguments.piecewise_strips,
        joint_piecewise_strip_products=arguments.joint_piecewise_strips,
        piecewise_cell_count=arguments.piecewise_cells,
        piecewise_product_pairs=arguments.piecewise_product,
    )
    report = solve_highs(model, time_limit_seconds=arguments.time_limit)
    print("status", report.status)
    print("message", report.message)
    print("milp_z", report.objective)
    print("numerical_dual_upper", report.maximization_dual_bound)
    print("mip_gap", report.mip_gap)
    print("mip_nodes", report.mip_nodes)
    print("maximum_constraint_violation", report.maximum_constraint_violation)
    print("maximum_integrality_violation", report.maximum_integrality_violation)
    print("geometric_minimum_area", report.geometric_minimum_area)
    print("geometric_minimum_triangle", report.geometric_minimum_triangle)
    print("largest_product_gaps", report.largest_product_gaps)
    print("coordinates", report.points)
    print("interpretation", "NUMERICAL OUTER RELAXATION ONLY; geometry is checked separately")


if __name__ == "__main__":
    main()
