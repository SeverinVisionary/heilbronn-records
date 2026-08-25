## Verdict on CRITICAL: none found

I could not construct any path by which a subset is classified RIGID unsoundly. Concretely verified:

- **Every** `Classification(RIGID, …)` is constructed only downstream of `_verify_stress` (`rigidity_core.py:381`, `:565`); **every** `NONRIGID` only downstream of `_verify_velocity` (`:391`, `:474`, `:539`, `:547`, `:573`). Float LP appears only in `_propose_*`; a bad proposal can only lose a certificate, never mint one.
- **Strict stress + rank 16 ⟹ C(H)={0}** holds, and the code enforces the part that makes it work: strict negativity on *all eight* normals (`:214`). If one normal coefficient were allowed to be zero, the equality argument would leave that inward component free and rank 16 would not close it. `:201` enforces `y_e > 0`.
- **Rank 16 is established before every RIGID return**: `classify` at `:542`; `_resolve_stiemke` at `:471–474`, where `ker(M)=0` ⟺ free-matrix rank 16, because the eight unit rows (`:326–329`) force `u₁₆..₂₃ = 0`.
- **Stiemke logic is airtight.** `C(H)={0}` ⟺ full column rank **and** `∃y>0: Mᵀy=0`, and a strictly positive `y` restricted to its first `|H|` entries is exactly the spec's strict stress (the trailing 8 entries are the `−n_j > 0` slacks). The dim-0/1/2 case split is exhaustive, and each constructed `target` is nonnegative, nonzero, and orthogonal to `ker(Mᵀ)` hence in `range(M)`.
- **`_positive_combination_2d`**: the reduction to `t ∈ {1,−1,0}` is complete by positive-scaling invariance; `None` is a proof. Fuzzed 4,000 random instances against brute force — 0 discrepancies.
- **Support-3 witness search**: extreme rays of `{c ≥ 0} ∩ ker(K)^⊥` with `dim ker = 2` have support ≤ 3, so it is complete; and failure returns `UNDECIDED`, never `RIGID`.
- **Upward closure (question 2) is correct.** The 8 boundary-feasibility rows are built from `INWARD_COORDINATES` alone and do not depend on `H` (`:326–329`), so `H ⊆ H' ⟹ C(H') ⊆ C(H)`. I additionally re-classified **all 39 subsets the scan inherits** — 39/39 independently RIGID, 0 mismatches.
- Independent cross-checks I ran: the three cores have exact free-rank 16 and trivial free kernel; all 17/18/18 one-triangle deletions are NONRIGID; the 14 raw cores are D4-closed with orbit sizes 4/2/8 and 3 canonical classes; `classify` is D4-equivariant on 60 random subsets × 8 symmetries (0 violations); a float LP (`max Σ(Mu)` s.t. `Mu ≥ 0`, `‖u‖∞ ≤ 1`) gives 0 for the cores and 3.0–4.6 for one-deletions.

The claimed theorem is, as far as I can verify, true and correctly certified.

---

## HIGH

**1. `--sizes` accepts a non-downward-closed range and still prints minimality + `COMPLETE`.** — `rigidity_core.py:700–702` (guard is only `16 ≤ size ≤ 20`), `:684–692`, `:713–740`

The minimality argument requires that *every* smaller size was scanned. `main()` only rejects sizes outside 16..20; `scan()` has no guard at all.

Failure scenario — I ran it:
```
$ python3 rigidity_core.py --sizes 18
minimal_rigid_cores 26
minimal_rigid_cores_up_to_d4 5
core (0,...,13,14,15,18,19) ... least_negative_normal -0.027897095646623912192369
status COMPLETE: every subset in the scanned sizes carries an exact certificate
```
Five "minimal cores" of size 18, none of which is minimal (four are supersets of the size-17 core). Anyone re-running the paper's artifact with a narrowed size list gets a wrong theorem with a `COMPLETE` stamp.

Fix: in `scan()`, require `sorted(sizes) == list(range(16, max(sizes)+1))`; otherwise suppress `minimal_rigid_cores*` / `core` lines entirely and emit `status PARTIAL: no minimality claim`.

**2. The geometry premise is hardcoded and never checked against the actual point coordinates.** — `rigidity_core.py:45–54`, `:83–88`; `tangent_certificate.py:66`, `:176–203`

`INWARD_COORDINATES` and `FREE_COORDINATES` encode *which coordinate of which point is boundary-constrained*. `_coordinate_layout_check` verifies only that the two index sets are disjoint and cover 0..23 — a statement about integers, not about geometry. Nothing asserts that points 0–3 actually lie on `y ∈ {0,1}`, that 4–7 lie on `x ∈ {0,1}`, that 8–11 are strictly interior, or that no point is at a corner (a corner point would have **two** active normals and the tangent cone would be a quadrant, not a half-space).

