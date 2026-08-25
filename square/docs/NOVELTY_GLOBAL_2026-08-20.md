# Global novelty sweep — 2026-08-20/21

Second prior-art gate for this campaign, run *after* the rigidity milestone and
deliberately extended past Google Scholar into DOI-registered gray literature
(Zenodo, figshare, OSF, Dryad via DataCite), preprint servers outside arXiv,
and the LLM/evolutionary-discovery literature. It supplements — and in one
place corrects the emphasis of — [PRIOR_ART.md](PRIOR_ART.md).

**Addendum 2026-08-21:** this sweep did not cover code-hosting platforms, which
turned out to hold the most active Heilbronn work of the last six weeks. See
[NOVELTY_REPOS_2026-08-21.md](NOVELTY_REPOS_2026-08-21.md) — the rigidity
contribution survives, but `exact_ascent` is downgraded to tooling and
exactification is contested.

Two questions are audited separately:

- **R (record).** Has anyone published a twelve-point unit-square configuration
  above the frozen algebraic target `0.032598858691819698...`?
- **M (method).** Has anyone published a rigidity / active-set / stress
  analysis of a Heilbronn configuration — in any domain, for any `n`?

## Indexes queried (all on 2026-08-20/21)

| Index | Query | Hits reviewed |
|---|---|---|
| OpenAlex | `search=heilbronn triangle`, date-sorted | 933 works, newest 50 read |
| DataCite (Zenodo, figshare, OSF, Dryad, arXiv DOIs) | exact phrase `"Heilbronn triangle"` | 15 records — **all** read |
| Zenodo native API | `title:(Heilbronn)`; phrase `"Heilbronn triangle"` | 16 + 2 |
| Crossref | bibliographic `Heilbronn triangle problem` | 40 |
| DBLP | `heilbronn` | 71 |
| HAL | `Heilbronn triangle` | 2 |
| OSF preprints API | `filter[title]=Heilbronn` | 0 |
| viXra | site search | 1 (2406.0086, disk upper bound) |
| Web search | record/rigidity/local-optimality phrasings, `site:` sweeps of preprints.org, TechRxiv, Research Square | ~10 queries |
| Erich Friedman, *Heilbronn Problem for Squares* | refetched 2026-08-21 | n=12 entry unchanged |
| erdosproblems.com #507 | refetched 2026-08-21 | disk variant, asymptotic only; page last edited 2025-12-30 |

arXiv's own API rate-limited every request during this sweep; arXiv coverage
came through OpenAlex, DataCite (arXiv DOIs) and direct fetches of the
individual papers below.

## R — the record is unchanged

