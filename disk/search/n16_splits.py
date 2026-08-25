"""Boundary/interior split enumeration, seeded from configurations worth polishing.

Cold random seeds are far too weak at n = 16 -- 240 of them polished to
0.0411 in the b = 8 family against a target of .0661+.  The families only mean
something if each one is entered from a configuration that is already good, so
every family here is seeded three ways:

  1. from the best ANNEALED candidates that already end with exactly k points
     on the circle (the family the annealer selected for itself);
  2. from the best configuration found anywhere, pushed into the family --
     interior points nearest the rim are pushed onto it to raise k, boundary
     points are pulled in to lower it;
  3. from random symmetric seeds, as a control.

Each seed is polished with the family ENFORCED (boundary points held on the
circle by a tangential-displacement equality plus renormalisation), then again
with the constraint released, so we can see both the best value inside the
family and whether the family is a barrier at all.

Usage: python3 n16_splits.py <n> <k_lo> <k_hi> <cand_file> <anchor.json> <key> <threads>
"""
import json
import math
import os
import sys
from multiprocessing import Pool

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import circle_attack as ca         # noqa: E402
import circle_families as CF       # noqa: E402
import circle_lp_polish as L       # noqa: E402
import circle_symmetry as CS       # noqa: E402


def read_candidates(path, n):
    out = []
    if not os.path.exists(path):
        return out
    for line in open(path):
        v = [float(x) for x in line.split()]
        if len(v) == 2 * n + 1:
            out.append(np.array([(v[1 + 2 * i], v[2 + 2 * i]) for i in range(n)]))
    return out


def push_to_family(P, k):
    """Move points so that exactly k of them sit on the unit circle."""
    P = np.array(P, float).copy()
    r = np.hypot(P[:, 0], P[:, 1])
    order = np.argsort(-r)
    on = order[:k]
    P[on] = P[on] / np.hypot(P[on, 0], P[on, 1])[:, None]
    for i in order[k:]:
        if r[i] > 1 - 1e-9:
            P[i] *= 0.985
    return P


def main():
    n = int(sys.argv[1]); klo = int(sys.argv[2]); khi = int(sys.argv[3])
    cand_file = sys.argv[4]; anchor_src = sys.argv[5]; anchor_key = sys.argv[6]
    threads = int(sys.argv[7])
    per_random = int(sys.argv[8]) if len(sys.argv) > 8 else 24

    node = json.load(open(os.path.join(HERE, anchor_src)))
    for kk in anchor_key.split("/"):
        node = node[kk]
    anchor = np.array(node, dtype=float)
    if np.abs(anchor).max() > 10:
        anchor = anchor / 10 ** 12

    cands = read_candidates(os.path.join(HERE, cand_file), n)
    print(f"{len(cands)} annealed candidates, anchor min="
          f"{L.min_area(anchor, L.triples_of(n)):.12f}")
    by_k = {}
    for P in cands:
        k = int((np.hypot(P[:, 0], P[:, 1]) > 1 - 1e-9).sum())
        by_k.setdefault(k, []).append(P)

    rng = np.random.default_rng(20260824)
    path = os.path.join(HERE, f"splits_n{n}.json")
    res = json.load(open(path)) if os.path.exists(path) else {}
    for k in range(klo, khi + 1):
        on = list(range(k))
        seeds = []
        pool_k = by_k.get(k, [])
        pool_k.sort(key=lambda P: -L.min_area(P, L.triples_of(n)))
        for P in pool_k[:24]:
            seeds.append(push_to_family(P, k))
        seeds.append(push_to_family(anchor, k))
        for _ in range(6):
            seeds.append(push_to_family(
                L.project(anchor + rng.normal(0, 0.03, anchor.shape)), k))
        seeds.extend(CF.seeds_for(n, k, per_random, rng))
        # relabel so the first k indices are the ones on the circle
        norm = []
        for P in seeds:
            P = np.array(P, float)
            r = np.hypot(P[:, 0], P[:, 1])
            idx = np.argsort(-r)
            norm.append(P[idx])
        with Pool(threads) as pool:
            got = pool.map(CF._job, [(P, on) for P in norm], chunksize=2)
        infam = max(got, key=lambda r: r[0])
        free = max(got, key=lambda r: r[2])
        ints_in = ca.snap_to_disk(infam[1]); ex_in = ca.exact_minimum(ints_in)
        ints_fr = ca.snap_to_disk(free[3]);  ex_fr = ca.exact_minimum(ints_fr)
        di = CS.describe(np.array(infam[1]))
        df = CS.describe(np.array(free[3]))
        res[str(k)] = {
            "family": f"{k} on circle + {n - k} interior",
            "seeds": len(norm), "annealed_seeds": len(pool_k[:24]),
            "in_family_exact": str(ex_in), "in_family": float(ex_in),
            "in_family_active": di["active_triangles"],
            "in_family_refl_defect": di["reflection_defect"],
            "free_exact": str(ex_fr), "free": float(ex_fr),
            "free_split": f"{df['on_circle']}+{df['interior']}",
            "free_refl_defect": df["reflection_defect"],
            "points_in_family": ints_in, "points_free": ints_fr,
        }
        json.dump(res, open(path, "w"), indent=1)
        print(f"  k={k:2d}  {k:2d}+{n - k:<2d}  in-family={float(ex_in):.12f} "
              f"({di['active_triangles']} active, refl "
              f"{di['reflection_defect']:.1e})   free={float(ex_fr):.12f} "
              f"(ends {df['on_circle']}+{df['interior']}, refl "
              f"{df['reflection_defect']:.1e})   [{len(pool_k[:24])} annealed seeds]",
              flush=True)
    if res:
        bb = max(res, key=lambda kk: res[kk]["in_family"])
        print(f"best family: k={bb} at {res[bb]['in_family']:.12f}")


if __name__ == "__main__":
    main()
