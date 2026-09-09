# ETL Lifecycle & Deployment Governance / ETL 生命週期與部署治理

## 繁體中文

### Platform lifecycle

`Design → Develop → Validate → Lifecycle Smoke → Observability Smoke → Security Scan → Build → TEST → Approve → Promote → PROD → Observe → Audit`

### Execution governance

每次 execution 仍以：

- `run_id`
- `attempt_number`
- `correlation_id`

維持 retry 與 target-data traceability。

Retry 是新 attempt，不覆蓋失敗歷史。

### Artifact governance

v0.4 規則維持：

**Build once. Promote the same artifact. Never rebuild for PROD.**

### Observability governance

v0.5 增加：

- monitoring queries 只能經 read-only observability surface
- Grafana 不直接連 raw audit table
- SLO / alert rule 必須納入 version control
- CI 必須證明 Prometheus rule 可載入
- CI 必須證明關鍵 alert 可實際 firing
- notification credential 不可 commit
- production receiver / escalation 應由部署環境管理

### SLO baseline

`ETL completed-attempt success ratio >= 99%`

此為 portfolio baseline，不代表所有 production pipeline 使用同一 threshold。

正式環境應按 business criticality 調整：

- SLO target
- burn-rate window
- maintenance window
- escalation
- retention

### Release gate

Tag / Release 仍只在相同 main commit 的：

- CI success
- Security success

後建立。

v0.5 CI 已包含 lifecycle、observability、immutable supply-chain 三層 runtime smoke。

## English

v0.5 adds operational governance to the existing execution and artifact governance model.

Monitoring queries use a read-only observability surface; Grafana does not query raw audit data directly. SLO and alert rules are version controlled and CI must prove both rule loading and real alert evaluation.

The 99% completed-attempt success SLO is a portfolio baseline. Production thresholds, burn-rate windows, escalation, maintenance windows, and retention should be governed by workload criticality.

Release gating still requires CI and Security success on the same main commit.
