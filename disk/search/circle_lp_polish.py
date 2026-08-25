"""Sequential-LP endgame for max-min triangle area in the unit disk.

At a configuration p the objective min_t |area_t(p)| is a degenerate max-min
ridge: many triangles are simultaneously minimal, and coordinate-wise or random
moves stall because every *single* direction that helps one active triangle
hurts another.  Linearising all triangle areas and solving

    max s   s.t.  sigma_t * (area_t + grad_t . d) >= s  for every triple t
                  2 (x_i dx_i + y_i dy_i) <= 1 - r_i^2  (stay in the disk)
                  |d|_inf <= trust

finds the coordinated move directly.  Iterate with a trust region; every step is
accepted only if the TRUE min area (recomputed exactly, not the linear model)
goes up, so the result is always a valid configuration.
"""
import numpy as np
from itertools import combinations
from scipy.optimize import linprog

_CACHE = {}


def triples_of(n):
    if n not in _CACHE:
        _CACHE[n] = np.array(list(combinations(range(n), 3)))
    return _CACHE[n]


def signed_areas(P, T):
    a, b, c = P[T[:, 0]], P[T[:, 1]], P[T[:, 2]]
    return 0.5 * ((b[:, 0] - a[:, 0]) * (c[:, 1] - a[:, 1])
                  - (c[:, 0] - a[:, 0]) * (b[:, 1] - a[:, 1]))


def project(P):
    r = np.hypot(P[:, 0], P[:, 1])
    bad = r > 1.0
    if bad.any():
        P = P.copy()
        P[bad] /= r[bad, None]
    return P


def min_area(P, T):
    return float(np.abs(signed_areas(P, T)).min())


def lp_polish(P, trust0=1e-2, iters=400, tol=1e-14):
    P = project(np.asarray(P, dtype=float).copy())
    n = len(P)
    T = triples_of(n)
    m = len(T)
    nv = 2 * n + 1                      # d (2n) then s
    best = min_area(P, T)
    trust = trust0
    for _ in range(iters):
        if trust < tol:
            break
        A = signed_areas(P, T)
        sig = np.where(A >= 0, 1.0, -1.0)
        x, y = P[:, 0], P[:, 1]
        ia, ib, ic = T[:, 0], T[:, 1], T[:, 2]

        G = np.zeros((m, 2 * n))
        rows = np.arange(m)
        # d(signed area)/d(coords), from A = .5[xa(yb-yc)+xb(yc-ya)+xc(ya-yb)]
        np.add.at(G, (rows, 2 * ia), 0.5 * (y[ib] - y[ic]))
        np.add.at(G, (rows, 2 * ib), 0.5 * (y[ic] - y[ia]))
        np.add.at(G, (rows, 2 * ic), 0.5 * (y[ia] - y[ib]))
        np.add.at(G, (rows, 2 * ia + 1), 0.5 * (x[ic] - x[ib]))
        np.add.at(G, (rows, 2 * ib + 1), 0.5 * (x[ia] - x[ic]))
        np.add.at(G, (rows, 2 * ic + 1), 0.5 * (x[ib] - x[ia]))

        # sigma*(A + G d) >= s   ->   -sigma*G d + s <= sigma*A
        A_ub = np.zeros((m + n, nv))
        A_ub[:m, :2 * n] = -sig[:, None] * G
        A_ub[:m, -1] = 1.0
        b_ub = np.concatenate([sig * A, np.empty(n)])
        # disk: 2(x dx + y dy) <= 1 - r^2
        for i in range(n):
            A_ub[m + i, 2 * i] = 2 * x[i]
            A_ub[m + i, 2 * i + 1] = 2 * y[i]
            b_ub[m + i] = 1.0 - (x[i] ** 2 + y[i] ** 2)

        c_obj = np.zeros(nv)
        c_obj[-1] = -1.0                # maximise s
        bounds = [(-trust, trust)] * (2 * n) + [(None, None)]
        res = linprog(c_obj, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method="highs")
        if not res.success:
            trust *= 0.5
            continue
        d = res.x[:2 * n].reshape(n, 2)
        Q = project(P + d)
        v = min_area(Q, T)
        if v > best * (1 + 1e-15):
            P, best = Q, v
            trust = min(trust * 1.6, 1e-2)
        else:
            trust *= 0.45
    return P, best
