# Architecture / 架構

## 繁體中文

### v0.2 執行架構

v0.2 明確切分責任：**Airflow 負責 orchestration，Hop Server 提供受驗證的 execution endpoint，Apache Hop pipeline 負責 data processing**。

```mermaid
flowchart LR
  USER[Operator] --> AF[Apache Airflow]
  AF -->|Basic Auth REST /hop/execPipeline| HS[Apache Hop Server 2.19]
  HS --> HPL[synthetic_customer_daily.hpl]
  HPL --> GEN[Generate synthetic rows]
  GEN --> SEQ[Add record sequence]
  SEQ --> LOG[WriteToLog]

  ENV[DEV / TEST / PROD variable] --> AF
  AF -->|RUN_ENV| HPL

  AF -. v0.3 .-> AUDIT[(PostgreSQL ETL Audit)]
  HS -. v0.3 .-> AUDIT

  CI[CI / Security] --> ART[Validated Source / Artifact]
  ART --> TEST[TEST]
  TEST --> PROD[PROD Promotion]
```

### Component responsibility

| Component | v0.2 Responsibility |
|---|---|
| Apache Airflow | DAG scheduling/orchestration、retry、Hop invocation |
| Apache Hop Server | Authenticated execution gateway for Hop files |
| Apache Hop pipeline | Data processing logic |
| PostgreSQL | v0.1 audit schema preserved；完整 execution write 在 v0.3 |
| Docker Compose | Reproducible local integration |
| CI | Static validation + real Hop Server API smoke test |
| Security | Secret policy、Trivy filesystem scan、SBOM |
| Release gate | main CI + Security 成功後才能建立 Tag / Release |

### 為何使用 Hop Server REST

v0.2 不掛載 Docker socket 給 Airflow，也不要求額外 Docker/Kubernetes provider。Airflow 使用 Python standard library 對 Hop Server 發出 authenticated HTTP request，將 runtime 與 orchestration 解耦。

### Environment separation

`PLATFORM_ENV` 由 Airflow 轉成 `RUN_ENV` 傳入 Hop pipeline。真實 infrastructure endpoint 與 Credential 不應寫入 pipeline；v0.2 sample 只使用 generic values。

## English

### v0.2 execution architecture

v0.2 separates responsibilities explicitly: **Airflow owns orchestration, Hop Server exposes the authenticated execution endpoint, and Apache Hop pipelines own data processing**.

Airflow calls `/hop/execPipeline` through Basic Auth and passes `RUN_ENV` into the pipeline. This avoids exposing a Docker socket to Airflow and avoids adding an orchestration-specific container provider to the v0.2 baseline.

PostgreSQL audit tables remain part of the platform foundation, while complete execution writes and retry/error lifecycle persistence are intentionally scheduled for v0.3.
