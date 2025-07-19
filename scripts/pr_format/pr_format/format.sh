#!/usr/bin/env bash

uv run "${GITHUB_WORKSPACE}/scripts/pr_format/pr_format/fix_pyproject.py"
uv sync --dev

if [ "$(yq .tool.uv.sources.sudden-death.git pyproject.toml)" != 'null' ]; then
	uv lock --upgrade-package sudden-death
fi

uv tool run autopep8 --exit-code --in-place --recursive .
uv tool run isort --sp .isort.cfg .