I checked externally and the assumed layout is correct for this incumbent (`x ≈ 0.11535`, `y ≈ 0.18055`, no corners, no point on a wrong edge), so no wrong result today. But this is the single unverified modeling premise the entire two-sided certificate rests on, and it directly contradicts the spec's own "No implicit parameters" gate. If it were wrong, NONRIGID witnesses would be infeasible *and* RIGID stresses would be missing a constraint — both directions fail silently.

Fix: derive `INWARD_COORDINATES` from `incumbent_points()` (test each coordinate for `is_zero()` / `(c−ONE).is_zero()`), assert exactly 8 constrained coordinates over 8 distinct points, assert no point is constrained in both coordinates, and assert points 8–11 satisfy `sign(c) > 0 and sign(ONE−c) > 0` in both coordinates.

**3. The exact resolver is complete only for `|H| ≤ 18`; `COMPLETE` at sizes 19–20 rests entirely on the float LP.** — `rigidity_core.py:456–526` (`:497` dim-2 branch, `:526` fallthrough), `:285–312`

With full column rank, `dim ker(Mᵀ) = |H| + 8 − 24 = |H| − 16`. I confirmed empirically: sizes 16/17/18/19/20 give kernel dims 0/1/2/3/4, so `_resolve_stiemke` returns `UNDECIDED` for **every** subset of size 19 and 20. That is exactly why run 5's 24 UNDECIDED sat at sizes 17–18 and why the resolver closed them.

I then checked the 8 size-19 subsets that the scan actually classifies (drops of triangles 1,2,5,6,8,9,11,12 — the only ones not inherited):

```
drop 1  free-rank 16  status NONRIGID  rank-deficient path: False
        LP proposal available: True    resolver alone: UNDECIDED
... identical for 2, 5, 6, 8, 9, 11, 12
```

All eight NONRIGID verdicts come *only* from `_propose_velocity` → scipy/HiGHS. The certificates are exact (re-verified in `Q(x)`), so soundness is intact — but the headline "COMPLETE: every subset carries an exact certificate" is contingent on a float solver's behaviour and is not reproducible by construction. A different scipy build that returns `success=False` or `t ≤ 1e-9` on one of these turns the paper's central claim back into `COMPLETE-WITH-UNDECIDED`.

Fix: generalize the strictly-positive-kernel decision beyond dim 2. For `k ≤ 4` exact Fourier–Motzkin on `k` variables is trivial, or run an exact rational simplex on `Mᵀy = 0, y ≥ 1`. Then assert `resolver never returns UNDECIDED` as a scan invariant, and state in the results doc which verdicts depended on the LP.

---

## MEDIUM

**4. The dual margin is not scale-invariant, so verdict claim 2 is not a claim.** — `rigidity_core.py:721–733`; `RIGIDITY_TEETH_VERDICT_2026-08-20.md:25–26`

`_verify_stress` accepts any positive rescaling of `y`. The reported `least_negative_normal` is whatever `_kernel`'s RREF normalization happened to pick (note the weight vectors all end in exactly `1.0` — the free column). I verified: multiplying each core's stress by 1000 still verifies, and the "margin" becomes −36.27 / −58.90 / −250.75. Normalizing by `Σy` instead gives −0.00315 / −0.00496 / −0.0163 — i.e. order `1e-3`, not the "order 1e-1–1e-2, not numerically marginal" the doc asserts.

Fix: define the margin as an LP value with a fixed normalization, e.g. `max t s.t. G(y)=0 on free, G(y)_j ≤ −t, y ≥ 0, Σy = 1`, computed exactly; report that number and drop the raw one. Also report the *primal* margin (how far a feasible velocity must decrease some triangle), which is what a sharpness constant will need.

**5. "The size-17 core is independently cross-validated by two exact methods" overstates independence.** — `RIGIDITY_TEETH_VERDICT_2026-08-20.md:22–24`

For `|H| = 17` the stress space is 1-dimensional (`dim ker(free_matrixᵀ) = 17 − 16 = 1`), so the LP-proposed stress and the resolver's kernel vector are *the same ray*. Both then pass through the same `_verify_stress`, the same `sign()`, and the same `unsigned_area_gradient`. Two proposal routes, one verifier — not two methods.

Fix: say "two proposal routes converge on the same (necessarily unique up to scale) stress ray"; for genuine independence, add a checker that reads only a serialized certificate (see T6).

**6. Part B's recurrence evidence is vacuous: the 882 "near-record samples" are the incumbent itself.** — `RIGIDITY_SAMPLING_PERTURBED_2026-08-20.md:488, 943, 1092, 1156`; verdict `:27–32`

