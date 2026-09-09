#!/usr/bin/env bash
set -euo pipefail

if [[ "$#" -ne 2 ]]; then
  echo "Usage: $0 <source-image-ref> <target-image-ref>"
  exit 2
fi

SOURCE_REF="$1"
TARGET_REF="$2"
SOURCE_ID="$(docker image inspect "${SOURCE_REF}" --format '{{.Id}}')"

docker tag "${SOURCE_REF}" "${TARGET_REF}"

TARGET_ID="$(docker image inspect "${TARGET_REF}" --format '{{.Id}}')"
if [[ "${SOURCE_ID}" != "${TARGET_ID}" ]]; then
  echo "Promotion rebuilt or changed the image: ${SOURCE_ID} != ${TARGET_ID}"
  exit 1
fi

echo "Promoted ${SOURCE_REF} -> ${TARGET_REF} without rebuild (${TARGET_ID})."
