#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VERSION="$(tr -d '[:space:]' < "${ROOT_DIR}/VERSION")"
SOURCE_SHA="${SOURCE_SHA:-${GITHUB_SHA:-}}"
IMAGE_REPOSITORY="${IMAGE_REPOSITORY:-enterprise-etl-hop}"
IMAGE_TAG="${IMAGE_TAG:-candidate-v${VERSION}}"
IMAGE_REF="${IMAGE_REPOSITORY}:${IMAGE_TAG}"
OUTPUT_DIR="${OUTPUT_DIR:-${ROOT_DIR}/dist/supply-chain}"

if [[ -z "${SOURCE_SHA}" ]]; then
  SOURCE_SHA="$(git -C "${ROOT_DIR}" rev-parse HEAD 2>/dev/null || printf 'local')"
fi

mkdir -p "${OUTPUT_DIR}"

docker build \
  --file "${ROOT_DIR}/docker/hop-runtime.Dockerfile" \
  --build-arg "VERSION=${VERSION}" \
  --build-arg "VCS_REF=${SOURCE_SHA}" \
  --tag "${IMAGE_REF}" \
  "${ROOT_DIR}"

IMAGE_ID="$(docker image inspect "${IMAGE_REF}" --format '{{.Id}}')"
LABEL_VERSION="$(docker image inspect "${IMAGE_REF}" --format '{{ index .Config.Labels "org.opencontainers.image.version" }}')"
LABEL_REVISION="$(docker image inspect "${IMAGE_REF}" --format '{{ index .Config.Labels "org.opencontainers.image.revision" }}')"

if [[ "${LABEL_VERSION}" != "${VERSION}" ]]; then
  echo "Image version label mismatch: ${LABEL_VERSION}"
  exit 1
fi

if [[ "${LABEL_REVISION}" != "${SOURCE_SHA}" ]]; then
  echo "Image revision label mismatch: ${LABEL_REVISION}"
  exit 1
fi

probe_container="$(docker create "${IMAGE_REF}")"
trap 'docker rm -f "${probe_container}" >/dev/null 2>&1 || true' EXIT
docker cp "${probe_container}:/opt/enterprise-etl/project/project-config.json" /tmp/enterprise-etl-project-config.json
docker cp "${probe_container}:/opt/enterprise-etl/project/pipelines/synthetic_customer_daily.hpl" /tmp/enterprise-etl-pipeline.hpl
rm -f /tmp/enterprise-etl-project-config.json /tmp/enterprise-etl-pipeline.hpl
docker rm -f "${probe_container}" >/dev/null
trap - EXIT

cat > "${OUTPUT_DIR}/build.env" <<EOF
VERSION=${VERSION}
SOURCE_SHA=${SOURCE_SHA}
IMAGE_REF=${IMAGE_REF}
IMAGE_ID=${IMAGE_ID}
EOF

printf '%s\n' "${IMAGE_ID}" > "${OUTPUT_DIR}/image-id.txt"
echo "Built immutable candidate ${IMAGE_REF} (${IMAGE_ID})."
