# Enterprise ETL Platform

**目前版本 / Current release: v0.6.0**

> **📘 Interactive Project Guide / 專案互動式說明文件**  
> [Open Live Project Guide](https://kewinall.github.io/enterprise-etl-platform/) · [Repository HTML](docs/enterprise-etl-platform-guide.html) — 面試官 5 分鐘速讀、完整架構、Airflow → Hop ETL lifecycle、PostgreSQL Audit/Retry、ETL Intelligence、GitLab Enterprise Delivery、CVE Remediation、Immutable Supply Chain、Air-Gapped Delivery、Prometheus/Grafana、SLO/Alerting 與使用教學集中於 Interactive HTML Guide。

[繁體中文](#繁體中文) | [English](#english)

## 繁體中文

`enterprise-etl-platform` 是以 **Enterprise Data Engineering Platform** 為核心的作品集專案，涵蓋 ETL/ELT execution、Airflow orchestration、Apache Hop runtime、PostgreSQL audit、retry lifecycle、design-time ETL intelligence、GitLab enterprise delivery、CVE remediation、immutable supply chain、Air-Gapped deployment、Prometheus/Grafana observability、SLO 與 alerting。

## Engineering Decisions & Production Evidence

### Problem

企業 ETL 的風險不只在 transformation 是否能執行，而是 **scheduler、runtime、audit、retry、artifact promotion、offline delivery 與 observability** 之間是否有一致且可追蹤的 lifecycle。只看 Airflow task 綠燈，無法回答「第一次失敗有沒有被保留」、「TEST 與 PROD 是否真的是同一個 artifact」、「監控告警是否真的會 firing」。

### Key Engineering Decisions & Trade-offs

| Decision | Why / Benefit | Trade-off |
|---|---|---|
| **Airflow 負責 orchestration，Apache Hop 負責 data processing** | 將 scheduling/retry/context 與 ETL transformation responsibility 分離，讓 workflow 與資料處理各自演進 | 多一層 runtime 與 connection/configuration 管理，故障關聯需要跨 Airflow / Hop / Audit |
| **PostgreSQL 作為 execution truth** | Run / Attempt / Event 可持久化，retry 不覆蓋歷史，可支援 audit、metrics、SLO | PostgreSQL 成為平台依賴，需要 HA、backup 與 schema migration 管理 |
| **Build once, promote same immutable artifact** | 避免 TEST 與 PROD 重新 build 造成 drift，可用 digest/checksum 驗證交付一致性 | 需要額外 promotion、bundle、verification 與 registry/offline artifact lifecycle |
| **Observability 從 read-only audit views 匯出** | Monitoring 不需要直接寫入 ETL runtime；SQL Exporter → Prometheus → Alertmanager/Grafana 可獨立演進 | Metrics freshness 依賴 audit 資料與 exporter scrape path |

### Production Failure & Recovery

| Scenario | Engineering Behavior / Detection | Recovery Strategy |
|---|---|---|
| Hop execution 失敗後 retry | Failure 與 retry 被視為不同 attempt，不覆蓋前一次 execution history | 依 Airflow retry policy 重試；用 PostgreSQL audit 追蹤 attempt history |
| Audit database 不可用 | Durable execution truth 不可被確認；不能只依 scheduler UI 推定完整成功 | 將 audit DB 視為平台 dependency，恢復後重新驗證 run/attempt 狀態並補做必要 retry |
| Prometheus / Grafana 暫時不可用 | Data execution truth 仍保留於 PostgreSQL；監控面與 ETL execution path 分離 | 恢復 SQL Exporter / Prometheus / Alertmanager / Grafana 後重新 scrape，不重建 ETL history |
| Offline bundle / image identity 不一致 | checksum / image identity verification 應阻止不一致 artifact promotion | 重新產生或驗證 bundle，只有通過 identity/checksum 驗證的 artifact 才進入下一環境 |

### Production Evidence

| Claim | Repository Evidence |
|---|---|
| Retry / audit lifecycle 可執行驗證 | `scripts/etl_lifecycle_smoke.sh`, `docs/AUDIT_LIFECYCLE.md`, `postgres/init/002_v0_3_audit_lifecycle.sql` |
| Observability / SLO / firing alert 不是紙上設計 | `scripts/observability_smoke.sh`, `postgres/init/003_v0_5_observability.sql`, `monitoring/sql-exporter/etl_audit.collector.yml` |
| Immutable promotion / offline bundle 有 runtime verification | `scripts/supply_chain_smoke.sh`, `scripts/promote_image.sh`, `scripts/verify_offline_bundle.sh` |
| Repository policy 與 regression baseline | `scripts/validate_repository.py`, `tests/test_repository.py` |
| CI / Security gate | `.github/workflows/ci.yml`, `.github/workflows/security.yml` |

### Interview Questions This Project Can Answer

- 為什麼不是「全部用 Airflow PythonOperator」或「全部用 Hop」？
- Retry 如何避免把第一次 failure 覆蓋掉？
- 如何證明 TEST 與 PROD 使用的是同一個 artifact？
- Monitoring stack 掛掉時，為什麼 execution history 不會一起消失？
- CI 綠燈到底驗證了 syntax，還是實際 runtime behavior？


### v0.6 — ETL Intelligence + Enterprise Delivery Security

v0.6 將既有 runtime / audit / observability 平台延伸到 **design-time intelligence** 與 **remediation-driven delivery security**。

~~~text
Legacy ETL / Apache Hop
          |
          v
Deterministic ETL Parser
          |
          v
Normalized Metadata + Evidence
          |
          v
Sensitive Context Filter
          |
          v
AI Semantic Analyzer
          |
          v
Evidence-bound ETL Intelligence
~~~

Engineering invariant：

- parser 決定 structural truth；AI 只做 semantic explanation。
- AI 不直接解析整份 ETL artifact。
- AI result 必須引用 parser evidence，且不能建立不存在的 SQL / step / dependency。
- AI unavailable 或 contract validation 失敗時，回到 deterministic fallback。
- Connection credential 不進 AI context；SQL literal 會 redaction。
- ETL AI 僅處理 design-time parsing / explanation / migration assistance，不負責 runtime incident RCA。

Enterprise delivery 提供根目錄 .gitlab-ci.yml：

~~~text
MR → Validate/Test → Build Once → Trivy/Secret/SBOM/CVE Gate
   → TEST same digest → Approval → PROD same digest
~~~

Vulnerability lifecycle：

~~~text
Detect → Applicability → Remediation → Rebuild → SBOM → Rescan
→ TEST → Approval → Same Digest PROD → Audit Evidence
~~~

可執行證據：

- scripts/etl_intelligence_smoke.sh
- scripts/vulnerability_lifecycle_smoke.sh
- ci/gitlab/verify_reference.py
- scripts/registry_promote.sh
- scripts/verify_image_digest.sh
- tests/test_etl_intelligence.py
- tests/test_vulnerability_management.py
- tests/test_gitlab_reference.py

詳細文件：

- docs/ETL_INTELLIGENCE.md
- docs/GITLAB_CICD.md
- docs/ENVIRONMENT_PROMOTION.md
- docs/VULNERABILITY_MANAGEMENT.md

### v0.5 — Executable Observability

v0.5 新增完整監控鏈：

```text
PostgreSQL Audit
      ↓
etl_observability read-only views
      ↓
SQL Exporter
      ↓
Prometheus
  ├─ ETL metrics
  ├─ SLO recording rules
  └─ alert rules
      ↓
Alertmanager
      ↓
Grafana
```

核心內容：

- SQL Exporter **0.24.8**
- Prometheus **3.14.0**
- Alertmanager **0.34.0**
- Grafana **13.2.1**
- read-only `etl_observability` schema
- least-privilege `etl_monitor` sample role
- ETL run / failure / retry counters
- records-written counter
- stale RUNNING gauge
- latest-success timestamp
- average / P95 duration
- **99% ETL success SLO**
- error ratio / error budget recording rules
- SLO breach / stale execution / no-recent-success alerts
- auto-provisioned Grafana datasource + dashboard
- runtime CI observability smoke

### Metrics

```text
etl_pipeline_run_total
etl_pipeline_failure_total
etl_pipeline_retry_total
etl_records_written_total
etl_running_stale_total
etl_last_success_timestamp_seconds
etl_pipeline_duration_seconds
etl_pipeline_duration_p95_seconds
```

### 快速驗證

```bash
cp .env.example .env
python scripts/validate_repository.py
python -m unittest discover -s tests -v
docker compose config --quiet

make etl-intelligence-smoke
make lifecycle-smoke
make observability-smoke
make supply-chain-smoke
make vulnerability-smoke
make gitlab-verify
```

`make observability-smoke` 會實際建立 synthetic SUCCESS / FAILED / retry SUCCESS / stale RUNNING execution，然後驗證 Prometheus scrape、SLO rules、firing alerts、Alertmanager readiness、Grafana datasource 與 dashboard provisioning。

### 啟動 Monitoring Stack

```bash
docker compose --profile monitoring up -d
docker compose ps
```

- Grafana: `http://localhost:3000`
- Prometheus: `http://localhost:9090`
- Alertmanager: `http://localhost:9093`
- SQL Exporter: `http://localhost:9399/metrics`
- Dashboard: **Enterprise ETL Operations**

> Repository 只含 synthetic / generic configuration。正式 database、Grafana、Alertmanager credential 與 notification endpoint 應由部署環境注入。

詳細文件：

- [Interactive Project Guide / 專案互動式說明文件](docs/enterprise-etl-platform-guide.html)
- `docs/OBSERVABILITY.md`
- `docs/SLO_ALERTING.md`
- `docs/AUDIT_LIFECYCLE.md`
- `docs/SUPPLY_CHAIN.md`
- `docs/GOVERNANCE.md`

## English

`enterprise-etl-platform` is an **Enterprise Data Engineering Platform** portfolio project covering ETL execution, orchestration, design-time ETL intelligence, audit/retry lifecycle, GitLab enterprise delivery, vulnerability remediation, immutable supply chain, air-gapped delivery, and executable observability.

v0.6 adds deterministic ETL parsing, normalized evidence/provenance, evidence-bound semantic analysis with deterministic fallback, a GitLab CI/CD reference, same-digest promotion, and a verifiable CVE remediation lifecycle. v0.5 observability remains fully supported.

`make observability-smoke` creates synthetic success/failure/retry/stale executions and proves metrics, SLO rules, firing alerts, Alertmanager, and Grafana provisioning at runtime.

All sample data, credentials, hostnames, schemas, and company information are synthetic or generic.

## Documentation

- [Interactive Project Guide / 專案互動式說明文件](docs/enterprise-etl-platform-guide.html)
- [Architecture](docs/ARCHITECTURE.md)
- [ETL Intelligence](docs/ETL_INTELLIGENCE.md)
- [GitLab CI/CD Reference](docs/GITLAB_CICD.md)
- [Environment Promotion](docs/ENVIRONMENT_PROMOTION.md)
- [Vulnerability Management](docs/VULNERABILITY_MANAGEMENT.md)
- [Installation](docs/INSTALLATION.md)
- [Audit Lifecycle](docs/AUDIT_LIFECYCLE.md)
- [Supply Chain](docs/SUPPLY_CHAIN.md)
- [Observability](docs/OBSERVABILITY.md)
- [SLO & Alerting](docs/SLO_ALERTING.md)
- [Security](docs/SECURITY.md)
- [Governance](docs/GOVERNANCE.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
- [Roadmap](docs/ROADMAP.md)
