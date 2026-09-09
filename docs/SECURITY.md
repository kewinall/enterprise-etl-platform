# Security / 安全

## 繁體中文

### v0.4 Security baseline

1. **Secret Scan**：Repository policy + Trivy secret scanner。
2. **Trivy**：PR 與 main 執行 filesystem vulnerability / secret scan。
3. **Repository SBOM**：Security workflow 產生 CycloneDX JSON。
4. **Image SBOM**：v0.4 offline bundle 使用 Syft 產生 CycloneDX image SBOM。
5. **Executable ETL CI**：PostgreSQL + Hop audit/retry/persistence。
6. **Executable Supply-Chain CI**：build / promote / checksum / signing / offline load。
7. **Synthetic-only**：Sample Data、Hostname、Credential、Schema 全為 generic。
8. **Runtime credential injection**：真實 Secret 不 bake 進 runtime image。

### Image security boundary

Runtime image包含：

- Apache Hop runtime
- ETL project
- generic metadata
- provenance labels

Runtime image不應包含：

- production database password
- API token
- private signing key
- customer data
- environment-specific production endpoint

### Signing

`create_offline_bundle.sh` 支援：

`SIGNING_PRIVATE_KEY=/secure/path/key.pem`

若沒有提供，CI 只會建立 ephemeral key 來測試流程。

**Ephemeral CI key 不是 production trust anchor。**

正式 signing private key 應存放於：

- HSM
- Vault
- CI protected secret
- 其他受控 signing service

Trusted public key 應透過獨立可信任管道配送到 Air-Gapped environment。

### Verification

Offline environment 先驗：

1. detached signature
2. archive SHA-256
3. internal SHA256SUMS signature
4. individual file checksums
5. loaded image ID

驗證未完成前不得部署。

### PostgreSQL / Airflow / Hop

v0.3 原有規則維持：

- PostgreSQL metadata 使用 runtime variables。
- Audit error 不保存 Credential/token/full sensitive payload。
- Hop Server 應位於 private network。
- 不把 Docker socket 掛給 Airflow runtime。

## English

v0.4 adds image-level SBOM generation, signed/checksummed offline bundles, immutable image identity checks, and executable supply-chain validation.

Real credentials and signing private keys are never baked into the runtime image. CI may use an ephemeral key only to prove the mechanism; production signing keys must come from protected external key management.

An air-gapped environment must verify the detached signature, archive checksum, internal signed checksums, and loaded image identity before deployment.
