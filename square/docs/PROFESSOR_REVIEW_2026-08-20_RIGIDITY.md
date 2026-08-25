# Professor review of the rigidity milestone — 2026-08-20 (second review)

## Provenance

- ChatGPT desktop, `gpt-5-6-pro` at `tierAtSend: "Pro"` (session
  `663ed6a3-e023-4d74-b3c6-61b28ddb90c3`, conversation
  `6a875aa7-d5a4-83e8-aa34-3afc13365b7a`).
- The CLI's reply-capture and recover paths failed on a DOM-bridge error
  (`window.__cgpt.pinnedReply is not a function`; `chatgpt doctor` reports
  all selectors healthy, so this is a capture-helper injection bug). The
  reply was extracted from the app's DOM by direct `chatgpt eval` after
  expanding four collapsed sections; generation had completed
  (`streaming: false`, single assistant unit). The CLI's
  character-for-character verify could not run for this session; the
  extraction method is recorded here in its place. Verbatim (with the
  usual duplicated-MathML rendering of formulas):
  [PROFESSOR_REVIEW_2026-08-20_RIGIDITY_verbatim.md](PROFESSOR_REVIEW_2026-08-20_RIGIDITY_verbatim.md).
- Prompt: the five-question audit of the TEETH verdict, the certified-radius
  plan, and the paper shape, with the milestone data summarized.

## Headline

"The project has crossed the line from 'numerical archaeology' into 'a
legitimate computational rigidity result.'" The minimal-core statement is
"potentially a real theorem" — a theorem about the first-order active
constraint system, not a Heilbronn bound — provided four named
publication-killers are closed.

## The four publication-killers (theorem audit)

1. **Boundary-cone completeness** (its declared first attack): prove the
   eight inward normals generate the entire active feasibility cone —
   i.e., enumerate every non-area constraint (box constraints, any
   normalization or gauge) and show only the eight boundary contacts are
   active at the incumbent. (Our `_derived_layout_check` already proves
   the eight-contacts-only fact; the paper must state the lemma and note
   that the scan works in raw R^24 with no quotient — the square has no
   continuous symmetries, so there are no gauge modes.)
2. **Orientation-branch certification**: the unsigned-area linearization
   is valid only where every active determinant keeps its sign; the
   later isolation radius must provably stay inside that orientation-
   stable neighborhood. (Cites Connelly 1982, Asimow-Roth 1978 for the
   branch-fixing philosophy — references to verify before citing.)
3. **Careful Stiemke/Farkas writing**: the stress certificate must be
   proven equivalent to the objective obstruction, not assumed.
4. **Rank-statement precision**: "rank 16 of what matrix, after
   quotienting what motions" must be unambiguous; state the theorem
   invariantly (the five-boundary normal form belongs in proofs, never in
   the theorem statement).

## Verdict audit

"TEETH" must be disciplined to **local** obstruction power: the honest
statement is "the active-triangle rigidity mechanism has confirmed local
obstruction power and deserves continuation." The blind-DE null is
valuable (it killed "easy remote optima") but says nothing about thin or
disconnected basins. Before "teeth" appears in a paper: prove either the
epsilon-neighborhood core-obstruction theorem (strong), the isolated-
local-maximizer theorem (medium), or say "evidence for a rigidity
mechanism" (weak). This matches and sharpens our post-panel rewrite.

## Certified radius: the prescribed route

Use the stress as a scalar barrier `L = sum w_i A_i`: first-order margin
`gamma` on feasible directions, exact second-derivative bound `M` (the
determinants are quadratic, so `M` is exactly computable), radius
`r < 2*gamma/M`, distance measured to the D4 orbit, not the point. The
radius is scale-invariant in the stress (both gamma and M scale
linearly), sidestepping the margin-normalization issue for this purpose.
Expected scale: `1e-2` plausible, `1e-3` near-certain; a constant like
`1e-8` "proves something but communicates nothing." Traps: second-order
flexes, cone corners (bound the Hessian over the full box rather than
diagonalizing), and the orientation-flip hypersurface.

## Ranked next steps (value per week, as delivered)

1. **Stress uniqueness at size 17** — already established: the stress
   space is the one-dimensional kernel found by the resolver; to be
   stated as an explicit lemma with its exact certificate.
2. **Second-order local isolation** — the paper's centerpiece; changes it
   from "interesting combinatorics" to "certified isolated local
   extremum."
3. **Core intersection / hitting structure** — compute the intersection
   of the three core classes and the transversal number; look for a 3-5
   triangle seed motif that explains all three.
4. **Flex diagrams** — for each triangle whose removal breaks rigidity,
   exhibit the emerging first-order flex; "a single diagram ... more
   valuable than 100 pages of certificates."
5. **C4 Bernstein bracket** — cut from this paper entirely; it is a
   second paper.

## Paper shape

Title candidates: "Local Rigidity and Minimal Active Constraint Cores in
the 12-Point Heilbronn Triangle Problem" / "Certified Active-Set Rigidity
in an Extremal Triangle Packing Problem." Structure: intro (kill the
overclaim immediately), exact incumbent, active hypergraph, minimal-core
theorem, certification methodology, local isolation theorem (if landed),
sampling as motivation only, discussion. Venues: Experimental
Mathematics / Journal of Computational Geometry / SIDMA; with the
isolation theorem, Discrete & Computational Geometry. "Not Inventiones.
Not JAMS."

## Disposition

Adopted in full as the next milestone's program: (i) tangent-cone and
orientation lemmas + invariant theorem statement; (ii) stress-uniqueness
lemma from the existing kernel computation; (iii) core-intersection and
flex structure (cheap exact computations); (iv) the second-order
isolation radius; (v) paper assembly per the prescribed shape, C4 cut.
The Connelly / Asimow-Roth citations must be independently verified
before use ([[prior-art-gate-first]] discipline).
