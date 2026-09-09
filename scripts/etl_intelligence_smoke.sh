#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

python "$ROOT/scripts/etl_intelligence.py" parse   "$ROOT/samples/etl_intelligence/generic_order_enrichment.json"   --output "$TMP_DIR/metadata.json"

python "$ROOT/scripts/etl_intelligence.py" analyze   "$TMP_DIR/metadata.json"   --output "$TMP_DIR/analysis.json"

python - "$TMP_DIR/metadata.json" "$TMP_DIR/analysis.json" <<'PY'
import json
import sys

metadata = json.load(open(sys.argv[1], encoding="utf-8"))
analysis = json.load(open(sys.argv[2], encoding="utf-8"))

assert metadata["pipeline"]["name"] == "generic_order_enrichment"
assert len(metadata["steps"]) == 3
assert metadata["sources"][0]["name"] == "staging.orders"
assert metadata["targets"][0]["name"] == "analytics.orders"
assert analysis["analysis_mode"] == "fallback"
assert analysis["provenance"]["parser_truth_preserved"] is True
print("ETL intelligence smoke passed.")
PY
