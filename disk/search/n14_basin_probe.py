"""How wide is the n = 14 record basin?  Measured, not guessed.

`n14_reproduction.py` answers "how often does a random restart land in it?".
That is the number a referee asks for, but on its own a zero tells you nothing
about *why*.  This script measures the other half directly: start from the
committed record configuration, kick it by a known amount, and count how often
the LP endgame walks back.  The kick size at which recovery collapses is the
radius of the basin, and it is what makes a miss rate intelligible.

Two checks come first, because a basin probe is meaningless if the centre is
not an attractor at all:

  1. the committed integers re-derive to the recorded exact rational, with
     exact closed-disk containment (integers and Fractions only);
  2. `circle_lp_polish.lp_polish` started AT the record returns the record --
     i.e. the double-precision endgame recognises it as a fixed point rather
     than walking off it.

Then, for each kick size sigma, K perturbations are drawn from a recorded
numpy seed, projected back into the disk, and polished; a draw "recovers" when
its polished value is within `BASIN_REL` of the record.

Usage:
    python3 n14_basin_probe.py <draws_per_sigma> <threads> <numpy_seed> <out.json>
"""
from __future__ import annotations

import json
import os
import sys
import time
from fractions import Fraction as F
from itertools import combinations
from multiprocessing import Pool

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import circle_lp_polish as L        # noqa: E402
import circle_symmetry as CS        # noqa: E402

CONFIG = os.path.join(HERE, "circle_configs", "circle_n14_converged.json")
RECORD = 0.0767158857710272457569510867362245565
BASIN_REL = 1e-9
SIGMAS = [1e-4, 1e-3, 3e-3, 1e-2, 2e-2, 3e-2, 4e-2, 5e-2, 7e-2, 1e-1, 1.5e-1,
          2e-1, 3e-1]


def exact_check():
    """Re-derive the committed value from the integers alone."""
    rec = json.load(open(CONFIG))
    pts = [tuple(int(v) for v in p) for p in rec["points"]]
    scale = int(rec["scale"])
    s2 = scale * scale
    assert len(set(pts)) == len(pts), "duplicate points"
    rmax = max(x * x + y * y for x, y in pts)
    assert rmax <= s2, "point outside the closed unit disk"
    twice_min = min(abs((x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1))
                    for (x1, y1), (x2, y2), (x3, y3)
                    in ((pts[a], pts[b], pts[c])
                        for a, b, c in combinations(range(len(pts)), 3)))
    exact = F(twice_min, 2 * s2)
    assert exact == F(rec["min_area_exact"]), "recomputation disagrees"
    P = np.array([[x / scale, y / scale] for x, y in pts])
    return rec, P, exact, s2 - rmax


def _probe(job):
    sigma, k, seed, P0 = job
    rng = np.random.default_rng(seed)
    P = np.asarray(P0) + rng.normal(0.0, sigma, (len(P0), 2))
    P = L.project(P)
    _, v = L.lp_polish(P)
    return {"sigma": sigma, "draw": k, "seed": int(seed), "polished": v,
            "recovered": abs(v - RECORD) <= RECORD * BASIN_REL}


def main():
    draws = int(sys.argv[1])
    threads = int(sys.argv[2])
    np_seed = int(sys.argv[3])
    out_path = sys.argv[4]

    rec, P, exact, slack = exact_check()
    print(f"exact re-derivation   {exact}")
    print(f"                    = {float(exact):.25f}")
    print(f"containment slack     {slack} (scale^2 units), strictly inside")

    _, v0 = L.lp_polish(P)
    fixed = abs(v0 - RECORD) <= RECORD * BASIN_REL
    print(f"lp_polish at the record -> {v0:.18f}  "
          f"{'FIXED POINT' if fixed else 'WALKS OFF -- not an LP attractor'}")

    ss = np.random.SeedSequence(np_seed)
    children = ss.spawn(len(SIGMAS) * draws)
    jobs, ci = [], 0
    for sigma in SIGMAS:
        for k in range(draws):
            jobs.append((sigma, k, children[ci].generate_state(1)[0], P.tolist()))
            ci += 1

    t0 = time.time()
    with Pool(threads) as pool:
        rows = pool.map(_probe, jobs, chunksize=4)
    wall = time.time() - t0

    by_sigma = []
    for sigma in SIGMAS:
        got = [r for r in rows if r["sigma"] == sigma]
        rec_n = sum(r["recovered"] for r in got)
        vals = sorted((r["polished"] for r in got), reverse=True)
        by_sigma.append({"sigma": sigma, "draws": len(got), "recovered": rec_n,
                         "recovery_rate": rec_n / len(got),
                         "best_polished": vals[0],
                         "median_polished": vals[len(vals) // 2],
                         "best_ratio_to_record": vals[0] / RECORD})
        print(f"sigma={sigma:<8g} recovered {rec_n:4d}/{len(got):<4d} "
              f"({100 * rec_n / len(got):6.2f}%)  best {vals[0]:.12f}  "
              f"median {vals[len(vals) // 2]:.12f}")

    d = CS.describe(P)
    out = {
        "what": "basin-width probe for the n=14 record configuration",
        "config": os.path.relpath(CONFIG, HERE),
        "record_value": RECORD,
        "exact_min_area": str(exact),
        "exact_min_area_float": float(exact),
        "containment_slack_scale2": slack,
        "lp_polish_at_record": v0,
        "record_is_lp_fixed_point": bool(fixed),
        "structure": {"on_circle": d["on_circle"], "interior": d["interior"],
                      "reflection_defect": d["reflection_defect"],
                      "active_triangles_rel1e-9": d["active_triangles"]},
        "basin_relative_tolerance": BASIN_REL,
        "numpy_seed": np_seed,
        "seed_model": "numpy SeedSequence(numpy_seed).spawn(len(SIGMAS)*draws), "
                      "consumed in (sigma, draw) order",
        "draws_per_sigma": draws,
        "sigmas": SIGMAS,
        "by_sigma": by_sigma,
        "draws_detail": [{k: r[k] for k in ("sigma", "draw", "seed",
                                            "polished", "recovered")}
                         for r in rows],
        "wall_seconds": round(wall, 1),
        "threads": threads,
        "nproc": os.cpu_count(),
    }
    with open(out_path, "w") as fh:
        json.dump(out, fh, indent=1)
    print(f"\nwrote {out_path}")


if __name__ == "__main__":
    main()
