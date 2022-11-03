#!/usr/bin/env bash

npm_version=$(jq -r '.engines.npm | ltrimstr("^")' package.json)
npm install --prefer-offline --location=global "npm@${npm_version}"
npm install
