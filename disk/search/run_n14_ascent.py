import json
import os
import sys

from mpmath import mp

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import circle_hp_ascent as HA  # noqa: E402

src = sys.argv[1] if len(sys.argv) > 1 else "circle_configs/circle_n14_converged.json"
dps = int(sys.argv[2]) if len(sys.argv) > 2 else 60
iters = int(sys.argv[3]) if len(sys.argv) > 3 else 300
trust0 = float(sys.argv[4]) if len(sys.argv) > 4 else 1e-5
out = sys.argv[5] if len(sys.argv) > 5 else "n14_hp_state.json"

rec = json.load(open(os.path.join(HERE, src)))
if "scale" in rec:
    s = rec["scale"]
    P = [(mp.mpf(x) / s, mp.mpf(y) / s) for x, y in rec["points"]]
else:
    P = [(mp.mpf(x), mp.mpf(y)) for x, y in rec["points_hp"]]

Q, v = HA.ascend(P, dps=dps, iters=iters, trust0=trust0)
print("value", mp.nstr(v, 34))
for w in ("1e-30", "1e-25", "1e-20", "1e-15", "1e-12", "1e-9"):
    a, _, _, _ = HA.active_set(Q, rel=w)
    print(f"  active@{w}: {len(a)}")
act, m, T, A = HA.active_set(Q, rel="1e-20")
print("active triples:", [tuple(t) for t in act])
r = [mp.sqrt(p[0] ** 2 + p[1] ** 2) for p in Q]
print("radii:", [mp.nstr(x, 12) for x in r])
json.dump({"points_hp": [[mp.nstr(p[0], 45), mp.nstr(p[1], 45)] for p in Q],
           "min_area_hp": mp.nstr(v, 45), "dps": dps,
           "active_1e-20": len(act)},
          open(os.path.join(HERE, out), "w"), indent=1)
print("wrote", out)
