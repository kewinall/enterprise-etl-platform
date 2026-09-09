# Security / 安全

## 繁體中文

### v0.1 Security baseline

1. **Secret Scan**：`scripts/secret_scan.py` 做 repository policy scan，GitHub Actions 另以 Trivy secret scanner 驗證。
2. **Trivy**：Pull Request 與 main push 皆執行 filesystem vulnerability / secret scan。
3. **SBOM**：Security workflow 產生 CycloneDX JSON SBOM artifact。
4. **Synthetic-only**：Sample Data、Hostname、Schema、Credential 一律使用 synthetic/generic 值。
5. **Immutable promotion**：PROD 應 promotion 已通過 TEST 的同一 image digest，不重新 build。
6. **Air-Gapped**：離線環境只接收經核准的 image、SBOM、configuration bundle 與 checksum。

### Credential 原則

- Repository 不保存真實 password、token、private key。
- `.env` 被 `.gitignore` 排除。
- `*.env.example` 只使用 synthetic 值。
- 真實 Credential 應由 CI secret store、Vault、Kubernetes Secret 或等價機制注入。

## English

### v0.1 security baseline

The repository uses layered controls: a local repository policy scan, Trivy filesystem/secret scanning on Pull Requests and main, CycloneDX SBOM generation, synthetic-only sample values, immutable image promotion, and an air-gapped transfer model based on approved artifacts plus checksums.

Real passwords, tokens, and private keys must never be committed. Runtime credentials should be injected by a CI secret store, Vault, Kubernetes Secret, or an equivalent mechanism.
