#!/usr/bin/env bash
set -e

uv_version=$(docker run --rm ghcr.io/dependabot/dependabot-updater-uv uv --version | sed -e 's/^uv //g')
sed -i -e "s/required-version = .*/required-version = \"$uv_version\"/g" pyproject.toml
image_name=ghcr.io/astral-sh/uv
image_suffix=python3.14-bookworm-slim
image_tag=$image_name:$uv_version-$image_suffix
token=$(curl -s "https://ghcr.io/token?service=ghcr.io&scope=repository:astral-sh/uv:pull" | jq -r .token)
status=$(curl -s -o /dev/null -w "%{http_code}" "https://ghcr.io/v2/astral-sh/uv/manifests/$uv_version-$image_suffix" -H "Authorization: Bearer $token")

if [ "$status" != "200" ]; then
  echo "Error: $image_tag が見つかりません (HTTP $status)。" >&2
  echo "uv $uv_version に対応する $image_suffix タグが存在しない可能性があります。" >&2
  echo "利用可能なタグ: https://github.com/astral-sh/uv/pkgs/container/uv" >&2
  exit 1
fi

docker pull "$image_tag"
sed -i -e "s?^FROM $image_name:.[^ ]* ?FROM $image_tag$(docker inspect "$image_tag" | yq '.[0].RepoDigests[0]' | sed -e "s:^$image_name::g") ?g" Dockerfile
