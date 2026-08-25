# Rigidity teeth-test verdict — 2026-08-20 (rewritten after the HEAVY panel)

Evaluates the criteria fixed in
[RIGIDITY_CORE_SPEC_2026-08-20.md](RIGIDITY_CORE_SPEC_2026-08-20.md)
against cloud runs 5-7. This document was rewritten in the disposition of
[PANEL_REVIEW_2026-08-20.md](PANEL_REVIEW_2026-08-20.md) (0 CRITICAL;
several claims of the first draft were found unsupported and are corrected
here; the first draft is superseded and retrievable at commit `1f2742d`).

## Verdict: TEETH on the exact side; recurrence untested

**The exact half of the professor's avenue 5.1 passes.** The sampling half
produced no usable recurrence evidence, for a reason worth having on the
record.

### What is established exactly (first-order statements at the incumbent)

1. **Minimal-core theorem.** The 20 incumbent-active triangles contain
   exactly three D4-classes of inclusion-minimal rigid cores: one of size
   17 (8 copies) and two of size 18; no 16-triangle subsystem is rigid
   (all 4,845 certified NONRIGID), so 17 is tight. Every one of the 6,196
   subsets of sizes 16-20 was classified with an exact two-sided
   certificate or is a superset of a certified rigid core (33 subsets
   inherit by the monotonicity lemma `C(H') ⊆ C(H)` for `H ⊆ H'`; a
   panel-leg recheck classified all such subsets independently RIGID, and
   a `--verify-inherited` mode is queued to make that part of the
   committed run). Runs:
   [RIGIDITY_CORE_RESULTS_2026-08-20.md](RIGIDITY_CORE_RESULTS_2026-08-20.md),
   [RIGIDITY_RESULTS_RUN6_2026-08-20.md](RIGIDITY_RESULTS_RUN6_2026-08-20.md).
2. **Certified stress margins, correctly normalized.** A raw
   inward-normal margin is meaningless (any positive rescaling of a
   stress verifies), so the certified quantities are the exact
   sum-normalized values (`sum y = 1`): least-negative inward normal
   `-0.00315` (size-17 core), `-0.00496` and `-0.0163` (size-18 cores),
   with normalized minimum weights `0.0174`, `0.00496`, `0.0229`. These
   are exactly certified nonzero; whether they are *large enough* for a
   useful isolation radius is precisely what the certified-radius step
   must determine, and no claim of "comfortably large" is made here.
3. **Scope.** These are first-order rigidity statements: every nonzero
   feasible velocity strictly decreases some core triangle *to first
   order*. They do not by themselves establish local optimality (that
   needs the curvature/remainder control of the certified-radius step),
   and they say nothing about remote configurations or global optimality.

### Prior-art scope of the certificate idea (added 2026-08-21)

The *idea* that a strictly positive combination of the active-area gradients
certifies first-order local maximality is **not new**: Comellas & Yebra
(Electron. J. Combin. 9 (2002) #R6, §2.2) state it and exhibit such positive
combinations for `H₈` and `H₁₀`. They give no certificate for `n = 12`, work
inside a 2-3 parameter symmetric ansatz with boundary contacts absorbed into
the parametrisation, and claim confidence rather than proof. What is
unprecedented here is the full-dimensional treatment (16 free coordinates plus
8 inward boundary normals), the exact two-sided decisions, and the subset-level
census. See [NOVELTY_GLOBAL_2026-08-20.md](NOVELTY_GLOBAL_2026-08-20.md); the
citation is mandatory in any write-up.

### What the sampling actually showed

- **Blind scarcity.** Random-start differential evolution never reached
  incumbent−1e-4: 0 of 300 trials at the run-6 budget; the recorded
  high-budget trials peak at 0.0244 vs record 0.03260. Scoped claim: at
  these budgets and with this optimizer, blind search finds nothing near
  the record. No stronger scarcity claim is made.
- **Perturbed sampling is degenerate as recurrence evidence.** All 882
  kept perturbed samples re-converged to the incumbent itself (assignment
  distance 1e-24..1e-30, i.e. ~1e-13 per coordinate; "matched" means
  within the float tolerance, not exact orbit membership). "The cores
  recur in every kept sample" is therefore 882 observations of one
  configuration and adds nothing beyond Part A. What the campaign does
  support: perturbed local polish at sigma up to 0.1 was never observed
  to produce a near-record configuration outside the incumbent orbit — a
  fixed-point observation, not a recurrence statistic. Additional
  degeneracies found by the panel and acknowledged: both near-active
  deltas sit below the incumbent's 0.0118 gap to its second area tier
  (the delta sweep discriminated nothing), and the sampler explores only
  the five-boundary normal form, in which non-conforming configurations
  are unrepresentable rather than unreached. Erratum to
  [RIGIDITY_SAMPLING_PERTURBED_2026-08-20.md](RIGIDITY_SAMPLING_PERTURBED_2026-08-20.md):
  its per-campaign summaries say dropped trials landed "above" the
  near-record window; the filter drops trials *below* it.
- **Recurrence in genuinely distinct near-record configurations remains
  untested.** Testing it needs a generator constrained away from the
  incumbent orbit (e.g. minimum assignment distance >= epsilon), queued
  as future work. The kill criterion (proliferating unrelated
  hypergraphs) was *not* triggered — nothing distinct was observed at
  all.

## What the verdict unlocks

The paper plan proceeds on the exact side alone: the minimal-core theorem
+ the all-20 tangent-cone certificate + the <=3-labelled-point transversal
no-go + the complete two-parameter D4 bracket. The sampling campaign is
reported as method-scoped observations (scarcity + fixed-point), never as
recurrence evidence. Next lever step: the certified isolation radius and
sharpness constant from the size-17 core's stress, which is also the test
of whether the normalized margins above are quantitatively useful.

Panel dispositions in progress (tracked in
[PANEL_REVIEW_2026-08-20.md](PANEL_REVIEW_2026-08-20.md)): the `--sizes`
prefix guard, the derived-and-asserted boundary layout, the exact resolver
generalization to kernel dimension <= 4, the per-subset certificate
manifest with a standalone verifier, and the test-gap checklist.
