#!/usr/bin/env bash

DOCKER_CMD="npm --version"
DEPENDABOT_NPM_VERSION="$(docker run ghcr.io/dependabot/dependabot-core sh -c "${DOCKER_CMD}")"
echo "Dependabot npm version:" "${DEPENDABOT_NPM_VERSION}"
RENOVATE_NPM_VERSION="$(docker run ghcr.io/renovatebot/renovate sh -c "${DOCKER_CMD}")"
echo "Renovate npm version:" "${RENOVATE_NPM_VERSION}"
NPM_PATTERN_PACKAGE="s/\"npm\": \".*\"/\"npm\": \"^${RENOVATE_NPM_VERSION} || ^${DEPENDABOT_NPM_VERSION}\"/g"
sed -i -e "${NPM_PATTERN_PACKAGE}" package.json
bash "${GITHUB_WORKSPACE}/scripts/pr_check_npm/npm_install.sh"
