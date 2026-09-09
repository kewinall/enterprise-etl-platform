.PHONY: validate test compose-check security-check hop-smoke

validate:
	python scripts/validate_repository.py

test:
	python -m unittest discover -s tests -v

compose-check:
	docker compose config --quiet

security-check:
	python scripts/secret_scan.py

hop-smoke:
	bash scripts/hop_api_smoke.sh
