"""Recorded, replayable reproduction study of the n = 14 unit-disk construction.

Answers one question and only that question: *how hard is the record basin to
find?*  The bound itself is not at issue here -- it is checkable from the
integers in ``circle_configs/circle_n14_converged.json`` alone.

What earlier revisions lacked was provenance: reproduction counts were quoted
("7 independent restarts", "23 of 8192") with no committed artifact and with the
raw candidate dumps gitignored, and one row's budget metadata was byte-identical
to another's.  This script replaces all of that with a run whose every restart
is addressable by an explicitly recorded seed.

Seed model (read out of ``circle_search.c``, not copied from any config):
    restart ``r`` of an invocation with base ``S`` uses RNG seed
    ``S + 1000003 * r`` and initial family ``k = 3 + (r mod (n-2))`` boundary
    points, ``fam = r div (n-2)`` (``fam % 3 == 0`` starts from a regular
    k-gon; ``fam % 2 == 0`` with a single interior point starts it at the
    centre).

The study runs in chunks so a long job checkpoints and cannot be lost.  Chunk
``j`` is invoked with base ``seed_base + 1000003 * j * chunk``, so the global
seed set is exactly ``{seed_base + 1000003 * g : g = 0 .. restarts-1}`` -- the
same set an un-chunked run of the same length would use.  What chunking *does*
change is the seeding family, which cycles on the within-chunk index ``r``, not
on the global index ``g``; both are recorded per restart.

Pipeline per restart, unchanged from ``circle_pipeline.run_n``:
    circle_search SA + pattern search + (1+1)-ES   [double, C]
        -> circle_lp_polish.lp_polish              [double, HiGHS]
        -> snap to a 1/scale integer grid, exact rational minimum with an
           exact closed-disk containment check     [Fraction]

Floating point proposes; every value reported for a *configuration* is
re-derived as an exact rational from integer-scaled coordinates.

Usage:
    cc -O3 -o circle_search circle_search.c -lm -lpthread
    python3 n14_reproduction.py <restarts> <chunk> <iters> <threads> \\
                                <seed_base> <out.json> [snap_scale]
Re-running with the same arguments resumes from ``<out.json>.partial``.
"""
from __future__ import annotations

import json
import math
import os
import resource
import subprocess
import sys
import time
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import circle_attack as ca          # noqa: E402
import circle_lp_polish as L        # noqa: E402
import circle_symmetry as CS        # noqa: E402

BIN = os.path.join(HERE, "circle_search")
N = 14
SEED_STEP = 1000003                 # circle_search.c: seed_base + 1000003 * r

# The two landmarks this study classifies against.  RECORD is the committed
# construction; CANTRELL is the published row (D. Cantrell 2007 via Friedman),
# transported to the unit-radius disk as alpha = pi * H.
RECORD = 0.0767158857710272457569510867362245565
CANTRELL = ca.MATHWORLD_UNIT_AREA[N] * math.pi        # 0.07585725106090124

# Two polished configurations are called the same basin when their values agree
# to this relative tolerance.  lp_polish accepts a step only when the true
# minimum improves by a relative 1e-15, so a converged run pins its ridge to
# double round-off; 1e-9 is six orders looser than that and still far tighter
# than the 1.4e-2 relative gap between the record and Cantrell.  Coarser
# tolerances are also reported, because at n = 14 the count of distinct values
# is itself the headline fact about the landscape.
BASIN_REL = 1e-9
BASIN_RELS = (1e-9, 1e-7, 1e-5, 1e-3)


def _polish(job):
    gid, rid, chunk_id, seed, pre, P = job
    Q, v = L.lp_polish(P)
    return {"restart": gid, "chunk": chunk_id, "restart_in_chunk": rid,
            "seed": seed, "pre_lp": pre, "post_lp": v, "points": Q.tolist()}


