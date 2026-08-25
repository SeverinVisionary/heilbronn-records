"""Measure the symmetry of a configuration, and count active (tied) triangles.

Friedman's circle page annotates a symmetry class for every row of Cantrell's
table.  If those configurations were found under a symmetry ansatz, then an
unrestricted search can only beat a row by leaving the symmetry class -- so
symmetry has to be MEASURED, not eyeballed.
"""
import math
import os
import sys

import numpy as np
from scipy.optimize import linear_sum_assignment

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import circle_lp_polish as L


def _match_defect(P, Q):
    """Max distance under the best one-to-one matching of Q onto P."""
    D = np.hypot(P[:, None, 0] - Q[None, :, 0], P[:, None, 1] - Q[None, :, 1])
    r, c = linear_sum_assignment(D)
    return float(D[r, c].max())


def reflection_defect(P, samples=1440, refine=6):
    """Smallest mismatch over all reflection axes through the origin."""
    P = np.asarray(P, float)

    def defect(theta):
        c, s = math.cos(2 * theta), math.sin(2 * theta)
        Q = np.column_stack([c * P[:, 0] + s * P[:, 1],
                             s * P[:, 0] - c * P[:, 1]])
        return _match_defect(P, Q)

    best_t = min(np.linspace(0, math.pi, samples, endpoint=False), key=defect)
    step = math.pi / samples
    for _ in range(refine):
        cand = [best_t - step, best_t, best_t + step]
        best_t = min(cand, key=defect)
        step /= 4
    return defect(best_t), best_t


def rotation_defect(P, k):
    """Mismatch under rotation by 2 pi / k about the origin."""
    P = np.asarray(P, float)
    a = 2 * math.pi / k
    c, s = math.cos(a), math.sin(a)
    Q = np.column_stack([c * P[:, 0] - s * P[:, 1], s * P[:, 0] + c * P[:, 1]])
    return _match_defect(P, Q)


def active_triangles(P, rel=1e-9):
    """How many triangles attain the minimum area (within a relative window).
    A converged max-min configuration has many; one or two means the value is a
    certified floor from snapping, not a converged optimum."""
    P = np.asarray(P, float)
    T = L.triples_of(len(P))
    A = np.abs(L.signed_areas(P, T))
    m = A.min()
    return int((A <= m * (1 + rel)).sum()), len(A), m


def describe(P):
    P = np.asarray(P, float)
    n = len(P)
    r = np.hypot(P[:, 0], P[:, 1])
    on = int((r > 1 - 1e-9).sum())
    refl, axis = reflection_defect(P)
    rots = {k: rotation_defect(P, k) for k in range(2, n + 1) if n % k == 0 or k <= 6}
    best_k = min(rots, key=rots.get) if rots else None
    act, tot, mn = active_triangles(P)
    return {"n": n, "on_circle": on, "interior": n - on,
            "min_area": mn, "active_triangles": act, "total_triangles": tot,
            "reflection_defect": refl, "reflection_axis_rad": axis,
            "best_rotation_order": best_k,
            "best_rotation_defect": rots[best_k] if best_k else None,
            "symmetric": bool(refl < 1e-6 or (best_k and rots[best_k] < 1e-6))}


def fmt(d):
    sym = ("reflection" if d["reflection_defect"] < 1e-6 else
           (f"C_{d['best_rotation_order']}"
            if d["best_rotation_defect"] is not None and d["best_rotation_defect"] < 1e-6
            else "ASYMMETRIC"))
    return (f"{d['on_circle']}+{d['interior']} split, "
            f"{d['active_triangles']}/{d['total_triangles']} active, "
            f"{sym} (refl defect {d['reflection_defect']:.2e}, "
            f"best rot C_{d['best_rotation_order']} defect "
            f"{d['best_rotation_defect']:.2e})")
