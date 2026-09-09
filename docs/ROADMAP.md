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
- Append-only lifecycle events
- Persisted synthetic target
- Failure audit before retry
- Data-to-execution traceability

### v0.4 — Immutable Supply Chain + Air-Gapped Bundle ✅

- Packaged Apache Hop runtime image
- OCI provenance labels
- Build once / promote same image identity
- Candidate → TEST → PROD
- CycloneDX image SBOM
- Offline Docker image archive
- Promotion manifest
- SHA-256 checksums
- Detached signature
- Offline verification + reload identity proof
- GitHub Release offline assets

### 後續版本

- v0.5：Prometheus/Grafana observability、SLO/alert baseline
- v0.6：Deployment governance hardening、release/recovery scenarios

## English

### v0.1 — Foundation ✅

Established platform boundaries, runtime skeletons, environment separation, and security gates.

### v0.2 — Executable Hop + Airflow Integration ✅

Added a real Apache Hop pipeline, Hop Server, authenticated Airflow orchestration, and executable CI.

### v0.3 — PostgreSQL Audit + Retry Lifecycle ✅

Added retry-aware execution attempts, lifecycle events, persisted ETL output, and data-to-execution traceability.

### v0.4 — Immutable Supply Chain + Air-Gapped Bundle ✅

Adds a packaged Hop runtime image, OCI provenance, build-once promotion, image SBOM, signed/checksummed offline bundle creation, offline reload verification, and release assets.

### Future versions

- v0.5: Prometheus/Grafana observability, alerts, and SLO baseline
- v0.6: deployment-governance hardening and failure-recovery scenarios
