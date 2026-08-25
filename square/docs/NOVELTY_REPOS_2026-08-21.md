# Prior-art addendum: public repositories and community venues — 2026-08-21

The [global sweep](NOVELTY_GLOBAL_2026-08-20.md) covered paper and dataset
indexes (OpenAlex, DataCite, Zenodo, Crossref, DBLP, HAL, OSF, viXra). It did
**not** cover code-hosting platforms, and that was a real gap: the most active
Heilbronn work of the last six weeks lives on GitHub and is invisible to every
index we queried.

## What the repository layer contains

| Repository | Dated | Content | Overlap with us |
|---|---|---|---|
| [rhyschappell/heilbronn-n14-exact](https://github.com/rhyschappell/heilbronn-n14-exact) | 2026-08-19 | **Exact algebraic realization of the best-known square n=14** (Beyleveld 2006, previously 6-decimal only): `a` the root of `8a^3-12a^2-12a+1` in `(0.07,0.08)`, min area `1/20-(3/10)a-(2/5)a^2`, the smallest positive root of `320t^3+768t^2-60t+1` | **Directly pre-empts** our planned "exactification of float-only records" item, at n=14, two days before we planned it |
| [TejSteadQC/heilbronn-configurations](https://github.com/TejSteadQC/heilbronn-configurations) | 2026-07-07 → 2026-08-20 | New best-known configurations (triangle n=13, convex n=15), an **exact** D6-symmetric convex n=18 solution, first entries n=17-20. Method stated: multistart basin-hopping over a **trust-region successive-LP local maximizer**, then verified exactly | The successive-LP local maximizer is the same idea as our `exact_ascent` direction step; ours is exact end-to-end, theirs float-with-exact-verification |
| [cnemri/heilbronn-alphaevolve](https://github.com/cnemri/heilbronn-alphaevolve) | 2026-08-03 | AlphaEvolve on Google Cloud: new best-known **unit-square** values at n=17 (+4.74%), n=21 (+1.71%), n=22 (+10.72%), with exact rational values | Shows AlphaEvolve now *does* beat unit-square records — the Nov-2025 statement that it beat none is out of date |
| [daiki078/heilbronn-triangle](https://github.com/daiki078/heilbronn-triangle) | 2026-07-23 | no README | — |

**None of these repositories contains any rigidity content.** A recursive
file-tree scan of the two substantial ones (1,531 and 4 files) for
`rigid|stress|certif|flex|kernel` returns zero matches. The certificate
programme — stresses, minimal rigid cores, prestress stability — remains
unclaimed in the repository layer as well as in the literature.

## The maintained table lags the repositories

Erich Friedman's square table (fetched 2026-08-21) lists `n=17 = .016481`
(Tej Stead, July 2026) and `n=22 = .009569` (Sudermann-Merx, August 2026),
while `cnemri/heilbronn-alphaevolve` published `0.017261677...` and
`0.010472534...` on 2026-08-03. Whatever the reason — unsubmitted, unverified,
or simply not yet processed — **"the record" now depends on which venue you
ask.** Any future improvement claim of ours must be checked against *both* the
maintained table and the active repositories, and must say which baseline it
beats.

## The disk has no maintained table — **WRONG, corrected 2026-08-23**

~~The Packing Center index lists exactly three Heilbronn pages … our disk rows
are measured against the correct (and only) baseline.~~

The Packing Center index (fetched 2026-08-21) does list only Squares, Triangles
and Convex Regions, with no circle/disk page — but the conclusion drawn from
that was false. **MathWorld's Heilbronn Triangle Problem page carries best-known
constants for the circle** (Friedman 2007; D. Cantrell, pers. comm.,
2007-06-18), in unit-*area* normalization; the values sit in the page's image
`alt` attributes, which is why a text scrape missed them. Checking one index and
concluding "no table exists" was the error — the same shape of mistake as
concluding "no competitor exists, therefore our value is best known", which the
[disk retraction](../heilbronn_disk/DISK_ASCENT_2026-08-21.md) also had to undo.

Practical consequence: any disk work must compare against **both** the Zenodo
table and the MathWorld/Cantrell constants (converting: a unit-radius value
divided by `pi` gives the unit-area value).

## OEIS

`A248866` (discrete Heilbronn on a grid) and `A343851` (decimal expansion of
the n=7 square value) are the only relevant sequences; neither touches
configuration structure or rigidity.

## Consequences for the campaign

1. **Unchanged:** the rigidity/certificate contribution — audits, minimal cores,
   prestress stability, isolation radius — has no precedent in papers, datasets,
   or repositories.
2. **Downgraded:** `exact_ascent` is not a novel *method*. A trust-region
   successive-LP local maximizer is already community practice; our version's
   only distinction is that it is exact end-to-end rather than float-then-verify.
   It should be presented as tooling, never as a contribution.
3. **Contested:** exactification of float-only records is being done right now
   (n=14 on 2026-08-19; exact convex n=18). Remaining unexactified square
   records should be checked repository-by-repository before any work starts,
   and the item is worth doing only where it is still open *and* where the
   rigidity certificate adds something the exact coordinates alone do not.
4. **Crowded:** the square range n >= 13 has at least four active searchers plus
   an AlphaEvolve deployment. Record-chasing there is a poor use of our compute,
   which is what the campaign already concluded on other grounds.

## Third pass — the venues the professor review named (2026-08-21)

The [professor review](PROFESSOR_REVIEW_2026-08-21.md) attacked the sweep and
named specific places it expected work to hide. Results:

| Venue / query | Outcome |
|---|---|
| **zbMATH Open**, `heilbronn triangle` (25 results) | Every hit already known: Roth 1951/1972, Schmidt, Komlós–Pintz–Szemerédi, Lefmann, Dress–Yang–Zeng 1995, Jiang–Li–Vitányi, the on-line and `d`-dimensional variants. **All English; no Russian-language Heilbronn configuration work, no rigidity treatment.** |
| **zbMATH**, `irreducible contact graph` | Returns exactly the two Musin–Tarasov papers we already cite as the method analogue (sphere 2015, square flat torus 2016). Confirms the framing; nothing closer. |
| **zbMATH**, `rigidity packing locally maximal`, `stress certificate optimal packing` | Nothing on max-min *area* configurations. |
| **Math-Net.Ru** (Russian literature), English and Cyrillic query forms | The search interface returned no machine-readable results through its URL query form; **this leg is unresolved, not cleared.** Recorded as an open gap rather than a clean sweep. |
| **OEIS** | `A248866` (discrete/grid Heilbronn), `A343851` (n=7 decimal). No configuration structure, no rigidity. |

Net: the third pass found **no new prior art**, and confirmed that the closest
method relatives remain Musin–Tarasov's irreducible contact graphs. The one
honest gap is Math-Net.Ru and, behind it, Russian technical-report series,
which no open API we can reach indexes.
