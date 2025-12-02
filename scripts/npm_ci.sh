#!/usr/bin/env bash
set -e

bash "${GITHUB_WORKSPACE}/scripts/install_npm.sh"
npm ci
