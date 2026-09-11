# Enterprise ETL Platform

**Current release: v0.8.0**

> **Interactive architecture & project overview**  
> [Live GitHub Pages](https://kewinall.github.io/enterprise-etl-platform/) · [Repository HTML](docs/enterprise-etl-platform-guide.html)

Production-oriented **Enterprise Data Engineering Platform** covering legacy ETL modernization, deterministic ETL intelligence, normalized metadata/lineage, Airflow orchestration, Apache Hop runtime, PostgreSQL audit, secure delivery, air-gapped promotion, observability, SLOs, and ETL AI evaluation.

## Engineering Scope

This repository owns the portfolio's **ETL and data-engineering truth layer**:

- Pentaho / legacy ETL parsing
- normalized ETL metadata contracts
- structural and deterministic lineage
- migration planning toward Apache Hop
- deterministic validation and reconciliation
- Airflow orchestration
- Apache Hop execution
- PostgreSQL run / attempt / event audit
- GitLab delivery reference implementation
- Trivy / SBOM / CVE remediation lifecycle
- immutable artifact promotion
- air-gapped deployment workflow
- Prometheus / Grafana / Alertmanager observability
- design-time ETL AI assistance with evidence boundaries
- evaluation of parser quality, semantic grounding, usage, latency and cost evidence

It intentionally does not own the canonical MCP protocol layer, enterprise RAG layer, DataOps incident agent, or multi-provider model gateway.

## Architecture

```text
Legacy Pentaho / ETL Definitions
            |
            v
   Deterministic Parser
            |
            v
   Normalized Metadata
      /            \
     v              v
Migration Planner  Lineage Graph
     |              |
     v              +--> MCP / RAG / DataOps consumers
 Apache Hop Target
     |
     v
Deterministic Validation
     |
     v
Representative Reconciliation

Runtime path:
Airflow -> Apache Hop -> PostgreSQL Audit -> Metrics / Alerts / Grafana

Delivery path:
Build once -> Scan / SBOM -> TEST -> Approval -> Same immutable artifact -> PROD
```

## Core Engineering Invariants

- structural truth is produced deterministically, not by an LLM
- AI may explain or assist, but must not fabricate steps, SQL, dependencies, or lineage
- unknown or unsupported components fall back to manual review
- retry creates a new attempt instead of overwriting prior failure evidence
- PostgreSQL is the durable execution truth; monitoring is derived from read-only views
- TEST and PROD should consume the same immutable artifact identity
- security remediation is verified by rebuild + rescan + promotion evidence
- MCP / RAG / DataOps / Model Gateway integrations consume ETL truth but do not redefine it

## Key Engineering Decisions

| Decision | Rationale | Trade-off |
|---|---|---|
| Airflow for orchestration, Hop for data processing | Separates scheduling/retry/context from ETL transformation runtime | More cross-system operational correlation |
| PostgreSQL as execution truth | Preserves run/attempt/event history for audit, metrics and retry analysis | Adds a durable platform dependency |
| Build once, promote same immutable artifact | Prevents TEST/PROD rebuild drift | Requires explicit artifact verification and promotion lifecycle |
| Read-only audit views for observability | Monitoring stays decoupled from ETL execution path | Metric freshness depends on exporter/scrape path |
| Deterministic parse before AI explanation | Makes migration truth reproducible and testable | Parser/plugin coverage must be maintained |
| ETL truth decoupled from other AI layers | Preserves clear cross-repository ownership | Requires contract/version compatibility |
| Evidence over feature count | Makes quality, failure and cost claims inspectable | Synthetic evidence must not be overstated as production accuracy |

## Legacy ETL Modernization

```text
Pentaho KTR / KJB
      |
      v
Deterministic Parser
      |
      v
Normalized Metadata
      |
      +--> structural lineage
      +--> inferred-deterministic lineage
      +--> migration plan
      +--> capability boundary
      |
      v
Apache Hop Target
      |
      v
Validation / Reconciliation
```

AI interpretation remains a separate semantic layer and is not treated as lineage or migration truth.

## Runtime Lifecycle

```text
Airflow DAG
    |
    v
Apache Hop execution
    |
    +--> run
    +--> attempt 1: failed
    +--> attempt 2: succeeded
    |
    v
PostgreSQL audit truth
    |
    +--> SQL Exporter
    +--> Prometheus
    +--> Alertmanager
    +--> Grafana
```

A successful retry does not erase the evidence of the original failure.

## Secure Delivery

```text
Merge / Release
      |
      v
Validate / Test
      |
      v
Build Once
      |
      +--> Trivy
      +--> Secret Scan
      +--> SBOM
      +--> CVE Gate
      |
      v
TEST same digest
      |
   Approval
      |
      v
PROD same digest
```

Air-gapped delivery uses bundle/checksum/image-identity verification so offline transport does not remove provenance controls.

## ETL AI Evaluation / Production Evidence

P2 focuses on proving whether ETL AI assistance is **effective, reliable, controlled and measurable** rather than adding more model features.

```text
Synthetic Ground Truth
        |
        v
Deterministic Parser ------> Precision / Recall / Exact Match
        |
        v
Normalized Evidence
        |
        v
Semantic Analyzer ----------> Grounding / Unsupported Claims
        |
        +--------------------> Gateway Usage / Cost / Latency
        |
        v
JSON / Markdown / Interactive HTML
```

Current evaluation assets include a synthetic corpus covering extraction, joins, lookup, filters, aggregation, SQL-heavy definitions, multi-pipeline dependencies, invalid definitions, unsupported components, and complex parameters.

Synthetic exact-match results are regression evidence only; they are not presented as production accuracy. Token/cost remain null when live provider usage evidence is unavailable.

## Production Evidence

| Claim | Repository Evidence |
|---|---|
| Retry / audit lifecycle | `scripts/etl_lifecycle_smoke.sh`, `docs/AUDIT_LIFECYCLE.md`, `postgres/init/002_v0_3_audit_lifecycle.sql` |
| Executable observability / SLO | `scripts/observability_smoke.sh`, `postgres/init/003_v0_5_observability.sql`, `monitoring/sql-exporter/etl_audit.collector.yml` |
| Immutable promotion / offline verification | `scripts/supply_chain_smoke.sh`, `scripts/promote_image.sh`, `scripts/verify_offline_bundle.sh` |
| Repository policy / regression baseline | `scripts/validate_repository.py`, `tests/test_repository.py` |
| CI / Security gates | `.github/workflows/ci.yml`, `.github/workflows/security.yml` |
| Pentaho -> Hop modernization | `scripts/p1_integration_smoke.sh`, `tests/test_migration_case.py`, `etl_intelligence/migration.py` |
| Metadata / lineage authority | `etl_intelligence/metadata.py`, `schemas/etl-metadata.schema.json`, `docs/METADATA_LINEAGE.md` |
| Enterprise AI integration boundary | `etl_intelligence/gateway.py`, `docs/PORTFOLIO_INTEGRATION.md` |
| ETL AI evaluation | `evaluation/dataset.json`, `etl_intelligence/evaluation.py`, `tests/test_p2_evaluation.py`, `reports/baseline/` |

## Quick Start / Validation

Use the repository's Compose, smoke-test and evaluation scripts according to the relevant deployment or evidence scenario. Key executable entry points include:

```bash
scripts/etl_lifecycle_smoke.sh
scripts/observability_smoke.sh
scripts/supply_chain_smoke.sh
scripts/p1_integration_smoke.sh
scripts/evaluate_etl_ai.py
```

## Documentation

Key engineering references:

- `docs/ETL_INTELLIGENCE.md`
- `docs/PENTAHO_TO_HOP_MIGRATION.md`
- `docs/METADATA_LINEAGE.md`
- `docs/PORTFOLIO_INTEGRATION.md`
- `docs/ETL_AI_EVALUATION.md`
- `docs/GITLAB_CICD.md`
- `docs/ENVIRONMENT_PROMOTION.md`
- `docs/VULNERABILITY_MANAGEMENT.md`
- `docs/AUDIT_LIFECYCLE.md`

## Portfolio Boundary

- **Enterprise ETL Platform:** ETL metadata producer, modernization truth, runtime lifecycle and delivery evidence
- **Data Platform MCP Server:** governed read-only access to ETL/platform capabilities
- **Enterprise RAG Platform:** enterprise knowledge retrieval and grounding
- **Agentic DataOps Copilot:** runtime incident reasoning and governed remediation
- **Multi-LLM AI Gateway:** model routing, provider resilience and cost/policy governance

## License

MIT
