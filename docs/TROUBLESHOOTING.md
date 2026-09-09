# Troubleshooting / 疑難排解

## 繁體中文

### `make lifecycle-smoke` 失敗

先確認：

```bash
docker version
docker compose version
docker pull postgres:16-alpine
docker pull apache/hop:2.19.0
```

Smoke script 失敗時會保留 response/log 於 workflow output，結束時 cleanup temporary containers/network。

### PostgreSQL 找不到 v0.3 table

症狀：

```text
relation etl_audit.etl_execution_event does not exist
relation etl_data.synthetic_customer_daily does not exist
```

原因通常是沿用 v0.2 volume，init scripts 沒有重新執行。

套用 migration：

```bash
docker compose exec -T postgres \
  psql -U etl_user -d etl_audit \
  < postgres/init/002_v0_3_audit_lifecycle.sql
```

### Hop 找不到 `audit-postgres`

確認：

```bash
docker compose exec hop \
  ls -l /files/project/metadata/rdbms/
```

並確認 Hop container 有：

```bash
docker compose exec hop env | grep '^POSTGRES_'
```

### Duplicate execution attempt

若看到 unique constraint / `uq_etl_execution_attempt` 錯誤，代表相同：

`pipeline + environment + run_id + attempt_number`

被重複建立。

正常 Airflow retry 會增加 `try_number`；不要手動重用同一 attempt identity。

### Execution 長期停在 RUNNING

查詢：

```sql
SELECT *
FROM etl_audit.etl_execution_log
WHERE status = 'RUNNING'
ORDER BY started_at;
```

可能原因：

- Airflow task/process 被強制終止。
- audit finalize endpoint 未執行。
- PostgreSQL/Hop 在 finalize 時不可用。

v0.3 保留 RUNNING 讓維運人員能識別 incomplete execution；自動 reconciliation 可於後續版本加入。

### Target 已寫入但 attempt FAILED

若 data pipeline 成功、finalize 過程失敗，Airflow task 仍可判定該 attempt 失敗。Target row 有 `attempt_number`，因此 retry 資料可分辨，不會覆蓋上一 attempt。

### Airflow retry 沒有增加 attempt

確認 DAG 使用：

`context["ti"].try_number`

以及 `execute_etl_with_audit` task 設定 `retries=2`。

### Security workflow 失敗

```bash
python scripts/secret_scan.py
```

Trivy finding 應更新 dependency/base image 或建立有期限且具理由的 exception，不應直接停用 gate。

## English

### Lifecycle smoke failure

Verify Docker, PostgreSQL 16 Alpine, and Apache Hop 2.19.0 are available. The CI smoke script prints Hop responses and logs when pipeline execution fails.

### Missing v0.3 tables

An existing v0.2 PostgreSQL volume does not rerun initialization scripts. Apply `002_v0_3_audit_lifecycle.sql` manually.

### Duplicate attempt

The unique execution identity is pipeline + environment + run_id + attempt_number. Airflow retries must use a new `try_number`.

### Stuck RUNNING execution

A RUNNING row may indicate abrupt task termination or a failed audit-finalization call. v0.3 intentionally preserves incomplete attempts for investigation.

### Data persisted but attempt failed

Target rows carry `attempt_number`, so side effects from a failed attempt remain distinguishable from data produced by a retry.
