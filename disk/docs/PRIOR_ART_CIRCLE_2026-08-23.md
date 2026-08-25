# Circle prior-art gate — 2026-08-23

**Verdict: the n = 11 improvement claim is retracted. Our configuration is an
independent rediscovery of a construction David Cantrell found in August 2006.**

## The primary source

Erich Friedman, *The Heilbronn Problem for Circles*
([archived copy](friedman_heilcirc_20190919.html), snapshot 2019-09-19 of
`www2.stetson.edu/~efriedma/heilcirc/`; the current
`erich-friedman.github.io/packing/heilcirc/` path 404s). The page states:

> The following pictures show n points inside a unit circle so that the area A
> of the smallest triangle formed by these points is maximized.

so its normalization is the **unit-radius** circle. This is confirmed
independently: the page gives `5. A = sqrt(50-10 sqrt5)/8 = .657+`, and a direct
regular-pentagon computation in the unit-radius disk gives `0.657163890`.

Its row for eleven points reads, verbatim:

> **11. A = .113+ Found by David Cantrell, August 2006. Horizontally symmetric.**

Our value is `0.113938117431`. That is Cantrell's number.

## MathWorld disagrees with Friedman at exactly one row

Converting MathWorld's unit-AREA constants by `alpha_disk = pi * H_n`:

| n | Friedman (unit radius) | MathWorld * pi | agree |
|---|---|---|---|
| 10 | .150+ | 0.150385 | yes |
| **11** | **.113+** | **0.109773** | **NO** |
| 12 | .104+ | 0.104915 | yes |
| 13 | .0856+ | 0.085658 | yes |
| 14 | .0758+ | 0.075857 | yes |
| 15 | .0700+ | 0.070040 | yes |
| 16 | .0661+ | 0.066128 | yes |

Six of seven rows agree. **MathWorld's `H_11 = 0.03494193340280051` is
erroneous** — it is not Cantrell's value, and a configuration achieving
`0.1139 > pi * 0.0349419 = 0.109773` demonstrably exists, since we hold exactly
certified coordinates for one. The error has stood since at least 2013. It is
worth reporting upstream to Wolfram; it is not a research result.

## What this cost, and the rule it re-establishes

The softness audit (`circle_attack.py:softness_audit`) flagged n = 11 as an
outlier at +13.5% below its neighbour mean — nearly 4x the next candidate — and
that flag was *correct*: the row really was anomalous. But the audit cannot
distinguish "under-optimized configuration" from "wrong number in the table",
and we read it as the former. Only the primary source separates the two.

The prior-art gate is supposed to run **before** the compute. Here it ran after.
The specific failure: Friedman's Packing Center was checked at
`packing/heilbronn/`, which covers the square only, and that was recorded as
"the site has no circle table". The circle table lives at a **separate path**,
`heilcirc/`. An index page that does not link a table is not evidence the table
does not exist.

This is the second time this campaign has inferred a record from the *absence*
of a competing entry rather than from a located source — the first was the disk
retraction of 2026-08-21. Absence of evidence keeps getting read as evidence of
absence.

## What survives

* `n = 13`: ours `0.085689772657` vs published `0.085658235732` (+0.037%).
* `n = 14`: ours `0.075861514504` vs published `0.075857251061` (+0.0056%).

Friedman prints `.0856+` and `.0758+`, which cannot discriminate margins this
small, and MathWorld agrees with Friedman at both rows. These are polish, not
records, and are **not** to be described as new best-known constants until
Cantrell's own values are recovered to full precision and shown to be exceeded.

* The exact-certification machinery is unaffected: containment and minimum area
  are recomputed as exact rationals from integer coordinates, independently
  re-verified. The configurations are what they claim to be. Whether they are
  *new* is a separate question, and it is the question we got wrong.

## Completed sweep (2026-08-23) — the record is Cantrell's, and nothing since 2007

An independent sweep confirms the retraction and closes the remaining gaps.

**Friedman's page history.** Wayback CDX for `www2.stetson.edu/~efriedma/heilcirc/`
shows captures 2006-09-04 → 2019-02-18 (200), then 404 from 2024-07-31. Every
capture from 2007-10-21 onward carries the **identical digest**
`RYYQ5NVYAHDAU6A7KZ5IDEIFX2GQPAQW`, so the page never changed after Oct 2007 and
no later revision exists anywhere. The 2006-09-04 capture already has n=11 at
`.113+`, but n=13 = `.0838+` and n=14 = `.0734+`; those were superseded in June
2007 by `.0856+` and `.0758+`. `heilcirc` **never existed** on the current
github.io host — the live index links only `heilbronn/`, `heiltri/`,
`heilconvex/`. MathWorld's own bibliography cites the *archived* stetson URL,
so Wolfram knows the page is dead.