Every kept sample reports `min_area 0.032598859` (the incumbent value to 9 digits) and `match_distance` between `7.1e-31` and `1.06e-24` — a *summed squared* assignment distance over 12 points, i.e. ~10⁻¹³ per coordinate. The optimizer relaxed back onto the incumbent to machine precision in every kept trial. "The cores recur in every near-record sample observed" is 882 observations of one configuration; it cannot distinguish "the cores are robust" from "the polisher found the same point again".

Fix: either report this honestly ("perturbed polishing returns to the incumbent to ~1e-13 in every kept trial; the recurrence statistic is therefore degenerate"), or change the experiment: hold a constraint that forbids returning to the incumbent orbit (e.g. minimum assignment distance ≥ ε) and ask what near-active hypergraphs the constrained optima carry.

**7. The two deltas carry zero information.** — `rigidity_sampling.py:87–91`; verdict `:30`

The incumbent's second distinct area tier is `0.04437`, a gap of `0.011772` above the minimum. I confirmed `near_active` returns exactly the 20 active triangles for delta `1e-4`, `1e-3`, **and** `1e-2`. "every one covers all three cores at both deltas" is one measurement presented as two, and the delta sweep in the spec's Part B protocol never exercises its own tolerance.

Fix: choose deltas relative to the observed gap (e.g. `0.5×`, `1.0×`, `2.0×` the min-to-second-tier gap) so at least one delta changes the hypergraph, and report the near-active *count*, not just the ⊇-test.

**8. The perturbed doc states the drop condition backwards.** — `RIGIDITY_SAMPLING_PERTURBED_2026-08-20.md:536, 991, 1140` vs `rigidity_sampling.py:222–226`

The doc says "7 / 313 / 398 trials landed **above** the near-record window and were dropped". The filter keeps `trial.minimum_area >= threshold` and drops otherwise, so dropped trials landed *below* `incumbent − 1e-4`. As written, a reader concludes 313 trials beat the record. Line 1226 of the same document says the opposite ("fail to reach the near-record window"), so the doc contradicts itself.

Fix: change "above" to "below" in all three per-campaign summaries.

**9. "Every one of the 6,196 subsets carries an exact certificate" is not what the run established.** — verdict `:18–19`; `rigidity_core.py:670–673`

33 subsets (20 at size 18, 12 at 19, 1 at 20) were skipped by the inheritance shortcut and carry no certificate of their own. The inherited proof is *valid* but it is not the spec's RIGID certificate — extending a core's stress by zero weights gives `y ≥ 0`, not `y > 0` on `H'`, so the emitted object would fail `_verify_stress` on `H'`. I re-classified all 39 such subsets and every one **does** independently certify RIGID — but the committed run never did that.

Fix: add a `--verify-inherited` pass (39 extra classifications, a few minutes) and record the result; or reword to "carries an exact certificate or is a superset of a certified rigid core, with the monotonicity lemma stated".

**10. Part B's search space is structurally restricted, and the Limitation section doesn't say so.** — `global_normal_form_search.py:107–118`, `:146–158`; `rigidity_sampling.py:114–145`; verdict `:34–46`

The sampler perturbs the 19-parameter *five-boundary normal form*, which pins `p₀.x = 0`, `p₁.y = 0`, `p₂.x = 1`, `p₃.y = 1`, `p₄.x = 0`. Configurations not of that boundary shape cannot be represented at all — not "hard to reach", *unrepresentable*. The Limitation section mentions only the reachable basin. Also, `np.clip(base + noise, 0, 1)` at `rigidity_sampling.py:126` pushes out-of-range perturbations onto the parameter box face, biasing samples toward extra boundary incidences.

Fix: state the normal-form restriction in the Limitation section alongside the basin restriction, and cite whatever justifies the five-boundary form (or flag it as an assumption).

**11. Coverage statistics are conditioned on `matched`, and unmatched hypergraphs are counted in raw labels.** — `rigidity_sampling.py:257–276`

`covered_by N of K` uses `matched` as both numerator pool and denominator (`:259–271`), so the recurrence question is answered only over samples already declared to be in the incumbent orbit. Separately, `distinct` at `:273` keys on `near_active_raw` — un-permuted, non-D4-canonicalized labels — so two identical hypergraphs under different sample labelings count as distinct. That direction is conservative for the kill criterion, and the run's count was 0, but it is wrong as a statistic.

Fix: report coverage over *all* kept samples with `matched` as a separate column; canonicalize unmatched hypergraphs by the D4 orbit before counting distinct ones.

**12. The RIGID certificate payload omits its own rank half.** — `rigidity_core.py:73–80`, `:374–381`, `:713–734`

`_stress_from_positive_kernel` does not verify rank 16 itself; it is correct only because both call sites happen to have established it. `Classification` records `stress` and `stress_normals` but no rank witness, and `main()` prints neither. A third party holding the printed certificate cannot complete the proof. `tangent_certificate.py:71–72` shows the right pattern (`CRITICAL_ACTIVE_INDICES` + `CRITICAL_MINOR`) for the all-20 case; it is not emitted per core.

