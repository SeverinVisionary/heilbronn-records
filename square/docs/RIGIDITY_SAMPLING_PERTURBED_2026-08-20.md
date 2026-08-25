# Run 7 — perturbed-mode Part B sampling of the rigidity teeth test

**Date:** 2026-08-20. **Status:** on-demand cloud verification run 7 for
`RIGIDITY_CORE_SPEC_2026-08-20.md`, Part B (sampling, numerical).

## Preamble

Run 7 executes the perturbed-mode leg of the Part B sampling protocol
(`rigidity_sampling.py --seed-mode perturbed`) using the incumbent frame as
the seed, then locally polishing with independent noise. Run 6 (still
executing on its own branch, not touched by this run) exercised the blind
random-start generator and found near-record thresholds to be unreachable
by blind starts within the trial budget; run 7 answers the follow-up
question — under a warm-start generator, which triangles of the 20 active
incumbent set recur (matched=True kept samples), and can a kept sample
land outside the incumbent orbit (matched=False)?

Every numeric output in this document is descriptive floating-point
statistics about independently optimized numerical samples. Nothing here
is exact; no sample is a candidate record; the tool's DESCRIPTIVE-ONLY
banner and its perturbed-mode CAVEAT lines are preserved verbatim inside
each campaign's stdout dump.

## Step 0 — environment evidence (verbatim)

```text
Linux vm 6.18.5-fc-v20 #1 SMP PREEMPT_DYNAMIC @0 x86_64 x86_64 x86_64 GNU/Linux
vm
root
4
               total        used        free      shared  buff/cache   available
Mem:            15Gi       663Mi        14Gi       4.8Mi       563Mi        15Gi
Swap:             0B          0B          0B
Python 3.11.15
```

Environment gate: Linux x86_64 confirmed; hostname `vm`; not the local
Mac.

## Step 1 — pinned checkout

- Base branch: `codex/heilbronn-n12-global`
- Local branch: `cloud/heilbronn-n12-verify-7`
- `git rev-parse HEAD` → `f59f1aa57c7e9084cdaecee6c762bb7918e15207` (matches
  the pin exactly)
- Working tree clean before compute.

## Step 2 — dependencies

Installed from `research/heilbronn_n12/requirements-research.txt`:

- numpy 2.0.2
- scipy 1.13.1

## Step 3 — commands (serial)

### (a) `python3 -m unittest -v`

- Exit code: 0
- Elapsed: 72 seconds
- Totals: `Ran 32 tests in 71.973s` — `OK` (32/32 passing)

Full stdout log stored outside the repo at
`$HOME/heilbronn_logs/step_a_unittest.log`.

### (b) perturbed sigma = 0.005, seed_base = 2026082301

```text
python3 rigidity_sampling.py --seed-mode perturbed --sigma 0.005 --trials 400 --seed-base 2026082301 --cores "0,1,2,3,4,5,6,7,8,9,10,11,12,14,16,18,19;0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17;0,1,2,3,4,5,6,7,8,9,10,11,12,13,15,16,18,19"
```

- Exit code: 0
- Elapsed: 4 seconds
- Kept-fraction summary: 400/400 at every threshold; 400/400 matched to the incumbent orbit at every threshold; no matched=False samples; all three cores covered by 400 of 400 samples at every (threshold, delta).

Complete stdout (verbatim from `$HOME/heilbronn_logs/step_b_sigma_0.005.log`):

