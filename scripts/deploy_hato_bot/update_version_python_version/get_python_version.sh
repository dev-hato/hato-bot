#!/usr/bin/env bash
set -euo pipefail

repository="${REPOSITORY:-dev-hato/hato-bot}"
export TAG_NAME="${HEAD_REF//\//-}"
image="ghcr.io/${repository}/hato-bot:${TAG_NAME}"

docker pull "${image}"
python_version="$(docker run --rm --entrypoint python "${image}" --version 2>&1 | sed -e 's/^Python //g')"
echo "Python version:" "${python_version}"
sed -i -e "s/requires-python = \"==.*\"/requires-python = \"==${python_version}\"/g" pyproject.toml
