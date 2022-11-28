#!/usr/bin/env bash

DOCKER_CMD="npm --version"
npm_version="$(docker run ghcr.io/dependabot/dependabot-core sh -c "${DOCKER_CMD}")"
echo "npm version:" "${npm_version}"
DEPENDABOT_NPM_VERSION="${npm_version}"
NPM_PATTERN_PACKAGE="s/\"npm\": \".*\"/\"npm\": \"^${DEPENDABOT_NPM_VERSION}\"/g"
sed -i -e "${NPM_PATTERN_PACKAGE}" package.json
bash "${GITHUB_WORKSPACE}/scripts/pr_check_npm/npm_install.sh"
