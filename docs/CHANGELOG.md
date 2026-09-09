# Changelog / 變更紀錄

## 繁體中文

### [0.6.0] - 2026-09-10

#### Added

- deterministic Apache Hop / legacy JSON ETL parser
- normalized ETL metadata schemas
- parser provenance / source SHA-256 / evidence locators
- AI semantic context boundary、sensitive filtering、structured validation、deterministic fallback
- synthetic ETL Intelligence sample + smoke/regression tests
- executable root .gitlab-ci.yml enterprise delivery reference
- registry same-digest promotion + image digest verifier
- CVE applicability/remediation gate
- SBOM diff + pre/post remediation synthetic evidence
- ETL Intelligence / GitLab / Environment Promotion / Vulnerability Management docs

#### Changed

- Repository 定位強化為 Enterprise ETL Platform with Design-time ETL Intelligence + Enterprise Delivery Security
- v0.6 吸收原 Roadmap 的 deployment governance hardening
- GitHub CI 增加 P0 validation；GitHub Actions 仍為 public portfolio CI
- PROD promotion 明確禁止 rebuild


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

### [0.6.0] - 2026-09-10

#### Added

- deterministic Apache Hop / legacy JSON ETL parser
- normalized schemas, provenance, source digest, and evidence locators
- filtered evidence-bound semantic-analysis boundary with deterministic fallback
- synthetic ETL Intelligence smoke/regression evidence
- executable GitLab CI/CD enterprise reference
- same-registry-digest promotion and digest verification
- remediation-driven CVE gate and SBOM diff evidence
- ETL Intelligence, GitLab, environment-promotion, and vulnerability-management documentation

#### Changed

- repository positioning now explicitly includes design-time ETL intelligence and enterprise delivery security
- v0.6 incorporates deployment-governance hardening
- GitHub Actions remains the public portfolio CI while GitLab models enterprise delivery
- PROD promotion explicitly prohibits rebuilds


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