```text
DESCRIPTIVE-ONLY: float statistics; no exactness claims; no candidate records
incumbent_float 0.0325988586918197
thresholds (0.0324988586918197, 0.0325888586918197, 0.0325978586918197)
seed_mode perturbed sigma 0.005
CAVEAT: perturbed mode samples the basin reachable from the incumbent's
CAVEAT: neighborhood; it is not independent global optimization
trials 400 popsize 16 maxiter 600
sample 2026082301 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.152e-29 matched True
sample 2026082302 min_area 0.032598859 best_threshold 0.032597859 match_distance 5.341e-26 matched True
sample 2026082303 min_area 0.032598859 best_threshold 0.032597859 match_distance 5.224e-26 matched True
sample 2026082304 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.413e-29 matched True
sample 2026082305 min_area 0.032598859 best_threshold 0.032597859 match_distance 3.538e-27 matched True
sample 2026082306 min_area 0.032598859 best_threshold 0.032597859 match_distance 3.045e-28 matched True
sample 2026082307 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.456e-29 matched True
sample 2026082308 min_area 0.032598859 best_threshold 0.032597859 match_distance 3.312e-25 matched True
sample 2026082309 min_area 0.032598859 best_threshold 0.032597859 match_distance 3.690e-30 matched True
sample 2026082310 min_area 0.032598859 best_threshold 0.032597859 match_distance 9.329e-30 matched True
sample 2026082311 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.263e-29 matched True
sample 2026082312 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.278e-28 matched True
sample 2026082313 min_area 0.032598859 best_threshold 0.032597859 match_distance 3.671e-29 matched True
sample 2026082314 min_area 0.032598859 best_threshold 0.032597859 match_distance 6.278e-30 matched True
sample 2026082315 min_area 0.032598859 best_threshold 0.032597859 match_distance 4.614e-29 matched True
sample 2026082316 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.779e-29 matched True
sample 2026082317 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.866e-27 matched True
sample 2026082318 min_area 0.032598859 best_threshold 0.032597859 match_distance 6.345e-27 matched True
sample 2026082319 min_area 0.032598859 best_threshold 0.032597859 match_distance 9.107e-27 matched True
sample 2026082320 min_area 0.032598859 best_threshold 0.032597859 match_distance 4.706e-30 matched True
sample 2026082321 min_area 0.032598859 best_threshold 0.032597859 match_distance 5.239e-30 matched True
sample 2026082322 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.056e-27 matched True
sample 2026082323 min_area 0.032598859 best_threshold 0.032597859 match_distance 3.822e-30 matched True
sample 2026082324 min_area 0.032598859 best_threshold 0.032597859 match_distance 6.862e-30 matched True
sample 2026082325 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.461e-26 matched True
sample 2026082326 min_area 0.032598859 best_threshold 0.032597859 match_distance 9.530e-29 matched True
sample 2026082327 min_area 0.032598859 best_threshold 0.032597859 match_distance 7.497e-26 matched True
sample 2026082328 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.895e-29 matched True
sample 2026082329 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.550e-29 matched True
sample 2026082330 min_area 0.032598859 best_threshold 0.032597859 match_distance 5.623e-28 matched True
sample 2026082331 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.111e-30 matched True
sample 2026082332 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.634e-29 matched True
sample 2026082333 min_area 0.032598859 best_threshold 0.032597859 match_distance 9.570e-30 matched True
sample 2026082334 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.944e-29 matched True
sample 2026082335 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.738e-30 matched True
sample 2026082336 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.130e-28 matched True
sample 2026082337 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.116e-29 matched True
sample 2026082338 min_area 0.032598859 best_threshold 0.032597859 match_distance 4.769e-29 matched True
sample 2026082339 min_area 0.032598859 best_threshold 0.032597859 match_distance 8.546e-30 matched True
sample 2026082340 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.136e-28 matched True
sample 2026082341 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.350e-26 matched True
sample 2026082342 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.784e-26 matched True
sample 2026082343 min_area 0.032598859 best_threshold 0.032597859 match_distance 5.579e-30 matched True
sample 2026082344 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.741e-28 matched True
sample 2026082345 min_area 0.032598859 best_threshold 0.032597859 match_distance 5.508e-29 matched True
sample 2026082346 min_area 0.032598859 best_threshold 0.032597859 match_distance 5.470e-30 matched True
sample 2026082347 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.036e-29 matched True
sample 2026082348 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.492e-28 matched True
sample 2026082349 min_area 0.032598859 best_threshold 0.032597859 match_distance 3.056e-29 matched True
sample 2026082350 min_area 0.032598859 best_threshold 0.032597859 match_distance 3.192e-30 matched True
sample 2026082351 min_area 0.032598859 best_threshold 0.032597859 match_distance 4.929e-30 matched True
sample 2026082352 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.350e-29 matched True
sample 2026082353 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.008e-29 matched True
sample 2026082354 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.891e-30 matched True
sample 2026082355 min_area 0.032598859 best_threshold 0.032597859 match_distance 4.870e-29 matched True
sample 2026082356 min_area 0.032598859 best_threshold 0.032597859 match_distance 4.133e-29 matched True
sample 2026082357 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.089e-28 matched True
sample 2026082358 min_area 0.032598859 best_threshold 0.032597859 match_distance 3.494e-29 matched True
sample 2026082359 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.759e-29 matched True
sample 2026082360 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.385e-29 matched True
sample 2026082361 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.087e-28 matched True
sample 2026082362 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.384e-29 matched True
sample 2026082363 min_area 0.032598859 best_threshold 0.032597859 match_distance 4.615e-30 matched True
sample 2026082364 min_area 0.032598859 best_threshold 0.032597859 match_distance 7.012e-27 matched True
sample 2026082365 min_area 0.032598859 best_threshold 0.032597859 match_distance 9.627e-27 matched True
sample 2026082366 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.669e-27 matched True
sample 2026082367 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.866e-29 matched True
sample 2026082368 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.182e-29 matched True
sample 2026082369 min_area 0.032598859 best_threshold 0.032597859 match_distance 6.824e-30 matched True
sample 2026082370 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.555e-29 matched True
sample 2026082371 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.127e-29 matched True
sample 2026082372 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.139e-30 matched True
sample 2026082373 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.205e-27 matched True
sample 2026082374 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.058e-28 matched True
sample 2026082375 min_area 0.032598859 best_threshold 0.032597859 match_distance 6.333e-27 matched True
sample 2026082376 min_area 0.032598859 best_threshold 0.032597859 match_distance 7.285e-26 matched True
sample 2026082377 min_area 0.032598859 best_threshold 0.032597859 match_distance 7.446e-30 matched True
sample 2026082378 min_area 0.032598859 best_threshold 0.032597859 match_distance 4.597e-28 matched True
sample 2026082379 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.006e-26 matched True
sample 2026082380 min_area 0.032598859 best_threshold 0.032597859 match_distance 8.812e-27 matched True
sample 2026082381 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.345e-27 matched True
sample 2026082382 min_area 0.032598859 best_threshold 0.032597859 match_distance 7.782e-30 matched True
sample 2026082383 min_area 0.032598859 best_threshold 0.032597859 match_distance 3.995e-28 matched True
sample 2026082384 min_area 0.032598859 best_threshold 0.032597859 match_distance 7.162e-30 matched True
sample 2026082385 min_area 0.032598859 best_threshold 0.032597859 match_distance 4.002e-26 matched True
sample 2026082386 min_area 0.032598859 best_threshold 0.032597859 match_distance 6.197e-27 matched True
sample 2026082387 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.967e-26 matched True
sample 2026082388 min_area 0.032598859 best_threshold 0.032597859 match_distance 4.115e-28 matched True
sample 2026082389 min_area 0.032598859 best_threshold 0.032597859 match_distance 5.481e-30 matched True
sample 2026082390 min_area 0.032598859 best_threshold 0.032597859 match_distance 3.609e-29 matched True
sample 2026082391 min_area 0.032598859 best_threshold 0.032597859 match_distance 3.594e-30 matched True
sample 2026082392 min_area 0.032598859 best_threshold 0.032597859 match_distance 4.618e-30 matched True
sample 2026082393 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.002e-29 matched True
sample 2026082394 min_area 0.032598859 best_threshold 0.032597859 match_distance 4.621e-27 matched True
sample 2026082395 min_area 0.032598859 best_threshold 0.032597859 match_distance 7.587e-30 matched True
sample 2026082396 min_area 0.032598859 best_threshold 0.032597859 match_distance 3.506e-30 matched True
sample 2026082397 min_area 0.032598859 best_threshold 0.032597859 match_distance 4.821e-28 matched True
sample 2026082398 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.421e-28 matched True
sample 2026082399 min_area 0.032598859 best_threshold 0.032597859 match_distance 8.452e-30 matched True
sample 2026082400 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.632e-30 matched True
sample 2026082401 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.651e-26 matched True
sample 2026082402 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.225e-27 matched True
sample 2026082403 min_area 0.032598859 best_threshold 0.032597859 match_distance 6.493e-29 matched True
sample 2026082404 min_area 0.032598859 best_threshold 0.032597859 match_distance 3.713e-30 matched True
sample 2026082405 min_area 0.032598859 best_threshold 0.032597859 match_distance 5.230e-27 matched True
sample 2026082406 min_area 0.032598859 best_threshold 0.032597859 match_distance 7.794e-30 matched True
sample 2026082407 min_area 0.032598859 best_threshold 0.032597859 match_distance 9.103e-28 matched True
sample 2026082408 min_area 0.032598859 best_threshold 0.032597859 match_distance 7.943e-27 matched True
sample 2026082409 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.628e-29 matched True
sample 2026082410 min_area 0.032598859 best_threshold 0.032597859 match_distance 5.401e-28 matched True
sample 2026082411 min_area 0.032598859 best_threshold 0.032597859 match_distance 4.387e-30 matched True
sample 2026082412 min_area 0.032598859 best_threshold 0.032597859 match_distance 4.513e-28 matched True
sample 2026082413 min_area 0.032598859 best_threshold 0.032597859 match_distance 7.215e-30 matched True
sample 2026082414 min_area 0.032598859 best_threshold 0.032597859 match_distance 5.101e-28 matched True
sample 2026082415 min_area 0.032598859 best_threshold 0.032597859 match_distance 8.944e-28 matched True
sample 2026082416 min_area 0.032598859 best_threshold 0.032597859 match_distance 5.094e-30 matched True
sample 2026082417 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.356e-28 matched True
sample 2026082418 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.932e-29 matched True
sample 2026082419 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.376e-29 matched True
sample 2026082420 min_area 0.032598859 best_threshold 0.032597859 match_distance 7.013e-30 matched True
sample 2026082421 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.717e-28 matched True
sample 2026082422 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.367e-29 matched True
sample 2026082423 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.932e-30 matched True
sample 2026082424 min_area 0.032598859 best_threshold 0.032597859 match_distance 3.526e-30 matched True
sample 2026082425 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.353e-30 matched True
sample 2026082426 min_area 0.032598859 best_threshold 0.032597859 match_distance 3.045e-26 matched True
sample 2026082427 min_area 0.032598859 best_threshold 0.032597859 match_distance 8.557e-27 matched True
sample 2026082428 min_area 0.032598859 best_threshold 0.032597859 match_distance 5.090e-30 matched True
sample 2026082429 min_area 0.032598859 best_threshold 0.032597859 match_distance 4.910e-28 matched True
sample 2026082430 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.996e-30 matched True
sample 2026082431 min_area 0.032598859 best_threshold 0.032597859 match_distance 5.663e-27 matched True
sample 2026082432 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.084e-29 matched True
sample 2026082433 min_area 0.032598859 best_threshold 0.032597859 match_distance 3.290e-29 matched True
sample 2026082434 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.150e-28 matched True
sample 2026082435 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.216e-28 matched True
sample 2026082436 min_area 0.032598859 best_threshold 0.032597859 match_distance 6.182e-30 matched True
sample 2026082437 min_area 0.032598859 best_threshold 0.032597859 match_distance 4.076e-28 matched True
sample 2026082438 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.259e-29 matched True
sample 2026082439 min_area 0.032598859 best_threshold 0.032597859 match_distance 7.723e-28 matched True
sample 2026082440 min_area 0.032598859 best_threshold 0.032597859 match_distance 6.232e-29 matched True
sample 2026082441 min_area 0.032598859 best_threshold 0.032597859 match_distance 6.184e-30 matched True
sample 2026082442 min_area 0.032598859 best_threshold 0.032597859 match_distance 3.113e-29 matched True
sample 2026082443 min_area 0.032598859 best_threshold 0.032597859 match_distance 5.021e-30 matched True
sample 2026082444 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.137e-29 matched True
sample 2026082445 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.426e-27 matched True
sample 2026082446 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.912e-29 matched True
sample 2026082447 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.372e-29 matched True
sample 2026082448 min_area 0.032598859 best_threshold 0.032597859 match_distance 6.177e-27 matched True
sample 2026082449 min_area 0.032598859 best_threshold 0.032597859 match_distance 4.414e-28 matched True
sample 2026082450 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.815e-27 matched True
sample 2026082451 min_area 0.032598859 best_threshold 0.032597859 match_distance 8.149e-30 matched True
sample 2026082452 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.001e-29 matched True
sample 2026082453 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.580e-28 matched True
sample 2026082454 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.173e-29 matched True
sample 2026082455 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.086e-28 matched True
sample 2026082456 min_area 0.032598859 best_threshold 0.032597859 match_distance 4.375e-30 matched True
sample 2026082457 min_area 0.032598859 best_threshold 0.032597859 match_distance 8.215e-29 matched True
sample 2026082458 min_area 0.032598859 best_threshold 0.032597859 match_distance 7.167e-30 matched True
sample 2026082459 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.759e-28 matched True
sample 2026082460 min_area 0.032598859 best_threshold 0.032597859 match_distance 4.433e-29 matched True
sample 2026082461 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.866e-30 matched True
sample 2026082462 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.099e-28 matched True
sample 2026082463 min_area 0.032598859 best_threshold 0.032597859 match_distance 4.401e-30 matched True
sample 2026082464 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.367e-28 matched True
sample 2026082465 min_area 0.032598859 best_threshold 0.032597859 match_distance 3.766e-30 matched True
sample 2026082466 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.820e-30 matched True
sample 2026082467 min_area 0.032598859 best_threshold 0.032597859 match_distance 3.468e-30 matched True
sample 2026082468 min_area 0.032598859 best_threshold 0.032597859 match_distance 5.296e-29 matched True
sample 2026082469 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.241e-30 matched True
sample 2026082470 min_area 0.032598859 best_threshold 0.032597859 match_distance 3.863e-30 matched True
sample 2026082471 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.880e-30 matched True
sample 2026082472 min_area 0.032598859 best_threshold 0.032597859 match_distance 3.409e-29 matched True
sample 2026082473 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.728e-29 matched True
sample 2026082474 min_area 0.032598859 best_threshold 0.032597859 match_distance 3.415e-28 matched True
sample 2026082475 min_area 0.032598859 best_threshold 0.032597859 match_distance 9.110e-27 matched True
sample 2026082476 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.666e-28 matched True
sample 2026082477 min_area 0.032598859 best_threshold 0.032597859 match_distance 4.974e-29 matched True
sample 2026082478 min_area 0.032598859 best_threshold 0.032597859 match_distance 3.830e-26 matched True
sample 2026082479 min_area 0.032598859 best_threshold 0.032597859 match_distance 4.915e-30 matched True
sample 2026082480 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.329e-29 matched True
sample 2026082481 min_area 0.032598859 best_threshold 0.032597859 match_distance 9.535e-30 matched True
sample 2026082482 min_area 0.032598859 best_threshold 0.032597859 match_distance 4.864e-30 matched True
sample 2026082483 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.895e-28 matched True
sample 2026082484 min_area 0.032598859 best_threshold 0.032597859 match_distance 8.388e-26 matched True
sample 2026082485 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.878e-26 matched True
sample 2026082486 min_area 0.032598859 best_threshold 0.032597859 match_distance 3.466e-27 matched True
sample 2026082487 min_area 0.032598859 best_threshold 0.032597859 match_distance 6.848e-28 matched True
sample 2026082488 min_area 0.032598859 best_threshold 0.032597859 match_distance 7.575e-28 matched True
sample 2026082489 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.041e-28 matched True
sample 2026082490 min_area 0.032598859 best_threshold 0.032597859 match_distance 4.018e-29 matched True
sample 2026082491 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.560e-27 matched True
sample 2026082492 min_area 0.032598859 best_threshold 0.032597859 match_distance 8.955e-28 matched True
sample 2026082493 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.495e-30 matched True
sample 2026082494 min_area 0.032598859 best_threshold 0.032597859 match_distance 9.366e-30 matched True
sample 2026082495 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.798e-29 matched True
sample 2026082496 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.732e-28 matched True
sample 2026082497 min_area 0.032598859 best_threshold 0.032597859 match_distance 5.615e-30 matched True
sample 2026082498 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.426e-29 matched True
sample 2026082499 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.635e-28 matched True
sample 2026082500 min_area 0.032598859 best_threshold 0.032597859 match_distance 5.459e-30 matched True
sample 2026082501 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.658e-29 matched True
sample 2026082502 min_area 0.032598859 best_threshold 0.032597859 match_distance 4.335e-30 matched True
sample 2026082503 min_area 0.032598859 best_threshold 0.032597859 match_distance 4.031e-29 matched True
sample 2026082504 min_area 0.032598859 best_threshold 0.032597859 match_distance 6.528e-29 matched True
sample 2026082505 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.372e-27 matched True
sample 2026082506 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.468e-28 matched True
sample 2026082507 min_area 0.032598859 best_threshold 0.032597859 match_distance 6.730e-30 matched True
sample 2026082508 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.242e-28 matched True
sample 2026082509 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.138e-27 matched True
sample 2026082510 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.590e-28 matched True
sample 2026082511 min_area 0.032598859 best_threshold 0.032597859 match_distance 7.612e-27 matched True
sample 2026082512 min_area 0.032598859 best_threshold 0.032597859 match_distance 3.923e-29 matched True
sample 2026082513 min_area 0.032598859 best_threshold 0.032597859 match_distance 8.204e-30 matched True
sample 2026082514 min_area 0.032598859 best_threshold 0.032597859 match_distance 7.519e-28 matched True
sample 2026082515 min_area 0.032598859 best_threshold 0.032597859 match_distance 8.080e-30 matched True
sample 2026082516 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.848e-28 matched True
sample 2026082517 min_area 0.032598859 best_threshold 0.032597859 match_distance 4.696e-29 matched True
sample 2026082518 min_area 0.032598859 best_threshold 0.032597859 match_distance 8.829e-30 matched True
sample 2026082519 min_area 0.032598859 best_threshold 0.032597859 match_distance 5.350e-29 matched True
sample 2026082520 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.868e-26 matched True
sample 2026082521 min_area 0.032598859 best_threshold 0.032597859 match_distance 9.556e-27 matched True
sample 2026082522 min_area 0.032598859 best_threshold 0.032597859 match_distance 4.041e-28 matched True
sample 2026082523 min_area 0.032598859 best_threshold 0.032597859 match_distance 4.221e-30 matched True
sample 2026082524 min_area 0.032598859 best_threshold 0.032597859 match_distance 5.884e-30 matched True
sample 2026082525 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.674e-30 matched True
sample 2026082526 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.027e-29 matched True
sample 2026082527 min_area 0.032598859 best_threshold 0.032597859 match_distance 5.904e-27 matched True
sample 2026082528 min_area 0.032598859 best_threshold 0.032597859 match_distance 5.608e-30 matched True
sample 2026082529 min_area 0.032598859 best_threshold 0.032597859 match_distance 6.433e-30 matched True
sample 2026082530 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.410e-27 matched True
sample 2026082531 min_area 0.032598859 best_threshold 0.032597859 match_distance 4.748e-27 matched True
sample 2026082532 min_area 0.032598859 best_threshold 0.032597859 match_distance 3.603e-29 matched True
sample 2026082533 min_area 0.032598859 best_threshold 0.032597859 match_distance 7.980e-30 matched True
sample 2026082534 min_area 0.032598859 best_threshold 0.032597859 match_distance 6.674e-30 matched True
sample 2026082535 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.316e-29 matched True
sample 2026082536 min_area 0.032598859 best_threshold 0.032597859 match_distance 5.346e-27 matched True
sample 2026082537 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.190e-27 matched True
sample 2026082538 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.018e-29 matched True
sample 2026082539 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.697e-26 matched True
sample 2026082540 min_area 0.032598859 best_threshold 0.032597859 match_distance 7.834e-29 matched True
sample 2026082541 min_area 0.032598859 best_threshold 0.032597859 match_distance 6.743e-30 matched True
sample 2026082542 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.987e-30 matched True
sample 2026082543 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.374e-26 matched True
sample 2026082544 min_area 0.032598859 best_threshold 0.032597859 match_distance 8.529e-28 matched True
sample 2026082545 min_area 0.032598859 best_threshold 0.032597859 match_distance 5.742e-29 matched True
sample 2026082546 min_area 0.032598859 best_threshold 0.032597859 match_distance 4.836e-29 matched True
sample 2026082547 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.135e-26 matched True
sample 2026082548 min_area 0.032598859 best_threshold 0.032597859 match_distance 4.837e-29 matched True
sample 2026082549 min_area 0.032598859 best_threshold 0.032597859 match_distance 5.055e-29 matched True
sample 2026082550 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.471e-27 matched True
sample 2026082551 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.800e-28 matched True
sample 2026082552 min_area 0.032598859 best_threshold 0.032597859 match_distance 8.383e-30 matched True
sample 2026082553 min_area 0.032598859 best_threshold 0.032597859 match_distance 6.219e-30 matched True
sample 2026082554 min_area 0.032598859 best_threshold 0.032597859 match_distance 5.061e-28 matched True
sample 2026082555 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.018e-29 matched True
sample 2026082556 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.617e-29 matched True
sample 2026082557 min_area 0.032598859 best_threshold 0.032597859 match_distance 7.220e-30 matched True
sample 2026082558 min_area 0.032598859 best_threshold 0.032597859 match_distance 4.712e-29 matched True
sample 2026082559 min_area 0.032598859 best_threshold 0.032597859 match_distance 3.663e-30 matched True
sample 2026082560 min_area 0.032598859 best_threshold 0.032597859 match_distance 8.287e-29 matched True
sample 2026082561 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.401e-28 matched True
sample 2026082562 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.497e-27 matched True
sample 2026082563 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.807e-27 matched True
sample 2026082564 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.701e-28 matched True
sample 2026082565 min_area 0.032598859 best_threshold 0.032597859 match_distance 5.265e-30 matched True
sample 2026082566 min_area 0.032598859 best_threshold 0.032597859 match_distance 3.099e-28 matched True
sample 2026082567 min_area 0.032598859 best_threshold 0.032597859 match_distance 4.667e-30 matched True
sample 2026082568 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.650e-29 matched True
sample 2026082569 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.470e-28 matched True
sample 2026082570 min_area 0.032598859 best_threshold 0.032597859 match_distance 7.020e-29 matched True
sample 2026082571 min_area 0.032598859 best_threshold 0.032597859 match_distance 8.456e-29 matched True
sample 2026082572 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.349e-29 matched True
sample 2026082573 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.838e-29 matched True
sample 2026082574 min_area 0.032598859 best_threshold 0.032597859 match_distance 3.390e-28 matched True
sample 2026082575 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.923e-29 matched True
sample 2026082576 min_area 0.032598859 best_threshold 0.032597859 match_distance 3.646e-30 matched True
sample 2026082577 min_area 0.032598859 best_threshold 0.032597859 match_distance 8.175e-30 matched True
sample 2026082578 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.362e-27 matched True
sample 2026082579 min_area 0.032598859 best_threshold 0.032597859 match_distance 6.064e-29 matched True
sample 2026082580 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.154e-29 matched True
sample 2026082581 min_area 0.032598859 best_threshold 0.032597859 match_distance 3.289e-28 matched True
sample 2026082582 min_area 0.032598859 best_threshold 0.032597859 match_distance 4.440e-29 matched True
sample 2026082583 min_area 0.032598859 best_threshold 0.032597859 match_distance 7.628e-30 matched True
sample 2026082584 min_area 0.032598859 best_threshold 0.032597859 match_distance 6.918e-30 matched True
sample 2026082585 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.006e-30 matched True
sample 2026082586 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.316e-29 matched True
sample 2026082587 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.419e-29 matched True
sample 2026082588 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.802e-27 matched True
sample 2026082589 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.008e-29 matched True
sample 2026082590 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.668e-29 matched True
sample 2026082591 min_area 0.032598859 best_threshold 0.032597859 match_distance 9.351e-30 matched True
sample 2026082592 min_area 0.032598859 best_threshold 0.032597859 match_distance 8.478e-29 matched True
sample 2026082593 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.041e-28 matched True
sample 2026082594 min_area 0.032598859 best_threshold 0.032597859 match_distance 3.410e-26 matched True
sample 2026082595 min_area 0.032598859 best_threshold 0.032597859 match_distance 7.526e-30 matched True
sample 2026082596 min_area 0.032598859 best_threshold 0.032597859 match_distance 8.654e-29 matched True
sample 2026082597 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.154e-26 matched True
sample 2026082598 min_area 0.032598859 best_threshold 0.032597859 match_distance 4.328e-30 matched True
sample 2026082599 min_area 0.032598859 best_threshold 0.032597859 match_distance 5.329e-30 matched True
sample 2026082600 min_area 0.032598859 best_threshold 0.032597859 match_distance 8.256e-27 matched True
sample 2026082601 min_area 0.032598859 best_threshold 0.032597859 match_distance 6.982e-28 matched True
sample 2026082602 min_area 0.032598859 best_threshold 0.032597859 match_distance 3.313e-29 matched True
sample 2026082603 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.657e-27 matched True
sample 2026082604 min_area 0.032598859 best_threshold 0.032597859 match_distance 4.311e-30 matched True
sample 2026082605 min_area 0.032598859 best_threshold 0.032597859 match_distance 9.463e-29 matched True
sample 2026082606 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.240e-28 matched True
sample 2026082607 min_area 0.032598859 best_threshold 0.032597859 match_distance 5.531e-30 matched True
sample 2026082608 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.501e-26 matched True
sample 2026082609 min_area 0.032598859 best_threshold 0.032597859 match_distance 6.721e-30 matched True
sample 2026082610 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.574e-29 matched True
sample 2026082611 min_area 0.032598859 best_threshold 0.032597859 match_distance 9.798e-30 matched True
sample 2026082612 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.097e-26 matched True
sample 2026082613 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.341e-30 matched True
sample 2026082614 min_area 0.032598859 best_threshold 0.032597859 match_distance 7.281e-27 matched True
sample 2026082615 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.558e-30 matched True
sample 2026082616 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.296e-29 matched True
sample 2026082617 min_area 0.032598859 best_threshold 0.032597859 match_distance 5.688e-30 matched True
sample 2026082618 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.129e-29 matched True
sample 2026082619 min_area 0.032598859 best_threshold 0.032597859 match_distance 7.824e-28 matched True
sample 2026082620 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.629e-28 matched True
sample 2026082621 min_area 0.032598859 best_threshold 0.032597859 match_distance 5.870e-30 matched True
sample 2026082622 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.208e-27 matched True
sample 2026082623 min_area 0.032598859 best_threshold 0.032597859 match_distance 8.255e-30 matched True
sample 2026082624 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.943e-30 matched True
sample 2026082625 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.144e-28 matched True
sample 2026082626 min_area 0.032598859 best_threshold 0.032597859 match_distance 3.372e-30 matched True
sample 2026082627 min_area 0.032598859 best_threshold 0.032597859 match_distance 4.157e-28 matched True
sample 2026082628 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.178e-29 matched True
sample 2026082629 min_area 0.032598859 best_threshold 0.032597859 match_distance 3.595e-29 matched True
sample 2026082630 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.450e-28 matched True
sample 2026082631 min_area 0.032598859 best_threshold 0.032597859 match_distance 9.711e-30 matched True
sample 2026082632 min_area 0.032598859 best_threshold 0.032597859 match_distance 3.748e-29 matched True
sample 2026082633 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.517e-29 matched True
sample 2026082634 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.858e-29 matched True
sample 2026082635 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.275e-27 matched True
sample 2026082636 min_area 0.032598859 best_threshold 0.032597859 match_distance 5.486e-30 matched True
sample 2026082637 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.081e-28 matched True
sample 2026082638 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.680e-30 matched True
sample 2026082639 min_area 0.032598859 best_threshold 0.032597859 match_distance 4.069e-30 matched True
sample 2026082640 min_area 0.032598859 best_threshold 0.032597859 match_distance 3.582e-26 matched True
sample 2026082641 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.375e-27 matched True
sample 2026082642 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.686e-26 matched True
sample 2026082643 min_area 0.032598859 best_threshold 0.032597859 match_distance 5.319e-29 matched True
sample 2026082644 min_area 0.032598859 best_threshold 0.032597859 match_distance 4.640e-30 matched True
sample 2026082645 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.735e-29 matched True
sample 2026082646 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.286e-26 matched True
sample 2026082647 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.664e-29 matched True
sample 2026082648 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.529e-26 matched True
sample 2026082649 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.591e-30 matched True
sample 2026082650 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.208e-29 matched True
sample 2026082651 min_area 0.032598859 best_threshold 0.032597859 match_distance 5.509e-30 matched True
sample 2026082652 min_area 0.032598859 best_threshold 0.032597859 match_distance 8.818e-29 matched True
sample 2026082653 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.813e-28 matched True
sample 2026082654 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.627e-29 matched True
sample 2026082655 min_area 0.032598859 best_threshold 0.032597859 match_distance 3.822e-30 matched True
sample 2026082656 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.149e-29 matched True
sample 2026082657 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.210e-29 matched True
sample 2026082658 min_area 0.032598859 best_threshold 0.032597859 match_distance 4.974e-28 matched True
sample 2026082659 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.086e-29 matched True
sample 2026082660 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.180e-28 matched True
sample 2026082661 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.989e-29 matched True
sample 2026082662 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.645e-29 matched True
sample 2026082663 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.975e-30 matched True
sample 2026082664 min_area 0.032598859 best_threshold 0.032597859 match_distance 5.699e-30 matched True
sample 2026082665 min_area 0.032598859 best_threshold 0.032597859 match_distance 9.491e-31 matched True
sample 2026082666 min_area 0.032598859 best_threshold 0.032597859 match_distance 5.895e-29 matched True
sample 2026082667 min_area 0.032598859 best_threshold 0.032597859 match_distance 6.000e-30 matched True
sample 2026082668 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.263e-27 matched True
sample 2026082669 min_area 0.032598859 best_threshold 0.032597859 match_distance 3.394e-30 matched True
sample 2026082670 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.467e-28 matched True
sample 2026082671 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.906e-27 matched True
sample 2026082672 min_area 0.032598859 best_threshold 0.032597859 match_distance 4.151e-29 matched True
sample 2026082673 min_area 0.032598859 best_threshold 0.032597859 match_distance 6.597e-30 matched True
sample 2026082674 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.997e-30 matched True
sample 2026082675 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.623e-30 matched True
sample 2026082676 min_area 0.032598859 best_threshold 0.032597859 match_distance 5.576e-30 matched True
sample 2026082677 min_area 0.032598859 best_threshold 0.032597859 match_distance 6.345e-27 matched True
sample 2026082678 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.535e-29 matched True
sample 2026082679 min_area 0.032598859 best_threshold 0.032597859 match_distance 3.796e-29 matched True
sample 2026082680 min_area 0.032598859 best_threshold 0.032597859 match_distance 8.601e-31 matched True
sample 2026082681 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.882e-30 matched True
sample 2026082682 min_area 0.032598859 best_threshold 0.032597859 match_distance 8.479e-29 matched True
sample 2026082683 min_area 0.032598859 best_threshold 0.032597859 match_distance 8.498e-28 matched True
sample 2026082684 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.860e-29 matched True
sample 2026082685 min_area 0.032598859 best_threshold 0.032597859 match_distance 9.023e-28 matched True
sample 2026082686 min_area 0.032598859 best_threshold 0.032597859 match_distance 7.803e-30 matched True
sample 2026082687 min_area 0.032598859 best_threshold 0.032597859 match_distance 9.369e-28 matched True
sample 2026082688 min_area 0.032598859 best_threshold 0.032597859 match_distance 8.573e-27 matched True
sample 2026082689 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.536e-28 matched True
sample 2026082690 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.507e-29 matched True
sample 2026082691 min_area 0.032598859 best_threshold 0.032597859 match_distance 4.214e-28 matched True
sample 2026082692 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.567e-27 matched True
sample 2026082693 min_area 0.032598859 best_threshold 0.032597859 match_distance 9.521e-30 matched True
sample 2026082694 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.047e-29 matched True
sample 2026082695 min_area 0.032598859 best_threshold 0.032597859 match_distance 5.769e-28 matched True
sample 2026082696 min_area 0.032598859 best_threshold 0.032597859 match_distance 3.250e-30 matched True
sample 2026082697 min_area 0.032598859 best_threshold 0.032597859 match_distance 5.537e-30 matched True
sample 2026082698 min_area 0.032598859 best_threshold 0.032597859 match_distance 3.105e-26 matched True
sample 2026082699 min_area 0.032598859 best_threshold 0.032597859 match_distance 9.682e-30 matched True
sample 2026082700 min_area 0.032598859 best_threshold 0.032597859 match_distance 6.689e-26 matched True
threshold 0.032498859 kept 400 of 400
  matched_to_incumbent_orbit 400
  match_distance_min_median_max 8.601e-31 3.494e-29 3.312e-25
  delta 0.001 matched_samples_covering_all_20_active 400
  delta 0.001 core 0 covered_by 400 of 400
  delta 0.001 core 1 covered_by 400 of 400
  delta 0.001 core 2 covered_by 400 of 400
  delta 0.001 unmatched_samples 0 distinct_hypergraphs 0
  delta 0.0001 matched_samples_covering_all_20_active 400
  delta 0.0001 core 0 covered_by 400 of 400
  delta 0.0001 core 1 covered_by 400 of 400
  delta 0.0001 core 2 covered_by 400 of 400
  delta 0.0001 unmatched_samples 0 distinct_hypergraphs 0
threshold 0.032588859 kept 400 of 400
  matched_to_incumbent_orbit 400
  match_distance_min_median_max 8.601e-31 3.494e-29 3.312e-25
  delta 0.001 matched_samples_covering_all_20_active 400
  delta 0.001 core 0 covered_by 400 of 400
  delta 0.001 core 1 covered_by 400 of 400
  delta 0.001 core 2 covered_by 400 of 400
  delta 0.001 unmatched_samples 0 distinct_hypergraphs 0
  delta 0.0001 matched_samples_covering_all_20_active 400
  delta 0.0001 core 0 covered_by 400 of 400
  delta 0.0001 core 1 covered_by 400 of 400
  delta 0.0001 core 2 covered_by 400 of 400
  delta 0.0001 unmatched_samples 0 distinct_hypergraphs 0
threshold 0.032597859 kept 400 of 400
  matched_to_incumbent_orbit 400
  match_distance_min_median_max 8.601e-31 3.494e-29 3.312e-25
  delta 0.001 matched_samples_covering_all_20_active 400
  delta 0.001 core 0 covered_by 400 of 400
  delta 0.001 core 1 covered_by 400 of 400
  delta 0.001 core 2 covered_by 400 of 400
  delta 0.001 unmatched_samples 0 distinct_hypergraphs 0
  delta 0.0001 matched_samples_covering_all_20_active 400
  delta 0.0001 core 0 covered_by 400 of 400
  delta 0.0001 core 1 covered_by 400 of 400
  delta 0.0001 core 2 covered_by 400 of 400
  delta 0.0001 unmatched_samples 0 distinct_hypergraphs 0
status DESCRIPTIVE: sampling evidence only; rigidity verdicts come from the exact Part A scan
```

