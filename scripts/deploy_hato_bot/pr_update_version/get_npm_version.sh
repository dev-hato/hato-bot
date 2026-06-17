#!/usr/bin/env bash
set -euo pipefail

DEPENDABOT_NPM_VERSION="10.9.3"
repository="${REPOSITORY:-dev-hato/hato-bot}"
export TAG_NAME="${HEAD_REF//\//-}"
image="ghcr.io/${repository}/hato-bot:${TAG_NAME}"

docker pull "${image}"
HATO_BOT_NPM_VERSION="$(docker run --rm --entrypoint npm "${image}" --version)"
echo "hato-bot npm version:" "${HATO_BOT_NPM_VERSION}"
NPM_PATTERN_PACKAGE="s/\"npm\": \".*\"/\"npm\": \"~${HATO_BOT_NPM_VERSION} || ^${DEPENDABOT_NPM_VERSION}\"/g"
sed -i -e "${NPM_PATTERN_PACKAGE}" package.json
npm install --package-lock-only
