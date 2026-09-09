#!/usr/bin/env python3
"""Compare CycloneDX component versions before and after remediation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def components(path: Path) -> dict[str, str]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    result: dict[str, str] = {}
    for component in payload.get("components", []):
        name = str(component.get("name") or "")
        version = str(component.get("version") or "")
        if name:
            result[name] = version
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("before")
    parser.add_argument("after")
    args = parser.parse_args()

    before = components(Path(args.before))
    after = components(Path(args.after))
    names = sorted(set(before) | set(after))

    changes = []
    for name in names:
        old = before.get(name)
        new = after.get(name)
        if old != new:
            changes.append({"component": name, "before": old, "after": new})

    print(json.dumps({"changes": changes}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
