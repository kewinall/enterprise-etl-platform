#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VERSION="$(tr -d '[:space:]' < "${ROOT_DIR}/VERSION")"
IMAGE_REF="${IMAGE_REF:-enterprise-etl-hop:prod-v${VERSION}}"
SOURCE_SHA="${SOURCE_SHA:-${GITHUB_SHA:-local}}"
SYFT_IMAGE="${SYFT_IMAGE:-anchore/syft:v1.51.1}"
DIST_DIR="${DIST_DIR:-${ROOT_DIR}/dist}"
BUNDLE_DIR="${DIST_DIR}/offline/v${VERSION}"
RELEASE_DIR="${DIST_DIR}/release"
IMAGE_ARCHIVE="enterprise-etl-hop-v${VERSION}.tar"
ARCHIVE_NAME="enterprise-etl-offline-v${VERSION}.tar.gz"
ARCHIVE_PATH="${RELEASE_DIR}/${ARCHIVE_NAME}"

rm -rf "${BUNDLE_DIR}" "${RELEASE_DIR}"
mkdir -p "${BUNDLE_DIR}" "${RELEASE_DIR}"

IMAGE_ID="$(docker image inspect "${IMAGE_REF}" --format '{{.Id}}')"

docker save --output "${BUNDLE_DIR}/${IMAGE_ARCHIVE}" "${IMAGE_REF}"

docker run --rm \
  -v /var/run/docker.sock:/var/run/docker.sock \
  "${SYFT_IMAGE}" "${IMAGE_REF}" -o cyclonedx-json \
  > "${BUNDLE_DIR}/image-sbom.cdx.json"

export VERSION IMAGE_REF IMAGE_ID SOURCE_SHA IMAGE_ARCHIVE
python - "${BUNDLE_DIR}/manifest.json" <<'PY'
import json
import os
import sys

path = sys.argv[1]
payload = {
    "schema_version": 1,
    "platform_version": os.environ["VERSION"],
    "source_commit": os.environ["SOURCE_SHA"],
    "image_ref": os.environ["IMAGE_REF"],
    "image_id": os.environ["IMAGE_ID"],
    "image_archive": os.environ["IMAGE_ARCHIVE"],
    "sbom": "image-sbom.cdx.json",
    "promotion_policy": "build-once-promote-same-image-id",
    "credential_policy": "runtime-injection-only",
}
with open(path, "w", encoding="utf-8") as handle:
    json.dump(payload, handle, indent=2, sort_keys=True)
    handle.write("\n")
PY

(
  cd "${BUNDLE_DIR}"
  sha256sum "${IMAGE_ARCHIVE}" image-sbom.cdx.json manifest.json > SHA256SUMS
)

EPHEMERAL_KEY=""
if [[ -n "${SIGNING_PRIVATE_KEY:-}" ]]; then
  PRIVATE_KEY="${SIGNING_PRIVATE_KEY}"
else
  EPHEMERAL_KEY="$(mktemp)"
  PRIVATE_KEY="${EPHEMERAL_KEY}"
  openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:2048 -out "${PRIVATE_KEY}" >/dev/null 2>&1
fi

PUBLIC_KEY="${BUNDLE_DIR}/signing-public-key.pem"
openssl pkey -in "${PRIVATE_KEY}" -pubout -out "${PUBLIC_KEY}" >/dev/null 2>&1
openssl dgst -sha256 -sign "${PRIVATE_KEY}" -out "${BUNDLE_DIR}/SHA256SUMS.sig" "${BUNDLE_DIR}/SHA256SUMS"
openssl dgst -sha256 -verify "${PUBLIC_KEY}" -signature "${BUNDLE_DIR}/SHA256SUMS.sig" "${BUNDLE_DIR}/SHA256SUMS" >/dev/null

tar -C "${BUNDLE_DIR}" -czf "${ARCHIVE_PATH}" .
(
  cd "${RELEASE_DIR}"
  sha256sum "${ARCHIVE_NAME}" > "${ARCHIVE_NAME}.sha256"
)

openssl dgst -sha256 -sign "${PRIVATE_KEY}" -out "${ARCHIVE_PATH}.sig" "${ARCHIVE_PATH}"
cp "${PUBLIC_KEY}" "${RELEASE_DIR}/${ARCHIVE_NAME}.public.pem"
openssl dgst -sha256 \
  -verify "${RELEASE_DIR}/${ARCHIVE_NAME}.public.pem" \
  -signature "${ARCHIVE_PATH}.sig" \
  "${ARCHIVE_PATH}" >/dev/null

if [[ -n "${EPHEMERAL_KEY}" ]]; then
  rm -f "${EPHEMERAL_KEY}"
fi

echo "Created offline bundle: ${ARCHIVE_PATH}"
echo "Image ID: ${IMAGE_ID}"
