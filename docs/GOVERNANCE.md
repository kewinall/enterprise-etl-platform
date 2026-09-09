# ETL Lifecycle & Deployment Governance / ETL 生命週期與部署治理

## 繁體中文

### Lifecycle

`Design → Develop → Validate → Security Scan → Package → TEST → Approve → Promote → PROD → Observe → Audit`

### Environment separation

| Environment | Purpose | Artifact rule |
|---|---|---|
| DEV | 開發與快速驗證 | 可建立 candidate artifact |
| TEST | 整合與驗收 | 僅使用 CI 產出的 immutable artifact |
| PROD | 正式執行 | promotion TEST 已驗證的同一 digest |

### Promotion policy

- 不在 PROD rebuild image。
- Tag 必須對應已通過 main CI/Security 的 commit。
- Release notes 記錄版本範圍與安全基線。
- Deployment configuration 與 Credential 分離。
- rollback 使用前一個已核准 digest。

### Release gate

`.github/workflows/release.yml` 以 main branch 的 CI 完成事件作為觸發點，並在建立版本前再次確認同一 commit 的 Security workflow 已成功。只有兩個 gate 都成功時，才會依 `VERSION` 建立 `vX.Y.Z` tag 與 GitHub Release。

### Air-Gapped transfer

離線部署 bundle 應包含 approved image archive、SBOM、checksum、release metadata、deployment configuration template；真實 Credential 由目標環境注入。

## English

### Lifecycle

`Design → Develop → Validate → Security Scan → Package → TEST → Approve → Promote → PROD → Observe → Audit`

DEV may produce candidate artifacts. TEST consumes immutable CI-produced artifacts. PROD promotes the exact digest validated in TEST. Production rebuilds are prohibited; rollback selects a previously approved digest.

### Release gate

`.github/workflows/release.yml` is triggered by completion of CI on main and verifies that the Security workflow for the same commit has also succeeded before creating a version. Only after both gates pass does it create the `vX.Y.Z` tag and GitHub Release from `VERSION`.

For air-gapped deployment, transfer only approved image archives, SBOMs, checksums, release metadata, and configuration templates. Real credentials are injected inside the target environment.
