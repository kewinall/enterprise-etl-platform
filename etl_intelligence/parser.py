#!/usr/bin/env python3
"""Deterministic ETL parser for Apache Hop XML and a generic legacy JSON format."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any
from xml.etree import ElementTree

from .metadata import finalize_metadata

SCHEMA_VERSION = "1.1"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _text(node: ElementTree.Element, path: str, default: str = "") -> str:
    value = node.findtext(path)
    return value.strip() if isinstance(value, str) else default


class EvidenceBuilder:
    def __init__(self, source_path: str) -> None:
        self.source_path = source_path
        self.items: list[dict[str, str]] = []

    def add(self, kind: str, locator: str, value: str = "") -> str:
        evidence_id = f"ev-{len(self.items) + 1:04d}"
        self.items.append(
            {
                "id": evidence_id,
                "source_path": self.source_path,
                "kind": kind,
                "locator": locator,
                "value": value,
            }
        )
        return evidence_id


class DeterministicETLParser:
    """Parse ETL artifacts without using AI or probabilistic inference."""

    def parse(self, source: str | Path) -> dict[str, Any]:
        path = Path(source)
        suffix = path.suffix.lower()
        if suffix in {".ktr", ".kjb"}:
            from .pentaho import PentahoLegacyParser

            return PentahoLegacyParser().parse(path)
        if suffix in {".hpl", ".hwf", ".xml"}:
            return finalize_metadata(self._parse_hop_xml(path))
        if suffix == ".json":
            return finalize_metadata(self._parse_legacy_json(path))
        raise ValueError(f"unsupported ETL artifact: {path}")

    def _base(self, path: Path, name: str, kind: str, fmt: str) -> dict[str, Any]:
        return {
            "schema_version": SCHEMA_VERSION,
            "pipeline": {
                "id": name,
                "name": name,
                "kind": kind,
                "format": fmt,
                "source_path": path.as_posix(),
            },
            "steps": [],
            "hops": [],
            "sql": [],
            "sources": [],
            "targets": [],
            "tables": [],
            "fields": [],
            "connections": [],
            "evidence": [],
            "provenance": {
                "parser": "enterprise-etl deterministic parser",
                "parser_version": SCHEMA_VERSION,
                "source_sha256": _sha256(path),
                "ai_used": False,
            },
        }

    def _parse_hop_xml(self, path: Path) -> dict[str, Any]:
        root = ElementTree.parse(path).getroot()
        if root.tag not in {"pipeline", "workflow"}:
            raise ValueError(f"unsupported Hop root element: {root.tag}")

        name = _text(root, "./info/name", path.stem)
        data = self._base(path, name, f"apache-hop-{root.tag}", "xml")
        evidence = EvidenceBuilder(path.as_posix())
        pipeline_ev = evidence.add("pipeline", "./info/name", name)
        data["pipeline"]["evidence_refs"] = [pipeline_ev]

        data.setdefault("parameters", [])
        for parameter_index, parameter in enumerate(root.findall("./info/parameters/parameter"), start=1):
            parameter_name = _text(parameter, "name")
            if not parameter_name:
                continue
            parameter_ev = evidence.add(
                "parameter",
                f"./info/parameters/parameter[{parameter_index}]",
                parameter_name,
            )
            data["parameters"].append(
                {
                    "name": parameter_name,
                    "default_value": _text(parameter, "default_value") or _text(parameter, "default"),
                    "description": _text(parameter, "description"),
                    "evidence_refs": [parameter_ev],
                }
            )

        data.setdefault("variables", [])
        for variable_index, variable in enumerate(root.findall(".//variables/variable"), start=1):
            variable_name = _text(variable, "name")
            if not variable_name:
                continue
            variable_ev = evidence.add(
                "variable",
                f".//variables/variable[{variable_index}]",
                variable_name,
            )
            data["variables"].append(
                {
                    "name": variable_name,
                    "value": _text(variable, "value"),
                    "scope": _text(variable, "scope", "artifact"),
                    "evidence_refs": [variable_ev],
                }
            )

        seen_connections: set[str] = set()
        seen_tables: set[tuple[str, str]] = set()

        for index, transform in enumerate(root.findall("./transform"), start=1):
            step_name = _text(transform, "name", f"step-{index}")
            step_type = _text(transform, "type", "unknown")
            locator = f"./transform[{index}]"
            step_ev = evidence.add("step", locator, f"{step_name}:{step_type}")
            connection = _text(transform, "connection")
            schema = _text(transform, "schema")
            table = _text(transform, "table")
            sql_text = _text(transform, "sql")

            step = {
                "id": f"step-{index:04d}",
                "name": step_name,
                "type": step_type,
                "description": _text(transform, "description"),
                "connection": connection or None,
                "schema": schema or None,
                "table": table or None,
                "evidence_refs": [step_ev],
            }
            data["steps"].append(step)

            if connection and connection not in seen_connections:
                seen_connections.add(connection)
                conn_ev = evidence.add("connection", f"{locator}/connection", connection)
                data["connections"].append(
                    {
                        "name": connection,
                        "type": "reference",
                        "config": {},
                        "evidence_refs": [conn_ev],
                    }
                )

            for field_index, field in enumerate(transform.findall("./fields/field"), start=1):
                field_name = (
                    _text(field, "name")
                    or _text(field, "stream_name")
                    or _text(field, "column_name")
                )
                if not field_name:
                    continue
                field_ev = evidence.add(
                    "field",
                    f"{locator}/fields/field[{field_index}]",
                    field_name,
                )
                data["fields"].append(
                    {
                        "step_id": step["id"],
                        "name": field_name,
                        "target_name": _text(field, "column_name") or None,
                        "data_type": _text(field, "type") or None,
                        "evidence_refs": [field_ev],
                    }
                )

            if sql_text:
                sql_ev = evidence.add("sql", f"{locator}/sql", sql_text)
                data["sql"].append(
                    {
                        "id": f"sql-{len(data['sql']) + 1:04d}",
                        "step_id": step["id"],
                        "statement": sql_text,
                        "evidence_refs": [sql_ev],
                    }
                )

            if table:
                qualified = ".".join(part for part in (schema, table) if part)
                role = (
                    "source"
                    if "input" in step_type.lower()
                    else "target"
                    if "output" in step_type.lower()
                    else "referenced"
                )
                table_key = (qualified, role)
                table_ev = evidence.add("table", f"{locator}/table", qualified)
                if table_key not in seen_tables:
                    seen_tables.add(table_key)
                    data["tables"].append(
                        {
                            "name": qualified,
                            "role": role,
                            "connection": connection or None,
                            "evidence_refs": [table_ev],
                        }
                    )
                if role == "source":
                    data["sources"].append(
                        {
                            "kind": "table",
                            "name": qualified,
                            "connection": connection or None,
                            "evidence_refs": [table_ev],
                        }
                    )
                elif role == "target":
                    data["targets"].append(
                        {
                            "kind": "table",
                            "name": qualified,
                            "connection": connection or None,
                            "evidence_refs": [table_ev],
                        }
                    )

        for index, hop in enumerate(root.findall("./order/hop"), start=1):
            from_name = _text(hop, "from")
            to_name = _text(hop, "to")
            hop_ev = evidence.add("hop", f"./order/hop[{index}]", f"{from_name}->{to_name}")
            data["hops"].append(
                {
                    "from": from_name,
                    "to": to_name,
                    "enabled": _text(hop, "enabled", "Y").upper() != "N",
                    "evidence_refs": [hop_ev],
                }
            )

        data["evidence"] = evidence.items
        return data

    def _parse_legacy_json(self, path: Path) -> dict[str, Any]:
        payload = json.loads(path.read_text(encoding="utf-8"))
        pipeline = payload.get("pipeline") or {}
        name = str(pipeline.get("name") or path.stem)
        data = self._base(path, name, "legacy-etl", "json")
        evidence = EvidenceBuilder(path.as_posix())
        data["pipeline"]["description"] = str(pipeline.get("description") or "")
        data["pipeline"]["evidence_refs"] = [
            evidence.add("pipeline", "$.pipeline.name", name)
        ]

        for index, connection in enumerate(payload.get("connections", []), start=1):
            name_value = str(connection.get("name") or f"connection-{index}")
            ev = evidence.add("connection", f"$.connections[{index - 1}]", name_value)
            config = {
                str(k): v
                for k, v in connection.items()
                if k not in {"name", "type"}
            }
            data["connections"].append(
                {
                    "name": name_value,
                    "type": str(connection.get("type") or "unknown"),
                    "config": config,
                    "evidence_refs": [ev],
                }
            )

        for index, step_payload in enumerate(payload.get("steps", []), start=1):
            step_id = str(step_payload.get("id") or f"step-{index:04d}")
            name_value = str(step_payload.get("name") or step_id)
            step_type = str(step_payload.get("type") or "unknown")
            ev = evidence.add("step", f"$.steps[{index - 1}]", f"{name_value}:{step_type}")
            connection = step_payload.get("connection")
            table = step_payload.get("table")
            step = {
                "id": step_id,
                "name": name_value,
                "type": step_type,
                "description": str(step_payload.get("description") or ""),
                "connection": connection,
                "schema": step_payload.get("schema"),
                "table": table,
                "evidence_refs": [ev],
            }
            data["steps"].append(step)

            sql_text = step_payload.get("sql")
            if isinstance(sql_text, str) and sql_text.strip():
                sql_ev = evidence.add("sql", f"$.steps[{index - 1}].sql", sql_text)
                data["sql"].append(
                    {
                        "id": f"sql-{len(data['sql']) + 1:04d}",
                        "step_id": step_id,
                        "statement": sql_text,
                        "evidence_refs": [sql_ev],
                    }
                )

            for field_index, field in enumerate(step_payload.get("fields", []), start=1):
                if isinstance(field, str):
                    field = {"name": field}
                field_name = str(field.get("name") or "")
                if not field_name:
                    continue
                field_ev = evidence.add(
                    "field",
                    f"$.steps[{index - 1}].fields[{field_index - 1}]",
                    field_name,
                )
                data["fields"].append(
                    {
                        "step_id": step_id,
                        "name": field_name,
                        "target_name": field.get("target_name"),
                        "data_type": field.get("type"),
                        "expression": field.get("expression"),
                        "evidence_refs": [field_ev],
                    }
                )

            if table:
                role = str(step_payload.get("role") or "").lower()
                if role not in {"source", "target", "referenced"}:
                    lowered = step_type.lower()
                    role = (
                        "source"
                        if "input" in lowered or "source" in lowered or "read" in lowered
                        else "target"
                        if "output" in lowered or "target" in lowered or "write" in lowered
                        else "referenced"
                    )
                table_ev = evidence.add(
                    "table", f"$.steps[{index - 1}].table", str(table)
                )
                data["tables"].append(
                    {
                        "name": str(table),
                        "role": role,
                        "connection": connection,
                        "evidence_refs": [table_ev],
                    }
                )
                endpoint = {
                    "kind": "table",
                    "name": str(table),
                    "connection": connection,
                    "evidence_refs": [table_ev],
                }
                if role == "source":
                    data["sources"].append(endpoint)
                elif role == "target":
                    data["targets"].append(endpoint)

        for index, hop in enumerate(payload.get("hops", []), start=1):
            from_name = str(hop.get("from") or "")
            to_name = str(hop.get("to") or "")
            hop_ev = evidence.add(
                "hop", f"$.hops[{index - 1}]", f"{from_name}->{to_name}"
            )
            data["hops"].append(
                {
                    "from": from_name,
                    "to": to_name,
                    "enabled": bool(hop.get("enabled", True)),
                    "evidence_refs": [hop_ev],
                }
            )

        data["evidence"] = evidence.items
        return data
