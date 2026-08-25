# HEAVY panel review of the rigidity milestone — 2026-08-20

## Provenance

First full three-leg HEAVY panel of this campaign (previous gates ran
DeepSeek-only with Claude spend-limited and Codex quota-blocked):

- **Claude Opus 5** via `claude -p --model claude-opus-5`, fresh repo-scoped
  print session; ran its own verification code (4,000-case fuzz of the 2-D
  slice logic against brute force, re-classification of all 39 inherited
  subsets, D4-equivariance sweep, external check of the coordinate layout).
  Verbatim: [PANEL_2026-08-20_claude_opus5_verbatim.md](PANEL_2026-08-20_claude_opus5_verbatim.md).
- **Codex `gpt-5.6-terra`**, `model_reasoning_effort=max`, read-only sandbox
  in the worktree (first successful Codex leg of this program; 204k tokens).
  Verbatim: [PANEL_2026-08-20_codex_terra_verbatim.md](PANEL_2026-08-20_codex_terra_verbatim.md).
- **DeepSeek `deepseek-v4-pro`** via opencode (banner verified), reading the
  pinned commit by `git show` from the main checkout. Verbatim (final
  findings; agentic trace not retained):
  [PANEL_2026-08-20_deepseek_v4pro_verbatim.md](PANEL_2026-08-20_deepseek_v4pro_verbatim.md).

All three legs reviewed commits `02a34eb..1f2742d` with the same prompt.

## Unanimous verdict: 0 CRITICAL

Each leg independently re-derived and endorsed: (a) strict stress + free
rank 16 implies a trivial critical cone; (b) the upward-closure inheritance
(feasibility rows are subset-independent, so `C(H') ⊆ C(H)` for
`H ⊆ H'`); (c) every RIGID/NONRIGID verdict passes through the exact
verifiers, so float proposals cannot mint a certificate. Claude: "The
claimed theorem is, as far as I can verify, true and correctly certified."
Codex: "No CRITICAL issues found." DeepSeek: "no CRITICAL soundness"
issues, inheritance correct, "17 tight ... genuinely established."

## Agreed findings (present in two or three legs)

1. **The reported dual margin is a scale artifact** (Claude M4, Codex M2).
   `_verify_stress` accepts any positive rescaling; the printed
   `least_negative_normal` depends on RREF normalization. Under `sum(y)=1`
   normalization the margins are of order 1e-3, so the verdict's "not
   numerically marginal" was unsupported (and "double-area units" was
   wrong — the gradient already halves). Fix: exact normalized margin.
2. **Part B's recurrence statistic is vacuous** (Claude M6, DeepSeek M3,
   Codex M3). All 882 kept perturbed samples re-converged to the incumbent
   itself (assignment distance 1e-24..1e-30 ≈ 1e-13 per coordinate); "the
   cores recur in every sample" is 882 observations of one configuration
   and adds nothing beyond Part A. The honest statement: perturbed local
   polish is observed to be a fixed point of the incumbent orbit; no
   distinct near-record hypergraph was observed; recurrence in genuinely
   distinct near-record configurations remains untested.
3. **Certificates are not persisted for independent verification**
   (Codex H1, Claude M9/M12, DeepSeek L5). Stresses, rank witnesses, and
   NONRIGID velocities are discarded after in-process verification; 33
   inherited subsets carry no own-certificate (Claude re-classified all
   39 inherited subsets independently: 39/39 RIGID). Fix: machine-readable
   per-subset manifest + a standalone verifier + a `--verify-inherited`
   mode.
4. **The resolver's completeness is narrower than the commit message
   claimed** (Claude H3, DeepSeek M1, Codex M5). Combined kernel dimension
   is `|H|-16`, so sizes 19-20 are structurally out of the resolver's
   dim<=2 scope (their 8 classified NONRIGID verdicts rest on exact-verified
   LP proposals — sound but not reproducible by construction), and the
   dim-2 small-support witness search misses support-1/2 and nullity-2
   block cases (can only cause honest UNDECIDED, never unsoundness). Fix:
   exact decision for kernel dim <= 4 (Fourier-Motzkin or exact simplex),
   then assert the resolver never returns UNDECIDED.
5. **"Cross-validated by two exact methods" overstated** (Claude M5,
   DeepSeek M2). The size-17 stress space is one-dimensional: both routes
   produce the same ray through the same verifier, and the standalone
   resolver control did not re-check rank. Fix: resolver asserts rank
   before RIGID; reword to "two proposal routes, one exact verifier, on a
   necessarily unique stress ray".

## Unique findings adopted

- **Claude H1 (demonstrated):** a non-prefix `--sizes` (e.g. `--sizes 18`)
  prints false "minimal cores" under a `COMPLETE` stamp. Guard required.
- **Claude H2:** the boundary/interior layout (`INWARD_COORDINATES`,
  `FREE_COORDINATES`) is a hardcoded modeling premise, checked only as
  integer bookkeeping; it must be derived-and-asserted from
  `incumbent_points()` (including the no-corner condition). Claude
  externally verified it is correct for this incumbent.
- **Claude M7:** both Part B deltas sit below the incumbent's 0.0118 gap
  to its second area tier, so the delta sweep carries zero information.
- **Claude M8:** the run-7 document says dropped trials landed "above" the
  near-record window; the filter drops those below. Erratum required.
- **Claude M10:** Part B's search space is the five-boundary normal form —
  non-conforming configurations are unrepresentable, not merely unreached;
  the limitation section must say so.
- **Claude M13:** the verdict must distinguish first-order rigidity from
  local optimality explicitly.
- **Codex L4:** `Trial.minimum_area` is an epigraph score that can sit
  below the recomputed geometric minimum by ~1e-17 (observed); rename or
  recompute before thresholding.
- **Claude L14:** `Qx.is_zero()` soundness rests on the (true, unasserted)
  irreducibility of `4x^3-12x^2+10x-1`; assert it.
- Test-gap tables from all three legs (Claude T1-T12, Codex's five
  additions, DeepSeek's five) are adopted as the pre-paper checklist.

## Disposition

No CRITICAL: the milestone stands, the verdict document is rewritten to
match the evidence (margins, Part B vacuity, certificate-recording claim,
first-order scoping), and the HIGH/MEDIUM code fixes plus the certificate
manifest are the immediate next commits, cloud-verified before paper
assembly. Every finding above is tracked to a disposition commit.