- Friedman's maintained table still reads `A = .03260+ Found by F. Comellas and
  J. Yebra in December 2001` for `n = 12`.
- Sudermann-Merx, [arXiv:2603.11107v2](https://arxiv.org/abs/2603.11107)
  (unit square, MINLP + exact coordinates, certified optimal for `n ≤ 9`):
  “their configurations for n=10 and n=12 remain the best known to date.”
  Appendix A lists `Δ₁₂ ≥ ¼x + ½xy − ½x² ≈ 0.03260`, i.e. our frozen target.
- **The AI-discovery wave did not touch the square records.** Georgiev,
  Gómez-Serrano, Tao, Wagner, *Mathematical exploration and discovery at
  scale*, [arXiv:2511.02864](https://arxiv.org/abs/2511.02864) §29, report of
  their AlphaEvolve campaign over many `(n, K)` pairs: “AlphaEvolve did not
  manage to beat any of the records where `K` is the unit square.” Their
  Heilbronn improvements are in *other variants*: `n = 11` in the unit-area
  **equilateral triangle** (`≥ 0.0365`), and `n = 13, 14` for the
  **arbitrary convex hull** variant (`≥ 0.0309`, `≥ 0.0278`).
- GigaEvo, [arXiv:2511.17592](https://arxiv.org/abs/2511.17592), reproduces
  that same unit-triangle `n = 11` result (0.0364). Not the square.
- FlowBoost, [arXiv:2601.18005](https://arxiv.org/abs/2601.18005), runs the
  unit square at `n = 13` (0.0259285) and `n = 15` (0.0187494) — both below the
  best-known 0.0270 / 0.0211 it cites. No `n = 11`, `12`, no record.
- Berthold–Kamp–Mexi–Pokutta–Pólik,
  [arXiv:2601.05943](https://arxiv.org/abs/2601.05943) (solvers vs. AlphaEvolve
  benchmarks): zero occurrences of “Heilbronn” in the full text.
- Monji–Modir–Kocuk, [arXiv:2512.14505](https://arxiv.org/abs/2512.14505):
  unit square, `n = 8, 9` only.
- Sudermann-Merx, [arXiv:2607.15021](https://arxiv.org/abs/2607.15021)
  (2026-07): unit **right triangle**, `n ≤ 8`. Not the square, no `n = 12`.
- Qi–Dehbi–Liu–Yang–Zeng, *J. Syst. Sci. Complex.* 38 (2025) 2252–2271: a
  different “Heilbronn problem of convex polygons” (equal consecutive-vertex
  triangle areas, `n = 10` decagon). Unrelated to the square variant.

### Gray literature: one live Heilbronn deposit, and it is the disk

DataCite's exact-phrase index returns exactly one non-arXiv research artifact
family: T. Alexander Lystad, *Heilbronn triangle problem (Erdős #507):
exact-certified unit-disk configurations*, Zenodo, 2026-08-01 —
[v1.1 n=5..40](https://doi.org/10.5281/zenodo.21739767),
[v1.2 n=5..48](https://doi.org/10.5281/zenodo.21751173). It is the **unit
disk**, a dataset of constructions (lower bounds) with a standard-library
verifier, self-described as “the first public exact-certified table for the
disk variant”, referencing Friedman's square table only as a baseline. No
square configurations, no `n = 12` square claim, no rigidity content. It is
*not* in Google Scholar; it was reached only through DataCite/OpenAlex — which
is precisely why this sweep was run.

Nothing on OSF, HAL, viXra, preprints.org, TechRxiv or Research Square claims a
square `n = 12` construction.

**R verdict: cleared.** The frozen target stands; no configuration above
`0.032598858691819698...` exists in any indexed venue, formal or gray.

## M — the method audit, including one credit we owe

### The precedent inside the incumbent's own paper

Comellas & Yebra, *New lower bounds for Heilbronn numbers*, Electron. J.
Combin. 9 (2002) #R6, §2.2 “The local optimization procedure”, already state
and use the first-order condition for a max-min of smooth functions: at a point
where `f₁ = ⋯ = f_{k+1}` are tied, a necessary condition for a local maximum is
a linear dependence `Σ cᵢ ∇fᵢ = 0` with `cᵢ ≥ 0`, and they note that requiring
the combination to have *strictly positive* coefficients is what makes the
point a genuine (in their words, “in a certain sense”) stationary point. They
exhibit such positive combinations explicitly for `H₈` (four tied areas) and
`H₁₀` (three tied areas, with `S₄` deliberately excluded because including it
destroys positivity).

So **the stress-certificate idea for Heilbronn is prior art from 2002, in the
very paper that produced our incumbent.** Any write-up of ours that presents
“a positive combination of active-area gradients certifies first-order local
maximality” as new would be wrong. Three qualifications, all verified against
the paper's own text:

1. Their theorem is cited to reference [5], *F. Comellas and J.L.A. Yebra, “An
   optimization problem”, manuscript* — an unpublished manuscript. The result
   itself is the standard nonsmooth first-order condition; the paper contains
   no proof and no rank or constraint-qualification discussion.
2. They apply it in a **2–3 parameter symmetric ansatz**, not in the full
   configuration space, and **boundary contacts are built into the ansatz**
   rather than treated as active constraints with their own multipliers.
3. For `n = 12` they give only the parametrisation and the value —
   `x = 0.115354`, `y = 2x²−3x+½`, `H₁₂ ≥ ¼x + ½xy − ½x² = 0.032599` — and
   **no certificate at all**. Their own summary is that the method “gives us
   confidence that very likely these values are optimal”, not a proof.

### The open question our milestone actually answers

Sudermann-Merx (2603.11107v2) closes §6 with two remarks that are, in effect, a
request for exactly the analysis we performed:

- Remark 9: “we do not know whether LICQ holds for optimal Heilbronn
  configurations.”
- §6.2 observes clustered noncritical area levels and says this “suggests a
  structural rigidity in the extremal configurations that goes beyond the
  optimality of the minimum area.”

At our `n = 12` incumbent the counting alone settles the constraint
qualification: 20 active area constraints plus 8 boundary contacts is 28 active
gradients in 24 coordinates (25 with the epigraph variable `t`), so LICQ fails
at the incumbent — and the interesting content is *how* it fails, which is the
minimal-core census: which subfamilies of the active set still pin the
configuration. That is the framing the paper should use.

### No rigidity treatment of Heilbronn exists

Across all indexes above, no paper — formal or gray, any `n`, any domain —
applies infinitesimal rigidity, equilibrium stresses, Stiemke/Gordan
alternatives, or minimal-rigid-subsystem enumeration to a Heilbronn
configuration. The words “rigidity”/“rigid” appear in this literature only in
Sudermann-Merx's informal §6.2 sense quoted above.

### Method-family prior art to cite (packing, not Heilbronn)

The technique is a transfer of a well-established packing tradition, and the
paper must position it as such:

- **Danzerian rigidity** for circle packings (Danzer; symmetry treatment by
  Fowler & Guest), where a rigidity computation confirms local optimality.
- **Irreducible contact graphs**: Musin & Tarasov's solution of the Tammes
  problem (`N = 13, 14`) and their flat-torus packing work enumerate *rigid,
  irreducible* contact graphs — the closest structural analogue to our minimal
  rigid cores.
- **Connelly**'s rigidity of packings (including flexible radii), where
  stresses assert local maximality.

The difference to state plainly: those objects are pairwise-distance **contact
graphs**; ours is a 3-uniform **area hypergraph** of unsigned determinants,
plus one-sided boundary contacts, and the certificates are decided in exact
algebraic arithmetic rather than numerically.

## Net effect on our claims

| Claim | Status after this sweep |
|---|---|
| n=12 record improvement | Not claimed. Incumbent is prior art; target unchanged. |
| Positive-stress certificate for a Heilbronn local max | **Prior art (Comellas–Yebra 2002 §2.2)** — must be cited, not claimed. |
| Full-dimensional active set incl. 8 boundary normals, exact two-sided decisions | No precedent found. |
| Certificate-classification of all 6,196 subsets; 3 D4-classes / 14 minimal rigid cores (17/18/18) | No precedent found. |
| Stress uniqueness at size 17; core intersection = the orbit-1 octet; hitting number 1; the eight global flexes | No precedent found. |
| Answering the LICQ/“structural rigidity” questions of 2603.11107v2 at n=12 | Open in the literature as of 2026-08-21. |

**Gate verdict: cleared, with one mandatory citation change** — every write-up
of the rigidity milestone must credit Comellas–Yebra §2.2 for the
positive-combination certificate and scope our contribution to the
full-dimensional, exact, subset-level census and its structure theorem.
