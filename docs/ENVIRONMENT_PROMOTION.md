# Environment Promotion / 環境升版治理

## 繁體中文

### Promotion contract

Build once → identify digest → TEST → approve → promote same digest → PROD

環境差異只能來自 runtime configuration / credential injection，不可透過重新 build image 產生。

### Registry digest

企業 Registry 應以 repo@sha256:... 作為 artifact identity，而不是 mutable tag。

scripts/registry_promote.sh 會：

1. pull source image
2. 解析 source RepoDigest
3. tag + push target reference
4. pull target reference
5. 比對 source / target digest

scripts/verify_image_digest.sh 則可在部署前再次確認 expected digest。

### Approval and release

GitLab reference 在 promote_prod 使用：

- when: manual
- allow_failure: false
- resource_group: production

正式環境還應配合 protected environment、authorized approver、release evidence retention。

### Air-gapped promotion

無法直接連 Registry 時，沿用 signed/checksummed offline bundle：

candidate digest
→ SBOM
→ archive
→ checksum/signature
→ offline transfer
→ verify
→ docker load
→ identity check
→ deploy

### Rollback

Rollback 不重新 build。應選擇前一個已批准 digest / bundle，重做 identity verification 後部署。

## English

Promotion is based on immutable registry digest identity. Environment-specific configuration is injected at runtime rather than baked into a new image.

TEST and PROD promotion must prove digest equality. Air-gapped environments use the existing signed/checksummed bundle and identity verification process.

Rollback selects a previously approved immutable digest or bundle; it does not rebuild.
