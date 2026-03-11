#!/usr/bin/env bash
set -e

uv_version=$(docker run --rm ghcr.io/dependabot/dependabot-updater-uv uv --version | sed -e 's/^uv //g')
sed -i -e "s/required-version = .*/required-version = \"$uv_version\"/g" pyproject.toml
image_name=ghcr.io/astral-sh/uv
token=$(curl -s "https://ghcr.io/token?service=ghcr.io&scope=repository:astral-sh/uv:pull" | jq -r .token)
image_tag=""
last="$uv_version"

while [ -z "$image_tag" ]; do
  tags=$(curl -s "https://ghcr.io/v2/astral-sh/uv/tags/list?n=100&last=$last" \
    -H "Authorization: Bearer $token" | jq -r '.tags[]' 2>/dev/null)

  if [ -z "$tags" ]; then
    break
  fi

  match=$(echo "$tags" | grep -m 1 -E "^${uv_version}-python3\.14-.+-slim$")

  if [ -n "$match" ]; then
    image_tag=$image_name:$match
    break
  fi

  # このバージョンのタグを過ぎたら終了
  if ! echo "$tags" | grep -q "^${uv_version}-"; then
    break
  fi

  last=$(echo "$tags" | tail -1)
done

if [ -z "$image_tag" ]; then
  echo "Error: uv $uv_version に対応するDebian slimタグが見つかりません。" >&2
  echo "利用可能なタグ: https://github.com/astral-sh/uv/pkgs/container/uv" >&2
  exit 1
fi

docker pull "$image_tag"
sed -i -e "s?^FROM $image_name:.[^ ]* ?FROM $image_tag$(docker inspect "$image_tag" | yq '.[0].RepoDigests[0]' | sed -e "s:^$image_name::g") ?g" Dockerfile
