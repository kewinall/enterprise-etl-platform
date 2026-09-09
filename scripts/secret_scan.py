#!/usr/bin/env python3
"""Lightweight repository secret policy scan."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATTERNS = {
    "private_key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "aws_access_key": re.compile(r"AKIA[0-9A-Z]{16}"),
    "github_pat": re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),
    "generic_bearer": re.compile(r"Bearer\s+[A-Za-z0-9._~+/=-]{24,}"),
}


def main() -> int:
    findings: list[str] = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for name, pattern in PATTERNS.items():
            if pattern.search(text):
                findings.append(f"{name}: {path.relative_to(ROOT)}")

    if findings:
        print("Potential secrets detected:")
        for finding in findings:
            print(f" - {finding}")
        return 1

    print("No prohibited secret pattern detected.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
