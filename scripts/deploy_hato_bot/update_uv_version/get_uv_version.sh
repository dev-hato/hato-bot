#!/usr/bin/env bash
set -euo pipefail

image='ghcr.io/dependabot/dependabot-updater-uv:latest'

echo "Pulling $image" >&2
docker pull "$image" >&2

echo "Getting uv version from $image" >&2
uv_version="$(
  docker run --rm --entrypoint uv "$image" --version 2>&1 |
    sed -nE 's/^uv ([0-9]+\.[0-9]+\.[0-9]+).*/\1/p'
)"

if [ -z "$uv_version" ]; then
  echo "Error: failed to parse uv version from $image" >&2
  exit 1
fi

echo "Detected uv version: $uv_version" >&2

sed -i -e "s/required-version = .*/required-version = \"$uv_version\"/g" pyproject.toml

match="$(
  gh api --paginate /orgs/astral-sh/packages/container/uv/versions --jq '.[].metadata.container.tags[]' |
    grep -m 1 -E "^${uv_version}-python3\\.14-.+-slim$"
)"

if [ -z "$match" ]; then
  echo "Error: uv $uv_version に対応するDebian slimタグが見つかりません。" >&2
  echo "利用可能なタグ: https://github.com/orgs/astral-sh/packages/container/package/uv" >&2
  exit 1
fi

image_name=ghcr.io/astral-sh/uv
image_tag=$image_name:$match

echo "Pulling $image_tag" >&2
docker pull "$image_tag"
sed -i -e "s?^FROM $image_name:.[^ ]* ?FROM $image_tag$(docker inspect "$image_tag" | yq '.[0].RepoDigests[0]' | sed -e "s:^$image_name::g") ?g" Dockerfile
