#!/usr/bin/env bash
set -e

uv_version=$(docker run --rm ghcr.io/dependabot/dependabot-updater-uv uv --version | sed -e 's/^uv //g')
sed -i -e "s/required-version = .*/required-version = \"$uv_version\"/g" pyproject.toml
image_name=ghcr.io/astral-sh/uv
image_tag=$image_name:$uv_version-python3.14-trixie-slim
docker pull "$image_tag"
sed -i -e "s?^FROM $image_name:.[^ ]* ?FROM $image_tag$(docker inspect "$image_tag" | yq '.[0].RepoDigests[0]' | sed -e "s:^$image_name::g") ?g" Dockerfile
