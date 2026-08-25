# Size-5 transversal discovery stream — 2026-08-16

## Scope

The active hypergraph of the incumbent has three D4 orbits of size-5 hitting
sets.  `transversal_search.py` runs one edge-locked representative of each:

| Name | Moved labels | Variables |
|---|---|---:|
| `four-interiors-plus-boundary` | `{0,8,9,10,11}` | 9 |
| `two-boundary-three-interior-a` | `{0,2,8,10,11}` | 8 |
| `two-boundary-three-interior-b` | `{0,5,9,10,11}` | 8 |

The seven-point complement remains exactly fixed at the incumbent.  Moved
boundary labels remain on their original edge; moved interiors are free in the
square.  These are discovery strata, not a claim about all size-5 changes, and
not a global search over twelve free points.

## Candidate discipline

Every printed score keeps the coordinates that attained that score, records the
number of nearly active triangles, and computes unlabeled bottleneck distance to
the incumbent modulo D4.  A score above the incumbent is still exploratory: it
must survive exact rational or interval verification before it can be a result.

Run a small deterministic pass with:

```sh
cd research/heilbronn_n12
python3 transversal_search.py --seed-limit 1
```

The planned rigorous follow-up is an exact interval branch-and-bound over each
named parameter box.  Its results must be reported only after every remaining
box has a replayable rational witness triangle; numerical discovery does not
substitute for that certificate.

`transversal_interval.py` is the exact `Fraction` interval engine for that
follow-up.  Its default finite box budget is deliberately labelled
`INCOMPLETE`; only a run that empties its pending queue can be a cover.

## First deterministic pass

With the four seeds `2026081601`--`2026081604`, all three strata either returned
to the incumbent orbit or converged to a markedly weaker distinct configuration.
No score exceeded the incumbent float evaluation.

| Stratum | Incumbent-orbit returns | Distinct lower results | Best observed gap |
|---|---:|---:|---:|
| `four-interiors-plus-boundary` | 2 / 4 | 2 / 4 | `-3.747e-16` |
| `two-boundary-three-interior-a` | 3 / 4 | 1 / 4 | `-6.245e-17` |
| `two-boundary-three-interior-b` | 4 / 4 | 0 / 4 | `-6.939e-17` |

The near-zero negative gaps are ordinary floating-point polish error.  The
lower distinct results range from approximately `0.0208` to `0.0266`; they are
not near-record candidates.  This small campaign is a diagnostic, not a
coverage claim.
