# Five-boundary normal-form discovery campaign — 2026-08-17

## Scope

`global_normal_form_search.py` searches all 19 free coordinates in the
five-boundary normal form used by the global interval and McCormick tracks:
five ordered boundary coordinates, seven ordered free x-coordinates, and
seven free y-coordinates.  It is therefore broader than the frozen-boundary,
size-five, C2, C4, and D4 exploratory strata.

Its global interpretation is conditional on the Sudermann--Merx boundary
theorem: an optimizer can be relabelled into this normal form.  This is a
numerical discovery campaign, not an upper-bound proof and not a resolution of
the n=12 problem.

## Discovery and exact gate

Each trial uses blind differential evolution over the unit box; it receives
neither incumbent coordinates nor the incumbent score.  The best discovered
orientation cell is then polished by a signed epigraph SLSQP solve.  A reported
floating score is always recomputed from its coordinates.

Finally, the selected coordinates are rounded to a stated dyadic grid and the
existing `incumbent.py` `Fraction` verifier enumerates all 220 triangles.  Only
that exact audit could support a strict-improvement statement.

## First four-seed campaign

All four recorded seeds used `popsize=24`, `maxiter=3000`, and a 32-bit dyadic
audit.  Each differential-evolution stage made 1,368,456 objective calls.

| Seed | DE minimum | Polished minimum | Exact 32-bit snapped minimum | Strictly beats incumbent? |
|---:|---:|---:|---|---|
| 2026081601 | 0.010555975326669510 | 0.020364845659030007 | `375665095004066231 / 18446744073709551616` | no |
| 2026081602 | 0.011055789155816537 | 0.024447426089270585 | `112743852692828237 / 4611686018427387904` | no |
| 2026081603 | 0.012359909713736128 | 0.019653732856867209 | `362547378610620703 / 18446744073709551616` | no |
| 2026081604 | 0.012527130771879915 | 0.020333263731128162 | `375082511154956767 / 18446744073709551616` | no |

Every epigraph polish returned success and was the selected stage.  The best
exact snap was the second seed, approximately `0.024447426089270585`, still
well below the Comellas--Yebra value `0.032598858691819698...`.

The campaign found neither an exact candidate nor evidence that the record is
optimal.  It merely rules out these four reproducible numerical outputs as
improvements and supplies broader starting points for later exact subdivision.

## Reproduction

```sh
cd research/heilbronn_n12

# Small exact-audited smoke trial.
make global-normal-search

# The recorded four-seed batch.
for seed in 2026081601 2026081602 2026081603 2026081604; do
  python3 global_normal_form_search.py --seed "$seed" --popsize 24 --maxiter 3000 --snap-bits 32
done
```
