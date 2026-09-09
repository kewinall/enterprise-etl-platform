import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class GitLabReferenceTest(unittest.TestCase):
    def test_reference_pipeline_covers_delivery_gates(self):
        text = (ROOT / ".gitlab-ci.yml").read_text()
        for token in (
            "validate_repository.py",
            "etl_intelligence_smoke.sh",
            "vulnerability_lifecycle_smoke.sh",
            "repository_trivy:",
            "container_trivy:",
            "sbom:",
            "registry_promote.sh",
            "verify_image_digest.sh",
            "when: manual",
            "resource_group: production",
        ):
            self.assertIn(token, text)

    def test_prod_job_never_rebuilds(self):
        text = (ROOT / ".gitlab-ci.yml").read_text()
        prod = text.split("promote_prod:", 1)[1]
        self.assertNotIn("docker build", prod)
        self.assertNotIn("build_runtime_image.sh", prod)
        self.assertIn("SOURCE_DIGEST", prod)

    def test_registry_promotion_checks_digest_identity(self):
        script = (ROOT / "scripts/registry_promote.sh").read_text()
        self.assertIn("SOURCE_DIGEST", script)
        self.assertIn("TARGET_DIGEST", script)
        self.assertIn("promotion digest mismatch", script)


if __name__ == "__main__":
    unittest.main()
