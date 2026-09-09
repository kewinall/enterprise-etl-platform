#!/usr/bin/env bash
set -euo pipefail

if [[ "$#" -lt 1 || "$#" -gt 2 ]]; then
  echo "Usage: $0 <offline-bundle.tar.gz> [trusted-public-key.pem]"
  exit 2
fi

ARCHIVE_PATH="$(realpath "$1")"
PUBLIC_KEY="${2:-${ARCHIVE_PATH}.public.pem}"
SIGNATURE="${ARCHIVE_PATH}.sig"
CHECKSUM_FILE="${ARCHIVE_PATH}.sha256"
WORK_DIR="$(mktemp -d)"
trap 'rm -rf "${WORK_DIR}"' EXIT

for required in "${ARCHIVE_PATH}" "${PUBLIC_KEY}" "${SIGNATURE}" "${CHECKSUM_FILE}"; do
  if [[ ! -f "${required}" ]]; then
    echo "Missing verification artifact: ${required}"
    exit 1
  fi
done

openssl dgst -sha256 -verify "${PUBLIC_KEY}" -signature "${SIGNATURE}" "${ARCHIVE_PATH}" >/dev/null
(
  cd "$(dirname "${ARCHIVE_PATH}")"
  sha256sum -c "$(basename "${CHECKSUM_FILE}")"
)

tar -C "${WORK_DIR}" -xzf "${ARCHIVE_PATH}"

openssl dgst -sha256 \
  -verify "${PUBLIC_KEY}" \
  -signature "${WORK_DIR}/SHA256SUMS.sig" \
  "${WORK_DIR}/SHA256SUMS" >/dev/null

(
  cd "${WORK_DIR}"
  sha256sum -c SHA256SUMS
)

readarray -t manifest_values < <(
  python - "${WORK_DIR}/manifest.json" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as handle:
    payload = json.load(handle)

print(payload["image_ref"])
print(payload["image_id"])
print(payload["image_archive"])
PY
)

IMAGE_REF="${manifest_values[0]}"
EXPECTED_IMAGE_ID="${manifest_values[1]}"
IMAGE_ARCHIVE="${manifest_values[2]}"

docker load --input "${WORK_DIR}/${IMAGE_ARCHIVE}" >/dev/null
LOADED_IMAGE_ID="$(docker image inspect "${IMAGE_REF}" --format '{{.Id}}')"

if [[ "${LOADED_IMAGE_ID}" != "${EXPECTED_IMAGE_ID}" ]]; then
  echo "Loaded image ID mismatch: ${LOADED_IMAGE_ID} != ${EXPECTED_IMAGE_ID}"
  exit 1
fi

echo "Offline bundle verified and loaded ${IMAGE_REF} (${LOADED_IMAGE_ID})."
