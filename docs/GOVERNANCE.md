# ETL Lifecycle & Deployment Governance / ETL 生命週期與部署治理

## 繁體中文

### Lifecycle

`Design → Develop → Validate → Execute Smoke Test → Security Scan → Package → TEST → Approve → Promote → PROD → Observe → Audit`

v0.2 在 `Validate` 與 Security gate 之間加入 **real Hop execution smoke test**，避免只有 syntax/config validation。

### Environment separation

| Environment | Purpose | Artifact rule |
|---|---|---|
| DEV | 開發與快速驗證 | 可建立 candidate artifact |
| TEST | 整合與驗收 | 僅使用 CI 驗證的 immutable artifact |
| PROD | 正式執行 | promotion TEST 驗證的同一 digest |

`PLATFORM_ENV` 由 Airflow 傳入 Hop 的 `RUN_ENV`。Infrastructure-specific Credential 不屬於 pipeline source code。

### Release gate

`.github/workflows/release.yml`：

1. 等待 main CI 成功。
2. 尋找同一 commit 的 Security workflow。
3. 等 Security 成功。
4. 讀取 `VERSION`。
5. 要求存在 `docs/releases/vX.Y.Z.md` 雙語 notes。
6. 建立 Tag 與 GitHub Release。

因此 Tag 不會指向未通過 CI/Security 的 commit。

### Promotion policy

- PROD 不 rebuild。
- rollback 使用前一個 approved digest/tag。
- Deployment configuration 與 Credential 分離。
- Release metadata、SBOM、checksum 應跟 artifact 一起保存。

### Air-Gapped transfer

離線 bundle 應包含 approved image archive、SBOM、checksum、release metadata、deployment configuration template；真實 Credential 在目標環境內注入。

## English

### Lifecycle

`Design → Develop → Validate → Execute Smoke Test → Security Scan → Package → TEST → Approve → Promote → PROD → Observe → Audit`

v0.2 adds a real Hop execution smoke test before release. Environment-specific credentials remain outside pipeline source code.

The release gate waits for CI and the matching Security workflow on the same main commit, reads `VERSION`, requires bilingual version-specific release notes, and only then creates the tag and GitHub Release.

Production must promote the artifact already validated in TEST rather than rebuilding it. Air-gapped bundles should include approved images, SBOMs, checksums, release metadata, and configuration templates, with real credentials injected in the target environment.
