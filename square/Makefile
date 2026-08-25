PYTHON ?= python3

.PHONY: check calibration d4-certificate frozen-boundary tangent-certificate size5-search size5-interval-smoke c4-search c4-interval-coarse-certificate c4-interval-smoke c2-boundary-search global-highs-smoke global-interval-smoke global-normal-search rigidity-core rigidity-core-smoke rigidity-sampling-smoke

check:
	$(PYTHON) -m unittest -v

rigidity-core:
	$(PYTHON) rigidity_core.py

rigidity-core-smoke:
	$(PYTHON) rigidity_core.py --max-subsets 3

rigidity-sampling-smoke:
	$(PYTHON) rigidity_sampling.py --trials 1 --popsize 4 --maxiter 20

calibration:
	$(PYTHON) calibration.py

d4-certificate:
	$(PYTHON) d4_interval_certificate.py

frozen-boundary:
	$(PYTHON) frozen_boundary_search.py

tangent-certificate:
	$(PYTHON) tangent_certificate.py

size5-search:
	$(PYTHON) transversal_search.py --seed-limit 1

size5-interval-smoke:
	$(PYTHON) transversal_interval.py --max-boxes 100

c4-search:
	$(PYTHON) c4_symmetry_search.py --seed-limit 1 --popsize 16 --maxiter 1200

c4-interval-coarse-certificate:
	$(PYTHON) c4_interval_certificate.py --max-boxes 0 --slack-bits 4 --root-bisections 96

c4-interval-smoke:
	$(PYTHON) c4_interval_certificate.py --max-boxes 100 --slack-bits 12 --root-bisections 64

c2-boundary-search:
	$(PYTHON) c2_boundary_search.py --seed-limit 1 --popsize 16 --maxiter 1200 --snap-bits 30

global-highs-smoke:
	$(PYTHON) highs_milp.py --n 6 --time-limit 15

global-interval-smoke:
	$(PYTHON) global_interval_branch.py --max-boxes 100

global-normal-search:
	$(PYTHON) global_normal_form_search.py --seed-limit 1 --popsize 16 --maxiter 1200 --snap-bits 30
