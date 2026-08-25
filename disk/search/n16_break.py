"""Deliberately break Cantrell's square symmetry and see whether it pays.

The D_4 optimum is also C_4-symmetric, C_2-symmetric and reflection-symmetric,
so it sits inside every weaker class.  Polishing it under a WEAKER constraint
therefore starts from the D_4 value and can only report an improvement if the
larger class really contains a better configuration nearby -- which is exactly
the question, and it is not answerable by seeding the weaker class at random
(that only measures how good the seeding was).

For each subgroup we read the permutation off the configuration itself by
matching the rotated/reflected point set back onto it, verify the match is
exact, then run the symmetry-constrained LP.  Also reported: the same run
starting from a within-class perturbation, so the weaker class is explored, not
just re-confirmed at its D_4 point.

Usage: python3 n16_break.py <config.json> <key-path> <trials> <threads>
"""
import json
import math
import os
import sys
from multiprocessing import Pool

import numpy as np
from scipy.optimize import linear_sum_assignment

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import circle_attack as ca         # noqa: E402
import circle_lp_polish as L       # noqa: E402
import circle_symfam as SF         # noqa: E402
import circle_symmetry as CS       # noqa: E402


def match_perm(P, M):
    """Permutation pi with P[pi[i]] ~= M p_i, and the residual of that match."""
    Q = P @ np.asarray(M).T
    D = np.hypot(P[:, None, 0] - Q[None, :, 0], P[:, None, 1] - Q[None, :, 1])
    r, c = linear_sum_assignment(D.T)
    perm = np.empty(len(P), dtype=int)
    perm[r] = c
    return perm.tolist(), float(D.T[r, c].max())


def project_sym(P, gens, rounds=8):
    """Average a configuration over the group so it lies exactly in the class."""
    P = np.array(P, float)
    for _ in range(rounds):
        acc = P.copy()
        for perm, M in gens:
            acc = acc + (P @ np.asarray(M).T)[np.argsort(perm)]
        P = acc / (1 + len(gens))
    return L.project(P)


def _job(arg):
    P, gens, sigma, seed = arg
    if sigma > 0:
        rng = np.random.default_rng(seed)
        P = project_sym(L.project(np.array(P) + rng.normal(0, sigma, np.array(P).shape)),
                        gens) if gens else L.project(np.array(P) + rng.normal(0, sigma, np.array(P).shape))
    Q, v = SF.lp_polish_sym(P, gens) if gens else L.lp_polish(P)
    return v, np.array(Q).tolist()


def main():
    src, keypath = sys.argv[1], sys.argv[2]
    trials = int(sys.argv[3])
    threads = int(sys.argv[4])
    node = json.load(open(os.path.join(HERE, src)))
    for k in keypath.split("/"):
        node = node[k]
    P = np.array(node, dtype=float)
    if np.abs(P).max() > 10:
        P = P / 10 ** 12
    n = len(P)
    base = L.min_area(P, L.triples_of(n))
    print(f"base = {base:.15f}   {CS.fmt(CS.describe(P))}")

    REF = np.array([[1.0, 0.0], [0.0, -1.0]])

    def rot(a):
        c, s = math.cos(a), math.sin(a)
        return np.array([[c, -s], [s, c]])

    # the reflection axis is not necessarily the x-axis; find it
    _, axis = CS.reflection_defect(P)
    A = rot(axis) @ REF @ rot(-axis)

    gens = {}
    p4, r4 = match_perm(P, rot(2 * math.pi / 4))
    p2, r2 = match_perm(P, rot(math.pi))
    pa, ra = match_perm(P, A)
    print(f"  generator match residuals: C_4 {r4:.2e}  C_2 {r2:.2e}  mirror {ra:.2e}")
    gens["D4 (as found)"] = [(p4, rot(2 * math.pi / 4)), (pa, A)]
    gens["C4 (square symmetry broken: no mirror)"] = [(p4, rot(2 * math.pi / 4))]
    gens["C2 (square symmetry broken: half turn only)"] = [(p2, rot(math.pi))]
    gens["mirror only"] = [(pa, A)]
    gens["none (unrestricted)"] = []

    out = {}
    for name, g in gens.items():
        jobs = [(P.tolist(), g, 0.0, 0)]
        for t in range(trials):
            for sigma in (0.005, 0.02, 0.06):
                jobs.append((P.tolist(), g, sigma, 500000 + 31 * t + int(sigma * 1000)))
        with Pool(threads) as pool:
            got = pool.map(_job, jobs, chunksize=2)
        v, Q = max(got, key=lambda r: r[0])
        ints = ca.snap_to_disk(Q)
        exact = ca.exact_minimum(ints)
        d = CS.describe(np.array(Q))
        gain = v / base - 1
        print(f"  {name:45s} {float(exact):.15f}  gain {gain:+.2e}  "
              f"refl {d['reflection_defect']:.1e}  split {d['on_circle']}+{d['interior']}"
              f"  {'IMPROVES' if gain > 1e-9 else 'no improvement'}")
        out[name] = {"exact": str(exact), "float": float(exact),
                     "float_prepolish": v, "relative_gain_vs_D4": gain,
                     "reflection_defect": d["reflection_defect"],
                     "split": f"{d['on_circle']}+{d['interior']}",
                     "seeds": len(jobs), "points": ints}
    out["_base"] = base
    json.dump(out, open(os.path.join(HERE, "break_n16.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
