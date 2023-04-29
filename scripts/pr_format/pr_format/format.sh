#!/usr/bin/env bash

pipenv run python "${GITHUB_WORKSPACE}/scripts/pr_format/pr_format/add_missing_pipfile_package.py"
pipenv install --dev
pipenv run autopep8 --exit-code --in-place --recursive .
pipenv run black --config .python-black .
pipenv run isort --sp .isort.cfg .
