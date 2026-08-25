#!/usr/bin/env python3
"""Retrieve the third-party sources this deposit's historical claims cite.

Provided so the deposit can be made reproducible WITHOUT redistributing
material whose rights have not been cleared (see THIRD_PARTY.md).  Nothing in
`configs/` or `verify.py` depends on these files; they support only the
historical comparison in NOTE.md.

    python3 fetch_sources.py            # download into ./sources
    python3 fetch_sources.py --check    # verify checksums of what is present
"""
import argparse, hashlib, pathlib, re, sys, urllib.request

WAYBACK = "http://web.archive.org/web/20190919050056"
STETSON = "https://www2.stetson.edu/~efriedma/heilcirc"
FIGURES = ["hc3","hc4","hc5","hc6","hc7","hc8","hc9","hc9b","hc10","hc11","hc11b",
           "hc11c","hc12","hc13","hc13b","hc14a","hc14b","hc14c","hc15","hc15b",
           "hc15c","hc16"]


def get(url: str) -> bytes:
    with urllib.request.urlopen(url, timeout=60) as response:
        return response.read()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    out = pathlib.Path(__file__).parent / "sources"

    expected = {}
    table = (pathlib.Path(__file__).parent / "THIRD_PARTY.md")
    if table.exists():
        for line in table.read_text().splitlines():
            m = re.match(r"\|\s*`([^`]+)`\s*\|\s*(\d+)\s*\|\s*`([0-9a-f]+)", line)
            if m:
                expected[m.group(1)] = m.group(3)

    if args.check:
        bad = 0
        for name, prefix in expected.items():
            path = pathlib.Path(__file__).parent / name
            if not path.exists():
                print(f"MISSING  {name}"); bad += 1; continue
            got = hashlib.sha256(path.read_bytes()).hexdigest()
            ok = got.startswith(prefix)
            print(f"{'ok      ' if ok else 'MISMATCH'} {name}")
            bad += 0 if ok else 1
        return 1 if bad else 0

    (out / "friedman_figures").mkdir(parents=True, exist_ok=True)
    print(f"fetching the archived page -> {out}")
    (out / "friedman_heilcirc_20190919.html").write_bytes(get(f"{WAYBACK}/{STETSON}/"))
    for name in FIGURES:
        try:
            data = get(f"{WAYBACK}im_/{STETSON}/{name}.gif")
            (out / "friedman_figures" / f"{name}.gif").write_bytes(data)
            print(f"  {name}.gif  {len(data)} bytes")
        except Exception as error:
            print(f"  {name}.gif  FAILED: {error}", file=sys.stderr)
    print("\nKarpov's pages are at http://inversed.ru/Ascension.htm (plain HTTP;\n"
          "HTTPS fails TLS SNI). Not fetched automatically -- see THIRD_PARTY.md.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
