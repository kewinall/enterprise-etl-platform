#!/usr/bin/env python3
"""Repository policy checks for the v0.1 portfolio baseline."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_DOCS = [
    "README.md",
    "docs/ARCHITECTURE.md",
    "docs/INSTALLATION.md",
    "docs/SECURITY.md",
    "docs/TROUBLESHOOTING.md",
    "docs/ROADMAP.md",
    "docs/CHANGELOG.md",
    "docs/GOVERNANCE.md",
    "docs/OBSERVABILITY.md",
]
FORBIDDEN_TOKENS = [
    "10." + "0.0.",
    "192." + "168.",
    "corp" + "." + "local",
    "production-" + "password",
    "real-" + "customer",
]


def main() -> int:
    errors: list[str] = []

    for rel in REQUIRED_DOCS:
        path = ROOT / rel
        if not path.exists():
            errors.append(f"missing required document: {rel}")
            continue
        text = path.read_text(encoding="utf-8")
        if "繁體中文" not in text or "English" not in text:
            errors.append(f"document must be bilingual: {rel}")

    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue

        for token in FORBIDDEN_TOKENS:
            if token in text:
                errors.append(
                    f"forbidden non-generic token '{token}' in {path.relative_to(ROOT)}"
                )

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print("Repository policy validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
