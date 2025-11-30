#!/usr/bin/env bash

uv run "${GITHUB_WORKSPACE}/scripts/pr_format/pr_format/fix_pyproject.py"
action="$(yq '.jobs.pr-super-lint.steps[-1].uses | line_comment' .github/workflows/pr-test.yml)"
mypy_version=$(docker run --rm --entrypoint '' "ghcr.io/super-linter/super-linter:slim-${action}" /bin/sh -c 'mypy --version | sed -e "s/.* \([0-9]*\.[0-9]*\.[0-9]*\) .*/\1/"')
sed -i -e "s/mypy==[0-9.]*/mypy==${mypy_version}/g" pyproject.toml
uv sync --dev

if [ "$(yq .tool.uv.sources.sudden-death.git pyproject.toml)" != 'null' ]; then
	uv lock --upgrade-package sudden-death
fi

uv tool run autopep8 --exit-code --in-place --recursive .
uv tool run isort --sp .isort.cfg .
