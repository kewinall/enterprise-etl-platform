import unittest
from pathlib import Path

from etl_intelligence import DeterministicETLParser
from etl_intelligence.migration import MigrationPlanner, MigrationValidator

ROOT = Path(__file__).resolve().parents[1]
CASE = ROOT / "samples/pentaho_to_hop"


class PentahoToHopMigrationCaseTest(unittest.TestCase):
    def test_ktr_parser_extracts_migration_relevant_metadata(self):
        metadata = DeterministicETLParser().parse(CASE / "legacy_order_enrichment.ktr")
        self.assertEqual(metadata["schema_version"], "1.1")
        self.assertEqual(metadata["pipeline"]["kind"], "pentaho-transformation")
        self.assertIn("staging.orders", {item["name"] for item in metadata["sources"]})
        self.assertIn("staging.discounts", {item["name"] for item in metadata["sources"]})
        self.assertIn("${TARGET_SCHEMA}.orders_enriched", {item["name"] for item in metadata["targets"]})
        self.assertIn("BATCH_DATE", {item["name"] for item in metadata["parameters"]})
        self.assertIn("TARGET_SCHEMA", {item["name"] for item in metadata["variables"]})
        self.assertTrue(metadata["lineage"]["structural"])
        self.assertTrue(metadata["lineage"]["inferred"])
        self.assertEqual(metadata["lineage"]["ai_interpretation"], [])
        self.assertTrue(metadata["capability_boundaries"])

    def test_kjb_preserves_job_to_transformation_dependency(self):
        metadata = DeterministicETLParser().parse(CASE / "legacy_daily_orders.kjb")
        dependencies = [
            item for item in metadata["dependencies"] if item.get("kind") == "pipeline"
        ]
        self.assertEqual(dependencies[0]["to"], "legacy_order_enrichment.ktr")
        self.assertEqual(dependencies[0]["classification"], "structural")

    def test_planner_marks_merge_join_for_manual_review(self):
        metadata = DeterministicETLParser().parse(CASE / "legacy_order_enrichment.ktr")
        plan = MigrationPlanner().plan(metadata)
        decisions = {item["legacy_type"]: item["disposition"] for item in plan["component_mapping"]}
        self.assertEqual(decisions["TableInput"], "direct")
        self.assertEqual(decisions["DatabaseLookup"], "direct-with-validation")
        self.assertEqual(decisions["MergeJoin"], "manual-review")
        self.assertIn(
            "AI recommendation is advisory and never a pass/fail correctness gate",
            plan["correctness_gates"],
        )

    def test_deterministic_validation_passes_representative_target_design(self):
        parser = DeterministicETLParser()
        legacy = parser.parse(CASE / "legacy_order_enrichment.ktr")
        target = parser.parse(CASE / "hop_order_enrichment.hpl")
        result = MigrationValidator().validate(legacy, target)
        self.assertEqual(result["status"], "PASS")
        self.assertFalse(result["ai_used"])
        self.assertEqual(result["correctness_authority"], "deterministic migration validator")


if __name__ == "__main__":
    unittest.main()
