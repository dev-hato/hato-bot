#!/usr/bin/env bash

bash "${GITHUB_WORKSPACE}/scripts/npm_ci.sh"
npm install --save-dev tsx
echo "PYTHONPATH=/github/workspace/:/github/workflow/.venv/lib/python$(echo 'import sys; print(".".join(map(str, sys.version_info[0:2])))' | python)/site-packages" >>"${GITHUB_ENV}"
action="$(yq '.jobs.pr-super-lint.steps[-1].uses | line_comment' .github/workflows/pr-test.yml)"
PATH="$(docker run --rm --entrypoint '' "ghcr.io/super-linter/super-linter:slim-${action}" /bin/sh -c 'echo $PATH')"
echo "PATH=/github/workspace/node_modules/.bin:${PATH}" >>"$GITHUB_ENV"
