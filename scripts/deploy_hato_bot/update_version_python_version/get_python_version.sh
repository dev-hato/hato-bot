#!/usr/bin/env bash

cp .env.example .env
export TAG_NAME="${HEAD_REF//\//-}"
docker compose pull
DOCKER_CMD="python --version 2>&1 | sed -e 's/^Python //g'"
python_version=$(docker compose run hato-bot sh -c "${DOCKER_CMD}")
echo "Python version:" "${python_version}"
sed -i -e "s/requires-python = \"==.*\"/requires-python = \"==${python_version}\"/g" pyproject.toml
DOCKER_CMD="uv version | sed -e 's/uv \([0-9.]*\)/\1/g'"
uv_version=$(docker compose run hato-bot sh -c "${DOCKER_CMD}")
sed -i -e "s/required-version = .*/required-version = \"$uv_version\"/g" pyproject.toml
