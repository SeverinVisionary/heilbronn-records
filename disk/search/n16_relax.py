"""Does leaving the symmetry class help at this row?

The per-class numbers from `n16_symmetry.py` are seeding-limited lower bounds:
D_2, C_4, C_2 and the reflection class all CONTAIN the D_4 configurations, so
their true optima are at least the D_4 optimum, and a random seed inside the
larger class simply may not land in that basin.  Quoting them as "the value of
the class" would be wrong.

The question that actually matters -- does asymmetry buy anything here, as it
did at n = 13 and n = 14 -- is answered by starting AT the class optimum and
leaving it deliberately:

  * free LP polish from the class optimum (no constraints at all);
  * asymmetric kicks of many sizes, each followed by a free polish, so the
    basin is probed at several radii rather than at one;
  * the reflection defect of every result, measured rather than assumed.

If none of that exceeds the class optimum, the row is not another n = 13/14.

Usage: python3 n16_relax.py <config.json> <key-path> <trials> <threads> [out]
"""
import json
import os
import sys
from multiprocessing import Pool

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import circle_attack as ca         # noqa: E402
import circle_lp_polish as L       # noqa: E402
import circle_symmetry as CS       # noqa: E402

KICKS = [0.002, 0.005, 0.01, 0.02, 0.04, 0.08, 0.15, 0.30]


def _job(arg):
    P0, sigma, seed = arg
    rng = np.random.default_rng(seed)
    P = np.array(P0)
    if sigma > 0:
        P = L.project(P + rng.normal(0, sigma, P.shape))
    Q, v = L.lp_polish(P)
    return v, sigma, Q.tolist()


def main():
    src, keypath = sys.argv[1], sys.argv[2]
    trials = int(sys.argv[3])
    threads = int(sys.argv[4])
    out = sys.argv[5] if len(sys.argv) > 5 else "relax_n16.json"

    node = json.load(open(os.path.join(HERE, src)))
    for k in keypath.split("/"):
        node = node[k]
    A = np.array(node, dtype=float)
    if np.abs(A).max() > 10:
        A = A / 10 ** 12
    n = len(A)
    base = L.min_area(A, L.triples_of(n))
    print(f"n={n}  base={base:.15f}   {CS.fmt(CS.describe(A))}")

    jobs = [(A.tolist(), 0.0, 0)]
    s = 1
    for sigma in KICKS:
        for _ in range(trials):
            jobs.append((A.tolist(), sigma, 900000 + s))
            s += 1
    with Pool(threads) as pool:
        got = pool.map(_job, jobs, chunksize=4)

    by_sigma = {}
    for v, sigma, Q in got:
        cur = by_sigma.get(sigma)
        if cur is None or v > cur[0]:
            by_sigma[sigma] = (v, Q)
    rows = []
    for sigma in sorted(by_sigma):
        v, Q = by_sigma[sigma]
        d = CS.describe(np.array(Q))
        beats = v > base * (1 + 1e-12)
        n_at = sum(1 for w, sg, _ in got if sg == sigma and w > base * (1 - 1e-9))
        print(f"  kick sigma={sigma:<5} best={v:.15f}  {'BEATS' if beats else 'below'}"
              f"  refl {d['reflection_defect']:.1e}  split {d['on_circle']}+"
              f"{d['interior']}  returned_to_base={n_at}/"
              f"{sum(1 for _, sg, _ in got if sg == sigma)}")
        rows.append({"sigma": sigma, "best": v, "beats_base": bool(beats),
                     "reflection_defect": d["reflection_defect"],
                     "split": f"{d['on_circle']}+{d['interior']}",
                     "returned_to_base": n_at})
    gv, gs, gQ = max(got, key=lambda r: r[0])
    ints = ca.snap_to_disk(gQ)
    exact = ca.exact_minimum(ints)
    print(f"overall best {float(exact):.15f} at sigma={gs}   "
          f"{'BEATS the class optimum' if gv > base * (1 + 1e-12) else 'does NOT beat the class optimum'}")
    json.dump({"base": base, "trials_per_sigma": trials, "rows": rows,
               "overall_best_exact": str(exact), "overall_best": float(exact),
               "overall_best_sigma": gs, "points": ints},
              open(os.path.join(HERE, out), "w"), indent=1)


if __name__ == "__main__":
    main()
