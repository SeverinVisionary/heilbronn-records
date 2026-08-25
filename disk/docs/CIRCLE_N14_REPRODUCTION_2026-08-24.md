# n = 14: how hard is the record basin to find?

The bound is not in question here. It is checkable from the integers in
[circle_configs/circle_n14_converged.json](circle_configs/circle_n14_converged.json)
alone, and this document changes nothing about it. What it fixes is the finding
the 2026-08-24 panel left open: **the reproduction provenance was
undocumented.** Earlier revisions quoted "7 independent restarts" and "23 of
8192" with no committed artifact, the raw candidate dumps were gitignored, and
one row's budget metadata was byte-identical to `circle_n8.json`'s — so it may
simply have been copied.

Everything below is a fresh run from an explicitly recorded seed set, with the
parameters read out of the code rather than copied from any config.

## The one-sentence answer

**The record basin is hard to find but not out of reach: 9 of 16384 independent
restarts reached it, a hit rate of 0.055%, or about one restart in 1800 and
1600 CPU-seconds per hit.**

And the number the panel actually asked about: **at the historical budget of
8192 restarts this run found 6, not the "23 of 8192" an earlier revision
claimed.** That figure had no committed artifact behind it and does not survive
measurement. The bound is unaffected — it never depended on the count.


## The seed set

`circle_search.c` derives restart `r`'s RNG seed from the invocation's base `S`
as `S + 1000003 * r`, and its initial family from `r` alone: `k = 3 + (r mod 12)`
points start on the bounding circle, `fam = r div 12` selects the flavour
(`fam % 3 == 0` starts from a regular `k`-gon; `fam % 2 == 0` with a single
interior point starts that point at the centre). So the pair *(seed base,
restart count)* **is** the seed set, and any one restart replays alone.

| | |
|---|---|
| seed base | `20260824` |
| restarts | `16384`, global indices `0 … 16383` |
| restart seed | `20260824 + 1000003 * g` — first `20260824`, last `16384069471577` |
| chunking | 16 chunks of 1024; chunk `j` is invoked with base `20260824 + 1000003 * 1024 * j`, so the global seed set is exactly what one un-chunked run of 16384 would use |
| what chunking *does* change | the seeding family cycles on the within-chunk index, not the global one; both are recorded per restart |

The full list of 16384 seeds, and every restart's pre-LP and post-LP value, are
in [circle_configs/n14_reproduction.json](circle_configs/n14_reproduction.json).

## The parameters

Read out of `circle_search.c` and `circle_lp_polish.py` at run time, not copied
from another row's metadata:

| stage | parameter | value |
|---|---|---|
| SA | iterations per restart | `600000` |
| SA | initial step / decay | `0.10`, `x0.75` every `iters/40`, floor `1e-7` |
| SA | temperature | `0.02 * cur * (1 - it/iters)^2`, floor `1e-15` |
| pattern search | step0 / floor / max passes | `3e-3` / `1e-14` / `20000` |
| (1+1)-ES | iterations / sigma0 | `400000` / `1e-3` |
| LP endgame | trust0 / iters / trust floor / accept | `1e-2` / `400` / `1e-14` / relative `1e-15` |
| snap | grid | `1/10^12` for the study's exact re-derivations |

Every restart is LP-polished — `topk = restarts`, no truncation — so the
distribution below is over all 16384, not over a pre-selected top slice.

## The counts

| | count | rate |
|---|---|---|
| restarts | 16384 | |
| **reaching the record basin** (within `1e-9` relative of `0.07671588577`) | **9** | **0.0549%** |
| reaching Cantrell's 11+3 basin (`0.075857251061`) | 4 | 0.0244% |
| within `1e-4` relative of Cantrell | 29 | |
| exceeding Cantrell's value at all | 34 | 0.21% |
| distinct basins at `1e-9` / `1e-7` / `1e-5` / `1e-3` relative | 13684 / 13603 / 9369 / 453 | |

With 9 hits the Poisson uncertainty is real and worth stating: the 95% interval
on the count is roughly 3 to 15, i.e. **0.018% to 0.092%**. The rate is known to
within a factor of three, not to two significant figures.

The nine hits, replayable one at a time:

| restart | seed | pre-LP | post-LP |
|---|---|---|---|
| 714 | `734262966` | 0.069758030790 | 0.076715885770842 |
| 1113 | `1133264163` | 0.069659337707 | 0.076715885770772 |
| 1382 | `1402264970` | 0.073224926917 | 0.076715885770957 |
| 1396 | `1416265012` | 0.073023597787 | 0.076715885769205 |
| 2081 | `2101267067` | 0.072528455610 | 0.076715885770955 |
| 3509 | `3529271351` | 0.068027821938 | 0.076715885770965 |
| 10474 | `10494292246` | 0.070596667579 | 0.076715885770918 |
| 10983 | `11003293773` | 0.073854717904 | 0.076715885770581 |
| 13991 | `14011302797` | 0.073288604084 | 0.076715885771001 |

