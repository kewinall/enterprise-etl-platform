#!/usr/bin/env python3
"""CLI for deterministic ETL parsing and evidence-bound semantic analysis."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from etl_intelligence import DeterministicETLParser, SemanticAnalyzer


def write_json(payload: dict, destination: str | None) -> None:
    text = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if destination:
        Path(destination).write_text(text, encoding="utf-8")
    else:
        print(text, end="")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    parse_cmd = sub.add_parser("parse")
    parse_cmd.add_argument("source")
    parse_cmd.add_argument("--output")

    analyze_cmd = sub.add_parser("analyze")
    analyze_cmd.add_argument("metadata")
    analyze_cmd.add_argument("--output")
    analyze_cmd.add_argument("--validate-ai-response")

    args = parser.parse_args()
    if args.command == "parse":
        write_json(DeterministicETLParser().parse(args.source), args.output)
        return 0

    metadata = json.loads(Path(args.metadata).read_text(encoding="utf-8"))
    if args.validate_ai_response:
        captured = Path(args.validate_ai_response).read_text(encoding="utf-8")

        def static_client(_system_prompt: str, _context: str) -> str:
            return captured

        analyzer = SemanticAnalyzer(static_client, provider_name="captured-response")
    else:
        analyzer = SemanticAnalyzer()

    write_json(analyzer.analyze(metadata), args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
