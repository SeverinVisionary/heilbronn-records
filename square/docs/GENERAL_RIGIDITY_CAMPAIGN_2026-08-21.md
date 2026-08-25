# Campaign: certificate-guided attack on the Heilbronn record landscape

**Opened 2026-08-21.** Supersedes the n=12-only record chase as the primary
program. Approved by the operator after the [global novelty
sweep](NOVELTY_GLOBAL_2026-08-20.md) and the ~3% estimate for improving n=12.

## Thesis

Stop using search to find records. Use exact rigidity certificates to find
**weak incumbents**, and spend search only where a certificate says an
incumbent is soft. Every best-known configuration falls into one of three
audit classes:

| Class | Certificate outcome | Action |
|---|---|---|
| **A. float-only** | no exact form published | exactify via the active-set system; the polish either reproduces the decimals or strictly improves them |
| **B. flexible** | exact first-order flex exists (NONRIGID) | certificate-guided ascent along the flex with second-order control — search *with a warrant* |
| **C. rigid** | strict stress + full rank | do not attack; certify the isolation radius and bank a theorem |

n=12 is class C — which is why it resisted, and why the compute spent on it
bought an instrument rather than a record.

## Why this is methodologically new

No Heilbronn paper applies rigidity certificates to configurations at all
(established in the novelty sweep; the only precedent is Comellas-Yebra 2002
§2.2, a positive-gradient combination in a 2-3 parameter ansatz for `H₈`/`H₁₀`).
The nearest working analogue is packing: Danzerian rigidity, Connelly's
stresses, and Musin-Tarasov's enumeration of *irreducible contact graphs*,
which is how Tammes `N = 13, 14` fell. This campaign transfers that programme
from pairwise-distance contact graphs to 3-uniform **area hypergraphs** with
one-sided domain contacts, in exact arithmetic.

## Engine generalization (the actual work)

`rigidity_core.py` is hardwired to the n=12 five-boundary normal form. Three
axes must open up, and the certificate logic itself needs no change:

1. **Any `n`.** Nothing in the resolver depends on 12; only the coordinate
   layout tables do.
2. **Any convex domain.** Square, unit triangle, disk. Boundary contacts stop
   being axis-aligned coordinate pins and become general inward normals:
   an interior point contributes 2 free directions, an edge point 1 tangential
   direction and 1 inward normal, a **corner** point 2 inward normals (the
   n=12 model forbids corners; other incumbents have them, e.g. the n=8
   square configuration sits on `(0,0)` and `(1,1)`). The disk contributes a
   non-axis-aligned inward radial normal.
3. **Any coordinate field.** Rational (the whole disk table, square n=6 and
   n=11), quadratic (`√13`, `√65`), cubic (n=7, n=10, n=12), and float-only
   incumbents that must first be exactified.

### Simplification found while planning

The free/inward coordinate split in `rigidity_core` is a normal-form artifact.
The general and cleaner criterion is stated directly on the full constraint
matrix `M` (rows = active area gradients of `H`, plus active inward normals;
columns = all `2n` coordinates):

```
C(H) = {v : Mv >= 0} = {0}   <=>   ker(M) = {0}  and  exists y > 0 with M^T y = 0
```

the second half being Stiemke's alternative. This is exactly the logic the
HEAVY panel audited for n=12, restated without any coordinate bookkeeping, so
the generalization *removes* incumbent-specific structure rather than adding
special cases.

### Architecture

- `exact_field.py` — exact arithmetic over `Q` and over `Q(α)` for an arbitrary
  minimal polynomial with an isolating interval; sign by interval refinement.
- `heilbronn_configs.py` — the audited configuration registry: `n`, domain,
  exact coordinates, published value, source citation, prior-art date.
- `rigidity_engine.py` — field- and domain-generic classification and census.
  `rigidity_core.py` stays frozen as the n=12 reference implementation.
- **Equivalence gate:** the engine, run on the n=12 incumbent, must reproduce
  `rigidity_core`'s verdicts exactly — 14 minimal cores, sizes 17/18/18, the
  three normalized margins. The generalization is validated against an audited
  artifact, not trusted.
- **Negative controls with known answers:** square `n = 6` (optimum belongs to
  an infinite family, so the engine *must* return NONRIGID with an explicit
  flex) and `n = 3, 4` (trivial families).

## Target inventory

| Tier | Targets | Field | Why soft |
|---|---|---|---|
| 1 | Unit disk `n = 5..48` (Zenodo DISK_TABLE v1.2, 2026-08-01) | rational | rows self-labelled "candidate"; `n = 27, 28` published *below* the transported square value |
| 2 | Square `n = 13..16` (Cantrell's numerical candidates) | float-only | never exactified, never audited |
| 3 | Unit triangle / convex-hull variants | mixed | AlphaEvolve moved `n = 11` (triangle) and `n = 13, 14` (hull) in 2025 — this tier still moves |
| 4 | Square `n = 5..12` | exact algebraic | audit for the record; `n = 11` (Goldberg 1972, rational) is the only pre-2001 survivor and has never been audited |
| 5 | Square `n = 10, 12` | cubic | already class C / expected class C — theorem lane |

## Execution order

1. `exact_field.py` + `rigidity_engine.py` + equivalence gate + negative controls.
2. **Square `n = 11` (Goldberg, rational).** Cheapest real audit, oldest
   surviving record, exact coordinates already published.
3. Square `n = 5..10` audit → the first rigidity table of the square record
   landscape, plus the empirical answer to arXiv:2603.11107v2's question about
   how many critical triangles an optimal configuration must have.
4. Disk table sweep (cloud; embarrassingly parallel over 44 rows).
5. Class-A exactification for square `n = 13..16`.
6. Flagship theorem in parallel: the n=12 isolation radius.

## Gates that do not bend

- **Per-variant prior-art gate before any claim.** The disk baseline is three
  weeks old and may be updated by its depositor; the square table is
  maintained. No improvement claim without a fresh gate on that specific
  `(n, domain)` and a verbatim source quote.
- **Certificates stay exact.** Float LP proposes; exact arithmetic decides.
  A float-only incumbent is exactified *before* it is audited, never audited
  numerically.
- **Improvements are claimed only after an exact strict comparison** against
  the frozen published value for that row, in that row's own domain
  normalization.
- Heavy sweeps run in cloud sessions per [CLOUD_JOB.md](CLOUD_JOB.md).
- Milestone reviews (HEAVY panel + professor) fire at: engine validated, first
  audit table complete, first improvement candidate.
