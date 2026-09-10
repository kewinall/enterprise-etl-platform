#!/usr/bin/env python3
"""Repeatable ETL AI evaluation over synthetic, repository-owned ground truth."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from time import perf_counter
from typing import Any, Callable

from .analyzer import SemanticAnalyzer, build_ai_context, metadata_digest, validate_ai_result
from .parser import DeterministicETLParser


def load_dataset(path: str | Path) -> dict[str, Any]:
    dataset_path = Path(path)
    payload = json.loads(dataset_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or not isinstance(payload.get("cases"), list):
        raise ValueError("evaluation dataset must be an object with a cases array")
    payload["_dataset_path"] = dataset_path.as_posix()
    return payload


def _as_set(values: list[Any]) -> set[str]:
    return {str(value) for value in values}


def _dependency_set(metadata: dict[str, Any]) -> set[str]:
    result: set[str] = set()
    for item in metadata.get("dependencies", []):
        kind = str(item.get("kind") or "")
        from_value = str(item.get("from_name") or item.get("from") or "")
        to_value = str(item.get("to_name") or item.get("to") or "")
        result.add(f"{kind}:{from_value}->{to_value}")
    return result


def _expected_dependency_set(truth: dict[str, Any]) -> set[str]:
    return {
        f"{item.get('kind')}:{item.get('from')}->{item.get('to')}"
        for item in truth.get("dependencies", [])
    }


def detect_unsupported_components(
    metadata: dict[str, Any], supported_step_types: set[str]
) -> list[str]:
    return sorted(
        {
            str(step.get("type"))
            for step in metadata.get("steps", [])
            if str(step.get("type") or "").lower() not in supported_step_types
        }
    )


def _metric_values(metadata: dict[str, Any], unsupported: list[str]) -> dict[str, set[str]]:
    return {
        "steps": _as_set([item.get("name") for item in metadata.get("steps", []) if item.get("name")]),
        "sources": _as_set([item.get("name") for item in metadata.get("sources", []) if item.get("name")]),
        "targets": _as_set([item.get("name") for item in metadata.get("targets", []) if item.get("name")]),
        "dependencies": _dependency_set(metadata),
        "sql": _as_set([item.get("statement") for item in metadata.get("sql", []) if item.get("statement")]),
        "tables": _as_set([item.get("name") for item in metadata.get("tables", []) if item.get("name")]),
        "parameters": _as_set([item.get("name") for item in metadata.get("parameters", []) if item.get("name")]),
        "variables": _as_set([item.get("name") for item in metadata.get("variables", []) if item.get("name")]),
        "unsupported_components": _as_set(unsupported),
    }


def _truth_values(truth: dict[str, Any]) -> dict[str, set[str]]:
    return {
        "steps": _as_set(truth.get("steps", [])),
        "sources": _as_set(truth.get("sources", [])),
        "targets": _as_set(truth.get("targets", [])),
        "dependencies": _expected_dependency_set(truth),
        "sql": _as_set(truth.get("sql", [])),
        "tables": _as_set(truth.get("tables", [])),
        "parameters": _as_set(truth.get("parameters", [])),
        "variables": _as_set(truth.get("variables", [])),
        "unsupported_components": _as_set(truth.get("unsupported_components", [])),
    }


def _new_counter() -> dict[str, int]:
    return {"tp": 0, "fp": 0, "fn": 0, "exact": 0, "cases": 0}


def _finish_counter(counter: dict[str, int]) -> dict[str, float | int]:
    tp, fp, fn = counter["tp"], counter["fp"], counter["fn"]
    precision = tp / (tp + fp) if tp + fp else 1.0
    recall = tp / (tp + fn) if tp + fn else 1.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {
        **counter,
        "precision": round(precision, 6),
        "recall": round(recall, 6),
        "f1": round(f1, 6),
        "exact_match_rate": round(counter["exact"] / counter["cases"], 6)
        if counter["cases"]
        else 1.0,
    }


def detect_unsupported_claims(
    ai_result: dict[str, Any], metadata: dict[str, Any]
) -> list[str]:
    """Structural hallucination detector; not a universal natural-language fact checker."""
    try:
        validate_ai_result(copy.deepcopy(ai_result), metadata)
    except Exception as exc:
        return [str(exc)]
    return []


class SyntheticEvidenceClient:
    """Deterministic semantic-contract fixture used by CI, not a model benchmark."""

    model = "deterministic"

    def __call__(self, _system_prompt: str, request_text: str) -> dict[str, Any]:
        request = json.loads(request_text)
        metadata = request["normalized_metadata"]
        pipeline = metadata.get("pipeline", {})
        sources = metadata.get("sources", [])
        targets = metadata.get("targets", [])
        dependencies = metadata.get("dependencies", [])

        source_target = []
        for source in sources:
            for target in targets:
                source_target.append(
                    {
                        "source": source.get("name"),
                        "target": target.get("name"),
                        "text": (
                            f"Parser evidence identifies {source.get('name')} as a source "
                            f"and {target.get('name')} as a target."
                        ),
                        "evidence_refs": list(
                            dict.fromkeys(
                                list(source.get("evidence_refs", []))
                                + list(target.get("evidence_refs", []))
                            )
                        ),
                    }
                )

        dependency_summary = []
        for dependency in dependencies:
            from_value = dependency.get("from_name") or dependency.get("from")
            to_value = dependency.get("to_name") or dependency.get("to")
            dependency_summary.append(
                {
                    "from": from_value,
                    "to": to_value,
                    "text": f"Parser-recorded {dependency.get('kind')} dependency.",
                    "evidence_refs": dependency.get("evidence_refs", []),
                }
            )

        return {
            "pipeline_summary": {
                "text": (
                    f"{pipeline.get('name', 'unnamed')} has "
                    f"{len(metadata.get('steps', []))} parser-recorded steps."
                ),
                "evidence_refs": pipeline.get("evidence_refs", []),
            },
            "business_logic": [
                {
                    "text": f"Step {step.get('name')} is parser-typed as {step.get('type')}.",
                    "evidence_refs": step.get("evidence_refs", []),
                }
                for step in metadata.get("steps", [])
            ],
            "sql_explanations": [
                {
                    "sql_id": item.get("id"),
                    "text": "SQL exists in deterministic parser metadata.",
                    "evidence_refs": item.get("evidence_refs", []),
                }
                for item in metadata.get("sql", [])
            ],
            "source_target_interpretation": source_target,
            "dependency_summary": dependency_summary,
            "migration_assistance": [],
            "warnings": [],
        }


def _semantic_quality(
    result: dict[str, Any], metadata: dict[str, Any]
) -> dict[str, float | int]:
    if result.get("analysis_mode") != "ai":
        return {
            "structured_output_valid": 0,
            "factual_consistency": 0,
            "grounding": 0.0,
            "completeness": 0.0,
            "semantic_usefulness_proxy": 0.0,
            "unsupported_claim_count": 1,
            "parser_truth_preserved": int(
                result.get("parser_truth_digest") == metadata_digest(metadata)
            ),
        }

    unsupported = detect_unsupported_claims(result, metadata)
    allowed_evidence = {str(item.get("id")) for item in metadata.get("evidence", [])}
    factual_items: list[dict[str, Any]] = []
    summary = result.get("pipeline_summary")
    if isinstance(summary, dict):
        factual_items.append(summary)
    for key in (
        "business_logic",
        "sql_explanations",
        "source_target_interpretation",
        "dependency_summary",
        "migration_assistance",
    ):
        factual_items.extend(item for item in result.get(key, []) if isinstance(item, dict))
    grounded = 0
    for item in factual_items:
        refs = {str(ref) for ref in item.get("evidence_refs", [])}
        if refs and refs <= allowed_evidence:
            grounded += 1
    grounding = grounded / len(factual_items) if factual_items else 1.0

    dimensions = [1.0 if isinstance(summary, dict) and summary.get("text") else 0.0]
    if metadata.get("steps"):
        dimensions.append(min(len(result.get("business_logic", [])) / len(metadata["steps"]), 1.0))
    if metadata.get("sql"):
        dimensions.append(min(len(result.get("sql_explanations", [])) / len(metadata["sql"]), 1.0))
    if metadata.get("dependencies"):
        dimensions.append(
            min(len(result.get("dependency_summary", [])) / len(metadata["dependencies"]), 1.0)
        )
    endpoints = {
        str(item.get("name"))
        for item in metadata.get("sources", []) + metadata.get("targets", [])
        if item.get("name")
    }
    if endpoints:
        covered = {
            str(item.get(field))
            for item in result.get("source_target_interpretation", [])
            for field in ("source", "target")
            if item.get(field)
        }
        dimensions.append(len(covered & endpoints) / len(endpoints))

    completeness = sum(dimensions) / len(dimensions)
    preserved = result.get("parser_truth_digest") == metadata_digest(metadata)
    factual_consistency = int(not unsupported and preserved)
    usefulness = (grounding + completeness + factual_consistency) / 3
    return {
        "structured_output_valid": 1,
        "factual_consistency": factual_consistency,
        "grounding": round(grounding, 6),
        "completeness": round(completeness, 6),
        "semantic_usefulness_proxy": round(usefulness, 6),
        "unsupported_claim_count": len(unsupported),
        "parser_truth_preserved": int(preserved),
    }


def _observations(client: Any) -> list[dict[str, Any]]:
    getter = getattr(client, "usage_observations", None)
    if not callable(getter):
        return []
    value = getter()
    return value if isinstance(value, list) else []


def _usage_for_observations(observations: list[dict[str, Any]]) -> dict[str, Any]:
    if not observations:
        return {
            "input_tokens": None,
            "output_tokens": None,
            "estimated_cost_usd": None,
            "pricing_known": False,
            "gateway_provider_attempt_count": None,
        }
    usage_values = [item.get("usage") for item in observations]
    tokens_known = all(isinstance(item, dict) for item in usage_values)
    input_tokens = (
        sum(int(item.get("prompt_tokens", 0)) for item in usage_values)
        if tokens_known else None
    )
    output_tokens = (
        sum(int(item.get("completion_tokens", 0)) for item in usage_values)
        if tokens_known else None
    )
    gateways = [item.get("gateway") for item in observations]
    pricing_known = all(
        isinstance(item, dict) and item.get("pricing_known") is True for item in gateways
    )
    cost = (
        sum(float(item.get("cost_usd", 0.0)) for item in gateways)
        if pricing_known else None
    )
    provider_attempts = (
        sum(len(item.get("attempts", [])) for item in gateways if isinstance(item, dict))
        if all(isinstance(item, dict) for item in gateways) else None
    )
    return {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "estimated_cost_usd": round(cost, 8) if cost is not None else None,
        "pricing_known": pricing_known,
        "gateway_provider_attempt_count": provider_attempts,
    }


def _aggregate_usage(records: list[dict[str, Any]]) -> dict[str, Any]:
    token_complete = all(record.get("input_tokens") is not None for record in records)
    output_complete = all(record.get("output_tokens") is not None for record in records)
    cost_complete = all(record.get("estimated_cost_usd") is not None for record in records)
    timing_complete = all(record.get("total_duration_ms") is not None for record in records)
    return {
        "pipeline_count": len(records),
        "ai_request_count": sum(int(record.get("ai_request_count", 0)) for record in records),
        "input_tokens": sum(record["input_tokens"] for record in records) if token_complete else None,
        "output_tokens": sum(record["output_tokens"] for record in records) if output_complete else None,
        "estimated_cost_usd": round(sum(record["estimated_cost_usd"] for record in records), 8)
        if cost_complete else None,
        "parser_duration_ms": round(sum(float(record["parser_duration_ms"]) for record in records), 6)
        if timing_complete else None,
        "ai_latency_ms": round(sum(float(record["ai_latency_ms"]) for record in records), 6)
        if timing_complete else None,
        "total_duration_ms": round(sum(float(record["total_duration_ms"]) for record in records), 6)
        if timing_complete else None,
        "failure_count": sum(int(record.get("failure_count", 0)) for record in records),
        "retry_count": sum(int(record.get("retry_count", 0)) for record in records),
    }


def run_evaluation(
    dataset_path: str | Path,
    *,
    ai_client: Callable[[str, str], str | dict[str, Any]] | None = None,
    provider_name: str = "synthetic-evidence-contract",
    stable: bool = False,
) -> dict[str, Any]:
    dataset_path = Path(dataset_path)
    dataset = load_dataset(dataset_path)
    supported = {str(value).lower() for value in dataset.get("supported_step_types", [])}
    parser = DeterministicETLParser()
    client = ai_client or SyntheticEvidenceClient()
    counters = {
        name: _new_counter()
        for name in (
            "steps", "sources", "targets", "dependencies", "sql", "tables",
            "parameters", "variables", "unsupported_components",
        )
    }
    case_results: list[dict[str, Any]] = []
    semantic_results: list[dict[str, Any]] = []
    usage_records: list[dict[str, Any]] = []
    expected_failures = observed_failures = unexpected_failures = exact_cases = 0
    raw_bytes_total = structured_bytes_total = repeatable = truth_preserved = valid_cases = 0

    for case in dataset["cases"]:
        artifact = (dataset_path.parent / str(case["artifact"])).resolve()
        truth = case.get("truth", {})
        expected_failure = bool(case.get("expect_parse_failure", False))
        expected_failures += int(expected_failure)
        raw_bytes_total += len(artifact.read_bytes())
        parser_started = perf_counter()
        try:
            metadata = parser.parse(artifact)
            parse_error = None
        except Exception as exc:
            metadata = None
            parse_error = f"{type(exc).__name__}: {exc}"
        parser_duration = (perf_counter() - parser_started) * 1000
        observed_failures += int(metadata is None)

        if expected_failure:
            passed = metadata is None
            exact_cases += int(passed)
            if metadata is not None:
                unexpected_failures += 1
            case_results.append({
                "id": case["id"], "category": case.get("category"),
                "expected_parse_failure": True, "parse_failed": metadata is None,
                "exact_match": passed, "error": parse_error,
                "parser_duration_ms": None if stable else round(parser_duration, 6),
            })
            continue

        if metadata is None:
            unexpected_failures += 1
            case_results.append({
                "id": case["id"], "category": case.get("category"),
                "expected_parse_failure": False, "parse_failed": True,
                "exact_match": False, "error": parse_error,
                "parser_duration_ms": None if stable else round(parser_duration, 6),
            })
            continue

        valid_cases += 1
        unsupported = detect_unsupported_components(metadata, supported)
        actual = _metric_values(metadata, unsupported)
        expected = _truth_values(truth)
        dimension_exact: dict[str, bool] = {}
        for name, counter in counters.items():
            actual_set, expected_set = actual[name], expected[name]
            counter["tp"] += len(actual_set & expected_set)
            counter["fp"] += len(actual_set - expected_set)
            counter["fn"] += len(expected_set - actual_set)
            counter["cases"] += 1
            is_exact = actual_set == expected_set
            counter["exact"] += int(is_exact)
            dimension_exact[name] = is_exact
        case_exact = all(dimension_exact.values())
        exact_cases += int(case_exact)

        repeated = parser.parse(artifact)
        repeatable += int(metadata_digest(repeated) == metadata_digest(metadata))
        structured_bytes_total += len(
            json.dumps(build_ai_context(metadata), ensure_ascii=False, sort_keys=True,
                       separators=(",", ":")).encode("utf-8")
        )

        before_observations = len(_observations(client))
        ai_started = perf_counter()
        analysis = SemanticAnalyzer(
            client, provider_name=provider_name, max_validation_attempts=2
        ).analyze(metadata)
        ai_latency = (perf_counter() - ai_started) * 1000
        observations = _observations(client)[before_observations:]
        quality = _semantic_quality(analysis, metadata)
        semantic_results.append({"case_id": case["id"], **quality})
        truth_preserved += int(quality["parser_truth_preserved"])
        usage = _usage_for_observations(observations)
        provenance = analysis.get("provenance", {})
        gateway_meta = observations[-1].get("gateway", {}) if observations else {}
        provider = (
            str(gateway_meta.get("provider"))
            if isinstance(gateway_meta, dict) and gateway_meta.get("provider")
            else provider_name
        )
        model = (
            str(gateway_meta.get("model"))
            if isinstance(gateway_meta, dict) and gateway_meta.get("model")
            else str(getattr(client, "model", "unknown"))
        )
        usage_records.append({
            "case_id": case["id"], "provider": provider, "model": model,
            "ai_request_count": int(provenance.get("ai_attempts", 1)), **usage,
            "parser_duration_ms": None if stable else round(parser_duration, 6),
            "ai_latency_ms": None if stable else round(ai_latency, 6),
            "total_duration_ms": None if stable else round(parser_duration + ai_latency, 6),
            "failure_count": int(analysis.get("analysis_mode") != "ai"),
            "retry_count": int(provenance.get("retry_count", 0)),
        })
        case_results.append({
            "id": case["id"], "category": case.get("category"),
            "expected_parse_failure": False, "parse_failed": False,
            "exact_match": case_exact, "dimension_exact": dimension_exact,
            "parser_duration_ms": None if stable else round(parser_duration, 6),
            "ai": {"analysis_mode": analysis.get("analysis_mode"), **quality},
        })

    parser_metrics = {name: _finish_counter(counter) for name, counter in counters.items()}
    semantic_count = len(semantic_results)

    def average(name: str) -> float:
        return round(sum(float(item[name]) for item in semantic_results) / semantic_count, 6) if semantic_count else 0.0

    semantic_summary = {
        "evaluated_cases": semantic_count,
        "structured_output_validity": average("structured_output_valid"),
        "factual_consistency": average("factual_consistency"),
        "grounding": average("grounding"),
        "completeness": average("completeness"),
        "semantic_usefulness_proxy": average("semantic_usefulness_proxy"),
        "unsupported_claim_count": sum(int(item["unsupported_claim_count"]) for item in semantic_results),
        "parser_truth_preservation_rate": average("parser_truth_preserved"),
    }
    batch_usage = _aggregate_usage(usage_records)
    grouped: dict[str, list[dict[str, Any]]] = {}
    for record in usage_records:
        grouped.setdefault(f"{record['provider']}::{record['model']}", []).append(record)
    provider_model = {key: _aggregate_usage(records) for key, records in sorted(grouped.items())}
    denominator = max(1, len(usage_records))
    projected_requests = round(batch_usage["ai_request_count"] / denominator * 243)
    projected_cost = (
        round(batch_usage["estimated_cost_usd"] / denominator * 243, 8)
        if batch_usage["estimated_cost_usd"] is not None else None
    )

    return {
        "schema_version": "1.0",
        "scope": "synthetic-generic-etl-evaluation",
        "stable_mode": stable,
        "dataset": {
            "path": dataset_path.as_posix(), "case_count": len(dataset["cases"]),
            "valid_case_count": valid_cases, "expected_parse_failure_count": expected_failures,
        },
        "parser": {
            "observed_parsing_failure_rate": round(observed_failures / len(dataset["cases"]), 6),
            "unexpected_parsing_failure_rate": round(
                unexpected_failures / max(1, len(dataset["cases"]) - expected_failures), 6
            ),
            "structural_case_exact_match_rate": round(exact_cases / len(dataset["cases"]), 6),
            "metrics": parser_metrics,
        },
        "semantic": semantic_summary,
        "usage": {
            "per_pipeline": usage_records, "batch": batch_usage,
            "per_provider_model": provider_model,
            "projection_243": {
                "pipeline_count": 243, "ai_request_count": projected_requests,
                "estimated_cost_usd": projected_cost,
                "basis": "linear projection from this evaluation run",
                "cost_status": "measured" if projected_cost is not None
                else "unavailable-without-gateway-pricing-evidence",
            },
        },
        "ablation": {
            "parser_only_structural_exact_match_rate": round(exact_cases / len(dataset["cases"]), 6),
            "parser_plus_ai_truth_preservation_rate": round(truth_preserved / max(1, semantic_count), 6),
            "deterministic_repeatability_rate": round(repeatable / max(1, valid_cases), 6),
            "raw_artifact_input_bytes": raw_bytes_total,
            "structured_ai_context_bytes": structured_bytes_total,
            "structured_to_raw_byte_ratio": round(structured_bytes_total / max(1, raw_bytes_total), 6),
            "raw_to_llm_provider_benchmark_performed": False,
            "raw_to_llm_note": (
                "CI does not send raw ETL directly to a provider. Input-surface size is measured, "
                "but provider token/cost claims require an explicit live run."
            ),
        },
        "cases": case_results,
        "notes": [
            "All artifacts and ground truth are synthetic/generic.",
            "A perfect score on this small regression corpus is not a production accuracy claim.",
            "Semantic usefulness is an explicit deterministic proxy, not a human-judged model-quality score.",
            "Token and cost fields remain null when the Multi-LLM AI Gateway does not provide usage/pricing evidence.",
            "Provider timeout/rate-limit routing and fallback remain the Multi-LLM AI Gateway responsibility.",
        ],
    }


def render_markdown(report: dict[str, Any]) -> str:
    parser, semantic = report["parser"], report["semantic"]
    usage, ablation = report["usage"]["batch"], report["ablation"]
    return "\n".join([
        "# ETL AI Evaluation Report / ETL AI 評測報告", "",
        "## 繁體中文", "",
        f"- Synthetic cases：**{report['dataset']['case_count']}**",
        f"- Structural case exact match：**{parser['structural_case_exact_match_rate']:.1%}**",
        f"- Unexpected parsing failure rate：**{parser['unexpected_parsing_failure_rate']:.1%}**",
        f"- AI structured output validity：**{semantic['structured_output_validity']:.1%}**",
        f"- Unsupported structured claims：**{semantic['unsupported_claim_count']}**",
        f"- Parser truth preservation：**{semantic['parser_truth_preservation_rate']:.1%}**",
        f"- Deterministic repeatability：**{ablation['deterministic_repeatability_rate']:.1%}**", "",
        "### Usage / Cost / Latency", "",
        f"- AI requests：{usage['ai_request_count']}",
        f"- Input tokens：{usage['input_tokens']}",
        f"- Output tokens：{usage['output_tokens']}",
        f"- Estimated cost USD：{usage['estimated_cost_usd']}",
        f"- Parser duration ms：{usage['parser_duration_ms']}",
        f"- AI latency ms：{usage['ai_latency_ms']}",
        f"- Failures / retries：{usage['failure_count']} / {usage['retry_count']}", "",
        "> 這是 synthetic regression corpus，不是真實客戶或 production benchmark。"
        " 若沒有 Gateway usage/pricing evidence，token/cost 會保留為 null，而不是估造數字。", "",
        "## English", "",
        "This report is generated from repository-owned synthetic ETL cases and deterministic ground truth.",
        "Provider/model token, cost, and latency evidence is only claimed when actually observed from the Multi-LLM AI Gateway contract.", "",
        "### Capability Boundary", "",
        "- Deterministic code owns structural truth and exact-match evaluation.",
        "- AI owns optional semantic explanation only.",
        "- Structured unsupported-claim detection is not a universal natural-language fact checker.",
        "- Gateway owns provider routing, timeout/rate-limit fallback, pricing, and budget governance.", "",
    ])


def render_html(report: dict[str, Any]) -> str:
    embedded = json.dumps(report, ensure_ascii=False).replace("</", "<\\/")
    return f"""<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>ETL AI Evaluation Evidence</title>
