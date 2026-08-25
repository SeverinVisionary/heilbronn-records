# Unrestricted search over Cantrell's circle table, 7 <= n <= 15

Every row attacked with the same budget that produced the n = 14 result (8192
multistart SA restarts, 600k iterations, boundary count cycled over `3..n`,
sequential-LP endgame), then snapped to a `1/10^12` grid and certified in exact
rational arithmetic. Verified independently of the producing code: containment
and distinctness in pure integer arithmetic, exact minimum over all `C(n,3)`
triples, active-triangle count, and a measured reflection defect.

Baseline is **Friedman's printed value** (unit radius), with MathWorld's
higher-precision transcription shown where it exists — noting MathWorld is
[erroneous at n = 11](PRIOR_ART_CIRCLE_2026-08-23.md).

| n | ours (exact) | Cantrell | Friedman | ratio | bdry+int | refl. defect | verdict |
|---|---|---|---|---|---|---|---|
| 7 | 0.294367526377 | 0.294367232 | `.294+` | 1.000001 | 7+0 | 5.3e-04 | matches |
| 8 | 0.216941869558 | 0.216942681 | `.216+` | 0.999996 | 7+1 | 1.7e-04 | matches |
| 9 | 0.173763752508 | 0.173763748 | `.173+` | 1.000000 | 6+3 | 2.9e-03 | matches |
| 10 | 0.150383733180 | 0.150383732 | `.150+` | 1.000000 | 9+1 | 7.1e-03 | matches |
| 11 | 0.113938117431 | **.113+** | `.113+` | 1.000000 | 8+3 | 1.3e-03 | matches (rediscovery) |
| 12 | 0.104915382840 | 0.104915383 | `.104+` | 1.000000 | 9+3 | 3.8e-03 | matches |
| 13 | 0.085689772657 | 0.085658236 | `.0856+` | 1.000368 | 6+7 | 2.1e-01 | +0.037%, below bar |
| **14** | **0.076715885771** | 0.075857251 | `.0758+` | **1.011319** | 8+6 | 3.0e-02 | **BEATS, +1.13%** |
| 15 | 0.070039522128 | 0.070039522 | `.0700+` | 1.000000 | 6+9 | 2.4e-03 | matches |
| 16 | 0.066134764311 | `.0661+` | `.0661+` | 1.000017 | 8+8 | 0.0e+00 | matches |

**The gap at n = 16 is now closed** (2026-08-24, [CIRCLE_N16](CIRCLE_N16_2026-08-24.md)),
and it closes the way the table above predicts: it MATCHES. The row needed a
different method, though — unrestricted multistart reaches only `0.0598` there,
9.5% low, so the value was obtained by constructing Cantrell's annotated
symmetry class (D_4) directly, which finds it in 120 seeds. Three independent
tests (every boundary split k = 8..16, asymmetric kicks at eight sigmas, and
relaxing each subgroup from the D_4 optimum itself) all say asymmetry buys
nothing at n = 16. The reflection defect of `0.0e+00` in the row above is the
symmetry-constrained optimum; a free high-precision ascent from it drifts to
`3.0e-06` and gains `5e-14`.

## The symmetry hypothesis is mostly disconfirmed

After n = 14 we conjectured that Cantrell's whole table came from a symmetry
ansatz, making every row a candidate. **The census does not support that.**
Unrestricted search **reproduces** Cantrell at 7 of the 9 rows tested — n = 7, 8,
9, 10, 11, 12, 15 all land on his value to 6-9 significant figures. His table is
good. Where our search agrees, it agrees to the digits he published.

What survives of the idea is narrower and still real: **the only two rows we
exceed are exactly the two whose winners are asymmetric.** Reflection defect is
`~1e-3` or smaller at every matching row (i.e. our search independently
rediscovers a symmetric configuration, consistent with Friedman's per-row
symmetry annotations), but `3.0e-02` at n = 14 and `2.1e-01` at n = 13. So the
symmetry restriction does cost something — it just costs it at two rows out of
nine, not everywhere.

**n = 14 is an isolated miss in an otherwise strong table, not the first crack in
a systematically weak one.** That is a smaller claim than the one made when
n = 14 first landed, and it is the one the evidence supports.

## Every row is snap-limited; n = 14 is the one that has since been converged

All nine configurations have **exactly one** active triangle. That was first
recorded here as an artifact of the final snap breaking ties the pre-snap
configuration held. A later revision said polishing n = 14 had shown that
diagnosis wrong — that the 16 active triangles spanned `8.5e-14` relative at the
optimum, so a single exact tie was *intrinsic*. **That revision was itself
wrong, and it is now retracted.** The `8.5e-14` spread was not a property of the
optimum; it was the distance the configuration still had to travel.

Driving n = 14 to a stationary candidate (2026-08-24) closes it: at the
stationary point the 16 active triangles agree to `1.4e-44` relative, and the
single exact tie after snapping is exactly what the original diagnosis said —
**a property of the grid, not of the configuration.** The reason every earlier
pass stopped short is structural and is written up in
[CIRCLE_N14](CIRCLE_N14_2026-08-23.md#convergence-why-we-stopped): the set
`{all active triangles equal}` is a *curve*, not a point, so a Newton solve
lands on it and reports a tiny residual while an ascent direction survives.

The practical consequence is small. Converging n = 14 moved its value by
`2.2e-14` relative — the 15th significant digit — and changed no verdict in the
table above. The other eight rows have **not** been put through the same walk,
so they remain certified floors at snap-limited points, and the same `~1e-12`
snap cost applies to them. Whether any of them would move more than n = 14 did
is untested.
