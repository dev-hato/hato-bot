#!/usr/bin/env bash
set -e

npm ci
echo "PYTHONPATH=/github/workspace/:/github/workflow/.venv/lib/python$(uv run "${GITHUB_WORKSPACE}/scripts/pr_test/pr_super_lint/get_python_version.py")/site-packages" >>"${GITHUB_ENV}"
action="$(yq '.jobs.pr-super-lint.steps[-1].uses | line_comment' .github/workflows/pr-test.yml)"
PATH="$(docker run --rm --entrypoint '' "ghcr.io/super-linter/super-linter:slim-${action}" /bin/sh -c 'echo $PATH')"
echo "PATH=/github/workspace/node_modules/.bin:${PATH}" >>"$GITHUB_ENV"
