# Rigorous D4-family bracket — 2026-08-16

## Statement

Consider the complete two-parameter D4 incidence family containing the
Comellas--Yebra construction:

```text
boundary: (x,0), (1-x,0), (x,1), (1-x,1),
          (0,x), (1,x), (0,1-x), (1,1-x)
interior: (1/2,y), (y,1/2), (1-y,1/2), (1/2,1-y).
```

Replacing `x` by `1-x`, or `y` by `1-y`, does not change the unlabeled point
set.  It is therefore enough to cover the complete parameter square
`(x,y) in [0,1/2]^2`.

The exact interval computation establishes

```text
0.032598858691819698218764006623515408... <= H_incidence
<= 0.032598858691819698218764833804127961...
```

where the lower bound is the Comellas--Yebra configuration itself.  The upper
endpoint is the rigorously enclosed incumbent value plus `2^-80`; its distance
above the exact incumbent is less than `2^-79`.  Thus any improvement within
this incidence family is smaller than `2^-79`, beyond the 24th decimal place.

This is a certified bracket for the stated incumbent orbit pattern.  It does
not cover every conceivable D4-symmetric 12-point pattern, does not assert
exact D4 optimality, and is not a global upper bound for unconstrained 12-point
configurations.

## Certificate method

`d4_interval_certificate.py` starts with the full square and recursively
bisects dyadic parameter boxes.  For every box it interval-evaluates the
signed determinant of all 220 triangles using only `Fraction` arithmetic.  If
the minimum of the 220 absolute-area upper bounds is no greater than the
target endpoint, the entire box is discarded.  Otherwise it is bisected along
its longer side.

At the recorded precision the exhaustive cover has:

| Quantity | Value |
|---|---:|
| root-isolation bisections | 192 |
| slack above record enclosure | `2^-80` |
| visited boxes | 1,843 |
| certified terminal boxes | 922 |
| maximum subdivision depth | 155 |

Every terminal box is individually certified below the stated rational upper
endpoint; all arithmetic, branching decisions, and coverage are exact.

Run it with:

```sh
cd research/heilbronn_n12
python3 d4_interval_certificate.py
```
