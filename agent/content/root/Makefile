.PHONY: install test dry-run validate

install:
	python -m pip install -r requirements.txt

test:
	python -m pytest -q

dry-run:
	python scripts/run_daily_maintenance.py --dry-run

validate:
	python scripts/validate_repository.py