def run_chunk(chunk_id, chunk, iters, threads, seed_base):
    """Run one chunk of restarts and LP-polish every candidate."""
    base = seed_base + SEED_STEP * chunk_id * chunk
    t0 = time.time()
    out = subprocess.run([BIN, str(N), str(iters), str(chunk), str(threads),
                          str(base), str(chunk)],
                         capture_output=True, text=True, check=True)
    t_search = time.time() - t0

    jobs = []
    for line in out.stdout.strip().split("\n"):
        v = [float(x) for x in line.split()]
        if len(v) != 1 + 2 * N + 2:
            raise SystemExit("circle_search did not emit the provenance fields; "
                             "rebuild it from the committed circle_search.c")
        rid, seed = int(v[-2]), int(v[-1])
        if seed != base + SEED_STEP * rid:
            raise SystemExit(f"seed mismatch at restart {rid}: {seed}")
        P = [(v[1 + 2 * i], v[2 + 2 * i]) for i in range(N)]
        jobs.append((chunk_id * chunk + rid, rid, chunk_id, seed, v[0], P))
    if len(jobs) != chunk:
        raise SystemExit(f"expected {chunk} restarts, got {len(jobs)}")
    if len({j[1] for j in jobs}) != chunk:
        raise SystemExit("restart indices are not distinct")

    t1 = time.time()
    with Pool(threads) as pool:
        rows = pool.map(_polish, jobs, chunksize=4)
    return rows, t_search, time.time() - t1, out.stderr.strip()


def exact_of(points, scale):
    """Re-derive the minimum as an exact rational, with exact containment."""
    ints = ca.snap_to_disk(points, scale=scale)
    exact = ca.exact_minimum(ints, scale=scale)   # raises if it leaves the disk
    rmax = max(x * x + y * y for x, y in ints)
    assert rmax <= scale * scale, "snapped configuration leaves the closed disk"
    return ints, exact, scale * scale - rmax


def cluster(rows, rel):
    """Group polished values into basins by relative tolerance, richest first.

    Scanning in descending order, a value can only join the most recently
    opened basin: basin values decrease, so if v were within a relative `rel`
    of an earlier basin it would be within `rel` of the latest one too, which
    sits between them.  That makes the grouping O(n) rather than O(n * basins).
    """
    basins = []
    for r in sorted(rows, key=lambda r: -r["post_lp"]):
        if basins and abs(r["post_lp"] - basins[-1]["value"]) \
                <= basins[-1]["value"] * rel:
            basins[-1]["members"].append(r)
        else:
            basins.append({"value": r["post_lp"], "members": [r]})
    return basins


