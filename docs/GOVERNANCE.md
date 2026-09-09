# ETL Lifecycle & Deployment Governance / ETL 生命週期與部署治理

## 繁體中文

### Platform lifecycle

Design → Parse → Normalize → Semantic Analyze → Validate → Test → Security Gate → Build → TEST → Approve → Promote → PROD → Observe → Audit

### Design-time governance

ETL Intelligence 只處理 design-time：

- deterministic parsing
- normalized metadata
- evidence / provenance
- business-logic explanation
- SQL explanation
- source-target interpretation
- dependency summary
- migration assistance

AI 不負責 runtime incident RCA。

Parser truth 可在沒有 AI 的情況下獨立使用；AI output 必須引用 parser evidence，且透過 parser_truth_digest 與原始 metadata 關聯。

### Execution governance

每次 execution 仍以 run_id、attempt_number、correlation_id 維持 retry 與 target-data traceability。Retry 是新 attempt，不覆蓋失敗歷史。

### Delivery governance

- GitHub Actions：公開 Portfolio CI。
- GitLab CI：Enterprise Delivery Reference。
- Build once。
- TEST / PROD：same registry digest。
- PROD：manual approval + serialized promotion。
- Rollback：選擇前一個已批准 digest，不 rebuild。

### Vulnerability governance

Scanner finding 必須留下 applicability / remediation decision evidence。

可接受 disposition：

- remediated
- vendor-backport
- not-applicable
- risk-accepted with approval

Artifact 有變更時必須產生新的 candidate digest 並重跑 SBOM / scan / tests / TEST。

### Observability governance

Monitoring 維持 read-only observability surface；Grafana 不直接讀 raw audit table。SLO / alert rules 進 version control，CI 必須證明 rule loading 與關鍵 alert firing。

### Portfolio responsibility boundary

- enterprise-etl-platform：ETL design-time + runtime + delivery/security lifecycle
- agentic-dataops-copilot：runtime incident reasoning / RCA
- enterprise-rag-platform：knowledge AI / grounding
- data-platform-mcp-server：tool / integration layer
- multi-llm-ai-gateway：model control plane

## English

v0.6 governs design-time ETL semantic analysis separately from runtime operations.

Parser truth is authoritative and AI output is evidence-bound. Enterprise delivery uses build-once same-digest promotion, explicit vulnerability disposition evidence, manual production approval, and rollback to previously approved immutable artifacts.

Adjacent repositories retain incident RCA, knowledge AI, integration, and model-control responsibilities.