### (c) perturbed sigma = 0.02, seed_base = 2026082701

```text
python3 rigidity_sampling.py --seed-mode perturbed --sigma 0.02 --trials 400 --seed-base 2026082701 --cores "0,1,2,3,4,5,6,7,8,9,10,11,12,14,16,18,19;0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17;0,1,2,3,4,5,6,7,8,9,10,11,12,13,15,16,18,19"
```

- Exit code: 0
- Elapsed: 6 seconds
- Kept-fraction summary: 393/400 at every threshold (7 trials landed below [erratum 2026-08-20, panel finding: original said "above"; the filter drops trials below the window] the near-record window and were dropped); all 393 kept samples matched to the incumbent orbit; no matched=False samples; all three cores covered by 393 of 393 samples at every (threshold, delta).

Complete stdout (verbatim from `$HOME/heilbronn_logs/step_c_sigma_0.02.log`):

```text
DESCRIPTIVE-ONLY: float statistics; no exactness claims; no candidate records
incumbent_float 0.0325988586918197
thresholds (0.0324988586918197, 0.0325888586918197, 0.0325978586918197)
seed_mode perturbed sigma 0.02
CAVEAT: perturbed mode samples the basin reachable from the incumbent's
CAVEAT: neighborhood; it is not independent global optimization
trials 400 popsize 16 maxiter 600
sample 2026082701 min_area 0.032598859 best_threshold 0.032597859 match_distance 6.761e-30 matched True
sample 2026082702 min_area 0.032598859 best_threshold 0.032597859 match_distance 7.153e-30 matched True
sample 2026082703 min_area 0.032598859 best_threshold 0.032597859 match_distance 8.455e-30 matched True
sample 2026082704 min_area 0.032598859 best_threshold 0.032597859 match_distance 7.221e-30 matched True
sample 2026082705 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.345e-29 matched True
sample 2026082706 min_area 0.032598859 best_threshold 0.032597859 match_distance 5.255e-30 matched True
sample 2026082707 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.182e-29 matched True
sample 2026082708 min_area 0.032598859 best_threshold 0.032597859 match_distance 3.397e-30 matched True
sample 2026082709 min_area 0.032598859 best_threshold 0.032597859 match_distance 4.707e-30 matched True
sample 2026082710 min_area 0.032598859 best_threshold 0.032597859 match_distance 8.420e-30 matched True
sample 2026082711 min_area 0.032598859 best_threshold 0.032597859 match_distance 7.741e-30 matched True
sample 2026082712 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.956e-29 matched True
sample 2026082713 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.904e-30 matched True
sample 2026082714 min_area 0.032598859 best_threshold 0.032597859 match_distance 3.001e-29 matched True
sample 2026082715 min_area 0.032598859 best_threshold 0.032597859 match_distance 7.057e-30 matched True
sample 2026082716 min_area 0.032598859 best_threshold 0.032597859 match_distance 6.923e-30 matched True
sample 2026082717 min_area 0.032598859 best_threshold 0.032597859 match_distance 4.547e-30 matched True
sample 2026082718 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.536e-30 matched True
sample 2026082719 min_area 0.032598859 best_threshold 0.032597859 match_distance 7.011e-30 matched True
sample 2026082720 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.805e-29 matched True
sample 2026082721 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.634e-29 matched True
sample 2026082722 min_area 0.032598859 best_threshold 0.032597859 match_distance 6.290e-30 matched True
sample 2026082723 min_area 0.032598859 best_threshold 0.032597859 match_distance 4.130e-30 matched True
sample 2026082724 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.589e-30 matched True
sample 2026082725 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.070e-29 matched True
sample 2026082726 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.060e-24 matched True
sample 2026082727 min_area 0.032598859 best_threshold 0.032597859 match_distance 4.937e-30 matched True
sample 2026082728 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.308e-27 matched True
sample 2026082729 min_area 0.032598859 best_threshold 0.032597859 match_distance 6.013e-30 matched True
sample 2026082730 min_area 0.032598859 best_threshold 0.032597859 match_distance 6.546e-30 matched True
sample 2026082731 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.024e-29 matched True
sample 2026082733 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.169e-29 matched True
sample 2026082734 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.038e-29 matched True
sample 2026082735 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.939e-29 matched True
sample 2026082736 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.652e-28 matched True
sample 2026082737 min_area 0.032598859 best_threshold 0.032597859 match_distance 9.187e-27 matched True
sample 2026082738 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.679e-29 matched True
sample 2026082739 min_area 0.032598859 best_threshold 0.032597859 match_distance 3.950e-30 matched True
sample 2026082740 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.006e-29 matched True
sample 2026082741 min_area 0.032598859 best_threshold 0.032597859 match_distance 6.124e-30 matched True
sample 2026082742 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.096e-29 matched True
sample 2026082743 min_area 0.032598859 best_threshold 0.032597859 match_distance 6.516e-30 matched True
sample 2026082744 min_area 0.032598859 best_threshold 0.032597859 match_distance 5.669e-30 matched True
sample 2026082745 min_area 0.032598859 best_threshold 0.032597859 match_distance 4.175e-30 matched True
sample 2026082746 min_area 0.032598859 best_threshold 0.032597859 match_distance 8.023e-30 matched True
sample 2026082747 min_area 0.032598859 best_threshold 0.032597859 match_distance 4.660e-30 matched True
sample 2026082748 min_area 0.032598859 best_threshold 0.032597859 match_distance 8.225e-30 matched True
sample 2026082749 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.201e-27 matched True
sample 2026082750 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.995e-30 matched True
sample 2026082751 min_area 0.032598859 best_threshold 0.032597859 match_distance 9.345e-29 matched True
sample 2026082752 min_area 0.032598859 best_threshold 0.032597859 match_distance 7.279e-30 matched True
sample 2026082753 min_area 0.032598859 best_threshold 0.032597859 match_distance 3.511e-30 matched True
sample 2026082754 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.972e-29 matched True
sample 2026082755 min_area 0.032598859 best_threshold 0.032597859 match_distance 3.587e-30 matched True
sample 2026082756 min_area 0.032598859 best_threshold 0.032597859 match_distance 5.854e-30 matched True
sample 2026082757 min_area 0.032598859 best_threshold 0.032597859 match_distance 5.243e-30 matched True
sample 2026082758 min_area 0.032598859 best_threshold 0.032597859 match_distance 6.794e-30 matched True
sample 2026082759 min_area 0.032598859 best_threshold 0.032597859 match_distance 6.340e-28 matched True
sample 2026082760 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.157e-29 matched True
sample 2026082761 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.152e-27 matched True
sample 2026082762 min_area 0.032598859 best_threshold 0.032597859 match_distance 9.780e-30 matched True
sample 2026082763 min_area 0.032598859 best_threshold 0.032597859 match_distance 4.970e-30 matched True
sample 2026082764 min_area 0.032598859 best_threshold 0.032597859 match_distance 5.258e-30 matched True
sample 2026082765 min_area 0.032598859 best_threshold 0.032597859 match_distance 5.277e-30 matched True
sample 2026082766 min_area 0.032598859 best_threshold 0.032597859 match_distance 3.802e-28 matched True
sample 2026082767 min_area 0.032598859 best_threshold 0.032597859 match_distance 7.072e-30 matched True
sample 2026082768 min_area 0.032598859 best_threshold 0.032597859 match_distance 6.572e-30 matched True
sample 2026082769 min_area 0.032598859 best_threshold 0.032597859 match_distance 3.688e-29 matched True
sample 2026082770 min_area 0.032598859 best_threshold 0.032597859 match_distance 5.871e-30 matched True
sample 2026082771 min_area 0.032598859 best_threshold 0.032597859 match_distance 6.185e-30 matched True
sample 2026082772 min_area 0.032598859 best_threshold 0.032597859 match_distance 5.991e-30 matched True
sample 2026082773 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.429e-29 matched True
sample 2026082774 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.588e-29 matched True
sample 2026082775 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.046e-29 matched True
sample 2026082776 min_area 0.032598859 best_threshold 0.032597859 match_distance 5.752e-29 matched True
sample 2026082777 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.388e-30 matched True
sample 2026082778 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.109e-29 matched True
sample 2026082779 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.061e-29 matched True
sample 2026082780 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.810e-29 matched True
sample 2026082781 min_area 0.032598859 best_threshold 0.032597859 match_distance 5.859e-30 matched True
sample 2026082782 min_area 0.032598859 best_threshold 0.032597859 match_distance 3.016e-30 matched True
sample 2026082783 min_area 0.032598859 best_threshold 0.032597859 match_distance 8.224e-30 matched True
sample 2026082784 min_area 0.032598859 best_threshold 0.032597859 match_distance 6.618e-30 matched True
sample 2026082785 min_area 0.032598859 best_threshold 0.032597859 match_distance 3.186e-30 matched True
sample 2026082786 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.186e-29 matched True
sample 2026082787 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.486e-29 matched True
sample 2026082788 min_area 0.032598859 best_threshold 0.032597859 match_distance 5.637e-30 matched True
sample 2026082789 min_area 0.032598859 best_threshold 0.032597859 match_distance 3.368e-30 matched True
sample 2026082790 min_area 0.032598859 best_threshold 0.032597859 match_distance 4.064e-29 matched True
sample 2026082791 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.424e-30 matched True
sample 2026082792 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.477e-27 matched True
sample 2026082793 min_area 0.032598859 best_threshold 0.032597859 match_distance 8.242e-30 matched True
sample 2026082794 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.184e-29 matched True
sample 2026082795 min_area 0.032598859 best_threshold 0.032597859 match_distance 8.279e-30 matched True
sample 2026082796 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.326e-30 matched True
sample 2026082797 min_area 0.032598859 best_threshold 0.032597859 match_distance 9.824e-30 matched True
sample 2026082798 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.016e-26 matched True
sample 2026082799 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.479e-28 matched True
sample 2026082800 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.843e-30 matched True
sample 2026082801 min_area 0.032598859 best_threshold 0.032597859 match_distance 4.107e-30 matched True
sample 2026082803 min_area 0.032598859 best_threshold 0.032597859 match_distance 3.940e-30 matched True
sample 2026082804 min_area 0.032598859 best_threshold 0.032597859 match_distance 6.614e-30 matched True
sample 2026082805 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.516e-26 matched True
sample 2026082806 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.487e-30 matched True
sample 2026082807 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.311e-29 matched True
sample 2026082808 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.032e-27 matched True
sample 2026082809 min_area 0.032598859 best_threshold 0.032597859 match_distance 4.020e-30 matched True
sample 2026082810 min_area 0.032598859 best_threshold 0.032597859 match_distance 9.072e-29 matched True
sample 2026082811 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.675e-29 matched True
sample 2026082812 min_area 0.032598859 best_threshold 0.032597859 match_distance 8.168e-29 matched True
sample 2026082813 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.551e-29 matched True
sample 2026082814 min_area 0.032598859 best_threshold 0.032597859 match_distance 6.179e-30 matched True
sample 2026082815 min_area 0.032598859 best_threshold 0.032597859 match_distance 7.861e-30 matched True
sample 2026082816 min_area 0.032598859 best_threshold 0.032597859 match_distance 3.530e-30 matched True
sample 2026082817 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.445e-29 matched True
sample 2026082818 min_area 0.032598859 best_threshold 0.032597859 match_distance 9.513e-29 matched True
sample 2026082819 min_area 0.032598859 best_threshold 0.032597859 match_distance 6.163e-30 matched True
sample 2026082820 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.958e-29 matched True
sample 2026082821 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.316e-29 matched True
sample 2026082822 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.674e-28 matched True
sample 2026082823 min_area 0.032598859 best_threshold 0.032597859 match_distance 4.699e-27 matched True
sample 2026082825 min_area 0.032598859 best_threshold 0.032597859 match_distance 5.983e-30 matched True
sample 2026082826 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.061e-29 matched True
sample 2026082827 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.003e-29 matched True
sample 2026082828 min_area 0.032598859 best_threshold 0.032597859 match_distance 6.900e-30 matched True
sample 2026082829 min_area 0.032598859 best_threshold 0.032597859 match_distance 9.625e-29 matched True
sample 2026082830 min_area 0.032598859 best_threshold 0.032597859 match_distance 3.564e-30 matched True
sample 2026082831 min_area 0.032598859 best_threshold 0.032597859 match_distance 5.819e-30 matched True
sample 2026082832 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.412e-27 matched True
sample 2026082833 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.647e-30 matched True
sample 2026082834 min_area 0.032598859 best_threshold 0.032597859 match_distance 4.187e-30 matched True
sample 2026082835 min_area 0.032598859 best_threshold 0.032597859 match_distance 4.298e-30 matched True
sample 2026082836 min_area 0.032598859 best_threshold 0.032597859 match_distance 3.649e-29 matched True
sample 2026082837 min_area 0.032598859 best_threshold 0.032597859 match_distance 5.751e-30 matched True
sample 2026082838 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.887e-30 matched True
sample 2026082839 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.195e-30 matched True
sample 2026082840 min_area 0.032598859 best_threshold 0.032597859 match_distance 4.304e-30 matched True
sample 2026082841 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.040e-29 matched True
sample 2026082842 min_area 0.032598859 best_threshold 0.032597859 match_distance 3.381e-30 matched True
sample 2026082843 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.524e-28 matched True
sample 2026082844 min_area 0.032598859 best_threshold 0.032597859 match_distance 6.897e-27 matched True
sample 2026082845 min_area 0.032598859 best_threshold 0.032597859 match_distance 7.064e-29 matched True
sample 2026082846 min_area 0.032598859 best_threshold 0.032597859 match_distance 5.400e-30 matched True
sample 2026082847 min_area 0.032598859 best_threshold 0.032597859 match_distance 9.287e-30 matched True
sample 2026082848 min_area 0.032598859 best_threshold 0.032597859 match_distance 4.503e-30 matched True
sample 2026082849 min_area 0.032598859 best_threshold 0.032597859 match_distance 6.483e-30 matched True
sample 2026082850 min_area 0.032598859 best_threshold 0.032597859 match_distance 3.291e-30 matched True
sample 2026082851 min_area 0.032598859 best_threshold 0.032597859 match_distance 8.179e-30 matched True
sample 2026082853 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.408e-29 matched True
sample 2026082854 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.216e-29 matched True
sample 2026082855 min_area 0.032598859 best_threshold 0.032597859 match_distance 5.478e-30 matched True
sample 2026082856 min_area 0.032598859 best_threshold 0.032597859 match_distance 3.613e-27 matched True
sample 2026082857 min_area 0.032598859 best_threshold 0.032597859 match_distance 6.277e-30 matched True
sample 2026082858 min_area 0.032598859 best_threshold 0.032597859 match_distance 5.955e-30 matched True
sample 2026082859 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.610e-30 matched True
sample 2026082860 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.440e-29 matched True
sample 2026082861 min_area 0.032598859 best_threshold 0.032597859 match_distance 3.941e-30 matched True
sample 2026082862 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.693e-30 matched True
sample 2026082863 min_area 0.032598859 best_threshold 0.032597859 match_distance 5.058e-30 matched True
sample 2026082864 min_area 0.032598859 best_threshold 0.032597859 match_distance 4.751e-30 matched True
sample 2026082865 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.548e-29 matched True
sample 2026082866 min_area 0.032598859 best_threshold 0.032597859 match_distance 8.474e-27 matched True
sample 2026082867 min_area 0.032598859 best_threshold 0.032597859 match_distance 8.358e-30 matched True
sample 2026082868 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.912e-30 matched True
sample 2026082869 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.652e-27 matched True
sample 2026082870 min_area 0.032598859 best_threshold 0.032597859 match_distance 4.271e-30 matched True
sample 2026082871 min_area 0.032598859 best_threshold 0.032597859 match_distance 7.649e-30 matched True
sample 2026082872 min_area 0.032598859 best_threshold 0.032597859 match_distance 7.089e-27 matched True
sample 2026082873 min_area 0.032598859 best_threshold 0.032597859 match_distance 6.782e-30 matched True
sample 2026082874 min_area 0.032598859 best_threshold 0.032597859 match_distance 3.444e-29 matched True
sample 2026082875 min_area 0.032598859 best_threshold 0.032597859 match_distance 3.303e-29 matched True
sample 2026082876 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.183e-29 matched True
sample 2026082877 min_area 0.032598859 best_threshold 0.032597859 match_distance 8.370e-30 matched True
sample 2026082878 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.424e-29 matched True
sample 2026082879 min_area 0.032598859 best_threshold 0.032597859 match_distance 3.113e-30 matched True
sample 2026082880 min_area 0.032598859 best_threshold 0.032597859 match_distance 4.395e-26 matched True
sample 2026082881 min_area 0.032598859 best_threshold 0.032597859 match_distance 4.440e-30 matched True
sample 2026082882 min_area 0.032598859 best_threshold 0.032597859 match_distance 5.309e-30 matched True
sample 2026082883 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.740e-29 matched True
sample 2026082884 min_area 0.032598859 best_threshold 0.032597859 match_distance 5.277e-28 matched True
sample 2026082885 min_area 0.032598859 best_threshold 0.032597859 match_distance 5.412e-30 matched True
sample 2026082886 min_area 0.032598859 best_threshold 0.032597859 match_distance 6.333e-30 matched True
sample 2026082887 min_area 0.032598859 best_threshold 0.032597859 match_distance 6.926e-30 matched True
sample 2026082888 min_area 0.032598859 best_threshold 0.032597859 match_distance 5.137e-30 matched True
sample 2026082889 min_area 0.032598859 best_threshold 0.032597859 match_distance 7.199e-30 matched True
sample 2026082890 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.445e-29 matched True
sample 2026082891 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.600e-29 matched True
sample 2026082892 min_area 0.032598859 best_threshold 0.032597859 match_distance 6.502e-30 matched True
sample 2026082893 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.826e-27 matched True
sample 2026082894 min_area 0.032598859 best_threshold 0.032597859 match_distance 6.818e-30 matched True
sample 2026082895 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.873e-28 matched True
sample 2026082896 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.106e-29 matched True
sample 2026082897 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.078e-29 matched True
sample 2026082898 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.473e-29 matched True
sample 2026082899 min_area 0.032598859 best_threshold 0.032597859 match_distance 6.619e-29 matched True
sample 2026082900 min_area 0.032598859 best_threshold 0.032597859 match_distance 6.195e-30 matched True
sample 2026082901 min_area 0.032598859 best_threshold 0.032597859 match_distance 3.174e-30 matched True
sample 2026082902 min_area 0.032598859 best_threshold 0.032597859 match_distance 3.773e-30 matched True
sample 2026082903 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.109e-26 matched True
sample 2026082904 min_area 0.032598859 best_threshold 0.032597859 match_distance 5.750e-30 matched True
sample 2026082905 min_area 0.032598859 best_threshold 0.032597859 match_distance 5.160e-30 matched True
sample 2026082906 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.212e-28 matched True
sample 2026082907 min_area 0.032598859 best_threshold 0.032597859 match_distance 8.367e-30 matched True
sample 2026082908 min_area 0.032598859 best_threshold 0.032597859 match_distance 5.552e-30 matched True
sample 2026082909 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.502e-29 matched True
sample 2026082910 min_area 0.032598859 best_threshold 0.032597859 match_distance 6.224e-29 matched True
sample 2026082911 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.160e-28 matched True
sample 2026082912 min_area 0.032598859 best_threshold 0.032597859 match_distance 7.550e-31 matched True
sample 2026082913 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.405e-29 matched True
sample 2026082914 min_area 0.032598859 best_threshold 0.032597859 match_distance 8.390e-30 matched True
sample 2026082915 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.314e-29 matched True
sample 2026082916 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.270e-29 matched True
sample 2026082917 min_area 0.032598859 best_threshold 0.032597859 match_distance 5.728e-30 matched True
sample 2026082918 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.915e-30 matched True
sample 2026082919 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.577e-29 matched True
sample 2026082920 min_area 0.032598859 best_threshold 0.032597859 match_distance 6.920e-29 matched True
sample 2026082922 min_area 0.032598859 best_threshold 0.032597859 match_distance 6.376e-30 matched True
sample 2026082923 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.671e-29 matched True
sample 2026082924 min_area 0.032598859 best_threshold 0.032597859 match_distance 4.601e-27 matched True
sample 2026082925 min_area 0.032598859 best_threshold 0.032597859 match_distance 7.449e-30 matched True
sample 2026082926 min_area 0.032598859 best_threshold 0.032597859 match_distance 7.614e-30 matched True
sample 2026082927 min_area 0.032598859 best_threshold 0.032597859 match_distance 3.219e-30 matched True
sample 2026082928 min_area 0.032598859 best_threshold 0.032597859 match_distance 9.327e-30 matched True
sample 2026082929 min_area 0.032598859 best_threshold 0.032597859 match_distance 3.879e-29 matched True
sample 2026082930 min_area 0.032598859 best_threshold 0.032597859 match_distance 6.964e-30 matched True
sample 2026082931 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.129e-29 matched True
sample 2026082932 min_area 0.032598859 best_threshold 0.032597859 match_distance 9.275e-30 matched True
sample 2026082933 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.912e-29 matched True
sample 2026082934 min_area 0.032598859 best_threshold 0.032597859 match_distance 8.092e-27 matched True
sample 2026082935 min_area 0.032598859 best_threshold 0.032597859 match_distance 8.184e-30 matched True
sample 2026082936 min_area 0.032598859 best_threshold 0.032597859 match_distance 7.342e-30 matched True
sample 2026082937 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.028e-30 matched True
sample 2026082938 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.207e-29 matched True
sample 2026082939 min_area 0.032598859 best_threshold 0.032597859 match_distance 5.656e-30 matched True
sample 2026082940 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.240e-29 matched True
sample 2026082941 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.529e-27 matched True
sample 2026082942 min_area 0.032598859 best_threshold 0.032597859 match_distance 8.882e-30 matched True
sample 2026082943 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.544e-29 matched True
sample 2026082944 min_area 0.032598859 best_threshold 0.032597859 match_distance 3.264e-30 matched True
sample 2026082945 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.051e-29 matched True
sample 2026082946 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.350e-29 matched True
sample 2026082947 min_area 0.032598859 best_threshold 0.032597859 match_distance 7.519e-29 matched True
sample 2026082948 min_area 0.032598859 best_threshold 0.032597859 match_distance 4.526e-29 matched True
sample 2026082949 min_area 0.032598859 best_threshold 0.032597859 match_distance 3.603e-30 matched True
sample 2026082950 min_area 0.032598859 best_threshold 0.032597859 match_distance 7.373e-30 matched True
sample 2026082951 min_area 0.032598859 best_threshold 0.032597859 match_distance 8.150e-30 matched True
sample 2026082952 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.033e-29 matched True
sample 2026082954 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.214e-30 matched True
sample 2026082955 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.969e-29 matched True
sample 2026082956 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.780e-28 matched True
sample 2026082957 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.133e-29 matched True
sample 2026082958 min_area 0.032598859 best_threshold 0.032597859 match_distance 3.950e-30 matched True
sample 2026082959 min_area 0.032598859 best_threshold 0.032597859 match_distance 9.104e-27 matched True
sample 2026082960 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.985e-29 matched True
sample 2026082961 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.112e-29 matched True
sample 2026082962 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.316e-29 matched True
sample 2026082963 min_area 0.032598859 best_threshold 0.032597859 match_distance 7.026e-30 matched True
sample 2026082964 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.516e-29 matched True
sample 2026082965 min_area 0.032598859 best_threshold 0.032597859 match_distance 4.012e-30 matched True
sample 2026082966 min_area 0.032598859 best_threshold 0.032597859 match_distance 5.837e-30 matched True
sample 2026082967 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.426e-29 matched True
sample 2026082968 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.386e-30 matched True
sample 2026082969 min_area 0.032598859 best_threshold 0.032597859 match_distance 7.064e-29 matched True
sample 2026082970 min_area 0.032598859 best_threshold 0.032597859 match_distance 6.418e-30 matched True
sample 2026082971 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.364e-29 matched True
sample 2026082972 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.756e-29 matched True
sample 2026082973 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.514e-29 matched True
sample 2026082974 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.256e-30 matched True
sample 2026082975 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.496e-29 matched True
sample 2026082976 min_area 0.032598859 best_threshold 0.032597859 match_distance 7.133e-31 matched True
sample 2026082977 min_area 0.032598859 best_threshold 0.032597859 match_distance 7.557e-30 matched True
sample 2026082978 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.655e-29 matched True
sample 2026082979 min_area 0.032598859 best_threshold 0.032597859 match_distance 4.659e-30 matched True
sample 2026082980 min_area 0.032598859 best_threshold 0.032597859 match_distance 6.562e-30 matched True
sample 2026082981 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.768e-29 matched True
sample 2026082982 min_area 0.032598859 best_threshold 0.032597859 match_distance 6.091e-30 matched True
sample 2026082983 min_area 0.032598859 best_threshold 0.032597859 match_distance 5.182e-30 matched True
sample 2026082984 min_area 0.032598859 best_threshold 0.032597859 match_distance 5.845e-30 matched True
sample 2026082985 min_area 0.032598859 best_threshold 0.032597859 match_distance 3.240e-29 matched True
sample 2026082986 min_area 0.032598859 best_threshold 0.032597859 match_distance 8.148e-28 matched True
sample 2026082987 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.241e-28 matched True
sample 2026082988 min_area 0.032598859 best_threshold 0.032597859 match_distance 8.745e-30 matched True
sample 2026082989 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.874e-30 matched True
sample 2026082990 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.303e-29 matched True
sample 2026082991 min_area 0.032598859 best_threshold 0.032597859 match_distance 9.677e-30 matched True
sample 2026082992 min_area 0.032598859 best_threshold 0.032597859 match_distance 5.240e-30 matched True
sample 2026082993 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.804e-29 matched True
sample 2026082994 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.018e-29 matched True
sample 2026082995 min_area 0.032598859 best_threshold 0.032597859 match_distance 7.721e-30 matched True
sample 2026082996 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.760e-29 matched True
sample 2026082997 min_area 0.032598859 best_threshold 0.032597859 match_distance 8.092e-30 matched True
sample 2026082998 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.650e-30 matched True
sample 2026082999 min_area 0.032598859 best_threshold 0.032597859 match_distance 7.667e-30 matched True
sample 2026083000 min_area 0.032598859 best_threshold 0.032597859 match_distance 3.625e-30 matched True
sample 2026083001 min_area 0.032598859 best_threshold 0.032597859 match_distance 5.554e-30 matched True
sample 2026083002 min_area 0.032598859 best_threshold 0.032597859 match_distance 4.804e-26 matched True
sample 2026083003 min_area 0.032598859 best_threshold 0.032597859 match_distance 4.604e-30 matched True
sample 2026083004 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.226e-29 matched True
sample 2026083005 min_area 0.032598859 best_threshold 0.032597859 match_distance 6.741e-30 matched True
sample 2026083006 min_area 0.032598859 best_threshold 0.032597859 match_distance 3.650e-30 matched True
sample 2026083007 min_area 0.032598859 best_threshold 0.032597859 match_distance 5.239e-30 matched True
sample 2026083008 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.051e-29 matched True
sample 2026083009 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.185e-29 matched True
sample 2026083010 min_area 0.032598859 best_threshold 0.032597859 match_distance 5.081e-30 matched True
sample 2026083011 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.681e-28 matched True
sample 2026083012 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.460e-29 matched True
sample 2026083013 min_area 0.032598859 best_threshold 0.032597859 match_distance 5.507e-30 matched True
sample 2026083014 min_area 0.032598859 best_threshold 0.032597859 match_distance 3.660e-30 matched True
sample 2026083015 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.994e-29 matched True
sample 2026083016 min_area 0.032598859 best_threshold 0.032597859 match_distance 7.499e-29 matched True
sample 2026083017 min_area 0.032598859 best_threshold 0.032597859 match_distance 3.911e-30 matched True
sample 2026083018 min_area 0.032598859 best_threshold 0.032597859 match_distance 9.715e-30 matched True
sample 2026083019 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.877e-29 matched True
sample 2026083020 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.450e-29 matched True
sample 2026083021 min_area 0.032598859 best_threshold 0.032597859 match_distance 3.873e-30 matched True
sample 2026083022 min_area 0.032598859 best_threshold 0.032597859 match_distance 5.607e-30 matched True
sample 2026083023 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.293e-29 matched True
sample 2026083024 min_area 0.032598859 best_threshold 0.032597859 match_distance 3.856e-27 matched True
sample 2026083025 min_area 0.032598859 best_threshold 0.032597859 match_distance 8.959e-30 matched True
sample 2026083026 min_area 0.032598859 best_threshold 0.032597859 match_distance 5.692e-30 matched True
sample 2026083027 min_area 0.032598859 best_threshold 0.032597859 match_distance 4.784e-30 matched True
sample 2026083028 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.056e-29 matched True
sample 2026083029 min_area 0.032598859 best_threshold 0.032597859 match_distance 3.075e-26 matched True
sample 2026083030 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.198e-29 matched True
sample 2026083031 min_area 0.032598859 best_threshold 0.032597859 match_distance 4.038e-30 matched True
sample 2026083032 min_area 0.032598859 best_threshold 0.032597859 match_distance 6.599e-30 matched True
sample 2026083033 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.895e-29 matched True
sample 2026083034 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.794e-30 matched True
sample 2026083035 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.677e-29 matched True
sample 2026083036 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.316e-27 matched True
sample 2026083037 min_area 0.032598859 best_threshold 0.032597859 match_distance 4.653e-30 matched True
sample 2026083038 min_area 0.032598859 best_threshold 0.032597859 match_distance 7.052e-29 matched True
sample 2026083039 min_area 0.032598859 best_threshold 0.032597859 match_distance 6.755e-30 matched True
sample 2026083040 min_area 0.032598859 best_threshold 0.032597859 match_distance 4.298e-30 matched True
sample 2026083041 min_area 0.032598859 best_threshold 0.032597859 match_distance 8.758e-30 matched True
sample 2026083042 min_area 0.032598859 best_threshold 0.032597859 match_distance 6.229e-30 matched True
sample 2026083043 min_area 0.032598859 best_threshold 0.032597859 match_distance 6.606e-30 matched True
sample 2026083044 min_area 0.032598859 best_threshold 0.032597859 match_distance 7.682e-30 matched True
sample 2026083045 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.135e-29 matched True
sample 2026083046 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.096e-29 matched True
sample 2026083047 min_area 0.032598859 best_threshold 0.032597859 match_distance 5.930e-30 matched True
sample 2026083048 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.937e-29 matched True
sample 2026083049 min_area 0.032598859 best_threshold 0.032597859 match_distance 6.560e-30 matched True
sample 2026083050 min_area 0.032598859 best_threshold 0.032597859 match_distance 5.435e-30 matched True
sample 2026083052 min_area 0.032598859 best_threshold 0.032597859 match_distance 8.331e-27 matched True
sample 2026083053 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.369e-29 matched True
sample 2026083054 min_area 0.032598859 best_threshold 0.032597859 match_distance 4.456e-28 matched True
sample 2026083055 min_area 0.032598859 best_threshold 0.032597859 match_distance 8.755e-30 matched True
sample 2026083056 min_area 0.032598859 best_threshold 0.032597859 match_distance 5.103e-30 matched True
sample 2026083057 min_area 0.032598859 best_threshold 0.032597859 match_distance 5.237e-30 matched True
sample 2026083058 min_area 0.032598859 best_threshold 0.032597859 match_distance 4.373e-30 matched True
sample 2026083059 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.235e-29 matched True
sample 2026083060 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.737e-29 matched True
sample 2026083061 min_area 0.032598859 best_threshold 0.032597859 match_distance 4.325e-30 matched True
sample 2026083062 min_area 0.032598859 best_threshold 0.032597859 match_distance 6.886e-30 matched True
sample 2026083063 min_area 0.032598859 best_threshold 0.032597859 match_distance 3.675e-30 matched True
sample 2026083064 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.809e-30 matched True
sample 2026083065 min_area 0.032598859 best_threshold 0.032597859 match_distance 6.585e-30 matched True
sample 2026083066 min_area 0.032598859 best_threshold 0.032597859 match_distance 3.430e-30 matched True
sample 2026083067 min_area 0.032598859 best_threshold 0.032597859 match_distance 8.676e-28 matched True
sample 2026083068 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.873e-30 matched True
sample 2026083069 min_area 0.032598859 best_threshold 0.032597859 match_distance 4.952e-28 matched True
sample 2026083070 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.547e-29 matched True
sample 2026083071 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.668e-29 matched True
sample 2026083072 min_area 0.032598859 best_threshold 0.032597859 match_distance 3.341e-29 matched True
sample 2026083073 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.028e-29 matched True
sample 2026083074 min_area 0.032598859 best_threshold 0.032597859 match_distance 6.723e-30 matched True
sample 2026083075 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.940e-28 matched True
sample 2026083076 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.782e-29 matched True
sample 2026083077 min_area 0.032598859 best_threshold 0.032597859 match_distance 7.504e-30 matched True
sample 2026083078 min_area 0.032598859 best_threshold 0.032597859 match_distance 4.639e-30 matched True
sample 2026083079 min_area 0.032598859 best_threshold 0.032597859 match_distance 4.278e-30 matched True
sample 2026083080 min_area 0.032598859 best_threshold 0.032597859 match_distance 5.518e-30 matched True
sample 2026083081 min_area 0.032598859 best_threshold 0.032597859 match_distance 9.051e-30 matched True
sample 2026083082 min_area 0.032598859 best_threshold 0.032597859 match_distance 4.418e-30 matched True
sample 2026083083 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.580e-30 matched True
sample 2026083084 min_area 0.032598859 best_threshold 0.032597859 match_distance 7.922e-30 matched True
sample 2026083085 min_area 0.032598859 best_threshold 0.032597859 match_distance 3.510e-30 matched True
sample 2026083086 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.305e-29 matched True
sample 2026083087 min_area 0.032598859 best_threshold 0.032597859 match_distance 8.364e-30 matched True
sample 2026083088 min_area 0.032598859 best_threshold 0.032597859 match_distance 8.068e-30 matched True
sample 2026083089 min_area 0.032598859 best_threshold 0.032597859 match_distance 7.001e-30 matched True
sample 2026083090 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.989e-30 matched True
sample 2026083091 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.774e-28 matched True
sample 2026083092 min_area 0.032598859 best_threshold 0.032597859 match_distance 5.693e-29 matched True
sample 2026083093 min_area 0.032598859 best_threshold 0.032597859 match_distance 3.186e-30 matched True
sample 2026083094 min_area 0.032598859 best_threshold 0.032597859 match_distance 5.917e-30 matched True
sample 2026083095 min_area 0.032598859 best_threshold 0.032597859 match_distance 3.377e-30 matched True
sample 2026083096 min_area 0.032598859 best_threshold 0.032597859 match_distance 4.924e-29 matched True
sample 2026083097 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.604e-27 matched True
sample 2026083098 min_area 0.032598859 best_threshold 0.032597859 match_distance 7.463e-30 matched True
sample 2026083099 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.291e-29 matched True
sample 2026083100 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.303e-29 matched True
threshold 0.032498859 kept 393 of 400
  matched_to_incumbent_orbit 393
  match_distance_min_median_max 7.133e-31 8.242e-30 1.060e-24
  delta 0.001 matched_samples_covering_all_20_active 393
  delta 0.001 core 0 covered_by 393 of 393
  delta 0.001 core 1 covered_by 393 of 393
  delta 0.001 core 2 covered_by 393 of 393
  delta 0.001 unmatched_samples 0 distinct_hypergraphs 0
  delta 0.0001 matched_samples_covering_all_20_active 393
  delta 0.0001 core 0 covered_by 393 of 393
  delta 0.0001 core 1 covered_by 393 of 393
  delta 0.0001 core 2 covered_by 393 of 393
  delta 0.0001 unmatched_samples 0 distinct_hypergraphs 0
threshold 0.032588859 kept 393 of 400
  matched_to_incumbent_orbit 393
  match_distance_min_median_max 7.133e-31 8.242e-30 1.060e-24
  delta 0.001 matched_samples_covering_all_20_active 393
  delta 0.001 core 0 covered_by 393 of 393
  delta 0.001 core 1 covered_by 393 of 393
  delta 0.001 core 2 covered_by 393 of 393
  delta 0.001 unmatched_samples 0 distinct_hypergraphs 0
  delta 0.0001 matched_samples_covering_all_20_active 393
  delta 0.0001 core 0 covered_by 393 of 393
  delta 0.0001 core 1 covered_by 393 of 393
  delta 0.0001 core 2 covered_by 393 of 393
  delta 0.0001 unmatched_samples 0 distinct_hypergraphs 0
threshold 0.032597859 kept 393 of 400
  matched_to_incumbent_orbit 393
  match_distance_min_median_max 7.133e-31 8.242e-30 1.060e-24
  delta 0.001 matched_samples_covering_all_20_active 393
  delta 0.001 core 0 covered_by 393 of 393
  delta 0.001 core 1 covered_by 393 of 393
  delta 0.001 core 2 covered_by 393 of 393
  delta 0.001 unmatched_samples 0 distinct_hypergraphs 0
  delta 0.0001 matched_samples_covering_all_20_active 393
  delta 0.0001 core 0 covered_by 393 of 393
  delta 0.0001 core 1 covered_by 393 of 393
  delta 0.0001 core 2 covered_by 393 of 393
  delta 0.0001 unmatched_samples 0 distinct_hypergraphs 0
status DESCRIPTIVE: sampling evidence only; rigidity verdicts come from the exact Part A scan
```

