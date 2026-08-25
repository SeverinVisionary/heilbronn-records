"""Explicit structural-family enumeration for one n.

A family is "b points constrained to the bounding circle, n-b strictly inside".
Random restarts only reach a family if the annealer happens to wander into it,
so this enumerates them directly and polishes each to convergence with the
family constraint ENFORCED (boundary points are held on the circle by a
tangential-move constraint plus renormalisation), which is what makes a
per-family number meaningful rather than an artefact of where a restart landed.
"""
import itertools, json, math, os, sys
from multiprocessing import Pool

import numpy as np
from scipy.optimize import linprog

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import circle_lp_polish as L

REPO = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, REPO)
import circle_attack as ca


def renorm(P, on):
    P = P.copy()
    if len(on):
        r = np.hypot(P[on, 0], P[on, 1])
        r[r == 0] = 1.0
        P[on] = P[on] / r[:, None]
    inside = [i for i in range(len(P)) if i not in set(on)]
    if inside:
        r = np.hypot(P[inside, 0], P[inside, 1])
        bad = r > 1.0
        if bad.any():
            idx = np.array(inside)[bad]
            P[idx] /= np.hypot(P[idx, 0], P[idx, 1])[:, None]
    return P


def lp_polish_family(P, on, trust0=1e-2, iters=500, tol=1e-14):
    """Same sequential LP as lp_polish, but points in `on` are held on the unit
    circle (tangential displacement + renormalisation) so the family is fixed."""
    on = list(on)
    onset = set(on)
    P = renorm(np.asarray(P, float).copy(), on)
    n = len(P)
    T = L.triples_of(n)
    m = len(T)
    nv = 2 * n + 1
    best = L.min_area(P, T)
    trust = trust0
    for _ in range(iters):
        if trust < tol:
            break
        A = L.signed_areas(P, T)
        sig = np.where(A >= 0, 1.0, -1.0)
        x, y = P[:, 0], P[:, 1]
        ia, ib, ic = T[:, 0], T[:, 1], T[:, 2]
        G = np.zeros((m, 2 * n))
        rows = np.arange(m)
        np.add.at(G, (rows, 2 * ia), 0.5 * (y[ib] - y[ic]))
        np.add.at(G, (rows, 2 * ib), 0.5 * (y[ic] - y[ia]))
        np.add.at(G, (rows, 2 * ic), 0.5 * (y[ia] - y[ib]))
        np.add.at(G, (rows, 2 * ia + 1), 0.5 * (x[ic] - x[ib]))
        np.add.at(G, (rows, 2 * ib + 1), 0.5 * (x[ia] - x[ic]))
        np.add.at(G, (rows, 2 * ic + 1), 0.5 * (x[ib] - x[ia]))

        interior = [i for i in range(n) if i not in onset]
        A_ub = np.zeros((m + len(interior), nv))
        A_ub[:m, :2 * n] = -sig[:, None] * G
        A_ub[:m, -1] = 1.0
        b_ub = np.concatenate([sig * A, np.empty(len(interior))])
        for r, i in enumerate(interior):
            A_ub[m + r, 2 * i] = 2 * x[i]
            A_ub[m + r, 2 * i + 1] = 2 * y[i]
            b_ub[m + r] = 1.0 - (x[i] ** 2 + y[i] ** 2)
        # boundary points move tangentially: x dx + y dy = 0
        A_eq = np.zeros((len(on), nv)) if on else None
        b_eq = np.zeros(len(on)) if on else None
        for r, i in enumerate(on):
            A_eq[r, 2 * i] = x[i]
            A_eq[r, 2 * i + 1] = y[i]

        c = np.zeros(nv); c[-1] = -1.0
        bounds = [(-trust, trust)] * (2 * n) + [(None, None)]
        res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
                      bounds=bounds, method="highs")
        if not res.success:
            trust *= 0.5
            continue
        Q = renorm(P + res.x[:2 * n].reshape(n, 2), on)
        v = L.min_area(Q, T)
        if v > best * (1 + 1e-15):
            P, best = Q, v
            trust = min(trust * 1.6, 1e-2)
        else:
            trust *= 0.45
    return P, best


