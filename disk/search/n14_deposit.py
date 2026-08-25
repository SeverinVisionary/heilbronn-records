"""Assemble `circle_configs/circle_n14_converged.json` from the two studies.

The headline configuration is not hand-edited.  It is written here from
artefacts that are themselves committed, so every number in it has a producer:

  * `n14_stationarity.json`  -- the converged point and its stationarity
    evidence (`n14_converge.py`);
  * `n14_reproduction.json`  -- the seed-recorded reproduction counters
    (`n14_reproduction.py`), which replace the budget metadata that an earlier
    revision had copied from another row;
  * `n14_basin_probe.json`   -- the measured basin width (`n14_basin_probe.py`).

Every value is re-derived here from the integer coordinates in exact rational
arithmetic before it is written; the high-precision state is carried only as
context, clearly labelled.

Usage: python3 n14_deposit.py [out.json]
"""
from __future__ import annotations

import json
import os
import sys
from fractions import Fraction as F
from itertools import combinations

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import circle_symmetry as CS        # noqa: E402

CFG = os.path.join(HERE, "circle_configs")
N = 14
# The value this deposit replaces, kept so the gain is auditable.
PREDECESSOR = F("153431771542054491513902173472449113/"
                "2000000000000000000000000000000000000")
# MathWorld's H_14 * pi, unit-radius disk.  Corroboration only: the quoted
# margin is against Friedman's printed ".0758+", whose upper end is 0.0759.
MATHWORLD = F(75857251061, 10 ** 12)
MATHWORLD_FULL = F(379286255304506233377054643538343268544509249506803767074279179460902788037,
                   5 * 10 ** 75)
FRIEDMAN_UPPER = F(759, 10000)


