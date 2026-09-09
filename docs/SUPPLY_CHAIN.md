# Supply Chain & Offline Promotion / 供應鏈與離線升版

## 繁體中文

### v0.4 目標

v0.4 將 v0.3 的可執行 ETL runtime 封裝為 **immutable Apache Hop runtime image**，並建立可驗證的 promotion 與 Air-Gapped 交付流程。

核心原則：

`Build once → identify → TEST → approve → promote same image → PROD`

**PROD 不重新 build。**

### Runtime image

`docker/hop-runtime.Dockerfile` 以 `apache/hop:2.19.0` 為 base，將：

`hop/projects/enterprise-etl`

bake 到：

`/opt/enterprise-etl/project`

Image 只包含 project artifact；Database endpoint、Password、Token 與環境差異仍由 runtime environment 注入。

OCI labels：

- `org.opencontainers.image.version`
- `org.opencontainers.image.revision`
- `org.opencontainers.image.source`

### Immutable promotion

`scripts/promote_image.sh` 不執行 `docker build`，只允許既有 image retag。

CI 驗證：

```text
candidate-v0.4.0
      │
      │ same sha256 image ID
      ▼
test-v0.4.0
      │
      │ same sha256 image ID
      ▼
prod-v0.4.0
```

Candidate、TEST、PROD 三個 reference 的 `docker image inspect .Id` 必須完全一致。

在正式 Registry 中，應以 registry digest（例如 `repo@sha256:...`）作為 promotion identity；本作品集 CI 使用 local Docker image ID 模擬同一不可變 artifact 的 promotion invariant。

### Image SBOM

Offline bundle 會使用 Syft 產生 CycloneDX JSON：

`image-sbom.cdx.json`

目前 CI pin：

`anchore/syft:v1.51.1`

SBOM 與 image archive、manifest 一起納入 checksum。

### Offline / Air-Gapped bundle

`scripts/create_offline_bundle.sh` 產生：

```text
enterprise-etl-offline-v0.4.0.tar.gz
├── enterprise-etl-hop-v0.4.0.tar
├── image-sbom.cdx.json
├── manifest.json
├── SHA256SUMS
├── SHA256SUMS.sig
└── signing-public-key.pem
```

Release 另外附：

- `enterprise-etl-offline-v0.4.0.tar.gz.sha256`
- `enterprise-etl-offline-v0.4.0.tar.gz.sig`
- `enterprise-etl-offline-v0.4.0.tar.gz.public.pem`

### Verification order

離線環境應依序：

1. 使用已信任的 public key 驗證 bundle detached signature。
2. 驗證 bundle SHA-256。
3. 解壓 bundle。
4. 驗證內層 `SHA256SUMS.sig`。
5. 執行 `sha256sum -c SHA256SUMS`。
6. `docker load` image archive。
7. 比對 loaded image ID 與 `manifest.json`。
8. 注入目標環境 Credential/Configuration 後部署。

可使用：

```bash
bash scripts/verify_offline_bundle.sh \
  dist/release/enterprise-etl-offline-v0.4.0.tar.gz \
  /secure/path/trusted-public-key.pem
```

### Signing trust model

CI 若沒有提供 `SIGNING_PRIVATE_KEY`，會產生 **ephemeral test key** 來證明 signing/verification 機制可執行。

這個 ephemeral key **不是 production trust anchor**。

正式流程應：

- Private key 存於 HSM、Vault、CI protected secret 或等價受控系統。
- CI 只在 signing step 暫時取得 private key。
- Public key 透過獨立、可信任的管道配送到離線環境。
- Offline verifier 以預先信任的 public key 驗證，不應只相信 bundle 自己附帶的 key。

### Promotion manifest

`manifest.json` 保存：

- platform version
- source commit
- image reference
- image ID
- image archive name
- SBOM name
- promotion policy
- credential policy

因此交付物能回溯到 source commit 與 immutable image identity。

## English

v0.4 packages the ETL project into an immutable Apache Hop runtime image and introduces build-once promotion plus an offline delivery bundle.

The CI contract is:

`candidate → TEST → PROD`

with the exact same Docker image ID at every stage. A production registry should use the registry digest as the authoritative identity.

The offline bundle contains the saved runtime image, a CycloneDX image SBOM, a manifest, checksums, and detached signatures. Verification proves both package integrity and that the loaded image ID matches the manifest.

When no signing key is supplied, CI creates an ephemeral key only to exercise the signing flow. Production private keys must be supplied by a protected signing system, and offline environments must trust a public key distributed independently from the bundle.
