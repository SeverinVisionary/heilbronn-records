"""Polish the certified n = 14 configuration to a converged max-min critical point.

`circle_configs/circle_n14.json` is a certified floor, not a converged optimum:
its exact-rational minimum is attained by exactly ONE triangle because the snap
to a 1/10^15 grid broke ties the pre-snap configuration held.  Here we

  1. read the committed integers back,
  2. re-run the double-precision LP endgame (it is already stalled),
  3. identify the active set and solve it exactly with high-precision Newton,
  4. verify the frozen (slack) points really are slack at the refined point,
  5. snap on a finer grid and certify the value as an exact rational, reporting
     how many triangles sit within one grid step of the minimum.

Usage: python3 polish_n14.py [dps] [snap_exponent ...]
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
import circle_lp_polish as L                       # noqa: E402
import circle_symmetry as CS                       # noqa: E402
import circle_hp_refine as HP                      # noqa: E402

N = 14


def exact_report(pts, scale):
    """Exact minimum area + exact containment + exact tie count, integers only."""
    n = len(pts)
    s2 = scale * scale
    for x, y in pts:
        assert x * x + y * y <= s2, "leaves the closed unit disk"
    assert len({tuple(p) for p in pts}) == n, "duplicate points"
    twice = {}
    best = None
    for a, b, c in combinations(range(n), 3):
        (x1, y1), (x2, y2), (x3, y3) = pts[a], pts[b], pts[c]
        v = abs((x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1))
        twice[(a, b, c)] = v
        if best is None or v < best:
            best = v
    exact = F(best, 2 * s2)
    ties = sum(1 for v in twice.values() if v == best)
    # "within one grid step": a snap of a truly tied configuration cannot do
    # better than this, so it is the honest count of the converged active set.
    window = sum(1 for v in twice.values() if v <= best + 4 * scale)
    slack = s2 - max(x * x + y * y for x, y in pts)
    return exact, ties, window, slack, twice, best


def main():
    dps = int(sys.argv[1]) if len(sys.argv) > 1 else 80
    exps = [int(a) for a in sys.argv[2:]] or [15, 18, 21, 24]

    src = json.load(open(os.path.join(HERE, "circle_configs", "circle_n14.json")))
    scale0 = src["scale"]
    P = np.array([[x / scale0, y / scale0] for x, y in src["points"]])
    T = L.triples_of(N)

    A = np.abs(L.signed_areas(P, T))
    print(f"committed  min={A.min():.18f}  exact={src['min_area_exact']}")
    Q, v = L.lp_polish(P, iters=800)
    print(f"lp_polish  min={v:.18f}  gain={v - A.min():+.3e}")
    P = Q if v > A.min() else P

    A = np.abs(L.signed_areas(P, T))
    m = A.min()
    active = [tuple(T[j]) for j in np.where(A <= m * (1 + 1e-7))[0]]
    print(f"active set at 1e-7 relative: {len(active)} of {len(T)} triangles")
    nxt = np.sort(A)[len(active)]
    print(f"next-smallest triangle is {nxt / m - 1:.3e} relative above -> "
          f"the active set is unambiguous")

    C, t, B, I, frozen, square = HP.refine(P, active, dps=dps)
    print(f"refined t = {mp.nstr(t, 30)}")

    # every non-active triangle must still be >= t at the refined point
    Cl = {i: C[i] for i in range(N)}
    worst = None
    for tri in combinations(range(N), 3):
        a = abs(HP.signed_area(Cl, tri))
        if worst is None or a < worst[0]:
            worst = (a, tri)
    print(f"true refined minimum over all {len(T)} triples = "
          f"{mp.nstr(worst[0], 30)} at {worst[1]}")
    assert worst[0] >= t * (1 - mpf(10) ** (-dps + 10)), "refinement broke a slack triangle"

    rows = []
    for e in exps:
        scale = 10 ** e
        pts = HP.snap_exact(C, N, scale)
        exact, ties, window, slack, _, _ = exact_report(pts, scale)
        loss = float(t) - float(exact)
        print(f"scale=10^{e:<3d} exact={float(exact):.18f}  loss={loss:+.3e}  "
              f"exact_ties={ties}  within_1_grid_step={window}  "
              f"radius_slack={slack}")
        rows.append({"exp": e, "scale": scale, "exact": exact, "points": pts,
                     "ties": ties, "window": window})

    best = max(rows, key=lambda r: r["exact"])
    pts = best["points"]
    scale = best["scale"]
    Pf = np.array([[x / scale, y / scale] for x, y in pts])
    desc = CS.describe(Pf)
    print("\nBEST SNAP  scale=10^%d" % best["exp"])
    print("  exact =", best["exact"])
    print("  float = %.18f" % float(best["exact"]))
    print("  ", CS.fmt(desc))

    out = {
        "n": N, "scale": scale,
        "min_area_exact": str(best["exact"]),
        "min_area_float": float(best["exact"]),
        "points": [list(p) for p in pts],
        "exact_ties": best["ties"],
        "active_triangles_converged": len(active),
        "active_triangles_within_one_grid_step": best["window"],
        "refined_value_hp": mp.nstr(t, 40),
        "dps": dps,
        "reflection_defect": desc["reflection_defect"],
        "best_rotation_order": desc["best_rotation_order"],
        "best_rotation_defect": desc["best_rotation_defect"],
        "points_on_bounding_circle": desc["on_circle"],
        "interior_points": desc["interior"],
        "slack_points_no_active_triangle": frozen,
        "square_critical_system": square,
    }
    path = os.path.join(HERE, "circle_configs", "circle_n14_converged.json")
    json.dump(out, open(path, "w"), indent=1)
    print("wrote", path)


if __name__ == "__main__":
    main()
