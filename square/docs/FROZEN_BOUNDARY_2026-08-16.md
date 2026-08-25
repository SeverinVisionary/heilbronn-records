# Frozen-boundary basin experiment — 2026-08-16

## Scope

The eight incumbent boundary points are held fixed.  The four interior points
are free (`8` continuous variables), so this is the smallest stratum that can
move the unique minimum active-set hitting set.

Each trial uses a random seeded differential-evolution population and then a
sign-fixed epigraph SLSQP polish.  No incumbent interior coordinate is supplied
to the optimizer.  The result is exploratory evidence only: floating-point
agreement never constitutes a record certificate.

## Results

All eight recorded seeds re-entered the incumbent basin, up to permutation of
the four interior labels.  No run found a distinct topology or a positive gap
above the incumbent.

| Seed | DE minimum | Epigraph minimum | Evaluations |
|---:|---:|---:|---:|
| 20260816 | 0.032598858691524124 | 0.032598858691819221 | 264,669 |
| 20260817 | 0.032598858691339716 | 0.032598858691819527 | 188,349 |
| 20260818 | 0.032598858691441066 | 0.032598858691819568 | 203,949 |
| 20260819 | 0.032598858691407773 | 0.032598858691819665 | 282,429 |
| 20260820 | 0.032598858691403887 | 0.032598858691819332 | 339,309 |
| 20260821 | 0.032598858691537724 | 0.032598858691819499 | 319,629 |
| 20260822 | 0.032598858691306964 | 0.032598858691819443 | 189,549 |
| 20260823 | 0.032598858691195817 | 0.032598858691819499 | 239,949 |

The independently reconstructed incumbent evaluates to
`0.032598858691819679` in the same float evaluator.  The tiny negative gaps
above are ordinary floating-point/polish error, not evidence of a lower value.

Reproduce a chosen seed with:

```sh
cd research/heilbronn_n12
python3 frozen_boundary_search.py --seed 20260816
```

This experiment increases confidence that the incumbent has a wide attraction
funnel in the frozen-boundary stratum.  It cannot rule out an asymmetric,
remote, or non-boundary-fixed improvement; the exact incumbent-D4-incidence
bracket is a separate result.
