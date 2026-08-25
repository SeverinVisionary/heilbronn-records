"""Absorb one chunk of `circle_search` output into a resumable sweep state.

Why this is split out of the driver: on macOS a child launched through Python's
`subprocess` inherits a background QoS and runs ~15x slower than the identical
command launched directly by the shell (measured here: 6.8 s vs > 110 s for the
same 64 restarts).  So the annealer is launched by the shell and only the
LP-polish/certify half runs in Python, which is unaffected because it uses a
multiprocessing Pool rather than an exec'd child.

Usage: python3 absorb_chunk.py <n> <chunk_file> <threads> [state_file]
"""
import json
import os
import sys
from multiprocessing import Pool

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import circle_attack as ca            # noqa: E402
import circle_lp_polish as L          # noqa: E402
import circle_symmetry as CS          # noqa: E402


def main():
    n = int(sys.argv[1])
    chunk_file = sys.argv[2]
    threads = int(sys.argv[3])
    state_path = os.path.join(HERE, sys.argv[4] if len(sys.argv) > 4
                              else f"n{n}_sweep_state.json")
    st = (json.load(open(state_path)) if os.path.exists(state_path)
          else {"n": n, "restarts_done": 0, "best_float": 0.0,
                "best_points": None, "best_exact": None, "chunks": [],
                "by_boundary_count": {}})

    cands = []
    for line in open(os.path.join(HERE, chunk_file)):
        v = [float(x) for x in line.split()]
        if len(v) != 2 * n + 1:
            continue
        cands.append([(v[1 + 2 * i], v[2 + 2 * i]) for i in range(n)])
    if not cands:
        print("empty chunk")
        return
    with Pool(threads) as pool:
        polished = pool.map(L.lp_polish, cands, chunksize=2)
    polished = [(v, np.asarray(Q)) for Q, v in polished]
    polished.sort(key=lambda r: -r[0])

    fam = st.setdefault("by_boundary_count", {})
    for w, R in polished:
        k = str(int((np.hypot(R[:, 0], R[:, 1]) > 1 - 1e-9).sum()))
        cur = fam.get(k)
        if cur is None or w > cur["best"]:
            fam[k] = {"best": w, "points": R.tolist(),
                      "count": (cur["count"] + 1) if cur else 1}
        else:
            cur["count"] += 1

    st["restarts_done"] += len(cands)
    v, P = polished[0]
    improved = v > st["best_float"] * (1 + 1e-12)
    if improved:
        ints = ca.snap_to_disk(P.tolist())
        exact = ca.exact_minimum(ints)
        st["best_float"] = v
        st["best_points"] = P.tolist()
        st["best_exact"] = str(exact)
        st["best_exact_float"] = float(exact)
        st["best_points_int"] = ints
    hits = sum(1 for w, _ in polished if w > st["best_float"] * (1 - 1e-9))
    st["chunks"].append({"restarts": len(cands), "chunk_best": v, "hits": hits})
    json.dump(st, open(state_path, "w"), indent=1)
    print(f"restarts={st['restarts_done']:6d}  chunk_best={v:.12f}  "
          f"running_best={st['best_float']:.12f}  hits_at_best={hits}"
          f"{'   <-- NEW BEST' if improved else ''}")
    if st["best_points"]:
        print("  best:", CS.fmt(CS.describe(np.array(st["best_points"]))))
    print("  by final boundary count: " + "  ".join(
        f"{k}+{n - int(k)}:{fam[k]['best']:.9f}" for k in sorted(fam, key=int)))


if __name__ == "__main__":
    main()
