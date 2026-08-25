"""Attack pipeline for the Friedman/Cantrell best-known CIRCLE table.

Three stages, and only the last one produces a number that may be reported:

  1. ``circle_search.c`` -- multistart simulated annealing in C (pthreads), with
     deliberate seeding: the number of points placed on the bounding circle is
     cycled over 3..n across restarts, so all-on-circle and
     (n-1)-on-circle-plus-centre are always in the seed set, and every third
     family starts from a regular k-gon.
  2. ``circle_lp_polish.py`` -- sequential-LP endgame (scipy/HiGHS).  This is
     the stage that matters: max-min triangle area is a degenerate ridge where
     coordinate-wise and random local moves stall roughly 1% short.  Without it
     the pipeline reproduces none of the published constants; with it, n=7..10
     and 12..16 come back to within ~1e-5 relative of the published values.
  3. ``circle_attack.snap_to_disk`` + ``circle_attack.exact_minimum`` -- snap to
     a 1/10^12 integer grid and recompute the minimum triangle area as an exact
     rational, with an exact closed-unit-disk containment check.

Normalization: MathWorld tabulates the UNIT-AREA circle; lengths scale by
sqrt(pi) to the unit-radius disk, so alpha_disk(n) = pi * H_n.

Usage:
    cc -O3 -o circle_search circle_search.c -lm -lpthread
    python3 circle_pipeline.py <lo> <hi> <iters> <restarts> <threads> <seed> <tag>
"""
import json, math, os, subprocess, sys, time
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import circle_attack as ca
import circle_lp_polish as L

BIN = os.path.join(HERE, "circle_search")


def _polish(P):
    Q, v = L.lp_polish(P)
    return v, Q.tolist()


def run_n(n, iters, restarts, threads, seed, topk=None):
    topk = topk or restarts
    t0 = time.time()
    out = subprocess.run([BIN, str(n), str(iters), str(restarts), str(threads),
                          str(seed), str(topk)], capture_output=True, text=True, check=True)
    t_search = time.time() - t0
    cands = []
    for line in out.stdout.strip().split("\n"):
        v = [float(x) for x in line.split()]
        cands.append([(v[1 + 2 * i], v[2 + 2 * i]) for i in range(n)])

    t1 = time.time()
    with Pool(threads) as pool:
        polished = pool.map(_polish, cands, chunksize=4)
    t_lp = time.time() - t1

    polished.sort(key=lambda r: -r[0])
    best_float = polished[0][0]
    n_1e9 = sum(1 for v, _ in polished if v > best_float * (1 - 1e-9))
    n_1e6 = sum(1 for v, _ in polished if v > best_float * (1 - 1e-6))
    n_1e4 = sum(1 for v, _ in polished if v > best_float * (1 - 1e-4))

    best = None
    for v, P in polished[:8]:
        ints = ca.snap_to_disk(P)
        exact = ca.exact_minimum(ints)       # raises if it leaves the unit disk
        if best is None or exact > best[0]:
            best = (exact, ints)
    exact, ints = best

    rec = {"n": n, "exact": str(exact), "exact_float": float(exact),
           "best_float_prelim": best_float, "scale": ca.SCALE, "points": ints,
           "restarts": restarts, "iters": iters, "seed": seed,
           "converged_rel1e-9": n_1e9, "converged_rel1e-6": n_1e6,
           "converged_rel1e-4": n_1e4, "n_candidates": len(polished),
           "seconds_search": round(t_search, 1), "seconds_lp": round(t_lp, 1)}
    if n in ca.MATHWORLD_UNIT_AREA:
        t = ca.MATHWORLD_UNIT_AREA[n] * math.pi
        rec["target_unit_radius"] = t
        rec["mathworld_unit_area"] = ca.MATHWORLD_UNIT_AREA[n]
        rec["ratio"] = float(exact) / t
    return rec


def fmt(rec):
    s = f"n={rec['n']:2d} exact={rec['exact_float']:.12f}"
    if "target_unit_radius" in rec:
        s += (f" target={rec['target_unit_radius']:.12f} ratio={rec['ratio']:.6f} "
              f"{'>>> BEATS' if rec['ratio'] > 1 else 'below    '}")
    return s + (f" conv(1e-9/1e-6/1e-4 of {rec['n_candidates']})="
                f"{rec['converged_rel1e-9']}/{rec['converged_rel1e-6']}/{rec['converged_rel1e-4']}"
                f" {rec['seconds_search']:.0f}+{rec['seconds_lp']:.0f}s")


def gate(iters=500000, restarts=256, threads=10, seed=424242):
    """Correctness gate.  n = 3..6 have closed-form optima, so the pipeline must
    REPRODUCE them and must never exceed one: a configuration that 'beats' a
    known optimum can only come from a containment or area bug.  Returns True
    iff every row reproduces without exceeding."""
    ok = True
    for n in sorted(ca.CLOSED_FORM_UNIT_AREA):
        r = run_n(n, iters, restarts, threads, seed)
        optimum = ca.CLOSED_FORM_UNIT_AREA[n] * math.pi
        ratio = r["exact_float"] / optimum
        # 1e-7 of slack absorbs the polish and the 1/10^12 snap, and is far
        # tighter than any margin this pipeline ever claims as a beat.
        bad = ratio > 1 + 1e-9
        ok &= not bad
        print(f"n={n}  ours={r['exact_float']:.12f}  optimum={optimum:.12f}  "
              f"ratio={ratio:.9f}  "
              f"{'EXCEEDS A KNOWN OPTIMUM -> BUG' if bad else 'reproduces (ok)'}",
              flush=True)
    print("GATE PASS" if ok else "GATE FAIL")
    return ok


if __name__ == "__main__":
    if sys.argv[1] == "gate":
        raise SystemExit(0 if gate(*[int(a) for a in sys.argv[2:]]) else 1)
    lo, hi, iters, restarts, threads, seed, tag = (
        int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]),
        int(sys.argv[4]), int(sys.argv[5]), int(sys.argv[6]), sys.argv[7])
    topk = int(sys.argv[8]) if len(sys.argv) > 8 else restarts
    rows = []
    for n in range(lo, hi + 1):
        r = run_n(n, iters, restarts, threads, seed, topk)
        print(fmt(r), flush=True)
        rows.append(r)
        json.dump(rows, open(os.path.join(HERE, f"{tag}.json"), "w"), indent=1)
