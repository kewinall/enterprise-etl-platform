#!/usr/bin/env python3
"""Run the public Pentaho-to-Hop migration case."""

from __future__ import annotations

import argparse
from pathlib import Path

from etl_intelligence import DeterministicETLParser
from etl_intelligence.migration import dumps_report, migration_report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("legacy", type=Path)
    parser.add_argument("--target", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    etl_parser = DeterministicETLParser()
    legacy = etl_parser.parse(args.legacy)
    target = etl_parser.parse(args.target) if args.target else None
    rendered = dumps_report(migration_report(legacy, target))
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
