"""Deterministic legacy ETL migration planning and validation."""

from __future__ import annotations

import hashlib
import json
import re
from typing import Any

DIRECT = {
    "tableinput": ("Table Input", "direct"),
    "filterrows": ("Filter Rows", "direct"),
    "databaselookup": ("Database Lookup", "direct-with-validation"),
    "calculator": ("Calculator", "direct-with-validation"),
    "selectvalues": ("Select Values", "direct"),
    "tableoutput": ("Table Output", "direct"),
    "mergejoin": ("Merge Join", "manual-review"),
    "trans": ("Pipeline action", "manual-review"),
    "job": ("Workflow action", "manual-review"),
    "setvariables": ("Set Variables", "direct-with-validation"),
}

SPACE = re.compile(r"\s+")


def _sql_digest(sql: str) -> str:
    normalized = SPACE.sub(" ", sql.strip()).lower()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _table_set(metadata: dict[str, Any], key: str) -> set[str]:
    return {str(item.get("name")) for item in metadata.get(key, []) if item.get("name")}


class MigrationPlanner:
    """Create a deterministic compatibility assessment from normalized metadata."""

    def plan(self, metadata: dict[str, Any]) -> dict[str, Any]:
        components = []
        for step in metadata.get("steps", []):
            step_type = str(step.get("type") or "unknown")
            target_type, disposition = DIRECT.get(
                step_type.lower(),
                ("No automatic mapping", "manual-required"),
            )
            components.append(
                {
                    "step_id": step.get("id"),
                    "legacy_name": step.get("name"),
                    "legacy_type": step_type,
                    "hop_target": target_type,
                    "disposition": disposition,
                    "evidence_refs": list(step.get("evidence_refs", [])),
                }
            )

        return {
            "pipeline": metadata.get("pipeline", {}),
            "component_mapping": components,
            "connection_strategy": [
                {
                    "name": item.get("name"),
                    "action": (
                        "Recreate as Apache Hop metadata connection; resolve credentials "
                        "from environment/secret management, never from generated code."
                    ),
                    "evidence_refs": list(item.get("evidence_refs", [])),
                }
                for item in metadata.get("connections", [])
            ],
            "parameter_strategy": [
                {
                    "name": item.get("name"),
                    "action": "Preserve name and explicit default; bind per Hop environment at runtime.",
                    "evidence_refs": list(item.get("evidence_refs", [])),
                }
                for item in metadata.get("parameters", [])
            ],
            "variable_strategy": [
                {
                    "name": item.get("name"),
                    "action": "Preserve variable reference; validate scope and late binding explicitly.",
                    "evidence_refs": list(item.get("evidence_refs", [])),
                }
                for item in metadata.get("variables", [])
            ],
            "workflow_dependencies": [
                item for item in metadata.get("dependencies", []) if item.get("kind") == "pipeline"
            ],
            "sql_strategy": [
                {
                    "sql_id": item.get("id"),
                    "source_digest": _sql_digest(str(item.get("statement") or "")),
                    "action": (
                        "Carry SQL as reviewed source text first; parameterize connection/runtime "
                        "values separately. Optimize only after equivalence validation."
                    ),
                    "evidence_refs": list(item.get("evidence_refs", [])),
                }
                for item in metadata.get("sql", [])
            ],
            "correctness_gates": [
                "parser evidence and source SHA remain immutable",
                "all source/target tables are reconciled deterministically",
                "workflow dependencies and parameter/variable names are preserved",
                "SQL text changes require explicit review or digest-equivalence evidence",
                "representative input/output reconciliation is required before production",
                "AI recommendation is advisory and never a pass/fail correctness gate",
            ],
        }


class MigrationValidator:
    """Compare normalized legacy and target metadata using deterministic checks."""

    def validate(self, legacy: dict[str, Any], target: dict[str, Any]) -> dict[str, Any]:
        checks: list[dict[str, Any]] = []

        def add(name: str, passed: bool, expected: Any, actual: Any, severity: str = "error") -> None:
            checks.append(
                {
                    "name": name,
                    "passed": bool(passed),
                    "severity": severity,
                    "expected": expected,
                    "actual": actual,
                }
            )

        legacy_sources = sorted(_table_set(legacy, "sources"))
        target_sources = sorted(_table_set(target, "sources"))
        legacy_targets = sorted(_table_set(legacy, "targets"))
        target_targets = sorted(_table_set(target, "targets"))
        add("source tables preserved", legacy_sources == target_sources, legacy_sources, target_sources)
        add("target tables preserved", legacy_targets == target_targets, legacy_targets, target_targets)

        legacy_params = sorted(str(x.get("name")) for x in legacy.get("parameters", []) if x.get("name"))
        target_params = sorted(str(x.get("name")) for x in target.get("parameters", []) if x.get("name"))
        add(
            "parameters preserved",
            set(legacy_params).issubset(set(target_params)),
            legacy_params,
            target_params,
            severity="warning",
        )

        legacy_vars = sorted(str(x.get("name")) for x in legacy.get("variables", []) if x.get("name"))
        target_vars = sorted(str(x.get("name")) for x in target.get("variables", []) if x.get("name"))
        add(
            "variables preserved",
            set(legacy_vars).issubset(set(target_vars)),
            legacy_vars,
            target_vars,
            severity="warning",
        )

        legacy_sql = sorted(_sql_digest(str(x.get("statement") or "")) for x in legacy.get("sql", []))
        target_sql = sorted(_sql_digest(str(x.get("statement") or "")) for x in target.get("sql", []))
        add("SQL digest preserved", legacy_sql == target_sql, legacy_sql, target_sql)

        source_steps = {str(x.get("name")) for x in legacy.get("steps", []) if x.get("name")}
        target_steps = {str(x.get("name")) for x in target.get("steps", []) if x.get("name")}
        add(
            "named transformation steps preserved",
            source_steps.issubset(target_steps),
            sorted(source_steps),
            sorted(target_steps),
            severity="warning",
        )

        errors = [item for item in checks if not item["passed"] and item["severity"] == "error"]
        warnings = [item for item in checks if not item["passed"] and item["severity"] == "warning"]
        return {
            "status": "PASS" if not errors else "FAIL",
            "checks": checks,
            "error_count": len(errors),
            "warning_count": len(warnings),
            "ai_used": False,
            "correctness_authority": "deterministic migration validator",
        }


def migration_report(metadata: dict[str, Any], target: dict[str, Any] | None = None) -> dict[str, Any]:
    result = {"plan": MigrationPlanner().plan(metadata)}
    if target is not None:
        result["validation"] = MigrationValidator().validate(metadata, target)
    return result


def dumps_report(report: dict[str, Any]) -> str:
    return json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True)
