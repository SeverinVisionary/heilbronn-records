# First rigidity audit of the unit-square record landscape — 2026-08-21

Produced by the generalized engine ([rigidity_engine.py](rigidity_engine.py))
over the exact configuration registry ([heilbronn_configs.py](heilbronn_configs.py)),
in the campaign of
[GENERAL_RIGIDITY_CAMPAIGN_2026-08-21.md](GENERAL_RIGIDITY_CAMPAIGN_2026-08-21.md).
Every row is exact: coordinates live in the configuration's own field
(rational, `Q(sqrt 13)`, or a cubic field), and every certificate is verified in
that field. Floating point only proposes.

## Guard

Each registry entry carries its published minimum area as an exact expression
and is rejected unless the value recomputed from the coordinates equals it
exactly. All four entries below passed, so these are the published
configurations and not lookalikes.

## Results

**Complete for 7 <= n <= 12** (extended 2026-08-23):

| n | min area (exact) | active triangles | contacts | rank / dim | verdict | first-order improvement |
|---|---|---|---|---|---|---|
| 7 | `(14z+2z^2-1)/38` | 8 | 7 | 14/14 | **RIGID** | none |
| 8 | `(sqrt13-1)/36` | 12 | 8 | 16/16 | **RIGID** | none |
| 9 | `(9 sqrt65-55)/320` | 11 | 8 | 18/18 | **RIGID** | none |
| 10 | `5z^2/8 - z^3/2` | 16 | 8 | **19/20** | **NONRIGID** (1-dim flex, `Q = -109.241`) | none |
| 11 | `1/27` | 28 | 8 | 22/22 | **RIGID** | none |
| 12 | `x/4 + xy/2 - x^2/2` | 20 | 8 | 24/24 | **RIGID** | none |

**Every best-known square configuration for `7 <= n <= 12` is now audited, and
`n = 10` is the unique first-order flexible one.** That is a sharper statement
than the single-case observation, and it also *disconfirms* the generalization
we hoped for: the flex is not the visible tip of a systematic degeneracy in
low-parameter symmetric ansaetze, since the other five configurations (three of
them found by the same authors with the same method) are rigid.

Cross-checks that fell out: `n = 8` has 12 critical triangles, matching the
count reported independently in arXiv:2603.11107v2 §6; the `n = 7` entry was
initially rejected by the registry guard (a mis-transcribed coordinate,
`-1+6z+2z^2` where the configuration needs `-1+6z+z^2`) — the guard doing
exactly its job.

"No first-order improvement" is stated exactly, but it is *not* the LP's failure
to find one (that proves nothing): it follows from the verified strict stress —
for any `v` with `Mv >= 0`, `y^T M v = 0` with `y > 0` forces `Mv = 0`, so no
area row can be strictly positive. The LP is a search, the stress is the proof.

Two independent validations of the engine itself:

- **n = 12** reproduces `rigidity_core`'s audited verdict (RIGID, 20 active
  triangles, 8 contacts, rank 24) through completely different code with no
  normal-form coordinate split.
- **n = 8 is a proved optimum** (Dehbi & Zeng 2022) and the engine certifies it
  RIGID, which is the expected answer for a true isolated optimum. Its twelve
  critical triangles also match the count reported independently in
  arXiv:2603.11107v2 §6.

## The n = 10 finding

The best-known ten-point configuration (Comellas-Yebra 2001, unimproved for
25 years) is **not infinitesimally rigid**. Exactly:

- the constraint matrix has rank 19 in dimension 20, so there is a
  one-dimensional exact kernel;
- the flex moves **all ten points** — it is not a rattler; every point occurs
  in at least one active triangle;
- all 16 active area gradients and all 8 boundary normals annihilate it
  exactly, so along this line every minimum-area triangle is stationary and
  every boundary point slides tangentially.

Because a triangle area is quadratic along a line, the behaviour along the flex
is decided exactly with no remainder term. Writing `A_e(t) = A_e(0) + c_e t^2`:

- **12 of the 16 active areas have `c_e < 0`** (the quoted `-10.950222...` and
  `-3.737555...` are *doubled*-area coefficients; in area units they are
  `-5.475111...` and `-1.868778...`), 4 have `c_e > 0`. One negative coefficient
  already forces the minimum down along the flex; the count is descriptive;
- hence the minimum strictly decreases in both directions along the flex, and
  the configuration is a strict local maximum along it.

