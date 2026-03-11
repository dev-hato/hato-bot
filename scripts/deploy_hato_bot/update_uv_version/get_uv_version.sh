#!/usr/bin/env bash
set -e

uv_version=$(docker run --rm ghcr.io/dependabot/dependabot-updater-uv uv --version | sed -e 's/^uv //g')
sed -i -e "s/required-version = .*/required-version = \"$uv_version\"/g" pyproject.toml
match=$(gh api --paginate /orgs/astral-sh/packages/container/uv/versions --jq '.[].metadata.container.tags[]' |
  grep -m 1 -E "^${uv_version}-python3\.14-.+-slim$")

if [ -z "$match" ]; then
  echo "Error: uv $uv_version に対応するDebian slimタグが見つかりません。" >&2
  echo "利用可能なタグ: https://github.com/astral-sh/uv/pkgs/container/uv" >&2
  exit 1
fi

image_name=ghcr.io/astral-sh/uv
image_tag=$image_name:$match
docker pull "$image_tag"
sed -i -e "s?^FROM $image_name:.[^ ]* ?FROM $image_tag$(docker inspect "$image_tag" | yq '.[0].RepoDigests[0]' | sed -e "s:^$image_name::g") ?g" Dockerfile
