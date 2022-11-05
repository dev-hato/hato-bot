#!/usr/bin/env bash

DOCKER_CMD="python --version 2>&1 | sed -e 's/^Python //g'"
python_version=$(docker compose run hato-bot sh -c "${DOCKER_CMD}")
echo "Python version:" "${python_version}"
echo "python_version=${python_version}" >>"${GITHUB_OUTPUT}"
