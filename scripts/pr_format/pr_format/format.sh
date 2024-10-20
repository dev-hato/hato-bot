#!/usr/bin/env bash

pipenv run python "${GITHUB_WORKSPACE}/scripts/pr_format/pr_format/fix_pipfile.py"
tag_name="$(yq '.jobs.pr-super-lint.steps[-1].uses' .github/workflows/pr-test.yml | sed -e 's;/slim@.*;:slim;g')"
tag_version="$(yq '.jobs.pr-super-lint.steps[-1].uses | line_comment' .github/workflows/pr-test.yml)"
pyink_version="$(docker run --rm --entrypoint '' "ghcr.io/${tag_name}-${tag_version}" /bin/sh -c 'pyink --version' | grep pyink | awk '{ print $2 }')"
sed -i -e "s/pyink = .*/pyink = \"==${pyink_version}\"/g" Pipfile
pipenv install --dev
pipenv run autopep8 --exit-code --in-place --recursive .
pipenv run pyink --config .python-black .
pipenv run isort --sp .isort.cfg .
