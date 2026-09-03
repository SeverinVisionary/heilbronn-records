# A certified 14-point disk construction improving the best previously documented value located in a scoped search

**Hanyu Yang** · 2026-08 · *draft; not yet deposited*

## Abstract

For `n` points in a closed disk of radius 1, let `alpha_disk(n)` denote the
largest possible area of the smallest triangle they determine. We give an
explicit 14-point configuration, in exact integer coordinates, certifying

```
alpha_disk(14) >= 0.07671588577102893975178477550663348580098852235157588479993
```

This exceeds by more than 1% the best earlier value we have been able to locate:
`A = .0758+`, attributed to David Cantrell (June 2007) on Erich Friedman's
archived page *The Heilbronn Problem for Circles*. We also report a census of
`7 <= n <= 16` whose values fall inside Friedman's printed intervals at every
other `n` (the `n = 16` row required a symmetry-informed construction, not the
unrestricted search), and we document an error in a widely cited
secondary transcription of his table.

## 1. Three kinds of claim, kept separate

**Theorem (rigorous).** The 14 integer coordinates in §4, divided by
`scale = 10^33`, lie in the closed unit-radius disk and their least triangle
area is exactly
`76715885771028939751784775506633485800988522351575884799934177551 / 10^66`. Hence
`alpha_disk(14) >= 0.0767158857710272457...`. This is verifiable in finite exact
arithmetic and depends on nothing else in this note.

**Historical proposition (evidential, not proved).** This value exceeds the best
previously documented construction *known to us*. See §3 for exactly what the
source establishes and §7 for what we did and did not check.

**Numerical observation (not a claim).** The configuration is now numerically
stationary (§4.1); no local-optimality *theorem* is claimed, and the certified
rational sits `7.6e-34` below the high-precision value, so the bound remains
mildly conservative.

Note that `alpha_disk(14)` is a fixed unknown quantity: we improve a *lower
bound* for it, not the quantity itself.

## 2. Normalization

Two conventions are in use and mixing them has already corrupted one entry in
the secondary literature (§6):

| source | domain | conversion |
|---|---|---|
| Friedman, *The Heilbronn Problem for Circles* | radius 1 | native |
| MathWorld, *Heilbronn Triangle Problem* | area 1 | `alpha_disk = pi * H` |

We work in the **closed radius-1 disk**. Calibration: the regular pentagon gives
`alpha_disk(5) = sqrt(50 - 10 sqrt 5)/8 = 0.657163890148917`, agreeing with
Friedman's printed `.657+` and with no unit-area or unit-diameter reading.

## 3. What the source actually says, and what `.0758+` means

The primary source is a webpage, offline since approximately 2024 and cited here
from an Internet Archive capture of 2019-09-19, archived in this deposit at
`sources/friedman_heilcirc_20190919.html`. It states, verbatim:

> **14. A = .0758+  Found by David Cantrell, June 2007.  Horizontally symmetric.**

This is a **publicly reported construction attributed to Cantrell**, not a
peer-reviewed publication. We have located no paper, no exact coordinate list,
and no correspondence for it. We do not know that "personal communication" is
the right description; MathWorld says so, we cannot confirm it independently.

**On the `+` notation.** The page's closed-form rows show it marks truncation:
`3 sqrt 3 / 4 = 1.299038...` is printed `1.299+`, and
`sqrt(50-10 sqrt 5)/8 = 0.657163...` is printed `.657+`. The convention is not
applied perfectly consistently — `sqrt 3 / 4 = 0.433012...` is printed `.433`
with no `+` — so rather than rest on it we check **both** readings:

| reading of `.0758+` | Cantrell's value lies in | our margin |
|---|---|---|
| truncated to 4 dp | `[0.0758, 0.0759)` | **+1.075%** |
| rounded to 4 dp | `[0.07575, 0.07585)` | +1.142% |

The claim holds under either. We quote the **conservative +1.075%** throughout.

MathWorld's transcription gives `pi * 0.02414611295141071 = 0.075857251061`,
hence +1.132%. We use this only as secondary corroboration and never as the
basis of the comparison, because we have independently found that same table to
be wrong at `n = 11` (§6).

## 4. The configuration

Fourteen points; integers to be divided by `scale = 10^33`; also in
`data/circle_n14_converged.json`.

