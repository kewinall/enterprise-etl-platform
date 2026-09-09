# Roadmap / 路線圖

## 繁體中文

### v0.1 — Foundation ✅

- Platform boundary and architecture
- Docker Compose baseline
- Airflow DAG skeleton
- Hop workspace
- PostgreSQL audit schema
- DEV / TEST / PROD separation
- CI / Security / Trivy / SBOM
- Promotion, Air-Gapped, Observability documents

### v0.2 — Executable Hop + Airflow Integration ✅

- Apache Hop 2.19.0
- Hop project configuration
- Executable `synthetic_customer_daily.hpl`
- Long-lived Hop Server in Docker Compose
- Airflow `hop_synthetic_customer_daily` DAG
- Authenticated `/hop/execPipeline` orchestration
- `PLATFORM_ENV → RUN_ENV` parameter passing
- Real Hop Server API smoke test in CI
- Version-aware bilingual release notes

### 後續版本

- v0.3：完整 PostgreSQL audit logging、retry/error lifecycle、persisted sample ETL
- v0.4：Container image build/promotion、offline bundle、checksum/signing
- v0.5：Prometheus/Grafana observability、SLO/alert baseline
- v0.6：Deployment governance、release hardening、failure recovery scenario

## English

### v0.1 — Foundation ✅

Established the platform boundary, runtime skeletons, audit schema, environment separation, CI/security controls, and governance documentation.

### v0.2 — Executable Hop + Airflow Integration ✅

Adds Apache Hop 2.19.0, a real executable Hop pipeline, Hop Server, an Airflow orchestration DAG, authenticated pipeline execution, lifecycle parameter passing, executable CI smoke tests, and version-aware bilingual release notes.

### Future versions

- v0.3: complete PostgreSQL audit logging, retry/error lifecycle, and persisted sample ETL
- v0.4: container image build/promotion, offline bundle, checksum/signing
- v0.5: Prometheus/Grafana observability and SLO/alert baseline
- v0.6: deployment governance, release hardening, and failure-recovery scenarios
