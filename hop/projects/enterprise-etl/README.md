# Apache Hop Project Workspace

## 繁體中文

此目錄是 `enterprise-etl` 的 Apache Hop project home。

### v0.3 Pipelines

| Pipeline | Responsibility |
|---|---|
| `audit_execution_start.hpl` | 建立 RUNNING execution attempt |
| `synthetic_customer_daily.hpl` | 產生並寫入 3 筆 synthetic target rows |
| `audit_execution_finalize.hpl` | 更新 SUCCESS / FAILED 與 records/error |

### Metadata

- `project-config.json`
- `metadata/pipeline-run-configuration/local.json`
- `metadata/rdbms/audit-postgres.json`

`audit-postgres` 不保存真實 connection information，而是使用 `${POSTGRES_*}` runtime variables。

### Correlation

Pipeline 共同使用：

- `RUN_ENV`
- `RUN_ID`
- `ATTEMPT_NUMBER`
- `CORRELATION_ID`

因此 PostgreSQL target row 可以回查對應 execution attempt。

所有 data / hostname / credential 都是 synthetic / generic。

## English

This directory is the Apache Hop project home for `enterprise-etl`.

### v0.3 pipelines

- `audit_execution_start.hpl` creates a RUNNING execution attempt.
- `synthetic_customer_daily.hpl` persists three synthetic target rows.
- `audit_execution_finalize.hpl` records SUCCESS/FAILED status, counts, and error summary.

The `audit-postgres` metadata connection stores runtime `${POSTGRES_*}` expressions rather than real connection details.

All pipelines share run ID, attempt number, environment, and correlation ID so persisted target rows can be traced back to their execution attempt.

All data, hostnames, and credentials are synthetic or generic.
