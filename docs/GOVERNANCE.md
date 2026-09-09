# ETL Lifecycle & Deployment Governance / ETL 生命週期與部署治理

## 繁體中文

### Lifecycle

`Design → Develop → Validate → Lifecycle Smoke → Security Scan → Package → TEST → Approve → Promote → PROD → Observe → Audit`

v0.3 的 governance 不只看 deployment version，也要求每次 ETL execution 可回溯到：

- `run_id`
- `attempt_number`
- `correlation_id`
- final status
- records written
- error summary
- target rows

### Retry governance

每個 retry 必須建立新的 attempt，不覆蓋失敗歷史：

```text
run_id = X / attempt 1 / FAILED
run_id = X / attempt 2 / SUCCESS
```

這可區分「第一次失敗後成功」與「第一次就成功」。

### Status transition

允許的主流程：

- `RUNNING → SUCCESS`
- `RUNNING → FAILED`

Retry 是新的 execution row，不是把 `FAILED` 改回 `RUNNING`。

PostgreSQL trigger 會建立 append-only lifecycle event，並在 final state 寫入 `finished_at`。

### Data traceability

`etl_data.synthetic_customer_daily` 保存 `run_id + attempt_number + correlation_id`，讓資料落地可以回查 execution history。

### Environment separation

| Environment | Purpose | Governance |
|---|---|---|
| DEV | 開發與快速驗證 | synthetic/local candidate |
| TEST | Integration / acceptance | 必須通過 audit lifecycle test |
| PROD | 正式執行 | promotion 已驗證 artifact；Credential runtime injection |

### Release gate

Tag / Release 仍只在同一 main commit 的 CI 與 Security 都成功後建立。v0.3 CI 已包含 PostgreSQL + Hop 的 lifecycle smoke test。

### 後續

Container artifact promotion、offline bundle、checksum/signing 為 v0.4。

## English

v0.3 adds execution governance to deployment governance. Every retry is a distinct execution attempt identified by run ID, attempt number, and correlation ID.

Valid final transitions are `RUNNING → SUCCESS` and `RUNNING → FAILED`. A retry creates a new row; failed history is never rewritten as a new RUNNING attempt.

Persisted target rows carry the same execution identity, enabling data-to-execution traceability.

The release gate still requires successful CI and Security on the same main commit; v0.3 CI now includes the PostgreSQL/Hop lifecycle integration test.
