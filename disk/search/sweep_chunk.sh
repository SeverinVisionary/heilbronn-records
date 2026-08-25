#!/bin/sh
# One sweep chunk: the ANNEALER is launched by the shell (a child exec'd from
# Python inherits a background QoS on macOS and runs ~15x slower), then the
# LP-polish/certify half is absorbed by Python.
#
# usage: sh sweep_chunk.sh <n> <restarts> <iters> <threads> <seed> [state]
set -e
cd "$(dirname "$0")"
N="$1"; R="$2"; IT="$3"; TH="$4"; SEED="$5"; STATE="${6:-}"
./circle_search "$N" "$IT" "$R" "$TH" "$SEED" "$R" > "chunk_$N.txt" 2>/dev/null
if [ -n "$STATE" ]; then
  python3 -u absorb_chunk.py "$N" "chunk_$N.txt" "$TH" "$STATE"
else
  python3 -u absorb_chunk.py "$N" "chunk_$N.txt" "$TH"
fi