**The n=11 conflict is resolved, and MathWorld is the wrong one.** Both sources
attribute to Cantrell; they disagree only at n=11. This is decidable without
adjudicating provenance: a lower bound is settled by exhibiting a configuration,
and we hold exactly certified coordinates achieving `0.113938117431 >
0.109773321280`. Friedman's `.113+` is achievable; MathWorld's row is not the
best known. (Note MathWorld's value is close to the optimum of the
10-on-circle-plus-one-interior family, which is a *local* optimum — consistent
with a wrong-family entry rather than a typo. Lystad's n=11, `0.109464845502`,
lands in that same family.)

**Nothing else in the world reports disk numerics.** Explicit negatives, each
checked: Finch *Mathematical Constants* §8.16 (square and unit triangle only —
read in full, definitive); Goldberg 1972 (square-only per four independent
secondary sources); the Yang–Zhang–Zeng / Dress–Zeng Chinese literature (square,
triangular region, and n=6,7 in a general convex body); Wikipedia, HandWiki and
erdosproblems #507 (asymptotics only, no table); DataCite/figshare/OSF/Dryad
(the only disk deposits are Lystad's); Roth 1973, Komlós–Pintz–Szemerédi 1982
and Agama arXiv:2006.05269 (asymptotic only).

**No LLM/evolutionary system has touched the disk.** AlphaEvolve, GigaEvo,
EinsteinArena, SeaEvo, ShinkaEvolve, FlowBoost, BLADE and the rest all run
Heilbronn in the **square**, the **unit-area equilateral triangle** (n=11), or
**convex-hull** normalization (n=13,14) — never the disk. The single exception is
an OpenEvolve benchmark `erdos_507_heilbronn_disk_n12` whose stated target is the
regular 12-gon (`0.066987`), far below the long-known `0.1049`.

**Unverified, not negative:** Math-Net.Ru (JS-gated search), Croft–Falconer–Guy
§F7 p.155 (archive.org search-inside 403), Brass–Moser–Pach (gated). No evidence
any contains a disk table; recorded as gaps rather than clean negatives.

## Where this leaves the circle lane

`n <= 16` is **closed**: Cantrell optimized it well in 2006–07, and our pipeline
reproduces him rather than beating him. Our n=13/n=14 margins (`+0.037%`,
`+0.0056%`) are too small to claim against a record whose canonical precision we
cannot establish — MathWorld is demonstrably unreliable at one row, and
Friedman's printed `.0856+`/`.0758+` cannot discriminate margins this small.
**Not claimable.**

`n >= 17` has **no credible incumbent at all**: Friedman's page stops at 16,
MathWorld at 15, and the only table covering that range (Lystad v1.2) sits ~20%
below Cantrell where the two overlap (n=14: `0.0605` vs `0.0759`). Producing
better numbers there would be *establishing a first credible table*, not beating
a record — honest work, but a webpage, not a result.

## Third confirmation: image forensics on the archived figures

A third sweep confirmed the n=11 retraction by a route neither of the others
used — reconstructing Cantrell's configurations from the **figures** on the
archived page (dot-centroid extraction -> bounding-circle fit -> maximin
refinement with hard containment).

**Calibrated first on the undisputed rows**, which is what makes it evidence:

| figure | reconstructed | published | agreement |
|---|---|---|---|
| `hc10.gif` | 0.150383733 | 0.150383732407 (closed form) | 9 digits |
| `hc13b.gif` | 0.085658236 | 0.0856582357 | 10 digits |
| `hc14b.gif` | 0.075857251 | 0.0758572511 | 11 digits |

Then n=11: `hc11.gif`, `hc11b.gif`, `hc11c.gif` **all** refine to
`0.1139381174` — never `0.109773`. A rigid overlay of our own configuration onto
Cantrell's picture gives **0.77 px RMS on a 107.6 px radius**, identical
structure (8 boundary + 3 interior), interior radii
`{0.307827, 0.307827, 0.509904}`, distance multiset agreeing to `2.3e-8` and
minimum area to `1.4e-13`. Cantrell's picture *is* our configuration.

**Methodological note worth keeping.** A solver failing to reach `0.1139` from
random starts proves nothing about whether the value is attainable — that sweep's
own naive multistart topped out at `0.0888` over 150 SLSQP restarts. The basin is
hard to find. The archived picture was the evidence; the search was not.

### Consequence for n = 13 and n = 14

The reconstruction independently establishes **Cantrell's own values** at both
rows, without relying on MathWorld:

* **n = 14** — baseline `0.075857251061` confirmed to 11 digits from `hc14b.gif`.
  Our `0.076715885771` therefore exceeds a *doubly verified* baseline by
  **+1.13%**. This removes the last reservation about the claim: it no longer
  depends on trusting the table that is wrong at n=11.
* **n = 13** — baseline `0.085658235732` confirmed to 10 digits from `hc13b.gif`.
  Our `0.085689772657` exceeds it by `+0.037%`, and our configuration is
  structurally distinct (interior radii `0.407/0.473/0.487` vs Cantrell's
  `0.507/0.507/0.549`). Upgraded from *unresolved* to **probably real but small**
  — still below the ~0.05% bar for a headline claim, since Friedman prints only
  `.0856+`, but no longer resting on MathWorld alone.

### One more structural fact

Friedman's Packing Center still maintains **squares, triangles and convex
regions** through Aug 2026. The **circle page is the only one in the family with
no living maintainer** — dead since ~2024, archive-only. That is why a 2007 row
survived unchallenged: not because the problem is hard, but because nobody was
keeping score.

## The forensics, made reproducible (2026-08-24)

The section above reported figure reconstructions in prose only — no images, no
code, no coordinates. All three legs of the 2026-08-24 review panel flagged that
as the single load-bearing claim nobody could replay, and Codex rated it HIGH.
Fixed: the archived figures are committed under
[friedman_figures/](friedman_figures/) (16 GIFs, n = 9..16) together with
[extract_friedman_figure.py](extract_friedman_figure.py), which recovers a point
set from any of them.

The method matters because dots, outline and the coloured minimum-area triangles
are all one connected black/colour mass; a single erosion kills the one-pixel
outline and the triangle edges while the filled dots survive. At ~106 px circle
radius the **structure** is recoverable but the **value** is not — a dot centre
is good to ~0.5%, an area derived from three of them to a few percent.

**Use it as a discriminant, never as a measurement.** The interior-radius
signature identifies which configuration a figure shows, which is precisely what
the n=11 retraction turned on, and precisely what the n=14 claim needed:

| n | figures on the page | interior signature | ours | verdict |
|---|---|---|---|---|
| 11 | `hc11`, `hc11b`, `hc11c` | all Cantrell's | same | **rediscovery** |
| 14 | `hc14a`, `hc14b`, `hc14c` | all `{0.26, 0.333, 0.333}`, 11+3 | `{0.362, 0.362, 0.518, 0.518}`, 8+6 | **distinct** |

Only `hc14b` had been reconstructed before. Checking `a` and `c` was the gap
that, left open, is exactly how n=11 was missed.

## Karpov / inversed.ru — CHECKED 2026-08-24, clean negative

The last named open source is now closed. **Peter Karpov's Ascension framework
covers the Heilbronn problem in the unit SQUARE and the TRIANGLE only — there is
no circle or disk variant anywhere on the site.**

Why every automated leg reported it unreachable: `https://inversed.ru` fails TLS
with `TLSV1_ALERT_UNRECOGNIZED_NAME` (the server does not answer to that SNI),
and the fetch tooling force-upgrades `http` to `https`. **Plain HTTP serves the
site fine** — `http://inversed.ru/Ascension.htm` returns 200. The site was never
down; the tooling could not express the request. Worth remembering: an
"unreachable" verdict from a fetcher that rewrites the scheme is not evidence
the resource is gone.

Verbatim from the page (archived at
[karpov_inversed/Ascension_2026-08-24.html](karpov_inversed/Ascension_2026-08-24.html)):

> Heilbronn problem: maximize the area of the smallest triangle formed by N
> points inside of a **unit square**

> Some Heilbronn problem solutions for the **unit square and triangular
> regions**: N = 13, A = 0.0270+ … N = 15, A = 0.0211+ … N = 13, A = 0.0265+

His published coordinate files confirm the domains directly — archived
alongside:

| file | score | domain (from the coordinates) |
|---|---|---|
| `Heilbronn_S13.txt` | `0.0270192722391139` | unit square, all coordinates in `[0,1]^2` |
| `Heilbronn_S15.txt` | `0.0211056818784151` | unit square |
| `Heilbronn_T13.txt` | `0.0265013422223496` | triangle, coordinates signed |

A full-site scan found `heilbronn` only on `Ascension.htm`, with **zero**
occurrences of `circle`; the two `disk`/`disc` matches are `discrete` and
`discovery`.

**Consequence:** no prior-art item now stands against the n = 14 claim. The
"first change to that row since 2007" framing survives, and the certified lower
bound was never at risk from this source regardless.

Still unverified rather than negative: Math-Net.Ru, Croft-Falconer-Guy §F7,
Brass-Moser-Pach — none of which is a plausible home for a disk table.

Still unverified rather than negative, as before: Math-Net.Ru, Croft-Falconer-Guy
§F7, Brass-Moser-Pach.
