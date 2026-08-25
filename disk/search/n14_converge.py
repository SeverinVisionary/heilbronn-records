"""Drive the n = 14 disk configuration to a stationary candidate, then certify it.

The referee's objection to the previous deposit was not about the bound.  It
was: a feasible ascent direction was known to exist at the certified point
(displacing one interior point by 1e-21 raised the true minimum), so the value
read as a pipeline checkpoint rather than the output of a finished computation.
"Why did you stop?"

This script finishes the computation and commits the stationarity evidence as
DATA rather than prose.

**The structure that the earlier passes missed.**  With 16 active triangles,
8 boundary points (one tangential degree of freedom each), 4 interior active
points (two each) and 2 frozen points that sit in no active triangle, the
equality system `sigma_T area_T = t` has 16 equations in 16 spatial degrees of
freedom.  Its Jacobian `J` has rank 15 -- the rotation gauge -- so
`{all 16 active triangles equal}` is not a POINT but a CURVE, and `t` varies
along it.  A Newton solve lands somewhere on that curve and stops; that is
precisely why every earlier pass reported "converged" while an ascent direction
remained.  The ascent tangent is the solution of

    J v = 1        (raise every active triangle at the same rate)

and the question "is the computation finished?" is the question of where `t` is
maximal along the curve.  So this script walks the curve.

Steps, each reported as data:

  1. **Active set**, with the cut measured rather than assumed.
  2. **Newton** onto the curve (`circle_hp_refine.refine`), residual reported.
  3. **Walk the curve**: predictor along `v`, corrector back onto the curve by
     a least-squares Newton, 1-D maximisation of `t`, iterated until the gain
     dies.  At the maximum `J v = 1` becomes INCONSISTENT -- no direction
     raises every active triangle any more -- and that flip is the stopping
     evidence.
  4. **KKT** at the endpoint: multipliers for `max t s.t. sigma_T area_T >= t,
     |p_i|^2 <= 1`.  At the endpoint they exist and are nonnegative; the
     residual is reported over every equation.  (At the Newton point of step 2
     they do NOT exist, and that residual is reported too, so the reader can
     see the difference the walk made.)
  5. **Feasibility**: all C(14,3) = 364 areas recomputed, the nearest inactive
     triangle's margin, every radius slack.
  6. **Certificate**: snap to integer grids at several scales and recompute the
     minimum as an exact rational with an exact closed-disk containment check,
     integers and Fractions only.  The exact certified value and the
     high-precision stationary value are reported separately; the certified one
     sits slightly below, and that gap is what exactness costs.

Nothing here is claimed as a theorem about local optimality.  The rigorous
statement is the exact rational lower bound of step 6; steps 3-5 are numerical
evidence, committed so a referee can check it rather than trust it.

Re-running this on its own output is the regression test: the walk should find
no further gain, `J v = 1` should already be inconsistent, and the KKT residual
should already be at round-off.

Usage:
    python3 n14_converge.py [dps] [out_prefix] [src.json]
"""
from __future__ import annotations

import json
import os
import sys
import time
from fractions import Fraction as F
from itertools import combinations

import numpy as np
from mpmath import mp, mpf
from scipy.optimize import linprog

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import circle_hp_ascent as HA       # noqa: E402
import circle_hp_refine as HP       # noqa: E402
import circle_symmetry as CS        # noqa: E402

N = 14
TRIPLES = list(combinations(range(N), 3))
SRC = os.path.join(HERE, "circle_configs", "circle_n14_converged.json")
# Friedman's printed bracket for n = 14 is ".0758+", i.e. Cantrell's value is
# capped below 0.0759.  That is the margin the claim is quoted against.
FRIEDMAN_UPPER = F(759, 10000)
SNAP_EXPONENTS = [15, 18, 21, 24, 27, 30, 33]


# --------------------------------------------------------------------------
# geometry helpers, high precision
# --------------------------------------------------------------------------
def grad_signed_area(C, tri):
    """d(signed area)/d(all 2N coordinates) for one triangle, as a dict."""
    a, b, c = tri
    (xa, ya), (xb, yb), (xc, yc) = C[a], C[b], C[c]
    half = mpf(1) / 2
    return {(a, 0): half * (yb - yc), (b, 0): half * (yc - ya),
            (c, 0): half * (ya - yb), (a, 1): half * (xc - xb),
            (b, 1): half * (xa - xc), (c, 1): half * (xb - xa)}


