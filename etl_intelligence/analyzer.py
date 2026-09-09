#!/usr/bin/env python3
"""Semantic analysis boundary for deterministic ETL metadata."""

from __future__ import annotations

import copy
import hashlib
import json
import re
from typing import Any, Callable

SYSTEM_PROMPT = """You are an ETL design-time semantic analyzer.
Use only the supplied normalized parser metadata.
Never infer structural facts that are absent from the metadata.
Return JSON only and follow the requested output contract.
Every factual explanation must cite one or more evidence_refs from the context.
Do not create new tables, fields, steps, SQL IDs, connections, or dependencies.
Redacted values must remain redacted.
The deterministic parser is authoritative; your output is commentary, never parser truth.
"""

SENSITIVE_KEY = re.compile(
    r"(password|passwd|secret|token|api[_-]?key|credential|private[_-]?key)",
    re.IGNORECASE,
)
SQL_LITERAL = re.compile(r"'(?:''|[^'])*'")


def metadata_digest(metadata: dict[str, Any]) -> str:
    canonical = json.dumps(metadata, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _sanitize(value: Any, key: str = "") -> Any:
    if SENSITIVE_KEY.search(key):
        return "[REDACTED]"
    if isinstance(value, dict):
        return {k: _sanitize(v, str(k)) for k, v in value.items()}
    if isinstance(value, list):
        return [_sanitize(v, key) for v in value]
    return value


def _sanitize_sql(sql: str) -> str:
    return SQL_LITERAL.sub("'[REDACTED_LITERAL]'", sql)


def build_ai_context(metadata: dict[str, Any]) -> dict[str, Any]:
    """Create the only context allowed to cross the AI boundary."""

    context = {
        "schema_version": metadata.get("schema_version"),
        "pipeline": copy.deepcopy(metadata.get("pipeline", {})),
        "steps": copy.deepcopy(metadata.get("steps", [])),
        "hops": copy.deepcopy(metadata.get("hops", [])),
        "sql": copy.deepcopy(metadata.get("sql", [])),
        "sources": copy.deepcopy(metadata.get("sources", [])),
        "targets": copy.deepcopy(metadata.get("targets", [])),
        "tables": copy.deepcopy(metadata.get("tables", [])),
        "fields": copy.deepcopy(metadata.get("fields", [])),
        "columns": copy.deepcopy(metadata.get("columns", [])),
        "dependencies": copy.deepcopy(metadata.get("dependencies", [])),
        "parameters": [
            {
                "name": item.get("name"),
                "description": item.get("description"),
                "evidence_refs": item.get("evidence_refs", []),
            }
            for item in metadata.get("parameters", [])
        ],
        "variables": [
            {
                "name": item.get("name"),
                "scope": item.get("scope"),
                "evidence_refs": item.get("evidence_refs", []),
            }
            for item in metadata.get("variables", [])
        ],
        "lineage": copy.deepcopy(metadata.get("lineage", {})),
        "capability_boundaries": copy.deepcopy(metadata.get("capability_boundaries", [])),
        "connections": [
            {
                "name": item.get("name"),
                "type": item.get("type"),
                "evidence_refs": item.get("evidence_refs", []),
            }
            for item in metadata.get("connections", [])
        ],
        "evidence": copy.deepcopy(metadata.get("evidence", [])),
        "parser_truth_digest": metadata_digest(metadata),
    }
    for item in context["sql"]:
        item["statement"] = _sanitize_sql(str(item.get("statement") or ""))
    for item in context["evidence"]:
        if item.get("kind") == "sql":
            item["value"] = _sanitize_sql(str(item.get("value") or ""))
        else:
            item["value"] = _sanitize(item.get("value"), str(item.get("kind") or ""))
    return _sanitize(context)


def _all_evidence_refs(value: Any) -> list[str]:
    refs: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key == "evidence_refs" and isinstance(child, list):
                refs.extend(str(item) for item in child)
            else:
                refs.extend(_all_evidence_refs(child))
    elif isinstance(value, list):
        for child in value:
            refs.extend(_all_evidence_refs(child))
    return refs


def _strip_code_fence(text: str) -> str:
    stripped = text.strip()
    fence = chr(96) * 3
    if stripped.startswith(fence) and stripped.endswith(fence):
        lines = stripped.splitlines()
        return "\n".join(lines[1:-1]).strip()
    return stripped


def validate_ai_result(result: dict[str, Any], metadata: dict[str, Any]) -> dict[str, Any]:
    required = {
        "pipeline_summary",
        "business_logic",
        "sql_explanations",
        "source_target_interpretation",
        "dependency_summary",
        "migration_assistance",
        "warnings",
    }
    missing = sorted(required - set(result))
    if missing:
        raise ValueError(f"AI result missing keys: {', '.join(missing)}")

    allowed_evidence = {str(item["id"]) for item in metadata.get("evidence", [])}
    unknown_refs = sorted(set(_all_evidence_refs(result)) - allowed_evidence)
    if unknown_refs:
        raise ValueError(f"AI result contains unknown evidence refs: {unknown_refs}")

    allowed_sql = {str(item["id"]) for item in metadata.get("sql", [])}
    for item in result.get("sql_explanations", []):
        sql_id = str(item.get("sql_id") or "")
        if sql_id not in allowed_sql:
            raise ValueError(f"AI result references unknown sql_id: {sql_id}")

    allowed_nodes = {
        str(item.get("name"))
        for item in metadata.get("steps", [])
        if item.get("name")
    }
    allowed_nodes.update(
        str(value)
        for dependency in metadata.get("dependencies", [])
        for value in (dependency.get("from"), dependency.get("to"))
        if value
    )
    pipeline = metadata.get("pipeline", {})
    allowed_nodes.update(
        str(value) for value in (pipeline.get("id"), pipeline.get("name")) if value
    )
    for item in result.get("dependency_summary", []):
        if str(item.get("from") or "") not in allowed_nodes:
            raise ValueError(f"AI result references unknown dependency source: {item.get('from')}")
        if str(item.get("to") or "") not in allowed_nodes:
            raise ValueError(f"AI result references unknown dependency target: {item.get('to')}")

    return result


def deterministic_fallback(metadata: dict[str, Any], reason: str) -> dict[str, Any]:
    pipeline = metadata.get("pipeline", {})
    steps = metadata.get("steps", [])
    hops = metadata.get("hops", [])

    return {
        "schema_version": "1.0",
        "analysis_mode": "fallback",
        "parser_truth_digest": metadata_digest(metadata),
        "pipeline_summary": {
            "text": (
                f"{pipeline.get('name', 'unnamed')} contains {len(steps)} deterministic "
                f"steps and {len(hops)} declared dependencies."
            ),
            "evidence_refs": pipeline.get("evidence_refs", []),
        },
        "business_logic": [
            {
                "text": f"Step '{step.get('name')}' is structurally typed as '{step.get('type')}'.",
                "evidence_refs": step.get("evidence_refs", []),
            }
            for step in steps
        ],
        "sql_explanations": [
            {
                "sql_id": item.get("id"),
                "text": "SQL is present. Semantic explanation is unavailable without an approved AI client.",
                "evidence_refs": item.get("evidence_refs", []),
            }
            for item in metadata.get("sql", [])
        ],
        "source_target_interpretation": [],
        "dependency_summary": [
            {
                "from": hop.get("from"),
                "to": hop.get("to"),
                "text": f"Deterministic dependency: {hop.get('from')} -> {hop.get('to')}.",
                "evidence_refs": hop.get("evidence_refs", []),
            }
            for hop in hops
            if hop.get("enabled", True)
        ],
        "migration_assistance": [],
        "warnings": [f"AI semantic analysis unavailable or rejected: {reason}"],
        "provenance": {
            "ai_provider": "none",
            "parser_truth_preserved": True,
        },
    }


class SemanticAnalyzer:
    """Use an injected AI client and enforce evidence-bound structured output."""

    def __init__(
        self,
        ai_client: Callable[[str, str], str | dict[str, Any]] | None = None,
        provider_name: str = "injected-client",
    ) -> None:
        self.ai_client = ai_client
        self.provider_name = provider_name

    def analyze(self, metadata: dict[str, Any]) -> dict[str, Any]:
        if self.ai_client is None:
            return deterministic_fallback(metadata, "no AI client configured")

        context = build_ai_context(metadata)
        request = {
            "output_contract": {
                "pipeline_summary": {"text": "string", "evidence_refs": ["ev-0001"]},
                "business_logic": [{"text": "string", "evidence_refs": ["ev-0001"]}],
                "sql_explanations": [
                    {"sql_id": "sql-0001", "text": "string", "evidence_refs": ["ev-0001"]}
                ],
                "source_target_interpretation": [
                    {"source": "string", "target": "string", "text": "string", "evidence_refs": ["ev-0001"]}
                ],
                "dependency_summary": [
                    {"from": "step name", "to": "step name", "text": "string", "evidence_refs": ["ev-0001"]}
                ],
                "migration_assistance": [
                    {"recommendation": "string", "evidence_refs": ["ev-0001"]}
                ],
                "warnings": ["string"],
            },
            "normalized_metadata": context,
        }

        try:
            raw = self.ai_client(
                SYSTEM_PROMPT,
                json.dumps(request, ensure_ascii=False, sort_keys=True),
            )
            if isinstance(raw, str):
                parsed = json.loads(_strip_code_fence(raw))
            elif isinstance(raw, dict):
                parsed = copy.deepcopy(raw)
            else:
                raise ValueError("AI client returned unsupported response type")
            validated = validate_ai_result(parsed, metadata)
        except Exception as exc:
            return deterministic_fallback(metadata, str(exc))

        validated["schema_version"] = "1.0"
        validated["analysis_mode"] = "ai"
        validated["parser_truth_digest"] = metadata_digest(metadata)
        validated["provenance"] = {
            "ai_provider": self.provider_name,
            "parser_truth_preserved": True,
            "context_redacted": True,
        }
        return validated
