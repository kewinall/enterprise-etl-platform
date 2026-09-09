# Installation / 安裝

## 繁體中文

### 前置需求

- Docker Engine 24+ 或相容版本
- Docker Compose v2
- Python 3.12
- Git
- OpenSSL
- Internet-connected build zone 若需首次取得 base image / Syft image

### Clone 與驗證

```bash
git clone https://github.com/kewinall/enterprise-etl-platform.git
cd enterprise-etl-platform
cp .env.example .env

python scripts/validate_repository.py
python -m unittest discover -s tests -v
docker compose config --quiet

make lifecycle-smoke
make supply-chain-smoke
```

### Build packaged Hop runtime

```bash
SOURCE_SHA="$(git rev-parse HEAD)" \
IMAGE_REPOSITORY=enterprise-etl-hop \
IMAGE_TAG=candidate-v0.4.0 \
bash scripts/build_runtime_image.sh
```

Project 會 bake 到：

`/opt/enterprise-etl/project`

### Compose 啟動

```bash
docker compose --profile orchestration up -d --build
docker compose ps
```

Compose 只 mount runtime environment file，不再用 bind mount 取代 packaged ETL project。

### v0.3 lifecycle smoke

`make lifecycle-smoke` 仍會驗證：

`attempt 1 FAILED → attempt 2 SUCCESS → STARTED,FAILED,STARTED,SUCCEEDED → 3 target rows`

### v0.4 supply-chain smoke

`make supply-chain-smoke` 會：

1. build candidate image
2. candidate → TEST
3. TEST → PROD
4. 比對 immutable image ID
5. 產生 CycloneDX image SBOM
6. `docker save`
7. 建立 manifest/checksum/signature
8. 移除 local references
9. verify bundle
10. `docker load`
11. 再次比對 image ID

產出於：

`dist/release/`

### Air-Gapped install

將 Release assets 搬入離線環境後：

```bash
bash scripts/verify_offline_bundle.sh \
  enterprise-etl-offline-v0.4.0.tar.gz \
  /secure/path/trusted-public-key.pem
```

驗證成功後 image 已由 `docker load` 匯入。

接著由目標環境注入：

- PostgreSQL endpoint
- Database credential
- Hop Server credential
- 其他 production-specific configuration

### Signing key

正式 bundle 建立時：

```bash
SIGNING_PRIVATE_KEY=/secure/path/signing-key.pem \
IMAGE_REF=enterprise-etl-hop:prod-v0.4.0 \
bash scripts/create_offline_bundle.sh
```

Private key 不可 commit 到 repository。

## English

v0.4 builds a packaged Hop runtime image with the ETL project baked into `/opt/enterprise-etl/project`.

Run `make supply-chain-smoke` to prove build-once promotion, image SBOM generation, offline archive creation, checksums, detached signatures, image removal/reload, and identity verification.

For an air-gapped target, verify the bundle with an independently trusted public key before loading and deploying it. Production credentials are injected only inside the target environment.
