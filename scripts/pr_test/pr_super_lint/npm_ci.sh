#!/usr/bin/env bash

bash "${GITHUB_WORKSPACE}/scripts/npm_ci.sh"
echo "PYTHONPATH=/github/workspace/:/github/workflow/.venv/lib/python$(echo 'import sys; print(".".join(map(str, sys.version_info[0:2])))' | python)/site-packages" >>"${GITHUB_ENV}"
