# Calibration gate — 2026-08-16

## Purpose

Before applying a heuristic optimizer to `n=12`, it must rediscover lower-`n`
benchmarks with no published coordinates supplied as starting points.  The
objective is the actual minimum of all triangle areas; the final local step
uses a sign-fixed epigraph NLP only after differential evolution has selected
an orientation cell.

The templates use boundary incidences and symmetries reported for the known
solutions, not their coordinate values:

| Case | Template | Dimension | Target | Required hits |
|---|---|---:|---:|---:|
| `n=8` | C2, six boundary points + interior pair | 4 | 0.072376424318444 | 2 / 3 |
| `n=9` | anti-diagonal reflection, eight boundary points + fixed-axis point | 5 | 0.054875999170897 | 2 / 4 |
| `n=10` | C2, eight boundary points + interior pair | 6 | 0.046537419582542 | 3 / 4 |

The command is deterministic for the pinned NumPy/SciPy versions:

```sh
cd research/heilbronn_n12
python3 calibration.py
```

## Observed seeded runs

| Case | Seeds reaching the target | Result |
|---|---:|---|
| `n=8` | 20260816, 20260817, 20260818 | PASS (3 / 3) |
| `n=9` | 20260817, 20260818 | PASS (2 / 4) |
| `n=10` | 20260817, 20260818, 20260819 | PASS (3 / 4) |

Earlier free 16-variable `n=8` and 10-variable boundary-only `n=9` experiments
motivated the structured templates, but their code and outputs were not archived
in this package.  They are therefore not reproducible calibration evidence;
the reproducible record begins with the seeded structured gate above.  The
templates remain a deliberate prerequisite for the first `n=12` campaigns.

Passing this gate validates only basin recovery under the supplied structural
families.  It is not an optimality proof and does not authorize a claim that a
later `n=12` heuristic candidate is a record without exact rational
certification.