### (d) perturbed sigma = 0.05, seed_base = 2026083101

```text
python3 rigidity_sampling.py --seed-mode perturbed --sigma 0.05 --trials 400 --seed-base 2026083101 --cores "0,1,2,3,4,5,6,7,8,9,10,11,12,14,16,18,19;0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17;0,1,2,3,4,5,6,7,8,9,10,11,12,13,15,16,18,19"
```

- Exit code: 0
- Elapsed: 11 seconds
- Kept-fraction summary: 87/400 at every threshold (313 trials landed below [erratum 2026-08-20, panel finding: original said "above"; the filter drops trials below the window] the near-record window and were dropped); all 87 kept samples matched to the incumbent orbit; no matched=False samples; all three cores covered by 87 of 87 samples at every (threshold, delta).

Complete stdout (verbatim from `$HOME/heilbronn_logs/step_d_sigma_0.05.log`):

```text
DESCRIPTIVE-ONLY: float statistics; no exactness claims; no candidate records
incumbent_float 0.0325988586918197
thresholds (0.0324988586918197, 0.0325888586918197, 0.0325978586918197)
seed_mode perturbed sigma 0.05
CAVEAT: perturbed mode samples the basin reachable from the incumbent's
CAVEAT: neighborhood; it is not independent global optimization
trials 400 popsize 16 maxiter 600
sample 2026083101 min_area 0.032598859 best_threshold 0.032597859 match_distance 6.194e-30 matched True
sample 2026083103 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.831e-29 matched True
sample 2026083104 min_area 0.032598859 best_threshold 0.032597859 match_distance 6.070e-30 matched True
sample 2026083109 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.008e-28 matched True
sample 2026083110 min_area 0.032598859 best_threshold 0.032597859 match_distance 9.676e-30 matched True
sample 2026083113 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.013e-30 matched True
sample 2026083123 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.030e-29 matched True
sample 2026083127 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.198e-29 matched True
sample 2026083128 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.873e-29 matched True
sample 2026083134 min_area 0.032598859 best_threshold 0.032597859 match_distance 4.223e-27 matched True
sample 2026083136 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.237e-29 matched True
sample 2026083140 min_area 0.032598859 best_threshold 0.032597859 match_distance 6.452e-30 matched True
sample 2026083143 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.053e-28 matched True
sample 2026083157 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.245e-29 matched True
sample 2026083159 min_area 0.032598859 best_threshold 0.032597859 match_distance 4.567e-28 matched True
sample 2026083160 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.001e-29 matched True
sample 2026083162 min_area 0.032598859 best_threshold 0.032597859 match_distance 4.881e-29 matched True
sample 2026083166 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.443e-30 matched True
sample 2026083175 min_area 0.032598859 best_threshold 0.032597859 match_distance 8.302e-30 matched True
sample 2026083184 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.947e-29 matched True
sample 2026083198 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.075e-29 matched True
sample 2026083200 min_area 0.032598859 best_threshold 0.032597859 match_distance 6.078e-30 matched True
sample 2026083206 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.627e-29 matched True
sample 2026083212 min_area 0.032598859 best_threshold 0.032597859 match_distance 5.708e-30 matched True
sample 2026083213 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.114e-29 matched True
sample 2026083217 min_area 0.032598859 best_threshold 0.032597859 match_distance 5.513e-30 matched True
sample 2026083220 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.023e-29 matched True
sample 2026083229 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.011e-30 matched True
sample 2026083234 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.490e-29 matched True
sample 2026083235 min_area 0.032598859 best_threshold 0.032597859 match_distance 8.701e-29 matched True
sample 2026083237 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.144e-29 matched True
sample 2026083249 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.167e-29 matched True
sample 2026083251 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.987e-26 matched True
sample 2026083254 min_area 0.032598859 best_threshold 0.032597859 match_distance 7.697e-30 matched True
sample 2026083261 min_area 0.032598859 best_threshold 0.032597859 match_distance 4.532e-29 matched True
sample 2026083267 min_area 0.032598859 best_threshold 0.032597859 match_distance 4.395e-30 matched True
sample 2026083270 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.067e-29 matched True
sample 2026083272 min_area 0.032598859 best_threshold 0.032597859 match_distance 5.777e-27 matched True
sample 2026083278 min_area 0.032598859 best_threshold 0.032597859 match_distance 3.395e-30 matched True
sample 2026083281 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.045e-29 matched True
sample 2026083282 min_area 0.032598859 best_threshold 0.032597859 match_distance 5.399e-30 matched True
sample 2026083284 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.448e-29 matched True
sample 2026083294 min_area 0.032598859 best_threshold 0.032597859 match_distance 3.054e-30 matched True
sample 2026083314 min_area 0.032598859 best_threshold 0.032597859 match_distance 5.058e-30 matched True
sample 2026083320 min_area 0.032598859 best_threshold 0.032597859 match_distance 7.289e-30 matched True
sample 2026083322 min_area 0.032598859 best_threshold 0.032597859 match_distance 4.835e-29 matched True
sample 2026083324 min_area 0.032598859 best_threshold 0.032597859 match_distance 8.545e-29 matched True
sample 2026083336 min_area 0.032598859 best_threshold 0.032597859 match_distance 9.423e-30 matched True
sample 2026083340 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.659e-29 matched True
sample 2026083341 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.000e-29 matched True
sample 2026083342 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.728e-29 matched True
sample 2026083367 min_area 0.032598859 best_threshold 0.032597859 match_distance 3.404e-30 matched True
sample 2026083371 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.791e-29 matched True
sample 2026083374 min_area 0.032598859 best_threshold 0.032597859 match_distance 8.123e-30 matched True
sample 2026083384 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.631e-29 matched True
sample 2026083386 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.473e-29 matched True
sample 2026083391 min_area 0.032598859 best_threshold 0.032597859 match_distance 3.807e-26 matched True
sample 2026083399 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.815e-29 matched True
sample 2026083401 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.552e-29 matched True
sample 2026083404 min_area 0.032598859 best_threshold 0.032597859 match_distance 5.404e-29 matched True
sample 2026083407 min_area 0.032598859 best_threshold 0.032597859 match_distance 3.136e-29 matched True
sample 2026083408 min_area 0.032598859 best_threshold 0.032597859 match_distance 8.970e-30 matched True
sample 2026083412 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.052e-29 matched True
sample 2026083414 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.434e-30 matched True
sample 2026083416 min_area 0.032598859 best_threshold 0.032597859 match_distance 3.717e-29 matched True
sample 2026083419 min_area 0.032598859 best_threshold 0.032597859 match_distance 6.349e-30 matched True
sample 2026083421 min_area 0.032598859 best_threshold 0.032597859 match_distance 4.433e-27 matched True
sample 2026083422 min_area 0.032598859 best_threshold 0.032597859 match_distance 6.776e-30 matched True
sample 2026083424 min_area 0.032598859 best_threshold 0.032597859 match_distance 9.748e-30 matched True
sample 2026083427 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.470e-29 matched True
sample 2026083432 min_area 0.032598859 best_threshold 0.032597859 match_distance 5.367e-30 matched True
sample 2026083436 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.868e-30 matched True
sample 2026083438 min_area 0.032598859 best_threshold 0.032597859 match_distance 3.482e-28 matched True
sample 2026083441 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.128e-29 matched True
sample 2026083446 min_area 0.032598859 best_threshold 0.032597859 match_distance 6.394e-27 matched True
sample 2026083460 min_area 0.032598859 best_threshold 0.032597859 match_distance 3.789e-30 matched True
sample 2026083467 min_area 0.032598859 best_threshold 0.032597859 match_distance 3.315e-30 matched True
sample 2026083468 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.835e-29 matched True
sample 2026083470 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.842e-29 matched True
sample 2026083471 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.818e-29 matched True
sample 2026083474 min_area 0.032598859 best_threshold 0.032597859 match_distance 9.296e-30 matched True
sample 2026083476 min_area 0.032598859 best_threshold 0.032597859 match_distance 3.692e-26 matched True
sample 2026083477 min_area 0.032598859 best_threshold 0.032597859 match_distance 5.977e-26 matched True
sample 2026083479 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.161e-29 matched True
sample 2026083486 min_area 0.032598859 best_threshold 0.032597859 match_distance 1.198e-29 matched True
sample 2026083488 min_area 0.032598859 best_threshold 0.032597859 match_distance 3.445e-26 matched True
sample 2026083497 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.669e-29 matched True
threshold 0.032498859 kept 87 of 400
  matched_to_incumbent_orbit 87
  match_distance_min_median_max 1.434e-30 1.448e-29 5.977e-26
  delta 0.001 matched_samples_covering_all_20_active 87
  delta 0.001 core 0 covered_by 87 of 87
  delta 0.001 core 1 covered_by 87 of 87
  delta 0.001 core 2 covered_by 87 of 87
  delta 0.001 unmatched_samples 0 distinct_hypergraphs 0
  delta 0.0001 matched_samples_covering_all_20_active 87
  delta 0.0001 core 0 covered_by 87 of 87
  delta 0.0001 core 1 covered_by 87 of 87
  delta 0.0001 core 2 covered_by 87 of 87
  delta 0.0001 unmatched_samples 0 distinct_hypergraphs 0
threshold 0.032588859 kept 87 of 400
  matched_to_incumbent_orbit 87
  match_distance_min_median_max 1.434e-30 1.448e-29 5.977e-26
  delta 0.001 matched_samples_covering_all_20_active 87
  delta 0.001 core 0 covered_by 87 of 87
  delta 0.001 core 1 covered_by 87 of 87
  delta 0.001 core 2 covered_by 87 of 87
  delta 0.001 unmatched_samples 0 distinct_hypergraphs 0
  delta 0.0001 matched_samples_covering_all_20_active 87
  delta 0.0001 core 0 covered_by 87 of 87
  delta 0.0001 core 1 covered_by 87 of 87
  delta 0.0001 core 2 covered_by 87 of 87
  delta 0.0001 unmatched_samples 0 distinct_hypergraphs 0
threshold 0.032597859 kept 87 of 400
  matched_to_incumbent_orbit 87
  match_distance_min_median_max 1.434e-30 1.448e-29 5.977e-26
  delta 0.001 matched_samples_covering_all_20_active 87
  delta 0.001 core 0 covered_by 87 of 87
  delta 0.001 core 1 covered_by 87 of 87
  delta 0.001 core 2 covered_by 87 of 87
  delta 0.001 unmatched_samples 0 distinct_hypergraphs 0
  delta 0.0001 matched_samples_covering_all_20_active 87
  delta 0.0001 core 0 covered_by 87 of 87
  delta 0.0001 core 1 covered_by 87 of 87
  delta 0.0001 core 2 covered_by 87 of 87
  delta 0.0001 unmatched_samples 0 distinct_hypergraphs 0
status DESCRIPTIVE: sampling evidence only; rigidity verdicts come from the exact Part A scan
```

