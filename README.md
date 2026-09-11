# Enterprise ETL Platform

**目前版本：v0.8.0**

> **互動式架構與專案總覽**  
> [GitHub Pages](https://kewinall.github.io/enterprise-etl-platform/) · [Repository HTML](docs/enterprise-etl-platform-guide.html)

這是一套 production-oriented **Enterprise Data Engineering Platform**，涵蓋 legacy ETL modernization、deterministic ETL intelligence、normalized metadata / lineage、Airflow orchestration、Apache Hop runtime、PostgreSQL audit、secure delivery、air-gapped promotion、observability、SLO 與 ETL AI evaluation。

## 專案定位

本 Repository 負責 Portfolio 中的 **ETL 與 Data Engineering Truth Layer**：

- Pentaho / legacy ETL parsing
- normalized ETL metadata contracts
- structural 與 deterministic lineage
- migration planning toward Apache Hop
- deterministic validation 與 reconciliation
- Airflow orchestration
- Apache Hop execution
- PostgreSQL run / attempt / event audit
- GitLab delivery reference implementation
- Trivy / SBOM / CVE remediation lifecycle
- immutable artifact promotion
- air-gapped deployment workflow
- Prometheus / Grafana / Alertmanager observability
- design-time ETL AI assistance 與 evidence boundaries
- parser quality、semantic grounding、usage、latency、cost evidence evaluation

本專案刻意不負責 canonical MCP protocol layer、enterprise RAG layer、DataOps incident agent 或 multi-provider model gateway。

## 架構

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

## 核心工程 Invariants

- structural truth 由 deterministic parser 產生，不交由 LLM 決定
- AI 可提供 explanation / assistance，但不可 fabricate steps、SQL、dependencies 或 lineage
- unknown / unsupported component 必須 fallback 到 manual review
- retry 產生新的 attempt，不覆蓋先前 failure evidence
- PostgreSQL 是 durable execution truth；monitoring 從 read-only views 衍生
- TEST 與 PROD 應使用同一 immutable artifact identity
- security remediation 必須透過 rebuild + rescan + promotion evidence 驗證
- MCP / RAG / DataOps / Model Gateway 只能消費 ETL truth，不可重新定義 truth

## 關鍵工程決策

| 決策 | 原因 / 效益 | Trade-off |
|---|---|---|
| Airflow 負責 orchestration，Hop 負責 data processing | scheduling / retry / context 與 ETL transformation runtime 分離 | 跨系統 operation correlation 較複雜 |
| PostgreSQL 作為 execution truth | 保存 run / attempt / event history，支援 audit、metrics 與 retry analysis | 增加 durable platform dependency |
| Build once，promote same immutable artifact | 避免 TEST / PROD rebuild drift | 需要明確 artifact verification 與 promotion lifecycle |
| Read-only audit views 提供 observability | Monitoring 與 ETL execution path 解耦 | Metrics freshness 依賴 exporter / scrape path |
| Deterministic parse 先於 AI explanation | Migration truth 可重現、可測試 | Parser / plugin coverage 必須持續維護 |
| ETL truth 與其他 AI layers 解耦 | 維持清楚的 cross-repository ownership | 需要 contract / version compatibility |
| Evidence over feature count | 品質、failure 與 cost claim 都可被驗證 | Synthetic evidence 不可過度宣稱為 production accuracy |

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

AI interpretation 維持為獨立 semantic layer，不視為 lineage 或 migration truth。

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

成功 retry 不會抹除第一次 failure 的 evidence。

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

Air-gapped delivery 透過 bundle / checksum / image-identity verification，確保 offline transport 不會破壞 provenance controls。

## ETL AI Evaluation / Production Evidence

P2 的重點不是繼續增加 model feature，而是證明 ETL AI assistance 是否 **有效、可靠、可控、可量測**。

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

目前 evaluation assets 包含 synthetic corpus，涵蓋 extraction、join、lookup、filter、aggregation、SQL-heavy definitions、multi-pipeline dependencies、invalid definitions、unsupported components 與 complex parameters。

Synthetic exact-match 僅代表 regression evidence，不宣稱為 production accuracy；如果沒有 live provider usage evidence，token / cost 保持 `null`，不以估算值取代實測。

## 可驗證 Evidence

| Claim | Repository Evidence |
|---|---|
| Retry / audit lifecycle | `scripts/etl_lifecycle_smoke.sh`, `docs/AUDIT_LIFECYCLE.md`, `postgres/init/002_v0_3_audit_lifecycle.sql` |
| Executable observability / SLO | `scripts/observability_smoke.sh`, `postgres/init/003_v0_5_observability.sql`, `monitoring/sql-exporter/etl_audit.collector.yml` |
| Immutable promotion / offline verification | `scripts/supply_chain_smoke.sh`, `scripts/promote_image.sh`, `scripts/verify_offline_bundle.sh` |
| Repository policy / regression baseline | `scripts/validate_repository.py`, `tests/test_repository.py` |
| CI / Security gates | `.github/workflows/ci.yml`, `.github/workflows/security.yml` |
| Pentaho → Hop modernization | `scripts/p1_integration_smoke.sh`, `tests/test_migration_case.py`, `etl_intelligence/migration.py` |
| Metadata / lineage authority | `etl_intelligence/metadata.py`, `schemas/etl-metadata.schema.json`, `docs/METADATA_LINEAGE.md` |
| Enterprise AI integration boundary | `etl_intelligence/gateway.py`, `docs/PORTFOLIO_INTEGRATION.md` |
| ETL AI evaluation | `evaluation/dataset.json`, `etl_intelligence/evaluation.py`, `tests/test_p2_evaluation.py`, `reports/baseline/` |

## 快速驗證

依 deployment 或 evidence scenario 使用 Repository 中的 Compose、smoke-test 與 evaluation scripts。主要 executable entry points：

```bash
scripts/etl_lifecycle_smoke.sh
scripts/observability_smoke.sh
scripts/supply_chain_smoke.sh
scripts/p1_integration_smoke.sh
scripts/evaluate_etl_ai.py
```

## 工程文件

主要工程參考文件：

- `docs/ETL_INTELLIGENCE.md`
- `docs/PENTAHO_TO_HOP_MIGRATION.md`
- `docs/METADATA_LINEAGE.md`
- `docs/PORTFOLIO_INTEGRATION.md`
- `docs/ETL_AI_EVALUATION.md`
- `docs/GITLAB_CICD.md`
- `docs/ENVIRONMENT_PROMOTION.md`
- `docs/VULNERABILITY_MANAGEMENT.md`
- `docs/AUDIT_LIFECYCLE.md`

## Portfolio 責任邊界

- **Enterprise ETL Platform**：ETL metadata producer、modernization truth、runtime lifecycle、delivery evidence
- **Data Platform MCP Server**：governed read-only access to ETL / platform capabilities
- **Enterprise RAG Platform**：enterprise knowledge retrieval 與 grounding
- **Agentic DataOps Copilot**：runtime incident reasoning 與 governed remediation
- **Multi-LLM AI Gateway**：model routing、provider resilience、cost / policy governance

## 授權

MIT
