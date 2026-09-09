# Security / 安全

## 繁體中文

### v0.3 Security baseline

1. **Secret Scan**：Repository policy + Trivy secret scanner。
2. **Trivy**：PR 與 main 執行 filesystem vulnerability / secret scan。
3. **SBOM**：產生 CycloneDX JSON。
4. **Executable CI**：實際啟動 PostgreSQL + Hop，驗證 audit/retry/persistence。
5. **Synthetic-only**：Sample Data、Hostname、Credential、Schema 全為 generic。
6. **Credential injection**：Hop RDBMS metadata 使用 runtime variables，不保存真實 password。
7. **Audit minimization**：`error_message` 只記錄錯誤摘要，不記錄 Credential、token 或完整敏感 payload。

### PostgreSQL connection

`metadata/rdbms/audit-postgres.json` 只包含：

```text
${POSTGRES_HOST}
${POSTGRES_PORT}
${POSTGRES_DB}
${POSTGRES_USER}
${POSTGRES_PASSWORD}
```

正式環境應由 Secret manager、Vault、Kubernetes Secret、CI protected variable 或等價機制注入。

### Audit data 本身也是敏感資料

即使不含業務 payload，audit table 仍可能揭露：

- pipeline name
- 執行時間
- failure pattern
- deployment/environment pattern

正式環境應限制 SELECT/UPDATE 權限，並對 audit retention、backup、log export 建立政策。

### Airflow → Hop

- Hop Server 放在 private network。
- 跨不受信任網段使用 TLS。
- 限制 execution endpoint 的 runtime identity。
- 不掛載 Docker socket 給 Airflow。
- local Basic Auth sample 不是 production credential。

## English

v0.3 keeps secret scanning, Trivy, CycloneDX SBOM generation, synthetic-only configuration, and executable integration testing.

The Hop PostgreSQL metadata contains runtime variable expressions rather than real credentials. Production credentials must come from an appropriate secret-management system.

Audit records are operationally sensitive even when they contain no business payload. Apply least-privilege database permissions, retention rules, backup controls, and secure log/export handling.

Error messages must remain concise summaries and must not contain credentials, tokens, or full sensitive payloads.
