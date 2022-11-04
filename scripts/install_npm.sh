#!/usr/bin/env bash

npm_version=$(jq -r '.engines.npm | ltrimstr("^")' package.json)
npm install --location=global "npm@${npm_version}"