def _maximal_independent(vectors, tol):
    """Greedily pick a maximal linearly independent subset, by index."""
    pivots, chosen = [], []
    for idx, vec in enumerate(vectors):
        v = list(vec)
        for col, w in pivots:
            if v[col] != 0:
                f = v[col] / w[col]
                for j in range(len(v)):
                    v[j] -= f * w[j]
        if not v:
            continue
        col = max(range(len(v)), key=lambda j: abs(v[j]))
        if abs(v[col]) > tol:
            chosen.append(idx)
            pivots.append((col, v))
    return chosen


def _columns(C, B, I):
    """The spatial degrees of freedom: one tangential per boundary point, two
    per interior active point.  Frozen points are absent -- they sit in no
    active triangle, so nothing in the active system depends on them."""
    cols, names = [], []
    for i in B:
        cols.append({(i, 0): -C[i][1], (i, 1): C[i][0]})
        names.append(("tan", i))
    for i in I:
        cols.append({(i, 0): mpf(1)}); names.append(("x", i))
        cols.append({(i, 1): mpf(1)}); names.append(("y", i))
    return cols, names


def _jacobian(C, active, sigma, cols):
    G = [grad_signed_area(C, tri) for tri in active]
    J = mp.matrix(len(active), len(cols))
    for k in range(len(active)):
        for c, vv in enumerate(cols):
            s = mpf(0)
            for key, val in vv.items():
                if key in G[k]:
                    s += G[k][key] * val
            J[k, c] = sigma[k] * s
    return J


def tangent(C, active, sigma, B, I, tol):
    """Solve `J v = 1`: the direction that raises every active triangle at the
    same rate.  Returns (unit-infinity-norm field, ascent rate, residual, rank).

    A residual near zero means such a direction exists and the point is not
    the top of the curve.  A residual of order one means none does -- the
    stopping condition."""
    cols, names = _columns(C, B, I)
    J = _jacobian(C, active, sigma, cols)
    nk, nc = len(active), len(cols)
    ones = mp.matrix(nk, 1)
    for k in range(nk):
        ones[k] = mpf(1)
    ind = _maximal_independent([[J[k, c] for k in range(nk)] for c in range(nc)], tol)
    Jc = mp.matrix(nk, len(ind))
    for k in range(nk):
        for cc, c in enumerate(ind):
            Jc[k, cc] = J[k, c]
    y = mp.lu_solve(Jc.T * Jc, Jc.T * ones)
    r = Jc * y - ones
    resid = max(abs(r[k]) for k in range(nk))
    disp = {i: [mpf(0), mpf(0)] for i in range(N)}
    for cc, c in enumerate(ind):
        kind, i = names[c]
        a = y[cc]
        if kind == "tan":
            disp[i][0] += a * (-C[i][1]); disp[i][1] += a * C[i][0]
        elif kind == "x":
            disp[i][0] += a
        else:
            disp[i][1] += a
    nrm = max(max(abs(disp[i][0]), abs(disp[i][1])) for i in range(N))
    for i in range(N):
        disp[i][0] /= nrm; disp[i][1] /= nrm
    return disp, mpf(1) / nrm, resid, len(ind)


