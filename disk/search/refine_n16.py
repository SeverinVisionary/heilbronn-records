"""Take the best n = 16 configuration found so far to a converged critical point.

Reads a configuration (from the symmetry-class table, the family table, or the
sweep state), runs the high-precision ascent, and writes the exactly certified
record.

Usage: python3 refine_n16.py <source.json> <key-path> <out.json> <iters> [dps]
  key-path examples:  D4/points_in_class   best_points_int   9/points_free
"""
import json
import os
import sys

import numpy as np
from mpmath import mp

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import circle_hp_ascent as HA          # noqa: E402


def fetch(src, keypath):
    node = json.load(open(os.path.join(HERE, src)))
    for k in keypath.split("/"):
        node = node[k]
    return node


def main():
    src, keypath, out = sys.argv[1], sys.argv[2], sys.argv[3]
    iters = int(sys.argv[4]) if len(sys.argv) > 4 else 120
    dps = int(sys.argv[5]) if len(sys.argv) > 5 else 45
    trust0 = float(sys.argv[6]) if len(sys.argv) > 6 else 1e-4
    pts = fetch(src, keypath)
    A = np.array(pts, dtype=float)
    scale = 10 ** 12 if np.abs(A).max() > 10 else 1
    mp.dps = dps
    P = [(mp.mpf(int(x)) / scale, mp.mpf(int(y)) / scale) if scale != 1
         else (mp.mpf(x), mp.mpf(y)) for x, y in pts]
    n = len(P)
    print(f"n={n}  start min={mp.nstr(HA.min_area_mp(HA.to_mp(P), list(__import__('itertools').combinations(range(n), 3))), 20)}")
    Q, v = HA.ascend(P, dps=dps, iters=iters, trust0=trust0)
    print("converged", mp.nstr(v, 34))
    for w in ("1e-30", "1e-20", "1e-15", "1e-12", "1e-9"):
        a, _, _, _ = HA.active_set(Q, rel=w)
        print(f"  active@{w}: {len(a)}")
    json.dump({"points_hp": [[mp.nstr(p[0], 45), mp.nstr(p[1], 45)] for p in Q],
               "min_area_hp": mp.nstr(v, 45), "dps": dps},
              open(os.path.join(HERE, out), "w"), indent=1)
    print("wrote", out)


if __name__ == "__main__":
    main()
