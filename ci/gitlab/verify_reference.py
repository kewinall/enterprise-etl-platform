#!/usr/bin/env python3
"""Static verification for the GitLab enterprise delivery reference."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PIPELINE = (ROOT / ".gitlab-ci.yml").read_text(encoding="utf-8")

REQUIRED = [
    "validate_repository.py",
    "unittest discover",
    "etl_intelligence_smoke.sh",
    "vulnerability_lifecycle_smoke.sh",
    "trivy",
    "secret_scan.py",
    "cyclonedx-json",
    "registry_promote.sh",
    "verify_image_digest.sh",
    "environment:",
    "when: manual",
    "resource_group: production",
]

missing = [token for token in REQUIRED if token not in PIPELINE]
if missing:
    raise SystemExit("GitLab reference missing: " + ", ".join(missing))

prod = PIPELINE.split("promote_prod:", 1)[1]
if "docker build" in prod or "build_runtime_image.sh" in prod:
    raise SystemExit("PROD promotion must not rebuild the image")

print("GitLab reference verification passed.")
