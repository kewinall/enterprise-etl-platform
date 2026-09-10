#!/usr/bin/env python3
"""Generate repeatable ETL AI evaluation evidence."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) in sys.path:
    sys.path.remove(str(ROOT))
sys.path.insert(0, str(ROOT))

from etl_intelligence.evaluation import run_evaluation, write_report
from etl_intelligence.gateway import OpenAICompatibleGatewayClient


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, default=ROOT / "evaluation/dataset.json")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "reports/generated")
    parser.add_argument("--stable", action="store_true")
    parser.add_argument("--live-gateway", action="store_true")
    args = parser.parse_args()
    client = OpenAICompatibleGatewayClient() if args.live_gateway else None
    report = run_evaluation(
        args.dataset,
        ai_client=client,
        provider_name="multi-llm-ai-gateway" if args.live_gateway else "synthetic-evidence-contract",
        stable=args.stable,
    )
    paths = write_report(report, args.output_dir)
    print(json.dumps({
        "dataset_cases": report["dataset"]["case_count"],
        "parser_exact_match": report["parser"]["structural_case_exact_match_rate"],
        "unexpected_parse_failure_rate": report["parser"]["unexpected_parsing_failure_rate"],
        "semantic_structured_validity": report["semantic"]["structured_output_validity"],
        "unsupported_claim_count": report["semantic"]["unsupported_claim_count"],
        "input_tokens": report["usage"]["batch"]["input_tokens"],
        "output_tokens": report["usage"]["batch"]["output_tokens"],
        "estimated_cost_usd": report["usage"]["batch"]["estimated_cost_usd"],
        "outputs": paths,
    }, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