<style>:root{{--bg:#0b1220;--panel:#121d30;--text:#eef5ff;--muted:#9fb0c5;--line:#29405f;--accent:#69a9ff}}
*{{box-sizing:border-box}}body{{margin:0;font-family:Inter,"Noto Sans TC",system-ui;background:var(--bg);color:var(--text);line-height:1.6}}
main{{max-width:1180px;margin:auto;padding:42px 20px 70px}}.muted{{color:var(--muted)}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:12px;margin:24px 0}}
.card{{background:var(--panel);border:1px solid var(--line);border-radius:15px;padding:16px}}.big{{font-size:30px;font-weight:800}}table{{width:100%;border-collapse:collapse;background:var(--panel)}}th,td{{padding:10px 12px;border-bottom:1px solid var(--line);text-align:left}}input{{width:100%;padding:11px;background:var(--panel);color:var(--text);border:1px solid var(--line);border-radius:10px;margin:12px 0}}.warn{{border-left:4px solid #f5c55d;padding:12px 14px;background:var(--panel);margin:20px 0}}</style></head>
<body><main><div class="muted">P2 · Evidence over feature count</div><h1>ETL AI Evaluation</h1>
<div id="cards" class="grid"></div><div class="warn"><b>Scope warning:</b> a perfect score on this small synthetic regression corpus is not a production accuracy claim. Token/cost remain unavailable unless the Gateway actually reports usage and pricing evidence.</div>
<h2>Evaluation Cases</h2><input id="q" placeholder="Filter case id or category"><table><thead><tr><th>Case</th><th>Category</th><th>Parse</th><th>Structural Exact</th><th>AI Mode</th></tr></thead><tbody id="rows"></tbody></table>
<script>const report={embedded};const pct=v=>(Number(v)*100).toFixed(1)+'%';const cards=[['Dataset cases',report.dataset.case_count],['Parser exact',pct(report.parser.structural_case_exact_match_rate)],['Unexpected parse fail',pct(report.parser.unexpected_parsing_failure_rate)],['AI contract valid',pct(report.semantic.structured_output_validity)],['Unsupported claims',report.semantic.unsupported_claim_count],['Truth preserved',pct(report.semantic.parser_truth_preservation_rate)],['243 cost',report.usage.projection_243.estimated_cost_usd??'unavailable']];document.getElementById('cards').innerHTML=cards.map(([k,v])=>'<div class="card"><div class="big">'+v+'</div><div class="muted">'+k+'</div></div>').join('');function draw(){{const q=document.getElementById('q').value.toLowerCase();document.getElementById('rows').innerHTML=report.cases.filter(c=>(c.id+' '+(c.category||'')).toLowerCase().includes(q)).map(c=>'<tr><td>'+c.id+'</td><td>'+(c.category||'')+'</td><td>'+(c.parse_failed?(c.expected_parse_failure?'expected failure':'FAILED'):'ok')+'</td><td>'+(c.exact_match?'yes':'no')+'</td><td>'+(c.ai?.analysis_mode||'n/a')+'</td></tr>').join('')}}document.getElementById('q').addEventListener('input',draw);draw();</script>
</main></body></html>"""


def write_report(report: dict[str, Any], output_dir: str | Path) -> dict[str, str]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    paths = {
        "json": output / "etl-ai-evaluation.json",
        "markdown": output / "etl-ai-evaluation.md",
        "html": output / "etl-ai-evaluation.html",
    }
    paths["json"].write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    paths["markdown"].write_text(render_markdown(report) + "\n", encoding="utf-8")
    paths["html"].write_text(render_html(report) + "\n", encoding="utf-8")
    return {key: value.as_posix() for key, value in paths.items()}
