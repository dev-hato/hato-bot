#!/usr/bin/env bash

DEPENDABOT_NPM_VERSION="${{steps.get_dependabot_npm_version.outputs.npm_version}}"
NPM_PATTERN_PACKAGE="s/\"npm\": \".*\"/\"npm\": \"^${DEPENDABOT_NPM_VERSION}\"/g"
sed -i -e "${NPM_PATTERN_PACKAGE}" package.json
