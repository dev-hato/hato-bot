#!/usr/bin/env bash
set -e

result=$(git diff origin/develop origin/master)
echo "${result}"
result="${result//$'\n'/'%0A'}"
result="${result//$'\r'/'%0D'}"
echo "result=${result}" >>"${GITHUB_OUTPUT}"
