# Exact ascent over the unit-disk Heilbronn table — 2026-08-21

> ## RETRACTED 2026-08-23
>
> **The "best known for the disk" claims below are withdrawn, and the disk lane
> is closed.** The 2026-08-21 HEAVY panel refuted them, and we reproduced the
> refutation independently:
>
> | n | this document's value | naive annealer, ~10 min, one core | ratio |
> |---|---|---|---|
> | 19 | 0.031740345198 | **0.034457484708** | 1.086 |
> | 30 | 0.009711858577 | **0.011659261748** | 1.201 |
> | 37 | 0.005610948929 | **0.006568583245** | 1.171 |
> | 45 | 0.002692405631 | **0.003987637683** | **1.481** |
>
> A multistart simulated annealer with no structure, no symmetry and no
> certificates — 24 restarts of 200k incremental iterations on one core — beats
> **every** row this document reported, by up to 48%. The panel's own annealer
> found the same thing independently at n=30 and n=45.
>
> Three separate errors are being corrected:
>
> 1. **"Best known for the disk" was never established.** It was inferred from
>    the absence of a competing table, not from a search of comparable strength.
>    Absence of a published baseline is not evidence of quality.
> 2. **A published disk baseline does exist.** MathWorld's Heilbronn page
>    carries best-known **circle** constants (Friedman 2007; D. Cantrell, pers.
>    comm., 2007-06-18), in *unit-area* normalization. Our check of the Packing
>    Center index missed it because that table is not on the Packing Center.
>    The claim below that ours is "the correct (and only) baseline" is false.
> 3. **"38 rows resisted → at least locally polished" was wrong.** As the panel
>    showed, our own committed n=19 output provably admits a first-order
>    improvement direction while `ascend` makes no progress on it: "resisted"
>    measured the line search, not the configuration. The suspected mechanism is
>    the curved-boundary bug (tangential contacts at a disk boundary are
>    infeasible at every `t > 0`, though the linearized row admits them).
>
> What survives: the six configurations are *exactly verified* — containment and
> minimum area are correct rationals, and `verify_disk_configs.py` is sound.
> They are simply not good configurations, and the labels attached to them were
> not earned. Refutation artifacts: `refutation/`.
>
> **Lesson recorded:** an exact certificate proves a configuration is what it
> claims to be; it says nothing about whether the configuration is any good. We
> conflated the two. Any future record claim needs a *strength* baseline — a
> real optimizer run — before the word "best" appears.

First application of the certificate-guided campaign
([GENERAL_RIGIDITY_CAMPAIGN_2026-08-21.md](../heilbronn_n12/GENERAL_RIGIDITY_CAMPAIGN_2026-08-21.md))
to a domain other than the unit square.

## Baseline and prior-art gate

The only published exact-certified table for the unit-radius disk is
**DISK_TABLE v1.2**, T. Alexander Lystad / Shubin Sciences AS, Zenodo,
2026-08-01, [doi:10.5281/zenodo.21751173](https://doi.org/10.5281/zenodo.21751173)
(CC-BY-4.0), 44 rows, `n = 5..48`, integer coordinates scaled by `10^9`, each
row an exact rational lower bound on `alpha_disk(n)`. It was located through
DataCite/OpenAlex in the [global novelty sweep](../heilbronn_n12/NOVELTY_GLOBAL_2026-08-20.md);
Google Scholar does not index it.

Our own parser reproduces **every** sampled published value exactly, so the
baseline is sound and the comparison is like-for-like.

The competing construction at each `n` is the *transported square record*: a
unit square inscribed in the unit-radius disk has side `sqrt(2)`, so any square
configuration transports with all areas doubled, giving
`alpha_disk(n) >= 2 * alpha_square(n)`. Erich Friedman's square table was
re-fetched 2026-08-21 for this comparison.

## Why the rows were attackable

The audit answers this immediately. Every row is a float optimum snapped to a
`10^-9` grid, so:

- only **one or two** triangles attain the exact minimum (a critical
  configuration has many);
- **no point lies exactly on the bounding circle** (`x^2 + y^2 = 1` is not
  satisfiable at a generic grid point);

hence the active system has a handful of rows in dimension `2n`, is massively
rank-deficient, and admits directions that strictly increase every
minimum-area triangle. This is class A/B of the campaign: soft by certificate.

## Method

[exact_ascent.py](../heilbronn_n12/exact_ascent.py): per round, take the band of
triangles within a relative tolerance of the exact minimum, ask an LP for a
direction increasing all of them, rationalize it, then run an **exact** line
search — each trial step is accepted only if exact containment holds and the
exact minimum strictly increases. Floating point proposes; rational arithmetic
decides. Nothing float-valued enters a reported number.

## Results — 6 of 44 rows improved

| n | baseline (exact) | ours (exact) | relative gain | best-known status after this |
|---|---|---|---|---|
| 19 | 0.031709981415 | 0.031740345198 | +9.58e-04 | ~~best known~~ **RETRACTED** — a naive annealer reaches 0.034457 |
| 27 | 0.013261863657 | 0.013286118638 | +1.83e-03 | still below transported square (0.013580) |
| 28 | 0.012394625162 | 0.012395665315 | +8.39e-05 | still below transported square (0.013550) |
| 30 | 0.009324994109 | **0.009711858577** | **+4.15e-02** | still below transported square (0.010890) |
| 37 | 0.005610909168 | 0.005610948929 | +7.09e-06 | ~~best known~~ **RETRACTED** — a naive annealer reaches 0.006569 |
| 45 | 0.002666957539 | 0.002692405631 | +9.54e-03 | ~~best known~~ **RETRACTED** — a naive annealer reaches 0.003988 (1.48x) |

~~The remaining 38 rows resisted … those rows are at least locally polished.~~
**Retracted:** the ascent's failure to find a step measures the line search, not
the configuration. Our own n=19 output admits a verified first-order improvement
direction that `ascend` cannot act on.

Every improved configuration is committed in [configs/](configs/) as exact
integer-scaled coordinates and re-checked by
[verify_disk_configs.py](verify_disk_configs.py), a standalone
standard-library-only verifier that recomputes containment and the exact
minimum from scratch and asserts the strict improvement:

```bash
python3 research/heilbronn_disk/verify_disk_configs.py
```

`6 of 6 configurations verified`.

## Second finding: the baseline's labels are now stale

DISK_TABLE v1.2 froze on 2026-08-01 with the (then correct) premise that
Friedman's square table had no entries at `n >= 29`. Between 2026-07 and
2026-08 that table was extensively rewritten — Tej Stead, Nathan
Sudermann-Merx, William Shanley and Marc-Emmanuel Coupvent des Graviers moved
most records in `n = 15, 17..35`. Recomputing the transported bound against the
current table:

- **dominated by the transported square construction** (so the disk-native row
  is no longer "candidate best known"): `n = 27, 28, 29, 30, 31, 32, 34, 35`;
- **disk-native still best**: `n = 25, 26, 33`, and everything at `n >= 36`
  where the square table stops.

This is worth reporting upstream to the dataset's author; it is a labelling
correction, not an error in their arithmetic.

## Honest scope

- These are **constructions** (lower bounds), not optima, exactly as the
  baseline states of itself.
- The improvements are over a three-week-old dataset, not over a
  long-standing mathematical record. The `n = 30` row (+4.1%) is the only one
  large enough to be interesting on its own.
- Rational-coordinate configurations are inherently non-critical in the disk:
  a true critical configuration needs points exactly on the circle, hence
  algebraic coordinates. Producing *those* — with rigidity certificates — is
  the real disk project, and none exist anywhere in the literature.
