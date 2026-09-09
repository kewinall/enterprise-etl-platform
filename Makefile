.PHONY: validate test compose-check security-check hop-smoke lifecycle-smoke supply-chain-smoke observability-smoke etl-intelligence-smoke vulnerability-smoke gitlab-verify p0-check

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

lifecycle-smoke:
	bash scripts/etl_lifecycle_smoke.sh

supply-chain-smoke:
	bash scripts/supply_chain_smoke.sh

observability-smoke:
	bash scripts/observability_smoke.sh

etl-intelligence-smoke:
	bash scripts/etl_intelligence_smoke.sh

vulnerability-smoke:
	bash scripts/vulnerability_lifecycle_smoke.sh

gitlab-verify:
	python ci/gitlab/verify_reference.py

p0-check: validate test etl-intelligence-smoke vulnerability-smoke gitlab-verify