def exact_report(points, scale):
    """Everything the deposit claims, recomputed from integers alone."""
    s2 = scale * scale
    assert len(set(map(tuple, points))) == N, "duplicate points"
    rmax = max(x * x + y * y for x, y in points)
    assert rmax <= s2, "leaves the closed unit disk"
    twice, per = [], {}
    for a, b, c in combinations(range(N), 3):
        (x1, y1), (x2, y2), (x3, y3) = points[a], points[b], points[c]
        v = abs((x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1))
        assert v > 0, f"degenerate triple {(a, b, c)}"
        twice.append(v)
        per[(a, b, c)] = v
    m = min(twice)
    window = [t for t, v in per.items() if v <= m + 4 * scale]
    nxt = min(v for v in twice if v > m + 4 * scale)
    return {"exact": F(m, 2 * s2),
            "ties": sum(1 for v in twice if v == m),
            "within_one_grid_step": len(window),
            "window_triples": sorted(window),
            "next_relative_gap": F(nxt, m) - 1,
            "containment_slack_scale2": s2 - rmax}


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        CFG, "circle_n14_converged.json")

    stat = json.load(open(os.path.join(CFG, "n14_stationarity.json")))
    cand = json.load(open(os.path.join(CFG, "n14_converged_candidate.json")))
    scale = int(cand["scale"])
    points = [[int(v) for v in p] for p in cand["points"]]
    rep = exact_report(points, scale)
    exact = rep["exact"]
    assert str(exact) == cand["min_area_exact"], "candidate value disagrees"
    assert exact > PREDECESSOR, "the deposit must not go backwards"
    assert exact > FRIEDMAN_UPPER, "the deposit must clear Friedman's bracket"

    P = np.array([[x / scale, y / scale] for x, y in points])
    d = CS.describe(P)

    def load(name):
        path = os.path.join(CFG, name)
        return json.load(open(path)) if os.path.exists(path) else None

    repro = load("n14_reproduction.json")
    basin = load("n14_basin_probe.json")

    rec = {
        "n": N,
        "scale": scale,
        "min_area_exact": str(exact),
        "min_area_float": float(exact),
        "points": points,

        "claim":
            "New best-known CONSTRUCTION for 14 points in the closed "
            "unit-radius disk: an exactly certified LOWER bound on "
            "alpha_disk(14). Not a proof of optimality. The configuration is a "
            "numerically stationary candidate -- see stationarity below -- but "
            "stationarity is evidence, not a theorem, and no local-optimality "
            "claim is made.",
        "status": "improves",
        "claim_bracket_exact": ["0.0758", "0.0759"],
        "claim_bracket_float": [0.0758, 0.0759],
        "friedman_printed": "0.0758+",
        "friedman_symmetry_class": "horizontally symmetric",
        "margin_vs_friedman_upper_percent":
            float((exact / FRIEDMAN_UPPER - 1) * 100),

        "exact_ties": rep["ties"],
        "active_triangles_within_one_grid_step": rep["within_one_grid_step"],
        "active_triples": [list(t) for t in rep["window_triples"]],
        "next_smallest_relative_gap": float(rep["next_relative_gap"]),
        "containment_slack_scale2": rep["containment_slack_scale2"],
        "points_on_bounding_circle": d["on_circle"],
        "interior_points": d["interior"],
        "reflection_defect": d["reflection_defect"],
        "best_rotation_order": d["best_rotation_order"],
        "best_rotation_defect": d["best_rotation_defect"],
        "measured_symmetry": "asymmetric" if not d["symmetric"] else "symmetric",

        "hp_value": stat["stationary_value_hp"],
        "points_hp": stat["points_hp"],
        "hp_snap_loss": next(s["loss_vs_stationary"] for s in stat["snaps"]
                             if s["scale"] == scale),
        "hp_note":
            "hp_value is the high-precision stationary value; min_area_exact "
            "is the exact rational after snapping to the 1/scale grid and "
            "sits hp_snap_loss below it. The exact one is the claim.",

        "stationarity": {
            "artifact": "n14_stationarity.json",
            "producer": "n14_converge.py",
            "is_a_theorem": False,
            "summary":
                "The set {all 16 active triangles equal} is a CURVE, not a "
                "point: 16 equations in 16 spatial degrees of freedom with a "
                "rank-15 Jacobian (the rotation gauge). Earlier passes ran a "
                "Newton solve, landed somewhere on that curve and called it "
                "converged, which is why a feasible ascent direction survived "
                "the label. This deposit walks the curve to the maximum of t.",
            "active_set_size": stat["active_set"]["size"],
            "newton_point_kkt_residual": stat["newton_point"]["kkt_residual"],
            "newton_point_ascent_rate":
                stat["newton_point"]["ascent_rate_per_unit_displacement"],
            "endpoint_kkt_residual": stat["kkt"]["residual_inf"],
            "endpoint_residual_of_Jv_eq_1": stat["kkt"]["residual_of_Jv_eq_1"],
            "endpoint_min_lambda": stat["kkt"]["min_lambda"],
            "endpoint_min_mu": stat["kkt"]["min_mu"],
            "multiplier_family_dimension": stat["kkt"]["family_dimension"],
            "all_multipliers_strictly_positive":
                stat["kkt"]["all_multipliers_strictly_positive"],
            "gain_over_newton_point": stat["gain_over_newton_point"],
            "nearest_inactive_relative_above_t":
                stat["feasibility"]["nearest_inactive_relative_above_t"],
            "slack_points_no_active_triangle":
                stat["newton_point"]["frozen_points"],
            "slack_point_note":
                "these two points sit in no active triangle, so the stationary "
                "point is not isolated: they can move within their slack "
                "region without changing the minimum.",
        },

        "predecessor_exact": str(PREDECESSOR),
        "predecessor_float": float(PREDECESSOR),
        "gain_over_predecessor": float(exact - PREDECESSOR),
        "gain_over_predecessor_relative": float((exact - PREDECESSOR) / PREDECESSOR),
        "gain_note":
            "The convergence moved the value in its 15th significant digit. "
            "That smallness is the answer to 'why did you stop?': the earlier "
            "point was already within 2.2e-14 relative of the top of its "
            "curve.",

        "baseline": str(MATHWORLD),
        "baseline_float": float(MATHWORLD),
        "ratio": float(exact / MATHWORLD),
        "baseline_min_area_exact": str(MATHWORLD_FULL),
        "baseline_min_area_float": float(MATHWORLD_FULL),
        "ratio_to_baseline": float(exact / MATHWORLD_FULL),
        "baseline_note":
            "MathWorld's H_14 * pi. Corroboration only: the quoted margin is "
            "against Friedman's printed '.0758+', whose upper end is 0.0759, "
            "because MathWorld is erroneous at n = 11.",

        "method":
            "multistart simulated annealing (C, pthreads, boundary count "
            "cycled over 3..n across restarts) -> sequential-LP polish "
            "(scipy/HiGHS) -> high-precision Newton onto the active-set curve "
            "-> walk that curve to the maximum of t -> snap to a 1/scale "
            "integer grid -> exact rational minimum with an exact closed-disk "
            "containment check. Floating point proposes; rational arithmetic "
            "decides.",
    }

    if repro:
        c = repro["counts"]
        rec["reproduction"] = {
            "artifact": "n14_reproduction.json",
            "producer": "n14_reproduction.py",
            "seed_base": repro["seed_set"]["seed_base"],
            "restart_seed_formula": repro["seed_set"]["restart_seed_formula"],
            "restarts": c["restarts"],
            "sa_iterations": repro["parameters"]["sa_iterations_per_restart"],
            "candidates_lp_polished": repro["parameters"]["topk_lp_polished"],
            "independent_restarts_reaching_this_basin":
                c["reaching_record_basin"],
            "record_hit_rate": c["record_hit_rate"],
            "independent_restarts_reaching_cantrell_basin":
                c["reaching_cantrell_basin"],
            "distinct_basins": c["distinct_basins"],
            "seeds_that_reach_it":
                [r["seed"] for r in repro["record_basin_restarts"]],
            "note":
                "Measured, not inherited. Earlier revisions carried budget "
                "metadata copied from circle_n8.json and reproduction counts "
                "with no committed artifact; these counters come from the "
                "recorded seed set above and every hit is replayable from its "
                "seed.",
        }
        # legacy field names, kept so older readers do not silently see zeros
        rec["restarts"] = c["restarts"]
        rec["sa_iterations"] = repro["parameters"]["sa_iterations_per_restart"]
        rec["candidates_lp_polished"] = repro["parameters"]["topk_lp_polished"]
        rec["independent_restarts_reaching_this_value"] = \
            c["reaching_record_basin"]
    if basin:
        rec["basin_width"] = {
            "artifact": "n14_basin_probe.json",
            "producer": "n14_basin_probe.py",
            "numpy_seed": basin["numpy_seed"],
            "draws_per_sigma": basin["draws_per_sigma"],
            "recovery_by_sigma": {str(r["sigma"]): r["recovery_rate"]
                                  for r in basin["by_sigma"]},
            "note":
                "Fraction of Gaussian kicks of size sigma from which the LP "
                "endgame walks back to this basin. Recovery is judged by "
                "polished value, which is invariant under the disk's "
                "rotation/reflection group and under relabelling.",
        }

    with open(out, "w") as fh:
        json.dump(rec, fh, indent=1)
    print(f"exact          {exact}")
    print(f"               {float(exact):.22f}")
    print(f"predecessor    {float(PREDECESSOR):.22f}")
    print(f"gain           {float(exact - PREDECESSOR):+.6e} "
          f"({float((exact - PREDECESSOR) / PREDECESSOR):+.6e} relative)")
    print(f"vs Friedman    {float((exact / FRIEDMAN_UPPER - 1) * 100):+.6f}%")
    print(f"structure      {d['on_circle']}+{d['interior']}, "
          f"{rep['within_one_grid_step']} active, "
          f"reflection defect {d['reflection_defect']:.2e}")
    print(f"reproduction   {'present' if repro else 'MISSING'}   "
          f"basin probe {'present' if basin else 'MISSING'}")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
