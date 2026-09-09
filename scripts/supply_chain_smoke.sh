#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VERSION="$(tr -d '[:space:]' < "${ROOT_DIR}/VERSION")"
IMAGE_REPOSITORY="${IMAGE_REPOSITORY:-enterprise-etl-hop}"
SOURCE_SHA="${SOURCE_SHA:-${GITHUB_SHA:-local}}"
CANDIDATE_REF="${IMAGE_REPOSITORY}:candidate-v${VERSION}"
TEST_REF="${IMAGE_REPOSITORY}:test-v${VERSION}"
PROD_REF="${IMAGE_REPOSITORY}:prod-v${VERSION}"

cleanup_images() {
  docker image rm -f "${CANDIDATE_REF}" "${TEST_REF}" "${PROD_REF}" >/dev/null 2>&1 || true
}
trap cleanup_images EXIT

rm -rf "${ROOT_DIR}/dist"

SOURCE_SHA="${SOURCE_SHA}" \
IMAGE_REPOSITORY="${IMAGE_REPOSITORY}" \
IMAGE_TAG="candidate-v${VERSION}" \
  bash "${ROOT_DIR}/scripts/build_runtime_image.sh"

EXPECTED_IMAGE_ID="$(docker image inspect "${CANDIDATE_REF}" --format '{{.Id}}')"

bash "${ROOT_DIR}/scripts/promote_image.sh" "${CANDIDATE_REF}" "${TEST_REF}"
bash "${ROOT_DIR}/scripts/promote_image.sh" "${TEST_REF}" "${PROD_REF}"

TEST_ID="$(docker image inspect "${TEST_REF}" --format '{{.Id}}')"
PROD_ID="$(docker image inspect "${PROD_REF}" --format '{{.Id}}')"
if [[ "${EXPECTED_IMAGE_ID}" != "${TEST_ID}" || "${EXPECTED_IMAGE_ID}" != "${PROD_ID}" ]]; then
  echo "Immutable promotion invariant failed."
  exit 1
fi

IMAGE_REF="${PROD_REF}" SOURCE_SHA="${SOURCE_SHA}" \
  bash "${ROOT_DIR}/scripts/create_offline_bundle.sh"

ARCHIVE="${ROOT_DIR}/dist/release/enterprise-etl-offline-v${VERSION}.tar.gz"

cleanup_images
bash "${ROOT_DIR}/scripts/verify_offline_bundle.sh" "${ARCHIVE}"

LOADED_ID="$(docker image inspect "${PROD_REF}" --format '{{.Id}}')"
if [[ "${LOADED_ID}" != "${EXPECTED_IMAGE_ID}" ]]; then
  echo "Offline restore changed image ID."
  exit 1
fi

echo "v0.4 immutable image promotion/offline bundle smoke test passed."
