"""Boundary/interior family enumeration over a chosen range of b, resumable.

`circle_families.run` sweeps b = 3..n in one process; on a shared host that is
too long to hold a single foreground slot, and a kill loses everything.  This
driver does one family per invocation range and merges into a single JSON.

Usage: python3 n16_families.py <n> <b_lo> <b_hi> <seeds> <threads>
"""
import json
import os
import sys
from multiprocessing import Pool

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import circle_attack as ca            # noqa: E402
import circle_families as CF          # noqa: E402
import circle_lp_polish as L          # noqa: E402
import circle_symmetry as CS          # noqa: E402


def main():
    n, blo, bhi, seeds, threads = (int(sys.argv[1]), int(sys.argv[2]),
                                   int(sys.argv[3]), int(sys.argv[4]),
                                   int(sys.argv[5]))
    path = os.path.join(HERE, f"families_n{n}.json")
    res = json.load(open(path)) if os.path.exists(path) else {}
    rng = np.random.default_rng(20260824 + n)
    for b in range(blo, bhi + 1):
        on = list(range(b))
        jobs = [(P, on) for P in CF.seeds_for(n, b, seeds, rng)]
        with Pool(threads) as pool:
            got = pool.map(CF._job, jobs, chunksize=4)
        infam = max(got, key=lambda r: r[0])
        free = max(got, key=lambda r: r[2])
        hits = sum(1 for r in got if r[0] > infam[0] * (1 - 1e-9))
        fhits = sum(1 for r in got if r[2] > free[2] * (1 - 1e-9))
        ints_in = ca.snap_to_disk(infam[1]); ex_in = ca.exact_minimum(ints_in)
        ints_fr = ca.snap_to_disk(free[3]);  ex_fr = ca.exact_minimum(ints_fr)
        di = CS.describe(np.array(infam[1]))
        df = CS.describe(np.array(free[3]))
        res[str(b)] = {
            "family": f"{b} on circle + {n - b} interior",
            "in_family_exact": str(ex_in), "in_family": float(ex_in),
            "in_family_active": di["active_triangles"],
            "in_family_refl_defect": di["reflection_defect"],
            "free_exact": str(ex_fr), "free": float(ex_fr),
            "free_split": f"{df['on_circle']}+{df['interior']}",
            "free_active": df["active_triangles"],
            "free_refl_defect": df["reflection_defect"],
            "seeds": len(jobs), "seeds_at_family_best": hits,
            "seeds_at_free_best": fhits,
            "points_in_family": ints_in, "points_free": ints_fr,
        }
        json.dump(res, open(path, "w"), indent=1)
        print(f"  b={b:2d}  {b:2d}+{n - b:<2d}  in-family={float(ex_in):.12f} "
              f"({hits}/{len(jobs)}, {di['active_triangles']} active, refl "
              f"{di['reflection_defect']:.1e})   free={float(ex_fr):.12f} "
              f"({fhits}/{len(jobs)}, ends {df['on_circle']}+{df['interior']}, "
              f"refl {df['reflection_defect']:.1e})", flush=True)
    if res:
        bb = max(res, key=lambda k: res[k]["free"])
        print(f"best so far: b={bb} free={res[bb]['free']:.12f}")


if __name__ == "__main__":
    main()
