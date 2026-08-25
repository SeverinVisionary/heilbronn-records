# heilbronn-records

Exactly certified work on **Heilbronn's triangle problem**: given `n` points in a
convex domain, maximize the area of the smallest triangle they determine.

Everything here is auditable. Every certified geometric bound is re-derived from exact integer coordinates in
rational arithmetic. Numerical search results and stationarity diagnostics are
separately labelled and reproducible from their recorded artifacts.

> **What "records" means here, precisely.** This repository contains exactly
> **one** improved value (`disk/`, n = 14). It is a certified **lower bound** on
> an unknown quantity, improving the best previously *documented* construction we
> could locate — not a proved record, and not an optimality result. The square
> lane below broke **no** records at all; it produced structure and negatives.
> Current contents: one improved documented disk lower bound at n = 14, exact
> square-configuration certificates, and negative results.

## The one improved value — `disk/`

For `n` points in the **closed disk of radius 1**:

```
alpha_disk(14) >= 0.07671588577102893975178477550663348580098852235157588479993
```

exceeding by **+1.075%** the best earlier value we located — `A = .0758+`,
attributed to David Cantrell (June 2007) on Erich Friedman's page *The Heilbronn
Problem for Circles*, offline since ~2024 and archived here.

```bash
cd disk && python3 verify.py configs   # -> 12 of 12 configurations verified
```

Standard library only. It re-derives distinctness, closed-disk containment,
non-degeneracy, the complete `C(n,3)` enumeration, and the exact rational
minimum for every configuration, then compares each against the published
bracket. Short enough to audit by reading.

Alongside it, a census of `7 <= n <= 16` in which the values fall inside Friedman's
printed intervals at every other `n` (the `n = 16` row required a
symmetry-informed construction, not the unrestricted search). His 2007
table is, on this evidence, very well made.

An independent restart finds this basin about **once in 1800** tries — 9 of
16384 in a seed-recorded study — and no restart lands anywhere between `0.0759`
and `0.0765`. In that study no terminal value fell in that interval; it is a sampled gap, not a proven empty region.

Read [`disk/NOTE.md`](disk/NOTE.md) for the full statement, including a careful
separation of what is rigorous (the bound), what is evidential (the historical
comparison), and what is merely observed. §4.1 explains why an earlier value
looked converged when it was not: the equal-area set is a *curve*, not a point,
so a Newton solve reports a vanishing residual while a feasible ascent direction
survives.

## Structure, not records — `square/`

The unit-square lane produced **no improved values**, and none is claimed. What
it produced instead:

- **A rigidity audit of the record landscape, `7 <= n <= 12`.** Every best-known
  square configuration certified, in its own exact field. Five are
  infinitesimally rigid; **n = 10 is the unique exception**.
- **n = 10 is prestress stable.** First-order flexible (rank 19 in dimension 20)
  but second-order rigid: an exact strictly positive stress collapses the
  feasible cone onto the flex line, and the stress-weighted Hessian is negative
  (`Q = -109.241`). Hence a strict, isolated local maximum. Comellas–Yebra did
  not see this because their check ran inside a three-parameter symmetric ansatz.
- **An n = 12 minimal-core theorem.** All 6196 subsets of the active triangles
  classified with exact two-sided certificates: exactly three D₄-classes of
  inclusion-minimal rigid cores, sizes 17/18/18, and no rigid 16-subset.
- **A disconfirmation.** n = 10 being the *only* flexible configuration in that
  range refutes the hypothesis that symmetric ansätze systematically hide flexes.

"No first-order improvement" is a *proof*, not a failed search: it follows from
the verified strictly positive stress, so no feasible velocity can increase every
active area.

```bash
cd square && python3 -m pytest test_rigidity_engine.py -q    # 20 passed
```

## Negative results are kept, not deleted

[`disk/docs/DISK_ASCENT_2026-08-21.md`](disk/docs/DISK_ASCENT_2026-08-21.md)
carries a **retraction**: six configurations once claimed as "best known" were
beaten by a naive annealer by up to 48%. The error was inferring "best known"
from the *absence* of a competing table.

[`disk/docs/PRIOR_ART_CIRCLE_2026-08-23.md`](disk/docs/PRIOR_ART_CIRCLE_2026-08-23.md)
carries a second: a claimed +3.79% at n = 11 turned out to *be* Cantrell's own
2006 configuration, reached because the baseline came from a secondary table
that is wrong at exactly that row.

Both are kept deliberately. A repository that shows only its successes is not
auditable.

## Layout

```
disk/     configs/ verify.py NOTE.md search/ sources/ docs/
square/   rigidity engine, exact fields, config registry, tests, docs/
```

**No third-party material is redistributed here.** The primary source for the
historical comparison is a web page that went offline around 2024; rather than
mirror it, [`disk/THIRD_PARTY.md`](disk/THIRD_PARTY.md) records its URL, capture
timestamp and sha256, [`disk/fetch_sources.py`](disk/fetch_sources.py) retrieves
it from the Internet Archive on demand, and our own measurements of its figures
are committed as `disk/configs/friedman_figure_measurements.json`. Nothing
certified depends on any of it.

## License

CC-BY-4.0. Everything in this repository is our own work — see
[LICENSE](LICENSE). Third-party sources are cited and checksummed in
[`disk/THIRD_PARTY.md`](disk/THIRD_PARTY.md), never copied.
