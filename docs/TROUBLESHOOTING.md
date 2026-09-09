# Troubleshooting / 疑難排解

## 繁體中文

### `make supply-chain-smoke` build 失敗

確認：

```bash
docker version
docker pull apache/hop:2.19.0
docker pull anchore/syft:v1.51.1
```

並檢查 Docker daemon 可用空間。

### Baked project 不存在

驗證：

```bash
docker create --name etl-probe enterprise-etl-hop:local
docker cp etl-probe:/opt/enterprise-etl/project/project-config.json /tmp/project-config.json
docker rm etl-probe
```

若失敗，確認 `docker/hop-runtime.Dockerfile` build context 與 `.dockerignore`。

### Promotion image ID 不一致

`promote_image.sh` 不應 build，只能 retag。

若 source/target image ID 不一致，視為 artifact drift，停止 promotion。

### Syft 無法讀 Docker image

確認 Docker socket：

```bash
ls -l /var/run/docker.sock
docker image ls
```

CI 使用 containerized Syft 讀取 Docker daemon。

### Signature verification failed

確認使用的是**可信任且對應 signing private key 的 public key**：

```bash
openssl dgst -sha256 \
  -verify trusted-public-key.pem \
  -signature enterprise-etl-offline-v0.4.0.tar.gz.sig \
  enterprise-etl-offline-v0.4.0.tar.gz
```

不要把 bundle 內附 public key 自動視為 production trust root。

### SHA-256 failed

任何 checksum 不一致都應停止部署。不要重新產生 checksum 來讓錯誤消失；應重新取得可信任的 release bundle。

### Offline load image ID 不一致

若 `docker load` 後 image ID 與 `manifest.json` 不一致：

- 不部署。
- 保存 bundle 與 verification log。
- 回到 connected build zone 重新確認 artifact。
- 檢查 transfer/storage 是否損壞。

### `make lifecycle-smoke` 失敗

先確認：

```bash
docker pull postgres:16-alpine
docker pull apache/hop:2.19.0
```

v0.3 audit/retry/persistence troubleshooting 原則仍適用。

### Security workflow 失敗

```bash
python scripts/secret_scan.py
```

Trivy finding 應更新 dependency/base image 或建立有期限且具理由的 exception，不應直接停用 gate。

## English

If the supply-chain smoke fails, first verify Docker, the Apache Hop base image, and the pinned Syft image are available.

A promotion identity mismatch is artifact drift and must stop deployment. Signature or checksum failures must also stop deployment; do not regenerate verification data to hide the mismatch.

For production offline verification, trust a public key distributed independently from the bundle. If a loaded image ID differs from the manifest, quarantine the bundle and investigate the transfer/build chain.