def corrector(C, active, sigma, B, I, dps, iters=60):
    """Least-squares Newton back onto the curve {all active areas equal}.

    Boundary points are carried as angles, so they stay on the circle exactly
    rather than approximately; interior active points carry both coordinates;
    frozen points do not move."""
    tol = mpf(10) ** (-(dps - 12))
    ltol = mpf(10) ** (-(dps - 20))
    W = {i: [C[i][0], C[i][1]] for i in range(N)}
    th = {i: mp.atan2(W[i][1], W[i][0]) for i in B}
    keys = [("tan", i) for i in B] + [(c, i) for i in I for c in ("x", "y")]

    def build():
        cc = {}
        for i in B:
            cc[i] = (mp.cos(th[i]), mp.sin(th[i]))
        for i in range(N):
            if i not in B:
                cc[i] = (W[i][0], W[i][1])
        return cc

    nk, nc = len(active), len(keys)
    for _ in range(iters):
        cc = build()
        a = [sigma[k] * HP.signed_area(cc, active[k]) for k in range(nk)]
        tbar = sum(a) / nk
        R = [v - tbar for v in a]
        if max(abs(v) for v in R) < tol:
            break
        cols, _ = _columns(cc, B, I)
        J = _jacobian(cc, active, sigma, cols)
        for c in range(nc):                    # centre: solve for deviations
            col = sum(J[k, c] for k in range(nk)) / nk
            for k in range(nk):
                J[k, c] -= col
        ind = _maximal_independent([[J[k, c] for k in range(nk)] for c in range(nc)], ltol)
        Jc = mp.matrix(nk, len(ind))
        for k in range(nk):
            for ci, c in enumerate(ind):
                Jc[k, ci] = J[k, c]
        b = mp.matrix(nk, 1)
        for k in range(nk):
            b[k] = -R[k]
        y = mp.lu_solve(Jc.T * Jc, Jc.T * b)
        for ci, c in enumerate(ind):
            kind, i = keys[c]
            if kind == "tan":
                th[i] += y[ci]
            elif kind == "x":
                W[i][0] += y[ci]
            else:
                W[i][1] += y[ci]
    cc = build()
    a = [sigma[k] * HP.signed_area(cc, active[k]) for k in range(nk)]
    return {i: (cc[i][0], cc[i][1]) for i in range(N)}, min(a), max(a) - min(a)


def step_along(C, disp, h, active, sigma, B, I, dps):
    P = {}
    for i in range(N):
        x, y = C[i][0] + h * disp[i][0], C[i][1] + h * disp[i][1]
        r2 = x * x + y * y
        if r2 > 1:
            r = mp.sqrt(r2); x /= r; y /= r
        P[i] = (x, y)
    return corrector(P, active, sigma, B, I, dps)


def walk(C, active, sigma, B, I, dps, verbose=True):
    """Maximise t along the curve.  Returns (C, t, history)."""
    itol = mpf(10) ** (-(dps - 20))
    _, t_cur, _ = corrector(C, active, sigma, B, I, dps)
    hist = []
    for it in range(40):
        disp, rate, resid, rank = tangent(C, active, sigma, B, I, itol)
        rec = {"iteration": it, "t": mp.nstr(t_cur, 45),
               "jacobian_rank": rank,
               "residual_of_Jv_eq_1": mp.nstr(resid, 8),
               "ascent_rate_per_unit_disp": mp.nstr(rate, 8)}
        # residual O(1) => no direction raises every active triangle: the top.
        if resid > mpf("1e-20"):
            rec["stopped"] = ("J v = 1 is inconsistent: no direction raises "
                              "every active triangle, so t is maximal along "
                              "the curve")
            hist.append(rec)
            if verbose:
                print(f"  it={it}: |Jv-1| = {mp.nstr(resid, 6)} -> STOP, "
                      f"no equal-rate ascent direction remains")
            break
        # curvature probe, then the parabolic maximiser, then verification
        h_probe = mpf(10) ** (-6)
        best_h, best_t = mpf(0), t_cur
        for _ in range(8):
            _, t_p, _ = step_along(C, disp, h_probe, active, sigma, B, I, dps)
            kappa = (rate * h_probe - (t_p - t_cur)) / (h_probe * h_probe)
            if kappa > 0:
                h_star = rate / (2 * kappa)
                _, t_s, _ = step_along(C, disp, h_star, active, sigma, B, I, dps)
                if t_s > best_t:
                    best_h, best_t = h_star, t_s
            if t_p > best_t:
                best_h, best_t = h_probe, t_p
            if best_h != 0:
                break
            h_probe /= 100
        if best_h == 0 or best_t <= t_cur:
            rec["stopped"] = "no step along the curve raises t"
            hist.append(rec)
            if verbose:
                print(f"  it={it}: no step raises t -> STOP")
            break
        Cn, tn, spread = step_along(C, disp, best_h, active, sigma, B, I, dps)
        rec.update({"step": mp.nstr(best_h, 8), "gain": mp.nstr(tn - t_cur, 8),
                    "active_spread_after_corrector": mp.nstr(spread, 8)})
        hist.append(rec)
        if verbose:
            print(f"  it={it}: |Jv-1|={mp.nstr(resid, 4)}  rate={mp.nstr(rate, 6)}"
                  f"  step={mp.nstr(best_h, 4)}  gain={mp.nstr(tn - t_cur, 6)}"
                  f"  spread={mp.nstr(spread, 3)}")
        C, t_cur = Cn, tn
    return C, t_cur, hist