Fix: have `classify` attach the 16 row indices of a nonsingular free-gradient minor and its exact value; assert rank inside `_stress_from_positive_kernel` rather than relying on callers.

**13. The Limitation section covers only the sampling basin, not the first-order nature of the theorem.** — verdict `:34–46`

`C(H) = {0}` is a statement about the linearization: every nonzero feasible velocity strictly decreases some triangle *to first order*. It does not by itself establish that the incumbent is a local maximum — that needs the uniform margin plus curvature control the doc lists as the *next* step. The run docs say this ("NOT global optimality"); the verdict doc's Limitation section does not, while claim 1 is headed "exact, unconditional".

Fix: add one sentence to the Limitation section distinguishing first-order rigidity from local optimality.

---

## LOW

**14. Zero-testing in `Q(x)` is sound only because the cubic is irreducible; never asserted.** — `incumbent.py:100–101`, `:122–124`

`Qx.is_zero()` tests coefficients, which equals the field zero test only if `1, x, x²` is a `Q`-basis, i.e. `4x³ − 12x² + 10x − 1` is irreducible over `Q`. It is (rational root candidates `±1, ±1/2, ±1/4` all give nonzero), but every "vanishes identically" check in the paper depends on it and nothing states it. Add a one-line rational-root test.

**15. The spec's negative control (a) is not implemented as written.** — `rigidity_core.py:612–614` vs `RIGIDITY_CORE_SPEC_2026-08-20.md` "assert the scan refuses it"

The code classifies `range(15)` and asserts NONRIGID; the refusal lives only in `main()`'s argparse. Related to finding 1.

**16. The untouched-normal control tests 1 of up to 8 positions.** — `rigidity_core.py:631–641` (`break` at `:641`). Drop the `break`; it costs 8 classifications.

**17. A result under test is used as its own gate.** — `rigidity_core.py:624`

`seventeen_core = (0,…,12,14,16,18,19)` is the run-5 output, hardcoded as a "resolver control". It is a fine regression pin but should be labelled a pin, not an independent control.

**18. `except AssertionError: pass` swallows more than verification failure.** — `rigidity_core.py:566–567`, `:574–575`

Any `AssertionError` raised deeper (e.g. from `_solve_exact:367` or `_kernel`) silently degrades to the resolver path. Introduce `class CertificateRejected(Exception)` raised by the two verifiers and catch only that.

---

## Test gaps to close before this is a paper's computational core

| # | Test | Why |
|---|---|---|
| T1 | Derive-and-assert the boundary/interior/corner layout from `incumbent_points()` | Closes finding 2 — the one unverified premise |
| T2 | Unit tests for resolver primitives on synthetic matrices: `_positive_combination_2d` (property test vs brute force; my 4,000-case fuzz passed), each kernel-dim-1 sign branch (all-+, all-−, zero-entry, mixed), the dim-2 support-3 search, `_solve_exact` consistent/inconsistent | The resolver is 70 lines of case analysis with **zero** direct tests today |
| T3 | Rank–nullity property test for `_kernel`/`_rank` with `x`-bearing (non-rational) `Qx` entries | My fuzz only covered rational entries |
| T4 | `--verify-inherited` scan mode asserting all 39 inherited subsets independently certify | Closes finding 9; I ran it, 39/39 clean |
| T5 | D4-equivariance test: `classify(σ(H)).status == classify(H).status` for all 8 σ | Cheapest global check on gradient/row construction; I ran 60×8 with 0 violations |
| T6 | Serialize each core's certificate (subset, exact weights, exact normals, minor indices + value) and add a standalone verifier that reads only that file + `incumbent_points()` | Today the certificate never leaves the process that made it; a referee cannot check it |
| T7 | Exact normalized-margin computation and a regression bound on it | Closes finding 4 and is a prerequisite for the isolation-radius step |
| T8 | Mutation tests of the two verifiers: perturb one gradient entry by an exact ε and assert RIGID fails; delete one feasibility row and assert a NONRIGID witness becomes infeasible | The only negative control today is one sign flip |
| T9 | Assert a non-prefix `--sizes` suppresses minimality output and `COMPLETE` | Closes finding 1 |
| T10 | Irreducibility assertion for `4x³−12x²+10x−1` | Closes finding 14 |
| T11 | Part B: assert the delta sweep actually discriminates on at least one sampled configuration; assert `matched=False` samples are counted in D4-canonical form | Closes findings 7 and 11 |
| T12 | Scan invariant: `undecided == 0` must be *provable*, not observed — assert the resolver never returns UNDECIDED once generalized past dim 2 | Closes finding 3 |
