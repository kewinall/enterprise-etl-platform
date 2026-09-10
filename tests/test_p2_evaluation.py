import json
import unittest
from pathlib import Path

from etl_intelligence import DeterministicETLParser, SemanticAnalyzer
from etl_intelligence.evaluation import detect_unsupported_claims, run_evaluation

ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "evaluation/dataset.json"


class P2EvaluationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = run_evaluation(DATASET, stable=True)

    def test_synthetic_dataset_is_repository_derived_and_exact(self):
        self.assertEqual(self.report["dataset"]["case_count"], 10)
        self.assertEqual(self.report["dataset"]["valid_case_count"], 9)
        self.assertEqual(self.report["dataset"]["expected_parse_failure_count"], 1)
        self.assertEqual(self.report["parser"]["unexpected_parsing_failure_rate"], 0.0)
        self.assertEqual(self.report["parser"]["structural_case_exact_match_rate"], 1.0)
        for metric in self.report["parser"]["metrics"].values():
            self.assertEqual(metric["precision"], 1.0)
            self.assertEqual(metric["recall"], 1.0)
            self.assertEqual(metric["exact_match_rate"], 1.0)

    def test_semantic_contract_is_grounded_and_preserves_parser_truth(self):
        semantic = self.report["semantic"]
        self.assertEqual(semantic["evaluated_cases"], 9)
        self.assertEqual(semantic["structured_output_validity"], 1.0)
        self.assertEqual(semantic["factual_consistency"], 1.0)
        self.assertEqual(semantic["grounding"], 1.0)
        self.assertEqual(semantic["completeness"], 1.0)
        self.assertEqual(semantic["unsupported_claim_count"], 0)
        self.assertEqual(semantic["parser_truth_preservation_rate"], 1.0)

    def test_no_gateway_evidence_means_no_fabricated_token_or_cost(self):
        batch = self.report["usage"]["batch"]
        projection = self.report["usage"]["projection_243"]
        self.assertIsNone(batch["input_tokens"])
        self.assertIsNone(batch["output_tokens"])
        self.assertIsNone(batch["estimated_cost_usd"])
        self.assertIsNone(projection["estimated_cost_usd"])
        self.assertEqual(projection["cost_status"], "unavailable-without-gateway-pricing-evidence")

    def test_repeatability_and_truth_preservation_are_measured(self):
        self.assertEqual(self.report["ablation"]["deterministic_repeatability_rate"], 1.0)
        self.assertEqual(self.report["ablation"]["parser_plus_ai_truth_preservation_rate"], 1.0)
        self.assertGreater(self.report["ablation"]["raw_artifact_input_bytes"], 0)
        self.assertGreater(self.report["ablation"]["structured_ai_context_bytes"], 0)

    def test_checked_in_baseline_matches_live_evaluator_headline(self):
        baseline = json.loads((ROOT / "reports/baseline/etl-ai-evaluation-summary.json").read_text(encoding="utf-8"))
        self.assertEqual(baseline["dataset_cases"], self.report["dataset"]["case_count"])
        self.assertEqual(baseline["parser"]["structural_case_exact_match_rate"], self.report["parser"]["structural_case_exact_match_rate"])
        self.assertEqual(baseline["parser"]["unexpected_parsing_failure_rate"], self.report["parser"]["unexpected_parsing_failure_rate"])
        self.assertEqual(baseline["semantic"]["structured_output_validity"], self.report["semantic"]["structured_output_validity"])
        self.assertEqual(baseline["semantic"]["unsupported_claim_count"], self.report["semantic"]["unsupported_claim_count"])

    def test_hallucinated_source_is_rejected(self):
        metadata = DeterministicETLParser().parse(ROOT / "evaluation/cases/simple_extraction.json")
        response = {
            "pipeline_summary": {"text": "Synthetic.", "evidence_refs": metadata["pipeline"]["evidence_refs"]},
            "business_logic": [], "sql_explanations": [],
            "source_target_interpretation": [{
                "source": "imaginary.table", "target": metadata["targets"][0]["name"],
                "text": "Unsupported structural claim.",
                "evidence_refs": metadata["sources"][0]["evidence_refs"] + metadata["targets"][0]["evidence_refs"],
            }],
            "dependency_summary": [], "migration_assistance": [], "warnings": [],
        }
        self.assertTrue(detect_unsupported_claims(response, metadata))
        result = SemanticAnalyzer(lambda _system, _request: response, max_validation_attempts=1).analyze(metadata)
        self.assertEqual(result["analysis_mode"], "fallback")
        self.assertIn("unknown source", result["warnings"][0])

    def test_invalid_structured_output_retries_then_accepts(self):
        metadata = DeterministicETLParser().parse(ROOT / "evaluation/cases/simple_extraction.json")
        calls = {"count": 0}
        def client(_system, _request):
            calls["count"] += 1
            if calls["count"] == 1:
                return {"pipeline_summary": {"text": "incomplete"}}
            return {
                "pipeline_summary": {"text": "Recovered.", "evidence_refs": metadata["pipeline"]["evidence_refs"]},
                "business_logic": [], "sql_explanations": [], "source_target_interpretation": [],
                "dependency_summary": [], "migration_assistance": [], "warnings": [],
            }
        result = SemanticAnalyzer(client, max_validation_attempts=2).analyze(metadata)
        self.assertEqual(result["analysis_mode"], "ai")
        self.assertEqual(calls["count"], 2)
        self.assertEqual(result["provenance"]["ai_attempts"], 2)
        self.assertEqual(result["provenance"]["retry_count"], 1)

    def test_gateway_transport_failure_is_not_retried_by_domain_layer(self):
        metadata = DeterministicETLParser().parse(ROOT / "evaluation/cases/simple_extraction.json")
        calls = {"count": 0}
        def client(_system, _request):
            calls["count"] += 1
            raise RuntimeError("synthetic gateway timeout")
        result = SemanticAnalyzer(client, max_validation_attempts=2).analyze(metadata)
        self.assertEqual(result["analysis_mode"], "fallback")
        self.assertEqual(calls["count"], 1)
        self.assertEqual(result["provenance"]["ai_attempts"], 1)
        self.assertEqual(result["provenance"]["retry_count"], 0)


if __name__ == "__main__":
    unittest.main()
