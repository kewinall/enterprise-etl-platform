# Roadmap / 路線圖

## 繁體中文

### v0.1 — Foundation ✅

- Platform boundary / Docker Compose
- Airflow / Hop workspace
- PostgreSQL audit schema
- DEV / TEST / PROD
- CI / Security / Trivy / SBOM

### v0.2 — Executable Hop + Airflow Integration ✅

- Apache Hop 2.19.0
- Hop Server
- Executable `.hpl`
- Airflow REST orchestration
- Runtime parameter passing
- Real Hop API CI smoke

### v0.3 — PostgreSQL Audit + Retry Lifecycle ✅

- Retry-aware `run_id + attempt_number`
- `correlation_id` / `trigger_type`
- RUNNING / SUCCESS / FAILED execution model
- Append-only lifecycle events
- PostgreSQL final-state trigger
- Persisted synthetic target
- Variable-driven Hop PostgreSQL metadata
- Airflow failure audit before retry
- CI test: attempt 1 FAILED → attempt 2 SUCCESS
- Data-to-execution traceability

### 後續版本

- v0.4：Container image build/promotion、offline bundle、checksum/signing
- v0.5：Prometheus/Grafana observability、SLO/alert baseline
- v0.6：Deployment governance hardening、release/recovery scenarios

## English

### v0.1 — Foundation ✅

Established platform boundaries, runtime skeletons, environment separation, and security gates.

### v0.2 — Executable Hop + Airflow Integration ✅

Added a real Apache Hop pipeline, Hop Server, authenticated Airflow orchestration, and executable CI.

### v0.3 — PostgreSQL Audit + Retry Lifecycle ✅

Adds retry-aware execution attempts, correlation IDs, durable lifecycle events, final-state database triggers, persisted synthetic ETL output, failure auditing before Airflow retry, and data-to-execution traceability.

### Future versions

- v0.4: container image build/promotion, offline bundle, checksum/signing
- v0.5: Prometheus/Grafana observability, alerts, and SLO baseline
- v0.6: deployment-governance hardening and failure-recovery scenarios