Cantrell's basin was reached by restarts 1444, 11048, 14507, 15702 (seeds
`1464265156`, `11068293968`, `14527304345`, `15722307930`), landing on
`0.07585725106…` — the published value to eleven digits, found from random
starts with no knowledge of it.

### Wall time and hardware

| | |
|---|---|
| wall | 15693 s (4 h 22 m) |
| CPU | 14596 s, of which 15425 s wall in the C search and 217 s in the LP endgame |
| `nproc` | 10 (Apple M1 Pro), 8 search threads |
| per record-basin hit | ≈ 1820 restarts, ≈ 1622 CPU-seconds |

Wall time exceeds CPU-seconds divided by threads because the machine was shared
throughout; CPU-seconds is the portable number.

## The distribution

| polished value | restarts |
|---|---|
| `< 0.0500` | 582 |
| `0.0500 – 0.0550` | 3040 |
| `0.0550 – 0.0600` | 6010 |
| `0.0600 – 0.0650` | 4804 |
| `0.0650 – 0.0700` | 1559 |
| `0.0700 – 0.0720` | 178 |
| `0.0720 – 0.0740` | 154 |
| `0.0740 – 0.0755` | 17 |
| `0.0755 – 0.0759` | 31 |
| **`0.0759 – 0.0765`** | **0** |
| **`0.0765 – 0.0768`** | **9** |

**The record sits alone across an empty gap.** Nothing at all lands between
`0.0759` and `0.0765`; the nine hits are the whole of the top bin. Whatever the
record basin is, it is not the tip of a continuum — it is separated from the
rest of the landscape by about 0.8% in value.

## The basin landscape

Top basins by polished value, with the boundary/interior split of each:

| polished value | restarts | split | symmetry | ratio to record |
|---|---|---|---|---|
| **0.076715885771001** | **9** | **8+6** | asymmetric | **1.000000** |
| 0.075861514504420 | 25 | 7+7 | asymmetric | 0.988863 |
| 0.075857251060863 | 4 | 7+7 | asymmetric | 0.988808 |
| 0.075611754610513 | 2 | 5+9 | asymmetric | 0.985608 |
| 0.074875378028049 | 16 | 6+8 | asymmetric | 0.976009 |
| 0.074438132463936 | 1 | 6+8 | **symmetric** | 0.970309 |
| 0.073808636138587 | 50 | 6+8 | asymmetric | 0.962104 |
| 0.073482842192499 | 4 | 10+4 | **symmetric** | 0.957857 |
| 0.073452820494454 | 13 | 8+6 | asymmetric | 0.957466 |
| 0.073362784822351 | 21 | 6+8 | asymmetric | 0.956292 |

Two rows deserve a second look.

**Rows 2 and 3 are not the same configuration.** `0.0758615` and `0.0758573` are
both 7+7 and differ by `5.6e-5` relative, and the lower one is Cantrell's
published value. The *higher* one is reached six times more often (25 hits vs
4). So unrestricted search finds a 7+7 configuration marginally above the
published 7+7 row, and finds it more easily than the published one — consistent
with what this campaign recorded when the lane first opened.