def seeds_for(n, b, count, rng):
    """Random and symmetric seeds with exactly b points on the circle."""
    out = []
    inner = n - b
    # symmetric: regular b-gon outside, regular inner-gon inside at various radii
    for rad in np.linspace(0.15, 0.85, 12):
        for phase in (0.0, 0.5):
            P = [(math.cos(2 * math.pi * i / b), math.sin(2 * math.pi * i / b))
                 for i in range(b)]
            for j in range(inner):
                th = 2 * math.pi * (j + phase) / max(inner, 1)
                P.append((rad * math.cos(th), rad * math.sin(th)))
            out.append(P)
    # C_k symmetric seeds for small k
    for k in (2, 3, 4, 5):
        if b % k or (inner and inner % k):
            continue
        for rad in np.linspace(0.2, 0.8, 6):
            P = []
            for i in range(b):
                th = 2 * math.pi * i / b
                P.append((math.cos(th), math.sin(th)))
            for j in range(inner):
                th = 2 * math.pi * j / inner if inner else 0.0
                P.append((rad * math.cos(th), rad * math.sin(th)))
            out.append(P)
    while len(out) < count:
        ang = np.sort(rng.uniform(0, 2 * np.pi, b))
        P = [(math.cos(a), math.sin(a)) for a in ang]
        for _ in range(inner):
            th = rng.uniform(0, 2 * math.pi)
            rad = math.sqrt(rng.uniform(0.01, 0.97))
            P.append((rad * math.cos(th), rad * math.sin(th)))
        out.append(P)
    return out[:count]


def _job(args):
    """Two answers per seed: the value reachable WITHIN the family (boundary set
    held fixed), and the value reachable when the seed is allowed to leave the
    family (free polish, which may move points on or off the circle)."""
    P, on = args
    Q, v = lp_polish_family(P, on)
    R, w = L.lp_polish(Q)
    return v, Q.tolist(), w, R.tolist()


def run(n, per_family, threads):
    rng = np.random.default_rng(20260823)
    results = {}
    for b in range(3, n + 1):
        on = list(range(b))
        jobs = [(P, on) for P in seeds_for(n, b, per_family, rng)]
        with Pool(threads) as pool:
            got = pool.map(_job, jobs, chunksize=8)
        infam = max(got, key=lambda r: r[0])
        free = max(got, key=lambda r: r[2])
        hits = sum(1 for r in got if r[0] > infam[0] * (1 - 1e-9))
        fhits = sum(1 for r in got if r[2] > free[2] * (1 - 1e-9))

        ints_in = ca.snap_to_disk(infam[1]); ex_in = ca.exact_minimum(ints_in)
        ints_fr = ca.snap_to_disk(free[3]);  ex_fr = ca.exact_minimum(ints_fr)
        arr = np.array(free[3])
        final_on = int((np.hypot(arr[:, 0], arr[:, 1]) > 1 - 1e-9).sum())
        results[b] = {"family": f"{b} on circle + {n-b} interior",
                      "in_family_exact": str(ex_in), "in_family": float(ex_in),
                      "free_exact": str(ex_fr), "free": float(ex_fr),
                      "seeds": len(jobs), "seeds_at_family_best": hits,
                      "seeds_at_free_best": fhits,
                      "free_winner_on_circle": final_on,
                      "points_in_family": ints_in, "points_free": ints_fr}
        print(f"  b={b:2d}  {b:2d} on circle + {n-b:2d} interior   "
              f"in-family={float(ex_in):.12f} ({hits}/{len(jobs)})   "
              f"free={float(ex_fr):.12f} ({fhits}/{len(jobs)}, ends {final_on} on circle)",
              flush=True)
    return results


if __name__ == "__main__":
    n = int(sys.argv[1]); per_family = int(sys.argv[2]); threads = int(sys.argv[3])
    print(f"=== structural family enumeration, n={n}, {per_family} seeds/family ===",
          flush=True)
    res = run(n, per_family, threads)
    best_b = max(res, key=lambda b: res[b]["free"])
    print(f"best family: b={best_b} ({res[best_b]['family']}) "
          f"at {res[best_b]['free']:.12f}", flush=True)
    json.dump(res, open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                     f"families_n{n}.json"), "w"), indent=1)
