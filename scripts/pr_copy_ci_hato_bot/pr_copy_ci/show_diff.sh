#!/usr/bin/env bash

pwd
git add -A
result="$(git diff --cached)"
result="${result//'%'/'%25'}"
result="${result//$'\n'/'%0A'}"
result="${result//$'\r'/'%0D'}"
echo "diff=${result}" >>"${GITHUB_OUTPUT}"
