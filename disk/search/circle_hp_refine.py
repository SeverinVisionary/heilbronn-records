"""High-precision Newton refinement of a max-min critical point in the unit disk.

The sequential-LP endgame (`circle_lp_polish`) stalls at double precision: the
active triangles agree to ~1e-12 relative and no further LP step is accepted.
That leaves a configuration whose exact-rational snap has exactly ONE tied
triangle, which is a snap artifact rather than evidence about convergence.

This module closes the gap.  Given a configuration and its active-triangle set,
it solves the square system

    sigma_j * area_j(vars) = t     for every active triangle j

in mpmath at arbitrary precision.  Parameterisation:

  * boundary points (r = 1) carry a single angle variable, so containment is
    satisfied identically rather than as an inequality;
  * interior points appearing in an active triangle carry both coordinates;
  * points appearing in NO active triangle carry strict slack, do not constrain
    the critical point, and are held fixed (their slack is re-verified after);
  * one boundary angle is frozen to kill the rotation gauge.

For a genuine rigid max-min critical point this system is square.  If it is
not, the refinement falls back to least squares and says so -- a non-square
system is itself the finding, because it means the configuration still has a
free improving direction.
"""
from __future__ import annotations

import numpy as np
from mpmath import mp, mpf, matrix, lu_solve, cos, sin


def signed_area(C, tri):
    (xa, ya), (xb, yb), (xc, yc) = C[tri[0]], C[tri[1]], C[tri[2]]
    return ((xb - xa) * (yc - ya) - (xc - xa) * (yb - ya)) / 2


def refine(P, active, bnd_tol=1e-9, dps=60, iters=80, verbose=True):
    """Return (coords dict, t, boundary, interior, frozen, square?)."""
    mp.dps = dps
    n = len(P)
    P = np.asarray(P, float)
    r = np.hypot(P[:, 0], P[:, 1])
    active = [tuple(int(v) for v in t) for t in active]
    involved = sorted({i for t in active for i in t})
    B = [i for i in involved if r[i] > 1 - bnd_tol]
    I = [i for i in involved if r[i] <= 1 - bnd_tol]
    frozen = [i for i in range(n) if i not in involved]
    gauge = B[0]

    th = {i: mp.atan2(mpf(P[i, 1]), mpf(P[i, 0])) for i in B}
    fixed = {i: (mpf(P[i, 0]), mpf(P[i, 1])) for i in frozen}

    vars_ = ([("th", i) for i in B if i != gauge]
             + [("x", i) for i in I] + [("y", i) for i in I]
             + [("t", -1)])
    nv, ne = len(vars_), len(active)
    square = (nv == ne)
    if verbose:
        print(f"  boundary={len(B)} interior={len(I)} frozen={frozen} "
              f"vars={nv} eqs={ne} {'SQUARE' if square else 'NOT SQUARE'}")

    def coords(state):
        C = {}
        for i in B:
            a = state[("th", i)] if i != gauge else th[gauge]
            C[i] = (cos(a), sin(a))
        for i in I:
            C[i] = (state[("x", i)], state[("y", i)])
        for i in frozen:
            C[i] = fixed[i]
        return C

    state = {("th", i): th[i] for i in B if i != gauge}
    for i in I:
        state[("x", i)] = mpf(P[i, 0])
        state[("y", i)] = mpf(P[i, 1])
    C = coords(state)
    sig = [1 if signed_area(C, t) >= 0 else -1 for t in active]
    state[("t", -1)] = sum(sig[k] * signed_area(C, active[k])
                           for k in range(ne)) / ne

    def residual(st):
        C = coords(st)
        t = st[("t", -1)]
        return [sig[k] * signed_area(C, active[k]) - t for k in range(ne)]

    h = mpf(10) ** (-(dps // 2))
    for it in range(iters):
        R = residual(state)
        rn = max(abs(v) for v in R)
        if verbose and (it < 3 or it % 10 == 0):
            print(f"  newton it={it} |R|inf={mp.nstr(rn, 5)}")
        if rn < mpf(10) ** (-(dps - 8)):
            break
        J = matrix(ne, nv)
        for c, key in enumerate(vars_):
            s2 = dict(state)
            s2[key] = state[key] + h
            Rp = residual(s2)
            s2[key] = state[key] - h
            Rm = residual(s2)
            for rr in range(ne):
                J[rr, c] = (Rp[rr] - Rm[rr]) / (2 * h)
        b = matrix([-v for v in R])
        try:
            d = lu_solve(J, b) if square else lu_solve(J.T * J, J.T * b)
        except Exception as exc:                      # singular Jacobian
            if verbose:
                print("  linear solve failed:", exc)
            break
        for c, key in enumerate(vars_):
            state[key] = state[key] + d[c]

    if verbose:
        R = residual(state)
        print(f"  final |R|inf={mp.nstr(max(abs(v) for v in R), 5)}")
    return coords(state), state[("t", -1)], B, I, frozen, square


def snap_exact(C, n, scale):
    """Snap high-precision coordinates to a 1/scale integer grid, pulling any
    rounding escapee back inside the CLOSED unit disk."""
    pts = []
    for i in range(n):
        x, y = C[i]
        ix, iy = int(mp.floor(x * scale + mpf("0.5"))), int(mp.floor(y * scale + mpf("0.5")))
        while ix * ix + iy * iy > scale * scale:
            if abs(ix) >= abs(iy):
                ix -= 1 if ix > 0 else -1
            else:
                iy -= 1 if iy > 0 else -1
        pts.append((ix, iy))
    return pts
