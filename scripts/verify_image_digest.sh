#!/usr/bin/env bash
set -euo pipefail

if [[ "$#" -ne 2 ]]; then
  echo "usage: $0 IMAGE_REF EXPECTED_DIGEST" >&2
  exit 2
fi

IMAGE_REF="$1"
EXPECTED_DIGEST="$2"

docker pull "$IMAGE_REF" >/dev/null
ACTUAL_DIGEST="$(
  docker image inspect "$IMAGE_REF"     --format '{{range .RepoDigests}}{{println .}}{{end}}'   | sed -n 's/.*@\(sha256:[0-9a-f]\{64\}\)$/\1/p'   | head -n1
)"

if [[ -z "$ACTUAL_DIGEST" ]]; then
  echo "unable to resolve registry digest for $IMAGE_REF" >&2
  exit 1
fi

if [[ "$ACTUAL_DIGEST" != "$EXPECTED_DIGEST" ]]; then
  echo "digest mismatch: expected=$EXPECTED_DIGEST actual=$ACTUAL_DIGEST" >&2
  exit 1
fi

echo "image digest verified: $ACTUAL_DIGEST"
