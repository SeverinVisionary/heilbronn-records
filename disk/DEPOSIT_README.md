# A certified 14-point disk construction improving the best previously documented value, with a census for 7 ≤ n ≤ 16

Deposit accompanying [NOTE.md](NOTE.md). **Draft — not yet deposited.**

## The result, in one line

```
alpha_disk(14) >= 0.07671588577102893975178477550663348580098852235157588479993
```

for 14 points in the **closed disk of radius 1**, exceeding D. Cantrell's 2007
value (`.0758+`) by **+1.075%**. This is a certified lower bound, not a proof of
optimality.

## Verify it yourself

```bash
python3 verify.py configs
```

Python standard library only; no dependency on anything outside this deposit.
It re-derives, in exact integer and rational arithmetic, the containment,
non-degeneracy, complete triple enumeration and exact minimum of every
configuration, and compares each against Friedman's printed bracket. Expected output
ends `12 of 12 configurations verified`.

## Normalization — read this first

Every coordinate is an **integer** to be divided by `scale`. The domain is the
**closed disk of radius 1** (area π). The literature uses two conventions and
mixing them has already produced one error in the published record:

```
Friedman, "The Heilbronn Problem for Circles"   unit RADIUS   (used here)
MathWorld, "Heilbronn Triangle Problem"         unit AREA
alpha_disk(n) = pi * H_n^{unit area}
```

Calibration: the regular pentagon gives `alpha_disk(5) = sqrt(50-10*sqrt5)/8 =
0.657163890148917`, matching Friedman's `.657+`.

## Contents

| path | what it is |
|---|---|
| `NOTE.md` | the note: result, method, census, erratum, prior art |
| `verify.py` | standalone exact verifier (stdlib only) |
| `configs/circle_n*.json` | the configurations, as integers over `scale` |
| `THIRD_PARTY.md` | provenance + checksums for every mirrored third-party file |
| `fetch_sources.py` | retrieves those sources instead of redistributing them |
| `extract_friedman_figure.py` | recovers point sets from the archived figures |
| `THIRD_PARTY.md` | third-party sources we do **not** redistribute: URLs, capture dates, checksums |
| `fetch_sources.py` | retrieves them from the Internet Archive, or `--check`s a set you have |
| `configs/friedman_figure_measurements.json` | **our** measurements of the 16 figures |

## Notes on individual data files

- `circle_n14_converged.json` — **the headline configuration** (scale `10^33`).
- `circle_n14.json` — an earlier, very slightly weaker certificate for the same
  basin (scale `10^15`), retained so the two can be compared.
- `circle_n16_D4.json` — reproduces Cantrell's n = 16; transporting it back to
  unit-area gives `H_16 = 0.021051349301...`, matching every digit MathWorld
  prints.
- `circle_n16_unrestricted.json` — deliberately included as a **negative**
  result: the best an unrestricted 6912 × 600k search reached at n = 16, some
  9.9% below the constructed row. `verify.py` correctly reports it as *below the
  published bracket*. It documents that this pipeline cannot find the n = 16
  optimum without being told its symmetry class.

## Status of open items

- The reproduction study is complete; see `configs/n14_reproduction.json` and
  `configs/n14_stationarity.json`.
- Math-Net.Ru, Croft–Falconer–Guy §F7 and Brass–Moser–Pach are recorded as
  *unverified*, not as negatives.

## License

CC-BY-4.0. See [LICENSE](LICENSE).
