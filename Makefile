.PHONY: validate test compose-check security-check hop-smoke lifecycle-smoke supply-chain-smoke observability-smoke etl-intelligence-smoke vulnerability-smoke gitlab-verify p1-integration-smoke p2-evaluation p0-check p1-check p2-check

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

p1-integration-smoke:
	bash scripts/p1_integration_smoke.sh

p0-check: validate test etl-intelligence-smoke vulnerability-smoke gitlab-verify


p1-check: validate test etl-intelligence-smoke p1-integration-smoke vulnerability-smoke gitlab-verify

p2-evaluation:
	python scripts/evaluate_etl_ai.py --output-dir reports/generated

p2-check: validate test etl-intelligence-smoke p1-integration-smoke p2-evaluation vulnerability-smoke gitlab-verify
