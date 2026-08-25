# External strategic review ("Fields-medalist professor"), 2026-08-20

## Provenance

- Surface: ChatGPT desktop Chat via the `chatgpt` CLI, model `gpt-5-6-pro`,
  `tierAtSend: "Pro"` (the composer's `effortAtSend` attribute reads "medium"
  for Pro by a known UI quirk; the tier label is authoritative).
- Session `bd6d3d1d-2a56-4889-a979-69147859ce11`, conversation
  `6a86bc7e-eafc-83e8-95e6-f7a36a0f8d5e`, started 2026-08-20T08:36Z,
  completed 09:05Z (29.7 min).
- Prompt: harsh research-value critique of this campaign as of commit
  `02a34eb` state, five fixed questions (verdict / conditionality audit /
  ranked alternatives / keep-going question / new mathematical levers).
- Verbatim reply: [PROFESSOR_REVIEW_2026-08-20_verbatim.md](PROFESSOR_REVIEW_2026-08-20_verbatim.md)
  (byte-identical to the CLI-collected artifact; rendered math arrives with
  the MathML fallback duplicated, so formulas appear as exploded character
  runs — prose and findings are intact).
- Artifact integrity: VERIFY PASSED (exit 0) — the CLI's
  character-for-character comparison of the artifact against the app
  conversation, 25375 chars / 31480 bytes, tierAtSend Pro confirmed in the
  session record.

## Verdict, as delivered

1. **The unrestricted 19-dimensional box cover is declared a dead end.**
   Scale indicators put an honest planning range at 1e23-1e35 terminal
   boxes; a millionfold speedup compensates for roughly one extra
   refinement bit per coordinate. (The reviewer flags this range as an
   extrapolation, not a theorem, and prescribes a breadth-frontier profile
   test at 1e4/1e5/1e6 nodes to calibrate it.) Verbatim bottom line:
   "Stop trying to prove n=12 with a 19-dimensional box cover. ... Return
   to global n=12 only after you prove a structural theorem that removes at
   least ten continuous degrees of freedom."
2. **Genuinely valuable, per the review:** the exact tangent-cone
   certificate ("real mathematics ... the strongest thing in the branch" —
   upgrade it to a theorem with an explicit certified neighborhood); a
   completed C4-family uniqueness theorem; the <=3-point transversal no-go
   as part of a rigidity package; the D4 bracket as a component.
3. **Called engineering without mathematical consequence:** the exact
   branch-and-bound infrastructure as such, the McCormick/RLT relaxation
   ("scientifically worthless" as a bound), additional capacity grids, and
   the anchor propagation's trim count ("1,856 exact trims is a vanity
   metric" — the depth-625 profile is "chasing a pathological sliver",
   and anchored-vs-plain runs explore different trees so the comparison
   proves neither harm nor help).
4. **Conditionality audit:** the five-boundary normal form must be
   re-proved inside the repo as a self-contained "five-contact normal-form
   theorem" (contact classification including corner/tie/degenerate cases,
   distinct-role assignment via an explicit matching argument, D4
   canonicalization with non-strict orderings, correct quantifier logic
   applying the theorem to an optimizer, and a standalone cover verifier)
   before any completed cover could be called a theorem. Until then even an
   empty queue is a conditional computational statement.
5. **Ranked alternatives** (each with two-week starts and kill criteria in
   the verbatim text): (1) close the exact n=8 unit-triangle problem;
   (2) an n=12 restricted-rigidity paper assembled from what this branch
   already has; (3) n=10 global optimality behind a brutal feasibility
   gate (15 coordinates, 120 triangles, kill if incumbent+1e-4 needs more
   than ~1e7 nodes); (4) n=11 via a structural occupancy-counting theorem
   at target 1/27; (5) exact all-orbit classification for n=7/8 with an
   independent verifier. Named non-programs: n=13 beyond a two-week
   lottery, arbitrary convex domains, the incidence-geometry asymptotic
   route (a field change), free-standing SDP hierarchies.
6. **New mathematical levers** proposed: (5.1) active-triangle hypergraph
   rigidity — find a minimal rigid core with an exact positive dual stress
   and convert the tangent cone into a certified-radius terminal rule;
   (5.2) signed-area coordinates with four-point linear identities and
   Grassmann-Pluecker quadrics, excluding whole order-type cells by exact
   LP/SDP duals; (5.3) global capacity counting duality — occupancy
   templates from simultaneous strip/rectangle/pair-exclusion constraints.
   Each comes with a two-week teeth test and a deadness criterion.

## Citation checks performed before recording

- **Verified.** Cohen-Pohoata-Zakharov, "Lower bounds for incidences"
  (arXiv:2409.07658v2), Theorem 1.8: every n-point set in the unit square
  contains a triangle of area <= n^(-7/6+eps). The review's correction of
  the campaign's stale ~8/7 benchmark is correct; the same paper's
  Theorem 1.6 restates their earlier n^(-8/7-1/2000) bound
  (arXiv:2305.18253). The review's journal reference (Invent. Math. 240
  (2025)) is reported as given; the arXiv record is what was checked.
- **Not independently verified here:** the Zeng-Chen LNCS 6301 (2011)
  attribution for the five-boundary lemma, the reviewer's 1e23-1e35
  box-count extrapolation (flagged by the reviewer itself as untested), and
  the state-of-play claims about Monji-Modir-Kocuk n=10 runs. These carry
  the reviewer's own [VERIFY] discipline and must be checked before any of
  them is cited in a result document.

## Disposition within this branch

- Nothing in the review contradicts any exactness claim shipped on this
  branch; the DeepSeek v4-pro soundness pass (0 CRITICAL) stands.
- The review's strategic recommendations (kill/redirect decisions between
  n=12 global, the rigidity paper, n=8 triangle, n=10, n=11) are an
  operator decision and are recorded here without being enacted.
- Immediately actionable inside this branch regardless of that decision:
  the five-contact normal-form conditionality is already labeled in
  [GLOBAL_RELAXATION_2026-08-17.md](GLOBAL_RELAXATION_2026-08-17.md) and
  [global_interval_branch.py](global_interval_branch.py) docstrings; the
  review raises its priority and specifies the exact case list a
  self-contained re-proof must cover.
