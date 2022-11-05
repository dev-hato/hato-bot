#!/usr/bin/env bash

NPM_PATTERN_PACKAGE="s/\"npm\": \".*\"/\"npm\": \"^${DEPENDABOT_NPM_VERSION}\"/g"
sed -i -e "${NPM_PATTERN_PACKAGE}" package.json
