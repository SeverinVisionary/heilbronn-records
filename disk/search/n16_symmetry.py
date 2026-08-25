"""Symmetry-class attack on one n, matching and deliberately breaking the class
Friedman annotates for Cantrell's row.

Cantrell's n = 16 is annotated "Symmetry of a square", i.e. D_4.  A search that
only samples randomly will not reliably reach either the D_4 optimum or an
asymmetric competitor, so both are constructed:

  * for each class we build many seeds INSIDE the class and polish them with
    the class imposed as LP equalities -> the honest "best in this class";
  * the same seeds are polished with the constraints released -> "does leaving
    the class help";
  * and each class optimum is kicked asymmetrically and re-polished freely ->
    "is the class optimum a genuine local max of the unrestricted problem".

Usage: python3 n16_symmetry.py <n> <seeds_per_class> <threads>
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
import circle_lp_polish as L       # noqa: E402
import circle_symfam as SF         # noqa: E402
import circle_symmetry as CS       # noqa: E402


def class_seeds(n, name, count, rng):
    """Yield (points, generators) pairs inside the named symmetry class."""
    out = []
    if name.startswith("C"):
        k = int(name[1:])
        if n % k:
            return out
        norb = n // k
        while len(out) < count:
            nb = rng.integers(0, norb + 1)        # how many orbits on the circle
            orbits = []
            for j in range(norb):
                r = 1.0 if j < nb else float(rng.uniform(0.12, 0.95))
                th = float(rng.uniform(0, 2 * math.pi / k))
                orbits.append((r, th))
            out.append(SF.c_k_seed(k, orbits))
    elif name.startswith("D"):
        k = int(name[1:])
        # n = 2k*g + k*m  (g generic orbits of size 2k, m mirror orbits of size k)
        splits = [(g, m) for g in range(0, n // (2 * k) + 1)
                  for m in range(0, n // k + 1) if 2 * k * g + k * m == n]
        if not splits:
            return out
        while len(out) < count:
            g, m = splits[int(rng.integers(len(splits)))]
            generic, mirror = [], []
            for _ in range(g):
                r = 1.0 if rng.random() < 0.45 else float(rng.uniform(0.12, 0.95))
                generic.append((r, float(rng.uniform(0.05, math.pi / k - 0.05))))
            for _ in range(m):
                r = 1.0 if rng.random() < 0.45 else float(rng.uniform(0.12, 0.95))
                mirror.append((r, int(rng.integers(2))))
            out.append(SF.d_k_seed(k, generic, mirror))
    elif name == "reflect":
        while len(out) < count:
            na = int(rng.integers(0, min(4, n) + 1))
            if (n - na) % 2:
                na += 1
            if na > n:
                continue
            npair = (n - na) // 2
            pairs, axis = [], []
            for _ in range(npair):
                r = 1.0 if rng.random() < 0.5 else float(rng.uniform(0.12, 0.95))
                pairs.append((r, float(rng.uniform(0.05, math.pi - 0.05))))
            for _ in range(na):
                r = 1.0 if rng.random() < 0.5 else float(rng.uniform(0.1, 0.98))
                axis.append((r, 1 if rng.random() < 0.5 else -1))
            out.append(SF.reflect_seed(pairs, axis))
    elif name == "none":
        while len(out) < count:
            b = int(rng.integers(3, n + 1))
            ang = np.sort(rng.uniform(0, 2 * math.pi, b))
            P = [(math.cos(a), math.sin(a)) for a in ang]
            for _ in range(n - b):
                th = rng.uniform(0, 2 * math.pi)
                rad = math.sqrt(rng.uniform(0.01, 0.97))
                P.append((rad * math.cos(th), rad * math.sin(th)))
            out.append((np.array(P), []))
    return out[:count]


def _job(arg):
    P, gens, kick = arg
    if gens:
        Q, v = SF.lp_polish_sym(P, gens)
    else:
        Q, v = L.lp_polish(P)
    R, w = L.lp_polish(Q)                      # release the constraints
    rng = np.random.default_rng(int(abs(v) * 1e12) % (2 ** 31))
    K = np.array(Q) + rng.normal(0, kick, np.array(Q).shape)
    K = L.project(K)
    K2, u = L.lp_polish(K)                     # asymmetric kick, free polish
    return v, np.array(Q).tolist(), w, np.array(R).tolist(), u, np.array(K2).tolist()


def main():
    n = int(sys.argv[1])
    per = int(sys.argv[2])
    threads = int(sys.argv[3])
    kick = float(sys.argv[4]) if len(sys.argv) > 4 else 0.02
    seed = int(sys.argv[5]) if len(sys.argv) > 5 else 20260824
    classes = (sys.argv[6].split(",") if len(sys.argv) > 6
               else ["D4", "C4", "D2", "C2", "reflect", "none"])
    rng = np.random.default_rng(seed)
    path = os.path.join(HERE, f"symmetry_n{n}.json")
    results = json.load(open(path)) if os.path.exists(path) else {}
    for name in classes:
        seeds = class_seeds(n, name, per, rng)
        if not seeds:
            print(f"  {name}: no valid orbit decomposition for n={n}")
            continue
        with Pool(threads) as pool:
            got = pool.map(_job, [(P, g, kick) for P, g in seeds], chunksize=2)
        in_cls = max(got, key=lambda r: r[0])
        free = max(got, key=lambda r: r[2])
        kicked = max(got, key=lambda r: r[4])
        ints_c = ca.snap_to_disk(in_cls[1]); ex_c = ca.exact_minimum(ints_c)
        ints_f = ca.snap_to_disk(free[3]);   ex_f = ca.exact_minimum(ints_f)
        ints_k = ca.snap_to_disk(kicked[5]); ex_k = ca.exact_minimum(ints_k)
        dc = CS.describe(np.array(in_cls[1]))
        df = CS.describe(np.array(free[3]))
        dk = CS.describe(np.array(kicked[5]))
        prev = results.get(name)
        rec = {
            "seeds": len(seeds),
            "in_class_exact": str(ex_c), "in_class": float(ex_c),
            "in_class_refl_defect": dc["reflection_defect"],
            "in_class_split": f"{dc['on_circle']}+{dc['interior']}",
            "in_class_active": dc["active_triangles"],
            "released_exact": str(ex_f), "released": float(ex_f),
            "released_refl_defect": df["reflection_defect"],
            "released_split": f"{df['on_circle']}+{df['interior']}",
            "kicked_exact": str(ex_k), "kicked": float(ex_k),
            "kicked_refl_defect": dk["reflection_defect"],
            "kicked_split": f"{dk['on_circle']}+{dk['interior']}",
            "points_in_class": ints_c, "points_released": ints_f,
            "points_kicked": ints_k,
        }
        if prev is None or max(rec["in_class"], rec["released"], rec["kicked"]) > \
                max(prev["in_class"], prev["released"], prev["kicked"]):
            rec["seeds"] = rec["seeds"] + (prev["seeds"] if prev else 0)
            results[name] = rec
        else:
            prev["seeds"] += rec["seeds"]
        print(f"  {name:8s} in-class={float(ex_c):.12f} ({dc['on_circle']}+"
              f"{dc['interior']}, refl {dc['reflection_defect']:.1e})   "
              f"released={float(ex_f):.12f} ({df['on_circle']}+{df['interior']}, "
              f"refl {df['reflection_defect']:.1e})   "
              f"kicked={float(ex_k):.12f} (refl {dk['reflection_defect']:.1e})",
              flush=True)
        json.dump(results, open(path, "w"), indent=1)
    if results:
        best = max(results, key=lambda k: max(results[k]["in_class"],
                                              results[k]["released"],
                                              results[k]["kicked"]))
        print(f"best class: {best}")


if __name__ == "__main__":
    print(f"=== symmetry-class enumeration, n={sys.argv[1]} ===", flush=True)
    main()
