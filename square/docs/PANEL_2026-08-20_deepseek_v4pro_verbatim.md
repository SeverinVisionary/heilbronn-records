The RIGID/NONRIGID certificate semantics are sound, the Stiemke resolver is airtight on its decided cases, and the upward-closure inheritance is correct. Findings below are MEDIUM/LOW, mostly completeness-of-argument and wording, plus test gaps.

---

### Findings

**1. MEDIUM — dim-2 small-support witness search is not provably complete**
`rigidity_core.py:497-525` (`_resolve_stiemke`, the `for support in combinations(range(size), 3)` loop).

The search enumerates only support-3 subsets and, for each, checks only the *basis* vectors (and their negatives) of the 2×3 block's nullspace. For a block of nullity 2 (the two kernel vectors are proportional on that 3-support), a valid nonnegative witness `c` can be a nontrivial *positive combination* of the two basis vectors, which `_kernel` does not return directly — so it is missed. Support-1 and support-2 witnesses are also never enumerated. Concrete failure: a cone whose only nonnegative witness is a support-2 extreme ray embedded in a rank-1 3-support falls through to `UNDECIDED` (line 525). This can only produce honest `UNDECIDED`, never an unsound verdict, and run 6 had `undecided_count 0` so it did not bite — but the commit/verdict wording "kernel dims 0/1/2 decided fully in the field" is stronger than the code proves. Fix: enumerate supports 1..3, and for nullity-2 blocks run a dual 2-D sign analysis (reuse the `_positive_combination_2d` slicing idea) or a small LP to find a nonneg combination; keep the `undecided==0` assertion as the real guard.

**2. MEDIUM — `_resolve_stiemke` RIGID verdict does not re-verify rank 16 (standalone path)**
`rigidity_core.py:374-381, 480-497`; control at `624-626`.

A strictly positive kernel vector of `M^T` implies the strict stress but *not* `rank(free matrix)=16` (a positive dependence among free rows can coexist with free rank < 16). In production `classify` this is safe — the free-rank check at `rigidity_core.py:539-545` returns NONRIGID before the resolver runs, so full column rank is already established. But the standalone control `_resolve_stiemke(seventeen_core) == RIGID` certifies only the stress, not full rigidity, so the verdict's "independently cross-validated … by two exact methods" overstates what is re-derived (the stress only, not the rank). Fix: have `_resolve_stiemke` assert `rank(free_matrix)==16` before returning RIGID, or relabel the control as stress-only.

**3. MEDIUM — Part B recurrence evidence is vacuous as configured**
`rigidity_sampling.py:run_perturbed_trial` + `RIGIDITY_TEETH_VERDICT_2026-08-20.md` item 3.

Every kept perturbed sample re-converges to the incumbent (`match_distance` 1e-24…1e-30 across all four sigma levels; 882/882 matched). "Every sample covers all three cores" is therefore equivalent to "the incumbent's own active set contains the cores," which Part A already establishes by construction. The teeth criterion's Part B leg contributes no independent evidence of recurrence; the limitation paragraph states the reachable-basin caveat but item 3 still presents the recurrence as supporting evidence. Fix: reword item 3 to state plainly that the perturbed generator is a fixed point (no distinct near-record hypergraph observed) and/or add a generator that yields genuinely distinct near-record configurations before this can count as teeth evidence.

**4. LOW — "lie in the incumbent's D4 orbit" is float proximity, not exact membership**
`RIGIDITY_TEETH_VERDICT_2026-08-20.md` item 3 / `RIGIDITY_SAMPLING_PERTURBED_2026-08-20.md:1230`. The match is a `1e-3` tolerance test; actual distances (~1e-24) make "in the orbit" numerically justified here, but the honest phrase is "within match tolerance of the orbit." Purely a wording precision issue.

**5. LOW — `Classification(RIGID)` does not carry its rank witness**
`rigidity_core.py:59-66` vs `classify` `539-545`. The rank-16 side of the certificate is checked and discarded; a downstream consumer re-verifying from the returned `Classification` sees only `stress` + `stress_normals`. For a paper's computational core, store the free rank (or a rank witness) on the object.

---

### On the two CRITICAL questions (explicit answers)

- **Strict stress + rank 16 ⟹ C(H)={0}?** Yes, sound. Feasibility is exactly `inward components ≥ 0`; the stress vanishes on the 16 free coordinates and is strictly negative on all 8 inward normals, so for any feasible `v`, `0 ≤ Σy_e D_e(v) = ⟨G,v⟩ ≤ 0`, forcing every `D_e(v)=0` and every inward component of `v` to 0; rank 16 of the free matrix then forces `v_free=0`. The orientation table (`INWARD_COORDINATES`) is cross-checked against `tangent_certificate._assert_certificate_shape` by the all-20 positive control, so a sign transcription error fails loudly. `_verify_stress`/`_verify_velocity` are the final exact gates on every verdict, so no float proposal can leak an unsound classification.
- **Upward-closure inheritance?** Correct, including boundary feasibility rows: `C(H') ⊆ C(H)` for `H ⊆ H'` because the 8 feasibility rows are identical for every `H` and adding triangle rows only shrinks the cone. Rigidity is monotone up, non-rigidity monotone down, and the bottom-up scan's `issubset` skip (rigidity_core.py:666-671) is exact. The "17 tight" claim is genuinely established (all 4845 size-16 subsets NONRIGID; the size-17 core RIGID).

### Test gaps to close before this is a paper core

- A forced dim-2 small-support control (inject a rank-1 3-support block) asserting the resolver returns a witness or `UNDECIDED`, plus a support-2 extreme-ray case proving it is actually found (directly targets finding 1).
- A spot-check that one `RIGID-by-monotonicity` subset independently `classify`-es as RIGID (exercises the closure argument in code, not just the comment at `rigidity_core.py:660-664`).
- Pin the free-rank-16 certificate for the size-17 core explicitly (locks finding 2's rank side).
- Cross-check D4 dedup against `active_structure()` orbits rather than trusting `d4_index_maps` alone.
- A negative test that a stress with correct signs but rank < 16 must NOT be accepted as RIGID (locks the "stress alone is insufficient" semantics).
