# Exact no-go: inserting a 12th point into the Goldberg `n=11` configuration

## Result

Let `P` be the rational 11-point unit-square configuration whose least triangle area is `1/27`.  Among all points `u` in the unit square, the largest possible least area of a triangle in `P ∪ {u}` is

```
1/54
```

It is attained at `u = (1/2, 1/9)`.  Since

```
1/54 < 0.032598858691819698...,
```

this entire "best known 11 points plus one inserted point" family cannot improve the Comellas--Yebra 12-point record.

## Exact finite proof

For every pair `p_i, p_j` in `P`, twice the signed area of the triangle `(p_i, p_j, u)` is an affine rational function

```
D_ij(u_x, u_y).
```

The 55 zero lines `D_ij = 0` partition the square into sign cells.  On a fixed closed cell, maximizing the new least double area `s` is the rational linear program

```
maximize s
subject to sign(D_ij) * D_ij(u) >= s  for all 55 pairs,
           0 <= u_x, u_y <= 1,  s >= 0.
```

Each feasible program is bounded and therefore has an optimal basic feasible solution.  Every such vertex is the intersection of three rank-independent constraints selected from the 110 signed area constraints, four square bounds, and `s = 0`.

`n11_insertion.py` enumerates all `C(115,3) = 246,905` possible bases, solves each nonsingular one with exact `Fraction` Cramer's rule, and checks feasibility directly against all 55 absolute-area inequalities.  It finds 232,134 nonsingular bases and the exact optimum

```
u = (1/2, 1/9),  s = 1/27.
```

The pre-existing 11-point triangles have minimum `1/27`, while all new triangle areas are `|D_ij|/2`; hence the full 12-point minimum is `min(1/27, s/2) = 1/54`.

The code uses no numerical LP solver, tolerances, or rounded coordinates.  This result is a rigorous restricted-family no-go lemma, not a global upper bound for the 12-point Heilbronn problem.
