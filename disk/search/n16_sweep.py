"""Resumable deep unrestricted sweep at one n.

The census run died mid-campaign and this host is shared, so the sweep is
chunked and check-pointed: every chunk of restarts writes its running best, the
cumulative restart count and the wall time back to `n16_sweep_state.json`, and
re-invoking the script continues from the next seed block.  A killed chunk
costs one chunk, not the campaign.

Usage: python3 n16_sweep.py <n> <chunk_restarts> <iters> <threads> <budget_sec>
"""
import json
import os
import subprocess
import sys
import time
from multiprocessing import Pool

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import circle_attack as ca              # noqa: E402
import circle_lp_polish as L            # noqa: E402
import circle_symmetry as CS            # noqa: E402

BIN = os.path.join(HERE, "circle_search")


def _polish(P):
    Q, v = L.lp_polish(P)
    return v, Q.tolist()


def main():
    n = int(sys.argv[1])
    chunk = int(sys.argv[2])
    iters = int(sys.argv[3])
    threads = int(sys.argv[4])
    budget = float(sys.argv[5])
    state_path = os.path.join(HERE, f"n{n}_sweep_state.json")
    st = (json.load(open(state_path)) if os.path.exists(state_path)
          else {"n": n, "restarts_done": 0, "iters": iters, "best_float": 0.0,
                "best_points": None, "best_exact": None, "seconds": 0.0,
                "chunks": [], "hits_at_best": 0})

    t_start = time.time()
    while time.time() - t_start < budget:
        seed = 20260824 + 7919 * st["restarts_done"]
        t0 = time.time()
        out = subprocess.run([BIN, str(n), str(iters), str(chunk), str(threads),
                              str(seed), str(chunk)],
                             capture_output=True, text=True, check=True)
        cands = []
        for line in out.stdout.strip().split("\n"):
            v = [float(x) for x in line.split()]
            cands.append([(v[1 + 2 * i], v[2 + 2 * i]) for i in range(n)])
        with Pool(threads) as pool:
            polished = pool.map(_polish, cands, chunksize=4)
        polished.sort(key=lambda r: -r[0])
        dt = time.time() - t0
        st["restarts_done"] += chunk
        st["seconds"] += dt

        # per-family bookkeeping: classify every polished candidate by the
        # boundary/interior split it actually ENDS in, which is the family the
        # annealer selected rather than the one it was seeded with.
        fam = st.setdefault("by_boundary_count", {})
        for w, R in polished:
            A = np.array(R)
            k = int((np.hypot(A[:, 0], A[:, 1]) > 1 - 1e-9).sum())
            cur = fam.get(str(k))
            if cur is None or w > cur["best"]:
                fam[str(k)] = {"best": w, "points": R, "count": 1}
            else:
                cur["count"] += 1

        v, P = polished[0]
        improved = v > st["best_float"] * (1 + 1e-12)
        if improved:
            ints = ca.snap_to_disk(P)
            exact = ca.exact_minimum(ints)
            st["best_float"] = v
            st["best_points"] = P
            st["best_exact"] = str(exact)
            st["best_exact_float"] = float(exact)
        hits = sum(1 for w, _ in polished if w > st["best_float"] * (1 - 1e-9))
        st["hits_at_best"] = st.get("hits_at_best", 0) + hits
        st["chunks"].append({"restarts": chunk, "seconds": round(dt, 1),
                             "chunk_best": v, "hits": hits})
        json.dump(st, open(state_path, "w"), indent=1)
        print(f"restarts={st['restarts_done']:6d}  chunk_best={v:.12f}  "
              f"running_best={st['best_float']:.12f}  hits={hits}  "
              f"{dt:.0f}s  cum={st['seconds']:.0f}s"
              f"{'  <-- NEW BEST' if improved else ''}", flush=True)

    if st["best_points"]:
        A = np.array(st["best_points"])
        print("\nbest so far:", CS.fmt(CS.describe(A)))
        print("exact:", st["best_exact"], "=", st.get("best_exact_float"))
        print("by final boundary count:")
        for k in sorted(st.get("by_boundary_count", {}), key=int):
            e = st["by_boundary_count"][k]
            print(f"  {k:>2} on circle + {n - int(k):<2} interior  "
                  f"best={e['best']:.12f}  seen={e['count']}")


if __name__ == "__main__":
    main()