### (e) perturbed sigma = 0.1, seed_base = 2026083501

```text
python3 rigidity_sampling.py --seed-mode perturbed --sigma 0.1 --trials 400 --seed-base 2026083501 --cores "0,1,2,3,4,5,6,7,8,9,10,11,12,14,16,18,19;0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17;0,1,2,3,4,5,6,7,8,9,10,11,12,13,15,16,18,19"
```

- Exit code: 0
- Elapsed: 16 seconds
- Kept-fraction summary: 2/400 at every threshold (398 trials landed below [erratum 2026-08-20, panel finding: original said "above"; the filter drops trials below the window] the near-record window and were dropped); both kept samples matched to the incumbent orbit; no matched=False samples; all three cores covered by 2 of 2 samples at every (threshold, delta).

Complete stdout (verbatim from `$HOME/heilbronn_logs/step_e_sigma_0.1.log`):

```text
DESCRIPTIVE-ONLY: float statistics; no exactness claims; no candidate records
incumbent_float 0.0325988586918197
thresholds (0.0324988586918197, 0.0325888586918197, 0.0325978586918197)
seed_mode perturbed sigma 0.1
CAVEAT: perturbed mode samples the basin reachable from the incumbent's
CAVEAT: neighborhood; it is not independent global optimization
trials 400 popsize 16 maxiter 600
sample 2026083764 min_area 0.032598859 best_threshold 0.032597859 match_distance 2.572e-29 matched True
sample 2026083775 min_area 0.032598859 best_threshold 0.032597859 match_distance 3.086e-30 matched True
threshold 0.032498859 kept 2 of 400
  matched_to_incumbent_orbit 2
  match_distance_min_median_max 3.086e-30 2.572e-29 2.572e-29
  delta 0.001 matched_samples_covering_all_20_active 2
  delta 0.001 core 0 covered_by 2 of 2
  delta 0.001 core 1 covered_by 2 of 2
  delta 0.001 core 2 covered_by 2 of 2
  delta 0.001 unmatched_samples 0 distinct_hypergraphs 0
  delta 0.0001 matched_samples_covering_all_20_active 2
  delta 0.0001 core 0 covered_by 2 of 2
  delta 0.0001 core 1 covered_by 2 of 2
  delta 0.0001 core 2 covered_by 2 of 2
  delta 0.0001 unmatched_samples 0 distinct_hypergraphs 0
threshold 0.032588859 kept 2 of 400
  matched_to_incumbent_orbit 2
  match_distance_min_median_max 3.086e-30 2.572e-29 2.572e-29
  delta 0.001 matched_samples_covering_all_20_active 2
  delta 0.001 core 0 covered_by 2 of 2
  delta 0.001 core 1 covered_by 2 of 2
  delta 0.001 core 2 covered_by 2 of 2
  delta 0.001 unmatched_samples 0 distinct_hypergraphs 0
  delta 0.0001 matched_samples_covering_all_20_active 2
  delta 0.0001 core 0 covered_by 2 of 2
  delta 0.0001 core 1 covered_by 2 of 2
  delta 0.0001 core 2 covered_by 2 of 2
  delta 0.0001 unmatched_samples 0 distinct_hypergraphs 0
threshold 0.032597859 kept 2 of 400
  matched_to_incumbent_orbit 2
  match_distance_min_median_max 3.086e-30 2.572e-29 2.572e-29
  delta 0.001 matched_samples_covering_all_20_active 2
  delta 0.001 core 0 covered_by 2 of 2
  delta 0.001 core 1 covered_by 2 of 2
  delta 0.001 core 2 covered_by 2 of 2
  delta 0.001 unmatched_samples 0 distinct_hypergraphs 0
  delta 0.0001 matched_samples_covering_all_20_active 2
  delta 0.0001 core 0 covered_by 2 of 2
  delta 0.0001 core 1 covered_by 2 of 2
  delta 0.0001 core 2 covered_by 2 of 2
  delta 0.0001 unmatched_samples 0 distinct_hypergraphs 0
status DESCRIPTIVE: sampling evidence only; rigidity verdicts come from the exact Part A scan
```