```
  p0  = ( 786499799846926615375693930280731,  617590531696158998652628941829267)
  p1  = ( 180942503653202439767674958829984,  983493675816835551114025498961935)
  p2  = (-846287204797998422196199537333214,  532726915966511566620758609511051)
  p3  = (-237710290535001132699190962504222, -272872605038715368894895625919661)
  p4  = (-991245961654899310211419560801005,   43801737923100693417044482202982)
  p5  = (-794553015948279200985276955313296, -607194783284156335225574709212789)
  p6  = ( 264717990004378700569121657230042, -246759045578659708830932604761099)
  p7  = ( 433979673434219618753044579953698, -900922662078120940025864579868887)
  p8  = ( 853219308191560248748410371864039, -521552310060184979532378365052603)
  p9  = ( 950971813528100673451604052388575,  146028178726100688056277476789546)
  p10 = ( 346427557104198732674799862189500,  384790308031432381864375051041013)
  p11 = (-281925704300825002737664366855359,  959436239285594101617368873934325)
  p12 = (-338243242726214495132491513043272, -941058716951314969875693727346225)
  p13 = (-384451903734496005369995262609257,  346803066870852954478749170500835)
```

Exact least triangle area over all `C(14,3) = 364` triples:

```
76715885771028939751784775506633485800988522351575884799934177551 / 10^66
```

Structure: before inward rational snapping, **eight boundary constraints are
active**; every certified rational point lies *strictly* inside the disk. Radii
`0.361892, 0.361892, 0.517760, 0.517760, 0.962120, 0.992212`. Measured
reflection defect `3.01e-02` — **asymmetric**, whereas Friedman annotates every
row of Cantrell's table with a symmetry class (n=14: "horizontally symmetric").
No degenerate triple; minimum pairwise distance `0.463`.

### 4.1 Why an earlier value looked "converged" when it was not

Earlier revisions certified `0.0767158857710272457...` and described it as
converged, on the strength of a Newton solve reaching a `1e-121` residual. That
was wrong, and the reason is structural rather than numerical.

Requiring the 16 active triangles to have equal area is **15 independent
difference equations** in the configuration's **16 spatial degrees of freedom**
(8 boundary points contributing one tangential dof each, 4 interior active
points two each; 2 points lie in no active triangle and are frozen).

That `15 x 16` system has **rank 14**, so its kernel is **two-dimensional**: the
rotation gauge, *plus one further direction*. Modulo rotation the equal-area set
is therefore a **curve**, and the common area is non-constant along it.
Equivalently, adjoining the common area `t` as a 17th unknown gives a `16 x 17`
Jacobian of rank 15 and nullity 2.

The rank matters. At rank 15 the kernel would be the rotation orbit alone, along
which the common area cannot vary, and there would be no curve to walk. (An
earlier revision of `data/n14_stationarity.json` recorded this rank as 15. That
was an error; recomputation gives 14, and the argument below is sound only at
rank 14.)

A Newton solve lands *somewhere* on this curve, reports a vanishing residual,
and looks converged while a feasible ascent direction survives untouched.

Walking the curve to the maximum moves the value by `+1.694e-15` absolute,
`+2.21e-14` relative — the 14th significant digit. **That smallness is the
answer to "why did you stop?":** the earlier point was already within `2.2e-14`
relative of the top of its own curve. Stationarity evidence, as committed data
in `data/n14_stationarity.json`:

| | Newton point | curve endpoint |
|---|---|---|
| best equal-rate ascent per unit displacement | `1.25e-9` | `1.9e-53` |
| KKT residual (inf-norm over all `2N+1` rows) | `3.5e-10` — no feasible multipliers found at working precision | `5.3e-54` |
| smallest multipliers | — | `min lambda = 1.10e-2`, `min mu = 1.38e-3`, strictly positive |

Here `lambda_T >= 0` are the multipliers on the active area constraints
(normalised to `sum lambda_T = 1`) and `mu_i >= 0` those on the active disk
constraints, in the stationarity condition
`sum_T lambda_T grad(sigma_T area_T) = sum_i 2 mu_i p_i`. They form a
one-parameter family; the member reported is the one maximising the smallest
multiplier. The residual is the infinity-norm over all `2N+1` rows, dependent
rows included.

Two caveats, recorded rather than smoothed. The stationary point is **not
isolated** — two points lie in no active triangle and drift freely between
`r = 0.960` and `r = 1.000`. And re-running the walk re-snaps about `1.9e-34`
away, so this deposit reproduces to roughly one unit in the last place of the
`10^33` grid.

**Correction.** A previous revision called the single exact tie *intrinsic*. It
is not: at the stationary point the 16 active areas agree to `1.4e-44`, so the
lone exact tie is an artifact of the integer grid, exactly as the original
diagnosis said. The other nine circle rows have **not** been through this walk
and remain snap-limited certified floors.

### 4.2 How hard is this configuration to find?

A recorded, replayable study — seed base `20260824`, restart seeds
`20260824 + 1000003*k` for `k = 0..16383`, 600000 annealing iterations each,
every restart LP-polished (`data/n14_reproduction.json`):

- **9 of 16384 restarts reach the record basin — 0.055%, about one in 1800**,
  roughly 1600 CPU-seconds per hit. Wall-clock 15693 s; summed process CPU time
  14596 s, on a 10-core machine with 8 search threads (the run was not
  CPU-saturated, so summed CPU is below wall x cores).
