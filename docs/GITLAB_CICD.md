# GitLab CI/CD Reference / GitLab 企業交付參考實作

## 繁體中文

### 目的

GitHub Actions 繼續作為公開 Portfolio CI；根目錄 .gitlab-ci.yml 則展示較接近企業環境的 GitLab delivery reference。

### Pipeline

Developer
→ feature branch
→ Merge Request
→ validation / tests
→ candidate image
→ security gates
→ SBOM / offline bundle
→ TEST same-digest promotion
→ approval
→ PROD same-digest promotion

### 實作 Job

- validate: repository policy、compile、GitLab reference self-check
- unit_test: unittest、ETL Intelligence smoke、vulnerability lifecycle smoke
- build_candidate: 只建立一次 immutable candidate image
- secret_scan: synthetic secret policy scan
- repository_trivy: filesystem CVE/secret scan
- container_trivy: candidate image scan
- sbom: CycloneDX image SBOM
- vulnerability_gate: fail-before / pass-after remediation evidence
- package_offline: air-gapped bundle
- promote_test: registry digest promotion + verification
- release_candidate: main branch validated digest evidence
- promote_prod: manual approval、resource_group serialization、same digest verification

### Production invariants

1. PROD 不得 rebuild。
2. TEST / PROD 必須來自相同 registry digest。
3. Promotion job 必須驗證 digest。
4. Security/SBOM/vulnerability gate 必須在 TEST promotion 前完成。
5. PROD job 使用 manual gate。
6. production resource_group 防止平行 promotion。
7. Registry credential 應使用 protected/masked CI variables。

### Verify reference

~~~bash
python ci/gitlab/verify_reference.py
~~~

這個 verifier 會確認主要 gate 存在，並確認 promote_prod 不含 docker build 或 build_runtime_image.sh。

## English

The root .gitlab-ci.yml is an executable enterprise delivery reference that coexists with GitHub Actions.

It builds the candidate once, runs validation/testing/security/SBOM gates, promotes the same registry digest into TEST, and requires a manual serialized PROD promotion.

The verification script also asserts that the PROD job cannot rebuild the image.
