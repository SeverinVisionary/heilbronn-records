# C2 boundary-incidence search — 2026-08-17

## Scope

`c2_boundary_search.py` explores an eight-parameter family that preserves the
record's boundary incidence while allowing a half-turn symmetry only:

- two bottom seeds and their top half-turn images;
- two left seeds and their right half-turn images;
- two free interior seeds and their opposite partners.

It contains the Comellas--Yebra configuration exactly, but it is a distinct
boundary-incidence stratum.  It does **not** cover all C2-symmetric point sets,
the full C4 family, or arbitrary 12-point configurations.

Differential evolution receives no incumbent coordinates.  Its selected sign
cell is polished with the same epigraph SLSQP check used in the C4 campaign.
Every reported result is then dyadically rounded and checked with the exact
`Fraction` verifier.  This is discovery work only, not an upper-bound or
no-improvement certificate.

## Campaign

The reproducible campaign used seeds `2026081723`–`2026081726`, population
size 32, and at most 4,000 differential-evolution iterations per seed.  The
published record is `0.032598858691819698...`.

| Seed | Polished least area | Gap to record | Active triangles | 30-bit snap beats record? |
|---:|---:|---:|---:|---|
| 2026081723 | 0.029843788128357501 | -0.002755071 | 18 | no |
| 2026081724 | 0.031838473155266556 | -0.000760386 | 20 | no |
| 2026081725 | 0.030536470436816648 | -0.002062388 | 24 | no |
| 2026081726 | 0.028470243576449214 | -0.004128615 | 20 | no |

The best trial, seed `2026081724`, is still below the record.  Its exact
30-bit dyadic snap has least area

```
9176815033069345 / 288230376151711744
```

and `strictly_beats_incumbent=False`.  No improved configuration was found or
certified by this campaign.

A fresh same-budget follow-up over seeds `2026081727`–`2026081730` also found
no improvement: its best polished score was `0.029843788128357515`, and all
four 30-bit dyadic audits returned `strictly_beats_incumbent=False`.  Across
the eight recorded independent seeds, the best result therefore remains seed
`2026081724` from the table above.

## Reproduction

```sh
cd research/heilbronn_n12

# Fast one-seed smoke search with exact snap audit.
python3 c2_boundary_search.py --seed-limit 1 --popsize 16 --maxiter 1200 --snap-bits 30

# Recorded four-seed campaign.
python3 c2_boundary_search.py --popsize 32 --maxiter 4000 --snap-bits 30
```
