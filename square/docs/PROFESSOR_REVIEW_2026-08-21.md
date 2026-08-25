# Professor review of the campaign pivot — 2026-08-21 (third review)

## Provenance

- ChatGPT desktop, Pro tier, session `762d08eb-cb9b-49b3-a381-5d3cf287636f`.
- The CLI's reply capture failed again with the known DOM-bridge drift
  (`window.__cgpt.pinnedReply is not a function`; `chatgpt doctor` also reports
  `FAIL transcript root`), and `chatgpt recover` failed the same way.
  Generation had completed (no Stop control, single assistant unit); the reply
  was extracted by direct `chatgpt eval` after expanding two collapsed
  sections, 12,013 characters. Verbatim:
  [PROFESSOR_REVIEW_2026-08-21_verbatim.md](PROFESSOR_REVIEW_2026-08-21_verbatim.md).
  The character-for-character `verify` could not run; the extraction method is
  recorded in its place. This is the second consecutive run to hit this bug —
  it is now the expected path, not an anomaly.

## Headline

"The pivot is probably the best decision you made." But: "70% of the current
output is still data production." The publishable mathematics is concentrated
in the n=12 core theorem and the n=10 degeneracy phenomenon; the tables, the
exactification work and the record improvements are not the contribution.

Ranking delivered: (1) n=12 minimal-core theorem — **high**; (2) n=10
prestress stability — **high if framed correctly**; (3) n=12 isolation radius
— medium-high; (4) full rigidity table n=5..35 — medium, *only as supporting
evidence for a theorem*; (5) exactification n=13..35 — **low; "mostly
worthless unless needed"**; (6) the six improved disk rows — **low unless they
trigger theory**.

## The one substantive technical objection — and its resolution

The review rejected the n=10 write-up as stated:

> the feasible cone is not one-dimensional ... The kernel is only `Mv = 0`, not
> the entire cone.

It demanded an exact stress, the Hessian quadratic form on `ker(M)`, and a
proof that no first-order cone direction escapes, before the phrase *prestress
stable* could be used.

**All three were computed the same day, and the claim survives — upgraded:**

1. **The cone does collapse.** An exact strictly positive stress `y > 0` with
   `M^T y = 0` was found and verified for the full n=10 active system (24 rows,
   dimension 20, stress space dimension 5). With `y > 0`, any `v` with
   `Mv >= 0` satisfies `y^T M v = 0` and hence `Mv = 0`, so
   `C(H) = ker(M)` — exactly the single flex line. No cone direction escapes.
2. **The stress-weighted second-order form is exactly negative.**
   `Q = sum_e y_e D^2 A_e(v,v) = -109.241...` (normalized by the area stress
   weights, `-5.899...`), computed exactly in the cubic field.
3. **Hence a strict local maximum, for curves and not merely lines.** With
   `L(x) = sum_e y_e A_e(x) + sum_j y_j g_j(x)` one has `grad L(x*) = 0`, and
   the square's boundary constraints `g_j` are linear, so along any feasible
   curve the `t^2` coefficient of `L` is exactly `Q/2 < 0` — the curve's second
   derivative `w` drops out precisely because the stress annihilates the
   gradients. Since `min_e A_e <= L / sum_e y_e`, the minimum strictly
   decreases. This is the classical prestress-stability argument, so the term
   is now used in its proper sense with the definition stated.

This is the strongest statement available from the data, and it is the one the
review said would make the result "a serious theorem".

## Other findings and their disposition

| Finding | Disposition |
|---|---|
| "Audit" framing is bookkeeping; the mathematics is a theory of criticality/rigidity/degeneracy for max-min area configurations, with the audit as "the telescope" | Adopted — campaign doc to be reframed around the theory, not the sweep |
| The central theorem to aim for: *every isolated local maximum admits a positive active-triangle stress and contains a finite minimal rigid core; non-rigid optima are classified by the stress Hessian* | Adopted as the campaign's target theorem |
| Rigidity may explain **record longevity** — a 25-year-old record surviving weak search because of a rigid core / positive stress / tiny isolation radius | Adopted as the framing that connects our audits to something explanatory |
| Disk: the contribution is "published numerical optima without criticality certification are unreliable", not six better numbers | Adopted — [DISK_ASCENT](../heilbronn_disk/DISK_ASCENT_2026-08-21.md) already says the improvements are minor; framing to be sharpened |
| Disk criticality theorem: the scaling argument forces `max_i |x_i| = 1` (at least one boundary point); the real questions are how many boundary points are forced and whether criticality forces algebraic coordinates | Adopted as the disk direction, replacing more row-improvement |
| Exactification n=13..35 is low value | Adopted, and independently confirmed by the [repository sweep](NOVELTY_REPOS_2026-08-21.md): it is already being done by others |
| Table paper is forgettable; extract a classification theorem instead | Adopted |
| Prior-art gaps named: Russian/Eastern-European literature (Math-Net.Ru, zbMATH), DIMACS technical reports, and search strings "exchange method nonlinear programming geometry", "active set method packing", "certified optimization geometric packing", "tensegrity max-min distance", "critical frameworks"; people: Connelly, Nixon, Theran, Whiteley, Cohn, de Laat, Lubachevsky, Stillinger, Torquato, Kottwitz; Musin/Tarasov Tammes as the model | Queued as a third prior-art pass; the GitHub layer was already swept on the same day |

## Two-month programme as delivered

1. Finish the n=10 theorem (**done as of this review's disposition** — see above).
2. Rigidity *classification* of known square records — as a theorem, not a table.
3. A disk criticality theorem (boundary contact, active count, stress existence).
4. Minimal-core theory for general `n`: does every isolated optimum contain a
   rigid active subset?
5. Exactify only where rigidity suggests structure.
6. Record improvements last — "the search landscape is crowded".

Final judgement quoted for the record: without a general theorem the honest
classification is "a strong Experimental Mathematics paper with unusually
rigorous certificates, but not a major discrete geometry result"; with a
rigidity principle proved, "substantially more important".
