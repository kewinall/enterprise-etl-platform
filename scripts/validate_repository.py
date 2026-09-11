#!/usr/bin/env python3
"""Repository policy checks for the portfolio baseline."""

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
    "docs/ORCHESTRATION.md",
    "docs/AUDIT_LIFECYCLE.md",
    "docs/SUPPLY_CHAIN.md",
    "docs/SLO_ALERTING.md",
    "docs/ETL_INTELLIGENCE.md",
    "docs/GITLAB_CICD.md",
    "docs/ENVIRONMENT_PROMOTION.md",
    "docs/VULNERABILITY_MANAGEMENT.md",
    "docs/PENTAHO_TO_HOP_MIGRATION.md",
    "docs/METADATA_LINEAGE.md",
    "docs/PORTFOLIO_INTEGRATION.md",
    "docs/ETL_AI_EVALUATION.md",
    "reports/README.md",
]

# Public README files are intentionally Traditional Chinese first, with English
# technical terminology preserved. Engineering reference documents keep the
# existing bilingual marker policy until they are migrated separately.
BILINGUAL_DOCS = [
    rel for rel in REQUIRED_DOCS if rel != "README.md"
]

REQUIRED_IMPLEMENTATION = [
    ".gitlab-ci.yml",
    "etl_intelligence/parser.py",
    "etl_intelligence/analyzer.py",
    "schemas/etl-metadata.schema.json",
    "schemas/etl-intelligence.schema.json",
    "scripts/etl_intelligence_smoke.sh",
    "scripts/vulnerability_gate.py",
    "scripts/vulnerability_lifecycle_smoke.sh",
    "scripts/registry_promote.sh",
    "scripts/verify_image_digest.sh",
    "etl_intelligence/metadata.py",
    "etl_intelligence/pentaho.py",
    "etl_intelligence/migration.py",
    "etl_intelligence/gateway.py",
    "scripts/migration_case.py",
    "scripts/p1_integration_smoke.sh",
    "samples/pentaho_to_hop/legacy_order_enrichment.ktr",
    "samples/pentaho_to_hop/legacy_daily_orders.kjb",
    "etl_intelligence/evaluation.py",
    "scripts/evaluate_etl_ai.py",
    "evaluation/dataset.json",
    "tests/test_p2_evaluation.py",
    "reports/baseline/etl-ai-evaluation-summary.json",
    "reports/baseline/etl-ai-evaluation-summary.html",
]
FORBIDDEN_TOKENS = [
    "10." + "0.0.",
    "192." + "168.",
    "corp" + "." + "local",
    "production-" + "password",
    "real-" + "customer",
]


def validate_bilingual(path: Path, errors: list[str]) -> None:
    text = path.read_text(encoding="utf-8")
    if "繁體中文" not in text or "English" not in text:
        errors.append(f"document must be bilingual: {path.relative_to(ROOT)}")


def main() -> int:
    errors: list[str] = []

    for rel in REQUIRED_DOCS:
        path = ROOT / rel
        if not path.exists():
            errors.append(f"missing required document: {rel}")

    for rel in BILINGUAL_DOCS:
        path = ROOT / rel
        if path.exists():
            validate_bilingual(path, errors)

    for rel in REQUIRED_IMPLEMENTATION:
        if not (ROOT / rel).exists():
            errors.append(f"missing required implementation: {rel}")

    if (ROOT / "VERSION").read_text(encoding="utf-8").strip() != "0.8.0":
        errors.append("VERSION must be 0.8.0 for the v0.8 release")

    releases_dir = ROOT / "docs/releases"
    if releases_dir.exists():
        for path in releases_dir.glob("v*.md"):
            validate_bilingual(path, errors)

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