**The split of the record basin is not well defined**, and that is a fact about
the configuration rather than a defect in the measurement. All nine hits carry
the *same 16 active triangles*, but two of the fourteen points sit in no active
triangle at all and are free to wander: across the nine they land anywhere from
`r = 0.960` to `r = 1.000`. Eight hits therefore read as 8+6 and one — restart
10474, where a free point happened to settle exactly on the circle — reads as
9+5. The invariants of this basin are its value and its active set, not its
boundary count. This is the same non-isolation that the convergence work found
analytically (see
[CIRCLE_N14](CIRCLE_N14_2026-08-23.md#convergence-why-we-stopped)); the two
studies were run independently and agree.

The boundary/interior census over the top decile of all 16384 restarts, which
shows what shapes the search actually reaches:

| split | restarts in the top decile | best polished |
|---|---|---|
| 6+8 | 658 | 0.074875378028 |
| 5+9 | 333 | 0.075611754611 |
| 7+7 | 328 | 0.075861514504 |
| 8+6 | 140 | 0.076715885771 |
| 9+5 | 80 | 0.076715885771 |
| 12+2 | 71 | 0.066987298108 |
| 4+10 | 24 | 0.072894563018 |
| 10+4 | 4 | 0.073482842192 |


## The other route: structural family enumeration

`circle_families.py` does not sample randomly; it enumerates the families
"`b` points on the circle, `14 - b` strictly inside" for `b = 3 … 14` and
polishes each with the family constraint enforced, then again with it released.
Run at 512 seeds per family with numpy seed `20260823`
([circle_configs/n14_families.json](circle_configs/n14_families.json)):

| family | in-family best | free best | seeds at the free best |
|---|---|---|---|
| `b = 8` — **the record's own structure** | `0.052408752182` | `0.057166515439` | 1 / 512 |
| `b = 11` — Cantrell's structure | `0.074580571425` | **`0.075857251060`** | 2 / 512 |
| best over all 12 families | | `0.075857251060` (`b = 11`) | |

Two things worth stating plainly:

- **This route reproduces Cantrell's published value and not ours.** The `b = 11`
  family free-polishes to `0.075857251060`, matching `pi * H_14` to eleven
  digits. That is a strong independent check on the pipeline, and it is
  corroboration for the published row.
- **It never finds the record**, not even in the record's own `b = 8` family,
  which tops out 25% low. Structured seeding is the wrong instrument here: the
  record is asymmetric and does not sit near any regular-polygon seed. Only
  unrestricted multistart reaches it.

## How wide is the basin?

A miss rate on its own says nothing about *why*. So the basin was measured
directly, from the other end: start at the record, kick it by a known amount,
and count how often the LP endgame walks back
([circle_configs/n14_basin_probe.json](circle_configs/n14_basin_probe.json),
128 draws per sigma, numpy seed `20260824`).

Two guards run first: the committed integers re-derive to the recorded rational
with exact containment, and `lp_polish` started *at* the record returns the
record — so the centre is a genuine attractor rather than an assumed one.

| kick sigma | recovery |
|---|---|
| `1e-4` … `1e-2` | **100%** |
| `2e-2` | 99.2% |
| `3e-2` | 77.3% |
| `4e-2` | 36.7% |
| `5e-2` | 11.7% |
| `7e-2` | 1.6% |
| `>= 1e-1` | **0%** |

Recovery is judged by polished *value*, which is invariant under the disk's
rotation and reflection group and under relabelling, so this is a basin radius
modulo those symmetries.

**The endgame is not the bottleneck.** Anything within about `0.03` per
coordinate of the record lands on it, essentially always. The bottleneck is the
annealer, and the nine hits show it plainly: their pre-LP values run from
`0.0680` to `0.0739` — the same range as thousands of restarts that went
nowhere near the record. The best pre-LP value in the entire run was
`0.073855`, and it belongs to one of the nine, but restart 3509 got there from
`0.068028`, which is worse than most misses. **Pre-LP value does not predict
which basin you land in.** What matters is whether the annealer has stumbled
into the right *combinatorial arrangement*; once it has, the LP finishes the job
every time.

## Does a recorded seed actually get you the deposit?

Counting basin hits is not quite the same question as "does this seed reproduce
the committed configuration". So one hit was taken all the way through
([circle_configs/n14_reproduction_convergence.json](circle_configs/n14_reproduction_convergence.json)):

> **Restart 714, RNG seed `734262966`** — SA, LP polish, snap, active-set
> Newton, then the walk along the equality curve — lands on the **same
> stationary value to all 45 recorded digits**,
> `0.07671588577102893975178477550663424396046`, with the same 16-triangle
> active set, the same 8 boundary / 4 interior / 2 free structure, and the same
> multipliers to eight figures. Its certified rational sits `9.4e-35` from the
> committed one, which is one step of the `10^33` snap grid.

That is the check the provenance finding needed. Not "the value is right" — that
was always checkable from the integers — but *a recorded seed gets you there,
starting from nothing.*

## Two notes on how the numbers were computed

- **The basin window is `1e-9` relative**, which is four and a half orders of
  magnitude wider than the `2.2e-14` by which the 2026-08-24 convergence moved
  the deposit. Re-classifying all 16384 restarts against the old value and the
  new one gives the same 9 either way, so nothing here depends on which deposit
  is current. At the much tighter `1e-11` the count is 8.
- **The seed set was audited, not assumed.** All 16384 recorded seeds are
  distinct and every one satisfies `seed = 20260824 + 1000003 * restart`, checked
  against the values the C binary itself emitted rather than recomputed from the
  formula.


## Reproducing this

```bash
cd research/heilbronn_disk
cc -O3 -o circle_search circle_search.c -lm -lpthread

# correctness gate: n = 3..6 have closed-form optima, which the pipeline must
# reproduce and must never exceed
python3 circle_pipeline.py gate 500000 256 8 424242

python3 n14_reproduction.py 16384 1024 600000 8 20260824 \
        circle_configs/n14_reproduction.json
python3 n14_basin_probe.py 128 2 20260824 circle_configs/n14_basin_probe.json
python3 circle_families.py 14 512 8 20260823 circle_configs/n14_families.json
```

`n14_reproduction.py` checkpoints after every chunk, so a long run resumes
rather than restarting.
