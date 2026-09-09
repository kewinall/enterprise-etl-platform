import json
import unittest
from pathlib import Path

from etl_intelligence import DeterministicETLParser, SemanticAnalyzer, build_ai_context


ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "samples/etl_intelligence/generic_order_enrichment.json"


class ETLIntelligenceTest(unittest.TestCase):
    def setUp(self):
        self.metadata = DeterministicETLParser().parse(SAMPLE)

    def test_parser_builds_normalized_structural_truth(self):
        self.assertEqual(self.metadata["pipeline"]["name"], "generic_order_enrichment")
        self.assertEqual(len(self.metadata["steps"]), 3)
        self.assertEqual(len(self.metadata["hops"]), 2)
        self.assertEqual(self.metadata["sources"][0]["name"], "staging.orders")
        self.assertEqual(self.metadata["targets"][0]["name"], "analytics.orders")
        self.assertFalse(self.metadata["provenance"]["ai_used"])
        self.assertGreaterEqual(len(self.metadata["evidence"]), 10)

    def test_parser_understands_existing_hop_pipeline(self):
        hop = ROOT / "hop/projects/enterprise-etl/pipelines/synthetic_customer_daily.hpl"
        parsed = DeterministicETLParser().parse(hop)
        self.assertEqual(parsed["pipeline"]["name"], "synthetic_customer_daily")
        self.assertGreaterEqual(len(parsed["steps"]), 4)
        self.assertGreaterEqual(len(parsed["hops"]), 3)
        self.assertEqual(parsed["targets"][0]["name"], "etl_data.synthetic_customer_daily")

    def test_ai_context_filters_credentials_and_sql_literals(self):
        context = build_ai_context(self.metadata)
        serialized = json.dumps(context, ensure_ascii=False)
        self.assertNotIn("synthetic-password", serialized)
        self.assertNotIn("synthetic_reader", serialized)
        self.assertNotIn("'READY'", serialized)
        self.assertIn("[REDACTED_LITERAL]", serialized)
        for connection in context["connections"]:
            self.assertEqual(set(connection), {"name", "type", "evidence_refs"})

    def test_ai_unavailable_falls_back_without_mutating_truth(self):
        before = json.dumps(self.metadata, sort_keys=True)
        result = SemanticAnalyzer().analyze(self.metadata)
        after = json.dumps(self.metadata, sort_keys=True)
        self.assertEqual(before, after)
        self.assertEqual(result["analysis_mode"], "fallback")
        self.assertTrue(result["provenance"]["parser_truth_preserved"])

    def test_ai_result_with_unknown_evidence_is_rejected(self):
        response = {
            "pipeline_summary": {"text": "Synthetic summary", "evidence_refs": ["ev-9999"]},
            "business_logic": [],
            "sql_explanations": [],
            "source_target_interpretation": [],
            "dependency_summary": [],
            "migration_assistance": [],
            "warnings": []
        }
        result = SemanticAnalyzer(lambda _system, _context: response).analyze(self.metadata)
        self.assertEqual(result["analysis_mode"], "fallback")
        self.assertIn("unknown evidence refs", result["warnings"][0])

    def test_valid_ai_result_stays_separate_from_parser_truth(self):
        pipeline_ref = self.metadata["pipeline"]["evidence_refs"][0]
        hop = self.metadata["hops"][0]
        response = {
            "pipeline_summary": {"text": "Generic synthetic pipeline.", "evidence_refs": [pipeline_ref]},
            "business_logic": [],
            "sql_explanations": [],
            "source_target_interpretation": [],
            "dependency_summary": [{
                "from": hop["from"],
                "to": hop["to"],
                "text": "Parser-recorded dependency.",
                "evidence_refs": hop["evidence_refs"]
            }],
            "migration_assistance": [],
            "warnings": []
        }
        result = SemanticAnalyzer(
            lambda _system, _context: response,
            provider_name="synthetic-test-client"
        ).analyze(self.metadata)
        self.assertEqual(result["analysis_mode"], "ai")
        self.assertEqual(result["provenance"]["ai_provider"], "synthetic-test-client")
        self.assertTrue(result["provenance"]["parser_truth_preserved"])
        self.assertNotIn("normalized_metadata", result)


if __name__ == "__main__":
    unittest.main()
