# ETL Lifecycle & Deployment Governance / ETL 生命週期與部署治理

## 繁體中文

### Platform lifecycle

Understand → Parse → Normalize → Analyze → Modernize → Validate → Execute → Observe → Govern

### Modernization governance

Legacy ETL 不直接交給 AI 黑箱轉換。

1. source artifact 先由 deterministic parser 產生 metadata + evidence + SHA；
2. compatibility planner 對元件做 explicit disposition；
3. manual-review / manual-required 不得被 AI 自動升級成 direct；
4. target Hop design 必須通過 deterministic validation；
5. representative data reconciliation 與 human review 才能進 production delivery。

### Metadata / lineage governance

- structural lineage：explicit artifact fact。
- inferred-deterministic lineage：必須標示 derivation。
- AI interpretation：只在 semantic result，不能寫回 deterministic lineage。
- column-level lineage 無法可靠解析時必須聲明 capability boundary。

### AI governance

AI 只處理 design-time explanation / recommendation。

- context 僅來自 normalized metadata；
- credential / variable value 不送模型；
- SQL literal redaction；
- result 必須 evidence-bound；
- invalid output fallback；
- preferred model path 經 Multi-LLM AI Gateway；
- AI 不負責 runtime Incident RCA，也不作 migration correctness gate。

### MCP / RAG / DataOps governance

ETL repo 是 metadata producer。Data Platform MCP Server 是 controlled read-only access layer，不重新解析 ETL artifact。

RAG 可 ingest ETL docs / generated descriptions / runbooks，但 knowledge answer 不修改 parser truth。

DataOps Copilot 可透過 MCP 取得 pipeline metadata / dependency / lineage / execution context，用於 runtime evidence correlation；RCA ownership 仍在 DataOps repo。

### Execution governance

每次 execution 以 run_id、attempt_number、correlation_id 維持 retry 與 target-data traceability。Retry 是新 attempt，不覆蓋失敗歷史。

### Delivery / vulnerability governance

- GitHub Actions：公開 Portfolio CI。
- GitLab CI：Enterprise Delivery Reference。
- Build once，TEST / PROD same registry digest。
- PROD manual approval + serialized promotion。
- vulnerability finding 必須有 applicability / remediation evidence。
- artifact 改變就重跑 SBOM / scan / tests / TEST。
- rollback 選擇前一個已批准 digest，不 rebuild。

### Production failure / recovery

| Scenario | Governance response |
|---|---|
| unsupported migration component | fail to manual review; do not auto-convert |
| parser / target mismatch | migration validation fail |
| AI unavailable or hallucinated | fallback; parser truth preserved |
| MCP/RAG/Gateway outage | ETL truth/runtime remains independent |
| audit DB outage | execution truth cannot be confirmed; recover before claiming success |
| vulnerability gate fail | no promotion |
| digest mismatch | fail closed |

## English

v0.7 governs legacy modernization as a deterministic evidence pipeline with AI as an advisory semantic layer.

Structural and inferred lineage are explicitly classified, migration correctness does not depend on AI, and adjacent repositories retain MCP access, knowledge retrieval, incident reasoning, and model-control responsibilities.

Runtime, delivery, vulnerability, same-digest promotion, audit, and observability governance remain in force.
