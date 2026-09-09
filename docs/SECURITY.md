# Security / 安全

## 繁體中文

### Security baseline

1. **Secret Scan**：`scripts/secret_scan.py` + Trivy secret scanner。
2. **Trivy**：Pull Request 與 main push 執行 filesystem vulnerability / secret scan。
3. **SBOM**：Security workflow 產生 CycloneDX JSON SBOM。
4. **Executable CI**：v0.2 CI 實際啟動 Hop Server 並呼叫 pipeline execution endpoint。
5. **Synthetic-only**：Sample Data、Hostname、Schema、Credential 只使用 synthetic/generic values。
6. **Immutable promotion**：PROD 應 promotion TEST 驗證過的同一 artifact/image digest。
7. **Air-Gapped**：只轉移 approved image、SBOM、configuration、checksum、release metadata。

### Airflow → Hop Server

v0.2 使用 Hop Server Basic Auth。Repository 中的：

- `hop-user`
- `synthetic-hop-password`

只是 local synthetic defaults，不是正式 Credential。

正式環境要求：

- Credential 由 Secret store 注入，不 commit。
- Hop Server 應放在 private network。
- 跨主機或不受信任網段應使用 TLS。
- 僅 Airflow/runtime identity 可呼叫 execution endpoint。
- 不應將 Docker socket 掛入 Airflow container。

### Repository policy

`.env` 被 `.gitignore` 排除；`.env.example` 只保留 generic values。主要文件與 Release notes 需同時包含繁體中文與 English。

## English

### Security baseline

v0.2 keeps layered repository and runtime controls: local secret-policy validation, Trivy filesystem/secret scanning, CycloneDX SBOM generation, executable Hop API smoke tests, synthetic-only configuration, immutable promotion guidance, and an air-gapped artifact-transfer model.

### Airflow to Hop Server boundary

The repository contains synthetic local Basic Auth defaults only. In a real deployment, inject credentials from a secret manager, place Hop Server on a private network, use TLS across untrusted network boundaries, restrict execution endpoints to the Airflow/runtime identity, and do not expose the Docker socket to the Airflow container.