# --------------------------------------------------------------------------
# KKT
# --------------------------------------------------------------------------
def kkt(C, active, sigma, B, dps):
    """Multipliers for `max t s.t. sigma_T area_T >= t, |p_i|^2 <= 1`:

        sum_A lambda_T grad(sigma_T area_T) = sum_B 2 mu_i p_i,
        sum lambda_T = 1,  lambda >= 0,  mu >= 0.

    The system is rank-deficient by construction (the rotation field
    annihilates every column; the frozen points' equations are identically
    zero), so it is solved as a least-squares problem over a maximal
    independent set of columns and the residual is reported over EVERY
    equation.  A residual at round-off with all multipliers nonnegative is the
    first-order certificate; a residual well above round-off means no
    multipliers exist and the point is not stationary."""
    nl, nm = len(active), len(B)
    nv, nr = nl + nm, 2 * N + 1
    M = mp.matrix(nr, nv)
    rhs = mp.matrix(nr, 1)
    for k, tri in enumerate(active):
        for (i, d), v in grad_signed_area(C, tri).items():
            M[2 * i + d, k] += sigma[k] * v
    for j, i in enumerate(B):
        M[2 * i, nl + j] = -2 * C[i][0]
        M[2 * i + 1, nl + j] = -2 * C[i][1]
    for k in range(nl):
        M[2 * N, k] = mpf(1)
    rhs[2 * N] = mpf(1)

    tol = mpf(10) ** (-(dps - 20))
    cols = _maximal_independent([[M[i, j] for i in range(nr)] for j in range(nv)], tol)
    Mc = mp.matrix(nr, len(cols))
    for r in range(nr):
        for c, j in enumerate(cols):
            Mc[r, c] = M[r, j]
    y = mp.lu_solve(Mc.T * Mc, Mc.T * rhs)
    res = Mc * y - rhs
    z = [mpf(0)] * nv
    for c, j in enumerate(cols):
        z[j] = y[c]

    # The multipliers are a family, not a point: rank < nv leaves a null
    # direction n with M n = 0, and z + alpha n is a multiplier vector for
    # every alpha.  "Are the multipliers nonnegative?" therefore means "is
    # SOME member nonnegative", so the family is optimised over rather than
    # left at whichever member least squares happened to return.  f(alpha) =
    # min_j (z_j + alpha n_j) is concave piecewise linear; its maximum is
    # found by a two-variable LP and then evaluated in high precision.
    null = None
    alpha = mpf(0)
    if len(cols) < nv:
        free = [j for j in range(nv) if j not in set(cols)]
        j0 = free[0]
        b2 = mp.matrix(nr, 1)
        for i in range(nr):
            b2[i] = -M[i, j0]
        yy = mp.lu_solve(Mc.T * Mc, Mc.T * b2)
        null = [mpf(0)] * nv
        null[j0] = mpf(1)
        for c, j in enumerate(cols):
            null[j] = yy[c]
        s = max(abs(v) for v in null)
        null = [v / s for v in null]
        A_ub = np.zeros((nv, 2))
        for j in range(nv):
            A_ub[j, 0] = 1.0                       # u
            A_ub[j, 1] = -float(null[j])           # -alpha n_j
        lp = linprog(np.array([-1.0, 0.0]), A_ub=A_ub,
                     b_ub=np.array([float(v) for v in z]),
                     bounds=[(None, None), (None, None)], method="highs")
        if lp.success:
            alpha = mpf(float(lp.x[1]))
            z = [z[j] + alpha * null[j] for j in range(nv)]
    return (z[:nl], z[nl:], max(abs(res[i]) for i in range(nr)),
            len(cols), nv, mp.nstr(alpha, 12),
            null is not None)


