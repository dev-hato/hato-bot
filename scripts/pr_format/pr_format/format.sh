#!/usr/bin/env bash
set -e

pipenv run python "${GITHUB_WORKSPACE}/scripts/pr_format/pr_format/fix_pipfile.py"
pipenv install --dev
pipenv run autopep8 --exit-code --in-place --recursive .
pipenv run black --config .python-black .
pipenv run isort --sp .isort.cfg .
