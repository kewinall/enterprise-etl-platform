# Changelog / 變更紀錄

## 繁體中文

### [0.3.0] - 2026-09-09

#### Added

- PostgreSQL v0.3 audit lifecycle migration
- `correlation_id`、`attempt_number`、`trigger_type`
- `etl_audit.etl_execution_event`
- STARTED / SUCCEEDED / FAILED database-trigger events
- `etl_data.synthetic_customer_daily` persisted target
- Hop `audit-postgres` variable-driven metadata
- `audit_execution_start.hpl`
- `audit_execution_finalize.hpl`
- Retry-aware Airflow lifecycle
- PostgreSQL + Hop integration smoke test
- `docs/AUDIT_LIFECYCLE.md`

#### Changed

- `synthetic_customer_daily.hpl` now persists data to PostgreSQL
- CI now validates failed-attempt + successful-retry lifecycle

### [0.2.0] - 2026-09-09

- Executable Airflow → Hop Server integration
- Apache Hop 2.19.0
- Real Hop Server API smoke test
- Version-aware Release notes

### [0.1.0] - 2026-09-09

- Enterprise Data Engineering Platform foundation
- PostgreSQL audit baseline
- Docker Compose / DEV TEST PROD
- CI / Security / Trivy / SBOM

## English

### [0.3.0] - 2026-09-09

#### Added

- PostgreSQL v0.3 audit lifecycle migration
- `correlation_id`, `attempt_number`, and `trigger_type`
- `etl_audit.etl_execution_event`
- database-triggered STARTED / SUCCEEDED / FAILED events
- persisted `etl_data.synthetic_customer_daily`
- variable-driven Hop PostgreSQL metadata
- audit start/finalize Hop pipelines
- retry-aware Airflow lifecycle
- PostgreSQL + Hop integration smoke test
- `docs/AUDIT_LIFECYCLE.md`

#### Changed

- The main synthetic pipeline now persists rows to PostgreSQL
- CI now proves a failed attempt and successful retry remain separately auditable

### [0.2.0] - 2026-09-09

- Executable Airflow-to-Hop Server integration
- Apache Hop 2.19.0
- Real Hop Server API smoke test
- Version-aware release notes

### [0.1.0] - 2026-09-09

- Enterprise Data Engineering Platform foundation
- PostgreSQL audit baseline
- Docker Compose / DEV TEST PROD
- CI / Security / Trivy / SBOM
