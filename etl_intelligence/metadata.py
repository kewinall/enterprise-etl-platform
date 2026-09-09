"""Normalized metadata enrichment and deterministic lineage classification."""

from __future__ import annotations

import copy
from collections import deque
from typing import Any

SCHEMA_VERSION = "1.1"


def _uniq(items: list[str]) -> list[str]:
    return list(dict.fromkeys(item for item in items if item))


def _step_id_by_name(metadata: dict[str, Any]) -> dict[str, str]:
    return {
        str(step.get("name")): str(step.get("id"))
        for step in metadata.get("steps", [])
        if step.get("name") and step.get("id")
    }


def _resolve_endpoint_step(metadata: dict[str, Any], endpoint: dict[str, Any]) -> str | None:
    if endpoint.get("step_id"):
        return str(endpoint["step_id"])
    name = str(endpoint.get("name") or "")
    for step in metadata.get("steps", []):
        table = str(step.get("table") or "")
        schema = str(step.get("schema") or "")
        qualified = ".".join(part for part in (schema, table) if part)
        if qualified == name or table == name:
            return str(step.get("id"))
    return None


def _reachable(adjacency: dict[str, set[str]], start: str, target: str) -> bool:
    queue: deque[str] = deque([start])
    seen: set[str] = set()
    while queue:
        node = queue.popleft()
        if node == target:
            return True
        if node in seen:
            continue
        seen.add(node)
        queue.extend(sorted(adjacency.get(node, set()) - seen))
    return False


def finalize_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
    """Upgrade parser output to the v1.1 contract without probabilistic inference."""
    result = copy.deepcopy(metadata)
    result["schema_version"] = SCHEMA_VERSION
    result.setdefault("columns", [])
    result.setdefault("dependencies", [])
    result.setdefault("parameters", [])
    result.setdefault("variables", [])
    result.setdefault("capability_boundaries", [])

    if not result["columns"]:
        result["columns"] = [
            {
                "step_id": field.get("step_id"),
                "name": field.get("name"),
                "target_name": field.get("target_name"),
                "data_type": field.get("data_type"),
                "expression": field.get("expression"),
                "lineage_classification": "structural-field-declaration",
                "evidence_refs": list(field.get("evidence_refs", [])),
            }
            for field in result.get("fields", [])
        ]

    step_ids = _step_id_by_name(result)
    dependency_keys = {
        (str(item.get("kind")), str(item.get("from")), str(item.get("to")))
        for item in result["dependencies"]
    }
    structural: list[dict[str, Any]] = []

    for hop in result.get("hops", []):
        if not hop.get("enabled", True):
            continue
        from_name = str(hop.get("from") or "")
        to_name = str(hop.get("to") or "")
        from_id = step_ids.get(from_name, from_name)
        to_id = step_ids.get(to_name, to_name)
        key = ("step", from_id, to_id)
        if key not in dependency_keys:
            result["dependencies"].append(
                {
                    "kind": "step",
                    "from": from_id,
                    "to": to_id,
                    "from_name": from_name,
                    "to_name": to_name,
                    "classification": "structural",
                    "evidence_refs": list(hop.get("evidence_refs", [])),
                }
            )
            dependency_keys.add(key)
        structural.append(
            {
                "kind": "step_dependency",
                "from": f"step:{from_id}",
                "to": f"step:{to_id}",
                "classification": "structural",
                "evidence_refs": list(hop.get("evidence_refs", [])),
            }
        )

    for endpoint_name, edge_kind in (("sources", "reads_from"), ("targets", "writes_to")):
        for endpoint in result.get(endpoint_name, []):
            step_id = _resolve_endpoint_step(result, endpoint)
            if not step_id:
                continue
            endpoint["step_id"] = step_id
            table_name = str(endpoint.get("name") or "")
            if edge_kind == "reads_from":
                edge_from, edge_to = f"table:{table_name}", f"step:{step_id}"
            else:
                edge_from, edge_to = f"step:{step_id}", f"table:{table_name}"
            structural.append(
                {
                    "kind": edge_kind,
                    "from": edge_from,
                    "to": edge_to,
                    "classification": "structural",
                    "evidence_refs": list(endpoint.get("evidence_refs", [])),
                }
            )

    for dependency in result["dependencies"]:
        if dependency.get("kind") != "pipeline":
            continue
        structural.append(
            {
                "kind": "workflow_dependency",
                "from": f"pipeline:{result.get('pipeline', {}).get('id')}",
                "to": f"pipeline:{dependency.get('to')}",
                "classification": "structural",
                "evidence_refs": list(dependency.get("evidence_refs", [])),
            }
        )

    adjacency: dict[str, set[str]] = {}
    for dependency in result["dependencies"]:
        if dependency.get("kind") != "step" or dependency.get("classification") != "structural":
            continue
        adjacency.setdefault(str(dependency.get("from")), set()).add(str(dependency.get("to")))

    inferred: list[dict[str, Any]] = []
    for source in result.get("sources", []):
        source_step = source.get("step_id")
        if not source_step:
            continue
        for target in result.get("targets", []):
            target_step = target.get("step_id")
            if not target_step or not _reachable(adjacency, str(source_step), str(target_step)):
                continue
            refs = _uniq(
                list(source.get("evidence_refs", []))
                + list(target.get("evidence_refs", []))
            )
            inferred.append(
                {
                    "kind": "table_flow",
                    "from": f"table:{source.get('name')}",
                    "to": f"table:{target.get('name')}",
                    "classification": "inferred-deterministic",
                    "derivation": "reachable explicit step dependency path",
                    "evidence_refs": refs,
                }
            )

    result["lineage"] = {
        "structural": structural,
        "inferred": inferred,
        "ai_interpretation": [],
    }
    boundary = (
        "Column-level lineage is emitted only when a parser has an explicit field mapping. "
        "SQL expression lineage, wildcard expansion, dynamic SQL, and runtime-resolved schema "
        "are not claimed as deterministic column lineage."
    )
    if boundary not in result["capability_boundaries"]:
        result["capability_boundaries"].append(boundary)
    return result
