"""Deterministic Pentaho KTR/KJB parser for public synthetic migration fixtures."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any
from xml.etree import ElementTree

from .metadata import SCHEMA_VERSION, finalize_metadata

SQL_TABLE = re.compile(r"(?i)\b(?:from|join)\s+([A-Za-z0-9_$\{\}.]+)")


def _text(node: ElementTree.Element, path: str, default: str = "") -> str:
    value = node.findtext(path)
    return value.strip() if isinstance(value, str) else default


class _Evidence:
    def __init__(self, source_path: str):
        self.source_path = source_path
        self.items: list[dict[str, str]] = []

    def add(self, kind: str, locator: str, value: str = "") -> str:
        ref = f"ev-{len(self.items) + 1:04d}"
        self.items.append(
            {
                "id": ref,
                "source_path": self.source_path,
                "kind": kind,
                "locator": locator,
                "value": value,
            }
        )
        return ref


class PentahoLegacyParser:
    """Parse representative Pentaho transformation/job XML without AI."""

    def parse(self, source: str | Path) -> dict[str, Any]:
        path = Path(source)
        root = ElementTree.parse(path).getroot()
        if path.suffix.lower() == ".ktr" or root.tag == "transformation":
            return self._parse_transformation(path, root)
        if path.suffix.lower() == ".kjb" or root.tag == "job":
            return self._parse_job(path, root)
        raise ValueError(f"unsupported Pentaho artifact: {path}")

    def _base(self, path: Path, name: str, kind: str) -> dict[str, Any]:
        return {
            "schema_version": SCHEMA_VERSION,
            "pipeline": {
                "id": name,
                "name": name,
                "kind": kind,
                "format": "pentaho-xml",
                "source_path": path.as_posix(),
            },
            "steps": [],
            "hops": [],
            "sql": [],
            "sources": [],
            "targets": [],
            "tables": [],
            "fields": [],
            "columns": [],
            "connections": [],
            "dependencies": [],
            "parameters": [],
            "variables": [],
            "evidence": [],
            "provenance": {
                "parser": "enterprise-etl deterministic pentaho parser",
                "parser_version": SCHEMA_VERSION,
                "source_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "ai_used": False,
            },
        }

    def _read_parameters(self, root: ElementTree.Element, evidence: _Evidence) -> list[dict[str, Any]]:
        result = []
        nodes = root.findall("./info/parameters/parameter") + root.findall("./parameters/parameter")
        for index, node in enumerate(nodes, start=1):
            name = _text(node, "name")
            if not name:
                continue
            ref = evidence.add("parameter", f"parameter[{index}]", name)
            result.append(
                {
                    "name": name,
                    "default_value": _text(node, "default_value") or _text(node, "default"),
                    "description": _text(node, "description"),
                    "evidence_refs": [ref],
                }
            )
        return result

    def _read_variables(self, root: ElementTree.Element, evidence: _Evidence) -> list[dict[str, Any]]:
        result = []
        for index, node in enumerate(root.findall(".//variables/variable"), start=1):
            name = _text(node, "name")
            if not name:
                continue
            ref = evidence.add("variable", f"variable[{index}]", name)
            result.append(
                {
                    "name": name,
                    "value": _text(node, "value"),
                    "scope": _text(node, "scope", "artifact"),
                    "evidence_refs": [ref],
                }
            )
        return result

    def _read_connections(self, root: ElementTree.Element, evidence: _Evidence) -> list[dict[str, Any]]:
        result = []
        for index, node in enumerate(root.findall("./connection"), start=1):
            name = _text(node, "name")
            if not name:
                continue
            ref = evidence.add("connection", f"./connection[{index}]", name)
            result.append(
                {
                    "name": name,
                    "type": _text(node, "type", "database"),
                    "config": {
                        "server": _text(node, "server"),
                        "database": _text(node, "database"),
                        "port": _text(node, "port"),
                    },
                    "evidence_refs": [ref],
                }
            )
        return result

    def _add_table(
        self,
        data: dict[str, Any],
        evidence: _Evidence,
        name: str,
        role: str,
        step_id: str,
        locator: str,
        connection: str | None,
        classification: str = "structural",
    ) -> None:
        ref = evidence.add("table", locator, name)
        table = {
            "name": name,
            "role": role,
            "connection": connection,
            "step_id": step_id,
            "classification": classification,
            "evidence_refs": [ref],
        }
        if not any(
            item.get("name") == name and item.get("role") == role and item.get("step_id") == step_id
            for item in data["tables"]
        ):
            data["tables"].append(table)
        endpoint = {
            "kind": "table",
            "name": name,
            "connection": connection,
            "step_id": step_id,
            "classification": classification,
            "evidence_refs": [ref],
        }
        if role == "source":
            if not any(item.get("name") == name and item.get("step_id") == step_id for item in data["sources"]):
                data["sources"].append(endpoint)
        elif role == "target":
            if not any(item.get("name") == name and item.get("step_id") == step_id for item in data["targets"]):
                data["targets"].append(endpoint)

    def _parse_transformation(self, path: Path, root: ElementTree.Element) -> dict[str, Any]:
        name = _text(root, "./info/name", path.stem)
        data = self._base(path, name, "pentaho-transformation")
        evidence = _Evidence(path.as_posix())
        data["pipeline"]["evidence_refs"] = [evidence.add("pipeline", "./info/name", name)]
        data["connections"] = self._read_connections(root, evidence)
        data["parameters"] = self._read_parameters(root, evidence)
        data["variables"] = self._read_variables(root, evidence)

        for index, node in enumerate(root.findall("./step"), start=1):
            step_id = f"step-{index:04d}"
            step_name = _text(node, "name", step_id)
            step_type = _text(node, "type", "unknown")
            locator = f"./step[{index}]"
            step_ref = evidence.add("step", locator, f"{step_name}:{step_type}")
            connection = _text(node, "connection") or None
            schema = _text(node, "schema") or None
            table = _text(node, "table") or _text(node, "lookup/table") or None
            sql = _text(node, "sql")
            data["steps"].append(
                {
                    "id": step_id,
                    "name": step_name,
                    "type": step_type,
                    "description": _text(node, "description"),
                    "connection": connection,
                    "schema": schema,
                    "table": table,
                    "evidence_refs": [step_ref],
                }
            )

            if sql:
                sql_ref = evidence.add("sql", f"{locator}/sql", sql)
                data["sql"].append(
                    {
                        "id": f"sql-{len(data['sql']) + 1:04d}",
                        "step_id": step_id,
                        "statement": sql,
                        "evidence_refs": [sql_ref],
                    }
                )
                for sql_table in SQL_TABLE.findall(sql):
                    self._add_table(
                        data,
                        evidence,
                        sql_table,
                        "source",
                        step_id,
                        f"{locator}/sql:FROM_OR_JOIN",
                        connection,
                        classification="inferred-deterministic-sql-reference",
                    )

            if table:
                qualified = ".".join(part for part in (schema, table) if part)
                lowered = step_type.lower()
                role = (
                    "target"
                    if "output" in lowered or "writer" in lowered
                    else "source"
                    if "input" in lowered or "reader" in lowered
                    else "referenced"
                )
                self._add_table(
                    data,
                    evidence,
                    qualified,
                    role,
                    step_id,
                    f"{locator}/table",
                    connection,
                )

            for field_index, field in enumerate(node.findall(".//fields/field"), start=1):
                field_name = _text(field, "name") or _text(field, "field_name")
                if not field_name:
                    continue
                field_ref = evidence.add(
                    "field",
                    f"{locator}/fields/field[{field_index}]",
                    field_name,
                )
                data["fields"].append(
                    {
                        "step_id": step_id,
                        "name": field_name,
                        "target_name": _text(field, "rename") or _text(field, "column_name") or None,
                        "data_type": _text(field, "type") or None,
                        "expression": _text(field, "calculation") or _text(field, "formula") or None,
                        "evidence_refs": [field_ref],
                    }
                )

        for index, hop in enumerate(root.findall("./order/hop"), start=1):
            from_name = _text(hop, "from")
            to_name = _text(hop, "to")
            ref = evidence.add("hop", f"./order/hop[{index}]", f"{from_name}->{to_name}")
            data["hops"].append(
                {
                    "from": from_name,
                    "to": to_name,
                    "enabled": _text(hop, "enabled", "Y").upper() != "N",
                    "evidence_refs": [ref],
                }
            )

        data["evidence"] = evidence.items
        return finalize_metadata(data)

    def _parse_job(self, path: Path, root: ElementTree.Element) -> dict[str, Any]:
        name = _text(root, "./name") or _text(root, "./info/name", path.stem)
        data = self._base(path, name, "pentaho-job")
        evidence = _Evidence(path.as_posix())
        data["pipeline"]["evidence_refs"] = [evidence.add("pipeline", "./name", name)]
        data["parameters"] = self._read_parameters(root, evidence)
        data["variables"] = self._read_variables(root, evidence)

        for index, node in enumerate(root.findall("./entries/entry"), start=1):
            step_id = f"step-{index:04d}"
            step_name = _text(node, "name", step_id)
            step_type = _text(node, "type", "unknown")
            ref = evidence.add("step", f"./entries/entry[{index}]", f"{step_name}:{step_type}")
            data["steps"].append(
                {
                    "id": step_id,
                    "name": step_name,
                    "type": step_type,
                    "description": _text(node, "description"),
                    "connection": None,
                    "schema": None,
                    "table": None,
                    "evidence_refs": [ref],
                }
            )
            filename = _text(node, "filename") or _text(node, "transname") or _text(node, "jobname")
            if filename and step_type.upper() in {"TRANS", "JOB", "PIPELINE", "WORKFLOW"}:
                dep_ref = evidence.add(
                    "pipeline_dependency",
                    f"./entries/entry[{index}]/filename",
                    filename,
                )
                data["dependencies"].append(
                    {
                        "kind": "pipeline",
                        "from": name,
                        "to": filename,
                        "step_id": step_id,
                        "classification": "structural",
                        "evidence_refs": [dep_ref],
                    }
                )

        hop_nodes = root.findall("./hops/hop") + root.findall("./order/hop")
        for index, hop in enumerate(hop_nodes, start=1):
            from_name = _text(hop, "from")
            to_name = _text(hop, "to")
            ref = evidence.add("hop", f"job-hop[{index}]", f"{from_name}->{to_name}")
            data["hops"].append(
                {
                    "from": from_name,
                    "to": to_name,
                    "enabled": _text(hop, "enabled", "Y").upper() != "N",
                    "evidence_refs": [ref],
                }
            )

        data["evidence"] = evidence.items
        return finalize_metadata(data)
