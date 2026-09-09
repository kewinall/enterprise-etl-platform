.PHONY: validate test compose-check security-check

validate:
	python scripts/validate_repository.py

test:
	python -m unittest discover -s tests -v

compose-check:
	docker compose config --quiet

security-check:
	python scripts/secret_scan.py
