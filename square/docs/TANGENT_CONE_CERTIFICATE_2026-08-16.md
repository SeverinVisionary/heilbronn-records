# Exact first-order tangent-cone obstruction — 2026-08-16

## Statement

At the Comellas--Yebra configuration, every nonzero feasible first-order
velocity strictly decreases at least one of the 20 incumbent-active unsigned
triangle areas.

Consequently, the incumbent has a trivial active critical cone and is locally
isolated against all unit-square coordinate perturbations.  This is not a
global upper bound: a remote or different-incidence configuration can still
beat it.

## Exact certificate

Let the three D4 active-triangle orbits have sizes `(4, 8, 8)`, in the order
returned by `incumbent.active_structure()`.  Give each triangle in these orbits
the following positive weights, respectively:

```text
w0 = -4 + 44*x - 28*x^2 = 0.702986082060836941...
w1 =  3 - 14*x +  8*x^2 = 1.491498515295926170...
w2 = 1.
```

`tangent_certificate.py` differentiates every active unsigned triangle area
exactly in `Q(x)` and sums the gradients with those weights.  The resulting
gradient vanishes in all 16 interior/free or boundary-tangential coordinates.
For each of the eight inward boundary-normal directions, it equals

```text
-4 + 34*x - 22*x^2 = -0.370713120026876284...
```

which is strictly negative by the same rational root-isolation machinery used
for the incumbent.

For every feasible tangent velocity `v`, write `D_i(v)` for the derivative of
the `i`th active unsigned area.  The weighted derivative is

```text
W(v) = sum_i w_i D_i(v) = N * (sum of the eight inward normal components),
```

where `N = -4 + 34*x - 22*x^2 < 0`.  Feasibility makes each inward normal
component nonnegative, so `W(v) <= 0`.

Now take `v` in the active critical cone, namely assume **all** twenty
derivatives satisfy `D_i(v) >= 0`.  Positivity of every `w_i` gives `W(v) >=
0`; hence `W(v) = 0`.  Since `N < 0`, every inward normal component is zero,
and since every weight is positive, every active derivative is also zero.  On
the remaining 16 tangential and interior coordinates, the code takes the exact
determinant of a fixed 16-by-16 submatrix of active gradients:

```text
-89/2^21 + (419/2^20)*x - (9/2^15)*x^2
= 0.000000000933174599164018028... > 0.
```

The active derivative equations therefore have only the zero solution.  Thus
the active critical cone is trivial: every nonzero feasible velocity has at
least one active derivative strictly negative.  The standard compactness/Taylor
argument then yields a strict local isolation neighborhood, although this
script deliberately does not try to optimize or publish an explicit radius.

Run the exact check with:

```sh
cd research/heilbronn_n12
python3 tangent_certificate.py
```

## Consequence for the live research program

There are no nonzero neutral first-order directions to test at second order.
The next search stages are therefore necessarily nonlocal, beginning with the
three size-5 active-hypergraph support classes.  This certificate does not
prune those larger finite moves.
