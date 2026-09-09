# Apache Hop Project Workspace

## 繁體中文

此目錄是 `enterprise-etl` 的 Apache Hop project home。

v0.2 已包含：

- `project-config.json`
- `pipelines/synthetic_customer_daily.hpl`
- `RUN_ENV` lifecycle parameter
- Hop Server / `hop-run` compatible project layout

Pipeline 只產生 generic synthetic rows，加入 `record_id` sequence，再寫入 Hop execution log；不包含真實客戶資料，也不保存真實 Credential。

完整 PostgreSQL execution audit 與 persisted sample ETL 將於 v0.3 實作。

## English

This directory is the Apache Hop project home for `enterprise-etl`.

v0.2 includes:

- `project-config.json`
- `pipelines/synthetic_customer_daily.hpl`
- the `RUN_ENV` lifecycle parameter
- a project layout compatible with Hop Server and `hop-run`

The pipeline generates only generic synthetic rows, adds a `record_id` sequence, and writes output to the Hop execution log. It contains no real customer data or real credentials.

Complete PostgreSQL execution auditing and persisted sample ETL outputs are deferred to v0.3.