- 4 restarts reach the 11+3 basin matching the archived figure; 34 exceed
  Cantrell's printed value; 13684 distinct basins
  at a `1e-9` tolerance.
- **In this 16384-restart sample, no terminal value fell between `0.0759` and
  `0.0765`.** This is a sampled gap, not a proven empty region of the landscape.
- All nine hits carry the *same* 16 active triangles, but the two free points
  wander, so eight read as 8+6 and one as 9+5 — empirical confirmation of the
  non-isolation above.
- Systematic family enumeration never finds it (the record's own 8-on-circle
  *enumerated symmetric* 8-on-circle ansatz tops out 25% low — the record itself
  has eight boundary-active points, so this is a restriction of that family, not
  all of it), yet it matches Cantrell's printed value to 11 digits from the 11+3
  family.

With 9 successes in 16384 trials the exact Clopper–Pearson 95% interval is
`0.0251%`–`0.1043%`, i.e. about 4.1 to 17.1 hits per 16384. The rate is good to
a factor of three, not to two figures.

**Correction.** An earlier revision claimed "23 of 8192 restarts". That figure
had no artifact behind it and does not survive measurement: at the same 8192
budget this study found **6**.

**Not a match to any archived n = 14 figure.** Friedman's page carries three figures for n = 14
(`hc14a/b/c`). We recovered point sets from all three (`extract_friedman_figure.py`; the
measurements are committed as `configs/friedman_figure_measurements.json`, and
the figures themselves are retrievable via `fetch_sources.py` — we do not
redistribute them, see `THIRD_PARTY.md`); each shows an 11+3 configuration with
interior radii `~{0.26, 0.333, 0.333}`, against our 8+6 with interior
`{0.362, 0.362, 0.518, 0.518}`. Reconstructed figures are evidence of
*structure*, not of value, and are no substitute for Cantrell's original data.
The check matters: an earlier claim of ours at n = 11 was withdrawn because our
configuration there *was* Cantrell's, established the same way.

## 5. Verification

```bash
python3 verify.py configs
```

Python standard library only; no dependency outside this deposit. It re-derives
distinctness, closed-disk containment, non-degeneracy, the complete 364-triple
enumeration, and the exact rational minimum, then compares against Friedman's
bracket. It is deliberately short enough to audit by reading.

## 6. Census, and an erratum

| n | 7 | 8 | 9 | 10 | 11 | 12 | 13 | **14** | 15 | 16 |
|---|---|---|---|---|---|---|---|---|---|---|
| | in bracket | in bracket | in bracket | in bracket | in bracket | in bracket | in bracket | **+1.075%** | in bracket | in bracket* |

Nine of ten rows reproduce Cantrell — evidence that the optimizer is not
producing arbitrary incompatible families. We regard `n = 13` as **not
claimable**: Friedman prints only `.0856+`, which cannot discriminate a margin
of that size.

**Erratum.** MathWorld's `H_11 = 0.03494193340280051` (`0.109773` at unit
radius) disagrees with Friedman's `.113+`, at that row and no other, and
corresponds to an inferior 10+1 ring-and-interior family. Our n = 11
configuration attains `0.113938117431`, confirming Friedman. This is an erratum
worth reporting upstream, not a mathematical contribution.

## 7. Prior art — scope and limits

Checked, with no disk values found: Finch, *Mathematical Constants* §8.16;
Goldberg (1972), *Math. Mag.* **45** 135–144,
doi:10.1080/0025570X.1972.11976214; the Yang–Zhang–Zeng literature; Karpov's
Ascension framework (square and triangle only — his page and data archived
here); erdosproblems #507 (asymptotics only); DataCite / Zenodo / OSF /
figshare; and the LLM-discovery literature — AlphaEvolve, GigaEvo,
EinsteinArena, SeaEvo, BLADE — all of which treat the square, the unit-area
triangle, or a free convex hull, never the disk. The only other disk
tabulation, Lystad's *DISK_TABLE* v1.2 (2026), is below Cantrell at every `n`
we checked.

**Not checked.** Math-Net.Ru, Croft–Falconer–Guy §F7, Brass–Moser–Pach. We
therefore do **not** assert that our search is exhaustive, and we do not claim
"the first improvement since 2007" without qualification. The defensible
statement is: *the best previously documented value we have located*.

## 8. What would make this more than a data point

We state plainly that this is a computational note: one improved row, no new
theorem, no new method. It would become substantially more with any of — a
systematic certified improvement at several `n`; a structural explanation of why
the asymmetric 8+6 family wins here; a meaningful upper bound; or a fully
reconstructed and independently recomputed modern table for the disk.

## Data availability

All configurations, the verifier, the extraction code and our figure
measurements are in this deposit. Third-party sources are **not** redistributed;
`THIRD_PARTY.md` records how to retrieve and checksum them. License: CC-BY-4.0.
