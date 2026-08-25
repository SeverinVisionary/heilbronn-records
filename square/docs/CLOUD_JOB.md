# Cloud job: verify and continue the n=12 Heilbronn handoff

Run this only in a user-launched cloud session. Never run the compute section on
the operator's Mac.

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

Record the output before continuing. A remote tool that silently lands on
Darwin has failed the gate and must do no further work.

## Step 1: checkout and dependency check

```sh
git status --short
git branch --show-current
python3 --version
cd research/heilbronn_n12
python3 -m pip install -r requirements-research.txt
```

The checkout should be clean before a verification run. Do not discard or
overwrite unexpected changes.

## Step 2: proof and regression suite

```sh
python3 -m unittest -v
python3 incumbent.py
python3 decimal_verifier.py
python3 tangent_certificate.py
python3 n11_insertion.py
python3 d4_interval_certificate.py
```

Capture complete stdout, exit codes, Python version, and elapsed time. A solver
timeout, numerical warning, or incomplete interval queue is not a pass.

## Step 3: reproduce the traversal diagnostic

```sh
python3 global_interval_branch.py --max-boxes 40 --queue-policy breadth
python3 global_interval_branch.py --max-boxes 40 --queue-policy depth
```

Expected current diagnostic:

| policy | visited | discarded | pending | max depth | status |
|---|---:|---:|---:|---:|---|
| breadth | 40 | 0 | 41 | 5 | `INCOMPLETE` |
| depth | 40 | 4 | 33 | 34 | `INCOMPLETE` |

Any changed numbers require investigation, but matching them still does not
prove a global bound.

## Step 4: bounded continuation experiment

After Steps 0--3 pass, run the same code at a shared larger cloud budget:

```sh
python3 global_interval_branch.py --max-boxes 1000 --queue-policy breadth
python3 global_interval_branch.py --max-boxes 1000 --queue-policy depth
```

Report visited boxes, exact discard reasons, pending boxes, maximum depth,
largest pending upper bound, and strict-witness count. Preserve the word
`INCOMPLETE` whenever the queue is nonempty.

Then measure the exact anchor-triangle propagation at the same shared budget:

```sh
python3 global_interval_branch.py --max-boxes 1000 --queue-policy breadth --anchor-propagation anchored
python3 global_interval_branch.py --max-boxes 1000 --queue-policy depth --anchor-propagation anchored
```

For these two runs additionally report `anchor_trims` and the
`anchor-triangle` discard-reason count. The propagation is an exact optional
reduction; it changes neither the meaning of a completed cover nor the
`INCOMPLETE` semantics of a finite budget.

## Step 5: return results

Add a dated `CLOUD_RESULTS_YYYY-MM-DD.md` containing:

- the Step-0 environment evidence;
- the exact commit SHA;
- every command and exit code;
- full test totals;
- the traversal tables and discard-reason counts;
- any discrepancy or blocker without reinterpretation.

Commit only the result document and any narrowly justified fixes. Do not add a
GitHub Actions workflow; this repository's verification gate is local/cloud
execution recorded in the research artifact.
