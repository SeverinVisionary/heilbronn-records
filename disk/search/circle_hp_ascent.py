"""High-precision sequential-LP ascent for max-min triangle area in the unit disk.

`circle_lp_polish.lp_polish` runs entirely in double precision and accepts a
step only when the true minimum improves by a relative `1e-15`.  Near a critical
point the remaining improvements are *smaller than that*: at n = 14 the residual
gain is `~9e-15` relative, i.e. right at double round-off, so the double
pipeline reports "converged" while a real ascent direction is still available.
That is exactly the failure that leaves a configuration with one exact tie
instead of a full active set.

The fix is not more iterations but more precision, and the trick that makes it
cheap is to linearise in SHIFTED coordinates.  Writing `t0` for the current
minimum and `delta_t = sigma_t * area_t - t0`, the LP

    max s'   s.t.  delta_t + grad_t . d >= s'   for every triple t
                   2 (x_i dx_i + y_i dy_i) <= 1 - r_i^2
                   |d|_inf <= trust

is equivalent to the unshifted one but its data are the *small* numbers
`delta_t`, which a float carries to full relative accuracy even when the areas
themselves agree to 25 digits.  Gradients are O(1) and double is plenty for
them.  The state, the areas and the accept/reject decision stay in mpmath, so
the ascent keeps working far below double round-off.

Every step is accepted only if the TRUE minimum over all C(n,3) triples, in high
precision, goes up; a backtracking line search along the LP direction picks the
step length, because the boundary constraint is curved and the linear model
over-reaches.
"""
from __future__ import annotations

from itertools import combinations

import numpy as np
from mpmath import mp, mpf, sqrt as mpsqrt
from scipy.optimize import linprog


def to_mp(P):
    return [[mpf(x), mpf(y)] for x, y in P]


def areas_mp(Q, T):
    """Signed areas, high precision."""
    out = []
    for a, b, c in T:
        out.append(((Q[b][0] - Q[a][0]) * (Q[c][1] - Q[a][1])
                    - (Q[c][0] - Q[a][0]) * (Q[b][1] - Q[a][1])) / 2)
    return out


def min_area_mp(Q, T):
    return min(abs(v) for v in areas_mp(Q, T))


def project_mp(Q):
    for p in Q:
        r2 = p[0] * p[0] + p[1] * p[1]
        if r2 > 1:
            r = mpsqrt(r2)
            p[0] /= r
            p[1] /= r
    return Q


def ascend(P, dps=60, iters=400, trust0=1e-3, verbose=True, tol_trust=1e-30):
    """P: list of (x, y) floats or mpf.  Returns (Q, min_area) in mpmath."""
    mp.dps = dps
    n = len(P)
    T = list(combinations(range(n), 3))
    m = len(T)
    Q = project_mp(to_mp(P))
    best = min_area_mp(Q, T)
    trust = mpf(trust0)
    nv = 2 * n + 1
    stall = 0
    for it in range(iters):
        if trust < mpf(tol_trust):
            break
        A = areas_mp(Q, T)
        sig = np.array([1.0 if v >= 0 else -1.0 for v in A])
        t0 = min(abs(v) for v in A)
        # shifted, so the LP data keep full relative accuracy
        delta = np.array([float(sig[k] * A[k] - t0) for k in range(m)])
        x = np.array([float(p[0]) for p in Q])
        y = np.array([float(p[1]) for p in Q])
        Tarr = np.array(T)
        ia, ib, ic = Tarr[:, 0], Tarr[:, 1], Tarr[:, 2]
        G = np.zeros((m, 2 * n))
        rows = np.arange(m)
        np.add.at(G, (rows, 2 * ia), 0.5 * (y[ib] - y[ic]))
        np.add.at(G, (rows, 2 * ib), 0.5 * (y[ic] - y[ia]))
        np.add.at(G, (rows, 2 * ic), 0.5 * (y[ia] - y[ib]))
        np.add.at(G, (rows, 2 * ia + 1), 0.5 * (x[ic] - x[ib]))
        np.add.at(G, (rows, 2 * ib + 1), 0.5 * (x[ia] - x[ic]))
        np.add.at(G, (rows, 2 * ic + 1), 0.5 * (x[ib] - x[ia]))

        A_ub = np.zeros((m + n, nv))
        A_ub[:m, :2 * n] = -sig[:, None] * G
        A_ub[:m, -1] = 1.0
        b_ub = np.empty(m + n)
        b_ub[:m] = delta
        for i in range(n):
            A_ub[m + i, 2 * i] = 2 * x[i]
            A_ub[m + i, 2 * i + 1] = 2 * y[i]
            # exact residual of the disk constraint, in high precision
            b_ub[m + i] = float(1 - (Q[i][0] ** 2 + Q[i][1] ** 2))
        c = np.zeros(nv)
        c[-1] = -1.0
        tr = float(trust)
        res = linprog(c, A_ub=A_ub, b_ub=b_ub,
                      bounds=[(-tr, tr)] * (2 * n) + [(None, None)],
                      method="highs")
        if not res.success:
            trust *= mpf("0.5")
            continue
        d = res.x[:2 * n].reshape(n, 2)
        # backtracking line search on the TRUE high-precision minimum
        got = None
        scale = mpf(1)
        for _ in range(60):
            R = [[Q[i][0] + scale * mpf(d[i, 0]), Q[i][1] + scale * mpf(d[i, 1])]
                 for i in range(n)]
            project_mp(R)
            v = min_area_mp(R, T)
            if v > best:
                got = (R, v)
                break
            scale *= mpf("0.35")
        if got is None:
            trust *= mpf("0.3")
            stall += 1
            if stall > 40:
                break
            continue
        stall = 0
        Q, prev = got[0], best
        best = got[1]
        if verbose and (it < 10 or it % 10 == 0):
            print(f"  it={it:4d} min={mp.nstr(best, 24)} gain={mp.nstr(best - prev, 4)}"
                  f" trust={mp.nstr(trust, 3)} step={mp.nstr(scale, 3)}")
        trust = min(trust * mpf("1.5"), mpf(trust0))
    if verbose:
        print(f"  final min={mp.nstr(best, 30)}  trust={mp.nstr(trust, 3)}")
    return Q, best


def active_set(Q, rel=None, abs_win=None):
    n = len(Q)
    T = list(combinations(range(n), 3))
    A = [abs(v) for v in areas_mp(Q, T)]
    m = min(A)
    if abs_win is None:
        abs_win = m * mpf(rel if rel is not None else "1e-20")
    return [T[k] for k in range(len(T)) if A[k] <= m + abs_win], m, T, A