def main():
    restarts = int(sys.argv[1])
    chunk = int(sys.argv[2])
    iters = int(sys.argv[3])
    threads = int(sys.argv[4])
    seed_base = int(sys.argv[5])
    out_path = sys.argv[6]
    scale = int(sys.argv[7]) if len(sys.argv) > 7 else ca.SCALE
    if restarts % chunk:
        raise SystemExit("restarts must be a multiple of chunk")
    nchunks = restarts // chunk
    partial = out_path + ".partial"

    rows, t_search, t_lp = [], 0.0, 0.0
    done = 0
    if os.path.exists(partial):
        st = json.load(open(partial))
        if (st["restarts"], st["chunk"], st["iters"], st["seed_base"]) == \
                (restarts, chunk, iters, seed_base):
            rows, done = st["rows"], st["chunks_done"]
            t_search, t_lp = st["t_search"], st["t_lp"]
            print(f"[resume] {done}/{nchunks} chunks, {len(rows)} restarts",
                  flush=True)

    wall0 = time.time()
    for j in range(done, nchunks):
        r, ts, tl, log = run_chunk(j, chunk, iters, threads, seed_base)
        rows += r
        t_search += ts
        t_lp += tl
        best = max(x["post_lp"] for x in rows)
        hits = sum(1 for x in rows
                   if abs(x["post_lp"] - RECORD) <= RECORD * BASIN_REL)
        print(f"[chunk {j + 1}/{nchunks}] {ts:.0f}s search + {tl:.0f}s lp :: "
              f"{log} :: running best {best:.12f}, record hits {hits}",
              flush=True)
        with open(partial, "w") as fh:
            json.dump({"restarts": restarts, "chunk": chunk, "iters": iters,
                       "seed_base": seed_base, "chunks_done": j + 1,
                       "t_search": t_search, "t_lp": t_lp, "rows": rows}, fh)

    rows.sort(key=lambda r: r["restart"])
    if len({r["seed"] for r in rows}) != restarts:
        raise SystemExit("the recorded seed set is not distinct")

    hit_record = [r for r in rows
                  if abs(r["post_lp"] - RECORD) <= RECORD * BASIN_REL]
    hit_cantrell = [r for r in rows
                    if abs(r["post_lp"] - CANTRELL) <= CANTRELL * BASIN_REL]
    above_cantrell = [r for r in rows if r["post_lp"] > CANTRELL]
    near_cantrell = [r for r in rows
                     if abs(r["post_lp"] - CANTRELL) <= CANTRELL * 1e-4]

    basins = cluster(rows, BASIN_REL)
    # Structure is measured for the basins actually reported: the top 200 by
    # value, plus every basin that clears 0.999 * Cantrell however deep it
    # ranks, plus every basin with more than one member (a repeatedly reached
    # local maximum is the interesting kind).
    REPORT = 200
    reported = [i for i, b in enumerate(basins)
                if i < REPORT or b["value"] > CANTRELL * (1 - 1e-3)
                or len(b["members"]) > 1]
    basin_report = []
    for rank in reported:
        b = basins[rank]
        rep = max(b["members"], key=lambda r: r["post_lp"])
        d = CS.describe(rep["points"])
        entry = {"rank": rank, "polished_value": b["value"],
                 "restarts_reaching": len(b["members"]),
                 "hit_rate": len(b["members"]) / restarts,
                 "on_circle": d["on_circle"], "interior": d["interior"],
                 "active_triangles_rel1e-9": d["active_triangles"],
                 "reflection_defect": d["reflection_defect"],
                 "best_rotation_order": d["best_rotation_order"],
                 "best_rotation_defect": d["best_rotation_defect"],
                 "measured_symmetry":
                     "symmetric" if d["symmetric"] else "asymmetric",
                 "representative_restart": rep["restart"],
                 "representative_seed": rep["seed"],
                 "member_restarts": sorted(r["restart"] for r in b["members"])[:64],
                 "ratio_to_record": b["value"] / RECORD,
                 "ratio_to_cantrell": b["value"] / CANTRELL}
        # Exact re-derivation for every basin worth looking at, so the landscape
        # table is not a table of floats.
        if rank < 40 or b["value"] > CANTRELL * (1 - 1e-3):
            ints, exact, slack = exact_of(rep["points"], scale)
            entry["exact_min_area"] = str(exact)
            entry["exact_min_area_float"] = float(exact)
            entry["exact_scale"] = scale
            entry["exact_points"] = ints
            entry["containment_slack_scale2"] = slack
        basin_report.append(entry)

    # The boundary/interior split of the landscape as a whole, over the top
    # decile of polished values -- what shapes the search actually reaches.
    top = sorted(rows, key=lambda r: -r["post_lp"])[:max(1, restarts // 10)]
    split_census = {}
    for r in top:
        d = CS.describe(r["points"])
        key = f"{d['on_circle']}+{d['interior']}"
        s = split_census.setdefault(key, {"count": 0, "best_polished": 0.0})
        s["count"] += 1
        s["best_polished"] = max(s["best_polished"], r["post_lp"])

    ru_s, ru_c = (resource.getrusage(resource.RUSAGE_SELF),
                  resource.getrusage(resource.RUSAGE_CHILDREN))
    cpu_seconds = ru_s.ru_utime + ru_s.ru_stime + ru_c.ru_utime + ru_c.ru_stime
    wall = time.time() - wall0

    vals = sorted((r["post_lp"] for r in rows), reverse=True)
    edges = [0.0, 0.050, 0.055, 0.060, 0.065, 0.070, 0.072, 0.074, 0.0755,
             0.0759, 0.0765, 0.0768]
    hist = []
    for i, lo in enumerate(edges):
        hi = edges[i + 1] if i + 1 < len(edges) else float("inf")
        hist.append({"lo": lo, "hi": None if hi == float("inf") else hi,
                     "count": sum(1 for v in vals if lo <= v < hi)})

    rec = {
        "what": "seed-recorded reproduction study of the n=14 unit-disk construction",
        "n": N,
        "record_value": RECORD,
        "record_source": "circle_configs/circle_n14_converged.json",
        "cantrell_value": CANTRELL,
        "cantrell_source":
            "pi * MathWorld H_14 (D. Cantrell 2007 via Friedman), unit-radius disk",
        "basin_relative_tolerance": BASIN_REL,
        "seed_set": {
            "seed_base": seed_base,
            "restarts": restarts,
            "chunk": chunk,
            "chunk_seed_base_formula": "seed_base + 1000003 * chunk_index * chunk",
            "restart_seed_formula":
                "seed_base + 1000003 * global_restart_index (0-based, contiguous)",
            "seed_first": seed_base,
            "seed_last": seed_base + SEED_STEP * (restarts - 1),
            "family_note":
                "the initial family cycles on the WITHIN-CHUNK index: "
                "k = 3 + (r mod 12) boundary points, fam = r div 12",
        },
        "parameters": {
            "sa_iterations_per_restart": iters,
            "threads": threads,
            "topk_lp_polished": restarts,
            "sa_initial_step": 0.10,
            "sa_step_decay": "x0.75 every iters/40, floor 1e-7",
            "sa_temperature": "0.02 * cur * (1 - it/iters)^2, floor 1e-15",
            "pattern_search_step0": 3e-3,
            "pattern_search_step_floor": 1e-14,
            "pattern_search_max_passes": 20000,
            "es_iterations": 400000,
            "es_sigma0": 1e-3,
            "lp_trust0": 1e-2,
            "lp_iters": 400,
            "lp_trust_floor": 1e-14,
            "lp_accept_relative": 1e-15,
            "snap_scale": scale,
            "parameter_source":
                "read out of circle_search.c and circle_lp_polish.py, "
                "not copied from any config's metadata",
        },
        "counts": {
            "restarts": restarts,
            "reaching_record_basin": len(hit_record),
            "reaching_cantrell_basin": len(hit_cantrell),
            "within_1e-4_of_cantrell": len(near_cantrell),
            "above_cantrell_value": len(above_cantrell),
            "record_hit_rate": len(hit_record) / restarts,
            "cantrell_hit_rate": len(hit_cantrell) / restarts,
            "distinct_basins": {f"{r:g}": len(cluster(rows, r))
                                for r in BASIN_RELS},
        },
        "record_basin_restarts": [{"restart": r["restart"], "seed": r["seed"],
                                   "pre_lp": r["pre_lp"], "post_lp": r["post_lp"]}
                                  for r in hit_record],
        "cantrell_basin_restarts": [{"restart": r["restart"], "seed": r["seed"],
                                     "pre_lp": r["pre_lp"], "post_lp": r["post_lp"]}
                                    for r in hit_cantrell],
        "top20_polished": vals[:20],
        "histogram_polished": hist,
        "boundary_interior_census_top_decile": split_census,
        "basins": basin_report,
        "basins_reported":
            "top 200 by value, plus every basin above 0.999*Cantrell, plus "
            "every basin reached by more than one restart",
        "per_restart": [{"restart": r["restart"], "chunk": r["chunk"],
                         "restart_in_chunk": r["restart_in_chunk"],
                         "seed": r["seed"], "pre_lp": r["pre_lp"],
                         "post_lp": r["post_lp"]}
                        for r in rows],
        "resources": {
            "wall_seconds": round(wall, 1),
            "search_seconds": round(t_search, 1),
            "lp_seconds": round(t_lp, 1),
            "cpu_seconds": round(cpu_seconds, 1),
            "nproc": os.cpu_count(),
            "note": "wall excludes any resumed chunks; search/lp seconds and "
                    "cpu_seconds are cumulative over the whole study",
        },
    }
    with open(out_path, "w") as fh:
        json.dump(rec, fh, indent=1)

    print(f"\nrestarts                 {restarts}  (seed base {seed_base})")
    print(f"distinct basins @1e-9    {rec['counts']['distinct_basins']['1e-09']}")
    print(f"reaching the record      {len(hit_record)}  "
          f"({100 * len(hit_record) / restarts:.4f}%)")
    print(f"reaching Cantrell 11+3   {len(hit_cantrell)}  "
          f"({100 * len(hit_cantrell) / restarts:.4f}%)")
    print(f"within 1e-4 of Cantrell  {len(near_cantrell)}")
    print(f"above Cantrell's value   {len(above_cantrell)}")
    print(f"wall {wall:.0f}s   cpu {cpu_seconds:.0f}s   nproc {os.cpu_count()}")
    print("\ntop basins (polished value, hits, split, symmetry):")
    for e in basin_report[:20]:
        print(f"  {e['polished_value']:.15f}  {e['restarts_reaching']:5d}  "
              f"{e['on_circle']}+{e['interior']}  {e['measured_symmetry']:10s}  "
              f"ratio_to_record={e['ratio_to_record']:.6f}")
    print(f"\nwrote {out_path}")


if __name__ == "__main__":
    main()
