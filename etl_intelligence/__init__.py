"""Design-time ETL intelligence primitives.

The deterministic parser owns structural truth. Semantic analysis is a separate,
optional layer that may use an injected AI client but can never mutate parser truth.
"""

from .analyzer import SemanticAnalyzer, build_ai_context, metadata_digest
from .gateway import OpenAICompatibleGatewayClient
from .evaluation import detect_unsupported_claims, run_evaluation, write_report
from .migration import MigrationPlanner, MigrationValidator
from .parser import DeterministicETLParser

__all__ = [
    "DeterministicETLParser",
    "SemanticAnalyzer",
    "build_ai_context",
    "metadata_digest",
    "MigrationPlanner",
    "MigrationValidator",
    "OpenAICompatibleGatewayClient",
    "detect_unsupported_claims",
    "run_evaluation",
    "write_report",
]
