"""Snap a high-precision configuration to an integer grid and certify it exactly.

Floating point (here, mpmath) proposes; the reported number is an exact rational
recomputed from integer-scaled coordinates whose containment in the CLOSED unit
disk is checked in integer arithmetic.

Usage: python3 certify_hp.py <hp_state.json> <out.json> <baseline> [scale_exps...]
"""
import json
import os
import sys
from fractions import Fraction as F
from itertools import combinations

import numpy as np
from mpmath import mp, mpf

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import circle_symmetry as CS       # noqa: E402


def snap(Q, scale):
    pts = []
    for x, y in Q:
        ix = int(mp.floor(x * scale + mpf("0.5")))
        iy = int(mp.floor(y * scale + mpf("0.5")))
        while ix * ix + iy * iy > scale * scale:
            if abs(ix) >= abs(iy):
                ix -= 1 if ix > 0 else -1
            else:
                iy -= 1 if iy > 0 else -1
        pts.append((ix, iy))
    return pts


def exact_min(pts, scale):
    n = len(pts)
    s2 = scale * scale
    assert len(set(pts)) == n
    assert max(x * x + y * y for x, y in pts) <= s2
    vals = []
    for a, b, c in combinations(range(n), 3):
        (x1, y1), (x2, y2), (x3, y3) = pts[a], pts[b], pts[c]
        vals.append(abs((x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1)))
    m = min(vals)
    assert m > 0
    ties = sum(1 for v in vals if v == m)
    window = sum(1 for v in vals if v <= m + 4 * scale)
    return F(m, 2 * s2), ties, window, s2 - max(x * x + y * y for x, y in pts)


def main():
    mp.dps = 60
    state = json.load(open(os.path.join(HERE, sys.argv[1])))
    out_path = sys.argv[2]
    baseline = F(sys.argv[3])
    exps = [int(a) for a in sys.argv[4:]] or [15, 18, 21, 24]
    Q = [(mpf(a), mpf(b)) for a, b in state["points_hp"]]
    n = len(Q)
    hp = mpf(state["min_area_hp"])
    print(f"n={n}  hp value = {mp.nstr(hp, 30)}")

    rows = []
    for e in exps:
        scale = 10 ** e
        pts = snap(Q, scale)
        ex, ties, win, slack = exact_min(pts, scale)
        print(f"  scale=10^{e:<3d} exact={float(ex):.18f}  exact_ties={ties}  "
              f"within_1_step={win}  radius_slack={slack}")
        rows.append((ex, pts, scale, e, ties, win, slack))
    ex, pts, scale, e, ties, win, slack = max(rows, key=lambda r: r[0])

    P = np.array([[x / scale, y / scale] for x, y in pts])
    d = CS.describe(P)
    print("\nBEST scale=10^%d" % e)
    print("  exact  =", ex)
    print("  float  = %.18f" % float(ex))
    print("  ratio to baseline = %.9f  (%+.6f%%)"
          % (float(ex / baseline), float(ex / baseline - 1) * 100))
    print("  ", CS.fmt(d))
    rec = {
        "n": n, "scale": scale,
        "min_area_exact": str(ex), "min_area_float": float(ex),
        "points": [list(p) for p in pts],
        "hp_value": mp.nstr(hp, 40),
        "exact_ties": ties,
        "active_triangles_within_one_grid_step": win,
        "containment_slack_scale2": slack,
        "baseline": str(baseline), "baseline_float": float(baseline),
        "ratio": float(ex / baseline),
        "points_on_bounding_circle": d["on_circle"],
        "interior_points": d["interior"],
        "reflection_defect": d["reflection_defect"],
        "best_rotation_order": d["best_rotation_order"],
        "best_rotation_defect": d["best_rotation_defect"],
        "measured_symmetry": ("reflection" if d["reflection_defect"] < 1e-6 else
                              (f"C_{d['best_rotation_order']}"
                               if d["best_rotation_defect"] < 1e-6 else "asymmetric")),
    }
    json.dump(rec, open(os.path.join(HERE, out_path), "w"), indent=1)
    print("wrote", out_path)


if __name__ == "__main__":
    main()