## Totals table (per sigma)

Threshold labels: `T1 = z0 - 1e-4 = 0.032498859`, `T2 = z0 - 1e-5 = 0.032588859`,
`T3 = z0 - 1e-6 = 0.032597859` (`z0 = incumbent_float 0.0325988586918197`).
Cores from the Part A scan: `core 0 = {0..12,14,16,18,19}` (17 tri),
`core 1 = {0..17}` (18 tri), `core 2 = {0..13,15,16,18,19}` (18 tri). Deltas
`d1 = 1e-3`, `d2 = 1e-4`. All numbers descriptive floats, per the tool's
DESCRIPTIVE-ONLY banner.

| sigma | trials | elapsed s | kept T1 | kept T2 | kept T3 | matched T1 | matched T2 | matched T3 | core 0 @ (T*,d1)/(T*,d2) | core 1 @ (T*,d1)/(T*,d2) | core 2 @ (T*,d1)/(T*,d2) | unmatched kept samples | distinct unmatched hypergraphs |
|------:|-------:|----------:|--------:|--------:|--------:|-----------:|-----------:|-----------:|-------------------------:|-------------------------:|-------------------------:|:----------------------:|:------------------------------:|
| 0.005 | 400 | 4  | 400/400 | 400/400 | 400/400 | 400/400 | 400/400 | 400/400 | 400/400 (all) | 400/400 (all) | 400/400 (all) | none | 0 |
| 0.02  | 400 | 6  | 393/400 | 393/400 | 393/400 | 393/393 | 393/393 | 393/393 | 393/393 (all) | 393/393 (all) | 393/393 (all) | none | 0 |
| 0.05  | 400 | 11 |  87/400 |  87/400 |  87/400 |  87/87  |  87/87  |  87/87  |  87/87 (all)  |  87/87 (all)  |  87/87 (all)  | none | 0 |
| 0.1   | 400 | 16 |   2/400 |   2/400 |   2/400 |   2/2   |   2/2   |   2/2   |   2/2 (all)   |   2/2 (all)   |   2/2 (all)   | none | 0 |

