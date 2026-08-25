# Prior-art gate: 12-point Heilbronn problem in the unit square

**Audit date:** 2026-08-19. **Re-audited 2026-08-21** with a global sweep that
includes non-Scholar venues (DataCite/Zenodo/OSF/HAL/viXra) and the
LLM-discovery literature: [NOVELTY_GLOBAL_2026-08-20.md](NOVELTY_GLOBAL_2026-08-20.md).
Record unchanged; one mandatory citation added (Comellas-Yebra 2002 §2.2 is the
origin of the positive-stress local-maximality certificate used by the rigidity
milestone).

**Domain:** twelve points in the unit square `[0,1]^2`; triangle areas are
ordinary Euclidean areas. This is not the unit-triangle, unit-disc, or
arbitrary-convex-region variant.

## Current best-known construction

The maintained record table is Erich Friedman's
[Heilbronn Problem for Squares](https://erich-friedman.github.io/packing/heilbronn/),
whose index was updated on 2026-08-03. Its `n=12` entry says, verbatim:

> “A = .03260+ Found by F. Comellas and J. Yebra in December 2001.”

The independently maintained 2026 survey and certification paper by
Sudermann-Merx,
[arXiv:2603.11107v2](https://arxiv.org/html/2603.11107v2), states in Section
1.4, verbatim:

> “their configurations for n=10 and n=12 remain the best known to date.”

These sources agree. No contradictory newer `n=12` unit-square construction
was found in the forward check performed on the audit date. The live target is
therefore still the Comellas--Yebra construction, not a value derived locally
from an upper-bound theorem.

## Frozen exact target used by this repository

The source construction is F. Comellas and J. Yebra,
[“New Lower Bounds for Heilbronn Numbers”](https://www.combinatorics.org/ojs/index.php/eljc/article/view/v9i1r6)
(Electronic Journal of Combinatorics 9 (2002), R6).

The repository reconstructs its coordinates exactly in `incumbent.py`. If `x`
is the root in `(0,1/4)` of

```text
4*x^3 - 12*x^2 + 10*x - 1 = 0,
```

and `y = 2*x^2 - 3*x + 1/2`, the minimum triangle area is

```text
x/4 + x*y/2 - x^2/2
= 0.032598858691819698...
```

The area itself is the positive real root of

```text
64*z^3 + 80*z^2 + 28*z - 1 = 0.
```

This exact algebraic value is the strict comparison target for candidate
certification. A rounded decimal at or above `.03260` is not evidence of an
improvement.

## Novelty and completion boundary

- Reproducing the incumbent, its exact algebraic description, or its active
  triangles is prior art or validation infrastructure, not a new record.
- Restricted-family no-go results and local-optimality certificates do not
  solve the unrestricted `n=12` problem.
- A record claim requires one exact or interval-certified twelve-point
  configuration whose minimum over all 220 triangles is strictly above the
  frozen algebraic target.
- A global resolution requires a complete proof over arbitrary configurations;
  finite branch-and-bound queues and numerical optimizer failures do not count.
