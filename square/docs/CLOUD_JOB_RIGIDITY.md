# Cloud job: full rigid-core scan (Part A of the rigidity teeth test)

Run this only in a user-launched cloud session. Never run the compute
section on the operator's Mac. Spec:
[RIGIDITY_CORE_SPEC_2026-08-20.md](RIGIDITY_CORE_SPEC_2026-08-20.md).

## Step 0: environment gate

```sh
set -eu
uname -a
hostname

if [ "$(uname -s)" = "Darwin" ]; then
  echo "STOP: this job must not run on the operator's Mac" >&2
  exit 99
fi
```

## Step 1: checkout and dependency check

```sh
git status --short
git branch --show-current
python3 --version
cd research/heilbronn_n12
python3 -m pip install -r requirements-research.txt
```

## Step 2: regression gate

```sh
python3 -m unittest -v
```

All tests (31 expected) must pass before the scan; a failure is a
STOP-and-report.

## Step 3: the full scan

```sh
python3 rigidity_core.py
```

Expected structure of the output: `controls PASS`, then
`processed 6196 of 6196`, per-size census lines, the minimal-core list
with orbit signatures, D4 copy counts and least-negative normal margins,
and one of the three status lines. Record complete stdout and elapsed
time. Any `UNDECIDED` count above zero must be surfaced verbatim — it
bounds the minimality claim and is a result, not a nuisance.

## Step 4: return results

Add a dated `RIGIDITY_CORE_RESULTS_YYYY-MM-DD.md` containing the Step-0
evidence, the exact commit sha, the command, exit code, elapsed time, the
full census table, every minimal core with its exact margin decimals, and
the status line verbatim. Commit only the result document. No `.github`
files, no logs in the repo.

Part B (near-record sampling) is a separate job and must not be
improvised inside this one.
