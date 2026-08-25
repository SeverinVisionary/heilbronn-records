# Structure of the minimal rigid cores — 2026-08-20

Exact computations implementing ranks 1, 3, 4 of the post-review program
([PROFESSOR_REVIEW_2026-08-20_RIGIDITY.md](PROFESSOR_REVIEW_2026-08-20_RIGIDITY.md)).
Driver: [rigidity_structure.py](rigidity_structure.py) (6 s, exact; full
output reproduced by running it). Triangle indices refer to the
lexicographic active list; orbits are the D4 orbits of sizes (4, 8, 8)
in `active_structure()` order.

## Rank 1 — stress uniqueness

- The size-17 core class: stress-space dimension **1** — the strict
  stress is unique up to positive scaling. This is the stress the
  certified-radius step should use.
- Both size-18 classes: stress-space dimension 2 (a stress *cone*, not a
  ray).

## Rank 3 — the forced motif is the whole middle orbit

- The intersection of all fourteen minimal cores is exactly the eight
  orbit-1 triangles `{1, 2, 5, 6, 8, 9, 11, 12}` — signature (0, 8, 0):
  the (0,4,8)-type family. Every orbit-1 triangle lies in **all 14**
  cores; every orbit-0 and orbit-2 triangle lies in exactly 11 of 14.
- The professor's conjectured "3-5 triangle seed" does not exist as a
  smaller motif: the forced set is the full orbit-1 octet.
- **Core hitting number = 1**: removing any single orbit-1 triangle
  destroys every minimal core simultaneously (witness: triangle 1), and
  consistently, the scan's size-19 census shows exactly those eight
  single drops as NONRIGID.

## Rank 4 — the emerging flexes

For each of the eight orbit-1 single drops, the exact NONRIGID witness of
the remaining 19 triangles is a first-order flex that moves **all twelve
points** (sign patterns printed by the driver; no flex is localized).
Every orbit-0 or orbit-2 single drop leaves a RIGID 19-subsystem. So the
picture is clean: orbit 1 carries the rigidity — each of its triangles is
individually load-bearing — while orbits 0 and 2 are individually
redundant but not jointly (no 16-subset is rigid, and each core still
needs 9-10 of them).

## Consequences for the paper

- The minimal-core theorem gains a structural corollary: *a subset of the
  active triangles is contained in some rigid core only if it contains
  all of orbit 1; conversely each minimal core is orbit 1 plus 9-10
  triangles from orbits 0 and 2 in one of three D4-patterns.*
- The unique size-17 stress ray is the canonical certificate object for
  the isolation-radius step.
- The flex sign-patterns are the raw material for the professor's
  requested flex diagram ("more valuable than 100 pages of
  certificates").

Scope: all statements are first-order and at the incumbent; nothing here
is a local-optimality or global claim.

Prior art: the positive-stress certificate itself goes back to Comellas &
Yebra 2002 §2.2 (for `H₈`, `H₁₀`); the structure results above have no
precedent found in the 2026-08-21 global sweep, and they answer — at the
`n = 12` incumbent — the LICQ and "structural rigidity" questions raised in
arXiv:2603.11107v2 §6. See
[NOVELTY_GLOBAL_2026-08-20.md](NOVELTY_GLOBAL_2026-08-20.md).
