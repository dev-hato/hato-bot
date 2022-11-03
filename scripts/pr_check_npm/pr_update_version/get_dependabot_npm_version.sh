#!/usr/bin/env bash

DOCKER_CMD="npm --version"
npm_version="$(docker run ghcr.io/dependabot/dependabot-core sh -c "${DOCKER_CMD}")"
echo "npm version:" "${npm_version}"
echo "npm_version=${npm_version}" >>"${GITHUB_OUTPUT}"
