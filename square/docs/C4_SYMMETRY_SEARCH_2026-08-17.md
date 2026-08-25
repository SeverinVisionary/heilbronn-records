# C4 symmetry-breaking search — 2026-08-17

## Scope

This is a numerical exploration of the six-parameter family formed by three
four-point orbits under 90-degree rotation about the centre of the unit square.
It contains the Comellas--Yebra record, but it is larger than the earlier
two-parameter D4 incidence family because no reflection is imposed. It is not
a global C4 certificate and says nothing directly about asymmetric
configurations.

`c4_symmetry_search.py` uses three seed points `(a_r, b_r)`. Each produces

```text
(a_r, b_r), (1-b_r, a_r), (1-a_r, 1-b_r), (b_r, 1-a_r).
```

The record is represented by the seeds

```text
(x, 0), (1-x, 0), (1/2, y),
```

with the published cubic-field coordinates. A sign-fixed epigraph polish at
those values reproduces `0.032598858691819665` without moving the parameters.

## Recorded blind pass

```sh
python3 c4_symmetry_search.py --popsize 32 --maxiter 4000 --snap-bits 30
```

The four recorded seeds `2026081702` through `2026081705` all polished to the
same C4 basin, up to orbit order and rotation:

```text
minimum area = 0.030612244897959... = 3/98
gap to record = -0.001986613793860...
```

One exact representative uses seed points

```text
(5/7, 2/7), (6/7, 1), (6/7, 0),
```

and the existing exact `Fraction` verifier confirms its least triangle area is
exactly `3/98`. The 30-bit dyadic snaps of the floating results were also
non-improving. Thus this is a reproducible alternate local basin, not a record
candidate.

## Consequence

The pass neither proves C4 optimality nor rules out a reflection-breaking
improvement. Its value is that the search now covers a concrete six-dimensional
symmetry class beyond the D4 certificate, with an exact audit boundary for any
future candidate.
