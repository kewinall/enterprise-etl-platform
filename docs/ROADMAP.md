# Roadmap / 路線圖

## 繁體中文

### v0.1 — Foundation ✅
- Platform boundary / Docker Compose / CI / Security

### v0.2 — Executable Hop + Airflow Integration ✅
- Hop Server / executable pipeline / Airflow REST orchestration

### v0.3 — PostgreSQL Audit + Retry Lifecycle ✅
- retry-aware audit / lifecycle events / persisted target

### v0.4 — Immutable Supply Chain + Air-Gapped Bundle ✅
- packaged Hop runtime / same-image promotion / SBOM / signed offline bundle

### v0.5 — Prometheus/Grafana Observability + SLO/Alerting ✅
- read-only observability views / metrics / alerting / dashboard / runtime smoke

### v0.6 — ETL Intelligence + Enterprise Delivery Security ✅
- deterministic ETL parser
- normalized metadata / evidence / provenance
- AI semantic boundary / structured output / fallback / sensitive filtering
- GitLab CI/CD enterprise reference
- TEST → PROD same-registry-digest promotion
- CVE applicability / remediation lifecycle
- SBOM diff / CVE gate / digest verification / regression evidence
- deployment governance / rollback identity rules

### v0.7 — Legacy ETL Modernization + Metadata / Lineage + Enterprise AI Integration ✅
- synthetic Pentaho KTR / KJB deterministic parser
- normalized metadata v1.1
- structural / inferred-deterministic / AI interpretation lineage separation
- Pentaho → Apache Hop migration planner + deterministic validator
- workflow dependency / parameter / variable preservation
- Data Platform MCP read-only integration contract
- RAG / DataOps responsibility-boundary reference integration
- Multi-LLM AI Gateway semantic-analysis path
- explicit column-level lineage capability boundary

### 後續版本

v0.8 僅在能增加新的 production evidence 時考慮，例如 dialect-aware column lineage、large migration corpus、HA/DR exercise；不為版本號而堆疊與相鄰 Repository 重複的能力。

## English

v0.1 through v0.5 establish the executable data-engineering runtime, audit, immutable delivery, air-gapped packaging, and observability layers.

### v0.6 — ETL Intelligence + Enterprise Delivery Security ✅

v0.6 adds deterministic design-time ETL parsing, normalized provenance/evidence, an evidence-bound AI semantic layer with fallback, an executable GitLab delivery reference, same-digest environment promotion, and a remediation-driven vulnerability lifecycle.

### v0.7 — Legacy ETL Modernization + Metadata / Lineage + Enterprise AI Integration ✅

v0.7 adds a public synthetic Pentaho-to-Hop modernization case, normalized metadata v1.1, explicit lineage classifications, deterministic migration planning/validation, MCP controlled access, RAG/DataOps reference integration, and a Multi-LLM AI Gateway semantic path.

Future work remains optional and must add new production evidence rather than duplicate adjacent repositories.
