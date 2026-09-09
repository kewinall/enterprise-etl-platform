#!/usr/bin/env bash
set -euo pipefail

if [[ "$#" -ne 2 ]]; then
  echo "usage: $0 SOURCE_IMAGE TARGET_IMAGE" >&2
  exit 2
fi

SOURCE_IMAGE="$1"
TARGET_IMAGE="$2"

docker pull "$SOURCE_IMAGE" >/dev/null
SOURCE_DIGEST="$(
  docker image inspect "$SOURCE_IMAGE"     --format '{{range .RepoDigests}}{{println .}}{{end}}'   | sed -n 's/.*@\(sha256:[0-9a-f]\{64\}\)$/\1/p'   | head -n1
)"

if [[ -z "$SOURCE_DIGEST" ]]; then
  echo "unable to resolve source registry digest" >&2
  exit 1
fi

docker tag "$SOURCE_IMAGE" "$TARGET_IMAGE"
docker push "$TARGET_IMAGE" >/dev/null
docker pull "$TARGET_IMAGE" >/dev/null

TARGET_DIGEST="$(
  docker image inspect "$TARGET_IMAGE"     --format '{{range .RepoDigests}}{{println .}}{{end}}'   | sed -n 's/.*@\(sha256:[0-9a-f]\{64\}\)$/\1/p'   | head -n1
)"

if [[ "$SOURCE_DIGEST" != "$TARGET_DIGEST" ]]; then
  echo "promotion digest mismatch: source=$SOURCE_DIGEST target=$TARGET_DIGEST" >&2
  exit 1
fi

echo "$SOURCE_DIGEST"