- "kept T*" is the tool's own `threshold ... kept X of 400` line; identical
  across T1/T2/T3 in every campaign because the tool re-uses the same
  kept-set for the three thresholds (its `best_threshold` per sample
  reaches T3 = z0 - 1e-6 in every kept row, so all three thresholds keep
  the same X samples).
- "core c @ (T*,dj)" is the tool's `delta dj core c covered_by N of K`
  entry, again identical across T1/T2/T3 and across d1/d2 in every
  campaign; "N of K" is (matched-samples covering core c) / (matched
  samples). "all" means every matched sample covers that core.
- **Unmatched-kept scan:** across all four campaigns, no kept sample had
  `matched False`; the count of distinct near-active hypergraphs outside
  the incumbent orbit is 0.
- **Kept-fraction trend across sigma:** 400/400 -> 393/400 -> 87/400 ->
  2/400 as sigma grows through 0.005, 0.02, 0.05, 0.1. Local polishing
  from the incumbent frame stays inside the incumbent's basin for small
  perturbations; the fraction of trials that fail to reach the near-record
  window rises quickly past sigma ~ 0.05, and by sigma = 0.1 the basin is
  reached only twice out of 400 starts. Every kept sample from every
  campaign lands inside the incumbent D4 orbit (match_distance <= 1.060e-24)
  and every matched sample covers all three Part A cores at both deltas.

## Interpretation (descriptive)

Run 6 (blind random-start generator) had already established that
independent global optimization does not reach the near-record thresholds
inside the trial budget. Run 7's perturbed generator reverses the polarity
of the experiment: it warm-starts from the incumbent and asks whether
polishing ever escapes the incumbent basin into a distinct near-active
hypergraph. Across the four sigma settings and 1600 total trials, no kept
sample landed outside the incumbent D4 orbit and every matched sample
covered each of the three Part A cores under both delta values. This is
consistent with the teeth-test's positive-recurrence expectation, but the
scope guard applies: these are descriptive floating-point statistics about
independently optimized numerical samples; nothing here is exact, no
sample is a candidate record, and the rigidity verdicts come from the
exact Part A scan, as the tool's own `status DESCRIPTIVE:` line
re-iterates for every campaign.

