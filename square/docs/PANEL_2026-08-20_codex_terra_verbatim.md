No CRITICAL issues found.

The core cone logic is sound: strict stress plus free-rank 16 forces all inward coordinates, then all derivatives, then all free coordinates to zero. The resolver’s column-kernel check, 1-D sign cases, 2-D homogeneous slices, and verified row-space witnesses are mathematically valid. Superset inheritance is also valid: adding triangle rows retains the same eight boundary-feasibility rows, so \(C(H')\subseteq C(H)\).

1. **HIGH — the claimed per-subset certificate artifact is not actually recorded.**  
   [rigidity_core.py:670](rigidity_core.py:670) skips 33 supersets as `RIGID-by-monotonicity`, and [rigidity_core.py:684](rigidity_core.py:684) retains only minimal-core objects and undecided subsets. The exact stress vectors, rank pivots/minors, and all NONRIGID velocity witnesses are discarded; the run document records only counts and decimal margins. This conflicts with the verdict’s statement that every exact claim has a certificate “recorded in the run documents” at [RIGIDITY_TEETH_VERDICT_2026-08-20.md:5](RIGIDITY_TEETH_VERDICT_2026-08-20.md:5).

   Concrete failure scenario: a paper reader cannot independently check the certificate for a particular claimed NONRIGID subset, nor identify the parent core for a particular inherited RIGID subset. Also, an inherited core proof is sound, but is not an \(H'\)-specific stress with positive weight on every edge as the spec’s direct RIGID certificate defines.

   Suggested fix: emit a committed machine-readable manifest keyed by subset bitmask. Serialize every Q(x) triple for direct stresses/witnesses, a rank certificate, and an explicit parent-core reference for inherited statuses. Add a standalone verifier that consumes only this manifest and asserts all 6,196 results.

2. **MEDIUM — “large exact dual margins” is not meaningful without stress normalization.**  
   [_verify_stress](rigidity_core.py:193) accepts every positive rescaling of a stress, while [the scanner](rigidity_core.py:720) reports the raw normal coefficient. Thus \(y\mapsto\lambda y\) leaves rigidity unchanged but makes `-0.0363` arbitrarily small or large. The verdict’s “not numerically marginal” conclusion at [RIGIDITY_TEETH_VERDICT_2026-08-20.md:25](RIGIDITY_TEETH_VERDICT_2026-08-20.md:25) is therefore unsupported. It is also not a “double-area scale”: the gradient explicitly divides by two at [tangent_certificate.py:93](tangent_certificate.py:93).

   Suggested fix: exactly normalize each stress, e.g. \(\sum_e y_e=1\), then report the normalized least-negative normal and minimum weight with rational isolating bounds.

3. **MEDIUM — Part B’s caveat is good, but two verdict phrases overstate the measured protocol.**  
   The generator is explicitly incumbent-seeded local polish at [rigidity_sampling.py:114](rigidity_sampling.py:114). “All 882 kept samples lie in the incumbent’s D4 orbit” at [RIGIDITY_TEETH_VERDICT_2026-08-20.md:27](RIGIDITY_TEETH_VERDICT_2026-08-20.md:27) means float assignment cost below a tolerance, not exact orbit membership. Likewise, “the record configuration is hard to find” at line 42 only follows for the named DE configuration and budget.

   Concrete failure scenario: a different global optimizer finds a remote near-record basin; the current wording reads as a broader scarcity claim than the experiment supports.

   Suggested fix: state “numerically matched at assignment cost \(\leq\) threshold” and “this DE budget found none.” The remote-basin limitation itself is otherwise clearly stated.

4. **LOW — sampling thresholds and near-active sets use an epigraph lower score, not necessarily the recomputed geometric minimum.**  
   [global_normal_form_search.py:214](global_normal_form_search.py:214) returns `min(epigraph_z, actual_minimum)`, and [rigidity_sampling.py:134](rigidity_sampling.py:134) preserves that value. For run-7 seed `2026082301`, I observed reported `0.032598858691819534` versus recomputed actual `0.032598858691819541`.

   This is conservative and far below the 1e-6 thresholds/1e-4 deltas, so it does not affect the reported campaign counts. Still, rename it `score` or set `minimum_area` to the recomputed geometric minimum before thresholding and calling `near_active`.

5. **MEDIUM — resolver-specific proof gates are too narrow for a paper core.**  
   [full_set_controls](rigidity_core.py:616) tests one column-kernel case and one positive 1-D kernel core, but does not exercise the resolver’s zero-dimensional row-space path, mixed/zero 1-D signs, either nontrivial 2-D slice, or the 3-support witness construction at [rigidity_core.py:419](rigidity_core.py:419).

   Suggested additions before paper use:

   - Exact synthetic matrices for every Stiemke branch, including `t=1`, `t=-1`, `t=0`, and 1/2/3-support witnesses.
   - A checked manifest of the 24 formerly UNDECIDED subsets and their exact witnesses.
   - An independent exact finite-difference test of every active-area gradient, avoiding common-mode reliance on `unsigned_area_gradient`.
   - D4 action tests asserting each active-index map is a permutation, closes under composition, and maps all 14 raw cores into the reported three classes.
   - A full manifest recheck asserting the 6,196 combinatorial total and every certificate.

I did not rerun the cloud-only 23-minute scan; I reviewed its pinned output and performed local exact static checks of the active rank, D4 maps, and 2-D slice behavior.
