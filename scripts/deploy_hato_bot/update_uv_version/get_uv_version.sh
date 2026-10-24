#!/usr/bin/env bash
set -euo pipefail

image=$(curl https://raw.githubusercontent.com/github/dependabot-action/refs/heads/main/docker/containers.json | yq .uv)

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

echo "Detected uv version in Dependabot: $uv_version" >&2

export TAG_NAME="${HEAD_REF//\//-}"
cp .env.example .env

echo "Getting uv version from Docker image" >&2
docker_uv_version="$(
	docker compose run --rm -T hato-bot uv --version 2>&1 |
		sed -nE 's/^uv ([0-9]+\.[0-9]+\.[0-9]+).*/\1/p'
)"

if [ -z "$docker_uv_version" ]; then
	echo "Error: failed to parse uv version from Docker image" >&2
	exit 1
fi

echo "Detected uv version in Dockerfile: $docker_uv_version" >&2

# アプリのビルドで required-version の不一致が起きないよう、Dockerイメージのuvを調べてから更新する
# Dependabotのuvより古いバージョンで動かないよう下限のみ指定する
sed -i -e "s/required-version = .*/required-version = \">=$uv_version\"/g" pyproject.toml

# DockerイメージのuvがDependabotのuv以上であればそのままにする
if [ "$(printf '%s\n%s\n' "$uv_version" "$docker_uv_version" | sort -V | head -n 1)" = "$uv_version" ]; then
	echo "uv version in Dockerfile is up to date" >&2
	exit 0
fi

match="$(
	gh api --paginate /orgs/astral-sh/packages/container/uv/versions --jq '.[].metadata.container.tags[]' |
		awk -v pattern="^${uv_version}-python3\\\\.14-.+-slim$" '
      $0 ~ pattern && first == "" { first = $0 }
      END { if (first != "") print first }
    '
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
