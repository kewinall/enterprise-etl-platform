# Architecture / 架構

## 繁體中文

### v0.7 整體架構

~~~text
                         DESIGN / MODERNIZATION
Legacy Pentaho KTR/KJB / Apache Hop
              |
              v
      Deterministic Parser
              |
              v
   Normalized Metadata v1.1
 Pipeline / Step / SQL / Table / Column /
 Dependency / Parameter / Variable / Evidence
              |
       +------+-------------------+
       |                          |
       v                          v
Migration Planner            Lineage Model
       |                 structural / inferred
       v                          |
Apache Hop Target                 +--> JSON contract
       |                                   |
       v                                   v
Deterministic Validator            Data Platform MCP Server
       |                                   |
       v                              DataOps Copilot
Representative data
reconciliation

Optional semantic path:
Normalized filtered metadata
       |
       v
Semantic Analyzer
       |
       v
Multi-LLM AI Gateway
       |
OpenAI / Anthropic / Gemini / Local

Knowledge path:
ETL docs / generated descriptions / runbooks
       |
       v
Enterprise RAG Platform

                         RUNTIME
Airflow --> Packaged Apache Hop --> PostgreSQL Audit + Data
                                      |
                                      v
                               read-only metrics
                                      |
                          SQL Exporter --> Prometheus
                                           |      |
                                      Alertmanager Grafana

                         DELIVERY
Source / MR
   |
Validation + Unit + P1 Migration/Lineage Smoke
   |
Build Candidate ONCE
   |
Trivy + Secret + SBOM + CVE Applicability Gate
   |
TEST same registry digest
   |
Approval
   |
PROD same registry digest
   |
Audit Evidence / Air-Gapped Bundle
~~~

### Authority model

| Layer | Authority | May infer? |
|---|---|---|
| Deterministic parser | artifact structure | No probabilistic inference |
| Normalized metadata | canonical extracted facts | No |
| Structural lineage | explicit hops/read-write/workflow references | No |
| Inferred-deterministic lineage | conservative graph/SQL derivation | Yes, but explicitly labeled inferred |
| Migration validator | migration pass/fail evidence | deterministic only |
| AI semantic analyzer | explanation / recommendation | Yes, commentary only |
| MCP Server | controlled access to ETL truth | No new ETL truth |
| Runtime audit | execution truth | No |
| Observability | derived runtime metrics | No structural authority |

AI result 與 parser metadata 是兩個獨立 artifact。AI 不得新增 structural lineage，不得把 interpretation 寫回 deterministic truth。

### Failure / recovery

| Failure | Behavior | Recovery |
|---|---|---|
| Unsupported Pentaho/plugin component | migration disposition = manual-required / manual-review | plugin-specific parser + fixture + regression test 後才提高 automation |
| SQL / variable semantics uncertain | 不宣稱 automatic equivalence | preserve source SQL, explicit review, representative reconciliation |
| Column lineage cannot be proven | capability boundary 明確標示 | dialect AST + catalog expansion + plugin parser 後再提升 |
| AI unavailable / invalid output | deterministic metadata / migration 仍可工作 | fallback；稍後重跑 semantic analysis |
| AI hallucinated edge | validator / evidence contract 拒絕 | 不污染 lineage truth |
| MCP unavailable | ETL metadata producer 仍保有 truth artifact | 恢復 access layer，不重建 parser truth |
| RAG unavailable | modernization/runtime 不受影響 | 恢復 knowledge layer |
| CVE scan blocks | candidate 不得 promotion | applicability → remediation → rebuild → rescan |
| TEST/PROD digest mismatch | promotion fail closed | 使用已驗證 digest，不 rebuild PROD |

### Cross-repository responsibility boundary

- **enterprise-etl-platform**：Legacy ETL parser、normalized metadata、migration analysis、lineage truth、runtime/delivery。
- **data-platform-mcp-server**：MCP protocol、read-only tool contract、auth/scope/tenant/audit；不重新解析 Pentaho/Hop。
- **enterprise-rag-platform**：ETL 文件與描述的 knowledge ingestion / retrieval / grounding。
- **agentic-dataops-copilot**：runtime incident evidence correlation / RCA / governed operations。
- **multi-llm-ai-gateway**：LLM routing、fallback、provider abstraction、cost/policy/auth。

## English

v0.7 extends the platform into a legacy-modernization architecture while preserving deterministic authority boundaries.

Pentaho and Hop artifacts are parsed into normalized metadata v1.1. Structural lineage is separated from deterministic inference and AI interpretation. Migration pass/fail remains deterministic and is backed by parser evidence, SQL/table reconciliation, workflow dependency preservation, representative data checks, and human review.

The Data Platform MCP Server exposes this ETL truth through governed read-only tools; RAG consumes documentation/knowledge; DataOps consumes evidence for runtime reasoning; the Multi-LLM AI Gateway owns model routing and provider governance.
