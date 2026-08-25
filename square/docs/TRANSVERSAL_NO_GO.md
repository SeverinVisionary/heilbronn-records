# Exact transversal no-go around the incumbent

## Statement

Let `P` be the Comellas--Yebra 12-point configuration, and modify the locations
of any subset `S` of at most three of its labelled points while leaving the
other points fixed.  The resulting configuration cannot have minimum triangle
area strictly greater than the incumbent value.

This holds globally for the moved points: they may be placed anywhere in the
unit square, not merely in a local neighborhood of `P`.

## Proof

`incumbent.py` evaluates all 220 triangle areas exactly in the cubic field and
finds 20 triangles attaining the incumbent minimum.  A set of moved point
labels can affect every one of those pre-existing minimum triangles only if it
is a hitting set (transversal) of this active 3-uniform hypergraph.

Exact enumeration gives:

```text
no hitting set of sizes 0, 1, 2, or 3;
the unique size-4 hitting set is {8, 9, 10, 11}.
```

Therefore, for every `|S| <= 3`, at least one active incumbent triangle has no
vertex in `S`.  That triangle is unchanged by the modification and retains
area exactly equal to the incumbent.  The new configuration's minimum area is
at most that unchanged area, proving the claim.

## Consequence

An exactly four-label strict improvement must move all four interior points,
because they are the unique size-4 transversal.  A strict improvement that
moves five or more labels need only be another transversal and can have a
different pattern.  This justifies treating the frozen-boundary,
four-interior-point stratum as the first nontrivial four-label escape problem,
not as an exhaustive local search.

Run the exact enumeration with:

```sh
cd research/heilbronn_n12
python3 incumbent.py
```
