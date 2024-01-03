#!/usr/bin/env bash
set -e

echo aaa
pipenv run python "${GITHUB_WORKSPACE}/scripts/pr_format/pr_format/fix_pipfile.py"
echo iii
exit 1
pipenv install --dev
echo uuu
pipenv run autopep8 --exit-code --in-place --recursive .
echo eee
pipenv run black --config .python-black .
echo ooo
pipenv run isort --sp .isort.cfg .
echo kakaka
