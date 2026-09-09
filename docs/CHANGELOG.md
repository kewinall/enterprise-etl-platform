# Changelog / 變更紀錄

## 繁體中文

### [0.5.0] - 2026-09-09

#### Added

- PostgreSQL `etl_observability` views
- synthetic least-privilege monitor role
- SQL Exporter 0.24.8
- Prometheus 3.14.0
- Alertmanager 0.34.0
- Grafana 13.2.1
- ETL run / failure / retry metrics
- records-written / stale / last-success / duration metrics
- 99% success SLO
- error ratio / error budget recording rules
- SLO breach / stale / no-recent-success alert rules
- Grafana Prometheus datasource provisioning
- Enterprise ETL Operations dashboard
- `observability_smoke.sh`
- `docs/SLO_ALERTING.md`

#### Changed

- Docker Compose 新增 `monitoring` profile
- CI 新增 runtime observability gate
- Observability 從設計文件提升為 executable platform capability

### [0.4.0] - 2026-09-09

- immutable Apache Hop runtime
- build-once promotion
- image SBOM
- signed/checksummed Air-Gapped bundle
- validated GitHub Release assets

### [0.3.0] - 2026-09-09

- PostgreSQL retry-aware execution audit
- append-only lifecycle events
- persisted synthetic target

### [0.2.0] - 2026-09-09

- executable Airflow → Hop Server integration

### [0.1.0] - 2026-09-09

- Enterprise Data Engineering Platform foundation

## English

### [0.5.0] - 2026-09-09

#### Added

- read-only PostgreSQL observability views
- synthetic least-privilege monitor role
- SQL Exporter 0.24.8
- Prometheus 3.14.0
- Alertmanager 0.34.0
- Grafana 13.2.1
- ETL run/failure/retry and runtime-health metrics
- 99% success SLO
- error-ratio/error-budget recording rules
- operational alerts
- provisioned Grafana datasource and Enterprise ETL Operations dashboard
- executable observability CI smoke
- `docs/SLO_ALERTING.md`

#### Changed

- Docker Compose adds a `monitoring` profile
- CI adds a runtime observability gate
- observability moves from planned design to executable platform capability

### [0.4.0] - 2026-09-09

- immutable Apache Hop runtime
- build-once promotion
- image SBOM
- signed/checksummed air-gapped bundle
- validated GitHub Release assets

### [0.3.0] - 2026-09-09

- retry-aware PostgreSQL execution audit
- append-only lifecycle events
- persisted synthetic target

### [0.2.0] - 2026-09-09

- executable Airflow-to-Hop Server integration

### [0.1.0] - 2026-09-09

- Enterprise Data Engineering Platform foundation