### Upgraded after the 2026-08-21 professor review

The review rejected the first version of this claim: the second-order argument
above runs along the kernel *line*, while the feasible set is the cone
`C(H) = {v : Mv >= 0}`, and a referee would ask what happens in cone directions
outside `ker(M)` and along curves rather than lines. Both gaps are now closed
exactly:

- **The cone collapses to the line.** An exact strictly positive stress
  `y > 0` with `M^T y = 0` exists for the full n=10 active system (24 rows,
  dimension 20; stress space dimension 5) and is verified in exact arithmetic.
  For any `v` with `Mv >= 0`, `y^T M v = 0` with `y > 0` forces `Mv = 0`, so
  `C(H) = ker(M)` — the single flex line. Nothing escapes.
- **The stress-weighted Hessian is exactly negative.**
  `Q = sum_e y_e D^2A_e(v,v) = -109.241...`. (Reproducible since 2026-08-23 from
  `rigidity_engine.prestress_analysis`, pinned by
  `test_n10_prestress_stability_is_certified_by_committed_code`; both HEAVY-panel
  legs correctly flagged that this had been prose only. The normalization
  `-5.899` quoted earlier divided by the sum of area weights, which is not
  canonical — the stress cone is 5-dimensional — so only the sign is claimed.)
- **Therefore a strict local maximum, for curves too.** Put
  `L(x) = sum_e y_e A_e(x) + sum_j y_j g_j(x)`. Then `grad L(x*) = 0`, and the
  square's `g_j` are linear, so along any feasible curve the `t^2` coefficient
  of `L` equals `Q/2 < 0` — the curve's second-order correction `w` drops out
  exactly because the stress annihilates the gradients. Since
  `min_e A_e <= L / sum_e y_e` and equality holds at `x*`, the minimum strictly
  decreases in every feasible direction.

In rigidity-theory terms the configuration is **prestress stable** in the
proper sense — a stress whose quadratic form is definite on the infinitesimal
flex space — rather than infinitesimally rigid: first-order flexible,
second-order rigid, and an isolated local maximum. Comellas-Yebra did not see
this because their §2.2 check ran in a three-parameter symmetric ansatz with
three tied areas; in the full 20-dimensional space the active system is
rank-deficient.

This is the first structural fact this campaign has produced about a
configuration other than n = 12, and it was found in seconds on the first
sweep — evidence that auditing the landscape is worth more than searching it.

## What this closes and opens

- **Closed:** n = 8, 10, 11, 12 all have *no first-order improvement
  direction* — an exact LP-proposed, exactly-verified statement that no
  feasible velocity increases every active area. These four incumbents are not
  cheaply improvable, and the n = 10 flex is a dead end for ascent.
- **Open:** the second-order theory for prestress-stable configurations
  (n = 10) needs the same treatment n = 12 is getting — an isolation radius
  that accounts for the flex direction, where the quadratic coefficients above
  are exactly the data required.
- **Next targets:** square n = 5, 6, 7, 9. The unit-disk lane is **closed**
  (see the [retraction](../heilbronn_disk/DISK_ASCENT_2026-08-21.md)), and
  exactification of n = 13-16 is deprioritized: the professor review rated it
  "mostly worthless" and the [repository sweep](NOVELTY_REPOS_2026-08-21.md)
  found others already doing it.

## Tests

[test_rigidity_engine.py](test_rigidity_engine.py) (15 tests, ~2 s) pins all of
the above: exact field arithmetic and the rejection of a reducible minimal
polynomial; every registry entry against its published value; the n=12
equivalence gate (the relabelling between the paper's point order and
`rigidity_core`'s is recovered by coordinate matching, then the active
hypergraphs are compared); the n=10 flex with its exactly-zero linear terms and
twelve negative quadratic coefficients; and two controls that keep a negative
result honest — a configuration whose free corner point must be able to move,
and an obviously improvable configuration on which `improvement_direction`
must fire.

## Reproduction

```bash
python3 - <<'PY'
import heilbronn_configs as hc
from rigidity_engine import build_active_system, classify, improvement_direction, describe
for name in ("square-n8", "square-n10", "square-n11", "square-n12"):
    cfg = hc.load(name); system = build_active_system(cfg)
    print(describe(system, classify(system)),
          "\n  improvement:", improvement_direction(system) is not None)
PY
```

Runtime is seconds per configuration on one core; nothing here needed the
cloud.
