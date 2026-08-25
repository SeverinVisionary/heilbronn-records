# Third-party material in this deposit

**These files are NOT included in this deposit.** They are material owned by
other authors, whose rights we have not cleared, so we do not redistribute them.
What is recorded below is enough to retrieve each one yourself and confirm it is
byte-identical to what we used: source URL, capture timestamp, size and sha256.

Retrieve them with [`fetch_sources.py`](fetch_sources.py); check an existing set
with `python3 fetch_sources.py --check`.

A dead webpage is not public domain: text and images remain copyrighted whether
or not the page is still served. Scholarly quotation of the single line this
work depends on is one thing; wholesale mirroring of a page and its figures is
materially different, and rights should be cleared before republication.

The verifier and every certified result are unaffected by their absence: they
depend only on `configs/`, which is entirely our own work. Our *measurements* of
the figures — which is what the historical argument in `NOTE.md` actually uses —
are preserved as our own derived data in
`configs/friedman_figure_measurements.json`.

| file (NOT included; retrieve with fetch_sources.py) | bytes | sha256 |
|---|---|---|
| `sources/friedman_figures/hc10.gif` | 1137 | `8a6a73a3d1273436a6240a0141161281...` |
| `sources/friedman_figures/hc11.gif` | 1823 | `1dfe0e7a59ee1c801ef6b6cc2264c4cc...` |
| `sources/friedman_figures/hc11b.gif` | 1462 | `fbdf31c7c8768f7af95085293f34dfb8...` |
| `sources/friedman_figures/hc11c.gif` | 1662 | `1461f266c0db24535051cecaad9bfa9c...` |
| `sources/friedman_figures/hc12.gif` | 2170 | `18898fa5cb660c9e233df19147c88aa3...` |
| `sources/friedman_figures/hc13.gif` | 2533 | `8dac0248b03c3142fb1b8c7ceb8f4e5b...` |
| `sources/friedman_figures/hc13b.gif` | 1945 | `36d195e48ee833dd3672206e91fe4afb...` |
| `sources/friedman_figures/hc14a.gif` | 2351 | `66feb83c6abf6cbc9cbb5de3b09ae2b4...` |
| `sources/friedman_figures/hc14b.gif` | 2136 | `9398efb814d71acfa827acd70eea42bb...` |
| `sources/friedman_figures/hc14c.gif` | 1497 | `0cd0100e5cccbed1d5323dada7b0773d...` |
| `sources/friedman_figures/hc15.gif` | 2396 | `161d83fad8f0082b97d78144302efe02...` |
| `sources/friedman_figures/hc15b.gif` | 1648 | `961310051ec72877105fd8ae27994598...` |
| `sources/friedman_figures/hc15c.gif` | 1898 | `406bcb88ea3f4cdeaaea6586854dbc39...` |
| `sources/friedman_figures/hc16.gif` | 1959 | `7a19b5a70589218ca5f97ceaa6af183d...` |
| `sources/friedman_figures/hc9.gif` | 1729 | `c417f59d57617eed0b321fae8416f0b2...` |
| `sources/friedman_figures/hc9b.gif` | 2151 | `0bb5c17d4a2c5b328f0459ed3de78231...` |
| `sources/friedman_heilcirc_20190919.html` | 7690 | `361730f3b9ad7344e0f3fb1b0a770e2b...` |
| `sources/karpov_inversed/Ascension_2026-08-24.html` | 15925 | `19da436206392f408e9b11419a62f9af...` |
| `sources/karpov_inversed/Heilbronn_S13.txt` | 669 | `2180a899618f52fbdcb12635eb2a6358...` |
| `sources/karpov_inversed/Heilbronn_S15.txt` | 767 | `8eafcc63837533c177b7053b9464b0ff...` |
| `sources/karpov_inversed/Heilbronn_T13.txt` | 669 | `6b364258614bfb549d0b534d2c2f093b...` |

## Provenance

**Erich Friedman, *The Heilbronn Problem for Circles*** — `sources/friedman_heilcirc_20190919.html`
and `sources/friedman_figures/*.gif` (16 figures).
Original URL `http://www2.stetson.edu/~efriedma/heilcirc/`, offline since ~2024;
current host path `erich-friedman.github.io/packing/heilcirc/` returns 404 and
the CDX index shows it never existed there. Captured from the Internet Archive
snapshot of **2019-09-19** (`web.archive.org/web/20190919050056`). Owner: Erich
Friedman. Licence: **none stated**. Rights not cleared. This is the primary
source for the record being improved; the note quotes one line of it.

**Peter Karpov, *Ascension Framework*** — `sources/karpov_inversed/Ascension_2026-08-24.html`
and three coordinate files. Retrieved 2026-08-24 from `http://inversed.ru/Ascension.htm`
over plain HTTP (HTTPS fails TLS SNI). Owner: Peter Karpov. Licence: **none
stated**. Rights not cleared. Mirrored only to evidence a *negative* prior-art
finding — that his Heilbronn work covers the square and triangle, not the disk.

No modifications were made to any mirrored file. Checksums above allow a reader
to confirm that what is deposited matches what was retrieved.

## Status

**Resolved by removal (2026-08-24).** No third-party file is redistributed. The
deposit keeps only: the URLs and capture timestamps above, the checksums, the
single quoted line from Friedman's page that the historical claim depends on,
and our own derived measurements in
`configs/friedman_figure_measurements.json`.

If permission is later obtained from Erich Friedman, mirroring his archived
circle page would make the historical comparison permanently verifiable rather
than dependent on the Internet Archive continuing to serve it. That is the one
thing lost by removal, and it is worth asking for.

## What this deposit reuses, and on what basis

For completeness, everything in this repository that originates elsewhere:

| what | form here | basis |
|---|---|---|
| Friedman's row `14. A = .0758+ …` | three single-line quotations across the docs | short quotation for scholarship, attributed |
| Cantrell's constants (`.0758+`, `.113+`, …) | numbers cited in tables | facts; not copyrightable subject matter |
| Positions of the dots in Friedman's figures | our measurements, in `configs/friedman_figure_measurements.json` | measurements of factual content, produced by our own code; the figures themselves are not reproduced |
| Comellas–Yebra (2002) and Goldberg (1972) configurations | coordinates in `square/heilbronn_configs.py`, each with a `source=` field | published mathematical data, attributed |
| Karpov's `0.0270+`, `0.0211+`, `0.0265+` | numbers cited to evidence a negative finding | facts, attributed |
| MathWorld's `H_n` values | numbers cited, including the erroneous `H_11` | facts, attributed |
| numpy, scipy, mpmath, HiGHS, pytest | imported, never vendored or redistributed | dependencies, permissively licensed |

No third-party file is copied into this repository, and none is present anywhere
in its git history.

**This is a good-faith engineering audit, not legal advice.** The judgement that
short attributed quotation and factual data are reusable is the ordinary
scholarly one; if the deposit is ever challenged, that is a question for a
lawyer, not for this file.
