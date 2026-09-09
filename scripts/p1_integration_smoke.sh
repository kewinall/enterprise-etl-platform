#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

cd "$ROOT"

python "$ROOT/scripts/migration_case.py"   "$ROOT/samples/pentaho_to_hop/legacy_order_enrichment.ktr"   --target "$ROOT/samples/pentaho_to_hop/hop_order_enrichment.hpl"   --output "$TMP/migration-report.json"

python - "$TMP/migration-report.json" "$ROOT/samples/pentaho_to_hop/legacy_daily_orders.kjb" <<'PY'
import json
import sys
from pathlib import Path

from etl_intelligence import DeterministicETLParser

report = json.loads(Path(sys.argv[1]).read_text())
assert report["validation"]["status"] == "PASS"
assert report["validation"]["ai_used"] is False
assert any(
    item["disposition"] == "manual-review"
    for item in report["plan"]["component_mapping"]
)

job = DeterministicETLParser().parse(sys.argv[2])
pipeline_deps = [item for item in job["dependencies"] if item.get("kind") == "pipeline"]
assert pipeline_deps[0]["to"] == "legacy_order_enrichment.ktr"
assert pipeline_deps[0]["classification"] == "structural"
assert job["lineage"]["ai_interpretation"] == []

print("P1 modernization integration smoke passed.")
PY
