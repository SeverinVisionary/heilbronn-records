"""Symmetry-class enumeration for the circle Heilbronn problem.

Friedman annotates a symmetry class for every row of Cantrell's table, and the
two rows an unrestricted search beats (n = 13, 14) are exactly the two whose
winners are asymmetric.  So at a new row the question "does asymmetry help
here?" has to be answered by *constructing* the symmetric optima, not by hoping
random restarts land in the right basin.

This module builds configurations inside a named symmetry class and polishes
them with the symmetry ENFORCED, by adding the linear equalities

    d_{pi(i)} = R d_i        for every generator (pi, R) of the group

to the sequential LP.  A symmetric seed therefore stays symmetric to machine
precision no matter what the LP would rather do, which is what makes the
per-class number meaningful.  Each seed is then ALSO polished with the
constraints released (and with a deliberate asymmetric kick), so the two numbers
answer "what is the best configuration in this class" and "does leaving the
class help" separately.

Groups supported, as (permutation, 2x2 matrix) generator lists:
  C_k   rotation by 2 pi / k
  D_k   C_k plus a reflection in the x-axis
"""
from __future__ import annotations

import math
from itertools import combinations

import numpy as np
from scipy.optimize import linprog

import circle_lp_polish as L


def rot(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, -s], [s, c]])


REFLECT = np.array([[1.0, 0.0], [0.0, -1.0]])


# ---------------------------------------------------------------- seeds ----

def c_k_seed(k, orbits):
    """orbits: list of (radius, theta) representatives; each spawns k points."""
    P, perm = [], []
    for (r, th) in orbits:
        base = len(P)
        for j in range(k):
            a = th + 2 * math.pi * j / k
            P.append((r * math.cos(a), r * math.sin(a)))
        perm.extend([base + (j + 1) % k for j in range(k)])
    return np.array(P), [(perm, rot(2 * math.pi / k))]


def d_k_seed(k, generic, mirror):
    """D_k configuration.

    `generic`: (radius, theta) reps in general position -> orbits of size 2k
               (the C_k orbit of the point together with the C_k orbit of its
               mirror image).
    `mirror` : (radius, j) reps lying on a mirror line -> orbits of size k;
               j = 0 puts the point on the x-axis, j = 1 on the half-angle line.
    """
    P = []
    blocks = []                      # (start, size, kind)
    for (r, th) in generic:
        start = len(P)
        for j in range(k):           # upper copy
            a = th + 2 * math.pi * j / k
            P.append((r * math.cos(a), r * math.sin(a)))
        for j in range(k):           # mirrored copy
            a = -th + 2 * math.pi * j / k
            P.append((r * math.cos(a), r * math.sin(a)))
        blocks.append((start, k, "generic"))
    for (r, j0) in mirror:
        start = len(P)
        th = math.pi / k * j0
        for j in range(k):
            a = th + 2 * math.pi * j / k
            P.append((r * math.cos(a), r * math.sin(a)))
        blocks.append((start, k, "mirror"))
    P = np.array(P)
    n = len(P)

    # rotation permutation
    pr = list(range(n))
    for (start, size, kind) in blocks:
        reps = 2 if kind == "generic" else 1
        for c in range(reps):
            b = start + c * size
            for j in range(size):
                pr[b + j] = b + (j + 1) % size
    # reflection permutation: matched by nearest image (exact by construction)
    Q = P @ REFLECT.T
    pf = _match(P, Q)
    return P, [(pr, rot(2 * math.pi / k)), (pf, REFLECT)]


def reflect_seed(pairs, axis):
    """Pure reflection symmetry: `pairs` off-axis reps (each spawns 2 points),
    `axis` points on the mirror line (radius, sign)."""
    P = []
    for (r, th) in pairs:
        P.append((r * math.cos(th), r * math.sin(th)))
        P.append((r * math.cos(th), -r * math.sin(th)))
    for (r, sgn) in axis:
        P.append((sgn * r, 0.0))
    P = np.array(P)
    Q = P @ REFLECT.T
    return P, [(_match(P, Q), REFLECT)]


def _match(P, Q):
    """Permutation pi with P[pi[i]] ~= Q[i] (used to read off the group action)."""
    from scipy.optimize import linear_sum_assignment
    D = np.hypot(P[:, None, 0] - Q[None, :, 0], P[:, None, 1] - Q[None, :, 1])
    r, c = linear_sum_assignment(D.T)
    perm = np.empty(len(P), dtype=int)
    perm[r] = c
    return perm.tolist()


# --------------------------------------------------------------- polish ----

def sym_equalities(gens, n):
    """Rows of A_eq expressing d_{pi(i)} = R d_i for every generator."""
    rows = []
    for perm, R in gens:
        for i in range(n):
            j = perm[i]
            for comp in (0, 1):
                row = np.zeros(2 * n + 1)
                row[2 * j + comp] += 1.0
                row[2 * i] -= R[comp, 0]
                row[2 * i + 1] -= R[comp, 1]
                rows.append(row)
    if not rows:
        return None
    # Redundant rows are handed to HiGHS as they are: its presolve removes
    # them.  Filtering them here with an unpivoted QR is NOT rank-revealing and
    # silently dropped essential rows, which let the reflection generator leak
    # (a "D_4" polish came back with reflection defect 6.6e-02).
    return np.array(rows)


def lp_polish_sym(P, gens, trust0=1e-2, iters=400, tol=1e-14):
    """Sequential LP with the symmetry generators imposed as equalities."""
    P = L.project(np.asarray(P, float).copy())
    n = len(P)
    T = L.triples_of(n)
    m = len(T)
    nv = 2 * n + 1
    A_eq = sym_equalities(gens, n)
    b_eq = np.zeros(len(A_eq)) if A_eq is not None else None
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
        A_ub = np.zeros((m + n, nv))
        A_ub[:m, :2 * n] = -sig[:, None] * G
        A_ub[:m, -1] = 1.0
        b_ub = np.concatenate([sig * A, np.empty(n)])
        for i in range(n):
            A_ub[m + i, 2 * i] = 2 * x[i]
            A_ub[m + i, 2 * i + 1] = 2 * y[i]
            b_ub[m + i] = 1.0 - (x[i] ** 2 + y[i] ** 2)
        c = np.zeros(nv)
        c[-1] = -1.0
        res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
                      bounds=[(-trust, trust)] * (2 * n) + [(None, None)],
                      method="highs")
        if not res.success:
            trust *= 0.5
            continue
        Q = L.project(P + res.x[:2 * n].reshape(n, 2))
        v = L.min_area(Q, T)
        if v > best * (1 + 1e-15):
            P, best = Q, v
            trust = min(trust * 1.6, trust0)
        else:
            trust *= 0.45
    return P, best