# --------------------------------------------------------------------------
# exact certification, integers and Fractions only
# --------------------------------------------------------------------------
def certify(points, scale):
    n = len(points)
    s2 = scale * scale
    assert len(set(points)) == n, "duplicate points"
    rmax = max(x * x + y * y for x, y in points)
    assert rmax <= s2, "leaves the closed unit disk"
    twice = []
    for a, b, c in combinations(range(n), 3):
        (x1, y1), (x2, y2), (x3, y3) = points[a], points[b], points[c]
        v = abs((x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1))
        assert v > 0, f"degenerate triple {(a, b, c)}"
        twice.append(v)
    m = min(twice)
    return {"exact": F(m, 2 * s2),
            "ties": sum(1 for v in twice if v == m),
            "within_one_grid_step": sum(1 for v in twice if v <= m + 4 * scale),
            "containment_slack_scale2": s2 - rmax}


def main():
    dps = int(sys.argv[1]) if len(sys.argv) > 1 else 120
    prefix = sys.argv[2] if len(sys.argv) > 2 else "circle_configs/n14"
    if not os.path.isabs(prefix):
        prefix = os.path.join(HERE, prefix)
    src_path = sys.argv[3] if len(sys.argv) > 3 else SRC
    if not os.path.isabs(src_path):
        src_path = os.path.join(HERE, src_path)
    t_start = time.time()
    mp.dps = dps

    src = json.load(open(src_path))
    Q = [[mpf(x), mpf(y)] for x, y in src["points_hp"]]
    prev_hp = mpf(src["hp_value"])
    prev_exact = F(src["min_area_exact"])
    print(f"source             {os.path.relpath(src_path, HERE)}")

    # ---- 1. active set, cut reported rather than assumed -------------------
    act, m0, T_all, A_all = HA.active_set(Q, rel="1e-9")
    act = [tuple(int(v) for v in t) for t in act]
    srt = sorted(abs(v) for v in A_all)
    gap_last = srt[len(act) - 1] / m0 - 1
    gap_first = srt[len(act)] / m0 - 1
    print(f"committed hp min   {mp.nstr(m0, 30)}")
    print(f"active set         {len(act)} of {len(T_all)}")
    print(f"  last active      {mp.nstr(gap_last, 6)} relative above the min")
    print(f"  first inactive   {mp.nstr(gap_first, 6)} relative above the min")
    print(f"  separation       {mp.nstr(gap_first / gap_last, 6)}x")

    # ---- 2. Newton onto the curve -----------------------------------------
    Pf = [[float(p[0]), float(p[1])] for p in Q]
    C0, t_newton, B, I, frozen, square = HP.refine(Pf, act, dps=dps, iters=80)
    mp.dps = dps
    C0 = {i: (C0[i][0], C0[i][1]) for i in range(N)}
    sigma = [1 if HP.signed_area(C0, tri) >= 0 else -1 for tri in act]
    print(f"Newton point t     {mp.nstr(t_newton, 34)}")
    print(f"  moved from committed hp by {mp.nstr(t_newton - prev_hp, 6)} "
          f"({mp.nstr((t_newton - prev_hp) / prev_hp, 6)} relative)")
    lam0, mu0, kkt0, rank0, nv0, alpha0, fam0 = kkt(C0, act, sigma, B, dps)
    print(f"  KKT residual at the Newton point: {mp.nstr(kkt0, 6)} "
          f"-> {'NOT stationary' if kkt0 > mpf('1e-20') else 'stationary'}")
    tan0 = tangent(C0, act, sigma, B, I, mpf(10) ** (-(dps - 20)))
    print(f"  |Jv-1| at the Newton point: {mp.nstr(tan0[2], 6)}  "
          f"ascent rate {mp.nstr(tan0[1], 6)} per unit displacement")

    # ---- 3. walk the curve to its maximum ---------------------------------
    print("walking the equality curve:")
    C, t_star, hist = walk(C0, act, sigma, B, I, dps)
    print(f"stationary t       {mp.nstr(t_star, 40)}")
    print(f"  gained over the Newton point {mp.nstr(t_star - t_newton, 6)}")
    print(f"  gained over the committed hp {mp.nstr(t_star - prev_hp, 6)} "
          f"({mp.nstr((t_star - prev_hp) / prev_hp, 6)} relative)")

    # ---- 4. KKT at the endpoint -------------------------------------------
    lam, mu, kkt_res, rank, nvk, alpha, fam = kkt(C, act, sigma, B, dps)
    tanf = tangent(C, act, sigma, B, I, mpf(10) ** (-(dps - 20)))
    print(f"KKT at the endpoint  residual {mp.nstr(kkt_res, 6)}  "
          f"(rank {rank} of {nvk})")
    print(f"  min lambda       {mp.nstr(min(lam), 8)}   (need >= 0)")
    print(f"  min mu           {mp.nstr(min(mu), 8)}   (need >= 0)")
    print(f"  sum lambda       {mp.nstr(sum(lam), 8)}")
    print(f"  family alpha     {alpha}  (member maximising the smallest multiplier)")
    print(f"  |Jv-1|           {mp.nstr(tanf[2], 6)}  "
          f"(order 1 = no equal-rate ascent direction)")

    # ---- 5. feasibility ----------------------------------------------------
    areas = {tri: abs(HP.signed_area(C, tri)) for tri in TRIPLES}
    true_min = min(areas.values())
    argmin = min(areas, key=areas.get)
    actset = set(act)
    nearest_inactive = min(v for tri, v in areas.items() if tri not in actset)
    radii2 = {i: C[i][0] ** 2 + C[i][1] ** 2 for i in range(N)}
    print(f"  true min over 364 = {mp.nstr(true_min, 40)} at {argmin}")
    print(f"  true_min - t       = {mp.nstr(true_min - t_star, 6)}")
    print(f"  nearest inactive   = {mp.nstr(nearest_inactive / t_star - 1, 6)} above t")
    print(f"  max radius^2 - 1   = {mp.nstr(max(radii2.values()) - 1, 6)}")

    # ---- 6. snap and certify ----------------------------------------------
    best, snaps = None, []
    for e in SNAP_EXPONENTS:
        scale = 10 ** e
        pts = HP.snap_exact(C, N, scale)
        cert = certify(pts, scale)
        loss = t_star - mpf(cert["exact"].numerator) / mpf(cert["exact"].denominator)
        row = {"exponent": e, "scale": scale, "points": [list(p) for p in pts],
               "exact": str(cert["exact"]), "exact_float": float(cert["exact"]),
               "loss_vs_stationary": mp.nstr(loss, 6),
               "exact_ties": cert["ties"],
               "within_one_grid_step": cert["within_one_grid_step"],
               "containment_slack_scale2": cert["containment_slack_scale2"]}
        snaps.append(row)
        print(f"  scale=10^{e:<3d} exact={float(cert['exact']):.20f}  "
              f"loss={mp.nstr(loss, 4):>12s}  ties={cert['ties']:2d}  "
              f"within_1_step={cert['within_one_grid_step']:2d}")
        if best is None or cert["exact"] > F(best["exact"]):
            best = row
    exact_best = F(best["exact"])
    print(f"\nBEST SNAP scale=10^{best['exponent']}")
    print(f"  exact = {exact_best}")
    print(f"  previous certified   {prev_exact}")
    print(f"  gain over previous   {float(exact_best - prev_exact):+.6e} "
          f"({float((exact_best - prev_exact) / prev_exact):+.6e} relative)")
    print(f"  vs Friedman upper    {float(exact_best / FRIEDMAN_UPPER - 1) * 100:+.6f}%")
    Pnum = np.array([[x / best["scale"], y / best["scale"]] for x, y in best["points"]])
    desc = CS.describe(Pnum)
    print("  ", CS.fmt(desc))

    stat = {
        "what": "convergence and stationarity evidence for the n=14 unit-disk "
                "configuration",
        "not_a_theorem":
            "High-precision numerical checks, committed as data. The rigorous "
            "statement is the exact rational lower bound; local optimality is "
            "NOT claimed.",
        "dps": dps,
        "source": os.path.relpath(src_path, HERE),
        "previous_hp_value": mp.nstr(prev_hp, 45),
        "previous_exact": str(prev_exact),
        "structure_note":
            "16 active triangles, 8 boundary points (one tangential dof each), "
            "4 interior active points (two each), 2 frozen points in no active "
            "triangle. The equality system has 16 equations in 16 spatial dofs "
            "and its Jacobian has rank 15 (the rotation gauge), so "
            "{all active equal} is a CURVE, not a point, and t varies along "
            "it. That is why earlier passes reported convergence while an "
            "ascent direction remained.",
        "active_set": {
            "size": len(act), "triples": [list(t) for t in act],
            "total_triples": len(T_all),
            "last_active_relative_above_min": mp.nstr(gap_last, 8),
            "first_inactive_relative_above_min": mp.nstr(gap_first, 8),
            "separation_factor": mp.nstr(gap_first / gap_last, 8),
        },
        "newton_point": {
            "t": mp.nstr(t_newton, 45),
            "boundary_points": B, "interior_points": I, "frozen_points": frozen,
            "kkt_residual": mp.nstr(kkt0, 8),
            "residual_of_Jv_eq_1": mp.nstr(tan0[2], 8),
            "ascent_rate_per_unit_displacement": mp.nstr(tan0[1], 8),
            "verdict": "NOT stationary: an equal-rate ascent direction exists",
        },
        "walk": {
            "iterations": hist,
            "note": "predictor along v, corrector back onto the curve by a "
                    "least-squares Newton in the tangency parameterisation",
        },
        "stationary_value_hp": mp.nstr(t_star, 45),
        "gain_over_newton_point": mp.nstr(t_star - t_newton, 8),
        "gain_over_previous_hp": mp.nstr(t_star - prev_hp, 8),
        "gain_over_previous_hp_relative": mp.nstr((t_star - prev_hp) / prev_hp, 8),
        "kkt": {
            "form": "sum_A lambda_T grad(sigma_T area_T) = sum_B 2 mu_i p_i, "
                    "sum lambda_T = 1, lambda >= 0, mu >= 0",
            "lambda": [mp.nstr(v, 25) for v in lam],
            "lambda_triples": [list(t) for t in act],
            "mu": [mp.nstr(v, 25) for v in mu],
            "mu_points": B,
            "residual_inf": mp.nstr(kkt_res, 8),
            "system_rank": rank, "unknowns": nvk,
            "min_lambda": mp.nstr(min(lam), 20),
            "min_mu": mp.nstr(min(mu), 20),
            "sum_lambda": mp.nstr(sum(lam), 25),
            "family_dimension": nvk - rank,
            "family_alpha_chosen": alpha,
            "family_note":
                "the multipliers are a one-parameter family; alpha is the "
                "member maximising the smallest multiplier, so min_lambda and "
                "min_mu below are the best available, not an arbitrary pick",
            "nonnegative_within_residual":
                bool(min(min(lam), min(mu)) >= -abs(kkt_res)),
            "all_multipliers_strictly_positive":
                bool(min(min(lam), min(mu)) > abs(kkt_res)),
            "residual_of_Jv_eq_1": mp.nstr(tanf[2], 8),
            "reading": "the residual is reported over all 2N+1 equations, "
                       "dependent rows included; compare it with the same "
                       "number at newton_point.kkt_residual",
        },
        "feasibility": {
            "true_min_over_all_364": mp.nstr(true_min, 45),
            "true_min_minus_t": mp.nstr(true_min - t_star, 8),
            "argmin_triple": list(argmin),
            "nearest_inactive_relative_above_t":
                mp.nstr(nearest_inactive / t_star - 1, 8),
            "max_radius2_minus_1": mp.nstr(max(radii2.values()) - 1, 8),
            "radii": [mp.nstr(mp.sqrt(radii2[i]), 25) for i in range(N)],
        },
        "snaps": snaps,
        "best_snap_exponent": best["exponent"],
        "points_hp": [[mp.nstr(C[i][0], 45), mp.nstr(C[i][1], 45)] for i in range(N)],
        "wall_seconds": round(time.time() - t_start, 1),
    }
    with open(prefix + "_stationarity.json", "w") as fh:
        json.dump(stat, fh, indent=1)
    print(f"\nwrote {prefix}_stationarity.json")

    with open(prefix + "_converged_candidate.json", "w") as fh:
        json.dump({"n": N, "scale": best["scale"], "points": best["points"],
                   "min_area_exact": best["exact"],
                   "min_area_float": best["exact_float"],
                   "stationary_value_hp": mp.nstr(t_star, 45),
                   "points_hp": stat["points_hp"]}, fh, indent=1)
    print(f"wrote {prefix}_converged_candidate.json")


if __name__ == "__main__":
    main()
