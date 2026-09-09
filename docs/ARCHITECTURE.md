# Architecture / 架構

## 繁體中文

### v0.6 整體架構

~~~text
                     DESIGN-TIME
Legacy ETL / Hop
       |
       v
Deterministic Parser
       |
       v
Normalized Metadata + Evidence + Source SHA
       |
       +--> deterministic fallback
       |
       v
Sensitive Context Boundary
       |
       v
AI Semantic Analyzer
       |
       v
ETL Intelligence
(summary / logic / SQL / source-target / dependency / migration)

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
Validation + Unit + Intelligence Smoke
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

### Structural truth vs semantic commentary

| Layer | Authority | May infer? |
|---|---|---|
| Deterministic parser | ETL structure | No |
| Normalized metadata | Canonical extracted facts | No |
| AI semantic analyzer | Explanation only | Yes, but only within evidence |
| Runtime audit | Execution truth | No |
| Observability | Derived operational metrics | No structural authority |

AI result 與 parser metadata 是兩個獨立 artifact。AI result 透過 parser_truth_digest 指向其依據，但不能修改原始 metadata。

### Production failure & recovery

| Failure | Behavior | Recovery |
|---|---|---|
| AI unavailable | deterministic metadata 仍產生 | 使用 fallback summary；稍後可重新做 semantic analysis |
| AI hallucinated evidence / node | output validator 拒絕 | fallback；不污染 parser truth |
| Sensitive config exists in source | AI context 移除 connection config、SQL literals redaction | 修正 source secret handling；保留 parser evidence |
| CVE scan blocks | candidate 不得 promotion | applicability analysis → remediate/rebuild → SBOM/rescan |
| TEST/PROD digest mismatch | promotion fail closed | 回到已驗證 candidate digest，不 rebuild PROD |
| Monitoring unavailable | PostgreSQL execution truth 保留 | 恢復 exporter/Prometheus/Grafana 後重新 scrape |
| Offline bundle verification fail | 不部署 | 使用 trusted key/checksum 重新驗證或重新交付 |

### Portfolio responsibility boundary

- enterprise-etl-platform：Data Engineering runtime + design-time ETL intelligence + delivery/security lifecycle
- agentic-dataops-copilot：runtime incident reasoning / RCA / governed operations
- enterprise-rag-platform：knowledge retrieval / grounding / knowledge governance
- data-platform-mcp-server：tool / integration protocol layer
- multi-llm-ai-gateway：model routing / policy / budget / control plane

因此 v0.6 的 AI 能力只服務 ETL design-time，不變成通用 Agent、RAG、MCP 或 Model Gateway。

## English

v0.6 adds a design-time intelligence plane and an enterprise delivery-security plane without changing the repository boundary.

The deterministic parser owns ETL structural truth. AI receives only normalized filtered metadata and produces separately validated semantic commentary. Runtime execution truth remains in PostgreSQL audit data.

Delivery builds one immutable candidate and promotes the same registry digest through TEST and PROD after security, SBOM, vulnerability, test, and approval gates.

Adjacent portfolio repositories retain runtime RCA, knowledge AI, integration protocol, and model-control responsibilities.
